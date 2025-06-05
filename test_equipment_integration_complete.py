#!/usr/bin/env python3
"""
Complete Equipment Integration Test - Phase 4C Final Verification
Tests the end-to-end equipment workflow including state management.
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_equipment_integration():
    """Test complete equipment integration workflow."""
    print("🎮 Complete Equipment Integration Test")
    print("=" * 50)
    
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
        from backend.src.text_parser.parser_engine import _game_systems
        
        # The _game_systems should already have the integration manager from initialization
        if _game_systems._integration_manager:
            from system_integration_manager import SystemType
            _game_systems._integration_manager.register_system(SystemType.INVENTORY, inventory_system)
        
        # Create test items with proper equipment properties
        test_items = [
            ItemData(
                item_id="iron_sword",
                name="Iron Sword",
                description="A sturdy iron sword for combat.",
                item_type=ItemType.WEAPON,
                rarity=Rarity.COMMON,
                weight=3.0,
                value=25,
                properties={
                    "weapon_type": "sword",
                    "damage": 8,
                    "two_handed": False,
                    "slots": ["main_hand"]
                }
            ),
            ItemData(
                item_id="leather_armor",
                name="Leather Armor",
                description="Basic leather armor for protection.",
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
                item_id="magic_ring",
                name="Magic Ring",
                description="A ring imbued with magical power.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.UNCOMMON,
                weight=0.1,
                value=50,
                properties={
                    "accessory_type": "ring",
                    "magic_bonus": 2,
                    "slots": ["ring_left", "ring_right"]
                }
            ),
            ItemData(
                item_id="wooden_shield",
                name="Wooden Shield",
                description="A basic wooden shield.",
                item_type=ItemType.SHIELD,
                rarity=Rarity.COMMON,
                weight=2.0,
                value=15,
                properties={
                    "shield_type": "light",
                    "armor": 3,
                    "slots": ["off_hand"]
                }
            )
        ]
        
        # Register items and add to inventory
        for item in test_items:
            registry.register_item(item)
        
        player_id = "default_player"
        inventory_system.update_player_location(player_id, "test_location")
        player_inventory = inventory_system.get_or_create_inventory(player_id)
        
        for item in test_items:
            player_inventory.add_item(item.item_id, 1, registry)
        
        print(f"✅ Set up test environment with {len(test_items)} items")
        
        # Test workflow: Equipment Sequence
        print("\n=== Equipment Workflow Test ===")
        
        test_sequence = [
            {
                "command": "equip iron sword",
                "description": "Equip weapon to main hand",
                "expected_equipped": ["iron_sword"]
            },
            {
                "command": "wear leather armor", 
                "description": "Equip chest armor",
                "expected_equipped": ["iron_sword", "leather_armor"]
            },
            {
                "command": "put on magic ring",
                "description": "Equip ring accessory",
                "expected_equipped": ["iron_sword", "leather_armor", "magic_ring"]
            },
            {
                "command": "equip wooden shield",
                "description": "Equip shield to off-hand",
                "expected_equipped": ["iron_sword", "leather_armor", "magic_ring", "wooden_shield"]
            }
        ]
        
        equipped_items = []
        
        for i, test in enumerate(test_sequence, 1):
            print(f"\n{i}. {test['description']}")
            print(f"   Command: '{test['command']}'")
            
            # Parse command
            result = parser.parse(test['command'])
            
            # Check if equipment was successful
            if result.context.get('system_response') and 'equip' in result.context.get('system_response', '').lower():
                print(f"   ✅ {result.context.get('system_response')}")
                
                # Get current equipment state
                equipment_display = inventory_system.get_player_equipment_display(player_id)
                if equipment_display.get('success'):
                    current_equipment = equipment_display.get('data', {}).get('equipped_items', {})
                    equipped_item_ids = [item['item_id'] for item in current_equipment.values() if item]
                    print(f"   📋 Currently equipped: {equipped_item_ids}")
                    
                    # Verify expected items are equipped
                    for expected_item in test['expected_equipped']:
                        if expected_item in equipped_item_ids:
                            print(f"   ✓ {expected_item} is equipped")
                        else:
                            print(f"   ❌ {expected_item} is NOT equipped")
            else:
                print(f"   ❌ Equipment failed: {result.context.get('system_response', 'Unknown error')}")
        
        # Test unequip sequence
        print("\n=== Unequip Workflow Test ===")
        
        unequip_sequence = [
            {
                "command": "remove iron sword",
                "description": "Unequip weapon from main hand"
            },
            {
                "command": "take off ring",
                "description": "Unequip ring accessory"
            },
            {
                "command": "unequip armor",
                "description": "Unequip chest armor"
            },
            {
                "command": "remove shield",
                "description": "Unequip shield from off-hand"
            }
        ]
        
        for i, test in enumerate(unequip_sequence, 1):
            print(f"\n{i}. {test['description']}")
            print(f"   Command: '{test['command']}'")
            
            # Parse command
            result = parser.parse(test['command'])
            
            # Check if unequip was successful
            if result.context.get('system_response'):
                print(f"   Response: {result.context.get('system_response')}")
        
        # Final equipment state check
        print("\n=== Final Equipment State ===")
        equipment_display = inventory_system.get_player_equipment_display(player_id)
        
        if equipment_display.get('success'):
            current_equipment = equipment_display.get('data', {}).get('equipped_items', {})
            equipped_items = [item for item in current_equipment.values() if item]
            
            print(f"Equipment Display Result: {equipment_display.get('message')}")
            
            if equipped_items:
                print("Currently equipped items:")
                for slot, item in current_equipment.items():
                    if item:
                        # Handle both dict formats that might be returned
                        if isinstance(item, dict):
                            item_name = item.get('name') or item.get('item_name', 'Unknown')
                            item_id = item.get('item_id', 'Unknown')
                            print(f"  {slot}: {item_name} (ID: {item_id})")
                        else:
                            print(f"  {slot}: {item}")
            else:
                print("✅ No items currently equipped")
        
        # Test inventory contents
        print("\n=== Inventory Contents Check ===")
        inventory_display = inventory_system.get_player_inventory_display(player_id)
        
        if inventory_display:
            print(f"Items in inventory: {len(inventory_display)}")
            for item in inventory_display:
                print(f"  - {item['name']} x{item['quantity']}")
        
        print("\n🎉 Complete Equipment Integration Test Finished!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_equipment_integration()
    sys.exit(0 if success else 1)
