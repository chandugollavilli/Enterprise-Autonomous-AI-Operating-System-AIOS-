from celery import Celery
from src.config import settings
from src.infrastructure.celery.queues import CELERY_QUEUES, route_ocr_task

celery_app = Celery(
    "document_intelligence_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=settings.DEBUG,
    task_eager_propagates=True,
    task_queues=CELERY_QUEUES,
    task_routes=(route_ocr_task,),
    task_default_queue="normal_priority",
    task_default_exchange="ocr_exchange",
    task_default_routing_key="ocr.normal",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=1800,  # 30 mins hard limit per task
    task_soft_time_limit=1500,
)
