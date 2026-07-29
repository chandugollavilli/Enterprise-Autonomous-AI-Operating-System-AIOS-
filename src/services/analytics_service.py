from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.repositories.postgres.models import Document, DocumentPage, OCRJob


class UsageAnalyticsService:
    """Enterprise Platform Cost, Usage, and System Throughput Analytics Service."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_usage_metrics(self) -> Dict[str, Any]:
        """Aggregate total documents, page count, total storage, and job status distribution."""
        # Total documents count
        doc_count_res = await self.db.execute(select(func.count(Document.id)))
        total_documents = doc_count_res.scalar() or 0

        # Total pages count
        page_count_res = await self.db.execute(select(func.count(DocumentPage.id)))
        total_pages = page_count_res.scalar() or 0

        # Total file storage in MB
        size_res = await self.db.execute(select(func.sum(Document.file_size_bytes)))
        total_bytes = size_res.scalar() or 0
        total_storage_mb = round(total_bytes / (1024 * 1024), 2)

        # Job distribution by status
        job_res = await self.db.execute(
            select(OCRJob.status, func.count(OCRJob.id)).group_by(OCRJob.status)
        )
        job_stats = {status_name: count for status_name, count in job_res.all()}

        return {
            "total_documents_processed": total_documents,
            "total_pages_processed": total_pages,
            "total_storage_mb": total_storage_mb,
            "job_statistics": job_stats,
            "gpu_hours_estimated": round(total_pages * 0.0005, 3),
        }
