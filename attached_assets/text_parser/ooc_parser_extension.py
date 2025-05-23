"""
OOC (Out-of-Character) parser extension for the text parser engine
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from text_parser.parser_engine import CommandPattern, Token, TokenType, ParsedCommand


class OOCCommandType(Enum):
    """Types of OOC commands"""
    GENERAL_QUERY = "general_query"
    STATS_REQUEST = "stats_request"
    INVENTORY_REQUEST = "inventory_request"
    QUEST_LOG = "quest_log"
    HELP_REQUEST = "help_request"
    GAME_MECHANICS = "game_mechanics"
    LORE_QUESTION = "lore_question"
    SYSTEM_INFO = "system_info"


class OOCParser:
    """Parser specifically for OOC commands"""
    
    def __init__(self):
        # Keywords that trigger specific OOC command types
        self.ooc_keywords = {
            'stats': OOCCommandType.STATS_REQUEST,
            'inventory': OOCCommandType.INVENTORY_REQUEST,
            'inv': OOCCommandType.INVENTORY_REQUEST,
            'quest': OOCCommandType.QUEST_LOG,
            'quests': OOCCommandType.QUEST_LOG,
            'log': OOCCommandType.QUEST_LOG,
            'help': OOCCommandType.HELP_REQUEST,
            'rules': OOCCommandType.GAME_MECHANICS,
            'mechanics': OOCCommandType.GAME_MECHANICS,
            'how': OOCCommandType.GAME_MECHANICS,
            'what': OOCCommandType.LORE_QUESTION,
            'who': OOCCommandType.LORE_QUESTION,
            'where': OOCCommandType.LORE_QUESTION,
            'when': OOCCommandType.LORE_QUESTION,
            'why': OOCCommandType.LORE_QUESTION,
            'time': OOCCommandType.SYSTEM_INFO,
            'date': OOCCommandType.SYSTEM_INFO,
            'session': OOCCommandType.SYSTEM_INFO
        }
    
    def parse_ooc_command(self, ooc_payload: str) -> Tuple[OOCCommandType, str, Dict[str, Any]]:
        """
        Parse OOC command payload to determine type and extract relevant information.
        
        Args:
            ooc_payload: The text after /ooc command
            
        Returns:
            Tuple of (command_type, cleaned_payload, metadata)
        """
        payload_lower = ooc_payload.lower().strip()
        words = payload_lower.split()
        
        if not words:
            return OOCCommandType.GENERAL_QUERY, ooc_payload, {}
        
        # Check first word for command type
        first_word = words[0]
        command_type = self.ooc_keywords.get(first_word, OOCCommandType.GENERAL_QUERY)
        
        # Extract metadata based on command type
        metadata = self._extract_metadata(command_type, words, ooc_payload)
        
        return command_type, ooc_payload, metadata
    
    def _extract_metadata(self, command_type: OOCCommandType, words: List[str], full_payload: str) -> Dict[str, Any]:
        """Extract metadata from OOC command based on type"""
        metadata = {'original_payload': full_payload}
        
        if command_type == OOCCommandType.HELP_REQUEST:
            # Extract what they need help with
            if len(words) > 1:
                metadata['help_topic'] = ' '.join(words[1:])
            else:
                metadata['help_topic'] = 'general'
        
        elif command_type == OOCCommandType.LORE_QUESTION:
            # Extract the subject of the lore question
            metadata['lore_subject'] = self._extract_lore_subject(words, full_payload)
        
        elif command_type == OOCCommandType.GAME_MECHANICS:
            # Extract the mechanic being asked about
            metadata['mechanic_topic'] = self._extract_mechanic_topic(words, full_payload)
        
        elif command_type == OOCCommandType.STATS_REQUEST:
            # Check if they want specific stats
            if len(words) > 1:
                metadata['stat_type'] = ' '.join(words[1:])
            else:
                metadata['stat_type'] = 'all'
        
        return metadata
    
    def _extract_lore_subject(self, words: List[str], full_payload: str) -> str:
        """Extract the subject of a lore question"""
        # Look for key nouns after question words
        question_words = {'what', 'who', 'where', 'when', 'why', 'how'}
        
        for i, word in enumerate(words):
            if word in question_words and i + 1 < len(words):
                return ' '.join(words[i+1:])
        
        return full_payload
    
    def _extract_mechanic_topic(self, words: List[str], full_payload: str) -> str:
        """Extract the topic of a game mechanics question"""
        mechanic_indicators = {'how', 'rules', 'mechanics', 'does', 'do', 'work', 'works'}
        
        # Find content after mechanic indicators
        for i, word in enumerate(words):
            if word in mechanic_indicators and i + 1 < len(words):
                return ' '.join(words[i+1:])
        
        return full_payload


# Add to the existing CommandPattern enum
CommandPattern.OOC = "ooc"


# Extension to the existing ParserEngine class
def parse_ooc_command_extension(parser_engine_instance, input_text: str, context: Dict[str, Any] = None) -> ParsedCommand:
    """
    Extension method for ParserEngine to handle OOC commands.
    This should be integrated into the existing ParserEngine.parse() method.
    """
    
    # Check if input starts with /ooc
    normalized_input = input_text.strip()
    if not normalized_input.lower().startswith('/ooc'):
        return None  # Not an OOC command
    
    # Extract OOC payload (everything after /ooc)
    ooc_payload = normalized_input[4:].strip()  # Remove '/ooc' and trim
    
    if not ooc_payload:
        # Empty OOC command
        return ParsedCommand(
            raw_input=input_text,
            action="OOC_COMMAND",
            pattern=CommandPattern.OOC,
            error_message="OOC command is empty. Try '/ooc help' for assistance."
        )
    
    # Parse the OOC payload
    ooc_parser = OOCParser()
    command_type, cleaned_payload, metadata = ooc_parser.parse_ooc_command(ooc_payload)
    
    # Create ParsedCommand for OOC
    parsed_command = ParsedCommand(
        raw_input=input_text,
        action="OOC_COMMAND",
        pattern=CommandPattern.OOC,
        direct_object_phrase=None,  # OOC doesn't use standard noun phrases
        indirect_object_phrase=None,
        preposition=None
    )
    
    # Store OOC-specific data in the command
    parsed_command.ooc_data = {
        'command_type': command_type,
        'payload': cleaned_payload,
        'metadata': metadata
    }
    
    return parsed_command