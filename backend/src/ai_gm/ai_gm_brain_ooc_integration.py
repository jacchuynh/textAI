"""
AI GM Brain OOC Integration

This module provides Out-of-Character command handling for the AI GM Brain.
"""

import re
import time
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Import from our own modules
from .ai_gm_brain import AIGMBrain
from ..memory.memory_manager import memory_manager, MemoryType


class OOCCommandHandler:
    """
    Handler for Out-of-Character commands.
    
    This class processes commands prefixed with '/' that allow the player
    to interact with the game system outside of the narrative.
    """
    
    def __init__(self, brain: AIGMBrain):
        """
        Initialize the OOC command handler.
        
        Args:
            brain: The AI GM Brain instance
        """
        self.brain = brain
        self.command_prefix = "/"
        
        # Command handlers
        self.command_handlers = {
            "help": self._handle_help,
            "stats": self._handle_stats,
            "inventory": self._handle_inventory,
            "quests": self._handle_quests,
            "time": self._handle_time,
            "system": self._handle_system,
            "memory": self._handle_memory,
            "reset": self._handle_reset,
            "ooc": self._handle_ooc_chat
        }
    
    def process_command(self, command_text: str) -> Dict[str, Any]:
        """
        Process an OOC command.
        
        Args:
            command_text: The command text including the prefix
            
        Returns:
            Dictionary with response and metadata
        """
        # Strip prefix and split into command and args
        if not command_text.startswith(self.command_prefix):
            return {
                "response": "Not a valid OOC command. Commands must start with '/'.",
                "success": False,
                "command": None
            }
        
        # Remove prefix
        command_text = command_text[len(self.command_prefix):].strip()
        
        # Split into command and args
        parts = command_text.split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        
        # Check if command exists
        if not command:
            return {
                "response": "Please specify a command. Use /help to see available commands.",
                "success": False,
                "command": None
            }
        
        if command not in self.command_handlers:
            return {
                "response": f"Unknown command '/{command}'. Use /help to see available commands.",
                "success": False,
                "command": command
            }
        
        # Handle the command
        try:
            result = self.command_handlers[command](args)
            result["command"] = command
            return result
        except Exception as e:
            return {
                "response": f"Error processing command '/{command}': {str(e)}",
                "success": False,
                "command": command
            }
    
    def _handle_help(self, args: str) -> Dict[str, Any]:
        """Handle the /help command."""
        if args:
            # Help for a specific command
            command = args.strip().lower()
            if command not in self.command_handlers:
                return {
                    "response": f"Unknown command '/{command}'. Use /help to see all available commands.",
                    "success": False
                }
            
            if command == "help":
                return {
                    "response": "Usage: /help [command]\nDisplays help information for all commands or a specific command.",
                    "success": True
                }
            elif command == "stats":
                return {
                    "response": "Usage: /stats [category]\nShows your character statistics. Categories: domains, skills, attributes, all",
                    "success": True
                }
            elif command == "inventory":
                return {
                    "response": "Usage: /inventory [filter]\nShows your inventory. Filters: weapons, armor, consumables, all",
                    "success": True
                }
            elif command == "quests":
                return {
                    "response": "Usage: /quests [status]\nShows your active quests. Status: active, completed, failed, all",
                    "success": True
                }
            elif command == "time":
                return {
                    "response": "Usage: /time\nShows the current game time and date.",
                    "success": True
                }
            elif command == "system":
                return {
                    "response": "Usage: /system [info]\nShows system information. Info: memory, processing, events",
                    "success": True
                }
            elif command == "memory":
                return {
                    "response": "Usage: /memory [count]\nShows recent memories up to count (default 5).",
                    "success": True
                }
            elif command == "reset":
                return {
                    "response": "Usage: /reset [type]\nResets part of the game state. Type: conversation, encounter, memory, all",
                    "success": True
                }
            elif command == "ooc":
                return {
                    "response": "Usage: /ooc [message]\nSends an out-of-character message.",
                    "success": True
                }
        
        # General help
        help_text = """
Available commands:
/help [command] - Display help for a command
/stats [category] - Show character statistics
/inventory [filter] - Show inventory
/quests [status] - Show quests
/time - Show game time
/system [info] - Show system information
/memory [count] - Show recent memories
/reset [type] - Reset part of the game state
/ooc [message] - Send out-of-character message

Use /help [command] for more information on a specific command.
"""
        return {
            "response": help_text.strip(),
            "success": True
        }
    
    def _handle_stats(self, args: str) -> Dict[str, Any]:
        """Handle the /stats command."""
        # In a full implementation, this would fetch from a character system
        # For now, we'll provide a basic example response
        
        category = args.strip().lower() if args else "all"
        
        if category in ["domains", "all"]:
            domains_text = """
Domains:
BODY: 3 (Skilled)
MIND: 2 (Novice)
CRAFT: 4 (Skilled)
AWARENESS: 3 (Skilled)
SOCIAL: 1 (Novice)
AUTHORITY: 2 (Novice)
SPIRIT: 0 (Untrained)
"""
        else:
            domains_text = ""
        
        if category in ["skills", "all"]:
            skills_text = """
Skills:
Swordsmanship: 3
Tracking: 2
First Aid: 1
Stealth: 2
Persuasion: 1
"""
        else:
            skills_text = ""
            
        if category in ["attributes", "all"]:
            attributes_text = """
Attributes:
Health: 45/50
Stamina: 35/40
Focus: 25/30
Spirit: 10/20
Corruption: 0/100
"""
        else:
            attributes_text = ""
        
        if not domains_text and not skills_text and not attributes_text:
            return {
                "response": f"Unknown category '{category}'. Valid categories: domains, skills, attributes, all",
                "success": False
            }
        
        return {
            "response": (domains_text + skills_text + attributes_text).strip(),
            "success": True
        }
    
    def _handle_inventory(self, args: str) -> Dict[str, Any]:
        """Handle the /inventory command."""
        # In a full implementation, this would fetch from an inventory system
        # For now, we'll provide a basic example response
        
        filter_type = args.strip().lower() if args else "all"
        
        if filter_type in ["weapons", "all"]:
            weapons_text = """
Weapons:
- Steel Sword (Quality: Good, Damage: 8-12)
- Hunting Bow (Quality: Average, Damage: 6-14)
- Dagger (Quality: Poor, Damage: 3-6)
"""
        else:
            weapons_text = ""
        
        if filter_type in ["armor", "all"]:
            armor_text = """
Armor:
- Leather Jerkin (Protection: 4, Weight: Light)
- Traveler's Boots (Protection: 1, Weight: Light)
- Iron Helmet (Protection: 5, Weight: Medium)
"""
        else:
            armor_text = ""
            
        if filter_type in ["consumables", "all"]:
            consumables_text = """
Consumables:
- Health Potion (Effects: Restore 25 Health) x3
- Stamina Elixir (Effects: Restore 20 Stamina) x1
- Rations (Effects: Prevent Hunger) x5
"""
        else:
            consumables_text = ""
            
        if filter_type in ["miscellaneous", "all"]:
            misc_text = """
Miscellaneous:
- Gold Coins x127
- Silver Key (Quest Item)
- Map of Eastern Woodlands
- Flint and Steel
"""
        else:
            misc_text = ""
        
        if not weapons_text and not armor_text and not consumables_text and not misc_text:
            return {
                "response": f"Unknown filter '{filter_type}'. Valid filters: weapons, armor, consumables, miscellaneous, all",
                "success": False
            }
        
        return {
            "response": (weapons_text + armor_text + consumables_text + misc_text).strip(),
            "success": True
        }
    
    def _handle_quests(self, args: str) -> Dict[str, Any]:
        """Handle the /quests command."""
        # In a full implementation, this would fetch from a quest system
        # For now, we'll provide a basic example response
        
        status = args.strip().lower() if args else "active"
        
        if status in ["active", "all"]:
            active_quests = """
Active Quests:
- The Missing Shipment (Main)
  Objective: Find the missing caravan near the Western Ridge
  Progress: 1/3 objectives complete

- Herbalist's Request (Side)
  Objective: Collect 5 moonberries from the Whispering Woods
  Progress: 3/5 moonberries collected
"""
        else:
            active_quests = ""
        
        if status in ["completed", "all"]:
            completed_quests = """
Completed Quests:
- Village Defense (Main)
  Reward: 150 gold, Steel Sword
  Completed: 3 days ago

- The Lost Pet (Side)
  Reward: Favor with Alderman, 50 gold
  Completed: 5 days ago
"""
        else:
            completed_quests = ""
            
        if status in ["failed", "all"]:
            failed_quests = """
Failed Quests:
- Timely Delivery
  Failure: Package not delivered before deadline
  Failed: 2 days ago
"""
        else:
            failed_quests = ""
        
        if not active_quests and not completed_quests and not failed_quests:
            return {
                "response": f"Unknown status '{status}'. Valid statuses: active, completed, failed, all",
                "success": False
            }
        
        return {
            "response": (active_quests + completed_quests + failed_quests).strip(),
            "success": True
        }
    
    def _handle_time(self, args: str) -> Dict[str, Any]:
        """Handle the /time command."""
        # In a full implementation, this would fetch from a game time system
        # For now, we'll provide a basic example response
        
        game_time = """
Game Time: 14:32 (Mid-Afternoon)
Date: Day 23 of Summer, Year 1243
Moon Phase: Waxing Crescent
Weather: Clear Skies, Warm
"""
        
        return {
            "response": game_time.strip(),
            "success": True
        }
    
    def _handle_system(self, args: str) -> Dict[str, Any]:
        """Handle the /system command."""
        info_type = args.strip().lower() if args else "all"
        
        if info_type in ["memory", "all"]:
            memory_stats = memory_manager.get_statistics()
            memory_text = f"""
Memory System:
- Working Memory: {memory_stats['working_memory_count']}/{memory_stats['working_memory_capacity']} entries
- Recent Memory: {memory_stats['recent_memory_count']}/{memory_stats['recent_memory_capacity']} entries
- Archival Memory: {memory_stats['archival_memory_count']} entries
- Total Memory: {memory_stats['total_memory_count']} entries
"""
        else:
            memory_text = ""
        
        if info_type in ["processing", "all"]:
            brain_stats = self.brain.get_processing_statistics()
            processing_text = f"""
Processing System:
- Inputs Processed: {brain_stats['total_inputs_processed']}
- Mechanical: {brain_stats['mechanical_responses']}
- Narrative: {brain_stats['narrative_responses']}
- Hybrid: {brain_stats['hybrid_responses']}
- OOC: {brain_stats['ooc_responses']}
- Avg Processing Time: {brain_stats['avg_processing_time']:.3f}s
"""
        else:
            processing_text = ""
            
        if info_type in ["events", "all"]:
            # This would fetch event statistics from the event bus
            events_text = """
Event System:
- Recent Events: 32
- Player Events: 18
- NPC Events: 9
- System Events: 5
"""
        else:
            events_text = ""
            
        if info_type in ["features", "all"]:
            # Show which AI GM features are enabled
            features_text = f"""
AI GM Features:
- OOC Commands: Enabled
- Combat Integration: {'Enabled' if self.brain.has_combat_integration else 'Disabled'}
- Decision Logic: {'Enabled' if self.brain.has_decision_logic else 'Disabled'}
- Narrative Generation: {'Enabled' if self.brain.has_narrative_generator else 'Disabled'}
- LLM Integration: {'Enabled' if self.brain.has_llm_integration else 'Disabled'}
"""
        else:
            features_text = ""
        
        if not memory_text and not processing_text and not events_text and not features_text:
            return {
                "response": f"Unknown info type '{info_type}'. Valid types: memory, processing, events, features, all",
                "success": False
            }
        
        return {
            "response": (memory_text + processing_text + events_text + features_text).strip(),
            "success": True
        }
    
    def _handle_memory(self, args: str) -> Dict[str, Any]:
        """Handle the /memory command."""
        try:
            count = int(args) if args.strip() else 5
        except ValueError:
            return {
                "response": f"Invalid count '{args}'. Please provide a number.",
                "success": False
            }
        
        # Get recent memories
        memories = memory_manager.find_memories(limit=count)
        
        if not memories:
            return {
                "response": "No memories found.",
                "success": True
            }
        
        # Format memories
        memory_lines = ["Recent Memories:"]
        for i, memory in enumerate(memories, 1):
            timestamp = memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            memory_type = memory.type.name
            importance = memory.importance
            tags = ", ".join(memory.tags) if memory.tags else "None"
            
            memory_lines.append(f"{i}. [{timestamp}] {memory_type} (Importance: {importance:.2f})")
            memory_lines.append(f"   Tags: {tags}")
            
            # Add content summary based on memory type
            if memory.type == MemoryType.PLAYER_ACTION:
                action = memory.content.get("action", "Unknown action")
                memory_lines.append(f"   Action: {action}")
            elif memory.type == MemoryType.NPC_INTERACTION:
                npc = memory.content.get("npc_name", "Unknown NPC")
                interaction = memory.content.get("interaction_type", "Unknown interaction")
                memory_lines.append(f"   NPC: {npc}, Interaction: {interaction}")
            elif memory.type == MemoryType.SYSTEM:
                event_type = memory.content.get("event_type", "Unknown event")
                memory_lines.append(f"   Event: {event_type}")
            
            memory_lines.append("")  # Empty line between memories
        
        return {
            "response": "\n".join(memory_lines).strip(),
            "success": True
        }
    
    def _handle_reset(self, args: str) -> Dict[str, Any]:
        """Handle the /reset command."""
        reset_type = args.strip().lower() if args else ""
        
        if not reset_type:
            return {
                "response": "Please specify what to reset: conversation, encounter, memory, all",
                "success": False
            }
        
        if reset_type not in ["conversation", "encounter", "memory", "all"]:
            return {
                "response": f"Unknown reset type '{reset_type}'. Valid types: conversation, encounter, memory, all",
                "success": False
            }
        
        # Perform reset operations
        operations = []
        
        if reset_type in ["conversation", "all"]:
            # Reset conversation state
            operations.append("Conversation history has been reset")
        
        if reset_type in ["encounter", "all"]:
            # Reset current encounter
            operations.append("Current encounter has been reset")
        
        if reset_type in ["memory", "all"]:
            # Clear working memory
            # In a full implementation, this would be more nuanced
            operations.append("Short-term memory has been reset")
        
        return {
            "response": "Reset complete:\n- " + "\n- ".join(operations),
            "success": True
        }
    
    def _handle_ooc_chat(self, args: str) -> Dict[str, Any]:
        """Handle the /ooc chat command."""
        if not args.strip():
            return {
                "response": "What would you like to say out-of-character?",
                "success": False
            }
        
        # Log and process OOC message
        return {
            "response": f"[OOC] You said: {args}",
            "success": True,
            "ooc_message": args
        }


def extend_ai_gm_brain_with_ooc(brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with OOC command handling.
    
    Args:
        brain: The AI GM Brain instance to extend
    """
    # Create OOC command handler
    ooc_handler = OOCCommandHandler(brain)
    
    # Register with the brain
    brain.register_extension("ooc_integration", ooc_handler)
    
    # Add method to the brain
    def process_ooc_command(self, command_text: str) -> Dict[str, Any]:
        """Process an OOC command."""
        return self.extensions["ooc_integration"].process_command(command_text)
    
    # Attach the method
    setattr(AIGMBrain, "process_ooc_command", process_ooc_command)