"""
Database models using SQLAlchemy.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class NotificationTypeEnum(str, enum.Enum):
    """Notification type enumeration."""
    email = "email"
    push = "push"


class NotificationStatusEnum(str, enum.Enum):
    """Notification status enumeration."""
    pending = "pending"
    delivered = "delivered"
    failed = "failed"


class Notification(Base):
    """
    Notification model for tracking notification requests and status.
    """
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    notification_type = Column(SQLEnum(NotificationTypeEnum), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    template_code = Column(String, nullable=False)
    variables = Column(JSON, nullable=False)
    request_id = Column(String, unique=True, nullable=False, index=True)
    priority = Column(Integer, nullable=False)
    custom_metadata = Column(JSON, nullable=True)
    status = Column(SQLEnum(NotificationStatusEnum), default=NotificationStatusEnum.pending, index=True)
    attempts = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status})>"
