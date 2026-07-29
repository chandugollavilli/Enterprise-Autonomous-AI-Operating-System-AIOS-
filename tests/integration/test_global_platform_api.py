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
async def platform_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="platform_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Platform Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_global_platform_api_endpoints(platform_admin_headers):
    # 1. List Global Regions API Endpoint
    res_regions = client.get("/api/v1/platform/regions", headers=platform_admin_headers)
    assert res_regions.status_code == 200
    regions = res_regions.json()
    assert len(regions) >= 3

    # 2. List Cloud Clusters API Endpoint
    res_clusters = client.get("/api/v1/platform/clusters", headers=platform_admin_headers)
    assert res_clusters.status_code == 200
    assert len(res_clusters.json()) >= 2

    # 3. Get Digital Twin Topology API Endpoint
    res_dt = client.get("/api/v1/platform/digital-twin", headers=platform_admin_headers)
    assert res_dt.status_code == 200
    assert res_dt.json()["system_health"] == "operational"

    # 4. Get FinOps Costs API Endpoint
    res_costs = client.get("/api/v1/platform/costs", headers=platform_admin_headers)
    assert res_costs.status_code == 200
    assert res_costs.json()["total_monthly_spend_usd"] > 0

    # 5. Execute SRE Runbook API Endpoint
    res_rb = client.post(
        "/api/v1/platform/runbooks/execute",
        json={"runbook_name": "Scale Out Celery Queue", "target": "eks-cluster-us-east-1"},
        headers=platform_admin_headers,
    )
    assert res_rb.status_code == 200
    assert res_rb.json()["status"] == "success"
