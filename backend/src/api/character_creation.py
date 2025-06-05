"""
Character creation API for TextRealms.
"""
from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import Dict, List, Optional, Any
import uuid

from ..shared.character_creation_models import (
    CharacterCreationPreset,
    CharacterCreationSession,
    DefaultPresets
)
from ..shared.models import DomainType
from ..game_engine.character_creation import CharacterCreationService
from ..game_engine.game_engine import GameEngine
from ..game_engine.survival_system import SurvivalSystem
from ..game_engine.survival_integration import SurvivalIntegration


router = APIRouter(
    prefix="/character-creation",
    tags=["character-creation"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
game_engine = GameEngine()
survival_system = SurvivalSystem()
survival_integration = SurvivalIntegration(survival_system, game_engine)
character_creation_service = CharacterCreationService(
    survival_system=survival_system,
    survival_integration=survival_integration
)


@router.get("/presets")
async def get_presets():
    """Get all available character creation presets"""
    try:
        presets = character_creation_service.get_presets()
        return {
            "success": True,
            "presets": [preset.model_dump() for preset in presets]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get presets: {str(e)}")


@router.get("/preset/{preset_id}")
async def get_preset(preset_id: str):
    """Get a specific character creation preset"""
    preset = character_creation_service.get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")
    
    return {
        "success": True,
        "preset": preset.model_dump()
    }


@router.post("/presets")
async def create_preset(preset: CharacterCreationPreset = Body(...)):
    """Create a new character creation preset"""
    try:
        preset = character_creation_service.create_preset(preset)
        return {
            "success": True,
            "preset": preset.model_dump(),
            "message": "Preset created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create preset: {str(e)}")


@router.post("/sessions")
async def create_session(
    preset_id: str = Body(...),
    user_id: Optional[str] = Body(None)
):
    """Create a new character creation session"""
    try:
        session = character_creation_service.create_session(preset_id, user_id)
        return {
            "success": True,
            "session": session.model_dump(),
            "message": "Character creation session started"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get a character creation session"""
    session = character_creation_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    return {
        "success": True,
        "session": session.model_dump()
    }


@router.post("/session/{session_id}/domains")
async def update_domains(
    session_id: str,
    domain_allocations: Dict[DomainType, int] = Body(...)
):
    """Update domain allocations for a character creation session"""
    try:
        session = character_creation_service.update_domain_allocations(session_id, domain_allocations)
        
        # Also return validation status
        errors = character_creation_service.validate_session(session_id)
        
        return {
            "success": True,
            "session": session.model_dump(),
            "derived_stats": session.derived_stats,
            "is_valid": len(errors) == 0,
            "validation_errors": errors,
            "message": "Domain allocations updated"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update domains: {str(e)}")


@router.post("/session/{session_id}/tags")
async def update_tags(
    session_id: str,
    tag_allocations: Dict[str, int] = Body(...)
):
    """Update tag allocations for a character creation session"""
    try:
        session = character_creation_service.update_tag_allocations(session_id, tag_allocations)
        
        # Also return validation status
        errors = character_creation_service.validate_session(session_id)
        
        return {
            "success": True,
            "session": session.model_dump(),
            "is_valid": len(errors) == 0,
            "validation_errors": errors,
            "message": "Tag allocations updated"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tags: {str(e)}")


@router.post("/session/{session_id}/details")
async def update_details(
    session_id: str,
    name: Optional[str] = Body(None),
    background: Optional[str] = Body(None),
    character_class: Optional[str] = Body(None),
    traits: Optional[List[str]] = Body(None)
):
    """Update character details for a character creation session"""
    try:
        session = character_creation_service.update_character_details(
            session_id=session_id,
            name=name,
            background=background,
            character_class=character_class,
            traits=traits
        )
        
        # Also return validation status
        errors = character_creation_service.validate_session(session_id)
        
        return {
            "success": True,
            "session": session.model_dump(),
            "is_valid": len(errors) == 0,
            "validation_errors": errors,
            "message": "Character details updated"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character details: {str(e)}")


@router.post("/session/{session_id}/validate")
async def validate_session(session_id: str):
    """Validate a character creation session"""
    try:
        errors = character_creation_service.validate_session(session_id)
        
        return {
            "success": True,
            "is_valid": len(errors) == 0,
            "validation_errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate session: {str(e)}")


@router.post("/session/{session_id}/finalize")
async def finalize_character(session_id: str):
    """Finalize character creation and create the character"""
    try:
        # Validate the session first
        errors = character_creation_service.validate_session(session_id)
        if errors:
            return {
                "success": False,
                "is_valid": False,
                "validation_errors": errors,
                "message": "Character creation is not valid"
            }
        
        # Finalize the character
        result = character_creation_service.finalize_character(session_id)
        
        return {
            "success": True,
            "character": result["character"].model_dump(),
            "survival_state": result["survival_state"],
            "inventory": result["inventory"],
            "currency": result["currency"],
            "message": "Character created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to finalize character: {str(e)}")


@router.get("/ai-suggest/character")
async def ai_suggest_character(
    preset_id: str,
    character_concept: Optional[str] = Query(None),
    preferred_domains: Optional[List[DomainType]] = Query(None)
):
    """Get AI-suggested character based on concept and preferences"""
    try:
        # This would ideally use an AI system to generate character suggestions
        # For now, we'll return a placeholder message
        return {
            "success": True,
            "message": "AI character suggestion is not yet implemented",
            "suggested_concept": "This endpoint will be enhanced with AI generation capabilities in a future update."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI suggestion: {str(e)}")
