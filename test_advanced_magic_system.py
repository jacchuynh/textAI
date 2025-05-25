#!/usr/bin/env python3
"""
Advanced Magic System Integration Test

This script demonstrates the complete magic system with all advanced features:
- Environmental magic resonance
- Mana heart evolution
- Spell combination
- Spell crafting
- Magical consequences
- Domain-magic synergy
- Tactical magic in combat
- Asynchronous processing with Redis and Celery
"""

import sys
import time
import random
from typing import Dict, List, Any, Optional, Tuple

# Add backend directory to path
sys.path.append("backend/src")

# Import magic system components
from game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, MagicTier, MagicSource, 
    Domain, DamageType, EffectType, TargetType
)

# Import advanced features
from game_engine.advanced_magic_features import (
    EnvironmentalMagicResonance, ManaHeartEvolution, SpellCombinationSystem,
    SpellCraftingSystem, MagicalConsequenceSystem, NPCMagicRelationship, 
    DomainMagicSynergy, TacticalMagicCombat, MagicalEconomy, AIGMMagicIntegration,
    NPC, CombatContext, Effect
)

# Import async processing
from game_engine.magic_async_processing import (
    MagicAsyncProcessor, create_magic_async_processor
)

# Import combat system components
from game_engine.enhanced_combat.combat_system_core import (
    Combatant, CombatMove, MoveType, Status
)


def create_test_character() -> Tuple[Combatant, Dict[Domain, int]]:
    """Create a test character with balanced domains"""
    domains = {
        Domain.BODY: 3,
        Domain.MIND: 4,
        Domain.CRAFT: 3,
        Domain.AWARENESS: 3,
        Domain.SOCIAL: 2,
        Domain.AUTHORITY: 2,
        Domain.SPIRIT: 4,
        Domain.FIRE: 2,
        Domain.WATER: 0,
        Domain.EARTH: 0,
        Domain.AIR: 0,
        Domain.LIGHT: 0,
        Domain.DARKNESS: 0
    }
    
    character = Combatant(
        name="Test Mage",
        domains=domains,
        max_health=100,
        current_health=100,
        max_stamina=50,
        current_stamina=50,
        max_focus=60,
        current_focus=60,
        max_spirit=70,
        current_spirit=70
    )
    
    return character, domains


def create_forest_location() -> Dict[str, Any]:
    """Create a test forest location with magical properties"""
    return {
        "id": "forest_grove_1",
        "name": "Whispering Grove",
        "description": "A dense forest with ancient trees. The air shimmers with magical energy from nearby leylines.",
        "environment": "forest",
        "features": ["ley_nexus", "ancient_trees", "sacred_grove"],
        "leyline_base": 3,
        "mana_flux_base": 2,
        "recent_magic_use": 3,
        "magical_instability": 1,
        "time": "dawn",
        "weather": "clear",
        "historical_events": ["ancient_ritual_site"]
    }


def create_corrupted_cave_location() -> Dict[str, Any]:
    """Create a test corrupted cave location"""
    return {
        "id": "corrupted_cave_1",
        "name": "Void's Maw",
        "description": "A dark cave where corruption seeps from the walls. Magic behaves unpredictably here.",
        "environment": "cave",
        "features": ["corrupted_leyline", "void_breach"],
        "leyline_base": 2,
        "mana_flux_base": 4,
        "recent_magic_use": 7,
        "magical_instability": 5,
        "corruption_level": 4,
        "time": "any",
        "weather": "n/a",
        "historical_events": ["magical_disaster", "crimson_dissonance_site"]
    }


def test_environmental_resonance():
    """Test the environmental magic resonance system"""
    print("\n=== Testing Environmental Magic Resonance ===")
    
    # Create the environmental resonance system
    resonance_system = EnvironmentalMagicResonance()
    
    # Create a test spell
    fire_spell = Spell(
        id="spell_test_fireball",
        name="Test Fireball",
        description="A ball of fire that explodes on impact",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A fiery explosion engulfs the target",
                magnitude=15,
                target_type=TargetType.SINGLE_ENEMY,
                damage_type=DamageType.FIRE
            )
        ],
        mana_cost=10,
        casting_time_seconds=2,
        domain_requirements=[],
        backlash_potential=0.1
    )
    
    # Create a healing spell
    heal_spell = Spell(
        id="spell_test_heal",
        name="Test Healing",
        description="A healing spell that restores health",
        tier=MagicTier.MANA_INFUSION,
        magic_source_affinity=[MagicSource.LEYLINE],
        effects=[
            MagicalEffect(
                effect_type=EffectType.HEAL,
                description_template="Healing energy flows through the target",
                magnitude=15,
                target_type=TargetType.SELF,
                damage_type=None
            )
        ],
        mana_cost=0,
        ley_energy_cost=10,
        casting_time_seconds=3,
        domain_requirements=[],
        backlash_potential=0.05
    )
    
    # Set spell schools (not in base class but used by advanced features)
    setattr(fire_spell, "school", "EVOCATION")
    setattr(heal_spell, "school", "RESTORATION")
    
    # Test different environments
    test_locations = [
        {"name": "Forest at Dawn", "time": "dawn", "weather": "clear", "environment_type": "forest"},
        {"name": "Desert Storm", "time": "noon", "weather": "storm", "environment_type": "desert"},
        {"name": "Night Graveyard", "time": "night", "weather": "fog", "environment_type": "graveyard"},
        {"name": "Volcano", "time": "day", "weather": "clear", "environment_type": "volcano"}
    ]
    
    for location in test_locations:
        fire_modifier = resonance_system.calculate_spell_power_modifier(fire_spell, location)
        heal_modifier = resonance_system.calculate_spell_power_modifier(heal_spell, location)
        
        print(f"\nLocation: {location['name']}")
        print(f"Fire Spell Modifier: {fire_modifier:.2f}x (base damage: {fire_spell.effects[0].magnitude}, modified: {int(fire_spell.effects[0].magnitude * fire_modifier)})")
        print(f"Healing Spell Modifier: {heal_modifier:.2f}x (base healing: {heal_spell.effects[0].magnitude}, modified: {int(heal_spell.effects[0].magnitude * heal_modifier)})")
        
        # Check for backlash chance modifiers
        backlash_mod = resonance_system.get_backlash_chance_modifier(fire_spell, location)
        if backlash_mod != 0:
            print(f"Backlash chance modifier: {backlash_mod:+.2f}")
        
        # Generate any environmental effects
        env_effects = resonance_system.get_environmental_magic_effects(location)
        if env_effects:
            print("Environmental magical effects:")
            for effect in env_effects:
                print(f"- {effect.description}")


def test_mana_heart_evolution():
    """Test the mana heart evolution system"""
    print("\n=== Testing Mana Heart Evolution ===")
    
    # Create a magic system
    magic_system = MagicSystem()
    
    # Create a character with a magic profile
    character, domains = create_test_character()
    magic_profile = magic_system.initialize_magic_user(domains)
    
    # Ensure the character has a Mana Heart
    if not magic_profile.has_mana_heart:
        result = magic_system.develop_mana_heart("test_character", magic_profile)
        print(f"Developed Mana Heart: {result['message']}")
        print(f"Mana: {magic_profile.mana_current}/{magic_profile.mana_max}")
    
    # Create the mana heart evolution system
    evolution_system = ManaHeartEvolution()
    
    # Get available evolution paths
    additional_stats = {
        "mana_heart_stage": "DEVELOPING",
        "spells_backfired": 3,
        "known_runes": 2
    }
    
    available_paths = evolution_system.get_available_evolution_paths(magic_profile, domains, additional_stats)
    
    print("\nAvailable Evolution Paths:")
    for path_id, path_info in available_paths.items():
        status = "Available" if path_info["requirements_met"] else "Requirements not met"
        print(f"- {path_info['name']}: {status}")
        if not path_info["requirements_met"]:
            print(f"  Missing requirements: {', '.join(path_info['unmet_requirements'])}")
    
    # Choose a path to evolve (if any are available)
    available_path = None
    for path_id, path_info in available_paths.items():
        if path_info["requirements_met"]:
            available_path = path_id
            break
    
    if available_path:
        print(f"\nEvolving along path: {available_paths[available_path]['name']}")
        result = evolution_system.evolve_mana_heart(magic_profile, available_path, domains, additional_stats)
        
        print(f"Evolution result: {result['message']}")
        print(f"New abilities: {', '.join(result['new_abilities'])}")
        print(f"Bonuses: {result['bonuses']}")
        
        if "mana_heart_stage" in result:
            print(f"Mana Heart Stage: {result['mana_heart_stage']['previous']} → {result['mana_heart_stage']['new']}")
        
        # Show updated magic profile
        print("\nUpdated Magic Profile:")
        print(f"Mana: {magic_profile.mana_current}/{magic_profile.mana_max}")
        print(f"Mana Regeneration: {magic_profile.mana_regeneration_rate}/second")
        print(f"Attunements: {', '.join(magic_profile.attunements)}")
        print(f"Skills: {', '.join(magic_profile.known_skills)}")
    else:
        print("\nNo evolution paths available. Work on meeting requirements first.")


def test_spell_combination():
    """Test the spell combination system"""
    print("\n=== Testing Spell Combination System ===")
    
    # Create a magic system
    magic_system = MagicSystem()
    
    # Create spells to combine
    fire_spell = Spell(
        id="spell_combine_fire",
        name="Flame Dart",
        description="A small dart of magical fire",
        tier=MagicTier.MANA_INFUSION,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A dart of fire strikes the target",
                magnitude=8,
                target_type=TargetType.SINGLE_ENEMY,
                damage_type=DamageType.FIRE
            )
        ],
        mana_cost=5,
        casting_time_seconds=1,
        domain_requirements=[],
        backlash_potential=0.05
    )
    
    ice_spell = Spell(
        id="spell_combine_ice",
        name="Frost Shard",
        description="A shard of magical ice",
        tier=MagicTier.MANA_INFUSION,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A shard of ice pierces the target",
                magnitude=7,
                target_type=TargetType.SINGLE_ENEMY,
                damage_type=DamageType.ICE
            )
        ],
        mana_cost=5,
        casting_time_seconds=1,
        domain_requirements=[],
        backlash_potential=0.05
    )
    
    # Register the spells with the magic system
    magic_system.casting_service.register_spell(fire_spell)
    magic_system.casting_service.register_spell(ice_spell)
    
    # Create a character with a magic profile
    character, domains = create_test_character()
    magic_profile = magic_system.initialize_magic_user(domains)
    
    # Ensure character has a Mana Heart and enough mana
    if not magic_profile.has_mana_heart:
        magic_system.develop_mana_heart("test_character", magic_profile)
    
    # Learn the spells
    magic_profile.known_spells.append("spell_combine_fire")
    magic_profile.known_spells.append("spell_combine_ice")
    
    # Add spell combination skill
    magic_profile.known_skills.append("spell_combination")
    
    # Create the spell combination system
    combination_system = SpellCombinationSystem(magic_system)
    
    # Check if spells can be combined
    can_combine, reason = combination_system.can_combine_spells("spell_combine_fire", "spell_combine_ice", magic_profile)
    
    print(f"Can combine spells: {can_combine}")
    print(f"Reason: {reason}")
    
    if can_combine:
        # Combine the spells
        result = combination_system.combine_spells("spell_combine_fire", "spell_combine_ice", magic_profile)
        
        print(f"\nCombination result: {result['message']}")
        if result['success']:
            print("\nCombined Spell:")
            print(f"Name: {result['combined_spell']['name']}")
            print(f"Description: {result['combined_spell']['description']}")
            print(f"Damage Multiplier: {result['combined_spell']['damage_multiplier']}")
            print(f"Base Power: {result['combined_spell']['base_power']}")
            print(f"Special Effects: {', '.join(str(effect) for effect in result['combined_spell']['special_effects'])}")
            print(f"Mana Cost: {result['combined_spell']['mana_cost']}")
            print(f"Backlash Chance: {result['combined_spell']['backlash_chance']:.2f}")
            print(f"\nRemaining Mana: {result['resources_remaining']['mana']}")
    else:
        print("\nCannot combine these spells.")


def test_spell_crafting():
    """Test the spell crafting system"""
    print("\n=== Testing Spell Crafting System ===")
    
    # Create a magic system
    magic_system = MagicSystem()
    
    # Create a character with a magic profile
    character, domains = create_test_character()
    magic_profile = magic_system.initialize_magic_user(domains)
    
    # Ensure character has a Mana Heart
    if not magic_profile.has_mana_heart:
        magic_system.develop_mana_heart("test_character", magic_profile)
    
    # Add spell crafting skill
    magic_profile.known_skills.append("spell_crafting")
    
    # Create the spell crafting system
    crafting_system = SpellCraftingSystem(magic_system)
    
    # Get available modifiers
    available_modifiers = crafting_system.get_available_modifiers(domains)
    
    print("Available Spell Modifiers:")
    for modifier_id, modifier_info in available_modifiers.items():
        status = "Available" if modifier_info["requirements_met"] else "Requirements not met"
        print(f"- {modifier_info['name']}: {status}")
        print(f"  Description: {modifier_info['description']}")
        if not modifier_info["requirements_met"]:
            print(f"  Missing requirements: {', '.join(modifier_info['unmet_requirements'])}")
    
    # Create a test spell
    test_spell = Spell(
        id="spell_to_modify",
        name="Lightning Strike",
        description="Calls down a bolt of lightning on the target",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A bolt of lightning strikes the target",
                magnitude=15,
                target_type=TargetType.SINGLE_ENEMY,
                damage_type=DamageType.LIGHTNING
            )
        ],
        mana_cost=12,
        casting_time_seconds=2,
        domain_requirements=[],
        backlash_potential=0.1
    )
    
    # Register the spell
    magic_system.casting_service.register_spell(test_spell)
    
    # Choose a modifier to apply (if any are available)
    available_modifier = None
    for modifier_id, modifier_info in available_modifiers.items():
        if modifier_info["requirements_met"]:
            available_modifier = modifier_id
            break
    
    if available_modifier:
        print(f"\nApplying modifier: {available_modifiers[available_modifier]['name']}")
        result = crafting_system.apply_spell_modifier("spell_to_modify", available_modifier, domains)
        
        if result['success']:
            print("\nOriginal Spell:")
            print(f"Name: {result['original_spell']['name']}")
            print(f"Description: {result['original_spell']['description']}")
            print(f"Mana Cost: {result['original_spell']['mana_cost']}")
            print(f"Casting Time: {result['original_spell']['casting_time_seconds']}s")
            
            print("\nModified Spell:")
            print(f"Name: {result['modified_spell']['name']}")
            print(f"Description: {result['modified_spell']['description']}")
            print(f"Mana Cost: {result['modified_spell']['mana_cost']}")
            print(f"Casting Time: {result['modified_spell']['casting_time_seconds']}s")
            print(f"Modified Effects: {', '.join(result['modified_spell']['modified_effects'])}")
        else:
            print(f"Modification failed: {result['message']}")
    else:
        print("\nNo modifiers available to apply. Work on meeting requirements first.")
    
    # Test creating a custom spell
    print("\nCreating a custom spell:")
    
    custom_spell_data = {
        "name": "Frost Nova",
        "description": "Creates an expanding ring of frost that damages and slows enemies",
        "tier": MagicTier.MANA_INFUSION,
        "magic_sources": [MagicSource.MANA_HEART, MagicSource.LEYLINE],
        "mana_cost": 15,
        "ley_energy_cost": 5,
        "casting_time_seconds": 3,
        "domain_requirements": [
            {"domain": "MIND", "value": 3},
            {"domain": "ICE", "value": 2}
        ],
        "effects": [
            {
                "effect_type": "DAMAGE",
                "target_type": "AREA_ENEMIES",
                "damage_type": "ICE",
                "magnitude": 12,
                "duration_seconds": None,
                "description": "A wave of frost expands outward, freezing enemies"
            },
            {
                "effect_type": "DEBUFF_STAT",
                "target_type": "AREA_ENEMIES",
                "magnitude": "movement_speed_reduction_30_percent",
                "duration_seconds": 30,
                "description": "The intense cold slows enemy movement"
            }
        ]
    }
    
    result = crafting_system.create_custom_spell(magic_profile, domains, custom_spell_data)
    
    if result['success']:
        print(f"Custom spell created: {result['spell']['name']}")
        print(f"Description: {result['spell']['description']}")
        print(f"Tier: {result['spell']['tier']}")
        print(f"Mana Cost: {result['spell']['mana_cost']}")
        print(f"Ley Energy Cost: {result['spell']['ley_energy_cost']}")
        print(f"Effects: {len(result['spell']['effects'])}")
        for i, effect in enumerate(result['spell']['effects']):
            print(f"  Effect {i+1}: {effect['type']} - {effect['damage_type'] if effect['damage_type'] else 'No damage'}")
        print(f"Backlash Potential: {result['spell']['backlash_potential']:.2f}")
    else:
        print(f"Custom spell creation failed: {result['message']}")


def test_magical_consequences():
    """Test the magical consequences system"""
    print("\n=== Testing Magical Consequences System ===")
    
    # Create the magical consequence system
    consequence_system = MagicalConsequenceSystem()
    
    # Create a test spell
    necromancy_spell = Spell(
        id="spell_test_necromancy",
        name="Raise Dead",
        description="Raises a corpse as an undead servant",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.SUMMON,
                description_template="A corpse rises as an undead servant",
                magnitude="undead_minion",
                target_type=TargetType.ENVIRONMENT
            )
        ],
        mana_cost=20,
        casting_time_seconds=5,
        domain_requirements=[],
        backlash_potential=0.2
    )
    
    # Set spell school
    setattr(necromancy_spell, "school", "NECROMANCY")
    
    # Create a dangerous spell with high backlash
    void_spell = Spell(
        id="spell_test_void",
        name="Void Rift",
        description="Opens a small rift to the void",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A rift to the void opens, pulling in nearby matter",
                magnitude=25,
                target_type=TargetType.AREA_ENEMIES,
                damage_type=DamageType.NECROTIC
            )
        ],
        mana_cost=30,
        casting_time_seconds=6,
        domain_requirements=[],
        backlash_potential=0.4
    )
    
    # Test successful necromancy spell
    location_id = "test_graveyard"
    location_magic_profile = {}  # In a real implementation, this would be a LocationMagicProfile
    spell_context = {
        "recent_casts_count": 1
    }
    
    print("\nCasting necromancy spell (success):")
    consequences = consequence_system.apply_spell_consequences(
        necromancy_spell, True, location_id, location_magic_profile, spell_context
    )
    
    if consequences:
        print("Magical consequences applied:")
        for effect in consequences:
            print(f"- {effect.id}: {effect.description}")
            if isinstance(effect.magnitude, list):
                for game_effect in effect.magnitude:
                    if isinstance(game_effect, dict) and "description" in game_effect:
                        print(f"  * {game_effect['description']}")
    else:
        print("No consequences were triggered.")
    
    # Test failed dangerous spell
    print("\nCasting dangerous void spell (failure):")
    spell_context["recent_casts_count"] = 2
    consequences = consequence_system.apply_spell_consequences(
        void_spell, False, location_id, location_magic_profile, spell_context
    )
    
    if consequences:
        print("Magical consequences applied:")
        for effect in consequences:
            print(f"- {effect.id}: {effect.description}")
            if isinstance(effect.magnitude, list):
                for game_effect in effect.magnitude:
                    if isinstance(game_effect, dict) and "description" in game_effect:
                        print(f"  * {game_effect['description']}")
    else:
        print("No consequences were triggered.")
    
    # Test rapid spellcasting
    print("\nRapid spellcasting (5 spells in quick succession):")
    spell_context["recent_casts_count"] = 5
    consequences = consequence_system.apply_spell_consequences(
        necromancy_spell, True, location_id, location_magic_profile, spell_context
    )
    
    if consequences:
        print("Magical consequences applied:")
        for effect in consequences:
            print(f"- {effect.id}: {effect.description}")
            if isinstance(effect.magnitude, list):
                for game_effect in effect.magnitude:
                    if isinstance(game_effect, dict) and "description" in game_effect:
                        print(f"  * {game_effect['description']}")
    else:
        print("No consequences were triggered.")
    
    # Update active consequences
    print("\nUpdating consequences (passage of time):")
    consequence_system.update_consequences(seconds_elapsed=3600)  # 1 hour
    active_consequences = consequence_system.get_active_consequences(location_id)
    
    if active_consequences:
        print("Active consequences after 1 hour:")
        for effect in active_consequences:
            print(f"- {effect.id}: {effect.description}")
            if effect.duration_seconds:
                print(f"  Time remaining: {effect.duration_seconds // 60} minutes")
    else:
        print("No active consequences remain.")


def test_npc_magic_reactions():
    """Test NPC reactions to magic"""
    print("\n=== Testing NPC Magic Reactions ===")
    
    # Create the NPC magic relationship system
    npc_magic_system = NPCMagicRelationship()
    
    # Create test NPCs
    npcs = [
        NPC(id="temple_priest", name="Brother Lumin", faction="Temple_of_Light", profession="healer"),
        NPC(id="city_guard", name="Guard Captain Vorn", faction="City_Watch", profession="guard"),
        NPC(id="mage_guild", name="Archmage Elira", faction="Mage_Guild", profession="scholar"),
        NPC(id="tribal_shaman", name="Elder Koda", faction="Wilderness_Tribes", profession="healer")
    ]
    
    # Create test spells with different schools
    restoration_spell = Spell(
        id="spell_test_heal",
        name="Divine Healing",
        description="A healing spell that restores health",
        tier=MagicTier.SPIRITUAL_UTILITY,
        magic_source_affinity=[MagicSource.LEYLINE],
        effects=[
            MagicalEffect(
                effect_type=EffectType.HEAL,
                description_template="Healing light surrounds the target",
                magnitude=15,
                target_type=TargetType.SINGLE_ALLY
            )
        ],
        mana_cost=0,
        ley_energy_cost=10,
        casting_time_seconds=3,
        domain_requirements=[],
        backlash_potential=0.05
    )
    setattr(restoration_spell, "school", "RESTORATION")
    
    necromancy_spell = Spell(
        id="spell_test_necro",
        name="Dark Revival",
        description="Raises a corpse as an undead servant",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.SUMMON,
                description_template="A corpse rises as an undead servant",
                magnitude="undead_minion",
                target_type=TargetType.ENVIRONMENT
            )
        ],
        mana_cost=20,
        casting_time_seconds=5,
        domain_requirements=[],
        backlash_potential=0.2
    )
    setattr(necromancy_spell, "school", "NECROMANCY")
    
    evocation_spell = Spell(
        id="spell_test_fireball",
        name="Fireball",
        description="A ball of fire that explodes on impact",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A fiery explosion engulfs the target",
                magnitude=15,
                target_type=TargetType.AREA_ENEMIES,
                damage_type=DamageType.FIRE
            )
        ],
        mana_cost=15,
        casting_time_seconds=2,
        domain_requirements=[],
        backlash_potential=0.1
    )
    setattr(evocation_spell, "school", "EVOCATION")
    
    # Test NPC reactions to different spells
    print("\nNPC Reactions to Different Spells:")
    
    for npc in npcs:
        print(f"\n{npc.name} ({npc.faction}, {npc.profession}):")
        
        # Reaction to healing spell
        reaction = npc_magic_system.get_npc_magic_reaction(npc, restoration_spell, True)
        print(f"- Reaction to healing magic: {reaction.reaction_type}")
        print(f"  \"{reaction.narrative}\"")
        print(f"  Reputation change: {reaction.reputation_change:+d}")
        
        # Reaction to necromancy
        reaction = npc_magic_system.get_npc_magic_reaction(npc, necromancy_spell, True)
        print(f"- Reaction to necromancy: {reaction.reaction_type}")
        print(f"  \"{reaction.narrative}\"")
        print(f"  Reputation change: {reaction.reputation_change:+d}")
        
        # Reaction to combat magic
        reaction = npc_magic_system.get_npc_magic_reaction(npc, evocation_spell, True)
        print(f"- Reaction to evocation magic: {reaction.reaction_type}")
        print(f"  \"{reaction.narrative}\"")
        print(f"  Reputation change: {reaction.reputation_change:+d}")
        
        # Reaction to failed spell
        reaction = npc_magic_system.get_npc_magic_reaction(npc, evocation_spell, False)
        print(f"- Reaction to failed evocation: {reaction.reaction_type}")
        print(f"  \"{reaction.narrative}\"")
        print(f"  Reputation change: {reaction.reputation_change:+d}")


def test_domain_magic_synergy():
    """Test domain-magic synergy system"""
    print("\n=== Testing Domain-Magic Synergy ===")
    
    # Create the domain magic synergy system
    synergy_system = DomainMagicSynergy()
    
    # Create test character domains
    character_domains = {
        Domain.BODY: 2,
        Domain.MIND: 5,  # Mastery
        Domain.CRAFT: 2,
        Domain.AWARENESS: 4,  # High competence
        Domain.SOCIAL: 1,
        Domain.AUTHORITY: 1,
        Domain.SPIRIT: 5,  # Mastery
        Domain.FIRE: 3,  # Competence
        Domain.WATER: 0,
        Domain.EARTH: 0,
        Domain.AIR: 0,
        Domain.LIGHT: 0,
        Domain.DARKNESS: 0
    }
    
    character = {
        "name": "Test Mage",
        "domains": character_domains
    }
    
    # Create test spells with different schools
    divination_spell = Spell(
        id="spell_test_divination",
        name="Farsight",
        description="Allows seeing distant locations",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.SCRY,
                description_template="Your vision extends to a distant location",
                magnitude="scry_location",
                target_type=TargetType.LOCATION
            )
        ],
        mana_cost=10,
        casting_time_seconds=5,
        domain_requirements=[],
        backlash_potential=0.1
    )
    setattr(divination_spell, "school", "DIVINATION")
    
    fire_spell = Spell(
        id="spell_test_fire",
        name="Flame Strike",
        description="A column of fire descends on the target",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A column of fire engulfs the target",
                magnitude=20,
                target_type=TargetType.SINGLE_ENEMY,
                damage_type=DamageType.FIRE
            )
        ],
        mana_cost=15,
        casting_time_seconds=3,
        domain_requirements=[],
        backlash_potential=0.1
    )
    setattr(fire_spell, "school", "EVOCATION")
    
    psychic_spell = Spell(
        id="spell_test_psychic",
        name="Mind Blast",
        description="A blast of psychic energy",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="Psychic energy assaults the target's mind",
                magnitude=15,
                target_type=TargetType.SINGLE_ENEMY,
                damage_type=DamageType.PSYCHIC
            )
        ],
        mana_cost=12,
        casting_time_seconds=2,
        domain_requirements=[],
        backlash_potential=0.1
    )
    setattr(psychic_spell, "school", "MENTALISM")
    
    # Test synergy bonuses
    print("\nTesting Domain Synergy Bonuses:")
    
    spells = [
        ("Divination", divination_spell),
        ("Fire Magic", fire_spell),
        ("Psychic Magic", psychic_spell)
    ]
    
    for spell_name, spell in spells:
        bonus = synergy_system.calculate_synergy_bonus(character, spell)
        
        print(f"\n{spell_name} Synergy Bonus: {bonus:.2f}x")
        descriptions = synergy_system.get_domain_synergy_description(character, spell)
        
        if descriptions:
            print("Synergy descriptions:")
            for desc in descriptions:
                print(f"- {desc}")
        else:
            print("No significant domain synergies.")
        
        # Calculate effective power
        spell_power = 0
        for effect in spell.effects:
            if effect.effect_type == EffectType.DAMAGE and isinstance(effect.magnitude, (int, float)):
                spell_power = effect.magnitude
                break
        
        if spell_power > 0:
            print(f"Base power: {spell_power}, With synergy: {int(spell_power * bonus)}")


def test_tactical_magic_combat():
    """Test tactical magic in combat"""
    print("\n=== Testing Tactical Magic Combat ===")
    
    # Create a magic system
    magic_system = MagicSystem()
    
    # Create the tactical magic combat system
    tactical_system = TacticalMagicCombat(magic_system)
    
    # Create test spells
    fire_spell = Spell(
        id="spell_combat_fire",
        name="Fireball",
        description="A ball of fire that explodes on impact",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.DAMAGE,
                description_template="A fiery explosion engulfs the target",
                magnitude=15,
                target_type=TargetType.AREA_ENEMIES,
                damage_type=DamageType.FIRE
            )
        ],
        mana_cost=15,
        casting_time_seconds=2,
        domain_requirements=[],
        backlash_potential=0.1
    )
    setattr(fire_spell, "school", "EVOCATION")
    
    ice_wall_spell = Spell(
        id="spell_combat_ice_wall",
        name="Wall of Ice",
        description="Creates a wall of solid ice",
        tier=MagicTier.ARCANE_MASTERY,
        magic_source_affinity=[MagicSource.MANA_HEART],
        effects=[
            MagicalEffect(
                effect_type=EffectType.WARD,
                description_template="A wall of ice forms",
                magnitude="ice_barrier",
                target_type=TargetType.ENVIRONMENT,
                damage_type=DamageType.ICE
            )
        ],
        mana_cost=12,
        casting_time_seconds=3,
        domain_requirements=[],
        backlash_potential=0.1
    )
    setattr(ice_wall_spell, "school", "ABJURATION")
    
    # Test in different combat contexts
    test_contexts = [
        {
            "name": "Forest Ambush",
            "context": CombatContext(
                enemy_count=3,
                terrain="forest",
                enemy_casting_magic=False,
                weather_conditions="rain",
                time_of_day="night",
                nearby_leyline_strength=1,
                environment_elements=["trees", "wet_ground"]
            )
        },
        {
            "name": "Magical Duel",
            "context": CombatContext(
                enemy_count=1,
                terrain="magical_circle",
                enemy_casting_magic=True,
                weather_conditions="clear",
                time_of_day="day",
                nearby_leyline_strength=4,
                environment_elements=["ley_crystals", "magical_symbols"]
            )
        },
        {
            "name": "Desert Standoff",
            "context": CombatContext(
                enemy_count=5,
                terrain="desert",
                enemy_casting_magic=False,
                weather_conditions="hot",
                time_of_day="noon",
                nearby_leyline_strength=0,
                environment_elements=["sand", "heat"]
            )
        }
    ]
    
    for test in test_contexts:
        context_name = test["name"]
        context = test["context"]
        
        print(f"\n{context_name} Context:")
        print(f"Enemies: {context.enemy_count}, Terrain: {context.terrain}, Weather: {context.weather_conditions}")
        print(f"Enemy casting magic: {context.enemy_casting_magic}, Leyline strength: {context.nearby_leyline_strength}")
        
        # Create tactical combat moves
        fire_move = tactical_system.create_magical_combat_move(fire_spell, context)
        ice_wall_move = tactical_system.create_magical_combat_move(ice_wall_spell, context)
        
        print("\nTactical Combat Moves:")
        print(f"- {fire_move.name}: {fire_move.description}")
        print(f"  Base Damage: {fire_move.base_damage}")
        print(f"  Effects: {', '.join(fire_move.effects)}")
        
        print(f"- {ice_wall_move.name}: {ice_wall_move.description}")
        print(f"  Effects: {', '.join(ice_wall_move.effects)}")
        
        # Get tactical suggestions
        spells = [fire_spell, ice_wall_spell]
        suggestions = tactical_system.suggest_tactical_spell_use(spells, context)
        
        print("\nTactical Suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion['tactic']}: {suggestion['description']}")
            print(f"  Suggested spells: {', '.join(suggestion['suggested_spells'])}")
        
        # Calculate tactical advantage
        fire_advantage = tactical_system.calculate_tactical_advantage(fire_spell, context)
        ice_advantage = tactical_system.calculate_tactical_advantage(ice_wall_spell, context)
        
        print("\nTactical Advantage:")
        print(f"- {fire_spell.name}: {fire_advantage:.2f}x")
        print(f"- {ice_wall_spell.name}: {ice_advantage:.2f}x")


def test_magical_economy():
    """Test the magical economy system"""
    print("\n=== Testing Magical Economy ===")
    
    # Create the magical economy system
    economy_system = MagicalEconomy()
    
    # Test locations
    test_locations = [
        {
            "name": "Capital City",
            "remoteness": 0.1,
            "settlement_size": 5,
            "has_magical_academy": True,
            "active_mages": 12,
            "region_type": "urban"
        },
        {
            "name": "Remote Mountain Village",
            "remoteness": 0.8,
            "settlement_size": 1,
            "has_magical_academy": False,
            "active_mages": 1,
            "region_type": "mountains"
        },
        {
            "name": "Forest Enclave",
            "remoteness": 0.5,
            "settlement_size": 2,
            "has_magical_academy": True,
            "active_mages": 8,
            "region_type": "forest"
        }
    ]
    
    # Test component prices
    print("\nMagical Component Prices:")
    for location in test_locations:
        prices = economy_system.calculate_component_prices(location)
        
        print(f"\n{location['name']}:")
        print(f"Settlement size: {location['settlement_size']}, Remoteness: {location['remoteness']}")
        print(f"Has magical academy: {location['has_magical_academy']}, Active mages: {location['active_mages']}")
        
        # Display prices for common components
        common_components = ["ley_crystal", "spiritbloom", "crimson_residue", "void_shard", "phoenix_feather"]
        for component in common_components:
            if component in prices:
                print(f"- {component}: {prices[component]} gold")
    
    # Test magical services
    print("\nMagical Services:")
    
    # Test NPCs
    test_npcs = [
        NPC(
            id="archmage", 
            name="Archmage Elorin", 
            faction="Mage_Guild", 
            profession="scholar",
            magic_tier=MagicTier.ARCANE_MASTERY,
            known_schools=["EVOCATION", "ABJURATION", "DIVINATION", "CONJURATION"]
        ),
        NPC(
            id="hedge_wizard", 
            name="Old Miriam", 
            faction="Wilderness_Tribes", 
            profession="healer",
            magic_tier=MagicTier.MANA_INFUSION,
            known_schools=["RESTORATION", "DIVINATION"]
        ),
        NPC(
            id="temple_priest", 
            name="Brother Lumin", 
            faction="Temple_of_Light", 
            profession="healer",
            magic_tier=MagicTier.SPIRITUAL_UTILITY,
            known_schools=["RESTORATION", "ABJURATION"]
        )
    ]
    
    for npc in test_npcs:
        # Pick a location for the NPC
        location = random.choice(test_locations)
        
        print(f"\n{npc.name} ({npc.faction}, {npc.profession}) in {location['name']}:")
        services = economy_system.generate_magical_services(npc, location)
        
        if services:
            print("Offered services:")
            for service in services:
                print(f"- {service.name}: {service.base_cost} gold")
                print(f"  {service.description}")
                
                if service.cost_per_level > 0:
                    print(f"  Cost per level: +{service.cost_per_level} gold")
                
                if service.reputation_requirement > 0:
                    print(f"  Requires reputation: {service.reputation_requirement}+")
        else:
            print("No magical services offered.")


def test_ai_gm_magic_integration():
    """Test AI GM magic integration"""
    print("\n=== Testing AI GM Magic Integration ===")
    
    # Create the AI GM magic integration system
    ai_gm_magic = AIGMMagicIntegration()
    
    # Create a test character with a magic profile
    character, domains = create_test_character()
    magic_system = MagicSystem()
    magic_profile = magic_system.initialize_magic_user(domains)
    
    # Ensure character has a Mana Heart
    if not magic_profile.has_mana_heart:
        magic_system.develop_mana_heart("test_character", magic_profile)
    
    # Test different character profiles
    test_profiles = [
        {
            "name": "Novice Mage",
            "profile": magic_profile
        },
        {
            "name": "Corrupted Mage",
            "profile": MagicUser(
                has_mana_heart=True,
                mana_current=60,
                mana_max=60,
                mana_regeneration_rate=0.8,
                ley_energy_sensitivity=5,
                current_ley_energy=10,
                corruption_level=40,
                attunements=["void_touched"],
                known_skills=["ManaHeartDeveloped", "void_channeling"]
            )
        },
        {
            "name": "Elemental Master",
            "profile": MagicUser(
                has_mana_heart=True,
                mana_current=100,
                mana_max=100,
                mana_regeneration_rate=1.5,
                ley_energy_sensitivity=8,
                current_ley_energy=25,
                corruption_level=5,
                attunements=["elemental_attunement"],
                known_skills=["ManaHeartDeveloped", "elemental_mastery"],
                primary_element="FIRE"
            )
        }
    ]
    
    # Test locations
    test_locations = [
        {
            "name": "Academy Library",
            "leyline_strength": 2,
            "corruption_level": 0,
            "recent_spellcasting": True
        },
        {
            "name": "Ancient Battlefield",
            "leyline_strength": 3,
            "corruption_level": 2,
            "historical_events": ["crimson_dissonance_site"]
        },
        {
            "name": "Corrupted Grove",
            "leyline_strength": 4,
            "corruption_level": 5,
            "leyline_disruption": True
        }
    ]
    
    for profile_data in test_profiles:
        profile_name = profile_data["name"]
        profile = profile_data["profile"]
        
        print(f"\n{profile_name}:")
        
        for location in test_locations:
            location_name = location["name"]
            
            print(f"\nIn {location_name}:")
            
            # Create a base narrative context
            base_context = {
                "character_name": profile_name,
                "location": location,
                "npc_reactions": []
            }
            
            # Enhance with magic
            enhanced_context = ai_gm_magic.enhance_narrative_with_magic(base_context, profile)
            
            # Display enhancements
            if "aura_description" in enhanced_context:
                print(f"Character Aura: {enhanced_context['aura_description']}")
            
            if "elemental_aura_description" in enhanced_context:
                print(f"Elemental Aura: {enhanced_context['elemental_aura_description']}")
            
            if "void_aura_description" in enhanced_context:
                print(f"Void Aura: {enhanced_context['void_aura_description']}")
            
            if "npc_reactions" in enhanced_context and enhanced_context["npc_reactions"]:
                print(f"NPC Reactions: {', '.join(enhanced_context['npc_reactions'])}")
            
            if "environmental_description" in enhanced_context:
                print(f"Environment: {enhanced_context['environmental_description']}")
            
            if "magical_hooks" in enhanced_context and enhanced_context["magical_hooks"]:
                print("Potential Story Hooks:")
                for hook in enhanced_context["magical_hooks"]:
                    print(f"- {hook['description']}")
            
            # Generate a random magical event
            event = ai_gm_magic.generate_magical_event(location, profile)
            if event:
                print(f"\nRandom Magical Event: {event['title']}")
                print(f"Description: {event['description']}")
                print(f"Effects: {', '.join(event['effects'])}")
                print(f"Intensity: {event['intensity']}/5, Duration: {event['duration']}")


def test_async_processing():
    """Test the asynchronous processing with Redis and Celery"""
    print("\n=== Testing Asynchronous Processing with Redis and Celery ===")
    
    # Create required systems
    magic_system = MagicSystem()
    consequence_system = MagicalConsequenceSystem()
    
    try:
        # Create the async processor
        async_processor = create_magic_async_processor(magic_system, consequence_system)
        
        print("Successfully created async processor with Redis and Celery")
        
        # Test location magic processing
        forest_location = create_forest_location()
        corrupted_location = create_corrupted_cave_location()
        
        print("\nProcessing location magic asynchronously:")
        print(f"- {forest_location['name']}")
        print(f"- {corrupted_location['name']}")
        
        # Process the forest location (this would normally be asynchronous)
        result = async_processor.process_location_magic(forest_location['id'], forest_location)
        print(f"\nForest location processing result: {result.get('status', 'completed')}")
        if 'leyline_strength' in result:
            print(f"Leyline Strength: {result['leyline_strength']}/5")
            print(f"Mana Flux Level: {result['mana_flux_level']}/5")
            print(f"Allows Rituals: {result['allows_rituals']}")
        
        # Register a delayed magical effect
        print("\nRegistering a delayed magical effect:")
        effect = Effect(
            id="test_delayed_effect",
            description="A magical residue lingers in the area",
            duration_seconds=3600,  # 1 hour
            magnitude={"type": "ambient", "boost": "ley_sensitivity"}
        )
        effect_id = async_processor.register_delayed_effect(
            effect=effect,
            target_id=forest_location['id'],
            delay_seconds=10,  # 10 seconds delay
            location_id=forest_location['id']
        )
        print(f"Registered delayed effect with ID: {effect_id}")
        
        # Test spell casting async
        print("\nAsynchronous spell casting:")
        cast_result = async_processor.cast_spell_async(
            caster_id="test_character",
            spell_id="spell_test_fireball",
            targets=["enemy_1", "enemy_2"],
            location_id=forest_location['id'],
            context={"battle_round": 1, "tension_level": "high"}
        )
        print(f"Spell cast queued with task ID: {cast_result['task_id']}")
        print(f"Status: {cast_result['status']}")
        
        # In a real implementation, we would check the status later
        
        print("\nAsync processing features are ready to use!")
        
    except Exception as e:
        print(f"Error setting up async processing: {str(e)}")
        print("Redis and Celery integration could not be tested.")
        print("Ensure Redis server is running and Celery is properly configured.")


def main():
    """Run all test functions for the advanced magic system"""
    print("=== Advanced Magic System Integration Test ===")
    
    # Test environmental magic resonance
    test_environmental_resonance()
    
    # Test mana heart evolution
    test_mana_heart_evolution()
    
    # Test spell combination
    test_spell_combination()
    
    # Test spell crafting
    test_spell_crafting()
    
    # Test magical consequences
    test_magical_consequences()
    
    # Test NPC magic reactions
    test_npc_magic_reactions()
    
    # Test domain-magic synergy
    test_domain_magic_synergy()
    
    # Test tactical magic combat
    test_tactical_magic_combat()
    
    # Test magical economy
    test_magical_economy()
    
    # Test AI GM magic integration
    test_ai_gm_magic_integration()
    
    # Test async processing with Redis and Celery
    test_async_processing()
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    main()