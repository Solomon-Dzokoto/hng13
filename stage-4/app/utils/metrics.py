"""
Prometheus metrics configuration.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import logging

logger = logging.getLogger(__name__)

# Define metrics
api_requests_total = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
)

published_messages_total = Counter(
    "published_messages_total",
    "Total messages published to queue",
    ["notification_type"],
)

publish_errors_total = Counter(
    "publish_errors_total",
    "Total publish errors",
    ["notification_type"],
)

idempotency_hits_total = Counter(
    "idempotency_hits_total",
    "Total duplicate requests rejected",
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections",
    ["service"],
)


def setup_metrics(app):
    """
    Setup Prometheus metrics endpoint.
    """
    
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """
        Prometheus metrics endpoint.
        """
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )
    
    logger.info("Metrics endpoint configured at /metrics")
