
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
