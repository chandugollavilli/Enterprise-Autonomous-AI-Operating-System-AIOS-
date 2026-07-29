from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class NodeSpecDTO(BaseModel):
    id: str
    type: str
    name: str
    config: Optional[Dict[str, Any]] = None


class EdgeSpecDTO(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    condition_expression: Optional[str] = None


class WorkflowCreateRequest(BaseModel):
    name: str
    category: str = "document_automation"
    nodes: List[NodeSpecDTO] = []
    edges: List[EdgeSpecDTO] = []


class WorkflowResponse(BaseModel):
    id: str
    name: str
    category: str
    status: str
    created_at: str


class ApprovalTaskResolveRequest(BaseModel):
    resolution: str  # "approved" or "rejected"
    comments: Optional[str] = ""


class ApprovalTaskResponse(BaseModel):
    task_id: str
    execution_id: str
    node_id: str
    title: str
    assignee_role: str
    status: str
