"""
Decision Logic & Mechanical Integration Test Script

This script demonstrates the Decision Tree Logic and Mechanical Integration
components of the AI GM Brain system.
"""

import sys
import time
from typing import Dict, Any, List

# Import core components
from backend.src.ai_gm.ai_gm_brain import get_ai_gm_brain, ProcessingMode
from backend.src.ai_gm.ai_gm_decision_logic import extend_ai_gm_brain_with_decision_logic
from backend.src.ai_gm.ai_gm_mechanical_integration import extend_ai_gm_brain_with_mechanical_integration


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 60 + "\n")


def test_decision_tree_logic():
    """Test the decision tree logic implementation."""
    print("\n=== Testing AI GM Decision Tree Logic ===")
    
    # Create AI GM Brain
    brain = get_ai_gm_brain("test_game", "test_player")
    
    # Extend with decision logic
    extend_ai_gm_brain_with_decision_logic(brain)
    
    print("Decision logic added to AI GM Brain")
    
    # Test with mocked parsed command and LLM output
    parsed_command = {
        "command": "look",
        "target": "room"
    }
    
    # Test different scenarios using the decision tree
    
    # Scenario 1: LLM identified opportunity
    print("\nScenario 1: LLM identified narrative opportunity")
    llm_output = {
        "player_intent_summary": "The player wants to investigate the strange glowing crystal.",
        "suggested_gm_acknowledgement": "You approach the strange crystal, its eerie light casting shadows across the cavern walls.",
        "aligned_opportunity_id": "mystery_crystal_investigation"
    }
    
    result = brain.process_decision_tree(parsed_command, llm_output)
    
    print(f"Action taken: {result.get('action_taken')}")
    print(f"Response basis: {result.get('response_basis')}")
    print(f"Suggested response: {result.get('suggested_response')}")
    print(f"Success: {result.get('success')}")
    
    # Scenario 2: LLM identified branch action
    print("\nScenario 2: LLM identified branch action")
    llm_output = {
        "player_intent_summary": "The player wants to pick the lock on the chest.",
        "suggested_gm_acknowledgement": "You kneel before the ornate chest and pull out your lockpicks.",
        "aligned_branch_action": "pick_lock"
    }
    
    result = brain.process_decision_tree(parsed_command, llm_output)
    
    print(f"Action taken: {result.get('action_taken')}")
    print(f"Response basis: {result.get('response_basis')}")
    print(f"Suggested response: {result.get('suggested_response')}")
    print(f"Success: {result.get('success')}")
    
    # Scenario 3: Parsed command only
    print("\nScenario 3: Parsed command only")
    llm_output = {
        "player_intent_summary": "The player wants to look around the room.",
        "suggested_gm_acknowledgement": "You survey your surroundings carefully."
    }
    
    result = brain.process_decision_tree(parsed_command, llm_output)
    
    print(f"Action taken: {result.get('action_taken')}")
    print(f"Response basis: {result.get('response_basis')}")
    print(f"Suggested response: {result.get('suggested_response')}")
    print(f"Success: {result.get('success')}")
    
    # Scenario 4: General LLM interpretation
    print("\nScenario 4: General LLM interpretation (no specific alignment or parsed command)")
    parsed_command = None
    llm_output = {
        "player_intent_summary": "The player is asking about the history of the castle.",
        "suggested_gm_acknowledgement": "The castle dates back to the Third Era, built by the ancient Durmand dynasty as a fortress against the northern invaders."
    }
    
    result = brain.process_decision_tree(parsed_command, llm_output)
    
    print(f"Action taken: {result.get('action_taken')}")
    print(f"Response basis: {result.get('response_basis')}")
    print(f"Suggested response: {result.get('suggested_response')}")
    print(f"Success: {result.get('success')}")
    
    # Get statistics
    print("\nDecision Tree Statistics:")
    stats = brain.decision_logic.decision_tree.get_statistics()
    for key, value in stats.items():
        print(f"- {key}: {value}")
    
    return brain


def test_mechanical_integration(brain):
    """Test the mechanical integration implementation."""
    print("\n=== Testing Mechanical Integration ===")
    
    # Extend with mechanical integration
    extend_ai_gm_brain_with_mechanical_integration(brain)
    
    print("Mechanical integration added to AI GM Brain")
    
    # Test different mechanical outcomes and their integration into narrative responses
    
    # Scenario 1: Skill check success
    print("\nScenario 1: Skill check success")
    base_response = "You attempt to climb the steep cliff"
    outcome = {
        "success": True,
        "action_type": "climb",
        "details": {
            "skill_check": {
                "result": "success",
                "roll": 18,
                "dc": 15,
                "skill": "climbing"
            }
        },
        "message": "You successfully climb the cliff."
    }
    context = {"location": "mountain_pass", "weather": "clear"}
    
    enhanced_response = brain.integrate_mechanical_outcome(base_response, outcome, context)
    print(f"Enhanced response: {enhanced_response}")
    
    # Scenario 2: Combat failure
    print("\nScenario 2: Combat failure")
    base_response = "You swing your sword at the goblin"
    outcome = {
        "success": False,
        "action_type": "attack",
        "details": {
            "combat": {
                "damage_dealt": 0,
                "target": "the goblin",
                "attack_type": "sword swing"
            }
        },
        "message": "Your attack misses."
    }
    context = {"combat": True, "enemies": ["goblin"]}
    
    enhanced_response = brain.integrate_mechanical_outcome(base_response, outcome, context)
    print(f"Enhanced response: {enhanced_response}")
    
    # Scenario 3: Progression success
    print("\nScenario 3: Progression success")
    base_response = "You place the ancient key in the lock and turn it"
    outcome = {
        "success": True,
        "action_type": "unlock",
        "details": {
            "progression": {
                "advanced": True,
                "new_stage": "crypt_entrance"
            }
        },
        "message": "The door unlocks with a satisfying click."
    }
    context = {"quest": "tomb_raiders", "stage": "find_key"}
    
    enhanced_response = brain.integrate_mechanical_outcome(base_response, outcome, context)
    print(f"Enhanced response: {enhanced_response}")
    
    # Get statistics
    print("\nMechanical Integration Statistics:")
    stats = brain.mechanical_integration.get_statistics()
    for key, value in stats.items():
        print(f"- {key}: {value}")


def test_full_player_input_processing(brain):
    """Test full player input processing with decision tree and mechanical integration."""
    print("\n=== Testing Full Player Input Processing ===")
    
    # Test different player inputs
    test_inputs = [
        "look around the cave",
        "pick the lock on the chest",
        "attack the goblin with my sword",
        "tell me about the history of this place"
    ]
    
    for input_text in test_inputs:
        print(f"\nProcessing input: '{input_text}'")
        
        start_time = time.time()
        response = brain.process_player_input(input_text)
        elapsed = time.time() - start_time
        
        print(f"Response: {response['response_text']}")
        print(f"Processing time: {elapsed:.3f}s")
        
        # Print decision tree metadata if available
        if 'decision_tree' in response.get('metadata', {}):
            decision_info = response['metadata']['decision_tree']
            print("\nDecision Tree Info:")
            print(f"- Action taken: {decision_info.get('action_taken')}")
            print(f"- Response basis: {decision_info.get('response_basis')}")
            
            # Print mechanical outcome if available
            if 'mechanical_outcome' in decision_info:
                print("\nMechanical Outcome:")
                outcome = decision_info['mechanical_outcome']
                print(f"- Success: {outcome.get('success')}")
                if 'details' in outcome:
                    print(f"- Details: {outcome.get('details')}")


def main():
    """Main function to run the tests."""
    print_separator()
    brain = test_decision_tree_logic()
    
    print_separator()
    test_mechanical_integration(brain)
    
    print_separator()
    test_full_player_input_processing(brain)
    
    print_separator()
    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    main()