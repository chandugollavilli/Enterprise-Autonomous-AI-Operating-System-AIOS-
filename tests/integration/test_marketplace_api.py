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
async def marketplace_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="marketplace_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Marketplace Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_marketplace_and_webhook_api_endpoints(marketplace_admin_headers):
    # 1. List Marketplace Packages API Endpoint
    res_pkgs = client.get("/api/v1/marketplace/packages", headers=marketplace_admin_headers)
    assert res_pkgs.status_code == 200
    pkgs = res_pkgs.json()
    assert len(pkgs) >= 2

    # 2. Install Marketplace Package API Endpoint
    res_inst = client.post("/api/v1/marketplace/packages/pkg_sap_connector/install", headers=marketplace_admin_headers)
    assert res_inst.status_code == 201
    assert res_inst.json()["package_id"] == "pkg_sap_connector"

    # 3. Create Webhook Subscription API Endpoint
    res_wh = client.post(
        "/api/v1/webhooks",
        json={"target_url": "https://api.enterprise.com/webhooks", "event_types": ["document.uploaded", "ocr.completed"]},
        headers=marketplace_admin_headers,
    )
    assert res_wh.status_code == 201
    assert res_wh.json()["target_url"] == "https://api.enterprise.com/webhooks"
