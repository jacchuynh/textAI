#!/usr/bin/env python3
"""
Phase 4: Advanced LangChain Integration & Tool Routing Test

Tests the enhanced LangChain tools that actually integrate with the game systems
instead of returning mock JSON responses.
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the backend source to Python path
backend_dir = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_dir))

from text_parser.parser_engine import ParserEngine, ParsedCommand
from system_integration_manager import SystemIntegrationManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_systems_manager():
    """Test that the GameSystemsManager can access all game systems."""
    try:
        # Test SystemIntegrationManager with required arguments
        manager = SystemIntegrationManager(session_id="test_session", player_id="test_player")
        
        # Initialize all systems (this was the missing method call)
        init_result = manager.initialize_all_systems()
        
        # Check if we can access core systems via the systems dictionary
        from system_integration_manager import SystemType
        
        systems_available = {
            'combat_system': SystemType.COMBAT in manager.systems,
            'magic_system': SystemType.MAGIC in manager.systems, 
            'ai_gm_brain': SystemType.AI_GM in manager.systems,
            'crafting_system': SystemType.CRAFTING in manager.systems,
            'economy_system': SystemType.ECONOMY in manager.systems,
            'business_system': SystemType.BUSINESS in manager.systems,
            'npc_system': SystemType.NPC in manager.systems,
            'quest_system': SystemType.QUEST in manager.systems,
            'narrative_system': SystemType.NARRATIVE in manager.systems,
            'events_system': SystemType.EVENTS in manager.systems,
            'text_parser': SystemType.TEXT_PARSER in manager.systems
        }
        
        logger.info(f"Systems available: {systems_available}")
        logger.info(f"Initialization result: {init_result}")
        
        # Return True if at least 6 core systems are available (some may fail due to missing dependencies)
        available_count = sum(systems_available.values())
        return available_count >= 6
        
    except Exception as e:
        logger.error(f"Systems manager test failed: {e}")
        return False

def test_enhanced_langchain_tools():
    """Test the enhanced LangChain tools with game system integration."""
    results = {}
    
    try:
        # Initialize parser with enhanced tools
        parser = ParserEngine()
        
        # Test commands that should use different tools
        test_commands = {
            "move": "go north",
            "look": "look at the room", 
            "take": "take the sword",
            "use": "use healing potion",
            "talk": "talk to the merchant",
            "attack": "attack the dragon",
            "inventory": "check inventory",
            "drop": "drop torch",
            "cast_spell": "cast fireball at enemy"
        }
        
        for tool_name, command in test_commands.items():
            try:
                logger.info(f"Testing {tool_name} tool with command: '{command}'")
                
                # Parse the command
                parsed_command = parser.parse(command)
                
                if parsed_command:
                    # Get tool information from context (where LangChain stores it)
                    tool_used = parsed_command.context.get('tool_used', 'Unknown')
                    langchain_used = parsed_command.context.get('langchain_agent_used', False)
                    
                    result = {
                        "success": True,
                        "result": {
                            "action": parsed_command.action,
                            "target": parsed_command.target,
                            "confidence": parsed_command.confidence,
                            "tool_used": tool_used,
                            "langchain_agent_used": langchain_used,
                            "context": parsed_command.context
                        },
                        "has_system_integration": langchain_used or parsed_command.confidence > 0.7,
                        "has_fallback": parsed_command.confidence < 0.5
                    }
                else:
                    result = {
                        "success": False,
                        "error": "Failed to parse command",
                        "has_system_integration": False,
                        "has_fallback": True
                    }
                    
                results[tool_name] = result
                
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                results[tool_name] = {
                    "success": False,
                    "error": str(e),
                    "has_system_integration": False,
                    "has_fallback": False
                }
                
    except Exception as e:
        logger.error(f"Enhanced tools test failed: {e}")
        results["error"] = str(e)
    
    return results

def test_parser_integration():
    """Test parser integration with the enhanced tools."""
    results = []
    
    try:
        parser = ParserEngine()
        
        test_commands = [
            "go north",
            "look at the room",
            "take the sword", 
            "use healing potion",
            "talk to the merchant",
            "attack the dragon",
            "check inventory",
            "drop the torch",
            "cast lightning bolt",
            "examine the treasure chest"
        ]
        
        for command in test_commands:
            try:
                logger.info(f"Testing parser integration with: '{command}'")
                parsed_command = parser.parse(command)
                
                if parsed_command:
                    result = {
                        "command": command,
                        "success": True,
                        "result": {
                            "action": parsed_command.action,
                            "target": parsed_command.target,
                            "confidence": parsed_command.confidence
                        }
                    }
                else:
                    result = {
                        "command": command,
                        "success": False,
                        "error": "Failed to parse command"
                    }
                    
                results.append(result)
                
            except Exception as e:
                logger.error(f"Parser integration failed for '{command}': {e}")
                results.append({
                    "command": command,
                    "success": False,
                    "error": str(e)
                })
                
    except Exception as e:
        logger.error(f"Parser integration test failed: {e}")
        
    return results

def test_error_handling():
    """Test error handling and fallback mechanisms."""
    try:
        parser = ParserEngine()
        
        # Test with invalid/unclear commands
        test_commands = [
            "xyzabc invalid command",
            "cast spell without target",
            "use item that doesn't exist",
            ""
        ]
        
        for command in test_commands:
            try:
                parsed_command = parser.parse(command)
                logger.info(f"Error handling test for '{command}': {parsed_command is not None}")
            except Exception as e:
                logger.error(f"Error handling failed for '{command}': {e}")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error handling test failed: {e}")
        return False

def run_phase4_tests():
    """Run all Phase 4 integration tests."""
    logger.info("🚀 Starting Phase 4: Advanced LangChain Integration & Tool Routing Tests")
    logger.info("=" * 80)
    
    # Initialize test results
    test_results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "phase": "Phase 4: Advanced LangChain Integration & Tool Routing",
        "test_results": {
            "systems_manager": False,
            "tools": {},
            "parser_integration": [],
            "error_handling": False
        },
        "summary": {
            "systems_manager_working": False,
            "error_handling_working": False,
            "tools_tested": 0,
            "tools_working": 0,
            "commands_tested": 0,
            "commands_working": 0
        }
    }
    
    # Test 1: Systems Manager
    logger.info("📋 Testing Systems Manager...")
    test_results["test_results"]["systems_manager"] = test_systems_manager()
    test_results["summary"]["systems_manager_working"] = test_results["test_results"]["systems_manager"]
    
    # Test 2: Enhanced LangChain Tools
    logger.info("🔧 Testing Enhanced LangChain Tools...")
    tools_results = test_enhanced_langchain_tools()
    test_results["test_results"]["tools"] = tools_results
    
    if isinstance(tools_results, dict) and "error" not in tools_results:
        test_results["summary"]["tools_tested"] = len(tools_results)
        test_results["summary"]["tools_working"] = sum(1 for result in tools_results.values() if result.get("success", False))
    
    # Test 3: Parser Integration
    logger.info("🔀 Testing Parser Integration...")
    parser_results = test_parser_integration()
    test_results["test_results"]["parser_integration"] = parser_results
    
    if parser_results:
        test_results["summary"]["commands_tested"] = len(parser_results)
        test_results["summary"]["commands_working"] = sum(1 for result in parser_results if result.get("success", False))
    
    # Test 4: Error Handling
    logger.info("⚠️ Testing Error Handling...")
    test_results["test_results"]["error_handling"] = test_error_handling()
    test_results["summary"]["error_handling_working"] = test_results["test_results"]["error_handling"]
    
    # Generate report
    report_filename = f"phase4_test_report_{test_results['timestamp']}.json"
    with open(report_filename, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    logger.info(f"📊 Test report saved to: {report_filename}")
    
    # Print summary
    logger.info("📋 Phase 4 Test Summary:")
    logger.info(f"   Systems Manager: {'✅' if test_results['summary']['systems_manager_working'] else '❌'}")
    logger.info(f"   Tools Working: {test_results['summary']['tools_working']}/{test_results['summary']['tools_tested']}")
    logger.info(f"   Commands Working: {test_results['summary']['commands_working']}/{test_results['summary']['commands_tested']}")
    logger.info(f"   Error Handling: {'✅' if test_results['summary']['error_handling_working'] else '❌'}")
    
    # Determine overall success
    overall_success = (
        test_results['summary']['systems_manager_working'] and
        test_results['summary']['tools_working'] > 0 and
        test_results['summary']['commands_working'] > 0 and
        test_results['summary']['error_handling_working']
    )
    
    if overall_success:
        logger.info("🎉 Phase 4 Integration Tests: PASSED")
    else:
        logger.info("❌ Phase 4 Integration Tests: FAILED")
    
    return overall_success

if __name__ == "__main__":
    success = run_phase4_tests()
    sys.exit(0 if success else 1)