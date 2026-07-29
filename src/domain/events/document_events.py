import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DomainEvent:
    event_id: str
    occurred_at: str

    def __init__(self):
        self.event_id = str(uuid.uuid4())
        self.occurred_at = datetime.now(timezone.utc).isoformat()


@dataclass
class DocumentUploadedEvent(DomainEvent):
    document_id: str
    user_id: str
    filename: str
    file_size_bytes: int
    content_type: str

    def __init__(self, document_id: str, user_id: str, filename: str, file_size_bytes: int, content_type: str):
        super().__init__()
        self.document_id = document_id
        self.user_id = user_id
        self.filename = filename
        self.file_size_bytes = file_size_bytes
        self.content_type = content_type


@dataclass
class OCRJobCreatedEvent(DomainEvent):
    job_id: str
    document_id: str
    task_id: str
    priority: str

    def __init__(self, job_id: str, document_id: str, task_id: str, priority: str):
        super().__init__()
        self.job_id = job_id
        self.document_id = document_id
        self.task_id = task_id
        self.priority = priority
