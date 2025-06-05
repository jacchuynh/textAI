#!/usr/bin/env python3
"""
Test script specifically for equipment persistence events
"""

import os
import sys
import logging
import tempfile
import shutil
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'backend', 'src'))

from system_integration_manager import SystemIntegrationManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_equipment_persistence():
    """Test equipment change persistence events."""
    print("🧪 Testing Equipment Persistence Events")
    print("="*50)
    
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp(prefix="textrealsai_equipment_test_")
    print(f"📁 Using temporary directory: {temp_dir}")
    
    try:
        # Initialize systems
        print("\n1️⃣ Initializing systems...")
        manager = SystemIntegrationManager("test_equipment_session", "test_player")
        
        # Get inventory system
        from system_integration_manager import SystemType
        inventory_system = manager.systems.get(SystemType.INVENTORY)
        if not inventory_system:
            print("❌ Inventory system not available")
            return False
        
        print("✅ Systems initialized")
        
        # Set up player location
        print("\n2️⃣ Setting up test environment...")
        inventory_system.update_player_location("test_player", "test_armory")
        
        # Give player equipment items
        sword_result = inventory_system.handle_player_command("test_player", "GIVE", {
            "item_name_or_id": "iron_sword",
            "quantity": 1
        })
        print(f"🗡️  Give sword result: {sword_result.get('success')} - {sword_result.get('message')}")
        
        armor_result = inventory_system.handle_player_command("test_player", "GIVE", {
            "item_name_or_id": "leather_armor",
            "quantity": 1
        })
        print(f"🛡️  Give armor result: {armor_result.get('success')} - {armor_result.get('message')}")
        
        # Test equipment operations
        print("\n3️⃣ Testing equip command with persistence...")
        equip_result = inventory_system.handle_player_command("test_player", "EQUIP", {
            "item_name_or_id": "iron_sword"
        })
        print(f"⚔️  Equip sword result: {equip_result.get('success')} - {equip_result.get('message')}")
        
        equip_armor_result = inventory_system.handle_player_command("test_player", "EQUIP", {
            "item_name_or_id": "leather_armor"
        })
        print(f"🛡️  Equip armor result: {equip_armor_result.get('success')} - {equip_armor_result.get('message')}")
        
        # Test unequip operations
        print("\n4️⃣ Testing unequip command with persistence...")
        unequip_result = inventory_system.handle_player_command("test_player", "UNEQUIP", {
            "item_name_or_id": "iron_sword"
        })
        print(f"🗡️  Unequip sword result: {unequip_result.get('success')} - {unequip_result.get('message')}")
        
        unequip_slot_result = inventory_system.handle_player_command("test_player", "UNEQUIP", {
            "slot_name": "chest"
        })
        print(f"🛡️  Unequip armor by slot result: {unequip_slot_result.get('success')} - {unequip_slot_result.get('message')}")
        
        # Check persistence system state
        print("\n5️⃣ Checking persistence system...")
        persistence_system = manager.systems.get(SystemType.PERSISTENCE)
        if persistence_system:
            dirty_flags = persistence_system.dirty_flags
            dirty_count = sum(1 for flag in dirty_flags.values() if flag)
            print(f"🏴 Dirty flags: {dirty_count} sections need saving")
            
            # Trigger save
            save_result = manager.save_game_state()
            print(f"💾 Save result: {save_result}")
        
        print("\n✅ Equipment persistence test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Equipment persistence test failed: {e}")
        logger.exception("Test failed with exception")
        return False
    
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temporary directory")

if __name__ == "__main__":
    test_equipment_persistence()
