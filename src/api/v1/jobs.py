import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User, OCRJob
from src.repositories.postgres.document_repo import OCRJobRepository
from src.api.schemas.document import OCRJobStatusResponse
from src.infrastructure.celery.tasks import process_ocr_document

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobListResponse(BaseModel := type("BaseModel", (), {})):
    pass


from pydantic import BaseModel


class JobListResponse(BaseModel):
    items: List[OCRJobStatusResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List OCR jobs with optional status and priority filtering."""
    repo = OCRJobRepository(db)
    all_jobs = await repo.get_all(skip=skip, limit=limit)

    filtered = []
    for job in all_jobs:
        if status_filter and job.status != status_filter:
            continue
        if priority_filter and job.priority != priority_filter:
            continue
        filtered.append(
            OCRJobStatusResponse(
                id=str(job.id),
                task_id=job.task_id,
                priority=job.priority,
                status=job.status,
                retry_count=job.retry_count,
                error_message=job.error_message,
                processing_time_ms=job.processing_time_ms,
                created_at=job.created_at.isoformat(),
            )
        )

    return JobListResponse(
        items=filtered,
        total=len(filtered),
        skip=skip,
        limit=limit,
    )


@router.get("/{job_id}", response_model=OCRJobStatusResponse)
async def get_job_status(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve status of an OCR job."""
    repo = OCRJobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OCR job not found.")

    return OCRJobStatusResponse(
        id=str(job.id),
        task_id=job.task_id,
        priority=job.priority,
        status=job.status,
        retry_count=job.retry_count,
        error_message=job.error_message,
        processing_time_ms=job.processing_time_ms,
        created_at=job.created_at.isoformat(),
    )


@router.post("/{job_id}/retry", response_model=OCRJobStatusResponse)
async def retry_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-queue a failed or dead-lettered job back into the Celery priority queue."""
    repo = OCRJobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OCR job not found.")

    # Generate new Celery Task ID and reset status
    new_task_id = str(uuid.uuid4())
    job.task_id = new_task_id
    job.status = "queued"
    job.error_message = None
    await repo.update(job)

    # Re-dispatch to Celery
    try:
        process_ocr_document.apply_async(
            args=[str(job.document_id), str(job.id), job.priority],
            task_id=new_task_id,
        )
    except Exception as e:
        pass

    return OCRJobStatusResponse(
        id=str(job.id),
        task_id=job.task_id,
        priority=job.priority,
        status=job.status,
        retry_count=job.retry_count,
        error_message=job.error_message,
        processing_time_ms=job.processing_time_ms,
        created_at=job.created_at.isoformat(),
    )


@router.patch("/{job_id}/cancel", response_model=OCRJobStatusResponse)
async def cancel_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a pending or queued OCR job."""
    repo = OCRJobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OCR job not found.")

    job.status = "cancelled"
    await repo.update(job)

    return OCRJobStatusResponse(
        id=str(job.id),
        task_id=job.task_id,
        priority=job.priority,
        status=job.status,
        retry_count=job.retry_count,
        error_message=job.error_message,
        processing_time_ms=job.processing_time_ms,
        created_at=job.created_at.isoformat(),
    )
