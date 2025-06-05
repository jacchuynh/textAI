#!/usr/bin/env python3
"""
Test script to verify the integration between InventorySystem and VocabularyManager
through the parser tools.
"""

import sys
import os
import json
from pathlib import Path

# Add the backend src directory to the path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Also add the main directory for system_integration_manager
sys.path.insert(0, str(Path(__file__).parent))

# Import necessary modules
from inventory.inventory_system import InventorySystem
from inventory.item_definitions import ItemDataRegistry
from text_parser.vocabulary_manager import VocabularyManager
from text_parser.parser_engine import ParserEngine, GameSystemsManager
from system_integration_manager import SystemIntegrationManager, SystemType

def test_inventory_vocabulary_integration():
    """Test that inventory system properly registers items with vocabulary manager."""
    
    print("=== Testing Inventory-Vocabulary Integration ===\n")
    
    # 1. Initialize systems
    print("1. Initializing systems...")
    
    # Initialize item registry and load items
    item_registry = ItemDataRegistry()
    item_file = backend_src / "inventory" / "data" / "basic_items.json"
    
    if item_file.exists():
        items_loaded = item_registry.load_from_files([str(item_file)])
        print(f"   - Loaded {items_loaded} items from {item_file}")
    else:
        print(f"   - Warning: {item_file} not found, using empty registry")
    
    # Initialize inventory system with registry
    inventory_system = InventorySystem(item_registry=item_registry)
    print(f"   - Inventory system initialized with {len(inventory_system.item_registry.get_all_items())} items")
    
    # Initialize vocabulary manager
    vocabulary_manager = VocabularyManager()
    print(f"   - Vocabulary manager initialized")
    
    # Connect them
    inventory_system.set_vocabulary_manager(vocabulary_manager)
    print(f"   - Connected inventory system to vocabulary manager")
    
    # 2. Test vocabulary registration
    print("\n2. Testing vocabulary registration...")
    
    # Check if some items are registered - use actual items from the registry
    available_items = list(inventory_system.item_registry._items.keys())[:3]  # Take first 3 items
    for item_id in available_items:
        if item_id in inventory_system.item_registry._items:
            item_def = inventory_system.item_registry._items[item_id]
            name = item_def.name.lower()
            item_found_id = vocabulary_manager.get_item_id(name)
            print(f"   - Checking '{name}': {item_found_id}")
    
    # 3. Test system integration
    print("\n3. Testing system integration...")
    
    # Create integration manager
    integration_manager = SystemIntegrationManager("test_session", "test_player")
    print(f"   - Created integration manager with test session")
    
    # Register systems
    integration_manager.register_system(SystemType.INVENTORY, inventory_system)
    print(f"   - Registered inventory system with integration manager")
    
    # Initialize text parser
    text_parser = ParserEngine()
    integration_manager.register_system(SystemType.TEXT_PARSER, text_parser)
    
    # Connect vocabulary manager (this should trigger inventory registration)
    inventory_system.set_vocabulary_manager(text_parser.vocabulary_manager)
    print(f"   - Connected systems through integration manager")
    
    # 4. Test game systems global reference
    print("\n4. Testing GameSystemsManager global reference...")
    
    game_systems = GameSystemsManager()
    game_systems._integration_manager = integration_manager
    
    # Test vocabulary lookups again
    print(f"   - Testing vocabulary after full integration:")
    for item_id in available_items:
        if item_id in inventory_system.item_registry._items:
            item_def = inventory_system.item_registry._items[item_id]
            name = item_def.name.lower()
            item_found_id = text_parser.vocabulary_manager.get_item_id(name)
            print(f"     * '{name}': {item_found_id}")
    
    # 5. Test parser tools
    print("\n5. Testing parser tools...")
    
    # Give player some items to test with - use available items
    if available_items:
        inventory_system.give_player_item("default_player", available_items[0], 1)
        if len(available_items) > 1:
            inventory_system.give_player_item("default_player", available_items[1], 3)
        print(f"   - Added test items to player inventory")
    
    # Test inventory tool
    from text_parser.parser_engine import InventoryTool
    inventory_tool = InventoryTool()
    result = inventory_tool._run("check inventory")
    result_data = json.loads(result)
    print(f"   - InventoryTool result: {result_data.get('success', False)} - {result_data.get('system_response', 'No response')}")
    
    # Test take tool (should fail since item not in room)
    from text_parser.parser_engine import TakeTool
    take_tool = TakeTool()
    result = take_tool._run("take sword")
    result_data = json.loads(result)
    print(f"   - TakeTool result: {result_data.get('success', False)} - {result_data.get('system_response', 'No response')}")
    
    # Test drop tool - use first available item
    if available_items:
        from text_parser.parser_engine import DropTool
        drop_tool = DropTool()
        item_name = inventory_system.item_registry._items[available_items[1]].name if len(available_items) > 1 else "item"
        result = drop_tool._run(f"drop {item_name}")
        result_data = json.loads(result)
        print(f"   - DropTool result: {result_data.get('success', False)} - {result_data.get('system_response', 'No response')}")
    
    print("\n=== Integration Test Complete ===")
    
    return True

if __name__ == "__main__":
    try:
        test_inventory_vocabulary_integration()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
