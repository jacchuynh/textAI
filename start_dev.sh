#!/bin/bash

# TextRealmsAI Development Server Startup Script

echo "🎮 Starting TextRealmsAI Development Environment"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the TextRealmsAI root directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Install Python dependencies for AI GM Brain
echo "📦 Installing AI GM Brain dependencies..."
if [ ! -d "ai_gm_venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv ai_gm_venv
fi

source ai_gm_venv/bin/activate
pip install -r ai_gm_requirements.txt

# Start AI GM Brain server in background
echo "🧠 Starting AI GM Brain API server on port 8000..."
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use, skipping AI GM Brain server"
else
    python ai_gm_server.py &
    AI_GM_PID=$!
    echo "✅ AI GM Brain server started (PID: $AI_GM_PID)"
fi

# Wait a moment for the AI GM server to start
sleep 2

# Start the main Node.js server
echo "🚀 Starting main TypeScript server on port 3001..."
if check_port 3001; then
    echo "⚠️  Port 3001 is already in use"
    echo "Run: kill $(lsof -ti:3001) to stop existing server"
else
    PORT=3001 DATABASE_URL="postgresql://textrealmsai_user:jacc251203@localhost:5432/textrealmsai_db" npm run dev
fi

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$AI_GM_PID" ]; then
        kill $AI_GM_PID 2>/dev/null
        echo "✅ AI GM Brain server stopped"
    fi
    
    # Kill any remaining Python processes
    pkill -f "ai_gm_server.py" 2>/dev/null
    
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
echo ""
echo "🎮 TextRealmsAI is running!"
echo "   • Main server: http://localhost:3001"
echo "   • AI GM Brain API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"
wait
