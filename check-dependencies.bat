@echo off
chcp 65001 > nul
title Crepto_Ai - Dependency Checker
color 0E

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          CREPTO_AI DEPENDENCY CHECKER                     ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Checking development environment...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set all_ok=1

:: Check Python
echo [1/7] Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python: NOT FOUND
    echo    Download from: https://www.python.org/downloads/
    set all_ok=0
) else (
    for /f "tokens=*" %%i in ('python --version') do set python_version=%%i
    echo ✅ Python: %python_version%
)
echo.

:: Check Node.js
echo [2/7] Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js: NOT FOUND
    echo    Download from: https://nodejs.org/
    set all_ok=0
) else (
    for /f "tokens=*" %%i in ('node --version') do set node_version=%%i
    echo ✅ Node.js: %node_version%
)
echo.

:: Check npm
echo [3/7] Checking npm...
npm --version > nul 2>&1
if errorlevel 1 (
    echo ❌ npm: NOT FOUND
    set all_ok=0
) else (
    for /f "tokens=*" %%i in ('npm --version') do set npm_version=%%i
    echo ✅ npm: v%npm_version%
)
echo.

:: Check Git
echo [4/7] Checking Git...
git --version > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git: NOT FOUND (optional)
    echo    Download from: https://git-scm.com/
) else (
    for /f "tokens=*" %%i in ('git --version') do set git_version=%%i
    echo ✅ Git: %git_version%
)
echo.

:: Check if project dependencies are installed
echo [5/7] Checking project dependencies...

if exist "node_modules\" (
    echo ✅ Root node_modules: FOUND
) else (
    echo ❌ Root node_modules: NOT FOUND
    echo    Run: npm install
    set all_ok=0
)

if exist "backend\venv\" (
    echo ✅ Backend virtual environment: FOUND
) else (
    echo ⚠️  Backend virtual environment: NOT FOUND
    echo    Run: cd backend && python -m venv venv
)

if exist "backend\venv\" (
    backend\venv\Scripts\python.exe -c "import fastapi" > nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Backend dependencies: NOT INSTALLED
        echo    Run: cd backend && venv\Scripts\activate && pip install -r requirements.txt
    ) else (
        echo ✅ Backend dependencies: INSTALLED
    )
)
echo.

:: Check required ports
echo [6/7] Checking port availability...

netstat -an | find ":8000" | find "LISTENING" > nul 2>&1
if errorlevel 1 (
    echo ✅ Port 8000 (Backend): AVAILABLE
) else (
    echo ⚠️  Port 8000 (Backend): IN USE
    echo    You may need to stop existing processes
)

netstat -an | find ":5173" | find "LISTENING" > nul 2>&1
if errorlevel 1 (
    echo ✅ Port 5173 (Frontend): AVAILABLE
) else (
    echo ⚠️  Port 5173 (Frontend): IN USE
    echo    You may need to stop existing processes
)
echo.

:: Check system resources
echo [7/7] Checking system information...
echo.
echo System Info:
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
echo.
echo Available Memory:
wmic OS get FreePhysicalMemory /value | find "="
echo.

:: Summary
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
if %all_ok%==1 (
    color 0A
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║              ✅ ALL CHECKS PASSED                          ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    echo Your environment is ready to run Crepto_Ai!
    echo.
    echo Next steps:
    echo   1. Run: start-app.bat
    echo   2. Or use: process-manager.bat for advanced controls
) else (
    color 0C
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║              ⚠️  SOME CHECKS FAILED                        ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    echo Please install missing dependencies before running the app.
    echo.
    echo Quick fix:
    echo   1. Install Node.js if missing
    echo   2. Run: npm install (in root directory)
    echo   3. Run: cd backend ^&^& npm install
    echo   4. Run this checker again
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
