"""
Magic-Crafting Integration Database Models
Defines the schema for magical materials, enchantments, and crafting integration
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, Index, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class MagicalMaterial(Base):
    """
    Magical materials used in crafting
    Properties affect enchantment success and item quality
    """
    __tablename__ = 'magical_materials'
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Material properties
    rarity = Column(String(50), nullable=False, index=True)  # common, uncommon, rare, legendary
    magical_affinity = Column(ARRAY(String))  # fire, water, void, etc.
    leyline_resonance = Column(Float, default=1.0)  # how strongly it connects to leylines
    corruption_resistance = Column(Float, default=1.0)  # how well it resists magical corruption
    
    # Crafting properties
    crafting_properties = Column(JSONB)  # hardness, malleability, etc.
    
    # Gathering information
    gathering_difficulty = Column(Integer, default=1)  # 1-10 scale
    primary_locations = Column(ARRAY(String))  # region types where this can be found
    required_tool = Column(String(100))  # tool needed to gather
    
    # Game balance
    base_value = Column(Integer, default=1)  # base gold value
    base_yield = Column(Integer, default=1)  # average amount found
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_material_rarity', 'rarity'),
        Index('idx_material_resonance', 'leyline_resonance'),
        Index('idx_material_difficulty', 'gathering_difficulty'),
    )


class Enchantment(Base):
    """
    Magical enchantments that can be applied to crafted items
    """
    __tablename__ = 'enchantments'
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Enchantment properties
    tier = Column(Integer, nullable=False, index=True)  # 1-5 scale of power
    magic_school = Column(String(50))  # corresponds to magic schools
    compatible_item_types = Column(ARRAY(String))  # weapon, armor, tool, etc.
    
    # Application requirements
    min_mana_cost = Column(Integer, default=10)
    min_arcane_mastery = Column(Integer, default=1)
    required_materials = Column(JSONB)  # material_id: amount
    
    # Effect data
    effects = Column(JSONB)  # JSON describing magical effects
    duration_type = Column(String(50))  # permanent, temporary, charges
    max_charges = Column(Integer, nullable=True)
    
    # Crafting difficulty
    base_success_chance = Column(Float, default=0.8)  # 0.0-1.0
    complexity = Column(Integer, default=1)  # 1-10 scale
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_enchantment_tier', 'tier'),
        Index('idx_enchantment_school', 'magic_school'),
        Index('idx_enchantment_complexity', 'complexity'),
    )


class EnchantedItem(Base):
    """
    Tracking for items that have been enchanted
    """
    __tablename__ = 'enchanted_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(String(100), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Enchantment data
    enchantment_id = Column(String(100), ForeignKey('enchantments.id'))
    enchantment = relationship("Enchantment")
    
    # Enchantment state
    quality = Column(Float, default=1.0)  # quality of the enchantment (0.5-2.0)
    charges_remaining = Column(Integer, nullable=True)  # for charge-based enchantments
    expiration_date = Column(DateTime(timezone=True), nullable=True)  # for temporary enchantments
    
    # Application details
    enchanted_by = Column(UUID(as_uuid=True), index=True)  # player who enchanted it
    enchanted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Custom properties from the enchanting process
    custom_properties = Column(JSONB)  # additional magical properties
    
    __table_args__ = (
        Index('idx_enchanted_owner', 'owner_id'),
        Index('idx_enchanted_type', 'item_type'),
        Index('idx_enchanted_quality', 'quality'),
    )


class LeylineCraftingStation(Base):
    """
    Crafting stations enhanced by leyline energy
    """
    __tablename__ = 'leyline_crafting_stations'
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    location_id = Column(String(100), nullable=False, index=True)
    
    # Station properties
    station_type = Column(String(50), nullable=False)  # forge, alchemy_lab, enchanting_table, etc.
    leyline_connection = Column(Float, default=1.0, nullable=False)
    
    # Bonuses provided
    quality_bonus = Column(Float, default=0.0)
    material_efficiency = Column(Float, default=1.0)  # material cost multiplier (lower is better)
    time_efficiency = Column(Float, default=1.0)  # crafting time multiplier (lower is better)
    special_abilities = Column(JSONB)  # special abilities unlocked
    
    # Access requirements
    access_level = Column(Integer, default=0)  # 0=public, higher=restricted
    required_reputation = Column(Integer, default=0)
    
    # State
    last_leyline_update = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_station_type', 'station_type'),
        Index('idx_station_connection', 'leyline_connection'),
        Index('idx_station_location', 'location_id'),
    )


class MagicalMaterialInstance(Base):
    """
    Instances of magical materials that players have gathered
    """
    __tablename__ = 'magical_material_instances'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = Column(String(100), ForeignKey('magical_materials.id'), nullable=False)
    material = relationship("MagicalMaterial")
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    storage_location = Column(String(100), nullable=True)  # inventory, storage, etc.
    
    # Instance properties
    quantity = Column(Integer, default=1, nullable=False)
    quality = Column(Float, default=1.0, nullable=False)  # 0.5-2.0 scale
    
    # Gathering information
    gathered_from = Column(String(100), nullable=True)  # location where gathered
    gathered_at = Column(DateTime(timezone=True), server_default=func.now())
    gathered_by = Column(UUID(as_uuid=True), nullable=True)  # player who gathered it
    
    # Special properties
    has_special_properties = Column(Boolean, default=False)
    special_properties = Column(JSONB, nullable=True)
    
    __table_args__ = (
        Index('idx_material_instance_owner', 'owner_id'),
        Index('idx_material_instance_type', 'material_id'),
        Index('idx_material_instance_quality', 'quality'),
    )


class MagicalGatheringLocation(Base):
    """
    Locations where magical materials can be gathered
    """
    __tablename__ = 'magical_gathering_locations'
    
    id = Column(String(100), primary_key=True)
    region_id = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    
    # Location properties
    location_type = Column(String(50), nullable=False)  # forest, mountain, cave, etc.
    coordinates = Column(JSONB)  # x, y coordinates
    
    # Material availability
    available_materials = Column(JSONB)  # material_id: base_chance
    current_abundance = Column(Float, default=1.0)  # modifier to drop rates
    
    # Magical properties
    leyline_strength = Column(Float, default=1.0)
    magical_aura = Column(String(50), nullable=True)  # elemental affinity
    corruption_level = Column(Float, default=0.0)
    
    # Access and state
    is_discovered = Column(Boolean, default=False)
    discovery_difficulty = Column(Integer, default=1)  # 1-10 scale
    last_refresh = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_gathering_region', 'region_id'),
        Index('idx_gathering_type', 'location_type'),
        Index('idx_gathering_leyline', 'leyline_strength'),
    )


class MagicalCraftingEvent(Base):
    """
    Events related to magical crafting and enchanting
    """
    __tablename__ = 'magical_crafting_events'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # enchant, gather, craft
    
    # Related objects
    item_id = Column(String(100), nullable=True)
    material_id = Column(String(100), nullable=True)
    enchantment_id = Column(String(100), nullable=True)
    
    # Event details
    location_id = Column(String(100), nullable=True)
    event_data = Column(JSONB)
    success = Column(Boolean, default=True)
    
    # Magic system integration
    mana_cost = Column(Float, nullable=True)
    leyline_influence = Column(Float, nullable=True)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_crafting_event_player_type', 'player_id', 'event_type'),
        Index('idx_crafting_event_item', 'item_id'),
        Index('idx_crafting_event_success', 'success'),
    )


# Materialized view for crafting statistics
CRAFTING_MATERIALIZED_VIEWS = {
    'magic_crafting_stats': """
        CREATE MATERIALIZED VIEW magic_crafting_stats AS
        SELECT 
            player_id,
            COUNT(*) as total_crafting_events,
            SUM(CASE WHEN event_type = 'enchant' THEN 1 ELSE 0 END) as enchantments_performed,
            SUM(CASE WHEN event_type = 'gather' THEN 1 ELSE 0 END) as materials_gathered,
            AVG(CASE WHEN event_type = 'enchant' THEN mana_cost ELSE NULL END) as avg_enchantment_mana,
            MAX(created_at) as last_crafting_activity,
            AVG(CASE WHEN success = true THEN 1.0 ELSE 0.0 END) as success_rate
        FROM magical_crafting_events 
        GROUP BY player_id;
    """,
    
    'material_popularity': """
        CREATE MATERIALIZED VIEW material_popularity AS
        SELECT 
            material_id,
            COUNT(*) as gather_count,
            COUNT(DISTINCT player_id) as unique_gatherers,
            AVG(CASE WHEN event_data->>'quality' IS NOT NULL 
                THEN (event_data->>'quality')::float ELSE 1.0 END) as avg_quality,
            MAX(created_at) as last_gathered
        FROM magical_crafting_events 
        WHERE event_type = 'gather' AND material_id IS NOT NULL
        GROUP BY material_id
        ORDER BY gather_count DESC;
    """,
    
    'enchantment_success_rates': """
        CREATE MATERIALIZED VIEW enchantment_success_rates AS
        SELECT 
            enchantment_id,
            COUNT(*) as attempt_count,
            SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as success_count,
            (SUM(CASE WHEN success = true THEN 1 ELSE 0 END)::float / COUNT(*)::float) as success_rate,
            AVG(mana_cost) as avg_mana_cost,
            AVG(leyline_influence) as avg_leyline_influence
        FROM magical_crafting_events 
        WHERE event_type = 'enchant' AND enchantment_id IS NOT NULL
        GROUP BY enchantment_id;
    """
}