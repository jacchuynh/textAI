"""
Event Bus Module

This module provides a centralized event bus system for the narrative engine
and other game systems to communicate through events. It supports event
publishing, subscription, and asynchronous processing.
"""

from typing import Dict, Any, List, Optional, Set, Union, Callable
import logging
import json
from datetime import datetime
import uuid
import asyncio
from collections import defaultdict
import threading
import queue

logger = logging.getLogger(__name__)

class Event:
    """
    Represents an event in the system.
    
    Events are the primary means of communication between different components
    of the system, allowing for decoupled interactions.
    """
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None, source: str = None):
        """
        Initialize a new event.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Source of the event
        """
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.data = data or {}
        self.source = source
        self.timestamp = datetime.utcnow().isoformat()
        self.processed = False
        self.processed_by = set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp,
            "processed": self.processed,
            "processed_by": list(self.processed_by)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create an event from dictionary representation."""
        event = cls(
            event_type=data["type"],
            data=data.get("data", {}),
            source=data.get("source")
        )
        
        # Set additional attributes
        event.id = data["id"]
        event.timestamp = data["timestamp"]
        event.processed = data.get("processed", False)
        event.processed_by = set(data.get("processed_by", []))
        
        return event
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"Event({self.type}, id={self.id}, source={self.source})"


class EventBus:
    """
    Central event bus for the system.
    
    Manages event subscriptions, event publishing, and ensures
    events are properly routed to interested subscribers.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers = defaultdict(list)
        self.global_subscribers = []
        self.event_history = []
        self.max_history_size = 1000  # Maximum number of events to keep in history
        
        # Set up asynchronous processing
        self.async_enabled = True
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.stop_processing = False
        
        # For integration with Celery
        self.celery_integration = None
    
    def set_celery_integration(self, celery_integration) -> None:
        """
        Set the Celery integration for asynchronous event processing.
        
        Args:
            celery_integration: Celery integration object
        """
        self.celery_integration = celery_integration
    
    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type}")
    
    def subscribe_to_all(self, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to all events.
        
        Args:
            callback: Function to call when any event occurs
        """
        self.global_subscribers.append(callback)
        logger.debug("Subscribed to all events")
    
    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> bool:
        """
        Unsubscribe from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
            
        Returns:
            Success flag
        """
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event type: {event_type}")
                return True
            except ValueError:
                logger.warning(f"Callback not found in subscribers for event type: {event_type}")
        return False
    
    def unsubscribe_from_all(self, callback: Callable[[Event], None]) -> bool:
        """
        Unsubscribe from all events.
        
        Args:
            callback: Function to remove from global subscribers
            
        Returns:
            Success flag
        """
        try:
            self.global_subscribers.remove(callback)
            logger.debug("Unsubscribed from all events")
            return True
        except ValueError:
            logger.warning("Callback not found in global subscribers")
            return False
    
    def publish(self, event: Union[Event, Dict[str, Any]], async_processing: bool = True) -> str:
        """
        Publish an event to the bus.
        
        Args:
            event: Event or event data to publish
            async_processing: Whether to process the event asynchronously
            
        Returns:
            Event ID
        """
        # Convert dict to Event if necessary
        if isinstance(event, dict):
            if "type" not in event:
                raise ValueError("Event dictionary must contain 'type' key")
                
            event = Event(
                event_type=event["type"],
                data=event.get("data", {}),
                source=event.get("source")
            )
            
        # Add to event history
        self.event_history.append(event)
        
        # Trim history if needed
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]
            
        # Process event
        if async_processing and self.async_enabled:
            # Add to processing queue
            self.processing_queue.put(event)
            
            # Start processing thread if not running
            if self.processing_thread is None or not self.processing_thread.is_alive():
                self.start_processing_thread()
                
            # If Celery integration is available, also process with Celery
            if self.celery_integration:
                self._process_with_celery(event)
        else:
            # Process synchronously
            self._process_event(event)
            
        return event.id
    
    def _process_event(self, event: Event) -> None:
        """
        Process an event by notifying all relevant subscribers.
        
        Args:
            event: Event to process
        """
        # Notify specific subscribers
        for callback in self.subscribers.get(event.type, []):
            try:
                callback(event)
                event.processed_by.add(str(callback))
            except Exception as e:
                logger.error(f"Error in event subscriber callback: {e}")
                
        # Notify global subscribers
        for callback in self.global_subscribers:
            try:
                callback(event)
                event.processed_by.add(str(callback))
            except Exception as e:
                logger.error(f"Error in global event subscriber callback: {e}")
                
        # Mark as processed
        event.processed = True
    
    def _process_with_celery(self, event: Event) -> None:
        """
        Process an event using Celery for asynchronous handling.
        
        Args:
            event: Event to process
        """
        if not self.celery_integration:
            return
            
        try:
            # Convert event to dictionary for Celery
            event_dict = event.to_dict()
            
            # Use Celery to process the event asynchronously
            asyncio.create_task(self.celery_integration.process_event_queue_async([event_dict]))
            
        except Exception as e:
            logger.error(f"Error in Celery event processing: {e}")
    
    def start_processing_thread(self) -> None:
        """Start the asynchronous event processing thread."""
        self.stop_processing = False
        self.processing_thread = threading.Thread(target=self._processing_worker, daemon=True)
        self.processing_thread.start()
    
    def stop_processing_thread(self) -> None:
        """Stop the asynchronous event processing thread."""
        self.stop_processing = True
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
    
    def _processing_worker(self) -> None:
        """Worker function for the event processing thread."""
        while not self.stop_processing:
            try:
                # Get event from queue with timeout
                try:
                    event = self.processing_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                    
                # Process the event
                self._process_event(event)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in event processing worker: {e}")
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """
        Get an event by ID from the event history.
        
        Args:
            event_id: Event identifier
            
        Returns:
            Event or None if not found
        """
        for event in self.event_history:
            if event.id == event_id:
                return event
                
        return None
    
    def get_events_by_type(self, event_type: str, limit: int = None) -> List[Event]:
        """
        Get events of a specific type from the event history.
        
        Args:
            event_type: Type of events to get
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = [e for e in self.event_history if e.type == event_type]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit is not None:
            events = events[:limit]
            
        return events
    
    def get_events_by_source(self, source: str, limit: int = None) -> List[Event]:
        """
        Get events from a specific source from the event history.
        
        Args:
            source: Source of events to get
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = [e for e in self.event_history if e.source == source]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit is not None:
            events = events[:limit]
            
        return events
    
    def get_recent_events(self, limit: int = 10) -> List[Event]:
        """
        Get recent events from the event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        # Sort by timestamp (newest first)
        events = sorted(self.event_history, key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    def clear_history(self) -> None:
        """Clear the event history."""
        self.event_history = []


# Singleton instance for global use
_event_bus = None

def get_event_bus() -> EventBus:
    """
    Get the global event bus instance.
    
    Returns:
        Global event bus instance
    """
    global _event_bus
    
    if _event_bus is None:
        _event_bus = EventBus()
        
    return _event_bus