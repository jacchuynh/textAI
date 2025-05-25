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
        "base_value": 200, # total value for 100g bar
        "weight": 0.1, # 100g converted to kg
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
        "name": "Gold Jewelry Bar (18k)",
        "description": "High-quality gold alloy suitable for fine jewelry work. Warm yellow color with excellent workability.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.RARE,
        "base_value": 500, # total value for 50g bar
        "weight": 0.05, # 50g converted to kg
        "is_craftable": True,
        "source_tags": ["refined_gold_alloyed_copper_silver", "skarport_jewelers_guild_standard"],
        "illicit_in_regions": [],
        "properties": {
            "purity_percent": 75,
            "purity_karat": 18,
            "malleability": "excellent",
            "tarnish_resistance": "very_high",
            "color": "rich_yellow",
            "mana_conductivity": "moderate",
            "melting_point_celsius": 950
        }
    }
]

# Relicsmithing & Artifact Tinkering Materials
RELICSMITHING_MATERIALS = [
    # Unstable Relic Components
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