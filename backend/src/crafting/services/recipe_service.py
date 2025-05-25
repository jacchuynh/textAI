"""
Recipe Service

This module provides services for managing recipes in the crafting system.
"""

import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from sqlalchemy.orm import Session

from backend.src.crafting.db.crud import recipe as crud_recipe
from backend.src.crafting.db.crud import player_known_recipe as crud_player_known_recipe
from backend.src.crafting.models.pydantic_models import Recipe, RecipeIngredient, RecipeOutput, SkillRequirement

class RecipeService:
    """
    Service for managing recipes in the crafting system.
    """
    
    def create_recipe(self, db: Session, recipe_data: Recipe) -> Recipe:
        """
        Create a new recipe with all related data (ingredients, outputs, skills).
        
        Args:
            db: Database session
            recipe_data: Complete recipe data
            
        Returns:
            Created recipe
        """
        # Generate UUID if not provided
        if not recipe_data.id:
            recipe_data.id = str(uuid.uuid4())
        
        # Create the recipe with all relationships
        db_recipe = crud_recipe.create_recipe_with_relationships(db=db, recipe_data=recipe_data)
        
        # Convert DB model to Pydantic model (this would need to handle relationships too)
        return self._db_recipe_to_pydantic(db_recipe)
    
    def get_recipe(self, db: Session, recipe_id: str) -> Optional[Recipe]:
        """
        Get a recipe by ID.
        
        Args:
            db: Database session
            recipe_id: Recipe ID
            
        Returns:
            Recipe if found, None otherwise
        """
        db_recipe = crud_recipe.get(db=db, id=recipe_id)
        if db_recipe:
            return self._db_recipe_to_pydantic(db_recipe)
        return None
    
    def get_recipe_by_name(self, db: Session, name: str) -> Optional[Recipe]:
        """
        Get a recipe by name.
        
        Args:
            db: Database session
            name: Recipe name
            
        Returns:
            Recipe if found, None otherwise
        """
        db_recipe = crud_recipe.get_by_name(db=db, name=name)
        if db_recipe:
            return self._db_recipe_to_pydantic(db_recipe)
        return None
    
    def get_recipes(self, db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """
        Get multiple recipes with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        db_recipes = crud_recipe.get_multi(db=db, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def get_recipes_by_category(
        self, db: Session, category: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes by category.
        
        Args:
            db: Database session
            category: Recipe category
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        db_recipes = crud_recipe.get_by_category(db=db, category=category, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def get_recipes_by_output_item(
        self, db: Session, item_id: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes that produce a specific item.
        
        Args:
            db: Database session
            item_id: ID of the output item
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        db_recipes = crud_recipe.get_by_output_item(db=db, item_id=item_id, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def get_recipes_by_ingredient(
        self, db: Session, item_id: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes that use a specific ingredient.
        
        Args:
            db: Database session
            item_id: ID of the ingredient
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        db_recipes = crud_recipe.get_by_ingredient(db=db, item_id=item_id, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def get_recipes_by_station_type(
        self, db: Session, station_type: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes that require a specific station type.
        
        Args:
            db: Database session
            station_type: Type of crafting station
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of recipes
        """
        db_recipes = crud_recipe.get_by_station_type(db=db, station_type=station_type, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def get_discoverable_recipes(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Get recipes that can be discovered.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of discoverable recipes
        """
        db_recipes = crud_recipe.get_discoverable_recipes(db=db, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def search_recipes(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """
        Search for recipes by name or description.
        
        Args:
            db: Database session
            search_term: Term to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching recipes
        """
        db_recipes = crud_recipe.search_recipes(db=db, search_term=search_term, skip=skip, limit=limit)
        return [self._db_recipe_to_pydantic(r) for r in db_recipes]
    
    def update_recipe(
        self, db: Session, recipe_id: str, recipe_data: Recipe
    ) -> Optional[Recipe]:
        """
        Update a recipe with all related data.
        
        Args:
            db: Database session
            recipe_id: Recipe ID
            recipe_data: Updated recipe data
            
        Returns:
            Updated recipe or None if not found
        """
        db_recipe = crud_recipe.get(db=db, id=recipe_id)
        if not db_recipe:
            return None
        
        # Ensure recipe_data has the correct ID
        recipe_data.id = recipe_id
        
        updated_recipe = crud_recipe.update_recipe_with_relationships(
            db=db, db_obj=db_recipe, obj_in=recipe_data
        )
        return self._db_recipe_to_pydantic(updated_recipe)
    
    def delete_recipe(self, db: Session, recipe_id: str) -> Optional[Recipe]:
        """
        Delete a recipe.
        
        Args:
            db: Database session
            recipe_id: Recipe ID
            
        Returns:
            Deleted recipe or None if not found
        """
        db_recipe = crud_recipe.get(db=db, id=recipe_id)
        if not db_recipe:
            return None
        
        # Convert to Pydantic model before deletion for return value
        recipe = self._db_recipe_to_pydantic(db_recipe)
        
        # Delete the recipe (this should cascade to related entities)
        crud_recipe.remove(db=db, id=recipe_id)
        
        return recipe
    
    # === Player Recipe Knowledge Management ===
    
    def is_recipe_known_by_player(self, db: Session, player_id: str, recipe_id: str) -> bool:
        """
        Check if a recipe is known by a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            True if the recipe is known, False otherwise
        """
        return crud_player_known_recipe.is_recipe_known_by_player(
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
        known_recipe_records = crud_player_known_recipe.get_player_known_recipes(
            db=db, player_id=player_id, skip=skip, limit=limit
        )
        
        result = []
        for record in known_recipe_records:
            # Get the full recipe
            db_recipe = crud_recipe.get(db=db, id=record.recipe_id)
            if db_recipe:
                recipe_data = self._db_recipe_to_pydantic(db_recipe).dict()
                # Add player-specific data
                recipe_data.update({
                    "mastery_level": record.mastery_level,
                    "times_crafted": record.times_crafted,
                    "highest_quality_crafted": record.highest_quality_crafted,
                    "discovery_date": record.discovery_date,
                })
                result.append(recipe_data)
        
        return result
    
    def learn_recipe_for_player(self, db: Session, player_id: str, recipe_id: str) -> bool:
        """
        Add a recipe to a player's known recipes.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            True if successful, False if recipe not found
        """
        # Check if recipe exists
        db_recipe = crud_recipe.get(db=db, id=recipe_id)
        if not db_recipe:
            return False
        
        # Add recipe to player's known recipes
        crud_player_known_recipe.add_recipe_to_player(
            db=db, player_id=player_id, recipe_id=recipe_id
        )
        
        return True
    
    def forget_recipe_for_player(self, db: Session, player_id: str, recipe_id: str) -> bool:
        """
        Remove a recipe from a player's known recipes.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            True if successful, False if not found
        """
        result = crud_player_known_recipe.remove_recipe_from_player(
            db=db, player_id=player_id, recipe_id=recipe_id
        )
        return result is not None
    
    def update_recipe_mastery(
        self, db: Session, player_id: str, recipe_id: str, mastery_level: int
    ) -> bool:
        """
        Update a player's mastery level for a recipe.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            mastery_level: New mastery level
            
        Returns:
            True if successful, False if not found
        """
        result = crud_player_known_recipe.update_mastery_level(
            db=db, player_id=player_id, recipe_id=recipe_id, mastery_level=mastery_level
        )
        return result is not None
    
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
        if skills_data is None:
            skills_data = {}
        
        # Get all recipes
        all_recipes = crud_recipe.get_multi(db=db)
        
        # Filter out already known recipes
        known_recipes = set()
        for record in crud_player_known_recipe.get_player_known_recipes(db=db, player_id=player_id):
            known_recipes.add(record.recipe_id)
        
        learnable_recipes = []
        
        for db_recipe in all_recipes:
            # Skip already known recipes
            if db_recipe.id in known_recipes:
                continue
            
            recipe_data = self._db_recipe_to_pydantic(db_recipe)
            
            # Check if recipe should be auto-learned based on skill level
            if check_auto_learn and recipe_data.auto_learn_at_skill_level:
                skill_name = recipe_data.auto_learn_at_skill_level.skill_name
                required_level = recipe_data.auto_learn_at_skill_level.level
                
                if skills_data.get(skill_name, 0) >= required_level:
                    # Auto-learn the recipe
                    crud_player_known_recipe.add_recipe_to_player(
                        db=db, player_id=player_id, recipe_id=db_recipe.id
                    )
                    continue  # Skip adding to learnable list since it's now known
            
            # Check if player meets unlock conditions
            meets_conditions = True
            
            # Check for character level requirement
            if "min_character_level" in db_recipe.unlock_conditions:
                required_level = db_recipe.unlock_conditions["min_character_level"]
                # This would need to get the player's level from wherever it's stored
                player_level = skills_data.get("character_level", 0)
                if player_level < required_level:
                    meets_conditions = False
            
            # Check for skill requirements
            for skill_req in db_recipe.required_skills:
                if skills_data.get(skill_req.skill_name, 0) < skill_req.level:
                    meets_conditions = False
                    break
            
            # Check other custom unlock conditions
            # (These would depend on your specific game mechanics)
            
            if meets_conditions:
                learnable_recipe = {
                    "id": db_recipe.id,
                    "name": db_recipe.name,
                    "description": db_recipe.description,
                    "category": db_recipe.recipe_category,
                    "difficulty_level": db_recipe.difficulty_level,
                    "required_skills": [
                        {"skill_name": s.skill_name, "level": s.level}
                        for s in recipe_data.required_skills
                    ],
                    "unlock_conditions": db_recipe.unlock_conditions
                }
                learnable_recipes.append(learnable_recipe)
        
        return learnable_recipes
    
    # Helper methods
    def _db_recipe_to_pydantic(self, db_recipe) -> Recipe:
        """Convert a DB recipe model to a Pydantic model, handling relationships."""
        # Get primary output
        primary_output = next(
            (
                RecipeOutput(
                    item_id=output.item_id,
                    quantity=output.quantity,
                    chance=output.chance,
                    quality_modifier=output.quality_modifier,
                    custom_data=output.custom_data
                )
                for output in db_recipe.outputs if output.is_primary
            ),
            RecipeOutput(item_id="unknown", quantity=1)  # Fallback if none found
        )
        
        # Get byproducts (non-primary outputs)
        byproducts = [
            RecipeOutput(
                item_id=output.item_id,
                quantity=output.quantity,
                chance=output.chance,
                quality_modifier=output.quality_modifier,
                custom_data=output.custom_data
            )
            for output in db_recipe.outputs if not output.is_primary
        ]
        
        # Get ingredients
        ingredients = [
            RecipeIngredient(
                item_id=ingredient.item_id,
                quantity=ingredient.quantity,
                can_be_substituted=ingredient.can_be_substituted,
                possible_substitutes=ingredient.possible_substitutes,
                consumed_in_crafting=ingredient.consumed_in_crafting
            )
            for ingredient in db_recipe.ingredients
        ]
        
        # Get skill requirements
        required_skills = [
            SkillRequirement(
                skill_name=skill.skill_name,
                level=skill.level,
                affects_quality=skill.affects_quality,
                affects_speed=skill.affects_speed
            )
            for skill in db_recipe.required_skills
        ]
        
        # Create and return the Pydantic model
        return Recipe(
            id=db_recipe.id,
            name=db_recipe.name,
            description=db_recipe.description,
            primary_output=primary_output,
            byproducts=byproducts,
            ingredients=ingredients,
            crafting_time_seconds=db_recipe.crafting_time_seconds,
            required_skills=required_skills,
            required_tools=db_recipe.required_tools,
            required_station_type=db_recipe.required_station_type,
            unlock_conditions=db_recipe.unlock_conditions,
            experience_gained=db_recipe.experience_gained,
            is_discoverable=db_recipe.is_discoverable,
            auto_learn_at_skill_level=None,  # This would need special handling
            difficulty_level=db_recipe.difficulty_level,
            recipe_category=db_recipe.recipe_category,
            quality_range=db_recipe.quality_range,
            region_specific=db_recipe.region_specific,
            failure_outputs=[],  # This would need to be populated from somewhere
            custom_data=db_recipe.custom_data
        )

# Create a singleton instance
recipe_service = RecipeService()