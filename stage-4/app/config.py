"""
Configuration management using Pydantic Settings.
Loads environment variables and provides typed configuration.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    env: str = "development"
    log_level: str = "info"
    allowed_origins: List[str] = ["*"]
    
    # Database
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Redis
    redis_url: str
    redis_max_connections: int = 50
    idempotency_ttl_seconds: int = 604800  # 7 days
    
    # RabbitMQ
    rabbitmq_url: str
    rabbitmq_exchange: str = "notifications.direct"
    rabbitmq_email_queue: str = "email.queue"
    rabbitmq_push_queue: str = "push.queue"
    rabbitmq_failed_queue: str = "failed.queue"
    rabbitmq_prefetch_count: int = 10
    
    # JWT Authentication
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY","secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM","HS256")
    jwt_audience: str = "notification-api"
    jwt_issuer: str = "notification-gateway"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 20
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # External Services
    user_service_url: str = os.getenv("USER_SERVICE_URL","http://localhost:8001")
    template_service_url: str = os.getenv("TEMPLATE_SERVICE_URL","http://localhost:8002")
    
    # Deployment
    deployment_environment: str = "staging"
    health_check_timeout: int = 5
    graceful_shutdown_timeout: int = 30
    
    # Container Image (for CI/CD)
    image_registry: str = "ghcr.io"
    image_name: str = "notification-gateway"
    image_tag: str = "latest"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
