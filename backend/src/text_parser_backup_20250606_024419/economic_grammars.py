"""
Economic Grammars - Grammar rules and patterns for economic interactions

This module provides grammar rules and regex patterns for identifying economic commands
and extracting key entities from player input. It works with the economic vocabulary
to parse a wide range of economic interactions including trading, crafting, and business
management.
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Set, Match
from dataclasses import dataclass, field
from pydantic import BaseModel

from .economic_actions import EconomicAction
from .economic_vocabulary import (
    BUY_VERBS, SELL_VERBS, SHOP_BROWSE_VERBS, PRICE_CHECK_VERBS, BARTER_VERBS,
    CRAFT_VERBS, RECIPE_VERBS, BUSINESS_VERBS, HIRE_VERBS, UPGRADE_VERBS,
    FINANCE_VERBS, CONSTRUCTION_VERBS, REPAIR_VERBS, PROPERTY_VERBS,
    INVENTORY_VERBS, MARKET_VERBS, ILLICIT_VERBS, SHOP_NOUNS, BUSINESS_NOUNS,
    BUILDING_NOUNS, BLACK_MARKET_TERMS, CURRENCY_NOUNS, PROFESSION_NAMES,
    QUANTITY_MODIFIERS, PRICE_MODIFIERS
)


class ParsedEconomicCommand(BaseModel):
    """Structured representation of a parsed economic command."""
    action: EconomicAction
    primary_target: Optional[str] = None  # Item, recipe, business, building name
    secondary_target: Optional[str] = None  # Shop, vendor, location name
    quantity: Optional[int] = None
    price: Optional[float] = None
    currency_type: Optional[str] = "gold"
    raw_text: str
    modifiers: Dict[str, Any] = {}
    confidence: float = 1.0


class GameContext(BaseModel):
    """Context information for the current game state."""
    player_id: str
    location_id: Optional[str] = None
    current_npc_id: Optional[str] = None
    current_shop_id: Optional[str] = None
    current_business_id: Optional[str] = None
    market_region_id: Optional[str] = None
    inventory_open: bool = False
    crafting_open: bool = False
    in_black_market: bool = False
    in_conversation: bool = False
    

# Compile regex patterns for each category of economic command
class EconomicGrammarPatterns:
    """Regex patterns for different categories of economic commands."""
    
    # Buy patterns - buy [quantity] [item] from [shop/vendor] for [price] [currency]
    BUY_PATTERNS = [
        # Basic buy: "buy sword"
        re.compile(r"^(?:" + "|".join(BUY_VERBS) + r")\s+(.+?)$", re.IGNORECASE),
        
        # Buy with quantity: "buy 5 health potions"
        re.compile(r"^(?:" + "|".join(BUY_VERBS) + r")\s+(\d+)\s+(.+?)$", re.IGNORECASE),
        
        # Buy from vendor: "buy sword from blacksmith"
        re.compile(r"^(?:" + "|".join(BUY_VERBS) + r")\s+(.+?)\s+(?:from|at)\s+(.+?)$", re.IGNORECASE),
        
        # Buy with quantity from vendor: "buy 5 arrows from fletcher"
        re.compile(r"^(?:" + "|".join(BUY_VERBS) + r")\s+(\d+)\s+(.+?)\s+(?:from|at)\s+(.+?)$", re.IGNORECASE),
        
        # Buy with price: "buy sword for 50 gold"
        re.compile(r"^(?:" + "|".join(BUY_VERBS) + r")\s+(.+?)\s+for\s+(\d+)\s+(.+?)$", re.IGNORECASE),
        
        # Complete: "buy 2 health potions from alchemist for 30 gold"
        re.compile(r"^(?:" + "|".join(BUY_VERBS) + r")\s+(\d+)\s+(.+?)\s+(?:from|at)\s+(.+?)\s+for\s+(\d+)\s+(.+?)$", re.IGNORECASE),
    ]
    
    # Sell patterns - sell [quantity] [item] to [shop/vendor] for [price] [currency]
    SELL_PATTERNS = [
        # Basic sell: "sell sword"
        re.compile(r"^(?:" + "|".join(SELL_VERBS) + r")\s+(.+?)$", re.IGNORECASE),
        
        # Sell with quantity: "sell 5 ores"
        re.compile(r"^(?:" + "|".join(SELL_VERBS) + r")\s+(\d+)\s+(.+?)$", re.IGNORECASE),
        
        # Sell to vendor: "sell sword to blacksmith"
        re.compile(r"^(?:" + "|".join(SELL_VERBS) + r")\s+(.+?)\s+(?:to|at)\s+(.+?)$", re.IGNORECASE),
        
        # Sell with quantity to vendor: "sell 5 ores to miner"
        re.compile(r"^(?:" + "|".join(SELL_VERBS) + r")\s+(\d+)\s+(.+?)\s+(?:to|at)\s+(.+?)$", re.IGNORECASE),
        
        # Sell with price: "sell sword for 50 gold"
        re.compile(r"^(?:" + "|".join(SELL_VERBS) + r")\s+(.+?)\s+for\s+(\d+)\s+(.+?)$", re.IGNORECASE),
        
        # Complete: "sell 2 iron swords to blacksmith for 30 gold"
        re.compile(r"^(?:" + "|".join(SELL_VERBS) + r")\s+(\d+)\s+(.+?)\s+(?:to|at)\s+(.+?)\s+for\s+(\d+)\s+(.+?)$", re.IGNORECASE),
    ]
    
    # Shop browse patterns - browse [shop/vendor]
    SHOP_BROWSE_PATTERNS = [
        # Basic browse: "browse shop"
        re.compile(r"^(?:" + "|".join(SHOP_BROWSE_VERBS) + r")\s+(.+?)$", re.IGNORECASE),
        
        # List items: "list items in shop"
        re.compile(r"^(?:list|show|see|view)\s+(?:items|goods|products|merchandise|wares|inventory)\s+(?:in|at|from)\s+(.+?)$", re.IGNORECASE),
        
        # What's for sale: "what do you have for sale"
        re.compile(r"^what(?:'s| is| do you have| are you selling)?\s+(?:for sale|available|in stock)$", re.IGNORECASE),
        
        # Show me: "show me what you have"
        re.compile(r"^show\s+(?:me|us)\s+(?:what you have|your wares|your goods|your items|your inventory)$", re.IGNORECASE),
    ]
    
    # Price check patterns - price/value/cost of [item]
    PRICE_CHECK_PATTERNS = [
        # Basic price check: "price of sword"
        re.compile(r"^(?:" + "|".join(PRICE_CHECK_VERBS) + r")\s+(?:of|for)\s+(.+?)$", re.IGNORECASE),
        
        # How much: "how much for a sword"
        re.compile(r"^how much\s+(?:is|for|would you pay for|would you charge for)\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
        
        # What's the price: "what's the price of a health potion"
        re.compile(r"^what(?:'s| is)\s+the\s+(?:price|cost|value)\s+of\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
    ]
    
    # Craft patterns - craft [quantity] [item] using [materials]
    CRAFT_PATTERNS = [
        # Basic craft: "craft sword"
        re.compile(r"^(?:" + "|".join(CRAFT_VERBS) + r")\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
        
        # Craft with quantity: "craft 5 potions"
        re.compile(r"^(?:" + "|".join(CRAFT_VERBS) + r")\s+(\d+)\s+(.+?)$", re.IGNORECASE),
        
        # Craft using materials: "craft sword using iron ingot and leather"
        re.compile(r"^(?:" + "|".join(CRAFT_VERBS) + r")\s+(?:a|an|the)?\s*(.+?)\s+using\s+(.+?)$", re.IGNORECASE),
        
        # Craft with quantity using materials: "craft 3 arrows using wood and feathers"
        re.compile(r"^(?:" + "|".join(CRAFT_VERBS) + r")\s+(\d+)\s+(.+?)\s+using\s+(.+?)$", re.IGNORECASE),
    ]
    
    # Recipe patterns - list recipes, view recipe details
    RECIPE_PATTERNS = [
        # List all recipes: "list recipes"
        re.compile(r"^(?:list|show|view|see)\s+(?:all)?\s*(?:recipes|formulas|blueprints|schematics)$", re.IGNORECASE),
        
        # List craftable recipes: "list craftable recipes"
        re.compile(r"^(?:list|show|view|see)\s+(?:craftable|available)\s+(?:recipes|formulas|blueprints|schematics)$", re.IGNORECASE),
        
        # View recipe details: "view recipe for sword"
        re.compile(r"^(?:view|show|examine|inspect|check)\s+(?:recipe|formula|blueprint|schematic)\s+(?:for|of)\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
        
        # Learn/discover recipe: "learn recipe for potion"
        re.compile(r"^(?:learn|discover|research|study)\s+(?:recipe|formula|blueprint|schematic)\s+(?:for|of)\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
    ]
    
    # Business management patterns - manage business, view status, etc.
    BUSINESS_PATTERNS = [
        # View business status: "view business status"
        re.compile(r"^(?:view|check|see|show)\s+(?:business|shop|store)\s+(?:status|stats|info|information|overview)$", re.IGNORECASE),
        
        # Set product price: "set price of sword to 50 gold"
        re.compile(r"^(?:set|change|adjust|modify)\s+(?:price|cost|value)\s+of\s+(?:a|an|the)?\s*(.+?)\s+to\s+(\d+)\s+(?:gold|coins|money|currency)$", re.IGNORECASE),
        
        # Manage business inventory: "manage business inventory"
        re.compile(r"^(?:manage|check|view|see|show)\s+(?:business|shop|store)\s+(?:inventory|stock|supplies|goods)$", re.IGNORECASE),
        
        # Hire staff: "hire assistant for shop"
        re.compile(r"^(?:hire|recruit|employ|engage)\s+(?:a|an|the)?\s*(.+?)\s+(?:for|at|in)\s+(?:my)?\s*(?:business|shop|store)$", re.IGNORECASE),
        
        # Assign staff task: "assign crafting to apprentice"
        re.compile(r"^(?:assign|give|set)\s+(.+?)\s+(?:to|for)\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
        
        # Upgrade business: "upgrade business"
        re.compile(r"^(?:upgrade|improve|enhance|expand)\s+(?:my)?\s*(?:business|shop|store)$", re.IGNORECASE),
        
        # View business ledger: "view business ledger"
        re.compile(r"^(?:view|check|see|show)\s+(?:business|shop|store)\s+(?:ledger|finances|accounts|books|profits|income)$", re.IGNORECASE),
        
        # Pay business taxes: "pay business taxes"
        re.compile(r"^(?:pay|settle|clear)\s+(?:business|shop|store)\s+(?:taxes|dues|fees|tariffs)$", re.IGNORECASE),
        
        # Collect business profits: "collect business profits"
        re.compile(r"^(?:collect|gather|take|withdraw)\s+(?:business|shop|store)\s+(?:profits|earnings|income|money|revenue)$", re.IGNORECASE),
    ]
    
    # Building patterns - construct building, upgrade building, etc.
    BUILDING_PATTERNS = [
        # Construct building: "construct blacksmith shop"
        re.compile(r"^(?:" + "|".join(CONSTRUCTION_VERBS) + r")\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
        
        # Construct building at location: "construct tavern at town square"
        re.compile(r"^(?:" + "|".join(CONSTRUCTION_VERBS) + r")\s+(?:a|an|the)?\s*(.+?)\s+(?:at|in|on|near)\s+(.+?)$", re.IGNORECASE),
        
        # Upgrade building: "upgrade blacksmith shop"
        re.compile(r"^(?:" + "|".join(UPGRADE_VERBS) + r")\s+(?:my|the)?\s*(.+?)$", re.IGNORECASE),
        
        # List available buildings: "list available buildings"
        re.compile(r"^(?:list|show|view|see)\s+(?:available|possible)\s+(?:buildings|structures|constructions|building types)$", re.IGNORECASE),
        
        # View building details: "view details of blacksmith shop"
        re.compile(r"^(?:view|show|examine|inspect|check)\s+(?:details|info|information|specs|specifics)\s+(?:of|for|about)\s+(?:a|an|the)?\s*(.+?)$", re.IGNORECASE),
        
        # Repair building: "repair tavern"
        re.compile(r"^(?:" + "|".join(REPAIR_VERBS) + r")\s+(?:my|the)?\s*(.+?)$", re.IGNORECASE),
    ]
    
    # Inventory and currency patterns - check inventory, check currency
    INVENTORY_PATTERNS = [
        # Basic inventory check: "check inventory"
        re.compile(r"^(?:check|view|see|show|open|display)\s+(?:my)?\s*(?:inventory|items|possessions|backpack|bag|belongings)$", re.IGNORECASE),
        
        # Check for specific item: "check inventory for health potions"
        re.compile(r"^(?:check|view|see|show)\s+(?:my)?\s*(?:inventory|items|possessions|backpack|bag|belongings)\s+for\s+(.+?)$", re.IGNORECASE),
        
        # Check currency: "check gold"
        re.compile(r"^(?:check|view|see|show|count)\s+(?:my)?\s*(?:gold|coins|money|currency|funds|wallet|purse)$", re.IGNORECASE),
        
        # Locate material source: "where to find iron ore"
        re.compile(r"^(?:where|how)\s+(?:to|can i|do i)\s+(?:find|get|obtain|acquire|gather|mine|harvest|collect)\s+(.+?)$", re.IGNORECASE),
    ]
    
    # Market and black market patterns - access market, check prices, etc.
    MARKET_PATTERNS = [
        # Get market prices: "check market prices"
        re.compile(r"^(?:check|view|see|show)\s+(?:market|shop|store|vendor)\s+(?:prices|rates|values|costs)$", re.IGNORECASE),
        
        # Get price of specific item in market: "check market price of health potion"
        re.compile(r"^(?:check|view|see|show)\s+(?:market|shop|store|vendor)\s+(?:price|rate|value|cost)\s+(?:of|for)\s+(.+?)$", re.IGNORECASE),
        
        # Access black market: "access black market"
        re.compile(r"^(?:access|enter|visit|go to)\s+(?:the)?\s*(?:" + "|".join(BLACK_MARKET_TERMS) + r")$", re.IGNORECASE),
        
        # List black market goods: "list black market goods"
        re.compile(r"^(?:list|show|view|see)\s+(?:the)?\s*(?:" + "|".join(BLACK_MARKET_TERMS) + r")\s+(?:goods|items|wares|merchandise|inventory|products)$", re.IGNORECASE),
    ]
    
    # Illicit business operations patterns - launder money, bribe official, etc.
    ILLICIT_PATTERNS = [
        # Start illicit operation: "start smuggling operation"
        re.compile(r"^(?:start|begin|initiate|setup|establish)\s+(?:a|an|the)?\s*(.+?)\s+(?:operation|business|venture|racket)$", re.IGNORECASE),
        
        # Launder money: "launder money"
        re.compile(r"^(?:launder|clean|wash)\s+(?:money|funds|gold|coins|currency|cash)$", re.IGNORECASE),
        
        # Bribe official: "bribe guard"
        re.compile(r"^(?:bribe|pay off|corrupt|influence)\s+(?:the)?\s*(.+?)$", re.IGNORECASE),
        
        # Check heat level: "check heat level"
        re.compile(r"^(?:check|view|see|show)\s+(?:heat|suspicion|attention|wanted|notoriety|infamy)\s+(?:level|status|rating)$", re.IGNORECASE),
        
        # Fence stolen goods: "fence stolen necklace"
        re.compile(r"^(?:fence|sell|dispose of|offload)\s+(?:stolen|hot|illegal|illicit)\s+(.+?)$", re.IGNORECASE),
    ]
    
    @classmethod
    def get_all_patterns(cls) -> Dict[str, List[re.Pattern]]:
        """Get all grammar patterns organized by category."""
        return {
            "buy": cls.BUY_PATTERNS,
            "sell": cls.SELL_PATTERNS,
            "shop_browse": cls.SHOP_BROWSE_PATTERNS,
            "price_check": cls.PRICE_CHECK_PATTERNS,
            "craft": cls.CRAFT_PATTERNS,
            "recipe": cls.RECIPE_PATTERNS,
            "business": cls.BUSINESS_PATTERNS,
            "building": cls.BUILDING_PATTERNS,
            "inventory": cls.INVENTORY_PATTERNS,
            "market": cls.MARKET_PATTERNS,
            "illicit": cls.ILLICIT_PATTERNS
        }


def match_economic_command(text: str, context: Optional[GameContext] = None) -> Optional[ParsedEconomicCommand]:
    """
    Match an economic command from player input text.
    
    Args:
        text: The player's input text
        context: Optional game context information
        
    Returns:
        ParsedEconomicCommand object if a match is found, None otherwise
    """
    # Clean up input text
    text = text.strip().lower()
    
    # Categorize by looking for action verbs
    for category, patterns in EconomicGrammarPatterns.get_all_patterns().items():
        for pattern in patterns:
            match = pattern.match(text)
            if match:
                # Process match based on category
                if category == "buy":
                    return _process_buy_match(match, text, pattern)
                elif category == "sell":
                    return _process_sell_match(match, text, pattern)
                elif category == "shop_browse":
                    return _process_shop_browse_match(match, text, pattern)
                elif category == "price_check":
                    return _process_price_check_match(match, text, pattern)
                elif category == "craft":
                    return _process_craft_match(match, text, pattern)
                elif category == "recipe":
                    return _process_recipe_match(match, text, pattern)
                elif category == "business":
                    return _process_business_match(match, text, pattern)
                elif category == "building":
                    return _process_building_match(match, text, pattern)
                elif category == "inventory":
                    return _process_inventory_match(match, text, pattern)
                elif category == "market":
                    return _process_market_match(match, text, pattern)
                elif category == "illicit":
                    return _process_illicit_match(match, text, pattern)
    
    # Use contextual information for better matching
    if context:
        if context.inventory_open:
            # If inventory is open, check for item interactions
            words = text.split()
            if len(words) >= 1:
                # Simplistic handling for single item reference while inventory is open
                item_name = text
                return ParsedEconomicCommand(
                    action=EconomicAction.VIEW_ITEM_DETAILS,
                    primary_target=item_name,
                    raw_text=text,
                    confidence=0.7
                )
        
        if context.crafting_open:
            # If crafting interface is open, check for crafting commands
            words = text.split()
            if len(words) >= 1:
                # Simplistic handling for single recipe reference while crafting is open
                recipe_name = text
                return ParsedEconomicCommand(
                    action=EconomicAction.CRAFT_ITEM,
                    primary_target=recipe_name,
                    raw_text=text,
                    confidence=0.7
                )
    
    # No match found
    return None


def _process_buy_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a buy command match."""
    groups = match.groups()
    
    if len(groups) == 1:
        # Simple "buy sword"
        item_name = groups[0]
        return ParsedEconomicCommand(
            action=EconomicAction.BUY_ITEM,
            primary_target=item_name,
            quantity=1,
            raw_text=text
        )
    elif len(groups) == 2:
        # "buy 5 health potions" or "buy sword from blacksmith"
        if groups[0].isdigit():
            quantity = int(groups[0])
            item_name = groups[1]
            return ParsedEconomicCommand(
                action=EconomicAction.BUY_ITEM,
                primary_target=item_name,
                quantity=quantity,
                raw_text=text
            )
        else:
            item_name = groups[0]
            vendor_name = groups[1]
            return ParsedEconomicCommand(
                action=EconomicAction.BUY_ITEM,
                primary_target=item_name,
                secondary_target=vendor_name,
                quantity=1,
                raw_text=text
            )
    elif len(groups) == 3:
        # Multiple possible formats
        if groups[0].isdigit() and "from" in text or "at" in text:
            # "buy 5 arrows from fletcher"
            quantity = int(groups[0])
            item_name = groups[1]
            vendor_name = groups[2]
            return ParsedEconomicCommand(
                action=EconomicAction.BUY_ITEM,
                primary_target=item_name,
                secondary_target=vendor_name,
                quantity=quantity,
                raw_text=text
            )
        elif "for" in text and groups[1].isdigit():
            # "buy sword for 50 gold"
            item_name = groups[0]
            price = int(groups[1])
            currency = groups[2]
            return ParsedEconomicCommand(
                action=EconomicAction.BUY_ITEM,
                primary_target=item_name,
                quantity=1,
                price=price,
                currency_type=currency,
                raw_text=text
            )
    elif len(groups) == 5:
        # "buy 2 health potions from alchemist for 30 gold"
        quantity = int(groups[0])
        item_name = groups[1]
        vendor_name = groups[2]
        price = int(groups[3])
        currency = groups[4]
        return ParsedEconomicCommand(
            action=EconomicAction.BUY_ITEM,
            primary_target=item_name,
            secondary_target=vendor_name,
            quantity=quantity,
            price=price,
            currency_type=currency,
            raw_text=text
        )
    
    # Default fallback for partial matches
    return ParsedEconomicCommand(
        action=EconomicAction.BUY_ITEM,
        primary_target=groups[0] if groups else None,
        raw_text=text,
        confidence=0.8
    )


def _process_sell_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a sell command match."""
    groups = match.groups()
    
    if len(groups) == 1:
        # Simple "sell sword"
        item_name = groups[0]
        return ParsedEconomicCommand(
            action=EconomicAction.SELL_ITEM,
            primary_target=item_name,
            quantity=1,
            raw_text=text
        )
    elif len(groups) == 2:
        # "sell 5 ores" or "sell sword to blacksmith"
        if groups[0].isdigit():
            quantity = int(groups[0])
            item_name = groups[1]
            return ParsedEconomicCommand(
                action=EconomicAction.SELL_ITEM,
                primary_target=item_name,
                quantity=quantity,
                raw_text=text
            )
        else:
            item_name = groups[0]
            vendor_name = groups[1]
            return ParsedEconomicCommand(
                action=EconomicAction.SELL_ITEM,
                primary_target=item_name,
                secondary_target=vendor_name,
                quantity=1,
                raw_text=text
            )
    elif len(groups) == 3:
        # Multiple possible formats
        if groups[0].isdigit() and "to" in text or "at" in text:
            # "sell 5 ores to miner"
            quantity = int(groups[0])
            item_name = groups[1]
            vendor_name = groups[2]
            return ParsedEconomicCommand(
                action=EconomicAction.SELL_ITEM,
                primary_target=item_name,
                secondary_target=vendor_name,
                quantity=quantity,
                raw_text=text
            )
        elif "for" in text and groups[1].isdigit():
            # "sell sword for 50 gold"
            item_name = groups[0]
            price = int(groups[1])
            currency = groups[2]
            return ParsedEconomicCommand(
                action=EconomicAction.SELL_ITEM,
                primary_target=item_name,
                quantity=1,
                price=price,
                currency_type=currency,
                raw_text=text
            )
    elif len(groups) == 5:
        # "sell 2 iron swords to blacksmith for 30 gold"
        quantity = int(groups[0])
        item_name = groups[1]
        vendor_name = groups[2]
        price = int(groups[3])
        currency = groups[4]
        return ParsedEconomicCommand(
            action=EconomicAction.SELL_ITEM,
            primary_target=item_name,
            secondary_target=vendor_name,
            quantity=quantity,
            price=price,
            currency_type=currency,
            raw_text=text
        )
    
    # Default fallback for partial matches
    return ParsedEconomicCommand(
        action=EconomicAction.SELL_ITEM,
        primary_target=groups[0] if groups else None,
        raw_text=text,
        confidence=0.8
    )


def _process_shop_browse_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a shop browse command match."""
    groups = match.groups()
    
    # Handle "what do you have for sale", etc.
    if not any(groups) or all(g is None for g in groups):
        return ParsedEconomicCommand(
            action=EconomicAction.LIST_SHOP_ITEMS,
            raw_text=text
        )
    
    # "browse shop" or "list items in shop"
    shop_name = next((g for g in groups if g), None)
    
    return ParsedEconomicCommand(
        action=EconomicAction.LIST_SHOP_ITEMS,
        secondary_target=shop_name,
        raw_text=text
    )


def _process_price_check_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a price check command match."""
    groups = match.groups()
    
    # "price of sword", "how much for a sword", "what's the price of a health potion"
    item_name = next((g for g in groups if g), None)
    
    return ParsedEconomicCommand(
        action=EconomicAction.GET_ITEM_PRICE,
        primary_target=item_name,
        raw_text=text
    )


def _process_craft_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a craft command match."""
    groups = match.groups()
    
    if len(groups) == 1:
        # "craft sword"
        item_name = groups[0]
        return ParsedEconomicCommand(
            action=EconomicAction.CRAFT_ITEM,
            primary_target=item_name,
            quantity=1,
            raw_text=text
        )
    elif len(groups) == 2:
        # "craft 5 potions" or "craft sword using iron ingot"
        if groups[0].isdigit():
            quantity = int(groups[0])
            item_name = groups[1]
            return ParsedEconomicCommand(
                action=EconomicAction.CRAFT_ITEM,
                primary_target=item_name,
                quantity=quantity,
                raw_text=text
            )
        else:
            item_name = groups[0]
            materials = groups[1]
            return ParsedEconomicCommand(
                action=EconomicAction.CRAFT_ITEM,
                primary_target=item_name,
                quantity=1,
                modifiers={"materials": materials.split(" and ")},
                raw_text=text
            )
    elif len(groups) == 3:
        # "craft 3 arrows using wood and feathers"
        quantity = int(groups[0])
        item_name = groups[1]
        materials = groups[2]
        return ParsedEconomicCommand(
            action=EconomicAction.CRAFT_ITEM,
            primary_target=item_name,
            quantity=quantity,
            modifiers={"materials": materials.split(" and ")},
            raw_text=text
        )
    
    # Default fallback for partial matches
    return ParsedEconomicCommand(
        action=EconomicAction.CRAFT_ITEM,
        primary_target=groups[0] if groups else None,
        raw_text=text,
        confidence=0.8
    )


def _process_recipe_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a recipe command match."""
    groups = match.groups()
    
    # No groups or all None - basic "list recipes"
    if not any(groups) or all(g is None for g in groups):
        if "craftable" in text or "available" in text:
            return ParsedEconomicCommand(
                action=EconomicAction.LIST_CRAFTABLE_RECIPES,
                raw_text=text
            )
        else:
            return ParsedEconomicCommand(
                action=EconomicAction.LIST_KNOWN_RECIPES,
                raw_text=text
            )
    
    # "view recipe for sword" or "learn recipe for potion"
    recipe_name = next((g for g in groups if g), None)
    
    if "view" in text or "show" in text or "examine" in text or "inspect" in text or "check" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.VIEW_RECIPE_DETAILS,
            primary_target=recipe_name,
            raw_text=text
        )
    elif "learn" in text or "discover" in text or "research" in text or "study" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.ATTEMPT_RECIPE_DISCOVERY,
            primary_target=recipe_name,
            raw_text=text
        )
    
    # Default
    return ParsedEconomicCommand(
        action=EconomicAction.VIEW_RECIPE_DETAILS,
        primary_target=recipe_name,
        raw_text=text,
        confidence=0.8
    )


def _process_business_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a business management command match."""
    groups = match.groups()
    
    # Determine the action based on the text
    if "status" in text or "stats" in text or "info" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.VIEW_BUSINESS_STATUS,
            raw_text=text
        )
    elif "price" in text or "cost" in text or "value" in text:
        # "set price of sword to 50 gold"
        item_name = groups[0] if groups and len(groups) > 0 else None
        price = int(groups[1]) if groups and len(groups) > 1 and groups[1].isdigit() else None
        return ParsedEconomicCommand(
            action=EconomicAction.SET_PRODUCT_PRICE,
            primary_target=item_name,
            price=price,
            raw_text=text
        )
    elif "inventory" in text or "stock" in text or "supplies" in text or "goods" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.MANAGE_BUSINESS_INVENTORY,
            raw_text=text
        )
    elif "hire" in text or "recruit" in text or "employ" in text:
        # "hire assistant for shop"
        staff_type = groups[0] if groups and len(groups) > 0 else None
        return ParsedEconomicCommand(
            action=EconomicAction.HIRE_STAFF,
            primary_target=staff_type,
            raw_text=text
        )
    elif "assign" in text or "give" in text or "set" in text:
        # "assign crafting to apprentice"
        task = groups[0] if groups and len(groups) > 0 else None
        staff = groups[1] if groups and len(groups) > 1 else None
        return ParsedEconomicCommand(
            action=EconomicAction.ASSIGN_STAFF_TASK,
            primary_target=staff,
            modifiers={"task": task},
            raw_text=text
        )
    elif "upgrade" in text or "improve" in text or "enhance" in text or "expand" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.UPGRADE_BUSINESS,
            raw_text=text
        )
    elif "ledger" in text or "finances" in text or "accounts" in text or "books" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.VIEW_BUSINESS_LEDGER,
            raw_text=text
        )
    elif "taxes" in text or "dues" in text or "fees" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.PAY_BUSINESS_TAXES,
            raw_text=text
        )
    elif "profits" in text or "earnings" in text or "income" in text or "revenue" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.COLLECT_BUSINESS_PROFITS,
            raw_text=text
        )
    
    # Default - status check
    return ParsedEconomicCommand(
        action=EconomicAction.VIEW_BUSINESS_STATUS,
        raw_text=text,
        confidence=0.8
    )


def _process_building_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a building command match."""
    groups = match.groups()
    
    # Construct building
    if any(verb in text for verb in CONSTRUCTION_VERBS):
        building_name = groups[0] if groups and len(groups) > 0 else None
        location = groups[1] if groups and len(groups) > 1 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.CONSTRUCT_BUILDING,
            primary_target=building_name,
            secondary_target=location,
            raw_text=text
        )
    # Upgrade building
    elif any(verb in text for verb in UPGRADE_VERBS):
        building_name = groups[0] if groups and len(groups) > 0 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.UPGRADE_BUILDING,
            primary_target=building_name,
            raw_text=text
        )
    # List available buildings
    elif "list" in text or "show" in text or "view" in text or "see" in text:
        if "details" in text or "info" in text or "specs" in text:
            # View building details
            building_name = groups[0] if groups and len(groups) > 0 else None
            
            return ParsedEconomicCommand(
                action=EconomicAction.VIEW_BUILDING_DETAILS,
                primary_target=building_name,
                raw_text=text
            )
        else:
            # List available buildings
            return ParsedEconomicCommand(
                action=EconomicAction.LIST_AVAILABLE_BUILDINGS,
                raw_text=text
            )
    # Repair building
    elif any(verb in text for verb in REPAIR_VERBS):
        building_name = groups[0] if groups and len(groups) > 0 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.REPAIR_BUILDING,
            primary_target=building_name,
            raw_text=text
        )
    
    # Default
    return ParsedEconomicCommand(
        action=EconomicAction.VIEW_BUILDING_DETAILS,
        primary_target=groups[0] if groups and len(groups) > 0 else None,
        raw_text=text,
        confidence=0.8
    )


def _process_inventory_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process an inventory command match."""
    groups = match.groups()
    
    # Check inventory
    if "inventory" in text or "items" in text or "possessions" in text or "backpack" in text or "bag" in text:
        if "for" in text and groups and len(groups) > 0:
            # "check inventory for health potions"
            item_name = groups[0]
            
            return ParsedEconomicCommand(
                action=EconomicAction.CHECK_INVENTORY,
                primary_target=item_name,
                raw_text=text
            )
        else:
            # "check inventory"
            return ParsedEconomicCommand(
                action=EconomicAction.CHECK_INVENTORY,
                raw_text=text
            )
    # Check currency
    elif any(term in text for term in CURRENCY_NOUNS):
        return ParsedEconomicCommand(
            action=EconomicAction.CHECK_CURRENCY,
            raw_text=text
        )
    # Locate material source
    elif "where" in text or "how" in text or "find" in text or "get" in text:
        material_name = groups[0] if groups and len(groups) > 0 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.LOCATE_MATERIAL_SOURCE,
            primary_target=material_name,
            raw_text=text
        )
    
    # Default
    return ParsedEconomicCommand(
        action=EconomicAction.CHECK_INVENTORY,
        raw_text=text,
        confidence=0.8
    )


def _process_market_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process a market command match."""
    groups = match.groups()
    
    # Check market prices
    if "prices" in text or "rates" in text or "values" in text or "costs" in text:
        if "of" in text or "for" in text:
            # "check market price of health potion"
            item_name = groups[0] if groups and len(groups) > 0 else None
            
            return ParsedEconomicCommand(
                action=EconomicAction.GET_MARKET_PRICE_INFO,
                primary_target=item_name,
                raw_text=text
            )
        else:
            # "check market prices"
            return ParsedEconomicCommand(
                action=EconomicAction.GET_MARKET_PRICE_INFO,
                raw_text=text
            )
    # Access black market
    elif any(term.lower() in text.lower() for term in BLACK_MARKET_TERMS):
        if "list" in text or "show" in text or "view" in text or "see" in text:
            # "list black market goods"
            return ParsedEconomicCommand(
                action=EconomicAction.LIST_BLACK_MARKET_GOODS,
                raw_text=text
            )
        else:
            # "access black market"
            return ParsedEconomicCommand(
                action=EconomicAction.ACCESS_BLACK_MARKET,
                raw_text=text
            )
    
    # Default
    return ParsedEconomicCommand(
        action=EconomicAction.GET_MARKET_PRICE_INFO,
        raw_text=text,
        confidence=0.8
    )


def _process_illicit_match(match: Match, text: str, pattern: re.Pattern) -> ParsedEconomicCommand:
    """Process an illicit operations command match."""
    groups = match.groups()
    
    # Start illicit operation
    if "start" in text or "begin" in text or "initiate" in text or "setup" in text or "establish" in text:
        operation_type = groups[0] if groups and len(groups) > 0 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.START_ILLICIT_OPERATION,
            primary_target=operation_type,
            raw_text=text
        )
    # Launder money
    elif "launder" in text or "clean" in text or "wash" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.LAUNDER_MONEY,
            raw_text=text
        )
    # Bribe official
    elif "bribe" in text or "pay off" in text or "corrupt" in text or "influence" in text:
        official = groups[0] if groups and len(groups) > 0 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.BRIBE_AUTHORITY,
            primary_target=official,
            raw_text=text
        )
    # Check heat level
    elif "heat" in text or "suspicion" in text or "attention" in text or "wanted" in text or "notoriety" in text:
        return ParsedEconomicCommand(
            action=EconomicAction.CHECK_HEAT_LEVEL,
            raw_text=text
        )
    # Fence stolen goods
    elif "fence" in text or "sell" in text or "dispose of" in text or "offload" in text:
        item_name = groups[0] if groups and len(groups) > 0 else None
        
        return ParsedEconomicCommand(
            action=EconomicAction.FENCE_STOLEN_GOODS,
            primary_target=item_name,
            raw_text=text
        )
    
    # Default
    return ParsedEconomicCommand(
        action=EconomicAction.ACCESS_BLACK_MARKET,
        raw_text=text,
        confidence=0.8
    )