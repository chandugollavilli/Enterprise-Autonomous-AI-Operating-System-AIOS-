from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ILLMProvider(ABC):
    """Standardized Abstract Interface for Enterprise LLM Providers."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize LLM provider connections or model weights."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute chat completion. Returns dict with 'content', 'role', 'tokens_used'."""
        pass

    @abstractmethod
    async def complete(self, prompt: str, config: Dict[str, Any] = None) -> str:
        """Execute text completion prompt."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check LLM provider health and readiness."""
        pass

    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Return model metadata (name, provider, context_window)."""
        pass

    @abstractmethod
    def token_usage(self, text: str) -> int:
        """Estimate token count for text."""
        pass
