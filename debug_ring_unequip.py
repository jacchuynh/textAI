#!/usr/bin/env python3
"""
Debug script to test the specific "take off ring" command that failed in the integration test.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_ring_unequip():
    try:
        # Import systems
        from backend.src.inventory.inventory_system import InventorySystem
        from backend.src.inventory.item_definitions import ItemDataRegistry, ItemData, ItemType, Rarity
        from backend.src.text_parser.parser_engine import ParserEngine
        from system_integration_manager import SystemIntegrationManager
        
        print("🔍 Debug: Ring Unequip Command")
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
            description="A mystical ring that glows with inner light."
        )
        registry.register_item(ring_data)
        
        # Initialize systems
        inventory_system = InventorySystem(item_registry=registry)
        parser = ParserEngine()
        
        # Initialize integration (use existing game systems manager)
        from backend.src.text_parser.parser_engine import _game_systems
        integration_manager = _game_systems._integration_manager
        if integration_manager:
            integration_manager.register_system("inventory", inventory_system)
        
        player_id = "default_player"
        
        # Set up player with ring equipped
        inventory_system.add_item_to_player(player_id, "magic_ring", 1)
        equip_result = inventory_system.equip_item(player_id, "magic_ring")
        print(f"✅ Setup: {equip_result}")
        
        # Check initial equipment state
        equipment_display = inventory_system.get_player_equipment_display(player_id)
        print(f"Initial equipment: {equipment_display.get('message')}")
        
        # Test the problematic command
        print("\n🧪 Testing: 'take off ring'")
        result = parser.parse("take off ring")
        
        print(f"Parser result: {result}")
        print(f"Action: {result.action}")
        print(f"Context: {result.context}")
        print(f"Confidence: {result.confidence}")
        
        if hasattr(result, 'system_response'):
            print(f"System response: {result.system_response}")
        
        # Check final equipment state
        final_equipment = inventory_system.get_player_equipment_display(player_id)
        print(f"\nFinal equipment: {final_equipment.get('message')}")
        
        # Check if ring is still equipped
        equipped_items = final_equipment.get('data', {}).get('equipped_items', {})
        ring_still_equipped = any(item and item.get('item_id') == 'magic_ring' for item in equipped_items.values())
        
        if ring_still_equipped:
            print("❌ ISSUE CONFIRMED: Ring is still equipped after 'take off ring' command")
        else:
            print("✅ SUCCESS: Ring was successfully unequipped")
            
        return not ring_still_equipped
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_ring_unequip()
    print(f"\nDebug result: {'SUCCESS' if success else 'FAILED'}")
