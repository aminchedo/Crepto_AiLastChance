@echo off
title Crepto AI - Docker Deployment
color 0A

echo.
echo ====================================================
echo       CREPTO AI - DOCKER DEPLOYMENT
echo ====================================================
echo.

:: Check if Docker is installed
echo [1/6] Checking Docker...
docker --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Docker is not installed!
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo OK - Docker found
echo.

:: Check if Docker is running
echo [2/6] Checking if Docker is running...
docker ps > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Docker is not running!
    echo.
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo OK - Docker is running
echo.

:: Check if .env file exists
echo [3/6] Checking environment file...
if not exist ".env" (
    echo Creating .env from .env.docker...
    copy .env.docker .env
    echo.
    echo IMPORTANT: Please edit .env and update:
    echo   - POSTGRES_PASSWORD
    echo   - SECRET_KEY
    echo   - GF_SECURITY_ADMIN_PASSWORD
    echo.
    echo Press any key to continue after editing .env...
    pause > nul
)
echo OK - .env file exists
echo.

:: Stop existing containers
echo [4/6] Stopping existing containers...
docker-compose -f docker-compose.enhanced.yml down > nul 2>&1
echo OK - Old containers stopped
echo.

:: Build images
echo [5/6] Building Docker images...
echo This may take 5-10 minutes on first run...
docker-compose -f docker-compose.enhanced.yml build
if errorlevel 1 (
    color 0C
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo OK - Images built successfully
echo.

:: Start services
echo [6/6] Starting services...
docker-compose -f docker-compose.enhanced.yml up -d
if errorlevel 1 (
    color 0C
    echo ERROR: Failed to start services!
    pause
    exit /b 1
)
echo OK - Services starting...
echo.

:: Wait for services to be ready
echo Waiting for services to be healthy...
timeout /t 15 /nobreak > nul

:: Check service status
echo.
echo ====================================================
echo         SERVICE STATUS
echo ====================================================
echo.
docker-compose -f docker-compose.enhanced.yml ps
echo.

:: Display URLs
echo ====================================================
echo         ACCESS URLS
echo ====================================================
echo.
echo Frontend:        http://localhost:80
echo Nginx Proxy:     http://localhost:8080
echo Backend API:     http://localhost:8000
echo Proxy Server:    http://localhost:3002
echo Grafana:         http://localhost:3001
echo Prometheus:      http://localhost:9090
echo.
echo ====================================================
echo         CREDENTIALS
echo ====================================================
echo.
echo Grafana:
echo   Username: admin
echo   Password: (check .env - GF_SECURITY_ADMIN_PASSWORD)
echo.
echo PostgreSQL:
echo   Host: localhost:5432
echo   Database: crepto_ai_db
echo   Username: postgres
echo   Password: (check .env - POSTGRES_PASSWORD)
echo.
echo ====================================================

:: Health checks
echo.
echo Checking service health...
echo.

curl -s http://localhost:3002/health > nul 2>&1
if errorlevel 1 (
    echo [WARN] Proxy not responding yet
) else (
    echo [OK] Proxy Server is healthy
)

curl -s http://localhost:8000/health > nul 2>&1
if errorlevel 1 (
    echo [WARN] Backend not responding yet
) else (
    echo [OK] Backend is healthy
)

curl -s http://localhost:80 > nul 2>&1
if errorlevel 1 (
    echo [WARN] Frontend not responding yet
) else (
    echo [OK] Frontend is healthy
)

echo.
echo ====================================================
echo.
echo DEPLOYMENT COMPLETE!
echo.
echo View logs:
echo   docker-compose -f docker-compose.enhanced.yml logs -f
echo.
echo Stop services:
echo   docker-compose -f docker-compose.enhanced.yml down
echo.
echo Opening browser...
timeout /t 3 /nobreak > nul
start http://localhost:80

echo.
echo Press any key to exit...
pause > nul
