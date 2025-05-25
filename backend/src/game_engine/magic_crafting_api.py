"""
Magic Crafting API Endpoints

This module provides API endpoints for interacting with the
magic-crafting integration system.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from .magic_crafting_integration import create_magic_crafting_integration
from .magic_system import MagicSystem
from ..db.database import get_db
from ..player.auth import get_current_player

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/magic-crafting",
    tags=["magic-crafting"],
    responses={404: {"description": "Not found"}},
)

# Create magic system instance
magic_system = MagicSystem()

# Create magic crafting integration
magic_crafting = create_magic_crafting_integration(magic_system)


# ======================================================================
# Helper Functions
# ======================================================================

def get_character_skills(player_id: str, db: Session) -> Dict[str, int]:
    """
    Get character skills for a player
    In a real implementation, this would query the character skills from the database
    For now, we return some dummy skills
    """
    # In a real implementation, this would be:
    # return db.query(CharacterSkill).filter_by(player_id=player_id).first()
    
    # Dummy skills
    return {
        "crafting": 3,
        "alchemy": 2,
        "gathering": 4,
        "perception": 3,
        "tracking": 2,
        "nature_knowledge": 3
    }


# ======================================================================
# Material Endpoints
# ======================================================================

@router.get("/materials/regions/{region_id}/locations")
async def get_gathering_locations(
    region_id: str,
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get all discovered gathering locations in a region
    """
    try:
        locations = magic_crafting.get_gathering_locations(region_id)
        return {"success": True, "locations": locations}
    except Exception as e:
        logger.error(f"Error getting gathering locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/materials/regions/{region_id}/discover")
async def discover_gathering_location(
    region_id: str,
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Attempt to discover a new gathering location in a region
    """
    try:
        player_id = current_player["id"]
        magic_profile = magic_system.get_player_profile(player_id)
        character_skills = get_character_skills(player_id, db)
        
        result = magic_crafting.discover_gathering_location(
            player_id, region_id, character_skills, magic_profile)
        
        return result
    except Exception as e:
        logger.error(f"Error discovering gathering location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/materials/locations/{location_id}/gather")
async def gather_materials(
    location_id: str,
    tool_id: Optional[str] = None,
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Gather magical materials from a location
    """
    try:
        player_id = current_player["id"]
        magic_profile = magic_system.get_player_profile(player_id)
        character_skills = get_character_skills(player_id, db)
        
        result = magic_crafting.gather_materials(
            player_id, location_id, character_skills, magic_profile, tool_id)
        
        return result
    except Exception as e:
        logger.error(f"Error gathering materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/materials/inventory")
async def get_player_materials(
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get all materials owned by a player
    """
    try:
        player_id = current_player["id"]
        materials = magic_crafting.get_player_materials(player_id)
        return {"success": True, "materials": materials}
    except Exception as e:
        logger.error(f"Error getting player materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/materials/{instance_id}/process")
async def process_material(
    instance_id: str,
    processing_type: str = Body(..., embed=True),
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Process a material to enhance its properties
    """
    try:
        player_id = current_player["id"]
        magic_profile = magic_system.get_player_profile(player_id)
        character_skills = get_character_skills(player_id, db)
        
        # Validate processing type
        valid_types = ["refine", "extract", "enchant"]
        if processing_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid processing type. Must be one of: {', '.join(valid_types)}")
        
        result = magic_crafting.process_material(
            player_id, instance_id, processing_type, character_skills, magic_profile)
        
        return result
    except Exception as e:
        logger.error(f"Error processing material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# Crafting Station Endpoints
# ======================================================================

@router.get("/stations/regions/{region_id}")
async def get_crafting_stations(
    region_id: str,
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get all crafting stations in a region
    """
    try:
        stations = magic_crafting.get_crafting_stations(region_id)
        return {"success": True, "stations": stations}
    except Exception as e:
        logger.error(f"Error getting crafting stations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stations/{station_id}/craft")
async def craft_item_with_magic(
    station_id: str,
    recipe_id: str = Body(..., embed=True),
    material_ids: List[str] = Body(..., embed=True),
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Craft an item with magical enhancement from a leyline crafting station
    """
    try:
        player_id = current_player["id"]
        magic_profile = magic_system.get_player_profile(player_id)
        character_skills = get_character_skills(player_id, db)
        
        # Get material instances
        materials = []
        for material_id in material_ids:
            # In a real implementation, this would query the database
            # material_instance = db.query(MagicalMaterialInstance).filter_by(id=material_id).first()
            # For now, we'll create a dummy material instance
            materials.append({"material_id": material_id, "quantity": 1, "quality": 1.0})
        
        result = magic_crafting.craft_item_with_magic(
            player_id, station_id, recipe_id, materials, magic_profile, character_skills)
        
        return result
    except Exception as e:
        logger.error(f"Error crafting item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# Enchantment Endpoints
# ======================================================================

@router.get("/enchantments/available")
async def get_available_enchantments(
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get enchantments available to a player based on their magic abilities
    """
    try:
        player_id = current_player["id"]
        magic_profile = magic_system.get_player_profile(player_id)
        
        enchantments = magic_crafting.get_available_enchantments(player_id, magic_profile)
        return {"success": True, "enchantments": enchantments}
    except Exception as e:
        logger.error(f"Error getting available enchantments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enchantments/apply")
async def apply_enchantment(
    item_id: str = Body(..., embed=True),
    enchantment_id: str = Body(..., embed=True),
    material_ids: List[str] = Body(..., embed=True),
    location_id: Optional[str] = Body(None, embed=True),
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Apply an enchantment to a crafted item
    """
    try:
        player_id = current_player["id"]
        
        # Get materials
        materials = []
        for material_id in material_ids:
            # In a real implementation, this would query the database
            # material_instance = db.query(MagicalMaterialInstance).filter_by(id=material_id).first()
            # For now, we'll create a dummy material instance
            materials.append({"material_id": material_id, "quantity": 1, "quality": 1.0})
        
        # Get location data if provided
        location = None
        if location_id:
            # In a real implementation, this would query the database
            # location = db.query(MagicalGatheringLocation).filter_by(id=location_id).first()
            # For now, we'll create dummy location data
            location = {"id": location_id, "leyline_strength": 1.5, "magical_aura": "FIRE"}
        
        result = magic_crafting.apply_enchantment(
            player_id, item_id, enchantment_id, materials, location)
        
        return result
    except Exception as e:
        logger.error(f"Error applying enchantment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enchanted-items")
async def get_enchanted_items(
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get all enchanted items owned by a player
    """
    try:
        player_id = current_player["id"]
        items = magic_crafting.get_enchanted_items(player_id)
        return {"success": True, "items": items}
    except Exception as e:
        logger.error(f"Error getting enchanted items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enchanted-items/{item_id}/use-charge")
async def use_enchanted_item_charge(
    item_id: str,
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Use a charge from an enchanted item
    """
    try:
        result = magic_crafting.use_enchanted_item_charge(item_id)
        return result
    except Exception as e:
        logger.error(f"Error using enchanted item charge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================================
# System Maintenance Endpoints
# ======================================================================

@router.post("/system/refresh", include_in_schema=False)
async def refresh_all_systems(
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Refresh all magic-crafting systems
    This endpoint is admin-only and not included in the API schema
    """
    # Check if player is an admin
    if current_player.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = magic_crafting.refresh_all_systems()
        return result
    except Exception as e:
        logger.error(f"Error refreshing systems: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/performance", include_in_schema=False)
async def get_performance_stats(
    current_player: Dict[str, Any] = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Get performance statistics for the integration
    This endpoint is admin-only and not included in the API schema
    """
    # Check if player is an admin
    if current_player.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        stats = magic_crafting.get_performance_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))