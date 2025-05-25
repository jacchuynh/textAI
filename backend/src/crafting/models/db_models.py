"""
Crafting System Database Models

This module defines the database models for the Material and Recipe System.
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, 
    ForeignKey, DateTime, Text, JSON, Enum
)
from sqlalchemy.orm import relationship
import enum

from backend.src.database.base import Base
from backend.src.crafting.models.pydantic_models import MaterialType, Rarity

class DBMaterial(Base):
    """Database model for materials used in crafting."""
    
    __tablename__ = "materials"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    material_type = Column(String(50), nullable=False, index=True)  # Enum as string
    rarity = Column(String(50), nullable=False, index=True)  # Enum as string
    base_value = Column(Float, nullable=False, default=0.0)
    weight = Column(Float, nullable=False, default=0.0)
    is_craftable = Column(Boolean, nullable=False, default=False)
    source_tags = Column(JSON, nullable=False, default=list)  # Array of strings
    illicit_in_regions = Column(JSON, nullable=False, default=list)  # Array of strings
    properties = Column(JSON, nullable=False, default=dict)  # JSON object
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ingredients_in = relationship("DBRecipeIngredient", back_populates="material")
    outputs_in = relationship("DBRecipeOutput", back_populates="material")
    
    def __repr__(self):
        return f"<Material {self.name} ({self.material_type}, {self.rarity})>"

class DBRecipe(Base):
    """Database model for crafting recipes."""
    
    __tablename__ = "recipes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    recipe_category = Column(String(100), nullable=False, index=True)
    crafting_time_seconds = Column(Integer, nullable=False, default=60)
    required_station_type = Column(String(100), nullable=True)
    difficulty_level = Column(Integer, nullable=False, default=1)
    is_discoverable = Column(Boolean, nullable=False, default=False)
    region_specific = Column(JSON, nullable=True)  # Array of region IDs
    unlock_conditions = Column(JSON, nullable=True, default=dict)  # JSON object
    experience_gained = Column(JSON, nullable=False, default=list)  # Array of objects
    quality_range = Column(JSON, nullable=False, default={"min": 1, "max": 3})  # JSON object
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ingredients = relationship("DBRecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    outputs = relationship("DBRecipeOutput", back_populates="recipe", cascade="all, delete-orphan")
    required_skills = relationship("DBSkillRequirement", back_populates="recipe", cascade="all, delete-orphan")
    known_by_players = relationship("DBPlayerKnownRecipe", back_populates="recipe", cascade="all, delete-orphan")
    crafting_logs = relationship("DBCraftingLog", back_populates="recipe")
    
    def __repr__(self):
        return f"<Recipe {self.name} (Difficulty: {self.difficulty_level})>"

class DBRecipeIngredient(Base):
    """Database model for ingredients required in a recipe."""
    
    __tablename__ = "recipe_ingredients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id = Column(String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    can_be_substituted = Column(Boolean, nullable=False, default=False)
    possible_substitutes = Column(JSON, nullable=True)  # Array of item IDs or null
    consumed_in_crafting = Column(Boolean, nullable=False, default=True)
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    
    # Relationships
    recipe = relationship("DBRecipe", back_populates="ingredients")
    material = relationship("DBMaterial", back_populates="ingredients_in")
    
    def __repr__(self):
        return f"<RecipeIngredient {self.id} (Recipe: {self.recipe_id}, Item: {self.item_id})>"

class DBRecipeOutput(Base):
    """Database model for outputs produced by a recipe."""
    
    __tablename__ = "recipe_outputs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id = Column(String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    is_primary = Column(Boolean, nullable=False, default=True)
    chance = Column(Float, nullable=False, default=1.0)  # 0.0 to 1.0
    quality_modifier = Column(Float, nullable=False, default=0.0)  # Modifier to base quality
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    
    # Relationships
    recipe = relationship("DBRecipe", back_populates="outputs")
    material = relationship("DBMaterial", back_populates="outputs_in")
    
    def __repr__(self):
        return f"<RecipeOutput {self.id} (Recipe: {self.recipe_id}, Item: {self.item_id}, Primary: {self.is_primary})>"

class DBSkillRequirement(Base):
    """Database model for skills required to craft a recipe."""
    
    __tablename__ = "skill_requirements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id = Column(String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False, default=1)
    affects_quality = Column(Boolean, nullable=False, default=True)
    affects_speed = Column(Boolean, nullable=False, default=False)
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    
    # Relationships
    recipe = relationship("DBRecipe", back_populates="required_skills")
    
    def __repr__(self):
        return f"<SkillRequirement {self.id} (Recipe: {self.recipe_id}, Skill: {self.skill_name}, Level: {self.level})>"

class DBPlayerKnownRecipe(Base):
    """Database model for tracking which recipes a player knows."""
    
    __tablename__ = "player_known_recipes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), nullable=False, index=True)
    recipe_id = Column(String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    discovery_date = Column(DateTime, default=datetime.utcnow)
    mastery_level = Column(Integer, nullable=False, default=0)  # 0-5 (0=novice, 5=master)
    times_crafted = Column(Integer, nullable=False, default=0)
    highest_quality_crafted = Column(Integer, nullable=False, default=0)
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    
    # Relationships
    recipe = relationship("DBRecipe", back_populates="known_by_players")
    
    def __repr__(self):
        return f"<PlayerKnownRecipe {self.id} (Player: {self.player_id}, Recipe: {self.recipe_id}, Mastery: {self.mastery_level})>"

class DBCraftingLog(Base):
    """Database model for logging crafting attempts."""
    
    __tablename__ = "crafting_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), nullable=False, index=True)
    recipe_id = Column(String(36), ForeignKey("recipes.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, nullable=False, default=True)
    quantity_attempted = Column(Integer, nullable=False, default=1)
    quantity_produced = Column(Integer, nullable=False, default=0)
    quality_achieved = Column(Integer, nullable=False, default=0)
    ingredients_consumed = Column(JSON, nullable=False, default=list)  # Array of objects {item_id, quantity}
    outputs_produced = Column(JSON, nullable=False, default=list)  # Array of objects {item_id, quantity, quality}
    experience_gained = Column(JSON, nullable=False, default=list)  # Array of objects {skill_name, amount}
    crafting_location = Column(String(255), nullable=True)  # Location ID or description
    crafting_station_used = Column(String(255), nullable=True)  # Station type used
    business_id = Column(String(36), nullable=True, index=True)  # Optional business ID if crafted for business
    custom_data = Column(JSON, nullable=True)  # Additional flexible data
    
    # Relationships
    recipe = relationship("DBRecipe", back_populates="crafting_logs")
    
    def __repr__(self):
        return f"<CraftingLog {self.id} (Player: {self.player_id}, Recipe: {self.recipe_id}, Success: {self.success})>"