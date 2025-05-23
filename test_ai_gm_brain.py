"""
AI GM Brain Test Script

This script demonstrates the basic functionality of the AI GM Brain system.
It shows how to process different types of player input and handle responses.
"""

import sys
import time
from backend.src.ai_gm.ai_gm_brain import get_ai_gm_brain
from backend.src.ai_gm.ai_gm_brain_ooc_integration import extend_ai_gm_brain_with_ooc


def run_test():
    """Run a basic test of AI GM Brain functionality."""
    print("=== AI GM Brain Test ===")
    
    # Create AI GM Brain instance
    game_id = "test_game_session_1"
    player_id = "test_player_1"
    
    print(f"\nInitializing AI GM Brain for game {game_id} and player {player_id}...")
    ai_gm = get_ai_gm_brain(game_id, player_id)
    
    # Extend with OOC functionality
    print("Adding OOC command capabilities...")
    extend_ai_gm_brain_with_ooc(ai_gm)
    
    # Test various input types
    test_inputs = [
        # Simple commands
        "look",
        "go north",
        "take sword",
        
        # Conversational inputs
        "what is this place?",
        "tell me about the history of this town",
        
        # Ambiguous inputs
        "hmm",
        "the dragon",
        
        # OOC commands
        "/ooc help",
        "/ooc stats",
        "/ooc inventory"
    ]
    
    # Process each test input
    for input_text in test_inputs:
        print("\n" + "="*60)
        print(f"PLAYER INPUT: {input_text}")
        print("-"*60)
        
        # Measure processing time
        start_time = time.time()
        response = ai_gm.process_player_input(input_text)
        elapsed = time.time() - start_time
        
        # Display response
        print(f"AI GM RESPONSE: {response['response_text']}")
        print("-"*60)
        print(f"Processing time: {elapsed:.3f} seconds")
        print(f"Complexity: {response['metadata']['complexity']}")
        print(f"Processing mode: {response['metadata']['processing_mode']}")
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Display stats
    print("\n=== AI GM Brain Statistics ===")
    stats = ai_gm.get_processing_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run_test()