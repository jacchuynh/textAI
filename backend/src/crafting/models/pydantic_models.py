"""
Crafting System Pydantic Models

This module defines Pydantic models for the material and recipe system.
"""

import enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class MaterialType(str, enum.Enum):
    """Types of materials in the crafting system."""
    RAW_RESOURCE = "raw_resource"
    REFINED_MATERIAL = "refined_material"
    COMPONENT = "component"
    CONSUMABLE_INGREDIENT = "consumable_ingredient"
    FINISHED_GOOD = "finished_good"

class Rarity(str, enum.Enum):
    """Rarity levels for materials and items."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class Material(BaseModel):
    """Model representing a material or item that can be used in crafting."""
    id: str
    name: str
    description: str
    material_type: MaterialType
    rarity: Rarity
    base_value: float
    stackable: bool = True
    max_stack_size: Optional[int] = 100
    source_tags: List[str] = Field(default_factory=list)  # e.g., "mining", "woodcutting"
    properties: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"flammable": True}
    icon: Optional[str] = None
    is_craftable: bool = False
    illicit_in_regions: List[str] = Field(default_factory=list)  # List of MarketRegionInfo.id
    weight_per_unit: float = 1.0  # Weight in kg or other unit
    durability: Optional[int] = None  # For tools or equipment
    custom_data: Dict[str, Any] = Field(default_factory=dict)  # For any additional properties

class RecipeIngredient(BaseModel):
    """Model representing an ingredient required for a recipe."""
    item_id: str  # References Material.id or a general Item.id
    quantity: int
    # Optional fields for more complex recipes
    can_be_substituted: bool = False
    possible_substitutes: List[str] = Field(default_factory=list)  # List of other material IDs
    consumed_in_crafting: bool = True  # Whether the ingredient is consumed (e.g., tools aren't)

class RecipeOutput(BaseModel):
    """Model representing an output (product) of a recipe."""
    item_id: str
    quantity: int
    # Optional fields for more detailed output management
    chance: float = 1.0  # Probability of getting this output (1.0 = guaranteed)
    quality_modifier: Optional[float] = None  # For variable quality crafting
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class SkillRequirement(BaseModel):
    """Model representing a skill requirement for a recipe."""
    skill_name: str
    level: int
    # Optional fields for more nuanced skill requirements
    affects_quality: bool = False  # Whether skill level affects output quality
    affects_speed: bool = False  # Whether skill level affects crafting speed

class Recipe(BaseModel):
    """Model representing a crafting recipe."""
    id: str
    name: str
    description: str
    primary_output: RecipeOutput
    byproducts: List[RecipeOutput] = Field(default_factory=list)
    ingredients: List[RecipeIngredient]
    crafting_time_seconds: int = 0  # Default 0 for instant
    required_skills: List[SkillRequirement] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)  # List of Item.id
    required_station_type: Optional[str] = None  # e.g., "forge", "alchemy_lab"
    unlock_conditions: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"min_character_level": 10}
    experience_gained: List[Dict[str, Any]] = Field(default_factory=list)  # e.g., [{"skill_name": "blacksmithing", "xp": 50}]
    is_discoverable: bool = False
    auto_learn_at_skill_level: Optional[SkillRequirement] = None
    # Additional fields for more complex recipe systems
    difficulty_level: int = 1  # Used for determining success chance based on skill
    recipe_category: Optional[str] = None  # For categorization (e.g., "weapons", "potions")
    quality_range: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"min": 1, "max": 5}
    region_specific: List[str] = Field(default_factory=list)  # Regions where this recipe is available
    failure_outputs: List[RecipeOutput] = Field(default_factory=list)  # What you get if crafting fails
    custom_data: Dict[str, Any] = Field(default_factory=dict)  # For any additional properties

class PlayerKnownRecipe(BaseModel):
    """Model representing a recipe known by a player."""
    player_id: str
    recipe_id: str
    discovery_date: Optional[str] = None
    mastery_level: int = 0  # Players can master recipes to improve quality/speed
    times_crafted: int = 0
    highest_quality_crafted: int = 0
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class CraftingResult(BaseModel):
    """Model representing the result of a crafting attempt."""
    success: bool
    message: str
    outputs: List[RecipeOutput] = Field(default_factory=list)
    consumed_ingredients: List[RecipeIngredient] = Field(default_factory=list)
    experience_gained: List[Dict[str, Any]] = Field(default_factory=list)
    crafting_time_taken: int = 0
    quality_achieved: int = 1
    skill_improvements: List[Dict[str, Any]] = Field(default_factory=list)
    recipe_mastery_gained: int = 0
    custom_data: Dict[str, Any] = Field(default_factory=dict)