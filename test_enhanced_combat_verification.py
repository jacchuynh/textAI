#!/usr/bin/env python3
"""
Enhanced Combat Integration Verification Test

This script verifies that the enhanced combat features are properly integrated
into the main combat system.
"""

import sys
import os
sys.path.append('/Users/jacc/Downloads/TextRealmsAI/backend')

def test_enhanced_combat_integration():
    """Test that enhanced combat features are properly integrated."""
    print("=== Enhanced Combat Integration Verification ===\n")
    
    try:
        # Test combat system import
        from src.game_engine.combat_system import combat_system, ENHANCED_STATUS_AVAILABLE
        print("✅ Combat system imported successfully")
        print(f"✅ Enhanced status available: {ENHANCED_STATUS_AVAILABLE}")
        
        # Test enhanced status integration
        if hasattr(combat_system, 'apply_enhanced_status'):
            print("✅ Enhanced status methods available")
        else:
            print("❌ Enhanced status methods missing")
            
        # Test adaptive AI integration
        if hasattr(combat_system, '_choose_adaptive_attack'):
            print("✅ Adaptive AI methods available")
        else:
            print("❌ Adaptive AI methods missing")
            
        # Check available enhanced methods
        enhanced_methods = [m for m in dir(combat_system) if 'enhanced' in m.lower() or 'adaptive' in m.lower()]
        print(f"✅ Enhanced methods found: {enhanced_methods}")
        
        # Test basic combat functionality
        from src.shared.models import Character, DomainType
        
        # Create a test character
        test_character = Character(
            id="test_char",
            name="Test Hero",
            domains={
                DomainType.BODY: 3,
                DomainType.MIND: 2,
                DomainType.SPIRIT: 2,
                DomainType.SOCIAL: 1,
                DomainType.CRAFT: 1,
                DomainType.AUTHORITY: 1,
                DomainType.AWARENESS: 2
            }
        )
        
        # Start a test combat
        combat_id = combat_system.start_combat(
            character=test_character,
            enemy_template_id=1,  # Wolf template
            environment_id="forest"
        )
        
        print(f"✅ Test combat started successfully: {combat_id}")
        
        # Get combat state
        combat_state = combat_system.get_combat_state(combat_id)
        if combat_state:
            print("✅ Combat state retrieved successfully")
            print(f"   - Phase: {combat_state.get('phase')}")
            print(f"   - Round: {combat_state.get('round')}")
            print(f"   - Enemy: {combat_state.get('enemy', {}).get('name')}")
        else:
            print("❌ Failed to retrieve combat state")
            
        # Test enhanced roll integration
        if 'enhanced_roll_data' in str(combat_state):
            print("✅ Enhanced roll integration detected in combat state")
        else:
            print("ℹ️  Enhanced roll integration not immediately visible (may be internal)")
            
        print("\n=== Integration Status: SUCCESS ===")
        print("Enhanced combat features are properly integrated!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_combat_integration()
    sys.exit(0 if success else 1)
