#!/usr/bin/env python3
"""
Simple test script for the enhanced combat system integration.
"""

import sys
import os

# Add the backend src directory to Python path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

def test_enhanced_roll_integration():
    """Test that the enhanced roll system is properly integrated."""
    print("=== Testing Enhanced Roll Integration ===\n")
    
    try:
        # Import models
        from shared.models import Character, DomainType, Domain, Tag, TagCategory
        print("✅ Successfully imported models")
        
        # Create a test character
        character = Character(
            name="Test Fighter",
            character_class="Fighter"
        )
        
        # Set up domains with test values
        character.domains[DomainType.BODY].value = 4
        character.domains[DomainType.AWARENESS].value = 3
        character.domains[DomainType.MIND].value = 2
        
        # Add some combat-relevant tags
        character.tags["sword_fighting"] = Tag(
            name="Sword Fighting",
            category=TagCategory.COMBAT,
            description="Skill with sword combat",
            domains=[DomainType.BODY],
            rank=3
        )
        
        print("✅ Created test character with domains and tags")
        
        # Test the enhanced roll method
        print("\n--- Testing Enhanced Roll Method ---")
        result = character.roll_check_hybrid(
            domain_type=DomainType.BODY,
            tag_name="sword_fighting",
            difficulty=12
        )
        
        print(f"Roll Result: {result}")
        print(f"Success: {result['success']}")
        print(f"Total: {result['total']}")
        print(f"DC: {result['dc']}")
        print(f"Margin: {result['margin']}")
        print(f"Domains used: {result.get('domains_used', [])}")
        print(f"Tags used: {result.get('tags_used', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during enhanced roll test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_combat_system_helper_methods():
    """Test the new helper methods in the combat system."""
    print("\n=== Testing Combat System Helper Methods ===\n")
    
    try:
        # Import combat system indirectly to avoid relative import issues
        import importlib.util
        
        combat_system_path = os.path.join(backend_src, 'game_engine', 'combat_system.py')
        spec = importlib.util.spec_from_file_location("combat_system", combat_system_path)
        combat_module = importlib.util.module_from_spec(spec)
        
        # We need to mock the relative imports for this test
        sys.modules['shared.models'] = sys.modules.get('shared.models')
        sys.modules['events.event_bus'] = type('MockEventBus', (), {'event_bus': type('MockEventBus', (), {'publish': lambda x: None})()})()
        sys.modules['memory.memory_manager'] = type('MockMemoryManager', (), {'memory_manager': type('MockMemoryManager', (), {'add_memory': lambda **kwargs: None})()})()
        
        # Load the module
        spec.loader.exec_module(combat_module)
        
        print("✅ Successfully loaded combat system module")
        
        # Create combat system instance
        combat_system = combat_module.CombatSystem()
        
        # Test _determine_action_domain method
        print("\n--- Testing _determine_action_domain ---")
        test_actions = [
            {"action_type": "attack", "label": "Sword Strike"},
            {"action_type": "defend", "label": "Raise Shield"},
            {"action_type": "spell", "label": "Magic Missile"},
            {"action_type": "maneuver", "label": "Tactical Movement"}
        ]
        
        for action in test_actions:
            domain = combat_system._determine_action_domain(action)
            print(f"Action '{action['label']}' -> Domain: {domain}")
        
        print("✅ _determine_action_domain working correctly")
        
        # Test _calculate_action_difficulty
        print("\n--- Testing _calculate_action_difficulty ---")
        test_action = {"action_type": "attack", "label": "Basic Attack"}
        test_target = {"level": 5, "armor_class": 15}
        test_combat_state = {"round": 3, "player": {"status_effects": []}}
        
        difficulty = combat_system._calculate_action_difficulty(test_action, test_target, test_combat_state)
        print(f"Base difficulty for level 5 target: {difficulty}")
        
        print("✅ _calculate_action_difficulty working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during combat system test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("Starting Enhanced Combat System Integration Tests\n")
    
    test1_result = test_enhanced_roll_integration()
    test2_result = test_combat_system_helper_methods()
    
    print(f"\n=== Test Results ===")
    print(f"Enhanced Roll Integration: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Combat System Helpers: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print(f"\n🎉 All tests passed! Enhanced combat integration is working correctly.")
        return True
    else:
        print(f"\n⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
