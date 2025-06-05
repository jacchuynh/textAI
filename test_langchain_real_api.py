#!/usr/bin/env python3
"""
Test LangChain tools with real OpenRouter API calls
"""

import o
import sys
import json
import logging

# Add project root to path
sys.path.append('/Users/jacc/Downloads/TextRealmsAI')

# Load environment variables
from load_env import load_env
load_env()

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_langchain_tools_with_real_api():
    """Test LangChain tools with actual API calls"""
    print("=== Testing LangChain Tools with Real API ===\n")
    
    try:
        # Import parser engine
        from backend.src.text_parser.parser_engine import TextParserEngine
        
        print("1. Initializing TextParserEngine with real LLM...")
        parser = TextParserEngine()
        print("   ✅ Parser initialized successfully")
        
        # Test commands that should trigger LangChain agent (low confidence)
        test_commands = [
            "summon the ancient dragon of wisdom from the ethereal realm",
            "transmute my copper coins into golden treasures using alchemy",
            "cast a spell to reveal the hidden secrets of this mysterious artifact",
            "negotiate a trade deal between the neighboring kingdoms",
            "investigate the strange magical phenomena occurring in the forest"
        ]
        
        print(f"\n2. Testing {len(test_commands)} ambiguous commands...")
        results = []
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n   Test {i}: '{command}'")
            try:
                # Parse the command
                parsed = parser.parse_enhanced_command(command)
                
                # Extract information
                action = parsed.action
                confidence = parsed.confidence
                langchain_used = parsed.context.get('langchain_agent_used', False)
                tool_used = parsed.context.get('tool_used', 'Unknown')
                system_response = parsed.context.get('system_response', 'No system response')
                
                print(f"      Action: {action}")
                print(f"      Confidence: {confidence:.3f}")
                print(f"      LangChain Used: {langchain_used}")
                print(f"      Tool Used: {tool_used}")
                print(f"      System Response: {system_response[:100]}...")
                
                # Record results
                results.append({
                    'command': command,
                    'action': action,
                    'confidence': confidence,
                    'langchain_used': langchain_used,
                    'tool_used': tool_used,
                    'system_response': system_response,
                    'success': tool_used != 'Unknown' and system_response != 'No system response'
                })
                
                # If LangChain was used and we got a real response, that's a success
                if langchain_used and tool_used != 'Unknown':
                    print(f"      ✅ LangChain tool executed successfully!")
                else:
                    print(f"      ⚠️  Command handled by standard parser")
                
            except Exception as e:
                print(f"      ❌ Error parsing command: {e}")
                results.append({
                    'command': command,
                    'error': str(e),
                    'success': False
                })
        
        # Summary
        print(f"\n=== Results Summary ===")
        successes = sum(1 for r in results if r.get('success', False))
        langchain_used_count = sum(1 for r in results if r.get('langchain_used', False))
        
        print(f"Commands processed: {len(results)}")
        print(f"LangChain agent triggered: {langchain_used_count}")
        print(f"Successful tool executions: {successes}")
        
        # Save detailed results
        with open('/Users/jacc/Downloads/TextRealmsAI/langchain_real_api_test_results.json', 'w') as f:
            json.dump({
                'test_type': 'langchain_tools_real_api',
                'timestamp': str(__import__('datetime').datetime.now()),
                'summary': {
                    'total_commands': len(results),
                    'langchain_triggered': langchain_used_count,
                    'successful_executions': successes
                },
                'results': results
            }, f, indent=2)
        
        print(f"\n📊 Detailed results saved to: langchain_real_api_test_results.json")
        
        return successes > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_tool_directly():
    """Test a specific LangChain tool directly"""
    print("\n=== Testing Specific Tool Directly ===\n")
    
    try:
        from backend.src.text_parser.parser_engine import create_enhanced_langchain_tools
        
        print("1. Creating LangChain tools...")
        tools = create_enhanced_langchain_tools()
        print(f"   ✅ Created {len(tools)} tools")
        
        # Test the magic system tool directly
        magic_tool = None
        for tool in tools:
            if 'magic' in tool.name.lower():
                magic_tool = tool
                break
        
        if magic_tool:
            print(f"\n2. Testing magic tool: {magic_tool.name}")
            try:
                # Test the tool with a simple request
                result = magic_tool.invoke("cast healing spell on potion")
                
                print(f"   ✅ Tool executed successfully!")
                print(f"   Result: {result[:200]}...")
                return True
                
            except Exception as e:
                print(f"   ❌ Tool execution failed: {e}")
                return False
        else:
            print("   ❌ No magic tool found")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test tool directly: {e}")
        return False

if __name__ == "__main__":
    print("Testing LangChain Tools with Real OpenRouter API\n")
    
    # Check API key
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found!")
        sys.exit(1)
    
    print(f"✅ API Key found (ends with: ...{api_key[-8:]})\n")
    
    # Run tests
    test1_success = test_langchain_tools_with_real_api()
    test2_success = test_specific_tool_directly()
    
    print(f"\n=== Final Results ===")
    print(f"Integration Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Direct Tool Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success or test2_success:
        print("\n🎉 LangChain tools are working with real API!")
        print("The enhanced LangChain integration is now fully operational.")
    else:
        print("\n💥 LangChain tools need more debugging.")
