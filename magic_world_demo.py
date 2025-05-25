"""
Magic World Demo

This script demonstrates how the magic system integrates with the world generator
to create a rich, magical world with leylines, magical POIs, and material deposits.
"""

import random
import sys
import os
import json

# Set the random seed for reproducible results
random.seed(42)

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "backend", "src"))

# Import from the world generator
from backend.src.world_generation.world_model import World, Location, POI, Climate, Terrain
from backend.src.world_generation.poi_placement_service import POIType

# Import from magic system integration
from backend.src.magic_system.magic_world_integration import MagicWorldIntegration, MagicalMaterialWorldIntegration


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