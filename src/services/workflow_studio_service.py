import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import WorkflowDefinition, WorkflowVersion
from src.domain.workflow.graph_validator import WorkflowGraphValidator, WorkflowNodeSpec, WorkflowEdgeSpec
from src.infrastructure.workflow.state_machine import WorkflowStateMachine, WorkflowState

logger = logging.getLogger("document_intelligence.workflow_studio_service")


class WorkflowStudioService:
    """Service orchestrating visual workflow graph CRUD, graph validation, publishing, and version management."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_workflow(
        self,
        name: str,
        category: str = "document_automation",
        tenant_id: Optional[uuid.UUID] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[WorkflowDefinition, WorkflowVersion]:
        # Validate graph
        node_specs = [WorkflowNodeSpec(**n) for n in (nodes or [])]
        edge_specs = [WorkflowEdgeSpec(**e) for e in (edges or [])]

        is_valid, errors = WorkflowGraphValidator.validate_graph(node_specs, edge_specs)
        if not is_valid and (nodes or edges):
            raise ValueError(f"Workflow graph validation failed: {', '.join(errors)}")

        definition = WorkflowDefinition(
            tenant_id=tenant_id,
            name=name,
            category=category,
            status="draft",
        )
        self.db.add(definition)
        await self.db.flush()

        version = WorkflowVersion(
            workflow_id=definition.id,
            version="v1.0",
            graph_json={"nodes": nodes or [], "edges": edges or []},
            is_active=True,
        )
        self.db.add(version)
        await self.db.commit()

        logger.info(f"Created Visual Workflow Definition: '{name}' (ID: {definition.id})")
        return definition, version

    async def publish_workflow(self, workflow_id: uuid.UUID) -> WorkflowDefinition:
        stmt = select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
        definition = (await self.db.execute(stmt)).scalar_one_or_none()
        if not definition:
            raise ValueError(f"Workflow Definition '{workflow_id}' not found.")

        if not WorkflowStateMachine.can_transition(definition.status, "published"):
            raise ValueError(f"Cannot transition workflow state from '{definition.status}' to 'published'.")

        definition.status = "published"
        await self.db.commit()

        logger.info(f"Published Workflow Definition '{workflow_id}'")
        return definition

    async def list_workflows(self) -> List[WorkflowDefinition]:
        stmt = select(WorkflowDefinition)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_workflow_by_id(self, workflow_id: uuid.UUID) -> Optional[WorkflowDefinition]:
        stmt = select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
