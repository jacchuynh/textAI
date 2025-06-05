#!/usr/bin/env python3
"""
Simple debug to test the "take off ring" command specifically.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ring_command():
    try:
        # Import systems
        from backend.src.inventory.inventory_system import InventorySystem
        from backend.src.inventory.item_definitions import ItemDataRegistry, ItemData, ItemType, Rarity
        from backend.src.text_parser.parser_engine import ParserEngine
        
        print("🔍 Testing 'take off ring' command")
        print("=" * 40)
        
        # Set up minimal test environment 
        registry = ItemDataRegistry()
        
        # Register magic ring
        ring_data = ItemData(
            item_id="magic_ring",
            name="Magic Ring",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.RARE,
            value=500,
            weight=0.1,
            description="A mystical ring that glows with inner light."
        )
        registry.register_item(ring_data)
        
        # Initialize systems
        inventory_system = InventorySystem(item_registry=registry)
        parser = ParserEngine()
        
        player_id = "default_player"
        
        # Set up player with ring equipped
        inventory_system.give_player_item(player_id, "magic_ring", 1)
        equip_result = inventory_system.equip_item(player_id, "magic_ring")
        print(f"Setup: {equip_result}")
        
        # Check initial state
        equipment_display = inventory_system.get_player_equipment_display(player_id)
        print(f"Initial equipment: {equipment_display.get('message')}")
        
        # Test the command - but let's test several variations
        test_commands = [
            "take off ring",
            "remove ring", 
            "unequip ring",
            "take off magic ring"
        ]
        
        for cmd in test_commands:
            print(f"\n🧪 Testing: '{cmd}'")
            try:
                result = parser.parse(cmd)
                print(f"  Action: {result.action}")
                print(f"  Confidence: {result.confidence}")
                print(f"  System response: {result.context.get('system_response', 'None')}")
                
                # Check equipment state after command
                equipment_check = inventory_system.get_player_equipment_display(player_id)
                equipped_items = equipment_check.get('data', {}).get('equipped_items', {})
                ring_equipped = any(item and item.get('item_id') == 'magic_ring' for item in equipped_items.values())
                print(f"  Ring still equipped: {ring_equipped}")
                
                if not ring_equipped:
                    print(f"  ✅ SUCCESS: Ring was unequipped by '{cmd}'")
                    return True
                    
            except Exception as e:
                print(f"  ❌ Command '{cmd}' failed: {e}")
        
        print("\n❌ None of the test commands successfully unequipped the ring")
        return False
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ring_command()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
