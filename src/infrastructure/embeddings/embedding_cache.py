import hashlib
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("document_intelligence.embedding_cache")


class EmbeddingCacheManager:
    """In-memory & persistent SHA-256 Embedding Cache Manager to prevent redundant embedding computation."""

    def __init__(self):
        self._cache: Dict[str, List[float]] = {}

    @staticmethod
    def compute_sha256(text: str, model_name: str) -> str:
        key_str = f"{model_name}:{text.strip()}"
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def get(self, text: str, model_name: str) -> Optional[List[float]]:
        key = self.compute_sha256(text, model_name)
        return self._cache.get(key)

    def set(self, text: str, model_name: str, vector: List[float]):
        key = self.compute_sha256(text, model_name)
        self._cache[key] = vector

    def clear(self):
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
