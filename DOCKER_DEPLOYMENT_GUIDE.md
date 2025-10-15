# 🐳 Crepto AI - Docker Deployment Guide

**Updated:** 2025-10-15  
**Status:** ✅ All Dockerfiles Updated with Enhanced Proxy & API Keys

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Files Updated](#files-updated)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed (Windows/Mac/Linux)
- Docker Compose v2.0+
- At least 4GB RAM available
- Ports available: 80, 3001, 3002, 5432, 6379, 8000, 8080, 9090

### Step 1: Configure Environment

```bash
# Copy the Docker environment file
cp .env.docker .env

# Edit .env and update:
# - POSTGRES_PASSWORD (change from default)
# - SECRET_KEY (generate a secure key)
# - GF_SECURITY_ADMIN_PASSWORD (Grafana password)
```

### Step 2: Build and Start

```bash
# Build all services
docker-compose -f docker-compose.enhanced.yml build

# Start all services
docker-compose -f docker-compose.enhanced.yml up -d

# Check status
docker-compose -f docker-compose.enhanced.yml ps
```

### Step 3: Verify

```bash
# Check proxy health
curl http://localhost:3002/health

# Check backend health
curl http://localhost:8000/health

# Open browser
http://localhost:80
```

---

## 📁 Files Updated

### New Files Created:

1. ✅ **`Dockerfile.proxy`**
   - Node.js Alpine image
   - Enhanced proxy server with auto-fallback
   - Health checks enabled
   - Non-root user for security

2. ✅ **`Dockerfile.frontend.enhanced`**
   - Multi-stage build (Node + Nginx)
   - Production-optimized React build
   - Environment variables support
   - Gzip compression

3. ✅ **`docker-compose.enhanced.yml`**
   - All services configured
   - Proxy server added
   - Updated API keys from api.txt
   - Health checks for all services
   - Logging configuration

4. ✅ **`.env.docker`**
   - All API keys configured
   - Database credentials
   - Service URLs
   - Production-ready defaults

5. ✅ **`nginx/docker.conf`**
   - Reverse proxy configuration
   - CORS headers
   - Load balancing
   - Security headers

6. ✅ **`DOCKER_DEPLOYMENT_GUIDE.md`** (this file)
   - Complete deployment guide
   - Troubleshooting tips
   - Best practices

### Updated Files:

1. ✅ **`Dockerfile.backend`** (verified, already good)
2. ✅ **`Dockerfile.frontend`** (original kept, new enhanced version added)
3. ✅ **`docker-compose.yml`** (original kept, new enhanced version added)

---

## 🏗️ Architecture

### Service Architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Internet / User                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Nginx Reverse Proxy (Port 8080)            │
│            Routes: /, /api/, /grafana/, /prometheus/    │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
         ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Frontend   │ │    Backend   │ │  Proxy Server│
│   (Port 80)  │ │  (Port 8000) │ │  (Port 3002) │
│              │ │              │ │              │
│ React + Nginx│ │ FastAPI      │ │ Node.js      │
│              │ │              │ │ Auto-Fallback│
└──────────────┘ └──────┬───────┘ └──────┬───────┘
                        │                │
                  ┌─────┴────────┬───────┴────────┐
                  ↓              ↓                ↓
           ┌──────────┐   ┌──────────┐   ┌──────────────┐
           │PostgreSQL│   │  Redis   │   │External APIs │
           │          │   │          │   │              │
           │Port 5432 │   │Port 6379 │   │CoinMarketCap │
           └──────────┘   └──────────┘   │CoinGecko     │
                                          │NewsAPI       │
                                          │etc.          │
                                          └──────────────┘
```

### Docker Network:

All services communicate via internal Docker network `crepto_network` (172.25.0.0/16)

---

## ⚙️ Configuration

### Environment Variables (.env.docker)

#### Required (Must Change):

```env
# Database
POSTGRES_PASSWORD=your_secure_password_here   # CHANGE THIS!
SECRET_KEY=your_secret_key_here               # CHANGE THIS!

# Monitoring
GF_SECURITY_ADMIN_PASSWORD=admin123           # CHANGE THIS!
```

#### API Keys (Already Configured):

```env
# Market Data
CMC_API_KEY=b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c
CMC_API_KEY_2=04cf4b5b-9868-465c-8ba0-9f2e78c92eb1
CRYPTOCOMPARE_KEY=e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f

# Block Explorers
ETHERSCAN_KEY=SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2
BSCSCAN_KEY=K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT
TRONSCAN_KEY=7ae72726-bffe-4e74-9c33-97b761eeea21

# News (UPDATED)
NEWSAPI_KEY=968a5e25552b4cb5ba3280361d8444ab
```

#### Optional:

```env
# Add if you have these API keys
SANTIMENT_KEY=
LUNARCRUSH_KEY=
WHALEALERT_KEY=
```

---

## 🚀 Deployment

### Development Deployment:

```bash
# Start services
docker-compose -f docker-compose.enhanced.yml up -d

# Watch logs
docker-compose -f docker-compose.enhanced.yml logs -f

# Stop services
docker-compose -f docker-compose.enhanced.yml down
```

### Production Deployment:

```bash
# Build with production settings
docker-compose -f docker-compose.enhanced.yml build --no-cache

# Start in production mode
docker-compose -f docker-compose.enhanced.yml up -d --remove-orphans

# Enable auto-restart
docker-compose -f docker-compose.enhanced.yml up -d --restart unless-stopped
```

### Scaling:

```bash
# Scale backend instances
docker-compose -f docker-compose.enhanced.yml up -d --scale backend=3

# Scale proxy instances
docker-compose -f docker-compose.enhanced.yml up -d --scale proxy=2
```

---

## 📊 Service Ports

| Service    | Internal Port | External Port | URL                        |
|------------|---------------|---------------|----------------------------|
| Frontend   | 80            | 80            | http://localhost:80        |
| Backend    | 8000          | 8000          | http://localhost:8000      |
| Proxy      | 3002          | 3002          | http://localhost:3002      |
| Nginx      | 80            | 8080          | http://localhost:8080      |
| PostgreSQL | 5432          | 5432          | localhost:5432             |
| Redis      | 6379          | 6379          | localhost:6379             |
| Grafana    | 3000          | 3001          | http://localhost:3001      |
| Prometheus | 9090          | 9090          | http://localhost:9090      |

---

## 📈 Monitoring

### Access Monitoring Tools:

1. **Grafana Dashboard:**
   - URL: http://localhost:3001
   - Username: `admin`
   - Password: (set in .env as GF_SECURITY_ADMIN_PASSWORD)

2. **Prometheus:**
   - URL: http://localhost:9090
   - No authentication (internal use)

3. **Application Logs:**
   ```bash
   # View all logs
   docker-compose -f docker-compose.enhanced.yml logs

   # View specific service
   docker-compose -f docker-compose.enhanced.yml logs proxy

   # Follow logs
   docker-compose -f docker-compose.enhanced.yml logs -f backend
   ```

---

## 🔧 Common Commands

### Service Management:

```bash
# Start all services
docker-compose -f docker-compose.enhanced.yml up -d

# Stop all services
docker-compose -f docker-compose.enhanced.yml down

# Restart a specific service
docker-compose -f docker-compose.enhanced.yml restart proxy

# Rebuild a service
docker-compose -f docker-compose.enhanced.yml up -d --build proxy

# View service status
docker-compose -f docker-compose.enhanced.yml ps

# View service logs
docker-compose -f docker-compose.enhanced.yml logs -f
```

### Database Management:

```bash
# Access PostgreSQL
docker exec -it crepto_postgres psql -U postgres -d crepto_ai_db

# Backup database
docker exec crepto_postgres pg_dump -U postgres crepto_ai_db > backup.sql

# Restore database
docker exec -i crepto_postgres psql -U postgres crepto_ai_db < backup.sql
```

### Redis Management:

```bash
# Access Redis CLI
docker exec -it crepto_redis redis-cli -a redis123

# Monitor Redis
docker exec -it crepto_redis redis-cli -a redis123 monitor

# Check keys
docker exec -it crepto_redis redis-cli -a redis123 keys '*'
```

---

## 🐛 Troubleshooting

### Issue 1: Services Not Starting

**Problem:** Services fail to start or exit immediately

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.enhanced.yml logs

# Check specific service
docker-compose -f docker-compose.enhanced.yml logs proxy

# Rebuild from scratch
docker-compose -f docker-compose.enhanced.yml down -v
docker-compose -f docker-compose.enhanced.yml build --no-cache
docker-compose -f docker-compose.enhanced.yml up -d
```

### Issue 2: Port Already in Use

**Problem:** `bind: address already in use`

**Solution:**
```bash
# Find process using the port (Windows)
netstat -ano | findstr :3002

# Find process using the port (Linux/Mac)
lsof -i :3002

# Kill the process or change port in docker-compose
```

### Issue 3: Proxy API Calls Failing

**Problem:** API calls returning errors

**Solution:**
```bash
# Check proxy logs
docker-compose -f docker-compose.enhanced.yml logs proxy

# Test proxy health
curl http://localhost:3002/health

# Test API endpoint
curl http://localhost:3002/api/feargreed

# Verify API keys in .env
cat .env | grep API_KEY
```

### Issue 4: Database Connection Failed

**Problem:** Backend can't connect to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is healthy
docker-compose -f docker-compose.enhanced.yml ps postgres

# Check PostgreSQL logs
docker-compose -f docker-compose.enhanced.yml logs postgres

# Verify DATABASE_URL in .env matches PostgreSQL settings
```

### Issue 5: Frontend Not Loading

**Problem:** Browser shows blank page or errors

**Solution:**
```bash
# Check frontend logs
docker-compose -f docker-compose.enhanced.yml logs frontend

# Rebuild frontend
docker-compose -f docker-compose.enhanced.yml build --no-cache frontend
docker-compose -f docker-compose.enhanced.yml up -d frontend

# Check nginx logs
docker-compose -f docker-compose.enhanced.yml logs nginx
```

---

## 🔒 Security Best Practices

### Before Production:

1. ✅ Change all default passwords in `.env`
2. ✅ Generate secure `SECRET_KEY`
3. ✅ Use HTTPS (add SSL certificates)
4. ✅ Enable firewall rules
5. ✅ Limit exposed ports
6. ✅ Use Docker secrets for sensitive data
7. ✅ Enable log rotation
8. ✅ Set up automated backups

### SSL/HTTPS Setup:

```bash
# Add SSL certificates to nginx/certs/
# Update nginx/docker.conf to use SSL

# Restart nginx
docker-compose -f docker-compose.enhanced.yml restart nginx
```

---

## 📦 Volume Management

### Backup Volumes:

```bash
# Backup PostgreSQL data
docker run --rm -v crepto_ai_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data

# Backup Redis data
docker run --rm -v crepto_ai_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data
```

### Restore Volumes:

```bash
# Restore PostgreSQL data
docker run --rm -v crepto_ai_postgres_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/postgres-backup.tar.gz --strip 1"
```

### Clean Up:

```bash
# Remove all containers and volumes
docker-compose -f docker-compose.enhanced.yml down -v

# Remove all images
docker-compose -f docker-compose.enhanced.yml down --rmi all

# Clean Docker system
docker system prune -a
```

---

## 🎯 Health Checks

All services have health checks configured:

```bash
# Check all service health
docker-compose -f docker-compose.enhanced.yml ps

# Healthy services show: (healthy)
# Unhealthy services show: (unhealthy)
```

### Manual Health Check URLs:

- Proxy: http://localhost:3002/health
- Backend: http://localhost:8000/health
- Frontend: http://localhost:80/
- Nginx: http://localhost:8080/health

---

## 🚀 CI/CD Integration

### GitHub Actions Example:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and Deploy
        run: |
          docker-compose -f docker-compose.enhanced.yml build
          docker-compose -f docker-compose.enhanced.yml up -d
```

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ All services show `(healthy)` status
2. ✅ Frontend accessible at http://localhost:80
3. ✅ No CORS errors in browser console
4. ✅ API calls returning data successfully
5. ✅ Grafana dashboard accessible
6. ✅ Database accepting connections
7. ✅ Logs showing no errors

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose -f docker-compose.enhanced.yml logs`
2. Verify .env configuration
3. Check port availability
4. Review this troubleshooting guide
5. Rebuild from scratch if needed

---

**Status:** ✅ All Docker files updated and ready for deployment!

---

*Last Updated: 2025-10-15*  
*Docker Compose Version: 3.8*  
*All API Keys: Configured*  
*Auto-Fallback: Enabled*
