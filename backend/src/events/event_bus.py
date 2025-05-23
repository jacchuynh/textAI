"""
Event Bus System

This module provides the event bus that allows game components
to communicate through an event-driven architecture.
"""

import uuid
import logging
from enum import Enum, auto
from typing import Dict, Any, List, Callable, Set
from datetime import datetime


class EventType(Enum):
    """Types of events that can occur in the game."""
    PLAYER_JOINED = auto()
    PLAYER_LEFT = auto()
    LOCATION_ENTERED = auto()
    LOCATION_EXITED = auto()
    NPC_INTERACTION = auto()
    ITEM_ACQUIRED = auto()
    ITEM_USED = auto()
    COMBAT_STARTED = auto()
    COMBAT_ENDED = auto()
    COMBAT_ROUND = auto()
    QUEST_STARTED = auto()
    QUEST_PROGRESSED = auto()
    QUEST_COMPLETED = auto()
    DOMAIN_ADVANCED = auto()
    PLAYER_CHOICE = auto()
    SYSTEM_EVENT = auto()


class GameEvent:
    """
    Represents an event that occurs in the game.
    
    Events are used to communicate between different components
    of the game system in a decoupled manner.
    """
    
    def __init__(self, 
                type: EventType, 
                source_id: str,
                context: Dict[str, Any] = None,
                tags: List[str] = None):
        """
        Initialize a game event.
        
        Args:
            type: Type of event
            source_id: ID of the component/entity that generated the event
            context: Additional context data for the event
            tags: Tags for categorizing the event
        """
        self.id = str(uuid.uuid4())
        self.type = type
        self.source_id = source_id
        self.context = context or {}
        self.tags = tags or []
        self.timestamp = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"GameEvent(id={self.id}, type={self.type.name}, source={self.source_id}, tags={self.tags})"
    
    def has_tag(self, tag: str) -> bool:
        """Check if event has a specific tag."""
        return tag in self.tags
    
    def get_context_value(self, key: str, default=None) -> Any:
        """Get a value from the context, with a default if not found."""
        return self.context.get(key, default)


class EventBus:
    """
    Central event dispatcher for the game system.
    
    This class manages the registration of event handlers and
    dispatches events to registered handlers.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.handlers: Dict[EventType, Set[Callable]] = {}
        self.logger = logging.getLogger("EventBus")
        
        # Recent events cache
        self.recent_events: List[GameEvent] = []
        self.max_recent_events = 100
    
    def subscribe(self, event_type: EventType, handler: Callable[[GameEvent], None]) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event occurs
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = set()
        
        self.handlers[event_type].add(handler)
        self.logger.debug(f"Handler {handler.__name__} subscribed to {event_type.name}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[GameEvent], None]) -> None:
        """
        Unsubscribe a handler from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to unsubscribe
        """
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            self.logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type.name}")
    
    def publish(self, event: GameEvent) -> None:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event: Event to publish
        """
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler {handler.__name__}: {str(e)}")
        
        # Add to recent events
        self.recent_events.append(event)
        
        # Trim if needed
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events = self.recent_events[-self.max_recent_events:]
        
        self.logger.debug(f"Published event: {event}")
    
    def get_recent_events(self, 
                        event_type: EventType = None, 
                        source_id: str = None,
                        tag: str = None,
                        limit: int = 10) -> List[GameEvent]:
        """
        Get recent events, optionally filtered.
        
        Args:
            event_type: Filter by event type
            source_id: Filter by source ID
            tag: Filter by tag
            limit: Maximum number of events to return
            
        Returns:
            List of recent events matching filters
        """
        filtered_events = self.recent_events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.type == event_type]
        
        if source_id:
            filtered_events = [e for e in filtered_events if e.source_id == source_id]
        
        if tag:
            filtered_events = [e for e in filtered_events if e.has_tag(tag)]
        
        # Return most recent events first, up to limit
        return filtered_events[-limit:][::-1]


# Singleton instance
event_bus = EventBus()