# Alchemy & Potion Brewing Materials

## Herbal Reagents

| Name                       | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                              | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                            |
| :------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------- | :------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sunpetal Leaf              | HERB            | COMMON     | 1            | 0.01     | False          | `["harvested_verdant_frontier_daytime", "common_field_herb"]`                | `[]`                 | `{"alchemical_property": "minor_healing_stimulant", "potency": 0.2, "preparation": "crush_infuse", "duration_modifier": 0.8, "synergy_with": ["Purified Water", "Honey"]}`                                             |
| Mooncluster Berries        | HERB            | UNCOMMON   | 5            | 0.02     | False          | `["harvested_whispering_woods_night", "lunar_affinity", "elven_cultivation_lethandrel"]` | `[]`                 | `{"alchemical_property": "mana_regeneration_slow", "potency": 0.3, "preparation": "juice_ferment_lightly", "duration_seconds": 300, "side_effect_chance": "mild_drowsiness_0.05"}`                               |
| Shimmering Marsh Cap       | HERB            | RARE       | 20           | 0.05     | False          | `["harvested_shimmering_marshes_bioluminescent_fungus", "toxic_if_raw"]`     | `[]`                 | `{"alchemical_property": "invisibility_brief", "potency": 0.6, "preparation": "distill_neutralize_toxin", "duration_seconds": 60, "toxicity_raw": "medium", "purified_by": ["Ferverl Ash Salts"]}`                 |
| Rivercress Sprig           | HERB            | COMMON     | 0.8          | 0.01     | False          | `["harvested_rivemark_riverbanks", "aquatic_herb"]`                          | `[]`                 | `{"alchemical_property": "minor_stamina_recovery", "potency": 0.15, "preparation": "steep", "taste_profile": "peppery"}`                                                                                                |
| Ember Wastes Bloom         | HERB            | UNCOMMON   | 8            | 0.03     | False          | `["harvested_ember_wastes_oases_heat_resistant", "ferverl_use"]`             | `[]`                 | `{"alchemical_property": "minor_fire_resistance", "potency": 0.4, "preparation": "dry_powder", "duration_seconds": 180, "synergy_with": ["Drake Scale Powder"]}`                                                  |
| Frostbound Lichen          | HERB            | UNCOMMON   | 7            | 0.02     | False          | `["harvested_frostbound_tundra_rocks", "cryo_adapted"]`                      | `[]`                 | `{"alchemical_property": "minor_cold_resistance", "potency": 0.4, "preparation": "grind_infuse_cold", "duration_seconds": 180, "antagonistic_to": ["Ember Wastes Bloom"]}`                                       |
| Verdant Vine Extract       | HERB            | RARE       | 25           | 0.01     | True           | `["processed_lethandrel_sentient_vines_elven_ritual", "living_essence"]`     | `["Stonewake_uncontrolled"]` | `{"alchemical_property": "enhanced_regeneration_cellular", "potency": 0.7, "preparation": "ritual_extraction_stabilize", "duration_seconds": 30, "side_effect_chance": "minor_plant_growth_on_user_0.01"}` |
| Crystal Highlands Wort     | HERB            | UNCOMMON   | 10           | 0.04     | False          | `["harvested_crystal_highlands_mineral_rich_soil", "earth_affinity"]`        | `[]`                 | `{"alchemical_property": "physical_damage_resistance_potion_base", "potency": 0.3, "preparation": "decoct", "notes": "Absorbs properties of added minerals."}`                                                     |
| Corpse-Finder Moss         | HERB            | RARE       | 15           | 0.02     | False          | `["grows_near_undead_remains_shimmering_marshes", "necromantic_trace"]`       | `["Skarport_public_market"]` | `{"alchemical_property": "detect_undead_briefly", "potency": 0.5, "preparation": "burn_as_incense_inhale_fumes", "duration_seconds": 120, "toxicity_fumes": "low_headache"}`                               |
| Thal-Zirad Sun-Dried Petals| HERB            | RARE       | 30           | 0.01     | False          | `["thal_zirad_sacred_garden_offering_flower", "ritual_preparation"]`         | `[]`                 | `{"alchemical_property": "clarity_of_mind_divination_aid", "potency": 0.6, "preparation": "steep_in_blessed_water", "duration_modifier": 1.2, "requires_ritual_focus": true}`                                  |

## Animal & Monster Parts

| Name                       | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                 | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                          |
| :------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :---------------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Giant Spider Venom Gland   | ANIMAL_PART     | UNCOMMON   | 12           | 0.05     | False          | `["harvested_whispering_woods_giant_spider", "toxic_creature_part"]`          | `[]`                 | `{"alchemical_property": "paralysis_poison_weak", "potency": 0.4, "preparation": "extract_dilute_stabilize", "application": "weapon_coating_trap_component", "antidote_known": "Sunpetal Leaf Paste"}`            |
| Wyvern Scale Powder        | MAGICAL         | RARE       | 75           | 0.03     | True           | `["hunted_ember_wastes_wyvern_ground_scales", "elemental_creature_fire"]`     | `[]`                 | `{"alchemical_property": "fire_resistance_potion_strong", "potency_modifier": 1.5, "elemental_charge": "fire", "preparation": "infuse_in_oil_base_potion", "synergy_with": ["Ember Wastes Bloom"]}`           |
| Spirit Fox Saliva          | MAGICAL         | EPIC       | 300          | 0.01     | False          | `["beastfolk_ritual_collection_ashkar_vale_spirit_animal", "ethereal_essence"]` | `[]`                 | `{"alchemical_property": "heightened_senses_elixir_major", "potency": 0.9, "preparation": "handle_with_silver_tools_infuse_moonlight", "duration_seconds": 600, "volatility": "medium", "requires_stabilizer": true}` |
| Grotesque Hide Oil         | ANIMAL_PART     | UNCOMMON   | 9            | 0.1      | True           | `["rendered_fat_shimmering_marshes_grotesque", "mutated_creature"]`           | `[]`                 | `{"alchemical_property": "acid_resistance_potion_minor", "potency": 0.3, "preparation": "render_filter", "smell": "pungent_acrid", "duration_seconds": 240}`                                                  |
| Griffin Feather (Down)     | ANIMAL_PART     | RARE       | 40           | 0.005    | False          | `["collected_crystal_highlands_griffin_nest_shed_feather", "sky_affinity"]`   | `[]`                 | `{"alchemical_property": "levitation_potion_component_lightness", "potency": 0.5, "preparation": "weave_into_potion_filter_chant", "notes": "Aids in reducing potion weight and improving ascent."}`           |
| Basilisk Eye (Petrified)   | MAGICAL         | EPIC       | 250          | 0.2      | False          | `["slain_basilisk_ember_wastes_rare_drop", "petrification_magic_source"]`     | `["Skarport_restricted_trade"]` | `{"alchemical_property": "stoneflesh_potion_ingredient_major_defense", "potency": 0.8, "preparation": "grind_carefully_under_ward_infuse_lead_solution", "side_effect_chance": "slight_stiffness_0.1"}`       |
| Troll Blood (Regenerative) | MAGICAL         | RARE       | 60           | 0.15     | False          | `["harvested_frostbound_tundra_troll_requires_rapid_preservation", "vital_essence"]` | `[]`                 | `{"alchemical_property": "regeneration_potion_potent_base", "potency": 0.6, "preparation": "stabilize_with_iron_salts_keep_cold", "notes": "Highly unstable if not preserved quickly."}`                 |

## Mineral & Magical Reagents

| Name                       | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                                       | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                                          |
| :------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :---------------------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Purified Leyline Water     | MAGICAL         | UNCOMMON   | 10           | 0.1      | True           | `["lethandrel_ritual_purification_leylines", "base_solvent_elven_alchemy"]`         | `[]`                 | `{"solvent_power": "high", "purity_level": 0.95, "mana_infusion_base": true, "stability": "good", "notes": "Standard for Elven potions."}`                                                                       |
| Ferverl Blood-Ash          | MAGICAL         | RARE       | 60           | 0.02     | False          | `["ferverl_ritual_byproduct_ashkar_vale_emberflow_mana_imbued_ash"]`                | `["Skarport_Accord_controlled"]` | `{"alchemical_property": "mutation_inducer_controlled_catalyst", "potency_modifier": 1.3, "preparation": "handle_with_obsidian_tools", "corruption_taint": "low_residual_if_blessed", "synergy_with": ["Spirit Fox Saliva"]}` |
| Ground Moonstone           | GEM             | UNCOMMON   | 18           | 0.03     | True           | `["crystal_highlands_moonstone_gem_pulverized", "lunar_reflective_properties"]`     | `[]`                 | `{"alchemical_property": "illusion_potion_enhancer_duration", "potency": 0.4, "preparation": "grind_fine_charge_under_moonlight", "notes": "Amplifies subtle energies."}`                                            |
| Sulfur Powder              | MINERAL         | COMMON     | 2            | 0.04     | False          | `["volcanic_vents_stonewake_caldera_ember_wastes_geothermal", "combustible_element"]` | `[]`                 | `{"alchemical_property": "fumigation_ingredient_minor_poison_component", "potency": 0.2, "preparation": "grind_sift", "flammability": "high", "use_in": ["Smokesticks", "Weak Acid Vials"]}`                         |
| Quicksilver Globules       | METAL           | RARE       | 70           | 0.25     | False          | `["rare_cinnabar_ore_refinement_dwarven_process", "liquid_metal_volatile"]`         | `["Lethandrel_restricted"]` | `{"alchemical_property": "transmutation_agent_base_catalyst_for_change", "potency": 0.7, "preparation": "store_in_sealed_glass_handle_with_care", "toxicity": "high_fumes_and_contact", "stability": "low"}` |
| Rock Salt Chunks           | MINERAL         | COMMON     | 0.5          | 0.08     | False          | `["mined_ember_wastes_salt_flats", "preservative_mundane_reagent"]`                 | `[]`                 | `{"alchemical_property": "stabilizer_minor_preservative", "potency": 0.1, "preparation": "crush_dissolve", "notes": "Common in food preservation, limited alchemical use."}`                                    |
| Ectoplasmic Residue        | MAGICAL         | RARE       | 50           | 0.01     | False          | `["haunted_ruins_verdant_frontier_ethereal_remains", "spirit_essence"]`             | `[]`                 | `{"alchemical_property": "etherealness_potion_component_incorporeality", "potency": 0.6, "preparation": "collect_in_silvered_vial_stabilize_with_salt", "duration_seconds": 30, "instability": "medium"}`          |
| Mana-Charged Crystal Dust  | MAGICAL         | EPIC       | 150          | 0.02     | True           | `["shattered_mana_crystal_crucible_spire_lethandrel_leyroot_grove", "pure_mana_form"]`| `[]`                 | `{"alchemical_property": "direct_mana_infusion_potion_powerful", "potency": 1.0, "preparation": "handle_with_insulated_gloves_infuse_directly", "notes": "Can supercharge potions or cause overload."}`        |

## Solvents & Bases

| Name                       | `material_type` | `rarity`   | `base_value` | `weight` | `is_craftable` | `source_tags`                                                              | `illicit_in_regions` | `properties` (JSON Example)                                                                                                                                                                             |
| :------------------------- | :-------------- | :--------- | :----------- | :------- | :------------- | :------------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Filtered River Water       | CRAFTED         | COMMON     | 0.2          | 0.1      | True           | `["collected_rivemark_river_filtered_cloth_sand", "basic_solvent"]`        | `[]`                 | `{"solvent_power": "low", "purity_level": 0.6, "mana_infusion_base": false, "stability": "low_spoils_quickly", "notes": "Suitable for very simple brews."}`                                           |
| Dwarven Spring Water       | MAGICAL         | UNCOMMON   | 5            | 0.1      | False          | `["stonewake_deep_springs_mineral_rich", "dwarven_brewing_base"]`            | `[]`                 | `{"solvent_power": "medium", "purity_level": 0.8, "mana_infusion_base": "trace", "stability": "medium", "notes": "Imparts a slight earthy taste, good for fortitude potions."}`                            |
| Orcish Grog Base           | CRAFTED         | UNCOMMON   | 4            | 0.1      | True           | `["fermented_grain_herbs_rivemark_orcish_recipe", "potent_alcoholic_base"]`  | `[]`                 | `{"solvent_power": "medium_volatile", "purity_level": 0.5, "mana_infusion_base": false, "stability": "good_if_sealed", "notes": "Can make potions very strong, or very unpredictable. Flammable."}`          |
| Refined Animal Fat         | CRAFTED         | COMMON     | 3            | 0.08     | True           | `["rendered_animal_fat_purified_multiple_sources", "oil_base_salves"]`       | `[]`                 | `{"solvent_power": "oil_soluble_only", "purity_level": 0.7, "application": "topical_salves_ointments", "stability": "medium"}`                                                                           |
| Lethandrel Moon-Dew        | MAGICAL         | RARE       | 40           | 0.05     | False          | `["collected_lethandrel_ritual_grove_lunar_cycle", "pure_elven_solvent"]`    | `[]`                 | `{"solvent_power": "very_high_ethereal", "purity_level": 0.99, "mana_infusion_base": true, "stability": "high_if_kept_dark", "notes": "Preserves delicate magical properties, enhances illusion/mind effects."}` |
| Ashkar Vale Spirit-Water   | MAGICAL         | RARE       | 35           | 0.1      | False          | `["ashkar_vale_emberflow_springs_blessed_by_shamans", "beastfolk_ritual_base"]` | `[]`                 | `{"solvent_power": "medium_wild", "purity_level": 0.75, "mana_infusion_base": "shamanic_wild", "stability": "medium_absorbs_ambient_energies", "notes": "Favored for nature or spirit-aspected potions."}` |

<br/>
<hr/>
<br/>

# Alchemy & Potion Brewing Recipes

## Basic Potions

---
**Recipe Archetype 22: Minor Healing Draught**

*   **Recipe Table Entry:**
    *   `id`: (UUID)
    *   `name`: "Minor Healing Draught"
    *   `description`: "A common herbal brew that mends minor wounds and restores a small amount of vitality. A staple for any adventurer."
    *   `recipe_category`: "Potion - Healing"
    *   `crafting_time_seconds`: 120
    *   `required_station_type`: "Apothecary's Bench"
    *   `difficulty_level`: 1
    *   `is_discoverable`: False (Basic alchemical knowledge)
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 20}]`
    *   `quality_range`: `{"min": 1, "max": 3}` (Quality affects amount healed)
    *   `custom_data`: `{"healing_amount_base": 10, "healing_per_quality_point": 5, "taste": "slightly_bitter_sweet"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Sunpetal Leaf): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Filtered River Water): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Glass Vial - Basic): `quantity`: 1, `consumed_in_crafting`: True (container)
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Minor Healing Draught): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 23: Weak Mana Potion**

*   **Recipe Table Entry:**
    *   `name`: "Weak Mana Potion"
    *   `description`: "A shimmering blue potion that restores a small amount of magical energy. Favored by novice mages and scholars."
    *   `recipe_category`: "Potion - Mana Restoration"
    *   `crafting_time_seconds`: 180
    *   `required_station_type`: "Apothecary's Bench"
    *   `difficulty_level`: 2
    *   `is_discoverable`: False
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 30}]`
    *   `quality_range`: `{"min": 1, "max": 3}`
    *   `custom_data`: `{"mana_restored_base": 15, "mana_per_quality_point": 7, "glows_faintly": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Mooncluster Berries): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Purified Leyline Water): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Ground Moonstone - trace): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Glass Vial - Basic): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Weak Mana Potion): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 24: Potion of Minor Fortitude**

*   **Recipe Table Entry:**
    *   `name`: "Potion of Minor Fortitude"
    *   `description`: "An earthy brew that temporarily increases physical resilience, allowing one to endure more punishment. Often smells of damp soil and iron."
    *   `recipe_category`: "Potion - Buff (Defense)"
    *   `crafting_time_seconds`: 240
    *   `required_station_type`: "Dwarven Alchemical Still" (or "Sturdy Alembic")
    *   `difficulty_level`: 3
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"manual_read": "Dwarven Brews and Tonics", "skill_name": "Alchemy", "level": 2}`
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 50}, {"skill_name": "Dwarven Lore", "amount": 10}]`
    *   `quality_range`: `{"min": 2, "max": 4}`
    *   `custom_data`: `{"defense_bonus_percentage": 5, "defense_bonus_per_quality": 2, "duration_seconds": 300, "taste": "metallic_earthy"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Crystal Highlands Wort): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Dwarven Spring Water): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Iron Shavings - trace, for mineral content): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Clay Flask): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Potion of Minor Fortitude): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Herbalism", `level`: 1, `affects_quality`: False

## Advanced Potions & Elixirs

---
**Recipe Archetype 25: Elixir of Elven Sight (Revised)**

*   **Recipe Table Entry:**
    *   `name`: "Elixir of Elven Sight"
    *   `description`: "An elven elixir that temporarily grants enhanced perception, allowing the imbiber to see subtle magical auras, hidden details, and traces of recent passage. A closely guarded Lethandrel formula."
    *   `recipe_category`: "Elixir - Sensory Enhancement"
    *   `crafting_time_seconds`: 1800
    *   `required_station_type`: "Elven Moonstill Altar"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"item_id_known": "Ancient Elven Scroll Fragment - Vision Rites", "skill_name": "Elven Alchemy", "level": 5, "location_specific_ritual": "Lethandrel_Leyroot_Grove_Moon_Phase_New"}`
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 400}, {"skill_name": "Elven Lore", "amount": 100}, {"skill_name": "Ritual Magic (Moon)", "amount": 50}]`
    *   `quality_range`: `{"min": 4, "max": 8}` (Quality affects duration and clarity of vision)
    *   `custom_data`: `{"effects": ["see_magical_auras", "detect_hidden_objects_chance", "see_recent_tracks"], "duration_base_seconds": 600, "duration_per_quality": 120, "side_effect": "mild_headache_after_0.1"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Spirit Fox Saliva): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Lethandrel Moon-Dew): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Ground Moonstone): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Silver Inlay Crystal Vial - Crafted): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Elixir of Elven Sight): `quantity`: 1, `is_primary`: True, `chance`: 0.95 (delicate process)
    *   `item_id` (Blurred Vision Dust - byproduct if slightly failed): `quantity`: 1, `is_primary`: False, `chance`: 0.05
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 6, `affects_quality`: True, `affects_speed`: False
    *   `skill_name`: "Elven Alchemy", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Ritual Magic (Moon)", `level`: 3, `affects_quality`: True (critical for potency)

---
**Recipe Archetype 26: Ferverl Ash-Bound Resilience Tincture**

*   **Recipe Table Entry:**
    *   `name`: "Ferverl Ash-Bound Resilience Tincture"
    *   `description`: "A potent, dark tincture developed by Ferverl survivors. Grants significant resistance to environmental hazards like extreme heat, toxins, or magical corruption for a short period. Tastes of ash and determination."
    *   `recipe_category`: "Tincture - Environmental Resistance"
    *   `crafting_time_seconds`: 3600
    *   `required_station_type`: "Ferverl Ritual Brazier & Alembic"
    *   `difficulty_level`: 8
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"faction_reputation": "Ferverl_Clans_Respected", "quest_completed": "The Emberflow Trials", "skill_name": "Ferverl Alchemy", "level": 6}`
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 600}, {"skill_name": "Ferverl Alchemy", "amount": 300}, {"skill_name": "Survival", "amount": 100}]`
    *   `quality_range`: `{"min": 5, "max": 9}` (Quality affects resistance strength and duration)
    *   `custom_data`: `{"resistances_granted": ["fire_medium", "poison_medium", "corruption_low"], "duration_seconds_base": 180, "duration_per_quality": 60, "side_effect": "temporary_numbness_0.05"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Ferverl Blood-Ash): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Ember Wastes Bloom): `quantity`: 5, `consumed_in_crafting`: True
    *   `item_id` (Basilisk Eye (Petrified) - sliver): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Orcish Grog Base - as a harsh solvent): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Obsidian Flask - Crafted/Purchased): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Ferverl Ash-Bound Resilience Tincture): `quantity`: 1, `is_primary`: True, `chance`: 0.9
    *   `item_id` (Inert Ash Clump - byproduct): `quantity`: 1, `is_primary`: False, `chance`: 0.1
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 7, `affects_quality`: True
    *   `skill_name`: "Ferverl Alchemy", `level`: 5, `affects_quality`: True, `affects_speed`: False
    *   `skill_name`: "Ritualism (Ferverl)", `level`: 4, `affects_quality`: True

---
**Recipe Archetype 27: Potion of Shadow Blending**

*   **Recipe Table Entry:**
    *   `name`: "Potion of Shadow Blending"
    *   `description`: "This murky potion, when consumed, allows the user to blend more effectively with shadows, making them harder to detect for a limited time. Smells faintly of damp earth and night."
    *   `recipe_category`: "Potion - Stealth/Illusion"
    *   `crafting_time_seconds`: 900
    *   `required_station_type`: "Shrouded Alchemical Table"
    *   `difficulty_level`: 5
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"manual_found": "Thief's Compendium - Chapter on Evasion", "skill_name": "Alchemy", "level": 4}`
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 150}, {"skill_name": "Stealth Lore", "amount": 30}]`
    *   `quality_range`: `{"min": 3, "max": 6}` (Quality affects stealth bonus and duration)
    *   `custom_data`: `{"stealth_bonus_modifier": 0.15, "stealth_bonus_per_quality": 0.05, "duration_seconds_base": 120, "duration_per_quality": 30, "visual_effect": "user_appears_dimmer_in_shadows"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Shimmering Marsh Cap - Purified): `quantity`: 2, `consumed_in_crafting`: True
    *   `item_id` (Shadow Panther Hide Oil - small amount): `quantity`: 1, `consumed_in_crafting`: True (Conceptual, might need a "Shadow Panther Hide Segment" to process into oil first)
    *   `item_id` (Lethandrel Moon-Dew): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Darkened Glass Vial): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Potion of Shadow Blending): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Herbalism (Fungi)", `level`: 3, `affects_quality`: True

## Alchemical Components & Bases

---
**Recipe Archetype 28: Universal Solvent Base (Weak)**

*   **Recipe Table Entry:**
    *   `name`: "Universal Solvent Base (Weak)"
    *   `description`: "A basic alchemical solvent created by carefully neutralizing common acids and bases. Can dissolve a wider range of materials than simple water, but is not particularly potent."
    *   `recipe_category`: "Alchemical Component - Solvent"
    *   `crafting_time_seconds`: 600
    *   `required_station_type`: "Glassware & Distillation Setup"
    *   `difficulty_level`: 3
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"textbook_studied": "Fundamentals of Alchemical Reactions", "skill_name": "Basic Chemistry", "level": 2}`
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 40}, {"skill_name": "Basic Chemistry", "amount": 20}]`
    *   `quality_range`: `{"min": 1, "max": 3}` (Quality affects purity and solvent strength)
    *   `custom_data`: `{"solvent_power_rating": 3, "neutral_ph": true, "shelf_life_days": 30}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Sulfur Powder): `quantity`: 1, `consumed_in_crafting`: True (to make weak sulfuric acid)
    *   `item_id` (Forge Ash - for Lye): `quantity`: 2, `consumed_in_crafting`: True (to make weak potassium hydroxide)
    *   `item_id` (Filtered River Water): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Rock Salt Chunks - for stabilization): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Large Glass Beaker): `quantity`: 1, `consumed_in_crafting`: True (as the product container)
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Universal Solvent Base (Weak)): `quantity`: 1, `is_primary`: True, `chance`: 0.9
    *   `item_id` (Impure Salt Precipitate - byproduct): `quantity`: 1, `is_primary`: False, `chance`: 0.1
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 2, `affects_quality`: True
    *   `skill_name`: "Basic Chemistry", `level`: 1, `affects_quality`: True

---
**Recipe Archetype 29: Beastfolk Totemic Catalyst**

*   **Recipe Table Entry:**
    *   `name`: "Beastfolk Totemic Catalyst"
    *   `description`: "A potent alchemical catalyst prepared by Ashkar Vale shamans. It's made from a blend of animal parts, sacred herbs, and spirit-infused water, designed to empower nature-aspected potions and rituals."
    *   `recipe_category`: "Alchemical Component - Catalyst"
    *   `crafting_time_seconds`: 7200 (includes ritual steeping)
    *   `required_station_type`: "Ashkar Vale Spirit Circle with Offering Bowl"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"tribal_favor": "Ashkar_Vale_Shamans_Friendly", "vision_quest_completed": "The Whispering Wilds", "skill_name": "Beastfolk Shamanism", "level": 5}`
    *   `experience_gained`: `[{"skill_name": "Alchemy", "amount": 300}, {"skill_name": "Beastfolk Shamanism", "amount": 200}, {"skill_name": "Ritualism (Nature)", "amount": 100}]`
    *   `quality_range`: `{"min": 4, "max": 8}` (Quality affects potency multiplication)
    *   `custom_data`: `{"catalyst_effect": "doubles_potency_nature_potions_reduces_brewing_time_by_25_percent", "charges": 3, "revered_by_beastfolk": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Spirit Fox Saliva): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Griffin Feather (Down)): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Verdant Vine Extract): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Ashkar Vale Spirit-Water): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Carved Bone Fetish - as ritual focus): `quantity`: 1, `consumed_in_crafting`: False (reusable focus)
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Beastfolk Totemic Catalyst): `quantity`: 1, `is_primary`: True, `chance`: 1.0
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Alchemy", `level`: 5, `affects_quality`: True
    *   `skill_name`: "Beastfolk Shamanism", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Ritualism (Nature)", `level`: 3, `affects_quality`: True

---
This provides a good range of alchemical materials and recipes, from common brews to culturally specific and powerful elixirs. As with blacksmithing, this can be expanded almost infinitely by:

*   Introducing more unique flora and fauna for reagents.
*   Creating multi-stage recipes (e.g., first create a "Purified Toxin," then use that in a "Weak Poison" recipe).
*   Adding recipes for alchemical greases, bombs, incense, or even transformative concoctions.
*   Detailing more specific ritual components or preparation steps in the `custom_data` or as ingredient notes.

Let me know when you're ready for the next crafting skill, or if you'd like to refine Alchemy further!