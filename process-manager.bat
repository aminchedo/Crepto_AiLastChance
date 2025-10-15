@echo off
chcp 65001 > nul
title Crepto_Ai - Process Manager
color 0B

:MENU
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          CREPTO_AI PROCESS MANAGER                        ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo   1. 🚀 Start Both Servers
echo   2. 🛑 Stop All Servers
echo   3. 🔄 Restart Backend Only
echo   4. 🔄 Restart Frontend Only
echo   5. 🔄 Restart Both Servers
echo   6. 👀 View Running Processes
echo   7. 🏥 Health Check
echo   8. 📊 View Server Logs
echo   9. 🔧 Install Dependencies
echo   0. ❌ Exit
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto STOP_ALL
if "%choice%"=="3" goto RESTART_BACKEND
if "%choice%"=="4" goto RESTART_FRONTEND
if "%choice%"=="5" goto RESTART_BOTH
if "%choice%"=="6" goto VIEW_PROCESSES
if "%choice%"=="7" goto HEALTH_CHECK
if "%choice%"=="8" goto VIEW_LOGS
if "%choice%"=="9" goto INSTALL_DEPS
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 > nul
goto MENU

:START_ALL
cls
echo.
echo 🚀 Starting All Servers...
echo.
call start-app.bat
goto MENU

:STOP_ALL
cls
echo.
echo 🛑 Stopping All Servers...
echo.
taskkill /f /im node.exe > nul 2>&1
if errorlevel 1 (
    echo ℹ️  No Node.js processes found
) else (
    echo ✅ All Node.js processes stopped
)
timeout /t 2 > nul
goto MENU

:RESTART_BACKEND
cls
echo.
echo 🔄 Restarting Backend Server...
echo.
:: Kill only backend processes (by window title if possible, otherwise all node)
taskkill /FI "WINDOWTITLE eq Crepto_Ai Backend*" /F > nul 2>&1
if errorlevel 1 (
    echo Stopping all Node.js processes...
    taskkill /f /im node.exe > nul 2>&1
)
timeout /t 2 /nobreak > nul

echo Starting Backend...
cd backend
start "Crepto_Ai Backend [Port 5000]" cmd /k "title Crepto_Ai Backend [Port 5000] && color 0B && npm run dev"
cd ..
echo ✅ Backend restarted
timeout /t 3 > nul
goto MENU

:RESTART_FRONTEND
cls
echo.
echo 🔄 Restarting Frontend Server...
echo.
:: Kill only frontend processes
taskkill /FI "WINDOWTITLE eq Crepto_Ai Frontend*" /F > nul 2>&1
timeout /t 2 /nobreak > nul

echo Starting Frontend...
start "Crepto_Ai Frontend [Port 5173]" cmd /k "title Crepto_Ai Frontend [Port 5173] && color 0E && npm run dev"
echo ✅ Frontend restarted
timeout /t 3 > nul
goto MENU

:RESTART_BOTH
cls
echo.
echo 🔄 Restarting Both Servers...
echo.
call :STOP_ALL
timeout /t 2 /nobreak > nul
call :START_ALL
goto MENU

:VIEW_PROCESSES
cls
echo.
echo 👀 Running Node.js Processes:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
tasklist /FI "IMAGENAME eq node.exe" /FO TABLE
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Listening Ports:
netstat -an | find "LISTENING" | find ":5000"
netstat -an | find "LISTENING" | find ":5173"
echo.
pause
goto MENU

:HEALTH_CHECK
cls
echo.
echo 🏥 Performing Health Check...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: Check Backend
echo Checking Backend (Port 5000)...
netstat -an | find ":5000" | find "LISTENING" > nul 2>&1
if errorlevel 1 (
    echo ❌ Backend: NOT RUNNING
) else (
    echo ✅ Backend: RUNNING on port 5000
)

:: Check Frontend
echo.
echo Checking Frontend (Port 5173)...
netstat -an | find ":5173" | find "LISTENING" > nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend: NOT RUNNING
) else (
    echo ✅ Frontend: RUNNING on port 5173
)

:: Check Node.js
echo.
echo Checking Node.js processes...
tasklist /FI "IMAGENAME eq node.exe" > nul 2>&1
if errorlevel 1 (
    echo ❌ No Node.js processes found
) else (
    echo ✅ Node.js processes found
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pause
goto MENU

:VIEW_LOGS
cls
echo.
echo 📊 Server Logs Location:
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Backend logs:  logs\backend.log
echo Frontend logs: Console in Frontend server window
echo.
echo To view logs:
echo   • Check server console windows
echo   • Use F12 Developer Tools in browser
echo   • Run: universalAPITester.showMetrics() in browser console
echo.
pause
goto MENU

:INSTALL_DEPS
cls
echo.
echo 🔧 Installing Dependencies...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Installing Root Dependencies...
call npm install
if errorlevel 1 (
    color 0C
    echo ❌ Root dependencies installation failed
    pause
    goto MENU
)

echo.
echo Installing Backend Dependencies...
cd backend
call npm install
if errorlevel 1 (
    color 0C
    echo ❌ Backend dependencies installation failed
    cd ..
    pause
    goto MENU
)
cd ..

echo.
echo ✅ All dependencies installed successfully!
timeout /t 3 > nul
goto MENU

:EXIT
cls
echo.
echo Thanks for using Crepto_Ai Process Manager!
echo.
echo Note: This will exit the manager but servers will continue running.
echo       Use option 2 to stop servers before exiting if needed.
echo.
timeout /t 2 > nul
exit /b 0
