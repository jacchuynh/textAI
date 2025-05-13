"""
API endpoints for the combat system.

These endpoints handle:
- Starting combat encounters
- Processing player actions
- Getting combat state
- Ending combat
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..game_engine.combat_system import combat_system
from ..shared.models import Character
from ..storage.character_storage import get_character


router = APIRouter()


class StartCombatRequest(BaseModel):
    """Request model for starting combat."""
    character_id: str = Field(..., description="ID of the player character")
    enemy_template_id: int = Field(..., description="ID of the enemy template")
    level_override: Optional[int] = Field(None, description="Optional level override for the enemy")
    location_name: str = Field("Unknown", description="Name of the combat location")
    environment_factors: list[str] = Field(default_factory=list, description="List of environmental effects")
    surprise: bool = Field(False, description="Whether this is a surprise attack")
    game_id: Optional[str] = Field(None, description="Optional game ID for event tracking")


class CombatActionRequest(BaseModel):
    """Request model for a combat action."""
    combat_id: str = Field(..., description="ID of the combat")
    character_id: str = Field(..., description="ID of the player character")
    action_data: Dict[str, Any] = Field(..., description="Action data")


@router.post("/start")
async def start_combat(request: StartCombatRequest) -> Dict[str, Any]:
    """
    Start a new combat encounter.
    
    Args:
        request: Start combat request
        
    Returns:
        New combat state
    """
    # Get the character
    character = get_character(request.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    try:
        # Start combat
        combat_state = combat_system.start_combat(
            character=character,
            enemy_template_id=request.enemy_template_id,
            level_override=request.level_override,
            location_name=request.location_name,
            environment_factors=request.environment_factors,
            surprise=request.surprise,
            game_id=request.game_id
        )
        
        return combat_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start combat: {str(e)}")


@router.post("/action")
async def process_action(request: CombatActionRequest) -> Dict[str, Any]:
    """
    Process a player's combat action.
    
    Args:
        request: Combat action request
        
    Returns:
        Updated combat state
    """
    # Get the character
    character = get_character(request.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    try:
        # Get combat state
        combat_state = combat_system.get_combat_state(request.combat_id)
        if not combat_state:
            raise HTTPException(status_code=404, detail="Combat not found")
        
        # Process action
        updated_state = combat_system.process_combat_action(
            combat_id=request.combat_id,
            action_data=request.action_data,
            character=character
        )
        
        return updated_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process action: {str(e)}")


@router.get("/{combat_id}")
async def get_combat(combat_id: str) -> Dict[str, Any]:
    """
    Get the current state of a combat.
    
    Args:
        combat_id: The combat ID
        
    Returns:
        The combat state
    """
    combat_state = combat_system.get_combat_state(combat_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    return combat_state


@router.post("/{combat_id}/end")
async def end_combat(combat_id: str, game_id: Optional[str] = None) -> Dict[str, Any]:
    """
    End a combat encounter.
    
    Args:
        combat_id: The combat ID
        game_id: Optional game ID for event tracking
        
    Returns:
        The final combat state
    """
    final_state = combat_system.end_combat(combat_id, game_id)
    if not final_state:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    return final_state


@router.get("/{combat_id}/growth-log")
async def get_growth_log(combat_id: str) -> Dict[str, Any]:
    """
    Get the growth log for a combat.
    
    Args:
        combat_id: The combat ID
        
    Returns:
        The combat growth log
    """
    growth_log = combat_system.get_combat_growth_log(combat_id)
    
    return {
        "combat_id": combat_id,
        "growth_log": growth_log
    }