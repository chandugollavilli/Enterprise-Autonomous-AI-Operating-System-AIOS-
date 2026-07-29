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
async def admin_auth_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="admin_user@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Enterprise Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_api_endpoints(admin_auth_headers):
    # 1. Models List API
    res_models = client.get("/api/v1/admin/models", headers=admin_auth_headers)
    assert res_models.status_code == 200
    assert len(res_models.json()) >= 1

    # 2. Plugins List API
    res_plugins = client.get("/api/v1/admin/plugins", headers=admin_auth_headers)
    assert res_plugins.status_code == 200

    # 3. Workflows List API
    res_workflows = client.get("/api/v1/admin/workflows", headers=admin_auth_headers)
    assert res_workflows.status_code == 200
    assert len(res_workflows.json()) >= 1

    # 4. Feature Flags List API
    res_flags = client.get("/api/v1/admin/feature-flags", headers=admin_auth_headers)
    assert res_flags.status_code == 200
    assert len(res_flags.json()) >= 1

    # 5. Toggle Feature Flag API
    res_toggle = client.post(
        "/api/v1/admin/feature-flags/analytics.enabled",
        json={"enabled": True},
        headers=admin_auth_headers,
    )
    assert res_toggle.status_code == 200
    assert res_toggle.json()["enabled"] is True

    # 6. Usage Analytics API
    res_analytics = client.get("/api/v1/admin/analytics", headers=admin_auth_headers)
    assert res_analytics.status_code == 200
    assert "total_documents_processed" in res_analytics.json()
