from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ISolutionPack(ABC):
    """Abstract Interface for Industry Solution Packs (Legal, Finance, HR, Healthcare, Research)."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize solution pack models, prompts, and agents."""
        pass

    @abstractmethod
    async def install(self, tenant_id: str) -> bool:
        """Install solution pack assets for target tenant."""
        pass

    @abstractmethod
    async def execute(self, document_text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute domain-specific AI analysis pipeline on document."""
        pass

    @abstractmethod
    def pack_info(self) -> Dict[str, Any]:
        """Return pack metadata (id, name, version, category, description)."""
        pass
