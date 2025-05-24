"""
Crafting Service Module

This module handles crafting mechanics for players and NPCs, including
recipe management, skill-based crafting, resource consumption, and
quality variation in crafted items.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import random
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session
import uuid

# Import models
from backend.src.economy.models.pydantic_models import (
    Item, Shop, InventorySlot, ItemCategory, ItemRarity, MarketRegionInfo
)
from backend.src.economy.models.db_models import (
    DBItem, DBShop, DBLocation, DBMarketRegionInfo, DBCharacter, DBResource
)

# Import Celery integration for async processing
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class CraftingService:
    """
    Service for handling crafting mechanics in the game world.
    """
    
    def __init__(self):
        """Initialize the crafting service."""
        self.logger = logging.getLogger("CraftingService")
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration for async operations
        self.celery_integration = NarrativeEngineCeleryIntegration()
        
        # Subscribe to relevant events
        self.event_bus.subscribe("crafting_started", self._handle_crafting_started)
        self.event_bus.subscribe("crafting_completed", self._handle_crafting_completed)
        self.event_bus.subscribe("crafting_failed", self._handle_crafting_failed)
        self.event_bus.subscribe("recipe_discovered", self._handle_recipe_discovered)
    
    async def craft_item(self,
                      db: Session,
                      crafter_id: str,
                      recipe_id: str,
                      quantity: int = 1,
                      use_quality_materials: bool = False,
                      async_processing: bool = True) -> Dict[str, Any]:
        """
        Craft an item using a recipe.
        
        Args:
            db: Database session
            crafter_id: Character crafting the item
            recipe_id: Recipe identifier
            quantity: Number of items to craft
            use_quality_materials: Whether to use higher quality materials
            async_processing: Whether to process asynchronously
            
        Returns:
            Crafting result
        """
        # Check if crafter exists
        crafter = db.query(DBCharacter).filter(DBCharacter.id == crafter_id).first()
        if not crafter:
            return {"error": f"Character {crafter_id} not found"}
        
        # Get the recipe
        recipe = self._get_recipe(db, recipe_id)
        if not recipe:
            return {"error": f"Recipe {recipe_id} not found"}
        
        # Check if character has the recipe
        if not self._character_has_recipe(db, crafter_id, recipe_id):
            return {"error": f"Character {crafter_id} does not know recipe {recipe_id}"}
        
        # Check if character has the required materials
        materials_check = self._check_crafting_materials(db, crafter_id, recipe, quantity)
        if "error" in materials_check:
            return materials_check
        
        # Check if character has the required skill level
        skill_check = self._check_crafting_skill(db, crafter_id, recipe)
        if "error" in skill_check:
            return skill_check
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.craft_item_task",
                task_args=[crafter_id, recipe_id],
                task_kwargs={
                    "quantity": quantity,
                    "use_quality_materials": use_quality_materials
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "craft_item",
                "crafter_id": crafter_id,
                "recipe_id": recipe_id,
                "status": "processing",
                "message": f"Crafting of {recipe['item_name']} ({quantity}) dispatched for asynchronous processing"
            }
        
        # For synchronous processing, craft the item here
        # This is a simplified implementation
        
        # Consume materials
        self._consume_crafting_materials(db, crafter_id, recipe, quantity, use_quality_materials)
        
        # Calculate crafting success chance and quality
        skill_level = self._get_character_crafting_skill(db, crafter_id, recipe["skill_type"])
        base_success_chance = recipe["base_success_chance"]
        skill_bonus = min(0.5, skill_level / 100)  # Max 50% bonus from skill
        quality_material_bonus = 0.1 if use_quality_materials else 0.0
        
        success_chance = min(0.98, base_success_chance + skill_bonus + quality_material_bonus)
        
        # Roll for success
        success = random.random() <= success_chance
        
        if success:
            # Calculate quality
            base_quality = recipe["base_quality"]
            quality_bonus = skill_level / 200  # Max 50% bonus from skill
            material_quality_bonus = 0.2 if use_quality_materials else 0.0
            
            quality = min(1.0, base_quality + quality_bonus + material_quality_bonus)
            
            # Determine item rarity based on quality
            rarity = self._determine_rarity_from_quality(quality)
            
            # Create the crafted item
            result = self._create_crafted_item(
                db, 
                crafter_id, 
                recipe,
                quantity,
                quality,
                rarity,
                use_quality_materials
            )
            
            # Update crafting skill
            self._update_crafting_skill(db, crafter_id, recipe["skill_type"], success=True)
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="crafting_completed",
                data={
                    "crafter_id": crafter_id,
                    "crafter_name": crafter.name,
                    "recipe_id": recipe_id,
                    "item_id": recipe["item_id"],
                    "item_name": recipe["item_name"],
                    "quantity": quantity,
                    "quality": quality,
                    "rarity": rarity,
                    "used_quality_materials": use_quality_materials,
                    "skill_gained": 1 + (0.5 if recipe["difficulty"] > 0.7 else 0),
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="crafting_service"
            ))
            
            return {
                "action": "craft_item",
                "status": "success",
                "crafter_id": crafter_id,
                "crafter_name": crafter.name,
                "recipe_id": recipe_id,
                "item_id": recipe["item_id"],
                "item_name": recipe["item_name"],
                "quantity": quantity,
                "quality": round(quality * 100),
                "rarity": rarity,
                "success_chance": round(success_chance * 100),
                "used_quality_materials": use_quality_materials,
                "skill_gained": 1 + (0.5 if recipe["difficulty"] > 0.7 else 0),
                "added_to_inventory": result["added_to_inventory"]
            }
        else:
            # Crafting failed, some materials lost
            lost_materials = {}
            for material_id, amount in recipe["materials"].items():
                # 50-75% of materials are lost on failure
                lost_percent = random.uniform(0.5, 0.75)
                lost_amount = int(amount * quantity * lost_percent)
                if lost_amount > 0:
                    item = db.query(DBItem).filter(DBItem.id == material_id).first()
                    lost_materials[material_id] = {
                        "name": item.name if item else material_id,
                        "amount": lost_amount
                    }
            
            # Update crafting skill (less skill gain on failure)
            self._update_crafting_skill(db, crafter_id, recipe["skill_type"], success=False)
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="crafting_failed",
                data={
                    "crafter_id": crafter_id,
                    "crafter_name": crafter.name,
                    "recipe_id": recipe_id,
                    "item_name": recipe["item_name"],
                    "quantity": quantity,
                    "success_chance": success_chance,
                    "lost_materials": lost_materials,
                    "skill_gained": 0.5,  # Less skill gain on failure
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="crafting_service"
            ))
            
            return {
                "action": "craft_item",
                "status": "failure",
                "crafter_id": crafter_id,
                "crafter_name": crafter.name,
                "recipe_id": recipe_id,
                "item_name": recipe["item_name"],
                "quantity": quantity,
                "success_chance": round(success_chance * 100),
                "used_quality_materials": use_quality_materials,
                "lost_materials": lost_materials,
                "skill_gained": 0.5,
                "message": f"Failed to craft {recipe['item_name']}. Some materials were lost."
            }
    
    async def discover_recipe(self,
                           db: Session,
                           character_id: str,
                           recipe_id: Optional[str] = None,
                           recipe_difficulty: Optional[float] = None,
                           async_processing: bool = True) -> Dict[str, Any]:
        """
        Discover a new crafting recipe.
        
        Args:
            db: Database session
            character_id: Character discovering the recipe
            recipe_id: Optional specific recipe to discover
            recipe_difficulty: Optional difficulty filter for random recipe
            async_processing: Whether to process asynchronously
            
        Returns:
            Recipe discovery result
        """
        # Check if character exists
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {"error": f"Character {character_id} not found"}
        
        # If no recipe specified, pick a random one
        if not recipe_id:
            recipe = self._get_random_recipe(db, character_id, recipe_difficulty)
            if not recipe:
                return {"error": "No suitable recipes found to discover"}
            recipe_id = recipe["id"]
        else:
            recipe = self._get_recipe(db, recipe_id)
            if not recipe:
                return {"error": f"Recipe {recipe_id} not found"}
        
        # Check if character already knows this recipe
        if self._character_has_recipe(db, character_id, recipe_id):
            return {"error": f"Character {character_id} already knows recipe {recipe_id}"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.discover_recipe_task",
                task_args=[character_id, recipe_id],
                task_kwargs={}
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "discover_recipe",
                "character_id": character_id,
                "recipe_id": recipe_id,
                "status": "processing",
                "message": f"Recipe discovery for {recipe['item_name']} dispatched for asynchronous processing"
            }
        
        # For synchronous processing, discover the recipe here
        # This is a simplified implementation
        
        # Add recipe to character's known recipes
        custom_data = character.custom_data or {}
        known_recipes = custom_data.get("known_recipes", [])
        
        # Check again if character already knows this recipe
        if recipe_id in known_recipes:
            return {"error": f"Character {character_id} already knows recipe {recipe_id}"}
        
        # Add the recipe
        known_recipes.append(recipe_id)
        custom_data["known_recipes"] = known_recipes
        character.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="recipe_discovered",
            data={
                "character_id": character_id,
                "character_name": character.name,
                "recipe_id": recipe_id,
                "recipe_name": recipe["name"],
                "item_name": recipe["item_name"],
                "item_id": recipe["item_id"],
                "skill_type": recipe["skill_type"],
                "difficulty": recipe["difficulty"],
                "timestamp": datetime.utcnow().isoformat()
            },
            source="crafting_service"
        ))
        
        return {
            "action": "discover_recipe",
            "status": "success",
            "character_id": character_id,
            "character_name": character.name,
            "recipe_id": recipe_id,
            "recipe_name": recipe["name"],
            "item_name": recipe["item_name"],
            "item_id": recipe["item_id"],
            "skill_type": recipe["skill_type"],
            "difficulty": recipe["difficulty"],
            "materials": {
                mat_id: {
                    "name": self._get_item_name(db, mat_id),
                    "amount": amount
                } for mat_id, amount in recipe["materials"].items()
            },
            "known_recipes_count": len(known_recipes)
        }
    
    async def create_recipe(self,
                         db: Session,
                         character_id: str,
                         item_id: str,
                         materials: Dict[str, int],
                         skill_type: str,
                         difficulty: float,
                         base_success_chance: float,
                         base_quality: float,
                         async_processing: bool = True) -> Dict[str, Any]:
        """
        Create a new crafting recipe.
        
        Args:
            db: Database session
            character_id: Character creating the recipe
            item_id: Item to be crafted
            materials: Dictionary mapping material item IDs to amounts
            skill_type: Type of crafting skill required
            difficulty: Recipe difficulty (0.0 to 1.0)
            base_success_chance: Base chance of success (0.0 to 1.0)
            base_quality: Base quality of crafted item (0.0 to 1.0)
            async_processing: Whether to process asynchronously
            
        Returns:
            Recipe creation result
        """
        # Check if character exists
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {"error": f"Character {character_id} not found"}
        
        # Check if item exists
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        if not item:
            return {"error": f"Item {item_id} not found"}
        
        # Check if materials exist
        for material_id in materials.keys():
            material = db.query(DBItem).filter(DBItem.id == material_id).first()
            if not material:
                return {"error": f"Material {material_id} not found"}
        
        # Validate skill type
        valid_skill_types = [
            "blacksmithing", "alchemy", "tailoring", "cooking", 
            "carpentry", "jewelcrafting", "leatherworking", "engineering"
        ]
        if skill_type not in valid_skill_types:
            return {"error": f"Invalid skill type: {skill_type}. Valid types: {', '.join(valid_skill_types)}"}
        
        # Validate numeric parameters
        if not (0.0 <= difficulty <= 1.0):
            return {"error": f"Difficulty must be between 0.0 and 1.0, got {difficulty}"}
        if not (0.0 <= base_success_chance <= 1.0):
            return {"error": f"Base success chance must be between 0.0 and 1.0, got {base_success_chance}"}
        if not (0.0 <= base_quality <= 1.0):
            return {"error": f"Base quality must be between 0.0 and 1.0, got {base_quality}"}
        
        # Generate recipe ID
        recipe_id = f"recipe-{item_id}-{uuid.uuid4().hex[:8]}"
        
        # Create recipe data
        recipe_data = {
            "id": recipe_id,
            "name": f"Recipe: {item.name}",
            "item_id": item_id,
            "item_name": item.name,
            "materials": materials,
            "skill_type": skill_type,
            "difficulty": difficulty,
            "base_success_chance": base_success_chance,
            "base_quality": base_quality,
            "creator_id": character_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.create_recipe_task",
                task_args=[character_id, recipe_data],
                task_kwargs={}
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "create_recipe",
                "character_id": character_id,
                "recipe_id": recipe_id,
                "status": "processing",
                "message": f"Recipe creation for {item.name} dispatched for asynchronous processing"
            }
        
        # For synchronous processing, create the recipe here
        # This is a simplified implementation
        
        # Store recipe in global recipes
        custom_data = {}
        # In a real implementation, this would be stored in a database table
        # For now, we'll use a system character to store global recipes
        system_character = db.query(DBCharacter).filter(DBCharacter.id == "system").first()
        if not system_character:
            # Create system character if it doesn't exist
            system_character = DBCharacter(
                id="system",
                name="System",
                character_type="system",
                custom_data={"global_recipes": {}}
            )
            db.add(system_character)
        
        system_custom_data = system_character.custom_data or {}
        global_recipes = system_custom_data.get("global_recipes", {})
        global_recipes[recipe_id] = recipe_data
        system_custom_data["global_recipes"] = global_recipes
        system_character.custom_data = system_custom_data
        
        # Add recipe to character's known recipes
        character_custom_data = character.custom_data or {}
        known_recipes = character_custom_data.get("known_recipes", [])
        if recipe_id not in known_recipes:
            known_recipes.append(recipe_id)
            character_custom_data["known_recipes"] = known_recipes
            character.custom_data = character_custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="recipe_created",
            data={
                "recipe_id": recipe_id,
                "recipe_name": recipe_data["name"],
                "item_id": item_id,
                "item_name": item.name,
                "creator_id": character_id,
                "creator_name": character.name,
                "skill_type": skill_type,
                "difficulty": difficulty,
                "materials_count": len(materials),
                "timestamp": datetime.utcnow().isoformat()
            },
            source="crafting_service"
        ))
        
        return {
            "action": "create_recipe",
            "status": "success",
            "recipe_id": recipe_id,
            "recipe_name": recipe_data["name"],
            "item_id": item_id,
            "item_name": item.name,
            "creator_id": character_id,
            "creator_name": character.name,
            "skill_type": skill_type,
            "difficulty": difficulty,
            "base_success_chance": base_success_chance,
            "base_quality": base_quality,
            "materials": {
                mat_id: {
                    "name": self._get_item_name(db, mat_id),
                    "amount": amount
                } for mat_id, amount in materials.items()
            }
        }
    
    async def improve_crafting_skill(self,
                                  db: Session,
                                  character_id: str,
                                  skill_type: str,
                                  training_intensity: float = 0.5,
                                  duration_hours: int = 4,
                                  async_processing: bool = True) -> Dict[str, Any]:
        """
        Improve a character's crafting skill through training.
        
        Args:
            db: Database session
            character_id: Character to train
            skill_type: Type of crafting skill to improve
            training_intensity: Intensity of training (0.0 to 1.0)
            duration_hours: Hours spent training
            async_processing: Whether to process asynchronously
            
        Returns:
            Skill improvement result
        """
        # Check if character exists
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {"error": f"Character {character_id} not found"}
        
        # Validate skill type
        valid_skill_types = [
            "blacksmithing", "alchemy", "tailoring", "cooking", 
            "carpentry", "jewelcrafting", "leatherworking", "engineering"
        ]
        if skill_type not in valid_skill_types:
            return {"error": f"Invalid skill type: {skill_type}. Valid types: {', '.join(valid_skill_types)}"}
        
        # Validate numeric parameters
        if not (0.0 <= training_intensity <= 1.0):
            return {"error": f"Training intensity must be between 0.0 and 1.0, got {training_intensity}"}
        if duration_hours <= 0:
            return {"error": f"Duration hours must be positive, got {duration_hours}"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.improve_crafting_skill_task",
                task_args=[character_id, skill_type],
                task_kwargs={
                    "training_intensity": training_intensity,
                    "duration_hours": duration_hours
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "improve_crafting_skill",
                "character_id": character_id,
                "skill_type": skill_type,
                "status": "processing",
                "message": f"Crafting skill improvement for {skill_type} dispatched for asynchronous processing"
            }
        
        # For synchronous processing, improve the skill here
        # This is a simplified implementation
        
        # Get current skill level
        current_skill = self._get_character_crafting_skill(db, character_id, skill_type)
        
        # Calculate skill gain based on training parameters
        # Formula: base_gain * intensity * duration * diminishing_returns
        base_gain = 1.0
        diminishing_returns = max(0.1, 1.0 - (current_skill / 200))  # Higher skill = less gain
        skill_gain = base_gain * training_intensity * (duration_hours / 4) * diminishing_returns
        
        # Apply a random factor (80% to 120% of calculated gain)
        skill_gain *= random.uniform(0.8, 1.2)
        
        # Round to one decimal place
        skill_gain = round(skill_gain, 1)
        
        # Update character's skill
        custom_data = character.custom_data or {}
        crafting_skills = custom_data.get("crafting_skills", {})
        new_skill_level = crafting_skills.get(skill_type, 0) + skill_gain
        crafting_skills[skill_type] = new_skill_level
        custom_data["crafting_skills"] = crafting_skills
        character.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="crafting_skill_improved",
            data={
                "character_id": character_id,
                "character_name": character.name,
                "skill_type": skill_type,
                "previous_level": current_skill,
                "new_level": new_skill_level,
                "skill_gain": skill_gain,
                "training_intensity": training_intensity,
                "duration_hours": duration_hours,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="crafting_service"
        ))
        
        return {
            "action": "improve_crafting_skill",
            "status": "success",
            "character_id": character_id,
            "character_name": character.name,
            "skill_type": skill_type,
            "previous_level": current_skill,
            "new_level": new_skill_level,
            "skill_gain": skill_gain,
            "training_intensity": training_intensity,
            "duration_hours": duration_hours
        }
    
    def get_character_known_recipes(self, db: Session, character_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of recipes known by a character.
        
        Args:
            db: Database session
            character_id: Character identifier
            
        Returns:
            List of recipe data
        """
        # Check if character exists
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return []
        
        # Get known recipe IDs
        custom_data = character.custom_data or {}
        known_recipe_ids = custom_data.get("known_recipes", [])
        
        # Get recipe details
        known_recipes = []
        for recipe_id in known_recipe_ids:
            recipe = self._get_recipe(db, recipe_id)
            if recipe:
                known_recipes.append({
                    "id": recipe["id"],
                    "name": recipe["name"],
                    "item_id": recipe["item_id"],
                    "item_name": recipe["item_name"],
                    "skill_type": recipe["skill_type"],
                    "difficulty": recipe["difficulty"],
                    "materials": {
                        mat_id: {
                            "name": self._get_item_name(db, mat_id),
                            "amount": amount
                        } for mat_id, amount in recipe["materials"].items()
                    },
                    "base_success_chance": recipe["base_success_chance"],
                    "base_quality": recipe["base_quality"]
                })
        
        return known_recipes
    
    def get_character_crafting_skills(self, db: Session, character_id: str) -> Dict[str, float]:
        """
        Get a character's crafting skill levels.
        
        Args:
            db: Database session
            character_id: Character identifier
            
        Returns:
            Dictionary mapping skill types to levels
        """
        # Check if character exists
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {}
        
        # Get crafting skills
        custom_data = character.custom_data or {}
        crafting_skills = custom_data.get("crafting_skills", {})
        
        return crafting_skills
    
    def _get_recipe(self, db: Session, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a recipe by ID.
        
        Args:
            db: Database session
            recipe_id: Recipe identifier
            
        Returns:
            Recipe data or None if not found
        """
        # In a real implementation, this would query a recipe table
        # For now, we'll use a system character to store global recipes
        system_character = db.query(DBCharacter).filter(DBCharacter.id == "system").first()
        if not system_character:
            return None
        
        custom_data = system_character.custom_data or {}
        global_recipes = custom_data.get("global_recipes", {})
        
        return global_recipes.get(recipe_id)
    
    def _get_random_recipe(self, 
                         db: Session, 
                         character_id: str, 
                         difficulty: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get a random recipe that the character doesn't know yet.
        
        Args:
            db: Database session
            character_id: Character identifier
            difficulty: Optional difficulty filter
            
        Returns:
            Random recipe or None if none available
        """
        # Get character's known recipes
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return None
        
        custom_data = character.custom_data or {}
        known_recipe_ids = custom_data.get("known_recipes", [])
        
        # Get all recipes
        system_character = db.query(DBCharacter).filter(DBCharacter.id == "system").first()
        if not system_character:
            return None
        
        system_custom_data = system_character.custom_data or {}
        global_recipes = system_custom_data.get("global_recipes", {})
        
        # Filter recipes the character doesn't know yet
        unknown_recipes = [
            recipe for recipe_id, recipe in global_recipes.items()
            if recipe_id not in known_recipe_ids
        ]
        
        # Apply difficulty filter if specified
        if difficulty is not None:
            unknown_recipes = [
                recipe for recipe in unknown_recipes
                if abs(recipe["difficulty"] - difficulty) <= 0.2  # Within 0.2 of target difficulty
            ]
        
        # Return a random recipe, or None if none available
        if unknown_recipes:
            return random.choice(unknown_recipes)
        else:
            return None
    
    def _character_has_recipe(self, db: Session, character_id: str, recipe_id: str) -> bool:
        """
        Check if a character knows a recipe.
        
        Args:
            db: Database session
            character_id: Character identifier
            recipe_id: Recipe identifier
            
        Returns:
            True if the character knows the recipe, False otherwise
        """
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return False
        
        custom_data = character.custom_data or {}
        known_recipes = custom_data.get("known_recipes", [])
        
        return recipe_id in known_recipes
    
    def _check_crafting_materials(self, 
                               db: Session, 
                               character_id: str, 
                               recipe: Dict[str, Any],
                               quantity: int) -> Dict[str, Any]:
        """
        Check if a character has the materials needed for a recipe.
        
        Args:
            db: Database session
            character_id: Character identifier
            recipe: Recipe data
            quantity: Number of items to craft
            
        Returns:
            Success dict or error dict
        """
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {"error": f"Character {character_id} not found"}
        
        inventory = character.inventory or {}
        
        # Check each required material
        missing_materials = {}
        for material_id, amount_needed in recipe["materials"].items():
            total_needed = amount_needed * quantity
            
            if material_id not in inventory:
                item = db.query(DBItem).filter(DBItem.id == material_id).first()
                item_name = item.name if item else material_id
                missing_materials[material_id] = {
                    "name": item_name,
                    "needed": total_needed,
                    "have": 0
                }
                continue
            
            slot_data = inventory[material_id]
            have_amount = slot_data.get("quantity", 0)
            
            if have_amount < total_needed:
                item = db.query(DBItem).filter(DBItem.id == material_id).first()
                item_name = item.name if item else material_id
                missing_materials[material_id] = {
                    "name": item_name,
                    "needed": total_needed,
                    "have": have_amount
                }
        
        if missing_materials:
            return {
                "error": f"Missing materials for crafting {recipe['item_name']}",
                "missing_materials": missing_materials
            }
        
        return {"success": True}
    
    def _check_crafting_skill(self, 
                           db: Session, 
                           character_id: str, 
                           recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a character has sufficient skill for a recipe.
        
        Args:
            db: Database session
            character_id: Character identifier
            recipe: Recipe data
            
        Returns:
            Success dict or error dict
        """
        skill_type = recipe["skill_type"]
        difficulty = recipe["difficulty"]
        
        # Get character's skill level
        skill_level = self._get_character_crafting_skill(db, character_id, skill_type)
        
        # Calculate minimum skill needed (difficulty * 100)
        min_skill = difficulty * 50  # Easier threshold, 50% of difficulty scale
        
        if skill_level < min_skill:
            return {
                "error": f"Insufficient {skill_type} skill ({skill_level}) for crafting {recipe['item_name']}. Needs at least {min_skill}."
            }
        
        return {"success": True}
    
    def _get_character_crafting_skill(self, 
                                   db: Session, 
                                   character_id: str, 
                                   skill_type: str) -> float:
        """
        Get a character's level in a specific crafting skill.
        
        Args:
            db: Database session
            character_id: Character identifier
            skill_type: Type of crafting skill
            
        Returns:
            Skill level
        """
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return 0.0
        
        custom_data = character.custom_data or {}
        crafting_skills = custom_data.get("crafting_skills", {})
        
        return crafting_skills.get(skill_type, 0.0)
    
    def _consume_crafting_materials(self, 
                                 db: Session, 
                                 character_id: str, 
                                 recipe: Dict[str, Any],
                                 quantity: int,
                                 use_quality_materials: bool) -> None:
        """
        Consume materials for crafting.
        
        Args:
            db: Database session
            character_id: Character identifier
            recipe: Recipe data
            quantity: Number of items to craft
            use_quality_materials: Whether to use higher quality materials
        """
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return
        
        inventory = character.inventory or {}
        
        # Consume each required material
        for material_id, amount_needed in recipe["materials"].items():
            total_needed = amount_needed * quantity
            
            if material_id in inventory:
                slot_data = inventory[material_id]
                have_amount = slot_data.get("quantity", 0)
                
                # Consume materials
                new_amount = have_amount - total_needed
                
                if new_amount <= 0:
                    # Remove material from inventory
                    inventory.pop(material_id)
                else:
                    # Update quantity
                    slot_data["quantity"] = new_amount
                    inventory[material_id] = slot_data
        
        # Update character inventory
        character.inventory = inventory
        
        # Commit changes
        db.commit()
    
    def _update_crafting_skill(self, 
                            db: Session, 
                            character_id: str, 
                            skill_type: str,
                            success: bool) -> None:
        """
        Update a character's crafting skill after an attempt.
        
        Args:
            db: Database session
            character_id: Character identifier
            skill_type: Type of crafting skill
            success: Whether the crafting attempt was successful
        """
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return
        
        # Get current skill level
        custom_data = character.custom_data or {}
        crafting_skills = custom_data.get("crafting_skills", {})
        current_skill = crafting_skills.get(skill_type, 0.0)
        
        # Calculate skill gain
        if success:
            # More skill gain on success
            skill_gain = 1.0
            # Less gain at higher levels
            if current_skill > 50:
                skill_gain *= 0.8
            if current_skill > 75:
                skill_gain *= 0.6
            if current_skill > 90:
                skill_gain *= 0.4
        else:
            # Less skill gain on failure
            skill_gain = 0.5
            # Even less gain at higher levels
            if current_skill > 50:
                skill_gain *= 0.7
            if current_skill > 75:
                skill_gain *= 0.5
            if current_skill > 90:
                skill_gain *= 0.3
        
        # Apply the skill gain
        new_skill = current_skill + skill_gain
        crafting_skills[skill_type] = new_skill
        custom_data["crafting_skills"] = crafting_skills
        character.custom_data = custom_data
        
        # Commit changes
        db.commit()
    
    def _determine_rarity_from_quality(self, quality: float) -> str:
        """
        Determine item rarity based on quality.
        
        Args:
            quality: Item quality (0.0 to 1.0)
            
        Returns:
            Item rarity
        """
        if quality >= 0.95:
            return "legendary"
        elif quality >= 0.85:
            return "epic"
        elif quality >= 0.7:
            return "rare"
        elif quality >= 0.5:
            return "uncommon"
        else:
            return "common"
    
    def _create_crafted_item(self,
                          db: Session,
                          crafter_id: str,
                          recipe: Dict[str, Any],
                          quantity: int,
                          quality: float,
                          rarity: str,
                          used_quality_materials: bool) -> Dict[str, Any]:
        """
        Create a crafted item and add it to the crafter's inventory.
        
        Args:
            db: Database session
            crafter_id: Crafter identifier
            recipe: Recipe data
            quantity: Number of items crafted
            quality: Quality of the crafted item
            rarity: Rarity of the crafted item
            used_quality_materials: Whether quality materials were used
            
        Returns:
            Crafting result
        """
        character = db.query(DBCharacter).filter(DBCharacter.id == crafter_id).first()
        if not character:
            return {"error": "Character not found"}
        
        # Get base item
        item_id = recipe["item_id"]
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        if not item:
            return {"error": f"Item {item_id} not found"}
        
        # Add to character's inventory
        inventory = character.inventory or {}
        
        if item_id in inventory:
            # Update existing inventory slot
            slot_data = inventory[item_id]
            have_amount = slot_data.get("quantity", 0)
            new_amount = have_amount + quantity
            
            # Update quantity
            slot_data["quantity"] = new_amount
            
            # Update quality if crafted item is better
            current_quality = slot_data.get("quality", 0.0)
            if quality > current_quality:
                slot_data["quality"] = quality
                slot_data["rarity"] = rarity
            
            inventory[item_id] = slot_data
        else:
            # Create new inventory slot
            slot_data = {
                "quantity": quantity,
                "condition": 1.0,  # New items are in perfect condition
                "quality": quality,
                "rarity": rarity,
                "crafted_by": crafter_id,
                "crafted_at": datetime.utcnow().isoformat(),
                "used_quality_materials": used_quality_materials
            }
            
            inventory[item_id] = slot_data
        
        # Update character inventory
        character.inventory = inventory
        
        # Commit changes
        db.commit()
        
        return {
            "added_to_inventory": True,
            "item_id": item_id,
            "item_name": item.name,
            "quantity": quantity,
            "quality": quality,
            "rarity": rarity
        }
    
    def _get_item_name(self, db: Session, item_id: str) -> str:
        """
        Get an item's name by ID.
        
        Args:
            db: Database session
            item_id: Item identifier
            
        Returns:
            Item name or item ID if not found
        """
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        return item.name if item else item_id
    
    def _handle_crafting_started(self, event: Event) -> None:
        """
        Handle a crafting started event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling crafting started: {event.data}")
        
        # In a real implementation, this might trigger NPCs to react,
        # update crafting station status, etc.
    
    def _handle_crafting_completed(self, event: Event) -> None:
        """
        Handle a crafting completed event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling crafting completed: {event.data}")
        
        # In a real implementation, this might update market supplies,
        # trigger achievements, etc.
    
    def _handle_crafting_failed(self, event: Event) -> None:
        """
        Handle a crafting failed event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling crafting failed: {event.data}")
        
        # In a real implementation, this might trigger reactions from NPCs,
        # damage crafting stations, etc.
    
    def _handle_recipe_discovered(self, event: Event) -> None:
        """
        Handle a recipe discovered event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling recipe discovered: {event.data}")
        
        # In a real implementation, this might update quest progress,
        # trigger achievements, etc.