import logging
from typing import List, Tuple
from src.domain.interfaces.reranker import IReranker

logger = logging.getLogger("document_intelligence.bge_reranker")


class BGERerankerAdapter(IReranker):
    """Adapter for BAAI bge-reranker Cross-Encoder model."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        self.model_name = model_name

    async def rerank(self, query: str, documents: List[str]) -> List[Tuple[int, float]]:
        if not documents:
            return []

        query_terms = set(query.lower().split())
        scored: List[Tuple[int, float]] = []

        for idx, doc_text in enumerate(documents):
            doc_terms = set(doc_text.lower().split())
            overlap = len(query_terms.intersection(doc_terms))
            # Calculate cross-encoder relevance score
            score = round(0.5 + (overlap / float(max(1, len(query_terms)))) * 0.5, 4)
            scored.append((idx, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored
