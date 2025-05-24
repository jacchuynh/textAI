"""
Quest System Pydantic Models

This module defines Pydantic models for the quest generation system,
ensuring data validation and type safety.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
from uuid import uuid4

class QuestType(str, Enum):
    """Types of quests available in the game."""
    FETCH_ITEM = "fetch_item"
    DELIVER_ITEM = "deliver_item"
    ESCORT_NPC = "escort_npc"
    PROTECT_LOCATION = "protect_location"
    INVESTIGATE_AREA = "investigate_area"
    CRAFT_ITEM = "craft_item"
    SLAY_CREATURES = "slay_creatures"
    ECONOMIC_OPPORTUNITY = "economic_opportunity"
    GATHER_RESOURCE = "gather_resource"
    CLEAR_LOCATION = "clear_location"
    PERSUADE_NPC = "persuade_npc"
    SABOTAGE = "sabotage"
    STEAL_ITEM = "steal_item"
    EXPLORE_AREA = "explore_area"
    DIPLOMATIC_MISSION = "diplomatic_mission"
    FACTION_TASK = "faction_task"

class QuestStatus(str, Enum):
    """Status of quests in the game."""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED_SUCCESS = "completed_success"
    COMPLETED_FAILURE = "completed_failure"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ObjectiveType(str, Enum):
    """Types of objectives within quests."""
    ACQUIRE_ITEM = "acquire_item"
    REACH_LOCATION = "reach_location"
    INTERACT_NPC = "interact_npc"
    USE_SKILL = "use_skill"
    DEFEAT_TARGET = "defeat_target"
    PROTECT_TARGET = "protect_target"
    DELIVER_ITEM = "deliver_item"
    INVESTIGATE = "investigate"
    CRAFT_ITEM = "craft_item"
    GATHER_RESOURCE = "gather_resource"
    PERSUADE = "persuade"
    BRIBE = "bribe"
    INTIMIDATE = "intimidate"
    ESCORT = "escort"
    SABOTAGE = "sabotage"
    STEAL = "steal"

class QuestObjective(BaseModel):
    """
    Represents a specific objective within a quest.
    """
    id: str = Field(default_factory=lambda: f"objective-{uuid4().hex[:8]}", description="Unique identifier for the objective")
    description: str = Field(..., description="Text description of the objective")
    type: ObjectiveType = Field(..., description="Type of objective")
    target_id: Optional[str] = Field(default=None, description="ID of the item, NPC, location, or creature related to the objective")
    target_name: Optional[str] = Field(default=None, description="Name of the target for display purposes")
    required_quantity: Optional[int] = Field(default=1, description="Quantity required for completion (e.g., number of items)")
    current_quantity: int = Field(default=0, description="Current progress towards the required quantity")
    is_completed: bool = Field(default=False, description="Whether this objective has been completed")
    order: Optional[int] = Field(default=None, description="Order in which objective should be completed (if sequential)")
    optional: bool = Field(default=False, description="Whether this objective is optional")
    hidden: bool = Field(default=False, description="Whether this objective is hidden until revealed")
    completion_text: Optional[str] = Field(default=None, description="Text displayed when objective is completed")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Additional custom data for this objective")

class QuestReward(BaseModel):
    """
    Represents rewards given upon successful quest completion.
    """
    currency: float = Field(default=0.0, description="Amount of in-game currency rewarded")
    items: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Dictionary mapping item IDs to reward data (quantity, etc.)")
    experience_points: Optional[int] = Field(default=None, description="Amount of experience points rewarded")
    reputation_changes: Dict[str, float] = Field(default_factory=dict, description="Dictionary mapping faction/NPC IDs to reputation change amounts")
    skill_experience: Dict[str, int] = Field(default_factory=dict, description="Dictionary mapping skill names to experience gained")
    unlocked_quests: List[str] = Field(default_factory=list, description="List of quest IDs unlocked by completing this quest")
    unlocked_locations: List[str] = Field(default_factory=list, description="List of location IDs unlocked by completing this quest")
    unlocked_items: List[str] = Field(default_factory=list, description="List of item IDs unlocked by completing this quest")
    custom_rewards: Dict[str, Any] = Field(default_factory=dict, description="Additional custom rewards")

class QuestPrerequisite(BaseModel):
    """
    Represents a prerequisite condition for a quest to be available.
    """
    type: str = Field(..., description="Type of prerequisite (e.g., 'quest_completed', 'level', 'faction_standing')")
    value: Any = Field(..., description="Value required (e.g., quest_id, minimum level, faction reputation)")
    comparator: str = Field(default=">=", description="Comparison operator to use (e.g., '>=', '==', 'in')")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Additional custom data for this prerequisite")

class QuestFailureCondition(BaseModel):
    """
    Represents a condition that would cause quest failure.
    """
    type: str = Field(..., description="Type of failure condition (e.g., 'npc_dies', 'time_expires', 'item_destroyed')")
    target_id: Optional[str] = Field(default=None, description="ID of the entity related to the failure condition")
    description: str = Field(..., description="Human-readable description of the failure condition")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Additional custom data for this failure condition")

class QuestData(BaseModel):
    """
    Core data model for a quest.
    """
    id: str = Field(default_factory=lambda: f"quest-{uuid4().hex}", description="Unique identifier for the quest")
    title: str = Field(..., description="Title of the quest")
    description_template: str = Field(..., description="Template string for the quest description with placeholders")
    generated_description: str = Field(..., description="Fully formed description after placeholder substitution")
    quest_type: QuestType = Field(..., description="Type of quest")
    status: QuestStatus = Field(default=QuestStatus.AVAILABLE, description="Current status of the quest")
    difficulty: int = Field(default=1, description="Difficulty level of the quest (1-10)")
    objectives: List[QuestObjective] = Field(default_factory=list, description="List of objectives for this quest")
    rewards: QuestReward = Field(default_factory=QuestReward, description="Rewards for completing the quest")
    failure_conditions: List[QuestFailureCondition] = Field(default_factory=list, description="Conditions that would cause quest failure")
    quest_giver_npc_id: Optional[str] = Field(default=None, description="ID of the NPC who offers the quest")
    target_npc_ids: List[str] = Field(default_factory=list, description="List of NPC IDs relevant to the quest")
    related_location_ids: List[str] = Field(default_factory=list, description="List of location IDs relevant to the quest")
    prerequisites: List[QuestPrerequisite] = Field(default_factory=list, description="Conditions that must be met to start the quest")
    time_limit_seconds: Optional[int] = Field(default=None, description="Time limit for quest completion in seconds")
    recommended_level: Optional[int] = Field(default=None, description="Recommended player level for this quest")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing and filtering quests")
    is_repeatable: bool = Field(default=False, description="Whether this quest can be repeated")
    cooldown_hours: Optional[int] = Field(default=None, description="Hours before a repeatable quest can be taken again")
    creation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the quest was generated")
    acceptance_timestamp: Optional[datetime] = Field(default=None, description="When the quest was accepted by a player")
    completion_timestamp: Optional[datetime] = Field(default=None, description="When the quest was completed or failed")
    associated_faction_id: Optional[str] = Field(default=None, description="ID of the faction associated with this quest")
    template_id: Optional[str] = Field(default=None, description="ID of the template used to generate this quest")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Additional custom data for this quest")

class QuestGenerationContext(BaseModel):
    """
    Context information for generating a quest.
    """
    triggering_npc_id: Optional[str] = Field(default=None, description="ID of the NPC initiating the quest")
    triggering_location_id: Optional[str] = Field(default=None, description="ID of the location where the quest is initiated")
    triggering_economic_event: Optional[Dict[str, Any]] = Field(default=None, description="Details of an economic event triggering the quest")
    player_character_id: Optional[str] = Field(default=None, description="ID of the player character for quest tailoring")
    player_level: Optional[int] = Field(default=None, description="Player's level for quest difficulty scaling")
    player_faction_id: Optional[str] = Field(default=None, description="Player's faction affiliation")
    player_skills: Optional[Dict[str, int]] = Field(default=None, description="Player's skills for quest tailoring")
    desired_quest_type: Optional[QuestType] = Field(default=None, description="Specific type of quest desired")
    desired_difficulty: Optional[int] = Field(default=None, description="Desired difficulty level (1-10)")
    desired_tags: Optional[List[str]] = Field(default=None, description="Desired tags for the quest")
    excluded_quest_ids: List[str] = Field(default_factory=list, description="List of quest IDs to exclude from generation")
    world_state: Optional[Dict[str, Any]] = Field(default=None, description="Current state of the game world")
    narrative_context: Optional[Dict[str, Any]] = Field(default=None, description="Current narrative context")
    generation_reason: Optional[str] = Field(default=None, description="Reason for generating this quest")
    custom_parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional custom parameters for quest generation")

class QuestTemplate(BaseModel):
    """
    Template for generating quests of a specific type.
    """
    id: str = Field(..., description="Unique identifier for the template")
    name: str = Field(..., description="Name of the template")
    quest_type: QuestType = Field(..., description="Type of quest this template generates")
    title_format: str = Field(..., description="Format string for generating the quest title")
    description_format: str = Field(..., description="Format string for generating the quest description")
    objective_templates: List[Dict[str, Any]] = Field(..., description="Templates for generating objectives")
    reward_ranges: Dict[str, Any] = Field(..., description="Ranges for determining rewards")
    potential_failure_conditions: List[Dict[str, Any]] = Field(default_factory=list, description="Potential failure conditions")
    difficulty_range: Tuple[int, int] = Field(default=(1, 10), description="Min and max difficulty level")
    suitable_locations: List[str] = Field(default_factory=list, description="Types of locations suitable for this template")
    suitable_npcs: List[str] = Field(default_factory=list, description="Types of NPCs suitable for this template")
    required_npc_count: int = Field(default=1, description="Number of NPCs required for this template")
    required_location_count: int = Field(default=1, description="Number of locations required for this template")
    required_items: List[str] = Field(default_factory=list, description="Types of items required for this template")
    parameter_selection_rules: Dict[str, Any] = Field(default_factory=dict, description="Rules for selecting parameters")
    common_prerequisites: List[Dict[str, Any]] = Field(default_factory=list, description="Common prerequisites for this template")
    cooldown_hours: Optional[int] = Field(default=None, description="Default cooldown for repeatable quests")
    default_time_limit_hours: Optional[int] = Field(default=None, description="Default time limit in hours")
    suitable_factions: List[str] = Field(default_factory=list, description="Types of factions suitable for this template")
    tags: List[str] = Field(default_factory=list, description="Tags associated with this template")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Additional custom data for this template")

class QuestProgressUpdate(BaseModel):
    """
    Information for updating progress on a quest objective.
    """
    quest_id: str = Field(..., description="ID of the quest being updated")
    objective_id: str = Field(..., description="ID of the objective being updated")
    new_quantity: Optional[int] = Field(default=None, description="New quantity value")
    increment_by: Optional[int] = Field(default=None, description="Amount to increment current quantity by")
    set_completed: Optional[bool] = Field(default=None, description="Directly set the completed status")
    update_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data for the update")
    
    @validator('new_quantity', 'increment_by', 'set_completed')
    def validate_update_values(cls, v, values):
        """Ensure at least one update value is provided."""
        if all(values.get(field) is None for field in ['new_quantity', 'increment_by', 'set_completed']):
            raise ValueError("At least one of new_quantity, increment_by, or set_completed must be provided")
        return v