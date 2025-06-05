from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import Dict, List, Optional, Any
import uuid

from ..shared.survival_models import (
    SurvivalState, 
    SurvivalStateUpdate,
    CampaignSurvivalConfig,
    CampaignType,
    MoodState,
    ShelterQuality
)
from ..game_engine.survival_system import SurvivalSystem
from ..storage.survival_storage import SurvivalStorage
from ..narrative_engine.survival_integration import SurvivalNarrativeIntegration

# Initialize router
router = APIRouter(prefix="/survival", tags=["survival"])

# Initialize survival system and storage
storage = SurvivalStorage()
survival_system = SurvivalSystem(storage=storage)
narrative_integration = SurvivalNarrativeIntegration(survival_system=survival_system)


@router.post("/state/create")
async def create_survival_state(
    character_id: str = Body(...),
    campaign_id: Optional[str] = Body(None),
    base_health: Optional[int] = Body(None),
    body_domain_value: Optional[int] = Body(None)
):
    """Create a new survival state for a character
    
    Args:
        character_id: ID of the character
        campaign_id: Optional campaign ID to associate with
        base_health: Optional base health value for character creation
        body_domain_value: Optional Body domain value to use for health scaling
    """
    try:
        # Create survival state
        state = survival_system.create_survival_state(character_id)
        
        # If campaign ID is provided, associate with campaign config
        if campaign_id:
            # Check if campaign config exists
            config = survival_system.get_campaign_config(campaign_id)
            
            # If not, create default config
            if not config:
                config = survival_system.create_campaign_config(
                    campaign_id=campaign_id,
                    campaign_type=CampaignType.SURVIVAL
                )
        
        # Apply custom base health if provided
        if base_health is not None or body_domain_value is not None:
            # Use integration layer for full character data if available
            try:
                from ..game_engine.game_engine import GameEngine
                from ..game_engine.survival_integration import SurvivalIntegration
                
                game_engine = GameEngine()
                survival_integration = SurvivalIntegration(survival_system, game_engine)
                
                # Initialize with base_health
                state = survival_integration.initialize_character_survival(character_id, base_health)
            except ImportError:
                # Fall back to direct update if integration not available
                bv = body_domain_value if body_domain_value is not None else 1
                state.update_max_health_from_domain(bv, base_health)
        
        return {
            "success": True,
            "state": state.model_dump(),
            "health_stats": {
                "current_health": state.current_health,
                "max_health": state.max_health,
                "health_percentage": state.get_health_percentage()
            },
            "message": "Survival state created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create survival state: {str(e)}")


@router.get("/state/{character_id}")
async def get_survival_state(character_id: str):
    """Get a character's survival state"""
    state = survival_system.get_survival_state(character_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Survival state not found")
    
    return {
        "success": True,
        "state": state.model_dump()
    }


@router.post("/state/update/{character_id}")
async def update_survival_state(
    character_id: str,
    update: SurvivalStateUpdate = Body(...)
):
    """Update a character's survival state"""
    try:
        # Update survival state
        state = survival_system.update_survival_state(character_id, update)
        
        return {
            "success": True,
            "state": state.model_dump(),
            "message": "Survival state updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update survival state: {str(e)}")


@router.post("/action/{character_id}")
async def process_action(
    character_id: str,
    action_type: str = Body(...),
    environment: str = Body("normal")
):
    """Process an action's effect on survival state"""
    try:
        # Process action
        state, events = survival_system.process_action(character_id, action_type, environment)
        
        return {
            "success": True,
            "state": state.model_dump(),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process action: {str(e)}")


@router.post("/time/{character_id}")
async def process_time_passage(
    character_id: str,
    hours: float = Body(...),
    activity_level: str = Body("normal")
):
    """Process the passage of time on survival state"""
    try:
        # Process time passage
        state, events = survival_system.process_time_passage(character_id, hours, activity_level)
        
        return {
            "success": True,
            "state": state.model_dump(),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process time passage: {str(e)}")


@router.post("/consume/{character_id}")
async def consume_item(
    character_id: str,
    item_name: str = Body(...),
    quantity: int = Body(1)
):
    """Process consuming an item"""
    try:
        # Consume item
        state, events = survival_system.consume_item(character_id, item_name, quantity)
        
        return {
            "success": True,
            "state": state.model_dump(),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to consume item: {str(e)}")


@router.post("/campaign/config")
async def create_campaign_config(
    campaign_id: str = Body(...),
    campaign_type: CampaignType = Body(...)
):
    """Create a new campaign survival configuration"""
    try:
        # Create campaign config
        config = survival_system.create_campaign_config(campaign_id, campaign_type)
        
        return {
            "success": True,
            "config": config.model_dump(),
            "message": "Campaign config created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create campaign config: {str(e)}")


@router.get("/campaign/config/{campaign_id}")
async def get_campaign_config(campaign_id: str):
    """Get a campaign's survival configuration"""
    config = survival_system.get_campaign_config(campaign_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Campaign config not found")
    
    return {
        "success": True,
        "config": config.model_dump()
    }


@router.post("/narrative/context/{character_id}")
async def get_narrative_context(
    character_id: str,
    base_context: Dict = Body({})
):
    """Get narrative context with survival integration"""
    try:
        # Enhance narrative context
        enhanced_context = narrative_integration.enhance_narrative_context(base_context, character_id)
        
        return {
            "success": True,
            "context": enhanced_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get narrative context: {str(e)}")


@router.get("/narrative/hooks/{character_id}")
async def get_narrative_hooks(character_id: str):
    """Get narrative hooks based on survival state"""
    try:
        # Generate narrative hooks
        narrative = narrative_integration.generate_survival_narrative(character_id)
        
        return {
            "success": True,
            "narrative": narrative
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get narrative hooks: {str(e)}")


@router.get("/narrative/tags/{character_id}")
async def get_prompt_tags(character_id: str):
    """Get prompt tags based on survival state"""
    try:
        # Generate prompt tags
        tags = narrative_integration.generate_prompt_tags(character_id)
        
        return {
            "success": True,
            "tags": tags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prompt tags: {str(e)}")


@router.get("/critical-effects/{character_id}")
async def get_critical_effects(character_id: str):
    """Get critical state effects if any"""
    try:
        effect = narrative_integration.get_critical_state_effect(character_id)
        
        return {
            "success": True,
            "critical_effect": effect,
            "has_effect": effect is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get critical effects: {str(e)}")


@router.post("/update-max-health/{character_id}")
async def update_max_health(
    character_id: str, 
    body_value: Optional[int] = Body(None),
    base_health: Optional[int] = Body(None)
):
    """Update max health based on character's Body domain or provided value
    
    Args:
        character_id: ID of the character
        body_value: Optional Body domain value to use instead of fetching from character
        base_health: Optional base health value for character creation scaling
    """
    try:
        # Get current survival state
        state = survival_system.get_survival_state(character_id)
        if not state:
            raise HTTPException(status_code=404, detail="Survival state not found")
        
        if body_value is not None:
            # Use provided body value and optional base health
            state.update_max_health_from_domain(body_value, base_health)
        else:
            # Need to connect with game engine/character system
            # This requires the integration layer
            from ..game_engine.game_engine import GameEngine
            from ..game_engine.survival_integration import SurvivalIntegration
            
            game_engine = GameEngine()
            survival_integration = SurvivalIntegration(survival_system, game_engine)
            
            # Update max health using character data and optional base health
            updated_state = survival_integration.update_max_health_from_character(
                character_id, base_health=base_health
            )
            
            if not updated_state:
                raise HTTPException(
                    status_code=404, 
                    detail="Failed to update max health - character not found or missing Body domain"
                )
            
            state = updated_state
        
        return {
            "success": True,
            "state": state.model_dump(),
            "health_stats": {
                "current_health": state.current_health,
                "max_health": state.max_health,
                "health_percentage": state.get_health_percentage()
            },
            "message": "Max health updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update max health: {str(e)}")
