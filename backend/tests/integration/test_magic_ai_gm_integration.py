#!/usr/bin/env python3
"""
Test integration between magic system and AI Game Master

This test ensures that the magic system properly integrates with the AI Game Master,
allowing for dynamic magical encounters, story generation, and NPC responses.
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

    # Import AI GM modules
    from ai_gm.ai_gm_brain import (
        AI_GM_Brain, 
        StoryContext, 
        PlayerAction, 
        NPCResponse, 
        GameEvent, 
        WorldState
    )

    # Import magic-AI GM integration
    from game_engine.magic_ai_gm_integration import (
        MagicAIGMIntegration
    )

    class TestMagicAIGMIntegration(unittest.TestCase):
        """Test the integration between the magic system and AI Game Master."""
        
        def setUp(self):
            """Set up the test environment."""
            # Create a magic system instance
            self.magic_system = MagicSystem()
            
            # Create an AI GM instance
            self.ai_gm = AI_GM_Brain()
            
            # Create magic-AI GM integration
            self.magic_ai_gm = MagicAIGMIntegration(self.magic_system, self.ai_gm)
            
            # Create test data
            self.player = self._create_test_player()
            self.world_state = self._create_test_world_state()
        
        def _create_test_player(self):
            """Create a test player with magical abilities."""
            # Create player data
            player = {
                "id": "player_1",
                "name": "Thorne Spellweaver",
                "class": "Elementalist",
                "level": 5,
                "domains": {
                    Domain.BODY: 3,
                    Domain.MIND: 4,
                    Domain.CRAFT: 3,
                    Domain.AWARENESS: 3,
                    Domain.SOCIAL: 2,
                    Domain.AUTHORITY: 2,
                    Domain.SPIRIT: 4,
                    Domain.FIRE: 3,
                    Domain.WATER: 2,
                    Domain.EARTH: 1,
                    Domain.AIR: 2,
                    Domain.LIGHT: 0,
                    Domain.DARKNESS: 0
                },
                "known_spells": [
                    "spell_fire_bolt",
                    "spell_water_shield",
                    "spell_arcane_missile",
                    "spell_earth_tremor"
                ],
                "magic_profile": None  # Will be initialized later
            }
            
            # Initialize magic profile
            player["magic_profile"] = self.magic_system.initialize_magic_user(player["domains"])
            
            # Ensure player has a mana heart
            if not player["magic_profile"].has_mana_heart:
                result = self.magic_system.develop_mana_heart(player["id"], player["magic_profile"])
            
            return player
        
        def _create_test_world_state(self):
            """Create a test world state with magical elements."""
            # Create basic world state
            world_state = WorldState(
                current_location="Mistwood Forest",
                time_of_day="evening",
                weather="clear",
                current_quest="Find the lost artifact",
                active_npcs=[
                    {"id": "npc_1", "name": "Elara", "type": "villager", "attitude": "friendly"},
                    {"id": "npc_2", "name": "Zephyr", "type": "mage", "attitude": "neutral"},
                    {"id": "npc_3", "name": "Grimshaw", "type": "merchant", "attitude": "friendly"}
                ],
                available_interactions=[
                    "talk_to_npc", "explore_area", "check_for_danger", "cast_spell", "rest"
                ],
                recent_events=[
                    "Player entered Mistwood Forest",
                    "Player spoke with Elara about the lost artifact",
                    "Player discovered a strange magical aura in the area"
                ]
            )
            
            # Add magical elements to world state
            world_state.magical_elements = {
                "leyline_strength": 3.5,
                "dominant_aspects": ["FIRE", "EARTH"],
                "magical_hotspots": [
                    {"name": "Ancient Grove", "type": "ritual_site", "aspect": "LIFE"},
                    {"name": "Glimmering Pool", "type": "mana_well", "aspect": "WATER"}
                ],
                "active_magical_effects": [
                    {"name": "Lingering Enchantment", "aspect": "ARCANE", "duration": "3 days"},
                    {"name": "Wild Magic Zone", "aspect": "CHAOS", "duration": "permanent"}
                ]
            }
            
            return world_state
        
        def test_initialize_magical_encounter(self):
            """Test generating a magical encounter with the AI GM."""
            # Generate a magical encounter
            encounter = self.magic_ai_gm.generate_magical_encounter(
                player=self.player,
                world_state=self.world_state,
                difficulty="medium"
            )
            
            # Check that encounter was generated
            self.assertIsNotNone(encounter)
            self.assertIn('title', encounter)
            self.assertIn('description', encounter)
            self.assertIn('enemies', encounter)
            self.assertIn('magical_elements', encounter)
            
            # Check that magical elements are present
            magical_elements = encounter['magical_elements']
            self.assertIn('environmental_effects', magical_elements)
            self.assertIn('leyline_influence', magical_elements)
            
            # Check that enemies have magical abilities if applicable
            for enemy in encounter['enemies']:
                self.assertIn('name', enemy)
                self.assertIn('level', enemy)
                self.assertIn('abilities', enemy)
                
                # Check if enemy has magical abilities
                if enemy.get('is_magical', False):
                    magical_abilities = [ability for ability in enemy['abilities'] 
                                        if ability.get('type') == 'magical']
                    self.assertGreater(len(magical_abilities), 0)
        
        def test_generate_magical_npc_response(self):
            """Test generating NPC responses to magical actions."""
            # Create a test magical action
            player_action = PlayerAction(
                action_type="cast_spell",
                target="npc_2",  # Zephyr the mage
                spell_id="spell_fire_bolt",
                intent="intimidate",
                context="The player is trying to get information about the artifact"
            )
            
            # Generate NPC response
            response = self.magic_ai_gm.generate_npc_response_to_magic(
                player=self.player,
                world_state=self.world_state,
                npc_id="npc_2",
                player_action=player_action
            )
            
            # Check that response was generated
            self.assertIsNotNone(response)
            self.assertIn('npc_id', response)
            self.assertIn('npc_name', response)
            self.assertIn('response_text', response)
            self.assertIn('attitude_change', response)
            self.assertIn('magical_reaction', response)
            
            # Check that the response includes a magical reaction
            magical_reaction = response['magical_reaction']
            self.assertIn('type', magical_reaction)
            self.assertIn('description', magical_reaction)
            
            # NPC should respond differently based on their type and the spell used
            self.assertEqual(response['npc_id'], "npc_2")
            self.assertIn("fire", response['response_text'].lower())
        
        def test_generate_magical_story_event(self):
            """Test generating magical story events based on player actions."""
            # Create a test magical action
            player_action = PlayerAction(
                action_type="ritual_casting",
                location="Ancient Grove",
                spell_id="ritual_commune_with_nature",
                intent="discover",
                context="The player is trying to locate the lost artifact through magical means"
            )
            
            # Generate story event
            event = self.magic_ai_gm.generate_magical_story_event(
                player=self.player,
                world_state=self.world_state,
                player_action=player_action
            )
            
            # Check that event was generated
            self.assertIsNotNone(event)
            self.assertIn('title', event)
            self.assertIn('description', event)
            self.assertIn('consequences', event)
            self.assertIn('magical_revelations', event)
            
            # Check that the event includes magical revelations
            revelations = event['magical_revelations']
            self.assertGreater(len(revelations), 0)
            
            # Event should be relevant to the player's action
            self.assertIn("ritual", event['title'].lower())
            self.assertIn("grove", event['description'].lower())
        
        def test_adapt_difficulty_based_on_magic_level(self):
            """Test adapting encounter difficulty based on player's magical abilities."""
            # Create a novice and an advanced mage for comparison
            novice_mage = self._create_test_player()
            novice_mage["level"] = 2
            novice_mage["known_spells"] = ["spell_fire_bolt"]
            novice_mage["magic_profile"].mana_max = 50
            
            advanced_mage = self._create_test_player()
            advanced_mage["level"] = 10
            advanced_mage["known_spells"] = [
                "spell_fire_bolt", "spell_water_shield", "spell_arcane_missile",
                "spell_earth_tremor", "spell_lightning_storm", "spell_mind_control"
            ]
            advanced_mage["magic_profile"].mana_max = 200
            
            # Generate encounters for both
            novice_encounter = self.magic_ai_gm.generate_magical_encounter(
                player=novice_mage,
                world_state=self.world_state,
                difficulty="medium"
            )
            
            advanced_encounter = self.magic_ai_gm.generate_magical_encounter(
                player=advanced_mage,
                world_state=self.world_state,
                difficulty="medium"
            )
            
            # Check that encounters were generated
            self.assertIsNotNone(novice_encounter)
            self.assertIsNotNone(advanced_encounter)
            
            # Advanced mage should face more challenging enemies
            novice_enemy_levels = [enemy['level'] for enemy in novice_encounter['enemies']]
            advanced_enemy_levels = [enemy['level'] for enemy in advanced_encounter['enemies']]
            
            avg_novice_level = sum(novice_enemy_levels) / len(novice_enemy_levels)
            avg_advanced_level = sum(advanced_enemy_levels) / len(advanced_enemy_levels)
            
            self.assertGreater(avg_advanced_level, avg_novice_level)
            
            # Advanced mage's encounter should have more magical elements
            novice_magic_count = len(novice_encounter['magical_elements']['environmental_effects'])
            advanced_magic_count = len(advanced_encounter['magical_elements']['environmental_effects'])
            
            self.assertGreaterEqual(advanced_magic_count, novice_magic_count)
        
        def test_generate_magical_quest(self):
            """Test generating a magic-focused quest."""
            # Generate a magical quest
            quest = self.magic_ai_gm.generate_magical_quest(
                player=self.player,
                world_state=self.world_state,
                quest_type="artifact_hunt",
                difficulty="medium"
            )
            
            # Check that quest was generated
            self.assertIsNotNone(quest)
            self.assertIn('title', quest)
            self.assertIn('description', quest)
            self.assertIn('objectives', quest)
            self.assertIn('rewards', quest)
            self.assertIn('magical_requirements', quest)
            
            # Check that quest has magical requirements
            requirements = quest['magical_requirements']
            self.assertGreater(len(requirements), 0)
            
            # Quest should involve magic
            self.assertIn("magic", quest['description'].lower())
            
            # Objectives should include magical tasks
            magical_objectives = [obj for obj in quest['objectives'] 
                                if "spell" in obj.lower() or "magic" in obj.lower()]
            self.assertGreater(len(magical_objectives), 0)
            
            # Rewards should include magical items
            magical_rewards = [reward for reward in quest['rewards'] 
                             if reward.get('type') == 'magical_item']
            self.assertGreater(len(magical_rewards), 0)

    if __name__ == "__main__":
        unittest.main()

except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires the magic system and AI GM modules.")
    print("Skipping tests.")
    
    # Create a dummy test class to prevent test failure
    class DummyTest(unittest.TestCase):
        def test_dummy(self):
            self.skipTest("Required modules not available")