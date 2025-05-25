"""
Magic-World Integration Tests

This module tests the integration between the magic system and the world generation system.
"""

import pytest
import random
from typing import Dict, List, Any

# Import core components when available
try:
    from game_engine.magic_system import (
        MagicSystem, MagicUser, LocationMagicProfile, Domain, DamageType
    )
    from magic_system.magic_world_integration import (
        MagicWorldIntegration, World, Location, POI, POIType
    )
    MAGIC_WORLD_AVAILABLE = True
except ImportError:
    MAGIC_WORLD_AVAILABLE = False

# Set a seed for consistent random results in tests
random.seed(42)


# Skip the entire module if dependencies aren't available
pytestmark = pytest.mark.skipif(
    not MAGIC_WORLD_AVAILABLE,
    reason="Magic world integration components not available"
)


class TestMagicWorldIntegration:
    """Tests for the integration between magic and world systems."""

    def test_world_enhancement(self, magic_world_integration, test_world):
        """Test that a world can be enhanced with magical features."""
        # Enhance the world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # Verify the world was enhanced
        assert enhanced_world is not None
        assert enhanced_world.id == test_world.id
        assert enhanced_world.name == test_world.name
        
        # Check that locations have magic profiles
        for location_id, location in enhanced_world.locations.items():
            assert hasattr(location, 'magic_profile')
            assert location.magic_profile is not None
    
    def test_leyline_generation(self, magic_world_integration, test_world):
        """Test that leylines are generated between locations."""
        # Enhance the world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # Get the leyline network
        leyline_network = magic_world_integration.get_leyline_network()
        
        # There should be some leylines in the network
        assert len(leyline_network) > 0
        
        # Check leyline strengths are within expected range
        for source_id, connections in leyline_network.items():
            for target_id, strength in connections.items():
                assert 0.0 <= strength <= 5.0
    
    def test_magical_hotspots(self, magic_world_integration, test_world):
        """Test that magical hotspots are identified in the world."""
        # Enhance the world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # Get the magical hotspots
        hotspots = magic_world_integration.get_magical_hotspots()
        
        # There should be at least one hotspot
        assert len(hotspots) > 0
        
        # Hotspots should be valid location IDs
        for hotspot_id in hotspots:
            assert hotspot_id in enhanced_world.locations
            
            # Hotspot locations should have high leyline strength
            location = enhanced_world.locations[hotspot_id]
            assert location.magic_profile.leyline_strength > 1.0
            
            # Hotspots should allow ritual sites
            assert location.magic_profile.allows_ritual_sites == True
    
    def test_magical_poi_generation(self, magic_world_integration, test_world):
        """Test that magical points of interest are generated in the world."""
        # Enhance the world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # Check if magical POIs were added to locations
        magical_pois_found = False
        magical_poi_types = [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]
        
        for location_id, location in enhanced_world.locations.items():
            # Check if this location has any magical POIs
            for poi in location.pois:
                if poi.poi_type in magical_poi_types:
                    magical_pois_found = True
                    
                    # POI should have a name and description
                    assert poi.name is not None and len(poi.name) > 0
                    assert poi.description is not None and len(poi.description) > 0
                    
                    # Coordinates should be near the location
                    poi_x, poi_y = poi.coordinates
                    loc_x, loc_y = location.coordinates
                    assert abs(poi_x - loc_x) <= 1.0
                    assert abs(poi_y - loc_y) <= 1.0
        
        # At least one magical POI should have been generated
        assert magical_pois_found
    
    def test_biome_magic_correlation(self, magic_world_integration, test_world):
        """Test that biomes influence the magic aspects of locations."""
        # Enhance the world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # Check biome-magic correlations
        for location_id, location in enhanced_world.locations.items():
            if hasattr(location, 'biome') and location.biome is not None:
                # Check if the magic aspects match expected biome correlations
                if location.biome == 'forest':
                    # Forest should have earth/life aspects
                    aspects = [aspect.name for aspect in location.magic_profile.dominant_magic_aspects]
                    assert any(aspect in ['EARTH', 'LIFE'] for aspect in aspects)
                
                elif location.biome == 'mountain':
                    # Mountain should have earth/air aspects
                    aspects = [aspect.name for aspect in location.magic_profile.dominant_magic_aspects]
                    assert any(aspect in ['EARTH', 'AIR'] for aspect in aspects)
    
    def test_location_magic_environmental_effects(self, magic_system, enhanced_world):
        """Test that location magic profiles generate appropriate environmental effects."""
        # Create a test character
        test_character = type('TestCharacter', (), {
            'current_health': 100,
            'max_health': 100,
            'magic_profile': MagicUser(
                character_id="test_character",
                has_mana_heart=True,
                mana_max=100,
                mana_current=50,
                mana_regeneration_rate=1.0
            )
        })
        
        # Test environmental effects in each location
        for location_id, location in enhanced_world.locations.items():
            # Apply environmental effects
            effects = location.magic_profile.apply_magical_environmental_effects(test_character)
            
            # Check that effects were applied
            assert effects is not None
            
            # In high magic areas, character should regenerate mana
            if location.magic_profile.mana_flux_level.name in ['HIGH', 'VERY_HIGH']:
                mana_regen_effects = [e for e in effects if e.get('effect_type') == 'mana_regeneration']
                assert len(mana_regen_effects) > 0
                
                # Check mana was actually regenerated
                assert mana_regen_effects[0].get('amount', 0) > 0


# Simple dummy test to ensure pytest discovers the module
class DummyTest:
    def test_dummy(self):
        assert True