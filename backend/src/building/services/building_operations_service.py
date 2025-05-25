"""
Building Operations Service

This module provides services for managing day-to-day building operations,
maintenance, and customization.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from backend.src.building.models.db_models import (
    DBConstructedBuilding, DBMaintenanceRecord, DBCosmecticCustomization
)
from backend.src.building.models.pydantic_models import (
    ConstructedBuilding, MaintenanceRecord, CosmecticCustomization
)
from backend.src.building.services.building_design_knowledge_service import BuildingDesignAndKnowledgeService

logger = logging.getLogger(__name__)

class BuildingOperationsService:
    """
    Service for managing building operations, maintenance, and customization.
    """

    def __init__(self):
        self.building_knowledge_service = BuildingDesignAndKnowledgeService()

    def get_player_building_details(
        self, db: Session, player_id: str, constructed_building_id: str
    ) -> Optional[ConstructedBuilding]:
        """
        Get detailed information about a player's constructed building.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building

        Returns:
            Building details or None if not found/not owned by player
        """
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if building:
            return self._db_to_pydantic_building(building)
        
        return None

    def get_player_buildings(
        self, db: Session, player_id: str, 
        business_id: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[ConstructedBuilding]:
        """
        Get all buildings owned by a player, optionally filtered.

        Args:
            db: Database session
            player_id: ID of the player
            business_id: Optional business ID to filter by
            category_filter: Optional building category to filter by

        Returns:
            List of constructed buildings
        """
        query = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.player_owner_id == player_id
        )
        
        if business_id:
            query = query.filter(DBConstructedBuilding.player_business_profile_id == business_id)
        
        if category_filter:
            # This requires joining with the blueprint table
            query = query.join(
                DBConstructedBuilding.blueprint
            ).filter(
                DBConstructedBuilding.blueprint.has(building_category=category_filter)
            )
        
        buildings = query.all()
        
        return [self._db_to_pydantic_building(building) for building in buildings]

    def perform_building_maintenance(
        self, db: Session, player_id: str, constructed_building_id: str, 
        maintenance_details: Dict[str, Any]
    ) -> Tuple[MaintenanceRecord, str]:
        """
        Perform maintenance on a building to improve its condition.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building
            maintenance_details: Details of the maintenance

        Returns:
            Tuple of (maintenance_record, message)
        """
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if not building:
            raise ValueError(f"Building with ID {constructed_building_id} not found or not owned by player.")
        
        # Extract maintenance details
        maintenance_type = maintenance_details.get('maintenance_type', 'routine')
        materials_used = maintenance_details.get('materials_used', {})
        labor_hours = maintenance_details.get('labor_hours', 1.0)
        labor_cost = maintenance_details.get('labor_cost', 0.0)
        performed_by_player = maintenance_details.get('performed_by_player', True)
        performed_by_npc_ids = maintenance_details.get('performed_by_npc_ids', [])
        notes = maintenance_details.get('notes', '')
        
        # Calculate condition improvement
        condition_before = building.current_condition_percentage
        condition_improvement = self._calculate_maintenance_effectiveness(
            maintenance_type, materials_used, labor_hours, building
        )
        
        # Apply condition improvement
        new_condition = min(100.0, condition_before + condition_improvement)
        building.current_condition_percentage = new_condition
        building.last_maintenance_date = datetime.utcnow()
        
        # Create maintenance record
        maintenance_id = str(uuid.uuid4())
        maintenance_record = DBMaintenanceRecord(
            id=maintenance_id,
            building_id=constructed_building_id,
            maintenance_type=maintenance_type,
            materials_used=materials_used,
            labor_hours=labor_hours,
            labor_cost=labor_cost,
            condition_before=condition_before,
            condition_after=new_condition,
            maintenance_date=datetime.utcnow(),
            performed_by_player=performed_by_player,
            performed_by_npc_ids=performed_by_npc_ids,
            notes=notes
        )
        
        db.add(maintenance_record)
        db.commit()
        db.refresh(maintenance_record)
        
        # TODO: Remove used materials from player inventory
        
        message = (
            f"Maintenance complete. Building condition improved from "
            f"{condition_before:.1f}% to {new_condition:.1f}%."
        )
        
        return self._db_to_pydantic_maintenance_record(maintenance_record), message

    def get_maintenance_history(
        self, db: Session, constructed_building_id: str, 
        limit: int = 10, skip: int = 0
    ) -> List[MaintenanceRecord]:
        """
        Get maintenance history for a building.

        Args:
            db: Database session
            constructed_building_id: ID of the constructed building
            limit: Maximum number of records to return
            skip: Number of records to skip

        Returns:
            List of maintenance records
        """
        maintenance_records = db.query(DBMaintenanceRecord).filter(
            DBMaintenanceRecord.building_id == constructed_building_id
        ).order_by(
            DBMaintenanceRecord.maintenance_date.desc()
        ).offset(skip).limit(limit).all()
        
        return [self._db_to_pydantic_maintenance_record(record) for record in maintenance_records]

    def check_building_condition(
        self, db: Session, constructed_building_id: str
    ) -> Tuple[float, str, bool]:
        """
        Check the current condition of a building and whether maintenance is needed.

        Args:
            db: Database session
            constructed_building_id: ID of the constructed building

        Returns:
            Tuple of (condition_percentage, description, needs_maintenance)
        """
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id
        ).first()
        
        if not building:
            raise ValueError(f"Building with ID {constructed_building_id} not found.")
        
        condition = building.current_condition_percentage
        
        # Generate a descriptive message based on condition
        if condition >= 90:
            description = "Excellent condition. The building looks almost new."
            needs_maintenance = False
        elif condition >= 75:
            description = "Good condition. Some minor wear is visible but nothing concerning."
            needs_maintenance = False
        elif condition >= 50:
            description = "Fair condition. Signs of wear and tear are becoming noticeable."
            needs_maintenance = True
        elif condition >= 25:
            description = "Poor condition. The building is showing significant deterioration."
            needs_maintenance = True
        else:
            description = "Critical condition. Urgent repairs are needed to prevent structural damage."
            needs_maintenance = True
        
        return condition, description, needs_maintenance

    def apply_cosmetic_customization(
        self, db: Session, player_id: str, constructed_building_id: str, 
        customization_details: Dict[str, Any]
    ) -> Tuple[CosmecticCustomization, str]:
        """
        Apply a cosmetic customization to a building.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building
            customization_details: Details of the customization

        Returns:
            Tuple of (cosmetic_customization, message)
        """
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if not building:
            raise ValueError(f"Building with ID {constructed_building_id} not found or not owned by player.")
        
        # Extract customization details
        customization_type = customization_details.get('type')
        customization_value = customization_details.get('value')
        cost_materials = customization_details.get('cost_materials', {})
        cost_currency = customization_details.get('cost_currency', 0.0)
        visual_tags = customization_details.get('visual_description_tags_added', [])
        
        if not customization_type or not customization_value:
            raise ValueError("Customization type and value are required.")
        
        # TODO: Check if player has the required materials/currency
        # TODO: Remove materials/currency from player inventory
        
        # Create customization record
        customization_id = str(uuid.uuid4())
        customization = DBCosmecticCustomization(
            id=customization_id,
            building_id=constructed_building_id,
            customization_type=customization_type,
            customization_value=customization_value,
            applied_date=datetime.utcnow(),
            cost_materials=cost_materials,
            cost_currency=cost_currency,
            visual_description_tags_added=visual_tags
        )
        
        db.add(customization)
        
        # Add visual tags to the building
        building.visual_description_tags.extend(visual_tags)
        
        db.commit()
        db.refresh(customization)
        
        return self._db_to_pydantic_customization(customization), f"Applied {customization_type} customization to the building."

    def get_building_customizations(
        self, db: Session, constructed_building_id: str
    ) -> List[CosmecticCustomization]:
        """
        Get all cosmetic customizations applied to a building.

        Args:
            db: Database session
            constructed_building_id: ID of the constructed building

        Returns:
            List of cosmetic customizations
        """
        customizations = db.query(DBCosmecticCustomization).filter(
            DBCosmecticCustomization.building_id == constructed_building_id
        ).order_by(
            DBCosmecticCustomization.applied_date.desc()
        ).all()
        
        return [self._db_to_pydantic_customization(customization) for customization in customizations]

    def assign_building_to_business(
        self, db: Session, player_id: str, constructed_building_id: str, 
        business_id: str
    ) -> Tuple[bool, str]:
        """
        Assign a building to a player's business.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building
            business_id: ID of the business

        Returns:
            Tuple of (success, message)
        """
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if not building:
            return False, f"Building with ID {constructed_building_id} not found or not owned by player."
        
        # TODO: Check if the business exists and is owned by the player
        
        # Check if building is already assigned to a business
        if building.player_business_profile_id:
            if building.player_business_profile_id == business_id:
                return False, "Building is already assigned to this business."
            else:
                return False, "Building is already assigned to another business."
        
        # Assign the building to the business
        building.player_business_profile_id = business_id
        db.commit()
        
        return True, f"Building successfully assigned to business ID {business_id}."

    def remove_building_from_business(
        self, db: Session, player_id: str, constructed_building_id: str
    ) -> Tuple[bool, str]:
        """
        Remove a building from a player's business.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building

        Returns:
            Tuple of (success, message)
        """
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if not building:
            return False, f"Building with ID {constructed_building_id} not found or not owned by player."
        
        # Check if building is assigned to a business
        if not building.player_business_profile_id:
            return False, "Building is not assigned to any business."
        
        # Remove the building from the business
        building.player_business_profile_id = None
        db.commit()
        
        return True, "Building successfully removed from business."

    def rename_building(
        self, db: Session, player_id: str, constructed_building_id: str, 
        new_name: str
    ) -> Tuple[bool, str]:
        """
        Rename a player's building.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building
            new_name: New name for the building

        Returns:
            Tuple of (success, message)
        """
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if not building:
            return False, f"Building with ID {constructed_building_id} not found or not owned by player."
        
        old_name = building.custom_name_given_by_player
        building.custom_name_given_by_player = new_name
        db.commit()
        
        return True, f"Building renamed from '{old_name}' to '{new_name}'."

    def get_available_upgrades(
        self, db: Session, constructed_building_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all available upgrades for a building.

        Args:
            db: Database session
            constructed_building_id: ID of the constructed building

        Returns:
            List of available upgrade nodes with availability information
        """
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id
        ).first()
        
        if not building:
            raise ValueError(f"Building with ID {constructed_building_id} not found.")
        
        # Get the building's blueprint
        blueprint = self.building_knowledge_service.get_blueprint_by_id(db, building.blueprint_used_id)
        if not blueprint:
            raise ValueError(f"Blueprint with ID {building.blueprint_used_id} not found.")
        
        # Get all applicable upgrade nodes
        upgrade_nodes = self.building_knowledge_service.get_upgrade_nodes_for_building(
            db, blueprint.id
        )
        upgrade_nodes.extend(
            self.building_knowledge_service.get_upgrade_nodes_for_building(
                db, blueprint.building_category.value
            )
        )
        
        # Filter out already applied upgrades
        upgrade_nodes = [
            node for node in upgrade_nodes 
            if node.id not in building.current_applied_upgrades
        ]
        
        # For each upgrade node, check prerequisites
        result = []
        for node in upgrade_nodes:
            # Check if prerequisites are met
            prerequisites_met = True
            missing_prerequisites = []
            
            # Check prerequisite upgrades
            for prereq_id in node.prerequisite_upgrade_nodes:
                if prereq_id not in building.current_applied_upgrades:
                    prerequisites_met = False
                    prereq_node = self.building_knowledge_service.get_upgrade_node_by_id(db, prereq_id)
                    if prereq_node:
                        missing_prerequisites.append(f"Missing prerequisite upgrade: {prereq_node.name}")
            
            # Check prerequisite research
            if node.prerequisite_research_id:
                # TODO: Check if player has completed the research
                # For now, assume research is not completed
                prerequisites_met = False
                missing_prerequisites.append(f"Research required: {node.prerequisite_research_id}")
            
            # Add to result with availability info
            result.append({
                "upgrade_node": node,
                "prerequisites_met": prerequisites_met,
                "missing_prerequisites": missing_prerequisites,
                "estimated_cost": self._calculate_total_upgrade_cost(node)
            })
        
        return result

    # Helper methods
    def _calculate_maintenance_effectiveness(
        self, maintenance_type: str, materials_used: Dict[str, int], 
        labor_hours: float, building: DBConstructedBuilding
    ) -> float:
        """
        Calculate the effectiveness of maintenance based on type, materials, and labor.

        Args:
            maintenance_type: Type of maintenance
            materials_used: Materials used
            labor_hours: Hours of labor
            building: The building being maintained

        Returns:
            Condition improvement percentage
        """
        # Base improvement based on maintenance type
        if maintenance_type == "routine":
            base_improvement = 5.0
        elif maintenance_type == "major":
            base_improvement = 15.0
        elif maintenance_type == "emergency":
            base_improvement = 25.0
        elif maintenance_type == "seasonal":
            base_improvement = 10.0
        else:
            base_improvement = 5.0
        
        # Material quality modifier
        material_modifier = 1.0
        total_materials = sum(materials_used.values())
        if total_materials > 0:
            # TODO: Calculate material quality based on actual materials
            # For now, simply scale based on quantity
            material_modifier = 1.0 + (total_materials / 20.0)  # Cap at 2.0x for 20+ materials
            if material_modifier > 2.0:
                material_modifier = 2.0
        
        # Labor modifier
        labor_modifier = 1.0
        if labor_hours > 0:
            labor_modifier = 1.0 + (labor_hours / 10.0)  # Cap at 2.0x for 10+ hours
            if labor_modifier > 2.0:
                labor_modifier = 2.0
        
        # Building age modifier (older buildings are harder to maintain)
        age_days = (datetime.utcnow() - building.construction_date).days
        age_modifier = 1.0
        if age_days > 30:  # If older than 30 days
            age_modifier = 1.0 - (min(age_days, 365) / 365.0) * 0.5  # Cap at 0.5x reduction for 1+ year
        
        # Calculate final improvement
        improvement = base_improvement * material_modifier * labor_modifier * age_modifier
        
        # Cap the improvement based on current condition
        # (it's harder to improve a building that's already in good condition)
        current_condition = building.current_condition_percentage
        if current_condition > 90:
            improvement *= 0.5  # 50% effectiveness for buildings in excellent condition
        elif current_condition > 75:
            improvement *= 0.75  # 75% effectiveness for buildings in good condition
        
        return improvement

    def _calculate_total_upgrade_cost(
        self, upgrade_node: Any
    ) -> Dict[str, Any]:
        """
        Calculate the total cost of an upgrade, including materials and currency.

        Args:
            upgrade_node: The upgrade node

        Returns:
            Dictionary with cost details
        """
        return {
            "materials": upgrade_node.resource_cost_materials,
            "currency": upgrade_node.currency_cost_for_specialist_labor_or_parts,
            "labor_hours": upgrade_node.estimated_labor_hours_for_upgrade
        }

    # Conversion methods
    def _db_to_pydantic_building(self, db_building: DBConstructedBuilding) -> ConstructedBuilding:
        """Convert a DB building model to a Pydantic model."""
        return ConstructedBuilding(
            id=db_building.id,
            player_owner_id=db_building.player_owner_id,
            player_business_profile_id=db_building.player_business_profile_id,
            property_deed_or_lease_id=db_building.property_deed_or_lease_id,
            blueprint_used_id=db_building.blueprint_used_id,
            custom_name_given_by_player=db_building.custom_name_given_by_player,
            current_condition_percentage=db_building.current_condition_percentage,
            current_applied_upgrades=db_building.current_applied_upgrades,
            current_sq_meters_or_plot_size_occupied=db_building.current_sq_meters_or_plot_size_occupied,
            current_functional_features_summary=db_building.current_functional_features_summary,
            current_staff_capacity=db_building.current_staff_capacity,
            current_customer_capacity=db_building.current_customer_capacity,
            current_storage_capacity=db_building.current_storage_capacity,
            active_operational_bonuses=db_building.active_operational_bonuses,
            visual_description_tags=db_building.visual_description_tags,
            last_maintenance_date=db_building.last_maintenance_date,
            construction_date=db_building.construction_date,
            custom_data=db_building.custom_data
        )

    def _db_to_pydantic_maintenance_record(self, db_record: DBMaintenanceRecord) -> MaintenanceRecord:
        """Convert a DB maintenance record model to a Pydantic model."""
        return MaintenanceRecord(
            id=db_record.id,
            building_id=db_record.building_id,
            maintenance_type=db_record.maintenance_type,
            materials_used=db_record.materials_used,
            labor_hours=db_record.labor_hours,
            labor_cost=db_record.labor_cost,
            condition_before=db_record.condition_before,
            condition_after=db_record.condition_after,
            maintenance_date=db_record.maintenance_date,
            performed_by_player=db_record.performed_by_player,
            performed_by_npc_ids=db_record.performed_by_npc_ids,
            notes=db_record.notes,
            custom_data=db_record.custom_data
        )

    def _db_to_pydantic_customization(self, db_customization: DBCosmecticCustomization) -> CosmecticCustomization:
        """Convert a DB cosmetic customization model to a Pydantic model."""
        return CosmecticCustomization(
            id=db_customization.id,
            building_id=db_customization.building_id,
            customization_type=db_customization.customization_type,
            customization_value=db_customization.customization_value,
            applied_date=db_customization.applied_date,
            cost_materials=db_customization.cost_materials,
            cost_currency=db_customization.cost_currency,
            visual_description_tags_added=db_customization.visual_description_tags_added,
            custom_data=db_customization.custom_data
        )