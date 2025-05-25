
# Relic-Smithing & Artifact Tinkering Recipes

Recipes here are more like "Procedures" or "Experimental Blueprints." Success is often not guaranteed, and failure can be catastrophic.

---
**Recipe Archetype 30: Procedure - Stabilize Minor War-Core Fragment**

*   **Recipe Table Entry:**
    *   `id`: (UUID)
    *   `name`: "Procedure: Stabilize Minor War-Core Fragment"
    *   `description`: "A risky procedure to temporarily stabilize a small fragment of a Crimson Dissonance War-Core, reducing its ambient corruption and allowing for safer study or use as a very short-term power source."
    *   `recipe_category`: "Relic Stabilization - Power Core"
    *   `crafting_time_seconds`: 7200 (Requires constant monitoring)
    *   `required_station_type`: "Relic Containment Workbench with Nullifier Array"
    *   `difficulty_level`: 8 (High chance of partial failure or minor incident)
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"research_notes_found": "Fragmented_Dissonance_Core_Studies_Crucible_Spire", "skill_name": "Relic Tinkering", "level": 5, "tool_possessed": "Accord-Standard Nullifier Rod"}`
    *   `experience_gained`: `[{"skill_name": "Relic Tinkering", "amount": 1000}, {"skill_name": "Dissonance Lore", "amount": 200}, {"skill_name": "Hazardous Material Handling", "amount": 100}]`
    *   `quality_range`: `{"min": 1, "max": 4}` (Quality represents stability level achieved: 1=Barely Stable, 4=Moderately Stable for Short Term)
    *   `custom_data`: `{"failure_consequences_critical": "Mana_explosion_corruption_spread_spawns_energy_wisp", "failure_consequences_minor": "Increased_instability_nullifier_rod_drained_minor_researcher_corruption", "successful_output_lifespan_hours": "quality_level_x_6"}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Shattered War-Core Fragment - Small Size Only): `quantity`: 1, `consumed_in_crafting`: True (item is transformed)
    *   `item_id` (Accord-Standard Nullifier Rod - Min 50% Charge): `quantity`: 1, `consumed_in_crafting`: False (charge is consumed based on success)
    *   `item_id` (Inert Clay (Mana Absorptive)): `quantity`: 5, `consumed_in_crafting`: True (as packing and emergency absorption)
    *   `item_id` (Quenched Quicksilver Solution - for fine-tuning): `quantity`: 1, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Stabilized Minor War-Core Fragment - Quality X): `quantity`: 1, `is_primary`: True, `chance`: 0.6 (Success chance based on skill, tools, luck)
    *   `item_id` (Highly Corrupted Dross - hazardous waste): `quantity`: 1, `is_primary`: False, `chance`: 0.3 (Partial failure)
    *   `item_id` (Empty/Destroyed Containment - on critical failure): `quantity`: 1, `is_primary`: False, `chance`: 0.1
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Relic Tinkering", `level`: 7, `affects_quality`: True, `affects_speed`: False (cannot rush)
    *   `skill_name`: "Energy Systems (Relic)", `level`: 5, `affects_quality`: True
    *   `skill_name`: "Hazardous Material Handling", `level`: 3, `affects_quality`: False (Pass/Fail for safety)

---
**Recipe Archetype 31: Blueprint - Repurpose Sentinel Plating for Shield Core**

*   **Recipe Table Entry:**
    *   `name`: "Blueprint: Repurpose Sentinel Plating for Shield Core"
    *   `description`: "A complex blueprint detailing how to integrate a segment of Dissonance-era Sentinel Plating into the core of a modern shield, hoping to impart some of its legendary resilience and energy dampening."
    *   `recipe_category`: "Relic Repurposing - Armor Enhancement"
    *   `crafting_time_seconds`: 10800
    *   `required_station_type`: "Master Armorer's Forge with Relic Integration Rig"
    *   `difficulty_level`: 7
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"blueprint_acquired": "Salvaged_Accord_R&D_Notes_Stonewake_Vault", "skill_name": "Armorsmithing (Master)", "level": 8, "skill_name": "Relic Tinkering", "level": 4}`
    *   `experience_gained`: `[{"skill_name": "Armorsmithing (Master)", "amount": 700}, {"skill_name": "Relic Tinkering", "amount": 300}, {"skill_name": "Material Science (Alloy)", "amount": 150}]`
    *   `quality_range`: `{"min": 3, "max": 7}` (Quality reflects integration success and resulting shield properties)
    *   `custom_data`: `{"resulting_shield_properties": ["enhanced_physical_dr", "chance_to_dampen_specific_magic_type_if_aligned"], "risk_of_latent_energy_awakening": 0.05}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Inert Sentinel Plating Segment): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Dwarven Steel Ingot - for shield frame): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Silver Wire Spool (Fine) - for energy conduits): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Elven Ward-Weave Mesh - for internal dampening): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Multi-Spectrum Goggles - tool, not consumed): `quantity`: 1, `consumed_in_crafting`: False
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Sentinel-Core Shield (Quality X)): `quantity`: 1, `is_primary`: True, `chance`: 0.75
    *   `item_id` (Cracked Sentinel Plating & Ruined Shield Frame - failure): `quantity`: 1, `is_primary`: False, `chance`: 0.25
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Armorsmithing (Master)", `level`: 7, `affects_quality`: True
    *   `skill_name`: "Relic Tinkering", `level`: 6, `affects_quality`: True
    *   `skill_name`: "Material Science (Alloy)", `level`: 4, `affects_quality`: True

---
**Recipe Archetype 32: Experiment - Controlled Discharge of Dissonance Echo Crystal**

*   **Recipe Table Entry:**
    *   `name`: "Experiment: Controlled Discharge of Dissonance Echo Crystal"
    *   `description`: "EXTREMELY DANGEROUS. An experimental attempt to trigger a controlled, minor discharge from a Dissonance Echo Crystal, hoping to capture a sliver of its trapped energy or information without causing a catastrophic release. Success is highly improbable."
    *   `recipe_category`: "Relic Research - Forbidden Knowledge"
    *   `crafting_time_seconds`: 21600 (Mostly setup and remote observation)
    *   `required_station_type`: "Remote Relic Analysis Chamber (Fortified)"
    *   `difficulty_level`: 10 (Almost certain to have unintended consequences)
    *   `is_discoverable`: True (Only through piecing together multiple forbidden texts and surviving previous relic mishaps)
    *   `unlock_conditions`: `{"forbidden_knowledge_fragments_combined": 5, "skill_name": "Relic Tinkering (Grandmaster)", "level": 10, "will_to_risk_everything_flag": true, "containment_field_projector_available": true}`
    *   `experience_gained`: `[{"skill_name": "Relic Tinkering (Grandmaster)", "amount": 5000_if_survived, "skill_name": "Dissonance Theory (PhD)", "amount": 1000_if_data_retrieved}]`
    *   `quality_range`: `{"min": 0, "max": 2}` (0=Catastrophic Failure, 1=Minor Data/Energy Fragment Retrieved, 2=Significant Data/Energy Fragment Retrieved)
    *   `custom_data`: `{"catastrophic_failure_outcomes": ["reality_tear_local_area", "summon_powerful_dissonance_echo_entity", "temporal_distortion_wave", "researcher_disintegrated_or_driven_mad"], "success_rewards_potential": ["unique_spell_fragment", "blueprint_for_lost_tech", "glimpse_into_dissonance_event"]}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Echo Crystal Shard (Dissonance)): `quantity`: 1, `consumed_in_crafting`: True (likely destroyed or altered)
    *   `item_id` (Containment Field Projector (Small) - multiple units if possible): `quantity`: 1, `consumed_in_crafting`: True (likely overloaded/destroyed)
    *   `item_id` (Ferverl Leyline Siphon - multiple, as sacrificial drains): `quantity`: 3, `consumed_in_crafting`: True
    *   `item_id` (Sonic Emitter (Fine Tuned) - for precise resonance trigger): `quantity`: 1, `consumed_in_crafting`: False (if not destroyed in failure)
    *   `item_id` (Researcher's Last Will and Testament - optional but advised): `quantity`: 1, `consumed_in_crafting`: False
*   **Recipe Outputs Table Entries (Highly Variable, examples):**
    *   `item_id` (Fragment of Lost Dissonance Knowledge - Quality X): `quantity`: 1, `is_primary`: True, `chance`: 0.05 (for Q1 or Q2)
    *   `item_id` (Unstable Temporal Essence): `quantity`: 1, `is_primary`: True, `chance`: 0.02 (for Q1 or Q2)
    *   `item_id` (Zone of Complete Annihilation - byproduct of Q0): `quantity`: 1, `is_primary`: False, `chance`: 0.93 (for Q0 - Catastrophe)
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Relic Tinkering (Grandmaster)", `level`: 10, `affects_quality`: True (influences chance of non-catastrophic outcome)
    *   `skill_name`: "Theoretical Physics (Dissonance)", `level`: 8, `affects_quality`: True
    *   `skill_name`: "Planetary Scale Evacuation Planning", `level`: 1, `affects_quality`: False (Joke, but implies severe risk)

---
**Recipe Archetype 33: Procedure - Attune Relic Shard to User (Minor)**

*   **Recipe Table Entry:**
    *   `name`: "Procedure: Attune Relic Shard to User (Minor)"
    *   `description`: "A dangerous ritual to attempt a minor psychic and magical attunement between a user and a relatively stable, small relic shard. Success can grant minor passive bonuses or abilities, but failure can lead to corruption or backlash."
    *   `recipe_category`: "Relic Attunement - Personal Enhancement"
    *   `crafting_time_seconds`: 3600 (Requires meditation and ritual focus)
    *   `required_station_type`: "Attunement Circle with Warding Runes"
    *   `difficulty_level`: 6
    *   `is_discoverable`: True
    *   `unlock_conditions`: `{"study_of_ferverl_symbiosis_texts": true, "skill_name": "Relic Empathy", "level": 3, "item_to_attune_is_minor_and_semi_stable": true}`
    *   `experience_gained`: `[{"skill_name": "Relic Empathy", "amount": 500}, {"skill_name": "Willpower Training", "amount": 100}]`
    *   `quality_range`: `{"min": 0, "max": 3}` (0=Failure/Corruption, 1=Weak Attunement, 2=Moderate Attunement, 3=Strong Minor Attunement)
    *   `custom_data`: `{"attunement_effect_depends_on_relic_type": true, "corruption_points_gained_on_failure_1d6": true, "mental_strain_involved": true}`
*   **Recipe Ingredients Table Entries:**
    *   `item_id` (Specific Minor Relic Shard - e.g., "Inert Sentinel Plating Fragment"): `quantity`: 1, `consumed_in_crafting`: False (item is modified, not consumed)
    *   `item_id` (User's Own Blood - small vial, for sympathetic link): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Purified Leyline Water - for cleansing ritual space): `quantity`: 1, `consumed_in_crafting`: True
    *   `item_id` (Incense of Mental Clarity - e.g., Thal-Zirad Sun-Dried Petals): `quantity`: 3, `consumed_in_crafting`: True
*   **Recipe Outputs Table Entries:**
    *   `item_id` (Attuned [Relic Shard Name] - Quality X, bound to user): `quantity`: 1, `is_primary`: True, `chance`: 0.7
    *   `item_id` (Corrupted [Relic Shard Name] - hostile or inert): `quantity`: 1, `is_primary`: False, `chance`: 0.3
*   **Skill Requirements Table Entries:**
    *   `skill_name`: "Relic Empathy", `level`: 5, `affects_quality`: True
    *   `skill_name`: "Meditation & Focus", `level`: 4, `affects_quality`: True
    *   `skill_name`: "Ritualism (Warding)", `level`: 3, `affects_quality`: False (prevents worse outcomes)

---

This skill is all about high stakes. The materials are rare and dangerous, the procedures complex, and the outcomes uncertain. It offers a path to unique power but at considerable risk, fitting the lore of Crucible Spire and the Crimson Dissonance.

This should provide a strong thematic and mechanical basis for Relic-Smithing. Let me know where you'd like to go next!