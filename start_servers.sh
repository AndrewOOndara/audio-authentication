#!/bin/bash

# Audio Authenticity MVP - Startup Script
echo "🎧 Starting Audio Authenticity MVP..."

# Function to start backend
start_backend() {
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
}

# Start both servers
start_backend
sleep 3
start_frontend

echo ""
echo "✅ Both servers are starting up!"
echo "📡 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap 'echo "Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait
