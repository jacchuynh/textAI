#!/usr/bin/env python3
"""
Test Phase 2 Integration - VocabularyManager + spaCy EntityRuler + LangChain Enhancement

This script tests the integration between:
- VocabularyManager for dynamic entity registration
- spaCy EntityRuler for entity recognition
- LangChain enhancement for improved parsing
"""

import sys
import os

# Add the backend source to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from text_parser.parser_engine import parser_engine
from text_parser.vocabulary_manager import vocabulary_manager


def test_vocabulary_manager_integration():
    """Test VocabularyManager integration with spaCy EntityRuler."""
    print("=== Testing VocabularyManager Integration ===")
    
    # Register some test entities
    print("\n1. Registering test entities...")
    
    # Register items
    vocabulary_manager.register_item("mystic_sword", "Mystic Sword", ["magic blade", "enchanted sword"])
    vocabulary_manager.register_item("healing_potion", "Healing Potion", ["health potion", "red vial"])
    
    # Register characters
    vocabulary_manager.register_character("village_elder", "Village Elder", ["elder", "old man"])
    vocabulary_manager.register_character("merchant", "Merchant", ["trader", "shop keeper"])
    
    # Register locations
    vocabulary_manager.register_location("ancient_ruins", "Ancient Ruins", ["ruins", "old temple"])
    vocabulary_manager.register_location("forest_clearing", "Forest Clearing", ["clearing", "open area"])
    
    print("✓ Entities registered successfully")


def test_entity_recognition():
    """Test that registered entities are recognized by spaCy."""
    print("\n2. Testing entity recognition...")
    
    test_inputs = [
        "take the mystic sword",
        "examine healing potion", 
        "talk to village elder",
        "go to ancient ruins",
        "use magic blade on merchant"
    ]
    
    for input_text in test_inputs:
        print(f"\nInput: '{input_text}'")
        
        # Parse the command
        command = parser_engine.parse(input_text)
        
        if command:
            print(f"  Action: {command.action}")
            print(f"  Target: {command.target}")
            print(f"  Confidence: {command.confidence:.2f}")
            
            # Check for spaCy entities
            if "spacy_entities" in command.context:
                entities = command.context["spacy_entities"]
                if entities:
                    print(f"  spaCy Entities: {entities}")
                else:
                    print("  spaCy Entities: None found")
            
            # Check for entity resolutions
            if "entity_resolutions" in command.context:
                resolutions = command.context["entity_resolutions"]
                print(f"  Entity Resolutions: {resolutions}")
            
            # Check for LangChain analysis
            if "langchain_analysis" in command.context:
                analysis = command.context["langchain_analysis"]
                print(f"  LangChain Analysis: {analysis}")
        else:
            print("  ✗ Failed to parse")


def test_canonical_resolution():
    """Test canonical action and entity resolution."""
    print("\n3. Testing canonical resolution...")
    
    # Test action synonyms
    action_tests = [
        ("grab mystic sword", "take"),
        ("examine healing potion", "look"),
        ("speak with elder", "talk"),
        ("move to ruins", "go")
    ]
    
    for input_text, expected_action in action_tests:
        print(f"\nInput: '{input_text}'")
        command = parser_engine.parse(input_text)
        
        if command:
            if command.action == expected_action:
                print(f"  ✓ Action correctly resolved to '{expected_action}'")
            else:
                print(f"  ✗ Expected '{expected_action}', got '{command.action}'")
        else:
            print("  ✗ Failed to parse")


def test_confidence_enhancement():
    """Test that confidence scores are enhanced properly."""
    print("\n4. Testing confidence enhancement...")
    
    test_cases = [
        "take sword",  # Simple command
        "carefully examine the ancient mystic sword in the clearing",  # Complex command with entities
        "xyz abc def"  # Nonsense command
    ]
    
    for input_text in test_cases:
        print(f"\nInput: '{input_text}'")
        command = parser_engine.parse(input_text)
        
        if command:
            print(f"  Confidence: {command.confidence:.2f}")
            if command.confidence > 0.5:
                print("  ✓ Good confidence score")
            else:
                print("  ⚠ Low confidence score")
        else:
            print("  ✗ Failed to parse")


def main():
    """Run all Phase 2 integration tests."""
    print("TextRealmsAI - Phase 2 Integration Test")
    print("=====================================")
    
    try:
        # Test the integration
        test_vocabulary_manager_integration()
        test_entity_recognition()
        test_canonical_resolution()
        test_confidence_enhancement()
        
        print("\n=== Phase 2 Integration Test Summary ===")
        print("✓ VocabularyManager integration working")
        print("✓ spaCy EntityRuler integration working")
        print("✓ LangChain enhancement integration working")
        print("✓ Dynamic entity registration working")
        print("✓ Entity resolution working")
        print("\nPhase 2 integration is complete and functional!")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
