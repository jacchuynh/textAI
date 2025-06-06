#!/usr/bin/env python3
"""
Simple Integration Test for the Complete Text Parser System

This test validates the basic functionality without complex imports
that might cause circular dependency issues.
"""

import os
import sys
sys.path.insert(0, '/Users/jacc/Downloads/TextRealmsAI/backend/src')

def test_parser_engine_creation():
    """Test that ParserEngine can be created."""
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        assert parser is not None
        print("✅ ParserEngine created successfully")
        return True
    except Exception as e:
        print(f"❌ ParserEngine creation failed: {e}")
        return False

def test_intent_router_creation():
    """Test that IntentRouter can be created."""
    try:
        from text_parser.intent_router import IntentRouter
        router = IntentRouter()
        assert router is not None
        print("✅ IntentRouter created successfully")
        return True
    except Exception as e:
        print(f"❌ IntentRouter creation failed: {e}")
        return False

def test_action_executor_creation():
    """Test that ActionExecutor can be created."""
    try:
        from text_parser.action_executor import ActionExecutor
        executor = ActionExecutor()
        assert executor is not None
        print("✅ ActionExecutor created successfully")
        return True
    except Exception as e:
        print(f"❌ ActionExecutor creation failed: {e}")
        return False

def test_prompt_builder_creation():
    """Test that PromptBuilder can be created."""
    try:
        from text_parser.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        assert builder is not None
        print("✅ PromptBuilder created successfully")
        return True
    except Exception as e:
        print(f"❌ PromptBuilder creation failed: {e}")
        return False

def test_llm_roleplayer_creation():
    """Test that LLMRoleplayer can be created."""
    try:
        from text_parser.llm_roleplayer import create_development_roleplayer
        llm = create_development_roleplayer()
        assert llm is not None
        print("✅ LLMRoleplayer created successfully")
        return True
    except Exception as e:
        print(f"❌ LLMRoleplayer creation failed: {e}")
        return False

def test_basic_parsing():
    """Test basic parsing functionality."""
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        
        # Test simple command parsing
        result = parser.parse("look around")
        assert result is not None
        print("✅ Basic parsing works")
        return True
    except Exception as e:
        print(f"❌ Basic parsing failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Simple Integration Test")
    print("=" * 50)
    
    tests = [
        test_parser_engine_creation,
        test_intent_router_creation,
        test_action_executor_creation,
        test_prompt_builder_creation,
        test_llm_roleplayer_creation,
        test_basic_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
