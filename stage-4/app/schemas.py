"""
Pydantic schemas for request/response validation.
All naming follows snake_case convention.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class NotificationType(str, Enum):
    """Notification delivery type."""
    email = "email"
    push = "push"


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    pending = "pending"
    delivered = "delivered"
    failed = "failed"


class UserData(BaseModel):
    """User-specific data for template variable substitution."""
    name: str = Field(..., description="User's name")
    link: HttpUrl = Field(..., description="Action link")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreateNotificationRequest(BaseModel):
    """Request schema for creating a notification."""
    notification_type: NotificationType = Field(..., description="Type of notification")
    user_id: str = Field(..., description="Target user UUID")
    template_code: str = Field(..., description="Template identifier")
    variables: UserData = Field(..., description="Template variables")
    request_id: str = Field(..., description="Idempotency key")
    priority: int = Field(..., ge=1, le=10, description="Priority (1=highest)")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    
    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user_id is a valid UUID."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("user_id must be a valid UUID")
        return v


class NotificationData(BaseModel):
    """Notification data in response."""
    notification_id: str
    status: NotificationStatus
    created_at: datetime


class NotificationStatusData(BaseModel):
    """Detailed notification status."""
    notification_id: str
    status: NotificationStatus
    notification_type: NotificationType
    created_at: datetime
    updated_at: datetime
    attempts: int


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    page: int = Field(..., description="Current page")
    total_pages: int = Field(..., description="Total pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: str
    meta: Optional[PaginationMeta] = None


class NotificationResponse(APIResponse):
    """Response for notification creation."""
    data: Optional[NotificationData] = None


class NotificationStatusResponse(APIResponse):
    """Response for notification status query."""
    data: Optional[NotificationStatusData] = None


class UpdateStatusRequest(BaseModel):
    """Request to update notification status (internal use)."""
    notification_id: str
    status: NotificationStatus
    timestamp: Optional[datetime] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime
    dependencies: Dict[str, str] = Field(..., description="Dependency health status")
