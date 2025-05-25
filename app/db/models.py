"""
SQLAlchemy database models for the Time System.
These models represent the database tables for storing time-related information.
"""

import json
import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class DBGameTimeState(Base):
    """
    Database model for storing the current game time state.
    Each game (or world) has its own time state.
    """
    __tablename__ = "game_time_states"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, unique=True, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    
    # Relationships
    scheduled_events = relationship("DBScheduledGameEvent", back_populates="game_time_state")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "game_id": self.game_id,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute
        }


class DBScheduledGameEvent(Base):
    """
    Database model for storing scheduled game events.
    Events can be one-time or recurring and are triggered when game time reaches their scheduled time.
    """
    __tablename__ = "scheduled_game_events"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, unique=True, index=True, nullable=False)
    game_time_state_id = Column(String, ForeignKey("game_time_states.id"), nullable=False)
    
    # Trigger datetime components
    trigger_year = Column(Integer, nullable=False)
    trigger_month = Column(Integer, nullable=False)
    trigger_day = Column(Integer, nullable=False)
    trigger_hour = Column(Integer, nullable=False)
    trigger_minute = Column(Integer, nullable=False)
    
    event_type = Column(String, nullable=False)
    event_context = Column(JSON, nullable=True)
    character_id = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_interval_minutes = Column(Integer, nullable=True)
    
    # Relationships
    game_time_state = relationship("DBGameTimeState", back_populates="scheduled_events")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "game_time_state_id": self.game_time_state_id,
            "trigger_year": self.trigger_year,
            "trigger_month": self.trigger_month,
            "trigger_day": self.trigger_day,
            "trigger_hour": self.trigger_hour,
            "trigger_minute": self.trigger_minute,
            "event_type": self.event_type,
            "event_context": self.event_context,
            "character_id": self.character_id,
            "is_recurring": self.is_recurring,
            "recurrence_interval_minutes": self.recurrence_interval_minutes
        }