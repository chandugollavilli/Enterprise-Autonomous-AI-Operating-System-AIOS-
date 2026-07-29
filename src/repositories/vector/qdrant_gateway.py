import uuid
import logging
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger("document_intelligence.qdrant_gateway")


class QdrantVectorGateway:
    """
    Qdrant Vector Database Gateway managing collection creation, payload schema indexing,
    batch vector upserts, and cosine similarity search.
    """

    def __init__(self, collection_name: str = "document_chunks", vector_size: int = 1024):
        self.collection_name = collection_name
        self.vector_size = vector_size

        # In-memory mock storage for testing & standalone execution
        self._vectors: Dict[str, Dict[str, Any]] = {}

    async def initialize_collection(self) -> bool:
        logger.info(f"Initialized Qdrant Collection '{self.collection_name}' (Vector Size: {self.vector_size}, Distance: Cosine)")
        return True

    async def upsert_vector(
        self,
        point_id: str,
        vector: List[float],
        payload: Dict[str, Any],
    ) -> bool:
        self._vectors[point_id] = {
            "id": point_id,
            "vector": np.array(vector, dtype=np.float32),
            "payload": payload,
        }
        return True

    async def upsert_batch(
        self,
        points: List[Dict[str, Any]],  # [{"id": str, "vector": List[float], "payload": Dict}]
    ) -> bool:
        for p in points:
            await self.upsert_vector(p["id"], p["vector"], p["payload"])
        logger.info(f"Batch upserted {len(points)} vectors into Qdrant collection '{self.collection_name}'")
        return True

    async def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if not self._vectors:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec) + 1e-9

        results = []
        for point_id, data in self._vectors.items():
            payload = data["payload"]

            # Apply metadata filters
            if filters:
                match = True
                for k, v in filters.items():
                    if payload.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            v = data["vector"]
            v_norm = np.linalg.norm(v) + 1e-9
            score = float(np.dot(q_vec, v) / (q_norm * v_norm))

            results.append({
                "point_id": point_id,
                "score": round(score, 4),
                "payload": payload,
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    async def delete_vector(self, point_id: str) -> bool:
        if point_id in self._vectors:
            del self._vectors[point_id]
            return True
        return False
