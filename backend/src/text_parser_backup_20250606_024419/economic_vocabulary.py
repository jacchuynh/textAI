"""
Economic Vocabulary - Specialized vocabulary for economic interactions

This module provides an extended vocabulary system to support economic interactions
in the game, including verbs, nouns, and modifiers related to trading, crafting,
business management, and building.
"""

from typing import Dict, List, Set


# Shop/Trade verbs
BUY_VERBS = [
    "buy", "purchase", "acquire", "get", "obtain", "procure", 
    "shop for", "pay for", "spend on"
]

SELL_VERBS = [
    "sell", "vend", "trade", "offer", "exchange", "hawk", 
    "market", "peddle", "deal", "liquidate"
]

SHOP_BROWSE_VERBS = [
    "browse", "shop", "peruse", "look through", "check out",
    "examine", "view", "see", "explore", "look at"
]

PRICE_CHECK_VERBS = [
    "price", "appraise", "value", "evaluate", "assess",
    "check price of", "how much for", "cost of", "worth of"
]

BARTER_VERBS = [
    "barter", "haggle", "negotiate", "bargain", "deal",
    "dicker", "wrangle", "parley", "talk price"
]

# Crafting verbs
CRAFT_VERBS = [
    "craft", "make", "create", "forge", "brew", "construct",
    "produce", "fashion", "fabricate", "manufacture", "assemble",
    "build", "smith", "weave", "sew", "tailor", "carve", "cut",
    "mix", "concoct", "prepare", "compose"
]

RECIPE_VERBS = [
    "know", "learn", "memorize", "study", "remember",
    "discover", "experiment", "try", "test", "formulate",
    "develop", "research", "list", "show"
]

# Business management verbs
BUSINESS_VERBS = [
    "manage", "run", "operate", "administer", "direct",
    "oversee", "supervise", "handle", "maintain", "control"
]

HIRE_VERBS = [
    "hire", "employ", "recruit", "engage", "enlist",
    "take on", "contract", "bring on", "staff", "sign"
]

UPGRADE_VERBS = [
    "upgrade", "improve", "enhance", "augment", "advance",
    "expand", "develop", "refine", "renovate", "modernize"
]

FINANCE_VERBS = [
    "pay", "invest", "fund", "finance", "bankroll",
    "capitalize", "back", "subsidize", "underwrite", "stake"
]

# Building verbs
CONSTRUCTION_VERBS = [
    "build", "construct", "erect", "raise", "assemble",
    "establish", "set up", "found", "install", "create"
]

REPAIR_VERBS = [
    "repair", "fix", "mend", "restore", "refurbish",
    "renovate", "recondition", "patch", "rebuild", "overhaul"
]

PROPERTY_VERBS = [
    "own", "possess", "hold", "maintain", "keep",
    "claim", "retain", "acquire", "have", "occupy"
]

# Inventory verbs
INVENTORY_VERBS = [
    "check", "view", "see", "examine", "inspect",
    "review", "look at", "assess", "evaluate", "tally"
]

# Market verbs
MARKET_VERBS = [
    "visit", "frequent", "attend", "patronize", "go to",
    "shop at", "buy from", "sell at", "trade in", "deal in"
]

# Illicit verbs
ILLICIT_VERBS = [
    "smuggle", "fence", "launder", "bribe", "extort",
    "blackmail", "swindle", "scam", "con", "racketeer"
]

# Economic nouns (categories)
SHOP_NOUNS = [
    "shop", "store", "market", "vendor", "merchant",
    "trader", "dealer", "retailer", "peddler", "hawker", "stand"
]

CURRENCY_NOUNS = [
    "gold", "coin", "money", "currency", "cash",
    "payment", "funds", "capital", "finance", "wealth", "treasure"
]

BUSINESS_NOUNS = [
    "business", "shop", "store", "establishment", "venture",
    "enterprise", "outfit", "operation", "concern", "firm",
    "company", "trade", "service", "proprietorship"
]

CRAFTING_NOUNS = [
    "recipe", "blueprint", "formula", "schematic", "pattern",
    "design", "template", "instruction", "guide", "method",
    "technique", "procedure", "process", "material", "ingredient",
    "component", "element", "piece", "part", "supply", "resource"
]

BUILDING_NOUNS = [
    "building", "structure", "construction", "edifice", "property",
    "establishment", "premises", "house", "facility", "installation",
    "shop", "store", "warehouse", "workshop", "factory", "plant",
    "mill", "foundry", "laboratory", "tavern", "inn", "lodge"
]

STAFF_NOUNS = [
    "staff", "employee", "worker", "personnel", "help",
    "laborer", "hand", "assistant", "aide", "associate",
    "craftsman", "artisan", "specialist", "expert", "journeyman",
    "apprentice", "novice", "trainee", "student", "pupil"
]

# Economic modifiers and prepositions
QUANTITY_MODIFIERS = [
    "quantity", "amount", "number", "count", "sum",
    "total", "volume", "bulk", "mass", "weight"
]

QUALITY_MODIFIERS = [
    "quality", "grade", "class", "tier", "caliber",
    "standard", "level", "rank", "category", "classification"
]

PRICE_MODIFIERS = [
    "price", "cost", "expense", "charge", "fee",
    "rate", "worth", "value", "premium", "discount"
]

LOCATION_PREPOSITIONS = [
    "at", "in", "from", "to", "with", "by", "near",
    "around", "inside", "outside", "beside", "beneath",
    "beyond", "through", "throughout", "within", "without"
]

# Profession names
PROFESSION_NAMES = [
    "blacksmith", "alchemist", "woodworker", "tailor",
    "leatherworker", "jeweler", "gemcutter", "relicsmith",
    "enchanter", "cook", "scribe", "smith", "weaponsmith",
    "armorsmith", "herbalist", "carpenter", "weaver",
    "cobbler", "tanner", "silversmith", "goldsmith"
]

# Business types
BUSINESS_TYPES = [
    "shop", "tavern", "smithy", "apothecary", "tailor",
    "jeweler", "carpenter", "tannery", "guild hall", "market",
    "stall", "stand", "store", "emporium", "boutique", "outlet"
]

# Building types
BUILDING_TYPES = [
    "house", "shop", "warehouse", "workshop", "tavern",
    "inn", "fort", "outpost", "tower", "cabin", "shack",
    "cottage", "mansion", "lodge", "hall", "hideout",
    "den", "lair", "sanctuary", "retreat", "haven"
]

# Black market terms
BLACK_MARKET_TERMS = [
    "black market", "underground market", "shadow market",
    "illegal goods", "contraband", "smuggled", "stolen",
    "illicit", "forbidden", "prohibited", "restricted", 
    "hot merchandise", "fence", "smuggler", "dealer",
    "underworld", "black marketeer", "crime ring"
]


def get_all_economic_verbs() -> List[str]:
    """Get a list of all economic verbs for pattern matching."""
    all_verbs = []
    all_verbs.extend(BUY_VERBS)
    all_verbs.extend(SELL_VERBS)
    all_verbs.extend(SHOP_BROWSE_VERBS)
    all_verbs.extend(PRICE_CHECK_VERBS)
    all_verbs.extend(BARTER_VERBS)
    all_verbs.extend(CRAFT_VERBS)
    all_verbs.extend(RECIPE_VERBS)
    all_verbs.extend(BUSINESS_VERBS)
    all_verbs.extend(HIRE_VERBS)
    all_verbs.extend(UPGRADE_VERBS)
    all_verbs.extend(FINANCE_VERBS)
    all_verbs.extend(CONSTRUCTION_VERBS)
    all_verbs.extend(REPAIR_VERBS)
    all_verbs.extend(PROPERTY_VERBS)
    all_verbs.extend(INVENTORY_VERBS)
    all_verbs.extend(MARKET_VERBS)
    all_verbs.extend(ILLICIT_VERBS)
    
    # Remove duplicates and standardize
    return list(set([verb.lower() for verb in all_verbs]))


def get_all_economic_nouns() -> List[str]:
    """Get a list of all economic nouns for pattern matching."""
    all_nouns = []
    all_nouns.extend(SHOP_NOUNS)
    all_nouns.extend(CURRENCY_NOUNS)
    all_nouns.extend(BUSINESS_NOUNS)
    all_nouns.extend(CRAFTING_NOUNS)
    all_nouns.extend(BUILDING_NOUNS)
    all_nouns.extend(STAFF_NOUNS)
    all_nouns.extend(PROFESSION_NAMES)
    all_nouns.extend(BUSINESS_TYPES)
    all_nouns.extend(BUILDING_TYPES)
    all_nouns.extend(BLACK_MARKET_TERMS)
    
    # Remove duplicates and standardize
    return list(set([noun.lower() for noun in all_nouns]))


def get_all_economic_modifiers() -> List[str]:
    """Get a list of all economic modifiers for pattern matching."""
    all_modifiers = []
    all_modifiers.extend(QUANTITY_MODIFIERS)
    all_modifiers.extend(QUALITY_MODIFIERS)
    all_modifiers.extend(PRICE_MODIFIERS)
    all_modifiers.extend(LOCATION_PREPOSITIONS)
    
    # Remove duplicates and standardize
    return list(set([modifier.lower() for modifier in all_modifiers]))


# Verb category mapping
VERB_CATEGORY_MAP = {
    "buy": BUY_VERBS,
    "sell": SELL_VERBS,
    "browse": SHOP_BROWSE_VERBS,
    "price": PRICE_CHECK_VERBS,
    "barter": BARTER_VERBS,
    "craft": CRAFT_VERBS,
    "recipe": RECIPE_VERBS,
    "business": BUSINESS_VERBS,
    "hire": HIRE_VERBS,
    "upgrade": UPGRADE_VERBS,
    "finance": FINANCE_VERBS,
    "build": CONSTRUCTION_VERBS,
    "repair": REPAIR_VERBS,
    "property": PROPERTY_VERBS,
    "inventory": INVENTORY_VERBS,
    "market": MARKET_VERBS,
    "illicit": ILLICIT_VERBS
}


def get_verb_category(verb: str) -> str:
    """
    Get the category of a verb.
    
    Args:
        verb: The verb to categorize
        
    Returns:
        The category name or None if not found
    """
    verb = verb.lower()
    
    for category, verbs in VERB_CATEGORY_MAP.items():
        if verb in verbs:
            return category
            
    return None