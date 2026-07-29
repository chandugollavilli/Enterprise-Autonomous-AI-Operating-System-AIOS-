import uuid
import logging
from typing import List, Dict, Any, Optional
from src.domain.interfaces.embedding_model import IEmbeddingModel
from src.infrastructure.embeddings.bge_m3_adapter import BGEM3EmbeddingAdapter
from src.infrastructure.embeddings.embedding_cache import EmbeddingCacheManager
from src.repositories.vector.qdrant_gateway import QdrantVectorGateway
from src.repositories.postgres.models import DocumentChunk

logger = logging.getLogger("document_intelligence.batch_indexer")


class VectorBatchIndexer:
    """Batch & Incremental Document Chunk Vector Indexer."""

    def __init__(
        self,
        embedder: Optional[IEmbeddingModel] = None,
        vector_gateway: Optional[QdrantVectorGateway] = None,
        cache_manager: Optional[EmbeddingCacheManager] = None,
    ):
        self.embedder = embedder or BGEM3EmbeddingAdapter()
        self.vector_gateway = vector_gateway or QdrantVectorGateway()
        self.cache = cache_manager or EmbeddingCacheManager()

    async def index_chunks(self, chunks: List[DocumentChunk]) -> List[str]:
        """Convert document chunks to vector embeddings and upsert into Qdrant in batch."""
        if not chunks:
            return []

        points_to_upsert: List[Dict[str, Any]] = []
        point_ids: List[str] = []

        texts_to_embed = [c.content for c in chunks]
        embeddings = await self.embedder.embed_batch(texts_to_embed)

        for chunk, vector in zip(chunks, embeddings):
            point_id = str(uuid.uuid4())
            chunk.qdrant_point_id = point_id

            payload = {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "heading_context": chunk.heading_context,
                "pages": chunk.page_references_json.get("pages", []),
                "bboxes": chunk.page_references_json.get("bboxes", []),
            }

            points_to_upsert.append({"id": point_id, "vector": vector, "payload": payload})
            point_ids.append(point_id)

        await self.vector_gateway.upsert_batch(points_to_upsert)
        return point_ids
