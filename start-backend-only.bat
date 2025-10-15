@echo off
chcp 65001 > nul
title Crepto_Ai - Backend Server Only
color 0B

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          CREPTO_AI PYTHON BACKEND SERVER                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Check Python
echo Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Python not found
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%
echo.

:: Navigate to backend directory
if not exist "backend\" (
    color 0C
    echo ❌ ERROR: Backend directory not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

cd backend

:: Check if requirements are installed
echo Checking Python dependencies...
python -c "import fastapi" > nul 2>&1
if errorlevel 1 (
    color 0E
    echo ⚠️  FastAPI not found. Installing dependencies...
    
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate
        pip install -r requirements.txt
    ) else (
        echo ⚠️  No virtual environment found!
        echo Creating virtual environment...
        python -m venv venv
        call venv\Scripts\activate
        pip install -r requirements.txt
    )
    
    if errorlevel 1 (
        color 0C
        echo ❌ Failed to install dependencies
        cd ..
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
    echo.
)

:: Kill existing backend processes
echo Stopping existing backend processes...
taskkill /FI "WINDOWTITLE eq Crepto_Ai Backend*" /F > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
timeout /t 1 /nobreak > nul

:: Start backend server
echo.
echo Starting Python Backend Server...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Port: 8000
echo URL:  http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
)
