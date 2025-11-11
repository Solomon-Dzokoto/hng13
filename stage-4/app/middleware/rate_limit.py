"""
Rate limiting middleware.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from app.services.redis import check_rate_limit
from app.config import settings

logger = logging.getLogger(__name__)


async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting based on user ID or IP address.
    """
    # Skip rate limiting for health endpoint
    if request.url.path == "/health":
        return await call_next(request)
    
    # Get identifier (user ID from auth or IP address)
    identifier = None
    
    # Try to get user from auth header
    auth_header = request.headers.get("authorization")
    if auth_header:
        # Extract user identifier from token (simplified)
        # In real implementation, decode JWT to get user_id
        identifier = auth_header
    else:
        # Fallback to IP address
        identifier = request.client.host
    
    # Check rate limit
    try:
        within_limit = await check_rate_limit(
            identifier=f"api:{identifier}",
            limit=settings.rate_limit_per_minute,
            window=60,  # 1 minute
        )
        
        if not within_limit:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "data": None,
                    "error": "Rate limit exceeded. Retry after 60 seconds",
                    "message": "Too many requests",
                    "meta": None,
                },
            )
    except Exception as e:
        # Log error but don't block request if rate limiting fails
        logger.error(f"Rate limiting error: {e}")
    
    return await call_next(request)
