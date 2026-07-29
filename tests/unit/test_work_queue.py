import pytest
from src.infrastructure.workforce.work_queue import WorkQueueManager


def test_work_queue_manager():
    wq = WorkQueueManager()
    item = wq.enqueue_task("Finance", "Audit Q3 Expense Report", {"report_id": "rep_102"}, priority="high")

    assert item["department"] == "Finance"
    assert item["priority"] == "high"

    status = wq.get_queue_status("Finance")
    assert status["pending_tasks_count"] == 1
