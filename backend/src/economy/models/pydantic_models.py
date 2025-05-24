"""
Economy System Pydantic Models

This module defines Pydantic models for the economy system,
ensuring data validation and type safety.
"""

from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ItemCategory(str, Enum):
    """Categories for items in the economy system."""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    FOOD = "food"
    MATERIAL = "material"
    TOOL = "tool"
    MAGICAL = "magical"
    CLOTHING = "clothing"
    TREASURE = "treasure"
    MISCELLANEOUS = "miscellaneous"

class ItemRarity(str, Enum):
    """Rarity levels for items."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class InventorySlot(BaseModel):
    """
    Represents a slot in an inventory containing an item.
    """
    quantity: int = Field(default=1, description="Number of items in this slot")
    condition: float = Field(default=1.0, description="Condition of the items (0.0 to 1.0)")
    price_override: Optional[float] = Field(default=None, description="Optional price override")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this slot")

class Item(BaseModel):
    """
    Represents an item in the game world.
    """
    id: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., description="Name of the item")
    description: str = Field(..., description="Description of the item")
    base_price: float = Field(..., description="Base price of the item")
    weight: float = Field(default=0.0, description="Weight of the item in pounds")
    category: ItemCategory = Field(..., description="Category of the item")
    rarity: ItemRarity = Field(default=ItemRarity.COMMON, description="Rarity of the item")
    tags: List[str] = Field(default_factory=list, description="Tags for the item")
    stackable: bool = Field(default=False, description="Whether the item can be stacked")
    max_stack: int = Field(default=1, description="Maximum stack size if stackable")
    usable: bool = Field(default=False, description="Whether the item can be used")
    equippable: bool = Field(default=False, description="Whether the item can be equipped")
    craftable: bool = Field(default=False, description="Whether the item can be crafted")
    crafting_recipe: Optional[Dict[str, int]] = Field(default=None, description="Recipe for crafting")
    effects: Dict[str, Any] = Field(default_factory=dict, description="Effects of the item when used")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this item")

class Shop(BaseModel):
    """
    Represents a shop in the game world.
    """
    id: str = Field(..., description="Unique identifier for the shop")
    name: str = Field(..., description="Name of the shop")
    description: str = Field(..., description="Description of the shop")
    owner_id: str = Field(..., description="ID of the shop owner (NPC or player)")
    location_id: str = Field(..., description="ID of the shop's location")
    shop_type: str = Field(..., description="Type of shop (e.g., blacksmith, alchemist)")
    inventory: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Shop inventory keyed by item ID")
    currency_balance: float = Field(default=100.0, description="Shop's currency balance")
    buy_price_modifier: float = Field(default=0.8, description="Modifier for buying items (0.0 to 2.0)")
    sell_price_modifier: float = Field(default=1.2, description="Modifier for selling items (0.0 to 2.0)")
    reputation_required: int = Field(default=0, description="Minimum reputation required to access shop")
    restocks: bool = Field(default=True, description="Whether the shop restocks inventory")
    restock_interval: int = Field(default=24, description="Hours between restocks")
    last_restock: Optional[datetime] = Field(default=None, description="When the shop was last restocked")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this shop")

class MarketRegionInfo(BaseModel):
    """
    Represents market information for a region.
    """
    region_id: str = Field(..., description="Unique identifier for the region")
    name: str = Field(..., description="Name of the region")
    prosperity_level: float = Field(default=0.5, description="Prosperity level of the region (0.0 to 1.0)")
    supply_demand_signals: Dict[str, float] = Field(default_factory=dict, description="Supply/demand signals by item category or ID")
    category_price_modifiers: Dict[str, float] = Field(default_factory=dict, description="Price modifiers by category")
    tax_rate: float = Field(default=0.05, description="Tax rate for transactions in this region")
    currency_name: str = Field(default="gold", description="Name of the currency used in this region")
    currency_exchange_rates: Dict[str, float] = Field(default_factory=dict, description="Exchange rates with other currencies")
    trade_restrictions: List[str] = Field(default_factory=list, description="Restricted items or categories")
    trade_bonuses: Dict[str, float] = Field(default_factory=dict, description="Bonus for trading specific items or categories")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this region")

class Resource(BaseModel):
    """
    Represents a natural resource in the game world.
    """
    id: str = Field(..., description="Unique identifier for the resource")
    name: str = Field(..., description="Name of the resource")
    description: str = Field(..., description="Description of the resource")
    location_id: str = Field(..., description="ID of the resource's location")
    resource_type: str = Field(..., description="Type of resource (e.g., mine, forest, farm)")
    depletion_level: float = Field(default=0.0, description="Current depletion level (0.0 to 1.0)")
    max_yield: float = Field(..., description="Maximum yield per extraction")
    regeneration_rate: float = Field(default=0.0, description="Rate of regeneration per day")
    extraction_difficulty: float = Field(default=0.5, description="Difficulty of extraction (0.0 to 1.0)")
    products: Dict[str, float] = Field(..., description="Products and their yield rates")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this resource")

class Business(BaseModel):
    """
    Represents a business in the game world.
    """
    id: str = Field(..., description="Unique identifier for the business")
    name: str = Field(..., description="Name of the business")
    description: str = Field(..., description="Description of the business")
    owner_id: str = Field(..., description="ID of the business owner (NPC or player)")
    location_id: str = Field(..., description="ID of the business's location")
    business_type: str = Field(..., description="Type of business (e.g., production, service)")
    capital: float = Field(default=100.0, description="Business capital")
    employees: List[str] = Field(default_factory=list, description="IDs of employees")
    inventory: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Business inventory")
    input_materials_required: Dict[str, int] = Field(default_factory=dict, description="Required input materials")
    production_item_id: Optional[str] = Field(default=None, description="ID of item being produced")
    production_capacity: int = Field(default=1, description="Number of items produced per cycle")
    production_time: int = Field(default=24, description="Hours per production cycle")
    last_production: Optional[datetime] = Field(default=None, description="When production last occurred")
    efficiency: float = Field(default=0.5, description="Production efficiency (0.0 to 1.0)")
    morale: float = Field(default=0.5, description="Employee morale (0.0 to 1.0)")
    upkeep_cost: float = Field(default=10.0, description="Daily upkeep cost")
    income_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of income")
    weekly_income_history: List[float] = Field(default_factory=list, description="Weekly income history")
    upgrades: Dict[str, Any] = Field(default_factory=dict, description="Applied business upgrades")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for this business")