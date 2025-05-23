"""
Text Parser Module

This module provides natural language parsing capabilities for the AI Game Master,
enabling it to understand and interpret player commands in a flexible way.
"""

from .parser_engine import ParserEngine, parse_input, ParsedCommand
from .vocabulary_manager import VocabularyManager
from .object_resolver import ObjectResolver

__all__ = [
    'ParserEngine', 
    'parse_input', 
    'ParsedCommand', 
    'VocabularyManager',
    'ObjectResolver'
]