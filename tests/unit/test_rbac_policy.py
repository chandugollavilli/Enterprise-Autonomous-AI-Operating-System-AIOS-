import pytest
from src.infrastructure.security.rbac_policy import EnterpriseRBAC, Role


def test_rbac_permissions():
    assert EnterpriseRBAC.has_permission("SystemAdmin", "tenant:create") is True
    assert EnterpriseRBAC.has_permission("Viewer", "document:read") is True
    assert EnterpriseRBAC.has_permission("Viewer", "tenant:create") is False
    assert EnterpriseRBAC.has_permission("Reviewer", "ocr:correct") is True
