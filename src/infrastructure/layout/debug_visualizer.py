from typing import List
import cv2
import numpy as np
from src.domain.layout.canonical_model import CanonicalNode, NodeType

# Color codes for layout element visualization (BGR)
COLOR_MAP = {
    NodeType.HEADING: (0, 0, 255),      # Red
    NodeType.PARAGRAPH: (0, 255, 0),    # Green
    NodeType.TABLE: (255, 0, 0),        # Blue
    NodeType.LIST_ITEM: (0, 255, 255),  # Yellow
    NodeType.FIGURE: (255, 0, 255),     # Magenta
}


class DebugVisualizer:
    """Draws colored bounding boxes and reading order flow onto page images for visual debugging."""

    @staticmethod
    def draw_layout_overlay(image: np.ndarray, nodes: List[CanonicalNode]) -> np.ndarray:
        overlay = image.copy()
        h, w = image.shape[:2]

        for node in nodes:
            color = COLOR_MAP.get(node.node_type, (128, 128, 128))

            # Re-convert normalized 0.0-1.0 bbox to pixel coordinates
            x1 = int(node.bbox[0] * w)
            y1 = int(node.bbox[1] * h)
            x2 = int(node.bbox[2] * w)
            y2 = int(node.bbox[3] * h)

            # Draw bounding box rectangle
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

            # Draw Reading Order badge number
            badge_text = f"#{node.reading_order} [{node.node_type.value}]"
            cv2.putText(
                overlay,
                badge_text,
                (x1, max(15, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        return overlay
