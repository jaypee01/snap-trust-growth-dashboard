#!/bin/bash

# AI Chat Integration Startup Script
# This script starts both the backend and frontend services

echo "🚀 Starting AI Chat Integration Services..."
echo "=============================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Check if ports are available
echo "Checking port availability..."
check_port 8000 || exit 1
check_port 5173 || exit 1

# Check if .env file exists
if [ ! -f "/Users/neelkhalade/hackathon/snap-trust-growth-dashboard/backend/.env" ]; then
    echo "❌ .env file not found in backend directory"
    echo "Please create it with your OpenAI API key:"
    echo "echo 'OPENAI_API_KEY=your_key_here' > /Users/neelkhalade/hackathon/snap-trust-growth-dashboard/backend/.env"
    exit 1
fi

echo "✅ .env file found"

# Start backend in background
echo "🔧 Starting backend server..."
cd /Users/neelkhalade/hackathon/snap-trust-growth-dashboard/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd /Users/neelkhalade/hackathon/ai-credit-scorer
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started successfully!"
echo "=============================================="
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
