#!/usr/bin/env python3
"""
AI GM Integration System - Main Entry Point

This is the main entry point for the AI GM integration system.
It provides a simplified interface for creating and using AI GM instances
using the combined implementation strategy (unified or minimal).
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the stable combined implementation
try:
    from ai_gm_combined_stable import (
        create_ai_gm, AIGMMode, AIGMCombined,
        ProcessingMode, InputComplexity, ActionSignificance
    )
    STABLE_AVAILABLE = True
except ImportError:
    STABLE_AVAILABLE = False
    logging.warning("Could not import stable combined implementation")

def create_game_master(
    game_id: str,
    player_id: str,
    initial_context: Optional[Dict[str, Any]] = None,
    use_unified: bool = True
) -> Any:
    """
    Create an AI Game Master instance for a new game session.
    
    Args:
        game_id: Unique identifier for the game
        player_id: Identifier for the player
        initial_context: Optional initial game context
        use_unified: Whether to use the unified implementation (if False, uses minimal)
        
    Returns:
        An AI GM instance that can process player input
    """
    if not STABLE_AVAILABLE:
        raise ImportError("AI GM Combined implementation not available")
    
    # Determine the mode based on the use_unified parameter
    mode = AIGMMode.AUTO if use_unified else AIGMMode.MINIMAL
    
    # Create and return the AI GM instance
    return create_ai_gm(
        game_id=game_id,
        player_id=player_id,
        initial_context=initial_context,
        mode=mode
    )

def process_command(gm_instance: Any, player_input: str) -> Dict[str, Any]:
    """
    Process a player command using the AI GM.
    
    Args:
        gm_instance: The AI GM instance
        player_input: The player's input text
        
    Returns:
        A response dictionary with the AI GM's response
    """
    return gm_instance.process_player_input(player_input)

def update_game_context(gm_instance: Any, context_update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the game context.
    
    Args:
        gm_instance: The AI GM instance
        context_update: The context updates to apply
        
    Returns:
        The updated context
    """
    return gm_instance.update_context(context_update)

def get_game_context(gm_instance: Any) -> Dict[str, Any]:
    """
    Get the current game context.
    
    Args:
        gm_instance: The AI GM instance
        
    Returns:
        The current game context
    """
    return gm_instance.get_context()

def get_implementation_info(gm_instance: Any) -> Dict[str, Any]:
    """
    Get information about the AI GM implementation.
    
    Args:
        gm_instance: The AI GM instance
        
    Returns:
        Information about the implementation being used
    """
    return {
        "implementation_mode": gm_instance.get_implementation_mode(),
        "status": gm_instance.get_system_status()
    }

def run_demo():
    """Run a simple demonstration of the AI GM integration."""
    print("=" * 60)
    print("AI GM Integration Demo")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create a Game Master instance with AUTO mode
    print("\nCreating AI Game Master...")
    gm = create_game_master(
        game_id="demo_session",
        player_id="demo_player",
        initial_context={
            "player": {
                "name": "Hero",
                "health": 100,
                "inventory": ["Map", "Compass", "Rations"]
            },
            "location": "Village Square",
            "time_of_day": "Morning",
            "weather": "Clear"
        }
    )
    
    # Show which implementation was selected
    info = get_implementation_info(gm)
    print(f"Using {info['implementation_mode']} implementation")
    
    # Process a few commands
    commands = [
        "look around",
        "check map",
        "/help",
        "go to tavern"
    ]
    
    print("\nProcessing commands:")
    for cmd in commands:
        print(f"\n> {cmd}")
        response = process_command(gm, cmd)
        print(f"Response: {response['response_text']}")
    
    # Update context
    print("\nUpdating game context...")
    update_game_context(gm, {
        "location": "Tavern",
        "time_of_day": "Afternoon",
        "active_npcs": ["Barkeeper", "Adventurer", "Musician"]
    })
    
    # Show updated context
    context = get_game_context(gm)
    print(f"\nUpdated context:")
    print(f"  Location: {context.get('location')}")
    print(f"  Time: {context.get('time_of_day')}")
    print(f"  NPCs: {', '.join(context.get('active_npcs', []))}")
    
    # Process more commands with updated context
    more_commands = [
        "look around",
        "talk to barkeeper",
        "order a drink"
    ]
    
    print("\nProcessing more commands with updated context:")
    for cmd in more_commands:
        print(f"\n> {cmd}")
        response = process_command(gm, cmd)
        print(f"Response: {response['response_text']}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        print("AI GM Integration System")
        print("=" * 60)
        print("Import this module to use the AI GM integration in your application.")
        print("Run with --demo argument to see a demonstration.")

if __name__ == "__main__":
    main() 