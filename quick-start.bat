@echo off
title Crepto AI - Quick Start
color 0A

echo.
echo ====================================================
echo         CREPTO AI - QUICK START
echo ====================================================
echo.
echo Checking if proxy server is running...

curl -s http://localhost:3002/health > nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Proxy server is not running!
    echo.
    echo Please start the proxy server first:
    echo   cd proxy-server
    echo   npm start
    echo.
    pause
    exit /b 1
)

echo OK - Proxy server is running on port 3002
echo.

echo Starting Backend Server...
cd backend
if exist "venv\Scripts\activate.bat" (
    start "Crepto AI Backend" cmd /k "title Crepto AI Backend && color 0B && call venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) else (
    start "Crepto AI Backend" cmd /k "title Crepto AI Backend && color 0B && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
)
cd ..

echo Waiting for backend to start...
timeout /t 8 /nobreak > nul

echo Starting Frontend Server...
start "Crepto AI Frontend" cmd /k "title Crepto AI Frontend && color 0E && npm run dev"

echo Waiting for frontend to start...
timeout /t 5 /nobreak > nul

echo.
echo ====================================================
echo         ALL SERVERS STARTED!
echo ====================================================
echo.
echo Proxy:    http://localhost:3002 (already running)
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Opening browser...
timeout /t 2 /nobreak > nul
start http://localhost:5173

echo.
echo All servers are running!
echo Press any key to exit this window...
echo (Servers will continue running in their own windows)
pause > nul
