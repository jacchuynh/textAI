"""
Business System Integration Example

This module demonstrates how to use the business system API
and how it integrates with other game systems.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

# Import business system components
from backend.src.business.api import BusinessAPI
from backend.src.business.models.pydantic_models import (
    BusinessFoundingRequest, BusinessType, CustomOrderStatus, TransactionType
)

# Import related systems (uncomment and adjust as needed)
# from backend.src.economy.services.economy_service import EconomyService
# from backend.src.quest.services.quest_generator_service import QuestGeneratorService
# from backend.src.npc.npc_generator_service import NPCGeneratorService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BusinessIntegrationExample")

class BusinessSystemIntegrationExample:
    """
    Example class demonstrating how to use the business system API
    and integrate it with other game systems.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the example with a database session.
        
        Args:
            db: Database session
        """
        self.db = db
        self.business_api = BusinessAPI()
        
        # Initialize related services
        # self.economy_service = EconomyService()
        # self.quest_generator = QuestGeneratorService()
        # self.npc_generator = NPCGeneratorService()
    
    # === FOUNDING A BUSINESS ===
    
    def example_found_new_business(self, player_id: str) -> str:
        """
        Example of founding a new business.
        
        Args:
            player_id: ID of the player founding the business
            
        Returns:
            ID of the newly founded business
        """
        logger.info("=== EXAMPLE: FOUNDING A NEW BUSINESS ===")
        
        # Create a founding request
        founding_request = BusinessFoundingRequest(
            player_character_id=player_id,
            business_name_player_chosen="The Blacksmith's Anvil",
            business_type=BusinessType.BLACKSMITH.value,
            founding_capital=1000.0,
            location_id="town_square_123",
            founding_inventory={
                "iron_ingots": {
                    "item_id": "iron_ingots",
                    "quantity": 50,
                    "purchase_price_per_unit": 5.0,
                    "selling_price_per_unit": 8.0,
                    "is_material": True,
                    "category": "metal",
                    "restock_threshold": 10,
                    "last_restocked": datetime.utcnow().isoformat()
                },
                "leather": {
                    "item_id": "leather",
                    "quantity": 30,
                    "purchase_price_per_unit": 3.0,
                    "selling_price_per_unit": 5.0,
                    "is_material": True,
                    "category": "crafting",
                    "restock_threshold": 5,
                    "last_restocked": datetime.utcnow().isoformat()
                },
                "basic_sword": {
                    "item_id": "basic_sword",
                    "quantity": 5,
                    "purchase_price_per_unit": 0.0,  # Crafted, not purchased
                    "selling_price_per_unit": 25.0,
                    "is_material": False,
                    "category": "weapon",
                    "restock_threshold": 2,
                    "last_restocked": datetime.utcnow().isoformat()
                }
            },
            founding_staff_contracts=[
                {
                    "staff_name": "Jormund the Apprentice",
                    "role": "apprentice",
                    "agreed_wage_per_period": 25.0,
                    "wage_payment_schedule": "weekly",
                    "assigned_tasks_description": "Assist with basic smithing tasks and handle customer requests.",
                    "work_schedule": "morning-afternoon"
                }
            ],
            business_description="A quality blacksmith shop specializing in weapons and tools."
        )
        
        # Found the business
        business = self.business_api.found_business(self.db, founding_request)
        
        logger.info(f"Founded new business: {business.business_name_player_chosen} (ID: {business.id})")
        logger.info(f"Starting capital: {business.current_capital}")
        logger.info(f"Inventory items: {len(business.inventory)}")
        logger.info(f"Staff members: {len(business.current_staff_contracts)}")
        
        return business.id
    
    # === DAILY OPERATIONS ===
    
    def example_daily_operations(self, business_id: str) -> None:
        """
        Example of daily business operations.
        
        Args:
            business_id: ID of the business
        """
        logger.info("=== EXAMPLE: DAILY BUSINESS OPERATIONS ===")
        
        # Get the business
        business = self.business_api.get_business(self.db, business_id)
        if not business:
            logger.error(f"Business {business_id} not found")
            return
        
        logger.info(f"Running daily operations for: {business.business_name_player_chosen}")
        
        # Process a customer purchase
        self._example_process_customer_purchase(business_id)
        
        # Handle a custom order
        self._example_handle_custom_order(business_id)
        
        # Record various financial transactions
        self._example_record_financial_transactions(business_id)
        
        # Generate a business summary
        summary = self.business_api.get_business_summary(self.db, business_id)
        
        logger.info("Daily business summary:")
        logger.info(f"Total sales: {summary.get('total_sales', 0)}")
        logger.info(f"Total expenses: {summary.get('total_expenses', 0)}")
        logger.info(f"Net profit: {summary.get('net_profit', 0)}")
        logger.info(f"Customer interactions: {summary.get('customer_interaction_count', 0)}")
        
    def _example_process_customer_purchase(self, business_id: str) -> None:
        """Example of processing a customer purchase."""
        # Process a customer purchase
        purchase_result = self.business_api.process_customer_purchase(
            self.db,
            business_id,
            customer_id="player_654321",
            items=[
                {
                    "item_id": "basic_sword",
                    "quantity": 1,
                    "price_per_unit": 25.0
                }
            ],
            total_price=25.0,
            transaction_notes="Player purchased a basic sword."
        )
        
        logger.info(f"Processed customer purchase: {purchase_result.get('success', False)}")
        logger.info(f"Transaction ID: {purchase_result.get('transaction_id')}")
        logger.info(f"Updated inventory: Swords remaining: {purchase_result.get('remaining_quantities', {}).get('basic_sword', 0)}")
    
    def _example_handle_custom_order(self, business_id: str) -> None:
        """Example of handling a custom order."""
        # Create a custom order
        custom_order = self.business_api.handle_custom_order(
            self.db,
            business_id,
            {
                "requesting_npc_id": "guard_captain_789",
                "item_description_by_npc": "I need a sturdy steel sword with a balanced weight for combat. Good craftsmanship is essential.",
                "item_category_hint": "weapon",
                "quantity": 1,
                "offered_price_initial": 50.0,
                "deadline_preference_days": 3,
                "deadline_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "status": CustomOrderStatus.AWAITING_PLAYER_REVIEW.value
            }
        )
        
        logger.info(f"Created custom order: {custom_order.id}")
        logger.info(f"From: {custom_order.requesting_npc_id}")
        logger.info(f"Description: {custom_order.item_description_by_npc}")
        logger.info(f"Offered price: {custom_order.offered_price_initial}")
        
        # Accept the order
        update_result = self.business_api.update_custom_order_status(
            self.db,
            business_id,
            custom_order.id,
            CustomOrderStatus.ACCEPTED_BY_PLAYER.value,
            "I'll have this ready for you by the deadline."
        )
        
        logger.info(f"Updated order status: {update_result.get('success', False)}")
        logger.info(f"New status: {update_result.get('new_status')}")
    
    def _example_record_financial_transactions(self, business_id: str) -> None:
        """Example of recording various financial transactions."""
        # Record rent payment
        rent_transaction = self.business_api.record_transaction(
            self.db,
            business_id,
            TransactionType.EXPENSE.value,
            amount=20.0,
            description="Weekly shop rental payment",
            related_entity_id="town_council",
            transaction_data={"category": "rent", "recurring": True}
        )
        
        logger.info(f"Recorded rent transaction: {rent_transaction.get('transaction_id')}")
        
        # Record material purchase
        material_transaction = self.business_api.record_transaction(
            self.db,
            business_id,
            TransactionType.EXPENSE.value,
            amount=50.0,
            description="Purchase of additional iron ingots",
            related_entity_id="mining_company_456",
            transaction_data={"category": "materials", "material_type": "metal"}
        )
        
        logger.info(f"Recorded material purchase: {material_transaction.get('transaction_id')}")
        
        # Record staff wages
        wage_transaction = self.business_api.record_transaction(
            self.db,
            business_id,
            TransactionType.EXPENSE.value,
            amount=25.0,
            description="Weekly wages for Jormund the Apprentice",
            related_entity_id="npc_jormund",
            transaction_data={"category": "wages", "staff_id": "staff_001"}
        )
        
        logger.info(f"Recorded wage payment: {wage_transaction.get('transaction_id')}")
        
        # Get financial records
        financial_records = self.business_api.get_financial_records(
            self.db,
            business_id,
            start_date=datetime.utcnow() - timedelta(days=7),
            limit=10
        )
        
        logger.info(f"Retrieved {len(financial_records)} recent financial records")
    
    # === BUSINESS DEVELOPMENT ===
    
    def example_business_development(self, business_id: str) -> None:
        """
        Example of business development activities.
        
        Args:
            business_id: ID of the business
        """
        logger.info("=== EXAMPLE: BUSINESS DEVELOPMENT ===")
        
        # Get the business
        business = self.business_api.get_business(self.db, business_id)
        if not business:
            logger.error(f"Business {business_id} not found")
            return
            
        logger.info(f"Developing business: {business.business_name_player_chosen}")
        
        # Apply a business upgrade
        upgrade_result = self.business_api.upgrade_business(
            self.db,
            business_id,
            "equipment",
            {
                "upgrade_name": "Advanced Forge",
                "upgrade_description": "A better forge for creating higher quality weapons",
                "cost": 200.0,
                "benefits": {
                    "production_efficiency": 0.2,  # 20% efficiency increase
                    "quality_bonus": 0.15,         # 15% quality increase
                    "unlocked_recipes": ["steel_sword", "ornate_dagger"]
                }
            }
        )
        
        logger.info(f"Applied business upgrade: {upgrade_result.get('success', False)}")
        logger.info(f"Upgrade: {upgrade_result.get('upgrade_name')}")
        logger.info(f"Cost: {upgrade_result.get('cost')}")
        logger.info(f"New capabilities: {upgrade_result.get('benefits', {}).get('unlocked_recipes', [])}")
        
        # Research a new product
        research_result = self.business_api.research_new_product(
            self.db,
            business_id,
            {
                "product_name": "Enchanted Blade",
                "product_description": "A sword with magical properties",
                "research_cost": 100.0,
                "research_time_days": 7,
                "materials_required": {
                    "iron_ingots": 10,
                    "magical_essence": 5
                },
                "expected_selling_price": 200.0
            }
        )
        
        logger.info(f"Started product research: {research_result.get('success', False)}")
        logger.info(f"Research: {research_result.get('product_name')}")
        logger.info(f"Expected completion: {research_result.get('expected_completion_date')}")
        
        # Create a marketing campaign
        campaign_result = self.business_api.create_marketing_campaign(
            self.db,
            business_id,
            {
                "campaign_name": "Summer Weapon Sale",
                "campaign_description": "Promoting a special discount on all weapons",
                "cost": 50.0,
                "duration_days": 14,
                "expected_benefits": {
                    "customer_traffic_increase": 0.3,  # 30% more customers
                    "sales_boost": 0.25             # 25% boost in sales
                },
                "special_offers": [
                    {"item_id": "basic_sword", "discount_percentage": 15}
                ]
            }
        )
        
        logger.info(f"Created marketing campaign: {campaign_result.get('success', False)}")
        logger.info(f"Campaign: {campaign_result.get('campaign_name')}")
        logger.info(f"Cost: {campaign_result.get('cost')}")
        logger.info(f"Duration: {campaign_result.get('duration_days')} days")
    
    # === SYSTEM INTEGRATIONS ===
    
    def example_system_integrations(self, business_id: str) -> None:
        """
        Example of integrations with other game systems.
        
        Args:
            business_id: ID of the business
        """
        logger.info("=== EXAMPLE: SYSTEM INTEGRATIONS ===")
        
        # Get the business
        business = self.business_api.get_business(self.db, business_id)
        if not business:
            logger.error(f"Business {business_id} not found")
            return
            
        logger.info(f"Running system integrations for: {business.business_name_player_chosen}")
        
        # Economy integration - sync with market prices
        # In a real implementation, this would get data from the economy system
        economy_data = {
            "inflation_rate": 0.05,  # 5% inflation
            "market_prices": {
                "iron_ingots": 5.5,   # Price has increased
                "leather": 2.8,       # Price has decreased
                "basic_sword": 27.0   # Price has increased
            },
            "regional_modifiers": {
                "town_square_123": 1.1  # 10% premium in this region
            },
            "supply_demand": {
                "iron_ingots": {
                    "supply_factor": 0.9,  # Lower supply, higher prices
                    "shortage": True,
                    "shortage_severity": 0.3
                },
                "leather": {
                    "supply_factor": 1.2,  # Higher supply, lower prices
                    "surplus": True,
                    "surplus_severity": 0.2
                }
            }
        }
        
        sync_result = self.business_api.sync_with_economy(self.db, business_id, economy_data)
        
        logger.info(f"Synchronized with economy: {len(sync_result.get('changes', {}).get('price_adjustments', []))} price adjustments")
        logger.info(f"Supply impacts: {len(sync_result.get('changes', {}).get('supply_impacts', []))}")
        logger.info(f"Events triggered: {len(sync_result.get('changes', {}).get('events_triggered', []))}")
        
        # Economic event - price shock
        event_result = self.business_api.apply_economic_event(
            self.db,
            {
                "event_type": "price_shock",
                "impact": 0.2,  # 20% price increase
                "affected_items": ["iron_ingots"],
                "description": "Due to a mine collapse, iron prices have spiked."
            },
            affected_region_ids=["town_square_123"],
            affected_business_types=[BusinessType.BLACKSMITH.value]
        )
        
        logger.info(f"Applied economic event to {event_result.get('businesses_affected', 0)} businesses")
        logger.info(f"Total impact: {event_result.get('total_impact', 0.0)}")
        
        # Quest integration - generate business-related quest
        quest_result = self.business_api.generate_business_quest(
            self.db,
            business_id,
            quest_difficulty=3,
            quest_type="supply_chain"
        )
        
        logger.info(f"Generated business quest: {quest_result.get('quest_type')}")
        logger.info(f"Quest title: {quest_result.get('quest_data', {}).get('title')}")
        logger.info(f"Quest difficulty: {quest_result.get('quest_data', {}).get('difficulty')}")
        
        # Process quest completion
        completion_result = self.business_api.process_quest_completion(
            self.db,
            "quest_123456",  # In a real implementation, this would be the actual quest ID
            business_id,
            {
                "quest_type": "supply_chain",
                "outcome": "success",
                "acquired_materials": {
                    "iron_ingots": 20,
                    "coal": 10
                },
                "purchase_price": {
                    "iron_ingots": 4.5,  # Discount due to quest success
                    "coal": 2.0
                }
            }
        )
        
        logger.info(f"Processed quest completion with {len(completion_result.get('effects_applied', []))} effects")
        
        # NPC integration - generate NPC order
        npc_data = {
            "npc_id": "knight_commander",
            "name": "Sir Galavant",
            "wealth_level": 8,  # Wealthy (1-10)
            "social_status": 9,  # High status (1-10)
            "profession": "knight",
            "preferences": {
                "equipment": {
                    "preferred_material": "steel",
                    "preferred_style": "functional yet elegant"
                }
            },
            "urgency": 6  # Moderate urgency (1-10)
        }
        
        npc_order = self.business_api.generate_npc_order(self.db, business_id, "knight_commander", npc_data)
        
        logger.info(f"Generated NPC order: {npc_order.id}")
        logger.info(f"Description: {npc_order.item_description_by_npc}")
        logger.info(f"Offered price: {npc_order.offered_price_initial}")
        logger.info(f"Deadline: {npc_order.deadline_date}")
        
        # Process NPC satisfaction
        satisfaction_result = self.business_api.process_npc_satisfaction(
            self.db,
            business_id,
            "knight_commander",
            "custom_order",
            4,  # Satisfied (1-5)
            {
                "order_id": npc_order.id,
                "completed_on_time": True,
                "product_quality": "high",
                "comments": "The sword is well-balanced and finely crafted."
            }
        )
        
        logger.info(f"Processed NPC satisfaction: {satisfaction_result.get('satisfaction_rating')}")
        logger.info(f"Reputation impact: {satisfaction_result.get('reputation_impact')}")
        logger.info(f"New NPC satisfaction level: {satisfaction_result.get('new_npc_satisfaction')}")
        
        # Trigger business event
        event_result = self.business_api.trigger_business_event(
            self.db,
            business_id,
            "festival",
            {
                "festival_name": "Summer Solstice Festival",
                "duration_days": 3,
                "magnitude": 0.5,  # Medium-sized festival
                "description": "The annual Summer Solstice Festival brings many visitors to town."
            }
        )
        
        logger.info(f"Triggered business event: {event_result.get('event_type')}")
        logger.info(f"Event impacts: {len(event_result.get('impacts', []))}")


# Example of how to use this example class
def run_full_example(db: Session, player_id: str) -> None:
    """
    Run the full business system integration example.
    
    Args:
        db: Database session
        player_id: ID of the player character
    """
    example = BusinessSystemIntegrationExample(db)
    
    # Found a new business
    business_id = example.example_found_new_business(player_id)
    
    # Run daily operations
    example.example_daily_operations(business_id)
    
    # Run business development
    example.example_business_development(business_id)
    
    # Run system integrations
    example.example_system_integrations(business_id)
    
    logger.info("Completed full business system integration example")
    
    return business_id