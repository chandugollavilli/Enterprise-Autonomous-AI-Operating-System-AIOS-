import pytest
from src.config import settings


def test_settings_default_values():
    assert settings.PROJECT_NAME == "Enterprise Document Intelligence Platform"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.POSTGRES_PORT == 5432
    assert settings.MINIO_BUCKET_NAME == "documents"


def test_database_uri_generation():
    async_uri = settings.SQLALCHEMY_DATABASE_URI
    assert async_uri.startswith("postgresql+asyncpg://")

    sync_uri = settings.SQLALCHEMY_SYNC_DATABASE_URI
    assert sync_uri.startswith("postgresql://")


def test_health_check_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == settings.PROJECT_NAME
