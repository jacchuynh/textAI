"""
AI GM Brain - OOC Command Handler

This module provides specialized handling for Out-of-Character (OOC) commands
that allow players to interact with game systems directly without roleplaying.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Import from core brain
from .ai_gm_brain import AIGMBrain


class OOCCommandHandler:
    """
    Handler for Out-of-Character (OOC) commands to access system functionality.
    
    OOC commands provide direct access to game information and systems outside
    of the narrative context, using a /ooc prefix.
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the OOC command handler.
        
        Args:
            ai_gm_brain: Reference to the parent AI GM Brain
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"OOCHandler_{ai_gm_brain.game_id}")
        
        # Command registry
        self.commands = {
            'help': self._cmd_help,
            'stats': self._cmd_stats,
            'inventory': self._cmd_inventory,
            'quests': self._cmd_quests,
            'location': self._cmd_location,
            'time': self._cmd_game_time,
            'domains': self._cmd_domains,
            'combat': self._cmd_combat_info,
            'npc': self._cmd_npc_info,
            'system': self._cmd_system_info,
            'memory': self._cmd_memory_info
        }
        
    def process_command(self, command_text: str) -> Dict[str, Any]:
        """
        Process an OOC command from the full input (including slash prefix).
        This method is called by the AI GM Brain to handle OOC commands.
        
        Args:
            command_text: The complete command text (e.g., "/stats")
            
        Returns:
            A response dictionary for the AI GM Brain
        """
        # Remove the slash prefix
        if command_text.startswith('/'):
            command_text = command_text[1:]
            
        # Process with the handler
        result = self.handle_command(command_text)
        
        # Format for AI GM Brain
        return {
            "response": result['response_text'],
            "status": "success",
            "ooc_command": True,
            "requires_llm": False,
            "command": command_text.split()[0] if command_text else ""
        }
    
    def handle_command(self, command_str: str) -> Dict[str, Any]:
        """
        Process an OOC command and return a response.
        
        Args:
            command_str: The command string without the '/ooc' prefix
            
        Returns:
            Response data dictionary
        """
        start_time = time.time()
        command_str = command_str.strip()
        
        # Parse the command
        parts = command_str.split(maxsplit=1)
        cmd = parts[0].lower() if parts else ''
        args = parts[1] if len(parts) > 1 else ''
        
        # Check for empty command
        if not cmd:
            return self._generate_response(
                "Available commands: " + ", ".join(self.commands.keys()) + "\nUse '/ooc help' for more information.",
                start_time
            )
        
        # Execute the command if it exists
        if cmd in self.commands:
            # Get the command function (we're now keeping function references directly)
            command_func = self.commands[cmd]
            # Check if it's a function or a dictionary
            if callable(command_func):
                return command_func(args, start_time)
            elif isinstance(command_func, dict) and "handler" in command_func:
                # If it's a dictionary with a handler, call the handler
                handler = command_func["handler"]
                if callable(handler):
                    # For handlers that expect a different format (from test scripts)
                    try:
                        return handler({"text": args}, self.ai_gm_brain)
                    except Exception:
                        try:
                            # Fall back to original format
                            return handler(args, start_time)
                        except Exception as e:
                            return self._generate_response(f"Error executing command: {str(e)}", start_time)
                else:
                    return self._generate_response(f"Invalid handler for command: {cmd}", start_time)
            else:
                return self._generate_response(f"Invalid command format: {cmd}", start_time)
            
        # Unknown command
        return self._generate_response(
            f"Unknown command: '{cmd}'. Type '/ooc help' for available commands.",
            start_time
        )
    
    def _generate_response(self, message: str, start_time: float) -> Dict[str, Any]:
        """
        Generate a standard OOC response.
        
        Args:
            message: Response message text
            start_time: Processing start time for metrics
            
        Returns:
            Response data dictionary
        """
        return {
            'response_text': f"(OOC) {message}",
            'ooc_response': True,
            'requires_llm': False,
            'processing_time': time.time() - start_time
        }
    
    # Command implementations
    
    def _cmd_help(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'help' command."""
        if args:
            # Help for a specific command
            cmd = args.split()[0].lower()
            if cmd in self.commands:
                help_text = self._get_command_help(cmd)
                return self._generate_response(help_text, start_time)
            return self._generate_response(f"Unknown command: '{cmd}'", start_time)
        
        # General help
        help_text = """Available commands:
- help [command]: Show help for all commands or a specific command
- stats: Show character statistics and domain levels
- inventory: Show your inventory
- quests: Show active and completed quests
- location: Show information about your current location
- time: Show current game time and date
- domains: Show information about your domain progression
- combat: Show combat-related information and stats
- npc [name]: Show information about a specific NPC or nearby NPCs
- system: Show system information and statistics
- memory: Show memory usage statistics
"""
        return self._generate_response(help_text, start_time)
    
    def _cmd_stats(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'stats' command."""
        # This would connect to the character system to retrieve actual stats
        # For now, we'll return a placeholder
        stats_text = """Your Character Statistics:
- Level: [level]
- Health: [current]/[max]
- Experience: [current]/[needed for next level]

Domains:
- BODY: [level] ([progress]%)
- MIND: [level] ([progress]%)
- SPIRIT: [level] ([progress]%)
- SOCIAL: [level] ([progress]%)
- CRAFT: [level] ([progress]%)
- AUTHORITY: [level] ([progress]%)
- AWARENESS: [level] ([progress]%)

Active Effects:
- [effect1]: [duration]
- [effect2]: [duration]
"""
        return self._generate_response(stats_text, start_time)
    
    def _cmd_inventory(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'inventory' command."""
        # This would connect to the inventory system
        # For now, we'll return a placeholder
        inventory_text = """Your Inventory:
- [item1] (x[quantity]) - [description]
- [item2] (x[quantity]) - [description]
- [item3] (x[quantity]) - [description]

Equipment:
- Head: [equipped_item]
- Body: [equipped_item]
- Hands: [equipped_item]
- Feet: [equipped_item]
- Weapon: [equipped_item]

Carrying: [current_weight]/[max_weight] weight units
"""
        return self._generate_response(inventory_text, start_time)
    
    def _cmd_quests(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'quests' command."""
        # This would connect to the quest system
        # For now, we'll return a placeholder
        quests_text = """Active Quests:
- [quest1_name]: [objective] ([progress]%)
  - Current step: [current_step]
- [quest2_name]: [objective] ([progress]%)
  - Current step: [current_step]

Recently Completed:
- [completed_quest1]: Completed on [date]
- [completed_quest2]: Completed on [date]
"""
        return self._generate_response(quests_text, start_time)
    
    def _cmd_location(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'location' command."""
        # This would connect to the location system
        # For now, we'll return a placeholder based on current_location
        location_id = self.ai_gm_brain.current_location or "unknown"
        location_text = f"""Current Location: [{location_id}]
Description: [location_description]

Nearby NPCs:
- [npc1_name]: [brief_description]
- [npc2_name]: [brief_description]

Available Exits:
- North: [destination]
- East: [destination]
- South: [destination]
- West: [destination]
"""
        return self._generate_response(location_text, start_time)
    
    def _cmd_game_time(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'time' command."""
        # This would connect to the game time system
        # For now, we'll use real time as a placeholder
        current_time = datetime.utcnow()
        time_text = f"""Game Time:
Date: [in-game date]
Time: [in-game time]

Real Time:
{current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
Session Duration: [hours:minutes:seconds]
"""
        return self._generate_response(time_text, start_time)
    
    def _cmd_domains(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'domains' command."""
        # This would connect to the domain progression system
        # For now, we'll return a placeholder
        domains_text = """Domain Progression:
- BODY: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]
  
- MIND: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]
  
- SPIRIT: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]
  
- SOCIAL: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]
  
- CRAFT: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]
  
- AUTHORITY: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]
  
- AWARENESS: Level [level] ([entries]/[needed] entries)
  Next milestone: [milestone_description]

Growth tiers: Novice (0-2), Skilled (3-4), Expert (5-7), Master (8-9), Paragon (10+)
"""
        return self._generate_response(domains_text, start_time)
    
    def _cmd_combat_info(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'combat' command."""
        # This would connect to the combat system
        # For now, we'll return a placeholder
        combat_text = """Combat Information:
Combat Style: [style]
Preferred Moves: [moves]

Recent Combat:
- [opponent]: [result] ([date])
- [opponent]: [result] ([date])

Combat Statistics:
- Victories: [count]
- Defeats: [count]
- Draws: [count]
- Damage Dealt: [amount]
- Damage Taken: [amount]
"""
        return self._generate_response(combat_text, start_time)
    
    def _cmd_npc_info(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'npc' command."""
        # This would connect to the NPC system
        # If args is provided, show info for that specific NPC
        # Otherwise show info about nearby NPCs
        if args:
            npc_name = args.strip()
            npc_text = f"""Information about {npc_name}:
Relationship: [relationship_status]
Disposition: [disposition] ([value]/100)
Notable Interactions:
- [interaction1] ([date])
- [interaction2] ([date])

Known Information:
- [fact1]
- [fact2]
"""
        else:
            npc_text = """Nearby NPCs:
- [npc1_name]: [relationship] - [brief_description]
- [npc2_name]: [relationship] - [brief_description]

Recent NPC Interactions:
- [npc3_name]: [interaction] ([time_ago])
- [npc4_name]: [interaction] ([time_ago])
"""
        return self._generate_response(npc_text, start_time)
    
    def _cmd_system_info(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'system' command."""
        # Get stats from the AI GM Brain
        stats = self.ai_gm_brain.get_processing_statistics()
        
        system_text = f"""System Information:
Total Interactions: {stats['total_interactions']}
Current Processing Mode: {stats['current_mode']}
Active Conversations: {stats['active_conversations']}
Current Location: {stats['current_location'] or 'Unknown'}
Last LLM Interaction: {stats['last_llm_interaction'] or 'None'}

Processing Statistics:
- Mechanical Responses: [count] ([percentage]%)
- Narrative Responses: [count] ([percentage]%)
- Interpretive Responses: [count] ([percentage]%)
- Error Responses: [count] ([percentage]%)

Memory Usage:
- Short-term Memories: [count]
- Medium-term Memories: [count]
- Long-term Memories: [count]
"""
        return self._generate_response(system_text, start_time)
    
    def _cmd_memory_info(self, args: str, start_time: float) -> Dict[str, Any]:
        """Handle the 'memory' command."""
        # This would connect to the memory system
        # For now, we'll return a placeholder
        memory_text = """Memory System Information:
Recent Memories:
- [memory1] (Importance: [level]) ([time_ago])
- [memory2] (Importance: [level]) ([time_ago])
- [memory3] (Importance: [level]) ([time_ago])

Memory Stats:
- Short-term Memories: [count] ([capacity]%)
- Medium-term Memories: [count] ([capacity]%)
- Long-term Memories: [count] ([capacity]%)
- Total Memory Entries: [count]
"""
        return self._generate_response(memory_text, start_time)
    
    def _get_command_help(self, command: str) -> str:
        """Get detailed help for a specific command."""
        help_texts = {
            'help': "help [command] - Show help for all commands or a specific command",
            'stats': "stats - Show your character's statistics, including health, domains, and active effects",
            'inventory': "inventory - Show your inventory contents, equipped items, and carrying capacity",
            'quests': "quests - Show active quests and their progress, as well as recently completed quests",
            'location': "location - Show information about your current location, nearby NPCs, and available exits",
            'time': "time - Show the current game time and date, as well as real-time session information",
            'domains': "domains - Show detailed information about your domain progression and next milestones",
            'combat': "combat - Show combat statistics, recent combat encounters, and your combat style",
            'npc': "npc [name] - Show information about a specific NPC (if name is provided) or nearby NPCs",
            'system': "system - Show system information and statistics about the game's operation",
            'memory': "memory - Show information about the game's memory system and recent memories"
        }
        
        return help_texts.get(command, f"No detailed help available for '{command}'")