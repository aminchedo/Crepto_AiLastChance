@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title Crepto AI Toolbox

:MAIN_MENU
cls
echo.
echo ==================================================
echo    🛠️  CREPTO AI - COMPLETE TOOLBOX
echo ==================================================
echo.
echo  📊 APPLICATION MANAGEMENT:
echo     1. 🚀 Start Full Stack App
echo     2. ⚡ Quick Start (Direct)
echo     3. 🔄 Restart Servers
echo     4. 🛑 Stop All Servers
echo.
echo  🔧 SYSTEM TOOLS:
echo     5. 🔍 Run Full Diagnostics
echo     6. 📦 Install/Update Dependencies
echo     7. 🧹 Clean System & Cache
echo     8. 📡 Check Network & Ports
echo.
echo  📈 MONITORING:
echo     9. 📊 View Server Status
echo     10. 📝 View Server Logs
echo     11. 🌐 Open Application URLs
echo.
echo  ⚙️  CONFIGURATION:
echo     12. 🔧 Configure Ports
echo     13. 📁 Project Structure Info
echo     14. 💾 Backup Configuration
echo.
echo  🚨 TROUBLESHOOTING:
echo     15. 🐛 Fix Common Issues
echo     16. 📋 System Information
echo     17. 🧪 Run Health Check
echo.
echo  ❌ 18. Exit Toolbox
echo.
set /p CHOICE="Select option (1-18): "

if "%CHOICE%"=="1" goto START_FULL
if "%CHOICE%"=="2" goto QUICK_START
if "%CHOICE%"=="3" goto RESTART
if "%CHOICE%"=="4" goto STOP_SERVERS
if "%CHOICE%"=="5" goto DIAGNOSTICS
if "%CHOICE%"=="6" goto INSTALL_DEPS
if "%CHOICE%"=="7" goto CLEAN_SYSTEM
if "%CHOICE%"=="8" goto NETWORK_CHECK
if "%CHOICE%"=="9" goto SERVER_STATUS
if "%CHOICE%"=="10" goto VIEW_LOGS
if "%CHOICE%"=="11" goto OPEN_URLS
if "%CHOICE%"=="12" goto CONFIG_PORTS
if "%CHOICE%"=="13" goto PROJECT_INFO
if "%CHOICE%"=="14" goto BACKUP_CONFIG
if "%CHOICE%"=="15" goto FIX_ISSUES
if "%CHOICE%"=="16" goto SYSTEM_INFO
if "%CHOICE%"=="17" goto HEALTH_CHECK
if "%CHOICE%"=="18" goto EXIT

echo Invalid choice! Press any key to continue...
pause >nul
goto MAIN_MENU

:START_FULL
cls
echo ==================================================
echo    🚀 STARTING FULL STACK APPLICATION
echo ==================================================
echo.
call :run_diagnostic quiet
call :install_dependencies
call :stop_servers
call :start_servers
call :show_status
echo.
echo Press any key to return to toolbox...
pause >nul
goto MAIN_MENU

:QUICK_START
cls
echo ==================================================
echo    ⚡ QUICK START - DIRECT LAUNCH
echo ==================================================
echo.
call :stop_servers
timeout /t 2 /nobreak >nul

if exist "server\package.json" (
    echo Starting Backend Server...
    cd server
    start "Crepto Backend" /min cmd /c "npm run dev"
    cd ..
)

if exist "frontend\package.json" (
    timeout /t 3 /nobreak >nul
    echo Starting Frontend Server...
    cd frontend
    start "Crepto Frontend" /min cmd /c "npm run dev"
    cd ..
)

if exist "backend\package.json" (
    echo Starting Backend Server...
    cd backend
    start "Crepto Backend" /min cmd /c "npm run dev"
    cd ..
)

echo.
echo ✅ Quick start completed!
echo Servers starting in background windows...
timeout /t 3 /nobreak >nul
goto MAIN_MENU

:RESTART
cls
echo ==================================================
echo    🔄 RESTARTING ALL SERVERS
echo ==================================================
echo.
call :stop_servers
timeout /t 3 /nobreak >nul
call :start_servers
call :show_status
echo.
echo Press any key to continue...
pause >nul
goto MAIN_MENU

:STOP_SERVERS
cls
echo ==================================================
echo    🛑 STOPPING ALL SERVERS
echo ==================================================
echo.
call :stop_servers
echo.
echo ✅ All servers stopped!
pause
goto MAIN_MENU

:DIAGNOSTICS
cls
echo ==================================================
echo    🔍 RUNNING FULL DIAGNOSTICS
echo ==================================================
echo.
call :run_diagnostic full
echo.
echo Press any key to continue...
pause >nul
goto MAIN_MENU

:INSTALL_DEPS
cls
echo ==================================================
echo    📦 INSTALLING/UPDATE DEPENDENCIES
echo ==================================================
echo.
call :install_dependencies
echo.
echo Press any key to continue...
pause >nul
goto MAIN_MENU

:CLEAN_SYSTEM
cls
echo ==================================================
echo    🧹 CLEANING SYSTEM & CACHE
echo ==================================================
echo.
echo Cleaning Node modules cache...
npm cache clean --force >nul 2>&1
echo Cleaning temporary files...
del /q /f *.log >nul 2>&1
del /q /f app-config.txt >nul 2>&1
echo Stopping all processes...
call :stop_servers
echo.
echo ✅ System cleaned successfully!
pause
goto MAIN_MENU

:NETWORK_CHECK
cls
echo ==================================================
echo    📡 NETWORK & PORT CHECK
echo ==================================================
echo.
echo Checking common application ports:
echo.
for %%p in (3000 3001 5000 5173 8000 8080 9000) do (
    netstat -ano | findstr ":%%p " >nul
    if errorlevel 1 (
        echo ✅ Port %%p: Available
    ) else (
        echo ❌ Port %%p: In Use
    )
)
echo.
echo Network configuration:
ipconfig | findstr "IPv4" | findstr /v "127.0.0.1"
echo.
pause
goto MAIN_MENU

:SERVER_STATUS
cls
echo ==================================================
echo    📊 SERVER STATUS & PROCESSES
echo ==================================================
echo.
echo Node.js Processes:
tasklist /fi "imagename eq node.exe" /fo table
echo.
echo Active Ports:
netstat -ano | findstr "LISTENING" | findstr ":3000 :5000 :5173 :8080"
echo.
pause
goto MAIN_MENU

:VIEW_LOGS
cls
echo ==================================================
echo    📝 SERVER LOGS MANAGEMENT
echo ==================================================
echo.
echo 1. View Backend Logs (if window exists)
echo 2. View Frontend Logs (if window exists)
echo 3. Check Recent Log Files
echo 4. Back to Main Menu
echo.
set /p LOG_CHOICE="Select option: "

if "%LOG_CHOICE%"=="1" (
    powershell -command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('Crepto Backend')" 2>nul
    if errorlevel 1 echo Backend window not found!
    timeout /t 2 /nobreak >nul
    goto VIEW_LOGS
)

if "%LOG_CHOICE%"=="2" (
    powershell -command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('Crepto Frontend')" 2>nul
    if errorlevel 1 echo Frontend window not found!
    timeout /t 2 /nobreak >nul
    goto VIEW_LOGS
)

if "%LOG_CHOICE%"=="3" (
    echo Recent log files:
    dir *.log 2>nul
    if errorlevel 1 echo No log files found.
    echo.
    pause
    goto VIEW_LOGS
)

goto MAIN_MENU

:OPEN_URLS
cls
echo ==================================================
echo    🌐 OPENING APPLICATION URLS
echo ==================================================
echo.
echo Opening application URLs in browser...
start "" "http://localhost:5173"  // Frontend
timeout /t 1 /nobreak >nul
start "" "http://localhost:5000"  // Backend API
timeout /t 1 /nobreak >nul
start "" "http://localhost:5000/api"  // API Docs
echo.
echo ✅ URLs opened in browser!
pause
goto MAIN_MENU

:CONFIG_PORTS
cls
echo ==================================================
echo    🔧 CONFIGURE PORTS
echo ==================================================
echo.
set /p NEW_BACKEND_PORT="Enter Backend Port (current: 5000): "
set /p NEW_FRONTEND_PORT="Enter Frontend Port (current: 5173): "

if not "!NEW_BACKEND_PORT!"=="" set BACKEND_PORT=!NEW_BACKEND_PORT!
if not "!NEW_FRONTEND_PORT!"=="" set FRONTEND_PORT=!NEW_FRONTEND_PORT!

echo BACKEND_PORT=!BACKEND_PORT! > toolbox-config.txt
echo FRONTEND_PORT=!FRONTEND_PORT! >> toolbox-config.txt

echo.
echo ✅ Port configuration saved!
echo Backend: !BACKEND_PORT! | Frontend: !FRONTEND_PORT!
pause
goto MAIN_MENU

:PROJECT_INFO
cls
echo ==================================================
echo    📁 PROJECT STRUCTURE INFORMATION
echo ==================================================
echo.
echo Current Directory: %cd%
echo.
echo Directory Structure:
tree /f /a | more
echo.
pause
goto MAIN_MENU

:BACKUP_CONFIG
cls
echo ==================================================
echo    💾 BACKUP CONFIGURATION
echo ==================================================
echo.
echo Creating configuration backup...
set BACKUP_FOLDER=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
mkdir !BACKUP_FOLDER! >nul 2>&1

copy app-config.txt !BACKUP_FOLDER! >nul 2>&1
copy toolbox-config.txt !BACKUP_FOLDER! >nul 2>&1

echo ✅ Configuration backed up to: !BACKUP_FOLDER!
echo.
dir !BACKUP_FOLDER!
pause
goto MAIN_MENU

:FIX_ISSUES
cls
echo ==================================================
echo    🐛 FIXING COMMON ISSUES
echo ==================================================
echo.
echo 1. Fix Missing Dependencies
echo 2. Fix Port Conflicts
echo 3. Clear Node Cache
echo 4. Reset Configuration
echo 5. Back to Main Menu
echo.
set /p FIX_CHOICE="Select fix to apply: "

if "%FIX_CHOICE%"=="1" (
    echo Reinstalling dependencies...
    call :stop_servers
    if exist "server" ( cd server && del /q node_modules 2>nul && cd .. )
    if exist "frontend" ( cd frontend && del /q node_modules 2>nul && cd .. )
    call :install_dependencies
    goto FIX_ISSUES
)

if "%FIX_CHOICE%"=="2" (
    echo Resolving port conflicts...
    call :stop_servers
    echo Ports cleared. You can now restart servers.
    goto FIX_ISSUES
)

if "%FIX_CHOICE%"=="3" (
    echo Clearing Node.js cache...
    npm cache clean --force
    echo ✅ Cache cleared!
    goto FIX_ISSUES
)

if "%FIX_CHOICE%"=="4" (
    echo Resetting configuration...
    del app-config.txt 2>nul
    del toolbox-config.txt 2>nul
    echo ✅ Configuration reset!
    goto FIX_ISSUES
)

goto MAIN_MENU

:SYSTEM_INFO
cls
echo ==================================================
echo    📋 SYSTEM INFORMATION
echo ==================================================
echo.
echo Operating System:
ver
echo.
echo Node.js Version:
node --version
echo.
echo npm Version:
npm --version
echo.
echo Disk Space:
for /f "tokens=3" %%a in ('dir /-c /w ^| find "bytes free"') do echo Available: %%a bytes
echo.
echo Current User:
echo %username%
echo.
pause
goto MAIN_MENU

:HEALTH_CHECK
cls
echo ==================================================
echo    🧪 RUNNING HEALTH CHECK
echo ==================================================
echo.
echo 🔍 Checking system health...

:: Check if servers are responsive
echo Checking backend (port 5000)...
curl --silent --output nul --max-time 5 http://localhost:5000/health
if errorlevel 1 echo ❌ Backend not responding
if not errorlevel 1 echo ✅ Backend healthy

echo Checking frontend (port 5173)...
curl --silent --output nul --max-time 5 http://localhost:5173
if errorlevel 1 echo ❌ Frontend not responding
if not errorlevel 1 echo ✅ Frontend healthy

echo.
echo ✅ Health check completed!
pause
goto MAIN_MENU

:EXIT
cls
echo ==================================================
echo    👋 THANK YOU FOR USING CREPTO AI TOOLBOX
echo ==================================================
echo.
echo Servers are still running in background.
echo Use 'Stop All Servers' option to close them.
echo.
timeout /t 3 /nobreak >nul
exit /b 0

:: ==================================================
:: 🛠️  TOOLBOX FUNCTIONS
:: ==================================================

:run_diagnostic
cls
echo Running comprehensive diagnostics...
echo.

set ERROR_COUNT=0
echo [1/6] Checking Node.js...
node --version >nul 2>&1 || (echo ❌ Node.js missing & set /a ERROR_COUNT+=1)

echo [2/6] Checking project structure...
set SERVER_FOUND=0
for %%d in (server backend) do if exist "%%d\package.json" set SERVER_FOUND=1
if !SERVER_FOUND! equ 0 (echo ❌ No server found & set /a ERROR_COUNT+=1)

echo [3/6] Checking dependencies...
if exist "server" if not exist "server\node_modules" echo ⚠️ Server deps missing
if exist "frontend" if not exist "frontend\node_modules" echo ⚠️ Frontend deps missing

echo [4/6] Checking ports...
for %%p in (5000 5173) do (
    netstat -ano | findstr ":%%p " >nul && echo ❌ Port %%p in use
)

echo [5/6] Checking scripts...
if exist "server\package.json" (
    cd server
    npm run | findstr "dev" >nul || echo ❌ No dev script in server
    cd ..
)

echo [6/6] System resources...
for /f "tokens=3" %%a in ('dir /-c /w ^| find "bytes free"') do echo Disk: %%a free

echo.
if !ERROR_COUNT! equ 0 (
    echo ✅ Diagnostics: ALL SYSTEMS GO
) else (
    echo ❌ Diagnostics: !ERROR_COUNT! issues found
)
exit /b !ERROR_COUNT!

:install_dependencies
echo Installing dependencies...
if exist "server\package.json" (
    echo Installing server dependencies...
    cd server
    npm install
    cd ..
)
if exist "frontend\package.json" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)
echo ✅ Dependencies installed
exit /b 0

:stop_servers
echo Stopping all servers...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.exe >nul 2>&1
timeout /t 2 /nobreak >nul
exit /b 0

:start_servers
echo Starting servers...
if exist "server\package.json" (
    echo Starting backend...
    cd server
    start "Crepto Backend" /min cmd /c "npm run dev"
    cd ..
    timeout /t 5 /nobreak >nul
)
if exist "frontend\package.json" (
    echo Starting frontend...
    cd frontend
    start "Crepto Frontend" /min cmd /c "npm run dev"
    cd ..
)
exit /b 0

:show_status
cls
echo ==================================================
echo    📊 APPLICATION STATUS
echo ==================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Active Node processes:
tasklist /fi "imagename eq node.exe" | find "node.exe" >nul && echo ✅ Servers running || echo ❌ No servers running
echo.
exit /b 0

endlocal