#!/usr/bin/env python3
"""
Test Phase 3: Location-Based Inventory Integration

This test verifies that the inventory system is properly integrated with the
location container system for spatial item management.
"""

import sys
import os
import json

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.inventory import InventorySystem, ItemDataRegistry
from src.inventory.location_container_system import LocationContainerSystem, ContainerType


def test_player_location_tracking():
    """Test player location tracking functionality."""
    print("\n=== Testing Player Location Tracking ===")
    
    # Create system
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    player_id = "test_player_001"
    location1 = "village_square"
    location2 = "forest_clearing"
    
    # Test initial state
    assert system.get_player_location(player_id) is None, "Player should start without location"
    
    # Test setting location
    system.update_player_location(player_id, location1)
    assert system.get_player_location(player_id) == location1, "Location should be updated"
    
    # Test moving to new location
    system.update_player_location(player_id, location2)
    assert system.get_player_location(player_id) == location2, "Location should change"
    
    print(f"✅ Player location tracking: {player_id} in {location2}")
    # return True  # Remove return statement for pytest


def test_location_container_system_integration():
    """Test that inventory system properly integrates with location container system."""
    print("\n=== Testing Location Container System Integration ===")
    
    # Create system
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    # Load some test items
    item_file = os.path.join(
        os.path.dirname(__file__), 
        "data", 
        "basic_items.json"
    )
    
    if os.path.exists(item_file):
        items_loaded = registry.load_from_files([item_file])
        print(f"Loaded {items_loaded} items for testing")
    else:
        # Create a minimal test item if file doesn't exist
        from src.inventory.item_definitions import ItemData, ItemType, Rarity
        
        test_item = ItemData(
            item_id="test_apple",
            name="Test Apple",
            description="A red apple for testing.",
            item_type=ItemType.CONSUMABLE,
            rarity=Rarity.COMMON,
            weight=0.5,
            value=1,
            stackable=True,
            max_stack_size=10
        )
        registry.register_item(test_item)
        print("Created test item: test_apple")
    
    # Test location container system access
    location_system = system.location_container_system
    assert location_system is not None, "Location container system should be available"
    assert location_system.item_registry == registry, "Should use same item registry"
    
    print("✅ Location container system properly integrated")
    # return True  # Remove return statement for pytest


def test_location_aware_take_command():
    """Test location-aware take command."""
    print("\n=== Testing Location-Aware Take Command ===")
    
    # Create system
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    # Create test item
    from src.inventory.item_definitions import ItemData, ItemType, Rarity
    
    test_item = ItemData(
        item_id="magic_crystal",
        name="Magic Crystal",
        description="A glowing crystal.",
        item_type=ItemType.MATERIAL_MAGICAL,
        rarity=Rarity.RARE,
        weight=1.0,
        value=50,
        stackable=True,
        max_stack_size=5
    )
    registry.register_item(test_item)
    
    player_id = "test_player_002"
    location_id = "crystal_cave"
    
    # Set player location
    system.update_player_location(player_id, location_id)
    
    # Add item to location ground
    success = system.location_container_system.drop_item_at_location(
        location_id, "magic_crystal", 2
    )
    assert success, "Should be able to add item to location"
    
    # Test take command without location (should fail)
    result = system.handle_player_command(
        "player_no_location",
        "TAKE",
        {"item_name_or_id": "magic_crystal", "quantity": 1}
    )
    assert not result["success"], "Take should fail without location"
    assert "need to be in a location" in result["message"].lower()
    
    # Test take command with location
    result = system.handle_player_command(
        player_id,
        "TAKE", 
        {"item_name_or_id": "magic_crystal", "quantity": 1}
    )
    assert result["success"], f"Take should succeed: {result.get('message', '')}"
    assert result["data"]["quantity"] == 1
    assert result["data"]["item_taken"]["item_id"] == "magic_crystal"
    assert result["data"]["location"] == location_id
    
    # Verify item was removed from location and added to player
    player_inventory = system.get_or_create_inventory(player_id, "player")
    assert player_inventory.has_item("magic_crystal", 1), "Player should have the item"
    
    print("✅ Location-aware take command working correctly")
    # return True  # Remove return statement for pytest


def test_location_aware_drop_command():
    """Test location-aware drop command."""
    print("\n=== Testing Location-Aware Drop Command ===")
    
    # Create system
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    # Create test item
    from src.inventory.item_definitions import ItemData, ItemType, Rarity
    
    test_item = ItemData(
        item_id="gold_coin",
        name="Gold Coin",
        description="A shiny gold coin.",
        item_type=ItemType.CURRENCY,
        rarity=Rarity.COMMON,
        weight=0.1,
        value=1,
        stackable=True,
        max_stack_size=100
    )
    registry.register_item(test_item)
    
    player_id = "test_player_003"
    location_id = "merchant_square"
    
    # Set player location
    system.update_player_location(player_id, location_id)
    
    # Give player some coins
    system.give_player_item(player_id, "gold_coin", 5)
    
    # Test drop command without location (should fail)
    result = system.handle_player_command(
        "player_no_location",
        "DROP",
        {"item_name_or_id": "gold_coin", "quantity": 2}
    )
    assert not result["success"], "Drop should fail without location"
    assert "need to be in a location" in result["message"].lower()
    
    # Test drop command with location
    result = system.handle_player_command(
        player_id,
        "DROP",
        {"item_name_or_id": "gold_coin", "quantity": 3}
    )
    assert result["success"], f"Drop should succeed: {result.get('message', '')}"
    assert result["data"]["quantity"] == 3
    assert result["data"]["item_dropped"]["item_id"] == "gold_coin"
    assert result["data"]["location"] == location_id
    
    # Verify item was removed from player and added to location
    player_inventory = system.get_or_create_inventory(player_id, "player")
    assert player_inventory.get_item_quantity("gold_coin") == 2, "Player should have 2 coins left"
    
    # Verify item is on ground at location
    items_at_location = system.location_container_system.get_items_at_location(location_id)
    assert "gold_coin" in items_at_location["ground_items"], "Coins should be on ground"
    assert items_at_location["ground_items"]["gold_coin"]["quantity"] == 3
    
    print("✅ Location-aware drop command working correctly")
    # return True  # Remove return statement for pytest


def test_container_interaction():
    """Test taking from and dropping into containers."""
    print("\n=== Testing Container Interaction ===")
    
    # Create system
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    # Create test item
    from src.inventory.item_definitions import ItemData, ItemType, Rarity
    
    test_item = ItemData(
        item_id="healing_herbs",
        name="Healing Herbs",
        description="Fresh herbs with healing properties.",
        item_type=ItemType.CONSUMABLE,
        rarity=Rarity.COMMON,
        weight=0.2,
        value=5,
        stackable=True,
        max_stack_size=20
    )
    registry.register_item(test_item)
    
    player_id = "test_player_004"
    location_id = "herb_garden"
    
    # Set player location
    system.update_player_location(player_id, location_id)
    
    # Create a container at the location
    container_id = system.location_container_system.create_container(
        location_id=location_id,
        container_type=ContainerType.CHEST,
        name="Herb Storage Chest",
        description="A wooden chest for storing herbs.",
        capacity_slots=10,
        capacity_weight=50.0
    )
    
    # Add herbs to the container
    success = system.location_container_system.add_item_to_container(
        container_id, "healing_herbs", 5
    )
    assert success, "Should be able to add herbs to container"
    
    # Test taking from container
    result = system.handle_player_command(
        player_id,
        "TAKE",
        {"item_name_or_id": "healing_herbs", "quantity": 2, "container_id": container_id}
    )
    assert result["success"], f"Take from container should succeed: {result.get('message', '')}"
    assert result["data"]["source"] == container_id
    
    # Give player some herbs and test dropping into container
    system.give_player_item(player_id, "healing_herbs", 3)
    
    result = system.handle_player_command(
        player_id,
        "DROP",
        {"item_name_or_id": "healing_herbs", "quantity": 2, "container_id": container_id}
    )
    assert result["success"], f"Drop into container should succeed: {result.get('message', '')}"
    assert result["data"]["target"] == container_id
    
    print("✅ Container interaction working correctly")
    # return True  # Remove return statement for pytest


def test_inventory_full_scenarios():
    """Test scenarios where inventory is full."""
    print("\n=== Testing Inventory Full Scenarios ===")
    
    # Create system with small inventory
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    system.default_player_slots = 2  # Very small inventory for testing
    
    # Create test items
    from src.inventory.item_definitions import ItemData, ItemType, Rarity
    
    # Create non-stackable items to fill inventory quickly
    sword_item = ItemData(
        item_id="iron_sword",
        name="Iron Sword",
        description="A sturdy iron sword.",
        item_type=ItemType.WEAPON,
        rarity=Rarity.COMMON,
        weight=3.0,
        value=50,
        stackable=False
    )
    
    shield_item = ItemData(
        item_id="wooden_shield",
        name="Wooden Shield",
        description="A basic wooden shield.",
        item_type=ItemType.ARMOR,
        rarity=Rarity.COMMON,
        weight=2.0,
        value=30,
        stackable=False
    )
    
    gem_item = ItemData(
        item_id="ruby_gem",
        name="Ruby Gem",
        description="A precious ruby.",
        item_type=ItemType.MATERIAL_ECONOMIC,
        rarity=Rarity.RARE,
        weight=0.1,
        value=100,
        stackable=True,
        max_stack_size=10
    )
    
    registry.register_item(sword_item)
    registry.register_item(shield_item)
    registry.register_item(gem_item)
    
    player_id = "test_player_005"
    location_id = "treasure_room"
    
    # Set player location
    system.update_player_location(player_id, location_id)
    
    # Fill player inventory
    system.give_player_item(player_id, "iron_sword", 1)
    system.give_player_item(player_id, "wooden_shield", 1)
    
    # Add gem to location
    system.location_container_system.drop_item_at_location(location_id, "ruby_gem", 1)
    
    # Try to take gem with full inventory
    result = system.handle_player_command(
        player_id,
        "TAKE",
        {"item_name_or_id": "ruby_gem", "quantity": 1}
    )
    assert not result["success"], "Take should fail with full inventory"
    assert "inventory is full" in result["message"].lower()
    
    # Verify gem is still at location (should be restored)
    items_at_location = system.location_container_system.get_items_at_location(location_id)
    assert "ruby_gem" in items_at_location["ground_items"], "Gem should still be at location"
    
    print("✅ Inventory full scenarios handled correctly")
    # return True  # Remove return statement for pytest


def test_system_integration():
    """Test overall system integration status."""
    print("\n=== Testing System Integration Status ===")
    
    # Create system
    registry = ItemDataRegistry()
    system = InventorySystem(item_registry=registry)
    
    # Test system stats
    stats = system.get_system_stats()
    assert isinstance(stats, dict), "System stats should be a dictionary"
    assert "total_inventories" in stats, "Should include inventory count"
    
    # Test location container system status
    location_system = system.location_container_system
    status = location_system.get_system_status()
    assert isinstance(status, dict), "Status should be a dictionary"
    assert "total_locations" in status, "Should include location count"
    
    # Test that systems are properly connected
    assert location_system.item_registry == registry, "Should share item registry"
    
    print("✅ System integration status verified")
    # return True  # Remove return statement for pytest


def main():
    """Run all Phase 3 tests."""
    print("=" * 60)
    print("INVENTORY SYSTEM - PHASE 3 INTEGRATION TESTS")
    print("Testing Location-Based Inventory Management")
    print("=" * 60)
    
    tests = [
        test_player_location_tracking,
        test_location_container_system_integration,
        test_location_aware_take_command,
        test_location_aware_drop_command,
        test_container_interaction,
        test_inventory_full_scenarios,
        test_system_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()  # Test functions don't return True anymore (pytest style)
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("PHASE 3 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    
    if passed + failed > 0:
        print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    else:
        print("📊 Success Rate: 0.0%")
    
    if failed == 0:
        print("\n🎉 ALL PHASE 3 TESTS PASSED!")
        print("✅ Location-based inventory integration is working correctly!")
        
        # Generate completion report
        generate_phase3_completion_report()
        
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the issues above.")
        return False


def generate_phase3_completion_report():
    """Generate a completion report for Phase 3."""
    
    report = {
        "phase": "Phase 3 - Location-Based Inventory Integration",
        "completion_date": "2025-06-01",
        "status": "COMPLETE",
        "objectives_completed": [
            "✅ Player location tracking system implemented",
            "✅ Take command integrated with location container system",
            "✅ Drop command integrated with location container system",
            "✅ Container interaction (take from/drop into containers)",
            "✅ Inventory full error handling with item restoration",
            "✅ Location validation for spatial operations",
            "✅ Integration with existing LocationContainerSystem",
            "✅ Comprehensive testing suite"
        ],
        "key_features": [
            "Player location tracking (update_player_location, get_player_location)",
            "Location-aware take command with container support",
            "Location-aware drop command with container/ground support",
            "Error recovery (items restored on failed operations)",
            "Container-specific item operations",
            "Spatial validation (must be in location for operations)",
            "Integration with comprehensive LocationContainerSystem"
        ],
        "test_results": {
            "tests_run": 7,
            "tests_passed": 7,
            "tests_failed": 0,
            "success_rate": "100%"
        },
        "files_modified": [
            "backend/src/inventory/inventory_system.py (take/drop commands updated)",
            "backend/src/inventory/test_phase3.py (comprehensive test suite created)"
        ],
        "integration_points": [
            "LocationContainerSystem for spatial item management",
            "Ground item handling via drop_item_at_location/take_item_from_location",
            "Container item handling via add_item_to_container/remove_item_from_container",
            "Player location tracking for spatial operations",
            "Error recovery and item restoration"
        ]
    }
    
    # Save report
    report_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", "INVENTORY_PHASE3_COMPLETE.md")
    
    with open(report_file, "w") as f:
        f.write("# Inventory System - Phase 3 Implementation Complete ✅\n\n")
        f.write("## Executive Summary\n\n")
        f.write("**Phase 3 of the inventory system integration has been successfully completed!** ")
        f.write("The inventory system is now fully integrated with the location container system, ")
        f.write("enabling spatial item management with location-aware take and drop commands.\n\n")
        
        f.write("## Phase 3 Objectives - ✅ ALL COMPLETED\n\n")
        for objective in report["objectives_completed"]:
            f.write(f"### {objective}\n")
        
        f.write("\n## Key Features Implemented\n\n")
        for feature in report["key_features"]:
            f.write(f"- **{feature}**\n")
        
        f.write(f"\n## Test Results\n\n")
        f.write(f"- **Tests Run**: {report['test_results']['tests_run']}\n")
        f.write(f"- **Tests Passed**: {report['test_results']['tests_passed']}\n") 
        f.write(f"- **Tests Failed**: {report['test_results']['tests_failed']}\n")
        f.write(f"- **Success Rate**: {report['test_results']['success_rate']}\n")
        
        f.write(f"\n## Files Modified\n\n")
        for file_mod in report["files_modified"]:
            f.write(f"- `{file_mod}`\n")
        
        f.write(f"\n## Integration Points\n\n")
        for integration in report["integration_points"]:
            f.write(f"- {integration}\n")
        
        f.write("\n## Next Steps\n\n")
        f.write("Phase 3 is complete! The inventory system now supports:\n")
        f.write("- ✅ Spatial item management\n")
        f.write("- ✅ Location-aware commands\n") 
        f.write("- ✅ Container interactions\n")
        f.write("- ✅ Error recovery and validation\n\n")
        f.write("Consider implementing:\n")
        f.write("- Look/Search commands for location exploration\n")
        f.write("- Advanced container interactions (lock/unlock, hidden containers)\n")
        f.write("- Equipment system integration\n")
        f.write("- World state persistence\n")
    
    print(f"\n📋 Phase 3 completion report saved to: {report_file}")


if __name__ == "__main__":
    main()
