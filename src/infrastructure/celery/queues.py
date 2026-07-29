from kombu import Exchange, Queue

# Define Direct Exchanges for OCR Queue Architecture
ocr_exchange = Exchange("ocr_exchange", type="direct")
dlq_exchange = Exchange("ocr_dlq_exchange", type="direct")

# Celery Priority & Dead-Letter Queues
CELERY_QUEUES = [
    Queue(
        "high_priority",
        ocr_exchange,
        routing_key="ocr.high",
        queue_arguments={"x-max-priority": 10},
    ),
    Queue(
        "normal_priority",
        ocr_exchange,
        routing_key="ocr.normal",
        queue_arguments={"x-max-priority": 5},
    ),
    Queue(
        "low_priority",
        ocr_exchange,
        routing_key="ocr.low",
        queue_arguments={"x-max-priority": 1},
    ),
    Queue(
        "ocr_dlq",
        dlq_exchange,
        routing_key="ocr.dlq",
    ),
]


def route_ocr_task(name, args, kwargs, options, task=None, **kw):
    """Custom task router assigning tasks to Kombu priority queues."""
    priority = kwargs.get("priority", "normal") if kwargs else "normal"
    if priority == "high":
        return {"queue": "high_priority", "routing_key": "ocr.high"}
    elif priority == "low":
        return {"queue": "low_priority", "routing_key": "ocr.low"}
    return {"queue": "normal_priority", "routing_key": "ocr.normal"}
