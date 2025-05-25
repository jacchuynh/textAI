
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