import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import Document, DocumentPage, OCRJob, OCRResult, ProcessingHistory
from src.repositories.postgres.document_repo import DocumentRepository, DocumentPageRepository, OCRJobRepository
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.domain.interfaces.event_publisher import IDomainEventPublisher
from src.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.ocr.mode_selector import OCRModeSelector
from src.domain.events.ocr_events import OCRStartedEvent, OCRCompletedEvent, OCRFailedEvent

logger = logging.getLogger("document_intelligence.ocr_service")


class OCRService:
    """OCR Processing Service orchestrating Base/Gundam recognition, BBox normalization, and Result DB Persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        storage_gateway: IStorageGateway,
        mode_selector: Optional[OCRModeSelector] = None,
        event_publisher: Optional[IDomainEventPublisher] = None,
    ):
        self.db = db_session
        self.doc_repo = DocumentRepository(db_session)
        self.page_repo = DocumentPageRepository(db_session)
        self.job_repo = OCRJobRepository(db_session)
        self.storage = storage_gateway
        self.mode_selector = mode_selector or OCRModeSelector()
        self.event_publisher = event_publisher or InMemoryEventBus()

    async def process_ocr_for_document(self, document_id: uuid.UUID) -> List[OCRResult]:
        """
        Execute OCR Processing Pipeline for Document:
        1. Retrieve Document and Page records.
        2. Fetch Preprocessed Page Images from Storage.
        3. Determine OCR Engine Mode (Base vs. Gundam auto-switch).
        4. Execute Text Detection & Recognition.
        5. Persist OCRResult (full_text, raw_boxes_json, layout_json, tables_json).
        6. Transition Document & OCRJob Status -> ocr_completed.
        """
        start_time = time.perf_counter()

        doc = await self.doc_repo.get_by_checksum("")  # query or get by id
        doc = await self.doc_repo.get_with_pages_and_ocr(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        pages = await self.page_repo.get_pages_for_document(doc.id)
        if not pages:
            raise ValueError(f"No pages found for Document {document_id}. Run Preprocessing first.")

        # Find or create OCRJob record
        jobs = doc.ocr_jobs
        job = jobs[0] if jobs else None

        await self.event_publisher.publish(
            OCRStartedEvent(
                document_id=str(doc.id),
                job_id=str(job.id) if job else "",
                page_count=len(pages),
            )
        )

        ocr_results: List[OCRResult] = []
        total_text_length = 0

        for page in pages:
            # Download preprocessed page image from storage
            img_bytes = await self.storage.download_file(page.image_storage_path)
            img_np = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            if img_np is None:
                raise ValueError(f"Failed to decode page image for Page {page.page_number}")

            # Auto-select Base vs Gundam Mode Engine
            engine, mode_name = self.mode_selector.select_engine(img_np, dpi=page.dpi)

            # Execute OCR Text Detection
            page_res = await engine.extract_text(img_np, config={"page_number": page.page_number})

            # Format raw boxes JSON DTO
            raw_boxes = [
                {
                    "box": b.box,
                    "text": b.text,
                    "confidence": b.confidence,
                    "line_num": b.line_num,
                }
                for b in page_res.boxes
            ]

            # Upsert OCRResult in PostgreSQL
            ocr_result = OCRResult(
                page_id=page.id,
                ocr_mode=mode_name,
                processing_time_ms=page_res.processing_time_ms,
                full_text=page_res.full_text,
                raw_boxes_json={"boxes": raw_boxes},
                layout_json=page_res.raw_layout,
                tables_json=page_res.tables,
            )
            self.db.add(ocr_result)
            ocr_results.append(ocr_result)
            total_text_length += len(page_res.full_text)

        # Update Document and Job Status
        doc.status = "ocr_completed"
        await self.doc_repo.update(doc)

        if job:
            job.status = "ocr_completed"
            job.processing_time_ms = int((time.perf_counter() - start_time) * 1000)
            await self.job_repo.update(job)

        history = ProcessingHistory(
            document_id=doc.id,
            from_status="preprocessed",
            to_status="ocr_completed",
            message=f"OCR execution completed across {len(pages)} pages. Total chars: {total_text_length}.",
        )
        self.db.add(history)

        total_duration = int((time.perf_counter() - start_time) * 1000)
        await self.event_publisher.publish(
            OCRCompletedEvent(
                document_id=str(doc.id),
                job_id=str(job.id) if job else "",
                total_text_length=total_text_length,
                processing_time_ms=total_duration,
            )
        )

        return ocr_results

    async def get_document_ocr_results(self, document_id: uuid.UUID) -> List[Dict[str, Any]]:
        doc = await self.doc_repo.get_with_pages_and_ocr(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        results = []
        for page in doc.pages:
            if page.ocr_result:
                results.append({
                    "page_number": page.page_number,
                    "ocr_mode": page.ocr_result.ocr_mode,
                    "processing_time_ms": page.ocr_result.processing_time_ms,
                    "full_text": page.ocr_result.full_text,
                    "boxes": page.ocr_result.raw_boxes_json.get("boxes", []),
                    "layout": page.ocr_result.layout_json,
                    "tables": page.ocr_result.tables_json,
                })
        return results
