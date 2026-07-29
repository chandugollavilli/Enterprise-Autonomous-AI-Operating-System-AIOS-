import pytest
from src.infrastructure.solutions.legal_pack import LegalSolutionPack
from src.infrastructure.solutions.finance_pack import FinanceSolutionPack
from src.infrastructure.solutions.hr_pack import HRSolutionPack
from src.infrastructure.solutions.solution_registry import SolutionPackRegistry


@pytest.mark.asyncio
async def test_legal_solution_pack():
    legal = LegalSolutionPack()
    await legal.initialize()
    res = await legal.execute("Master Services Agreement with Unlimited Liability clause.", {"filename": "contract.pdf"})

    assert res["pack_id"] == "solution_legal"
    assert res["risk_score"] > 0.5
    assert len(res["risk_factors"]) >= 1


@pytest.mark.asyncio
async def test_finance_solution_pack():
    finance = FinanceSolutionPack()
    await finance.initialize()
    res = await finance.execute("Tax Invoice INV-2026-8891 Total: $12,500.00", {"filename": "invoice.pdf"})

    assert res["pack_id"] == "solution_finance"
    assert res["total_amount"] == 12500.00
    assert res["po_match_status"] == "matched"


@pytest.mark.asyncio
async def test_hr_solution_pack():
    hr = HRSolutionPack()
    await hr.initialize()
    res = await hr.execute("Jane Doe - 8 years Python and Machine Learning experience", {"filename": "resume.pdf"})

    assert res["pack_id"] == "solution_hr"
    assert "Python" in res["skills"]
    assert res["job_match_score"] > 0.8


def test_solution_registry():
    assert len(SolutionPackRegistry.list_packs()) >= 3
    assert SolutionPackRegistry.get_pack("solution_legal") is not None
