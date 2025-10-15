#!/bin/bash
# Monitoring Stack Verification Script

echo "=================================="
echo "Crepto AI - Monitoring Verification"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_service() {
    local service=$1
    local url=$2
    local name=$3
    
    echo -n "Checking $name... "
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Check Docker
echo "1. Checking Docker..."
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi

echo ""

# Check services
echo "2. Checking Monitoring Services..."
check_service "prometheus" "http://localhost:9090/-/healthy" "Prometheus"
check_service "grafana" "http://localhost:3000/api/health" "Grafana"
check_service "alertmanager" "http://localhost:9093/-/healthy" "Alertmanager"
check_service "node-exporter" "http://localhost:9100/metrics" "Node Exporter"
check_service "cadvisor" "http://localhost:8080/healthz" "cAdvisor"

echo ""

# Check Prometheus targets
echo "3. Checking Prometheus Targets..."
TARGETS=$(curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"up"' | wc -l)
echo -e "Active targets: ${GREEN}$TARGETS${NC}"

echo ""

# Check Grafana datasources
echo "4. Checking Grafana Datasources..."
DATASOURCES=$(curl -s http://admin:admin123@localhost:3000/api/datasources | grep -o '"name":"Prometheus"' | wc -l)
if [ "$DATASOURCES" -gt 0 ]; then
    echo -e "${GREEN}✓ Prometheus datasource configured${NC}"
else
    echo -e "${YELLOW}⚠ Prometheus datasource not found${NC}"
fi

echo ""

# Check alert rules
echo "5. Checking Alert Rules..."
RULES=$(curl -s http://localhost:9090/api/v1/rules | grep -o '"name"' | wc -l)
echo -e "Loaded alert rules: ${GREEN}$RULES${NC}"

echo ""

# Summary
echo "=================================="
echo "Verification Complete!"
echo "=================================="
echo ""
echo "Access URLs:"
echo "  Prometheus:   http://localhost:9090"
echo "  Grafana:      http://localhost:3000"
echo "  Alertmanager: http://localhost:9093"
echo ""
echo "Credentials:"
echo "  Grafana - admin:admin123"
echo ""
