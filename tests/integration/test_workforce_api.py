import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.repositories.postgres.models import User
from src.infrastructure.security.password import hash_password
from src.infrastructure.security.jwt import create_access_token
from tests.conftest import TestingSessionFactory

client = TestClient(app)


@pytest_asyncio.fixture
async def workforce_admin_headers():
    async with TestingSessionFactory() as session:
        user = User(
            email="workforce_admin@enterprise.com",
            hashed_password=hash_password("Password123!"),
            full_name="Workforce Admin User",
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(subject=user.id, claims={"role": "admin"})
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_workforce_api_endpoints(workforce_admin_headers):
    # 1. List Digital Employees API Endpoint
    res_emp = client.get("/api/v1/workforce/employees", headers=workforce_admin_headers)
    assert res_emp.status_code == 200
    employees = res_emp.json()
    assert len(employees) >= 3

    # 2. Register Digital Employee API Endpoint
    res_reg = client.post(
        "/api/v1/workforce/employees",
        json={
            "employee_id": "emp_proc_01",
            "name": "Procurement Auto-Specialist",
            "department": "Procurement",
            "role": "Vendor Evaluation Analyst",
            "skills": ["quotation_comparison", "supplier_risk_assessment"],
        },
        headers=workforce_admin_headers,
    )
    assert res_reg.status_code == 201

    # 3. Submit Task to Work Queue API Endpoint
    res_task = client.post(
        "/api/v1/workforce/tasks",
        json={"department": "Finance", "task_name": "Audit Q3 Expense Claims", "payload": {"claim_id": "c99"}, "priority": "high"},
        headers=workforce_admin_headers,
    )
    assert res_task.status_code == 201
    assert res_task.json()["status"] == "queued"

    # 4. Get Work Queues Status API Endpoint
    res_q = client.get("/api/v1/workforce/queues?department=Finance", headers=workforce_admin_headers)
    assert res_q.status_code == 200
    assert res_q.json()["pending_tasks_count"] >= 1

    # 5. Create Escalation Gate API Endpoint
    res_esc = client.post(
        "/api/v1/workforce/escalations",
        json={"employee_id": "emp_leg_01", "reason": "Uncapped liability clause detected in vendor agreement"},
        headers=workforce_admin_headers,
    )
    assert res_esc.status_code == 201
    assert res_esc.json()["status"] == "pending_human_review"

    # 6. Get Performance Analytics API Endpoint
    res_perf = client.get("/api/v1/workforce/performance", headers=workforce_admin_headers)
    assert res_perf.status_code == 200
    assert res_perf.json()["automation_rate_pct"] > 90.0
