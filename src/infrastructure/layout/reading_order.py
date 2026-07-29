from typing import List
from src.domain.layout.canonical_model import CanonicalNode


class ReadingOrderEngine:
    """Reconstructs human reading order across single, two-column, and multi-column document layouts."""

    @staticmethod
    def sort_nodes(nodes: List[CanonicalNode], column_threshold: float = 0.45) -> List[CanonicalNode]:
        """
        Sort nodes per page using spatial column detection.
        - Clusters nodes into left column (x1 < threshold) vs. right column (x1 >= threshold).
        - Sorts left column top-to-bottom, then right column top-to-bottom.
        """
        if not nodes:
            return []

        # Check if page is two-column layout by inspecting x1 coordinates
        left_column = []
        right_column = []

        has_two_columns = False
        for node in nodes:
            x1 = node.bbox[0]
            if x1 >= column_threshold:
                has_two_columns = True
                right_column.append(node)
            else:
                left_column.append(node)

        if has_two_columns and len(left_column) > 0 and len(right_column) > 0:
            # Sort left column top-to-bottom
            left_column.sort(key=lambda n: n.bbox[1])
            # Sort right column top-to-bottom
            right_column.sort(key=lambda n: n.bbox[1])
            sorted_page_nodes = left_column + right_column
        else:
            # Standard single column top-to-bottom sort
            sorted_page_nodes = sorted(nodes, key=lambda n: n.bbox[1])

        # Assign sequential reading order numbers
        for idx, node in enumerate(sorted_page_nodes):
            node.reading_order = idx + 1

        return sorted_page_nodes
