"""
Event bus system for game events.

This module provides the core event infrastructure for the game engine,
allowing different systems to communicate via a publish-subscribe pattern.
"""
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from collections import defaultdict
from enum import Enum, auto


class EventType(Enum):
    """Event types for the game engine."""
    # Character events
    CHARACTER_CREATED = auto()
    CHARACTER_UPDATED = auto()
    CHARACTER_DELETED = auto()
    LEVEL_UP = auto()
    DOMAIN_INCREASED = auto()
    TAG_INCREASED = auto()
    
    # Action events
    ACTION_PERFORMED = auto()
    SKILL_CHECK = auto()
    DOMAIN_CHECK = auto()
    
    # Inventory events
    ITEM_ACQUIRED = auto()
    ITEM_USED = auto()
    ITEM_CRAFTED = auto()
    ITEM_SOLD = auto()
    
    # Combat events
    COMBAT_STARTED = auto()
    COMBAT_ENDED = auto()
    ATTACK_PERFORMED = auto()
    DAMAGE_DEALT = auto()
    DAMAGE_TAKEN = auto()
    ENEMY_DEFEATED = auto()
    CHARACTER_DEFEATED = auto()
    
    # NPC events
    NPC_INTERACTION = auto()
    NPC_RELATIONSHIP_CHANGED = auto()
    
    # Location events
    LOCATION_DISCOVERED = auto()
    LOCATION_ENTERED = auto()
    LOCATION_EXITED = auto()
    
    # Quest events
    QUEST_STARTED = auto()
    QUEST_UPDATED = auto()
    QUEST_COMPLETED = auto()
    QUEST_FAILED = auto()
    
    # Game session events
    GAME_STARTED = auto()
    GAME_SAVED = auto()
    GAME_LOADED = auto()
    GAME_ENDED = auto()
    
    # System events
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


class GameEvent:
    """
    Game event object that encapsulates event information.
    
    Attributes:
        type: The type of the event
        actor: The entity that triggered the event (character, NPC, system, etc.)
        context: Additional contextual information about the event
        metadata: Additional metadata about the event
        timestamp: The time when the event occurred
    """
    def __init__(self, 
                 type: EventType, 
                 actor: str, 
                 context: Optional[Dict[str, Any]] = None, 
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a new game event.
        
        Args:
            type: The type of the event
            actor: The entity that triggered the event
            context: Additional contextual information about the event
            metadata: Additional metadata about the event
        """
        self.type = type
        self.actor = actor
        self.context = context or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "type": self.type.name,
            "actor": self.actor,
            "context": self.context,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """String representation of the event."""
        return (f"GameEvent({self.type.name}, actor={self.actor}, "
                f"context={self.context}, timestamp={self.timestamp})")


class EventLogger:
    """
    Logger for game events.
    
    Attributes:
        history: List of events that have been logged
    """
    def __init__(self, max_history: int = 1000):
        """
        Initialize a new event logger.
        
        Args:
            max_history: Maximum number of events to keep in history
        """
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history

    def log(self, event: GameEvent) -> None:
        """
        Log an event.
        
        Args:
            event: The event to log
        """
        self.history.append(event.to_dict())
        # Trim history if it exceeds max size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
    def get_history(self, 
                    event_types: Optional[List[EventType]] = None, 
                    actor: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get filtered event history.
        
        Args:
            event_types: Optional filter for event types
            actor: Optional filter for actor
            limit: Optional limit on number of events returned
            
        Returns:
            Filtered list of events
        """
        filtered_history = self.history
        
        if event_types:
            event_type_names = [et.name for et in event_types]
            filtered_history = [
                e for e in filtered_history 
                if e["type"] in event_type_names
            ]
            
        if actor:
            filtered_history = [
                e for e in filtered_history 
                if e["actor"] == actor
            ]
            
        if limit and limit > 0:
            filtered_history = filtered_history[-limit:]
            
        return filtered_history
    
    def clear(self) -> None:
        """Clear all event history."""
        self.history = []


class GameEventBus:
    """
    Event bus for game events using a publish-subscribe pattern.
    
    Attributes:
        subscribers: Dictionary mapping event types to callbacks
        logger: Logger for events published to the bus
    """
    def __init__(self):
        """Initialize a new game event bus."""
        self.subscribers: Dict[EventType, List[Callable[[GameEvent], None]]] = defaultdict(list)
        self.logger = EventLogger()

    def subscribe(self, event_type: EventType, callback: Callable[[GameEvent], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: The event type to subscribe to
            callback: The callback to invoke when an event of this type is published
        """
        self.subscribers[event_type].append(callback)
        
    def unsubscribe(self, event_type: EventType, callback: Callable[[GameEvent], None]) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback to remove
            
        Returns:
            True if the callback was removed, False otherwise
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            return True
        return False

    def publish(self, event: GameEvent) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Log the event
        self.logger.log(event)
        
        # Notify subscribers
        for callback in self.subscribers[event.type]:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event subscriber: {e}")
                
    def get_history(self, 
                    event_types: Optional[List[EventType]] = None, 
                    actor: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get filtered event history.
        
        Args:
            event_types: Optional filter for event types
            actor: Optional filter for actor
            limit: Optional limit on number of events returned
            
        Returns:
            Filtered list of events from the logger
        """
        return self.logger.get_history(event_types, actor, limit)


# Global event bus instance
event_bus = GameEventBus()