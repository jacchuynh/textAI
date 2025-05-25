"""
Black Market API

This module provides a unified API for the black market and illicit business operations system.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.business.services.black_market_operations_service import BlackMarketOperationsService
from backend.src.business.services.illicit_business_activities_service import IllicitBusinessActivitiesService
from backend.src.business.services.authority_consequence_service import AuthorityConsequenceService
from backend.src.business.models.illicit_models import (
    IllicitItemCategory, IllicitServiceType, SecurityMeasure
)

logger = logging.getLogger(__name__)

class BlackMarketAPI:
    """
    Provides a unified API for all black market and illicit business operations.
    This class serves as the main entry point for interacting with the black market system.
    """
    
    def __init__(self):
        """Initialize the black market API."""
        self.black_market_service = BlackMarketOperationsService()
        self.illicit_business_service = IllicitBusinessActivitiesService()
        self.authority_service = AuthorityConsequenceService()
        self.logger = logging.getLogger("BlackMarketAPI")
    
    # === BLACK MARKET OPERATIONS ===
    
    def find_black_market_contact(
        self,
        db: Session,
        player_id: str,
        location_id: str,
        desired_service_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find a black market contact in a location.
        
        Args:
            db: Database session
            player_id: ID of the player
            location_id: ID of the location
            desired_service_type: Optional type of service needed
            
        Returns:
            Dictionary with contact information or failure details
        """
        return self.black_market_service.find_black_market_contact(
            db, player_id, location_id, desired_service_type
        )
    
    def initiate_illicit_trade(
        self,
        db: Session,
        player_id: str,
        contact_npc_id: str,
        item_to_buy_or_sell: Dict[str, Any],
        quantity: int,
        is_buying: bool = True,
        location_id: Optional[str] = None,
        business_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an illicit trade with a black market contact.
        
        Args:
            db: Database session
            player_id: ID of the player
            contact_npc_id: ID of the contact NPC
            item_to_buy_or_sell: Item data
            quantity: Quantity to trade
            is_buying: Whether the player is buying (True) or selling (False)
            location_id: Optional location ID (required if not using business)
            business_id: Optional business ID (if trading through a business)
            
        Returns:
            Dictionary with trade results
        """
        return self.black_market_service.initiate_illicit_trade(
            db, player_id, contact_npc_id, item_to_buy_or_sell, quantity,
            is_buying, location_id, business_id
        )
    
    def manage_underworld_reputation(
        self,
        db: Session,
        player_id: str,
        faction_id: str,
        reputation_change: float,
        action_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Manage a player's reputation with an underworld faction.
        
        Args:
            db: Database session
            player_id: ID of the player
            faction_id: ID of the faction
            reputation_change: Change in reputation (-1.0 to 1.0)
            action_description: Optional description of the action
            
        Returns:
            Dictionary with updated reputation details
        """
        return self.black_market_service.manage_underworld_reputation(
            db, player_id, faction_id, reputation_change, action_description
        )
    
    def get_regional_heat_level(
        self,
        db: Session,
        location_id: str
    ) -> Dict[str, Any]:
        """
        Get the current heat level for a region.
        
        Args:
            db: Database session
            location_id: ID of the location
            
        Returns:
            Dictionary with heat level details
        """
        return self.black_market_service.get_regional_heat_level(db, location_id)
    
    def plan_smuggling_operation(
        self,
        db: Session,
        player_id: str,
        details: Dict[str, Any],
        business_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Plan a smuggling operation.
        
        Args:
            db: Database session
            player_id: ID of the player
            details: Dictionary with operation details
            business_id: Optional business ID
            
        Returns:
            Dictionary with the planned operation
        """
        return self.black_market_service.plan_smuggling_operation(
            db, player_id, details, business_id
        )
    
    def execute_smuggling_operation(
        self,
        db: Session,
        operation_id: str,
        player_id: str
    ) -> Dict[str, Any]:
        """
        Execute a planned smuggling operation.
        
        Args:
            db: Database session
            operation_id: ID of the operation
            player_id: ID of the player
            
        Returns:
            Dictionary with operation results
        """
        return self.black_market_service.execute_smuggling_operation(
            db, operation_id, player_id
        )
    
    def discover_hidden_location(
        self,
        db: Session,
        player_id: str,
        region_id: str,
        search_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Attempt to discover a hidden location for black market activities.
        
        Args:
            db: Database session
            player_id: ID of the player
            region_id: ID of the region
            search_parameters: Optional parameters to guide the search
            
        Returns:
            Dictionary with discovery results
        """
        return self.black_market_service.discover_hidden_location(
            db, player_id, region_id, search_parameters
        )
    
    # === ILLICIT BUSINESS OPERATIONS ===
    
    def toggle_illicit_operation_mode(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        is_active: bool
    ) -> Dict[str, Any]:
        """
        Toggle a business's illicit operation mode.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            is_active: Whether illicit operations should be active
            
        Returns:
            Dictionary with toggle results
        """
        return self.illicit_business_service.toggle_illicit_operation_mode(
            db, player_id, business_id, is_active
        )
    
    def add_security_measure(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        security_measure: str,
        cost: float
    ) -> Dict[str, Any]:
        """
        Add a security measure to a business's illicit operations.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            security_measure: Security measure to add
            cost: Cost of the security measure
            
        Returns:
            Dictionary with security measure addition results
        """
        return self.illicit_business_service.add_security_measure(
            db, player_id, business_id, security_measure, cost
        )
    
    def craft_illicit_item(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        item_recipe_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Craft an illicit item in a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            item_recipe_id: ID of the item recipe
            quantity: Quantity to craft
            
        Returns:
            Dictionary with crafting results
        """
        return self.illicit_business_service.craft_illicit_item(
            db, player_id, business_id, item_recipe_id, quantity
        )
    
    def launder_money(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        amount_to_launder: float
    ) -> Dict[str, Any]:
        """
        Launder illicit money through a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            amount_to_launder: Amount of money to launder
            
        Returns:
            Dictionary with laundering results
        """
        return self.illicit_business_service.launder_money(
            db, player_id, business_id, amount_to_launder
        )
    
    def add_illicit_item_to_inventory(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add an illicit item to a business's hidden inventory.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            item_data: Data for the illicit item
            
        Returns:
            Dictionary with item addition results
        """
        return self.illicit_business_service.add_illicit_item_to_inventory(
            db, player_id, business_id, item_data
        )
    
    def get_illicit_inventory(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a business's illicit inventory.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            category_filter: Optional category to filter items
            
        Returns:
            Dictionary with illicit inventory
        """
        return self.illicit_business_service.get_illicit_inventory(
            db, player_id, business_id, category_filter
        )
    
    def sell_illicit_item(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        item_id: str,
        quantity: int,
        buyer_id: Optional[str] = None,
        custom_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sell an illicit item from a business's hidden inventory.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            item_id: ID of the item to sell
            quantity: Quantity to sell
            buyer_id: Optional ID of the buyer (NPC or player)
            custom_price: Optional custom price
            
        Returns:
            Dictionary with sale results
        """
        return self.illicit_business_service.sell_illicit_item(
            db, player_id, business_id, item_id, quantity, buyer_id, custom_price
        )
    
    def offer_illicit_service(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        service_type: str,
        service_details: Dict[str, Any],
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Offer an illicit service through a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            service_type: Type of service
            service_details: Details of the service
            customer_id: Optional ID of the customer
            
        Returns:
            Dictionary with service results
        """
        return self.illicit_business_service.offer_illicit_service(
            db, player_id, business_id, service_type, service_details, customer_id
        )
    
    def handle_illicit_custom_order(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        order_id: str,
        action: str,
        action_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an illicit custom order.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            order_id: ID of the order
            action: Action to take (accept, reject, complete, etc.)
            action_details: Optional action details
            
        Returns:
            Dictionary with action results
        """
        return self.illicit_business_service.handle_illicit_custom_order(
            db, player_id, business_id, order_id, action, action_details
        )
    
    # === AUTHORITY & CONSEQUENCES ===
    
    def calculate_detection_risk(
        self,
        db: Session,
        player_id: str,
        location_id: str,
        action_details: Dict[str, Any]
    ) -> float:
        """
        Calculate the risk of detection for an illicit action.
        
        Args:
            db: Database session
            player_id: ID of the player
            location_id: ID of the location
            action_details: Details of the action
            
        Returns:
            Detection risk as a float (0.0-1.0)
        """
        return self.authority_service.calculate_detection_risk(
            db, player_id, location_id, action_details
        )
    
    def trigger_investigation(
        self,
        db: Session,
        location_id: str,
        target_id: str,
        target_type: str,
        suspicion_cause: str,
        initial_evidence_level: float = 0.1
    ) -> Dict[str, Any]:
        """
        Trigger a new authority investigation.
        
        Args:
            db: Database session
            location_id: ID of the location
            target_id: ID of the target (player, business, or location)
            target_type: Type of the target ("player", "business", "location")
            suspicion_cause: Cause of suspicion
            initial_evidence_level: Initial evidence level (0.0-1.0)
            
        Returns:
            Dictionary with investigation details
        """
        return self.authority_service.trigger_investigation(
            db, location_id, target_id, target_type, suspicion_cause, initial_evidence_level
        )
    
    def update_investigation(
        self,
        db: Session,
        investigation_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing investigation.
        
        Args:
            db: Database session
            investigation_id: ID of the investigation
            updates: Updates to apply
            
        Returns:
            Dictionary with updated investigation details
        """
        return self.authority_service.update_investigation(
            db, investigation_id, updates
        )
    
    def simulate_patrol_encounter(
        self,
        db: Session,
        player_id: str,
        location_id: str,
        encounter_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate an encounter with a patrol in a location.
        
        Args:
            db: Database session
            player_id: ID of the player
            location_id: ID of the location
            encounter_context: Optional context for the encounter
            
        Returns:
            Dictionary with encounter results
        """
        return self.authority_service.simulate_patrol_encounter(
            db, player_id, location_id, encounter_context
        )
    
    def apply_penalty_for_crime(
        self,
        db: Session,
        player_id: str,
        crime_details: Dict[str, Any],
        severity_level: str
    ) -> Dict[str, Any]:
        """
        Apply a penalty for a committed crime.
        
        Args:
            db: Database session
            player_id: ID of the player
            crime_details: Details of the crime
            severity_level: Severity level ("minor", "moderate", "severe")
            
        Returns:
            Dictionary with penalty application results
        """
        return self.authority_service.apply_penalty_for_crime(
            db, player_id, crime_details, severity_level
        )
    
    def schedule_patrol(
        self,
        db: Session,
        location_id: str,
        patrol_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a patrol in a location.
        
        Args:
            db: Database session
            location_id: ID of the location
            patrol_details: Optional patrol details
            
        Returns:
            Dictionary with patrol scheduling results
        """
        return self.authority_service.schedule_patrol(
            db, location_id, patrol_details
        )