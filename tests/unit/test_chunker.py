import pytest
from src.domain.layout.canonical_model import CanonicalDocument, CanonicalNode, NodeType
from src.infrastructure.layout.chunker import HeadingAwareChunker


def test_heading_aware_chunking():
    doc = CanonicalDocument(document_id="doc_chunk_1")
    doc.nodes = [
        CanonicalNode(node_type=NodeType.HEADING, text="1. Section One", level=1, reading_order=1, page_number=1),
        CanonicalNode(node_type=NodeType.PARAGRAPH, text="Paragraph text in section one.", reading_order=2, page_number=1),
        CanonicalNode(node_type=NodeType.HEADING, text="2. Section Two", level=1, reading_order=3, page_number=2),
        CanonicalNode(node_type=NodeType.PARAGRAPH, text="Paragraph text in section two.", reading_order=4, page_number=2),
    ]

    chunker = HeadingAwareChunker(max_tokens=50)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    assert chunks[0].heading_context == "1. Section One"
    assert chunks[0].page_references == [1]
    assert "Paragraph text in section one." in chunks[0].content

    assert chunks[1].heading_context == "2. Section Two"
    assert chunks[1].page_references == [2]
    assert "Paragraph text in section two." in chunks[1].content
