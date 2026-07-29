from src.config import settings
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.repositories.storage.local_storage import LocalStorageGateway
from src.repositories.storage.minio_storage import MinIOStorageGateway


def get_storage_gateway() -> IStorageGateway:
    """Storage Strategy Factory based on environment configuration."""
    if settings.ENVIRONMENT == "development" and not settings.MINIO_ENDPOINT:
        return LocalStorageGateway()
    try:
        return MinIOStorageGateway()
    except Exception:
        # Fallback to local storage if MinIO is not available
        return LocalStorageGateway()
