"""
Time System Test Script

This script demonstrates the functionality of the Time System in a turn-based text-based RPG.
It shows how time advances, how events are scheduled and triggered, and how other game
systems can respond to time changes.
"""

import logging
import time
from sqlalchemy.orm import Session

from app.db.base import Base, engine, SessionLocal
from app.models.time_models import GameDateTime, TimeBlock, Season, GameTimeSettings
from app.services.time_service import TimeService
from app.events.event_bus import event_bus, EventType, GameEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("time_system_test")

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Sample event handlers for different game systems
def handle_time_progressed(event: GameEvent) -> None:
    """Handle when game time progresses."""
    minutes = event.context.get("minutes_advanced", 0)
    old_time = event.context.get("old_datetime", {})
    new_time = event.context.get("new_datetime", {})
    
    logger.info(f"Weather system updating due to {minutes} minutes passing")
    logger.info(f"From {old_time.get('hour', 0):02d}:{old_time.get('minute', 0):02d} to "
                f"{new_time.get('hour', 0):02d}:{new_time.get('minute', 0):02d}")

def handle_time_block_changed(event: GameEvent) -> None:
    """Handle when the time block changes (e.g., morning to afternoon)."""
    old_block = event.context.get("old_time_block", "")
    new_block = event.context.get("new_time_block", "")
    
    logger.info(f"NPC schedules updating due to time block change: {old_block} -> {new_block}")
    logger.info(f"Some NPCs are now in different locations or performing different activities")

def handle_season_changed(event: GameEvent) -> None:
    """Handle when the season changes."""
    old_season = event.context.get("old_season", "")
    new_season = event.context.get("new_season", "")
    
    logger.info(f"World environment updating due to season change: {old_season} -> {new_season}")
    logger.info(f"Available resources, weather patterns, and NPC behaviors have changed")

def handle_scheduled_event(event: GameEvent) -> None:
    """Handle when a scheduled event is triggered."""
    scheduled_event_id = event.context.get("scheduled_event_id", "")
    event_type = event.context.get("event_type", "")
    event_context = event.context.get("event_context", {})
    
    logger.info(f"Scheduled event triggered: {scheduled_event_id}, Type: {event_type}")
    logger.info(f"Event context: {event_context}")
    
    # Handle different types of scheduled events
    if event_type == "SPELL_DURATION_END":
        logger.info(f"Spell '{event_context.get('spell_name', '')}' has worn off")
    elif event_type == "CRAFTING_COMPLETION":
        logger.info(f"Crafting of '{event_context.get('item_name', '')}' is complete")
    elif event_type == "NPC_SCHEDULE_EVENT":
        logger.info(f"NPC '{event_context.get('npc_name', '')}' is performing action: "
                    f"{event_context.get('action', '')}")
    elif event_type == "RESOURCE_RESPAWN":
        logger.info(f"Resource at location {event_context.get('location', '')} has respawned")

def handle_resource_regeneration(event: GameEvent) -> None:
    """Handle character resource regeneration."""
    minutes = event.context.get("minutes_advanced", 0)
    character_id = event.context.get("character_id", "")
    
    if character_id:
        stamina_regen = (minutes / 60) * 5  # 5 stamina points per hour
        health_regen = (minutes / 60) * 2   # 2 health points per hour
        mana_regen = (minutes / 60) * 3     # 3 mana points per hour
        
        logger.info(f"Character {character_id} regenerated:")
        logger.info(f"  Stamina: +{stamina_regen:.1f}")
        logger.info(f"  Health: +{health_regen:.1f}")
        logger.info(f"  Mana: +{mana_regen:.1f}")


def demonstrate_time_cost_allocation() -> None:
    """
    Demonstrate how different actions have different time costs.
    This shows the strategy for allocating time costs to player actions.
    """
    logger.info("\n=== TIME COST ALLOCATION STRATEGY ===")
    
    # Time cost examples for different action categories
    time_costs = {
        "Trivial Actions": {
            "examine item": 1,               # 1 minute
            "pick up object": 1,             # 1 minute
            "talk to NPC (brief)": 5,        # 5 minutes
            "open door": 1                   # 1 minute
        },
        "Minor Actions": {
            "search area": 10,               # 10 minutes
            "talk to NPC (detailed)": 15,    # 15 minutes
            "cook simple meal": 20,          # 20 minutes
            "pick a simple lock": 10         # 10 minutes
        },
        "Significant Actions": {
            "thorough area investigation": 30,  # 30 minutes
            "shop at market": 60,               # 1 hour
            "repair equipment": 90,             # 1.5 hours
            "train basic skill": 120            # 2 hours
        },
        "Major Actions": {
            "craft item": 240,                # 4 hours
            "research spell": 180,            # 3 hours
            "long journey (per region)": 360, # 6 hours
            "complex ritual": 120             # 2 hours
        },
        "Rest Actions": {
            "short rest": 60,                # 1 hour
            "full night's sleep": 480,       # 8 hours
            "meditation": 30,                # 30 minutes
            "meal break": 45                 # 45 minutes
        },
        "Wait Actions": {
            "wait until time block": "variable",
            "wait X hours": "specified by player",
            "wait for event": "determined by event timing"
        }
    }
    
    # Print the time costs
    for category, actions in time_costs.items():
        logger.info(f"\n{category}:")
        for action, minutes in actions.items():
            logger.info(f"  {action}: {minutes} minutes")
    
    logger.info("\nThese time costs would be defined in command handlers in the Text Parser Engine")
    logger.info("After executing an action, the handler would call time_service.advance_time(minutes)")


def run_test():
    """Run a demonstration of the Time System functionality."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Subscribe to events
        event_bus.subscribe(EventType.GAME_TIME_PROGRESSED, handle_time_progressed)
        event_bus.subscribe(EventType.TIME_BLOCK_CHANGED, handle_time_block_changed)
        event_bus.subscribe(EventType.SEASON_CHANGED, handle_season_changed)
        event_bus.subscribe(EventType.SCHEDULED_EVENT_TRIGGERED, handle_scheduled_event)
        event_bus.subscribe(EventType.GAME_TIME_PROGRESSED, handle_resource_regeneration)
        
        # Create game time settings
        settings = GameTimeSettings()
        
        # Create a time service for a specific game
        game_id = "test_game_001"
        time_service = TimeService(db, settings, game_id)
        
        # Get current time state
        current_dt = time_service.get_current_datetime()
        current_block = time_service.get_current_time_block()
        current_season = time_service.get_current_season()
        
        logger.info("\n=== INITIAL GAME TIME STATE ===")
        logger.info(f"Current DateTime: {current_dt.format()}")
        logger.info(f"Current TimeBlock: {current_block.value}")
        logger.info(f"Current Season: {current_season.value}")
        logger.info(f"Formatted DateTime: {time_service.format_datetime()}")
        
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
        
        # Schedule a recurring NPC action every 60 minutes
        npc_action_dt = current_dt.add_minutes(60, settings)
        npc_event_id = time_service.schedule_event(
            trigger_datetime=npc_action_dt,
            event_type="NPC_SCHEDULE_EVENT",
            event_context={
                "npc_name": "Blacksmith",
                "action": "Check furnace",
                "location": "Forge"
            },
            is_recurring=True,
            recurrence_interval_minutes=60
        )
        logger.info(f"Scheduled recurring NPC action: {npc_event_id} at {npc_action_dt.format()}, repeats every 60 minutes")
        
        # Schedule resource respawn in 4 hours
        resource_respawn_dt = current_dt.add_minutes(240, settings)
        resource_event_id = time_service.schedule_event(
            trigger_datetime=resource_respawn_dt,
            event_type="RESOURCE_RESPAWN",
            event_context={
                "resource_type": "Iron Ore",
                "location": "Mountain Mine",
                "quantity": 5
            }
        )
        logger.info(f"Scheduled resource respawn: {resource_event_id} at {resource_respawn_dt.format()}")
        
        # Demonstrate time advancement and event triggering
        logger.info("\n=== ADVANCING TIME ===")
        
        # Advance by 15 minutes (no events should trigger)
        logger.info("\nAdvancing time by 15 minutes...")
        new_dt = time_service.advance_minutes(15)
        logger.info(f"New DateTime: {new_dt.format()}")
        logger.info(f"New TimeBlock: {time_service.get_current_time_block().value}")
        
        # Advance by 20 minutes (spell expiry should trigger)
        logger.info("\nAdvancing time by 20 minutes...")
        new_dt = time_service.advance_minutes(20)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Advance by 30 minutes (first NPC action should trigger)
        logger.info("\nAdvancing time by 30 minutes...")
        new_dt = time_service.advance_minutes(30)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Advance by 60 minutes (crafting completion should trigger)
        logger.info("\nAdvancing time by 60 minutes...")
        new_dt = time_service.advance_minutes(60)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Advance by 60 minutes (second NPC action should trigger)
        logger.info("\nAdvancing time by 60 minutes...")
        new_dt = time_service.advance_minutes(60)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Advance by 60 minutes (resource respawn should trigger)
        logger.info("\nAdvancing time by 60 minutes...")
        new_dt = time_service.advance_minutes(60)
        logger.info(f"New DateTime: {new_dt.format()}")
        
        # Demonstrate advancing until a specific time block
        logger.info("\n=== ADVANCING TO SPECIFIC TIME BLOCK ===")
        target_block = TimeBlock.EVENING
        minutes_until = time_service.calculate_time_until_block(target_block)
        logger.info(f"Minutes until {target_block.value}: {minutes_until}")
        
        logger.info(f"Advancing time until {target_block.value}...")
        new_dt = time_service.advance_until_block(target_block)
        logger.info(f"New DateTime: {new_dt.format()}")
        logger.info(f"New TimeBlock: {time_service.get_current_time_block().value}")
        
        # Demonstrate time cost allocation for different actions
        demonstrate_time_cost_allocation()
        
        # Cancel a scheduled event
        if time_service.cancel_scheduled_event(npc_event_id):
            logger.info(f"\nCanceled recurring NPC event: {npc_event_id}")
        
        # Demonstrate advancing a whole day
        logger.info("\n=== ADVANCING A WHOLE DAY ===")
        logger.info("Advancing time by 1 day...")
        new_dt = time_service.advance_days(1)
        logger.info(f"New DateTime: {new_dt.format()}")
        logger.info(f"New TimeBlock: {time_service.get_current_time_block().value}")
        
    finally:
        # Clean up
        db.close()


if __name__ == "__main__":
    run_test()