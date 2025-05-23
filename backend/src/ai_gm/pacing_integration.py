"""
Pacing System Integration for AI GM Brain

This module integrates the pacing system with the AI GM Brain,
controlling narrative rhythm and ambient storytelling.
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

# Add the assets directory to path to allow importing pacing components
sys.path.insert(0, 'attached_assets')

try:
    from pacing.pacing_manager import PacingManager, PacingState, AmbientTrigger
    from pacing.event_summarizer import EventSummarizer
    
    PACING_AVAILABLE = True
except ImportError:
    PACING_AVAILABLE = False
    print("Pacing system components not available.")


class PacingIntegration:
    """Integration module for the pacing system with AI GM Brain."""
    
    def __init__(self, brain):
        """
        Initialize the pacing integration.
        
        Args:
            brain: The AI GM Brain instance to integrate with
        """
        self.brain = brain
        self.enabled = PACING_AVAILABLE
        
        if not self.enabled:
            return
            
        # Initialize the pacing manager with default configuration
        self.pacing_config = {
            'significant_event_threshold': timedelta(minutes=5),
            'branch_progression_threshold': timedelta(minutes=15),
            'player_inactivity_threshold': timedelta(minutes=2),
            'lull_threshold': timedelta(minutes=10),
            'stagnant_threshold': timedelta(minutes=20),
            'ambient_content_min_delay': timedelta(seconds=30),
            'ambient_content_probability': {
                PacingState.ACTIVE.value: 0.05,     # Low probability during active periods
                PacingState.SETTLING.value: 0.15,   # Medium probability during settling periods
                PacingState.LULL.value: 0.35,       # High probability during lulls
                PacingState.STAGNANT.value: 0.70    # Very high probability during stagnant periods
            }
        }
        
        # Initialize the pacing manager
        self.pacing_manager = PacingManager(config=self.pacing_config)
        
        # Initialize the event summarizer
        self.event_summarizer = EventSummarizer()
        
        # Initialize ambient content triggers and templates
        self._init_ambient_content()
        
        # Set time tracking
        self.last_input_time = datetime.now()
        self.last_ambient_content_time = None
    
    def _init_ambient_content(self):
        """Initialize ambient content triggers and templates."""
        if not self.enabled:
            return
            
        # Define ambient content templates based on trigger types
        self.ambient_templates = {
            AmbientTrigger.TIME_BASED.value: [
                "As time passes, {time_description}.",
                "You notice that {time_description}.",
                "{time_description}."
            ],
            AmbientTrigger.LOCATION_BASED.value: [
                "Looking around the {location}, you notice {detail}.",
                "The {location} {location_activity}.",
                "A {location_detail} catches your attention."
            ],
            AmbientTrigger.WORLD_STATE_BASED.value: [
                "News spreads about {world_event}.",
                "You overhear talk of {world_event}.",
                "There are rumors that {world_event}."
            ],
            AmbientTrigger.NPC_BASED.value: [
                "{npc_name} {npc_action}.",
                "You notice {npc_name} {npc_action}.",
                "Nearby, {npc_name} {npc_action}."
            ],
            AmbientTrigger.WEATHER_BASED.value: [
                "The weather {weather_change}.",
                "You feel {weather_sensation} as {weather_description}.",
                "{weather_description}."
            ],
            AmbientTrigger.MOOD_BASED.value: [
                "The atmosphere feels {mood_description}.",
                "There's a {mood_description} feeling in the air.",
                "You sense a {mood_description} mood around you."
            ]
        }
        
        # Sample ambient content data for each trigger type (would be expanded in a full implementation)
        self.ambient_content_data = {
            AmbientTrigger.TIME_BASED.value: {
                "time_description": [
                    "the sun begins to set, casting long shadows",
                    "night is falling rapidly now",
                    "daylight is beginning to fade",
                    "dawn's first light is appearing on the horizon",
                    "it's nearly midday, with the sun high overhead"
                ]
            },
            AmbientTrigger.LOCATION_BASED.value: {
                "location_activity": [
                    "is busier than before",
                    "has grown quieter",
                    "seems different somehow",
                    "has several interesting details you didn't notice before",
                    "contains hidden aspects that reveal themselves upon closer inspection"
                ],
                "location_detail": [
                    "small detail in the corner",
                    "peculiar marking on the wall",
                    "distinct smell",
                    "unusual sound",
                    "change in the arrangement"
                ]
            },
            AmbientTrigger.NPC_BASED.value: {
                "npc_action": [
                    "glances in your direction briefly",
                    "appears to be deep in thought",
                    "is engaged in conversation with someone else",
                    "seems troubled by something",
                    "is focused on a task"
                ]
            }
        }
    
    def is_enabled(self) -> bool:
        """Check if the pacing system is enabled."""
        return self.enabled
    
    def update_pacing_state(self, player_input: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the pacing state based on player input and system response.
        
        Args:
            player_input: The player's input text
            response_data: The response data from the AI GM Brain
            
        Returns:
            Updated pacing information
        """
        if not self.enabled:
            return {"status": "disabled", "pacing_state": "unknown"}
            
        # Update the last input time
        self.last_input_time = datetime.now()
        
        # Check if the response represents a significant event
        is_significant = self._is_significant_event(response_data)
        
        # Check if the response represents branch progression
        is_branch_progression = self._is_branch_progression(response_data)
        
        # Update the pacing manager with this information
        self.pacing_manager.update_metrics(
            input_time=self.last_input_time,
            is_significant_event=is_significant,
            is_branch_progression=is_branch_progression
        )
        
        # Calculate current pacing state
        current_state = self.pacing_manager.get_current_state()
        
        return {
            "status": "success",
            "pacing_state": current_state.value,
            "is_significant_event": is_significant,
            "is_branch_progression": is_branch_progression,
            "time_since_significant": self.pacing_manager.current_metrics.time_since_significant_event().total_seconds(),
            "time_since_branch": self.pacing_manager.current_metrics.time_since_branch_progression().total_seconds()
        }
    
    def check_for_ambient_content(self) -> Optional[Dict[str, Any]]:
        """
        Check if ambient content should be generated based on pacing state.
        
        Returns:
            Ambient content data if it should be generated, None otherwise
        """
        if not self.enabled:
            return None
            
        # Check if enough time has passed since the last ambient content
        now = datetime.now()
        min_delay = self.pacing_config['ambient_content_min_delay']
        
        if (self.last_ambient_content_time and 
                now - self.last_ambient_content_time < min_delay):
            return None
            
        # Check if enough time has passed since the last player input
        time_since_input = now - self.last_input_time
        if time_since_input < timedelta(seconds=15):
            return None
            
        # Get current pacing state
        current_state = self.pacing_manager.get_current_state()
        
        # Determine probability based on state
        probability = self.pacing_config['ambient_content_probability'].get(
            current_state.value, 0.05
        )
        
        # Roll for ambient content
        import random
        if random.random() > probability:
            return None
            
        # Generate ambient content
        trigger_type = self._select_ambient_trigger(current_state)
        content = self._generate_ambient_content(trigger_type)
        
        # Update last ambient content time
        self.last_ambient_content_time = now
        
        return {
            "content": content,
            "trigger_type": trigger_type,
            "pacing_state": current_state.value
        }
    
    def _select_ambient_trigger(self, state: PacingState) -> str:
        """
        Select an appropriate ambient trigger based on the current state.
        
        Args:
            state: The current pacing state
            
        Returns:
            The selected trigger type
        """
        import random
        
        # Define weights for different trigger types based on pacing state
        if state == PacingState.ACTIVE:
            weights = {
                AmbientTrigger.NPC_BASED.value: 0.4,
                AmbientTrigger.LOCATION_BASED.value: 0.3,
                AmbientTrigger.TIME_BASED.value: 0.1,
                AmbientTrigger.WORLD_STATE_BASED.value: 0.1,
                AmbientTrigger.WEATHER_BASED.value: 0.05,
                AmbientTrigger.MOOD_BASED.value: 0.05
            }
        elif state == PacingState.SETTLING:
            weights = {
                AmbientTrigger.LOCATION_BASED.value: 0.3,
                AmbientTrigger.NPC_BASED.value: 0.25,
                AmbientTrigger.TIME_BASED.value: 0.2,
                AmbientTrigger.MOOD_BASED.value: 0.1,
                AmbientTrigger.WEATHER_BASED.value: 0.1,
                AmbientTrigger.WORLD_STATE_BASED.value: 0.05
            }
        elif state == PacingState.LULL:
            weights = {
                AmbientTrigger.TIME_BASED.value: 0.3,
                AmbientTrigger.MOOD_BASED.value: 0.25,
                AmbientTrigger.WEATHER_BASED.value: 0.2,
                AmbientTrigger.LOCATION_BASED.value: 0.15,
                AmbientTrigger.WORLD_STATE_BASED.value: 0.05,
                AmbientTrigger.NPC_BASED.value: 0.05
            }
        else:  # STAGNANT
            weights = {
                AmbientTrigger.WORLD_STATE_BASED.value: 0.35,
                AmbientTrigger.NPC_BASED.value: 0.25,
                AmbientTrigger.MOOD_BASED.value: 0.2,
                AmbientTrigger.TIME_BASED.value: 0.1,
                AmbientTrigger.WEATHER_BASED.value: 0.05,
                AmbientTrigger.LOCATION_BASED.value: 0.05
            }
        
        # Weighted random selection
        triggers = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(triggers, probabilities)[0]
    
    def _generate_ambient_content(self, trigger_type: str) -> str:
        """
        Generate ambient content based on the trigger type.
        
        Args:
            trigger_type: The type of ambient trigger
            
        Returns:
            Generated ambient content
        """
        import random
        
        # Select a template
        templates = self.ambient_templates.get(trigger_type, ["Something ambient happens."])
        template = random.choice(templates)
        
        # Get data for the trigger type
        data = self.ambient_content_data.get(trigger_type, {})
        
        # Simple template filling (in a full implementation, this would be more sophisticated)
        if trigger_type == AmbientTrigger.TIME_BASED.value and "time_description" in data:
            time_desc = random.choice(data["time_description"])
            return template.format(time_description=time_desc)
            
        elif trigger_type == AmbientTrigger.LOCATION_BASED.value:
            location = "area"
            if hasattr(self.brain, "_context") and isinstance(self.brain._context, dict):
                location = self.brain._context.get("current_location", "area")
                
            if "location_activity" in data:
                location_activity = random.choice(data["location_activity"])
                return template.format(location=location, location_activity=location_activity)
                
            elif "location_detail" in data:
                location_detail = random.choice(data["location_detail"])
                return template.format(location=location, location_detail=location_detail)
                
        elif trigger_type == AmbientTrigger.NPC_BASED.value and "npc_action" in data:
            npc_name = "Someone"
            if hasattr(self.brain, "_context") and isinstance(self.brain._context, dict):
                npcs = self.brain._context.get("active_npcs", [])
                if npcs:
                    npc_name = random.choice(npcs)
                    
            npc_action = random.choice(data["npc_action"])
            return template.format(npc_name=npc_name, npc_action=npc_action)
            
        # Fallback for other types or missing data
        return "You sense a subtle shift in the atmosphere around you."
    
    def _is_significant_event(self, response: Dict[str, Any]) -> bool:
        """
        Check if a response represents a significant event.
        
        Args:
            response: The response data
            
        Returns:
            True if the response represents a significant event, False otherwise
        """
        if not isinstance(response, dict):
            return False
            
        # Check for obvious indicators in the response
        metadata = response.get("metadata", {})
        if metadata.get("significant_event", False):
            return True
            
        # Check complexity
        if metadata.get("complexity") in ["COMPLEX", "VERY_COMPLEX"]:
            return True
            
        # Combat success is significant
        if response.get("combat_result", {}).get("outcome") == "victory":
            return True
            
        # Check action execution
        if response.get("action_executed", False):
            action_result = response.get("action_result", {})
            if action_result.get("outcome") == "success":
                return True
        
        return False
    
    def _is_branch_progression(self, response: Dict[str, Any]) -> bool:
        """
        Check if a response represents branch progression.
        
        Args:
            response: The response data
            
        Returns:
            True if the response represents branch progression, False otherwise
        """
        if not isinstance(response, dict):
            return False
            
        action_result = response.get("action_result", {})
        if action_result:
            action_type = action_result.get("action_type", "")
            if action_type in ["opportunity_initiation", "branch_action", "quest_progress"]:
                return action_result.get("outcome") == "success"
        
        return False
    
    def summarize_recent_events(self, max_events: int = 5) -> str:
        """
        Summarize recent events for context refresh.
        
        Args:
            max_events: Maximum number of events to include
            
        Returns:
            Summary of recent events
        """
        if not self.enabled or not self.event_summarizer:
            return "No recent events to summarize."
            
        # In a full implementation, events would be tracked and retrieved
        # For now, we return a placeholder
        
        return "Recent events have been relatively uneventful."


def attach_to_brain(brain):
    """
    Attach the pacing system to the AI GM Brain.
    
    Args:
        brain: The AI GM Brain instance
        
    Returns:
        The created integration instance
    """
    integration = PacingIntegration(brain)
    brain.register_extension("pacing", integration)
    return integration