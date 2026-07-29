import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.api.dependencies import get_current_user, get_storage
from src.repositories.postgres.models import User
from src.services.ocr_service import OCRService
from src.api.schemas.ocr import OCRDocumentResultResponse, OCRPageResultDTO

router = APIRouter(prefix="/ocr", tags=["OCR Engine"])


@router.post("/process/{document_id}", response_model=OCRDocumentResultResponse)
async def process_document_ocr(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """
    Trigger OCR text detection & recognition pipeline for a document.
    Auto-switches between Base Mode (Standard) and Gundam Mode (High-Res/Tile).
    """
    ocr_service = OCRService(db, storage)
    try:
        await ocr_service.process_ocr_for_document(document_id)
        results = await ocr_service.get_document_ocr_results(document_id)

        page_dtos = [OCRPageResultDTO(**r) for r in results]
        return OCRDocumentResultResponse(
            document_id=str(document_id),
            status="ocr_completed",
            page_count=len(page_dtos),
            pages=page_dtos,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/results/{document_id}", response_model=OCRDocumentResultResponse)
async def get_ocr_results(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Retrieve structured OCR extraction results for a document."""
    ocr_service = OCRService(db, storage)
    try:
        results = await ocr_service.get_document_ocr_results(document_id)
        page_dtos = [OCRPageResultDTO(**r) for r in results]
        return OCRDocumentResultResponse(
            document_id=str(document_id),
            status="ocr_completed" if page_dtos else "pending",
            page_count=len(page_dtos),
            pages=page_dtos,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
