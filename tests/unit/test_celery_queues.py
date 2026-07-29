import pytest
from src.infrastructure.celery.queues import route_ocr_task, CELERY_QUEUES


def test_celery_queue_definitions():
    queue_names = {q.name for q in CELERY_QUEUES}
    assert "high_priority" in queue_names
    assert "normal_priority" in queue_names
    assert "low_priority" in queue_names
    assert "ocr_dlq" in queue_names


def test_route_ocr_task_priority():
    high_route = route_ocr_task(None, None, {"priority": "high"}, None)
    assert high_route["queue"] == "high_priority"
    assert high_route["routing_key"] == "ocr.high"

    low_route = route_ocr_task(None, None, {"priority": "low"}, None)
    assert low_route["queue"] == "low_priority"
    assert low_route["routing_key"] == "ocr.low"

    normal_route = route_ocr_task(None, None, {"priority": "normal"}, None)
    assert normal_route["queue"] == "normal_priority"
    assert normal_route["routing_key"] == "ocr.normal"
