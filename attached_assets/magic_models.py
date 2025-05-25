"""
Enhanced Magic System Database Models for PostgreSQL
Optimized for performance with your existing magic system
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, Index, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class MagicEvent(Base):
    """
    Partitioned table for all magic-related events
    Optimized for time-series queries and analytics
    """
    __tablename__ = 'magic_events'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    spell_id = Column(String(100), index=True)
    domain_id = Column(String(50), index=True)
    
    # JSONB for flexible magic data storage
    event_data = Column(JSONB)
    
    # Performance metrics
    mana_cost = Column(Float)
    cast_time = Column(Float)
    success_rate = Column(Float)
    
    # Corruption tracking
    corruption_before = Column(Float)
    corruption_after = Column(Float)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_magic_events_player_type_time', 'player_id', 'event_type', 'created_at'),
        Index('idx_magic_events_domain_time', 'domain_id', 'created_at'),
        Index('idx_magic_events_spell_success', 'spell_id', 'success_rate'),
        Index('idx_magic_events_mana_cost', 'mana_cost'),
        # GIN index for JSONB queries
        Index('idx_magic_events_data_gin', 'event_data', postgresql_using='gin'),
    )

class PlayerMagicState(Base):
    """
    Current magic state for each player
    Frequently updated, heavily cached
    """
    __tablename__ = 'player_magic_state'
    
    player_id = Column(UUID(as_uuid=True), primary_key=True)
    
    # Current mana state
    current_mana = Column(Float, nullable=False, default=100.0)
    max_mana = Column(Float, nullable=False, default=100.0)
    mana_regen_rate = Column(Float, nullable=False, default=1.0)
    
    # Magic mastery levels
    arcane_mastery = Column(Integer, default=0)
    mana_infusion = Column(Integer, default=0)
    spiritual_utility = Column(Integer, default=0)
    
    # Corruption state
    corruption_level = Column(Float, default=0.0)
    corruption_resistance = Column(Float, default=1.0)
    
    # Active effects
    active_enchantments = Column(ARRAY(String))
    active_buffs = Column(JSONB)
    
    # Cooldowns
    spell_cooldowns = Column(JSONB)
    
    # Last updates
    last_mana_update = Column(DateTime(timezone=True), server_default=func.now())
    last_corruption_check = Column(DateTime(timezone=True), server_default=func.now())
    
    # Performance indexes
    __table_args__ = (
        Index('idx_player_magic_mana', 'current_mana'),
        Index('idx_player_magic_corruption', 'corruption_level'),
        Index('idx_player_magic_last_update', 'last_mana_update'),
    )

class SpellTemplate(Base):
    """
    Spell definitions with performance metadata
    """
    __tablename__ = 'spell_templates'
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    tier = Column(Integer, nullable=False, index=True)
    magic_type = Column(String(50), nullable=False, index=True)
    
    # Spell requirements
    mana_cost = Column(Float, nullable=False)
    min_mastery_level = Column(Integer, default=0)
    components = Column(ARRAY(String))
    cast_time = Column(Float, default=1.0)
    
    # Spell effects data
    effects = Column(JSONB)
    
    # Performance tracking
    avg_success_rate = Column(Float, default=1.0)
    usage_count = Column(Integer, default=0)
    
    # Vector for similarity matching
    feature_vector = Column(ARRAY(Float))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_spell_tier_type', 'tier', 'magic_type'),
        Index('idx_spell_mana_cost', 'mana_cost'),
        Index('idx_spell_usage', 'usage_count'),
    )

class LeylineNode(Base):
    """
    Leyline network with real-time strength tracking
    """
    __tablename__ = 'leyline_nodes'
    
    id = Column(String(100), primary_key=True)
    region_id = Column(String(50), nullable=False, index=True)
    
    # Position
    x_coordinate = Column(Float, nullable=False)
    y_coordinate = Column(Float, nullable=False)
    
    # Leyline properties
    strength = Column(Float, nullable=False, default=1.0)
    element_type = Column(String(50), index=True)
    stability = Column(Float, default=1.0)
    
    # Dynamic properties
    current_flux = Column(Float, default=0.0)
    connected_nodes = Column(ARRAY(String))
    
    # Environmental factors
    environment_data = Column(JSONB)
    
    last_strength_update = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_leyline_region_strength', 'region_id', 'strength'),
        Index('idx_leyline_coordinates', 'x_coordinate', 'y_coordinate'),
        Index('idx_leyline_element', 'element_type'),
    )

class MagicCacheState(Base):
    """
    Table for managing cache invalidation timestamps
    """
    __tablename__ = 'magic_cache_state'
    
    cache_key = Column(String(200), primary_key=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer, default=1)
    
    # For cache dependency tracking
    dependencies = Column(ARRAY(String))

# Materialized view definitions (to be created separately)
MATERIALIZED_VIEWS = {
    'magic_player_stats': """
        CREATE MATERIALIZED VIEW magic_player_stats AS
        SELECT 
            player_id,
            COUNT(*) as total_spells_cast,
            AVG(mana_cost) as avg_mana_cost,
            MAX(created_at) as last_magic_activity,
            COUNT(DISTINCT spell_id) as unique_spells_used,
            AVG(success_rate) as avg_success_rate,
            SUM(CASE WHEN event_type = 'corruption_gain' THEN 1 ELSE 0 END) as corruption_events
        FROM magic_events 
        WHERE event_type IN ('spell_cast', 'ritual_performed', 'corruption_gain')
        GROUP BY player_id;
    """,
    
    'spell_popularity': """
        CREATE MATERIALIZED VIEW spell_popularity AS
        SELECT 
            spell_id,
            COUNT(*) as usage_count,
            AVG(success_rate) as avg_success_rate,
            AVG(mana_cost) as avg_mana_cost,
            COUNT(DISTINCT player_id) as unique_users,
            MAX(created_at) as last_used
        FROM magic_events 
        WHERE event_type = 'spell_cast' AND spell_id IS NOT NULL
        GROUP BY spell_id
        ORDER BY usage_count DESC;
    """,
    
    'leyline_activity': """
        CREATE MATERIALIZED VIEW leyline_activity AS
        SELECT 
            region_id,
            AVG(strength) as avg_strength,
            COUNT(*) as node_count,
            MAX(last_strength_update) as last_update,
            AVG(current_flux) as avg_flux
        FROM leyline_nodes
        GROUP BY region_id;
    """
}

# Partition creation function
def create_monthly_partition(year, month):
    """Create monthly partition for magic_events table"""
    partition_name = f"magic_events_{year}_{month:02d}"
    start_date = f"{year}-{month:02d}-01"
    
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    return f"""
        CREATE TABLE {partition_name} PARTITION OF magic_events
        FOR VALUES FROM ('{start_date}') TO ('{end_date}');
        
        -- Create indexes on partition
        CREATE INDEX idx_{partition_name}_player_type 
        ON {partition_name} (player_id, event_type);
        
        CREATE INDEX idx_{partition_name}_spell 
        ON {partition_name} (spell_id) WHERE spell_id IS NOT NULL;
    """
