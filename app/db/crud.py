"""
CRUD operations for the Time System.
This module provides functions for interacting with the time-related database models.
"""

from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Union
from uuid import uuid4
from sqlalchemy.orm import Session

from app.db.models import DBGameTimeState, DBScheduledGameEvent
from app.models.time_models import GameDateTime, ScheduledGameEvent, GameTimeSettings

# Generic type for database models
ModelType = TypeVar("ModelType", bound=Any)

class CRUDBase(Generic[ModelType]):
    """Base class for CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUD operations with a specific model.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
    
    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            The record if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get multiple records.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Dictionary with values to create
            
        Returns:
            The created record
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Record to update
            obj_in: Dictionary with values to update
            
        Returns:
            The updated record
        """
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: str) -> ModelType:
        """
        Remove a record.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            The removed record
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDGameTimeState(CRUDBase[DBGameTimeState]):
    """CRUD operations for GameTimeState."""
    
    def get_by_game_id(self, db: Session, game_id: str) -> Optional[DBGameTimeState]:
        """
        Get the time state for a specific game.
        
        Args:
            db: Database session
            game_id: Game ID
            
        Returns:
            The game time state if found, None otherwise
        """
        return db.query(DBGameTimeState).filter(DBGameTimeState.game_id == game_id).first()
    
    def create_or_update(self, db: Session, *, game_id: str, datetime: GameDateTime) -> DBGameTimeState:
        """
        Create or update the time state for a specific game.
        
        Args:
            db: Database session
            game_id: Game ID
            datetime: New game datetime
            
        Returns:
            The created or updated game time state
        """
        db_obj = self.get_by_game_id(db, game_id)
        
        if db_obj:
            # Update existing time state
            return self.update(db, db_obj=db_obj, obj_in={
                "year": datetime.year,
                "month": datetime.month,
                "day": datetime.day,
                "hour": datetime.hour,
                "minute": datetime.minute
            })
        else:
            # Create new time state
            return self.create(db, obj_in={
                "game_id": game_id,
                "year": datetime.year,
                "month": datetime.month,
                "day": datetime.day,
                "hour": datetime.hour,
                "minute": datetime.minute
            })
    
    def get_datetime(self, db: Session, game_id: str) -> Optional[GameDateTime]:
        """
        Get the current datetime for a specific game.
        
        Args:
            db: Database session
            game_id: Game ID
            
        Returns:
            The current game datetime if found, None otherwise
        """
        db_obj = self.get_by_game_id(db, game_id)
        
        if not db_obj:
            return None
        
        return GameDateTime(
            year=db_obj.year,
            month=db_obj.month,
            day=db_obj.day,
            hour=db_obj.hour,
            minute=db_obj.minute
        )


class CRUDScheduledGameEvent(CRUDBase[DBScheduledGameEvent]):
    """CRUD operations for ScheduledGameEvent."""
    
    def get_by_event_id(self, db: Session, event_id: str) -> Optional[DBScheduledGameEvent]:
        """
        Get a scheduled event by its event ID.
        
        Args:
            db: Database session
            event_id: Event ID
            
        Returns:
            The scheduled event if found, None otherwise
        """
        return db.query(DBScheduledGameEvent).filter(DBScheduledGameEvent.event_id == event_id).first()
    
    def get_by_game_id(self, db: Session, game_id: str) -> List[DBScheduledGameEvent]:
        """
        Get all scheduled events for a specific game.
        
        Args:
            db: Database session
            game_id: Game ID
            
        Returns:
            List of scheduled events
        """
        game_time_state = db.query(DBGameTimeState).filter(DBGameTimeState.game_id == game_id).first()
        
        if not game_time_state:
            return []
        
        return db.query(DBScheduledGameEvent).filter(
            DBScheduledGameEvent.game_time_state_id == game_time_state.id
        ).all()
    
    def create_event(self, db: Session, *, game_id: str, event: ScheduledGameEvent) -> DBScheduledGameEvent:
        """
        Create a new scheduled event.
        
        Args:
            db: Database session
            game_id: Game ID
            event: Event details
            
        Returns:
            The created scheduled event
        """
        # Get game time state
        game_time_state = db.query(DBGameTimeState).filter(DBGameTimeState.game_id == game_id).first()
        
        if not game_time_state:
            # Create game time state if it doesn't exist yet
            # This shouldn't normally happen as the game time state should be created before scheduling events
            game_time_state = CRUDGameTimeState(DBGameTimeState).create(db, obj_in={
                "game_id": game_id,
                "year": 1000,  # Default starting year
                "month": 1,
                "day": 1,
                "hour": 8,  # Default starting time - 8:00 AM
                "minute": 0
            })
        
        # Create the scheduled event
        return self.create(db, obj_in={
            "event_id": event.event_id,
            "game_time_state_id": game_time_state.id,
            "trigger_year": event.trigger_datetime.year,
            "trigger_month": event.trigger_datetime.month,
            "trigger_day": event.trigger_datetime.day,
            "trigger_hour": event.trigger_datetime.hour,
            "trigger_minute": event.trigger_datetime.minute,
            "event_type": event.event_type,
            "event_context": event.event_context,
            "character_id": event.character_id,
            "is_recurring": event.is_recurring,
            "recurrence_interval_minutes": event.recurrence_interval_minutes
        })
    
    def get_events_due(self, db: Session, game_id: str, current_datetime: GameDateTime) -> List[DBScheduledGameEvent]:
        """
        Get all scheduled events that are due to be triggered.
        
        Args:
            db: Database session
            game_id: Game ID
            current_datetime: Current game datetime
            
        Returns:
            List of scheduled events that are due
        """
        game_time_state = db.query(DBGameTimeState).filter(DBGameTimeState.game_id == game_id).first()
        
        if not game_time_state:
            return []
        
        # Get all events for this game
        all_events = db.query(DBScheduledGameEvent).filter(
            DBScheduledGameEvent.game_time_state_id == game_time_state.id
        ).all()
        
        # Filter for events that are due
        due_events = []
        for event in all_events:
            event_datetime = GameDateTime(
                year=event.trigger_year,
                month=event.trigger_month,
                day=event.trigger_day,
                hour=event.trigger_hour,
                minute=event.trigger_minute
            )
            
            if event_datetime <= current_datetime:
                due_events.append(event)
        
        return due_events
    
    def convert_to_model(self, db_event: DBScheduledGameEvent) -> ScheduledGameEvent:
        """
        Convert a database event to a Pydantic model.
        
        Args:
            db_event: Database event
            
        Returns:
            Pydantic model representation
        """
        return ScheduledGameEvent(
            event_id=db_event.event_id,
            trigger_datetime=GameDateTime(
                year=db_event.trigger_year,
                month=db_event.trigger_month,
                day=db_event.trigger_day,
                hour=db_event.trigger_hour,
                minute=db_event.trigger_minute
            ),
            event_type=db_event.event_type,
            event_context=db_event.event_context or {},
            character_id=db_event.character_id,
            is_recurring=db_event.is_recurring,
            recurrence_interval_minutes=db_event.recurrence_interval_minutes
        )


# Create instances for each CRUD class
game_time_state_crud = CRUDGameTimeState(DBGameTimeState)
scheduled_game_event_crud = CRUDScheduledGameEvent(DBScheduledGameEvent)