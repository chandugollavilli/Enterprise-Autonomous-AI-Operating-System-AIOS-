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
async def tenant_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="tenant_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Tenant Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "SystemAdmin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_tenant_provisioning_and_listing(tenant_admin_headers):
    # 1. Provision Tenant API Endpoint
    res_create = client.post(
        "/api/v1/tenants",
        json={
            "slug": "acme-corp",
            "name": "Acme Corporation Enterprise",
            "contact_email": "admin@acmecorp.com",
            "max_documents": 20000,
            "max_pages_per_month": 100000,
        },
        headers=tenant_admin_headers,
    )
    assert res_create.status_code == 201
    data = res_create.json()
    assert data["slug"] == "acme-corp"
    assert data["status"] == "active"

    # 2. List Tenants API Endpoint
    res_list = client.get("/api/v1/tenants", headers=tenant_admin_headers)
    assert res_list.status_code == 200
    tenants = res_list.json()
    assert len(tenants) >= 1
    assert any(t["slug"] == "acme-corp" for t in tenants)
