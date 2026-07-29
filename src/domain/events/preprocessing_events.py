from dataclasses import dataclass
from src.domain.events.document_events import DomainEvent


@dataclass
class DocumentRenderedEvent(DomainEvent):
    document_id: str
    page_count: int
    rendering_dpi: int
    profile_name: str

    def __init__(self, document_id: str, page_count: int, rendering_dpi: int, profile_name: str):
        super().__init__()
        self.document_id = document_id
        self.page_count = page_count
        self.rendering_dpi = rendering_dpi
        self.profile_name = profile_name


@dataclass
class PageRenderedEvent(DomainEvent):
    document_id: str
    page_number: int
    width: int
    height: int
    dpi: int

    def __init__(self, document_id: str, page_number: int, width: int, height: int, dpi: int):
        super().__init__()
        self.document_id = document_id
        self.page_number = page_number
        self.width = width
        self.height = height
        self.dpi = dpi


@dataclass
class PreprocessingCompletedEvent(DomainEvent):
    document_id: str
    pages_processed: int
    total_duration_ms: float

    def __init__(self, document_id: str, pages_processed: int, total_duration_ms: float):
        super().__init__()
        self.document_id = document_id
        self.pages_processed = pages_processed
        self.total_duration_ms = total_duration_ms
