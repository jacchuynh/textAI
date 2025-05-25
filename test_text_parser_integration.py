"""
Test Script for Text Parser Integration with Economic Systems

This script demonstrates how the Text Parser Integrator connects player commands to the
game's economic systems, including crafting, trading, business operations, and more.
"""

import logging
import sys
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

# Import necessary modules
from backend.src.text_parser.parser_integrator import create_parser_integrator
from backend.src.ai_gm.ai_gm_brain_config_integrated import AIGMBrainConfig
from backend.src.ai_gm.ai_gm_brain_integrated import AIGMBrain
from backend.src.crafting.db.seed import seed_database

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
        game_id="test_text_parser_integration",
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

def test_parser_integrator(parser_integrator, player_id="test_player"):
    """Test the text parser integration with various command types."""
    print_divider()
    print("TESTING TEXT PARSER INTEGRATION")
    print_divider()
    
    # Test context with different settings
    context_rivemark_market = {
        "current_region": "Rivemark",
        "is_market": True,
        "available_crafting_stations": ["Forge", "Anvil", "Quenching Trough", "Tailor's Workbench"],
        "npcs_present": [
            {"id": "npc_blacksmith_rivemark", "name": "Hammerfist", "profession": "Blacksmith", "specialization": "Weapons"},
            {"id": "npc_tailor_rivemark", "name": "Silkweaver", "profession": "Tailor", "specialization": "Fine Clothing"}
        ]
    }
    
    context_stonewake_forge = {
        "current_region": "Stonewake",
        "is_market": False,
        "available_crafting_stations": ["Forge", "Anvil", "Quenching Trough", "Grindstone", "Smelter"],
        "npcs_present": [
            {"id": "npc_blacksmith_stonewake", "name": "Steelbeard", "profession": "Blacksmith", "specialization": "Armor"},
            {"id": "npc_miner_stonewake", "name": "Deepdelver", "profession": "Miner", "specialization": "Rare Ores"}
        ]
    }
    
    context_whispering_woods = {
        "current_region": "Whispering Woods",
        "is_market": False,
        "available_crafting_stations": ["Herbalist's Table", "Alchemy Lab", "Woodworking Bench"],
        "npcs_present": [
            {"id": "npc_alchemist_whispering", "name": "Herbroot", "profession": "Alchemist", "specialization": "Healing Potions"},
            {"id": "npc_woodworker_whispering", "name": "Oakcarver", "profession": "Woodworker", "specialization": "Bows"}
        ]
    }
    
    # Test commands for different economic activities
    test_commands = [
        # Crafting commands
        {
            "command": "craft iron dagger",
            "context": context_rivemark_market,
            "description": "Basic crafting command"
        },
        {
            "command": "what can I craft",
            "context": context_rivemark_market,
            "description": "List known recipes"
        },
        {
            "command": "learn recipe for steel sword",
            "context": context_stonewake_forge,
            "description": "Learn a new recipe"
        },
        
        # Material gathering commands
        {
            "command": "gather iron ore",
            "context": context_stonewake_forge,
            "description": "Gather basic material"
        },
        {
            "command": "search for rare herbs in Whispering Woods",
            "context": context_whispering_woods,
            "description": "Search for materials in specific location"
        },
        
        # Trading commands
        {
            "command": "sell 5 iron ingots to Hammerfist",
            "context": context_rivemark_market,
            "description": "Sell to specific NPC"
        },
        {
            "command": "buy healing potion from Herbroot",
            "context": context_whispering_woods,
            "description": "Buy from specific NPC"
        },
        {
            "command": "check price of steel ingot",
            "context": context_stonewake_forge,
            "description": "Check item price"
        },
        
        # Business commands
        {
            "command": "start blacksmith shop in Rivemark",
            "context": context_rivemark_market,
            "description": "Start a new business"
        },
        {
            "command": "hire Deepdelver for my mining business",
            "context": context_stonewake_forge,
            "description": "Hire NPC for business"
        },
        
        # Black market commands
        {
            "command": "find black market in Stonewake",
            "context": context_stonewake_forge,
            "description": "Find black market"
        },
        {
            "command": "smuggle rare herbs to Rivemark",
            "context": context_whispering_woods,
            "description": "Smuggle illicit goods"
        },
        
        # Information commands
        {
            "command": "check the economy in Rivemark",
            "context": context_rivemark_market,
            "description": "Get economic information"
        },
        {
            "command": "what materials are found in Whispering Woods",
            "context": context_whispering_woods,
            "description": "List regional materials"
        }
    ]
    
    # Process each test command
    for idx, test in enumerate(test_commands):
        print(f"\nTest #{idx+1}: {test['description']}")
        print(f"Command: '{test['command']}'")
        print(f"Context: {test['context']['current_region']}")
        
        # Process the command
        result = parser_integrator.process_text_command(
            player_id=player_id,
            command_text=test["command"],
            context=test["context"]
        )
        
        # Display the result
        print(f"Success: {result.get('success', False)}")
        print(f"Action: {result.get('action', 'unknown')}")
        print(f"Response: '{result.get('message', 'No response')}'")
        print()
        
        # Display additional details for debugging
        if "crafting_result" in result:
            print("Crafting Results:")
            print(f"  Outputs: {result['crafting_result'].get('outputs')}")
            print(f"  Experience: {result['crafting_result'].get('experience_gained')}")
        
        if "material_data" in result:
            print("Material Data:")
            print(f"  Name: {result['material_data'].get('name')}")
            print(f"  Type: {result['material_data'].get('material_type')}")
            print(f"  Rarity: {result['material_data'].get('rarity')}")

def main():
    """Main function to run the text parser integration tests."""
    try:
        print("\nTESTING TEXT PARSER INTEGRATION WITH ECONOMIC SYSTEMS")
        print_divider()
        
        # Setup
        setup_database()
        ai_gm_brain = setup_ai_gm_brain()
        parser_integrator = create_parser_integrator()
        
        # Run tests
        test_parser_integrator(parser_integrator)
        
        # Cleanup
        parser_integrator.close()
        
        print_divider()
        print("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        print(f"\nTEST FAILED: {e}")
    
if __name__ == "__main__":
    main()