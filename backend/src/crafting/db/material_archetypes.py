"""
Material Archetypes for the Crafting System

This module contains comprehensive material data for seeding the database.
All material archetypes are organized by profession.
"""

from backend.src.crafting.models.pydantic_models import MaterialType, Rarity

# Blacksmithing & Armorsmithing Materials
BLACKSMITHING_MATERIALS = [
    # Ores & Raw Metals
    {
        "name": "Rusty Iron Scrap",
        "description": "Rusty pieces of iron salvaged from ruins or old equipment. Requires significant cleaning and processing before use.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 0.5,
        "weight": 0.3,
        "is_craftable": False,
        "source_tags": ["salvaged_ruins", "surface_find"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Low Quality Iron Ingot",
            "purity": 0.4,
            "yield_per_unit": 0.3,
            "notes": "Requires significant cleaning and processing."
        }
    },
    {
        "name": "Common Iron Ore",
        "description": "Unrefined iron ore commonly found in mountainous regions and hills. A staple resource for blacksmiths.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.5,
        "is_craftable": False,
        "source_tags": ["mined_stonewake", "mountain_vein", "rivemark_hills"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Iron Ingot",
            "purity": 0.7,
            "yield_per_unit": 0.5
        }
    },
    {
        "name": "Copper Ore",
        "description": "Raw copper ore with distinctive blue-green coloration. Essential for bronze production and decorative metalwork.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.4,
        "is_craftable": False,
        "source_tags": ["mined_crystal_highlands", "surface_deposit"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Copper Ingot",
            "purity": 0.8,
            "yield_per_unit": 0.6,
            "conductivity": "high"
        }
    },
    {
        "name": "Tin Ore",
        "description": "Silvery-white metal ore used primarily in alloys. Essential for bronze production.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 5,
        "weight": 0.4,
        "is_craftable": False,
        "source_tags": ["mined_dwarven_foothills", "stream_panned"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Tin Ingot",
            "purity": 0.6,
            "alloy_component": "bronze"
        }
    },
    {
        "name": "Deepvein Silver Ore",
        "description": "Lustrous silver ore mined from deep shaft mines. Prized for both decorative use and effectiveness against undead.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 0.6,
        "is_craftable": False,
        "source_tags": ["mined_dwarven_deepshafts", "anti_undead_trace", "lethandrel_trade_rare"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Silver Ingot",
            "purity": 0.85,
            "magical_conductivity": "low",
            "value_modifier_vs_undead": 1.1
        }
    },
    {
        "name": "Stonewake Coal Seam",
        "description": "Coal from the Stonewake region, a vital fuel source for forges and industry.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["mined_stonewake_caldera", "fuel_source", "industrial_grade"],
        "illicit_in_regions": [],
        "properties": {
            "fuel_value": 15,
            "smoke_level": "medium",
            "ash_content": "high"
        }
    },
    {
        "name": "Orcish Blood Iron Ore",
        "description": "A mysterious ore mined in sacred orcish sites. Contains trace elements that give it unique properties when forged with traditional orcish methods.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.RARE,
        "base_value": 40,
        "weight": 0.7,
        "is_craftable": False,
        "source_tags": ["orcish_sacred_mine", "rivemark_borderlands", "ritual_harvest"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Blood Iron Ingot",
            "purity": 0.6,
            "innate_property": "minor_life_steal_weapon",
            "strength_modifier": 1.1,
            "brittleness_if_impure": "high"
        }
    },
    {
        "name": "Dwarven Deep Iron Ore",
        "description": "Rare iron ore found only in the deepest dwarven mines. Known for its exceptional hardness and magical resistance properties.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.RARE,
        "base_value": 55,
        "weight": 0.8,
        "is_craftable": False,
        "source_tags": ["dwarven_ancestral_mine", "stonewake_exclusive", "geothermal_vein"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Deep Iron Ingot",
            "purity": 0.9,
            "innate_property": "exceptional_hardness",
            "magic_resistance_armor": "low"
        }
    },
    {
        "name": "Star Metal Fragment",
        "description": "A fragment of metal from a fallen star. Extremely rare and difficult to work with, but possesses inherent magical properties.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 150,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["meteorite_fall_crystal_highlands", "celestial_origin", "rare_find"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 8,
            "malleability": 3,
            "innate_property": "starlight_glow",
            "affinity_enchantment": "air_lightning",
            "notes": "Difficult to work."
        }
    },
    {
        "name": "Ferverl Sunstone Ore",
        "description": "A gleaming ore mined in sacred desert quarries. Contains the essence of the desert sun and imparts fire properties to weapons and heat resistance to armor.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.EPIC,
        "base_value": 300,
        "weight": 0.6,
        "is_craftable": False,
        "source_tags": ["thal_zirad_sacred_quarry", "mana_charged_desert", "ritual_mined"],
        "illicit_in_regions": ["Crucible Spire"],
        "properties": {
            "smelts_into": "Sunstone Ingot",
            "purity": 0.75,
            "innate_property": "fire_damage_on_hit_weapon",
            "heat_absorption_armor": "high",
            "requires_ritual_forge": "Thal-Zirad Sun Blessing"
        }
    },
    {
        "name": "Crimsonite Ore",
        "description": "A highly volatile and corrupted ore found in areas tainted by crimson dissonance. Extremely dangerous to mine and process, but potentially immensely powerful.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.EPIC,
        "base_value": 500,
        "weight": 1.0,
        "is_craftable": False,
        "source_tags": ["dissonance_scar_ember_wastes", "volatile_leyline_deposit", "excavated_relic_site"],
        "illicit_in_regions": ["Skarport", "Lethandrel", "Stonewake_Anvilring"],
        "properties": {
            "smelts_into": "Unstable Crimsonite Ingot",
            "corruption_risk_smelting": 0.4,
            "energy_signature": "crimson_dissonance",
            "power_potential": "immense_unstable"
        }
    },
    {
        "name": "Bog Iron Ore",
        "description": "Iron ore gathered from marshy areas, often with high impurity content. Requires extensive processing but is relatively accessible.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.COMMON,
        "base_value": 1.5,
        "weight": 0.6,
        "is_craftable": False,
        "source_tags": ["shimmering_marshes_deposit", "surface_harvest", "high_impurity"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Impure Iron Ingot",
            "purity": 0.5,
            "yield_per_unit": 0.4,
            "notes": "Requires extensive purification or results in brittle metal."
        }
    },
    {
        "name": "Volcanic Obsidian Shard",
        "description": "Naturally sharp volcanic glass formed from rapidly cooled lava. Too brittle for weapons but useful for decorative inlays or razor-sharp edges.",
        "material_type": MaterialType.GEM,
        "rarity": Rarity.UNCOMMON,
        "base_value": 12,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["stonewake_caldera_cooled_lava", "sharp_edge_natural"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 6,
            "brittleness": "high",
            "can_be_knapped": True,
            "smithing_use": "decorative_inlay_or_sacrificial_blade_component"
        }
    },
    {
        "name": "Glacial Iron Ore",
        "description": "Rare iron ore found in frozen tundras. Contains traces of cryo-magic that impart cold properties to weapons forged from it.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 0.7,
        "is_craftable": False,
        "source_tags": ["frostbound_tundra_ice_vein", "cryo_infused_trace"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Frost Iron Ingot",
            "purity": 0.8,
            "innate_property": "minor_cold_damage_weapon",
            "cold_resistance_armor": "low",
            "notes": "Difficult to smelt without specialized forge."
        }
    },
    {
        "name": "Meteoric Iron Chunk",
        "description": "A large piece of celestial iron from a meteorite impact. Contains exotic metals and magical disruption properties.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 120,
        "weight": 2.0,
        "is_craftable": False,
        "source_tags": ["meteorite_impact_ember_wastes", "unrefined_celestial"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Meteoric Steel Ingot",
            "purity": 0.65,
            "innate_property": "minor_magic_disruption",
            "workability": "medium_requires_high_heat"
        }
    },
    {
        "name": "Hematite Ore",
        "description": "A common iron ore with distinctive reddish coloration when ground. Produces iron with a slight reddish tint.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.COMMON,
        "base_value": 1.8,
        "weight": 0.55,
        "is_craftable": False,
        "source_tags": ["common_sedimentary_rock", "surface_deposits_verdant_frontier"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Iron Ingot",
            "purity": 0.65,
            "yield_per_unit": 0.45,
            "color_tint": "reddish_hue_to_iron"
        }
    },
    {
        "name": "Magnetite Ore",
        "description": "Naturally magnetic iron ore that produces metal with inherent magnetic properties.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 4,
        "weight": 0.6,
        "is_craftable": False,
        "source_tags": ["igneous_rock_formations_crystal_highlands", "naturally_magnetic"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Lodestone Enriched Iron Ingot",
            "purity": 0.7,
            "yield_per_unit": 0.5,
            "innate_property": "minor_magnetic_pull_tools"
        }
    },
    {
        "name": "Nickel Ore",
        "description": "A silvery ore that, when alloyed with iron, significantly increases corrosion resistance.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.4,
        "is_craftable": False,
        "source_tags": ["laterite_deposits_ember_wastes", "alloy_component_for_steel"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Nickel Ingot",
            "purity": 0.75,
            "corrosion_resistance_enhancer": True
        }
    },
    {
        "name": "Chromium Ore",
        "description": "A rare ore used to create stainless steel and decorative platings. Provides exceptional shine and hardness.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.RARE,
        "base_value": 25,
        "weight": 0.35,
        "is_craftable": False,
        "source_tags": ["rare_vein_stonewake_mines", "stainless_steel_component"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Chromium Ingot",
            "purity": 0.8,
            "hardness_enhancer": True,
            "shine_factor": "high"
        }
    },
    {
        "name": "Cobalt Ore",
        "description": "A rare blue-tinted ore valued for its heat resistance and ability to impart vibrant blue coloration to alloys.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.RARE,
        "base_value": 30,
        "weight": 0.4,
        "is_craftable": False,
        "source_tags": ["ashkar_vale_high_altitude_mine", "blue_pigment_source", "high_strength_alloy_component"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Cobalt Ingot",
            "purity": 0.7,
            "heat_resistance_enhancer": True,
            "color_imparted": "deep_blue_to_alloys"
        }
    },
    {
        "name": "Tungsten Ore (Wolframite)",
        "description": "Extremely dense and hard metal ore that requires specialized equipment to process. Essential for creating armor-piercing weapons.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.EPIC,
        "base_value": 150,
        "weight": 0.9,
        "is_craftable": False,
        "source_tags": ["dwarven_deep_core_mining", "extremely_dense_metal_source"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Tungsten Ingot",
            "purity": 0.6,
            "melting_point": "extremely_high",
            "hardness_extreme": True,
            "notes": "Requires specialized forge and techniques."
        }
    },
    {
        "name": "Cast Iron Scrap",
        "description": "Fragments of broken cast iron items, primarily cookware and machinery parts. Can be reforged into usable metal.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 0.8,
        "weight": 0.4,
        "is_craftable": False,
        "source_tags": ["discarded_cookware", "broken_machinery_parts_skarport"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Recycled Cast Iron Ingot",
            "purity": 0.6,
            "brittleness": "high",
            "good_for_non_impact_items": True
        }
    },
    {
        "name": "Raw Lead Chunks",
        "description": "Heavy, soft metal chunks often found alongside silver deposits. Useful for weights and specialized applications.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 6,
        "weight": 0.8,
        "is_craftable": False,
        "source_tags": ["mined_alongside_silver_dwarven_mines", "soft_heavy_metal"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Lead Ingot",
            "purity": 0.9,
            "density": "very_high",
            "toxicity_warning_if_used_for_food_items": True
        }
    },
    {
        "name": "Tarnished Silver Lumps",
        "description": "Darkened silver pieces from old jewelry, cutlery, or minor treasure finds. Can be refined into usable silver.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 5,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["old_jewelry_scrap", "discarded_cutlery", "minor_treasure_finds"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Reclaimed Silver Ingot",
            "purity": 0.7,
            "requires_polishing_flux": True
        }
    },
    {
        "name": "Gold Dust",
        "description": "Fine particles of gold collected from riverbeds or salvaged from jewelry workshop sweepings. Must be accumulated to be useful.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["panned_from_rivemark_delta_sands", "jewelry_workshop_sweepings", "treasure_hoard_trace"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Gold Nugget",
            "purity": 0.95,
            "notes": "Usually requires accumulation to be useful for ingots."
        }
    },
    {
        "name": "Colored Glass Shards",
        "description": "Broken pieces of colored glass from bottles or alchemical vials. Can be melted for crude decorative inlays.",
        "material_type": MaterialType.GEM,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["broken_bottles_skarport_alleys", "discarded_alchemical_vials_lethandrel"],
        "illicit_in_regions": [],
        "properties": {
            "smithing_use": "crude_decorative_inlay_requires_melting",
            "color_variety": ["green", "brown", "clear_ish"],
            "sharpness": "low"
        }
    },
    {
        "name": "Polished River Stones",
        "description": "Smooth stones in various colors collected from riverbeds. Used as weights or decorative elements in smithing.",
        "material_type": MaterialType.GEM,
        "rarity": Rarity.COMMON,
        "base_value": 0.5,
        "weight": 0.15,
        "is_craftable": False,
        "source_tags": ["collected_rivemark_riverbeds", "smooth_varied_colors"],
        "illicit_in_regions": [],
        "properties": {
            "smithing_use": "pommel_weights_decorative_insets_non_gem_quality",
            "hardness": 4
        }
    },
    # Refined Metals (Ingots)
    {
        "name": "Low Quality Iron Ingot",
        "description": "Iron refined from scrap. Brittle and prone to rust, but usable for basic items.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.25,
        "is_craftable": True,
        "source_tags": ["smelted_scrap"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 3,
            "tensile_strength": 2,
            "rust_susceptibility": "high"
        }
    },
    {
        "name": "Iron Ingot",
        "description": "Refined iron metal, ready for smithing into tools, weapons, or armor. A fundamental material in blacksmithing.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 5,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["smelted_ore_standard"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 5,
            "tensile_strength": 4,
            "rust_susceptibility": "medium"
        }
    },
    {
        "name": "Copper Ingot",
        "description": "Refined copper with a distinctive reddish-orange color. Highly malleable and excellent conductor.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 7,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["smelted_ore_standard"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 2,
            "malleability": 8,
            "conductivity_electrical_magical": "high",
            "corrosion_resistance": "good"
        }
    },
    {
        "name": "Tin Ingot",
        "description": "Soft, silvery metal primarily used in alloys, especially bronze. Relatively low melting point makes it easy to work with.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["smelted_ore_standard"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 1,
            "malleability": 7,
            "alloy_primary_use": "bronze_production"
        }
    },
    {
        "name": "Bronze Ingot",
        "description": "An alloy of copper and tin. More durable than copper alone and historically significant for early armaments.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["alloyed_copper_tin"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 6,
            "tensile_strength": 5,
            "corrosion_resistance": "very_good",
            "historical_significance": "early_accord_armaments"
        }
    },
    {
        "name": "Steel Ingot",
        "description": "Iron alloyed with carbon for improved hardness and durability. Essential for quality weapons and armor.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 30,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["refined_iron_carbon_alloy"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 7,
            "tensile_strength": 6,
            "edge_retention": "good"
        }
    },
    {
        "name": "Silver Ingot",
        "description": "Purified silver metal, prized for its luster and effectiveness against supernatural threats like lycanthropes.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 45,
        "weight": 0.5,
        "is_craftable": True,
        "source_tags": ["smelted_ore_refined"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 3,
            "malleability": 7,
            "purity_for_enchanting": "high",
            "value_modifier_vs_lycanthropes": 1.2
        }
    },
    {
        "name": "Dwarven Steel Ingot",
        "description": "Premium steel created using secret dwarven metallurgical techniques. Lighter and stronger than standard steel.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 120,
        "weight": 0.45,
        "is_craftable": True,
        "source_tags": ["dwarven_forge_secret_alloy", "stonewake_guild_marked"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 8,
            "durability_modifier": 1.3,
            "requires_skill_handling": "Dwarven Smithing L3",
            "weight_optimized": True,
            "ancestral_quality": True
        }
    },
    {
        "name": "Orcish Grognard Steel Ingot",
        "description": "A distinctive dark steel with reddish mottling, produced by orcish smiths using traditional blood-tempering techniques.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 100,
        "weight": 0.55,
        "is_craftable": True,
        "source_tags": ["orcish_bloomery_ritual_steel", "rivemark_militia_standard", "blood_tempered_hints"],
        "illicit_in_regions": [],
        "properties": {
            "impact_resistance": 9,
            "weight_modifier": 1.15,
            "appearance": "dark_mottled_red_sheen",
            "intimidation_factor": "low",
            "requires_skill_handling": "Orcish Smithing L2"
        }
    },
    {
        "name": "Human Guildsteel Ingot",
        "description": "The standard steel alloy produced by human smiths in Skarport. Known for consistency and versatility rather than specialization.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 70,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["skarport_trade_guild_standard", "versatile_alloy"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 6,
            "tensile_strength": 6,
            "adaptability_enchantment": "medium",
            "cost_efficiency": "high",
            "mass_producible": True
        }
    },
    {
        "name": "Ferverl Sun-Forged Steel Ingot",
        "description": "Steel that's been imbued with solar essence through Ferverl desert rituals. Glows faintly with inner heat and is extremely heat resistant.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.EPIC,
        "base_value": 450,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["ferverl_desert_ritual_forge", "thal_zirad_exclusive_process", "mana_imbued"],
        "illicit_in_regions": ["Crucible Spire_unlicensed"],
        "properties": {
            "hardness": 7,
            "heat_resistance": "extreme",
            "mana_affinity": "fire_sun",
            "requires_ritual_finalizing": "Sun Blessing Attunement",
            "weight_modifier": 0.9
        }
    },
    {
        "name": "Star Metal Ingot",
        "description": "Metal refined from celestial fragments. Glows faintly and has natural magic resistance. Notoriously difficult to forge without shattering.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.EPIC,
        "base_value": 700,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["refined_star_metal_fragment", "arcane_forge_needed"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 9,
            "malleability": 2,
            "innate_magic_resistance": "high",
            "affinity_enchantment": "celestial_air",
            "glows_faintly": True,
            "shatters_if_impure_craft": True
        }
    },
    {
        "name": "Refined Crimsonite Ingot",
        "description": "A stabilized form of crimsonite, pulsing with dangerous power. Extremely rare and heavily regulated. Potentially corrupts its wielder.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.LEGENDARY,
        "base_value": 2000,
        "weight": 0.8,
        "is_craftable": True,
        "source_tags": ["stabilized_crimsonite_ore_dangerous", "relic_smithing_process"],
        "illicit_in_regions": ["ALL_ACCORD_CITIES"],
        "properties": {
            "hardness": 10,
            "power_output_weapon": "extreme",
            "corruption_wearer_chance": 0.1,
            "durability": "variable_unstable",
            "requires_containment_runes": True,
            "notes": "Extremely dangerous."
        }
    },
    {
        "name": "Impure Iron Ingot",
        "description": "Iron with high impurity content, usually from bog iron. Prone to rust and brittleness but serviceable for non-critical applications.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.5,
        "is_craftable": True,
        "source_tags": ["smelted_bog_iron"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 4,
            "tensile_strength": 3,
            "rust_susceptibility": "very_high",
            "crafting_penalty_modifier": 0.8
        }
    },
    {
        "name": "Electrum Ingot",
        "description": "A natural alloy of silver and gold with a pale yellow color. Prized by elves for decorative work and magical conductivity.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 180,
        "weight": 0.45,
        "is_craftable": True,
        "source_tags": ["alloyed_silver_gold", "skarport_luxury_trade", "elven_preference_decorative"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 4,
            "malleability": 9,
            "magical_conductivity": "medium_high",
            "value_modifier_decorative": 1.5,
            "tarnish_resistance": "good"
        }
    },
    {
        "name": "Rose Gold Ingot",
        "description": "A pink-hued gold alloy containing copper. Softer than yellow gold and particularly prized for jewelry.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 150,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["alloyed_copper_gold_silver_trace", "human_artisan_craft", "jewelry_smithing"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 3,
            "malleability": 8,
            "appearance": "lustrous_pink",
            "value_modifier_artistic": 1.3
        }
    },
    {
        "name": "Blued Steel Ingot",
        "description": "Heat-treated steel with a distinctive blue-black finish that provides excellent corrosion resistance.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 45,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["heat_treated_steel_ingot", "rust_resistant_finish"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 7,
            "tensile_strength": 6,
            "corrosion_resistance": "high",
            "appearance": "dark_blue_black_sheen"
        }
    },
    {
        "name": "Case-Hardened Iron Ingot",
        "description": "Iron with a carbon-enriched surface layer. Hard exterior but more flexible core, suitable for armor plates.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 25,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["carbon_treated_iron_surface", "rivemark_fortification_material"],
        "illicit_in_regions": [],
        "properties": {
            "surface_hardness": 8,
            "core_hardness": 4,
            "impact_resistance": "good_surface_brittle_core",
            "notes": "Good for specific armor plates, not full weapons."
        }
    },
    {
        "name": "Frost Iron Ingot",
        "description": "Metal refined from glacial iron ore. Retains a perpetual chill and can inflict cold effects when used in weapons.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 250,
        "weight": 0.65,
        "is_craftable": True,
        "source_tags": ["smelted_glacial_iron_ore", "cryo_forge_process"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 6,
            "innate_effect_weapon": "chance_of_chill_slow_on_hit",
            "innate_effect_armor": "minor_cold_aura_resistance",
            "brittleness_at_high_temp": "medium"
        }
    },
    {
        "name": "Meteoric Steel Ingot",
        "description": "An alloy incorporating meteoric iron. Has natural anti-magic properties and exceptional durability.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.EPIC,
        "base_value": 650,
        "weight": 1.8,
        "is_craftable": True,
        "source_tags": ["refined_meteoric_iron_chunk", "celestial_forge_attuned"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 8,
            "magic_disruption_field_small": True,
            "anti_magic_weapon_property": "low",
            "durability": "very_high",
            "enchantment_difficulty": "high"
        }
    },
    {
        "name": "Lodestone Enriched Iron Ingot",
        "description": "Iron with natural magnetic properties, useful for tools that need to handle small metal parts.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.55,
        "is_craftable": True,
        "source_tags": ["smelted_magnetite_ore"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 5,
            "magnetic_strength": "low",
            "tool_crafting_bonus": "easier_to_handle_small_parts"
        }
    },
    {
        "name": "Nickel Ingot",
        "description": "A silvery metal that strengthens iron and prevents rust when alloyed.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["smelted_nickel_ore"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 4,
            "malleability": 6,
            "alloy_use": "strengthens_iron_prevents_rust"
        }
    },
    {
        "name": "Chromium Ingot",
        "description": "A lustrous metal that provides extreme corrosion resistance and a bright shine when alloyed with steel.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["smelted_chromium_ore"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 8,
            "malleability": 2,
            "alloy_use": "stainless_steel_decorative_plating"
        }
    },
    {
        "name": "Cobalt Ingot",
        "description": "A hard metal with a blue tint, known for heat resistance and coloration properties.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["smelted_cobalt_ore"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 5,
            "heat_resistance": "high",
            "alloy_use": "high_temperature_tools_blue_tinted_alloys"
        }
    },
    {
        "name": "Stainless Steel Ingot",
        "description": "A rust-resistant steel alloy incorporating chromium and nickel. Used for precision tools and high-quality cutlery.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 90,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["alloyed_steel_chromium_nickel", "skarport_cutlery_medical_tools"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 7,
            "corrosion_resistance": "extreme",
            "edge_retention": "very_good",
            "appearance": "bright_shiny"
        }
    },
    {
        "name": "Tool Steel Ingot",
        "description": "A specialized steel alloy formulated for extreme hardness and wear resistance. Ideal for durable tools.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 110,
        "weight": 0.45,
        "is_craftable": True,
        "source_tags": ["high_carbon_steel_alloy_tungsten_trace", "dwarven_toolmaking_standard"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 9,
            "wear_resistance": "very_high",
            "brittleness": "medium",
            "notes": "Excellent for crafting tools that last."
        }
    },
    {
        "name": "Tungsten Carbide Ingot",
        "description": "An extremely hard and dense alloy used for armor-piercing weapons and heavy-duty industrial tools.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.EPIC,
        "base_value": 400,
        "weight": 0.8,
        "is_craftable": True,
        "source_tags": ["alloyed_tungsten_carbon_high_pressure_forge", "armor_piercing_cores"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 10,
            "density": "very_high",
            "melting_point": "extreme",
            "use": "specialized_arrowheads_weapon_cores_industrial_tools"
        }
    },
    {
        "name": "Elven Moonsteel Ingot",
        "description": "A silvery metal with faint blue luminescence created by elven smiths using moon-aligned forging techniques.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.EPIC,
        "base_value": 550,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["elven_secret_alloy_silver_starmetal_trace_moon_flux", "lethandrel_lunar_forge"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 7,
            "malleability": 6,
            "innate_magic_affinity": "moon_illusion",
            "weight_modifier": 0.85,
            "glows_faintly_in_moonlight": True,
            "anti_shadow_property": "minor"
        }
    },
    {
        "name": "Orcish Slagsteel Ingot",
        "description": "A rough but effective steel created by orcish smiths using battlefield scrap metal. Inexpensive but serviceable.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 0.6,
        "is_craftable": True,
        "source_tags": ["reforged_battlefield_scrap_orcish_techniques", "rivemark_rough_construction"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 5,
            "tensile_strength": 3,
            "impurity_level": "high_but_stable",
            "appearance": "rough_pitted",
            "cost_efficiency_brute_force": "high"
        }
    },
    {
        "name": "Recycled Cast Iron Ingot",
        "description": "Metal reprocessed from cast iron scrap. Good heat retention and suitable for cookware and non-impact items.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["smelted_cast_iron_scrap"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 4,
            "tensile_strength": 2,
            "heat_retention": "good",
            "uses": ["cookware", "simple_tools", "weights"]
        }
    },
    {
        "name": "Lead Ingot",
        "description": "Soft, dense metal with low melting point. Used for weights, sinkers, and radiation shielding for relic containment.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.7,
        "is_craftable": True,
        "source_tags": ["smelted_raw_lead"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 1,
            "malleability": 9,
            "uses": ["weights", "fishing_sinkers", "radiation_shielding_trace_relic_containment", "pipe_making_archaic"]
        }
    },
    {
        "name": "Pewter Ingot",
        "description": "A soft alloy primarily of tin with copper and antimony traces. Used for tankards, plates and decorative items.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 18,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["alloyed_tin_copper_antimony_trace", "human_artisan_metal_tableware"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 2,
            "malleability": 7,
            "low_melting_point": True,
            "finish": "dull_silver_lustre",
            "uses": ["tankards", "plates", "figurines", "buttons"]
        }
    },
    {
        "name": "Brass Ingot",
        "description": "An alloy of copper and zinc with a gold-like appearance. Used for decorative fittings, musical instruments, and gears.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 22,
        "weight": 0.35,
        "is_craftable": True,
        "source_tags": ["alloyed_copper_zinc_skarport_guilds", "decorative_and_functional"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 4,
            "malleability": 6,
            "corrosion_resistance": "good",
            "acoustic_properties": "good_for_instruments",
            "appearance": "bright_gold_like_sheen",
            "uses": ["fittings", "musical_instruments", "gears"]
        }
    },
    {
        "name": "Reclaimed Silver Ingot",
        "description": "Silver recovered from tarnished scrap. Slightly lower purity than mined silver but still valuable.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 30,
        "weight": 0.45,
        "is_craftable": True,
        "source_tags": ["smelted_tarnished_silver_lumps_refined"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 3,
            "malleability": 7,
            "purity_for_enchanting": "medium_low",
            "uses": ["simple_jewelry", "inlays", "electroplating_solution_component"]
        }
    },
    {
        "name": "Small Gold Nugget",
        "description": "A concentrated piece of pure gold, often created by melting gold dust. Highly valuable despite its small size.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 200,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["accumulated_gold_dust_melted_down", "raw_form_gold"],
        "illicit_in_regions": [],
        "properties": {
            "smelts_into": "Gold Ingot",
            "purity": 0.98,
            "malleability": 10,
            "value_density": "high"
        }
    },
    {
        "name": "Gold Ingot",
        "description": "Pure refined gold, prized for its resistance to tarnish, high magical conductivity, and intrinsic value.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.EPIC,
        "base_value": 1000,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["refined_gold_nuggets_or_high_purity_ore", "currency_standard_jewelry_mastercraft"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 2,
            "malleability": 10,
            "conductivity_magical": "very_high",
            "non_corrosive": True,
            "symbol_of_wealth_power": True
        }
    },
    # Smithing Byproducts & Consumables
    {
        "name": "Iron Slag",
        "description": "Waste material from iron smelting. Almost worthless, but can be used as crude construction filler.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 0.1,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["byproduct_iron_smelting"],
        "illicit_in_regions": [],
        "properties": {
            "use": "crude_construction_filler_roadbeds",
            "trade_value": "very_low"
        }
    },
    {
        "name": "Steel Shavings",
        "description": "Metal fragments produced during grinding and shaping of steel. Can be collected and reforged in bulk.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 0.5,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["byproduct_steel_smithing_grinding"],
        "illicit_in_regions": [],
        "properties": {
            "use": "can_be_reforged_into_low_quality_ingot_in_bulk",
            "component_for_sparking_powder": True
        }
    },
    {
        "name": "Broken Whetstone Fragments",
        "description": "Pieces of used-up whetstones. Can be repurposed as abrasive material.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 0.2,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["used_up_whetstone", "salvageable_grit"],
        "illicit_in_regions": [],
        "properties": {
            "use": "component_for_grinding_paste",
            "sharpening_value": "minimal"
        }
    },
    {
        "name": "Forge Ash",
        "description": "Residual ash from forge fires. Has minimal value but can be used in soap making or as poor soil additive.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 0.05,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["byproduct_forge_fuel_burning"],
        "illicit_in_regions": [],
        "properties": {
            "use": "component_for_lye_soap_making_soil_additive_poorly",
            "trade_value": "negligible"
        }
    },
    {
        "name": "Tempering Salts (Basic)",
        "description": "A mineral salt blend used during heat treatment to control hardening and reduce brittleness in standard metals.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["mineral_salt_blend", "heat_treatment_control"],
        "illicit_in_regions": [],
        "properties": {
            "effect_on_metal": "improves_hardness_reduces_brittleness_standard_metals",
            "quantity_per_use": "small_pinch",
            "effectiveness_modifier": 1.0
        }
    },
    # Fuels & Additives
    {
        "name": "Seasoned Hardwood",
        "description": "Properly dried hardwood for forge use. Burns hotter than green wood but with more smoke.",
        "material_type": MaterialType.WOOD,
        "rarity": Rarity.COMMON,
        "base_value": 0.5,
        "weight": 0.3,
        "is_craftable": False,
        "source_tags": ["general_fuel", "forestry_byproduct"],
        "illicit_in_regions": [],
        "properties": {
            "fuel_value": 5,
            "smoke_level": "high",
            "burn_duration_modifier": 0.8
        }
    },
    {
        "name": "Magma-Kissed Coal",
        "description": "Coal from geothermal vents in Stonewake. Burns extremely hot with minimal smoke, ideal for high-temperature forging.",
        "material_type": MaterialType.ORE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 8,
        "weight": 0.25,
        "is_craftable": False,
        "source_tags": ["stonewake_lower_vents", "geothermal_fuel", "dwarven_preferred"],
        "illicit_in_regions": [],
        "properties": {
            "fuel_value": 25,
            "smoke_level": "low",
            "heat_intensity": "very_high",
            "ignites_quickly": True
        }
    },
    {
        "name": "Limestone Flux",
        "description": "Powdered limestone used as a purification agent in smelting to remove impurities and improve metal quality.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["crushed_limestone", "purification_agent"],
        "illicit_in_regions": [],
        "properties": {
            "impurity_removal_efficiency": 0.6,
            "slag_reduction": True
        }
    },
    {
        "name": "Dwarven Oath-Sand",
        "description": "Crystalline sand from sacred dwarven caves. Used in ritual smithing to enhance durability and bind oaths to metal.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 30,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["dwarven_sacred_cave_sand", "ritual_smithing_additive"],
        "illicit_in_regions": [],
        "properties": {
            "effect_on_metal": "enhances_durability_oaths",
            "application": "sprinkled_during_tempering",
            "rarity_modifier_dwarven_items": 1.1
        }
    },
    {
        "name": "Standard Quenching Oil",
        "description": "A blend of animal fats and mineral oils used to rapidly cool heated metal during tempering.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 4,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["rendered_animal_fat", "mineral_oil_blend"],
        "illicit_in_regions": [],
        "properties": {
            "cooling_rate": "medium",
            "effect_on_hardness": "standard"
        }
    },
    {
        "name": "Orcish Fury-Quench",
        "description": "A volatile quenching fluid used by orcish smiths, containing herbs, blood, and secret ingredients. Creates jagged edges.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 25,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["orcish_ritual_blend_herbs_blood", "secret_ingredient_grog"],
        "illicit_in_regions": [],
        "properties": {
            "cooling_rate": "fast_volatile",
            "effect_on_metal": "adds_minor_jagged_edge_chance",
            "risk_of_brittleness": 0.1,
            "fumes_intoxicating": True
        }
    },
    {
        "name": "Purified Firecrystal Dust",
        "description": "Refined dust from fire crystals found in the Ember Wastes. Drastically increases forge temperature when added to fuel.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 35,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["refined_firecrystal_ember_wastes", "high_temp_fuel_additive"],
        "illicit_in_regions": [],
        "properties": {
            "fuel_value_boost_percentage": 50,
            "heat_intensity_increase": "high",
            "risk_of_flare_up": 0.05,
            "notes": "Use sparingly."
        }
    },
    {
        "name": "Elven Moon-Flux",
        "description": "A shimmering silver powder created by elven alchemists under moonlight. Purifies magical metals and enhances enchantability.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 120,
        "weight": 0.03,
        "is_craftable": False,
        "source_tags": ["lethandrel_alchemical_creation", "lunar_aligned_purifier"],
        "illicit_in_regions": [],
        "properties": {
            "impurity_removal_efficiency_magical_metals": 0.9,
            "enhances_enchantability": True,
            "requires_moonlight_during_use": True,
            "rarity_modifier_elven_items": 1.3
        }
    },
    {
        "name": "Dwarven Hearthstone Powder",
        "description": "Ground stone from dwarven forges that have been active for centuries. Imparts minor fire resistance and durability to items.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 40,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["ground_dwarven_forge_hearthstone", "ritual_smithing_additive"],
        "illicit_in_regions": [],
        "properties": {
            "effect_on_metal": "imparts_minor_fire_resistance_and_durability_dwarven_items",
            "application": "mixed_with_quenching_oil_or_dusted_on"
        }
    },
    # Hafts, Grips, Components
    {
        "name": "Sturdy Ash Wood Haft",
        "description": "A well-crafted wooden handle for tools and weapons, made from durable ash wood.",
        "material_type": MaterialType.WOOD,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["shaped_ash_wood", "tool_weapon_component"],
        "illicit_in_regions": [],
        "properties": {
            "strength": 6,
            "flexibility": 4,
            "grip_surface": "smooth"
        }
    },
    {
        "name": "Beastfolk Bone-Studded Grip",
        "description": "A leather grip reinforced with small bone shards for improved handling. Distinctive to Ashkar Vale beastfolk craftsmanship.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 12,
        "weight": 0.15,
        "is_craftable": True,
        "source_tags": ["leather_wrapped_bone_shards", "ashkar_vale_craft"],
        "illicit_in_regions": [],
        "properties": {
            "grip_enhancement": "high",
            "intimidation_factor": "low",
            "damage_type_bash": "piercing_traces"
        }
    },
    {
        "name": "Hardened Leather Strips",
        "description": "Treated leather strips used for binding, wrapping, and crafting components in both weapons and armor.",
        "material_type": MaterialType.LEATHER,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["tanned_hide", "binding_wrapping_material"],
        "illicit_in_regions": [],
        "properties": {
            "flexibility": 6,
            "binding_strength": 4,
            "durability": "medium"
        }
    },
    {
        "name": "Steel Rivets & Fittings",
        "description": "Small steel parts used in armor construction and to connect components in weapons and tools.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 4,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["small_steel_parts", "armor_construction"],
        "illicit_in_regions": [],
        "properties": {
            "quantity_per_unit": 50,
            "strength_rating": 5
        }
    },
    {
        "name": "Dwarven Rune-Etched Clasp",
        "description": "A small metal fastener inscribed with dwarven protective runes. Used to enhance armor with minor warding.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 75,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["dwarven_runesmith_craft", "armor_enhancement_component"],
        "illicit_in_regions": [],
        "properties": {
            "rune_effect": "minor_warding_physical",
            "attunement_required": "dwarven_kin_or_oathbound",
            "glows_faintly_near_danger": True
        }
    },
    {
        "name": "Carved Ironwood Hilt",
        "description": "A precisely carved weapon hilt made from dense ironwood. Provides excellent grip comfort and dampens vibration.",
        "material_type": MaterialType.WOOD,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 0.25,
        "is_craftable": True,
        "source_tags": ["artisan_carved_ironwood", "weapon_hilt_superior_grip"],
        "illicit_in_regions": [],
        "properties": {
            "strength": 8,
            "grip_comfort_modifier": 1.1,
            "vibration_dampening": "good"
        }
    },
    {
        "name": "Wire-Wrapped Leather Grip",
        "description": "A leather grip reinforced with a steel wire wrapping pattern. Provides secure handling even in wet conditions.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 8,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["leather_strips_steel_wire_wrap", "secure_weapon_grip"],
        "illicit_in_regions": [],
        "properties": {
            "grip_enhancement": "medium_high",
            "durability": "medium",
            "requires_skill_assembly": "Leatherworking L1"
        }
    },
    {
        "name": "Weighted War-Pick Head",
        "description": "A specialized pick head designed for armor penetration. Can be hafted to create a devastating anti-armor weapon.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 0.8,
        "is_craftable": True,
        "source_tags": ["forged_tool_steel", "armor_piercing_pick_component"],
        "illicit_in_regions": [],
        "properties": {
            "armor_penetration_base": 1.5,
            "hafting_socket_type": "standard_pick"
        }
    },
    {
        "name": "Serrated Axe Blade Insert",
        "description": "A toothed steel insert designed to be added to axe blades. Creates vicious wounds against unarmored targets.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 35,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["high_carbon_steel_insert", "enhances_axe_tearing_damage"],
        "illicit_in_regions": [],
        "properties": {
            "bonus_damage_vs_unarmored_or_lightly_armored": "1d4_bleed",
            "requires_precision_fitting": True
        }
    },
    {
        "name": "Balanced Steel Pommel",
        "description": "A carefully weighted pommel that improves weapon balance. Can be customized for different weight distributions.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["forged_steel_component", "weapon_balance_enhancement"],
        "illicit_in_regions": [],
        "properties": {
            "balance_improvement_modifier": 0.1,
            "weight_customizable": True
        }
    },
    {
        "name": "Ornate Silver Crossguard",
        "description": "A decorative yet functional crossguard made from silver. Provides a small bonus to parrying while adding aesthetic value.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 0.25,
        "is_craftable": True,
        "source_tags": ["silver_artisan_craft", "decorative_protective_weapon_part"],
        "illicit_in_regions": [],
        "properties": {
            "parry_bonus_modifier": 0.05,
            "aesthetic_appeal": "high",
            "vulnerability_to_tarnish": "medium"
        }
    },
    {
        "name": "Drake Scale (Red)",
        "description": "A large, fire-resistant scale from an ember drake. Can be worked into armor for heat protection or weapons for fire damage.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 90,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["harvested_ember_wastes_drake", "fire_affinity"],
        "illicit_in_regions": [],
        "properties": {
            "elemental_resistance_fire_armor": "high",
            "imbue_weapon_fire_damage_chance": "medium",
            "flexibility": "low",
            "requires_special_tools_to_work": True
        }
    },
    {
        "name": "Shadow Panther Hide Segment",
        "description": "A piece of dark hide from the elusive shadow panthers of Whispering Woods. Enhances stealth when incorporated into armor.",
        "material_type": MaterialType.LEATHER,
        "rarity": Rarity.RARE,
        "base_value": 70,
        "weight": 0.3,
        "is_craftable": False,
        "source_tags": ["hunted_whispering_woods_shadow_panther", "stealth_properties"],
        "illicit_in_regions": [],
        "properties": {
            "smithing_use": "armor_lining_grip_wrap",
            "stealth_modifier_when_used_in_armor": 0.1,
            "darkness_affinity": True
        }
    },
    {
        "name": "Spiritwood Heart",
        "description": "A rare core of wood from an ancient spirit tree. Acts as a mana conduit and enchantment focus in weapons.",
        "material_type": MaterialType.WOOD,
        "rarity": Rarity.EPIC,
        "base_value": 300,
        "weight": 0.4,
        "is_craftable": False,
        "source_tags": ["lethandrel_ancient_spirit_tree_fallen_branch", "mana_conductive"],
        "illicit_in_regions": ["Stonewake_unless_licensed"],
        "properties": {
            "smithing_use": "weapon_haft_core_enchantment_focus",
            "mana_capacity_modifier": 1.2,
            "durability": "medium",
            "requires_elven_carving_techniques": True
        }
    },
    {
        "name": "Crysteel Shard",
        "description": "A razor-sharp crystalline material that emanates intense cold. Extremely effective but dangerously brittle.",
        "material_type": MaterialType.GEM,
        "rarity": Rarity.EPIC,
        "base_value": 400,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["crystal_highlands_deep_cavern_growth", "intense_cold_emanation"],
        "illicit_in_regions": [],
        "properties": {
            "smithing_use": "weapon_core_inlay_arrowhead",
            "innate_cold_damage_high": True,
            "brittleness": "very_high_handle_with_care",
            "can_shatter_if_struck_hard": True
        }
    },
    # Sharpening/Polishing
    {
        "name": "Basic Whetstone",
        "description": "A simple stone for sharpening blades. Coarse grade but effective for basic maintenance.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["shaped_sandstone", "blade_maintenance"],
        "illicit_in_regions": [],
        "properties": {
            "sharpening_grade": "coarse",
            "uses": 10
        }
    },
    {
        "name": "Dwarven Grindstone Wheel",
        "description": "A precision-crafted grinding wheel for achieving master-grade edges. Requires workshop mounting.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 5.0,
        "is_craftable": True,
        "source_tags": ["stonewake_artisan_tool", "requires_workshop_setup"],
        "illicit_in_regions": [],
        "properties": {
            "sharpening_grade": "fine_master",
            "durability": "high",
            "can_sharpen_magical_metals": True
        }
    },
    {
        "name": "Ferverl Sun-Sand Polish",
        "description": "Sacred sand from Thal-Zirad, blessed by solar priests. Imparts a mirror finish and minor fire resistance.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 18,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["thal_zirad_blessed_sand", "ritual_finish_agent"],
        "illicit_in_regions": [],
        "properties": {
            "polishing_effect": "mirror_sheen",
            "minor_fire_resistance_buff_duration_hours": 1,
            "application_ritual": "sun_chant"
        }
    },
    {
        "name": "Hollow Grindstone Wheel",
        "description": "A specialized grindstone with a concave face, designed to create razor-sharp hollow-ground edges.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 4.0,
        "is_craftable": True,
        "source_tags": ["dwarven_engineered_grindstone", "allows_for_concave_blade_grinds_razor_sharpness"],
        "illicit_in_regions": [],
        "properties": {
            "sharpening_grade": "razor_fine",
            "durability": "medium",
            "can_create_hollow_grind_edge": True,
            "notes": "Requires careful control."
        }
    },
    # Components for Other Crafts
    {
        "name": "Iron Nails (Bag of 100)",
        "description": "Standard iron nails in various sizes. Essential for carpentry and construction.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.5,
        "is_craftable": True,
        "source_tags": ["mass_produced_smithies", "construction_carpentry_basic"],
        "illicit_in_regions": [],
        "properties": {
            "size_variety": ["small", "medium", "large_available_by_order"],
            "strength": "standard_iron",
            "quantity_per_unit": 100
        }
    },
    {
        "name": "Steel Hinges (Pair)",
        "description": "A pair of durable hinges for doors, chests, or other furniture. Standard construction quality.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.COMMON,
        "base_value": 5,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["standard_door_chest_hinge", "utility_smithing"],
        "illicit_in_regions": [],
        "properties": {
            "load_capacity_kg": 50,
            "durability": "good",
            "requires_screws_or_nails_to_fit": True
        }
    },
    {
        "name": "Bronze Gear Blank",
        "description": "A cast bronze disc ready to be shaped into precision gears for clockwork or mechanical devices.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 12,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["cast_bronze_disc", "tinkering_clockwork_component_preform"],
        "illicit_in_regions": [],
        "properties": {
            "diameter_cm": 5,
            "thickness_cm": 0.5,
            "machinability": "good",
            "requires_further_shaping_into_gear": True
        }
    },
    {
        "name": "Steel Plowshare Blank",
        "description": "A heavy steel piece shaped for agricultural use. Requires final sharpening and hafting to become a functional plow.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 25,
        "weight": 2.5,
        "is_craftable": True,
        "source_tags": ["heavy_steel_forging", "agricultural_tool_component_rivemark"],
        "illicit_in_regions": [],
        "properties": {
            "hardness": 7,
            "wear_resistance_soil": "good",
            "requires_sharpening_and_hafting": True
        }
    },
    {
        "name": "Iron Cauldron Shell",
        "description": "The main body of an iron cooking cauldron. Needs legs and handle attachments to be complete.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 18,
        "weight": 3.0,
        "is_craftable": True,
        "source_tags": ["hammered_iron_sheets_shaped", "cookware_alchemical_vessel_component"],
        "illicit_in_regions": [],
        "properties": {
            "capacity_liters": 10,
            "heat_distribution": "even",
            "requires_legs_and_handle_attachment": True
        }
    },
    {
        "name": "Silver Wire Spool (Fine)",
        "description": "Thin, pure silver wire for detailed jewelry work and rune etching. High magical conductivity but low tensile strength.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["drawn_silver_ingot", "jewelry_enchanting_fine_detail_work"],
        "illicit_in_regions": [],
        "properties": {
            "gauge": "30_fine",
            "length_meters": 5,
            "conductivity_for_runes": "high",
            "tensile_strength": "low"
        }
    }
]

# Alchemy & Potion Brewing Materials
ALCHEMY_MATERIALS = [
    # Herbal Reagents
    {
        "name": "Sunpetal Leaf",
        "description": "Bright yellow leaves that absorb sunlight. When crushed and infused, they provide minor healing properties.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["harvested_verdant_frontier_daytime", "common_field_herb"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "minor_healing_stimulant",
            "potency": 0.2,
            "preparation": "crush_infuse",
            "duration_modifier": 0.8,
            "synergy_with": ["Purified Water", "Honey"]
        }
    },
    {
        "name": "Mooncluster Berries",
        "description": "Small luminescent berries that glow faintly in moonlight. They have mild mana regenerative properties when properly prepared.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.UNCOMMON,
        "base_value": 5,
        "weight": 0.02,
        "is_craftable": False,
        "source_tags": ["harvested_whispering_woods_night", "lunar_affinity", "elven_cultivation_lethandrel"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "mana_regeneration_slow",
            "potency": 0.3,
            "preparation": "juice_ferment_lightly",
            "duration_seconds": 300,
            "side_effect_chance": "mild_drowsiness_0.05"
        }
    },
    {
        "name": "Shimmering Marsh Cap",
        "description": "Bioluminescent mushroom that grows in marshlands. Has brief invisibility properties when properly processed.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.RARE,
        "base_value": 20,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["harvested_shimmering_marshes_bioluminescent_fungus", "toxic_if_raw"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "invisibility_brief",
            "potency": 0.6,
            "preparation": "distill_neutralize_toxin",
            "duration_seconds": 60,
            "toxicity_raw": "medium",
            "purified_by": ["Ferverl Ash Salts"]
        }
    },
    {
        "name": "Rivercress Sprig",
        "description": "A common aquatic herb found along riverbanks. Provides minor stamina recovery when steeped.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.COMMON,
        "base_value": 0.8,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["harvested_rivemark_riverbanks", "aquatic_herb"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "minor_stamina_recovery",
            "potency": 0.15,
            "preparation": "steep",
            "taste_profile": "peppery"
        }
    },
    {
        "name": "Ember Wastes Bloom",
        "description": "A hardy flower that blooms in the heat of desert oases. Provides minor fire resistance when prepared.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.UNCOMMON,
        "base_value": 8,
        "weight": 0.03,
        "is_craftable": False,
        "source_tags": ["harvested_ember_wastes_oases_heat_resistant", "ferverl_use"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "minor_fire_resistance",
            "potency": 0.4,
            "preparation": "dry_powder",
            "duration_seconds": 180,
            "synergy_with": ["Drake Scale Powder"]
        }
    },
    {
        "name": "Frostbound Lichen",
        "description": "A cold-adapted lichen that grows on rocks in frozen regions. Provides minor cold resistance.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.UNCOMMON,
        "base_value": 7,
        "weight": 0.02,
        "is_craftable": False,
        "source_tags": ["harvested_frostbound_tundra_rocks", "cryo_adapted"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "minor_cold_resistance",
            "potency": 0.4,
            "preparation": "grind_infuse_cold",
            "duration_seconds": 180,
            "antagonistic_to": ["Ember Wastes Bloom"]
        }
    },
    {
        "name": "Verdant Vine Extract",
        "description": "A rare extract from sentient vines, processed through elven ritual techniques. Enhances cellular regeneration.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.RARE,
        "base_value": 25,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["processed_lethandrel_sentient_vines_elven_ritual", "living_essence"],
        "illicit_in_regions": ["Stonewake_uncontrolled"],
        "properties": {
            "alchemical_property": "enhanced_regeneration_cellular",
            "potency": 0.7,
            "preparation": "ritual_extraction_stabilize",
            "duration_seconds": 30,
            "side_effect_chance": "minor_plant_growth_on_user_0.01"
        }
    },
    {
        "name": "Crystal Highlands Wort",
        "description": "An herb that grows in mineral-rich soil. Serves as a base for physical resistance potions.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.04,
        "is_craftable": False,
        "source_tags": ["harvested_crystal_highlands_mineral_rich_soil", "earth_affinity"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "physical_damage_resistance_potion_base",
            "potency": 0.3,
            "preparation": "decoct",
            "notes": "Absorbs properties of added minerals."
        }
    },
    {
        "name": "Corpse-Finder Moss",
        "description": "A rare moss that grows near undead remains. Can be used to detect undead when burned as incense.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.RARE,
        "base_value": 15,
        "weight": 0.02,
        "is_craftable": False,
        "source_tags": ["grows_near_undead_remains_shimmering_marshes", "necromantic_trace"],
        "illicit_in_regions": ["Skarport_public_market"],
        "properties": {
            "alchemical_property": "detect_undead_briefly",
            "potency": 0.5,
            "preparation": "burn_as_incense_inhale_fumes",
            "duration_seconds": 120,
            "toxicity_fumes": "low_headache"
        }
    },
    {
        "name": "Thal-Zirad Sun-Dried Petals",
        "description": "Sacred flower petals dried in the desert sun and used in ritual offerings. Provides clarity of mind.",
        "material_type": MaterialType.HERB,
        "rarity": Rarity.RARE,
        "base_value": 30,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["thal_zirad_sacred_garden_offering_flower", "ritual_preparation"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "clarity_of_mind_divination_aid",
            "potency": 0.6,
            "preparation": "steep_in_blessed_water",
            "duration_modifier": 1.2,
            "requires_ritual_focus": True
        }
    },
    # Animal & Monster Parts
    {
        "name": "Giant Spider Venom Gland",
        "description": "A toxic sac extracted from giant spiders. When properly processed, it creates a paralytic agent.",
        "material_type": MaterialType.ANIMAL_PART,
        "rarity": Rarity.UNCOMMON,
        "base_value": 12,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["harvested_whispering_woods_giant_spider", "toxic_creature_part"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "paralysis_poison_weak",
            "potency": 0.4,
            "preparation": "extract_dilute_stabilize",
            "application": "weapon_coating_trap_component",
            "antidote_known": "Sunpetal Leaf Paste"
        }
    },
    {
        "name": "Ember Drake Scale",
        "description": "Heat-resistant scales from ember drakes that retain fiery properties. Used in fire-resistance potions.",
        "material_type": MaterialType.ANIMAL_PART,
        "rarity": Rarity.RARE,
        "base_value": 35,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["hunted_ember_wastes_drake", "predator_trophy", "heat_resistant"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "fire_resistance_strong",
            "potency": 0.7,
            "preparation": "grind_to_powder_infuse",
            "duration_seconds": 300,
            "side_effect": "body_temperature_increased_slightly",
            "material_resistance_fire": "high"
        }
    },
    {
        "name": "Wyvern Scale Powder",
        "description": "Ground scales from ember wyverns. Provides strong fire resistance and can enhance fire-based potions.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 75,
        "weight": 0.03,
        "is_craftable": True,
        "source_tags": ["hunted_ember_wastes_wyvern_ground_scales", "elemental_creature_fire"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "fire_resistance_potion_strong",
            "potency_modifier": 1.5,
            "elemental_charge": "fire",
            "preparation": "infuse_in_oil_base_potion",
            "synergy_with": ["Ember Wastes Bloom"]
        }
    },
    {
        "name": "Spirit Fox Saliva",
        "description": "Ethereal saliva collected through beastfolk rituals. Greatly enhances sensory perception when prepared.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 300,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["beastfolk_ritual_collection_ashkar_vale_spirit_animal", "ethereal_essence"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "heightened_senses_elixir_major",
            "potency": 0.9,
            "preparation": "handle_with_silver_tools_infuse_moonlight",
            "duration_seconds": 600,
            "volatility": "medium",
            "requires_stabilizer": True
        }
    },
    {
        "name": "Grotesque Hide Oil",
        "description": "Rendered fat from marsh grotesques. Provides minor acid resistance when processed into potions.",
        "material_type": MaterialType.ANIMAL_PART,
        "rarity": Rarity.UNCOMMON,
        "base_value": 9,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["rendered_fat_shimmering_marshes_grotesque", "mutated_creature"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "acid_resistance_potion_minor",
            "potency": 0.3,
            "preparation": "render_filter",
            "smell": "pungent_acrid",
            "duration_seconds": 240
        }
    },
    {
        "name": "Griffin Feather (Down)",
        "description": "Soft down feathers shed from griffin nests. Used to create levitation and lightness effects.",
        "material_type": MaterialType.ANIMAL_PART,
        "rarity": Rarity.RARE,
        "base_value": 40,
        "weight": 0.005,
        "is_craftable": False,
        "source_tags": ["collected_crystal_highlands_griffin_nest_shed_feather", "sky_affinity"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "levitation_potion_component_lightness",
            "potency": 0.5,
            "preparation": "weave_into_potion_filter_chant",
            "notes": "Aids in reducing potion weight and improving ascent."
        }
    },
    {
        "name": "Basilisk Eye (Petrified)",
        "description": "The petrified eye of a slain basilisk. Provides powerful defensive properties when carefully processed.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 250,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["slain_basilisk_ember_wastes_rare_drop", "petrification_magic_source"],
        "illicit_in_regions": ["Skarport_restricted_trade"],
        "properties": {
            "alchemical_property": "stoneflesh_potion_ingredient_major_defense",
            "potency": 0.8,
            "preparation": "grind_carefully_under_ward_infuse_lead_solution",
            "side_effect_chance": "slight_stiffness_0.1"
        }
    },
    {
        "name": "Troll Blood (Regenerative)",
        "description": "Blood from tundra trolls that retains regenerative properties. Must be preserved quickly or it becomes useless.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 0.15,
        "is_craftable": False,
        "source_tags": ["harvested_frostbound_tundra_troll_requires_rapid_preservation", "vital_essence"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "regeneration_potion_potent_base",
            "potency": 0.6,
            "preparation": "stabilize_with_iron_salts_keep_cold",
            "notes": "Highly unstable if not preserved quickly."
        }
    },
    # Minerals & Crystals
    {
        "name": "Purified Alchemical Salt",
        "description": "Refined white crystalline substance essential for stabilizing volatile reactions and preserving potions.",
        "material_type": MaterialType.MINERAL,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["refined_crystal_highlands_salt_deposits", "skarport_alchemists_standard"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "stabilizer_preservative",
            "potency": 0.3,
            "preparation": "dissolve_or_add_directly",
            "shelf_life_extension_days": 30,
            "neutralizes_acidity": "low"
        }
    },
    {
        "name": "Purified Leyline Water",
        "description": "Water purified through elven ritual techniques and infused with leyline energy. Standard for elven alchemy.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["lethandrel_ritual_purification_leylines", "base_solvent_elven_alchemy"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "high",
            "purity_level": 0.95,
            "mana_infusion_base": True,
            "stability": "good",
            "notes": "Standard for Elven potions."
        }
    },
    {
        "name": "Ferverl Blood-Ash",
        "description": "Ash created through ferverl blood rituals, imbued with mana. A powerful but potentially corrupting catalyst.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 0.02,
        "is_craftable": False,
        "source_tags": ["ferverl_ritual_byproduct_ashkar_vale_emberflow_mana_imbued_ash"],
        "illicit_in_regions": ["Skarport_Accord_controlled"],
        "properties": {
            "alchemical_property": "mutation_inducer_controlled_catalyst",
            "potency_modifier": 1.3,
            "preparation": "handle_with_obsidian_tools",
            "corruption_taint": "low_residual_if_blessed",
            "synergy_with": ["Spirit Fox Saliva"]
        }
    },
    {
        "name": "Ground Moonstone",
        "description": "Pulverized moonstone gem charged under moonlight. Enhances illusion potions and amplifies subtle energies.",
        "material_type": MaterialType.GEM,
        "rarity": Rarity.UNCOMMON,
        "base_value": 18,
        "weight": 0.03,
        "is_craftable": True,
        "source_tags": ["crystal_highlands_moonstone_gem_pulverized", "lunar_reflective_properties"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "illusion_potion_enhancer_duration",
            "potency": 0.4,
            "preparation": "grind_fine_charge_under_moonlight",
            "notes": "Amplifies subtle energies."
        }
    },
    {
        "name": "Sulfur Powder",
        "description": "Ground sulfur from volcanic vents. Used in fumigation and as a component for weak acids and smokesticks.",
        "material_type": MaterialType.MINERAL,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.04,
        "is_craftable": False,
        "source_tags": ["volcanic_vents_stonewake_caldera_ember_wastes_geothermal", "combustible_element"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "fumigation_ingredient_minor_poison_component",
            "potency": 0.2,
            "preparation": "grind_sift",
            "flammability": "high",
            "use_in": ["Smokesticks", "Weak Acid Vials"]
        }
    },
    {
        "name": "Quicksilver Globules",
        "description": "Liquid mercury obtained from rare cinnabar ore. A powerful transmutation agent but highly toxic.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 70,
        "weight": 0.25,
        "is_craftable": False,
        "source_tags": ["rare_cinnabar_ore_refinement_dwarven_process", "liquid_metal_volatile"],
        "illicit_in_regions": ["Lethandrel_restricted"],
        "properties": {
            "alchemical_property": "transmutation_agent_base_catalyst_for_change",
            "potency": 0.7,
            "preparation": "store_in_sealed_glass_handle_with_care",
            "toxicity": "high_fumes_and_contact",
            "stability": "low"
        }
    },
    {
        "name": "Rock Salt Chunks",
        "description": "Common salt mined from desert flats. Used as a preservative and minor stabilizer in simple preparations.",
        "material_type": MaterialType.MINERAL,
        "rarity": Rarity.COMMON,
        "base_value": 0.5,
        "weight": 0.08,
        "is_craftable": False,
        "source_tags": ["mined_ember_wastes_salt_flats", "preservative_mundane_reagent"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "stabilizer_minor_preservative",
            "potency": 0.1,
            "preparation": "crush_dissolve",
            "notes": "Common in food preservation, limited alchemical use."
        }
    },
    {
        "name": "Ectoplasmic Residue",
        "description": "Ethereal remains collected from haunted ruins. Used to create potions of incorporeality and etherealness.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["haunted_ruins_verdant_frontier_ethereal_remains", "spirit_essence"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "etherealness_potion_component_incorporeality",
            "potency": 0.6,
            "preparation": "collect_in_silvered_vial_stabilize_with_salt",
            "duration_seconds": 30,
            "instability": "medium"
        }
    },
    {
        "name": "Mana-Charged Crystal Dust",
        "description": "Dust from shattered mana crystals containing pure mana energy. Can supercharge potions or cause dangerous overloads.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 150,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["shattered_mana_crystal_crucible_spire_lethandrel_leyroot_grove", "pure_mana_form"],
        "illicit_in_regions": [],
        "properties": {
            "alchemical_property": "direct_mana_infusion_potion_powerful",
            "potency": 1.0,
            "preparation": "handle_with_insulated_gloves_infuse_directly",
            "notes": "Can supercharge potions or cause overload."
        }
    },
    # Solvents & Bases
    {
        "name": "Filtered River Water",
        "description": "Basic river water filtered through cloth and sand. Suitable only for the simplest alchemical preparations.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 0.2,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["collected_rivemark_river_filtered_cloth_sand", "basic_solvent"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "low",
            "purity_level": 0.6,
            "mana_infusion_base": False,
            "stability": "low_spoils_quickly",
            "notes": "Suitable for very simple brews."
        }
    },
    {
        "name": "Dwarven Spring Water",
        "description": "Mineral-rich water from deep Stonewake springs. Imparts earthy flavors and is good for fortitude potions.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 5,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["stonewake_deep_springs_mineral_rich", "dwarven_brewing_base"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "medium",
            "purity_level": 0.8,
            "mana_infusion_base": "trace",
            "stability": "medium",
            "notes": "Imparts a slight earthy taste, good for fortitude potions."
        }
    },
    {
        "name": "Orcish Grog Base",
        "description": "Fermented grain and herb mixture following traditional orcish recipes. Volatile but potent alcoholic base.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 4,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["fermented_grain_herbs_rivemark_orcish_recipe", "potent_alcoholic_base"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "medium_volatile",
            "purity_level": 0.5,
            "mana_infusion_base": False,
            "stability": "good_if_sealed",
            "notes": "Can make potions very strong, or very unpredictable. Flammable."
        }
    },
    {
        "name": "Refined Animal Fat",
        "description": "Purified animal fat suitable for creating oil-based salves and ointments for topical applications.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.08,
        "is_craftable": True,
        "source_tags": ["rendered_animal_fat_purified_multiple_sources", "oil_base_salves"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "oil_soluble_only",
            "purity_level": 0.7,
            "application": "topical_salves_ointments",
            "stability": "medium"
        }
    },
    {
        "name": "Lethandrel Moon-Dew",
        "description": "Dew collected during lunar cycles from sacred groves. The purest elven solvent, excellent for delicate magical properties.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 40,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["collected_lethandrel_ritual_grove_lunar_cycle", "pure_elven_solvent"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "very_high_ethereal",
            "purity_level": 0.99,
            "mana_infusion_base": True,
            "stability": "high_if_kept_dark",
            "notes": "Preserves delicate magical properties, enhances illusion/mind effects."
        }
    },
    {
        "name": "Ashkar Vale Spirit-Water",
        "description": "Spring water blessed by beastfolk shamans. Absorbs ambient energies and is favored for nature-aspected potions.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 35,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["ashkar_vale_emberflow_springs_blessed_by_shamans", "beastfolk_ritual_base"],
        "illicit_in_regions": [],
        "properties": {
            "solvent_power": "medium_wild",
            "purity_level": 0.75,
            "mana_infusion_base": "shamanic_wild",
            "stability": "medium_absorbs_ambient_energies",
            "notes": "Favored for nature or spirit-aspected potions."
        }
    }
]

# Woodworking & Carpentry Materials
WOODWORKING_MATERIALS = [
    # Raw & Processed Woods
    {
        "name": "Pine Log (Rough Cut)",
        "description": "A freshly cut log of pine wood. Soft and easy to work with, but not very durable.",
        "material_type": MaterialType.WOOD_RAW,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 15.0,
        "is_craftable": False,
        "source_tags": ["harvested_verdant_frontier_pine_forests", "common_softwood_lumber"],
        "illicit_in_regions": [],
        "properties": {
            "processes_into": "Pine Planks",
            "density_kg_m3": 450,
            "hardness_janka_lbf": 380,
            "workability": "easy",
            "knot_frequency": "medium",
            "resin_content": "medium_high",
            "uses_raw": ["firewood", "rough_shelter_construction"]
        }
    },
    {
        "name": "Pine Planks (Bundle of 5)",
        "description": "Milled pine boards ready for construction or crafting. Affordable but prone to warping and splintering.",
        "material_type": MaterialType.WOOD_PROCESSED,
        "rarity": Rarity.COMMON,
        "base_value": 5,
        "weight": 5.0,
        "is_craftable": True,
        "source_tags": ["milled_pine_logs_rivemark_sawmill", "basic_construction_material"],
        "illicit_in_regions": [],
        "properties": {
            "dimensions_cm_each_plank": "200x20x2.5",
            "finish": "rough_sawn",
            "nail_holding_ability": "fair",
            "splinter_risk": "medium",
            "uses": ["simple_furniture", "crates", "fences", "flooring_sublayer"]
        }
    },
    {
        "name": "Oak Log (Seasoned)",
        "description": "A properly aged oak log, dried to reduce moisture content. Prized for its strength and beautiful grain.",
        "material_type": MaterialType.WOOD_RAW,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 25.0,
        "is_craftable": False,
        "source_tags": ["harvested_whispering_woods_oak_groves_aged_one_year", "durable_hardwood_lumber"],
        "illicit_in_regions": [],
        "properties": {
            "processes_into": "Oak Beams_Oak Planks",
            "density_kg_m3": 720,
            "hardness_janka_lbf": 1290,
            "workability": "moderate_requires_sharp_tools",
            "tannin_content": "high_corrodes_iron_fasteners",
            "strength": "high"
        }
    },
    {
        "name": "Oak Planks (Bundle of 3)",
        "description": "High-quality oak planks milled from seasoned logs. Excellent for fine furniture and structural applications.",
        "material_type": MaterialType.WOOD_PROCESSED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 25,
        "weight": 7.0,
        "is_craftable": True,
        "source_tags": ["milled_seasoned_oak_logs_skarport_carpentry_guild", "high_quality_furniture_construction"],
        "illicit_in_regions": [],
        "properties": {
            "dimensions_cm_each_plank": "200x15x3",
            "finish": "planed_smooth",
            "nail_holding_ability": "good",
            "stain_affinity": "excellent",
            "uses": ["fine_furniture", "weapon_hafts", "ship_decking", "heavy_doors"]
        }
    },
    {
        "name": "Ash Wood Branches (Bundle)",
        "description": "Flexible ash wood branches from pruned trees. Excellent for tool handles due to shock resistance.",
        "material_type": MaterialType.WOOD_RAW,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 4.0,
        "is_craftable": False,
        "source_tags": ["pruned_verdant_frontier_ash_trees_tool_handles", "flexible_strong_wood"],
        "illicit_in_regions": [],
        "properties": {
            "processes_into": "Ash Staves_Tool Handles",
            "flexibility": "high",
            "shock_resistance": "excellent",
            "workability": "good",
            "uses_raw": ["temporary_tool_handles", "kindling"]
        }
    },
    {
        "name": "Ironwood Log (Small)",
        "description": "A rare log of ironwood from the deep forests. Extremely hard and dense, favored by orcs for weapons.",
        "material_type": MaterialType.WOOD_RAW,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 30.0,
        "is_craftable": False,
        "source_tags": ["harvested_deep_whispering_woods_ironwood_trees_orcish_preference", "extremely_hard_wood"],
        "illicit_in_regions": [],
        "properties": {
            "processes_into": "Ironwood Planks_Ironwood Blocks",
            "density_kg_m3": 950,
            "hardness_janka_lbf": 3200,
            "workability": "very_difficult_blunts_tools",
            "strength": "exceptional",
            "uses": ["weapon_hafts", "fortifications"]
        }
    },
    {
        "name": "Ironwood Planks (Single)",
        "description": "A single plank of processed ironwood. Incredibly hard and impact-resistant but difficult to work with.",
        "material_type": MaterialType.WOOD_PROCESSED,
        "rarity": Rarity.RARE,
        "base_value": 70,
        "weight": 8.0,
        "is_craftable": True,
        "source_tags": ["milled_ironwood_log_orcish_master_carpenter_rivemark", "premium_impact_resistant_wood"],
        "illicit_in_regions": [],
        "properties": {
            "dimensions_cm_plank": "150x20x4",
            "finish": "rough_difficult_to_plane",
            "nail_holding_ability": "poor_requires_drilling",
            "uses": ["heavy_weapon_components", "shield_cores", "reinforced_structures"]
        }
    },
    {
        "name": "Lethandrel Spiritwood Branch",
        "description": "A mana-infused branch from ancient spirit trees. Glows faintly and conducts magical energy.",
        "material_type": MaterialType.WOOD_MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 400,
        "weight": 1.5,
        "is_craftable": False,
        "source_tags": ["ethically_harvested_lethandrel_ancient_spirit_trees_elven_ritual", "mana_infused_wood"],
        "illicit_in_regions": ["Stonewake_unlicensed"],
        "properties": {
            "processes_into": "Spiritwood Wand_Staff Core_Enchanted Carvings",
            "mana_conductivity": "high",
            "natural_wards": "minor_vs_undead_corruption",
            "workability": "easy_responds_to_elven_tools_chants",
            "glows_faintly": True
        }
    },
    {
        "name": "Shimmering Marshes Mangrove Root",
        "description": "Water-logged mangrove root from the marshes. Naturally resistant to rot and salt water.",
        "material_type": MaterialType.WOOD_RAW,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 8.0,
        "is_craftable": False,
        "source_tags": ["harvested_shimmering_marshes_mangrove_water_logged_wood", "rot_resistant_wood"],
        "illicit_in_regions": [],
        "properties": {
            "processes_into": "Mangrove Planks_Carved Fetishes",
            "water_resistance": "very_high",
            "salt_resistance": "high",
            "workability": "moderate_stringy_fibers",
            "density": "medium_light_when_dried",
            "uses": ["boat_parts", "dock_pilings"]
        }
    },
    {
        "name": "Petrified Wood Chunk",
        "description": "Ancient fossilized wood that has turned to stone. Extremely durable but requires special tools to work.",
        "material_type": MaterialType.WOOD_MINERAL,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 5.0,
        "is_craftable": False,
        "source_tags": ["found_ember_wastes_ancient_forest_remains_fossilized_wood", "stone_like_wood"],
        "illicit_in_regions": [],
        "properties": {
            "processes_into": "Petrified Wood Carvings_Inlays",
            "hardness_mohs": 7,
            "workability": "difficult_requires_stone_tools_or_magic",
            "appearance": "polished_stone_wood_grain",
            "uses": ["durable_ornaments", "weapon_pommels"]
        }
    },
    {
        "name": "Whispering Birch Planks",
        "description": "Silvery white planks with a soft, almost luminous appearance. Favored by Lethandrel elves for musical instruments.",
        "material_type": MaterialType.WOOD_PROCESSED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 18,
        "weight": 4.0,
        "is_craftable": True,
        "source_tags": ["milled_whispering_woods_birch", "lethandrel_acoustically_tested", "instrument_grade"],
        "illicit_in_regions": [],
        "properties": {
            "dimensions_cm_each_plank": "180x15x1.5",
            "finish": "fine_sanded",
            "acoustic_resonance": "high",
            "accepts_finish": "extremely_well",
            "mana_conductivity": "low_trace",
            "appearance": "silvery_pale"
        }
    },
    # Adhesives, Finishes & Fasteners (Wood Specific)
    {
        "name": "Pine Resin (Lump)",
        "description": "Natural resin tapped from pine trees. Useful for waterproofing and as a crude adhesive.",
        "material_type": MaterialType.RESIN,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["tapped_pine_trees_verdant_frontier", "sticky_natural_adhesive_waterproofer"],
        "illicit_in_regions": [],
        "properties": {
            "use": "crude_adhesive_waterproofing_torches",
            "melting_point_celsius": 70,
            "flammability": "high",
            "processed_into": "Pine Tar_Pitch"
        }
    },
    {
        "name": "Animal Hide Glue (Pot)",
        "description": "Traditional wood glue made from rendered animal hides and bones. Strong but brittle when dry.",
        "material_type": MaterialType.ADHESIVE,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["rendered_animal_hides_bones_traditional_wood_glue", "strong_brittle_glue"],
        "illicit_in_regions": [],
        "properties": {
            "bond_strength_psi": 3000,
            "shelf_life_prepared_days": 7,
            "application_method": "hot_brush",
            "water_resistance": "low",
            "reversibility": "with_heat_moisture"
        }
    },
    {
        "name": "Beeswax Polish (Tin)",
        "description": "Natural wood finish made from beeswax and linseed oil. Provides water resistance and enhances grain.",
        "material_type": MaterialType.FINISH,
        "rarity": Rarity.UNCOMMON,
        "base_value": 8,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["beeswax_linseed_oil_blend_human_craft", "natural_wood_finish_and_protector"],
        "illicit_in_regions": [],
        "properties": {
            "finish_type": "soft_sheen_water_resistant",
            "application_method": "cloth_buff",
            "drying_time_hours": 2,
            "scent": "honey_mild",
            "enhances_wood_grain": True
        }
    },
    {
        "name": "Elven Moonpetal Varnish (Vial)",
        "description": "Magical varnish that enhances mana conductivity and provides minor warding. Must be applied under moonlight.",
        "material_type": MaterialType.FINISH_MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["lethandrel_alchemical_preparation_moonpetal_essence_tree_saps", "magically_protective_finish"],
        "illicit_in_regions": [],
        "properties": {
            "finish_type": "hard_clear_magically_resonant",
            "application_method": "fine_brush_moonlight_curing",
            "drying_time_hours": "12_under_moon",
            "enhances_mana_conductivity_of_wood": True,
            "minor_warding_properties": True
        }
    },
    {
        "name": "Wooden Dowels (Bag of 50)",
        "description": "Traditional hardwood pegs for joinery. Metal-free fastening method preferred by some craftsmen.",
        "material_type": MaterialType.FASTENER_WOOD,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["turned_hardwood_pegs_joinery_component", "metal_free_fastening"],
        "illicit_in_regions": [],
        "properties": {
            "material": "oak_birch",
            "diameter_mm": 8,
            "length_cm": 5,
            "strength": "good_in_shear",
            "quantity": 50,
            "use": "furniture_joinery_reinforcement"
        }
    },
    {
        "name": "Iron Wood Screws (Box of 20)",
        "description": "Threaded iron screws designed for wood construction. Prone to rust if not properly maintained.",
        "material_type": MaterialType.FASTENER_METAL,
        "rarity": Rarity.COMMON,
        "base_value": 4,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["forged_iron_threaded_screws_skarport_smithies", "strong_wood_fasteners"],
        "illicit_in_regions": [],
        "properties": {
            "material": "iron",
            "length_cm": 4,
            "thread_type": "coarse_wood",
            "head_type": "flat_slot",
            "quantity": 20,
            "rust_prone": "true_if_not_oiled"
        }
    }
]

# Tailoring & Leatherworking Materials
TAILORING_MATERIALS = [
    # Fibers & Cloths
    {
        "name": "Roughspun Linen Bolt (10m)",
        "description": "Coarse linen fabric with visible weave. Durable but not especially comfortable until broken in.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.COMMON,
        "base_value": 5,
        "weight": 1.0,
        "is_craftable": True,
        "source_tags": ["processed_flax_verdant_frontier_farms", "basic_textile"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "low",
            "durability": "medium_low",
            "comfort": "scratchy_initially",
            "dye_affinity": "good_natural_dyes",
            "insulation_value": "low",
            "length_meters": 10
        }
    },
    {
        "name": "Cotton Bolt (10m)",
        "description": "Soft cotton fabric from delta plantations. Breathable and comfortable, with excellent dye affinity.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.COMMON,
        "base_value": 8,
        "weight": 0.8,
        "is_craftable": True,
        "source_tags": ["harvested_cotton_rivemark_delta_plantations", "soft_common_textile"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "medium",
            "durability": "medium",
            "comfort": "good",
            "dye_affinity": "excellent",
            "breathability": "high",
            "length_meters": 10
        }
    },
    {
        "name": "Woolsey (5m)",
        "description": "Sturdy wool-linen blend fabric suitable for commoner clothing. Practical rather than luxurious.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.COMMON,
        "base_value": 8,
        "weight": 1.2,
        "is_craftable": True,
        "source_tags": ["rivemark_textile_guild_standard", "everyday_garment_material"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "medium",
            "durability": "medium_high",
            "comfort": "modest",
            "insulation_value": "medium",
            "water_resistance": "low",
            "length_meters": 5
        }
    },
    {
        "name": "Woolen Cloth Bolt (Heavy, 5m)",
        "description": "Thick wool from highland sheep. Provides excellent insulation and natural water resistance.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 1.5,
        "is_craftable": True,
        "source_tags": ["sheared_highland_sheep_crystal_highlands_processed_human_settlements", "warm_textile"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "medium_thick",
            "durability": "high",
            "comfort": "good_itchy_if_coarse",
            "dye_affinity": "good",
            "insulation_value": "high_water_resistant_naturally",
            "length_meters": 5
        }
    },
    {
        "name": "Skarport Merchant's Silk (5m)",
        "description": "Luxurious silk fabric imported and processed by Skarport guilds. A status symbol among the wealthy.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.RARE,
        "base_value": 70,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["imported_silkworm_cocoons_processed_skarport_guilds", "luxury_textile"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "very_high_fine",
            "durability": "medium_delicate",
            "comfort": "excellent_smooth",
            "dye_affinity": "superb_vibrant_colors",
            "insulation_value": "medium_surprisingly_warm",
            "length_meters": 5,
            "status_symbol": True
        }
    },
    {
        "name": "Lethandrel Spider-Silk Thread (Spool)",
        "description": "Magical thread spun from mana-infused spiders. Incredibly strong for its weight and conducts mana.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 200,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["harvested_lethandrel_mana_infused_spiders_whispering_woods_elven_collection", "magical_fiber"],
        "illicit_in_regions": [],
        "properties": {
            "strength_to_weight_ratio": "extremely_high",
            "mana_conductivity": "low_but_stable",
            "durability": "exceptional",
            "use": "enchanted_clothing_bowstrings_suture_thread",
            "length_meters_per_spool": 50
        }
    },
    {
        "name": "Beastfolk Woven Reed Matting (Large)",
        "description": "Woven reed matting from marsh reeds. Rugged material good for backing crude armor or floor mats.",
        "material_type": MaterialType.PLANT_FIBER,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 2.0,
        "is_craftable": True,
        "source_tags": ["harvested_shimmering_marshes_reeds_beastfolk_weaving_ashkar_vale", "rugged_natural_material"],
        "illicit_in_regions": [],
        "properties": {
            "durability": "good_for_mats_crude_armor_backing",
            "comfort": "rough",
            "water_resistance": "moderate",
            "insulation_value": "low",
            "size": "2x2_meters"
        }
    },
    {
        "name": "Ferverl Desert Linen (Heat-Treated, 5m)",
        "description": "Specially processed linen from Thal-Zirad that provides excellent heat protection and breathability.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.RARE,
        "base_value": 40,
        "weight": 0.7,
        "is_craftable": True,
        "source_tags": ["thal_zirad_flax_processed_ferverl_heat_ritual", "heat_resistant_breathable_cloth"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "medium_fine",
            "durability": "good",
            "comfort": "excellent_in_heat",
            "dye_affinity": "poor_resists_most_dyes",
            "insulation_value_vs_heat": "high",
            "length_meters": 5
        }
    },
    {
        "name": "Canvas Bolt (Heavy Duty, 5m)",
        "description": "Thick, coarse fabric ideal for sails, tents, and heavy-duty applications. Very durable but stiff.",
        "material_type": MaterialType.CLOTH,
        "rarity": Rarity.UNCOMMON,
        "base_value": 12,
        "weight": 2.0,
        "is_craftable": True,
        "source_tags": ["thick_hemp_or_cotton_weave_rivemark_sailmakers_skarport_docks", "tough_utility_fabric"],
        "illicit_in_regions": [],
        "properties": {
            "thread_count": "very_thick_coarse",
            "durability": "very_high_abrasion_resistant",
            "comfort": "low_stiff",
            "water_resistance": "good_if_waxed",
            "uses": ["sails", "tents", "heavy_bags", "workwear"],
            "length_meters": 5
        }
    },
    # Leathers & Hides
    {
        "name": "Raw Deer Hide (Medium)",
        "description": "Untreated hide from a deer, still requiring tanning. Must be preserved quickly to prevent spoilage.",
        "material_type": MaterialType.HIDE,
        "rarity": Rarity.COMMON,
        "base_value": 4,
        "weight": 1.5,
        "is_craftable": False,
        "source_tags": ["hunted_verdant_frontier_deer", "untanned_animal_skin"],
        "illicit_in_regions": [],
        "properties": {
            "tans_into": "Buckskin Leather",
            "size_approx_sq_meters": 1.5,
            "quality_potential": "medium",
            "preservation_needed_quickly": True
        }
    },
    {
        "name": "Buckskin Leather (Medium Piece)",
        "description": "Soft, supple leather tanned from deer hide. Versatile material suitable for clothing and light gear.",
        "material_type": MaterialType.LEATHER,
        "rarity": Rarity.COMMON,
        "base_value": 10,
        "weight": 0.7,
        "is_craftable": True,
        "source_tags": ["tanned_deer_hide_human_beastfolk_craft", "soft_flexible_leather"],
        "illicit_in_regions": [],
        "properties": {
            "thickness_mm": 1.5,
            "flexibility": "high",
            "durability": "medium",
            "comfort": "good",
            "water_resistance": "low_unless_treated",
            "uses": ["light_armor", "clothing", "pouches"]
        }
    },
    {
        "name": "Boar Hide (Tough)",
        "description": "Thick, bristly hide from wild boar. Requires bristle removal but tans into very tough leather.",
        "material_type": MaterialType.HIDE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 12,
        "weight": 2.5,
        "is_craftable": False,
        "source_tags": ["hunted_whispering_woods_boar_rivemark_farmland_pest", "thick_bristly_hide"],
        "illicit_in_regions": [],
        "properties": {
            "tans_into": "Tough Boar Leather",
            "size_approx_sq_meters": 1.2,
            "quality_potential": "medium_high_scarring_common",
            "bristle_removal_required": True
        }
    },
    {
        "name": "Tough Boar Leather (Piece)",
        "description": "Rigid, protective leather from boar hide. Favored by orcs for its impact resistance but requires padding.",
        "material_type": MaterialType.LEATHER,
        "rarity": Rarity.UNCOMMON,
        "base_value": 25,
        "weight": 1.2,
        "is_craftable": True,
        "source_tags": ["tanned_boar_hide_orcish_preference", "rigid_protective_leather"],
        "illicit_in_regions": [],
        "properties": {
            "thickness_mm": 3,
            "flexibility": "low",
            "durability": "high_impact_resistant",
            "comfort": "low_requires_padding",
            "uses": ["medium_armor_jackets", "shield_facings", "tool_sheaths"]
        }
    },
    {
        "name": "Giant Lizard Scale Hide (Large)",
        "description": "Scaled hide from ember wastes sand lizards. Natural scales provide armor-like protection.",
        "material_type": MaterialType.EXOTIC_HIDE,
        "rarity": Rarity.RARE,
        "base_value": 60,
        "weight": 3.0,
        "is_craftable": False,
        "source_tags": ["hunted_ember_wastes_sand_lizard_beastfolk_ferverl_hunt", "scaled_reptilian_hide"],
        "illicit_in_regions": [],
        "properties": {
            "tans_into": "Scaled Leather",
            "size_approx_sq_meters": 2.0,
            "scale_hardness": "medium",
            "flexibility_between_scales": "good",
            "heat_resistance": "good"
        }
    },
    {
        "name": "Scaled Leather (Large Piece)",
        "description": "Naturally armored leather with intact scales. Provides good pierce resistance while maintaining flexibility.",
        "material_type": MaterialType.EXOTIC_LEATHER,
        "rarity": Rarity.RARE,
        "base_value": 120,
        "weight": 1.4,
        "is_craftable": True,
        "source_tags": ["tanned_lizard_scale_hide_ashkar_vale_specialty", "naturally_armored_leather"],
        "illicit_in_regions": [],
        "properties": {
            "thickness_mm_scales": 4,
            "flexibility": "medium",
            "durability": "high_good_pierce_resistance",
            "comfort": "medium_can_be_stiff",
            "uses": ["exotic_armor", "decorative_pieces", "helmets"]
        }
    },
    {
        "name": "Shadow Panther Pelt (Prime)",
        "description": "Rare pelt from a master shadow panther. Retains magical properties that blend with shadows.",
        "material_type": MaterialType.EXOTIC_HIDE,
        "rarity": Rarity.EPIC,
        "base_value": 350,
        "weight": 1.0,
        "is_craftable": False,
        "source_tags": ["hunted_whispering_woods_master_shadow_panther_elven_beastfolk_stalkers", "magically_infused_pelt"],
        "illicit_in_regions": [],
        "properties": {
            "tans_into": "Shadow-Walker Leather",
            "size_approx_sq_meters": 1.0,
            "innate_property": "blends_with_shadows",
            "fur_quality": "exceptional_soft_dark",
            "magical_aura": "faint_illusion"
        }
    },
    {
        "name": "Shadow-Walker Leather (Piece)",
        "description": "Legendary leather that grants stealth abilities. Crafted through secret elven processes from shadow panther pelts.",
        "material_type": MaterialType.EXOTIC_LEATHER,
        "rarity": Rarity.LEGENDARY,
        "base_value": 700,
        "weight": 0.4,
        "is_craftable": True,
        "source_tags": ["tanned_shadow_panther_pelt_secret_elven_process", "leather_of_stealth_and_night"],
        "illicit_in_regions": [],
        "properties": {
            "thickness_mm": 1,
            "flexibility": "very_high",
            "durability": "good_magically_resilient",
            "comfort": "superb",
            "innate_ability": "minor_stealth_bonus_in_dim_light",
            "enchantment_affinity": "illusion_shadow_magic"
        }
    },
    {
        "name": "Crude Beastfolk Hide Scraps",
        "description": "Mixed quality hide scraps from various beasts. Useful for padding and repairs but little else.",
        "material_type": MaterialType.HIDE,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.5,
        "is_craftable": False,
        "source_tags": ["butchering_byproduct_ashkar_vale_various_beasts", "untanned_mixed_quality_scraps"],
        "illicit_in_regions": [],
        "properties": {
            "tans_into": "Rough Patchwork Leather",
            "size_approx_sq_meters": "variable_small_pieces",
            "usability": "low_good_for_bindings_padding_filler"
        }
    },
    {
        "name": "Rough Patchwork Leather",
        "description": "Low-grade leather stitched from various hide scraps. Prone to tearing but functional for basic needs.",
        "material_type": MaterialType.LEATHER,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["tanned_stitched_hide_scraps_beastfolk_utility_craft", "low_grade_functional_leather"],
        "illicit_in_regions": [],
        "properties": {
            "thickness_mm": "variable",
            "flexibility": "medium",
            "durability": "low_prone_to_tearing_at_seams",
            "comfort": "poor",
            "uses": ["crude_pouches", "armor_padding", "tent_repairs"]
        }
    },
    # Threads, Fasteners & Dyes
    {
        "name": "Linen Thread Spool (100m)",
        "description": "Standard linen thread for basic sewing and repairs. Natural undyed color.",
        "material_type": MaterialType.THREAD,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["spun_flax_fibers_common_sewing_thread"],
        "illicit_in_regions": [],
        "properties": {
            "tensile_strength_kg": 2,
            "thickness": "standard",
            "color": "natural_undyed",
            "length_meters": 100
        }
    },
    {
        "name": "Heavy Woolen Yarn (50m)",
        "description": "Thick yarn spun from wool fibers. Good for knitting and heavy stitching work.",
        "material_type": MaterialType.THREAD,
        "rarity": Rarity.UNCOMMON,
        "base_value": 5,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["spun_wool_fibers_thick_yarn_for_knitting_heavy_stitching"],
        "illicit_in_regions": [],
        "properties": {
            "tensile_strength_kg": 5,
            "thickness": "thick",
            "color": "natural_undyed_cream",
            "length_meters": 50,
            "insulating_when_stitched": True
        }
    },
    {
        "name": "Sinew Thread (Dried, 20m)",
        "description": "Strong thread made from processed animal tendons. Shrinks when drying, creating very tight seams.",
        "material_type": MaterialType.THREAD,
        "rarity": Rarity.UNCOMMON,
        "base_value": 8,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["processed_animal_tendons_beastfolk_orcish_craft_strong_natural_thread"],
        "illicit_in_regions": [],
        "properties": {
            "tensile_strength_kg": 10,
            "thickness": "medium_variable",
            "color": "brownish_translucent",
            "length_meters": 20,
            "water_resistance_swells_when_wet": True,
            "notes": "Shrinks as it dries, making tight seams."
        }
    },
    {
        "name": "Silk Thread Spool (Gilded, 20m)",
        "description": "Luxurious silk thread infused with gold dust. Used for decorative embroidery and minor enchantments.",
        "material_type": MaterialType.THREAD,
        "rarity": Rarity.RARE,
        "base_value": 30,
        "weight": 0.005,
        "is_craftable": True,
        "source_tags": ["skarport_silk_thread_infused_with_gold_dust_decorative_embroidery"],
        "illicit_in_regions": [],
        "properties": {
            "tensile_strength_kg": 1,
            "thickness": "very_fine",
            "color": "gold_shimmer",
            "length_meters": 20,
            "decorative_only": True,
            "enchantment_conduit_minor": True
        }
    },
    {
        "name": "Wooden Buttons (Dozen)",
        "description": "Simple wooden buttons carved from common wood. Basic but functional clothing fasteners.",
        "material_type": MaterialType.FASTENER,
        "rarity": Rarity.COMMON,
        "base_value": 1,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["carved_common_wood_simple_clothing_fasteners"],
        "illicit_in_regions": [],
        "properties": {
            "material": "ash_pine",
            "size_mm": 15,
            "durability": "medium_can_split",
            "quantity": 12
        }
    },
    {
        "name": "Bone Toggles (Half Dozen)",
        "description": "Polished bone toggles in beastfolk style. Rugged fasteners for tribal and rustic clothing.",
        "material_type": MaterialType.FASTENER,
        "rarity": Rarity.UNCOMMON,
        "base_value": 4,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["carved_polished_animal_bone_beastfolk_ashkar_vale_style", "rugged_fasteners"],
        "illicit_in_regions": [],
        "properties": {
            "material": "deer_boar_bone",
            "size_mm_length": 30,
            "durability": "high_can_chip",
            "quantity": 6,
            "style": "tribal_rustic"
        }
    },
    {
        "name": "Bronze Clasps (Pair)",
        "description": "Decorative bronze clasps with interlocking mechanism. Sturdy fasteners for cloaks and armor.",
        "material_type": MaterialType.FASTENER,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.03,
        "is_craftable": True,
        "source_tags": ["cast_bronze_fittings_skarport_human_craft", "sturdy_decorative_clasps_for_cloaks_armor"],
        "illicit_in_regions": [],
        "properties": {
            "material": "bronze",
            "size_mm_each": "25x40",
            "durability": "very_good",
            "mechanism": "hook_and_eye_interlocking",
            "quantity": 2
        }
    },
    {
        "name": "Madder Root Dye (Red Pigment)",
        "description": "Natural red dye processed from madder root. Produces rustic red and orange tones.",
        "material_type": MaterialType.DYE,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["processed_madder_root_verdant_frontier_natural_dye"],
        "illicit_in_regions": [],
        "properties": {
            "color_imparted": "rustic_red_orange_tones",
            "fabric_suitability": ["linen", "cotton", "wool"],
            "permanence": "good_fades_slowly_with_sun",
            "quantity_sufficient_for_bolt_of_cloth": 1
        }
    },
    {
        "name": "Indigo Leaf Paste (Blue Pigment)",
        "description": "Rich blue dye from fermented indigo leaves. Produces deep blue to sky blue colors with excellent permanence.",
        "material_type": MaterialType.DYE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 8,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["fermented_indigo_leaves_rivemark_specialty_crop", "rich_blue_dye"],
        "illicit_in_regions": [],
        "properties": {
            "color_imparted": "deep_blue_to_sky_blue_depending_on_concentration",
            "fabric_suitability": ["cotton", "silk", "linen"],
            "permanence": "excellent",
            "quantity_sufficient_for_bolt_of_cloth": 1
        }
    },
    {
        "name": "Soot Black Pigment Pouch",
        "description": "Basic black dye made from purified soot. Produces dull black and greyish tones.",
        "material_type": MaterialType.DYE,
        "rarity": Rarity.COMMON,
        "base_value": 2,
        "weight": 0.03,
        "is_craftable": True,
        "source_tags": ["collected_fine_soot_purified_basic_black_dye"],
        "illicit_in_regions": [],
        "properties": {
            "color_imparted": "dull_black_greyish_tones",
            "fabric_suitability": ["wool", "rough_leathers"],
            "permanence": "medium_can_rub_off",
            "quantity_sufficient_for_garment_or_leather_piece": 1
        }
    }
]

# Jewelcrafting & Gemcutting Materials
JEWELCRAFTING_MATERIALS = [
    # Raw Gemstones & Crystals
    {
        "name": "Rough Quartz Crystal",
        "description": "An uncut crystal of quartz with translucent white appearance. Common but useful for basic gem crafting.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["mined_crystal_highlands_common_geodes", "rivemark_riverbed_finds"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Clear Quartz Cabochon", "Faceted Quartz Gem"],
            "hardness_mohs": 7,
            "clarity_potential": "variable_included_to_flawless",
            "carat_potential_avg": 5,
            "mana_focus_potential": "very_low_unless_perfectly_clear"
        }
    },
    {
        "name": "Uncut Amethyst Geode",
        "description": "A beautiful geode containing amethyst crystals. When opened, reveals varying grades of purple crystals suitable for cutting.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["dwarven_mine_stonewake_geode_veins", "volcanic_rock_cavities"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Faceted Amethyst", "Amethyst Drusy Piece"],
            "hardness_mohs": 7,
            "color_intensity_potential": "pale_lilac_to_deep_purple",
            "carat_potential_avg_per_crystal": 2,
            "spiritual_affinity_calm": True
        }
    },
    {
        "name": "Raw Garnet Nodule",
        "description": "An unpolished garnet showing deep red coloration. Found in metamorphic rocks of the Ember Wastes.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 0.03,
        "is_craftable": False,
        "source_tags": ["metamorphic_rock_ember_wastes_alluvial_deposits", "deep_red_gemstone"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Faceted Garnet", "Garnet Cabochon"],
            "hardness_mohs": 7.5,
            "color_variety": ["deep_red_almandine_pyrope", "orange_spessartine_rare"],
            "carat_potential_avg": 3,
            "fire_element_trace_affinity": True
        }
    },
    {
        "name": "Flawed Emerald Chunk",
        "description": "Raw emerald with visible inclusions and fractures. Still valuable despite flaws due to emerald's rarity.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.RARE,
        "base_value": 80,
        "weight": 0.02,
        "is_craftable": False,
        "source_tags": ["lethandrel_hidden_groves_pegmatite_veins_elven_mined", "green_beryl_variety_included"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Faceted Emerald (Included)", "Emerald Cabochon (Opaque)"],
            "hardness_mohs": 7.5,
            "clarity_potential": "heavily_included_to_moderately_included",
            "carat_potential_avg": 1.5,
            "nature_magic_affinity": True
        }
    },
    {
        "name": "Star Ruby (Unpolished)",
        "description": "A rare ruby with silk inclusions that create asterism when properly cut. Legendary quality gemstone.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.EPIC,
        "base_value": 400,
        "weight": 0.01,
        "is_craftable": False,
        "source_tags": ["thal_zirad_legendary_sand_ruby_mines_ferverl_guarded", "asterism_phenomenon_potential"],
        "illicit_in_regions": ["Skarport_unlicensed_trade"],
        "properties": {
            "cuts_into": ["Star Ruby Cabochon"],
            "hardness_mohs": 9,
            "clarity_potential": "translucent_with_silk_inclusions",
            "carat_potential_avg": 2,
            "phenomenal_property": "asterism_6_ray_star_if_cut_correctly",
            "fire_sun_affinity_strong": True
        }
    },
    {
        "name": "Raw Diamond Crystal (Industrial)",
        "description": "Off-color diamond with inclusions. Too flawed for fine jewelry but valuable for cutting tools and abrasives.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.RARE,
        "base_value": 150,
        "weight": 0.005,
        "is_craftable": False,
        "source_tags": ["dwarven_deep_kimberlite_pipes_stonewake", "hardest_natural_substance_off_color_included"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Industrial Diamond Grit", "Small Faceted Diamond (Off-Color)"],
            "hardness_mohs": 10,
            "clarity_potential": "heavily_included_yellowish_brownish",
            "carat_potential_avg": 0.5,
            "use": ["cutting_tools", "abrasives"]
        }
    },
    {
        "name": "Gem-Quality Diamond Octahedron",
        "description": "An exceptionally rare flawless diamond in perfect octahedral crystal form. Symbol of ultimate wealth and power.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.LEGENDARY,
        "base_value": 2000,
        "weight": 0.002,
        "is_craftable": False,
        "source_tags": ["legendary_dwarven_motherlode_stonewake_once_a_generation_find", "perfect_crystal_structure"],
        "illicit_in_regions": ["Crucible Spire_Accord_Tax_Evasion"],
        "properties": {
            "cuts_into": ["Brilliant Cut Diamond (Flawless)"],
            "hardness_mohs": 10,
            "clarity_potential": "internally_flawless_to_vvs",
            "carat_potential_avg": 1,
            "light_refraction_index": "exceptional",
            "symbol_of_power_wealth": True
        }
    },
    {
        "name": "Mana-Charged Geode Fragment",
        "description": "Crystallized ley energy formed during mana storms. Pulsates with raw magical power but unstable without proper setting.",
        "material_type": MaterialType.GEM_MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 300,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["crucible_spire_mana_storm_aftermath_crystalized_ley_energy", "pulsating_raw_mana_crystal"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Mana Crystal Focus", "Charged Crystal Shard"],
            "hardness_mohs": "variable_5_8",
            "mana_type_attunement": "random_or_dominant_leyline_type",
            "energy_output_passive_mu_per_hour": 5,
            "stability": "low_decays_if_not_set"
        }
    },
    {
        "name": "Ember Garnet (Rough)",
        "description": "Fiery red garnet with orange highlights. Found in the volcanic soils of the Ember Wastes.",
        "material_type": MaterialType.GEM_RAW,
        "rarity": Rarity.UNCOMMON,
        "base_value": 25,
        "weight": 0.03,
        "is_craftable": False,
        "source_tags": ["mined_ember_wastes_volcanic_soil", "fire_affinity"],
        "illicit_in_regions": [],
        "properties": {
            "cuts_into": ["Ember Garnet Cabochon", "Faceted Ember Garnet"],
            "hardness_mohs": 7.5,
            "clarity_potential": "high",
            "carat_potential_avg": 2,
            "magical_resonance": "fire_elements",
            "appearance": "deep_red_orange_highlights"
        }
    },
    # Precious Metals for Jewelry
    {
        "name": "Silver Jewelry Bar (92.5% Pure)",
        "description": "Sterling silver ingot specifically alloyed for jewelry making. Maintains shine while offering good durability.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.UNCOMMON,
        "base_value": 200,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["refined_silver_ingot_alloyed_copper_sterling_standard", "skarport_jewelers_supply"],
        "illicit_in_regions": [],
        "properties": {
            "purity_karat_equivalent": "sterling",
            "malleability": "high",
            "tarnish_resistance": "medium",
            "melting_point_celsius": 961,
            "common_uses": ["rings", "chains", "settings_for_soft_gems"]
        }
    },
    {
        "name": "Gold Jewelry Ingot (18k Yellow)",
        "description": "High-quality gold alloy suitable for fine jewelry work. Warm yellow color with excellent workability.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.RARE,
        "base_value": 1500,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["refined_gold_ingot_alloyed_silver_copper_durable_gold_standard", "human_elven_luxury_craft"],
        "illicit_in_regions": [],
        "properties": {
            "purity_karat_equivalent": "18k_75_percent_gold",
            "malleability": "good",
            "tarnish_resistance": "excellent",
            "melting_point_celsius": 900,
            "color": "rich_yellow",
            "common_uses": ["high_value_jewelry", "intricate_settings"]
        }
    },
    {
        "name": "Platinum Wire (Pure, 10cm)",
        "description": "Ultra-refined platinum wire for the most exclusive jewelry work. Inert and corrosion-resistant.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.EPIC,
        "base_value": 500,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["ultra_refined_rare_platinum_group_metals_dwarven_master_refiners", "elite_jewelry_material"],
        "illicit_in_regions": [],
        "properties": {
            "purity_karat_equivalent": "999_fine",
            "malleability": "good_but_dense",
            "tarnish_resistance": "superior_inert",
            "melting_point_celsius": 1768,
            "color": "bright_silvery_white",
            "uses": ["secure_settings_for_diamonds_rare_gems"]
        }
    },
    {
        "name": "Electrum Leaf (Thin Sheet)",
        "description": "Beaten electrum formed into delicate leaves for gilding and decorative inlays. Extremely fragile but beautiful.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.RARE,
        "base_value": 150,
        "weight": 0.001,
        "is_craftable": True,
        "source_tags": ["beaten_electrum_ingot_elven_gilding_technique", "decorative_metal_leaf"],
        "illicit_in_regions": [],
        "properties": {
            "thickness_microns": 1,
            "alloy_composition": "gold_silver_variable",
            "use": "gilding_inlays_on_jewelry_and_art_objects",
            "fragility": "very_high_handle_with_care"
        }
    },
    {
        "name": "Rose Gold Pellets (Casting)",
        "description": "Small pellets of rose gold alloy optimized for casting jewelry. Popular for its warm, romantic coloration.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.RARE,
        "base_value": 1250,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["alloyed_gold_copper_silver_trace_casting_granules", "fashionable_warm_toned_gold"],
        "illicit_in_regions": [],
        "properties": {
            "purity_karat_equivalent": "14k_to_18k_typical",
            "malleability": "good",
            "casting_fluidity": "excellent",
            "color": "pinkish_red_hue",
            "uses": ["cast_jewelry_settings_decorative_elements"]
        }
    },
    # Tools, Findings & Consumables
    {
        "name": "Jeweler's Saw Blades (Dozen)",
        "description": "Ultra-fine toothed blades for precision cutting of precious metals and soft gemstones. Break easily under stress.",
        "material_type": MaterialType.TOOL_PART,
        "rarity": Rarity.COMMON,
        "base_value": 5,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["fine_toothed_steel_blades_skarport_toolmaker", "for_cutting_metal_and_soft_gems"],
        "illicit_in_regions": [],
        "properties": {
            "blade_thickness_mm": 0.2,
            "teeth_per_inch": 80,
            "material": "hardened_steel",
            "fragility": "high_snap_easily",
            "quantity": 12
        }
    },
    {
        "name": "Gem Cutting Dop Sticks (Set of 5)",
        "description": "Wooden rods with wax cups for securely holding gemstones during cutting and polishing operations.",
        "material_type": MaterialType.TOOL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 10,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["wooden_or_metal_rods_with_wax_cup_for_holding_gems_during_cutting", "lapidary_tool"],
        "illicit_in_regions": [],
        "properties": {
            "sizes_included": ["small_medium_large_cabochon_facet"],
            "material": "hardwood_brass",
            "wax_type_required": "Dop_Wax"
        }
    },
    {
        "name": "Dop Wax (Cake)",
        "description": "Thermoplastic wax blend for securing gems to dop sticks during cutting. Can be remelted and reused multiple times.",
        "material_type": MaterialType.CONSUMABLE,
        "rarity": Rarity.COMMON,
        "base_value": 3,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["beeswax_shellac_resin_blend_jewelers_adhesive_for_dop_sticks", "thermoplastic_adhesive"],
        "illicit_in_regions": [],
        "properties": {
            "melting_point_celsius": 60,
            "adhesion_strength": "good_for_gems",
            "reusability": "high_can_be_remelted",
            "color": "dark_brown_or_green"
        }
    },
    {
        "name": "Diamond Dust (Abrasive Grade)",
        "description": "Crushed industrial diamonds used as abrasive for polishing the hardest gemstones. Essential for diamond cutting.",
        "material_type": MaterialType.GEM_PROCESSED,
        "rarity": Rarity.RARE,
        "base_value": 50,
        "weight": 0.001,
        "is_craftable": True,
        "source_tags": ["crushed_industrial_diamonds_lapidary_abrasive_for_hard_gems", "ultra_hard_polishing_agent"],
        "illicit_in_regions": [],
        "properties": {
            "grit_size_microns": "variable_1_to_50",
            "use": "grinding_faceting_polishing_diamonds_rubies_sapphires",
            "application": "mixed_with_oil_on_lap_wheel"
        }
    },
    {
        "name": "Jeweler's Rouge (Polishing Bar)",
        "description": "Fine iron oxide compound in wax binder for achieving mirror polish on precious metals. Final finishing step.",
        "material_type": MaterialType.CONSUMABLE,
        "rarity": Rarity.UNCOMMON,
        "base_value": 8,
        "weight": 0.03,
        "is_craftable": True,
        "source_tags": ["fine_iron_oxide_powder_in_wax_binder_metal_polishing_compound", "final_polish_for_metals"],
        "illicit_in_regions": [],
        "properties": {
            "abrasive_type": "very_fine_ferric_oxide",
            "use": "high_mirror_polish_on_gold_silver_platinum",
            "color_imparted_residue": "reddish_brown_wash_off"
        }
    },
    {
        "name": "Silver Earring Hooks (10 Pairs)",
        "description": "Pre-formed sterling silver ear wires for earring construction. Standard jewelry findings for pierced ears.",
        "material_type": MaterialType.FINDING,
        "rarity": Rarity.COMMON,
        "base_value": 12,
        "weight": 0.01,
        "is_craftable": True,
        "source_tags": ["bent_silver_wire_basic_earring_component", "standard_jewelry_finding"],
        "illicit_in_regions": [],
        "properties": {
            "material": "sterling_silver",
            "gauge_mm": 0.8,
            "style": "french_hook_fish_hook",
            "quantity": 20
        }
    },
    {
        "name": "Gold Necklace Clasp (Lobster)",
        "description": "High-quality spring-loaded clasp for securing necklaces. Made from durable 14k gold alloy.",
        "material_type": MaterialType.FINDING,
        "rarity": Rarity.RARE,
        "base_value": 40,
        "weight": 0.005,
        "is_craftable": True,
        "source_tags": ["14k_gold_spring_loaded_clasp_secure_necklace_closure", "quality_jewelry_finding"],
        "illicit_in_regions": [],
        "properties": {
            "material": "14k_yellow_gold",
            "size_mm_length": 10,
            "mechanism": "spring_loaded_lobster_claw",
            "durability": "good"
        }
    },
    {
        "name": "Bezel Setting Strip (Silver, 10cm)",
        "description": "Thin silver strip for forming bezels around cabochon gemstones. Flexible enough to shape by hand.",
        "material_type": MaterialType.FINDING,
        "rarity": Rarity.UNCOMMON,
        "base_value": 15,
        "weight": 0.02,
        "is_craftable": True,
        "source_tags": ["thin_flat_silver_strip_for_forming_bezels_around_cabochons", "gem_setting_component"],
        "illicit_in_regions": [],
        "properties": {
            "material": "fine_silver_or_sterling",
            "width_mm": 3,
            "thickness_mm": 0.5,
            "length_cm": 10,
            "flexibility": "high_easy_to_form"
        }
    }
]

# Relicsmithing & Artifact Tinkering Materials
RELICSMITHING_MATERIALS = [
    # Unstable Relic Components & Dissonance Residue
    {
        "name": "Shattered War-Core Fragment",
        "description": "A dangerous fragment of a destroyed relic weapon core. Pulses with unstable crimson energy that threatens to corrupt its surroundings.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 800,
        "weight": 2.5,
        "is_craftable": False,
        "source_tags": ["crimson_dissonance_battlefield_excavation_crucible_spire_depths", "unstable_power_source"],
        "illicit_in_regions": ["Skarport", "Lethandrel_high_security"],
        "properties": {
            "energy_type": "raw_crimson_mana",
            "instability_level": 9,
            "potential_power_output_mw": "variable_1_to_100",
            "corruption_aura_radius_meters": 1,
            "decay_rate_outside_containment_percent_day": 5,
            "research_difficulty": "very_high"
        }
    },
    {
        "name": "Fused Clockwork Mechanism",
        "description": "Complex mechanical component salvaged from a ruined automaton. The gears are partially fused but may still contain functional elements.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 350,
        "weight": 1.2,
        "is_craftable": False,
        "source_tags": ["ruined_automaton_crucible_spire", "damaged_intricate_gears_dissonance_tech"],
        "illicit_in_regions": [],
        "properties": {
            "complexity": 7,
            "repair_difficulty": "high",
            "known_function": "unknown_possibly_targeting_array_or_locomotion",
            "material_composition": ["unknown_alloy", "trace_crimsonite"],
            "potential_kinetic_energy_release_if_mishandled": True
        }
    },
    {
        "name": "Inert Sentinel Plating Segment",
        "description": "Heavy armor plating from a decommissioned Accord peacekeeper prototype. Still retains some protective properties.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 200,
        "weight": 5.0,
        "is_craftable": False,
        "source_tags": ["decommissioned_accord_peacekeeper_prototype_dissonance_era_design", "heavy_armor_plate"],
        "illicit_in_regions": [],
        "properties": {
            "damage_resistance_physical_rating": 10,
            "energy_dampening_property_specific_frequency": "moderate_unknown_freq",
            "weight_class": "heavy",
            "latent_energy_signature": "faint_dissonance_echo",
            "repurpose_potential": "shielding_heavy_constructs"
        }
    },
    {
        "name": "Warped Leyline Conduit Section",
        "description": "A twisted section of leyline conduit damaged by dissonance weapons. Extremely dangerous but potentially valuable for research.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 600,
        "weight": 3.0,
        "is_craftable": False,
        "source_tags": ["shattered_leyline_nexus_ember_wastes_dissonance_weapon_strike_zone", "twisted_magic_channel"],
        "illicit_in_regions": ["Lethandrel_forbidden_study"],
        "properties": {
            "mana_conductivity_raw": "extremely_high_unpredictable",
            "instability_surges_per_hour_avg": 2,
            "emits_reality_distortions_minor": True,
            "can_be_stabilized_partially": "with_ferverl_siphons_or_accord_nullifiers",
            "research_value": "leyline_weaponry_defense"
        }
    },
    {
        "name": "Echo Crystal Shard (Dissonance)",
        "description": "An incredibly dangerous crystal that contains echoes of a dissonance event. Strictly forbidden in all Accord territories.",
        "material_type": MaterialType.GEM,
        "rarity": Rarity.LEGENDARY,
        "base_value": 1500,
        "weight": 0.1,
        "is_craftable": False,
        "source_tags": ["core_of_imploded_relic_crucible_spire_rift", "trapped_dissonance_event_echo"],
        "illicit_in_regions": ["ALL_ACCORD_CITIES_STRICTLY_FORBIDDEN"],
        "properties": {
            "trapped_echo_type": "random_battle_screams_energy_bursts_temporal_loops",
            "release_condition_unpredictable": True,
            "stabilization_method": "unknown_containment_field_only",
            "power_potential_if_harnessed": "immense_catastrophic",
            "psychic_resonance_strong": True
        }
    },
    {
        "name": "Corrupted Servitor Actuator",
        "description": "A joint mechanism from a war construct that retains some functionality but is tainted with malevolent energy.",
        "material_type": MaterialType.METAL,
        "rarity": Rarity.RARE,
        "base_value": 280,
        "weight": 0.8,
        "is_craftable": False,
        "source_tags": ["dismantled_crimson_war_construct_lingering_malevolence", "functional_but_tainted_limb_joint"],
        "illicit_in_regions": ["Skarport_public_display"],
        "properties": {
            "functionality_remaining_percent": 60,
            "corruption_type": "aggressive_sentience_attempts_control",
            "power_requirement_ma": "high",
            "can_be_purified": "partially_with_thal_zirad_flame_rites",
            "repurpose_use": "risky_automaton_component"
        }
    },
    {
        "name": "Unstable Isotope Pellet (D-Era)",
        "description": "A highly radioactive magical isotope from a breached relic power cell. Extremely hazardous but potentially powerful.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 900,
        "weight": 0.05,
        "is_craftable": False,
        "source_tags": ["breached_relic_power_cell_crucible_spire_vaults", "highly_radioactive_magical_isotope"],
        "illicit_in_regions": ["Everywhere_extreme_hazard"],
        "properties": {
            "radiation_type": "alpha_beta_crimson_gamma",
            "half_life_years_approx": 50,
            "energy_output_slow_decay_mw": 0.5,
            "shielding_required_material": "lead_or_dwarven_deep_iron",
            "mutagenic_properties_strong": True
        }
    },
    {
        "name": "Frozen Time Shard",
        "description": "A fragment of crystallized time from a temporal dissonance weapon effect. Causes localized time stasis on contact.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.LEGENDARY,
        "base_value": 2200,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["epicenter_of_temporal_dissonance_weapon_effect_whispering_woods_anomaly", "localized_time_stasis_fragment"],
        "illicit_in_regions": ["Accord_Council_Level_Containment_Only"],
        "properties": {
            "temporal_effect_radius_cm": "variable_1_to_10_on_contact",
            "stasis_duration_local_seconds": "unpredictable_minutes_to_eons",
            "stabilization_difficulty": "extreme",
            "can_shatter_releasing_temporal_wave": True,
            "study_value_chronomancy": "priceless_dangerous"
        }
    },
    {
        "name": "Resonant Echo Shard",
        "description": "Fragment of an ancient speaking stone that still carries traces of voices from the past. Valuable to scholars and artificers.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 250,
        "weight": 0.2,
        "is_craftable": False,
        "source_tags": ["excavated_ancient_ruins_pre_strife", "archaeologically_significant"],
        "illicit_in_regions": [],
        "properties": {
            "energy_type": "residual_echo_sound",
            "stability": "high",
            "activation_trigger": "specific_resonant_frequencies",
            "information_content": "historical_fragments_unpredictable",
            "used_in": ["communication_relics", "memory_stones", "sound_projection_devices"]
        }
    },
    # Stabilization & Containment Materials
    {
        "name": "Accord-Standard Nullifier Rod",
        "description": "A specialized tool developed by Accord mages to temporarily contain and dampen wild magical energies. Essential for relic handling.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.EPIC,
        "base_value": 1200,
        "weight": 0.5,
        "is_craftable": True,
        "source_tags": ["accord_tech_licensed_skarport_high_council_issue", "stabilization_tool_dampens_wild_magic"],
        "illicit_in_regions": [],
        "properties": {
            "function": "dampen_wild_magic_radius_m_5",
            "charge_capacity_units": 100,
            "rechargeable": "at_accord_sanctioned_stations_only",
            "single_use_for_epic_relics": True,
            "effectiveness_vs_crimson_mana": "moderate"
        }
    },
    {
        "name": "Ferverl Leyline Siphon (Crude)",
        "description": "A crude but functional device for drawing ambient mana or slowly draining relic energy. Made by Ferverl tinkerers.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 450,
        "weight": 1.5,
        "is_craftable": True,
        "source_tags": ["ferverl_wasteland_tech_ashkar_vale_tinkerer", "draws_ambient_mana_can_stabilize_minor_relics"],
        "illicit_in_regions": [],
        "properties": {
            "function": "draw_ambient_mana_or_drain_relic_slowly",
            "efficiency_percent": 30,
            "backlash_potential_on_overload": "medium_mana_burn",
            "requires_attunement_ritual": "Ferverl_basic_grounding",
            "durability_low": True
        }
    },
    {
        "name": "Dwarven Lead-Lined Containment Box",
        "description": "A heavy-duty containment box with lead lining, designed to shield radioactive and magical items from detection.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.RARE,
        "base_value": 300,
        "weight": 10.0,
        "is_craftable": True,
        "source_tags": ["dwarven_smithing_stonewake_special_order", "shielding_radioactive_magical_items"],
        "illicit_in_regions": [],
        "properties": {
            "shielding_effectiveness_percent_dissonance_radiation": 70,
            "internal_volume_liters": 5,
            "lock_type": "heavy_duty_bolt_runic_seal_optional",
            "material": "steel_lead_lining_1cm"
        }
    },
    {
        "name": "Elven Ward-Weave Mesh (Silver)",
        "description": "Enchanted silver mesh that can contain ethereal entities and spirit energy. Requires periodic re-enchanting.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 750,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["lethandrel_spellweaver_artisan_enchanted_silver_mesh", "contains_ethereal_or_spirit_energy"],
        "illicit_in_regions": [],
        "properties": {
            "containment_type": "ethereal_entities_spirit_energy_minor_telepathic_echoes",
            "strength_vs_physical_force": "low",
            "mana_conductivity_wards": "high",
            "requires_re_enchanting_periodically": True,
            "size_square_meter": 0.5
        }
    },
    {
        "name": "Inert Clay (Mana Absorptive)",
        "description": "Naturally occurring clay that absorbs ambient mana. Useful for temporary shielding of unstable relics.",
        "material_type": MaterialType.MINERAL,
        "rarity": Rarity.UNCOMMON,
        "base_value": 20,
        "weight": 1.0,
        "is_craftable": False,
        "source_tags": ["crystal_highlands_geothermal_clay_beds", "naturally_absorbs_ambient_mana"],
        "illicit_in_regions": [],
        "properties": {
            "mana_absorption_capacity_units_per_kg": 50,
            "saturation_indicator": "faint_glow_then_crumbles",
            "use": "packing_material_for_unstable_relics_temporary_shielding",
            "reusability": "low_once_saturated"
        }
    },
    {
        "name": "Quenched Quicksilver Solution",
        "description": "Stabilized mercury solution used as coolant and conductor for relic cores. Still toxic but more stable than raw quicksilver.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.EPIC,
        "base_value": 600,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["stabilized_quicksilver_alchemical_process_crucible_spire_lab", "coolant_and_conductor_for_relic_cores"],
        "illicit_in_regions": ["Lethandrel_highly_restricted"],
        "properties": {
            "thermal_conductivity": "very_high",
            "mana_conductivity": "high_stable",
            "viscosity": "low",
            "toxicity_reduced_but_still_present": "medium",
            "use": "relic_core_coolant_fine_tuning_energy_flow",
            "container_required": "sealed_quartz_ampule"
        }
    },
    {
        "name": "Activated Charcoal Filter (Heavy)",
        "description": "High-grade activated charcoal filter for removing toxins and magical particulates from air in relic work areas.",
        "material_type": MaterialType.CRAFTED,
        "rarity": Rarity.UNCOMMON,
        "base_value": 30,
        "weight": 0.5,
        "is_craftable": True,
        "source_tags": ["processed_hardwood_high_temp_steam_activation", "filters_airborne_toxins_minor_magical_particulates"],
        "illicit_in_regions": [],
        "properties": {
            "filtration_efficiency_percent_common_toxins": 80,
            "filtration_magic_particulates": "low_gaseous_only",
            "lifespan_hours_continuous_use": 24,
            "use": "respirators_lab_environments_relic_disassembly_zones"
        }
    },
    {
        "name": "Elven Mana-Silk Thread (Spool)",
        "description": "Incredibly fine thread spun from silk infused with stabilized mana. Used for inscription and binding of magical elements.",
        "material_type": MaterialType.MAGICAL,
        "rarity": Rarity.RARE,
        "base_value": 180,
        "weight": 0.05,
        "is_craftable": True,
        "source_tags": ["lethandrel_arcanist_crafted", "binding_component"],
        "illicit_in_regions": [],
        "properties": {
            "tensile_strength_magical": "very_high",
            "conducts_mana": True,
            "containment_potential": "medium",
            "glow_when_active": "faint_user_attuned_color",
            "spool_length_meters": 50
        }
    },
    # Tools for Relic Tinkering
    {
        "name": "Insulated Cerametal Pliers",
        "description": "Specialized pliers with ceramic coating for handling electrically and magically charged relic components safely.",
        "material_type": MaterialType.TOOL,
        "rarity": Rarity.RARE,
        "base_value": 150,
        "weight": 0.3,
        "is_craftable": True,
        "source_tags": ["ferverl_innovation_crucible_spire_workshop", "handles_electrically_magically_charged_components"],
        "illicit_in_regions": [],
        "properties": {
            "insulation_rating_volts_mana_units": "10kV_100MU",
            "grip_precision": "high",
            "material": "ceramic_coated_tool_steel",
            "heat_resistance_celsius": 800,
            "notes": "Essential for disarming certain relic traps."
        }
    },
    {
        "name": "Multi-Spectrum Goggles",
        "description": "Advanced goggles that reveal hidden energy signatures and auras. Essential equipment for relic analysis.",
        "material_type": MaterialType.TOOL,
        "rarity": Rarity.EPIC,
        "base_value": 500,
        "weight": 0.2,
        "is_craftable": True,
        "source_tags": ["human_artificer_skarport_guild_of_innovators", "reveals_hidden_energy_signatures_auras"],
        "illicit_in_regions": [],
        "properties": {
            "vision_modes": ["thermal", "mana_flow_basic", "ethereal_echoes_faint", "structural_integrity_scan_microfractures"],
            "power_source": "miniature_mana_crystal_replaceable",
            "durability": "medium_delicate_lenses"
        }
    },
    {
        "name": "Sonic Emitter (Fine Tuned)",
        "description": "Precision instrument that uses sound waves to detect flaws or trigger mechanisms in relics. Requires expert handling.",
        "material_type": MaterialType.TOOL,
        "rarity": Rarity.EPIC,
        "base_value": 700,
        "weight": 0.6,
        "is_craftable": True,
        "source_tags": ["dwarven_acoustic_engineer_stonewake_labs", "used_to_resonate_and_detect_flaws_or_trigger_mechanisms_in_relics"],
        "illicit_in_regions": [],
        "properties": {
            "frequency_range_hz": "1_to_100000",
            "amplitude_control_fine": True,
            "power_output_max_decibels": 120,
            "use_risk": "can_shatter_delicate_relics_if_miscalibrated",
            "requires_skill": "Acoustic Engineering L5"
        }
    },
    {
        "name": "Containment Field Projector (Small)",
        "description": "Reverse-engineered Accord technology that generates temporary localized stasis fields for containing dangerous relics.",
        "material_type": MaterialType.TOOL,
        "rarity": Rarity.LEGENDARY,
        "base_value": 3000,
        "weight": 2.0,
        "is_craftable": True,
        "source_tags": ["lost_accord_tech_reverse_engineered_crucible_spire_secret_lab", "generates_temporary_localized_stasis_field"],
        "illicit_in_regions": ["Accord_High_Council_Monopoly"],
        "properties": {
            "field_radius_max_meters": 0.5,
            "duration_max_minutes_at_full_power": 5,
            "power_cell_type": "refined_crimsonite_pellet_stabilized",
            "field_strength_rating": 8,
            "failure_chance_on_critical_relic": 0.15,
            "recharge_time_hours": 12
        }
    },
    {
        "name": "Glyphic Scraper Set (Obsidian)",
        "description": "Set of obsidian tools for removing or altering magical runes on relics. The obsidian is magically inert.",
        "material_type": MaterialType.TOOL,
        "rarity": Rarity.RARE,
        "base_value": 90,
        "weight": 0.1,
        "is_craftable": True,
        "source_tags": ["ferverl_artisan_thal_zirad_engraved_obsidian_tools", "for_removing_or_altering_magical_runes_on_relics"],
        "illicit_in_regions": [],
        "properties": {
            "tool_tips_shapes": ["fine_point", "curved_edge", "flat_chisel"],
            "material_hardness_mohs": 6,
            "non_conductive_magically_inert": True,
            "delicacy_required": "high_can_damage_runes_if_unskilled"
        }
    }
]

# Combine all materials for easy access
ALL_MATERIALS = (
    BLACKSMITHING_MATERIALS +
    ALCHEMY_MATERIALS +
    WOODWORKING_MATERIALS +
    TAILORING_MATERIALS +
    JEWELCRAFTING_MATERIALS +
    RELICSMITHING_MATERIALS
)