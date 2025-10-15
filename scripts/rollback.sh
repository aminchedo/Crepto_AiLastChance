#!/bin/bash

# Bolt AI Crypto - Rollback Script
# Rolls back to previous deployment

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"

echo "=========================================="
echo "Rolling Back Deployment"
echo "=========================================="

cd "$PROJECT_ROOT"

# Stop current containers
echo "Stopping current containers..."
docker-compose down

# Find most recent backup
LATEST_POSTGRES_BACKUP=$(ls -t "$BACKUP_DIR"/postgres_*.sql.gz 2>/dev/null | head -n 1)
LATEST_REDIS_BACKUP=$(ls -t "$BACKUP_DIR"/redis_*.rdb 2>/dev/null | head -n 1)

if [ -z "$LATEST_POSTGRES_BACKUP" ]; then
    echo "Error: No PostgreSQL backup found"
    exit 1
fi

echo "Found backups:"
echo "  PostgreSQL: $LATEST_POSTGRES_BACKUP"
echo "  Redis: $LATEST_REDIS_BACKUP"
echo ""

read -p "Do you want to restore from these backups? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

# Start only database services
echo "Starting database services..."
docker-compose up -d postgres redis

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 10

# Load environment variables
if [ -f ".env" ]; then
    export $(cat ".env" | grep -v '^#' | xargs)
fi

POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-bolt_ai_crypto}

# Restore PostgreSQL
echo "Restoring PostgreSQL database..."
gunzip -c "$LATEST_POSTGRES_BACKUP" | docker exec -i bolt_postgres psql -U "$POSTGRES_USER" "$POSTGRES_DB"
echo "✓ PostgreSQL restored"

# Restore Redis
if [ -n "$LATEST_REDIS_BACKUP" ]; then
    echo "Restoring Redis data..."
    docker cp "$LATEST_REDIS_BACKUP" bolt_redis:/data/dump.rdb
    docker-compose restart redis
    echo "✓ Redis restored"
fi

# Checkout previous git commit (if using git)
if [ -d ".git" ]; then
    echo "Rolling back to previous git commit..."
    git checkout HEAD~1
fi

# Rebuild and start all services
echo "Rebuilding and starting all services..."
docker-compose build
docker-compose up -d

# Wait for services
sleep 10

# Health check
echo "Performing health checks..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Rollback successful - Backend is healthy"
else
    echo "✗ Rollback failed - Backend is not healthy"
    exit 1
fi

echo ""
echo "=========================================="
echo "Rollback completed successfully!"
echo "=========================================="
docker-compose ps

