# Deployment Guide - Bolt AI Crypto

Complete guide for deploying Bolt AI Crypto to a self-hosted VPS.

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 22.04 LTS or similar
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: 2+ cores
- **Storage**: 50GB+ SSD
- **Network**: Static IP address

### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- Git
- OpenSSL

## Initial Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

### 3. Configure Firewall
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 4. Create Application User
```bash
sudo adduser bolt
sudo usermod -aG docker bolt
sudo su - bolt
```

## Application Deployment

### 1. Clone Repository
```bash
cd /home/bolt
git clone https://github.com/yourusername/bolt-ai-crypto.git
cd bolt-ai-crypto
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.production .env

# Generate secret key
openssl rand -hex 32

# Edit environment file
nano .env
```

**Required Environment Variables:**
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=bolt_ai_crypto

# Backend
SECRET_KEY=<generated-secret-key>
ENVIRONMENT=production
DEBUG=False

# API URLs
VITE_API_URL=https://yourdomain.com/api

# Grafana
GRAFANA_PASSWORD=<admin-password>
```

### 3. SSL Certificate (Let's Encrypt)

#### Option A: Using Certbot
```bash
# Install Certbot
sudo apt install certbot -y

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chown -R bolt:bolt nginx/ssl/
```

#### Option B: Self-Signed (Development Only)
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem
```

### 4. Update Nginx Configuration
Edit `nginx/nginx.conf` and uncomment the HTTPS server block. Update `server_name` with your domain.

### 5. Deploy Application
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run deployment
./scripts/deploy.sh production
```

### 6. Verify Deployment
```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs -f backend

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:3000
```

## Post-Deployment

### 1. Create Admin User
```bash
# Access backend container
docker exec -it bolt_backend bash

# Run Python shell
python

# Create admin user
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
            password="ChangeThisPassword123!",
            full_name="Administrator",
            role=UserRole.ADMIN
        )
        print(f"Admin user created: {user.email}")

asyncio.run(create_admin())
exit()
```

### 2. Configure Automated Backups
```bash
# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/bolt/bolt-ai-crypto/scripts/backup.sh >> /home/bolt/backups/backup.log 2>&1
```

### 3. Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/bolt-ai-crypto
```

Add:
```
/home/bolt/bolt-ai-crypto/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 bolt bolt
    sharedscripts
}
```

### 4. Configure SSL Auto-Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab
sudo crontab -e

# Add renewal check twice daily
0 0,12 * * * certbot renew --quiet --deploy-hook "docker-compose -f /home/bolt/bolt-ai-crypto/docker-compose.yml restart nginx"
```

## Monitoring

### Access Monitoring Dashboards
- **Grafana**: https://yourdomain.com:3001
  - Username: admin
  - Password: (from .env GRAFANA_PASSWORD)

- **Prometheus**: https://yourdomain.com:9090

### Setup Alerts
Configure Grafana alerts for:
- High API error rate (> 5%)
- Database connection failures
- High memory usage (> 80%)
- Disk space low (< 10%)

## Maintenance

### Update Application
```bash
cd /home/bolt/bolt-ai-crypto
git pull origin main
./scripts/deploy.sh production
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Database Backup
```bash
# Manual backup
./scripts/backup.sh

# Restore from backup
./scripts/rollback.sh
```

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Check database connection
docker exec -it bolt_postgres psql -U postgres -d bolt_ai_crypto

# Verify environment variables
docker exec -it bolt_backend env | grep DATABASE_URL
```

### Database Migration Issues
```bash
# Check migration status
docker exec -it bolt_backend alembic current

# Run migrations manually
docker exec -it bolt_backend alembic upgrade head

# Rollback migration
docker exec -it bolt_backend alembic downgrade -1
```

### High Memory Usage
```bash
# Check container stats
docker stats

# Restart heavy services
docker-compose restart backend redis
```

### SSL Certificate Issues
```bash
# Check certificate expiry
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates

# Renew certificate
sudo certbot renew --force-renewal
```

## Security Checklist

- [ ] Changed all default passwords
- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (only ports 22, 80, 443 open)
- [ ] SSH key-based authentication enabled
- [ ] Database backups automated
- [ ] Monitoring and alerts configured
- [ ] Log rotation configured
- [ ] Environment variables secured
- [ ] Admin user created with strong password
- [ ] Rate limiting enabled

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation in `docs/`
- Check GitHub issues

## Next Steps

1. Configure Telegram bot for alerts (see `docs/TELEGRAM_SETUP.md`)
2. Setup email notifications (see `docs/EMAIL_SETUP.md`)
3. Customize Grafana dashboards
4. Configure backup retention policy
5. Setup monitoring alerts

