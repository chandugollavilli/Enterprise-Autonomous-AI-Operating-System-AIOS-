import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.vector_search_service import VectorSearchService
from src.api.schemas.search import SearchQueryRequest, SearchResponse, SearchResultDTO

router = APIRouter(prefix="/search", tags=["Semantic & Hybrid Search"])


@router.post("", response_model=SearchResponse)
@router.post("/hybrid", response_model=SearchResponse)
async def perform_hybrid_search(
    payload: SearchQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute Hybrid Search: BAAI bge-m3 dense vector similarity + BM25 keyword matching + BGE Cross-Encoder Reranking.
    """
    search_service = VectorSearchService(db)
    raw_results = await search_service.search(
        query=payload.query,
        top_k=payload.top_k,
        filters=payload.filters,
        user_id=current_user.id,
        search_type="hybrid",
    )

    dtos = [
        SearchResultDTO(
            point_id=r["point_id"],
            score=r.get("final_score", r.get("score", 0.0)),
            chunk_id=r["payload"].get("chunk_id", ""),
            document_id=r["payload"].get("document_id", ""),
            chunk_index=r["payload"].get("chunk_index", 0),
            content=r["payload"].get("content", ""),
            heading_context=r["payload"].get("heading_context", ""),
            pages=r["payload"].get("pages", []),
            bboxes=r["payload"].get("bboxes", []),
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=payload.query,
        total_results=len(dtos),
        results=dtos,
    )


@router.post("/vector", response_model=SearchResponse)
async def perform_vector_search(
    payload: SearchQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute pure Qdrant dense vector similarity search."""
    search_service = VectorSearchService(db)
    raw_results = await search_service.search(
        query=payload.query,
        top_k=payload.top_k,
        filters=payload.filters,
        user_id=current_user.id,
        search_type="vector",
    )

    dtos = [
        SearchResultDTO(
            point_id=r["point_id"],
            score=r.get("score", 0.0),
            chunk_id=r["payload"].get("chunk_id", ""),
            document_id=r["payload"].get("document_id", ""),
            chunk_index=r["payload"].get("chunk_index", 0),
            content=r["payload"].get("content", ""),
            heading_context=r["payload"].get("heading_context", ""),
            pages=r["payload"].get("pages", []),
            bboxes=r["payload"].get("bboxes", []),
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=payload.query,
        total_results=len(dtos),
        results=dtos,
    )


@router.get("/documents/{document_id}/related", response_model=SearchResponse)
async def get_related_documents(
    document_id: uuid.UUID,
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Find related documents based on vector content similarity."""
    search_service = VectorSearchService(db)
    raw_results = await search_service.find_similar_documents(document_id, top_k=top_k)

    dtos = [
        SearchResultDTO(
            point_id=r["point_id"],
            score=r.get("score", 0.0),
            chunk_id=r["payload"].get("chunk_id", ""),
            document_id=r["payload"].get("document_id", ""),
            chunk_index=r["payload"].get("chunk_index", 0),
            content=r["payload"].get("content", ""),
            heading_context=r["payload"].get("heading_context", ""),
            pages=r["payload"].get("pages", []),
            bboxes=r["payload"].get("bboxes", []),
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=f"related_to:{document_id}",
        total_results=len(dtos),
        results=dtos,
    )
