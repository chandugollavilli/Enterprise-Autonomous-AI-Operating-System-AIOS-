import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import DocumentChunk, SearchHistory, VectorIndex
from src.infrastructure.indexing.batch_indexer import VectorBatchIndexer
from src.infrastructure.search.hybrid_search_engine import HybridSearchEngine
from src.repositories.vector.qdrant_gateway import QdrantVectorGateway

logger = logging.getLogger("document_intelligence.vector_search_service")

# Global Qdrant instance shared for service operations
shared_qdrant_gateway = QdrantVectorGateway()


class VectorSearchService:
    """Service orchestrating document indexing, hybrid search, similar document retrieval, and telemetry logging."""

    def __init__(
        self,
        db_session: AsyncSession,
        hybrid_engine: Optional[HybridSearchEngine] = None,
        indexer: Optional[VectorBatchIndexer] = None,
    ):
        self.db = db_session
        self.gateway = shared_qdrant_gateway
        self.hybrid_engine = hybrid_engine or HybridSearchEngine(vector_gateway=self.gateway)
        self.indexer = indexer or VectorBatchIndexer(vector_gateway=self.gateway)

    async def index_document_vectors(self, document_id: uuid.UUID) -> int:
        """Fetch unindexed DocumentChunks from DB, generate BGE-M3 embeddings, and upsert to Qdrant."""
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        res = await self.db.execute(stmt)
        chunks = list(res.scalars().all())

        if not chunks:
            return 0

        point_ids = await self.indexer.index_chunks(chunks)

        for chunk, point_id in zip(chunks, point_ids):
            v_idx = VectorIndex(
                document_id=document_id,
                point_id=point_id,
                collection_name="document_chunks",
                vector_dim=1024,
                status="indexed",
            )
            self.db.add(v_idx)

        await self.db.commit()
        return len(point_ids)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None,
        search_type: str = "hybrid",
    ) -> List[Dict[str, Any]]:
        start_time = time.perf_counter()

        results = await self.hybrid_engine.search(
            query=query,
            top_k=top_k,
            filters=filters,
            enable_reranking=True,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Log Search Telemetry in PostgreSQL
        history = SearchHistory(
            user_id=user_id,
            query_text=query,
            search_type=search_type,
            result_count=len(results),
            latency_ms=elapsed_ms,
            filters_json=filters or {},
        )
        self.db.add(history)
        await self.db.commit()

        return results

    async def find_similar_documents(self, document_id: uuid.UUID, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find related/similar documents by vector similarity match across document chunks."""
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id).limit(1)
        res = await self.db.execute(stmt)
        seed_chunk = res.scalar_one_or_none()

        if not seed_chunk:
            return []

        # Exclude original document from results
        filters = {"document_id": str(document_id)}
        results = await self.search(query=seed_chunk.content[:200], top_k=top_k + 1, search_type="similar")
        return [r for r in results if r["payload"].get("document_id") != str(document_id)][:top_k]
