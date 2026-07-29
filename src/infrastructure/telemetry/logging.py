import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict

# Context variables for tracing request context across async execution
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
document_id_var: ContextVar[str] = ContextVar("document_id", default="")
job_id_var: ContextVar[str] = ContextVar("job_id", default="")


class StructuredJSONFormatter(logging.Formatter):
    """JSON log formatter adhering to enterprise telemetry requirements."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get() or None,
            "user_id": user_id_var.get() or None,
            "document_id": document_id_var.get() or None,
            "job_id": job_id_var.get() or None,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)

        return json.dumps(log_data)
