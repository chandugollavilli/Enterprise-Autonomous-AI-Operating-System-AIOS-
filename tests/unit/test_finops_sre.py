import pytest
from src.infrastructure.platform.finops_engine import FinOpsCostEngine
from src.infrastructure.platform.sre_engine import SRERemediationEngine


def test_finops_cost_engine():
    costs = FinOpsCostEngine.get_cost_analytics()
    assert costs["total_monthly_spend_usd"] > 1000.0
    assert costs["budget_utilisation_pct"] < 100.0
    assert len(costs["cost_saving_recommendations"]) >= 1


def test_sre_remediation_engine():
    sre = SRERemediationEngine()
    incidents = sre.list_incidents()
    assert len(incidents) >= 1

    rb_res = sre.execute_runbook("Restart Worker Pool", "celery_worker_us_1")
    assert rb_res["status"] == "success"
    assert "celery_worker_us_1" in rb_res["output"]
