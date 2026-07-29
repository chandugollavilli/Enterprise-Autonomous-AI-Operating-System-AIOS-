import pytest
from src.infrastructure.rag.context_builder import ContextBuilder
from src.infrastructure.rag.citation_generator import CitationGenerator
from src.infrastructure.rag.rag_engine import EnterpriseRAGEngine
from src.infrastructure.llm.prompt_registry import PromptRegistry


def test_context_builder_formatting():
    results = [
        {"score": 0.95, "payload": {"content": "Paragraph 1 text.", "heading_context": "Section 1", "pages": [1]}},
        {"score": 0.85, "payload": {"content": "Paragraph 2 text.", "heading_context": "Section 2", "pages": [2]}},
    ]

    context_str, items = ContextBuilder.build_context(results, max_tokens=100)
    assert "[1] (Header: Section 1 | Page 1)" in context_str
    assert "Paragraph 1 text." in context_str
    assert len(items) == 2


def test_citation_generator():
    items = [
        {
            "citation_index": 1,
            "score": 0.95,
            "payload": {
                "document_id": "doc_123",
                "chunk_id": "chunk_456",
                "pages": [1],
                "heading_context": "Overview",
                "bboxes": [[0.1, 0.1, 0.9, 0.2]],
                "content": "Source text snippet",
            },
        }
    ]

    citations = CitationGenerator.generate_citations(items)
    assert len(citations) == 1
    assert citations[0].citation_index == 1
    assert citations[0].document_id == "doc_123"
    assert citations[0].page_number == 1


@pytest.mark.asyncio
async def test_enterprise_rag_engine():
    rag_engine = EnterpriseRAGEngine()
    chunks = [
        {"score": 0.9, "payload": {"content": "Deliverables due by Q3 end.", "pages": [1]}}
    ]

    res = await rag_engine.answer_question("When are deliverables due?", chunks)
    assert "answer" in res
    assert len(res["citations"]) == 1
    assert res["total_tokens"] > 0
