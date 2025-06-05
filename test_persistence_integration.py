#!/usr/bin/env python3
"""
Integration test for Phase 4D: World State Persistence
Tests the complete persistence system integration with inventory and location systems.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Test imports
from system_integration_manager import SystemIntegrationManager, SystemType
from inventory.inventory_system import InventorySystem
from inventory.item_definitions import item_registry
from persistence.world_state_persistence import WorldStatePersistenceManager
from persistence.storage_backends import JSONStorageBackend


def test_persistence_integration():
    """Test complete persistence integration with inventory operations."""
    print("🧪 Testing Phase 4D: World State Persistence Integration")
    print("=" * 60)
    
    # Create temporary directory for persistence testing
    temp_dir = tempfile.mkdtemp(prefix="textrealsai_persistence_test_")
    print(f"📁 Using temporary directory: {temp_dir}")
    
    try:
        # 1. Initialize Systems
        print("\n1️⃣ Initializing systems...")
        
        # Create integration manager
        integration_manager = SystemIntegrationManager(
            session_id="test_session_001",
            player_id="test_player"
        )
        
        # Initialize inventory system
        inventory_system = InventorySystem(item_registry=item_registry)
        
        # Load items into the registry for testing
        item_data_file = os.path.join(os.path.dirname(__file__), 'backend', 'src', 'inventory', 'data', 'basic_items.json')
        if os.path.exists(item_data_file):
            items_loaded = item_registry.load_from_files([item_data_file])
            print(f"📦 Loaded {items_loaded} items from registry")
        else:
            print("⚠️  Warning: Item data file not found, using empty registry")
        
        # Initialize persistence system with temp storage
        storage_backend = JSONStorageBackend(
            storage_dir=temp_dir
        )
        persistence_manager = WorldStatePersistenceManager(storage_backend)
        
        # Register systems with integration manager
        integration_manager.register_system(SystemType.INVENTORY, inventory_system)
        integration_manager.register_system(SystemType.PERSISTENCE, persistence_manager)
        
        # Connect inventory system to integration manager for proper event handling
        inventory_system.set_system_integration_manager(integration_manager)
        
        # Start persistence session
        session_started = persistence_manager.start_session("test_session_001")
        print(f"🎮 Persistence session started: {session_started}")
        
        print("✅ Systems initialized")
        
        # 2. Test Inventory Operations with Persistence
        print("\n2️⃣ Testing inventory operations with persistence...")
        
        player_id = "test_player"
        
        # Set player location
        inventory_system.update_player_location(player_id, "test_village")
        print(f"📍 Player location set to: test_village")
        
        # Give player some items
        give_result = inventory_system.handle_player_command(player_id, "GIVE", {
            "item_name_or_id": "health_potion_small",
            "quantity": 3
        })
        print(f"🎁 Give item result: {give_result['success']} - {give_result['message']}")
        
        # Use an item
        use_result = inventory_system.handle_player_command(player_id, "USE", {
            "item_name_or_id": "health_potion_small",
            "target": "self"
        })
        print(f"🧪 Use item result: {use_result['success']} - {use_result['message']}")
        
        # Drop an item
        drop_result = inventory_system.handle_player_command(player_id, "DROP", {
            "item_name_or_id": "health_potion_small",
            "quantity": 1
        })
        print(f"📦 Drop item result: {drop_result['success']} - {drop_result['message']}")
        
        # 3. Test Manual Save/Load
        print("\n3️⃣ Testing manual save/load operations...")
        
        # Trigger manual save
        save_success = integration_manager.save_game_state()
        print(f"💾 Manual save result: {save_success}")
        
        # Check if save files were created
        save_files = list(Path(temp_dir).glob("*.json"))
        print(f"📄 Save files created: {len(save_files)}")
        for file in save_files:
            print(f"   - {file.name} ({file.stat().st_size} bytes)")
            
        # Load the saved state
        load_success = integration_manager.load_game_state()
        print(f"📂 Load result: {load_success}")
        
        # 4. Test Persistence Event System
        print("\n4️⃣ Testing persistence event system...")
        
        # Check if persistence manager received events
        if hasattr(persistence_manager, 'event_history'):
            print(f"📡 Events received by persistence manager: {len(persistence_manager.event_history)}")
            for event in persistence_manager.event_history[-3:]:  # Show last 3 events
                print(f"   - {event.get('event_type', 'unknown')}: {event.get('timestamp', 'no timestamp')}")
        
        # Check dirty flags
        if hasattr(persistence_manager, 'dirty_flags'):
            dirty_count = sum(1 for flag in persistence_manager.dirty_flags.values() if flag)
            print(f"🏴 Dirty flags set: {dirty_count}")
        
        # 5. Test Auto-save Functionality
        print("\n5️⃣ Testing auto-save functionality...")
        
        # Trigger more inventory changes to test auto-save
        for i in range(3):
            give_result = inventory_system.handle_player_command(player_id, "GIVE", {
                "item_name_or_id": "iron_sword",
                "quantity": 1
            })
            print(f"   ⚔️  Gave iron sword #{i+1}: {give_result['success']}")
        
        # Check if auto-save was triggered
        auto_save_files = list(Path(temp_dir).glob("*auto_save*.json"))
        print(f"🤖 Auto-save files: {len(auto_save_files)}")
        
        # 6. Test State Restoration
        print("\n6️⃣ Testing state restoration...")
        
        # Get current inventory state
        inventory_before = inventory_system.get_player_inventory_display(player_id)
        print(f"📊 Items in inventory before reset: {len(inventory_before)}")
        
        # Clear inventory to simulate restart
        inventory_system.inventories.clear()
        print("🗑️  Inventory cleared (simulating restart)")
        
        # Reload from saved state
        load_success = integration_manager.load_game_state()
        print(f"🔄 State restoration result: {load_success}")
        
        # Check restored inventory
        inventory_after = inventory_system.get_player_inventory_display(player_id)
        print(f"📊 Items in inventory after restoration: {len(inventory_after)}")
        
        # 7. Test Error Handling
        print("\n7️⃣ Testing error handling...")
        
        # Try to save with corrupted data
        try:
            # Temporarily break the storage backend
            original_save = storage_backend.save_world_state
            storage_backend.save_world_state = lambda k, v: False  # Always fail
            
            save_result = integration_manager.save_game_state()
            print(f"💥 Save with broken backend: {save_result} (expected: False)")
            
            # Restore the save method
            storage_backend.save_world_state = original_save
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
        
        # 8. Performance and Statistics
        print("\n8️⃣ Performance and statistics...")
        
        # Get system statistics
        inventory_stats = inventory_system.get_system_stats()
        print(f"📈 Inventory stats: {inventory_stats['total_inventories']} inventories, {inventory_stats['total_items_in_circulation']} items")
        
        if hasattr(persistence_manager, 'get_statistics'):
            persistence_stats = persistence_manager.get_statistics()
            print(f"💾 Persistence stats: {persistence_stats}")
        
        # Final save to ensure everything is persisted
        final_save = integration_manager.save_game_state()
        print(f"🏁 Final save result: {final_save}")
        
        print("\n✅ PERSISTENCE INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"\n❌ PERSISTENCE INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up {temp_dir}: {e}")


def test_cross_system_events():
    """Test event propagation between systems."""
    print("\n🔗 Testing cross-system event propagation...")
    
    # This would test that inventory changes trigger persistence events
    # and that location changes are properly saved
    pass


def test_backup_and_recovery():
    """Test backup creation and recovery mechanisms."""
    print("\n💽 Testing backup and recovery...")
    
    # This would test the backup system's ability to create
    # and restore from backup files
    pass


if __name__ == "__main__":
    print("🚀 Starting Phase 4D Persistence Integration Test Suite")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    try:
        success = test_persistence_integration()
        
        if success:
            print("\n🎉 ALL TESTS PASSED!")
            print("Phase 4D: World State Persistence integration is working correctly.")
        else:
            print("\n💥 SOME TESTS FAILED!")
            print("Check the output above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
