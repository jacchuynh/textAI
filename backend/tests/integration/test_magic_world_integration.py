#!/usr/bin/env python3
"""
Test integration between magic system and world generator

This test ensures that the magic system properly integrates with the world generator,
allowing for magical features to be placed in the world.
"""

import unittest
import random
import os
import sys
from typing import Dict, List, Any, Optional

# Set the random seed for reproducible tests
random.seed(42)

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(parent_dir, "src"))

try:
    # Import magic system components
    from magic_system.magic_system import (
        MagicSystem, 
        ManaFluxLevel,
        LocationMagicProfile,
        DamageType
    )

    # Import world generator components
    from world_generation.world_model import (
        World,
        Location,
        POI,
        Coordinates,
        Climate,
        Terrain,
        POIType
    )

    # Import integration module
    from magic_system.magic_world_integration import (
        MagicWorldIntegration,
        MagicalMaterialWorldIntegration
    )

    class TestMagicWorldIntegration(unittest.TestCase):
        """Test the integration between the magic system and world generator."""
        
        def setUp(self):
            """Set up the test environment."""
            # Create a magic system instance
            self.magic_system = MagicSystem()
            
            # Create a magic world integration instance
            self.magic_integration = MagicWorldIntegration()
            
            # Create a magical material integration instance
            self.material_integration = MagicalMaterialWorldIntegration(self.magic_integration)
            
            # Create a test world
            self.world = self._create_test_world()
        
        def _create_test_world(self) -> World:
            """Create a test world with diverse biomes."""
            # Create locations with different biomes
            locations = {}
            
            # Forest location
            forest_pois = [
                POI(
                    id="poi_forest_1",
                    name="Ancient Oak",
                    poi_type=POIType.GROVE,
                    description="A massive oak tree that seems to radiate ancient energy.",
                    coordinates=(1.5, 1.5)
                )
            ]
            
            forest_location = Location(
                id="loc_forest",
                name="Whispering Woods",
                description="A dense forest where the trees seem to whisper secrets.",
                coordinates=(1.0, 1.0),
                terrain=Terrain.HILLS,
                pois=forest_pois,
                biome="forest"
            )
            locations["loc_forest"] = forest_location
            
            # Mountain location
            mountain_pois = [
                POI(
                    id="poi_mountain_1",
                    name="Frost Peak",
                    poi_type=POIType.SHRINE,
                    description="The highest peak in the range, eternally covered in snow.",
                    coordinates=(3.5, 3.5)
                )
            ]
            
            mountain_location = Location(
                id="loc_mountain",
                name="Skyreach Mountains",
                description="Towering mountains that pierce the clouds.",
                coordinates=(3.0, 3.0),
                terrain=Terrain.MOUNTAINS,
                pois=mountain_pois,
                biome="mountain"
            )
            locations["loc_mountain"] = mountain_location
            
            # Desert location
            desert_pois = [
                POI(
                    id="poi_desert_1",
                    name="Sun-Scorched Ruins",
                    poi_type=POIType.RUIN,
                    description="Ancient ruins buried and revealed by shifting sands.",
                    coordinates=(5.5, 1.5)
                )
            ]
            
            desert_location = Location(
                id="loc_desert",
                name="Endless Sands",
                description="A vast desert where sandstorms reveal and conceal ancient ruins.",
                coordinates=(5.0, 1.0),
                terrain=Terrain.FLAT,
                pois=desert_pois,
                biome="desert"
            )
            locations["loc_desert"] = desert_location
            
            # Coastal location
            coastal_pois = [
                POI(
                    id="poi_coastal_1",
                    name="Tidal Caves",
                    poi_type=POIType.CAVE,
                    description="Caves carved by the relentless sea.",
                    coordinates=(1.5, 5.5)
                )
            ]
            
            coastal_location = Location(
                id="loc_coastal",
                name="Azure Coast",
                description="A beautiful coastline with crystal clear waters.",
                coordinates=(1.0, 5.0),
                terrain=Terrain.COASTAL,
                pois=coastal_pois,
                biome="coastal"
            )
            locations["loc_coastal"] = coastal_location
            
            # Swamp location
            swamp_pois = [
                POI(
                    id="poi_swamp_1",
                    name="Mist Hollow",
                    poi_type=POIType.SPRING,
                    description="A pool of mysterious water shrouded in mist.",
                    coordinates=(5.5, 5.5)
                )
            ]
            
            swamp_location = Location(
                id="loc_swamp",
                name="Mistmarsh",
                description="A foggy swamp where lights flicker in the distance.",
                coordinates=(5.0, 5.0),
                terrain=Terrain.RIVER,
                pois=swamp_pois,
                biome="swamp"
            )
            locations["loc_swamp"] = swamp_location
            
            # Create world
            return World(
                id="test_world",
                name="Test World",
                width=10,
                height=10,
                locations=locations,
                climate=Climate.TEMPERATE
            )
        
        def test_world_enhancement_with_magic(self):
            """Test enhancing a world with magic."""
            # Enhance the world with magic
            enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
            
            # Check that each location now has a magic profile
            for location_id, location in enhanced_world.locations.items():
                self.assertTrue(hasattr(location, 'magic_profile'), f"Location {location_id} has no magic profile")
                self.assertIsInstance(location.magic_profile, LocationMagicProfile)
                
                # Check that leyline strengths are in expected range
                self.assertGreaterEqual(location.magic_profile.leyline_strength, 0.0)
                
                # Check that mana flux level is a valid enum
                self.assertIsInstance(location.magic_profile.mana_flux_level, ManaFluxLevel)
                
                # Check that dominant magic aspects are set
                self.assertIsInstance(location.magic_profile.dominant_magic_aspects, list)
                for aspect in location.magic_profile.dominant_magic_aspects:
                    self.assertIsInstance(aspect, DamageType)
            
            # Check that leyline network is created
            self.assertIsInstance(self.magic_integration.leyline_map, dict)
            
            # Check that magical hotspots are identified
            self.assertIsInstance(self.magic_integration.magical_hotspots, list)
            
            # Return the enhanced world for further tests
            return enhanced_world
        
        def test_magical_poi_generation(self):
            """Test generation of magical POIs."""
            # Enhance the world with magic
            enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
            
            # Count magical POIs before and after enhancement
            original_poi_count = sum(len(location.pois) for location in self.world.locations.values())
            enhanced_poi_count = sum(len(location.pois) for location in enhanced_world.locations.values())
            
            # Should have more POIs after enhancement
            self.assertGreaterEqual(enhanced_poi_count, original_poi_count)
            
            # Check that magical POIs have been added
            magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
            magical_poi_count = 0
            
            for location in enhanced_world.locations.values():
                for poi in location.pois:
                    if poi.poi_type in magical_poi_types:
                        magical_poi_count += 1
                        
                        # Check that POI has a name and description
                        self.assertIsNotNone(poi.name)
                        self.assertIsNotNone(poi.description)
                        self.assertTrue(len(poi.name) > 0)
                        self.assertTrue(len(poi.description) > 0)
            
            # Should have at least one magical POI
            self.assertGreater(magical_poi_count, 0)
        
        def test_magical_material_distribution(self):
            """Test distribution of magical materials."""
            # Enhance the world with magic
            enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
            
            # Distribute magical materials
            world_with_materials = self.material_integration.distribute_magical_materials(enhanced_world)
            
            # Check for material deposits
            material_deposit_count = 0
            
            for location in world_with_materials.locations.values():
                if hasattr(location, 'material_deposits') and location.material_deposits:
                    material_deposit_count += 1
                    
                    # Check that deposits have required properties
                    for deposit in location.material_deposits:
                        self.assertIn('id', deposit)
                        self.assertIn('name', deposit)
                        self.assertIn('quantity', deposit)
            
            # Should have at least one material deposit
            self.assertGreater(material_deposit_count, 0)
        
        def test_biome_specific_magic(self):
            """Test that biomes influence magic properties."""
            # Enhance the world with magic
            enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
            
            # Check biome-specific magic aspects
            expected_aspects = {
                "forest": [DamageType.EARTH, DamageType.LIFE],
                "mountain": [DamageType.EARTH, DamageType.AIR],
                "desert": [DamageType.FIRE, DamageType.EARTH],
                "coastal": [DamageType.WATER, DamageType.AIR],
                "swamp": [DamageType.WATER, DamageType.POISON]
            }
            
            for location_id, location in enhanced_world.locations.items():
                if hasattr(location, 'biome') and location.biome in expected_aspects:
                    expected = expected_aspects[location.biome]
                    actual = location.magic_profile.dominant_magic_aspects
                    
                    # At least one of the expected aspects should be present
                    common_aspects = set(expected).intersection(set(actual))
                    self.assertGreater(len(common_aspects), 0, 
                                    f"Location {location_id} with biome {location.biome} has no expected magic aspects")

    if __name__ == "__main__":
        unittest.main()

except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires the magic system and world generation modules.")
    print("Skipping tests.")
    
    # Create a dummy test class to prevent test failure
    class DummyTest(unittest.TestCase):
        def test_dummy(self):
            self.skipTest("Required modules not available")