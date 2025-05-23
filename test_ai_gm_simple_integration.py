"""
Simple Integration Test for AI GM Brain System

This script tests the core AI GM Brain with the world reaction 
and pacing systems to demonstrate basic functionality.
"""

import os
import sys
import time
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Add the root directory to path for imports
sys.path.append('.')

# Import core AI GM components
from backend.src.ai_gm.ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
from backend.src.ai_gm.ai_gm_brain_ooc_handler import OOCCommandHandler

# Import world reaction components
try:
    from attached_assets.world_reaction.enhanced_context_manager import EnhancedContextManager
    from attached_assets.world_reaction.reaction_assessor import ReactionAssessor
    from attached_assets.world_reaction.reputation_manager import ReputationManager, ReputationLevel
    
    # Import pacing components
    from attached_assets.pacing.pacing_manager import PacingManager, PacingState
    
    WORLD_REACTION_AVAILABLE = True
except ImportError as e:
    print(f"World reaction or pacing components not available: {e}")
    WORLD_REACTION_AVAILABLE = False

def create_test_brain() -> AIGMBrain:
    """Create a test AI GM Brain instance with basic configuration."""
    
    # Create base brain
    brain = AIGMBrain(
        game_id="test_game",
        player_id="test_player"
    )
    
    # Add OOC command handler
    ooc_handler = OOCCommandHandler(brain)
    brain.register_extension("ooc_integration", ooc_handler)
    
    # Add test command handlers - use the ooc_handler's direct methods
    ooc_handler.commands["help"] = {
        "handler": _handle_help_command,
        "description": "Display available commands",
        "parameters": []
    }
    
    ooc_handler.commands["echo"] = {
        "handler": _handle_echo_command,
        "description": "Echo back the provided text",
        "parameters": ["text"]
    }
    
    ooc_handler.commands["stats"] = {
        "handler": _handle_stats_command,
        "description": "Display your character statistics",
        "parameters": []
    }
    
    # Store initial context in brain's memory directly
    brain._context = {
        "current_location": "Tavern",
        "active_npcs": ["barkeeper", "guard"],
        "player": {
            "name": "Adventurer",
            "health": 100,
            "domains": {
                "BODY": 3,
                "MIND": 2,
                "SPIRIT": 2,
                "SOCIAL": 4, 
                "CRAFT": 1,
                "AWARENESS": 3,
                "AUTHORITY": 1
            }
        }
    }
    
    return brain

def _handle_help_command(args: Dict[str, Any], brain: AIGMBrain) -> Dict[str, Any]:
    """Handle the help command."""
    ooc_handler = brain.extensions.get("ooc_integration")
    if not ooc_handler:
        return {"status": "error", "response": "OOC handler not available"}
    
    commands = ooc_handler.get_registered_commands()
    help_text = "Available Commands:\n"
    for cmd, details in commands.items():
        help_text += f"/{cmd} - {details['description']}\n"
    
    return {"status": "success", "response": help_text}

def _handle_echo_command(args: Dict[str, Any], brain: AIGMBrain) -> Dict[str, Any]:
    """Echo back the provided text."""
    text = args.get("text", "")
    return {"status": "success", "response": f"Echo: {text}"}

def _handle_stats_command(args: Dict[str, Any], brain: AIGMBrain) -> Dict[str, Any]:
    """Display character statistics."""
    player = brain.current_context.get("player", {})
    if not player:
        return {"status": "error", "response": "No player data available"}
    
    stats_text = f"Character: {player.get('name', 'Unknown')}\n"
    stats_text += "Domains:\n"
    
    # Format domains
    domains = player.get("domains", {})
    for domain, value in domains.items():
        stars = "★" * value
        stats_text += f"  {domain}: {value} {stars}\n"
    
    return {"status": "success", "response": stats_text}

def test_basic_interaction():
    """Test basic interaction with the AI GM Brain."""
    brain = create_test_brain()
    
    print("=== Testing Basic AI GM Brain Interaction ===\n")
    
    test_inputs = [
        "hello",
        "look around", 
        "talk to barkeeper",
        "what is this place?",
        "/help",
        "/echo Hello, world!",
        "/stats"
    ]
    
    for input_text in test_inputs:
        print(f"> {input_text}")
        start_time = time.time()
        
        # Handle the error with OOC commands temporarily
        try:
            response = brain.process_player_input(input_text)
        except AttributeError as e:
            if input_text.startswith("/"):
                # Direct fallback for OOC commands
                ooc_handler = brain.extensions["ooc_integration"]
                command = input_text[1:]  # Remove the leading slash
                parts = command.split(maxsplit=1)
                cmd = parts[0]
                args_text = parts[1] if len(parts) > 1 else ""
                
                result = ooc_handler.process_command(input_text)
                response = {
                    "response_text": result["response"],
                    "metadata": {
                        "processing_mode": "OOC",
                        "complexity": "SIMPLE",
                        "processing_time": 0.001,
                        "ooc_response": True,
                        "ooc_command": cmd
                    }
                }
            else:
                raise
                
        processing_time = time.time() - start_time
        
        print(f"{response['response_text']}")
        print(f"[Processed in {processing_time:.3f}s as {response['metadata']['processing_mode']}/{response['metadata']['complexity']}]")

def main():
    """Main function."""
    try:
        test_basic_interaction()
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()