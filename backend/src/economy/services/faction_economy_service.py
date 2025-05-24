"""
Faction Economy Service

This module manages faction-specific economic systems, including trade agreements,
economic bonuses, resource sharing, and unique faction-based market conditions.
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
    DBMarketRegionInfo, DBLocation, DBItem, DBCharacter, DBShop, DBResource, DBBusiness
)

# Import Celery integration for async processing
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class FactionEconomyService:
    """
    Service for managing faction-specific economic systems.
    """
    
    def __init__(self):
        """Initialize the faction economy service."""
        self.logger = logging.getLogger("FactionEconomyService")
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration for async operations
        self.celery_integration = NarrativeEngineCeleryIntegration()
        
        # Subscribe to relevant events
        self.event_bus.subscribe("faction_relationship_change", self._handle_faction_relationship_change)
        self.event_bus.subscribe("faction_territory_change", self._handle_faction_territory_change)
        self.event_bus.subscribe("faction_economic_policy_change", self._handle_economic_policy_change)
    
    async def establish_trade_agreement(self,
                                     db: Session,
                                     faction1_id: str,
                                     faction2_id: str,
                                     agreement_type: str,
                                     affected_categories: List[str],
                                     tariff_reduction: float = 0.5,
                                     duration_months: int = 12,
                                     async_processing: bool = True) -> Dict[str, Any]:
        """
        Establish a trade agreement between two factions.
        
        Args:
            db: Database session
            faction1_id: First faction identifier
            faction2_id: Second faction identifier
            agreement_type: Type of agreement (free_trade, preferred_trade, specialized_trade, etc.)
            affected_categories: Item categories affected by the agreement
            tariff_reduction: How much to reduce tariffs (0.0 to 1.0, where 1.0 is 100% reduction)
            duration_months: How long the agreement lasts
            async_processing: Whether to process asynchronously
            
        Returns:
            Trade agreement information
        """
        # Check if factions exist
        faction1 = db.query(DBCharacter).filter(
            DBCharacter.id == faction1_id,
            DBCharacter.character_type == "faction"
        ).first()
        
        faction2 = db.query(DBCharacter).filter(
            DBCharacter.id == faction2_id,
            DBCharacter.character_type == "faction"
        ).first()
        
        if not faction1 or not faction2:
            return {"error": "One or both factions not found"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.establish_trade_agreement_task",
                task_args=[faction1_id, faction2_id, agreement_type],
                task_kwargs={
                    "affected_categories": affected_categories,
                    "tariff_reduction": tariff_reduction,
                    "duration_months": duration_months
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "establish_trade_agreement",
                "faction1_id": faction1_id,
                "faction2_id": faction2_id,
                "agreement_type": agreement_type,
                "status": "processing",
                "message": f"Trade agreement establishment dispatched for asynchronous processing"
            }
        
        # For synchronous processing, establish the agreement here
        # This is a simplified implementation
        
        # Calculate economic effects based on agreement type
        if agreement_type == "free_trade":
            # Free trade reduces prices across all specified categories
            price_modifier = max(0.5, 1.0 - tariff_reduction)
            supply_modifier = 1.0 + (tariff_reduction * 0.5)
        elif agreement_type == "preferred_trade":
            # Preferred trade gives moderate benefits
            price_modifier = max(0.7, 1.0 - (tariff_reduction * 0.7))
            supply_modifier = 1.0 + (tariff_reduction * 0.3)
        elif agreement_type == "specialized_trade":
            # Specialized trade gives strong benefits to specific categories
            price_modifier = max(0.6, 1.0 - (tariff_reduction * 0.8))
            supply_modifier = 1.0 + (tariff_reduction * 0.6)
        else:
            # Default moderate agreement
            price_modifier = max(0.8, 1.0 - (tariff_reduction * 0.5))
            supply_modifier = 1.0 + (tariff_reduction * 0.2)
        
        # Get regions controlled by each faction
        faction1_regions = self._get_faction_regions(db, faction1_id)
        faction2_regions = self._get_faction_regions(db, faction2_id)
        
        # Apply economic effects to regions
        for region_id in faction1_regions + faction2_regions:
            region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
            if not region:
                continue
            
            # Update price modifiers
            category_price_modifiers = region.category_price_modifiers or {}
            for category in affected_categories:
                current_modifier = category_price_modifiers.get(category, 1.0)
                category_price_modifiers[category] = current_modifier * price_modifier
            
            region.category_price_modifiers = category_price_modifiers
            
            # Update supply/demand signals
            supply_demand_signals = region.supply_demand_signals or {}
            for category in affected_categories:
                # Convert supply modifier to supply/demand signal
                # Higher supply = lower demand = negative signal
                supply_change = supply_modifier - 1.0
                signal_change = -supply_change  # Inverse relationship
                
                current_signal = supply_demand_signals.get(category, 0.0)
                new_signal = max(-1.0, min(1.0, current_signal + signal_change))
                supply_demand_signals[category] = new_signal
            
            region.supply_demand_signals = supply_demand_signals
            
            # Record the agreement in region's custom data
            custom_data = region.custom_data or {}
            trade_agreements = custom_data.get("trade_agreements", [])
            
            new_agreement = {
                "faction1_id": faction1_id,
                "faction1_name": faction1.name,
                "faction2_id": faction2_id,
                "faction2_name": faction2.name,
                "agreement_type": agreement_type,
                "affected_categories": affected_categories,
                "tariff_reduction": tariff_reduction,
                "price_modifier": price_modifier,
                "supply_modifier": supply_modifier,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat(),
                "is_active": True
            }
            
            trade_agreements.append(new_agreement)
            custom_data["trade_agreements"] = trade_agreements
            region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Record the agreement in factions' custom data
        for faction in [faction1, faction2]:
            custom_data = faction.custom_data or {}
            trade_agreements = custom_data.get("trade_agreements", [])
            
            partner_id = faction2_id if faction.id == faction1_id else faction1_id
            partner_name = faction2.name if faction.id == faction1_id else faction1.name
            
            new_agreement = {
                "partner_id": partner_id,
                "partner_name": partner_name,
                "agreement_type": agreement_type,
                "affected_categories": affected_categories,
                "tariff_reduction": tariff_reduction,
                "price_modifier": price_modifier,
                "supply_modifier": supply_modifier,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat(),
                "is_active": True
            }
            
            trade_agreements.append(new_agreement)
            custom_data["trade_agreements"] = trade_agreements
            faction.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="trade_agreement_established",
            data={
                "faction1_id": faction1_id,
                "faction1_name": faction1.name,
                "faction2_id": faction2_id,
                "faction2_name": faction2.name,
                "agreement_type": agreement_type,
                "affected_categories": affected_categories,
                "tariff_reduction": tariff_reduction,
                "price_modifier": price_modifier,
                "supply_modifier": supply_modifier,
                "duration_months": duration_months,
                "affected_regions": faction1_regions + faction2_regions,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="faction_economy_service"
        ))
        
        return {
            "action": "establish_trade_agreement",
            "status": "success",
            "faction1_id": faction1_id,
            "faction1_name": faction1.name,
            "faction2_id": faction2_id,
            "faction2_name": faction2.name,
            "agreement_type": agreement_type,
            "affected_categories": affected_categories,
            "tariff_reduction": f"{tariff_reduction * 100:.1f}%",
            "price_effect": f"{(price_modifier - 1.0) * 100:.1f}%",
            "supply_effect": f"{(supply_modifier - 1.0) * 100:.1f}%",
            "affected_regions_count": len(faction1_regions) + len(faction2_regions),
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat(),
            "duration_months": duration_months
        }
    
    async def set_faction_economic_bonus(self,
                                     db: Session,
                                     faction_id: str,
                                     bonus_type: str,
                                     bonus_value: float,
                                     affected_categories: Optional[List[str]] = None,
                                     async_processing: bool = True) -> Dict[str, Any]:
        """
        Set economic bonuses for a faction.
        
        Args:
            db: Database session
            faction_id: Faction identifier
            bonus_type: Type of bonus (production, trade, crafting, resource_gathering, etc.)
            bonus_value: Value of the bonus (1.0 is no bonus, 1.2 is 20% bonus)
            affected_categories: Optional list of specific item categories to affect
            async_processing: Whether to process asynchronously
            
        Returns:
            Faction bonus information
        """
        # Check if faction exists
        faction = db.query(DBCharacter).filter(
            DBCharacter.id == faction_id,
            DBCharacter.character_type == "faction"
        ).first()
        
        if not faction:
            return {"error": f"Faction {faction_id} not found"}
        
        # If no categories specified, affect all
        if not affected_categories:
            affected_categories = [
                "weapon", "armor", "food", "material", "tool", 
                "magical", "clothing", "treasure", "miscellaneous"
            ]
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.set_faction_economic_bonus_task",
                task_args=[faction_id, bonus_type, bonus_value],
                task_kwargs={
                    "affected_categories": affected_categories
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "set_faction_economic_bonus",
                "faction_id": faction_id,
                "bonus_type": bonus_type,
                "status": "processing",
                "message": f"Faction economic bonus setting dispatched for asynchronous processing"
            }
        
        # For synchronous processing, set the bonus here
        # This is a simplified implementation
        
        # Get regions controlled by the faction
        faction_regions = self._get_faction_regions(db, faction_id)
        
        # Calculate economic effects based on bonus type
        production_modifier = 1.0
        price_modifier = 1.0
        prosperity_modifier = 1.0
        supply_modifier = 1.0
        
        if bonus_type == "production":
            production_modifier = bonus_value
            supply_modifier = 1.0 + ((bonus_value - 1.0) * 0.8)
            price_modifier = max(0.8, 1.0 - ((bonus_value - 1.0) * 0.5))
        elif bonus_type == "trade":
            price_modifier = max(0.7, 1.0 - ((bonus_value - 1.0) * 0.7))
            prosperity_modifier = 1.0 + ((bonus_value - 1.0) * 0.3)
        elif bonus_type == "crafting":
            production_modifier = bonus_value * 1.2
            supply_modifier = 1.0 + ((bonus_value - 1.0) * 0.6)
        elif bonus_type == "resource_gathering":
            supply_modifier = bonus_value
            prosperity_modifier = 1.0 + ((bonus_value - 1.0) * 0.2)
        else:
            # Default general bonus
            production_modifier = 1.0 + ((bonus_value - 1.0) * 0.5)
            price_modifier = max(0.9, 1.0 - ((bonus_value - 1.0) * 0.3))
            prosperity_modifier = 1.0 + ((bonus_value - 1.0) * 0.1)
            supply_modifier = 1.0 + ((bonus_value - 1.0) * 0.4)
        
        # Update faction custom data with the bonus
        custom_data = faction.custom_data or {}
        economic_bonuses = custom_data.get("economic_bonuses", {})
        
        economic_bonuses[bonus_type] = {
            "bonus_value": bonus_value,
            "affected_categories": affected_categories,
            "production_modifier": production_modifier,
            "price_modifier": price_modifier,
            "prosperity_modifier": prosperity_modifier,
            "supply_modifier": supply_modifier,
            "set_date": datetime.utcnow().isoformat()
        }
        
        custom_data["economic_bonuses"] = economic_bonuses
        faction.custom_data = custom_data
        
        # Apply effects to regions
        for region_id in faction_regions:
            region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
            if not region:
                continue
            
            # Update prosperity
            if prosperity_modifier != 1.0:
                region.prosperity_level = min(1.0, max(0.1, region.prosperity_level * prosperity_modifier))
            
            # Update price modifiers
            if price_modifier != 1.0:
                category_price_modifiers = region.category_price_modifiers or {}
                for category in affected_categories:
                    current_modifier = category_price_modifiers.get(category, 1.0)
                    category_price_modifiers[category] = current_modifier * price_modifier
                
                region.category_price_modifiers = category_price_modifiers
            
            # Update supply/demand signals
            if supply_modifier != 1.0:
                supply_demand_signals = region.supply_demand_signals or {}
                for category in affected_categories:
                    # Convert supply modifier to supply/demand signal
                    # Higher supply = lower demand = negative signal
                    supply_change = supply_modifier - 1.0
                    signal_change = -supply_change  # Inverse relationship
                    
                    current_signal = supply_demand_signals.get(category, 0.0)
                    new_signal = max(-1.0, min(1.0, current_signal + signal_change))
                    supply_demand_signals[category] = new_signal
                
                region.supply_demand_signals = supply_demand_signals
            
            # Record the bonus in region's custom data
            custom_data = region.custom_data or {}
            faction_bonuses = custom_data.get("faction_bonuses", {})
            
            faction_bonuses[faction_id] = {
                "faction_name": faction.name,
                "bonus_type": bonus_type,
                "bonus_value": bonus_value,
                "affected_categories": affected_categories,
                "production_modifier": production_modifier,
                "price_modifier": price_modifier,
                "prosperity_modifier": prosperity_modifier,
                "supply_modifier": supply_modifier,
                "set_date": datetime.utcnow().isoformat()
            }
            
            custom_data["faction_bonuses"] = faction_bonuses
            region.custom_data = custom_data
        
        # If production modifier affects businesses, update them
        if bonus_type in ["production", "crafting"] and production_modifier != 1.0:
            self._update_faction_businesses(db, faction_id, production_modifier, affected_categories)
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="faction_economic_bonus_set",
            data={
                "faction_id": faction_id,
                "faction_name": faction.name,
                "bonus_type": bonus_type,
                "bonus_value": bonus_value,
                "affected_categories": affected_categories,
                "production_modifier": production_modifier,
                "price_modifier": price_modifier,
                "prosperity_modifier": prosperity_modifier,
                "supply_modifier": supply_modifier,
                "affected_regions": faction_regions,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="faction_economy_service"
        ))
        
        return {
            "action": "set_faction_economic_bonus",
            "status": "success",
            "faction_id": faction_id,
            "faction_name": faction.name,
            "bonus_type": bonus_type,
            "bonus_value": bonus_value,
            "affected_categories": affected_categories,
            "production_effect": f"{(production_modifier - 1.0) * 100:.1f}%",
            "price_effect": f"{(price_modifier - 1.0) * 100:.1f}%",
            "prosperity_effect": f"{(prosperity_modifier - 1.0) * 100:.1f}%",
            "supply_effect": f"{(supply_modifier - 1.0) * 100:.1f}%",
            "affected_regions_count": len(faction_regions)
        }
    
    async def create_faction_marketplace(self,
                                      db: Session,
                                      faction_id: str,
                                      marketplace_name: str,
                                      location_id: str,
                                      specializations: List[str],
                                      exclusivity_level: float = 0.5,  # 0.0 to 1.0
                                      async_processing: bool = True) -> Dict[str, Any]:
        """
        Create a specialized marketplace for a faction.
        
        Args:
            db: Database session
            faction_id: Faction identifier
            marketplace_name: Name of the marketplace
            location_id: Location where the marketplace is established
            specializations: Item categories this marketplace specializes in
            exclusivity_level: How exclusive the marketplace is (0.0 open to all, 1.0 faction-only)
            async_processing: Whether to process asynchronously
            
        Returns:
            Marketplace information
        """
        # Check if faction exists
        faction = db.query(DBCharacter).filter(
            DBCharacter.id == faction_id,
            DBCharacter.character_type == "faction"
        ).first()
        
        if not faction:
            return {"error": f"Faction {faction_id} not found"}
        
        # Check if location exists
        location = db.query(DBLocation).filter(DBLocation.id == location_id).first()
        if not location:
            return {"error": f"Location {location_id} not found"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.create_faction_marketplace_task",
                task_args=[faction_id, marketplace_name, location_id],
                task_kwargs={
                    "specializations": specializations,
                    "exclusivity_level": exclusivity_level
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "create_faction_marketplace",
                "faction_id": faction_id,
                "marketplace_name": marketplace_name,
                "location_id": location_id,
                "status": "processing",
                "message": f"Faction marketplace creation dispatched for asynchronous processing"
            }
        
        # For synchronous processing, create the marketplace here
        # This is a simplified implementation
        
        # Generate unique ID for the marketplace
        marketplace_id = f"marketplace-{faction_id}-{location_id}-{datetime.utcnow().timestamp()}"
        
        # Create marketplace custom data
        marketplace_data = {
            "id": marketplace_id,
            "name": marketplace_name,
            "faction_id": faction_id,
            "faction_name": faction.name,
            "location_id": location_id,
            "location_name": location.name,
            "region_id": location.region_id,
            "specializations": specializations,
            "exclusivity_level": exclusivity_level,
            "creation_date": datetime.utcnow().isoformat(),
            "is_active": True,
            "shops": [],
            "trade_volume": 0.0,
            "last_month_revenue": 0.0
        }
        
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == location.region_id).first()
        if not region:
            return {"error": f"Region {location.region_id} not found for location {location_id}"}
        
        # Calculate marketplace effects
        # Higher exclusivity means better prices for faction members but less overall volume
        # Higher specialization means better prices for specialized categories
        
        # Calculate specialization bonus
        specialization_bonus = min(0.3, 0.1 * len(specializations))
        
        # Calculate price effects
        faction_price_modifier = max(0.7, 1.0 - (0.2 + specialization_bonus))  # 20-50% discount
        non_faction_price_modifier = 1.0 + (exclusivity_level * 0.3)  # 0-30% markup
        
        # Apply effects to the location and region
        
        # Update location custom data
        location_custom_data = location.custom_data or {}
        marketplaces = location_custom_data.get("marketplaces", [])
        marketplaces.append(marketplace_data)
        location_custom_data["marketplaces"] = marketplaces
        location.custom_data = location_custom_data
        
        # Update region custom data
        region_custom_data = region.custom_data or {}
        faction_marketplaces = region_custom_data.get("faction_marketplaces", [])
        faction_marketplaces.append({
            "id": marketplace_id,
            "name": marketplace_name,
            "faction_id": faction_id,
            "faction_name": faction.name,
            "location_id": location_id,
            "location_name": location.name,
            "specializations": specializations,
            "exclusivity_level": exclusivity_level
        })
        region_custom_data["faction_marketplaces"] = faction_marketplaces
        
        # Update region price modifiers for specialized categories
        category_price_modifiers = region.category_price_modifiers or {}
        for category in specializations:
            # Slightly reduce overall prices in the region due to increased competition
            current_modifier = category_price_modifiers.get(category, 1.0)
            category_price_modifiers[category] = current_modifier * 0.95
        
        region.category_price_modifiers = category_price_modifiers
        region.custom_data = region_custom_data
        
        # Update faction custom data
        faction_custom_data = faction.custom_data or {}
        owned_marketplaces = faction_custom_data.get("owned_marketplaces", [])
        owned_marketplaces.append({
            "id": marketplace_id,
            "name": marketplace_name,
            "location_id": location_id,
            "location_name": location.name,
            "region_id": location.region_id,
            "specializations": specializations,
            "exclusivity_level": exclusivity_level,
            "creation_date": datetime.utcnow().isoformat()
        })
        faction_custom_data["owned_marketplaces"] = owned_marketplaces
        faction.custom_data = faction_custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="faction_marketplace_created",
            data={
                "marketplace_id": marketplace_id,
                "marketplace_name": marketplace_name,
                "faction_id": faction_id,
                "faction_name": faction.name,
                "location_id": location_id,
                "location_name": location.name,
                "region_id": location.region_id,
                "specializations": specializations,
                "exclusivity_level": exclusivity_level,
                "faction_price_modifier": faction_price_modifier,
                "non_faction_price_modifier": non_faction_price_modifier,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="faction_economy_service"
        ))
        
        # Create 3-5 specialized shops in the marketplace
        created_shops = []
        for i in range(random.randint(3, 5)):
            category = random.choice(specializations)
            shop_type = self._get_shop_type_for_category(category)
            shop_name = f"{faction.name}'s {shop_type.capitalize()}"
            
            # Create shop data
            shop_data = {
                "id": f"shop-{marketplace_id}-{i}",
                "name": shop_name,
                "description": f"A {shop_type} shop in {marketplace_name}, specializing in {category} items.",
                "owner_id": faction_id,
                "location_id": location_id,
                "shop_type": shop_type,
                "marketplace_id": marketplace_id,
                "specialization": category,
                "faction_price_modifier": faction_price_modifier,
                "non_faction_price_modifier": non_faction_price_modifier
            }
            
            created_shops.append(shop_data)
        
        return {
            "action": "create_faction_marketplace",
            "status": "success",
            "marketplace_id": marketplace_id,
            "marketplace_name": marketplace_name,
            "faction_id": faction_id,
            "faction_name": faction.name,
            "location_id": location_id,
            "location_name": location.name,
            "region_id": location.region_id,
            "specializations": specializations,
            "exclusivity_level": exclusivity_level,
            "faction_price_modifier": f"{(faction_price_modifier - 1.0) * 100:.1f}%",
            "non_faction_price_modifier": f"{(non_faction_price_modifier - 1.0) * 100:.1f}%",
            "created_shops": created_shops
        }
    
    async def implement_faction_tax_policy(self,
                                        db: Session,
                                        faction_id: str,
                                        tax_policy: str,
                                        base_tax_rate: float,
                                        category_modifiers: Dict[str, float] = None,
                                        async_processing: bool = True) -> Dict[str, Any]:
        """
        Implement a tax policy for a faction's territories.
        
        Args:
            db: Database session
            faction_id: Faction identifier
            tax_policy: Type of policy (progressive, flat, luxury, etc.)
            base_tax_rate: Base tax rate (0.0 to 1.0)
            category_modifiers: Optional dict mapping categories to tax modifiers
            async_processing: Whether to process asynchronously
            
        Returns:
            Tax policy information
        """
        # Check if faction exists
        faction = db.query(DBCharacter).filter(
            DBCharacter.id == faction_id,
            DBCharacter.character_type == "faction"
        ).first()
        
        if not faction:
            return {"error": f"Faction {faction_id} not found"}
        
        # Initialize category modifiers if not provided
        if not category_modifiers:
            category_modifiers = {}
        
        # Set default modifiers based on policy type
        if tax_policy == "luxury":
            # Higher taxes on luxury items
            category_modifiers.setdefault("treasure", 2.0)
            category_modifiers.setdefault("luxury", 1.8)
            category_modifiers.setdefault("magical", 1.5)
            # Lower taxes on necessities
            category_modifiers.setdefault("food", 0.5)
            category_modifiers.setdefault("tool", 0.7)
        elif tax_policy == "wartime":
            # Higher taxes on all items except military supplies
            category_modifiers.setdefault("weapon", 0.5)
            category_modifiers.setdefault("armor", 0.5)
            category_modifiers.setdefault("food", 0.8)
            # Higher taxes on non-essential items
            category_modifiers.setdefault("luxury", 2.0)
            category_modifiers.setdefault("treasure", 2.0)
        elif tax_policy == "mercantile":
            # Lower taxes on trade goods to stimulate economy
            category_modifiers.setdefault("material", 0.7)
            category_modifiers.setdefault("tool", 0.8)
            # But higher taxes on finished goods
            category_modifiers.setdefault("weapon", 1.2)
            category_modifiers.setdefault("armor", 1.2)
            category_modifiers.setdefault("clothing", 1.3)
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.implement_faction_tax_policy_task",
                task_args=[faction_id, tax_policy, base_tax_rate],
                task_kwargs={
                    "category_modifiers": category_modifiers
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "implement_faction_tax_policy",
                "faction_id": faction_id,
                "tax_policy": tax_policy,
                "status": "processing",
                "message": f"Faction tax policy implementation dispatched for asynchronous processing"
            }
        
        # For synchronous processing, implement the tax policy here
        # This is a simplified implementation
        
        # Get regions controlled by the faction
        faction_regions = self._get_faction_regions(db, faction_id)
        
        # Calculate economic effects of tax policy
        prosperity_modifier = max(0.7, 1.0 - (base_tax_rate * 0.5))  # Higher taxes reduce prosperity
        price_modifiers = {}
        
        # Calculate price modifiers for each category
        for category, modifier in category_modifiers.items():
            # Tax affects prices directly
            category_tax = base_tax_rate * modifier
            price_modifiers[category] = 1.0 + category_tax
        
        # Apply default tax to categories not explicitly modified
        all_categories = [
            "weapon", "armor", "food", "material", "tool", 
            "magical", "clothing", "treasure", "miscellaneous"
        ]
        for category in all_categories:
            if category not in price_modifiers:
                price_modifiers[category] = 1.0 + base_tax_rate
        
        # Update faction custom data with the tax policy
        custom_data = faction.custom_data or {}
        tax_policies = custom_data.get("tax_policies", {})
        
        tax_policies["current"] = {
            "policy_type": tax_policy,
            "base_rate": base_tax_rate,
            "category_modifiers": category_modifiers,
            "price_modifiers": price_modifiers,
            "prosperity_modifier": prosperity_modifier,
            "implementation_date": datetime.utcnow().isoformat()
        }
        
        custom_data["tax_policies"] = tax_policies
        faction.custom_data = custom_data
        
        # Apply tax policy to regions
        for region_id in faction_regions:
            region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
            if not region:
                continue
            
            # Update tax rate
            region.tax_rate = base_tax_rate
            
            # Update prosperity
            region.prosperity_level = min(1.0, max(0.1, region.prosperity_level * prosperity_modifier))
            
            # Update price modifiers
            category_price_modifiers = region.category_price_modifiers or {}
            for category, modifier in price_modifiers.items():
                current_modifier = category_price_modifiers.get(category, 1.0)
                category_price_modifiers[category] = current_modifier * modifier
            
            region.category_price_modifiers = category_price_modifiers
            
            # Record the tax policy in region's custom data
            custom_data = region.custom_data or {}
            custom_data["tax_policy"] = {
                "faction_id": faction_id,
                "faction_name": faction.name,
                "policy_type": tax_policy,
                "base_rate": base_tax_rate,
                "category_modifiers": category_modifiers,
                "price_modifiers": price_modifiers,
                "prosperity_modifier": prosperity_modifier,
                "implementation_date": datetime.utcnow().isoformat()
            }
            
            region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="faction_tax_policy_implemented",
            data={
                "faction_id": faction_id,
                "faction_name": faction.name,
                "tax_policy": tax_policy,
                "base_tax_rate": base_tax_rate,
                "category_modifiers": category_modifiers,
                "price_modifiers": price_modifiers,
                "prosperity_modifier": prosperity_modifier,
                "affected_regions": faction_regions,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="faction_economy_service"
        ))
        
        return {
            "action": "implement_faction_tax_policy",
            "status": "success",
            "faction_id": faction_id,
            "faction_name": faction.name,
            "tax_policy": tax_policy,
            "base_tax_rate": f"{base_tax_rate * 100:.1f}%",
            "category_modifiers": {k: f"{v:.1f}x" for k, v in category_modifiers.items()},
            "price_effects": {k: f"+{(v - 1.0) * 100:.1f}%" for k, v in price_modifiers.items()},
            "prosperity_effect": f"{(prosperity_modifier - 1.0) * 100:.1f}%",
            "affected_regions_count": len(faction_regions)
        }
    
    def _get_faction_regions(self, db: Session, faction_id: str) -> List[str]:
        """
        Get regions controlled by a faction.
        
        Args:
            db: Database session
            faction_id: Faction identifier
            
        Returns:
            List of region IDs
        """
        # Get locations controlled by the faction
        locations = db.query(DBLocation).filter(DBLocation.owner_id == faction_id).all()
        
        # Extract unique region IDs
        region_ids = list(set(location.region_id for location in locations))
        
        return region_ids
    
    def _update_faction_businesses(self, 
                                db: Session, 
                                faction_id: str, 
                                production_modifier: float,
                                affected_categories: List[str]) -> None:
        """
        Update businesses owned by a faction with production bonuses.
        
        Args:
            db: Database session
            faction_id: Faction identifier
            production_modifier: Production modifier to apply
            affected_categories: Item categories affected
        """
        # Get businesses owned by the faction
        businesses = db.query(DBBusiness).filter(DBBusiness.owner_id == faction_id).all()
        
        for business in businesses:
            # Check if business produces items in affected categories
            if not business.production_item_id:
                continue
                
            item = db.query(DBItem).filter(DBItem.id == business.production_item_id).first()
            if not item or item.category not in affected_categories:
                continue
            
            # Apply production bonus
            business.efficiency = min(1.0, business.efficiency * production_modifier)
            business.production_capacity = int(business.production_capacity * production_modifier)
            
            # Update custom data to record bonus
            custom_data = business.custom_data or {}
            bonuses = custom_data.get("production_bonuses", [])
            
            bonuses.append({
                "source": "faction_bonus",
                "faction_id": faction_id,
                "modifier": production_modifier,
                "applied_date": datetime.utcnow().isoformat()
            })
            
            custom_data["production_bonuses"] = bonuses
            business.custom_data = custom_data
    
    def _get_shop_type_for_category(self, category: str) -> str:
        """
        Get appropriate shop type for an item category.
        
        Args:
            category: Item category
            
        Returns:
            Shop type
        """
        category_to_shop = {
            "weapon": "blacksmith",
            "armor": "armorer",
            "food": "grocer",
            "material": "general_store",
            "tool": "hardware_store",
            "magical": "magic_shop",
            "clothing": "tailor",
            "treasure": "jeweler",
            "miscellaneous": "general_store"
        }
        
        return category_to_shop.get(category, "general_store")
    
    def _handle_faction_relationship_change(self, event: Event) -> None:
        """
        Handle a change in faction relationships.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling faction relationship change: {event.data}")
        
        # In a real implementation, this would affect trade agreements,
        # marketplace access, etc.
    
    def _handle_faction_territory_change(self, event: Event) -> None:
        """
        Handle a change in faction territories.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling faction territory change: {event.data}")
        
        # In a real implementation, this would update economic controls,
        # tax policies, etc.
    
    def _handle_economic_policy_change(self, event: Event) -> None:
        """
        Handle a change in faction economic policies.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling economic policy change: {event.data}")
        
        # In a real implementation, this would update various economic
        # factors across the faction's territories