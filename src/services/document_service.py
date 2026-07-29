import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.base import Base
from src.repositories.postgres.models import Document, DocumentPage, OCRJob, ProcessingHistory, User
from src.repositories.postgres.document_repo import DocumentRepository, DocumentPageRepository, OCRJobRepository
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.domain.interfaces.virus_scanner import IVirusScanner, MockVirusScanner
from src.domain.interfaces.event_publisher import IDomainEventPublisher
from src.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.security.file_validator import (
    sanitize_filename,
    calculate_sha256,
    detect_file_type_from_magic_bytes,
)
from src.infrastructure.image_processing.metadata_inspector import PDFInspector, ImageInspector
from src.infrastructure.celery.tasks import process_ocr_document
from src.domain.events.document_events import DocumentUploadedEvent, OCRJobCreatedEvent

logger = logging.getLogger("document_intelligence.document_service")


class DocumentService:
    """Document Ingestion, Validation, Storage, and Queue Dispatching Service."""

    def __init__(
        self,
        db_session: AsyncSession,
        storage_gateway: IStorageGateway,
        virus_scanner: Optional[IVirusScanner] = None,
        event_publisher: Optional[IDomainEventPublisher] = None,
    ):
        self.db = db_session
        self.doc_repo = DocumentRepository(db_session)
        self.job_repo = OCRJobRepository(db_session)
        self.storage = storage_gateway
        self.scanner = virus_scanner or MockVirusScanner()
        self.event_publisher = event_publisher or InMemoryEventBus()

    async def upload_document(
        self,
        file_content: bytes,
        original_filename: str,
        user: User,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Complete document ingestion pipeline:
        Sanitization -> Magic Number Validation -> Virus Scanning -> SHA256 Checksum ->
        Duplicate Check -> PDF/Image Metadata Inspection -> Object Storage Upload ->
        DB Record Creation -> OCR Job Registration -> Celery Queue Dispatch.
        """
        # 1. Sanitize Filename
        clean_filename = sanitize_filename(original_filename)

        # 2. Magic Number & MIME Validation
        ext, content_type = detect_file_type_from_magic_bytes(file_content)

        # 3. Security Anti-Virus Scan
        await self.scanner.scan_bytes(file_content, filename=clean_filename)

        # 4. Calculate SHA-256 Checksum
        checksum = calculate_sha256(file_content)

        # 5. Duplicate Check
        existing_doc = await self.doc_repo.get_by_checksum(checksum)
        if existing_doc:
            logger.info(f"Duplicate document detected (Checksum: {checksum}). Returning existing Document ID: {existing_doc.id}")
            return {
                "document": existing_doc,
                "is_duplicate": True,
                "message": "Duplicate document detected. Existing record returned.",
            }

        # 6. Metadata Inspection
        if ext == "pdf":
            metrics = PDFInspector.inspect(file_content)
        else:
            metrics = ImageInspector.inspect(file_content)

        # 7. Object Storage Upload
        doc_uuid = uuid.uuid4()
        storage_path = f"documents/{user.id}/{doc_uuid}.{ext}"

        import io
        file_stream = io.BytesIO(file_content)
        await self.storage.upload_file(file_stream, storage_path, content_type=content_type)

        # 8. Create Document Database Record
        doc = Document(
            id=doc_uuid,
            user_id=user.id,
            filename=clean_filename,
            content_type=content_type,
            file_size_bytes=len(file_content),
            storage_path=storage_path,
            checksum_sha256=checksum,
            status="ingested",
            page_count=metrics["page_count"],
        )
        created_doc = await self.doc_repo.create(doc)

        # 9. Processing History Log
        history = ProcessingHistory(
            document_id=created_doc.id,
            from_status="pending",
            to_status="ingested",
            message="Document uploaded, validated, and stored successfully.",
        )
        self.db.add(history)

        # 10. OCR Job Registration
        celery_task_id = str(uuid.uuid4())
        job = OCRJob(
            document_id=created_doc.id,
            task_id=celery_task_id,
            priority=priority,
            status="queued",
        )
        created_job = await self.job_repo.create(job)

        # 11. Dispatch Celery Task
        try:
            process_ocr_document.apply_async(
                args=[str(created_doc.id), str(created_job.id), priority],
                task_id=celery_task_id,
            )
        except Exception as e:
            logger.warning(f"Celery Redis broker dispatch warning (Task ID {celery_task_id}): {e}")

        # 12. Publish Domain Events
        await self.event_publisher.publish(
            DocumentUploadedEvent(
                document_id=str(created_doc.id),
                user_id=str(user.id),
                filename=clean_filename,
                file_size_bytes=len(file_content),
                content_type=content_type,
            )
        )
        await self.event_publisher.publish(
            OCRJobCreatedEvent(
                job_id=str(created_job.id),
                document_id=str(created_doc.id),
                task_id=celery_task_id,
                priority=priority,
            )
        )

        return {
            "document": created_doc,
            "job": created_job,
            "metrics": metrics,
            "is_duplicate": False,
        }

    async def get_document_details(self, document_id: uuid.UUID, user: User) -> Optional[Document]:
        doc = await self.doc_repo.get_with_pages_and_ocr(document_id)
        if not doc or (doc.user_id != user.id and not user.is_superuser):
            return None
        return doc

    async def list_user_documents(self, user: User, skip: int = 0, limit: int = 50) -> List[Document]:
        return await self.doc_repo.get_user_documents(user.id, skip=skip, limit=limit)

    async def delete_document(self, document_id: uuid.UUID, user: User) -> bool:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc or (doc.user_id != user.id and not user.is_superuser):
            return False

        # Soft delete in DB
        await self.doc_repo.soft_delete(document_id)

        # Remove from storage
        try:
            await self.storage.delete_file(doc.storage_path)
        except Exception as e:
            logger.error(f"Error removing storage object {doc.storage_path}: {e}")

        return True
