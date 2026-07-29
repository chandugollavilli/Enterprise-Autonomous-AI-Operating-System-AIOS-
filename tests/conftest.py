import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.domain.models.base import Base
from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_storage
from src.repositories.storage.local_storage import LocalStorageGateway

# Async SQLite In-Memory Engine for Testing
TEST_SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_db():
    async with TestingSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def override_get_storage():
    return LocalStorageGateway(base_directory="/tmp/test_ocr_storage")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_storage] = override_get_storage


@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
