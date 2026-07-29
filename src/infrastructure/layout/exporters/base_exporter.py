from abc import ABC, abstractmethod
from typing import Any
from src.domain.layout.canonical_model import CanonicalDocument


class IExporter(ABC):
    """Unified Abstract Interface for Document Format Exporters."""

    @abstractmethod
    def export(self, doc: CanonicalDocument) -> Any:
        """Export Canonical Document Model into target format representation."""
        pass

    @abstractmethod
    def format_name(self) -> str:
        """Return format name string (e.g. 'markdown', 'html', 'json', 'docx')."""
        pass
