"""
Event bus system for game events.
... (rest of your event_bus.py code from previous response) ...
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional, Union, Set
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
    
    # Quest events (can be seen as a type of narrative branch)
    QUEST_STARTED = auto()
    QUEST_UPDATED = auto()
    QUEST_COMPLETED = auto()
    QUEST_FAILED = auto()

    # Narrative Branch Events -- NEW / ENSURED --
    NARRATIVE_BRANCH_AVAILABLE = auto()
    NARRATIVE_BRANCH_CREATED = auto()   # Player accepted/started a branch
    NARRATIVE_BRANCH_UPDATED = auto()   # Progress/stage change
    NARRATIVE_BRANCH_COMPLETED = auto()
    NARRATIVE_BRANCH_FAILED = auto()
    # -- END NEW / ENSURED --
    
    # Game session events
    GAME_STARTED = auto()
    GAME_SAVED = auto()
    GAME_LOADED = auto()
    GAME_ENDED = auto()
    
    # Economy events
    TRANSACTION_COMPLETED = auto()
    ITEM_PRICE_CHANGED = auto()
    SHOP_INVENTORY_UPDATED = auto()
    
    # Basebuilding events
    STRUCTURE_BUILT = auto()
    STRUCTURE_UPGRADED = auto()
    RESOURCE_GATHERED = auto()
    
    # Kingdom management events
    TERRITORY_ACQUIRED = auto()
    LAW_ENACTED = auto()
    DIPLOMATIC_RELATION_CHANGED = auto()
    
    # Crafting events
    RECIPE_LEARNED = auto()
    ITEM_CRAFTED_SUCCESS = auto()
    ITEM_CRAFTED_FAILURE = auto()
    MATERIAL_GATHERED = auto()

    # World State and Global Events
    WORLD_STATE_CHANGED = auto()        # Generic event for any world state update
    GLOBAL_ECONOMIC_SHIFT = auto()      # E.g., start of a recession or boom
    GLOBAL_POLITICAL_SHIFT = auto()   # E.g., declaration of war, peace treaty
    SEASONAL_EVENT_TRIGGERED = auto() # E.g., first snow, harvest festival announcement
    GLOBAL_THREAT_EVENT = auto()      # E.g., news of a spreading plague, dragon sighting
    AMBIENT_WORLD_NARRATIVE = auto()  # For general observations about the world state
    
    # System events
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    
    # Wildcard for all events
    WILDCARD = "*"
    
    @classmethod
    def from_string(cls, event_type_str: str) -> 'EventType':
        if event_type_str == "*":
            return cls.WILDCARD
        try: # Try direct name match first
            return cls[event_type_str.upper()]
        except KeyError: # Fallback to iterating if mixed case or different naming
            for event_type in cls:
                if event_type.name == event_type_str:
                    return event_type
            raise ValueError(f"Invalid event type: {event_type_str}")


class GameEvent:
    """
    Game event object that encapsulates event information.
    
    Attributes:
        id: Unique identifier for the event
        type: The type of the event
        actor: The entity that triggered the event (character, NPC, system, etc.)
        context: Additional contextual information about the event
        metadata: Additional metadata about the event
        tags: List of tags for categorizing the event
        effects: List of effects resulting from the event
        timestamp: The time when the event occurred
    """
    def __init__(self, 
                 type: Union[EventType, str], 
                 actor: str, 
                 context: Optional[Dict[str, Any]] = None, 
                 metadata: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 effects: Optional[List[Dict[str, Any]]] = None,
                 game_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        
        if isinstance(type, str):
            try:
                self.type = EventType.from_string(type)
            except ValueError:
                # print(f"Warning: Unknown event type string '{type}', treating as custom event type string.")
                self.type = type # Store as string if not a valid EventType name
        elif isinstance(type, EventType):
            self.type = type
        else:
            raise TypeError(f"Event type must be EventType enum or string, got {type.__class__.__name__}")
            
        self.actor = actor
        self.context = context or {}
        self.metadata = metadata or {}
        self.tags = tags or []
        self.effects = effects or []
        self.game_id = game_id
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        type_repr = self.type.name if isinstance(self.type, EventType) else str(self.type)
        return {
            "id": self.id, "type": type_repr, "actor": self.actor, "context": self.context,
            "metadata": self.metadata, "tags": self.tags, "effects": self.effects,
            "game_id": self.game_id, "timestamp": self.timestamp
        }
    
    def summarize(self) -> Dict[str, Any]:
        type_repr = self.type.name if isinstance(self.type, EventType) else str(self.type)
        summary_str = f"{self.actor} triggered {type_repr}"
        key_context_items = ['location', 'target', 'result', 'success', 'amount', 'duration', 'change', 'new_value', 'threat', 'season', 'branch_name', 'reason']
        context_summary_parts = [f"{k}='{v}'" for k, v in self.context.items() if k in key_context_items]
        if context_summary_parts:
            summary_str += f" ({', '.join(context_summary_parts)})"
            
        return {"id": self.id, "type": type_repr, "actor": self.actor, "summary": summary_str,
                "tags": self.tags[:3], "timestamp": self.timestamp}
    
    def __str__(self) -> str:
        type_repr = self.type.name if isinstance(self.type, EventType) else str(self.type)
        return (f"GameEvent(type={type_repr}, actor='{self.actor}', "
                f"context={self.context}, tags={self.tags}, timestamp='{self.timestamp}')")

# ... (Rest of EventLogger and GameEventBus classes remain the same as in previous response)
# Global event bus instance
event_bus = GameEventBus()