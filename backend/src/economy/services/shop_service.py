"""
Shop Service Module

This module handles shop interactions, including inventory management,
pricing calculations, and shop-related operations.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from datetime import datetime
from sqlalchemy.orm import Session

# Import models
from backend.src.economy.models.pydantic_models import (
    Item, Shop, InventorySlot, ItemCategory, ItemRarity, MarketRegionInfo
)
from backend.src.economy.models.db_models import (
    DBItem, DBShop, DBLocation, DBMarketRegionInfo
)

# Import Celery integration for async processing
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
from backend.src.narrative_engine.event_bus import get_event_bus, Event

# Import CRUD operations (to be implemented)
# from backend.src.economy.crud import item, shop, location, market_region_info

logger = logging.getLogger(__name__)

class ShopService:
    """
    Service for managing shops, their inventories, and pricing.
    """
    
    def __init__(self):
        """Initialize the shop service."""
        self.logger = logging.getLogger("ShopService")
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration for async operations
        self.celery_integration = NarrativeEngineCeleryIntegration()
    
    def get_shop_inventory_display(self, 
                                 db: Session, 
                                 shop_id: str, 
                                 player_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a display-friendly version of a shop's inventory.
        
        Args:
            db: Database session
            shop_id: Shop identifier
            player_id: Optional player identifier for relationship modifiers
            
        Returns:
            List of inventory items with display information
        """
        # Get the shop from the database
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            self.logger.warning(f"Shop {shop_id} not found")
            return []
        
        # Get the shop's location
        location = db.query(DBLocation).filter(DBLocation.id == shop.location_id).first()
        
        if not location:
            self.logger.warning(f"Location {shop.location_id} not found for shop {shop_id}")
            return []
        
        # Get the market region info
        region_info = db.query(DBMarketRegionInfo).filter(
            DBMarketRegionInfo.region_id == location.region_id
        ).first()
        
        if not region_info:
            self.logger.warning(f"Market region {location.region_id} not found for location {location.id}")
            return []
        
        # Get relationship modifier if player_id is provided
        relationship_modifier = 1.0
        if player_id:
            relationship_modifier = self._get_relationship_modifier(db, player_id, shop.owner_id)
        
        inventory_display = []
        
        # Process each item in the shop's inventory
        for item_id, slot_data in shop.inventory.items():
            # Get the item template from the database
            item = db.query(DBItem).filter(DBItem.id == item_id).first()
            
            if not item:
                self.logger.warning(f"Item {item_id} not found for shop {shop_id}")
                continue
            
            # Reconstruct the inventory slot
            slot = InventorySlot(**slot_data)
            
            # Calculate the price with all modifiers
            calculated_price = self.calculate_item_price(
                db,
                item_id=item_id,
                shop_id=shop_id,
                relationship_modifier=relationship_modifier,
                is_buying=True  # Player is buying from the shop
            )
            
            # Create the display entry
            display_entry = {
                "item_id": item_id,
                "name": item.name,
                "description": item.description,
                "category": item.category,
                "rarity": item.rarity,
                "quantity": slot.quantity,
                "condition": slot.condition,
                "base_price": item.base_price,
                "calculated_price": calculated_price,
                "price_override": slot.price_override,
                "effective_price": slot.price_override if slot.price_override is not None else calculated_price,
                "stackable": item.stackable,
                "max_stack": item.max_stack,
                "equippable": item.equippable,
                "weight": item.weight
            }
            
            inventory_display.append(display_entry)
        
        return inventory_display
    
    def calculate_item_price(self, 
                           db: Session, 
                           item_id: str, 
                           shop_id: str, 
                           relationship_modifier: float = 1.0,
                           is_buying: bool = True) -> float:
        """
        Calculate the price of an item with all applicable modifiers.
        
        Args:
            db: Database session
            item_id: Item identifier
            shop_id: Shop identifier
            relationship_modifier: Modifier based on player's relationship with shop owner
            is_buying: Whether the player is buying (True) or selling (False)
            
        Returns:
            Calculated price
        """
        # Get the item from the database
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        
        if not item:
            self.logger.warning(f"Item {item_id} not found")
            return 0.0
        
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            self.logger.warning(f"Shop {shop_id} not found")
            return 0.0
        
        # Get the shop's location
        location = db.query(DBLocation).filter(DBLocation.id == shop.location_id).first()
        
        if not location:
            self.logger.warning(f"Location {shop.location_id} not found for shop {shop_id}")
            return 0.0
        
        # Get the market region info
        region_info = db.query(DBMarketRegionInfo).filter(
            DBMarketRegionInfo.region_id == location.region_id
        ).first()
        
        if not region_info:
            self.logger.warning(f"Market region {location.region_id} not found for location {location.id}")
            return 0.0
        
        # Start with base price
        base_price = item.base_price
        
        # Apply rarity modifier
        rarity_modifiers = {
            "common": 1.0,
            "uncommon": 1.5,
            "rare": 2.5,
            "epic": 5.0,
            "legendary": 10.0,
            "artifact": 25.0
        }
        rarity_modifier = rarity_modifiers.get(item.rarity, 1.0)
        
        # Apply category price modifier from region
        category_modifier = region_info.category_price_modifiers.get(item.category, 1.0)
        
        # Apply supply/demand signal from region
        supply_demand_modifier = 1.0
        if item.category in region_info.supply_demand_signals:
            # Signal ranges from -1.0 (oversupply) to 1.0 (high demand)
            signal = region_info.supply_demand_signals.get(item.category, 0.0)
            # Convert signal to modifier (0.5 to 1.5)
            supply_demand_modifier = 1.0 + (signal * 0.5)
        
        # Apply shop's buy/sell modifier
        transaction_modifier = shop.sell_price_modifier if is_buying else shop.buy_price_modifier
        
        # Calculate final price
        price = base_price * rarity_modifier * category_modifier * supply_demand_modifier * transaction_modifier * relationship_modifier
        
        # Round to 2 decimal places
        return round(price, 2)
    
    def create_shop(self, 
                  db: Session, 
                  shop_data: Shop) -> DBShop:
        """
        Create a new shop.
        
        Args:
            db: Database session
            shop_data: Shop data
            
        Returns:
            Created shop
        """
        # Create shop in database
        db_shop = DBShop(
            id=shop_data.id,
            name=shop_data.name,
            description=shop_data.description,
            owner_id=shop_data.owner_id,
            location_id=shop_data.location_id,
            shop_type=shop_data.shop_type,
            inventory=shop_data.inventory,
            currency_balance=shop_data.currency_balance,
            buy_price_modifier=shop_data.buy_price_modifier,
            sell_price_modifier=shop_data.sell_price_modifier,
            reputation_required=shop_data.reputation_required,
            restocks=shop_data.restocks,
            restock_interval=shop_data.restock_interval,
            last_restock=shop_data.last_restock,
            custom_data=shop_data.custom_data
        )
        
        db.add(db_shop)
        db.commit()
        db.refresh(db_shop)
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="shop_created",
            data={
                "shop_id": db_shop.id,
                "location_id": db_shop.location_id,
                "shop_type": db_shop.shop_type
            },
            source="shop_service"
        ))
        
        return db_shop
    
    def add_item_to_shop_inventory(self, 
                                 db: Session, 
                                 shop_id: str, 
                                 item_id: str, 
                                 quantity: int, 
                                 price_override: Optional[float] = None) -> bool:
        """
        Add an item to a shop's inventory.
        
        Args:
            db: Database session
            shop_id: Shop identifier
            item_id: Item identifier
            quantity: Quantity to add
            price_override: Optional price override
            
        Returns:
            Success flag
        """
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            self.logger.warning(f"Shop {shop_id} not found")
            return False
        
        # Get the item to check if it exists and get properties
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        
        if not item:
            self.logger.warning(f"Item {item_id} not found")
            return False
        
        # Handle inventory update
        inventory = shop.inventory
        
        # Check if item already exists in inventory
        if item_id in inventory:
            slot_data = inventory[item_id]
            slot = InventorySlot(**slot_data)
            
            # If item is stackable, add to quantity
            if item.stackable:
                # Check max stack size
                new_quantity = slot.quantity + quantity
                if new_quantity > item.max_stack:
                    self.logger.warning(f"Cannot add {quantity} of {item_id} to shop {shop_id}. Max stack size is {item.max_stack}.")
                    return False
                
                slot.quantity = new_quantity
            else:
                # Non-stackable items get new entries
                self.logger.warning(f"Item {item_id} is not stackable. Create a new entry.")
                return False
                
            # Update price override if provided
            if price_override is not None:
                slot.price_override = price_override
                
            # Update inventory
            inventory[item_id] = slot.dict()
        else:
            # Create new inventory slot
            slot = InventorySlot(
                quantity=quantity,
                condition=1.0,  # New items are in perfect condition
                price_override=price_override,
                custom_data={}
            )
            
            # Add to inventory
            inventory[item_id] = slot.dict()
        
        # Update shop inventory
        shop.inventory = inventory
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="shop_inventory_updated",
            data={
                "shop_id": shop_id,
                "item_id": item_id,
                "quantity_change": quantity,
                "new_quantity": inventory[item_id]["quantity"]
            },
            source="shop_service"
        ))
        
        return True
    
    def remove_item_from_shop_inventory(self, 
                                      db: Session, 
                                      shop_id: str, 
                                      item_id: str, 
                                      quantity: int) -> bool:
        """
        Remove an item from a shop's inventory.
        
        Args:
            db: Database session
            shop_id: Shop identifier
            item_id: Item identifier
            quantity: Quantity to remove
            
        Returns:
            Success flag
        """
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            self.logger.warning(f"Shop {shop_id} not found")
            return False
        
        # Handle inventory update
        inventory = shop.inventory
        
        # Check if item exists in inventory
        if item_id not in inventory:
            self.logger.warning(f"Item {item_id} not in shop {shop_id} inventory")
            return False
        
        slot_data = inventory[item_id]
        slot = InventorySlot(**slot_data)
        
        # Check if we have enough quantity
        if slot.quantity < quantity:
            self.logger.warning(f"Not enough quantity of {item_id} in shop {shop_id} inventory")
            return False
        
        # Update quantity
        slot.quantity -= quantity
        
        # If quantity is now 0, remove the item
        if slot.quantity <= 0:
            inventory.pop(item_id)
        else:
            # Update inventory
            inventory[item_id] = slot.dict()
        
        # Update shop inventory
        shop.inventory = inventory
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="shop_inventory_updated",
            data={
                "shop_id": shop_id,
                "item_id": item_id,
                "quantity_change": -quantity,
                "new_quantity": inventory.get(item_id, {}).get("quantity", 0)
            },
            source="shop_service"
        ))
        
        return True
    
    def update_shop_currency(self, 
                           db: Session, 
                           shop_id: str, 
                           amount: float) -> bool:
        """
        Update a shop's currency balance.
        
        Args:
            db: Database session
            shop_id: Shop identifier
            amount: Amount to add (positive) or subtract (negative)
            
        Returns:
            Success flag
        """
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            self.logger.warning(f"Shop {shop_id} not found")
            return False
        
        # Update currency balance
        old_balance = shop.currency_balance
        new_balance = old_balance + amount
        
        # Ensure balance doesn't go negative
        if new_balance < 0:
            self.logger.warning(f"Cannot update shop {shop_id} currency. Would result in negative balance.")
            return False
        
        shop.currency_balance = new_balance
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="shop_currency_updated",
            data={
                "shop_id": shop_id,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "change": amount
            },
            source="shop_service"
        ))
        
        return True
    
    async def restock_shop(self, 
                         db: Session, 
                         shop_id: str,
                         async_processing: bool = True) -> Dict[str, Any]:
        """
        Restock a shop's inventory based on its type and location.
        
        Args:
            db: Database session
            shop_id: Shop identifier
            async_processing: Whether to process asynchronously
            
        Returns:
            Restock results or task information
        """
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            self.logger.warning(f"Shop {shop_id} not found")
            return {"error": f"Shop {shop_id} not found"}
        
        # Check if shop allows restocking
        if not shop.restocks:
            return {"error": f"Shop {shop_id} does not restock"}
        
        # Check if it's time to restock
        now = datetime.utcnow()
        last_restock = shop.last_restock or datetime.min
        hours_since_restock = (now - last_restock).total_seconds() / 3600
        
        if hours_since_restock < shop.restock_interval:
            return {
                "shop_id": shop_id,
                "status": "not_ready",
                "hours_until_restock": shop.restock_interval - hours_since_restock
            }
        
        # Use Celery for async processing
        if async_processing:
            # This would be defined in economy/tasks.py
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.restock_shop_task",
                task_args=[shop_id],
                task_kwargs={}
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "shop_id": shop_id,
                "status": "processing",
                "message": "Shop restock dispatched for asynchronous processing"
            }
        
        # For synchronous processing, perform the restock here
        # This is a simplified implementation
        
        # Get the shop's location
        location = db.query(DBLocation).filter(DBLocation.id == shop.location_id).first()
        
        if not location:
            return {"error": f"Location {shop.location_id} not found for shop {shop_id}"}
        
        # Get the market region info
        region_info = db.query(DBMarketRegionInfo).filter(
            DBMarketRegionInfo.region_id == location.region_id
        ).first()
        
        if not region_info:
            return {"error": f"Market region {location.region_id} not found for location {location.id}"}
        
        # Determine items to restock based on shop type
        restock_items = self._get_restock_items_for_shop(db, shop, location, region_info)
        
        # Add items to inventory
        items_added = []
        for item_id, quantity in restock_items.items():
            if self.add_item_to_shop_inventory(db, shop_id, item_id, quantity):
                items_added.append({"item_id": item_id, "quantity": quantity})
        
        # Update last restock time
        shop.last_restock = now
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="shop_restocked",
            data={
                "shop_id": shop_id,
                "items_added": items_added,
                "timestamp": now.isoformat()
            },
            source="shop_service"
        ))
        
        return {
            "shop_id": shop_id,
            "status": "restocked",
            "items_added": items_added,
            "next_restock_time": (now + shop.restock_interval).isoformat()
        }
    
    def _get_relationship_modifier(self, 
                                 db: Session, 
                                 player_id: str, 
                                 shop_owner_id: str) -> float:
        """
        Get price modifier based on player's relationship with shop owner.
        
        Args:
            db: Database session
            player_id: Player identifier
            shop_owner_id: Shop owner identifier
            
        Returns:
            Relationship modifier
        """
        # In a real implementation, this would query the relationship system
        # For now, return default value
        return 1.0
    
    def _get_restock_items_for_shop(self,
                                  db: Session,
                                  shop: DBShop,
                                  location: DBLocation,
                                  region_info: DBMarketRegionInfo) -> Dict[str, int]:
        """
        Determine which items and quantities to restock based on shop type.
        
        Args:
            db: Database session
            shop: Shop object
            location: Location object
            region_info: Market region info
            
        Returns:
            Dictionary of item IDs to quantities
        """
        # In a real implementation, this would be more sophisticated
        # For now, return a simple mapping based on shop type
        
        restock_items = {}
        
        # Get all items in the database
        items = db.query(DBItem).all()
        
        # Filter by shop type
        if shop.shop_type == "blacksmith":
            for item in items:
                if item.category in ["weapon", "armor", "tool"]:
                    restock_items[item.id] = 5
        elif shop.shop_type == "alchemist":
            for item in items:
                if item.category in ["potion", "material"]:
                    restock_items[item.id] = 10
        elif shop.shop_type == "general_store":
            for item in items:
                if item.category in ["food", "miscellaneous", "tool"]:
                    restock_items[item.id] = 15
        elif shop.shop_type == "magic_shop":
            for item in items:
                if item.category in ["magical", "potion"]:
                    restock_items[item.id] = 3
        else:
            # Generic restock
            for item in items:
                restock_items[item.id] = 5
        
        return restock_items