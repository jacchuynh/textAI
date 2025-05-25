
"""
Season System Models

This module defines models for seasonal change events and seasonal effects
that integrate with the existing time system.
"""

from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel

from .time_models import Season
from app.events.event_bus import GameEvent, EventType


class SeasonChangeEventData(BaseModel):
    """
    Data payload for seasonal change events.
    """
    previous_season: Optional[Season] = None
    current_season: Season
    year: int
    month: int
    day: int
    narrative_summary: Optional[str] = None
    
    def get_transition_narrative(self) -> str:
        """Generate narrative description of the seasonal transition."""
        if self.narrative_summary:
            return self.narrative_summary
            
        # Default transition narratives
        transitions = {
            (Season.WINTER, Season.SPRING): "The harsh grip of winter loosens as the first tender shoots of spring emerge from the thawing earth.",
            (Season.SPRING, Season.SUMMER): "Spring's gentle warmth gives way to summer's vibrant energy as flowers bloom in full splendor.",
            (Season.SUMMER, Season.AUTUMN): "Summer's heat begins to fade as autumn paints the world in brilliant shades of gold and crimson.",
            (Season.AUTUMN, Season.WINTER): "Autumn's colorful display yields to winter's quiet embrace as the world prepares for its seasonal rest.",
            (None, Season.SPRING): "Spring awakens the world with renewed life and gentle warmth.",
            (None, Season.SUMMER): "Summer brings warmth and abundance to the land.",
            (None, Season.AUTUMN): "Autumn arrives with its harvest bounty and changing colors.",
            (None, Season.WINTER): "Winter settles over the land with its quiet, contemplative stillness."
        }
        
        key = (self.previous_season, self.current_season)
        return transitions.get(key, f"The season changes from {self.previous_season} to {self.current_season}.")


class SeasonChangeEvent(GameEvent):
    """
    Event published when seasons change.
    """
    event_type: EventType = EventType.SEASON_CHANGED
    data: SeasonChangeEventData
    
    def __init__(self, data: SeasonChangeEventData, game_id: str, **kwargs):
        super().__init__(
            event_type=EventType.SEASON_CHANGED,
            context={
                "game_id": game_id,
                "previous_season": data.previous_season.value if data.previous_season else None,
                "current_season": data.current_season.value,
                "year": data.year,
                "month": data.month,
                "day": data.day,
                "narrative_summary": data.get_transition_narrative()
            },
            source_id="SYSTEM",
            **kwargs
        )
        self.data = data


class SeasonalModifier(BaseModel):
    """
    Represents seasonal modifications to various game systems.
    """
    season: Season
    modifier_type: str  # e.g., "weather_probability", "resource_availability", "magic_potency"
    target_id: str      # e.g., weather phenomenon ID, resource ID, spell ID
    modifier_value: float  # Multiplier (1.0 = no change, 0.5 = half effectiveness, 2.0 = double effectiveness)
    description: Optional[str] = None


class SeasonalEffect(BaseModel):
    """
    Represents a specific seasonal effect on game systems.
    """
    effect_id: str
    name: str
    description: str
    active_seasons: list[Season]
    effect_type: str  # e.g., "weather", "economy", "magic", "combat", "narrative"
    effect_data: Dict[str, Any]  # Flexible data for different effect types
    
    def is_active_in_season(self, season: Season) -> bool:
        """Check if this effect is active in the given season."""
        return season in self.active_seasons


class SeasonalSchedule(BaseModel):
    """
    Represents an NPC's seasonal schedule or behavior pattern.
    """
    schedule_id: str
    season: Season
    daily_activities: Dict[str, str]  # time_block -> activity description
    preferred_locations: list[str]
    dialogue_tags: list[str]  # Tags for seasonal dialogue options
    appearance_modifiers: Dict[str, str]  # clothing, accessories, etc.
