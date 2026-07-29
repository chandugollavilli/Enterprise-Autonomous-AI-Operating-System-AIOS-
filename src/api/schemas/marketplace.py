from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl


class MarketplacePackageDTO(BaseModel):
    package_id: str
    name: str
    category: str
    publisher: str
    version: str
    rating: float
    downloads: int


class PluginInstallResponse(BaseModel):
    installation_id: str
    package_id: str
    status: str
    installed_at: str


class WebhookCreateRequest(BaseModel):
    target_url: str
    event_types: List[str]  # e.g. ["document.uploaded", "workflow.completed"]
    secret: Optional[str] = "whsec_default123"


class WebhookSubscriptionResponse(BaseModel):
    id: str
    target_url: str
    event_types: List[str]
    status: str
    created_at: str
