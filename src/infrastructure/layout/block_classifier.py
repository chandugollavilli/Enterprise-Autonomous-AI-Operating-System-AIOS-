import re
from typing import Dict, Any, List
from src.domain.layout.canonical_model import CanonicalNode, NodeType


class BlockClassifier:
    """Classifies OCR bounding box text lines into Headings (H1-H6), Paragraphs, Tables, Lists, and Figures."""

    @staticmethod
    def classify(text: str, bbox: List[float], page_number: int = 1) -> CanonicalNode:
        clean_text = text.strip()
        
        # 1. Heading Detection
        is_heading, level = BlockClassifier._detect_heading(clean_text, bbox)
        if is_heading:
            return CanonicalNode(
                node_type=NodeType.HEADING,
                bbox=bbox,
                text=clean_text,
                level=level,
                page_number=page_number,
            )

        # 2. List Detection (Bulleted or Numbered)
        if BlockClassifier._is_list_item(clean_text):
            return CanonicalNode(
                node_type=NodeType.LIST_ITEM,
                bbox=bbox,
                text=clean_text,
                page_number=page_number,
            )

        # 3. Table Line Detection
        if "|" in clean_text or "\t" in clean_text:
            return CanonicalNode(
                node_type=NodeType.TABLE,
                bbox=bbox,
                text=clean_text,
                page_number=page_number,
            )

        # 4. Standard Paragraph
        return CanonicalNode(
            node_type=NodeType.PARAGRAPH,
            bbox=bbox,
            text=clean_text,
            page_number=page_number,
        )

    @staticmethod
    def _detect_heading(text: str, bbox: List[float]) -> tuple[bool, int]:
        # Heading rules: Short line length, title case or all caps, section numbering
        if not text or len(text) > 100:
            return False, 1

        # Check section pattern e.g. "1. Executive Summary" or "Section 2.1"
        if re.match(r"^(\d+(\.\d+)*)\s+[A-Z]", text) or re.match(r"^(SECTION|CHAPTER)\s+\d+", text, re.I):
            depth = text.split()[0].count(".") + 1 if "." in text.split()[0] else 1
            return True, min(depth, 6)

        # All Caps short string
        if text.isupper() and len(text) < 60:
            return True, 2

        # Title Case short string without trailing period
        if text.istitle() and not text.endswith(".") and len(text) < 50:
            return True, 3

        return False, 1

    @staticmethod
    def _is_list_item(text: str) -> bool:
        return bool(
            re.match(r"^[\bullet\-\*\•]\s+", text)
            or re.match(r"^\d+[\.\)]\s+", text)
            or re.match(r"^[a-z][\.\)]\s+", text)
        )
