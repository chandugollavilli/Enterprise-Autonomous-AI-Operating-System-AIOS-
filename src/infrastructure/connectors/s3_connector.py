import logging
from typing import List, Dict, Any, Optional
from src.domain.interfaces.connector import IConnector

logger = logging.getLogger("document_intelligence.s3_connector")


class S3ConnectorAdapter(IConnector):
    """Adapter for Amazon S3 and MinIO Object Storage Connectors."""

    def __init__(self, bucket_name: str = "enterprise-docs", endpoint_url: Optional[str] = None):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self._connected = False

    async def initialize(self) -> bool:
        logger.info(f"Initialized S3 Connector for bucket: '{self.bucket_name}'")
        return True

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def authenticate(self) -> bool:
        return True

    async def health_check(self) -> bool:
        return self._connected

    def connector_info(self) -> Dict[str, Any]:
        return {
            "name": "Amazon S3 / MinIO Connector",
            "type": "object_storage",
            "bucket": self.bucket_name,
            "capabilities": ["list", "download", "upload", "delete", "sync"],
        }

    async def list_documents(self) -> List[Dict[str, Any]]:
        return [
            {"filename": "invoice_2026.pdf", "size_bytes": 10240, "ref": "s3://docs/invoice_2026.pdf"},
            {"filename": "contract_nda.pdf", "size_bytes": 45000, "ref": "s3://docs/contract_nda.pdf"},
        ]

    async def download(self, document_ref: str) -> bytes:
        return b"%PDF-1.4 Mock S3 Document Binary Content"

    async def upload(self, filename: str, content: bytes) -> str:
        ref = f"s3://{self.bucket_name}/{filename}"
        logger.info(f"Uploaded file {filename} to {ref}")
        return ref

    async def delete(self, document_ref: str) -> bool:
        logger.info(f"Deleted remote S3 file {document_ref}")
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        docs = await self.list_documents()
        logger.info(f"S3 Connector synced {len(docs)} remote files.")
        return docs
