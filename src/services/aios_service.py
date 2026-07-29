import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import AgentSession, AgentTask, MemoryRecord, PlanningGoal
from src.infrastructure.aios.multi_agent_collaborator import MultiAgentCollaborator
from src.infrastructure.aios.knowledge_graph import EnterpriseKnowledgeGraph
from src.infrastructure.aios.memory_system import HierarchicalMemoryService
from src.infrastructure.aios.planner_engine import AutonomousPlannerEngine
from src.infrastructure.aios.copilot_engine import EnterpriseCopilotEngine

logger = logging.getLogger("document_intelligence.aios_service")


class AIOSService:
    """Service managing AIOS multi-agent collaboration, copilot execution, knowledge search, and memory management."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.collaborator = MultiAgentCollaborator()
        self.knowledge_graph = EnterpriseKnowledgeGraph()
        self.memory_service = HierarchicalMemoryService()

        # Seed sample Knowledge Graph Nodes
        self.knowledge_graph.add_node("doc_101", "Master Services Agreement 2026.pdf", "Contract", {"risk_score": 0.3})
        self.knowledge_graph.add_node("dept_legal", "Legal & Compliance Department", "Department")
        self.knowledge_graph.add_edge("doc_101", "dept_legal", "GOVERNED_BY")

    async def execute_collaboration(self, goal: str, tenant_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        # Perform Multi-Agent Collaboration
        collab_result = await self.collaborator.collaborate_on_goal(goal)

        # Persist Agent Session in PostgreSQL
        session = AgentSession(tenant_id=tenant_id, status="completed")
        self.db.add(session)
        await self.db.flush()

        task = AgentTask(
            session_id=session.id,
            agent_id="collaborator_coordinator",
            task_name=f"Goal Execution: {goal}",
            payload_json={"goal": goal},
            result_json=collab_result,
            status="completed",
        )
        self.db.add(task)
        await self.db.commit()

        collab_result["session_id"] = str(session.id)
        return collab_result

    async def copilot_chat(self, message: str) -> Dict[str, Any]:
        return EnterpriseCopilotEngine.process_chat(message)

    async def create_plan(self, goal: str, tenant_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        plan = AutonomousPlannerEngine.create_plan(goal)
        goal_entity = PlanningGoal(
            tenant_id=tenant_id,
            goal=goal,
            tasks_json={"tasks": plan["tasks"]},
            status="active",
        )
        self.db.add(goal_entity)
        await self.db.commit()

        plan["goal_id"] = str(goal_entity.id)
        return plan

    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        return self.knowledge_graph.search_entity(query)

    async def query_memory(self, query: str, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.memory_service.query_memory(query, memory_type)
