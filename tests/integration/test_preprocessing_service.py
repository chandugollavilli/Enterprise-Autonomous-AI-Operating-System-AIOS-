import io
import fitz
import pytest
import pytest_asyncio
from src.repositories.postgres.models import User, Document
from src.infrastructure.security.password import hash_password
from src.services.document_service import DocumentService
from src.services.preprocessing_service import DocumentPreprocessingService
from tests.conftest import TestingSessionFactory
from src.repositories.storage.local_storage import LocalStorageGateway


@pytest_asyncio.fixture
async def test_user_and_doc():
    storage = LocalStorageGateway(base_directory="/tmp/test_ocr_storage")
    async with TestingSessionFactory() as session:
        user = User(
            email="preprocessor_user@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Preprocessor Test User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create multi-page PDF bytes
        pdf_doc = fitz.open()
        p1 = pdf_doc.new_page(width=595, height=842)
        p1.insert_text((50, 50), "Page 1 Financial Report")
        p2 = pdf_doc.new_page(width=595, height=842)
        p2.insert_text((50, 50), "Page 2 Annexure Data")
        pdf_bytes = pdf_doc.tobytes()
        pdf_doc.close()

        doc_service = DocumentService(session, storage)
        res = await doc_service.upload_document(
            file_content=pdf_bytes,
            original_filename="financial_report.pdf",
            user=user,
        )
        await session.commit()
        return session, user, res["document"], storage


@pytest.mark.asyncio
async def test_preprocessing_service_flow(test_user_and_doc):
    session, user, doc, storage = test_user_and_doc
    preprocessing_service = DocumentPreprocessingService(session, storage)

    pages = await preprocessing_service.process_document_pages(doc.id, profile_name="balanced")
    await session.commit()

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[1].page_number == 2
    assert pages[0].dpi == 300
    assert pages[0].image_storage_path.startswith(f"preprocessed/{doc.id}/")

    # Check preprocessed image file exists in storage
    exists = await storage.file_exists(pages[0].image_storage_path)
    assert exists is True
