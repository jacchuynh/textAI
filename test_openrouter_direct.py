#!/usr/bin/env python3
"""
Test OpenRouter LLM implementation directly
"""

import os
import sys
import logging

# Add project root to path
sys.path.append('/Users/jacc/Downloads/TextRealmsAI')

# Load environment variables
from load_env import load_env
load_env()

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_openrouter_llm():
    """Test the OpenRouterLLM class directly"""
    print("=== Testing OpenRouter LLM Implementation ===\n")
    
    try:
        # Import the OpenRouterLLM class
        from backend.src.text_parser.parser_engine import OpenRouterLLM
        from langchain_core.messages import HumanMessage
        
        print("1. Creating OpenRouterLLM instance...")
        llm = OpenRouterLLM()
        print(f"   ✅ Created successfully")
        print(f"   - Model: {llm.model_name}")
        print(f"   - API Base: {llm.openai_api_base}")
        print(f"   - Temperature: {llm.temperature}")
        print(f"   - Max Tokens: {llm.max_tokens}")
        print(f"   - Use Account Default: {getattr(llm, '_use_account_default', False)}")
        
        print("\n2. Testing simple generation...")
        messages = [HumanMessage(content="Say 'Hello, OpenRouter!' in exactly those words.")]
        
        try:
            result = llm._generate(messages)
            print("   ✅ Generation successful!")
            print(f"   Response: {result.generations[0].message.content}")
            
            # Check generation info
            if hasattr(result.generations[0], 'generation_info') and result.generations[0].generation_info:
                info = result.generations[0].generation_info
                if 'model_name' in info:
                    print(f"   Model used: {info['model_name']}")
                if 'token_usage' in info:
                    usage = info['token_usage']
                    print(f"   Tokens: {usage.get('total_tokens', 'N/A')} total")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Failed to create OpenRouterLLM: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_specific_model():
    """Test with a specific model instead of account default"""
    print("\n=== Testing with Specific Model ===\n")
    
    try:
        from backend.src.text_parser.parser_engine import OpenRouterLLM
        from langchain_core.messages import HumanMessage
        
        print("1. Creating OpenRouterLLM with specific model...")
        # Use a reliable, fast model for testing
        llm = OpenRouterLLM(model_name="openai/gpt-3.5-turbo")
        print(f"   ✅ Created successfully with model: {llm.model_name}")
        print(f"   - Use Account Default: {getattr(llm, '_use_account_default', False)}")
        
        print("\n2. Testing generation with specific model...")
        messages = [HumanMessage(content="Respond with just the number '42'.")]
        
        try:
            result = llm._generate(messages)
            print("   ✅ Generation successful!")
            print(f"   Response: {result.generations[0].message.content}")
            return True
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test specific model: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenRouter LLM Integration\n")
    
    # Check API key first
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found!")
        sys.exit(1)
    
    print(f"✅ API Key found (ends with: ...{api_key[-8:]})\n")
    
    # Test account default first
    success1 = test_openrouter_llm()
    
    # Test specific model
    success2 = test_with_specific_model()
    
    print(f"\n=== Results ===")
    print(f"Account Default: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Specific Model: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 or success2:
        print("\n🎉 OpenRouter LLM is working! Ready for LangChain integration.")
    else:
        print("\n💥 OpenRouter LLM needs debugging.")
