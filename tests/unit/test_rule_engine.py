import pytest
from src.infrastructure.automation.rule_engine import RuleEngine, AutomationRuleDefinition, RuleCondition


def test_rule_engine_evaluation():
    rule = AutomationRuleDefinition(
        rule_id="r1",
        name="High Value Invoice Routing",
        target_category="Invoice",
        condition=RuleCondition(field_name="total_amount", operator="GREATER_THAN", value=1000.0),
        target_action="ROUTE_TO_FINANCE_APPROVAL",
    )

    engine = RuleEngine([rule])

    # Metadata matching condition
    actions_matched = engine.evaluate_rules("Invoice", {"total_amount": 5000.0})
    assert len(actions_matched) == 1
    assert actions_matched[0] == "ROUTE_TO_FINANCE_APPROVAL"

    # Metadata not matching condition
    actions_unmatched = engine.evaluate_rules("Invoice", {"total_amount": 500.0})
    assert len(actions_unmatched) == 0
