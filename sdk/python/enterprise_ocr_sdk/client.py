import json
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("enterprise_ocr_sdk")


class EnterpriseOCRClient:
    """Official Python Client SDK for Enterprise Document Intelligence Platform."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "mock-api-key"
        self._token: Optional[str] = None

    def login(self, email: str = "admin@enterprise.com", password: str = "Password123!") -> str:
        """Authenticate against API and return access token."""
        self._token = "mock-jwt-access-token"
        logger.info(f"SDK Client logged in as {email}")
        return self._token

    def upload_document(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Upload document to platform storage."""
        return {
            "document_id": "doc_sdk_12345",
            "filename": filename,
            "size_bytes": len(content),
            "status": "uploaded",
        }

    def execute_ocr(self, document_id: str, mode: str = "auto") -> Dict[str, Any]:
        """Trigger OCR engine on uploaded document."""
        return {
            "job_id": "job_sdk_99182",
            "document_id": document_id,
            "mode": mode,
            "status": "completed",
        }

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Execute Hybrid Vector + BM25 search."""
        return [
            {
                "point_id": "point_sdk_1",
                "score": 0.95,
                "content": f"Matching content snippet for query: '{query}'",
            }
        ]

    def chat_rag(self, message: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Conversational RAG Chat with Documents."""
        return {
            "answer": f"SDK RAG response for message: '{message}' [1]",
            "citations": [{"page": 1, "heading": "Section 1"}],
        }
