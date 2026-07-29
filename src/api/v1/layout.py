import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, HTMLResponse as FastAPIHTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.api.dependencies import get_current_user, get_storage
from src.repositories.postgres.models import User
from src.services.layout_service import LayoutService
from src.infrastructure.layout.exporters.markdown_exporter import MarkdownGenerator
from src.infrastructure.layout.exporters.html_exporter import HTML5Generator
from src.infrastructure.layout.exporters.json_exporter import JSONExporter
from src.api.schemas.layout import (
    MarkdownResponse,
    HTMLResponse,
    ChunksResponse,
    ChunkDTO,
    LayoutResponse,
    LayoutBlockDTO,
)

router = APIRouter(prefix="/documents", tags=["Document Layout & Structure"])


@router.get("/{document_id}/markdown", response_model=MarkdownResponse)
async def get_document_markdown(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Generate and return GitHub Flavored Markdown (GFM) export."""
    layout_service = LayoutService(db, storage)
    try:
        cdm, md, html, chunks = await layout_service.process_and_persist_layout(document_id)
        return MarkdownResponse(document_id=str(document_id), markdown=md)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{document_id}/html", response_model=HTMLResponse)
async def get_document_html(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Generate and return semantic HTML5 export."""
    layout_service = LayoutService(db, storage)
    try:
        cdm, md, html, chunks = await layout_service.process_and_persist_layout(document_id)
        return HTMLResponse(document_id=str(document_id), html=html)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{document_id}/json")
async def get_document_json(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Generate and return Canonical Document Model (CDM) structured JSON tree."""
    layout_service = LayoutService(db, storage)
    try:
        cdm = await layout_service.build_canonical_document(document_id)
        return JSONExporter.generate(cdm)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{document_id}/chunks", response_model=ChunksResponse)
async def get_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Retrieve heading-aware semantic chunks prepared for RAG vector indexing (Phase 8)."""
    layout_service = LayoutService(db, storage)
    try:
        cdm, md, html, chunks = await layout_service.process_and_persist_layout(document_id)
        chunk_dtos = [
            ChunkDTO(
                id=str(c.id),
                chunk_index=c.chunk_index,
                content=c.content,
                heading_context=c.heading_context,
                page_references=c.page_references_json.get("pages", []),
            )
            for c in chunks
        ]
        return ChunksResponse(
            document_id=str(document_id),
            total_chunks=len(chunk_dtos),
            chunks=chunk_dtos,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{document_id}/layout", response_model=LayoutResponse)
async def get_document_layout(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: IStorageGateway = Depends(get_storage),
):
    """Retrieve raw layout blocks ordered by spatial reading order."""
    layout_service = LayoutService(db, storage)
    try:
        cdm = await layout_service.build_canonical_document(document_id)
        ordered_nodes = cdm.get_ordered_nodes()
        block_dtos = [
            LayoutBlockDTO(
                node_type=n.node_type.value,
                page_number=n.page_number,
                reading_order=n.reading_order,
                text=n.text,
                bbox=n.bbox,
            )
            for n in ordered_nodes
        ]
        return LayoutResponse(
            document_id=str(document_id),
            total_blocks=len(block_dtos),
            blocks=block_dtos,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
