"""
Text Parser Module

This module handles parsing of natural language commands from players
into structured game actions.
"""

import re
from typing import Dict, Any, List, Optional

class TextParser:
    """
    Parser for converting natural language commands into game actions.
    """
    def __init__(self):
        # Initialize action patterns
        self._init_action_patterns()
    
    def _init_action_patterns(self):
        """Initialize regex patterns for detecting different action types."""
        self.movement_patterns = [
            r"(?:go|walk|move|travel|head)(?:\s+(?:to|towards|into))?\s+(.+)",
            r"enter\s+(.+)",
        ]
        
        self.dialogue_patterns = [
            r"(?:talk|speak|chat)\s+(?:to|with)?\s+(.+)",
            r"ask\s+(.+)\s+about\s+(.+)",
            r"tell\s+(.+)\s+about\s+(.+)",
            r"greet\s+(.+)"
        ]
        
        self.combat_patterns = [
            r"(?:attack|fight|hit|strike)\s+(.+)",
            r"cast\s+(.+)\s+(?:at|on)\s+(.+)",
            r"shoot\s+(.+)\s+(?:at|with)\s+(.+)?",
            r"use\s+(.+)\s+(?:on|against)\s+(.+)"
        ]
        
        self.inventory_patterns = [
            r"(?:check|view|see|look at)\s+(?:my\s+)?(?:inventory|items|gear)",
            r"(?:use|consume|drink|eat)\s+(?:my\s+)?(.+)",
            r"equip\s+(?:my\s+)?(.+)",
            r"unequip\s+(?:my\s+)?(.+)",
            r"drop\s+(?:my\s+)?(.+)"
        ]
        
        self.magic_patterns = [
            r"cast\s+(.+?)(?:\s+(?:at|on)\s+(.+))?",
            r"(?:use|activate)\s+(?:spell|magic)\s+(.+?)(?:\s+(?:at|on)\s+(.+))?",
            r"enchant\s+(.+)\s+with\s+(.+)"
        ]
        
        self.crafting_patterns = [
            r"craft\s+(.+)",
            r"make\s+(.+)",
            r"forge\s+(.+)",
            r"brew\s+(.+)",
            r"create\s+(.+)",
            r"(?:check|view|see|list)\s+(?:crafting\s+)?recipes"
        ]
        
        self.quest_patterns = [
            r"(?:check|view|see|list)\s+(?:my\s+)?quests",
            r"(?:accept|take)\s+(?:quest|mission)\s+(.+)",
            r"(?:complete|finish|turn in)\s+(?:quest|mission)\s+(.+)",
            r"track\s+(?:quest|mission)\s+(.+)"
        ]
        
        self.examine_patterns = [
            r"(?:look|examine|inspect|check)\s+(?:at\s+)?(.+)",
            r"read\s+(.+)",
            r"search\s+(.+)",
            r"investigate\s+(.+)"
        ]
    
    def parse_command(self, command_text: str) -> Dict[str, Any]:
        """
        Parse a natural language command into a structured action dictionary.
        
        Args:
            command_text: The command text to parse
            
        Returns:
            A dictionary with the parsed action details
        """
        # Clean and normalize the command text
        command = command_text.strip().lower()
        
        # Store original text for AI GM fallback
        result = {
            "original_text": command_text
        }
        
        # Try to match against known patterns
        action_type = self._determine_action_type(command)
        result["action_type"] = action_type
        
        # Parse the details based on action type
        if action_type == "movement":
            self._parse_movement(command, result)
        elif action_type == "dialogue":
            self._parse_dialogue(command, result)
        elif action_type == "combat":
            self._parse_combat(command, result)
        elif action_type == "inventory":
            self._parse_inventory(command, result)
        elif action_type == "magic":
            self._parse_magic(command, result)
        elif action_type == "crafting":
            self._parse_crafting(command, result)
        elif action_type == "quest":
            self._parse_quest(command, result)
        elif action_type == "examine":
            self._parse_examine(command, result)
        else:
            # Unknown action type, let the AI GM handle it
            result["action_type"] = "unknown"
        
        return result
    
    def _determine_action_type(self, command: str) -> str:
        """Determine the type of action from the command."""
        # Check each pattern group
        if self._match_any_pattern(command, self.movement_patterns):
            return "movement"
        elif self._match_any_pattern(command, self.dialogue_patterns):
            return "dialogue"
        elif self._match_any_pattern(command, self.combat_patterns):
            return "combat"
        elif self._match_any_pattern(command, self.inventory_patterns):
            return "inventory"
        elif self._match_any_pattern(command, self.magic_patterns):
            return "magic"
        elif self._match_any_pattern(command, self.crafting_patterns):
            return "crafting"
        elif self._match_any_pattern(command, self.quest_patterns):
            return "quest"
        elif self._match_any_pattern(command, self.examine_patterns):
            return "examine"
        
        # Look around is a special case of examine
        if re.search(r"look\s+(?:around|about)", command):
            return "examine"
        
        # Default to unknown
        return "unknown"
    
    def _match_any_pattern(self, command: str, patterns: List[str]) -> bool:
        """Check if command matches any of the given patterns."""
        for pattern in patterns:
            if re.search(pattern, command):
                return True
        return False
    
    def _parse_movement(self, command: str, result: Dict[str, Any]) -> None:
        """Parse movement command details."""
        # Extract destination
        for pattern in self.movement_patterns:
            match = re.search(pattern, command)
            if match:
                result["action"] = "move"
                result["target"] = match.group(1).strip()
                return
        
        # If we get here, the command was identified as movement but didn't match any pattern
        result["action"] = "move"
        # Try to extract anything after "go", "move", etc.
        words = command.split()
        if len(words) > 1:
            result["target"] = " ".join(words[1:])
    
    def _parse_dialogue(self, command: str, result: Dict[str, Any]) -> None:
        """Parse dialogue command details."""
        # Check for "ask X about Y" pattern
        ask_pattern = r"ask\s+(.+)\s+about\s+(.+)"
        match = re.search(ask_pattern, command)
        if match:
            result["action"] = "ask"
            result["target"] = match.group(1).strip()
            result["topic"] = match.group(2).strip()
            return
        
        # Check for "talk to X" pattern
        talk_pattern = r"(?:talk|speak|chat)\s+(?:to|with)?\s+(.+)"
        match = re.search(talk_pattern, command)
        if match:
            result["action"] = "talk"
            result["target"] = match.group(1).strip()
            # Look for topic keywords
            if "quest" in command:
                result["topic"] = "quest"
            elif "shop" in command or "buy" in command or "sell" in command:
                result["topic"] = "shop"
            else:
                result["topic"] = "greeting"
            return
        
        # Other dialogue patterns
        for pattern in self.dialogue_patterns:
            match = re.search(pattern, command)
            if match:
                result["action"] = "talk"
                result["target"] = match.group(1).strip()
                result["topic"] = "greeting"
                return
    
    def _parse_combat(self, command: str, result: Dict[str, Any]) -> None:
        """Parse combat command details."""
        # Check for "cast X at Y" pattern
        cast_pattern = r"cast\s+(.+)\s+(?:at|on)\s+(.+)"
        match = re.search(cast_pattern, command)
        if match:
            result["action"] = "cast"
            result["spell"] = match.group(1).strip()
            result["target"] = match.group(2).strip()
            return
        
        # Check for "attack X" pattern
        attack_pattern = r"(?:attack|fight|hit|strike)\s+(.+)"
        match = re.search(attack_pattern, command)
        if match:
            result["action"] = "attack"
            result["target"] = match.group(1).strip()
            return
        
        # Check for flee/run
        if re.search(r"(?:flee|run|escape)", command):
            result["action"] = "flee"
            return
        
        # Other combat patterns
        for pattern in self.combat_patterns:
            match = re.search(pattern, command)
            if match:
                result["action"] = match.group(0).split()[0]  # first word as action
                result["target"] = match.group(1).strip()
                return
    
    def _parse_inventory(self, command: str, result: Dict[str, Any]) -> None:
        """Parse inventory command details."""
        # Check for view inventory
        if re.search(r"(?:check|view|see|look at)\s+(?:my\s+)?(?:inventory|items|gear)", command):
            result["action"] = "view"
            return
        
        # Check for use item
        use_pattern = r"(?:use|consume|drink|eat)\s+(?:my\s+)?(.+)"
        match = re.search(use_pattern, command)
        if match:
            result["action"] = "use"
            result["item"] = match.group(1).strip()
            return
        
        # Check for equip item
        equip_pattern = r"equip\s+(?:my\s+)?(.+)"
        match = re.search(equip_pattern, command)
        if match:
            result["action"] = "use"  # equipping is handled through "use"
            result["item"] = match.group(1).strip()
            return
        
        # Check for drop item
        drop_pattern = r"drop\s+(?:my\s+)?(.+)"
        match = re.search(drop_pattern, command)
        if match:
            result["action"] = "drop"
            result["item"] = match.group(1).strip()
            return
        
        # Default inventory action is view
        result["action"] = "view"
    
    def _parse_magic(self, command: str, result: Dict[str, Any]) -> None:
        """Parse magic command details."""
        # Check for "cast X at Y" pattern
        cast_pattern = r"cast\s+(.+?)(?:\s+(?:at|on)\s+(.+))?"
        match = re.search(cast_pattern, command)
        if match:
            result["action"] = "cast"
            result["spell"] = match.group(1).strip()
            if match.group(2):
                result["target"] = match.group(2).strip()
            return
        
        # Check for enchant
        enchant_pattern = r"enchant\s+(.+)\s+with\s+(.+)"
        match = re.search(enchant_pattern, command)
        if match:
            result["action"] = "enchant"
            result["item"] = match.group(1).strip()
            result["enchantment"] = match.group(2).strip()
            return
        
        # Default magic action is view available spells
        result["action"] = "view"
    
    def _parse_crafting(self, command: str, result: Dict[str, Any]) -> None:
        """Parse crafting command details."""
        # Check for list recipes
        if re.search(r"(?:check|view|see|list)\s+(?:crafting\s+)?recipes", command):
            result["action"] = "recipes"
            return
        
        # Check for craft item
        craft_pattern = r"(?:craft|make|forge|brew|create)\s+(.+)"
        match = re.search(craft_pattern, command)
        if match:
            result["action"] = "craft"
            result["recipe"] = match.group(1).strip()
            return
        
        # Default crafting action is view recipes
        result["action"] = "recipes"
    
    def _parse_quest(self, command: str, result: Dict[str, Any]) -> None:
        """Parse quest command details."""
        # Check for view quests
        if re.search(r"(?:check|view|see|list)\s+(?:my\s+)?quests", command):
            result["action"] = "view"
            return
        
        # Check for accept quest
        accept_pattern = r"(?:accept|take)\s+(?:quest|mission)\s+(.+)"
        match = re.search(accept_pattern, command)
        if match:
            result["action"] = "accept"
            result["quest"] = match.group(1).strip()
            return
        
        # Check for complete quest
        complete_pattern = r"(?:complete|finish|turn in)\s+(?:quest|mission)\s+(.+)"
        match = re.search(complete_pattern, command)
        if match:
            result["action"] = "complete"
            result["quest"] = match.group(1).strip()
            return
        
        # Check for track quest
        track_pattern = r"track\s+(?:quest|mission)\s+(.+)"
        match = re.search(track_pattern, command)
        if match:
            result["action"] = "track"
            result["quest"] = match.group(1).strip()
            return
        
        # Default quest action is view
        result["action"] = "view"
    
    def _parse_examine(self, command: str, result: Dict[str, Any]) -> None:
        """Parse examine command details."""
        # Check for look around
        if re.search(r"look\s+(?:around|about)", command):
            result["action"] = "look"
            result["target"] = "area"
            return
        
        # Check for examine object
        examine_pattern = r"(?:look|examine|inspect|check)\s+(?:at\s+)?(.+)"
        match = re.search(examine_pattern, command)
        if match:
            result["action"] = "examine"
            result["target"] = match.group(1).strip()
            return
        
        # Check for read object
        read_pattern = r"read\s+(.+)"
        match = re.search(read_pattern, command)
        if match:
            result["action"] = "read"
            result["target"] = match.group(1).strip()
            return
        
        # Default examine action
        result["action"] = "examine"
        
        # Try to extract target
        words = command.split()
        if len(words) > 1:
            result["target"] = " ".join(words[1:])