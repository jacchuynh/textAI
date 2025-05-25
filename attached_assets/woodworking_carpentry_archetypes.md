# Woodworking & Carpentry Materials

## Raw & Processed Woods

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                               | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                                      |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------------------------ | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pine Log (Rough Cut)             | WOOD_RAW        | COMMON     | 2            | 15.0     | False          | `["harvested_verdant_frontier_pine_forests", "common_softwood_lumber"]`                     | `[]`                 | `{"processes_into": "Pine Planks", "density_kg_m3": 450, "hardness_janka_lbf": 380, "workability": "easy", "knot_frequency": "medium", "resin_content": "medium_high", "uses_raw": ["firewood", "rough_shelter_construction"]}` |
| Pine Planks (Bundle of 5)        | WOOD_PROCESSED  | COMMON     | 5            | 5.0      | True           | `["milled_pine_logs_rivemark_sawmill", "basic_construction_material"]`                      | `[]`                 | `{"dimensions_cm_each_plank": "200x20x2.5", "finish": "rough_sawn", "nail_holding_ability": "fair", "splinter_risk": "medium", "uses": ["simple_furniture", "crates", "fences", "flooring_sublayer"]}`                          |
| Oak Log (Seasoned)               | WOOD_RAW        | UNCOMMON   | 15           | 25.0     | False          | `["harvested_whispering_woods_oak_groves_aged_one_year", "durable_hardwood_lumber"]`        | `[]`                 | `{"processes_into": "Oak Beams_Oak Planks", "density_kg_m3": 720, "hardness_janka_lbf": 1290, "workability": "moderate_requires_sharp_tools", "tannin_content": "high_corrodes_iron_fasteners", "strength": "high"}`    |
| Oak Planks (Bundle of 3)         | WOOD_PROCESSED  | UNCOMMON   | 25           | 7.0      | True           | `["milled_seasoned_oak_logs_skarport_carpentry_guild", "high_quality_furniture_construction"]`| `[]`                 | `{"dimensions_cm_each_plank": "200x15x3", "finish": "planed_smooth", "nail_holding_ability": "good", "stain_affinity": "excellent", "uses": ["fine_furniture", "weapon_hafts", "ship_decking", "heavy_doors"]}`         |
| Ash Wood Branches (Bundle)       | WOOD_RAW        | COMMON     | 3            | 4.0      | False          | `["pruned_verdant_frontier_ash_trees_tool_handles", "flexible_strong_wood"]`                | `[]`                 | `{"processes_into": "Ash Staves_Tool Handles", "flexibility": "high", "shock_resistance": "excellent", "workability": "good", "uses_raw": ["temporary_tool_handles", "kindling"]}`                                     |
| Ironwood Log (Small)             | WOOD_RAW        | RARE       | 50           | 30.0     | False          | `["harvested_deep_whispering_woods_ironwood_trees_orcish_preference", "extremely_hard_wood"]` | `[]`                 | `{"processes_into": "Ironwood Planks_Ironwood Blocks", "density_kg_m3": 950, "hardness_janka_lbf": 3200, "workability": "very_difficult_blunts_tools", "strength": "exceptional", "uses": ["weapon_hafts", "fortifications"]}` |
| Ironwood Planks (Single)         | WOOD_PROCESSED  | RARE       | 70           | 8.0      | True           | `["milled_ironwood_log_orcish_master_carpenter_rivemark", "premium_impact_resistant_wood"]` | `[]`                 | `{"dimensions_cm_plank": "150x20x4", "finish": "rough_difficult_to_plane", "nail_holding_ability": "poor_requires_drilling", "uses": ["heavy_weapon_components", "shield_cores", "reinforced_structures"]}`          |
| Lethandrel Spiritwood Branch     | WOOD_MAGICAL    | EPIC       | 400          | 1.5      | False          | `["ethically_harvested_lethandrel_ancient_spirit_trees_elven_ritual", "mana_infused_wood"]` | `["Stonewake_unlicensed"]` | `{"processes_into": "Spiritwood Wand_Staff Core_Enchanted Carvings", "mana_conductivity": "high", "natural_wards": "minor_vs_undead_corruption", "workability": "easy_responds_to_elven_tools_chants", "glows_faintly": true}` |
| Shimmering Marshes Mangrove Root | WOOD_RAW        | UNCOMMON   | 10           | 8.0      | False          | `["harvested_shimmering_marshes_mangrove_water_logged_wood", "rot_resistant_wood"]`        | `[]`                 | `{"processes_into": "Mangrove Planks_Carved Fetishes", "water_resistance": "very_high", "salt_resistance": "high", "workability": "moderate_stringy_fibers", "density": "medium_light_when_dried", "uses": ["boat_parts", "dock_pilings"]}` |
| Petrified Wood Chunk             | WOOD_MINERAL    | RARE       | 60           | 5.0      | False          | `["found_ember_wastes_ancient_forest_remains_fossilized_wood", "stone_like_wood"]`         | `[]`                 | `{"processes_into": "Petrified Wood Carvings_Inlays", "hardness_mohs": 7, "workability": "difficult_requires_stone_tools_or_magic", "appearance": "polished_stone_wood_grain", "uses": ["durable_ornaments", "weapon_pommels"]}` |

## Adhesives, Finishes & Fasteners (Wood Specific)

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                               | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                                  |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------------------------ | :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pine Resin (Lump)                | RESIN           | COMMON     | 1            | 0.1      | False          | `["tapped_pine_trees_verdant_frontier", "sticky_natural_adhesive_waterproofer"]`            | `[]`                 | `{"use": "crude_adhesive_waterproofing_torches", "melting_point_celsius": 70, "flammability": "high", "processed_into": "Pine Tar_Pitch"}`                                                                               |
| Animal Hide Glue (Pot)           | ADHESIVE        | COMMON     | 3            | 0.2      | True           | `["rendered_animal_hides_bones_traditional_wood_glue", "strong_brittle_glue"]`              | `[]`                 | `{"bond_strength_psi": 3000, "shelf_life_prepared_days": 7, "application_method": "hot_brush", "water_resistance": "low", "reversibility": "with_heat_moisture"}`                                                             |
| Beeswax Polish (Tin)             | FINISH          | UNCOMMON   | 8            | 0.1      | True           | `["beeswax_linseed_oil_blend_human_craft", "natural_wood_finish_and_protector"]`            | `[]`                 | `{"finish_type": "soft_sheen_water_resistant", "application_method": "cloth_buff", "drying_time_hours": 2, "scent": "honey_mild", "enhances_wood_grain": true}`                                                               |
| Elven Moonpetal Varnish (Vial)   | FINISH_MAGICAL  | RARE       | 50           | 0.05     | True           | `["lethandrel_alchemical_preparation_moonpetal_essence_tree_saps", "magically_protective_finish"]` | `[]`                 | `{"finish_type": "hard_clear_magically_resonant", "application_method": "fine_brush_moonlight_curing", "drying_time_hours": 12_under_moon", "enhances_mana_conductivity_of_wood": true, "minor_warding_properties": true}` |
| Wooden Dowels (Bag of 50)        | FASTENER_WOOD   | COMMON     | 2            | 0.3      | True           | `["turned_hardwood_pegs_joinery_component", "metal_free_fastening"]`                        | `[]`                 | `{"material": "oak_birch", "diameter_mm": 8, "length_cm": 5, "strength": "good_in_shear", "quantity": 50, "use": "furniture_joinery_reinforcement"}`                                                                     |
| Iron Wood Screws (Box of 20)     | FASTENER_METAL  | COMMON     | 4            | 0.2      | True           | `["forged_iron_threaded_screws_skarport_smithies", "strong_wood_fasteners"]`                 | `[]`                 | `{"material": "iron", "length_cm": 4, "thread_type": "coarse_wood", "head_type": "flat_slot", "quantity": 20, "rust_prone": true_if_not_oiled}`                                                                        |

<br/>
<hr/>
<br/>

# Woodworking & Carpentry Recipes

## Basic Construction & Furniture

---
**Recipe Archetype 42: Simple Pine Crate**

*   **Recipe Table Entry:**
    *   `id`: (UUID)
    *   `name`: "Simple Pine Crate"
    *   `description`: "A roughly constructed pine crate, suitable for storing or transporting common goods. Not very secure, but cheap and easy to make."
    *   `recipe_category`: "Container - Crate (Small)"
    *   `crafting_time_seconds`: 900
    *   `required_station_type`: "Carpenter's Sawhorse & Basic Tools"
    *   `difficulty_level`: 1
    *   `is_discoverable`: False (Common knowledge)
    *   `experience_gained`: `[{"skill_name": "Carpentry", "amount": 20}]`
    *   `quality_range`: `{"min": 1, "max": 3}` (Quality affects sturdiness and joinery tightness)
    *   `custom_data`: `{"internal_volume_liters": 50, "max_weight_capacity_kg": 20, "lid_type": "loose_or_nailed_shut"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Pine Planks (Bundle of 5)): `quantity`: 1 (i.e., 5 planks), `consumed_in_crafting`: True
    *   `item_id` (Iron Nails (Bag of 100)): `quantity`: 0.2 (i.e., 20 nails), `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Simple Pine Crate): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Carpentry", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 43: Sturdy Oak Stool**

*   **Recipe Table Entry:**
    *   `name`: "Sturdy Oak Stool"
    *   `description`: "A robust, four-legged stool made from solid oak. Built to last and can withstand heavy use in a home, workshop, or tavern."
    *   `recipe_category`: "Furniture - Seating (Basic)"
    *   `crafting_time_seconds`: 2400
    *   `required_station_type`: "Woodworker's Bench with Joinery Tools"
    *   `difficulty_level`: 3
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Woodworking (Furniture)", "amount": 50}]`
    *   `quality_range`: `{"min": 2, "max": 6}` (Quality affects stability, finish, and comfort)
    *   `custom_data`: `{"seat_height_cm": 45, "weight_capacity_kg": 150, "joinery_type": "mortise_and_tenon_pegged"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Oak Planks (Bundle of 3)): `quantity`: 1 (i.e., 3 planks), `consumed_in_crafting`: True
    *   `item_id` (Wooden Dowels (Bag of 50)): `quantity`: 0.2 (i.e., 10 dowels), `consumed_in_crafting`: True
    *   `item_id` (Animal Hide Glue (Pot)): `quantity`: 0.1, `consumed_in_crafting`: True
    *   `item_id` (Beeswax Polish (Tin) - optional finish): `quantity`: 0.1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Sturdy Oak Stool): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Woodworking (Furniture)", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Joinery", `level`: 1, `affects_quality`: True

## Tools & Weapon Components

---
**Recipe Archetype 44: Ash Tool Handle (Axe/Hammer)**

*   **Recipe Table Entry:**
    *   `name`: "Ash Tool Handle (Axe/Hammer)"
    *   `description`: "A strong and flexible tool handle crafted from ash wood, suitable for axes, hammers, or similar hafted tools. Provides good shock absorption."
    *   `recipe_category`: "Tool Component - Handle"
    *   `crafting_time_seconds`: 600
    *   `required_station_type`: "Shaving Horse & Spokeshave"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Woodworking (Toolmaking)", "amount": 25}]`
    *   `quality_range`: `{"min": 1, "max": 5}` (Quality affects durability and grip comfort)
    *   `custom_data`: `{"length_cm": 60, "grip_shape": "oval_ergonomic", "grain_orientation_critical": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Ash Wood Branches (Bundle)): `quantity`: 1 (select suitable branch), `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Ash Tool Handle): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Woodworking (Toolmaking)", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 45: Orcish Ironwood Warclub Head**

*   **Recipe Table Entry:**
    *   `name`: "Orcish Ironwood Warclub Head"
    *   `description`: "A brutally heavy and dense warclub head carved from a block of ironwood. Designed by Orcish crafters for maximum impact. Often has protrusions or a roughly shaped point."
    *   `recipe_category`: "Weapon Component - Bludgeon Head"
    *   `crafting_time_seconds`: 3600
    *   `required_station_type`: "Orcish Carving Stump & Heavy Chisels"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"observed_orcish_weaponmaster_crafting": true, "skill_name": "Orcish Woodcraft", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Woodworking (Weapons)", "amount": 100}, {"skill_name": "Orcish Woodcraft", "amount": 70}]`
    *   `quality_range`: `{"min": 3, "max": 7}` (Quality affects weight distribution, impact force, and chance to splinter on critical hits)
    *   `custom_data`: `{"weight_kg": 3.5, "impact_modifier_blunt": 1.3, "haft_socket_type": "large_reinforced_taper"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Ironwood Log (Small) - portion of): `quantity`: 0.5, `consumed_in_crafting`: True (or 1 Ironwood Block if you make that an intermediate)
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Orcish Ironwood Warclub Head): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Woodworking (Weapons)", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Orcish Woodcraft", `level`: 2, `affects_quality`: True, `affects_speed`: True

---
**Recipe Archetype 46: Elven Spiritwood Staff Core (Unenchanted)**

*   **Recipe Table Entry:**
    *   `name`: "Elven Spiritwood Staff Core (Unenchanted)"
    *   `description`: "A perfectly balanced and resonant staff core carved from a branch of Lethandrel Spiritwood. It hums faintly with latent mana and is ready for enchanting or further magical embellishment."
    *   `recipe_category`: "Weapon Component - Magical Staff Core"
    *   `crafting_time_seconds`: 10800 (Includes meditative carving)
    *   `required_station_type`: "Elven Moonlit Carving Grove"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"elven_master_guidance_lethandrel": true, "skill_name": "Elven Sacred Carving", "level": 5, "item_possessed": "Lethandrel Spiritwood Branch"}`
    *   `experience_gained`: `[{"skill_name": "Woodworking (Magical)", "amount": 500}, {"skill_name": "Elven Sacred Carving", "amount": 300}, {"skill_name": "Mana Attunement", "amount": 50}]`
    *   `quality_range`: `{"min": 5, "max": 9}` (Quality affects mana conductivity, balance, and receptiveness to enchantments)
    *   `custom_data`: `{"length_cm": 150, "mana_conductivity_rating_base": 7, "weight_kg": 0.8, "natural_wards_strength": "quality_dependent", "requires_finishing_varnish": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Lethandrel Spiritwood Branch): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Purified Leyline Water - for cleansing wood): `quantity`: 0.1, `consumed_in_crafting`: True
    *   `item_id` (Elven Carving Knives - tool, not consumed): `quantity`: 1, `consumed_in_crafting`: False
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Elven Spiritwood Staff Core): `quantity`: 1, `is_primary`: True, `chance`: 0.95 (delicate, can be ruined)
    *   `item_id` (Spiritwood Shavings - minor magical essence): `quantity`: 1, `is_primary`: False, `chance`: 0.5
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Woodworking (Magical)", `level`: 6, `affects_quality`: True
    *   `skill_name`: "Elven Sacred Carving", `level`: 4, `affects_quality`: True, `affects_speed`: False (cannot rush)

## Shields & Armor Components

---
**Recipe Archetype 47: Round Pine Shield (Basic)**

*   **Recipe Table Entry:**
    *   `name`: "Round Pine Shield (Basic)"
    *   `description`: "A simple, lightweight round shield made from cross-laminated pine planks. Offers minimal protection but is easy to carry. Often used by bandits or very green recruits."
    *   `recipe_category`: "Armor - Shield (Light Wood)"
    *   `crafting_time_seconds`: 1800
    *   `required_station_type`: "Shieldwright's Bench"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Woodworking (Armor)", "amount": 40}]`
    *   `quality_range`: `{"min": 1, "max": 3}` (Quality affects durability against blows)
    *   `custom_data`: `{"block_chance_modifier": 0.05, "durability_hp_base": 50, "weight_kg": 2.0, "requires_boss_and_straps": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Pine Planks (Bundle of 5)): `quantity`: 1 (i.e., 5 planks), `consumed_in_crafting`: True
    *   `item_id` (Animal Hide Glue (Pot)): `quantity`: 0.2, `consumed_in_crafting`: True
    *   `item_id` (Rough Patchwork Leather - for straps): `quantity`: 0.5, `consumed_in_crafting`: True
    *   `item_id` (Iron Ingot - for crude boss, or pre-made boss): `quantity`: 0.2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Round Pine Shield): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Woodworking (Armor)", `level`: 1, `affects_quality`: True
    *   `skill_name`: "Carpentry", `level`: 1, `affects_quality`: False

---
**Recipe Archetype 48: Laminated Ash Recurve Bow (Unstrung)**

*   **Recipe Table Entry:**
    *   `name`: "Laminated Ash Recurve Bow (Unstrung)"
    *   `description`: "The carefully shaped wooden body of a recurve bow, made from laminated strips of ash wood for flexibility and power. Requires a bowstring to be functional. Favored by Rivemark hunters."
    *   `recipe_category`: "Weapon - Bow (Unstrung)"
    *   `crafting_time_seconds`: 5400
    *   `required_station_type`: "Bowyer's Bench with Steaming Rig"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"apprenticeship_with_rivemark_bowyer": true, "skill_name": "Bowyer/Fletcher", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Woodworking (Weapons)", "amount": 150}, {"skill_name": "Bowyer/Fletcher", "amount": 100}]`
    *   `quality_range`: `{"min": 3, "max": 7}` (Quality affects draw weight, accuracy potential, and durability)
    *   `custom_data`: `{"potential_draw_weight_lbs_base": 40, "arrow_velocity_modifier_base": 1.1, "requires_stringing_skill": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Ash Wood Branches (Bundle) - select straightest, knot-free pieces): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Animal Hide Glue (Pot) - strong variant): `quantity`: 0.3, `consumed_in_crafting`: True
    *   `item_id` (Linen Thread Spool (100m) - for wrapping grips): `quantity`: 0.1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Laminated Ash Recurve Bow (Unstrung)): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Woodworking (Weapons)", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Bowyer/Fletcher", `level`: 2, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Wood Bending & Lamination", `level`: 2, `affects_quality`: True

---
This set should give a good starting point for woodworking, covering practical items, furniture, tools, and components for weapons and armor, with cultural touches.

What craft shall we explore next?
1.  **Jewelcrafting & Gemcutting**
2.  **Scribing & Scroll Making**
3.  **Ritual Crafting & Totem Carving**
4.  **Cooking & Provisioning**
5.  Or something else?