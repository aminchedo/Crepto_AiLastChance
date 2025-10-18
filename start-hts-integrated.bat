@echo off
echo Starting Bolt AI Crypto + HTS Trading System Integration
echo.

echo Starting Python Backend (Port 8000)...
start "Python Backend" cmd /k "cd backend && python main.py"

echo Starting Node.js HTS Backend (Port 3001)...
start "HTS Backend" cmd /k "cd backend-node && npm install && npm run dev"

echo Starting Frontend (Port 5173)...
start "Frontend" cmd /k "npm run dev"

echo.
echo All services starting...
echo - Python Backend: http://localhost:8000
echo - HTS Backend: http://localhost:3001
echo - Frontend: http://localhost:5173
echo.
echo Press any key to exit...
pause > nul