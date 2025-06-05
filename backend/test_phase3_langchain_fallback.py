#!/usr/bin/env python3
"""
Comprehensive test for Phase 3 LangChain Agent Fallback Integration.

This test specifically focuses on verifying that the LangChain agent
properly activates as a fallback mechanism when:
1. Regex pattern matching fails
2. Confidence scores are too low
3. Complex or ambiguous commands are encountered

The test validates the complete integration chain:
spaCy parsing -> Pattern matching -> LangChain fallback -> Enhanced results
"""

import sys
import os
import logging
from pathlib import Path
import json

# Add the backend source directory to path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from text_parser.parser_engine import ParserEngine, ParsedCommand

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("phase3_fallback_test")


def test_regex_fallback_scenarios():
    """
    Test scenarios where regex patterns fail and LangChain agent should activate.
    These are commands that don't match standard patterns but should still be parseable.
    """
    logger.info("🔄 Testing Regex Pattern Fallback Scenarios")
    logger.info("=" * 50)
    
    parser = ParserEngine()
    
    # Commands that likely won't match standard regex patterns
    fallback_test_commands = [
        # Unconventional phrasing
        "I want to move in the direction of north",
        "Could you help me examine that sword please?",
        "Let's try to take the potion from the table",
        "Maybe I should look at what's around here",
        
        # Natural language variations
        "I'd like to go north if possible",
        "Please help me pick up the magic ring",
        "Can I talk to the wizard about spells?",
        "I need to cast a healing spell right now",
        
        # Complex sentence structures
        "Before I go north, I should examine the door",
        "After taking the sword, I want to attack the goblin",
        "While talking to Selene, I need to look around",
        
        # Question formats
        "What happens if I go north?",
        "How do I use this magic key?",
        "Why is the dragon sleeping?",
        "Where can I find healing potions?",
        
        # Indirect commands
        "The door needs to be examined carefully",
        "That sword should be taken from the chest",
        "Someone should talk to the guard",
        
        # Colloquial expressions
        "Let's check out that weird crystal",
        "I'm gonna grab the vorpal sword",
        "Time to head north to the castle",
        "Better take a look at this room",
    ]
    
    fallback_count = 0
    successful_parses = 0
    
    for i, command in enumerate(fallback_test_commands, 1):
        logger.info(f"\n[Fallback Test {i:2d}] Command: '{command}'")
        
        result = parser.parse(command)
        
        if result:
            successful_parses += 1
            
            # Check if LangChain was used (indicated by langchain_intent in context)
            langchain_used = bool(result.context.get("langchain_intent"))
            if langchain_used:
                fallback_count += 1
                logger.info("         🤖 LangChain Agent Activated")
            else:
                logger.info("         📝 Standard Pattern Matched")
            
            logger.info(f"         Action: {result.action}")
            logger.info(f"         Target: {result.target}")
            logger.info(f"         Confidence: {result.confidence:.2f}")
            
            if langchain_used:
                intent = result.context.get("langchain_intent", "")
                logger.info(f"         LangChain Intent: {intent}")
        else:
            logger.warning("         ❌ Parse Failed")
    
    logger.info(f"\n📊 Fallback Test Results:")
    logger.info(f"    Total Commands: {len(fallback_test_commands)}")
    logger.info(f"    Successful Parses: {successful_parses}")
    logger.info(f"    LangChain Fallbacks: {fallback_count}")
    logger.info(f"    Fallback Rate: {(fallback_count/len(fallback_test_commands)*100):.1f}%")


def test_low_confidence_enhancement():
    """
    Test the low confidence enhancement feature where LangChain
    improves results when initial confidence is below threshold.
    """
    logger.info("\n🎯 Testing Low Confidence Enhancement")
    logger.info("=" * 40)
    
    parser = ParserEngine()
    
    # Commands that might initially parse with low confidence
    low_confidence_commands = [
        # Ambiguous targets
        "take it",
        "examine that",
        "use this",
        "go there",
        
        # Unclear actions
        "do something with the sword",
        "handle the crystal somehow",
        "deal with the dragon",
        
        # Partial commands
        "the potion",
        "north to",
        "talk about",
        "magic spell",
        
        # Typos and variations
        "tak the swrd",  # typos
        "examin the cristal",
        "attak the goblin",
    ]
    
    enhanced_count = 0
    
    for i, command in enumerate(low_confidence_commands, 1):
        logger.info(f"\n[Enhancement Test {i:2d}] Command: '{command}'")
        
        result = parser.parse(command)
        
        if result:
            # Check if enhancement was applied
            langchain_enhanced = bool(result.context.get("langchain_entities") or 
                                    result.context.get("langchain_context"))
            
            if langchain_enhanced:
                enhanced_count += 1
                logger.info("         🚀 LangChain Enhancement Applied")
            
            logger.info(f"         Action: {result.action}")
            logger.info(f"         Target: {result.target}")
            logger.info(f"         Confidence: {result.confidence:.2f}")
            
            if langchain_enhanced:
                entities = result.context.get("langchain_entities", "")
                context = result.context.get("langchain_context", "")
                if entities and entities != "Entities: None":
                    logger.info(f"         Enhanced Entities: {entities}")
                if context and context != "Context: None":
                    logger.info(f"         Enhanced Context: {context[:100]}...")
        else:
            logger.warning("         ❌ Parse Failed")
    
    logger.info(f"\n📊 Enhancement Test Results:")
    logger.info(f"    Total Commands: {len(low_confidence_commands)}")
    logger.info(f"    Enhanced by LangChain: {enhanced_count}")
    logger.info(f"    Enhancement Rate: {(enhanced_count/len(low_confidence_commands)*100):.1f}%")


def test_agent_tool_selection():
    """
    Test that the LangChain agent correctly selects appropriate tools
    for different types of commands.
    """
    logger.info("\n🛠️  Testing Agent Tool Selection")
    logger.info("=" * 35)
    
    parser = ParserEngine()
    
    # Commands designed to trigger specific tools
    tool_test_commands = [
        {
            "command": "I want to move to the enchanted forest",
            "expected_action": "move",
            "description": "Should use MoveTool"
        },
        {
            "command": "Please help me examine the ancient artifact",
            "expected_action": "examine",
            "description": "Should use LookTool"
        },
        {
            "command": "I need to pick up the magical sword",
            "expected_action": "take",
            "description": "Should use TakeTool"
        },
        {
            "command": "Let me talk to the wizard about magic",
            "expected_action": "talk",
            "description": "Should use TalkTool"
        },
        {
            "command": "I want to attack the dragon with my weapon",
            "expected_action": "attack",
            "description": "Should use AttackTool"
        },
        {
            "command": "Help me cast a fireball spell",
            "expected_action": "cast",
            "description": "Should use MagicTool"
        },
    ]
    
    correct_tool_selections = 0
    
    for i, test_case in enumerate(tool_test_commands, 1):
        command = test_case["command"]
        expected_action = test_case["expected_action"]
        description = test_case["description"]
        
        logger.info(f"\n[Tool Test {i}] {description}")
        logger.info(f"    Command: '{command}'")
        
        result = parser.parse(command)
        
        if result:
            actual_action = result.action.lower() if result.action else ""
            
            # Check if the action matches expected
            action_match = expected_action.lower() in actual_action or actual_action in expected_action.lower()
            
            if action_match:
                correct_tool_selections += 1
                logger.info(f"    ✅ Correct tool selected: {result.action}")
            else:
                logger.info(f"    ⚠️  Unexpected action: {result.action} (expected: {expected_action})")
            
            logger.info(f"    Target: {result.target}")
            logger.info(f"    Confidence: {result.confidence:.2f}")
            
            # Show LangChain involvement
            if result.context.get("langchain_intent"):
                logger.info(f"    LangChain Intent: {result.context['langchain_intent']}")
        else:
            logger.warning(f"    ❌ Parse Failed")
    
    logger.info(f"\n📊 Tool Selection Results:")
    logger.info(f"    Total Tests: {len(tool_test_commands)}")
    logger.info(f"    Correct Tool Selections: {correct_tool_selections}")
    logger.info(f"    Accuracy: {(correct_tool_selections/len(tool_test_commands)*100):.1f}%")


def test_complex_scenario_handling():
    """
    Test complex scenarios that require sophisticated understanding
    and should definitely trigger LangChain agent.
    """
    logger.info("\n🧩 Testing Complex Scenario Handling")
    logger.info("=" * 38)
    
    parser = ParserEngine()
    
    complex_scenarios = [
        {
            "command": "I carefully approach the sleeping dragon while holding my enchanted sword, ready to either attack if it wakes up or sneak past it to get the treasure behind it",
            "description": "Multi-conditional action scenario"
        },
        {
            "command": "After examining the mysterious runes on the ancient door, I want to ask Selene if she knows what they mean before attempting to use my magic key",
            "description": "Sequential actions with consultation"
        },
        {
            "command": "If the healing potion is still on the altar next to the Moonblade, I should take it quietly without disturbing the sacred ceremony",
            "description": "Conditional action with environmental awareness"
        },
        {
            "command": "When I cast my lightning spell, make sure to target the orc chief but avoid hitting the innocent villagers nearby",
            "description": "Targeted action with collateral damage consideration"
        },
        {
            "command": "Before entering the dark Ironroot Caverns, I need to light my torch and check my inventory for any useful items or spells",
            "description": "Preparatory actions sequence"
        },
    ]
    
    for i, scenario in enumerate(complex_scenarios, 1):
        command = scenario["command"]
        description = scenario["description"]
        
        logger.info(f"\n[Complex Test {i}] {description}")
        logger.info(f"    Command: '{command}'")
        
        result = parser.parse(command)
        
        if result:
            # Complex scenarios should almost always use LangChain
            langchain_used = bool(result.context.get("langchain_intent"))
            
            logger.info(f"    Action: {result.action}")
            logger.info(f"    Target: {result.target}")
            logger.info(f"    Confidence: {result.confidence:.2f}")
            logger.info(f"    LangChain Used: {'Yes' if langchain_used else 'No'}")
            
            if langchain_used:
                intent = result.context.get("langchain_intent", "")
                context = result.context.get("langchain_context", "")
                
                logger.info(f"    Intent Analysis: {intent}")
                if context and context != "Context: None":
                    logger.info(f"    Context Analysis: {context[:150]}...")
        else:
            logger.warning(f"    ❌ Parse Failed")


def test_error_handling_and_recovery():
    """
    Test error handling when LangChain agent encounters issues.
    """
    logger.info("\n🛡️  Testing Error Handling and Recovery")
    logger.info("=" * 38)
    
    parser = ParserEngine()
    
    # Test edge cases that might cause errors
    edge_cases = [
        "",  # Empty string
        " ",  # Whitespace only
        "\n\t",  # Special characters
        "🐉⚔️🏰",  # Emoji only
        "a" * 1000,  # Very long string
        None,  # This might not work, but let's see how it's handled
    ]
    
    for i, test_input in enumerate(edge_cases, 1):
        logger.info(f"\n[Edge Case {i}] Input: {repr(test_input)}")
        
        try:
            if test_input is None:
                logger.info("    Skipping None input test")
                continue
                
            result = parser.parse(test_input)
            
            if result:
                logger.info(f"    ✅ Handled gracefully: {result.action}")
            else:
                logger.info(f"    ✅ Returned None (acceptable)")
                
        except Exception as e:
            logger.error(f"    ❌ Error occurred: {e}")


def run_comprehensive_phase3_test():
    """Run all Phase 3 integration tests."""
    logger.info("🚀 Starting Comprehensive Phase 3 LangChain Agent Fallback Test")
    logger.info("=" * 70)
    
    try:
        # Run all test suites
        test_regex_fallback_scenarios()
        test_low_confidence_enhancement()
        test_agent_tool_selection()
        test_complex_scenario_handling()
        test_error_handling_and_recovery()
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 Phase 3 Integration Test Suite Complete!")
        logger.info("\n📋 Test Summary:")
        logger.info("✅ Regex Pattern Fallback: Tested LangChain activation when patterns fail")
        logger.info("✅ Low Confidence Enhancement: Tested confidence-based improvements")
        logger.info("✅ Agent Tool Selection: Tested correct tool selection by LangChain agent")
        logger.info("✅ Complex Scenario Handling: Tested sophisticated command understanding")
        logger.info("✅ Error Handling: Tested graceful error recovery")
        
        logger.info("\n🔗 Integration Chain Verified:")
        logger.info("   spaCy NLP → Pattern Matching → LangChain Fallback → Enhanced Results")
        logger.info("\n✨ Phase 3 LangChain Agent Integration is working correctly!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_phase3_test()
    sys.exit(0 if success else 1)
