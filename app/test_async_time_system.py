"""
Async Time System Test Script

This script demonstrates how to use the Time System with Redis and Celery
for asynchronous processing and caching.
"""

import logging
import time
from sqlalchemy.orm import Session

from app.db.base import Base, engine, SessionLocal
from app.models.time_models import GameDateTime, TimeBlock, Season, GameTimeSettings
from app.services.time_service import TimeService
from app.events.event_bus import event_bus, EventType, GameEvent
from app.async_tasks.time_tasks import (
    cache_time_settings,
    cache_game_time,
    process_time_advancement,
    process_scheduled_event,
    schedule_real_time_task
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("async_time_system_test")

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Event handlers that forward events to Celery tasks
def handle_time_progressed_async(event: GameEvent) -> None:
    """Handle time progressed event by forwarding to a Celery task."""
    game_id = event.context.get("game_id", "unknown")
    minutes_advanced = event.context.get("minutes_advanced", 0)
    old_datetime = event.context.get("old_datetime", {})
    new_datetime = event.context.get("new_datetime", {})
    old_time_block = event.context.get("old_time_block", "")
    new_time_block = event.context.get("new_time_block", "")
    old_season = event.context.get("old_season", "")
    new_season = event.context.get("new_season", "")
    
    logger.info(f"Forwarding time progression to Celery: {minutes_advanced} minutes")
    
    # Call Celery task to process the time advancement asynchronously
    process_time_advancement.delay(
        game_id,
        minutes_advanced,
        old_datetime,
        new_datetime,
        old_time_block,
        new_time_block,
        old_season,
        new_season
    )

def handle_scheduled_event_async(event: GameEvent) -> None:
    """Handle scheduled event by forwarding to a Celery task."""
    game_id = event.context.get("game_id", "unknown")
    scheduled_event_id = event.context.get("scheduled_event_id", "")
    event_type = event.context.get("event_type", "")
    event_context = event.context.get("event_context", {})
    character_id = event.target_id
    
    logger.info(f"Forwarding scheduled event to Celery: {event_type}")
    
    # Call Celery task to process the scheduled event asynchronously
    process_scheduled_event.delay(
        game_id,
        scheduled_event_id,
        event_type,
        event_context,
        character_id
    )

def run_test():
    """Run a demonstration of the Time System with Redis and Celery."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Subscribe to events and forward them to Celery tasks
        event_bus.subscribe(EventType.GAME_TIME_PROGRESSED, handle_time_progressed_async)
        event_bus.subscribe(EventType.SCHEDULED_EVENT_TRIGGERED, handle_scheduled_event_async)
        
        # Create game time settings
        settings = GameTimeSettings()
        
        # Cache the settings in Redis (via Celery)
        settings_dict = {
            "minutes_per_hour": settings.minutes_per_hour,
            "hours_per_day": settings.hours_per_day,
            "days_per_month": {str(k): v for k, v in settings.days_per_month.items()},
            "months_per_year": settings.months_per_year,
            "year_zero_epoch": settings.year_zero_epoch,
            "season_definitions": {s.value: d for s, d in settings.season_definitions.items()},
            "time_block_definitions": {tb.value: d for tb, d in settings.time_block_definitions.items()}
        }
        cache_time_settings.delay(settings_dict)
        
        # Create a time service for a specific game
        game_id = "test_async_game_001"
        time_service = TimeService(db, settings, game_id)
        
        # Get current time state
        current_dt = time_service.get_current_datetime()
        current_block = time_service.get_current_time_block()
        current_season = time_service.get_current_season()
        
        logger.info("\n=== INITIAL GAME TIME STATE ===")
        logger.info(f"Current DateTime: {current_dt.format()}")
        logger.info(f"Current TimeBlock: {current_block.value}")
        logger.info(f"Current Season: {current_season.value}")
        
        # Cache the current game time in Redis (via Celery)
        current_dt_dict = {
            "year": current_dt.year,
            "month": current_dt.month,
            "day": current_dt.day,
            "hour": current_dt.hour,
            "minute": current_dt.minute
        }
        cache_game_time.delay(game_id, current_dt_dict)
        
        # Schedule some events
        logger.info("\n=== SCHEDULING EVENTS ===")
        
        # Schedule a spell expiration in 30 minutes
        spell_expiry_dt = current_dt.add_minutes(30, settings)
        spell_event_id = time_service.schedule_event(
            trigger_datetime=spell_expiry_dt,
            event_type="SPELL_DURATION_END",
            event_context={
                "spell_name": "Shield of Protection",
                "spell_level": 3,
                "caster_id": "player_001",
                "target_id": "player_001"
            }
        )
        logger.info(f"Scheduled spell expiry: {spell_event_id} at {spell_expiry_dt.format()}")
        
        # Also schedule it as a real-time task to demonstrate the feature
        spell_expiry_dt_dict = {
            "year": spell_expiry_dt.year,
            "month": spell_expiry_dt.month,
            "day": spell_expiry_dt.day,
            "hour": spell_expiry_dt.hour,
            "minute": spell_expiry_dt.minute
        }
        schedule_real_time_task.delay(
            game_id,
            spell_event_id,
            spell_expiry_dt_dict,
            "SPELL_DURATION_END",
            {
                "spell_name": "Shield of Protection",
                "spell_level": 3,
                "caster_id": "player_001",
                "target_id": "player_001"
            },
            "player_001"
        )
        
        # Schedule a crafting completion in 2 hours
        crafting_completion_dt = current_dt.add_minutes(120, settings)
        crafting_event_id = time_service.schedule_event(
            trigger_datetime=crafting_completion_dt,
            event_type="CRAFTING_COMPLETION",
            event_context={
                "item_name": "Steel Sword",
                "quality": "Good",
                "crafter_id": "player_001"
            }
        )
        logger.info(f"Scheduled crafting completion: {crafting_event_id} at {crafting_completion_dt.format()}")
        
        # Demonstrate time advancement and event triggering
        logger.info("\n=== ADVANCING TIME ===")
        
        # Advance by 15 minutes (no events should trigger)
        logger.info("\nAdvancing time by 15 minutes...")
        new_dt = time_service.advance_minutes(15)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Pause to let Celery tasks process
        logger.info("Waiting for Celery tasks to process...")
        time.sleep(2)
        
        # Advance by 20 minutes (spell expiry should trigger)
        logger.info("\nAdvancing time by 20 minutes...")
        new_dt = time_service.advance_minutes(20)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Pause to let Celery tasks process
        logger.info("Waiting for Celery tasks to process...")
        time.sleep(2)
        
        # Advance by 90 minutes (crafting completion should trigger)
        logger.info("\nAdvancing time by 90 minutes...")
        new_dt = time_service.advance_minutes(90)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Pause to let Celery tasks process
        logger.info("Waiting for Celery tasks to process...")
        time.sleep(2)
        
        # Demonstrate advancing until a specific time block
        logger.info("\n=== ADVANCING TO SPECIFIC TIME BLOCK ===")
        target_block = TimeBlock.EVENING
        minutes_until = time_service.calculate_time_until_block(target_block)
        logger.info(f"Minutes until {target_block.value}: {minutes_until}")
        
        logger.info(f"Advancing time until {target_block.value}...")
        new_dt = time_service.advance_until_block(target_block)
        logger.info(f"New DateTime: {new_dt.format()}")
        logger.info(f"New TimeBlock: {time_service.get_current_time_block().value}")
        
        # Final cache update
        current_dt = time_service.get_current_datetime()
        current_dt_dict = {
            "year": current_dt.year,
            "month": current_dt.month,
            "day": current_dt.day,
            "hour": current_dt.hour,
            "minute": current_dt.minute
        }
        cache_game_time.delay(game_id, current_dt_dict)
        
        logger.info("\n=== TEST COMPLETE ===")
        logger.info("In a real application, the Celery tasks would be running in separate processes")
        logger.info("and would handle the time-intensive operations asynchronously.")
        
    finally:
        # Clean up
        db.close()


if __name__ == "__main__":
    logger.info("Starting Async Time System Test")
    logger.info("Note: This test assumes Redis and Celery are running")
    logger.info("If they aren't, the test will still run, but the async tasks will fail")
    run_test()