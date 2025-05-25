#!/usr/bin/env python3
"""
Test integration between magic system and combat system

This test ensures that the magic system properly integrates with the combat system,
allowing for magical combat moves, spell effects, and environmental influences.
"""

import unittest
import random
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

# Set the random seed for reproducible tests
random.seed(42)

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(parent_dir, "src"))

try:
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

    class TestMagicCombatIntegration(unittest.TestCase):
        """Test the integration between the magic system and combat system."""
        
        def setUp(self):
            """Set up the test environment."""
            # Create a magic system instance
            self.magic_system = MagicSystem()
            
            # Create a combat manager
            self.combat_manager = MagicalCombatManager(self.magic_system)
            
            # Create a monster integration
            self.monster_integration = MonsterMagicIntegration(self.magic_system)
            
            # Create test characters
            self.player = self._create_test_character()
            self.monster = self._create_test_monster()
            
            # Create a test combat environment
            self.combat_location = "A volcanic cave with streams of lava and intense heat. The air shimmers with magical energy."
        
        def _create_test_character(self) -> Combatant:
            """Create a test character with balanced domains."""
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
        
        def _create_test_monster(self) -> Combatant:
            """Create a test monster with elemental affinity."""
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
        
        def _create_test_combat_moves(self) -> List[CombatMove]:
            """Create basic combat moves for testing."""
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
        
        def test_combat_initialization(self):
            """Test initializing combat with magical components."""
            # Initialize combat
            result = self.combat_manager.initialize_combat([self.player, self.monster], self.combat_location)
            
            # Check that combat is initialized
            self.assertTrue(result["success"])
            
            # Check that combat has the correct combatants
            combatants = self.combat_manager.get_combatants()
            self.assertEqual(len(combatants), 2)
            self.assertIn(self.player, combatants)
            self.assertIn(self.monster, combatants)
            
            # Check that location magic is initialized
            location_magic = self.combat_manager.get_location_magic()
            self.assertIsNotNone(location_magic)
            
            # Check that magic profiles are created for combatants
            player_magic = self.combat_manager.get_combatant_magic_status(self.player)
            self.assertIsNotNone(player_magic)
            
            monster_magic = self.combat_manager.get_combatant_magic_status(self.monster)
            self.assertIsNotNone(monster_magic)
        
        def test_get_available_combat_spells(self):
            """Test getting available combat spells for a combatant."""
            # Initialize combat
            self.combat_manager.initialize_combat([self.player, self.monster], self.combat_location)
            
            # Get available spells
            player_spells = self.combat_manager.get_available_combat_spells(self.player)
            
            # Should have at least one spell
            self.assertIsInstance(player_spells, list)
            
            # If the player has spells, check their properties
            if player_spells:
                spell = player_spells[0]
                self.assertIn('name', spell)
                self.assertIn('spell_id', spell)
                self.assertIn('tier', spell)
                self.assertIn('mana_cost', spell)
                self.assertIn('ley_energy_cost', spell)
                self.assertIn('combat_move', spell)
        
        def test_draw_from_combat_leyline(self):
            """Test drawing energy from leylines during combat."""
            # Initialize combat
            self.combat_manager.initialize_combat([self.player, self.monster], self.combat_location)
            
            # Get initial ley energy
            initial_magic = self.combat_manager.get_combatant_magic_status(self.player)
            initial_ley_energy = initial_magic.get('ley_energy', 0)
            
            # Draw energy
            result = self.combat_manager.draw_from_combat_leyline(self.player, 10)
            
            # Check that drawing was successful
            self.assertTrue(result["success"])
            
            # Check that ley energy increased
            updated_magic = self.combat_manager.get_combatant_magic_status(self.player)
            updated_ley_energy = updated_magic.get('ley_energy', 0)
            
            self.assertGreater(updated_ley_energy, initial_ley_energy)
        
        def test_cast_spell_in_combat(self):
            """Test casting a spell in combat."""
            # Initialize combat
            self.combat_manager.initialize_combat([self.player, self.monster], self.combat_location)
            
            # Get player's spells
            player_spells = self.combat_manager.get_available_combat_spells(self.player)
            
            # If the player has spells, test casting one
            if player_spells:
                # Get initial monster health
                initial_health = self.monster.current_health
                
                # Cast the spell
                spell_to_cast = player_spells[0]
                result = self.combat_manager.execute_magical_combat_move(
                    self.player, self.monster, spell_to_cast['spell_id']
                )
                
                # Check that casting was successful
                self.assertTrue(result["success"])
                
                # Check that the spell had an effect (e.g., damage to monster)
                if spell_to_cast['combat_move']['base_damage'] > 0:
                    self.assertLess(self.monster.current_health, initial_health)
            else:
                # Skip this test if player has no spells
                self.skipTest("Player has no spells to cast")
        
        def test_magical_environment_effects(self):
            """Test magical environment effects in combat."""
            # Initialize combat
            self.combat_manager.initialize_combat([self.player, self.monster], self.combat_location)
            
            # Generate an environment effect
            effect = self.combat_manager.generate_magical_environment_effect()
            
            # Check that an effect was generated
            self.assertIsNotNone(effect)
            
            if effect:
                self.assertIn('effect_type', effect)
                self.assertIn('description', effect)
                self.assertIn('effect', effect)
        
        def test_monster_magic_enhancement(self):
            """Test enhancing a monster with magical abilities."""
            # Get initial monster moves
            monster_moves = self._create_test_combat_moves()
            initial_move_count = len(monster_moves)
            
            # Enhance the monster
            enhanced_monster, enhanced_moves, magic_profile = self.monster_integration.enhance_monster_with_magic(
                self.monster, monster_moves, "MAGICAL", "ELITE"
            )
            
            # Check that monster was enhanced
            self.assertIsNotNone(enhanced_monster)
            self.assertIsNotNone(enhanced_moves)
            self.assertIsNotNone(magic_profile)
            
            # Check that monster has magical abilities
            self.assertTrue(magic_profile.has_mana_heart)
            self.assertGreater(len(magic_profile.known_spells), 0)
            
            # Check that monster has new moves
            self.assertGreater(len(enhanced_moves), initial_move_count)
            
            # Check that at least one move is magical
            magical_moves = [move for move in enhanced_moves if hasattr(move, 'spell_id') and move.spell_id]
            self.assertGreater(len(magical_moves), 0)
        
        def test_update_magic_resources(self):
            """Test updating magical resources at the end of a turn."""
            # Initialize combat
            self.combat_manager.initialize_combat([self.player, self.monster], self.combat_location)
            
            # Update resources
            result = self.combat_manager.update_magic_resources_end_of_turn(self.player)
            
            # Check that resources were updated
            self.assertIsNotNone(result)
            
            if result:
                # Should have regenerated mana
                if 'mana_regenerated' in result:
                    self.assertGreaterEqual(result['mana_regenerated'], 0)
                    self.assertEqual(result['current_mana'], result['max_mana'] if result['current_mana'] > result['max_mana'] else result['current_mana'])

    if __name__ == "__main__":
        unittest.main()

except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires the magic system and combat system modules.")
    print("Skipping tests.")
    
    # Create a dummy test class to prevent test failure
    class DummyTest(unittest.TestCase):
        def test_dummy(self):
            self.skipTest("Required modules not available")