#!/usr/bin/env python3
"""
Test script to verify AI GM import fixes are working correctly.
"""

import sys
import os

# Add the backend/src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_imports():
    """Test that all the fixed imports work correctly."""
    print("Testing AI GM import fixes...")
    
    try:
        # Test core imports
        print("✓ Testing core AI GM imports...")
        from ai_gm.ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
        print("  ✓ AIGMBrain core classes imported successfully")
        
        # Test world reaction imports
        print("✓ Testing world reaction imports...")
        from ai_gm.world_reaction.world_reaction_integration import extend_ai_gm_brain_with_world_reaction
        print("  ✓ World reaction functions imported successfully")
        
        # Test pacing imports
        print("✓ Testing pacing imports...")
        from ai_gm.pacing.pacing_integration import PacingIntegration
        print("  ✓ PacingIntegration class imported successfully")
        
        # Test LLM manager imports
        print("✓ Testing LLM manager imports...")
        from ai_gm.ai_gm_llm_manager import LLMInteractionManager
        print("  ✓ LLMInteractionManager class imported successfully")
        
        # Test unified integration imports
        print("✓ Testing unified integration imports...")
        from ai_gm.ai_gm_unified_integration import AIGMUnifiedSystem
        print("  ✓ AIGMUnifiedSystem class imported successfully")
        
        print("\n🎉 All import fixes successful!")
        print("\nAvailable systems detection:")
        
        # Import the availability flags
        from ai_gm.ai_gm_unified_integration import (
            WORLD_REACTION_AVAILABLE,
            PACING_AVAILABLE,
            OUTPUT_AVAILABLE,
            OOC_AVAILABLE,
            LLM_AVAILABLE,
            COMBAT_AVAILABLE
        )
        
        systems = {
            "World Reaction": WORLD_REACTION_AVAILABLE,
            "Pacing": PACING_AVAILABLE,
            "Output": OUTPUT_AVAILABLE,
            "OOC": OOC_AVAILABLE,
            "LLM": LLM_AVAILABLE,
            "Combat": COMBAT_AVAILABLE
        }
        
        for name, available in systems.items():
            status = "✓ Available" if available else "✗ Unavailable"
            print(f"  {name}: {status}")
        
        active_count = sum(systems.values())
        total_count = len(systems)
        print(f"\nSystems Status: {active_count}/{total_count} subsystems available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
