# Operations Runbook - Bolt AI Crypto

Quick reference guide for common operational tasks and troubleshooting.

## Quick Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Check service status
docker-compose ps
```

### Deployment
```bash
# Deploy to production
./scripts/deploy.sh production

# Create backup
./scripts/backup.sh

# Rollback deployment
./scripts/rollback.sh
```

---

## Common Issues

### 1. Backend Won't Start

**Symptoms:**
- Container exits immediately
- Health check fails
- Database connection errors

**Diagnosis:**
```bash
# Check logs
docker-compose logs backend

# Check environment
docker exec -it bolt_backend env | grep -E "DATABASE|REDIS|SECRET"

# Test database connection
docker exec -it bolt_postgres psql -U postgres -d bolt_ai_crypto -c "SELECT 1"
```

**Solutions:**
```bash
# Fix database connection
docker-compose restart postgres
docker-compose restart backend

# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose run --rm backend alembic upgrade head
docker-compose up -d
```

---

### 2. High Memory Usage

**Symptoms:**
- System slowdown
- OOM (Out of Memory) errors
- Container restarts

**Diagnosis:**
```bash
# Check memory usage
docker stats

# Check system memory
free -h

# Check logs for memory errors
dmesg | grep -i "out of memory"
```

**Solutions:**
```bash
# Restart memory-intensive services
docker-compose restart backend redis

# Clear Redis cache
docker exec -it bolt_redis redis-cli FLUSHALL

# Increase swap space (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### 3. Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- Slow API responses
- Connection timeouts

**Diagnosis:**
```bash
# Check active connections
docker exec -it bolt_postgres psql -U postgres -c \
  "SELECT count(*) FROM pg_stat_activity"

# Check connection details
docker exec -it bolt_postgres psql -U postgres -c \
  "SELECT * FROM pg_stat_activity WHERE datname='bolt_ai_crypto'"
```

**Solutions:**
```bash
# Kill idle connections
docker exec -it bolt_postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
   WHERE datname='bolt_ai_crypto' AND state='idle' 
   AND state_change < NOW() - INTERVAL '5 minutes'"

# Restart backend to reset pool
docker-compose restart backend
```

---

### 4. Redis Connection Issues

**Symptoms:**
- Cache misses
- Slow responses
- Connection refused errors

**Diagnosis:**
```bash
# Check Redis status
docker exec -it bolt_redis redis-cli ping

# Check memory usage
docker exec -it bolt_redis redis-cli INFO memory

# Check connected clients
docker exec -it bolt_redis redis-cli CLIENT LIST
```

**Solutions:**
```bash
# Restart Redis
docker-compose restart redis

# Clear cache
docker exec -it bolt_redis redis-cli FLUSHALL

# Check persistence
docker exec -it bolt_redis redis-cli LASTSAVE
```

---

### 5. SSL Certificate Expired

**Symptoms:**
- Browser security warnings
- HTTPS connection failures
- Certificate expiry errors

**Diagnosis:**
```bash
# Check certificate expiry
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates

# Check certificate details
openssl x509 -in nginx/ssl/fullchain.pem -noout -text
```

**Solutions:**
```bash
# Renew with Certbot
sudo certbot renew --force-renewal

# Copy new certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Restart Nginx
docker-compose restart nginx
```

---

### 6. Disk Space Full

**Symptoms:**
- Write errors
- Container failures
- Database errors

**Diagnosis:**
```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Find large files
du -sh /* | sort -rh | head -10
```

**Solutions:**
```bash
# Clean Docker resources
docker system prune -a --volumes

# Clean old logs
find backend/logs -name "*.log" -mtime +30 -delete
find nginx/logs -name "*.log" -mtime +30 -delete

# Clean old backups
find backups -name "*.sql.gz" -mtime +30 -delete
```

---

### 7. High API Latency

**Symptoms:**
- Slow response times
- Timeouts
- Poor user experience

**Diagnosis:**
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Check database query times
docker exec -it bolt_postgres psql -U postgres -d bolt_ai_crypto -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC LIMIT 10"

# Check Redis latency
docker exec -it bolt_redis redis-cli --latency
```

**Solutions:**
```bash
# Restart services
docker-compose restart backend redis

# Check for slow queries
# Add indexes if needed

# Increase cache TTL in backend/config.py
```

---

### 8. Model Training Failures

**Symptoms:**
- Training doesn't start
- Training stops unexpectedly
- Poor model performance

**Diagnosis:**
```bash
# Check training logs
docker-compose logs backend | grep -i "training"

# Check model metrics in database
docker exec -it bolt_postgres psql -U postgres -d bolt_ai_crypto -c \
  "SELECT * FROM model_metrics ORDER BY created_at DESC LIMIT 10"

# Check available memory
docker stats bolt_backend
```

**Solutions:**
```bash
# Stop current training
curl -X POST http://localhost:8000/api/predictions/train/stop \
  -H "Authorization: Bearer <admin_token>"

# Clear old model files
docker exec -it bolt_backend rm -rf /app/models/*

# Restart training with fewer epochs
curl -X POST http://localhost:8000/api/predictions/train \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"epochs": 20, "symbols": ["BTC", "ETH"]}'
```

---

## Monitoring Alerts

### Setup Alert Rules

**High Error Rate (> 5%)**
```yaml
# monitoring/alerts/high_error_rate.yml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High error rate detected"
```

**Database Connection Failures**
```yaml
- alert: DatabaseDown
  expr: up{job="postgres"} == 0
  for: 1m
  annotations:
    summary: "Database is down"
```

**High Memory Usage**
```yaml
- alert: HighMemoryUsage
  expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.8
  for: 5m
  annotations:
    summary: "Memory usage above 80%"
```

---

## Performance Tuning

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_predictions_symbol ON prediction_logs(symbol, predicted_at);
CREATE INDEX idx_alerts_user_status ON alerts(user_id, status);

-- Analyze tables
ANALYZE users;
ANALYZE prediction_logs;
ANALYZE alerts;

-- Vacuum database
VACUUM ANALYZE;
```

### Redis Optimization
```bash
# Set maxmemory policy
docker exec -it bolt_redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Set maxmemory limit (2GB)
docker exec -it bolt_redis redis-cli CONFIG SET maxmemory 2gb
```

### Backend Optimization
```python
# Increase worker count in docker-compose.yml
command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]

# Adjust database pool size in backend/config.py
DATABASE_POOL_SIZE = 40
DATABASE_MAX_OVERFLOW = 20
```

---

## Backup & Recovery

### Manual Backup
```bash
# Full backup
./scripts/backup.sh

# Database only
docker exec bolt_postgres pg_dump -U postgres bolt_ai_crypto | gzip > backup.sql.gz
```

### Restore from Backup
```bash
# Full restore
./scripts/rollback.sh

# Database only
gunzip -c backup.sql.gz | docker exec -i bolt_postgres psql -U postgres bolt_ai_crypto
```

---

## Security Checklist

### Regular Security Tasks
- [ ] Review access logs weekly
- [ ] Update dependencies monthly
- [ ] Rotate secrets quarterly
- [ ] Review user permissions monthly
- [ ] Check for security updates weekly
- [ ] Audit database access monthly
- [ ] Review firewall rules quarterly

### Security Commands
```bash
# Check for failed login attempts
docker-compose logs backend | grep "401\|403" | tail -50

# List active users
docker exec -it bolt_postgres psql -U postgres -d bolt_ai_crypto -c \
  "SELECT username, last_login FROM users WHERE is_active=true"

# Check open ports
sudo netstat -tulpn | grep LISTEN
```

---

## Emergency Procedures

### Complete System Failure
1. Stop all services: `docker-compose down`
2. Check disk space: `df -h`
3. Check system logs: `sudo journalctl -xe`
4. Restore from backup: `./scripts/rollback.sh`
5. Start services: `docker-compose up -d`

### Data Corruption
1. Stop affected service
2. Restore from latest backup
3. Run database integrity checks
4. Restart services
5. Verify data integrity

### Security Breach
1. Immediately stop all services
2. Change all passwords and secrets
3. Review access logs
4. Restore from clean backup
5. Update all dependencies
6. Re-deploy with new credentials

---

## Contact & Escalation

### Support Levels
- **L1**: Basic troubleshooting, restart services
- **L2**: Database issues, performance tuning
- **L3**: Security incidents, architecture changes

### On-Call Procedures
1. Check monitoring dashboards
2. Review recent logs
3. Attempt standard fixes
4. Escalate if unresolved in 30 minutes
5. Document incident in runbook

