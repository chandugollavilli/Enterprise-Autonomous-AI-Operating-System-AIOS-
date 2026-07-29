from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class AgentCollaborateRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = None


class AgentCollaborateResponse(BaseModel):
    session_id: str
    goal: str
    plan: Dict[str, Any]
    reasoning: Dict[str, Any]
    consensus_vote: Dict[str, int]
    status: str
    duration_ms: float


class CopilotChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class CopilotChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    confidence_score: float
    suggested_actions: List[str]


class PlannerGoalRequest(BaseModel):
    goal: str
    constraints: Optional[Dict[str, Any]] = None


class PlannerGoalResponse(BaseModel):
    goal_id: str
    goal: str
    tasks: List[Dict[str, Any]]
    status: str
