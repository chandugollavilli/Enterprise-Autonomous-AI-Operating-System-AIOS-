import io
import logging
from datetime import timedelta
from typing import BinaryIO
from minio import Minio
from minio.error import S3Error

from src.config import settings
from src.domain.interfaces.storage_gateway import IStorageGateway

logger = logging.getLogger("document_intelligence.storage")


class MinIOStorageGateway(IStorageGateway):
    """MinIO / AWS S3 compatible implementation of storage gateway."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket '{self.bucket_name}'")
        except Exception as e:
            logger.warning(f"Unable to check/create MinIO bucket at startup: {e}")

    async def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        content = file_data.read()
        file_size = len(content)
        data_stream = io.BytesIO(content)

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=data_stream,
            length=file_size,
            content_type=content_type,
        )
        return object_name

    async def download_file(self, object_name: str) -> bytes:
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete_file(self, object_name: str) -> bool:
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            logger.error(f"Failed to delete file {object_name} from MinIO: {e}")
            return False

    async def file_exists(self, object_name: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    async def get_file_url(self, object_name: str, expires_in_seconds: int = 3600) -> str:
        return self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            expires=timedelta(seconds=expires_in_seconds),
        )
