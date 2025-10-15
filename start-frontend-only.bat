@echo off
chcp 65001 > nul
title Crepto_Ai - Frontend Server Only
color 0E

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          CREPTO_AI FRONTEND SERVER                        ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Check Node.js
echo Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ ERROR: Node.js not found
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

:: Check if dependencies are installed
if not exist "node_modules\" (
    color 0E
    echo ⚠️  Dependencies not found. Installing...
    call npm install
    if errorlevel 1 (
        color 0C
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
    echo.
)

:: Kill existing frontend processes
echo Stopping existing frontend processes...
taskkill /FI "WINDOWTITLE eq Crepto_Ai Frontend*" /F > nul 2>&1
timeout /t 1 /nobreak > nul

:: Start frontend server
echo.
echo Starting Frontend Server...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Port: 5173 (Vite default)
echo URL:  http://localhost:5173
echo.
echo 💡 The frontend expects the backend to be running on port 5000
echo    Start backend with: start-backend-only.bat
echo.
echo Press Ctrl+C to stop the server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

npm run dev
