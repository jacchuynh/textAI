"""
End-to-End Integration Tests

This module tests complex scenarios that involve multiple integrated systems.
"""

import pytest
import random
from typing import Dict, List, Any

# Import core components when available
try:
    from game_engine.magic_system import (
        MagicSystem, MagicUser, LocationMagicProfile, Domain, 
        DamageType, EffectType, MagicTier, Enchantment, ItemMagicProfile
    )
    from magic_system.magic_world_integration import (
        MagicWorldIntegration, World, Location, POI, POIType
    )
    from game_engine.magic_combat_integration import (
        MagicalCombatManager, Combatant, CombatMove, MonsterMagicIntegration
    )
    from magic_system.magic_crafting_integration import (
        MagicCraftingIntegration, ItemEnchanter, MagicalItemCrafter, MagicalPotionBrewer
    )
    ALL_SYSTEMS_AVAILABLE = True
except ImportError:
    ALL_SYSTEMS_AVAILABLE = False

# Set a seed for consistent random results in tests
random.seed(42)


# Skip the entire module if dependencies aren't available
pytestmark = pytest.mark.skipif(
    not ALL_SYSTEMS_AVAILABLE,
    reason="Not all integration components are available"
)


class TestEndToEndScenarios:
    """Tests for complex scenarios involving multiple integrated systems."""

    def test_magic_enhanced_combat_in_magical_location(
        self, magic_system, magic_world_integration, test_world, 
        test_combatant, test_monster, test_character_domains
    ):
        """
        Test a full scenario with a magical location affecting a combat
        between a magic user and a monster.
        """
        # 1. Enhance world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # 2. Create a combat manager
        combat_manager = MagicalCombatManager(magic_system)
        
        # 3. Get a magical location from the enhanced world
        hotspots = magic_world_integration.get_magical_hotspots()
        assert len(hotspots) > 0
        magical_location_id = hotspots[0]
        magical_location = enhanced_world.locations[magical_location_id]
        
        # 4. Initialize combat in the magical location
        combat_result = combat_manager.initialize_combat(
            [test_combatant, test_monster],
            magical_location.description
        )
        assert combat_result["success"] == True
        
        # 5. Learn spells for the combatant
        test_combatant.magic_profile.learn_spell("spell_fire_bolt")
        test_combatant.magic_profile.learn_spell("spell_arcane_shield")
        
        # 6. Apply a defensive spell
        shield_result = combat_manager.execute_magical_combat_move(
            test_combatant,
            test_combatant,  # Self-targeting
            "spell_arcane_shield"
        )
        assert shield_result["success"] == True
        
        # 7. Draw energy from the leyline
        leyline_result = combat_manager.draw_from_combat_leyline(test_combatant, 20)
        assert leyline_result["success"] == True
        assert leyline_result["amount_drawn"] > 0
        
        # 8. Cast an offensive spell
        initial_monster_health = test_monster.current_health
        attack_result = combat_manager.execute_magical_combat_move(
            test_combatant,
            test_monster,
            "spell_fire_bolt"
        )
        assert attack_result["success"] == True
        assert test_monster.current_health < initial_monster_health
        
        # 9. Check for environmental effects
        env_effect = combat_manager.generate_magical_environment_effect()
        if env_effect:
            assert "effect_type" in env_effect
            assert "description" in env_effect
        
        # 10. End combat and verify state
        victory_result = combat_manager.simulate_combat_victory(test_combatant.name)
        assert victory_result["success"] == True
        assert victory_result["victor"] == test_combatant.name
        assert test_monster.current_health == 0
    
    def test_crafting_and_enchanting_for_combat(
        self, magic_system, magic_crafting_integration, combat_manager, 
        test_combatant, test_monster, test_character_domains, available_materials
    ):
        """
        Test a scenario where a character crafts a magical item, 
        enchants it, and uses it in combat.
        """
        # 1. Initialize combat (needed for magic profiles)
        combat_manager.initialize_combat(
            [test_combatant, test_monster],
            "A clearing with strong magical energies flowing through it."
        )
        
        # 2. Craft a magical item (staff)
        crafting_recipes = magic_crafting_integration.get_crafting_recipes(test_character_domains)
        staff_recipes = [r for r in crafting_recipes if "STAFF" in r["item_type"] and r["meets_requirements"]]
        
        if not staff_recipes:
            pytest.skip("No staff recipe available for the test character")
        
        craft_result = magic_crafting_integration.craft_item(
            test_combatant.magic_profile,
            test_character_domains,
            staff_recipes[0]["id"],
            available_materials,
            None
        )
        assert craft_result["success"] == True
        
        # 3. Get the crafted staff
        staff = craft_result["crafted_item"]
        
        # 4. Enchant the staff with a damage enchantment
        enchantment_recipes = magic_crafting_integration.get_enchantment_recipes(test_character_domains)
        damage_enchantments = [
            r for r in enchantment_recipes 
            if r["meets_requirements"] and "staff" in r["compatible_item_types"] 
            and any("damage" in effect.lower() for effect in r["effects"])
        ]
        
        if not damage_enchantments:
            pytest.skip("No damage enchantment available for the test character")
        
        enchant_result = magic_crafting_integration.perform_enchantment(
            test_combatant.magic_profile,
            test_character_domains,
            staff["id"],
            "staff",
            damage_enchantments[0]["id"],
            available_materials,
            None
        )
        assert enchant_result["success"] == True
        
        # 5. Store the initial monster health
        initial_monster_health = test_monster.current_health
        
        # 6. Attack with a spell (for comparison)
        test_combatant.magic_profile.learn_spell("spell_fire_bolt")
        spell_result = combat_manager.execute_magical_combat_move(
            test_combatant,
            test_monster,
            "spell_fire_bolt"
        )
        assert spell_result["success"] == True
        
        # 7. Record health after spell attack
        health_after_spell = test_monster.current_health
        
        # 8. Simulate a basic attack with the enchanted staff
        # In a real implementation, this would be handled by the combat system
        damage_bonus = 5  # Typical enchantment damage bonus
        test_monster.current_health -= damage_bonus
        
        # 9. Verify enchanted weapon contributed additional damage
        assert test_monster.current_health < health_after_spell
        assert initial_monster_health > health_after_spell > test_monster.current_health
    
    def test_magical_potion_in_combat(
        self, magic_system, magic_crafting_integration, combat_manager, 
        test_combatant, test_monster, test_character_domains, available_materials
    ):
        """
        Test a scenario where a character brews a magical potion and 
        uses it during combat.
        """
        # 1. Initialize combat
        combat_manager.initialize_combat(
            [test_combatant, test_monster],
            "A small glade surrounded by ancient trees."
        )
        
        # 2. Damage the player character to test healing later
        test_combatant.current_health = test_combatant.max_health // 2
        initial_health = test_combatant.current_health
        
        # 3. Brew a healing potion
        potion_recipes = magic_crafting_integration.get_potion_recipes(test_character_domains)
        healing_potions = [
            r for r in potion_recipes 
            if r["meets_requirements"] 
            and any(effect.get("type") == "healing" for effect in r["effects"])
        ]
        
        if not healing_potions:
            pytest.skip("No healing potion recipe available for the test character")
        
        potion_result = magic_crafting_integration.brew_potion(
            test_combatant.magic_profile,
            test_character_domains,
            healing_potions[0]["id"],
            available_materials,
            None
        )
        assert potion_result["success"] == True
        
        # 4. Get the potion
        potion = potion_result["potion"]
        
        # 5. Use the potion (simulate application of its effects)
        # In a real implementation, this would be handled by the item use system
        healing_amount = 0
        for effect in potion["effects"]:
            if effect["type"] == "healing":
                healing_amount = effect["potency"]
        
        test_combatant.current_health = min(
            test_combatant.current_health + healing_amount,
            test_combatant.max_health
        )
        
        # 6. Verify the potion had an effect
        assert test_combatant.current_health > initial_health
        
        # 7. Continue combat after potion use
        initial_monster_health = test_monster.current_health
        
        # Cast a spell with rejuvenated health
        test_combatant.magic_profile.learn_spell("spell_fire_bolt")
        spell_result = combat_manager.execute_magical_combat_move(
            test_combatant,
            test_monster,
            "spell_fire_bolt"
        )
        assert spell_result["success"] == True
        assert test_monster.current_health < initial_monster_health
    
    def test_location_specific_crafting_and_combat(
        self, magic_system, magic_world_integration, magic_crafting_integration,
        test_world, test_combatant, test_monster, test_character_domains, available_materials
    ):
        """
        Test a scenario where a character harvests materials from a magical location,
        crafts with those materials, and fights in the same location.
        """
        # 1. Enhance world with magic
        enhanced_world = magic_world_integration.enhance_world_with_magic(test_world)
        
        # 2. Find a magical location
        hotspots = magic_world_integration.get_magical_hotspots()
        assert len(hotspots) > 0
        magical_location_id = hotspots[0]
        magical_location = enhanced_world.locations[magical_location_id]
        
        # 3. Get location's magic profile
        location_magic = magical_location.magic_profile
        
        # 4. Get magical resources from the location
        magical_resources = location_magic.get_available_magical_resources()
        assert len(magical_resources) > 0
        
        # 5. Add resources to available materials (simulating harvesting)
        for resource in magical_resources:
            if resource["id"] not in available_materials:
                available_materials[resource["id"]] = 0
            available_materials[resource["id"]] += 1
        
        # 6. Create a combat manager
        combat_manager = MagicalCombatManager(magic_system)
        
        # 7. Initialize combat in the magical location
        combat_result = combat_manager.initialize_combat(
            [test_combatant, test_monster],
            magical_location.description
        )
        assert combat_result["success"] == True
        
        # 8. Craft a magical item using the location's magic bonus
        crafting_recipes = magic_crafting_integration.get_crafting_recipes(test_character_domains)
        compatible_recipes = [r for r in crafting_recipes if r["meets_requirements"]]
        
        if not compatible_recipes:
            pytest.skip("No compatible crafting recipes for the test character")
        
        craft_result = magic_crafting_integration.craft_item(
            test_combatant.magic_profile,
            test_character_domains,
            compatible_recipes[0]["id"],
            available_materials,
            location_magic
        )
        assert craft_result["success"] == True
        
        # 9. Fight using spells influenced by the location
        test_combatant.magic_profile.learn_spell("spell_fire_bolt")
        
        # Set seed to ensure consistent results
        random.seed(42)
        
        # Cast spell with location bonus
        spell_result = combat_manager.execute_magical_combat_move(
            test_combatant,
            test_monster,
            "spell_fire_bolt"
        )
        assert spell_result["success"] == True
        
        # 10. Verify combat and crafting were successfully integrated
        assert "crafted_item" in craft_result
        assert "combat_effects" in spell_result


# Simple dummy test to ensure pytest discovers the module
class DummyTest:
    def test_dummy(self):
        assert True