"""
Recipe Archetypes for the Crafting System

This module contains comprehensive recipe data for seeding the database.
All recipe archetypes are organized by profession.
"""

# Blacksmithing & Armorsmithing Recipes
BLACKSMITHING_RECIPES = [
    # Smelting & Basic Processing
    {
        "name": "Smelt Iron Ingot",
        "description": "Smelt raw iron ore into usable metal ingots using a forge.",
        "recipe_category": "Blacksmithing - Smelting",
        "crafting_time_seconds": 600,
        "required_station_type": "Forge",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 30}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Common Iron Ore", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Iron Ingot", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": True}
        ]
    },
    {
        "name": "Smelt Steel Ingot",
        "description": "Create steel by combining iron with carbon at high temperatures. A fundamental alloy in advanced smithing.",
        "recipe_category": "Blacksmithing - Alloy Creation",
        "crafting_time_seconds": 1200,
        "required_station_type": "Forge",
        "difficulty_level": 3,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 50}],
        "quality_range": {"min": 1, "max": 5},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Stonewake Coal Seam", "quantity": 0.5, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Steel Ingot", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 2, "affects_quality": True}
        ]
    },
    # Weapons & Tools
    {
        "name": "Forge Simple Iron Dagger",
        "description": "A basic iron dagger suitable for self-defense or utility purposes. Simple to craft but not particularly durable.",
        "recipe_category": "Blacksmithing - Weapons (Basic)",
        "crafting_time_seconds": 1200,
        "required_station_type": "Forge",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 40}, {"skill_name": "Weaponsmithing", "amount": 20}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Sturdy Ash Wood Haft", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 0.5, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Simple Iron Dagger", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 2, "affects_quality": True},
            {"skill_name": "Weaponsmithing", "level": 1, "affects_quality": True}
        ]
    },
    {
        "name": "Forge Steel Longsword",
        "description": "A well-balanced steel longsword suitable for serious combat. The standard weapon of many professional soldiers.",
        "recipe_category": "Blacksmithing - Weapons (Advanced)",
        "crafting_time_seconds": 3600,
        "required_station_type": "Forge",
        "difficulty_level": 4,
        "is_discoverable": True,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 80}, {"skill_name": "Weaponsmithing", "amount": 100}],
        "quality_range": {"min": 2, "max": 5},
        "ingredients": [
            {"item_id": "Steel Ingot", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Sturdy Ash Wood Haft", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Standard Quenching Oil", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Steel Longsword", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 3, "affects_quality": True},
            {"skill_name": "Weaponsmithing", "level": 3, "affects_quality": True}
        ]
    },
    # Armor
    {
        "name": "Forge Iron Breastplate",
        "description": "A solid iron breastplate that offers good protection against slashing attacks. Heavy but reliable.",
        "recipe_category": "Blacksmithing - Armor (Medium)",
        "crafting_time_seconds": 4800,
        "required_station_type": "Forge",
        "difficulty_level": 3,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 60}, {"skill_name": "Armorsmithing", "amount": 80}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 4.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Iron Breastplate", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 2, "affects_quality": True},
            {"skill_name": "Armorsmithing", "level": 2, "affects_quality": True}
        ]
    }
]

# Alchemy & Potion Brewing Recipes
ALCHEMY_RECIPES = [
    # Basic Potions
    {
        "name": "Brew Minor Healing Potion",
        "description": "A simple healing potion that accelerates natural recovery for a short time. Commonly used for minor injuries.",
        "recipe_category": "Alchemy - Healing",
        "crafting_time_seconds": 900,
        "required_station_type": "Alchemy Lab",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Alchemy", "amount": 30}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Sunpetal Leaf", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Purified Alchemical Salt", "quantity": 0.5, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Minor Healing Potion", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 1, "affects_quality": True}
        ]
    },
    {
        "name": "Brew Mana Regeneration Tonic",
        "description": "A pleasant-tasting tonic that gently stimulates mana regeneration. Favored by mages for extended study sessions.",
        "recipe_category": "Alchemy - Mana",
        "crafting_time_seconds": 1200,
        "required_station_type": "Alchemy Lab",
        "difficulty_level": 3,
        "is_discoverable": True,
        "experience_gained": [{"skill_name": "Alchemy", "amount": 45}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Mooncluster Berries", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Purified Alchemical Salt", "quantity": 0.5, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Mana Regeneration Tonic", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 2, "affects_quality": True}
        ]
    },
    # Poisons & Combat Substances
    {
        "name": "Distill Weak Paralytic Poison",
        "description": "A mild paralytic agent that can slow an opponent's movements temporarily. Often used by hunters and trappers.",
        "recipe_category": "Alchemy - Poisons",
        "crafting_time_seconds": 1800,
        "required_station_type": "Alchemy Lab",
        "difficulty_level": 3,
        "is_discoverable": True,
        "experience_gained": [{"skill_name": "Alchemy", "amount": 50}, {"skill_name": "Poison Craft", "amount": 40}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Giant Spider Venom Gland", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Purified Alchemical Salt", "quantity": 0.5, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Weak Paralytic Poison", "quantity": 2.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 2, "affects_quality": True},
            {"skill_name": "Poison Craft", "level": 1, "affects_quality": True}
        ]
    }
]

# Woodworking & Carpentry Recipes
WOODWORKING_RECIPES = [
    # Lumber Processing
    {
        "name": "Mill Pine Planks",
        "description": "Process raw pine logs into usable planks for construction and crafting.",
        "recipe_category": "Woodworking - Lumber Processing",
        "crafting_time_seconds": 900,
        "required_station_type": "Sawmill",
        "difficulty_level": 1,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Woodworking", "amount": 20}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Pine Log (Rough Cut)", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Pine Planks (Bundle of 5)", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Woodworking", "level": 1, "affects_quality": True}
        ]
    },
    # Basic Furniture & Containers
    {
        "name": "Craft Simple Wooden Crate",
        "description": "A roughly constructed pine crate, suitable for storing or transporting common goods. Not very secure, but cheap and easy to make.",
        "recipe_category": "Woodworking - Container (Small)",
        "crafting_time_seconds": 900,
        "required_station_type": "Carpenter's Workbench",
        "difficulty_level": 1,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Woodworking", "amount": 20}, {"skill_name": "Carpentry", "amount": 15}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Pine Planks (Bundle of 5)", "quantity": 0.4, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Simple Wooden Crate", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Carpentry", "level": 1, "affects_quality": True}
        ]
    },
    {
        "name": "Craft Oak Dining Table",
        "description": "A sturdy oak dining table that can seat six people comfortably. Built to last generations with proper care.",
        "recipe_category": "Woodworking - Furniture",
        "crafting_time_seconds": 3600,
        "required_station_type": "Carpenter's Workbench",
        "difficulty_level": 3,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Woodworking", "amount": 60}, {"skill_name": "Carpentry", "amount": 80}, {"skill_name": "Furniture Making", "amount": 100}],
        "quality_range": {"min": 1, "max": 5},
        "ingredients": [
            {"item_id": "Oak Planks", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Oak Dining Table", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Carpentry", "level": 3, "affects_quality": True},
            {"skill_name": "Furniture Making", "level": 2, "affects_quality": True}
        ]
    }
]

# Tailoring & Leatherworking Recipes
TAILORING_RECIPES = [
    # Tanning & Processing
    {
        "name": "Tan Buckskin Leather",
        "description": "Process raw deer hide into soft, flexible buckskin leather using traditional tanning techniques.",
        "recipe_category": "Leatherworking - Tanning",
        "crafting_time_seconds": 3600,
        "required_station_type": "Tanning Rack",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Leatherworking", "amount": 30}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Raw Deer Hide (Medium)", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Buckskin Leather (Medium Piece)", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Leatherworking", "level": 1, "affects_quality": True}
        ]
    },
    # Basic Accessories
    {
        "name": "Craft Simple Leather Pouch",
        "description": "A small leather pouch with a drawstring closure, useful for carrying coins, herbs, or small items.",
        "recipe_category": "Leatherworking - Accessories (Basic)",
        "crafting_time_seconds": 900,
        "required_station_type": "Leatherworking Table",
        "difficulty_level": 1,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Leatherworking", "amount": 15}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Buckskin Leather (Medium Piece)", "quantity": 0.2, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Simple Leather Pouch", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Leatherworking", "level": 1, "affects_quality": True}
        ]
    },
    # Clothing
    {
        "name": "Tailor Common Linen Shirt",
        "description": "A basic linen shirt suitable for everyday wear. Nothing fancy, but durable and comfortable after breaking in.",
        "recipe_category": "Tailoring - Clothing (Basic)",
        "crafting_time_seconds": 1800,
        "required_station_type": "Tailor's Workbench",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Tailoring", "amount": 25}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Roughspun Linen Bolt (10m)", "quantity": 0.3, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Common Linen Shirt", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Tailoring", "level": 1, "affects_quality": True}
        ]
    }
]

# Jewelcrafting & Gemcutting Recipes
JEWELCRAFTING_RECIPES = [
    # Gem Processing
    {
        "name": "Cut Quartz Cabochon",
        "description": "Shape and polish a rough quartz crystal into a smooth, domed cabochon suitable for jewelry setting.",
        "recipe_category": "Jewelcrafting - Gem Cutting",
        "crafting_time_seconds": 1800,
        "required_station_type": "Jeweler's Workbench",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Jewelcrafting", "amount": 25}, {"skill_name": "Gemcutting", "amount": 30}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Rough Quartz Crystal", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Clear Quartz Cabochon", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Gemcutting", "level": 1, "affects_quality": True}
        ]
    },
    # Basic Jewelry
    {
        "name": "Craft Silver Ring with Quartz",
        "description": "A simple but elegant silver ring set with a polished quartz cabochon. A popular gift or first jewelry purchase.",
        "recipe_category": "Jewelcrafting - Rings",
        "crafting_time_seconds": 2400,
        "required_station_type": "Jeweler's Workbench",
        "difficulty_level": 3,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Jewelcrafting", "amount": 40}, {"skill_name": "Silversmithing", "amount": 35}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Silver Jewelry Bar (92.5% Pure)", "quantity": 0.05, "consumed_in_crafting": True},
            {"item_id": "Clear Quartz Cabochon", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Silver Quartz Ring", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Jewelcrafting", "level": 2, "affects_quality": True},
            {"skill_name": "Silversmithing", "level": 1, "affects_quality": True}
        ]
    }
]

# Relicsmithing & Artifact Tinkering Recipes
RELICSMITHING_RECIPES = [
    # Basic Relic Components
    {
        "name": "Craft Echo-Preserving Container",
        "description": "A specialized container that prevents resonant echo shards from degrading. Essential for proper study and later use in artifact creation.",
        "recipe_category": "Relicsmithing - Containment",
        "crafting_time_seconds": 3600,
        "required_station_type": "Artificer's Workbench",
        "difficulty_level": 4,
        "is_discoverable": True,
        "experience_gained": [{"skill_name": "Relicsmithing", "amount": 75}, {"skill_name": "Containment Artifice", "amount": 60}],
        "quality_range": {"min": 2, "max": 5},
        "ingredients": [
            {"item_id": "Silver Jewelry Bar (92.5% Pure)", "quantity": 0.1, "consumed_in_crafting": True},
            {"item_id": "Elven Mana-Silk Thread (Spool)", "quantity": 0.05, "consumed_in_crafting": True},
            {"item_id": "Clear Quartz Cabochon", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Echo-Preserving Container", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Relicsmithing", "level": 3, "affects_quality": True},
            {"skill_name": "Containment Artifice", "level": 2, "affects_quality": True}
        ]
    },
    # Simple Artifacts
    {
        "name": "Craft Voice-Preserving Stone",
        "description": "A simple communication artifact that can record a short message and play it back when activated. Popular for sending secure messages.",
        "recipe_category": "Relicsmithing - Communication",
        "crafting_time_seconds": 7200,
        "required_station_type": "Artificer's Workbench",
        "difficulty_level": 5,
        "is_discoverable": True,
        "experience_gained": [{"skill_name": "Relicsmithing", "amount": 120}, {"skill_name": "Sound Artifice", "amount": 100}],
        "quality_range": {"min": 2, "max": 5},
        "ingredients": [
            {"item_id": "Resonant Echo Shard", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Clear Quartz Cabochon", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Silver Jewelry Bar (92.5% Pure)", "quantity": 0.2, "consumed_in_crafting": True},
            {"item_id": "Elven Mana-Silk Thread (Spool)", "quantity": 0.1, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Voice-Preserving Stone", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Relicsmithing", "level": 4, "affects_quality": True},
            {"skill_name": "Sound Artifice", "level": 3, "affects_quality": True}
        ]
    }
]

# Combine all recipes for easy access
ALL_RECIPES = (
    BLACKSMITHING_RECIPES +
    ALCHEMY_RECIPES +
    WOODWORKING_RECIPES +
    TAILORING_RECIPES +
    JEWELCRAFTING_RECIPES +
    RELICSMITHING_RECIPES
)