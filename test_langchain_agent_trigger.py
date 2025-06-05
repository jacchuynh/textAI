#!/usr/bin/env python3
"""
Test to specifically trigger the LangChain agent by using commands
that result in low confidence scores from the regular parser.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the backend source to Python path
backend_dir = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_dir))

from text_parser.parser_engine import ParserEngine, ParsedCommand

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_langchain_agent_activation():
    """Test commands that should trigger the LangChain agent due to low confidence."""
    
    # Initialize parser
    parser = ParserEngine()
    
    # Test commands that should result in low confidence and trigger LangChain agent
    low_confidence_commands = [
        "blargify the glompnoodle",  # Nonsense words
        "xyz abc def",               # Random letters  
        "do the thing with stuff",   # Very vague
        "make it happen now",        # Unclear action
        "process the thingy",        # Unclear target
    ]
    
    results = []
    
    for command_text in low_confidence_commands:
        try:
            logger.info(f"Testing low-confidence command: '{command_text}'")
            parsed_command = parser.parse(command_text)
            
            if parsed_command:
                langchain_used = parsed_command.context.get('langchain_agent_used', False)
                tool_used = parsed_command.context.get('tool_used', 'None')
                
                result = {
                    "command": command_text,
                    "success": True,
                    "action": parsed_command.action,
                    "target": parsed_command.target,
                    "confidence": parsed_command.confidence,
                    "langchain_used": langchain_used,
                    "tool_used": tool_used,
                    "context_keys": list(parsed_command.context.keys()) if parsed_command.context else []
                }
            else:
                result = {
                    "command": command_text,
                    "success": False,
                    "error": "Failed to parse command"
                }
                
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error testing '{command_text}': {e}")
            results.append({
                "command": command_text,
                "success": False,
                "error": str(e)
            })
    
    return results

def test_confidence_threshold():
    """Test what confidence levels different commands produce."""
    
    parser = ParserEngine()
    
    test_commands = [
        # Should be high confidence
        "go north",
        "look at sword", 
        "take the potion",
        
        # Should be medium confidence
        "examine the mysterious object",
        "use the strange device",
        
        # Should be low confidence
        "do something weird",
        "handle the situation",
        "make it work",
    ]
    
    results = []
    
    for command_text in test_commands:
        try:
            logger.info(f"Testing confidence for: '{command_text}'")
            parsed_command = parser.parse(command_text)
            
            if parsed_command:
                results.append({
                    "command": command_text,
                    "action": parsed_command.action,
                    "target": parsed_command.target,
                    "confidence": parsed_command.confidence,
                    "langchain_used": parsed_command.context.get('langchain_agent_used', False),
                    "tool_used": parsed_command.context.get('tool_used', 'None')
                })
            else:
                results.append({
                    "command": command_text,
                    "confidence": 0.0,
                    "error": "Parse failed"
                })
                
        except Exception as e:
            logger.error(f"Error testing confidence for '{command_text}': {e}")
            results.append({
                "command": command_text,
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    logger.info("🧪 Testing LangChain Agent Activation")
    logger.info("=" * 50)
    
    # Test 1: Commands that should trigger LangChain agent
    logger.info("📋 Testing Low-Confidence Commands (should trigger LangChain agent)...")
    langchain_results = test_langchain_agent_activation()
    
    # Test 2: Confidence threshold testing
    logger.info("📊 Testing Confidence Thresholds...")
    confidence_results = test_confidence_threshold()
    
    # Save results
    all_results = {
        "langchain_activation_test": langchain_results,
        "confidence_threshold_test": confidence_results
    }
    
    with open("langchain_agent_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Print summary
    logger.info("📋 Test Summary:")
    logger.info(f"Low-confidence commands tested: {len(langchain_results)}")
    
    langchain_triggered = sum(1 for r in langchain_results if r.get('langchain_used', False))
    logger.info(f"LangChain agent triggered: {langchain_triggered}/{len(langchain_results)}")
    
    logger.info(f"Confidence threshold commands tested: {len(confidence_results)}")
    
    # Show confidence distribution
    confidences = [r.get('confidence', 0) for r in confidence_results if 'confidence' in r]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)
        max_confidence = max(confidences)
        logger.info(f"Confidence range: {min_confidence:.2f} - {max_confidence:.2f} (avg: {avg_confidence:.2f})")
    
    logger.info("📊 Results saved to: langchain_agent_test_results.json")
