"""
Magic World Integration Module

This module handles the integration between the magic system and the world generator.
It adds magical features to the world including leylines, magical POIs, and material deposits.
"""

import random
import math
from typing import Dict, List, Any, Tuple, Set, Optional
import uuid
import logging

from ..world_generation.world_model import World, Location, POI, Coordinates
from ..world_generation.poi_placement_service import POIType, POIPlacementService

from .magic_system import (
    MagicSource, 
    MagicTier, 
    EffectType, 
    TargetType, 
    DamageType,
    ManaFluxLevel,
    LocationMagicProfile
)

from .magical_material_service import MagicalMaterialService

# Configure logging
logger = logging.getLogger(__name__)


class MagicWorldIntegration:
    """
    Integrates the magic system with the world generator.
    Handles adding magical features to the world.
    """
    
    def __init__(self):
        """Initialize the magic world integration"""
        self.leyline_map = {}  # Map of leyline connections between locations
        self.magical_hotspots = []  # List of locations with high magical energy
        self.poi_service = POIPlacementService()
    
    def enhance_world_with_magic(self, world: World) -> World:
        """
        Enhance a world with magical features
        
        Args:
            world: The world to enhance
            
        Returns:
            The enhanced world
        """
        # Generate leyline network
        self._generate_leyline_network(world)
        
        # Add magic profiles to locations
        for location_id, location in world.locations.items():
            location.magic_profile = self._generate_location_magic_profile(location)
            
            # Add magical POIs based on the location's magic profile
            self._add_magical_pois(location)
        
        return world
    
    def _generate_leyline_network(self, world: World) -> None:
        """
        Generate a network of leylines connecting locations
        
        Args:
            world: The world to generate leylines for
        """
        # Identify potential leyline nodes (about 30% of locations)
        potential_nodes = []
        for location_id, location in world.locations.items():
            # Some locations are more likely to be leyline nodes based on biome
            biome_factor = 1.0
            
            if hasattr(location, 'biome'):
                if location.biome == 'forest':
                    biome_factor = 1.5
                elif location.biome == 'mountain':
                    biome_factor = 2.0
                elif location.biome == 'swamp':
                    biome_factor = 1.8
                elif location.biome == 'desert':
                    biome_factor = 0.7
            
            if random.random() < 0.3 * biome_factor:
                potential_nodes.append(location_id)
        
        # Select magical hotspots (about 10% of nodes)
        self.magical_hotspots = random.sample(
            potential_nodes,
            min(max(1, len(potential_nodes) // 10), 5)
        )
        
        # Connect nodes to form leylines
        for i, node_id in enumerate(potential_nodes):
            # Each node connects to 1-3 other nodes
            num_connections = random.randint(1, min(3, len(potential_nodes) - 1))
            
            # Get possible connections (not yet connected nodes)
            possible_connections = [n for n in potential_nodes if n != node_id and n not in self.leyline_map.get(node_id, {})]
            
            if not possible_connections:
                continue
                
            # Select connections
            connections = random.sample(
                possible_connections,
                min(num_connections, len(possible_connections))
            )
            
            # Add connections to leyline map
            for conn_id in connections:
                # Determine leyline strength (higher for hotspots)
                strength = random.uniform(0.5, 1.0)
                
                if node_id in self.magical_hotspots:
                    strength *= 2.0
                if conn_id in self.magical_hotspots:
                    strength *= 2.0
                
                # Add bidirectional connection
                if node_id not in self.leyline_map:
                    self.leyline_map[node_id] = {}
                if conn_id not in self.leyline_map:
                    self.leyline_map[conn_id] = {}
                
                self.leyline_map[node_id][conn_id] = strength
                self.leyline_map[conn_id][node_id] = strength
    
    def _generate_location_magic_profile(self, location: Location) -> LocationMagicProfile:
        """
        Generate a magic profile for a location
        
        Args:
            location: The location to generate a profile for
            
        Returns:
            A magic profile for the location
        """
        # Default values
        leyline_strength = 0.1
        mana_flux_level = ManaFluxLevel.LOW
        dominant_magic_aspects = []
        allows_ritual_sites = False
        
        # Check if location is in the leyline network
        if location.id in self.leyline_map:
            # Calculate leyline strength based on connections
            connections = self.leyline_map[location.id]
            leyline_strength = sum(connections.values()) / max(1, len(connections))
            
            # Stronger leylines have higher mana flux
            if leyline_strength > 1.5:
                mana_flux_level = ManaFluxLevel.VERY_HIGH
            elif leyline_strength > 1.0:
                mana_flux_level = ManaFluxLevel.HIGH
            elif leyline_strength > 0.5:
                mana_flux_level = ManaFluxLevel.MEDIUM
            
            # Hotspots always allow ritual sites
            if location.id in self.magical_hotspots:
                allows_ritual_sites = True
            # Other leyline locations might allow ritual sites
            elif random.random() < leyline_strength * 0.7:
                allows_ritual_sites = True
        
        # Determine dominant magic aspects based on biome
        if hasattr(location, 'biome'):
            if location.biome == 'forest':
                dominant_magic_aspects = [DamageType.EARTH, DamageType.LIFE]
            elif location.biome == 'mountain':
                dominant_magic_aspects = [DamageType.EARTH, DamageType.AIR]
            elif location.biome == 'desert':
                dominant_magic_aspects = [DamageType.FIRE, DamageType.EARTH]
            elif location.biome == 'coastal':
                dominant_magic_aspects = [DamageType.WATER, DamageType.AIR]
            elif location.biome == 'swamp':
                dominant_magic_aspects = [DamageType.WATER, DamageType.POISON]
            elif location.biome == 'plains':
                dominant_magic_aspects = [DamageType.EARTH, DamageType.LIFE]
            elif location.biome == 'tundra':
                dominant_magic_aspects = [DamageType.ICE, DamageType.AIR]
            else:
                # Default to random aspects
                all_aspects = [
                    DamageType.FIRE, DamageType.WATER, DamageType.EARTH, 
                    DamageType.AIR, DamageType.ARCANE, DamageType.LIFE, 
                    DamageType.DEATH, DamageType.POISON, DamageType.ICE
                ]
                dominant_magic_aspects = random.sample(all_aspects, 2)
        
        # Create and return the magic profile
        return LocationMagicProfile(
            leyline_strength=leyline_strength,
            mana_flux_level=mana_flux_level,
            dominant_magic_aspects=dominant_magic_aspects,
            allows_ritual_sites=allows_ritual_sites
        )
    
    def _add_magical_pois(self, location: Location) -> None:
        """
        Add magical POIs to a location based on its magic profile
        
        Args:
            location: The location to add POIs to
        """
        # Skip if location has no magic profile
        if not hasattr(location, 'magic_profile'):
            return
        
        # Determine number of magical POIs based on magic strength
        num_pois = 0
        
        if location.magic_profile.leyline_strength > 1.5:
            num_pois = random.randint(2, 3)
        elif location.magic_profile.leyline_strength > 0.8:
            num_pois = random.randint(1, 2)
        elif location.magic_profile.leyline_strength > 0.3:
            num_pois = 1 if random.random() < 0.7 else 0
        else:
            # Low magic areas rarely have magical POIs
            num_pois = 1 if random.random() < 0.2 else 0
        
        # No POIs to add
        if num_pois == 0:
            return
        
        # Add magical POIs
        for _ in range(num_pois):
            # Select POI type based on location and magic profile
            poi_type = self._select_magical_poi_type(location)
            
            # Generate name and description
            name, description = self._generate_magical_poi_details(location, poi_type)
            
            # Create the POI
            poi = POI(
                id=f"poi_{uuid.uuid4().hex[:8]}",
                name=name,
                poi_type=poi_type,
                description=description,
                coordinates=(
                    location.coordinates[0] + random.uniform(-0.5, 0.5),
                    location.coordinates[1] + random.uniform(-0.5, 0.5)
                )
            )
            
            # Add to location
            location.pois.append(poi)
    
    def _select_magical_poi_type(self, location: Location) -> POIType:
        """
        Select an appropriate magical POI type for a location
        
        Args:
            location: The location to select a POI type for
            
        Returns:
            A POI type
        """
        # Potential magical POI types
        magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
        
        # Filter by biome and magic profile
        suitable_types = []
        
        if hasattr(location, 'biome'):
            if location.biome == 'forest':
                suitable_types = [POIType.GROVE, POIType.SHRINE]
            elif location.biome == 'mountain':
                suitable_types = [POIType.SHRINE, POIType.RELIC_SITE]
            elif location.biome == 'desert':
                suitable_types = [POIType.SHRINE, POIType.RELIC_SITE]
            elif location.biome == 'coastal' or location.biome == 'swamp':
                suitable_types = [POIType.SPRING, POIType.SHRINE]
            elif location.biome == 'plains':
                suitable_types = [POIType.GROVE, POIType.SHRINE]
            elif location.biome == 'tundra':
                suitable_types = [POIType.SHRINE, POIType.RELIC_SITE]
        
        # If no suitable types or ritual site is allowed, use all types
        if not suitable_types or location.magic_profile.allows_ritual_sites:
            suitable_types = magical_poi_types
        
        # Always allow shrines
        if POIType.SHRINE not in suitable_types:
            suitable_types.append(POIType.SHRINE)
        
        # Select a random type from suitable types
        return random.choice(suitable_types)
    
    def _generate_magical_poi_details(self, location: Location, poi_type: POIType) -> Tuple[str, str]:
        """
        Generate a name and description for a magical POI
        
        Args:
            location: The location of the POI
            poi_type: The type of POI
            
        Returns:
            A tuple of (name, description)
        """
        # Get the dominant magic aspects as strings
        magic_aspects = [aspect.name.lower() for aspect in location.magic_profile.dominant_magic_aspects]
        
        # Generate name based on type and magic
        name = ""
        description = ""
        
        if poi_type == POIType.SHRINE:
            # Generate shrine name
            element = random.choice(magic_aspects) if magic_aspects else "arcane"
            prefix = random.choice(["Ancient", "Sacred", "Forgotten", "Hidden", "Mystic", "Radiant", "Silent"])
            name = f"{prefix} {element.capitalize()} Shrine"
            
            # Generate description
            descriptions = [
                f"A shrine dedicated to the power of {element}. The air here feels charged with magical energy.",
                f"This {element} shrine has stood for centuries, drawing pilgrims seeking magical knowledge.",
                f"A place of worship where {element} magic flows strongly. Ritual symbols adorn the weathered stone.",
                f"The remnants of an old temple where practitioners once channeled {element} energy."
            ]
            description = random.choice(descriptions)
            
        elif poi_type == POIType.GROVE:
            # Generate grove name
            prefix = random.choice(["Whispering", "Ancient", "Verdant", "Glowing", "Ethereal", "Timeless", "Enchanted"])
            name = f"{prefix} Grove"
            
            # Generate description
            descriptions = [
                "A sacred grove where the trees seem to whisper ancient secrets. The foliage glows faintly at night.",
                "This ancient grove has been shaped by magical energies, creating a sanctuary for mystical creatures.",
                "A circle of trees that seem to have a consciousness of their own. The ground is carpeted with luminescent moss.",
                "Within this grove, the barrier between worlds grows thin. Wisps of magical energy dance between the trees."
            ]
            description = random.choice(descriptions)
            
        elif poi_type == POIType.SPRING:
            # Generate spring name
            element = random.choice(magic_aspects) if magic_aspects else "clear"
            prefix = random.choice(["Healing", "Mystic", "Eternal", "Shimmering", "Luminous", "Whispering"])
            name = f"{prefix} {element.capitalize()} Spring"
            
            # Generate description
            descriptions = [
                f"A spring whose waters are infused with {element} energy, said to grant magical insights to those who drink.",
                f"This {element} spring bubbles with magical properties. The water glows faintly in the darkness.",
                f"A source of magical water that never runs dry. The {element} energies here have attracted magical creatures.",
                f"The waters of this spring are known for their {element} properties and healing abilities."
            ]
            description = random.choice(descriptions)
            
        elif poi_type == POIType.RELIC_SITE:
            # Generate relic site name
            prefix = random.choice(["Forgotten", "Ancient", "Lost", "Mysterious", "Hidden", "Forbidden", "Arcane"])
            site_type = random.choice(["Ruins", "Stones", "Circle", "Monoliths", "Altar", "Pillars", "Temple"])
            name = f"{prefix} {site_type}"
            
            # Generate description
            descriptions = [
                "The remains of an ancient magical site. Powerful artifacts may still be buried beneath the rubble.",
                "These ancient stones form a perfect ritual circle. The ground here is saturated with residual magical energy.",
                "A site where a powerful magical event once occurred. The air still crackles with arcane power.",
                "These mysterious ruins date back to an age when magic was more prevalent. Strange symbols are carved into the stones."
            ]
            description = random.choice(descriptions)
        
        # Fallback for any other POI type
        if not name or not description:
            name = f"Magical {poi_type.name.capitalize()}"
            description = f"A site of magical significance related to {', '.join(magic_aspects)}."
        
        return name, description


class MagicalMaterialWorldIntegration:
    """
    Integrates magical materials with the world generator.
    Handles the distribution of magical materials throughout the world.
    """
    
    def __init__(self, magic_integration: MagicWorldIntegration):
        """
        Initialize the magical material world integration
        
        Args:
            magic_integration: The magic world integration instance
        """
        self.magic_integration = magic_integration
        self.material_service = MagicalMaterialService()
    
    def distribute_magical_materials(self, world: World) -> None:
        """
        Distribute magical materials throughout the world
        
        Args:
            world: The world to distribute materials in
        """
        # Get all possible magical materials
        materials = self.material_service.get_all_materials()
        
        # For each location, determine if it should have material deposits
        for location_id, location in world.locations.items():
            # Skip if location has no magic profile
            if not hasattr(location, 'magic_profile'):
                continue
            
            # Higher chance of materials in high-magic areas
            chance = min(0.8, location.magic_profile.leyline_strength * 0.5)
            
            if random.random() < chance:
                self._add_material_deposit(location, materials)
    
    def _add_material_deposit(self, location: Location, materials: List[Dict[str, Any]]) -> None:
        """
        Add a magical material deposit to a location
        
        Args:
            location: The location to add a deposit to
            materials: List of possible materials
        """
        # Filter materials by location biome compatibility
        compatible_materials = []
        
        if hasattr(location, 'biome'):
            for material in materials:
                # Check if material has biome preferences
                if 'preferred_biomes' not in material:
                    compatible_materials.append(material)
                    continue
                
                # Check if this biome is preferred for the material
                if location.biome in material['preferred_biomes']:
                    # Higher weight for preferred biomes
                    compatible_materials.extend([material] * 3)
                else:
                    # Still possible but less likely
                    compatible_materials.append(material)
        else:
            compatible_materials = materials
        
        # No compatible materials
        if not compatible_materials:
            return
        
        # Select a random material
        material = random.choice(compatible_materials)
        
        # Create a mine POI for the material
        mine_name = f"Glimmering {material['name']} Deposit"
        
        # Generate description
        descriptions = [
            f"A rich deposit of {material['name']}, the crystals glowing with magical energy.",
            f"This mine contains veins of {material['name']}, prized by enchanters and spellcrafters.",
            f"The walls of this cave sparkle with {material['name']} deposits, emanating {material['magical_aspect'].lower()} energy.",
            f"A natural formation where {material['name']} can be harvested. The entire area resonates with magical potential."
        ]
        mine_description = random.choice(descriptions)
        
        # Create the POI
        poi = POI(
            id=f"poi_{uuid.uuid4().hex[:8]}",
            name=mine_name,
            poi_type=POIType.MINE,
            description=mine_description,
            coordinates=(
                location.coordinates[0] + random.uniform(-0.5, 0.5),
                location.coordinates[1] + random.uniform(-0.5, 0.5)
            )
        )
        
        # Add material information to POI metadata
        poi.metadata = {
            "material_id": material.get("id", str(uuid.uuid4())),
            "material_name": material["name"],
            "material_rarity": material.get("rarity", "common"),
            "material_magical_aspect": material.get("magical_aspect", "arcane")
        }
        
        # Add to location
        location.pois.append(poi)