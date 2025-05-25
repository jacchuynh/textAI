"""
Building System API

This module provides a unified API for the building and upgrade system.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.building.services.building_design_knowledge_service import BuildingDesignAndKnowledgeService
from backend.src.building.services.construction_management_service import ConstructionManagementService
from backend.src.building.services.building_operations_service import BuildingOperationsService
from backend.src.building.models.pydantic_models import (
    BuildingBlueprint, BuildingUpgradeNode, ConstructedBuilding,
    ConstructionOrUpgradeProject, ResearchProject,
    MaintenanceRecord, CosmecticCustomization, ConstructionStatus
)

logger = logging.getLogger(__name__)

class BuildingAPI:
    """
    Provides a unified API for all building and upgrade system operations.
    This class serves as the main entry point for interacting with the building system.
    """
    
    def __init__(self):
        """Initialize the building API."""
        self.building_knowledge_service = BuildingDesignAndKnowledgeService()
        self.construction_management_service = ConstructionManagementService()
        self.building_operations_service = BuildingOperationsService()
        self.logger = logging.getLogger("BuildingAPI")
    
    # === BUILDING KNOWLEDGE & DESIGN ===
    
    def get_available_blueprints(
        self,
        db: Session,
        player_id: str
    ) -> List[BuildingBlueprint]:
        """
        Get all building blueprints available to a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            
        Returns:
            List of available building blueprints
        """
        return self.building_knowledge_service.get_available_blueprints_for_player(db, player_id)
    
    def get_blueprint_details(
        self,
        db: Session,
        blueprint_id: str
    ) -> Optional[BuildingBlueprint]:
        """
        Get detailed information about a specific building blueprint.
        
        Args:
            db: Database session
            blueprint_id: ID of the blueprint
            
        Returns:
            Building blueprint details or None if not found
        """
        return self.building_knowledge_service.get_blueprint_by_id(db, blueprint_id)
    
    def learn_blueprint(
        self,
        db: Session,
        player_id: str,
        blueprint_id_or_source_details: Union[str, Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Learn or purchase a new building blueprint.
        
        Args:
            db: Database session
            player_id: ID of the player
            blueprint_id_or_source_details: Either a blueprint ID or source details
            
        Returns:
            Tuple of (success, message)
        """
        return self.building_knowledge_service.learn_or_purchase_blueprint(
            db, player_id, blueprint_id_or_source_details
        )
    
    def start_research_project(
        self,
        db: Session,
        player_id: str,
        research_subject: str,
        research_details: Optional[Dict[str, Any]] = None
    ) -> Tuple[ResearchProject, str]:
        """
        Start a research project to unlock new building technologies or upgrades.
        
        Args:
            db: Database session
            player_id: ID of the player
            research_subject: Subject of the research
            research_details: Optional additional details
            
        Returns:
            Tuple of (research_project, message)
        """
        return self.building_knowledge_service.research_building_technology_or_upgrade(
            db, player_id, research_subject, research_details
        )
    
    def get_research_projects(
        self,
        db: Session,
        player_id: str,
        include_completed: bool = False
    ) -> List[ResearchProject]:
        """
        Get all research projects for a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            include_completed: Whether to include completed projects
            
        Returns:
            List of research projects
        """
        return self.building_knowledge_service.get_research_projects_for_player(
            db, player_id, include_completed
        )
    
    def update_research_progress(
        self,
        db: Session,
        research_project_id: str,
        hours_spent: float,
        resources_used: Optional[Dict[str, int]] = None
    ) -> Tuple[float, str]:
        """
        Update the progress of a research project.
        
        Args:
            db: Database session
            research_project_id: ID of the research project
            hours_spent: Hours spent researching
            resources_used: Optional resources used
            
        Returns:
            Tuple of (new_progress_percentage, message)
        """
        return self.building_knowledge_service.update_research_progress(
            db, research_project_id, hours_spent, resources_used
        )
    
    def get_available_upgrades_for_building(
        self,
        db: Session,
        building_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all available upgrades for a specific building.
        
        Args:
            db: Database session
            building_id: ID of the building
            
        Returns:
            List of available upgrades with availability information
        """
        return self.building_operations_service.get_available_upgrades(db, building_id)
    
    def get_upgrade_details(
        self,
        db: Session,
        upgrade_id: str
    ) -> Optional[BuildingUpgradeNode]:
        """
        Get detailed information about a specific building upgrade.
        
        Args:
            db: Database session
            upgrade_id: ID of the upgrade
            
        Returns:
            Building upgrade details or None if not found
        """
        return self.building_knowledge_service.get_upgrade_node_by_id(db, upgrade_id)
    
    # === CONSTRUCTION & UPGRADE MANAGEMENT ===
    
    def start_building_construction(
        self,
        db: Session,
        player_id: str,
        property_id: str,
        blueprint_id: str,
        initial_resources: Optional[Dict[str, int]] = None,
        custom_name: Optional[str] = None
    ) -> Tuple[ConstructionOrUpgradeProject, str]:
        """
        Start a new building construction project.
        
        Args:
            db: Database session
            player_id: ID of the player
            property_id: ID of the property/land
            blueprint_id: ID of the building blueprint
            initial_resources: Optional initial resources to allocate
            custom_name: Optional custom name for the building
            
        Returns:
            Tuple of (construction_project, message)
        """
        return self.construction_management_service.initiate_building_project(
            db, player_id, property_id, blueprint_id, initial_resources, custom_name
        )
    
    def start_building_upgrade(
        self,
        db: Session,
        player_id: str,
        building_id: str,
        upgrade_id: str,
        initial_resources: Optional[Dict[str, int]] = None
    ) -> Tuple[ConstructionOrUpgradeProject, str]:
        """
        Start a new building upgrade project.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            upgrade_id: ID of the upgrade
            initial_resources: Optional initial resources to allocate
            
        Returns:
            Tuple of (upgrade_project, message)
        """
        return self.construction_management_service.initiate_upgrade_project(
            db, player_id, building_id, upgrade_id, initial_resources
        )
    
    def allocate_resources_to_project(
        self,
        db: Session,
        project_id: str,
        resources: Dict[str, int]
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Allocate resources to a construction or upgrade project.
        
        Args:
            db: Database session
            project_id: ID of the project
            resources: Resources to allocate
            
        Returns:
            Tuple of (success, message, remaining_resources_needed)
        """
        return self.construction_management_service.allocate_resources_to_project(
            db, project_id, resources
        )
    
    def assign_labor_to_project(
        self,
        db: Session,
        project_id: str,
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
        return self.construction_management_service.assign_labor_to_project(
            db, project_id, labor_source, hours_per_source
        )
    
    def update_project_progress(
        self,
        db: Session,
        project_id: str,
        hours_passed: float
    ) -> Tuple[float, str]:
        """
        Update the progress of a construction or upgrade project.
        
        Args:
            db: Database session
            project_id: ID of the project
            hours_passed: Hours that have passed
            
        Returns:
            Tuple of (new_progress_percentage, message)
        """
        return self.construction_management_service.process_project_progress_tick(
            db, project_id, hours_passed
        )
    
    def complete_project(
        self,
        db: Session,
        project_id: str
    ) -> Tuple[Optional[ConstructedBuilding], str]:
        """
        Complete a construction or upgrade project.
        
        Args:
            db: Database session
            project_id: ID of the project
            
        Returns:
            Tuple of (constructed_building, message)
        """
        return self.construction_management_service.complete_project(db, project_id)
    
    def get_player_projects(
        self,
        db: Session,
        player_id: str,
        status_filter: Optional[List[ConstructionStatus]] = None,
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
        return self.construction_management_service.get_player_construction_projects(
            db, player_id, status_filter, include_completed
        )
    
    def get_project_details(
        self,
        db: Session,
        project_id: str
    ) -> Optional[ConstructionOrUpgradeProject]:
        """
        Get details of a specific construction or upgrade project.
        
        Args:
            db: Database session
            project_id: ID of the project
            
        Returns:
            Project details or None if not found
        """
        return self.construction_management_service.get_project_details(db, project_id)
    
    def cancel_project(
        self,
        db: Session,
        project_id: str,
        player_id: str
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Cancel a construction or upgrade project.
        
        Args:
            db: Database session
            project_id: ID of the project
            player_id: ID of the player
            
        Returns:
            Tuple of (success, message, refunded_resources)
        """
        return self.construction_management_service.cancel_project(db, project_id, player_id)
    
    # === BUILDING OPERATIONS & MAINTENANCE ===
    
    def get_player_buildings(
        self,
        db: Session,
        player_id: str,
        business_id: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[ConstructedBuilding]:
        """
        Get all buildings owned by a player.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: Optional business ID to filter by
            category_filter: Optional building category to filter by
            
        Returns:
            List of constructed buildings
        """
        return self.building_operations_service.get_player_buildings(
            db, player_id, business_id, category_filter
        )
    
    def get_building_details(
        self,
        db: Session,
        player_id: str,
        building_id: str
    ) -> Optional[ConstructedBuilding]:
        """
        Get detailed information about a player's building.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            
        Returns:
            Building details or None if not found
        """
        return self.building_operations_service.get_player_building_details(db, player_id, building_id)
    
    def perform_maintenance(
        self,
        db: Session,
        player_id: str,
        building_id: str,
        maintenance_details: Dict[str, Any]
    ) -> Tuple[MaintenanceRecord, str]:
        """
        Perform maintenance on a building.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            maintenance_details: Details of the maintenance
            
        Returns:
            Tuple of (maintenance_record, message)
        """
        return self.building_operations_service.perform_building_maintenance(
            db, player_id, building_id, maintenance_details
        )
    
    def get_maintenance_history(
        self,
        db: Session,
        building_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[MaintenanceRecord]:
        """
        Get maintenance history for a building.
        
        Args:
            db: Database session
            building_id: ID of the building
            limit: Maximum number of records to return
            skip: Number of records to skip
            
        Returns:
            List of maintenance records
        """
        return self.building_operations_service.get_maintenance_history(db, building_id, limit, skip)
    
    def check_building_condition(
        self,
        db: Session,
        building_id: str
    ) -> Tuple[float, str, bool]:
        """
        Check the current condition of a building.
        
        Args:
            db: Database session
            building_id: ID of the building
            
        Returns:
            Tuple of (condition_percentage, description, needs_maintenance)
        """
        return self.building_operations_service.check_building_condition(db, building_id)
    
    def apply_cosmetic_customization(
        self,
        db: Session,
        player_id: str,
        building_id: str,
        customization_details: Dict[str, Any]
    ) -> Tuple[CosmecticCustomization, str]:
        """
        Apply a cosmetic customization to a building.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            customization_details: Details of the customization
            
        Returns:
            Tuple of (cosmetic_customization, message)
        """
        return self.building_operations_service.apply_cosmetic_customization(
            db, player_id, building_id, customization_details
        )
    
    def get_building_customizations(
        self,
        db: Session,
        building_id: str
    ) -> List[CosmecticCustomization]:
        """
        Get all cosmetic customizations applied to a building.
        
        Args:
            db: Database session
            building_id: ID of the building
            
        Returns:
            List of cosmetic customizations
        """
        return self.building_operations_service.get_building_customizations(db, building_id)
    
    def assign_building_to_business(
        self,
        db: Session,
        player_id: str,
        building_id: str,
        business_id: str
    ) -> Tuple[bool, str]:
        """
        Assign a building to a player's business.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            business_id: ID of the business
            
        Returns:
            Tuple of (success, message)
        """
        return self.building_operations_service.assign_building_to_business(
            db, player_id, building_id, business_id
        )
    
    def remove_building_from_business(
        self,
        db: Session,
        player_id: str,
        building_id: str
    ) -> Tuple[bool, str]:
        """
        Remove a building from a player's business.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            
        Returns:
            Tuple of (success, message)
        """
        return self.building_operations_service.remove_building_from_business(
            db, player_id, building_id
        )
    
    def rename_building(
        self,
        db: Session,
        player_id: str,
        building_id: str,
        new_name: str
    ) -> Tuple[bool, str]:
        """
        Rename a player's building.
        
        Args:
            db: Database session
            player_id: ID of the player
            building_id: ID of the building
            new_name: New name for the building
            
        Returns:
            Tuple of (success, message)
        """
        return self.building_operations_service.rename_building(
            db, player_id, building_id, new_name
        )