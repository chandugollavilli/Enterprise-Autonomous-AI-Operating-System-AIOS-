from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.aios_service import AIOSService
from src.api.schemas.aios import (
    AgentCollaborateRequest,
    AgentCollaborateResponse,
    CopilotChatRequest,
    CopilotChatResponse,
    PlannerGoalRequest,
    PlannerGoalResponse,
)

router = APIRouter(tags=["Enterprise Autonomous AI Operating System (AIOS)"])


@router.post("/agents/collaborate", response_model=AgentCollaborateResponse, status_code=status.HTTP_200_OK)
async def collaborate_agents(
    payload: AgentCollaborateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger multi-agent collaborative goal decomposition, reasoning, and voting consensus."""
    service = AIOSService(db)
    res = await service.execute_collaboration(payload.goal)
    return AgentCollaborateResponse(**res)


@router.get("/agents/status")
async def get_agents_status(
    current_user: User = Depends(get_current_user),
):
    """Get active autonomous AIOS agents and health status."""
    return [
        {"agent_id": "planner", "name": "Planner Agent", "role": "Planning", "status": "active"},
        {"agent_id": "reasoning", "name": "Reasoning Agent", "role": "Reasoning", "status": "active"},
        {"agent_id": "research", "name": "Research Agent", "role": "Retrieval", "status": "active"},
        {"agent_id": "compliance", "name": "Compliance Agent", "role": "Audit", "status": "active"},
        {"agent_id": "report", "name": "Report Agent", "role": "Generation", "status": "active"},
    ]


@router.post("/copilot/chat", response_model=CopilotChatResponse)
async def copilot_chat(
    payload: CopilotChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Conversational Enterprise Copilot with multi-document reasoning and citation generation."""
    service = AIOSService(db)
    res = await service.copilot_chat(payload.message)
    return CopilotChatResponse(**res)


@router.post("/planner/create", response_model=PlannerGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_autonomous_plan(
    payload: PlannerGoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Decompose high-level goal into dependency DAG execution plan."""
    service = AIOSService(db)
    res = await service.create_plan(payload.goal)
    return PlannerGoalResponse(**res)


@router.get("/knowledge/search")
async def search_knowledge_graph(
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search Enterprise Knowledge Graph entities and relationship links."""
    service = AIOSService(db)
    return await service.search_knowledge(query)


@router.get("/memory/query")
async def query_memory(
    query: str,
    memory_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query Hierarchical Long-Term Semantic Memory records."""
    service = AIOSService(db)
    return await service.query_memory(query, memory_type)
