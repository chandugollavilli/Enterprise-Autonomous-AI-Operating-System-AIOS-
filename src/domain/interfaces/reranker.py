from abc import ABC, abstractmethod
from typing import List, Tuple


class IReranker(ABC):
    """Abstract Interface for Cross-Encoder Document Reranking Models."""

    @abstractmethod
    async def rerank(self, query: str, documents: List[str]) -> List[Tuple[int, float]]:
        """Rerank candidate documents against query. Returns list of (original_idx, rerank_score)."""
        pass
