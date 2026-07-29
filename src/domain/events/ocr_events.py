from dataclasses import dataclass
from src.domain.events.document_events import DomainEvent


@dataclass
class OCRStartedEvent(DomainEvent):
    document_id: str
    job_id: str
    page_count: int

    def __init__(self, document_id: str, job_id: str, page_count: int):
        super().__init__()
        self.document_id = document_id
        self.job_id = job_id
        self.page_count = page_count


@dataclass
class OCRCompletedEvent(DomainEvent):
    document_id: str
    job_id: str
    total_text_length: int
    processing_time_ms: int

    def __init__(self, document_id: str, job_id: str, total_text_length: int, processing_time_ms: int):
        super().__init__()
        self.document_id = document_id
        self.job_id = job_id
        self.total_text_length = total_text_length
        self.processing_time_ms = processing_time_ms


@dataclass
class OCRFailedEvent(DomainEvent):
    document_id: str
    job_id: str
    error_message: str

    def __init__(self, document_id: str, job_id: str, error_message: str):
        super().__init__()
        self.document_id = document_id
        self.job_id = job_id
        self.error_message = error_message
