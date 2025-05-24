"""
Business System API

This module provides a high-level API for interacting with the business system,
acting as a façade for the underlying services and integrations.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, BusinessFoundingRequest, CustomOrderRequest,
    BusinessType, CustomOrderStatus, TransactionType, StaffRole
)
from backend.src.business.services.player_business_founding_service import PlayerBusinessFoundingService
from backend.src.business.services.player_business_daily_operations_service import PlayerBusinessDailyOperationsService
from backend.src.business.services.business_development_service import BusinessDevelopmentService
from backend.src.business.integrations.system_integrations import BusinessSystemIntegrations
from backend.src.business.crud import (
    get_business, get_businesses_by_player, get_all_businesses,
    create_business, update_business, delete_business
)

logger = logging.getLogger(__name__)

class BusinessAPI:
    """
    Provides a unified API for all business-related functionality.
    This class serves as the main entry point for interacting with the business system.
    """
    
    def __init__(self):
        """Initialize the business API."""
        self.founding_service = PlayerBusinessFoundingService()
        self.daily_operations_service = PlayerBusinessDailyOperationsService()
        self.development_service = BusinessDevelopmentService()
        self.system_integrations = BusinessSystemIntegrations()
        self.logger = logging.getLogger("BusinessAPI")
    
    # === BUSINESS MANAGEMENT ===
    
    def get_business(self, db: Session, business_id: str) -> Optional[PlayerBusinessProfile]:
        """Get a business by ID."""
        return get_business(db, business_id)
    
    def get_player_businesses(self, db: Session, player_id: str) -> List[PlayerBusinessProfile]:
        """Get all businesses owned by a player."""
        return get_businesses_by_player(db, player_id)
    
    def found_business(
        self, 
        db: Session, 
        founding_request: BusinessFoundingRequest
    ) -> PlayerBusinessProfile:
        """
        Found a new business.
        
        Args:
            db: Database session
            founding_request: Business founding request with all required details
            
        Returns:
            Newly created business profile
        """
        return self.founding_service.found_business(db, founding_request)
    
    def close_business(
        self, 
        db: Session, 
        business_id: str, 
        player_id: str,
        closure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Close an existing business.
        
        Args:
            db: Database session
            business_id: ID of the business to close
            player_id: ID of the player (must be owner)
            closure_reason: Optional reason for closure
            
        Returns:
            Dictionary with closure results
        """
        return self.founding_service.close_business(db, business_id, player_id, closure_reason)
    
    def transfer_business_ownership(
        self,
        db: Session,
        business_id: str,
        current_owner_id: str,
        new_owner_id: str,
        transfer_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transfer ownership of a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            current_owner_id: ID of the current owner
            new_owner_id: ID of the new owner
            transfer_terms: Terms of the transfer (price, conditions, etc.)
            
        Returns:
            Dictionary with transfer results
        """
        return self.founding_service.transfer_ownership(
            db, business_id, current_owner_id, new_owner_id, transfer_terms
        )
    
    def get_business_summary(
        self,
        db: Session,
        business_id: str,
        time_period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get a summary of business operations.
        
        Args:
            db: Database session
            business_id: ID of the business
            time_period: Summary period ("daily", "weekly", or "monthly")
            
        Returns:
            Dictionary with business summary data
        """
        return self.daily_operations_service.generate_business_summary(db, business_id, time_period)
    
    def get_business_value_estimation(
        self,
        db: Session,
        business_id: str
    ) -> Dict[str, Any]:
        """
        Calculate an estimated value for a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            
        Returns:
            Dictionary with value estimation details
        """
        return self.daily_operations_service.estimate_business_value(db, business_id)
    
    # === INVENTORY MANAGEMENT ===
    
    def get_business_inventory(
        self,
        db: Session,
        business_id: str,
        category_filter: Optional[str] = None,
        include_out_of_stock: bool = False
    ) -> Dict[str, Any]:
        """
        Get the inventory of a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            category_filter: Optional category to filter items
            include_out_of_stock: Whether to include out-of-stock items
            
        Returns:
            Dictionary with inventory data
        """
        return self.daily_operations_service.get_inventory(
            db, business_id, category_filter, include_out_of_stock
        )
    
    def add_inventory_item(
        self,
        db: Session,
        business_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a new item to business inventory.
        
        Args:
            db: Database session
            business_id: ID of the business
            item_data: Data for the new inventory item
            
        Returns:
            Dictionary with the added item details
        """
        return self.daily_operations_service.add_inventory_item(db, business_id, item_data)
    
    def update_inventory_item(
        self,
        db: Session,
        business_id: str,
        item_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing inventory item.
        
        Args:
            db: Database session
            business_id: ID of the business
            item_id: ID of the item to update
            update_data: Data to update
            
        Returns:
            Dictionary with the updated item details
        """
        return self.daily_operations_service.update_inventory_item(db, business_id, item_id, update_data)
    
    def remove_inventory_item(
        self,
        db: Session,
        business_id: str,
        item_id: str
    ) -> Dict[str, Any]:
        """
        Remove an item from inventory.
        
        Args:
            db: Database session
            business_id: ID of the business
            item_id: ID of the item to remove
            
        Returns:
            Dictionary with removal results
        """
        return self.daily_operations_service.remove_inventory_item(db, business_id, item_id)
    
    def restock_inventory(
        self,
        db: Session,
        business_id: str,
        restock_items: Dict[str, int],
        restock_costs: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Restock multiple inventory items.
        
        Args:
            db: Database session
            business_id: ID of the business
            restock_items: Dictionary of item IDs and quantities to restock
            restock_costs: Optional dictionary of item IDs and their new costs
            
        Returns:
            Dictionary with restock results
        """
        return self.daily_operations_service.restock_inventory(db, business_id, restock_items, restock_costs)
    
    # === FINANCIAL MANAGEMENT ===
    
    def record_transaction(
        self,
        db: Session,
        business_id: str,
        transaction_type: str,
        amount: float,
        description: str,
        related_entity_id: Optional[str] = None,
        transaction_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a financial transaction for a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            transaction_type: Type of transaction
            amount: Transaction amount
            description: Transaction description
            related_entity_id: Optional ID of related entity (player, NPC, etc.)
            transaction_data: Optional additional transaction data
            
        Returns:
            Dictionary with transaction details
        """
        return self.daily_operations_service.record_financial_transaction(
            db, business_id, transaction_type, amount, description,
            related_entity_id, transaction_data
        )
    
    def get_financial_records(
        self,
        db: Session,
        business_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get financial records for a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            start_date: Optional start date for records
            end_date: Optional end date for records
            transaction_type: Optional transaction type filter
            limit: Maximum number of records to return
            
        Returns:
            List of transaction records
        """
        return self.daily_operations_service.get_financial_records(
            db, business_id, start_date, end_date, transaction_type, limit
        )
    
    def calculate_profit_and_loss(
        self,
        db: Session,
        business_id: str,
        period: str = "week"
    ) -> Dict[str, Any]:
        """
        Calculate profit and loss for a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            period: Time period ("day", "week", "month", or "year")
            
        Returns:
            Dictionary with profit and loss statement
        """
        return self.daily_operations_service.calculate_profit_and_loss(db, business_id, period)
    
    # === STAFF MANAGEMENT ===
    
    def hire_staff(
        self,
        db: Session,
        business_id: str,
        staff_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Hire a new staff member.
        
        Args:
            db: Database session
            business_id: ID of the business
            staff_data: Data for the new staff member
            
        Returns:
            Dictionary with the hired staff details
        """
        return self.daily_operations_service.hire_staff_member(db, business_id, staff_data)
    
    def fire_staff(
        self,
        db: Session,
        business_id: str,
        staff_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fire a staff member.
        
        Args:
            db: Database session
            business_id: ID of the business
            staff_id: ID of the staff member to fire
            reason: Optional reason for firing
            
        Returns:
            Dictionary with firing results
        """
        return self.daily_operations_service.fire_staff_member(db, business_id, staff_id, reason)
    
    def update_staff_contract(
        self,
        db: Session,
        business_id: str,
        staff_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a staff member's contract.
        
        Args:
            db: Database session
            business_id: ID of the business
            staff_id: ID of the staff member
            update_data: Data to update
            
        Returns:
            Dictionary with the updated contract details
        """
        return self.daily_operations_service.update_staff_contract(db, business_id, staff_id, update_data)
    
    def get_staff(
        self,
        db: Session,
        business_id: str,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get staff members for a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            role_filter: Optional role filter
            
        Returns:
            List of staff members
        """
        return self.daily_operations_service.get_staff_members(db, business_id, role_filter)
    
    # === CUSTOMER MANAGEMENT ===
    
    def process_customer_purchase(
        self,
        db: Session,
        business_id: str,
        customer_id: str,
        items: List[Dict[str, Any]],
        total_price: float,
        transaction_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a customer purchase.
        
        Args:
            db: Database session
            business_id: ID of the business
            customer_id: ID of the customer
            items: List of items purchased
            total_price: Total price of the purchase
            transaction_notes: Optional transaction notes
            
        Returns:
            Dictionary with purchase results
        """
        return self.daily_operations_service.process_customer_purchase(
            db, business_id, customer_id, items, total_price, transaction_notes
        )
    
    def handle_custom_order(
        self,
        db: Session,
        business_id: str,
        order_data: Dict[str, Any]
    ) -> CustomOrderRequest:
        """
        Handle a new custom order.
        
        Args:
            db: Database session
            business_id: ID of the business
            order_data: Custom order data
            
        Returns:
            Created custom order
        """
        return self.daily_operations_service.create_custom_order(db, business_id, order_data)
    
    def update_custom_order_status(
        self,
        db: Session,
        business_id: str,
        order_id: str,
        new_status: str,
        status_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a custom order.
        
        Args:
            db: Database session
            business_id: ID of the business
            order_id: ID of the order
            new_status: New status
            status_notes: Optional status notes
            
        Returns:
            Dictionary with update results
        """
        return self.daily_operations_service.update_custom_order_status(
            db, business_id, order_id, new_status, status_notes
        )
    
    def get_custom_orders(
        self,
        db: Session,
        business_id: str,
        status_filter: Optional[str] = None
    ) -> List[CustomOrderRequest]:
        """
        Get custom orders for a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            status_filter: Optional status filter
            
        Returns:
            List of custom orders
        """
        return self.daily_operations_service.get_custom_orders(db, business_id, status_filter)
    
    # === BUSINESS DEVELOPMENT ===
    
    def upgrade_business(
        self,
        db: Session,
        business_id: str,
        upgrade_type: str,
        upgrade_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply an upgrade to a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            upgrade_type: Type of upgrade
            upgrade_data: Upgrade details
            
        Returns:
            Dictionary with upgrade results
        """
        return self.development_service.apply_business_upgrade(db, business_id, upgrade_type, upgrade_data)
    
    def research_new_product(
        self,
        db: Session,
        business_id: str,
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Research a new product or service.
        
        Args:
            db: Database session
            business_id: ID of the business
            research_data: Research details
            
        Returns:
            Dictionary with research results
        """
        return self.development_service.research_new_product(db, business_id, research_data)
    
    def create_marketing_campaign(
        self,
        db: Session,
        business_id: str,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a marketing campaign.
        
        Args:
            db: Database session
            business_id: ID of the business
            campaign_data: Campaign details
            
        Returns:
            Dictionary with campaign results
        """
        return self.development_service.create_marketing_campaign(db, business_id, campaign_data)
    
    def expand_business(
        self,
        db: Session,
        business_id: str,
        expansion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Expand a business (new location, increased capacity, etc.).
        
        Args:
            db: Database session
            business_id: ID of the business
            expansion_data: Expansion details
            
        Returns:
            Dictionary with expansion results
        """
        return self.development_service.expand_business(db, business_id, expansion_data)
    
    # === SYSTEM INTEGRATIONS ===
    
    def sync_with_economy(
        self,
        db: Session,
        business_id: str,
        economy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synchronize a business with the economy system.
        
        Args:
            db: Database session
            business_id: ID of the business
            economy_data: Economy data
            
        Returns:
            Dictionary with synchronization results
        """
        return self.system_integrations.synchronize_with_economy(db, business_id, economy_data)
    
    def apply_economic_event(
        self,
        db: Session,
        event_data: Dict[str, Any],
        affected_region_ids: Optional[List[str]] = None,
        affected_business_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Apply an economic event to businesses.
        
        Args:
            db: Database session
            event_data: Event data
            affected_region_ids: Optional list of affected region IDs
            affected_business_types: Optional list of affected business types
            
        Returns:
            Dictionary with event application results
        """
        return self.system_integrations.apply_economic_event_to_businesses(
            db, event_data, affected_region_ids, affected_business_types
        )
    
    def generate_business_quest(
        self,
        db: Session,
        business_id: str,
        quest_difficulty: int = 3,
        quest_type: Optional[str] = None,
        for_player_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a quest related to a business.
        
        Args:
            db: Database session
            business_id: ID of the business
            quest_difficulty: Quest difficulty (1-10)
            quest_type: Optional specific quest type
            for_player_id: Optional player ID (if not the business owner)
            
        Returns:
            Dictionary with quest generation results
        """
        return self.system_integrations.generate_business_related_quest(
            db, business_id, quest_difficulty, quest_type, for_player_id
        )
    
    def process_quest_completion(
        self,
        db: Session,
        quest_id: str,
        business_id: str,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process the completion of a business-related quest.
        
        Args:
            db: Database session
            quest_id: Quest ID
            business_id: Business ID
            completion_data: Quest completion data
            
        Returns:
            Dictionary with processing results
        """
        return self.system_integrations.process_quest_completion_for_business(
            db, quest_id, business_id, completion_data
        )
    
    def generate_npc_order(
        self,
        db: Session,
        business_id: str,
        npc_id: str,
        npc_data: Dict[str, Any]
    ) -> CustomOrderRequest:
        """
        Generate a custom order from an NPC.
        
        Args:
            db: Database session
            business_id: Business ID
            npc_id: NPC ID
            npc_data: NPC data
            
        Returns:
            Created custom order
        """
        return self.system_integrations.generate_npc_custom_order(db, business_id, npc_id, npc_data)
    
    def process_npc_satisfaction(
        self,
        db: Session,
        business_id: str,
        npc_id: str,
        interaction_type: str,
        satisfaction_rating: int,
        interaction_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process NPC satisfaction with a business interaction.
        
        Args:
            db: Database session
            business_id: Business ID
            npc_id: NPC ID
            interaction_type: Type of interaction
            satisfaction_rating: Satisfaction rating (1-5)
            interaction_details: Interaction details
            
        Returns:
            Dictionary with impact results
        """
        return self.system_integrations.process_npc_satisfaction_impact(
            db, business_id, npc_id, interaction_type, satisfaction_rating, interaction_details
        )
    
    def trigger_business_event(
        self,
        db: Session,
        business_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a special event for a business.
        
        Args:
            db: Database session
            business_id: Business ID
            event_type: Type of event
            event_data: Event details
            
        Returns:
            Dictionary with event results
        """
        return self.system_integrations.trigger_business_event(db, business_id, event_type, event_data)