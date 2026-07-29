import io
import pytest
import shutil
from pathlib import Path
from src.repositories.storage.local_storage import LocalStorageGateway


@pytest.mark.asyncio
async def test_local_storage_crud(tmp_path):
    storage = LocalStorageGateway(base_directory=str(tmp_path))
    object_name = "documents/test.pdf"
    content = b"PDF Sample Data Stream"
    file_stream = io.BytesIO(content)

    # 1. Upload
    path = await storage.upload_file(file_stream, object_name, content_type="application/pdf")
    assert Path(path).exists()

    # 2. Exists
    assert await storage.file_exists(object_name) is True

    # 3. Download
    downloaded_bytes = await storage.download_file(object_name)
    assert downloaded_bytes == content

    # 4. URL
    url = await storage.get_file_url(object_name)
    assert url.startswith("file://")

    # 5. Delete
    deleted = await storage.delete_file(object_name)
    assert deleted is True
    assert await storage.file_exists(object_name) is False
