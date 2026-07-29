from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ModelInfoDTO(BaseModel):
    name: str
    category: str
    provider: str
    version: str
    capabilities: List[str]
    is_default: bool
    health_status: str


class PluginInfoDTO(BaseModel):
    name: str
    category: str
    version: str
    description: str
    author: str


class WorkflowStepDTO(BaseModel):
    step_id: str
    name: str
    action_name: str
    is_optional: bool


class WorkflowDTO(BaseModel):
    workflow_id: str
    name: str
    steps: List[WorkflowStepDTO]


class FeatureFlagDTO(BaseModel):
    name: str
    enabled: bool


class FeatureFlagUpdateRequest(BaseModel):
    enabled: bool


class UsageAnalyticsResponse(BaseModel):
    total_documents_processed: int
    total_pages_processed: int
    total_storage_mb: float
    job_statistics: Dict[str, int]
    gpu_hours_estimated: float
