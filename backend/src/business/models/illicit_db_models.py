"""
Illicit Business Database Models

This module defines SQLAlchemy database models for the black market and illicit business operations.
"""

import enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from backend.src.database.base import Base
from backend.src.business.models.illicit_models import (
    IllicitItemCategory, IllicitServiceType, UnderworldRole,
    CriminalFaction, SecurityMeasure, InvestigationStatus,
    CrimeType, ConsequenceType, SmugglingStatus
)


class DBIllicitBusinessOperation(Base):
    """Database model for a business's illicit operations."""
    __tablename__ = "illicit_business_operations"

    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    is_active = Column(Boolean, default=False)
    hidden_capacity = Column(Integer, default=10)
    security_level = Column(Integer, default=1)
    security_measures = Column(JSON, default=list)
    laundering_efficiency = Column(Float, default=0.85)
    known_black_market_contacts = Column(JSON, default=list)
    bribed_officials = Column(JSON, default=list)
    criminal_faction_affiliation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    custom_data = Column(JSON, default=dict)

    # Relationships
    business = relationship("DBPlayerBusinessProfile", back_populates="illicit_operation")
    illicit_inventory = relationship("DBIllicitInventoryItem", back_populates="business_operation")
    illicit_services = relationship("DBIllicitService", back_populates="business_operation")


class DBIllicitInventoryItem(Base):
    """Database model for an item in the illicit inventory."""
    __tablename__ = "illicit_inventory_items"

    id = Column(String, primary_key=True)
    business_operation_id = Column(String, ForeignKey("illicit_business_operations.id"), nullable=False)
    item_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    purchase_price_per_unit = Column(Float, nullable=False)
    selling_price_per_unit = Column(Float, nullable=False)
    category = Column(Enum(IllicitItemCategory), nullable=False)
    is_stolen = Column(Boolean, default=False)
    origin_region_id = Column(String, nullable=True)
    acquisition_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    custom_data = Column(JSON, default=dict)

    # Relationships
    business_operation = relationship("DBIllicitBusinessOperation", back_populates="illicit_inventory")


class DBIllicitService(Base):
    """Database model for an illicit service offered by a business."""
    __tablename__ = "illicit_services"

    id = Column(String, primary_key=True)
    business_operation_id = Column(String, ForeignKey("illicit_business_operations.id"), nullable=False)
    service_type = Column(Enum(IllicitServiceType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Float, nullable=False)
    skill_requirement = Column(Integer, default=1)
    risk_level = Column(Integer, default=5)
    is_available = Column(Boolean, default=True)
    required_resources = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)

    # Relationships
    business_operation = relationship("DBIllicitBusinessOperation", back_populates="illicit_services")


class DBBlackMarketTransaction(Base):
    """Database model for a black market transaction."""
    __tablename__ = "black_market_transactions"

    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=True)
    player_id = Column(String, nullable=False)
    contact_npc_id = Column(String, nullable=True)
    transaction_type = Column(String, nullable=False)  # "buy", "sell", "service"
    item_id = Column(String, nullable=True)
    service_id = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    location_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_taken = Column(Float, nullable=False)  # 0.0-1.0
    was_detected = Column(Boolean, default=False)
    custom_data = Column(JSON, default=dict)

    # Relationships
    business = relationship("DBPlayerBusinessProfile")


class DBRegionalHeatLevel(Base):
    """Database model for heat level in a specific region."""
    __tablename__ = "regional_heat_levels"

    id = Column(String, primary_key=True)
    region_id = Column(String, nullable=False, unique=True)
    current_heat = Column(Float, default=0.0)  # 0.0-10.0
    authority_presence = Column(Integer, default=5)  # 1-10 scale
    recent_incidents = Column(Integer, default=0)
    last_patrol_time = Column(DateTime, nullable=True)
    active_investigations = Column(Integer, default=0)
    special_conditions = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBAuthorityInvestigation(Base):
    """Database model for an investigation by authorities."""
    __tablename__ = "authority_investigations"

    id = Column(String, primary_key=True)
    target_id = Column(String, nullable=False)  # Could be business_id, player_id, etc.
    target_type = Column(String, nullable=False)  # "business", "player", "location"
    investigator_npc_id = Column(String, nullable=False)
    region_id = Column(String, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.INITIAL)
    evidence_level = Column(Float, default=0.0)  # 0.0-1.0
    suspicion_cause = Column(Text, nullable=True)
    progress_notes = Column(JSON, default=list)
    expected_completion_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBSmugglingOperation(Base):
    """Database model for a smuggling operation."""
    __tablename__ = "smuggling_operations"

    id = Column(String, primary_key=True)
    business_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=True)
    player_id = Column(String, nullable=False)
    route = Column(JSON, nullable=False)  # From region_id to region_id
    goods = Column(JSON, nullable=False)  # Item ID to quantity
    assigned_npcs = Column(JSON, default=list)  # NPC IDs
    risk_assessment = Column(Float, nullable=False)  # 0.0-1.0
    start_date = Column(DateTime, default=datetime.utcnow)
    estimated_completion_date = Column(DateTime, nullable=False)
    actual_completion_date = Column(DateTime, nullable=True)
    status = Column(Enum(SmugglingStatus), default=SmugglingStatus.PLANNING)
    profit_potential = Column(Float, nullable=False)
    outcome_notes = Column(Text, nullable=True)
    custom_data = Column(JSON, default=dict)

    # Relationships
    business = relationship("DBPlayerBusinessProfile")


class DBPlayerCriminalRecord(Base):
    """Database model for a player's criminal record."""
    __tablename__ = "player_criminal_records"

    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False, unique=True)
    notoriety = Column(Float, default=0.0)  # 0.0-10.0
    known_crimes = Column(JSON, default=list)
    current_bounty = Column(Float, default=0.0)
    times_caught = Column(Integer, default=0)
    times_escaped = Column(Integer, default=0)
    faction_relationships = Column(JSON, default=dict)  # Faction ID to relationship score
    current_disguise_effectiveness = Column(Float, default=0.0)  # 0.0-1.0
    suspected_by_regions = Column(JSON, default=list)  # Region IDs
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBHiddenLocation(Base):
    """Database model for a hidden location for black market activities."""
    __tablename__ = "hidden_locations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    region_id = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "hideout", "black_market", "smuggler_den", etc.
    controlled_by_faction = Column(Enum(CriminalFaction), nullable=True)
    access_difficulty = Column(Integer, default=5)  # 1-10 scale
    security_level = Column(Integer, default=5)  # 1-10 scale
    available_services = Column(JSON, default=list)
    known_to_player_ids = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBIllicitCustomOrderRequest(Base):
    """Database model for an illicit custom order request."""
    __tablename__ = "illicit_custom_order_requests"

    id = Column(String, primary_key=True)
    requesting_npc_id = Column(String, nullable=False)
    target_player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    item_description_by_npc = Column(Text, nullable=False)
    item_category_hint = Column(Enum(IllicitItemCategory), nullable=False)
    quantity = Column(Integer, default=1)
    offered_price_initial = Column(Float, nullable=False)
    deadline_preference_days = Column(Integer, nullable=False)
    deadline_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # "awaiting_review", "accepted", "declined", "completed", "failed"
    risk_level = Column(Float, default=0.5)  # 0.0-1.0
    requires_special_skills = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("DBPlayerBusinessProfile")


# Extend existing models
def extend_item_model():
    """Add fields to the Item model to support illicit items."""
    from backend.src.item.models import DBItem
    
    # These would be added to the DBItem class if it exists
    # DBItem.illicit_in_regions = Column(JSON, default=list)
    # DBItem.is_stolen = Column(Boolean, default=False)
    # DBItem.contraband_tax_evasion_value = Column(Float, default=0.0)


def extend_business_model():
    """Add fields to the PlayerBusinessProfile model to support illicit operations."""
    from backend.src.business.models.db_models import DBPlayerBusinessProfile
    
    # These would be added to the DBPlayerBusinessProfile class
    DBPlayerBusinessProfile.criminal_notoriety_score = Column(Float, default=0.0)
    DBPlayerBusinessProfile.current_heat_level_modifier = Column(Float, default=0.0)
    
    # Add relationship to illicit operations
    DBPlayerBusinessProfile.illicit_operation = relationship(
        "DBIllicitBusinessOperation", back_populates="business", uselist=False
    )


def extend_npc_model():
    """Add fields to the NPC model to support criminal roles."""
    from backend.src.npc.models import DBNPCProfile
    
    # These would be added to the DBNPCProfile class if it exists
    # DBNPCProfile.criminal_affiliation_faction_id = Column(String, nullable=True)
    # DBNPCProfile.underworld_role = Column(Enum(UnderworldRole), nullable=True)
    # DBNPCProfile.trustworthiness_score = Column(Float, default=0.5)  # 0.0-1.0