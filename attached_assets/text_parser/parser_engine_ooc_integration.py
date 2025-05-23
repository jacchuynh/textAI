"""
Integration of OOC parsing into the main parser engine
"""

from text_parser.parser_engine import ParserEngine
from text_parser.ooc_parser_extension import parse_ooc_command_extension


# Monkey patch or extend the ParserEngine class
def enhanced_parse_with_ooc(self, input_text: str, context_override=None):
    """
    Enhanced parse method that handles OOC commands first, then falls back to normal parsing.
    This replaces or extends the original ParserEngine.parse() method.
    """
    from game_context import game_context
    
    # Get context
    context = context_override or game_context.get_context()
    
    # First, check for OOC command
    ooc_command = parse_ooc_command_extension(self, input_text, context)
    if ooc_command:
        return ooc_command
    
    # If not OOC, proceed with normal parsing
    return self._original_parse(input_text, context_override)


# Store original parse method and replace with enhanced version
ParserEngine._original_parse = ParserEngine.parse
ParserEngine.parse = enhanced_parse_with_ooc