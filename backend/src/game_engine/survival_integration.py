"""
Integration module to connect the Survival System with the main Game Engine.
"""
from typing import Dict, List, Optional, Any
import uuid

from ..shared.survival_models import (
    SurvivalState, 
    SurvivalStateUpdate,
    CampaignSurvivalConfig,
    CampaignType
)
from ..game_engine.survival_system import SurvivalSystem
from ..storage.survival_storage import SurvivalStorage
from ..narrative_engine.survival_integration import SurvivalNarrativeIntegration


class SurvivalIntegration:
    """Integrates the survival system with the game engine"""
    
    def __init__(self, game_engine=None):
        """Initialize the integration
        
        Args:
            game_engine: The game engine to integrate with
        """
        self.game_engine = game_engine
        self.storage = SurvivalStorage()
        self.survival_system = SurvivalSystem(storage=self.storage)
        self.narrative_integration = SurvivalNarrativeIntegration(survival_system=self.survival_system)
    
    def initialize(self):
        """Initialize the integration with the game engine"""
        if not self.game_engine:
            return
            
        # Store reference to the survival system
        self.game_engine.survival_system = self.survival_system
        
        # Register survival tags with the game engine
        self._register_survival_tags()
        
        print("Survival system integrated with game engine")
    
    def _register_survival_tags(self):
        """Register survival-related tags with the game engine"""
        if not self.game_engine or not hasattr(self.game_engine, "standard_tags"):
            return
            
        # Add survival-related tags to the standard tags
        from ..shared.models import Tag, TagCategory, DomainType
        
        # Foraging tag
        self.game_engine.standard_tags["foraging"] = Tag(
            name="Foraging",
            category=TagCategory.SURVIVAL,
            description="Finding food and resources in the wild",
            domains=[DomainType.AWARENESS, DomainType.MIND]
        )
        
        # Shelter tag
        self.game_engine.standard_tags["shelter"] = Tag(
            name="Shelter",
            category=TagCategory.SURVIVAL,
            description="Building and finding shelter",
            domains=[DomainType.CRAFT, DomainType.BODY]
        )
        
        # First aid tag
        self.game_engine.standard_tags["first_aid"] = Tag(
            name="First Aid",
            category=TagCategory.SURVIVAL,
            description="Treating injuries and illness",
            domains=[DomainType.MIND, DomainType.CRAFT]
        )
        
        # Navigation tag
        self.game_engine.standard_tags["navigation"] = Tag(
            name="Navigation",
            category=TagCategory.SURVIVAL,
            description="Finding your way in the wilderness",
            domains=[DomainType.AWARENESS, DomainType.MIND]
        )
        
        # Hunting tag
        self.game_engine.standard_tags["hunting"] = Tag(
            name="Hunting",
            category=TagCategory.SURVIVAL,
            description="Tracking and hunting animals for food",
            domains=[DomainType.AWARENESS, DomainType.BODY]
        )
        
        print("Survival tags registered with game engine")
    
    def initialize_character_survival(self, character_id: str, base_health: Optional[int] = None) -> SurvivalState:
        """Initialize survival state for a new character
        
        Args:
            character_id: ID of the character
            base_health: Optional base health value from character creation
            
        Returns:
            Newly created survival state
        """
        state = self.survival_system.create_survival_state(character_id)
        
        # Initialize max health based on character's Body domain if available
        if self.game_engine and hasattr(self.game_engine, "get_character"):
            character = self.game_engine.get_character(character_id)
            if character:
                # Extract base health from character if available and not explicitly provided
                if base_health is None and hasattr(character, "base_health"):
                    base_health = character.base_health
                    
                # Update max health based on Body domain level and base health
                self.update_max_health_from_character(character_id, character, base_health)
                
        # If base health was provided but character wasn't found or didn't have Body domain
        # Update the max health directly
        elif base_health is not None:
            # Set a default level of 1 if no character data available
            body_level = 1
            state.update_max_health_from_domain(body_level, base_health)
                
        return state
        
    def update_max_health_from_character(self, character_id: str, character=None, base_health: Optional[int] = None) -> Optional[SurvivalState]:
        """Update max health based on character's Body domain level
        
        Args:
            character_id: ID of the character
            character: Character data (optional, will be fetched if not provided)
            base_health: Optional base health value from character creation
            
        Returns:
            Updated survival state or None if character not found
        """
        if not self.game_engine:
            return None
            
        # Get character data if not provided
        if not character and hasattr(self.game_engine, "get_character"):
            character = self.game_engine.get_character(character_id)
            
        if not character:
            return None
            
        # Get current survival state
        state = self.survival_system.get_survival_state(character_id)
        if not state:
            return None
            
        # Get Body domain level
        from ..shared.models import DomainType
        body_level = 1  # Default if no body domain found
        
        if hasattr(character, "domains") and character.domains:
            body_domain = next((d for d in character.domains if d.type == DomainType.BODY), None)
            if body_domain:
                body_level = body_domain.level
        
        # Extract base health from character if available and not explicitly provided
        if base_health is None and hasattr(character, "base_health"):
            base_health = character.base_health
            
        # Update max health using SurvivalState's method which now handles base health
        state.update_max_health_from_domain(body_level, base_health)
        return state
    
    def initialize_campaign_survival(self, campaign_id: str, campaign_type: str) -> CampaignSurvivalConfig:
        """Initialize survival configuration for a new campaign
        
        Args:
            campaign_id: ID of the campaign
            campaign_type: Type of campaign
            
        Returns:
            Newly created campaign survival configuration
        """
        # Convert string to enum
        try:
            campaign_type_enum = CampaignType(campaign_type)
        except ValueError:
            # Default to survival if invalid type
            campaign_type_enum = CampaignType.SURVIVAL
            
        return self.survival_system.create_campaign_config(campaign_id, campaign_type_enum)
    
    def process_game_action(self, game_action: Dict[str, Any], character_id: str) -> Dict[str, Any]:
        """Process a game action and update survival state accordingly
        
        Args:
            game_action: The game action data
            character_id: ID of the character
            
        Returns:
            Updated game action with survival effects
        """
        # Check for character progression events (level up, domain increase) and update max health
        self._check_character_progression(game_action, character_id)
        
        # Map game action types to survival action types
        action_mapping = {
            "move": "explore",
            "attack": "fight",
            "defend": "fight",
            "rest": "rest",
            "search": "forage",
            "craft": "craft",
            "talk": "socialize",
            "trade": "socialize",
            "eat": "rest",
            "drink": "rest",
            "sleep": "rest"
        }
        
        # Get the survival action type
        action_type = action_mapping.get(game_action.get("type", ""), "explore")
        
        # Get the environment from the game action
        environment = game_action.get("environment", "normal")
        
        # Process the action
        state, events = self.survival_system.process_action(character_id, action_type, environment)
        
        # Add survival events to the game action
        if "survival" not in game_action:
            game_action["survival"] = {}
            
        game_action["survival"]["events"] = events
        game_action["survival"]["state"] = state.model_dump()
        
        # Generate narrative hooks
        narrative = self.narrative_integration.generate_survival_narrative(character_id)
        if narrative:
            game_action["survival"]["narrative"] = narrative
            
        # Check for critical effects
        critical_effect = self.narrative_integration.get_critical_state_effect(character_id)
        if critical_effect:
            game_action["survival"]["critical_effect"] = critical_effect
            
        return game_action
        
    def _check_character_progression(self, game_action: Dict[str, Any], character_id: str) -> None:
        """Check if a game action resulted in character progression and update max health if needed
        
        Args:
            game_action: The game action data
            character_id: ID of the character
        """
        # Check for level up or domain increase events
        progression_events = [
            "level_up", "domain_increase", "skill_increase", "attribute_gain", 
            "stats_changed", "character_updated"
        ]
        
        # Determine if this action contains a progression event
        contains_progression = False
        
        # Check action type
        if game_action.get("type") in progression_events:
            contains_progression = True
            
        # Check for events list
        if "events" in game_action:
            for event in game_action["events"]:
                event_type = event.get("type") if isinstance(event, dict) else event
                if event_type in progression_events:
                    contains_progression = True
                    break
                    
        # If progression detected, update max health from character
        if contains_progression and self.game_engine:
            self.update_max_health_from_character(character_id)
    
    def enhance_narrative(self, narrative_context: Dict[str, Any], character_id: str) -> Dict[str, Any]:
        """Enhance narrative context with survival information
        
        Args:
            narrative_context: Existing narrative context
            character_id: ID of the character
            
        Returns:
            Enhanced narrative context
        """
        return self.narrative_integration.enhance_narrative_context(narrative_context, character_id)
