from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IEmbeddingModel(ABC):
    """Standardized Abstract Interface for Enterprise Embedding Models."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize embedding model weights and resources."""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate dense vector embedding for single text string."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings for batch of text strings."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check embedding model health and readiness."""
        pass

    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Return model metadata (dimension, name, provider)."""
        pass

    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Return list of supported languages."""
        pass
