"""
Crafting System Database Seed Script

This script populates the database with initial materials and recipes
for the Material and Recipe System.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from backend.src.database.session import SessionLocal
from backend.src.crafting.models.db_models import (
    DBMaterial, DBRecipe, DBRecipeIngredient, DBRecipeOutput, DBSkillRequirement
)
from backend.src.crafting.models.pydantic_models import (
    MaterialType, Rarity, Material, Recipe, RecipeIngredient, RecipeOutput, SkillRequirement
)

logger = logging.getLogger(__name__)

# Material seed data by profession
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
    # Refined Metals (Ingots)
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
    }
]

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
    }
]

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
    # Precious Metals for Jewelry
    {
        "name": "Silver Jewelry Bar (92.5% Pure)",
        "description": "Sterling silver ingot specifically alloyed for jewelry making. Maintains shine while offering good durability.",
        "material_type": MaterialType.METAL_PRECIOUS,
        "rarity": Rarity.UNCOMMON,
        "base_value": 2, # per gram
        "weight": 100, # assuming 100g bar
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
    }
]

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
    }
]

# Combine all materials
ALL_MATERIALS = (
    BLACKSMITHING_MATERIALS +
    ALCHEMY_MATERIALS +
    WOODWORKING_MATERIALS +
    TAILORING_MATERIALS +
    JEWELCRAFTING_MATERIALS +
    RELICSMITHING_MATERIALS
)

# Recipe seed data
BLACKSMITHING_RECIPES = [
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
            {"item_id": "Pine Planks (Bundle of 5)", "quantity": 0.2, "consumed_in_crafting": True}
        ],
        "primary_output": {"item_id": "Simple Iron Dagger", "quantity": 1.0},
        "required_skills": [
            {"skill_name": "Blacksmithing", "level": 2, "affects_quality": True},
            {"skill_name": "Weaponsmithing", "level": 1, "affects_quality": True}
        ]
    }
]

WOODWORKING_RECIPES = [
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
    }
]

TAILORING_RECIPES = [
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
    }
]

# Combine all recipes
ALL_RECIPES = (
    BLACKSMITHING_RECIPES +
    WOODWORKING_RECIPES +
    TAILORING_RECIPES
)

def seed_materials(db: Session) -> Dict[str, str]:
    """
    Seed the materials table with initial data.
    
    Returns a mapping of material names to their UUIDs.
    """
    logger.info("Seeding materials...")
    material_id_map = {}
    
    for material_data in ALL_MATERIALS:
        # Check if material already exists
        existing = db.query(DBMaterial).filter(DBMaterial.name == material_data["name"]).first()
        if existing:
            logger.info(f"Material '{material_data['name']}' already exists, skipping.")
            material_id_map[material_data["name"]] = existing.id
            continue
        
        # Create new material
        material = Material(**material_data)
        db_material = DBMaterial(
            name=material.name,
            description=material.description,
            material_type=material.material_type.value,
            rarity=material.rarity.value,
            base_value=material.base_value,
            weight=material.weight,
            is_craftable=material.is_craftable,
            source_tags=material.source_tags,
            illicit_in_regions=material.illicit_in_regions,
            properties=material.properties,
            custom_data=material.custom_data
        )
        db.add(db_material)
        db.flush()
        
        logger.info(f"Added material: {material.name}")
        material_id_map[material.name] = db_material.id
    
    db.commit()
    return material_id_map

def seed_recipes(db: Session, material_id_map: Dict[str, str]) -> None:
    """
    Seed the recipes table with initial data.
    
    Args:
        db: Database session
        material_id_map: Mapping of material names to their UUIDs
    """
    logger.info("Seeding recipes...")
    
    for recipe_data in ALL_RECIPES:
        # Check if recipe already exists
        existing = db.query(DBRecipe).filter(DBRecipe.name == recipe_data["name"]).first()
        if existing:
            logger.info(f"Recipe '{recipe_data['name']}' already exists, skipping.")
            continue
        
        # Create new recipe
        db_recipe = DBRecipe(
            name=recipe_data["name"],
            description=recipe_data["description"],
            recipe_category=recipe_data["recipe_category"],
            crafting_time_seconds=recipe_data["crafting_time_seconds"],
            required_station_type=recipe_data["required_station_type"],
            difficulty_level=recipe_data["difficulty_level"],
            is_discoverable=recipe_data["is_discoverable"],
            experience_gained=recipe_data["experience_gained"],
            quality_range=recipe_data["quality_range"]
        )
        db.add(db_recipe)
        db.flush()  # Get the recipe ID
        
        # Add primary output
        primary_output = recipe_data["primary_output"]
        item_id = material_id_map.get(primary_output["item_id"])
        if not item_id:
            logger.warning(f"Output material '{primary_output['item_id']}' not found for recipe '{recipe_data['name']}', using placeholder.")
            # Create a placeholder material
            placeholder_material = DBMaterial(
                name=primary_output["item_id"],
                description=f"Placeholder for {primary_output['item_id']}",
                material_type=MaterialType.CRAFTED.value,
                rarity=Rarity.COMMON.value,
                base_value=1.0,
                weight=1.0,
                is_craftable=True,
                source_tags=["crafted"],
                properties={}
            )
            db.add(placeholder_material)
            db.flush()
            item_id = placeholder_material.id
            material_id_map[primary_output["item_id"]] = item_id
        
        db_output = DBRecipeOutput(
            recipe_id=db_recipe.id,
            item_id=item_id,
            quantity=primary_output["quantity"],
            is_primary=True,
            chance=1.0
        )
        db.add(db_output)
        
        # Add byproducts (if any)
        if "byproducts" in recipe_data:
            for byproduct in recipe_data["byproducts"]:
                byproduct_item_id = material_id_map.get(byproduct["item_id"])
                if byproduct_item_id:
                    db_byproduct = DBRecipeOutput(
                        recipe_id=db_recipe.id,
                        item_id=byproduct_item_id,
                        quantity=byproduct["quantity"],
                        is_primary=False,
                        chance=byproduct.get("chance", 1.0),
                        quality_modifier=byproduct.get("quality_modifier", 0.0)
                    )
                    db.add(db_byproduct)
        
        # Add ingredients
        for ingredient in recipe_data["ingredients"]:
            ingredient_item_id = material_id_map.get(ingredient["item_id"])
            if not ingredient_item_id:
                logger.warning(f"Ingredient material '{ingredient['item_id']}' not found for recipe '{recipe_data['name']}', skipping.")
                continue
            
            db_ingredient = DBRecipeIngredient(
                recipe_id=db_recipe.id,
                item_id=ingredient_item_id,
                quantity=ingredient["quantity"],
                consumed_in_crafting=ingredient.get("consumed_in_crafting", True),
                can_be_substituted=ingredient.get("can_be_substituted", False),
                possible_substitutes=ingredient.get("possible_substitutes")
            )
            db.add(db_ingredient)
        
        # Add skill requirements
        for skill in recipe_data["required_skills"]:
            db_skill = DBSkillRequirement(
                recipe_id=db_recipe.id,
                skill_name=skill["skill_name"],
                level=skill["level"],
                affects_quality=skill.get("affects_quality", True),
                affects_speed=skill.get("affects_speed", False)
            )
            db.add(db_skill)
        
        logger.info(f"Added recipe: {recipe_data['name']}")
    
    db.commit()

def seed_database() -> None:
    """Seed the database with initial materials and recipes."""
    db = SessionLocal()
    try:
        material_id_map = seed_materials(db)
        seed_recipes(db, material_id_map)
        logger.info("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()