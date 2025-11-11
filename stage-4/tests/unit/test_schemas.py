"""
Unit tests for notification schemas validation.
"""

import pytest
from pydantic import ValidationError

from app.schemas import (
    CreateNotificationRequest,
    UserData,
    NotificationType,
)


def test_create_notification_request_valid():
    """Test valid notification request."""
    request = CreateNotificationRequest(
        notification_type=NotificationType.email,
        user_id="550e8400-e29b-41d4-a716-446655440000",
        template_code="welcome_email",
        variables=UserData(
            name="John Doe",
            link="https://example.com/verify",
        ),
        request_id="req_123456",
        priority=1,
    )
    
    assert request.notification_type == NotificationType.email
    assert request.priority == 1


def test_create_notification_request_invalid_uuid():
    """Test invalid user_id UUID."""
    with pytest.raises(ValidationError):
        CreateNotificationRequest(
            notification_type=NotificationType.email,
            user_id="invalid-uuid",
            template_code="welcome_email",
            variables=UserData(
                name="John Doe",
                link="https://example.com/verify",
            ),
            request_id="req_123456",
            priority=1,
        )


def test_create_notification_request_invalid_priority():
    """Test invalid priority value."""
    with pytest.raises(ValidationError):
        CreateNotificationRequest(
            notification_type=NotificationType.email,
            user_id="550e8400-e29b-41d4-a716-446655440000",
            template_code="welcome_email",
            variables=UserData(
                name="John Doe",
                link="https://example.com/verify",
            ),
            request_id="req_123456",
            priority=20,  # Out of range
        )
