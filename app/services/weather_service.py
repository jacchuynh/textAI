"""
Weather Service

This module provides the WeatherService class, which is responsible for generating,
managing, and applying weather conditions throughout the game world.
"""

import logging
import random
import math
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from redis import Redis

from app.models.weather_models import (
    WeatherType, PrecipitationType, WindDirection, VisibilityLevel, WeatherEffectType,
    DBWeatherCondition, DBWeatherPattern, DBActiveWeatherEffect,
    WeatherConditionPydantic, WeatherPatternPydantic, ActiveWeatherEffectPydantic
)
from app.models.time_models import GameDateTime, TimeBlock, Season
from app.services.time_service import TimeService
from app.events.event_bus import event_bus, EventType, GameEvent
from app.db.crud import CRUDBase
from app.async_tasks.celery_app import celery_app

# Configure logging
logger = logging.getLogger(__name__)

# Define CRUD operations for weather models
crud_weather_condition = CRUDBase(DBWeatherCondition)
crud_weather_pattern = CRUDBase(DBWeatherPattern)
crud_weather_effect = CRUDBase(DBActiveWeatherEffect)

# Redis cache keys
WEATHER_CONDITION_CACHE_KEY = "weather_system:condition:{region_id}"
WEATHER_PATTERN_CACHE_KEY = "weather_system:pattern:{region_id}:{season}"

class WeatherService:
    """
    Service class for managing weather in the game world.
    """
    
    def __init__(self, db_session: Session, time_service: TimeService, redis_client: Optional[Redis] = None):
        """
        Initialize the WeatherService.
        
        Args:
            db_session: SQLAlchemy database session
            time_service: TimeService instance for accessing game time
            redis_client: Optional Redis client for caching
        """
        self.db = db_session
        self.time_service = time_service
        self.redis = redis_client
        
        # Subscribe to time-related events
        event_bus.subscribe(EventType.TIME_BLOCK_CHANGED, self._handle_time_block_changed)
        event_bus.subscribe(EventType.SEASON_CHANGED, self._handle_season_changed)
    
    def update_weather_for_all_regions(self) -> Dict[str, WeatherConditionPydantic]:
        """
        Update weather for all configured regions.
        
        Returns:
            Dictionary of region IDs to their new weather conditions
        """
        logger.info("Updating weather for all regions")
        
        # Get all regions from weather patterns
        regions = self._get_all_configured_regions()
        
        # Update weather for each region
        results = {}
        for region_id in regions:
            try:
                new_condition = self._calculate_and_apply_new_weather_for_region(region_id)
                results[region_id] = WeatherConditionPydantic.from_orm(new_condition)
            except Exception as e:
                logger.error(f"Error updating weather for region {region_id}: {e}")
        
        return results
    
    def _calculate_and_apply_new_weather_for_region(self, region_id: str) -> DBWeatherCondition:
        """
        Calculate and apply new weather for a specific region.
        
        Args:
            region_id: The region ID
            
        Returns:
            The new weather condition
        """
        # Get current time and season
        current_time_block = self.time_service.get_current_time_block()
        current_season = self.time_service.get_current_season()
        current_game_time = self.time_service.get_current_datetime()
        
        logger.info(f"Calculating new weather for region {region_id} "
                   f"(TimeBlock: {current_time_block.value}, Season: {current_season.value})")
        
        # Get weather pattern for this region and season
        pattern = self._get_weather_pattern(region_id, current_season.value)
        if not pattern:
            logger.warning(f"No weather pattern found for region {region_id}, season {current_season.value}. "
                         f"Creating default pattern.")
            pattern = self._create_default_weather_pattern(region_id, current_season.value)
        
        # Get current weather condition for the region
        current_condition = self.get_current_weather(region_id)
        
        # Calculate new weather condition
        new_condition = self._generate_weather_condition(
            region_id, 
            pattern, 
            current_time_block,
            current_season,
            current_game_time,
            current_condition
        )
        
        # Save to database
        if current_condition:
            # Update end time for existing weather effects
            self._end_active_weather_effects(current_condition.id, new_condition.timestamp)
        
        # Create database record
        db_condition = crud_weather_condition.create(self.db, obj_in=new_condition)
        
        # Apply weather effects
        self._apply_weather_effects(db_condition)
        
        # Publish weather change event
        self._publish_weather_change_event(db_condition, current_condition)
        
        # Cache the new condition
        if self.redis:
            self._cache_weather_condition(region_id, db_condition)
        
        return db_condition
    
    def get_current_weather(self, region_id: str) -> Optional[DBWeatherCondition]:
        """
        Get the current weather condition for a region.
        
        Args:
            region_id: The region ID
            
        Returns:
            The current weather condition, or None if not found
        """
        # Try to get from cache first
        if self.redis:
            cached = self._get_cached_weather_condition(region_id)
            if cached:
                return cached
        
        # Get from database
        latest = self.db.query(DBWeatherCondition)\
            .filter(DBWeatherCondition.region_id == region_id)\
            .order_by(DBWeatherCondition.timestamp.desc())\
            .first()
        
        return latest
    
    def _apply_weather_effects(self, weather_condition: DBWeatherCondition) -> List[DBActiveWeatherEffect]:
        """
        Apply weather effects based on the weather condition.
        
        Args:
            weather_condition: The weather condition
            
        Returns:
            List of created weather effects
        """
        logger.info(f"Applying weather effects for condition {weather_condition.id} "
                   f"in region {weather_condition.region_id}")
        
        effects = []
        
        # Calculate expected end time
        end_time = weather_condition.timestamp
        if weather_condition.expected_duration_hours:
            end_time += timedelta(hours=weather_condition.expected_duration_hours)
        else:
            # Default to 4 hours if not specified
            end_time += timedelta(hours=4)
        
        # Apply regional effects first
        regional_effects = self._generate_regional_weather_effects(
            weather_condition, 
            end_time
        )
        
        for effect_data in regional_effects:
            effect = crud_weather_effect.create(self.db, obj_in=effect_data)
            effects.append(effect)
        
        # TODO: Apply effects to specific entities (players, NPCs, buildings, etc.)
        # This would likely involve querying for entities in the region and applying
        # weather effects based on their attributes, location, etc.
        
        return effects
    
    def get_active_effects_for_entity(self, entity_id: str, entity_type: str) -> List[DBActiveWeatherEffect]:
        """
        Get active weather effects for a specific entity.
        
        Args:
            entity_id: The entity ID
            entity_type: The entity type
            
        Returns:
            List of active weather effects
        """
        current_time = datetime.utcnow()
        
        return self.db.query(DBActiveWeatherEffect)\
            .filter(
                DBActiveWeatherEffect.target_entity_id == entity_id,
                DBActiveWeatherEffect.target_entity_type == entity_type,
                DBActiveWeatherEffect.calculated_end_time > current_time
            )\
            .all()
    
    def get_active_effects_for_region(self, region_id: str) -> List[DBActiveWeatherEffect]:
        """
        Get active regional weather effects.
        
        Args:
            region_id: The region ID
            
        Returns:
            List of active weather effects
        """
        current_time = datetime.utcnow()
        
        # Get the latest weather condition for the region
        latest_condition = self.get_current_weather(region_id)
        if not latest_condition:
            return []
        
        return self.db.query(DBActiveWeatherEffect)\
            .filter(
                DBActiveWeatherEffect.weather_condition_id == latest_condition.id,
                DBActiveWeatherEffect.target_entity_id.is_(None),  # Regional effects have no target entity
                DBActiveWeatherEffect.calculated_end_time > current_time
            )\
            .all()
    
    def _get_weather_pattern(self, region_id: str, season: str) -> Optional[DBWeatherPattern]:
        """
        Get the weather pattern for a region and season.
        
        Args:
            region_id: The region ID
            season: The season
            
        Returns:
            The weather pattern, or None if not found
        """
        # Try to get from cache first
        if self.redis:
            cached = self._get_cached_weather_pattern(region_id, season)
            if cached:
                return cached
        
        # Get from database
        pattern = self.db.query(DBWeatherPattern)\
            .filter(
                DBWeatherPattern.region_id == region_id,
                DBWeatherPattern.season == season
            )\
            .first()
        
        # Cache if found
        if pattern and self.redis:
            self._cache_weather_pattern(region_id, season, pattern)
        
        return pattern
    
    def _create_default_weather_pattern(self, region_id: str, season: str) -> DBWeatherPattern:
        """
        Create a default weather pattern for a region and season.
        
        Args:
            region_id: The region ID
            season: The season
            
        Returns:
            The created weather pattern
        """
        # Create default probabilities based on season
        if season == "SUMMER":
            weather_probs = {
                "CLEAR": 0.4,
                "PARTLY_CLOUDY": 0.3,
                "CLOUDY": 0.15,
                "LIGHT_RAIN": 0.1,
                "THUNDERSTORM": 0.05
            }
            temp_min, temp_max = 20.0, 35.0
            precip_chances = {"NONE": 0.7, "RAIN": 0.3, "SNOW": 0.0, "HAIL": 0.0}
        elif season == "AUTUMN" or season == "FALL":
            weather_probs = {
                "CLEAR": 0.25,
                "PARTLY_CLOUDY": 0.3,
                "CLOUDY": 0.2,
                "LIGHT_RAIN": 0.15,
                "HEAVY_RAIN": 0.05,
                "FOG": 0.05
            }
            temp_min, temp_max = 10.0, 25.0
            precip_chances = {"NONE": 0.6, "RAIN": 0.4, "SNOW": 0.0, "HAIL": 0.0}
        elif season == "WINTER":
            weather_probs = {
                "CLEAR": 0.25,
                "PARTLY_CLOUDY": 0.2,
                "CLOUDY": 0.25,
                "LIGHT_SNOW": 0.15,
                "HEAVY_SNOW": 0.1,
                "BLIZZARD": 0.05
            }
            temp_min, temp_max = -10.0, 5.0
            precip_chances = {"NONE": 0.5, "RAIN": 0.1, "SNOW": 0.4, "HAIL": 0.0}
        else:  # SPRING
            weather_probs = {
                "CLEAR": 0.3,
                "PARTLY_CLOUDY": 0.3,
                "CLOUDY": 0.15,
                "LIGHT_RAIN": 0.15,
                "HEAVY_RAIN": 0.05,
                "THUNDERSTORM": 0.05
            }
            temp_min, temp_max = 10.0, 25.0
            precip_chances = {"NONE": 0.5, "RAIN": 0.5, "SNOW": 0.0, "HAIL": 0.0}
        
        # Create pattern object
        pattern_data = {
            "region_id": region_id,
            "season": season,
            "weather_type_probabilities": weather_probs,
            "temperature_base_min": temp_min,
            "temperature_base_max": temp_max,
            "humidity_range_min": 0.3,
            "humidity_range_max": 0.8,
            "default_wind_speeds": {
                "min": 5.0,
                "max": 15.0,
                "gust_chance": 0.1,
                "gust_max_multiplier": 1.5
            },
            "precipitation_chances": precip_chances,
            "cloud_cover_range_min": 0.0,
            "cloud_cover_range_max": 1.0,
            "transition_matrices": self._create_default_transition_matrix(weather_probs)
        }
        
        pattern = crud_weather_pattern.create(self.db, obj_in=pattern_data)
        
        # Cache the pattern
        if self.redis:
            self._cache_weather_pattern(region_id, season, pattern)
        
        return pattern
    
    def _create_default_transition_matrix(self, weather_probs: Dict[str, float]) -> Dict[str, List[List[float]]]:
        """
        Create a default weather transition matrix.
        
        Args:
            weather_probs: Dictionary of weather type probabilities
            
        Returns:
            Dictionary mapping each weather type to its transition probabilities
        """
        # Get all possible weather types
        weather_types = list(weather_probs.keys())
        num_types = len(weather_types)
        
        # Create a default matrix with higher probability of staying the same
        # and lower probabilities of transitioning to other types
        transitions = {}
        for i, from_type in enumerate(weather_types):
            row = []
            for j, to_type in enumerate(weather_types):
                if i == j:  # Same type, high probability of staying
                    prob = 0.7
                else:
                    # Distribute remaining 0.3 probability among other types
                    # weighted by their base probabilities
                    base_probs = [weather_probs[t] for t in weather_types if t != from_type]
                    total_base = sum(base_probs)
                    if total_base > 0:
                        prob = 0.3 * (weather_probs[to_type] / total_base)
                    else:
                        prob = 0.3 / (num_types - 1)
                row.append(prob)
            
            # Normalize to ensure row sums to 1.0
            total = sum(row)
            if total > 0:
                row = [p / total for p in row]
            
            transitions[from_type] = row
        
        return transitions
    
    def _generate_weather_condition(
        self, 
        region_id: str, 
        pattern: DBWeatherPattern,
        time_block: TimeBlock,
        season: Season,
        game_time: GameDateTime,
        current_condition: Optional[DBWeatherCondition] = None
    ) -> Dict[str, Any]:
        """
        Generate a new weather condition based on the pattern and current conditions.
        
        Args:
            region_id: The region ID
            pattern: The weather pattern for the region and season
            time_block: The current time block (morning, afternoon, etc.)
            season: The current season
            game_time: The current game time
            current_condition: The current weather condition, if any
            
        Returns:
            Dictionary representing the new weather condition
        """
        # Determine the weather type
        weather_type = self._determine_next_weather_type(pattern, current_condition)
        
        # Determine temperature based on season, time block, and weather type
        temperature = self._calculate_temperature(pattern, time_block, weather_type)
        
        # Determine wind speed and direction
        wind_speed, wind_direction = self._calculate_wind(pattern, weather_type, current_condition)
        
        # Determine precipitation type and intensity
        precip_type, precip_intensity = self._calculate_precipitation(
            pattern, weather_type, temperature, current_condition
        )
        
        # Determine humidity
        humidity = self._calculate_humidity(
            pattern, weather_type, precip_type, precip_intensity, current_condition
        )
        
        # Determine cloud cover
        cloud_cover = self._calculate_cloud_cover(weather_type, current_condition)
        
        # Determine visibility
        visibility = self._calculate_visibility(
            weather_type, precip_type, precip_intensity, cloud_cover, wind_speed
        )
        
        # Calculate "feels like" temperature based on wind and humidity
        temp_feels_like = self._calculate_feels_like_temperature(
            temperature, wind_speed, humidity
        )
        
        # Generate a description
        description = self._generate_weather_description(
            weather_type, 
            temperature,
            wind_speed,
            wind_direction,
            precip_type,
            precip_intensity,
            cloud_cover,
            time_block,
            season
        )
        
        # Determine expected duration
        duration_hours = self._calculate_expected_duration(weather_type)
        
        # Create the new condition
        return {
            "region_id": region_id,
            "timestamp": datetime.utcnow(),  # Use current real time for simplicity
            "weather_type": weather_type,
            "temperature": temperature,
            "temperature_feels_like": temp_feels_like,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "precipitation_type": precip_type,
            "precipitation_intensity": precip_intensity,
            "humidity": humidity,
            "cloud_cover": cloud_cover,
            "visibility": visibility,
            "generated_description": description,
            "expected_duration_hours": duration_hours
        }
    
    def _determine_next_weather_type(
        self, 
        pattern: DBWeatherPattern,
        current_condition: Optional[DBWeatherCondition] = None
    ) -> str:
        """
        Determine the next weather type based on the pattern and current condition.
        
        Args:
            pattern: The weather pattern
            current_condition: The current weather condition, if any
            
        Returns:
            The next weather type
        """
        # If no current condition, select based on base probabilities
        if not current_condition:
            return self._select_random_weather_type(pattern.weather_type_probabilities)
        
        # Use Markov chain transition matrix to determine next state
        current_type = current_condition.weather_type.value
        
        # Check if we have a transition matrix for this type
        if current_type in pattern.transition_matrices:
            transition_row = pattern.transition_matrices[current_type]
            
            # Get all possible weather types
            weather_types = list(pattern.weather_type_probabilities.keys())
            
            # Ensure transition_row length matches weather_types length
            if len(transition_row) == len(weather_types):
                # Select next type based on transition probabilities
                random_value = random.random()
                cumulative_prob = 0.0
                
                for i, prob in enumerate(transition_row):
                    cumulative_prob += prob
                    if random_value <= cumulative_prob:
                        return weather_types[i]
        
        # Fallback to base probabilities if transition matrix not available
        return self._select_random_weather_type(pattern.weather_type_probabilities)
    
    def _select_random_weather_type(self, probabilities: Dict[str, float]) -> str:
        """
        Select a random weather type based on probabilities.
        
        Args:
            probabilities: Dictionary mapping weather types to probabilities
            
        Returns:
            A randomly selected weather type
        """
        random_value = random.random()
        cumulative_prob = 0.0
        
        for weather_type, prob in probabilities.items():
            cumulative_prob += prob
            if random_value <= cumulative_prob:
                return weather_type
        
        # Fallback to a random type if something goes wrong
        return random.choice(list(probabilities.keys()))
    
    def _calculate_temperature(
        self, 
        pattern: DBWeatherPattern,
        time_block: TimeBlock,
        weather_type: str
    ) -> float:
        """
        Calculate temperature based on pattern, time block, and weather type.
        
        Args:
            pattern: The weather pattern
            time_block: The current time block
            weather_type: The weather type
            
        Returns:
            The calculated temperature
        """
        # Get base temperature range from pattern
        base_min = pattern.temperature_base_min
        base_max = pattern.temperature_base_max
        
        # Apply time block modifier
        if time_block == TimeBlock.MORNING:
            # Morning is cooler, closer to min
            base = base_min + (base_max - base_min) * 0.25
            variation = (base_max - base_min) * 0.15
        elif time_block == TimeBlock.AFTERNOON:
            # Afternoon is warmer, closer to max
            base = base_min + (base_max - base_min) * 0.75
            variation = (base_max - base_min) * 0.15
        elif time_block == TimeBlock.EVENING:
            # Evening is cooling down
            base = base_min + (base_max - base_min) * 0.5
            variation = (base_max - base_min) * 0.15
        else:  # NIGHT
            # Night is coolest, at or below min
            base = base_min
            variation = (base_max - base_min) * 0.1
        
        # Apply weather type modifier
        if weather_type in ["CLEAR", "PARTLY_CLOUDY"]:
            # Clear weather has more temperature variation
            modifier = random.uniform(-variation, variation)
        elif weather_type in ["CLOUDY", "LIGHT_RAIN", "LIGHT_SNOW"]:
            # Clouds moderate temperature
            modifier = random.uniform(-variation * 0.7, variation * 0.5)
        elif weather_type in ["HEAVY_RAIN", "HEAVY_SNOW", "THUNDERSTORM", "BLIZZARD"]:
            # These typically lower temperature
            modifier = random.uniform(-variation * 1.2, 0)
        else:
            modifier = random.uniform(-variation * 0.5, variation * 0.5)
        
        # Calculate final temperature
        temperature = base + modifier
        
        # Round to one decimal place
        return round(temperature, 1)
    
    def _calculate_wind(
        self, 
        pattern: DBWeatherPattern,
        weather_type: str,
        current_condition: Optional[DBWeatherCondition] = None
    ) -> Tuple[float, str]:
        """
        Calculate wind speed and direction.
        
        Args:
            pattern: The weather pattern
            weather_type: The weather type
            current_condition: The current weather condition, if any
            
        Returns:
            Tuple of (wind_speed, wind_direction)
        """
        # Get wind speed range from pattern
        min_speed = pattern.default_wind_speeds.get("min", 0)
        max_speed = pattern.default_wind_speeds.get("max", 10)
        gust_chance = pattern.default_wind_speeds.get("gust_chance", 0.1)
        gust_multiplier = pattern.default_wind_speeds.get("gust_max_multiplier", 1.5)
        
        # Apply weather type modifier
        if weather_type in ["CLEAR", "PARTLY_CLOUDY", "LIGHT_RAIN", "LIGHT_SNOW"]:
            # These typically have lighter winds
            wind_range = (min_speed, min_speed + (max_speed - min_speed) * 0.5)
        elif weather_type in ["CLOUDY", "FOG", "HEAVY_RAIN", "HEAVY_SNOW"]:
            # Medium winds
            wind_range = (min_speed + (max_speed - min_speed) * 0.2, max_speed)
        elif weather_type in ["THUNDERSTORM", "BLIZZARD", "GALE", "WINDY", "DUST_STORM"]:
            # Strong winds
            wind_range = (max_speed * 0.7, max_speed * 1.2)
        else:
            wind_range = (min_speed, max_speed)
        
        # Calculate base wind speed
        base_wind_speed = random.uniform(wind_range[0], wind_range[1])
        
        # Check for gusts
        if random.random() < gust_chance:
            wind_speed = base_wind_speed * random.uniform(1.0, gust_multiplier)
        else:
            wind_speed = base_wind_speed
        
        # Determine wind direction
        if current_condition:
            # 70% chance of keeping similar direction, 30% chance of changing
            if random.random() < 0.7:
                current_dir = current_condition.wind_direction.value
                directions = list(WindDirection)
                current_idx = next(i for i, d in enumerate(directions) if d.value == current_dir)
                
                # Get adjacent directions (wrap around if needed)
                options = [
                    directions[current_idx],  # Same direction
                    directions[(current_idx - 1) % len(directions)],  # Shift left
                    directions[(current_idx + 1) % len(directions)]   # Shift right
                ]
                wind_direction = random.choice(options).value
            else:
                wind_direction = random.choice(list(WindDirection)).value
        else:
            wind_direction = random.choice(list(WindDirection)).value
        
        # Round wind speed to one decimal place
        return round(wind_speed, 1), wind_direction
    
    def _calculate_precipitation(
        self, 
        pattern: DBWeatherPattern,
        weather_type: str,
        temperature: float,
        current_condition: Optional[DBWeatherCondition] = None
    ) -> Tuple[str, float]:
        """
        Calculate precipitation type and intensity.
        
        Args:
            pattern: The weather pattern
            weather_type: The weather type
            temperature: The current temperature
            current_condition: The current weather condition, if any
            
        Returns:
            Tuple of (precipitation_type, intensity)
        """
        # Determine precipitation type based on weather type and temperature
        if weather_type in ["CLEAR", "PARTLY_CLOUDY", "CLOUDY", "FOG", "WINDY", "DUST_STORM"]:
            # These typically don't have precipitation
            return "NONE", 0.0
        
        elif weather_type in ["LIGHT_RAIN", "HEAVY_RAIN", "THUNDERSTORM"]:
            # Rain types
            precip_type = "RAIN"
            
            # Determine intensity
            if weather_type == "LIGHT_RAIN":
                intensity_range = (0.1, 0.3)
            elif weather_type == "HEAVY_RAIN":
                intensity_range = (0.5, 0.8)
            else:  # THUNDERSTORM
                intensity_range = (0.7, 1.0)
                
                # Small chance of hail in a thunderstorm
                if random.random() < 0.15:
                    precip_type = "HAIL"
        
        elif weather_type in ["LIGHT_SNOW", "HEAVY_SNOW", "BLIZZARD"]:
            # Snow types
            # But check temperature - if it's above freezing, it might be rain instead
            if temperature > 0:
                precip_type = "RAIN"
            else:
                precip_type = "SNOW"
            
            # Determine intensity
            if weather_type == "LIGHT_SNOW":
                intensity_range = (0.1, 0.3)
            elif weather_type == "HEAVY_SNOW":
                intensity_range = (0.5, 0.8)
            else:  # BLIZZARD
                intensity_range = (0.7, 1.0)
        
        elif weather_type == "HAIL":
            # Explicit hail
            precip_type = "HAIL"
            intensity_range = (0.4, 0.9)
        
        else:
            # Default - should not happen with proper weather types
            precip_type = "NONE"
            intensity_range = (0.0, 0.0)
        
        # Calculate intensity within the determined range
        if precip_type == "NONE":
            intensity = 0.0
        else:
            # If there's a current condition with the same precipitation type,
            # make intensity somewhat continuous
            if (current_condition and 
                current_condition.precipitation_type.value == precip_type and
                current_condition.precipitation_intensity > 0):
                
                current_intensity = current_condition.precipitation_intensity
                min_intensity = max(intensity_range[0], current_intensity * 0.7)
                max_intensity = min(intensity_range[1], current_intensity * 1.3)
                
                intensity = random.uniform(min_intensity, max_intensity)
            else:
                intensity = random.uniform(intensity_range[0], intensity_range[1])
        
        # Round intensity to two decimal places
        return precip_type, round(intensity, 2)
    
    def _calculate_humidity(
        self, 
        pattern: DBWeatherPattern,
        weather_type: str,
        precip_type: str,
        precip_intensity: float,
        current_condition: Optional[DBWeatherCondition] = None
    ) -> float:
        """
        Calculate humidity.
        
        Args:
            pattern: The weather pattern
            weather_type: The weather type
            precip_type: The precipitation type
            precip_intensity: The precipitation intensity
            current_condition: The current weather condition, if any
            
        Returns:
            The calculated humidity (0-1)
        """
        # Get base humidity range from pattern
        min_humidity = pattern.humidity_range_min
        max_humidity = pattern.humidity_range_max
        
        # Adjust base range based on weather type and precipitation
        if precip_type != "NONE":
            # Higher humidity with precipitation
            base_humidity = min_humidity + (max_humidity - min_humidity) * 0.7
            # Increase further based on intensity
            base_humidity += (max_humidity - base_humidity) * precip_intensity
        elif weather_type in ["FOG", "CLOUDY"]:
            # These typically have higher humidity
            base_humidity = min_humidity + (max_humidity - min_humidity) * 0.6
        elif weather_type == "PARTLY_CLOUDY":
            # Medium humidity
            base_humidity = min_humidity + (max_humidity - min_humidity) * 0.4
        elif weather_type == "CLEAR":
            # Lower humidity
            base_humidity = min_humidity + (max_humidity - min_humidity) * 0.2
        else:
            # Default
            base_humidity = min_humidity + (max_humidity - min_humidity) * 0.5
        
        # Apply some random variation
        variation = (max_humidity - min_humidity) * 0.1
        humidity = base_humidity + random.uniform(-variation, variation)
        
        # Ensure within bounds
        humidity = max(min_humidity, min(max_humidity, humidity))
        
        # If there's a current condition, make humidity somewhat continuous
        if current_condition:
            current_humidity = current_condition.humidity
            # Blend current and calculated
            humidity = current_humidity * 0.6 + humidity * 0.4
        
        # Round to two decimal places
        return round(humidity, 2)
    
    def _calculate_cloud_cover(
        self, 
        weather_type: str,
        current_condition: Optional[DBWeatherCondition] = None
    ) -> float:
        """
        Calculate cloud cover.
        
        Args:
            weather_type: The weather type
            current_condition: The current weather condition, if any
            
        Returns:
            The calculated cloud cover (0-1)
        """
        # Determine base cloud cover from weather type
        if weather_type == "CLEAR":
            base_cover = 0.0
            variation = 0.1
        elif weather_type == "PARTLY_CLOUDY":
            base_cover = 0.4
            variation = 0.2
        elif weather_type == "CLOUDY":
            base_cover = 0.8
            variation = 0.15
        elif weather_type in ["LIGHT_RAIN", "LIGHT_SNOW"]:
            base_cover = 0.7
            variation = 0.15
        elif weather_type in ["HEAVY_RAIN", "HEAVY_SNOW", "THUNDERSTORM", "BLIZZARD"]:
            base_cover = 0.9
            variation = 0.1
        elif weather_type == "FOG":
            base_cover = 0.6  # Fog doesn't necessarily mean full cloud cover
            variation = 0.2
        else:
            base_cover = 0.5
            variation = 0.3
        
        # Apply random variation
        cloud_cover = base_cover + random.uniform(-variation, variation)
        
        # Ensure within bounds
        cloud_cover = max(0.0, min(1.0, cloud_cover))
        
        # If there's a current condition, make cloud cover somewhat continuous
        if current_condition:
            current_cover = current_condition.cloud_cover
            # Blend current and calculated
            cloud_cover = current_cover * 0.7 + cloud_cover * 0.3
        
        # Round to two decimal places
        return round(cloud_cover, 2)
    
    def _calculate_visibility(
        self, 
        weather_type: str,
        precip_type: str,
        precip_intensity: float,
        cloud_cover: float,
        wind_speed: float
    ) -> str:
        """
        Calculate visibility level.
        
        Args:
            weather_type: The weather type
            precip_type: The precipitation type
            precip_intensity: The precipitation intensity
            cloud_cover: The cloud cover
            wind_speed: The wind speed
            
        Returns:
            The visibility level
        """
        # Start with base visibility score (0-100)
        visibility_score = 100
        
        # Reduce for various factors
        if weather_type == "FOG":
            visibility_score -= 70  # Major reduction for fog
        
        if precip_type != "NONE":
            # Reduce based on precipitation intensity
            visibility_score -= precip_intensity * 50
        
        if cloud_cover > 0.5:
            # Reduce somewhat for heavy cloud cover
            visibility_score -= (cloud_cover - 0.5) * 20
        
        if weather_type in ["DUST_STORM", "BLIZZARD"]:
            # Major reduction for these types
            visibility_score -= 60
        
        if wind_speed > 20:
            # High winds can reduce visibility (dust, blowing snow, etc.)
            visibility_score -= (wind_speed - 20) * 2
        
        # Ensure within bounds
        visibility_score = max(0, min(100, visibility_score))
        
        # Map to visibility levels
        if visibility_score >= 80:
            return "EXCELLENT"
        elif visibility_score >= 60:
            return "GOOD"
        elif visibility_score >= 40:
            return "MODERATE"
        elif visibility_score >= 20:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def _calculate_feels_like_temperature(
        self, 
        temperature: float,
        wind_speed: float,
        humidity: float
    ) -> float:
        """
        Calculate "feels like" temperature considering wind chill and heat index.
        
        Args:
            temperature: The actual temperature (Celsius)
            wind_speed: The wind speed
            humidity: The humidity (0-1)
            
        Returns:
            The "feels like" temperature
        """
        if temperature <= 10:
            # Wind chill effect (simplified approximation)
            if wind_speed >= 5:
                wind_chill = 13.12 + 0.6215 * temperature - 11.37 * wind_speed**0.16 + 0.3965 * temperature * wind_speed**0.16
                return round(wind_chill, 1)
            return temperature
        
        elif temperature >= 25:
            # Heat index effect (simplified approximation)
            if humidity >= 0.4:
                heat_index = temperature + (humidity * 0.5) * (temperature - 24)
                return round(heat_index, 1)
            return temperature
        
        else:
            # No significant modification in the comfortable range
            return temperature
    
    def _calculate_expected_duration(self, weather_type: str) -> float:
        """
        Calculate expected duration of the weather condition.
        
        Args:
            weather_type: The weather type
            
        Returns:
            Expected duration in hours
        """
        # Different weather types have different typical durations
        if weather_type in ["CLEAR", "CLOUDY"]:
            # These tend to last longer
            base_duration = 6.0
            variation = 4.0
        elif weather_type in ["PARTLY_CLOUDY", "LIGHT_RAIN", "LIGHT_SNOW"]:
            # Medium duration
            base_duration = 4.0
            variation = 2.0
        elif weather_type in ["HEAVY_RAIN", "HEAVY_SNOW"]:
            # These typically don't last as long
            base_duration = 3.0
            variation = 1.5
        elif weather_type in ["THUNDERSTORM", "BLIZZARD", "HAIL"]:
            # These are usually brief
            base_duration = 1.5
            variation = 1.0
        elif weather_type == "FOG":
            # Fog often burns off after a few hours
            base_duration = 3.0
            variation = 2.0
        else:
            # Default
            base_duration = 4.0
            variation = 2.0
        
        # Apply some random variation
        duration = base_duration + random.uniform(-variation, variation)
        
        # Ensure positive
        duration = max(0.5, duration)
        
        # Round to one decimal place
        return round(duration, 1)
    
    def _generate_weather_description(
        self, 
        weather_type: str,
        temperature: float,
        wind_speed: float,
        wind_direction: str,
        precip_type: str,
        precip_intensity: float,
        cloud_cover: float,
        time_block: TimeBlock,
        season: Season
    ) -> str:
        """
        Generate a descriptive string for the weather.
        
        Args:
            Various weather parameters
            
        Returns:
            A descriptive string
        """
        # This could be much more sophisticated with templates, NLG, etc.
        # For now, we'll use a simple template approach
        
        # Sky description
        if cloud_cover < 0.2:
            sky = "clear"
        elif cloud_cover < 0.5:
            sky = "partly cloudy"
        elif cloud_cover < 0.8:
            sky = "mostly cloudy"
        else:
            sky = "overcast"
        
        # Precipitation description
        if precip_type == "NONE":
            precip_desc = ""
        elif precip_type == "RAIN":
            if precip_intensity < 0.3:
                precip_desc = "with a light drizzle"
            elif precip_intensity < 0.7:
                precip_desc = "with steady rainfall"
            else:
                precip_desc = "with heavy downpour"
        elif precip_type == "SNOW":
            if precip_intensity < 0.3:
                precip_desc = "with light snowflakes drifting down"
            elif precip_intensity < 0.7:
                precip_desc = "with steady snowfall"
            else:
                precip_desc = "with heavy snow"
        elif precip_type == "HAIL":
            precip_desc = "with hailstones falling"
        
        # Wind description
        if wind_speed < 5:
            wind_desc = "The air is still"
        elif wind_speed < 15:
            wind_desc = f"A gentle breeze blows from the {wind_direction}"
        elif wind_speed < 30:
            wind_desc = f"Strong winds blow from the {wind_direction}"
        else:
            wind_desc = f"Powerful gusts howl from the {wind_direction}"
        
        # Temperature description
        if temperature < 0:
            temp_desc = "freezing cold"
        elif temperature < 10:
            temp_desc = "cold"
        elif temperature < 20:
            temp_desc = "cool"
        elif temperature < 30:
            temp_desc = "warm"
        else:
            temp_desc = "hot"
        
        # Time of day flavor
        if time_block == TimeBlock.MORNING:
            time_desc = "The morning sky is"
        elif time_block == TimeBlock.AFTERNOON:
            time_desc = "The afternoon sky is"
        elif time_block == TimeBlock.EVENING:
            time_desc = "The evening sky is"
        else:  # NIGHT
            time_desc = "The night sky is"
        
        # Seasonal flavor
        if season == Season.SPRING:
            season_desc = "Spring flowers sway"
        elif season == Season.SUMMER:
            season_desc = "Summer heat radiates"
        elif season == Season.AUTUMN:
            season_desc = "Autumn leaves rustle"
        else:  # WINTER
            season_desc = "Winter's chill pervades"
        
        # Special case descriptions for certain weather types
        if weather_type == "FOG":
            return f"A thick fog blankets the area, limiting visibility. {wind_desc}. The air feels {temp_desc}."
        
        elif weather_type == "THUNDERSTORM":
            return f"Thunder rumbles as lightning flashes across the dark sky. {precip_desc}. {wind_desc}. The air feels {temp_desc} and charged with energy."
        
        elif weather_type == "BLIZZARD":
            return f"A blizzard rages with swirling snow severely limiting visibility. {wind_desc}. The air is bitterly {temp_desc}."
        
        elif weather_type == "DUST_STORM":
            return f"A dust storm sweeps through, carrying particles of dirt and debris. {wind_desc}. The air feels {temp_desc} and gritty."
        
        # Standard description template
        desc = f"{time_desc} {sky}"
        if precip_desc:
            desc += f" {precip_desc}"
        desc += f". {wind_desc}. {season_desc} as the temperature feels {temp_desc}."
        
        return desc
    
    def _generate_regional_weather_effects(
        self, 
        weather_condition: DBWeatherCondition,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generate weather effects for a region.
        
        Args:
            weather_condition: The weather condition
            end_time: When the effects should end
            
        Returns:
            List of weather effect data dictionaries
        """
        effects = []
        weather_type = weather_condition.weather_type.value
        
        # Common effect data
        base_effect = {
            "weather_condition_id": weather_condition.id,
            "start_time": weather_condition.timestamp,
            "calculated_end_time": end_time,
        }
        
        # Movement effects
        if weather_type in ["HEAVY_RAIN", "HEAVY_SNOW", "BLIZZARD"]:
            movement_modifier = {"multiplier": 0.5}  # 50% slower
            if weather_type == "BLIZZARD":
                movement_modifier = {"multiplier": 0.3}  # 70% slower
            
            effects.append({
                **base_effect,
                "effect_type": "MOVEMENT_PENALTY",
                "modifier_value": movement_modifier,
                "description": f"Movement slowed due to {weather_type.lower().replace('_', ' ')}"
            })
        
        # Visibility effects
        if weather_type in ["FOG", "HEAVY_RAIN", "HEAVY_SNOW", "BLIZZARD", "DUST_STORM"]:
            visibility_modifier = {"range_reduction": 0.5}  # 50% reduction
            if weather_type in ["BLIZZARD", "DUST_STORM"]:
                visibility_modifier = {"range_reduction": 0.8}  # 80% reduction
            
            effects.append({
                **base_effect,
                "effect_type": "VISIBILITY_REDUCTION",
                "modifier_value": visibility_modifier,
                "description": f"Visibility reduced due to {weather_type.lower().replace('_', ' ')}"
            })
        
        # Resource gathering effects
        if weather_condition.precipitation_type.value != "NONE" or weather_type in ["WINDY", "GALE"]:
            resource_modifier = {"difficulty_increase": 0.3}  # 30% harder
            
            effects.append({
                **base_effect,
                "effect_type": "RESOURCE_GATHERING_DIFFICULTY",
                "modifier_value": resource_modifier,
                "description": f"Resource gathering more difficult due to {weather_type.lower().replace('_', ' ')}"
            })
        
        # Comfort/warmth effects for extreme temperatures
        if weather_condition.temperature < 5:
            # Cold weather
            warmth_modifier = {"loss_rate": 0.2}
            if weather_condition.temperature < 0:
                warmth_modifier = {"loss_rate": 0.4}
            
            effects.append({
                **base_effect,
                "effect_type": "WARMTH_LOSS",
                "modifier_value": warmth_modifier,
                "description": "Warmth drains quickly in the cold temperature"
            })
        
        elif weather_condition.temperature > 30:
            # Hot weather
            comfort_modifier = {"decrease_rate": 0.2}
            
            effects.append({
                **base_effect,
                "effect_type": "COMFORT_DECREASE",
                "modifier_value": comfort_modifier,
                "description": "Comfort decreases in the oppressive heat"
            })
        
        # Combat advantage for certain weather types
        if weather_type in ["THUNDERSTORM", "BLIZZARD", "DUST_STORM"]:
            advantage_modifier = {"concealment_bonus": 0.3}
            
            effects.append({
                **base_effect,
                "effect_type": "COMBAT_ADVANTAGE",
                "modifier_value": advantage_modifier,
                "description": f"The {weather_type.lower().replace('_', ' ')} provides concealment in combat"
            })
        
        # Spell effectiveness modifications
        if weather_type in ["THUNDERSTORM", "HEAVY_RAIN", "HEAVY_SNOW", "BLIZZARD"]:
            # Define which types of magic are enhanced or weakened
            spell_modifier = {}
            
            if weather_type == "THUNDERSTORM":
                spell_modifier = {
                    "lightning_boost": 0.3,
                    "fire_penalty": 0.2
                }
            elif weather_type in ["HEAVY_RAIN", "HEAVY_SNOW", "BLIZZARD"]:
                spell_modifier = {
                    "water_boost": 0.2,
                    "ice_boost": 0.3 if weather_type in ["HEAVY_SNOW", "BLIZZARD"] else 0.1,
                    "fire_penalty": 0.3
                }
            
            effects.append({
                **base_effect,
                "effect_type": "SPELL_EFFECTIVENESS",
                "modifier_value": spell_modifier,
                "description": f"The {weather_type.lower().replace('_', ' ')} affects magical energies"
            })
        
        # Perception penalties
        if weather_condition.visibility in ["POOR", "VERY_POOR"]:
            perception_modifier = {"penalty": 0.3}
            if weather_condition.visibility == "VERY_POOR":
                perception_modifier = {"penalty": 0.5}
            
            effects.append({
                **base_effect,
                "effect_type": "PERCEPTION_PENALTY",
                "modifier_value": perception_modifier,
                "description": "Poor visibility makes it difficult to notice details"
            })
        
        return effects
    
    def _end_active_weather_effects(self, old_condition_id: int, new_timestamp: datetime) -> None:
        """
        End active weather effects from the previous condition.
        
        Args:
            old_condition_id: ID of the previous weather condition
            new_timestamp: Timestamp when the new condition begins
        """
        active_effects = self.db.query(DBActiveWeatherEffect)\
            .filter(
                DBActiveWeatherEffect.weather_condition_id == old_condition_id,
                DBActiveWeatherEffect.calculated_end_time > new_timestamp
            )\
            .all()
        
        for effect in active_effects:
            effect.calculated_end_time = new_timestamp
            self.db.add(effect)
        
        self.db.commit()
    
    def _get_all_configured_regions(self) -> List[str]:
        """
        Get all regions that have weather patterns configured.
        
        Returns:
            List of region IDs
        """
        regions = self.db.query(DBWeatherPattern.region_id)\
            .distinct()\
            .all()
        
        return [r[0] for r in regions]
    
    def _handle_time_block_changed(self, event: GameEvent) -> None:
        """
        Handle a time block changed event.
        
        Args:
            event: The event
        """
        logger.info(f"Time block changed to {event.context.get('new_time_block')}")
        
        # Every time block change, there's a chance of weather changing
        # We'll update weather for all regions
        # This could potentially be moved to a Celery task if needed
        self.update_weather_for_all_regions()
    
    def _handle_season_changed(self, event: GameEvent) -> None:
        """
        Handle a season changed event.
        
        Args:
            event: The event
        """
        logger.info(f"Season changed to {event.context.get('new_season')}")
        
        # Season changes always trigger weather updates
        self.update_weather_for_all_regions()
    
    def _publish_weather_change_event(
        self, 
        new_condition: DBWeatherCondition,
        previous_condition: Optional[DBWeatherCondition]
    ) -> None:
        """
        Publish a weather change event.
        
        Args:
            new_condition: The new weather condition
            previous_condition: The previous weather condition, if any
        """
        # Convert to Pydantic models for the event payload
        new_pydantic = WeatherConditionPydantic.from_orm(new_condition)
        previous_pydantic = None
        if previous_condition:
            previous_pydantic = WeatherConditionPydantic.from_orm(previous_condition)
        
        # Create and publish the event
        event = GameEvent(
            event_type=EventType.WEATHER_CHANGE,
            source_id="weather_service",
            target_id=new_condition.region_id,
            context={
                "region_id": new_condition.region_id,
                "previous_weather_condition": previous_pydantic.dict() if previous_pydantic else None,
                "current_weather_condition": new_pydantic.dict()
            }
        )
        
        event_bus.publish(event)
    
    # Redis caching methods
    def _get_cached_weather_condition(self, region_id: str) -> Optional[DBWeatherCondition]:
        """
        Get a cached weather condition from Redis.
        
        Args:
            region_id: The region ID
            
        Returns:
            The cached weather condition, or None if not found
        """
        if not self.redis:
            return None
        
        key = WEATHER_CONDITION_CACHE_KEY.format(region_id=region_id)
        cached = self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                # Convert the dictionary back to a DBWeatherCondition
                condition = DBWeatherCondition()
                
                # Set attributes from the cached data
                for attr, value in data.items():
                    if attr == "timestamp" and value:
                        value = datetime.fromisoformat(value)
                    elif attr == "weather_type" and value:
                        value = WeatherType(value)
                    elif attr == "wind_direction" and value:
                        value = WindDirection(value)
                    elif attr == "precipitation_type" and value:
                        value = PrecipitationType(value)
                    elif attr == "visibility" and value:
                        value = VisibilityLevel(value)
                    
                    setattr(condition, attr, value)
                
                return condition
            
            except Exception as e:
                logger.error(f"Error deserializing cached weather condition: {e}")
                return None
        
        return None
    
    def _cache_weather_condition(self, region_id: str, condition: DBWeatherCondition) -> None:
        """
        Cache a weather condition in Redis.
        
        Args:
            region_id: The region ID
            condition: The weather condition to cache
        """
        if not self.redis:
            return
        
        key = WEATHER_CONDITION_CACHE_KEY.format(region_id=region_id)
        
        try:
            # Convert to a serializable dictionary
            data = condition.to_dict()
            
            # Cache with expiration (e.g., 1 hour)
            self.redis.setex(key, 3600, json.dumps(data))
            
        except Exception as e:
            logger.error(f"Error caching weather condition: {e}")
    
    def _get_cached_weather_pattern(self, region_id: str, season: str) -> Optional[DBWeatherPattern]:
        """
        Get a cached weather pattern from Redis.
        
        Args:
            region_id: The region ID
            season: The season
            
        Returns:
            The cached weather pattern, or None if not found
        """
        if not self.redis:
            return None
        
        key = WEATHER_PATTERN_CACHE_KEY.format(region_id=region_id, season=season)
        cached = self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                # Convert the dictionary back to a DBWeatherPattern
                pattern = DBWeatherPattern()
                
                # Set attributes from the cached data
                for attr, value in data.items():
                    setattr(pattern, attr, value)
                
                return pattern
            
            except Exception as e:
                logger.error(f"Error deserializing cached weather pattern: {e}")
                return None
        
        return None
    
    def _cache_weather_pattern(self, region_id: str, season: str, pattern: DBWeatherPattern) -> None:
        """
        Cache a weather pattern in Redis.
        
        Args:
            region_id: The region ID
            season: The season
            pattern: The weather pattern to cache
        """
        if not self.redis:
            return
        
        key = WEATHER_PATTERN_CACHE_KEY.format(region_id=region_id, season=season)
        
        try:
            # Convert to a serializable dictionary
            data = pattern.to_dict()
            
            # Cache with long expiration (e.g., 1 day) since patterns change rarely
            self.redis.setex(key, 86400, json.dumps(data))
            
        except Exception as e:
            logger.error(f"Error caching weather pattern: {e}")
            
# Optional: Create Celery task for updating weather
@celery_app.task
def update_weather_task(game_id: str) -> Dict[str, Any]:
    """
    Celery task for updating weather in all regions.
    
    Args:
        game_id: The game ID
        
    Returns:
        Dictionary with results
    """
    from app.db.base import SessionLocal
    from app.services.time_service import TimeService
    from app.models.time_models import GameTimeSettings
    
    logger.info(f"Running scheduled weather update task for game {game_id}")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Create services
            time_service = TimeService(db, GameTimeSettings(), game_id)
            weather_service = WeatherService(db, time_service)
            
            # Update weather for all regions
            results = weather_service.update_weather_for_all_regions()
            
            return {
                "success": True,
                "regions_updated": len(results),
                "details": {region: condition.dict() for region, condition in results.items()}
            }
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in weather update task: {e}")
        return {
            "success": False,
            "error": str(e)
        }