"""
Integration Test Fixtures

This module provides fixtures for integration tests.
"""

import os
import sys
import pytest
from typing import Dict, List, Any, Optional

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import core components when available
try:
    from game_engine.magic_system import (
        MagicSystem, MagicUser, LocationMagicProfile, Domain, 
        MagicTier, DamageType, Spell
    )
    MAGIC_SYSTEM_AVAILABLE = True
except ImportError:
    MAGIC_SYSTEM_AVAILABLE = False

try:
    from magic_system.magic_world_integration import (
        MagicWorldIntegration, World, Location, POI, POIType
    )
    MAGIC_WORLD_AVAILABLE = True
except ImportError:
    MAGIC_WORLD_AVAILABLE = False

try:
    from game_engine.magic_combat_integration import (
        MagicalCombatManager, Combatant, CombatMove, MonsterMagicIntegration
    )
    MAGIC_COMBAT_AVAILABLE = True
except ImportError:
    MAGIC_COMBAT_AVAILABLE = False

try:
    from magic_system.magic_crafting_integration import (
        MagicCraftingIntegration, ItemEnchanter, MagicalItemCrafter, MagicalPotionBrewer
    )
    MAGIC_CRAFTING_AVAILABLE = True
except ImportError:
    MAGIC_CRAFTING_AVAILABLE = False


@pytest.fixture
def magic_system():
    """Fixture for the magic system."""
    if not MAGIC_SYSTEM_AVAILABLE:
        pytest.skip("Magic system not available")
    return MagicSystem()


@pytest.fixture
def test_character_domains():
    """Fixture for test character domains."""
    if not MAGIC_SYSTEM_AVAILABLE:
        pytest.skip("Magic system not available")
    return {
        Domain.BODY: 3,
        Domain.MIND: 4,
        Domain.CRAFT: 3,
        Domain.AWARENESS: 3,
        Domain.SOCIAL: 2,
        Domain.AUTHORITY: 2,
        Domain.SPIRIT: 4,
        Domain.FIRE: 3,
        Domain.WATER: 2,
        Domain.EARTH: 2,
        Domain.AIR: 1,
        Domain.LIGHT: 1,
        Domain.DARKNESS: 0
    }


@pytest.fixture
def magic_user(magic_system, test_character_domains):
    """Fixture for a magic user."""
    if not MAGIC_SYSTEM_AVAILABLE:
        pytest.skip("Magic system not available")
    magic_user = magic_system.initialize_magic_user(test_character_domains)
    # Learn a few spells for testing
    magic_user.learn_spell("spell_fire_bolt")
    magic_user.learn_spell("spell_arcane_shield")
    if "spell_communion_with_nature" in magic_system._rituals:
        magic_user.learn_ritual("ritual_commune_with_nature")
    return magic_user


@pytest.fixture
def test_location_description():
    """Fixture for a test location description."""
    return """
    A mystical forest clearing with ancient standing stones. The air shimmers with magical energy,
    and a strong leyline runs through the center of the area. The stones are covered in arcane
    runes that glow faintly in the moonlight. The forest around the clearing is ancient and seems
    to whisper with ancient wisdom.
    """


@pytest.fixture
def location_magic_profile(magic_system, test_location_description):
    """Fixture for a location magic profile."""
    if not MAGIC_SYSTEM_AVAILABLE:
        pytest.skip("Magic system not available")
    return magic_system.initialize_location_magic(test_location_description)


@pytest.fixture
def test_world():
    """Fixture for a test world."""
    if not MAGIC_WORLD_AVAILABLE:
        pytest.skip("Magic world integration not available")
    
    # Create some POIs
    forest_shrine = POI(
        id="poi_1",
        name="Ancient Forest Shrine",
        poi_type=POIType.SHRINE,
        description="A shrine dedicated to the forest spirits.",
        coordinates=(1, 1)
    )
    
    mountain_cave = POI(
        id="poi_2",
        name="Crystal Cave",
        poi_type=POIType.CAVE,
        description="A cave filled with glowing crystals.",
        coordinates=(2, 2)
    )
    
    # Create some locations
    forest_location = Location(
        id="loc_1",
        name="Mystic Forest",
        description="An ancient forest filled with magical energy.",
        coordinates=(1, 1),
        terrain="forest",
        pois=[forest_shrine],
        biome="forest"
    )
    
    mountain_location = Location(
        id="loc_2",
        name="Crystal Mountains",
        description="Towering mountains with veins of magical crystals.",
        coordinates=(2, 2),
        terrain="mountain",
        pois=[mountain_cave],
        biome="mountain"
    )
    
    # Create a world
    locations = {
        "loc_1": forest_location,
        "loc_2": mountain_location
    }
    
    return World(
        id="world_1",
        name="Test World",
        width=10,
        height=10,
        locations=locations,
        climate="temperate"
    )


@pytest.fixture
def magic_world_integration(magic_system):
    """Fixture for a magic world integration."""
    if not MAGIC_WORLD_AVAILABLE:
        pytest.skip("Magic world integration not available")
    return MagicWorldIntegration()


@pytest.fixture
def enhanced_world(magic_world_integration, test_world):
    """Fixture for a world enhanced with magic."""
    if not MAGIC_WORLD_AVAILABLE:
        pytest.skip("Magic world integration not available")
    return magic_world_integration.enhance_world_with_magic(test_world)


@pytest.fixture
def test_combatant():
    """Fixture for a test combatant."""
    if not MAGIC_COMBAT_AVAILABLE:
        pytest.skip("Magic combat integration not available")
    
    # Create a test combatant
    return Combatant(
        name="Test Fighter",
        domains={
            Domain.BODY: 3,
            Domain.MIND: 2,
            Domain.CRAFT: 2,
            Domain.AWARENESS: 3,
            Domain.SOCIAL: 2,
            Domain.AUTHORITY: 1,
            Domain.SPIRIT: 2,
            Domain.FIRE: 2,
            Domain.WATER: 1,
            Domain.EARTH: 1,
            Domain.AIR: 0,
            Domain.LIGHT: 0,
            Domain.DARKNESS: 0
        },
        max_health=100,
        current_health=100,
        max_stamina=50,
        current_stamina=50,
        max_focus=50,
        current_focus=50,
        max_spirit=50,
        current_spirit=50
    )


@pytest.fixture
def test_monster():
    """Fixture for a test monster."""
    if not MAGIC_COMBAT_AVAILABLE:
        pytest.skip("Magic combat integration not available")
    
    # Create a test monster
    return Combatant(
        name="Fire Elemental",
        domains={
            Domain.BODY: 2,
            Domain.MIND: 1,
            Domain.CRAFT: 0,
            Domain.AWARENESS: 2,
            Domain.SOCIAL: 0,
            Domain.AUTHORITY: 0,
            Domain.SPIRIT: 3,
            Domain.FIRE: 4,
            Domain.WATER: 0,
            Domain.EARTH: 1,
            Domain.AIR: 1,
            Domain.LIGHT: 0,
            Domain.DARKNESS: 0
        },
        max_health=80,
        current_health=80,
        max_stamina=40,
        current_stamina=40,
        max_focus=30,
        current_focus=30,
        max_spirit=40,
        current_spirit=40
    )


@pytest.fixture
def combat_manager(magic_system):
    """Fixture for a combat manager."""
    if not MAGIC_COMBAT_AVAILABLE:
        pytest.skip("Magic combat integration not available")
    return MagicalCombatManager(magic_system)


@pytest.fixture
def magic_crafting_integration(magic_system):
    """Fixture for a magic crafting integration."""
    if not MAGIC_CRAFTING_AVAILABLE:
        pytest.skip("Magic crafting integration not available")
    return MagicCraftingIntegration(magic_system)


@pytest.fixture
def available_materials():
    """Fixture for available crafting materials."""
    if not MAGIC_CRAFTING_AVAILABLE:
        pytest.skip("Magic crafting integration not available")
    
    # Return a dict of material IDs to quantities
    return {
        "fire_essence": 5,
        "resonant_crystal": 3,
        "dragon_scale": 2,
        "arcane_dust": 10,
        "moonstone": 3,
        "ethereal_silk": 3,
        "mana_crystal": 4,
        "celestial_prism": 1,
        "wooden_shaft": 5,
        "leather_binding": 3,
        "healing_herb": 6,
        "pure_water": 5,
        "alchemical_catalyst": 4
    }