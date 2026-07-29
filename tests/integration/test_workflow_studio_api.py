import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.postgres.models import User
from src.infrastructure.security.password import hash_password
from src.infrastructure.security.jwt import create_access_token
from tests.conftest import TestingSessionFactory

client = TestClient(app)


@pytest_asyncio.fixture
async def studio_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="studio_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Studio Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_workflow_studio_api_endpoints(studio_admin_headers):
    # 1. Create Workflow Definition REST Endpoint
    res_create = client.post(
        "/api/v1/workflows",
        json={
            "name": "Invoice Auto Processing Pipeline",
            "category": "document_automation",
            "nodes": [
                {"id": "n1", "type": "import", "name": "Import"},
                {"id": "n2", "type": "ocr", "name": "OCR Engine"},
            ],
            "edges": [
                {"id": "e1", "source_node_id": "n1", "target_node_id": "n2"},
            ],
        },
        headers=studio_admin_headers,
    )
    assert res_create.status_code == 201
    data_wf = res_create.json()
    assert data_wf["name"] == "Invoice Auto Processing Pipeline"
    assert data_wf["status"] == "draft"
    wf_id = data_wf["id"]

    # 2. Publish Workflow Definition Endpoint
    res_pub = client.post(f"/api/v1/workflows/{wf_id}/publish", headers=studio_admin_headers)
    assert res_pub.status_code == 200
    assert res_pub.json()["status"] == "published"

    # 3. List Workflows Endpoint
    res_list = client.get("/api/v1/workflows", headers=studio_admin_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
