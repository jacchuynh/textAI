"""
Building System Pydantic Models

This module defines Pydantic models for the building and upgrade system.
"""

import enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

class BuildingCategory(str, enum.Enum):
    """Categories of buildings that can be constructed."""
    RESIDENTIAL = "residential"
    COMMERCIAL_SHOP = "commercial_shop" 
    INDUSTRIAL_WORKSHOP = "industrial_workshop"
    AGRICULTURAL_FARMHOUSE = "agricultural_farmhouse"
    STORAGE_WAREHOUSE = "storage_warehouse"

class ConstructionStatus(str, enum.Enum):
    """Status of a construction or upgrade project."""
    PLANNING_RESOURCES = "planning_resources"
    AWAITING_LABOR = "awaiting_labor"
    IN_PROGRESS = "in_progress"
    STALLED_NO_RESOURCES = "stalled_no_resources"
    STALLED_NO_LABOR = "stalled_no_labor"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BuildingBlueprint(BaseModel):
    """Blueprint for constructing a building."""
    id: str
    name: str
    description: str
    building_category: BuildingCategory
    prerequisites_to_acquire_blueprint: Dict[str, Any] = Field(default_factory=dict)
    resource_cost_materials: Dict[str, int] = Field(default_factory=dict)
    estimated_labor_hours: float
    required_tools_categories: List[str] = Field(default_factory=list)
    initial_sq_meters_or_plot_size_required: float
    initial_functional_features: Dict[str, Any] = Field(default_factory=dict)
    initial_staff_capacity: int = 0
    initial_customer_capacity: int = 0
    initial_storage_capacity: int = 0
    allowed_first_tier_upgrade_paths: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class ConstructedBuilding(BaseModel):
    """A building that has been constructed by a player."""
    id: str
    player_owner_id: str
    player_business_profile_id: Optional[str] = None
    property_deed_or_lease_id: str
    blueprint_used_id: str
    custom_name_given_by_player: str
    current_condition_percentage: float = 100.0
    current_applied_upgrades: List[str] = Field(default_factory=list)
    current_sq_meters_or_plot_size_occupied: float
    current_functional_features_summary: str
    current_staff_capacity: int
    current_customer_capacity: int
    current_storage_capacity: int
    active_operational_bonuses: Dict[str, float] = Field(default_factory=dict)
    visual_description_tags: List[str] = Field(default_factory=list)
    last_maintenance_date: Optional[datetime] = None
    construction_date: datetime
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class ConstructionOrUpgradeProject(BaseModel):
    """A project to construct a new building or upgrade an existing one."""
    id: str
    player_owner_id: str
    target_building_id: Optional[str] = None
    target_property_deed_or_lease_id: Optional[str] = None
    target_blueprint_id: Optional[str] = None
    target_upgrade_node_id: Optional[str] = None
    status: ConstructionStatus = ConstructionStatus.PLANNING_RESOURCES
    assigned_labor_npc_ids: List[str] = Field(default_factory=list)
    player_contributing_labor_hours: float = 0.0
    resources_allocated: Dict[str, int] = Field(default_factory=dict)
    resources_still_needed: Dict[str, int] = Field(default_factory=dict)
    estimated_total_labor_hours_remaining: float
    progress_percentage: float = 0.0
    start_date: Optional[datetime] = None
    estimated_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class BuildingUpgradeNode(BaseModel):
    """An upgrade that can be applied to a building."""
    id: str
    name: str
    description: str
    applies_to_building_category_or_blueprint_id: Union[BuildingCategory, str]
    prerequisite_upgrade_nodes: List[str] = Field(default_factory=list)
    prerequisite_player_skills: Dict[str, int] = Field(default_factory=dict)
    prerequisite_research_id: Optional[str] = None
    resource_cost_materials: Dict[str, int] = Field(default_factory=dict)
    estimated_labor_hours_for_upgrade: float
    currency_cost_for_specialist_labor_or_parts: float = 0.0
    functional_benefits_bestowed: Dict[str, Any] = Field(default_factory=dict)
    visual_change_description_tags_added: List[str] = Field(default_factory=list)
    unlocks_further_upgrade_nodes: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class ResearchProject(BaseModel):
    """A research project to unlock new building technologies or upgrades."""
    id: str
    player_id: str
    research_name: str
    research_description: str
    required_player_skills: Dict[str, int] = Field(default_factory=dict)
    required_resources: Dict[str, int] = Field(default_factory=dict)
    required_tools_or_facilities: List[str] = Field(default_factory=list)
    estimated_research_hours: float
    progress_percentage: float = 0.0
    unlocks_blueprints: List[str] = Field(default_factory=list)
    unlocks_upgrade_nodes: List[str] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    estimated_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class CosmecticCustomization(BaseModel):
    """A cosmetic customization that can be applied to a building."""
    id: str
    building_id: str
    customization_type: str  # e.g., "paint_color", "sign_design", "window_style"
    customization_value: str  # e.g., "deep_red", "ornate_gold_lettering", "stained_glass"
    applied_date: datetime
    cost_materials: Dict[str, int] = Field(default_factory=dict)
    cost_currency: float = 0.0
    visual_description_tags_added: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class MaintenanceRecord(BaseModel):
    """Record of maintenance performed on a building."""
    id: str
    building_id: str
    maintenance_type: str  # e.g., "routine", "emergency", "seasonal"
    materials_used: Dict[str, int] = Field(default_factory=dict)
    labor_hours: float
    labor_cost: float = 0.0
    condition_before: float
    condition_after: float
    maintenance_date: datetime
    performed_by_player: bool = True
    performed_by_npc_ids: List[str] = Field(default_factory=list)
    notes: str = ""
    custom_data: Dict[str, Any] = Field(default_factory=dict)