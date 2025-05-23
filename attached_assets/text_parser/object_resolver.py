"""
Object resolution for the parser engine.

This module handles resolving noun phrases to actual game objects or monsters.
"""
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from game_context import game_context
from .vocabulary import VocabularyManager


class DisambiguationNeeded(Exception):
    """Exception raised when disambiguation is needed."""
    def __init__(self, candidates: List[Dict[str, Any]]):
        self.candidates = candidates
        super().__init__("Multiple objects match the description. Disambiguation needed.")


class ObjectResolver:
    """
    Resolves noun phrases to game objects or monsters.
    
    This class handles finding game objects that match noun phrases,
    including disambiguation when multiple objects match.
    """
    
    def __init__(self, vocabulary_manager: VocabularyManager):
        """
        Initialize the object resolver.
        
        Args:
            vocabulary_manager: Vocabulary manager for noun lookups
        """
        self.vocabulary = vocabulary_manager
    
    def resolve_object(self, 
                      noun: str, 
                      adjectives: List[str] = None, 
                      entity_types: List[str] = None,
                      context: Dict[str, Any] = None) -> Union[str, Dict[str, Any]]:
        """
        Resolve a noun phrase to a game object or monster ID.
        
        Args:
            noun: The main noun
            adjectives: Optional list of adjectives
            entity_types: Optional list of entity types to limit search to ("object", "monster", "npc")
            context: Optional context information
            
        Returns:
            Game object/monster ID, or dictionary with disambiguation info if needed
        """
        adjectives = adjectives or []
        
        # Get canonical form of noun
        canonical_noun = self.vocabulary.get_canonical_noun(noun)
        
        # Get all objects in scope (current location + inventory + monsters)
        objects_in_scope = self._get_objects_in_scope(entity_types)
        
        # Filter objects by noun (using canonical form)
        candidates = self._filter_by_noun(objects_in_scope, canonical_noun)
        
        # If adjectives provided, filter further
        if adjectives and candidates:
            candidates = self._filter_by_adjectives(candidates, adjectives)
        
        # If no candidates found, try last word of noun (for multi-word monsters like "Vine Weasel")
        if not candidates and ' ' in noun:
            last_word = noun.split()[-1]
            candidates = self._filter_by_noun(objects_in_scope, last_word)
            # Filter by adjectives if provided
            if adjectives and candidates:
                candidates = self._filter_by_adjectives(candidates, adjectives)
        
        # Handle disambiguation
        if len(candidates) > 1:
            # First try to disambiguate by recency/context
            best_candidate = self._disambiguate_by_context(candidates, context)
            if best_candidate:
                return best_candidate['id']
            
            # If context doesn't help, return disambiguation info
            return {
                "disambiguation_required": True,
                "candidates": self.get_disambiguation_options(candidates)
            }
        elif candidates:
            # Single match found
            object_id = candidates[0]['id']
            
            # Update reference history
            entity_type = "monsters" if candidates[0].get("threat_tier") else "objects"
            game_context.reference_entity(object_id, entity_type)
            
            return object_id
        
        # No matches found
        return None
    
    def _get_objects_in_scope(self, entity_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get all objects in the current scope.
        
        Args:
            entity_types: Optional list of entity types to limit search to
                        ("object", "monster", "npc")
            
        Returns:
            List of game objects and monsters in scope
        """
        objects_in_scope = []
        
        # Get current location for scoping
        location_id = game_context.get_current_location()
        
        # Include objects if not limited or explicitly included
        if not entity_types or "object" in entity_types:
            # Objects at current location
            objects_in_scope.extend(game_context.get_objects_at_location(location_id))
            
            # Objects in inventory
            player_id = game_context.get_player_id()
            objects_in_scope.extend(game_context.get_player_inventory(player_id))
        
        # Include monsters if not limited or explicitly included
        if not entity_types or "monster" in entity_types:
            objects_in_scope.extend(game_context.get_monsters_at_location(location_id))
        
        # Include NPCs if implemented and requested
        # if not entity_types or "npc" in entity_types:
        #     objects_in_scope.extend(game_context.get_npcs_at_location(location_id))
        
        return objects_in_scope
    
    def _filter_by_noun(self, objects: List[Dict[str, Any]], noun: str) -> List[Dict[str, Any]]:
        """
        Filter objects by noun.
        
        Args:
            objects: List of game objects
            noun: The noun to filter by
            
        Returns:
            Filtered list of objects
        """
        noun_lower = noun.lower()
        
        # Filter objects by name, including aliases
        return [
            obj for obj in objects
            if (obj.get('name', '').lower() == noun_lower or
                noun_lower in [alias.lower() for alias in obj.get('aliases', [])])
        ]
    
    def _filter_by_adjectives(self, objects: List[Dict[str, Any]], adjectives: List[str]) -> List[Dict[str, Any]]:
        """
        Filter objects by adjectives.
        
        Args:
            objects: List of game objects
            adjectives: List of adjectives to filter by
            
        Returns:
            Filtered list of objects
        """
        filtered = []
        for obj in objects:
            # Get object adjectives
            obj_adjectives = set(adj.lower() for adj in obj.get('adjectives', []))
            
            # Check if all specified adjectives are in object adjectives
            if all(adj.lower() in obj_adjectives for adj in adjectives):
                filtered.append(obj)
            # Also check if any specified adjective is in the name
            elif any(adj.lower() in obj.get('name', '').lower() for adj in adjectives):
                filtered.append(obj)
            # Consider threat tier (e.g., "minion goblin")
            elif any(adj.lower() == obj.get('threat_tier', '').lower() for adj in adjectives):
                filtered.append(obj)
            # Consider category (e.g., "beast monster")
            elif any(adj.lower() == obj.get('category', '').lower() for adj in adjectives):
                filtered.append(obj)
        
        return filtered
    
    def _disambiguate_by_context(self, 
                               candidates: List[Dict[str, Any]], 
                               context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Try to disambiguate based on context.
        
        Args:
            candidates: List of candidate objects
            context: Optional context information
            
        Returns:
            Best candidate or None if can't disambiguate
        """
        if not context:
            return None
            
        # Check if in combat and one candidate is the current enemy
        if context.get("in_combat") and context.get("last_enemy"):
            for candidate in candidates:
                if candidate.get("id") == context.get("last_enemy"):
                    return candidate
        
        # Try recently referenced entities of matching type
        if any("threat_tier" in c for c in candidates):
            # These are monsters
            recent_monster = context.get("recently_referenced", {}).get("monsters")
            if recent_monster:
                for candidate in candidates:
                    if candidate.get("id") == recent_monster:
                        return candidate
        else:
            # These are objects
            recent_object = context.get("recently_referenced", {}).get("objects")
            if recent_object:
                for candidate in candidates:
                    if candidate.get("id") == recent_object:
                        return candidate
        
        # Prefer enemies in combat over passive monsters
        combat_candidates = [c for c in candidates if c.get("in_combat", False)]
        if combat_candidates:
            return combat_candidates[0]
        
        # No contextual match found
        return None
    
    def get_disambiguation_options(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get disambiguation options for multiple matching objects.
        
        Args:
            candidates: List of candidate objects
            
        Returns:
            List of simplified objects for disambiguation
        """
        options = []
        for obj in candidates:
            option = {
                'id': obj['id'],
                'name': obj['name'],
                'adjectives': obj.get('adjectives', []),
            }
            
            # Add threat_tier if it's a monster
            if 'threat_tier' in obj:
                option['threat_tier'] = obj['threat_tier']
                
            # Add description (truncated if needed)
            if 'description' in obj:
                option['description'] = obj.get('description', '')[:50]
                if len(obj.get('description', '')) > 50:
                    option['description'] += '...'
                    
            # Add location
            if 'location' in obj:
                option['location'] = obj['location']
                
            options.append(option)
            
        return options