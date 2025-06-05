#!/usr/bin/env python3
"""
Test equipment parser integration - Phase 4C
Tests natural language equipment commands through the parser system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_equipment_parser():
    """Test equipment commands through the parser system."""
    print("🎮 Equipment Parser Integration Test")
    print("=" * 40)
    
    try:
        # Import required systems
        from backend.src.inventory.inventory_system import InventorySystem
        from backend.src.inventory.item_definitions import ItemDataRegistry, ItemData, ItemType, Rarity
        from backend.src.text_parser.parser_engine import ParserEngine
        
        print("✅ Imported systems")
        
        # Set up test environment
        registry = ItemDataRegistry()
        inventory_system = InventorySystem(item_registry=registry)
        parser = ParserEngine()
        
        # Set up parser with inventory system
        # The parser uses a global _game_systems instance that gets auto-initialized
        from backend.src.text_parser.parser_engine import _game_systems
        
        # The _game_systems should already have the integration manager from initialization
        # We just need to ensure our inventory system is available via the integration manager
        if _game_systems._integration_manager:
            from system_integration_manager import SystemType
            _game_systems._integration_manager.register_system(SystemType.INVENTORY, inventory_system)
        
        # Create test items
        test_items = [
            ItemData(
                item_id="iron_sword",
                name="Iron Sword",
                description="A sturdy iron sword.",
                item_type=ItemType.WEAPON,
                rarity=Rarity.COMMON,
                weight=3.0,
                value=25,
                properties={
                    "weapon_type": "sword",
                    "damage": 8,
                    "two_handed": False
                }
            ),
            ItemData(
                item_id="leather_armor",
                name="Leather Armor",
                description="Basic leather armor.",
                item_type=ItemType.ARMOR,
                rarity=Rarity.COMMON,
                weight=8.0,
                value=20,
                properties={
                    "armor_type": "chest",
                    "armor": 5,
                    "slots": ["chest"]
                }
            ),
            ItemData(
                item_id="silver_ring",
                name="Silver Ring",
                description="A simple silver ring.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.COMMON,
                weight=0.1,
                value=15,
                properties={
                    "accessory_type": "ring",
                    "magic_bonus": 1
                }
            )
        ]
        
        # Register items and add to inventory
        for item in test_items:
            registry.register_item(item)
        
        player_id = "default_player"  # Match what the parser tools expect
        inventory_system.update_player_location(player_id, "test_location")
        player_inventory = inventory_system.get_or_create_inventory(player_id)
        
        for item in test_items:
            player_inventory.add_item(item.item_id, 1, registry)
        
        print(f"✅ Set up test environment with {len(test_items)} items")
        
        # Test natural language equipment commands
        test_commands = [
            "equip iron sword",
            "wear leather armor", 
            "put on silver ring",
            "check my equipment",
            "remove iron sword",
            "take off ring",
            "unequip armor",
            "show my equipment"
        ]
        
        print("\n=== Testing Natural Language Commands ===")
        
        for command in test_commands:
            print(f"\n🗣️ Testing: '{command}'")
            
            try:
                # Mock the conversation state that parser expects
                conversation_state = {
                    'player_id': player_id,
                    'location': 'test_location',
                    'context': {}
                }
                
                # Process command through parser using the correct method
                result = parser.parse(command)
                print(f"   📝 Parser Result: {result}")
                
                # Also test the direct tool call
                if "equip" in command.lower() and "unequip" not in command.lower():
                    from backend.src.text_parser.parser_engine import EquipTool
                    tool = EquipTool()
                    tool_result = tool._run(command)
                    print(f"   🔧 EquipTool Result: {tool_result}")
                    
                elif "remove" in command.lower() or "take off" in command.lower() or "unequip" in command.lower():
                    from backend.src.text_parser.parser_engine import UnequipTool
                    tool = UnequipTool()
                    tool_result = tool._run(command)
                    print(f"   🔧 UnequipTool Result: {tool_result}")
                    
                elif "equipment" in command.lower() or "gear" in command.lower():
                    # Test equipment display
                    equipment_display = inventory_system.get_player_equipment_display(player_id)
                    print(f"   📋 Equipment Display: {equipment_display['message']}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n🎉 Equipment Parser Integration Test Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_equipment_parser()
