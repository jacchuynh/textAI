"""
Inventory Models - Core inventory data structures

This module defines the InventorySlot and Inventory classes that manage
collections of items for players, NPCs, and containers.
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from .item_definitions import ItemData, ItemDataRegistry

logger = logging.getLogger("inventory.models")


@dataclass
class InventorySlot:
    """
    Represents an item (or stack of items) within an inventory.
    
    This class handles both stackable items (with quantities) and unique
    items with individual properties.
    """
    item_id: str  # References ItemData.item_id
    quantity: int = 1  # Number of items in this slot
    instance_properties: Optional[Dict[str, Any]] = None  # Unique item properties
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.quantity < 0:
            self.quantity = 0
        
        if self.instance_properties is None:
            self.instance_properties = {}
    
    def add_quantity(self, amount: int) -> int:
        """
        Add to the quantity in this slot.
        
        Args:
            amount: Amount to add
            
        Returns:
            New total quantity
        """
        if amount < 0:
            raise ValueError("Cannot add negative quantity")
        
        self.quantity += amount
        return self.quantity
    
    def remove_quantity(self, amount: int) -> int:
        """
        Remove from the quantity in this slot.
        
        Args:
            amount: Amount to remove
            
        Returns:
            Amount actually removed
        """
        if amount < 0:
            raise ValueError("Cannot remove negative quantity")
        
        removed = min(amount, self.quantity)
        self.quantity -= removed
        return removed
    
    def can_stack_with(self, other: 'InventorySlot') -> bool:
        """
        Check if this slot can be stacked with another slot.
        
        Args:
            other: Another InventorySlot
            
        Returns:
            True if they can be stacked together
        """
        if not isinstance(other, InventorySlot):
            return False
        
        # Must be same item
        if self.item_id != other.item_id:
            return False
        
        # Items with unique properties can't be stacked
        if (self.instance_properties and any(self.instance_properties.values()) or
            other.instance_properties and any(other.instance_properties.values())):
            return False
        
        return True
    
    def merge_with(self, other: 'InventorySlot', max_stack_size: int) -> int:
        """
        Merge another slot into this one, respecting stack limits.
        
        Args:
            other: InventorySlot to merge
            max_stack_size: Maximum items per stack
            
        Returns:
            Quantity that couldn't be merged (overflow)
        """
        if not self.can_stack_with(other):
            return other.quantity
        
        available_space = max_stack_size - self.quantity
        can_merge = min(other.quantity, available_space)
        
        self.quantity += can_merge
        return other.quantity - can_merge
    
    def split(self, amount: int) -> Optional['InventorySlot']:
        """
        Split this slot into two, removing the specified amount.
        
        Args:
            amount: Amount to split off
            
        Returns:
            New InventorySlot with the split amount, or None if invalid
        """
        if amount <= 0 or amount >= self.quantity:
            return None
        
        # Create new slot with split amount
        new_slot = InventorySlot(
            item_id=self.item_id,
            quantity=amount,
            instance_properties=self.instance_properties.copy() if self.instance_properties else {}
        )
        
        # Reduce this slot's quantity
        self.quantity -= amount
        
        return new_slot
    
    def is_empty(self) -> bool:
        """Check if this slot is empty (quantity <= 0)."""
        return self.quantity <= 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "quantity": self.quantity,
            "instance_properties": self.instance_properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventorySlot':
        """Create InventorySlot from dictionary."""
        return cls(
            item_id=data["item_id"],
            quantity=data.get("quantity", 1),
            instance_properties=data.get("instance_properties", {})
        )


class Inventory:
    """
    Represents a collection of items for a specific entity.
    
    This class manages items for players, NPCs, or containers with support
    for capacity limits, weight limits, and item stacking.
    """
    
    def __init__(self, 
                 owner_id: str,
                 capacity_slots: Optional[int] = None,
                 capacity_weight: Optional[float] = None):
        """
        Initialize inventory.
        
        Args:
            owner_id: ID of the entity owning this inventory
            capacity_slots: Maximum number of distinct item types/slots
            capacity_weight: Maximum total weight capacity
        """
        self.owner_id = owner_id
        self.capacity_slots = capacity_slots
        self.capacity_weight = capacity_weight
        self.current_weight = 0.0
        
        # Use list for ordered slots, with empty slots removed automatically
        self._slots: List[InventorySlot] = []
        
        # Cache for quick lookups
        self._item_slot_map: Dict[str, List[int]] = {}  # item_id -> list of slot indices
        
        self._last_modified = datetime.utcnow()
        
        logger.debug(f"Created inventory for {owner_id}")
    
    def _rebuild_cache(self):
        """Rebuild the item->slot mapping cache."""
        self._item_slot_map.clear()
        
        for i, slot in enumerate(self._slots):
            if slot.item_id not in self._item_slot_map:
                self._item_slot_map[slot.item_id] = []
            self._item_slot_map[slot.item_id].append(i)
    
    def _update_weight(self, item_registry: 'ItemDataRegistry'):
        """Recalculate current weight based on items."""
        total_weight = 0.0
        
        for slot in self._slots:
            item_data = item_registry.get_item_data(slot.item_id)
            if item_data:
                total_weight += item_data.weight * slot.quantity
        
        self.current_weight = total_weight
        self._last_modified = datetime.utcnow()
    
    def _can_add(self, item_id: str, quantity: int, item_data: 'ItemData') -> bool:
        """
        Check if items can be added to this inventory.
        
        Args:
            item_id: Item identifier
            quantity: Quantity to add
            item_data: ItemData instance
            
        Returns:
            True if items can be added
        """
        # Check weight capacity
        if self.capacity_weight is not None:
            additional_weight = item_data.weight * quantity
            if self.current_weight + additional_weight > self.capacity_weight:
                return False
        
        # Check if we can stack with existing slots
        existing_slots = self._item_slot_map.get(item_id, [])
        
        if item_data.stackable and existing_slots:
            # Try to fit into existing stackable slots
            remaining_quantity = quantity
            
            for slot_idx in existing_slots:
                slot = self._slots[slot_idx]
                available_space = item_data.max_stack_size - slot.quantity
                if available_space > 0:
                    can_fit = min(remaining_quantity, available_space)
                    remaining_quantity -= can_fit
                    
                    if remaining_quantity <= 0:
                        return True
            
            # If we still have remaining quantity, check if we can create new slots
            if remaining_quantity > 0:
                if self.capacity_slots is not None:
                    new_slots_needed = (remaining_quantity + item_data.max_stack_size - 1) // item_data.max_stack_size
                    if len(self._slots) + new_slots_needed > self.capacity_slots:
                        return False
        else:
            # Non-stackable or no existing slots
            if self.capacity_slots is not None:
                new_slots_needed = quantity if not item_data.stackable else (quantity + item_data.max_stack_size - 1) // item_data.max_stack_size
                if len(self._slots) + new_slots_needed > self.capacity_slots:
                    return False
        
        return True
    
    def add_item(self, item_id: str, quantity: int, item_registry: 'ItemDataRegistry') -> bool:
        """
        Add item(s) to the inventory.
        
        Args:
            item_id: Item identifier
            quantity: Quantity to add
            item_registry: ItemDataRegistry for item definitions
            
        Returns:
            True if items were successfully added
        """
        if quantity <= 0:
            return False
        
        item_data = item_registry.get_item_data(item_id)
        if not item_data:
            logger.warning(f"Unknown item ID: {item_id}")
            return False
        
        # Check if we can add these items
        if not self._can_add(item_id, quantity, item_data):
            logger.debug(f"Cannot add {quantity}x {item_id} to inventory {self.owner_id} (capacity exceeded)")
            return False
        
        remaining_quantity = quantity
        
        # Try to add to existing stackable slots first
        if item_data.stackable:
            existing_slots = self._item_slot_map.get(item_id, [])
            
            for slot_idx in existing_slots:
                if remaining_quantity <= 0:
                    break
                
                slot = self._slots[slot_idx]
                available_space = item_data.max_stack_size - slot.quantity
                
                if available_space > 0:
                    can_add = min(remaining_quantity, available_space)
                    slot.add_quantity(can_add)
                    remaining_quantity -= can_add
        
        # Create new slots for remaining quantity
        while remaining_quantity > 0:
            if item_data.stackable:
                slot_quantity = min(remaining_quantity, item_data.max_stack_size)
            else:
                slot_quantity = 1
            
            new_slot = InventorySlot(item_id=item_id, quantity=slot_quantity)
            self._slots.append(new_slot)
            
            # Update cache
            if item_id not in self._item_slot_map:
                self._item_slot_map[item_id] = []
            self._item_slot_map[item_id].append(len(self._slots) - 1)
            
            remaining_quantity -= slot_quantity
        
        # Update weight and modification time
        self._update_weight(item_registry)
        
        logger.debug(f"Added {quantity}x {item_id} to inventory {self.owner_id}")
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove item(s) from the inventory.
        
        Args:
            item_id: Item identifier
            quantity: Quantity to remove
            
        Returns:
            True if items were successfully removed
        """
        if quantity <= 0:
            return False
        
        if not self.has_item(item_id, quantity):
            return False
        
        remaining_to_remove = quantity
        slots_to_remove = []
        
        # Get slots containing this item
        slot_indices = self._item_slot_map.get(item_id, []).copy()
        
        for slot_idx in slot_indices:
            if remaining_to_remove <= 0:
                break
            
            slot = self._slots[slot_idx]
            removed = slot.remove_quantity(remaining_to_remove)
            remaining_to_remove -= removed
            
            # Mark empty slots for removal
            if slot.is_empty():
                slots_to_remove.append(slot_idx)
        
        # Remove empty slots (in reverse order to maintain indices)
        for slot_idx in sorted(slots_to_remove, reverse=True):
            del self._slots[slot_idx]
        
        # Rebuild cache after slot removal
        self._rebuild_cache()
        self._last_modified = datetime.utcnow()
        
        logger.debug(f"Removed {quantity}x {item_id} from inventory {self.owner_id}")
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Check if inventory contains enough of an item.
        
        Args:
            item_id: Item identifier
            quantity: Required quantity
            
        Returns:
            True if inventory has enough items
        """
        return self.get_item_quantity(item_id) >= quantity
    
    def get_item_quantity(self, item_id: str) -> int:
        """
        Get total quantity of a specific item.
        
        Args:
            item_id: Item identifier
            
        Returns:
            Total quantity of the item
        """
        total = 0
        slot_indices = self._item_slot_map.get(item_id, [])
        
        for slot_idx in slot_indices:
            if slot_idx < len(self._slots):
                total += self._slots[slot_idx].quantity
        
        return total
    
    def get_all_items(self) -> List[InventorySlot]:
        """Get all items in the inventory."""
        return [slot for slot in self._slots if not slot.is_empty()]
    
    def get_item_summary(self) -> Dict[str, int]:
        """
        Get a summary of all items by ID and quantity.
        
        Returns:
            Dictionary mapping item_id to total quantity
        """
        summary = {}
        for slot in self._slots:
            if not slot.is_empty():
                summary[slot.item_id] = summary.get(slot.item_id, 0) + slot.quantity
        
        return summary
    
    def get_available_slots(self) -> Optional[int]:
        """
        Get number of available inventory slots.
        
        Returns:
            Number of available slots, or None if no limit
        """
        if self.capacity_slots is None:
            return None
        
        return max(0, self.capacity_slots - len(self._slots))
    
    def get_available_weight(self) -> Optional[float]:
        """
        Get available weight capacity.
        
        Returns:
            Available weight capacity, or None if no limit
        """
        if self.capacity_weight is None:
            return None
        
        return max(0.0, self.capacity_weight - self.current_weight)
    
    def is_full(self) -> bool:
        """Check if inventory is at capacity (slots or weight)."""
        if self.capacity_slots is not None and len(self._slots) >= self.capacity_slots:
            return True
        
        if self.capacity_weight is not None and self.current_weight >= self.capacity_weight:
            return True
        
        return False
    
    def clear(self):
        """Remove all items from the inventory."""
        self._slots.clear()
        self._item_slot_map.clear()
        self.current_weight = 0.0
        self._last_modified = datetime.utcnow()
        
        logger.debug(f"Cleared inventory {self.owner_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "owner_id": self.owner_id,
            "capacity_slots": self.capacity_slots,
            "capacity_weight": self.capacity_weight,
            "current_weight": self.current_weight,
            "slots": [slot.to_dict() for slot in self._slots],
            "last_modified": self._last_modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventory':
        """Create Inventory from dictionary."""
        inventory = cls(
            owner_id=data["owner_id"],
            capacity_slots=data.get("capacity_slots"),
            capacity_weight=data.get("capacity_weight")
        )
        
        inventory.current_weight = data.get("current_weight", 0.0)
        
        # Load slots
        slots_data = data.get("slots", [])
        for slot_data in slots_data:
            slot = InventorySlot.from_dict(slot_data)
            inventory._slots.append(slot)
        
        # Rebuild cache
        inventory._rebuild_cache()
        
        # Set modification time
        if "last_modified" in data:
            inventory._last_modified = datetime.fromisoformat(data["last_modified"])
        
        return inventory
    
    def get_stats(self) -> Dict[str, Any]:
        """Get inventory statistics."""
        return {
            "owner_id": self.owner_id,
            "total_items": sum(slot.quantity for slot in self._slots),
            "unique_items": len(self._item_slot_map),
            "used_slots": len(self._slots),
            "capacity_slots": self.capacity_slots,
            "available_slots": self.get_available_slots(),
            "current_weight": self.current_weight,
            "capacity_weight": self.capacity_weight,
            "available_weight": self.get_available_weight(),
            "is_full": self.is_full(),
            "last_modified": self._last_modified.isoformat()
        }
