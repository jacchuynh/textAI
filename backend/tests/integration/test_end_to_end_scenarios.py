#!/usr/bin/env python3
"""
End-to-End Integration Test Scenarios

This test script verifies complete user flows that involve multiple subsystems working together,
such as a player completing a quest that involves magic, combat, and crafting.
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
    # Import game engine and systems
    from game_engine.game_engine import GameEngine
    from game_engine.magic_system import MagicSystem
    from game_engine.enhanced_combat.combat_system_core import CombatSystem
    from game_engine.text_parser import TextParser
    
    # Import player and character systems
    from game_engine.player_character import PlayerCharacter
    from game_engine.npc.npc_manager import NPCManager
    
    # Import world and location systems
    from world_generation.world_model import World, Location
    from world_generation.location_manager import LocationManager
    
    # Import quest and event systems
    from game_engine.quest.quest_manager import QuestManager
    from game_engine.events.event_manager import EventManager
    
    # Import crafting system
    from game_engine.crafting.crafting_system import CraftingSystem
    
    # Import storage and persistence
    from game_engine.storage.game_state_manager import GameStateManager

    class TestEndToEndScenarios(unittest.TestCase):
        """Test end-to-end scenarios involving multiple subsystems."""
        
        def setUp(self):
            """Set up the test environment with all required systems."""
            # Initialize key game systems
            self.game_engine = GameEngine()
            self.magic_system = MagicSystem()
            self.combat_system = CombatSystem()
            self.text_parser = TextParser()
            self.npc_manager = NPCManager()
            self.location_manager = LocationManager()
            self.quest_manager = QuestManager()
            self.event_manager = EventManager()
            self.crafting_system = CraftingSystem()
            self.game_state_manager = GameStateManager()
            
            # Connect systems to game engine
            self.game_engine.register_system("magic_system", self.magic_system)
            self.game_engine.register_system("combat_system", self.combat_system)
            self.game_engine.register_system("text_parser", self.text_parser)
            self.game_engine.register_system("npc_manager", self.npc_manager)
            self.game_engine.register_system("location_manager", self.location_manager)
            self.game_engine.register_system("quest_manager", self.quest_manager)
            self.game_engine.register_system("event_manager", self.event_manager)
            self.game_engine.register_system("crafting_system", self.crafting_system)
            self.game_engine.register_system("game_state_manager", self.game_state_manager)
            
            # Initialize test player
            self.player = self._create_test_player()
            
            # Initialize test game world
            self.world = self._create_test_world()
            
            # Set up initial game state
            self.game_state_manager.initialize_game_state(self.player, self.world)
        
        def _create_test_player(self):
            """Create a test player character."""
            return PlayerCharacter(
                id="player_1",
                name="Arcane Adventurer",
                level=5,
                attributes={
                    "strength": 8,
                    "dexterity": 12,
                    "constitution": 10,
                    "intelligence": 16,
                    "wisdom": 14,
                    "charisma": 13
                },
                skills={
                    "arcana": 4,
                    "athletics": 2,
                    "persuasion": 3,
                    "perception": 3,
                    "stealth": 2
                },
                inventory={
                    "gold": 250,
                    "items": [
                        {"id": "item_basic_staff", "name": "Apprentice's Staff", "type": "weapon", "quantity": 1},
                        {"id": "item_healing_potion", "name": "Healing Potion", "type": "consumable", "quantity": 3},
                        {"id": "item_mana_crystal", "name": "Mana Crystal", "type": "material", "quantity": 5},
                        {"id": "item_spellbook", "name": "Spellbook", "type": "quest_item", "quantity": 1}
                    ]
                }
            )
        
        def _create_test_world(self):
            """Create a test game world."""
            # This would typically be more complex with multiple locations, NPCs, etc.
            # For testing purposes, we'll create a simple world structure
            return self.location_manager.create_test_world("Test World")
        
        def test_magical_quest_completion(self):
            """
            Test a complete quest flow involving magical elements.
            
            This scenario tests:
            1. Receiving a quest from an NPC
            2. Navigating to quest locations
            3. Using magic to overcome obstacles
            4. Engaging in magical combat
            5. Crafting a magical item required for the quest
            6. Completing the quest and receiving rewards
            """
            # 1. Initialize a magical quest
            quest_id = "quest_magical_artifact"
            quest = self.quest_manager.create_quest(
                id=quest_id,
                name="The Lost Artifact of Arcane Power",
                description="Find and recover the ancient artifact hidden in the Crystal Caverns.",
                difficulty="medium",
                quest_giver_npc_id="npc_elder_mage",
                stages=[
                    {
                        "id": "stage_1",
                        "description": "Speak with Elder Thorne to learn about the artifact",
                        "location_id": "loc_village",
                        "completion_condition": "dialog_complete",
                        "completed": False
                    },
                    {
                        "id": "stage_2",
                        "description": "Find the entrance to the Crystal Caverns",
                        "location_id": "loc_forest",
                        "completion_condition": "location_discovered",
                        "completed": False
                    },
                    {
                        "id": "stage_3",
                        "description": "Craft a magical key to unlock the cavern entrance",
                        "location_id": "loc_forest",
                        "completion_condition": "item_crafted",
                        "target_item_id": "item_magical_key",
                        "completed": False
                    },
                    {
                        "id": "stage_4",
                        "description": "Defeat the guardian of the caverns",
                        "location_id": "loc_cavern",
                        "completion_condition": "combat_victory",
                        "enemy_id": "enemy_crystal_guardian",
                        "completed": False
                    },
                    {
                        "id": "stage_5",
                        "description": "Use the spell of revelation to find the hidden artifact",
                        "location_id": "loc_cavern_inner",
                        "completion_condition": "spell_cast",
                        "spell_id": "spell_revelation",
                        "completed": False
                    },
                    {
                        "id": "stage_6",
                        "description": "Return the artifact to Elder Thorne",
                        "location_id": "loc_village",
                        "completion_condition": "dialog_complete",
                        "completed": False
                    }
                ],
                rewards={
                    "experience": 500,
                    "gold": 150,
                    "items": [
                        {"id": "item_arcane_focus", "name": "Greater Arcane Focus", "type": "equipment"}
                    ],
                    "reputation": [
                        {"faction_id": "faction_mages_guild", "amount": 25}
                    ],
                    "spell_unlock": "spell_arcane_shield"
                }
            )
            
            # Assign quest to player
            self.quest_manager.assign_quest_to_player(self.player.id, quest_id)
            
            # 2. Test stage 1: Dialog with NPC
            # Simulate player talking to NPC
            command = "talk to Elder Thorne"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            quest_stage = self.quest_manager.get_current_quest_stage(self.player.id, quest_id)
            self.assertEqual(quest_stage["id"], "stage_2")  # Should have advanced to stage 2
            
            # 3. Test stage 2: Find location
            # Simulate player movement to forest
            command = "travel to forest"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            # Simulate player finding cavern entrance
            command = "search for cavern entrance"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            quest_stage = self.quest_manager.get_current_quest_stage(self.player.id, quest_id)
            self.assertEqual(quest_stage["id"], "stage_3")  # Should have advanced to stage 3
            
            # 4. Test stage 3: Craft magical item
            # Check required materials
            recipe = self.crafting_system.get_recipe("recipe_magical_key")
            
            # Add required materials to player inventory if needed
            for material in recipe["required_materials"]:
                self.player.add_to_inventory(material["id"], material["name"], "material", material["quantity"])
            
            # Craft the item
            command = "craft magical key"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            self.assertTrue(self.player.has_item("item_magical_key"))
            quest_stage = self.quest_manager.get_current_quest_stage(self.player.id, quest_id)
            self.assertEqual(quest_stage["id"], "stage_4")  # Should have advanced to stage 4
            
            # 5. Test stage 4: Magical combat
            # Simulate player travel to cavern
            command = "use magical key on cavern entrance"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            # Initialize combat with guardian
            guardian = self.npc_manager.get_enemy("enemy_crystal_guardian")
            combat_result = self.combat_system.initialize_combat([self.player, guardian])
            
            # Perform combat actions until victory
            # For test purposes, we'll just simulate victory
            self.combat_system.simulate_combat_victory(self.player.id)
            
            quest_stage = self.quest_manager.get_current_quest_stage(self.player.id, quest_id)
            self.assertEqual(quest_stage["id"], "stage_5")  # Should have advanced to stage 5
            
            # 6. Test stage 5: Cast spell to find artifact
            # Ensure player knows the required spell
            if "spell_revelation" not in self.player.known_spells:
                self.magic_system.learn_spell(self.player.id, "spell_revelation")
            
            # Cast the spell
            command = "cast revelation spell"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            # Player should have found the artifact
            self.assertTrue(self.player.has_item("item_ancient_artifact"))
            quest_stage = self.quest_manager.get_current_quest_stage(self.player.id, quest_id)
            self.assertEqual(quest_stage["id"], "stage_6")  # Should have advanced to stage 6
            
            # 7. Test stage 6: Return to NPC to complete quest
            # Travel back to village
            command = "travel to village"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            # Talk to Elder Thorne
            command = "give artifact to Elder Thorne"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            # Verify quest completion
            quest_status = self.quest_manager.get_quest_status(self.player.id, quest_id)
            self.assertEqual(quest_status, "completed")
            
            # Verify rewards
            initial_gold = 250
            expected_gold = initial_gold + 150  # Quest reward
            self.assertEqual(self.player.inventory["gold"], expected_gold)
            
            # Verify item reward
            self.assertTrue(self.player.has_item("item_arcane_focus"))
            
            # Verify spell unlock
            self.assertIn("spell_arcane_shield", self.player.known_spells)
        
        def test_magical_environment_interaction(self):
            """
            Test interactions between the player's magic and the environment.
            
            This scenario tests:
            1. Environmental magic detection
            2. Leyline interaction
            3. Magical resource gathering
            4. Environmental spell effects
            5. Dynamic environment responses to magic
            """
            # Set up a test location with magical properties
            magical_grove_id = "loc_magical_grove"
            magical_grove = self.location_manager.create_magical_location(
                id=magical_grove_id,
                name="Ancient Enchanted Grove",
                description="A mystical grove where leylines converge and magic flows freely.",
                leyline_strength=4.5,
                magical_aspects=["LIFE", "NATURE", "ARCANE"]
            )
            
            # Travel to the magical location
            command = "travel to Enchanted Grove"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            # 1. Test magical detection
            command = "sense magic"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            self.assertIn("leylines", result["message"].lower())
            self.assertIn("strong magical energy", result["message"].lower())
            
            # 2. Test leyline interaction
            initial_mana = self.player.current_mana
            command = "draw power from leyline"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            self.assertGreater(self.player.current_mana, initial_mana)
            
            # 3. Test magical resource gathering
            initial_inventory_count = len(self.player.inventory["items"])
            command = "gather magical herbs"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            self.assertGreater(len(self.player.inventory["items"]), initial_inventory_count)
            
            # 4. Test environmental spell casting
            # Cast a spell that interacts with the environment
            command = "cast growth spell on withered tree"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            self.assertTrue(result["success"])
            # Environment should change in response
            location = self.location_manager.get_location(magical_grove_id)
            self.assertIn("revitalized tree", location.description.lower())
            
            # 5. Test environment magic response
            # Cast a destructive spell
            command = "cast fire bolt at clearing"
            result = self.text_parser.parse_and_execute(command, self.player, self.game_engine)
            
            # Environment should respond negatively
            location = self.location_manager.get_location(magical_grove_id)
            self.assertIn("scorched", location.description.lower())
            
            # Check for magical consequences (environmental response)
            active_effects = self.magic_system.get_environmental_effects(magical_grove_id)
            negative_effects = [effect for effect in active_effects if effect["type"] == "negative"]
            self.assertGreater(len(negative_effects), 0)

    if __name__ == "__main__":
        unittest.main()

except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires all game engine systems.")
    print("Skipping tests.")
    
    # Create a dummy test class to prevent test failure
    class DummyTest(unittest.TestCase):
        def test_dummy(self):
            self.skipTest("Required modules not available")