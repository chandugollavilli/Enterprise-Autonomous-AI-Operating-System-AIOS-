from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CitationDetailDTO(BaseModel):
    citation_index: int
    document_id: str
    chunk_id: str
    page_number: int
    heading_context: str
    bbox: List[float]
    confidence: float
    source_text: str


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    document_id: Optional[str] = None
    top_k: int = 5


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: List[CitationDetailDTO]
    tokens_used: int


class RAGQueryRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    prompt_id: str = "qa_default"
    top_k: int = 5


class RAGQueryResponse(BaseModel):
    answer: str
    citations: List[CitationDetailDTO]
    tokens_used: int
    duration_ms: float
