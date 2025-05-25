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
    {
        "name": "Bronze Ingot",
        "description": "An ancient and reliable alloy of copper and tin. Stronger than copper, easier to cast than iron. Used for tools, early armaments, and decorative items.",
        "recipe_category": "Alloy - Basic",
        "crafting_time_seconds": 450,
        "required_station_type": "Crucible Forge",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Metallurgy", "amount": 20}, {"skill_name": "Blacksmithing", "amount": 10}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Copper Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Tin Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Stonewake Coal Seam", "quantity": 3.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Bronze Ingot", "quantity": 2.0},
        "secondary_outputs": [
            {"item_id": "Copper-Tin Dross", "quantity": 1.0, "chance": 0.05}
        ],
        "required_skills": [
            {"skill_name": "Metallurgy", "level": 1, "affects_quality": True},
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": False}
        ],
        "custom_data": {"alloy_ratio_copper": 0.9, "alloy_ratio_tin": 0.1}
    },
    {
        "name": "Tool Steel Ingot",
        "description": "A very hard and wear-resistant steel alloy, perfect for crafting durable tools. Often includes traces of tungsten or chromium, a technique perfected by Dwarven smiths.",
        "recipe_category": "Alloy - Advanced",
        "crafting_time_seconds": 1800,
        "required_station_type": "High-Temperature Forge with Controlled Atmosphere",
        "difficulty_level": 6,
        "is_discoverable": True,
        "unlock_conditions": {"manual_read": "Dwarven Metallurgy Vol. III", "skill_name": "Metallurgy", "level": 5},
        "experience_gained": [{"skill_name": "Metallurgy", "amount": 150}, {"skill_name": "Dwarven Smithing", "amount": 50}],
        "quality_range": {"min": 4, "max": 8},
        "ingredients": [
            {"item_id": "Steel Ingot", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Chromium Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Magma-Kissed Coal", "quantity": 5.0, "consumed_in_crafting": True},
            {"item_id": "Limestone Flux", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Tungsten Ore", "quantity": 1.0, "can_be_substituted": True, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Tool Steel Ingot", "quantity": 3.0},
        "secondary_outputs": [
            {"item_id": "High-Carbon Slag", "quantity": 1.0, "chance": 0.1}
        ],
        "required_skills": [
            {"skill_name": "Metallurgy", "level": 5, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Dwarven Smithing", "level": 3, "affects_quality": True}
        ],
        "custom_data": {"key_elements": ["high_carbon", "chromium_trace", "tungsten_trace_optional"]}
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
    {
        "name": "Orcish Spine-Cleaver",
        "description": "A brutally effective cleaver favored by Orcish warriors from Rivemark and Stonewake. Designed more for intimidation and heavy chopping than finesse. Often bears clan markings.",
        "recipe_category": "Weapon - One-Handed Axe",
        "crafting_time_seconds": 900,
        "required_station_type": "Orcish War-Forge",
        "difficulty_level": 4,
        "is_discoverable": True,
        "region_specific": ["Rivemark", "Stonewake_Hammerdeep"],
        "unlock_conditions": {"skill_name": "Orcish Smithing", "level": 3, "faction_allegiance": "Any Orc Clan Friendly+"},
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 120}, {"skill_name": "Orcish Smithing", "amount": 80}],
        "quality_range": {"min": 2, "max": 5},
        "ingredients": [
            {"item_id": "Orcish Grognard Steel Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Sturdy Ash Wood Haft", "quantity": 1.0, "can_be_substituted": True, "possible_substitutes": ["Ironwood Haft", "Bone-Reinforced Grip"], "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Orcish Fury-Quench", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Orcish Spine-Cleaver", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 3, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Orcish Smithing", "level": 2, "affects_quality": True, "affects_speed": False}
        ],
        "custom_data": {"clan_marking_slot": True, "chance_to_cause_fear_on_crit": 0.05}
    },
    {
        "name": "Skarport Guild Standard Longsword",
        "description": "A well-balanced and reliable longsword crafted from Human Guildsteel. Favored by Accord peacekeepers, city guards, and traveling merchants for its versatility and ease of maintenance. Mass-produced but of consistent quality.",
        "recipe_category": "Weapon - One-Handed Sword",
        "crafting_time_seconds": 1200,
        "required_station_type": "Standard Forge with Quench Tank",
        "difficulty_level": 3,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 70}],
        "quality_range": {"min": 2, "max": 6},
        "ingredients": [
            {"item_id": "Human Guildsteel Ingot", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Standard Quenching Oil", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Skarport Guild Standard Longsword", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 2, "affects_quality": True, "affects_speed": True}
        ],
        "custom_data": {"maintenance_kit_bonus_multiplier": 1.1, "guild_stamp_slot": True}
    },
    {
        "name": "Ferverl Sun-Blessed Scimitar",
        "description": "A gracefully curved scimitar forged in the sacred desert fires of Thal-Zirad. The Ferverl Sun-Forged steel glows with an inner heat, and the blade is said to sear the spirits of the unworthy. Requires a specific ritual to complete.",
        "recipe_category": "Weapon - One-Handed Sword (Exotic)",
        "crafting_time_seconds": 10800,
        "required_station_type": "Thal-Zirad Sun Forge",
        "difficulty_level": 9,
        "is_discoverable": True,
        "unlock_conditions": {"faction_reputation": "Thal_Zirad_Ember_Veil_Honored", "quest_line_completed": "The Oracle's Trials", "skill_name": "Ferverl Metallurgy", "level": 7},
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 800}, {"skill_name": "Ferverl Metallurgy", "amount": 500}, {"skill_name": "Ritual Magic (Fire)", "amount": 200}],
        "quality_range": {"min": 6, "max": 10},
        "ingredients": [
            {"item_id": "Ferverl Sun-Forged Steel Ingot", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Gold Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Ferverl Sun-Sand Polish", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Magma-Kissed Coal", "quantity": 5.0, "consumed_in_crafting": True},
            {"item_id": "Living Flame Essence - RARE", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Ferverl Sun-Blessed Scimitar", "quantity": 1.0, "quality_modifier": 1.1},
        "secondary_outputs": [
            {"item_id": "Scorched Sunstone Fragment", "quantity": 1.0, "chance": 0.1}
        ],
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 8, "affects_quality": True, "affects_speed": False},
            {"skill_name": "Ferverl Metallurgy", "level": 6, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Ritual Magic (Fire)", "level": 5, "affects_quality": True}
        ],
        "custom_data": {"on_hit_effect": "minor_fire_damage_chance", "bonus_vs_shadow_creatures": True, "requires_attunement_by_owner": True}
    },
    {
        "name": "Elven Star-Metal Shortblade",
        "description": "A light, exquisitely balanced shortblade crafted from rare Star Metal. Elven smiths in Lethandrel sometimes forge these for scouts or duelists, valuing its natural resistance to magic and uncanny sharpness.",
        "recipe_category": "Weapon - Dagger/Shortsword",
        "crafting_time_seconds": 14400,
        "required_station_type": "Elven Celestial Forge",
        "difficulty_level": 8,
        "is_discoverable": True,
        "unlock_conditions": {"skill_name": "Elven Smithing", "level": 7, "item_possessed_for_inspiration": "Star Metal Ingot", "location_access": "Lethandrel_CanopyTiers_MasterForge"},
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 700}, {"skill_name": "Elven Smithing", "amount": 400}, {"skill_name": "Celestial Metallurgy", "amount": 100}],
        "quality_range": {"min": 6, "max": 10},
        "ingredients": [
            {"item_id": "Star Metal Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Spiritwood Heart", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Silver Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Elven Moon-Flux", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Elven Star-Metal Shortblade", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Star Metal Shavings", "quantity": 1.0, "chance": 0.5}
        ],
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 7, "affects_quality": True},
            {"skill_name": "Elven Smithing", "level": 6, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Celestial Metallurgy", "level": 4, "affects_quality": True}
        ],
        "custom_data": {"innate_magic_resistance_value": 15, "critical_hit_chance_modifier": 0.05, "weight_modifier": 0.8, "glows_faintly_under_starlight": True}
    },
    {
        "name": "Steel Bodkin Arrowheads (Bundle of 20)",
        "description": "A bundle of sharp, armor-piercing steel bodkin arrowheads. Standard ammunition for hunters and archers.",
        "recipe_category": "Ammunition - Arrowhead",
        "crafting_time_seconds": 600,
        "required_station_type": "Basic Forge",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 20}, {"skill_name": "Fletching", "amount": 10}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Steel Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Stonewake Coal Seam", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Steel Bodkin Arrowhead", "quantity": 20.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"armor_penetration_modifier_base": 1.1, "bundle_size": 20}
    },
    # Tools & Equipment
    {
        "name": "Basic Field Repair Kit",
        "description": "A simple kit containing a few essential tools and materials for minor repairs to weapons and armor in the field. Not as effective as a proper forge, but better than nothing.",
        "recipe_category": "Tool - Repair",
        "crafting_time_seconds": 300,
        "required_station_type": "Tinker's Workbench",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Tinkering", "amount": 30}, {"skill_name": "Blacksmithing", "amount": 10}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Sturdy Ash Wood Haft", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Basic Whetstone", "quantity": 1.0, "consumed_in_crafting": False}
        ],
        "primary_output": {"item_id": "Basic Field Repair Kit", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Tinkering", "level": 1, "affects_quality": True},
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": False}
        ],
        "custom_data": {"repair_potency_percentage": 15, "number_of_uses": 3}
    },
    {
        "name": "Masterwork Smithing Hammer",
        "description": "A perfectly balanced smithing hammer, crafted by a master for a master. Using this hammer improves the quality of crafted items and slightly reduces crafting time for metal goods.",
        "recipe_category": "Tool - Smithing",
        "crafting_time_seconds": 21600,
        "required_station_type": "Master Forge with Precision Tools",
        "difficulty_level": 9,
        "is_discoverable": True,
        "unlock_conditions": {"skill_name": "Blacksmithing", "level": 10, "items_crafted_of_epic_quality_or_higher": 5, "self_realization_quest": "The Heart of the Forge"},
        "experience_gained": [{"skill_name": "Tool Crafting", "amount": 1000}, {"skill_name": "Blacksmithing", "amount": 500}],
        "quality_range": {"min": 8, "max": 10},
        "ingredients": [
            {"item_id": "Dwarven Steel Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Star Metal Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Ironwood Haft - Master Grade", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Dwarven Oath-Sand", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Artisan's Own Sweat & Tears", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Masterwork Smithing Hammer", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 9, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Tool Crafting", "level": 7, "affects_quality": True}
        ],
        "custom_data": {"crafting_quality_bonus_modifier": 0.1, "crafting_speed_bonus_modifier": 0.05, "tool_durability": "extremely_high", "attunement_to_user": True}
    },
    {
        "name": "Dwarven Smithing Tongs (Set of 3 - Flat, Round, Pick-up)",
        "description": "A set of sturdy, reliable smithing tongs crafted in the Dwarven style. Essential for handling hot metal safely and precisely. This set includes flat-jaw, round-jaw, and pick-up tongs.",
        "recipe_category": "Tool - Smithing Accessory",
        "crafting_time_seconds": 2700,
        "required_station_type": "Dwarven Forge with Swage Block",
        "difficulty_level": 4,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Tool Crafting", "amount": 100}, {"skill_name": "Dwarven Smithing", "amount": 50}],
        "quality_range": {"min": 3, "max": 7},
        "ingredients": [
            {"item_id": "Steel Ingot", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Dwarven Flat-Jaw Tongs", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Dwarven Round-Jaw Tongs", "quantity": 1.0, "chance": 1.0},
            {"item_id": "Dwarven Pick-up Tongs", "quantity": 1.0, "chance": 1.0}
        ],
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 3, "affects_quality": True},
            {"skill_name": "Tool Crafting", "level": 2, "affects_quality": True},
            {"skill_name": "Dwarven Smithing", "level": 1, "affects_speed": True}
        ],
        "custom_data": {"tool_set_id": "DwarvenTongsBasic", "heat_resistance_level": "high"}
    },
    {
        "name": "Tinker's Repair Hammer",
        "description": "A small, versatile hammer with interchangeable heads (soft brass, hard steel) designed for repairing damaged metal items without a full forge. Less effective than forge repairs but highly portable.",
        "recipe_category": "Tool - Repair Accessory",
        "crafting_time_seconds": 1200,
        "required_station_type": "Tinker's Workbench",
        "difficulty_level": 3,
        "is_discoverable": True,
        "unlock_conditions": {"skill_name": "Tinkering", "level": 3, "manual_read": "Field Maintenance and You"},
        "experience_gained": [{"skill_name": "Tool Crafting", "amount": 80}, {"skill_name": "Tinkering", "amount": 40}],
        "quality_range": {"min": 2, "max": 5},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Copper Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Sturdy Ash Wood Haft", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Tinker's Repair Hammer", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Tool Crafting", "level": 2, "affects_quality": True},
            {"skill_name": "Tinkering", "level": 2, "affects_quality": True}
        ],
        "custom_data": {"repair_efficiency_modifier": 0.25, "tool_durability_uses": 50, "interchangeable_heads_included": ["brass_soft", "steel_hard"]}
    },
    {
        "name": "Farmer's Iron Hoe Head",
        "description": "The durable iron head for a farmer's hoe, designed for tilling soil in places like Rivemark or the Verdant Frontier. Requires a wooden haft to be functional.",
        "recipe_category": "Tool Component - Agricultural",
        "crafting_time_seconds": 900,
        "required_station_type": "Basic Forge",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 30}, {"skill_name": "Tool Crafting", "amount": 15}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Stonewake Coal Seam", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Farmer's Iron Hoe Head", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"haft_socket_type": "standard_tapered", "edge_requires_sharpening": True}
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
    },
    {
        "name": "Dwarven Oathkeeper's Shield",
        "description": "A shield of legendary Dwarven steel, often passed down through generations or forged for those who have taken solemn oaths. Its construction emphasizes absolute defense and resilience. Features a central boss suitable for a clan emblem.",
        "recipe_category": "Armor - Shield",
        "crafting_time_seconds": 5400,
        "required_station_type": "Dwarven Ancestral Forge",
        "difficulty_level": 7,
        "is_discoverable": True,
        "unlock_conditions": {"quest_completed": "The Honor of the Forge", "item_in_inventory": "Dwarven Master Smith's Hammer Token", "skill_name": "Dwarven Smithing", "level": 7},
        "experience_gained": [{"skill_name": "Armorsmithing", "amount": 500}, {"skill_name": "Dwarven Smithing", "amount": 300}],
        "quality_range": {"min": 5, "max": 9},
        "ingredients": [
            {"item_id": "Dwarven Steel Ingot", "quantity": 4.0, "consumed_in_crafting": True},
            {"item_id": "Deep Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Dwarven Rune-Etched Clasp", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Dwarven Oath-Sand", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Dwarven Oathkeeper's Shield", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Armorsmithing", "level": 6, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Dwarven Smithing", "level": 5, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Runescribing (Basic)", "level": 2, "affects_quality": False, "affects_speed": False}
        ],
        "custom_data": {"emblem_slot": True, "knockback_resistance_modifier": 1.2}
    },
    {
        "name": "Dwarven Heavy Iron Shield",
        "description": "A solid, no-nonsense shield crafted from thick iron plates. Favored by Dwarven tunnel guards and those expecting a tough fight. Heavier than steel but cheaper to produce.",
        "recipe_category": "Armor - Shield",
        "crafting_time_seconds": 3600,
        "required_station_type": "Basic Forge with Anvil",
        "difficulty_level": 3,
        "is_discoverable": False,
        "region_specific": ["Stonewake", "Dwarven_Outposts"],
        "unlock_conditions": {"race": "Dwarf", "skill_name": "Blacksmithing", "level": 2},
        "experience_gained": [{"skill_name": "Armorsmithing", "amount": 90}, {"skill_name": "Dwarven Smithing", "amount": 30}],
        "quality_range": {"min": 2, "max": 5},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 5.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Sturdy Ash Wood Haft", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Dwarven Heavy Iron Shield", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Armorsmithing", "level": 2, "affects_quality": True},
            {"skill_name": "Dwarven Smithing", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"block_solidity_modifier": 1.1, "weight_penalty_modifier": 1.15}
    },
    {
        "name": "Footman's Steel Cuirass",
        "description": "The standard steel cuirass issued to human footmen in cities like Skarport and Rivemark. Offers good protection against common threats. Part of a matching set.",
        "recipe_category": "Armor - Heavy Chest",
        "crafting_time_seconds": 7200,
        "required_station_type": "Armorer's Forge",
        "difficulty_level": 5,
        "is_discoverable": True,
        "unlock_conditions": {"guild_membership": "Skarport_Artisans_Guild_Smithing_Chapter", "manual_read": "Accord_Standard_Armor_Patterns_Vol1"},
        "experience_gained": [{"skill_name": "Armorsmithing", "amount": 250}],
        "quality_range": {"min": 3, "max": 7},
        "ingredients": [
            {"item_id": "Steel Ingot", "quantity": 6.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 4.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Limestone Flux", "quantity": 2.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Footman's Steel Cuirass", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Armorsmithing", "level": 4, "affects_quality": True, "affects_speed": True},
            {"skill_name": "Human Smithing Traditions", "level": 2, "affects_quality": True}
        ],
        "custom_data": {"set_bonus_id": "FootmansArmorSet", "repair_ease_modifier": 1.2, "weight_class": "medium_heavy"}
    },
    {
        "name": "Orcish Gut-Puncher Gauntlets",
        "description": "Heavy steel gauntlets reinforced with brutal spikes, favored by Orcish brawlers. More of a weapon than simple hand protection.",
        "recipe_category": "Armor - Heavy Gloves / Weapon - Fist",
        "crafting_time_seconds": 3200,
        "required_station_type": "Orcish War-Forge",
        "difficulty_level": 5,
        "is_discoverable": True,
        "unlock_conditions": {"faction_allegiance": "Any Orc Clan Respected+", "witnessed_in_use_by_orc_champion": True},
        "experience_gained": [{"skill_name": "Armorsmithing", "amount": 120}, {"skill_name": "Orcish Smithing", "amount": 90}, {"skill_name": "Weapon Crafting (Fist)", "amount": 50}],
        "quality_range": {"min": 3, "max": 6},
        "ingredients": [
            {"item_id": "Orcish Grognard Steel Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Hardened Leather Strips", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Steel Shavings", "quantity": 2.0, "can_be_substituted": True, "possible_substitutes": ["Broken Weapon Fragments"], "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Orcish Gut-Puncher Gauntlets - Pair", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Armorsmithing", "level": 4, "affects_quality": True},
            {"skill_name": "Orcish Smithing", "level": 3, "affects_quality": True, "affects_speed": True}
        ],
        "custom_data": {"damage_type": "piercing_bludgeoning", "unarmed_damage_bonus": "1d6", "intimidation_on_equip": True}
    },
    # Household & Utility Items
    {
        "name": "Sturdy Iron Cooking Pot",
        "description": "A heavy iron cooking pot, essential for any hearth or campfire. Known for its even heat distribution and durability. A common sight in kitchens across all cultures.",
        "recipe_category": "Household - Cookware",
        "crafting_time_seconds": 1800,
        "required_station_type": "Basic Forge with Hammering Stump",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 40}, {"skill_name": "Household Crafting", "amount": 20}],
        "quality_range": {"min": 1, "max": 5},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Iron Cauldron Shell", "quantity": 1.0, "can_be_substituted": True, "possible_substitutes": ["Sheet Iron Plates"], "consumed_in_crafting": True},
            {"item_id": "Steel Rivets & Fittings", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Sturdy Iron Cooking Pot", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": True},
            {"skill_name": "Sheet Metal Working", "level": 1, "affects_speed": True}
        ],
        "custom_data": {"capacity_liters": 5, "heat_retention_modifier": 1.1, "can_be_seasoned_for_non_stick": True}
    },
    {
        "name": "Simple Pewter Tankard",
        "description": "A plain but sturdy tankard made from pewter. Common in taverns and homes for serving drinks. Can be easily dented but also easily repaired.",
        "recipe_category": "Household - Tableware",
        "crafting_time_seconds": 600,
        "required_station_type": "Tinker's Bench with Casting Molds",
        "difficulty_level": 1,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Soft Metal Casting", "amount": 20}, {"skill_name": "Tinkering", "amount": 10}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Pewter Ingot", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Basic Casting Mold - Tankard Shape", "quantity": 1.0, "consumed_in_crafting": False}
        ],
        "primary_output": {"item_id": "Simple Pewter Tankard", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Soft Metal Casting", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"volume_ml": 500, "can_be_engraved": True}
    },
    {
        "name": "Iron Nails (Bag of 100)",
        "description": "A bag containing one hundred standard iron nails. Essential for carpentry, construction, and various repairs.",
        "recipe_category": "Component - Construction",
        "crafting_time_seconds": 300,
        "required_station_type": "Nail Header Anvil",
        "difficulty_level": 1,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 10}, {"skill_name": "Mass Production Techniques", "amount": 5}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Iron Nails (Bag of 100)", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"nail_type": "common_construction", "average_length_cm": 5}
    },
    {
        "name": "Decorative Iron Wall Sconce",
        "description": "An artistically twisted iron wall sconce designed to hold a candle or small lantern. Adds a touch of rustic elegance to any room. Popular in Human and Dwarven dwellings.",
        "recipe_category": "Household - Lighting Fixture",
        "crafting_time_seconds": 2400,
        "required_station_type": "Artisan's Forge with Scrollwork Tools",
        "difficulty_level": 4,
        "is_discoverable": True,
        "unlock_conditions": {"inspiration_from_seeing_similar_item": True, "skill_name": "Decorative Smithing", "level": 3},
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 80}, {"skill_name": "Decorative Smithing", "amount": 120}],
        "quality_range": {"min": 2, "max": 7},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Beeswax or Tallow", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Fine Steel Wire", "quantity": 1.0, "can_be_substituted": True, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Decorative Iron Wall Sconce", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 3, "affects_quality": True},
            {"skill_name": "Decorative Smithing", "level": 2, "affects_quality": True, "affects_speed": True}
        ],
        "custom_data": {"style": "rustic_scrollwork", "holds_item_type": ["candle", "small_lantern"], "wall_mountable": True}
    },
    {
        "name": "Standard Iron Horseshoes (Set of 4)",
        "description": "A set of four durable iron horseshoes, essential for any mounted travel or labor. Requires skill to fit properly to a horse.",
        "recipe_category": "Tool - Farriery",
        "crafting_time_seconds": 1500,
        "required_station_type": "Farrier's Forge",
        "difficulty_level": 3,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Blacksmithing", "amount": 50}, {"skill_name": "Farriery", "amount": 70}],
        "quality_range": {"min": 2, "max": 6},
        "ingredients": [
            {"item_id": "Iron Ingot", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Stonewake Coal Seam", "quantity": 3.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Standard Iron Horseshoe", "quantity": 4.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 2, "affects_quality": True},
            {"skill_name": "Farriery", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"horse_size_suitability": ["medium", "large"], "includes_nail_holes": True}
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
    },
    # Additional Basic Potions
    {
        "name": "Minor Healing Draught",
        "description": "A common herbal brew that mends minor wounds and restores a small amount of vitality. A staple for any adventurer.",
        "recipe_category": "Potion - Healing",
        "crafting_time_seconds": 120,
        "required_station_type": "Apothecary's Bench",
        "difficulty_level": 1,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Alchemy", "amount": 20}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Sunpetal Leaf", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Filtered River Water", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Glass Vial - Basic", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Minor Healing Draught", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"healing_amount_base": 10, "healing_per_quality_point": 5, "taste": "slightly_bitter_sweet"}
    },
    {
        "name": "Weak Mana Potion",
        "description": "A shimmering blue potion that restores a small amount of magical energy. Favored by novice mages and scholars.",
        "recipe_category": "Potion - Mana Restoration",
        "crafting_time_seconds": 180,
        "required_station_type": "Apothecary's Bench",
        "difficulty_level": 2,
        "is_discoverable": False,
        "experience_gained": [{"skill_name": "Alchemy", "amount": 30}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Mooncluster Berries", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Purified Leyline Water", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Ground Moonstone - trace", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Glass Vial - Basic", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Weak Mana Potion", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"mana_restored_base": 15, "mana_per_quality_point": 7, "glows_faintly": True}
    },
    {
        "name": "Potion of Minor Fortitude",
        "description": "An earthy brew that temporarily increases physical resilience, allowing one to endure more punishment. Often smells of damp soil and iron.",
        "recipe_category": "Potion - Buff (Defense)",
        "crafting_time_seconds": 240,
        "required_station_type": "Dwarven Alchemical Still",
        "difficulty_level": 3,
        "is_discoverable": True,
        "unlock_conditions": {"manual_read": "Dwarven Brews and Tonics", "skill_name": "Alchemy", "level": 2},
        "experience_gained": [{"skill_name": "Alchemy", "amount": 50}, {"skill_name": "Dwarven Lore", "amount": 10}],
        "quality_range": {"min": 2, "max": 4},
        "ingredients": [
            {"item_id": "Crystal Highlands Wort", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Dwarven Spring Water", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Iron Shavings - trace", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Clay Flask", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Potion of Minor Fortitude", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 2, "affects_quality": True},
            {"skill_name": "Herbalism", "level": 1, "affects_quality": False}
        ],
        "custom_data": {"defense_bonus_percentage": 5, "defense_bonus_per_quality": 2, "duration_seconds": 300, "taste": "metallic_earthy"}
    },
    # Advanced Potions & Elixirs
    {
        "name": "Elixir of Elven Sight",
        "description": "An elven elixir that temporarily grants enhanced perception, allowing the imbiber to see subtle magical auras, hidden details, and traces of recent passage. A closely guarded Lethandrel formula.",
        "recipe_category": "Elixir - Sensory Enhancement",
        "crafting_time_seconds": 1800,
        "required_station_type": "Elven Moonstill Altar",
        "difficulty_level": 7,
        "is_discoverable": True,
        "unlock_conditions": {"item_id_known": "Ancient Elven Scroll Fragment - Vision Rites", "skill_name": "Elven Alchemy", "level": 5, "location_specific_ritual": "Lethandrel_Leyroot_Grove_Moon_Phase_New"},
        "experience_gained": [{"skill_name": "Alchemy", "amount": 400}, {"skill_name": "Elven Lore", "amount": 100}, {"skill_name": "Ritual Magic (Moon)", "amount": 50}],
        "quality_range": {"min": 4, "max": 8},
        "ingredients": [
            {"item_id": "Spirit Fox Saliva", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Lethandrel Moon-Dew", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Ground Moonstone", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Silver Inlay Crystal Vial - Crafted", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Elixir of Elven Sight", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Blurred Vision Dust", "quantity": 1.0, "chance": 0.05}
        ],
        "required_skills": [
            {"skill_name": "Alchemy", "level": 6, "affects_quality": True, "affects_speed": False},
            {"skill_name": "Elven Alchemy", "level": 4, "affects_quality": True},
            {"skill_name": "Ritual Magic (Moon)", "level": 3, "affects_quality": True}
        ],
        "custom_data": {"effects": ["see_magical_auras", "detect_hidden_objects_chance", "see_recent_tracks"], "duration_base_seconds": 600, "duration_per_quality": 120, "side_effect": "mild_headache_after_0.1"}
    },
    {
        "name": "Ferverl Ash-Bound Resilience Tincture",
        "description": "A potent, dark tincture developed by Ferverl survivors. Grants significant resistance to environmental hazards like extreme heat, toxins, or magical corruption for a short period. Tastes of ash and determination.",
        "recipe_category": "Tincture - Environmental Resistance",
        "crafting_time_seconds": 3600,
        "required_station_type": "Ferverl Ritual Brazier & Alembic",
        "difficulty_level": 8,
        "is_discoverable": True,
        "unlock_conditions": {"faction_reputation": "Ferverl_Clans_Respected", "quest_completed": "The Emberflow Trials", "skill_name": "Ferverl Alchemy", "level": 6},
        "experience_gained": [{"skill_name": "Alchemy", "amount": 600}, {"skill_name": "Ferverl Alchemy", "amount": 300}, {"skill_name": "Survival", "amount": 100}],
        "quality_range": {"min": 5, "max": 9},
        "ingredients": [
            {"item_id": "Ferverl Blood-Ash", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Ember Wastes Bloom", "quantity": 5.0, "consumed_in_crafting": True},
            {"item_id": "Basilisk Eye (Petrified) - sliver", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Orcish Grog Base", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Obsidian Flask - Crafted", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Ferverl Ash-Bound Resilience Tincture", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Inert Ash Clump", "quantity": 1.0, "chance": 0.1}
        ],
        "required_skills": [
            {"skill_name": "Alchemy", "level": 7, "affects_quality": True},
            {"skill_name": "Ferverl Alchemy", "level": 5, "affects_quality": True, "affects_speed": False},
            {"skill_name": "Ritualism (Ferverl)", "level": 4, "affects_quality": True}
        ],
        "custom_data": {"resistances_granted": ["fire_medium", "poison_medium", "corruption_low"], "duration_seconds_base": 180, "duration_per_quality": 60, "side_effect": "temporary_numbness_0.05"}
    },
    {
        "name": "Potion of Shadow Blending",
        "description": "This murky potion, when consumed, allows the user to blend more effectively with shadows, making them harder to detect for a limited time. Smells faintly of damp earth and night.",
        "recipe_category": "Potion - Stealth/Illusion",
        "crafting_time_seconds": 900,
        "required_station_type": "Shrouded Alchemical Table",
        "difficulty_level": 5,
        "is_discoverable": True,
        "unlock_conditions": {"manual_found": "Thief's Compendium - Chapter on Evasion", "skill_name": "Alchemy", "level": 4},
        "experience_gained": [{"skill_name": "Alchemy", "amount": 150}, {"skill_name": "Stealth Lore", "amount": 30}],
        "quality_range": {"min": 3, "max": 6},
        "ingredients": [
            {"item_id": "Shimmering Marsh Cap", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Shadow Panther Hide Oil", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Lethandrel Moon-Dew", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Darkened Glass Vial", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Potion of Shadow Blending", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 4, "affects_quality": True},
            {"skill_name": "Herbalism (Fungi)", "level": 3, "affects_quality": True}
        ],
        "custom_data": {"stealth_bonus_modifier": 0.15, "stealth_bonus_per_quality": 0.05, "duration_seconds_base": 120, "duration_per_quality": 30, "visual_effect": "user_appears_dimmer_in_shadows"}
    },
    # Alchemical Components & Bases
    {
        "name": "Universal Solvent Base (Weak)",
        "description": "A basic alchemical solvent created by carefully neutralizing common acids and bases. Can dissolve a wider range of materials than simple water, but is not particularly potent.",
        "recipe_category": "Alchemical Component - Solvent",
        "crafting_time_seconds": 600,
        "required_station_type": "Glassware & Distillation Setup",
        "difficulty_level": 3,
        "is_discoverable": True,
        "unlock_conditions": {"textbook_studied": "Fundamentals of Alchemical Reactions", "skill_name": "Basic Chemistry", "level": 2},
        "experience_gained": [{"skill_name": "Alchemy", "amount": 40}, {"skill_name": "Basic Chemistry", "amount": 20}],
        "quality_range": {"min": 1, "max": 3},
        "ingredients": [
            {"item_id": "Sulfur Powder", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Forge Ash", "quantity": 2.0, "consumed_in_crafting": True},
            {"item_id": "Filtered River Water", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Rock Salt Chunks", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Large Glass Beaker", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Universal Solvent Base (Weak)", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Impure Salt Precipitate", "quantity": 1.0, "chance": 0.1}
        ],
        "required_skills": [
            {"skill_name": "Alchemy", "level": 2, "affects_quality": True},
            {"skill_name": "Basic Chemistry", "level": 1, "affects_quality": True}
        ],
        "custom_data": {"solvent_power_rating": 3, "neutral_ph": True, "shelf_life_days": 30}
    },
    {
        "name": "Beastfolk Totemic Catalyst",
        "description": "A potent alchemical catalyst prepared by Ashkar Vale shamans. It's made from a blend of animal parts, sacred herbs, and spirit-infused water, designed to empower nature-aspected potions and rituals.",
        "recipe_category": "Alchemical Component - Catalyst",
        "crafting_time_seconds": 7200,
        "required_station_type": "Ashkar Vale Spirit Circle with Offering Bowl",
        "difficulty_level": 7,
        "is_discoverable": True,
        "unlock_conditions": {"tribal_favor": "Ashkar_Vale_Shamans_Friendly", "vision_quest_completed": "The Whispering Wilds", "skill_name": "Beastfolk Shamanism", "level": 5},
        "experience_gained": [{"skill_name": "Alchemy", "amount": 300}, {"skill_name": "Beastfolk Shamanism", "amount": 200}, {"skill_name": "Ritualism (Nature)", "amount": 100}],
        "quality_range": {"min": 4, "max": 8},
        "ingredients": [
            {"item_id": "Spirit Fox Saliva", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Griffin Feather (Down)", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Verdant Vine Extract", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Ashkar Vale Spirit-Water", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Carved Bone Fetish", "quantity": 1.0, "consumed_in_crafting": False}
        ],
        "primary_output": {"item_id": "Beastfolk Totemic Catalyst", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Alchemy", "level": 5, "affects_quality": True},
            {"skill_name": "Beastfolk Shamanism", "level": 4, "affects_quality": True},
            {"skill_name": "Ritualism (Nature)", "level": 3, "affects_quality": True}
        ],
        "custom_data": {"catalyst_effect": "doubles_potency_nature_potions_reduces_brewing_time_by_25_percent", "charges": 3, "revered_by_beastfolk": True}
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
    },
    # Dangerous Relic Procedures
    {
        "name": "Procedure: Stabilize Minor War-Core Fragment",
        "description": "A risky procedure to temporarily stabilize a small fragment of a Crimson Dissonance War-Core, reducing its ambient corruption and allowing for safer study or use as a very short-term power source.",
        "recipe_category": "Relic Stabilization - Power Core",
        "crafting_time_seconds": 7200,
        "required_station_type": "Relic Containment Workbench with Nullifier Array",
        "difficulty_level": 8,
        "is_discoverable": True,
        "unlock_conditions": {"research_notes_found": "Fragmented_Dissonance_Core_Studies_Crucible_Spire", "skill_name": "Relic Tinkering", "level": 5, "tool_possessed": "Accord-Standard Nullifier Rod"},
        "experience_gained": [{"skill_name": "Relic Tinkering", "amount": 1000}, {"skill_name": "Dissonance Lore", "amount": 200}, {"skill_name": "Hazardous Material Handling", "amount": 100}],
        "quality_range": {"min": 1, "max": 4},
        "ingredients": [
            {"item_id": "Shattered War-Core Fragment", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Accord-Standard Nullifier Rod", "quantity": 1.0, "consumed_in_crafting": False},
            {"item_id": "Inert Clay (Mana Absorptive)", "quantity": 5.0, "consumed_in_crafting": True},
            {"item_id": "Quenched Quicksilver Solution", "quantity": 1.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Stabilized Minor War-Core Fragment", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Highly Corrupted Dross", "quantity": 1.0, "chance": 0.3},
            {"item_id": "Empty Containment Vessel", "quantity": 1.0, "chance": 0.1}
        ],
        "required_skills": [
            {"skill_name": "Relic Tinkering", "level": 7, "affects_quality": True, "affects_speed": False},
            {"skill_name": "Energy Systems (Relic)", "level": 5, "affects_quality": True},
            {"skill_name": "Hazardous Material Handling", "level": 3, "affects_quality": False}
        ],
        "custom_data": {
            "failure_consequences_critical": "Mana_explosion_corruption_spread_spawns_energy_wisp",
            "failure_consequences_minor": "Increased_instability_nullifier_rod_drained_minor_researcher_corruption",
            "successful_output_lifespan_hours": "quality_level_x_6"
        }
    },
    {
        "name": "Blueprint: Repurpose Sentinel Plating for Shield Core",
        "description": "A complex blueprint detailing how to integrate a segment of Dissonance-era Sentinel Plating into the core of a modern shield, hoping to impart some of its legendary resilience and energy dampening.",
        "recipe_category": "Relic Repurposing - Armor Enhancement",
        "crafting_time_seconds": 10800,
        "required_station_type": "Master Armorer's Forge with Relic Integration Rig",
        "difficulty_level": 7,
        "is_discoverable": True,
        "unlock_conditions": {"blueprint_acquired": "Salvaged_Accord_R&D_Notes_Stonewake_Vault", "skill_name": "Armorsmithing (Master)", "level": 8, "skill_name_2": "Relic Tinkering", "level_2": 4},
        "experience_gained": [{"skill_name": "Armorsmithing (Master)", "amount": 700}, {"skill_name": "Relic Tinkering", "amount": 300}, {"skill_name": "Material Science (Alloy)", "amount": 150}],
        "quality_range": {"min": 3, "max": 7},
        "ingredients": [
            {"item_id": "Inert Sentinel Plating Segment", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Dwarven Steel Ingot", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Silver Wire Spool (Fine)", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Elven Ward-Weave Mesh", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Multi-Spectrum Goggles", "quantity": 1.0, "consumed_in_crafting": False}
        ],
        "primary_output": {"item_id": "Sentinel-Core Shield", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Cracked Sentinel Plating & Ruined Shield Frame", "quantity": 1.0, "chance": 0.25}
        ],
        "required_skills": [
            {"skill_name": "Armorsmithing (Master)", "level": 7, "affects_quality": True},
            {"skill_name": "Relic Tinkering", "level": 6, "affects_quality": True},
            {"skill_name": "Material Science (Alloy)", "level": 4, "affects_quality": True}
        ],
        "custom_data": {
            "resulting_shield_properties": ["enhanced_physical_dr", "chance_to_dampen_specific_magic_type_if_aligned"],
            "risk_of_latent_energy_awakening": 0.05
        }
    },
    {
        "name": "Experiment: Controlled Discharge of Dissonance Echo Crystal",
        "description": "EXTREMELY DANGEROUS. An experimental attempt to trigger a controlled, minor discharge from a Dissonance Echo Crystal, hoping to capture a sliver of its trapped energy or information without causing a catastrophic release. Success is highly improbable.",
        "recipe_category": "Relic Research - Forbidden Knowledge",
        "crafting_time_seconds": 21600,
        "required_station_type": "Remote Relic Analysis Chamber (Fortified)",
        "difficulty_level": 10,
        "is_discoverable": True,
        "unlock_conditions": {"forbidden_knowledge_fragments_combined": 5, "skill_name": "Relic Tinkering (Grandmaster)", "level": 10, "will_to_risk_everything_flag": True, "containment_field_projector_available": True},
        "experience_gained": [{"skill_name": "Relic Tinkering (Grandmaster)", "amount": 5000}, {"skill_name": "Dissonance Theory (PhD)", "amount": 1000}],
        "quality_range": {"min": 0, "max": 2},
        "ingredients": [
            {"item_id": "Echo Crystal Shard (Dissonance)", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Containment Field Projector (Small)", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Ferverl Leyline Siphon", "quantity": 3.0, "consumed_in_crafting": True},
            {"item_id": "Sonic Emitter (Fine Tuned)", "quantity": 1.0, "consumed_in_crafting": False},
            {"item_id": "Researcher's Last Will and Testament", "quantity": 1.0, "consumed_in_crafting": False}
        ],
        "primary_output": {"item_id": "Fragment of Lost Dissonance Knowledge", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Unstable Temporal Essence", "quantity": 1.0, "chance": 0.02},
            {"item_id": "Zone of Complete Annihilation", "quantity": 1.0, "chance": 0.93}
        ],
        "required_skills": [
            {"skill_name": "Relic Tinkering (Grandmaster)", "level": 10, "affects_quality": True},
            {"skill_name": "Theoretical Physics (Dissonance)", "level": 8, "affects_quality": True},
            {"skill_name": "Planetary Scale Evacuation Planning", "level": 1, "affects_quality": False}
        ],
        "custom_data": {
            "catastrophic_failure_outcomes": ["reality_tear_local_area", "summon_powerful_dissonance_echo_entity", "temporal_distortion_wave", "researcher_disintegrated_or_driven_mad"],
            "success_rewards_potential": ["unique_spell_fragment", "blueprint_for_lost_tech", "glimpse_into_dissonance_event"]
        }
    },
    {
        "name": "Procedure: Attune Relic Shard to User (Minor)",
        "description": "A dangerous ritual to attempt a minor psychic and magical attunement between a user and a relatively stable, small relic shard. Success can grant minor passive bonuses or abilities, but failure can lead to corruption or backlash.",
        "recipe_category": "Relic Attunement - Personal Enhancement",
        "crafting_time_seconds": 3600,
        "required_station_type": "Attunement Circle with Warding Runes",
        "difficulty_level": 6,
        "is_discoverable": True,
        "unlock_conditions": {"study_of_ferverl_symbiosis_texts": True, "skill_name": "Relic Empathy", "level": 3, "item_to_attune_is_minor_and_semi_stable": True},
        "experience_gained": [{"skill_name": "Relic Empathy", "amount": 500}, {"skill_name": "Willpower Training", "amount": 100}],
        "quality_range": {"min": 0, "max": 3},
        "ingredients": [
            {"item_id": "Inert Sentinel Plating Fragment", "quantity": 1.0, "consumed_in_crafting": False},
            {"item_id": "User's Own Blood", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Purified Leyline Water", "quantity": 1.0, "consumed_in_crafting": True},
            {"item_id": "Thal-Zirad Sun-Dried Petals", "quantity": 3.0, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Attuned Relic Shard", "quantity": 1.0},
        "secondary_outputs": [
            {"item_id": "Corrupted Relic Shard", "quantity": 1.0, "chance": 0.3}
        ],
        "required_skills": [
            {"skill_name": "Relic Empathy", "level": 5, "affects_quality": True},
            {"skill_name": "Meditation & Focus", "level": 4, "affects_quality": True},
            {"skill_name": "Ritualism (Warding)", "level": 3, "affects_quality": False}
        ],
        "custom_data": {
            "attunement_effect_depends_on_relic_type": True,
            "corruption_points_gained_on_failure_1d6": True,
            "mental_strain_involved": True
        }
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