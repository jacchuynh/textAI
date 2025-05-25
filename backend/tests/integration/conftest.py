"""
Shared fixtures for integration tests

This file contains pytest fixtures that can be shared across multiple test modules.
These fixtures provide common test objects like test characters, worlds, and system instances.
"""

import pytest
import os
import sys
import random
from typing import Dict, List, Any, Optional

# Set the random seed for reproducible tests
random.seed(42)

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, os.path.join(parent_dir, "src"))

# Try to import required modules, skip tests if not available
try:
    # Import magic system
    from game_engine.magic_system import (
        MagicSystem, MagicUser, Spell, Domain, DamageType,
        MagicTier, MagicSource, EffectType, TargetType
    )
    
    # Import combat system
    from game_engine.enhanced_combat.combat_system_core import (
        Combatant, CombatMove, MoveType, Status
    )
    
    # Import world generation
    from world_generation.world_model import (
        World, Location, POI, Coordinates, Climate, Terrain, POIType
    )
    
    # Flag that imports succeeded
    IMPORTS_SUCCEEDED = True
except ImportError:
    IMPORTS_SUCCEEDED = False

# Only define fixtures if imports succeeded
if IMPORTS_SUCCEEDED:
    @pytest.fixture
    def magic_system():
        """Fixture providing a MagicSystem instance."""
        return MagicSystem()
    
    @pytest.fixture
    def test_character():
        """Fixture providing a test character with balanced domains."""
        domains = {
            Domain.BODY: 3,
            Domain.MIND: 4,
            Domain.CRAFT: 3,
            Domain.AWARENESS: 3,
            Domain.SOCIAL: 2,
            Domain.AUTHORITY: 2,
            Domain.SPIRIT: 4,
            Domain.FIRE: 2,
            Domain.WATER: 0,
            Domain.EARTH: 0,
            Domain.AIR: 0,
            Domain.LIGHT: 0,
            Domain.DARKNESS: 0
        }
        
        return Combatant(
            name="Test Mage",
            domains=domains,
            max_health=100,
            current_health=100,
            max_stamina=50,
            current_stamina=50,
            max_focus=60,
            current_focus=60,
            max_spirit=70,
            current_spirit=70
        )
    
    @pytest.fixture
    def test_monster():
        """Fixture providing a test monster with elemental affinity."""
        domains = {
            Domain.BODY: 4,
            Domain.MIND: 2,
            Domain.CRAFT: 1,
            Domain.AWARENESS: 3,
            Domain.SOCIAL: 1,
            Domain.AUTHORITY: 2,
            Domain.SPIRIT: 2,
            Domain.FIRE: 4,  # Fire-based monster
            Domain.WATER: 0,
            Domain.EARTH: 0,
            Domain.AIR: 0,
            Domain.LIGHT: 0,
            Domain.DARKNESS: 0
        }
        
        return Combatant(
            name="Ember Elemental",
            domains=domains,
            max_health=120,
            current_health=120,
            max_stamina=40,
            current_stamina=40,
            max_focus=30,
            current_focus=30,
            max_spirit=50,
            current_spirit=50
        )
    
    @pytest.fixture
    def test_combat_moves():
        """Fixture providing basic combat moves for testing."""
        return [
            CombatMove(
                name="Basic Attack",
                description="A simple physical attack",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                base_damage=5,
                stamina_cost=2,
                focus_cost=0,
                spirit_cost=0
            ),
            CombatMove(
                name="Defensive Stance",
                description="A defensive position that reduces incoming damage",
                move_type=MoveType.DEFEND,
                domains=[Domain.BODY, Domain.AWARENESS],
                base_damage=0,
                stamina_cost=3,
                focus_cost=0,
                spirit_cost=0
            ),
            CombatMove(
                name="Tactical Assessment",
                description="Analyze the opponent for weaknesses",
                move_type=MoveType.FOCUS,
                domains=[Domain.MIND, Domain.AWARENESS],
                base_damage=0,
                stamina_cost=0,
                focus_cost=3,
                spirit_cost=0
            )
        ]
    
    @pytest.fixture
    def test_world():
        """Fixture providing a test world with diverse biomes."""
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
    
    @pytest.fixture
    def test_magical_materials():
        """Fixture providing test magical materials for crafting."""
        return {
            "material_ley_crystal": 5,
            "material_crimson_residue": 5,
            "material_spiritbloom": 5,
            "material_void_essence": 3,
            "material_starlight_fragment": 2,
            "Charcoal": 10,
            "Red mushroom": 5,
            "Honey": 5,
            "Spring water": 5,
            "Weapon": 2,
            "Armor": 1,
            "Jewelry": 1
        }