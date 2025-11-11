"""
Correlation ID middleware for request tracing.
"""

from fastapi import Request
import uuid
import logging

logger = logging.getLogger(__name__)


async def correlation_id_middleware(request: Request, call_next):
    """
    Add or extract correlation ID for request tracing.
    """
    # Get correlation ID from header or generate new one
    correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
    
    # Store in request state
    request.state.correlation_id = correlation_id
    
    # Add to response headers
    response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id
    
    return response
