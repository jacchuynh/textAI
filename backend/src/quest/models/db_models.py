"""
Quest System Database Models

This module defines SQLAlchemy models for the quest generation system,
providing database persistence for quests and related data.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Import the database base class (assuming it's defined elsewhere)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Enum for quest types
class QuestType(enum.Enum):
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

# Enum for quest statuses
class QuestStatus(enum.Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED_SUCCESS = "completed_success"
    COMPLETED_FAILURE = "completed_failure"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

# Enum for objective types
class ObjectiveType(enum.Enum):
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

class DBQuest(Base):
    """SQLAlchemy model for quests."""
    __tablename__ = "quests"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description_template = Column(Text, nullable=False)
    generated_description = Column(Text, nullable=False)
    quest_type = Column(Enum(QuestType), nullable=False)
    status = Column(Enum(QuestStatus), default=QuestStatus.AVAILABLE, nullable=False)
    difficulty = Column(Integer, default=1, nullable=False)
    quest_giver_npc_id = Column(String, nullable=True)
    time_limit_seconds = Column(Integer, nullable=True)
    recommended_level = Column(Integer, nullable=True)
    is_repeatable = Column(Boolean, default=False, nullable=False)
    cooldown_hours = Column(Integer, nullable=True)
    creation_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    acceptance_timestamp = Column(DateTime, nullable=True)
    completion_timestamp = Column(DateTime, nullable=True)
    associated_faction_id = Column(String, nullable=True)
    template_id = Column(String, nullable=True)
    
    # JSON fields for complex data
    objectives = Column(JSON, default=list, nullable=False)
    rewards = Column(JSON, default=dict, nullable=False)
    failure_conditions = Column(JSON, default=list, nullable=False)
    target_npc_ids = Column(JSON, default=list, nullable=False)
    related_location_ids = Column(JSON, default=list, nullable=False)
    prerequisites = Column(JSON, default=list, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    custom_data = Column(JSON, default=dict, nullable=False)
    
    # Define relationships (uncomment as needed)
    # quest_giver = relationship("DBNpc", foreign_keys=[quest_giver_npc_id])
    # associated_faction = relationship("DBFaction", foreign_keys=[associated_faction_id])
    # player_quests = relationship("DBPlayerQuest", back_populates="quest")

class DBQuestTemplate(Base):
    """SQLAlchemy model for quest templates."""
    __tablename__ = "quest_templates"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quest_type = Column(Enum(QuestType), nullable=False)
    title_format = Column(String, nullable=False)
    description_format = Column(Text, nullable=False)
    
    # JSON fields for complex data
    objective_templates = Column(JSON, nullable=False)
    reward_ranges = Column(JSON, nullable=False)
    potential_failure_conditions = Column(JSON, default=list, nullable=False)
    difficulty_range = Column(JSON, default=[1, 10], nullable=False)
    suitable_locations = Column(JSON, default=list, nullable=False)
    suitable_npcs = Column(JSON, default=list, nullable=False)
    required_npc_count = Column(Integer, default=1, nullable=False)
    required_location_count = Column(Integer, default=1, nullable=False)
    required_items = Column(JSON, default=list, nullable=False)
    parameter_selection_rules = Column(JSON, default=dict, nullable=False)
    common_prerequisites = Column(JSON, default=list, nullable=False)
    cooldown_hours = Column(Integer, nullable=True)
    default_time_limit_hours = Column(Integer, nullable=True)
    suitable_factions = Column(JSON, default=list, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    custom_data = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    creation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Define relationships
    quests = relationship("DBQuest", primaryjoin="DBQuestTemplate.id==DBQuest.template_id", viewonly=True)

class DBPlayerQuest(Base):
    """SQLAlchemy model for tracking player quest progress."""
    __tablename__ = "player_quests"
    
    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, nullable=False, index=True)
    quest_id = Column(String, ForeignKey("quests.id"), nullable=False, index=True)
    status = Column(Enum(QuestStatus), default=QuestStatus.ACTIVE, nullable=False)
    current_objectives = Column(JSON, default=list, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict, nullable=False)
    
    # Define relationships
    quest = relationship("DBQuest", foreign_keys=[quest_id])
    
    # Indexes (these would be created via migrations)
    # __table_args__ = (
    #     Index('ix_player_quests_player_quest', 'player_id', 'quest_id', unique=True),
    # )

class DBQuestEvent(Base):
    """SQLAlchemy model for tracking quest-related events."""
    __tablename__ = "quest_events"
    
    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, nullable=False, index=True)
    quest_id = Column(String, ForeignKey("quests.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, default=dict, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Define relationships
    quest = relationship("DBQuest", foreign_keys=[quest_id])