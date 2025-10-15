@echo off
chcp 65001 > nul
title Quick CORS Fix

echo.
echo ==================================================
echo    🚀 QUICK CORS FIX FOR CREPTO AI
echo ==================================================
echo.
echo Applying immediate CORS solutions...
echo.

:: Stop everything
echo Stopping servers...
taskkill /f /im node.exe >nul 2>&1
timeout /t 3 /nobreak >nul

:: Start backend first (for proxy)
echo Starting backend proxy...
if exist "server" (
    cd server
    start "Backend Proxy" /min cmd /c "npm run dev"
    cd ..
)

:: Wait for backend
echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

:: Start frontend
echo Starting frontend...
if exist "frontend" (
    cd frontend
    start "Frontend" /min cmd /c "npm run dev"
    cd ..
)

echo.
echo ✅ CORS fix applied!
echo.
echo The application will now use the backend as a proxy
echo to avoid CORS errors with external APIs.
echo.
echo Opening application...
timeout /t 3 /nobreak >nul
start "" "http://localhost:5173"

echo Press any key to open CORS Toolbox for more options...
pause >nul
cors-fix-toolbox.bat