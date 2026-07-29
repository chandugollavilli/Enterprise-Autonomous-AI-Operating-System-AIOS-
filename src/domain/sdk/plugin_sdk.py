from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IPluginSDK(ABC):
    """Abstract Interface for Third-Party Extensions and Plugin SDK."""

    @abstractmethod
    async def on_load(self) -> bool:
        """Lifecycle hook invoked when plugin is loaded into memory."""
        pass

    @abstractmethod
    async def on_unload(self) -> bool:
        """Lifecycle hook invoked prior to plugin unloading or updating."""
        pass

    @abstractmethod
    async def on_event(self, event_name: str, payload: Dict[str, Any]) -> bool:
        """Event listener hook invoked on platform event publishing."""
        pass

    @abstractmethod
    def manifest_info(self) -> Dict[str, Any]:
        """Return plugin manifest (id, name, version, author, permissions)."""
        pass
