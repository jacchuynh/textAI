"""
Event Bus System

This module provides a central event bus for publishing and subscribing to game events.
It allows different systems to communicate with each other in a decoupled way.
"""

from typing import Dict, List, Any, Callable, Optional
import logging
from enum import Enum, auto
import uuid

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Types of events that can be published on the event bus."""
    GAME_TIME_PROGRESSED = "GAME_TIME_PROGRESSED"
    SCHEDULED_EVENT_TRIGGERED = "SCHEDULED_EVENT_TRIGGERED"
    WEATHER_CHANGED = "WEATHER_CHANGED"
    SEASON_CHANGED = "SEASON_CHANGED"
    TIME_BLOCK_CHANGED = "TIME_BLOCK_CHANGED"
    SPELL_EXPIRED = "SPELL_EXPIRED"
    BUFF_EXPIRED = "BUFF_EXPIRED"
    RITUAL_COMPLETED = "RITUAL_COMPLETED"
    CRAFTING_COMPLETED = "CRAFTING_COMPLETED"
    RESOURCE_REGENERATED = "RESOURCE_REGENERATED"
    

class GameEvent:
    """
    Represents an event in the game system.
    Events have a type, context, and optional source and target identifiers.
    """
    def __init__(
        self,
        event_type: EventType,
        context: Dict[str, Any],
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        event_id: Optional[str] = None
    ):
        """
        Initialize a new game event.
        
        Args:
            event_type: Type of the event
            context: Dictionary containing event details
            source_id: ID of the entity that generated the event (optional)
            target_id: ID of the entity that is the target of the event (optional)
            event_id: Unique identifier for the event (generated if not provided)
        """
        self.event_type = event_type
        self.context = context
        self.source_id = source_id
        self.target_id = target_id
        self.event_id = event_id or str(uuid.uuid4())
    
    def __str__(self) -> str:
        """String representation of the event."""
        return (f"GameEvent(type={self.event_type}, "
                f"source={self.source_id}, target={self.target_id})")


EventCallback = Callable[[GameEvent], None]


class EventBus:
    """
    Central event bus for the game system.
    Allows systems to publish and subscribe to events.
    """
    def __init__(self):
        """Initialize the event bus with empty subscriber lists."""
        self._subscribers: Dict[EventType, List[EventCallback]] = {}
        
        # Initialize subscriber lists for all event types
        for event_type in EventType:
            self._subscribers[event_type] = []
    
    def subscribe(self, event_type: EventType, callback: EventCallback) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Function to call when an event of this type is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")
    
    def unsubscribe(self, event_type: EventType, callback: EventCallback) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of events to unsubscribe from
            callback: Function to remove from subscribers
            
        Returns:
            True if the callback was removed, False if it wasn't found
        """
        if event_type not in self._subscribers:
            return False
        
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from {event_type}")
            return True
        
        return False
    
    def publish(self, event: GameEvent) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        if event.event_type not in self._subscribers:
            logger.warning(f"No subscribers for event type {event.event_type}")
            return
        
        logger.debug(f"Publishing event: {event}")
        
        # Notify all subscribers
        for callback in self._subscribers[event.event_type]:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")


# Create a global event bus instance
event_bus = EventBus()