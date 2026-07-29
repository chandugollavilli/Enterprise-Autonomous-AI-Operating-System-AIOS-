import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import SolutionPack, GeneratedReport
from src.infrastructure.solutions.solution_registry import SolutionPackRegistry
from src.infrastructure.reports.report_exporter import ReportExporterEngine, ReportFormat
from src.infrastructure.dashboards.dashboard_engine import SolutionDashboardEngine

logger = logging.getLogger("document_intelligence.solution_service")


class SolutionPackService:
    """Service managing solution pack installation, domain workflow execution, and report generation."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def install_pack(self, pack_id: str, tenant_id: Optional[uuid.UUID] = None) -> SolutionPack:
        pack = SolutionPackRegistry.get_pack(pack_id)
        if not pack:
            raise ValueError(f"Solution Pack '{pack_id}' not found in registry.")

        info = pack.pack_info()
        installed_pack = SolutionPack(
            tenant_id=tenant_id,
            pack_id=pack_id,
            name=info["name"],
            category=info["category"],
            version=info["version"],
            status="installed",
        )
        self.db.add(installed_pack)
        await self.db.commit()
        await self.db.refresh(installed_pack)

        logger.info(f"Installed Solution Pack '{pack_id}' for Tenant {tenant_id}")
        return installed_pack

    async def execute_pack_analysis(
        self,
        pack_id: str,
        document_text: str,
        filename: str = "document.pdf",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pack = SolutionPackRegistry.get_pack(pack_id)
        if not pack:
            raise ValueError(f"Solution Pack '{pack_id}' not found in registry.")

        # Execute Domain Solution Pack Analysis
        analysis_result = await pack.execute(document_text, metadata)

        # Generate Executive Summary Report
        report_content = ReportExporterEngine.generate_report(
            pack_id=pack_id,
            document_filename=filename,
            analysis_result=analysis_result,
            fmt=ReportFormat.MARKDOWN,
        )

        # Persist Generated Report in PostgreSQL
        gen_report = GeneratedReport(
            pack_id=pack_id,
            report_format="markdown",
            report_content=report_content,
        )
        self.db.add(gen_report)
        await self.db.commit()

        analysis_result["report_id"] = str(gen_report.id)
        analysis_result["report_markdown"] = report_content

        return analysis_result

    async def get_dashboard(self, pack_id: str) -> Dict[str, Any]:
        return SolutionDashboardEngine.get_dashboard_metrics(pack_id)
