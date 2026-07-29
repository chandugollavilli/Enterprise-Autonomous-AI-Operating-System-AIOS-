import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import Connector, ConnectorSyncJob, AutomationRule, WorkflowTemplate
from src.infrastructure.connectors.s3_connector import S3ConnectorAdapter
from src.infrastructure.automation.automation_workflow import AutomationWorkflowEngine
from src.infrastructure.automation.rule_engine import RuleEngine, AutomationRuleDefinition, RuleCondition

logger = logging.getLogger("document_intelligence.automation_service")


class AutomationService:
    """Application Service orchestrating connector configuration, automated sync jobs, and rule management."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.workflow_engine = AutomationWorkflowEngine()

    async def register_connector(
        self,
        name: str,
        connector_type: str,
        config: Dict[str, Any],
        tenant_id: Optional[uuid.UUID] = None,
    ) -> Connector:
        connector = Connector(
            tenant_id=tenant_id,
            connector_type=connector_type,
            name=name,
            config_json=config,
            status="active",
        )
        self.db.add(connector)
        await self.db.commit()
        await self.db.refresh(connector)
        return connector

    async def trigger_connector_sync(self, connector_id: uuid.UUID) -> ConnectorSyncJob:
        stmt = select(Connector).where(Connector.id == connector_id)
        connector = (await self.db.execute(stmt)).scalar_one_or_none()
        if not connector:
            raise ValueError(f"Connector '{connector_id}' not found.")

        # Create Sync Job
        sync_job = ConnectorSyncJob(connector_id=connector_id, status="running", documents_synced=0)
        self.db.add(sync_job)
        await self.db.commit()

        # Instantiate Adapter & Sync
        adapter = S3ConnectorAdapter(bucket_name=connector.config_json.get("bucket", "enterprise-docs"))
        await adapter.initialize()
        await adapter.connect()

        docs = await adapter.sync()

        sync_job.documents_synced = len(docs)
        sync_job.status = "completed"
        await self.db.commit()

        logger.info(f"Triggered Sync for Connector '{connector.name}'. Synced {len(docs)} files.")
        return sync_job

    async def create_automation_rule(
        self,
        name: str,
        target_category: str,
        field_name: str,
        operator: str,
        threshold_value: str,
        target_action: str,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> AutomationRule:
        rule = AutomationRule(
            tenant_id=tenant_id,
            name=name,
            target_category=target_category,
            field_name=field_name,
            operator=operator,
            threshold_value=threshold_value,
            target_action=target_action,
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule
