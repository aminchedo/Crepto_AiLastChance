@echo off
chcp 65001 > nul
title Crepto_Ai - Full Stack with Proxy
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║       CREPTO_AI FULL STACK + PROXY LAUNCHER            ║
echo ║    React + Python + Node.js Proxy (CORS-Free)          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Set environment variables
set PROXY_PORT=3002
set BACKEND_PORT=8000
set FRONTEND_PORT=5173
set PROXY_URL=http://localhost:%PROXY_PORT%
set BACKEND_URL=http://localhost:%BACKEND_PORT%
set FRONTEND_URL=http://localhost:%FRONTEND_PORT%

:: Check Node.js
echo [1/8] Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Node.js not installed
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

:: Check Python
echo [2/8] Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Python not installed
    pause
    exit /b 1
)
echo ✅ Python found
echo.

:: Kill existing processes
echo [3/8] Cleaning up processes...
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
timeout /t 2 /nobreak > nul
echo ✅ Cleanup complete
echo.

:: Install proxy dependencies if needed
echo [4/8] Checking proxy server dependencies...
cd proxy-server
if not exist "node_modules\" (
    echo Installing proxy dependencies...
    call npm install
    if errorlevel 1 (
        color 0C
        echo ❌ Failed to install proxy dependencies
        cd ..
        pause
        exit /b 1
    )
)
echo ✅ Proxy dependencies ready
cd ..
echo.

:: Start Proxy Server
echo [5/8] Starting CORS Proxy Server...
echo     Port: %PROXY_PORT%
echo     URL:  %PROXY_URL%
cd proxy-server
start "Crepto_Ai Proxy [Port %PROXY_PORT%]" cmd /k "title Crepto_Ai Proxy [Port %PROXY_PORT%] && color 0D && node server.js"
cd ..
echo ✅ Proxy server starting...
echo.

:: Wait for proxy
echo Waiting for proxy to be ready...
timeout /t 5 /nobreak > nul

:: Start Python Backend
echo [6/8] Starting Python Backend...
echo     Port: %BACKEND_PORT%
cd backend
if exist "venv\Scripts\activate.bat" (
    start "Crepto_Ai Backend [Port %BACKEND_PORT%]" cmd /k "title Crepto_Ai Backend [Port %BACKEND_PORT%] && color 0B && call venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
) else (
    start "Crepto_Ai Backend [Port %BACKEND_PORT%]" cmd /k "title Crepto_Ai Backend [Port %BACKEND_PORT%] && color 0B && python -m uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
)
cd ..
echo ✅ Backend server starting...
echo.

:: Wait for backend
echo [7/8] Waiting for backend...
timeout /t 8 /nobreak > nul

:: Start Frontend
echo [8/8] Starting React Frontend...
echo     Port: %FRONTEND_PORT%
start "Crepto_Ai Frontend [Port %FRONTEND_PORT%]" cmd /k "title Crepto_Ai Frontend [Port %FRONTEND_PORT%] && color 0E && npm run dev"
echo ✅ Frontend server starting...
echo.

:: Wait for frontend
timeout /t 5 /nobreak > nul

:: Display final status
color 0A
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           🎉 ALL SERVERS ARE RUNNING                    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🌐 Proxy Server (CORS-Free):     %PROXY_URL%
echo 🐍 Backend Server (Python):      %BACKEND_URL%
echo 🎨 Frontend Server (React):      %FRONTEND_URL%
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📊 PROXY API ENDPOINTS (CORS-Free):
echo    • Health: %PROXY_URL%/health
echo    • CMC:    %PROXY_URL%/api/coinmarketcap/quotes?symbols=BTC,ETH
echo    • Gecko:  %PROXY_URL%/api/coingecko/price?ids=bitcoin,ethereum
echo    • Fear:   %PROXY_URL%/api/feargreed
echo    • News:   %PROXY_URL%/api/news/crypto
echo.
echo 🧪 TEST IN BROWSER CONSOLE:
echo    • await qt()
echo    • await universalAPITester.quickTest()
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 ADVANTAGES OF PROXY MODE:
echo    ✅ NO CORS errors
echo    ✅ API keys secured on server
echo    ✅ All external APIs accessible
echo    ✅ Rate limiting handled
echo    ✅ Request logging enabled
echo.
echo Opening application...
timeout /t 3 /nobreak > nul
start %FRONTEND_URL%

echo.
echo ✅ All servers launched!
echo Press any key to exit (servers continue running)...
pause > nul
