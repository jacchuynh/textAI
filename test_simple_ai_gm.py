"""
Simple Test for AI GM Brain and Basic Integrations

This script demonstrates the basic functionality of the AI GM Brain system
with some of the integration components.
"""

import os
import sys
import time
from typing import Dict, Any, List

# Add the root directory to path for imports
sys.path.append('.')

# Import the AI GM Brain and OOC handler
from backend.src.ai_gm.ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
from backend.src.ai_gm.ai_gm_brain_ooc_handler import OOCCommandHandler

def setup_brain():
    """Set up a basic AI GM Brain with OOC commands for testing."""
    # Create the brain
    brain = AIGMBrain(
        game_id="test_game",
        player_id="test_player"
    )
    
    # Set up OOC handler
    ooc_handler = OOCCommandHandler(brain)
    brain.register_extension("ooc_integration", ooc_handler)
    
    # We'll use the existing OOC command handlers without modifying them
    # This is simpler and will work with the existing structure
    
    return brain

def run_test_inputs(brain, inputs):
    """Run a series of test inputs through the brain and display results."""
    print("\n=== Running Test Inputs ===")
    
    for input_text in inputs:
        print(f"\n> {input_text}")
        start_time = time.time()
        
        try:
            response = brain.process_player_input(input_text)
            processing_time = time.time() - start_time
            
            # Display response
            print(f"{response['response_text']}")
            
            # Display metadata
            mode = response['metadata']['processing_mode']
            complexity = response['metadata']['complexity']
            print(f"[Processed in {processing_time:.3f}s as {mode}/{complexity}]")
            
        except Exception as e:
            print(f"Error processing input: {e}")
            import traceback
            traceback.print_exc()

def run_interactive_console(brain):
    """Run an interactive console for testing the AI GM Brain."""
    print("\n=== AI GM Brain Interactive Console ===")
    print("Type your input to interact with the AI GM. Type 'exit' to quit.")
    
    while True:
        user_input = input("\n> ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
            
        start_time = time.time()
        
        try:
            response = brain.process_player_input(user_input)
            processing_time = time.time() - start_time
            
            # Display response
            print(f"{response['response_text']}")
            
            # Display metadata
            mode = response['metadata']['processing_mode']
            complexity = response['metadata']['complexity'] 
            print(f"[Processed in {processing_time:.3f}s as {mode}/{complexity}]")
            
        except Exception as e:
            print(f"Error processing input: {e}")

def main():
    """Main function to run the tests."""
    # Set up the AI GM Brain
    brain = setup_brain()
    
    # Define test inputs
    test_inputs = [
        "hello",
        "look around",
        "talk to the bartender",
        "/help",
        "/stats",
        "/look"
    ]
    
    # Run the test inputs
    run_test_inputs(brain, test_inputs)
    
    # Run interactive console if requested
    try:
        choice = input("\nDo you want to enter interactive mode? (y/n): ").lower()
        if choice.startswith("y"):
            run_interactive_console(brain)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()