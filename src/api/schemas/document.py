from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class OCRJobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    priority: str
    status: str
    retry_count: int
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: str


class DocumentMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str
    file_size_bytes: int
    checksum_sha256: str
    status: str
    page_count: int
    storage_path: str
    download_url: Optional[str] = None
    created_at: str


class DocumentUploadResponse(BaseModel):
    document: DocumentMetadataResponse
    job: Optional[OCRJobStatusResponse] = None
    is_duplicate: bool = False
    message: str = "Document uploaded successfully and queued for OCR processing."


class DocumentListResponse(BaseModel):
    items: List[DocumentMetadataResponse]
    total: int
    skip: int
    limit: int
