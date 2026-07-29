import json
from typing import Dict, Any
from src.domain.layout.canonical_model import CanonicalDocument


class JSONExporter:
    """Generates structured JSON tree for AI agents, RAG, and external integrations."""

    @staticmethod
    def generate(doc: CanonicalDocument) -> Dict[str, Any]:
        return doc.to_dict()

    @staticmethod
    def generate_json_string(doc: CanonicalDocument, indent: int = 2) -> str:
        return json.dumps(doc.to_dict(), indent=indent)
