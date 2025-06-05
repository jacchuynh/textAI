#!/bin/bash
# Start script for the TextRealmsAI system with integrated AI GM Brain

echo "🎮 Starting TextRealmsAI with Advanced AI GM Brain..."

# Setup environment variables
export DATABASE_URL=${DATABASE_URL:-"postgresql://localhost:5432/textrealms_dev"}
export AI_GM_BRAIN_URL=${AI_GM_BRAIN_URL:-"http://localhost:8000"}
export PORT=${PORT:-3001}
export NODE_ENV=${NODE_ENV:-"development"}

# Default LLM settings (can be customized)
export LLM_PROVIDER=${LLM_PROVIDER:-"openai"}
export LLM_DEFAULT_MODEL=${LLM_DEFAULT_MODEL:-"gpt-4"}
export LLM_FAST_MODEL=${LLM_FAST_MODEL:-"gpt-3.5-turbo"}

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to start the AI GM Brain server
start_ai_gm_brain() {
    echo -e "${BLUE}🧠 Starting Advanced AI GM Brain server...${NC}"
    cd "$(dirname "$0")"
    
    # Activate virtual environment
    if [ -d "./ai_gm_venv" ]; then
        source ./ai_gm_venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found, using system Python${NC}"
    fi
    
    # Start AI GM Brain server in background
    python advanced_ai_gm_server.py &
    AI_GM_PID=$!
    
    echo -e "${GREEN}✅ AI GM Brain server started (PID: $AI_GM_PID)${NC}"
    
    # Wait for server to start
    sleep 2
    
    # Check if server is running
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ AI GM Brain server is healthy${NC}"
    else
        echo -e "${RED}❌ AI GM Brain server failed to start${NC}"
        exit 1
    fi
}

# Function to start the game server
start_game_server() {
    echo -e "${BLUE}🎲 Starting TextRealmsAI game server...${NC}"
    cd "$(dirname "$0")"
    
    # Start the game server
    DATABASE_URL=$DATABASE_URL PORT=$PORT npm run dev &
    GAME_SERVER_PID=$!
    
    echo -e "${GREEN}✅ Game server started (PID: $GAME_SERVER_PID)${NC}"
    
    # Wait for server to start
    sleep 5
    
    # Check if server is running
    if curl -s http://localhost:$PORT > /dev/null; then
        echo -e "${GREEN}✅ Game server is running${NC}"
    else
        echo -e "${RED}❌ Game server failed to start${NC}"
        exit 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}⚠️  Shutting down servers...${NC}"
    kill $AI_GM_PID $GAME_SERVER_PID 2>/dev/null
    exit 0
}

# Register the cleanup function
trap cleanup SIGINT SIGTERM

# Main process
echo -e "${BLUE}=== TextRealmsAI Integrated System ===${NC}"
echo -e "${YELLOW}Database URL: $DATABASE_URL${NC}"
echo -e "${YELLOW}AI GM Brain URL: $AI_GM_BRAIN_URL${NC}"
echo -e "${YELLOW}Game Server Port: $PORT${NC}"

# Start servers
start_ai_gm_brain
start_game_server

echo -e "${GREEN}=== TextRealmsAI System Started ===${NC}"
echo -e "${BLUE}🌐 Web interface: http://localhost:$PORT${NC}"
echo -e "${BLUE}🧠 AI GM Brain API: $AI_GM_BRAIN_URL${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep the script running
while true; do
    sleep 1
done
