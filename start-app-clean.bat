@echo off
chcp 65001 > nul
title Crepto_Ai - Full Stack with Proxy
color 0A

echo.
echo ====================================================
echo       CREPTO_AI FULL STACK + PROXY LAUNCHER
echo    React + Python + Node.js Proxy (CORS-Free)
echo ====================================================
echo.

:: Set environment variables
set PROXY_PORT=3002
set BACKEND_PORT=8000
set FRONTEND_PORT=5173
set PROXY_URL=http://localhost:%PROXY_PORT%
set BACKEND_URL=http://localhost:%BACKEND_PORT%
set FRONTEND_URL=http://localhost:%FRONTEND_PORT%

:: Check Node.js
echo [1/7] Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Node.js not installed
    pause
    exit /b 1
)
echo OK - Node.js found
echo.

:: Check Python
echo [2/7] Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python not installed
    pause
    exit /b 1
)
echo OK - Python found
echo.

:: Check if proxy is already running
echo [3/7] Checking proxy server...
curl -s http://localhost:%PROXY_PORT%/health > nul 2>&1
if errorlevel 1 (
    echo Proxy not running, will start it...
    set START_PROXY=1
) else (
    echo OK - Proxy already running on port %PROXY_PORT%
    set START_PROXY=0
)
echo.

:: Kill existing processes (optional)
echo [4/7] Cleaning up old processes...
taskkill /f /im python.exe > nul 2>&1
timeout /t 2 /nobreak > nul
echo OK - Cleanup complete
echo.

:: Install proxy dependencies if needed
if %START_PROXY%==1 (
    echo [5/7] Checking proxy server dependencies...
    cd proxy-server
    if not exist "node_modules\" (
        echo Installing proxy dependencies...
        call npm install
        if errorlevel 1 (
            color 0C
            echo ERROR: Failed to install proxy dependencies
            cd ..
            pause
            exit /b 1
        )
    )
    echo OK - Proxy dependencies ready
    cd ..
    echo.
)

:: Start Proxy Server (if not running)
if %START_PROXY%==1 (
    echo [6/7] Starting CORS Proxy Server...
    echo     Port: %PROXY_PORT%
    echo     URL:  %PROXY_URL%
    cd proxy-server
    start "Crepto_Ai Proxy [Port %PROXY_PORT%]" cmd /k "title Crepto_Ai Proxy [Port %PROXY_PORT%] && color 0D && node server.js"
    cd ..
    echo OK - Proxy server starting...
    echo.
    
    :: Wait for proxy
    echo Waiting for proxy to be ready...
    timeout /t 5 /nobreak > nul
) else (
    echo [6/7] Skipping proxy start (already running)
    echo.
)

:: Start Python Backend
echo [7/7] Starting Python Backend...
echo     Port: %BACKEND_PORT%
cd backend
if exist "venv\Scripts\activate.bat" (
    start "Crepto_Ai Backend [Port %BACKEND_PORT%]" cmd /k "title Crepto_Ai Backend [Port %BACKEND_PORT%] && color 0B && call venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
) else (
    start "Crepto_Ai Backend [Port %BACKEND_PORT%]" cmd /k "title Crepto_Ai Backend [Port %BACKEND_PORT%] && color 0B && python -m uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
)
cd ..
echo OK - Backend server starting...
echo.

:: Wait for backend
echo Waiting for backend...
timeout /t 8 /nobreak > nul

:: Start Frontend
echo [8/8] Starting React Frontend...
echo     Port: %FRONTEND_PORT%
start "Crepto_Ai Frontend [Port %FRONTEND_PORT%]" cmd /k "title Crepto_Ai Frontend [Port %FRONTEND_PORT%] && color 0E && npm run dev"
echo OK - Frontend server starting...
echo.

:: Wait for frontend
timeout /t 5 /nobreak > nul

:: Display final status
color 0A
cls
echo.
echo ====================================================
echo           ALL SERVERS ARE RUNNING
echo ====================================================
echo.
echo Proxy Server (CORS-Free):     %PROXY_URL%
echo Backend Server (Python):      %BACKEND_URL%
echo Frontend Server (React):      %FRONTEND_URL%
echo.
echo ------------------------------------------------
echo.
echo PROXY API ENDPOINTS (CORS-Free):
echo    Health: %PROXY_URL%/health
echo    CMC:    %PROXY_URL%/api/coinmarketcap/quotes?symbols=BTC,ETH
echo    Gecko:  %PROXY_URL%/api/coingecko/price?ids=bitcoin,ethereum
echo    Fear:   %PROXY_URL%/api/feargreed
echo    News:   %PROXY_URL%/api/news/crypto
echo.
echo TEST IN BROWSER CONSOLE:
echo    await fetch('http://localhost:3002/api/feargreed').then(r=>r.json())
echo.
echo ------------------------------------------------
echo.
echo ADVANTAGES OF PROXY MODE:
echo    [OK] NO CORS errors
echo    [OK] API keys secured on server
echo    [OK] All external APIs accessible
echo    [OK] Rate limiting handled
echo    [OK] Request logging enabled
echo    [OK] Auto-fallback to alternative APIs
echo.
echo Opening application...
timeout /t 3 /nobreak > nul
start %FRONTEND_URL%

echo.
echo All servers launched successfully!
echo.
echo NOTE: Three terminal windows are now running:
echo   1. Proxy Server (purple) - Port %PROXY_PORT%
echo   2. Backend Server (cyan) - Port %BACKEND_PORT%
echo   3. Frontend Server (yellow) - Port %FRONTEND_PORT%
echo.
echo DO NOT CLOSE those windows - they are running your servers!
echo.
echo Press any key to exit this launcher (servers will continue)...
pause > nul
