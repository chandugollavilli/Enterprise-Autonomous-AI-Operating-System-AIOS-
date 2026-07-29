import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any
from src.domain.layout.canonical_model import CanonicalDocument, CanonicalNode, NodeType


@dataclass
class DocumentChunkDTO:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    chunk_index: int = 0
    content: str = ""
    heading_context: str = ""
    page_references: List[int] = field(default_factory=list)
    bboxes: List[List[float]] = field(default_factory=list)
    token_count: int = 0


class HeadingAwareChunker:
    """
    Heading-Aware Semantic Chunker.
    Splits documents into cohesive chunks bounded by section headings (H1-H6) and token limits.
    Preserves heading breadcrumbs, page numbers, and bounding boxes for RAG citations.
    """

    def __init__(self, max_tokens: int = 800, overlap_tokens: int = 100):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk_document(self, doc: CanonicalDocument) -> List[DocumentChunkDTO]:
        nodes = doc.get_ordered_nodes()
        if not nodes:
            return []

        chunks: List[DocumentChunkDTO] = []
        current_heading_path: List[str] = []
        current_chunk_nodes: List[CanonicalNode] = []
        current_token_count = 0
        chunk_idx = 0

        for node in nodes:
            # Estimate word token count
            node_tokens = len(node.text.split())

            if node.node_type == NodeType.HEADING:
                # If current chunk has content, finalize it before starting new section
                if current_chunk_nodes:
                    chunk = self._build_chunk(
                        doc.document_id, chunk_idx, current_heading_path, current_chunk_nodes
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                    current_chunk_nodes = []
                    current_token_count = 0

                # Update Heading Breadcrumb Context (H1 > H2 > H3)
                level_idx = max(0, node.level - 1)
                current_heading_path = current_heading_path[:level_idx]
                current_heading_path.append(node.text)

            # Check max token threshold
            if current_token_count + node_tokens > self.max_tokens and len(current_chunk_nodes) > 0:
                chunk = self._build_chunk(
                    doc.document_id, chunk_idx, current_heading_path, current_chunk_nodes
                )
                chunks.append(chunk)
                chunk_idx += 1
                current_chunk_nodes = [node]
                current_token_count = node_tokens
            else:
                current_chunk_nodes.append(node)
                current_token_count += node_tokens

        # Finalize trailing chunk
        if current_chunk_nodes:
            chunk = self._build_chunk(
                doc.document_id, chunk_idx, current_heading_path, current_chunk_nodes
            )
            chunks.append(chunk)

        return chunks

    def _build_chunk(
        self,
        document_id: str,
        chunk_idx: int,
        heading_path: List[str],
        nodes: List[CanonicalNode],
    ) -> DocumentChunkDTO:
        heading_context = " > ".join(heading_path) if heading_path else "General"
        content_lines = [n.text for n in nodes if n.text.strip()]
        full_content = "\n".join(content_lines)
        page_refs = sorted(list({n.page_number for n in nodes}))
        bboxes = [n.bbox for n in nodes]

        return DocumentChunkDTO(
            document_id=document_id,
            chunk_index=chunk_idx,
            content=full_content,
            heading_context=heading_context,
            page_references=page_refs,
            bboxes=bboxes,
            token_count=len(full_content.split()),
        )
