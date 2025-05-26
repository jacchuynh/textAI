
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import uuid

from ..shared.models import Character, DomainType
from ..game_engine.core import GameEngine
from ..storage.character_storage import save_character

# Initialize router
router = APIRouter(prefix="/game", tags=["game"])

# Create a game engine instance
game_engine = GameEngine()

# In-memory game storage (would use a database in production)
games: Dict[str, Dict[str, Any]] = {}


@router.post("/start")
async def start_game(
    name: str = Body(...),
    characterClass: str = Body(...),
    background: str = Body(...)
):
    """Start a new game with character creation"""
    try:
        # Create a new character
        character = game_engine.create_character(name)
        
        # Set character class and background
        character.character_class = characterClass
        character.background = background
        
        # Create a game ID
        game_id = str(uuid.uuid4())
        
        # Store the game state
        games[game_id] = {
            "gameId": game_id,
            "character": character,
            "status": "active"
        }
        
        # Save character to storage
        save_character(character)
        
        # Return the game data
        return {
            "gameId": game_id,
            "character": {
                "id": character.id,
                "name": character.name,
                "class": characterClass,
                "background": background,
                "level": 1,
                "xp": 0,
                "domains": {domain.type.value: domain.value for domain in character.domains.values()},
                "tags": list(character.tags.keys())
            },
            "location": {
                "name": "Starting Village",
                "description": "A peaceful village where your adventure begins."
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create character: {str(e)}")


@router.post("/send-input")
async def send_input(
    gameId: str = Body(...),
    input: str = Body(...)
):
    """Process player input and return AI response"""
    try:
        if gameId not in games:
            raise HTTPException(status_code=404, detail="Game not found")
        
        game_data = games[gameId]
        character = game_data["character"]
        
        # For now, return a simple response based on the input
        # In a full implementation, this would use the AI GM system
        
        # Generate a basic response
        narrative_response = f"You decide to {input.lower()}. "
        
        if "look" in input.lower() or "examine" in input.lower():
            narrative_response += "You take a moment to observe your surroundings. The village bustles with activity as merchants hawk their wares and children play in the streets."
        elif "talk" in input.lower() or "speak" in input.lower():
            narrative_response += "A friendly villager approaches you with a warm smile. 'Welcome, traveler! What brings you to our humble village?'"
        elif "explore" in input.lower() or "wander" in input.lower():
            narrative_response += "You begin to explore the area, discovering new paths and interesting locations. The adventure beckons!"
        elif "inventory" in input.lower() or "items" in input.lower():
            narrative_response += "You check your belongings. You carry the basic equipment of an adventurer - a simple weapon, some coins, and traveling supplies."
        else:
            narrative_response += "Your action ripples through the world, creating new possibilities for adventure."
        
        # Generate some choices based on the input
        choices = []
        if "talk" in input.lower():
            choices = [
                "Ask about local rumors",
                "Inquire about work opportunities", 
                "Ask for directions to interesting places"
            ]
        elif "explore" in input.lower():
            choices = [
                "Head to the town square",
                "Visit the local tavern",
                "Explore the outskirts of town"
            ]
        else:
            choices = [
                "Look around for opportunities",
                "Talk to nearby people",
                "Continue exploring"
            ]
        
        return {
            "response": {
                "narrative": narrative_response,
                "choices": choices,
                "combat": None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process input: {str(e)}")


@router.get("/{game_id}")
async def get_game(game_id: str):
    """Get game state by ID"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = games[game_id]
    character = game_data["character"]
    
    return {
        "gameId": game_id,
        "character": {
            "id": character.id,
            "name": character.name,
            "class": getattr(character, 'character_class', 'Adventurer'),
            "background": getattr(character, 'background', 'Commoner'),
            "level": 1,
            "xp": 0,
            "domains": {domain.type.value: domain.value for domain in character.domains.values()},
            "tags": list(character.tags.keys())
        },
        "location": {
            "name": "Starting Village",
            "description": "A peaceful village where your adventure begins."
        },
        "status": game_data["status"]
    }
