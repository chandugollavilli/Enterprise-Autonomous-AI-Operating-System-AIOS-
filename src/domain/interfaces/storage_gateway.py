from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class IStorageGateway(ABC):
    """Abstract interface defining object storage actions."""

    @abstractmethod
    async def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload file stream to storage and return object path/URL."""
        pass

    @abstractmethod
    async def download_file(self, object_name: str) -> bytes:
        """Download file content from storage as bytes."""
        pass

    @abstractmethod
    async def delete_file(self, object_name: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def file_exists(self, object_name: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    async def get_file_url(self, object_name: str, expires_in_seconds: int = 3600) -> str:
        """Get pre-signed or direct URL for file retrieval."""
        pass
