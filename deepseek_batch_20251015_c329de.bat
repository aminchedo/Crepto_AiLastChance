@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title Crepto AI - Full Stack Launcher
color 0A

echo.
echo ===============================================
echo    CREPTO AI - FULL STACK LAUNCHER
echo ===============================================
echo.

:: Set default ports with command line overrides
if not "%~1"=="" (
  set BACKEND_PORT=%~1
) else (
  set BACKEND_PORT=5000
)

if not "%~2"=="" (
  set FRONTEND_PORT=%~2
) else (
  set FRONTEND_PORT=5173
)

set BACKEND_URL=http://localhost:%BACKEND_PORT%
set FRONTEND_URL=http://localhost:%FRONTEND_PORT%
set BACKEND_DIR=backend
set FRONTEND_DIR=frontend
set MAX_WAIT_TIME=30
set START_DIR=%cd%

echo Configuration:
echo   Backend Port:  %BACKEND_PORT%
echo   Frontend Port: %FRONTEND_PORT%
echo.

:: Pre-flight validation
echo [1/7] Performing pre-flight checks...

:: Check Node.js installation
echo [2/7] Checking Node.js installation...
where node >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>nul') do set NODE_VER=%%v
echo Node.js found: %NODE_VER%

:: Check npm installation
echo [3/7] Checking npm installation...
where npm >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: npm is not installed.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('npm --version 2^>nul') do set NPM_VER=%%v
echo npm found: %NPM_VER%

:: Validate project structure
echo [4/7] Validating project structure...
if not exist "%BACKEND_DIR%" (
    color 0C
    echo ERROR: Backend directory '%BACKEND_DIR%' not found
    pause
    exit /b 1
)
if not exist "%FRONTEND_DIR%" (
    color 0C
    echo ERROR: Frontend directory '%FRONTEND_DIR%' not found
    pause
    exit /b 1
)
echo Project structure validated

:: Check package.json files
echo [5/7] Checking package configurations...

cd "%BACKEND_DIR%"
if not exist "package.json" (
    color 0C
    echo ERROR: Backend package.json not found
    cd ..
    pause
    exit /b 1
)
npm run | findstr /i "dev" >nul
if errorlevel 1 (
    color 0C
    echo ERROR: No 'dev' script found in backend package.json
    cd ..
    pause
    exit /b 1
)
echo Backend package.json validated
cd ..

cd "%FRONTEND_DIR%"
if not exist "package.json" (
    color 0C
    echo ERROR: Frontend package.json not found
    cd ..
    pause
    exit /b 1
)
npm run | findstr /i "dev" >nul
if errorlevel 1 (
    color 0C
    echo ERROR: No 'dev' script found in frontend package.json
    cd ..
    pause
    exit /b 1
)
echo Frontend package.json validated
cd ..

:: Check port availability
echo [6/7] Checking port availability...
set PORTS_AVAILABLE=1
for %%p in (%BACKEND_PORT% %FRONTEND_PORT%) do (
    netstat -ano | findstr ":%%p " >nul
    if not errorlevel 1 (
        echo ERROR: Port %%p is already in use
        set PORTS_AVAILABLE=0
    ) else (
        echo Port %%p is available
    )
)

if %PORTS_AVAILABLE% equ 0 (
    color 0C
    echo.
    echo Please free up the required ports or specify different ports:
    echo launcher.bat [backend_port] [frontend_port]
    pause
    exit /b 1
)

:: Clean up any existing processes
echo [7/7] Cleaning up previous sessions...
tasklist /fi "imagename eq node.exe" | find /i "node.exe" >nul 2>&1
if errorlevel 1 (
    echo No existing Node.js processes detected.
) else (
    taskkill /f /im node.exe >nul 2>&1
    if errorlevel 1 (
        echo Warning: Failed to kill some node.exe processes
    ) else (
        echo Existing Node processes stopped
    )
)
timeout /t 2 /nobreak >nul

:: Start backend server
echo.
echo Starting Backend on port %BACKEND_PORT%...
cd "%BACKEND_DIR%"
start "Crepto AI Backend [Port %BACKEND_PORT%]" /min cmd /c "title Crepto AI Backend [Port %BACKEND_PORT%] && color 0B && npm run dev || echo Backend failed to start && pause"
cd ..

:: Wait for backend to be ready
echo Waiting for backend to be ready...
set attempts=0
set max_attempts=%MAX_WAIT_TIME%

:CHECK_BACKEND
set /a attempts+=1

:: Check if port is listening
netstat -ano | findstr /R /C:":%BACKEND_PORT% .*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo Backend port %BACKEND_PORT% is listening
    goto BACKEND_SUCCESS
)

if %attempts% gtr %max_attempts% (
    color 0E
    echo WARNING: Backend health check timed out after %max_attempts% seconds.
    echo Backend may still be starting up. Proceeding to start frontend.
    goto START_FRONTEND
)

echo Attempt %attempts%/%max_attempts% - Waiting for backend...
timeout /t 1 /nobreak >nul
goto CHECK_BACKEND

:BACKEND_SUCCESS
color 0A

:START_FRONTEND
:: Start frontend server
echo Starting Frontend on port %FRONTEND_PORT%...
cd "%FRONTEND_DIR%"
start "Crepto AI Frontend [Port %FRONTEND_PORT%]" /min cmd /c "title Crepto AI Frontend [Port %FRONTEND_PORT%] && color 0E && npm run dev || echo Frontend failed to start && pause"
cd ..

:: Final output
timeout /t 3 /nobreak >nul
color 0A
cls
echo.
echo ===============================================
echo    CREPTO AI STARTED SUCCESSFULLY
echo ===============================================
echo.
echo Backend Server:   %BACKEND_URL%
echo Frontend Server:  %FRONTEND_URL%
echo.
echo Example API endpoints:
echo   %BACKEND_URL%/api/market
echo   %BACKEND_URL%/api/sentiment
echo   %BACKEND_URL%/api/news
echo   %BACKEND_URL%/api/whales
echo.
echo Servers are running in minimized windows.
echo.

:: Open application in browser
echo Opening application in default browser...
timeout /t 2 /nobreak >nul
start "" "%FRONTEND_URL%"

echo.
echo Press any key to show server management options...
pause >nul

:: Server management menu
:MENU
cls
echo ===============================================
echo    CREPTO AI - SERVER MANAGEMENT
echo ===============================================
echo.
echo Application URLs:
echo  Backend:  %BACKEND_URL%
echo  Frontend: %FRONTEND_URL%
echo.
echo Management Options:
echo 1. Open Backend URL
echo 2. Open Frontend URL
echo 3. View Backend Logs
echo 4. View Frontend Logs
echo 5. Restart Both Servers
echo 6. Stop All Servers
echo 7. Exit (Leave servers running)
echo.
set /p CHOICE=Enter your choice (1-7): 

if "%CHOICE%"=="1" (
    start "" "%BACKEND_URL%"
    goto MENU
)
if "%CHOICE%"=="2" (
    start "" "%FRONTEND_URL%"
    goto MENU
)
if "%CHOICE%"=="3" (
    echo Bringing backend console to foreground...
    powershell -command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('Crepto AI Backend [Port %BACKEND_PORT%]')" 2>nul
    if errorlevel 1 (
        echo Backend window not found. It may have closed.
    )
    goto MENU
)
if "%CHOICE%"=="4" (
    echo Bringing frontend console to foreground...
    powershell -command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('Crepto AI Frontend [Port %FRONTEND_PORT%]')" 2>nul
    if errorlevel 1 (
        echo Frontend window not found. It may have closed.
    )
    goto MENU
)
if "%CHOICE%"=="5" (
    echo Restarting all servers...
    taskkill /f /im node.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    cls
    echo.
    echo ===============================================
    echo    RESTARTING CREPTO AI SERVERS
    echo ===============================================
    echo.
    endlocal
    call "%~f0" %BACKEND_PORT% %FRONTEND_PORT%
    exit /b 0
)
if "%CHOICE%"=="6" (
    echo Stopping all servers...
    taskkill /f /im node.exe >nul 2>&1
    echo.
    echo All servers have been stopped.
    pause
    exit /b 0
)
if "%CHOICE%"=="7" (
    echo.
    echo Servers will continue running in background.
    echo Use system task manager to stop them if needed.
    timeout /t 2 /nobreak >nul
    exit /b 0
)

echo Invalid choice. Please try again.
timeout /t 2 /nobreak >nul
goto MENU

endlocal