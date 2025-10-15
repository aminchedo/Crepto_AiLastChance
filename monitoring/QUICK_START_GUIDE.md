# 🚀 Monitoring System - Quick Start Guide

**Get your monitoring stack running in 2 minutes!**

---

## ⚡ Super Quick Start (Windows)

### Step 1: Start Monitoring

```bash
# Just double-click this file:
C:\project\Crepto_Ai\monitoring\start-monitoring.bat
```

**That's it!** Wait 30 seconds and your monitoring stack will be running.

---

## 🌐 Access Your Dashboards

After starting, open these URLs in your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | (none) |
| **Alertmanager** | http://localhost:9093 | (none) |

---

## ✅ Verify Everything Works

### 1. Check Services Running

```bash
cd C:\project\Crepto_Ai\monitoring
docker-compose ps
```

**Expected output:**
```
crepto_prometheus     running    0.0.0.0:9090->9090/tcp
crepto_grafana        running    0.0.0.0:3000->3000/tcp
crepto_alertmanager   running    0.0.0.0:9093->9093/tcp
crepto_node_exporter  running    0.0.0.0:9100->9100/tcp
crepto_cadvisor       running    0.0.0.0:8080->8080/tcp
```

All should show: `running` ✅

---

### 2. Check Prometheus Targets

Open: http://localhost:9090/targets

**All targets should be UP** (green):
- prometheus
- alertmanager
- node-exporter
- cadvisor

---

### 3. Open Grafana Dashboard

1. Go to: http://localhost:3000
2. Login: `admin` / `admin123`
3. Click **Dashboards** → **Crepto AI - System Overview**

You should see:
- ✅ Service health status
- ✅ CPU usage graph
- ✅ Memory usage graph

---

## 🔌 Connect to Your Crepto AI App

### Backend (Python)

**1. Install dependency:**
```bash
cd backend
pip install prometheus-client
```

**2. Add to `main.py`:**
```python
from metrics import metrics_middleware, metrics_endpoint

# Add middleware
app.middleware("http")(metrics_middleware)

# Add metrics endpoint
app.add_route("/metrics", metrics_endpoint, methods=["GET"])
```

**3. Restart backend:**
```bash
# Backend will now expose metrics at:
http://localhost:8000/metrics
```

---

### Frontend (React/TypeScript)

**1. Enable metrics in `.env.local`:**
```env
VITE_ENABLE_METRICS=true
VITE_METRICS_ENDPOINT=http://localhost:3002/metrics
```

**2. Use in your components:**
```typescript
import { prometheusClient } from './utils/prometheus-client';

// Track page view
prometheusClient.trackPageView('/dashboard');

// Track user action
prometheusClient.trackInteraction('button_click', 'submit');
```

**3. Restart frontend:**
```bash
npm run dev
```

---

## 📊 View Your Metrics

### Prometheus

**URL:** http://localhost:9090

**Try these queries:**

```promql
# Check if backend is up
up{job="backend-api"}

# Get CPU usage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Check HTTP request rate
rate(http_requests_total[5m])
```

---

### Grafana

**URL:** http://localhost:3000  
**Login:** admin / admin123

**Default Dashboard:**
- Click **Dashboards** (left menu)
- Select **Crepto AI - System Overview**

**Import More Dashboards:**
1. Click **+** → **Import**
2. Enter Dashboard ID: `1860` (Node Exporter Full)
3. Select **Prometheus** as datasource
4. Click **Import**

---

## 🚨 Set Up Alerts

### Email Notifications

**Edit:** `monitoring/alerting/alertmanager.yml`

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'your-email@gmail.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'  # Get from Gmail App Passwords
```

**Restart Alertmanager:**
```bash
docker-compose restart alertmanager
```

---

## 🛑 Stop Monitoring

```bash
# Option 1: Double-click
stop-monitoring.bat

# Option 2: Command line
cd C:\project\Crepto_Ai\monitoring
docker-compose down
```

---

## 🐛 Troubleshooting

### Problem: Services won't start

**Solution:**
```bash
# Check if Docker is running
docker ps

# Check port conflicts
netstat -ano | findstr :9090
netstat -ano | findstr :3000

# View logs
cd monitoring
docker-compose logs
```

---

### Problem: No metrics in Prometheus

**Solution:**
```bash
# Check if backend is exposing metrics
curl http://localhost:8000/metrics

# Check Prometheus targets
http://localhost:9090/targets

# Restart Prometheus
docker-compose restart prometheus
```

---

### Problem: Grafana dashboard is blank

**Solution:**
1. Go to **Configuration** → **Data Sources**
2. Click **Prometheus**
3. Click **Save & Test**
4. Should show: "Data source is working"

If not, check Prometheus is running:
```bash
curl http://localhost:9090/api/v1/status/config
```

---

## 📈 Next Steps

### 1. Customize Dashboards

- Modify `monitoring/grafana/dashboards/creptoai-dashboard.json`
- Or create new dashboards in Grafana UI
- Export and save to the dashboards folder

### 2. Add More Alerts

Edit `monitoring/alerting/creptoai-alert-rules.yml`:

```yaml
- alert: CustomAlert
  expr: your_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom alert description"
```

### 3. Configure Slack Notifications

Uncomment in `alerting/alertmanager.yml`:

```yaml
slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: 'Alert: {{ .GroupLabels.alertname }}'
```

---

## 📁 Folder Structure

```
monitoring/
├── docker-compose.yml          # Main config
├── start-monitoring.bat        # Start script (Windows)
├── stop-monitoring.bat         # Stop script (Windows)
├── README.md                   # Full documentation
├── QUICK_START_GUIDE.md        # This file
│
├── prometheus/
│   └── prometheus.yml          # Prometheus config
│
├── grafana/
│   ├── dashboards/
│   │   └── creptoai-dashboard.json
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml
│       └── dashboards/
│           └── default.yml
│
├── alerting/
│   ├── creptoai-alert-rules.yml
│   └── alertmanager.yml
│
└── scripts/
    └── verify-monitoring.sh    # Verification script
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] All services running (`docker-compose ps`)
- [ ] Prometheus targets UP (http://localhost:9090/targets)
- [ ] Grafana login works (admin/admin123)
- [ ] Dashboard displays data
- [ ] Backend metrics endpoint works (http://localhost:8000/metrics)
- [ ] Alerts configured (http://localhost:9090/alerts)

---

## 🎉 You're Done!

Your monitoring system is now running and tracking:

✅ **System Metrics** - CPU, Memory, Disk  
✅ **Container Metrics** - Docker stats  
✅ **Application Metrics** - HTTP requests, errors  
✅ **Custom Metrics** - Your business logic  
✅ **Alerts** - Get notified of issues  

**View your dashboards:**  
http://localhost:3000 (admin/admin123)

---

**Need help?** Check the full README.md for detailed documentation.

---

*Quick Start Guide - v1.0*  
*Last Updated: 2025-10-15*
