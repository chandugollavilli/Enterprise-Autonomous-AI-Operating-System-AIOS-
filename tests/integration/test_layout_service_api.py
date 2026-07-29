import io
import fitz
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.postgres.models import User
from src.infrastructure.security.password import hash_password
from src.infrastructure.security.jwt import create_access_token
from src.services.document_service import DocumentService
from src.services.preprocessing_service import DocumentPreprocessingService
from src.services.ocr_service import OCRService
from tests.conftest import TestingSessionFactory
from src.repositories.storage.local_storage import LocalStorageGateway

client = TestClient(app)


@pytest_asyncio.fixture
async def test_layout_environment():
    storage = LocalStorageGateway(base_directory="/tmp/test_ocr_storage")
    async with TestingSessionFactory() as session:
        user = User(
            email="layout_user@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Layout Integration User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        pdf_doc = fitz.open()
        p1 = pdf_doc.new_page(width=595, height=842)
        p1.insert_text((50, 50), "1. Executive Summary Overview")
        p1.insert_text((50, 100), "This report presents Q3 performance metrics.")
        pdf_bytes = pdf_doc.tobytes()
        pdf_doc.close()

        doc_service = DocumentService(session, storage)
        res = await doc_service.upload_document(
            file_content=pdf_bytes,
            original_filename="executive_report.pdf",
            user=user,
        )
        await session.commit()
        doc = res["document"]

        # Run preprocessing and OCR pipelines
        preprocessor = DocumentPreprocessingService(session, storage)
        await preprocessor.process_document_pages(doc.id)
        await session.commit()

        ocr_service = OCRService(session, storage)
        await ocr_service.process_ocr_for_document(doc.id)
        await session.commit()

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}

        return session, user, doc, headers


@pytest.mark.asyncio
async def test_layout_export_api_endpoints(test_layout_environment):
    session, user, doc, headers = test_layout_environment

    # 1. Markdown Export API
    res_md = client.get(f"/api/v1/documents/{doc.id}/markdown", headers=headers)
    assert res_md.status_code == 200
    assert "markdown" in res_md.json()

    # 2. HTML Export API
    res_html = client.get(f"/api/v1/documents/{doc.id}/html", headers=headers)
    assert res_html.status_code == 200
    assert "<article" in res_html.json()["html"]

    # 3. JSON CDM Export API
    res_json = client.get(f"/api/v1/documents/{doc.id}/json", headers=headers)
    assert res_json.status_code == 200
    assert res_json.json()["document_id"] == str(doc.id)

    # 4. Chunks API
    res_chunks = client.get(f"/api/v1/documents/{doc.id}/chunks", headers=headers)
    assert res_chunks.status_code == 200
    assert res_chunks.json()["total_chunks"] >= 1

    # 5. Layout Blocks API
    res_layout = client.get(f"/api/v1/documents/{doc.id}/layout", headers=headers)
    assert res_layout.status_code == 200
    assert res_layout.json()["total_blocks"] >= 1
