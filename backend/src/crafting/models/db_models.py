"""
Crafting System Database Models

This module defines SQLAlchemy models for the material and recipe system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, 
    ForeignKey, JSON, DateTime, Enum, Text, Table
)
from sqlalchemy.orm import relationship

# Import Base class from your database module
from backend.src.database.base import Base
from backend.src.crafting.models.pydantic_models import MaterialType, Rarity

class DBMaterial(Base):
    """Database model for materials and items that can be used in crafting."""
    __tablename__ = "materials"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    material_type = Column(Enum(MaterialType), nullable=False)
    rarity = Column(Enum(Rarity), nullable=False)
    base_value = Column(Float, nullable=False)
    stackable = Column(Boolean, default=True)
    max_stack_size = Column(Integer, default=100)
    source_tags = Column(JSON, default=list)  # Stored as JSON array
    properties = Column(JSON, default=dict)  # Stored as JSON object
    icon = Column(String, nullable=True)
    is_craftable = Column(Boolean, default=False)
    illicit_in_regions = Column(JSON, default=list)  # Stored as JSON array
    weight_per_unit = Column(Float, default=1.0)
    durability = Column(Integer, nullable=True)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    used_in_recipes = relationship(
        "DBRecipeIngredient", 
        back_populates="material",
        foreign_keys="DBRecipeIngredient.item_id"
    )
    produced_by_recipes = relationship(
        "DBRecipeOutput", 
        back_populates="material",
        foreign_keys="DBRecipeOutput.item_id"
    )
    
    # Integration with inventory system (if applicable)
    inventory_items = relationship(
        "DBInventoryItem", 
        back_populates="material",
        foreign_keys="DBInventoryItem.material_id",
        cascade="all, delete-orphan"
    )

class DBRecipeIngredient(Base):
    """Database model for recipe ingredients."""
    __tablename__ = "recipe_ingredients"

    id = Column(String, primary_key=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    item_id = Column(String, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    can_be_substituted = Column(Boolean, default=False)
    possible_substitutes = Column(JSON, default=list)
    consumed_in_crafting = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipe = relationship("DBRecipe", back_populates="ingredients")
    material = relationship("DBMaterial", back_populates="used_in_recipes", foreign_keys=[item_id])

class DBRecipeOutput(Base):
    """Database model for recipe outputs."""
    __tablename__ = "recipe_outputs"

    id = Column(String, primary_key=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    item_id = Column(String, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    is_primary = Column(Boolean, default=False)  # Whether this is the primary output
    chance = Column(Float, default=1.0)
    quality_modifier = Column(Float, nullable=True)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipe = relationship("DBRecipe", back_populates="outputs")
    material = relationship("DBMaterial", back_populates="produced_by_recipes", foreign_keys=[item_id])

class DBSkillRequirement(Base):
    """Database model for recipe skill requirements."""
    __tablename__ = "skill_requirements"

    id = Column(String, primary_key=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    affects_quality = Column(Boolean, default=False)
    affects_speed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipe = relationship("DBRecipe", back_populates="required_skills")

class DBRecipe(Base):
    """Database model for crafting recipes."""
    __tablename__ = "recipes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    crafting_time_seconds = Column(Integer, default=0)
    required_tools = Column(JSON, default=list)
    required_station_type = Column(String, nullable=True)
    unlock_conditions = Column(JSON, default=dict)
    experience_gained = Column(JSON, default=list)
    is_discoverable = Column(Boolean, default=False)
    difficulty_level = Column(Integer, default=1)
    recipe_category = Column(String, nullable=True)
    quality_range = Column(JSON, default=dict)
    region_specific = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ingredients = relationship("DBRecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    outputs = relationship("DBRecipeOutput", back_populates="recipe", cascade="all, delete-orphan")
    required_skills = relationship("DBSkillRequirement", back_populates="recipe", cascade="all, delete-orphan")
    known_by_players = relationship("DBPlayerKnownRecipe", back_populates="recipe", cascade="all, delete-orphan")

class DBPlayerKnownRecipe(Base):
    """Database model for tracking which recipes are known by which players."""
    __tablename__ = "player_known_recipes"

    id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    discovery_date = Column(DateTime, nullable=True)
    mastery_level = Column(Integer, default=0)
    times_crafted = Column(Integer, default=0)
    highest_quality_crafted = Column(Integer, default=0)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    player = relationship("DBPlayer", back_populates="known_recipes")
    recipe = relationship("DBRecipe", back_populates="known_by_players")

class DBCraftingLog(Base):
    """Database model for tracking crafting history."""
    __tablename__ = "crafting_logs"

    id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    quantity_attempted = Column(Integer, default=1)
    quantity_produced = Column(Integer, default=0)
    quality_achieved = Column(Integer, default=1)
    ingredients_consumed = Column(JSON, default=list)
    outputs_produced = Column(JSON, default=list)
    experience_gained = Column(JSON, default=list)
    crafting_location = Column(String, nullable=True)  # e.g., business_id or location_id
    crafting_station_used = Column(String, nullable=True)
    custom_data = Column(JSON, default=dict)

    # Relationships
    player = relationship("DBPlayer", back_populates="crafting_logs")
    recipe = relationship("DBRecipe")

# This table is expected to exist in your database model
# If it doesn't exist yet, you should create it
class DBInventoryItem(Base):
    """
    Database model for inventory items.
    This is a placeholder - integrate with your actual inventory system.
    """
    __tablename__ = "inventory_items"

    id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    material_id = Column(String, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Integer, default=0)
    quality = Column(Integer, default=1)
    durability_remaining = Column(Integer, nullable=True)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    player = relationship("DBPlayer", back_populates="inventory")
    material = relationship("DBMaterial", back_populates="inventory_items")

# This is a placeholder for the player table that would exist in your system
class DBPlayer(Base):
    """
    Database model for players.
    This is a placeholder - integrate with your actual player system.
    """
    __tablename__ = "players"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    # Add other player fields as needed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    known_recipes = relationship("DBPlayerKnownRecipe", back_populates="player")
    crafting_logs = relationship("DBCraftingLog", back_populates="player")
    inventory = relationship("DBInventoryItem", back_populates="player")
    # Skills would be another relationship (not implemented here)