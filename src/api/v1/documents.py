import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.api.dependencies import get_current_user, get_storage
from src.repositories.postgres.models import User
from src.services.document_service import DocumentService
from src.api.schemas.document import (
    DocumentUploadResponse,
    DocumentMetadataResponse,
    DocumentListResponse,
    OCRJobStatusResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    priority: str = Query("normal", pattern="^(low|normal|high)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """
    Ingest a document (PDF, PNG, JPEG, TIFF, BMP, WEBP).
    Validates magic bytes, checks for duplicates, extracts metadata, stores file, and queues Celery OCR job.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    doc_service = DocumentService(db, storage)
    try:
        res = await doc_service.upload_document(
            file_content=content,
            original_filename=file.filename or "upload.pdf",
            user=current_user,
            priority=priority,
        )
        doc = res["document"]
        job = res.get("job")

        download_url = await storage.get_file_url(doc.storage_path)

        doc_dto = DocumentMetadataResponse(
            id=str(doc.id),
            filename=doc.filename,
            content_type=doc.content_type,
            file_size_bytes=doc.file_size_bytes,
            checksum_sha256=doc.checksum_sha256,
            status=doc.status,
            page_count=doc.page_count,
            storage_path=doc.storage_path,
            download_url=download_url,
            created_at=doc.created_at.isoformat(),
        )

        job_dto = (
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
            if job
            else None
        )

        return DocumentUploadResponse(
            document=doc_dto,
            job=job_dto,
            is_duplicate=res["is_duplicate"],
            message=res.get("message", "Document uploaded successfully and queued for OCR."),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Retrieve paginated documents owned by current user."""
    doc_service = DocumentService(db, storage)
    docs = await doc_service.list_user_documents(current_user, skip=skip, limit=limit)
    
    items = []
    for doc in docs:
        url = await storage.get_file_url(doc.storage_path)
        items.append(
            DocumentMetadataResponse(
                id=str(doc.id),
                filename=doc.filename,
                content_type=doc.content_type,
                file_size_bytes=doc.file_size_bytes,
                checksum_sha256=doc.checksum_sha256,
                status=doc.status,
                page_count=doc.page_count,
                storage_path=doc.storage_path,
                download_url=url,
                created_at=doc.created_at.isoformat(),
            )
        )

    return DocumentListResponse(
        items=items,
        total=len(items),
        skip=skip,
        limit=limit,
    )


@router.get("/{document_id}", response_model=DocumentMetadataResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Get document details by ID."""
    doc_service = DocumentService(db, storage)
    doc = await doc_service.get_document_details(document_id, current_user)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    download_url = await storage.get_file_url(doc.storage_path)
    return DocumentMetadataResponse(
        id=str(doc.id),
        filename=doc.filename,
        content_type=doc.content_type,
        file_size_bytes=doc.file_size_bytes,
        checksum_sha256=doc.checksum_sha256,
        status=doc.status,
        page_count=doc.page_count,
        storage_path=doc.storage_path,
        download_url=download_url,
        created_at=doc.created_at.isoformat(),
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Delete a document by ID."""
    doc_service = DocumentService(db, storage)
    success = await doc_service.delete_document(document_id, current_user)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or access denied.")
    return None
