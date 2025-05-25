"""
Magic System Core Models

This module defines the core Pydantic models for the magic system.
"""

import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from pydantic import BaseModel, Field

from monster_combat_test import Domain as DomainType
from backend.src.magic.models.magic_enums import (
    MagicSource, MagicTier, MagicSchool, ManaHeartStage,
    ElementType, SpellComplexity, EnchantmentType, MagicItemRarity
)


class ActiveMagicEffect(BaseModel):
    """
    Model representing an active magical effect on a character.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    source_spell_id: Optional[str] = None
    source_item_id: Optional[str] = None
    
    # Duration and timing
    duration_seconds: Optional[int] = None
    start_time: float  # Unix timestamp
    is_permanent: bool = False
    
    # Effect properties
    effect_type: str  # "buff", "debuff", "transformation", "utility", etc.
    effect_strength: float = 1.0
    effect_properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Attribute modifiers
    attribute_modifiers: Dict[str, float] = Field(default_factory=dict)
    domain_modifiers: Dict[DomainType, float] = Field(default_factory=dict)
    
    # Combat modifiers
    combat_modifiers: Dict[str, float] = Field(default_factory=dict)
    
    # Effect flags
    can_be_dispelled: bool = True
    is_visible: bool = True
    requires_concentration: bool = False


class MagicProfile(BaseModel):
    """
    Base magic profile for characters.
    """
    character_id: str
    magic_tier: MagicTier = MagicTier.SPIRITUAL_UTILITY
    mana_heart_stage: ManaHeartStage = ManaHeartStage.DORMANT
    
    # Magic sources and their strength (0.0 to 1.0)
    magic_sources: Dict[MagicSource, float] = Field(default_factory=dict)
    
    # School proficiencies (0.0 to 1.0)
    school_proficiencies: Dict[MagicSchool, float] = Field(default_factory=dict)
    
    # Elemental affinities (0.0 to 1.0)
    elemental_affinities: Dict[ElementType, float] = Field(default_factory=dict)
    
    # Current magical state
    current_mana: int = 0
    max_mana: int = 0
    mana_regeneration_rate: float = 1.0  # Points per minute
    
    # Known spells and abilities
    known_spells: List[str] = Field(default_factory=list)
    active_effects: Dict[str, ActiveMagicEffect] = Field(default_factory=dict)
    
    # Magic learning
    spell_learning_points: int = 0
    
    # Magical corruption and limitations
    corruption_level: float = 0.0
    corruption_effects: List[str] = Field(default_factory=list)
    corruption_threshold: float = 10.0
    
    # Magic item attunement
    attuned_items: List[str] = Field(default_factory=list)
    max_attunements: int = 3


class SpellComponent(BaseModel):
    """
    Model for a spell component requirement.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    component_type: str  # "material", "focus", "catalyst"
    is_consumed: bool = True
    quantity: int = 1
    rarity: str = "common"
    substitutes: List[str] = Field(default_factory=list)


class SpellDomainRequirement(BaseModel):
    """
    Model for domain requirements to cast a spell.
    """
    domain: DomainType
    minimum_level: int = 1
    scaling_factor: float = 0.1  # How much spell power scales with domain


class Spell(BaseModel):
    """
    Individual spell definition.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    school: MagicSchool
    tier: MagicTier
    complexity: SpellComplexity = SpellComplexity.SIMPLE
    
    # Visual and thematic elements
    visual_description: str = ""
    flavor_text: str = ""
    
    # Classification
    tags: List[str] = Field(default_factory=list)
    elements: List[ElementType] = Field(default_factory=list)
    
    # Requirements
    required_domain_levels: Dict[DomainType, int] = Field(default_factory=dict)
    required_sources: Dict[MagicSource, float] = Field(default_factory=dict)
    required_components: List[SpellComponent] = Field(default_factory=list)
    
    # Casting details
    mana_cost: int = 0
    casting_time_seconds: float = 1.0
    cooldown_seconds: Optional[float] = None
    
    # Effect details
    effect_type: str  # "enhancement", "damage", "utility", "social"
    base_power: float = 1.0
    duration_seconds: Optional[int] = None
    range_meters: float = 5.0
    area_of_effect_meters: float = 0.0
    
    # Domain scaling
    domain_scaling: List[SpellDomainRequirement] = Field(default_factory=list)
    
    # Special properties
    has_verbal_component: bool = True
    has_somatic_component: bool = True
    corruption_risk: float = 0.0
    
    # Learning
    is_teachable: bool = True
    learning_difficulty: int = 1  # 1-10 scale
    prerequisites: List[str] = Field(default_factory=list)  # Spell IDs
    
    # Advanced
    variable_mana_cost: bool = False
    max_mana_cost: Optional[int] = None
    
    def get_scaling_power(self, character_domains: Dict[DomainType, int]) -> float:
        """
        Calculate the scaled power of this spell based on character's domain levels.
        
        Args:
            character_domains: Dictionary of character's domain levels
            
        Returns:
            Scaled power value
        """
        scaled_power = self.base_power
        
        for domain_req in self.domain_scaling:
            domain = domain_req.domain
            if domain in character_domains:
                # Apply scaling based on how much the character exceeds the minimum
                excess_levels = max(0, character_domains[domain] - domain_req.minimum_level)
                scaled_power += excess_levels * domain_req.scaling_factor
        
        return scaled_power


class EnchantmentEffect(BaseModel):
    """
    Effect that can be applied through enchantment.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    enchantment_type: EnchantmentType
    
    # Effect properties
    power_level: float = 1.0
    effect_properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Item property modifiers
    attribute_bonuses: Dict[str, float] = Field(default_factory=dict)
    
    # Requirements for application
    required_item_types: List[str] = Field(default_factory=list)
    incompatible_effects: List[str] = Field(default_factory=list)


class EnchantmentRecipe(BaseModel):
    """
    Recipe for enchanting items.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Requirements
    required_craft_level: int = 1
    required_magic_tier: MagicTier = MagicTier.SPIRITUAL_UTILITY
    required_schools: Dict[MagicSchool, float] = Field(default_factory=dict)
    required_materials: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Process
    ritual_components: List[SpellComponent] = Field(default_factory=list)
    casting_time_minutes: int = 10
    
    # Output
    enchantment_effects: List[str] = Field(default_factory=list)  # Effect IDs
    success_rate_base: float = 0.7
    
    # Domain influences
    primary_domains: List[DomainType] = Field(default_factory=list)
    domain_bonuses: Dict[DomainType, float] = Field(default_factory=dict)


class MagicalItem(BaseModel):
    """
    A magical item with enchantments.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    item_type: str  # "weapon", "armor", "accessory", "focus", "consumable"
    base_item_id: Optional[str] = None  # Reference to non-magical base item
    
    # Item properties
    rarity: MagicItemRarity = MagicItemRarity.COMMON
    value: int = 0
    weight: float = 0.0
    
    # Magic properties
    magic_tier: MagicTier = MagicTier.SPIRITUAL_UTILITY
    enchantments: List[str] = Field(default_factory=list)  # Enchantment Effect IDs
    schools: List[MagicSchool] = Field(default_factory=list)
    charges: Optional[int] = None
    max_charges: Optional[int] = None
    recharge_method: Optional[str] = None
    
    # Usage requirements
    required_domains: Dict[DomainType, int] = Field(default_factory=dict)
    attunement_required: bool = False
    
    # Special properties
    unique: bool = False
    cursed: bool = False
    sentient: bool = False
    corruption_influence: float = 0.0


class SpellcastResult(BaseModel):
    """
    Result of a spellcasting attempt.
    """
    success: bool
    spell_id: str
    caster_id: str
    target_ids: List[str] = Field(default_factory=list)
    
    # Performance details
    mana_spent: int
    casting_time_actual: float  # Seconds
    power_level: float
    
    # Effect details
    effects_applied: List[Dict[str, Any]] = Field(default_factory=list)
    damage_dealt: Dict[str, float] = Field(default_factory=dict)
    healing_done: Dict[str, float] = Field(default_factory=dict)
    
    # Special outcomes
    critical_success: bool = False
    partial_success: bool = False
    failure_type: Optional[str] = None
    corruption_gained: float = 0.0
    
    # Narrative
    narrative_description: str = ""
    visible_effects: List[str] = Field(default_factory=list)


class ManaHeart(BaseModel):
    """
    Represents a character's mana heart development.
    """
    character_id: str
    stage: ManaHeartStage = ManaHeartStage.DORMANT
    
    # Core metrics
    purity: float = 1.0  # 0.0-1.0, affects spell efficacy
    stability: float = 1.0  # 0.0-1.0, affects corruption risk
    resonance: float = 0.0  # 0.0-1.0, affects elemental/domain synergies
    
    # Development metrics
    cultivation_progress: float = 0.0  # Progress toward next stage
    cultivation_threshold: float = 100.0  # Required for advancement
    breakthrough_attempts: int = 0
    
    # Special properties
    elemental_alignment: Optional[ElementType] = None
    domain_alignment: Optional[DomainType] = None
    
    # Advanced attributes (for higher stages)
    mana_channels: int = 1  # Number of concurrent spells possible
    mana_quality: float = 1.0  # Affects spell power
    regeneration_multiplier: float = 1.0  # Affects mana regeneration


class MagicLocation(BaseModel):
    """
    Represents a location with magical properties.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    
    # Magical properties
    magic_density: float = 0.5  # 0.0-1.0
    ambient_mana: float = 0.5  # 0.0-1.0
    corruption_level: float = 0.0  # 0.0-1.0
    
    # Dominant influences
    dominant_elements: Dict[ElementType, float] = Field(default_factory=dict)
    dominant_schools: Dict[MagicSchool, float] = Field(default_factory=dict)
    
    # Special properties
    ley_line_intersection: bool = False
    dimensional_thinness: float = 0.0  # 0.0-1.0, how close to other planes
    reality_stability: float = 1.0  # 0.0-1.0, affects spell predictability
    
    # Environmental effects
    environmental_effects: List[str] = Field(default_factory=list)
    spell_modifiers: Dict[MagicSchool, float] = Field(default_factory=dict)
    
    # Restrictions
    blocked_schools: List[MagicSchool] = Field(default_factory=list)
    enhanced_schools: List[MagicSchool] = Field(default_factory=list)