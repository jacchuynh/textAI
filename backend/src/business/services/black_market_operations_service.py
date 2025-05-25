"""
Black Market Operations Service

This module provides functionality for black market operations, including
finding contacts, conducting illicit trades, and managing underworld reputation.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.src.business.models.illicit_models import (
    IllicitItemCategory, IllicitServiceType, UnderworldRole,
    CriminalFaction, BlackMarketTransaction, RegionalHeatLevel,
    HiddenLocation, PlayerCriminalRecord
)
from backend.src.business.models.illicit_db_models import (
    DBBlackMarketTransaction, DBRegionalHeatLevel,
    DBHiddenLocation, DBPlayerCriminalRecord
)
from backend.src.business.crud import get_business

logger = logging.getLogger(__name__)

class BlackMarketOperationsService:
    """Service for black market operations."""
    
    def __init__(self):
        """Initialize the black market operations service."""
        self.logger = logging.getLogger("BlackMarketOperationsService")
    
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
        # Get player criminal record
        criminal_record = self._get_or_create_criminal_record(db, player_id)
        
        # Get regional heat level
        heat_level = self._get_or_create_heat_level(db, location_id)
        
        # Calculate base success chance
        base_success = 0.5  # 50% base chance
        
        # Adjust based on player notoriety and regional heat
        if criminal_record.notoriety > 3.0:
            # Known criminal has better connections
            base_success += (criminal_record.notoriety / 20)  # Up to +0.5 for max notoriety
        else:
            # Novice might not know where to look
            base_success -= 0.1
            
        # Regional heat affects difficulty
        if heat_level.current_heat > 7.0:
            # High heat means contacts are laying low
            base_success -= 0.2
        elif heat_level.current_heat < 3.0:
            # Low heat means more open operations
            base_success += 0.1
            
        # Authority presence makes it harder
        base_success -= (heat_level.authority_presence / 50)  # Up to -0.2
        
        # Check for known hidden locations which helps greatly
        hidden_locations = db.query(DBHiddenLocation).filter(
            DBHiddenLocation.region_id == location_id,
            DBHiddenLocation.known_to_player_ids.contains([player_id])
        ).all()
        
        if hidden_locations:
            base_success += 0.3
            
        # If looking for a specific service, adjust chance
        if desired_service_type:
            # Some services are rarer than others
            service_rarity = {
                IllicitServiceType.FENCE.value: 0.1,  # Common
                IllicitServiceType.INFORMATION_BROKER.value: 0.05,  # Common
                IllicitServiceType.SMUGGLING.value: 0.0,  # Average
                IllicitServiceType.FORGERY.value: -0.05,  # Uncommon
                IllicitServiceType.MONEY_LAUNDERING.value: -0.1,  # Rare
                IllicitServiceType.UNLICENSED_MAGIC.value: -0.15,  # Very rare
                IllicitServiceType.ASSASSINATION.value: -0.2  # Extremely rare
            }
            base_success += service_rarity.get(desired_service_type, 0.0)
        
        # Cap success chance
        final_success_chance = max(0.05, min(0.95, base_success))
        
        # Roll for success
        if random.random() <= final_success_chance:
            # Success - generate a contact
            contact_npc = self._generate_black_market_contact(
                db, location_id, desired_service_type
            )
            
            # Slightly increase notoriety for successful networking
            self._update_criminal_record(
                db, 
                player_id, 
                {"notoriety": criminal_record.notoriety + 0.1}
            )
            
            return {
                "success": True,
                "contact": contact_npc,
                "message": "You've found a contact in the shadows.",
                "risk_taken": 1.0 - final_success_chance
            }
        else:
            # Failure - determine if there are consequences
            risk_of_authority_attention = 0.2 + (heat_level.current_heat / 20)
            authority_noticed = random.random() <= risk_of_authority_attention
            
            # Increase regional heat slightly
            self._update_heat_level(
                db,
                location_id,
                {"current_heat": heat_level.current_heat + 0.2}
            )
            
            if authority_noticed:
                # Authorities became suspicious
                self._update_criminal_record(
                    db,
                    player_id,
                    {
                        "notoriety": criminal_record.notoriety + 0.2,
                        "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [location_id]))
                    }
                )
                
                return {
                    "success": False,
                    "message": "Your inquiries have drawn unwanted attention. A guard seems to be watching you.",
                    "consequences": "authority_suspicion",
                    "risk_taken": 1.0 - final_success_chance
                }
            else:
                return {
                    "success": False,
                    "message": "You can't seem to find anyone willing to talk about such matters here.",
                    "risk_taken": 1.0 - final_success_chance
                }
    
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
        # Validate parameters
        if not location_id and not business_id:
            raise ValueError("Either location_id or business_id must be provided")
            
        # If business_id is provided, get the business and use its location
        if business_id:
            business = get_business(db, business_id)
            if not business:
                raise ValueError(f"Business {business_id} not found")
            if business.player_character_id != player_id:
                raise ValueError("You don't own this business")
            location_id = business.location_id
        
        # Get player criminal record
        criminal_record = self._get_or_create_criminal_record(db, player_id)
        
        # Get regional heat level
        heat_level = self._get_or_create_heat_level(db, location_id)
        
        # Calculate base detection risk
        base_detection_risk = 0.2  # 20% base risk
        
        # Adjust based on various factors
        # Authority presence is a major factor
        base_detection_risk += (heat_level.authority_presence / 20)  # Up to +0.5
        
        # High regional heat increases risk
        base_detection_risk += (heat_level.current_heat / 25)  # Up to +0.4
        
        # Player notoriety can help or hurt
        if criminal_record.notoriety > 5.0:
            # Well-known criminals attract more attention
            base_detection_risk += 0.1
        elif criminal_record.notoriety > 2.0:
            # Some experience helps
            base_detection_risk -= 0.05
            
        # Larger trades are riskier
        if quantity > 10:
            base_detection_risk += 0.2
        elif quantity > 5:
            base_detection_risk += 0.1
        
        # Business provides cover
        if business_id:
            base_detection_risk -= 0.15
            
            # Check business security measures
            business_illicit_op = self._get_business_illicit_operation(db, business_id)
            if business_illicit_op:
                # Security measures reduce risk
                base_detection_risk -= (business_illicit_op.security_level / 50)  # Up to -0.2
        
        # Disguise helps
        if criminal_record.current_disguise_effectiveness > 0:
            base_detection_risk -= criminal_record.current_disguise_effectiveness / 2
            
        # Item category affects risk
        category = item_to_buy_or_sell.get("category", "")
        category_risk_modifier = {
            IllicitItemCategory.STOLEN.value: 0.05,  # Slightly risky
            IllicitItemCategory.CONTRABAND.value: 0.1,  # Moderately risky
            IllicitItemCategory.FORBIDDEN_ARTIFACT.value: 0.2,  # Very risky
            IllicitItemCategory.ILLEGAL_SUBSTANCE.value: 0.15,  # Quite risky
            IllicitItemCategory.COUNTERFEIT.value: 0.1,  # Moderately risky
            IllicitItemCategory.SMUGGLED.value: 0.05  # Slightly risky
        }
        base_detection_risk += category_risk_modifier.get(category, 0.0)
        
        # Cap detection risk
        final_detection_risk = max(0.05, min(0.95, base_detection_risk))
        
        # Calculate price based on market factors
        item_id = item_to_buy_or_sell.get("item_id", "")
        base_price = item_to_buy_or_sell.get("base_price", 0.0)
        
        # Black market has different pricing
        if is_buying:
            # Player buying - markup
            price_modifier = 1.5 + (heat_level.current_heat / 20)  # 150-200% of base price
            
            # Notorious players might get better deals
            if criminal_record.notoriety > 5.0:
                price_modifier -= 0.1
        else:
            # Player selling - discount
            price_modifier = 0.6 - (heat_level.current_heat / 50)  # 40-60% of base price
            
            # Notorious players might get better deals
            if criminal_record.notoriety > 5.0:
                price_modifier += 0.1
        
        # Calculate final price
        unit_price = base_price * price_modifier
        total_price = unit_price * quantity
        
        # Record the transaction
        transaction_id = str(uuid4())
        transaction = DBBlackMarketTransaction(
            id=transaction_id,
            business_id=business_id,
            player_id=player_id,
            contact_npc_id=contact_npc_id,
            transaction_type="buy" if is_buying else "sell",
            item_id=item_id,
            quantity=quantity,
            total_price=total_price,
            location_id=location_id,
            risk_taken=final_detection_risk,
            was_detected=False,  # Will be updated if detected
            custom_data={
                "item_name": item_to_buy_or_sell.get("name", ""),
                "item_category": category,
                "unit_price": unit_price
            }
        )
        db.add(transaction)
        
        # Determine if the transaction is detected
        is_detected = random.random() <= final_detection_risk
        
        if is_detected:
            # Transaction was detected by authorities
            transaction.was_detected = True
            
            # Increase regional heat
            self._update_heat_level(
                db,
                location_id,
                {
                    "current_heat": heat_level.current_heat + 0.5,
                    "recent_incidents": heat_level.recent_incidents + 1
                }
            )
            
            # Update player criminal record
            self._update_criminal_record(
                db,
                player_id,
                {
                    "notoriety": criminal_record.notoriety + 0.5,
                    "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [location_id])),
                    "known_crimes": criminal_record.known_crimes + [{
                        "date": datetime.utcnow().isoformat(),
                        "type": "illegal_trading",
                        "location_id": location_id,
                        "details": {
                            "item": item_to_buy_or_sell.get("name", ""),
                            "quantity": quantity,
                            "through_business": business_id is not None
                        }
                    }]
                }
            )
            
            # Determine consequences
            consequence_roll = random.random()
            
            if consequence_roll < 0.2:
                # Minor - warning or small fine
                consequence = {
                    "type": "warning" if consequence_roll < 0.1 else "fine",
                    "severity": "minor",
                    "details": "A guard noticed the suspicious transaction" if consequence_roll < 0.1 else f"You've been fined {total_price * 0.2} gold for suspicious activity"
                }
            elif consequence_roll < 0.6:
                # Moderate - larger fine, item confiscation
                consequence = {
                    "type": "fine_and_confiscation",
                    "severity": "moderate",
                    "details": f"Guards confiscated the goods and issued a fine of {total_price * 0.5} gold"
                }
            else:
                # Severe - item confiscation, large fine, possible arrest
                consequence = {
                    "type": "arrest_attempt",
                    "severity": "severe",
                    "details": "Guards are attempting to arrest you for illegal trading"
                }
            
            # Update transaction with consequence
            transaction.custom_data["consequence"] = consequence
            
            result = {
                "success": False,
                "transaction_id": transaction_id,
                "message": "The transaction was detected by authorities!",
                "detected": True,
                "consequence": consequence,
                "risk_taken": final_detection_risk
            }
        else:
            # Successful transaction
            
            # Slightly increase regional heat
            self._update_heat_level(
                db,
                location_id,
                {"current_heat": heat_level.current_heat + 0.1}
            )
            
            # Slightly increase player notoriety
            self._update_criminal_record(
                db,
                player_id,
                {"notoriety": criminal_record.notoriety + 0.2}
            )
            
            result = {
                "success": True,
                "transaction_id": transaction_id,
                "item_id": item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "message": f"Successfully {'purchased' if is_buying else 'sold'} {quantity} {item_to_buy_or_sell.get('name', '')}",
                "detected": False,
                "risk_taken": final_detection_risk
            }
        
        db.commit()
        return result
    
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
        # Get player criminal record
        criminal_record = self._get_or_create_criminal_record(db, player_id)
        
        # Get current faction relationship or default to neutral (0.0)
        current_relationship = criminal_record.faction_relationships.get(faction_id, 0.0)
        
        # Calculate new relationship value
        new_relationship = max(-10.0, min(10.0, current_relationship + reputation_change))
        
        # Update faction relationships
        faction_relationships = criminal_record.faction_relationships.copy()
        faction_relationships[faction_id] = new_relationship
        
        # Update criminal record
        self._update_criminal_record(
            db,
            player_id,
            {"faction_relationships": faction_relationships}
        )
        
        # Determine relationship tier
        relationship_tier = self._get_relationship_tier(new_relationship)
        
        # Update player notoriety if significant change
        if abs(reputation_change) >= 0.5:
            notoriety_change = abs(reputation_change) / 5.0  # Smaller change to notoriety
            self._update_criminal_record(
                db,
                player_id,
                {"notoriety": criminal_record.notoriety + notoriety_change}
            )
        
        # Generate message based on change
        if reputation_change > 0:
            message = f"Your standing with the {faction_id.replace('_', ' ').title()} has improved."
        elif reputation_change < 0:
            message = f"Your standing with the {faction_id.replace('_', ' ').title()} has deteriorated."
        else:
            message = f"Your standing with the {faction_id.replace('_', ' ').title()} remains unchanged."
            
        return {
            "player_id": player_id,
            "faction_id": faction_id,
            "previous_relationship": current_relationship,
            "new_relationship": new_relationship,
            "relationship_tier": relationship_tier,
            "message": message,
            "action": action_description
        }
    
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
        # Get heat level
        heat_level = self._get_or_create_heat_level(db, location_id)
        
        # Count active investigations in the region
        active_investigations = db.query(DBAuthorityInvestigation).filter(
            DBAuthorityInvestigation.region_id == location_id,
            DBAuthorityInvestigation.status.in_([
                "initial", "ongoing", "gathering_evidence", "preparing_raid"
            ])
        ).count()
        
        # Update active investigations count
        if heat_level.active_investigations != active_investigations:
            self._update_heat_level(
                db,
                location_id,
                {"active_investigations": active_investigations}
            )
        
        # Determine patrol frequency based on heat and authority presence
        patrol_frequency = {
            "very_low": heat_level.current_heat < 2.0 and heat_level.authority_presence < 3,
            "low": heat_level.current_heat < 4.0 and heat_level.authority_presence < 5,
            "moderate": heat_level.current_heat < 6.0 or heat_level.authority_presence < 7,
            "high": heat_level.current_heat >= 6.0 or heat_level.authority_presence >= 7,
            "very_high": heat_level.current_heat >= 8.0 or heat_level.authority_presence >= 9
        }
        
        # Determine heat level description
        heat_description = "unknown"
        if heat_level.current_heat < 2.0:
            heat_description = "minimal"
        elif heat_level.current_heat < 4.0:
            heat_description = "low"
        elif heat_level.current_heat < 6.0:
            heat_description = "moderate"
        elif heat_level.current_heat < 8.0:
            heat_description = "high"
        else:
            heat_description = "extreme"
            
        # Generate a human-readable description
        description = f"The heat level in this area is {heat_description}. "
        
        if heat_level.authority_presence >= 8:
            description += "There is a heavy authority presence. "
        elif heat_level.authority_presence >= 5:
            description += "There is a moderate authority presence. "
        else:
            description += "Authority presence is minimal. "
            
        if active_investigations > 0:
            description += f"There {'is' if active_investigations == 1 else 'are'} {active_investigations} active investigation{'s' if active_investigations != 1 else ''} in the area."
        
        return {
            "location_id": location_id,
            "current_heat": heat_level.current_heat,
            "heat_description": heat_description,
            "authority_presence": heat_level.authority_presence,
            "active_investigations": active_investigations,
            "recent_incidents": heat_level.recent_incidents,
            "patrol_frequency": next(k for k, v in patrol_frequency.items() if v),
            "last_patrol_time": heat_level.last_patrol_time.isoformat() if heat_level.last_patrol_time else None,
            "description": description
        }
    
    def plan_smuggling_run(
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
        # Validate required details
        required_fields = ["route", "goods", "assigned_npcs"]
        for field in required_fields:
            if field not in details:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate route
        route = details["route"]
        if not isinstance(route, dict) or "from" not in route or "to" not in route:
            raise ValueError("Route must specify 'from' and 'to' locations")
            
        # If business_id is provided, validate ownership
        if business_id:
            business = get_business(db, business_id)
            if not business:
                raise ValueError(f"Business {business_id} not found")
            if business.player_character_id != player_id:
                raise ValueError("You don't own this business")
        
        # Get player criminal record
        criminal_record = self._get_or_create_criminal_record(db, player_id)
        
        # Get heat levels for both locations
        origin_heat = self._get_or_create_heat_level(db, route["from"])
        destination_heat = self._get_or_create_heat_level(db, route["to"])
        
        # Calculate base risk
        base_risk = 0.3  # 30% base risk
        
        # Heat at both locations affects risk
        base_risk += (origin_heat.current_heat / 25)  # Up to +0.4
        base_risk += (destination_heat.current_heat / 25)  # Up to +0.4
        
        # Authority presence affects risk
        base_risk += (origin_heat.authority_presence / 30)  # Up to +0.33
        base_risk += (destination_heat.authority_presence / 30)  # Up to +0.33
        
        # Player notoriety helps with smuggling expertise
        if criminal_record.notoriety > 5.0:
            base_risk -= 0.15
        elif criminal_record.notoriety > 2.0:
            base_risk -= 0.05
            
        # Business provides resources and cover
        if business_id:
            base_risk -= 0.1
            
            # Check business illicit operations
            business_illicit_op = self._get_business_illicit_operation(db, business_id)
            if business_illicit_op:
                # Security measures reduce risk
                base_risk -= (business_illicit_op.security_level / 40)  # Up to -0.25
        
        # NPCs quality affects risk (would need NPC service to check skills)
        assigned_npcs = details["assigned_npcs"]
        if len(assigned_npcs) > 3:
            base_risk -= 0.1  # More NPCs helps
            
        # Goods quantity and value affects risk
        goods = details["goods"]
        total_quantity = sum(goods.values())
        
        if total_quantity > 20:
            base_risk += 0.2  # Large shipments are riskier
        elif total_quantity > 10:
            base_risk += 0.1
            
        # Calculate estimated completion time
        # Base time plus adjustments for distance and quantity
        base_days = 1
        distance_factor = details.get("distance_days", 1)
        quantity_factor = max(1, total_quantity / 10)
        
        total_days = base_days + distance_factor + (quantity_factor * 0.5)
        
        # Calculate estimated profit potential
        # This would use economic data in a real implementation
        base_profit_margin = 0.4  # 40% profit margin
        
        # Higher risk should mean higher reward
        profit_margin = base_profit_margin + (base_risk * 0.5)
        
        # Calculate total value and profit
        total_value = details.get("total_value", 1000.0)  # Default if not provided
        estimated_profit = total_value * profit_margin
        
        # Create smuggling operation
        operation_id = str(uuid4())
        
        start_date = datetime.utcnow()
        estimated_completion_date = start_date + timedelta(days=total_days)
        
        operation = DBSmugglingOperation(
            id=operation_id,
            business_id=business_id,
            player_id=player_id,
            route=route,
            goods=goods,
            assigned_npcs=assigned_npcs,
            risk_assessment=max(0.05, min(0.95, base_risk)),
            start_date=start_date,
            estimated_completion_date=estimated_completion_date,
            status="planning",
            profit_potential=estimated_profit,
            custom_data={
                "origin_heat": origin_heat.current_heat,
                "destination_heat": destination_heat.current_heat,
                "total_value": total_value,
                "profit_margin": profit_margin,
                "planned_by": player_id
            }
        )
        
        db.add(operation)
        db.commit()
        
        # Slightly increase player notoriety for planning smuggling
        self._update_criminal_record(
            db,
            player_id,
            {"notoriety": criminal_record.notoriety + 0.3}
        )
        
        return {
            "operation_id": operation_id,
            "player_id": player_id,
            "business_id": business_id,
            "route": route,
            "start_date": start_date.isoformat(),
            "estimated_completion_date": estimated_completion_date.isoformat(),
            "estimated_days": total_days,
            "risk_assessment": operation.risk_assessment,
            "goods": goods,
            "total_quantity": total_quantity,
            "assigned_npcs": assigned_npcs,
            "profit_potential": estimated_profit,
            "message": f"Smuggling operation planned from {route['from']} to {route['to']}. Estimated completion in {total_days:.1f} days."
        }
    
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
        # Get the operation
        operation = db.query(DBSmugglingOperation).filter(
            DBSmugglingOperation.id == operation_id
        ).first()
        
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")
            
        # Verify player ownership
        if operation.player_id != player_id:
            raise ValueError("This is not your smuggling operation")
            
        # Check operation status
        if operation.status != "planning":
            raise ValueError(f"Operation is already {operation.status}")
        
        # Update operation status
        operation.status = "in_progress"
        db.commit()
        
        # Get player criminal record
        criminal_record = self._get_or_create_criminal_record(db, player_id)
        
        # Get latest heat levels for both locations
        origin_heat = self._get_or_create_heat_level(db, operation.route["from"])
        destination_heat = self._get_or_create_heat_level(db, operation.route["to"])
        
        # Calculate success chance based on risk assessment and current conditions
        base_success = 1.0 - operation.risk_assessment
        
        # If heat has changed since planning, adjust success chance
        original_origin_heat = operation.custom_data.get("origin_heat", origin_heat.current_heat)
        original_destination_heat = operation.custom_data.get("destination_heat", destination_heat.current_heat)
        
        heat_change_factor = (
            (original_origin_heat - origin_heat.current_heat) / 20 +
            (original_destination_heat - destination_heat.current_heat) / 20
        )
        
        # Positive heat_change_factor means heat decreased (good)
        # Negative means heat increased (bad)
        final_success_chance = max(0.05, min(0.95, base_success + heat_change_factor))
        
        # Roll for success
        success_roll = random.random()
        operation_succeeded = success_roll <= final_success_chance
        
        # Determine operation outcome
        if operation_succeeded:
            # Successful smuggling
            operation.status = "completed"
            operation.actual_completion_date = datetime.utcnow()
            
            # Calculate actual profit
            profit_variation = random.uniform(0.8, 1.2)  # 80-120% of estimated profit
            actual_profit = operation.profit_potential * profit_variation
            
            operation.custom_data["actual_profit"] = actual_profit
            operation.outcome_notes = "Smuggling completed successfully."
            
            # Increase player notoriety
            self._update_criminal_record(
                db,
                player_id,
                {"notoriety": criminal_record.notoriety + 0.5}
            )
            
            # Record successful smuggling in criminal record
            known_crimes = criminal_record.known_crimes.copy()
            known_crimes.append({
                "date": datetime.utcnow().isoformat(),
                "type": "smuggling",
                "detected": False,
                "location_ids": [operation.route["from"], operation.route["to"]],
                "details": {
                    "operation_id": operation_id,
                    "goods_quantity": sum(operation.goods.values()),
                    "profit": actual_profit
                }
            })
            
            self._update_criminal_record(
                db,
                player_id,
                {"known_crimes": known_crimes}
            )
            
            result = {
                "success": True,
                "operation_id": operation_id,
                "status": "completed",
                "actual_profit": actual_profit,
                "message": f"Smuggling operation completed successfully. Profit: {actual_profit:.2f} gold.",
                "goods_delivered": operation.goods
            }
        else:
            # Failed smuggling - determine if intercepted or just failed
            interception_chance = (1.0 - final_success_chance) * 0.7  # 70% of failure is interception
            
            if success_roll <= final_success_chance + interception_chance:
                # Intercepted by authorities
                operation.status = "intercepted"
                operation.actual_completion_date = datetime.utcnow()
                operation.outcome_notes = "Smuggling operation intercepted by authorities."
                
                # Increase player notoriety significantly
                self._update_criminal_record(
                    db,
                    player_id,
                    {
                        "notoriety": criminal_record.notoriety + 1.0,
                        "times_caught": criminal_record.times_caught + 1
                    }
                )
                
                # Record failed smuggling in criminal record
                known_crimes = criminal_record.known_crimes.copy()
                known_crimes.append({
                    "date": datetime.utcnow().isoformat(),
                    "type": "smuggling",
                    "detected": True,
                    "location_ids": [operation.route["from"], operation.route["to"]],
                    "details": {
                        "operation_id": operation_id,
                        "interception_point": "origin" if random.random() < 0.5 else "route",
                        "goods_quantity": sum(operation.goods.values())
                    }
                })
                
                self._update_criminal_record(
                    db,
                    player_id,
                    {"known_crimes": known_crimes}
                )
                
                # Increase heat in both regions
                self._update_heat_level(
                    db,
                    operation.route["from"],
                    {
                        "current_heat": origin_heat.current_heat + 1.0,
                        "recent_incidents": origin_heat.recent_incidents + 1
                    }
                )
                
                self._update_heat_level(
                    db,
                    operation.route["to"],
                    {
                        "current_heat": destination_heat.current_heat + 0.5,
                        "recent_incidents": destination_heat.recent_incidents + 1
                    }
                )
                
                # Determine consequences
                consequence_roll = random.random()
                
                if consequence_roll < 0.3:
                    # Minor consequences - confiscation and small fine
                    consequence = {
                        "type": "confiscation_and_fine",
                        "severity": "minor",
                        "fine_amount": operation.profit_potential * 0.5,
                        "details": "Goods confiscated and a fine issued"
                    }
                elif consequence_roll < 0.7:
                    # Moderate consequences - confiscation, larger fine
                    consequence = {
                        "type": "confiscation_and_fine",
                        "severity": "moderate",
                        "fine_amount": operation.profit_potential * 1.0,
                        "details": "Goods confiscated and a substantial fine issued"
                    }
                else:
                    # Severe consequences - confiscation, large fine, possible imprisonment
                    consequence = {
                        "type": "confiscation_and_arrest",
                        "severity": "severe",
                        "fine_amount": operation.profit_potential * 1.5,
                        "imprisonment_days": random.randint(3, 10),
                        "details": "Goods confiscated, heavy fine, and imprisonment"
                    }
                
                operation.custom_data["consequence"] = consequence
                
                result = {
                    "success": False,
                    "operation_id": operation_id,
                    "status": "intercepted",
                    "message": "Smuggling operation intercepted by authorities!",
                    "consequence": consequence
                }
            else:
                # Failed but not intercepted (e.g., goods lost, NPC betrayal)
                operation.status = "failed"
                operation.actual_completion_date = datetime.utcnow()
                
                # Determine failure reason
                failure_reasons = [
                    "The goods were lost during transport.",
                    "One of your hired smugglers disappeared with the goods.",
                    "The contact at the destination refused to receive the shipment.",
                    "The goods were damaged beyond usability during transport."
                ]
                failure_reason = random.choice(failure_reasons)
                operation.outcome_notes = failure_reason
                
                # Small increase in notoriety
                self._update_criminal_record(
                    db,
                    player_id,
                    {"notoriety": criminal_record.notoriety + 0.2}
                )
                
                result = {
                    "success": False,
                    "operation_id": operation_id,
                    "status": "failed",
                    "message": f"Smuggling operation failed. {failure_reason}",
                    "goods_lost": operation.goods
                }
        
        db.commit()
        return result
    
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
        # Get player criminal record
        criminal_record = self._get_or_create_criminal_record(db, player_id)
        
        # Get regional heat level
        heat_level = self._get_or_create_heat_level(db, region_id)
        
        # Calculate base discovery chance
        base_discovery = 0.3  # 30% base chance
        
        # Adjust based on player notoriety
        if criminal_record.notoriety > 5.0:
            # Well-connected criminals know more
            base_discovery += 0.3
        elif criminal_record.notoriety > 2.0:
            # Some criminal connections help
            base_discovery += 0.15
            
        # Regional heat affects availability
        if heat_level.current_heat > 7.0:
            # High heat means locations are more hidden
            base_discovery -= 0.2
        elif heat_level.current_heat < 3.0:
            # Low heat means more open operations
            base_discovery += 0.1
            
        # Authority presence makes it harder
        base_discovery -= (heat_level.authority_presence / 30)
        
        # Search parameters can help
        if search_parameters:
            if "information_from_npc" in search_parameters:
                base_discovery += 0.3
            if "specific_faction" in search_parameters:
                base_discovery += 0.2
            if "previous_knowledge" in search_parameters:
                base_discovery += 0.1
        
        # Cap discovery chance
        final_discovery_chance = max(0.05, min(0.95, base_discovery))
        
        # Roll for discovery
        if random.random() <= final_discovery_chance:
            # Success - generate or find a hidden location
            # Check if player already knows any locations in this region
            known_locations = db.query(DBHiddenLocation).filter(
                DBHiddenLocation.region_id == region_id,
                DBHiddenLocation.known_to_player_ids.contains([player_id])
            ).all()
            
            # If player knows all locations in region, generate a new one
            all_locations = db.query(DBHiddenLocation).filter(
                DBHiddenLocation.region_id == region_id
            ).all()
            
            if len(known_locations) >= len(all_locations):
                # Generate a new location
                location = self._generate_hidden_location(db, region_id, player_id, search_parameters)
            else:
                # Find an existing location the player doesn't know
                unknown_locations = [loc for loc in all_locations if player_id not in loc.known_to_player_ids]
                location = random.choice(unknown_locations)
                
                # Add player to known_to_player_ids
                known_players = location.known_to_player_ids.copy()
                known_players.append(player_id)
                location.known_to_player_ids = known_players
                db.commit()
            
            # Slightly increase notoriety for finding hidden locations
            self._update_criminal_record(
                db,
                player_id,
                {"notoriety": criminal_record.notoriety + 0.2}
            )
            
            return {
                "success": True,
                "location_id": location.id,
                "name": location.name,
                "description": location.description,
                "type": location.type,
                "controlled_by_faction": location.controlled_by_faction,
                "available_services": location.available_services,
                "message": f"You've discovered {location.name}, a hidden {location.type}."
            }
        else:
            # Failure - determine if there are consequences
            risk_of_authority_attention = 0.2 + (heat_level.current_heat / 20)
            authority_noticed = random.random() <= risk_of_authority_attention
            
            # Increase regional heat slightly
            self._update_heat_level(
                db,
                region_id,
                {"current_heat": heat_level.current_heat + 0.1}
            )
            
            if authority_noticed:
                # Authorities became suspicious
                self._update_criminal_record(
                    db,
                    player_id,
                    {
                        "notoriety": criminal_record.notoriety + 0.1,
                        "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [region_id]))
                    }
                )
                
                return {
                    "success": False,
                    "message": "Your search has drawn unwanted attention. Guards seem suspicious of your activities.",
                    "consequences": "authority_suspicion"
                }
            else:
                return {
                    "success": False,
                    "message": "You couldn't find any hidden locations in this area."
                }
    
    # === HELPER METHODS ===
    
    def _get_or_create_criminal_record(
        self,
        db: Session,
        player_id: str
    ) -> PlayerCriminalRecord:
        """Get or create a player's criminal record."""
        record = db.query(DBPlayerCriminalRecord).filter(
            DBPlayerCriminalRecord.player_id == player_id
        ).first()
        
        if not record:
            # Create new record
            record = DBPlayerCriminalRecord(
                id=str(uuid4()),
                player_id=player_id,
                notoriety=0.0,
                known_crimes=[],
                current_bounty=0.0,
                times_caught=0,
                times_escaped=0,
                faction_relationships={},
                current_disguise_effectiveness=0.0,
                suspected_by_regions=[]
            )
            db.add(record)
            db.commit()
        
        # Convert to Pydantic model
        return PlayerCriminalRecord(
            player_id=record.player_id,
            notoriety=record.notoriety,
            known_crimes=record.known_crimes,
            current_bounty=record.current_bounty,
            times_caught=record.times_caught,
            times_escaped=record.times_escaped,
            faction_relationships=record.faction_relationships,
            current_disguise_effectiveness=record.current_disguise_effectiveness,
            suspected_by_regions=record.suspected_by_regions
        )
    
    def _update_criminal_record(
        self,
        db: Session,
        player_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update a player's criminal record."""
        record = db.query(DBPlayerCriminalRecord).filter(
            DBPlayerCriminalRecord.player_id == player_id
        ).first()
        
        if not record:
            raise ValueError(f"Criminal record for player {player_id} not found")
            
        # Apply updates
        for key, value in updates.items():
            if hasattr(record, key):
                setattr(record, key, value)
                
        db.commit()
    
    def _get_or_create_heat_level(
        self,
        db: Session,
        location_id: str
    ) -> RegionalHeatLevel:
        """Get or create heat level for a region."""
        heat_level = db.query(DBRegionalHeatLevel).filter(
            DBRegionalHeatLevel.region_id == location_id
        ).first()
        
        if not heat_level:
            # Create new heat level
            heat_level = DBRegionalHeatLevel(
                id=str(uuid4()),
                region_id=location_id,
                current_heat=1.0,  # Starting heat
                authority_presence=5,  # Default presence
                recent_incidents=0,
                special_conditions={}
            )
            db.add(heat_level)
            db.commit()
        
        # Convert to Pydantic model
        return RegionalHeatLevel(
            region_id=heat_level.region_id,
            current_heat=heat_level.current_heat,
            authority_presence=heat_level.authority_presence,
            recent_incidents=heat_level.recent_incidents,
            last_patrol_time=heat_level.last_patrol_time,
            active_investigations=heat_level.active_investigations,
            special_conditions=heat_level.special_conditions
        )
    
    def _update_heat_level(
        self,
        db: Session,
        location_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update heat level for a region."""
        heat_level = db.query(DBRegionalHeatLevel).filter(
            DBRegionalHeatLevel.region_id == location_id
        ).first()
        
        if not heat_level:
            raise ValueError(f"Heat level for location {location_id} not found")
            
        # Apply updates
        for key, value in updates.items():
            if hasattr(heat_level, key):
                setattr(heat_level, key, value)
                
        db.commit()
    
    def _get_business_illicit_operation(
        self,
        db: Session,
        business_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get illicit operation for a business."""
        from backend.src.business.models.illicit_db_models import DBIllicitBusinessOperation
        
        operation = db.query(DBIllicitBusinessOperation).filter(
            DBIllicitBusinessOperation.business_id == business_id
        ).first()
        
        return operation
    
    def _generate_black_market_contact(
        self,
        db: Session,
        location_id: str,
        desired_service_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a black market contact NPC."""
        # This would normally use the NPC generation system
        # For now, generate a simple placeholder
        
        # Determine NPC role based on desired service
        role = UnderworldRole.FENCE.value  # Default
        
        if desired_service_type:
            service_to_role = {
                IllicitServiceType.FENCE.value: UnderworldRole.FENCE.value,
                IllicitServiceType.SMUGGLING.value: UnderworldRole.SMUGGLER.value,
                IllicitServiceType.FORGERY.value: UnderworldRole.FORGER.value,
                IllicitServiceType.UNLICENSED_MAGIC.value: UnderworldRole.ALCHEMIST.value,
                IllicitServiceType.INFORMATION_BROKER.value: UnderworldRole.SPY.value,
                IllicitServiceType.MONEY_LAUNDERING.value: UnderworldRole.FIXER.value,
                IllicitServiceType.ASSASSINATION.value: UnderworldRole.ASSASSIN.value
            }
            role = service_to_role.get(desired_service_type, UnderworldRole.FENCE.value)
            
        # Generate a name
        first_names = ["Krag", "Silda", "Vex", "Durga", "Zarn", "Nix", "Mira", "Thorn"]
        nicknames = ["Shadow", "Swift", "Silent", "Grim", "Sly", "Whisper", "Blade", "Fingers"]
        name = f"{random.choice(first_names)} '{random.choice(nicknames)}'"
        
        # Assign a faction
        faction = random.choice(list(CriminalFaction))
        
        # Generate contact details
        contact_id = f"npc_{str(uuid4())[:8]}"
        
        return {
            "id": contact_id,
            "name": name,
            "role": role,
            "faction": faction.value,
            "location_id": location_id,
            "description": f"A {role.replace('_', ' ')} with connections to the {faction.value.replace('_', ' ').title()}.",
            "services_offered": [desired_service_type] if desired_service_type else [],
            "trustworthiness": random.uniform(0.3, 0.8)
        }
    
    def _generate_hidden_location(
        self,
        db: Session,
        region_id: str,
        player_id: str,
        search_parameters: Optional[Dict[str, Any]] = None
    ) -> DBHiddenLocation:
        """Generate a hidden location for black market activities."""
        # Determine location type
        location_types = [
            "black_market",
            "smuggler_den",
            "thieves_hideout",
            "forbidden_shop",
            "underground_tavern",
            "secret_meeting_place"
        ]
        location_type = random.choice(location_types)
        
        # Determine controlling faction
        faction = None
        if random.random() < 0.7:  # 70% chance of faction control
            faction = random.choice(list(CriminalFaction))
        
        # Determine available services
        available_services = []
        service_count = random.randint(1, 4)
        for _ in range(service_count):
            service = random.choice(list(IllicitServiceType))
            if service.value not in available_services:
                available_services.append(service.value)
        
        # Generate name
        name_prefixes = ["Hidden", "Shadow", "Secret", "Dark", "Whisper", "Forgotten", "Cloaked"]
        name_suffixes = ["Haven", "Den", "Hideaway", "Refuge", "Sanctum", "Hollow", "Corner"]
        
        if location_type == "black_market":
            name = f"The {random.choice(name_prefixes)} Bazaar"
        elif location_type == "smuggler_den":
            name = f"The {random.choice(name_prefixes)} Harbor"
        elif location_type == "thieves_hideout":
            name = f"The {random.choice(name_prefixes)} {random.choice(name_suffixes)}"
        elif location_type == "forbidden_shop":
            name = f"The {random.choice(['Curious', 'Mysterious', 'Arcane', 'Forbidden'])} {random.choice(['Emporium', 'Shop', 'Store', 'Merchant'])}"
        elif location_type == "underground_tavern":
            name = f"The {random.choice(['Rusty', 'Broken', 'Silver', 'Crooked'])} {random.choice(['Dagger', 'Flagon', 'Goblet', 'Tankard'])}"
        else:
            name = f"The {random.choice(name_prefixes)} {random.choice(name_suffixes)}"
        
        # Generate description
        descriptions = {
            "black_market": "A bustling hidden marketplace where all manner of illicit goods change hands.",
            "smuggler_den": "A secretive location where smugglers gather to plan operations and trade contraband.",
            "thieves_hideout": "A well-hidden refuge where thieves and pickpockets fence their stolen goods.",
            "forbidden_shop": "A discreet establishment selling items that most legitimate merchants wouldn't touch.",
            "underground_tavern": "A clandestine tavern frequented by those who prefer to conduct business away from prying eyes.",
            "secret_meeting_place": "A hidden location used for clandestine meetings and exchanges."
        }
        
        # Create location
        location = DBHiddenLocation(
            id=str(uuid4()),
            name=name,
            description=descriptions.get(location_type, "A hidden location for illicit activities."),
            region_id=region_id,
            type=location_type,
            controlled_by_faction=faction.value if faction else None,
            access_difficulty=random.randint(3, 8),
            security_level=random.randint(2, 7),
            available_services=available_services,
            known_to_player_ids=[player_id],
            custom_data={}
        )
        
        db.add(location)
        db.commit()
        
        return location
    
    def _get_relationship_tier(self, relationship_value: float) -> str:
        """Get relationship tier based on value."""
        if relationship_value <= -8.0:
            return "mortal_enemy"
        elif relationship_value <= -5.0:
            return "enemy"
        elif relationship_value <= -2.0:
            return "hostile"
        elif relationship_value < 2.0:
            return "neutral"
        elif relationship_value < 5.0:
            return "friendly"
        elif relationship_value < 8.0:
            return "ally"
        else:
            return "trusted"