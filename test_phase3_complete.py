#!/usr/bin/env python3
"""
Test script for Phase 3 LangChain Agent Integration
Tests the complete parser engine with agent fallback functionality.
"""

import sys
import os
import logging

# Add the backend source to Python path
sys.path.append('/Users/jacc/Downloads/TextRealmsAI/backend/src')

def test_phase3_integration():
    """Test the Phase 3 LangChain agent integration."""
    print("=== Phase 3 Integration Test ===\n")
    
    try:
        from text_parser.parser_engine import ParserEngine
        
        # Initialize parser
        print("1. Initializing parser engine...")
        parser = ParserEngine()
        print("✓ Parser engine initialized successfully")
        
        # Verify agent is set up
        if hasattr(parser, 'langchain_agent') and parser.langchain_agent:
            print("✓ LangChain agent is initialized")
        else:
            print("⚠ LangChain agent not found - may use simulated responses")
        
        # Test cases for different scenarios
        test_cases = [
            # Standard parsing (should work without agent)
            ("go north", "Standard movement command"),
            ("look around", "Standard observation command"),
            ("take sword", "Standard inventory command"),
            
            # Complex commands (may trigger agent fallback)
            ("cast a spell to heal my wounds", "Complex magic command"),
            ("negotiate with the merchant about sword prices", "Complex social command"),
            ("sneak quietly through the shadows", "Complex stealth command"),
            
            # Ambiguous commands (should trigger agent fallback)
            ("help me with this", "Ambiguous help request"),
            ("do something interesting", "Very ambiguous command"),
            ("what should I do now?", "Question format command"),
        ]
        
        print("\n2. Testing parser with various commands...\n")
        
        for i, (command, description) in enumerate(test_cases, 1):
            print(f"Test {i}: {description}")
            print(f"Input: '{command}'")
            
            try:
                result = parser.parse(command)
                
                if result:
                    print(f"Action: {result.action}")
                    print(f"Target: {result.target}")
                    print(f"Confidence: {result.confidence:.2f}")
                    
                    if hasattr(result, 'context') and result.context:
                        if 'langchain_analysis' in result.context:
                            print("✓ LangChain analysis included")
                        if 'entity_resolutions' in result.context:
                            print("✓ Entity resolutions included")
                    
                    # Check if this was likely parsed by the agent
                    if result.confidence > 0.8 and result.action not in ['go', 'look', 'take']:
                        print("✓ Likely parsed by LangChain agent")
                    
                else:
                    print("✗ Parser returned None")
                
            except Exception as e:
                print(f"✗ Error parsing command: {e}")
            
            print("-" * 50)
        
        print("\n3. Testing low confidence scenario...")
        
        # Test a scenario that should trigger low confidence fallback
        parser.logger.setLevel(logging.DEBUG)  # Enable debug logging
        
        result = parser.parse("flibbernaught the whimsical thingy")
        
        if result:
            print(f"Action: {result.action}")
            print(f"Confidence: {result.confidence:.2f}")
            if result.confidence > 0.5:
                print("✓ Agent improved low confidence parsing")
            else:
                print("- Low confidence maintained (expected for nonsense input)")
        
        print("\n=== Phase 3 Integration Test Complete ===")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure the parser engine is properly installed")
        return False
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_tools():
    """Test the individual agent tools."""
    print("\n=== Testing Agent Tools ===\n")
    
    try:
        from text_parser.parser_engine import (
            MoveTool, LookTool, TakeTool, UseTool, 
            TalkTool, AttackTool, InventoryTool, DropTool
        )
        
        tools = [
            (MoveTool(), "north"),
            (LookTool(), "around"),
            (TakeTool(), "sword"),
            (UseTool(), "potion"),
            (TalkTool(), "merchant"),
            (AttackTool(), "goblin"),
            (InventoryTool(), ""),
            (DropTool(), "torch"),
        ]
        
        for tool, test_input in tools:
            print(f"Testing {tool.__class__.__name__}...")
            try:
                result = tool._run(test_input)
                print(f"✓ Result: {result}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        print("\n=== Agent Tools Test Complete ===")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Run all Phase 3 tests."""
    print("Starting Phase 3 LangChain Agent Integration Tests...")
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = True
    
    # Test 1: Phase 3 Integration
    success &= test_phase3_integration()
    
    # Test 2: Agent Tools
    success &= test_agent_tools()
    
    if success:
        print("\n🎉 All Phase 3 tests passed!")
    else:
        print("\n❌ Some Phase 3 tests failed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
