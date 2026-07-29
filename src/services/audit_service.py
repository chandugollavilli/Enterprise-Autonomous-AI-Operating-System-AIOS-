import uuid
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.postgres.models import AuditLog

logger = logging.getLogger("document_intelligence.audit_service")


class EnterpriseAuditService:
    """Service producing immutable audit records for authentication, document processing, and administrative actions."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def log_event(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        event_details = details or {}
        if tenant_id:
            event_details["tenant_id"] = tenant_id
        if correlation_id:
            event_details["correlation_id"] = correlation_id

        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=correlation_id,
            ip_address=ip_address,
            details=event_details,
        )
        self.db.add(log_entry)
        await self.db.commit()

        logger.info(
            f"Audit Log: action='{action}', resource='{resource_type}:{resource_id}', user='{user_id}', tenant='{tenant_id}'"
        )
        return log_entry
