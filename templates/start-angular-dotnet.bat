@echo off
REM Template for Angular + .NET Core Stack
chcp 65001 > nul
title Angular + .NET Core Launcher
color 0D

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          ANGULAR + .NET CORE LAUNCHER                     ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Set ports
set BACKEND_PORT=7000
set FRONTEND_PORT=4200

:: Check .NET
echo [1/4] Checking .NET SDK...
dotnet --version > nul 2>&1
if errorlevel 1 (
    echo ❌ .NET SDK not found
    echo Download from: https://dotnet.microsoft.com/download
    pause
    exit /b 1
)
echo ✅ .NET SDK found
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
taskkill /f /im dotnet.exe > nul 2>&1
taskkill /f /im node.exe > nul 2>&1
timeout /t 2 /nobreak > nul

:: Start .NET Backend
echo [3/4] Starting .NET Core Backend...
cd backend
start ".NET Backend [Port %BACKEND_PORT%]" cmd /k "title .NET Backend && color 0B && dotnet run --urls=http://localhost:%BACKEND_PORT%"
cd ..
echo ✅ Backend starting on port %BACKEND_PORT%
echo.

:: Wait for backend
echo Waiting for backend to be ready...
timeout /t 10 /nobreak > nul

:: Start Angular Frontend
echo [4/4] Starting Angular Frontend...
cd frontend
start "Angular Frontend [Port %FRONTEND_PORT%]" cmd /k "title Angular Frontend && color 0E && ng serve --port %FRONTEND_PORT%"
cd ..
echo ✅ Frontend starting on port %FRONTEND_PORT%
echo.

:: Display info
timeout /t 5 /nobreak > nul
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              SERVERS ARE RUNNING                          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🚀 Backend (.NET):     http://localhost:%BACKEND_PORT%
echo 🌐 Swagger UI:         http://localhost:%BACKEND_PORT%/swagger
echo 🎨 Frontend (Angular): http://localhost:%FRONTEND_PORT%
echo.
echo Press any key to open application...
pause > nul
start http://localhost:%FRONTEND_PORT%
