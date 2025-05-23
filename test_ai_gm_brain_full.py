"""
AI GM Brain - Complete System Test

This script demonstrates the full AI GM Brain system with all components working together.
It provides an interactive console that allows for testing various aspects of the system.
"""

import sys
import time
import random
import argparse
from typing import Dict, Any
from backend.src.ai_gm.ai_gm_brain_full import get_ai_gm_brain_full


class AIGMBrainTester:
    """Test harness for the complete AI GM Brain system."""
    
    def __init__(self, game_id: str = "test_game", player_id: str = "test_player"):
        """
        Initialize the AI GM Brain tester.
        
        Args:
            game_id: Game session ID to use
            player_id: Player ID to use
        """
        print(f"Initializing AI GM Brain for game {game_id} and player {player_id}...")
        self.ai_gm = get_ai_gm_brain_full(game_id, player_id)
        self.in_combat = False
        
        # Sample monster IDs for testing
        self.sample_monsters = ["wolf", "goblin", "troll", "dragon", "bandit"]
        
        # Sample locations for testing
        self.sample_locations = ["forest", "mountain", "cave", "village", "city", "dungeon"]
        
        # Debug mode flag
        self.debug_mode = False
    
    def run_interactive_console(self):
        """Run an interactive console for testing the AI GM Brain."""
        print("\n===== AI GM Brain Interactive Test Console =====")
        print("Type 'exit' to quit.")
        print("Type 'help' to see available commands.")
        print("Type 'debug' to toggle debug mode.")
        print("================================================\n")
        
        while True:
            try:
                # Get input
                user_input = input("\nEnter your command or message: ")
                
                # Check for exit
                if user_input.lower() == 'exit':
                    print("Exiting test console.")
                    break
                
                # Check for help
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                # Check for debug mode toggle
                if user_input.lower() == 'debug':
                    self.debug_mode = not self.debug_mode
                    print(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}.")
                    continue
                
                # Check for special test commands
                if user_input.startswith('!'):
                    self._handle_test_command(user_input[1:])
                    continue
                
                # Process regular input
                start_time = time.time()
                response = self.ai_gm.process_input(user_input)
                processing_time = time.time() - start_time
                
                # Print response
                print("\nAI GM: " + response["response_text"])
                print(f"[Processed in {processing_time:.3f}s]")
                
                # Print additional information in debug mode
                if self.debug_mode:
                    print("\nResponse Metadata:")
                    for key, value in response.get("metadata", {}).items():
                        print(f"- {key}: {value}")
                    
                    # Check for combat state change
                    if response.get("combat_started", False):
                        self.in_combat = True
                        print("\n[Debug] Combat started!")
                    
                    if response.get("combat_ended", False):
                        self.in_combat = False
                        print("\n[Debug] Combat ended!")
            
            except KeyboardInterrupt:
                print("\nExiting test console.")
                break
            
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
Available Commands:
------------------
exit - Exit the test console
help - Show this help information
debug - Toggle debug mode

Special Test Commands:
--------------------
!stats - Show AI GM Brain statistics
!combat [monster] - Start combat with a monster (random if not specified)
!end_combat [result] - End current combat (result: victory, defeat, flee)
!describe [location] - Generate a location description (random if not specified)
!dialogue [disposition] - Generate NPC dialogue with specified disposition
!tension [amount] - Adjust narrative tension by amount (-1.0 to 1.0)
!decision - Make a narrative direction decision

Regular Commands:
---------------
Standard text input will be processed through the AI GM Brain
/ooc [command] - Out-of-character commands (try '/ooc help')
"""
        print(help_text)
    
    def _handle_test_command(self, command: str):
        """
        Handle special test commands.
        
        Args:
            command: Test command string
        """
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == 'stats':
            self._show_stats()
        
        elif cmd == 'combat':
            monster = args if args else random.choice(self.sample_monsters)
            self._start_combat(monster)
        
        elif cmd == 'end_combat':
            result = args if args in ['victory', 'defeat', 'flee'] else 'victory'
            self._end_combat(result)
        
        elif cmd == 'describe':
            location = args if args else random.choice(self.sample_locations)
            self._describe_location(location)
        
        elif cmd == 'dialogue':
            disposition = args if args in ['friendly', 'hostile', 'neutral', 'fearful', 'mysterious'] else 'neutral'
            self._generate_dialogue(disposition)
        
        elif cmd == 'tension':
            try:
                amount = float(args) if args else 0.2
                self._adjust_tension(amount)
            except ValueError:
                print("Error: Tension adjustment must be a number")
        
        elif cmd == 'decision':
            self._make_decision()
        
        else:
            print(f"Unknown test command: {cmd}")
    
    def _show_stats(self):
        """Show AI GM Brain statistics."""
        stats = self.ai_gm.get_statistics()
        
        print("\nAI GM Brain Statistics:")
        print("======================")
        
        # Core stats
        print("\nCore Statistics:")
        for key, value in stats.get("core", {}).items():
            print(f"- {key}: {value}")
        
        # Component availability
        print("\nComponents Available:")
        for comp, available in stats.get("components", {}).items():
            print(f"- {comp}: {'Yes' if available else 'No'}")
        
        # LLM stats if available
        if "llm" in stats:
            print("\nLLM Statistics:")
            for key, value in stats.get("llm", {}).items():
                print(f"- {key}: {value}")
    
    def _start_combat(self, monster: str):
        """Start combat with a monster."""
        print(f"Starting combat with {monster}...")
        response = self.ai_gm.start_combat(monster)
        
        if response.get("error", False):
            print(f"Error: {response.get('response_text', 'Unknown error')}")
            return
        
        print("\nAI GM: " + response["response_text"])
        
        if self.debug_mode:
            print("\nCombat Details:")
            print(f"- Monster: {response.get('monster_name', 'Unknown')}")
            print(f"- Monster Health: {response.get('monster_health', 0)}")
            print(f"- Player Health: {response.get('player_health', 0)}")
            print(f"- Available Moves: {', '.join(response.get('available_moves', []))}")
        
        self.in_combat = True
    
    def _end_combat(self, result: str):
        """End current combat with specified result."""
        if not self.in_combat:
            print("Error: Not currently in combat")
            return
        
        print(f"Ending combat with result: {result}...")
        response = self.ai_gm.end_combat(result)
        
        if response.get("error", False):
            print(f"Error: {response.get('response_text', 'Unknown error')}")
            return
        
        print("\nAI GM: " + response["response_text"])
        self.in_combat = False
    
    def _describe_location(self, location: str):
        """Generate a description for a location."""
        print(f"Generating description for {location}...")
        
        # Add some random details for variety
        details = {
            "detail": random.choice([
                "A sense of ancient history permeates the area.",
                "The atmosphere feels charged with unseen energy.",
                "There's a peculiar stillness about this place.",
                "Signs of recent activity are evident."
            ]),
            "light_source": random.choice([
                "flickering torches",
                "shafts of sunlight",
                "glowing fungi",
                "magical illumination"
            ])
        }
        
        description = self.ai_gm.generate_location_description(location, details)
        print("\nLocation Description:")
        print(description)
    
    def _generate_dialogue(self, disposition: str):
        """Generate NPC dialogue with specified disposition."""
        print(f"Generating {disposition} NPC dialogue...")
        
        # Random NPC names and dialogue content for testing
        npc_names = ["Gareth", "Elara", "Torvald", "Lysandra", "Krug"]
        
        dialogue_content = {
            "friendly": [
                "Good to see a fresh face around here! Can I help you with anything?",
                "Welcome, traveler! You look like you could use a hot meal and a place to rest.",
                "Ah, perfect timing! I was just looking for someone to help me with a small matter."
            ],
            "hostile": [
                "I don't like the look of you. Best move along before there's trouble.",
                "Another outsider? Haven't you people done enough damage already?",
                "Stay where you are! One more step and you'll regret it."
            ],
            "neutral": [
                "Yes? What do you want?",
                "I suppose you're here about the notice. Everyone is these days.",
                "Hmm, you're not from around here. State your business."
            ],
            "fearful": [
                "Please, don't hurt me! I've done nothing wrong!",
                "Keep your voice down! They might hear us talking...",
                "I-I shouldn't be seen with you. There are eyes everywhere."
            ],
            "mysterious": [
                "The shadows whisper of your coming. I've been waiting.",
                "Fate has interesting ways of bringing souls together, wouldn't you agree?",
                "You seek answers, but are you prepared for the truth they reveal?"
            ]
        }
        
        npc_name = random.choice(npc_names)
        content = random.choice(dialogue_content.get(disposition, dialogue_content["neutral"]))
        
        dialogue = self.ai_gm.generate_npc_dialogue(npc_name, disposition, content)
        print("\nNPC Dialogue:")
        print(dialogue)
    
    def _adjust_tension(self, amount: float):
        """Adjust narrative tension level."""
        print(f"Adjusting narrative tension by {amount}...")
        self.ai_gm.adjust_narrative_tension(amount)
        print("Tension adjusted!")
    
    def _make_decision(self):
        """Make a narrative direction decision."""
        print("Making narrative direction decision...")
        
        # Sample context for decision making
        context = {
            "tension": random.uniform(0.3, 0.8),
            "location": random.choice(self.sample_locations),
            "recent_events": [
                "LOCATION_ENTERED",
                "NPC_INTERACTION",
                "ITEM_FOUND"
            ]
        }
        
        decision = self.ai_gm.make_narrative_decision(context)
        
        if decision.get("error", False):
            print(f"Error: {decision.get('response_text', 'Unknown error')}")
            return
        
        print("\nDecision Result:")
        print(f"Selected: {decision['selected']}")
        print(f"Confidence: {decision['confidence']:.2f}")
        print("\nAll Choices:")
        for choice, weight in sorted(decision['choices'].items(), key=lambda x: x[1], reverse=True):
            print(f"- {choice}: {weight:.2f}")


def main():
    """Main function to run the test console."""
    parser = argparse.ArgumentParser(description="Test the AI GM Brain system")
    parser.add_argument("--game", default="test_game", help="Game ID to use")
    parser.add_argument("--player", default="test_player", help="Player ID to use")
    args = parser.parse_args()
    
    tester = AIGMBrainTester(args.game, args.player)
    tester.run_interactive_console()


if __name__ == "__main__":
    main()