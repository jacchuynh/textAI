"""
Crafting System Pydantic Models

This module defines the Pydantic models for the Material and Recipe System.
"""

import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MaterialType(str, Enum):
    """Enumeration of material types."""
    # Raw Materials
    ORE = "ORE"
    METAL = "METAL"
    METAL_PRECIOUS = "METAL_PRECIOUS"
    WOOD_RAW = "WOOD_RAW"
    WOOD_PROCESSED = "WOOD_PROCESSED"
    WOOD_MAGICAL = "WOOD_MAGICAL"
    WOOD_MINERAL = "WOOD_MINERAL"
    HIDE = "HIDE"
    LEATHER = "LEATHER"
    EXOTIC_HIDE = "EXOTIC_HIDE"
    EXOTIC_LEATHER = "EXOTIC_LEATHER"
    CLOTH = "CLOTH"
    THREAD = "THREAD"
    PLANT_FIBER = "PLANT_FIBER"
    HERB = "HERB"
    GEM_RAW = "GEM_RAW"
    GEM = "GEM"
    GEM_PROCESSED = "GEM_PROCESSED"
    GEM_MAGICAL = "GEM_MAGICAL"
    ANIMAL_PART = "ANIMAL_PART"
    MAGICAL = "MAGICAL"
    MINERAL = "MINERAL"
    
    # Crafting Components
    RESIN = "RESIN"
    ADHESIVE = "ADHESIVE"
    FINISH = "FINISH"
    FINISH_MAGICAL = "FINISH_MAGICAL"
    FASTENER_WOOD = "FASTENER_WOOD"
    FASTENER_METAL = "FASTENER_METAL"
    FINDING = "FINDING"
    TOOL = "TOOL"
    TOOL_PART = "TOOL_PART"
    CONSUMABLE = "CONSUMABLE"
    
    # Generic types
    CRAFTED = "CRAFTED"
    MATERIAL = "MATERIAL"
    OTHER = "OTHER"


class Rarity(str, Enum):
    """Enumeration of item rarities."""
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"


class RecipeIngredient(BaseModel):
    """Model for ingredients required in a recipe."""
    item_id: str
    quantity: float = 1.0
    can_be_substituted: bool = False
    possible_substitutes: Optional[List[str]] = None
    consumed_in_crafting: bool = True
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class RecipeOutput(BaseModel):
    """Model for outputs produced by a recipe."""
    item_id: str
    quantity: float = 1.0
    chance: float = 1.0  # 0.0 to 1.0
    quality_modifier: float = 0.0  # Modifier to base quality
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class SkillRequirement(BaseModel):
    """Model for skills required to craft a recipe."""
    skill_name: str
    level: int = 1
    affects_quality: bool = True
    affects_speed: bool = False
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class AutoLearnSkillLevel(BaseModel):
    """Model for skills that trigger auto-learning of a recipe."""
    skill_name: str
    level: int

    class Config:
        orm_mode = True


class Material(BaseModel):
    """Model for materials used in crafting."""
    id: Optional[str] = None
    name: str
    description: str
    material_type: MaterialType
    rarity: Rarity
    base_value: float = 0.0
    weight: float = 0.0
    is_craftable: bool = False
    source_tags: List[str] = Field(default_factory=list)
    illicit_in_regions: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class Recipe(BaseModel):
    """Model for crafting recipes."""
    id: Optional[str] = None
    name: str
    description: str
    primary_output: RecipeOutput
    byproducts: List[RecipeOutput] = Field(default_factory=list)
    ingredients: List[RecipeIngredient] = Field(default_factory=list)
    crafting_time_seconds: int = 60
    required_skills: List[SkillRequirement] = Field(default_factory=list)
    required_tools: Optional[List[str]] = None
    required_station_type: Optional[str] = None
    unlock_conditions: Dict[str, Any] = Field(default_factory=dict)
    experience_gained: List[Dict[str, Any]] = Field(default_factory=list)
    is_discoverable: bool = False
    auto_learn_at_skill_level: Optional[AutoLearnSkillLevel] = None
    difficulty_level: int = 1
    recipe_category: str
    quality_range: Dict[str, int] = Field(default_factory=lambda: {"min": 1, "max": 3})
    region_specific: Optional[List[str]] = None
    failure_outputs: List[RecipeOutput] = Field(default_factory=list)
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class PlayerKnownRecipe(BaseModel):
    """Model for tracking which recipes a player knows."""
    id: Optional[str] = None
    player_id: str
    recipe_id: str
    discovery_date: datetime = Field(default_factory=datetime.utcnow)
    mastery_level: int = 0  # 0-5 (0=novice, 5=master)
    times_crafted: int = 0
    highest_quality_crafted: int = 0
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class CraftingLog(BaseModel):
    """Model for logging crafting attempts."""
    id: Optional[str] = None
    player_id: str
    recipe_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    quantity_attempted: int = 1
    quantity_produced: int = 0
    quality_achieved: int = 0
    ingredients_consumed: List[Dict[str, Any]] = Field(default_factory=list)
    outputs_produced: List[Dict[str, Any]] = Field(default_factory=list)
    experience_gained: List[Dict[str, Any]] = Field(default_factory=list)
    crafting_location: Optional[str] = None
    crafting_station_used: Optional[str] = None
    business_id: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class CraftingResult(BaseModel):
    """Model for the result of a crafting attempt."""
    success: bool
    message: str
    outputs: List[Dict[str, Any]]
    consumed_ingredients: List[Dict[str, Any]]
    experience_gained: List[Dict[str, Any]]
    crafting_time_taken: Optional[int] = None
    quality_achieved: Optional[int] = None
    skill_improvements: List[Dict[str, Any]] = Field(default_factory=list)
    recipe_mastery_gained: Optional[int] = None
    custom_data: Optional[Dict[str, Any]] = None