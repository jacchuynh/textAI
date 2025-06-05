#!/usr/bin/env python3
"""
Simple test to debug the 'take off ring' command parsing issue
"""

import sys
import os
sys.path.insert(0, '/Users/jacc/Downloads/TextRealmsAI')

def test_ring_command_simple():
    """Test just the 'take off ring' command parsing"""
    try:
        # Import required systems
        from backend.src.inventory.inventory_system import InventorySystem
        from backend.src.inventory.item_definitions import ItemDataRegistry, ItemData, ItemType, Rarity
        from backend.src.text_parser.parser_engine import ParserEngine
        from system_integration_manager import SystemIntegrationManager, SystemType
        
        print("🔍 Simple Ring Command Debug Test")
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
        from system_integration_manager import SystemType
        integration_manager = _game_systems._integration_manager
        if integration_manager:
            integration_manager.register_system(SystemType.INVENTORY, inventory_system)
        
        parser = ParserEngine()
        
        # Set up player with ring equipped
        player_id = "default_player"
        inventory_system.give_player_item(player_id, "magic_ring", 1)
        equip_result = inventory_system.handle_player_command(
            player_id, "EQUIP", {"item_name": "Magic Ring"}
        )
        print(f"✅ Setup: {equip_result.get('message')}")
        
        # Check initial equipment state
        equipment_display = inventory_system.get_player_equipment_display(player_id)
        print(f"Initial equipment: {equipment_display.get('message')}")
        
        # Test the problematic command
        print("\n🧪 Testing: 'take off ring'")
        result = parser.parse("take off ring")
        
        print(f"✏️ Parser result:")
        print(f"   Action: {result.action}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Raw text: {result.raw_text}")
        
        if hasattr(result, 'context') and result.context:
            print(f"   Context keys: {list(result.context.keys())}")
            if 'system_response' in result.context:
                print(f"   System response: {result.context['system_response']}")
        
        # Check if equipment changed
        final_equipment = inventory_system.get_player_equipment_display(player_id)
        print(f"\nFinal equipment: {final_equipment.get('message')}")
        
        # Check if ring is still equipped
        equipped_items = final_equipment.get('data', {}).get('equipped_items', {})
        ring_still_equipped = any(item and item.get('item_id') == 'magic_ring' for item in equipped_items.values())
        
        if ring_still_equipped:
            print("❌ CONFIRMED: Ring is still equipped after 'take off ring' command")
            print("🔧 The command was not processed properly")
        else:
            print("✅ SUCCESS: Ring was successfully unequipped")
            
        return not ring_still_equipped
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ring_command_simple()
