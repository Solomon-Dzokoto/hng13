"""
RabbitMQ service for message publishing.
"""

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from typing import Optional, Dict, Any
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global RabbitMQ connection and channel
connection: Optional[aio_pika.Connection] = None
channel: Optional[aio_pika.Channel] = None
exchange: Optional[aio_pika.Exchange] = None


async def init_rabbitmq():
    """Initialize RabbitMQ connection and declare exchange/queues."""
    global connection, channel, exchange
    
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    
    # Set QoS (prefetch count)
    await channel.set_qos(prefetch_count=settings.rabbitmq_prefetch_count)
    
    # Declare exchange
    exchange = await channel.declare_exchange(
        settings.rabbitmq_exchange,
        ExchangeType.DIRECT,
        durable=True,
    )
    
    # Declare queues
    email_queue = await channel.declare_queue(
        settings.rabbitmq_email_queue,
        durable=True,
        arguments={
            "x-message-ttl": 86400000,  # 24 hours
            "x-max-length": 100000,
        },
    )
    
    push_queue = await channel.declare_queue(
        settings.rabbitmq_push_queue,
        durable=True,
        arguments={
            "x-message-ttl": 86400000,
            "x-max-length": 100000,
        },
    )
    
    failed_queue = await channel.declare_queue(
        settings.rabbitmq_failed_queue,
        durable=True,
    )
    
    # Bind queues to exchange
    await email_queue.bind(exchange, routing_key="notification.email")
    await push_queue.bind(exchange, routing_key="notification.push")
    
    logger.info("RabbitMQ connection and queues initialized")


async def close_rabbitmq():
    """Close RabbitMQ connection."""
    global connection
    if connection:
        await connection.close()
        logger.info("RabbitMQ connection closed")


async def check_rabbitmq_health() -> bool:
    """Check if RabbitMQ is accessible."""
    try:
        return connection is not None and not connection.is_closed
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        return False


async def publish_notification(
    notification_id: str,
    notification_type: str,
    user_id: str,
    template_code: str,
    variables: Dict[str, Any],
    request_id: str,
    priority: int,
    custom_metadata: Dict[str, Any],
    correlation_id: str,
):
    """
    Publish notification message to RabbitMQ.
    """
    # Prepare message payload
    payload = {
        "notification_id": notification_id,
        "notification_type": notification_type,
        "user_id": user_id,
        "template_code": template_code,
        "variables": variables,
        "request_id": request_id,
        "priority": priority,
        "custom_metadata": custom_metadata,
    }
    
    # Create message
    message = Message(
        body=json.dumps(payload).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        headers={
            "correlation_id": correlation_id,
            "attempts": 0,
            "notification_type": notification_type,
        },
        priority=priority,
    )
    
    # Determine routing key based on notification type
    routing_key = f"notification.{notification_type}"
    
    # Publish to exchange
    await exchange.publish(
        message,
        routing_key=routing_key,
    )
    
    logger.info(
        f"Published message to {routing_key}",
        extra={
            "notification_id": notification_id,
            "correlation_id": correlation_id,
        },
    )
