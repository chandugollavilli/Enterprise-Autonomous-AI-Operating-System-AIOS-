import uuid
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.postgres.models import User, Document, DocumentChunk
from src.infrastructure.security.password import hash_password
from src.infrastructure.security.jwt import create_access_token
from src.services.vector_search_service import VectorSearchService
from tests.conftest import TestingSessionFactory

client = TestClient(app)


@pytest_asyncio.fixture
async def search_test_environment():
    async with TestingSessionFactory() as session:
        user = User(
            email="search_user@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Search Test User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        doc = Document(
            user_id=user.id,
            filename="search_doc.pdf",
            content_type="application/pdf",
            file_size_bytes=1024,
            storage_path="documents/search_doc.pdf",
            checksum_sha256="searchsha123",
            status="structured",
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        chunk1 = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="Enterprise Contract Agreement regarding quarterly deliverables.",
            heading_context="Section 1 > Deliverables",
            page_references_json={"pages": [1], "bboxes": [[0.1, 0.1, 0.9, 0.2]]},
        )
        chunk2 = DocumentChunk(
            document_id=doc.id,
            chunk_index=1,
            content="Payment schedule terms: Total due is $100,000 payable in 30 days.",
            heading_context="Section 2 > Payment Terms",
            page_references_json={"pages": [2], "bboxes": [[0.1, 0.3, 0.9, 0.4]]},
        )
        session.add_all([chunk1, chunk2])
        await session.commit()

        search_service = VectorSearchService(session)
        await search_service.index_document_vectors(doc.id)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}

        return user, doc, headers


@pytest.mark.asyncio
async def test_search_api_endpoints(search_test_environment):
    user, doc, headers = search_test_environment

    # 1. Hybrid Search API Endpoint
    res_hybrid = client.post(
        "/api/v1/search/hybrid",
        json={"query": "payment terms deliverables", "top_k": 5},
        headers=headers,
    )
    assert res_hybrid.status_code == 200
    data_hybrid = res_hybrid.json()
    assert data_hybrid["query"] == "payment terms deliverables"
    assert len(data_hybrid["results"]) >= 1

    # 2. Pure Vector Search API Endpoint
    res_vector = client.post(
        "/api/v1/search/vector",
        json={"query": "contract agreement", "top_k": 5},
        headers=headers,
    )
    assert res_vector.status_code == 200
    assert len(res_vector.json()["results"]) >= 1

    # 3. Related Documents API Endpoint
    res_related = client.get(f"/api/v1/search/documents/{doc.id}/related", headers=headers)
    assert res_related.status_code == 200
