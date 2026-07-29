import pytest
from src.domain.layout.canonical_model import CanonicalDocument, CanonicalNode, NodeType
from src.infrastructure.layout.exporters.markdown_exporter import MarkdownGenerator
from src.infrastructure.layout.exporters.html_exporter import HTML5Generator
from src.infrastructure.layout.exporters.json_exporter import JSONExporter


@pytest.fixture
def sample_canonical_document():
    doc = CanonicalDocument(document_id="doc_test_123")
    doc.nodes = [
        CanonicalNode(node_type=NodeType.HEADING, text="Executive Summary", level=1, reading_order=1),
        CanonicalNode(node_type=NodeType.PARAGRAPH, text="This is the main body paragraph content.", reading_order=2),
        CanonicalNode(node_type=NodeType.LIST_ITEM, text="Key Finding 1", reading_order=3),
        CanonicalNode(node_type=NodeType.TABLE, text="Col1\tCol2", reading_order=4),
    ]
    return doc


def test_markdown_generator(sample_canonical_document):
    md = MarkdownGenerator.generate(sample_canonical_document)
    assert "# Executive Summary" in md
    assert "This is the main body paragraph content." in md
    assert "- Key Finding 1" in md
    assert "| Col1 | Col2 |" in md


def test_html5_generator(sample_canonical_document):
    html = HTML5Generator.generate(sample_canonical_document)
    assert "<h1>Executive Summary</h1>" in html
    assert "<p>This is the main body paragraph content.</p>" in html
    assert "<li>Key Finding 1</li>" in html
    assert "<table>" in html


def test_json_exporter(sample_canonical_document):
    json_data = JSONExporter.generate(sample_canonical_document)
    assert json_data["document_id"] == "doc_test_123"
    assert len(json_data["nodes"]) == 4
    assert json_data["nodes"][0]["node_type"] == "heading"
