import pytest
from src.infrastructure.embeddings.bge_m3_adapter import BGEM3EmbeddingAdapter
from src.infrastructure.embeddings.sentence_transformer_adapter import SentenceTransformerAdapter
from src.infrastructure.embeddings.embedding_cache import EmbeddingCacheManager


@pytest.mark.asyncio
async def test_bge_m3_embedding_adapter():
    adapter = BGEM3EmbeddingAdapter()
    await adapter.initialize()

    info = adapter.model_info()
    assert info["dimension"] == 1024
    assert info["provider"] == "BAAI"

    vec = await adapter.embed_text("Sample financial invoice document")
    assert len(vec) == 1024
    assert type(vec[0]) is float


@pytest.mark.asyncio
async def test_sentence_transformer_adapter():
    adapter = SentenceTransformerAdapter()
    vec = await adapter.embed_text("Contract agreement section")
    assert len(vec) == 384


def test_embedding_cache_manager():
    cache = EmbeddingCacheManager()
    text = "Enterprise Document Intelligence"
    model = "BAAI/bge-m3"

    assert cache.get(text, model) is None

    vector = [0.1, 0.2, 0.3]
    cache.set(text, model, vector)
    assert cache.get(text, model) == vector
    assert cache.size() == 1
