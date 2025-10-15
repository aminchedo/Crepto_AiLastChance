# 🚀 Quick Start Guide - Bolt AI Crypto

Get your AI-powered crypto trading dashboard running in **5 minutes**!

## Prerequisites Check

```bash
# Check Docker
docker --version  # Need 24.0+

# Check Docker Compose
docker compose version  # Need 2.20+

# Check Git
git --version
```

## Step 1: Setup (2 minutes)

```bash
# Clone repository
git clone <your-repo-url>
cd bolt-ai-crypto

# Copy environment file
cp .env.production .env

# Generate secret key
openssl rand -hex 32
# Copy the output
```

## Step 2: Configure (1 minute)

Edit `.env` file:

```bash
nano .env
```

**Minimum required changes:**
```env
SECRET_KEY=<paste-your-generated-key-here>
POSTGRES_PASSWORD=YourStrongPassword123!
GRAFANA_PASSWORD=admin123
```

Save and exit (Ctrl+X, Y, Enter)

## Step 3: Deploy (2 minutes)

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy everything
./scripts/deploy.sh production
```

**Wait for the deployment to complete** (~60-90 seconds)

## Step 4: Access & Test

### Open in Browser
- **🎨 Frontend**: http://localhost:3000
- **📚 API Docs**: http://localhost:8000/api/docs
- **📊 Grafana**: http://localhost:3001 (admin/admin123)

### Create First User
1. Go to http://localhost:3000
2. Click "Create one" (register)
3. Fill in:
   - Email: `admin@example.com`
   - Username: `admin`
   - Password: `Admin123!`
4. Click "Create Account"

### Test the System
1. **Login** with your new credentials
2. **Dashboard** should show live crypto prices
3. **AI Predictions** will appear in ~10 seconds
4. Click **"AI Training"** tab to see the model

## ✅ Verification Checklist

Run these commands to verify everything works:

```bash
# Check all services are running
docker compose ps
# Should show: backend, frontend, nginx, postgres, redis (all healthy)

# Test backend health
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# Test frontend
curl http://localhost:3000
# Should return: HTML content

# View logs
docker compose logs -f backend
# Should show: "Application startup complete"
```

## 🎯 Next Steps

### 1. Create Admin User (Optional)
```bash
docker exec -it bolt_backend python << 'EOF'
from db.database import AsyncSessionLocal
from services.auth_service import AuthService
from models.user import UserRole
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        user = await AuthService.create_user(
            db=db,
            email="admin@yourdomain.com",
            username="admin",
            password="ChangeThis123!",
            full_name="Administrator",
            role=UserRole.ADMIN
        )
        print(f"✅ Admin created: {user.email}")

asyncio.run(create_admin())
EOF
```

### 2. Configure SSL (Production)
```bash
# Install Certbot
sudo apt install certbot -y

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/*.pem nginx/ssl/

# Update nginx.conf (uncomment HTTPS section)
nano nginx/nginx.conf

# Restart nginx
docker compose restart nginx
```

### 3. Setup Automated Backups
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/yourusername/bolt-ai-crypto/scripts/backup.sh >> /home/yourusername/backups/backup.log 2>&1
```

### 4. Configure Monitoring Alerts

Open Grafana: http://localhost:3001

1. Login (admin/admin123)
2. Go to: Alerting → Alert rules
3. Create new alert rule:
   - **Name**: High Error Rate
   - **Query**: `rate(http_requests_total{status=~"5.."}[5m]) > 0.05`
   - **Notification**: Add email/Slack channel

## 🔧 Common Commands

### Service Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a service
docker compose restart backend

# View logs
docker compose logs -f backend

# Check status
docker compose ps
```

### Maintenance
```bash
# Create backup
./scripts/backup.sh

# Update application
git pull origin main
./scripts/deploy.sh production

# Rollback if issues
./scripts/rollback.sh
```

### Database
```bash
# Access database
docker exec -it bolt_postgres psql -U postgres -d bolt_ai_crypto

# Run migrations
docker exec -it bolt_backend alembic upgrade head

# Check migration status
docker exec -it bolt_backend alembic current
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Check database connection
docker exec -it bolt_postgres psql -U postgres -c "SELECT 1"

# Restart services
docker compose restart postgres backend
```

### Frontend shows error
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose up -d --build frontend
```

### Database connection errors
```bash
# Check environment variables
docker exec -it bolt_backend env | grep DATABASE_URL

# Reset database
docker compose down -v
docker compose up -d postgres
sleep 10
docker exec -it bolt_backend alembic upgrade head
docker compose up -d
```

### High memory usage
```bash
# Check container stats
docker stats

# Restart memory-intensive services
docker compose restart backend redis

# Clear Redis cache
docker exec -it bolt_redis redis-cli FLUSHALL
```

## 📚 Documentation

For detailed information, see:

- **[README_FULL.md](README_FULL.md)** - Complete project overview
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Full deployment guide
- **[docs/API.md](docs/API.md)** - API reference
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** - Operations runbook
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built

## 🆘 Getting Help

1. **Check logs**: `docker compose logs -f`
2. **Review docs**: See `docs/` folder
3. **Health check**: `curl http://localhost:8000/health`
4. **Test API**: http://localhost:8000/api/docs

## 🎉 Success!

If you see:
- ✅ Frontend at http://localhost:3000
- ✅ Backend health check passes
- ✅ Can login and see dashboard
- ✅ AI predictions appear

**Congratulations! Your AI-powered crypto trading dashboard is live! 🚀**

---

## Quick Reference Card

```
📱 SERVICES
Frontend:    http://localhost:3000
Backend:     http://localhost:8000
API Docs:    http://localhost:8000/api/docs
Grafana:     http://localhost:3001
Prometheus:  http://localhost:9090

🔧 COMMANDS
Deploy:      ./scripts/deploy.sh production
Backup:      ./scripts/backup.sh
Rollback:    ./scripts/rollback.sh
Logs:        docker compose logs -f [service]
Status:      docker compose ps

📂 KEY FILES
Config:      .env
Backend:     backend/main.py
Frontend:    src/App.tsx
Database:    backend/models/
Migrations:  backend/alembic/versions/

🔐 DEFAULT CREDENTIALS
Grafana:     admin / <GRAFANA_PASSWORD from .env>
Postgres:    postgres / <POSTGRES_PASSWORD from .env>
```

---

**Need help?** Check the docs or review the logs!

