"""
Time System Models

This module defines Pydantic models for the game's time system, which tracks
and manages the passage of time in the game world.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class TimeBlock(str, Enum):
    """Time blocks representing different parts of the day."""
    DEAD_OF_NIGHT = "DEAD_OF_NIGHT"
    LATE_NIGHT = "LATE_NIGHT"
    DAWN = "DAWN"
    MORNING = "MORNING"
    MIDDAY = "MIDDAY" 
    AFTERNOON = "AFTERNOON"
    DUSK = "DUSK"
    EVENING = "EVENING"

class Season(str, Enum):
    """Seasons of the year."""
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"
    WINTER = "WINTER"

class GameDateTime(BaseModel):
    """
    Model representing a specific date and time in the game world.
    Allows for easy manipulation and comparison of game times.
    """
    year: int = Field(ge=0)
    month: int = Field(ge=1)
    day: int = Field(ge=1)
    hour: int = Field(ge=0, lt=24)
    minute: int = Field(ge=0, lt=60)
    
    @validator('month')
    def validate_month(cls, v, values, **kwargs):
        """Validate month is within proper range."""
        if v < 1 or v > 12:
            raise ValueError(f"Month must be between 1 and 12, got {v}")
        return v
    
    @validator('day')
    def validate_day(cls, v, values, **kwargs):
        """Validate day is within proper range for the month."""
        # This is a simplified validation, in a full implementation we would 
        # check against days_per_month from GameTimeSettings
        month = values.get('month', 1)
        max_days = 31  # Simplified - actual days would depend on month
        if v < 1 or v > max_days:
            raise ValueError(f"Day must be between 1 and {max_days} for month {month}, got {v}")
        return v
    
    def add_minutes(self, minutes: int, settings: 'GameTimeSettings') -> 'GameDateTime':
        """
        Add the specified number of minutes to this GameDateTime.
        
        Args:
            minutes: Number of minutes to add (can be negative)
            settings: Game time settings to use for calendar calculations
            
        Returns:
            A new GameDateTime instance with the added time
        """
        result = self.copy(deep=True)
        
        # Handle adding minutes
        result.minute += minutes
        
        # Handle minute overflow
        while result.minute >= settings.minutes_per_hour:
            result.minute -= settings.minutes_per_hour
            result.hour += 1
        
        # Handle hour overflow
        while result.hour >= settings.hours_per_day:
            result.hour -= settings.hours_per_day
            result.day += 1
        
        # Handle day overflow - simplified version
        while result.day > settings.days_per_month.get(result.month, 30):
            result.day -= settings.days_per_month.get(result.month, 30)
            result.month += 1
            
            # Handle month overflow
            if result.month > settings.months_per_year:
                result.month = 1
                result.year += 1
        
        # Handle negative time (going backward)
        while result.minute < 0:
            result.minute += settings.minutes_per_hour
            result.hour -= 1
        
        while result.hour < 0:
            result.hour += settings.hours_per_day
            result.day -= 1
        
        while result.day < 1:
            result.month -= 1
            if result.month < 1:
                result.month = settings.months_per_year
                result.year -= 1
            result.day += settings.days_per_month.get(result.month, 30)
        
        return result
    
    def to_minutes(self, settings: 'GameTimeSettings') -> int:
        """
        Convert this GameDateTime to a total minute count from year zero.
        Useful for easy comparison of GameDateTimes.
        
        Args:
            settings: Game time settings to use for calendar calculations
            
        Returns:
            Total minutes from year zero
        """
        total_minutes = 0
        
        # Add minutes from years
        for y in range(self.year):
            for m in range(1, settings.months_per_year + 1):
                total_minutes += settings.days_per_month.get(m, 30) * settings.hours_per_day * settings.minutes_per_hour
        
        # Add minutes from months in current year
        for m in range(1, self.month):
            total_minutes += settings.days_per_month.get(m, 30) * settings.hours_per_day * settings.minutes_per_hour
        
        # Add minutes from days in current month
        total_minutes += (self.day - 1) * settings.hours_per_day * settings.minutes_per_hour
        
        # Add minutes from hours in current day
        total_minutes += self.hour * settings.minutes_per_hour
        
        # Add minutes in current hour
        total_minutes += self.minute
        
        return total_minutes
    
    def __lt__(self, other: 'GameDateTime') -> bool:
        """Less than comparison."""
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        if self.day != other.day:
            return self.day < other.day
        if self.hour != other.hour:
            return self.hour < other.hour
        return self.minute < other.minute
    
    def __gt__(self, other: 'GameDateTime') -> bool:
        """Greater than comparison."""
        if self.year != other.year:
            return self.year > other.year
        if self.month != other.month:
            return self.month > other.month
        if self.day != other.day:
            return self.day > other.day
        if self.hour != other.hour:
            return self.hour > other.hour
        return self.minute > other.minute
    
    def __eq__(self, other: object) -> bool:
        """Equal comparison."""
        if not isinstance(other, GameDateTime):
            return False
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day and
                self.hour == other.hour and
                self.minute == other.minute)
    
    def __le__(self, other: 'GameDateTime') -> bool:
        """Less than or equal comparison."""
        return self < other or self == other
    
    def __ge__(self, other: 'GameDateTime') -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other
    
    def format(self) -> str:
        """Format the date and time as a string."""
        return f"Year {self.year}, Month {self.month}, Day {self.day}, {self.hour:02d}:{self.minute:02d}"
    
    def get_time_description(self, settings: 'GameTimeSettings') -> str:
        """Get a narrative description of the current time of day."""
        for time_block, (start_hour, end_hour) in settings.time_block_definitions.items():
            if start_hour <= self.hour < end_hour:
                return time_block.value
        return "Unknown time of day"
    
    def get_season(self, settings: 'GameTimeSettings') -> Season:
        """Get the current season based on the date."""
        for season, (start_month, start_day) in settings.season_definitions.items():
            # This is a simplified version, a more complex implementation would handle year wrapping
            if self.month > start_month or (self.month == start_month and self.day >= start_day):
                return season
        return Season.WINTER  # Default to winter if no match found

class GameTimeSettings(BaseModel):
    """
    Configuration settings for the game time system.
    Defines the structure of the game calendar and time blocks.
    """
    minutes_per_hour: int = 60
    hours_per_day: int = 24
    days_per_month: Dict[int, int] = Field(default_factory=lambda: {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    })
    months_per_year: int = 12
    year_zero_epoch: int = 1000  # Starting year of the game world
    
    season_definitions: Dict[Season, Tuple[int, int]] = Field(default_factory=lambda: {
        Season.SPRING: (3, 1),   # Spring starts on Month 3, Day 1
        Season.SUMMER: (6, 1),   # Summer starts on Month 6, Day 1
        Season.AUTUMN: (9, 1),   # Autumn starts on Month 9, Day 1
        Season.WINTER: (12, 1)   # Winter starts on Month 12, Day 1
    })
    
    time_block_definitions: Dict[TimeBlock, Tuple[int, int]] = Field(default_factory=lambda: {
        TimeBlock.DEAD_OF_NIGHT: (0, 3),    # 12am-3am
        TimeBlock.LATE_NIGHT: (3, 6),       # 3am-6am
        TimeBlock.DAWN: (6, 8),             # 6am-8am
        TimeBlock.MORNING: (8, 11),         # 8am-11am
        TimeBlock.MIDDAY: (11, 14),         # 11am-2pm
        TimeBlock.AFTERNOON: (14, 18),      # 2pm-6pm
        TimeBlock.DUSK: (18, 20),           # 6pm-8pm
        TimeBlock.EVENING: (20, 24)         # 8pm-12am
    })
    
    @validator('days_per_month')
    def validate_days_per_month(cls, v):
        """Validate that all months have a reasonable number of days."""
        for month, days in v.items():
            if month < 1 or month > 12:
                raise ValueError(f"Invalid month number: {month}")
            if days < 28 or days > 31:
                raise ValueError(f"Invalid number of days for month {month}: {days}")
        return v

class ScheduledGameEvent(BaseModel):
    """
    Represents an event scheduled to occur at a specific game time.
    Events can be one-time or recurring.
    """
    event_id: str
    trigger_datetime: GameDateTime
    event_type: str
    event_context: Dict[str, Any] = Field(default_factory=dict)
    character_id: Optional[str] = None
    is_recurring: bool = False
    recurrence_interval_minutes: Optional[int] = None
    
    @validator('recurrence_interval_minutes')
    def validate_recurrence(cls, v, values, **kwargs):
        """Validate that recurring events have an interval specified."""
        if values.get('is_recurring', False) and (v is None or v <= 0):
            raise ValueError("Recurring events must have a positive recurrence interval")
        return v