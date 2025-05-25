"""
Construction Management Service

This module provides services for managing building construction and upgrade projects.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from backend.src.building.models.db_models import (
    DBConstructionOrUpgradeProject, DBConstructedBuilding, 
    DBBuildingBlueprint, DBBuildingUpgradeNode
)
from backend.src.building.models.pydantic_models import (
    ConstructionOrUpgradeProject, ConstructedBuilding, 
    ConstructionStatus, BuildingBlueprint, BuildingUpgradeNode
)
from backend.src.building.services.building_design_knowledge_service import BuildingDesignAndKnowledgeService

logger = logging.getLogger(__name__)

class ConstructionManagementService:
    """
    Service for managing building construction and upgrade projects.
    """

    def __init__(self):
        self.building_knowledge_service = BuildingDesignAndKnowledgeService()

    def initiate_building_project(
        self, db: Session, player_id: str, property_id: str, 
        blueprint_id: str, initial_resource_commitment: Dict[str, int] = None,
        custom_name: Optional[str] = None
    ) -> Tuple[ConstructionOrUpgradeProject, str]:
        """
        Initiate a new building construction project.

        Args:
            db: Database session
            player_id: ID of the player
            property_id: ID of the property/land
            blueprint_id: ID of the building blueprint
            initial_resource_commitment: Initial resources to allocate
            custom_name: Custom name for the building

        Returns:
            Tuple of (construction_project, message)
        """
        if initial_resource_commitment is None:
            initial_resource_commitment = {}
        
        # Get the blueprint
        blueprint = self.building_knowledge_service.get_blueprint_by_id(db, blueprint_id)
        if not blueprint:
            raise ValueError(f"Blueprint with ID {blueprint_id} not found.")
        
        # TODO: Verify player owns the property
        # TODO: Verify the property has enough space for the building
        # TODO: Verify the property is in a suitable location for this building type
        
        # Create a new construction project
        project_id = str(uuid.uuid4())
        project = DBConstructionOrUpgradeProject(
            id=project_id,
            player_owner_id=player_id,
            target_property_deed_or_lease_id=property_id,
            target_blueprint_id=blueprint_id,
            status=ConstructionStatus.PLANNING_RESOURCES,
            resources_allocated=initial_resource_commitment,
            resources_still_needed=self._calculate_remaining_resources(
                blueprint.resource_cost_materials, initial_resource_commitment
            ),
            estimated_total_labor_hours_remaining=blueprint.estimated_labor_hours,
            progress_percentage=0.0,
            start_date=None,  # Will be set when actual construction begins
            estimated_completion_date=None,  # Will be calculated when construction begins
            custom_data={
                "custom_name": custom_name or blueprint.name,
                "site_preparation_complete": False,
                "foundation_complete": False,
                "structure_complete": False,
                "current_phase": "planning"
            }
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return self._db_to_pydantic_project(project), f"Construction project initiated for {blueprint.name}."

    def initiate_upgrade_project(
        self, db: Session, player_id: str, constructed_building_id: str, 
        upgrade_node_id: str, initial_resource_commitment: Dict[str, int] = None
    ) -> Tuple[ConstructionOrUpgradeProject, str]:
        """
        Initiate a new building upgrade project.

        Args:
            db: Database session
            player_id: ID of the player
            constructed_building_id: ID of the constructed building
            upgrade_node_id: ID of the upgrade node
            initial_resource_commitment: Initial resources to allocate

        Returns:
            Tuple of (upgrade_project, message)
        """
        if initial_resource_commitment is None:
            initial_resource_commitment = {}
        
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == constructed_building_id,
            DBConstructedBuilding.player_owner_id == player_id
        ).first()
        
        if not building:
            raise ValueError(f"Building with ID {constructed_building_id} not found or not owned by player.")
        
        # Get the upgrade node
        upgrade_node = self.building_knowledge_service.get_upgrade_node_by_id(db, upgrade_node_id)
        if not upgrade_node:
            raise ValueError(f"Upgrade node with ID {upgrade_node_id} not found.")
        
        # Check if the upgrade is applicable to this building
        if not self._is_upgrade_applicable_to_building(db, upgrade_node, building):
            raise ValueError(f"Upgrade {upgrade_node.name} is not applicable to this building.")
        
        # Check if player can apply this upgrade
        can_apply, reason = self.building_knowledge_service.check_if_player_can_apply_upgrade(
            db, player_id, upgrade_node_id, constructed_building_id
        )
        
        if not can_apply:
            raise ValueError(f"Cannot apply upgrade: {reason}")
        
        # Check if this upgrade is already applied
        if upgrade_node_id in building.current_applied_upgrades:
            raise ValueError(f"Upgrade {upgrade_node.name} is already applied to this building.")
        
        # Create a new upgrade project
        project_id = str(uuid.uuid4())
        project = DBConstructionOrUpgradeProject(
            id=project_id,
            player_owner_id=player_id,
            target_building_id=constructed_building_id,
            target_upgrade_node_id=upgrade_node_id,
            status=ConstructionStatus.PLANNING_RESOURCES,
            resources_allocated=initial_resource_commitment,
            resources_still_needed=self._calculate_remaining_resources(
                upgrade_node.resource_cost_materials, initial_resource_commitment
            ),
            estimated_total_labor_hours_remaining=upgrade_node.estimated_labor_hours_for_upgrade,
            progress_percentage=0.0,
            start_date=None,  # Will be set when actual upgrade begins
            estimated_completion_date=None,  # Will be calculated when upgrade begins
            custom_data={
                "upgrade_name": upgrade_node.name,
                "upgrade_phase": "planning",
                "temporary_structure_required": upgrade_node.custom_data.get("requires_temp_structure", False),
                "building_functionality_reduced_during_upgrade": 
                    upgrade_node.custom_data.get("reduces_functionality_during_upgrade", False),
                "functionality_reduction_percentage": 
                    upgrade_node.custom_data.get("functionality_reduction_percentage", 0.0)
            }
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return self._db_to_pydantic_project(project), f"Upgrade project initiated for {upgrade_node.name}."

    def allocate_resources_to_project(
        self, db: Session, project_id: str, resources: Dict[str, int]
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Allocate resources to a construction or upgrade project.

        Args:
            db: Database session
            project_id: ID of the project
            resources: Resources to allocate (item_id -> quantity)

        Returns:
            Tuple of (success, message, remaining_resources_needed)
        """
        # Get the project
        project = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.id == project_id
        ).first()
        
        if not project:
            return False, f"Project with ID {project_id} not found.", {}
        
        # TODO: Check if player has these resources
        # TODO: Remove resources from player inventory
        
        # Update allocated resources
        for item_id, quantity in resources.items():
            if item_id in project.resources_allocated:
                project.resources_allocated[item_id] += quantity
            else:
                project.resources_allocated[item_id] = quantity
        
        # Update remaining resources needed
        if project.target_blueprint_id:
            blueprint = self.building_knowledge_service.get_blueprint_by_id(db, project.target_blueprint_id)
            if blueprint:
                project.resources_still_needed = self._calculate_remaining_resources(
                    blueprint.resource_cost_materials, project.resources_allocated
                )
        elif project.target_upgrade_node_id:
            upgrade_node = self.building_knowledge_service.get_upgrade_node_by_id(db, project.target_upgrade_node_id)
            if upgrade_node:
                project.resources_still_needed = self._calculate_remaining_resources(
                    upgrade_node.resource_cost_materials, project.resources_allocated
                )
        
        # Check if all resources are allocated
        if not project.resources_still_needed:
            if project.status == ConstructionStatus.PLANNING_RESOURCES:
                project.status = ConstructionStatus.AWAITING_LABOR
                message = "All resources allocated. Project now awaiting labor assignment."
            else:
                message = "All resources allocated. Project can continue."
        else:
            message = "Resources allocated. Additional resources still needed."
        
        db.commit()
        
        return True, message, project.resources_still_needed

    def assign_labor_to_project(
        self, db: Session, project_id: str, 
        labor_source: Union[str, List[str]], 
        hours_per_source: float
    ) -> Tuple[bool, str]:
        """
        Assign labor to a construction or upgrade project.

        Args:
            db: Database session
            project_id: ID of the project
            labor_source: "player" or list of NPC IDs
            hours_per_source: Hours each source will contribute

        Returns:
            Tuple of (success, message)
        """
        # Get the project
        project = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.id == project_id
        ).first()
        
        if not project:
            return False, f"Project with ID {project_id} not found."
        
        # Check if project is ready for labor
        if project.status == ConstructionStatus.PLANNING_RESOURCES and project.resources_still_needed:
            return False, "Project needs all resources allocated before labor can be assigned."
        
        # Update labor assignment
        if labor_source == "player":
            project.player_contributing_labor_hours += hours_per_source
        else:
            for npc_id in labor_source:
                if npc_id not in project.assigned_labor_npc_ids:
                    project.assigned_labor_npc_ids.append(npc_id)
        
        # If the project hasn't started yet, set start date and estimated completion
        if project.status in [ConstructionStatus.PLANNING_RESOURCES, ConstructionStatus.AWAITING_LABOR]:
            project.status = ConstructionStatus.IN_PROGRESS
            project.start_date = datetime.utcnow()
            
            # Calculate estimated completion date
            total_labor_hours = project.player_contributing_labor_hours
            for _ in project.assigned_labor_npc_ids:
                # Assuming each NPC contributes the same amount of hours per day
                # In a real system, NPCs would have different skills and efficiency
                total_labor_hours += hours_per_source
            
            labor_hours_per_day = total_labor_hours  # Assuming this is daily labor commitment
            days_to_complete = project.estimated_total_labor_hours_remaining / labor_hours_per_day
            
            project.estimated_completion_date = project.start_date + timedelta(days=days_to_complete)
        
        db.commit()
        
        if labor_source == "player":
            return True, f"Player labor assigned to project ({hours_per_source} hours)."
        else:
            return True, f"{len(labor_source)} NPCs assigned to project ({hours_per_source} hours each)."

    def process_project_progress_tick(
        self, db: Session, project_id: str, hours_passed: float
    ) -> Tuple[float, str]:
        """
        Process progress on a construction or upgrade project for a time period.
        This would typically be called by a scheduled task (e.g., Celery task).

        Args:
            db: Database session
            project_id: ID of the project
            hours_passed: Hours that have passed

        Returns:
            Tuple of (new_progress_percentage, message)
        """
        # Get the project
        project = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.id == project_id
        ).first()
        
        if not project:
            return 0.0, f"Project with ID {project_id} not found."
        
        # Check if project is in progress
        if project.status != ConstructionStatus.IN_PROGRESS:
            return project.progress_percentage, f"Project is not in progress (current status: {project.status.value})."
        
        # Calculate labor progress
        total_labor_hours_per_tick = project.player_contributing_labor_hours
        for _ in project.assigned_labor_npc_ids:
            # Assuming each NPC contributes at a standard rate
            # In a real system, NPCs would have different skills and efficiency
            total_labor_hours_per_tick += 1.0  # Simplified for example
        
        labor_progress_this_tick = total_labor_hours_per_tick * hours_passed
        
        # Check if we need to consume resources
        if project.resources_still_needed:
            return project.progress_percentage, "Project is stalled: resources still needed."
        
        # Calculate progress increase
        progress_increase = (labor_progress_this_tick / project.estimated_total_labor_hours_remaining) * 100.0
        new_progress = min(100.0, project.progress_percentage + progress_increase)
        
        # Update project progress
        project.progress_percentage = new_progress
        
        # Reduce remaining labor hours
        project.estimated_total_labor_hours_remaining -= labor_progress_this_tick
        if project.estimated_total_labor_hours_remaining < 0:
            project.estimated_total_labor_hours_remaining = 0
        
        # Update project phase/custom data based on progress milestones
        self._update_project_phase_based_on_progress(project)
        
        # Check if project is complete
        if new_progress >= 100.0:
            project.status = ConstructionStatus.COMPLETED
            project.actual_completion_date = datetime.utcnow()
            message = f"Project completed! {project.custom_data.get('upgrade_name', 'Building')} is now finished."
        else:
            message = f"Project progress updated to {new_progress:.1f}%."
        
        db.commit()
        
        return new_progress, message

    def complete_project(
        self, db: Session, project_id: str
    ) -> Tuple[Optional[ConstructedBuilding], str]:
        """
        Complete a construction or upgrade project and apply the results.

        Args:
            db: Database session
            project_id: ID of the project

        Returns:
            Tuple of (constructed_building, message)
        """
        # Get the project
        project = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.id == project_id
        ).first()
        
        if not project:
            return None, f"Project with ID {project_id} not found."
        
        # Check if project is complete
        if project.status != ConstructionStatus.COMPLETED:
            return None, f"Project is not complete (status: {project.status.value})."
        
        # Handle building construction
        if project.target_blueprint_id:
            return self._complete_building_construction(db, project)
        
        # Handle building upgrade
        elif project.target_upgrade_node_id and project.target_building_id:
            return self._complete_building_upgrade(db, project)
        
        return None, "Invalid project: neither a construction nor an upgrade."

    def get_player_construction_projects(
        self, db: Session, player_id: str, status_filter: Optional[List[ConstructionStatus]] = None,
        include_completed: bool = False
    ) -> List[ConstructionOrUpgradeProject]:
        """
        Get all construction and upgrade projects for a player.

        Args:
            db: Database session
            player_id: ID of the player
            status_filter: Optional filter by project status
            include_completed: Whether to include completed projects

        Returns:
            List of construction and upgrade projects
        """
        query = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.player_owner_id == player_id
        )
        
        if status_filter:
            query = query.filter(DBConstructionOrUpgradeProject.status.in_([s.value for s in status_filter]))
        
        if not include_completed:
            query = query.filter(DBConstructionOrUpgradeProject.status != ConstructionStatus.COMPLETED)
        
        projects = query.all()
        
        return [self._db_to_pydantic_project(project) for project in projects]

    def get_project_details(
        self, db: Session, project_id: str
    ) -> Optional[ConstructionOrUpgradeProject]:
        """
        Get details of a specific construction or upgrade project.

        Args:
            db: Database session
            project_id: ID of the project

        Returns:
            Project details or None if not found
        """
        project = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.id == project_id
        ).first()
        
        if project:
            return self._db_to_pydantic_project(project)
        
        return None

    def cancel_project(
        self, db: Session, project_id: str, player_id: str
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Cancel a construction or upgrade project.

        Args:
            db: Database session
            project_id: ID of the project
            player_id: ID of the player (for verification)

        Returns:
            Tuple of (success, message, refunded_resources)
        """
        # Get the project
        project = db.query(DBConstructionOrUpgradeProject).filter(
            DBConstructionOrUpgradeProject.id == project_id,
            DBConstructionOrUpgradeProject.player_owner_id == player_id
        ).first()
        
        if not project:
            return False, f"Project with ID {project_id} not found or not owned by player.", {}
        
        # Check if project can be canceled
        if project.status == ConstructionStatus.COMPLETED:
            return False, "Cannot cancel a completed project.", {}
        
        # Calculate refundable resources
        # In a real system, you might refund a percentage based on progress
        refundable_resources = {}
        refund_percentage = 1.0 - (project.progress_percentage / 100.0)
        
        for item_id, quantity in project.resources_allocated.items():
            refundable_quantity = int(quantity * refund_percentage)
            if refundable_quantity > 0:
                refundable_resources[item_id] = refundable_quantity
        
        # TODO: Return resources to player inventory
        
        # Update project status
        project.status = ConstructionStatus.CANCELLED
        db.commit()
        
        return True, "Project canceled. Refundable resources calculated.", refundable_resources

    # Helper methods
    def _calculate_remaining_resources(
        self, required_resources: Dict[str, int], allocated_resources: Dict[str, int]
    ) -> Dict[str, int]:
        """Calculate remaining resources needed for a project."""
        remaining = {}
        
        for item_id, required_qty in required_resources.items():
            allocated_qty = allocated_resources.get(item_id, 0)
            if allocated_qty < required_qty:
                remaining[item_id] = required_qty - allocated_qty
        
        return remaining

    def _is_upgrade_applicable_to_building(
        self, db: Session, upgrade_node: BuildingUpgradeNode, 
        building: DBConstructedBuilding
    ) -> bool:
        """Check if an upgrade node is applicable to a building."""
        # Get the building's blueprint
        blueprint = db.query(DBBuildingBlueprint).filter(
            DBBuildingBlueprint.id == building.blueprint_used_id
        ).first()
        
        if not blueprint:
            return False
        
        # Check if upgrade applies to this building category or blueprint
        applies_to = upgrade_node.applies_to_building_category_or_blueprint_id
        
        if applies_to == blueprint.building_category:
            # Upgrade applies to this building category
            return True
        elif applies_to == blueprint.id:
            # Upgrade applies specifically to this blueprint
            return True
        
        return False

    def _update_project_phase_based_on_progress(
        self, project: DBConstructionOrUpgradeProject
    ) -> None:
        """Update the project's phase based on progress milestones."""
        if project.target_blueprint_id:
            # Construction project phases
            if project.progress_percentage >= 20 and not project.custom_data.get("site_preparation_complete"):
                project.custom_data["site_preparation_complete"] = True
                project.custom_data["current_phase"] = "foundation"
            
            if project.progress_percentage >= 50 and not project.custom_data.get("foundation_complete"):
                project.custom_data["foundation_complete"] = True
                project.custom_data["current_phase"] = "structure"
            
            if project.progress_percentage >= 80 and not project.custom_data.get("structure_complete"):
                project.custom_data["structure_complete"] = True
                project.custom_data["current_phase"] = "finishing"
        
        elif project.target_upgrade_node_id:
            # Upgrade project phases
            if project.progress_percentage >= 25 and project.custom_data.get("upgrade_phase") == "planning":
                project.custom_data["upgrade_phase"] = "preparation"
            
            if project.progress_percentage >= 50 and project.custom_data.get("upgrade_phase") == "preparation":
                project.custom_data["upgrade_phase"] = "implementation"
            
            if project.progress_percentage >= 75 and project.custom_data.get("upgrade_phase") == "implementation":
                project.custom_data["upgrade_phase"] = "finishing"

    def _complete_building_construction(
        self, db: Session, project: DBConstructionOrUpgradeProject
    ) -> Tuple[ConstructedBuilding, str]:
        """Complete a building construction project and create the building."""
        # Get the blueprint
        blueprint = self.building_knowledge_service.get_blueprint_by_id(db, project.target_blueprint_id)
        if not blueprint:
            raise ValueError(f"Blueprint with ID {project.target_blueprint_id} not found.")
        
        # Create the constructed building
        building_id = str(uuid.uuid4())
        building = DBConstructedBuilding(
            id=building_id,
            player_owner_id=project.player_owner_id,
            property_deed_or_lease_id=project.target_property_deed_or_lease_id,
            blueprint_used_id=project.target_blueprint_id,
            custom_name_given_by_player=project.custom_data.get("custom_name", blueprint.name),
            current_condition_percentage=100.0,
            current_applied_upgrades=[],
            current_sq_meters_or_plot_size_occupied=blueprint.initial_sq_meters_or_plot_size_required,
            current_functional_features_summary=self._generate_functional_features_summary(blueprint.initial_functional_features),
            current_staff_capacity=blueprint.initial_staff_capacity,
            current_customer_capacity=blueprint.initial_customer_capacity,
            current_storage_capacity=blueprint.initial_storage_capacity,
            active_operational_bonuses={},
            visual_description_tags=self._generate_initial_visual_description_tags(blueprint),
            construction_date=datetime.utcnow()
        )
        
        db.add(building)
        db.commit()
        db.refresh(building)
        
        return self._db_to_pydantic_building(building), f"Building '{building.custom_name_given_by_player}' constructed successfully!"

    def _complete_building_upgrade(
        self, db: Session, project: DBConstructionOrUpgradeProject
    ) -> Tuple[ConstructedBuilding, str]:
        """Complete a building upgrade project and apply the upgrade."""
        # Get the building
        building = db.query(DBConstructedBuilding).filter(
            DBConstructedBuilding.id == project.target_building_id
        ).first()
        
        if not building:
            raise ValueError(f"Building with ID {project.target_building_id} not found.")
        
        # Get the upgrade node
        upgrade_node = self.building_knowledge_service.get_upgrade_node_by_id(db, project.target_upgrade_node_id)
        if not upgrade_node:
            raise ValueError(f"Upgrade node with ID {project.target_upgrade_node_id} not found.")
        
        # Apply the upgrade to the building
        building.current_applied_upgrades.append(project.target_upgrade_node_id)
        
        # Apply functional benefits
        for benefit_key, benefit_value in upgrade_node.functional_benefits_bestowed.items():
            if benefit_key == "staff_capacity_increase":
                building.current_staff_capacity += int(benefit_value)
            elif benefit_key == "customer_capacity_increase":
                building.current_customer_capacity += int(benefit_value)
            elif benefit_key == "storage_capacity_increase":
                building.current_storage_capacity += int(benefit_value)
            elif benefit_key == "size_increase":
                building.current_sq_meters_or_plot_size_occupied += float(benefit_value)
            elif benefit_key == "operational_bonus":
                for bonus_key, bonus_value in benefit_value.items():
                    building.active_operational_bonuses[bonus_key] = (
                        building.active_operational_bonuses.get(bonus_key, 0.0) + float(bonus_value)
                    )
        
        # Add visual description tags
        building.visual_description_tags.extend(upgrade_node.visual_change_description_tags_added)
        
        # Update functional features summary
        if "functional_features_added" in upgrade_node.functional_benefits_bestowed:
            new_features = self._generate_functional_features_summary(
                upgrade_node.functional_benefits_bestowed["functional_features_added"]
            )
            building.current_functional_features_summary += f"\n{new_features}"
        
        db.commit()
        db.refresh(building)
        
        return self._db_to_pydantic_building(building), f"Building upgrade '{upgrade_node.name}' completed successfully!"

    def _generate_functional_features_summary(self, features: Dict[str, Any]) -> str:
        """Generate a human-readable summary of building functional features."""
        summary_parts = []
        
        for feature_type, feature_details in features.items():
            if isinstance(feature_details, int) and feature_details > 0:
                summary_parts.append(f"{feature_details} {feature_type.replace('_', ' ')}")
            elif isinstance(feature_details, list) and feature_details:
                summary_parts.append(f"{feature_type.replace('_', ' ')}: {', '.join(feature_details)}")
            elif isinstance(feature_details, dict) and feature_details:
                details_str = ", ".join(f"{k}: {v}" for k, v in feature_details.items())
                summary_parts.append(f"{feature_type.replace('_', ' ')}: {details_str}")
            elif isinstance(feature_details, str) and feature_details:
                summary_parts.append(f"{feature_type.replace('_', ' ')}: {feature_details}")
        
        return ". ".join(summary_parts)

    def _generate_initial_visual_description_tags(self, blueprint: BuildingBlueprint) -> List[str]:
        """Generate initial visual description tags based on the blueprint."""
        # These would normally come from the blueprint or be generated based on blueprint attributes
        base_tags = []
        
        if blueprint.building_category.value == "residential":
            base_tags.extend(["Modest Home", "Simple Roof", "Plain Walls"])
        elif blueprint.building_category.value == "commercial_shop":
            base_tags.extend(["Shop Front", "Display Window", "Counter"])
        elif blueprint.building_category.value == "industrial_workshop":
            base_tags.extend(["Sturdy Structure", "Workbenches", "Tool Racks"])
        elif blueprint.building_category.value == "agricultural_farmhouse":
            base_tags.extend(["Barn Style", "Hay Storage", "Rustic Exterior"])
        elif blueprint.building_category.value == "storage_warehouse":
            base_tags.extend(["Large Door", "High Ceiling", "Empty Floor Space"])
        
        # Add material-based tags based on resource costs
        if "wood" in blueprint.resource_cost_materials:
            base_tags.append("Wooden Framework")
        if "stone" in blueprint.resource_cost_materials:
            base_tags.append("Stone Foundation")
        if "thatch" in blueprint.resource_cost_materials:
            base_tags.append("Thatched Roof")
        elif "tile" in blueprint.resource_cost_materials:
            base_tags.append("Tiled Roof")
        
        # Add any custom visual tags from the blueprint
        if "visual_description_tags" in blueprint.custom_data:
            base_tags.extend(blueprint.custom_data["visual_description_tags"])
        
        return base_tags

    # Conversion methods
    def _db_to_pydantic_project(self, db_project: DBConstructionOrUpgradeProject) -> ConstructionOrUpgradeProject:
        """Convert a DB project model to a Pydantic model."""
        return ConstructionOrUpgradeProject(
            id=db_project.id,
            player_owner_id=db_project.player_owner_id,
            target_building_id=db_project.target_building_id,
            target_property_deed_or_lease_id=db_project.target_property_deed_or_lease_id,
            target_blueprint_id=db_project.target_blueprint_id,
            target_upgrade_node_id=db_project.target_upgrade_node_id,
            status=db_project.status,
            assigned_labor_npc_ids=db_project.assigned_labor_npc_ids,
            player_contributing_labor_hours=db_project.player_contributing_labor_hours,
            resources_allocated=db_project.resources_allocated,
            resources_still_needed=db_project.resources_still_needed,
            estimated_total_labor_hours_remaining=db_project.estimated_total_labor_hours_remaining,
            progress_percentage=db_project.progress_percentage,
            start_date=db_project.start_date,
            estimated_completion_date=db_project.estimated_completion_date,
            actual_completion_date=db_project.actual_completion_date,
            custom_data=db_project.custom_data
        )

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