"""
Comprehensive Integration Test for AI GM Brain System

This script demonstrates the full AI GM Brain system with all integrated components:
- Core brain processing
- OOC command handling
- World reaction assessment
- Pacing and ambient content
- Output generation and formatting
"""

import os
import sys
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root directory to the path for imports
sys.path.append('.')

# Import the integrated AI GM system
from backend.src.ai_gm.ai_gm_integration import (
    create_integrated_gm,
    AIGMIntegrated, 
    OutputType,
    DeliveryChannel,
    ResponsePriority
)

class AIGMTester:
    """Test harness for the integrated AI GM Brain system."""
    
    def __init__(self, game_id: str = "test_game", player_id: str = "test_player"):
        """
        Initialize the AI GM tester.
        
        Args:
            game_id: Game session ID to use
            player_id: Player ID to use
        """
        # Create integrated AI GM
        self.integrated_gm = create_integrated_gm(game_id, player_id)
        
        # Set up initial game state for testing
        self._setup_test_environment()
        
        # Track test statistics
        self.test_stats = {
            "inputs_processed": 0,
            "ooc_commands": 0,
            "world_reactions": 0,
            "ambient_content": 0,
            "start_time": datetime.now()
        }
    
    def _setup_test_environment(self):
        """Set up test environment with initial context."""
        # Create a fictional game world for testing
        initial_context = {
            "current_location": "The Crimson Blade Tavern",
            "location_description": "A lively tavern with wooden beams and a roaring fireplace. The air is filled with the scent of ale and roasted meats.",
            "active_npcs": ["Galen (Barkeeper)", "Lyra (Bard)", "Sergeant Voss", "Mysterious Stranger"],
            "known_locations": [
                "Town Square", 
                "Merchant District", 
                "The Crimson Blade Tavern",
                "Temple of Light",
                "Northern Gate"
            ],
            "time_of_day": "Evening",
            "weather": "Light rain",
            "player": {
                "name": "Adventurer",
                "domains": {
                    "BODY": 3,
                    "MIND": 2,
                    "SPIRIT": 2,
                    "SOCIAL": 4,
                    "CRAFT": 1,
                    "AWARENESS": 3,
                    "AUTHORITY": 1,
                    "FIRE": 0,
                    "WATER": 0,
                    "EARTH": 0,
                    "AIR": 0
                },
                "health": 100,
                "max_health": 100,
                "experience": 150,
                "inventory": [
                    "Short sword",
                    "Leather armor",
                    "Backpack",
                    "3 health potions",
                    "25 gold coins"
                ],
                "quests": [
                    {
                        "name": "Strange Disappearances",
                        "description": "Investigate the recent disappearances in the northern forest",
                        "status": "active"
                    }
                ]
            }
        }
        
        # Set initial context
        self.integrated_gm.set_initial_context(initial_context)
    
    async def run_interactive_console(self):
        """Run an interactive console for testing the AI GM Brain."""
        self._display_welcome()
        
        try:
            while True:
                try:
                    # Get input from user
                    user_input = input("\n> ")
                    
                    # Check for quit command
                    if user_input.lower() in ["quit", "exit", "/quit", "/exit"]:
                        print("Exiting test console...")
                        self._display_stats()
                        break
                        
                    # Check for special test commands
                    if user_input.startswith("!"):
                        self._handle_test_command(user_input[1:])
                        continue
                    
                    # Process input through integrated GM
                    await self._process_and_display(user_input)
                    
                except KeyboardInterrupt:
                    print("\nExiting test console...")
                    break
                    
                except Exception as e:
                    print(f"Error processing input: {e}")
        finally:
            self._display_stats()
    
    async def _process_and_display(self, input_text: str):
        """Process input and display the result nicely formatted."""
        # Track input
        self.test_stats["inputs_processed"] += 1
        
        # Check for OOC command
        if input_text.startswith("/"):
            self.test_stats["ooc_commands"] += 1
        
        # Process through integrated GM
        try:
            print("\nProcessing...")
            result = await self.integrated_gm.process_input_with_reactions(input_text)
            
            # Display the result
            self._display_formatted_response(result)
            
            # Update stats
            if result.get("world_reaction") and result.get("world_reaction").get("success", False):
                self.test_stats["world_reactions"] += 1
                
            # Check for ambient content
            formatted_response = result.get("formatted_response", {})
            if formatted_response and "ambient_response" in formatted_response:
                self.test_stats["ambient_content"] += 1
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _display_formatted_response(self, result: Dict[str, Any]):
        """Display the formatted response."""
        # Get basic response text
        response_text = result.get("response_text", "")
        
        # Get formatted response if available
        formatted_response = result.get("formatted_response", None)
        
        if formatted_response:
            # Display with styling
            formatted_text = formatted_response.get("formatted_response", {}).get("text", response_text)
            
            # Get output type
            output_type = formatted_response.get("formatted_response", {}).get("type", "narrative")
            
            # Different display based on output type
            if output_type == "system":
                # Display system messages in green
                print(f"\033[92m{formatted_text}\033[0m")
            elif output_type == "combat":
                # Display combat text in red and bold
                print(f"\033[1;31m{formatted_text}\033[0m")
            elif output_type == "dialogue":
                # Display dialogue in light blue and italic (using underscore as terminal might not support italic)
                print(f"\033[3;94m{formatted_text}\033[0m")
            elif output_type == "ambient":
                # Display ambient content in gray
                print(f"\033[90m{formatted_text}\033[0m")
            else:
                # Default to normal text
                print(formatted_text)
                
            # Display ambient content if available
            if "ambient_response" in formatted_response:
                ambient_text = formatted_response["ambient_response"]["formatted_response"]["text"]
                print(f"\n\033[90m{ambient_text}\033[0m")
        else:
            # No formatting, just display the text
            print(response_text)
        
        # Display metadata if available and verbose mode
        metadata = result.get("metadata", {})
        if self.verbose_mode and metadata:
            print("\n--- Response Metadata ---")
            print(f"Processing mode: {metadata.get('processing_mode', 'Unknown')}")
            print(f"Complexity: {metadata.get('complexity', 'Unknown')}")
            print(f"Processing time: {metadata.get('processing_time_total', 0):.3f}s")
            print(f"World reaction: {'Yes' if metadata.get('world_reaction_processed', False) else 'No'}")
            print(f"Pacing updated: {'Yes' if metadata.get('pacing_updated', False) else 'No'}")
            print(f"Response formatted: {'Yes' if metadata.get('response_formatted', False) else 'No'}")
    
    def _handle_test_command(self, command: str):
        """
        Handle special test commands.
        
        Args:
            command: Test command string (without the ! prefix)
        """
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "help":
            self._show_test_help()
        elif cmd == "stats":
            self._display_stats()
        elif cmd == "verbose":
            self.verbose_mode = not self.verbose_mode
            print(f"Verbose mode {'enabled' if self.verbose_mode else 'disabled'}")
        elif cmd == "context":
            self._display_context()
        elif cmd == "update":
            self._handle_context_update(args)
        elif cmd == "test":
            self._run_test_sequence(args)
        else:
            print(f"Unknown test command: {cmd}")
    
    def _show_test_help(self):
        """Show help information for test commands."""
        print("\n=== Test Commands ===")
        print("!help - Show this help information")
        print("!stats - Display test statistics")
        print("!verbose - Toggle verbose mode for metadata display")
        print("!context - Display current game context")
        print("!update <key> <value> - Update a context value")
        print("!test <scenario> - Run a test scenario (basic, dialogue, combat)")
    
    def _display_stats(self):
        """Display current test statistics."""
        print("\n=== Test Statistics ===")
        duration = datetime.now() - self.test_stats["start_time"]
        print(f"Session duration: {duration}")
        print(f"Inputs processed: {self.test_stats['inputs_processed']}")
        print(f"OOC commands: {self.test_stats['ooc_commands']}")
        print(f"World reactions: {self.test_stats['world_reactions']}")
        print(f"Ambient content: {self.test_stats['ambient_content']}")
        
        # Get AI GM system status
        system_status = self.integrated_gm.get_system_status()
        print("\n=== AI GM System Status ===")
        print(f"Extensions loaded: {', '.join(system_status['extensions'])}")
        
        # Display brain stats
        brain_stats = system_status.get("brain_stats", {})
        if brain_stats:
            print("\nBrain Processing Statistics:")
            for mode, stats in brain_stats.items():
                print(f"  {mode}: {stats['count']} ({stats['processing_time']:.3f}s total)")
    
    def _display_context(self):
        """Display the current game context."""
        context = self.integrated_gm.get_context()
        
        print("\n=== Current Game Context ===")
        print(f"Location: {context.get('current_location', 'Unknown')}")
        
        if 'active_npcs' in context:
            print("\nPresent Characters:")
            for npc in context['active_npcs']:
                print(f"- {npc}")
        
        if 'player' in context:
            player = context['player']
            print(f"\nPlayer: {player.get('name', 'Unknown')}")
            print(f"Health: {player.get('health', 0)}/{player.get('max_health', 0)}")
            
            if 'domains' in player:
                print("\nDomains:")
                for domain, value in player['domains'].items():
                    stars = "★" * value
                    print(f"  {domain}: {value} {stars}")
            
            if 'inventory' in player:
                print("\nInventory:")
                for item in player['inventory']:
                    print(f"- {item}")
    
    def _handle_context_update(self, args_str: str):
        """
        Handle context update command.
        
        Args:
            args_str: Arguments string for the update command
        """
        parts = args_str.split(maxsplit=1)
        if len(parts) < 2:
            print("Usage: !update <key> <value>")
            return
            
        key, value = parts
        
        # Handle special cases
        if key == "location":
            self.integrated_gm.update_context({"current_location": value})
            print(f"Updated location to: {value}")
        elif key == "health":
            try:
                health = int(value)
                context = self.integrated_gm.get_context()
                player = context.get('player', {}).copy()
                player['health'] = health
                self.integrated_gm.update_context({"player": player})
                print(f"Updated player health to: {health}")
            except ValueError:
                print("Health must be an integer value")
        elif key.startswith("domain."):
            domain = key.split(".", 1)[1].upper()
            try:
                domain_value = int(value)
                context = self.integrated_gm.get_context()
                player = context.get('player', {}).copy()
                domains = player.get('domains', {}).copy()
                domains[domain] = domain_value
                player['domains'] = domains
                self.integrated_gm.update_context({"player": player})
                print(f"Updated {domain} domain to: {domain_value}")
            except ValueError:
                print("Domain value must be an integer")
        else:
            print(f"Unknown context key: {key}")
    
    def _run_test_sequence(self, test_name: str):
        """
        Run a predefined test sequence.
        
        Args:
            test_name: Name of the test sequence to run
        """
        test_name = test_name.lower()
        
        if test_name == "basic":
            asyncio.create_task(self._run_basic_test())
        elif test_name == "dialogue":
            asyncio.create_task(self._run_dialogue_test())
        elif test_name == "combat":
            asyncio.create_task(self._run_combat_test())
        else:
            print(f"Unknown test sequence: {test_name}")
    
    async def _run_basic_test(self):
        """Run a basic test sequence."""
        test_inputs = [
            "look around",
            "examine the tavern",
            "talk to Galen",
            "/help",
            "/stats"
        ]
        
        print("\n=== Running Basic Test Sequence ===")
        for test_input in test_inputs:
            print(f"\n> {test_input}")
            await self._process_and_display(test_input)
            time.sleep(1)  # Add a small delay between inputs
    
    async def _run_dialogue_test(self):
        """Run a dialogue test sequence."""
        test_inputs = [
            "approach Lyra the bard",
            "ask Lyra about her music",
            "compliment Lyra's performance",
            "ask about local rumors",
            "thank Lyra and walk away"
        ]
        
        print("\n=== Running Dialogue Test Sequence ===")
        for test_input in test_inputs:
            print(f"\n> {test_input}")
            await self._process_and_display(test_input)
            time.sleep(1.5)  # Add a small delay between inputs
    
    async def _run_combat_test(self):
        """Run a combat test sequence."""
        # First update context to put player in a dangerous location
        self.integrated_gm.update_context({
            "current_location": "Dark Alley",
            "location_description": "A narrow, dimly lit alley between buildings. The perfect place for an ambush.",
            "active_npcs": ["Suspicious Thug", "Hooded Figure"],
            "combat_enabled": True
        })
        
        test_inputs = [
            "look around carefully",
            "approach cautiously",
            "draw my sword",
            "attack the thug",
            "dodge and counter-attack",
            "finish the fight"
        ]
        
        print("\n=== Running Combat Test Sequence ===")
        for test_input in test_inputs:
            print(f"\n> {test_input}")
            await self._process_and_display(test_input)
            time.sleep(2)  # Add a slightly longer delay for combat
    
    def _display_welcome(self):
        """Display welcome message."""
        print("\n" + "=" * 60)
        print("AI GM BRAIN - INTEGRATED SYSTEM TEST CONSOLE".center(60))
        print("=" * 60)
        print("Type your input to interact with the AI GM.")
        print("Use /commands for out-of-character actions.")
        print("Use !commands for test functions (try !help)")
        print("Type 'quit' or 'exit' to end the session.")
        print("=" * 60)
        
        # Start with verbose mode off
        self.verbose_mode = False


def main():
    """Main function to run the test console."""
    tester = AIGMTester()
    
    try:
        # Run the interactive console
        asyncio.run(tester.run_interactive_console())
    except Exception as e:
        print(f"Error in test console: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()