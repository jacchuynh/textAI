#!/usr/bin/env python3
"""
Example AI GM Integration with LLM

This script demonstrates how to integrate the AI GM with LLM support into a real application.
It provides a simple command-line interface for interacting with the AI GM.
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_gm_integration.log'  # Log to file
)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)  # Only show warnings and errors in console
logging.getLogger('').addHandler(console)

# Import the AI GM unified integration
try:
    from ai_gm_unified_integration_full import create_ai_gm, check_openrouter_api_key
except ImportError:
    print("Error: AI GM unified integration not found!")
    print("Make sure ai_gm_unified_integration_full.py is in the current directory.")
    sys.exit(1)

class ExampleGameApp:
    """Example game application using the AI GM with LLM integration."""
    
    def __init__(self):
        """Initialize the example game application."""
        self.game_id = f"example_{int(time.time())}"  # Unique game ID
        self.player_id = "player1"
        self.ai_gm = None
        self.running = False
        self.context = {
            "player": {
                "name": "Hero",
                "domains": {"Combat": 3, "Magic": 4, "Exploration": 2},
                "health": 100,
                "inventory": ["Steel Sword", "Magic Amulet", "Health Potion"]
            },
            # LLM-specific context fields
            "player_name": "Hero",
            "location_name": "Mystic Forest",
            "location_description": "A dense, ancient forest filled with towering trees and magical energy. Glowing fungi illuminate the forest floor, and distant sounds of creatures echo through the trees.",
            "recent_events": [
                "You discovered a hidden path",
                "You found traces of a magical ritual",
                "You heard whispers from deeper in the forest"
            ],
            "active_npcs": [
                {"name": "Forest Spirit", "description": "A glowing, ethereal entity that appears to be watching you"},
                {"name": "Lost Traveler", "description": "A weary traveler who seems disoriented and afraid"}
            ],
            "character_info": {
                "domains": {
                    "Combat": 3,
                    "Magic": 4,
                    "Exploration": 2
                }
            }
        }
    
    async def initialize(self):
        """Initialize the AI GM and check for required dependencies."""
        print("Initializing AI GM integration...")
        
        # Check if OpenRouter API key is set
        if not check_openrouter_api_key():
            print("\nWarning: OpenRouter API key not set!")
            print("LLM functionality will be limited.")
            print("To set up the API key, run: python setup_ai_gm_llm.py --setup\n")
        
        # Create the AI GM instance
        try:
            self.ai_gm = create_ai_gm(
                game_id=self.game_id,
                player_id=self.player_id,
                initial_context=self.context
            )
            print("AI GM initialized successfully!")
            
            # Display system status
            status = self.ai_gm.get_system_status()
            print(f"Game ID: {self.game_id}")
            print(f"LLM Support: {'Available' if status.get('llm_support', False) else 'Not Available'}")
            
            return True
            
        except Exception as e:
            print(f"Error initializing AI GM: {e}")
            logging.error(f"Error initializing AI GM: {e}", exc_info=True)
            return False
    
    async def process_command(self, command: str) -> str:
        """Process a player command through the AI GM."""
        if not self.ai_gm:
            return "Error: AI GM not initialized!"
        
        try:
            # Process the command
            # Use the async version if available, for better LLM integration
            if hasattr(self.ai_gm, 'process_player_input_async'):
                response = await self.ai_gm.process_player_input_async(command)
            else:
                response = self.ai_gm.process_player_input(command)
            
            # Log the response
            if "token_usage" in response:
                tokens = response.get("token_usage", {})
                logging.info(f"Command: '{command}' - Tokens: {tokens.get('total_tokens', 0)}")
            else:
                logging.info(f"Command: '{command}'")
            
            # Return the response text
            return response.get("response_text", "No response")
            
        except Exception as e:
            error_msg = f"Error processing command: {e}"
            logging.error(error_msg, exc_info=True)
            return error_msg
    
    def update_game_state(self, state_update: Dict[str, Any]):
        """Update the game state."""
        if not self.ai_gm:
            print("Error: AI GM not initialized!")
            return
        
        try:
            # Update the context
            self.ai_gm.update_context(state_update)
            print("Game state updated.")
            
        except Exception as e:
            print(f"Error updating game state: {e}")
            logging.error(f"Error updating game state: {e}", exc_info=True)
    
    async def run_interactive_session(self):
        """Run an interactive session with the AI GM."""
        if not self.ai_gm:
            print("Error: AI GM not initialized!")
            return
        
        self.running = True
        print("\n" + "=" * 60)
        print("AI GM Interactive Session")
        print("=" * 60)
        print("Type your commands to interact with the AI GM.")
        print("Type 'exit' or 'quit' to end the session.")
        print("Type 'help' for available commands.")
        print("=" * 60 + "\n")
        
        # Display initial description
        initial_response = await self.process_command("look around")
        print(f"GM: {initial_response}\n")
        
        # Main interaction loop
        while self.running:
            try:
                # Get player input
                command = input("> ").strip()
                
                # Check for special commands
                if command.lower() in ['exit', 'quit']:
                    self.running = False
                    print("Ending session...")
                    break
                    
                if command.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  exit, quit - End the session")
                    print("  help - Display this help message")
                    print("  status - Display game status")
                    print("  inventory - Show your inventory")
                    print("  Any other text will be sent to the AI GM as a command or statement")
                    continue
                
                if command.lower() == 'status':
                    # Get the current context
                    context = self.ai_gm.get_context()
                    player = context.get("player", {})
                    print("\nPlayer Status:")
                    print(f"  Name: {player.get('name', 'Unknown')}")
                    print(f"  Health: {player.get('health', 0)}")
                    
                    # Show domains if available
                    domains = player.get("domains", {})
                    if domains:
                        print("  Domains:")
                        for domain, value in domains.items():
                            print(f"    {domain}: {value}")
                    
                    continue
                
                if command.lower() == 'inventory':
                    # Get the current context
                    context = self.ai_gm.get_context()
                    inventory = context.get("player", {}).get("inventory", [])
                    
                    print("\nInventory:")
                    if inventory:
                        for item in inventory:
                            print(f"  - {item}")
                    else:
                        print("  Your inventory is empty.")
                    
                    continue
                
                # Process the command through the AI GM
                print("Processing...")
                response = await self.process_command(command)
                print(f"\nGM: {response}\n")
                
            except KeyboardInterrupt:
                print("\nSession interrupted by user.")
                self.running = False
                break
                
            except Exception as e:
                print(f"Error: {e}")
                logging.error(f"Error in interactive session: {e}", exc_info=True)
        
        print("\nSession ended.")

async def main():
    """Main function to run the example."""
    print("=" * 60)
    print("AI GM Integration Example with LLM Support")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create and initialize the example game
    app = ExampleGameApp()
    if await app.initialize():
        # Run the interactive session
        await app.run_interactive_session()
    else:
        print("Failed to initialize AI GM. Exiting.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 