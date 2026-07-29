from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SolutionPackDTO(BaseModel):
    pack_id: str
    name: str
    version: str
    category: str
    description: str


class SolutionExecuteRequest(BaseModel):
    document_text: str
    filename: str = "document.pdf"
    metadata: Optional[Dict[str, Any]] = None


class SolutionExecuteResponse(BaseModel):
    pack_id: str
    document_type: str
    report_id: str
    report_markdown: str
    analysis_details: Dict[str, Any]


class DashboardResponse(BaseModel):
    pack_id: str
    total_documents_processed: int
    average_ai_confidence: float
    average_processing_time_ms: float
    risk_distribution: Dict[str, int]
    sla_compliance_rate: str
