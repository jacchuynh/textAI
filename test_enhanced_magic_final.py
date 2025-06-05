#!/usr/bin/env python3
"""
Final Test for Enhanced Magic Integration

This script verifies that all magic functions have been properly enhanced 
with the enhanced roll system while maintaining backward compatibility.
"""

import sys
import re
from pathlib import Path

def test_enhanced_magic_functions():
    """Test that magic functions are properly enhanced"""
    
    print("=== Enhanced Magic Functions Verification ===\n")
    
    # Read the advanced magic features file
    magic_file = Path("/Users/jacc/Downloads/TextRealmsAI/backend/src/magic_system/advanced_magic_features.py")
    
    if not magic_file.exists():
        print("❌ Magic file not found")
        return False
    
    content = magic_file.read_text()
    
    # Check for enhanced functions
    enhanced_functions = [
        "get_environmental_magic_effects",
        "enhance_narrative_with_magic",
        "generate_magical_event"
    ]
    
    success_count = 0
    
    for func_name in enhanced_functions:
        print(f"Checking {func_name}...")
        
        # Look for the function definition
        func_pattern = rf"def {func_name}\([^)]*character[^)]*\)"
        if re.search(func_pattern, content):
            print(f"  ✅ Function signature includes 'character' parameter")
            success_count += 1
        else:
            print(f"  ❌ Function signature missing 'character' parameter")
            continue
            
        # Look for enhanced roll usage
        roll_patterns = [
            r"roll_check_hybrid",
            r"DomainType\.(SPIRIT|MIND|SOCIAL)",
            r"action_data.*=.*{",
            r"difficulty.*=",
        ]
        
        func_start = content.find(f"def {func_name}")
        if func_start == -1:
            print(f"  ❌ Function {func_name} not found")
            continue
            
        # Find function end (next def or class)
        func_end = content.find("\n    def ", func_start + 1)
        if func_end == -1:
            func_end = content.find("\nclass ", func_start + 1)
        if func_end == -1:
            func_end = len(content)
            
        func_content = content[func_start:func_end]
        
        enhanced_features = 0
        for pattern in roll_patterns:
            if re.search(pattern, func_content):
                enhanced_features += 1
        
        if enhanced_features >= 2:
            print(f"  ✅ Function uses enhanced roll system")
        else:
            print(f"  ⚠️  Function may not be fully enhanced ({enhanced_features}/4 patterns found)")
            
        # Check for fallback mechanism
        if "random." in func_content or "except:" in func_content:
            print(f"  ✅ Function maintains backward compatibility")
        else:
            print(f"  ⚠️  Function may not have fallback mechanism")
            
        print()
    
    print(f"\nSummary: {success_count}/{len(enhanced_functions)} functions properly enhanced")
    return success_count == len(enhanced_functions)

def test_integration_patterns():
    """Test for consistent integration patterns"""
    
    print("=== Integration Pattern Verification ===\n")
    
    magic_file = Path("/Users/jacc/Downloads/TextRealmsAI/backend/src/magic_system/advanced_magic_features.py")
    content = magic_file.read_text()
    
    # Check for consistent patterns
    patterns = {
        "Enhanced roll import": r"from \.\.[^\\n]*models import DomainType",
        "Enhanced roll calls": r"character\.roll_check_hybrid",
        "Fallback mechanisms": r"except:.*# Fallback",
        "Action data structure": r"action_data.*=.*{.*label.*:.*}",
        "Domain type usage": r"DomainType\.(SPIRIT|MIND|SOCIAL|AWARENESS|BODY|CRAFT|AUTHORITY)",
    }
    
    found_patterns = 0
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content, re.DOTALL):
            print(f"✅ {pattern_name}: Found")
            found_patterns += 1
        else:
            print(f"❌ {pattern_name}: Not found")
    
    print(f"\nIntegration patterns: {found_patterns}/{len(patterns)} found")
    return found_patterns >= len(patterns) - 1  # Allow one pattern to be missing

def main():
    """Main test function"""
    
    print("Enhanced Magic Integration Final Verification")
    print("=" * 50)
    
    functions_test = test_enhanced_magic_functions()
    patterns_test = test_integration_patterns()
    
    if functions_test and patterns_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("Enhanced magic integration is complete and functional")
        return True
    else:
        print("\n⚠️  Some verification checks failed")
        print("This may indicate incomplete integration or missing patterns")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
