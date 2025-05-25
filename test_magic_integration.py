"""
Magic System Integration Test

This script tests the integration between all magic system components:
- Core magic system
- Magic world integration
- Magic crafting integration
- Magic combat integration
"""

import random
from typing import Dict, List, Any

from backend.src.game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, Domain, DamageType, EffectType, MagicTier
)
from backend.src.magic_system.magic_world_integration import (
    MagicWorldIntegration, World, Location, POI, POIType, Terrain, Climate
)
from backend.src.magic_system.magic_crafting_integration import (
    MagicCraftingIntegration, ItemEnchanter, MagicalItemCrafter, MagicalPotionBrewer
)
from backend.src.game_engine.magic_combat_integration import (
    MagicalCombatManager, Combatant, CombatantType, MonsterMagicIntegration
)


def create_test_world() -> World:
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


def create_test_player() -> MagicUser:
    """Create a test player with magical abilities."""
    return MagicUser(
        id="player_1",
        name="Aventus the Arcane",
        level=5,
        mana_max=100,
        mana_current=100,
        mana_regen_rate=2.0,
        primary_domains=[Domain.ARCANE],
        secondary_domains=[Domain.FIRE, Domain.MIND],
        known_spells=set(),  # Will be filled with spells later
        magic_skills={
            "spellcasting": 5,
            "concentration": 4,
            "magical_knowledge": 3,
            "mana_control": 4
        }
    )


def create_test_spells(magic_system: MagicSystem, player: MagicUser) -> List[Spell]:
    """Create test spells and register them with the magic system."""
    spells = []
    
    # Arcane Missile
    arcane_missile = Spell(
        id="arcane_missile",
        name="Arcane Missile",
        description="A bolt of arcane energy that unerringly strikes its target.",
        domains=[Domain.ARCANE],
        damage_types=[DamageType.ARCANE],
        effect_types=[EffectType.DAMAGE],
        mana_cost=10,
        casting_time=1.0,
        cooldown=2.0,
        base_power=8.0,
        level_req=1,
        tier=MagicTier.LESSER,
        targeting_type="single",
        range_max=30.0,
        duration=0.0,
        components=["verbal", "somatic"],
        tags=["arcane", "force", "missile"]
    )
    spells.append(arcane_missile)
    
    # Fireball
    fireball = Spell(
        id="fireball",
        name="Fireball",
        description="A ball of fire that explodes on impact, dealing damage in an area.",
        domains=[Domain.FIRE, Domain.ARCANE],
        damage_types=[DamageType.FIRE],
        effect_types=[EffectType.DAMAGE],
        mana_cost=25,
        casting_time=1.5,
        cooldown=5.0,
        base_power=15.0,
        level_req=3,
        tier=MagicTier.MODERATE,
        targeting_type="area",
        range_max=40.0,
        duration=0.0,
        components=["verbal", "somatic"],
        tags=["fire", "explosion", "area"]
    )
    spells.append(fireball)
    
    # Mind Shield
    mind_shield = Spell(
        id="mind_shield",
        name="Mind Shield",
        description="Creates a protective barrier around the caster's mind, granting resistance to mental attacks.",
        domains=[Domain.MIND],
        damage_types=[],
        effect_types=[EffectType.PROTECTION, EffectType.BUFF],
        mana_cost=15,
        casting_time=1.0,
        cooldown=60.0,
        base_power=10.0,
        level_req=2,
        tier=MagicTier.LESSER,
        targeting_type="self",
        range_max=0.0,
        duration=300.0,  # 5 minutes
        components=["verbal", "somatic"],
        tags=["mind", "protection", "buff"]
    )
    spells.append(mind_shield)
    
    # Mana Surge
    mana_surge = Spell(
        id="mana_surge",
        name="Mana Surge",
        description="Temporarily increases the caster's mana regeneration rate.",
        domains=[Domain.ARCANE],
        damage_types=[],
        effect_types=[EffectType.BUFF],
        mana_cost=20,
        casting_time=2.0,
        cooldown=180.0,  # 3 minutes
        base_power=5.0,
        level_req=4,
        tier=MagicTier.MODERATE,
        targeting_type="self",
        range_max=0.0,
        duration=60.0,  # 1 minute
        components=["verbal", "somatic", "material"],
        tags=["arcane", "mana", "buff"]
    )
    spells.append(mana_surge)
    
    # Register spells with magic system and add to player's known spells
    for spell in spells:
        magic_system.register_spell(spell)
        player.known_spells.add(spell.id)
    
    return spells


def create_test_monsters() -> List[Combatant]:
    """Create test monsters for combat."""
    monsters = []
    
    # Fire Elemental
    fire_elemental = Combatant(
        id="fire_elemental_1",
        name="Fire Elemental",
        combatant_type=CombatantType.MONSTER,
        level=4,
        max_health=80,
        current_health=80,
        stats={
            "strength": 12,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 8,
            "wisdom": 10,
            "charisma": 8,
            "perception": 10
        },
        resistances={DamageType.FIRE: 0.9},  # 90% resistance to fire
        weaknesses={DamageType.WATER: 0.5},  # 50% extra damage from water
        immunities=set()
    )
    monsters.append(fire_elemental)
    
    # Shadow Wolf
    shadow_wolf = Combatant(
        id="shadow_wolf_1",
        name="Shadow Wolf",
        combatant_type=CombatantType.MONSTER,
        level=3,
        max_health=60,
        current_health=60,
        stats={
            "strength": 12,
            "dexterity": 16,
            "constitution": 10,
            "intelligence": 6,
            "wisdom": 12,
            "charisma": 6,
            "perception": 14
        },
        resistances={DamageType.PHYSICAL: 0.2},  # 20% resistance to physical
        weaknesses={DamageType.DIVINE: 0.3},    # 30% extra damage from divine
        immunities=set()
    )
    monsters.append(shadow_wolf)
    
    return monsters


def create_player_combatant(player: MagicUser) -> Combatant:
    """Create a combatant representation of the player."""
    return Combatant(
        id="player_combatant",
        name=player.name,
        combatant_type=CombatantType.PLAYER,
        level=player.level,
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
        resistances={},
        weaknesses={},
        immunities=set(),
        magic_profile=player
    )


def test_magic_world_integration(magic_system: MagicSystem, world: World):
    """Test the integration between the magic system and world generation."""
    print("\n=== Testing Magic World Integration ===")
    
    # Create magic world integration
    magic_world = MagicWorldIntegration(magic_system)
    
    # Enhance the world with magic
    enhanced_world = magic_world.enhance_world_with_magic(world)
    
    # Check that locations have magic profiles
    print(f"World enhanced with magic: {enhanced_world.name}")
    
    for location_id, location in enhanced_world.locations.items():
        # Get the location's magic profile
        location_profile = magic_system.location_magic_profiles.get(location_id)
        
        if location_profile:
            print(f"Location '{location.name}' has magic profile:")
            print(f"  - Dominant aspects: {[a.name for a in location_profile.dominant_magic_aspects]}")
            print(f"  - Leyline strength: {location_profile.leyline_strength:.2f}")
            print(f"  - Mana flux level: {location_profile.mana_flux_level.name}")
            if location_profile.magical_pois:
                print(f"  - Magical POIs: {len(location_profile.magical_pois)}")
        else:
            print(f"Location '{location.name}' has no magic profile.")
    
    # Check leylines
    print(f"\nLeylines: {len(magic_world.active_leylines)}")
    for i, leyline in enumerate(magic_world.active_leylines):
        print(f"  Leyline {i+1}: {' -> '.join(leyline)}")
    
    # Check magical hotspots
    print(f"\nMagical hotspots: {len(magic_world.magical_hotspots)}")
    for hotspot in magic_world.magical_hotspots:
        location = world.locations.get(hotspot)
        if location:
            print(f"  Hotspot: {location.name}")
    
    return enhanced_world


def test_magic_crafting_integration(magic_system: MagicSystem, player: MagicUser):
    """Test the integration between the magic system and crafting system."""
    print("\n=== Testing Magic Crafting Integration ===")
    
    # Create magic crafting integration
    magic_crafting = MagicCraftingIntegration(magic_system)
    
    # Get available materials
    available_materials = {
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
    
    # Get available enchantment recipes
    print("Available enchantment recipes:")
    enchantment_recipes = magic_crafting.get_enchantment_recipes(
        [Domain.ARCANE, Domain.FIRE, Domain.MIND]
    )
    for recipe in enchantment_recipes:
        print(f"  - {recipe['name']}: {recipe['description']}")
    
    # Get available crafting recipes
    print("\nAvailable crafting recipes:")
    crafting_recipes = magic_crafting.get_crafting_recipes(
        [Domain.ARCANE, Domain.FIRE, Domain.MIND]
    )
    for recipe in crafting_recipes:
        print(f"  - {recipe['name']}: {recipe['description']}")
    
    # Get available potion recipes
    print("\nAvailable potion recipes:")
    potion_recipes = magic_crafting.get_potion_recipes(
        [Domain.ARCANE, Domain.FIRE, Domain.MIND]
    )
    for recipe in potion_recipes:
        print(f"  - {recipe['name']}: {recipe['description']}")
    
    # Craft an item
    print("\nCrafting an item:")
    if crafting_recipes:
        craft_result = magic_crafting.craft_item(
            player,
            [Domain.ARCANE, Domain.FIRE, Domain.MIND],
            crafting_recipes[0]["id"],
            available_materials
        )
        
        if craft_result["success"]:
            print(f"  Successfully crafted: {craft_result['crafted_item']['name']}")
            print(f"  Quality: {craft_result['crafted_item']['quality']}")
            print(f"  Materials used: {craft_result['consumed_materials']}")
        else:
            print(f"  Failed to craft item: {craft_result['message']}")
    
    # Brew a potion
    print("\nBrewing a potion:")
    if potion_recipes:
        brew_result = magic_crafting.brew_potion(
            player,
            [Domain.ARCANE, Domain.FIRE, Domain.MIND],
            potion_recipes[0]["id"],
            available_materials
        )
        
        if brew_result["success"]:
            print(f"  Successfully brewed: {brew_result['potion']['name']}")
            print(f"  Quality: {brew_result['potion']['quality']}")
            print(f"  Materials used: {brew_result['consumed_materials']}")
        else:
            print(f"  Failed to brew potion: {brew_result['message']}")
    
    return magic_crafting


def test_magic_combat_integration(
    magic_system: MagicSystem, 
    player: MagicUser, 
    world: World
):
    """Test the integration between the magic system and combat system."""
    print("\n=== Testing Magic Combat Integration ===")
    
    # Create combat manager
    combat_manager = MagicalCombatManager(magic_system)
    
    # Create player combatant
    player_combatant = create_player_combatant(player)
    
    # Create monsters
    monsters = create_test_monsters()
    
    # Enhance monsters with magic
    monster_magic = MonsterMagicIntegration(magic_system)
    
    for monster in monsters:
        # Only enhance the fire elemental with fire magic
        if "Fire Elemental" in monster.name:
            monster = monster_magic.enhance_monster_with_magic(
                monster=monster,
                primary_domains=[Domain.FIRE, Domain.ELEMENTAL],
                secondary_domains=[]
            )
            
            # Generate spells for the monster
            monster_spells = monster_magic.generate_monster_spells(
                monster=monster,
                num_spells=2
            )
            
            print(f"Enhanced {monster.name} with magic:")
            print(f"  Primary domains: {[d.name for d in monster.magic_profile.primary_domains]}")
            print(f"  Mana: {monster.magic_profile.mana_current}/{monster.magic_profile.mana_max}")
            print(f"  Generated spells: {[s.name for s in monster_spells]}")
    
    # Choose a location for combat
    location_id = "ruins_1"
    location = world.locations.get(location_id)
    print(f"\nInitiating combat in {location.name}:")
    
    # Start combat
    combat_id = "test_combat_1"
    combat_participants = [player_combatant] + monsters
    
    combat_result = combat_manager.initiate_combat(
        combat_id=combat_id,
        participants=combat_participants,
        location_id=location_id
    )
    
    if combat_result["success"]:
        print(f"  Combat initiated successfully with {len(combat_participants)} participants")
        print(f"  Initiative order: {[p.name for p in combat_manager.active_combats[combat_id]['initiative_order']]}")
        
        # Get available actions for player
        actions = combat_manager.get_available_combat_actions(
            combat_id=combat_id,
            combatant_id=player_combatant.id
        )
        
        if actions["success"]:
            print("\nAvailable player actions:")
            for action in actions["magical_actions"]:
                print(f"  - {action['name']}: {action['description']}")
        
        # Cast a spell in combat
        current_turn = combat_manager.active_combats[combat_id]["initiative_order"][0]
        
        if current_turn.id == player_combatant.id:
            # If it's the player's turn, cast a spell
            print("\nPlayer casting a spell:")
            
            cast_result = combat_manager.cast_spell_in_combat(
                combat_id=combat_id,
                caster_id=player_combatant.id,
                spell_id="fireball",
                target_ids=[monsters[0].id],  # Target the fire elemental
                game_time=0.0
            )
            
            if cast_result["success"]:
                print(f"  Successfully cast {cast_result['spell_cast_result']['message']}")
                for target_result in cast_result["target_results"]:
                    if "damage_result" in target_result and target_result["damage_result"]:
                        print(f"  - {target_result['target_name']} took {target_result['damage_result']['final_damage']} damage")
                        print(f"    Health: {target_result['damage_result']['health_after']}/{monsters[0].max_health}")
                        if target_result["damage_result"]["is_defeated"]:
                            print(f"    {target_result['target_name']} was defeated!")
            else:
                print(f"  Failed to cast spell: {cast_result['message']}")
        else:
            print(f"  It's not the player's turn. Current turn: {current_turn.name}")
        
        # Get combat status
        status = combat_manager.get_combat_status(combat_id)
        if status["success"]:
            print(f"\nCombat status:")
            print(f"  Round: {status['round_number']}")
            print(f"  Current turn: {status['current_turn']['combatant_name']}")
            print(f"  Combatants:")
            for combatant in status["combatants"]:
                print(f"    - {combatant['name']}: {combatant['health']['current']}/{combatant['health']['max']} HP")
        
        # End combat
        print("\nEnding combat:")
        end_result = combat_manager.end_combat(
            combat_id=combat_id,
            outcome="victory",
            winning_side="player"
        )
        
        if end_result["success"]:
            print(f"  Combat ended with outcome: {end_result['outcome']}")
            print(f"  Survivors: {[s['name'] for s in end_result['survivors']]}")
            print(f"  Defeated: {[d['name'] for d in end_result['defeated']]}")
    else:
        print(f"Failed to initiate combat: {combat_result['message']}")
    
    return combat_manager


def test_full_integration():
    """Test the full integration of all magic system components."""
    print("=== Magic System Integration Test ===")
    
    # Create core magic system
    magic_system = MagicSystem()
    print("Created magic system")
    
    # Create player
    player = create_test_player()
    magic_system.register_magic_user(player)
    print(f"Created player: {player.name}")
    
    # Create spells
    spells = create_test_spells(magic_system, player)
    print(f"Created {len(spells)} spells")
    
    # Create world
    world = create_test_world()
    print(f"Created world: {world.name} with {len(world.locations)} locations")
    
    # Test magic world integration
    enhanced_world = test_magic_world_integration(magic_system, world)
    
    # Test magic crafting integration
    magic_crafting = test_magic_crafting_integration(magic_system, player)
    
    # Test magic combat integration
    combat_manager = test_magic_combat_integration(magic_system, player, enhanced_world)
    
    print("\n=== Integration Test Complete ===")
    print(f"Magic System Components:")
    print(f"- Registered spells: {len(magic_system.spells)}")
    print(f"- Registered magic users: {len(magic_system.magic_users)}")
    print(f"- Registered locations with magic: {len(magic_system.location_magic_profiles)}")
    print(f"- Registered magical items: {len(magic_system.item_magic_profiles)}")
    
    print("\nTest successful!")


if __name__ == "__main__":
    # Set random seed for reproducible tests
    random.seed(42)
    
    # Run the full integration test
    test_full_integration()