
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