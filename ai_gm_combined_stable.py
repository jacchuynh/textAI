#!/usr/bin/env python3
"""
AI GM Combined Implementation (Stable Version)

This script provides a combined implementation that unifies both the
comprehensive integration approach and the minimal wrapper approach
under a single interface, with better error handling and fallbacks.
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

# Define fallback enum classes to avoid dependency issues
class ProcessingMode(Enum):
    NORMAL = auto()
    OOC = auto()
    SYSTEM = auto()
    AMBIENT = auto()

class InputComplexity(Enum):
    SIMPLE_COMMAND = auto()
    COMPLEX_COMMAND = auto()
    CONVERSATION = auto()
    COMPLEX_QUERY = auto()
    OOC_COMMAND = auto()

class ActionSignificance(Enum):
    MINOR = auto()
    MODERATE = auto()
    MAJOR = auto()
    CRITICAL = auto()
    LEGENDARY = auto()

class ReputationLevel(Enum):
    HOSTILE = auto()
    UNFRIENDLY = auto()
    NEUTRAL = auto()
    FRIENDLY = auto()
    ALLIED = auto()

class OutputType(Enum):
    NARRATIVE = auto()
    DIALOGUE = auto()
    DESCRIPTION = auto()
    COMBAT = auto()
    SYSTEM = auto()

class DeliveryChannel(Enum):
    CONSOLE = auto()
    UI = auto()
    AUDIO = auto()
    VISUAL = auto()

class ResponsePriority(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    IMMEDIATE = auto()

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
            
            # First try ai_gm_direct_test
            try:
                from ai_gm_direct_test import create_unified_gm
                self.implementation = create_unified_gm(
                    game_id=self.game_id,
                    player_id=self.player_id,
                    initial_context=self.initial_context
                )
                unified_available = True
                logging.info("Using ai_gm_direct_test implementation")
            except ImportError as e:
                logging.warning(f"Could not import ai_gm_direct_test: {e}")
                # Try importing from backend directory as fallback
                try:
                    from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
                    self.implementation = create_unified_gm(
                        game_id=self.game_id,
                        player_id=self.player_id,
                        initial_context=self.initial_context
                    )
                    unified_available = True
                    logging.info("Using ai_gm_unified_integration implementation")
                except Exception as e:
                    logging.warning(f"Could not import from backend: {e}")
                    unified_available = False
            
            if unified_available:
                self.actual_mode = AIGMMode.UNIFIED
                self.info["implementation_type"] = "unified"
                return True
            else:
                return False
            
        except Exception as e:
            logging.warning(f"Failed to initialize unified implementation: {e}")
            traceback.print_exc()
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
            traceback.print_exc()
            raise
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """Process player input and return a response."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            response = self.implementation.process_player_input(input_text)
            
            # Add information about which implementation processed this
            if "metadata" not in response:
                response["metadata"] = {}
            
            response["metadata"]["implementation_mode"] = self.actual_mode
            
            return response
        except Exception as e:
            logging.error(f"Error processing player input: {e}")
            # Provide a fallback response
            return {
                "status": "error",
                "response_text": f"The AI GM system encountered an error while processing your input. Please try again.",
                "metadata": {
                    "implementation_mode": self.actual_mode,
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
            # Fallback to just updating our local context copy
            self.initial_context.update(context_update)
            return self.initial_context
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current game context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            return self.implementation.get_context()
        except Exception as e:
            logging.error(f"Error getting context: {e}")
            # Return our local copy as fallback
            return self.initial_context
    
    def set_initial_context(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Set the initial game context, overriding any existing context."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        self.initial_context = initial_context
        try:
            return self.implementation.set_initial_context(initial_context)
        except Exception as e:
            logging.error(f"Error setting initial context: {e}")
            return self.initial_context
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the system status information."""
        if not self.implementation:
            raise RuntimeError("AI GM implementation not initialized")
        
        try:
            # Get the implementation's status
            status = self.implementation.get_system_status()
        except Exception as e:
            logging.error(f"Error getting system status from implementation: {e}")
            # Fallback status
            status = {
                "game_id": self.game_id,
                "player_id": self.player_id,
                "status": "degraded",
                "error": str(e)
            }
        
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

def run_non_interactive_demo():
    """Run a non-interactive demonstration of the combined AI GM implementation."""
    print("=" * 60)
    print("AI GM Combined Implementation (Stable) Demo")
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
                "health": 100,
                "equipment": ["Steel Sword", "Leather Armor", "Health Potion"]
            },
            "current_location": "Crossroads",
            "location_description": "A dusty crossroads where several paths meet under an ancient oak tree.",
            "active_npcs": ["Traveling Merchant", "Old Farmer"]
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
            "active_npcs": ["Hunter", "Wolf"]
        },
        mode=AIGMMode.MINIMAL
    )
    
    print(f"Explicitly using: {minimal_gm.get_implementation_mode()} implementation")
    
    # Test both implementations with the same commands
    test_commands = [
        "look around",
        "/help",
        "talk to merchant",
        "examine tree",
        "go north",
        "take sword",
        "/status",
        "/inventory"
    ]
    
    print("\nTesting both implementations with the same commands:")
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        
        # Process with AUTO mode
        auto_response = auto_gm.process_player_input(cmd)
        print(f"AUTO ({auto_gm.get_implementation_mode()}) response:")
        print(f"  {auto_response['response_text']}")
        
        # Process with MINIMAL mode
        minimal_response = minimal_gm.process_player_input(cmd)
        print(f"MINIMAL response:")
        print(f"  {minimal_response['response_text']}")
        
        # Short pause between commands for readability
        time.sleep(0.5)
    
    # Test context update
    print("\n" + "=" * 60)
    print("Testing context updates:")
    
    # Update AUTO GM context
    print("\nUpdating AUTO GM context...")
    auto_gm.update_context({
        "weather": "Rainy",
        "time_of_day": "Night",
        "danger_level": "Moderate"
    })
    
    auto_context = auto_gm.get_context()
    print(f"AUTO GM context updated:")
    print(f"  Weather: {auto_context.get('weather')}")
    print(f"  Time of day: {auto_context.get('time_of_day')}")
    print(f"  Danger level: {auto_context.get('danger_level')}")
    
    # Update MINIMAL GM context
    print("\nUpdating MINIMAL GM context...")
    minimal_gm.update_context({
        "weather": "Foggy",
        "time_of_day": "Dawn",
        "visibility": "Poor"
    })
    
    minimal_context = minimal_gm.get_context()
    print(f"MINIMAL GM context updated:")
    print(f"  Weather: {minimal_context.get('weather')}")
    print(f"  Time of day: {minimal_context.get('time_of_day')}")
    print(f"  Visibility: {minimal_context.get('visibility')}")
    
    # Test system status
    print("\n" + "=" * 60)
    print("System status:")
    
    auto_status = auto_gm.get_system_status()
    print(f"\nAUTO GM status:")
    print(f"  Game ID: {auto_status.get('game_id')}")
    print(f"  Player ID: {auto_status.get('player_id')}")
    print(f"  Requested mode: {auto_status.get('requested_mode')}")
    print(f"  Actual mode: {auto_status.get('actual_mode')}")
    print(f"  Implementation type: {auto_status.get('implementation_type')}")
    
    minimal_status = minimal_gm.get_system_status()
    print(f"\nMINIMAL GM status:")
    print(f"  Game ID: {minimal_status.get('game_id')}")
    print(f"  Player ID: {minimal_status.get('player_id')}")
    print(f"  Requested mode: {minimal_status.get('requested_mode')}")
    print(f"  Actual mode: {minimal_status.get('actual_mode')}")
    print(f"  Implementation type: {minimal_status.get('implementation_type')}")
    
    print("\nNon-interactive demonstration completed!")

def main():
    """Main function to run the demonstration."""
    print("🧠 AI GM Combined Implementation (Stable Version)")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        run_non_interactive_demo()
    except Exception as e:
        print(f"Error during demonstration: {e}")
        traceback.print_exc()
    
    print(f"\nDemo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 