"""
Magic Crafting Seed Data

This script populates the database with initial magical materials, 
enchantments, and crafting stations to get the system started.
"""

import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .magic_crafting_models import (
    MagicalMaterial, Enchantment, 
    LeylineCraftingStation, MagicalGatheringLocation
)
from ..db.database import SessionLocal

def seed_magical_materials():
    """Seed the database with initial magical materials"""
    print("Seeding magical materials...")
    
    session = SessionLocal()
    
    # Check if materials already exist
    existing_count = session.query(MagicalMaterial).count()
    if existing_count > 0:
        print(f"Found {existing_count} existing magical materials. Skipping seed.")
        session.close()
        return
    
    # Define materials
    materials = [
        # Fire materials
        {
            "id": "fire_crystal",
            "name": "Fire Crystal",
            "description": "A crystal that resonates with fire energy. Glows with an inner light.",
            "rarity": "uncommon",
            "magical_affinity": ["FIRE"],
            "leyline_resonance": 1.5,
            "corruption_resistance": 0.8,
            "crafting_properties": {
                "hardness": 6,
                "melting_point": 1200,
                "magical_conductivity": 0.8
            },
            "gathering_difficulty": 4,
            "primary_locations": ["volcanic", "mountain", "hot_springs"],
            "required_tool": "pickaxe",
            "base_value": 25,
            "base_yield": 2
        },
        {
            "id": "phoenix_feather",
            "name": "Phoenix Feather",
            "description": "A feather that radiates heat. Never burns out.",
            "rarity": "rare",
            "magical_affinity": ["FIRE", "SPIRIT"],
            "leyline_resonance": 2.0,
            "corruption_resistance": 1.5,
            "crafting_properties": {
                "hardness": 1,
                "heat_retention": 0.9,
                "magical_conductivity": 0.9
            },
            "gathering_difficulty": 7,
            "primary_locations": ["volcanic", "mountain_peak", "sacred_grove"],
            "required_tool": "feather_charm",
            "base_value": 80,
            "base_yield": 1
        },
        
        # Water materials
        {
            "id": "deep_sea_pearl",
            "name": "Deep Sea Pearl",
            "description": "A lustrous pearl formed in the deepest oceans. Contains water magic.",
            "rarity": "uncommon",
            "magical_affinity": ["WATER"],
            "leyline_resonance": 1.4,
            "corruption_resistance": 1.2,
            "crafting_properties": {
                "hardness": 3,
                "luster": 0.9,
                "magical_conductivity": 0.7
            },
            "gathering_difficulty": 5,
            "primary_locations": ["ocean_depth", "underwater_cave", "coral_reef"],
            "required_tool": "diving_kit",
            "base_value": 30,
            "base_yield": 1
        },
        {
            "id": "glacial_ice_shard",
            "name": "Glacial Ice Shard",
            "description": "Ice that never melts, formed over centuries in ancient glaciers.",
            "rarity": "uncommon",
            "magical_affinity": ["WATER", "AIR"],
            "leyline_resonance": 1.3,
            "corruption_resistance": 0.7,
            "crafting_properties": {
                "hardness": 4,
                "temperature": -50,
                "magical_conductivity": 0.6
            },
            "gathering_difficulty": 4,
            "primary_locations": ["glacier", "frozen_peak", "ice_cave"],
            "required_tool": "ice_pick",
            "base_value": 20,
            "base_yield": 3
        },
        
        # Earth materials
        {
            "id": "resonant_quartz",
            "name": "Resonant Quartz",
            "description": "Quartz crystal that vibrates with earth energy. Amplifies magical signals.",
            "rarity": "common",
            "magical_affinity": ["EARTH"],
            "leyline_resonance": 1.7,
            "corruption_resistance": 1.0,
            "crafting_properties": {
                "hardness": 7,
                "resonance": 0.8,
                "magical_conductivity": 0.8
            },
            "gathering_difficulty": 3,
            "primary_locations": ["cave", "mountain", "crystal_formation"],
            "required_tool": "pickaxe",
            "base_value": 15,
            "base_yield": 4
        },
        {
            "id": "living_root",
            "name": "Living Root",
            "description": "A root that continues to grow even after being harvested.",
            "rarity": "uncommon",
            "magical_affinity": ["EARTH", "LIFE"],
            "leyline_resonance": 1.4,
            "corruption_resistance": 1.1,
            "crafting_properties": {
                "hardness": 2,
                "flexibility": 0.9,
                "magical_conductivity": 0.7
            },
            "gathering_difficulty": 4,
            "primary_locations": ["ancient_forest", "swamp", "sacred_grove"],
            "required_tool": "herbalism_kit",
            "base_value": 22,
            "base_yield": 2
        },
        
        # Air materials
        {
            "id": "cloud_essence",
            "name": "Cloud Essence",
            "description": "Condensed cloud material that floats in its container.",
            "rarity": "uncommon",
            "magical_affinity": ["AIR"],
            "leyline_resonance": 1.5,
            "corruption_resistance": 0.9,
            "crafting_properties": {
                "density": 0.2,
                "volatility": 0.7,
                "magical_conductivity": 0.8
            },
            "gathering_difficulty": 6,
            "primary_locations": ["mountain_peak", "sky_island", "thunderstorm"],
            "required_tool": "air_bottle",
            "base_value": 35,
            "base_yield": 2
        },
        {
            "id": "lightning_quill",
            "name": "Lightning Quill",
            "description": "A feather struck by lightning. Crackles with electricity.",
            "rarity": "rare",
            "magical_affinity": ["AIR", "FIRE"],
            "leyline_resonance": 1.9,
            "corruption_resistance": 0.8,
            "crafting_properties": {
                "hardness": 1,
                "conductivity": 0.95,
                "magical_conductivity": 0.9
            },
            "gathering_difficulty": 7,
            "primary_locations": ["thunderstorm", "mountain_peak", "storm_plain"],
            "required_tool": "lightning_rod",
            "base_value": 70,
            "base_yield": 1
        },
        
        # Spirit materials
        {
            "id": "ghost_silk",
            "name": "Ghost Silk",
            "description": "Ethereal threads spun by spirits. Barely visible in normal light.",
            "rarity": "rare",
            "magical_affinity": ["SPIRIT"],
            "leyline_resonance": 2.1,
            "corruption_resistance": 1.2,
            "crafting_properties": {
                "hardness": 1,
                "etherealness": 0.9,
                "magical_conductivity": 0.95
            },
            "gathering_difficulty": 8,
            "primary_locations": ["haunted_ruin", "ancient_battlefield", "spirit_grove"],
            "required_tool": "spirit_catcher",
            "base_value": 85,
            "base_yield": 1
        },
        {
            "id": "memory_crystal",
            "name": "Memory Crystal",
            "description": "A crystal that stores memories and emotions. Changes color based on mood.",
            "rarity": "uncommon",
            "magical_affinity": ["SPIRIT", "MIND"],
            "leyline_resonance": 1.8,
            "corruption_resistance": 1.0,
            "crafting_properties": {
                "hardness": 5,
                "clarity": 0.8,
                "magical_conductivity": 0.85
            },
            "gathering_difficulty": 5,
            "primary_locations": ["ancient_ruin", "meditation_site", "crystal_cave"],
            "required_tool": "mind_focus",
            "base_value": 40,
            "base_yield": 2
        },
        
        # Void materials
        {
            "id": "void_shard",
            "name": "Void Shard",
            "description": "A fragment of nothingness. Absorbs light and magic.",
            "rarity": "rare",
            "magical_affinity": ["VOID"],
            "leyline_resonance": 0.5,
            "corruption_resistance": 0.3,
            "crafting_properties": {
                "hardness": 8,
                "absorption": 0.9,
                "magical_conductivity": 0.2
            },
            "gathering_difficulty": 9,
            "primary_locations": ["corruption_zone", "reality_tear", "ancient_ruin"],
            "required_tool": "void_container",
            "base_value": 100,
            "base_yield": 1
        },
        {
            "id": "shadow_glass",
            "name": "Shadow Glass",
            "description": "Glass formed in absolute darkness. Shows shadows of other realms.",
            "rarity": "uncommon",
            "magical_affinity": ["VOID", "SPIRIT"],
            "leyline_resonance": 0.8,
            "corruption_resistance": 0.6,
            "crafting_properties": {
                "hardness": 6,
                "transparency": 0.3,
                "magical_conductivity": 0.5
            },
            "gathering_difficulty": 6,
            "primary_locations": ["deep_cave", "shadow_realm_border", "ancient_tomb"],
            "required_tool": "shadow_net",
            "base_value": 55,
            "base_yield": 2
        },
        
        # Life materials
        {
            "id": "heartwood",
            "name": "Heartwood",
            "description": "Wood from the center of an ancient tree. Pulses with life energy.",
            "rarity": "uncommon",
            "magical_affinity": ["LIFE"],
            "leyline_resonance": 1.6,
            "corruption_resistance": 1.4,
            "crafting_properties": {
                "hardness": 5,
                "vitality": 0.9,
                "magical_conductivity": 0.7
            },
            "gathering_difficulty": 5,
            "primary_locations": ["ancient_forest", "sacred_grove", "world_tree"],
            "required_tool": "blessed_axe",
            "base_value": 45,
            "base_yield": 2
        },
        {
            "id": "healing_herb",
            "name": "Healing Herb",
            "description": "A rare herb with remarkable healing properties.",
            "rarity": "common",
            "magical_affinity": ["LIFE", "EARTH"],
            "leyline_resonance": 1.3,
            "corruption_resistance": 1.5,
            "crafting_properties": {
                "potency": 0.8,
                "preservation": 0.7,
                "magical_conductivity": 0.6
            },
            "gathering_difficulty": 2,
            "primary_locations": ["meadow", "sacred_grove", "riverside"],
            "required_tool": "herbalism_kit",
            "base_value": 10,
            "base_yield": 5
        },
        
        # Mind materials
        {
            "id": "thought_crystal",
            "name": "Thought Crystal",
            "description": "A crystal that resonates with mental energy. Stores and amplifies thoughts.",
            "rarity": "rare",
            "magical_affinity": ["MIND"],
            "leyline_resonance": 1.7,
            "corruption_resistance": 1.1,
            "crafting_properties": {
                "hardness": 7,
                "clarity": 0.9,
                "magical_conductivity": 0.85
            },
            "gathering_difficulty": 7,
            "primary_locations": ["meditation_site", "ancient_library", "dream_realm_border"],
            "required_tool": "mind_focus",
            "base_value": 75,
            "base_yield": 1
        },
        {
            "id": "dream_silk",
            "name": "Dream Silk",
            "description": "Fabric woven from dreams. Changes patterns based on nearby thoughts.",
            "rarity": "uncommon",
            "magical_affinity": ["MIND", "SPIRIT"],
            "leyline_resonance": 1.5,
            "corruption_resistance": 0.9,
            "crafting_properties": {
                "hardness": 1,
                "flexibility": 0.95,
                "magical_conductivity": 0.8
            },
            "gathering_difficulty": 6,
            "primary_locations": ["dream_realm_border", "ancient_library", "meditation_site"],
            "required_tool": "dream_catcher",
            "base_value": 50,
            "base_yield": 2
        },
        
        # Legendary materials
        {
            "id": "dragon_scale",
            "name": "Dragon Scale",
            "description": "A scale from an ancient dragon. Extremely durable and magically potent.",
            "rarity": "legendary",
            "magical_affinity": ["FIRE", "EARTH", "SPIRIT"],
            "leyline_resonance": 3.0,
            "corruption_resistance": 2.0,
            "crafting_properties": {
                "hardness": 10,
                "heat_resistance": 0.95,
                "magical_conductivity": 0.9
            },
            "gathering_difficulty": 10,
            "primary_locations": ["dragon_lair", "volcanic_peak", "ancient_battlefield"],
            "required_tool": "legendary_dagger",
            "base_value": 500,
            "base_yield": 1
        },
        {
            "id": "stardust",
            "name": "Stardust",
            "description": "Dust from a fallen star. Glows with celestial energy.",
            "rarity": "legendary",
            "magical_affinity": ["COSMIC", "VOID", "LIGHT"],
            "leyline_resonance": 3.5,
            "corruption_resistance": 1.8,
            "crafting_properties": {
                "hardness": 2,
                "luminosity": 0.95,
                "magical_conductivity": 0.95
            },
            "gathering_difficulty": 9,
            "primary_locations": ["meteor_crash", "mountain_peak", "reality_tear"],
            "required_tool": "star_collector",
            "base_value": 450,
            "base_yield": 1
        }
    ]
    
    # Add materials to database
    for material_data in materials:
        material = MagicalMaterial(**material_data)
        session.add(material)
    
    # Commit changes
    session.commit()
    print(f"Added {len(materials)} magical materials to the database.")
    session.close()

def seed_enchantments():
    """Seed the database with initial enchantments"""
    print("Seeding enchantments...")
    
    session = SessionLocal()
    
    # Check if enchantments already exist
    existing_count = session.query(Enchantment).count()
    if existing_count > 0:
        print(f"Found {existing_count} existing enchantments. Skipping seed.")
        session.close()
        return
    
    # Define enchantments
    enchantments = [
        # Weapon enchantments
        {
            "id": "fire_damage",
            "name": "Enchantment of Fire Damage",
            "description": "Infuses the weapon with fire elemental damage.",
            "tier": 2,
            "magic_school": "evocation",
            "compatible_item_types": ["weapon", "ammunition"],
            "min_mana_cost": 25,
            "min_arcane_mastery": 2,
            "required_materials": {
                "fire_crystal": 2
            },
            "effects": {
                "fire_damage": 5,
                "ignite_chance": 0.1
            },
            "duration_type": "permanent",
            "base_success_chance": 0.8,
            "complexity": 3
        },
        {
            "id": "frost_edge",
            "name": "Enchantment of Frost Edge",
            "description": "Coats the weapon's edge with magical frost that slows enemies.",
            "tier": 2,
            "magic_school": "evocation",
            "compatible_item_types": ["weapon"],
            "min_mana_cost": 30,
            "min_arcane_mastery": 2,
            "required_materials": {
                "glacial_ice_shard": 2
            },
            "effects": {
                "frost_damage": 3,
                "slow_effect": 0.2
            },
            "duration_type": "permanent",
            "base_success_chance": 0.75,
            "complexity": 3
        },
        {
            "id": "thunder_strike",
            "name": "Enchantment of Thunder Strike",
            "description": "Weapon occasionally releases a thunderous blast on impact.",
            "tier": 3,
            "magic_school": "evocation",
            "compatible_item_types": ["weapon"],
            "min_mana_cost": 45,
            "min_arcane_mastery": 3,
            "required_materials": {
                "lightning_quill": 1,
                "cloud_essence": 2
            },
            "effects": {
                "lightning_damage": 8,
                "thunder_blast_chance": 0.15,
                "stun_chance": 0.05
            },
            "duration_type": "permanent",
            "base_success_chance": 0.7,
            "complexity": 5
        },
        
        # Armor enchantments
        {
            "id": "flame_ward",
            "name": "Enchantment of Flame Ward",
            "description": "Protects the wearer from fire and heat.",
            "tier": 2,
            "magic_school": "abjuration",
            "compatible_item_types": ["armor", "shield"],
            "min_mana_cost": 30,
            "min_arcane_mastery": 2,
            "required_materials": {
                "fire_crystal": 1,
                "phoenix_feather": 1
            },
            "effects": {
                "fire_resistance": 0.3,
                "heat_tolerance": 100
            },
            "duration_type": "permanent",
            "base_success_chance": 0.8,
            "complexity": 3
        },
        {
            "id": "feather_fall",
            "name": "Enchantment of Feather Fall",
            "description": "Slows the wearer's fall to a safe speed.",
            "tier": 1,
            "magic_school": "transmutation",
            "compatible_item_types": ["armor", "boots", "cloak"],
            "min_mana_cost": 20,
            "min_arcane_mastery": 1,
            "required_materials": {
                "cloud_essence": 1
            },
            "effects": {
                "fall_speed_reduction": 0.9,
                "fall_damage_reduction": 0.8
            },
            "duration_type": "permanent",
            "base_success_chance": 0.85,
            "complexity": 2
        },
        {
            "id": "spirit_shield",
            "name": "Enchantment of Spirit Shield",
            "description": "Creates a spiritual barrier that absorbs damage.",
            "tier": 3,
            "magic_school": "abjuration",
            "compatible_item_types": ["armor", "shield", "amulet"],
            "min_mana_cost": 40,
            "min_arcane_mastery": 3,
            "required_materials": {
                "ghost_silk": 1,
                "memory_crystal": 1
            },
            "effects": {
                "damage_absorption": 0.2,
                "spiritual_protection": 0.4
            },
            "duration_type": "permanent",
            "base_success_chance": 0.7,
            "complexity": 4
        },
        
        # Tool enchantments
        {
            "id": "harvest_bounty",
            "name": "Enchantment of Harvest Bounty",
            "description": "Increases yield when gathering resources.",
            "tier": 2,
            "magic_school": "transmutation",
            "compatible_item_types": ["tool", "gloves"],
            "min_mana_cost": 25,
            "min_arcane_mastery": 2,
            "required_materials": {
                "living_root": 1,
                "healing_herb": 3
            },
            "effects": {
                "gathering_yield_bonus": 0.3,
                "resource_quality_chance": 0.15
            },
            "duration_type": "permanent",
            "base_success_chance": 0.8,
            "complexity": 3
        },
        {
            "id": "miners_insight",
            "name": "Enchantment of Miner's Insight",
            "description": "Helps locate valuable minerals and gems.",
            "tier": 2,
            "magic_school": "divination",
            "compatible_item_types": ["tool", "helmet"],
            "min_mana_cost": 30,
            "min_arcane_mastery": 2,
            "required_materials": {
                "resonant_quartz": 2,
                "thought_crystal": 1
            },
            "effects": {
                "mineral_detection_range": 10,
                "gem_quality_bonus": 0.2
            },
            "duration_type": "permanent",
            "base_success_chance": 0.75,
            "complexity": 3
        },
        
        # Jewelry enchantments
        {
            "id": "mental_clarity",
            "name": "Enchantment of Mental Clarity",
            "description": "Enhances focus and mental capabilities.",
            "tier": 2,
            "magic_school": "enchantment",
            "compatible_item_types": ["amulet", "ring", "circlet"],
            "min_mana_cost": 35,
            "min_arcane_mastery": 2,
            "required_materials": {
                "thought_crystal": 1,
                "memory_crystal": 1
            },
            "effects": {
                "focus_bonus": 0.25,
                "mental_resistance": 0.2,
                "mana_regeneration": 0.1
            },
            "duration_type": "permanent",
            "base_success_chance": 0.75,
            "complexity": 4
        },
        {
            "id": "life_binding",
            "name": "Enchantment of Life Binding",
            "description": "Stores healing energy that activates when the wearer is injured.",
            "tier": 3,
            "magic_school": "restoration",
            "compatible_item_types": ["amulet", "ring"],
            "min_mana_cost": 50,
            "min_arcane_mastery": 3,
            "required_materials": {
                "heartwood": 1,
                "healing_herb": 3,
                "ghost_silk": 1
            },
            "effects": {
                "emergency_healing": 50,
                "healing_trigger_threshold": 0.3,
                "regeneration_bonus": 0.15
            },
            "duration_type": "charges",
            "max_charges": 3,
            "base_success_chance": 0.65,
            "complexity": 5
        },
        
        # Temporary enchantments
        {
            "id": "shadow_veil",
            "name": "Enchantment of Shadow Veil",
            "description": "Grants temporary stealth by wrapping the item in shadows.",
            "tier": 2,
            "magic_school": "illusion",
            "compatible_item_types": ["cloak", "armor", "boots"],
            "min_mana_cost": 35,
            "min_arcane_mastery": 2,
            "required_materials": {
                "shadow_glass": 1,
                "void_shard": 1
            },
            "effects": {
                "stealth_bonus": 0.4,
                "noise_reduction": 0.3,
                "shadow_blend": 0.5
            },
            "duration_type": "temporary",
            "max_charges": None,
            "base_success_chance": 0.7,
            "complexity": 4
        },
        {
            "id": "dreamwalker",
            "name": "Enchantment of Dreamwalking",
            "description": "Allows the wearer to enter and influence dreams.",
            "tier": 4,
            "magic_school": "enchantment",
            "compatible_item_types": ["circlet", "amulet"],
            "min_mana_cost": 60,
            "min_arcane_mastery": 4,
            "required_materials": {
                "dream_silk": 2,
                "thought_crystal": 1,
                "memory_crystal": 1
            },
            "effects": {
                "dream_entry": 1.0,
                "dream_manipulation": 0.5,
                "memory_reading": 0.3
            },
            "duration_type": "charges",
            "max_charges": 5,
            "base_success_chance": 0.6,
            "complexity": 6
        },
        
        # Legendary enchantments
        {
            "id": "dragonbane",
            "name": "Enchantment of Dragonbane",
            "description": "Imbues a weapon with the power to greatly harm draconic creatures.",
            "tier": 5,
            "magic_school": "evocation",
            "compatible_item_types": ["weapon"],
            "min_mana_cost": 100,
            "min_arcane_mastery": 5,
            "required_materials": {
                "dragon_scale": 1,
                "fire_crystal": 3,
                "void_shard": 1
            },
            "effects": {
                "dragon_damage_bonus": 1.0,
                "armor_penetration": 0.5,
                "fire_resistance": 0.5
            },
            "duration_type": "permanent",
            "base_success_chance": 0.5,
            "complexity": 8
        },
        {
            "id": "cosmic_attunement",
            "name": "Enchantment of Cosmic Attunement",
            "description": "Attunes an item to cosmic forces, granting otherworldly powers.",
            "tier": 5,
            "magic_school": "conjuration",
            "compatible_item_types": ["staff", "wand", "amulet"],
            "min_mana_cost": 120,
            "min_arcane_mastery": 5,
            "required_materials": {
                "stardust": 1,
                "void_shard": 1,
                "thought_crystal": 1
            },
            "effects": {
                "spell_power_bonus": 0.5,
                "mana_cost_reduction": 0.3,
                "planar_sight": 1.0,
                "teleportation_range": 100
            },
            "duration_type": "permanent",
            "base_success_chance": 0.45,
            "complexity": 9
        }
    ]
    
    # Add enchantments to database
    for enchantment_data in enchantments:
        enchantment = Enchantment(**enchantment_data)
        session.add(enchantment)
    
    # Commit changes
    session.commit()
    print(f"Added {len(enchantments)} enchantments to the database.")
    session.close()

def seed_crafting_stations():
    """Seed the database with initial leyline crafting stations"""
    print("Seeding leyline crafting stations...")
    
    session = SessionLocal()
    
    # Check if stations already exist
    existing_count = session.query(LeylineCraftingStation).count()
    if existing_count > 0:
        print(f"Found {existing_count} existing crafting stations. Skipping seed.")
        session.close()
        return
    
    # Define regions
    regions = [
        "northlands", "eastern_kingdom", "western_provinces", 
        "southern_isles", "central_plains"
    ]
    
    # Define station types
    station_types = [
        "forge", "alchemy_lab", "enchanting_table", 
        "workbench", "loom", "crystallizer"
    ]
    
    # Generate stations
    stations = []
    
    for region in regions:
        # Major stations in each region (high leyline connection)
        major_station_type = random.choice(station_types)
        major_station = {
            "id": f"{major_station_type}_{region}_major",
            "name": f"Greater {major_station_type.replace('_', ' ').title()} of {region.replace('_', ' ').title()}",
            "location_id": f"{region}_capital",
            "station_type": major_station_type,
            "leyline_connection": round(random.uniform(3.0, 4.0), 1),
            "quality_bonus": 0.0,  # Will be calculated
            "material_efficiency": 1.0,  # Will be calculated
            "time_efficiency": 1.0,  # Will be calculated
            "special_abilities": {},  # Will be populated
            "access_level": 1,  # Slightly restricted
            "required_reputation": 10,
            "is_active": True,
            "last_leyline_update": datetime.utcnow()
        }
        
        # Calculate stats based on leyline connection
        major_station["quality_bonus"] = round(0.05 * major_station["leyline_connection"], 3)
        major_station["material_efficiency"] = round(max(0.5, 1.0 - (0.05 * major_station["leyline_connection"])), 2)
        major_station["time_efficiency"] = round(max(0.5, 1.0 - (0.05 * major_station["leyline_connection"])), 2)
        
        # Special abilities based on leyline strength
        if major_station["leyline_connection"] >= 2.0:
            major_station["special_abilities"]["magical_affinity"] = True
        
        if major_station["leyline_connection"] >= 3.0:
            major_station["special_abilities"]["leyline_channeling"] = True
        
        if major_station["leyline_connection"] >= 3.5:
            major_station["special_abilities"]["rare_crafting"] = True
        
        stations.append(major_station)
        
        # 2-3 minor stations in each region
        minor_count = random.randint(2, 3)
        for i in range(minor_count):
            minor_station_type = random.choice([t for t in station_types if t != major_station_type])
            settlement_type = random.choice(["village", "outpost", "town", "hamlet"])
            minor_station = {
                "id": f"{minor_station_type}_{region}_minor_{i+1}",
                "name": f"{minor_station_type.replace('_', ' ').title()} of {region.replace('_', ' ').title()} {settlement_type.title()}",
                "location_id": f"{region}_{settlement_type}_{i+1}",
                "station_type": minor_station_type,
                "leyline_connection": round(random.uniform(1.0, 2.5), 1),
                "quality_bonus": 0.0,  # Will be calculated
                "material_efficiency": 1.0,  # Will be calculated
                "time_efficiency": 1.0,  # Will be calculated
                "special_abilities": {},  # Will be populated
                "access_level": 0,  # Public
                "required_reputation": 0,
                "is_active": True,
                "last_leyline_update": datetime.utcnow()
            }
            
            # Calculate stats based on leyline connection
            minor_station["quality_bonus"] = round(0.05 * minor_station["leyline_connection"], 3)
            minor_station["material_efficiency"] = round(max(0.5, 1.0 - (0.05 * minor_station["leyline_connection"])), 2)
            minor_station["time_efficiency"] = round(max(0.5, 1.0 - (0.05 * minor_station["leyline_connection"])), 2)
            
            # Special abilities based on leyline strength
            if minor_station["leyline_connection"] >= 2.0:
                minor_station["special_abilities"]["magical_affinity"] = True
            
            stations.append(minor_station)
    
    # Add stations to database
    for station_data in stations:
        station = LeylineCraftingStation(**station_data)
        session.add(station)
    
    # Commit changes
    session.commit()
    print(f"Added {len(stations)} leyline crafting stations to the database.")
    session.close()

def seed_gathering_locations():
    """Seed the database with initial magical gathering locations"""
    print("Seeding magical gathering locations...")
    
    session = SessionLocal()
    
    # Check if locations already exist
    existing_count = session.query(MagicalGatheringLocation).count()
    if existing_count > 0:
        print(f"Found {existing_count} existing gathering locations. Skipping seed.")
        session.close()
        return
    
    # Define regions
    regions = [
        "northlands", "eastern_kingdom", "western_provinces", 
        "southern_isles", "central_plains"
    ]
    
    # Define location types
    location_types = [
        "cave", "forest", "mountain", "lake", "ruins", 
        "swamp", "beach", "volcano", "glacier", "desert"
    ]
    
    # Generate locations
    locations = []
    
    for region in regions:
        # 3-5 locations per region
        location_count = random.randint(3, 5)
        for i in range(location_count):
            location_type = random.choice(location_types)
            
            # Generate name
            adjectives = ["mystic", "ancient", "hidden", "forgotten", "sacred", "haunted", "shimmering", "thundering", "whispering", "frozen"]
            nouns = {"cave": ["cavern", "grotto", "hollow", "depths"],
                     "forest": ["woods", "grove", "thicket", "wildwood"],
                     "mountain": ["peak", "crag", "summit", "highlands"],
                     "lake": ["waters", "mere", "basin", "depths"],
                     "ruins": ["remains", "remnants", "citadel", "temple"],
                     "swamp": ["marsh", "bog", "mire", "wetlands"],
                     "beach": ["shore", "coast", "sands", "cove"],
                     "volcano": ["caldera", "furnace", "forge", "mountain"],
                     "glacier": ["ice", "frost", "tundra", "expanse"],
                     "desert": ["sands", "dunes", "wastes", "barrens"]}
            
            name = f"The {random.choice(adjectives).title()} {random.choice(nouns[location_type]).title()}"
            
            # Determine magical properties based on location type
            magical_aura_options = {
                "cave": ["EARTH", "VOID", "SPIRIT"],
                "forest": ["LIFE", "EARTH", "SPIRIT"],
                "mountain": ["EARTH", "AIR", "FIRE"],
                "lake": ["WATER", "LIFE", "SPIRIT"],
                "ruins": ["MIND", "SPIRIT", "VOID"],
                "swamp": ["LIFE", "WATER", "VOID"],
                "beach": ["WATER", "AIR", "EARTH"],
                "volcano": ["FIRE", "EARTH", "VOID"],
                "glacier": ["WATER", "AIR", "VOID"],
                "desert": ["FIRE", "AIR", "SPIRIT"]
            }
            
            magical_aura = random.choice(magical_aura_options[location_type])
            leyline_strength = round(random.uniform(1.0, 4.0), 1)
            corruption_level = round(random.uniform(0.0, 0.5), 1) if random.random() < 0.2 else 0.0
            
            # More exotic locations have higher discovery difficulty
            base_difficulty = {"cave": 3, "forest": 1, "mountain": 4, "lake": 2, 
                               "ruins": 5, "swamp": 3, "beach": 1, "volcano": 5, 
                               "glacier": 4, "desert": 3}
            discovery_difficulty = min(10, base_difficulty[location_type] + random.randint(0, 3))
            
            # Generate available materials based on location type and magical aura
            available_materials = {}
            
            # Get list of potential materials from the database
            all_materials = session.query(MagicalMaterial).all()
            
            # Filter materials by location type and magical affinity
            suitable_materials = []
            for material in all_materials:
                # Check if location type matches
                if location_type in material.primary_locations:
                    suitable_materials.append(material)
                # Check if magical affinity matches
                elif magical_aura in material.magical_affinity:
                    suitable_materials.append(material)
            
            # Add some additional random materials
            additional_materials = [m for m in all_materials if m not in suitable_materials]
            if additional_materials:
                suitable_materials.extend(random.sample(additional_materials, min(2, len(additional_materials))))
            
            # Select 3-5 materials for this location
            selected_materials = random.sample(suitable_materials, min(random.randint(3, 5), len(suitable_materials)))
            
            # Set availability chances based on rarity
            rarity_chances = {
                "common": (0.4, 0.7),
                "uncommon": (0.2, 0.5),
                "rare": (0.1, 0.3),
                "legendary": (0.05, 0.15)
            }
            
            for material in selected_materials:
                rarity = material.rarity
                min_chance, max_chance = rarity_chances.get(rarity, (0.1, 0.3))
                available_materials[material.id] = round(random.uniform(min_chance, max_chance), 2)
            
            # Create location data
            location_data = {
                "id": f"{region}_{location_type}_{i+1}",
                "region_id": region,
                "name": name,
                "location_type": location_type,
                "coordinates": {"x": random.randint(1, 1000), "y": random.randint(1, 1000)},
                "available_materials": available_materials,
                "current_abundance": 1.0,
                "leyline_strength": leyline_strength,
                "magical_aura": magical_aura,
                "corruption_level": corruption_level,
                "is_discovered": random.random() < 0.3,  # 30% chance to be discovered by default
                "discovery_difficulty": discovery_difficulty,
                "last_refresh": datetime.utcnow()
            }
            
            locations.append(location_data)
    
    # Add locations to database
    for location_data in locations:
        location = MagicalGatheringLocation(**location_data)
        session.add(location)
    
    # Commit changes
    session.commit()
    print(f"Added {len(locations)} magical gathering locations to the database.")
    session.close()

def seed_all():
    """Seed all magic crafting data"""
    seed_magical_materials()
    seed_enchantments()
    seed_crafting_stations()
    seed_gathering_locations()
    print("Magic crafting seed data complete!")

if __name__ == "__main__":
    seed_all()