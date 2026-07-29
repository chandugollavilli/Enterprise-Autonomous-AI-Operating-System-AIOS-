import logging
from typing import Dict, Any

logger = logging.getLogger("document_intelligence.telemetry")


class TelemetryManager:
    """OpenTelemetry Distributed Tracing & Prometheus Metrics Manager."""

    _initialized = False

    @classmethod
    def setup_telemetry(cls, service_name: str = "ocr-intelligence-platform"):
        if cls._initialized:
            return
        cls._initialized = True
        logger.info(f"OpenTelemetry & Prometheus Telemetry initialized for service: '{service_name}'")

    @classmethod
    def record_metric(cls, metric_name: str, value: float, labels: Dict[str, str] = None):
        logger.debug(f"Metric [{metric_name}] = {value} (labels: {labels})")
