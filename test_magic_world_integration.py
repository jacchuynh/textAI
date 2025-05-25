"""
Test integration between magic system and world generator

This test ensures that the magic system properly integrates with the world generator,
allowing for magical features to be placed in the world.
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
from magic_system.magic_system import (
    MagicSource, 
    MagicTier, 
    EffectType, 
    TargetType, 
    DamageType,
    ManaFluxLevel,
    LocationMagicProfile
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

from world_generation.world_persistence_manager import (
    WorldPersistenceManager
)

from location_generators.generator_factory import (
    LocationGeneratorFactory
)

from location_generators.village_generator import (
    VillageGenerator
)

from location_generators.base_generator import (
    BaseLocationGenerator,
    LocationFeature
)

# Import integration module
from magic_system.magic_world_integration import (
    MagicWorldIntegration,
    MagicalMaterialWorldIntegration
)


class TestMagicWorldIntegration(unittest.TestCase):
    """Test cases for magic system integration with world generator"""
    
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
        
        # Add some test locations
        location_types = ["forest", "mountain", "desert", "coastal", "swamp"]
        
        for i in range(10):
            x = random.randint(0, self.world_size[0] - 1)
            y = random.randint(0, self.world_size[1] - 1)
            
            location = Location(
                id=f"location_{i}",
                name=f"Test Location {i}",
                description=f"A test location in a {random.choice(location_types)} biome",
                coordinates=(x, y),
                terrain=random.choice(list(Terrain)),
                pois=[],
                biome=random.choice(location_types)
            )
            
            # Add some basic POIs
            for j in range(random.randint(1, 3)):
                poi = POI(
                    id=f"poi_{i}_{j}",
                    name=f"Test POI {j}",
                    poi_type=random.choice(list(POIType)),
                    description="A test POI",
                    coordinates=(x + random.randint(-1, 1), y + random.randint(-1, 1))
                )
                location.pois.append(poi)
            
            world.locations[location.id] = location
        
        return world
    
    def test_magic_integration_enhances_world(self):
        """Test that the magic integration enhances the world with magical features"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Verify that the world has been enhanced with leylines
        self.assertGreater(len(self.magic_integration.leyline_map), 0, 
                          "No leylines were generated")
        
        # Verify that all locations have magic profiles
        for location_id, location in enhanced_world.locations.items():
            self.assertTrue(hasattr(location, 'magic_profile'), 
                           f"Location {location_id} has no magic profile")
            
            # Verify that the magic profile has valid values
            self.assertIsInstance(location.magic_profile, LocationMagicProfile,
                                 f"Magic profile for location {location_id} is not a LocationMagicProfile")
            
            self.assertTrue(0 <= location.magic_profile.leyline_strength <= 5,
                           f"Leyline strength {location.magic_profile.leyline_strength} is out of range")
            
            self.assertIsInstance(location.magic_profile.mana_flux_level, ManaFluxLevel,
                                 "Mana flux level is not a ManaFluxLevel enum")
            
            self.assertTrue(len(location.magic_profile.dominant_magic_aspects) > 0,
                           "No dominant magic aspects in profile")
    
    def test_magical_pois_added(self):
        """Test that magical POIs are added to locations"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Get initial POI count
        initial_poi_count = sum(len(location.pois) for location in self.world.locations.values())
        
        # Count magical POIs
        magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
        magical_poi_count = 0
        
        for location in enhanced_world.locations.values():
            for poi in location.pois:
                if poi.poi_type in magical_poi_types:
                    magical_poi_count += 1
        
        # Verify that magical POIs were added
        self.assertGreater(magical_poi_count, 0, 
                          "No magical POIs were added to the world")
        
        # Print detailed information for debugging
        print(f"Initial POI count: {initial_poi_count}")
        print(f"Magical POI count: {magical_poi_count}")
        print(f"Leyline count: {len(self.magic_integration.leyline_map)}")
        print(f"Magical hotspots: {len(self.magic_integration.magical_hotspots)}")
    
    def test_material_distribution(self):
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
        
        # Verify that material deposits were added
        self.assertGreater(deposit_count, 0, 
                          "No magical material deposits were added to the world")
        
        print(f"Material deposit count: {deposit_count}")
    
    def test_location_magic_profile_consistency(self):
        """Test that location magic profiles are consistent with their environment"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Check that biomes have appropriate magic aspects
        for location_id, location in enhanced_world.locations.items():
            if hasattr(location, 'biome') and hasattr(location, 'magic_profile'):
                # Forest locations should have Earth magic
                if location.biome == 'forest':
                    self.assertIn(DamageType.EARTH, location.magic_profile.dominant_magic_aspects,
                                 f"Forest location {location_id} doesn't have Earth magic")
                
                # Desert locations should have Fire magic
                elif location.biome == 'desert':
                    self.assertIn(DamageType.FIRE, location.magic_profile.dominant_magic_aspects,
                                 f"Desert location {location_id} doesn't have Fire magic")
                
                # Coastal locations should have Water magic
                elif location.biome == 'coastal':
                    self.assertIn(DamageType.WATER, location.magic_profile.dominant_magic_aspects,
                                 f"Coastal location {location_id} doesn't have Water magic")
    
    def test_leyline_influence_on_magic_profile(self):
        """Test that leylines influence the magic profiles of nearby locations"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Check locations near leylines
        for location_id, location in enhanced_world.locations.items():
            x, y = location.coordinates
            
            # Check if there's a leyline at or near this location
            has_nearby_leyline = False
            
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if (x + dx, y + dy) in self.magic_integration.leyline_map:
                        has_nearby_leyline = True
                        break
                if has_nearby_leyline:
                    break
            
            # If there's a nearby leyline, the mana flux should be elevated
            if has_nearby_leyline and hasattr(location, 'magic_profile'):
                self.assertGreaterEqual(location.magic_profile.mana_flux_level.value, 
                                      ManaFluxLevel.MODERATE.value,
                                     f"Location {location_id} near a leyline has low mana flux")
                
                # Locations on strong leylines should allow ritual sites
                if (x, y) in self.magic_integration.leyline_map and \
                   self.magic_integration.leyline_map[(x, y)] >= 3:
                    self.assertTrue(location.magic_profile.allows_ritual_sites,
                                   f"Location {location_id} on a strong leyline doesn't allow ritual sites")
    
    def test_serialization(self):
        """Test that the enhanced world can be serialized to JSON"""
        # Enhance the world with magic
        enhanced_world = self.magic_integration.enhance_world_with_magic(self.world)
        
        # Distribute magical materials
        self.material_integration.distribute_magical_materials(enhanced_world)
        
        # Try to serialize the world
        try:
            # Need to convert some objects to dictionaries for JSON serialization
            world_dict = {
                "id": enhanced_world.id,
                "name": enhanced_world.name,
                "width": enhanced_world.width,
                "height": enhanced_world.height,
                "climate": enhanced_world.climate.name,
                "locations": {}
            }
            
            for loc_id, location in enhanced_world.locations.items():
                # Convert location to dict
                loc_dict = {
                    "id": location.id,
                    "name": location.name,
                    "description": location.description,
                    "coordinates": location.coordinates,
                    "terrain": location.terrain.name if hasattr(location, 'terrain') else None,
                    "biome": location.biome if hasattr(location, 'biome') else None,
                    "pois": []
                }
                
                # Add POIs
                for poi in location.pois:
                    poi_dict = {
                        "id": poi.id,
                        "name": poi.name,
                        "poi_type": poi.poi_type.name,
                        "description": poi.description,
                        "coordinates": poi.coordinates
                    }
                    loc_dict["pois"].append(poi_dict)
                
                # Add magic profile
                if hasattr(location, 'magic_profile'):
                    loc_dict["magic_profile"] = {
                        "leyline_strength": location.magic_profile.leyline_strength,
                        "mana_flux_level": location.magic_profile.mana_flux_level.name,
                        "dominant_magic_aspects": [aspect.name for aspect in location.magic_profile.dominant_magic_aspects],
                        "environmental_decay_level": location.magic_profile.environmental_decay_level,
                        "allows_ritual_sites": location.magic_profile.allows_ritual_sites,
                        "historical_magic_events": location.magic_profile.historical_magic_events
                    }
                
                world_dict["locations"][loc_id] = loc_dict
            
            # Serialize to JSON
            json_str = json.dumps(world_dict, indent=2)
            
            # Verify JSON is valid
            json.loads(json_str)
            
            self.assertTrue(True, "World serialized successfully")
            
        except Exception as e:
            self.fail(f"Failed to serialize world: {e}")


if __name__ == "__main__":
    unittest.main()