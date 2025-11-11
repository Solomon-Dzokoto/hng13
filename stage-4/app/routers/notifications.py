"""
Notifications router for handling notification requests.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional
import logging
import uuid
from datetime import datetime

from app.schemas import (
    CreateNotificationRequest,
    NotificationResponse,
    NotificationStatusResponse,
    NotificationData,
    NotificationStatusData,
    NotificationStatus,
    UpdateStatusRequest,
)
from app.services.rabbitmq import publish_notification
from app.services.redis import check_idempotency, store_idempotency
from app.services.database import create_notification, get_notification, update_notification_status
from app.middleware.auth import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def create_notification_endpoint(
    request: CreateNotificationRequest,
    x_correlation_id: Optional[str] = Header(None),
    current_user: dict = Depends(verify_token),
):
    """
    Create and queue a new notification.
    Supports idempotency via request_id.
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    
    logger.info(
        f"Received notification request",
        extra={
            "correlation_id": correlation_id,
            "request_id": request.request_id,
            "notification_type": request.notification_type,
            "user_id": request.user_id,
        },
    )
    
    # Check idempotency
    existing_notification_id = await check_idempotency(request.request_id)
    if existing_notification_id:
        logger.info(f"Duplicate request detected: {request.request_id}")
        
        # Return existing notification
        notification = await get_notification(existing_notification_id)
        if notification:
            return NotificationResponse(
                success=True,
                data=NotificationData(
                    notification_id=notification.id,
                    status=NotificationStatus(notification.status),
                    created_at=notification.created_at,
                ),
                message="Notification already exists (idempotent request)",
            )
    
    # Generate notification ID
    notification_id = f"ntf_{uuid.uuid4()}"
    
    try:
        # Store in database
        notification = await create_notification(
            notification_id=notification_id,
            notification_type=request.notification_type,
            user_id=request.user_id,
            template_code=request.template_code,
            variables=request.variables.model_dump(),
            request_id=request.request_id,
            priority=request.priority,
            custom_metadata=request.custom_metadata,
        )
        
        # Store idempotency mapping
        await store_idempotency(request.request_id, notification_id)
        
        # Publish to RabbitMQ
        await publish_notification(
            notification_id=notification_id,
            notification_type=request.notification_type,
            user_id=request.user_id,
            template_code=request.template_code,
            variables=request.variables.model_dump(),
            request_id=request.request_id,
            priority=request.priority,
            custom_metadata=request.custom_metadata or {},
            correlation_id=correlation_id,
        )
        
        logger.info(
            f"Notification queued successfully: {notification_id}",
            extra={"correlation_id": correlation_id, "notification_id": notification_id},
        )
        
        return NotificationResponse(
            success=True,
            data=NotificationData(
                notification_id=notification_id,
                status=NotificationStatus.pending,
                created_at=notification.created_at,
            ),
            message="Notification queued successfully",
        )
        
    except Exception as e:
        logger.error(
            f"Failed to create notification: {e}",
            extra={"correlation_id": correlation_id, "request_id": request.request_id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue notification",
        )


@router.get("/notifications/{notification_id}", response_model=NotificationStatusResponse)
async def get_notification_status(
    notification_id: str,
    current_user: dict = Depends(verify_token),
):
    """
    Get the status of a notification by ID.
    """
    notification = await get_notification(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    return NotificationStatusResponse(
        success=True,
        data=NotificationStatusData(
            notification_id=notification.id,
            status=NotificationStatus(notification.status),
            notification_type=notification.notification_type,
            created_at=notification.created_at,
            updated_at=notification.updated_at or notification.created_at,
            attempts=notification.attempts,
        ),
        message="Status retrieved successfully",
    )


@router.post("/notification_status", response_model=NotificationResponse)
async def update_notification_status_endpoint(
    request: UpdateStatusRequest,
    current_user: dict = Depends(verify_token),
):
    """
    Update notification status (internal endpoint for services).
    """
    try:
        await update_notification_status(
            notification_id=request.notification_id,
            status=request.status,
            error_message=request.error,
        )
        
        logger.info(f"Notification status updated: {request.notification_id} -> {request.status}")
        
        return NotificationResponse(
            success=True,
            data={"notification_id": request.notification_id, "updated": True},
            message="Status updated successfully",
        )
        
    except Exception as e:
        logger.error(f"Failed to update notification status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update status",
        )
