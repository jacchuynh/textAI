#!/usr/bin/env python3
"""
AI GM Combined Implementation

This script provides a combined implementation that unifies both the
comprehensive integration approach and the minimal wrapper approach
under a single interface, allowing for easy switching between them.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AIGMMode:
    """Available AI GM implementation modes."""
    UNIFIED = "unified"     # Comprehensive implementation
    MINIMAL = "minimal"     # Minimal wrapper
    AUTO = "auto"           # Automatically choose best available

class AIGMCombined:
    """
    Combined AI GM implementation that provides a unified interface
    to both the comprehensive and minimal implementations.
    """
    
    def __init__(self, game_id: str, player_id: str, initial_context: Optional[Dict[str, Any]] = None, mode: str = AIGMMode.AUTO):
        """
        Initialize the combined AI GM Brain.
        
        Args:
            game_id: Unique identifier for the game session
            player_id: Identifier for the player
            initial_context: Initial game context
            mode: Implementation mode (unified, minimal, or auto)
        """
        self.game_id = game_id
        self.player_id = player_id
        self.initial_context = initial_context or {}
        self.requested_mode = mode
        self.actual_mode = None
        self.implementation = None
        self.info = {
            "initialized_at": datetime.now().isoformat(),
            "requested_mode": mode
        }
        
        # Initialize the implementation
        self._initialize_implementation()
    
    def _initialize_implementation(self):
        """Initialize the appropriate implementation based on the mode."""
        if self.requested_mode == AIGMMode.MINIMAL:
            # Force minimal implementation
            self._initialize_minimal()
        elif self.requested_mode == AIGMMode.UNIFIED:
            # Try unified implementation, fail if not available
            success = self._initialize_unified()
            if not success:
                raise ImportError("Unified implementation not available and mode was set to UNIFIED")
        else:
            # Auto mode - try unified first, fall back to minimal
            success = self._initialize_unified()
            if not success:
                self._initialize_minimal()
    
    def _initialize_unified(self) -> bool:
        """Initialize the unified implementation."""
        try:
            # Try to import the unified implementation
            unified_available = False
            
            # First try ai_gm_unified_demo
            try:
                from ai_gm_unified_demo import create_unified_gm
                self.implementation = create_unified_gm(
                    game_id=self.game_id,
                    player_id=self.player_id,
                    initial_context=self.initial_context
                )
                unified_available = True
                logging.info("Using ai_gm_unified_demo implementation")
            except ImportError:
                # Try ai_gm_direct_test as fallback
                try:
                    from ai_gm_direct_test import create_unified_gm
                    self.implementation = create_unified_gm(
                        game_id=self.game_id,
                        player_id=self.player_id,
                        initial_context=self.initial_context
                    )
                    unified_available = True
                    logging.info("Using ai_gm_direct_test implementation")
                except ImportError:
                    unified_available = False
            
            if unified_available:
                self.actual_mode = AIGMMode.UNIFIED
                self.info["implementation_type"] = "unified"
                return True
            else:
                return False
            
        except Exception as e:
            logging.warning(f"Failed to initialize unified implementation: {e}")
            return False
    
    def _initialize_minimal(self):
        """Initialize the minimal implementation."""
        try:
            # Import the minimal implementation
            from ai_gm_minimal_wrapper import create_minimal_gm
            self.implementation = create_minimal_gm(
                game_id=self.game_id,
                player_id=self.player_id,
                initial_context=self.initial_context
            )
            self.actual_mode = AIGMMode.MINIMAL
            self.info["implementation_type"] = "minimal"
            logging.info("Using minimal wrapper implementation")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize minimal implementation: {e}")
            raise
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """Process player input and return a response."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        response = self.implementation.process_player_input(input_text)
        
        # Add information about which implementation processed this
        if "metadata" not in response:
            response["metadata"] = {}
        
        response["metadata"]["implementation_mode"] = self.actual_mode
        
        return response
    
    def update_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update the game context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        return self.implementation.update_context(context_update)
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current game context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        return self.implementation.get_context()
    
    def set_initial_context(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Set the initial game context, overriding any existing context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        self.initial_context = initial_context
        return self.implementation.set_initial_context(initial_context)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the system status information."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        # Get the implementation's status
        status = self.implementation.get_system_status()
        
        # Add combined implementation info
        status.update({
            "requested_mode": self.requested_mode,
            "actual_mode": self.actual_mode,
            "combined_initialized_at": self.info["initialized_at"],
            "implementation_type": self.info.get("implementation_type", "unknown")
        })
        
        return status
    
    def get_implementation_mode(self) -> str:
        """Get the actual implementation mode being used."""
        return self.actual_mode

def create_ai_gm(
    game_id: str, 
    player_id: str, 
    initial_context: Optional[Dict[str, Any]] = None, 
    mode: str = AIGMMode.AUTO
) -> AIGMCombined:
    """
    Create an AI GM instance using the combined implementation.
    
    Args:
        game_id: Unique identifier for the game session
        player_id: Identifier for the player
        initial_context: Initial game context
        mode: Implementation mode (unified, minimal, or auto)
        
    Returns:
        An initialized AIGMCombined instance
    """
    return AIGMCombined(
        game_id=game_id,
        player_id=player_id,
        initial_context=initial_context,
        mode=mode
    )

def demonstrate_combined_usage():
    """Demonstrate the usage of the combined AI GM implementation."""
    print("=" * 60)
    print("AI GM Combined Implementation Demonstration")
    print("=" * 60)
    
    # Create an AI GM instance in AUTO mode
    print("\nCreating AI GM in AUTO mode...")
    auto_gm = create_ai_gm(
        game_id="auto_demo",
        player_id="auto_player",
        initial_context={
            "player": {
                "name": "Adventurer",
                "domains": {"Combat": 3, "Magic": 4, "Survival": 2},
                "health": 100
            },
            "current_location": "Crossroads",
            "location_description": "A dusty crossroads where several paths meet under an ancient oak tree.",
            "active_npcs": ["Traveling Merchant"]
        }
    )
    
    # Display which implementation was chosen
    print(f"AUTO mode selected: {auto_gm.get_implementation_mode()} implementation")
    
    # Try the minimal implementation explicitly
    print("\nCreating AI GM in MINIMAL mode...")
    minimal_gm = create_ai_gm(
        game_id="minimal_demo",
        player_id="minimal_player",
        initial_context={
            "player": {
                "name": "Ranger",
                "health": 90,
                "equipment": ["Bow", "Dagger", "Rope"]
            },
            "current_location": "Forest Edge",
            "location_description": "The edge of a dense forest. Tall trees cast long shadows.",
            "active_npcs": ["Hunter"]
        },
        mode=AIGMMode.MINIMAL
    )
    
    print(f"Explicitly using: {minimal_gm.get_implementation_mode()} implementation")
    
    # Test both implementations with the same commands
    test_commands = [
        "look around",
        "/help",
        "talk to merchant"
    ]
    
    print("\nTesting both implementations with the same commands:")
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        
        # Process with AUTO mode
        auto_response = auto_gm.process_player_input(cmd)
        print(f"AUTO ({auto_gm.get_implementation_mode()}) response:")
        print(f"  {auto_response['response_text'][:100]}...")
        
        # Process with MINIMAL mode
        minimal_response = minimal_gm.process_player_input(cmd)
        print(f"MINIMAL response:")
        print(f"  {minimal_response['response_text'][:100]}...")
    
    print("\n" + "=" * 60)
    print("Integration Demonstration")
    print("Type commands to interact with the system. Type 'exit' to quit.")
    print("Type 'switch' to toggle between implementations.")
    print("=" * 60 + "\n")
    
    # Use the AUTO implementation for interactive demo
    current_gm = auto_gm
    
    while True:
        mode_label = f"[{current_gm.get_implementation_mode()}]"
        user_input = input(f"{mode_label} > ")
        
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Exiting demo. Thank you for testing!")
            break
        
        if user_input.lower() == "switch":
            # Switch between implementations
            if current_gm == auto_gm:
                current_gm = minimal_gm
                print("Switched to MINIMAL implementation")
            else:
                current_gm = auto_gm
                print(f"Switched to AUTO ({auto_gm.get_implementation_mode()}) implementation")
            continue
        
        # Process the input
        response = current_gm.process_player_input(user_input)
        
        # Display the response
        print(f"\n{response['response_text']}\n")

def main():
    """Main function to run the demonstration."""
    print("🧠 AI GM Combined Implementation")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        demonstrate_combined_usage()
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main() 