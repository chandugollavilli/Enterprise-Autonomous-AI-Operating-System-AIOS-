from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class CitationDTO:
    citation_index: int
    document_id: str
    chunk_id: str
    page_number: int
    heading_context: str
    bbox: List[float] = field(default_factory=lambda: [0.0, 0.0, 1.0, 1.0])
    confidence: float = 1.0
    source_text: str = ""


class CitationGenerator:
    """Generates inline citation markers and detailed source metadata DTOs for RAG answers."""

    @staticmethod
    def generate_citations(referenced_items: List[Dict[str, Any]]) -> List[CitationDTO]:
        citations: List[CitationDTO] = []

        for item in referenced_items:
            payload = item.get("payload", {})
            idx = item.get("citation_index", 1)
            pages = payload.get("pages", [1])
            bboxes = payload.get("bboxes", [[0.0, 0.0, 1.0, 1.0]])

            citation = CitationDTO(
                citation_index=idx,
                document_id=payload.get("document_id", ""),
                chunk_id=payload.get("chunk_id", ""),
                page_number=pages[0] if pages else 1,
                heading_context=payload.get("heading_context", "General"),
                bbox=bboxes[0] if bboxes else [0.0, 0.0, 1.0, 1.0],
                confidence=item.get("score", 1.0),
                source_text=payload.get("content", ""),
            )
            citations.append(citation)

        return citations
