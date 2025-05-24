"""
NPC System Database Models

This module defines SQLAlchemy models for the NPC generation system,
providing database persistence for NPCs and related data.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Import the database base class (assuming it's defined elsewhere)
# Replace this with your actual base class import
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Enum for economic roles
class EconomicRole(enum.Enum):
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

# Enum for gender
class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    UNSPECIFIED = "unspecified"

class DBNpc(Base):
    """SQLAlchemy model for NPCs."""
    __tablename__ = "npcs"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), default=Gender.UNSPECIFIED)
    personality_tags = Column(JSON, default=list)
    backstory_hook = Column(Text, nullable=False)
    current_location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    economic_role = Column(Enum(EconomicRole), nullable=False)
    skills = Column(JSON, default=dict)
    currency = Column(Float, default=0.0)
    inventory = Column(JSON, default=dict)
    needs = Column(JSON, default=dict)
    current_business_id = Column(String, nullable=True)
    faction_id = Column(String, nullable=True)
    relationships = Column(JSON, default=dict)
    daily_schedule = Column(JSON, default=dict)
    creation_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    custom_data = Column(JSON, default=dict)
    
    # Define relationships (uncomment as needed)
    # location = relationship("DBLocation", back_populates="npcs")
    # business = relationship("DBBusiness", back_populates="npcs")
    # faction = relationship("DBFaction", back_populates="members")

class DBNpcArchetype(Base):
    """SQLAlchemy model for NPC archetypes."""
    __tablename__ = "npc_archetypes"
    
    name = Column(String, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    possible_roles = Column(JSON, nullable=False)
    age_range = Column(JSON, default=[20, 60])
    gender_weights = Column(JSON, default=dict)
    currency_range = Column(JSON, nullable=False)
    skill_ranges = Column(JSON, nullable=False)
    personality_weights = Column(JSON, nullable=False)
    inventory_items = Column(JSON, nullable=False)
    backstory_templates = Column(JSON, nullable=False)
    need_modifiers = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)
    creation_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DBNpcSimulationState(Base):
    """SQLAlchemy model for tracking NPC simulation states."""
    __tablename__ = "npc_simulation_states"
    
    npc_id = Column(String, ForeignKey("npcs.id"), primary_key=True, index=True)
    current_activity = Column(String, default="idle")
    hunger = Column(Float, default=0.0)
    energy = Column(Float, default=1.0)
    mood = Column(Float, default=0.5)
    target_location_id = Column(String, nullable=True)
    daily_transactions = Column(JSON, default=list)
    last_meal_time = Column(DateTime, nullable=True)
    last_rest_time = Column(DateTime, nullable=True)
    last_work_time = Column(DateTime, nullable=True)
    scheduled_events = Column(JSON, default=list)
    simulation_data = Column(JSON, default=dict)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship to NPC
    npc = relationship("DBNpc")