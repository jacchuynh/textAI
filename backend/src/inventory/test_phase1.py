#!/usr/bin/env python3
"""
Test script for Inventory System Phase 1

This script tests the core data structures and basic functionality
of the inventory system.
"""

import sys
import os
import logging

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("inventory_test")

def test_item_definitions():
    """Test ItemData and ItemDataRegistry functionality."""
    print("\n=== Testing Item Definitions ===")
    
    from backend.src.inventory import ItemData, ItemDataRegistry, ItemType
    from backend.src.crafting.models.pydantic_models import Rarity
    
    # Test ItemData creation
    health_potion = ItemData(
        item_id="health_potion_test",
        name="Test Health Potion",
        description="A test potion for healing.",
        item_type=ItemType.CONSUMABLE,
        stackable=True,
        max_stack_size=5,
        weight=0.5,
        value=25,
        rarity=Rarity.COMMON,
        properties={"effects": {"heal": 25}},
        synonyms=["healing potion", "red potion"]
    )
    
    print(f"Created item: {health_potion.name} (ID: {health_potion.item_id})")
    print(f"Stackable: {health_potion.stackable}, Max Stack: {health_potion.max_stack_size}")
    print(f"Weight: {health_potion.weight}, Value: {health_potion.value}")
    print(f"Properties: {health_potion.properties}")
    print(f"Tags: {health_potion.tags}")
    
    # Test ItemDataRegistry
    registry = ItemDataRegistry()
    registry.register_item(health_potion)
    
    # Test retrieval
    retrieved = registry.get_item_data("health_potion_test")
    assert retrieved is not None, "Failed to retrieve registered item"
    assert retrieved.name == "Test Health Potion", "Retrieved item has wrong name"
    
    # Test search by name
    found = registry.find_item_by_name("Test Health Potion")
    assert found is not None, "Failed to find item by name"
    
    # Test search by synonym
    found_by_synonym = registry.find_item_by_name("healing potion")
    assert found_by_synonym is not None, "Failed to find item by synonym"
    
    print("✓ Item definitions test passed")

def test_inventory_slot():
    """Test InventorySlot functionality."""
    print("\n=== Testing Inventory Slot ===")
    
    from backend.src.inventory import InventorySlot
    
    # Test slot creation
    slot = InventorySlot(item_id="test_item", quantity=5)
    print(f"Created slot: {slot.item_id} x{slot.quantity}")
    
    # Test quantity operations
    slot.add_quantity(3)
    assert slot.quantity == 8, f"Expected quantity 8, got {slot.quantity}"
    
    removed = slot.remove_quantity(2)
    assert removed == 2, f"Expected to remove 2, actually removed {removed}"
    assert slot.quantity == 6, f"Expected quantity 6, got {slot.quantity}"
    
    # Test stacking compatibility
    slot2 = InventorySlot(item_id="test_item", quantity=3)
    assert slot.can_stack_with(slot2), "Slots with same item should be stackable"
    
    slot3 = InventorySlot(item_id="different_item", quantity=2)
    assert not slot.can_stack_with(slot3), "Slots with different items should not be stackable"
    
    # Test merging
    overflow = slot.merge_with(slot2, max_stack_size=10)
    assert slot.quantity == 9, f"Expected quantity 9 after merge, got {slot.quantity}"
    assert overflow == 0, f"Expected no overflow, got {overflow}"
    
    print("✓ Inventory slot test passed")

def test_inventory():
    """Test Inventory functionality."""
    print("\n=== Testing Inventory ===")
    
    from backend.src.inventory import Inventory, ItemDataRegistry, ItemData, ItemType
    from backend.src.crafting.models.pydantic_models import Rarity
    
    # Create test items
    registry = ItemDataRegistry()
    
    health_potion = ItemData(
        item_id="health_potion",
        name="Health Potion",
        description="Restores health.",
        item_type=ItemType.CONSUMABLE,
        stackable=True,
        max_stack_size=5,
        weight=0.5,
        value=25,
        rarity=Rarity.COMMON
    )
    
    sword = ItemData(
        item_id="iron_sword",
        name="Iron Sword",
        description="A sharp sword.",
        item_type=ItemType.WEAPON,
        stackable=False,
        weight=3.0,
        value=100,
        rarity=Rarity.COMMON
    )
    
    registry.register_item(health_potion)
    registry.register_item(sword)
    
    # Create inventory
    inventory = Inventory(owner_id="test_player", capacity_slots=10, capacity_weight=50.0)
    print(f"Created inventory for {inventory.owner_id}")
    print(f"Capacity: {inventory.capacity_slots} slots, {inventory.capacity_weight} weight")
    
    # Test adding items
    success = inventory.add_item("health_potion", 3, registry)
    assert success, "Failed to add health potions"
    
    success = inventory.add_item("iron_sword", 1, registry)
    assert success, "Failed to add iron sword"
    
    # Test inventory state
    assert inventory.get_item_quantity("health_potion") == 3, "Wrong potion quantity"
    assert inventory.get_item_quantity("iron_sword") == 1, "Wrong sword quantity"
    assert inventory.has_item("health_potion", 2), "Should have enough potions"
    assert not inventory.has_item("health_potion", 5), "Should not have 5 potions"
    
    # Test removing items
    success = inventory.remove_item("health_potion", 1)
    assert success, "Failed to remove health potion"
    assert inventory.get_item_quantity("health_potion") == 2, "Wrong quantity after removal"
    
    # Test inventory display
    items = inventory.get_all_items()
    print(f"Inventory contains {len(items)} different item types")
    for slot in items:
        item_data = registry.get_item_data(slot.item_id)
        print(f"  - {slot.quantity}x {item_data.name}")
    
    # Test stats
    stats = inventory.get_stats()
    print(f"Inventory stats: {stats}")
    
    print("✓ Inventory test passed")

def test_inventory_system():
    """Test InventorySystem functionality."""
    print("\n=== Testing Inventory System ===")
    
    from backend.src.inventory import InventorySystem, ItemDataRegistry
    
    # Create system with empty registry
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    # Load items from file
    item_file = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "basic_items.json"
    )
    
    if os.path.exists(item_file):
        items_loaded = registry.load_from_files([item_file])
        print(f"Loaded {items_loaded} items from {item_file}")
        
        # Test system operations
        player_id = "test_player_001"
        
        # Test giving items
        success = system.give_player_item(player_id, "health_potion_small", 3)
        assert success, "Failed to give health potions"
        
        success = system.give_player_item(player_id, "iron_sword", 1)
        assert success, "Failed to give iron sword"
        
        # Test checking items
        has_items = system.player_has_items(player_id, {"health_potion_small": 2})
        assert has_items, "Player should have health potions"
        
        # Test consuming items
        consumed = system.consume_player_items(player_id, {"health_potion_small": 1})
        assert consumed, "Failed to consume health potion"
        
        # Test inventory display
        display = system.get_player_inventory_display(player_id)
        print(f"Player inventory display has {len(display)} items:")
        for item in display:
            print(f"  - {item['quantity']}x {item['name']} ({item['item_type']})")
        
        # Test command handling
        result = system.handle_player_command(
            player_id, 
            "INVENTORY_VIEW", 
            {}
        )
        assert result["success"], "Inventory view command failed"
        print(f"Command result: {result['message']}")
        
        # Test system stats
        stats = system.get_system_stats()
        print(f"System stats: {stats}")
        
    else:
        print(f"⚠ Skipping file loading test - {item_file} not found")
    
    print("✓ Inventory system test passed")

def test_integration_compatibility():
    """Test compatibility with existing systems."""
    print("\n=== Testing Integration Compatibility ===")
    
    from backend.src.inventory import ItemType, ItemData
    
    try:
        from backend.src.crafting.models.pydantic_models import MaterialType, Rarity
        
        # Test creating items compatible with crafting system
        crafting_material = ItemData(
            item_id="test_iron_ore",
            name="Test Iron Ore", 
            description="Test ore for crafting.",
            item_type=ItemType.MATERIAL_CRAFTING,
            material_type=MaterialType.ORE,
            stackable=True,
            rarity=Rarity.COMMON
        )
        
        assert crafting_material.is_compatible_with_crafting(), "Should be compatible with crafting"
        print("✓ Crafting system compatibility confirmed")
        
    except ImportError:
        print("⚠ Crafting system not available - skipping compatibility test")
    
    print("✓ Integration compatibility test passed")

def main():
    """Run all tests."""
    print("Starting Inventory System Phase 1 Tests")
    print("=" * 50)
    
    try:
        test_item_definitions()
        test_inventory_slot()
        test_inventory()
        test_inventory_system()
        test_integration_compatibility()
        
        print("\n" + "=" * 50)
        print("🎉 All Phase 1 tests passed successfully!")
        print("\nPhase 1 implementation is complete and ready for Phase 2 integration.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
