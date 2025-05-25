"""
Time System Asynchronous Tasks

This module defines Celery tasks for handling time-related operations asynchronously.
These tasks offload computationally intensive work from the main game loop.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from redis import Redis

from app.db.base import SessionLocal
from app.models.time_models import GameDateTime, GameTimeSettings
from app.async_tasks.celery_app import celery_app
from app.events.event_bus import EventType, GameEvent
from app.services.time_service import TimeService

logger = logging.getLogger(__name__)

# Create Redis client for caching
def get_redis_client():
    """Get a Redis client."""
    import os
    
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_db = os.getenv('REDIS_DB', '0')
    
    return Redis(host=redis_host, port=int(redis_port), db=int(redis_db), decode_responses=True)

# Cache keys
TIME_SETTINGS_CACHE_KEY = "time_system:settings"
GAME_TIME_CACHE_KEY_PREFIX = "time_system:game_time:"

@celery_app.task
def cache_time_settings(settings_dict: Dict[str, Any]) -> bool:
    """
    Cache the game time settings in Redis.
    
    Args:
        settings_dict: Dictionary representation of GameTimeSettings
        
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = get_redis_client()
        redis_client.set(TIME_SETTINGS_CACHE_KEY, json.dumps(settings_dict))
        logger.info("Cached time settings in Redis")
        return True
    except Exception as e:
        logger.error(f"Error caching time settings: {e}")
        return False

@celery_app.task
def cache_game_time(game_id: str, datetime_dict: Dict[str, Any]) -> bool:
    """
    Cache the current game time for a specific game in Redis.
    
    Args:
        game_id: Game identifier
        datetime_dict: Dictionary representation of GameDateTime
        
    Returns:
        True if successful, False otherwise
    """
    try:
        redis_client = get_redis_client()
        cache_key = f"{GAME_TIME_CACHE_KEY_PREFIX}{game_id}"
        redis_client.set(cache_key, json.dumps(datetime_dict))
        logger.info(f"Cached game time for game {game_id} in Redis")
        return True
    except Exception as e:
        logger.error(f"Error caching game time: {e}")
        return False

@celery_app.task
def process_time_advancement(
    game_id: str,
    minutes_advanced: int,
    old_datetime_dict: Dict[str, Any],
    new_datetime_dict: Dict[str, Any],
    old_time_block: str,
    new_time_block: str,
    old_season: str,
    new_season: str
) -> bool:
    """
    Process time advancement asynchronously.
    This task handles computationally intensive updates triggered by time passing.
    
    Args:
        game_id: Game identifier
        minutes_advanced: Number of minutes that have passed
        old_datetime_dict: Dictionary of the previous game datetime
        new_datetime_dict: Dictionary of the new game datetime
        old_time_block: Previous time block
        new_time_block: New time block
        old_season: Previous season
        new_season: New season
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Processing time advancement for game {game_id}: {minutes_advanced} minutes")
    
    try:
        # Create a database session
        db = SessionLocal()
        
        try:
            # Process NPC schedule updates
            _process_npc_schedules(db, game_id, old_time_block, new_time_block)
            
            # Process world state updates
            _process_world_state_updates(db, game_id, minutes_advanced)
            
            # Process character resource regeneration
            _process_resource_regeneration(db, game_id, minutes_advanced)
            
            # Handle weather changes if time block or season changed
            if old_time_block != new_time_block or old_season != new_season:
                _process_weather_changes(db, game_id, new_time_block, new_season)
            
            # Cache the new game time
            cache_game_time.delay(game_id, new_datetime_dict)
            
            return True
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error processing time advancement: {e}")
        return False

@celery_app.task
def process_scheduled_event(
    game_id: str,
    event_id: str,
    event_type: str,
    event_context: Dict[str, Any],
    character_id: Optional[str] = None
) -> bool:
    """
    Process a scheduled event asynchronously.
    
    Args:
        game_id: Game identifier
        event_id: Scheduled event identifier
        event_type: Type of the scheduled event
        event_context: Additional context for the event
        character_id: Optional character ID if the event is character-specific
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Processing scheduled event {event_id} of type {event_type} for game {game_id}")
    
    try:
        # Create a database session
        db = SessionLocal()
        
        try:
            # Handle different types of scheduled events
            if event_type == "SPELL_DURATION_END":
                _process_spell_expiry(db, game_id, event_context, character_id)
            
            elif event_type == "CRAFTING_COMPLETION":
                _process_crafting_completion(db, game_id, event_context, character_id)
            
            elif event_type == "NPC_SCHEDULE_EVENT":
                _process_npc_schedule_event(db, game_id, event_context)
            
            elif event_type == "RESOURCE_RESPAWN":
                _process_resource_respawn(db, game_id, event_context)
            
            else:
                logger.warning(f"Unknown event type: {event_type}")
            
            return True
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error processing scheduled event: {e}")
        return False

@celery_app.task
def schedule_real_time_task(
    game_id: str,
    scheduled_event_id: str,
    trigger_datetime_dict: Dict[str, Any],
    event_type: str,
    event_context: Dict[str, Any],
    character_id: Optional[str] = None
) -> bool:
    """
    Schedule a Celery task to run at a real-world time that corresponds to a game time event.
    This is useful for very long-term scheduled events that should persist across server restarts.
    
    Args:
        game_id: Game identifier
        scheduled_event_id: Scheduled event identifier
        trigger_datetime_dict: Dictionary of the scheduled event's trigger datetime
        event_type: Type of the scheduled event
        event_context: Additional context for the event
        character_id: Optional character ID if the event is character-specific
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Scheduling real-time task for event {scheduled_event_id} of type {event_type}")
    
    try:
        # Create the task to process the scheduled event
        task = process_scheduled_event.apply_async(
            args=[game_id, scheduled_event_id, event_type, event_context, character_id],
            countdown=_calculate_real_time_delay(game_id, trigger_datetime_dict)
        )
        
        logger.info(f"Scheduled real-time task with ID {task.id}")
        return True
    
    except Exception as e:
        logger.error(f"Error scheduling real-time task: {e}")
        return False

# Helper functions for processing different event types
def _process_npc_schedules(db: SessionLocal, game_id: str, old_time_block: str, new_time_block: str) -> None:
    """
    Process NPC schedule updates based on time block changes.
    
    Args:
        db: Database session
        game_id: Game identifier
        old_time_block: Previous time block
        new_time_block: New time block
    """
    logger.info(f"Processing NPC schedules for game {game_id}: {old_time_block} -> {new_time_block}")
    # In a real implementation, this would query the NPC database and update their locations and activities
    # based on their schedules for the new time block

def _process_world_state_updates(db: SessionLocal, game_id: str, minutes_advanced: int) -> None:
    """
    Process world state updates based on time passing.
    
    Args:
        db: Database session
        game_id: Game identifier
        minutes_advanced: Number of minutes that have passed
    """
    logger.info(f"Processing world state updates for game {game_id}: {minutes_advanced} minutes passed")
    # In a real implementation, this would update world state elements like:
    # - Market prices
    # - Political events
    # - Random encounters
    # - Quest timers

def _process_resource_regeneration(db: SessionLocal, game_id: str, minutes_advanced: int) -> None:
    """
    Process character resource regeneration based on time passing.
    
    Args:
        db: Database session
        game_id: Game identifier
        minutes_advanced: Number of minutes that have passed
    """
    logger.info(f"Processing resource regeneration for game {game_id}: {minutes_advanced} minutes passed")
    # In a real implementation, this would:
    # 1. Get all characters in the game
    # 2. Calculate resource regeneration based on character attributes, equipment, buffs, etc.
    # 3. Update character resources in the database

def _process_weather_changes(db: SessionLocal, game_id: str, time_block: str, season: str) -> None:
    """
    Process weather changes based on time block and season.
    
    Args:
        db: Database session
        game_id: Game identifier
        time_block: Current time block
        season: Current season
    """
    logger.info(f"Processing weather changes for game {game_id}: {time_block}, {season}")
    # In a real implementation, this would:
    # 1. Get the current region for each active location in the game
    # 2. Generate new weather based on the region, time block, and season
    # 3. Apply weather effects to the game world

def _process_spell_expiry(db: SessionLocal, game_id: str, event_context: Dict[str, Any], character_id: Optional[str]) -> None:
    """
    Process a spell expiration event.
    
    Args:
        db: Database session
        game_id: Game identifier
        event_context: Event context containing spell details
        character_id: Optional character ID
    """
    spell_name = event_context.get("spell_name", "Unknown Spell")
    spell_level = event_context.get("spell_level", 1)
    target_id = event_context.get("target_id", character_id)
    
    logger.info(f"Processing spell expiry for game {game_id}: {spell_name} (Level {spell_level}) on {target_id}")
    # In a real implementation, this would:
    # 1. Remove the spell effects from the target
    # 2. Notify the player that the spell has expired
    # 3. Update the target's status in the database

def _process_crafting_completion(db: SessionLocal, game_id: str, event_context: Dict[str, Any], character_id: Optional[str]) -> None:
    """
    Process a crafting completion event.
    
    Args:
        db: Database session
        game_id: Game identifier
        event_context: Event context containing crafting details
        character_id: Optional character ID
    """
    item_name = event_context.get("item_name", "Unknown Item")
    quality = event_context.get("quality", "Normal")
    crafter_id = event_context.get("crafter_id", character_id)
    
    logger.info(f"Processing crafting completion for game {game_id}: {item_name} ({quality}) by {crafter_id}")
    # In a real implementation, this would:
    # 1. Create the crafted item in the database
    # 2. Add it to the crafter's inventory
    # 3. Notify the player that crafting is complete
    # 4. Grant crafting experience to the player

def _process_npc_schedule_event(db: SessionLocal, game_id: str, event_context: Dict[str, Any]) -> None:
    """
    Process an NPC schedule event.
    
    Args:
        db: Database session
        game_id: Game identifier
        event_context: Event context containing NPC schedule details
    """
    npc_name = event_context.get("npc_name", "Unknown NPC")
    action = event_context.get("action", "Unknown Action")
    location = event_context.get("location", "Unknown Location")
    
    logger.info(f"Processing NPC schedule event for game {game_id}: {npc_name} performing {action} at {location}")
    # In a real implementation, this would:
    # 1. Update the NPC's current action and location in the database
    # 2. Potentially trigger effects in the game world
    # 3. Notify nearby players of the NPC's actions if relevant

def _process_resource_respawn(db: SessionLocal, game_id: str, event_context: Dict[str, Any]) -> None:
    """
    Process a resource respawn event.
    
    Args:
        db: Database session
        game_id: Game identifier
        event_context: Event context containing resource details
    """
    resource_type = event_context.get("resource_type", "Unknown Resource")
    location = event_context.get("location", "Unknown Location")
    quantity = event_context.get("quantity", 1)
    
    logger.info(f"Processing resource respawn for game {game_id}: {quantity} {resource_type} at {location}")
    # In a real implementation, this would:
    # 1. Restore the resource node in the database
    # 2. Make the resource harvestable again
    # 3. Potentially notify nearby players if the resource is visible

def _calculate_real_time_delay(game_id: str, trigger_datetime_dict: Dict[str, Any]) -> int:
    """
    Calculate the real-world delay in seconds until a game time event should trigger.
    
    Args:
        game_id: Game identifier
        trigger_datetime_dict: Dictionary of the scheduled event's trigger datetime
        
    Returns:
        Delay in seconds
    """
    try:
        # Get the current game time from cache
        redis_client = get_redis_client()
        cache_key = f"{GAME_TIME_CACHE_KEY_PREFIX}{game_id}"
        cached_time = redis_client.get(cache_key)
        
        if cached_time:
            current_datetime_dict = json.loads(cached_time)
            
            # Get time settings from cache
            settings_json = redis_client.get(TIME_SETTINGS_CACHE_KEY)
            if not settings_json:
                # Default to 1 minute of real time = 60 minutes of game time
                game_time_to_real_time_ratio = 60
            else:
                settings_dict = json.loads(settings_json)
                # In a real implementation, this would be calculated based on the game's time settings
                game_time_to_real_time_ratio = 60
            
            # Convert dictionaries to GameDateTime objects
            trigger_year = trigger_datetime_dict.get("year", 1000)
            trigger_month = trigger_datetime_dict.get("month", 1)
            trigger_day = trigger_datetime_dict.get("day", 1)
            trigger_hour = trigger_datetime_dict.get("hour", 0)
            trigger_minute = trigger_datetime_dict.get("minute", 0)
            
            current_year = current_datetime_dict.get("year", 1000)
            current_month = current_datetime_dict.get("month", 1)
            current_day = current_datetime_dict.get("day", 1)
            current_hour = current_datetime_dict.get("hour", 0)
            current_minute = current_datetime_dict.get("minute", 0)
            
            # Calculate game time difference in minutes (simplified)
            trigger_total_minutes = ((trigger_year * 12 + trigger_month) * 30 + trigger_day) * 24 * 60 + trigger_hour * 60 + trigger_minute
            current_total_minutes = ((current_year * 12 + current_month) * 30 + current_day) * 24 * 60 + current_hour * 60 + current_minute
            
            game_minutes_until_trigger = max(0, trigger_total_minutes - current_total_minutes)
            
            # Convert game minutes to real seconds
            real_seconds_delay = game_minutes_until_trigger * 60 / game_time_to_real_time_ratio
            
            return int(real_seconds_delay)
        
        else:
            # Default delay if we can't calculate precisely
            logger.warning(f"Could not find cached game time for game {game_id}, using default delay")
            return 3600  # 1 hour default
    
    except Exception as e:
        logger.error(f"Error calculating real-time delay: {e}")
        return 3600  # 1 hour default