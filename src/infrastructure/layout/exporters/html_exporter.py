from typing import List
from html import escape
from src.domain.layout.canonical_model import CanonicalDocument, CanonicalNode, NodeType


class HTML5Generator:
    """Generates semantic HTML5 markup from Canonical Document Model."""

    @staticmethod
    def generate(doc: CanonicalDocument) -> str:
        html_lines: List[str] = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head><meta charset="UTF-8"><title>Document Export</title></head>',
            '<body>',
            '  <article class="document-content">',
        ]

        nodes = doc.get_ordered_nodes()

        for node in nodes:
            safe_text = escape(node.text)

            if node.node_type == NodeType.HEADING:
                level = max(1, min(node.level, 6))
                html_lines.append(f"    <h{level}>{safe_text}</h{level}>")

            elif node.node_type == NodeType.LIST_ITEM:
                html_lines.append(f"    <ul><li>{safe_text}</li></ul>")

            elif node.node_type == NodeType.TABLE:
                cells = "".join(f"<td>{escape(c)}</td>" for c in node.text.split("\t"))
                html_lines.append(f"    <table><tr>{cells}</tr></table>")

            elif node.node_type == NodeType.FIGURE:
                html_lines.append(f"    <figure><figcaption>{safe_text}</figcaption></figure>")

            else:
                html_lines.append(f"    <p>{safe_text}</p>")

        html_lines.extend([
            '  </article>',
            '</body>',
            '</html>',
        ])

        return "\n".join(html_lines)
