# Notification Gateway API

Distributed notification system API Gateway built with FastAPI. Handles email and push notification requests using message queues (RabbitMQ) for asynchronous processing.

## Features

- ✅ RESTful API with OpenAPI/Swagger documentation
- ✅ JWT authentication and authorization
- ✅ Request idempotency using Redis
- ✅ Asynchronous message publishing to RabbitMQ
- ✅ Rate limiting per user/API key
- ✅ Health checks and monitoring (Prometheus metrics)
- ✅ Correlation ID tracking for distributed tracing
- ✅ PostgreSQL for persistent storage
- ✅ Docker containerization
- ✅ CI/CD with GitHub Actions

## Architecture

```
Client → API Gateway → RabbitMQ → [Email Service, Push Service]
                ↓
          [Redis Cache]
                ↓
          [PostgreSQL]
```

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL (via SQLAlchemy + asyncpg)
- **Cache**: Redis
- **Message Queue**: RabbitMQ (aio-pika)
- **Auth**: JWT (python-jose)
- **Monitoring**: Prometheus
- **Testing**: pytest + pytest-asyncio

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

## Quick Start

### 1. Clone the repository

```bash
cd stage-4
```

### 2. Copy environment variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration values.

### 3. Start services with Docker Compose

```bash
docker-compose up -d
```

This will start:
- API Gateway (port 8000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (port 5672, management UI: 15672)
- Prometheus (port 9091)

### 4. Check health

```bash
curl http://localhost:8000/health
```

### 5. Access API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- RabbitMQ Management: http://localhost:15672 (guest/guest)

## Development Setup

### Local development without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Run tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests (requires services running)
pytest tests/integration -v

# With coverage
pytest --cov=app --cov-report=html
```

### Code formatting and linting

```bash
# Format code
black app/

# Lint
flake8 app/ --max-line-length=120

# Type checking
mypy app/
```

## API Usage

### Authentication

All endpoints (except `/health`) require JWT authentication.

```bash
# Example with Bearer token
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "email",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "template_code": "welcome_email",
    "variables": {
      "name": "John Doe",
      "link": "https://example.com/verify"
    },
    "request_id": "req_123456789",
    "priority": 1
  }'
```

### Idempotency

Use the `request_id` field to prevent duplicate notifications. The same `request_id` will return the existing notification.

### Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "message": "Operation successful",
  "meta": null
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `RABBITMQ_URL` | RabbitMQ connection string | - |
| `JWT_SECRET_KEY` | Secret key for JWT | - |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute limit | `100` |
| `IDEMPOTENCY_TTL_SECONDS` | Idempotency key TTL | `604800` (7 days) |

See `.env.example` for all available variables.

## Message Queue Structure

### Exchange
- **Name**: `notifications.direct`
- **Type**: direct

### Queues
- `email.queue` → Email Service (routing key: `notification.email`)
- `push.queue` → Push Service (routing key: `notification.push`)
- `failed.queue` → Dead Letter Queue

### Message Format

```json
{
  "notification_id": "ntf_uuid",
  "notification_type": "email",
  "user_id": "user_uuid",
  "template_code": "welcome_email",
  "variables": { ... },
  "request_id": "req_id",
  "priority": 1,
  "metadata": { ... }
}
```

## Monitoring

### Metrics (Prometheus)

Access metrics at: http://localhost:9090/metrics

Key metrics:
- `api_requests_total` - Total API requests
- `api_request_duration_seconds` - Request latency
- `published_messages_total` - Messages published to queue
- `idempotency_hits_total` - Duplicate request rejections

### Health Checks

```bash
curl http://localhost:8000/health
```

Returns dependency status for PostgreSQL, Redis, and RabbitMQ.

## CI/CD

### Continuous Integration (`.github/workflows/ci.yml`)

Runs on every PR and push:
1. Code linting (Black, Flake8, MyPy)
2. Unit tests
3. Integration tests
4. Docker build
5. Security scanning (Trivy)

### Continuous Deployment (`.github/workflows/cd.yml`)

Runs on merge to `main`:
1. Build and push Docker image to registry
2. Deploy to staging (automatic)
3. Run health checks
4. Deploy to production (manual approval)
5. Blue-green deployment with rollback

## Deployment

### Request a deployment server

Use the HNG command in your channel:

```
/request-server environment:staging type:k8s-cluster region:eu-west-1 team:notifications
```

### GitHub Secrets Required

For CI/CD to work, add these secrets to your repository:

- `STAGING_SSH_KEY` - SSH private key for staging
- `STAGING_HOST` - Staging server hostname
- `STAGING_USER` - SSH username for staging
- `STAGING_URL` - Staging API URL
- `PROD_SSH_KEY` - SSH private key for production
- `PROD_HOST` - Production server hostname
- `PROD_USER` - SSH username for production
- `PROD_URL` - Production API URL
- `SLACK_WEBHOOK` - Slack webhook for notifications
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### Manual Deployment

```bash
# Build image
docker build -t notification-gateway:v1.0.0 .

# Tag for registry
docker tag notification-gateway:v1.0.0 ghcr.io/your-org/notification-gateway:v1.0.0

# Push to registry
docker push ghcr.io/your-org/notification-gateway:v1.0.0

# Deploy on server
ssh user@server 'cd /opt/notification-gateway && docker-compose pull && docker-compose up -d'
```

## Project Structure

```
stage-4/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── dependencies.py         # FastAPI dependencies
│   ├── middleware/
│   │   ├── auth.py            # JWT authentication
│   │   ├── idempotency.py     # Idempotency middleware
│   │   ├── rate_limit.py      # Rate limiting
│   │   └── correlation.py     # Correlation ID tracking
│   ├── routers/
│   │   ├── notifications.py   # Notification endpoints
│   │   └── health.py          # Health check endpoint
│   ├── services/
│   │   ├── rabbitmq.py        # RabbitMQ publisher
│   │   ├── redis.py           # Redis operations
│   │   └── database.py        # Database operations
│   └── utils/
│       ├── logger.py          # Structured logging
│       └── metrics.py         # Prometheus metrics
├── tests/
│   ├── unit/
│   └── integration/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── openapi.yml
├── prometheus.yml
└── README.md
```

## Performance Targets

- ✅ API response time: < 100ms
- ✅ Throughput: 1,000+ notifications/min
- ✅ Delivery success rate: 99.5%+
- ✅ Horizontal scaling support

## Troubleshooting

### RabbitMQ connection issues

```bash
# Check RabbitMQ status
docker-compose logs rabbitmq

# Verify queues
curl -u guest:guest http://localhost:15672/api/queues
```

### Redis connection issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Database migration issues

```bash
# Reset database (development only!)
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a PR
5. Wait for CI checks to pass

## License

MIT License - see LICENSE file for details

## Team

HNG13 Internship - Stage 4
Notification System Team

## Support

For issues or questions, contact the team or create an issue in the repository.
