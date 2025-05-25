"""
Building System Database Models

This module defines SQLAlchemy database models for the building and upgrade system.
"""

import enum
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Enum, Text
from sqlalchemy.orm import relationship

# Import Base class from your database module
from backend.src.database.base import Base
from backend.src.building.models.pydantic_models import BuildingCategory, ConstructionStatus

class DBBuildingBlueprint(Base):
    """Database model for building blueprints."""
    __tablename__ = "building_blueprints"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    building_category = Column(Enum(BuildingCategory), nullable=False)
    prerequisites_to_acquire_blueprint = Column(JSON, default=dict)
    resource_cost_materials = Column(JSON, default=dict)
    estimated_labor_hours = Column(Float, nullable=False)
    required_tools_categories = Column(JSON, default=list)
    initial_sq_meters_or_plot_size_required = Column(Float, nullable=False)
    initial_functional_features = Column(JSON, default=dict)
    initial_staff_capacity = Column(Integer, default=0)
    initial_customer_capacity = Column(Integer, default=0)
    initial_storage_capacity = Column(Integer, default=0)
    allowed_first_tier_upgrade_paths = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buildings = relationship("DBConstructedBuilding", back_populates="blueprint")
    construction_projects = relationship("DBConstructionOrUpgradeProject", 
                                        foreign_keys="DBConstructionOrUpgradeProject.target_blueprint_id",
                                        back_populates="target_blueprint")

class DBConstructedBuilding(Base):
    """Database model for constructed buildings."""
    __tablename__ = "constructed_buildings"

    id = Column(String, primary_key=True)
    player_owner_id = Column(String, nullable=False)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=True)
    property_deed_or_lease_id = Column(String, nullable=False)
    blueprint_used_id = Column(String, ForeignKey("building_blueprints.id"), nullable=False)
    custom_name_given_by_player = Column(String, nullable=False)
    current_condition_percentage = Column(Float, default=100.0)
    current_applied_upgrades = Column(JSON, default=list)
    current_sq_meters_or_plot_size_occupied = Column(Float, nullable=False)
    current_functional_features_summary = Column(Text, nullable=False)
    current_staff_capacity = Column(Integer, nullable=False)
    current_customer_capacity = Column(Integer, nullable=False)
    current_storage_capacity = Column(Integer, nullable=False)
    active_operational_bonuses = Column(JSON, default=dict)
    visual_description_tags = Column(JSON, default=list)
    last_maintenance_date = Column(DateTime, nullable=True)
    construction_date = Column(DateTime, nullable=False)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    blueprint = relationship("DBBuildingBlueprint", back_populates="buildings")
    maintenance_records = relationship("DBMaintenanceRecord", back_populates="building")
    cosmetic_customizations = relationship("DBCosmecticCustomization", back_populates="building")
    upgrade_projects = relationship("DBConstructionOrUpgradeProject", 
                                  foreign_keys="DBConstructionOrUpgradeProject.target_building_id",
                                  back_populates="target_building")

    # Optional relationship to business profile
    business_profile = relationship("DBPlayerBusinessProfile", back_populates="buildings")

class DBConstructionOrUpgradeProject(Base):
    """Database model for construction or upgrade projects."""
    __tablename__ = "construction_upgrade_projects"

    id = Column(String, primary_key=True)
    player_owner_id = Column(String, nullable=False)
    target_building_id = Column(String, ForeignKey("constructed_buildings.id"), nullable=True)
    target_property_deed_or_lease_id = Column(String, nullable=True)
    target_blueprint_id = Column(String, ForeignKey("building_blueprints.id"), nullable=True)
    target_upgrade_node_id = Column(String, ForeignKey("building_upgrade_nodes.id"), nullable=True)
    status = Column(Enum(ConstructionStatus), default=ConstructionStatus.PLANNING_RESOURCES)
    assigned_labor_npc_ids = Column(JSON, default=list)
    player_contributing_labor_hours = Column(Float, default=0.0)
    resources_allocated = Column(JSON, default=dict)
    resources_still_needed = Column(JSON, default=dict)
    estimated_total_labor_hours_remaining = Column(Float, nullable=False)
    progress_percentage = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=True)
    estimated_completion_date = Column(DateTime, nullable=True)
    actual_completion_date = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    target_building = relationship("DBConstructedBuilding", 
                                 foreign_keys=[target_building_id],
                                 back_populates="upgrade_projects")
    target_blueprint = relationship("DBBuildingBlueprint", 
                                  foreign_keys=[target_blueprint_id],
                                  back_populates="construction_projects")
    target_upgrade_node = relationship("DBBuildingUpgradeNode", 
                                     foreign_keys=[target_upgrade_node_id],
                                     back_populates="upgrade_projects")

class DBBuildingUpgradeNode(Base):
    """Database model for building upgrade nodes."""
    __tablename__ = "building_upgrade_nodes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    applies_to_building_category_or_blueprint_id = Column(String, nullable=False)
    prerequisite_upgrade_nodes = Column(JSON, default=list)
    prerequisite_player_skills = Column(JSON, default=dict)
    prerequisite_research_id = Column(String, nullable=True)
    resource_cost_materials = Column(JSON, default=dict)
    estimated_labor_hours_for_upgrade = Column(Float, nullable=False)
    currency_cost_for_specialist_labor_or_parts = Column(Float, default=0.0)
    functional_benefits_bestowed = Column(JSON, default=dict)
    visual_change_description_tags_added = Column(JSON, default=list)
    unlocks_further_upgrade_nodes = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    upgrade_projects = relationship("DBConstructionOrUpgradeProject", 
                                  foreign_keys="DBConstructionOrUpgradeProject.target_upgrade_node_id",
                                  back_populates="target_upgrade_node")
    research_projects = relationship("DBResearchProject", 
                                   secondary="research_project_upgrade_nodes",
                                   back_populates="unlocked_upgrade_nodes")

class DBResearchProject(Base):
    """Database model for research projects."""
    __tablename__ = "research_projects"

    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False)
    research_name = Column(String, nullable=False)
    research_description = Column(Text, nullable=False)
    required_player_skills = Column(JSON, default=dict)
    required_resources = Column(JSON, default=dict)
    required_tools_or_facilities = Column(JSON, default=list)
    estimated_research_hours = Column(Float, nullable=False)
    progress_percentage = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=True)
    estimated_completion_date = Column(DateTime, nullable=True)
    actual_completion_date = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    unlocked_blueprints = relationship("DBBuildingBlueprint", 
                                     secondary="research_project_blueprints",
                                     backref="research_projects")
    unlocked_upgrade_nodes = relationship("DBBuildingUpgradeNode", 
                                        secondary="research_project_upgrade_nodes",
                                        back_populates="research_projects")

# Association tables for many-to-many relationships
class DBResearchProjectBlueprintAssociation(Base):
    """Association table for research projects and unlocked blueprints."""
    __tablename__ = "research_project_blueprints"

    research_project_id = Column(String, ForeignKey("research_projects.id"), primary_key=True)
    blueprint_id = Column(String, ForeignKey("building_blueprints.id"), primary_key=True)

class DBResearchProjectUpgradeNodeAssociation(Base):
    """Association table for research projects and unlocked upgrade nodes."""
    __tablename__ = "research_project_upgrade_nodes"

    research_project_id = Column(String, ForeignKey("research_projects.id"), primary_key=True)
    upgrade_node_id = Column(String, ForeignKey("building_upgrade_nodes.id"), primary_key=True)

class DBCosmecticCustomization(Base):
    """Database model for cosmetic customizations."""
    __tablename__ = "cosmetic_customizations"

    id = Column(String, primary_key=True)
    building_id = Column(String, ForeignKey("constructed_buildings.id"), nullable=False)
    customization_type = Column(String, nullable=False)
    customization_value = Column(String, nullable=False)
    applied_date = Column(DateTime, nullable=False)
    cost_materials = Column(JSON, default=dict)
    cost_currency = Column(Float, default=0.0)
    visual_description_tags_added = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = relationship("DBConstructedBuilding", back_populates="cosmetic_customizations")

class DBMaintenanceRecord(Base):
    """Database model for maintenance records."""
    __tablename__ = "maintenance_records"

    id = Column(String, primary_key=True)
    building_id = Column(String, ForeignKey("constructed_buildings.id"), nullable=False)
    maintenance_type = Column(String, nullable=False)
    materials_used = Column(JSON, default=dict)
    labor_hours = Column(Float, nullable=False)
    labor_cost = Column(Float, default=0.0)
    condition_before = Column(Float, nullable=False)
    condition_after = Column(Float, nullable=False)
    maintenance_date = Column(DateTime, nullable=False)
    performed_by_player = Column(Boolean, default=True)
    performed_by_npc_ids = Column(JSON, default=list)
    notes = Column(Text, default="")
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = relationship("DBConstructedBuilding", back_populates="maintenance_records")