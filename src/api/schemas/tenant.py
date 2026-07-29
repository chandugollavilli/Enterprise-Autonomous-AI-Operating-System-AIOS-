from typing import Optional, List
from pydantic import BaseModel, EmailStr


class TenantCreateRequest(BaseModel):
    slug: str
    name: str
    contact_email: EmailStr
    max_documents: int = 10000
    max_pages_per_month: int = 50000


class TenantQuotaDTO(BaseModel):
    max_documents: int
    max_pages_per_month: int
    max_storage_mb: float
    current_documents_count: int
    current_pages_this_month: int


class TenantResponse(BaseModel):
    id: str
    slug: str
    name: str
    status: str
    contact_email: str
    created_at: str
