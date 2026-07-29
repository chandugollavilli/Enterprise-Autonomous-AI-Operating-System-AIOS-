import pytest
from src.domain.tenant.tenant_context import TenantContext


def test_tenant_context_scoping():
    assert TenantContext.get_tenant_id() is None

    TenantContext.set_tenant_context("tenant_acme", org_id="org_engineering", role="OrgAdmin")
    assert TenantContext.get_tenant_id() == "tenant_acme"
    assert TenantContext.get_org_id() == "org_engineering"
    assert TenantContext.get_user_role() == "OrgAdmin"

    TenantContext.clear()
    assert TenantContext.get_tenant_id() is None
