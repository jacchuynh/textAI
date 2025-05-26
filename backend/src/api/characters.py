from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, List, Optional, Any

from ..shared.models import Character, DomainType, TagCategory
from ..game_engine.core import GameEngine

# Initialize router
router = APIRouter(prefix="/characters", tags=["characters"])

# Create a game engine instance (would be dependency injected in production)
game_engine = GameEngine()

# In-memory character storage (would use a database in production)
characters: Dict[str, Character] = {}


@router.post("/", response_model=Character)
async def create_character(name: str = Body(..., embed=True)):
    """Create a new character"""
    try:
        # Create character using game engine
        character = game_engine.create_character(name)
        
        # Store in memory
        characters[character.id] = character
        
        # Save to file storage (not database)
        from ..storage.character_storage import save_character
        save_success = save_character(character)
        
        if not save_success:
            print(f"Warning: Failed to save character {character.id} to file storage")
        
        return character
    except Exception as e:
        print(f"Error creating character: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create character: {str(e)}")


@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: str = Path(...)):
    """Get a character by ID"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    return characters[character_id]


@router.post("/{character_id}/actions", response_model=dict)
async def perform_action(
    character_id: str = Path(...),
    action_type: str = Body(...),
    domain: str = Body(...),
    tag: Optional[str] = Body(None),
    difficulty: int = Body(10)
):
    """Perform a character action using the domain system"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = characters[character_id]
    
    # Convert domain string to enum
    try:
        domain_type = DomainType(domain.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
    
    # Perform the action
    result = game_engine.perform_action(
        character=character,
        action_type=action_type,
        domain_type=domain_type,
        tag_name=tag,
        difficulty=difficulty
    )
    
    return result


@router.post("/{character_id}/tags/{tag_name}", response_model=Character)
async def add_tag(character_id: str = Path(...), tag_name: str = Path(...)):
    """Add a tag to a character"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = characters[character_id]
    success = game_engine.add_tag_to_character(character, tag_name)
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Tag '{tag_name}' not found or already added")
    
    return character


@router.get("/{character_id}/domains/drift", response_model=dict)
async def get_drift_options(
    character_id: str = Path(...),
    life_event: str = Body(..., embed=True)
):
    """Get domain drift options based on a life event"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = characters[character_id]
    drift_options = game_engine.process_domain_drift(character, life_event)
    
    return drift_options


@router.get("/{character_id}/shadow-profile", response_model=dict)
async def get_shadow_profile(character_id: str = Path(...)):
    """Get a character's shadow profile"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get the shadow profile
    profile_data = game_engine.get_character_shadow_profile(character_id)
    
    if "error" in profile_data:
        raise HTTPException(status_code=404, detail=profile_data["error"])
    
    return profile_data


@router.post("/{character_id}/domains/drift", response_model=Character)
async def apply_drift(
    character_id: str = Path(...),
    from_domain: str = Body(...),
    to_domain: str = Body(...),
):
    """Apply domain drift"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = characters[character_id]
    
    # Convert domain strings to enums
    try:
        from_domain_type = DomainType(from_domain.lower())
        to_domain_type = DomainType(to_domain.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid domain")
    
    success = game_engine.apply_domain_drift(
        character=character,
        from_domain=from_domain_type,
        to_domain=to_domain_type
    )
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Could not apply drift. Check that from_domain has at least 1 point and to_domain is not maxed out."
        )
    
    return character


@router.get("/tags/available", response_model=Dict[str, Any])
async def get_available_tags():
    """Get all available tags by category"""
    tags_by_category = {}
    
    for tag_name, tag in game_engine.standard_tags.items():
        category = tag.category.value
        if category not in tags_by_category:
            tags_by_category[category] = []
        
        tags_by_category[category].append({
            "name": tag.name,
            "id": tag_name,
            "domains": [d.value for d in tag.domains],
            "description": tag.description
        })
    
    return {"categories": tags_by_category}


@router.post("/{character_id}/detect-tags", response_model=Dict[str, Any])
async def detect_action_tags(
    character_id: str = Path(...),
    action_text: str = Body(..., embed=True)
):
    """Detect tags in an action description"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Detect tags
    tags = game_engine.detect_action_tags(action_text)
    
    return {"detected_tags": tags}


@router.post("/{character_id}/suggest-approach", response_model=Dict[str, Any])
async def suggest_action_approach(
    character_id: str = Path(...),
    action_text: str = Body(..., embed=True)
):
    """Suggest domain and tag for an action"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get character
    character = characters[character_id]
    
    # Get suggestions
    suggestion = game_engine.suggest_action_approach(action_text, character)
    
    return suggestion


@router.get("/{character_id}/shadow-profile", response_model=Dict[str, Any])
async def get_shadow_profile(character_id: str = Path(...)):
    """Get a character's shadow profile data"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get the shadow profile
    profile_data = game_engine.get_character_shadow_profile(character_id)
    
    if "error" in profile_data:
        raise HTTPException(status_code=404, detail=profile_data["error"])
    
    return profile_data


@router.post("/{character_id}/npc-reaction", response_model=Dict[str, Any])
async def get_npc_reaction(
    character_id: str = Path(...),
    npc_name: str = Body(...),
    recent_action: Optional[str] = Body(None)
):
    """Get an NPC's reaction to a character"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get the NPC reaction
    reaction = game_engine.get_npc_reaction_to_character(character_id, npc_name, recent_action)
    
    if "error" in reaction:
        raise HTTPException(status_code=404, detail=reaction["error"])
    
    return reaction