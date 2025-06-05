from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class SurvivalModuleType(str, Enum):
    """Enumeration of the different survival modules that can be enabled/disabled"""
    VITAL_NEEDS = "vital_needs"             # Hunger, Thirst, Fatigue
    HEALTH_INJURY = "health_injury"         # Physical state, wounds, illness
    MENTAL_STATE = "mental_state"           # Morale, clarity, stress
    EMOTIONAL_BALANCE = "emotional_balance" # Mood swings, burnout, loneliness
    SHELTER_COMFORT = "shelter_comfort"     # Exposure, rest, safe places
    RESOURCES_ECONOMY = "resources_economy" # Inventory, money, crafting materials


class CampaignType(str, Enum):
    """Campaign types with different recommended survival modules"""
    COMBAT = "combat"               # Combat-focused campaign
    SURVIVAL = "survival"           # Wilderness survival campaign
    HORROR = "horror"               # Horror-themed campaign 
    POLITICAL = "political"         # Political intrigue campaign
    SLICE_OF_LIFE = "slice_of_life" # Everyday life campaign
    EXPLORATION = "exploration"     # Exploration-focused campaign


class MoodState(str, Enum):
    """Enumeration of different mood states for emotional tracking"""
    ELATED = "elated"
    HAPPY = "happy"
    CONTENT = "content"
    NEUTRAL = "neutral"
    CONCERNED = "concerned"
    STRESSED = "stressed"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    PANICKED = "panicked"


class ShelterQuality(str, Enum):
    """Enumeration of shelter quality levels"""
    EXCELLENT = "excellent"     # Luxury accommodations
    GOOD = "good"               # Comfortable home
    ADEQUATE = "adequate"       # Basic shelter
    POOR = "poor"               # Minimal protection
    EXPOSED = "exposed"         # No real shelter
    HAZARDOUS = "hazardous"     # Dangerous environment


class SurvivalStateUpdate(BaseModel):
    """Model for updates to a character's survival state"""
    hunger: Optional[int] = None
    thirst: Optional[int] = None
    fatigue: Optional[int] = None
    current_health: Optional[int] = None
    max_health: Optional[int] = None
    morale: Optional[int] = None
    clarity: Optional[int] = None
    mood: Optional[MoodState] = None
    shelter_quality: Optional[ShelterQuality] = None
    inventory_updates: Optional[Dict[str, int]] = None


class SurvivalState(BaseModel):
    """A character's current survival state across all modules"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Vital Needs Module
    hunger: int = Field(default=100, ge=0, le=100)        # 0 = starving, 100 = full
    thirst: int = Field(default=100, ge=0, le=100)        # 0 = dehydrated, 100 = hydrated
    fatigue: int = Field(default=0, ge=0, le=100)         # 0 = rested, 100 = exhausted
    
    # Health & Injury Module
    current_health: int = Field(default=100, ge=0)         # Current health points
    max_health: int = Field(default=100, ge=1)            # Maximum health points (scales with progression)
    injuries: Dict[str, int] = Field(default_factory=dict) # Specific injuries and severity
    
    # Mental State Module
    morale: int = Field(default=100, ge=0, le=100)        # 0 = breakdown, 100 = excellent spirits
    clarity: int = Field(default=100, ge=0, le=100)       # 0 = confused/hallucinating, 100 = perfect clarity
    stress: int = Field(default=0, ge=0, le=100)          # 0 = calm, 100 = extreme stress
    
    # Emotional Balance Module
    mood: MoodState = Field(default=MoodState.NEUTRAL)    # Current emotional state
    emotional_stability: int = Field(default=100, ge=0, le=100) # How stable emotions are
    social_connection: int = Field(default=50, ge=0, le=100)    # Sense of connection to others
    
    # Shelter & Comfort Module
    shelter_quality: ShelterQuality = Field(default=ShelterQuality.ADEQUATE)
    exposure: int = Field(default=0, ge=0, le=100)        # 0 = protected, 100 = fully exposed
    comfort: int = Field(default=50, ge=0, le=100)        # 0 = miserable, 100 = luxurious
    
    # Resources & Economy Module
    inventory: Dict[str, int] = Field(default_factory=dict) # Items and quantities
    
    # History tracking for state changes over time
    state_history: List[Dict] = Field(default_factory=list)
    
    def update_state(self, update: SurvivalStateUpdate):
        """Update the survival state with changes and record history"""
        # Store current state in history before updating
        current_state = {
            "timestamp": datetime.now(),
            "hunger": self.hunger,
            "thirst": self.thirst,
            "fatigue": self.fatigue,
            "current_health": self.current_health,
            "max_health": self.max_health,
            "morale": self.morale,
            "clarity": self.clarity,
            "mood": self.mood,
            "shelter_quality": self.shelter_quality
        }
        self.state_history.append(current_state)
        
        # Apply updates if they exist
        if update.hunger is not None:
            self.hunger = max(0, min(100, self.hunger + update.hunger))
        if update.thirst is not None:
            self.thirst = max(0, min(100, self.thirst + update.thirst))
        if update.fatigue is not None:
            self.fatigue = max(0, min(100, self.fatigue + update.fatigue))
        if update.current_health is not None:
            self.current_health = max(0, min(self.max_health, self.current_health + update.current_health))
        if update.max_health is not None:
            old_max = self.max_health
            self.max_health = max(1, update.max_health)
            # Scale current health proportionally if max_health increases
            if self.max_health > old_max:
                self.current_health = int((self.current_health / old_max) * self.max_health)
        if update.morale is not None:
            self.morale = max(0, min(100, self.morale + update.morale))
        if update.clarity is not None:
            self.clarity = max(0, min(100, self.clarity + update.clarity))
        if update.mood is not None:
            self.mood = update.mood
        if update.shelter_quality is not None:
            self.shelter_quality = update.shelter_quality
        if update.inventory_updates:
            for item, quantity in update.inventory_updates.items():
                if item in self.inventory:
                    self.inventory[item] += quantity
                    # Remove item if quantity is 0 or less
                    if self.inventory[item] <= 0:
                        del self.inventory[item]
                elif quantity > 0:
                    self.inventory[item] = quantity
        
        # Update timestamp
        self.updated_at = datetime.now()
    
    def get_health_percentage(self) -> float:
        """Get health as a percentage of maximum health"""
        return (self.current_health / self.max_health) * 100 if self.max_health > 0 else 0
    
    def update_max_health_from_domain(self, body_domain_value: int, base_health: Optional[int] = None):
        """Update max health based on character's Body domain value
        
        Args:
            body_domain_value: The character's Body domain value
            base_health: Optional base health value from character creation (defaults to current base)
        """
        # Use provided base_health or calculate from current max_health by removing domain contribution
        if base_health is None:
            # Extract current base health by removing domain contribution from current max_health
            # If this is the first update, default to 100
            current_base = self.max_health - (self._get_last_body_value() * 20)
            base_health = current_base if current_base > 0 else 100
            
        # Store the body value used for this calculation in state history for future reference
        self._record_body_value(body_domain_value)
            
        # Formula: base_health + 20 per Body domain point
        new_max = base_health + (body_domain_value * 20)
        
        # Create an update to handle scaling current health properly
        update = SurvivalStateUpdate(max_health=new_max)
        self.update_state(update)
        
    def _record_body_value(self, body_value: int):
        """Record Body domain value for tracking scaling history
        
        Args:
            body_value: The Body domain value to record
        """
        # Add to state history for tracking
        if not hasattr(self, "_body_value_history"):
            self._body_value_history = []
            
        self._body_value_history.append(body_value)
        
    def _get_last_body_value(self) -> int:
        """Get the last recorded Body domain value
        
        Returns:
            The last Body domain value or 0 if none recorded
        """
        if not hasattr(self, "_body_value_history") or not self._body_value_history:
            return 0
            
        return self._body_value_history[-1]
    
    def get_survival_status(self) -> Dict[str, str]:
        """Get a dictionary of status descriptions for all survival metrics"""
        status = {}
        
        # Vital Needs
        if self.hunger <= 20:
            status["hunger"] = "You are starving and desperately need food."
        elif self.hunger <= 40:
            status["hunger"] = "Your stomach growls with hunger."
        elif self.hunger <= 70:
            status["hunger"] = "You're getting hungry."
        
        if self.thirst <= 20:
            status["thirst"] = "You are severely dehydrated and need water immediately."
        elif self.thirst <= 40:
            status["thirst"] = "Your throat is parched and you need water soon."
        elif self.thirst <= 70:
            status["thirst"] = "You're feeling thirsty."
            
        if self.fatigue >= 80:
            status["fatigue"] = "You are completely exhausted and need rest."
        elif self.fatigue >= 60:
            status["fatigue"] = "You are very tired and should rest soon."
        elif self.fatigue >= 40:
            status["fatigue"] = "You're feeling somewhat tired."
        
        # Health & Injury - use percentage for thresholds
        health_percent = self.get_health_percentage()
        if health_percent <= 20:
            status["health"] = "You are critically injured and need medical attention."
        elif health_percent <= 50:
            status["health"] = "You are injured and in pain."
        elif health_percent <= 80:
            status["health"] = "You have some minor injuries."
        
        # Mental State
        if self.morale <= 30:
            status["morale"] = "You feel deeply demoralized and hopeless."
        elif self.morale <= 60:
            status["morale"] = "Your spirits are low."
        
        if self.clarity <= 40:
            status["clarity"] = "Your thoughts are foggy and confused."
        elif self.clarity <= 70:
            status["clarity"] = "You're having trouble focusing clearly."
        
        # Add more statuses for other survival metrics
            
        return status

    def get_survival_tags(self) -> List[str]:
        """Get tags for AI prompt based on current survival state"""
        tags = []
        
        # Add numerical values
        tags.append(f"hunger: {self.hunger}")
        tags.append(f"thirst: {self.thirst}")
        tags.append(f"fatigue: {self.fatigue}")
        
        # Health as both absolute and percentage
        health_percent = self.get_health_percentage()
        tags.append(f"health: {self.current_health}/{self.max_health} ({health_percent:.1f}%)")
        
        tags.append(f"morale: {self.morale}")
        tags.append(f"clarity: {self.clarity}")
        
        # Add descriptive tags for severe conditions
        if self.hunger <= 30:
            tags.append("severely_hungry")
        if self.thirst <= 30:
            tags.append("severely_thirsty")
        if self.fatigue >= 70:
            tags.append("severely_tired")
        if health_percent <= 30:
            tags.append("severely_injured")
        if self.morale <= 30:
            tags.append("severely_demoralized")
        if self.clarity <= 30:
            tags.append("confused_thinking")
        
        # Add mood and shelter status
        tags.append(f"mood: {self.mood}")
        tags.append(f"shelter: {self.shelter_quality}")
        
        return tags


class CampaignSurvivalConfig(BaseModel):
    """Configuration for which survival modules are active in a campaign"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    campaign_type: CampaignType = CampaignType.SURVIVAL
    
    # Which modules are active
    vital_needs_active: bool = True
    health_injury_active: bool = True
    mental_state_active: bool = True
    emotional_balance_active: bool = False
    shelter_comfort_active: bool = True
    resources_economy_active: bool = True
    
    # Difficulty settings (0.0 - 1.0 scale)
    survival_difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Environmental impact multipliers
    environmental_impact: Dict[str, float] = Field(
        default_factory=lambda: {
            "desert": 2.0,       # Thirst depletes faster
            "arctic": 1.5,       # Shelter more important
            "forest": 0.8,       # Food easier to find
            "mountains": 1.2,    # Fatigue increases faster
            "urban": 0.5,        # Resources more available
        }
    )
    
    @classmethod
    def create_for_campaign_type(cls, campaign_id: str, campaign_type: CampaignType) -> "CampaignSurvivalConfig":
        """Create a default configuration based on campaign type"""
        config = cls(campaign_id=campaign_id, campaign_type=campaign_type)
        
        # Adjust modules based on campaign type
        if campaign_type == CampaignType.COMBAT:
            config.vital_needs_active = True
            config.health_injury_active = True
            config.mental_state_active = False
            config.emotional_balance_active = False
            config.shelter_comfort_active = True
            config.resources_economy_active = True
        elif campaign_type == CampaignType.SURVIVAL:
            # All modules active for survival campaign
            pass
        elif campaign_type == CampaignType.HORROR:
            config.vital_needs_active = True
            config.health_injury_active = True
            config.mental_state_active = True
            config.emotional_balance_active = True
            config.shelter_comfort_active = True
            config.resources_economy_active = False
        elif campaign_type == CampaignType.POLITICAL:
            config.vital_needs_active = False
            config.health_injury_active = False
            config.mental_state_active = True
            config.emotional_balance_active = True
            config.shelter_comfort_active = False
            config.resources_economy_active = True
        elif campaign_type == CampaignType.SLICE_OF_LIFE:
            config.vital_needs_active = False
            config.health_injury_active = False
            config.mental_state_active = True
            config.emotional_balance_active = True
            config.shelter_comfort_active = True
            config.resources_economy_active = True
        elif campaign_type == CampaignType.EXPLORATION:
            config.vital_needs_active = True
            config.health_injury_active = True
            config.mental_state_active = False
            config.emotional_balance_active = False
            config.shelter_comfort_active = True
            config.resources_economy_active = True
            
        return config
