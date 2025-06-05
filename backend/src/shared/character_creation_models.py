"""
Character creation models for TextRealms.
"""
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any
from pydantic import BaseModel, Field, validator
import uuid
from datetime import datetime

from .models import DomainType, GrowthTier, TagCategory
from .character_presets import MagicTier


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
    
    # Equipment and starting inventory
    starting_items: Dict[str, int] = Field(default_factory=dict, description="Starting items and quantities")
    starting_currency: int = Field(default=0, description="Starting currency amount")
    
    # Magic system attributes
    has_mana_heart: bool = Field(default=False, description="Whether the character has a mana heart for internal magic")
    starting_mana: int = Field(default=0, description="Initial mana pool size")
    mana_regen_rate: float = Field(default=0.0, description="Rate of mana regeneration per unit time")
    starting_spells: List[str] = Field(default_factory=list, description="Initial spells known by character")
    starting_rituals: List[str] = Field(default_factory=list, description="Initial rituals known by character")
    magic_tier: Optional[MagicTier] = Field(default=None, description="Starting magic capability tier")
    ley_energy_sensitivity: int = Field(default=0, description="Ability to detect and channel leyline energy")
    
    @validator('domain_points')
    def validate_domain_points(cls, v):
        """Ensure domain points are within reasonable limits"""
        if v < 7:  # At least 1 per domain
            raise ValueError("Domain points must be at least 7 (1 per domain minimum)")
        return v
    
    @validator('max_per_domain')
    def validate_max_domain(cls, v, values):
        """Ensure max domain doesn't exceed total points"""
        if 'domain_points' in values and v > values['domain_points']:
            raise ValueError("Max per domain cannot exceed total domain points")
        return v


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
    
    # Validation state
    is_valid: bool = Field(default=False)
    validation_errors: List[str] = Field(default_factory=list)
    
    # Magic system fields
    magic_profile: Dict[str, Any] = Field(default_factory=dict, description="Magic user profile configuration")
    selected_spells: List[str] = Field(default_factory=list, description="Spells selected during character creation")
    selected_rituals: List[str] = Field(default_factory=list, description="Rituals selected during character creation")
    
    def calculate_derived_stats(self, preset: CharacterCreationPreset):
        """Calculate all derived stats based on domain allocations and preset formulas"""
        body_value = self.domain_allocations.get(DomainType.BODY, 0)
        spirit_value = self.domain_allocations.get(DomainType.SPIRIT, 0)
        mind_value = self.domain_allocations.get(DomainType.MIND, 0)
        awareness_value = self.domain_allocations.get(DomainType.AWARENESS, 0)
        
        self.derived_stats = {
            "max_health": preset.base_health + (body_value * preset.health_per_body),
            "max_clarity": preset.base_clarity + (spirit_value * preset.clarity_per_spirit),
            "max_stamina": preset.base_stamina + (body_value * preset.stamina_per_body),
            "max_focus": preset.base_focus + (mind_value * preset.focus_per_mind),
        }
        
        # Calculate magic-related stats if preset has magic capabilities
        if preset.has_mana_heart:
            # Calculate mana from MIND, SPIRIT, and AWARENESS
            magic_potential = (mind_value * 1.5) + (spirit_value * 1.5) + (awareness_value * 1.0)
            
            self.magic_profile = {
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
            self.derived_stats["mana_max"] = self.magic_profile["mana_max"]
            self.derived_stats["mana_current"] = self.magic_profile["mana_current"]
            self.derived_stats["mana_regen"] = self.magic_profile["mana_regeneration_rate"]
        
        return self.derived_stats
    
    def validate(self, preset: CharacterCreationPreset):
        """Validate that the character creation is complete and valid"""
        self.validation_errors = []
        total_allocated = sum(self.domain_allocations.values())
        
        # Check domain allocations
        if total_allocated != preset.domain_points:
            self.validation_errors.append(f"Domain points allocated ({total_allocated}) must equal preset total ({preset.domain_points})")
        
        # Check max per domain
        for domain, value in self.domain_allocations.items():
            if value > preset.max_per_domain:
                self.validation_errors.append(f"Domain {domain} exceeds maximum allowed ({value} > {preset.max_per_domain})")
            if value < preset.min_per_domain:
                self.validation_errors.append(f"Domain {domain} below minimum required ({value} < {preset.min_per_domain})")
        
        # Check for required character info
        if not self.character_name:
            self.validation_errors.append("Character name is required")
        
        # Validate magic selections for magic-capable characters
        if preset.has_mana_heart:
            mind_value = self.domain_allocations.get(DomainType.MIND, 0)
            spirit_value = self.domain_allocations.get(DomainType.SPIRIT, 0)
            
            # Check if there's a minimum requirement for magical domains
            if mind_value < 2 and spirit_value < 2:
                self.validation_errors.append("Magic users need at least 2 points in either MIND or SPIRIT domain")
            
            # Validate spell selections if they have chosen any
            if len(self.selected_spells) > 0:
                max_additional_spells = mind_value + spirit_value - 2  # -2 as base threshold
                if max_additional_spells < 0:
                    max_additional_spells = 0
                    
                allowed_spell_count = len(preset.starting_spells) + max_additional_spells
                if len(self.selected_spells) > allowed_spell_count:
                    self.validation_errors.append(f"Too many spells selected. Maximum allowed is {allowed_spell_count}")
        
        self.is_valid = len(self.validation_errors) == 0
        return self.is_valid


class DefaultPresets:
    """Default character creation presets"""
    
    @staticmethod
    def commoner() -> CharacterCreationPreset:
        """A humble, realistic start with limited skills."""
        return CharacterCreationPreset(
            name="Commoner",
            description="A humble, realistic start with limited skills.",
            campaign_type="realistic",
            domain_points=14,
            max_per_domain=3,
            min_per_domain=1,
            starting_tag_points=2,
            bonus_traits=[],
            starting_tier=GrowthTier.NOVICE,
            base_health=50,
            health_per_body=10,
            starting_items={"bread": 2, "water_flask": 1}
        )
    
    @staticmethod
    def adventurer() -> CharacterCreationPreset:
        """A balanced start with moderate skills and equipment."""
        return CharacterCreationPreset(
            name="Adventurer",
            description="A balanced start with moderate skills and equipment.",
            campaign_type="standard",
            domain_points=21,
            max_per_domain=5,
            min_per_domain=1,
            starting_tag_points=5,
            bonus_traits=["Traveler"],
            starting_tier=GrowthTier.SKILLED,
            base_health=75,
            health_per_body=15,
            starting_items={"bread": 4, "water_flask": 1, "torch": 2, "bedroll": 1},
            starting_currency=50
        )
    
    @staticmethod
    def veteran() -> CharacterCreationPreset:
        """An experienced character with specialized skills."""
        return CharacterCreationPreset(
            name="Veteran",
            description="An experienced character with specialized skills.",
            campaign_type="advanced",
            domain_points=28,
            max_per_domain=7,
            min_per_domain=2,
            starting_tag_points=8,
            bonus_traits=["Battle Scarred", "Survivor"],
            starting_tier=GrowthTier.EXPERT,
            base_health=100,
            health_per_body=20,
            starting_items={"rations": 6, "water_flask": 2, "torch": 4, "bedroll": 1, "bandages": 3},
            starting_currency=200
        )
    
    @staticmethod
    def hero() -> CharacterCreationPreset:
        """A legendary character with exceptional abilities."""
        return CharacterCreationPreset(
            name="Hero",
            description="A legendary character with exceptional abilities.",
            campaign_type="epic",
            domain_points=35,
            max_per_domain=9,
            min_per_domain=3,
            starting_tag_points=12,
            bonus_traits=["Chosen One", "Famous", "Heroic"],
            starting_tier=GrowthTier.MASTER,
            base_health=150,
            health_per_body=25,
            starting_items={"rations": 10, "water_flask": 2, "torch": 5, "bedroll": 1, "healing_potion": 3},
            starting_currency=500
        )
    
    @staticmethod
    def all_presets() -> List[CharacterCreationPreset]:
        """Get all default presets"""
        return [
            DefaultPresets.commoner(),
            DefaultPresets.adventurer(),
            DefaultPresets.veteran(),
            DefaultPresets.hero()
        ]
