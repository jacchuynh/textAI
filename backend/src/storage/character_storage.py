"""
Character storage module for persisting character data.

This module handles loading and saving character data to the database.
"""
from typing import Dict, Optional, List, Any
import json
import os
from datetime import datetime

from ..shared.models import Character


# In-memory character cache for fast access
_character_cache: Dict[str, Character] = {}


def get_character(character_id: str) -> Optional[Character]:
    """
    Get a character by ID.
    
    Args:
        character_id: The ID of the character
        
    Returns:
        The character if found, None otherwise
    """
    # Check cache first
    if character_id in _character_cache:
        return _character_cache[character_id]
    
    # TODO: Replace with actual database query
    # For now, we'll just use a simple JSON file for simplicity
    character_file = os.path.join("data", "characters", f"{character_id}.json")
    if os.path.exists(character_file):
        try:
            with open(character_file, "r", encoding="utf-8") as f:
                character_data = json.load(f)
                character = Character.parse_obj(character_data)
                _character_cache[character_id] = character
                return character
        except Exception as e:
            print(f"Error loading character {character_id}: {e}")
    
    return None


def save_character(character: Character) -> bool:
    """
    Save a character to storage.
    
    Args:
        character: The character to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    character_id = str(character.id)
    
    # Update cache
    _character_cache[character_id] = character
    
    # TODO: Replace with actual database save
    # For now, we'll just use a simple JSON file for simplicity
    os.makedirs(os.path.join("data", "characters"), exist_ok=True)
    character_file = os.path.join("data", "characters", f"{character_id}.json")
    
    try:
        with open(character_file, "w", encoding="utf-8") as f:
            # Convert character to dict with model_dump() or dict()
            character_dict = character.dict() if hasattr(character, "dict") else character.model_dump()
            json.dump(character_dict, f, default=str, indent=2)
        return True
    except Exception as e:
        print(f"Error saving character {character_id}: {e}")
        return False


def delete_character(character_id: str) -> bool:
    """
    Delete a character from storage.
    
    Args:
        character_id: The ID of the character to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    # Remove from cache
    if character_id in _character_cache:
        del _character_cache[character_id]
    
    # TODO: Replace with actual database delete
    # For now, we'll just delete the JSON file
    character_file = os.path.join("data", "characters", f"{character_id}.json")
    if os.path.exists(character_file):
        try:
            os.remove(character_file)
            return True
        except Exception as e:
            print(f"Error deleting character {character_id}: {e}")
    
    return False


def list_characters(game_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all characters, optionally filtered by game.
    
    Args:
        game_id: Optional game ID to filter by
        
    Returns:
        List of character summary dictionaries
    """
    # TODO: Replace with actual database query
    # For now, we'll just list the JSON files
    character_dir = os.path.join("data", "characters")
    if not os.path.exists(character_dir):
        return []
    
    characters = []
    for filename in os.listdir(character_dir):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(character_dir, filename), "r", encoding="utf-8") as f:
                    character_data = json.load(f)
                    
                    # Filter by game_id if provided
                    if game_id and character_data.get("game_id") != game_id:
                        continue
                    
                    # Create a summary
                    summary = {
                        "id": character_data.get("id"),
                        "name": character_data.get("name"),
                        "class": character_data.get("class"),
                        "level": character_data.get("level", 1),
                        "game_id": character_data.get("game_id")
                    }
                    characters.append(summary)
            except Exception as e:
                print(f"Error loading character summary from {filename}: {e}")
    
    return characters