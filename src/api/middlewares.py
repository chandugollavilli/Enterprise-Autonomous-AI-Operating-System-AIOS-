import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.infrastructure.telemetry.logging import request_id_var, user_id_var

logger = logging.getLogger("document_intelligence.middleware")


class EnterpriseSecurityAndTelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware executing Request ID tracing, timing metrics, and security headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        # Extract or generate X-Request-ID header
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        user_id_var.set("")  # reset per request

        response: Response = await call_next(request)

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Inject Security Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(execution_time_ms)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        logger.info(
            f"HTTP {request.method} {request.url.path} -> {response.status_code} ({execution_time_ms}ms)"
        )

        return response
