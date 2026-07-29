from enum import Enum
from typing import Dict, Set, List
import logging

logger = logging.getLogger("document_intelligence.rbac_policy")


class Role(str, Enum):
    SYSTEM_ADMIN = "SystemAdmin"
    ORG_ADMIN = "OrgAdmin"
    MANAGER = "Manager"
    ANALYST = "Analyst"
    REVIEWER = "Reviewer"
    OPERATOR = "Operator"
    VIEWER = "Viewer"


class EnterpriseRBAC:
    """Enterprise Role-Based Access Control (RBAC) Policy & Permission Matrix."""

    # Role Permissions Mapping
    ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
        Role.SYSTEM_ADMIN: {
            "tenant:create", "tenant:read", "tenant:update", "tenant:delete",
            "document:upload", "document:read", "document:delete",
            "ocr:process", "search:execute", "chat:execute", "admin:access",
        },
        Role.ORG_ADMIN: {
            "tenant:read", "tenant:update",
            "document:upload", "document:read", "document:delete",
            "ocr:process", "search:execute", "chat:execute", "admin:read",
        },
        Role.MANAGER: {
            "document:upload", "document:read", "ocr:process",
            "search:execute", "chat:execute",
        },
        Role.ANALYST: {
            "document:read", "search:execute", "chat:execute",
        },
        Role.REVIEWER: {
            "document:read", "ocr:correct", "search:execute", "chat:execute",
        },
        Role.OPERATOR: {
            "document:upload", "ocr:process", "search:execute",
        },
        Role.VIEWER: {
            "document:read", "search:execute",
        },
    }

    @classmethod
    def has_permission(cls, role_name: str, permission: str) -> bool:
        try:
            role = Role(role_name)
        except ValueError:
            logger.warning(f"Unknown Role string: {role_name}")
            return False

        allowed = cls.ROLE_PERMISSIONS.get(role, set())
        return permission in allowed or "admin:access" in allowed
