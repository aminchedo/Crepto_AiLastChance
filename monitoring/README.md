# 📊 Crepto AI - Monitoring System

**Complete Prometheus + Grafana + Alertmanager Stack**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Services](#services)
5. [Dashboards](#dashboards)
6. [Alerts](#alerts)
7. [Integration](#integration)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This monitoring system provides:

- ✅ **Prometheus** - Metrics collection and storage
- ✅ **Grafana** - Beautiful dashboards and visualization
- ✅ **Alertmanager** - Alert routing and notifications
- ✅ **Node Exporter** - System metrics (CPU, Memory, Disk)
- ✅ **cAdvisor** - Container metrics
- ✅ **Custom Metrics** - Backend and Frontend application metrics

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- Ports available: 3000, 8080, 9090, 9093, 9100

### Option 1: Windows (Double-Click)

```bash
# Just double-click this file:
start-monitoring.bat
```

### Option 2: Manual Start

```bash
cd monitoring
docker-compose up -d
```

### Option 3: Verify Installation

```bash
# Linux/Mac
./scripts/verify-monitoring.sh

# Windows
docker-compose ps
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Crepto AI Application                 │
│  Backend (8000) | Proxy (3002) | Frontend (5173)│
└────────────┬────────────────────────────────────┘
             │ Metrics Export (/metrics)
             ↓
┌─────────────────────────────────────────────────┐
│              Prometheus (9090)                   │
│  • Scrapes metrics every 15s                    │
│  • Evaluates alert rules                        │
│  • Stores time-series data                      │
└────────────┬────────────────────────────────────┘
             │
        ┌────┴──────┐
        ↓           ↓
┌──────────────┐ ┌──────────────────┐
│ Alertmanager │ │ Grafana (3000)   │
│    (9093)    │ │ • Dashboards     │
│ • Alerts     │ │ • Visualization  │
│ • Routing    │ │ • Admin Panel    │
└──────────────┘ └──────────────────┘
        │
        ↓
┌──────────────────────┐
│  Alert Channels      │
│  • Email             │
│  • Slack (optional)  │
│  • Webhook           │
└──────────────────────┘
```

---

## 📊 Services

### 1. Prometheus (Port 9090)

**URL:** http://localhost:9090

**Features:**
- Metrics collection every 15s
- 30 days data retention
- Alert rule evaluation
- PromQL query interface

**Scrape Targets:**
```yaml
- Backend API:    host.docker.internal:8000/metrics
- Proxy Server:   host.docker.internal:3002/metrics
- Node Exporter:  localhost:9100/metrics
- cAdvisor:       localhost:8080/metrics
- Prometheus:     localhost:9090/metrics
- Alertmanager:   localhost:9093/metrics
```

**Access:**
```bash
# Web UI
http://localhost:9090

# API
http://localhost:9090/api/v1/query?query=up

# Targets
http://localhost:9090/targets

# Alerts
http://localhost:9090/alerts
```

---

### 2. Grafana (Port 3000)

**URL:** http://localhost:3000

**Credentials:**
- Username: `admin`
- Password: `admin123`

**Features:**
- Pre-configured Prometheus datasource
- Custom Crepto AI dashboard
- Real-time metrics visualization
- Alert annotations

**Dashboards:**
1. **Crepto AI - System Overview**
   - Service health status
   - CPU/Memory usage
   - API request rates
   - Error rates

**Import Additional Dashboards:**
```
1. Go to http://localhost:3000
2. Login (admin/admin123)
3. Click + → Import
4. Use ID: 1860 (Node Exporter Full)
5. Select Prometheus datasource
6. Click Import
```

---

### 3. Alertmanager (Port 9093)

**URL:** http://localhost:9093

**Features:**
- Alert deduplication
- Silencing
- Routing to different channels
- Email notifications

**Alert Routing:**
```
Critical Alerts  → Email + Slack (optional)
API Alerts       → api-team@crepto-ai.com
Performance      → ops-team@crepto-ai.com
Default          → Webhook
```

**Configure Email:**
Edit `alerting/alertmanager.yml`:
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@crepto-ai.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'
```

---

### 4. Node Exporter (Port 9100)

**URL:** http://localhost:9100

**Metrics:**
- CPU usage and load
- Memory usage
- Disk I/O and space
- Network statistics
- System uptime

---

### 5. cAdvisor (Port 8080)

**URL:** http://localhost:8080

**Metrics:**
- Container CPU usage
- Container memory usage
- Container network I/O
- Container filesystem usage

---

## 📈 Dashboards

### Crepto AI System Overview

**Location:** `grafana/dashboards/creptoai-dashboard.json`

**Panels:**

1. **Service Health Status**
   - Shows up/down status of all services
   - Real-time health monitoring

2. **Backend API Status**
   - Current status (UP/DOWN)
   - Color-coded indicator

3. **Proxy Server Status**
   - Current status (UP/DOWN)
   - Color-coded indicator

4. **CPU Usage**
   - System-wide CPU usage
   - Per-core breakdown

5. **Memory Usage**
   - RAM usage percentage
   - Available vs Used

**Access:**
```
http://localhost:3000/d/crepto-ai-overview/crepto-ai-system-overview
```

---

## 🚨 Alerts

### Configured Alert Rules

**Location:** `alerting/creptoai-alert-rules.yml`

#### API Health Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| BackendAPIDown | Backend down for 1min | Critical |
| ProxyServerDown | Proxy down for 1min | Critical |
| FrontendDown | Frontend down for 2min | Warning |

#### Performance Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighCPUUsage | CPU > 80% for 5min | Warning |
| HighMemoryUsage | Memory > 85% for 5min | Warning |
| HighDiskUsage | Disk > 85% for 5min | Warning |

#### API Latency Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| SlowAPIResponses | p95 > 2s for 5min | Warning |

#### Error Rate Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | Error rate > 5% for 5min | Critical |
| APIFailures | >10 5xx/sec for 2min | Warning |

#### External API Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| CoinMarketCapFailures | CMC error rate high | Warning |
| NewsAPIFailures | News API error rate high | Warning |

**View Alerts:**
```
http://localhost:9090/alerts
http://localhost:9093/#/alerts
```

---

## 🔌 Integration

### Backend Integration (Python/FastAPI)

**File:** `backend/metrics.py`

**1. Install dependencies:**
```bash
pip install prometheus-client
```

**2. Add to `backend/main.py`:**
```python
from metrics import metrics_middleware, metrics_endpoint, set_app_info

# Add middleware
app.middleware("http")(metrics_middleware)

# Add metrics endpoint
app.add_route("/metrics", metrics_endpoint, methods=["GET"])

# Set app info
set_app_info(version="1.0.0", environment="production")
```

**3. Track custom metrics:**
```python
from metrics import track_external_api_call, track_database_query

@track_external_api_call("coinmarketcap")
async def get_crypto_prices():
    # Your code here
    pass

@track_database_query("select_users")
async def get_users():
    # Your code here
    pass
```

---

### Frontend Integration (TypeScript/React)

**File:** `src/utils/prometheus-client.ts`

**1. Import and use:**
```typescript
import { prometheusClient, trackAPICall } from './utils/prometheus-client';

// Track page view
prometheusClient.trackPageView('/dashboard');

// Track user interaction
prometheusClient.trackInteraction('button_click', 'submit_form');

// Track API call
const data = await trackAPICall(
  () => fetch('/api/data'),
  '/api/data',
  'GET'
);

// Track custom metric
prometheusClient.track('custom_metric', 1, { label: 'value' });
```

**2. Enable metrics in `.env.local`:**
```env
VITE_ENABLE_METRICS=true
VITE_METRICS_ENDPOINT=http://localhost:3002/metrics
```

---

### Proxy Server Integration (Node.js)

**Add to `proxy-server/server.js`:**

```javascript
const promClient = require('prom-client');

// Create metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});

// Track requests
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.labels(req.method, req.path, res.statusCode).observe(duration);
  });
  next();
});
```

---

## 🔍 Monitoring Best Practices

### 1. Query Examples

**Check service health:**
```promql
up{job="backend-api"}
```

**Calculate error rate:**
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

**Get p95 latency:**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Check CPU usage:**
```promql
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

---

### 2. Dashboard Tips

- Use time range selector (top right)
- Set auto-refresh interval
- Create dashboard variables for filtering
- Use template variables for dynamic queries
- Add annotations for deployments

---

### 3. Alert Configuration

**Severity Levels:**
- `critical` - Requires immediate action
- `warning` - Needs attention soon
- `info` - Informational only

**Alert Timing:**
- Use `for:` clause to avoid flapping
- Set appropriate thresholds
- Test alerts before production

---

## 🐛 Troubleshooting

### Services Not Starting

**Check Docker:**
```bash
docker ps
docker-compose logs
```

**Check ports:**
```bash
netstat -ano | findstr :9090
netstat -ano | findstr :3000
```

---

### No Metrics in Prometheus

**1. Check targets:**
```
http://localhost:9090/targets
```

**2. Verify backend is exposing metrics:**
```bash
curl http://localhost:8000/metrics
```

**3. Check Prometheus logs:**
```bash
docker-compose logs prometheus
```

---

### Grafana Dashboard Not Loading

**1. Check datasource:**
```
http://localhost:3000/datasources
```

**2. Test connection:**
```
Settings → Test
```

**3. Reimport dashboard:**
```
Import → Upload JSON file
```

---

### Alerts Not Firing

**1. Check alert rules:**
```
http://localhost:9090/rules
```

**2. Check Alertmanager:**
```
http://localhost:9093/#/alerts
```

**3. Verify alert configuration:**
```bash
docker-compose exec prometheus promtool check rules /etc/prometheus/rules/*.yml
```

---

## 📦 Data Management

### Backup Metrics

```bash
# Backup Prometheus data
docker run --rm -v monitoring_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data

# Backup Grafana dashboards
docker run --rm -v monitoring_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

### Clean Old Data

```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Restart
docker-compose up -d
```

---

## 🔒 Security

### Change Default Passwords

**Grafana:**
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=YOUR_SECURE_PASSWORD
```

**Alertmanager Email:**
```yaml
smtp_auth_password: 'YOUR_APP_PASSWORD'
```

---

## 📞 Support

### Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f prometheus

# Restart a service
docker-compose restart grafana

# Check service health
docker-compose ps
```

---

## ✅ Success Checklist

- [ ] All services running (green status)
- [ ] Prometheus targets are UP
- [ ] Grafana login works
- [ ] Dashboard loads correctly
- [ ] Metrics are being collected
- [ ] Alerts are configured
- [ ] Email notifications work (if configured)

---

**Status:** ✅ Monitoring System Ready!

Access your dashboards:
- **Grafana:** http://localhost:3000 (admin/admin123)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

---

*Last Updated: 2025-10-15*  
*Version: 1.0.0*  
*Status: PRODUCTION READY*
