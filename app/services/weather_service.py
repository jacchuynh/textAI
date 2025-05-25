
"""
Weather Service

This module provides weather management with seasonal awareness,
integrating with the Time System to provide realistic weather patterns.
"""

import logging
import random
from typing import Dict, List, Optional, Any
from enum import Enum
from sqlalchemy.orm import Session

from app.models.time_models import Season, GameDateTime
from app.models.season_models import SeasonChangeEvent, SeasonalModifier
from app.events.event_bus import event_bus, EventType

logger = logging.getLogger(__name__)


class WeatherPhenomenon(str, Enum):
    """Types of weather phenomena."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    LIGHT_SNOW = "light_snow"
    HEAVY_SNOW = "heavy_snow"
    BLIZZARD = "blizzard"
    FOG = "fog"
    WIND = "wind"
    HOT = "hot"
    COLD = "cold"
    FREEZING = "freezing"


class WeatherIntensity(str, Enum):
    """Intensity levels for weather."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class RegionalWeather:
    """Represents weather conditions in a specific region."""
    
    def __init__(self, region_id: str, phenomenon: WeatherPhenomenon, 
                 intensity: WeatherIntensity, duration_hours: int = 6):
        self.region_id = region_id
        self.phenomenon = phenomenon
        self.intensity = intensity
        self.duration_hours = duration_hours
        self.start_time: Optional[GameDateTime] = None
    
    def get_description(self, season: Season) -> str:
        """Get a narrative description of the weather, influenced by season."""
        base_descriptions = {
            WeatherPhenomenon.CLEAR: {
                Season.SPRING: "bright spring sunshine with gentle breezes",
                Season.SUMMER: "brilliant sunshine and warm, clear skies",
                Season.AUTUMN: "crisp, clear skies with golden autumn light",
                Season.WINTER: "cold, clear skies with pale winter sunlight"
            },
            WeatherPhenomenon.LIGHT_RAIN: {
                Season.SPRING: "a gentle spring shower bringing life to the earth",
                Season.SUMMER: "a refreshing summer sprinkle cooling the air",
                Season.AUTUMN: "a light autumn drizzle painting the leaves",
                Season.WINTER: "a cold winter drizzle chilling the air"
            },
            WeatherPhenomenon.HEAVY_RAIN: {
                Season.SPRING: "a heavy spring downpour nourishing the awakening land",
                Season.SUMMER: "a powerful summer storm with driving rain",
                Season.AUTUMN: "a steady autumn rain washing the fallen leaves",
                Season.WINTER: "a cold, heavy rain making the world feel dreary"
            },
            WeatherPhenomenon.LIGHT_SNOW: {
                Season.SPRING: "an unexpected late spring snow dusting the new growth",
                Season.SUMMER: "impossible summer snow (magical phenomenon)",
                Season.AUTUMN: "the first gentle snowfall of the approaching winter",
                Season.WINTER: "light, peaceful snowflakes drifting from gray skies"
            },
            WeatherPhenomenon.HEAVY_SNOW: {
                Season.SPRING: "a surprising late spring snowstorm",
                Season.SUMMER: "an unnatural magical snowstorm",
                Season.AUTUMN: "heavy snow marking winter's early arrival",
                Season.WINTER: "thick, heavy snowfall blanketing the landscape"
            }
        }
        
        # Get seasonal description or fall back to generic
        seasonal_desc = base_descriptions.get(self.phenomenon, {}).get(season)
        if seasonal_desc:
            return seasonal_desc
        
        # Generic fallback
        return f"{self.intensity.value} {self.phenomenon.value.replace('_', ' ')}"


class WeatherService:
    """Service for managing weather systems with seasonal awareness."""
    
    def __init__(self, db: Session, game_id: str):
        self.db = db
        self.game_id = game_id
        
        # Subscribe to seasonal change events
        event_bus.subscribe(EventType.SEASON_CHANGED, self._handle_season_change)
        
        # Define seasonal weather probabilities
        self.seasonal_weather_probabilities = self._initialize_seasonal_probabilities()
        
        # Current weather by region
        self.regional_weather: Dict[str, RegionalWeather] = {}
    
    def _initialize_seasonal_probabilities(self) -> Dict[Season, Dict[WeatherPhenomenon, float]]:
        """Initialize weather probabilities by season."""
        return {
            Season.SPRING: {
                WeatherPhenomenon.CLEAR: 0.3,
                WeatherPhenomenon.CLOUDY: 0.25,
                WeatherPhenomenon.LIGHT_RAIN: 0.25,
                WeatherPhenomenon.HEAVY_RAIN: 0.1,
                WeatherPhenomenon.THUNDERSTORM: 0.05,
                WeatherPhenomenon.LIGHT_SNOW: 0.03,
                WeatherPhenomenon.FOG: 0.02
            },
            Season.SUMMER: {
                WeatherPhenomenon.CLEAR: 0.4,
                WeatherPhenomenon.HOT: 0.2,
                WeatherPhenomenon.CLOUDY: 0.15,
                WeatherPhenomenon.THUNDERSTORM: 0.15,
                WeatherPhenomenon.LIGHT_RAIN: 0.08,
                WeatherPhenomenon.HEAVY_RAIN: 0.02
            },
            Season.AUTUMN: {
                WeatherPhenomenon.CLOUDY: 0.3,
                WeatherPhenomenon.CLEAR: 0.25,
                WeatherPhenomenon.LIGHT_RAIN: 0.2,
                WeatherPhenomenon.HEAVY_RAIN: 0.1,
                WeatherPhenomenon.WIND: 0.08,
                WeatherPhenomenon.FOG: 0.05,
                WeatherPhenomenon.LIGHT_SNOW: 0.02
            },
            Season.WINTER: {
                WeatherPhenomenon.CLOUDY: 0.25,
                WeatherPhenomenon.OVERCAST: 0.2,
                WeatherPhenomenon.LIGHT_SNOW: 0.2,
                WeatherPhenomenon.HEAVY_SNOW: 0.15,
                WeatherPhenomenon.COLD: 0.1,
                WeatherPhenomenon.FREEZING: 0.05,
                WeatherPhenomenon.BLIZZARD: 0.03,
                WeatherPhenomenon.CLEAR: 0.02
            }
        }
    
    def _handle_season_change(self, event: SeasonChangeEvent) -> None:
        """Handle seasonal change events by updating weather patterns."""
        if event.context.get("game_id") != self.game_id:
            return
        
        new_season = Season(event.context.get("current_season"))
        logger.info(f"Weather system responding to seasonal change: {new_season}")
        
        # Trigger weather updates for all regions
        for region_id in self.regional_weather.keys():
            self._update_regional_weather(region_id, new_season)
    
    def _update_regional_weather(self, region_id: str, season: Season) -> None:
        """Update weather for a specific region based on current season."""
        probabilities = self.seasonal_weather_probabilities.get(season, {})
        
        if not probabilities:
            logger.warning(f"No weather probabilities defined for season {season}")
            return
        
        # Select weather phenomenon based on seasonal probabilities
        phenomena = list(probabilities.keys())
        weights = list(probabilities.values())
        
        selected_phenomenon = random.choices(phenomena, weights=weights)[0]
        
        # Determine intensity based on phenomenon and season
        intensity = self._determine_weather_intensity(selected_phenomenon, season)
        
        # Set duration (longer in winter, shorter in summer)
        base_duration = 6
        seasonal_duration_modifier = {
            Season.SPRING: 1.0,
            Season.SUMMER: 0.8,
            Season.AUTUMN: 1.2,
            Season.WINTER: 1.5
        }
        duration = int(base_duration * seasonal_duration_modifier.get(season, 1.0))
        
        # Create new weather
        new_weather = RegionalWeather(region_id, selected_phenomenon, intensity, duration)
        self.regional_weather[region_id] = new_weather
        
        logger.info(f"Updated weather for {region_id}: {selected_phenomenon.value} ({intensity.value}) lasting {duration} hours")
    
    def _determine_weather_intensity(self, phenomenon: WeatherPhenomenon, season: Season) -> WeatherIntensity:
        """Determine weather intensity based on phenomenon and season."""
        # Seasonal intensity modifiers
        intensity_weights = {
            WeatherIntensity.MILD: 0.4,
            WeatherIntensity.MODERATE: 0.4,
            WeatherIntensity.SEVERE: 0.15,
            WeatherIntensity.EXTREME: 0.05
        }
        
        # Modify weights based on season and phenomenon
        if season == Season.WINTER and phenomenon in [WeatherPhenomenon.HEAVY_SNOW, WeatherPhenomenon.BLIZZARD]:
            intensity_weights[WeatherIntensity.SEVERE] = 0.3
            intensity_weights[WeatherIntensity.EXTREME] = 0.15
        elif season == Season.SUMMER and phenomenon in [WeatherPhenomenon.THUNDERSTORM, WeatherPhenomenon.HOT]:
            intensity_weights[WeatherIntensity.SEVERE] = 0.25
        
        intensities = list(intensity_weights.keys())
        weights = list(intensity_weights.values())
        
        return random.choices(intensities, weights=weights)[0]
    
    def get_regional_weather(self, region_id: str, season: Season) -> Optional[RegionalWeather]:
        """Get current weather for a region."""
        if region_id not in self.regional_weather:
            self._update_regional_weather(region_id, season)
        
        return self.regional_weather.get(region_id)
    
    def get_weather_description(self, region_id: str, season: Season) -> str:
        """Get a narrative description of the weather in a region."""
        weather = self.get_regional_weather(region_id, season)
        if not weather:
            return "The weather is unremarkable."
        
        return f"The weather is {weather.get_description(season)}."
    
    def get_weather_effects(self, region_id: str, season: Season) -> Dict[str, Any]:
        """Get gameplay effects of current weather."""
        weather = self.get_regional_weather(region_id, season)
        if not weather:
            return {}
        
        effects = {}
        
        # Define weather effects on gameplay
        if weather.phenomenon == WeatherPhenomenon.HEAVY_RAIN:
            effects["visibility"] = 0.7  # Reduced visibility
            effects["travel_speed"] = 0.8  # Slower travel
            effects["fire_magic_penalty"] = 0.2  # Fire magic less effective
        elif weather.phenomenon == WeatherPhenomenon.HEAVY_SNOW:
            effects["visibility"] = 0.6
            effects["travel_speed"] = 0.6
            effects["cold_damage_risk"] = True
            effects["ice_magic_bonus"] = 0.3  # Ice magic more effective
        elif weather.phenomenon == WeatherPhenomenon.HOT:
            effects["stamina_drain"] = 1.5  # Faster stamina loss
            effects["fire_magic_bonus"] = 0.2
            effects["ice_magic_penalty"] = 0.2
        elif weather.phenomenon == WeatherPhenomenon.CLEAR:
            effects["visibility"] = 1.2  # Better visibility
            effects["morale_bonus"] = 0.1
        
        return effects
