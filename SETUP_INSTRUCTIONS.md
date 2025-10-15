# 🚀 Complete Setup Instructions

## Current Status

The project has been enhanced with:
- ✅ Feature flag system (fully functional)
- ✅ Testing infrastructure (configured)
- ✅ Docker setup (ready)
- ⚠️ Testing dependencies need to be installed

## 📝 Step-by-Step Setup

### Step 1: Install Core Dependencies

```bash
cd /mnt/c/project/Crepto_Ai

# Install existing dependencies
npm install --ignore-scripts
```

### Step 2: Install Testing Dependencies

Due to the current setup, you have two options:

#### Option A: Manual Installation (Recommended for immediate use)
```bash
npm install --save-dev \
  vitest@^1.0.4 \
  @vitest/ui@^1.0.4 \
  @vitest/coverage-v8@^1.0.4 \
  @testing-library/react@^14.1.2 \
  @testing-library/jest-dom@^6.1.4 \
  @testing-library/user-event@^14.5.1 \
  @playwright/test@^1.40.0 \
  @types/jest@^29.5.8 \
  jsdom@^23.0.1 \
  msw@^2.0.8 \
  happy-dom@^12.10.3
```

#### Option B: Update package.json (Recommended for long-term)

The package.json already has the testing scripts configured, but needs the devDependencies added.
The dependencies are documented in the file but may need manual addition due to the existing configuration.

### Step 3: Run Tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run with UI
npm run test:ui
```

### Step 4: Build Docker Images

```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build backend
docker-compose build frontend
```

### Step 5: Start Docker Containers

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Verify Setup

#### A. Check Services
```bash
# Check container health
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

#### B. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin123)

#### C. Test Feature Flags
1. Open http://localhost:3000
2. Click the settings button (⚙️) in bottom-right corner
3. Toggle feature flags on/off
4. Observe UI changes

## 🎯 Success Checklist

### Development Environment
- [ ] npm install completed successfully
- [ ] Testing dependencies installed
- [ ] Tests run without errors
- [ ] Test coverage > 80% (target)

### Docker Environment
- [ ] All Docker images built
- [ ] All containers running (7 services)
- [ ] All health checks passing
- [ ] No error logs in containers

### Application Functionality
- [ ] Frontend loads at http://localhost:3000
- [ ] Backend responds at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/api/docs
- [ ] Feature flags UI opens
- [ ] Feature flags can be toggled
- [ ] UI updates when flags change

### Monitoring
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards loading
- [ ] Container stats showing normal usage

## 🐛 Troubleshooting

### Issue: npm install fails with electron-builder

**Solution:**
```bash
npm install --ignore-scripts
```

### Issue: Testing dependencies not found

**Solution:**
```bash
# Manually install testing packages
npm install --save-dev vitest @vitest/ui @vitest/coverage-v8 \
  @testing-library/react @testing-library/jest-dom \
  @testing-library/user-event jsdom @playwright/test msw
```

### Issue: Docker build fails

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Issue: Port already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Stop the process or change ports in docker-compose.yml
```

### Issue: Database connection fails

**Solution:**
```bash
# Restart database
docker-compose restart postgres

# Wait for database to be ready
sleep 10

# Check database logs
docker-compose logs postgres
```

## 📊 What's Working Now

### Feature Flag System ✅
- Complete context provider implementation
- 15+ pre-configured feature flags
- Multiple wrapper components
- UI management interface
- Real-time updates
- localStorage persistence

### Testing Infrastructure ✅
- Vitest configuration file created
- Test setup with comprehensive mocks
- Test utilities and helpers
- Example unit tests
- Example integration tests

### Docker Infrastructure ✅
- Multi-service docker-compose setup
- PostgreSQL database
- Redis cache
- FastAPI backend
- React frontend
- Nginx reverse proxy
- Prometheus monitoring
- Grafana visualization

### Documentation ✅
- Complete feature flag guide
- Docker setup instructions
- Quick reference commands
- Follow-up action plan
- Project summary
- Master index

## 🔄 Alternative Quick Start (Without Tests)

If you want to skip tests and just run the application:

```bash
# 1. Install core dependencies
npm install --ignore-scripts

# 2. Build Docker
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Access application
# http://localhost:3000
```

## 📚 Documentation Guide

- **Start Here**: `INDEX.md`
- **Quick Commands**: `QUICK_REFERENCE.md`
- **Feature Flags**: `FEATURE_FLAGS.md`
- **Docker Setup**: `DOCKER_SETUP_GUIDE.md`
- **Next Steps**: `FOLLOWUP_ACTIONS.md`
- **Project Status**: `PROJECT_SUMMARY.md`

## 🆘 Need Help?

1. Check `QUICK_REFERENCE.md` for common commands
2. Review `DOCKER_SETUP_GUIDE.md` for infrastructure issues
3. See `FOLLOWUP_ACTIONS.md` for known issues
4. Check container logs: `docker-compose logs -f`
5. Verify services: `docker-compose ps`

## ✅ Final Verification

Once everything is running, verify:

```bash
# 1. Check Docker
docker-compose ps
# All services should show "Up" and "healthy"

# 2. Test backend
curl http://localhost:8000/health
# Should return: {"status":"ok"}

# 3. Test frontend
curl http://localhost:3000
# Should return HTML

# 4. Check logs
docker-compose logs --tail=50
# Should show no errors

# 5. Open browser
# Navigate to http://localhost:3000
# Application should load with all features
```

## 🎉 You're Ready!

When all checks pass:
- ✅ Open http://localhost:3000
- ✅ Explore the feature flag system
- ✅ Toggle features in settings
- ✅ Test AI predictions
- ✅ Check portfolio management
- ✅ Review monitoring dashboards

---

**For detailed information, see:**
- Full setup: `DOCKER_SETUP_GUIDE.md`
- Feature details: `FEATURE_FLAGS.md`
- Commands: `QUICK_REFERENCE.md`