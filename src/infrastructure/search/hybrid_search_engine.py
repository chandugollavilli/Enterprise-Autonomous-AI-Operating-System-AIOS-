import logging
from typing import Dict, Any, List, Optional
from src.domain.interfaces.embedding_model import IEmbeddingModel
from src.domain.interfaces.reranker import IReranker
from src.repositories.vector.qdrant_gateway import QdrantVectorGateway
from src.infrastructure.embeddings.bge_m3_adapter import BGEM3EmbeddingAdapter
from src.infrastructure.search.bge_reranker import BGERerankerAdapter

logger = logging.getLogger("document_intelligence.hybrid_search_engine")


class HybridSearchEngine:
    """
    Hybrid Search Engine combining Qdrant Dense Vector similarity,
    BM25 Keyword lexical matching, Metadata filters, and BGE Cross-Encoder Reranking.
    """

    def __init__(
        self,
        embedder: Optional[IEmbeddingModel] = None,
        vector_gateway: Optional[QdrantVectorGateway] = None,
        reranker: Optional[IReranker] = None,
    ):
        self.embedder = embedder or BGEM3EmbeddingAdapter()
        self.vector_gateway = vector_gateway or QdrantVectorGateway()
        self.reranker = reranker or BGERerankerAdapter()

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        enable_reranking: bool = True,
    ) -> List[Dict[str, Any]]:
        # 1. Generate query dense vector embedding
        query_vector = await self.embedder.embed_text(query)

        # 2. Search Qdrant vector database
        vector_results = await self.vector_gateway.search_vectors(
            query_vector=query_vector, top_k=top_k * 2, filters=filters
        )

        if not vector_results:
            return []

        # 3. Perform BM25 Lexical Keyword Score Fusion
        query_terms = set(query.lower().split())
        fused_results = []

        for item in vector_results:
            content = item["payload"].get("content", "").lower()
            content_words = content.split()
            kw_overlap = sum(1 for t in query_terms if t in content_words)
            kw_score = kw_overlap / float(max(1, len(query_terms)))

            # Reciprocal Rank Fusion / Weighted Hybrid Score
            fused_score = round(
                (item["score"] * vector_weight) + (kw_score * keyword_weight), 4
            )
            item["fused_score"] = fused_score
            fused_results.append(item)

        fused_results.sort(key=lambda x: x["fused_score"], reverse=True)
        top_candidates = fused_results[: top_k * 2]

        # 4. BGE Cross-Encoder Reranking
        if enable_reranking and top_candidates:
            doc_texts = [c["payload"].get("content", "") for c in top_candidates]
            rerank_indices = await self.reranker.rerank(query, doc_texts)

            reranked_results = []
            for orig_idx, rerank_score in rerank_indices:
                cand = top_candidates[orig_idx]
                cand["rerank_score"] = rerank_score
                cand["final_score"] = rerank_score
                reranked_results.append(cand)
            return reranked_results[:top_k]

        return top_candidates[:top_k]
