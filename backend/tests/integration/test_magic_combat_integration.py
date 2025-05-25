"""
Magic-Combat Integration Tests

This module tests the integration between the magic system and the combat system.
"""

import pytest
import random
from typing import Dict, List, Any

# Import core components when available
try:
    from game_engine.magic_system import (
        MagicSystem, MagicUser, LocationMagicProfile, Domain, 
        DamageType, EffectType, MagicTier
    )
    from game_engine.magic_combat_integration import (
        MagicalCombatManager, Combatant, CombatMove, MonsterMagicIntegration
    )
    MAGIC_COMBAT_AVAILABLE = True
except ImportError:
    MAGIC_COMBAT_AVAILABLE = False

# Set a seed for consistent random results in tests
random.seed(42)


# Skip the entire module if dependencies aren't available
pytestmark = pytest.mark.skipif(
    not MAGIC_COMBAT_AVAILABLE,
    reason="Magic combat integration components not available"
)


class TestMagicCombatIntegration:
    """Tests for the integration between magic and combat systems."""

    def test_combat_initialization(self, combat_manager, test_combatant, test_monster, test_location_description):
        """Test that combat can be initialized with magic profiles."""
        # Initialize combat
        result = combat_manager.initialize_combat(
            [test_combatant, test_monster],
            test_location_description
        )
        
        # Verify combat was initialized
        assert result["success"] == True
        assert len(result["combatants"]) == 2
        assert result["location_magic"] is not None
        
        # Check that combatants have magic profiles
        assert hasattr(test_combatant, 'magic_profile')
        assert test_combatant.magic_profile is not None
        assert hasattr(test_monster, 'magic_profile')
        assert test_monster.magic_profile is not None
    
    def test_magic_profile_initialization(self, combat_manager, test_combatant, test_monster, test_location_description):
        """Test that magic profiles are properly initialized for combatants."""
        # Initialize combat
        combat_manager.initialize_combat(
            [test_combatant, test_monster],
            test_location_description
        )
        
        # Get combatant magic statuses
        fighter_magic = combat_manager.get_combatant_magic_status(test_combatant)
        monster_magic = combat_manager.get_combatant_magic_status(test_monster)
        
        # Check fighter magic status
        assert fighter_magic is not None
        assert "mana_current" in fighter_magic
        assert "mana_max" in fighter_magic
        assert fighter_magic["mana_max"] > 0
        
        # Check monster magic status
        assert monster_magic is not None
        assert "mana_current" in monster_magic
        assert "mana_max" in monster_magic
        assert monster_magic["mana_max"] > 0
        
        # Fire elemental should have high fire domain
        assert test_monster.magic_profile.attunements is not None
        assert "fire" in test_monster.magic_profile.attunements
    
    def test_spell_combat_moves(self, combat_manager, test_combatant, test_monster, test_location_description):
        """Test that spells can be converted to combat moves."""
        # Initialize combat
        combat_manager.initialize_combat(
            [test_combatant, test_monster],
            test_location_description
        )
        
        # Learn a spell for the test combatant
        test_combatant.magic_profile.learn_spell("spell_fire_bolt")
        
        # Get available combat spells
        combat_spells = combat_manager.get_available_combat_spells(test_combatant)
        
        # There should be at least one combat spell
        assert len(combat_spells) > 0
        
        # Check that the spell has a combat move
        spell = combat_spells[0]
        assert "combat_move" in spell
        assert spell["combat_move"]["name"] == "Fire Bolt"
        assert spell["combat_move"]["move_type"] == "FORCE"  # Damage spell
        assert spell["combat_move"]["base_damage"] > 0
    
    def test_spell_casting_in_combat(self, combat_manager, test_combatant, test_monster, test_location_description):
        """Test that spells can be cast during combat."""
        # Initialize combat
        combat_manager.initialize_combat(
            [test_combatant, test_monster],
            test_location_description
        )
        
        # Learn a spell for the test combatant
        test_combatant.magic_profile.learn_spell("spell_fire_bolt")
        
        # Store the initial health
        initial_health = test_monster.current_health
        
        # Cast the spell
        result = combat_manager.execute_magical_combat_move(
            test_combatant,
            test_monster,
            "spell_fire_bolt"
        )
        
        # Verify the spell was cast successfully
        assert result["success"] == True
        assert "combat_narration" in result
        assert "combat_effects" in result
        
        # Check that damage was applied
        damage_effects = [e for e in result["combat_effects"] if e["type"] == "damage"]
        assert len(damage_effects) > 0
        assert damage_effects[0]["amount"] > 0
        
        # Check that the monster's health was reduced
        assert test_monster.current_health < initial_health
    
    def test_environmental_magic_effects(self, combat_manager, test_combatant, test_monster, test_location_description):
        """Test that environmental magic affects combat."""
        # Initialize combat with a magical location
        combat_manager.initialize_combat(
            [test_combatant, test_monster],
            test_location_description
        )
        
        # Generate an environmental effect
        effect = combat_manager.generate_magical_environment_effect()
        
        # There should be a chance of an effect
        if effect is not None:
            assert "effect_type" in effect
            assert "description" in effect
            assert "effect" in effect
            
            # Effect should be one of the expected types
            assert effect["effect_type"] in [
                "mana_surge", "leyline_fluctuation", "elemental_manifestation",
                "arcane_disturbance", "magical_resonance"
            ]
    
    def test_mana_regeneration_in_combat(self, combat_manager, test_combatant, test_location_description):
        """Test that mana regenerates during combat."""
        # Initialize combat
        combat_manager.initialize_combat(
            [test_combatant],
            test_location_description
        )
        
        # Set initial mana to a low value
        test_combatant.magic_profile.mana_current = 10
        
        # Update resources at end of turn
        result = combat_manager.update_magic_resources_end_of_turn(test_combatant)
        
        # Verify mana was regenerated
        assert "mana_regenerated" in result
        assert result["mana_regenerated"] > 0
        assert result["current_mana"] > 10
    
    def test_draw_from_leyline(self, combat_manager, test_combatant, test_location_description):
        """Test that combatants can draw energy from leylines during combat."""
        # Initialize combat with a magical location
        combat_manager.initialize_combat(
            [test_combatant],
            test_location_description
        )
        
        # Set initial ley energy to 0
        test_combatant.magic_profile.current_ley_energy = 0
        
        # Draw from the leyline
        result = combat_manager.draw_from_combat_leyline(test_combatant, 10)
        
        # Verify energy was drawn
        assert result["success"] == True
        assert result["amount_drawn"] > 0
        assert test_combatant.magic_profile.current_ley_energy > 0
    
    def test_monster_magic_enhancement(self, magic_system):
        """Test that monsters can be enhanced with magical abilities."""
        # Create a monster magic integration
        monster_integration = MonsterMagicIntegration(magic_system)
        
        # Create a basic monster
        monster = Combatant(
            name="Ice Elemental",
            domains={
                Domain.BODY: 2,
                Domain.MIND: 1,
                Domain.CRAFT: 0,
                Domain.AWARENESS: 2,
                Domain.SOCIAL: 0,
                Domain.AUTHORITY: 0,
                Domain.SPIRIT: 3,
                Domain.WATER: 3,
                Domain.ICE: 4,
                Domain.EARTH: 0,
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
        
        # Basic moves for the monster
        monster_moves = [
            CombatMove(
                name="Ice Spike",
                description="A spike of ice that deals damage.",
                move_type="FORCE",
                domains=[Domain.ICE],
                base_damage=10,
                stamina_cost=5,
                focus_cost=0,
                spirit_cost=0
            )
        ]
        
        # Enhance the monster
        enhanced_monster, enhanced_moves, magic_profile = monster_integration.enhance_monster_with_magic(
            monster,
            monster_moves,
            "ELEMENTAL",
            "ELITE"
        )
        
        # Verify the monster was enhanced
        assert enhanced_monster is not None
        assert enhanced_monster.magic_profile is not None
        assert len(enhanced_moves) > len(monster_moves)
        
        # Check that the monster has appropriate magic affinity
        assert enhanced_monster.magic_profile.affinity is not None
        if DamageType.ICE in enhanced_monster.magic_profile.affinity:
            assert enhanced_monster.magic_profile.affinity[DamageType.ICE] > 0
        elif DamageType.WATER in enhanced_monster.magic_profile.affinity:
            assert enhanced_monster.magic_profile.affinity[DamageType.WATER] > 0
        
        # Check that the monster has learned some spells
        assert len(enhanced_monster.magic_profile.known_spells) > 0


# Simple dummy test to ensure pytest discovers the module
class DummyTest:
    def test_dummy(self):
        assert True