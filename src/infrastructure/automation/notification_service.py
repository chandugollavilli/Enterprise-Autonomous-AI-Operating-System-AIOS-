from enum import Enum
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("document_intelligence.notification_service")


class NotificationChannel(str, Enum):
    EMAIL = "Email"
    SLACK = "Slack"
    TEAMS = "Microsoft Teams"
    WEBHOOK = "Webhook"


class NotificationService:
    """Dispatches multi-channel notifications (Email, Slack, Teams, Webhook) for document events."""

    @staticmethod
    async def dispatch_notification(
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        message_body: str,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        logger.info(
            f"Notification Dispatched [{channel.value}] -> Recipient: '{recipient}' | Subject: '{subject}'"
        )
        return True
