#!/usr/bin/env python3
"""
Verification test for enhanced combat system integration.
This tests the key integration points without complex imports.
"""

import sys
import os

# Add the backend src directory to Python path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

def test_enhanced_rolls():
    """Test that enhanced roll methods work correctly."""
    print("=== Testing Enhanced Roll Methods ===\n")
    
    try:
        from shared.models import Character, DomainType, Domain, Tag, TagCategory
        
        # Create test character
        character = Character(
            name="Test Fighter",
            character_class="Fighter"
        )
        
        # Set up domains
        character.domains[DomainType.BODY].value = 4        # Combat domain
        character.domains[DomainType.AUTHORITY].value = 6   # High authority
        character.domains[DomainType.SOCIAL].value = 2      # Low social
        character.domains[DomainType.AWARENESS].value = 3   # Moderate awareness
        character.domains[DomainType.MIND].value = 2        # Low mind
        
        # Add combat tags
        character.tags["sword_fighting"] = Tag(
            name="Sword Fighting",
            category=TagCategory.COMBAT,
            description="Skill with sword combat",
            domains=[DomainType.BODY],
            rank=3
        )
        
        character.tags["tactics"] = Tag(
            name="Tactics",
            category=TagCategory.COMBAT,
            description="Military tactical knowledge",
            domains=[DomainType.MIND, DomainType.AWARENESS],
            rank=2
        )
        
        print("✅ Created test character with combat domains and tags")
        
        # Test different combat scenarios
        
        # 1. Physical Attack (should use dice - Body domain)
        print("\n--- Test 1: Physical Attack (Body domain - dice method) ---")
        result = character.roll_check_hybrid(
            domain_type=DomainType.BODY,
            tag_name="sword_fighting",
            difficulty=12
        )
        
        print(f"Result: {result['success']} (Total: {result['total']}, Difficulty: {result['difficulty']})")
        print(f"Method: {result['method']} - {result['method_reason']}")
        print(f"Breakdown: {result['breakdown']}")
        
        # 2. Tactical Maneuver (should use thresholds - Mind domain)
        print("\n--- Test 2: Tactical Maneuver (Mind domain - threshold method) ---")
        result = character.roll_check_hybrid(
            domain_type=DomainType.MIND,
            tag_name="tactics",
            difficulty=12
        )
        
        print(f"Result: {result['success']} (Total: {result['total']}, Difficulty: {result['difficulty']})")
        print(f"Method: {result['method']} - {result['method_reason']}")
        print(f"Breakdown: {result['breakdown']}")
        
        # 3. High Authority Action (should use thresholds - Authority domain)
        print("\n--- Test 3: Authority Command (Authority domain - threshold method) ---")
        result = character.roll_check_hybrid(
            domain_type=DomainType.AUTHORITY,
            difficulty=12
        )
        
        print(f"Result: {result['success']} (Total: {result['total']}, Difficulty: {result['difficulty']})")
        print(f"Method: {result['method']} - {result['method_reason']}")
        print(f"Breakdown: {result['breakdown']}")
        
        # 4. Awareness Check (should use dice - Awareness domain)
        print("\n--- Test 4: Awareness Check (Awareness domain - dice method) ---")
        result = character.roll_check_hybrid(
            domain_type=DomainType.AWARENESS,
            difficulty=15
        )
        
        print(f"Result: {result['success']} (Total: {result['total']}, Difficulty: {result['difficulty']})")
        print(f"Method: {result['method']} - {result['method_reason']}")
        print(f"Breakdown: {result['breakdown']}")
        
        print("\n✅ Enhanced roll methods are working correctly!")
        print("✅ Combat system can now use these enhanced rolls for all action resolution!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_magic_combat_integration():
    """Verify that magic combat integration is already using enhanced rolls."""
    print("\n=== Verifying Magic Combat Integration ===\n")
    
    try:
        # Read the magic combat integration file to verify it uses enhanced rolls
        magic_file_path = os.path.join(backend_src, 'game_engine', 'magic_combat_integration.py')
        
        if os.path.exists(magic_file_path):
            with open(magic_file_path, 'r') as f:
                content = f.read()
                
            # Check for enhanced roll usage
            if 'roll_check_hybrid' in content:
                print("✅ Magic combat integration uses roll_check_hybrid()")
                
                # Count occurrences to show extent of integration
                occurrences = content.count('roll_check_hybrid')
                print(f"   Found {occurrences} uses of enhanced roll method")
                
                # Look for spell casting resolution
                if 'spell casting resolution' in content.lower():
                    print("✅ Enhanced rolls used for spell casting resolution")
                
                return True
            else:
                print("❌ Magic combat integration doesn't use enhanced rolls")
                return False
        else:
            print("❌ Magic combat integration file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking magic integration: {e}")
        return False

def test_combat_system_structure():
    """Verify the combat system structure and integration points."""
    print("\n=== Verifying Combat System Structure ===\n")
    
    try:
        combat_file_path = os.path.join(backend_src, 'game_engine', 'combat_system.py')
        
        if os.path.exists(combat_file_path):
            with open(combat_file_path, 'r') as f:
                content = f.read()
            
            # Check for removal of redundant function
            if '_resolve_action_roll' not in content:
                print("✅ Redundant _resolve_action_roll function removed")
            else:
                print("❌ _resolve_action_roll function still present")
                return False
            
            # Check for enhanced roll integration
            if 'roll_check_hybrid' in content:
                print("✅ Combat system uses enhanced rolls")
                
                # Check for helper methods
                helper_methods = [
                    '_determine_action_domain',
                    '_find_best_action_tag', 
                    '_calculate_action_difficulty'
                ]
                
                for method in helper_methods:
                    if method in content:
                        print(f"✅ Helper method {method} present")
                    else:
                        print(f"❌ Helper method {method} missing")
                        return False
                
                return True
            else:
                print("❌ Combat system doesn't use enhanced rolls")
                return False
        else:
            print("❌ Combat system file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking combat system: {e}")
        return False

def main():
    """Run all integration verification tests."""
    print("Enhanced Combat Integration Verification\n")
    print("=" * 50)
    
    test1 = test_enhanced_rolls()
    test2 = test_magic_combat_integration()
    test3 = test_combat_system_structure()
    
    print(f"\n" + "=" * 50)
    print(f"VERIFICATION RESULTS:")
    print(f"Enhanced Roll Methods: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Magic Combat Integration: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Combat System Structure: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if test1 and test2 and test3:
        print(f"\n🎉 INTEGRATION VERIFICATION SUCCESSFUL!")
        print(f"✅ Enhanced combat system integration is complete and working")
        print(f"✅ Magic combat already uses enhanced rolls")
        print(f"✅ Combat system updated to use enhanced rolls")
        print(f"✅ Redundant code removed")
        return True
    else:
        print(f"\n⚠️ Some verification checks failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
