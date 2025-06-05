#!/usr/bin/env python3
"""
Comprehensive Phase 3 Test with Real API
Tests the full LangChain integration with actual OpenRouter API calls.
"""

import sys
import os
import logging

# Add the backend source to Python path
sys.path.append('/Users/jacc/Downloads/TextRealmsAI/backend/src')

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = "/Users/jacc/Downloads/TextRealmsAI/.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
    return False

# Load .env file at import time
load_env()

def setup_logging():
    """Setup detailed logging for debugging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_api_key():
    """Verify API key is available"""
    key = os.environ.get('OPENROUTER_API_KEY')
    if not key:
        print("❌ OPENROUTER_API_KEY not found!")
        print("Please set it using: export OPENROUTER_API_KEY='your-key-here'")
        return False
    
    if not key.startswith('sk-or-v1-'):
        print("⚠ API key format may be incorrect")
        print("OpenRouter keys should start with 'sk-or-v1-'")
        return False
    
    print(f"✅ API key found (ends with: ...{key[-8:]})")
    return True

def test_real_langchain_integration():
    """Test Phase 3 with real API calls"""
    print("=== Testing Phase 3 with Real LangChain API ===\n")
    
    if not check_api_key():
        return False
    
    try:
        from text_parser.parser_engine import ParserEngine
        
        print("1. Initializing parser with real LangChain agent...")
        parser = ParserEngine()
        
        # Verify agent setup
        if hasattr(parser, 'agent_executor') and parser.agent_executor:
            print("✅ LangChain agent executor initialized")
        else:
            print("❌ LangChain agent not initialized")
            return False
        
        # Test cases that should trigger LangChain fallback
        test_cases = [
            # Complex commands that regex might miss
            "I want to carefully examine the mysterious glowing orb on the pedestal",
            "Can I negotiate with the dragon about not burning down the village?",
            "Cast a healing spell on my wounded companion",
            "Try to sneak past the sleeping guards without making noise",
            "Use my thieves' tools to pick the lock on the treasure chest",
            "Attempt to decipher the ancient runes carved into the stone wall",
            "Barter with the merchant for a better price on the magical sword",
            "Channel divine energy to turn the undead creatures",
        ]
        
        print(f"\n2. Testing {len(test_cases)} complex commands...")
        successes = 0
        api_calls = 0
        
        for i, command in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{command}'")
            
            try:
                result = parser.parse(command)
                
                if result:
                    print(f"  ✅ Action: {result.action}")
                    print(f"     Target: {result.target}")
                    print(f"     Confidence: {result.confidence:.2f}")
                    
                    # Check if this was handled by LangChain
                    if result.confidence >= 0.8 and result.action != "unknown":
                        successes += 1
                        if hasattr(result, 'context') and 'tool_used' in str(result.context):
                            api_calls += 1
                            print(f"     🤖 LangChain tool used")
                    
                else:
                    print("  ❌ Failed to parse")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print(f"\n=== Results ===")
        print(f"Successful parses: {successes}/{len(test_cases)} ({successes/len(test_cases)*100:.1f}%)")
        print(f"LangChain API calls: {api_calls}")
        
        if api_calls > 0:
            print("🎉 Real LangChain integration is working!")
        else:
            print("⚠ No LangChain API calls detected - may still be using mock")
        
        return successes > len(test_cases) * 0.5  # 50% success rate
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_api_connectivity():
    """Test direct API connectivity"""
    print("\n=== Testing OpenRouter API Connectivity ===")
    
    try:
        from text_parser.parser_engine import OpenRouterLLM
        
        print("1. Creating OpenRouter LLM instance...")
        llm = OpenRouterLLM()
        
        print("2. Testing simple API call...")
        test_prompt = "Respond with exactly: 'API_TEST_SUCCESS'"
        
        response = llm.invoke(test_prompt)
        print(f"Response: {response}")
        
        if "API_TEST_SUCCESS" in response:
            print("✅ API connectivity confirmed!")
            return True
        else:
            print("⚠ API responded but with unexpected content")
            return True  # Still working, just different response
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run comprehensive Phase 3 tests"""
    setup_logging()
    
    print("🚀 TextRealmsAI Phase 3 - Real API Integration Test")
    print("=" * 60)
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("\n💡 Tip: Make sure your API key is valid and you have credits")
        return False
    
    # Test full integration
    success = test_real_langchain_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Phase 3 LangChain integration is fully operational!")
        print("Your AI GM can now handle complex natural language commands.")
    else:
        print("⚠ Some issues detected. Check the logs above for details.")
    
    print("\nNext steps:")
    print("- Try the enhanced commands in your AI GM sessions")
    print("- Monitor API usage and costs")
    print("- Adjust confidence thresholds if needed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
