from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class DigitalEmployeeDTO(BaseModel):
    employee_id: str
    name: str
    department: str
    role: str
    skills: List[str]
    tasks_completed: int
    status: str


class EmployeeCreateRequest(BaseModel):
    employee_id: str
    name: str
    department: str
    role: str
    skills: List[str]


class TaskSubmitRequest(BaseModel):
    department: str
    task_name: str
    payload: Dict[str, Any]
    priority: Optional[str] = "medium"


class TaskSubmitResponse(BaseModel):
    task_id: str
    task_name: str
    department: str
    priority: str
    status: str


class EscalationCreateRequest(BaseModel):
    employee_id: str
    reason: str
    context: Optional[Dict[str, Any]] = None


class EscalationResponse(BaseModel):
    escalation_id: str
    employee_id: str
    reason: str
    assignee_role: str
    status: str


class PerformanceAnalyticsResponse(BaseModel):
    total_digital_employees: int
    tasks_completed_24h: int
    automation_rate_pct: float
    average_task_latency_ms: float
    human_escalation_rate_pct: float
    department_throughput: Dict[str, int]
