# Blacksmithing & Armorsmithing Materials

## Initial Material Archetypes

| Name                          | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                 | `illicit_in_regions`   | `properties` (JSON Example)                                                                                                                                                                   |
| :---------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :---------------------------------------------------------------------------- | :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ores & Raw Metals**         |                 |            |              |          |                |                                                                               |                        |                                                                                                                                                                                               |
| Rusty Iron Scrap              | METAL           | COMMON     | 0.5          | 0.3      | False          | `["salvaged_ruins", "surface_find"]`                                          | `[]`                   | `{"smelts_into": "Low Quality Iron Ingot", "purity": 0.4, "yield_per_unit": 0.3, "notes": "Requires significant cleaning and processing."}`                                                     |
| Common Iron Ore               | ORE             | COMMON     | 2            | 0.5      | False          | `["mined_stonewake", "mountain_vein", "rivemark_hills"]`                      | `[]`                   | `{"smelts_into": "Iron Ingot", "purity": 0.7, "yield_per_unit": 0.5}`                                                                                                                          |
| Copper Ore                    | ORE             | COMMON     | 3            | 0.4      | False          | `["mined_crystal_highlands", "surface_deposit"]`                              | `[]`                   | `{"smelts_into": "Copper Ingot", "purity": 0.8, "yield_per_unit": 0.6, "conductivity": "high"}`                                                                                                 |
| Tin Ore                       | ORE             | UNCOMMON   | 5            | 0.4      | False          | `["mined_dwarven_foothills", "stream_panned"]`                                | `[]`                   | `{"smelts_into": "Tin Ingot", "purity": 0.6, "alloy_component": "bronze"}`                                                                                                                      |
| Deepvein Silver Ore           | ORE             | UNCOMMON   | 15           | 0.6      | False          | `["mined_dwarven_deepshafts", "anti_undead_trace", "lethandrel_trade_rare"]` | `[]`                   | `{"smelts_into": "Silver Ingot", "purity": 0.85, "magical_conductivity": "low", "value_modifier_vs_undead": 1.1}`                                                                              |
| Stonewake Coal Seam           | ORE             | COMMON     | 1            | 0.2      | False          | `["mined_stonewake_caldera", "fuel_source", "industrial_grade"]`              | `[]`                   | `{"fuel_value": 15, "smoke_level": "medium", "ash_content": "high"}`                                                                                                                            |
| Orcish Blood Iron Ore         | ORE             | RARE       | 40           | 0.7      | False          | `["orcish_sacred_mine", "rivemark_borderlands", "ritual_harvest"]`            | `[]`                   | `{"smelts_into": "Blood Iron Ingot", "purity": 0.6, "innate_property": "minor_life_steal_weapon", "strength_modifier": 1.1, "brittleness_if_impure": "high"}`                                     |
| Dwarven Deep Iron Ore         | ORE             | RARE       | 55           | 0.8      | False          | `["dwarven_ancestral_mine", "stonewake_exclusive", "geothermal_vein"]`        | `[]`                   | `{"smelts_into": "Deep Iron Ingot", "purity": 0.9, "innate_property": "exceptional_hardness", "magic_resistance_armor": "low"}`                                                                 |
| Star Metal Fragment           | METAL           | RARE       | 150          | 0.1      | False          | `["meteorite_fall_crystal_highlands", "celestial_origin", "rare_find"]`     | `[]`                   | `{"hardness": 8, "malleability": 3, "innate_property": "starlight_glow", "affinity_enchantment": "air_lightning", "notes": "Difficult to work."}`                                               |
| Ferverl Sunstone Ore          | ORE             | EPIC       | 300          | 0.6      | False          | `["thal_zirad_sacred_quarry", "mana_charged_desert", "ritual_mined"]`         | `["Crucible Spire"]`   | `{"smelts_into": "Sunstone Ingot", "purity": 0.75, "innate_property": "fire_damage_on_hit_weapon", "heat_absorption_armor": "high", "requires_ritual_forge": "Thal-Zirad Sun Blessing"}`         |
| Crimsonite Ore                | ORE             | EPIC       | 500          | 1.0      | False          | `["dissonance_scar_ember_wastes", "volatile_leyline_deposit", "excavated_relic_site"]` | `["Skarport", "Lethandrel", "Stonewake_Anvilring"]` | `{"smelts_into": "Unstable Crimsonite Ingot", "corruption_risk_smelting": 0.4, "energy_signature": "crimson_dissonance", "power_potential": "immense_unstable"}`                               |
| **Refined Metals (Ingots)**   |                 |            |              |          |                |                                                                               |                        |                                                                                                                                                                                               |
| Low Quality Iron Ingot        | METAL           | COMMON     | 1            | 0.25     | True           | `["smelted_scrap"]`                                                           | `[]`                   | `{"hardness": 3, "tensile_strength": 2, "rust_susceptibility": "high"}`                                                                                                                        |
| Iron Ingot                    | METAL           | COMMON     | 5            | 0.4      | True           | `["smelted_ore_standard"]`                                                    | `[]`                   | `{"hardness": 5, "tensile_strength": 4, "rust_susceptibility": "medium"}`                                                                                                                      |
| Copper Ingot                  | METAL           | COMMON     | 7            | 0.35     | True           | `["smelted_ore_standard"]`                                                    | `[]`                   | `{"hardness": 2, "malleability": 8, "conductivity_electrical_magical": "high", "corrosion_resistance": "good"}`                                                                                |
| Tin Ingot                     | METAL           | UNCOMMON   | 10           | 0.35     | True           | `["smelted_ore_standard"]`                                                    | `[]`                   | `{"hardness": 1, "malleability": 7, "alloy_primary_use": "bronze_production"}`                                                                                                                 |
| Bronze Ingot                  | METAL           | UNCOMMON   | 20           | 0.4      | True           | `["alloyed_copper_tin"]`                                                      | `[]`                   | `{"hardness": 6, "tensile_strength": 5, "corrosion_resistance": "very_good", "historical_significance": "early_accord_armaments"}`                                                              |
| Steel Ingot                   | METAL           | UNCOMMON   | 30           | 0.4      | True           | `["refined_iron_carbon_alloy"]`                                               | `[]`                   | `{"hardness": 7, "tensile_strength": 6, "edge_retention": "good"}`                                                                                                                             |
| Silver Ingot                  | METAL           | UNCOMMON   | 45           | 0.5      | True           | `["smelted_ore_refined"]`                                                     | `[]`                   | `{"hardness": 3, "malleability": 7, "purity_for_enchanting": "high", "value_modifier_vs_lycanthropes": 1.2}`                                                                                 |
| Dwarven Steel Ingot           | METAL           | RARE       | 120          | 0.45     | True           | `["dwarven_forge_secret_alloy", "stonewake_guild_marked"]`                    | `[]`                   | `{"hardness": 8, "durability_modifier": 1.3, "requires_skill_handling": "Dwarven Smithing L3", "weight_optimized": true, "ancestral_quality": true}`                                         |
| Orcish Grognard Steel Ingot   | METAL           | RARE       | 100          | 0.55     | True           | `["orcish_bloomery_ritual_steel", "rivemark_militia_standard", "blood_tempered_hints"]` | `[]`                   | `{"impact_resistance": 9, "weight_modifier": 1.15, "appearance": "dark_mottled_red_sheen", "intimidation_factor": "low", "requires_skill_handling": "Orcish Smithing L2"}`                      |
| Human Guildsteel Ingot        | METAL           | UNCOMMON   | 70           | 0.4      | True           | `["skarport_trade_guild_standard", "versatile_alloy"]`                        | `[]`                   | `{"hardness": 6, "tensile_strength": 6, "adaptability_enchantment": "medium", "cost_efficiency": "high", "mass_producible": true}`                                                             |
| Ferverl Sun-Forged Steel Ingot| METAL           | EPIC       | 450          | 0.35     | True           | `["ferverl_desert_ritual_forge", "thal_zirad_exclusive_process", "mana_imbued"]` | `["Crucible Spire_unlicensed"]` | `{"hardness": 7, "heat_resistance": "extreme", "mana_affinity": "fire_sun", "requires_ritual_finalizing": "Sun Blessing Attunement", "weight_modifier": 0.9}`                                   |
| Star Metal Ingot              | METAL           | EPIC       | 700          | 0.3      | True           | `["refined_star_metal_fragment", "arcane_forge_needed"]`                      | `[]`                   | `{"hardness": 9, "malleability": 2, "innate_magic_resistance": "high", "affinity_enchantment": "celestial_air", "glows_faintly": true, "shatters_if_impure_craft": true}`                        |
| Refined Crimsonite Ingot      | METAL           | LEGENDARY  | 2000         | 0.8      | True           | `["stabilized_crimsonite_ore_dangerous", "relic_smithing_process"]`         | `["ALL_ACCORD_CITIES"]`| `{"hardness": 10, "power_output_weapon": "extreme", "corruption_wearer_chance": 0.1, "durability": "variable_unstable", "requires_containment_runes": true, "notes": "Extremely dangerous."}` |
| **Fuels & Additives**       |                 |            |              |          |                |                                                                               |                        |                                                                                                                                                                                               |
| Seasoned Hardwood             | WOOD            | COMMON     | 0.5          | 0.3      | False          | `["general_fuel", "forestry_byproduct"]`                                      | `[]`                   | `{"fuel_value": 5, "smoke_level": "high", "burn_duration_modifier": 0.8}`                                                                                                                      |
| Magma-Kissed Coal             | ORE             | UNCOMMON   | 8            | 0.25     | False          | `["stonewake_lower_vents", "geothermal_fuel", "dwarven_preferred"]`           | `[]`                   | `{"fuel_value": 25, "smoke_level": "low", "heat_intensity": "very_high", "ignites_quickly": true}`                                                                                             |
| Limestone Flux                | CRAFTED         | COMMON     | 1            | 0.1      | True           | `["crushed_limestone", "purification_agent"]`                                 | `[]`                   | `{"impurity_removal_efficiency": 0.6, "slag_reduction": true}`                                                                                                                                |
| Dwarven Oath-Sand             | MAGICAL         | RARE       | 30           | 0.05     | False          | `["dwarven_sacred_cave_sand", "ritual_smithing_additive"]`                    | `[]`                   | `{"effect_on_metal": "enhances_durability_oaths", "application": "sprinkled_during_tempering", "rarity_modifier_dwarven_items": 1.1}`                                                              |
| Standard Quenching Oil        | CRAFTED         | COMMON     | 4            | 0.2      | True           | `["rendered_animal_fat", "mineral_oil_blend"]`                                | `[]`                   | `{"cooling_rate": "medium", "effect_on_hardness": "standard"}`                                                                                                                                |
| Orcish Fury-Quench            | MAGICAL         | RARE       | 25           | 0.2      | True           | `["orcish_ritual_blend_herbs_blood", "secret_ingredient_grog"]`               | `[]`                   | `{"cooling_rate": "fast_volatile", "effect_on_metal": "adds_minor_jagged_edge_chance", "risk_of_brittleness": 0.1, "fumes_intoxicating": true}`                                                  |
| **Hafts, Grips, Components**  |                 |            |              |          |                |                                                                               |                        |                                                                                                                                                                                               |
| Sturdy Ash Wood Haft          | WOOD            | COMMON     | 2            | 0.3      | True           | `["shaped_ash_wood", "tool_weapon_component"]`                                | `[]`                   | `{"strength": 6, "flexibility": 4, "grip_surface": "smooth"}`                                                                                                                                 |
| Beastfolk Bone-Studded Grip   | CRAFTED         | UNCOMMON   | 12           | 0.15     | True           | `["leather_wrapped_bone_shards", "ashkar_vale_craft"]`                        | `[]`                   | `{"grip_enhancement": "high", "intimidation_factor": "low", "damage_type_bash": "piercing_traces"}`                                                                                             |
| Hardened Leather Strips       | LEATHER         | COMMON     | 3            | 0.05     | True           | `["tanned_hide", "binding_wrapping_material"]`                                | `[]`                   | `{"flexibility": 6, "binding_strength": 4, "durability": "medium"}`                                                                                                                            |
| Steel Rivets & Fittings       | METAL           | COMMON     | 4            | 0.1      | True           | `["small_steel_parts", "armor_construction"]`                                 | `[]`                   | `{"quantity_per_unit": 50, "strength_rating": 5}`                                                                                                                                              |
| Dwarven Rune-Etched Clasp     | MAGICAL         | RARE       | 75           | 0.02     | True           | `["dwarven_runesmith_craft", "armor_enhancement_component"]`                  | `[]`                   | `{"rune_effect": "minor_warding_physical", "attunement_required": "dwarven_kin_or_oathbound", "glows_faintly_near_danger": true}`                                                                |
| **Sharpening/Polishing**      |                 |            |              |          |                |                                                                               |                        |                                                                                                                                                                                               |
| Basic Whetstone               | CRAFTED         | COMMON     | 2            | 0.1      | True           | `["shaped_sandstone", "blade_maintenance"]`                                   | `[]`                   | `{"sharpening_grade": "coarse", "uses": 10}`                                                                                                                                                   |
| Dwarven Grindstone Wheel      | CRAFTED         | UNCOMMON   | 20           | 5.0      | True           | `["stonewake_artisan_tool", "requires_workshop_setup"]`                       | `[]`                   | `{"sharpening_grade": "fine_master", "durability": "high", "can_sharpen_magical_metals": true}`                                                                                                   |
| Ferverl Sun-Sand Polish       | MAGICAL         | RARE       | 18           | 0.05     | False          | `["thal_zirad_blessed_sand", "ritual_finish_agent"]`                          | `[]`                   | `{"polishing_effect": "mirror_sheen", "minor_fire_resistance_buff_duration_hours": 1, "application_ritual": "sun_chant"}`                                                                      |

## Additional Material Archetypes

| Name                          | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                    | `illicit_in_regions`   | `properties` (JSON Example)                                                                                                                                                                                            |
| :---------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------------- | :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ores & Raw Metals (Continued)** |                 |            |              |          |                |                                                                                  |                        |                                                                                                                                                                                                                    |
| Bog Iron Ore                  | ORE             | COMMON     | 1.5          | 0.6      | False          | `["shimmering_marshes_deposit", "surface_harvest", "high_impurity"]`               | `[]`                   | `{"smelts_into": "Impure Iron Ingot", "purity": 0.5, "yield_per_unit": 0.4, "notes": "Requires extensive purification or results in brittle metal."}`                                                                  |
| Volcanic Obsidian Shard       | GEM             | UNCOMMON   | 12           | 0.2      | False          | `["stonewake_caldera_cooled_lava", "sharp_edge_natural"]`                          | `[]`                   | `{"hardness": 6, "brittleness": "high", "can_be_knapped": true, "smithing_use": "decorative_inlay_or_sacrificial_blade_component"}`                                                                                 |
| Glacial Iron Ore              | ORE             | RARE       | 60           | 0.7      | False          | `["frostbound_tundra_ice_vein", "cryo_infused_trace"]`                             | `[]`                   | `{"smelts_into": "Frost Iron Ingot", "purity": 0.8, "innate_property": "minor_cold_damage_weapon", "cold_resistance_armor": "low", "notes": "Difficult to smelt without specialized forge."}`                      |
| Meteoric Iron Chunk           | METAL           | RARE       | 120          | 2.0      | False          | `["meteorite_impact_ember_wastes", "unrefined_celestial"]`                         | `[]`                   | `{"smelts_into": "Meteoric Steel Ingot", "purity": 0.65, "innate_property": "minor_magic_disruption", "workability": "medium_requires_high_heat"}`                                                                  |
| **Refined Metals (Ingots - Continued)** |                 |            |              |          |                |                                                                                  |                        |                                                                                                                                                                                                                    |
| Impure Iron Ingot             | METAL           | COMMON     | 3            | 0.5      | True           | `["smelted_bog_iron"]`                                                           | `[]`                   | `{"hardness": 4, "tensile_strength": 3, "rust_susceptibility": "very_high", "crafting_penalty_modifier": 0.8}`                                                                                                    |
| Electrum Ingot                | METAL           | RARE       | 180          | 0.45     | True           | `["alloyed_silver_gold", "skarport_luxury_trade", "elven_preference_decorative"]`  | `[]`                   | `{"hardness": 4, "malleability": 9, "magical_conductivity": "medium_high", "value_modifier_decorative": 1.5, "tarnish_resistance": "good"}`                                                                   |
| Rose Gold Ingot               | METAL           | RARE       | 150          | 0.4      | True           | `["alloyed_copper_gold_silver_trace", "human_artisan_craft", "jewelry_smithing"]`  | `[]`                   | `{"hardness": 3, "malleability": 8, "appearance": "lustrous_pink", "value_modifier_artistic": 1.3}`                                                                                                        |
| Blued Steel Ingot             | METAL           | UNCOMMON   | 45           | 0.4      | True           | `["heat_treated_steel_ingot", "rust_resistant_finish"]`                            | `[]`                   | `{"hardness": 7, "tensile_strength": 6, "corrosion_resistance": "high", "appearance": "dark_blue_black_sheen"}`                                                                                               |
| Case-Hardened Iron Ingot      | METAL           | UNCOMMON   | 25           | 0.4      | True           | `["carbon_treated_iron_surface", "rivemark_fortification_material"]`             | `[]`                   | `{"surface_hardness": 8, "core_hardness": 4, "impact_resistance": "good_surface_brittle_core", "notes": "Good for specific armor plates, not full weapons."}`                                                   |
| Frost Iron Ingot              | METAL           | RARE       | 250          | 0.65     | True           | `["smelted_glacial_iron_ore", "cryo_forge_process"]`                               | `[]`                   | `{"hardness": 6, "innate_effect_weapon": "chance_of_chill_slow_on_hit", "innate_effect_armor": "minor_cold_aura_resistance", "brittleness_at_high_temp": "medium"}`                                            |
| Meteoric Steel Ingot          | METAL           | EPIC       | 650          | 1.8      | True           | `["refined_meteoric_iron_chunk", "celestial_forge_attuned"]`                       | `[]`                   | `{"hardness": 8, "magic_disruption_field_small": true, "anti_magic_weapon_property": "low", "durability": "very_high", "enchantment_difficulty": "high"}`                                                        |
| **Special Smithing Components** |                 |            |              |          |                |                                                                                  |                        |                                                                                                                                                                                                                    |
| Drake Scale (Red)             | MAGICAL         | RARE       | 90           | 0.1      | False          | `["harvested_ember_wastes_drake", "fire_affinity"]`                                | `[]`                   | `{"elemental_resistance_fire_armor": "high", "imbue_weapon_fire_damage_chance": "medium", "flexibility": "low", "requires_special_tools_to_work": true}`                                                         |
| Shadow Panther Hide Segment   | LEATHER         | RARE       | 70           | 0.3      | False          | `["hunted_whispering_woods_shadow_panther", "stealth_properties"]`                 | `[]`                   | `{"smithing_use": "armor_lining_grip_wrap", "stealth_modifier_when_used_in_armor": 0.1, "darkness_affinity": true}`                                                                                             |
| Spiritwood Heart              | WOOD            | EPIC       | 300          | 0.4      | False          | `["lethandrel_ancient_spirit_tree_fallen_branch", "mana_conductive"]`              | `["Stonewake_unless_licensed"]` | `{"smithing_use": "weapon_haft_core_enchantment_focus", "mana_capacity_modifier": 1.2, "durability": "medium", "requires_elven_carving_techniques": true}`                                                |
| Crysteel Shard                | GEM             | EPIC       | 400          | 0.05     | False          | `["crystal_highlands_deep_cavern_growth", "intense_cold_emanation"]`               | `[]`                   | `{"smithing_use": "weapon_core_inlay_arrowhead", "innate_cold_damage_high": true, "brittleness": "very_high_handle_with_care", "can_shatter_if_struck_hard": true}`                                          |
| Balanced Steel Pommel         | METAL           | UNCOMMON   | 15           | 0.2      | True           | `["forged_steel_component", "weapon_balance_enhancement"]`                         | `[]`                   | `{"balance_improvement_modifier": 0.1, "weight_customizable": true}`                                                                                                                                           |
| Ornate Silver Crossguard      | METAL           | RARE       | 60           | 0.25     | True           | `["silver_artisan_craft", "decorative_protective_weapon_part"]`                    | `[]`                   | `{"parry_bonus_modifier": 0.05, "aesthetic_appeal": "high", "vulnerability_to_tarnish": "medium"}`                                                                                                          |
| **Fuel & Additives (Continued)** |              |            |              |          |                |                                                                                  |                        |                                                                                                                                                                                                                    |
| Purified Firecrystal Dust     | MAGICAL         | RARE       | 35           | 0.02     | True           | `["refined_firecrystal_ember_wastes", "high_temp_fuel_additive"]`                  | `[]`                   | `{"fuel_value_boost_percentage": 50, "heat_intensity_increase": "high", "risk_of_flare_up": 0.05, "notes": "Use sparingly."}`                                                                                 |
| Elven Moon-Flux               | MAGICAL         | EPIC       | 120          | 0.03     | False          | `["lethandrel_alchemical_creation", "lunar_aligned_purifier"]`                     | `[]`                   | `{"impurity_removal_efficiency_magical_metals": 0.9, "enhances_enchantability": true, "requires_moonlight_during_use": true, "rarity_modifier_elven_items": 1.3}`                                         |

## Even More Material Archetypes

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                              | `illicit_in_regions`   | `properties` (JSON Example)                                                                                                                                                                                                           |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :----------------------------------------------------------------------------------------- | :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ores & Raw Metals (Further Additions)** |                 |            |              |          |                |                                                                                            |                        |                                                                                                                                                                                                                   |
| Hematite Ore                     | ORE             | COMMON     | 1.8          | 0.55     | False          | `["common_sedimentary_rock", "surface_deposits_verdant_frontier"]`                         | `[]`                   | `{"smelts_into": "Iron Ingot", "purity": 0.65, "yield_per_unit": 0.45, "color_tint": "reddish_hue_to_iron"}`                                                                                                          |
| Magnetite Ore                    | ORE             | UNCOMMON   | 4            | 0.6      | False          | `["igneous_rock_formations_crystal_highlands", "naturally_magnetic"]`                      | `[]`                   | `{"smelts_into": "Lodestone Enriched Iron Ingot", "purity": 0.7, "yield_per_unit": 0.5, "innate_property": "minor_magnetic_pull_tools"}`                                                                          |
| Nickel Ore                       | ORE             | UNCOMMON   | 10           | 0.4      | False          | `["laterite_deposits_ember_wastes", "alloy_component_for_steel"]`                          | `[]`                   | `{"smelts_into": "Nickel Ingot", "purity": 0.75, "corrosion_resistance_enhancer": true}`                                                                                                                              |
| Chromium Ore                     | ORE             | RARE       | 25           | 0.35     | False          | `["rare_vein_stonewake_mines", "stainless_steel_component"]`                               | `[]`                   | `{"smelts_into": "Chromium Ingot", "purity": 0.8, "hardness_enhancer": true, "shine_factor": "high"}`                                                                                                               |
| Cobalt Ore                       | ORE             | RARE       | 30           | 0.4      | False          | `["ashkar_vale_high_altitude_mine", "blue_pigment_source", "high_strength_alloy_component"]` | `[]`                   | `{"smelts_into": "Cobalt Ingot", "purity": 0.7, "heat_resistance_enhancer": true, "color_imparted": "deep_blue_to_alloys"}`                                                                                           |
| Tungsten Ore (Wolframite)        | ORE             | EPIC       | 150          | 0.9      | False          | `["dwarven_deep_core_mining", "extremely_dense_metal_source"]`                             | `[]`                   | `{"smelts_into": "Tungsten Ingot", "purity": 0.6, "melting_point": "extremely_high", "hardness_extreme": true, "notes": "Requires specialized forge and techniques."}`                                          |
| **Refined Metals & Alloys (Further Additions)** |                 |            |              |          |                |                                                                                            |                        |                                                                                                                                                                                                                   |
| Lodestone Enriched Iron Ingot    | METAL           | UNCOMMON   | 10           | 0.55     | True           | `["smelted_magnetite_ore"]`                                                                | `[]`                   | `{"hardness": 5, "magnetic_strength": "low", "tool_crafting_bonus": "easier_to_handle_small_parts"}`                                                                                                             |
| Nickel Ingot                     | METAL           | UNCOMMON   | 20           | 0.35     | True           | `["smelted_nickel_ore"]`                                                                   | `[]`                   | `{"hardness": 4, "malleability": 6, "alloy_use": "strengthens_iron_prevents_rust"}`                                                                                                                                |
| Chromium Ingot                   | METAL           | RARE       | 50           | 0.3      | True           | `["smelted_chromium_ore"]`                                                                 | `[]`                   | `{"hardness": 8, "malleability": 2, "alloy_use": "stainless_steel_decorative_plating"}`                                                                                                                            |
| Cobalt Ingot                     | METAL           | RARE       | 60           | 0.35     | True           | `["smelted_cobalt_ore"]`                                                                   | `[]`                   | `{"hardness": 5, "heat_resistance": "high", "alloy_use": "high_temperature_tools_blue_tinted_alloys"}`                                                                                                           |
| Stainless Steel Ingot            | METAL           | RARE       | 90           | 0.4      | True           | `["alloyed_steel_chromium_nickel", "skarport_cutlery_medical_tools"]`                      | `[]`                   | `{"hardness": 7, "corrosion_resistance": "extreme", "edge_retention": "very_good", "appearance": "bright_shiny"}`                                                                                                 |
| Tool Steel Ingot                 | METAL           | RARE       | 110          | 0.45     | True           | `["high_carbon_steel_alloy_tungsten_trace", "dwarven_toolmaking_standard"]`                | `[]`                   | `{"hardness": 9, "wear_resistance": "very_high", "brittleness": "medium", "notes": "Excellent for crafting tools that last."}`                                                                                        |
| Tungsten Carbide Ingot           | METAL           | EPIC       | 400          | 0.8      | True           | `["alloyed_tungsten_carbon_high_pressure_forge", "armor_piercing_cores"]`                  | `[]`                   | `{"hardness": 10, "density": "very_high", "melting_point": "extreme", "use": "specialized_arrowheads_weapon_cores_industrial_tools"}`                                                                             |
| Elven Moonsteel Ingot            | METAL           | EPIC       | 550          | 0.35     | True           | `["elven_secret_alloy_silver_starmetal_trace_moon_flux", "lethandrel_lunar_forge"]`        | `[]`                   | `{"hardness": 7, "malleability": 6, "innate_magic_affinity": "moon_illusion", "weight_modifier": 0.85, "glows_faintly_in_moonlight": true, "anti_shadow_property": "minor"}`                                |
| Orcish Slagsteel Ingot           | METAL           | UNCOMMON   | 20           | 0.6      | True           | `["reforged_battlefield_scrap_orcish_techniques", "rivemark_rough_construction"]`        | `[]`                   | `{"hardness": 5, "tensile_strength": 3, "impurity_level": "high_but_stable", "appearance": "rough_pitted", "cost_efficiency_brute_force": "high"}`                                                               |
| **Smithing Byproducts & Consumables** |           |            |              |          |                |                                                                                            |                        |                                                                                                                                                                                                                   |
| Iron Slag                        | CRAFTED         | COMMON     | 0.1          | 0.2      | True           | `["byproduct_iron_smelting"]`                                                              | `[]`                   | `{"use": "crude_construction_filler_roadbeds", "trade_value": "very_low"}`                                                                                                                                        |
| Steel Shavings                   | CRAFTED         | COMMON     | 0.5          | 0.01     | True           | `["byproduct_steel_smithing_grinding"]`                                                    | `[]`                   | `{"use": "can_be_reforged_into_low_quality_ingot_in_bulk", "component_for_sparking_powder": true}`                                                                                                              |
| Broken Whetstone Fragments       | CRAFTED         | COMMON     | 0.2          | 0.05     | True           | `["used_up_whetstone", "salvageable_grit"]`                                                | `[]`                   | `{"use": "component_for_grinding_paste", "sharpening_value": "minimal"}`                                                                                                                                          |
| Forge Ash                        | CRAFTED         | COMMON     | 0.05         | 0.1      | True           | `["byproduct_forge_fuel_burning"]`                                                         | `[]`                   | `{"use": "component_for_lye_soap_making_soil_additive_poorly", "trade_value": "negligible"}`                                                                                                                    |
| Tempering Salts (Basic)          | CRAFTED         | UNCOMMON   | 10           | 0.1      | True           | `["mineral_salt_blend", "heat_treatment_control"]`                                         | `[]`                   | `{"effect_on_metal": "improves_hardness_reduces_brittleness_standard_metals", "quantity_per_use": "small_pinch", "effectiveness_modifier": 1.0}`                                                                 |
| Dwarven Hearthstone Powder       | MAGICAL         | RARE       | 40           | 0.05     | False          | `["ground_dwarven_forge_hearthstone", "ritual_smithing_additive"]`                         | `[]`                   | `{"effect_on_metal": "imparts_minor_fire_resistance_and_durability_dwarven_items", "application": "mixed_with_quenching_oil_or_dusted_on"}`                                                                    |
| **Specialized Grips/Hilts/Components** |        |            |              |          |                |                                                                                            |                        |                                                                                                                                                                                                                   |
| Carved Ironwood Hilt             | WOOD            | UNCOMMON   | 15           | 0.25     | True           | `["artisan_carved_ironwood", "weapon_hilt_superior_grip"]`                                 | `[]`                   | `{"strength": 8, "grip_comfort_modifier": 1.1, "vibration_dampening": "good"}`                                                                                                                                 |
| Wire-Wrapped Leather Grip        | CRAFTED         | COMMON     | 8            | 0.1      | True           | `["leather_strips_steel_wire_wrap", "secure_weapon_grip"]`                                 | `[]`                   | `{"grip_enhancement": "medium_high", "durability": "medium", "requires_skill_assembly": "Leatherworking L1"}`                                                                                                  |
| Weighted War-Pick Head           | METAL           | UNCOMMON   | 20           | 0.8      | True           | `["forged_tool_steel", "armor_piercing_pick_component"]`                                   | `[]`                   | `{"armor_penetration_base": 1.5, "hafting_socket_type": "standard_pick"}`                                                                                                                                         |
| Serrated Axe Blade Insert        | METAL           | RARE       | 35           | 0.3      | True           | `["high_carbon_steel_insert", "enhances_axe_tearing_damage"]`                              | `[]`                   | `{"bonus_damage_vs_unarmored_or_lightly_armored": "1d4_bleed", "requires_precision_fitting": true}`                                                                                                               |
| Hollow Grindstone Wheel          | CRAFTED         | RARE       | 50           | 4.0      | True           | `["dwarven_engineered_grindstone", "allows_for_concave_blade_grinds_razor_sharpness"]`     | `[]`                   | `{"sharpening_grade": "razor_fine", "durability": "medium", "can_create_hollow_grind_edge": true, "notes": "Requires careful control."}`                                                                           |

## Slice-of-Life Material Archetypes

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                            | `illicit_in_regions`   | `properties` (JSON Example)                                                                                                                                                                                                |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :--------------------------------------------------------------------------------------- | :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Common & Utility Metals/Alloys** |                 |            |              |          |                |                                                                                          |                        |                                                                                                                                                                                                                        |
| Cast Iron Scrap                  | METAL           | COMMON     | 0.8          | 0.4      | False          | `["discarded_cookware", "broken_machinery_parts_skarport"]`                              | `[]`                   | `{"smelts_into": "Recycled Cast Iron Ingot", "purity": 0.6, "brittleness": "high", "good_for_non_impact_items": true}`                                                                                                     |
| Recycled Cast Iron Ingot         | METAL           | COMMON     | 2            | 0.35     | True           | `["smelted_cast_iron_scrap"]`                                                            | `[]`                   | `{"hardness": 4, "tensile_strength": 2, "heat_retention": "good", "uses": ["cookware", "simple_tools", "weights"]}`                                                                                                        |
| Raw Lead Chunks                  | ORE             | UNCOMMON   | 6            | 0.8      | False          | `["mined_alongside_silver_dwarven_mines", "soft_heavy_metal"]`                           | `[]`                   | `{"smelts_into": "Lead Ingot", "purity": 0.9, "density": "very_high", "toxicity_warning_if_used_for_food_items": true}`                                                                                                  |
| Lead Ingot                       | METAL           | UNCOMMON   | 10           | 0.7      | True           | `["smelted_raw_lead"]`                                                                   | `[]`                   | `{"hardness": 1, "malleability": 9, "uses": ["weights", "fishing_sinkers", "radiation_shielding_trace_relic_containment", "pipe_making_archaic"]}`                                                                       |
| Pewter Ingot                     | METAL           | UNCOMMON   | 18           | 0.3      | True           | `["alloyed_tin_copper_antimony_trace", "human_artisan_metal_tableware"]`                 | `[]`                   | `{"hardness": 2, "malleability": 7, "low_melting_point": true, "finish": "dull_silver_lustre", "uses": ["tankards", "plates", "figurines", "buttons"]}`                                                                  |
| Brass Ingot                      | METAL           | UNCOMMON   | 22           | 0.35     | True           | `["alloyed_copper_zinc_skarport_guilds", "decorative_and_functional"]`                   | `[]`                   | `{"hardness": 4, "malleability": 6, "corrosion_resistance": "good", "acoustic_properties": "good_for_instruments", "appearance": "bright_gold_like_sheen", "uses": ["fittings", "musical_instruments", "gears"]}` |
| **Artistic & Decorative Materials** |              |            |              |          |                |                                                                                          |                        |                                                                                                                                                                                                                        |
| Tarnished Silver Lumps           | METAL           | COMMON     | 5            | 0.2      | False          | `["old_jewelry_scrap", "discarded_cutlery", "minor_treasure_finds"]`                     | `[]`                   | `{"smelts_into": "Reclaimed Silver Ingot", "purity": 0.7, "requires_polishing_flux": true}`                                                                                                                            |
| Reclaimed Silver Ingot           | METAL           | UNCOMMON   | 30           | 0.45     | True           | `["smelted_tarnished_silver_lumps_refined"]`                                             | `[]`                   | `{"hardness": 3, "malleability": 7, "purity_for_enchanting": "medium_low", "uses": ["simple_jewelry", "inlays", "electroplating_solution_component"]}`                                                                  |
| Gold Dust                        | METAL           | RARE       | 50           | 0.01     | False          | `["panned_from_rivemark_delta_sands", "jewelry_workshop_sweepings", "treasure_hoard_trace"]` | `[]`                   | `{"smelts_into": "Gold Nugget", "purity": 0.95, "notes": "Usually requires accumulation to be useful for ingots."}`                                                                                                    |
| Small Gold Nugget                | METAL           | RARE       | 200          | 0.05     | True           | `["accumulated_gold_dust_melted_down", "raw_form_gold"]`                                 | `[]`                   | `{"smelts_into": "Gold Ingot", "purity": 0.98, "malleability": 10, "value_density": "high"}`                                                                                                                            |
| Gold Ingot                       | METAL           | EPIC       | 1000         | 0.2      | True           | `["refined_gold_nuggets_or_high_purity_ore", "currency_standard_jewelry_mastercraft"]`   | `[]`                   | `{"hardness": 2, "malleability": 10, "conductivity_magical": "very_high", "non_corrosive": true, "symbol_of_wealth_power": true}`                                                                                       |
| Colored Glass Shards             | GEM             | COMMON     | 1            | 0.1      | False          | `["broken_bottles_skarport_alleys", "discarded_alchemical_vials_lethandrel"]`            | `[]`                   | `{"smithing_use": "crude_decorative_inlay_requires_melting", "color_variety": ["green", "brown", "clear_ish"], "sharpness": "low"}`                                                                                       |
| Polished River Stones            | GEM             | COMMON     | 0.5          | 0.15     | False          | `["collected_rivemark_riverbeds", "smooth_varied_colors"]`                               | `[]`                   | `{"smithing_use": "pommel_weights_decorative_insets_non_gem_quality", "hardness": 4}`                                                                                                                                    |
| **Components for Other Crafts**  |                 |            |              |          |                |                                                                                          |                        |                                                                                                                                                                                                                        |
| Iron Nails (Bag of 100)          | METAL           | COMMON     | 3            | 0.5      | True           | `["mass_produced_smithies", "construction_carpentry_basic"]`                             | `[]`                   | `{"size_variety": ["small", "medium", "large_available_by_order"], "strength": "standard_iron", "quantity_per_unit": 100}`                                                                                             |
| Steel Hinges (Pair)              | METAL           | COMMON     | 5            | 0.3      | True           | `["standard_door_chest_hinge", "utility_smithing"]`                                      | `[]`                   | `{"load_capacity_kg": 50, "durability": "good", "requires_screws_or_nails_to_fit": true}`                                                                                                                                |
| Bronze Gear Blank                | METAL           | UNCOMMON   | 12           | 0.2      | True           | `["cast_bronze_disc", "tinkering_clockwork_component_preform"]`                          | `[]`                   | `{"diameter_cm": 5, "thickness_cm": 0.5, "machinability": "good", "requires_further_shaping_into_gear": true}`                                                                                                         |
| Steel Plowshare Blank            | METAL           | UNCOMMON   | 25           | 2.5      | True           | `["heavy_steel_forging", "agricultural_tool_component_rivemark"]`                        | `[]`                   | `{"hardness": 7, "wear_resistance_soil": "good", "requires_sharpening_and_hafting": true}`                                                                                                                            |
| Iron Cauldron Shell              | METAL           | UNCOMMON   | 18           | 3.0      | True           | `["hammered_iron_sheets_shaped", "cookware_alchemical_vessel_component"]`                | `[]`                   | `{"capacity_liters": 10, "heat_distribution": "even", "requires_legs_and_handle_attachment": true}`                                                                                                                    |
| Silver Wire Spool (Fine)         | METAL           | RARE       | 60           | 0.05     | True           | `["drawn_silver_ingot", "jewelry_enchanting_fine_detail_work"]`                          | `[]`                   | `{"gauge": "30_fine", "length_meters": 5, "conductivity_for_runes": "high", "tensile_strength": "low"}`                                                                                                              |

<br/>
<hr/>
<br/>

# Blacksmithing & Armorsmithing Recipes

## Initial Recipe Archetypes

**Recipe Archetype 1: Orcish Cleaver**

*   **Recipe Table Entry:**
    *   `id`: (UUID)
    *   `name`: "Orcish Spine-Cleaver"
    *   `description`: "A brutally effective cleaver favored by Orcish warriors from Rivemark and Stonewake. Designed more for intimidation and heavy chopping than finesse. Often bears clan markings."
    *   `recipe_category`: "Weapon - One-Handed Axe"
    *   `crafting_time_seconds`: 900
    *   `required_station_type`: "Orcish War-Forge" (or "Heavy Forge")
    *   `difficulty_level`: 4
    *   `is_discoverable`: True
    *   `region_specific`: `["Rivemark", "Stonewake_Hammerdeep"]`
    *   `unlock_conditions`: `{"skill_name": "Orcish Smithing", "level": 3, "faction_allegiance": "Any Orc Clan Friendly+"}`
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 120}, {"skill_name": "Orcish Smithing", "amount": 80}]`
    *   `quality_range`: `{"min": 2, "max": 5}`
    *   `custom_data`: `{"clan_marking_slot": true, "chance_to_cause_fear_on_crit": 0.05}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Orcish Grognard Steel Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Sturdy Ash Wood Haft): `quantity`: 1, `can_be_substituted`: True, `possible_substitutes`: `["Ironwood Haft", "Bone-Reinforced Grip"]`, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Orcish Fury-Quench): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Orcish Spine-Cleaver): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 3, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Orcish Smithing", `level`: 2, `affects_quality`: True, `affects_speed`: False

---
**Recipe Archetype 2: Dwarven Steel Shield**

*   **Recipe Table Entry:**
    *   `name`: "Dwarven Oathkeeper's Shield"
    *   `description`: "A shield of legendary Dwarven steel, often passed down through generations or forged for those who have taken solemn oaths. Its construction emphasizes absolute defense and resilience. Features a central boss suitable for a clan emblem."
    *   `recipe_category`: "Armor - Shield"
    *   `crafting_time_seconds`: 5400
    *   `required_station_type`: "Dwarven Ancestral Forge"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"quest_completed": "The Honor of the Forge", "item_in_inventory": "Dwarven Master Smith's Hammer Token", "skill_name": "Dwarven Smithing", "level": 7}`
    *   `experience_gained`: `[{"skill_name": "Armorsmithing", "amount": 500}, {"skill_name": "Dwarven Smithing", "amount": 300}]`
    *   `quality_range`: `{"min": 5, "max": 9}`
    *   `custom_data`: `{"emblem_slot": true, "knockback_resistance_modifier": 1.2}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Dwarven Steel Ingot): `quantity`: 4, `consumed_in_crafting`: True
    *   `item_id` (Deep Iron Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Dwarven Rune-Etched Clasp): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Dwarven Oath-Sand): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Dwarven Oathkeeper's Shield): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Armorsmithing", `level`: 6, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Dwarven Smithing", `level`: 5, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Runescribing (Basic)", `level`: 2, `affects_quality`: False, `affects_speed`: False

---
**Recipe Archetype 3: Human Guildsteel Longsword**

*   **Recipe Table Entry:**
    *   `name`: "Skarport Guild Standard Longsword"
    *   `description`: "A well-balanced and reliable longsword crafted from Human Guildsteel. Favored by Accord peacekeepers, city guards, and traveling merchants for its versatility and ease of maintenance. Mass-produced but of consistent quality."
    *   `recipe_category`: "Weapon - One-Handed Sword"
    *   `crafting_time_seconds`: 1200
    *   `required_station_type`: "Standard Forge with Quench Tank"
    *   `difficulty_level`: 3
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 70}]`
    *   `quality_range`: `{"min": 2, "max": 6}`
    *   `custom_data`: `{"maintenance_kit_bonus_multiplier": 1.1, "guild_stamp_slot": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Human Guildsteel Ingot): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Standard Quenching Oil): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Skarport Guild Standard Longsword): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 2, `affects_quality`: True, `affects_speed`: True

---
**Recipe Archetype 4: Ferverl Sun-Forged Scimitar (Requires Ritual)**

*   **Recipe Table Entry:**
    *   `name`: "Ferverl Sun-Blessed Scimitar"
    *   `description`: "A gracefully curved scimitar forged in the sacred desert fires of Thal-Zirad. The Ferverl Sun-Forged steel glows with an inner heat, and the blade is said to sear the spirits of the unworthy. Requires a specific ritual to complete."
    *   `recipe_category`: "Weapon - One-Handed Sword (Exotic)"
    *   `crafting_time_seconds`: 10800
    *   `required_station_type`: "Thal-Zirad Sun Forge"
    *   `difficulty_level`: 9
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"faction_reputation": "Thal_Zirad_Ember_Veil_Honored", "quest_line_completed": "The Oracle's Trials", "skill_name": "Ferverl Metallurgy", "level": 7}`
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 800}, {"skill_name": "Ferverl Metallurgy", "amount": 500}, {"skill_name": "Ritual Magic (Fire)", "amount": 200}]`
    *   `quality_range`: `{"min": 6, "max": 10}`
    *   `custom_data`: `{"on_hit_effect": "minor_fire_damage_chance", "bonus_vs_shadow_creatures": true, "requires_attunement_by_owner": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Ferverl Sun-Forged Steel Ingot): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Gold Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Ferverl Sun-Sand Polish): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Magma-Kissed Coal): `quantity`: 5, `consumed_in_crafting`: True
    *   `item_id` (Living Flame Essence - RARE): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Ferverl Sun-Blessed Scimitar): `quantity`: 1, `is_primary`: True, `chance`: 0.9, `quality_modifier`: 1.1
    *   `item_id` (Scorched Sunstone Fragment - byproduct if ritual fails slightly): `quantity`: 1, `is_primary`: False, `chance`: 0.1
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 8, `affects_quality`: True, `affects_speed`: False
    *   `skill_name`: "Ferverl Metallurgy", `level`: 6, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Ritual Magic (Fire)", `level`: 5, `affects_quality`: True

---
**Recipe Archetype 5: Basic Field Repair Kit**

*   **Recipe Table Entry:**
    *   `name`: "Basic Field Repair Kit"
    *   `description`: "A simple kit containing a few essential tools and materials for minor repairs to weapons and armor in the field. Not as effective as a proper forge, but better than nothing."
    *   `recipe_category`: "Tool - Repair"
    *   `crafting_time_seconds`: 300
    *   `required_station_type`: "Tinker's Workbench" (or "Any Basic Forge")
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Tinkering", "amount": 30}, {"skill_name": "Blacksmithing", "amount": 10}]`
    *   `quality_range`: `{"min": 1, "max": 3}`
    *   `custom_data`: `{"repair_potency_percentage": 15, "number_of_uses": 3}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Sturdy Ash Wood Haft - small piece): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Basic Whetstone): `quantity`: 1, `consumed_in_crafting`: False
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Basic Field Repair Kit): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Tinkering", `level`: 1, `affects_quality`: True
    *   `skill_name`: "Blacksmithing", `level`: 1, `affects_quality`: False

## Additional Recipe Archetypes

---
**Recipe Archetype 6: Dwarven Heavy Iron Shield**

*   **Recipe Table Entry:**
    *   `name`: "Dwarven Heavy Iron Shield"
    *   `description`: "A solid, no-nonsense shield crafted from thick iron plates. Favored by Dwarven tunnel guards and those expecting a tough fight. Heavier than steel but cheaper to produce."
    *   `recipe_category`: "Armor - Shield"
    *   `crafting_time_seconds`: 3600
    *   `required_station_type`: "Basic Forge with Anvil"
    *   `difficulty_level`: 3
    *   `is_discoverable`: False
    *   `region_specific`: `["Stonewake", "Dwarven_Outposts"]`
    *   `unlock_conditions`: `{"race": "Dwarf", "skill_name": "Blacksmithing", "level": 2}`
    *   `experience_gained`: `[{"skill_name": "Armorsmithing", "amount": 90}, {"skill_name": "Dwarven Smithing", "amount": 30}]`
    *   `quality_range`: `{"min": 2, "max": 5}`
    *   `custom_data`: `{"block_solidity_modifier": 1.1, "weight_penalty_modifier": 1.15}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 5, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Sturdy Ash Wood Haft): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Dwarven Heavy Iron Shield): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Armorsmithing", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Dwarven Smithing", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 7: Human Footman's Steel Armor Set (Cuirass Example)**

*   **Recipe Table Entry (for Footman's Steel Cuirass):**
    *   `name`: "Footman's Steel Cuirass"
    *   `description`: "The standard steel cuirass issued to human footmen in cities like Skarport and Rivemark. Offers good protection against common threats. Part of a matching set."
    *   `recipe_category`: "Armor - Heavy Chest"
    *   `crafting_time_seconds`: 7200
    *   `required_station_type`: "Armorer's Forge"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"guild_membership": "Skarport_Artisans_Guild_Smithing_Chapter", "manual_read": "Accord_Standard_Armor_Patterns_Vol1"}`
    *   `experience_gained`: `[{"skill_name": "Armorsmithing", "amount": 250}]`
    *   `quality_range`: `{"min": 3, "max": 7}`
    *   `custom_data`: `{"set_bonus_id": "FootmansArmorSet", "repair_ease_modifier": 1.2, "weight_class": "medium_heavy"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Steel Ingot): `quantity`: 6, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 4, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Limestone Flux): `quantity`: 2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Footman's Steel Cuirass): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Armorsmithing", `level`: 4, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Human Smithing Traditions", `level`: 2, `affects_quality`: True

---
**Recipe Archetype 8: Elven Star-Metal Shortblade**

*   **Recipe Table Entry:**
    *   `name`: "Elven Star-Metal Shortblade"
    *   `description`: "A light, exquisitely balanced shortblade crafted from rare Star Metal. Elven smiths in Lethandrel sometimes forge these for scouts or duelists, valuing its natural resistance to magic and uncanny sharpness."
    *   `recipe_category`: "Weapon - Dagger/Shortsword"
    *   `crafting_time_seconds`: 14400
    *   `required_station_type`: "Elven Celestial Forge"
    *   `difficulty_level`: 8
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"skill_name": "Elven Smithing", "level": 7, "item_possessed_for_inspiration": "Star Metal Ingot", "location_access": "Lethandrel_CanopyTiers_MasterForge"}`
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 700}, {"skill_name": "Elven Smithing", "amount": 400}, {"skill_name": "Celestial Metallurgy", "amount": 100}]`
    *   `quality_range`: `{"min": 6, "max": 10}`
    *   `custom_data`: `{"innate_magic_resistance_value": 15, "critical_hit_chance_modifier": 0.05, "weight_modifier": 0.8, "glows_faintly_under_starlight": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Star Metal Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Spiritwood Heart): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Silver Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Elven Moon-Flux): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Elven Star-Metal Shortblade): `quantity`: 1, `is_primary`: True, `chance`: 0.95
    *   `item_id` (Star Metal Shavings - valuable byproduct): `quantity`: 1, `is_primary`: False, `chance`: 0.5
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 7, `affects_quality`: True
    *   `skill_name`: "Elven Smithing", `level`: 6, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Celestial Metallurgy", `level`: 4, `affects_quality`: True

---
**Recipe Archetype 9: Masterwork Smithing Hammer**

*   **Recipe Table Entry:**
    *   `name`: "Masterwork Smithing Hammer"
    *   `description`: "A perfectly balanced smithing hammer, crafted by a master for a master. Using this hammer improves the quality of crafted items and slightly reduces crafting time for metal goods."
    *   `recipe_category`: "Tool - Smithing"
    *   `crafting_time_seconds`: 21600
    *   `required_station_type`: "Master Forge with Precision Tools"
    *   `difficulty_level`: 9
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"skill_name": "Blacksmithing", "level": 10, "items_crafted_of_epic_quality_or_higher": 5, "self_realization_quest": "The Heart of the Forge"}`
    *   `experience_gained`: `[{"skill_name": "Tool Crafting", "amount": 1000}, {"skill_name": "Blacksmithing", "amount": 500}]`
    *   `quality_range`: `{"min": 8, "max": 10}`
    *   `custom_data`: `{"crafting_quality_bonus_modifier": 0.1, "crafting_speed_bonus_modifier": 0.05, "tool_durability": "extremely_high", "attunement_to_user": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Dwarven Steel Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Star Metal Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Ironwood Haft - Master Grade): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Dwarven Oath-Sand): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Artisan's Own Sweat & Tears): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Masterwork Smithing Hammer): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 9, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Tool Crafting", `level`: 7, `affects_quality`: True
    *   `skill_name` (Any one of): "Dwarven Smithing" Lvl 7, "Elven Smithing" Lvl 7, "Orcish Smithing" Lvl 7, or "Ferverl Metallurgy" Lvl 7

---
**Recipe Archetype 10: Steel Arrowheads (Bundle)**

*   **Recipe Table Entry:**
    *   `name`: "Steel Bodkin Arrowheads (Bundle of 20)"
    *   `description`: "A bundle of sharp, armor-piercing steel bodkin arrowheads. Standard ammunition for hunters and archers."
    *   `recipe_category`: "Ammunition - Arrowhead"
    *   `crafting_time_seconds`: 600
    *   `required_station_type`: "Basic Forge"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 20}, {"skill_name": "Fletching", "amount": 10}]`
    *   `quality_range`: `{"min": 1, "max": 4}`
    *   `custom_data`: `{"armor_penetration_modifier_base": 1.1, "bundle_size": 20}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Steel Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Stonewake Coal Seam): `quantity`: 2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Steel Bodkin Arrowhead): `quantity`: 20, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 1, `affects_quality`: True

## Even More Recipe Archetypes

---
**Recipe Archetype 11: Bronze Ingot (Alloy Recipe)**

*   **Recipe Table Entry:**
    *   `name`: "Bronze Ingot"
    *   `description`: "An ancient and reliable alloy of copper and tin. Stronger than copper, easier to cast than iron. Used for tools, early armaments, and decorative items."
    *   `recipe_category`: "Alloy - Basic"
    *   `crafting_time_seconds`: 450
    *   `required_station_type`: "Crucible Forge"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Metallurgy", "amount": 20}, {"skill_name": "Blacksmithing", "amount": 10}]`
    *   `quality_range`: `{"min": 1, "max": 4}`
    *   `custom_data`: `{"alloy_ratio_copper": 0.9, "alloy_ratio_tin": 0.1}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Copper Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Tin Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Stonewake Coal Seam): `quantity`: 3, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Bronze Ingot): `quantity`: 2, `is_primary`: True, `chance`: 0.95
    *   `item_id` (Copper-Tin Dross - low value scrap): `quantity`: 1, `is_primary`: False, `chance`: 0.05
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Metallurgy", `level`: 1, `affects_quality`: True
    *   `skill_name`: "Blacksmithing", `level`: 1, `affects_quality`: False

---
**Recipe Archetype 12: Tool Steel Ingot (Alloy Recipe)**

*   **Recipe Table Entry:**
    *   `name`: "Tool Steel Ingot"
    *   `description`: "A very hard and wear-resistant steel alloy, perfect for crafting durable tools. Often includes traces of tungsten or chromium, a technique perfected by Dwarven smiths."
    *   `recipe_category`: "Alloy - Advanced"
    *   `crafting_time_seconds`: 1800
    *   `required_station_type`: "High-Temperature Forge with Controlled Atmosphere"
    *   `difficulty_level`: 6
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"manual_read": "Dwarven Metallurgy Vol. III", "skill_name": "Metallurgy", "level": 5}`
    *   `experience_gained`: `[{"skill_name": "Metallurgy", "amount": 150}, {"skill_name": "Dwarven Smithing", "amount": 50}]`
    *   `quality_range`: `{"min": 4, "max": 8}`
    *   `custom_data`: `{"key_elements": ["high_carbon", "chromium_trace", "tungsten_trace_optional"]}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Steel Ingot): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Chromium Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Magma-Kissed Coal): `quantity`: 5, `consumed_in_crafting`: True
    *   `item_id` (Limestone Flux): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Tungsten Ore - optional): `quantity`: 1, `can_be_substituted`: True, `possible_substitutes`: `[]`, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Tool Steel Ingot): `quantity`: 3, `is_primary`: True, `chance`: 0.9
    *   `item_id` (High-Carbon Slag - minor byproduct): `quantity`: 1, `is_primary`: False, `chance`: 0.1
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Metallurgy", `level`: 5, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Dwarven Smithing", `level`: 3, `affects_quality`: True

---
**Recipe Archetype 13: Dwarven Smithing Tongs (Tool Recipe)**

*   **Recipe Table Entry:**
    *   `name`: "Dwarven Smithing Tongs (Set of 3 - Flat, Round, Pick-up)"
    *   `description`: "A set of sturdy, reliable smithing tongs crafted in the Dwarven style. Essential for handling hot metal safely and precisely. This set includes flat-jaw, round-jaw, and pick-up tongs."
    *   `recipe_category`: "Tool - Smithing Accessory"
    *   `crafting_time_seconds`: 2700
    *   `required_station_type`: "Dwarven Forge with Swage Block"
    *   `difficulty_level`: 4
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Tool Crafting", "amount": 100}, {"skill_name": "Dwarven Smithing", "amount": 50}]`
    *   `quality_range`: `{"min": 3, "max": 7}`
    *   `custom_data`: `{"tool_set_id": "DwarvenTongsBasic", "heat_resistance_level": "high"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Steel Ingot): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Dwarven Flat-Jaw Tongs): `quantity`: 1, `is_primary`: True
    *   `item_id` (Dwarven Round-Jaw Tongs): `quantity`: 1, `is_primary`: True
    *   `item_id` (Dwarven Pick-up Tongs): `quantity`: 1, `is_primary`: True
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 3, `affects_quality`: True
    *   `skill_name`: "Tool Crafting", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Dwarven Smithing", `level`: 1, `affects_speed`: True

---
**Recipe Archetype 14: Orcish Spiked Gauntlets (Armor Component/Weapon)**

*   **Recipe Table Entry:**
    *   `name`: "Orcish Gut-Puncher Gauntlets"
    *   `description`: "Heavy steel gauntlets reinforced with brutal spikes, favored by Orcish brawlers. More of a weapon than simple hand protection."
    *   `recipe_category`: "Armor - Heavy Gloves / Weapon - Fist"
    *   `crafting_time_seconds`: 3200
    *   `required_station_type`: "Orcish War-Forge"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"faction_allegiance": "Any Orc Clan Respected+", "witnessed_in_use_by_orc_champion": true}`
    *   `experience_gained`: `[{"skill_name": "Armorsmithing", "amount": 120}, {"skill_name": "Orcish Smithing", "amount": 90}, {"skill_name": "Weapon Crafting (Fist)", "amount": 50}]`
    *   `quality_range`: `{"min": 3, "max": 6}`
    *   `custom_data`: `{"damage_type": "piercing_bludgeoning", "unarmed_damage_bonus": "1d6", "intimidation_on_equip": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Orcish Grognard Steel Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Hardened Leather Strips): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Steel Shavings - for crude spikes): `quantity`: 2, `can_be_substituted`: True, `possible_substitutes`: `["Broken Weapon Fragments"]`, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Orcish Gut-Puncher Gauntlets - Pair): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Armorsmithing", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Orcish Smithing", `level`: 3, `affects_quality`: True, `affects_speed`: True

---
**Recipe Archetype 15: Repair Hammer (Tool for Repairing Items)**

*   **Recipe Table Entry:**
    *   `name`: "Tinker's Repair Hammer"
    *   `description`: "A small, versatile hammer with interchangeable heads (soft brass, hard steel) designed for repairing damaged metal items without a full forge. Less effective than forge repairs but highly portable."
    *   `recipe_category`: "Tool - Repair Accessory"
    *   `crafting_time_seconds`: 1200
    *   `required_station_type`: "Tinker's Workbench"
    *   `difficulty_level`: 3
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"skill_name": "Tinkering", "level": 3, "manual_read": "Field Maintenance and You"}`
    *   `experience_gained`: `[{"skill_name": "Tool Crafting", "amount": 80}, {"skill_name": "Tinkering", "amount": 40}]`
    *   `quality_range`: `{"min": 2, "max": 5}`
    *   `custom_data`: `{"repair_efficiency_modifier": 0.25, "tool_durability_uses": 50, "interchangeable_heads_included": ["brass_soft", "steel_hard"]}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Copper Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Sturdy Ash Wood Haft - small): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Tinker's Repair Hammer): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Tool Crafting", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Tinkering", `level`: 2, `affects_quality`: True

## Slice-of-Life Recipe Archetypes

---
**Recipe Archetype 16: Iron Cooking Pot**

*   **Recipe Table Entry:**
    *   `name`: "Sturdy Iron Cooking Pot"
    *   `description`: "A heavy iron cooking pot, essential for any hearth or campfire. Known for its even heat distribution and durability. A common sight in kitchens across all cultures."
    *   `recipe_category`: "Household - Cookware"
    *   `crafting_time_seconds`: 1800
    *   `required_station_type`: "Basic Forge with Hammering Stump"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 40}, {"skill_name": "Household Crafting", "amount": 20}]`
    *   `quality_range`: `{"min": 1, "max": 5}`
    *   `custom_data`: `{"capacity_liters": 5, "heat_retention_modifier": 1.1, "can_be_seasoned_for_non_stick": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Iron Cauldron Shell - optional): `quantity`: 1, `can_be_substituted`: True, `possible_substitutes`: `["Sheet Iron Plates"]`, `consumed_in_crafting`: True
    *   `item_id` (Steel Rivets & Fittings): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Sturdy Iron Cooking Pot): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 1, `affects_quality`: True
    *   `skill_name`: "Sheet Metal Working", `level`: 1, `affects_speed`: True

---
**Recipe Archetype 17: Farmer's Iron Hoe Head**

*   **Recipe Table Entry:**
    *   `name`: "Farmer's Iron Hoe Head"
    *   `description`: "The durable iron head for a farmer's hoe, designed for tilling soil in places like Rivemark or the Verdant Frontier. Requires a wooden haft to be functional."
    *   `recipe_category`: "Tool Component - Agricultural"
    *   `crafting_time_seconds`: 900
    *   `required_station_type`: "Basic Forge"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 30}, {"skill_name": "Tool Crafting", "amount": 15}]`
    *   `quality_range`: `{"min": 1, "max": 4}`
    *   `custom_data`: `{"haft_socket_type": "standard_tapered", "edge_requires_sharpening": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Stonewake Coal Seam): `quantity`: 2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Farmer's Iron Hoe Head): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 18: Simple Pewter Tankard**

*   **Recipe Table Entry:**
    *   `name`: "Simple Pewter Tankard"
    *   `description`: "A plain but sturdy tankard made from pewter. Common in taverns and homes for serving drinks. Can be easily dented but also easily repaired."
    *   `recipe_category`: "Household - Tableware"
    *   `crafting_time_seconds`: 600
    *   `required_station_type`: "Tinker's Bench with Casting Molds"
    *   `difficulty_level`: 1
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Soft Metal Casting", "amount": 20}, {"skill_name": "Tinkering", "amount": 10}]`
    *   `quality_range`: `{"min": 1, "max": 3}`
    *   `custom_data`: `{"volume_ml": 500, "can_be_engraved": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Pewter Ingot): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Basic Casting Mold - Tankard Shape): `quantity`: 1, `consumed_in_crafting`: False
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Simple Pewter Tankard): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Soft Metal Casting", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 19: Iron Nails (Bag of 100)**

*   **Recipe Table Entry:**
    *   `name`: "Iron Nails (Bag of 100)"
    *   `description`: "A bag containing one hundred standard iron nails. Essential for carpentry, construction, and various repairs."
    *   `recipe_category`: "Component - Construction"
    *   `crafting_time_seconds`: 300
    *   `required_station_type`: "Nail Header Anvil"
    *   `difficulty_level`: 1
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 10}, {"skill_name": "Mass Production Techniques", "amount": 5}]`
    *   `quality_range`: `{"min": 1, "max": 3}`
    *   `custom_data`: `{"nail_type": "common_construction", "average_length_cm": 5}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Iron Nails (Bag of 100)): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 20: Decorative Iron Wall Sconce**

*   **Recipe Table Entry:**
    *   `name`: "Decorative Iron Wall Sconce"
    *   `description`: "An artistically twisted iron wall sconce designed to hold a candle or small lantern. Adds a touch of rustic elegance to any room. Popular in Human and Dwarven dwellings."
    *   `recipe_category`: "Household - Lighting Fixture"
    *   `crafting_time_seconds`: 2400
    *   `required_station_type`: "Artisan's Forge with Scrollwork Tools"
    *   `difficulty_level`: 4
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"inspiration_from_seeing_similar_item": true, "skill_name": "Decorative Smithing", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 80}, {"skill_name": "Decorative Smithing", "amount": 120}]`
    *   `quality_range`: `{"min": 2, "max": 7}`
    *   `custom_data`: `{"style": "rustic_scrollwork", "holds_item_type": ["candle", "small_lantern"], "wall_mountable": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Beeswax or Tallow - for blackening): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Fine Steel Wire - optional): `quantity`: 1, `can_be_substituted`: True, `possible_substitutes`: `[]`, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Decorative Iron Wall Sconce): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 3, `affects_quality`: True
    *   `skill_name`: "Decorative Smithing", `level`: 2, `affects_quality`: True, `affects_speed`: True

---
**Recipe Archetype 21: Horseshoes (Set of 4)**

*   **Recipe Table Entry:**
    *   `name`: "Standard Iron Horseshoes (Set of 4)"
    *   `description`: "A set of four durable iron horseshoes, essential for any mounted travel or labor. Requires skill to fit properly to a horse."
    *   `recipe_category`: "Tool - Farriery"
    *   `crafting_time_seconds`: 1500
    *   `required_station_type`: "Farrier's Forge"
    *   `difficulty_level`: 3
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Blacksmithing", "amount": 50}, {"skill_name": "Farriery", "amount": 70}]`
    *   `quality_range`: `{"min": 2, "max": 6}`
    *   `custom_data`: `{"horse_size_suitability": ["medium", "large"], "includes_nail_holes": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Iron Ingot): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Stonewake Coal Seam): `quantity`: 3, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Standard Iron Horseshoe): `quantity`: 4, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Blacksmithing", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Farriery", `level`: 1, `affects_quality`: True