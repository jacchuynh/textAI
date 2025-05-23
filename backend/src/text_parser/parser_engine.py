"""
Parser Engine - Core text parsing capabilities for the AI GM system

This module provides the main parsing engine that converts player input text
into structured command objects for the AI GM to process.
"""

import re
import logging
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger("text_parser")


@dataclass
class ParsedCommand:
    """Structured representation of a player's text command."""
    action: str                 # Primary verb/action (e.g., "go", "look", "take")
    target: Optional[str] = None  # Primary object of the action
    modifiers: Dict[str, Any] = None  # Additional qualifiers (direction, manner, etc.)
    context: Dict[str, Any] = None  # Additional context for command execution
    confidence: float = 1.0     # Confidence level of the parse (0.0-1.0)
    raw_text: str = ""          # Original raw text input
    
    def __post_init__(self):
        """Initialize default values for empty fields."""
        if self.modifiers is None:
            self.modifiers = {}
        if self.context is None:
            self.context = {}


class ActionType(Enum):
    """Categories of player actions for classification."""
    MOVEMENT = auto()       # Moving in space
    OBSERVATION = auto()    # Looking, examining, perceiving
    INTERACTION = auto()    # Touching, using, manipulating
    COMMUNICATION = auto()  # Talking, asking, telling
    COMBAT = auto()         # Fighting, attacking, defending
    INVENTORY = auto()      # Taking, dropping, inventory management
    META = auto()           # Help, quit, save, etc.
    UNKNOWN = auto()        # Could not classify


class ParserEngine:
    """
    Main engine for parsing player input text into structured commands.
    """
    
    def __init__(self):
        """Initialize the parser engine with vocabulary and patterns."""
        self.patterns = self._init_patterns()
        self.action_mappings = self._init_action_mappings()
        self.logger = logging.getLogger("text_parser.engine")
    
    def _init_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for command parsing."""
        patterns = {
            # Simple movement: go north, move west, etc.
            "movement": re.compile(r"^(?:go|move|walk|run|head|travel)(?:\s+to)?\s+([a-zA-Z]+)$", re.IGNORECASE),
            
            # Look: look, look around, look at X, examine X
            "look": re.compile(r"^(?:look|examine|inspect|observe)(?:\s+(?:at|around|in|inside))?\s*(.*)$", re.IGNORECASE),
            
            # Take/Get: take X, get X, pick up X
            "take": re.compile(r"^(?:take|get|grab|pick up)\s+(.+)$", re.IGNORECASE),
            
            # Drop: drop X, put down X
            "drop": re.compile(r"^(?:drop|discard|put down|throw away)\s+(.+)$", re.IGNORECASE),
            
            # Use: use X, activate X, with Y
            "use": re.compile(r"^(?:use|activate|operate|with)\s+(.+?)(?:\s+(?:on|with)\s+(.+))?$", re.IGNORECASE),
            
            # Talk: talk to X, speak with X, ask X about Y
            "talk": re.compile(r"^(?:talk|speak|chat|converse)(?:\s+(?:to|with))?\s+(.+?)(?:\s+about\s+(.+))?$", re.IGNORECASE),
            
            # Attack: attack X, fight X, hit X with Y
            "attack": re.compile(r"^(?:attack|fight|hit|strike)\s+(.+?)(?:\s+with\s+(.+))?$", re.IGNORECASE),
            
            # Inventory: inventory, i, check inventory
            "inventory": re.compile(r"^(?:inventory|i|items|check inventory)$", re.IGNORECASE),
            
            # Help: help, ?, commands, etc.
            "help": re.compile(r"^(?:help|\?|commands|what can i do)$", re.IGNORECASE),
        }
        return patterns
    
    def _init_action_mappings(self) -> Dict[str, ActionType]:
        """Initialize mappings from actions to action types."""
        return {
            "go": ActionType.MOVEMENT,
            "move": ActionType.MOVEMENT,
            "walk": ActionType.MOVEMENT,
            "run": ActionType.MOVEMENT,
            "look": ActionType.OBSERVATION,
            "examine": ActionType.OBSERVATION,
            "inspect": ActionType.OBSERVATION,
            "observe": ActionType.OBSERVATION,
            "take": ActionType.INVENTORY,
            "get": ActionType.INVENTORY,
            "grab": ActionType.INVENTORY,
            "drop": ActionType.INVENTORY,
            "discard": ActionType.INVENTORY,
            "use": ActionType.INTERACTION,
            "activate": ActionType.INTERACTION,
            "operate": ActionType.INTERACTION,
            "talk": ActionType.COMMUNICATION,
            "speak": ActionType.COMMUNICATION,
            "ask": ActionType.COMMUNICATION,
            "tell": ActionType.COMMUNICATION,
            "attack": ActionType.COMBAT,
            "fight": ActionType.COMBAT,
            "hit": ActionType.COMBAT,
            "inventory": ActionType.INVENTORY,
            "help": ActionType.META,
        }
    
    def parse(self, input_text: str) -> Optional[ParsedCommand]:
        """
        Parse player input text into a structured command.
        
        Args:
            input_text: Raw text input from the player
            
        Returns:
            ParsedCommand object if parsing succeeds, None otherwise
        """
        if not input_text or not input_text.strip():
            return None
            
        text = input_text.strip().lower()
        
        # Try each pattern to see if we get a match
        for action, pattern in self.patterns.items():
            match = pattern.match(text)
            if match:
                # We have a match, process according to the action type
                if action == "movement":
                    direction = match.group(1)
                    return ParsedCommand(
                        action="go",
                        target=direction,
                        raw_text=input_text
                    )
                elif action == "look":
                    target = match.group(1).strip() if match.group(1) else None
                    return ParsedCommand(
                        action="look",
                        target=target if target else None,
                        raw_text=input_text
                    )
                elif action in ["take", "drop"]:
                    item = match.group(1).strip()
                    return ParsedCommand(
                        action=action,
                        target=item,
                        raw_text=input_text
                    )
                elif action == "use":
                    item = match.group(1).strip()
                    target = match.group(2).strip() if match.group(2) else None
                    modifiers = {"with": target} if target else {}
                    return ParsedCommand(
                        action="use",
                        target=item,
                        modifiers=modifiers,
                        raw_text=input_text
                    )
                elif action == "talk":
                    person = match.group(1).strip()
                    topic = match.group(2).strip() if match.group(2) else None
                    modifiers = {"about": topic} if topic else {}
                    return ParsedCommand(
                        action="talk",
                        target=person,
                        modifiers=modifiers,
                        raw_text=input_text
                    )
                elif action == "attack":
                    enemy = match.group(1).strip()
                    weapon = match.group(2).strip() if match.group(2) else None
                    modifiers = {"with": weapon} if weapon else {}
                    return ParsedCommand(
                        action="attack",
                        target=enemy,
                        modifiers=modifiers,
                        raw_text=input_text
                    )
                elif action in ["inventory", "help"]:
                    return ParsedCommand(
                        action=action,
                        raw_text=input_text
                    )
                
        # If we get here, no pattern matched
        # Try to extract a simple verb-noun structure
        words = text.split()
        if len(words) >= 1:
            action = words[0]
            target = " ".join(words[1:]) if len(words) > 1 else None
            
            # Check if the action is known
            if action in self.action_mappings:
                return ParsedCommand(
                    action=action,
                    target=target,
                    confidence=0.7,  # Lower confidence for simple extraction
                    raw_text=input_text
                )
        
        # Could not parse, return None
        return None
    
    def get_suggestions(self, input_text: str) -> List[str]:
        """
        Get suggestions for failed parsing.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            List of command suggestions
        """
        words = input_text.lower().split()
        suggestions = []
        
        # Common commands to suggest
        common_commands = [
            "look", "examine", "go", "move", "take", "get", "use",
            "talk", "speak", "attack", "help", "inventory"
        ]
        
        # Check if any word is close to a common command
        for word in words:
            for cmd in common_commands:
                if word in cmd or (len(word) > 2 and word[:3] == cmd[:3]):
                    if cmd not in suggestions:
                        suggestions.append(cmd)
                        
        # Add some context-specific suggestions
        if "go" in suggestions or "move" in suggestions:
            suggestions.append("go north")
            
        if "look" in suggestions or "examine" in suggestions:
            suggestions.append("look around")
            
        return suggestions[:3]  # Limit to 3 suggestions


# Create a global instance of the parser engine
parser_engine = ParserEngine()


def parse_input(input_text: str) -> Optional[ParsedCommand]:
    """
    Parse player input text into a structured command using the global parser engine.
    
    Args:
        input_text: Raw text input from the player
        
    Returns:
        ParsedCommand object if parsing succeeds, None otherwise
    """
    return parser_engine.parse(input_text)