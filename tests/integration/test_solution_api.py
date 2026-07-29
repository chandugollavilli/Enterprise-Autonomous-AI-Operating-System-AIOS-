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
async def solution_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="solution_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Solution Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_solution_pack_api_endpoints(solution_admin_headers):
    # 1. List Available Solution Packs API Endpoint
    res_list = client.get("/api/v1/solutions", headers=solution_admin_headers)
    assert res_list.status_code == 200
    packs = res_list.json()
    assert len(packs) >= 3

    # 2. Install Solution Pack API Endpoint
    res_install = client.post("/api/v1/solutions/solution_legal/install", headers=solution_admin_headers)
    assert res_install.status_code == 201

    # 3. Execute Solution Pack Analysis Endpoint
    res_exec = client.post(
        "/api/v1/solutions/solution_legal/execute",
        json={"document_text": "Agreement with indemnification and unlimited liability", "filename": "contract.pdf"},
        headers=solution_admin_headers,
    )
    assert res_exec.status_code == 200
    data_exec = res_exec.json()
    assert data_exec["pack_id"] == "solution_legal"
    assert "report_markdown" in data_exec

    # 4. Get Dashboard Analytics Endpoint
    res_dash = client.get("/api/v1/solutions/solution_legal/dashboards", headers=solution_admin_headers)
    assert res_dash.status_code == 200
    assert res_dash.json()["total_documents_processed"] > 0
