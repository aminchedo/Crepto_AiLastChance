@echo off
chcp 65001 > nul
title Crepto AI - Quick Launcher

echo.
echo ==================================================
echo    🚀 CREPTO AI - ONE-CLICK LAUNCHER
echo ==================================================
echo.
echo This will:
echo ✅ Run diagnostics
echo ✅ Install dependencies if needed
echo ✅ Stop existing servers
echo ✅ Start backend & frontend
echo ✅ Open application in browser
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

call crepto-toolbox.bat