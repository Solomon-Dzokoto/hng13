"""
Redis service for caching and idempotency.
"""

import redis.asyncio as redis
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection."""
    global redis_client
    
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections,
    )
    
    # Test connection
    await redis_client.ping()
    logger.info("Redis connection established")


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def check_redis_health() -> bool:
    """Check if Redis is accessible."""
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


async def check_idempotency(request_id: str) -> Optional[str]:
    """
    Check if request_id has been processed before.
    Returns notification_id if exists, None otherwise.
    """
    key = f"idempotency:{request_id}"
    notification_id = await redis_client.get(key)
    return notification_id


async def store_idempotency(request_id: str, notification_id: str):
    """
    Store idempotency mapping with TTL.
    """
    key = f"idempotency:{request_id}"
    await redis_client.setex(
        key,
        settings.idempotency_ttl_seconds,
        notification_id,
    )


async def check_rate_limit(identifier: str, limit: int, window: int) -> bool:
    """
    Check if identifier has exceeded rate limit.
    Uses sliding window counter.
    
    Args:
        identifier: User ID, API key, or IP address
        limit: Maximum requests allowed
        window: Time window in seconds
    
    Returns:
        True if within limit, False if exceeded
    """
    key = f"ratelimit:{identifier}"
    
    current = await redis_client.get(key)
    
    if current is None:
        # First request in window
        await redis_client.setex(key, window, 1)
        return True
    
    current_count = int(current)
    
    if current_count < limit:
        await redis_client.incr(key)
        return True
    
    return False


async def get_cache(key: str) -> Optional[str]:
    """Get cached value."""
    return await redis_client.get(key)


async def set_cache(key: str, value: str, ttl: int = 300):
    """Set cached value with TTL."""
    await redis_client.setex(key, ttl, value)
