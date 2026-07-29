from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class RegionDTO(BaseModel):
    region_id: str
    name: str
    cloud_provider: str
    status: str
    cluster_count: int


class ClusterDTO(BaseModel):
    cluster_id: str
    region_id: str
    name: str
    cloud_provider: str
    status: str


class DigitalTwinTopologyDTO(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    system_health: str


class FinOpsCostResponse(BaseModel):
    total_monthly_spend_usd: float
    breakdown: Dict[str, float]
    budget_usd: float
    budget_utilisation_pct: float
    cost_saving_recommendations: List[str]


class RunbookExecuteRequest(BaseModel):
    runbook_name: str
    target: str


class RunbookExecuteResponse(BaseModel):
    execution_id: str
    runbook_name: str
    target: str
    status: str
    output: str
