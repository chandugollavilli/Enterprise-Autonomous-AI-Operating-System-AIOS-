import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repositories.postgres.base_repo import BaseRepository
from src.repositories.postgres.models import Document, DocumentPage, OCRJob, OCRResult


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_by_checksum(self, checksum: str) -> Optional[Document]:
        query = select(Document).where(
            Document.checksum_sha256 == checksum, Document.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_pages_and_ocr(self, document_id: uuid.UUID) -> Optional[Document]:
        query = (
            select(Document)
            .where(Document.id == document_id, Document.is_deleted == False)
            .options(
                selectinload(Document.pages).selectinload(DocumentPage.ocr_result),
                selectinload(Document.ocr_jobs),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_documents(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> List[Document]:
        query = (
            select(Document)
            .where(Document.user_id == user_id, Document.is_deleted == False)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class DocumentPageRepository(BaseRepository[DocumentPage]):
    def __init__(self, session: AsyncSession):
        super().__init__(DocumentPage, session)

    async def get_pages_for_document(self, document_id: uuid.UUID) -> List[DocumentPage]:
        query = (
            select(DocumentPage)
            .where(DocumentPage.document_id == document_id, DocumentPage.is_deleted == False)
            .order_by(DocumentPage.page_number.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


class OCRJobRepository(BaseRepository[OCRJob]):
    def __init__(self, session: AsyncSession):
        super().__init__(OCRJob, session)

    async def get_by_task_id(self, task_id: str) -> Optional[OCRJob]:
        query = select(OCRJob).where(OCRJob.task_id == task_id, OCRJob.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
