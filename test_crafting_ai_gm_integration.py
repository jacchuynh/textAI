"""
Test Script for Crafting System Integration with AI GM Brain

This script demonstrates how the Material and Recipe System integrates with the AI GM Brain,
allowing NPCs to craft items, trade materials, and operate businesses using the detailed
material archetypes provided.
"""

import logging
import sys
import json
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

# Import necessary modules
from backend.src.database.session import SessionLocal
from backend.src.ai_gm.ai_gm_brain_config_integrated import AIGMBrainConfig
from backend.src.ai_gm.ai_gm_brain_integrated import AIGMBrain
from backend.src.ai_gm.crafting_npc_behavior import CraftingNPCBehavior
from backend.src.crafting.db.seed import seed_database
from backend.src.crafting.services.crafting_integration_service import create_crafting_integration_service

def print_divider():
    """Print a divider for better readability of test output."""
    print("\n" + "=" * 80 + "\n")

def setup_database():
    """Seed the database with materials and recipes."""
    print("Setting up the database with materials and recipes...")
    seed_database()
    print("Database setup complete!")

def setup_ai_gm_brain():
    """Set up the AI GM Brain for testing."""
    # Create a config for the AI GM Brain
    config = AIGMBrainConfig(
        game_id="test_crafting_integration",
        use_openai=False,  # We'll use the rule-based processing for testing
        debug_mode=True
    )
    
    # Create the AI GM Brain
    ai_gm = AIGMBrain(config)
    
    # Initialize knowledge base with test data
    ai_gm.knowledge_base["game_world"] = {
        "regions": {
            "Rivemark": {
                "name": "Rivemark",
                "description": "A bustling town known for its riverside markets and craftspeople.",
                "economy_strength": 7,
                "primary_resources": ["Iron", "Wood", "Fish"]
            },
            "Stonewake": {
                "name": "Stonewake",
                "description": "A dwarven settlement built into the mountains, famous for its forges.",
                "economy_strength": 8,
                "primary_resources": ["Stone", "Iron", "Gold"]
            },
            "Whispering Woods": {
                "name": "Whispering Woods",
                "description": "An elven settlement among ancient trees, with skilled woodworkers.",
                "economy_strength": 6,
                "primary_resources": ["Wood", "Herbs", "Magic Crystals"]
            }
        },
        "current_region": "Rivemark"
    }
    
    return ai_gm

def test_region_material_availability(crafting_service):
    """Test getting materials available in different regions."""
    print_divider()
    print("TESTING REGION MATERIAL AVAILABILITY")
    print_divider()
    
    regions = ["Rivemark", "Stonewake", "Whispering Woods", "Ember Wastes"]
    
    for region in regions:
        print(f"\nMaterials available in {region}:")
        availability = crafting_service.generate_region_material_availability(region)
        
        # Display available materials by rarity
        for rarity, materials in availability.items():
            if materials and rarity != "illicit":
                print(f"  {rarity.capitalize()} materials ({len(materials)}):")
                for material in materials[:3]:  # Show just a few examples
                    print(f"    - {material['name']} ({material['material_type']})")
                if len(materials) > 3:
                    print(f"    - ...and {len(materials) - 3} more")
        
        # Display illicit materials
        if availability.get("illicit"):
            print(f"  Illicit materials ({len(availability['illicit'])}):")
            for material in availability["illicit"][:3]:
                print(f"    - {material['name']} ({material['material_type']})")
            if len(availability["illicit"]) > 3:
                print(f"    - ...and {len(availability['illicit']) - 3} more")

def test_npc_crafting_professions(crafting_npc_behavior):
    """Test registering and interacting with crafting NPCs."""
    print_divider()
    print("TESTING NPC CRAFTING PROFESSIONS")
    print_divider()
    
    # Define test NPCs with different professions
    test_npcs = [
        {"id": "npc_blacksmith", "name": "Hargrim", "profession": "Blacksmith", "specialization": "Weapons", "wealth_level": 4},
        {"id": "npc_alchemist", "name": "Elindra", "profession": "Alchemist", "specialization": "Healing Potions", "wealth_level": 3},
        {"id": "npc_tailor", "name": "Thimble", "profession": "Tailor", "specialization": "Fine Clothing", "wealth_level": 5},
        {"id": "npc_woodworker", "name": "Oakenhart", "profession": "Woodworker", "specialization": "Furniture", "wealth_level": 3},
        {"id": "npc_jeweler", "name": "Gemhand", "profession": "Jeweler", "specialization": "Gemcutting", "wealth_level": 5},
        {"id": "npc_relicsmith", "name": "Arcanum", "profession": "Relicsmith", "specialization": None, "wealth_level": 4}
    ]
    
    # Register NPCs with crafting behaviors
    for npc in test_npcs:
        print(f"\nRegistering {npc['name']} as a {npc['profession']}")
        profession_info = crafting_npc_behavior.register_npc_profession(
            npc_id=npc["id"],
            profession=npc["profession"],
            specialization=npc["specialization"],
            wealth_level=npc["wealth_level"]
        )
        
        # Show NPC's skill levels
        print(f"  Skill levels:")
        for skill, level in profession_info["skill_levels"].items():
            print(f"    - {skill}: {level}")
        
        # Show crafting stations
        print(f"  Crafting stations: {', '.join(profession_info['crafting_stations'])}")
        
        # Show inventory summary
        inventory = profession_info["inventory"]
        raw_materials = [item for item in inventory if item.get("is_raw_material", False)]
        crafted_items = [item for item in inventory if not item.get("is_raw_material", False)]
        
        print(f"  Inventory: {len(inventory)} items")
        print(f"    - Raw materials: {len(raw_materials)} types")
        print(f"    - Crafted items: {len(crafted_items)} types")

def test_npc_crafting_responses(crafting_npc_behavior):
    """Test NPC responses to player requests about crafting."""
    print_divider()
    print("TESTING NPC CRAFTING RESPONSES")
    print_divider()
    
    # Test cases for player requests and expected responses
    test_cases = [
        {
            "npc_id": "npc_blacksmith",
            "request": "What do you do?",
            "expected_response_type": "ask_profession"
        },
        {
            "npc_id": "npc_blacksmith",
            "request": "Can you craft an iron sword for me?",
            "expected_response_type": "craft_item"
        },
        {
            "npc_id": "npc_blacksmith",
            "request": "Do you have any steel ingots for sale?",
            "expected_response_type": "buy_material"
        },
        {
            "npc_id": "npc_alchemist",
            "request": "I'd like to sell you some herbs I gathered.",
            "expected_response_type": "sell_material"
        },
        {
            "npc_id": "npc_alchemist",
            "request": "What items do you have available?",
            "expected_response_type": "ask_available_items"
        },
        {
            "npc_id": "npc_woodworker",
            "request": "Hello, how's business?",
            "expected_response_type": "general_conversation"
        }
    ]
    
    # Process each test case
    for idx, case in enumerate(test_cases):
        print(f"\nTest Case #{idx+1}: {case['npc_id']} - '{case['request']}'")
        
        response = crafting_npc_behavior.get_npc_crafting_response(
            npc_id=case["npc_id"],
            player_request=case["request"],
            player_id="test_player"
        )
        
        print(f"NPC Response: '{response.get('response', 'No response')}'")
        
        # Check if response matches expected type
        response_type = next((k for k, v in response.items() if k != "response" and v is True), 
                           "general_conversation")
        print(f"Response type: {response_type}")
        
        if "error" in response:
            print(f"Error: {response['error']}")

def test_npc_crafting_activity(crafting_npc_behavior):
    """Test simulating NPCs engaged in crafting activities."""
    print_divider()
    print("TESTING NPC CRAFTING ACTIVITY SIMULATION")
    print_divider()
    
    # Define test cases for NPC activities in different regions
    test_cases = [
        {"npc_id": "npc_blacksmith", "region_id": "Rivemark"},
        {"npc_id": "npc_alchemist", "region_id": "Whispering Woods"},
        {"npc_id": "npc_jeweler", "region_id": "Stonewake"},
        {"npc_id": "npc_woodworker", "region_id": "Whispering Woods"},
        {"npc_id": "npc_relicsmith", "region_id": "Stonewake"}
    ]
    
    # Simulate activities for each NPC
    for case in test_cases:
        activity = crafting_npc_behavior.simulate_npc_crafting_activity(
            npc_id=case["npc_id"],
            region_id=case["region_id"]
        )
        
        print(f"\nNPC {case['npc_id']} in {case['region_id']}:")
        print(f"Activity: {activity.get('activity', 'unknown')}")
        print(f"Description: {activity.get('description', 'No description')}")
        
        if activity.get("item_being_crafted"):
            print(f"Crafting: {activity['item_being_crafted']}")
            print(f"Difficulty: {activity.get('difficulty_level', 'unknown')}")
            print(f"Time remaining: {activity.get('crafting_time_remaining', 'unknown')} seconds")

def main():
    """Main function to run the crafting integration tests."""
    try:
        print("\nTESTING CRAFTING SYSTEM INTEGRATION WITH AI GM BRAIN")
        print_divider()
        
        # Setup
        setup_database()
        ai_gm_brain = setup_ai_gm_brain()
        crafting_service = create_crafting_integration_service()
        crafting_npc_behavior = CraftingNPCBehavior(ai_gm_brain)
        
        # Run tests
        test_region_material_availability(crafting_service)
        test_npc_crafting_professions(crafting_npc_behavior)
        test_npc_crafting_responses(crafting_npc_behavior)
        test_npc_crafting_activity(crafting_npc_behavior)
        
        # Cleanup
        crafting_service.close()
        crafting_npc_behavior.close()
        
        print_divider()
        print("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        print(f"\nTEST FAILED: {e}")
    
if __name__ == "__main__":
    main()