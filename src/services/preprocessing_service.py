import io
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.postgres.models import Document, DocumentPage, OCRJob, ProcessingHistory
from src.repositories.postgres.document_repo import DocumentRepository, DocumentPageRepository, OCRJobRepository
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.domain.interfaces.event_publisher import IDomainEventPublisher
from src.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.image_processing.pdf_renderer import PDFRenderingEngine, PROFILES, RenderingProfile
from src.infrastructure.image_processing.pipeline import PreprocessingPipeline
from src.infrastructure.image_processing.quality_analyzer import ImageQualityAnalyzer, ImageClassifier
from src.infrastructure.image_processing.thumbnail_generator import ThumbnailGenerator
from src.domain.events.preprocessing_events import DocumentRenderedEvent, PageRenderedEvent, PreprocessingCompletedEvent

logger = logging.getLogger("document_intelligence.preprocessing_service")


class DocumentPreprocessingService:
    """Orchestrator Service for PDF Rendering, Preprocessing Pipeline, Quality Assessment, and DB Page Registration."""

    def __init__(
        self,
        db_session: AsyncSession,
        storage_gateway: IStorageGateway,
        pipeline: Optional[PreprocessingPipeline] = None,
        event_publisher: Optional[IDomainEventPublisher] = None,
    ):
        self.db = db_session
        self.doc_repo = DocumentRepository(db_session)
        self.page_repo = DocumentPageRepository(db_session)
        self.job_repo = OCRJobRepository(db_session)
        self.storage = storage_gateway
        self.pipeline = pipeline or PreprocessingPipeline()
        self.event_publisher = event_publisher or InMemoryEventBus()

    async def process_document_pages(
        self, document_id: uuid.UUID, profile_name: str = "balanced"
    ) -> List[DocumentPage]:
        """
        Full Phase 4 Processing Workflow:
        1. Fetch Document from Storage
        2. Render PDF Pages / Decode Image
        3. Execute Preprocessing Plugins (deskew, denoise, CLAHE, sharpen)
        4. Compute Quality Metrics & Classify Document Type
        5. Generate Multi-Scale Thumbnails (128px, 256px, 512px)
        6. Store Artifacts in Object Storage (rendered/, preprocessed/, thumbnails/)
        7. Persist DocumentPage Records to PostgreSQL
        8. Transition Document & OCRJob Status
        """
        start_time = time.perf_counter()

        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        # 1. Download raw original file from storage
        raw_file_bytes = await self.storage.download_file(doc.storage_path)

        # 2. Select Rendering Strategy & Render Pages
        profile = PROFILES.get(profile_name, PROFILES["balanced"])
        if doc.content_type == "application/pdf":
            rendered_pages = PDFRenderingEngine.render_pdf_bytes(raw_file_bytes, profile=profile)
        else:
            rendered_pages = PDFRenderingEngine.render_image_bytes(raw_file_bytes)

        await self.event_publisher.publish(
            DocumentRenderedEvent(
                document_id=str(doc.id),
                page_count=len(rendered_pages),
                rendering_dpi=profile.dpi,
                profile_name=profile.name,
            )
        )

        created_page_records: List[DocumentPage] = []

        for page_num, raw_bgr_img, raw_png_bytes in rendered_pages:
            # 3. Execute Preprocessing Plugins Pipeline
            preprocessed_img, pipeline_metrics = self.pipeline.execute(raw_bgr_img)

            # 4. Image Quality Analysis
            quality_metrics = ImageQualityAnalyzer.analyze(preprocessed_img)
            skew_angle = next(
                (p["skew_angle"] for p in pipeline_metrics["plugins_executed"] if "skew_angle" in p), 0.0
            )

            # 5. Generate Thumbnails
            thumbnails = ThumbnailGenerator.generate_thumbnails(preprocessed_img)

            # 6. Store Preprocessed Page Artifacts in Storage
            preprocessed_png_bytes = cv2.imencode(".png", preprocessed_img)[1].tobytes()

            rendered_path = f"rendered/{doc.id}/page_{page_num}.png"
            preprocessed_path = f"preprocessed/{doc.id}/page_{page_num}.png"
            thumb_path = f"thumbnails/{doc.id}/page_{page_num}_thumb_256.png"

            await self.storage.upload_file(io.BytesIO(raw_png_bytes), rendered_path, content_type="image/png")
            await self.storage.upload_file(
                io.BytesIO(preprocessed_png_bytes), preprocessed_path, content_type="image/png"
            )
            await self.storage.upload_file(
                io.BytesIO(thumbnails["medium"]), thumb_path, content_type="image/png"
            )

            # 7. Create DocumentPage Entity
            page_record = DocumentPage(
                document_id=doc.id,
                page_number=page_num,
                image_storage_path=preprocessed_path,
                width=quality_metrics["width"],
                height=quality_metrics["height"],
                dpi=profile.dpi,
                deskew_angle=skew_angle,
            )
            saved_page = await self.page_repo.create(page_record)
            created_page_records.append(saved_page)

            await self.event_publisher.publish(
                PageRenderedEvent(
                    document_id=str(doc.id),
                    page_number=page_num,
                    width=quality_metrics["width"],
                    height=quality_metrics["height"],
                    dpi=profile.dpi,
                )
            )

        # 8. Update Document and Job Status
        doc.status = "preprocessed"
        doc.page_count = len(created_page_records)
        await self.doc_repo.update(doc)

        history = ProcessingHistory(
            document_id=doc.id,
            from_status="ingested",
            to_status="preprocessed",
            message=f"Successfully rendered and preprocessed {len(created_page_records)} pages at {profile.dpi} DPI.",
        )
        self.db.add(history)

        total_duration = round((time.perf_counter() - start_time) * 1000, 2)
        await self.event_publisher.publish(
            PreprocessingCompletedEvent(
                document_id=str(doc.id),
                pages_processed=len(created_page_records),
                total_duration_ms=total_duration,
            )
        )

        return created_page_records
