"""
Main FastAPI application entry point for the Notification Gateway API.

This module initializes the FastAPI app, configures middleware, registers routers,
and sets up health checks and monitoring.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uuid
from datetime import datetime

from app.config import settings
from app.routers import notifications, health
from app.middleware.correlation import correlation_id_middleware
from app.middleware.auth import auth_middleware
from app.middleware.rate_limit import rate_limit_middleware
from app.services.database import init_db, close_db
from app.services.rabbitmq import init_rabbitmq, close_rabbitmq
from app.services.redis import init_redis, close_redis
from app.utils.logger import setup_logging
from app.utils.metrics import setup_metrics

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Notification Gateway API")
    
    try:
        # Initialize database connection
        await init_db()
        logger.info("Database connection established")
        
        # Initialize Redis connection
        await init_redis()
        logger.info("Redis connection established")
        
        # Initialize RabbitMQ connection
        await init_rabbitmq()
        logger.info("RabbitMQ connection established")
        
        # Setup Prometheus metrics
        setup_metrics(app)
        logger.info("Metrics endpoint configured")
        
        logger.info(f"Application started successfully on {settings.host}:{settings.port}")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notification Gateway API")
    
    try:
        await close_rabbitmq()
        logger.info("RabbitMQ connection closed")
        
        await close_redis()
        logger.info("Redis connection closed")
        
        await close_db()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title="Notification Gateway API",
    description="API Gateway for distributed notification system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add custom middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to all requests for tracing."""
    return await correlation_id_middleware(request, call_next)


@app.middleware("http")
async def rate_limiting(request: Request, call_next):
    """Apply rate limiting to API requests."""
    return await rate_limit_middleware(request, call_next)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    correlation_id = request.state.correlation_id if hasattr(request.state, "correlation_id") else str(uuid.uuid4())
    
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "correlation_id": correlation_id,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "meta": None,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handler for validation errors.
    """
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": str(exc),
            "message": "Invalid request",
            "meta": None,
        },
    )


# Register routers
app.include_router(health.router, tags=["health"])
app.include_router(
    notifications.router,
    prefix="/api/v1",
    tags=["notifications"],
)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Notification Gateway API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development",
        log_level=settings.log_level.lower(),
    )
