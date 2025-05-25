"""
Building Design and Knowledge Service

This module provides services for managing building blueprints, upgrades, and research.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.building.models.db_models import (
    DBBuildingBlueprint, DBBuildingUpgradeNode, DBResearchProject,
    DBResearchProjectBlueprintAssociation, DBResearchProjectUpgradeNodeAssociation
)
from backend.src.building.models.pydantic_models import (
    BuildingBlueprint, BuildingUpgradeNode, ResearchProject
)

logger = logging.getLogger(__name__)

class BuildingDesignAndKnowledgeService:
    """
    Service for managing building blueprints, upgrade knowledge, and research.
    """

    def get_available_blueprints_for_player(
        self, db: Session, player_id: str
    ) -> List[BuildingBlueprint]:
        """
        Get all building blueprints available to a player based on their
        skills, completed quests, faction relationships, etc.

        Args:
            db: Database session
            player_id: ID of the player

        Returns:
            List of building blueprints available to the player
        """
        # Fetch all blueprints from the database
        all_blueprints = db.query(DBBuildingBlueprint).all()
        
        available_blueprints = []
        
        for blueprint in all_blueprints:
            # Check if player meets prerequisites
            if self._check_player_meets_blueprint_prerequisites(db, player_id, blueprint):
                # Convert DB model to Pydantic model
                available_blueprints.append(self._db_to_pydantic_blueprint(blueprint))
        
        return available_blueprints

    def get_blueprint_by_id(
        self, db: Session, blueprint_id: str
    ) -> Optional[BuildingBlueprint]:
        """
        Get a building blueprint by its ID.

        Args:
            db: Database session
            blueprint_id: ID of the blueprint

        Returns:
            Building blueprint or None if not found
        """
        blueprint = db.query(DBBuildingBlueprint).filter(
            DBBuildingBlueprint.id == blueprint_id
        ).first()
        
        if blueprint:
            return self._db_to_pydantic_blueprint(blueprint)
        
        return None

    def learn_or_purchase_blueprint(
        self, db: Session, player_id: str, 
        blueprint_id_or_source_details: Union[str, Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Learn or purchase a new building blueprint.

        Args:
            db: Database session
            player_id: ID of the player
            blueprint_id_or_source_details: Either the ID of the blueprint or
                                           details about how to acquire it

        Returns:
            Tuple of (success: bool, message: str)
        """
        if isinstance(blueprint_id_or_source_details, str):
            # Fetch the blueprint by ID
            blueprint = db.query(DBBuildingBlueprint).filter(
                DBBuildingBlueprint.id == blueprint_id_or_source_details
            ).first()
            
            if not blueprint:
                return False, f"Blueprint with ID {blueprint_id_or_source_details} not found."
            
            # Check if player meets prerequisites
            if not self._check_player_meets_blueprint_prerequisites(db, player_id, blueprint):
                return False, "Player does not meet the prerequisites for this blueprint."
            
            # TODO: Add to player's known blueprints
            # This would involve updating a player_known_blueprints table or similar
            
            return True, f"Successfully learned blueprint: {blueprint.name}"
        else:
            # Handle acquiring blueprint from source like quest reward, purchase, etc.
            source_type = blueprint_id_or_source_details.get('source_type')
            
            if source_type == 'purchase':
                # Handle purchase logic
                return self._handle_blueprint_purchase(
                    db, player_id, blueprint_id_or_source_details
                )
            elif source_type == 'quest_reward':
                # Handle quest reward logic
                return self._handle_blueprint_quest_reward(
                    db, player_id, blueprint_id_or_source_details
                )
            elif source_type == 'faction_reward':
                # Handle faction reward logic
                return self._handle_blueprint_faction_reward(
                    db, player_id, blueprint_id_or_source_details
                )
            else:
                return False, f"Unknown source type: {source_type}"

    def research_building_technology_or_upgrade(
        self, db: Session, player_id: str, research_subject_str: str,
        research_details: Optional[Dict[str, Any]] = None
    ) -> Tuple[ResearchProject, str]:
        """
        Start a research project to unlock new building technologies or upgrades.

        Args:
            db: Database session
            player_id: ID of the player
            research_subject_str: Description of the research subject
            research_details: Optional additional details for the research

        Returns:
            Tuple of (research_project: ResearchProject, message: str)
        """
        if not research_details:
            research_details = {}
        
        # Create a new research project
        research_project = DBResearchProject(
            id=str(uuid.uuid4()),
            player_id=player_id,
            research_name=research_details.get('name', f"Research: {research_subject_str}"),
            research_description=research_details.get('description', 
                                                    f"Research into {research_subject_str}"),
            required_player_skills=research_details.get('required_skills', {}),
            required_resources=research_details.get('required_resources', {}),
            required_tools_or_facilities=research_details.get('required_tools', []),
            estimated_research_hours=research_details.get('estimated_hours', 24.0),
            progress_percentage=0.0,
            start_date=datetime.utcnow(),
            estimated_completion_date=datetime.utcnow() + timedelta(
                hours=research_details.get('estimated_hours', 24.0)
            ),
            unlocks_blueprints=research_details.get('unlocks_blueprints', []),
            unlocks_upgrade_nodes=research_details.get('unlocks_upgrade_nodes', []),
            custom_data=research_details.get('custom_data', {})
        )
        
        db.add(research_project)
        
        # If this research unlocks blueprints, create associations
        for blueprint_id in research_details.get('unlocks_blueprints', []):
            association = DBResearchProjectBlueprintAssociation(
                research_project_id=research_project.id,
                blueprint_id=blueprint_id
            )
            db.add(association)
        
        # If this research unlocks upgrade nodes, create associations
        for upgrade_node_id in research_details.get('unlocks_upgrade_nodes', []):
            association = DBResearchProjectUpgradeNodeAssociation(
                research_project_id=research_project.id,
                upgrade_node_id=upgrade_node_id
            )
            db.add(association)
        
        db.commit()
        
        # Convert DB model to Pydantic model
        pydantic_project = self._db_to_pydantic_research_project(research_project)
        
        return pydantic_project, f"Started research project: {research_project.research_name}"

    def get_research_projects_for_player(
        self, db: Session, player_id: str, include_completed: bool = False
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
        query = db.query(DBResearchProject).filter(
            DBResearchProject.player_id == player_id
        )
        
        if not include_completed:
            query = query.filter(
                DBResearchProject.progress_percentage < 100.0
            )
        
        research_projects = query.all()
        
        return [self._db_to_pydantic_research_project(project) for project in research_projects]

    def get_upgrade_nodes_for_building(
        self, db: Session, building_category_or_blueprint_id: str
    ) -> List[BuildingUpgradeNode]:
        """
        Get all upgrade nodes applicable to a building category or specific blueprint.

        Args:
            db: Database session
            building_category_or_blueprint_id: Building category or blueprint ID

        Returns:
            List of upgrade nodes
        """
        upgrade_nodes = db.query(DBBuildingUpgradeNode).filter(
            DBBuildingUpgradeNode.applies_to_building_category_or_blueprint_id == building_category_or_blueprint_id
        ).all()
        
        return [self._db_to_pydantic_upgrade_node(node) for node in upgrade_nodes]

    def get_upgrade_node_by_id(
        self, db: Session, upgrade_node_id: str
    ) -> Optional[BuildingUpgradeNode]:
        """
        Get an upgrade node by its ID.

        Args:
            db: Database session
            upgrade_node_id: ID of the upgrade node

        Returns:
            Upgrade node or None if not found
        """
        node = db.query(DBBuildingUpgradeNode).filter(
            DBBuildingUpgradeNode.id == upgrade_node_id
        ).first()
        
        if node:
            return self._db_to_pydantic_upgrade_node(node)
        
        return None

    def check_if_player_can_apply_upgrade(
        self, db: Session, player_id: str, upgrade_node_id: str,
        constructed_building_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if a player can apply an upgrade to a building.

        Args:
            db: Database session
            player_id: ID of the player
            upgrade_node_id: ID of the upgrade node
            constructed_building_id: Optional ID of the constructed building

        Returns:
            Tuple of (can_apply: bool, reason: str)
        """
        # Get the upgrade node
        upgrade_node = db.query(DBBuildingUpgradeNode).filter(
            DBBuildingUpgradeNode.id == upgrade_node_id
        ).first()
        
        if not upgrade_node:
            return False, f"Upgrade node with ID {upgrade_node_id} not found."
        
        # Check prerequisite upgrades
        if upgrade_node.prerequisite_upgrade_nodes:
            # TODO: Check if player has applied prerequisite upgrades to this building
            pass
        
        # Check prerequisite player skills
        if upgrade_node.prerequisite_player_skills:
            # TODO: Check if player has required skills
            pass
        
        # Check prerequisite research
        if upgrade_node.prerequisite_research_id:
            # TODO: Check if player has completed the required research
            pass
        
        # If all checks pass
        return True, "Player can apply this upgrade."

    def update_research_progress(
        self, db: Session, research_project_id: str, hours_spent: float, 
        resources_used: Optional[Dict[str, int]] = None
    ) -> Tuple[float, str]:
        """
        Update the progress of a research project.

        Args:
            db: Database session
            research_project_id: ID of the research project
            hours_spent: Hours spent on research
            resources_used: Optional resources used

        Returns:
            Tuple of (new_progress_percentage: float, message: str)
        """
        # Get the research project
        research_project = db.query(DBResearchProject).filter(
            DBResearchProject.id == research_project_id
        ).first()
        
        if not research_project:
            return 0.0, f"Research project with ID {research_project_id} not found."
        
        # Calculate progress increase
        progress_increase = (hours_spent / research_project.estimated_research_hours) * 100.0
        
        # Apply progress increase
        new_progress = min(100.0, research_project.progress_percentage + progress_increase)
        research_project.progress_percentage = new_progress
        
        # If resources were used, update them
        if resources_used:
            # TODO: Update player inventory to remove used resources
            pass
        
        # If research is complete, update completion date
        if new_progress >= 100.0:
            research_project.actual_completion_date = datetime.utcnow()
            message = f"Research project '{research_project.research_name}' completed!"
        else:
            message = f"Research project '{research_project.research_name}' progress updated to {new_progress:.1f}%."
        
        db.commit()
        
        return new_progress, message

    # Helper methods
    def _check_player_meets_blueprint_prerequisites(
        self, db: Session, player_id: str, blueprint: DBBuildingBlueprint
    ) -> bool:
        """
        Check if a player meets the prerequisites for a blueprint.

        Args:
            db: Database session
            player_id: ID of the player
            blueprint: Building blueprint

        Returns:
            Whether the player meets the prerequisites
        """
        # TODO: Implement comprehensive prerequisites checking
        # This would check against player skills, completed quests, faction relationships, etc.
        
        prerequisites = blueprint.prerequisites_to_acquire_blueprint
        
        if not prerequisites:
            # If there are no prerequisites, player automatically meets them
            return True
        
        # Check each type of prerequisite
        if 'skills' in prerequisites:
            # TODO: Check player skills
            pass
        
        if 'quests' in prerequisites:
            # TODO: Check completed quests
            pass
        
        if 'factions' in prerequisites:
            # TODO: Check faction relationships
            pass
        
        if 'currency' in prerequisites:
            # TODO: Check if player has enough currency
            pass
        
        # For now, just return True for demonstration
        return True

    def _handle_blueprint_purchase(
        self, db: Session, player_id: str, purchase_details: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle purchasing a blueprint.

        Args:
            db: Database session
            player_id: ID of the player
            purchase_details: Details of the purchase

        Returns:
            Tuple of (success: bool, message: str)
        """
        blueprint_id = purchase_details.get('blueprint_id')
        cost = purchase_details.get('cost', 0)
        currency_type = purchase_details.get('currency_type', 'gold')
        
        # Get the blueprint
        blueprint = db.query(DBBuildingBlueprint).filter(
            DBBuildingBlueprint.id == blueprint_id
        ).first()
        
        if not blueprint:
            return False, f"Blueprint with ID {blueprint_id} not found."
        
        # TODO: Check if player has enough currency
        # TODO: Deduct currency from player
        # TODO: Add blueprint to player's known blueprints
        
        return True, f"Successfully purchased blueprint: {blueprint.name}"

    def _handle_blueprint_quest_reward(
        self, db: Session, player_id: str, reward_details: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle receiving a blueprint as a quest reward.

        Args:
            db: Database session
            player_id: ID of the player
            reward_details: Details of the reward

        Returns:
            Tuple of (success: bool, message: str)
        """
        blueprint_id = reward_details.get('blueprint_id')
        quest_id = reward_details.get('quest_id')
        
        # Get the blueprint
        blueprint = db.query(DBBuildingBlueprint).filter(
            DBBuildingBlueprint.id == blueprint_id
        ).first()
        
        if not blueprint:
            return False, f"Blueprint with ID {blueprint_id} not found."
        
        # TODO: Verify quest completion
        # TODO: Add blueprint to player's known blueprints
        
        return True, f"Received blueprint as quest reward: {blueprint.name}"

    def _handle_blueprint_faction_reward(
        self, db: Session, player_id: str, reward_details: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle receiving a blueprint as a faction reward.

        Args:
            db: Database session
            player_id: ID of the player
            reward_details: Details of the reward

        Returns:
            Tuple of (success: bool, message: str)
        """
        blueprint_id = reward_details.get('blueprint_id')
        faction_id = reward_details.get('faction_id')
        required_reputation = reward_details.get('required_reputation', 0)
        
        # Get the blueprint
        blueprint = db.query(DBBuildingBlueprint).filter(
            DBBuildingBlueprint.id == blueprint_id
        ).first()
        
        if not blueprint:
            return False, f"Blueprint with ID {blueprint_id} not found."
        
        # TODO: Check player's reputation with faction
        # TODO: Add blueprint to player's known blueprints
        
        return True, f"Received blueprint as faction reward: {blueprint.name}"

    # Conversion methods
    def _db_to_pydantic_blueprint(self, db_blueprint: DBBuildingBlueprint) -> BuildingBlueprint:
        """Convert a DB blueprint model to a Pydantic model."""
        return BuildingBlueprint(
            id=db_blueprint.id,
            name=db_blueprint.name,
            description=db_blueprint.description,
            building_category=db_blueprint.building_category,
            prerequisites_to_acquire_blueprint=db_blueprint.prerequisites_to_acquire_blueprint,
            resource_cost_materials=db_blueprint.resource_cost_materials,
            estimated_labor_hours=db_blueprint.estimated_labor_hours,
            required_tools_categories=db_blueprint.required_tools_categories,
            initial_sq_meters_or_plot_size_required=db_blueprint.initial_sq_meters_or_plot_size_required,
            initial_functional_features=db_blueprint.initial_functional_features,
            initial_staff_capacity=db_blueprint.initial_staff_capacity,
            initial_customer_capacity=db_blueprint.initial_customer_capacity,
            initial_storage_capacity=db_blueprint.initial_storage_capacity,
            allowed_first_tier_upgrade_paths=db_blueprint.allowed_first_tier_upgrade_paths,
            custom_data=db_blueprint.custom_data
        )

    def _db_to_pydantic_upgrade_node(self, db_node: DBBuildingUpgradeNode) -> BuildingUpgradeNode:
        """Convert a DB upgrade node model to a Pydantic model."""
        return BuildingUpgradeNode(
            id=db_node.id,
            name=db_node.name,
            description=db_node.description,
            applies_to_building_category_or_blueprint_id=db_node.applies_to_building_category_or_blueprint_id,
            prerequisite_upgrade_nodes=db_node.prerequisite_upgrade_nodes,
            prerequisite_player_skills=db_node.prerequisite_player_skills,
            prerequisite_research_id=db_node.prerequisite_research_id,
            resource_cost_materials=db_node.resource_cost_materials,
            estimated_labor_hours_for_upgrade=db_node.estimated_labor_hours_for_upgrade,
            currency_cost_for_specialist_labor_or_parts=db_node.currency_cost_for_specialist_labor_or_parts,
            functional_benefits_bestowed=db_node.functional_benefits_bestowed,
            visual_change_description_tags_added=db_node.visual_change_description_tags_added,
            unlocks_further_upgrade_nodes=db_node.unlocks_further_upgrade_nodes,
            custom_data=db_node.custom_data
        )

    def _db_to_pydantic_research_project(self, db_project: DBResearchProject) -> ResearchProject:
        """Convert a DB research project model to a Pydantic model."""
        return ResearchProject(
            id=db_project.id,
            player_id=db_project.player_id,
            research_name=db_project.research_name,
            research_description=db_project.research_description,
            required_player_skills=db_project.required_player_skills,
            required_resources=db_project.required_resources,
            required_tools_or_facilities=db_project.required_tools_or_facilities,
            estimated_research_hours=db_project.estimated_research_hours,
            progress_percentage=db_project.progress_percentage,
            unlocks_blueprints=[bp.blueprint_id for bp in db_project.unlocked_blueprints] 
                if hasattr(db_project, 'unlocked_blueprints') else [],
            unlocks_upgrade_nodes=[node.upgrade_node_id for node in db_project.unlocked_upgrade_nodes]
                if hasattr(db_project, 'unlocked_upgrade_nodes') else [],
            start_date=db_project.start_date,
            estimated_completion_date=db_project.estimated_completion_date,
            actual_completion_date=db_project.actual_completion_date,
            custom_data=db_project.custom_data
        )