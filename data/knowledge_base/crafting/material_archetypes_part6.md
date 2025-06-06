## Fuels & Additives

### Seasoned Hardwood
- **Description:** Properly dried hardwood for forge use. Burns hotter than green wood but with more smoke.
- **Material Type:** WOOD
- **Rarity:** COMMON
- **Base Value:** 0.5
- **Weight:** 0.3
- **Is Craftable:** False
- **Source Tags:** general_fuel, forestry_byproduct
- **Illicit in Regions:** *None*
- **Properties:**
  - fuel_value: 5
  - smoke_level: high
  - burn_duration_modifier: 0.8

### Magma-Kissed Coal
- **Description:** Coal from geothermal vents in Stonewake. Burns extremely hot with minimal smoke, ideal for high-temperature forging.
- **Material Type:** ORE
- **Rarity:** UNCOMMON
- **Base Value:** 8
- **Weight:** 0.25
- **Is Craftable:** False
- **Source Tags:** stonewake_lower_vents, geothermal_fuel, dwarven_preferred
- **Illicit in Regions:** *None*
- **Properties:**
  - fuel_value: 25
  - smoke_level: low
  - heat_intensity: very_high
  - ignites_quickly: True

### Limestone Flux
- **Description:** Powdered limestone used as a purification agent in smelting to remove impurities and improve metal quality.
- **Material Type:** CRAFTED
- **Rarity:** COMMON
- **Base Value:** 1
- **Weight:** 0.1
- **Is Craftable:** True
- **Source Tags:** crushed_limestone, purification_agent
- **Illicit in Regions:** *None*
- **Properties:**
  - impurity_removal_efficiency: 0.6
  - slag_reduction: True

### Dwarven Oath-Sand
- **Description:** Crystalline sand from sacred dwarven caves. Used in ritual smithing to enhance durability and bind oaths to metal.
- **Material Type:** MAGICAL
- **Rarity:** RARE
- **Base Value:** 30
- **Weight:** 0.05
- **Is Craftable:** False
- **Source Tags:** dwarven_sacred_cave_sand, ritual_smithing_additive
- **Illicit in Regions:** *None*
- **Properties:**
  - effect_on_metal: enhances_durability_oaths
  - application: sprinkled_during_tempering
  - rarity_modifier_dwarven_items: 1.1

### Standard Quenching Oil
- **Description:** A blend of animal fats and mineral oils used to rapidly cool heated metal during tempering.
- **Material Type:** CRAFTED
- **Rarity:** COMMON
- **Base Value:** 4
- **Weight:** 0.2
- **Is Craftable:** True
- **Source Tags:** rendered_animal_fat, mineral_oil_blend
- **Illicit in Regions:** *None*
- **Properties:**
  - cooling_rate: medium
  - effect_on_hardness: standard

### Orcish Fury-Quench
- **Description:** A volatile quenching fluid used by orcish smiths, containing herbs, blood, and secret ingredients. Creates jagged edges.
- **Material Type:** MAGICAL
- **Rarity:** RARE
- **Base Value:** 25
- **Weight:** 0.2
- **Is Craftable:** True
- **Source Tags:** orcish_ritual_blend_herbs_blood, secret_ingredient_grog
- **Illicit in Regions:** *None*
- **Properties:**
  - cooling_rate: fast_volatile
  - effect_on_metal: adds_minor_jagged_edge_chance
  - risk_of_brittleness: 0.1
  - fumes_intoxicating: True

### Purified Firecrystal Dust
- **Description:** Refined dust from fire crystals found in the Ember Wastes. Drastically increases forge temperature when added to fuel.
- **Material Type:** MAGICAL
- **Rarity:** RARE
- **Base Value:** 35
- **Weight:** 0.02
- **Is Craftable:** True
- **Source Tags:** refined_firecrystal_ember_wastes, high_temp_fuel_additive
- **Illicit in Regions:** *None*
- **Properties:**
  - fuel_value_boost_percentage: 50
  - heat_intensity_increase: high
  - risk_of_flare_up: 0.05
  - notes: Use sparingly.

### Elven Moon-Flux
- **Description:** A shimmering silver powder created by elven alchemists under moonlight. Purifies magical metals and enhances enchantability.
- **Material Type:** MAGICAL
- **Rarity:** EPIC
- **Base Value:** 120
- **Weight:** 0.03
- **Is Craftable:** False
- **Source Tags:** lethandrel_alchemical_creation, lunar_aligned_purifier
- **Illicit in Regions:** *None*
- **Properties:**
  - impurity_removal_efficiency_magical_metals: 0.9
  - enhances_enchantability: True
  - requires_moonlight_during_use: True
  - rarity_modifier_elven_items: 1.3

### Dwarven Hearthstone Powder
- **Description:** Ground stone from dwarven forges that have been active for centuries. Imparts minor fire resistance and durability to items.
- **Material Type:** MAGICAL
- **Rarity:** RARE
- **Base Value:** 40
- **Weight:** 0.05
- **Is Craftable:** False
- **Source Tags:** ground_dwarven_forge_hearthstone, ritual_smithing_additive
- **Illicit in Regions:** *None*
- **Properties:**
  - effect_on_metal: imparts_minor_fire_resistance_and_durability_dwarven_items
  - application: mixed_with_quenching_oil_or_dusted_on

--- 

## Woodworking & Carpentry Materials

### Pine Log (Rough Cut)
- **Description:** A freshly cut log of pine wood. Soft and easy to work with, but not very durable.
- **Material Type:** WOOD_RAW
- **Rarity:** COMMON
- **Base Value:** 2
- **Weight:** 15.0
- **Is Craftable:** False
- **Source Tags:** harvested_verdant_frontier_pine_forests, common_softwood_lumber
- **Illicit in Regions:** *None*
- **Properties:**
  - processes_into: Pine Planks
  - density_kg_m3: 450
  - hardness_janka_lbf: 380
  - workability: easy
  - knot_frequency: medium
  - resin_content: medium_high
  - uses_raw: firewood, rough_shelter_construction

### Pine Planks (Bundle of 5)
- **Description:** Milled pine boards ready for construction or crafting. Affordable but prone to warping and splintering.
- **Material Type:** WOOD_PROCESSED
- **Rarity:** COMMON
- **Base Value:** 5
- **Weight:** 5.0
- **Is Craftable:** True
- **Source Tags:** milled_pine_logs_rivemark_sawmill, basic_construction_material
- **Illicit in Regions:** *None*
- **Properties:**
  - dimensions_cm_each_plank: 200x20x2.5
  - finish: rough_sawn
  - nail_holding_ability: fair
  - splinter_risk: medium
  - uses: simple_furniture, crates, fences, flooring_sublayer

### Oak Log (Seasoned)
- **Description:** A properly aged oak log, dried to reduce moisture content. Prized for its strength and beautiful grain.
- **Material Type:** WOOD_RAW
- **Rarity:** UNCOMMON
- **Base Value:** 15
- **Weight:** 25.0
- **Is Craftable:** False
- **Source Tags:** harvested_whispering_woods_oak_groves_aged_one_year, durable_hardwood_lumber
- **Illicit in Regions:** *None*
- **Properties:**
  - processes_into: Oak Beams_Oak Planks
  - density_kg_m3: 720
  - hardness_janka_lbf: 1290
  - workability: moderate_requires_sharp_tools
  - tannin_content: high_corrodes_iron_fasteners
  - strength: high

### Oak Planks (Bundle of 3)
- **Description:** High-quality oak planks milled from seasoned logs. Excellent for fine furniture and structural applications.
- **Material Type:** WOOD_PROCESSED
- **Rarity:** UNCOMMON
- **Base Value:** 25
- **Weight:** 7.0
- **Is Craftable:** True
- **Source Tags:** milled_seasoned_oak_logs_skarport_carpentry_guild, high_quality_furniture_construction
- **Illicit in Regions:** *None*
- **Properties:**
  - dimensions_cm_each_plank: 200x15x3
  - finish: planed_smooth
  - nail_holding_ability: good
  - stain_affinity: excellent
  - uses: fine_furniture, weapon_hafts, ship_decking, heavy_doors

<!-- ...continue with all woodworking, tailoring, alchemy, jewelcrafting, and relicsmithing materials as in the source file, expanding each entry in this detailed format... -->