#!/usr/bin/env python3
"""
Test script to verify which OpenRouter model is actually being used for LLM calls.
"""

import os
import sys
import logging

# Add the backend source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Load environment variables
from load_env import load_env
load_env()

# Import the OpenRouterLLM class directly
from text_parser.parser_engine import OpenRouterLLM

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_openrouter_model_usage():
    """Test which model OpenRouter actually uses."""
    print("🔍 Testing Actual OpenRouter Model Usage")
    print("=" * 50)
    
    # Test 1: Empty OPENROUTER_MODEL (should use account default)
    print("\n📌 Test 1: Empty OPENROUTER_MODEL environment variable")
    os.environ['OPENROUTER_MODEL'] = ''
    
    try:
        # Create OpenRouterLLM instance
        llm = OpenRouterLLM()
        print(f"LLM model_name: {llm.model_name}")
        print(f"LLM openai_api_base: {llm.openai_api_base}")
        
        # Make a simple test call
        print("Making test LLM call...")
        response = llm.invoke("What is 2+2? Answer in one word.")
        print(f"Response: {response}")
        print(f"Response type: {type(response)}")
        
        # Check if we can extract model info from response
        if hasattr(response, 'response_metadata'):
            print(f"Response metadata: {response.response_metadata}")
        
    except Exception as e:
        print(f"Error in Test 1: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    
    # Test 2: Specific model set
    print("\n📌 Test 2: Specific model (openai/gpt-4o-mini)")
    os.environ['OPENROUTER_MODEL'] = 'openai/gpt-4o-mini'
    
    try:
        # Create new OpenRouterLLM instance
        llm2 = OpenRouterLLM()
        print(f"LLM2 model_name: {llm2.model_name}")
        
        # Make a simple test call
        print("Making test LLM call...")
        response2 = llm2.invoke("What is 3+3? Answer in one word.")
        print(f"Response: {response2}")
        
        # Check response metadata
        if hasattr(response2, 'response_metadata'):
            print(f"Response metadata: {response2.response_metadata}")
        
    except Exception as e:
        print(f"Error in Test 2: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openrouter_model_usage()
