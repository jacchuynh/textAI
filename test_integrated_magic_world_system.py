"""
Test for the integrated magic system and world generation

This test demonstrates how the magic system and world generator
work together to create a rich, magical world.
"""

import unittest
import random
import os
import sys
import json
from typing import Dict, List, Any, Optional

# Set the random seed for reproducible tests
random.seed(42)

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "backend", "src"))

# Import magic system components
from magic_system import (
    MagicSource, 
    MagicTier, 
    EffectType, 
    TargetType, 
    DamageType,
    ManaFluxLevel,
    LocationMagicProfile,
    MagicWorldIntegration,
    MagicalMaterialWorldIntegration
)

# Import world generator components
from world_generation.world_model import (
    World,
    Location,
    POI,
    Coordinates,
    Climate,
    Terrain
)

from world_generation.poi_placement_service import (
    POIPlacementService,
    POIType
)


class TestIntegratedMagicWorld(unittest.TestCase):
    """Test cases for integrated magic system and world generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.world_size = (20, 20)  # Small world for testing
        self.world = self._create_test_world()
        self.magic_integration = MagicWorldIntegration()
        self.material_integration = MagicalMaterialWorldIntegration(self.magic_integration)
    
    def _create_test_world(self) -> World:
        """Create a test world with basic locations"""
        world = World(
            id="test_world",
            name="Test Magic World",
            width=self.world_size[0],
            height=self.world_size[1],
            locations={},
            climate=Climate.TEMPERATE
        )
        
        # Add some test locations with different biomes
        location_types = ["forest", "mountain", "desert", "coastal", "swamp"]
        
        for i in range(10):
            x = random.randint(0, self.world_size[0] - 1)
            y = random.randint(0, self.world_size[1] - 1)
            biome = random.choice(location_types)
            
            location = Location(
                id=f"location_{i}",
                name=f"Test Location {i}",
                description=f"A test location in a {biome} biome",
                coordinates=(x, y),
                terrain=random.choice(list(Terrain)),
                pois=[],
                biome=biome
            )
            
            world.locations[location.id] = location
        
        return world
    
    def test_magic_enriches_world(self):
        """Test that the magic system enriches the world with magical features"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Verify leylines were generated
        self.assertGreater(len(self.magic_integration.leyline_map), 0, 
                         "No leylines were generated")
        
        # Verify all locations have magic profiles
        for location_id, location in enhanced_world.locations.items():
            self.assertTrue(hasattr(location, 'magic_profile'), 
                          f"Location {location_id} has no magic profile")
            
            # Print some information about the location's magic profile
            print(f"Location {location.name} ({location.biome}):")
            print(f"  Leyline strength: {location.magic_profile.leyline_strength}")
            print(f"  Mana flux level: {location.magic_profile.mana_flux_level.name}")
            print(f"  Dominant magic: {[aspect.name for aspect in location.magic_profile.dominant_magic_aspects]}")
            print(f"  Allows ritual sites: {location.magic_profile.allows_ritual_sites}")
            print()
    
    def test_magical_pois_added(self):
        """Test that magical POIs are added to locations"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Count magical POIs
        magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
        magical_poi_count = 0
        
        for location in enhanced_world.locations.values():
            for poi in location.pois:
                if poi.poi_type in magical_poi_types:
                    magical_poi_count += 1
                    print(f"Magical POI found: {poi.name} ({poi.poi_type.name})")
                    print(f"  Description: {poi.description}")
                    print()
        
        # Verify that magical POIs were added
        self.assertGreater(magical_poi_count, 0, 
                         "No magical POIs were added to the world")
    
    def test_magical_material_distribution(self):
        """Test that magical materials are distributed throughout the world"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Distribute magical materials
        self.material_integration.distribute_magical_materials(enhanced_world)
        
        # Count material deposits
        deposit_count = 0
        
        for location in enhanced_world.locations.values():
            for poi in location.pois:
                if poi.poi_type == POIType.MINE and "Glimmering" in poi.name:
                    deposit_count += 1
                    print(f"Material deposit found: {poi.name}")
                    print(f"  Description: {poi.description}")
                    print()
        
        # Verify that material deposits were added
        self.assertGreater(deposit_count, 0, 
                         "No magical material deposits were added to the world")
    
    def test_biome_specific_magic(self):
        """Test that different biomes have appropriate magical properties"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Check forest locations for Earth magic
        for location in enhanced_world.locations.values():
            if hasattr(location, 'biome') and location.biome == 'forest':
                self.assertIn(DamageType.EARTH, location.magic_profile.dominant_magic_aspects,
                            f"Forest location {location.name} doesn't have Earth magic")
            
            # Check desert locations for Fire magic
            elif hasattr(location, 'biome') and location.biome == 'desert':
                self.assertIn(DamageType.FIRE, location.magic_profile.dominant_magic_aspects,
                            f"Desert location {location.name} doesn't have Fire magic")
            
            # Check coastal locations for Water magic
            elif hasattr(location, 'biome') and location.biome == 'coastal':
                self.assertIn(DamageType.WATER, location.magic_profile.dominant_magic_aspects,
                            f"Coastal location {location.name} doesn't have Water magic")


if __name__ == "__main__":
    unittest.main()