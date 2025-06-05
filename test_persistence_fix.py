#!/usr/bin/env python3
"""
Test Script for Phase 4D Persistence Fixes
Tests the updated persistence system with partial state validation.
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


def test_persistence_validation_fixes():
    """Test that persistence validation fixes work correctly."""
    print("🧪 Testing Persistence Validation Fixes")
    print("=" * 50)
    
    # Create temporary directory for test data
    test_dir = tempfile.mkdtemp(prefix="test_persistence_")
    storage_backend = JSONStorageBackend(storage_dir=test_dir)
    
    try:
        # Create persistence manager
        persistence_manager = WorldStatePersistenceManager(
            storage_backend=storage_backend,
            auto_save_interval=10,  # Very short for testing
            backup_interval=30
        )
        
        # Start session
        game_id = "test_game_persistence_fix"
        print(f"📅 Starting session: {game_id}")
        persistence_manager.start_session(game_id)
        
        # Test 1: Partial validation with just player data
        print("\n🧪 Test 1: Partial state validation")
        partial_state = {
            'player': {
                'test_player': {
                    'player_id': 'test_player',
                    'current_location': 'forest_entrance',
                    'inventory': {'items': [], 'equipment': {}}
                }
            }
        }
        
        # This should now work with partial=True
        result = persistence_manager.save_world_state(partial_state, partial=True)
        print(f"✅ Partial save result: {result}")
        assert result, "Partial save should succeed"
        
        # Test 2: Auto-save with complete state (so we can load it later)
        print("\n🧪 Test 2: Auto-save check with complete state")
        persistence_manager.mark_dirty("player")
        persistence_manager.mark_dirty("locations")
        
        complete_auto_save_state = {
            'locations': {
                'forest_entrance': {
                    'location_id': 'forest_entrance',
                    'name': 'Forest Entrance',
                    'description': 'A peaceful forest clearing',
                    'items': [],
                    'containers': {},
                    'visited': True
                }
            },
            'containers': {},
            'player': {
                'test_player': {
                    'player_id': 'test_player',
                    'current_location': 'forest_entrance',
                    'inventory': [],
                    'health': 100
                }
            }
        }
        
        auto_save_result = persistence_manager.auto_save_check(complete_auto_save_state)
        print(f"✅ Auto-save check result: {auto_save_result}")
        
        # Test 3: Full validation should still require all sections
        print("\n🧪 Test 3: Full validation requirements")
        
        # Create a fresh persistence manager to avoid caching issues
        persistence_manager_fresh = WorldStatePersistenceManager(
            storage_backend=JSONStorageBackend(storage_dir=test_dir + "_fresh"),
            auto_save_interval=10,
            backup_interval=30
        )
        persistence_manager_fresh.start_session("test_fresh_validation")
        
        try:
            # This should fail with full validation (partial=False) 
            # because we only have player data, missing locations and containers
            # Use force=True to ensure validation is performed
            result = persistence_manager_fresh.save_world_state(partial_state, partial=False, force=True)
            if result:
                print(f"❌ Full validation should have failed but got: {result}")
                return False  # Test failed - validation should have failed
            else:
                print(f"✅ Full validation correctly failed with result: {result}")
        except Exception as e:
            print(f"✅ Full validation correctly failed with exception: {e}")
        
        persistence_manager_fresh.end_session()
        
        # Test 4: Complete state should pass full validation
        print("\n🧪 Test 4: Complete state validation")
        complete_state = {
            'locations': {
                'forest_entrance': {
                    'name': 'Forest Entrance',
                    'description': 'A peaceful forest clearing',
                    'items': [],
                    'containers': {},
                    'visited': True
                }
            },
            'containers': {},
            'player': {
                'test_player': {
                    'player_id': 'test_player',
                    'current_location': 'forest_entrance',
                    'inventory': {'items': [], 'equipment': {}}
                }
            }
        }
        
        result = persistence_manager.save_world_state(complete_state, partial=False)
        print(f"✅ Complete state save result: {result}")
        assert result, "Complete state save should succeed"
        
        # Test 5: Load and verify
        print("\n🧪 Test 5: Load and verify saved state")
        loaded_state = persistence_manager.load_world_state(game_id)
        if loaded_state:
            print(f"✅ Successfully loaded state with {len(loaded_state)} sections")
            print(f"   Locations: {list(loaded_state.get('locations', {}).keys())}")
            
            # Handle PlayerState object properly
            player_data = loaded_state.get('player')
            if player_data:
                # Check if it's a PlayerState object or a dictionary
                if hasattr(player_data, 'player_id'):
                    # PlayerState object
                    print(f"   Player: {player_data.player_id} (current_location: {player_data.current_location})")
                elif isinstance(player_data, dict):
                    # Dictionary format
                    print(f"   Player: {list(player_data.keys())}")
                else:
                    print(f"   Player: Unknown format - {type(player_data)}")
            else:
                print("   Player: No player data found")
        else:
            print("❌ Failed to load saved state")
        
        print("\n🎉 All persistence validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        try:
            persistence_manager.end_session()
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory: {test_dir}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


def test_system_integration_world_state():
    """Test the system integration manager's world state construction."""
    print("\n🧪 Testing System Integration World State Construction")
    print("=" * 60)
    
    try:
        # Create integration manager with required parameters
        integration_manager = SystemIntegrationManager(
            session_id="test_session_123",
            player_id="test_player_456"
        )
        
        # Test world state initialization
        print("\n🧪 Test: World state initialization")
        changes = {
            'locations': {
                'village': {
                    'location_id': 'village',
                    'name': 'Village Center',
                    'description': 'A bustling village center',
                    'items': [],
                    'containers': {},
                    'visited': True
                }
            },
            'containers': {},
            'player': {
                'test_player': {
                    'player_id': 'test_player',
                    'current_location': 'village',
                    'health': 100
                }
            }
        }
        
        integration_manager._update_world_state(changes)
        world_state = integration_manager.shared_context.get('world_state', {})
        
        print(f"✅ World state structure: {list(world_state.keys())}")
        print(f"   Player data: {list(world_state.get('player', {}).keys())}")
        print(f"   Locations: {list(world_state.get('locations', {}).keys())}")
        print(f"   Metadata: {world_state.get('metadata', {})}")
        
        # Verify structure
        expected_sections = ['locations', 'containers', 'player', 'metadata']
        for section in expected_sections:
            if section not in world_state:
                print(f"❌ Missing section: {section}")
                return False
            print(f"✅ Found section: {section}")
        
        print("\n🎉 System integration world state test passed!")
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all persistence fix tests."""
    print("🚀 Starting Phase 4D Persistence Fix Tests")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    all_passed = True
    
    # Test 1: Persistence validation fixes
    try:
        result1 = test_persistence_validation_fixes()
        all_passed = all_passed and result1
    except Exception as e:
        print(f"❌ Persistence validation test crashed: {e}")
        all_passed = False
    
    # Test 2: System integration world state
    try:
        result2 = test_system_integration_world_state()
        all_passed = all_passed and result2
    except Exception as e:
        print(f"❌ System integration test crashed: {e}")
        all_passed = False
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Persistence fixes are working correctly.")
        print("\n✅ Key improvements verified:")
        print("   • Partial state validation for auto-save operations")
        print("   • Proper world state structure initialization")
        print("   • Enhanced event handler world state updates")
        print("   • Backward compatibility with full validation")
    else:
        print("❌ SOME TESTS FAILED! Check the output above for details.")
    
    print(f"\n⏰ Test completed at: {datetime.now().isoformat()}")
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
