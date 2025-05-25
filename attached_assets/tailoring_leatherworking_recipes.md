
# Tailoring & Leatherworking Recipes

## Basic Clothing & Accessories

---
**Recipe Archetype 34: Simple Linen Tunic**

*   **Recipe Table Entry:**
    *   `id`: (UUID)
    *   `name`: "Simple Linen Tunic"
    *   `description`: "A basic, practical tunic made from roughspun linen. Common everyday wear for peasants, laborers, and new adventurers across most human lands."
    *   `recipe_category`: "Clothing - Torso (Basic)"
    *   `crafting_time_seconds`: 1200
    *   `required_station_type`: "Tailor's Bench with Needle & Thread"
    *   `difficulty_level`: 1
    *   `is_discoverable`: False (Fundamental pattern)
    *   `experience_gained`: `[{"skill_name": "Tailoring", "amount": 20}]`
    *   `quality_range`: `{"min": 1, "max": 4}` (Quality affects comfort, seam strength, and appearance)
    *   `custom_data`: `{"insulation_value": "low", "layerable": true, "common_sizes": ["S", "M", "L"]}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Roughspun Linen Bolt (10m)): `quantity`: 0.3 (i.e., 3 meters), `consumed_in_crafting`: True
    *   `item_id` (Linen Thread Spool (100m)): `quantity`: 0.1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Simple Linen Tunic): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Tailoring", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 35: Sturdy Leather Belt**

*   **Recipe Table Entry:**
    *   `name`: "Sturdy Leather Belt"
    *   `description`: "A wide, durable belt made from buckskin or similar leather, with a simple metal buckle. Essential for holding up trousers, carrying pouches, or hanging a scabbard."
    *   `recipe_category`: "Accessory - Belt"
    *   `crafting_time_seconds`: 900
    *   `required_station_type`: "Leatherworker's Bench with Awl & Knife"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Leatherworking", "amount": 25}]`
    *   `quality_range`: `{"min": 1, "max": 5}` (Quality affects durability and buckle strength)
    *   `custom_data`: `{"attachment_points_for_pouches": 2, "buckle_material_default": "iron"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Buckskin Leather (Medium Piece)): `quantity`: 0.5, `consumed_in_crafting`: True
    *   `item_id` (Sinew Thread (Dried, 20m)): `quantity`: 0.2, `consumed_in_crafting`: True
    *   `item_id` (Iron Ingot - for buckle, or pre-made buckle): `quantity`: 0.1, `can_be_substituted`: True, `possible_substitutes`: `["Bronze Buckle Blank", "Steel Buckle Blank"]`, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Sturdy Leather Belt): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Leatherworking", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 36: Woolen Traveler's Cloak**

*   **Recipe Table Entry:**
    *   `name`: "Woolen Traveler's Cloak"
    *   `description`: "A heavy, warm cloak made from woolen cloth, often with a hood. Provides good protection against cold and light rain. A common sight on the roads of Rivemark and the northern regions."
    *   `recipe_category`: "Clothing - Cloak (Warm)"
    *   `crafting_time_seconds`: 3600
    *   `required_station_type`: "Tailor's Bench with Heavy Duty Needle"
    *   `difficulty_level`: 3
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"pattern_purchased": "Rivemark_Tailors_Guild_Cloak_Pattern", "skill_name": "Tailoring", "level": 2}`
    *   `experience_gained`: `[{"skill_name": "Tailoring", "amount": 70}]`
    *   `quality_range`: `{"min": 2, "max": 6}` (Quality affects warmth, water resistance, and clasp quality)
    *   `custom_data`: `{"insulation_value": "high", "includes_hood": true, "water_resistance_modifier_base": 0.3}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Woolen Cloth Bolt (Heavy, 5m)): `quantity`: 0.8 (i.e., 4 meters), `consumed_in_crafting`: True
    *   `item_id` (Heavy Woolen Yarn (50m)): `quantity`: 0.5, `consumed_in_crafting`: True
    *   `item_id` (Bronze Clasps (Pair)): `quantity`: 1, `can_be_substituted`: True, `possible_substitutes`: `["Wooden Toggles", "Bone Toggles"]`, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Woolen Traveler's Cloak): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Tailoring", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Heavy Stitching", `level`: 1, `affects_quality`: True (for durability)

## Light & Medium Armor

---
**Recipe Archetype 37: Padded Cloth Armor (Gambeson)**

*   **Recipe Table Entry:**
    *   `name`: "Padded Cloth Armor (Gambeson)"
    *   `description`: "A thick, quilted garment made of multiple layers of linen or canvas. Offers basic protection against blows and cuts, and is often worn under heavier armor or by lightly equipped skirmishers."
    *   `recipe_category`: "Armor - Light Torso"
    *   `crafting_time_seconds`: 5400
    *   `required_station_type`: "Armorer's Tailoring Bench"
    *   `difficulty_level`: 4
    *   `is_discoverable`: False (Standard military/militia pattern)
    *   `experience_gained`: `[{"skill_name": "Tailoring (Armor)", "amount": 120}]`
    *   `quality_range`: `{"min": 2, "max": 5}` (Quality affects padding density and coverage)
    *   `custom_data`: `{"physical_damage_reduction_blunt_base": 0.15, "physical_damage_reduction_slashing_base": 0.1, "weight_kg": 3.0, "can_be_worn_under_mail": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Canvas Bolt (Heavy Duty, 5m)): `quantity`: 0.6 (i.e., 3 meters), `can_be_substituted`: True, `possible_substitutes`: `["Roughspun Linen Bolt (multiple layers)"]`, `consumed_in_crafting`: True
    *   `item_id` (Raw Cotton - for padding, or Wool Scraps): `quantity`: 2.0 (by weight/volume), `consumed_in_crafting`: True
    *   `item_id` (Linen Thread Spool (100m) - Heavy Duty): `quantity`: 0.5, `consumed_in_crafting`: True
    *   `item_id` (Leather Strips - for reinforcement/buckles): `quantity`: 0.5, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Padded Cloth Armor): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Tailoring (Armor)", `level`: 3, `affects_quality`: True
    *   `skill_name`: "Quilting & Padding", `level`: 2, `affects_quality`: True

---
**Recipe Archetype 38: Beastfolk Hide Jerkin**

*   **Recipe Table Entry:**
    *   `name`: "Beastfolk Hide Jerkin"
    *   `description`: "A sleeveless jerkin crafted from tough, untamed beast hides by Ashkar Vale artisans. Offers decent protection while allowing freedom of movement. Often adorned with tribal symbols or fetishes."
    *   `recipe_category`: "Armor - Medium Torso (Tribal)"
    *   `crafting_time_seconds`: 4800
    *   `required_station_type`: "Beastfolk Tanning & Crafting Rack"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"tribal_teaching_ashkar_vale": true, "skill_name": "Beastfolk Leathercraft", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Leatherworking (Armor)", "amount": 150}, {"skill_name": "Beastfolk Leathercraft", "amount": 100}]`
    *   `quality_range`: `{"min": 3, "max": 7}` (Quality affects hide selection, stitching, and spiritual resonance if any)
    *   `custom_data`: `{"physical_damage_reduction_piercing_base": 0.1, "physical_damage_reduction_slashing_base": 0.15, "stamina_regen_penalty_modifier": -0.05, "allows_fetish_attachment_slots": 2}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Tough Boar Leather (Piece)): `quantity`: 2, `can_be_substituted`: True, `possible_substitutes`: `["Scaled Leather (Large Piece) - for higher quality"]`, `consumed_in_crafting`: True
    *   `item_id` (Sinew Thread (Dried, 20m)): `quantity`: 1.0, `consumed_in_crafting`: True
    *   `item_id` (Bone Toggles (Half Dozen)): `quantity`: 0.5 (i.e., 3 toggles), `consumed_in_crafting`: True
    *   `item_id` (Ritual Ochre Pigment - for markings, optional): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Beastfolk Hide Jerkin): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Leatherworking (Armor)", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Beastfolk Leathercraft", `level`: 2, `affects_quality`: True, `affects_speed`: True

---
**Recipe Archetype 39: Rivemark Skirmisher's Leather Cuirass**

*   **Recipe Table Entry:**
    *   `name`: "Rivemark Skirmisher's Leather Cuirass"
    *   `description`: "A practical cuirass made of hardened leather plates stitched onto a softer leather backing. Standard issue for Rivemark militia scouts and light infantry, offering a balance of protection and mobility."
    *   `recipe_category`: "Armor - Medium Torso (Military)"
    *   `crafting_time_seconds`: 7200
    *   `required_station_type`: "Armorer's Leatherworking Bench with Hardening Vat"
    *   `difficulty_level`: 6
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"military_pattern_access_rivemark_quartermaster": true, "skill_name": "Leatherworking (Hardened)", "level": 4}`
    *   `experience_gained`: `[{"skill_name": "Leatherworking (Armor)", "amount": 200}, {"skill_name": "Leatherworking (Hardened)", "amount": 120}]`
    *   `quality_range`: `{"min": 3, "max": 6}` (Quality affects plate fit, hardness, and buckle durability)
    *   `custom_data`: `{"physical_damage_reduction_slashing_base": 0.2, "physical_damage_reduction_blunt_base": 0.1, "weight_kg": 4.5, "mobility_penalty_modifier": -0.1}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Tough Boar Leather (Piece) - for plates): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Buckskin Leather (Medium Piece) - for backing): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Beeswax - for hardening, or special tree sap): `quantity`: 0.5, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings - small): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Bronze Clasps (Pair) - for side buckles): `quantity`: 2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Rivemark Skirmisher's Leather Cuirass): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Leatherworking (Armor)", `level`: 5, `affects_quality`: True
    *   `skill_name`: "Leatherworking (Hardened)", `level`: 3, `affects_quality`: True, `affects_speed`: True

## Bags & Containers

---
**Recipe Archetype 40: Small Belt Pouch**

*   **Recipe Table Entry:**
    *   `name`: "Small Leather Belt Pouch"
    *   `description`: "A simple drawstring pouch made from leather scraps or soft buckskin, designed to be worn on a belt. Useful for carrying coins, herbs, or small trinkets."
    *   `recipe_category`: "Container - Pouch (Small)"
    *   `crafting_time_seconds`: 600
    *   `required_station_type`: "Basic Sewing Kit"
    *   `difficulty_level`: 1
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Leatherworking", "amount": 15}, {"skill_name": "Basic Stitching", "amount": 5}]`
    *   `quality_range`: `{"min": 1, "max": 4}` (Quality affects capacity slightly and durability of drawstring)
    *   `custom_data`: `{"capacity_slots_or_volume_liters": 0.5, "closure_type": "drawstring"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Rough Patchwork Leather): `quantity`: 1, `can_be_substituted`: True, `possible_substitutes`: `["Buckskin Leather (Small Scrap)"]`, `consumed_in_crafting`: True
    *   `item_id` (Linen Thread Spool (100m)): `quantity`: 0.05, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Small Leather Belt Pouch): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Leatherworking", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 41: Adventurer's Backpack (Canvas & Leather)**

*   **Recipe Table Entry:**
    *   `name`: "Adventurer's Backpack (Canvas & Leather)"
    *   `description`: "A sturdy backpack made from heavy canvas with leather reinforcements and straps. Designed to carry a moderate amount of gear for extended journeys. Features multiple external attachment points."
    *   `recipe_category`: "Container - Backpack (Medium)"
    *   `crafting_time_seconds`: 7200
    *   `required_station_type`: "Tailor's & Leatherworker's Combined Bench"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"guild_pattern_skarport_explorers_league": true, "skill_name": "Tailoring", "level": 4, "skill_name": "Leatherworking", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Tailoring", "amount": 150}, {"skill_name": "Leatherworking", "amount": 100}, {"skill_name": "Utility Crafting", "amount": 50}]`
    *   `quality_range`: `{"min": 3, "max": 7}` (Quality affects carrying capacity, durability, and comfort)
    *   `custom_data`: `{"capacity_slots_or_volume_liters": 30, "water_resistance_level_base": "low", "number_of_external_straps": 4, "padded_shoulder_straps": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Canvas Bolt (Heavy Duty, 5m)): `quantity`: 0.5 (i.e., 2.5 meters), `consumed_in_crafting`: True
    *   `item_id` (Buckskin Leather (Medium Piece) - for straps & base): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Heavy Woolen Yarn (50m) - for strong seams): `quantity`: 0.5, `consumed_in_crafting`: True
    *   `item_id` (Bronze Clasps (Pair) - for main flap): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Steel Rings - for attachment points): `quantity`: 4, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Adventurer's Backpack): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Tailoring", `level`: 3, `affects_quality`: True
    *   `skill_name`: "Leatherworking", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Heavy Duty Stitching", `level`: 2, `affects_quality`: True (critical for durability)

---
This set covers a good range for Tailoring & Leatherworking, from basic clothing to functional armor and essential accessories, with cultural flairs.

Next up, we could explore:
1.  **Woodworking & Carpentry**
2.  **Jewelcrafting & Gemcutting**
3.  **Scribing & Scroll Making**
4.  Or another of your choice!