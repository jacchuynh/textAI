"""
Location Container System - Spatial item management for world locations

This module manages items placed in specific world locations, containers,
and provides the bridge between the inventory system and world state.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import random

from .inventory_models import Inventory, InventorySlot
from .item_definitions import ItemDataRegistry

logger = logging.getLogger("inventory.location_container")


class ContainerType(str, Enum):
    """Types of containers that can hold items in the world."""
    GROUND = "ground"              # Items dropped on the ground
    CHEST = "chest"                # Storage chests
    BARREL = "barrel"              # Barrels and crates
    CORPSE = "corpse"              # Dead creature inventories
    SHOP = "shop"                  # Merchant inventories
    NPC = "npc"                    # NPC inventories
    BOOKSHELF = "bookshelf"        # Book storage
    WEAPON_RACK = "weapon_rack"    # Weapon displays
    ALTAR = "altar"                # Religious altars with offerings
    LOOT_CONTAINER = "loot_container"  # Generated loot containers


@dataclass
class ContainerData:
    """Data structure for containers in the world."""
    container_id: str
    container_type: ContainerType
    location_id: str
    name: str
    description: str
    capacity_slots: Optional[int] = None
    capacity_weight: Optional[float] = None
    is_locked: bool = False
    lock_difficulty: int = 0
    key_required: Optional[str] = None  # Specific key item ID required to unlock
    is_hidden: bool = False
    discovery_difficulty: int = 0
    search_requirements: Dict[str, Any] = field(default_factory=dict)  # Advanced search requirements
    container_behaviors: Dict[str, Any] = field(default_factory=dict)  # Container type specific behaviors
    owner_id: Optional[str] = None  # For NPC/shop inventories
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class LocationContainerSystem:
    """
    Manages containers and items in specific world locations.
    
    This system provides spatial awareness to the inventory system,
    allowing items to be placed in specific locations and containers.
    """
    
    def __init__(self, item_registry: ItemDataRegistry):
        """
        Initialize the location container system.
        
        Args:
            item_registry: ItemDataRegistry for item validation
        """
        self.item_registry = item_registry
        
        # Maps location_id -> Dict[container_id, ContainerData]
        self.location_containers: Dict[str, Dict[str, ContainerData]] = {}
        
        # Maps container_id -> Inventory
        self.container_inventories: Dict[str, Inventory] = {}
        
        # Maps location_id -> Set[item_ids] for ground items
        self.ground_items: Dict[str, Set[str]] = {}
        
        # Integration managers (will be injected)
        self.world_state_manager: Optional[Any] = None
        self.system_integration_manager: Optional[Any] = None
        
        logger.info("LocationContainerSystem initialized")
    
    def set_world_state_manager(self, world_state_manager: Any):
        """Set the world state manager reference."""
        self.world_state_manager = world_state_manager
        logger.info("World state manager connected to LocationContainerSystem")
    
    def set_system_integration_manager(self, manager: Any):
        """Set the system integration manager reference."""
        self.system_integration_manager = manager
        logger.info("System integration manager connected to LocationContainerSystem")
    
    # === Advanced Container Features (Phase 4B) ===
    
    def get_container_type_behaviors(self, container_type: ContainerType) -> Dict[str, Any]:
        """Get default behaviors for a container type."""
        behaviors = {
            ContainerType.CHEST: {
                "can_be_locked": True,
                "default_capacity_slots": 20,
                "default_capacity_weight": 200.0,
                "discovery_hint": "a wooden chest",
                "unlock_difficulty_modifier": 0
            },
            ContainerType.BARREL: {
                "can_be_locked": False,
                "default_capacity_slots": 15,
                "default_capacity_weight": 150.0,
                "discovery_hint": "a storage barrel",
                "unlock_difficulty_modifier": -5
            },
            ContainerType.BOOKSHELF: {
                "can_be_locked": True,
                "default_capacity_slots": 30,
                "default_capacity_weight": 50.0,
                "discovery_hint": "a bookshelf with compartments",
                "unlock_difficulty_modifier": 5,
                "special_search": "requires careful examination of books"
            },
            ContainerType.WEAPON_RACK: {
                "can_be_locked": True,
                "default_capacity_slots": 10,
                "default_capacity_weight": 100.0,
                "discovery_hint": "a weapon rack",
                "unlock_difficulty_modifier": 0,
                "item_type_restriction": ["WEAPON", "SHIELD"]
            },
            ContainerType.ALTAR: {
                "can_be_locked": False,
                "default_capacity_slots": 5,
                "default_capacity_weight": 20.0,
                "discovery_hint": "a sacred altar",
                "unlock_difficulty_modifier": 10,
                "special_requirements": "requires reverent approach"
            },
            ContainerType.LOOT_CONTAINER: {
                "can_be_locked": True,
                "default_capacity_slots": 12,
                "default_capacity_weight": 100.0,
                "discovery_hint": "a hidden container",
                "unlock_difficulty_modifier": 3,
                "always_hidden": True
            }
        }
        return behaviors.get(container_type, {
            "can_be_locked": True,
            "default_capacity_slots": 10,
            "default_capacity_weight": 50.0,
            "discovery_hint": "a container",
            "unlock_difficulty_modifier": 0
        })
    
    def can_unlock_container(self, container_id: str, player_inventory: Any) -> Dict[str, Any]:
        """Check if a container can be unlocked with available items/skills."""
        container_data = self.get_container(container_id)
        if not container_data or not container_data.is_locked:
            return {"can_unlock": True, "method": "not_locked"}
        
        result = {
            "can_unlock": False,
            "methods": [],
            "required_items": [],
            "required_skills": []
        }
        
        # Check for specific key requirement
        if container_data.key_required:
            if player_inventory and player_inventory.has_item(container_data.key_required, 1):
                result["can_unlock"] = True
                result["methods"].append("key")
                return result
            else:
                result["required_items"].append(container_data.key_required)
        
        # Check for lockpicking capability (future skill system integration)
        if container_data.lock_difficulty > 0:
            # For now, assume basic lockpicking is available
            # This would be enhanced with actual skill system integration
            lockpick_available = player_inventory and player_inventory.has_item("lockpick", 1)
            if lockpick_available:
                result["can_unlock"] = True
                result["methods"].append("lockpick")
                result["difficulty"] = container_data.lock_difficulty
            else:
                result["required_items"].append("lockpick")
                result["required_skills"].append(f"lockpicking (difficulty {container_data.lock_difficulty})")
        
        return result
    
    def unlock_container(self, container_id: str, player_inventory: Any, method: str = "auto") -> Dict[str, Any]:
        """Attempt to unlock a container."""
        container_data = self.get_container(container_id)
        if not container_data:
            return {"success": False, "message": "Container not found."}
        
        if not container_data.is_locked:
            return {"success": True, "message": f"The {container_data.name} is already unlocked."}
        
        unlock_check = self.can_unlock_container(container_id, player_inventory)
        if not unlock_check["can_unlock"]:
            required = unlock_check.get("required_items", [])
            if required:
                return {
                    "success": False,
                    "message": f"You need {', '.join(required)} to unlock this container.",
                    "required_items": required
                }
            else:
                return {"success": False, "message": "You cannot unlock this container."}
        
        # Determine unlock method
        if method == "auto":
            method = unlock_check["methods"][0] if unlock_check["methods"] else None
        
        if method == "key" and container_data.key_required:
            # Use specific key
            if player_inventory.has_item(container_data.key_required, 1):
                container_data.is_locked = False
                
                # Get key item info for message
                key_item = self.item_registry.get_item_data(container_data.key_required)
                key_name = key_item.name if key_item else container_data.key_required
                
                self._notify_world_state_change("container_unlocked", {
                    "container_id": container_id,
                    "location_id": container_data.location_id,
                    "method": "key",
                    "key_used": container_data.key_required
                })
                
                return {
                    "success": True,
                    "message": f"You unlock the {container_data.name} with the {key_name}.",
                    "method": "key",
                    "key_used": key_name
                }
        
        elif method == "lockpick":
            # Use lockpick (simplified - could be enhanced with skill checks)
            if player_inventory.has_item("lockpick", 1):
                container_data.is_locked = False
                
                self._notify_world_state_change("container_unlocked", {
                    "container_id": container_id,
                    "location_id": container_data.location_id,
                    "method": "lockpick",
                    "difficulty": container_data.lock_difficulty
                })
                
                return {
                    "success": True,
                    "message": f"You successfully pick the lock on the {container_data.name}.",
                    "method": "lockpick",
                    "difficulty": container_data.lock_difficulty
                }
        
        return {"success": False, "message": "Failed to unlock the container."}

    # === Container Management ===
    
    def create_enhanced_container(self, 
                            location_id: str,
                            container_type: ContainerType,
                            name: str,
                            description: str,
                            enhancement_level: str = "basic",
                            **kwargs) -> str:
        """Create a container with enhanced type-specific behaviors and properties."""
        # Get type-specific behaviors
        behaviors = self.get_container_type_behaviors(container_type)
        
        # Apply default values from behaviors if not specified
        if "capacity_slots" not in kwargs:
            kwargs["capacity_slots"] = behaviors.get("default_capacity_slots", 10)
        
        if "capacity_weight" not in kwargs:
            kwargs["capacity_weight"] = behaviors.get("default_capacity_weight", 50.0)
        
        # Apply enhancement level modifications
        if enhancement_level == "enhanced":
            # Enhanced containers have better capacity and may have special features
            kwargs["capacity_slots"] = int(kwargs["capacity_slots"] * 1.5)
            kwargs["capacity_weight"] = kwargs["capacity_weight"] * 1.5
            
            # 50% chance of being lockable if type supports it
            if behaviors.get("can_be_locked", True) and "is_locked" not in kwargs:
                if random.random() < 0.5:
                    kwargs["is_locked"] = True
                    kwargs["lock_difficulty"] = random.randint(5, 15)
        
        elif enhancement_level == "legendary":
            # Legendary containers have maximum capacity and special properties
            kwargs["capacity_slots"] = int(kwargs["capacity_slots"] * 2)
            kwargs["capacity_weight"] = kwargs["capacity_weight"] * 2
            
            # Always locked with high difficulty or key requirement
            if behaviors.get("can_be_locked", True):
                kwargs["is_locked"] = True
                kwargs["lock_difficulty"] = random.randint(15, 25)
                # 30% chance of requiring a specific key
                if random.random() < 0.3:
                    kwargs["key_required"] = f"{container_type.value}_master_key"
        
        # Apply container behaviors
        kwargs["container_behaviors"] = behaviors
        
        return self.create_container(
            location_id=location_id,
            container_type=container_type,
            name=name,
            description=description,
            **kwargs
        )

    def create_container(self, 
                        location_id: str,
                        container_type: ContainerType,
                        name: str,
                        description: str,
                        capacity_slots: Optional[int] = None,
                        capacity_weight: Optional[float] = None,
                        **kwargs) -> str:
        """
        Create a new container in a location.
        
        Args:
            location_id: ID of the location where container is placed
            container_type: Type of container
            name: Display name of the container
            description: Description of the container
            capacity_slots: Maximum number of item slots (None = unlimited)
            capacity_weight: Maximum weight capacity (None = unlimited)
            **kwargs: Additional container properties
            
        Returns:
            container_id: Unique identifier for the created container
        """
        container_id = f"container_{location_id}_{uuid.uuid4().hex[:8]}"
        
        # Create container data
        container_data = ContainerData(
            container_id=container_id,
            container_type=container_type,
            location_id=location_id,
            name=name,
            description=description,
            capacity_slots=capacity_slots,
            capacity_weight=capacity_weight,
            **kwargs
        )
        
        # Create inventory for the container
        container_inventory = Inventory(
            owner_id=container_id,
            capacity_slots=capacity_slots,
            capacity_weight=capacity_weight
        )
        
        # Register container in location
        if location_id not in self.location_containers:
            self.location_containers[location_id] = {}
        
        self.location_containers[location_id][container_id] = container_data
        self.container_inventories[container_id] = container_inventory
        
        logger.info(f"Created {container_type} container '{name}' in location {location_id}")
        
        # Notify world state manager if available
        if self.world_state_manager:
            self._notify_world_state_change("container_created", {
                "location_id": location_id,
                "container_id": container_id,
                "container_data": container_data.__dict__
            })
        
        return container_id
    
    def get_container(self, container_id: str) -> Optional[ContainerData]:
        """Get container data by ID."""
        for location_containers in self.location_containers.values():
            if container_id in location_containers:
                return location_containers[container_id]
        return None
    
    def get_containers_in_location(self, location_id: str) -> Dict[str, ContainerData]:
        """Get all containers in a specific location."""
        return self.location_containers.get(location_id, {})
    
    def get_container_inventory(self, container_id: str) -> Optional[Inventory]:
        """Get the inventory of a specific container."""
        return self.container_inventories.get(container_id)
    
    # === Ground Item Management ===
    
    def drop_item_at_location(self, 
                             location_id: str,
                             item_id: str,
                             quantity: int = 1) -> bool:
        """
        Drop items on the ground at a specific location.
        
        Args:
            location_id: ID of the location
            item_id: ID of the item to drop
            quantity: Number of items to drop
            
        Returns:
            bool: True if items were successfully dropped
        """
        # Validate item exists
        item_data = self.item_registry.get_item_data(item_id)
        if not item_data:
            logger.warning(f"Cannot drop unknown item: {item_id}")
            return False
        
        # Get or create ground container for this location
        ground_container_id = self._get_or_create_ground_container(location_id)
        ground_inventory = self.container_inventories[ground_container_id]
        
        # Add item to ground inventory
        success = ground_inventory.add_item(item_id, quantity, self.item_registry)
        
        if success:
            # Track ground items for quick lookup
            if location_id not in self.ground_items:
                self.ground_items[location_id] = set()
            self.ground_items[location_id].add(item_id)
            
            logger.info(f"Dropped {quantity}x {item_data.name} at location {location_id}")
            
            # Notify world state manager
            if self.world_state_manager:
                self._notify_world_state_change("item_dropped", {
                    "location_id": location_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "item_name": item_data.name
                })
        
        return success
    
    def take_item_from_location(self, 
                               location_id: str,
                               item_id: str,
                               quantity: int = 1) -> bool:
        """
        Take items from the ground at a specific location.
        
        Args:
            location_id: ID of the location
            item_id: ID of the item to take
            quantity: Number of items to take
            
        Returns:
            bool: True if items were successfully taken
        """
        # Get ground container for this location
        ground_container_id = self._get_ground_container_id(location_id)
        if not ground_container_id:
            return False
        
        ground_inventory = self.container_inventories.get(ground_container_id)
        if not ground_inventory:
            return False
        
        # Check if item is available
        if not ground_inventory.has_item(item_id, quantity):
            return False
        
        # Remove item from ground
        success = ground_inventory.remove_item(item_id, quantity)
        
        if success:
            # Clean up tracking if no more items of this type
            if ground_inventory.get_item_quantity(item_id) == 0:
                if location_id in self.ground_items:
                    self.ground_items[location_id].discard(item_id)
                    
                    # Remove empty set
                    if not self.ground_items[location_id]:
                        del self.ground_items[location_id]
            
            item_data = self.item_registry.get_item_data(item_id)
            item_name = item_data.name if item_data else item_id
            
            logger.info(f"Took {quantity}x {item_name} from location {location_id}")
            
            # Notify world state manager
            if self.world_state_manager:
                self._notify_world_state_change("item_taken", {
                    "location_id": location_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "item_name": item_name
                })
        
        return success
    
    def get_items_at_location(self, location_id: str) -> Dict[str, Any]:
        """
        Get all items available at a location (ground + containers).
        
        Returns:
            Dict with 'ground_items' and 'containers' information
        """
        result = {
            "ground_items": {},
            "containers": {}
        }
        
        # Get ground items
        ground_container_id = self._get_ground_container_id(location_id)
        if ground_container_id:
            ground_inventory = self.container_inventories.get(ground_container_id)
            if ground_inventory:
                for slot in ground_inventory._slots:
                    item_data = self.item_registry.get_item_data(slot.item_id)
                    result["ground_items"][slot.item_id] = {
                        "name": item_data.name if item_data else slot.item_id,
                        "quantity": slot.quantity,
                        "description": item_data.description if item_data else ""
                    }
        
        # Get container items
        containers = self.get_containers_in_location(location_id)
        for container_id, container_data in containers.items():
            if container_data.container_type == ContainerType.GROUND:
                continue  # Already handled above
            
            container_inventory = self.container_inventories.get(container_id)
            if container_inventory:
                container_items = {}
                for slot in container_inventory._slots:
                    item_data = self.item_registry.get_item_data(slot.item_id)
                    container_items[slot.item_id] = {
                        "name": item_data.name if item_data else slot.item_id,
                        "quantity": slot.quantity,
                        "description": item_data.description if item_data else ""
                    }
                
                result["containers"][container_id] = {
                    "name": container_data.name,
                    "type": container_data.container_type,
                    "description": container_data.description,
                    "items": container_items,
                    "is_locked": container_data.is_locked,
                    "is_hidden": container_data.is_hidden
                }
        
        return result
    
    # === Container Item Management ===
    
    def add_item_to_container(self, 
                             container_id: str,
                             item_id: str,
                             quantity: int = 1) -> bool:
        """Add items to a specific container."""
        container_inventory = self.container_inventories.get(container_id)
        if not container_inventory:
            logger.warning(f"Container not found: {container_id}")
            return False
        
        item_data = self.item_registry.get_item_data(item_id)
        if not item_data:
            logger.warning(f"Unknown item: {item_id}")
            return False
        
        success = container_inventory.add_item(item_id, quantity, self.item_registry)
        
        if success:
            container_data = self.get_container(container_id)
            logger.info(f"Added {quantity}x {item_data.name} to {container_data.name if container_data else container_id}")
            
            # Notify world state manager
            if self.world_state_manager and container_data:
                self._notify_world_state_change("container_item_added", {
                    "location_id": container_data.location_id,
                    "container_id": container_id,
                    "item_id": item_id,
                    "quantity": quantity
                })
        
        return success
    
    def remove_item_from_container(self, 
                                  container_id: str,
                                  item_id: str,
                                  quantity: int = 1) -> bool:
        """Remove items from a specific container."""
        container_inventory = self.container_inventories.get(container_id)
        if not container_inventory:
            return False
        
        success = container_inventory.remove_item(item_id, quantity)
        
        if success:
            container_data = self.get_container(container_id)
            item_data = self.item_registry.get_item_data(item_id)
            item_name = item_data.name if item_data else item_id
            
            logger.info(f"Removed {quantity}x {item_name} from {container_data.name if container_data else container_id}")
            
            # Notify world state manager
            if self.world_state_manager and container_data:
                self._notify_world_state_change("container_item_removed", {
                    "location_id": container_data.location_id,
                    "container_id": container_id,
                    "item_id": item_id,
                    "quantity": quantity
                })
        
        return success
    
    # === Search and Discovery ===
    
    def search_location(self, location_id: str, search_skill: int = 0) -> Dict[str, Any]:
        """
        Search a location for hidden containers and items.
        
        Args:
            location_id: ID of the location to search
            search_skill: Player's search skill level
            
        Returns:
            Dict with discovered containers and items
        """
        discovered = {
            "containers": [],
            "items": [],
            "secrets": []
        }
        
        containers = self.get_containers_in_location(location_id)
        
        for container_id, container_data in containers.items():
            # Check if hidden container can be discovered
            if container_data.is_hidden and search_skill >= container_data.discovery_difficulty:
                discovered["containers"].append({
                    "id": container_id,
                    "name": container_data.name,
                    "type": container_data.container_type,
                    "description": container_data.description
                })
                
                # Reveal the container
                container_data.is_hidden = False
                logger.info(f"Player discovered hidden {container_data.container_type}: {container_data.name}")
        
        return discovered
    
    # === Private Helper Methods ===
    
    def _get_or_create_ground_container(self, location_id: str) -> str:
        """Get or create the ground container for a location."""
        # Check if ground container already exists
        ground_container_id = self._get_ground_container_id(location_id)
        if ground_container_id:
            return ground_container_id
        
        # Create new ground container
        return self.create_container(
            location_id=location_id,
            container_type=ContainerType.GROUND,
            name="Ground",
            description="Items dropped on the ground",
            capacity_slots=None,  # Unlimited
            capacity_weight=None   # Unlimited
        )
    
    def _get_ground_container_id(self, location_id: str) -> Optional[str]:
        """Get the ground container ID for a location."""
        containers = self.get_containers_in_location(location_id)
        for container_id, container_data in containers.items():
            if container_data.container_type == ContainerType.GROUND:
                return container_id
        return None
    
    def _notify_world_state_change(self, event_type: str, data: Dict[str, Any]):
        """Notify the world state manager of changes."""
        if self.system_integration_manager:
            try:
                self.system_integration_manager.emit_event(
                    event_type,
                    "INVENTORY",
                    data
                )
                
                # Also emit persistence events for container changes
                if event_type in ["container_item_added", "container_item_removed", "container_unlocked"]:
                    from system_integration_manager import SystemType
                    self.system_integration_manager.emit_event(
                        "location_change",
                        SystemType.PERSISTENCE,
                        {
                            'location_id': data.get('location_id'),
                            'container_data': data,
                            'event_type': event_type,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to emit event {event_type}: {e}")
    
    # === World Integration Methods ===
    
    def initialize_location_containers(self, location_id: str, location_data: Dict[str, Any]):
        """
        Initialize containers for a new location based on location data.
        
        This method is called when a location is first created or loaded
        to set up appropriate containers based on the location type.
        """
        location_type = location_data.get("type", "generic")
        biome = location_data.get("biome", "")
        
        # Generate appropriate containers based on location type
        if location_type == "village":
            self._generate_village_containers(location_id, location_data)
        elif location_type == "ruin":
            self._generate_ruin_containers(location_id, location_data)
        elif location_type == "cave":
            self._generate_cave_containers(location_id, location_data)
        elif location_type == "shop":
            self._generate_shop_containers(location_id, location_data)
        else:
            # Generic containers for unknown location types
            self._generate_generic_containers(location_id, location_data)
        
        logger.info(f"Initialized containers for {location_type} location: {location_id}")
    
    def _generate_village_containers(self, location_id: str, location_data: Dict[str, Any]):
        """Generate containers appropriate for a village."""
        # Village well (community resource)
        self.create_container(
            location_id=location_id,
            container_type=ContainerType.BARREL,
            name="Village Well",
            description="A stone well with a bucket. The community stores emergency supplies here.",
            capacity_slots=20,
            capacity_weight=100.0
        )
        
        # Notice board (for messages/quests)
        notice_board_id = self.create_container(
            location_id=location_id,
            container_type=ContainerType.BOOKSHELF,
            name="Village Notice Board",
            description="A wooden board where villagers post notices and requests.",
            capacity_slots=10,
            capacity_weight=5.0
        )
        
        # Add some sample notices
        self.add_item_to_container(notice_board_id, "scroll", 2)
    
    def _generate_ruin_containers(self, location_id: str, location_data: Dict[str, Any]):
        """Generate containers appropriate for ruins."""
        # Hidden treasure chest
        treasure_chest_id = self.create_container(
            location_id=location_id,
            container_type=ContainerType.CHEST,
            name="Ancient Chest",
            description="An old, ornate chest covered in dust and cobwebs.",
            capacity_slots=15,
            capacity_weight=200.0,
            is_hidden=True,
            discovery_difficulty=15,
            is_locked=True,
            lock_difficulty=20
        )
        
        # Add some treasure
        self.add_item_to_container(treasure_chest_id, "gold_coin", 50)
        self.add_item_to_container(treasure_chest_id, "health_potion_small", 2)
    
    def _generate_cave_containers(self, location_id: str, location_data: Dict[str, Any]):
        """Generate containers appropriate for caves."""
        # Mineral deposits
        self.create_container(
            location_id=location_id,
            container_type=ContainerType.LOOT_CONTAINER,
            name="Mineral Vein",
            description="A rich vein of ore visible in the cave wall.",
            capacity_slots=5,
            capacity_weight=500.0
        )
    
    def _generate_shop_containers(self, location_id: str, location_data: Dict[str, Any]):
        """Generate containers appropriate for shops."""
        # Shop inventory
        shop_inventory_id = self.create_container(
            location_id=location_id,
            container_type=ContainerType.SHOP,
            name="Shop Inventory",
            description="The merchant's wares displayed on shelves and counters.",
            capacity_slots=50,
            capacity_weight=1000.0,
            owner_id=location_data.get("shop_owner", "merchant")
        )
        
        # Stock basic items
        self.add_item_to_container(shop_inventory_id, "health_potion_small", 10)
        self.add_item_to_container(shop_inventory_id, "bread", 20)
        self.add_item_to_container(shop_inventory_id, "iron_sword", 3)
    
    def _generate_generic_containers(self, location_id: str, location_data: Dict[str, Any]):
        """Generate generic containers for unknown location types."""
        # Simple storage area
        self.create_container(
            location_id=location_id,
            container_type=ContainerType.BARREL,
            name="Storage Area",
            description="A small area where travelers sometimes leave supplies.",
            capacity_slots=10,
            capacity_weight=50.0
        )
    
    # === Status and Debug Methods ===
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the location container system."""
        total_containers = sum(len(containers) for containers in self.location_containers.values())
        total_ground_locations = len(self.ground_items)
        total_items_on_ground = sum(len(items) for items in self.ground_items.values())
        
        return {
            "total_locations": len(self.location_containers),
            "total_containers": total_containers,
            "total_ground_locations": total_ground_locations,
            "total_items_on_ground": total_items_on_ground,
            "container_inventories": len(self.container_inventories),
            "world_state_connected": self.world_state_manager is not None,
            "integration_manager_connected": self.system_integration_manager is not None
        }


# Global location container system instance
location_container_system = LocationContainerSystem(item_registry=None)  # Will be initialized properly
