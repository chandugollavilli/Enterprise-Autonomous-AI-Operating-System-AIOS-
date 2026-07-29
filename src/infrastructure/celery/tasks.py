import asyncio
import uuid
import logging
from celery.exceptions import MaxRetriesExceededError
from src.infrastructure.celery.app import celery_app
from src.infrastructure.postgres.database import AsyncSessionFactory
from src.repositories.storage.factory import get_storage_gateway
from src.services.preprocessing_service import DocumentPreprocessingService
from src.services.ocr_service import OCRService
from src.repositories.postgres.document_repo import OCRJobRepository

logger = logging.getLogger("document_intelligence.celery_tasks")


def run_async(coro):
    """Run an async coroutine inside a synchronous Celery worker function cleanly."""
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(lambda: asyncio.run(coro)).result()
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(
    bind=True,
    name="src.infrastructure.celery.tasks.process_ocr_document",
    max_retries=3,
    default_retry_delay=10,
    backoff=True,
)
def process_ocr_document(self, document_id: str, job_id: str, priority: str = "normal"):
    """
    Production Celery Worker Task:
    Executes DocumentPreprocessingService (Phase 4) -> OCRService (Phase 5).
    Updates task state: PROGRESS (rendering/preprocessing/ocr) -> SUCCESS / FAILURE.
    Reroutes to Dead-Letter Queue (DLQ) if max retries exceeded.
    """
    logger.info(
        f"[Celery Worker] Starting OCR Pipeline for Document: {document_id} (Job ID: {job_id}, Priority: {priority})"
    )

    doc_uuid = uuid.UUID(document_id)

    async def _execute_pipeline():
        async with AsyncSessionFactory() as session:
            storage = get_storage_gateway()
            job_repo = OCRJobRepository(session)
            job = await job_repo.get_by_id(uuid.UUID(job_id))

            # 1. Update State -> PROGRESS (Preprocessing Phase 4)
            self.update_state(state="PROGRESS", meta={"stage": "preprocessing", "progress": 25})
            if job:
                job.status = "processing"
                await job_repo.update(job)
                await session.commit()

            # 2. Execute Document Preprocessing & Multi-DPI Rendering
            preprocessor = DocumentPreprocessingService(session, storage)
            await preprocessor.process_document_pages(doc_uuid)
            await session.commit()

            # 3. Update State -> PROGRESS (OCR Phase 5)
            self.update_state(state="PROGRESS", meta={"stage": "ocr_extraction", "progress": 75})

            # 4. Execute OCR Text Recognition & BBox Extraction
            ocr_service = OCRService(session, storage)
            await ocr_service.process_ocr_for_document(doc_uuid)
            await session.commit()

            return {"status": "ocr_completed", "document_id": document_id, "job_id": job_id}

    try:
        result = run_async(_execute_pipeline())
        logger.info(f"[Celery Worker] Successfully completed OCR Pipeline for Document: {document_id}")
        return result
    except Exception as exc:
        logger.error(f"[Celery Worker] Error executing OCR pipeline for {document_id}: {exc}", exc_info=True)
        try:
            # Exponential Backoff Retry
            raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
        except MaxRetriesExceededError:
            logger.critical(
                f"[Celery Worker] Max retries (3) exceeded for Document {document_id}. Rerouting job to Dead-Letter Queue (ocr_dlq)."
            )
            # Reroute failed job metadata to DLQ
            async def _mark_dlq():
                async with AsyncSessionFactory() as session:
                    job_repo = OCRJobRepository(session)
                    j = await job_repo.get_by_id(uuid.UUID(job_id))
                    if j:
                        j.status = "dead_lettered"
                        j.error_message = f"Max retries exceeded: {exc}"
                        await job_repo.update(j)
                        await session.commit()

            run_async(_mark_dlq())
            raise exc
