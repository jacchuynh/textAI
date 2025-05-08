"""
Storage module for persisting game data.
"""

from .character_storage import get_character, save_character, delete_character, list_characters

__all__ = ["get_character", "save_character", "delete_character", "list_characters"]