"""
Transaction Service Module

This module handles economic transactions between players, shops, and businesses,
including buying, selling, and trading items. It integrates with Celery for
processing complex transactions asynchronously.
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
    DBItem, DBShop, DBLocation, DBMarketRegionInfo, DBCharacter
)

# Import Celery integration for async processing
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
from backend.src.narrative_engine.event_bus import get_event_bus, Event

# Import related services
from backend.src.economy.services.shop_service import ShopService

logger = logging.getLogger(__name__)

class TransactionService:
    """
    Service for handling economic transactions in the game world.
    """
    
    def __init__(self):
        """Initialize the transaction service."""
        self.logger = logging.getLogger("TransactionService")
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration for async operations
        self.celery_integration = NarrativeEngineCeleryIntegration()
        
        # Initialize related services
        self.shop_service = ShopService()
    
    def player_buy_item(self, 
                      db: Session, 
                      player_id: str, 
                      shop_id: str, 
                      item_id: str, 
                      quantity: int = 1) -> Dict[str, Any]:
        """
        Process a player buying an item from a shop.
        
        Args:
            db: Database session
            player_id: Player identifier
            shop_id: Shop identifier
            item_id: Item identifier
            quantity: Quantity to buy
            
        Returns:
            Transaction result
        """
        # Get the player
        player = db.query(DBCharacter).filter(DBCharacter.id == player_id).first()
        
        if not player:
            return {"error": f"Player {player_id} not found"}
        
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            return {"error": f"Shop {shop_id} not found"}
        
        # Get the item
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        
        if not item:
            return {"error": f"Item {item_id} not found"}
        
        # Check if the shop has the item in sufficient quantity
        if item_id not in shop.inventory:
            return {"error": f"Item {item_id} not available in shop {shop_id}"}
        
        shop_slot_data = shop.inventory[item_id]
        shop_slot = InventorySlot(**shop_slot_data)
        
        if shop_slot.quantity < quantity:
            return {"error": f"Shop {shop_id} only has {shop_slot.quantity} of item {item_id}"}
        
        # Calculate the price
        relationship_modifier = 1.0  # Default, could be queried from relationship system
        unit_price = self.shop_service.calculate_item_price(
            db=db,
            item_id=item_id,
            shop_id=shop_id,
            relationship_modifier=relationship_modifier,
            is_buying=True  # Player is buying from shop
        )
        
        # If item has a price override, use that instead
        if shop_slot.price_override is not None:
            unit_price = shop_slot.price_override
            
        total_price = unit_price * quantity
        
        # Check if the player has enough currency
        if player.currency < total_price:
            return {"error": f"Player {player_id} does not have enough currency. Needs {total_price}, has {player.currency}"}
        
        # Begin transaction
        try:
            # Update player currency
            player.currency -= total_price
            
            # Update shop currency
            shop.currency_balance += total_price
            
            # Remove item from shop inventory
            success = self.shop_service.remove_item_from_shop_inventory(
                db=db,
                shop_id=shop_id,
                item_id=item_id,
                quantity=quantity
            )
            
            if not success:
                db.rollback()
                return {"error": f"Failed to remove item {item_id} from shop {shop_id}"}
            
            # Add item to player inventory
            player_inventory = player.inventory or {}
            
            # Check if player already has this item
            if item_id in player_inventory:
                player_slot_data = player_inventory[item_id]
                player_slot = InventorySlot(**player_slot_data)
                
                # If item is stackable, add to quantity
                if item.stackable:
                    # Check max stack size
                    new_quantity = player_slot.quantity + quantity
                    if new_quantity > item.max_stack:
                        # This would be handled differently in a real implementation
                        # For now, just cap at max stack
                        player_slot.quantity = item.max_stack
                    else:
                        player_slot.quantity = new_quantity
                else:
                    # Non-stackable items get new entries
                    # For simplicity, we'll just update the quantity
                    # In a real implementation, this would create new inventory slots
                    player_slot.quantity += quantity
                    
                # Update player inventory
                player_inventory[item_id] = player_slot.dict()
            else:
                # Create new inventory slot
                player_slot = InventorySlot(
                    quantity=quantity,
                    condition=shop_slot.condition,  # Inherit condition from shop
                    custom_data={}
                )
                
                # Add to player inventory
                player_inventory[item_id] = player_slot.dict()
            
            # Update player inventory
            player.inventory = player_inventory
            
            # Commit transaction
            db.commit()
            
            # Get location for region ID
            location = db.query(DBLocation).filter(DBLocation.id == shop.location_id).first()
            region_id = location.region_id if location else "unknown"
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="market_transaction",
                data={
                    "transaction_type": "player_buy",
                    "player_id": player_id,
                    "shop_id": shop_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "region_id": region_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="transaction_service"
            ))
            
            # Return success result
            return {
                "transaction_type": "player_buy",
                "status": "success",
                "player_id": player_id,
                "shop_id": shop_id,
                "item_id": item_id,
                "item_name": item.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "player_currency_remaining": player.currency,
                "shop_currency_balance": shop.currency_balance
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error in player_buy_item: {e}")
            return {"error": f"Transaction failed: {str(e)}"}
    
    def player_sell_item(self, 
                       db: Session, 
                       player_id: str, 
                       shop_id: str, 
                       item_id: str, 
                       quantity: int = 1) -> Dict[str, Any]:
        """
        Process a player selling an item to a shop.
        
        Args:
            db: Database session
            player_id: Player identifier
            shop_id: Shop identifier
            item_id: Item identifier
            quantity: Quantity to sell
            
        Returns:
            Transaction result
        """
        # Get the player
        player = db.query(DBCharacter).filter(DBCharacter.id == player_id).first()
        
        if not player:
            return {"error": f"Player {player_id} not found"}
        
        # Get the shop
        shop = db.query(DBShop).filter(DBShop.id == shop_id).first()
        
        if not shop:
            return {"error": f"Shop {shop_id} not found"}
        
        # Get the item
        item = db.query(DBItem).filter(DBItem.id == item_id).first()
        
        if not item:
            return {"error": f"Item {item_id} not found"}
        
        # Check if the player has the item in sufficient quantity
        player_inventory = player.inventory or {}
        
        if item_id not in player_inventory:
            return {"error": f"Player {player_id} does not have item {item_id}"}
        
        player_slot_data = player_inventory[item_id]
        player_slot = InventorySlot(**player_slot_data)
        
        if player_slot.quantity < quantity:
            return {"error": f"Player {player_id} only has {player_slot.quantity} of item {item_id}"}
        
        # Calculate the price
        relationship_modifier = 1.0  # Default, could be queried from relationship system
        unit_price = self.shop_service.calculate_item_price(
            db=db,
            item_id=item_id,
            shop_id=shop_id,
            relationship_modifier=relationship_modifier,
            is_buying=False  # Player is selling to shop
        )
        
        total_price = unit_price * quantity
        
        # Check if the shop has enough currency
        if shop.currency_balance < total_price:
            return {"error": f"Shop {shop_id} does not have enough currency. Needs {total_price}, has {shop.currency_balance}"}
        
        # Begin transaction
        try:
            # Update player currency
            player.currency += total_price
            
            # Update shop currency
            shop.currency_balance -= total_price
            
            # Remove item from player inventory
            player_slot.quantity -= quantity
            
            if player_slot.quantity <= 0:
                # Remove item from inventory
                player_inventory.pop(item_id)
            else:
                # Update inventory
                player_inventory[item_id] = player_slot.dict()
            
            # Update player inventory
            player.inventory = player_inventory
            
            # Add item to shop inventory
            success = self.shop_service.add_item_to_shop_inventory(
                db=db,
                shop_id=shop_id,
                item_id=item_id,
                quantity=quantity,
                price_override=None  # No price override when selling to shop
            )
            
            if not success:
                db.rollback()
                return {"error": f"Failed to add item {item_id} to shop {shop_id}"}
            
            # Commit transaction
            db.commit()
            
            # Get location for region ID
            location = db.query(DBLocation).filter(DBLocation.id == shop.location_id).first()
            region_id = location.region_id if location else "unknown"
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="market_transaction",
                data={
                    "transaction_type": "player_sell",
                    "player_id": player_id,
                    "shop_id": shop_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "region_id": region_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="transaction_service"
            ))
            
            # Return success result
            return {
                "transaction_type": "player_sell",
                "status": "success",
                "player_id": player_id,
                "shop_id": shop_id,
                "item_id": item_id,
                "item_name": item.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "player_currency_balance": player.currency,
                "shop_currency_remaining": shop.currency_balance
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error in player_sell_item: {e}")
            return {"error": f"Transaction failed: {str(e)}"}
    
    async def process_npc_trade_transaction(self,
                                         db: Session,
                                         npc1_id: str,
                                         npc2_id: str,
                                         items_exchanged: Dict[str, Dict[str, int]],
                                         currency_exchanged: Dict[str, float],
                                         async_processing: bool = True) -> Dict[str, Any]:
        """
        Process a trade transaction between two NPCs.
        
        Args:
            db: Database session
            npc1_id: First NPC identifier
            npc2_id: Second NPC identifier
            items_exchanged: Items exchanged (e.g., {"npc1_to_npc2": {"item1": 2}, "npc2_to_npc1": {"item2": 1}})
            currency_exchanged: Currency exchanged (e.g., {"npc1_to_npc2": 50.0, "npc2_to_npc1": 0.0})
            async_processing: Whether to process asynchronously
            
        Returns:
            Transaction result or task information
        """
        # Use Celery for async processing
        if async_processing:
            # This would be defined in economy/tasks.py
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.process_npc_trade_task",
                task_args=[npc1_id, npc2_id],
                task_kwargs={
                    "items_exchanged": items_exchanged,
                    "currency_exchanged": currency_exchanged
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "transaction_type": "npc_trade",
                "npc1_id": npc1_id,
                "npc2_id": npc2_id,
                "status": "processing",
                "message": "NPC trade transaction dispatched for asynchronous processing"
            }
        
        # For synchronous processing, process the trade here
        # This is a simplified implementation
        
        # Get the NPCs
        npc1 = db.query(DBCharacter).filter(DBCharacter.id == npc1_id).first()
        npc2 = db.query(DBCharacter).filter(DBCharacter.id == npc2_id).first()
        
        if not npc1 or not npc2:
            return {"error": f"One or both NPCs not found: {npc1_id}, {npc2_id}"}
        
        # Begin transaction
        try:
            # Process currency exchange
            npc1_to_npc2_currency = currency_exchanged.get("npc1_to_npc2", 0.0)
            npc2_to_npc1_currency = currency_exchanged.get("npc2_to_npc1", 0.0)
            
            # Check if NPCs have enough currency
            if npc1.currency < npc1_to_npc2_currency:
                return {"error": f"NPC {npc1_id} does not have enough currency for the trade"}
            
            if npc2.currency < npc2_to_npc1_currency:
                return {"error": f"NPC {npc2_id} does not have enough currency for the trade"}
            
            # Update currencies
            npc1.currency = npc1.currency - npc1_to_npc2_currency + npc2_to_npc1_currency
            npc2.currency = npc2.currency - npc2_to_npc1_currency + npc1_to_npc2_currency
            
            # Process item exchange
            npc1_to_npc2_items = items_exchanged.get("npc1_to_npc2", {})
            npc2_to_npc1_items = items_exchanged.get("npc2_to_npc1", {})
            
            # Get inventories
            npc1_inventory = npc1.inventory or {}
            npc2_inventory = npc2.inventory or {}
            
            # Check if NPCs have the items
            for item_id, quantity in npc1_to_npc2_items.items():
                if item_id not in npc1_inventory or npc1_inventory[item_id]["quantity"] < quantity:
                    return {"error": f"NPC {npc1_id} does not have enough of item {item_id}"}
            
            for item_id, quantity in npc2_to_npc1_items.items():
                if item_id not in npc2_inventory or npc2_inventory[item_id]["quantity"] < quantity:
                    return {"error": f"NPC {npc2_id} does not have enough of item {item_id}"}
            
            # Transfer items from NPC1 to NPC2
            for item_id, quantity in npc1_to_npc2_items.items():
                # Get the item
                item = db.query(DBItem).filter(DBItem.id == item_id).first()
                
                if not item:
                    return {"error": f"Item {item_id} not found"}
                
                # Remove from NPC1
                npc1_slot_data = npc1_inventory[item_id]
                npc1_slot = InventorySlot(**npc1_slot_data)
                npc1_slot.quantity -= quantity
                
                if npc1_slot.quantity <= 0:
                    npc1_inventory.pop(item_id)
                else:
                    npc1_inventory[item_id] = npc1_slot.dict()
                
                # Add to NPC2
                if item_id in npc2_inventory:
                    npc2_slot_data = npc2_inventory[item_id]
                    npc2_slot = InventorySlot(**npc2_slot_data)
                    
                    if item.stackable:
                        # Add to existing stack
                        npc2_slot.quantity += quantity
                    else:
                        # Non-stackable items
                        # For simplicity, we'll just update the quantity
                        npc2_slot.quantity += quantity
                        
                    npc2_inventory[item_id] = npc2_slot.dict()
                else:
                    # Create new inventory slot
                    npc2_slot = InventorySlot(
                        quantity=quantity,
                        condition=npc1_slot_data["condition"],
                        custom_data={}
                    )
                    
                    npc2_inventory[item_id] = npc2_slot.dict()
            
            # Transfer items from NPC2 to NPC1
            for item_id, quantity in npc2_to_npc1_items.items():
                # Get the item
                item = db.query(DBItem).filter(DBItem.id == item_id).first()
                
                if not item:
                    return {"error": f"Item {item_id} not found"}
                
                # Remove from NPC2
                npc2_slot_data = npc2_inventory[item_id]
                npc2_slot = InventorySlot(**npc2_slot_data)
                npc2_slot.quantity -= quantity
                
                if npc2_slot.quantity <= 0:
                    npc2_inventory.pop(item_id)
                else:
                    npc2_inventory[item_id] = npc2_slot.dict()
                
                # Add to NPC1
                if item_id in npc1_inventory:
                    npc1_slot_data = npc1_inventory[item_id]
                    npc1_slot = InventorySlot(**npc1_slot_data)
                    
                    if item.stackable:
                        # Add to existing stack
                        npc1_slot.quantity += quantity
                    else:
                        # Non-stackable items
                        # For simplicity, we'll just update the quantity
                        npc1_slot.quantity += quantity
                        
                    npc1_inventory[item_id] = npc1_slot.dict()
                else:
                    # Create new inventory slot
                    npc1_slot = InventorySlot(
                        quantity=quantity,
                        condition=npc2_slot_data["condition"],
                        custom_data={}
                    )
                    
                    npc1_inventory[item_id] = npc1_slot.dict()
            
            # Update inventories
            npc1.inventory = npc1_inventory
            npc2.inventory = npc2_inventory
            
            # Commit transaction
            db.commit()
            
            # Get NPCs' locations for region ID
            npc1_location_id = npc1.location_id
            npc2_location_id = npc2.location_id
            
            # For simplicity, use the first NPC's location
            location = None
            region_id = "unknown"
            
            if npc1_location_id:
                location = db.query(DBLocation).filter(DBLocation.id == npc1_location_id).first()
                if location:
                    region_id = location.region_id
            
            # Publish event
            self.event_bus.publish(Event(
                event_type="market_transaction",
                data={
                    "transaction_type": "npc_trade",
                    "npc1_id": npc1_id,
                    "npc2_id": npc2_id,
                    "items_exchanged": items_exchanged,
                    "currency_exchanged": currency_exchanged,
                    "region_id": region_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                source="transaction_service"
            ))
            
            # Return success result
            return {
                "transaction_type": "npc_trade",
                "status": "success",
                "npc1_id": npc1_id,
                "npc2_id": npc2_id,
                "items_exchanged": items_exchanged,
                "currency_exchanged": currency_exchanged,
                "npc1_currency_balance": npc1.currency,
                "npc2_currency_balance": npc2.currency
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error in process_npc_trade_transaction: {e}")
            return {"error": f"Trade transaction failed: {str(e)}"}