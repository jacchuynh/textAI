"""
Weather System Models

This module defines the data models for the Weather System, including weather types,
conditions, patterns, and effects.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum as SQLAEnum, Text
from sqlalchemy.orm import relationship

from app.db.base import Base

class WeatherType(str, Enum):
    """Types of weather that can occur in the game world."""
    CLEAR = "CLEAR"
    CLOUDY = "CLOUDY"
    PARTLY_CLOUDY = "PARTLY_CLOUDY"
    FOG = "FOG"
    LIGHT_RAIN = "LIGHT_RAIN"
    HEAVY_RAIN = "HEAVY_RAIN"
    THUNDERSTORM = "THUNDERSTORM"
    LIGHT_SNOW = "LIGHT_SNOW"
    HEAVY_SNOW = "HEAVY_SNOW"
    BLIZZARD = "BLIZZARD"
    WINDY = "WINDY"
    GALE = "GALE"
    DUST_STORM = "DUST_STORM"
    HAIL = "HAIL"
    
    @property
    def description(self) -> str:
        """Get a description of this weather type."""
        descriptions = {
            self.CLEAR: "Clear skies with excellent visibility and no cloud cover.",
            self.CLOUDY: "Overcast with a blanket of clouds covering the sky.",
            self.PARTLY_CLOUDY: "Patches of clouds with intermittent sunshine.",
            self.FOG: "A thick mist limiting visibility to just a few yards.",
            self.LIGHT_RAIN: "A gentle drizzle that dampens the surroundings.",
            self.HEAVY_RAIN: "A downpour that soaks everything and creates puddles and streams.",
            self.THUNDERSTORM: "Violent rain accompanied by lightning and booming thunder.",
            self.LIGHT_SNOW: "Gentle snowflakes falling and dusting the ground.",
            self.HEAVY_SNOW: "Thick snowflakes accumulating rapidly on all surfaces.",
            self.BLIZZARD: "Howling winds carrying snow, severely limiting visibility.",
            self.WINDY: "Strong gusts that rustle leaves and make clothing flap.",
            self.GALE: "Powerful winds that can bend trees and make walking difficult.",
            self.DUST_STORM: "Clouds of dust and debris carried by fierce winds.",
            self.HAIL: "Ice pellets falling from the sky, potentially causing harm."
        }
        return descriptions.get(self, "Unknown weather type")

class PrecipitationType(str, Enum):
    """Types of precipitation that can occur with different weather types."""
    NONE = "NONE"
    RAIN = "RAIN"
    SNOW = "SNOW"
    HAIL = "HAIL"

class WindDirection(str, Enum):
    """Cardinal and ordinal directions for wind."""
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"

class VisibilityLevel(str, Enum):
    """Descriptive levels of visibility."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    POOR = "POOR"
    VERY_POOR = "VERY_POOR"

class WeatherEffectType(str, Enum):
    """Types of effects that weather can have on entities or regions."""
    MOVEMENT_PENALTY = "MOVEMENT_PENALTY"
    VISIBILITY_REDUCTION = "VISIBILITY_REDUCTION"
    CROP_YIELD_MODIFIER = "CROP_YIELD_MODIFIER"
    RESOURCE_GATHERING_DIFFICULTY = "RESOURCE_GATHERING_DIFFICULTY"
    COMFORT_DECREASE = "COMFORT_DECREASE"
    WARMTH_LOSS = "WARMTH_LOSS"
    SPELL_EFFECTIVENESS = "SPELL_EFFECTIVENESS"
    COMBAT_ADVANTAGE = "COMBAT_ADVANTAGE"
    STAMINA_DRAIN = "STAMINA_DRAIN"
    TERRAIN_DIFFICULTY = "TERRAIN_DIFFICULTY"
    SHELTER_REQUIREMENT = "SHELTER_REQUIREMENT"
    PERCEPTION_PENALTY = "PERCEPTION_PENALTY"

# SQLAlchemy Models
class DBWeatherCondition(Base):
    """Database model for weather conditions."""
    __tablename__ = "weather_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    weather_type = Column(SQLAEnum(WeatherType), nullable=False)
    temperature = Column(Float, nullable=False)
    temperature_feels_like = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(SQLAEnum(WindDirection), nullable=False)
    precipitation_type = Column(SQLAEnum(PrecipitationType), nullable=False)
    precipitation_intensity = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    cloud_cover = Column(Float, nullable=False)
    visibility = Column(SQLAEnum(VisibilityLevel), nullable=False)
    generated_description = Column(Text, nullable=False)
    expected_duration_hours = Column(Float, nullable=True)
    
    # Relationships
    active_effects = relationship("DBActiveWeatherEffect", back_populates="weather_condition")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "region_id": self.region_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "weather_type": self.weather_type.value if self.weather_type else None,
            "temperature": self.temperature,
            "temperature_feels_like": self.temperature_feels_like,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction.value if self.wind_direction else None,
            "precipitation_type": self.precipitation_type.value if self.precipitation_type else None,
            "precipitation_intensity": self.precipitation_intensity,
            "humidity": self.humidity,
            "cloud_cover": self.cloud_cover,
            "visibility": self.visibility.value if self.visibility else None,
            "generated_description": self.generated_description,
            "expected_duration_hours": self.expected_duration_hours
        }

class DBWeatherPattern(Base):
    """Database model for weather patterns by region and season."""
    __tablename__ = "weather_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String(50), index=True, nullable=False)
    season = Column(String(10), nullable=False)  # SPRING, SUMMER, AUTUMN, WINTER
    weather_type_probabilities = Column(JSON, nullable=False)  # {"CLEAR": 0.4, "LIGHT_RAIN": 0.2, ...}
    temperature_base_min = Column(Float, nullable=False)
    temperature_base_max = Column(Float, nullable=False)
    humidity_range_min = Column(Float, nullable=False)
    humidity_range_max = Column(Float, nullable=False)
    default_wind_speeds = Column(JSON, nullable=False)  # {"min": 5, "max": 15, "gust_chance": 0.1, "gust_max_multiplier": 1.5}
    precipitation_chances = Column(JSON, nullable=False)  # {"RAIN": 0.3, "SNOW": 0.1, "HAIL": 0.05}
    cloud_cover_range_min = Column(Float, nullable=False)
    cloud_cover_range_max = Column(Float, nullable=False)
    transition_matrices = Column(JSON, nullable=False)  # Markov chain transition probabilities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "region_id": self.region_id,
            "season": self.season,
            "weather_type_probabilities": self.weather_type_probabilities,
            "temperature_base_min": self.temperature_base_min,
            "temperature_base_max": self.temperature_base_max,
            "humidity_range_min": self.humidity_range_min,
            "humidity_range_max": self.humidity_range_max,
            "default_wind_speeds": self.default_wind_speeds,
            "precipitation_chances": self.precipitation_chances,
            "cloud_cover_range_min": self.cloud_cover_range_min,
            "cloud_cover_range_max": self.cloud_cover_range_max,
            "transition_matrices": self.transition_matrices
        }

class DBActiveWeatherEffect(Base):
    """Database model for active weather effects."""
    __tablename__ = "active_weather_effects"
    
    id = Column(Integer, primary_key=True, index=True)
    weather_condition_id = Column(Integer, ForeignKey("weather_conditions.id"), nullable=False)
    target_entity_id = Column(String(50), nullable=True)
    target_entity_type = Column(String(50), nullable=True)
    effect_type = Column(SQLAEnum(WeatherEffectType), nullable=False)
    modifier_value = Column(JSON, nullable=False)  # Could be a JSON string for complex modifiers
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    calculated_end_time = Column(DateTime, nullable=False)
    
    # Relationships
    weather_condition = relationship("DBWeatherCondition", back_populates="active_effects")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "weather_condition_id": self.weather_condition_id,
            "target_entity_id": self.target_entity_id,
            "target_entity_type": self.target_entity_type,
            "effect_type": self.effect_type.value if self.effect_type else None,
            "modifier_value": self.modifier_value,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "calculated_end_time": self.calculated_end_time.isoformat() if self.calculated_end_time else None
        }

# Pydantic Models (for API/internal use)
class WeatherConditionPydantic(BaseModel):
    """Pydantic model for weather conditions."""
    id: Optional[int] = None
    region_id: str
    timestamp: datetime
    weather_type: WeatherType
    temperature: float
    temperature_feels_like: float
    wind_speed: float
    wind_direction: WindDirection
    precipitation_type: PrecipitationType
    precipitation_intensity: float = Field(ge=0.0, le=1.0)
    humidity: float = Field(ge=0.0, le=1.0)
    cloud_cover: float = Field(ge=0.0, le=1.0)
    visibility: VisibilityLevel
    generated_description: str
    expected_duration_hours: Optional[float] = None
    
    class Config:
        orm_mode = True

class WeatherPatternPydantic(BaseModel):
    """Pydantic model for weather patterns."""
    id: Optional[int] = None
    region_id: str
    season: str  # SPRING, SUMMER, AUTUMN, WINTER
    weather_type_probabilities: Dict[WeatherType, float]
    temperature_base_min: float
    temperature_base_max: float
    humidity_range_min: float = Field(ge=0.0, le=1.0)
    humidity_range_max: float = Field(ge=0.0, le=1.0)
    default_wind_speeds: Dict[str, float]  # {"min": 5, "max": 15, "gust_chance": 0.1, "gust_max_multiplier": 1.5}
    precipitation_chances: Dict[PrecipitationType, float]
    cloud_cover_range_min: float = Field(ge=0.0, le=1.0)
    cloud_cover_range_max: float = Field(ge=0.0, le=1.0)
    transition_matrices: Dict[str, List[List[float]]]  # Markov chain transition probabilities
    
    class Config:
        orm_mode = True
    
    @validator('weather_type_probabilities')
    def validate_probabilities(cls, v):
        """Validate that probabilities sum to approximately 1.0."""
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # Allow for small floating-point errors
            raise ValueError(f"Weather type probabilities must sum to 1.0, got {total}")
        return v
    
    @validator('humidity_range_max')
    def validate_humidity_range(cls, v, values):
        """Validate that humidity_range_max >= humidity_range_min."""
        if 'humidity_range_min' in values and v < values['humidity_range_min']:
            raise ValueError("humidity_range_max must be >= humidity_range_min")
        return v
    
    @validator('cloud_cover_range_max')
    def validate_cloud_cover_range(cls, v, values):
        """Validate that cloud_cover_range_max >= cloud_cover_range_min."""
        if 'cloud_cover_range_min' in values and v < values['cloud_cover_range_min']:
            raise ValueError("cloud_cover_range_max must be >= cloud_cover_range_min")
        return v

class ActiveWeatherEffectPydantic(BaseModel):
    """Pydantic model for active weather effects."""
    id: Optional[int] = None
    weather_condition_id: int
    target_entity_id: Optional[str] = None
    target_entity_type: Optional[str] = None
    effect_type: WeatherEffectType
    modifier_value: Dict[str, Any]
    description: str
    start_time: datetime
    calculated_end_time: datetime
    
    class Config:
        orm_mode = True