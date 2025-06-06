# Material Archetypes

## Blacksmithing & Armorsmithing Materials

### Rusty Iron Scrap
- **Description:** Rusty pieces of iron salvaged from ruins or old equipment. Requires significant cleaning and processing before use.
- **Material Type:** METAL
- **Rarity:** COMMON
- **Base Value:** 0.5
- **Weight:** 0.3
- **Is Craftable:** False
- **Source Tags:** salvaged_ruins, surface_find
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Low Quality Iron Ingot
  - purity: 0.4
  - yield_per_unit: 0.3
  - notes: Requires significant cleaning and processing.

### Common Iron Ore
- **Description:** Unrefined iron ore commonly found in mountainous regions and hills. A staple resource for blacksmiths.
- **Material Type:** ORE
- **Rarity:** COMMON
- **Base Value:** 2
- **Weight:** 0.5
- **Is Craftable:** False
- **Source Tags:** mined_stonewake, mountain_vein, rivemark_hills
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Iron Ingot
  - purity: 0.7
  - yield_per_unit: 0.5

### Copper Ore
- **Description:** Raw copper ore with distinctive blue-green coloration. Essential for bronze production and decorative metalwork.
- **Material Type:** ORE
- **Rarity:** COMMON
- **Base Value:** 3
- **Weight:** 0.4
- **Is Craftable:** False
- **Source Tags:** mined_crystal_highlands, surface_deposit
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Copper Ingot
  - purity: 0.8
  - yield_per_unit: 0.6
  - conductivity: high

### Tin Ore
- **Description:** Silvery-white metal ore used primarily in alloys. Essential for bronze production.
- **Material Type:** ORE
- **Rarity:** UNCOMMON
- **Base Value:** 5
- **Weight:** 0.4
- **Is Craftable:** False
- **Source Tags:** mined_dwarven_foothills, stream_panned
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Tin Ingot
  - purity: 0.6
  - alloy_component: bronze

### Deepvein Silver Ore
- **Description:** Lustrous silver ore mined from deep shaft mines. Prized for both decorative use and effectiveness against undead.
- **Material Type:** ORE
- **Rarity:** UNCOMMON
- **Base Value:** 15
- **Weight:** 0.6
- **Is Craftable:** False
- **Source Tags:** mined_dwarven_deepshafts, anti_undead_trace, lethandrel_trade_rare
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Silver Ingot
  - purity: 0.85
  - magical_conductivity: low
  - value_modifier_vs_undead: 1.1

### Stonewake Coal Seam
- **Description:** Coal from the Stonewake region, a vital fuel source for forges and industry.
- **Material Type:** ORE
- **Rarity:** COMMON
- **Base Value:** 1
- **Weight:** 0.2
- **Is Craftable:** False
- **Source Tags:** mined_stonewake_caldera, fuel_source, industrial_grade
- **Illicit in Regions:** *None*
- **Properties:**
  - fuel_value: 15
  - smoke_level: medium
  - ash_content: high

### Orcish Blood Iron Ore
- **Description:** A mysterious ore mined in sacred orcish sites. Contains trace elements that give it unique properties when forged with traditional orcish methods.
- **Material Type:** ORE
- **Rarity:** RARE
- **Base Value:** 40
- **Weight:** 0.7
- **Is Craftable:** False
- **Source Tags:** orcish_sacred_mine, rivemark_borderlands, ritual_harvest
- **Illicit in Regions:** *None*
- **Properties:**
  - smelts_into: Blood Iron Ingot
  - purity: 0.6
  - innate_property: minor_life_steal_weapon
  - strength_modifier: 1.1
  - brittleness_if_impure: high

<!-- ...continue with all remaining BLACKSMITHING_MATERIALS entries... -->