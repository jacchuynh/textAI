## Blacksmithing & Armorsmithing Materials (continued)

### Cast Iron Scrap
- **Description:** Fragments of broken cast iron items, primarily cookware and machinery parts. Can be reforged into usable metal.
- **Material Type:** METAL
- **Rarity:** COMMON
- **Base Value:** 0.8
- **Weight:** 0.4
- **Is Craftable:** False
- **Source Tags:** discarded_cookware, broken_machinery_parts_skarport
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Recycled Cast Iron Ingot
  - purity: 0.6
  - brittleness: high
  - good_for_non_impact_items: True

### Raw Lead Chunks
- **Description:** Heavy, soft metal chunks often found alongside silver deposits. Useful for weights and specialized applications.
- **Material Type:** ORE
- **Rarity:** UNCOMMON
- **Base Value:** 6
- **Weight:** 0.8
- **Is Craftable:** False
- **Source Tags:** mined_alongside_silver_dwarven_mines, soft_heavy_metal
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Lead Ingot
  - purity: 0.9
  - density: very_high
  - toxicity_warning_if_used_for_food_items: True

### Tarnished Silver Lumps
- **Description:** Darkened silver pieces from old jewelry, cutlery, or minor treasure finds. Can be refined into usable silver.
- **Material Type:** METAL
- **Rarity:** COMMON
- **Base Value:** 5
- **Weight:** 0.2
- **Is Craftable:** False
- **Source Tags:** old_jewelry_scrap, discarded_cutlery, minor_treasure_finds
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Reclaimed Silver Ingot
  - purity: 0.7
  - requires_polishing_flux: True

### Gold Dust
- **Description:** Fine particles of gold collected from riverbeds or salvaged from jewelry workshop sweepings. Must be accumulated to be useful.
- **Material Type:** METAL
- **Rarity:** RARE
- **Base Value:** 50
- **Weight:** 0.01
- **Is Craftable:** False
- **Source Tags:** panned_from_rivemark_delta_sands, jewelry_workshop_sweepings, treasure_hoard_trace
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Gold Nugget
  - purity: 0.95
  - notes: Usually requires accumulation to be useful for ingots.

### Colored Glass Shards
- **Description:** Broken pieces of colored glass from bottles or alchemical vials. Can be melted for crude decorative inlays.
- **Material Type:** GEM
- **Rarity:** COMMON
- **Base Value:** 1
- **Weight:** 0.1
- **Is Craftable:** False
- **Source Tags:** broken_bottles_skarport_alleys, discarded_alchemical_vials_lethandrel
- **Illicit in Regions:** *None*
- **Properties:**
  - smithing_use: crude_decorative_inlay_requires_melting
  - color_variety: green, brown, clear_ish
  - sharpness: low

### Polished River Stones
- **Description:** Smooth stones in various colors collected from riverbeds. Used as weights or decorative elements in smithing.
- **Material Type:** GEM
- **Rarity:** COMMON
- **Base Value:** 0.5
- **Weight:** 0.15
- **Is Craftable:** False
- **Source Tags:** collected_rivemark_riverbeds, smooth_varied_colors
- **Illicit in Regions:** *None*
- **Properties:**
  - smithing_use: pommel_weights_decorative_insets_non_gem_quality
  - hardness: 4

---

## Refined Metals (Ingots)

### Low Quality Iron Ingot
- **Description:** Iron refined from scrap. Brittle and prone to rust, but usable for basic items.
- **Material Type:** METAL
- **Rarity:** COMMON
- **Base Value:** 1
- **Weight:** 0.25
- **Is Craftable:** True
- **Source Tags:** smelted_scrap
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 3
  - tensile_strength: 2
  - rust_susceptibility: high

### Iron Ingot
- **Description:** Refined iron metal, ready for smithing into tools, weapons, or armor. A fundamental material in blacksmithing.
- **Material Type:** METAL
- **Rarity:** COMMON
- **Base Value:** 5
- **Weight:** 0.4
- **Is Craftable:** True
- **Source Tags:** smelted_ore_standard
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 5
  - tensile_strength: 4
  - rust_susceptibility: medium

### Copper Ingot
- **Description:** Refined copper with a distinctive reddish-orange color. Highly malleable and excellent conductor.
- **Material Type:** METAL
- **Rarity:** COMMON
- **Base Value:** 7
- **Weight:** 0.35
- **Is Craftable:** True
- **Source Tags:** smelted_ore_standard
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 2
  - malleability: 8
  - conductivity_electrical_magical: high
  - corrosion_resistance: good

### Tin Ingot
- **Description:** Soft, silvery metal primarily used in alloys, especially bronze. Relatively low melting point makes it easy to work with.
- **Material Type:** METAL
- **Rarity:** UNCOMMON
- **Base Value:** 10
- **Weight:** 0.35
- **Is Craftable:** True
- **Source Tags:** smelted_ore_standard
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 1
  - malleability: 7
  - alloy_primary_use: bronze_production

### Bronze Ingot
- **Description:** An alloy of copper and tin. More durable than copper alone and historically significant for early armaments.
- **Material Type:** METAL
- **Rarity:** UNCOMMON
- **Base Value:** 20
- **Weight:** 0.4
- **Is Craftable:** True
- **Source Tags:** alloyed_copper_tin
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 6
  - tensile_strength: 5
  - corrosion_resistance: very_good
  - historical_significance: early_accord_armaments

### Steel Ingot
- **Description:** Iron alloyed with carbon for improved hardness and durability. Essential for quality weapons and armor.
- **Material Type:** METAL
- **Rarity:** UNCOMMON
- **Base Value:** 30
- **Weight:** 0.4
- **Is Craftable:** True
- **Source Tags:** refined_iron_carbon_alloy
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 7
  - tensile_strength: 6
  - edge_retention: good

### Silver Ingot
- **Description:** Purified silver metal, prized for its luster and effectiveness against supernatural threats like lycanthropes.
- **Material Type:** METAL
- **Rarity:** UNCOMMON
- **Base Value:** 45
- **Weight:** 0.5
- **Is Craftable:** True
- **Source Tags:** smelted_ore_refined
- **Illicit in Regions:** *None*
- **Properties:**
  - hardness: 3
  - malleability: 7
  - purity_for_enchanting: high
  - value_modifier_vs_lycanthropes: 1.2

<!-- ...continue with all other ingots, byproducts, and crafted items as in the source file... -->