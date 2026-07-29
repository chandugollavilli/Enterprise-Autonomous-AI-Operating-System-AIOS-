from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SearchQueryRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None
    enable_reranking: bool = True


class SearchResultDTO(BaseModel):
    point_id: str
    score: float
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    heading_context: str
    pages: List[int]
    bboxes: List[List[float]]


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultDTO]
