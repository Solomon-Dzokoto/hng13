"""
Health check router.
"""

from fastapi import APIRouter, Response, status
from datetime import datetime
import logging

from app.schemas import HealthResponse
from app.services.database import check_db_health
from app.services.redis import check_redis_health
from app.services.rabbitmq import check_rabbitmq_health

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response):
    """
    Health check endpoint that verifies all dependencies.
    Returns 200 if healthy, 503 if any dependency is down.
    """
    dependencies = {
        "postgres": "ok",
        "redis": "ok",
        "rabbitmq": "ok",
    }
    
    overall_status = "ok"
    
    # Check PostgreSQL
    try:
        if not await check_db_health():
            dependencies["postgres"] = "down"
            overall_status = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        dependencies["postgres"] = "down"
        overall_status = "degraded"
    
    # Check Redis
    try:
        if not await check_redis_health():
            dependencies["redis"] = "down"
            overall_status = "degraded"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        dependencies["redis"] = "down"
        overall_status = "degraded"
    
    # Check RabbitMQ
    try:
        if not await check_rabbitmq_health():
            dependencies["rabbitmq"] = "down"
            overall_status = "degraded"
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        dependencies["rabbitmq"] = "down"
        overall_status = "degraded"
    
    # Set HTTP status code based on health
    if overall_status == "degraded":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        dependencies=dependencies,
    )
