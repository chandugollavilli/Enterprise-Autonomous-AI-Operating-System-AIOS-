import time
import logging
from typing import Dict, Any, List, Optional
from src.infrastructure.automation.document_classifier import DocumentClassifier, DocumentCategory
from src.infrastructure.automation.rule_engine import RuleEngine, AutomationRuleDefinition, RuleCondition
from src.infrastructure.automation.notification_service import NotificationService, NotificationChannel

logger = logging.getLogger("document_intelligence.automation_workflow")


class AutomationWorkflowEngine:
    """Orchestrates event-driven document processing pipelines."""

    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        self.rule_engine = rule_engine or RuleEngine()

    async def execute_document_pipeline(
        self,
        document_text: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        meta = metadata or {}

        # 1. Automatic Document Classification
        category, confidence = DocumentClassifier.classify_document(document_text, filename)

        # 2. Rule Evaluation
        triggered_actions = self.rule_engine.evaluate_rules(category.value, meta)

        # 3. Trigger Action Notifications
        notifications_sent = []
        if "NOTIFY_SLACK" in triggered_actions or category == DocumentCategory.INVOICE:
            sent = await NotificationService.dispatch_notification(
                channel=NotificationChannel.SLACK,
                recipient="#finance-alerts",
                subject=f"New {category.value} Processed: {filename}",
                message_body=f"Document '{filename}' classified as {category.value} (Confidence: {confidence}).",
            )
            notifications_sent.append("Slack")

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "filename": filename,
            "category": category.value,
            "confidence": confidence,
            "triggered_actions": triggered_actions,
            "notifications_sent": notifications_sent,
            "duration_ms": elapsed_ms,
        }
