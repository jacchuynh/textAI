"""
Crafting System API

This module provides a unified API for the material and recipe system.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from sqlalchemy.orm import Session

from backend.src.crafting.services.material_service import material_service
from backend.src.crafting.services.recipe_service import recipe_service
from backend.src.crafting.services.crafting_service import crafting_service
from backend.src.crafting.models.pydantic_models import (
    Material, Recipe, CraftingResult, MaterialType, Rarity,
    RecipeIngredient, RecipeOutput
)

logger = logging.getLogger(__name__)

class CraftingAPI:
    """
    Provides a unified API for all crafting system operations.
    This class serves as the main entry point for interacting with the crafting system.
    """
    
    def __init__(self, event_bus=None, inventory_service=None, player_service=None):
        """
        Initialize the crafting API with optional service dependencies.
        
        Args:
            event_bus: Optional event bus for publishing events
            inventory_service: Optional inventory service for inventory operations
            player_service: Optional player service for player operations
        """
        self.event_bus = event_bus
        self.inventory_service = inventory_service
        self.player_service = player_service
        self.logger = logging.getLogger("CraftingAPI")
    
    # === Material Management ===
    
    def create_material(self, db: Session, material_data: Material) -> Material:
        """
        Create a new material.
        
        Args:
            db: Database session
            material_data: Material data
            
        Returns:
            Created material
        """
        return material_service.create_material(db=db, material_data=material_data)
    
    def get_material(self, db: Session, material_id: str) -> Optional[Material]:
        """
        Get a material by ID.
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            Material if found, None otherwise
        """
        return material_service.get_material(db=db, material_id=material_id)
    
    def get_material_by_name(self, db: Session, name: str) -> Optional[Material]:
        """
        Get a material by name.
        
        Args:
            db: Database session
            name: Material name
            
        Returns:
            Material if found, None otherwise
        """
        return material_service.get_material_by_name(db=db, name=name)
    
    def get_materials(
        self, db: Session, skip: int = 0, limit: int = 100, 
        material_type: Optional[MaterialType] = None,
        rarity: Optional[Rarity] = None,
        source_tag: Optional[str] = None,
        search_term: Optional[str] = None,
        craftable_only: bool = False
    ) -> List[Material]:
        """
        Get materials with various filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            material_type: Optional filter by material type
            rarity: Optional filter by rarity
            source_tag: Optional filter by source tag
            search_term: Optional search term
            craftable_only: Whether to only return craftable materials
            
        Returns:
            List of materials
        """
        if material_type:
            return material_service.get_materials_by_type(
                db=db, material_type=material_type, skip=skip, limit=limit
            )
        elif rarity:
            return material_service.get_materials_by_rarity(
                db=db, rarity=rarity, skip=skip, limit=limit
            )
        elif source_tag:
            return material_service.get_materials_by_source_tag(
                db=db, source_tag=source_tag, skip=skip, limit=limit
            )
        elif search_term:
            return material_service.search_materials(
                db=db, search_term=search_term, skip=skip, limit=limit
            )
        elif craftable_only:
            return material_service.get_craftable_materials(
                db=db, skip=skip, limit=limit
            )
        else:
            return material_service.get_materials(
                db=db, skip=skip, limit=limit
            )
    
    def update_material(
        self, db: Session, material_id: str, material_data: Union[Material, Dict[str, Any]]
    ) -> Optional[Material]:
        """
        Update a material.
        
        Args:
            db: Database session
            material_id: Material ID
            material_data: Updated material data
            
        Returns:
            Updated material or None if not found
        """
        return material_service.update_material(
            db=db, material_id=material_id, material_data=material_data
        )
    
    def delete_material(self, db: Session, material_id: str) -> Optional[Material]:
        """
        Delete a material.
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            Deleted material or None if not found
        """
        return material_service.delete_material(db=db, material_id=material_id)
    
    def get_material_recipes(
        self, db: Session, material_id: str, as_ingredient: bool = True, as_output: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get recipes related to a material (either as ingredient or output).
        
        Args:
            db: Database session
            material_id: Material ID
            as_ingredient: Whether to include recipes where the material is an ingredient
            as_output: Whether to include recipes where the material is an output
            
        Returns:
            Dictionary with recipes where the material is used or produced
        """
        return material_service.get_material_recipes(
            db=db, material_id=material_id, as_ingredient=as_ingredient, as_output=as_output
        )
    
    def get_illicit_materials(
        self, db: Session, region_id: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get materials that are considered illicit, optionally in a specific region.
        
        Args:
            db: Database session
            region_id: Optional region ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of illicit materials
        """
        return material_service.get_illicit_materials(
            db=db, region_id=region_id, skip=skip, limit=limit
        )
    
    # === Recipe Management ===
    
    def create_recipe(self, db: Session, recipe_data: Recipe) -> Recipe:
        """
        Create a new recipe.
        
        Args:
            db: Database session
            recipe_data: Recipe data
            
        Returns:
            Created recipe
        """
        return recipe_service.create_recipe(db=db, recipe_data=recipe_data)
    
    def get_recipe(self, db: Session, recipe_id: str) -> Optional[Recipe]:
        """
        Get a recipe by ID.
        
        Args:
            db: Database session
            recipe_id: Recipe ID
            
        Returns:
            Recipe if found, None otherwise
        """
        return recipe_service.get_recipe(db=db, recipe_id=recipe_id)
    
    def get_recipe_by_name(self, db: Session, name: str) -> Optional[Recipe]:
        """
        Get a recipe by name.
        
        Args:
            db: Database session
            name: Recipe name
            
        Returns:
            Recipe if found, None otherwise
        """
        return recipe_service.get_recipe_by_name(db=db, name=name)
    
    def get_recipes(
        self, db: Session, skip: int = 0, limit: int = 100,
        category: Optional[str] = None,
        output_item_id: Optional[str] = None,
        ingredient_item_id: Optional[str] = None,
        station_type: Optional[str] = None,
        search_term: Optional[str] = None,
        discoverable_only: bool = False
    ) -> List[Recipe]:
        """
        Get recipes with various filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Optional filter by category
            output_item_id: Optional filter by output item
            ingredient_item_id: Optional filter by ingredient item
            station_type: Optional filter by station type
            search_term: Optional search term
            discoverable_only: Whether to only return discoverable recipes
            
        Returns:
            List of recipes
        """
        if category:
            return recipe_service.get_recipes_by_category(
                db=db, category=category, skip=skip, limit=limit
            )
        elif output_item_id:
            return recipe_service.get_recipes_by_output_item(
                db=db, item_id=output_item_id, skip=skip, limit=limit
            )
        elif ingredient_item_id:
            return recipe_service.get_recipes_by_ingredient(
                db=db, item_id=ingredient_item_id, skip=skip, limit=limit
            )
        elif station_type:
            return recipe_service.get_recipes_by_station_type(
                db=db, station_type=station_type, skip=skip, limit=limit
            )
        elif search_term:
            return recipe_service.search_recipes(
                db=db, search_term=search_term, skip=skip, limit=limit
            )
        elif discoverable_only:
            return recipe_service.get_discoverable_recipes(
                db=db, skip=skip, limit=limit
            )
        else:
            return recipe_service.get_recipes(
                db=db, skip=skip, limit=limit
            )
    
    def update_recipe(
        self, db: Session, recipe_id: str, recipe_data: Recipe
    ) -> Optional[Recipe]:
        """
        Update a recipe.
        
        Args:
            db: Database session
            recipe_id: Recipe ID
            recipe_data: Updated recipe data
            
        Returns:
            Updated recipe or None if not found
        """
        return recipe_service.update_recipe(
            db=db, recipe_id=recipe_id, recipe_data=recipe_data
        )
    
    def delete_recipe(self, db: Session, recipe_id: str) -> Optional[Recipe]:
        """
        Delete a recipe.
        
        Args:
            db: Database session
            recipe_id: Recipe ID
            
        Returns:
            Deleted recipe or None if not found
        """
        return recipe_service.delete_recipe(db=db, recipe_id=recipe_id)
    
    # === Player Recipe Knowledge ===
    
    def is_recipe_known_by_player(
        self, db: Session, player_id: str, recipe_id: str
    ) -> bool:
        """
        Check if a recipe is known by a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            True if the recipe is known, False otherwise
        """
        return recipe_service.is_recipe_known_by_player(
            db=db, player_id=player_id, recipe_id=recipe_id
        )
    
    def get_known_recipes_for_player(
        self, db: Session, player_id: str, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all recipes known by a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of known recipes with additional player-specific data
        """
        return recipe_service.get_known_recipes_for_player(
            db=db, player_id=player_id, skip=skip, limit=limit
        )
    
    def learn_recipe_for_player(
        self, db: Session, player_id: str, recipe_id: str
    ) -> bool:
        """
        Add a recipe to a player's known recipes.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            True if successful, False if recipe not found
        """
        result = recipe_service.learn_recipe_for_player(
            db=db, player_id=player_id, recipe_id=recipe_id
        )
        
        # Publish event if successful and event bus is available
        if result and self.event_bus:
            recipe = recipe_service.get_recipe(db=db, recipe_id=recipe_id)
            recipe_name = recipe.name if recipe else "Unknown Recipe"
            
            self.event_bus.publish(
                event_type="player_learned_recipe",
                event_data={
                    "player_id": player_id,
                    "recipe_id": recipe_id,
                    "recipe_name": recipe_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return result
    
    def forget_recipe_for_player(
        self, db: Session, player_id: str, recipe_id: str
    ) -> bool:
        """
        Remove a recipe from a player's known recipes.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            True if successful, False if not found
        """
        return recipe_service.forget_recipe_for_player(
            db=db, player_id=player_id, recipe_id=recipe_id
        )
    
    def get_learnable_recipes_for_player(
        self, db: Session, player_id: str, 
        skills_data: Dict[str, int] = None, 
        check_auto_learn: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get recipes that a player can learn based on their skills and other conditions.
        
        Args:
            db: Database session
            player_id: ID of the player
            skills_data: Player's skill levels
            check_auto_learn: Whether to check for auto-learn recipes
            
        Returns:
            List of learnable recipes
        """
        return recipe_service.get_learnable_recipes_for_player(
            db=db, player_id=player_id, skills_data=skills_data, check_auto_learn=check_auto_learn
        )
    
    # === Crafting Operations ===
    
    def can_player_craft_recipe(
        self, db: Session, player_id: str, recipe_id: str, quantity_to_craft: int = 1,
        **context_data
    ) -> Tuple[bool, str]:
        """
        Check if a player can craft a specific recipe.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            quantity_to_craft: Quantity to craft
            context_data: Additional context data (inventory, skills, etc.)
            
        Returns:
            Tuple of (can_craft, reason)
        """
        return crafting_service.can_character_craft_recipe(
            db=db,
            player_id=player_id,
            recipe_id=recipe_id,
            quantity_to_craft=quantity_to_craft,
            inventory_data=context_data.get("inventory_data"),
            skills_data=context_data.get("skills_data"),
            available_tools=context_data.get("available_tools"),
            available_stations=context_data.get("available_stations"),
            location_data=context_data.get("location_data")
        )
    
    def craft_item(
        self, db: Session, player_id: str, recipe_id: str, quantity_to_craft: int = 1,
        **context_data
    ) -> CraftingResult:
        """
        Attempt to craft an item.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            quantity_to_craft: Quantity to craft
            context_data: Additional context data (inventory, skills, business_id, etc.)
            
        Returns:
            CraftingResult with details of the crafting attempt
        """
        return crafting_service.attempt_craft_item(
            db=db,
            player_id=player_id,
            recipe_id=recipe_id,
            quantity_to_craft=quantity_to_craft,
            inventory_service=self.inventory_service,
            player_service=self.player_service,
            event_bus=self.event_bus,
            inventory_data=context_data.get("inventory_data"),
            skills_data=context_data.get("skills_data"),
            available_tools=context_data.get("available_tools"),
            available_stations=context_data.get("available_stations"),
            location_data=context_data.get("location_data"),
            business_id=context_data.get("business_id"),
            custom_quality_modifier=context_data.get("quality_modifier")
        )
    
    def attempt_recipe_discovery(
        self, db: Session, player_id: str, provided_ingredients: List[Dict[str, Any]],
        **context_data
    ) -> Optional[Recipe]:
        """
        Attempt to discover a new recipe through experimentation.
        
        Args:
            db: Database session
            player_id: ID of the player
            provided_ingredients: List of ingredients provided
            context_data: Additional context data (skills, tools, etc.)
            
        Returns:
            Discovered recipe or None if discovery failed
        """
        discovered_recipe = crafting_service.discover_recipe_attempt(
            db=db,
            player_id=player_id,
            provided_ingredients=provided_ingredients,
            skills_data=context_data.get("skills_data"),
            available_tools=context_data.get("available_tools"),
            available_stations=context_data.get("available_stations"),
            location_data=context_data.get("location_data")
        )
        
        # Publish event if successful and event bus is available
        if discovered_recipe and self.event_bus:
            self.event_bus.publish(
                event_type="player_discovered_recipe",
                event_data={
                    "player_id": player_id,
                    "recipe_id": discovered_recipe.id,
                    "recipe_name": discovered_recipe.name,
                    "ingredients_used": [
                        {"item_id": ing.get("item_id"), "quantity": ing.get("quantity", 1)}
                        for ing in provided_ingredients
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return discovered_recipe
    
    def get_crafting_history(
        self, db: Session, player_id: str, skip: int = 0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get a player's crafting history.
        
        Args:
            db: Database session
            player_id: ID of the player
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of crafting log entries
        """
        return crafting_service.get_crafting_history(
            db=db, player_id=player_id, skip=skip, limit=limit
        )
    
    def get_popular_recipes(
        self, db: Session, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most popular recipes based on crafting frequency.
        
        Args:
            db: Database session
            limit: Maximum number of recipes to return
            
        Returns:
            List of popular recipes with crafting counts
        """
        return crafting_service.get_popular_recipes(db=db, limit=limit)
    
    # === Business Integration ===
    
    def get_business_recipes(
        self, db: Session, business_id: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes that can be crafted at a specific business.
        
        Args:
            db: Database session
            business_id: ID of the business
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        # This would typically query the business for its stations/capabilities
        # and then filter recipes based on those
        # For simplicity, we'll just get all recipes
        return recipe_service.get_recipes(db=db, skip=skip, limit=limit)
    
    def get_business_crafting_history(
        self, db: Session, business_id: str, skip: int = 0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get crafting history for a specific business.
        
        Args:
            db: Database session
            business_id: ID of the business
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of crafting log entries
        """
        # Query crafting logs where business_id matches
        # This would be implemented based on your specific database schema
        # For now, just return an empty list
        return []
    
    def craft_item_for_business(
        self, db: Session, player_id: str, business_id: str, 
        recipe_id: str, quantity_to_craft: int = 1,
        **context_data
    ) -> CraftingResult:
        """
        Craft an item for a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            recipe_id: ID of the recipe
            quantity_to_craft: Quantity to craft
            context_data: Additional context data
            
        Returns:
            CraftingResult with details of the crafting attempt
        """
        # Include business_id in context_data
        context_data["business_id"] = business_id
        
        # Get business-specific context data
        # This would typically query the business for its stations/inventory/etc.
        # and merge with the provided context_data
        
        # Delegate to the regular craft_item method
        return self.craft_item(
            db=db,
            player_id=player_id,
            recipe_id=recipe_id,
            quantity_to_craft=quantity_to_craft,
            **context_data
        )
    
    # === Integration with Building System ===
    
    def get_recipes_for_station(
        self, db: Session, station_type: str, building_id: Optional[str] = None,
        skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes that can be crafted at a specific station type, optionally in a specific building.
        
        Args:
            db: Database session
            station_type: Type of crafting station
            building_id: Optional ID of the building
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        # Get recipes that require this station type
        recipes = recipe_service.get_recipes_by_station_type(
            db=db, station_type=station_type, skip=skip, limit=limit
        )
        
        # If building_id is provided, we could further filter based on
        # the building's capabilities, upgrades, etc.
        # This would depend on your building system's implementation
        
        return recipes
    
    def get_building_crafting_capabilities(
        self, db: Session, building_id: str
    ) -> Dict[str, Any]:
        """
        Get the crafting capabilities of a building.
        
        Args:
            db: Database session
            building_id: ID of the building
            
        Returns:
            Dictionary with crafting capabilities
        """
        # This would query the building system to get the building's
        # crafting stations, bonuses, etc.
        # For simplicity, just return placeholder data
        return {
            "building_id": building_id,
            "station_types": ["basic_workbench"],  # Placeholder
            "quality_bonuses": {"crafting": 0.1},  # Placeholder
            "efficiency_bonuses": {"crafting_speed": 0.05}  # Placeholder
        }

# This would be the actual instance used by your application
# with the appropriate service instances injected
crafting_api = CraftingAPI(
    # event_bus=event_bus_instance,
    # inventory_service=inventory_service_instance,
    # player_service=player_service_instance
)