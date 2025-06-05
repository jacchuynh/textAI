"""
Item Definitions - Core item data structures for the Inventory System

This module defines the fundamental building blocks for items, including
item definitions, types, and the item registry system.
"""

import json
import yaml
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path

# Import existing enums from crafting system for compatibility
try:
    from backend.src.crafting.models.pydantic_models import MaterialType, Rarity
except ImportError:
    # Fallback definitions if crafting system not available
    class MaterialType(str, Enum):
        MATERIAL = "MATERIAL"
        CRAFTED = "CRAFTED"
        OTHER = "OTHER"
    
    class Rarity(str, Enum):
        COMMON = "COMMON"
        UNCOMMON = "UNCOMMON"
        RARE = "RARE"
        EPIC = "EPIC"
        LEGENDARY = "LEGENDARY"

logger = logging.getLogger("inventory.item_definitions")


class ItemType(str, Enum):
    """Enumeration of item types for the inventory system."""
    # Equipment
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    SHIELD = "SHIELD"
    ACCESSORY = "ACCESSORY"
    
    # Consumables
    CONSUMABLE = "CONSUMABLE"
    POTION = "POTION"
    FOOD = "FOOD"
    SCROLL = "SCROLL"
    
    # Materials (compatible with crafting system)
    MATERIAL_CRAFTING = "MATERIAL_CRAFTING"
    MATERIAL_MAGICAL = "MATERIAL_MAGICAL"
    MATERIAL_ECONOMIC = "MATERIAL_ECONOMIC"
    
    # Special items
    QUEST_ITEM = "QUEST_ITEM"
    CURRENCY = "CURRENCY"
    KEY = "KEY"
    TOOL = "TOOL"
    CONTAINER = "CONTAINER"
    
    # Generic
    GENERIC = "GENERIC"
    OTHER = "OTHER"


@dataclass
class ItemData:
    """
    Represents the static definition of an item type.
    
    This class defines the immutable properties of an item that are shared
    across all instances of that item type.
    """
    item_id: str  # Unique identifier
    name: str  # Display name
    description: str  # Flavor text or functional description
    item_type: ItemType  # Primary item type
    stackable: bool = False  # Can multiple instances stack?
    max_stack_size: Optional[int] = None  # Max per stack if stackable
    weight: float = 0.0  # Weight for inventory capacity
    value: int = 0  # Base economic value
    rarity: Rarity = Rarity.COMMON  # Item rarity
    properties: Dict[str, Any] = field(default_factory=dict)  # Type-specific data
    
    # Integration fields
    material_type: Optional[MaterialType] = None  # For crafting integration
    synonyms: List[str] = field(default_factory=list)  # Alternative names for parser
    tags: Set[str] = field(default_factory=set)  # Categorization tags
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Validate stack settings
        if self.stackable and self.max_stack_size is None:
            self.max_stack_size = 99  # Default stack size
        elif not self.stackable:
            self.max_stack_size = 1
        
        # Ensure weight is non-negative
        if self.weight < 0:
            self.weight = 0.0
        
        # Ensure value is non-negative
        if self.value < 0:
            self.value = 0
        
        # Convert tags to set if it's a list
        if isinstance(self.tags, list):
            self.tags = set(self.tags)
        
        # Add item type as a default tag
        self.tags.add(self.item_type.value.lower())
        
        # Add compatibility with crafting system
        if self.item_type in [ItemType.MATERIAL_CRAFTING, ItemType.MATERIAL_MAGICAL]:
            if self.material_type is None:
                self.material_type = MaterialType.MATERIAL
    
    def __hash__(self) -> int:
        """Hash based on item_id for use in sets/dictionaries."""
        return hash(self.item_id)
    
    def __eq__(self, other) -> bool:
        """Equality based on item_id."""
        if not isinstance(other, ItemData):
            return False
        return self.item_id == other.item_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "stackable": self.stackable,
            "max_stack_size": self.max_stack_size,
            "weight": self.weight,
            "value": self.value,
            "rarity": self.rarity.value,
            "properties": self.properties,
            "material_type": self.material_type.value if self.material_type else None,
            "synonyms": self.synonyms,
            "tags": list(self.tags)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemData':
        """Create ItemData from dictionary."""
        # Convert enum strings back to enums
        item_type = ItemType(data["item_type"])
        rarity = Rarity(data["rarity"])
        material_type = MaterialType(data["material_type"]) if data.get("material_type") else None
        
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            item_type=item_type,
            stackable=data.get("stackable", False),
            max_stack_size=data.get("max_stack_size"),
            weight=data.get("weight", 0.0),
            value=data.get("value", 0),
            rarity=rarity,
            properties=data.get("properties", {}),
            material_type=material_type,
            synonyms=data.get("synonyms", []),
            tags=set(data.get("tags", []))
        )
    
    def is_compatible_with_crafting(self) -> bool:
        """Check if this item can be used in crafting systems."""
        return (self.item_type in [ItemType.MATERIAL_CRAFTING, ItemType.MATERIAL_MAGICAL] or
                self.material_type is not None)
    
    def get_display_name(self) -> str:
        """Get formatted display name with rarity if not common."""
        if self.rarity == Rarity.COMMON:
            return self.name
        return f"{self.name} ({self.rarity.value.title()})"


class ItemDataRegistry:
    """
    Loads and provides access to all ItemData definitions.
    
    This class manages the global registry of item definitions and provides
    methods for loading, accessing, and dynamically registering items.
    """
    
    def __init__(self):
        """Initialize empty item registry."""
        self._items: Dict[str, ItemData] = {}
        self._items_by_name: Dict[str, str] = {}  # name -> item_id mapping
        self._items_by_tag: Dict[str, Set[str]] = {}  # tag -> set of item_ids
        self._loaded_files: List[str] = []
        
        logger.info("ItemDataRegistry initialized")
    
    def load_from_files(self, file_paths: List[str]) -> int:
        """
        Load item definitions from JSON/YAML files.
        
        Args:
            file_paths: List of file paths to load from
            
        Returns:
            Number of items loaded
        """
        items_loaded = 0
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if not path.exists():
                    logger.warning(f"Item definition file not found: {file_path}")
                    continue
                
                # Load data based on file extension
                with open(path, 'r', encoding='utf-8') as f:
                    if path.suffix.lower() == '.json':
                        data = json.load(f)
                    elif path.suffix.lower() in ['.yml', '.yaml']:
                        data = yaml.safe_load(f)
                    else:
                        logger.warning(f"Unsupported file format: {file_path}")
                        continue
                
                # Process the loaded data
                if isinstance(data, dict) and 'items' in data:
                    # Format: {"items": [item_dict, ...]}
                    items_data = data['items']
                elif isinstance(data, list):
                    # Format: [item_dict, ...]
                    items_data = data
                else:
                    logger.warning(f"Invalid item data format in {file_path}")
                    continue
                
                # Load individual items
                for item_dict in items_data:
                    try:
                        item = ItemData.from_dict(item_dict)
                        self.register_item(item)
                        items_loaded += 1
                    except Exception as e:
                        logger.error(f"Failed to load item from {file_path}: {e}")
                
                self._loaded_files.append(file_path)
                logger.info(f"Loaded items from {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to load item definitions from {file_path}: {e}")
        
        logger.info(f"ItemDataRegistry loaded {items_loaded} items from {len(file_paths)} files")
        return items_loaded
    
    def register_item(self, item_data: ItemData) -> None:
        """
        Register an item definition.
        
        Args:
            item_data: ItemData instance to register
        """
        # Check for duplicate item_id
        if item_data.item_id in self._items:
            logger.warning(f"Overwriting existing item definition: {item_data.item_id}")
        
        # Register the item
        self._items[item_data.item_id] = item_data
        
        # Register name mapping (case-insensitive)
        name_key = item_data.name.lower()
        self._items_by_name[name_key] = item_data.item_id
        
        # Register synonym mappings
        for synonym in item_data.synonyms:
            synonym_key = synonym.lower()
            self._items_by_name[synonym_key] = item_data.item_id
        
        # Register tag mappings
        for tag in item_data.tags:
            if tag not in self._items_by_tag:
                self._items_by_tag[tag] = set()
            self._items_by_tag[tag].add(item_data.item_id)
        
        logger.debug(f"Registered item: {item_data.item_id} ({item_data.name})")
    
    def get_item_data(self, item_id: str) -> Optional[ItemData]:
        """
        Retrieve item definition by ID.
        
        Args:
            item_id: Unique item identifier
            
        Returns:
            ItemData instance or None if not found
        """
        return self._items.get(item_id)
    
    def find_item_by_name(self, name: str) -> Optional[ItemData]:
        """
        Find item by name (case-insensitive).
        
        Args:
            name: Item name or synonym
            
        Returns:
            ItemData instance or None if not found
        """
        name_key = name.lower()
        item_id = self._items_by_name.get(name_key)
        if item_id:
            return self._items.get(item_id)
        return None
    
    def find_items_by_tag(self, tag: str) -> List[ItemData]:
        """
        Find all items with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of ItemData instances
        """
        item_ids = self._items_by_tag.get(tag, set())
        return [self._items[item_id] for item_id in item_ids if item_id in self._items]
    
    def find_items_by_type(self, item_type: ItemType) -> List[ItemData]:
        """
        Find all items of a specific type.
        
        Args:
            item_type: ItemType to search for
            
        Returns:
            List of ItemData instances
        """
        return [item for item in self._items.values() if item.item_type == item_type]
    
    def search_items(self, query: str) -> List[ItemData]:
        """
        Search for items by name, description, or tags.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching ItemData instances
        """
        query = query.lower()
        results = []
        
        for item in self._items.values():
            # Check name and synonyms
            if (query in item.name.lower() or 
                any(query in synonym.lower() for synonym in item.synonyms)):
                results.append(item)
                continue
            
            # Check description
            if query in item.description.lower():
                results.append(item)
                continue
            
            # Check tags
            if any(query in tag.lower() for tag in item.tags):
                results.append(item)
                continue
        
        return results
    
    def get_all_items(self) -> List[ItemData]:
        """Get all registered items."""
        return list(self._items.values())
    
    def get_item_count(self) -> int:
        """Get total number of registered items."""
        return len(self._items)
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the item registry."""
        type_counts = {}
        rarity_counts = {}
        
        for item in self._items.values():
            # Count by type
            type_name = item.item_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # Count by rarity
            rarity_name = item.rarity.value
            rarity_counts[rarity_name] = rarity_counts.get(rarity_name, 0) + 1
        
        return {
            "total_items": len(self._items),
            "items_by_type": type_counts,
            "items_by_rarity": rarity_counts,
            "total_tags": len(self._items_by_tag),
            "loaded_files": len(self._loaded_files)
        }


# Global item registry instance
item_registry = ItemDataRegistry()
