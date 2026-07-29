from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ConnectorCreateRequest(BaseModel):
    name: str
    connector_type: str  # "s3", "sftp", "sharepoint"
    config: Dict[str, Any]


class ConnectorResponse(BaseModel):
    id: str
    name: str
    connector_type: str
    status: str
    config: Dict[str, Any]


class SyncJobResponse(BaseModel):
    job_id: str
    connector_id: str
    status: str
    documents_synced: int


class AutomationRuleCreateRequest(BaseModel):
    name: str
    target_category: str
    field_name: str
    operator: str  # "EQUALS", "GREATER_THAN", "CONTAINS"
    threshold_value: str
    target_action: str


class AutomationRuleResponse(BaseModel):
    id: str
    name: str
    target_category: str
    field_name: str
    operator: str
    threshold_value: str
    target_action: str
