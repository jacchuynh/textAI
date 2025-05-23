"""
AI GM Brain - Example Implementation

This module provides an example implementation of the AI GM Brain that shows
how it can be integrated with the existing game systems.
"""

import logging
import asyncio
from typing import Dict, Any

# Import core brain components
from .ai_gm_brain import get_ai_gm_brain, InputComplexity, ProcessingMode
from .ai_gm_brain_ooc_integration import extend_ai_gm_brain_with_ooc
from .ai_gm_llm_manager import extend_ai_gm_brain_with_llm


class AIGMExample:
    """
    Example implementation of the AI GM Brain integration.
    
    This class shows how the AI GM Brain can be:
    1. Initialized and configured
    2. Extended with OOC and LLM capabilities
    3. Used to process player input
    """
    
    def __init__(self, game_id: str = "test_game", player_id: str = "test_player"):
        """
        Initialize the AI GM Example.
        
        Args:
            game_id: Game session ID
            player_id: Player character ID
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("AIGMExample")
        
        # Get AI GM Brain instance
        self.brain = get_ai_gm_brain(game_id, player_id)
        
        # Extend with OOC and LLM capabilities
        extend_ai_gm_brain_with_ooc(self.brain)
        # LLM extension would be added in Phase 2
        # extend_ai_gm_brain_with_llm(self.brain)
        
        self.logger.info("AI GM Example initialized")
    
    def process_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input through the AI GM Brain.
        
        Args:
            input_text: Player input text
            
        Returns:
            Response data from the AI GM Brain
        """
        # Process through the AI GM Brain
        response = self.brain.process_player_input(input_text)
        
        # Log for debugging
        self.logger.info(f"Input: '{input_text}'")
        self.logger.info(f"Response: '{response['response_text']}'")
        self.logger.info(f"Processing time: {response['metadata']['processing_time']:.3f}s")
        
        return response


def run_example():
    """
    Run an interactive example of the AI GM Brain.
    
    This function sets up the AI GM Brain and allows for
    interactive testing via console input.
    """
    # Create example instance
    example = AIGMExample()
    
    print("\n===== AI GM Brain Interactive Example =====")
    print("Type 'exit' to quit.")
    print("Type '/ooc help' to see available OOC commands.")
    print("================================================\n")
    
    # Process input until exit
    while True:
        try:
            # Get input
            user_input = input("\nEnter your command or message: ")
            
            # Check for exit
            if user_input.lower() == 'exit':
                print("Exiting example.")
                break
            
            # Process input
            response = example.process_input(user_input)
            
            # Print response
            print("\nAI GM: " + response["response_text"])
            
            # Print metadata in debug mode
            if '--debug' in user_input:
                print("\nResponse Metadata:")
                for key, value in response["metadata"].items():
                    print(f"- {key}: {value}")
        
        except KeyboardInterrupt:
            print("\nExiting example.")
            break
        
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    run_example()