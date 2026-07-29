from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IConnector(ABC):
    """Abstract Interface for Enterprise System Connectors (S3, MinIO, SFTP, SharePoint, Webhooks)."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize connector settings and drivers."""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """Establish network connection to target enterprise platform."""
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate credentials against target API / service."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check connector health and connection status."""
        pass

    @abstractmethod
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List remote files and documents available for sync."""
        pass

    @abstractmethod
    async def download(self, document_ref: str) -> bytes:
        """Download remote document content into memory bytes."""
        pass

    @abstractmethod
    async def upload(self, filename: str, content: bytes) -> str:
        """Upload file to enterprise target system. Returns remote reference path."""
        pass

    @abstractmethod
    async def delete(self, document_ref: str) -> bool:
        """Delete remote document from target system."""
        pass

    @abstractmethod
    async def sync(self) -> List[Dict[str, Any]]:
        """Execute full or incremental synchronization batch."""
        pass

    @abstractmethod
    def connector_info(self) -> Dict[str, Any]:
        """Return metadata (name, type, capabilities)."""
        pass
