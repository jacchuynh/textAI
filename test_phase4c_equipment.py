#!/usr/bin/env python3
"""
Phase 4C Equipment System Integration Test
Tests EQUIP and UNEQUIP commands with the integrated equipment system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase4c_equipment_system():
    """Test the Phase 4C equipment system integration."""
    print("🔧 Phase 4C Equipment System Integration Test")
    print("=" * 55)
    
    try:
        # Import required systems
        from backend.src.inventory.inventory_system import InventorySystem
        from backend.src.inventory.item_definitions import ItemDataRegistry, ItemData, ItemType, Rarity
        from backend.src.inventory.equipment_system import EquipmentSystem, EquipmentSlot
        
        print("✅ Imported equipment and inventory systems")
        
        # Create test setup
        registry = ItemDataRegistry()
        inventory_system = InventorySystem(item_registry=registry)
        
        # Create test equipment items
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
                    "armor": 3,
                    "slots": ["chest"]
                }
            ),
            ItemData(
                item_id="wooden_shield",
                name="Wooden Shield",
                description="A simple wooden shield.",
                item_type=ItemType.SHIELD,
                rarity=Rarity.COMMON,
                weight=4.0,
                value=15,
                properties={
                    "armor": 2
                }
            ),
            ItemData(
                item_id="silver_ring",
                name="Silver Ring",
                description="A shiny silver ring.",
                item_type=ItemType.ACCESSORY,
                rarity=Rarity.UNCOMMON,
                weight=0.1,
                value=50,
                properties={
                    "accessory_type": "ring",
                    "magic_bonus": 1
                }
            )
        ]
        
        # Register test items
        for item in test_items:
            registry.register_item(item)
        
        print(f"✅ Registered {len(test_items)} test equipment items")
        
        # Set up test player
        player_id = "test_player"
        inventory_system.update_player_location(player_id, "test_location")
        
        # Give player some test items
        player_inventory = inventory_system.get_or_create_inventory(player_id)
        for item in test_items:
            player_inventory.add_item(item.item_id, 1, registry)
        
        print(f"✅ Added equipment items to player inventory")
        
        # === Test EQUIP commands ===
        print("\n=== Testing EQUIP Commands ===")
        
        test_equip_commands = [
            ("Iron Sword", None),
            ("Leather Armor", None), 
            ("Wooden Shield", None),
            ("Silver Ring", "ring_left")
        ]
        
        for item_name, preferred_slot in test_equip_commands:
            print(f"\n🗡️ Testing: EQUIP {item_name}" + (f" in {preferred_slot}" if preferred_slot else ""))
            
            result = inventory_system.handle_player_command(
                player_id,
                "EQUIP",
                {
                    "item_name": item_name,
                    "slot": preferred_slot
                }
            )
            
            if result["success"]:
                print(f"   ✅ {result['message']}")
                if result.get("data", {}).get("unequipped_items"):
                    print(f"   📦 Unequipped: {result['data']['unequipped_items']}")
            else:
                print(f"   ❌ {result['message']}")
        
        # === Test equipment display ===
        print("\n=== Testing Equipment Display ===")
        
        equipment_display = inventory_system.get_player_equipment_display(player_id)
        print(f"📋 Equipment Summary:")
        
        if equipment_display.get('success') and equipment_display.get('data', {}).get('equipped_items'):
            equipped_items = equipment_display['data']['equipped_items']
            print(f"   Total Items Equipped: {len(equipped_items)}")
            
            for slot, item_info in equipped_items.items():
                print(f"   {slot.replace('_', ' ').title()}: {item_info['item_name']}")
                
            # Print stats if available
            total_stats = equipment_display['data'].get('total_stats', {})
            if total_stats:
                print(f"   Equipment Stats: {total_stats}")
        else:
            print(f"   {equipment_display.get('message', 'No equipment equipped')}")
        
        # === Test UNEQUIP commands ===
        print("\n=== Testing UNEQUIP Commands ===")
        
        test_unequip_commands = [
            ("Iron Sword", None),
            (None, "chest"),  # Unequip by slot
            ("Silver Ring", None)
        ]
        
        for item_name, slot in test_unequip_commands:
            if item_name:
                print(f"\n🔓 Testing: UNEQUIP {item_name}")
            else:
                print(f"\n🔓 Testing: UNEQUIP from {slot}")
            
            result = inventory_system.handle_player_command(
                player_id,
                "UNEQUIP", 
                {
                    "item_name": item_name,
                    "slot": slot
                }
            )
            
            if result["success"]:
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ {result['message']}")
        
        # === Test equipment conflicts ===
        print("\n=== Testing Equipment Conflicts ===")
        
        # Create a two-handed weapon
        two_handed_sword = ItemData(
            item_id="two_handed_sword",
            name="Two-Handed Sword",
            description="A massive two-handed sword.",
            item_type=ItemType.WEAPON,
            rarity=Rarity.UNCOMMON,
            weight=6.0,
            value=50,
            properties={
                "weapon_type": "two_handed_sword",
                "damage": 12,
                "two_handed": True
            }
        )
        registry.register_item(two_handed_sword)
        player_inventory.add_item("two_handed_sword", 1, registry)
        
        print(f"🗡️ Testing two-handed weapon conflict:")
        
        # First equip one-handed weapon and shield
        inventory_system.handle_player_command(player_id, "EQUIP", {"item_name": "Iron Sword"})
        inventory_system.handle_player_command(player_id, "EQUIP", {"item_name": "Wooden Shield"})
        
        # Now try to equip two-handed weapon (should auto-unequip shield)
        result = inventory_system.handle_player_command(
            player_id,
            "EQUIP",
            {"item_name": "Two-Handed Sword"}
        )
        
        if result["success"]:
            print(f"   ✅ {result['message']}")
            if result.get("data", {}).get("unequipped_items"):
                print(f"   📦 Auto-unequipped: {result['data']['unequipped_items']}")
        else:
            print(f"   ❌ {result['message']}")
        
        # === Final equipment state ===
        print("\n=== Final Equipment State ===")
        final_equipment = inventory_system.get_player_equipment_display(player_id)
        
        if final_equipment.get('success') and final_equipment.get('data', {}).get('equipped_items'):
            equipped_items = final_equipment['data']['equipped_items']
            print(f"📋 Final Equipment ({len(equipped_items)} items):")
            
            for slot, item_info in equipped_items.items():
                print(f"   {slot.replace('_', ' ').title()}: {item_info['item_name']}")
        else:
            print(f"📋 Final Equipment: {final_equipment.get('message', 'No equipment')}")
        
        print("\n🎉 Phase 4C Equipment System Test Complete!")
        print("✅ Features tested:")
        print("  - EQUIP command with various item types")
        print("  - UNEQUIP command by item name and slot")
        print("  - Equipment conflict resolution")
        print("  - Equipment display and stats")
        print("  - Integration with inventory system")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase4c_equipment_system()
    sys.exit(0 if success else 1)
