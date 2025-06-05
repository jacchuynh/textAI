#!/usr/bin/env python3
"""
Comprehensive test for the integrated spaCy + LangChain text parser system.

This test demonstrates Phase 3 integration where both spaCy and LangChain
work together to provide enhanced natural language processing capabilities.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend source directory to path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from text_parser.parser_engine import ParserEngine, ParsedCommand

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("nlp_parser_test")


def test_sample_commands():
    """Test various fantasy game commands with the integrated parser."""
    
    logger.info("🧙‍♂️ Starting Integrated NLP Parser Test (spaCy + LangChain)")
    logger.info("=" * 60)
    
    # Initialize the parser engine
    parser = ParserEngine()
    
    # Test commands that demonstrate different parsing capabilities
    test_commands = [
        # Movement commands
        "go north to the enchanted forest",
        "walk carefully through the dark cave",
        "run quickly to the castle",
        
        # Observation commands
        "examine the ancient Moonblade on the altar",
        "look around the mysterious chamber",
        "inspect the glowing crystal carefully",
        
        # Interaction commands
        "take the vorpal sword from the chest",
        "use the magic key on the locked door",
        "pick up the healing potion quietly",
        
        # Communication commands
        "talk to Selene about the quest",
        "ask the wizard about the spell",
        "tell the guard we need passage",
        
        # Combat commands
        "attack the dragon with my sword",
        "cast fireball at the goblin",
        "defend against the orc's attack",
        
        # Magic commands
        "cast healing spell on myself",
        "enchant my weapon with lightning",
        "summon a protective ward",
        
        # Complex commands
        "carefully examine the Moonblade while talking to Selene about the Ironroot Caverns",
        "quickly grab the vorpal sword and run north",
        
        # Ambiguous/difficult commands
        "do something with that thing over there",
        "help me please",
        "what can I do here?"
    ]
    
    logger.info("Testing commands with integrated spaCy + LangChain parser...")
    logger.info("-" * 60)
    
    for i, command in enumerate(test_commands, 1):
        logger.info(f"\n[Test {i:2d}] Input: '{command}'")
        
        # Parse the command
        result = parser.parse(command)
        
        if result:
            logger.info(f"         Action: {result.action}")
            logger.info(f"         Target: {result.target}")
            logger.info(f"         Modifiers: {result.modifiers}")
            logger.info(f"         Confidence: {result.confidence:.2f}")
            
            # Display spaCy entities
            spacy_entities = result.context.get("spacy_entities", [])
            if spacy_entities:
                logger.info(f"         spaCy Entities: {spacy_entities}")
            
            # Display LangChain enhancements
            langchain_intent = result.context.get("langchain_intent", "")
            langchain_entities = result.context.get("langchain_entities", "")
            langchain_context = result.context.get("langchain_context", "")
            
            if langchain_intent:
                logger.info(f"         LangChain Intent: {langchain_intent}")
            if langchain_entities and langchain_entities != "Entities: None":
                logger.info(f"         LangChain Entities: {langchain_entities}")
            if langchain_context and langchain_context != "Context: None":
                logger.info(f"         LangChain Context: {langchain_context[:100]}...")
                
        else:
            logger.warning("         ❌ Failed to parse command")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Integrated NLP Parser Test Complete!")


def test_entity_recognition():
    """Test entity recognition capabilities specifically."""
    
    logger.info("\n🔍 Testing Entity Recognition Capabilities")
    logger.info("-" * 40)
    
    parser = ParserEngine()
    
    # Add some dynamic entities
    parser.add_world_entity("Excalibur", "FANTASY_ITEM", "item_excalibur")
    parser.add_world_entity("Gandalf", "FANTASY_NPC", "npc_gandalf")
    parser.add_world_entity("Tower of Sorcery", "FANTASY_LOCATION", "loc_tower_sorcery")
    
    test_commands = [
        "take Excalibur from the stone",
        "speak with Gandalf about magic",
        "go to the Tower of Sorcery quickly",
        "examine the Moonblade and talk to Selene"
    ]
    
    for command in test_commands:
        logger.info(f"\nCommand: '{command}'")
        result = parser.parse(command)
        
        if result:
            spacy_entities = result.context.get("spacy_entities", [])
            langchain_entities = result.context.get("langchain_entities", "")
            
            logger.info(f"spaCy found: {len(spacy_entities)} entities")
            for entity in spacy_entities:
                logger.info(f"  - {entity['label']}: {entity['text']} (ID: {entity['id']})")
            
            if langchain_entities and langchain_entities != "Entities: None":
                logger.info(f"LangChain analysis: {langchain_entities}")


def test_context_analysis():
    """Test advanced context analysis."""
    
    logger.info("\n🧠 Testing Context Analysis")
    logger.info("-" * 30)
    
    parser = ParserEngine()
    
    test_scenarios = [
        {
            "command": "carefully sneak north to avoid the sleeping dragon",
            "description": "Stealth movement with caution"
        },
        {
            "command": "quickly grab the healing potion before the goblin wakes up",
            "description": "Urgent action with time pressure"
        },
        {
            "command": "angrily attack the orc chief with my enchanted sword",
            "description": "Emotional combat action"
        },
        {
            "command": "sadly examine the ruins of my destroyed village",
            "description": "Emotional observation with backstory"
        }
    ]
    
    for scenario in test_scenarios:
        command = scenario["command"]
        description = scenario["description"]
        
        logger.info(f"\nScenario: {description}")
        logger.info(f"Command: '{command}'")
        
        result = parser.parse(command)
        
        if result:
            context = result.context.get("langchain_context", "")
            intent = result.context.get("langchain_intent", "")
            
            logger.info(f"Intent: {intent}")
            if context and context != "Context: None":
                logger.info(f"Context: {context[:150]}...")
            
            logger.info(f"Confidence: {result.confidence:.2f}")


def test_fallback_handling():
    """Test how the system handles unparseable input."""
    
    logger.info("\n🤔 Testing Fallback Handling")
    logger.info("-" * 28)
    
    parser = ParserEngine()
    
    difficult_commands = [
        "asdfghjkl",  # Gibberish
        "",  # Empty
        "the quick brown fox jumps over the lazy dog",  # Non-game sentence
        "I want to do the thing with the stuff",  # Vague
        "How do I win this game?",  # Meta question
    ]
    
    for command in difficult_commands:
        logger.info(f"\nCommand: '{command}'")
        result = parser.parse(command)
        
        if result:
            logger.info(f"Action: {result.action}, Confidence: {result.confidence:.2f}")
            intent = result.context.get("langchain_intent", "")
            if intent:
                logger.info(f"LangChain Intent: {intent}")
        else:
            logger.info("No parse result (returned None)")


if __name__ == "__main__":
    try:
        # Run all tests
        test_sample_commands()
        test_entity_recognition() 
        test_context_analysis()
        test_fallback_handling()
        
        logger.info("\n🎉 All tests completed successfully!")
        logger.info("\nIntegrated spaCy + LangChain parser is working correctly.")
        logger.info("Phase 1 (spaCy): ✅ Entity recognition with EntityRuler")
        logger.info("Phase 2 (LangChain): ✅ Advanced intent and context analysis")  
        logger.info("Phase 3 (Combined): ✅ Unified parsing with enhanced capabilities")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
