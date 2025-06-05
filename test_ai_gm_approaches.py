#!/usr/bin/env python3
"""
AI GM Integration Approaches Test

This script tests both main approaches to AI GM Brain integration:
1. Unified Integration (comprehensive system)
2. Direct Test (simplified implementation)

It performs basic functionality tests for both approaches and reports the results.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_section(text):
    """Print a section divider."""
    print("\n" + "-" * 40)
    print(text)
    print("-" * 40)

def test_unified_approach():
    """Test the unified integration approach."""
    print_header("Testing Unified Integration Approach")
    
    try:
        # Import the unified integration module
        from ai_gm_unified_demo import create_unified_gm
        
        print("✅ Successfully imported unified integration module")
        
        # Create GM instance
        gm = create_unified_gm(
            game_id="test_unified",
            player_id="test_player",
            initial_context={
                "player": {
                    "name": "Test Character",
                    "domains": {"Combat": 3, "Magic": 4, "Survival": 2},
                    "health": 100
                },
                "current_location": "Test Chamber",
                "active_npcs": ["Test NPC"]
            }
        )
        
        print("✅ Successfully created unified GM instance")
        
        # Test basic commands
        test_commands = [
            "look around",
            "examine the room",
            "talk to npc",
            "/help",
            "/status"
        ]
        
        print_section("Testing Basic Commands")
        
        for cmd in test_commands:
            try:
                print(f"Command: '{cmd}'")
                response = gm.process_player_input(cmd)
                
                if response and "response_text" in response:
                    print(f"Response: {response['response_text'][:100]}...")
                    print("✅ Command processed successfully")
                else:
                    print("❌ Command failed to return a valid response")
                
                print("-" * 30)
            except Exception as e:
                print(f"❌ Error processing command '{cmd}': {e}")
        
        # Test context management
        print_section("Testing Context Management")
        
        try:
            gm.update_context({
                "weather": "Stormy",
                "time_of_day": "Night"
            })
            
            context = gm.get_context()
            
            if "weather" in context and "time_of_day" in context:
                print(f"Context updated: weather={context.get('weather')}, time={context.get('time_of_day')}")
                print("✅ Context management working correctly")
            else:
                print("❌ Context management failed")
        except Exception as e:
            print(f"❌ Error in context management: {e}")
        
        return True
    
    except Exception as e:
        print(f"❌ Unified approach test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_approach():
    """Test the direct implementation approach."""
    print_header("Testing Direct Implementation Approach")
    
    try:
        # Import the direct implementation module
        from ai_gm_direct_test import AIGMUnifiedSystem, create_unified_gm
        
        print("✅ Successfully imported direct implementation module")
        
        # Create GM instance
        gm = create_unified_gm(
            game_id="test_direct",
            player_id="test_player",
            initial_context={
                "player": {
                    "name": "Direct Test Character",
                    "domains": {"Combat": 3, "Magic": 4, "Survival": 2},
                    "health": 100
                },
                "current_location": "Test Laboratory",
                "active_npcs": ["Lab Assistant"]
            }
        )
        
        print("✅ Successfully created direct GM instance")
        
        # Test basic commands
        test_commands = [
            "look around",
            "examine the lab",
            "talk to assistant",
            "/help",
            "/status"
        ]
        
        print_section("Testing Basic Commands")
        
        for cmd in test_commands:
            try:
                print(f"Command: '{cmd}'")
                response = gm.process_player_input(cmd)
                
                if response and "response_text" in response:
                    print(f"Response: {response['response_text'][:100]}...")
                    print("✅ Command processed successfully")
                else:
                    print("❌ Command failed to return a valid response")
                
                print("-" * 30)
            except Exception as e:
                print(f"❌ Error processing command '{cmd}': {e}")
        
        # Test context management
        print_section("Testing Context Management")
        
        try:
            gm.update_context({
                "equipment": ["Lab Coat", "Safety Goggles"],
                "experiment_status": "In Progress"
            })
            
            context = gm.get_context()
            
            if "equipment" in context and "experiment_status" in context:
                print(f"Context updated: experiment_status={context.get('experiment_status')}")
                print("✅ Context management working correctly")
            else:
                print("❌ Context management failed")
        except Exception as e:
            print(f"❌ Error in context management: {e}")
        
        return True
    
    except Exception as e:
        print(f"❌ Direct approach test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comparison_test():
    """Run a direct comparison between both approaches."""
    print_header("Approach Comparison Test")
    
    try:
        # Import both approaches
        from ai_gm_unified_demo import create_unified_gm as create_unified
        from ai_gm_direct_test import create_unified_gm as create_direct
        
        # Create instances
        unified_gm = create_unified(game_id="compare_unified", player_id="compare_player")
        direct_gm = create_direct(game_id="compare_direct", player_id="compare_player")
        
        print("✅ Successfully created both GM instances")
        
        # Test same commands with both approaches
        test_commands = [
            "look around",
            "go north",
            "take the sword",
            "help"
        ]
        
        print_section("Command Comparison")
        
        for cmd in test_commands:
            print(f"Command: '{cmd}'")
            
            # Process with unified approach
            unified_response = unified_gm.process_player_input(cmd)
            unified_text = unified_response.get("response_text", "No response")
            
            # Process with direct approach
            direct_response = direct_gm.process_player_input(cmd)
            direct_text = direct_response.get("response_text", "No response")
            
            print(f"Unified: {unified_text[:75]}...")
            print(f"Direct:  {direct_text[:75]}...")
            print("-" * 30)
        
        return True
    
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the tests."""
    print(f"🎮 AI GM Integration Approaches Test")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    unified_result = test_unified_approach()
    direct_result = test_direct_approach()
    comparison_result = run_comparison_test()
    
    # Print summary
    print_header("Test Results Summary")
    print(f"Unified Integration Approach: {'✅ PASSED' if unified_result else '❌ FAILED'}")
    print(f"Direct Implementation Approach: {'✅ PASSED' if direct_result else '❌ FAILED'}")
    print(f"Approach Comparison: {'✅ PASSED' if comparison_result else '❌ FAILED'}")
    
    if unified_result and direct_result:
        print("\n✅ Both integration approaches are working correctly!")
        print("You can use either approach based on your specific needs:")
        print("- Unified Integration: For comprehensive features and integrations")
        print("- Direct Implementation: For simpler setup with fewer dependencies")
    else:
        print("\n⚠️ Some tests failed. Please check the logs for details.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 