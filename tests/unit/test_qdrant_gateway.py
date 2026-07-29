import pytest
from src.repositories.vector.qdrant_gateway import QdrantVectorGateway


@pytest.mark.asyncio
async def test_qdrant_vector_gateway_upsert_and_search():
    gateway = QdrantVectorGateway(collection_name="test_chunks", vector_size=4)
    await gateway.initialize_collection()

    # Upsert sample points
    p1 = {"id": "point_1", "vector": [1.0, 0.0, 0.0, 0.0], "payload": {"doc_type": "invoice"}}
    p2 = {"id": "point_2", "vector": [0.0, 1.0, 0.0, 0.0], "payload": {"doc_type": "contract"}}
    await gateway.upsert_batch([p1, p2])

    # Search with vector close to point_1
    results = await gateway.search_vectors([0.9, 0.1, 0.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]["point_id"] == "point_1"

    # Search with payload filter
    filtered = await gateway.search_vectors([1.0, 0.0, 0.0, 0.0], top_k=2, filters={"doc_type": "contract"})
    assert len(filtered) == 1
    assert filtered[0]["point_id"] == "point_2"
