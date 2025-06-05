"""
Game Context - Contextual information for text parsing

This module provides the GameContext class that holds information about the current
game state to assist with parsing and resolving player commands.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class GameContext:
    """
    Context information for the current game state.
    Provides all necessary details for the parser to correctly interpret commands.
    """
    # Core player information
    player_id: str
    character_name: Optional[str] = None
    
    # Location information
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    location_type: Optional[str] = None
    region_id: Optional[str] = None
    
    # Current interaction targets
    current_npc_id: Optional[str] = None
    current_npc_name: Optional[str] = None
    current_shop_id: Optional[str] = None
    current_shop_name: Optional[str] = None
    
    # Economic context
    current_business_id: Optional[str] = None  # Player's current business focus
    current_building_id: Optional[str] = None  # Player's current building focus
    market_region_id: Optional[str] = None     # Current market region
    
    # Player-owned entities
    owned_businesses: List[Dict[str, Any]] = field(default_factory=list)
    owned_buildings: List[Dict[str, Any]] = field(default_factory=list)
    owned_properties: List[Dict[str, Any]] = field(default_factory=list)
    
    # Skill and proficiency information
    known_crafting_professions: List[str] = field(default_factory=list)
    crafting_skill_levels: Dict[str, int] = field(default_factory=dict)
    known_recipes: List[str] = field(default_factory=list)
    
    # Economic status
    currency_balance: Optional[float] = None
    inventory_value: Optional[float] = None
    
    # UI/Interaction state
    inventory_open: bool = False
    crafting_open: bool = False
    shopping_open: bool = False
    business_menu_open: bool = False
    building_menu_open: bool = False
    in_black_market: bool = False
    in_conversation: bool = False
    
    # Additional context flags
    is_in_combat: bool = False
    is_sneaking: bool = False
    has_disguise: bool = False
    notoriety_level: Optional[float] = None  # For illegal activities
    
    # Temporary context for current command chain
    last_command_type: Optional[str] = None
    last_mentioned_items: List[str] = field(default_factory=list)
    last_mentioned_npcs: List[str] = field(default_factory=list)
    disambiguation_options: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_from_player_data(self, player_data: Dict[str, Any]) -> None:
        """
        Update context from player data retrieved from game services.
        
        Args:
            player_data: Dictionary of player information
        """
        if "id" in player_data:
            self.player_id = player_data["id"]
        
        if "name" in player_data:
            self.character_name = player_data["name"]
        
        if "location" in player_data:
            self.location_id = player_data["location"].get("id")
            self.location_name = player_data["location"].get("name")
            self.location_type = player_data["location"].get("type")
            self.region_id = player_data["location"].get("region_id")
        
        if "currency" in player_data:
            self.currency_balance = player_data["currency"]
        
        if "businesses" in player_data:
            self.owned_businesses = player_data["businesses"]
            
        if "buildings" in player_data:
            self.owned_buildings = player_data["buildings"]
            
        if "properties" in player_data:
            self.owned_properties = player_data["properties"]
            
        if "crafting" in player_data:
            crafting_data = player_data["crafting"]
            self.known_crafting_professions = crafting_data.get("professions", [])
            self.crafting_skill_levels = crafting_data.get("skill_levels", {})
            self.known_recipes = crafting_data.get("known_recipes", [])
            
        if "criminal" in player_data:
            self.notoriety_level = player_data["criminal"].get("notoriety", 0.0)
            
    def get_focused_business(self) -> Optional[Dict[str, Any]]:
        """Get the business that is currently in focus."""
        if not self.current_business_id:
            return None
            
        for business in self.owned_businesses:
            if business.get("id") == self.current_business_id:
                return business
                
        return None
        
    def get_focused_building(self) -> Optional[Dict[str, Any]]:
        """Get the building that is currently in focus."""
        if not self.current_building_id:
            return None
            
        for building in self.owned_buildings:
            if building.get("id") == self.current_building_id:
                return building
                
        return None
        
    def is_in_owned_business(self) -> bool:
        """Check if the player is currently in one of their own businesses."""
        if not self.location_id:
            return False
            
        for business in self.owned_businesses:
            if business.get("location_id") == self.location_id:
                return True
                
        return False
        
    def is_in_owned_building(self) -> bool:
        """Check if the player is currently in one of their own buildings."""
        if not self.location_id:
            return False
            
        for building in self.owned_buildings:
            if building.get("location_id") == self.location_id:
                return True
                
        return False
        
    def get_businesses_in_current_location(self) -> List[Dict[str, Any]]:
        """Get all player-owned businesses in the current location."""
        if not self.location_id:
            return []
            
        return [
            business for business in self.owned_businesses
            if business.get("location_id") == self.location_id
        ]
        
    def get_buildings_in_current_location(self) -> List[Dict[str, Any]]:
        """Get all player-owned buildings in the current location."""
        if not self.location_id:
            return []
            
        return [
            building for building in self.owned_buildings
            if building.get("location_id") == self.location_id
        ]
        
    def clear_interaction_state(self) -> None:
        """Clear all interaction state flags."""
        self.inventory_open = False
        self.crafting_open = False
        self.shopping_open = False
        self.business_menu_open = False
        self.building_menu_open = False
        self.in_conversation = False
        
    def clear_disambiguation(self) -> None:
        """Clear disambiguation options."""
        self.disambiguation_options = []

# Create a global game context instance for use throughout the system
game_context = GameContext(player_id="default_player")