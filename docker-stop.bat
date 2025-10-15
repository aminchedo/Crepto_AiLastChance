@echo off
title Crepto AI - Docker Stop
color 0C

echo.
echo ====================================================
echo       STOPPING CREPTO AI DOCKER SERVICES
echo ====================================================
echo.

echo Stopping all containers...
docker-compose -f docker-compose.enhanced.yml down

if errorlevel 1 (
    echo.
    echo ERROR: Failed to stop services
    pause
    exit /b 1
)

echo.
echo ====================================================
echo         ALL SERVICES STOPPED
echo ====================================================
echo.
echo To remove volumes as well (WARNING: deletes data):
echo   docker-compose -f docker-compose.enhanced.yml down -v
echo.
echo To start again:
echo   docker-start.bat
echo.
pause
