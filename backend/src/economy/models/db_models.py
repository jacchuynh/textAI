"""
Economy System Database Models

This module defines SQLAlchemy models for the economy system,
corresponding to the Pydantic models for ORM operations.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Import the database base class (assuming it's defined elsewhere)
# Replace this with your actual base class import
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class DBItem(Base):
    """SQLAlchemy model for items."""
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    base_price = Column(Float, nullable=False)
    weight = Column(Float, default=0.0)
    category = Column(String, nullable=False)
    rarity = Column(String, default="common")
    tags = Column(JSON, default=list)
    stackable = Column(Boolean, default=False)
    max_stack = Column(Integer, default=1)
    usable = Column(Boolean, default=False)
    equippable = Column(Boolean, default=False)
    craftable = Column(Boolean, default=False)
    crafting_recipe = Column(JSON, nullable=True)
    effects = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)
    
    # Relationships could be defined here
    # For example:
    # shop_inventories = relationship("DBShopInventory", back_populates="item")

class DBShop(Base):
    """SQLAlchemy model for shops."""
    __tablename__ = "shops"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    owner_id = Column(String, nullable=False)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    shop_type = Column(String, nullable=False)
    inventory = Column(JSON, default=dict)  # Stores InventorySlot as JSON
    currency_balance = Column(Float, default=100.0)
    buy_price_modifier = Column(Float, default=0.8)
    sell_price_modifier = Column(Float, default=1.2)
    reputation_required = Column(Integer, default=0)
    restocks = Column(Boolean, default=True)
    restock_interval = Column(Integer, default=24)
    last_restock = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    location = relationship("DBLocation", back_populates="shops")

class DBLocation(Base):
    """SQLAlchemy model for locations."""
    __tablename__ = "locations"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    region_id = Column(String, ForeignKey("market_regions.region_id"), nullable=False)
    location_type = Column(String, nullable=False)
    coordinates = Column(JSON, default=dict)  # {x: float, y: float, z: float}
    connected_locations = Column(JSON, default=list)  # List of location IDs
    owner_id = Column(String, nullable=True)  # May be owned by an NPC, faction, or player
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    region = relationship("DBMarketRegionInfo", back_populates="locations")
    shops = relationship("DBShop", back_populates="location")
    businesses = relationship("DBBusiness", back_populates="location")
    resources = relationship("DBResource", back_populates="location")

class DBMarketRegionInfo(Base):
    """SQLAlchemy model for market region information."""
    __tablename__ = "market_regions"
    
    region_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    prosperity_level = Column(Float, default=0.5)
    supply_demand_signals = Column(JSON, default=dict)
    category_price_modifiers = Column(JSON, default=dict)
    tax_rate = Column(Float, default=0.05)
    currency_name = Column(String, default="gold")
    currency_exchange_rates = Column(JSON, default=dict)
    trade_restrictions = Column(JSON, default=list)
    trade_bonuses = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    locations = relationship("DBLocation", back_populates="region")

class DBResource(Base):
    """SQLAlchemy model for natural resources."""
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    depletion_level = Column(Float, default=0.0)
    max_yield = Column(Float, nullable=False)
    regeneration_rate = Column(Float, default=0.0)
    extraction_difficulty = Column(Float, default=0.5)
    products = Column(JSON, nullable=False)  # Map of item ID to yield rate
    last_extraction = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    location = relationship("DBLocation", back_populates="resources")

class DBBusiness(Base):
    """SQLAlchemy model for businesses."""
    __tablename__ = "businesses"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    owner_id = Column(String, nullable=False)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    business_type = Column(String, nullable=False)
    capital = Column(Float, default=100.0)
    employees = Column(JSON, default=list)  # List of NPC or player IDs
    inventory = Column(JSON, default=dict)  # Stores InventorySlot as JSON
    input_materials_required = Column(JSON, default=dict)
    production_item_id = Column(String, nullable=True)
    production_capacity = Column(Integer, default=1)
    production_time = Column(Integer, default=24)
    last_production = Column(DateTime, nullable=True)
    efficiency = Column(Float, default=0.5)
    morale = Column(Float, default=0.5)
    upkeep_cost = Column(Float, default=10.0)
    income_history = Column(JSON, default=list)
    weekly_income_history = Column(JSON, default=list)
    upgrades = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    location = relationship("DBLocation", back_populates="businesses")

class DBCharacter(Base):
    """SQLAlchemy model for characters (players and NPCs)."""
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    character_type = Column(String, nullable=False)  # "player" or "npc"
    location_id = Column(String, nullable=True)
    currency = Column(Float, default=0.0)
    inventory = Column(JSON, default=dict)  # Stores InventorySlot as JSON
    equipped_items = Column(JSON, default=dict)
    stats = Column(JSON, default=dict)
    skills = Column(JSON, default=dict)
    reputation = Column(JSON, default=dict)  # Reputation with factions/regions
    quest_status = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)