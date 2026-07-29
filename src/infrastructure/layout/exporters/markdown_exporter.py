from typing import List
from src.domain.layout.canonical_model import CanonicalDocument, CanonicalNode, NodeType


class MarkdownGenerator:
    """Generates clean GitHub Flavored Markdown (GFM) from Canonical Document Model."""

    @staticmethod
    def generate(doc: CanonicalDocument) -> str:
        lines: List[str] = []
        nodes = doc.get_ordered_nodes()

        current_page = 1

        for node in nodes:
            # Inject page break marker when transitioning pages
            if node.page_number != current_page:
                lines.append(f"\n<!-- Page {node.page_number} -->\n")
                current_page = node.page_number

            if node.node_type == NodeType.HEADING:
                prefix = "#" * max(1, min(node.level, 6))
                lines.append(f"{prefix} {node.text}\n")

            elif node.node_type == NodeType.LIST_ITEM:
                lines.append(f"- {node.text}")

            elif node.node_type == NodeType.TABLE:
                # Format pipe table line
                lines.append(f"| {node.text.replace('\t', ' | ')} |")

            elif node.node_type == NodeType.FIGURE:
                lines.append(f"\n![{node.text}](figure_{node.id}.png)\n")

            else:
                lines.append(f"{node.text}\n")

        return "\n".join(lines)
