from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class MarkdownResponse(BaseModel):
    document_id: str
    markdown: str


class HTMLResponse(BaseModel):
    document_id: str
    html: str


class ChunkDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_index: int
    content: str
    heading_context: str
    page_references: List[int]


class ChunksResponse(BaseModel):
    document_id: str
    total_chunks: int
    chunks: List[ChunkDTO]


class LayoutBlockDTO(BaseModel):
    node_type: str
    page_number: int
    reading_order: int
    text: str
    bbox: List[float]


class LayoutResponse(BaseModel):
    document_id: str
    total_blocks: int
    blocks: List[LayoutBlockDTO]
