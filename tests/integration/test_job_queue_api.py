import uuid
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.postgres.models import User, Document, OCRJob
from src.infrastructure.security.password import hash_password
from src.infrastructure.security.jwt import create_access_token
from tests.conftest import TestingSessionFactory

client = TestClient(app)


@pytest_asyncio.fixture
async def test_job_environment():
    async with TestingSessionFactory() as session:
        user = User(
            email="job_manager@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Job Manager User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        doc = Document(
            user_id=user.id,
            filename="test_job_doc.pdf",
            content_type="application/pdf",
            file_size_bytes=2048,
            storage_path="documents/test_job_doc.pdf",
            checksum_sha256="abc123hash",
            status="ingested",
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        job = OCRJob(
            document_id=doc.id,
            task_id=str(uuid.uuid4()),
            priority="high",
            status="dead_lettered",
            error_message="Simulated DLQ error",
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        headers = {"Authorization": f"Bearer {token}"}

        return user, doc, job, headers


@pytest.mark.asyncio
async def test_list_and_retry_jobs(test_job_environment):
    user, doc, job, headers = test_job_environment

    # 1. List Jobs API
    res = client.get("/api/v1/jobs", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) >= 1

    # 2. Get Job Details
    res_details = client.get(f"/api/v1/jobs/{job.id}", headers=headers)
    assert res_details.status_code == 200
    assert res_details.json()["status"] == "dead_lettered"

    # 3. Retry Job API Endpoint
    res_retry = client.post(f"/api/v1/jobs/{job.id}/retry", headers=headers)
    assert res_retry.status_code == 200
    retry_data = res_retry.json()
    assert retry_data["status"] == "queued"
    assert retry_data["error_message"] is None
