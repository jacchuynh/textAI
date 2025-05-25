
"""
Seasonal Economy Service

This module integrates seasonal changes with the economy system,
affecting resource availability, demand, and pricing.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from sqlalchemy.orm import Session

from app.models.time_models import Season
from app.models.season_models import SeasonChangeEvent, SeasonalModifier
from app.events.event_bus import event_bus, EventType

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Types of resources affected by seasons."""
    HERBS = "herbs"
    FRUITS = "fruits"
    WOOD = "wood"
    STONE = "stone"
    METALS = "metals"
    PELTS = "pelts"
    GRAINS = "grains"
    FLOWERS = "flowers"
    MUSHROOMS = "mushrooms"
    GAME_MEAT = "game_meat"


class SeasonalEconomyService:
    """Service for managing seasonal effects on the economy."""
    
    def __init__(self, db: Session, game_id: str):
        self.db = db
        self.game_id = game_id
        
        # Subscribe to seasonal change events
        event_bus.subscribe(EventType.SEASON_CHANGED, self._handle_season_change)
        
        # Initialize seasonal modifiers
        self.seasonal_resource_availability = self._initialize_resource_availability()
        self.seasonal_demand_modifiers = self._initialize_demand_modifiers()
        self.current_season = Season.SPRING  # Default starting season
    
    def _initialize_resource_availability(self) -> Dict[Season, Dict[ResourceType, float]]:
        """Initialize seasonal resource availability modifiers."""
        return {
            Season.SPRING: {
                ResourceType.HERBS: 1.5,      # Fresh herbs emerging
                ResourceType.FLOWERS: 2.0,     # Blooming season
                ResourceType.FRUITS: 0.3,      # Early fruits
                ResourceType.WOOD: 1.2,        # Good cutting season
                ResourceType.STONE: 1.0,       # Normal availability
                ResourceType.METALS: 1.0,      # Mining not affected
                ResourceType.PELTS: 0.7,       # Animals shedding winter coats
                ResourceType.GRAINS: 0.2,      # Planting season, no harvest yet
                ResourceType.MUSHROOMS: 1.3,   # Spring mushrooms
                ResourceType.GAME_MEAT: 0.8    # Animals dispersing
            },
            Season.SUMMER: {
                ResourceType.HERBS: 2.0,       # Peak growing season
                ResourceType.FLOWERS: 1.8,     # Full bloom
                ResourceType.FRUITS: 2.5,      # Harvest season
                ResourceType.WOOD: 0.8,        # Harder to work in heat
                ResourceType.STONE: 1.2,       # Good quarrying weather
                ResourceType.METALS: 1.1,      # Easier mining conditions
                ResourceType.PELTS: 0.5,       # Summer coats are lighter
                ResourceType.GRAINS: 0.1,      # Growing but not ready
                ResourceType.MUSHROOMS: 0.7,   # Dry conditions
                ResourceType.GAME_MEAT: 1.0    # Normal hunting
            },
            Season.AUTUMN: {
                ResourceType.HERBS: 1.0,       # Some herbs still available
                ResourceType.FLOWERS: 0.5,     # Most flowers done
                ResourceType.FRUITS: 1.8,      # Late harvest
                ResourceType.WOOD: 1.5,        # Excellent cutting season
                ResourceType.STONE: 1.0,       # Normal availability
                ResourceType.METALS: 1.0,      # Normal mining
                ResourceType.PELTS: 1.5,       # Animals growing winter coats
                ResourceType.GRAINS: 3.0,      # Harvest season!
                ResourceType.MUSHROOMS: 2.0,   # Mushroom season
                ResourceType.GAME_MEAT: 1.8    # Animals fattening for winter
            },
            Season.WINTER: {
                ResourceType.HERBS: 0.3,       # Preserved/dried herbs only
                ResourceType.FLOWERS: 0.1,     # Very rare
                ResourceType.FRUITS: 0.2,      # Stored fruits only
                ResourceType.WOOD: 0.7,        # Difficult cutting conditions
                ResourceType.STONE: 0.8,       # Harder quarrying
                ResourceType.METALS: 0.8,      # More difficult mining
                ResourceType.PELTS: 2.5,       # Prime fur season
                ResourceType.GRAINS: 0.5,      # Stored grains
                ResourceType.MUSHROOMS: 0.4,   # Preserved mushrooms
                ResourceType.GAME_MEAT: 1.3    # Hunting season
            }
        }
    
    def _initialize_demand_modifiers(self) -> Dict[Season, Dict[str, float]]:
        """Initialize seasonal demand modifiers for different item types."""
        return {
            Season.SPRING: {
                "warm_clothing": 0.3,     # Less demand for warm clothes
                "cold_protection": 0.2,
                "preserved_food": 0.4,    # Using up winter stores
                "fresh_food": 1.8,        # High demand for fresh food
                "farming_tools": 2.0,     # Planting season
                "medicine": 1.5,          # Spring ailments
                "construction": 1.5       # Building season begins
            },
            Season.SUMMER: {
                "warm_clothing": 0.1,     # Very low demand
                "cold_protection": 0.1,
                "preserved_food": 0.6,
                "fresh_food": 2.0,        # Peak demand for fresh food
                "farming_tools": 1.2,
                "medicine": 1.0,
                "construction": 2.0,      # Peak construction season
                "travel_gear": 1.8        # Travel season
            },
            Season.AUTUMN: {
                "warm_clothing": 1.5,     # Preparing for winter
                "cold_protection": 1.8,
                "preserved_food": 2.5,    # Preserving for winter
                "fresh_food": 1.5,        # Harvest abundance
                "farming_tools": 1.8,     # Harvest tools
                "medicine": 1.2,
                "construction": 1.2,      # Finishing projects
                "travel_gear": 0.8        # Travel season ending
            },
            Season.WINTER: {
                "warm_clothing": 3.0,     # High demand
                "cold_protection": 2.8,
                "preserved_food": 1.8,    # Living off stores
                "fresh_food": 0.5,        # Limited fresh food
                "farming_tools": 0.3,     # No farming
                "medicine": 2.0,          # Winter illnesses
                "construction": 0.5,      # Limited construction
                "fuel": 2.5,             # Heating needs
                "indoor_entertainment": 1.8  # Long nights
            }
        }
    
    def _handle_season_change(self, event: SeasonChangeEvent) -> None:
        """Handle seasonal change events by updating economy modifiers."""
        if event.context.get("game_id") != self.game_id:
            return
        
        new_season = Season(event.context.get("current_season"))
        self.current_season = new_season
        
        logger.info(f"Economy system responding to seasonal change: {new_season}")
        
        # Update resource availability
        self._update_resource_markets(new_season)
        
        # Update demand patterns
        self._update_demand_patterns(new_season)
        
        # Trigger seasonal events
        self._trigger_seasonal_economic_events(new_season)
    
    def _update_resource_markets(self, season: Season) -> None:
        """Update resource availability in markets based on season."""
        availability_modifiers = self.seasonal_resource_availability.get(season, {})
        
        for resource_type, modifier in availability_modifiers.items():
            # Update market quantities and prices
            # In a full implementation, this would interact with market/shop services
            logger.info(f"Resource {resource_type.value} availability: {modifier:.1f}x")
            
            # Price typically inversely correlates with availability
            price_modifier = max(0.5, min(2.0, 1.0 / modifier))
            logger.info(f"Resource {resource_type.value} price modifier: {price_modifier:.1f}x")
    
    def _update_demand_patterns(self, season: Season) -> None:
        """Update item demand patterns based on season."""
        demand_modifiers = self.seasonal_demand_modifiers.get(season, {})
        
        for item_category, modifier in demand_modifiers.items():
            logger.info(f"Demand for {item_category}: {modifier:.1f}x")
    
    def _trigger_seasonal_economic_events(self, season: Season) -> None:
        """Trigger season-specific economic events."""
        seasonal_events = {
            Season.SPRING: [
                "Merchants begin organizing trade expeditions for the traveling season.",
                "Farmers seek loans and laborers for the planting season.",
                "Construction guilds start recruiting for the building season."
            ],
            Season.SUMMER: [
                "Trade routes reach peak activity as weather improves.",
                "Harvest contracts are negotiated in advance.",
                "Tourism and pilgrimage boost local economies."
            ],
            Season.AUTUMN: [
                "Harvest markets flood with seasonal produce.",
                "Winter preparation drives demand for preservation services.",
                "Final trade expeditions depart before winter weather."
            ],
            Season.WINTER: [
                "Trade activity slows as harsh weather affects travel.",
                "Demand for heating fuel and warm goods peaks.",
                "Craftsmen focus on indoor work and commission projects."
            ]
        }
        
        events = seasonal_events.get(season, [])
        for event_description in events:
            logger.info(f"Seasonal economic event: {event_description}")
    
    def get_resource_availability(self, resource_type: ResourceType, season: Optional[Season] = None) -> float:
        """Get the current availability modifier for a resource type."""
        if season is None:
            season = self.current_season
        
        return self.seasonal_resource_availability.get(season, {}).get(resource_type, 1.0)
    
    def get_demand_modifier(self, item_category: str, season: Optional[Season] = None) -> float:
        """Get the current demand modifier for an item category."""
        if season is None:
            season = self.current_season
        
        return self.seasonal_demand_modifiers.get(season, {}).get(item_category, 1.0)
    
    def get_seasonal_economic_summary(self, season: Optional[Season] = None) -> Dict[str, Any]:
        """Get a summary of current seasonal economic effects."""
        if season is None:
            season = self.current_season
        
        availability = self.seasonal_resource_availability.get(season, {})
        demand = self.seasonal_demand_modifiers.get(season, {})
        
        # Find most and least available resources
        most_available = max(availability.items(), key=lambda x: x[1]) if availability else None
        least_available = min(availability.items(), key=lambda x: x[1]) if availability else None
        
        # Find highest and lowest demand categories
        highest_demand = max(demand.items(), key=lambda x: x[1]) if demand else None
        lowest_demand = min(demand.items(), key=lambda x: x[1]) if demand else None
        
        return {
            "season": season.value,
            "most_available_resource": most_available[0].value if most_available else None,
            "least_available_resource": least_available[0].value if least_available else None,
            "highest_demand_category": highest_demand[0] if highest_demand else None,
            "lowest_demand_category": lowest_demand[0] if lowest_demand else None,
            "resource_availability": {k.value: v for k, v in availability.items()},
            "demand_modifiers": demand
        }
