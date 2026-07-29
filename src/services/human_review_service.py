import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.postgres.models import OCRResult, AuditLog
from src.repositories.postgres.document_repo import DocumentRepository

logger = logging.getLogger("document_intelligence.human_review")


class HumanReviewService:
    """Service handling low-confidence OCR flagging, manual corrections, and reviewer approval workflows."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.doc_repo = DocumentRepository(db_session)

    async def submit_correction(
        self,
        page_id: uuid.UUID,
        corrected_text: str,
        corrected_boxes: List[Dict[str, Any]],
        reviewer_id: uuid.UUID,
    ) -> OCRResult:
        """Apply manual reviewer text correction to OCRResult and log audit trail."""
        result = await self.db.get(OCRResult, page_id)
        if not result:
            raise ValueError(f"OCRResult for Page {page_id} not found.")

        # Log audit trail for correction history
        audit = AuditLog(
            user_id=reviewer_id,
            action="ocr_correction_submitted",
            resource_type="OCRResult",
            resource_id=str(result.id),
            details={
                "previous_text": result.full_text,
                "corrected_text": corrected_text,
            },
        )
        self.db.add(audit)

        # Update OCRResult with reviewer corrections
        result.full_text = corrected_text
        result.raw_boxes_json = {"boxes": corrected_boxes, "corrected_by": str(reviewer_id)}
        await self.db.commit()

        logger.info(f"Reviewer {reviewer_id} submitted OCR correction for Page {page_id}")
        return result
