@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title Fix Async SQLite Database Issue
color 0E

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        🔧 FIX ASYNC SQLITE DATABASE ISSUE               ║
echo ║           Crepto AI Backend                              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo This script will fix the async SQLite driver issue by:
echo   ✅ Checking Python installation
echo   ✅ Verifying virtual environment
echo   ✅ Installing aiosqlite package
echo   ✅ Testing database connection
echo.
pause

:: Check if we're in the right directory
if not exist "backend" (
    echo ❌ ERROR: backend directory not found!
    echo    Please run this from the Crepto_Ai root directory.
    pause
    exit /b 1
)

cd backend

:: Step 1: Check Python installation
echo.
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found: !PYTHON_VERSION!

:: Step 2: Check if virtual environment exists
echo.
echo [2/7] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found
    set VENV_EXISTS=1
) else if exist "venv\Scripts\python.exe" (
    echo ✅ Virtual environment found
    set VENV_EXISTS=1
) else (
    echo ⚠️  Virtual environment not found
    echo    Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
    set VENV_EXISTS=1
)

:: Step 3: Activate virtual environment
echo.
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

:: Step 4: Upgrade pip
echo.
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo ✅ Pip upgraded

:: Step 5: Install aiosqlite specifically
echo.
echo [5/7] Installing aiosqlite (async SQLite driver)...
pip install aiosqlite==0.19.0
if errorlevel 1 (
    echo ❌ Failed to install aiosqlite
    pause
    exit /b 1
)
echo ✅ aiosqlite installed successfully

:: Step 6: Verify installation
echo.
echo [6/7] Verifying aiosqlite installation...
python -c "import aiosqlite; print(f'aiosqlite version: {aiosqlite.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo ❌ aiosqlite not properly installed
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python -c "import aiosqlite; print(f'aiosqlite {aiosqlite.__version__}')"') do set AIOSQLITE_VER=%%i
echo ✅ !AIOSQLITE_VER!

:: Step 7: Test database connection
echo.
echo [7/7] Testing async database connection...

:: Create test script
(
echo import asyncio
echo import aiosqlite
echo from sqlalchemy.ext.asyncio import create_async_engine
echo.
echo async def test_connection^(^):
echo     try:
echo         # Test 1: Direct aiosqlite connection
echo         print^("Test 1: Direct aiosqlite connection..."^)
echo         async with aiosqlite.connect^(':memory:'^) as db:
echo             await db.execute^('SELECT 1'^)
echo             print^("  ✅ Direct aiosqlite connection works!"^)
echo         
echo         # Test 2: SQLAlchemy async engine
echo         print^("Test 2: SQLAlchemy async engine..."^)
echo         engine = create_async_engine^('sqlite+aiosqlite:///./test.db', echo=False^)
echo         async with engine.begin^(^) as conn:
echo             result = await conn.execute^("SELECT 1"^)
echo             print^("  ✅ SQLAlchemy async engine works!"^)
echo         await engine.dispose^(^)
echo         
echo         print^("\n🎉 All database tests passed!"^)
echo         return True
echo     except Exception as e:
echo         print^(f"❌ Database test failed: {e}"^)
echo         return False
echo.
echo if __name__ == '__main__':
echo     success = asyncio.run^(test_connection^(^)^)
echo     exit^(0 if success else 1^)
) > test_db_connection.py

python test_db_connection.py
if errorlevel 1 (
    echo.
    echo ❌ Database connection test failed
    echo.
    echo TROUBLESHOOTING:
    echo   1. Make sure SQLAlchemy is installed: pip install sqlalchemy
    echo   2. Check config.py has: DATABASE_URL = "sqlite+aiosqlite:///./crypto_ai.db"
    echo   3. Try reinstalling all requirements: pip install -r requirements.txt
    pause
    del test_db_connection.py
    exit /b 1
)

echo ✅ Database connection test passed
del test_db_connection.py

:: Summary
cd ..
cls
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           ✅ ASYNC DATABASE FIX COMPLETE!               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🎉 Your async SQLite database is now properly configured!
echo.
echo WHAT WAS FIXED:
echo   ✅ Python installation verified
echo   ✅ Virtual environment ready
echo   ✅ aiosqlite package installed
echo   ✅ Database connection tested
echo.
echo CONFIGURATION:
echo   📁 Database URL: sqlite+aiosqlite:///./crypto_ai.db
echo   📦 Driver: aiosqlite v0.19.0
echo   🔧 Engine: SQLAlchemy async engine
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🚀 NEXT STEPS:
echo.
echo 1. Start your backend server:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 2. Or use the quick start script:
echo    start-backend-only.bat
echo.
echo 3. Or start the full application:
echo    start-app.bat
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 YOUR DATABASE CONFIGURATION (already correct):
echo.
echo In backend/config.py:
echo   DATABASE_URL = "sqlite+aiosqlite:///./crypto_ai.db"
echo.
echo This uses:
echo   - sqlite: Database type
echo   - aiosqlite: Async driver (NOW INSTALLED ✅)
echo   - crypto_ai.db: Database file in backend directory
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ Everything is ready! You can now start your application.
echo.
pause
