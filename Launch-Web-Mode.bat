@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    Claude Desktop - Web Mode Launcher
echo ========================================
echo.

REM Set console to UTF-8 for Persian text support
chcp 65001 >nul 2>&1

echo Starting Claude Desktop in Web Mode...
echo This will open the application in your default web browser.
echo.

REM Check if Node.js is available
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    echo Download from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] Please run this script from the Claude Desktop project directory.
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    npm install --no-audit --no-fund
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
)

echo [INFO] Starting Vite development server...
echo [INFO] The app will open in your browser automatically.
echo [INFO] Server will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.

REM Start the Vite dev server with auto-open browser
echo [INFO] Starting Vite development server...
echo [INFO] Browser will open automatically at: http://localhost:5173
echo [INFO] Press Ctrl+C to stop the server when you're done.
echo.

REM Start the Vite dev server with auto-open
npm run dev -- --open

REM If we get here, the server was stopped
echo.
echo [INFO] Development server stopped.
echo.
pause
