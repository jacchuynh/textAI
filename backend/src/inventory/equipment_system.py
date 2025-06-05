"""
Equipment System - Character equipment management

This module provides equipment management for players and NPCs, including
equipment slots, conflict resolution, and stat bonuses.
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from .item_definitions import ItemData, ItemDataRegistry
    from .inventory_models import Inventory

logger = logging.getLogger("inventory.equipment")


class EquipmentSlot(str, Enum):
    """Equipment slot types for character equipment."""
    # Weapon slots
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    
    # Armor slots
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    
    # Accessory slots
    NECK = "neck"
    RING_LEFT = "ring_left"
    RING_RIGHT = "ring_right"
    BRACELET = "bracelet"
    BELT = "belt"
    
    # Special slots
    BACK = "back"  # cloaks, capes
    AMMO = "ammo"  # arrows, bolts


@dataclass
class EquippedItem:
    """Represents an equipped item with slot information."""
    item_id: str
    slot: EquipmentSlot
    equipped_at: datetime = field(default_factory=datetime.utcnow)
    instance_properties: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "slot": self.slot.value,
            "equipped_at": self.equipped_at.isoformat(),
            "instance_properties": self.instance_properties or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquippedItem':
        """Create from dictionary."""
        return cls(
            item_id=data["item_id"],
            slot=EquipmentSlot(data["slot"]),
            equipped_at=datetime.fromisoformat(data["equipped_at"]),
            instance_properties=data.get("instance_properties")
        )


class EquipmentManager:
    """Manages equipped items for a single entity (player or NPC)."""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self._equipped_items: Dict[EquipmentSlot, EquippedItem] = {}
    
    def equip_item(self, item_id: str, item_data: 'ItemData', 
                   inventory: 'Inventory', item_registry: 'ItemDataRegistry',
                   preferred_slot: Optional[EquipmentSlot] = None) -> Dict[str, Any]:
        """
        Equip an item from inventory.
        
        Args:
            item_id: Item to equip
            item_data: Item definition
            inventory: Source inventory
            item_registry: Item registry for lookups
            preferred_slot: Preferred slot (for items that can go in multiple slots)
            
        Returns:
            Dict with success status and details
        """
        # Check if item is in inventory
        if not inventory.has_item(item_id, 1):
            return {
                "success": False,
                "message": f"You don't have {item_data.name} in your inventory.",
                "data": {}
            }
        
        # Determine available slots for this item
        available_slots = self._get_available_slots_for_item(item_data)
        if not available_slots:
            return {
                "success": False,
                "message": f"{item_data.name} cannot be equipped.",
                "data": {"reason": "no_valid_slots"}
            }
        
        # Choose slot
        target_slot = self._choose_equipment_slot(
            available_slots, preferred_slot, item_data
        )
        
        # Check for conflicts and handle unequipping
        unequipped_items = []
        conflicts = self._check_slot_conflicts(target_slot, item_data)
        
        for conflicted_slot in conflicts:
            if conflicted_slot in self._equipped_items:
                unequipped_item = self._unequip_from_slot(
                    conflicted_slot, inventory, item_registry
                )
                if unequipped_item["success"]:
                    unequipped_items.append(unequipped_item["data"])
                else:
                    # If we can't unequip, fail the operation
                    return {
                        "success": False,
                        "message": f"Cannot unequip {unequipped_item['message']} to make room.",
                        "data": {"reason": "unequip_failed"}
                    }
        
        # Remove item from inventory
        if not inventory.remove_item(item_id, 1):
            return {
                "success": False,
                "message": f"Failed to remove {item_data.name} from inventory.",
                "data": {"reason": "inventory_removal_failed"}
            }
        
        # Equip the item
        equipped_item = EquippedItem(
            item_id=item_id,
            slot=target_slot
        )
        
        self._equipped_items[target_slot] = equipped_item
        
        # Generate response message
        message = f"You equip {item_data.name}"
        if target_slot.value.replace('_', ' '):
            message += f" on your {target_slot.value.replace('_', ' ')}"
        message += "."
        
        if unequipped_items:
            unequipped_names = [item["item_name"] for item in unequipped_items]
            message += f" You unequip {', '.join(unequipped_names)} first."
        
        logger.info(f"Entity {self.entity_id} equipped {item_id} in slot {target_slot}")
        
        return {
            "success": True,
            "message": message,
            "data": {
                "equipped_item": equipped_item.to_dict(),
                "slot": target_slot.value,
                "unequipped_items": unequipped_items
            }
        }
    
    def unequip_item(self, item_id: Optional[str], slot: Optional[EquipmentSlot],
                     inventory: 'Inventory', item_registry: 'ItemDataRegistry') -> Dict[str, Any]:
        """
        Unequip an item by item ID or slot.
        
        Args:
            item_id: Item to unequip (if None, use slot)
            slot: Slot to unequip from (if None, find item by ID)
            inventory: Target inventory
            item_registry: Item registry for lookups
            
        Returns:
            Dict with success status and details
        """
        # Find the item/slot to unequip
        target_slot = None
        target_item = None
        
        if slot:
            if slot in self._equipped_items:
                target_slot = slot
                target_item = self._equipped_items[slot]
            else:
                return {
                    "success": False,
                    "message": f"Nothing is equipped in your {slot.value.replace('_', ' ')}.",
                    "data": {}
                }
        elif item_id:
            # Find slot by item ID
            for eq_slot, eq_item in self._equipped_items.items():
                if eq_item.item_id == item_id:
                    target_slot = eq_slot
                    target_item = eq_item
                    break
            
            if not target_slot:
                item_data = item_registry.get_item_data(item_id)
                item_name = item_data.name if item_data else item_id
                return {
                    "success": False,
                    "message": f"You don't have {item_name} equipped.",
                    "data": {}
                }
        else:
            return {
                "success": False,
                "message": "Must specify either item or equipment slot to unequip.",
                "data": {"reason": "missing_parameters"}
            }
        
        return self._unequip_from_slot(target_slot, inventory, item_registry)
    
    def _unequip_from_slot(self, slot: EquipmentSlot, inventory: 'Inventory',
                          item_registry: 'ItemDataRegistry') -> Dict[str, Any]:
        """Internal method to unequip from a specific slot."""
        if slot not in self._equipped_items:
            return {
                "success": False,
                "message": f"Nothing equipped in {slot.value.replace('_', ' ')}.",
                "data": {}
            }
        
        equipped_item = self._equipped_items[slot]
        item_data = item_registry.get_item_data(equipped_item.item_id)
        
        if not item_data:
            return {
                "success": False,
                "message": f"Cannot find item data for equipped item {equipped_item.item_id}.",
                "data": {"reason": "missing_item_data"}
            }
        
        # Check if inventory has space by getting item data and using _can_add
        item_data = item_registry.get_item_data(equipped_item.item_id)
        if not item_data or not inventory._can_add(equipped_item.item_id, 1, item_data):
            return {
                "success": False,
                "message": f"Not enough space in inventory to unequip {item_data.name if item_data else 'item'}.",
                "data": {"reason": "inventory_full"}
            }
        
        # Remove from equipment
        del self._equipped_items[slot]
        
        # Add to inventory
        if inventory.add_item(equipped_item.item_id, 1, item_registry):
            logger.info(f"Entity {self.entity_id} unequipped {equipped_item.item_id} from slot {slot}")
            
            return {
                "success": True,
                "message": f"You unequip {item_data.name}.",
                "data": {
                    "item_id": equipped_item.item_id,
                    "item_name": item_data.name,
                    "slot": slot.value,
                    "unequipped_at": datetime.utcnow().isoformat()
                }
            }
        else:
            # Re-equip if adding to inventory failed
            self._equipped_items[slot] = equipped_item
            return {
                "success": False,
                "message": f"Failed to add {item_data.name} to inventory.",
                "data": {"reason": "inventory_add_failed"}
            }
    
    def get_equipped_items(self) -> Dict[str, Dict[str, Any]]:
        """Get all equipped items with their data."""
        return {
            slot.value: item.to_dict() 
            for slot, item in self._equipped_items.items()
        }
    
    def get_equipped_in_slot(self, slot: EquipmentSlot) -> Optional[EquippedItem]:
        """Get item equipped in a specific slot."""
        return self._equipped_items.get(slot)
    
    def is_slot_occupied(self, slot: EquipmentSlot) -> bool:
        """Check if a slot has an item equipped."""
        return slot in self._equipped_items
    
    def get_equipment_stats(self, item_registry: 'ItemDataRegistry') -> Dict[str, Any]:
        """Calculate total stats from all equipped items."""
        total_stats = {
            "armor": 0,
            "damage": 0,
            "strength": 0,
            "dexterity": 0,
            "intelligence": 0,
            "constitution": 0,
            "resistances": {},
            "special_effects": []
        }
        
        for equipped_item in self._equipped_items.values():
            item_data = item_registry.get_item_data(equipped_item.item_id)
            if item_data and item_data.properties:
                props = item_data.properties
                
                # Add numeric stats
                for stat in ["armor", "damage", "strength", "dexterity", 
                           "intelligence", "constitution"]:
                    if stat in props:
                        try:
                            # Ensure the value is numeric
                            stat_value = props[stat]
                            if isinstance(stat_value, (int, float)):
                                total_stats[stat] += stat_value
                            elif isinstance(stat_value, dict):
                                # Handle complex stat definitions (e.g., {"base": 5, "bonus": 2})
                                if "base" in stat_value:
                                    total_stats[stat] += stat_value["base"]
                                if "bonus" in stat_value:
                                    total_stats[stat] += stat_value["bonus"]
                        except (TypeError, ValueError) as e:
                            logger.warning(f"Invalid stat value for {stat} in item {item_data.item_id}: {props[stat]}")
                
                # Add resistances
                if "resistances" in props:
                    for res_type, value in props["resistances"].items():
                        if res_type not in total_stats["resistances"]:
                            total_stats["resistances"][res_type] = 0
                        total_stats["resistances"][res_type] += value
                
                # Add special effects
                if "special_effects" in props:
                    total_stats["special_effects"].extend(props["special_effects"])
        
        return total_stats
    
    def _get_available_slots_for_item(self, item_data: 'ItemData') -> List[EquipmentSlot]:
        """Determine which slots an item can be equipped in."""
        available_slots = []
        item_type = item_data.item_type
        props = item_data.properties or {}
        
        if item_type.value == "WEAPON":
            weapon_type = props.get("weapon_type", "").lower()
            
            # All weapons can go in main hand
            available_slots.append(EquipmentSlot.MAIN_HAND)
            
            # Some weapons can be dual-wielded or used as off-hand
            if weapon_type in ["dagger", "short_sword", "light"]:
                available_slots.append(EquipmentSlot.OFF_HAND)
                
        elif item_type.value == "SHIELD":
            available_slots.append(EquipmentSlot.OFF_HAND)
            
        elif item_type.value == "ARMOR":
            # Check armor slots from item properties
            slots = props.get("slots", [])
            for slot_name in slots:
                try:
                    slot = EquipmentSlot(slot_name.lower())
                    available_slots.append(slot)
                except ValueError:
                    logger.warning(f"Unknown armor slot: {slot_name}")
            
            # Fallback based on armor type
            if not available_slots:
                armor_type = props.get("armor_type", "").lower()
                if armor_type in ["chest", "body", "torso"]:
                    available_slots.append(EquipmentSlot.CHEST)
                elif armor_type in ["head", "helmet"]:
                    available_slots.append(EquipmentSlot.HEAD)
                elif armor_type in ["legs", "pants", "greaves"]:
                    available_slots.append(EquipmentSlot.LEGS)
                elif armor_type in ["feet", "boots", "shoes"]:
                    available_slots.append(EquipmentSlot.FEET)
                elif armor_type in ["hands", "gloves", "gauntlets"]:
                    available_slots.append(EquipmentSlot.HANDS)
                    
        elif item_type.value == "ACCESSORY":
            accessory_type = props.get("accessory_type", "").lower()
            if accessory_type == "ring":
                available_slots.extend([EquipmentSlot.RING_LEFT, EquipmentSlot.RING_RIGHT])
            elif accessory_type == "necklace":
                available_slots.append(EquipmentSlot.NECK)
            elif accessory_type == "bracelet":
                available_slots.append(EquipmentSlot.BRACELET)
            elif accessory_type == "belt":
                available_slots.append(EquipmentSlot.BELT)
            elif accessory_type == "cloak":
                available_slots.append(EquipmentSlot.BACK)
        
        return available_slots
    
    def _choose_equipment_slot(self, available_slots: List[EquipmentSlot],
                              preferred_slot: Optional[EquipmentSlot],
                              item_data: 'ItemData') -> EquipmentSlot:
        """Choose the best slot for an item."""
        # Use preferred slot if valid and available
        if preferred_slot and preferred_slot in available_slots:
            return preferred_slot
        
        # For rings, prefer left if empty, otherwise right
        ring_slots = [s for s in available_slots if s in [EquipmentSlot.RING_LEFT, EquipmentSlot.RING_RIGHT]]
        if ring_slots:
            if EquipmentSlot.RING_LEFT in ring_slots and not self.is_slot_occupied(EquipmentSlot.RING_LEFT):
                return EquipmentSlot.RING_LEFT
            elif EquipmentSlot.RING_RIGHT in ring_slots:
                return EquipmentSlot.RING_RIGHT
        
        # Default to first available slot
        return available_slots[0]
    
    def _check_slot_conflicts(self, target_slot: EquipmentSlot, 
                             item_data: 'ItemData') -> List[EquipmentSlot]:
        """Check for equipment conflicts and return slots that need to be cleared."""
        conflicts = []
        
        # Two-handed weapons conflict with off-hand
        if (target_slot == EquipmentSlot.MAIN_HAND and 
            item_data.item_type.value == "WEAPON" and
            item_data.properties and 
            item_data.properties.get("two_handed", False)):
            conflicts.append(EquipmentSlot.OFF_HAND)
        
        # Off-hand items conflict with two-handed weapons
        elif (target_slot == EquipmentSlot.OFF_HAND and 
              EquipmentSlot.MAIN_HAND in self._equipped_items):
            main_hand_item = self._equipped_items[EquipmentSlot.MAIN_HAND]
            # Would need to check if main hand weapon is two-handed
            # For now, assume no conflict
        
        # The target slot itself is a conflict if occupied
        if target_slot in self._equipped_items:
            conflicts.append(target_slot)
        
        return conflicts
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize equipment to dictionary."""
        return {
            "entity_id": self.entity_id,
            "equipped_items": {
                slot.value: item.to_dict()
                for slot, item in self._equipped_items.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquipmentManager':
        """Deserialize equipment from dictionary."""
        manager = cls(data["entity_id"])
        
        for slot_name, item_data in data.get("equipped_items", {}).items():
            slot = EquipmentSlot(slot_name)
            equipped_item = EquippedItem.from_dict(item_data)
            manager._equipped_items[slot] = equipped_item
        
        return manager


class EquipmentSystem:
    """System for managing equipment across all entities."""
    
    def __init__(self):
        self._equipment_managers: Dict[str, EquipmentManager] = {}
    
    def get_equipment_manager(self, entity_id: str) -> EquipmentManager:
        """Get or create equipment manager for an entity."""
        if entity_id not in self._equipment_managers:
            self._equipment_managers[entity_id] = EquipmentManager(entity_id)
        return self._equipment_managers[entity_id]
    
    def equip_item(self, entity_id: str, item_id: str, 
                   inventory: 'Inventory', item_registry: 'ItemDataRegistry',
                   preferred_slot: Optional[str] = None) -> Dict[str, Any]:
        """Equip an item for an entity."""
        manager = self.get_equipment_manager(entity_id)
        item_data = item_registry.get_item_data(item_id)
        
        if not item_data:
            return {
                "success": False,
                "message": f"Unknown item: {item_id}",
                "data": {}
            }
        
        # Convert string slot to enum if provided
        slot_enum = None
        if preferred_slot:
            try:
                slot_enum = EquipmentSlot(preferred_slot.lower())
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid equipment slot: {preferred_slot}",
                    "data": {}
                }
        
        return manager.equip_item(item_id, item_data, inventory, item_registry, slot_enum)
    
    def unequip_item(self, entity_id: str, item_id: Optional[str] = None,
                     slot: Optional[str] = None, inventory: 'Inventory' = None,
                     item_registry: 'ItemDataRegistry' = None) -> Dict[str, Any]:
        """Unequip an item for an entity."""
        if entity_id not in self._equipment_managers:
            return {
                "success": False,
                "message": "No equipment found.",
                "data": {}
            }
        
        manager = self._equipment_managers[entity_id]
        
        # Convert string slot to enum if provided
        slot_enum = None
        if slot:
            try:
                slot_enum = EquipmentSlot(slot.lower())
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid equipment slot: {slot}",
                    "data": {}
                }
        
        return manager.unequip_item(item_id, slot_enum, inventory, item_registry)
    
    def get_equipped_items(self, entity_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all equipped items for an entity."""
        if entity_id not in self._equipment_managers:
            return {}
        return self._equipment_managers[entity_id].get_equipped_items()
    
    def get_equipment_stats(self, entity_id: str, 
                           item_registry: 'ItemDataRegistry') -> Dict[str, Any]:
        """Get total equipment stats for an entity."""
        if entity_id not in self._equipment_managers:
            return {
                "armor": 0, "damage": 0, "strength": 0, "dexterity": 0,
                "intelligence": 0, "constitution": 0, "resistances": {},
                "special_effects": []
            }
        
        return self._equipment_managers[entity_id].get_equipment_stats(item_registry)
