"""
Database service for PostgreSQL operations.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import Optional
import logging

from app.config import settings
from app.models import Base, Notification, NotificationStatusEnum, NotificationTypeEnum

logger = logging.getLogger(__name__)

# Global engine and session maker
engine = None
async_session_maker = None


async def init_db():
    """Initialize database connection and create tables."""
    global engine, async_session_maker
    
    engine = create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.env == "development",
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


async def check_db_health() -> bool:
    """Check if database is accessible."""
    try:
        async with async_session_maker() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def create_notification(
    notification_id: str,
    notification_type: str,
    user_id: str,
    template_code: str,
    variables: dict,
    request_id: str,
    priority: int,
    custom_metadata: Optional[dict] = None,
) -> Notification:
    """Create a new notification record."""
    async with async_session_maker() as session:
        notification = Notification(
            id=notification_id,
            notification_type=NotificationTypeEnum(notification_type),
            user_id=user_id,
            template_code=template_code,
            variables=variables,
            request_id=request_id,
            priority=priority,
            custom_metadata=custom_metadata,
            status=NotificationStatusEnum.pending,
            attempts=0,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification


async def get_notification(notification_id: str) -> Optional[Notification]:
    """Get notification by ID."""
    async with async_session_maker() as session:
        result = await session.get(Notification, notification_id)
        return result


async def update_notification_status(
    notification_id: str,
    status: str,
    error_message: Optional[str] = None,
):
    """Update notification status."""
    async with async_session_maker() as session:
        notification = await session.get(Notification, notification_id)
        if notification:
            notification.status = NotificationStatusEnum(status)
            notification.attempts += 1
            if error_message:
                notification.error_message = error_message
            await session.commit()
