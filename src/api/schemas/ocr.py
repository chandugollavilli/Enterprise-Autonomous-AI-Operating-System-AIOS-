from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class OCRBoxDTO(BaseModel):
    box: List[float]  # [x1, y1, x2, y2]
    text: str
    confidence: float
    line_num: int


class OCRPageResultDTO(BaseModel):
    page_number: int
    ocr_mode: str
    processing_time_ms: int
    full_text: str
    boxes: List[OCRBoxDTO]
    layout: Dict[str, Any]
    tables: Dict[str, Any]


class OCRDocumentResultResponse(BaseModel):
    document_id: str
    status: str
    page_count: int
    pages: List[OCRPageResultDTO]
