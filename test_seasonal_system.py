
"""
Seasonal System Test

This script demonstrates the functionality of the Seasonal System integration
with the Time System and other game components.
"""

import logging
import time
from sqlalchemy.orm import Session

from app.db.base import Base, engine, SessionLocal
from app.models.time_models import GameDateTime, TimeBlock, Season, GameTimeSettings
from app.services.time_service import TimeService
from app.services.seasonal_integration_service import SeasonalIntegrationService
from app.events.event_bus import event_bus, EventType, GameEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("seasonal_system_test")

# Create tables in the database
Base.metadata.create_all(bind=engine)

def handle_seasonal_change(event: GameEvent) -> None:
    """Handle seasonal change events."""
    old_season = event.context.get("old_season", "None")
    new_season = event.context.get("current_season", "Unknown")
    narrative = event.context.get("narrative_summary", "No description available")
    
    logger.info(f"\n🌟 SEASONAL CHANGE DETECTED 🌟")
    logger.info(f"   From: {old_season}")
    logger.info(f"   To: {new_season}")
    logger.info(f"   Description: {narrative}")

def handle_time_progressed(event: GameEvent) -> None:
    """Handle time progression events."""
    if event.context.get("season_changed", False):
        logger.info("⏰ Time progression includes seasonal change")

def run_seasonal_test():
    """Run a demonstration of the Seasonal System functionality."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Subscribe to events
        event_bus.subscribe(EventType.SEASON_CHANGED, handle_seasonal_change)
        event_bus.subscribe(EventType.GAME_TIME_PROGRESSED, handle_time_progressed)
        
        # Create game time settings with specific seasonal definitions
        settings = GameTimeSettings(
            season_definitions={
                Season.SPRING: (3, 1),   # Spring starts Month 3, Day 1
                Season.SUMMER: (6, 1),   # Summer starts Month 6, Day 1
                Season.AUTUMN: (9, 1),   # Autumn starts Month 9, Day 1
                Season.WINTER: (12, 1)   # Winter starts Month 12, Day 1
            }
        )
        
        # Create services
        game_id = "seasonal_test_game_001"
        time_service = TimeService(db, settings, game_id)
        seasonal_service = SeasonalIntegrationService(db, game_id, time_service)
        
        # Get initial state
        current_dt = time_service.get_current_datetime()
        current_season = time_service.get_current_season()
        
        logger.info("\n=== INITIAL SEASONAL STATE ===")
        logger.info(f"Current DateTime: {current_dt.format()}")
        logger.info(f"Current Season: {current_season.value}")
        logger.info(f"Formatted DateTime: {time_service.format_datetime()}")
        
        # Get comprehensive seasonal state
        seasonal_state = seasonal_service.get_current_seasonal_state()
        logger.info(f"Season Progress: {seasonal_state['season_progress']['progress']:.1%}")
        logger.info(f"Days until next season: {seasonal_state['days_until_next_season']}")
        
        # Test location-specific seasonal effects
        logger.info("\n=== LOCATION-SPECIFIC SEASONAL EFFECTS ===")
        location_effects = seasonal_service.get_seasonal_effects_for_location("test_village", "northern_region")
        logger.info(f"Weather: {location_effects['weather']['description']}")
        logger.info(f"Resource availability sample: Herbs={location_effects['resources'].get('herbs', 1.0):.1f}x")
        logger.info(f"NPC Activity sample: Farmer is {location_effects['npc_activities'].get('farmer', 'unknown')}")
        
        # Simulate rapid seasonal progression
        logger.info("\n=== SIMULATING SEASONAL PROGRESSION ===")
        
        # Advance to next season (approximately 90 days forward)
        days_to_advance = 95  # Should trigger seasonal change
        minutes_to_advance = days_to_advance * settings.hours_per_day * settings.minutes_per_hour
        
        logger.info(f"Advancing time by {days_to_advance} days ({minutes_to_advance} minutes)...")
        new_dt = time_service.advance_minutes(minutes_to_advance)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Check new seasonal state
        time.sleep(0.5)  # Give events time to process
        
        new_seasonal_state = seasonal_service.get_current_seasonal_state()
        logger.info(f"New Season: {new_seasonal_state['current_season']}")
        logger.info(f"New Season Progress: {new_seasonal_state['season_progress']['progress']:.1%}")
        
        # Test another seasonal transition
        logger.info("\n=== ADVANCING TO NEXT SEASON ===")
        days_to_advance = 100  # Should trigger another seasonal change
        minutes_to_advance = days_to_advance * settings.hours_per_day * settings.minutes_per_hour
        
        logger.info(f"Advancing time by {days_to_advance} more days...")
        newer_dt = time_service.advance_minutes(minutes_to_advance)
        logger.info(f"New DateTime: {newer_dt.format()}")
        
        time.sleep(0.5)  # Give events time to process
        
        # Final state check
        final_state = seasonal_service.get_current_seasonal_state()
        logger.info(f"Final Season: {final_state['current_season']}")
        
        # Test seasonal effects in the new season
        logger.info("\n=== FINAL SEASONAL EFFECTS ===")
        final_effects = seasonal_service.get_seasonal_effects_for_location("test_village", "northern_region")
        logger.info(f"Final Weather: {final_effects['weather']['description']}")
        logger.info(f"Final Atmosphere: {final_effects['seasonal_atmosphere']}")
        
        # Display economic changes
        economy_summary = final_state['economic_state']
        logger.info(f"Most available resource: {economy_summary.get('most_available_resource', 'none')}")
        logger.info(f"Least available resource: {economy_summary.get('least_available_resource', 'none')}")
        logger.info(f"Highest demand category: {economy_summary.get('highest_demand_category', 'none')}")
        
        # Display NPC behavior changes
        npc_summary = final_state['npc_behavior']
        logger.info(f"General NPC mood: {npc_summary.get('general_mood', 'normal')}")
        logger.info(f"Clothing style: {npc_summary.get('clothing_style', 'practical')}")
        
        logger.info("\n=== SEASONAL SYSTEM TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"Error during seasonal system test: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_seasonal_test()
