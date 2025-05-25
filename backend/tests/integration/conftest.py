"""
Fixtures for integration tests.

This module provides fixtures that can be used across all integration tests.
"""

import pytest
import random
from typing import Dict, List, Any, Tuple

# Import core modules
from game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, MagicEffect, Domain, 
    DamageType, EffectType, MagicTier, LocationMagicProfile, 
    Enchantment, ItemMagicProfile, ManaFluxLevel
)

# Import integration modules
from game_engine.magic_combat_integration import (
    MagicalCombatManager, Combatant, CombatMove, MonsterMagicIntegration,
    CombatantType, MoveType
)
from magic_system.magic_world_integration import (
    MagicWorldIntegration, World, Location, POI, POIType,
    Terrain, Climate, MagicalMaterialWorldIntegration
)
from magic_system.magic_crafting_integration import (
    MagicCraftingIntegration, ItemEnchanter, MagicalItemCrafter, MagicalPotionBrewer,
    CraftingMaterial, EnchantmentRecipe, MagicalItemType
)

# Set random seed for reproducible tests
random.seed(42)


@pytest.fixture
def magic_system():
    """Create a magic system for testing."""
    return MagicSystem()


@pytest.fixture
def magic_world_integration(magic_system):
    """Create a magic world integration for testing."""
    return MagicWorldIntegration(magic_system)


@pytest.fixture
def magic_crafting_integration(magic_system):
    """Create a magic crafting integration for testing."""
    return MagicCraftingIntegration(magic_system)


@pytest.fixture
def combat_manager(magic_system):
    """Create a magical combat manager for testing."""
    return MagicalCombatManager(magic_system)


@pytest.fixture
def test_world():
    """Create a test world with multiple locations."""
    locations = {}
    
    # Create several locations with different terrains and biomes
    locations["forest_1"] = Location(
        id="forest_1",
        name="Deep Forest",
        description="A dense forest with ancient trees.",
        coordinates=(1, 1),
        terrain=Terrain.FLAT,
        pois=[],
        biome="forest"
    )
    
    locations["mountain_1"] = Location(
        id="mountain_1",
        name="High Peak",
        description="A tall mountain with snow-capped peaks.",
        coordinates=(5, 5),
        terrain=Terrain.MOUNTAINS,
        pois=[],
        biome="mountain"
    )
    
    locations["river_1"] = Location(
        id="river_1",
        name="Flowing River",
        description="A wide river cutting through the landscape.",
        coordinates=(3, 2),
        terrain=Terrain.RIVER,
        pois=[],
        biome="coastal"
    )
    
    locations["ruins_1"] = Location(
        id="ruins_1",
        name="Ancient Ruins",
        description="The crumbling remains of an ancient civilization.",
        coordinates=(2, 4),
        terrain=Terrain.HILLS,
        pois=[],
        biome="ruins"
    )
    
    locations["desert_1"] = Location(
        id="desert_1",
        name="Vast Desert",
        description="A sprawling desert with rolling sand dunes.",
        coordinates=(7, 2),
        terrain=Terrain.FLAT,
        pois=[],
        biome="desert"
    )
    
    # Create the world
    return World(
        id="test_world",
        name="Test World",
        width=10,
        height=10,
        locations=locations,
        climate=Climate.TEMPERATE
    )


@pytest.fixture
def enhanced_world(test_world, magic_world_integration):
    """Create an enhanced world with magical features."""
    return magic_world_integration.enhance_world_with_magic(test_world)


@pytest.fixture
def test_character_domains():
    """Create a list of domains for a test character."""
    return [Domain.ARCANE, Domain.ELEMENTAL, Domain.NATURAL]


@pytest.fixture
def magic_user():
    """Create a magic user for testing."""
    return MagicUser(
        id="test_user",
        name="Test Mage",
        level=5,
        mana_max=100,
        mana_current=100,
        primary_domains=[Domain.ARCANE],
        secondary_domains=[Domain.ELEMENTAL, Domain.NATURAL],
        known_spells={"fireball", "arcane_missile", "healing_touch"},
        magic_skills={
            "spellcasting": 5,
            "concentration": 4,
            "magical_knowledge": 3,
            "mana_control": 4
        }
    )


@pytest.fixture
def test_spell():
    """Create a test spell."""
    return Spell(
        id="test_fireball",
        name="Fireball",
        description="A ball of fire that explodes on impact.",
        domains=[Domain.ELEMENTAL],
        damage_types=[DamageType.FIRE],
        effect_types=[EffectType.DAMAGE],
        mana_cost=15,
        casting_time=1.5,
        cooldown=3.0,
        base_power=10.0,
        level_req=3,
        tier=MagicTier.MODERATE,
        targeting_type="area",
        range_max=20.0,
        duration=0.0,
        components=["verbal", "somatic"],
        tags=["fire", "explosion", "area"]
    )


@pytest.fixture
def location_magic_profile():
    """Create a location magic profile for testing."""
    return LocationMagicProfile(
        location_id="test_location",
        leyline_strength=0.7,
        mana_flux_level=ManaFluxLevel.HIGH,
        dominant_magic_aspects=[Domain.ARCANE, Domain.ELEMENTAL],
        allows_ritual_sites=True,
        magical_pois=[
            {"id": "magical_font", "type": "ARCANE_FONT", "power": 0.8}
        ],
        magical_resources=[
            {"id": "mana_crystal", "quantity": 5, "rarity": "uncommon"},
            {"id": "fire_essence", "quantity": 3, "rarity": "uncommon"}
        ]
    )


@pytest.fixture
def test_combatant(magic_user):
    """Create a test combatant with magic capabilities."""
    return Combatant(
        id="test_player",
        name="Test Player",
        combatant_type=CombatantType.PLAYER,
        level=5,
        max_health=100,
        current_health=100,
        stats={
            "strength": 10,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 16,
            "wisdom": 14,
            "charisma": 12,
            "perception": 13
        },
        resistances={DamageType.FIRE: 0.2},
        weaknesses={DamageType.ICE: 0.2},
        immunities=set(),
        magic_profile=magic_user
    )


@pytest.fixture
def test_monster():
    """Create a test monster."""
    return Combatant(
        id="test_monster",
        name="Test Monster",
        combatant_type=CombatantType.MONSTER,
        level=4,
        max_health=80,
        current_health=80,
        stats={
            "strength": 14,
            "dexterity": 10,
            "constitution": 12,
            "intelligence": 8,
            "wisdom": 10,
            "charisma": 8,
            "perception": 12
        },
        resistances={DamageType.PHYSICAL: 0.1},
        weaknesses={DamageType.FIRE: 0.3},
        immunities=set(),
        magic_profile=None  # Will be enhanced with magic if needed
    )


@pytest.fixture
def available_materials():
    """Create a dictionary of available crafting materials."""
    return {
        "mana_crystal": 5,
        "fire_essence": 3,
        "wood": 10,
        "hardwood": 5,
        "silver": 3,
        "gold": 2,
        "arcane_dust": 4,
        "mind_crystal": 2,
        "shadow_residue": 2,
        "divine_light": 1,
        "elemental_essence": 3,
        "pure_water": 10,
        "healing_herb": 8,
        "clarity_herb": 4,
        "frost_extract": 3,
        "ghost_flower": 1
    }


@pytest.fixture
def material_world_integration(magic_world_integration):
    """Create a magical material world integration for testing."""
    return MagicalMaterialWorldIntegration(magic_world_integration)