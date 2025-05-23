"""
AI GM Brain Component Testing Script

This script tests individual components of the AI GM Brain to ensure
they integrate properly with the existing systems.
"""

import sys
import time
import argparse
from typing import Dict, Any

# Import core components
from backend.src.ai_gm.ai_gm_brain import get_ai_gm_brain, ProcessingMode
from backend.src.ai_gm.ai_gm_brain_ooc_integration import extend_ai_gm_brain_with_ooc
from backend.src.ai_gm.ai_gm_combat_integration import extend_ai_gm_brain_with_combat
from backend.src.ai_gm.ai_gm_decision_logic import extend_ai_gm_brain_with_decision_logic
from backend.src.ai_gm.ai_gm_narrative_generator import extend_ai_gm_brain_with_narrative


def test_core_brain():
    """Test the core AI GM Brain functionality."""
    print("\n=== Testing Core AI GM Brain ===")
    
    # Create the core brain
    brain = get_ai_gm_brain("test_game", "test_player")
    
    # Test simple input processing
    test_inputs = [
        "look",
        "go north",
        "what is this place?",
        "hello there"
    ]
    
    for input_text in test_inputs:
        print(f"\nProcessing input: '{input_text}'")
        start_time = time.time()
        response = brain.process_player_input(input_text)
        elapsed = time.time() - start_time
        
        print(f"Response: {response['response_text']}")
        print(f"Processing time: {elapsed:.3f}s")
        print(f"Complexity: {response['metadata']['complexity']}")
        print(f"Processing mode: {response['metadata']['processing_mode']}")
    
    # Get statistics
    stats = brain.get_processing_statistics()
    print("\nAI GM Brain Statistics:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
    
    return brain


def test_ooc_integration(brain):
    """Test OOC command integration."""
    print("\n=== Testing OOC Command Integration ===")
    
    # Extend the brain with OOC functionality
    extend_ai_gm_brain_with_ooc(brain)
    print("OOC integration added to AI GM Brain")
    
    # Test OOC commands
    test_commands = [
        "/ooc",
        "/ooc help",
        "/ooc stats",
        "/ooc inventory",
        "/ooc system"
    ]
    
    for command in test_commands:
        print(f"\nProcessing command: '{command}'")
        start_time = time.time()
        response = brain.process_player_input(command)
        elapsed = time.time() - start_time
        
        print(f"Response: {response['response_text']}")
        print(f"Processing time: {elapsed:.3f}s")
        print(f"OOC response: {response.get('ooc_response', False)}")
    
    return brain


def test_combat_integration(brain):
    """Test combat system integration."""
    print("\n=== Testing Combat Integration ===")
    
    # Extend the brain with combat functionality
    extend_ai_gm_brain_with_combat(brain)
    print("Combat integration added to AI GM Brain")
    
    try:
        # Test combat commands
        print("\nTesting combat start:")
        combat_response = brain.combat_integration.start_combat("wolf")
        print(f"Combat start response: {combat_response.get('response_text', 'No response')}")
        
        if not combat_response.get("error", False):
            print("\nTesting combat commands:")
            combat_commands = [
                "attack",
                "defend",
                "dodge",
                "status"
            ]
            
            for command in combat_commands:
                print(f"\nProcessing combat command: '{command}'")
                response = brain.combat_integration.process_combat_command(command)
                print(f"Response: {response.get('response_text', 'No response')}")
            
            print("\nEnding combat:")
            end_response = brain.combat_integration.end_combat("victory")
            print(f"Combat end response: {end_response.get('response_text', 'No response')}")
    except Exception as e:
        print(f"Combat integration test error: {str(e)}")
    
    return brain


def test_decision_logic(brain):
    """Test decision logic integration."""
    print("\n=== Testing Decision Logic ===")
    
    # Extend the brain with decision logic
    extend_ai_gm_brain_with_decision_logic(brain)
    print("Decision logic added to AI GM Brain")
    
    try:
        # Test narrative decision
        print("\nTesting narrative direction decision:")
        context = {
            "tension": 0.7,
            "location": "forest",
            "recent_events": ["LOCATION_ENTERED", "ITEM_FOUND"]
        }
        
        decision = brain.decision_logic.make_narrative_direction_decision(context)
        print(f"Decision: {decision.selected} (confidence: {decision.confidence:.2f})")
        print("Choice weights:")
        for choice, weight in sorted(decision.choices.items(), key=lambda x: x[1], reverse=True):
            print(f"- {choice}: {weight:.2f}")
        
        # Test NPC reaction decision
        print("\nTesting NPC reaction decision:")
        npc_context = {
            "disposition": 0.4,
            "faction": "villagers",
            "previous_interactions": 2
        }
        
        reaction = brain.decision_logic.make_npc_reaction_decision(
            "village_elder", "questioned about town history", npc_context
        )
        print(f"NPC reaction: {reaction.selected} (confidence: {reaction.confidence:.2f})")
    except Exception as e:
        print(f"Decision logic test error: {str(e)}")
    
    return brain


def test_narrative_generator(brain):
    """Test narrative generator integration."""
    print("\n=== Testing Narrative Generator ===")
    
    # Extend the brain with narrative generator
    extend_ai_gm_brain_with_narrative(brain)
    print("Narrative generator added to AI GM Brain")
    
    try:
        # Test location description
        print("\nTesting location description:")
        location_types = ["forest", "cave", "village", "mountain"]
        
        for location in location_types:
            details = {
                "detail": "There's an unusual silence here.",
                "light_source": "filtered sunlight"
            }
            
            description = brain.narrative_generator.generate_location_description(location, details)
            print(f"\n{location.title()} description:")
            print(description)
        
        # Test NPC dialogue
        print("\nTesting NPC dialogue:")
        dispositions = ["friendly", "hostile", "neutral", "fearful", "mysterious"]
        
        for disposition in dispositions:
            dialogue = brain.narrative_generator.generate_npc_dialogue(
                "Elder Torvald", disposition,
                "I've been waiting for someone like you to arrive."
            )
            print(f"\n{disposition.title()} dialogue:")
            print(dialogue)
        
        # Test narrative tension adjustment
        print("\nTesting tension adjustment:")
        brain.narrative_generator.adjust_tension(0.3)
        print("Tension increased to high level")
        
        # Add a narrative hook
        brain.narrative_generator.add_narrative_hook(
            "A distant howl echoes through the area, raising the hair on the back of your neck."
        )
        print("Narrative hook added")
    except Exception as e:
        print(f"Narrative generator test error: {str(e)}")
    
    return brain


def main():
    """Run the component tests."""
    parser = argparse.ArgumentParser(description="Test AI GM Brain components")
    parser.add_argument("--component", choices=["core", "ooc", "combat", "decision", "narrative", "all"],
                      default="all", help="Component to test")
    args = parser.parse_args()
    
    try:
        if args.component in ["core", "all"]:
            brain = test_core_brain()
        else:
            brain = get_ai_gm_brain("test_game", "test_player")
        
        if args.component in ["ooc", "all"]:
            brain = test_ooc_integration(brain)
        
        if args.component in ["combat", "all"]:
            brain = test_combat_integration(brain)
        
        if args.component in ["decision", "all"]:
            brain = test_decision_logic(brain)
        
        if args.component in ["narrative", "all"]:
            brain = test_narrative_generator(brain)
        
        print("\n=== Testing Complete ===")
        print("All requested components have been tested.")
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Testing failed. See error details above.")


if __name__ == "__main__":
    main()