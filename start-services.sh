#!/bin/bash

# Bolt AI Crypto - Service Startup Script
# This script starts services in the correct order

set -e

echo "🚀 Starting Bolt AI Crypto Services..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Clean up any existing containers
echo "📦 Step 1: Cleaning up existing containers..."
docker-compose down 2>/dev/null || true
docker rm -f bolt_redis bolt_postgres bolt_backend bolt_frontend bolt_nginx 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 2: Start database and cache
echo "🗄️  Step 2: Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis
echo "   Waiting for services to be healthy (30 seconds)..."
sleep 30
docker-compose ps postgres redis
echo -e "${GREEN}✓ Database and cache started${NC}"
echo ""

# Step 3: Build backend (optional - can be slow)
echo "🔨 Step 3: Building backend..."
echo "   ${YELLOW}This may take 5-10 minutes on first build...${NC}"
if docker-compose build backend; then
    echo -e "${GREEN}✓ Backend built successfully${NC}"
else
    echo -e "${RED}✗ Backend build failed - continuing anyway${NC}"
fi
echo ""

# Step 4: Build frontend (optional - can be slow)
echo "🔨 Step 4: Building frontend..."
echo "   ${YELLOW}This may take 2-5 minutes on first build...${NC}"
if docker-compose build frontend; then
    echo -e "${GREEN}✓ Frontend built successfully${NC}"
else
    echo -e "${RED}✗ Frontend build failed - continuing anyway${NC}"
fi
echo ""

# Step 5: Start backend
echo "🚀 Step 5: Starting backend..."
if docker-compose up -d backend; then
    echo "   Waiting for backend to be ready (20 seconds)..."
    sleep 20
    echo -e "${GREEN}✓ Backend started${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
fi
echo ""

# Step 6: Start frontend
echo "🚀 Step 6: Starting frontend..."
if docker-compose up -d frontend; then
    echo "   Waiting for frontend to be ready (10 seconds)..."
    sleep 10
    echo -e "${GREEN}✓ Frontend started${NC}"
else
    echo -e "${RED}✗ Frontend failed to start${NC}"
fi
echo ""

# Step 7: Start monitoring (optional)
echo "📊 Step 7: Starting monitoring services..."
docker-compose up -d prometheus grafana 2>/dev/null || echo "   Skipping monitoring (optional)"
echo ""

# Step 8: Check status
echo "🔍 Step 8: Checking service status..."
docker-compose ps
echo ""

# Step 9: Display access URLs
echo "✨ Services are starting up!"
echo ""
echo "📱 Access URLs:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend:     http://localhost:8000"
echo "   API Docs:    http://localhost:8000/api/docs"
echo "   Prometheus:  http://localhost:9090"
echo "   Grafana:     http://localhost:3001 (admin/admin123)"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Check status:     docker-compose ps"
echo "   Stop services:    docker-compose down"
echo "   Restart service:  docker-compose restart backend"
echo ""
echo "🎯 Next Steps:"
echo "   1. Wait 30 seconds for all services to start"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Click settings icon (⚙️) to manage feature flags"
echo "   4. Check 'docker-compose logs -f' for any errors"
echo ""
echo -e "${GREEN}✓ Startup script complete!${NC}"