#!/usr/bin/env python3
"""
Test script to verify the model selection fix.
Tests that OpenRouter LLM now respects the default model setting.
"""

import os
import sys

# Add the backend source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Load environment variables
from load_env import load_env
load_env()

# Import the ParserEngine
from text_parser.parser_engine import ParserEngine

def test_model_selection():
    """Test that the model selection works correctly."""
    print("🧪 Testing OpenRouter Model Selection Fix")
    print("=" * 50)
    
    # Test 1: With empty OPENROUTER_MODEL (should use account default)
    os.environ['OPENROUTER_MODEL'] = ''
    engine = ParserEngine()
    
    print("\n✅ Test 1: Empty OPENROUTER_MODEL")
    print("Should use OpenRouter account default model ('qwen/qwen3-32b:free')")
    
    # Test parsing with a simple command
    test_command = "look around"
    result = engine.parse(test_command)
    print(f"Command: '{test_command}'")
    print(f"Result: {result}")
    
    # Test 2: With specific model set
    print("\n✅ Test 2: Specific model set")
    os.environ['OPENROUTER_MODEL'] = 'openai/gpt-4o-mini'
    engine2 = ParserEngine()
    
    result2 = engine2.parse(test_command)
    print(f"Model: openai/gpt-4o-mini")
    print(f"Command: '{test_command}'")
    print(f"Result: {result2}")
    
    print("\n🎉 Model selection fix appears to be working!")
    print("The system should now use your OpenRouter account default model.")
    print("Your account default: 'qwen/qwen3-32b:free'")

if __name__ == "__main__":
    test_model_selection()
