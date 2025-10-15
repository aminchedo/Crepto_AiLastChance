#!/bin/bash

# Bolt AI Crypto - Deployment Script
# Usage: ./scripts/deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================="
echo "Deploying Bolt AI Crypto - ${ENVIRONMENT}"
echo "=========================================="

cd "$PROJECT_ROOT"

# Load environment variables
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "Loading environment variables from .env.${ENVIRONMENT}"
    export $(cat ".env.${ENVIRONMENT}" | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    echo "Loading environment variables from .env"
    export $(cat ".env" | grep -v '^#' | xargs)
else
    echo "Error: No environment file found"
    exit 1
fi

# Validate required environment variables
REQUIRED_VARS=("SECRET_KEY" "POSTGRES_PASSWORD")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo "Pulling latest code..."
    git pull origin main
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p backend/models backend/logs nginx/logs nginx/ssl monitoring/grafana/dashboards

# Backup database before deployment
echo "Creating database backup..."
./scripts/backup.sh

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Build new images
echo "Building Docker images..."
docker-compose build --no-cache

# Run database migrations
echo "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 10

# Health check
echo "Performing health checks..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is healthy"
        break
    fi
    echo "Waiting for backend... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "✗ Backend health check failed"
    echo "Rolling back deployment..."
    ./scripts/rollback.sh
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ Frontend is healthy"
else
    echo "✗ Frontend health check failed"
    ./scripts/rollback.sh
    exit 1
fi

# Display running services
echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
docker-compose ps
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/docs"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001"
echo ""
echo "Logs:"
echo "  docker-compose logs -f [service_name]"
echo ""

