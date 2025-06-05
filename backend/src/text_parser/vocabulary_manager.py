"""
Vocabulary Manager - Manages known words and phrases for the text parser

This module maintains dictionaries of known verbs, nouns, adjectives, etc.
to help the parser engine recognize and process player commands effectively.
"""

from typing import Dict, List, Set, Optional, TYPE_CHECKING
import logging

# Type checking import to avoid circular imports
if TYPE_CHECKING:
    from .parser_engine import ParserEngine

logger = logging.getLogger("text_parser.vocabulary")


class VocabularyManager:
    """
    Manages dictionaries of known words and synonyms to assist in parsing.
    """
    
    def __init__(self):
        """Initialize vocabulary dictionaries."""
        self.action_synonyms = self._init_action_synonyms()
        self.item_synonyms = {}  # Will be populated as items are discovered
        self.direction_synonyms = self._init_direction_synonyms()
        self.character_synonyms = {}  # Will be populated with NPCs discovered
        self.location_synonyms = {}  # Will be populated with locations discovered
        
        # Parser engine reference for spaCy EntityRuler integration
        self._parser_engine: Optional['ParserEngine'] = None

    def set_parser_engine(self, parser_engine: 'ParserEngine') -> None:
        """
        Set the parser engine reference for spaCy EntityRuler integration.
        
        Args:
            parser_engine: The ParserEngine instance to integrate with
        """
        self._parser_engine = parser_engine
        logger.info("VocabularyManager connected to ParserEngine for spaCy integration")

    def _init_action_synonyms(self) -> Dict[str, List[str]]:
        """Initialize a dictionary of action synonyms."""
        return {
            "go": ["move", "walk", "run", "travel", "head", "journey"],
            "look": ["examine", "inspect", "observe", "view", "check", "see"],
            "take": ["get", "grab", "pick up", "collect", "acquire", "obtain"],
            "drop": ["put down", "leave", "discard", "throw away", "dispose"],
            "use": ["activate", "operate", "utilize", "apply", "employ"],
            "talk": ["speak", "chat", "converse", "discuss", "communicate"],
            "attack": ["fight", "hit", "strike", "assault", "battle", "combat"],
            "inventory": ["items", "belongings", "possessions", "gear", "equipment"],
            "help": ["guide", "instructions", "commands", "assistance", "tutorial"],
        }
        
    def _init_direction_synonyms(self) -> Dict[str, List[str]]:
        """Initialize a dictionary of direction synonyms."""
        return {
            "north": ["n", "forward"],
            "south": ["s", "backward", "backwards", "back"],
            "east": ["e", "right"],
            "west": ["w", "left"],
            "up": ["u", "above", "climb up", "ascend"],
            "down": ["d", "below", "climb down", "descend"],
            "northeast": ["ne"],
            "northwest": ["nw"],
            "southeast": ["se"],
            "southwest": ["sw"],
            "in": ["inside", "enter", "into"],
            "out": ["outside", "exit", "leave"],
        }
    
    def register_item(self, item_id: str, name: str, synonyms: List[str] = None) -> None:
        """
        Register an item in the vocabulary with optional synonyms.
        
        Args:
            item_id: Unique identifier for the item
            name: Primary name of the item
            synonyms: Optional list of synonyms for the item
        """
        if not synonyms:
            synonyms = []
            
        # Convert all to lowercase for case-insensitive matching
        name = name.lower()
        synonyms = [s.lower() for s in synonyms]
        
        if name not in synonyms:
            synonyms.append(name)
            
        self.item_synonyms[item_id] = synonyms
        logger.debug(f"Registered item {item_id} with names: {', '.join(synonyms)}")
        
        # Add to spaCy EntityRuler if parser engine is connected
        if self._parser_engine:
            # Add primary name and all synonyms to spaCy EntityRuler
            for synonym in synonyms:
                self._parser_engine.add_world_entity(synonym, "FANTASY_ITEM", f"item_{item_id}_{synonym}")
    
    def register_character(self, char_id: str, name: str, synonyms: List[str] = None) -> None:
        """
        Register a character in the vocabulary with optional synonyms.
        
        Args:
            char_id: Unique identifier for the character
            name: Primary name of the character
            synonyms: Optional list of synonyms for the character
        """
        if not synonyms:
            synonyms = []
            
        # Convert all to lowercase for case-insensitive matching
        name = name.lower()
        synonyms = [s.lower() for s in synonyms]
        
        if name not in synonyms:
            synonyms.append(name)
            
        self.character_synonyms[char_id] = synonyms
        logger.debug(f"Registered character {char_id} with names: {', '.join(synonyms)}")
        
        # Add to spaCy EntityRuler if parser engine is connected
        if self._parser_engine:
            # Add primary name and all synonyms to spaCy EntityRuler
            for synonym in synonyms:
                self._parser_engine.add_world_entity(synonym, "FANTASY_NPC", f"npc_{char_id}_{synonym}")
    
    def register_location(self, loc_id: str, name: str, synonyms: List[str] = None) -> None:
        """
        Register a location in the vocabulary with optional synonyms.
        
        Args:
            loc_id: Unique identifier for the location
            name: Primary name of the location
            synonyms: Optional list of synonyms for the location
        """
        if not synonyms:
            synonyms = []
            
        # Convert all to lowercase for case-insensitive matching
        name = name.lower()
        synonyms = [s.lower() for s in synonyms]
        
        if name not in synonyms:
            synonyms.append(name)
            
        self.location_synonyms[loc_id] = synonyms
        logger.debug(f"Registered location {loc_id} with names: {', '.join(synonyms)}")
        
        # Add to spaCy EntityRuler if parser engine is connected
        if self._parser_engine:
            # Add primary name and all synonyms to spaCy EntityRuler
            for synonym in synonyms:
                self._parser_engine.add_world_entity(synonym, "FANTASY_LOCATION", f"loc_{loc_id}_{synonym}")
    
    def get_canonical_action(self, action_text: str) -> Optional[str]:
        """
        Convert an action word to its canonical form.
        
        Args:
            action_text: Action text from player input
        
        Returns:
            Canonical action or None if not recognized
        """
        action_text = action_text.lower()
        
        # Check if it's already a canonical action
        if action_text in self.action_synonyms:
            return action_text
            
        # Check if it's a synonym
        for action, synonyms in self.action_synonyms.items():
            if action_text in synonyms:
                return action
                
        return None
    
    def get_canonical_direction(self, direction_text: str) -> Optional[str]:
        """
        Convert a direction word to its canonical form.
        
        Args:
            direction_text: Direction text from player input
        
        Returns:
            Canonical direction or None if not recognized
        """
        direction_text = direction_text.lower()
        
        # Check if it's already a canonical direction
        if direction_text in self.direction_synonyms:
            return direction_text
            
        # Check if it's a synonym
        for direction, synonyms in self.direction_synonyms.items():
            if direction_text in synonyms:
                return direction
                
        return None
    
    def get_item_id(self, item_text: str) -> Optional[str]:
        """
        Convert an item name to its canonical ID.
        
        Args:
            item_text: Item text from player input
        
        Returns:
            Item ID or None if not recognized
        """
        item_text = item_text.lower()
        
        for item_id, synonyms in self.item_synonyms.items():
            if item_text in synonyms:
                return item_id
                
        return None
    
    def get_character_id(self, char_text: str) -> Optional[str]:
        """
        Convert a character name to its canonical ID.
        
        Args:
            char_text: Character text from player input
        
        Returns:
            Character ID or None if not recognized
        """
        char_text = char_text.lower()
        
        for char_id, synonyms in self.character_synonyms.items():
            if char_text in synonyms:
                return char_id
                
        return None
    
    def get_location_id(self, loc_text: str) -> Optional[str]:
        """
        Convert a location name to its canonical ID.
        
        Args:
            loc_text: Location text from player input
        
        Returns:
            Location ID or None if not recognized
        """
        loc_text = loc_text.lower()
        
        for loc_id, synonyms in self.location_synonyms.items():
            if loc_text in synonyms:
                return loc_id
                
        return None


# Create a global instance of the vocabulary manager
vocabulary_manager = VocabularyManager()