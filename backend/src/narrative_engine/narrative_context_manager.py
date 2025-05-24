"""
Narrative Context Manager

This module manages the narrative context, storing and updating the state
of the narrative as it progresses, including character information, world state,
and past events.
"""

from typing import Dict, Any, List, Optional, Set, Union
import logging
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class NarrativeContext:
    """
    Container for narrative context data.
    
    Holds all relevant information about the current state of the narrative,
    including character information, world state, and event history.
    """
    
    def __init__(self, context_id: str = None):
        """
        Initialize a new narrative context.
        
        Args:
            context_id: Optional identifier for this context
        """
        self.id = context_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        
        # Core narrative state
        self.characters = {}
        self.locations = {}
        self.events = []
        self.active_threads = []
        self.completed_threads = []
        self.active_quests = {}
        self.relationships = {}
        
        # Meta information
        self.tension_level = 0.5  # 0.0 to 1.0, default is medium tension
        self.pacing = "normal"    # slow, normal, fast
        self.genre_tone = "neutral"
        self.theme_elements = []
        self.narrative_focus = "balanced"  # character, plot, world, or balanced
        
        # Tracking information
        self.player_choices = []
        self.significant_moments = []
        self.foreshadowing_elements = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "characters": self.characters,
            "locations": self.locations,
            "events": self.events,
            "active_threads": self.active_threads,
            "completed_threads": self.completed_threads,
            "active_quests": self.active_quests,
            "relationships": self.relationships,
            "tension_level": self.tension_level,
            "pacing": self.pacing,
            "genre_tone": self.genre_tone,
            "theme_elements": self.theme_elements,
            "narrative_focus": self.narrative_focus,
            "player_choices": self.player_choices,
            "significant_moments": self.significant_moments,
            "foreshadowing_elements": self.foreshadowing_elements
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeContext':
        """Create a context from dictionary representation."""
        context = cls(context_id=data.get("id"))
        
        # Set attributes from data dictionary
        context.created_at = data.get("created_at", context.created_at)
        context.updated_at = data.get("updated_at", context.updated_at)
        context.characters = data.get("characters", {})
        context.locations = data.get("locations", {})
        context.events = data.get("events", [])
        context.active_threads = data.get("active_threads", [])
        context.completed_threads = data.get("completed_threads", [])
        context.active_quests = data.get("active_quests", {})
        context.relationships = data.get("relationships", {})
        context.tension_level = data.get("tension_level", 0.5)
        context.pacing = data.get("pacing", "normal")
        context.genre_tone = data.get("genre_tone", "neutral")
        context.theme_elements = data.get("theme_elements", [])
        context.narrative_focus = data.get("narrative_focus", "balanced")
        context.player_choices = data.get("player_choices", [])
        context.significant_moments = data.get("significant_moments", [])
        context.foreshadowing_elements = data.get("foreshadowing_elements", [])
        
        return context
    
    def update_character(self, character_id: str, character_data: Dict[str, Any]) -> None:
        """
        Update character information in the context.
        
        Args:
            character_id: Character identifier
            character_data: Updated character data
        """
        if character_id in self.characters:
            # Update existing character
            self.characters[character_id].update(character_data)
        else:
            # Add new character
            self.characters[character_id] = character_data
            
        self.updated_at = datetime.utcnow().isoformat()
    
    def update_location(self, location_id: str, location_data: Dict[str, Any]) -> None:
        """
        Update location information in the context.
        
        Args:
            location_id: Location identifier
            location_data: Updated location data
        """
        if location_id in self.locations:
            # Update existing location
            self.locations[location_id].update(location_data)
        else:
            # Add new location
            self.locations[location_id] = location_data
            
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_event(self, event_data: Dict[str, Any]) -> str:
        """
        Add an event to the context history.
        
        Args:
            event_data: Event data
            
        Returns:
            Event ID
        """
        # Ensure event has an ID and timestamp
        event_id = event_data.get("id", str(uuid.uuid4()))
        event_data["id"] = event_id
        
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.utcnow().isoformat()
            
        # Add event to history
        self.events.append(event_data)
        self.updated_at = datetime.utcnow().isoformat()
        
        return event_id
    
    def add_thread(self, thread_data: Dict[str, Any]) -> str:
        """
        Add a narrative thread to active threads.
        
        Args:
            thread_data: Thread data
            
        Returns:
            Thread ID
        """
        # Ensure thread has an ID
        thread_id = thread_data.get("id", str(uuid.uuid4()))
        thread_data["id"] = thread_id
        
        # Add thread to active threads
        self.active_threads.append(thread_data)
        self.updated_at = datetime.utcnow().isoformat()
        
        return thread_id
    
    def complete_thread(self, thread_id: str, completion_data: Dict[str, Any] = None) -> None:
        """
        Mark a thread as completed and move it to completed threads.
        
        Args:
            thread_id: Thread identifier
            completion_data: Optional data about how the thread was completed
        """
        # Find the thread
        thread = None
        for t in self.active_threads:
            if t.get("id") == thread_id:
                thread = t
                break
                
        if thread is None:
            logger.warning(f"Attempted to complete non-existent thread: {thread_id}")
            return
            
        # Update thread with completion data
        if completion_data:
            thread.update(completion_data)
            
        thread["completed_at"] = datetime.utcnow().isoformat()
        
        # Move from active to completed
        self.active_threads.remove(thread)
        self.completed_threads.append(thread)
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_quest(self, quest_id: str, quest_data: Dict[str, Any]) -> None:
        """
        Add a quest to active quests.
        
        Args:
            quest_id: Quest identifier
            quest_data: Quest data
        """
        self.active_quests[quest_id] = quest_data
        self.updated_at = datetime.utcnow().isoformat()
    
    def update_relationship(self, entity1_id: str, entity2_id: str, relationship_data: Dict[str, Any]) -> None:
        """
        Update a relationship between two entities.
        
        Args:
            entity1_id: First entity ID
            entity2_id: Second entity ID
            relationship_data: Relationship data
        """
        # Create a consistent key for the relationship
        rel_key = f"{min(entity1_id, entity2_id)}:{max(entity1_id, entity2_id)}"
        
        if rel_key in self.relationships:
            # Update existing relationship
            self.relationships[rel_key].update(relationship_data)
        else:
            # Create new relationship
            self.relationships[rel_key] = relationship_data
            
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_player_choice(self, choice_data: Dict[str, Any]) -> None:
        """
        Record a player choice.
        
        Args:
            choice_data: Data about the player's choice
        """
        # Ensure choice has a timestamp
        if "timestamp" not in choice_data:
            choice_data["timestamp"] = datetime.utcnow().isoformat()
            
        self.player_choices.append(choice_data)
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_significant_moment(self, moment_data: Dict[str, Any]) -> None:
        """
        Record a significant narrative moment.
        
        Args:
            moment_data: Data about the significant moment
        """
        # Ensure moment has a timestamp and ID
        if "timestamp" not in moment_data:
            moment_data["timestamp"] = datetime.utcnow().isoformat()
            
        if "id" not in moment_data:
            moment_data["id"] = str(uuid.uuid4())
            
        self.significant_moments.append(moment_data)
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_foreshadowing(self, foreshadowing_data: Dict[str, Any]) -> None:
        """
        Add a foreshadowing element to the narrative.
        
        Args:
            foreshadowing_data: Data about the foreshadowing element
        """
        # Ensure foreshadowing has an ID
        if "id" not in foreshadowing_data:
            foreshadowing_data["id"] = str(uuid.uuid4())
            
        self.foreshadowing_elements.append(foreshadowing_data)
        self.updated_at = datetime.utcnow().isoformat()
    
    def adjust_tension(self, amount: float) -> float:
        """
        Adjust the narrative tension level.
        
        Args:
            amount: Amount to adjust tension by (-1.0 to 1.0)
            
        Returns:
            New tension level
        """
        self.tension_level = max(0.0, min(1.0, self.tension_level + amount))
        self.updated_at = datetime.utcnow().isoformat()
        return self.tension_level
    
    def set_pacing(self, pacing: str) -> None:
        """
        Set the narrative pacing.
        
        Args:
            pacing: Pacing value (slow, normal, fast)
        """
        valid_pacings = ["slow", "normal", "fast"]
        if pacing not in valid_pacings:
            logger.warning(f"Invalid pacing value: {pacing}. Using 'normal' instead.")
            pacing = "normal"
            
        self.pacing = pacing
        self.updated_at = datetime.utcnow().isoformat()
    
    def set_genre_tone(self, tone: str) -> None:
        """
        Set the genre tone.
        
        Args:
            tone: Genre tone value
        """
        self.genre_tone = tone
        self.updated_at = datetime.utcnow().isoformat()
    
    def set_theme_elements(self, elements: List[str]) -> None:
        """
        Set the theme elements.
        
        Args:
            elements: List of theme elements
        """
        self.theme_elements = elements
        self.updated_at = datetime.utcnow().isoformat()
    
    def set_narrative_focus(self, focus: str) -> None:
        """
        Set the narrative focus.
        
        Args:
            focus: Focus value (character, plot, world, balanced)
        """
        valid_focuses = ["character", "plot", "world", "balanced"]
        if focus not in valid_focuses:
            logger.warning(f"Invalid focus value: {focus}. Using 'balanced' instead.")
            focus = "balanced"
            
        self.narrative_focus = focus
        self.updated_at = datetime.utcnow().isoformat()


class NarrativeContextManager:
    """
    Manager for narrative contexts.
    
    Provides functionality for creating, loading, saving, and updating
    narrative contexts, as well as accessing specific aspects of the context.
    """
    
    def __init__(self, storage_service=None):
        """
        Initialize the narrative context manager.
        
        Args:
            storage_service: Optional service for persisting contexts
        """
        self.logger = logging.getLogger("NarrativeContextManager")
        self.storage_service = storage_service
        self.active_contexts = {}  # In-memory cache of active contexts
    
    def create_context(self, context_id: str = None) -> NarrativeContext:
        """
        Create a new narrative context.
        
        Args:
            context_id: Optional identifier for the context
            
        Returns:
            New narrative context
        """
        context = NarrativeContext(context_id)
        self.active_contexts[context.id] = context
        
        # Save to storage if available
        self._save_context(context)
        
        return context
    
    def get_context(self, context_id: str) -> Optional[NarrativeContext]:
        """
        Get a narrative context by ID.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Narrative context or None if not found
        """
        # Check in-memory cache first
        if context_id in self.active_contexts:
            return self.active_contexts[context_id]
            
        # Try to load from storage
        return self._load_context(context_id)
    
    def _save_context(self, context: NarrativeContext) -> bool:
        """
        Save a context to persistent storage.
        
        Args:
            context: Narrative context to save
            
        Returns:
            Success flag
        """
        if not self.storage_service:
            # No storage service available
            return False
            
        try:
            context_dict = context.to_dict()
            self.storage_service.save_narrative_context(context.id, context_dict)
            return True
        except Exception as e:
            self.logger.error(f"Error saving context {context.id}: {e}")
            return False
    
    def _load_context(self, context_id: str) -> Optional[NarrativeContext]:
        """
        Load a context from persistent storage.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Narrative context or None if not found or error
        """
        if not self.storage_service:
            # No storage service available
            return None
            
        try:
            context_dict = self.storage_service.load_narrative_context(context_id)
            
            if not context_dict:
                return None
                
            context = NarrativeContext.from_dict(context_dict)
            
            # Add to active contexts cache
            self.active_contexts[context.id] = context
            
            return context
        except Exception as e:
            self.logger.error(f"Error loading context {context_id}: {e}")
            return None
    
    def update_context(self, context_id: str, update_func) -> Optional[NarrativeContext]:
        """
        Update a context using a function.
        
        Args:
            context_id: Context identifier
            update_func: Function to apply to the context
            
        Returns:
            Updated context or None if error
        """
        context = self.get_context(context_id)
        
        if not context:
            self.logger.warning(f"Attempted to update non-existent context: {context_id}")
            return None
            
        # Apply the update function
        try:
            update_func(context)
        except Exception as e:
            self.logger.error(f"Error updating context {context_id}: {e}")
            return None
            
        # Save the updated context
        self._save_context(context)
        
        return context
    
    def get_recent_events(self, context_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent events from a context.
        
        Args:
            context_id: Context identifier
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        context = self.get_context(context_id)
        
        if not context:
            return []
            
        # Sort events by timestamp and return the most recent ones
        sorted_events = sorted(
            context.events,
            key=lambda e: e.get("timestamp", ""),
            reverse=True
        )
        
        return sorted_events[:limit]
    
    def get_active_threads(self, context_id: str) -> List[Dict[str, Any]]:
        """
        Get active narrative threads from a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            List of active threads
        """
        context = self.get_context(context_id)
        
        if not context:
            return []
            
        return context.active_threads
    
    def get_active_quests(self, context_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get active quests from a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Dictionary of active quests
        """
        context = self.get_context(context_id)
        
        if not context:
            return {}
            
        return context.active_quests
    
    def get_relationship(self, context_id: str, entity1_id: str, entity2_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the relationship between two entities.
        
        Args:
            context_id: Context identifier
            entity1_id: First entity ID
            entity2_id: Second entity ID
            
        Returns:
            Relationship data or None if not found
        """
        context = self.get_context(context_id)
        
        if not context:
            return None
            
        # Create a consistent key for the relationship
        rel_key = f"{min(entity1_id, entity2_id)}:{max(entity1_id, entity2_id)}"
        
        return context.relationships.get(rel_key)
    
    def add_event_to_context(self, context_id: str, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Add an event to a context.
        
        Args:
            context_id: Context identifier
            event_data: Event data
            
        Returns:
            Event ID or None if error
        """
        def _add_event(context):
            return context.add_event(event_data)
            
        context = self.update_context(context_id, lambda c: _add_event(c))
        
        if not context:
            return None
            
        # Return the event ID (should be the last event added)
        return context.events[-1]["id"] if context.events else None
    
    def get_context_summary(self, context_id: str) -> Dict[str, Any]:
        """
        Get a summary of a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Context summary
        """
        context = self.get_context(context_id)
        
        if not context:
            return {
                "error": f"Context {context_id} not found"
            }
            
        # Create a summary of the context
        summary = {
            "id": context.id,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
            "character_count": len(context.characters),
            "location_count": len(context.locations),
            "event_count": len(context.events),
            "active_thread_count": len(context.active_threads),
            "completed_thread_count": len(context.completed_threads),
            "active_quest_count": len(context.active_quests),
            "relationship_count": len(context.relationships),
            "tension_level": context.tension_level,
            "pacing": context.pacing,
            "genre_tone": context.genre_tone,
            "narrative_focus": context.narrative_focus
        }
        
        # Add most recent event if available
        if context.events:
            recent_event = max(context.events, key=lambda e: e.get("timestamp", ""))
            summary["most_recent_event"] = {
                "id": recent_event.get("id", "unknown"),
                "type": recent_event.get("type", "unknown"),
                "timestamp": recent_event.get("timestamp", "unknown")
            }
            
        return summary