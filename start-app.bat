@echo off
chcp 65001 > nul
title Crepto_Ai - Full Stack Launcher
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          CREPTO_AI FULL-STACK APPLICATION                ║
echo ║          React (Vite) + Python (FastAPI) Launcher        ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Set environment variables
set BACKEND_PORT=8000
set FRONTEND_PORT=5173
set BACKEND_URL=http://localhost:%BACKEND_PORT%
set FRONTEND_URL=http://localhost:%FRONTEND_PORT%

:: Check if Python is installed
echo [1/7] Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%
echo.

:: Check if Node.js is installed
echo [2/7] Checking Node.js installation...
node --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js found: %NODE_VERSION%
echo.

:: Check if npm is installed
echo [3/7] Checking npm installation...
npm --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: npm is not installed
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✅ npm found: v%NPM_VERSION%
echo.

:: Kill any existing processes to avoid port conflicts
echo [4/7] Cleaning up existing processes...
taskkill /f /im python.exe > nul 2>&1
if errorlevel 1 (
    echo ℹ️  No existing Python processes found
) else (
    echo ✅ Cleaned up existing Python processes
)
taskkill /f /im node.exe > nul 2>&1
if errorlevel 1 (
    echo ℹ️  No existing Node.js processes found
) else (
    echo ✅ Cleaned up existing Node.js processes
)
timeout /t 2 /nobreak > nul
echo.

:: Start Backend Server (Python FastAPI)
echo [5/7] Starting Python Backend Server...
echo     Port: %BACKEND_PORT%
echo     URL:  %BACKEND_URL%
echo     API Docs: %BACKEND_URL%/docs
if not exist "backend\" (
    color 0C
    echo ❌ ERROR: Backend directory not found!
    pause
    exit /b 1
)

cd backend

:: Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo ℹ️  Using virtual environment...
    start "Crepto_Ai Backend [Port %BACKEND_PORT%]" cmd /k "title Crepto_Ai Backend [Port %BACKEND_PORT%] && color 0B && cd /d "%CD%" && call venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
) else (
    echo ℹ️  No virtual environment found, using global Python...
    echo ⚠️  Tip: Create a venv with: python -m venv venv
    start "Crepto_Ai Backend [Port %BACKEND_PORT%]" cmd /k "title Crepto_Ai Backend [Port %BACKEND_PORT%] && color 0B && cd /d "%CD%" && python -m uvicorn main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"
)
cd ..
echo ✅ Backend server starting...
echo.

:: Wait for backend to be ready
echo [6/7] Waiting for backend to be ready...
set /a attempts=0
set /a max_attempts=30

:CHECK_BACKEND
set /a attempts+=1
if %attempts% gtr %max_attempts% (
    color 0E
    echo ⚠️  WARNING: Backend health check timed out after 30 seconds
    echo     Backend may still be starting up...
    goto START_FRONTEND
)

:: Simple port check
netstat -an | find ":%BACKEND_PORT%" | find "LISTENING" > nul 2>&1
if errorlevel 1 (
    echo     Attempt %attempts%/%max_attempts% - Waiting for backend...
    timeout /t 1 /nobreak > nul
    goto CHECK_BACKEND
)

echo ✅ Backend is ready!
echo.

:: Start Frontend Server (React + Vite)
:START_FRONTEND
echo [7/7] Starting React Frontend Server...
echo     Port: %FRONTEND_PORT%
echo     URL:  %FRONTEND_URL%

:: Frontend runs from root directory (not a separate folder)
start "Crepto_Ai Frontend [Port %FRONTEND_PORT%]" cmd /k "title Crepto_Ai Frontend [Port %FRONTEND_PORT%] && color 0E && npm run dev"
echo ✅ Frontend server starting...
echo.

:: Wait a moment for frontend to initialize
timeout /t 5 /nobreak > nul

:: Display final status
color 0A
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              SERVERS ARE NOW RUNNING                      ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🐍 Backend Server (Python/FastAPI):  %BACKEND_URL%
echo 📚 API Documentation:                %BACKEND_URL%/docs
echo 🎨 Frontend Server (React/Vite):     %FRONTEND_URL%
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📝 AVAILABLE API ENDPOINTS:
echo    • API Docs (Swagger):  %BACKEND_URL%/docs
echo    • API ReDoc:           %BACKEND_URL%/redoc
echo    • Health Check:        %BACKEND_URL%/health
echo    • Market Data:         %BACKEND_URL%/api/market
echo    • Predictions:         %BACKEND_URL%/api/predictions
echo.
echo 🧪 TEST COMMANDS (Run in browser console):
echo    • await qt() - Quick test all APIs
echo    • await universalAPITester.quickTest() - Test Universal APIs
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 CONTROL INSTRUCTIONS:
echo    • Press Ctrl+C in each server window to stop
echo    • Close this window to keep servers running
echo    • Use process-manager.bat for advanced controls
echo.
echo Opening application in browser...
timeout /t 3 /nobreak > nul

:: Open browser to frontend
start %FRONTEND_URL%

echo.
echo ✅ Application launched successfully!
echo.
echo Press any key to exit this launcher...
echo (Servers will continue running in separate windows)
pause > nul
