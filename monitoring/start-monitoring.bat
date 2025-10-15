@echo off
title Crepto AI - Monitoring Stack
color 0B

echo.
echo ====================================================
echo     CREPTO AI - MONITORING STACK LAUNCHER
echo ====================================================
echo.
echo Starting Prometheus + Grafana + Alertmanager...
echo.

:: Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

:: Navigate to monitoring directory
cd /d "%~dp0"

:: Stop existing containers
echo Stopping old containers...
docker-compose down 2>nul

:: Start monitoring stack
echo.
echo Starting monitoring services...
docker-compose up -d

if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: Failed to start monitoring stack!
    pause
    exit /b 1
)

:: Wait for services to start
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

:: Check service status
echo.
echo ====================================================
echo         MONITORING SERVICES STATUS
echo ====================================================
echo.
docker-compose ps

:: Display access URLs
echo.
echo ====================================================
echo         ACCESS URLS
echo ====================================================
echo.
echo Prometheus:      http://localhost:9090
echo Grafana:         http://localhost:3000
echo Alertmanager:    http://localhost:9093
echo Node Exporter:   http://localhost:9100
echo cAdvisor:        http://localhost:8080
echo.
echo ====================================================
echo         CREDENTIALS
echo ====================================================
echo.
echo Grafana:
echo   Username: admin
echo   Password: admin123
echo.
echo ====================================================
echo.
echo Monitoring stack is running!
echo.
echo View logs:
echo   docker-compose logs -f
echo.
echo Stop monitoring:
echo   docker-compose down
echo.
echo Opening Grafana dashboard...
timeout /t 3 /nobreak > nul
start http://localhost:3000

echo.
echo Press any key to exit (services will continue running)...
pause > nul
