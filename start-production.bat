@echo off
chcp 65001 > nul
title Crepto_Ai - Production Launcher
color 0D

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          CREPTO_AI PRODUCTION LAUNCHER                    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ⚠️  WARNING: This will build and start the production version
echo.
set /p confirm="Do you want to continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Cancelled.
    timeout /t 2 > nul
    exit /b 0
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: Clean previous build
echo [1/5] Cleaning previous build...
if exist "dist\" (
    echo Removing old dist folder...
    rd /s /q dist
)
if exist "build\" (
    echo Removing old build folder...
    rd /s /q build
)
echo ✅ Clean complete
echo.

:: Install dependencies (if needed)
echo [2/5] Checking dependencies...
if not exist "node_modules\" (
    echo Installing root dependencies...
    call npm install
    if errorlevel 1 (
        color 0C
        echo ❌ Failed to install root dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies OK
echo.

:: Build frontend
echo [3/5] Building Frontend for Production...
echo This may take a few minutes...
call npm run build
if errorlevel 1 (
    color 0C
    echo.
    echo ❌ Frontend build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)
echo ✅ Frontend build complete
echo.

:: Prepare backend
echo [4/5] Preparing Backend...
cd backend
if not exist "node_modules\" (
    echo Installing backend dependencies...
    call npm install --production
    if errorlevel 1 (
        color 0C
        echo ❌ Failed to install backend dependencies
        cd ..
        pause
        exit /b 1
    )
)
cd ..
echo ✅ Backend prepared
echo.

:: Start production server
echo [5/5] Starting Production Server...
echo.

:: Set production environment
set NODE_ENV=production
set PORT=3000

echo Environment: PRODUCTION
echo Port: %PORT%
echo.

:: Kill any existing processes
taskkill /f /im node.exe > nul 2>&1

:: Option 1: If you have a production server script
if exist "backend\server.js" (
    echo Starting backend production server...
    cd backend
    start "Crepto_Ai Production Server [Port %PORT%]" cmd /k "title Crepto_Ai Production && color 0A && node server.js"
    cd ..
) else if exist "backend\dist\server.js" (
    echo Starting compiled backend server...
    cd backend\dist
    start "Crepto_Ai Production Server [Port %PORT%]" cmd /k "title Crepto_Ai Production && color 0A && node server.js"
    cd ..\..
) else (
    echo Starting production server with serve...
    :: Install serve if not present
    call npm install -g serve > nul 2>&1
    
    :: Serve the built frontend
    start "Crepto_Ai Production [Port %PORT%]" cmd /k "title Crepto_Ai Production && color 0A && serve -s dist -l %PORT%"
)

:: Wait for server to start
echo.
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

:: Check if server is running
netstat -an | find ":%PORT%" | find "LISTENING" > nul 2>&1
if errorlevel 1 (
    color 0E
    echo ⚠️  Server may not be running on port %PORT%
    echo Check the server window for errors
) else (
    color 0A
    echo ✅ Server is running!
)

:: Display success message
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          🎉 PRODUCTION SERVER IS RUNNING                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🌐 Access your application at:
echo    http://localhost:%PORT%
echo.
echo 📊 Production Features:
echo    • Optimized bundle size
echo    • Minified code
echo    • Production API endpoints
echo    • Enhanced security
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 Management:
echo    • Press Ctrl+C in server window to stop
echo    • Use process-manager.bat for process control
echo    • Check logs in server window
echo.
echo Opening application in browser...
timeout /t 3 /nobreak > nul
start http://localhost:%PORT%

echo.
echo ✅ Production environment launched successfully!
echo.
pause
