"""
NPC System Pydantic Models

This module defines Pydantic models for the NPC generation system,
ensuring data validation and type safety.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
from uuid import uuid4

class EconomicRole(str, Enum):
    """Economic roles that NPCs can fulfill in the game world."""
    SHOPKEEPER = "shopkeeper"
    ARTISAN_BLACKSMITH = "artisan_blacksmith"
    ARTISAN_TAILOR = "artisan_tailor"
    ARTISAN_ALCHEMIST = "artisan_alchemist"
    ARTISAN_JEWELER = "artisan_jeweler"
    ARTISAN_CARPENTER = "artisan_carpenter"
    ARTISAN_LEATHERWORKER = "artisan_leatherworker"
    FARMER = "farmer"
    MINER = "miner"
    HUNTER = "hunter"
    FISHER = "fisher"
    LABORER = "laborer"
    MERCHANT = "merchant"
    TRADER = "trader"
    NOBLE_CONSUMER = "noble_consumer"
    UNEMPLOYED_DRIFTER = "unemployed_drifter"
    GUARD = "guard"
    BANDIT = "bandit"
    SCHOLAR = "scholar"
    CLERGY = "clergy"
    ENTERTAINER = "entertainer"

class Gender(str, Enum):
    """Gender options for NPCs."""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    UNSPECIFIED = "unspecified"

class InventorySlot(BaseModel):
    """
    Represents a slot in an inventory containing an item.
    """
    item_id: str = Field(..., description="ID of the item in this slot")
    quantity: int = Field(default=1, description="Number of items in this slot")
    condition: float = Field(default=1.0, description="Condition of the items (0.0 to 1.0)")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this slot")

class NpcNeeds(BaseModel):
    """
    Represents an NPC's basic needs that drive consumption.
    """
    food: float = Field(default=1.0, description="Units of food needed per day")
    shelter: float = Field(default=1.0, description="Units of shelter needed per day")
    clothing: float = Field(default=0.5, description="Units of clothing needed per day")
    leisure: float = Field(default=0.5, description="Units of leisure needed per day")
    healthcare: float = Field(default=0.3, description="Units of healthcare needed per day")
    luxury: float = Field(default=0.2, description="Units of luxury goods needed per day")
    
    @validator('*')
    def validate_positive(cls, v, values, **kwargs):
        if v < 0:
            raise ValueError("Need values must be non-negative")
        return v

class NpcData(BaseModel):
    """
    Core data model for an NPC.
    """
    id: str = Field(default_factory=lambda: f"npc-{uuid4().hex}", description="Unique identifier for the NPC")
    name: str = Field(..., description="NPC's full name")
    age: int = Field(..., description="NPC's age", ge=16, le=80)
    gender: Gender = Field(default=Gender.UNSPECIFIED, description="NPC's gender")
    personality_tags: List[str] = Field(default_factory=list, description="List of personality traits")
    backstory_hook: str = Field(..., description="Brief backstory or hook for narrative purposes")
    current_location_id: str = Field(..., description="ID of the location where this NPC currently resides")
    economic_role: EconomicRole = Field(..., description="Primary economic function of this NPC")
    skills: Dict[str, int] = Field(default_factory=dict, description="Dictionary of skill names to proficiency levels")
    currency: float = Field(default=0.0, description="Amount of currency the NPC possesses")
    inventory: Dict[str, InventorySlot] = Field(default_factory=dict, description="Dictionary of item IDs to inventory slots")
    needs: NpcNeeds = Field(default_factory=NpcNeeds, description="NPC's basic needs that drive consumption")
    current_business_id: Optional[str] = Field(default=None, description="ID of the business this NPC owns or works at")
    faction_id: Optional[str] = Field(default=None, description="ID of the faction this NPC belongs to")
    relationships: Dict[str, float] = Field(default_factory=dict, description="Dictionary of NPC/player IDs to relationship values (-1.0 to 1.0)")
    daily_schedule: Dict[str, str] = Field(default_factory=dict, description="Dictionary mapping time periods to activities")
    creation_date: datetime = Field(default_factory=datetime.utcnow, description="When this NPC was created")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When this NPC was last updated")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this NPC")

class NpcGenerationParams(BaseModel):
    """
    Parameters for generating a new NPC.
    """
    target_location_id: str = Field(..., description="ID of the location where the NPC will be generated")
    requested_role: Optional[EconomicRole] = Field(default=None, description="Specific economic role requested")
    archetype_name: Optional[str] = Field(default=None, description="Name of the archetype to use for generation")
    age_range: Optional[Tuple[int, int]] = Field(default=None, description="Min and max age range")
    gender: Optional[Gender] = Field(default=None, description="Specific gender requested")
    min_currency: Optional[float] = Field(default=None, description="Minimum starting currency")
    max_currency: Optional[float] = Field(default=None, description="Maximum starting currency")
    required_skills: Optional[List[str]] = Field(default=None, description="Skills the NPC must have")
    faction_id: Optional[str] = Field(default=None, description="Faction the NPC should belong to")
    personality_traits: Optional[List[str]] = Field(default=None, description="Specific personality traits to include")
    custom_params: Dict[str, Any] = Field(default_factory=dict, description="Additional custom parameters")

class NpcArchetype(BaseModel):
    """
    Template for generating NPCs of a specific type.
    """
    name: str = Field(..., description="Unique name of this archetype")
    description: str = Field(..., description="Description of this archetype")
    possible_roles: List[EconomicRole] = Field(..., description="Possible economic roles for this archetype")
    age_range: Tuple[int, int] = Field(default=(20, 60), description="Min and max age range")
    gender_weights: Dict[Gender, float] = Field(default_factory=dict, description="Probability weights for different genders")
    currency_range: Tuple[float, float] = Field(..., description="Min and max starting currency")
    skill_ranges: Dict[str, Tuple[int, int]] = Field(..., description="Dictionary mapping skill names to (min, max) proficiency")
    personality_weights: Dict[str, float] = Field(..., description="Probability weights for different personality traits")
    inventory_items: List[Dict[str, Any]] = Field(..., description="List of possible inventory items with weights and quantities")
    backstory_templates: List[str] = Field(..., description="Templates for generating backstory hooks")
    need_modifiers: Dict[str, float] = Field(default_factory=dict, description="Modifiers to apply to basic needs")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this archetype")

class NpcSimulationState(BaseModel):
    """
    Current simulation state for an NPC, used for tracking their activities and states.
    """
    npc_id: str = Field(..., description="ID of the NPC")
    current_activity: str = Field(default="idle", description="What the NPC is currently doing")
    hunger: float = Field(default=0.0, description="Current hunger level (0.0 to 1.0)")
    energy: float = Field(default=1.0, description="Current energy level (0.0 to 1.0)")
    mood: float = Field(default=0.5, description="Current mood (0.0 to 1.0)")
    target_location_id: Optional[str] = Field(default=None, description="Where the NPC is heading")
    daily_transactions: List[Dict[str, Any]] = Field(default_factory=list, description="Economic transactions made today")
    last_meal_time: Optional[datetime] = Field(default=None, description="When the NPC last ate")
    last_rest_time: Optional[datetime] = Field(default=None, description="When the NPC last rested")
    last_work_time: Optional[datetime] = Field(default=None, description="When the NPC last worked")
    scheduled_events: List[Dict[str, Any]] = Field(default_factory=list, description="Upcoming events for this NPC")
    simulation_data: Dict[str, Any] = Field(default_factory=dict, description="Additional simulation-specific data")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When this state was last updated")