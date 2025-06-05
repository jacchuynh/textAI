"""
Simplified character creation API for demo purposes.
"""
from fastapi import APIRouter, HTTPException, Body, status
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from shared.character_creation_models import CharacterCreationSession, CharacterCreationPreset, GrowthTier
from shared.magic_system import MagicTier, SpellComponent, SpellCategory, RitualType, ManaUtilization
from pydantic import BaseModel, Field

# Define spell and ritual libraries for demo purposes
SPELL_LIBRARY = {
    # Basic spells - Novice tier
    "light": {
        "name": "Light",
        "description": "Creates a small floating light that follows the caster.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.EVOCATION,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC],
        "mana_cost": 5,
        "difficulty": 1,
        "casting_time": "1 action",
        "duration": "1 hour",
        "range": "Self (10 ft radius)"
    },
    "detect_magic": {
        "name": "Detect Magic",
        "description": "Reveals magical auras and enchantments in the surrounding area.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.DIVINATION,
        "components": [SpellComponent.SOMATIC, SpellComponent.MENTAL],
        "mana_cost": 8,
        "difficulty": 2,
        "casting_time": "1 action",
        "duration": "Concentration, up to 10 minutes",
        "range": "30 ft radius"
    },
    "minor_healing": {
        "name": "Minor Healing",
        "description": "Seals minor wounds and eases pain, restoring a small amount of health.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.RESTORATION,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC],
        "mana_cost": 12,
        "difficulty": 2,
        "casting_time": "1 action",
        "duration": "Instantaneous",
        "range": "Touch"
    },
    
    # Academic spells
    "comprehend_language": {
        "name": "Comprehend Language",
        "description": "Allows understanding of one spoken or written language for the duration.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.DIVINATION,
        "components": [SpellComponent.VERBAL, SpellComponent.FOCUS],
        "mana_cost": 10,
        "difficulty": 2,
        "casting_time": "1 minute",
        "duration": "1 hour",
        "range": "Self"
    },
    
    # Mystic spells
    "sense_emotion": {
        "name": "Sense Emotion",
        "description": "Allows the caster to sense strong emotions from nearby creatures.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.DIVINATION,
        "components": [SpellComponent.MENTAL],
        "mana_cost": 7,
        "difficulty": 1,
        "casting_time": "1 action",
        "duration": "Concentration, up to 10 minutes",
        "range": "30 ft"
    },
    "guidance": {
        "name": "Guidance",
        "description": "Provides spiritual insight that grants a slight advantage on a single task.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.DIVINATION,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC],
        "mana_cost": 5,
        "difficulty": 1,
        "casting_time": "1 action",
        "duration": "Concentration, up to 1 minute",
        "range": "Touch"
    },
    "warding_gesture": {
        "name": "Warding Gesture",
        "description": "A quick protective gesture that provides minor protection against harm.",
        "tier": MagicTier.NOVICE,
        "category": SpellCategory.PROTECTION,
        "components": [SpellComponent.SOMATIC],
        "mana_cost": 8,
        "difficulty": 2,
        "casting_time": "1 reaction",
        "duration": "1 round",
        "range": "Self"
    },
    
    # Hero spells
    "heroic_surge": {
        "name": "Heroic Surge",
        "description": "Channels heroic energy to enhance physical abilities for a short time.",
        "tier": MagicTier.APPRENTICE,
        "category": SpellCategory.ALTERATION,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC],
        "mana_cost": 15,
        "difficulty": 3,
        "casting_time": "1 action",
        "duration": "1 minute",
        "range": "Self"
    },
    "healing_light": {
        "name": "Healing Light",
        "description": "Bathes an ally in restorative light, healing moderate wounds.",
        "tier": MagicTier.APPRENTICE,
        "category": SpellCategory.RESTORATION,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC, SpellComponent.FOCUS],
        "mana_cost": 20,
        "difficulty": 3,
        "casting_time": "1 action",
        "duration": "Instantaneous",
        "range": "30 ft"
    },
    "protective_aura": {
        "name": "Protective Aura",
        "description": "Creates a shimmering aura that helps deflect attacks.",
        "tier": MagicTier.APPRENTICE,
        "category": SpellCategory.PROTECTION,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC],
        "mana_cost": 18,
        "difficulty": 3,
        "casting_time": "1 action",
        "duration": "10 minutes",
        "range": "Self or touch"
    }
}

RITUAL_LIBRARY = {
    "commune_with_spirits": {
        "name": "Commune with Spirits",
        "description": "A ritual to connect with local spirits for guidance or information.",
        "tier": MagicTier.APPRENTICE,
        "type": RitualType.ETHEREAL,
        "components": [SpellComponent.VERBAL, SpellComponent.SOMATIC, SpellComponent.MATERIAL],
        "mana_cost": 25,
        "difficulty": 4,
        "casting_time": "10 minutes",
        "duration": "Up to 10 minutes",
        "materials_required": "Incense, ritual circle"
    }
}

class DomainType(str, Enum):
    BODY = "BODY"
    MIND = "MIND"
    SPIRIT = "SPIRIT"
    SOCIAL = "SOCIAL"
    CRAFT = "CRAFT" 
    AUTHORITY = "AUTHORITY"
    AWARENESS = "AWARENESS"

class GrowthTier(str, Enum):
    NOVICE = "NOVICE"
    SKILLED = "SKILLED"
    EXPERT = "EXPERT"
    MASTER = "MASTER"
    PARAGON = "PARAGON"

class CharacterCreationPreset(BaseModel):
    """Preset configuration for character creation based on campaign type"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    campaign_type: str
    domain_points: int = Field(ge=0, description="Total domain points to allocate")
    max_per_domain: int = Field(ge=0, description="Maximum points per domain")
    min_per_domain: int = Field(default=0, ge=0, description="Minimum points per domain")
    starting_tag_points: int = Field(ge=0, description="Points to allocate to tags")
    bonus_traits: List[str] = Field(default_factory=list, description="Free traits granted by this preset")
    starting_tier: GrowthTier = Field(default=GrowthTier.NOVICE, description="Starting growth tier")
    
    # Base health formula components
    base_health: int = Field(default=50, description="Base health value before domain modifiers")
    health_per_body: int = Field(default=10, description="Health points per BODY domain level")
    
    # Other derived stats formulas
    base_clarity: int = Field(default=20, description="Base clarity before domain modifiers")
    clarity_per_spirit: int = Field(default=5, description="Clarity points per SPIRIT domain level")
    
    base_stamina: int = Field(default=100, description="Base stamina before domain modifiers")
    stamina_per_body: int = Field(default=5, description="Stamina points per BODY domain level")
    
    base_focus: int = Field(default=20, description="Base focus before domain modifiers")
    focus_per_mind: int = Field(default=5, description="Focus points per MIND domain level")
    
    # Magic system attributes
    has_mana_heart: bool = Field(default=False, description="Whether the character has a mana heart for internal magic")
    starting_mana: int = Field(default=0, description="Initial mana pool size")
    mana_regen_rate: float = Field(default=0.0, description="Rate of mana regeneration per unit time")
    starting_spells: List[str] = Field(default_factory=list, description="Initial spells known by character")
    starting_rituals: List[str] = Field(default_factory=list, description="Initial rituals known by character")
    magic_tier: Optional[MagicTier] = Field(default=None, description="Starting magic capability tier")
    ley_energy_sensitivity: int = Field(default=0, description="Ability to detect and channel leyline energy")
    
    # Equipment and starting inventory
    starting_items: Dict[str, int] = Field(default_factory=dict, description="Starting items and quantities")
    starting_currency: int = Field(default=0, description="Starting currency amount")

class CharacterCreationSession(BaseModel):
    """Represents an in-progress character creation session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    preset_id: str
    preset: Optional[CharacterCreationPreset] = None
    started_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Allocation state
    domain_allocations: Dict[DomainType, int] = Field(default_factory=dict)
    tag_allocations: Dict[str, int] = Field(default_factory=dict)
    chosen_traits: List[str] = Field(default_factory=list)
    character_name: Optional[str] = None
    character_background: Optional[str] = None
    character_class: Optional[str] = None
    
    # Derived stats (calculated)
    derived_stats: Dict[str, Any] = Field(default_factory=dict)
    
    # Magic system fields
    magic_profile: Dict[str, Any] = Field(default_factory=dict, description="Magic user profile configuration")
    selected_spells: List[str] = Field(default_factory=list, description="Spells selected during character creation")
    selected_rituals: List[str] = Field(default_factory=list, description="Rituals selected during character creation")
    
    # Validation state
    is_valid: bool = Field(default=False)
    validation_errors: List[str] = Field(default_factory=list)

# Demo presets
def get_commoner_preset():
    return CharacterCreationPreset(
        name="Commoner",
        description="A humble, realistic start with limited skills.",
        campaign_type="slice_of_life",
        domain_points=10,  # Reduced from 14
        max_per_domain=2,  # Reduced from 3
        min_per_domain=1,
        starting_tag_points=2,
        bonus_traits=[],
        starting_tier=GrowthTier.NOVICE,
        base_health=45,
        health_per_body=8,
        base_clarity=15,
        clarity_per_spirit=4,
        base_stamina=80,
        stamina_per_body=4,
        base_focus=15,
        focus_per_mind=4,
        starting_items={"simple_clothes": 2, "rations": 3, "waterskin": 1},
        starting_currency=10,
        # No magic attributes - regular commoner
        has_mana_heart=False,
        starting_mana=0,
        mana_regen_rate=0.0
    )

def get_adventurer_preset():
    return CharacterCreationPreset(
        name="Adventurer",
        description="A balanced start with moderate skills and equipment. Perfect for traditional fantasy adventure campaigns.",
        campaign_type="exploration",
        domain_points=16,  # Reduced from 21
        max_per_domain=4,  # Reduced from 5
        min_per_domain=1,
        starting_tag_points=5,
        bonus_traits=["Traveler"],
        starting_tier=GrowthTier.NOVICE,
        base_health=60,
        health_per_body=10,
        base_clarity=20,
        clarity_per_spirit=5,
        base_stamina=100,
        stamina_per_body=5,
        base_focus=20,
        focus_per_mind=5,
        starting_items={"travelers_clothes": 1, "backpack": 1, "bedroll": 1, "rations": 5, "torch": 3, "waterskin": 1},
        starting_currency=50,
        # Minor magic capability
        has_mana_heart=False,  # But could develop one later
        starting_mana=0,
        mana_regen_rate=0.0
    )

def get_veteran_preset():
    return CharacterCreationPreset(
        name="Veteran",
        description="An experienced character with specialized skills from previous conflicts.",
        campaign_type="combat",
        domain_points=21,  # Reduced from 28
        max_per_domain=5,  # Reduced from 7
        min_per_domain=2,
        starting_tag_points=8,
        bonus_traits=["Battle Scarred", "Tactical Mind"],
        starting_tier=GrowthTier.SKILLED,  # One tier higher than normal
        base_health=80,
        health_per_body=12,
        base_clarity=25,
        clarity_per_spirit=6,
        base_stamina=120,
        stamina_per_body=7,
        base_focus=25,
        focus_per_mind=6,
        starting_items={"armor": 1, "weapon": 1, "healing_kit": 1, "rations": 7, "waterskin": 1, "bedroll": 1},
        starting_currency=100,
        # Some veterans have minor magical training
        has_mana_heart=False,
        starting_mana=0,
        mana_regen_rate=0.0
    )

def get_hero_preset():
    return CharacterCreationPreset(
        name="Hero",
        description="A legendary character with exceptional abilities and magical potential.",
        campaign_type="epic",
        domain_points=25,  # Reduced from 35
        max_per_domain=6,  # Reduced from 9
        min_per_domain=2,
        starting_tag_points=10,
        bonus_traits=["Chosen One", "Famous", "Heroic"],
        starting_tier=GrowthTier.SKILLED,  # Reduced from MASTER
        base_health=100,
        health_per_body=15,
        base_clarity=30,
        clarity_per_spirit=8,
        base_stamina=120,
        stamina_per_body=8,
        base_focus=30,
        focus_per_mind=8,
        starting_items={"heroic_garb": 1, "signature_weapon": 1, "magical_trinket": 1, "healing_potion": 2},
        starting_currency=200,
        # Magical capabilities
        has_mana_heart=True,
        starting_mana=40,
        mana_regen_rate=1.5,
        starting_spells=["heroic_surge", "healing_light", "protective_aura"],
        starting_rituals=[],
        magic_tier=MagicTier.APPRENTICE,
        ley_energy_sensitivity=2
    )

def get_scholar_preset():
    return CharacterCreationPreset(
        name="Scholar",
        description="An educated individual with specialized academic knowledge and basic magical training.",
        campaign_type="mystery",
        domain_points=15,  # Reduced from previous
        max_per_domain=4,
        min_per_domain=1,
        starting_tag_points=5,
        bonus_traits=["Well Read", "Analytical"],
        starting_tier=GrowthTier.NOVICE,
        base_health=40,
        health_per_body=7,
        base_clarity=30,  # Higher base clarity for magic
        clarity_per_spirit=8,  # Better clarity scaling
        base_stamina=60,
        stamina_per_body=3,
        base_focus=30,  # Higher base focus
        focus_per_mind=8,  # Better focus scaling
        starting_items={"books": 3, "writing_set": 1, "lantern": 1, "ink": 3, "parchment": 10},
        starting_currency=50,
        # Magic system integration
        has_mana_heart=True,
        starting_mana=30,
        mana_regen_rate=1.5,
        starting_spells=["detect_magic", "light", "comprehend_language"],
        starting_rituals=[],
        magic_tier=MagicTier.NOVICE,
        ley_energy_sensitivity=1
    )

def get_mystic_preset():
    return CharacterCreationPreset(
        name="Mystic",
        description="A spiritually attuned individual with supernatural insight or powers.",
        campaign_type="epic",
        domain_points=18,  # Reduced from 24
        max_per_domain=5,  # Reduced from 6
        min_per_domain=1,
        starting_tag_points=6,
        bonus_traits=["Spiritual Connection", "Intuitive"],
        starting_tier=GrowthTier.NOVICE,
        base_health=45,
        health_per_body=8,
        base_clarity=40,  # Very high base clarity
        clarity_per_spirit=10,  # Excellent clarity scaling
        base_stamina=70,
        stamina_per_body=4,
        base_focus=35,  # High base focus
        focus_per_mind=9,  # Excellent focus scaling
        starting_items={"ritual_robes": 1, "focus_item": 1, "incense": 5, "ritual_components": 3},
        starting_currency=40,
        # Magic system integration
        has_mana_heart=True,
        starting_mana=50,  # Higher starting mana
        mana_regen_rate=2.0,  # Better mana regen
        starting_spells=["sense_emotion", "guidance", "minor_healing", "warding_gesture"],
        starting_rituals=["commune_with_spirits"],
        magic_tier=MagicTier.APPRENTICE,  # Starts at apprentice level
        ley_energy_sensitivity=3  # Better at sensing leylines
    )

# Setup router
router = APIRouter(
    prefix="/character-creation",
    tags=["character-creation"],
    responses={404: {"description": "Not found"}},
)

# In-memory storage
presets = {
    "commoner": get_commoner_preset(),
    "adventurer": get_adventurer_preset(),
    "veteran": get_veteran_preset(),
    "hero": get_hero_preset(),
    "scholar": get_scholar_preset(),
    "mystic": get_mystic_preset()
}
sessions = {}

@router.get("/", response_model=List[str])
async def get_endpoints():
    """Get list of available endpoints"""
    return [
        "/presets",
        "/presets/{preset_name}",
        "/session/new",
        "/session/{session_id}",
        "/session/{session_id}/domains",
        "/session/{session_id}/details",
        "/session/{session_id}/magic",
        "/session/{session_id}/finalize",
        "/spells",
        "/rituals",
        "/spells/{spell_id}",
        "/rituals/{ritual_id}"
    ]

@router.get("/presets")
async def get_presets():
    """Get all available character creation presets"""
    return {
        "success": True,
        "presets": [preset.model_dump() for preset in presets.values()]
    }

@router.get("/preset/{preset_id}")
async def get_preset(preset_id: str):
    """Get a specific character creation preset"""
    if preset_id in presets:
        return {
            "success": True,
            "preset": presets[preset_id].model_dump()
        }
    raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")

@router.post("/sessions")
async def create_session(
    preset_id: str = Body(...),
    user_id: Optional[str] = Body(None)
):
    """Create a new character creation session"""
    if preset_id not in presets:
        raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")
    
    session = CharacterCreationSession(
        preset_id=preset_id,
        preset=presets[preset_id],
        user_id=user_id
    )
    
    # Initialize domain allocations with minimum values
    for domain in DomainType:
        session.domain_allocations[domain] = presets[preset_id].min_per_domain
    
    # Calculate derived stats
    body_value = session.domain_allocations.get(DomainType.BODY, 0)
    session.derived_stats = {
        "max_health": presets[preset_id].base_health + (body_value * presets[preset_id].health_per_body),
        "current_health": presets[preset_id].base_health + (body_value * presets[preset_id].health_per_body)
    }
    
    # Store the session
    sessions[session.id] = session
    
    return {
        "success": True,
        "session": session.model_dump(),
        "message": "Character creation session started"
    }

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get the current state of a character creation session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    session = sessions[session_id]
    preset = session.preset
    
    # Update validation status
    validation_errors = []
    total_allocated = sum(session.domain_allocations.values())
    
    # Basic validation checks
    if total_allocated != preset.domain_points:
        validation_errors.append(f"Domain points allocated ({total_allocated}) must equal preset total ({preset.domain_points})")
    
    for domain, value in session.domain_allocations.items():
        if value > preset.max_per_domain:
            validation_errors.append(f"Domain {domain.value} exceeds maximum allowed ({value} > {preset.max_per_domain})")
        if value < preset.min_per_domain:
            validation_errors.append(f"Domain {domain.value} below minimum required ({value} < {preset.min_per_domain})")
    
    if not session.character_name:
        validation_errors.append("Character name is required")
    
    # Magic-specific validation
    if preset.has_mana_heart:
        mind_value = session.domain_allocations.get(DomainType.MIND, 0)
        spirit_value = session.domain_allocations.get(DomainType.SPIRIT, 0)
        
        if mind_value < 2 and spirit_value < 2:
            validation_errors.append("Magic users need at least 2 points in either MIND or SPIRIT domain")
    
    session.is_valid = len(validation_errors) == 0
    session.validation_errors = validation_errors
    
    return {
        "success": True,
        "session": session.model_dump(),
        "is_valid": session.is_valid,
        "validation_errors": session.validation_errors
    }

@router.post("/session/{session_id}/domains")
async def update_domains(
    session_id: str,
    domain_allocations: Dict[str, int] = Body(...)
):
    """Update domain allocations for a character creation session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    session = sessions[session_id]
    preset = session.preset
    
    # Convert string keys to enum
    typed_allocations = {}
    for domain_str, value in domain_allocations.items():
        try:
            domain = DomainType(domain_str)
            typed_allocations[domain] = value
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid domain: {domain_str}")
    
    # Update allocations
    session.domain_allocations.update(typed_allocations)
    
    # Recalculate derived stats
    body_value = session.domain_allocations.get(DomainType.BODY, 0)
    spirit_value = session.domain_allocations.get(DomainType.SPIRIT, 0)
    mind_value = session.domain_allocations.get(DomainType.MIND, 0)
    awareness_value = session.domain_allocations.get(DomainType.AWARENESS, 0)
    
    session.derived_stats = {
        "max_health": preset.base_health + (body_value * preset.health_per_body),
        "current_health": preset.base_health + (body_value * preset.health_per_body),
        "max_clarity": preset.base_clarity + (spirit_value * preset.clarity_per_spirit),
        "current_clarity": preset.base_clarity + (spirit_value * preset.clarity_per_spirit),
        "max_stamina": preset.base_stamina + (body_value * preset.stamina_per_body),
        "current_stamina": preset.base_stamina + (body_value * preset.stamina_per_body),
        "max_focus": preset.base_focus + (mind_value * preset.focus_per_mind),
        "current_focus": preset.base_focus + (mind_value * preset.focus_per_mind)
    }
    
    # Calculate magic-related stats if preset has magic capabilities
    if preset.has_mana_heart:
        # Calculate mana from MIND, SPIRIT, and AWARENESS
        magic_potential = (mind_value * 1.5) + (spirit_value * 1.5) + (awareness_value * 1.0)
        
        session.magic_profile = {
            "has_mana_heart": preset.has_mana_heart,
            "mana_current": preset.starting_mana,
            "mana_max": preset.starting_mana + int(magic_potential * 5),
            "mana_regeneration_rate": preset.mana_regen_rate,
            "ley_energy_sensitivity": preset.ley_energy_sensitivity,
            "magic_tier": preset.magic_tier.value if preset.magic_tier else MagicTier.NOVICE.value,
            "corruption_level": 0,
            "known_spells": list(preset.starting_spells),
            "known_rituals": list(preset.starting_rituals)
        }
        
        # Add magic stats to derived stats
        session.derived_stats["mana_max"] = session.magic_profile["mana_max"]
        session.derived_stats["mana_current"] = session.magic_profile["mana_current"]
        session.derived_stats["mana_regen"] = session.magic_profile["mana_regeneration_rate"]
        
        # Initialize selected spells/rituals with preset starting values
        session.selected_spells = list(preset.starting_spells)
        session.selected_rituals = list(preset.starting_rituals)
    
    # Update timestamp
    session.updated_at = datetime.now()
    
    return {
        "success": True,
        "session": session.model_dump(),
        "derived_stats": session.derived_stats,
        "message": "Domain allocations updated"
    }

# Spell and ritual library endpoints
@router.get("/spells")
async def get_available_spells(
    tier: Optional[MagicTier] = None,
    category: Optional[SpellCategory] = None
):
    """Get list of available spells, optionally filtered by tier or category"""
    filtered_spells = {}
    
    for spell_id, spell_data in SPELL_LIBRARY.items():
        # Apply tier filter if specified
        if tier is not None and spell_data["tier"] != tier:
            continue
            
        # Apply category filter if specified
        if category is not None and spell_data["category"] != category:
            continue
            
        # Add spell to filtered results
        filtered_spells[spell_id] = spell_data
    
    return {
        "success": True,
        "spells": filtered_spells
    }

@router.get("/rituals")
async def get_available_rituals(
    tier: Optional[MagicTier] = None,
    ritual_type: Optional[RitualType] = None
):
    """Get list of available rituals, optionally filtered by tier or type"""
    filtered_rituals = {}
    
    for ritual_id, ritual_data in RITUAL_LIBRARY.items():
        # Apply tier filter if specified
        if tier is not None and ritual_data["tier"] != tier:
            continue
            
        # Apply type filter if specified
        if ritual_type is not None and ritual_data["type"] != ritual_type:
            continue
            
        # Add ritual to filtered results
        filtered_rituals[ritual_id] = ritual_data
    
    return {
        "success": True,
        "rituals": filtered_rituals
    }

@router.get("/spells/{spell_id}")
async def get_spell_details(spell_id: str):
    """Get detailed information about a specific spell"""
    if spell_id not in SPELL_LIBRARY:
        raise HTTPException(status_code=404, detail=f"Spell with ID {spell_id} not found")
    
    return {
        "success": True,
        "spell": SPELL_LIBRARY[spell_id]
    }

@router.get("/rituals/{ritual_id}")
async def get_ritual_details(ritual_id: str):
    """Get detailed information about a specific ritual"""
    if ritual_id not in RITUAL_LIBRARY:
        raise HTTPException(status_code=404, detail=f"Ritual with ID {ritual_id} not found")
    
    return {
        "success": True,
        "ritual": RITUAL_LIBRARY[ritual_id]
    }

@router.post("/session/{session_id}/details")
async def update_details(
    session_id: str,
    name: Optional[str] = Body(None),
    background: Optional[str] = Body(None),
    character_class: Optional[str] = Body(None),
    traits: Optional[List[str]] = Body(None)
):
    """Update character details for a character creation session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    session = sessions[session_id]
    
    # Update fields if provided
    if name is not None:
        session.character_name = name
    
    if background is not None:
        session.character_background = background
        
    if character_class is not None:
        session.character_class = character_class
    
    if traits is not None:
        session.chosen_traits = traits
    
    # Update timestamp
    session.updated_at = datetime.now()
    
    return {
        "success": True,
        "session": session.model_dump(),
        "message": "Character details updated"
    }

@router.post("/session/{session_id}/magic")
async def update_magic_selections(
    session_id: str,
    selected_spells: List[str] = Body([]),
    selected_rituals: List[str] = Body([])
):
    """Update magic spell and ritual selections for a character creation session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    session = sessions[session_id]
    preset = session.preset
    
    # Check if this character can use magic
    if not preset.has_mana_heart:
        return {
            "success": False,
            "message": "This character type does not have magical capabilities"
        }
    
    # Update spell and ritual selections
    session.selected_spells = selected_spells
    session.selected_rituals = selected_rituals
    
    # Validate selections based on domain allocations
    mind_value = session.domain_allocations.get(DomainType.MIND, 0)
    spirit_value = session.domain_allocations.get(DomainType.SPIRIT, 0)
    
    # Calculate allowed number of spells
    max_additional_spells = mind_value + spirit_value - 2  # -2 as base threshold
    if max_additional_spells < 0:
        max_additional_spells = 0
        
    allowed_spell_count = len(preset.starting_spells) + max_additional_spells
    
    # Validate
    errors = []
    if len(selected_spells) > allowed_spell_count:
        errors.append(f"Too many spells selected. Maximum allowed is {allowed_spell_count}")
    
    # Update the magic profile with new selections
    magic_potential = (mind_value * 1.5) + (spirit_value * 1.5) + \
                     session.domain_allocations.get(DomainType.AWARENESS, 0)
    
    session.magic_profile.update({
        "known_spells": selected_spells,
        "known_rituals": selected_rituals,
        "mana_max": preset.starting_mana + int(magic_potential * 5)
    })
    
    # Update session timestamp
    session.updated_at = datetime.now()
    
    return {
        "success": True if not errors else False,
        "session": session.model_dump(),
        "magic_profile": session.magic_profile,
        "errors": errors,
        "message": "Magic selections updated" if not errors else "Some magic selections were invalid"
    }

@router.post("/session/{session_id}/finalize")
async def finalize_character(session_id: str):
    """Finalize character creation and create the character"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")
    
    session = sessions[session_id]
    preset = session.preset
    
    # Perform validation (simplified)
    validation_errors = []
    total_allocated = sum(session.domain_allocations.values())
    
    # Check domain allocations
    if total_allocated != preset.domain_points:
        validation_errors.append(f"Domain points allocated ({total_allocated}) must equal preset total ({preset.domain_points})")
    
    # Check max per domain
    for domain, value in session.domain_allocations.items():
        if value > preset.max_per_domain:
            validation_errors.append(f"Domain {domain} exceeds maximum allowed ({value} > {preset.max_per_domain})")
        if value < preset.min_per_domain:
            validation_errors.append(f"Domain {domain} below minimum required ({value} < {preset.min_per_domain})")
    
    # Check for required character info
    if not session.character_name:
        validation_errors.append("Character name is required")
    
    # Validate magic selections for magic-capable characters
    if preset.has_mana_heart:
        mind_value = session.domain_allocations.get(DomainType.MIND, 0)
        spirit_value = session.domain_allocations.get(DomainType.SPIRIT, 0)
        
        # Check if there's a minimum requirement for magical domains
        if mind_value < 2 and spirit_value < 2:
            validation_errors.append("Magic users need at least 2 points in either MIND or SPIRIT domain")
    
    if validation_errors:
        return {
            "success": False,
            "message": "Character validation failed",
            "errors": validation_errors
        }
    
    # Create a character object (simplified for demo)
    character = {
        "id": str(uuid.uuid4()),
        "name": session.character_name,
        "background": session.character_background,
        "character_class": session.character_class,
        "traits": session.chosen_traits + preset.bonus_traits,
        "domain_values": {d.value: v for d, v in session.domain_allocations.items()},
        "derived_stats": session.derived_stats,
        "created_at": datetime.now().isoformat(),
        "growth_tier": preset.starting_tier.value,
        "preset_used": preset.name,
        "starting_items": preset.starting_items,
        "currency": preset.starting_currency
    }
    
    # Add magic profile if applicable
    if preset.has_mana_heart:
        character["magic_profile"] = session.magic_profile
        character["is_magic_user"] = True
        character["known_spells"] = session.selected_spells
        character["known_rituals"] = session.selected_rituals
    else:
        character["is_magic_user"] = False
        
    # Calculate remaining validation
    if session.validation_errors:
        return {
            "success": False,
            "message": "Character validation failed",
            "errors": session.validation_errors
        }
    
    return {
        "success": True,
        "character": character,
        "message": "Character created successfully"
    }
