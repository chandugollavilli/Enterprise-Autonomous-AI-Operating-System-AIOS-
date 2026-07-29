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
async def rag_test_environment():
    async with TestingSessionFactory() as session:
        user = User(
            email="rag_user@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="RAG Integration User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        doc = Document(
            user_id=user.id,
            filename="rag_contract.pdf",
            content_type="application/pdf",
            file_size_bytes=4096,
            storage_path="documents/rag_contract.pdf",
            checksum_sha256="ragcontracthash123",
            status="structured",
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="Section 2. Payment terms specify net 30 day settlement.",
            heading_context="Section 2 > Payment Terms",
            page_references_json={"pages": [3], "bboxes": [[0.1, 0.1, 0.9, 0.2]]},
        )
        session.add(chunk)
        await session.commit()

        # Index chunk vectors
        search_service = VectorSearchService(session)
        await search_service.index_document_vectors(doc.id)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}

        return user, doc, headers


@pytest.mark.asyncio
async def test_chat_and_rag_query_endpoints(rag_test_environment):
    user, doc, headers = rag_test_environment

    # 1. Chat with Documents API Endpoint
    res_chat = client.post(
        "/api/v1/chat",
        json={"message": "What are the payment terms?", "document_id": str(doc.id)},
        headers=headers,
    )
    assert res_chat.status_code == 200
    data_chat = res_chat.json()
    assert "answer" in data_chat
    assert "session_id" in data_chat
    assert len(data_chat["citations"]) >= 1
    assert data_chat["citations"][0]["page_number"] == 3

    # 2. RAG Query API Endpoint
    res_rag = client.post(
        "/api/v1/rag/query",
        json={"query": "What are the payment terms?", "document_id": str(doc.id)},
        headers=headers,
    )
    assert res_rag.status_code == 200
    assert "answer" in res_rag.json()
