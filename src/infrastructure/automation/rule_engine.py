from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("document_intelligence.rule_engine")


@dataclass
class RuleCondition:
    field_name: str
    operator: str  # "EQUALS", "GREATER_THAN", "CONTAINS"
    value: Any


@dataclass
class AutomationRuleDefinition:
    rule_id: str
    name: str
    target_category: str
    condition: RuleCondition
    target_action: str  # "ROUTE_TO_FINANCE", "FLAG_FOR_HUMAN_REVIEW", "NOTIFY_SLACK"


class RuleEngine:
    """Configurable Rule Evaluation Engine for Enterprise Document Routing & Actions."""

    def __init__(self, rules: Optional[List[AutomationRuleDefinition]] = None):
        self.rules = rules or []

    def add_rule(self, rule: AutomationRuleDefinition):
        self.rules.append(rule)

    def evaluate_rules(self, category: str, metadata: Dict[str, Any]) -> List[str]:
        triggered_actions: List[str] = []

        for rule in self.rules:
            if rule.target_category != category and rule.target_category != "*":
                continue

            field_val = metadata.get(rule.condition.field_name)
            if field_val is None:
                continue

            matched = False
            op = rule.condition.operator.upper()
            target_val = rule.condition.value

            if op == "EQUALS" and str(field_val).lower() == str(target_val).lower():
                matched = True
            elif op == "GREATER_THAN" and float(field_val) > float(target_val):
                matched = True
            elif op == "CONTAINS" and str(target_val).lower() in str(field_val).lower():
                matched = True

            if matched:
                logger.info(f"Rule '{rule.rule_id}' triggered -> Action: '{rule.target_action}'")
                triggered_actions.append(rule.target_action)

        return triggered_actions
