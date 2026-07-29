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
async def test_ocr_environment():
    storage = LocalStorageGateway(base_directory="/tmp/test_ocr_storage")
    async with TestingSessionFactory() as session:
        user = User(
            email="ocr_user@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="OCR Integration User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Generate sample PDF document
        pdf_doc = fitz.open()
        p1 = pdf_doc.new_page(width=595, height=842)
        p1.insert_text((50, 50), "Invoice #1001 Enterprise Services")
        pdf_bytes = pdf_doc.tobytes()
        pdf_doc.close()

        doc_service = DocumentService(session, storage)
        res = await doc_service.upload_document(
            file_content=pdf_bytes,
            original_filename="invoice_1001.pdf",
            user=user,
        )
        await session.commit()

        doc = res["document"]

        # Run preprocessing to generate preprocessed page images
        preprocessor = DocumentPreprocessingService(session, storage)
        await preprocessor.process_document_pages(doc.id)
        await session.commit()

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}

        return session, user, doc, headers


@pytest.mark.asyncio
async def test_ocr_process_and_results_flow(test_ocr_environment):
    session, user, doc, headers = test_ocr_environment

    # Trigger OCR Processing API Endpoint
    response = client.post(f"/api/v1/ocr/process/{doc.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == str(doc.id)
    assert data["status"] == "ocr_completed"
    assert len(data["pages"]) == 1
    assert data["pages"][0]["ocr_mode"] in ["base", "gundam"]

    # Fetch OCR Results API Endpoint
    res2 = client.get(f"/api/v1/ocr/results/{doc.id}", headers=headers)
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["status"] == "ocr_completed"
    assert len(d2["pages"]) == 1
