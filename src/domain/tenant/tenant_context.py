from contextvars import ContextVar
from typing import Optional
import logging

logger = logging.getLogger("document_intelligence.tenant_context")

_tenant_id_var: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)
_org_id_var: ContextVar[Optional[str]] = ContextVar("org_id", default=None)
_user_role_var: ContextVar[Optional[str]] = ContextVar("user_role", default=None)


class TenantContext:
    """Async Request Scoped ContextVar Manager for Multi-Tenant Isolation."""

    @classmethod
    def set_tenant_context(cls, tenant_id: str, org_id: Optional[str] = None, role: Optional[str] = None):
        _tenant_id_var.set(tenant_id)
        if org_id:
            _org_id_var.set(org_id)
        if role:
            _user_role_var.set(role)
        logger.debug(f"Set TenantContext: tenant_id='{tenant_id}', org_id='{org_id}', role='{role}'")

    @classmethod
    def get_tenant_id(cls) -> Optional[str]:
        return _tenant_id_var.get()

    @classmethod
    def get_org_id(cls) -> Optional[str]:
        return _org_id_var.get()

    @classmethod
    def get_user_role(cls) -> Optional[str]:
        return _user_role_var.get()

    @classmethod
    def clear(cls):
        _tenant_id_var.set(None)
        _org_id_var.set(None)
        _user_role_var.set(None)
