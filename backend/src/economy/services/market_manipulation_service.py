"""
Market Manipulation Service

This module provides functionalities for players and NPCs to manipulate
market conditions through various economic actions such as cornering markets,
spreading rumors, and other economic influence activities.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import random
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session

# Import models
from backend.src.economy.models.pydantic_models import MarketRegionInfo
from backend.src.economy.models.db_models import (
    DBMarketRegionInfo, DBLocation, DBItem, DBCharacter, DBShop
)

# Import Celery integration for async processing
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class MarketManipulationService:
    """
    Service for handling market manipulation activities in the game world.
    """
    
    def __init__(self):
        """Initialize the market manipulation service."""
        self.logger = logging.getLogger("MarketManipulationService")
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration for async operations
        self.celery_integration = NarrativeEngineCeleryIntegration()
        
        # Subscribe to relevant events
        self.event_bus.subscribe("market_manipulation_attempt", self._handle_manipulation_attempt)
        self.event_bus.subscribe("market_manipulation_detected", self._handle_manipulation_detected)
        self.event_bus.subscribe("rumor_spread", self._handle_rumor_spread)
    
    async def corner_market(self,
                         db: Session,
                         character_id: str,
                         region_id: str,
                         item_id: str,
                         investment_amount: float,
                         target_price_modifier: float = 1.5,
                         duration_days: int = 7,
                         async_processing: bool = True) -> Dict[str, Any]:
        """
        Attempt to corner the market for a specific item in a region.
        
        Args:
            db: Database session
            character_id: Character attempting the corner
            region_id: Target region
            item_id: Target item
            investment_amount: Amount of currency invested in cornering
            target_price_modifier: Target price increase (e.g., 1.5 = 50% increase)
            duration_days: How long the corner should last
            async_processing: Whether to process asynchronously
            
        Returns:
            Result of the market corner attempt
        """
        # Get the character
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {"error": f"Character {character_id} not found"}
        
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Get the item
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        if not item:
            return {"error": f"Item {item_id} not found"}
        
        # Check if character has enough currency
        if character.currency < investment_amount:
            return {"error": f"Character {character_id} does not have enough currency (has {character.currency}, needs {investment_amount})"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.corner_market_task",
                task_args=[character_id, region_id, item_id],
                task_kwargs={
                    "investment_amount": investment_amount,
                    "target_price_modifier": target_price_modifier,
                    "duration_days": duration_days
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "corner_market",
                "character_id": character_id,
                "region_id": region_id,
                "item_id": item_id,
                "investment_amount": investment_amount,
                "status": "processing",
                "message": "Market corner attempt dispatched for asynchronous processing"
            }
        
        # For synchronous processing, perform the corner here
        # This is a simplified implementation
        
        # Determine success chance based on investment and region size
        region_prosperity = region.prosperity_level
        region_size_factor = self._get_region_size_factor(db, region_id)
        
        # Calculate the cost to corner based on region size and prosperity
        corner_cost = item.base_price * region_size_factor * region_prosperity * 100
        
        # Calculate success chance
        success_chance = min(0.9, investment_amount / corner_cost)
        
        # Roll for success
        success = random.random() < success_chance
        
        if success:
            # Deduct currency from character
            character.currency -= investment_amount
            
            # Update region's price modifiers
            supply_demand_signals = region.supply_demand_signals or {}
            category_price_modifiers = region.category_price_modifiers or {}
            
            # Increase the supply/demand signal for this item (higher demand)
            current_signal = supply_demand_signals.get(item_id, 0.0)
            new_signal = min(1.0, current_signal + (target_price_modifier - 1.0))
            supply_demand_signals[item_id] = new_signal
            
            # Also affect the category
            current_category_signal = supply_demand_signals.get(item.category, 0.0)
            new_category_signal = min(1.0, current_category_signal + (target_price_modifier - 1.0) * 0.3)
            supply_demand_signals[item.category] = new_category_signal
            
            # Increase the category price modifier
            current_category_modifier = category_price_modifiers.get(item.category, 1.0)
            new_category_modifier = current_category_modifier * (1.0 + (target_price_modifier - 1.0) * 0.3)
            category_price_modifiers[item.category] = new_category_modifier
            
            # Update the region
            region.supply_demand_signals = supply_demand_signals
            region.category_price_modifiers = category_price_modifiers
            
            # Store the manipulation in custom_data
            custom_data = region.custom_data or {}
            manipulations = custom_data.get("market_manipulations", [])
            
            new_manipulation = {
                "type": "corner_market",
                "character_id": character_id,
                "item_id": item_id,
                "investment_amount": investment_amount,
                "target_price_modifier": target_price_modifier,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                "is_active": True
            }
            
            manipulations.append(new_manipulation)
            custom_data["market_manipulations"] = manipulations
            region.custom_data = custom_data
            
            # Commit changes
            db.commit()
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="market_manipulation_success",
                data={
                    "manipulation_type": "corner_market",
                    "character_id": character_id,
                    "region_id": region_id,
                    "item_id": item_id,
                    "item_name": item.name,
                    "investment_amount": investment_amount,
                    "price_impact": target_price_modifier,
                    "duration_days": duration_days,
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="market_manipulation_service"
            ))
            
            return {
                "action": "corner_market",
                "status": "success",
                "character_id": character_id,
                "region_id": region_id,
                "item_id": item_id,
                "item_name": item.name,
                "investment_amount": investment_amount,
                "price_impact": target_price_modifier,
                "duration_days": duration_days,
                "end_date": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                "success_chance": round(success_chance * 100, 1),
                "character_currency_remaining": character.currency
            }
        else:
            # Partial currency loss on failure
            lost_amount = investment_amount * 0.4
            character.currency -= lost_amount
            db.commit()
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="market_manipulation_failure",
                data={
                    "manipulation_type": "corner_market",
                    "character_id": character_id,
                    "region_id": region_id,
                    "item_id": item_id,
                    "item_name": item.name,
                    "investment_amount": investment_amount,
                    "lost_amount": lost_amount,
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="market_manipulation_service"
            ))
            
            return {
                "action": "corner_market",
                "status": "failure",
                "character_id": character_id,
                "region_id": region_id,
                "item_id": item_id,
                "item_name": item.name,
                "investment_amount": investment_amount,
                "lost_amount": lost_amount,
                "success_chance": round(success_chance * 100, 1),
                "character_currency_remaining": character.currency,
                "message": f"Failed to corner the market for {item.name} in {region.name}"
            }
    
    async def spread_market_rumor(self,
                              db: Session,
                              character_id: str,
                              region_id: str,
                              rumor_type: str,
                              target_item_id: Optional[str] = None,
                              target_category: Optional[str] = None,
                              investment_amount: float = 10.0,
                              async_processing: bool = True) -> Dict[str, Any]:
        """
        Spread a rumor to manipulate market prices.
        
        Args:
            db: Database session
            character_id: Character spreading the rumor
            region_id: Target region
            rumor_type: Type of rumor (shortage, surplus, quality_issue, etc.)
            target_item_id: Specific item targeted (optional)
            target_category: Item category targeted (optional)
            investment_amount: Amount invested in spreading the rumor
            async_processing: Whether to process asynchronously
            
        Returns:
            Result of the rumor attempt
        """
        # Validate input
        if not target_item_id and not target_category:
            return {"error": "Must specify either target_item_id or target_category"}
        
        # Get the character
        character = db.query(DBCharacter).filter(DBCharacter.id == character_id).first()
        if not character:
            return {"error": f"Character {character_id} not found"}
        
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Get the item if specified
        item = None
        if target_item_id:
            item = db.query(DBItem).filter(DBItem.id == target_item_id).first()
            if not item:
                return {"error": f"Item {target_item_id} not found"}
            target_category = item.category
        
        # Check if character has enough currency
        if character.currency < investment_amount:
            return {"error": f"Character {character_id} does not have enough currency (has {character.currency}, needs {investment_amount})"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.spread_market_rumor_task",
                task_args=[character_id, region_id, rumor_type],
                task_kwargs={
                    "target_item_id": target_item_id,
                    "target_category": target_category,
                    "investment_amount": investment_amount
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "spread_market_rumor",
                "character_id": character_id,
                "region_id": region_id,
                "rumor_type": rumor_type,
                "target_item_id": target_item_id,
                "target_category": target_category,
                "investment_amount": investment_amount,
                "status": "processing",
                "message": "Market rumor attempt dispatched for asynchronous processing"
            }
        
        # For synchronous processing, process the rumor here
        # This is a simplified implementation
        
        # Deduct currency from character
        character.currency -= investment_amount
        
        # Determine rumor effectiveness based on character's skills
        # In a real implementation, this would check social skills, reputation, etc.
        base_effectiveness = min(0.8, 0.3 + (investment_amount / 100))
        
        # Influence factors include whether it's an item or category
        # and whether the region is prosperous (more skeptical)
        influence_factor = 1.0
        if target_item_id:
            influence_factor *= 1.2  # More effective for specific items
        if region.prosperity_level > 0.7:
            influence_factor *= 0.8  # Prosperous regions are more skeptical
        
        # Calculate price effect based on rumor type
        price_effect = 0.0
        if rumor_type == "shortage":
            price_effect = 0.2 * base_effectiveness * influence_factor  # Prices increase
        elif rumor_type == "surplus":
            price_effect = -0.15 * base_effectiveness * influence_factor  # Prices decrease
        elif rumor_type == "quality_issue":
            price_effect = -0.25 * base_effectiveness * influence_factor  # Prices decrease significantly
        elif rumor_type == "high_demand":
            price_effect = 0.15 * base_effectiveness * influence_factor  # Prices increase
        else:
            price_effect = 0.1 * base_effectiveness * influence_factor  # Default mild increase
        
        # Update region's supply/demand signals
        supply_demand_signals = region.supply_demand_signals or {}
        
        if target_item_id:
            # Update specific item
            current_signal = supply_demand_signals.get(target_item_id, 0.0)
            new_signal = max(-1.0, min(1.0, current_signal + price_effect))
            supply_demand_signals[target_item_id] = new_signal
        
        # Always update category
        current_category_signal = supply_demand_signals.get(target_category, 0.0)
        category_effect = price_effect * 0.7  # Less impact on the entire category
        new_category_signal = max(-1.0, min(1.0, current_category_signal + category_effect))
        supply_demand_signals[target_category] = new_category_signal
        
        # Update the region
        region.supply_demand_signals = supply_demand_signals
        
        # Store the rumor in custom_data
        custom_data = region.custom_data or {}
        rumors = custom_data.get("market_rumors", [])
        
        new_rumor = {
            "type": rumor_type,
            "character_id": character_id,
            "target_item_id": target_item_id,
            "target_category": target_category,
            "investment_amount": investment_amount,
            "price_effect": price_effect,
            "start_date": datetime.utcnow().isoformat(),
            "duration_days": 3,  # Rumors last for 3 days by default
            "is_active": True
        }
        
        rumors.append(new_rumor)
        custom_data["market_rumors"] = rumors
        region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        target_name = item.name if item else f"all {target_category} items"
        self.event_bus.publish(Event(
            event_type="rumor_spread",
            data={
                "rumor_type": rumor_type,
                "character_id": character_id,
                "region_id": region_id,
                "target_item_id": target_item_id,
                "target_category": target_category,
                "target_name": target_name,
                "investment_amount": investment_amount,
                "price_effect": price_effect,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="market_manipulation_service"
        ))
        
        return {
            "action": "spread_market_rumor",
            "status": "success",
            "character_id": character_id,
            "region_id": region_id,
            "rumor_type": rumor_type,
            "target_name": target_name,
            "investment_amount": investment_amount,
            "price_effect": round(price_effect * 100, 1),
            "effectiveness": round(base_effectiveness * influence_factor * 100, 1),
            "duration_days": 3,
            "character_currency_remaining": character.currency
        }
    
    async def create_cartel(self,
                        db: Session,
                        leader_id: str,
                        member_ids: List[str],
                        region_id: str,
                        target_items: List[str],
                        investment_amount: float,
                        price_target: float,
                        duration_months: int = 3,
                        async_processing: bool = True) -> Dict[str, Any]:
        """
        Create a cartel to control prices of specific items.
        
        Args:
            db: Database session
            leader_id: Character leading the cartel
            member_ids: Other characters in the cartel
            region_id: Target region
            target_items: Items to control prices for
            investment_amount: Total investment amount
            price_target: Target price multiplier (e.g., 1.3 = 30% increase)
            duration_months: How long the cartel should last
            async_processing: Whether to process asynchronously
            
        Returns:
            Result of the cartel creation attempt
        """
        # Validate members
        all_members = [leader_id] + member_ids
        for member_id in all_members:
            character = db.query(DBCharacter).filter(DBCharacter.id == member_id).first()
            if not character:
                return {"error": f"Character {member_id} not found"}
        
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Validate items
        valid_items = []
        for item_id in target_items:
            item = db.query(DBItem).filter(DBItem.id == item_id).first()
            if item:
                valid_items.append(item_id)
        
        if not valid_items:
            return {"error": "No valid items specified for cartel control"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.create_cartel_task",
                task_args=[leader_id, region_id],
                task_kwargs={
                    "member_ids": member_ids,
                    "target_items": valid_items,
                    "investment_amount": investment_amount,
                    "price_target": price_target,
                    "duration_months": duration_months
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "create_cartel",
                "leader_id": leader_id,
                "member_count": len(all_members),
                "region_id": region_id,
                "target_items_count": len(valid_items),
                "investment_amount": investment_amount,
                "status": "processing",
                "message": "Cartel creation attempt dispatched for asynchronous processing"
            }
        
        # For synchronous processing, process the cartel creation here
        # This is a simplified implementation
        
        # Calculate per-member investment
        per_member_investment = investment_amount / len(all_members)
        
        # Check if all members have enough currency
        for member_id in all_members:
            character = db.query(DBCharacter).filter(DBCharacter.id == member_id).first()
            if character.currency < per_member_investment:
                return {"error": f"Character {member_id} does not have enough currency (has {character.currency}, needs {per_member_investment})"}
        
        # Deduct currency from all members
        for member_id in all_members:
            character = db.query(DBCharacter).filter(DBCharacter.id == member_id).first()
            character.currency -= per_member_investment
        
        # Calculate cartel strength based on members and investment
        member_count_factor = min(2.0, 1.0 + (len(all_members) - 1) * 0.1)
        investment_factor = min(2.0, 1.0 + (investment_amount / 1000))
        cartel_strength = member_count_factor * investment_factor
        
        # Calculate price effect
        max_price_effect = (price_target - 1.0) * cartel_strength
        actual_price_effect = min(max_price_effect, 0.5)  # Cap at 50% increase
        
        # Update region's price modifiers
        category_price_modifiers = region.category_price_modifiers or {}
        supply_demand_signals = region.supply_demand_signals or {}
        
        # Get affected categories
        affected_categories = set()
        for item_id in valid_items:
            item = db.query(DBItem).filter(DBItem.id == item_id).first()
            affected_categories.add(item.category)
            
            # Update supply/demand signal for specific item
            current_signal = supply_demand_signals.get(item_id, 0.0)
            new_signal = min(1.0, current_signal + actual_price_effect)
            supply_demand_signals[item_id] = new_signal
        
        # Update category price modifiers
        for category in affected_categories:
            current_modifier = category_price_modifiers.get(category, 1.0)
            new_modifier = current_modifier * (1.0 + actual_price_effect * 0.5)
            category_price_modifiers[category] = new_modifier
        
        # Update the region
        region.category_price_modifiers = category_price_modifiers
        region.supply_demand_signals = supply_demand_signals
        
        # Store the cartel in custom_data
        custom_data = region.custom_data or {}
        cartels = custom_data.get("cartels", [])
        
        new_cartel = {
            "leader_id": leader_id,
            "members": all_members,
            "target_items": valid_items,
            "investment_amount": investment_amount,
            "price_effect": actual_price_effect,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat(),
            "is_active": True
        }
        
        cartels.append(new_cartel)
        custom_data["cartels"] = cartels
        region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="cartel_created",
            data={
                "leader_id": leader_id,
                "member_ids": member_ids,
                "region_id": region_id,
                "target_items": valid_items,
                "investment_amount": investment_amount,
                "price_effect": actual_price_effect,
                "duration_months": duration_months,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="market_manipulation_service"
        ))
        
        return {
            "action": "create_cartel",
            "status": "success",
            "leader_id": leader_id,
            "member_count": len(all_members),
            "region_id": region_id,
            "target_items": valid_items,
            "investment_amount": investment_amount,
            "per_member_investment": per_member_investment,
            "cartel_strength": round(cartel_strength, 2),
            "price_effect": round(actual_price_effect * 100, 1),
            "duration_months": duration_months,
            "end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat()
        }
    
    async def check_active_manipulations(self,
                                      db: Session,
                                      region_id: str) -> Dict[str, Any]:
        """
        Check active market manipulations in a region.
        
        Args:
            db: Database session
            region_id: Region identifier
            
        Returns:
            Active manipulations data
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Get custom data containing manipulations
        custom_data = region.custom_data or {}
        
        # Get all types of manipulations
        market_corners = []
        rumors = []
        cartels = []
        
        # Get market corners
        for manipulation in custom_data.get("market_manipulations", []):
            if manipulation.get("is_active", False):
                end_date = datetime.fromisoformat(manipulation.get("end_date", ""))
                if end_date > datetime.utcnow():
                    market_corners.append(manipulation)
        
        # Get rumors
        for rumor in custom_data.get("market_rumors", []):
            if rumor.get("is_active", False):
                start_date = datetime.fromisoformat(rumor.get("start_date", ""))
                duration_days = rumor.get("duration_days", 3)
                end_date = start_date + timedelta(days=duration_days)
                if end_date > datetime.utcnow():
                    rumors.append(rumor)
        
        # Get cartels
        for cartel in custom_data.get("cartels", []):
            if cartel.get("is_active", False):
                end_date = datetime.fromisoformat(cartel.get("end_date", ""))
                if end_date > datetime.utcnow():
                    cartels.append(cartel)
        
        return {
            "region_id": region_id,
            "market_corners": market_corners,
            "rumors": rumors,
            "cartels": cartels,
            "total_active_manipulations": len(market_corners) + len(rumors) + len(cartels)
        }
    
    def _get_region_size_factor(self, db: Session, region_id: str) -> float:
        """
        Get a factor representing the region's size based on locations.
        
        Args:
            db: Database session
            region_id: Region identifier
            
        Returns:
            Size factor (1.0 is average)
        """
        # Count locations in the region
        location_count = db.query(DBLocation).filter(DBLocation.region_id == region_id).count()
        
        # Calculate size factor (1.0 is an average-sized region with ~10 locations)
        return max(0.5, min(3.0, location_count / 10))
    
    def _handle_manipulation_attempt(self, event: Event) -> None:
        """
        Handle a market manipulation attempt event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling manipulation attempt: {event.data}")
        
        # In a real implementation, this would trigger NPCs to react,
        # authorities to investigate, etc.
        
    def _handle_manipulation_detected(self, event: Event) -> None:
        """
        Handle a detected market manipulation event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling detected manipulation: {event.data}")
        
        # In a real implementation, this would trigger consequences,
        # like reputation loss, fines, etc.
    
    def _handle_rumor_spread(self, event: Event) -> None:
        """
        Handle a rumor spread event.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling rumor spread: {event.data}")
        
        # In a real implementation, this might trigger NPCs to react to the rumor