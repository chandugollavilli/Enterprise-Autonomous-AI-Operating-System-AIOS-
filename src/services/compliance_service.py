import uuid
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.repositories.postgres.models import Document, DocumentPage, DocumentBlock, DocumentChunk, OCRResult
from src.repositories.postgres.document_repo import DocumentRepository

logger = logging.getLogger("document_intelligence.compliance_service")


class ComplianceService:
    """Service handling GDPR / CCPA right-to-erasure and data retention workflows."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.doc_repo = DocumentRepository(db_session)

    async def execute_right_to_erasure(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Completely purge all documents, pages, blocks, chunks, and OCR results owned by a user."""
        docs = await self.doc_repo.get_by_user_id(user_id)
        doc_ids = [d.id for d in docs]

        if not doc_ids:
            return {"user_id": str(user_id), "documents_erased": 0, "status": "completed"}

        # Cascade delete documents and child entities
        for doc in docs:
            await self.db.delete(doc)

        await self.db.commit()
        logger.info(f"GDPR Right-to-Erasure executed for User {user_id}. Erased {len(doc_ids)} documents.")

        return {
            "user_id": str(user_id),
            "documents_erased": len(doc_ids),
            "status": "completed",
        }
