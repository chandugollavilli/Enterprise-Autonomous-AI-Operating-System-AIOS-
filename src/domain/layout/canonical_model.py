import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class NodeType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    LIST_ITEM = "list_item"
    FIGURE = "figure"
    CAPTION = "caption"
    HEADER = "header"
    FOOTER = "footer"


@dataclass
class CanonicalNode:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType = NodeType.PARAGRAPH
    bbox: List[float] = field(default_factory=lambda: [0.0, 0.0, 1.0, 1.0])  # [x1, y1, x2, y2]
    confidence: float = 1.0
    reading_order: int = 0
    page_number: int = 1
    text: str = ""
    level: int = 1  # For Headings (H1-H6)
    children: List["CanonicalNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_type": self.node_type.value,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "reading_order": self.reading_order,
            "page_number": self.page_number,
            "text": self.text,
            "level": self.level,
            "children": [c.to_dict() for c in self.children],
            "metadata": self.metadata,
        }


@dataclass
class CanonicalDocument:
    document_id: str
    nodes: List[CanonicalNode] = field(default_factory=list)

    def get_ordered_nodes(self) -> List[CanonicalNode]:
        """Return all nodes flattened in reading order sequence."""
        return sorted(self.nodes, key=lambda n: (n.page_number, n.reading_order))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "nodes": [n.to_dict() for n in self.nodes],
        }
