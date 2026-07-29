import os
import aiofiles
from pathlib import Path
from typing import BinaryIO
from src.domain.interfaces.storage_gateway import IStorageGateway


class LocalStorageGateway(IStorageGateway):
    """Local file system implementation of object storage gateway."""

    def __init__(self, base_directory: str = "/tmp/ocr_storage"):
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, object_name: str) -> Path:
        return self.base_dir / object_name.lstrip("/")

    async def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        full_path = self._get_full_path(object_name)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        content = file_data.read()
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)

        return str(full_path)

    async def download_file(self, object_name: str) -> bytes:
        full_path = self._get_full_path(object_name)
        if not full_path.exists():
            raise FileNotFoundError(f"File {object_name} not found in local storage.")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete_file(self, object_name: str) -> bool:
        full_path = self._get_full_path(object_name)
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def file_exists(self, object_name: str) -> bool:
        return self._get_full_path(object_name).exists()

    async def get_file_url(self, object_name: str, expires_in_seconds: int = 3600) -> str:
        return f"file://{self._get_full_path(object_name)}"
