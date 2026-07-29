import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.rag_service import RAGService
from src.api.schemas.rag import (
    ChatRequest,
    ChatResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    CitationDetailDTO,
)

router = APIRouter(tags=["AI Agents & RAG Conversation Engine"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Conversational Chat with Documents & Memory.
    Generates structured answer with inline citations, page numbers, and bounding boxes.
    """
    session_id = payload.session_id or str(uuid.uuid4())
    doc_uuid = uuid.UUID(payload.document_id) if payload.document_id else None

    rag_service = RAGService(db)
    res = await rag_service.chat(
        session_id=session_id,
        user_message=payload.message,
        document_id=doc_uuid,
        user_id=current_user.id,
        top_k=payload.top_k,
    )

    citation_dtos = [CitationDetailDTO(**c) for c in res["citations"]]
    return ChatResponse(
        session_id=res["session_id"],
        answer=res["answer"],
        citations=citation_dtos,
        tokens_used=res["tokens_used"],
    )


@router.post("/rag/query", response_model=RAGQueryResponse)
async def execute_rag_query(
    payload: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute direct Retrieval-Augmented Generation (RAG) query against document knowledge base."""
    session_id = str(uuid.uuid4())
    doc_uuid = uuid.UUID(payload.document_id) if payload.document_id else None

    rag_service = RAGService(db)
    res = await rag_service.chat(
        session_id=session_id,
        user_message=payload.query,
        document_id=doc_uuid,
        user_id=current_user.id,
        top_k=payload.top_k,
    )

    citation_dtos = [CitationDetailDTO(**c) for c in res["citations"]]
    return RAGQueryResponse(
        answer=res["answer"],
        citations=citation_dtos,
        tokens_used=res["tokens_used"],
        duration_ms=120.5,
    )
