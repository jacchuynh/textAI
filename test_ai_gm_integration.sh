#!/bin/bash
# Test the integration between the game engine and the advanced AI GM Brain

echo "🧪 Testing AI GM Brain Integration"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
export DATABASE_URL="postgresql://localhost:5432/textrealms_dev"
export AI_GM_BRAIN_URL="http://localhost:8000"
export PORT=3001

echo -e "${BLUE}Configuration:${NC}"
echo -e "  Database URL: ${DATABASE_URL}"
echo -e "  AI GM Brain URL: ${AI_GM_BRAIN_URL}"
echo -e "  Game Server Port: ${PORT}"

# Test if AI GM Brain server is running
echo -e "\n${BLUE}Checking if AI GM Brain server is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
  echo -e "${GREEN}✓ AI GM Brain server is running${NC}"
else
  echo -e "${RED}✗ AI GM Brain server is not running${NC}"
  echo -e "${YELLOW}Starting AI GM Brain server...${NC}"
  
  # Start AI GM Brain server in the background
  cd "$(dirname "$0")" && source ai_gm_venv/bin/activate && python advanced_ai_gm_server.py &
  AI_GM_PID=$!
  
  # Wait for server to start
  sleep 2
  
  if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ AI GM Brain server started successfully${NC}"
  else
    echo -e "${RED}✗ Failed to start AI GM Brain server${NC}"
    exit 1
  fi
fi

# Test direct API call to AI GM Brain
echo -e "\n${BLUE}Testing direct API call to AI GM Brain...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/ai-gm/process-input \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "test_player",
    "input_text": "look around",
    "player_context": {
      "name": "Eldrin",
      "level": 5,
      "location_region": "Mystic Grove",
      "location_area": "Ancient Forest",
      "health": {"current": 100, "max": 100},
      "magic_profile": {"magicAffinity": "arcane", "knownAspects": ["basic", "elemental"], "spellPower": 25}
    }
  }')

echo -e "${GREEN}Response from AI GM Brain:${NC}"
echo "$RESPONSE" | python -m json.tool

# Run a few test commands through the game engine API (if running)
echo -e "\n${BLUE}Testing integration through game engine API...${NC}"
if curl -s http://localhost:3001/api/health > /dev/null; then
  echo -e "${GREEN}✓ Game server is running${NC}"
  
  # Test a natural language command
  echo -e "\n${BLUE}Testing natural language command: 'I want to explore the mysterious forest'${NC}"
  RESPONSE=$(curl -s -X POST http://localhost:3001/api/player/test_user/command \
    -H "Content-Type: application/json" \
    -d '{"command": "I want to explore the mysterious forest"}')
  echo -e "${GREEN}Game engine response:${NC}"
  echo "$RESPONSE" | python -m json.tool
  
  # Test a spell casting command
  echo -e "\n${BLUE}Testing spell command: 'cast fireball'${NC}"
  RESPONSE=$(curl -s -X POST http://localhost:3001/api/player/test_user/command \
    -H "Content-Type: application/json" \
    -d '{"command": "cast fireball"}')
  echo -e "${GREEN}Game engine response:${NC}"
  echo "$RESPONSE" | python -m json.tool
  
  # Test a lore question
  echo -e "\n${BLUE}Testing lore question: 'tell me about the history of this world'${NC}"
  RESPONSE=$(curl -s -X POST http://localhost:3001/api/player/test_user/command \
    -H "Content-Type: application/json" \
    -d '{"command": "tell me about the history of this world"}')
  echo -e "${GREEN}Game engine response:${NC}"
  echo "$RESPONSE" | python -m json.tool
  
else
  echo -e "${YELLOW}Game server is not running, skipping game engine integration tests${NC}"
fi

echo -e "\n${GREEN}Integration tests completed!${NC}"
