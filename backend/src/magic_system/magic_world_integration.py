"""
Magic World Integration Module

This module integrates the magic system with the world generation system,
allowing for the creation of magical features such as leylines, magic-infused
locations, and magical points of interest.
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union
import random
import math
import uuid
from enum import Enum, auto

# Import the core magic system
from game_engine.magic_system import (
    MagicSystem, MagicUser, MagicEffect, Domain, DamageType,
    EffectType, MagicTier, ManaFluxLevel, LocationMagicProfile
)


class World:
    """
    Represents a game world containing multiple locations.
    """
    def __init__(
        self,
        id: str,
        name: str,
        width: int,
        height: int,
        locations: Dict[str, 'Location'],
        climate: 'Climate'
    ):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.locations = locations
        self.climate = climate
        self.leylines = []  # List of leyline paths as list of location_ids
        self.magical_hotspots = []  # List of location_ids with high magical activity
        self.world_events = []  # List of global magical events


class Climate(Enum):
    """Climate types for world regions."""
    TEMPERATE = auto()
    TROPICAL = auto()
    ARID = auto()
    ARCTIC = auto()


class Terrain(Enum):
    """Terrain types for locations."""
    FLAT = auto()
    HILLS = auto()
    MOUNTAINS = auto()
    COASTAL = auto()
    RIVER = auto()


class POI:
    """
    Represents a Point of Interest in a location.
    """
    def __init__(
        self,
        id: str,
        name: str,
        poi_type: 'POIType',
        description: str,
        coordinates: Tuple[float, float]
    ):
        self.id = id
        self.name = name
        self.poi_type = poi_type
        self.description = description
        self.coordinates = coordinates
        self.properties = {}  # Additional properties
        self.is_magical = False
        self.magical_properties = {}


class POIType(Enum):
    """Types of Points of Interest."""
    VILLAGE = auto()
    RUIN = auto()
    CAVE = auto()
    SHRINE = auto()
    TOWER = auto()
    BRIDGE = auto()
    CAMP = auto()
    SETTLEMENT = auto()
    MINE = auto()
    GROVE = auto()
    SPRING = auto()
    RELIC_SITE = auto()
    FARM = auto()
    # Magical POI types
    LEYLINE_NODE = auto()
    ARCANE_FONT = auto()
    ELEMENTAL_WELL = auto()
    RITUAL_CIRCLE = auto()
    WILD_MAGIC_ZONE = auto()
    MANA_CRYSTAL_FORMATION = auto()
    DIMENSIONAL_TEAR = auto()


class Location:
    """
    Represents a location in the game world.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        coordinates: Tuple[int, int],
        terrain: Terrain,
        pois: List[POI],
        biome: str
    ):
        self.id = id
        self.name = name
        self.description = description
        self.coordinates = coordinates
        self.terrain = terrain
        self.pois = pois
        self.biome = biome
        self.magic_profile = None  # Will be set by MagicWorldIntegration
        self.adjacent_locations = []  # Location IDs


class MagicWorldIntegration:
    """
    Integrates the magic system with world generation.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
        self.poi_counter = 0
        self.magical_hotspots = []
        
        # Maps terrain types to their natural magic affinity
        self.terrain_magic_affinity = {
            Terrain.FLAT: [Domain.NATURAL, Domain.ELEMENTAL],
            Terrain.HILLS: [Domain.NATURAL, Domain.EARTH],
            Terrain.MOUNTAINS: [Domain.ELEMENTAL, Domain.ARCANE],
            Terrain.COASTAL: [Domain.WATER, Domain.NATURAL],
            Terrain.RIVER: [Domain.WATER, Domain.NATURAL]
        }
        
        # Maps biome to dominant magic aspects
        self.biome_magic_affinity = {
            "forest": [Domain.NATURAL, Domain.SPIRIT],
            "desert": [Domain.ELEMENTAL, Domain.FIRE],
            "tundra": [Domain.ELEMENTAL, Domain.ICE],
            "swamp": [Domain.NATURAL, Domain.WATER, Domain.DEATH],
            "grassland": [Domain.NATURAL, Domain.AIR],
            "mountain": [Domain.ELEMENTAL, Domain.EARTH],
            "volcanic": [Domain.ELEMENTAL, Domain.FIRE, Domain.EARTH],
            "coastal": [Domain.WATER, Domain.AIR],
            "urban": [Domain.ARCANE, Domain.MIND],
            "ruins": [Domain.ARCANE, Domain.SHADOW, Domain.TEMPORAL],
            "mystical": [Domain.ARCANE, Domain.SPIRIT, Domain.VOID]
        }
    
    def enhance_world_with_magic(self, world: World) -> World:
        """
        Enhance a world with magical features.
        
        Args:
            world: The world to enhance
            
        Returns:
            The enhanced world
        """
        # Add magic profiles to all locations
        for location_id, location in world.locations.items():
            self._add_magic_profile(location)
        
        # Create a network of leylines
        self._create_leyline_network(world)
        
        # Create magical hotspots at leyline intersections
        self._create_magical_hotspots(world)
        
        # Add magical POIs to locations based on their magic profile
        for location in world.locations.values():
            self._add_magical_pois(location)
        
        # Register all location magic profiles with the magic system
        if self.magic_system:
            for location in world.locations.values():
                if location.magic_profile:
                    self.magic_system.register_location_profile(location.magic_profile)
        
        return world
    
    def _add_magic_profile(self, location: Location) -> None:
        """Add a magic profile to a location based on its biome."""
        # Determine leyline strength based on terrain
        base_leyline_strength = 0.1  # Default value
        if location.terrain == Terrain.MOUNTAINS:
            base_leyline_strength = 0.4
        elif location.terrain == Terrain.HILLS:
            base_leyline_strength = 0.25
        elif location.terrain == Terrain.RIVER:
            base_leyline_strength = 0.3
        
        # Add some randomness
        leyline_strength = min(1.0, base_leyline_strength + random.uniform(-0.1, 0.2))
        
        # Determine mana flux level based on biome and randomness
        mana_flux_options = list(ManaFluxLevel)
        biome_flux_weights = {
            "mystical": [0.05, 0.1, 0.2, 0.3, 0.35],  # Bias towards higher flux
            "ruins": [0.1, 0.2, 0.3, 0.3, 0.1],
            "volcanic": [0.1, 0.15, 0.25, 0.3, 0.2],
            "forest": [0.1, 0.2, 0.4, 0.2, 0.1],
            "desert": [0.3, 0.3, 0.2, 0.15, 0.05],
            "tundra": [0.25, 0.3, 0.25, 0.15, 0.05],
            "swamp": [0.1, 0.15, 0.3, 0.3, 0.15],
            "mountain": [0.1, 0.2, 0.3, 0.25, 0.15],
            "urban": [0.2, 0.3, 0.3, 0.15, 0.05]
        }
        
        weights = biome_flux_weights.get(location.biome, [0.2, 0.3, 0.3, 0.15, 0.05])
        mana_flux_level = random.choices(mana_flux_options, weights=weights, k=1)[0]
        
        # Determine dominant magic aspects based on biome and terrain
        dominant_magic_aspects = []
        
        # Add aspects from terrain
        if location.terrain in self.terrain_magic_affinity:
            terrain_aspects = self.terrain_magic_affinity[location.terrain]
            dominant_magic_aspects.extend(terrain_aspects)
        
        # Add aspects from biome
        if location.biome in self.biome_magic_affinity:
            biome_aspects = self.biome_magic_affinity[location.biome]
            dominant_magic_aspects.extend(biome_aspects)
        
        # Remove duplicates while preserving order
        seen = set()
        dominant_magic_aspects = [x for x in dominant_magic_aspects if not (x in seen or seen.add(x))]
        
        # Determine if the location allows ritual sites
        allows_ritual_sites = True
        if "urban" in location.biome or random.random() < 0.2:
            allows_ritual_sites = False
        
        # Create magic profile
        location.magic_profile = LocationMagicProfile(
            location_id=location.id,
            leyline_strength=leyline_strength,
            mana_flux_level=mana_flux_level,
            dominant_magic_aspects=dominant_magic_aspects,
            allows_ritual_sites=allows_ritual_sites
        )
    
    def _create_leyline_network(self, world: World) -> None:
        """Create a network of leylines connecting locations."""
        # First, identify locations with significant leyline strength
        leyline_nodes = []
        for location_id, location in world.locations.items():
            if location.magic_profile and location.magic_profile.leyline_strength > 0.3:
                leyline_nodes.append(location_id)
        
        # Ensure we have enough nodes for a network
        if len(leyline_nodes) < 3:
            # Add random locations to ensure a minimal network
            additional_needed = 3 - len(leyline_nodes)
            available_locations = [loc_id for loc_id in world.locations.keys() if loc_id not in leyline_nodes]
            
            if available_locations:
                random_additions = random.sample(available_locations, min(additional_needed, len(available_locations)))
                leyline_nodes.extend(random_additions)
        
        # Create leylines connecting nearby nodes
        leylines = []
        for i, node1 in enumerate(leyline_nodes):
            location1 = world.locations[node1]
            
            # Find the closest 1-3 other nodes to connect to
            distances = []
            for j, node2 in enumerate(leyline_nodes):
                if i != j:
                    location2 = world.locations[node2]
                    distance = math.sqrt(
                        (location1.coordinates[0] - location2.coordinates[0]) ** 2 +
                        (location1.coordinates[1] - location2.coordinates[1]) ** 2
                    )
                    distances.append((node2, distance))
            
            # Sort by distance and take the closest 1-3
            distances.sort(key=lambda x: x[1])
            num_connections = min(random.randint(1, 3), len(distances))
            
            for k in range(num_connections):
                if k < len(distances):
                    leyline = sorted([node1, distances[k][0]])  # Sort to avoid duplicates
                    leyline_key = f"{leyline[0]}-{leyline[1]}"
                    
                    # Only add if not already present
                    if leyline not in leylines:
                        leylines.append(leyline)
        
        # Store the leylines in the world
        world.leylines = leylines
    
    def _create_magical_hotspots(self, world: World) -> None:
        """Create magical hotspots at leyline intersections."""
        # Count how many leylines each location is part of
        leyline_counts = {}
        for leyline in world.leylines:
            for location_id in leyline:
                if location_id not in leyline_counts:
                    leyline_counts[location_id] = 0
                leyline_counts[location_id] += 1
        
        # Locations with 2+ leylines are hotspots
        hotspots = []
        for location_id, count in leyline_counts.items():
            if count >= 2:
                hotspots.append(location_id)
                
                # Enhance the location's magic profile to reflect hotspot status
                location = world.locations[location_id]
                if location.magic_profile:
                    # Increase leyline strength
                    location.magic_profile.leyline_strength = min(1.0, location.magic_profile.leyline_strength * 1.5)
                    
                    # Increase mana flux level if not already at max
                    flux_levels = list(ManaFluxLevel)
                    current_index = flux_levels.index(location.magic_profile.mana_flux_level)
                    if current_index < len(flux_levels) - 1:
                        location.magic_profile.mana_flux_level = flux_levels[current_index + 1]
        
        # Store hotspots in the world and in this instance
        world.magical_hotspots = hotspots
        self.magical_hotspots = hotspots
    
    def _add_magical_pois(self, location: Location) -> None:
        """Add magical POIs to a location based on its magic profile."""
        if not location.magic_profile:
            return
        
        # Determine how many magical POIs to add based on location's magic
        profile = location.magic_profile
        max_pois = 1
        
        # More POIs for stronger magical locations
        if profile.leyline_strength > 0.6:
            max_pois += 1
        
        # More POIs for higher mana flux
        if profile.mana_flux_level in (ManaFluxLevel.HIGH, ManaFluxLevel.VERY_HIGH):
            max_pois += 1
        
        # Extra POI for hotspots
        if location.id in self.magical_hotspots:
            max_pois += 1
        
        # Randomize the actual number
        num_pois = random.randint(0, max_pois)
        
        # Add the magical POIs
        for _ in range(num_pois):
            # Choose a random dominant magic aspect
            if profile.dominant_magic_aspects:
                aspect = random.choice(profile.dominant_magic_aspects)
            else:
                aspect = random.choice(list(Domain))
            
            # Determine POI type based on the aspect and location
            magical_poi_types = self._get_aspect_poi_types(aspect, location)
            poi_type = random.choice(magical_poi_types)
            
            # Generate POI details
            poi_details = self._generate_magical_poi_details(poi_type, aspect, location.biome)
            
            # Create the POI
            poi = POI(
                id=f"poi_{self.poi_counter}",
                name=poi_details["name"],
                poi_type=poi_type,
                description=poi_details["description"],
                coordinates=(
                    random.uniform(0, 1),  # x-coordinate within location
                    random.uniform(0, 1)   # y-coordinate within location
                )
            )
            self.poi_counter += 1
            
            # Mark as magical and add magical properties
            poi.is_magical = True
            poi.magical_properties = {
                "aspect": aspect.name,
                "power_level": poi_details["power_level"],
                "effects": poi_details["effects"]
            }
            
            # Add to location's POIs
            location.pois.append(poi)
    
    def _get_aspect_poi_types(self, aspect: Domain, location: Location) -> List[POIType]:
        """Get appropriate POI types for a given magical aspect and location."""
        aspect_poi_mapping = {
            Domain.ARCANE: [POIType.ARCANE_FONT, POIType.RITUAL_CIRCLE, POIType.DIMENSIONAL_TEAR],
            Domain.ELEMENTAL: [POIType.ELEMENTAL_WELL, POIType.MANA_CRYSTAL_FORMATION],
            Domain.NATURAL: [POIType.GROVE, POIType.SPRING, POIType.ELEMENTAL_WELL],
            Domain.DIVINE: [POIType.SHRINE, POIType.RITUAL_CIRCLE],
            Domain.SHADOW: [POIType.CAVE, POIType.RUIN, POIType.DIMENSIONAL_TEAR],
            Domain.BLOOD: [POIType.RITUAL_CIRCLE, POIType.RUIN],
            Domain.MIND: [POIType.TOWER, POIType.ARCANE_FONT],
            Domain.SPIRIT: [POIType.SHRINE, POIType.GROVE],
            Domain.CHAOS: [POIType.WILD_MAGIC_ZONE, POIType.DIMENSIONAL_TEAR],
            Domain.ORDER: [POIType.TOWER, POIType.RITUAL_CIRCLE],
            Domain.VOID: [POIType.DIMENSIONAL_TEAR, POIType.WILD_MAGIC_ZONE],
            Domain.TEMPORAL: [POIType.DIMENSIONAL_TEAR, POIType.ARCANE_FONT]
        }
        
        # All aspects can have leyline nodes if the location is a hotspot
        if location.id in self.magical_hotspots:
            for domain_types in aspect_poi_mapping.values():
                if POIType.LEYLINE_NODE not in domain_types:
                    domain_types.append(POIType.LEYLINE_NODE)
        
        return aspect_poi_mapping.get(aspect, [POIType.WILD_MAGIC_ZONE])
    
    def _generate_magical_poi_details(self, poi_type: POIType, aspect: Domain, biome: str) -> Dict[str, Any]:
        """Generate a name and description for a magical POI."""
        # Templates for names
        name_templates = {
            POIType.ARCANE_FONT: [
                "The {aspect} Font", 
                "{aspect}'s Wellspring", 
                "Font of {aspect} Energies"
            ],
            POIType.ELEMENTAL_WELL: [
                "{aspect} Well", 
                "The {element} Spring", 
                "Elemental Confluence"
            ],
            POIType.RITUAL_CIRCLE: [
                "Ancient {aspect} Circle", 
                "The {aspect} Ritual Grounds", 
                "Circle of {aspect} Binding"
            ],
            POIType.WILD_MAGIC_ZONE: [
                "The Unstable {aspect} Zone", 
                "Chaotic {aspect} Field", 
                "Wild {aspect} Nexus"
            ],
            POIType.MANA_CRYSTAL_FORMATION: [
                "{aspect} Crystal Cluster", 
                "The {aspect} Crystalline Formation", 
                "Mana Crystals of {aspect}"
            ],
            POIType.DIMENSIONAL_TEAR: [
                "{aspect} Dimensional Rift", 
                "Tear in the {aspect} Veil", 
                "The {aspect} Fracture"
            ],
            POIType.LEYLINE_NODE: [
                "The {aspect} Leyline Nexus", 
                "Confluence of {aspect} Leylines", 
                "The {aspect} Node"
            ]
        }
        
        # Templates for descriptions
        description_templates = {
            POIType.ARCANE_FONT: [
                "A bubbling font of pure {aspect} energy, casting a {color} glow over the surrounding {biome}.",
                "Streams of {aspect} magic flow from this ancient font, empowering those who know how to tap into it.",
                "An ornate magical font where {aspect} energy wells up from deep beneath the earth."
            ],
            POIType.ELEMENTAL_WELL: [
                "A deep well where pure elemental {element} can be drawn from the earth.",
                "Elemental {element} energies swirl visibly around this natural formation.",
                "A sacred well of {element} power, said to have been created in the earliest days of creation."
            ],
            POIType.RITUAL_CIRCLE: [
                "Ancient stones arranged in a perfect circle, etched with {aspect} runes that still pulse with power.",
                "A ritual site where {aspect} magic can be channeled with greater ease and precision.",
                "The ground within this circle seems to amplify {aspect} energies, making it ideal for complex magical workings."
            ],
            POIType.WILD_MAGIC_ZONE: [
                "An area where magic behaves unpredictably. {color} energy crackles through the air at random intervals.",
                "Reality itself seems thin here, with {aspect} energies manifesting in chaotic and unpredictable ways.",
                "A dangerous zone where wild {aspect} magic fluctuates and surges without warning."
            ],
            POIType.MANA_CRYSTAL_FORMATION: [
                "Beautiful crystals that resonate with {aspect} energies jut from the ground, storing vast amounts of magical power.",
                "A stunning formation of {color} crystals that naturally accumulate and store {aspect} mana.",
                "These crystalline structures have formed over centuries, concentrating {aspect} energy from the surrounding area."
            ],
            POIType.DIMENSIONAL_TEAR: [
                "A rip in reality where the boundaries between worlds have grown thin. {aspect} energies from beyond seep through.",
                "A shimmering tear in space, through which glimpses of other realms infused with {aspect} energy can be seen.",
                "This unstable rift pulses with {aspect} power, occasionally allowing things to pass between dimensions."
            ],
            POIType.LEYLINE_NODE: [
                "A major confluence of leylines, where multiple streams of {aspect} magical energy intersect and amplify each other.",
                "A powerful nexus where several leylines meet, creating a reservoir of {aspect} magical energy.",
                "The ground here thrums with the power of multiple leylines rich in {aspect} energy."
            ]
        }
        
        # Map aspects to elements and colors
        element_mapping = {
            Domain.ARCANE: "arcane",
            Domain.ELEMENTAL: "primal",
            Domain.NATURAL: "natural",
            Domain.DIVINE: "divine",
            Domain.SHADOW: "shadow",
            Domain.BLOOD: "blood",
            Domain.MIND: "mental",
            Domain.SPIRIT: "spiritual",
            Domain.CHAOS: "chaotic",
            Domain.ORDER: "ordered",
            Domain.VOID: "void",
            Domain.TEMPORAL: "temporal"
        }
        
        color_mapping = {
            Domain.ARCANE: "purple",
            Domain.ELEMENTAL: "multi-colored",
            Domain.NATURAL: "green",
            Domain.DIVINE: "golden",
            Domain.SHADOW: "black",
            Domain.BLOOD: "crimson",
            Domain.MIND: "blue",
            Domain.SPIRIT: "white",
            Domain.CHAOS: "swirling multi-hued",
            Domain.ORDER: "crystalline",
            Domain.VOID: "pitch-black",
            Domain.TEMPORAL: "shifting"
        }
        
        # Generate effects based on POI type and aspect
        effects = self._generate_poi_effects(poi_type, aspect)
        
        # Calculate power level
        power_level = random.uniform(0.3, 0.8)
        if poi_type == POIType.LEYLINE_NODE:
            power_level += 0.2
        
        # Select templates
        name_template = random.choice(name_templates.get(poi_type, ["Magical {aspect} Site"]))
        desc_template = random.choice(description_templates.get(poi_type, ["A site of {aspect} magical energy."]))
        
        # Fill in the templates
        aspect_name = aspect.name.capitalize()
        element = element_mapping.get(aspect, "magical")
        color = color_mapping.get(aspect, "magical")
        
        name = name_template.format(aspect=aspect_name, element=element, color=color)
        description = desc_template.format(
            aspect=aspect_name.lower(), 
            element=element, 
            color=color, 
            biome=biome
        )
        
        return {
            "name": name,
            "description": description,
            "power_level": power_level,
            "effects": effects
        }
    
    def _generate_poi_effects(self, poi_type: POIType, aspect: Domain) -> List[str]:
        """Generate magical effects for a POI based on its type and aspect."""
        effects = []
        
        if poi_type == POIType.ARCANE_FONT:
            effects.append(f"Doubles mana regeneration rate for {aspect.name.lower()} spells")
            effects.append(f"Allows one extra {aspect.name.lower()} spell to be prepared")
        
        elif poi_type == POIType.ELEMENTAL_WELL:
            damage_types = DamageType.get_domain_affinities().get(aspect, [])
            if damage_types:
                damage_type = damage_types[0].name.lower()
                effects.append(f"Enhances {damage_type} damage spells by 25%")
            effects.append("Provides elemental materials for crafting")
        
        elif poi_type == POIType.RITUAL_CIRCLE:
            effects.append("Reduces ritual casting time by 50%")
            effects.append("Increases ritual success chance by 20%")
            effects.append(f"Enhances {aspect.name.lower()} ritual effects")
        
        elif poi_type == POIType.WILD_MAGIC_ZONE:
            effects.append("Spells cast here have unpredictable effects")
            effects.append("10% chance for spells to be empowered or have unintended effects")
            effects.append("Magical research conducted here yields unusual results")
        
        elif poi_type == POIType.MANA_CRYSTAL_FORMATION:
            effects.append("Can be mined for magical crafting materials")
            effects.append("Standing nearby slowly restores mana")
            effects.append("Crystals can be used to store spell energy")
        
        elif poi_type == POIType.DIMENSIONAL_TEAR:
            effects.append("Occasional spawning of extra-dimensional entities")
            effects.append("Can be used for faster travel between known locations")
            effects.append("May yield rare magical components from other realms")
        
        elif poi_type == POIType.LEYLINE_NODE:
            effects.append("Significantly boosts all magical effects in the area")
            effects.append("Allows drawing of raw magical energy")
            effects.append("Can be used to enhance enchantment processes")
        
        return effects
    
    def get_magical_hotspots(self) -> List[str]:
        """Get the list of magical hotspot location IDs."""
        return self.magical_hotspots
    
    def get_location_magic_affinity(self, location: Location, domain: Domain) -> float:
        """
        Calculate how well a location resonates with a specific magical domain.
        Returns a value from 0.0 to 2.0, where higher values indicate stronger affinity.
        """
        if not location.magic_profile:
            return 1.0  # Neutral affinity
        
        affinity = 1.0  # Start with neutral
        
        # Check if domain is among the location's dominant aspects
        if domain in location.magic_profile.dominant_magic_aspects:
            affinity += 0.5
            
            # Extra bonus if it's the primary aspect (first in the list)
            if location.magic_profile.dominant_magic_aspects and location.magic_profile.dominant_magic_aspects[0] == domain:
                affinity += 0.2
        
        # Check for opposing domains
        opposing_domain = Domain.get_opposing_domains().get(domain)
        if opposing_domain and opposing_domain in location.magic_profile.dominant_magic_aspects:
            affinity -= 0.4
        
        # Adjust based on leyline strength
        affinity += location.magic_profile.leyline_strength * 0.3
        
        # Adjust based on mana flux
        flux_modifier = {
            ManaFluxLevel.VERY_LOW: -0.2,
            ManaFluxLevel.LOW: -0.1,
            ManaFluxLevel.MEDIUM: 0.0,
            ManaFluxLevel.HIGH: 0.1,
            ManaFluxLevel.VERY_HIGH: 0.2
        }
        affinity += flux_modifier.get(location.magic_profile.mana_flux_level, 0.0)
        
        # Ensure affinity stays in reasonable range
        return max(0.1, min(2.0, affinity))
    
    def find_closest_leyline(self, coordinates: Tuple[int, int], world: World) -> Optional[List[str]]:
        """
        Find the closest leyline to the given coordinates.
        Returns the leyline as a list of location IDs, or None if no leylines exist.
        """
        if not world.leylines:
            return None
        
        closest_leyline = None
        min_distance = float('inf')
        
        for leyline in world.leylines:
            # Calculate the average distance to all locations in the leyline
            total_distance = 0
            for location_id in leyline:
                location = world.locations[location_id]
                distance = math.sqrt(
                    (coordinates[0] - location.coordinates[0]) ** 2 +
                    (coordinates[1] - location.coordinates[1]) ** 2
                )
                total_distance += distance
            
            avg_distance = total_distance / len(leyline)
            
            if avg_distance < min_distance:
                min_distance = avg_distance
                closest_leyline = leyline
        
        return closest_leyline
    
    def get_magical_resource_locations(self, resource_type: str, world: World) -> List[str]:
        """
        Find locations where a specific magical resource can be found.
        
        Args:
            resource_type: The type of resource to look for
            world: The world to search in
            
        Returns:
            A list of location IDs where the resource can be found
        """
        resource_locations = []
        
        # Map resource types to domains and POI types that might contain them
        resource_domain_mapping = {
            "mana_crystal": [Domain.ARCANE, Domain.ELEMENTAL],
            "elemental_essence": [Domain.ELEMENTAL],
            "spirit_essence": [Domain.SPIRIT, Domain.NATURAL],
            "void_fragment": [Domain.VOID, Domain.SHADOW],
            "time_dust": [Domain.TEMPORAL, Domain.ARCANE],
            "divine_light": [Domain.DIVINE],
            "shadow_residue": [Domain.SHADOW],
            "chaos_shard": [Domain.CHAOS],
            "order_matrix": [Domain.ORDER],
            "blood_essence": [Domain.BLOOD],
            "mind_crystal": [Domain.MIND]
        }
        
        resource_poi_mapping = {
            "mana_crystal": [POIType.MANA_CRYSTAL_FORMATION, POIType.ARCANE_FONT],
            "elemental_essence": [POIType.ELEMENTAL_WELL],
            "spirit_essence": [POIType.GROVE, POIType.SHRINE],
            "void_fragment": [POIType.DIMENSIONAL_TEAR],
            "time_dust": [POIType.DIMENSIONAL_TEAR, POIType.ARCANE_FONT],
            "divine_light": [POIType.SHRINE],
            "shadow_residue": [POIType.CAVE, POIType.RUIN],
            "chaos_shard": [POIType.WILD_MAGIC_ZONE],
            "order_matrix": [POIType.RITUAL_CIRCLE, POIType.TOWER],
            "blood_essence": [POIType.RITUAL_CIRCLE],
            "mind_crystal": [POIType.TOWER, POIType.ARCANE_FONT]
        }
        
        related_domains = resource_domain_mapping.get(resource_type, [])
        related_poi_types = resource_poi_mapping.get(resource_type, [])
        
        for location_id, location in world.locations.items():
            # Check if location has relevant magical profile
            if location.magic_profile:
                domain_match = any(domain in location.magic_profile.dominant_magic_aspects for domain in related_domains)
                
                # Check if location has relevant POIs
                poi_match = False
                for poi in location.pois:
                    if poi.is_magical and poi.poi_type in related_poi_types:
                        poi_match = True
                        break
                
                # Hotspots are more likely to have any resource
                hotspot_bonus = location_id in self.magical_hotspots
                
                # Add location if it matches domain or POI criteria, or is a hotspot with some probability
                if domain_match or poi_match or (hotspot_bonus and random.random() < 0.7):
                    resource_locations.append(location_id)
        
        return resource_locations


class MagicalMaterialWorldIntegration:
    """
    Integrates magical materials with the world generation system.
    """
    def __init__(self, magic_integration: MagicWorldIntegration):
        self.magic_integration = magic_integration
        self.materials = self._get_mock_materials()
    
    def _get_mock_materials(self) -> Dict[str, Dict[str, Any]]:
        """Get mock magical materials for demonstration."""
        return {
            "mana_crystal": {
                "name": "Mana Crystal",
                "description": "A crystal that naturally accumulates magical energy.",
                "rarity": "common",
                "resonance": ["ARCANE", "ELEMENTAL"],
                "material_type": "mineral"
            },
            "elemental_essence": {
                "name": "Elemental Essence",
                "description": "Raw elemental power crystallized into physical form.",
                "rarity": "uncommon",
                "resonance": ["ELEMENTAL"],
                "material_type": "essence"
            },
            "spirit_essence": {
                "name": "Spirit Essence",
                "description": "The concentrated spiritual energy of the natural world.",
                "rarity": "uncommon",
                "resonance": ["SPIRIT", "NATURAL"],
                "material_type": "essence"
            },
            "void_fragment": {
                "name": "Void Fragment",
                "description": "A shard of nothingness from the void between worlds.",
                "rarity": "rare",
                "resonance": ["VOID", "SHADOW"],
                "material_type": "exotic"
            },
            "time_dust": {
                "name": "Time Dust",
                "description": "Glittering particles that exist partially outside of normal time.",
                "rarity": "rare",
                "resonance": ["TEMPORAL", "ARCANE"],
                "material_type": "exotic"
            },
            "divine_light": {
                "name": "Divine Light",
                "description": "Sacred light captured in crystalline form.",
                "rarity": "rare",
                "resonance": ["DIVINE"],
                "material_type": "essence"
            },
            "shadow_residue": {
                "name": "Shadow Residue",
                "description": "Congealed shadow energy with properties of both matter and darkness.",
                "rarity": "uncommon",
                "resonance": ["SHADOW"],
                "material_type": "essence"
            },
            "chaos_shard": {
                "name": "Chaos Shard",
                "description": "A crystallized fragment of pure chaos energy.",
                "rarity": "rare",
                "resonance": ["CHAOS"],
                "material_type": "exotic"
            },
            "order_matrix": {
                "name": "Order Matrix",
                "description": "A perfectly structured crystalline lattice of order magic.",
                "rarity": "rare",
                "resonance": ["ORDER"],
                "material_type": "mineral"
            },
            "blood_essence": {
                "name": "Blood Essence",
                "description": "Crystallized blood magic.",
                "rarity": "rare",
                "resonance": ["BLOOD"],
                "material_type": "essence"
            },
            "mind_crystal": {
                "name": "Mind Crystal",
                "description": "A crystal that resonates with mental energies.",
                "rarity": "uncommon",
                "resonance": ["MIND"],
                "material_type": "mineral"
            }
        }
    
    def distribute_magical_materials(self, world: World) -> World:
        """
        Distribute magical materials throughout the world.
        
        Args:
            world: The world to distribute materials in
            
        Returns:
            The world with distributed materials
        """
        for location_id, location in world.locations.items():
            if location.magic_profile:
                # Determine how many material deposits to add
                num_deposits = 0
                
                # More deposits at hotspots
                if location_id in self.magic_integration.magical_hotspots:
                    num_deposits += random.randint(1, 3)
                
                # More deposits with higher leyline strength
                if location.magic_profile.leyline_strength > 0.5:
                    num_deposits += 1
                
                # Random chance for additional deposits
                if random.random() < 0.3:
                    num_deposits += 1
                
                # Add the deposits
                for _ in range(num_deposits):
                    self._add_material_deposit(location)
        
        return world
    
    def _add_material_deposit(self, location: Location) -> None:
        """
        Add a magical material deposit to a location.
        
        Args:
            location: The location to add a deposit to
        """
        if not location.magic_profile:
            return
        
        # Determine which materials might be found here based on the location's magical profile
        suitable_materials = []
        
        for material_id, material in self.materials.items():
            # Check if any of the material's resonance domains match the location's dominant aspects
            domain_match = False
            for resonance in material["resonance"]:
                try:
                    domain = Domain[resonance]
                    if domain in location.magic_profile.dominant_magic_aspects:
                        domain_match = True
                        break
                except KeyError:
                    # Invalid domain name in resonance
                    continue
            
            if domain_match:
                suitable_materials.append(material_id)
        
        # If no suitable materials were found, add some based on rarity
        if not suitable_materials:
            for material_id, material in self.materials.items():
                if material["rarity"] == "common":
                    # 50% chance to include common materials
                    if random.random() < 0.5:
                        suitable_materials.append(material_id)
                elif material["rarity"] == "uncommon":
                    # 25% chance to include uncommon materials
                    if random.random() < 0.25:
                        suitable_materials.append(material_id)
                elif material["rarity"] == "rare":
                    # 10% chance to include rare materials
                    if random.random() < 0.1:
                        suitable_materials.append(material_id)
        
        # If we still have no suitable materials, pick a random one
        if not suitable_materials:
            suitable_materials = [random.choice(list(self.materials.keys()))]
        
        # Choose a material and create a deposit
        material_id = random.choice(suitable_materials)
        material = self.materials[material_id]
        
        # Determine the deposit size based on rarity
        if material["rarity"] == "common":
            size = random.choice(["small", "medium", "large"])
        elif material["rarity"] == "uncommon":
            size = random.choice(["small", "medium", "medium"])
        else:  # rare
            size = random.choice(["small", "small", "medium"])
        
        # Map size to quantity range
        quantity_ranges = {
            "small": (1, 5),
            "medium": (5, 15),
            "large": (15, 30)
        }
        
        quantity = random.randint(*quantity_ranges[size])
        
        # Create the deposit as a POI
        deposit_name = f"{size.capitalize()} {material['name']} Deposit"
        deposit_description = f"A {size} deposit of {material['name']}. {material['description']} This deposit could yield approximately {quantity} units."
        
        poi = POI(
            id=f"poi_material_{self.magic_integration.poi_counter}",
            name=deposit_name,
            poi_type=POIType.MINE,
            description=deposit_description,
            coordinates=(
                random.uniform(0, 1),  # x-coordinate within location
                random.uniform(0, 1)   # y-coordinate within location
            )
        )
        self.magic_integration.poi_counter += 1
        
        # Mark as magical and add magical properties
        poi.is_magical = True
        poi.magical_properties = {
            "material_id": material_id,
            "material_name": material["name"],
            "rarity": material["rarity"],
            "resonance": material["resonance"],
            "size": size,
            "quantity": quantity
        }
        
        # Add to location's POIs
        location.pois.append(poi)