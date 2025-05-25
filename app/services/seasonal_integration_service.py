
"""
Seasonal Integration Service

This service coordinates seasonal effects across all game systems,
providing a central point for seasonal system management.
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.models.time_models import Season, TimeBlock
from app.models.season_models import SeasonChangeEvent
from app.services.time_service import TimeService
from app.services.weather_service import WeatherService
from app.services.seasonal_economy_service import SeasonalEconomyService
from app.services.seasonal_npc_service import SeasonalNPCService
from app.events.event_bus import event_bus, EventType

logger = logging.getLogger(__name__)


class SeasonalIntegrationService:
    """Central service for coordinating seasonal effects across all game systems."""
    
    def __init__(self, db: Session, game_id: str, time_service: TimeService):
        self.db = db
        self.game_id = game_id
        self.time_service = time_service
        
        # Initialize component services
        self.weather_service = WeatherService(db, game_id)
        self.economy_service = SeasonalEconomyService(db, game_id)
        self.npc_service = SeasonalNPCService(db, game_id)
        
        # Subscribe to seasonal change events
        event_bus.subscribe(EventType.SEASON_CHANGED, self._handle_season_change)
        
        logger.info(f"Seasonal Integration Service initialized for game {game_id}")
    
    def _handle_season_change(self, event: SeasonChangeEvent) -> None:
        """Coordinate response to seasonal changes across all systems."""
        if event.context.get("game_id") != self.game_id:
            return
        
        new_season = Season(event.context.get("current_season"))
        old_season_str = event.context.get("old_season")
        old_season = Season(old_season_str) if old_season_str else None
        
        logger.info(f"Coordinating seasonal transition: {old_season} -> {new_season}")
        
        # Generate comprehensive seasonal narrative
        narrative = self._generate_seasonal_transition_narrative(old_season, new_season)
        
        # Log the transition for the game master and players
        self._log_seasonal_transition(old_season, new_season, narrative)
    
    def _generate_seasonal_transition_narrative(self, old_season: Optional[Season], new_season: Season) -> str:
        """Generate a comprehensive narrative for the seasonal transition."""
        
        # Get current game state for context
        current_datetime = self.time_service.get_current_datetime()
        season_progress = self.time_service.get_season_progress()
        
        # Get system-specific information
        weather_summary = self._get_weather_transition_summary(old_season, new_season)
        economy_summary = self._get_economy_transition_summary(old_season, new_season)
        npc_summary = self._get_npc_transition_summary(old_season, new_season)
        
        # Construct comprehensive narrative
        narrative_parts = []
        
        # Main transition
        if old_season:
            narrative_parts.append(f"As {old_season.value.lower()} fades into memory, {new_season.value.lower()} arrives with its own character and challenges.")
        else:
            narrative_parts.append(f"The world settles into the rhythm of {new_season.value.lower()}.")
        
        # Weather effects
        if weather_summary:
            narrative_parts.append(f"The weather patterns shift: {weather_summary}")
        
        # Economic impacts
        if economy_summary:
            narrative_parts.append(f"Markets and trade adapt: {economy_summary}")
        
        # Social changes
        if npc_summary:
            narrative_parts.append(f"The people adjust their routines: {npc_summary}")
        
        # Seasonal atmosphere
        atmosphere = self._get_seasonal_atmosphere(new_season)
        if atmosphere:
            narrative_parts.append(atmosphere)
        
        return " ".join(narrative_parts)
    
    def _get_weather_transition_summary(self, old_season: Optional[Season], new_season: Season) -> str:
        """Get a summary of weather changes for the seasonal transition."""
        weather_changes = {
            Season.SPRING: "gentle rains nurture new growth while temperatures warm gradually",
            Season.SUMMER: "warm, stable weather with occasional thunderstorms provides ideal growing conditions",
            Season.AUTUMN: "cooler temperatures and changing winds signal the approaching harvest season",
            Season.WINTER: "cold weather settles in, bringing snow and ice to quiet the land"
        }
        return weather_changes.get(new_season, "the weather patterns shift subtly")
    
    def _get_economy_transition_summary(self, old_season: Optional[Season], new_season: Season) -> str:
        """Get a summary of economic changes for the seasonal transition."""
        economy_changes = {
            Season.SPRING: "merchants prepare for the traveling season while farmers invest in new crops",
            Season.SUMMER: "trade reaches its peak as goods flow freely along open routes",
            Season.AUTUMN: "harvest markets flourish while people prepare for winter's scarcity",
            Season.WINTER: "trade slows as communities rely on stored goods and indoor crafts"
        }
        return economy_changes.get(new_season, "economic patterns adjust to the new season")
    
    def _get_npc_transition_summary(self, old_season: Optional[Season], new_season: Season) -> str:
        """Get a summary of NPC behavior changes for the seasonal transition."""
        npc_changes = {
            Season.SPRING: "people emerge from winter's isolation with renewed energy and optimism",
            Season.SUMMER: "everyone stays busy with the demands of the productive season",
            Season.AUTUMN: "communities come together to celebrate the harvest and prepare for winter",
            Season.WINTER: "people gather around warm fires, sharing stories and crafting through the long nights"
        }
        return npc_changes.get(new_season, "the community adapts to seasonal rhythms")
    
    def _get_seasonal_atmosphere(self, season: Season) -> str:
        """Get atmospheric description for the season."""
        atmospheres = {
            Season.SPRING: "The air itself seems to hum with potential and new beginnings.",
            Season.SUMMER: "Energy and abundance fill every corner of the world.",
            Season.AUTUMN: "A sense of completion and preparation permeates daily life.",
            Season.WINTER: "Quiet reflection and patient endurance mark the season's character."
        }
        return atmospheres.get(season, "")
    
    def _log_seasonal_transition(self, old_season: Optional[Season], new_season: Season, narrative: str) -> None:
        """Log the seasonal transition for game records."""
        current_datetime = self.time_service.get_current_datetime()
        
        log_entry = {
            "timestamp": current_datetime.format(),
            "event_type": "seasonal_transition",
            "old_season": old_season.value if old_season else None,
            "new_season": new_season.value,
            "year": current_datetime.year,
            "narrative": narrative
        }
        
        logger.info(f"Seasonal transition logged: {log_entry}")
        
        # In a full implementation, this would be saved to a game events log
    
    def get_current_seasonal_state(self) -> Dict[str, Any]:
        """Get comprehensive information about the current seasonal state."""
        current_season = self.time_service.get_current_season()
        current_datetime = self.time_service.get_current_datetime()
        season_progress = self.time_service.get_season_progress()
        
        # Get summaries from each system
        economy_summary = self.economy_service.get_seasonal_economic_summary()
        npc_summary = self.npc_service.get_seasonal_npc_summary()
        
        # Sample regional weather (in a full implementation, this would query actual regions)
        sample_weather = self.weather_service.get_weather_description("default_region", current_season)
        
        return {
            "current_season": current_season.value,
            "season_progress": season_progress,
            "current_time": current_datetime.format(),
            "formatted_time": self.time_service.format_datetime(),
            "weather_sample": sample_weather,
            "economic_state": economy_summary,
            "npc_behavior": npc_summary,
            "days_until_next_season": season_progress.get("days_remaining", 0)
        }
    
    def get_seasonal_effects_for_location(self, location_id: str, region_id: str = "default_region") -> Dict[str, Any]:
        """Get all seasonal effects that apply to a specific location."""
        current_season = self.time_service.get_current_season()
        current_time_block = self.time_service.get_current_time_block()
        
        # Get weather effects
        weather_description = self.weather_service.get_weather_description(region_id, current_season)
        weather_effects = self.weather_service.get_weather_effects(region_id, current_season)
        
        # Get economic effects (example resource availability)
        from app.services.seasonal_economy_service import ResourceType
        resource_availability = {
            resource.value: self.economy_service.get_resource_availability(resource)
            for resource in ResourceType
        }
        
        # Get NPC behaviors
        sample_npc_activities = {}
        from app.services.seasonal_npc_service import NPCRole
        for role in NPCRole:
            activity = self.npc_service.get_npc_activity_for_time(role, current_time_block)
            sample_npc_activities[role.value] = activity
        
        return {
            "location_id": location_id,
            "region_id": region_id,
            "season": current_season.value,
            "time_block": current_time_block.value,
            "weather": {
                "description": weather_description,
                "effects": weather_effects
            },
            "resources": resource_availability,
            "npc_activities": sample_npc_activities,
            "seasonal_atmosphere": self._get_seasonal_atmosphere(current_season)
        }
    
    def trigger_seasonal_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Trigger a custom seasonal event across all systems."""
        logger.info(f"Triggering seasonal event: {event_type}")
        
        # Publish the event for other systems to respond to
        from app.events.event_bus import GameEvent
        event = GameEvent(
            event_type=f"seasonal_custom_{event_type}",
            context={
                "game_id": self.game_id,
                "event_type": event_type,
                "event_data": event_data,
                "season": self.time_service.get_current_season().value
            },
            source_id="SEASONAL_INTEGRATION_SERVICE"
        )
        
        event_bus.publish(event)
