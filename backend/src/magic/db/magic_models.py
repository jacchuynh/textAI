"""
Magic System Database Models

This module defines the SQLAlchemy database models for the magic system.
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    ForeignKey, DateTime, Text, JSON, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from backend.src.database.base import Base
from backend.src.magic.models.magic_enums import (
    MagicSource, MagicTier, MagicSchool, ManaHeartStage,
    ElementType, SpellComplexity, EnchantmentType, MagicItemRarity
)


class DBMagicProfile(Base):
    """Database model for a character's magic profile."""
    __tablename__ = "magic_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String, nullable=False, index=True)
    magic_tier = Column(Enum(MagicTier), nullable=False, default=MagicTier.SPIRITUAL_UTILITY)
    mana_heart_stage = Column(Enum(ManaHeartStage), nullable=False, default=ManaHeartStage.DORMANT)
    
    # JSON fields for complex data
    magic_sources = Column(JSON, nullable=False, default=dict)
    school_proficiencies = Column(JSON, nullable=False, default=dict)
    elemental_affinities = Column(JSON, nullable=False, default=dict)
    
    # Mana and resources
    current_mana = Column(Integer, nullable=False, default=0)
    max_mana = Column(Integer, nullable=False, default=0)
    mana_regeneration_rate = Column(Float, nullable=False, default=1.0)
    spell_learning_points = Column(Integer, nullable=False, default=0)
    
    # Corruption data
    corruption_level = Column(Float, nullable=False, default=0.0)
    corruption_effects = Column(JSON, nullable=False, default=list)
    corruption_threshold = Column(Float, nullable=False, default=10.0)
    
    # Attunement
    max_attunements = Column(Integer, nullable=False, default=3)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    known_spells = relationship("DBCharacterKnownSpell", back_populates="magic_profile", cascade="all, delete-orphan")
    active_effects = relationship("DBActiveEffect", back_populates="magic_profile", cascade="all, delete-orphan")
    mana_heart = relationship("DBManaHeart", back_populates="magic_profile", uselist=False, cascade="all, delete-orphan")
    attuned_items = relationship("DBAttunedItem", back_populates="magic_profile", cascade="all, delete-orphan")


class DBManaHeart(Base):
    """Database model for a character's mana heart."""
    __tablename__ = "mana_hearts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String, nullable=False, index=True)
    magic_profile_id = Column(String, ForeignKey("magic_profiles.id"), nullable=False)
    stage = Column(Enum(ManaHeartStage), nullable=False, default=ManaHeartStage.DORMANT)
    
    # Core metrics
    purity = Column(Float, nullable=False, default=1.0)
    stability = Column(Float, nullable=False, default=1.0)
    resonance = Column(Float, nullable=False, default=0.0)
    
    # Development metrics
    cultivation_progress = Column(Float, nullable=False, default=0.0)
    cultivation_threshold = Column(Float, nullable=False, default=100.0)
    breakthrough_attempts = Column(Integer, nullable=False, default=0)
    
    # Alignments
    elemental_alignment = Column(Enum(ElementType), nullable=True)
    domain_alignment = Column(String, nullable=True)  # Using string for domain type
    
    # Advanced attributes
    mana_channels = Column(Integer, nullable=False, default=1)
    mana_quality = Column(Float, nullable=False, default=1.0)
    regeneration_multiplier = Column(Float, nullable=False, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    magic_profile = relationship("DBMagicProfile", back_populates="mana_heart")
    cultivation_history = relationship("DBManaHeartCultivationEvent", back_populates="mana_heart", cascade="all, delete-orphan")


class DBManaHeartCultivationEvent(Base):
    """Database model for tracking mana heart cultivation progress events."""
    __tablename__ = "mana_heart_cultivation_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mana_heart_id = Column(String, ForeignKey("mana_hearts.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "practice", "breakthrough", "setback"
    
    # Event details
    progress_gained = Column(Float, nullable=False, default=0.0)
    description = Column(Text, nullable=True)
    
    # Context
    location = Column(String, nullable=True)
    related_spell_id = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    mana_heart = relationship("DBManaHeart", back_populates="cultivation_history")


class DBSpell(Base):
    """Database model for a spell definition."""
    __tablename__ = "spells"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    school = Column(Enum(MagicSchool), nullable=False)
    tier = Column(Enum(MagicTier), nullable=False)
    complexity = Column(Enum(SpellComplexity), nullable=False, default=SpellComplexity.SIMPLE)
    
    # Visual and thematic elements
    visual_description = Column(Text, nullable=True)
    flavor_text = Column(Text, nullable=True)
    
    # Classification
    tags = Column(JSON, nullable=False, default=list)
    elements = Column(JSON, nullable=False, default=list)  # List of ElementType strings
    
    # Requirements
    required_domain_levels = Column(JSON, nullable=False, default=dict)
    required_sources = Column(JSON, nullable=False, default=dict)
    
    # Casting details
    mana_cost = Column(Integer, nullable=False, default=0)
    casting_time_seconds = Column(Float, nullable=False, default=1.0)
    cooldown_seconds = Column(Float, nullable=True)
    
    # Effect details
    effect_type = Column(String, nullable=False)
    base_power = Column(Float, nullable=False, default=1.0)
    duration_seconds = Column(Integer, nullable=True)
    range_meters = Column(Float, nullable=False, default=5.0)
    area_of_effect_meters = Column(Float, nullable=False, default=0.0)
    
    # Special properties
    has_verbal_component = Column(Boolean, nullable=False, default=True)
    has_somatic_component = Column(Boolean, nullable=False, default=True)
    corruption_risk = Column(Float, nullable=False, default=0.0)
    
    # Learning
    is_teachable = Column(Boolean, nullable=False, default=True)
    learning_difficulty = Column(Integer, nullable=False, default=1)
    
    # Advanced
    variable_mana_cost = Column(Boolean, nullable=False, default=False)
    max_mana_cost = Column(Integer, nullable=True)
    
    # System
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    components = relationship("DBSpellComponent", back_populates="spell", cascade="all, delete-orphan")
    domain_scaling = relationship("DBSpellDomainScaling", back_populates="spell", cascade="all, delete-orphan")
    prerequisites = relationship("DBSpellPrerequisite", back_populates="spell", cascade="all, delete-orphan")
    known_by = relationship("DBCharacterKnownSpell", back_populates="spell")


class DBSpellComponent(Base):
    """Database model for a spell component."""
    __tablename__ = "spell_components"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    spell_id = Column(String, ForeignKey("spells.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    component_type = Column(String, nullable=False)  # "material", "focus", "catalyst"
    is_consumed = Column(Boolean, nullable=False, default=True)
    quantity = Column(Integer, nullable=False, default=1)
    rarity = Column(String, nullable=False, default="common")
    substitutes = Column(JSON, nullable=False, default=list)
    
    # Relationships
    spell = relationship("DBSpell", back_populates="components")


class DBSpellDomainScaling(Base):
    """Database model for how a spell scales with domains."""
    __tablename__ = "spell_domain_scaling"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    spell_id = Column(String, ForeignKey("spells.id"), nullable=False)
    domain = Column(String, nullable=False)  # Domain name as string
    minimum_level = Column(Integer, nullable=False, default=1)
    scaling_factor = Column(Float, nullable=False, default=0.1)
    
    # Relationships
    spell = relationship("DBSpell", back_populates="domain_scaling")


class DBSpellPrerequisite(Base):
    """Database model for spell prerequisites."""
    __tablename__ = "spell_prerequisites"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    spell_id = Column(String, ForeignKey("spells.id"), nullable=False)
    prerequisite_spell_id = Column(String, ForeignKey("spells.id"), nullable=False)
    
    # Relationships
    spell = relationship("DBSpell", back_populates="prerequisites", foreign_keys=[spell_id])
    prerequisite_spell = relationship("DBSpell", foreign_keys=[prerequisite_spell_id])


class DBCharacterKnownSpell(Base):
    """Database model for spells known by a character."""
    __tablename__ = "character_known_spells"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    magic_profile_id = Column(String, ForeignKey("magic_profiles.id"), nullable=False)
    spell_id = Column(String, ForeignKey("spells.id"), nullable=False)
    proficiency = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0
    date_learned = Column(DateTime, nullable=False, default=datetime.utcnow)
    custom_modifications = Column(JSON, nullable=True)
    
    # Relationships
    magic_profile = relationship("DBMagicProfile", back_populates="known_spells")
    spell = relationship("DBSpell", back_populates="known_by")


class DBActiveEffect(Base):
    """Database model for active magical effects on a character."""
    __tablename__ = "active_effects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    magic_profile_id = Column(String, ForeignKey("magic_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    source_spell_id = Column(String, ForeignKey("spells.id"), nullable=True)
    source_item_id = Column(String, nullable=True)
    
    # Duration and timing
    duration_seconds = Column(Integer, nullable=True)
    start_time = Column(Float, nullable=False)  # Unix timestamp
    is_permanent = Column(Boolean, nullable=False, default=False)
    
    # Effect properties
    effect_type = Column(String, nullable=False)
    effect_strength = Column(Float, nullable=False, default=1.0)
    effect_properties = Column(JSON, nullable=False, default=dict)
    
    # Modifiers
    attribute_modifiers = Column(JSON, nullable=False, default=dict)
    domain_modifiers = Column(JSON, nullable=False, default=dict)
    combat_modifiers = Column(JSON, nullable=False, default=dict)
    
    # Flags
    can_be_dispelled = Column(Boolean, nullable=False, default=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    requires_concentration = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    magic_profile = relationship("DBMagicProfile", back_populates="active_effects")
    source_spell = relationship("DBSpell", foreign_keys=[source_spell_id])


class DBEnchantmentEffect(Base):
    """Database model for enchantment effects."""
    __tablename__ = "enchantment_effects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    enchantment_type = Column(Enum(EnchantmentType), nullable=False)
    
    # Effect properties
    power_level = Column(Float, nullable=False, default=1.0)
    effect_properties = Column(JSON, nullable=False, default=dict)
    
    # Item property modifiers
    attribute_bonuses = Column(JSON, nullable=False, default=dict)
    
    # Requirements
    required_item_types = Column(JSON, nullable=False, default=list)
    incompatible_effects = Column(JSON, nullable=False, default=list)
    
    # System
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipes = relationship("DBEnchantmentRecipeEffect", back_populates="effect")
    magic_items = relationship("DBMagicalItemEnchantment", back_populates="effect")


class DBEnchantmentRecipe(Base):
    """Database model for enchantment recipes."""
    __tablename__ = "enchantment_recipes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Requirements
    required_craft_level = Column(Integer, nullable=False, default=1)
    required_magic_tier = Column(Enum(MagicTier), nullable=False, default=MagicTier.SPIRITUAL_UTILITY)
    required_schools = Column(JSON, nullable=False, default=dict)
    required_materials = Column(JSON, nullable=False, default=list)
    
    # Process
    casting_time_minutes = Column(Integer, nullable=False, default=10)
    
    # Output
    success_rate_base = Column(Float, nullable=False, default=0.7)
    
    # Domain influences
    primary_domains = Column(JSON, nullable=False, default=list)
    domain_bonuses = Column(JSON, nullable=False, default=dict)
    
    # System
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    effects = relationship("DBEnchantmentRecipeEffect", back_populates="recipe", cascade="all, delete-orphan")
    components = relationship("DBEnchantmentRecipeComponent", back_populates="recipe", cascade="all, delete-orphan")


class DBEnchantmentRecipeEffect(Base):
    """Database model for enchantment recipe effects."""
    __tablename__ = "enchantment_recipe_effects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id = Column(String, ForeignKey("enchantment_recipes.id"), nullable=False)
    effect_id = Column(String, ForeignKey("enchantment_effects.id"), nullable=False)
    power_modifier = Column(Float, nullable=False, default=1.0)
    
    # Relationships
    recipe = relationship("DBEnchantmentRecipe", back_populates="effects")
    effect = relationship("DBEnchantmentEffect", back_populates="recipes")


class DBEnchantmentRecipeComponent(Base):
    """Database model for enchantment recipe components."""
    __tablename__ = "enchantment_recipe_components"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id = Column(String, ForeignKey("enchantment_recipes.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    component_type = Column(String, nullable=False)
    is_consumed = Column(Boolean, nullable=False, default=True)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Relationships
    recipe = relationship("DBEnchantmentRecipe", back_populates="components")


class DBMagicalItem(Base):
    """Database model for magical items."""
    __tablename__ = "magical_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    item_type = Column(String, nullable=False)  # "weapon", "armor", "accessory", "focus", "consumable"
    base_item_id = Column(String, nullable=True)
    
    # Item properties
    rarity = Column(Enum(MagicItemRarity), nullable=False, default=MagicItemRarity.COMMON)
    value = Column(Integer, nullable=False, default=0)
    weight = Column(Float, nullable=False, default=0.0)
    
    # Magic properties
    magic_tier = Column(Enum(MagicTier), nullable=False, default=MagicTier.SPIRITUAL_UTILITY)
    schools = Column(JSON, nullable=False, default=list)
    charges = Column(Integer, nullable=True)
    max_charges = Column(Integer, nullable=True)
    recharge_method = Column(String, nullable=True)
    
    # Usage requirements
    required_domains = Column(JSON, nullable=False, default=dict)
    attunement_required = Column(Boolean, nullable=False, default=False)
    
    # Special properties
    unique = Column(Boolean, nullable=False, default=False)
    cursed = Column(Boolean, nullable=False, default=False)
    sentient = Column(Boolean, nullable=False, default=False)
    corruption_influence = Column(Float, nullable=False, default=0.0)
    
    # System
    is_template = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enchantments = relationship("DBMagicalItemEnchantment", back_populates="item", cascade="all, delete-orphan")
    attuned_to = relationship("DBAttunedItem", back_populates="item")


class DBMagicalItemEnchantment(Base):
    """Database model for enchantments on magical items."""
    __tablename__ = "magical_item_enchantments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("magical_items.id"), nullable=False)
    effect_id = Column(String, ForeignKey("enchantment_effects.id"), nullable=False)
    power_level = Column(Float, nullable=False, default=1.0)
    custom_properties = Column(JSON, nullable=True)
    
    # Relationships
    item = relationship("DBMagicalItem", back_populates="enchantments")
    effect = relationship("DBEnchantmentEffect", back_populates="magic_items")


class DBAttunedItem(Base):
    """Database model for tracking item attunements to characters."""
    __tablename__ = "attuned_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    magic_profile_id = Column(String, ForeignKey("magic_profiles.id"), nullable=False)
    item_id = Column(String, ForeignKey("magical_items.id"), nullable=False)
    attuned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Attunement properties
    attunement_strength = Column(Float, nullable=False, default=1.0)
    custom_bonuses = Column(JSON, nullable=True)
    
    # Relationships
    magic_profile = relationship("DBMagicProfile", back_populates="attuned_items")
    item = relationship("DBMagicalItem", back_populates="attuned_to")


class DBMagicLocation(Base):
    """Database model for locations with magical properties."""
    __tablename__ = "magic_locations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Magical properties
    magic_density = Column(Float, nullable=False, default=0.5)
    ambient_mana = Column(Float, nullable=False, default=0.5)
    corruption_level = Column(Float, nullable=False, default=0.0)
    
    # Dominant influences
    dominant_elements = Column(JSON, nullable=False, default=dict)
    dominant_schools = Column(JSON, nullable=False, default=dict)
    
    # Special properties
    ley_line_intersection = Column(Boolean, nullable=False, default=False)
    dimensional_thinness = Column(Float, nullable=False, default=0.0)
    reality_stability = Column(Float, nullable=False, default=1.0)
    
    # Environmental effects
    environmental_effects = Column(JSON, nullable=False, default=list)
    spell_modifiers = Column(JSON, nullable=False, default=dict)
    
    # Restrictions
    blocked_schools = Column(JSON, nullable=False, default=list)
    enhanced_schools = Column(JSON, nullable=False, default=list)
    
    # System
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBSpellCastingLog(Base):
    """Database model for logging spell casting events."""
    __tablename__ = "spell_casting_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    spell_id = Column(String, ForeignKey("spells.id"), nullable=False)
    caster_id = Column(String, nullable=False, index=True)
    
    # Casting details
    success = Column(Boolean, nullable=False)
    mana_spent = Column(Integer, nullable=False)
    casting_time_actual = Column(Float, nullable=False)
    power_level = Column(Float, nullable=False)
    
    # Targets
    target_ids = Column(JSON, nullable=False, default=list)
    
    # Effect details
    effects_applied = Column(JSON, nullable=False, default=list)
    damage_dealt = Column(JSON, nullable=False, default=dict)
    healing_done = Column(JSON, nullable=False, default=dict)
    
    # Special outcomes
    critical_success = Column(Boolean, nullable=False, default=False)
    partial_success = Column(Boolean, nullable=False, default=False)
    failure_type = Column(String, nullable=True)
    corruption_gained = Column(Float, nullable=False, default=0.0)
    
    # Context
    location_id = Column(String, nullable=True)
    environmental_factors = Column(JSON, nullable=True)
    
    # Narrative
    narrative_description = Column(Text, nullable=True)
    visible_effects = Column(JSON, nullable=False, default=list)
    
    # Timestamp
    cast_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    spell = relationship("DBSpell")