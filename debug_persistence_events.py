#!/usr/bin/env python3
"""
Debug script to trace persistence event flow
"""

import os
import sys
import logging
import tempfile
import shutil

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'backend', 'src'))

from system_integration_manager import SystemIntegrationManager

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_event_flow():
    """Test and trace persistence event flow."""
    print("🔍 Debugging Persistence Event Flow")
    print("="*50)
    
    try:
        # Initialize systems with debug logging
        print("\n1️⃣ Initializing systems...")
        manager = SystemIntegrationManager("debug_session", "debug_player")
        
        from system_integration_manager import SystemType
        
        inventory_system = manager.systems.get(SystemType.INVENTORY)
        persistence_system = manager.systems.get(SystemType.PERSISTENCE)
        
        if not inventory_system:
            print("❌ Inventory system not available")
            return False
        
        if not persistence_system:
            print("❌ Persistence system not available")
            return False
        
        print("✅ Systems available")
        print(f"🔧 Inventory integration manager: {hasattr(inventory_system, 'integration_manager')}")
        print(f"🔧 Integration manager emit_event: {hasattr(manager, 'emit_event')}")
        
        # Load items
        item_data_file = os.path.join(current_dir, 'backend', 'src', 'inventory', 'data', 'basic_items.json')
        items_loaded = inventory_system.item_registry.load_from_files([item_data_file])
        print(f"📦 Loaded {items_loaded} items")
        
        # Set up test environment  
        print("\n2️⃣ Setting up test...")
        inventory_system.update_player_location("debug_player", "debug_room")
        
        # Give equipment
        inventory_system.handle_player_command("debug_player", "GIVE", {
            "item_name_or_id": "iron_sword",
            "quantity": 1
        })
        
        # Check initial persistence state
        print(f"\n3️⃣ Initial persistence state:")
        print(f"🏴 Dirty flags before: {persistence_system.dirty_flags}")
        
        # Perform equip operation with detailed logging
        print(f"\n4️⃣ Performing equip operation...")
        equip_result = inventory_system.handle_player_command("debug_player", "EQUIP", {
            "item_name_or_id": "iron_sword"
        })
        print(f"⚔️  Equip result: {equip_result}")
        
        # Check persistence state after equip
        print(f"\n5️⃣ Persistence state after equip:")
        print(f"🏴 Dirty flags after equip: {persistence_system.dirty_flags}")
        
        # Perform unequip operation
        print(f"\n6️⃣ Performing unequip operation...")
        unequip_result = inventory_system.handle_player_command("debug_player", "UNEQUIP", {
            "item_name_or_id": "iron_sword"
        })
        print(f"🗡️  Unequip result: {unequip_result}")
        
        # Check final persistence state
        print(f"\n7️⃣ Final persistence state:")
        print(f"🏴 Dirty flags after unequip: {persistence_system.dirty_flags}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        logger.exception("Debug test failed")
        return False

if __name__ == "__main__":
    test_event_flow()
