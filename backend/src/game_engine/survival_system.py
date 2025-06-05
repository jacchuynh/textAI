import random
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta

from ..shared.survival_models import (
    SurvivalState,
    SurvivalStateUpdate,
    CampaignSurvivalConfig,
    CampaignType,
    SurvivalModuleType,
    MoodState,
    ShelterQuality
)


class SurvivalSystem:
    """Core survival system that handles survival mechanics and state transitions"""

    def __init__(self, storage=None):
        """Initialize the survival system
        
        Args:
            storage: Storage service for persistence
        """
        self.storage = storage
        self.survival_states: Dict[str, SurvivalState] = {}
        self.campaign_configs: Dict[str, CampaignSurvivalConfig] = {}
        
        # Default rate of change per hour for various stats
        self.default_hourly_rates = {
            "hunger": -5,        # Lose 5 hunger points per hour
            "thirst": -8,        # Lose 8 thirst points per hour
            "fatigue": 4,        # Gain 4 fatigue points per hour of activity
            "rest_recovery": 15, # Recover 15 fatigue points per hour of rest
            "morale": -2,        # Slowly lose morale over time
            "clarity": -1,       # Slowly lose clarity over time
        }
        
        # Special events that can affect survival stats
        self.random_events = {
            "vital_needs": [
                {"name": "Found fresh water", "thirst": 30, "probability": 0.05},
                {"name": "Found berries", "hunger": 15, "probability": 0.08},
                {"name": "Stomach illness", "hunger": -20, "current_health": -10, "probability": 0.03}
            ],
            "mental_state": [
                {"name": "Inspiring sight", "morale": 15, "probability": 0.05},
                {"name": "Disturbing vision", "clarity": -15, "morale": -10, "probability": 0.04},
                {"name": "Moment of insight", "clarity": 20, "probability": 0.03}
            ],
            "emotional_balance": [
                {"name": "Homesickness", "mood": MoodState.CONCERNED, "probability": 0.07},
                {"name": "Comforting memory", "mood": MoodState.CONTENT, "probability": 0.06},
                {"name": "Sense of achievement", "mood": MoodState.HAPPY, "probability": 0.05}
            ]
        }
    
    def create_survival_state(self, character_id: str, base_health: Optional[int] = None, body_value: Optional[int] = None) -> SurvivalState:
        """Create a new survival state for a character
        
        Args:
            character_id: ID of the character
            base_health: Optional base health value from character creation
            body_value: Optional Body domain value to use for health scaling
            
        Returns:
            Newly created survival state
        """
        # Create initial state with default values
        survival_state = SurvivalState(character_id=character_id)
        
        # Apply custom base health if provided
        if base_health is not None:
            # Update max_health directly if only base_health is provided (no Body value)
            if body_value is None:
                update = SurvivalStateUpdate(max_health=base_health)
                survival_state.update_state(update)
            else:
                # If both base_health and body_value are provided, use the proper scaling
                survival_state.update_max_health_from_domain(body_value, base_health)
        
        # Store in memory cache
        self.survival_states[character_id] = survival_state
        
        # Save to storage if available
        if self.storage:
            self.storage.save_survival_state(survival_state)
            
        return survival_state
    
    def create_campaign_config(self, campaign_id: str, campaign_type: CampaignType) -> CampaignSurvivalConfig:
        """Create a new campaign configuration with appropriate survival settings"""
        config = CampaignSurvivalConfig.create_for_campaign_type(campaign_id, campaign_type)
        self.campaign_configs[campaign_id] = config
        
        # Save to storage if available
        if self.storage:
            self.storage.save_campaign_config(config)
            
        return config
    
    def get_survival_state(self, character_id: str) -> Optional[SurvivalState]:
        """Get a character's survival state"""
        if character_id in self.survival_states:
            return self.survival_states[character_id]
        
        # Try to load from storage
        if self.storage:
            state = self.storage.load_survival_state(character_id)
            if state:
                self.survival_states[character_id] = state
                return state
                
        return None
    
    def get_campaign_config(self, campaign_id: str) -> Optional[CampaignSurvivalConfig]:
        """Get a campaign's survival configuration"""
        if campaign_id in self.campaign_configs:
            return self.campaign_configs[campaign_id]
        
        # Try to load from storage
        if self.storage:
            config = self.storage.load_campaign_config(campaign_id)
            if config:
                self.campaign_configs[campaign_id] = config
                return config
                
        return None
    
    def update_survival_state(self, character_id: str, update: SurvivalStateUpdate) -> SurvivalState:
        """Update a character's survival state with specific changes"""
        state = self.get_survival_state(character_id)
        if not state:
            state = self.create_survival_state(character_id)
            
        state.update_state(update)
        
        # Save changes
        if self.storage:
            self.storage.save_survival_state(state)
            
        return state
    
    def process_time_passage(self, character_id: str, hours: float, activity_level: str = "normal") -> Tuple[SurvivalState, List[str]]:
        """Process the passage of time and its effects on survival state
        
        Args:
            character_id: ID of the character
            hours: Number of hours that have passed
            activity_level: Level of activity (rest, low, normal, high, extreme)
            
        Returns:
            Updated survival state and list of notable events
        """
        state = self.get_survival_state(character_id)
        if not state:
            state = self.create_survival_state(character_id)
            
        events = []
        
        # Calculate activity multipliers
        activity_multipliers = {
            "rest": 0.2,     # Minimal exertion during rest
            "low": 0.5,      # Light activity
            "normal": 1.0,   # Normal activity
            "high": 1.5,     # Strenuous activity
            "extreme": 2.0   # Maximum exertion
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.0)
        
        # Apply time-based changes
        update = SurvivalStateUpdate()
        
        # Vital needs changes
        if activity_level == "rest":
            # During rest, recover fatigue but still lose hunger/thirst
            update.hunger = self.default_hourly_rates["hunger"] * hours
            update.thirst = self.default_hourly_rates["thirst"] * hours
            update.fatigue = -self.default_hourly_rates["rest_recovery"] * hours
            events.append(f"Rested for {int(hours)} hours, recovering energy.")
        else:
            # Normal activity
            update.hunger = self.default_hourly_rates["hunger"] * hours * multiplier
            update.thirst = self.default_hourly_rates["thirst"] * hours * multiplier
            update.fatigue = self.default_hourly_rates["fatigue"] * hours * multiplier
            
        # Mental/emotional changes based on time
        update.morale = self.default_hourly_rates["morale"] * hours
        update.clarity = self.default_hourly_rates["clarity"] * hours
        
        # Apply the updates
        state.update_state(update)
        
        # Check for critical states and add events
        if state.hunger <= 20:
            events.append("You're now severely hungry and need food urgently.")
        if state.thirst <= 20:
            events.append("You're severely dehydrated and need water immediately.")
        if state.fatigue >= 80:
            events.append("You're completely exhausted and need rest soon.")
        
        # Check health percentage for critical state
        health_percent = state.calculate_health_percentage()
        if health_percent <= 20:
            events.append("You're severely injured and need medical attention urgently.")
        
        # Process random events with appropriate probability scaling for time passage
        random_event_scaling = min(hours / 4, 1.0)  # Cap scaling at 1.0
        self._process_random_events(state, random_event_scaling, events)
        
        # Save changes
        if self.storage:
            self.storage.save_survival_state(state)
            
        return state, events
    
    def _process_random_events(self, state: SurvivalState, probability_scale: float, events: List[str]):
        """Process potential random events that might affect survival state"""
        for category, event_list in self.random_events.items():
            for event in event_list:
                # Scale probability by the time factor
                adjusted_probability = event["probability"] * probability_scale
                
                if random.random() < adjusted_probability:
                    # Event triggered, apply effects
                    update = SurvivalStateUpdate()
                    
                    for key, value in event.items():
                        if key == "name" or key == "probability":
                            continue
                            
                        # Apply the effect
                        if key == "hunger":
                            update.hunger = value
                        elif key == "thirst":
                            update.thirst = value
                        elif key == "fatigue":
                            update.fatigue = value
                        elif key == "current_health":
                            update.current_health = value
                        elif key == "morale":
                            update.morale = value
                        elif key == "clarity":
                            update.clarity = value
                        elif key == "mood":
                            update.mood = value
                        elif key == "shelter_quality":
                            update.shelter_quality = value
                    
                    # Update the state
                    state.update_state(update)
                    
                    # Add to events list
                    events.append(f"Event: {event['name']}")
    
    def process_action(self, character_id: str, action_type: str, environment: str = "normal") -> Tuple[SurvivalState, List[str]]:
        """Process the effects of a character action on their survival state
        
        Args:
            character_id: ID of the character
            action_type: Type of action (explore, fight, rest, forage, etc.)
            environment: Environment type affecting survival (desert, forest, etc.)
            
        Returns:
            Updated survival state and list of notable events
        """
        state = self.get_survival_state(character_id)
        if not state:
            state = self.create_survival_state(character_id)
            
        events = []
        
        # Action effects mapping
        action_effects = {
            "explore": {
                "hunger": -10,
                "thirst": -15,
                "fatigue": 20,
                "clarity": 5,
                "description": "Exploring consumes energy but stimulates the mind."
            },
            "fight": {
                "hunger": -15,
                "thirst": -20,
                "fatigue": 30,
                "current_health": -10,
                "description": "Combat is physically demanding and potentially injurious."
            },
            "rest": {
                "fatigue": -30,
                "clarity": 10,
                "morale": 5,
                "description": "Resting recovers energy and clears the mind."
            },
            "forage": {
                "hunger": 25,
                "thirst": 10,
                "fatigue": 15,
                "description": "Foraging provides food and water but takes energy."
            },
            "craft": {
                "fatigue": 10,
                "clarity": -5,
                "description": "Crafting requires focus and some physical effort."
            },
            "socialize": {
                "morale": 15,
                "fatigue": 5,
                "description": "Socializing improves morale but takes some energy."
            }
        }
        
        # Environment modifiers
        environment_modifiers = {
            "desert": {
                "thirst": 2.0,  # Thirst depletes twice as fast
                "fatigue": 1.5  # Fatigue increases 50% faster
            },
            "arctic": {
                "hunger": 1.5,  # Hunger depletes 50% faster
                "current_health": 0.8   # Health preservation (insulated)
            },
            "forest": {
                "hunger": 0.7,  # Hunger depletes 30% slower (food available)
                "thirst": 0.8   # Thirst depletes 20% slower (water available)
            },
            "mountains": {
                "fatigue": 2.0,  # Fatigue increases twice as fast
                "clarity": 1.3   # Clarity 30% better (clear mountain air)
            },
            "urban": {
                "hunger": 0.5,   # Hunger depletes 50% slower (food available)
                "thirst": 0.5    # Thirst depletes 50% slower (water available)
            },
            "normal": {
                # No modifiers for normal environment
            }
        }
        
        # Get action effects or use defaults
        effects = action_effects.get(action_type, {
            "fatigue": 5,
            "description": "This action has minimal impact on survival."
        })
        
        # Get environment modifiers
        env_mod = environment_modifiers.get(environment, {})
        
        # Apply effects with environment modifiers
        update = SurvivalStateUpdate()
        
        if "hunger" in effects:
            modifier = env_mod.get("hunger", 1.0)
            update.hunger = effects["hunger"] * modifier
            
        if "thirst" in effects:
            modifier = env_mod.get("thirst", 1.0)
            update.thirst = effects["thirst"] * modifier
            
        if "fatigue" in effects:
            modifier = env_mod.get("fatigue", 1.0)
            update.fatigue = effects["fatigue"] * modifier
            
        if "current_health" in effects:
            modifier = env_mod.get("current_health", 1.0)
            update.current_health = effects["current_health"] * modifier
            
        if "morale" in effects:
            modifier = env_mod.get("morale", 1.0)
            update.morale = effects["morale"] * modifier
            
        if "clarity" in effects:
            modifier = env_mod.get("clarity", 1.0)
            update.clarity = effects["clarity"] * modifier
            
        # Add description to events
        if "description" in effects:
            events.append(effects["description"])
            
        # Apply the updates
        state.update_state(update)
        
        # Process potential random events
        self._process_random_events(state, 0.5, events)
        
        # Save changes
        if self.storage:
            self.storage.save_survival_state(state)
            
        return state, events
    
    def consume_item(self, character_id: str, item_name: str, quantity: int = 1) -> Tuple[SurvivalState, List[str]]:
        """Process the effects of consuming an item on survival state
        
        Args:
            character_id: ID of the character
            item_name: Name of the item to consume
            quantity: Number of items to consume
            
        Returns:
            Updated survival state and list of notable events
        """
        state = self.get_survival_state(character_id)
        if not state:
            state = self.create_survival_state(character_id)
            
        events = []
        
        # Check if the item exists in inventory
        if item_name not in state.inventory or state.inventory[item_name] < quantity:
            events.append(f"You don't have enough {item_name} to consume.")
            return state, events
            
        # Item effects mapping
        item_effects = {
            "water": {
                "thirst": 30,
                "description": "You drink water, quenching your thirst."
            },
            "ration": {
                "hunger": 25,
                "description": "You eat a ration, satisfying your hunger."
            },
            "bread": {
                "hunger": 15,
                "morale": 5,
                "description": "You eat bread, partially satisfying your hunger."
            },
            "meat": {
                "hunger": 40,
                "current_health": 5,
                "description": "You eat meat, substantially satisfying your hunger."
            },
            "fruit": {
                "hunger": 10,
                "thirst": 5,
                "current_health": 3,
                "description": "You eat fruit, getting some nutrition and hydration."
            },
            "vegetable": {
                "hunger": 10,
                "current_health": 5,
                "description": "You eat vegetables, getting some nutrition and vitamins."
            },
            "healing_potion": {
                "current_health": 40,
                "description": "You drink a healing potion, restoring your health."
            },
            "energy_drink": {
                "fatigue": -20,
                "clarity": 15,
                "description": "You drink an energy drink, feeling more alert and energetic."
            },
            "tea": {
                "thirst": 15,
                "morale": 10,
                "clarity": 5,
                "description": "You drink tea, feeling refreshed and a bit more focused."
            },
            "alcohol": {
                "thirst": 5,
                "morale": 15,
                "clarity": -10,
                "description": "You drink alcohol, feeling happier but less clear-headed."
            }
        }
        
        # Get item effects or use defaults
        effects = item_effects.get(item_name, {
            "description": f"You consume {item_name}, but it has no notable effect."
        })
        
        # Apply effects
        update = SurvivalStateUpdate()
        
        for key, value in effects.items():
            if key == "description":
                continue
                
            # Apply the effect multiplied by quantity
            if key == "hunger":
                update.hunger = value * quantity
            elif key == "thirst":
                update.thirst = value * quantity
            elif key == "fatigue":
                update.fatigue = value * quantity
            elif key == "current_health":
                update.current_health = value * quantity
            elif key == "morale":
                update.morale = value * quantity
            elif key == "clarity":
                update.clarity = value * quantity
        
        # Update inventory (consume the item)
        if update.inventory_updates is None:
            update.inventory_updates = {}
        update.inventory_updates[item_name] = -quantity
        
        # Add description to events
        if "description" in effects:
            if quantity > 1:
                events.append(f"{effects['description']} (x{quantity})")
            else:
                events.append(effects["description"])
            
        # Apply the updates
        state.update_state(update)
        
        # Save changes
        if self.storage:
            self.storage.save_survival_state(state)
            
        return state, events
    
    def get_narrative_context(self, character_id: str) -> Dict[str, Any]:
        """Get narrative context data for integration with narrative engine
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary of narrative context data
        """
        state = self.get_survival_state(character_id)
        if not state:
            return {}
            
        # Get status descriptions
        status = state.get_survival_status()
        
        # Get survival tags for AI prompt
        tags = state.get_survival_tags()
        
        # Construct context object
        context = {
            "survival_state": {
                "hunger": state.hunger,
                "thirst": state.thirst,
                "fatigue": state.fatigue,
                "current_health": state.current_health,
                "max_health": state.max_health,
                "health_percent": state.calculate_health_percentage(),
                "morale": state.morale,
                "clarity": state.clarity,
                "mood": state.mood,
                "shelter_quality": state.shelter_quality
            },
            "survival_status": status,
            "survival_tags": tags,
            "critical_needs": []
        }
        
        # Add critical needs if any
        if state.hunger <= 30:
            context["critical_needs"].append("food")
        if state.thirst <= 30:
            context["critical_needs"].append("water")
        if state.fatigue >= 70:
            context["critical_needs"].append("rest")
        health_percent = state.calculate_health_percentage()
        if health_percent <= 30:
            context["critical_needs"].append("medical")
        
        return context
