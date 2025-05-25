"""
Material Service

This module provides services for managing materials in the crafting system.
"""

import uuid
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session

from backend.src.crafting.db.crud import material as crud_material
from backend.src.crafting.models.pydantic_models import Material, MaterialType, Rarity

class MaterialService:
    """
    Service for managing materials in the crafting system.
    """
    
    def create_material(self, db: Session, material_data: Material) -> Material:
        """
        Create a new material.
        
        Args:
            db: Database session
            material_data: Material data
            
        Returns:
            Created material
        """
        # Generate UUID if not provided
        if not material_data.id:
            material_data.id = str(uuid.uuid4())
        
        # Create the material
        db_material = crud_material.create_with_id(db=db, obj_in=material_data)
        
        # Convert DB model to Pydantic model
        return Material.from_orm(db_material)
    
    def get_material(self, db: Session, material_id: str) -> Optional[Material]:
        """
        Get a material by ID.
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            Material if found, None otherwise
        """
        db_material = crud_material.get(db=db, id=material_id)
        if db_material:
            return Material.from_orm(db_material)
        return None
    
    def get_material_by_name(self, db: Session, name: str) -> Optional[Material]:
        """
        Get a material by name.
        
        Args:
            db: Database session
            name: Material name
            
        Returns:
            Material if found, None otherwise
        """
        db_material = crud_material.get_by_name(db=db, name=name)
        if db_material:
            return Material.from_orm(db_material)
        return None
    
    def get_materials(self, db: Session, skip: int = 0, limit: int = 100) -> List[Material]:
        """
        Get multiple materials with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of materials
        """
        db_materials = crud_material.get_multi(db=db, skip=skip, limit=limit)
        return [Material.from_orm(m) for m in db_materials]
    
    def get_materials_by_type(
        self, db: Session, material_type: MaterialType, skip: int = 0, limit: int = 100
    ) -> List[Material]:
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
        db_materials = crud_material.get_by_type(
            db=db, material_type=material_type, skip=skip, limit=limit
        )
        return [Material.from_orm(m) for m in db_materials]
    
    def get_materials_by_rarity(
        self, db: Session, rarity: Rarity, skip: int = 0, limit: int = 100
    ) -> List[Material]:
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
        db_materials = crud_material.get_by_rarity(
            db=db, rarity=rarity, skip=skip, limit=limit
        )
        return [Material.from_orm(m) for m in db_materials]
    
    def search_materials(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Search for materials by name or description.
        
        Args:
            db: Database session
            search_term: Term to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of materials
        """
        db_materials = crud_material.search_materials(
            db=db, search_term=search_term, skip=skip, limit=limit
        )
        return [Material.from_orm(m) for m in db_materials]
    
    def get_craftable_materials(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """
        Get materials that can be crafted.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of materials
        """
        db_materials = crud_material.get_craftable_materials(
            db=db, skip=skip, limit=limit
        )
        return [Material.from_orm(m) for m in db_materials]
    
    def get_materials_by_source_tag(
        self, db: Session, source_tag: str, skip: int = 0, limit: int = 100
    ) -> List[Material]:
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
        db_materials = crud_material.get_by_source_tag(
            db=db, source_tag=source_tag, skip=skip, limit=limit
        )
        return [Material.from_orm(m) for m in db_materials]
    
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
        db_material = crud_material.get(db=db, id=material_id)
        if not db_material:
            return None
        
        updated_material = crud_material.update(
            db=db, db_obj=db_material, obj_in=material_data
        )
        return Material.from_orm(updated_material)
    
    def delete_material(self, db: Session, material_id: str) -> Optional[Material]:
        """
        Delete a material.
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            Deleted material or None if not found
        """
        db_material = crud_material.get(db=db, id=material_id)
        if not db_material:
            return None
        
        deleted_material = crud_material.remove(db=db, id=material_id)
        return Material.from_orm(deleted_material)
    
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
        from backend.src.crafting.db.crud import recipe as crud_recipe
        
        result = {}
        
        if as_ingredient:
            input_recipes = crud_recipe.get_by_ingredient(db=db, item_id=material_id)
            result["used_in_recipes"] = [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "category": r.recipe_category
                }
                for r in input_recipes
            ]
        
        if as_output:
            output_recipes = crud_recipe.get_by_output_item(db=db, item_id=material_id)
            result["produced_by_recipes"] = [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "category": r.recipe_category
                }
                for r in output_recipes
            ]
        
        return result
    
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
        query = db.query(crud_material.model)
        
        if region_id:
            # This assumes illicit_in_regions is stored as a JSON array
            query = query.filter(crud_material.model.illicit_in_regions.contains([region_id]))
        else:
            # Get all materials that are illicit in at least one region
            query = query.filter(crud_material.model.illicit_in_regions != [])
        
        db_materials = query.offset(skip).limit(limit).all()
        return [Material.from_orm(m) for m in db_materials]

# Create a singleton instance
material_service = MaterialService()