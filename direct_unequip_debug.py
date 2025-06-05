#!/usr/bin/env python3
"""
Debug script to directly test the unequip tool for the "take off ring" command
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_unequip_tool():
    try:
        # Import required systems
        from backend.src.inventory.inventory_system import InventorySystem
        from backend.src.inventory.item_definitions import ItemDataRegistry, ItemData, ItemType, Rarity
        from backend.src.text_parser.parser_engine import UnequipTool, TakeTool
        from system_integration_manager import SystemIntegrationManager, SystemType
        
        print("🔍 Direct UnequipTool Debug Test")
        print("=" * 40)
        
        # Set up test environment
        registry = ItemDataRegistry()
        
        # Register magic ring
        ring_data = ItemData(
            item_id="magic_ring",
            name="Magic Ring",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.RARE,
            value=500,
            weight=0.1,
            description="A mystical ring that glows with inner light.",
            properties={"accessory_type": "ring"}
        )
        registry.register_item(ring_data)
        
        # Initialize systems
        inventory_system = InventorySystem(item_registry=registry)
        
        # Use the existing global systems integration
        from backend.src.text_parser.parser_engine import _game_systems
        integration_manager = _game_systems._integration_manager
        if integration_manager:
            integration_manager.register_system(SystemType.INVENTORY, inventory_system)
        
        player_id = "default_player"
        
        # Set up player with ring equipped
        inventory_system.give_player_item(player_id, "magic_ring", 1)
        equip_result = inventory_system.handle_player_command(
            player_id, "EQUIP", {"item_name": "Magic Ring"}
        )
        print(f"✅ Setup: {equip_result}")
        
        # Check initial equipment state
        equipment_display = inventory_system.get_player_equipment_display(player_id)
        print(f"Initial equipment: {equipment_display.get('message')}")
        
        # Create the tools
        unequip_tool = UnequipTool()
        take_tool = TakeTool()
        
        # Test commands
        test_commands = [
            "take off ring",
            "take the ring off",
            "remove ring",
            "unequip ring"
        ]
        
        for cmd in test_commands:
            print(f"\n🧪 Testing direct tool call: '{cmd}'")
            
            # First try the take tool to see if it detects and redirects
            take_result = take_tool._run(cmd)
            take_data = json.loads(take_result)
            print(f"TakeTool result: {take_data.get('action')} (redirect: {take_data.get('redirect_to', None)})")
            
            # Then test the unequip tool directly
            unequip_result = unequip_tool._run(cmd)
            unequip_data = json.loads(unequip_result)
            print(f"UnequipTool result: success={unequip_data.get('success')}")
            print(f"UnequipTool message: {unequip_data.get('system_response')}")
            
            # Check equipment state
            check_equip = inventory_system.get_player_equipment_display(player_id)
            print(f"Current equipment: {check_equip.get('message')}")
            
            # Check if ring is still equipped
            equipped_items = check_equip.get('data', {}).get('equipped_items', {})
            ring_still_equipped = any(item and item.get('item_id') == 'magic_ring' for item in equipped_items.values())
            
            if ring_still_equipped:
                print("❌ Still equipped after command")
            else:
                print("✅ Successfully unequipped")
                
            # Re-equip for next test if needed
            if not ring_still_equipped and len(test_commands) > 1:
                inventory_system.handle_player_command(
                    player_id, "EQUIP", {"item_name": "Magic Ring"}
                )
                
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_unequip_tool()
    print(f"\nDebug result: {'SUCCESS' if success else 'FAILED'}")
