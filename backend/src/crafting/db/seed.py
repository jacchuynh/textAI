"""
Crafting System Database Seed Script

This script populates the database with initial materials and recipes
for the Material and Recipe System.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from backend.src.database.session import SessionLocal
from backend.src.crafting.models.db_models import (
    DBMaterial, DBRecipe, DBRecipeIngredient, DBRecipeOutput, DBSkillRequirement
)
from backend.src.crafting.models.pydantic_models import (
    MaterialType, Rarity, Material, Recipe, RecipeIngredient, RecipeOutput, SkillRequirement
)
from backend.src.crafting.db.material_archetypes import ALL_MATERIALS
from backend.src.crafting.db.recipe_archetypes import ALL_RECIPES

logger = logging.getLogger(__name__)

def seed_materials(db: Session) -> Dict[str, str]:
    """
    Seed the materials table with initial data.
    
    Returns a mapping of material names to their UUIDs.
    """
    logger.info("Seeding materials...")
    material_id_map = {}
    
    for material_data in ALL_MATERIALS:
        # Check if material already exists
        existing = db.query(DBMaterial).filter(DBMaterial.name == material_data["name"]).first()
        if existing:
            logger.info(f"Material '{material_data['name']}' already exists, skipping.")
            material_id_map[material_data["name"]] = existing.id
            continue
        
        # Create new material
        material = Material(**material_data)
        db_material = DBMaterial(
            name=material.name,
            description=material.description,
            material_type=material.material_type.value,
            rarity=material.rarity.value,
            base_value=material.base_value,
            weight=material.weight,
            is_craftable=material.is_craftable,
            source_tags=material.source_tags,
            illicit_in_regions=material.illicit_in_regions,
            properties=material.properties,
            custom_data=material.custom_data
        )
        db.add(db_material)
        db.flush()
        
        logger.info(f"Added material: {material.name}")
        material_id_map[material.name] = db_material.id
    
    db.commit()
    return material_id_map

def seed_recipes(db: Session, material_id_map: Dict[str, str]) -> None:
    """
    Seed the recipes table with initial data.
    
    Args:
        db: Database session
        material_id_map: Mapping of material names to their UUIDs
    """
    logger.info("Seeding recipes...")
    
    for recipe_data in ALL_RECIPES:
        # Check if recipe already exists
        existing = db.query(DBRecipe).filter(DBRecipe.name == recipe_data["name"]).first()
        if existing:
            logger.info(f"Recipe '{recipe_data['name']}' already exists, skipping.")
            continue
        
        # Create new recipe
        db_recipe = DBRecipe(
            name=recipe_data["name"],
            description=recipe_data["description"],
            recipe_category=recipe_data["recipe_category"],
            crafting_time_seconds=recipe_data["crafting_time_seconds"],
            required_station_type=recipe_data["required_station_type"],
            difficulty_level=recipe_data["difficulty_level"],
            is_discoverable=recipe_data["is_discoverable"],
            experience_gained=recipe_data["experience_gained"],
            quality_range=recipe_data["quality_range"]
        )
        db.add(db_recipe)
        db.flush()  # Get the recipe ID
        
        # Add primary output
        primary_output = recipe_data["primary_output"]
        item_id = material_id_map.get(primary_output["item_id"])
        if not item_id:
            logger.warning(f"Output material '{primary_output['item_id']}' not found for recipe '{recipe_data['name']}', creating placeholder.")
            # Create a placeholder material
            placeholder_material = DBMaterial(
                name=primary_output["item_id"],
                description=f"Product of {recipe_data['name']}",
                material_type=MaterialType.CRAFTED.value,
                rarity=Rarity.COMMON.value,
                base_value=10.0,
                weight=1.0,
                is_craftable=True,
                source_tags=["crafted"],
                properties={}
            )
            db.add(placeholder_material)
            db.flush()
            item_id = placeholder_material.id
            material_id_map[primary_output["item_id"]] = item_id
        
        db_output = DBRecipeOutput(
            recipe_id=db_recipe.id,
            item_id=item_id,
            quantity=primary_output["quantity"],
            is_primary=True,
            chance=1.0
        )
        db.add(db_output)
        
        # Add byproducts (if any)
        if "byproducts" in recipe_data:
            for byproduct in recipe_data["byproducts"]:
                byproduct_item_id = material_id_map.get(byproduct["item_id"])
                if not byproduct_item_id:
                    logger.warning(f"Byproduct material '{byproduct['item_id']}' not found for recipe '{recipe_data['name']}', creating placeholder.")
                    placeholder_material = DBMaterial(
                        name=byproduct["item_id"],
                        description=f"Byproduct of {recipe_data['name']}",
                        material_type=MaterialType.CRAFTED.value,
                        rarity=Rarity.COMMON.value,
                        base_value=5.0,
                        weight=0.5,
                        is_craftable=True,
                        source_tags=["crafted", "byproduct"],
                        properties={}
                    )
                    db.add(placeholder_material)
                    db.flush()
                    byproduct_item_id = placeholder_material.id
                    material_id_map[byproduct["item_id"]] = byproduct_item_id
                
                db_byproduct = DBRecipeOutput(
                    recipe_id=db_recipe.id,
                    item_id=byproduct_item_id,
                    quantity=byproduct["quantity"],
                    is_primary=False,
                    chance=byproduct.get("chance", 0.5),
                    quality_modifier=byproduct.get("quality_modifier", 0.0)
                )
                db.add(db_byproduct)
        
        # Add ingredients
        for ingredient in recipe_data["ingredients"]:
            ingredient_item_id = material_id_map.get(ingredient["item_id"])
            if not ingredient_item_id:
                logger.warning(f"Ingredient material '{ingredient['item_id']}' not found for recipe '{recipe_data['name']}', creating placeholder.")
                placeholder_material = DBMaterial(
                    name=ingredient["item_id"],
                    description=f"Ingredient for {recipe_data['name']}",
                    material_type=MaterialType.MATERIAL.value,
                    rarity=Rarity.COMMON.value,
                    base_value=2.0,
                    weight=0.2,
                    is_craftable=False,
                    source_tags=["ingredient"],
                    properties={}
                )
                db.add(placeholder_material)
                db.flush()
                ingredient_item_id = placeholder_material.id
                material_id_map[ingredient["item_id"]] = ingredient_item_id
            
            db_ingredient = DBRecipeIngredient(
                recipe_id=db_recipe.id,
                item_id=ingredient_item_id,
                quantity=ingredient["quantity"],
                consumed_in_crafting=ingredient.get("consumed_in_crafting", True),
                can_be_substituted=ingredient.get("can_be_substituted", False),
                possible_substitutes=ingredient.get("possible_substitutes")
            )
            db.add(db_ingredient)
        
        # Add skill requirements
        for skill in recipe_data["required_skills"]:
            db_skill = DBSkillRequirement(
                recipe_id=db_recipe.id,
                skill_name=skill["skill_name"],
                level=skill["level"],
                affects_quality=skill.get("affects_quality", True),
                affects_speed=skill.get("affects_speed", False)
            )
            db.add(db_skill)
        
        logger.info(f"Added recipe: {recipe_data['name']}")
    
    db.commit()

def seed_database() -> None:
    """Seed the database with initial materials and recipes."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting database seeding process...")
    
    db = SessionLocal()
    try:
        material_id_map = seed_materials(db)
        seed_recipes(db, material_id_map)
        logger.info("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()