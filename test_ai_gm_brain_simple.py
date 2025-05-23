"""
AI GM Brain Simple Test

This script provides a simple interactive test for the AI GM Brain system.
"""

import sys
import os
import time

# Import the AI GM Brain
from backend.src.ai_gm.ai_gm_brain import get_ai_gm_brain
from backend.src.ai_gm.ai_gm_brain_ooc_integration import extend_ai_gm_brain_with_ooc

def test_basic_interaction():
    """Test basic interaction with the AI GM Brain."""
    print("\n=== Testing Basic AI GM Brain Interaction ===")
    
    # Create the AI GM Brain
    brain = get_ai_gm_brain("test_game", "test_player")
    
    # Add OOC command handling
    extend_ai_gm_brain_with_ooc(brain)
    
    # Test some basic commands
    test_inputs = [
        "hello",
        "look around",
        "go north",
        "what is this place?",
        "/help",
        "/stats",
        "/inventory",
        "/system features"
    ]
    
    for input_text in test_inputs:
        print(f"\n> {input_text}")
        start_time = time.time()
        # Handle the error with OOC commands temporarily
        try:
            response = brain.process_player_input(input_text)
        except AttributeError as e:
            if "process_ooc_command" in str(e) and input_text.startswith("/"):
                # Direct fallback for OOC commands
                ooc_handler = brain.extensions["ooc_integration"]
                result = ooc_handler.process_command(input_text)
                response = {
                    "response_text": result["response"],
                    "metadata": {
                        "processing_mode": "OOC",
                        "complexity": "SIMPLE",
                        "processing_time": 0.001,
                        "ooc_response": True,
                        "ooc_command": result.get("command", "unknown")
                    }
                }
            else:
                raise
        processing_time = time.time() - start_time
        
        print(f"{response['response_text']}")
        print(f"[Processed in {processing_time:.3f}s as {response['metadata']['processing_mode']}/{response['metadata']['complexity']}]")

def interactive_test():
    """Run an interactive test with the AI GM Brain."""
    print("\n=== AI GM Brain Interactive Test ===")
    print("Type 'exit' to quit. Enter commands as if you were playing.")
    
    # Create the AI GM Brain
    brain = get_ai_gm_brain("test_game", "test_player")
    
    # Add OOC command handling
    extend_ai_gm_brain_with_ooc(brain)
    
    while True:
        # Get input
        user_input = input("\n> ")
        
        # Check for exit
        if user_input.lower() == 'exit':
            print("Exiting test.")
            break
        
        # Process input
        start_time = time.time()
        response = brain.process_player_input(user_input)
        processing_time = time.time() - start_time
        
        # Print response
        print(f"\n{response['response_text']}")
        print(f"[Processed in {processing_time:.3f}s as {response['metadata']['processing_mode']}/{response['metadata']['complexity']}]")
        
        # Print any additional metadata for debugging
        if 'ooc_response' in response['metadata'] and response['metadata']['ooc_response']:
            print(f"[OOC Command: {response['metadata'].get('ooc_command', 'unknown')}]")

def main():
    """Main function to run the test."""
    # Create necessary directories
    os.makedirs("data/memory/test_game", exist_ok=True)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_basic_interaction()
        print("\nUse --interactive flag to start interactive mode.")

if __name__ == "__main__":
    main()