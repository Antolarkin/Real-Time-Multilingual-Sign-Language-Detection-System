#!/bin/bash

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap cleanup for SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "=================================================="
echo "   STARTING SIGN LANGUAGE RECOGNITION SYSTEM"
echo "=================================================="

# Check for MongoDB (Required for Login)
if ! pgrep -x "mongod" > /dev/null; then
    echo "WARNING: MongoDB is not running!"
    echo " - Login/Signup features will NOT work."
    echo " - Try running: brew services start mongodb-community"
    echo " - Or start mongod manually."
    echo "--------------------------------------------------"
    sleep 2
fi

# 0. Install Backend Dependencies (First run only check)
if [ ! -d "backend/node_modules" ]; then
    echo "[Init] Installing Auth Backend dependencies..."
    cd backend
    npm install
    cd ..
fi

# 1. Start Auth Backend (Node.js)
echo "[1/3] Starting Auth Backend (Port 3001)..."
cd backend
npm start &
AUTH_PID=$!
cd ..

# 2. Start ML Backend (Python)
echo "[2/3] Starting ML Backend (Port 8000)..."
> backend_debug.log # Clear previous log
./start_backend.sh > backend_debug.log 2>&1 &
ML_PID=$!

# Wait a moment for backends to initialize
sleep 3

# 3. Start Frontend (React)
echo "[3/3] Starting Frontend (Port 3000)..."
cd frontend
npm start &
FRONTEND_PID=$!

echo "=================================================="
echo "   SYSTEM RUNNING"
echo "   - Frontend:    http://localhost:3000"
echo "   - Auth API:    http://localhost:3001"
echo "   - ML API:      http://localhost:8000"
echo "=================================================="
echo "Press Ctrl+C to stop all services."

# Wait for all processes
wait $AUTH_PID $ML_PID $FRONTEND_PID
