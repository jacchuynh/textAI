# Jewelcrafting & Gemcutting Materials

## Raw Gemstones & Crystals

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                               | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                                    |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------------------------ | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rough Quartz Crystal             | GEM_RAW         | COMMON     | 3            | 0.05     | False          | `["mined_crystal_highlands_common_geodes", "rivemark_riverbed_finds"]`                      | `[]`                 | `{"cuts_into": ["Clear Quartz Cabochon", "Faceted Quartz Gem"], "hardness_mohs": 7, "clarity_potential": "variable_included_to_flawless", "carat_potential_avg": 5, "mana_focus_potential": "very_low_unless_perfectly_clear"}` |
| Uncut Amethyst Geode             | GEM_RAW         | UNCOMMON   | 15           | 0.2      | False          | `["dwarven_mine_stonewake_geode_veins", "volcanic_rock_cavities"]`                          | `[]`                 | `{"cuts_into": ["Faceted Amethyst", "Amethyst Drusy Piece"], "hardness_mohs": 7, "color_intensity_potential": "pale_lilac_to_deep_purple", "carat_potential_avg_per_crystal": 2, "spiritual_affinity_calm": true}`     |
| Raw Garnet Nodule                | GEM_RAW         | UNCOMMON   | 20           | 0.03     | False          | `["metamorphic_rock_ember_wastes_alluvial_deposits", "deep_red_gemstone"]`                  | `[]`                 | `{"cuts_into": ["Faceted Garnet", "Garnet Cabochon"], "hardness_mohs": 7.5, "color_variety": ["deep_red_almandine_pyrope", "orange_spessartine_rare"], "carat_potential_avg": 3, "fire_element_trace_affinity": true}` |
| Flawed Emerald Chunk             | GEM_RAW         | RARE       | 80           | 0.02     | False          | `["lethandrel_hidden_groves_pegmatite_veins_elven_mined", "green_beryl_variety_included"]` | `[]`                 | `{"cuts_into": ["Faceted Emerald (Included)", "Emerald Cabochon (Opaque)"], "hardness_mohs": 7.5, "clarity_potential": "heavily_included_to_moderately_included", "carat_potential_avg": 1.5, "nature_magic_affinity": true}` |
| Star Ruby (Unpolished)           | GEM_RAW         | EPIC       | 400          | 0.01     | False          | `["thal_zirad_legendary_sand_ruby_mines_ferverl_guarded", "asterism_phenomenon_potential"]` | `["Skarport_unlicensed_trade"]` | `{"cuts_into": ["Star Ruby Cabochon"], "hardness_mohs": 9, "clarity_potential": "translucent_with_silk_inclusions", "carat_potential_avg": 2, "phenomenal_property": "asterism_6_ray_star_if_cut_correctly", "fire_sun_affinity_strong": true}` |
| Raw Diamond Crystal (Industrial) | GEM_RAW         | RARE       | 150          | 0.005    | False          | `["dwarven_deep_kimberlite_pipes_stonewake", "hardest_natural_substance_off_color_included"]` | `[]`                 | `{"cuts_into": ["Industrial Diamond Grit", "Small Faceted Diamond (Off-Color)"], "hardness_mohs": 10, "clarity_potential": "heavily_included_yellowish_brownish", "carat_potential_avg": 0.5, "use": ["cutting_tools", "abrasives"]}` |
| Gem-Quality Diamond Octahedron   | GEM_RAW         | LEGENDARY  | 2000         | 0.002    | False          | `["legendary_dwarven_motherlode_stonewake_once_a_generation_find", "perfect_crystal_structure"]`| `["Crucible Spire_Accord_Tax_Evasion"]` | `{"cuts_into": ["Brilliant Cut Diamond (Flawless)"], "hardness_mohs": 10, "clarity_potential": "internally_flawless_to_vvs", "carat_potential_avg": 1, "light_refraction_index": "exceptional", "symbol_of_power_wealth": true}` |
| Mana-Charged Geode Fragment      | GEM_MAGICAL     | EPIC       | 300          | 0.1      | False          | `["crucible_spire_mana_storm_aftermath_crystalized_ley_energy", "pulsating_raw_mana_crystal"]` | `[]`                 | `{"cuts_into": ["Mana Crystal Focus", "Charged Crystal Shard"], "hardness_mohs": "variable_5_8", "mana_type_attunement": "random_or_dominant_leyline_type", "energy_output_passive_mu_per_hour": 5, "stability": "low_decays_if_not_set"}` |

## Precious Metals for Jewelry (Refined)

*Many of these are also used in Blacksmithing but are listed here for their primary jewelry context. We'll assume they are available as small ingots/bars/wire suitable for jewelcraft.*

| Name                             | `material_type` | `rarity`   | `base_value_per_gram` | `weight_unit` | `is_craftable` | `source_tags`                                                                               | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                                    |
| :------------------------------- | :-------------- | :--------- | :-------------------- | :------------ | :------------- | :------------------------------------------------------------------------------------------ | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Silver Jewelry Bar (92.5% Pure)  | METAL_PRECIOUS  | UNCOMMON   | 2                     | GRAM          | True           | `["refined_silver_ingot_alloyed_copper_sterling_standard", "skarport_jewelers_supply"]`     | `[]`                 | `{"purity_karat_equivalent": "sterling", "malleability": "high", "tarnish_resistance": "medium", "melting_point_celsius": 961, "common_uses": ["rings", "chains", "settings_for_soft_gems"]}`                                |
| Gold Jewelry Ingot (18k Yellow)  | METAL_PRECIOUS  | RARE       | 30                    | GRAM          | True           | `["refined_gold_ingot_alloyed_silver_copper_durable_gold_standard", "human_elven_luxury_craft"]`| `[]`                 | `{"purity_karat_equivalent": "18k_75_percent_gold", "malleability": "good", "tarnish_resistance": "excellent", "melting_point_celsius": 900, "color": "rich_yellow", "common_uses": ["high_value_jewelry", "intricate_settings"]}` |
| Platinum Wire (Pure, 10cm)       | METAL_PRECIOUS  | EPIC       | 50                    | GRAM          | True           | `["ultra_refined_rare_platinum_group_metals_dwarven_master_refiners", "elite_jewelry_material"]`| `[]`                 | `{"purity_karat_equivalent": "999_fine", "malleability": "good_but_dense", "tarnish_resistance": "superior_inert", "melting_point_celsius": 1768, "color": "bright_silvery_white", "uses": ["secure_settings_for_diamonds_rare_gems"]}` |
| Electrum Leaf (Thin Sheet)       | METAL_PRECIOUS  | RARE       | 15                    | GRAM          | True           | `["beaten_electrum_ingot_elven_gilding_technique", "decorative_metal_leaf"]`                | `[]`                 | `{"thickness_microns": 1, "alloy_composition": "gold_silver_variable", "use": "gilding_inlays_on_jewelry_and_art_objects", "fragility": "very_high_handle_with_care"}`                                                      |
| Rose Gold Pellets (Casting)      | METAL_PRECIOUS  | RARE       | 25                    | GRAM          | True           | `["alloyed_gold_copper_silver_trace_casting_granules", "fashionable_warm_toned_gold"]`        | `[]`                 | `{"purity_karat_equivalent": "14k_to_18k_typical", "malleability": "good", "casting_fluidity": "excellent", "color": "pinkish_red_hue", "uses": ["cast_jewelry_settings_decorative_elements"]}`                               |

## Findings, Polishes & Tools (Jewelcraft Specific)

| Name                             | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                               | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                                   |
| :------------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------------------------ | :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Jeweler's Saw Blades (Dozen)     | TOOL_PART       | COMMON     | 5            | 0.01     | True           | `["fine_toothed_steel_blades_skarport_toolmaker", "for_cutting_metal_and_soft_gems"]`         | `[]`                 | `{"blade_thickness_mm": 0.2, "teeth_per_inch": 80, "material": "hardened_steel", "fragility": "high_snap_easily", "quantity": 12}`                                                                                            |
| Gem Cutting Dop Sticks (Set of 5)| TOOL            | UNCOMMON   | 10           | 0.05     | True           | `["wooden_or_metal_rods_with_wax_cup_for_holding_gems_during_cutting", "lapidary_tool"]`     | `[]`                 | `{"sizes_included": ["small_medium_large_cabochon_facet"], "material": "hardwood_brass", "wax_type_required": "Dop_Wax"}`                                                                                                     |
| Dop Wax (Cake)                   | CONSUMABLE      | COMMON     | 3            | 0.02     | True           | `["beeswax_shellac_resin_blend_jewelers_adhesive_for_dop_sticks", "thermoplastic_adhesive"]`  | `[]`                 | `{"melting_point_celsius": 60, "adhesion_strength": "good_for_gems", "reusability": "high_can_be_remelted", "color": "dark_brown_or_green"}`                                                                                 |
| Diamond Dust (Abrasive Grade)    | GEM_PROCESSED   | RARE       | 50           | 0.001    | True           | `["crushed_industrial_diamonds_lapidary_abrasive_for_hard_gems", "ultra_hard_polishing_agent"]`| `[]`                 | `{"grit_size_microns": "variable_1_to_50", "use": "grinding_faceting_polishing_diamonds_rubies_sapphires", "application": "mixed_with_oil_on_lap_wheel"}`                                                                  |
| Jeweler's Rouge (Polishing Bar)  | CONSUMABLE      | UNCOMMON   | 8            | 0.03     | True           | `["fine_iron_oxide_powder_in_wax_binder_metal_polishing_compound", "final_polish_for_metals"]` | `[]`                 | `{"abrasive_type": "very_fine_ferric_oxide", "use": "high_mirror_polish_on_gold_silver_platinum", "color_imparted_residue": "reddish_brown_wash_off"}`                                                                      |
| Silver Earring Hooks (10 Pairs)  | FINDING         | COMMON     | 12           | 0.01     | True           | `["bent_silver_wire_basic_earring_component", "standard_jewelry_finding"]`                  | `[]`                 | `{"material": "sterling_silver", "gauge_mm": 0.8, "style": "french_hook_fish_hook", "quantity": 20_pieces}`                                                                                                               |
| Gold Necklace Clasp (Lobster)    | FINDING         | RARE       | 40           | 0.005    | True           | `["14k_gold_spring_loaded_clasp_secure_necklace_closure", "quality_jewelry_finding"]`         | `[]`                 | `{"material": "14k_yellow_gold", "size_mm_length": 10, "mechanism": "spring_loaded_lobster_claw", "durability": "good"}`                                                                                                  |
| Bezel Setting Strip (Silver, 10cm)| FINDING        | UNCOMMON   | 15           | 0.02     | True           | `["thin_flat_silver_strip_for_forming_bezels_around_cabochons", "gem_setting_component"]`   | `[]`                 | `{"material": "fine_silver_or_sterling", "width_mm": 3, "thickness_mm": 0.5, "length_cm": 10, "flexibility": "high_easy_to_form"}`                                                                                        |

<br/>
<hr/>
<br/>

# Jewelcrafting & Gemcutting Recipes

## Gem Cutting & Polishing

---
**Recipe Archetype 49: Cut & Polished Quartz Cabochon**

*   **Recipe Table Entry:**
    *   `id`: (UUID)
    *   `name`: "Cut & Polished Quartz Cabochon"
    *   `description`: "A smooth, domed quartz cabochon, polished to a gentle sheen. Suitable for simple jewelry or as a minor focus component."
    *   `recipe_category`: "Gemcutting - Cabochon"
    *   `crafting_time_seconds`: 1800
    *   `required_station_type`: "Lapidary Grinding Wheel & Polishing Station"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False (Basic lapidary technique)
    *   `experience_gained`: `[{"skill_name": "Gemcutting", "amount": 30}]`
    *   `quality_range`: `{"min": 1, "max": 5}` (Quality affects smoothness, symmetry, and clarity of polish)
    *   `custom_data`: `{"typical_size_mm": "10x14_oval", "potential_use": "low_cost_ring_pendant_inlay"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Rough Quartz Crystal): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Water - for grinding coolant): `quantity`: 0.1, `consumed_in_crafting`: True
    *   `item_id` (Basic Sandpaper or Fine Sand - for initial shaping/smoothing): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Jeweler's Rouge (Polishing Bar) - or similar fine polish): `quantity`: 0.1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Cut & Polished Quartz Cabochon - Quality X): `quantity`: 1, `is_primary`: True, `chance`: 0.95 (Chance of cracking if flawed)
    *   `item_id` (Quartz Dust - byproduct): `quantity`: 1, `is_primary`: False, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Gemcutting", `level`: 1, `affects_quality`: True
    *   `skill_name`: "Lapidary Basics", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 50: Faceted Amethyst Gem (Round Brilliant)**

*   **Recipe Table Entry:**
    *   `name`: "Faceted Amethyst Gem (Round Brilliant)"
    *   `description`: "A sparkling amethyst cut in a classic round brilliant style to maximize its purple fire. A popular choice for rings and pendants."
    *   `recipe_category`: "Gemcutting - Faceted Stone"
    *   `crafting_time_seconds`: 5400
    *   `required_station_type`: "Jeweler's Faceting Machine with Dop Station"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"studied_under_dwarven_gemcutter_stonewake": true, "skill_name": "Advanced Gem Faceting", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Gemcutting", "amount": 150}, {"skill_name": "Advanced Gem Faceting", "amount": 100}]`
    *   `quality_range`: `{"min": 3, "max": 8}` (Quality based on cut precision, polish, color, and clarity retention)
    *   `custom_data`: `{"target_carat_weight_from_rough": "0.5_to_2_carats", "facets_count": 57_or_58, "light_performance_rating_potential": "good_to_excellent"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Uncut Amethyst Geode - select suitable crystal): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Dop Wax (Cake)): `quantity`: 0.1, `consumed_in_crafting`: True
    *   `item_id` (Diamond Dust (Abrasive Grade) - for grinding/polishing laps): `quantity`: 0.01, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Faceted Amethyst Gem - Quality X, specific carat weight): `quantity`: 1, `is_primary`: True, `chance`: 0.85 (Risk of mis-cutting or shattering)
    *   `item_id` (Amethyst Chips & Dust - byproduct): `quantity`: 1, `is_primary`: False, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Gemcutting", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Advanced Gem Faceting", `level`: 2, `affects_quality`: True, `affects_speed`: False (precision takes time)
    *   `skill_name`: "Mineralogy (Quartz Varieties)", `level`: 1, `affects_quality`: False (helps select good rough)

## Jewelry Crafting

---
**Recipe Archetype 51: Simple Silver Ring with Quartz Cabochon**

*   **Recipe Table Entry:**
    *   `name`: "Simple Silver Ring with Quartz Cabochon"
    *   `description`: "A modest ring crafted from sterling silver, featuring a single polished quartz cabochon set in a simple bezel."
    *   `recipe_category`: "Jewelry - Ring (Basic)"
    *   `crafting_time_seconds`: 3600
    *   `required_station_type`: "Jeweler's Bench with Soldering Kit & Mandrel"
    *   `difficulty_level`: 3
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Jewelry Crafting", "amount": 70}, {"skill_name": "Silversmithing", "amount": 30}]`
    *   `quality_range`: `{"min": 2, "max": 6}` (Quality affects finish, setting security, and overall appeal)
    *   `custom_data`: `{"ring_size_standard": "US_7_default_adjustable_slightly", "stone_setting_type": "bezel"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Silver Jewelry Bar (92.5% Pure)): `quantity`: 5 (grams), `consumed_in_crafting`: True
    *   `item_id` (Cut & Polished Quartz Cabochon - Quality 2+): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Silver Solder Paste - or wire & flux): `quantity`: 0.1 (grams), `consumed_in_crafting`: True
    *   `item_id` (Bezel Setting Strip (Silver, 10cm)): `quantity`: 0.3 (i.e. 3cm), `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Simple Silver Ring with Quartz Cabochon - Quality X): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Jewelry Crafting", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Silversmithing", `level`: 1, `affects_quality`: True
    *   `skill_name`: "Basic Gem Setting", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 52: Dwarven Gold & Garnet Signet Ring**

*   **Recipe Table Entry:**
    *   `name`: "Dwarven Gold & Garnet Signet Ring"
    *   `description`: "A heavy, ornate signet ring crafted in the traditional Dwarven style from 18k gold, featuring a deep red faceted garnet. The flat top of the ring is suitable for engraving a clan symbol."
    *   `recipe_category`: "Jewelry - Ring (Ornate Signet)"
    *   `crafting_time_seconds`: 10800
    *   `required_station_type`: "Dwarven Master Jeweler's Forge & Engraving Station"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"dwarven_clan_commission_stonewake": true, "skill_name": "Dwarven Goldsmithing", "level": 5, "studied_dwarven_heraldry": true}`
    *   `experience_gained`: `[{"skill_name": "Jewelry Crafting (Master)", "amount": 400}, {"skill_name": "Dwarven Goldsmithing", "amount": 250}, {"skill_name": "Engraving", "amount": 50}]`
    *   `quality_range`: `{"min": 5, "max": 9}` (Quality impacts craftsmanship, gold purity feel, gem setting, and engraving depth)
    *   `custom_data`: `{"ring_weight_grams_approx": 15, "engraving_surface_mm_diameter": 12, "stone_setting_type": "flush_or_channel_robust"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Gold Jewelry Ingot (18k Yellow)): `quantity`: 20 (grams), `consumed_in_crafting`: True
    *   `item_id` (Faceted Garnet Gem - Quality 4+, deep red): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Dwarven Hearth-Flux - for clean gold soldering): `quantity`: 0.05, `consumed_in_crafting`: True
    *   `item_id` (Gold Solder (Matching Karat)): `quantity`: 0.5 (grams), `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Dwarven Gold & Garnet Signet Ring - Quality X, Engravable Blank): `quantity`: 1, `is_primary`: True, `chance`: 0.9 (Complex, risk of ruining gold or gem)
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Jewelry Crafting (Master)", `level`: 6, `affects_quality`: True
    *   `skill_name`: "Dwarven Goldsmithing", `level`: 4, `affects_quality`: True, `affects_speed`: False
    *   `skill_name`: "Secure Gem Setting", `level`: 3, `affects_quality`: True

---
**Recipe Archetype 53: Elven Moonpetal Pendant (Silver & Moonstone)**

*   **Recipe Table Entry:**
    *   `name`: "Elven Moonpetal Pendant"
    *   `description`: "An elegant silver pendant crafted in the flowing, organic style of Lethandrel Elves. It features a luminous moonstone cabochon, believed to capture and reflect the light of the moons, aiding in meditation and intuition."
    *   `recipe_category`: "Jewelry - Amulet/Pendant (Elven)"
    *   `crafting_time_seconds`: 7200
    *   `required_station_type`: "Elven Moonfire Brazier & Silver Finesmithing Tools"
    *   `difficulty_level`: 6
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"inspiration_from_lethandrel_art_or_nature": true, "skill_name": "Elven Silversmithing", "level": 4, "mana_sensitive_crafting_techniques_known": true}`
    *   `experience_gained`: `[{"skill_name": "Jewelry Crafting", "amount": 250}, {"skill_name": "Elven Silversmithing", "amount": 180}, {"skill_name": "Artistic Design (Elven)", "amount": 70}]`
    *   `quality_range`: `{"min": 4, "max": 8}` (Quality affects intricacy of silverwork, moonstone glow, and subtle magical resonance)
    *   `custom_data`: `{"design_motif": "intertwined_vines_and_moon_phases", "moonstone_glow_intensity_modifier": "quality_dependent", "enhances_meditation_focus_minorly": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Silver Jewelry Bar (92.5% Pure) - or Fine Silver for purer work): `quantity`: 10 (grams), `consumed_in_crafting`: True
    *   `item_id` (Cut & Polished Moonstone Cabochon - High Quality, good adularescence): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Elven Moon-Flux - for purifying silver and enhancing magic): `quantity`: 0.01, `consumed_in_crafting`: True
    *   `item_id` (Fine Silver Wire - for details): `quantity`: 1 (meter), `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Elven Moonpetal Pendant - Quality X): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Jewelry Crafting", `level`: 5, `affects_quality`: True
    *   `skill_name`: "Elven Silversmithing", `level`: 3, `affects_quality`: True, `affects_speed`: True
    *   `skill_name`: "Delicate Gem Setting", `level`: 2, `affects_quality`: True

## Enchanting Components & Foci

---
**Recipe Archetype 54: Mana Crystal Focus (Cut & Set)**

*   **Recipe Table Entry:**
    *   `name`: "Mana Crystal Focus (Cut & Set)"
    *   `description`: "A raw mana-charged geode fragment that has been carefully cut and set into a simple silver or copper housing. It can be used by enchanters to channel and store magical energies for imbuing items."
    *   `recipe_category`: "Enchanting Component - Focus Crystal"
    *   `crafting_time_seconds`: 9000
    *   `required_station_type`: "Arcane Lapidary & Jeweler's Bench with Mana Dampeners"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"research_notes_crucible_spire_on_mana_crystals": true, "skill_name": "Arcane Gemcutting", "level": 5, "skill_name": "Basic Enchanting Theory", "level": 3}`
    *   `experience_gained`: `[{"skill_name": "Gemcutting (Magical)", "amount": 300}, {"skill_name": "Jewelry Crafting (Functional)", "amount": 150}, {"skill_name": "Arcane Engineering (Basic)", "amount": 100}]`
    *   `quality_range`: `{"min": 4, "max": 8}` (Quality affects mana storage capacity, stability, and efficiency as a focus)
    *   `custom_data`: `{"mana_storage_capacity_units_base": 100, "mana_storage_per_quality": 25, "energy_leakage_rate_percent_per_day": "5_minus_quality", "attuned_mana_type_if_any": "inherited_from_raw_crystal"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Mana-Charged Geode Fragment): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Silver Jewelry Bar - for setting): `quantity`: 5 (grams), `can_be_substituted`: True, `possible_substitutes`: `["Copper Ingot (Pure)", "Gold Jewelry Ingot (Low Karat)"]`, `consumed_in_crafting`: True
    *   `item_id` (Insulated Cerametal Pliers - tool, for handling charged crystal): `quantity`: 1, `consumed_in_crafting`: False
    *   `item_id` (Inert Clay (Mana Absorptive) - for safe handling during cutting): `quantity`: 0.2, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Mana Crystal Focus - Quality X): `quantity`: 1, `is_primary`: True, `chance`: 0.8 (Risk of crystal shattering or mana discharge)
    *   `item_id` (Depleted Crystal Shards & Metal Scrap - failure): `quantity`: 1, `is_primary`: False, `chance`: 0.2
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Arcane Gemcutting", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Jewelry Crafting (Functional)", `level`: 3, `affects_quality`: True
    *   `skill_name`: "Mana Manipulation (Basic Control)", `level`: 2, `affects_quality`: True (critical for stability)

---
This gives us a good foundation for Jewelcrafting, combining artistic creation with the practical needs of enchanting and the inherent value of gems and precious metals.

What's the next crafting discipline you'd like to detail?
1.  **Scribing & Scroll Making**
2.  **Ritual Crafting & Totem Carving**
3.  **Cooking & Provisioning**
4.  Or another?