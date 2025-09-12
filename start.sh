#!/bin/bash

# AI Chat Integration Startup Script
# This script starts both the backend and frontend services

echo "🚀 Starting AI Chat Integration Services..."
echo "=============================================="

# Resolve project directories relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

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
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "❌ .env file not found in backend directory"
    echo "Please create it with your OpenAI API key:"
    echo "echo 'OPENAI_API_KEY=your_key_here' > $BACKEND_DIR/.env"
    exit 1
fi

echo "✅ .env file found"

# Start backend in background
echo "🔧 Starting backend server..."
cd "$BACKEND_DIR"
# Activate virtual environment if present (supports macOS/Linux and Windows layouts)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "ℹ️ Python virtual environment not found at $BACKEND_DIR/venv. Using system Python."
fi

# Install backend dependencies (pip on Windows, pip3 on macOS/Linux)
echo "📦 Installing backend dependencies (requirements.txt)..."
UNAME_OUT="$(uname -s 2>/dev/null || echo 'Unknown')"
case "$UNAME_OUT" in
    Darwin|Linux)
        PIP_CMD="pip3"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        PIP_CMD="pip"
        ;;
    *)
        PIP_CMD="pip3"
        ;;
esac
$PIP_CMD install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd "$FRONTEND_DIR"
# Install frontend dependencies
echo "📦 Installing frontend dependencies (npm i)..."
if [ ! -d "node_modules" ]; then
    npm i
else
    echo "node_modules already present; skipping npm i"
fi
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
