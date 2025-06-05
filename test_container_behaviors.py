#!/usr/bin/env python3
"""
Test script for container type behaviors and enhanced interactions.
"""

import json
import sys
import os

# Add the backend src to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from inventory.location_container_system import LocationContainerSystem, ContainerType
from inventory.item_definitions import ItemDataRegistry
from text_parser.parser_engine import LookTool, SearchTool, UnlockTool

def test_container_behaviors():
    """Test container type-specific behaviors."""
    print("=== Testing Container Type Behaviors ===\n")
    
    # Initialize systems
    item_registry = ItemDataRegistry()
    container_system = LocationContainerSystem(item_registry)
    
    test_location = "test_chamber"
    
    # Create different container types with behaviors
    containers = [
        ("chest", ContainerType.CHEST, "Ornate Chest", "enhanced"),
        ("barrel", ContainerType.BARREL, "Supply Barrel", "basic"),
        ("bookshelf", ContainerType.BOOKSHELF, "Ancient Bookshelf", "legendary"),
        ("weapon_rack", ContainerType.WEAPON_RACK, "Weapon Display", "enhanced"),
        ("altar", ContainerType.ALTAR, "Sacred Altar", "basic")
    ]
    
    for container_id, container_type, name, enhancement in containers:
        try:
            created_id = container_system.create_enhanced_container(
                location_id=test_location,
                container_type=container_type,
                name=name,
                description=f"A {enhancement} {container_type.value}",
                enhancement_level=enhancement
            )
            print(f"✓ Created {enhancement} {container_type.value}: {name}")
            
            # Test behaviors
            behaviors = container_system.get_container_type_behaviors(container_type)
            print(f"  Behaviors: {json.dumps(behaviors, indent=2)}")
            
        except Exception as e:
            print(f"✗ Failed to create {container_type.value}: {e}")
    
    print("\n=== Testing Tool Integration ===\n")
    
    # Test LookTool with container behaviors
    look_tool = LookTool()
    try:
        result = look_tool._run("around")
        result_data = json.loads(result)
        print(f"✓ LookTool result: {result_data.get('system_response', 'No response')}")
    except Exception as e:
        print(f"✗ LookTool error: {e}")
    
    # Test SearchTool with container behaviors
    search_tool = SearchTool()
    try:
        result = search_tool._run("thoroughly")
        result_data = json.loads(result)
        print(f"✓ SearchTool result: {result_data.get('system_response', 'No response')}")
    except Exception as e:
        print(f"✗ SearchTool error: {e}")
    
    print("\n=== Testing Specific Container Behaviors ===\n")
    
    # Test specific container type behaviors
    for container_type in [ContainerType.CHEST, ContainerType.BOOKSHELF, ContainerType.WEAPON_RACK]:
        try:
            behaviors = container_system.get_container_type_behaviors(container_type)
            print(f"✓ {container_type.value} behaviors:")
            print(f"  - Can be locked: {behaviors.get('can_be_locked', 'Unknown')}")
            print(f"  - Default capacity: {behaviors.get('default_capacity_slots', 'Unknown')} slots")
            print(f"  - Discovery hint: {behaviors.get('discovery_hint', 'None')}")
            
            if "special_search" in behaviors:
                print(f"  - Special search: {behaviors['special_search']}")
            if "item_type_restriction" in behaviors:
                print(f"  - Item restrictions: {behaviors['item_type_restriction']}")
            if "special_requirements" in behaviors:
                print(f"  - Special requirements: {behaviors['special_requirements']}")
                
        except Exception as e:
            print(f"✗ Failed to get behaviors for {container_type.value}: {e}")
    
    print("\n=== Testing Container Lock/Unlock System ===\n")
    
    # Test unlock functionality
    unlock_tool = UnlockTool()
    try:
        # Try to unlock a chest
        result = unlock_tool._run("chest")
        result_data = json.loads(result)
        print(f"✓ UnlockTool test: {result_data.get('system_response', 'No response')}")
    except Exception as e:
        print(f"✗ UnlockTool error: {e}")
    
    print("\n=== Container Enhanced Features Test ===\n")
    
    # Test enhanced container creation with different levels
    enhancement_levels = ["basic", "enhanced", "legendary"]
    for level in enhancement_levels:
        try:
            container_id = container_system.create_enhanced_container(
                location_id=test_location,
                container_type=ContainerType.CHEST,
                name=f"{level.capitalize()} Test Chest",
                description=f"A {level} chest for testing",
                enhancement_level=level
            )
            
            # Get the created container to check its properties
            containers = container_system.get_containers_in_location(test_location)
            if container_id in containers:
                container_data = containers[container_id]
                print(f"✓ {level.capitalize()} chest created:")
                print(f"  - Capacity: {container_data.capacity_slots} slots, {container_data.capacity_weight} weight")
                print(f"  - Locked: {container_data.is_locked}")
                if container_data.is_locked:
                    print(f"  - Lock difficulty: {container_data.lock_difficulty}")
                    if container_data.key_required:
                        print(f"  - Key required: {container_data.key_required}")
            
        except Exception as e:
            print(f"✗ Failed to create {level} container: {e}")
    
    print("\n=== Container Behaviors Test Complete ===")

def test_container_discovery():
    """Test hidden container discovery mechanics."""
    print("\n=== Testing Hidden Container Discovery ===\n")
    
    try:
        # Initialize systems
        item_registry = ItemDataRegistry()
        container_system = LocationContainerSystem(item_registry)
        
        test_location = "secret_room"
        
        # Create hidden containers
        hidden_chest_id = container_system.create_enhanced_container(
            location_id=test_location,
            container_type=ContainerType.CHEST,
            name="Hidden Treasure Chest",
            description="A well-concealed chest behind a tapestry",
            enhancement_level="legendary",
            is_hidden=True,
            discovery_difficulty=15
        )
        
        # Create secret compartment in bookshelf
        secret_compartment_id = container_system.create_enhanced_container(
            location_id=test_location,
            container_type=ContainerType.BOOKSHELF,
            name="Secret Compartment",
            description="A hidden compartment behind the books",
            enhancement_level="enhanced",
            is_hidden=True,
            discovery_difficulty=10
        )
        
        print(f"✓ Created hidden containers in {test_location}")
        
        # Test search for hidden containers
        search_tool = SearchTool()
        
        # Test different search intensities
        search_queries = [
            "search carefully",
            "search thoroughly",
            "search for hidden items",
            "examine the bookshelf carefully"
        ]
        
        for query in search_queries:
            try:
                result = search_tool._run(query)
                result_data = json.loads(result)
                print(f"✓ Search '{query}': {result_data.get('system_response', 'No response')}")
                
                if 'discoveries' in result_data and result_data['discoveries']:
                    print(f"  Discoveries: {result_data['discoveries']}")
                    
            except Exception as e:
                print(f"✗ Search '{query}' failed: {e}")
        
    except Exception as e:
        print(f"✗ Hidden container discovery test failed: {e}")

if __name__ == "__main__":
    try:
        test_container_behaviors()
        test_container_discovery()
        print("\n🎉 All container behavior tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
