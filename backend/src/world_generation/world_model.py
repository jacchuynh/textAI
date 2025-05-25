
"""
World Model - Core data structures for the Procedurally Assisted World System

This module defines the database models and data classes for regions, biomes,
predefined locations, and procedurally generated points of interest.
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from app.db.base import Base


class WorldModel:
    """
    Main world model container holding all world regions and settings.
    This class provides methods for world generation and management.
    """
    
    def __init__(self):
        """Initialize the world model."""
        self.regions = []
        self.settings = {}
        self.version = "1.0.0"
    
    def add_region(self, region):
        """Add a region to the world."""
        self.regions.append(region)
        return region
    
    def get_region(self, region_id):
        """Get a region by ID."""
        for region in self.regions:
            if getattr(region, 'id', None) == region_id:
                return region
        return None
    
    def __str__(self):
        """String representation of the world model."""
        return f"WorldModel(regions={len(self.regions)})"

# Enums for type safety
class BiomeType(str, Enum):
    VERDANT_FRONTIER = "verdant_frontier"
    EMBER_WASTES = "ember_wastes"
    SHIMMERING_MARSHES = "shimmering_marshes"
    CRYSTAL_HIGHLANDS = "crystal_highlands"
    WHISPERING_WOODS = "whispering_woods"
    FROSTBOUND_TUNDRA = "frostbound_tundra"
    CRIMSON_SCARS = "crimson_scars"  # War-torn areas with leyline damage
    RELIC_ZONES = "relic_zones"      # Areas with high concentrations of war relics

class POIType(str, Enum):
    VILLAGE = "village"
    RUIN = "ruin"
    CAVE = "cave"
    DANGEROUS_CAVE = "dangerous_cave"
    SHRINE = "shrine"
    TOWER = "tower"
    BRIDGE = "bridge"
    WAYSTATION = "waystation"
    CAMP = "camp"
    SETTLEMENT = "settlement"
    MINE = "mine"
    GROVE = "grove"
    SPRING = "spring"
    BATTLEFIELD = "battlefield"
    RELIC_SITE = "relic_site"
    FARM = "farm"
    OASIS = "oasis"
    NOMAD_CAMP = "nomad_camp"
    DRUID_ENCLAVE = "druid_enclave"
    CRATER = "crater"

class POIState(str, Enum):
    UNDISCOVERED = "undiscovered"
    DISCOVERED = "discovered"
    EXPLORED = "explored"
    CLEARED = "cleared"
    OCCUPIED = "occupied"
    RUINED = "ruined"
    ABANDONED = "abandoned"

class LocationSize(str, Enum):
    TINY = "tiny"           # 1-5 people
    SMALL = "small"         # 6-25 people
    MEDIUM = "medium"       # 26-100 people
    LARGE = "large"         # 101-500 people
    MAJOR = "major"         # 500+ people

# Database Models
class DBRegion(Base):
    """
    Major geographical regions in the world (e.g., around major cities).
    """
    __tablename__ = "regions"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    
    # Core lore and connections
    core_lore = Column(Text)  # Rich background story
    connected_regions = Column(JSON, default=list)  # List of region IDs
    
    # Regional characteristics
    dominant_races = Column(JSON, default=list)  # Primary races in this region
    political_influence = Column(JSON, default=dict)  # Which cities/factions control areas
    trade_routes = Column(JSON, default=list)  # Major trade connections
    
    # Economic and magical properties
    resource_abundance = Column(JSON, default=dict)  # Available resources
    leyline_strength = Column(Float, default=1.0)
    crimson_corruption = Column(Float, default=0.0)  # Legacy war damage
    
    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    biomes = relationship("DBBiome", back_populates="region")
    predefined_locations = relationship("DBPredefinedLocation", back_populates="region")

class DBBiome(Base):
    """
    Specific environmental zones within regions that define POI generation rules.
    """
    __tablename__ = "biomes"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String, ForeignKey("regions.id"), nullable=False)
    
    name = Column(String, nullable=False)
    biome_type = Column(String, nullable=False)  # BiomeType enum value
    description = Column(Text)
    
    # POI Generation Rules
    poi_density = Column(Float, default=0.5)  # POIs per square kilometer
    allowed_poi_types = Column(JSON, default=list)  # List of POIType enum values
    generation_keywords = Column(JSON, default=list)  # Thematic keywords for generation
    
    # Environmental characteristics
    flora_fauna = Column(JSON, default=list)  # Typical wildlife and plants
    atmospheric_tags = Column(JSON, default=list)  # Mood, weather, magical properties
    hazards = Column(JSON, default=list)  # Environmental dangers
    
    # Resource and magical properties
    available_resources = Column(JSON, default=dict)  # Resource type -> availability chance
    leyline_intensity = Column(Float, default=1.0)
    magical_phenomena = Column(JSON, default=list)  # Unique magical effects
    
    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    region = relationship("DBRegion", back_populates="biomes")
    points_of_interest = relationship("DBPointOfInterest", back_populates="biome")

class DBPredefinedLocation(Base):
    """
    Major cities, landmarks, and important locations that are hand-crafted.
    """
    __tablename__ = "predefined_locations"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String, ForeignKey("regions.id"), nullable=False)
    
    name = Column(String, nullable=False, index=True)
    location_type = Column(String, nullable=False)  # "city", "landmark", "fortress", etc.
    
    # Detailed information
    detailed_lore = Column(Text)
    key_npcs = Column(JSON, default=list)  # Important characters
    available_services = Column(JSON, default=list)  # What players can do here
    
    # Physical properties
    map_coordinates = Column(JSON)  # {"x": float, "y": float} for static map
    size = Column(String, default=LocationSize.MEDIUM.value)
    
    # Connections and accessibility
    connected_locations = Column(JSON, default=list)  # Location IDs
    travel_difficulty = Column(Integer, default=1)  # 1-5 scale
    access_requirements = Column(JSON, default=list)  # Special requirements to enter
    
    # Economic and political
    ruling_faction = Column(String)
    trade_specialties = Column(JSON, default=list)
    economic_wealth = Column(Integer, default=3)  # 1-5 scale
    
    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    region = relationship("DBRegion", back_populates="predefined_locations")

class DBPointOfInterest(Base):
    """
    Procedurally generated locations that can be discovered by players.
    """
    __tablename__ = "points_of_interest"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    biome_id = Column(String, ForeignKey("biomes.id"), nullable=False)
    
    # Basic identification
    poi_type = Column(String, nullable=False)  # POIType enum value
    generated_name = Column(String, nullable=False)
    
    # State and discovery
    current_state = Column(String, default=POIState.UNDISCOVERED.value)
    discovery_difficulty = Column(Integer, default=10)  # DC for finding this POI
    
    # Location and accessibility
    relative_location_tags = Column(JSON, default=list)  # "near_river", "mountain_peak", etc.
    travel_time_from_major = Column(Integer, default=1)  # Days from nearest major location
    
    # Generated content reference
    details_generated = Column(Boolean, default=False)
    generation_seed = Column(String)  # For consistent regeneration
    
    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    discovered_at = Column(DateTime, nullable=True)
    last_visited = Column(DateTime, nullable=True)
    
    # Relationships
    biome = relationship("DBBiome", back_populates="points_of_interest")
    location_details = relationship("DBGeneratedLocationDetails", back_populates="point_of_interest")

class DBGeneratedLocationDetails(Base):
    """
    Detailed, procedurally generated content for a specific POI.
    """
    __tablename__ = "generated_location_details"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    point_of_interest_id = Column(String, ForeignKey("points_of_interest.id"), nullable=False)
    
    # Generated content
    description = Column(Text)  # Rich environmental description
    detailed_features = Column(JSON, default=list)  # Specific notable features
    
    # NPCs and inhabitants
    generated_npcs = Column(JSON, default=list)  # List of NPC data
    local_issues = Column(JSON, default=list)  # Current problems or rumors
    
    # Services and interactions
    available_services = Column(JSON, default=list)  # What players can do here
    unique_items = Column(JSON, default=list)  # Special items or resources
    
    # Hooks and opportunities
    quest_hooks = Column(JSON, default=list)  # Potential adventure starts
    hidden_secrets = Column(JSON, default=list)  # Things to discover
    
    # Economic data
    local_economy = Column(JSON, default=dict)  # Trade goods, prices, etc.
    
    # Generation metadata
    generation_prompt = Column(Text)  # The prompt used to generate this
    generation_timestamp = Column(DateTime, default=datetime.utcnow)
    last_refreshed = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    point_of_interest = relationship("DBPointOfInterest", back_populates="location_details")

# Pydantic Models for API
class RegionData(BaseModel):
    """Pydantic model for Region data transfer."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    core_lore: Optional[str] = None
    connected_regions: List[str] = Field(default_factory=list)
    dominant_races: List[str] = Field(default_factory=list)
    political_influence: Dict[str, Any] = Field(default_factory=dict)
    trade_routes: List[str] = Field(default_factory=list)
    resource_abundance: Dict[str, float] = Field(default_factory=dict)
    leyline_strength: float = 1.0
    crimson_corruption: float = 0.0

class BiomeData(BaseModel):
    """Pydantic model for Biome data transfer."""
    id: Optional[str] = None
    region_id: str
    name: str
    biome_type: BiomeType
    description: Optional[str] = None
    poi_density: float = 0.5
    allowed_poi_types: List[POIType] = Field(default_factory=list)
    generation_keywords: List[str] = Field(default_factory=list)
    flora_fauna: List[str] = Field(default_factory=list)
    atmospheric_tags: List[str] = Field(default_factory=list)
    hazards: List[str] = Field(default_factory=list)
    available_resources: Dict[str, float] = Field(default_factory=dict)
    leyline_intensity: float = 1.0
    magical_phenomena: List[str] = Field(default_factory=list)

class PredefinedLocationData(BaseModel):
    """Pydantic model for PredefinedLocation data transfer."""
    id: Optional[str] = None
    region_id: str
    name: str
    location_type: str
    detailed_lore: Optional[str] = None
    key_npcs: List[Dict[str, Any]] = Field(default_factory=list)
    available_services: List[str] = Field(default_factory=list)
    map_coordinates: Optional[Dict[str, float]] = None
    size: LocationSize = LocationSize.MEDIUM
    connected_locations: List[str] = Field(default_factory=list)
    travel_difficulty: int = 1
    access_requirements: List[str] = Field(default_factory=list)
    ruling_faction: Optional[str] = None
    trade_specialties: List[str] = Field(default_factory=list)
    economic_wealth: int = 3

class PointOfInterestData(BaseModel):
    """Pydantic model for PointOfInterest data transfer."""
    id: Optional[str] = None
    biome_id: str
    poi_type: POIType
    generated_name: str
    current_state: POIState = POIState.UNDISCOVERED
    discovery_difficulty: int = 10
    relative_location_tags: List[str] = Field(default_factory=list)
    travel_time_from_major: int = 1
    details_generated: bool = False
    generation_seed: Optional[str] = None

class GeneratedLocationDetailsData(BaseModel):
    """Pydantic model for GeneratedLocationDetails data transfer."""
    id: Optional[str] = None
    point_of_interest_id: str
    description: Optional[str] = None
    detailed_features: List[str] = Field(default_factory=list)
    generated_npcs: List[Dict[str, Any]] = Field(default_factory=list)
    local_issues: List[str] = Field(default_factory=list)
    available_services: List[str] = Field(default_factory=list)
    unique_items: List[Dict[str, Any]] = Field(default_factory=list)
    quest_hooks: List[str] = Field(default_factory=list)
    hidden_secrets: List[str] = Field(default_factory=list)
    local_economy: Dict[str, Any] = Field(default_factory=dict)
    generation_prompt: Optional[str] = None

# World Constants based on your lore
MAJOR_CITIES = {
    "skarport": {
        "name": "Skarport",
        "region": "central_accord",
        "description": "The Harmonized Capital - diplomatic heart of the Crimson Accord",
        "government": "Rotating council with Accord-neutral moderator",
        "dominant_races": ["human", "mixed"],
        "specialties": ["diplomacy", "trade", "magical_archives"]
    },
    "stonewake": {
        "name": "Stonewake", 
        "region": "industrial_caldera",
        "description": "The Industrial Heart - forge-city built into a massive caldera",
        "government": "Forgeguild Master chosen by guilds and labor syndicate",
        "dominant_races": ["dwarf", "orc", "human"],
        "specialties": ["industry", "weapons", "enchanted_tools"]
    },
    "lethandrel": {
        "name": "Lethandrel",
        "region": "verdant_archive",
        "description": "The Living Archive - elven city preserving magical knowledge",
        "government": "Arcane council elects Voice of the Grove",
        "dominant_races": ["elf", "ferverl"],
        "specialties": ["magic", "knowledge", "botanical_alchemy"]
    },
    "rivemark": {
        "name": "Rivemark",
        "region": "grainward_delta",
        "description": "The Grainward Bastion - agricultural fortress city",
        "government": "Elected Marshal from military and agricultural unions",
        "dominant_races": ["human", "orc", "ferverl"],
        "specialties": ["agriculture", "military", "logistics"]
    },
    "ashkar_vale": {
        "name": "Ashkar Vale",
        "region": "wild_frontier",
        "description": "The Wild Front - beastfolk city on the edge of magic-scarred lands",
        "government": "Tribal Chieftain chosen via blood rite and shaman consensus",
        "dominant_races": ["beastfolk", "ferverl"],
        "specialties": ["monster_hunting", "spirit_totems", "relic_salvage"]
    },
    "crucible_spire": {
        "name": "Crucible Spire",
        "region": "broken_leylines",
        "description": "The Broken Beacon - vertical city built on collapsed leyline rift",
        "government": "No central ruler - rival houses influence shifting Speaker",
        "dominant_races": ["ferverl", "human", "elf_outcasts"],
        "specialties": ["relic_trade", "magical_research", "black_market"]
    },
    "thal_zirad": {
        "name": "Thal-Zirad",
        "region": "sacred_desert",
        "description": "The Jewel of Dust - desert theocracy built around sacred springs",
        "government": "Ritual-selected Oracle backed by caste houses",
        "dominant_races": ["human", "ferverl"],
        "specialties": ["ritual_crafting", "divine_magic", "glassworking"]
    }
}

RACIAL_CHARACTERISTICS = {
    "human": {
        "traits": ["adaptable", "diplomatic", "ambitious"],
        "economic_focus": ["trade", "administration", "cross_racial_commerce"],
        "preferred_locations": ["cities", "trade_hubs", "diverse_settlements"]
    },
    "elf": {
        "traits": ["patient", "traditional", "magical"],
        "economic_focus": ["magical_agriculture", "arcane_research", "artisan_crafts"],
        "preferred_locations": ["forests", "magical_sites", "ancient_places"]
    },
    "dwarf": {
        "traits": ["traditional", "craftsmanship", "industrious"],
        "economic_focus": ["heavy_industry", "mining", "relic_containment"],
        "preferred_locations": ["mountains", "underground", "forge_cities"]
    },
    "beastfolk": {
        "traits": ["instinctual", "communal", "spiritual"],
        "economic_focus": ["monster_hunting", "spiritual_trade", "wilderness_guiding"],
        "preferred_locations": ["wild_places", "clan_territories", "frontier_settlements"]
    },
    "orc": {
        "traits": ["disciplined", "redemptive", "strong"],
        "economic_focus": ["construction", "security", "heavy_labor"],
        "preferred_locations": ["industrial_cities", "fortress_towns", "work_sites"]
    },
    "ferverl": {
        "traits": ["adaptive", "resilient", "ritual_focused"],
        "economic_focus": ["mana_crafts", "purification", "survivalist_trades"],
        "preferred_locations": ["desert_cities", "war_scarred_areas", "magical_sites"]
    }
}

def get_biome_generation_rules(biome_type: BiomeType) -> Dict[str, Any]:
    """
    Get POI generation rules for a specific biome type based on world lore.
    """
    rules = {
        BiomeType.VERDANT_FRONTIER: {
            "poi_types": [POIType.VILLAGE, POIType.WAYSTATION, POIType.FARM, POIType.GROVE],
            "density": 0.6,
            "keywords": ["pastoral", "fertile", "trade_route", "agricultural"],
            "resources": {"grain": 0.8, "livestock": 0.7, "herbs": 0.5},
            "hazards": ["bandits", "magical_anomalies"],
            "atmosphere": ["peaceful", "productive", "growing"]
        },
        BiomeType.EMBER_WASTES: {
            "poi_types": [POIType.MINE, POIType.OASIS, POIType.NOMAD_CAMP, POIType.RELIC_SITE],
            "density": 0.3,
            "keywords": ["arid", "harsh", "mineral_rich", "survival"],
            "resources": {"minerals": 0.8, "rare_metals": 0.4, "water": 0.2},
            "hazards": ["heat_exhaustion", "sandstorms", "territorial_disputes"],
            "atmosphere": ["harsh", "unforgiving", "mineral_rich"]
        },
        BiomeType.WHISPERING_WOODS: {
            "poi_types": [POIType.GROVE, POIType.SHRINE, POIType.RUIN, POIType.DRUID_ENCLAVE],
            "density": 0.7,
            "keywords": ["ancient", "magical", "mysterious", "druidic"],
            "resources": {"magical_herbs": 0.9, "timber": 0.8, "enchanted_materials": 0.3},
            "hazards": ["wild_magic", "guardian_spirits", "treacherous_paths"],
            "atmosphere": ["mystical", "ancient", "alive_with_magic"]
        },
        BiomeType.CRIMSON_SCARS: {
            "poi_types": [POIType.RUIN, POIType.BATTLEFIELD, POIType.RELIC_SITE, POIType.CRATER],
            "density": 0.4,
            "keywords": ["war_torn", "corrupted", "dangerous", "relic_rich"],
            "resources": {"war_relics": 0.8, "corrupted_crystals": 0.6, "cursed_metals": 0.4},
            "hazards": ["leyline_instability", "relic_corruption", "war_spirits"],
            "atmosphere": ["haunted", "dangerous", "scarred_by_war"]
        }
    }
    
    return rules.get(biome_type, {
        "poi_types": [POIType.VILLAGE, POIType.RUIN],
        "density": 0.5,
        "keywords": ["generic", "unremarkable"],
        "resources": {},
        "hazards": [],
        "atmosphere": ["mundane"]
    })
