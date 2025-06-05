#!/usr/bin/env python3
"""
AI GM Unified Integration (Full LLM Implementation)

This script provides an integration implementation focused solely on the full-featured
unified AI GM Brain system with LLM support. It does not use fallbacks to minimal implementations.
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the unified AI GM Brain components
try:
    # Try to import from backend structure
    from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
    from backend.src.ai_gm.ai_gm_llm_manager import LLMInteractionManager
except ImportError:
    # Try to import from local directory
    try:
        from ai_gm_unified_integration import create_unified_gm
    except ImportError:
        # Try importing from direct_test as fallback
        from ai_gm_direct_test import create_unified_gm

class AIGMUnifiedLLM:
    """
    Unified AI GM implementation with full LLM support.
    This class does not fallback to minimal implementations.
    """
    
    def __init__(self, game_id: str, player_id: str, initial_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the unified AI GM Brain with LLM support.
        
        Args:
            game_id: Unique identifier for the game session
            player_id: Identifier for the player
            initial_context: Initial game context
        """
        self.game_id = game_id
        self.player_id = player_id
        self.initial_context = initial_context or {}
        self.info = {
            "initialized_at": datetime.now().isoformat(),
        }
        
        # Initialize the unified implementation
        self._initialize_unified()
    
    def _initialize_unified(self):
        """Initialize the unified implementation with LLM support."""
        try:
            # Create the unified AI GM with LLM support
            self.implementation = create_unified_gm(
                game_id=self.game_id,
                player_id=self.player_id,
                initial_context=self.initial_context
            )
            
            # Verify LLM support is available
            if not hasattr(self.implementation, 'llm_manager') or not self.implementation.available_systems.get("llm", False):
                self._ensure_llm_support()
                
            # Log initialization
            logging.info(f"Unified AI GM with LLM support initialized for game_id={self.game_id}")
            logging.info(f"OpenRouter API Key: {'Set' if os.environ.get('OPENROUTER_API_KEY') else 'Not Set'}")
            
        except Exception as e:
            logging.error(f"Failed to initialize unified implementation: {e}")
            traceback.print_exc()
            raise RuntimeError(f"Failed to initialize unified AI GM: {e}")
    
    def _ensure_llm_support(self):
        """Ensure LLM support is available by creating and registering the LLM manager."""
        try:
            # Check if we need to create LLM manager
            if not hasattr(self.implementation, 'llm_manager'):
                from backend.src.ai_gm.ai_gm_llm_manager import LLMInteractionManager
                self.implementation.llm_manager = LLMInteractionManager(self.implementation.brain)
                self.implementation.brain.register_extension("llm_manager", self.implementation.llm_manager)
                self.implementation.available_systems["llm"] = True
                logging.info("LLM manager manually registered")
        except Exception as e:
            logging.warning(f"Could not ensure LLM support: {e}")
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input and return a response.
        
        Args:
            input_text: The player's input text
            
        Returns:
            Response dictionary with AI GM's response
        """
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            # Process the player input
            response = self.implementation.process_player_input(input_text)
            
            # Add information about the implementation
            if "metadata" not in response:
                response["metadata"] = {}
            
            response["metadata"]["implementation_type"] = "unified_with_llm"
            
            # Log response stats
            if "token_usage" in response:
                tokens = response.get("token_usage", {})
                logging.info(f"LLM response generated with {tokens.get('total_tokens', 0)} tokens")
            
            return response
            
        except Exception as e:
            logging.error(f"Error processing player input: {e}")
            traceback.print_exc()
            
            # Provide a fallback response
            return {
                "status": "error",
                "response_text": f"The AI GM system encountered an error while processing your input. Please try again.",
                "metadata": {
                    "implementation_type": "unified_with_llm",
                    "error": str(e)
                }
            }
    
    async def process_player_input_async(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input asynchronously (for LLM integration).
        
        Args:
            input_text: The player's input text
            
        Returns:
            Response dictionary with AI GM's response
        """
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            # Process the player input asynchronously
            if hasattr(self.implementation, 'process_player_input_async'):
                response = await self.implementation.process_player_input_async(input_text)
            else:
                # Fallback to synchronous processing
                response = self.implementation.process_player_input(input_text)
            
            # Add information about the implementation
            if "metadata" not in response:
                response["metadata"] = {}
            
            response["metadata"]["implementation_type"] = "unified_with_llm"
            
            return response
            
        except Exception as e:
            logging.error(f"Error processing player input asynchronously: {e}")
            traceback.print_exc()
            
            # Provide a fallback response
            return {
                "status": "error",
                "response_text": f"The AI GM system encountered an error while processing your input. Please try again.",
                "metadata": {
                    "implementation_type": "unified_with_llm",
                    "error": str(e)
                }
            }
    
    def update_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update the game context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            return self.implementation.update_context(context_update)
        except Exception as e:
            logging.error(f"Error updating context: {e}")
            traceback.print_exc()
            raise
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current game context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            return self.implementation.get_context()
        except Exception as e:
            logging.error(f"Error getting context: {e}")
            traceback.print_exc()
            raise
    
    def set_initial_context(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Set the initial game context, overriding any existing context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        self.initial_context = initial_context
        try:
            return self.implementation.set_initial_context(initial_context)
        except Exception as e:
            logging.error(f"Error setting initial context: {e}")
            traceback.print_exc()
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the system status information."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            # Get the implementation's status
            status = self.implementation.get_system_status()
            
            # Add combined implementation info
            status.update({
                "llm_support": hasattr(self.implementation, 'llm_manager'),
                "openrouter_api_key": "Set" if os.environ.get('OPENROUTER_API_KEY') else "Not Set",
                "implementation_type": "unified_with_llm",
                "initialized_at": self.info["initialized_at"],
            })
            
            # Add LLM usage statistics if available
            if hasattr(self.implementation, 'llm_manager') and hasattr(self.implementation.llm_manager, 'get_usage_statistics'):
                status["llm_stats"] = self.implementation.llm_manager.get_usage_statistics()
            
            return status
            
        except Exception as e:
            logging.error(f"Error getting system status: {e}")
            traceback.print_exc()
            
            # Fallback status
            return {
                "status": "error",
                "error": str(e),
                "implementation_type": "unified_with_llm",
                "llm_support": hasattr(self.implementation, 'llm_manager'),
                "openrouter_api_key": "Set" if os.environ.get('OPENROUTER_API_KEY') else "Not Set",
            }
    
    def get_llm_manager(self) -> Any:
        """Get the LLM manager if available."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        if hasattr(self.implementation, 'llm_manager'):
            return self.implementation.llm_manager
        
        raise RuntimeError("LLM manager not available")

def create_ai_gm(
    game_id: str, 
    player_id: str, 
    initial_context: Optional[Dict[str, Any]] = None,
) -> AIGMUnifiedLLM:
    """
    Create an AI GM instance using the unified implementation with LLM support.
    
    Args:
        game_id: Unique identifier for the game session
        player_id: Identifier for the player
        initial_context: Initial game context
        
    Returns:
        An initialized AIGMUnifiedLLM instance
    """
    return AIGMUnifiedLLM(
        game_id=game_id,
        player_id=player_id,
        initial_context=initial_context
    )

def check_openrouter_api_key():
    """Check if the OpenRouter API key is set."""
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        logging.warning("OpenRouter API key not set. LLM functionality will be limited.")
        print("\n⚠️  WARNING: OpenRouter API key not set!")
        print("To enable full LLM functionality, set the OPENROUTER_API_KEY environment variable.")
        print("Example: export OPENROUTER_API_KEY=your_api_key_here\n")
        return False
    return True

def run_demo():
    """Run a demonstration of the unified AI GM with LLM integration."""
    print("=" * 60)
    print("AI GM Unified Integration with LLM Demo")
    print("=" * 60)
    
    # Check OpenRouter API key
    has_api_key = check_openrouter_api_key()
    
    # Create an AI GM instance
    print("\nInitializing AI GM with unified implementation and LLM support...")
    try:
        gm = create_ai_gm(
            game_id="llm_demo",
            player_id="demo_player",
            initial_context={
                "player": {
                    "name": "Adventurer",
                    "domains": {"Combat": 3, "Magic": 4, "Survival": 2},
                    "health": 100,
                    "inventory": ["Steel Sword", "Leather Armor", "Health Potion"]
                },
                "player_name": "Adventurer",  # Added for LLM prompting
                "location_name": "Ancient Forest",
                "location_description": "A dense forest with towering trees. Rays of sunlight pierce through the canopy, illuminating patches of the forest floor.",
                "recent_events": [
                    "You discovered an old stone shrine",
                    "You heard strange whispers in the wind",
                    "You found fresh tracks leading deeper into the forest"
                ],
                "active_npcs": [
                    {"name": "Forest Guardian", "description": "A mysterious figure dressed in green robes"},
                    {"name": "Lost Hunter", "description": "A weary-looking hunter searching for game"}
                ],
                "character_info": {
                    "domains": {
                        "Combat": 3,
                        "Magic": 4,
                        "Survival": 2
                    }
                }
            }
        )
        
        # Display system status
        status = gm.get_system_status()
        print(f"AI GM initialized with unified implementation")
        print(f"LLM Support: {'Available' if status.get('llm_support', False) else 'Not Available'}")
        print(f"OpenRouter API Key: {status.get('openrouter_api_key', 'Not Set')}")
        
        # Test commands
        test_commands = [
            "look around",
            "approach the Forest Guardian",
            "ask the Guardian about the strange whispers",
            "examine the shrine",
            "/help"
        ]
        
        print("\nProcessing commands:")
        for cmd in test_commands:
            print(f"\n> {cmd}")
            response = gm.process_player_input(cmd)
            print(f"Response: {response['response_text']}")
            
            # Add a pause between commands
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print("Demo completed!")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        traceback.print_exc()

def main():
    """Main function to run the demonstration."""
    print("🧠 AI GM Unified Integration with LLM Support")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        run_demo()
    except Exception as e:
        print(f"Error during demonstration: {e}")
        traceback.print_exc()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 