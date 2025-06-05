"""
Inventory System - Main system class for managing inventories

This module provides the main InventorySystem class that manages all inventories,
handles item-related game logic, and interfaces with other systems.
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime

from .item_definitions import ItemDataRegistry, item_registry, ItemType
from .inventory_models import Inventory, InventorySlot
from .location_container_system import LocationContainerSystem
from .equipment_system import EquipmentSystem

if TYPE_CHECKING:
    from ..text_parser.vocabulary_manager import VocabularyManager

logger = logging.getLogger("inventory.system")


class InventorySystem:
    """
    Manages all inventories, handles item-related game logic, and interfaces with other systems.
    
    This class serves as the main entry point for all inventory operations and provides
    APIs for other game systems to interact with player and entity inventories.
    """
    
    def __init__(self, 
                 item_registry: Optional[ItemDataRegistry] = None,
                 vocabulary_manager: Optional['VocabularyManager'] = None):
        """
        Initialize the inventory system.
        
        Args:
            item_registry: ItemDataRegistry instance (uses global if None)
            vocabulary_manager: VocabularyManager for parser integration
        """
        # Import the global item_registry from the same module
        from .item_definitions import item_registry as global_item_registry
        self.item_registry = item_registry or global_item_registry
        self.vocabulary_manager = vocabulary_manager
        
        # Dictionary mapping owner_id to their Inventory object
        self.inventories: Dict[str, Inventory] = {}
        
        # Location container system for spatial item management
        self.location_container_system = LocationContainerSystem(self.item_registry)
        
        # Equipment system for managing equipped items
        self.equipment_system = EquipmentSystem()
        
        # Player location tracking (for spatial item commands)
        self.player_locations: Dict[str, str] = {}  # player_id -> location_id
        
        # System integration manager reference (will be injected)
        self.integration_manager: Optional[Any] = None
        
        # Default inventory settings
        self.default_player_slots = 30
        self.default_player_weight = 100.0
        self.default_container_slots = 50
        self.default_container_weight = None  # No weight limit for containers
        
        # Register existing items with vocabulary manager if available
        if self.vocabulary_manager:
            self._register_all_items_with_vocabulary()
        
        logger.info("InventorySystem initialized")
    
    def set_system_integration_manager(self, manager: Any):
        """Set the system integration manager reference."""
        self.integration_manager = manager
        
        # Also pass it to the location container system
        self.location_container_system.set_system_integration_manager(manager)
        
        logger.info("InventorySystem connected to SystemIntegrationManager")
    
    def set_vocabulary_manager(self, vocabulary_manager: 'VocabularyManager'):
        """Set the vocabulary manager and register all items."""
        self.vocabulary_manager = vocabulary_manager
        self._register_all_items_with_vocabulary()
        logger.info("InventorySystem connected to VocabularyManager")

    # === Player Location Tracking ===
    
    def update_player_location(self, player_id: str, location_id: str) -> None:
        """
        Update a player's current location for spatial inventory operations.
        
        Args:
            player_id: ID of the player
            location_id: ID of the location where player is now
        """
        if self.player_locations.get(player_id) != location_id:
            old_location = self.player_locations.get(player_id, "unknown")
            self.player_locations[player_id] = location_id
            logger.debug(f"Player {player_id} moved from {old_location} to {location_id}")
    
    def get_player_location(self, player_id: str) -> Optional[str]:
        """
        Get a player's current location.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Location ID or None if player location is unknown
        """
        return self.player_locations.get(player_id)
    
    # === Public API Methods for other systems ===
    
    def get_entity_inventory(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity's inventory data for persistence and other systems.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Inventory data dictionary or None
        """
        inventory = self.inventories.get(entity_id)
        if inventory:
            return inventory.to_dict()
        return None
    
    def player_has_items(self, player_id: str, items_to_check: Dict[str, int]) -> bool:
        """
        Check if player has a list of items and quantities.
        
        Args:
            player_id: Player ID
            items_to_check: Dictionary mapping item_id to required quantity
            
        Returns:
            True if player has all required items
        """
        player_inventory = self.get_or_create_inventory(player_id, "player")
        
        for item_id, required_quantity in items_to_check.items():
            if not player_inventory.has_item(item_id, required_quantity):
                return False
        
        return True

    def _register_all_items_with_vocabulary(self):
        """Register all items from the registry with the vocabulary manager."""
        if not self.vocabulary_manager or not self.item_registry:
            return
        
        # Get all items from the registry
        all_items = self.item_registry.get_all_items()
        
        for item_data in all_items:
            # Create synonyms list from name variations
            synonyms = []
            
            # Add the primary name
            if item_data.name:
                synonyms.append(item_data.name.lower())
            
            # Add alternative forms
            name_words = item_data.name.lower().split()
            if len(name_words) > 1:
                # Add without spaces/underscores
                synonyms.append(''.join(name_words))
                # Add with underscores
                synonyms.append('_'.join(name_words))
            
            # Add item_id as synonym (for admin commands)
            synonyms.append(item_data.item_id.lower())
            
            # Register with vocabulary manager
            self.vocabulary_manager.register_item(item_data.item_id, item_data.name, synonyms)
        
        logger.debug(f"Registered {len(all_items)} items with VocabularyManager")
    
    def get_or_create_inventory(self, owner_id: str, 
                               inventory_type: str = "player") -> Inventory:
        """
        Retrieve or initialize an inventory for an entity.
        
        Args:
            owner_id: ID of the entity (player, NPC, container)
            inventory_type: Type of inventory ("player", "npc", "container")
            
        Returns:
            Inventory instance
        """
        if owner_id not in self.inventories:
            # Create new inventory with appropriate defaults
            if inventory_type == "player":
                capacity_slots = self.default_player_slots
                capacity_weight = self.default_player_weight
            elif inventory_type == "container":
                capacity_slots = self.default_container_slots
                capacity_weight = self.default_container_weight
            else:  # npc or other
                capacity_slots = self.default_player_slots
                capacity_weight = self.default_player_weight
            
            inventory = Inventory(
                owner_id=owner_id,
                capacity_slots=capacity_slots,
                capacity_weight=capacity_weight
            )
            
            self.inventories[owner_id] = inventory
            logger.debug(f"Created new {inventory_type} inventory for {owner_id}")
        
        return self.inventories[owner_id]
    
    def handle_player_command(self, player_id: str, command_type: str, 
                             details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for parser tool commands.
        
        Args:
            player_id: ID of the player issuing the command
            command_type: Type of command ("TAKE", "DROP", "USE", "INVENTORY_VIEW", etc.)
            details: Parsed command details
            
        Returns:
            Result dictionary with success, message, and data
        """
        try:
            logger.debug(f"Processing inventory command: {command_type} for player {player_id}")
            
            if command_type == "TAKE":
                return self._handle_take_command(player_id, details)
            elif command_type == "DROP":
                return self._handle_drop_command(player_id, details)
            elif command_type == "USE":
                return self._handle_use_command(player_id, details)
            elif command_type == "INVENTORY_VIEW":
                return self._handle_inventory_view_command(player_id, details)
            elif command_type == "GIVE":  # For admin/quest systems
                return self._handle_give_command(player_id, details)
            #New elif statements for EQUIP and UNEQUIP commands
            elif command_type == "EQUIP":
                return self._handle_equip_command(player_id, details)
            elif command_type == "UNEQUIP":
                return self._handle_unequip_command(player_id, details)
            else:
                return {
                    "success": False,
                    "message": f"Unknown inventory command: {command_type}",
                    "data": {}
                }
        
        except Exception as e:
            logger.error(f"Error handling inventory command {command_type}: {e}")
            return {
                "success": False,
                "message": f"An error occurred while processing your request: {str(e)}",
                "data": {"error": str(e)}
            }
    
    def _handle_take_command(self, player_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TAKE command with location container system integration."""
        item_name = details.get("item_name_or_id", "").strip()
        quantity = details.get("quantity", 1)
        container_id = details.get("container_id")  # Optional specific container
        
        if not item_name:
            return {
                "success": False,
                "message": "You need to specify what you want to take.",
                "data": {}
            }
        
        # Get player's current location
        player_location = self.get_player_location(player_id)
        if not player_location:
            return {
                "success": False,
                "message": "You need to be in a location to take items.",
                "data": {}
            }
        
        # Try to find the item by name
        item_data = self.item_registry.find_item_by_name(item_name)
        if not item_data:
            # Try to find by ID
            item_data = self.item_registry.get_item_data(item_name)
        
        if not item_data:
            return {
                "success": False,
                "message": f"You don't see any '{item_name}' here.",
                "data": {}
            }
        
        # Try to take item from location using location container system
        success = False
        source_description = "the ground"
        
        if container_id:
            # Take from specific container
            success = self.location_container_system.remove_item_from_container(
                container_id, item_data.item_id, quantity)
            source_description = f"the container"
        else:
            # Take from ground at current location
            success = self.location_container_system.take_item_from_location(
                player_location, item_data.item_id, quantity)
        
        if not success:
            return {
                "success": False,
                "message": f"You don't see any '{item_name}' available to take here.",
                "data": {}
            }
        
        # Add to player inventory
        player_inventory = self.get_or_create_inventory(player_id, "player")
        
        if player_inventory.add_item(item_data.item_id, quantity, self.item_registry):
            result = {
                "success": True,
                "message": f"You take {quantity}x {item_data.name} from {source_description}.",
                "data": {
                    "item_taken": item_data.to_dict(),
                    "quantity": quantity,
                    "source": container_id or "ground",
                    "location": player_location,
                    "inventory_stats": player_inventory.get_stats()
                }
            }
            # Emit persistence event for item take
            self._emit_persistence_event("item_taken", {
                "player_id": player_id,
                "item_id": item_data.item_id,
                "quantity": quantity,
                "source": container_id or "ground",
                "location": player_location
            })
            return result
        else:
            # Inventory full - restore item to original location
            if container_id:
                self.location_container_system.add_item_to_container(
                    container_id, item_data.item_id, quantity)
            else:
                self.location_container_system.drop_item_at_location(
                    player_location, item_data.item_id, quantity)
            
            return {
                "success": False,
                "message": f"You can't carry {quantity}x {item_data.name}. Your inventory is full.",
                "data": {
                    "item": item_data.to_dict(),
                    "inventory_stats": player_inventory.get_stats()
                }
            }
    
    def _handle_drop_command(self, player_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DROP command with location container system integration."""
        item_name = details.get("item_name_or_id", "").strip()
        quantity = details.get("quantity", 1)
        target_container = details.get("container_id")  # Optional specific container
        
        if not item_name:
            return {
                "success": False,
                "message": "You need to specify what you want to drop.",
                "data": {}
            }
        
        # Get player's current location
        player_location = self.get_player_location(player_id)
        if not player_location:
            return {
                "success": False,
                "message": "You need to be in a location to drop items.",
                "data": {}
            }
        
        # Find the item
        item_data = self.item_registry.find_item_by_name(item_name)
        if not item_data:
            item_data = self.item_registry.get_item_data(item_name)
        
        if not item_data:
            return {
                "success": False,
                "message": f"You don't have any '{item_name}' to drop.",
                "data": {}
            }
        
        player_inventory = self.get_or_create_inventory(player_id, "player")
        
        if not player_inventory.has_item(item_data.item_id, quantity):
            current_quantity = player_inventory.get_item_quantity(item_data.item_id)
            return {
                "success": False,
                "message": f"You only have {current_quantity}x {item_data.name}.",
                "data": {
                    "item": item_data.to_dict(),
                    "available_quantity": current_quantity
                }
            }
        
        # Remove from player inventory first
        if not player_inventory.remove_item(item_data.item_id, quantity):
            return {
                "success": False,
                "message": f"You can't drop {item_data.name}.",
                "data": {}
            }
        
        # Try to drop using location container system
        success = False
        target_description = "on the ground"
        
        if target_container:
            # Drop into specific container
            success = self.location_container_system.add_item_to_container(
                target_container, item_data.item_id, quantity)
            target_description = f"into the container"
        else:
            # Drop on ground at current location
            success = self.location_container_system.drop_item_at_location(
                player_location, item_data.item_id, quantity)
        
        if success:
            result = {
                "success": True,
                "message": f"You drop {quantity}x {item_data.name} {target_description}.",
                "data": {
                    "item_dropped": item_data.to_dict(),
                    "quantity": quantity,
                    "target": target_container or "ground",
                    "location": player_location,
                    "inventory_stats": player_inventory.get_stats()
                }
            }
            # Emit persistence event for item drop
            self._emit_persistence_event("item_dropped", {
                "player_id": player_id,
                "item_id": item_data.item_id,
                "quantity": quantity,
                "target": target_container or "ground",
                "location": player_location
            })
            return result
        else:
            # Failed to drop - restore item to player inventory
            player_inventory.add_item(item_data.item_id, quantity, self.item_registry)
            return {
                "success": False,
                "message": f"You can't drop {item_data.name} there.",
                "data": {
                    "item": item_data.to_dict(),
                    "inventory_stats": player_inventory.get_stats()
                }
            }
    
    def _handle_use_command(self, player_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle USE command."""
        item_name = details.get("item_name_or_id", "").strip()
        target = details.get("target", "self")
        
        if not item_name:
            return {
                "success": False,
                "message": "You need to specify what you want to use.",
                "data": {}
            }
        
        # Find the item
        item_data = self.item_registry.find_item_by_name(item_name)
        if not item_data:
            item_data = self.item_registry.get_item_data(item_name)
        
        if not item_data:
            return {
                "success": False,
                "message": f"You don't have any '{item_name}' to use.",
                "data": {}
            }
        
        player_inventory = self.get_or_create_inventory(player_id, "player")
        
        if not player_inventory.has_item(item_data.item_id, 1):
            return {
                "success": False,
                "message": f"You don't have any {item_data.name} to use.",
                "data": {}
            }
        
        # Handle different item types
        if item_data.item_type == ItemType.CONSUMABLE:
            return self._use_consumable_item(player_id, player_inventory, item_data, target)
        elif item_data.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.SHIELD]:
            return self._use_equipment_item(player_id, player_inventory, item_data)
        elif item_data.item_type == ItemType.TOOL:
            return self._use_tool_item(player_id, player_inventory, item_data, target)
        else:
            return {
                "success": False,
                "message": f"You can't use {item_data.name}.",
                "data": {"item": item_data.to_dict()}
            }
    
    def _use_consumable_item(self, player_id: str, inventory: Inventory, 
                           item_data, target: str) -> Dict[str, Any]:
        """Handle using a consumable item."""
        # Consume the item
        if inventory.remove_item(item_data.item_id, 1):
            # Apply effects based on item properties
            effects = item_data.properties.get("effects", {})
            
            # TODO: Integrate with magic/combat systems for actual effect application
            effect_messages = []
            for effect_type, effect_value in effects.items():
                if effect_type == "heal":
                    effect_messages.append(f"You feel healed for {effect_value} health.")
                elif effect_type == "mana":
                    effect_messages.append(f"You regain {effect_value} mana.")
                elif effect_type == "buff":
                    effect_messages.append(f"You feel {effect_value}.")
            
            message = f"You use {item_data.name}."
            if effect_messages:
                message += " " + " ".join(effect_messages)
            
            # Emit persistence event for item use
            self._emit_persistence_event("item_used", {
                "player_id": player_id,
                "item_id": item_data.item_id,
                "quantity": 1,
                "effects_applied": effects,
                "target": target
            })
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "item_used": item_data.to_dict(),
                    "effects_applied": effects,
                    "target": target,
                    "inventory_stats": inventory.get_stats()
                }
            }
        else:
            return {
                "success": False,
                "message": f"Failed to use {item_data.name}.",
                "data": {}
            }
    
    def _use_equipment_item(self, player_id: str, inventory: Inventory, 
                          item_data) -> Dict[str, Any]:
        """Handle using/equipping an equipment item."""
        # TODO: Integrate with equipment system
        return {
            "success": True,
            "message": f"You equip {item_data.name}. (Equipment system not yet implemented)",
            "data": {
                "item": item_data.to_dict(),
                "action": "equip"
            }
        }
    
    def _use_tool_item(self, player_id: str, inventory: Inventory, 
                      item_data, target: str) -> Dict[str, Any]:
        """Handle using a tool item."""
        # TODO: Integrate with crafting/gathering systems
        return {
            "success": True,
            "message": f"You use {item_data.name} on {target}. (Tool system not yet implemented)",
            "data": {
                "item": item_data.to_dict(),
                "target": target,
                "action": "use_tool"
            }
        }
    
    def _handle_inventory_view_command(self, player_id: str, 
                                     details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle INVENTORY_VIEW command."""
        player_inventory = self.get_or_create_inventory(player_id, "player")
        return {
            "success": True,
            "message": "Inventory contents:",
            "data": {
                "inventory": self.get_player_inventory_display(player_id),
                "stats": player_inventory.get_stats()
            }
        }
    
    def _handle_give_command(self, player_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GIVE command (for admin/quest systems)."""
        item_name = details.get("item_name_or_id", "").strip()
        quantity = details.get("quantity", 1)
        
        if not item_name:
            return {
                "success": False,
                "message": "No item specified to give.",
                "data": {}
            }

    
        
        # Find the item
        item_data = self.item_registry.find_item_by_name(item_name)
        if not item_data:
            item_data = self.item_registry.get_item_data(item_name)
        
        if not item_data:
            return {
                "success": False,
                "message": f"Unknown item: {item_name}",
                "data": {}
            }
        
        if self.give_player_item(player_id, item_data.item_id, quantity):
            # Emit persistence event for item given
            self._emit_persistence_event("item_given", {
                "player_id": player_id,
                "item_id": item_data.item_id,
                "quantity": quantity,
                "source": "admin_give"
            })
            
            return {
                "success": True,
                "message": f"Given {quantity}x {item_data.name}.",
                "data": {
                    "item_given": item_data.to_dict(),
                    "quantity": quantity
                }
            }
        else:
            return {
                "success": False,
                "message": f"Could not give {quantity}x {item_data.name} (inventory full).",
                "data": {}
            }
    
    def _handle_equip_command(self, player_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle equipment commands from the parser.
        
        Args:
            player_id: ID of the player
            details: Command details with item_name/item_name_or_id and optional slot/preferred_slot
            
        Returns:
            Result dictionary
        """
        try:
            # Support both "item_name" and "item_name_or_id" for compatibility
            item_name = (details.get("item_name_or_id") or details.get("item_name", "")).strip()
            # Support both "slot" and "preferred_slot" for compatibility
            preferred_slot = details.get("preferred_slot") or details.get("slot")
            
            if not item_name:
                return {
                    "success": False,
                    "message": "Please specify an item to equip.",
                    "data": {}
                }
            
            # Get player inventory
            inventory = self.get_or_create_inventory(player_id)
            if not inventory:
                return {
                    "success": False,
                    "message": "You don't have an inventory.",
                    "data": {}
                }
            
            # Find the item in inventory by name or ID
            item_data = self.item_registry.find_item_by_name(item_name)
            if not item_data:
                item_data = self.item_registry.get_item_data(item_name)
            
            if not item_data:
                return {
                    "success": False,
                    "message": f"You don't have '{item_name}' in your inventory.",
                    "data": {}
                }
            
            # Check if player has this item in inventory
            if not inventory.has_item(item_data.item_id, 1):
                return {
                    "success": False,
                    "message": f"You don't have '{item_name}' in your inventory.",
                    "data": {}
                }
            
            # Check if item can be equipped
            equippable_types = [ItemType.WEAPON, ItemType.ARMOR, ItemType.SHIELD, ItemType.ACCESSORY]
            if item_data.item_type not in equippable_types:
                return {
                    "success": False,
                    "message": f"You cannot equip {item_data.name}.",
                    "data": {}
                }
            
            # Use equipment system to equip the item
            result = self.equipment_system.equip_item(
                player_id, 
                item_data.item_id, 
                inventory,
                self.item_registry,
                preferred_slot=preferred_slot
            )
            
            if result.get("success"):
                # Emit persistence event for equipment change
                self._emit_persistence_event("equipment_change", {
                    "player_id": player_id,
                    "action": "equip",
                    "item_id": item_data.item_id,
                    "item_name": item_data.name,
                    "slot": result.get("data", {}).get("slot"),
                    "player_state": self._get_current_world_state_snapshot(player_id)
                })
                
                # Build response message
                message = f"You equip {item_data.name}"
                if preferred_slot:
                    message += f" in your {preferred_slot.replace('_', ' ')}"
                message += "."
                
                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "equipped_item": item_data.name,
                        "slot": preferred_slot,
                        "item_id": item_data.item_id
                    }
                }
            else:
                return {
                    "success": False,
                    "message": result.get("message", f"Cannot equip {item_data.name}."),
                    "data": {}
                }
                
        except Exception as e:
            logger.error(f"Error in equip command: {e}")
            return {
                "success": False,
                "message": f"An error occurred while equipping the item: {str(e)}",
                "data": {}
            }
    
    def _handle_unequip_command(self, player_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle unequip commands from the parser.
        
        Args:
            player_id: ID of the player
            details: Command details with item_name/item_name_or_id or slot_name/slot
            
        Returns:
            Result dictionary
        """
        try:
            # Support both naming conventions for compatibility
            item_name = details.get("item_name_or_id") or details.get("item_name")
            slot_name = details.get("slot_name") or details.get("slot")
            
            # Convert to strings and strip if not None
            if item_name:
                item_name = str(item_name).strip()
            if slot_name:
                slot_name = str(slot_name).strip()
            
            if not item_name and not slot_name:
                return {
                    "success": False,
                    "message": "Please specify an item or equipment slot to unequip.",
                    "data": {}
                }
            
            # Check inventory space first
            inventory = self.get_or_create_inventory(player_id)
            if not inventory:
                return {
                    "success": False,
                    "message": "You don't have an inventory.",
                    "data": {}
                }
            
            # Use equipment system to unequip
            # If we have an item name, we need to find the item_id first
            item_id_to_unequip = None
            if item_name:
                # Look up the item by name to get its item_id
                item_data = self.item_registry.find_item_by_name(item_name)
                if not item_data:
                    item_data = self.item_registry.get_item_data(item_name)
                
                if item_data:
                    item_id_to_unequip = item_data.item_id
                else:
                    return {
                        "success": False,
                        "message": f"Unknown item: {item_name}",
                        "data": {}
                    }
            
            result = self.equipment_system.unequip_item(
                player_id, 
                item_id_to_unequip if item_id_to_unequip else None,
                slot_name if slot_name else None,
                inventory,
                self.item_registry
            )
            
            if result.get("success"):
                message = f"You unequip"
                if item_name:
                    message += f" {item_name}"
                elif slot_name:
                    message += f" your {slot_name.replace('_', ' ')}"
                message += "."
                
                # Emit persistence event for equipment change
                self._emit_persistence_event("equipment_change", {
                    "player_id": player_id,
                    "action": "unequip",
                    "item_id": item_id_to_unequip,
                    "item_name": item_name,
                    "slot": slot_name or result.get("data", {}).get("slot"),
                    "player_state": self._get_current_world_state_snapshot(player_id)
                })
                
                return {
                    "success": True,
                    "message": message,
                    "data": result.get("data", {})
                }
            else:
                if slot_name:
                    message = f"You don't have anything equipped in your {slot_name.replace('_', ' ')}."
                else:
                    message = f"You don't have '{item_name}' equipped."
                
                return {
                    "success": False,
                    "message": result.get("message", message),
                    "data": {}
                }
                
        except Exception as e:
            logger.error(f"Error in unequip command: {e}")
            return {
                "success": False,
                "message": f"An error occurred while unequipping the item: {str(e)}",
                "data": {}
            }
    
    def get_player_equipment_display(self, player_id: str) -> Dict[str, Any]:
        """
        Get a formatted display of the player's equipped items.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Result dictionary with equipment display
        """
        try:
            equipment_manager = self.equipment_system.get_equipment_manager(player_id)
            if not equipment_manager:
                return {
                    "success": True,
                    "message": "You have no equipment equipped.",
                    "data": {
                        "equipped_items": {},
                        "total_stats": {}
                    }
                }
            
            equipped_items_dict = equipment_manager.get_equipped_items()
            if not equipped_items_dict:
                return {
                    "success": True,
                    "message": "You have no equipment equipped.",
                    "data": {
                        "equipped_items": {},
                        "total_stats": {}
                    }
                }
            
            # Format equipment display
            lines = ["=== EQUIPPED ITEMS ==="]
            equipped_data = {}
            
            for slot_name, item_dict in equipped_items_dict.items():
                slot_display = slot_name.replace('_', ' ').title()
                item_id = item_dict.get('item_id', '')
                
                # Get item data from registry
                item_data = self.item_registry.get_item_data(item_id)
                if item_data:
                    item_name = item_data.name
                    lines.append(f"{slot_display}: {item_name}")
                    
                    equipped_data[slot_name] = {
                        "item_name": item_name,
                        "item_id": item_id
                    }
            
            # Get total equipment stats
            try:
                total_stats = self.equipment_system.get_equipment_stats(player_id, self.item_registry)
            except Exception as e:
                logger.error(f"Error getting equipment stats: {e}")
                total_stats = {}
            
            if total_stats:
                lines.append("\n=== EQUIPMENT BONUSES ===")
                for stat, value in total_stats.items():
                    # Skip non-numeric stats that shouldn't be displayed as bonuses
                    if stat in ["resistances", "special_effects"]:
                        continue
                    
                    # Only display non-zero numeric values
                    if isinstance(value, (int, float)) and value != 0:
                        sign = "+" if value > 0 else ""
                        lines.append(f"{stat.replace('_', ' ').title()}: {sign}{value}")
                
                # Handle resistances separately
                if "resistances" in total_stats and total_stats["resistances"]:
                    resistance_lines = []
                    for res_type, res_value in total_stats["resistances"].items():
                        if isinstance(res_value, (int, float)) and res_value != 0:
                            sign = "+" if res_value > 0 else ""
                            resistance_lines.append(f"{res_type.replace('_', ' ').title()}: {sign}{res_value}")
                    
                    if resistance_lines:
                        lines.append("Resistances:")
                        lines.extend(f"  {line}" for line in resistance_lines)
                
                # Handle special effects
                if "special_effects" in total_stats and total_stats["special_effects"]:
                    lines.append("Special Effects:")
                    for effect in total_stats["special_effects"]:
                        lines.append(f"  • {effect}")
            
            message = "\n".join(lines)
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "equipped_items": equipped_data,
                    "total_stats": total_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting equipment display: {e}")
            return {
                "success": False,
                "message": f"An error occurred while checking your equipment: {str(e)}",
                "data": {}
            }

    # Public API methods for other systems
    
    def player_has_items(self, player_id: str, items_to_check: Dict[str, int]) -> bool:
        """
        Check if player has a list of items and quantities.
        
        Args:
            player_id: Player ID
            items_to_check: Dictionary mapping item_id to required quantity
            
        Returns:
            True if player has all required items
        """
        player_inventory = self.get_or_create_inventory(player_id, "player")
        
        for item_id, required_quantity in items_to_check.items():
            if not player_inventory.has_item(item_id, required_quantity):
                return False
        
        return True
    
    def consume_player_items(self, player_id: str, items_to_consume: Dict[str, int]) -> bool:
        """
        Remove items from player inventory.
        
        Args:
            player_id: Player ID
            items_to_consume: Dictionary mapping item_id to quantity to remove
            
        Returns:
            True if all items were successfully consumed
        """
        # First check if player has all required items
        if not self.player_has_items(player_id, items_to_consume):
            return False
        
        player_inventory = self.get_or_create_inventory(player_id, "player")
        
        # Remove all items
        for item_id, quantity in items_to_consume.items():
            if not player_inventory.remove_item(item_id, quantity):
                # This shouldn't happen if we checked first, but handle it
                logger.error(f"Failed to consume {quantity}x {item_id} from player {player_id}")
                return False
        
        logger.debug(f"Consumed items from player {player_id}: {items_to_consume}")
        return True
    
    def give_player_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """
        Add item to player inventory.
        
        Args:
            player_id: Player ID
            item_id: Item identifier
            quantity: Quantity to add
            
        Returns:
            True if item was successfully added
        """
        player_inventory = self.get_or_create_inventory(player_id, "player")
        success = player_inventory.add_item(item_id, quantity, self.item_registry)
        
        if success:
            logger.debug(f"Gave {quantity}x {item_id} to player {player_id}")
        
        return success
    
    def get_player_inventory_display(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Format inventory for display.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of item dictionaries with display information
        """
        player_inventory = self.get_or_create_inventory(player_id, "player")
        display_items = []
        
        for slot in player_inventory.get_all_items():
            item_data = self.item_registry.get_item_data(slot.item_id)
            if item_data:
                display_items.append({
                    "item_id": slot.item_id,
                    "name": item_data.name,
                    "description": item_data.description,
                    "quantity": slot.quantity,
                    "item_type": item_data.item_type.value,
                    "rarity": item_data.rarity.value,
                    "weight": item_data.weight,
                    "value": item_data.value,
                    "stackable": item_data.stackable,
                    "properties": item_data.properties,
                    "display_name": item_data.get_display_name()
                })
        
        return display_items
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        total_inventories = len(self.inventories)
        total_items = sum(
            sum(slot.quantity for slot in inv.get_all_items()) 
            for inv in self.inventories.values()
        )
        
        return {
            "total_inventories": total_inventories,
            "total_items_in_circulation": total_items,
            "item_registry_stats": self.item_registry.get_registry_stats(),
            "active_player_inventories": len([
                inv for inv in self.inventories.values() 
                if inv.owner_id.startswith("player_")
            ])
        }
    
    def save_all_inventories(self) -> Dict[str, Any]:
        """Save all inventory data for persistence."""
        return {
            "inventories": {
                owner_id: inventory.to_dict()
                for owner_id, inventory in self.inventories.items()
            },
            "system_stats": self.get_system_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def load_inventories(self, data: Dict[str, Any]) -> int:
        """
        Load inventory data from saved state.
        
        Args:
            data: Saved inventory data
            
        Returns:
            Number of inventories loaded
        """
        inventories_data = data.get("inventories", {})
        loaded_count = 0
        
        for owner_id, inventory_data in inventories_data.items():
            try:
                inventory = Inventory.from_dict(inventory_data)
                self.inventories[owner_id] = inventory
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load inventory for {owner_id}: {e}")
        
        logger.info(f"Loaded {loaded_count} inventories")
        return loaded_count
    
    def process_command(self, command_type: str, entity_id: str, item_name: str, 
                       quantity: int, additional_data: str = "") -> Dict[str, Any]:
        """
        Process inventory command (used by SystemIntegrationManager).
        
        Args:
            command_type: Type of command (TAKE, DROP, USE, INVENTORY_VIEW, GIVE)
            entity_id: ID of the entity performing the action
            item_name: Name or ID of the item
            quantity: Quantity involved
            additional_data: Additional data (e.g., receiver_id for GIVE)
            
        Returns:
            Result dictionary with success, message, and data
        """
        details = {
            "item_name_or_id": item_name,
            "quantity": quantity
        }
        
        if command_type == "GIVE" and additional_data:
            details["receiver_id"] = additional_data
        
        return self.handle_player_command(entity_id, command_type, details)
    
    def _emit_persistence_event(self, event_type: str, data: Dict[str, Any]):
        """Emit persistence event through the integration manager."""
        try:
            logger.info(f"🔔 Emitting persistence event: {event_type} with data keys: {list(data.keys())}")
            if self.integration_manager and hasattr(self.integration_manager, 'emit_event'):
                from system_integration_manager import SystemType
                self.integration_manager.emit_event(event_type, SystemType.PERSISTENCE, data)
                logger.info(f"✅ Persistence event {event_type} emitted successfully")
            else:
                logger.warning(f"❌ Integration manager not available for event {event_type}")
        except Exception as e:
            logger.warning(f"Could not emit persistence event {event_type}: {e}")
    
    def _get_current_world_state_snapshot(self, player_id: str) -> Dict[str, Any]:
        """Get current world state snapshot for persistence."""
        player_inventory = self.get_or_create_inventory(player_id, "player")
        player_location = self.get_player_location(player_id)
        
        return {
            'player_id': player_id,
            'current_location': player_location,
            'inventory': player_inventory.to_dict() if player_inventory else {},
            'timestamp': datetime.now().isoformat()
        }
