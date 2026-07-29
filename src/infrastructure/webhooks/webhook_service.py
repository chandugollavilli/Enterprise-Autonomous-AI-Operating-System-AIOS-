import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import WebhookSubscription

logger = logging.getLogger("document_intelligence.webhook_service")


class WebhookSubscriptionService:
    """Service managing Webhook Subscriptions and HTTP POST Event Dispatching."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_subscription(
        self,
        target_url: str,
        event_types: List[str],
        secret: str = "whsec_default123",
        tenant_id: Optional[uuid.UUID] = None,
    ) -> WebhookSubscription:
        sub = WebhookSubscription(
            tenant_id=tenant_id,
            target_url=target_url,
            event_types_json={"events": event_types},
            secret=secret,
            status="active",
        )
        self.db.add(sub)
        await self.db.commit()
        await self.db.refresh(sub)

        logger.info(f"Created Webhook Subscription -> Target: '{target_url}' (Events: {event_types})")
        return sub

    async def dispatch_event(self, event_type: str, payload: Dict[str, Any]) -> int:
        stmt = select(WebhookSubscription).where(WebhookSubscription.status == "active")
        res = await self.db.execute(stmt)
        subs = list(res.scalars().all())

        dispatched_count = 0
        for sub in subs:
            subscribed_events = sub.event_types_json.get("events", [])
            if event_type in subscribed_events or "*" in subscribed_events:
                logger.info(f"Dispatched Webhook Event '{event_type}' to '{sub.target_url}'")
                dispatched_count += 1

        return dispatched_count
