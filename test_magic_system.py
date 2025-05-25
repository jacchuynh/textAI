#!/usr/bin/env python3
"""
Magic System Integration Test Script

This script demonstrates the integration of the magic system with the
existing domain, combat, and crafting systems.
"""

import sys
import random
from typing import Dict, List, Any, Optional, Tuple

# Add backend directory to path
sys.path.append("backend/src")

# Import magic system modules
from game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, Ritual, Enchantment,
    MagicTier, MagicSource, EffectType, TargetType, DomainRequirement,
    Domain, DamageType, MagicalEffect, ItemMagicProfile
)

# Import combat system modules
from game_engine.enhanced_combat.combat_system_core import (
    Combatant, CombatMove, MoveType, Status
)

# Import magic combat integration
from game_engine.magic_combat_integration import (
    MagicalCombatManager, MonsterMagicIntegration
)

# Import magic crafting integration
from game_engine.magic_crafting_integration import (
    MagicalCraftingService, EnchantingRecipe, PotionRecipe
)


def create_test_character() -> Combatant:
    """Create a test character with balanced domains"""
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


def create_test_monster() -> Combatant:
    """Create a test monster with elemental affinity"""
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


def create_test_combat_moves() -> List[CombatMove]:
    """Create basic combat moves for testing"""
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


def test_magic_system_basics():
    """Test basic magic system functionality"""
    print("\n=== Testing Magic System Basics ===")
    
    # Create magic system
    magic_system = MagicSystem()
    
    # Create a character with domains
    character = create_test_character()
    print(f"Created character: {character.name}")
    print("Domains:", ", ".join([f"{domain.name}: {value}" for domain, value in character.domains.items()]))
    
    # Initialize magic user profile
    magic_profile = magic_system.initialize_magic_user(character.domains)
    print("\nInitialized Magic Profile:")
    print(f"Has Mana Heart: {magic_profile.has_mana_heart}")
    print(f"Mana: {magic_profile.mana_current}/{magic_profile.mana_max}")
    print(f"Mana Regeneration: {magic_profile.mana_regeneration_rate}/second")
    print(f"Ley Energy Sensitivity: {magic_profile.ley_energy_sensitivity}")
    print(f"Attunements: {', '.join(magic_profile.attunements) if magic_profile.attunements else 'None'}")
    
    # Develop mana heart if not already developed
    if not magic_profile.has_mana_heart:
        print("\nDeveloping Mana Heart...")
        result = magic_system.develop_mana_heart("test_character", magic_profile)
        print(f"Result: {result['message']}")
        print(f"New Mana: {magic_profile.mana_current}/{magic_profile.mana_max}")
    
    # Get available spells
    available_spells = magic_system.get_available_spells(magic_profile)
    print("\nAvailable Spells by Tier:")
    
    for tier, spells in available_spells.items():
        print(f"\n{tier.name} Tier Spells:")
        for spell in spells:
            status = "Known" if spell["known"] else "Unknown"
            can_cast = "Can Cast" if spell["can_cast"] else f"Cannot Cast: {spell['reason']}"
            print(f"  - {spell['name']} ({status}, {can_cast})")
    
    # Learn a spell
    if not magic_profile.known_spells:
        print("\nLearning a spell...")
        # Find a spell we can potentially learn
        learnable_spell = None
        for tier, spells in available_spells.items():
            for spell in spells:
                if not spell["known"] and "mana heart" not in spell["reason"].lower():
                    learnable_spell = spell
                    break
            if learnable_spell:
                break
        
        if learnable_spell:
            result = magic_system.learn_spell_from_study("test_character", learnable_spell["id"], magic_profile)
            print(f"Result: {result['message']}")
        else:
            print("No learnable spells found.")
    
    # Get location magic
    print("\nInitializing location magic...")
    location_desc = "A forested grove with a small shrine. Ancient leylines converge here, creating a powerful nexus of magical energy."
    location_magic = magic_system.initialize_location_magic(location_desc)
    
    print(f"Leyline Strength: {location_magic.leyline_strength}/5")
    print(f"Mana Flux Level: {location_magic.mana_flux_level.name}")
    print(f"Dominant Aspects: {', '.join([aspect.name for aspect in location_magic.dominant_magic_aspects]) if location_magic.dominant_magic_aspects else 'None'}")
    print(f"Allows Rituals: {location_magic.allows_ritual_sites}")
    
    # Draw from leylines
    print("\nDrawing energy from leylines...")
    amount_drawn = magic_profile.draw_from_leyline(location_magic.leyline_strength, 10)
    print(f"Drew {amount_drawn} ley energy")
    print(f"Current Ley Energy: {magic_profile.current_ley_energy}")
    
    # Create a magic item
    print("\nCreating a magic item...")
    item_magic = magic_system.create_magic_item("test_item", "enchant_flaming_weapon")
    print(f"Item enchanted: {item_magic.is_enchanted}")
    print(f"Enchantment ID: {item_magic.enchantment_id}")


def test_magic_combat_integration():
    """Test integration of magic with combat system"""
    print("\n=== Testing Magic Combat Integration ===")
    
    # Create magic system and combat manager
    magic_system = MagicSystem()
    combat_manager = MagicalCombatManager(magic_system)
    
    # Create combatants
    player = create_test_character()
    monster = create_test_monster()
    
    print(f"Player: {player.name}")
    print(f"Monster: {monster.name}")
    
    # Initialize combat with these combatants
    combat_location = "A volcanic cave with streams of lava and intense heat. The air shimmers with magical energy."
    combat_manager.initialize_combat([player, monster], combat_location)
    
    # Get player's magic status
    player_magic = combat_manager.get_combatant_magic_status(player)
    print("\nPlayer Magic Status:")
    print(f"Has Mana Heart: {player_magic['has_mana_heart']}")
    print(f"Mana: {player_magic['mana_current']}/{player_magic['mana_max']}")
    print(f"Ley Energy: {player_magic['ley_energy']}")
    
    # Get monster's magic status
    monster_magic = combat_manager.get_combatant_magic_status(monster)
    print("\nMonster Magic Status:")
    print(f"Has Mana Heart: {monster_magic['has_mana_heart']}")
    print(f"Mana: {monster_magic.get('mana_current', 0)}/{monster_magic.get('mana_max', 0)}")
    print(f"Ley Energy: {monster_magic.get('ley_energy', 0)}")
    
    # Get available combat spells for player
    player_spells = combat_manager.get_available_combat_spells(player)
    print("\nPlayer's Available Combat Spells:")
    for spell in player_spells:
        print(f"  - {spell['name']} ({spell['tier']})")
        print(f"    Mana Cost: {spell['mana_cost']}, Ley Energy Cost: {spell['ley_energy_cost']}")
        print(f"    Combat Move: {spell['combat_move']['name']} ({spell['combat_move']['move_type']})")
        print(f"    Base Damage: {spell['combat_move']['base_damage']}")
    
    # Draw energy from leylines during combat
    print("\nPlayer draws energy from leylines...")
    result = combat_manager.draw_from_combat_leyline(player, 10)
    print(f"Result: {result['message']}")
    
    # If player knows any spells, cast one
    if player_spells:
        print("\nCasting a spell...")
        spell_to_cast = player_spells[0]
        result = combat_manager.execute_magical_combat_move(player, monster, spell_to_cast['spell_id'])
        print(f"Result: {result['success']}")
        print(f"Combat Narration: {result['combat_narration']}")
        
        # Show updated health
        print(f"Monster Health: {monster.current_health}/{monster.max_health}")
    else:
        print("\nNo spells available to cast.")
    
    # Check for magical environment effects
    print("\nChecking for magical environment effects...")
    env_effect = combat_manager.generate_magical_environment_effect()
    if env_effect:
        print(f"Effect: {env_effect['effect_type']}")
        print(f"Description: {env_effect['description']}")
        print(f"Game Effect: {env_effect['effect']}")
    else:
        print("No magical environment effects occurred.")
    
    # Update resources end of turn
    print("\nUpdating magical resources at end of turn...")
    updates = combat_manager.update_magic_resources_end_of_turn(player)
    if updates:
        if 'mana_regenerated' in updates:
            print(f"Mana Regenerated: {updates['mana_regenerated']}")
            print(f"Current Mana: {updates['current_mana']}/{updates['max_mana']}")
        if 'expired_effects' in updates:
            print(f"Expired Effects: {updates['expired_effects']}")
    else:
        print("No resource updates.")


def test_monster_magic_integration():
    """Test enhancing monsters with magical abilities"""
    print("\n=== Testing Monster Magic Integration ===")
    
    # Create magic system and monster integration
    magic_system = MagicSystem()
    monster_integration = MonsterMagicIntegration(magic_system)
    
    # Create a basic monster
    monster = create_test_monster()
    monster_moves = create_test_combat_moves()
    
    print(f"Original Monster: {monster.name}")
    print(f"Original Moves: {', '.join([move.name for move in monster_moves])}")
    
    # Enhance the monster with magic
    enhanced_monster, enhanced_moves, magic_profile = monster_integration.enhance_monster_with_magic(
        monster, monster_moves, "MAGICAL", "ELITE"
    )
    
    print("\nEnhanced Monster Magic Profile:")
    print(f"Has Mana Heart: {magic_profile.has_mana_heart}")
    print(f"Mana: {magic_profile.mana_current}/{magic_profile.mana_max}")
    print(f"Known Spells: {len(magic_profile.known_spells)}")
    
    print("\nEnhanced Monster Moves:")
    for move in enhanced_moves:
        if hasattr(move, 'spell_id') and move.spell_id:
            print(f"  - {move.name} (Magical)")
            print(f"    Type: {move.move_type.name}")
            print(f"    Domains: {', '.join([domain.name for domain in move.domains])}")
            print(f"    Base Damage: {move.base_damage}")
            print(f"    Costs: Focus: {move.focus_cost}, Spirit: {move.spirit_cost}")
        else:
            print(f"  - {move.name} (Physical)")


def test_magic_crafting_integration():
    """Test magic crafting system integration"""
    print("\n=== Testing Magic Crafting Integration ===")
    
    # Create magic system
    magic_system = MagicSystem()
    
    # Get crafting services
    from game_engine.magic_crafting_integration import magical_crafting
    crafting_service = magical_crafting['crafting_service']
    
    # Create a character with domains
    character = create_test_character()
    magic_profile = magic_system.initialize_magic_user(character.domains)
    
    print(f"Character: {character.name}")
    print("Domains:", ", ".join([f"{domain.name}: {value}" for domain, value in character.domains.items()]))
    
    # List available magical materials
    print("\nAvailable Magical Materials:")
    materials = crafting_service.list_all_materials()
    for material in materials:
        print(f"  - {material['name']} ({material['rarity']})")
        print(f"    Description: {material['description']}")
        special = material['special_properties']
        if special:
            print(f"    Special Properties: {', '.join(special)}")
    
    # List enchanting recipes
    print("\nAvailable Enchanting Recipes:")
    recipes = crafting_service.list_all_enchanting_recipes()
    for recipe in recipes:
        print(f"  - {recipe['name']}")
        print(f"    Description: {recipe['description']}")
        print(f"    Tier: {recipe['tier']}")
        print(f"    Materials: {', '.join([f'{mat['name']} (x{mat['quantity']})' for mat in recipe['required_materials']])}")
        print(f"    Domain Requirements: {', '.join([f'{req['domain']} {req['minimum_value']}+' for req in recipe['domain_requirements']])}")
    
    # List potion recipes
    print("\nAvailable Potion Recipes:")
    potion_recipes = crafting_service.list_all_potion_recipes()
    for recipe in potion_recipes:
        print(f"  - {recipe['name']}")
        print(f"    Description: {recipe['description']}")
        print(f"    Effects: {', '.join([effect['effect_type'] for effect in recipe['effects']])}")
        print(f"    Materials: {', '.join([f'{mat['name']} (x{mat['quantity']})' for mat in recipe['required_materials']])}")
    
    # Simulate enchanting an item
    print("\nAttempting to enchant an item...")
    
    # Mock available materials
    available_materials = {
        "material_ley_crystal": 3,
        "material_crimson_residue": 5,
        "Charcoal": 10,
        "Weapon": 1
    }
    
    # Try to enchant a weapon
    result = crafting_service.enchant_item(
        character_id="test_character",
        character_magic=magic_profile,
        recipe_id="recipe_flaming_weapon",
        item_id="test_sword",
        available_materials=available_materials,
        character_domains=character.domains
    )
    
    print(f"Enchanting Result: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Enchantment: {result['enchantment']['name']}")
        print(f"Effects: {', '.join(result['enchantment']['effects'])}")
    
    # Simulate brewing a potion
    print("\nAttempting to brew a potion...")
    
    # Mock available materials
    available_materials = {
        "material_spiritbloom": 2,
        "Red mushroom": 5,
        "Honey": 3,
        "Spring water": 2
    }
    
    # Try to brew a healing potion
    result = crafting_service.brew_potion(
        character_id="test_character",
        character_magic=magic_profile,
        recipe_id="recipe_healing_potion",
        available_materials=available_materials,
        character_domains=character.domains
    )
    
    print(f"Brewing Result: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Potion: {result['potion']['name']}")
        print(f"Effects: {', '.join(result['potion']['effects'])}")
        print(f"Quantity Produced: {result['quantity_produced']}")


def main():
    """Run all test functions"""
    print("=== Magic System Integration Tests ===")
    
    # Test basic magic system functionality
    test_magic_system_basics()
    
    # Test magic combat integration
    test_magic_combat_integration()
    
    # Test monster magic integration
    test_monster_magic_integration()
    
    # Test magic crafting integration
    test_magic_crafting_integration()
    
    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    main()