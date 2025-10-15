@echo off
REM Template for Next.js Full Stack
chcp 65001 > nul
title Next.js Full Stack Launcher
color 0D

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          NEXT.JS FULL STACK LAUNCHER                      ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Set port
set PORT=3000

:: Check Node.js
echo [1/3] Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

:: Check dependencies
echo [2/3] Checking dependencies...
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies ready
echo.

:: Kill existing processes
echo Cleaning up existing processes...
taskkill /f /im node.exe > nul 2>&1
timeout /t 2 /nobreak > nul

:: Start Next.js
echo [3/3] Starting Next.js Development Server...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Port: %PORT%
echo URL:  http://localhost:%PORT%
echo.
echo Features:
echo   • Frontend + Backend in one project
echo   • API routes available at /api/*
echo   • Hot reload enabled
echo   • SSR (Server-Side Rendering)
echo.
echo Press Ctrl+C to stop the server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

npm run dev
