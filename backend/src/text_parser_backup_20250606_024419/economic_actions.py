"""
Economic Actions - Enum definitions for economic interactions

This module defines enums for all economic-related actions that players
can perform in the game, providing a standardized representation of player intent.
"""

from enum import Enum, auto


class EconomicAction(Enum):
    """
    Standardized representation of player intent for all economic activities.
    Used by the parser engine to categorize economic commands.
    """
    # Shop/Trade actions
    BUY_ITEM = auto()               # Purchase an item from shop/vendor
    SELL_ITEM = auto()              # Sell an item to shop/vendor
    LIST_SHOP_ITEMS = auto()        # List items available in a shop
    VIEW_ITEM_DETAILS = auto()      # View detailed information about an item
    GET_ITEM_PRICE = auto()         # Check the price of an item
    INITIATE_BARTER = auto()        # Start a bartering session with vendor
    COMPARE_PRICES = auto()         # Compare prices between vendors/markets

    # Crafting actions
    CRAFT_ITEM = auto()             # Craft an item from a recipe
    LIST_KNOWN_RECIPES = auto()     # List recipes the player knows
    LIST_CRAFTABLE_RECIPES = auto() # List recipes the player can currently craft
    VIEW_RECIPE_DETAILS = auto()    # View detailed information about a recipe
    ATTEMPT_RECIPE_DISCOVERY = auto() # Try to discover a new recipe
    CHECK_CRAFTING_MATERIALS = auto() # Check what materials are needed/available
    
    # Business Management (Player-Owned)
    VIEW_BUSINESS_STATUS = auto()       # Check status of player-owned business
    SET_PRODUCT_PRICE = auto()          # Set price for products in business
    MANAGE_BUSINESS_INVENTORY = auto()  # Manage business inventory
    HIRE_STAFF = auto()                 # Hire staff for business
    ASSIGN_STAFF_TASK = auto()          # Assign tasks to staff
    UPGRADE_BUSINESS = auto()           # Upgrade business facilities
    VIEW_BUSINESS_LEDGER = auto()       # View business financial records
    PAY_BUSINESS_TAXES = auto()         # Pay taxes for business
    COLLECT_BUSINESS_PROFITS = auto()   # Collect profits from business
    
    # Building & Property
    CONSTRUCT_BUILDING = auto()        # Construct a new building
    UPGRADE_BUILDING = auto()          # Upgrade an existing building
    LIST_AVAILABLE_BUILDINGS = auto()  # List available building templates
    VIEW_BUILDING_DETAILS = auto()     # View details of a building or template
    REPAIR_BUILDING = auto()           # Repair a damaged building
    BUY_PROPERTY = auto()              # Purchase land/property
    SELL_PROPERTY = auto()             # Sell land/property
    
    # Resource & Inventory Queries
    CHECK_INVENTORY = auto()           # Check player's inventory
    CHECK_CURRENCY = auto()            # Check player's currency balance
    LOCATE_MATERIAL_SOURCE = auto()    # Find where to obtain a material
    
    # Market Interaction
    GET_MARKET_PRICE_INFO = auto()     # Get information about market prices
    ACCESS_BLACK_MARKET = auto()       # Access the black market
    LIST_BLACK_MARKET_GOODS = auto()   # List black market goods
    
    # Illicit Business Operations
    START_ILLICIT_OPERATION = auto()   # Start an illicit business operation
    LAUNDER_MONEY = auto()             # Launder money from illicit operations
    BRIBE_AUTHORITY = auto()           # Bribe an authority figure
    CHECK_HEAT_LEVEL = auto()          # Check current "heat" level for illegal activity
    FENCE_STOLEN_GOODS = auto()        # Sell stolen goods to a fence


class CraftingProfession(Enum):
    """
    Crafting professions available in the game.
    Used for categorizing recipes and specializations.
    """
    BLACKSMITHING = auto()
    ALCHEMY = auto()
    WOODWORKING = auto()
    TAILORING = auto()
    LEATHERWORKING = auto()
    JEWELCRAFTING = auto()
    RELICSMITHING = auto()
    ENCHANTING = auto()
    COOKING = auto()
    SCRIBING = auto()


class BusinessType(Enum):
    """
    Types of businesses that can be operated in the game.
    """
    SHOP = auto()             # General merchandise
    TAVERN = auto()           # Food and drink
    SMITHY = auto()           # Weapons and armor
    APOTHECARY = auto()       # Potions and remedies
    TAILOR = auto()           # Clothing and fabric goods
    JEWELER = auto()          # Jewelry and precious stones
    CARPENTER = auto()        # Wooden items and furniture
    TANNERY = auto()          # Leather goods
    GUILD_HALL = auto()       # Professional services
    ILLICIT_FRONT = auto()    # Front for illicit operations


class BuildingType(Enum):
    """
    Types of buildings that can be constructed in the game.
    """
    RESIDENTIAL = auto()      # Living quarters
    COMMERCIAL = auto()       # Business operations
    WORKSHOP = auto()         # Crafting facilities
    WAREHOUSE = auto()        # Storage
    TAVERN = auto()           # Food, drink, lodging
    FORTIFICATION = auto()    # Defensive structures
    OUTPOST = auto()          # Remote operations
    HIDDEN = auto()           # Concealed facilities


class MarketType(Enum):
    """
    Types of markets that can be accessed in the game.
    """
    STANDARD = auto()         # Regular, legal marketplace
    PREMIUM = auto()          # High-end, luxury goods
    BLACK_MARKET = auto()     # Illegal goods and services
    UNDERGROUND = auto()      # Semi-legal, discretionary goods
    AUCTION = auto()          # Bidding-based marketplace