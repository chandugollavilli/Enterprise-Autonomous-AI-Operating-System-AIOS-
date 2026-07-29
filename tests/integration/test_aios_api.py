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
async def aios_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="aios_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="AIOS Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_aios_api_endpoints(aios_admin_headers):
    # 1. Multi-Agent Collaboration API Endpoint
    res_collab = client.post(
        "/api/v1/agents/collaborate",
        json={"goal": "Audit Q3 Legal & Tax Compliance"},
        headers=aios_admin_headers,
    )
    assert res_collab.status_code == 200
    data_collab = res_collab.json()
    assert data_collab["status"] == "consensus_achieved"

    # 2. Get Agents Status API Endpoint
    res_status = client.get("/api/v1/agents/status", headers=aios_admin_headers)
    assert res_status.status_code == 200
    assert len(res_status.json()) >= 5

    # 3. Copilot Chat API Endpoint
    res_copilot = client.post(
        "/api/v1/copilot/chat",
        json={"message": "Summarize key indemnification liabilities"},
        headers=aios_admin_headers,
    )
    assert res_copilot.status_code == 200
    assert "citations" in res_copilot.json()

    # 4. Autonomous Plan Creation API Endpoint
    res_plan = client.post(
        "/api/v1/planner/create",
        json={"goal": "Auto-process vendor invoice pipeline"},
        headers=aios_admin_headers,
    )
    assert res_plan.status_code == 201
    assert len(res_plan.json()["tasks"]) >= 3

    # 5. Search Knowledge Graph API Endpoint
    res_kg = client.get("/api/v1/knowledge/search?query=Contract", headers=aios_admin_headers)
    assert res_kg.status_code == 200
