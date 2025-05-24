"""
Narrative Pacing Module

This module manages the pacing of the narrative, controlling the flow of
events, tension, and intensity based on player actions and game state.
"""

from typing import Dict, Any, List, Optional, Set, Union, Tuple
import logging
import json
from datetime import datetime
import random
import math

from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class PacingManager:
    """
    Manages the pacing of the narrative.
    
    Dynamically adjusts tension, event frequency, and narrative focus
    based on player actions, game state, and pacing goals.
    """
    
    def __init__(self):
        """Initialize the pacing manager."""
        self.tension_level = 0.5  # 0.0 to 1.0, default is medium tension
        self.pacing_mode = "balanced"  # slow, balanced, fast
        self.narrative_arc_position = 0.0  # 0.0 to 1.0, progress through current arc
        self.recent_events = []  # Track recent events for pacing adjustments
        self.event_timer = 0  # Time since last significant event
        self.combat_intensity = 0.3  # Intensity of combat encounters
        self.dialogue_depth = 0.5  # Depth and length of dialogue interactions
        self.exploration_detail = 0.5  # Detail level for exploration
        
        # Hook into event bus if available
        try:
            self.event_bus = get_event_bus()
            self.event_bus.subscribe("player_action", self._handle_player_action)
            self.event_bus.subscribe("combat_start", self._handle_combat_start)
            self.event_bus.subscribe("combat_end", self._handle_combat_end)
            self.event_bus.subscribe("dialogue_start", self._handle_dialogue_start)
            self.event_bus.subscribe("time_advance", self._handle_time_advance)
            self.event_bus_available = True
        except Exception as e:
            logger.warning(f"Could not connect to event bus: {e}")
            self.event_bus_available = False
    
    def set_tension(self, level: float) -> None:
        """
        Set the tension level.
        
        Args:
            level: Tension level (0.0 to 1.0)
        """
        self.tension_level = max(0.0, min(1.0, level))
        
        # Publish event if event bus is available
        if self.event_bus_available:
            self.event_bus.publish(Event(
                event_type="tension_changed",
                data={"level": self.tension_level},
                source="pacing_manager"
            ))
    
    def adjust_tension(self, amount: float) -> float:
        """
        Adjust the tension level by a relative amount.
        
        Args:
            amount: Amount to adjust tension by (-1.0 to 1.0)
            
        Returns:
            New tension level
        """
        self.tension_level = max(0.0, min(1.0, self.tension_level + amount))
        
        # Publish event if event bus is available
        if self.event_bus_available:
            self.event_bus.publish(Event(
                event_type="tension_changed",
                data={"level": self.tension_level, "adjustment": amount},
                source="pacing_manager"
            ))
            
        return self.tension_level
    
    def set_pacing_mode(self, mode: str) -> None:
        """
        Set the pacing mode.
        
        Args:
            mode: Pacing mode (slow, balanced, fast)
        """
        valid_modes = ["slow", "balanced", "fast"]
        if mode not in valid_modes:
            logger.warning(f"Invalid pacing mode: {mode}. Using 'balanced' instead.")
            mode = "balanced"
            
        self.pacing_mode = mode
        
        # Adjust parameters based on pacing mode
        if mode == "slow":
            self.dialogue_depth = 0.7
            self.exploration_detail = 0.7
            self.combat_intensity = 0.3
        elif mode == "fast":
            self.dialogue_depth = 0.3
            self.exploration_detail = 0.3
            self.combat_intensity = 0.7
        else:  # balanced
            self.dialogue_depth = 0.5
            self.exploration_detail = 0.5
            self.combat_intensity = 0.5
            
        # Publish event if event bus is available
        if self.event_bus_available:
            self.event_bus.publish(Event(
                event_type="pacing_mode_changed",
                data={"mode": self.pacing_mode},
                source="pacing_manager"
            ))
    
    def set_narrative_arc_position(self, position: float) -> None:
        """
        Set the position within the current narrative arc.
        
        Args:
            position: Position (0.0 to 1.0)
        """
        self.narrative_arc_position = max(0.0, min(1.0, position))
        
        # Publish event if event bus is available
        if self.event_bus_available:
            self.event_bus.publish(Event(
                event_type="narrative_arc_position_changed",
                data={"position": self.narrative_arc_position},
                source="pacing_manager"
            ))
    
    def advance_narrative_arc(self, amount: float) -> float:
        """
        Advance the position within the current narrative arc.
        
        Args:
            amount: Amount to advance (0.0 to 1.0)
            
        Returns:
            New narrative arc position
        """
        self.narrative_arc_position = max(0.0, min(1.0, self.narrative_arc_position + amount))
        
        # Publish event if event bus is available
        if self.event_bus_available:
            self.event_bus.publish(Event(
                event_type="narrative_arc_position_changed",
                data={"position": self.narrative_arc_position, "advancement": amount},
                source="pacing_manager"
            ))
            
        return self.narrative_arc_position
    
    def add_event(self, event_data: Dict[str, Any]) -> None:
        """
        Add an event to the recent events list.
        
        Args:
            event_data: Event data
        """
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.utcnow().isoformat()
            
        # Add to recent events (limited to 20)
        self.recent_events.append(event_data)
        if len(self.recent_events) > 20:
            self.recent_events.pop(0)  # Remove oldest event
            
        # Reset event timer
        self.event_timer = 0
        
        # Adjust tension based on event type
        event_type = event_data.get("type", "")
        
        if event_type == "combat":
            self.adjust_tension(0.1)
        elif event_type == "danger":
            self.adjust_tension(0.15)
        elif event_type == "discovery":
            self.adjust_tension(0.05)
        elif event_type == "success":
            self.adjust_tension(-0.05)
        elif event_type == "failure":
            self.adjust_tension(0.1)
        elif event_type == "rest":
            self.adjust_tension(-0.15)
            
        # Publish event if event bus is available
        if self.event_bus_available:
            self.event_bus.publish(Event(
                event_type="pacing_event_added",
                data={"event": event_data},
                source="pacing_manager"
            ))
    
    def get_pacing_state(self) -> Dict[str, Any]:
        """
        Get the current pacing state.
        
        Returns:
            Pacing state dictionary
        """
        return {
            "tension_level": self.tension_level,
            "pacing_mode": self.pacing_mode,
            "narrative_arc_position": self.narrative_arc_position,
            "event_timer": self.event_timer,
            "combat_intensity": self.combat_intensity,
            "dialogue_depth": self.dialogue_depth,
            "exploration_detail": self.exploration_detail,
            "recent_events_count": len(self.recent_events)
        }
    
    def should_trigger_event(self, current_time: float, 
                           location: Optional[str] = None, 
                           context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if a narrative event should be triggered.
        
        Args:
            current_time: Current game time
            location: Optional location context
            context: Optional additional context
            
        Returns:
            Whether an event should be triggered
        """
        # Calculate time since last event
        time_factor = self.event_timer / 10.0  # More likely as time passes
        
        # Base chance depends on pacing mode
        if self.pacing_mode == "slow":
            base_chance = 0.1
        elif self.pacing_mode == "fast":
            base_chance = 0.3
        else:  # balanced
            base_chance = 0.2
            
        # Adjust based on tension
        tension_factor = self.tension_level * 0.2  # Higher tension, more events
        
        # Location factor
        location_factor = 0.0
        if location == "dangerous":
            location_factor = 0.1
        elif location == "safe":
            location_factor = -0.1
            
        # Context factors
        context_factor = 0.0
        if context:
            if context.get("player_health_percent", 100) < 30:
                context_factor -= 0.1  # Less likely when player is injured
            if context.get("is_night", False):
                context_factor += 0.05  # More likely at night
            if context.get("is_resting", False):
                context_factor -= 0.15  # Less likely when resting
                
        # Calculate final chance
        trigger_chance = base_chance + time_factor + tension_factor + location_factor + context_factor
        trigger_chance = max(0.05, min(0.5, trigger_chance))  # Clamp between 5% and 50%
        
        # Random check
        result = random.random() < trigger_chance
        
        # If triggered, reset timer
        if result:
            self.event_timer = 0
            
        return result
    
    def get_event_intensity(self) -> float:
        """
        Calculate the intensity for an event based on current pacing.
        
        Returns:
            Event intensity (0.0 to 1.0)
        """
        # Base intensity from tension
        base_intensity = self.tension_level
        
        # Adjust based on narrative arc position
        # Events near climax (0.7-0.9) should be more intense
        arc_factor = 0.0
        if 0.7 <= self.narrative_arc_position <= 0.9:
            arc_factor = 0.2
        elif self.narrative_arc_position > 0.9:
            arc_factor = -0.1  # Falling action after climax
            
        # Random variation
        variation = random.uniform(-0.1, 0.1)
        
        # Calculate final intensity
        intensity = base_intensity + arc_factor + variation
        return max(0.1, min(1.0, intensity))  # Clamp between 0.1 and 1.0
    
    def suggest_event_type(self) -> str:
        """
        Suggest an event type based on current pacing and history.
        
        Returns:
            Suggested event type
        """
        # Count recent event types
        event_counts = {}
        for event in self.recent_events[-5:]:  # Look at last 5 events
            event_type = event.get("type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
        # Define possible event types with base weights
        event_types = {
            "combat": 0.2,
            "discovery": 0.2,
            "dialogue": 0.2,
            "challenge": 0.15,
            "rest": 0.1,
            "decision": 0.15
        }
        
        # Adjust weights based on recent events (avoid repetition)
        for event_type, count in event_counts.items():
            if event_type in event_types:
                event_types[event_type] -= count * 0.05
                
        # Adjust based on tension
        if self.tension_level > 0.7:
            event_types["combat"] += 0.2
            event_types["challenge"] += 0.1
            event_types["rest"] -= 0.1
        elif self.tension_level < 0.3:
            event_types["rest"] += 0.1
            event_types["dialogue"] += 0.1
            event_types["combat"] -= 0.1
            
        # Adjust based on narrative arc position
        if self.narrative_arc_position < 0.2:
            event_types["discovery"] += 0.1  # More discovery early in arc
        elif 0.7 <= self.narrative_arc_position <= 0.9:
            event_types["combat"] += 0.1  # More combat near climax
            event_types["decision"] += 0.1  # More decisions near climax
            
        # Ensure all weights are positive
        for event_type in event_types:
            event_types[event_type] = max(0.05, event_types[event_type])
            
        # Normalize weights
        total_weight = sum(event_types.values())
        for event_type in event_types:
            event_types[event_type] /= total_weight
            
        # Choose event type based on weights
        r = random.random()
        cumulative = 0
        for event_type, weight in event_types.items():
            cumulative += weight
            if r <= cumulative:
                return event_type
                
        # Fallback
        return "discovery"
    
    def get_recommended_content_length(self, content_type: str) -> str:
        """
        Get recommended content length based on pacing.
        
        Args:
            content_type: Type of content (dialogue, description, etc.)
            
        Returns:
            Length recommendation (brief, normal, detailed)
        """
        if content_type == "dialogue":
            if self.dialogue_depth > 0.7:
                return "detailed"
            elif self.dialogue_depth < 0.3:
                return "brief"
            else:
                return "normal"
        elif content_type == "description":
            if self.exploration_detail > 0.7:
                return "detailed"
            elif self.exploration_detail < 0.3:
                return "brief"
            else:
                return "normal"
        elif content_type == "combat":
            if self.combat_intensity > 0.7:
                return "detailed"
            elif self.combat_intensity < 0.3:
                return "brief"
            else:
                return "normal"
        else:
            # Default based on pacing mode
            if self.pacing_mode == "slow":
                return "detailed"
            elif self.pacing_mode == "fast":
                return "brief"
            else:
                return "normal"
    
    def update(self, time_delta: float) -> None:
        """
        Update pacing based on time passing.
        
        Args:
            time_delta: Time since last update
        """
        # Increment event timer
        self.event_timer += time_delta
        
        # Gradually reduce tension over time if no events
        if self.event_timer > 5.0:
            tension_reduction = 0.01 * time_delta
            self.tension_level = max(0.3, self.tension_level - tension_reduction)
            
        # Natural arc progression
        if self.event_timer > 10.0:
            arc_progression = 0.005 * time_delta
            self.narrative_arc_position = min(1.0, self.narrative_arc_position + arc_progression)
    
    def _handle_player_action(self, event: Event) -> None:
        """
        Handle a player action event.
        
        Args:
            event: Player action event
        """
        action_type = event.data.get("action_type", "")
        
        # Adjust pacing based on action type
        if action_type == "aggressive":
            self.adjust_tension(0.05)
        elif action_type == "cautious":
            self.adjust_tension(-0.03)
        elif action_type == "explore":
            self.exploration_detail = min(1.0, self.exploration_detail + 0.05)
        elif action_type == "rush":
            self.exploration_detail = max(0.0, self.exploration_detail - 0.05)
            
        # Add to recent events
        self.add_event({
            "type": "player_action",
            "action_type": action_type,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_combat_start(self, event: Event) -> None:
        """
        Handle a combat start event.
        
        Args:
            event: Combat start event
        """
        # Increase tension when combat starts
        self.adjust_tension(0.2)
        
        # Add to recent events
        self.add_event({
            "type": "combat",
            "sub_type": "start",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_combat_end(self, event: Event) -> None:
        """
        Handle a combat end event.
        
        Args:
            event: Combat end event
        """
        # Reduce tension after combat ends
        result = event.data.get("result", "")
        
        if result == "victory":
            self.adjust_tension(-0.15)
        elif result == "defeat":
            self.adjust_tension(0.1)  # Tension remains higher after defeat
        else:  # draw or escape
            self.adjust_tension(-0.05)
            
        # Add to recent events
        self.add_event({
            "type": "combat",
            "sub_type": "end",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_dialogue_start(self, event: Event) -> None:
        """
        Handle a dialogue start event.
        
        Args:
            event: Dialogue start event
        """
        # Adjust pacing for dialogue
        importance = event.data.get("importance", "normal")
        
        if importance == "high":
            self.dialogue_depth = 0.8
        elif importance == "low":
            self.dialogue_depth = 0.3
        else:
            self.dialogue_depth = 0.5
            
        # Add to recent events
        self.add_event({
            "type": "dialogue",
            "sub_type": "start",
            "importance": importance,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_time_advance(self, event: Event) -> None:
        """
        Handle a time advance event.
        
        Args:
            event: Time advance event
        """
        time_delta = event.data.get("time_delta", 0.0)
        
        # Update pacing based on time
        self.update(time_delta)


# Create a singleton instance
_pacing_manager = None

def get_pacing_manager() -> PacingManager:
    """
    Get the global pacing manager instance.
    
    Returns:
        Global pacing manager instance
    """
    global _pacing_manager
    
    if _pacing_manager is None:
        _pacing_manager = PacingManager()
        
    return _pacing_manager