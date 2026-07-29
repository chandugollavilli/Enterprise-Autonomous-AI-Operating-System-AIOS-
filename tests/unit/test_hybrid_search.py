import pytest
from src.infrastructure.search.bge_reranker import BGERerankerAdapter
from src.infrastructure.search.hybrid_search_engine import HybridSearchEngine
from src.repositories.vector.qdrant_gateway import QdrantVectorGateway
from src.infrastructure.embeddings.bge_m3_adapter import BGEM3EmbeddingAdapter


@pytest.mark.asyncio
async def test_bge_reranker():
    reranker = BGERerankerAdapter()
    docs = ["Financial quarterly report results", "Engineering blue-print design", "Invoice summary payment"]
    scores = await reranker.rerank("financial report", docs)

    assert len(scores) == 3
    # Top ranked item should be index 0 ("Financial quarterly report results")
    assert scores[0][0] == 0


@pytest.mark.asyncio
async def test_hybrid_search_engine_fusion():
    gateway = QdrantVectorGateway(vector_size=1024)
    embedder = BGEM3EmbeddingAdapter()

    v1 = await embedder.embed_text("Revenue total payment invoice")
    v2 = await embedder.embed_text("System architecture design documentation")

    await gateway.upsert_batch([
        {"id": "p1", "vector": v1, "payload": {"content": "Revenue total payment invoice"}},
        {"id": "p2", "vector": v2, "payload": {"content": "System architecture design documentation"}},
    ])

    engine = HybridSearchEngine(embedder=embedder, vector_gateway=gateway)
    results = await engine.search(query="payment invoice", top_k=2)

    assert len(results) >= 1
    assert results[0]["payload"]["content"] == "Revenue total payment invoice"
