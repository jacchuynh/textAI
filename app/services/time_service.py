"""
Time Service

This module provides the TimeService class, which is responsible for managing
the game's time system. It handles time advancement, scheduled events, and
time-related queries.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from redis import Redis
from sqlalchemy.orm import Session

from app.models.time_models import (
    GameDateTime, TimeBlock, Season, GameTimeSettings, ScheduledGameEvent
)
from app.db.crud import game_time_state_crud, scheduled_game_event_crud
from app.events.event_bus import event_bus, GameEvent, EventType

logger = logging.getLogger(__name__)

class TimeService:
    """
    Service for managing the game's time system.
    
    The TimeService tracks the current game time, schedules future events,
    and handles time advancement. It integrates with the EventBus to notify
    other systems about time-related changes.
    """
    def __init__(self, db: Session, settings: GameTimeSettings, game_id: str, redis_client: Optional[Redis] = None):
        """
        Initialize the TimeService.
        
        Args:
            db: Database session
            settings: Time system configuration
            game_id: Identifier for the current game
            redis_client: Optional Redis client for caching
        """
        self.db = db
        self.settings = settings
        self.game_id = game_id
        self.redis_client = redis_client
        
        # Initialize time state from database or create new
        self._initialize_time_state()
    
    def _initialize_time_state(self) -> None:
        """
        Initialize the time state from the database or create a new one.
        """
        # Try to get current time state from database
        current_datetime = game_time_state_crud.get_datetime(self.db, self.game_id)
        
        if not current_datetime:
            # Create a new time state if none exists
            current_datetime = GameDateTime(
                year=self.settings.year_zero_epoch,
                month=1,
                day=1,
                hour=8,  # Start at 8:00 AM
                minute=0
            )
            
            # Save to database
            game_time_state_crud.create_or_update(self.db, game_id=self.game_id, datetime=current_datetime)
            
            logger.info(f"Created new time state for game {self.game_id}: {current_datetime.format()}")
        else:
            logger.info(f"Loaded time state for game {self.game_id}: {current_datetime.format()}")
    
    def get_current_datetime(self) -> GameDateTime:
        """
        Get the current game datetime.
        
        Returns:
            The current game datetime
        """
        current_datetime = game_time_state_crud.get_datetime(self.db, self.game_id)
        
        if not current_datetime:
            # This shouldn't happen unless the database was corrupted
            logger.error(f"Time state not found for game {self.game_id}, reinitializing")
            self._initialize_time_state()
            current_datetime = game_time_state_crud.get_datetime(self.db, self.game_id)
        
        return current_datetime
    
    def get_current_time_block(self) -> TimeBlock:
        """
        Get the current time block (e.g., MORNING, EVENING).
        
        Returns:
            The current time block
        """
        current_datetime = self.get_current_datetime()
        
        for time_block, (start_hour, end_hour) in self.settings.time_block_definitions.items():
            if start_hour <= current_datetime.hour < end_hour:
                return time_block
        
        # Default fallback - should not reach here if time blocks cover all hours
        return TimeBlock.MORNING
    
    def get_current_season(self) -> Season:
        """
        Get the current season.
        
        Returns:
            The current season
        """
        current_datetime = self.get_current_datetime()
        return current_datetime.get_season(self.settings)
    
    def advance_time(self, minutes_to_advance: int) -> GameDateTime:
        """
        Advance the game time and trigger any scheduled events.
        
        Args:
            minutes_to_advance: Number of minutes to advance
            
        Returns:
            The new game datetime
        """
        if minutes_to_advance <= 0:
            logger.warning(f"Cannot advance time by {minutes_to_advance} minutes")
            return self.get_current_datetime()
        
        # Get current state
        current_datetime = self.get_current_datetime()
        current_time_block = self.get_current_time_block()
        current_season = self.get_current_season()
        
        # Calculate new datetime
        new_datetime = current_datetime.add_minutes(minutes_to_advance, self.settings)
        
        # Persist the new datetime
        game_time_state_crud.create_or_update(self.db, game_id=self.game_id, datetime=new_datetime)
        
        # Determine if time block or season changed
        new_time_block = self.get_current_time_block()
        new_season = self.get_current_season()
        
        # Check and trigger scheduled events
        self._check_and_trigger_scheduled_events(new_datetime)
        
        # Publish time progression event
        self._publish_time_progressed_event(
            minutes_to_advance,
            current_datetime,
            new_datetime,
            current_time_block,
            new_time_block,
            current_season,
            new_season
        )
        
        # Publish specific events if time block or season changed
        if current_time_block != new_time_block:
            self._publish_time_block_changed_event(current_time_block, new_time_block)
        
        if current_season != new_season:
            self._publish_season_changed_event(current_season, new_season)
        
        return new_datetime
    
    def _publish_time_progressed_event(
        self,
        minutes_advanced: int,
        old_datetime: GameDateTime,
        new_datetime: GameDateTime,
        old_time_block: TimeBlock,
        new_time_block: TimeBlock,
        old_season: Season,
        new_season: Season
    ) -> None:
        """
        Publish a GAME_TIME_PROGRESSED event.
        
        Args:
            minutes_advanced: Number of minutes advanced
            old_datetime: Previous game datetime
            new_datetime: New game datetime
            old_time_block: Previous time block
            new_time_block: New time block
            old_season: Previous season
            new_season: New season
        """
        event = GameEvent(
            event_type=EventType.GAME_TIME_PROGRESSED,
            context={
                "game_id": self.game_id,
                "minutes_advanced": minutes_advanced,
                "old_datetime": {
                    "year": old_datetime.year,
                    "month": old_datetime.month,
                    "day": old_datetime.day,
                    "hour": old_datetime.hour,
                    "minute": old_datetime.minute
                },
                "new_datetime": {
                    "year": new_datetime.year,
                    "month": new_datetime.month,
                    "day": new_datetime.day,
                    "hour": new_datetime.hour,
                    "minute": new_datetime.minute
                },
                "old_time_block": old_time_block.value,
                "new_time_block": new_time_block.value,
                "old_season": old_season.value,
                "new_season": new_season.value,
                "time_block_changed": old_time_block != new_time_block,
                "season_changed": old_season != new_season
            }
        )
        
        event_bus.publish(event)
        logger.info(f"Published GAME_TIME_PROGRESSED event: {minutes_advanced} minutes advanced")
    
    def _publish_time_block_changed_event(self, old_time_block: TimeBlock, new_time_block: TimeBlock) -> None:
        """
        Publish a TIME_BLOCK_CHANGED event.
        
        Args:
            old_time_block: Previous time block
            new_time_block: New time block
        """
        event = GameEvent(
            event_type=EventType.TIME_BLOCK_CHANGED,
            context={
                "game_id": self.game_id,
                "old_time_block": old_time_block.value,
                "new_time_block": new_time_block.value
            }
        )
        
        event_bus.publish(event)
        logger.info(f"Published TIME_BLOCK_CHANGED event: {old_time_block.value} -> {new_time_block.value}")
    
    def _publish_season_changed_event(self, old_season: Season, new_season: Season) -> None:
        """
        Publish a SEASON_CHANGED event.
        
        Args:
            old_season: Previous season
            new_season: New season
        """
        event = GameEvent(
            event_type=EventType.SEASON_CHANGED,
            context={
                "game_id": self.game_id,
                "old_season": old_season.value,
                "new_season": new_season.value
            }
        )
        
        event_bus.publish(event)
        logger.info(f"Published SEASON_CHANGED event: {old_season.value} -> {new_season.value}")
    
    def schedule_event(
        self,
        trigger_datetime: GameDateTime,
        event_type: str,
        event_context: Dict[str, Any],
        character_id: Optional[str] = None,
        is_recurring: bool = False,
        recurrence_interval_minutes: Optional[int] = None
    ) -> str:
        """
        Schedule a game event to occur at a specific time.
        
        Args:
            trigger_datetime: When the event should trigger
            event_type: Type of event
            event_context: Additional context for the event
            character_id: Optional character ID if the event is character-specific
            is_recurring: Whether the event repeats
            recurrence_interval_minutes: How often the event repeats (in minutes)
            
        Returns:
            The event ID of the scheduled event
        """
        # Generate a unique event ID
        event_id = str(uuid.uuid4())
        
        # Create a ScheduledGameEvent
        event = ScheduledGameEvent(
            event_id=event_id,
            trigger_datetime=trigger_datetime,
            event_type=event_type,
            event_context=event_context,
            character_id=character_id,
            is_recurring=is_recurring,
            recurrence_interval_minutes=recurrence_interval_minutes
        )
        
        # Store the event
        scheduled_game_event_crud.create_event(self.db, game_id=self.game_id, event=event)
        
        logger.info(f"Scheduled event {event_id} of type {event_type} for {trigger_datetime.format()}")
        
        return event_id
    
    def cancel_scheduled_event(self, event_id: str) -> bool:
        """
        Cancel a scheduled event.
        
        Args:
            event_id: ID of the event to cancel
            
        Returns:
            True if the event was canceled, False if not found
        """
        db_event = scheduled_game_event_crud.get_by_event_id(self.db, event_id)
        
        if not db_event:
            logger.warning(f"Cannot cancel event {event_id}: not found")
            return False
        
        scheduled_game_event_crud.remove(self.db, id=db_event.id)
        logger.info(f"Canceled scheduled event {event_id}")
        
        return True
    
    def _check_and_trigger_scheduled_events(self, current_datetime: GameDateTime) -> None:
        """
        Check for scheduled events that should be triggered and trigger them.
        
        Args:
            current_datetime: Current game datetime
        """
        # Get all due events
        due_events = scheduled_game_event_crud.get_events_due(self.db, self.game_id, current_datetime)
        
        for db_event in due_events:
            # Convert to Pydantic model
            event = scheduled_game_event_crud.convert_to_model(db_event)
            
            # Trigger the event
            self._trigger_scheduled_event(event)
            
            # Handle recurring events
            if event.is_recurring and event.recurrence_interval_minutes:
                # Calculate next trigger time
                next_trigger_datetime = event.trigger_datetime.add_minutes(
                    event.recurrence_interval_minutes, self.settings
                )
                
                # Update the event with the new trigger time
                scheduled_game_event_crud.update(self.db, db_obj=db_event, obj_in={
                    "trigger_year": next_trigger_datetime.year,
                    "trigger_month": next_trigger_datetime.month,
                    "trigger_day": next_trigger_datetime.day,
                    "trigger_hour": next_trigger_datetime.hour,
                    "trigger_minute": next_trigger_datetime.minute
                })
                
                logger.info(
                    f"Rescheduled recurring event {event.event_id} for {next_trigger_datetime.format()}"
                )
            else:
                # Remove one-time events after they've triggered
                scheduled_game_event_crud.remove(self.db, id=db_event.id)
                logger.info(f"Removed one-time event {event.event_id} after triggering")
    
    def _trigger_scheduled_event(self, event: ScheduledGameEvent) -> None:
        """
        Trigger a scheduled event by publishing it on the event bus.
        
        Args:
            event: The event to trigger
        """
        game_event = GameEvent(
            event_type=EventType.SCHEDULED_EVENT_TRIGGERED,
            context={
                "game_id": self.game_id,
                "scheduled_event_id": event.event_id,
                "event_type": event.event_type,
                "event_context": event.event_context,
                "trigger_datetime": {
                    "year": event.trigger_datetime.year,
                    "month": event.trigger_datetime.month,
                    "day": event.trigger_datetime.day,
                    "hour": event.trigger_datetime.hour,
                    "minute": event.trigger_datetime.minute
                },
                "is_recurring": event.is_recurring,
                "recurrence_interval_minutes": event.recurrence_interval_minutes
            },
            source_id=None,
            target_id=event.character_id
        )
        
        event_bus.publish(game_event)
        logger.info(f"Triggered scheduled event {event.event_id} of type {event.event_type}")
    
    def calculate_time_until_block(self, target_block: TimeBlock, current_dt: Optional[GameDateTime] = None) -> int:
        """
        Calculate the minutes until the start of a specified time block.
        
        Args:
            target_block: The time block to calculate time until
            current_dt: The current datetime (uses system current time if not provided)
            
        Returns:
            Minutes until the start of the target time block
        """
        if current_dt is None:
            current_dt = self.get_current_datetime()
        
        # Get the target block's start hour
        target_start_hour, _ = self.settings.time_block_definitions[target_block]
        
        # If we're already in the target block, we need to calculate time until the next occurrence
        current_block = self.get_current_time_block()
        
        if current_block == target_block:
            # We're already in this block, so calculate time until the next day's occurrence
            target_dt = GameDateTime(
                year=current_dt.year,
                month=current_dt.month,
                day=current_dt.day + 1,  # Next day
                hour=target_start_hour,
                minute=0
            )
        elif current_dt.hour < target_start_hour:
            # Target block is later today
            target_dt = GameDateTime(
                year=current_dt.year,
                month=current_dt.month,
                day=current_dt.day,
                hour=target_start_hour,
                minute=0
            )
        else:
            # Target block is tomorrow
            target_dt = GameDateTime(
                year=current_dt.year,
                month=current_dt.month,
                day=current_dt.day + 1,
                hour=target_start_hour,
                minute=0
            )
        
        # Handle date overflow
        target_dt = target_dt.add_minutes(0, self.settings)
        
        # Calculate minutes between the current time and target time
        current_minutes = current_dt.to_minutes(self.settings)
        target_minutes = target_dt.to_minutes(self.settings)
        
        return target_minutes - current_minutes
    
    def calculate_time_until_datetime(self, target_dt: GameDateTime, current_dt: Optional[GameDateTime] = None) -> int:
        """
        Calculate the minutes until a specified datetime.
        
        Args:
            target_dt: The target datetime
            current_dt: The current datetime (uses system current time if not provided)
            
        Returns:
            Minutes until the target datetime, or 0 if the target is in the past
        """
        if current_dt is None:
            current_dt = self.get_current_datetime()
        
        # Calculate minutes between the current time and target time
        current_minutes = current_dt.to_minutes(self.settings)
        target_minutes = target_dt.to_minutes(self.settings)
        
        minutes_until = target_minutes - current_minutes
        
        # Return 0 if the target is in the past
        return max(0, minutes_until)
    
    # Helper methods for common time advances
    def advance_minutes(self, minutes: int) -> GameDateTime:
        """Advance time by a specific number of minutes."""
        return self.advance_time(minutes)
    
    def advance_hours(self, hours: int) -> GameDateTime:
        """Advance time by a specific number of hours."""
        return self.advance_time(hours * self.settings.minutes_per_hour)
    
    def advance_days(self, days: int) -> GameDateTime:
        """Advance time by a specific number of days."""
        return self.advance_time(days * self.settings.hours_per_day * self.settings.minutes_per_hour)
    
    def advance_until_block(self, target_block: TimeBlock) -> GameDateTime:
        """Advance time until the start of a specific time block."""
        minutes_to_advance = self.calculate_time_until_block(target_block)
        return self.advance_time(minutes_to_advance)
    
    def advance_until_datetime(self, target_dt: GameDateTime) -> GameDateTime:
        """Advance time until a specific datetime."""
        minutes_to_advance = self.calculate_time_until_datetime(target_dt)
        return self.advance_time(minutes_to_advance)
    
    def format_datetime(self, dt: Optional[GameDateTime] = None) -> str:
        """
        Format a datetime for display to the player.
        
        Args:
            dt: The datetime to format (uses current time if not provided)
            
        Returns:
            A formatted string representing the datetime
        """
        if dt is None:
            dt = self.get_current_datetime()
        
        time_block = dt.get_time_description(self.settings)
        season = dt.get_season(self.settings).value
        
        # Format: "MORNING, Spring - Year 1000, Month 3, Day 21"
        return f"{time_block}, {season} - Year {dt.year}, Month {dt.month}, Day {dt.day}"