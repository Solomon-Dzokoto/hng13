#!/bin/bash
# RabbitMQ initialization script for creating exchanges and queues

# Wait for RabbitMQ to be ready
sleep 10

# Declare exchange
rabbitmqadmin declare exchange name=notifications.direct type=direct durable=true

# Declare queues
rabbitmqadmin declare queue name=email.queue durable=true arguments='{"x-message-ttl":86400000,"x-max-length":100000}'
rabbitmqadmin declare queue name=push.queue durable=true arguments='{"x-message-ttl":86400000,"x-max-length":100000}'
rabbitmqadmin declare queue name=failed.queue durable=true

# Bind queues to exchange
rabbitmqadmin declare binding source=notifications.direct destination=email.queue routing_key=notification.email
rabbitmqadmin declare binding source=notifications.direct destination=push.queue routing_key=notification.push

echo "RabbitMQ initialization complete"
