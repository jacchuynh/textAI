"""
Object Resolver - Resolves text references to game objects

This module helps identify and resolve text references to game objects
like items, characters, and locations in the game world.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from .vocabulary_manager import vocabulary_manager

logger = logging.getLogger("text_parser.resolver")


class ObjectResolver:
    """
    Resolves text references to game objects like items, characters, locations.
    Works with the VocabularyManager to find matching objects in the game world.
    """
    
    def __init__(self):
        """Initialize the object resolver."""
        self.logger = logging.getLogger("text_parser.resolver")
        self.voc_manager = vocabulary_manager
        
    def resolve_item(self, item_text: str, context: Dict[str, Any] = None) -> Tuple[Optional[str], float]:
        """
        Resolve an item reference to a specific game item.
        
        Args:
            item_text: Text describing the item
            context: Optional context information (location, inventory, etc.)
            
        Returns:
            Tuple of (item_id, confidence) or (None, 0.0) if no match
        """
        if not item_text or not item_text.strip():
            return None, 0.0
            
        item_text = item_text.strip().lower()
        
        # Try exact match first
        item_id = self.voc_manager.get_item_id(item_text)
        if item_id:
            return item_id, 1.0
            
        # Try fuzzy matching by checking if input contains any item names
        best_match = None
        best_score = 0.0
        
        for item_id, synonyms in self.voc_manager.item_synonyms.items():
            for synonym in synonyms:
                if synonym in item_text or item_text in synonym:
                    # Calculate a score based on string similarity
                    score = self._calculate_similarity(item_text, synonym)
                    if score > best_score:
                        best_score = score
                        best_match = item_id
        
        # Check against context if provided
        if context and best_match and "location" in context:
            location_id = context["location"]
            # Logic to boost confidence if item is known to be in location
            # This would be implemented based on game world knowledge
            
        return best_match, best_score if best_match else 0.0
        
    def resolve_character(self, char_text: str, context: Dict[str, Any] = None) -> Tuple[Optional[str], float]:
        """
        Resolve a character reference to a specific game character.
        
        Args:
            char_text: Text describing the character
            context: Optional context information (location, etc.)
            
        Returns:
            Tuple of (character_id, confidence) or (None, 0.0) if no match
        """
        if not char_text or not char_text.strip():
            return None, 0.0
            
        char_text = char_text.strip().lower()
        
        # Try exact match first
        char_id = self.voc_manager.get_character_id(char_text)
        if char_id:
            return char_id, 1.0
            
        # Try fuzzy matching
        best_match = None
        best_score = 0.0
        
        for char_id, synonyms in self.voc_manager.character_synonyms.items():
            for synonym in synonyms:
                if synonym in char_text or char_text in synonym:
                    # Calculate a score based on string similarity
                    score = self._calculate_similarity(char_text, synonym)
                    if score > best_score:
                        best_score = score
                        best_match = char_id
        
        # Check against context if provided
        if context and best_match and "location" in context:
            location_id = context["location"]
            # Logic to boost confidence if character is known to be in location
            # This would be implemented based on game world knowledge
            
        return best_match, best_score if best_match else 0.0
        
    def resolve_location(self, loc_text: str, context: Dict[str, Any] = None) -> Tuple[Optional[str], float]:
        """
        Resolve a location reference to a specific game location.
        
        Args:
            loc_text: Text describing the location
            context: Optional context information (current location, etc.)
            
        Returns:
            Tuple of (location_id, confidence) or (None, 0.0) if no match
        """
        if not loc_text or not loc_text.strip():
            return None, 0.0
            
        loc_text = loc_text.strip().lower()
        
        # Try exact match first
        loc_id = self.voc_manager.get_location_id(loc_text)
        if loc_id:
            return loc_id, 1.0
            
        # Try fuzzy matching
        best_match = None
        best_score = 0.0
        
        for loc_id, synonyms in self.voc_manager.location_synonyms.items():
            for synonym in synonyms:
                if synonym in loc_text or loc_text in synonym:
                    # Calculate a score based on string similarity
                    score = self._calculate_similarity(loc_text, synonym)
                    if score > best_score:
                        best_score = score
                        best_match = loc_id
        
        # Check against context if provided
        if context and best_match and "current_location" in context:
            current_loc = context["current_location"]
            # Logic to boost confidence if location is connected to current location
            # This would be implemented based on game world knowledge
            
        return best_match, best_score if best_match else 0.0
        
    def resolve_direction(self, dir_text: str) -> Tuple[Optional[str], float]:
        """
        Resolve a direction reference to a canonical direction.
        
        Args:
            dir_text: Text describing the direction
            
        Returns:
            Tuple of (direction, confidence) or (None, 0.0) if no match
        """
        if not dir_text or not dir_text.strip():
            return None, 0.0
            
        dir_text = dir_text.strip().lower()
        
        # Try exact match first
        direction = self.voc_manager.get_canonical_direction(dir_text)
        if direction:
            return direction, 1.0
            
        # Try fuzzy matching
        for canonical, synonyms in self.voc_manager.direction_synonyms.items():
            if dir_text in synonyms or canonical.startswith(dir_text):
                return canonical, 0.8
                
        return None, 0.0
        
    def find_disambiguation_candidates(self, text: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find possible interpretations for ambiguous input.
        
        Args:
            text: Input text to disambiguate
            context: Current game context
            
        Returns:
            List of candidate interpretations with confidence scores
        """
        candidates = []
        text = text.strip().lower()
        
        # Check for item interpretations
        for item_id, synonyms in self.voc_manager.item_synonyms.items():
            for synonym in synonyms:
                if synonym in text or text in synonym:
                    score = self._calculate_similarity(text, synonym)
                    if score > 0.5:  # Threshold for being considered
                        candidates.append({
                            "type": "item",
                            "id": item_id,
                            "match": synonym,
                            "confidence": score,
                            "action": "examine" if score > 0.8 else None  # Suggest action if high confidence
                        })
        
        # Check for character interpretations
        for char_id, synonyms in self.voc_manager.character_synonyms.items():
            for synonym in synonyms:
                if synonym in text or text in synonym:
                    score = self._calculate_similarity(text, synonym)
                    if score > 0.5:
                        candidates.append({
                            "type": "character",
                            "id": char_id,
                            "match": synonym,
                            "confidence": score,
                            "action": "talk" if score > 0.8 else None
                        })
        
        # Check for location interpretations
        for loc_id, synonyms in self.voc_manager.location_synonyms.items():
            for synonym in synonyms:
                if synonym in text or text in synonym:
                    score = self._calculate_similarity(text, synonym)
                    if score > 0.5:
                        candidates.append({
                            "type": "location",
                            "id": loc_id,
                            "match": synonym,
                            "confidence": score,
                            "action": "go" if score > 0.8 else None
                        })
        
        # Sort by confidence score (highest first)
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        
        return candidates
        
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate string similarity between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Similarity score (0.0 - 1.0)
        """
        # Simple implementation - can be improved with more sophisticated algorithms
        if s1 == s2:
            return 1.0
            
        if s1 in s2:
            return 0.9
            
        if s2 in s1:
            return 0.8
            
        # Check for prefix/suffix matches
        if s1.startswith(s2) or s1.endswith(s2):
            return 0.7
            
        if s2.startswith(s1) or s2.endswith(s1):
            return 0.6
            
        # Check for substring
        if len(s1) > 3 and len(s2) > 3:
            if s1[:3] == s2[:3]:  # First 3 chars match
                return 0.5
                
        return 0.0  # No match


# Create a global instance of the object resolver
object_resolver = ObjectResolver()