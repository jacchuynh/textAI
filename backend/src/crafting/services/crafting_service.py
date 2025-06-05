"""
Crafting Service

This module provides services for crafting items in the game.
"""

import uuid
import random
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.crafting.db.crud import recipe as crud_recipe
from backend.src.crafting.db.crud import player_known_recipe as crud_player_known_recipe
from backend.src.crafting.db.crud import crafting_log as crud_crafting_log
from backend.src.crafting.models.pydantic_models import Recipe, CraftingResult
from backend.src.crafting.services.recipe_service import recipe_service

# Import Celery integration for async processing
try:
    from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
    from backend.src.narrative_engine.event_bus import get_event_bus, Event
    ASYNC_FEATURES_AVAILABLE = True
except ImportError:
    ASYNC_FEATURES_AVAILABLE = False

logger = logging.getLogger(__name__)

class CraftingService:
    """
    Service for handling crafting operations in the game.
    """
    
    def __init__(self):
        """Initialize the crafting service."""
        # Initialize async features if available
        if ASYNC_FEATURES_AVAILABLE:
            self.event_bus = get_event_bus()
            self.celery_integration = NarrativeEngineCeleryIntegration()
            
            # Subscribe to relevant events
            self.event_bus.subscribe("crafting_started", self._handle_crafting_started)
            self.event_bus.subscribe("crafting_completed", self._handle_crafting_completed)
            self.event_bus.subscribe("crafting_failed", self._handle_crafting_failed)
            self.event_bus.subscribe("recipe_discovered", self._handle_recipe_discovered)
        else:
            self.event_bus = None
            self.celery_integration = None
    
    def can_character_craft_recipe(
        self, 
        db: Session, 
        player_id: str, 
        recipe_id: str, 
        quantity_to_craft: int = 1,
        inventory_data: Optional[Dict[str, Any]] = None,
        skills_data: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        available_stations: Optional[List[str]] = None,
        location_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Check if a character can craft a specific recipe.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            quantity_to_craft: Quantity to craft
            inventory_data: Player's inventory data
            skills_data: Player's skills data
            available_tools: Available tools
            available_stations: Available crafting stations
            location_data: Current location data
            
        Returns:
            Tuple of (can_craft, reason)
        """
        # Get the recipe
        recipe = recipe_service.get_recipe(db=db, recipe_id=recipe_id)
        if not recipe:
            return False, f"Recipe with ID {recipe_id} not found."
        
        # Check if player knows the recipe
        if not crud_player_known_recipe.is_recipe_known_by_player(
            db=db, player_id=player_id, recipe_id=recipe_id
        ):
            return False, f"You don't know how to craft {recipe.name}."
        
        # Verify skills
        if skills_data is not None and recipe.required_skills:
            for skill_req in recipe.required_skills:
                player_skill_level = skills_data.get(skill_req.skill_name, 0)
                if player_skill_level < skill_req.level:
                    return False, f"You need {skill_req.skill_name} level {skill_req.level} to craft this (you have level {player_skill_level})."
        
        # Check required tools
        if available_tools is not None and recipe.required_tools:
            missing_tools = [tool for tool in recipe.required_tools if tool not in available_tools]
            if missing_tools:
                return False, f"You need the following tools: {', '.join(missing_tools)}."
        
        # Check required station
        if available_stations is not None and recipe.required_station_type:
            if recipe.required_station_type not in available_stations:
                return False, f"You need access to a {recipe.required_station_type} to craft this."
        
        # Check ingredients in inventory
        if inventory_data is not None:
            for ingredient in recipe.ingredients:
                required_quantity = ingredient.quantity * quantity_to_craft
                available_quantity = inventory_data.get(ingredient.item_id, 0)
                
                if available_quantity < required_quantity:
                    return False, f"You need {required_quantity} of item {ingredient.item_id} but only have {available_quantity}."
        
        # Check region-specific recipes
        if location_data is not None and recipe.region_specific:
            current_region = location_data.get("region_id")
            if current_region and current_region not in recipe.region_specific:
                return False, f"This recipe can only be crafted in specific regions: {', '.join(recipe.region_specific)}."
        
        return True, "You can craft this recipe."

    def attempt_craft_item(
        self,
        db: Session,
        player_id: str,
        recipe_id: str,
        quantity_to_craft: int = 1,
        inventory_service = None,  # Injected service
        player_service = None,     # Injected service
        event_bus = None,          # Injected event bus
        inventory_data: Optional[Dict[str, Any]] = None,
        skills_data: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        available_stations: Optional[List[str]] = None,
        location_data: Optional[Dict[str, Any]] = None,
        business_id: Optional[str] = None,
        custom_quality_modifier: Optional[float] = None
    ) -> CraftingResult:
        """
        Attempt to craft an item.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            quantity_to_craft: Quantity to craft
            inventory_service: Inventory service for updating inventory
            player_service: Player service for updating skills
            event_bus: Event bus for publishing events
            inventory_data: Player's inventory data
            skills_data: Player's skills data
            available_tools: Available tools
            available_stations: Available crafting stations
            location_data: Current location data
            business_id: Optional business ID (if crafting for a business)
            custom_quality_modifier: Optional quality modifier
            
        Returns:
            CraftingResult with details of the crafting attempt
        """
        # Check if player can craft this recipe
        can_craft, reason = self.can_character_craft_recipe(
            db=db,
            player_id=player_id,
            recipe_id=recipe_id,
            quantity_to_craft=quantity_to_craft,
            inventory_data=inventory_data,
            skills_data=skills_data,
            available_tools=available_tools,
            available_stations=available_stations,
            location_data=location_data
        )
        
        if not can_craft:
            return CraftingResult(
                success=False,
                message=reason,
                outputs=[],
                consumed_ingredients=[],
                experience_gained=[]
            )
        
        # Get the recipe
        recipe = recipe_service.get_recipe(db=db, recipe_id=recipe_id)
        
        # Calculate base success chance and quality
        success_chance, base_quality = self._calculate_crafting_success_chance(
            recipe=recipe,
            skills_data=skills_data,
            custom_quality_modifier=custom_quality_modifier
        )
        
        # Roll for success
        crafting_successful = random.random() <= success_chance
        
        # Record consumed ingredients (whether successful or not)
        consumed_ingredients = []
        for ingredient in recipe.ingredients:
            if ingredient.consumed_in_crafting:
                consumed_amount = ingredient.quantity * quantity_to_craft
                consumed_ingredients.append({
                    "item_id": ingredient.item_id,
                    "quantity": consumed_amount
                })
                
                # Update inventory if inventory service is provided
                if inventory_service:
                    inventory_service.remove_item(
                        db=db,
                        player_id=player_id,
                        item_id=ingredient.item_id,
                        quantity=consumed_amount,
                        business_id=business_id
                    )
        
        # Initialize outputs and experience
        outputs = []
        experience_gained = []
        
        if crafting_successful:
            # Calculate final quality based on skills and other factors
            quality_achieved = min(
                recipe.quality_range.get("max", 5),
                max(recipe.quality_range.get("min", 1), base_quality)
            )
            
            # Determine outputs based on success
            # Primary output
            outputs.append({
                "item_id": recipe.primary_output.item_id,
                "quantity": recipe.primary_output.quantity * quantity_to_craft,
                "quality": quality_achieved
            })
            
            # Byproducts (with chance rolls)
            for byproduct in recipe.byproducts:
                # Roll for each byproduct
                if random.random() <= byproduct.chance:
                    outputs.append({
                        "item_id": byproduct.item_id,
                        "quantity": byproduct.quantity * quantity_to_craft,
                        "quality": quality_achieved
                    })
            
            # Add items to inventory if inventory service is provided
            if inventory_service:
                for output in outputs:
                    inventory_service.add_item(
                        db=db,
                        player_id=player_id,
                        item_id=output["item_id"],
                        quantity=output["quantity"],
                        quality=output["quality"],
                        business_id=business_id
                    )
            
            # Calculate experience gained
            for exp_entry in recipe.experience_gained:
                skill_name = exp_entry.get("skill_name")
                base_xp = exp_entry.get("xp", 0)
                
                # Apply quality and quantity multipliers
                xp_gained = base_xp * quantity_to_craft * (1 + (quality_achieved - 1) * 0.1)
                
                experience_gained.append({
                    "skill_name": skill_name,
                    "xp_gained": xp_gained
                })
                
                # Update player skills if player service is provided
                if player_service:
                    player_service.add_skill_experience(
                        db=db,
                        player_id=player_id,
                        skill_name=skill_name,
                        experience=xp_gained
                    )
            
            # Update player's recipe mastery and times crafted
            self._update_recipe_mastery(
                db=db,
                player_id=player_id,
                recipe_id=recipe_id,
                quality_achieved=quality_achieved
            )
            
            result_message = f"Successfully crafted {quantity_to_craft} {recipe.name} with quality {quality_achieved}."
        else:
            # Handle failure
            # Check if there are failure outputs
            if recipe.failure_outputs:
                for failure_output in recipe.failure_outputs:
                    # Roll for each failure output
                    if random.random() <= failure_output.chance:
                        outputs.append({
                            "item_id": failure_output.item_id,
                            "quantity": failure_output.quantity * quantity_to_craft,
                            "quality": 1  # Failed items are usually low quality
                        })
                        
                        # Add items to inventory if inventory service is provided
                        if inventory_service:
                            inventory_service.add_item(
                                db=db,
                                player_id=player_id,
                                item_id=failure_output.item_id,
                                quantity=failure_output.quantity * quantity_to_craft,
                                quality=1,
                                business_id=business_id
                            )
            
            result_message = f"Failed to craft {recipe.name}. Some materials were lost in the process."
        
        # Calculate crafting time
        crafting_time = self._calculate_crafting_time(
            recipe=recipe,
            skills_data=skills_data,
            quantity=quantity_to_craft
        )
        
        # Create crafting log entry
        crafting_location = None
        if location_data:
            crafting_location = location_data.get("location_id")
        
        station_used = None
        if available_stations and recipe.required_station_type:
            station_used = recipe.required_station_type
        
        crud_crafting_log.create_crafting_log(
            db=db,
            player_id=player_id,
            recipe_id=recipe_id,
            success=crafting_successful,
            quantity_attempted=quantity_to_craft,
            quantity_produced=quantity_to_craft if crafting_successful else 0,
            quality_achieved=quality_achieved if crafting_successful else 0,
            ingredients_consumed=consumed_ingredients,
            outputs_produced=outputs,
            experience_gained=experience_gained,
            crafting_location=crafting_location,
            crafting_station_used=station_used,
            custom_data={
                "business_id": business_id,
                "success_chance": success_chance,
                "base_quality": base_quality
            }
        )
        
        # Publish event if event bus is provided
        if event_bus:
            event_data = {
                "player_id": player_id,
                "recipe_id": recipe_id,
                "recipe_name": recipe.name,
                "success": crafting_successful,
                "quantity": quantity_to_craft,
                "quality": quality_achieved if crafting_successful else 0,
                "ingredients": consumed_ingredients,
                "outputs": outputs,
                "experience": experience_gained,
                "business_id": business_id,
                "location": crafting_location,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            event_bus.publish(
                event_type="player_crafted_item",
                event_data=event_data
            )
        
        # Create and return CraftingResult
        return CraftingResult(
            success=crafting_successful,
            message=result_message,
            outputs=outputs,
            consumed_ingredients=consumed_ingredients,
            experience_gained=experience_gained,
            crafting_time_taken=crafting_time,
            quality_achieved=quality_achieved if crafting_successful else 0,
            skill_improvements=[],  # This would be populated by player_service
            recipe_mastery_gained=1 if crafting_successful else 0,
            custom_data={
                "recipe_id": recipe_id,
                "recipe_name": recipe.name,
                "business_id": business_id
            }
        )

    def discover_recipe_attempt(
        self,
        db: Session,
        player_id: str,
        provided_ingredients: List[Dict[str, Any]],
        skills_data: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        available_stations: Optional[List[str]] = None,
        location_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Recipe]:
        """
        Attempt to discover a new recipe through experimentation.
        
        Args:
            db: Database session
            player_id: ID of the player
            provided_ingredients: List of ingredients provided
            skills_data: Player's skills data
            available_tools: Available tools
            available_stations: Available crafting stations
            location_data: Current location data
            
        Returns:
            Discovered recipe or None if discovery failed
        """
        # Get all discoverable recipes
        discoverable_recipes = recipe_service.get_discoverable_recipes(db=db)
        
        # Filter out already known recipes
        known_recipes = set()
        for record in crud_player_known_recipe.get_player_known_recipes(db=db, player_id=player_id):
            known_recipes.add(record.recipe_id)
        
        discoverable_recipes = [r for r in discoverable_recipes if r.id not in known_recipes]
        
        # Convert provided ingredients to standardized format
        standardized_ingredients = {}
        for ingredient in provided_ingredients:
            item_id = ingredient.get("item_id")
            quantity = ingredient.get("quantity", 1)
            if item_id:
                standardized_ingredients[item_id] = quantity
        
        # Score each discoverable recipe based on ingredient match
        recipe_scores = []
        for recipe in discoverable_recipes:
            score = self._calculate_discovery_score(
                recipe=recipe,
                provided_ingredients=standardized_ingredients,
                skills_data=skills_data,
                available_tools=available_tools,
                available_stations=available_stations,
                location_data=location_data
            )
            recipe_scores.append((recipe, score))
        
        # Sort by score (highest first)
        recipe_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Check if the best match is good enough for discovery
        if recipe_scores and recipe_scores[0][1] > 0.7:  # Threshold for discovery
            discovered_recipe = recipe_scores[0][0]
            
            # Learn the recipe
            crud_player_known_recipe.add_recipe_to_player(
                db=db, player_id=player_id, recipe_id=discovered_recipe.id
            )
            
            # Return the discovered recipe
            return discovered_recipe
        
        return None

    def get_crafting_history(
        self,
        db: Session,
        player_id: str,
        skip: int = 0,
        limit: int = 20
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
        crafting_logs = crud_crafting_log.get_player_crafting_logs(
            db=db, player_id=player_id, skip=skip, limit=limit
        )
        
        result = []
        for log in crafting_logs:
            # Get recipe name
            recipe = None
            try:
                recipe = recipe_service.get_recipe(db=db, recipe_id=log.recipe_id)
            except:
                pass
            
            log_entry = {
                "id": log.id,
                "recipe_id": log.recipe_id,
                "recipe_name": recipe.name if recipe else "Unknown Recipe",
                "timestamp": log.timestamp.isoformat(),
                "success": log.success,
                "quantity_attempted": log.quantity_attempted,
                "quantity_produced": log.quantity_produced,
                "quality_achieved": log.quality_achieved,
                "ingredients_consumed": log.ingredients_consumed,
                "outputs_produced": log.outputs_produced,
                "experience_gained": log.experience_gained,
                "crafting_location": log.crafting_location,
                "crafting_station_used": log.crafting_station_used
            }
            result.append(log_entry)
        
        return result

    def get_popular_recipes(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most popular recipes based on crafting frequency.
        
        Args:
            db: Database session
            limit: Maximum number of recipes to return
            
        Returns:
            List of popular recipes with crafting counts
        """
        # This would typically be a more complex query in a real system
        # Here we're just counting crafting logs per recipe
        recipe_counts = {}
        
        # Get all crafting logs
        all_logs = db.query(crud_crafting_log.model).all()
        
        # Count successful crafts per recipe
        for log in all_logs:
            if log.success:
                if log.recipe_id in recipe_counts:
                    recipe_counts[log.recipe_id] += log.quantity_produced
                else:
                    recipe_counts[log.recipe_id] = log.quantity_produced
        
        # Sort by count (highest first)
        sorted_recipes = sorted(recipe_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Get recipe details for top recipes
        result = []
        for recipe_id, count in sorted_recipes[:limit]:
            recipe = recipe_service.get_recipe(db=db, recipe_id=recipe_id)
            if recipe:
                result.append({
                    "id": recipe_id,
                    "name": recipe.name,
                    "times_crafted": count,
                    "category": recipe.recipe_category,
                    "difficulty_level": recipe.difficulty_level
                })
        
        return result

    # Helper methods
    def _calculate_crafting_success_chance(
        self,
        recipe: Recipe,
        skills_data: Optional[Dict[str, Any]] = None,
        custom_quality_modifier: Optional[float] = None
    ) -> Tuple[float, int]:
        """
        Calculate the chance of successful crafting and base quality.
        
        Args:
            recipe: Recipe to craft
            skills_data: Player's skills data
            custom_quality_modifier: Optional quality modifier
            
        Returns:
            Tuple of (success_chance, base_quality)
        """
        # Base success chance depends on recipe difficulty
        base_success_chance = 1.0 - ((recipe.difficulty_level - 1) * 0.1)
        
        # Base quality starts at 1
        base_quality = 1
        
        # Apply skill modifiers if skills_data is provided
        if skills_data and recipe.required_skills:
            for skill_req in recipe.required_skills:
                player_skill_level = skills_data.get(skill_req.skill_name, 0)
                skill_level_difference = player_skill_level - skill_req.level
                
                # Increase success chance based on skill level above requirement
                if skill_level_difference > 0:
                    base_success_chance += skill_level_difference * 0.05
                elif skill_level_difference < 0:
                    # This case should not happen if can_character_craft_recipe was called
                    base_success_chance += skill_level_difference * 0.1
                
                # Increase quality based on skill level
                if skill_req.affects_quality:
                    quality_bonus = skill_level_difference * 0.2
                    base_quality += quality_bonus
        
        # Apply custom quality modifier if provided
        if custom_quality_modifier:
            base_quality += custom_quality_modifier
        
        # Apply recipe mastery bonus (placeholder - would be implemented with actual player data)
        # mastery_level = self._get_player_recipe_mastery(player_id, recipe_id)
        # base_success_chance += mastery_level * 0.02
        # base_quality += mastery_level * 0.1
        
        # Ensure success chance is within [0.1, 0.99] range
        success_chance = min(0.99, max(0.1, base_success_chance))
        
        # Ensure base quality is at least 1
        base_quality = max(1, base_quality)
        
        return success_chance, int(base_quality)

    def _calculate_crafting_time(
        self,
        recipe: Recipe,
        skills_data: Optional[Dict[str, Any]] = None,
        quantity: int = 1
    ) -> int:
        """
        Calculate the time required for crafting.
        
        Args:
            recipe: Recipe to craft
            skills_data: Player's skills data
            quantity: Quantity to craft
            
        Returns:
            Crafting time in seconds
        """
        # Base time from recipe
        base_time = recipe.crafting_time_seconds
        
        # Apply skill modifiers if skills_data is provided
        if skills_data and recipe.required_skills:
            time_modifier = 1.0
            for skill_req in recipe.required_skills:
                player_skill_level = skills_data.get(skill_req.skill_name, 0)
                skill_level_difference = player_skill_level - skill_req.level
                
                if skill_req.affects_speed and skill_level_difference > 0:
                    # Reduce crafting time by 2% per skill level above requirement
                    time_modifier -= skill_level_difference * 0.02
            
            # Ensure time modifier is within [0.5, 1.0] range
            time_modifier = min(1.0, max(0.5, time_modifier))
            base_time *= time_modifier
        
        # Scale by quantity (with diminishing returns for efficiency)
        if quantity > 1:
            # Each additional item takes 80% of the time of the first
            total_time = base_time * (1 + 0.8 * (quantity - 1))
        else:
            total_time = base_time
        
        return int(total_time)

    def _calculate_discovery_score(
        self,
        recipe: Recipe,
        provided_ingredients: Dict[str, int],
        skills_data: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        available_stations: Optional[List[str]] = None,
        location_data: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate how well the provided ingredients match a recipe for discovery.
        
        Args:
            recipe: Recipe to check
            provided_ingredients: Ingredients provided by the player
            skills_data: Player's skills data
            available_tools: Available tools
            available_stations: Available crafting stations
            location_data: Current location data
            
        Returns:
            Score from 0.0 to 1.0 indicating match quality
        """
        # Initialize score components
        ingredient_match_score = 0.0
        tool_match_score = 0.0
        station_match_score = 0.0
        skill_match_score = 0.0
        
        # Check ingredient match
        required_ingredients = {ing.item_id: ing.quantity for ing in recipe.ingredients}
        total_required_ingredients = len(required_ingredients)
        
        if total_required_ingredients == 0:
            return 0.0  # Can't discover a recipe with no ingredients
        
        matching_ingredients = 0
        quantity_match_score = 0.0
        
        for item_id, required_qty in required_ingredients.items():
            provided_qty = provided_ingredients.get(item_id, 0)
            if provided_qty > 0:
                matching_ingredients += 1
                
                # Calculate quantity match (1.0 if exact, less if too few or too many)
                if provided_qty >= required_qty:
                    qty_ratio = min(provided_qty / required_qty, 2.0)  # Cap at 2x
                    qty_match = 1.0 - (qty_ratio - 1.0) / 2.0  # Penalize excess, but less than shortage
                else:
                    qty_match = provided_qty / required_qty
                
                quantity_match_score += qty_match
        
        # Check for extraneous ingredients (penalties)
        extra_ingredients = 0
        for item_id in provided_ingredients:
            if item_id not in required_ingredients:
                extra_ingredients += 1
        
        # Calculate final ingredient match score
        if total_required_ingredients > 0:
            ingredient_match_score = (matching_ingredients / total_required_ingredients) * 0.7
            if matching_ingredients > 0:
                quantity_match_score = (quantity_match_score / matching_ingredients) * 0.3
            
            # Penalty for extraneous ingredients
            extra_penalty = min(0.5, extra_ingredients * 0.1)
            ingredient_match_score = max(0, ingredient_match_score - extra_penalty)
        
        # Check tool match if available_tools is provided
        if available_tools and recipe.required_tools:
            matching_tools = len(set(recipe.required_tools).intersection(set(available_tools)))
            total_required_tools = len(recipe.required_tools)
            if total_required_tools > 0:
                tool_match_score = matching_tools / total_required_tools
        elif not recipe.required_tools:
            tool_match_score = 1.0  # No tools required
        
        # Check station match if available_stations is provided
        if available_stations and recipe.required_station_type:
            if recipe.required_station_type in available_stations:
                station_match_score = 1.0
        elif not recipe.required_station_type:
            station_match_score = 1.0  # No station required
        
        # Check skill match if skills_data is provided
        if skills_data and recipe.required_skills:
            matching_skills = 0
            total_required_skills = len(recipe.required_skills)
            
            for skill_req in recipe.required_skills:
                player_skill_level = skills_data.get(skill_req.skill_name, 0)
                if player_skill_level >= skill_req.level:
                    matching_skills += 1
            
            if total_required_skills > 0:
                skill_match_score = matching_skills / total_required_skills
        elif not recipe.required_skills:
            skill_match_score = 1.0  # No skills required
        
        # Final score calculation (weighted components)
        final_score = (
            ingredient_match_score * 0.6 +
            quantity_match_score * 0.1 +
            tool_match_score * 0.1 +
            station_match_score * 0.1 +
            skill_match_score * 0.1
        )
        
        return final_score

    def _update_recipe_mastery(
        self,
        db: Session,
        player_id: str,
        recipe_id: str,
        quality_achieved: int
    ) -> None:
        """
        Update a player's mastery of a recipe based on successful crafting.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            quality_achieved: Quality achieved in crafting
        """
        # Increment times crafted counter
        crud_player_known_recipe.increment_times_crafted(
            db=db, player_id=player_id, recipe_id=recipe_id, quality=quality_achieved
        )
        
        # Get current record
        known_recipe = db.query(crud_player_known_recipe.model).filter(
            crud_player_known_recipe.model.player_id == player_id,
            crud_player_known_recipe.model.recipe_id == recipe_id
        ).first()
        
        if known_recipe:
            # Check if mastery should increase (based on times crafted and current mastery)
            # This is a simple algorithm - it could be more complex in a real system
            times_crafted = known_recipe.times_crafted
            current_mastery = known_recipe.mastery_level
            
            # Mastery levels: 0 (novice) to 5 (master)
            mastery_thresholds = [0, 5, 15, 30, 50, 75]  # Crafts needed for each level
            
            for level, threshold in enumerate(mastery_thresholds):
                if times_crafted >= threshold and current_mastery < level:
                    # Update mastery level
                    known_recipe.mastery_level = level
                    db.add(known_recipe)
                    db.commit()
                    break

# Create a singleton instance
crafting_service = CraftingService()