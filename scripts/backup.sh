#!/bin/bash

# Bolt AI Crypto - Backup Script
# Creates backups of PostgreSQL and Redis data

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "Creating Backup - $TIMESTAMP"
echo "=========================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-bolt_ai_crypto}

# Backup PostgreSQL
echo "Backing up PostgreSQL database..."
docker exec bolt_postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_DIR/postgres_${TIMESTAMP}.sql.gz"
echo "✓ PostgreSQL backup created: postgres_${TIMESTAMP}.sql.gz"

# Backup Redis
echo "Backing up Redis data..."
docker exec bolt_redis redis-cli BGSAVE
sleep 2
docker cp bolt_redis:/data/dump.rdb "$BACKUP_DIR/redis_${TIMESTAMP}.rdb"
echo "✓ Redis backup created: redis_${TIMESTAMP}.rdb"

# Backup environment file
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Backing up environment file..."
    cp "$PROJECT_ROOT/.env" "$BACKUP_DIR/env_${TIMESTAMP}.backup"
    echo "✓ Environment backup created: env_${TIMESTAMP}.backup"
fi

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo ""
echo "Backup completed successfully!"
echo "Location: $BACKUP_DIR"
echo "Size: $BACKUP_SIZE"
echo ""

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups (keeping last 7 days)..."
find "$BACKUP_DIR" -name "postgres_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "redis_*.rdb" -mtime +7 -delete
find "$BACKUP_DIR" -name "env_*.backup" -mtime +7 -delete
echo "✓ Old backups cleaned up"

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -n 10

