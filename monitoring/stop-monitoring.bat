@echo off
title Crepto AI - Stop Monitoring
color 0C

echo.
echo ====================================================
echo     STOPPING CREPTO AI MONITORING STACK
echo ====================================================
echo.

cd /d "%~dp0"

echo Stopping all monitoring containers...
docker-compose down

if errorlevel 1 (
    echo.
    echo ERROR: Failed to stop services
    pause
    exit /b 1
)

echo.
echo ====================================================
echo     ALL MONITORING SERVICES STOPPED
echo ====================================================
echo.
echo To remove volumes as well (WARNING: deletes metrics data):
echo   docker-compose down -v
echo.
echo To start again:
echo   start-monitoring.bat
echo.
pause
