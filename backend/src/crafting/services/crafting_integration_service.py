"""
Crafting System Integration Service

This module provides integration between the Crafting System and other game systems,
particularly the AI GM Brain, economy systems, and NPC behavior.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Union
from sqlalchemy.orm import Session

from backend.src.database.session import SessionLocal
from backend.src.crafting.models.db_models import (
    DBMaterial, DBRecipe, DBRecipeIngredient, DBRecipeOutput, DBSkillRequirement
)
from backend.src.crafting.models.pydantic_models import (
    Material, Recipe, Rarity, MaterialType, CraftingResult
)

# Import AI GM Brain components
from backend.src.ai_gm.ai_gm_brain_config_integrated import IntegratedAIGMConfig
# from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm  # Temporarily disabled

logger = logging.getLogger(__name__)

class CraftingIntegrationService:
    """Service for integrating the crafting system with other game systems."""
    
    def __init__(self):
        """Initialize the crafting integration service."""
        self.db = SessionLocal()
    
    def close(self):
        """Close the database session."""
        if self.db:
            self.db.close()
    
    def get_region_available_materials(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Get materials that are available in a specific region.
        
        Args:
            region_id: The region ID to check
            
        Returns:
            A list of materials with their details
        """
        try:
            # Query materials that are not illicit in this region
            materials = (
                self.db.query(DBMaterial)
                .filter(~DBMaterial.illicit_in_regions.contains([region_id]))
                .all()
            )
            
            return [
                {
                    "id": material.id,
                    "name": material.name,
                    "description": material.description,
                    "material_type": material.material_type,
                    "rarity": material.rarity,
                    "base_value": material.base_value,
                    "is_craftable": material.is_craftable,
                    "source_tags": material.source_tags,
                    "properties": material.properties
                }
                for material in materials
            ]
        except Exception as e:
            logger.error(f"Error getting region available materials: {e}")
            return []
    
    def get_illicit_materials_for_region(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Get materials that are considered illicit in a specific region.
        
        Args:
            region_id: The region ID to check
            
        Returns:
            A list of illicit materials with their details
        """
        try:
            # Query materials that are illicit in this region
            materials = (
                self.db.query(DBMaterial)
                .filter(DBMaterial.illicit_in_regions.contains([region_id]))
                .all()
            )
            
            return [
                {
                    "id": material.id,
                    "name": material.name,
                    "description": material.description,
                    "material_type": material.material_type,
                    "rarity": material.rarity,
                    "base_value": material.base_value,
                    "is_craftable": material.is_craftable,
                    "source_tags": material.source_tags,
                    "properties": material.properties
                }
                for material in materials
            ]
        except Exception as e:
            logger.error(f"Error getting illicit materials for region: {e}")
            return []
    
    def get_craftable_items_by_profession(self, profession: str) -> List[Dict[str, Any]]:
        """
        Get craftable items (recipes) based on a specific profession.
        
        Args:
            profession: The profession name (e.g., "Blacksmithing", "Alchemy")
            
        Returns:
            A list of recipes with their details
        """
        try:
            # Query recipes by category that matches the profession
            recipes = (
                self.db.query(DBRecipe)
                .filter(DBRecipe.recipe_category.like(f"{profession}%"))
                .all()
            )
            
            result = []
            for recipe in recipes:
                # Get primary output
                primary_output = (
                    self.db.query(DBRecipeOutput)
                    .filter(DBRecipeOutput.recipe_id == recipe.id, DBRecipeOutput.is_primary == True)
                    .first()
                )
                
                if primary_output:
                    output_material = (
                        self.db.query(DBMaterial)
                        .filter(DBMaterial.id == primary_output.item_id)
                        .first()
                    )
                    
                    if output_material:
                        result.append({
                            "recipe_id": recipe.id,
                            "recipe_name": recipe.name,
                            "recipe_description": recipe.description,
                            "difficulty_level": recipe.difficulty_level,
                            "crafting_time_seconds": recipe.crafting_time_seconds,
                            "required_station_type": recipe.required_station_type,
                            "output_item": {
                                "id": output_material.id,
                                "name": output_material.name,
                                "description": output_material.description,
                                "material_type": output_material.material_type,
                                "rarity": output_material.rarity,
                                "base_value": output_material.base_value
                            }
                        })
            
            return result
        except Exception as e:
            logger.error(f"Error getting craftable items by profession: {e}")
            return []
    
    def get_material_sources_by_region(self, region_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get materials that can be sourced (mined, harvested, etc.) in a specific region.
        
        Args:
            region_id: The region ID to check
            
        Returns:
            A dictionary mapping source types to lists of materials
        """
        try:
            # Define region-specific tags to search for
            region_tags = [
                f"mined_{region_id.lower()}",
                f"harvested_{region_id.lower()}",
                f"hunted_{region_id.lower()}",
                f"found_{region_id.lower()}",
                f"grown_{region_id.lower()}",
                f"{region_id.lower()}"
            ]
            
            materials_by_source = {}
            
            # Query all materials that have region-related source tags
            for tag in region_tags:
                materials = (
                    self.db.query(DBMaterial)
                    .filter(DBMaterial.source_tags.contains([tag]))
                    .all()
                )
                
                if materials:
                    source_type = tag.split('_')[0] if '_' in tag else 'general'
                    if source_type not in materials_by_source:
                        materials_by_source[source_type] = []
                    
                    for material in materials:
                        materials_by_source[source_type].append({
                            "id": material.id,
                            "name": material.name,
                            "description": material.description,
                            "material_type": material.material_type,
                            "rarity": material.rarity,
                            "base_value": material.base_value,
                            "properties": material.properties
                        })
            
            return materials_by_source
        except Exception as e:
            logger.error(f"Error getting material sources by region: {e}")
            return {}
    
    def generate_npc_inventory_for_profession(
        self, 
        profession: str, 
        wealth_level: int = 3,
        specialization: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a realistic inventory for an NPC based on their profession.
        
        Args:
            profession: The profession name (e.g., "Blacksmith", "Alchemist")
            wealth_level: The wealth level of the NPC (1-5)
            specialization: Optional specialization within the profession
            
        Returns:
            A list of inventory items with their details
        """
        try:
            # Determine profession category for database lookup
            profession_category_map = {
                "Blacksmith": "Blacksmithing",
                "Weaponsmith": "Blacksmithing - Weapons",
                "Armorsmith": "Blacksmithing - Armor",
                "Alchemist": "Alchemy",
                "Herbalist": "Alchemy - Herbs",
                "Woodworker": "Woodworking",
                "Carpenter": "Woodworking - Furniture",
                "Tailor": "Tailoring",
                "Leatherworker": "Leatherworking",
                "Jeweler": "Jewelcrafting",
                "Gemcutter": "Jewelcrafting - Gem Cutting",
                "Relicsmith": "Relicsmithing"
            }
            
            # Get base profession category
            base_profession = profession_category_map.get(profession, profession)
            
            # Add specialization if provided
            if specialization and "-" not in base_profession:
                search_category = f"{base_profession} - {specialization}"
            else:
                search_category = base_profession
            
            # Get craftable items for this profession
            recipes = (
                self.db.query(DBRecipe)
                .filter(DBRecipe.recipe_category.like(f"{search_category}%"))
                .all()
            )
            
            # Get raw materials commonly used in this profession
            profession_ingredients = set()
            for recipe in recipes:
                ingredients = (
                    self.db.query(DBRecipeIngredient)
                    .filter(DBRecipeIngredient.recipe_id == recipe.id)
                    .all()
                )
                for ingredient in ingredients:
                    profession_ingredients.add(ingredient.item_id)
            
            raw_materials = (
                self.db.query(DBMaterial)
                .filter(DBMaterial.id.in_(profession_ingredients))
                .all()
            )
            
            # Get crafted items (outputs of recipes)
            crafted_item_ids = set()
            for recipe in recipes:
                outputs = (
                    self.db.query(DBRecipeOutput)
                    .filter(DBRecipeOutput.recipe_id == recipe.id, DBRecipeOutput.is_primary == True)
                    .all()
                )
                for output in outputs:
                    crafted_item_ids.add(output.item_id)
            
            crafted_items = (
                self.db.query(DBMaterial)
                .filter(DBMaterial.id.in_(crafted_item_ids))
                .all()
            )
            
            # Determine inventory quantities based on wealth level and rarity
            inventory = []
            
            # Add raw materials
            for material in raw_materials:
                rarity_value = {"COMMON": 1, "UNCOMMON": 2, "RARE": 3, "EPIC": 4, "LEGENDARY": 5}.get(material.rarity, 1)
                quantity = max(1, int((wealth_level * 5) / rarity_value))
                
                # Randomize a bit
                quantity = int(quantity * random.uniform(0.5, 1.5))
                
                if quantity > 0:
                    inventory.append({
                        "item_id": material.id,
                        "name": material.name,
                        "description": material.description,
                        "quantity": quantity,
                        "unit_value": material.base_value,
                        "total_value": material.base_value * quantity,
                        "material_type": material.material_type,
                        "rarity": material.rarity,
                        "is_raw_material": True
                    })
            
            # Add crafted items
            for item in crafted_items:
                rarity_value = {"COMMON": 1, "UNCOMMON": 2, "RARE": 3, "EPIC": 4, "LEGENDARY": 5}.get(item.rarity, 1)
                quantity = max(1, int((wealth_level * 3) / rarity_value))
                
                # Randomize a bit
                quantity = int(quantity * random.uniform(0.5, 1.5))
                
                # Higher rarity items are less common
                if rarity_value > wealth_level:
                    quantity = max(0, quantity - (rarity_value - wealth_level))
                
                if quantity > 0:
                    inventory.append({
                        "item_id": item.id,
                        "name": item.name,
                        "description": item.description,
                        "quantity": quantity,
                        "unit_value": item.base_value,
                        "total_value": item.base_value * quantity,
                        "material_type": item.material_type,
                        "rarity": item.rarity,
                        "is_raw_material": False
                    })
            
            return inventory
        except Exception as e:
            logger.error(f"Error generating NPC inventory for profession: {e}")
            return []
    
    def get_material_info_for_ai_gm(self, material_ids: List[str]) -> Dict[str, Any]:
        """
        Get detailed information about materials for use by the AI GM Brain.
        
        Args:
            material_ids: List of material IDs to get information for
            
        Returns:
            A dictionary with detailed material information
        """
        try:
            materials = (
                self.db.query(DBMaterial)
                .filter(DBMaterial.id.in_(material_ids))
                .all()
            )
            
            result = {}
            for material in materials:
                result[material.id] = {
                    "name": material.name,
                    "description": material.description,
                    "material_type": material.material_type,
                    "rarity": material.rarity,
                    "base_value": material.base_value,
                    "properties": material.properties,
                    "source_tags": material.source_tags,
                    "is_craftable": material.is_craftable,
                    "illicit_in_regions": material.illicit_in_regions
                }
            
            return result
        except Exception as e:
            logger.error(f"Error getting material info for AI GM: {e}")
            return {}
    
    def get_recipe_info_for_ai_gm(self, recipe_ids: List[str]) -> Dict[str, Any]:
        """
        Get detailed information about recipes for use by the AI GM Brain.
        
        Args:
            recipe_ids: List of recipe IDs to get information for
            
        Returns:
            A dictionary with detailed recipe information
        """
        try:
            recipes = (
                self.db.query(DBRecipe)
                .filter(DBRecipe.id.in_(recipe_ids))
                .all()
            )
            
            result = {}
            for recipe in recipes:
                # Get primary output
                primary_output = (
                    self.db.query(DBRecipeOutput)
                    .filter(DBRecipeOutput.recipe_id == recipe.id, DBRecipeOutput.is_primary == True)
                    .first()
                )
                
                output_material = None
                if primary_output:
                    output_material = (
                        self.db.query(DBMaterial)
                        .filter(DBMaterial.id == primary_output.item_id)
                        .first()
                    )
                
                # Get ingredients
                ingredients = (
                    self.db.query(DBRecipeIngredient)
                    .filter(DBRecipeIngredient.recipe_id == recipe.id)
                    .all()
                )
                
                ingredient_info = []
                for ingredient in ingredients:
                    ingredient_material = (
                        self.db.query(DBMaterial)
                        .filter(DBMaterial.id == ingredient.item_id)
                        .first()
                    )
                    
                    if ingredient_material:
                        ingredient_info.append({
                            "name": ingredient_material.name,
                            "quantity": ingredient.quantity,
                            "rarity": ingredient_material.rarity,
                            "material_type": ingredient_material.material_type,
                            "base_value": ingredient_material.base_value
                        })
                
                result[recipe.id] = {
                    "name": recipe.name,
                    "description": recipe.description,
                    "recipe_category": recipe.recipe_category,
                    "difficulty_level": recipe.difficulty_level,
                    "crafting_time_seconds": recipe.crafting_time_seconds,
                    "required_station_type": recipe.required_station_type,
                    "is_discoverable": recipe.is_discoverable,
                    "ingredients": ingredient_info,
                    "output": {
                        "name": output_material.name if output_material else None,
                        "description": output_material.description if output_material else None,
                        "quantity": primary_output.quantity if primary_output else None,
                        "rarity": output_material.rarity if output_material else None,
                        "material_type": output_material.material_type if output_material else None,
                        "base_value": output_material.base_value if output_material else None
                    } if output_material else None
                }
            
            return result
        except Exception as e:
            logger.error(f"Error getting recipe info for AI GM: {e}")
            return {}
    
    def integrate_with_ai_gm_brain(self, ai_gm_brain: Any) -> None:
        """
        Integrate crafting system data with the AI GM Brain.
        
        Args:
            ai_gm_brain: The AI GM Brain instance to integrate with
        """
        try:
            # Get all materials
            materials = self.db.query(DBMaterial).all()
            material_data = {}
            
            for material in materials:
                material_data[material.name] = {
                    "id": material.id,
                    "description": material.description,
                    "material_type": material.material_type,
                    "rarity": material.rarity,
                    "base_value": material.base_value,
                    "properties": material.properties,
                    "source_tags": material.source_tags
                }
            
            # Get all recipes
            recipes = self.db.query(DBRecipe).all()
            recipe_data = {}
            
            for recipe in recipes:
                # Get primary output
                primary_output = (
                    self.db.query(DBRecipeOutput)
                    .filter(DBRecipeOutput.recipe_id == recipe.id, DBRecipeOutput.is_primary == True)
                    .first()
                )
                
                output_material = None
                if primary_output:
                    output_material = (
                        self.db.query(DBMaterial)
                        .filter(DBMaterial.id == primary_output.item_id)
                        .first()
                    )
                
                recipe_data[recipe.name] = {
                    "id": recipe.id,
                    "description": recipe.description,
                    "recipe_category": recipe.recipe_category,
                    "difficulty_level": recipe.difficulty_level,
                    "output_item": output_material.name if output_material else "Unknown"
                }
            
            # Add crafting data to AI GM Brain's knowledge base
            ai_gm_brain.knowledge_base["crafting_materials"] = material_data
            ai_gm_brain.knowledge_base["crafting_recipes"] = recipe_data
            
            logger.info("Successfully integrated crafting system with AI GM Brain.")
        except Exception as e:
            logger.error(f"Error integrating with AI GM Brain: {e}")
    
    def generate_region_material_availability(self, region_id: str) -> Dict[str, Any]:
        """
        Generate material availability information for a specific region.
        
        Args:
            region_id: The region ID to generate availability for
            
        Returns:
            A dictionary with material availability information
        """
        try:
            # Get all materials
            materials = self.db.query(DBMaterial).all()
            
            availability = {
                "common": [],
                "uncommon": [],
                "rare": [],
                "epic": [],
                "legendary": [],
                "illicit": []
            }
            
            for material in materials:
                # Check if material is illicit in this region
                if region_id in material.illicit_in_regions:
                    availability["illicit"].append({
                        "name": material.name,
                        "material_type": material.material_type,
                        "base_value": material.base_value
                    })
                    continue
                
                # Check if material is available in this region based on source tags
                region_related = False
                for tag in material.source_tags:
                    if region_id.lower() in tag.lower():
                        region_related = True
                        break
                
                if region_related:
                    rarity = material.rarity.lower()
                    if rarity in availability:
                        availability[rarity].append({
                            "name": material.name,
                            "material_type": material.material_type,
                            "base_value": material.base_value
                        })
            
            return availability
        except Exception as e:
            logger.error(f"Error generating region material availability: {e}")
            return {}
    
    def get_profession_skill_information(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get information about crafting professions and their associated skills.
        
        Returns:
            A dictionary mapping profession names to lists of skill information
        """
        try:
            # Define profession categories
            professions = {
                "Blacksmithing": ["Blacksmithing", "Weaponsmithing", "Armorsmithing"],
                "Alchemy": ["Alchemy", "Herbalism", "Poison Craft"],
                "Woodworking": ["Woodworking", "Carpentry", "Furniture Making"],
                "Tailoring": ["Tailoring", "Weaving", "Embroidery"],
                "Leatherworking": ["Leatherworking", "Tanning", "Leathercrafting"],
                "Jewelcrafting": ["Jewelcrafting", "Gemcutting", "Silversmithing", "Goldsmithing"],
                "Relicsmithing": ["Relicsmithing", "Containment Artifice", "Sound Artifice"]
            }
            
            # Get all recipes
            recipes = self.db.query(DBRecipe).all()
            
            # Map skills to required levels
            skill_requirements = {}
            for profession, skills in professions.items():
                skill_requirements[profession] = []
                
                for skill in skills:
                    max_level = 0
                    recipe_examples = []
                    
                    # Find recipes that require this skill
                    relevant_recipes = []
                    for recipe in recipes:
                        if profession in recipe.recipe_category:
                            relevant_recipes.append(recipe)
                    
                    # Check the skill level requirements
                    for recipe in relevant_recipes:
                        # Get skill requirements
                        skill_reqs = self.db.query(DBSkillRequirement).filter(
                            DBSkillRequirement.recipe_id == recipe.id,
                            DBSkillRequirement.skill_name == skill
                        ).all()
                        
                        for req in skill_reqs:
                            if req.level > max_level:
                                max_level = req.level
                                
                            # Add example recipe
                            if len(recipe_examples) < 3:  # Limit to 3 examples
                                recipe_examples.append(recipe.name)
                    
                    if max_level > 0:
                        skill_requirements[profession].append({
                            "skill_name": skill,
                            "max_level_observed": max_level,
                            "example_recipes": recipe_examples
                        })
            
            return skill_requirements
        except Exception as e:
            logger.error(f"Error getting profession skill information: {e}")
            return {}

# Factory function to create the service
def create_crafting_integration_service() -> CraftingIntegrationService:
    """Create and return a new CraftingIntegrationService instance."""
    return CraftingIntegrationService()