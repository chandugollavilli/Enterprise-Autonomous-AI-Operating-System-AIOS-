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
async def automation_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="automation_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Automation Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_connectors_and_rules_api_endpoints(automation_admin_headers):
    # 1. Register Connector API Endpoint
    res_conn = client.post(
        "/api/v1/connectors",
        json={
            "name": "Finance S3 Bucket",
            "connector_type": "s3",
            "config": {"bucket": "finance-inbound-docs"},
        },
        headers=automation_admin_headers,
    )
    assert res_conn.status_code == 201
    data_conn = res_conn.json()
    assert data_conn["name"] == "Finance S3 Bucket"
    conn_id = data_conn["id"]

    # 2. Trigger Connector Sync API Endpoint
    res_sync = client.post(f"/api/v1/connectors/{conn_id}/sync", headers=automation_admin_headers)
    assert res_sync.status_code == 200
    data_sync = res_sync.json()
    assert data_sync["status"] == "completed"
    assert data_sync["documents_synced"] >= 1

    # 3. Create Automation Rule API Endpoint
    res_rule = client.post(
        "/api/v1/rules",
        json={
            "name": "High Value Invoice Route",
            "target_category": "Invoice",
            "field_name": "amount",
            "operator": "GREATER_THAN",
            "threshold_value": "5000",
            "target_action": "ROUTE_TO_FINANCE",
        },
        headers=automation_admin_headers,
    )
    assert res_rule.status_code == 201
    assert res_rule.json()["target_action"] == "ROUTE_TO_FINANCE"
