# ⚡ Quick Reference - Crepto_Ai Commands

## 🚀 Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Run tests
npm run test

# 3. Build Docker
docker-compose build

# 4. Start application
docker-compose up -d

# 5. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 📦 NPM Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run preview          # Preview production build
npm run lint             # Run ESLint

# Testing
npm run test             # Run tests
npm run test:ui          # Run tests with UI
npm run test:coverage    # Run with coverage
npm run test:watch       # Watch mode
npm run test:e2e         # End-to-end tests
npm run test:e2e:ui      # E2E with UI

# Electron
npm run dev:electron     # Run as Electron app
npm run build:electron   # Build Electron app
npm run build:win        # Build for Windows
```

## 🐳 Docker Commands

```bash
# Build
docker-compose build              # Build all
docker-compose build backend      # Build one service
docker-compose build --no-cache   # Build without cache

# Run
docker-compose up                 # Start (foreground)
docker-compose up -d              # Start (background)
docker-compose up -d --build      # Build and start

# Stop
docker-compose stop               # Stop services
docker-compose down               # Stop and remove
docker-compose down -v            # Stop and remove volumes

# Logs
docker-compose logs               # All logs
docker-compose logs -f            # Follow logs
docker-compose logs backend       # Service logs

# Status
docker-compose ps                 # Container status
docker stats                      # Resource usage

# Access
docker-compose exec backend bash  # Backend shell
docker-compose exec frontend sh   # Frontend shell
docker-compose exec postgres psql # Database

# Clean
docker system prune -a            # Remove all unused
docker volume prune               # Remove volumes
docker image prune -a             # Remove images
```

## 🔧 Useful Commands

```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:3000/health

# Database
docker-compose exec postgres psql -U postgres -d bolt_ai_crypto

# Redis
docker-compose exec redis redis-cli

# Backup
docker-compose exec postgres pg_dump -U postgres bolt_ai_crypto > backup.sql

# Generate secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
openssl rand -base64 32
```

## 📊 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| Redoc | http://localhost:8000/api/redoc |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |

## 🐛 Troubleshooting

```bash
# Restart everything
docker-compose down && docker-compose up -d

# Rebuild everything
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Check logs for errors
docker-compose logs -f backend | grep ERROR

# Free up space
docker system prune -a --volumes

# Check port usage
lsof -i :8000              # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

## ✅ Quick Checks

```bash
# All systems go?
docker-compose ps
npm run test
curl http://localhost:8000/health
```

## 🔑 Environment Variables

```bash
# .env file locations
/mnt/c/project/Crepto_Ai/.env

# Key variables to set
SECRET_KEY=<generate-with-openssl>
POSTGRES_PASSWORD=<secure-password>
DEBUG=False  # for production
```

## 📝 Common Tasks

```bash
# Update code and restart
git pull
docker-compose build --no-cache
docker-compose up -d

# View real-time logs
docker-compose logs -f | grep -i error

# Run database migration
docker-compose exec backend alembic upgrade head

# Create backup
docker-compose exec postgres pg_dump -U postgres bolt_ai_crypto > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup.sql | docker-compose exec -T postgres psql -U postgres bolt_ai_crypto
```

## 🎯 Development Workflow

```bash
# 1. Start development
docker-compose up -d
npm run dev

# 2. Make changes
# Edit files...

# 3. Run tests
npm run test

# 4. Check logs
docker-compose logs -f backend

# 5. Restart if needed
docker-compose restart backend

# 6. Commit changes
git add .
git commit -m "Your message"
git push
```

## 🚨 Emergency Commands

```bash
# Stop everything immediately
docker-compose down

# Kill all Docker containers
docker kill $(docker ps -q)

# Remove everything and start fresh
docker-compose down -v
docker system prune -a --volumes
rm -rf node_modules
npm install
docker-compose build --no-cache
docker-compose up -d
```

---

**💡 Pro Tips:**
- Use `docker-compose logs -f` to debug issues
- Run `npm run test:coverage` before committing
- Keep `.env` file secure and never commit it
- Use `docker-compose restart <service>` for quick updates
- Check `FOLLOWUP_ACTIONS.md` for detailed tasks