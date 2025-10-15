@echo off
:: Quick aiosqlite installer
echo Installing aiosqlite...
cd backend
call venv\Scripts\activate
pip install aiosqlite==0.19.0
echo.
echo ✅ Done! Run: python verify_async_db.py to test
pause
