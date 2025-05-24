"""
Business System Integrations

This module provides integration points between the business system and other game systems,
such as quests, economy, NPCs, and events.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import business models and services
from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, CustomOrderRequest, BusinessReputation,
    BusinessType, CustomOrderStatus, TransactionType
)
from backend.src.business.services.player_business_daily_operations_service import PlayerBusinessDailyOperationsService
from backend.src.business.services.business_development_service import BusinessDevelopmentService
from backend.src.business.services.player_business_founding_service import PlayerBusinessFoundingService
from backend.src.business.crud import (
    get_business, get_businesses_by_player, update_business,
    create_custom_order, record_financial_transaction
)

# Import related systems (uncomment and adjust imports as needed)
# from backend.src.economy.services.economy_service import EconomyService
# from backend.src.economy.services.market_manipulation_service import MarketManipulationService
# from backend.src.quest.services.quest_generator_service import QuestGeneratorService
# from backend.src.npc.npc_generator_service import NPCGeneratorService

logger = logging.getLogger(__name__)

class BusinessSystemIntegrations:
    """
    Provides integration points between the business system and other game systems.
    """
    
    def __init__(self):
        """Initialize business system integrations."""
        self.daily_operations_service = PlayerBusinessDailyOperationsService()
        self.business_development_service = BusinessDevelopmentService()
        self.founding_service = PlayerBusinessFoundingService()
        
        # Initialize related services
        # self.economy_service = EconomyService()
        # self.quest_generator = QuestGeneratorService()
        # self.npc_generator = NPCGeneratorService()
        
        self.logger = logging.getLogger("BusinessSystemIntegrations")
        
    # === ECONOMY INTEGRATIONS ===
    
    def synchronize_with_economy(
        self,
        db: Session,
        business_id: str,
        economy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synchronize a business with the broader economy system.
        
        Args:
            db: Database session
            business_id: Business ID to synchronize
            economy_data: Economy data from economy service
            
        Returns:
            Dictionary with synchronization results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Extract relevant economy data
        global_inflation = economy_data.get("inflation_rate", 0.0)
        market_prices = economy_data.get("market_prices", {})
        regional_modifiers = economy_data.get("regional_modifiers", {})
        regional_modifier = regional_modifiers.get(business.region_id, 1.0) if hasattr(business, "region_id") else 1.0
        supply_demand = economy_data.get("supply_demand", {})
        
        # Track changes
        changes = {
            "price_adjustments": [],
            "supply_impacts": [],
            "events_triggered": []
        }
        
        # Update inventory prices based on economy
        inventory_updated = False
        inventory = business.inventory or {}
        
        for item_id, item_data in inventory.items():
            # Check if item has market price data
            if item_id in market_prices:
                market_price = market_prices[item_id]
                
                # Calculate adjustment factors
                inflation_factor = 1.0 + global_inflation
                market_factor = market_price / item_data.get("purchase_price_per_unit", market_price)
                supply_factor = supply_demand.get(item_id, {"supply_factor": 1.0}).get("supply_factor", 1.0)
                
                # Apply combined adjustment
                combined_factor = inflation_factor * market_factor * supply_factor * regional_modifier
                
                # Only update if significant change
                if abs(combined_factor - 1.0) > 0.05:  # 5% threshold
                    old_purchase_price = item_data.get("purchase_price_per_unit", 0)
                    old_selling_price = item_data.get("selling_price_per_unit", 0)
                    
                    # Adjust purchase price
                    new_purchase_price = old_purchase_price * combined_factor
                    
                    # Adjust selling price (with markup preservation)
                    markup = old_selling_price / old_purchase_price if old_purchase_price > 0 else 1.5
                    new_selling_price = new_purchase_price * markup
                    
                    # Update prices
                    inventory[item_id]["purchase_price_per_unit"] = new_purchase_price
                    inventory[item_id]["selling_price_per_unit"] = new_selling_price
                    
                    # Track change
                    changes["price_adjustments"].append({
                        "item_id": item_id,
                        "old_purchase_price": old_purchase_price,
                        "new_purchase_price": new_purchase_price,
                        "old_selling_price": old_selling_price,
                        "new_selling_price": new_selling_price,
                        "adjustment_factor": combined_factor
                    })
                    
                    inventory_updated = True
        
        # Update inventory if changes were made
        if inventory_updated:
            update_business(db, business_id, {"inventory": inventory})
        
        # Check for supply impact events
        for item_id, supply_data in supply_demand.items():
            if supply_data.get("shortage", False) and item_id in inventory and inventory[item_id]["quantity"] > 0:
                # Business has stock of a shortage item - potential event
                changes["supply_impacts"].append({
                    "item_id": item_id,
                    "type": "shortage",
                    "severity": supply_data.get("shortage_severity", 0.5),
                    "current_stock": inventory[item_id]["quantity"]
                })
                
                # Could trigger special orders, increased demand, etc.
                if supply_data.get("shortage_severity", 0.5) > 0.7 and inventory[item_id]["quantity"] > 5:
                    # Severe shortage and business has good stock - trigger high-value order
                    self._trigger_shortage_opportunity(db, business_id, item_id, inventory[item_id], supply_data)
                    
                    changes["events_triggered"].append({
                        "type": "shortage_opportunity",
                        "item_id": item_id,
                        "description": "High-value order opportunity due to market shortage"
                    })
            
            elif supply_data.get("surplus", False) and item_id in inventory:
                # Market surplus of an item - potential discount opportunity
                changes["supply_impacts"].append({
                    "item_id": item_id,
                    "type": "surplus",
                    "severity": supply_data.get("surplus_severity", 0.5),
                    "current_stock": inventory[item_id]["quantity"]
                })
                
                # Could trigger discount suppliers, bulk purchase opportunities, etc.
        
        # Log changes
        if changes["price_adjustments"] or changes["supply_impacts"] or changes["events_triggered"]:
            self.logger.info(f"Synchronized business {business_id} with economy: " +
                           f"{len(changes['price_adjustments'])} price adjustments, " +
                           f"{len(changes['supply_impacts'])} supply impacts, " +
                           f"{len(changes['events_triggered'])} events triggered")
        
        return {
            "business_id": business_id,
            "synchronization_date": datetime.utcnow().isoformat(),
            "changes": changes
        }
    
    def _trigger_shortage_opportunity(
        self,
        db: Session,
        business_id: str,
        item_id: str,
        item_data: Dict[str, Any],
        supply_data: Dict[str, Any]
    ) -> None:
        """
        Trigger a special opportunity due to market shortage.
        
        Args:
            db: Database session
            business_id: Business ID
            item_id: Shortage item ID
            item_data: Business inventory data for the item
            supply_data: Supply-demand data for the item
        """
        # Generate a high-value order for the shortage item
        shortage_severity = supply_data.get("shortage_severity", 0.5)
        
        # Calculate premium price (higher for severe shortages)
        premium_multiplier = 1.5 + shortage_severity
        premium_price = item_data.get("selling_price_per_unit", 10.0) * premium_multiplier
        
        # Calculate quantity (lower for severe shortages)
        max_quantity = min(item_data["quantity"] - 1, 5)  # Leave at least 1 in stock
        requested_quantity = max(1, int(max_quantity * (1.0 - shortage_severity)))
        
        # Create order request
        order_data = {
            "requesting_npc_id": f"merchant-{hash(datetime.utcnow().isoformat()) % 1000}",
            "target_player_business_profile_id": business_id,
            "item_description_by_npc": f"Urgent need for {item_id} due to market shortage. Willing to pay premium.",
            "item_category_hint": item_data.get("category"),
            "quantity": requested_quantity,
            "offered_price_initial": premium_price * requested_quantity,
            "deadline_preference_days": max(1, int(3 * (1.0 - shortage_severity))),  # Shorter deadline for severe shortages
            "deadline_date": datetime.utcnow() + timedelta(days=max(1, int(3 * (1.0 - shortage_severity)))),
            "status": CustomOrderStatus.AWAITING_PLAYER_REVIEW.value,
            "custom_data": {
                "shortage_opportunity": True,
                "shortage_severity": shortage_severity,
                "market_premium": premium_multiplier,
                "urgent": shortage_severity > 0.5
            }
        }
        
        # Create the order
        create_custom_order(db, order_data)
    
    def apply_economic_event_to_businesses(
        self,
        db: Session,
        event_data: Dict[str, Any],
        affected_region_ids: Optional[List[str]] = None,
        affected_business_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Apply an economic event to relevant businesses.
        
        Args:
            db: Database session
            event_data: Economic event data
            affected_region_ids: Optional list of affected region IDs
            affected_business_types: Optional list of affected business types
            
        Returns:
            Dictionary with event application results
        """
        # Build query filters based on parameters
        filters = []
        
        if affected_region_ids:
            # In a real implementation, filter by region
            pass
            
        if affected_business_types:
            # Filter by business type
            filters.extend([business.business_type in affected_business_types for business in range(0)])
        
        # Get affected businesses
        # In a real implementation, this would query the database with filters
        # For now, get all businesses
        businesses = []  # get_all_businesses(db, filters) would go here
        
        # Process the event
        event_type = event_data.get("event_type", "")
        event_impact = event_data.get("impact", 0.0)
        event_duration = event_data.get("duration_days", 7)
        affected_items = event_data.get("affected_items", [])
        
        results = {
            "event_type": event_type,
            "businesses_affected": 0,
            "total_impact": 0.0,
            "details": []
        }
        
        # Apply the event to each business
        for business in businesses:
            # Check if business is active
            if not hasattr(business, "is_active") or not business.is_active:
                continue
                
            # Apply event based on type
            if event_type == "price_shock":
                impact = self._apply_price_shock(db, business.id, event_impact, affected_items)
            elif event_type == "supply_disruption":
                impact = self._apply_supply_disruption(db, business.id, event_impact, affected_items, event_duration)
            elif event_type == "demand_surge":
                impact = self._apply_demand_surge(db, business.id, event_impact, affected_items, event_duration)
            elif event_type == "trade_restriction":
                impact = self._apply_trade_restriction(db, business.id, event_impact, affected_items, event_duration)
            else:
                # Unknown event type
                impact = None
            
            # Track results
            if impact:
                results["businesses_affected"] += 1
                results["total_impact"] += impact.get("total_impact", 0.0)
                results["details"].append({
                    "business_id": business.id,
                    "business_name": business.business_name_player_chosen,
                    "impact": impact
                })
        
        self.logger.info(f"Applied economic event {event_type} to {results['businesses_affected']} businesses")
        
        return results
    
    def _apply_price_shock(
        self,
        db: Session,
        business_id: str,
        impact_factor: float,
        affected_items: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply a price shock economic event to a business.
        
        Args:
            db: Database session
            business_id: Business ID
            impact_factor: Impact factor (positive = price increase, negative = price decrease)
            affected_items: List of affected item IDs
            
        Returns:
            Dictionary with impact details or None if no impact
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            return None
            
        # Check inventory for affected items
        inventory = business.inventory or {}
        affected_inventory_items = [item_id for item_id in affected_items if item_id in inventory]
        
        if not affected_inventory_items:
            return None
            
        # Apply price shock
        total_impact = 0.0
        price_changes = []
        
        for item_id in affected_inventory_items:
            item_data = inventory[item_id]
            old_purchase_price = item_data.get("purchase_price_per_unit", 0)
            old_selling_price = item_data.get("selling_price_per_unit", 0)
            
            # Calculate new prices
            new_purchase_price = old_purchase_price * (1.0 + impact_factor)
            
            # Adjust selling price (with markup preservation)
            markup = old_selling_price / old_purchase_price if old_purchase_price > 0 else 1.5
            new_selling_price = new_purchase_price * markup
            
            # Update prices
            inventory[item_id]["purchase_price_per_unit"] = new_purchase_price
            inventory[item_id]["selling_price_per_unit"] = new_selling_price
            
            # Calculate impact
            price_impact = (new_purchase_price - old_purchase_price) * item_data.get("quantity", 0)
            total_impact += price_impact
            
            # Track change
            price_changes.append({
                "item_id": item_id,
                "old_purchase_price": old_purchase_price,
                "new_purchase_price": new_purchase_price,
                "old_selling_price": old_selling_price,
                "new_selling_price": new_selling_price,
                "quantity": item_data.get("quantity", 0),
                "price_impact": price_impact
            })
        
        # Update inventory
        update_business(db, business_id, {"inventory": inventory})
        
        # Add event to custom data
        custom_data = business.custom_data or {}
        economic_events = custom_data.get("economic_events", [])
        
        economic_events.append({
            "date": datetime.utcnow().isoformat(),
            "event_type": "price_shock",
            "impact_factor": impact_factor,
            "affected_items": affected_inventory_items,
            "total_impact": total_impact
        })
        
        custom_data["economic_events"] = economic_events
        update_business(db, business_id, {"custom_data": custom_data})
        
        return {
            "event_type": "price_shock",
            "affected_items_count": len(affected_inventory_items),
            "price_changes": price_changes,
            "total_impact": total_impact
        }
    
    def _apply_supply_disruption(
        self,
        db: Session,
        business_id: str,
        severity: float,
        affected_items: List[str],
        duration_days: int
    ) -> Optional[Dict[str, Any]]:
        """
        Apply a supply disruption economic event to a business.
        
        Args:
            db: Database session
            business_id: Business ID
            severity: Disruption severity (0.0-1.0)
            affected_items: List of affected item IDs
            duration_days: Duration of disruption in days
            
        Returns:
            Dictionary with impact details or None if no impact
        """
        # Implementation would be similar to price shock but focusing on
        # availability rather than price
        
        # For brevity, returning None here
        return None
    
    def _apply_demand_surge(
        self,
        db: Session,
        business_id: str,
        magnitude: float,
        affected_items: List[str],
        duration_days: int
    ) -> Optional[Dict[str, Any]]:
        """
        Apply a demand surge economic event to a business.
        
        Args:
            db: Database session
            business_id: Business ID
            magnitude: Surge magnitude (0.0-1.0)
            affected_items: List of affected item IDs
            duration_days: Duration of surge in days
            
        Returns:
            Dictionary with impact details or None if no impact
        """
        # Implementation would focus on creating increased custom orders
        # and customer traffic for the affected items
        
        # For brevity, returning None here
        return None
    
    def _apply_trade_restriction(
        self,
        db: Session,
        business_id: str,
        severity: float,
        affected_items: List[str],
        duration_days: int
    ) -> Optional[Dict[str, Any]]:
        """
        Apply a trade restriction economic event to a business.
        
        Args:
            db: Database session
            business_id: Business ID
            severity: Restriction severity (0.0-1.0)
            affected_items: List of affected item IDs
            duration_days: Duration of restriction in days
            
        Returns:
            Dictionary with impact details or None if no impact
        """
        # Implementation would focus on restricting the ability to buy/sell
        # certain items and potentially increasing smuggling opportunities
        
        # For brevity, returning None here
        return None
    
    # === QUEST INTEGRATIONS ===
    
    def generate_business_related_quest(
        self,
        db: Session,
        business_id: str,
        quest_difficulty: int = 3,
        quest_type: Optional[str] = None,
        for_player_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a quest related to a specific business.
        
        Args:
            db: Database session
            business_id: Business ID
            quest_difficulty: Quest difficulty (1-10)
            quest_type: Optional specific quest type
            for_player_id: Optional player ID (if not the business owner)
            
        Returns:
            Dictionary with quest generation results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Determine quest type if not specified
        if not quest_type:
            possible_types = [
                "supply_chain", "customer_service", "business_development",
                "reputation", "staff_issue", "competitor", "regulatory"
            ]
            
            # Weight based on business state
            weights = [1.0] * len(possible_types)
            
            # Adjust weights based on business state
            inventory = business.inventory or {}
            if any(item.get("quantity", 0) < item.get("restock_threshold", 0) for item in inventory.values()):
                # Low inventory - increase supply chain quest weight
                weights[possible_types.index("supply_chain")] = 2.0
                
            staff_contracts = business.current_staff_contracts or []
            if not staff_contracts:
                # No staff - increase staff issue quest weight
                weights[possible_types.index("staff_issue")] = 2.0
                
            reputation = business.reputation or {}
            if reputation.get("overall_reputation", 5) < 4:
                # Low reputation - increase reputation quest weight
                weights[possible_types.index("reputation")] = 2.0
                
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            # Select quest type
            quest_type = random.choices(possible_types, weights=weights, k=1)[0]
        
        # Generate quest based on type
        if quest_type == "supply_chain":
            quest_data = self._generate_supply_chain_quest(db, business, quest_difficulty)
        elif quest_type == "customer_service":
            quest_data = self._generate_customer_service_quest(db, business, quest_difficulty)
        elif quest_type == "business_development":
            quest_data = self._generate_business_development_quest(db, business, quest_difficulty)
        elif quest_type == "reputation":
            quest_data = self._generate_reputation_quest(db, business, quest_difficulty)
        elif quest_type == "staff_issue":
            quest_data = self._generate_staff_issue_quest(db, business, quest_difficulty)
        elif quest_type == "competitor":
            quest_data = self._generate_competitor_quest(db, business, quest_difficulty)
        elif quest_type == "regulatory":
            quest_data = self._generate_regulatory_quest(db, business, quest_difficulty)
        else:
            # Default to supply chain quest
            quest_data = self._generate_supply_chain_quest(db, business, quest_difficulty)
        
        # Determine if quest is for business owner or another player
        target_player_id = for_player_id or business.player_character_id
        
        # Set common quest fields
        quest_data.update({
            "related_business_id": business_id,
            "target_player_id": target_player_id,
            "is_for_owner": target_player_id == business.player_character_id,
            "generation_date": datetime.utcnow().isoformat()
        })
        
        self.logger.info(f"Generated {quest_type} quest for business {business_id}")
        
        # In a real implementation, this would create the quest in the quest system
        # For now, just return the quest data
        
        return {
            "quest_type": quest_type,
            "quest_data": quest_data,
            "success": True
        }
    
    def _generate_supply_chain_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a supply chain related quest."""
        # This would be more detailed in a real implementation
        return {
            "quest_type": "supply_chain",
            "title": f"Supply Run for {business.business_name_player_chosen}",
            "description": "The business needs essential supplies to continue operations.",
            "difficulty": difficulty,
            "objectives": [
                {"type": "acquire_materials", "target": f"material-{difficulty}", "quantity": difficulty * 2},
                {"type": "deliver_materials", "destination": "business", "time_limit_hours": 48}
            ],
            "rewards": {
                "gold": difficulty * 50,
                "reputation": difficulty * 2,
                "business_benefit": "inventory_boost"
            }
        }
    
    def _generate_customer_service_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a customer service related quest."""
        # Implementation would be similar to the supply chain quest
        # but with different objectives and rewards
        
        # For brevity, returning a placeholder
        return {"quest_type": "customer_service", "difficulty": difficulty}
    
    def _generate_business_development_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a business development related quest."""
        # Implementation would be similar to the supply chain quest
        # but with different objectives and rewards
        
        # For brevity, returning a placeholder
        return {"quest_type": "business_development", "difficulty": difficulty}
    
    def _generate_reputation_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a reputation related quest."""
        # Implementation would be similar to the supply chain quest
        # but with different objectives and rewards
        
        # For brevity, returning a placeholder
        return {"quest_type": "reputation", "difficulty": difficulty}
    
    def _generate_staff_issue_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a staff issue related quest."""
        # Implementation would be similar to the supply chain quest
        # but with different objectives and rewards
        
        # For brevity, returning a placeholder
        return {"quest_type": "staff_issue", "difficulty": difficulty}
    
    def _generate_competitor_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a competitor related quest."""
        # Implementation would be similar to the supply chain quest
        # but with different objectives and rewards
        
        # For brevity, returning a placeholder
        return {"quest_type": "competitor", "difficulty": difficulty}
    
    def _generate_regulatory_quest(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        difficulty: int
    ) -> Dict[str, Any]:
        """Generate a regulatory related quest."""
        # Implementation would be similar to the supply chain quest
        # but with different objectives and rewards
        
        # For brevity, returning a placeholder
        return {"quest_type": "regulatory", "difficulty": difficulty}
    
    def process_quest_completion_for_business(
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
            business_id: Related business ID
            completion_data: Quest completion data
            
        Returns:
            Dictionary with processing results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Process based on quest type and outcome
        quest_type = completion_data.get("quest_type", "")
        outcome = completion_data.get("outcome", "success")
        impact_factor = 1.0 if outcome == "success" else -0.5
        
        results = {
            "quest_id": quest_id,
            "business_id": business_id,
            "effects_applied": []
        }
        
        # Apply effects based on quest type
        if quest_type == "supply_chain":
            # Supply chain quest might boost inventory
            if outcome == "success" and "acquired_materials" in completion_data:
                # Add materials to inventory
                materials = completion_data["acquired_materials"]
                inventory = business.inventory or {}
                
                for item_id, quantity in materials.items():
                    if item_id in inventory:
                        inventory[item_id]["quantity"] += quantity
                    else:
                        # Add new item to inventory
                        inventory[item_id] = {
                            "item_id": item_id,
                            "quantity": quantity,
                            "purchase_price_per_unit": completion_data.get("purchase_price", {}).get(item_id, 10.0),
                            "selling_price_per_unit": completion_data.get("purchase_price", {}).get(item_id, 10.0) * 1.5,
                            "is_material": True,
                            "last_restocked": datetime.utcnow().isoformat()
                        }
                
                # Update business inventory
                update_business(db, business_id, {"inventory": inventory})
                
                results["effects_applied"].append({
                    "type": "inventory_update",
                    "materials_added": materials
                })
        
        elif quest_type == "reputation":
            # Reputation quest might affect business reputation
            reputation = business.reputation or {}
            
            # Apply reputation change
            base_change = completion_data.get("reputation_change", 0.5) * impact_factor
            
            # Update specific reputation components
            if "overall_reputation" in reputation:
                reputation["overall_reputation"] = min(10, max(1, reputation["overall_reputation"] + base_change))
                
            if "community_standing" in reputation:
                reputation["community_standing"] = min(10, max(1, reputation["community_standing"] + base_change * 1.5))
            
            # Add to notable achievements if successful
            if outcome == "success":
                achievements = reputation.get("notable_achievements", [])
                achievements.append({
                    "date": datetime.utcnow().isoformat(),
                    "description": completion_data.get("achievement_description", 
                                                     "Completed a special task that improved business reputation"),
                    "quest_id": quest_id
                })
                reputation["notable_achievements"] = achievements
            
            # Update business reputation
            update_business(db, business_id, {"reputation": reputation})
            
            results["effects_applied"].append({
                "type": "reputation_update",
                "reputation_change": base_change
            })
        
        # Other quest types would have similar implementations
        
        # Record quest completion in business history
        custom_data = business.custom_data or {}
        quest_history = custom_data.get("quest_history", [])
        
        quest_history.append({
            "quest_id": quest_id,
            "quest_type": quest_type,
            "completion_date": datetime.utcnow().isoformat(),
            "outcome": outcome,
            "effects": results["effects_applied"]
        })
        
        custom_data["quest_history"] = quest_history
        update_business(db, business_id, {"custom_data": custom_data})
        
        self.logger.info(f"Processed {outcome} completion of {quest_type} quest for business {business_id}")
        
        return results
    
    # === NPC INTEGRATIONS ===
    
    def generate_npc_custom_order(
        self,
        db: Session,
        business_id: str,
        npc_id: str,
        npc_data: Dict[str, Any]
    ) -> CustomOrderRequest:
        """
        Generate a custom order from an NPC based on their characteristics.
        
        Args:
            db: Database session
            business_id: Target business ID
            npc_id: NPC ID
            npc_data: NPC data including preferences and resources
            
        Returns:
            Created custom order request
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Extract relevant NPC data
        npc_wealth = npc_data.get("wealth_level", 5)  # 1-10
        npc_social_status = npc_data.get("social_status", 5)  # 1-10
        npc_preferences = npc_data.get("preferences", {})
        npc_profession = npc_data.get("profession", "commoner")
        
        # Determine appropriate order based on business type and NPC
        # For now, use a simple approach
        if business.business_type == BusinessType.BLACKSMITH.value:
            item_categories = ["weapon", "tool", "armor"]
            preferences = npc_preferences.get("equipment", {})
            
            # Profession-based category preference
            if npc_profession in ["guard", "soldier", "mercenary"]:
                if random.random() < 0.7:  # 70% chance
                    item_categories = ["weapon", "armor"]
            elif npc_profession in ["farmer", "miner", "woodcutter"]:
                if random.random() < 0.7:  # 70% chance
                    item_categories = ["tool"]
                    
            item_category = random.choice(item_categories)
            
            # Generate description based on category
            if item_category == "weapon":
                weapons = ["sword", "axe", "mace", "dagger", "spear"]
                weapon_type = random.choice(weapons)
                description = f"I need a quality {weapon_type}."
                
                # Add details based on NPC wealth and status
                if npc_wealth >= 8:
                    description += " Money is no object, I want the finest materials and craftsmanship."
                elif npc_wealth >= 5:
                    description += " I can pay for good materials, but nothing extravagant."
                else:
                    description += " Something functional but affordable."
                    
                if npc_social_status >= 8:
                    description += " It should also reflect my status with appropriate decorative elements."
                    
                # Add specific preferences
                if "preferred_material" in preferences:
                    description += f" I prefer {preferences['preferred_material']} if possible."
                    
            elif item_category == "tool":
                tools = ["hammer", "saw", "plow", "pickaxe", "shears"]
                tool_type = random.choice(tools)
                description = f"I require a reliable {tool_type} for my work."
                
                # Add details based on NPC needs
                if npc_wealth >= 7:
                    description += " I'm willing to pay extra for something that will last longer than usual."
                else:
                    description += " Something sturdy but not too expensive."
                    
            else:  # armor
                armors = ["helmet", "breastplate", "gauntlets", "shield", "full set of armor"]
                armor_type = random.choice(armors)
                description = f"I'm in need of a {armor_type}."
                
                # Add details based on NPC wealth and status
                if npc_wealth >= 8:
                    description += " It should be of the highest quality, offering excellent protection."
                elif npc_wealth >= 5:
                    description += " Good protection is important, but it needs to be reasonably priced."
                else:
                    description += " Basic protection is all I need, nothing fancy."
                    
                if npc_social_status >= 8:
                    description += " I would like my family crest incorporated into the design."
        
        elif business.business_type == BusinessType.TAILOR.value:
            # Similar implementation for tailor orders
            item_category = "clothing"
            description = "I need a new outfit for an upcoming event."
        
        else:
            # Generic order for other business types
            item_category = "product"
            description = f"I'd like to place an order for something from your {business.business_type} shop."
        
        # Calculate appropriate price based on NPC wealth and order complexity
        base_price = 20 + (npc_wealth * 10)  # 30-120 base price
        complexity_factor = random.uniform(0.8, 1.5)  # Random complexity
        offered_price = base_price * complexity_factor
        
        # Determine deadline
        urgency = npc_data.get("urgency", random.randint(1, 10))
        deadline_days = max(1, 10 - urgency)
        
        # Create order data
        order_data = {
            "requesting_npc_id": npc_id,
            "target_player_business_profile_id": business_id,
            "item_description_by_npc": description,
            "item_category_hint": item_category,
            "quantity": 1,  # Typically custom orders are for single items
            "offered_price_initial": offered_price,
            "deadline_preference_days": deadline_days,
            "deadline_date": datetime.utcnow() + timedelta(days=deadline_days),
            "status": CustomOrderStatus.AWAITING_PLAYER_REVIEW.value,
            "custom_data": {
                "npc_wealth_level": npc_wealth,
                "npc_social_status": npc_social_status,
                "npc_profession": npc_profession,
                "complexity_factor": complexity_factor,
                "generated_order": True
            }
        }
        
        # Create the order
        custom_order = create_custom_order(db, order_data)
        
        self.logger.info(f"Generated custom order from NPC {npc_id} for business {business_id}")
        
        return custom_order
    
    def process_npc_satisfaction_impact(
        self,
        db: Session,
        business_id: str,
        npc_id: str,
        interaction_type: str,
        satisfaction_rating: int,
        interaction_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process the impact of NPC satisfaction with a business interaction.
        
        Args:
            db: Database session
            business_id: Business ID
            npc_id: NPC ID
            interaction_type: Type of interaction
            satisfaction_rating: Satisfaction rating (1-5)
            interaction_details: Details of the interaction
            
        Returns:
            Dictionary with impact results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Calculate reputation impact
        base_impact = (satisfaction_rating - 3) / 10.0  # -0.2 to +0.2
        
        # Adjust based on interaction type
        if interaction_type == "custom_order":
            # Custom orders have bigger impact
            impact_multiplier = 1.5
            reputation_type = "quality_reputation"
        elif interaction_type == "purchase":
            impact_multiplier = 1.0
            reputation_type = "service_reputation"
        elif interaction_type == "negotiation":
            impact_multiplier = 1.2
            reputation_type = "price_reputation"
        else:
            impact_multiplier = 1.0
            reputation_type = "overall_reputation"
        
        # Calculate final impact
        reputation_impact = base_impact * impact_multiplier
        
        # Apply to business reputation
        reputation = business.reputation or {}
        
        if reputation_type in reputation:
            old_value = reputation[reputation_type]
            reputation[reputation_type] = min(10, max(1, old_value + reputation_impact))
        
        if "overall_reputation" in reputation:
            old_overall = reputation["overall_reputation"]
            # Overall reputation is affected less
            reputation["overall_reputation"] = min(10, max(1, old_overall + (reputation_impact / 2)))
        
        # Update business reputation
        update_business(db, business_id, {"reputation": reputation})
        
        # Track NPC relationship
        custom_data = business.custom_data or {}
        npc_relationships = custom_data.get("npc_relationships", {})
        
        if npc_id not in npc_relationships:
            npc_relationships[npc_id] = {
                "satisfaction": satisfaction_rating,
                "interaction_count": 1,
                "last_interaction": datetime.utcnow().isoformat(),
                "interaction_history": []
            }
        else:
            # Update existing relationship
            old_satisfaction = npc_relationships[npc_id]["satisfaction"]
            # New satisfaction is weighted average (30% new, 70% history)
            new_satisfaction = (old_satisfaction * 0.7) + (satisfaction_rating * 0.3)
            
            npc_relationships[npc_id]["satisfaction"] = new_satisfaction
            npc_relationships[npc_id]["interaction_count"] += 1
            npc_relationships[npc_id]["last_interaction"] = datetime.utcnow().isoformat()
        
        # Add to interaction history
        interaction_history = npc_relationships[npc_id].get("interaction_history", [])
        interaction_history.append({
            "date": datetime.utcnow().isoformat(),
            "type": interaction_type,
            "satisfaction_rating": satisfaction_rating,
            "details": interaction_details
        })
        
        # Trim history if needed
        if len(interaction_history) > 10:
            interaction_history = interaction_history[-10:]  # Keep only most recent 10
            
        npc_relationships[npc_id]["interaction_history"] = interaction_history
        
        # Update NPC relationships
        custom_data["npc_relationships"] = npc_relationships
        update_business(db, business_id, {"custom_data": custom_data})
        
        # Result summary
        result = {
            "npc_id": npc_id,
            "interaction_type": interaction_type,
            "satisfaction_rating": satisfaction_rating,
            "reputation_impact": reputation_impact,
            "reputation_type": reputation_type,
            "new_npc_satisfaction": npc_relationships[npc_id]["satisfaction"],
            "interaction_count": npc_relationships[npc_id]["interaction_count"]
        }
        
        self.logger.info(f"Processed NPC {npc_id} satisfaction for business {business_id}: " +
                        f"Rating {satisfaction_rating}, Impact {reputation_impact:.2f}")
        
        return result
    
    # === EVENT INTEGRATIONS ===
    
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
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Process based on event type
        event_result = {
            "business_id": business_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "impacts": []
        }
        
        if event_type == "festival":
            # Festival events might increase customer traffic and sales
            event_result["impacts"] = self._handle_festival_event(db, business, event_data)
        
        elif event_type == "disaster":
            # Disaster events might damage inventory or property
            event_result["impacts"] = self._handle_disaster_event(db, business, event_data)
        
        elif event_type == "competition":
            # Competition events might affect prices or reputation
            event_result["impacts"] = self._handle_competition_event(db, business, event_data)
        
        elif event_type == "guild_inspection":
            # Guild inspections might affect reputation or status
            event_result["impacts"] = self._handle_guild_inspection_event(db, business, event_data)
        
        elif event_type == "vip_customer":
            # VIP customer events might create special orders and reputation opportunities
            event_result["impacts"] = self._handle_vip_customer_event(db, business, event_data)
        
        else:
            # Unknown event type
            event_result["impacts"] = [{"type": "unknown_event", "impact": "none"}]
        
        # Record event in business history
        custom_data = business.custom_data or {}
        event_history = custom_data.get("event_history", [])
        
        event_history.append({
            "date": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "event_data": event_data,
            "impacts": event_result["impacts"]
        })
        
        custom_data["event_history"] = event_history
        update_business(db, business_id, {"custom_data": custom_data})
        
        self.logger.info(f"Triggered {event_type} event for business {business_id}")
        
        return event_result
    
    def _handle_festival_event(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle a festival event for a business."""
        # In a real implementation, this would have more detailed logic
        # For now, return a simple impact
        return [{
            "type": "increased_customer_traffic",
            "magnitude": event_data.get("magnitude", 1.0),
            "duration_days": event_data.get("duration_days", 3)
        }]
    
    def _handle_disaster_event(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle a disaster event for a business."""
        # In a real implementation, this would have more detailed logic
        # For now, return a simple impact
        return [{
            "type": "property_damage",
            "severity": event_data.get("severity", 0.5),
            "repair_cost": event_data.get("repair_cost", 100.0)
        }]
    
    def _handle_competition_event(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle a competition event for a business."""
        # In a real implementation, this would have more detailed logic
        # For now, return a simple impact
        return [{
            "type": "price_pressure",
            "magnitude": event_data.get("magnitude", 0.5),
            "duration_days": event_data.get("duration_days", 7)
        }]
    
    def _handle_guild_inspection_event(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle a guild inspection event for a business."""
        # In a real implementation, this would have more detailed logic
        # For now, return a simple impact
        inspection_passed = event_data.get("result", "passed") == "passed"
        return [{
            "type": "guild_standing_change",
            "change": 0.5 if inspection_passed else -1.0
        }]
    
    def _handle_vip_customer_event(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle a VIP customer event for a business."""
        # In a real implementation, this would have more detailed logic
        # For now, return a simple impact
        return [{
            "type": "reputation_opportunity",
            "potential_gain": event_data.get("potential_gain", 1.0),
            "vip_name": event_data.get("vip_name", "Important Person")
        }]