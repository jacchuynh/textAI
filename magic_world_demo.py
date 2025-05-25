"""
Magic World Demo

This script demonstrates how the magic system integrates with the world generator
to create a rich, magical world with leylines, magical POIs, and material deposits.
"""

import random
import sys
import os
import json
from enum import Enum, auto

# Set the random seed for reproducible results
random.seed(42)

# Simple mock classes for demonstration purposes
class Climate(Enum):
    TEMPERATE = auto()
    TROPICAL = auto()
    ARID = auto()
    ARCTIC = auto()

class Terrain(Enum):
    FLAT = auto()
    HILLS = auto()
    MOUNTAINS = auto()
    COASTAL = auto()
    RIVER = auto()

class POIType(Enum):
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

class DamageType(Enum):
    FIRE = auto()
    WATER = auto()
    EARTH = auto()
    AIR = auto()
    ARCANE = auto()
    LIFE = auto()
    DEATH = auto()
    POISON = auto()
    ICE = auto()
    
class ManaFluxLevel(Enum):
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()

class POI:
    def __init__(self, id, name, poi_type, description, coordinates):
        self.id = id
        self.name = name
        self.poi_type = poi_type
        self.description = description
        self.coordinates = coordinates
        self.metadata = {}

class LocationMagicProfile:
    def __init__(self, leyline_strength, mana_flux_level, dominant_magic_aspects, allows_ritual_sites):
        self.leyline_strength = leyline_strength
        self.mana_flux_level = mana_flux_level
        self.dominant_magic_aspects = dominant_magic_aspects
        self.allows_ritual_sites = allows_ritual_sites

class Location:
    def __init__(self, id, name, description, coordinates, terrain, pois, biome):
        self.id = id
        self.name = name
        self.description = description
        self.coordinates = coordinates
        self.terrain = terrain
        self.pois = pois
        self.biome = biome
        
class World:
    def __init__(self, id, name, width, height, locations, climate):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.locations = locations
        self.climate = climate

# Mock integration classes for demonstration
class MagicWorldIntegration:
    def __init__(self):
        self.leyline_map = {}
        self.magical_hotspots = []
    
    def enhance_world_with_magic(self, world):
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
    
    def _add_magical_pois(self, location):
        """Add magical POIs to a location based on its magic profile"""
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

class MagicalMaterialWorldIntegration:
    def __init__(self, magic_integration):
        self.magic_integration = magic_integration
        self.materials = self._get_mock_materials()
    
    def _get_mock_materials(self):
        """Get mock magical materials for demonstration"""
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
    
    def distribute_magical_materials(self, world):
        """Distribute magical materials throughout the world"""
        for location_id, location in world.locations.items():
            # Skip if location has no magic profile
            if not hasattr(location, 'magic_profile'):
                continue
            
            # Higher chance of materials in high-magic areas
            chance = min(0.8, location.magic_profile.leyline_strength * 0.5)
            
            if random.random() < chance:
                self._add_material_deposit(location)
        
        return world
    
    def _add_material_deposit(self, location):
        """Add a magical material deposit to a location"""
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
        
        # Select a random material
        material = random.choice(compatible_materials)
        
        # Create a mine POI for the material
        mine_name = f"Glimmering {material['name']} Deposit"
        mine_description = f"A rich deposit of {material['name']}, the crystals glowing with magical energy."
        
        # Create the POI
        poi = POI(
            id=f"poi_mine_{random.randint(1000, 9999)}",
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
            "material_id": material.get("id"),
            "material_name": material["name"],
            "material_rarity": material.get("rarity", "common"),
            "material_magical_aspect": material.get("magical_aspect", "arcane")
        }
        
        # Add to location
        location.pois.append(poi)


def create_test_world():
    """Create a test world with diverse biomes"""
    world = World(
        id="demo_world",
        name="Mystic Realms",
        width=30,
        height=30,
        locations={},
        climate=Climate.TEMPERATE
    )
    
    # Add locations with different biomes
    biomes = ["forest", "mountain", "desert", "coastal", "swamp", "plains", "tundra"]
    
    for i in range(20):
        x = random.randint(0, world.width - 1)
        y = random.randint(0, world.height - 1)
        biome = biomes[i % len(biomes)]
        
        location = Location(
            id=f"loc_{i}",
            name=f"{biome.capitalize()} {random.choice(['Valley', 'Hills', 'Basin', 'Plateau', 'Lowlands'])}",
            description=f"A {biome} region with unique flora and fauna.",
            coordinates=(x, y),
            terrain=random.choice(list(Terrain)),
            pois=[],
            biome=biome
        )
        
        # Add some basic POIs
        for j in range(random.randint(1, 3)):
            poi_type = random.choice([POIType.VILLAGE, POIType.CAMP, POIType.MINE, POIType.SETTLEMENT])
            
            if poi_type == POIType.VILLAGE:
                name = f"{random.choice(['Green', 'Blue', 'Red', 'Black', 'White'])} {random.choice(['Hill', 'Creek', 'Wood', 'Stone'])} Village"
            elif poi_type == POIType.CAMP:
                name = f"{random.choice(['Hunter', 'Traveler', 'Nomad', 'Merchant'])} Camp"
            elif poi_type == POIType.MINE:
                name = f"{random.choice(['Iron', 'Copper', 'Silver', 'Gold'])} Mine"
            else:
                name = f"{random.choice(['New', 'Old', 'East', 'West'])} Settlement"
            
            poi = POI(
                id=f"poi_{i}_{j}",
                name=name,
                poi_type=poi_type,
                description=f"A {poi_type.name.lower()} in the {biome}.",
                coordinates=(x + random.randint(-1, 1), y + random.randint(-1, 1))
            )
            
            location.pois.append(poi)
        
        world.locations[location.id] = location
    
    return world


def enhance_world_with_magic(world):
    """Enhance the world with magical features"""
    # Create integration modules
    magic_integration = MagicWorldIntegration()
    material_integration = MagicalMaterialWorldIntegration(magic_integration)
    
    # Enhance world with magic
    enhanced_world = magic_integration.enhance_world_with_magic(world)
    
    # Add magical material deposits
    material_integration.distribute_magical_materials(enhanced_world)
    
    return enhanced_world, magic_integration


def print_world_overview(world, magic_integration):
    """Print an overview of the world's magical features"""
    print(f"WORLD: {world.name}")
    print(f"Size: {world.width}x{world.height}")
    print(f"Climate: {world.climate.name}")
    print(f"Locations: {len(world.locations)}")
    print()
    
    print("LEYLINE NETWORK:")
    print(f"Leylines: {len(magic_integration.leyline_map)}")
    print(f"Magical hotspots: {len(magic_integration.magical_hotspots)}")
    print()
    
    # Count magical POIs
    magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
    magical_poi_count = 0
    material_deposit_count = 0
    
    for location in world.locations.values():
        for poi in location.pois:
            if poi.poi_type in magical_poi_types:
                magical_poi_count += 1
            if poi.poi_type == POIType.MINE and "Glimmering" in poi.name:
                material_deposit_count += 1
    
    print(f"Magical POIs: {magical_poi_count}")
    print(f"Material deposits: {material_deposit_count}")
    print()


def print_location_details(world):
    """Print details for each location in the world"""
    print("LOCATION DETAILS:")
    
    for location_id, location in world.locations.items():
        if hasattr(location, 'magic_profile'):
            print(f"{location.name} ({location.biome}):")
            print(f"  Coordinates: {location.coordinates}")
            print(f"  Leyline strength: {location.magic_profile.leyline_strength}")
            print(f"  Mana flux: {location.magic_profile.mana_flux_level.name}")
            print(f"  Magic aspects: {[aspect.name for aspect in location.magic_profile.dominant_magic_aspects]}")
            print(f"  Allows rituals: {location.magic_profile.allows_ritual_sites}")
            
            # List POIs
            if location.pois:
                print("  Points of Interest:")
                for poi in location.pois:
                    print(f"    - {poi.name} ({poi.poi_type.name})")
                    print(f"      {poi.description}")
            
            print()


def print_magical_features(world):
    """Print details about magical features in the world"""
    print("MAGICAL FEATURES:")
    
    # List magical POIs
    magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
    magical_pois = []
    
    for location in world.locations.values():
        for poi in location.pois:
            if poi.poi_type in magical_poi_types:
                magical_pois.append((location, poi))
    
    print(f"Magical POIs ({len(magical_pois)}):")
    for location, poi in magical_pois:
        print(f"  {poi.name} ({poi.poi_type.name}) in {location.name}")
        print(f"    {poi.description}")
        print()
    
    # List material deposits
    material_deposits = []
    
    for location in world.locations.values():
        for poi in location.pois:
            if poi.poi_type == POIType.MINE and "Glimmering" in poi.name:
                material_deposits.append((location, poi))
    
    print(f"Magical Material Deposits ({len(material_deposits)}):")
    for location, poi in material_deposits:
        print(f"  {poi.name} in {location.name}")
        print(f"    {poi.description}")
        if hasattr(poi, 'metadata'):
            print(f"    Material: {poi.metadata.get('material_name', 'Unknown')} ({poi.metadata.get('material_rarity', 'common')})")
            print(f"    Magical Aspect: {poi.metadata.get('material_magical_aspect', 'arcane')}")
        print()


def main():
    """Main demonstration function"""
    print("Creating a test world...")
    world = create_test_world()
    
    print("Enhancing world with magical features...")
    enhanced_world, magic_integration = enhance_world_with_magic(world)
    
    print("\n" + "="*80 + "\n")
    print_world_overview(enhanced_world, magic_integration)
    
    print("="*80 + "\n")
    print_location_details(enhanced_world)
    
    print("="*80 + "\n")
    print_magical_features(enhanced_world)
    
    print("\nDemonstration complete.")


if __name__ == "__main__":
    main()