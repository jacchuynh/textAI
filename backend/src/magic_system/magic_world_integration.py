"""
Magic World Integration Module

This module integrates the magic system with the world generation system,
allowing for magical features to be placed in the world such as leylines,
magical points of interest, and material deposits.
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto

# Import magic system components
from game_engine.magic_system import (
    MagicSystem, 
    ManaFluxLevel,
    LocationMagicProfile,
    DamageType
)

class POIType(Enum):
    """Types of points of interest that can be placed in the world."""
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

class POI:
    """A point of interest in the world."""
    
    def __init__(self, id, name, poi_type, description, coordinates):
        self.id = id
        self.name = name
        self.poi_type = poi_type
        self.description = description
        self.coordinates = coordinates
        self.metadata = {}

class Location:
    """A location in the world."""
    
    def __init__(self, id, name, description, coordinates, terrain, pois, biome):
        self.id = id
        self.name = name
        self.description = description
        self.coordinates = coordinates
        self.terrain = terrain
        self.pois = pois
        self.biome = biome

class World:
    """A world containing locations."""
    
    def __init__(self, id, name, width, height, locations, climate):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.locations = locations
        self.climate = climate

class MagicWorldIntegration:
    """Integrates the magic system with the world generation system."""
    
    def __init__(self):
        """Initialize the magic world integration."""
        self.leyline_map = {}
        self.magical_hotspots = []
        self.magic_system = MagicSystem()
    
    def enhance_world_with_magic(self, world: World) -> World:
        """
        Enhance a world with magical features such as leylines and magical points of interest.
        
        Args:
            world: The world to enhance
            
        Returns:
            The enhanced world
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
        
        # Generate leylines between locations
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
        
        # Add magic profiles to locations
        for location_id, location in world.locations.items():
            # Default values
            leyline_strength = 0.1
            mana_flux_level = ManaFluxLevel.LOW
            dominant_magic_aspects = []
            allows_ritual_sites = False
            
            # Check if location is in the leyline network
            if location_id in self.leyline_map:
                # Calculate leyline strength based on connections
                connections = self.leyline_map[location_id]
                leyline_strength = sum(connections.values()) / max(1, len(connections))
                
                # Stronger leylines have higher mana flux
                if leyline_strength > 1.5:
                    mana_flux_level = ManaFluxLevel.VERY_HIGH
                elif leyline_strength > 1.0:
                    mana_flux_level = ManaFluxLevel.HIGH
                elif leyline_strength > 0.5:
                    mana_flux_level = ManaFluxLevel.MEDIUM
                
                # Hotspots always allow ritual sites
                if location_id in self.magical_hotspots:
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
            
            # Create and assign magic profile
            location.magic_profile = LocationMagicProfile(
                leyline_strength=leyline_strength,
                mana_flux_level=mana_flux_level,
                dominant_magic_aspects=dominant_magic_aspects,
                allows_ritual_sites=allows_ritual_sites
            )
            
            # Add magical POIs
            self._add_magical_pois(location)
        
        return world
    
    def _add_magical_pois(self, location: Location) -> None:
        """
        Add magical POIs to a location based on its magic profile.
        
        Args:
            location: The location to add POIs to
        """
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
            # Potential magical POI types
            magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
            
            # Filter by biome
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
            
            # If no suitable types or ritual site is allowed, use all types
            if not suitable_types or location.magic_profile.allows_ritual_sites:
                suitable_types = magical_poi_types
            
            # Always allow shrines
            if POIType.SHRINE not in suitable_types:
                suitable_types.append(POIType.SHRINE)
            
            # Select a POI type
            poi_type = random.choice(suitable_types)
            
            # Generate name and description
            name = ""
            description = ""
            
            # Get the dominant magic aspects as strings
            magic_aspects = [aspect.name.lower() for aspect in location.magic_profile.dominant_magic_aspects]
            element = random.choice(magic_aspects) if magic_aspects else "arcane"
            
            if poi_type == POIType.SHRINE:
                prefix = random.choice(["Ancient", "Sacred", "Forgotten", "Hidden", "Mystic"])
                name = f"{prefix} {element.capitalize()} Shrine"
                description = f"A shrine dedicated to the power of {element}. The air here feels charged with magical energy."
            
            elif poi_type == POIType.GROVE:
                prefix = random.choice(["Whispering", "Ancient", "Verdant", "Glowing", "Ethereal"])
                name = f"{prefix} Grove"
                description = "A sacred grove where the trees seem to whisper ancient secrets. The foliage glows faintly at night."
            
            elif poi_type == POIType.SPRING:
                prefix = random.choice(["Healing", "Mystic", "Eternal", "Shimmering", "Luminous"])
                name = f"{prefix} {element.capitalize()} Spring"
                description = f"A spring whose waters are infused with {element} energy, said to grant magical insights to those who drink."
            
            elif poi_type == POIType.RELIC_SITE:
                prefix = random.choice(["Forgotten", "Ancient", "Lost", "Mysterious", "Hidden"])
                site_type = random.choice(["Ruins", "Stones", "Circle", "Monoliths", "Altar"])
                name = f"{prefix} {site_type}"
                description = "The remains of an ancient magical site. Powerful artifacts may still be buried beneath the rubble."
            
            # Create POI and add to location
            poi = POI(
                id=f"poi_{random.randint(1000, 9999)}",
                name=name,
                poi_type=poi_type,
                description=description,
                coordinates=(
                    location.coordinates[0] + random.uniform(-0.5, 0.5),
                    location.coordinates[1] + random.uniform(-0.5, 0.5)
                )
            )
            
            location.pois.append(poi)
    
    def get_leyline_network(self) -> Dict[str, Dict[str, float]]:
        """
        Get the leyline network.
        
        Returns:
            Dict mapping location IDs to their connections and strengths
        """
        return self.leyline_map
    
    def get_magical_hotspots(self) -> List[str]:
        """
        Get the list of magical hotspot location IDs.
        
        Returns:
            List of location IDs
        """
        return self.magical_hotspots
    
    def get_location_magic_strength(self, location_id: str) -> float:
        """
        Get the magic strength of a location.
        
        Args:
            location_id: The location ID
            
        Returns:
            The magic strength (0.0 to 5.0)
        """
        if location_id not in self.leyline_map:
            return 0.1  # Default low magic
        
        connections = self.leyline_map[location_id]
        return sum(connections.values()) / max(1, len(connections))

class MagicalMaterialWorldIntegration:
    """Integrates magical materials with the world generation system."""
    
    def __init__(self, magic_integration: MagicWorldIntegration):
        """
        Initialize the magical material world integration.
        
        Args:
            magic_integration: The magic world integration instance
        """
        self.magic_integration = magic_integration
        self.materials = self._get_mock_materials()
    
    def _get_mock_materials(self) -> List[Dict[str, Any]]:
        """Get mock magical materials for demonstration."""
        return [
            {
                "id": "mat_1",
                "name": "Luminite Crystal",
                "rarity": "uncommon",
                "magical_aspect": "light",
                "preferred_biomes": ["mountain", "cave"]
            },
            {
                "id": "mat_2",
                "name": "Emberstone",
                "rarity": "rare",
                "magical_aspect": "fire",
                "preferred_biomes": ["desert", "volcano"]
            },
            {
                "id": "mat_3",
                "name": "Aqua Essence Gem",
                "rarity": "uncommon",
                "magical_aspect": "water",
                "preferred_biomes": ["coastal", "swamp"]
            },
            {
                "id": "mat_4",
                "name": "Verdant Heartwood",
                "rarity": "common",
                "magical_aspect": "life",
                "preferred_biomes": ["forest", "grove"]
            },
            {
                "id": "mat_5",
                "name": "Etheric Resonance Crystal",
                "rarity": "very rare",
                "magical_aspect": "arcane",
                "preferred_biomes": ["mountain", "forest"]
            }
        ]
    
    def distribute_magical_materials(self, world: World) -> World:
        """
        Distribute magical materials throughout the world.
        
        Args:
            world: The world to distribute materials in
            
        Returns:
            The world with materials added
        """
        for location_id, location in world.locations.items():
            # Skip if location has no magic profile
            if not hasattr(location, 'magic_profile'):
                continue
            
            # Higher chance of materials in high-magic areas
            chance = min(0.8, location.magic_profile.leyline_strength * 0.5)
            
            if random.random() < chance:
                self._add_material_deposit(location)
        
        return world
    
    def _add_material_deposit(self, location: Location) -> None:
        """
        Add a magical material deposit to a location.
        
        Args:
            location: The location to add a deposit to
        """
        # Filter materials by biome compatibility
        compatible_materials = []
        
        if hasattr(location, 'biome'):
            for material in self.materials:
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
            compatible_materials = self.materials
        
        # No compatible materials
        if not compatible_materials:
            return
        
        # Select a material
        material = random.choice(compatible_materials)
        
        # Determine quantity based on magic strength and rarity
        base_quantity = 0
        if material['rarity'] == 'common':
            base_quantity = random.randint(3, 8)
        elif material['rarity'] == 'uncommon':
            base_quantity = random.randint(2, 5)
        elif material['rarity'] == 'rare':
            base_quantity = random.randint(1, 3)
        elif material['rarity'] == 'very rare':
            base_quantity = 1
        
        # Adjust for location magic strength
        magic_multiplier = 1.0
        if hasattr(location, 'magic_profile'):
            magic_multiplier = 1.0 + (location.magic_profile.leyline_strength * 0.2)
        
        quantity = max(1, int(base_quantity * magic_multiplier))
        
        # Create deposit
        deposit = {
            "id": f"deposit_{material['id']}_{random.randint(1000, 9999)}",
            "material_id": material['id'],
            "name": material['name'],
            "rarity": material['rarity'],
            "quantity": quantity,
            "magical_aspect": material['magical_aspect'],
            "coordinates": (
                location.coordinates[0] + random.uniform(-0.3, 0.3),
                location.coordinates[1] + random.uniform(-0.3, 0.3)
            )
        }
        
        # Add deposit to location
        if not hasattr(location, 'material_deposits'):
            location.material_deposits = []
        
        location.material_deposits.append(deposit)
    
    def get_material_by_id(self, material_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a material by its ID.
        
        Args:
            material_id: The material ID
            
        Returns:
            The material data or None if not found
        """
        for material in self.materials:
            if material['id'] == material_id:
                return material
        return None
    
    def get_materials_in_location(self, location_id: str, world: World) -> List[Dict[str, Any]]:
        """
        Get all materials available in a location.
        
        Args:
            location_id: The location ID
            world: The world
            
        Returns:
            List of material deposit data
        """
        location = world.locations.get(location_id)
        if not location or not hasattr(location, 'material_deposits'):
            return []
        
        return location.material_deposits