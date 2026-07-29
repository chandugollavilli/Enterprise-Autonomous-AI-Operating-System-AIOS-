import io
import fitz
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
async def test_user_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="test_uploader@enterprise.com",
            hashed_password=hash_password("SecurePassword123!"),
            full_name="Test Ingestion User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}
        return user, headers


@pytest.mark.asyncio
async def test_upload_invalid_file_format(test_user_headers):
    user, headers = test_user_headers
    files = {"file": ("test.pdf", b"Not a real PDF file header", "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files, headers=headers)
    assert response.status_code == 400
    assert "Unsupported or invalid file format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_valid_pdf_flow(test_user_headers):
    user, headers = test_user_headers
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Sample Enterprise Contract")
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("contract.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["is_duplicate"] is False
    assert data["document"]["filename"] == "contract.pdf"
    assert data["document"]["page_count"] == 1
    assert data["job"]["status"] == "queued"


@pytest.mark.asyncio
async def test_upload_duplicate_detection(test_user_headers):
    user, headers = test_user_headers
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Unique Duplicate Stream Test")
    pdf_bytes = doc.tobytes()
    doc.close()

    files1 = {"file": ("first_upload.pdf", pdf_bytes, "application/pdf")}
    res1 = client.post("/api/v1/documents/upload", files=files1, headers=headers)
    assert res1.status_code == 201
    assert res1.json()["is_duplicate"] is False

    # Second upload with exact same pdf_bytes variable
    files2 = {"file": ("second_upload.pdf", pdf_bytes, "application/pdf")}
    res2 = client.post("/api/v1/documents/upload", files=files2, headers=headers)
    assert res2.status_code == 201
    assert res2.json()["is_duplicate"] is True
