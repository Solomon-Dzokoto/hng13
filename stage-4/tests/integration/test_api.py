"""
Integration tests for notification API endpoints.
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "dependencies" in data


@pytest.mark.asyncio
async def test_create_notification_unauthorized():
    """Test creating notification without auth token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/notifications",
            json={
                "notification_type": "email",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "template_code": "welcome",
                "variables": {
                    "name": "Test User",
                    "link": "https://example.com",
                },
                "request_id": "test_req_1",
                "priority": 1,
            },
        )
        assert response.status_code == 403  # Forbidden without auth
