"""
Weather System Test Script

This script demonstrates the functionality of the Weather System and its integration
with the Time System. It shows how weather conditions are generated, cached, and how
they change in response to time progression.
"""

import logging
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random

from app.db.base import Base, engine, SessionLocal
from app.models.time_models import GameDateTime, TimeBlock, Season, GameTimeSettings
from app.models.weather_models import (
    WeatherType, PrecipitationType, WindDirection, VisibilityLevel, WeatherEffectType,
    DBWeatherCondition, DBWeatherPattern, DBActiveWeatherEffect
)
from app.services.time_service import TimeService
from app.services.weather_service import WeatherService
from app.events.event_bus import event_bus, EventType, GameEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("weather_system_test")

# Create tables in the database
Base.metadata.create_all(bind=engine)

def setup_test_regions(db: Session) -> None:
    """
    Set up test regions with default weather patterns.
    
    Args:
        db: Database session
    """
    logger.info("Setting up test regions with default weather patterns")
    
    # Define test regions
    regions = [
        "forest_region",
        "mountain_region",
        "coastal_region",
        "desert_region"
    ]
    
    # For each region, create weather patterns for all seasons
    for region_id in regions:
        for season in ["SPRING", "SUMMER", "AUTUMN", "WINTER"]:
            # Check if pattern already exists
            existing = db.query(DBWeatherPattern).filter(
                DBWeatherPattern.region_id == region_id,
                DBWeatherPattern.season == season
            ).first()
            
            if not existing:
                # Create custom pattern data for this region and season
                pattern_data = create_custom_weather_pattern(region_id, season)
                
                # Create the pattern in the database
                pattern = DBWeatherPattern(**pattern_data)
                db.add(pattern)
    
    # Commit changes
    db.commit()
    logger.info("Test regions set up successfully")

def create_custom_weather_pattern(region_id: str, season: str) -> dict:
    """
    Create custom weather pattern data for a region and season.
    
    Args:
        region_id: The region ID
        season: The season
        
    Returns:
        Weather pattern data dictionary
    """
    # Base weather probabilities, will be modified based on region and season
    base_weather_probs = {
        "CLEAR": 0.3,
        "PARTLY_CLOUDY": 0.25,
        "CLOUDY": 0.15,
        "LIGHT_RAIN": 0.1,
        "HEAVY_RAIN": 0.05,
        "THUNDERSTORM": 0.03,
        "FOG": 0.05,
        "LIGHT_SNOW": 0.03,
        "HEAVY_SNOW": 0.02,
        "BLIZZARD": 0.01,
        "WINDY": 0.08,
        "GALE": 0.02,
        "DUST_STORM": 0.01,
        "HAIL": 0.01
    }
    
    # Region-specific customizations
    if region_id == "forest_region":
        # Forests have more rain and fog, less wind
        base_weather_probs["LIGHT_RAIN"] += 0.1
        base_weather_probs["HEAVY_RAIN"] += 0.05
        base_weather_probs["FOG"] += 0.1
        base_weather_probs["WINDY"] -= 0.05
        base_weather_probs["GALE"] -= 0.01
        base_weather_probs["DUST_STORM"] = 0
        temp_modifier = 0  # Average temperatures
        
    elif region_id == "mountain_region":
        # Mountains have more snow, wind, and storms
        base_weather_probs["LIGHT_SNOW"] += 0.1
        base_weather_probs["HEAVY_SNOW"] += 0.05
        base_weather_probs["BLIZZARD"] += 0.02
        base_weather_probs["WINDY"] += 0.1
        base_weather_probs["GALE"] += 0.05
        base_weather_probs["THUNDERSTORM"] += 0.02
        temp_modifier = -10  # Colder temperatures
        
    elif region_id == "coastal_region":
        # Coastal areas have more fog, wind, and rain
        base_weather_probs["FOG"] += 0.1
        base_weather_probs["WINDY"] += 0.1
        base_weather_probs["GALE"] += 0.05
        base_weather_probs["LIGHT_RAIN"] += 0.05
        base_weather_probs["HEAVY_RAIN"] += 0.03
        base_weather_probs["DUST_STORM"] = 0
        temp_modifier = -5  # Slightly cooler due to sea breeze
        
    elif region_id == "desert_region":
        # Deserts have more clear skies, dust storms, and less precipitation
        base_weather_probs["CLEAR"] += 0.2
        base_weather_probs["DUST_STORM"] += 0.1
        base_weather_probs["LIGHT_RAIN"] -= 0.07
        base_weather_probs["HEAVY_RAIN"] -= 0.04
        base_weather_probs["THUNDERSTORM"] -= 0.02
        base_weather_probs["FOG"] -= 0.04
        base_weather_probs["LIGHT_SNOW"] = 0
        base_weather_probs["HEAVY_SNOW"] = 0
        base_weather_probs["BLIZZARD"] = 0
        temp_modifier = 10  # Hotter temperatures
    
    else:
        # Default
        temp_modifier = 0
    
    # Season-specific customizations
    if season == "SPRING":
        # Spring has more rain, less extreme conditions
        base_weather_probs["LIGHT_RAIN"] += 0.05
        base_weather_probs["THUNDERSTORM"] += 0.02
        base_weather_probs["BLIZZARD"] -= 0.01
        base_weather_probs["DUST_STORM"] -= 0.01
        base_weather_probs["GALE"] -= 0.01
        temp_range = (10 + temp_modifier, 25 + temp_modifier)
        precip_chances = {"NONE": 0.5, "RAIN": 0.45, "SNOW": 0.04, "HAIL": 0.01}
        
    elif season == "SUMMER":
        # Summer has more clear skies, thunderstorms
        base_weather_probs["CLEAR"] += 0.1
        base_weather_probs["PARTLY_CLOUDY"] += 0.05
        base_weather_probs["THUNDERSTORM"] += 0.03
        base_weather_probs["LIGHT_SNOW"] -= 0.03
        base_weather_probs["HEAVY_SNOW"] -= 0.02
        base_weather_probs["BLIZZARD"] -= 0.01
        temp_range = (20 + temp_modifier, 35 + temp_modifier)
        precip_chances = {"NONE": 0.6, "RAIN": 0.38, "SNOW": 0.0, "HAIL": 0.02}
        
    elif season == "AUTUMN" or season == "FALL":
        # Autumn has more wind, clouds
        base_weather_probs["WINDY"] += 0.05
        base_weather_probs["CLOUDY"] += 0.05
        base_weather_probs["FOG"] += 0.02
        temp_range = (5 + temp_modifier, 20 + temp_modifier)
        precip_chances = {"NONE": 0.55, "RAIN": 0.4, "SNOW": 0.04, "HAIL": 0.01}
        
    else:  # WINTER
        # Winter has more snow, clouds, less clear skies
        base_weather_probs["LIGHT_SNOW"] += 0.1
        base_weather_probs["HEAVY_SNOW"] += 0.05
        base_weather_probs["BLIZZARD"] += 0.01
        base_weather_probs["CLOUDY"] += 0.05
        base_weather_probs["CLEAR"] -= 0.1
        base_weather_probs["PARTLY_CLOUDY"] -= 0.05
        temp_range = (-10 + temp_modifier, 5 + temp_modifier)
        precip_chances = {"NONE": 0.4, "RAIN": 0.1, "SNOW": 0.48, "HAIL": 0.02}
    
    # Normalize weather probabilities
    total_prob = sum(base_weather_probs.values())
    normalized_probs = {k: v / total_prob for k, v in base_weather_probs.items()}
    
    # Create transition matrices (simplified for test)
    # This would be more sophisticated in a real implementation
    transition_matrices = {}
    for weather_type in normalized_probs.keys():
        # Each weather type has a 70% chance of staying the same
        transition_row = {}
        for other_type in normalized_probs.keys():
            if other_type == weather_type:
                transition_row[other_type] = 0.7
            else:
                # Distribute remaining 0.3 based on base probabilities
                transition_row[other_type] = 0.3 * normalized_probs[other_type] / (1 - normalized_probs[weather_type])
        
        transition_matrices[weather_type] = transition_row
    
    # Create the pattern data
    return {
        "region_id": region_id,
        "season": season,
        "weather_type_probabilities": normalized_probs,
        "temperature_base_min": temp_range[0],
        "temperature_base_max": temp_range[1],
        "humidity_range_min": 0.3,
        "humidity_range_max": 0.8,
        "default_wind_speeds": {
            "min": 5.0,
            "max": 20.0,
            "gust_chance": 0.2,
            "gust_max_multiplier": 1.8
        },
        "precipitation_chances": precip_chances,
        "cloud_cover_range_min": 0.0,
        "cloud_cover_range_max": 1.0,
        "transition_matrices": transition_matrices
    }

def print_weather_condition(condition: DBWeatherCondition) -> None:
    """
    Print details of a weather condition.
    
    Args:
        condition: The weather condition
    """
    if not condition:
        logger.info("No weather condition available")
        return
    
    logger.info(f"\n=== WEATHER CONDITION ===")
    logger.info(f"Region: {condition.region_id}")
    logger.info(f"Time: {condition.timestamp}")
    logger.info(f"Weather Type: {condition.weather_type.value}")
    logger.info(f"Temperature: {condition.temperature}°C (Feels like: {condition.temperature_feels_like}°C)")
    logger.info(f"Wind: {condition.wind_speed} km/h from {condition.wind_direction.value}")
    logger.info(f"Precipitation: {condition.precipitation_type.value} (Intensity: {condition.precipitation_intensity})")
    logger.info(f"Humidity: {condition.humidity * 100:.1f}%")
    logger.info(f"Cloud Cover: {condition.cloud_cover * 100:.1f}%")
    logger.info(f"Visibility: {condition.visibility.value}")
    logger.info(f"Expected Duration: {condition.expected_duration_hours} hours")
    logger.info(f"Description: {condition.generated_description}")

def print_weather_effects(effects: list) -> None:
    """
    Print details of weather effects.
    
    Args:
        effects: List of weather effects
    """
    if not effects:
        logger.info("No active weather effects")
        return
    
    logger.info(f"\n=== ACTIVE WEATHER EFFECTS ({len(effects)}) ===")
    for effect in effects:
        target = f"{effect.target_entity_type}:{effect.target_entity_id}" if effect.target_entity_id else "Regional"
        logger.info(f"Effect: {effect.effect_type.value} on {target}")
        logger.info(f"  Modifier: {effect.modifier_value}")
        logger.info(f"  Description: {effect.description}")
        logger.info(f"  Active until: {effect.calculated_end_time}")
        logger.info(f"  -----")

def handle_weather_change(event: GameEvent) -> None:
    """
    Handle weather change events.
    
    Args:
        event: The weather change event
    """
    region_id = event.context.get("region_id", "unknown")
    current_weather = event.context.get("current_weather_condition", {})
    previous_weather = event.context.get("previous_weather_condition", {})
    
    weather_type = current_weather.get("weather_type", "UNKNOWN")
    
    logger.info(f"\n=== WEATHER CHANGE EVENT ===")
    logger.info(f"Region: {region_id}")
    logger.info(f"Weather changed to: {weather_type}")
    if previous_weather:
        prev_type = previous_weather.get("weather_type", "UNKNOWN")
        logger.info(f"Previous weather was: {prev_type}")
    else:
        logger.info("No previous weather (initial condition)")

def run_test():
    """Run a demonstration of the Weather System."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Subscribe to weather change events
        event_bus.subscribe(EventType.WEATHER_CHANGE, handle_weather_change)
        
        # Set up test regions
        setup_test_regions(db)
        
        # Create game time settings
        settings = GameTimeSettings()
        
        # Create a time service for a specific game
        game_id = "test_game_001"
        time_service = TimeService(db, settings, game_id)
        
        # Create a weather service
        weather_service = WeatherService(db, time_service)
        
        # Get current time state
        current_dt = time_service.get_current_datetime()
        current_block = time_service.get_current_time_block()
        current_season = time_service.get_current_season()
        
        logger.info("\n=== INITIAL GAME TIME STATE ===")
        logger.info(f"Current DateTime: {current_dt.format()}")
        logger.info(f"Current TimeBlock: {current_block.value}")
        logger.info(f"Current Season: {current_season.value}")
        
        # Generate initial weather for all regions
        logger.info("\n=== GENERATING INITIAL WEATHER ===")
        results = weather_service.update_weather_for_all_regions()
        logger.info(f"Generated weather for {len(results)} regions")
        
        # Select a test region
        test_region = "forest_region"
        logger.info(f"\n=== FOCUSING ON REGION: {test_region} ===")
        
        # Get and display current weather
        current_weather = weather_service.get_current_weather(test_region)
        print_weather_condition(current_weather)
        
        # Get and display active weather effects
        effects = weather_service.get_active_effects_for_region(test_region)
        print_weather_effects(effects)
        
        # Demonstrate weather changes with time progression
        logger.info("\n=== ADVANCING TIME TO TRIGGER WEATHER CHANGES ===")
        
        # Advance time to different time blocks and observe weather changes
        for i in range(3):
            logger.info(f"\n--- Time Advancement #{i+1} ---")
            
            # Determine how much time to advance
            if i == 0:
                # Advance to next time block
                next_block = time_service.get_next_time_block()
                minutes = time_service.calculate_time_until_block(next_block)
                logger.info(f"Advancing {minutes} minutes to reach {next_block.value} time block")
                new_dt = time_service.advance_until_block(next_block)
            elif i == 1:
                # Advance a few hours
                hours = 4
                minutes = hours * 60
                logger.info(f"Advancing {minutes} minutes ({hours} hours)")
                new_dt = time_service.advance_minutes(minutes)
            else:
                # Advance to next day
                current_dt = time_service.get_current_datetime()
                target_dt = current_dt.add_days(1, settings)
                target_dt = GameDateTime(
                    target_dt.year, 
                    target_dt.month, 
                    target_dt.day, 
                    8, 0  # 8:00 AM
                )
                minutes = time_service.calculate_minutes_between(current_dt, target_dt)
                logger.info(f"Advancing {minutes} minutes to next day morning")
                new_dt = time_service.advance_minutes(minutes)
            
            # Display new time state
            current_block = time_service.get_current_time_block()
            current_season = time_service.get_current_season()
            logger.info(f"New DateTime: {new_dt.format()}")
            logger.info(f"New TimeBlock: {current_block.value}")
            logger.info(f"Current Season: {current_season.value}")
            
            # Let events propagate
            time.sleep(1)
            
            # Get and display new weather
            new_weather = weather_service.get_current_weather(test_region)
            print_weather_condition(new_weather)
            
            # Get and display active weather effects
            effects = weather_service.get_active_effects_for_region(test_region)
            print_weather_effects(effects)
        
        logger.info("\n=== DEMONSTRATING WEATHER ACROSS DIFFERENT REGIONS ===")
        # Compare weather across different regions
        regions = ["forest_region", "mountain_region", "coastal_region", "desert_region"]
        
        for region_id in regions:
            weather = weather_service.get_current_weather(region_id)
            logger.info(f"\n--- {region_id.replace('_', ' ').title()} ---")
            print_weather_condition(weather)
        
        logger.info("\n=== DEMONSTRATING SEASONAL CHANGES ===")
        # Advance to different seasons and observe weather patterns
        current_season = time_service.get_current_season()
        
        for i in range(3):  # Advance through three more seasons
            # Determine target season
            seasons = list(Season)
            current_idx = seasons.index(current_season)
            target_season = seasons[(current_idx + i + 1) % len(seasons)]
            
            logger.info(f"\n--- Advancing to {target_season.value} ---")
            
            # Calculate days to advance (simplified)
            days_to_advance = 90  # Approximate days per season
            
            # Advance time to next season
            minutes_to_advance = days_to_advance * 24 * 60
            new_dt = time_service.advance_minutes(minutes_to_advance)
            
            # Display new time state
            current_block = time_service.get_current_time_block()
            current_season = time_service.get_current_season()
            logger.info(f"New DateTime: {new_dt.format()}")
            logger.info(f"New TimeBlock: {current_block.value}")
            logger.info(f"Current Season: {current_season.value}")
            
            # Let events propagate
            time.sleep(1)
            
            # Get and display weather for test region
            weather = weather_service.get_current_weather(test_region)
            print_weather_condition(weather)
        
        logger.info("\n=== TEST COMPLETE ===")
        
    finally:
        # Clean up
        db.close()

if __name__ == "__main__":
    logger.info("Starting Weather System Test")
    run_test()