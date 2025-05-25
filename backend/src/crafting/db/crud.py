"""
Crafting System CRUD Operations

This module provides CRUD operations for the material and recipe system.
"""

import uuid
from typing import Dict, List, Optional, Any, Union, Type, TypeVar, Generic
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, not_

from backend.src.crafting.models.db_models import (
    DBMaterial, DBRecipe, DBRecipeIngredient, DBRecipeOutput,
    DBSkillRequirement, DBPlayerKnownRecipe, DBCraftingLog
)
from backend.src.crafting.models.pydantic_models import (
    Material, Recipe, RecipeIngredient, RecipeOutput,
    SkillRequirement, MaterialType, Rarity
)

# Generic type for database models
ModelType = TypeVar("ModelType")
# Generic type for Pydantic models
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations with common methods.
    """
    def __init__(self, model: Type[ModelType]):
        """
        Initialize with the SQLAlchemy model.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
    
    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Record if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Pydantic model with creation data
            
        Returns:
            Created record
        """
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Existing database object
            obj_in: Update data (Pydantic model or dict)
            
        Returns:
            Updated record
        """
        obj_data = db_obj.__dict__.copy()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: str) -> ModelType:
        """
        Delete a record.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Deleted record
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

class CRUDMaterial(CRUDBase[DBMaterial, Material, Material]):
    """
    CRUD operations for materials.
    """
    def get_by_name(self, db: Session, *, name: str) -> Optional[DBMaterial]:
        """
        Get a material by name.
        
        Args:
            db: Database session
            name: Material name
            
        Returns:
            Material if found, None otherwise
        """
        return db.query(DBMaterial).filter(DBMaterial.name == name).first()
    
    def get_by_type(
        self, db: Session, *, material_type: MaterialType, skip: int = 0, limit: int = 100
    ) -> List[DBMaterial]:
        """
        Get materials by type.
        
        Args:
            db: Database session
            material_type: Material type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of materials
        """
        return (
            db.query(DBMaterial)
            .filter(DBMaterial.material_type == material_type)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_rarity(
        self, db: Session, *, rarity: Rarity, skip: int = 0, limit: int = 100
    ) -> List[DBMaterial]:
        """
        Get materials by rarity.
        
        Args:
            db: Database session
            rarity: Material rarity
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of materials
        """
        return (
            db.query(DBMaterial)
            .filter(DBMaterial.rarity == rarity)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_materials(
        self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[DBMaterial]:
        """
        Search for materials by name or description.
        
        Args:
            db: Database session
            search_term: Term to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching materials
        """
        search_pattern = f"%{search_term}%"
        return (
            db.query(DBMaterial)
            .filter(
                or_(
                    DBMaterial.name.ilike(search_pattern),
                    DBMaterial.description.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_craftable_materials(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[DBMaterial]:
        """
        Get materials that can be crafted.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of craftable materials
        """
        return (
            db.query(DBMaterial)
            .filter(DBMaterial.is_craftable == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_source_tag(
        self, db: Session, *, source_tag: str, skip: int = 0, limit: int = 100
    ) -> List[DBMaterial]:
        """
        Get materials with a specific source tag.
        
        Args:
            db: Database session
            source_tag: Source tag to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of materials
        """
        # This assumes source_tags is stored as a JSON array
        return (
            db.query(DBMaterial)
            .filter(DBMaterial.source_tags.contains([source_tag]))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_id(self, db: Session, *, obj_in: Material) -> DBMaterial:
        """
        Create a material with a specified ID or generate a new one.
        
        Args:
            db: Database session
            obj_in: Material data
            
        Returns:
            Created material
        """
        obj_in_data = obj_in.dict()
        if not obj_in_data.get("id"):
            obj_in_data["id"] = str(uuid.uuid4())
        db_obj = DBMaterial(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDRecipe(CRUDBase[DBRecipe, Recipe, Recipe]):
    """
    CRUD operations for recipes.
    """
    def get_by_name(self, db: Session, *, name: str) -> Optional[DBRecipe]:
        """
        Get a recipe by name.
        
        Args:
            db: Database session
            name: Recipe name
            
        Returns:
            Recipe if found, None otherwise
        """
        return db.query(DBRecipe).filter(DBRecipe.name == name).first()
    
    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[DBRecipe]:
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
        return (
            db.query(DBRecipe)
            .filter(DBRecipe.recipe_category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_output_item(
        self, db: Session, *, item_id: str, skip: int = 0, limit: int = 100
    ) -> List[DBRecipe]:
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
        return (
            db.query(DBRecipe)
            .join(DBRecipeOutput, DBRecipe.id == DBRecipeOutput.recipe_id)
            .filter(DBRecipeOutput.item_id == item_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_ingredient(
        self, db: Session, *, item_id: str, skip: int = 0, limit: int = 100
    ) -> List[DBRecipe]:
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
        return (
            db.query(DBRecipe)
            .join(DBRecipeIngredient, DBRecipe.id == DBRecipeIngredient.recipe_id)
            .filter(DBRecipeIngredient.item_id == item_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_station_type(
        self, db: Session, *, station_type: str, skip: int = 0, limit: int = 100
    ) -> List[DBRecipe]:
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
        return (
            db.query(DBRecipe)
            .filter(DBRecipe.required_station_type == station_type)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_discoverable_recipes(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[DBRecipe]:
        """
        Get recipes that can be discovered.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of discoverable recipes
        """
        return (
            db.query(DBRecipe)
            .filter(DBRecipe.is_discoverable == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_recipes(
        self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[DBRecipe]:
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
        search_pattern = f"%{search_term}%"
        return (
            db.query(DBRecipe)
            .filter(
                or_(
                    DBRecipe.name.ilike(search_pattern),
                    DBRecipe.description.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_recipe_with_relationships(
        self, db: Session, *, recipe_data: Recipe
    ) -> DBRecipe:
        """
        Create a recipe with all related ingredients, outputs, and skill requirements.
        
        Args:
            db: Database session
            recipe_data: Complete recipe data
            
        Returns:
            Created recipe with relationships
        """
        # Create recipe
        recipe_dict = recipe_data.dict(exclude={"ingredients", "primary_output", "byproducts", "required_skills"})
        if not recipe_dict.get("id"):
            recipe_dict["id"] = str(uuid.uuid4())
        
        recipe = DBRecipe(**recipe_dict)
        db.add(recipe)
        db.flush()  # Flush to get the recipe ID
        
        # Add primary output
        primary_output_dict = recipe_data.primary_output.dict()
        primary_output = DBRecipeOutput(
            id=str(uuid.uuid4()),
            recipe_id=recipe.id,
            is_primary=True,
            **primary_output_dict
        )
        db.add(primary_output)
        
        # Add byproducts
        for byproduct_data in recipe_data.byproducts:
            byproduct_dict = byproduct_data.dict()
            byproduct = DBRecipeOutput(
                id=str(uuid.uuid4()),
                recipe_id=recipe.id,
                is_primary=False,
                **byproduct_dict
            )
            db.add(byproduct)
        
        # Add ingredients
        for ingredient_data in recipe_data.ingredients:
            ingredient_dict = ingredient_data.dict()
            ingredient = DBRecipeIngredient(
                id=str(uuid.uuid4()),
                recipe_id=recipe.id,
                **ingredient_dict
            )
            db.add(ingredient)
        
        # Add skill requirements
        for skill_data in recipe_data.required_skills:
            skill_dict = skill_data.dict()
            skill = DBSkillRequirement(
                id=str(uuid.uuid4()),
                recipe_id=recipe.id,
                **skill_dict
            )
            db.add(skill)
        
        db.commit()
        db.refresh(recipe)
        return recipe
    
    def update_recipe_with_relationships(
        self, db: Session, *, db_obj: DBRecipe, obj_in: Recipe
    ) -> DBRecipe:
        """
        Update a recipe with all related ingredients, outputs, and skill requirements.
        
        Args:
            db: Database session
            db_obj: Existing recipe
            obj_in: Updated recipe data
            
        Returns:
            Updated recipe with relationships
        """
        # Update recipe basic fields
        recipe_dict = obj_in.dict(
            exclude={"id", "ingredients", "primary_output", "byproducts", "required_skills"}
        )
        for field, value in recipe_dict.items():
            setattr(db_obj, field, value)
        
        # Delete existing relationships to replace them
        db.query(DBRecipeOutput).filter(DBRecipeOutput.recipe_id == db_obj.id).delete()
        db.query(DBRecipeIngredient).filter(DBRecipeIngredient.recipe_id == db_obj.id).delete()
        db.query(DBSkillRequirement).filter(DBSkillRequirement.recipe_id == db_obj.id).delete()
        
        # Add primary output
        primary_output_dict = obj_in.primary_output.dict()
        primary_output = DBRecipeOutput(
            id=str(uuid.uuid4()),
            recipe_id=db_obj.id,
            is_primary=True,
            **primary_output_dict
        )
        db.add(primary_output)
        
        # Add byproducts
        for byproduct_data in obj_in.byproducts:
            byproduct_dict = byproduct_data.dict()
            byproduct = DBRecipeOutput(
                id=str(uuid.uuid4()),
                recipe_id=db_obj.id,
                is_primary=False,
                **byproduct_dict
            )
            db.add(byproduct)
        
        # Add ingredients
        for ingredient_data in obj_in.ingredients:
            ingredient_dict = ingredient_data.dict()
            ingredient = DBRecipeIngredient(
                id=str(uuid.uuid4()),
                recipe_id=db_obj.id,
                **ingredient_dict
            )
            db.add(ingredient)
        
        # Add skill requirements
        for skill_data in obj_in.required_skills:
            skill_dict = skill_data.dict()
            skill = DBSkillRequirement(
                id=str(uuid.uuid4()),
                recipe_id=db_obj.id,
                **skill_dict
            )
            db.add(skill)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDPlayerKnownRecipe(CRUDBase[DBPlayerKnownRecipe, None, None]):
    """
    CRUD operations for player known recipes.
    """
    def get_player_known_recipes(
        self, db: Session, *, player_id: str, skip: int = 0, limit: int = 100
    ) -> List[DBPlayerKnownRecipe]:
        """
        Get all recipes known by a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of known recipes
        """
        return (
            db.query(DBPlayerKnownRecipe)
            .filter(DBPlayerKnownRecipe.player_id == player_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def is_recipe_known_by_player(
        self, db: Session, *, player_id: str, recipe_id: str
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
        return db.query(
            db.query(DBPlayerKnownRecipe)
            .filter(
                DBPlayerKnownRecipe.player_id == player_id,
                DBPlayerKnownRecipe.recipe_id == recipe_id
            )
            .exists()
        ).scalar()
    
    def add_recipe_to_player(
        self, db: Session, *, player_id: str, recipe_id: str
    ) -> DBPlayerKnownRecipe:
        """
        Add a recipe to a player's known recipes.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            Created player known recipe record
        """
        # Check if already known
        if self.is_recipe_known_by_player(db=db, player_id=player_id, recipe_id=recipe_id):
            # Get and return the existing record
            return (
                db.query(DBPlayerKnownRecipe)
                .filter(
                    DBPlayerKnownRecipe.player_id == player_id,
                    DBPlayerKnownRecipe.recipe_id == recipe_id
                )
                .first()
            )
        
        # Create new record
        db_obj = DBPlayerKnownRecipe(
            id=str(uuid.uuid4()),
            player_id=player_id,
            recipe_id=recipe_id,
            discovery_date=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove_recipe_from_player(
        self, db: Session, *, player_id: str, recipe_id: str
    ) -> Optional[DBPlayerKnownRecipe]:
        """
        Remove a recipe from a player's known recipes.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            
        Returns:
            Removed record or None if not found
        """
        db_obj = (
            db.query(DBPlayerKnownRecipe)
            .filter(
                DBPlayerKnownRecipe.player_id == player_id,
                DBPlayerKnownRecipe.recipe_id == recipe_id
            )
            .first()
        )
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj
    
    def update_mastery_level(
        self, db: Session, *, player_id: str, recipe_id: str, mastery_level: int
    ) -> Optional[DBPlayerKnownRecipe]:
        """
        Update a player's mastery level for a recipe.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            mastery_level: New mastery level
            
        Returns:
            Updated record or None if not found
        """
        db_obj = (
            db.query(DBPlayerKnownRecipe)
            .filter(
                DBPlayerKnownRecipe.player_id == player_id,
                DBPlayerKnownRecipe.recipe_id == recipe_id
            )
            .first()
        )
        if db_obj:
            db_obj.mastery_level = mastery_level
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def increment_times_crafted(
        self, db: Session, *, player_id: str, recipe_id: str, quality: int = 1
    ) -> Optional[DBPlayerKnownRecipe]:
        """
        Increment the times_crafted counter for a player's known recipe.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            quality: Quality of the crafted item
            
        Returns:
            Updated record or None if not found
        """
        db_obj = (
            db.query(DBPlayerKnownRecipe)
            .filter(
                DBPlayerKnownRecipe.player_id == player_id,
                DBPlayerKnownRecipe.recipe_id == recipe_id
            )
            .first()
        )
        if db_obj:
            db_obj.times_crafted += 1
            if quality > db_obj.highest_quality_crafted:
                db_obj.highest_quality_crafted = quality
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

class CRUDCraftingLog(CRUDBase[DBCraftingLog, None, None]):
    """
    CRUD operations for crafting logs.
    """
    def get_player_crafting_logs(
        self, db: Session, *, player_id: str, skip: int = 0, limit: int = 100
    ) -> List[DBCraftingLog]:
        """
        Get crafting logs for a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of crafting logs
        """
        return (
            db.query(DBCraftingLog)
            .filter(DBCraftingLog.player_id == player_id)
            .order_by(DBCraftingLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_logs_by_recipe(
        self, db: Session, *, recipe_id: str, skip: int = 0, limit: int = 100
    ) -> List[DBCraftingLog]:
        """
        Get crafting logs for a specific recipe.
        
        Args:
            db: Database session
            recipe_id: ID of the recipe
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of crafting logs
        """
        return (
            db.query(DBCraftingLog)
            .filter(DBCraftingLog.recipe_id == recipe_id)
            .order_by(DBCraftingLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_crafting_log(
        self, db: Session, *,
        player_id: str,
        recipe_id: str,
        success: bool = True,
        quantity_attempted: int = 1,
        quantity_produced: int = 1,
        quality_achieved: int = 1,
        ingredients_consumed: List[Dict[str, Any]] = None,
        outputs_produced: List[Dict[str, Any]] = None,
        experience_gained: List[Dict[str, Any]] = None,
        crafting_location: Optional[str] = None,
        crafting_station_used: Optional[str] = None,
        custom_data: Dict[str, Any] = None
    ) -> DBCraftingLog:
        """
        Create a crafting log entry.
        
        Args:
            db: Database session
            player_id: ID of the player
            recipe_id: ID of the recipe
            success: Whether the crafting attempt was successful
            quantity_attempted: Quantity attempted to craft
            quantity_produced: Quantity actually produced
            quality_achieved: Quality level achieved
            ingredients_consumed: List of ingredients consumed
            outputs_produced: List of outputs produced
            experience_gained: List of experience gained
            crafting_location: Location where crafting occurred
            crafting_station_used: Crafting station used
            custom_data: Custom data
            
        Returns:
            Created crafting log
        """
        if ingredients_consumed is None:
            ingredients_consumed = []
        if outputs_produced is None:
            outputs_produced = []
        if experience_gained is None:
            experience_gained = []
        if custom_data is None:
            custom_data = {}
        
        db_obj = DBCraftingLog(
            id=str(uuid.uuid4()),
            player_id=player_id,
            recipe_id=recipe_id,
            timestamp=datetime.utcnow(),
            success=success,
            quantity_attempted=quantity_attempted,
            quantity_produced=quantity_produced,
            quality_achieved=quality_achieved,
            ingredients_consumed=ingredients_consumed,
            outputs_produced=outputs_produced,
            experience_gained=experience_gained,
            crafting_location=crafting_location,
            crafting_station_used=crafting_station_used,
            custom_data=custom_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# Create instances of CRUD classes
material = CRUDMaterial(DBMaterial)
recipe = CRUDRecipe(DBRecipe)
player_known_recipe = CRUDPlayerKnownRecipe(DBPlayerKnownRecipe)
crafting_log = CRUDCraftingLog(DBCraftingLog)