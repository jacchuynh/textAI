"""
AI GM Brain Server Implementation
Custom implementation for the advanced AI GM server.
"""

import logging
import time
import random
from typing import Dict, Any, List, Optional, Union
from enum import Enum, auto

class InputComplexity(Enum):
    """Categorizes input complexity to determine processing strategy."""
    SIMPLE_COMMAND = auto()      # Clear, parsed command
    CONVERSATIONAL = auto()      # Dialog, questions, complex interaction
    DISAMBIGUATION = auto()      # Needs player to choose between options
    PARSING_ERROR = auto()       # Parser couldn't understand input


class ProcessingMode(Enum):
    """Processing modes for different types of interactions."""
    MECHANICAL = auto()         # Template-based, fast responses via parser
    NARRATIVE = auto()         # Rich storytelling, moderate LLM usage
    INTERPRETIVE = auto()      # Heavy LLM usage for complex situations
    DISAMBIGUATION = auto()    # Handling parser disambiguation


class AIGMBrainCustom:
    """
    Advanced AI GM Brain with integrated processing for the standalone server.
    """
    
    def __init__(self, 
                 game_id: str,
                 player_id: str = "player_character_id"):
        """Initialize the AI GM Brain."""
        self.game_id = game_id
        self.player_id = player_id
        
        # Internal state tracking
        self.interaction_count = 0
        self.player_sessions = {}
        
        # Logging
        self.logger = logging.getLogger(f"AIGMBrain_{game_id}")
        self.logger.info(f"Custom AI GM Brain initialized for game {game_id}")
    
    def process_player_input(self, input_string: str) -> Dict[str, Any]:
        """
        Process player input and generate appropriate response.
        
        Args:
            input_string: Raw text input from the player
            
        Returns:
            Dictionary containing response and metadata
        """
        self.interaction_count += 1
        start_time = time.time()
        
        # Log the input
        self.logger.info(f"Processing input #{self.interaction_count}: '{input_string}'")
        
        # Check for help or system commands
        if input_string.lower().strip() in ['help', '?', 'commands']:
            return self._generate_help_response()
        
        # Process based on input type
        input_lower = input_string.lower()
        
        # Handle location-related commands
        if any(phrase in input_lower for phrase in ['look', 'examine surroundings', 'where am i']):
            return self._generate_location_response(input_string)
        
        # Handle inventory-related commands
        if any(phrase in input_lower for phrase in ['inventory', 'items', 'what am i carrying']):
            return self._generate_inventory_response(input_string)
        
        # Handle magic-related commands
        if any(phrase in input_lower for phrase in ['cast', 'spell', 'magic', 'mana']):
            return self._generate_magic_response(input_string)
        
        # Handle combat-related commands
        if any(phrase in input_lower for phrase in ['attack', 'fight', 'combat', 'battle']):
            return self._generate_combat_response(input_string)
        
        # Handle exploration commands
        if any(phrase in input_lower for phrase in ['explore', 'search', 'investigate']):
            return self._generate_exploration_response(input_string)
        
        # Handle crafting commands
        if any(phrase in input_lower for phrase in ['craft', 'create', 'make', 'forge']):
            return self._generate_crafting_response(input_string)
        
        # Handle NPC interaction
        if any(phrase in input_lower for phrase in ['talk', 'speak', 'ask', 'tell']):
            return self._generate_npc_interaction_response(input_string)
        
        # Handle lore/story questions
        if any(phrase in input_lower for phrase in ['lore', 'story', 'history', 'tell me about']):
            return self._generate_lore_response(input_string)
        
        # Default to interpretive response for unknown inputs
        return self._generate_interpretive_response(input_string)
    
    def _generate_help_response(self) -> Dict[str, Any]:
        """Generate help response."""
        return {
            "response_text": (
                "Welcome to TextRealmsAI! Here are some commands you can try:\n\n"
                "- Look/examine: Observe your surroundings\n"
                "- Inventory: Check what you're carrying\n"
                "- Cast [spell]: Use your magical abilities\n"
                "- Talk to [NPC]: Interact with characters\n"
                "- Explore [area]: Investigate your environment\n"
                "- Craft [item]: Create useful items\n"
                "- Attack [target]: Engage in combat\n\n"
                "You can also ask questions about the world, its history, or your current quest."
            ),
            "success": True,
            "metadata": {
                "processing_mode": ProcessingMode.MECHANICAL.name,
                "complexity": InputComplexity.SIMPLE_COMMAND.name
            }
        }
    
    def _generate_location_response(self, input_string: str) -> Dict[str, Any]:
        """Generate location description response."""
        descriptions = [
            "You find yourself in a lush forest clearing. Sunlight filters through the canopy above, creating dancing patterns on the forest floor. The air is fresh and filled with the scent of pine and wildflowers. Several paths lead off in different directions.",
            
            "You stand in the bustling marketplace of Eldoria's capital city. Merchants hawk their wares from colorful stalls, the air thick with the aroma of spices and street food. The crowd moves around you, a tapestry of diverse cultures and races.",
            
            "The ancient ruins stretch before you, crumbling stone structures half-reclaimed by nature. Moss and vines crawl up once-grand columns, and the silence holds a certain weight. You sense powerful magical residues lingering in this forgotten place.",
            
            "You're at the edge of a crystalline lake, its surface reflecting the surrounding mountains like a perfect mirror. The water appears unusually still and deep, with occasional ripples suggesting something moves beneath. A stone path winds along the shoreline."
        ]
        
        return {
            "response_text": random.choice(descriptions),
            "success": True,
            "metadata": {
                "processing_mode": ProcessingMode.NARRATIVE.name,
                "complexity": InputComplexity.SIMPLE_COMMAND.name,
                "requires_llm": False
            }
        }
    
    def _generate_inventory_response(self, input_string: str) -> Dict[str, Any]:
        """Generate inventory response."""
        return {
            "response_text": (
                "You check your inventory and find:\n\n"
                "- A steel sword (slightly worn but well-balanced)\n"
                "- A leather backpack containing:\n"
                "  • 3 health potions (red liquid, restores 50 health each)\n"
                "  • 2 mana potions (blue liquid, restores 40 mana each)\n"
                "  • A small pouch of gold coins (87 gold)\n"
                "- A spellbook with several marked pages\n"
                "- A silver amulet with a strange inscription\n"
                "- A map of the surrounding region (partially complete)\n"
                "- Basic supplies: flint, torch, rope, and dried rations"
            ),
            "success": True,
            "metadata": {
                "processing_mode": ProcessingMode.MECHANICAL.name,
                "complexity": InputComplexity.SIMPLE_COMMAND.name
            }
        }
    
    def _generate_magic_response(self, input_string: str) -> Dict[str, Any]:
        """Generate magic-related response."""
        # Extract spell name if present
        spell_parts = input_string.lower().split("cast ")
        if len(spell_parts) > 1:
            spell_name = spell_parts[1].strip()
            
            # Specific spell responses
            if "fire" in spell_name:
                return {
                    "response_text": (
                        f"You focus your magical energy and cast {spell_name}. Flames leap from your fingertips, "
                        "spiraling outward in a controlled pattern. The air around you grows noticeably warmer, "
                        "and nearby plant life seems to bend away from the heat. Your mastery of fire magic "
                        "allows you to shape the flames with precision."
                    ),
                    "success": True,
                    "metadata": {
                        "processing_mode": ProcessingMode.NARRATIVE.name,
                        "complexity": InputComplexity.SIMPLE_COMMAND.name,
                        "spell_cast": spell_name,
                        "element": "fire"
                    }
                }
            elif "heal" in spell_name:
                return {
                    "response_text": (
                        f"You channel restorative energy and cast {spell_name}. A warm, golden light emanates "
                        "from your hands, washing over you with gentle waves of healing energy. You feel your "
                        "wounds begin to close and your vitality return. The spell leaves behind a lingering "
                        "sensation of renewal and the faint scent of herbs."
                    ),
                    "success": True,
                    "metadata": {
                        "processing_mode": ProcessingMode.NARRATIVE.name,
                        "complexity": InputComplexity.SIMPLE_COMMAND.name,
                        "spell_cast": spell_name,
                        "element": "restoration"
                    }
                }
            elif "shield" in spell_name or "protect" in spell_name:
                return {
                    "response_text": (
                        f"You focus your will and cast {spell_name}. A translucent barrier of magical energy "
                        "forms around you, shimmering with a subtle blue-white light. You can feel the spell "
                        "drawing on your magical reserves to maintain its protective field. The shield will "
                        "absorb incoming damage until its energy is depleted or you dismiss it."
                    ),
                    "success": True,
                    "metadata": {
                        "processing_mode": ProcessingMode.NARRATIVE.name,
                        "complexity": InputComplexity.SIMPLE_COMMAND.name,
                        "spell_cast": spell_name,
                        "element": "protection"
                    }
                }
            else:
                # Generic spell response
                return {
                    "response_text": (
                        f"You weave magical energies and cast {spell_name}. The spell manifests with a display "
                        "of arcane power appropriate to its nature. Your magical affinity enhances the spell's "
                        "potency, creating effects that blend seamlessly with the environment around you."
                    ),
                    "success": True,
                    "metadata": {
                        "processing_mode": ProcessingMode.NARRATIVE.name,
                        "complexity": InputComplexity.SIMPLE_COMMAND.name,
                        "spell_cast": spell_name
                    }
                }
        
        # General magic information
        return {
            "response_text": (
                "You have access to various schools of magic, including:\n\n"
                "- Elemental (fire, water, earth, air)\n"
                "- Arcane (force, telekinesis, detection)\n"
                "- Restoration (healing, protection, purification)\n"
                "- Illusion (light, sound, sensory manipulation)\n\n"
                "To cast a spell, use 'cast [spell name]'. Your magical affinity and learned aspects "
                "determine which spells are most effective for you. Your current mana level is 78/100."
            ),
            "success": True,
            "metadata": {
                "processing_mode": ProcessingMode.MECHANICAL.name,
                "complexity": InputComplexity.CONVERSATIONAL.name
            }
        }
    
    def _generate_combat_response(self, input_string: str) -> Dict[str, Any]:
        """Generate combat-related response."""
        return {
            "response_text": (
                "You prepare for combat, adopting a balanced stance that allows for quick movement. "
                "Combat in this world is tactical, with outcomes determined by your skills, equipment, "
                "positioning, and understanding of your opponent's capabilities. You can use various "
                "combat styles including aggressive, defensive, or balanced approaches. Each weapon "
                "type offers unique advantages in different situations.\n\n"
                "To engage in combat, you can use commands like 'attack [target]', 'defend', 'use [skill]', "
                "or describe more complex actions like 'circle around the opponent to find an opening'."
            ),
            "success": True,
            "requires_llm": True,
            "llm_used": True,
            "metadata": {
                "processing_mode": ProcessingMode.INTERPRETIVE.name,
                "complexity": InputComplexity.CONVERSATIONAL.name,
                "combat_system": "tactical"
            }
        }
    
    def _generate_exploration_response(self, input_string: str) -> Dict[str, Any]:
        """Generate exploration-related response."""
        exploration_responses = [
            "You carefully explore the area, paying attention to details others might miss. Your thorough investigation reveals subtle clues about the history and nature of this place. Hidden pathways, concealed treasures, and environmental storytelling reward your curiosity.",
            
            "As you explore, you notice signs of recent activity - disturbed vegetation, subtle tracks, and other traces that tell a story about who or what has passed through here recently. Your exploration skills allow you to piece together a narrative from these environmental clues.",
            
            "Your exploration reveals both natural and constructed elements intertwined in this location. There's evidence of ancient presence here, with subtle architectural influences that most would overlook. The more you investigate, the more layers of history become apparent."
        ]
        
        return {
            "response_text": random.choice(exploration_responses),
            "success": True,
            "requires_llm": True,
            "llm_used": True,
            "metadata": {
                "processing_mode": ProcessingMode.NARRATIVE.name,
                "complexity": InputComplexity.CONVERSATIONAL.name,
                "exploration_focus": "environmental_storytelling"
            }
        }
    
    def _generate_crafting_response(self, input_string: str) -> Dict[str, Any]:
        """Generate crafting-related response."""
        return {
            "response_text": (
                "You access your crafting knowledge, recalling the various disciplines available to you:\n\n"
                "- Alchemy: Creating potions, elixirs, and magical reagents\n"
                "- Blacksmithing: Forging weapons, armor, and metal tools\n"
                "- Enchanting: Imbuing items with magical properties\n"
                "- Jewelcrafting: Working with precious gems and metals\n"
                "- Woodworking: Crafting bows, staves, and wooden items\n\n"
                "Each crafting discipline has its own skill progression, recipes, and required materials. "
                "Your crafting success is determined by your skill level, the quality of materials used, "
                "and the complexity of the item being created."
            ),
            "success": True,
            "requires_llm": True,
            "llm_used": True,
            "metadata": {
                "processing_mode": ProcessingMode.MECHANICAL.name,
                "complexity": InputComplexity.CONVERSATIONAL.name,
                "crafting_system": "multi_discipline"
            }
        }
    
    def _generate_npc_interaction_response(self, input_string: str) -> Dict[str, Any]:
        """Generate NPC interaction response."""
        npc_responses = [
            "The elderly merchant smiles warmly as you approach. 'Ah, a traveler! I've seen many come and go through these lands. What can old Torim do for you today? Looking for supplies, or perhaps some local knowledge? I've been trading along these routes for forty years - not much happens here without me hearing about it.'",
            
            "The armored guard regards you with a professional, measured gaze. 'State your business in Eldoria, traveler. We've had trouble with bandits on the eastern roads, so we're being cautious with newcomers. No offense intended - just doing my duty. If you're here peacefully, you'll find our town hospitable enough.'",
            
            "A young apprentice mage nervously adjusts her robes as you speak to her. 'Oh! Hello there. I'm Lyra, studying at the Arcanum. I'm actually out gathering specimens for my research on local magical flora. The convergence of ley lines in this region creates fascinating botanical anomalies. Would... would you like to know more about it?'"
        ]
        
        return {
            "response_text": random.choice(npc_responses),
            "success": True,
            "requires_llm": True,
            "llm_used": True,
            "metadata": {
                "processing_mode": ProcessingMode.NARRATIVE.name,
                "complexity": InputComplexity.CONVERSATIONAL.name,
                "npc_interaction": True
            }
        }
    
    def _generate_lore_response(self, input_string: str) -> Dict[str, Any]:
        """Generate lore/history response."""
        return {
            "response_text": (
                "The world of Eldoria has a rich and complex history spanning thousands of years. The current age, "
                "known as the Age of Renewal, began after the Cataclysm that ended the previous Golden Era. "
                "Ancient civilizations left behind ruins filled with lost knowledge and powerful artifacts.\n\n"
                "The land is divided into several major regions, each with distinct cultures, magical affinities, "
                "and political systems. The central kingdom of Valorian maintains an uneasy peace between "
                "the various factions. The Mages Conclave regulates magical practice, while the Adventurers "
                "Guild provides structure for those exploring the dangerous frontiers.\n\n"
                "Magic in this world flows from natural ley lines that crisscross the land, with concentrated "
                "nodes creating areas of unusual magical phenomena. Different regions have affinities for "
                "particular magical aspects, influencing the flora, fauna, and cultural practices of the inhabitants."
            ),
            "success": True,
            "requires_llm": True,
            "llm_used": True,
            "metadata": {
                "processing_mode": ProcessingMode.NARRATIVE.name,
                "complexity": InputComplexity.CONVERSATIONAL.name,
                "lore_topic": "world_history"
            }
        }
    
    def _generate_interpretive_response(self, input_string: str) -> Dict[str, Any]:
        """Generate interpretive response for complex or unknown inputs."""
        interpretive_responses = [
            "Your actions in this world have consequences that ripple outward in ways both seen and unseen. Every choice shapes your story and influences how others perceive and interact with you. What exactly are you trying to accomplish with this course of action?",
            
            "The path you're considering is intriguing. This world responds to player agency in complex ways, with systems that interact dynamically based on your decisions. Your unique approach to challenges is what makes your journey special. Could you elaborate on what you're trying to do?",
            
            "Your intuition leads you to explore possibilities beyond the obvious. The world has depth beyond what's immediately apparent, with interconnected systems of magic, politics, ecology, and history. Your curiosity opens doors that remain closed to less inquisitive minds. How would you like to proceed?"
        ]
        
        return {
            "response_text": random.choice(interpretive_responses),
            "success": True,
            "requires_llm": True,
            "llm_used": True,
            "metadata": {
                "processing_mode": ProcessingMode.INTERPRETIVE.name,
                "complexity": InputComplexity.CONVERSATIONAL.name,
                "interpretive_focus": "player_agency"
            }
        }
