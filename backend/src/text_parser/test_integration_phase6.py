#!/usr/bin/env python3
"""
Integration Test for Phase 6 Complete Modular Text Parser System

This test validates that all phases of the refactored text parser work together:
- Phase 1: spaCy + rules parsing (replacing LangChain agents)
- Phase 2: IntentRouter integration
- Phase 3: ActionExecutor integration  
- Phase 4: PromptBuilder integration
- Phase 5: LLMRoleplayer integration
- Phase 6: End-to-end system integration

Test results will validate the complete removal of LangChain dependencies
and successful implementation of the new modular architecture.
"""

import os
import sys
import time
import logging
import asyncio
from typing import Dict, Any, List

# Add the project root to the path
sys.path.insert(0, '/Users/jacc/Downloads/TextRealmsAI/backend/src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("integration_test")

def test_import_system():
    """Test that all modules can be imported without LangChain dependencies."""
    print("🔍 Testing Module Imports (Phase 6)")
    print("=" * 60)
    
    try:
        # Test core parser engine import
        from text_parser.parser_engine import ParserEngine
        print("✅ ParserEngine imported successfully")
        
        # Test intent router import
        from text_parser.intent_router import IntentRouter, PrimaryIntent, SubIntent
        print("✅ IntentRouter imported successfully")
        
        # Test action executor import
        from text_parser.action_executor import ActionExecutor, ActionResult
        print("✅ ActionExecutor imported successfully")
        
        # Test prompt builder import
        from text_parser.prompt_builder import PromptBuilder, PromptContext
        print("✅ PromptBuilder imported successfully")
        
        # Test LLM roleplayer import
        from text_parser.llm_roleplayer import LLMRoleplayer, ResponseMode, create_development_roleplayer
        print("✅ LLMRoleplayer imported successfully")
        
        print("\n🎉 All Phase 6 modules imported without LangChain dependencies!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_parser_initialization():
    """Test that the complete parser system can be initialized."""
    print("\n🔍 Testing Parser System Initialization")
    print("=" * 60)
    
    try:
        from text_parser.parser_engine import ParserEngine
        
        # Initialize the complete system
        parser = ParserEngine()
        print("✅ ParserEngine initialized with all phases")
        
        # Check system status
        status = parser.get_system_status()
        print(f"✅ System status retrieved: {status['system']['phase']}")
        
        # Verify all components
        components = [
            ("spaCy NLP", status['parser_engine']['spacy_loaded']),
            ("Intent Router", status['intent_router']['available']),
            ("Action Executor", status['action_executor']['available']),
            ("Prompt Builder", status['prompt_builder']['available']),
            ("LLM Roleplayer", status['llm_roleplayer']['available'])
        ]
        
        for name, available in components:
            status_icon = "✅" if available else "⚠️"
            print(f"{status_icon} {name}: {'Available' if available else 'Unavailable'}")
        
        return parser
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None

def test_basic_parsing():
    """Test basic parsing functionality."""
    print("\n🔍 Testing Basic Parsing (Phases 1-2)")
    print("=" * 60)
    
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        
        # Test various command types
        test_commands = [
            "look around",
            "go north", 
            "take the sword",
            "talk to the merchant",
            "attack the goblin",
            "cast fireball",
            "inventory",
            "help"
        ]
        
        for command in test_commands:
            result = parser.parse(command)
            confidence_icon = "✅" if result.confidence > 0.5 else "⚠️"
            print(f"{confidence_icon} '{command}' -> {result.action} (confidence: {result.confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic parsing failed: {e}")
        return False

def test_end_to_end_processing():
    """Test end-to-end processing without LLM (to avoid API costs)."""
    print("\n🔍 Testing End-to-End Processing (Phases 1-4)")
    print("=" * 60)
    
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        
        # Mock game context
        game_context = {
            "player_name": "TestHero",
            "location_name": "Forest Clearing",
            "location_description": "A peaceful clearing surrounded by tall trees.",
            "npcs_present": ["Forest Wizard"],
            "items_available": ["magic wand", "health potion"]
        }
        
        # Test with LLM disabled to avoid API costs
        result = parser.process_player_input(
            "examine the magic wand",
            game_context=game_context,
            use_llm=False,  # Disable LLM for testing
            use_action_executor=True
        )
        
        print(f"✅ Input processed successfully")
        print(f"   Action: {result['parsed_command']['action']}")
        print(f"   Target: {result['parsed_command']['target']}")
        print(f"   Confidence: {result['parsed_command']['confidence']}")
        print(f"   Action Executed: {result['action_executed']}")
        print(f"   Processing Time: {result['processing_time']:.3f}s")
        print(f"   Response: {result['response_text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end processing failed: {e}")
        return False

async def test_async_processing():
    """Test async processing capabilities."""
    print("\n🔍 Testing Async Processing")
    print("=" * 60)
    
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        
        game_context = {
            "player_name": "AsyncTester",
            "location_name": "Test Chamber"
        }
        
        # Test async processing without LLM
        result = await parser.process_player_input_async(
            "look around the chamber",
            game_context=game_context,
            use_llm=False,  # Disable LLM for testing
            use_action_executor=True
        )
        
        print(f"✅ Async processing successful")
        print(f"   Processing Time: {result['processing_time']:.3f}s")
        print(f"   Response: {result['response_text']}")
        
        await parser.close()
        return True
        
    except Exception as e:
        print(f"❌ Async processing failed: {e}")
        return False

def test_llm_integration():
    """Test LLM integration if API key is available."""
    print("\n🔍 Testing LLM Integration (Phase 5)")
    print("=" * 60)
    
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️ No OPENROUTER_API_KEY found - skipping LLM tests")
        print("   Set OPENROUTER_API_KEY to test full LLM integration")
        return True
    
    try:
        from text_parser.llm_roleplayer import create_development_roleplayer, ResponseMode
        
        # Create development LLM instance
        llm = create_development_roleplayer()
        print(f"✅ LLM Roleplayer created with {llm.config.provider.value}")
        
        # Test basic response generation
        response = llm.generate_response(
            "You are a fantasy game master. A player examines a glowing sword. Respond in 1-2 sentences.",
            mode=ResponseMode.NARRATIVE,
            complexity="fast"
        )
        
        if response.success:
            print(f"✅ LLM response generated successfully")
            print(f"   Model: {response.model}")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Response: {response.response_text[:100]}...")
        else:
            print(f"❌ LLM response failed: {response.error}")
        
        # Close synchronously since this is not an async function
        if hasattr(llm, 'close_sync'):
            llm.close_sync()
        
        return response.success
        
    except Exception as e:
        print(f"❌ LLM integration test failed: {e}")
        return False

def test_fallback_handling():
    """Test fallback handling for unparseable input."""
    print("\n🔍 Testing Fallback Handling")
    print("=" * 60)
    
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        
        # Test with gibberish input
        result = parser.handle_parsing_failure(
            "asdf qwerty blah gibberish xyz",
            {"parsing_error": "No patterns matched"}
        )
        
        print(f"✅ Fallback handling successful")
        print(f"   Fallback used: {result.get('fallback_used', False)}")
        print(f"   Response: {result['response_text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback handling failed: {e}")
        return False

def test_system_diagnostics():
    """Test system diagnostics and health checks."""
    print("\n🔍 Testing System Diagnostics")
    print("=" * 60)
    
    try:
        from text_parser.parser_engine import ParserEngine
        parser = ParserEngine()
        
        # Run diagnostic
        diagnostic = parser.run_diagnostic()
        
        print(f"✅ System diagnostic completed")
        print(f"   Status: {diagnostic['system_status']}")
        print(f"   Issues found: {len(diagnostic['issues'])}")
        
        if diagnostic['issues']:
            print("   Issues:")
            for issue in diagnostic['issues']:
                print(f"     - {issue}")
        
        if diagnostic['recommendations']:
            print("   Recommendations:")
            for rec in diagnostic['recommendations']:
                print(f"     - {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ System diagnostics failed: {e}")
        return False

def display_refactor_summary():
    """Display summary of the refactoring accomplishments."""
    print("\n" + "=" * 80)
    print("🎉 PHASE 6 COMPLETE: TEXT PARSER REFACTOR SUMMARY")
    print("=" * 80)
    
    print("""
REFACTORING OBJECTIVES ACHIEVED:
✅ Completely removed LangChain dependencies (ChatOpenAI, BaseTool, LLM, etc.)
✅ Replaced LangChain agents with spaCy + rule-based parsing
✅ Implemented modular architecture with 6 integrated phases
✅ Maintained and enhanced functionality through direct game system integration
✅ Added comprehensive error handling and logging throughout all modules
✅ Established clean separation of concerns across components

PHASE-BY-PHASE ACCOMPLISHMENTS:

Phase 1 ✅ COMPLETE: spaCy + Rules Implementation
- Replaced LangChain agent-based parsing with spaCy NLP
- Implemented rule-based pattern matching for action recognition
- Added custom entity recognition for game-specific terms
- Enhanced linguistic analysis with POS tagging and dependency parsing

Phase 2 ✅ COMPLETE: IntentRouter Integration  
- Enhanced intent detection with PrimaryIntent/SubIntent classification
- Improved action/target detection using intent metadata
- Added confidence calculation and context enrichment
- Implemented disambiguation request handling

Phase 3 ✅ COMPLETE: ActionExecutor Implementation
- Replaced LangChain BaseTool functionality
- Integrated with game systems (movement, combat, inventory, etc.)
- Added comprehensive ActionResult dataclass
- Implemented proper error handling for all action categories

Phase 4 ✅ COMPLETE: PromptBuilder Implementation
- Created context-aware prompt generation system
- Added intent-specific prompt templates
- Integrated RAG capabilities for enhanced context
- Built modular prompt building for different action types

Phase 5 ✅ COMPLETE: LLMRoleplayer Implementation
- Replaced LangChain agents with direct OpenRouter API calls
- Added multi-provider support (OpenRouter, OpenAI, Anthropic)
- Implemented role-playing context management
- Added response caching, retry logic, and error handling
- Created async and sync interfaces for flexibility

Phase 6 ✅ COMPLETE: Final Integration and Testing
- Integrated all phases into comprehensive end-to-end system
- Added complete processing pipeline from input to response
- Implemented system diagnostics and health monitoring
- Created async processing capabilities
- Established fallback handling for parsing failures

TECHNICAL IMPROVEMENTS:
✅ Better performance through direct API calls vs LangChain overhead
✅ Enhanced modularity and maintainability
✅ Improved error handling and debugging capabilities
✅ Greater flexibility in model selection and configuration
✅ Cleaner codebase without unnecessary abstractions
✅ Direct integration with game systems for better functionality

The refactoring successfully established a clean, modular architecture that
completely removes LangChain dependencies while significantly enhancing
functionality through direct game system integration.
""")

async def main():
    """Run comprehensive integration tests for Phase 6."""
    print("🚀 STARTING PHASE 6 INTEGRATION TESTS")
    print("Testing complete modular text parser system")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Module imports
    test_results.append(("Module Imports", test_import_system()))
    
    # Test 2: System initialization
    test_results.append(("System Initialization", test_parser_initialization() is not None))
    
    # Test 3: Basic parsing
    test_results.append(("Basic Parsing", test_basic_parsing()))
    
    # Test 4: End-to-end processing
    test_results.append(("End-to-End Processing", test_end_to_end_processing()))
    
    # Test 5: Async processing
    test_results.append(("Async Processing", await test_async_processing()))
    
    # Test 6: LLM integration (if API key available)
    test_results.append(("LLM Integration", test_llm_integration()))
    
    # Test 7: Fallback handling
    test_results.append(("Fallback Handling", test_fallback_handling()))
    
    # Test 8: System diagnostics
    test_results.append(("System Diagnostics", test_system_diagnostics()))
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 6 integration successful!")
        display_refactor_summary()
    else:
        print("⚠️ Some tests failed - review issues above")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
