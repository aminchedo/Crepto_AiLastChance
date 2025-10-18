#!/bin/bash

echo "Starting Bolt AI Crypto + HTS Trading System Integration"
echo

echo "Starting Python Backend (Port 8000)..."
cd backend && python main.py &
PYTHON_PID=$!

echo "Starting Node.js HTS Backend (Port 3001)..."
cd ../backend-node && npm install && npm run dev &
NODE_PID=$!

echo "Starting Frontend (Port 5173)..."
cd .. && npm run dev &
FRONTEND_PID=$!

echo
echo "All services starting..."
echo "- Python Backend: http://localhost:8000"
echo "- HTS Backend: http://localhost:3001"
echo "- Frontend: http://localhost:5173"
echo
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "Stopping all services..."
    kill $PYTHON_PID 2>/dev/null
    kill $NODE_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup INT

# Wait for all background processes
wait