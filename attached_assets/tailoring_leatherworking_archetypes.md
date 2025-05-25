# Tailoring & Leatherworking Materials

## Fibers & Cloths

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                              | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                                |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :----------------------------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Roughspun Linen Bolt (10m)       | CLOTH           | COMMON     | 5            | 1.0      | True           | `["processed_flax_verdant_frontier_farms", "basic_textile"]`                               | `[]`                 | `{"thread_count": "low", "durability": "medium_low", "comfort": "scratchy_initially", "dye_affinity": "good_natural_dyes", "insulation_value": "low", "length_meters": 10}`                                           |
| Cotton Bolt (10m)                | CLOTH           | COMMON     | 8            | 0.8      | True           | `["harvested_cotton_rivemark_delta_plantations", "soft_common_textile"]`                   | `[]`                 | `{"thread_count": "medium", "durability": "medium", "comfort": "good", "dye_affinity": "excellent", "breathability": "high", "length_meters": 10}`                                                                    |
| Woolen Cloth Bolt (Heavy, 5m)    | CLOTH           | UNCOMMON   | 15           | 1.5      | True           | `["sheared_highland_sheep_crystal_highlands_processed_human_settlements", "warm_textile"]` | `[]`                 | `{"thread_count": "medium_thick", "durability": "high", "comfort": "good_itchy_if_coarse", "dye_affinity": "good", "insulation_value": "high_water_resistant_naturally", "length_meters": 5}`                               |
| Skarport Merchant's Silk (5m)    | CLOTH           | RARE       | 70           | 0.3      | True           | `["imported_silkworm_cocoons_processed_skarport_guilds", "luxury_textile"]`                | `[]`                 | `{"thread_count": "very_high_fine", "durability": "medium_delicate", "comfort": "excellent_smooth", "dye_affinity": "superb_vibrant_colors", "insulation_value": "medium_surprisingly_warm", "length_meters": 5, "status_symbol": true}` |
| Lethandrel Spider-Silk Thread (Spool)| MAGICAL    | EPIC       | 200          | 0.05     | False          | `["harvested_lethandrel_mana_infused_spiders_whispering_woods_elven_collection", "magical_fiber"]` | `[]`                 | `{"strength_to_weight_ratio": "extremely_high", "mana_conductivity": "low_but_stable", "durability": "exceptional", "use": "enchanted_clothing_bowstrings_suture_thread", "length_meters_per_spool": 50}`                  |
| Beastfolk Woven Reed Matting (Large)| PLANT_FIBER  | UNCOMMON   | 10           | 2.0      | True           | `["harvested_shimmering_marshes_reeds_beastfolk_weaving_ashkar_vale", "rugged_natural_material"]`| `[]`                 | `{"durability": "good_for_mats_crude_armor_backing", "comfort": "rough", "water_resistance": "moderate", "insulation_value": "low", "size": "2x2_meters"}`                                                              |
| Ferverl Desert Linen (Heat-Treated, 5m)| CLOTH   | RARE       | 40           | 0.7      | True           | `["thal_zirad_flax_processed_ferverl_heat_ritual", "heat_resistant_breathable_cloth"]`      | `[]`                 | `{"thread_count": "medium_fine", "durability": "good", "comfort": "excellent_in_heat", "dye_affinity": "poor_resists_most_dyes", "insulation_value_vs_heat": "high", "length_meters": 5}`                             |
| Canvas Bolt (Heavy Duty, 5m)     | CLOTH           | UNCOMMON   | 12           | 2.0      | True           | `["thick_hemp_or_cotton_weave_rivemark_sailmakers_skarport_docks", "tough_utility_fabric"]` | `[]`                 | `{"thread_count": "very_thick_coarse", "durability": "very_high_abrasion_resistant", "comfort": "low_stiff", "water_resistance": "good_if_waxed", "uses": ["sails", "tents", "heavy_bags", "workwear"], "length_meters": 5}` |

## Leathers & Hides

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                                 | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                             |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :-------------------------------------------------------------------------------------------- | :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Raw Deer Hide (Medium)           | HIDE            | COMMON     | 4            | 1.5      | False          | `["hunted_verdant_frontier_deer", "untanned_animal_skin"]`                                      | `[]`                 | `{"tans_into": "Buckskin Leather", "size_approx_sq_meters": 1.5, "quality_potential": "medium", "preservation_needed_quickly": true}`                                                                              |
| Buckskin Leather (Medium Piece)  | LEATHER         | COMMON     | 10           | 0.7      | True           | `["tanned_deer_hide_human_beastfolk_craft", "soft_flexible_leather"]`                           | `[]`                 | `{"thickness_mm": 1.5, "flexibility": "high", "durability": "medium", "comfort": "good", "water_resistance": "low_unless_treated", "uses": ["light_armor", "clothing", "pouches"]}`                                   |
| Boar Hide (Tough)                | HIDE            | UNCOMMON   | 12           | 2.5      | False          | `["hunted_whispering_woods_boar_rivemark_farmland_pest", "thick_bristly_hide"]`                   | `[]`                 | `{"tans_into": "Tough Boar Leather", "size_approx_sq_meters": 1.2, "quality_potential": "medium_high_scarring_common", "bristle_removal_required": true}`                                                                |
| Tough Boar Leather (Piece)       | LEATHER         | UNCOMMON   | 25           | 1.2      | True           | `["tanned_boar_hide_orcish_preference", "rigid_protective_leather"]`                            | `[]`                 | `{"thickness_mm": 3, "flexibility": "low", "durability": "high_impact_resistant", "comfort": "low_requires_padding", "uses": ["medium_armor_jackets", "shield_facings", "tool_sheaths"]}`                               |
| Giant Lizard Scale Hide (Large)  | EXOTIC_HIDE     | RARE       | 60           | 3.0      | False          | `["hunted_ember_wastes_sand_lizard_beastfolk_ferverl_hunt", "scaled_reptilian_hide"]`            | `[]`                 | `{"tans_into": "Scaled Leather", "size_approx_sq_meters": 2.0, "scale_hardness": "medium", "flexibility_between_scales": "good", "heat_resistance": "good"}`                                                              |
| Scaled Leather (Large Piece)     | EXOTIC_LEATHER  | RARE       | 120          | 1.4      | True           | `["tanned_lizard_scale_hide_ashkar_vale_specialty", "naturally_armored_leather"]`               | `[]`                 | `{"thickness_mm_scales": 4, "flexibility": "medium", "durability": "high_good_pierce_resistance", "comfort": "medium_can_be_stiff", "uses": ["exotic_armor", "decorative_pieces", "helmets"]}`                               |
| Shadow Panther Pelt (Prime)      | EXOTIC_HIDE     | EPIC       | 350          | 1.0      | False          | `["hunted_whispering_woods_master_shadow_panther_elven_beastfolk_stalkers", "magically_infused_pelt"]`| `[]`                 | `{"tans_into": "Shadow-Walker Leather", "size_approx_sq_meters": 1.0, "innate_property": "blends_with_shadows", "fur_quality": "exceptional_soft_dark", "magical_aura": "faint_illusion"}`                               |
| Shadow-Walker Leather (Piece)    | EXOTIC_LEATHER  | LEGENDARY  | 700          | 0.4      | True           | `["tanned_shadow_panther_pelt_secret_elven_process", "leather_of_stealth_and_night"]`         | `[]`                 | `{"thickness_mm": 1, "flexibility": "very_high", "durability": "good_magically_resilient", "comfort": "superb", "innate_ability": "minor_stealth_bonus_in_dim_light", "enchantment_affinity": "illusion_shadow_magic"}` |
| Crude Beastfolk Hide Scraps      | HIDE            | COMMON     | 1            | 0.5      | False          | `["butchering_byproduct_ashkar_vale_various_beasts", "untanned_mixed_quality_scraps"]`          | `[]`                 | `{"tans_into": "Rough Patchwork Leather", "size_approx_sq_meters": "variable_small_pieces", "usability": "low_good_for_bindings_padding_filler"}`                                                                        |
| Rough Patchwork Leather          | LEATHER         | COMMON     | 3            | 0.2      | True           | `["tanned_stitched_hide_scraps_beastfolk_utility_craft", "low_grade_functional_leather"]`       | `[]`                 | `{"thickness_mm": "variable", "flexibility": "medium", "durability": "low_prone_to_tearing_at_seams", "comfort": "poor", "uses": ["crude_pouches", "armor_padding", "tent_repairs"]}`                                  |

## Threads, Fasteners & Dyes

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                              | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                               |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :----------------------------------------------------------------------------------------- | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Linen Thread Spool (100m)        | THREAD          | COMMON     | 2            | 0.02     | True           | `["spun_flax_fibers_common_sewing_thread"]`                                                | `[]`                 | `{"tensile_strength_kg": 2, "thickness": "standard", "color": "natural_undyed", "length_meters": 100}`                                                                                                               |
| Heavy Woolen Yarn (50m)          | THREAD          | UNCOMMON   | 5            | 0.05     | True           | `["spun_wool_fibers_thick_yarn_for_knitting_heavy_stitching"]`                             | `[]`                 | `{"tensile_strength_kg": 5, "thickness": "thick", "color": "natural_undyed_cream", "length_meters": 50, "insulating_when_stitched": true}`                                                                            |
| Sinew Thread (Dried, 20m)        | THREAD          | UNCOMMON   | 8            | 0.01     | True           | `["processed_animal_tendons_beastfolk_orcish_craft_strong_natural_thread"]`                | `[]`                 | `{"tensile_strength_kg": 10, "thickness": "medium_variable", "color": "brownish_translucent", "length_meters": 20, "water_resistance_swells_when_wet": true, "notes": "Shrinks as it dries, making tight seams."}`        |
| Silk Thread Spool (Gilded, 20m)  | THREAD          | RARE       | 30           | 0.005    | True           | `["skarport_silk_thread_infused_with_gold_dust_decorative_embroidery"]`                    | `[]`                 | `{"tensile_strength_kg": 1, "thickness": "very_fine", "color": "gold_shimmer", "length_meters": 20, "decorative_only": true, "enchantment_conduit_minor": true}`                                                          |
| Wooden Buttons (Dozen)           | FASTENER        | COMMON     | 1            | 0.01     | True           | `["carved_common_wood_simple_clothing_fasteners"]`                                         | `[]`                 | `{"material": "ash_pine", "size_mm": 15, "durability": "medium_can_split", "quantity": 12}`                                                                                                                            |
| Bone Toggles (Half Dozen)        | FASTENER        | UNCOMMON   | 4            | 0.02     | True           | `["carved_polished_animal_bone_beastfolk_ashkar_vale_style", "rugged_fasteners"]`           | `[]`                 | `{"material": "deer_boar_bone", "size_mm_length": 30, "durability": "high_can_chip", "quantity": 6, "style": "tribal_rustic"}`                                                                                             |
| Bronze Clasps (Pair)             | FASTENER        | UNCOMMON   | 10           | 0.03     | True           | `["cast_bronze_fittings_skarport_human_craft", "sturdy_decorative_clasps_for_cloaks_armor"]` | `[]`                 | `{"material": "bronze", "size_mm_each": "25x40", "durability": "very_good", "mechanism": "hook_and_eye_interlocking", "quantity": 2}`                                                                                    |
| Madder Root Dye (Red Pigment)    | DYE             | COMMON     | 3            | 0.05     | True           | `["processed_madder_root_verdant_frontier_natural_dye"]`                                   | `[]`                 | `{"color_imparted": "rustic_red_orange_tones", "fabric_suitability": ["linen", "cotton", "wool"], "permanence": "good_fades_slowly_with_sun", "quantity_sufficient_for_bolt_of_cloth": 1}`                             |
| Indigo Leaf Paste (Blue Pigment) | DYE             | UNCOMMON   | 8            | 0.05     | True           | `["fermented_indigo_leaves_rivemark_specialty_crop", "rich_blue_dye"]`                     | `[]`                 | `{"color_imparted": "deep_blue_to_sky_blue_depending_on_concentration", "fabric_suitability": ["cotton", "silk", "linen"], "permanence": "excellent", "quantity_sufficient_for_bolt_of_cloth": 1}`                |
| Soot Black Pigment Pouch         | DYE             | COMMON     | 2            | 0.03     | True           | `["collected_fine_soot_purified_basic_black_dye"]`                                         | `[]`                 | `{"color_imparted": "dull_black_greyish_tones", "fabric_suitability": ["wool", "rough_leathers"], "permanence": "medium_can_rub_off", "quantity_sufficient_for_garment_or_leather_piece": 1}`                        |

<br/>
<hr/>
<br/>

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