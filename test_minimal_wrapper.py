#!/usr/bin/env python3
"""
Test script for the minimal AI GM Brain wrapper.

This script tests the functionality of the minimal AI GM Brain wrapper
to ensure it works correctly as a fallback for the full implementation.
"""

import unittest
import sys
import os
import json
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the minimal wrapper
from ai_gm_minimal_wrapper import MinimalAIGM, create_minimal_gm

class TestMinimalWrapper(unittest.TestCase):
    """Test case for the minimal AI GM Brain wrapper."""
    
    def setUp(self):
        """Set up the test environment."""
        self.gm = create_minimal_gm(
            game_id="test_minimal",
            player_id="test_player",
            initial_context={
                "player": {
                    "name": "Test Character",
                    "domains": {"Combat": 3, "Social": 2, "Knowledge": 4},
                    "health": 100,
                    "equipment": ["Test Sword", "Test Shield"]
                },
                "current_location": "Test Room",
                "location_description": "A plain white room for testing purposes.",
                "active_npcs": ["Test NPC"]
            }
        )
    
    def test_initialization(self):
        """Test that the AI GM Brain initializes correctly."""
        self.assertEqual(self.gm.game_id, "test_minimal")
        self.assertEqual(self.gm.player_id, "test_player")
        self.assertEqual(self.gm.context["player"]["name"], "Test Character")
        self.assertEqual(self.gm.stats["inputs_processed"], 0)
    
    def test_ooc_commands(self):
        """Test out-of-character commands."""
        # Test help command
        help_response = self.gm.process_player_input("/help")
        self.assertEqual(help_response["status"], "success")
        self.assertIn("Available commands", help_response["response_text"])
        self.assertEqual(help_response["metadata"]["processing_mode"], "OOC")
        
        # Test status command
        status_response = self.gm.process_player_input("/status")
        self.assertIn("Test Character", status_response["response_text"])
        self.assertIn("Health: 100", status_response["response_text"])
        
        # Test inventory command
        inventory_response = self.gm.process_player_input("/inventory")
        self.assertIn("Test Sword", inventory_response["response_text"])
        self.assertIn("Test Shield", inventory_response["response_text"])
        
        # Test location command
        location_response = self.gm.process_player_input("/location")
        self.assertIn("Test Room", location_response["response_text"])
        self.assertIn("Test NPC", location_response["response_text"])
        
        # Test stats command
        stats_response = self.gm.process_player_input("/stats")
        self.assertIn("Game ID: test_minimal", stats_response["response_text"])
        self.assertIn("Player ID: test_player", stats_response["response_text"])
        
        # Test unknown command
        unknown_response = self.gm.process_player_input("/unknown")
        self.assertEqual(unknown_response["status"], "error")
        self.assertIn("Unknown command", unknown_response["response_text"])
    
    def test_look_commands(self):
        """Test look and examine commands."""
        # Test look around
        look_response = self.gm.process_player_input("look around")
        self.assertIn("Test Room", look_response["response_text"])
        self.assertIn("plain white room", look_response["response_text"])
        self.assertIn("Test NPC", look_response["response_text"])
        
        # Test examine object
        examine_response = self.gm.process_player_input("examine wall")
        self.assertIn("examine the wall", examine_response["response_text"])
        
        # Test examine NPC
        examine_npc_response = self.gm.process_player_input("examine Test NPC")
        self.assertIn("Test NPC", examine_npc_response["response_text"])
    
    def test_movement_commands(self):
        """Test movement commands."""
        # Test go direction
        go_response = self.gm.process_player_input("go north")
        self.assertIn("go north", go_response["response_text"])
        self.assertEqual(go_response["metadata"]["action_type"], "movement")
        
        # Test movement with no direction
        move_response = self.gm.process_player_input("move")
        self.assertIn("go somewhere", move_response["response_text"])
    
    def test_take_commands(self):
        """Test take commands."""
        take_response = self.gm.process_player_input("take artifact")
        self.assertIn("take the artifact", take_response["response_text"])
        self.assertEqual(take_response["metadata"]["action_type"], "acquisition")
    
    def test_talk_commands(self):
        """Test talk commands."""
        # Test talk to NPC
        talk_response = self.gm.process_player_input("talk to Test NPC")
        self.assertIn("Test NPC", talk_response["response_text"])
        self.assertEqual(talk_response["metadata"]["action_type"], "dialogue")
        
        # Test talk with no target
        talk_no_target = self.gm.process_player_input("talk")
        self.assertIn("speak, but there's no one", talk_no_target["response_text"])
    
    def test_context_management(self):
        """Test context management functions."""
        # Test update context
        self.gm.update_context({"weather": "Rainy", "time_of_day": "Night"})
        context = self.gm.get_context()
        self.assertEqual(context["weather"], "Rainy")
        self.assertEqual(context["time_of_day"], "Night")
        
        # Test set initial context
        new_context = {
            "player": {"name": "New Character"},
            "current_location": "New Location"
        }
        self.gm.set_initial_context(new_context)
        context = self.gm.get_context()
        self.assertEqual(context["player"]["name"], "New Character")
        self.assertEqual(context["current_location"], "New Location")
        self.assertNotIn("weather", context)  # Should be replaced, not merged
    
    def test_system_status(self):
        """Test system status function."""
        # Process some commands to update stats
        self.gm.process_player_input("/help")
        self.gm.process_player_input("look around")
        
        # Check status
        status = self.gm.get_system_status()
        self.assertEqual(status["game_id"], "test_minimal")
        self.assertEqual(status["player_id"], "test_player")
        self.assertEqual(status["inputs_processed"], 2)
        self.assertEqual(status["ooc_commands"], 1)
        self.assertEqual(status["normal_commands"], 1)

def print_test_results(result):
    """Print test results in a readable format."""
    print("\n" + "=" * 60)
    print(f"Test Results: {result.testsRun} tests run")
    print("-" * 60)
    
    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
    else:
        print(f"❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFailures:")
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"{i}. {test}")
                print("-" * 40)
                print(traceback)
        
        if result.errors:
            print("\nErrors:")
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"{i}. {test}")
                print("-" * 40)
                print(traceback)
    
    print("=" * 60)

def main():
    """Run the tests and print results."""
    print("🧪 Testing Minimal AI GM Brain Wrapper")
    
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMinimalWrapper)
    
    # Run the tests
    result = unittest.TestResult()
    suite.run(result)
    
    # Print results
    print_test_results(result)
    
    # Return 0 if successful, 1 if there were failures
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main()) 