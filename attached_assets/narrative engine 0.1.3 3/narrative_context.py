from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime, timedelta
import json
import os

class NarrativeContext:
    """
    Provides contextual information for narrative generation.
    
    This class tracks emotional states, relationships, location contexts,
    and narrative threads to create a rich narrative environment.
    """
    
    def __init__(self, max_context_events: int = 50, storage_dir: str = "data/narrative"):
        """
        Initialize the narrative context.
        
        Args:
            max_context_events: Maximum number of events to keep in active context
            storage_dir: Directory for persisting narrative context data
        """
        self.max_context_events = max_context_events
        self.storage_dir = storage_dir
        
        # Character emotional states - tracks mood, relationships, etc.
        self.character_states: Dict[str, Dict[str, Any]] = {}
        
        # Location contexts - what's happened in each place
        self.location_contexts: Dict[str, Dict[str, Any]] = {}
        
        # Narrative threads - ongoing story elements
        self.active_threads: Dict[str, Dict[str, Any]] = {}
        
        # Recent events cache
        self.recent_events: List[Dict[str, Any]] = []
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
    
    def update_emotion(self, character_id: str, event_type: str, 
                      context: Dict[str, Any] = None, 
                      traits: List[str] = None) -> Dict[str, Any]:
        """
        Update character's emotional state based on an event.
        
        Args:
            character_id: ID of the character
            event_type: Type of event affecting emotions
            context: Additional event context
            traits: Character traits affecting emotional response
            
        Returns:
            Updated emotional state
        """
        # Initialize character state if needed
        if character_id not in self.character_states:
            self.character_states[character_id] = {
                "emotions": {
                    "joy": 0,
                    "sorrow": 0,
                    "anger": 0,
                    "fear": 0,
                    "curiosity": 0,
                    "pride": 0,
                },
                "recent_significant_events": [],
                "relationships": {},
                "traits": traits or [],
                "last_updated": datetime.utcnow().isoformat()
            }
            
        character = self.character_states[character_id]
        context = context or {}
        
        # Different event types affect emotions differently
        emotion_map = {
            "QUEST_COMPLETED": {"joy": 2, "pride": 2},
            "QUEST_FAILED": {"sorrow": 2, "anger": 1},
            "ENEMY_DEFEATED": {"joy": 1, "pride": 1},
            "CHARACTER_DEFEATED": {"sorrow": 2, "anger": 1},
            "LEVEL_UP": {"joy": 1, "pride": 2},
            "DOMAIN_INCREASED": {"pride": 2},
            "LOCATION_DISCOVERED": {"curiosity": 2},
            "COMBAT_STARTED": {"fear": 1},
            "NPC_RELATIONSHIP_CHANGED": {"joy": 1} if context.get("change", 0) > 0 else {"sorrow": 1},
            "ITEM_ACQUIRED": {"joy": 1},
            # Add more event mappings as needed
        }
        
        # Apply emotion changes based on event type
        if event_type in emotion_map:
            # Get trait multipliers (some traits amplify or dampen emotions)
            trait_multipliers = self._get_trait_emotion_multipliers(character.get("traits", []))
            
            for emotion, base_change in emotion_map[event_type].items():
                # Apply trait multiplier
                multiplier = trait_multipliers.get(emotion, 1.0)
                change = base_change * multiplier
                
                # Apply context modifiers
                if "intensity" in context:
                    change *= context["intensity"]
                
                # Update emotion value with clamping
                character["emotions"][emotion] = min(10, max(0, character["emotions"][emotion] + change))
                
        # Calculate emotional impact of this event
        impact = self._calculate_emotional_impact(event_type, context)
        
        # Add to significant events if impact is high enough
        if impact > 3:
            significant_event = {
                "event_type": event_type,
                "impact": impact,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            }
            character["recent_significant_events"].append(significant_event)
            
            # Keep only the most significant recent events (up to 10)
            character