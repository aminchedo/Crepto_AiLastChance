@echo off
REM Template for Vue.js + Python FastAPI Stack
chcp 65001 > nul
title Vue.js + Python FastAPI Launcher
color 0D

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          VUE.JS + PYTHON FASTAPI LAUNCHER                 ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Set ports
set BACKEND_PORT=8000
set FRONTEND_PORT=8080

:: Check Python
echo [1/4] Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    pause
    exit /b 1
)
echo ✅ Python found
echo.

:: Check Node.js
echo [2/4] Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

:: Kill existing processes
echo Cleaning up existing processes...
taskkill /f /im python.exe > nul 2>&1
taskkill /f /im node.exe > nul 2>&1
timeout /t 2 /nobreak > nul

:: Start Python Backend
echo [3/4] Starting FastAPI Backend...
cd backend
start "FastAPI Backend [Port %BACKEND_PORT%]" cmd /k "title FastAPI Backend && color 0B && uvicorn main:app --reload --port %BACKEND_PORT%"
cd ..
echo ✅ Backend starting on port %BACKEND_PORT%
echo.

:: Wait for backend
echo Waiting for backend to be ready...
timeout /t 7 /nobreak > nul

:: Start Vue Frontend
echo [4/4] Starting Vue.js Frontend...
cd frontend
start "Vue Frontend [Port %FRONTEND_PORT%]" cmd /k "title Vue Frontend && color 0E && npm run serve"
cd ..
echo ✅ Frontend starting on port %FRONTEND_PORT%
echo.

:: Display info
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              SERVERS ARE RUNNING                          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🚀 Backend (FastAPI):  http://localhost:%BACKEND_PORT%
echo 📚 API Docs:           http://localhost:%BACKEND_PORT%/docs
echo 🎨 Frontend (Vue.js):  http://localhost:%FRONTEND_PORT%
echo.
echo Press any key to open application...
pause > nul
start http://localhost:%FRONTEND_PORT%
