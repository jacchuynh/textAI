"""
Inventory System Package

This package provides a comprehensive inventory management system for the TextRealmsAI
game engine, including item definitions, inventory models, and system integration.
"""

from .item_definitions import (
    ItemType, 
    ItemData, 
    ItemDataRegistry, 
    item_registry
)
from .inventory_models import (
    InventorySlot, 
    Inventory
)
from .inventory_system import InventorySystem

__all__ = [
    # Core classes
    'InventorySystem',
    'ItemDataRegistry',
    'ItemData', 
    'Inventory',
    'InventorySlot',
    
    # Enums
    'ItemType',
    
    # Global instances
    'item_registry'
]

__version__ = "1.0.0"
