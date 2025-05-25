"""
Advanced Magic Features

This module implements advanced features for the magic system including:
- Environmental magic resonance
- Mana heart evolution
- Spell combination
- Spell crafting and customization
- Magical consequences
- NPC magic relationships
- Domain-magic synergy
- Combat magic tactics
- Magical economy
- AI GM magic integration
"""

import random
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from enum import Enum, auto
from dataclasses import dataclass, field

from .magic_system import (
    MagicSystem, MagicUser, Spell, Ritual, Enchantment,
    MagicTier, MagicSource, EffectType, TargetType, DomainRequirement,
    Domain, DamageType, MagicalEffect, ItemMagicProfile, Status
)
from .enhanced_combat.combat_system_core import (
    Combatant, CombatMove, MoveType
)


# ======================================================================
# Magic Schools & Specializations
# ======================================================================

class MagicSchool(Enum):
    """Schools of magic representing different approaches and philosophies"""
    EVOCATION = auto()      # Offensive energy manipulation (fire, lightning)
    ABJURATION = auto()     # Protection and defense
    CONJURATION = auto()    # Summoning and creation
    TRANSMUTATION = auto()  # Changing properties of objects and creatures
    DIVINATION = auto()     # Gaining knowledge and predicting the future
    ENCHANTMENT = auto()    # Affecting minds and enhancing objects
    ILLUSION = auto()       # Creating false sensory impressions
    NECROMANCY = auto()     # Death magic and manipulation of life force
    RESTORATION = auto()    # Healing and repairing
    MENTALISM = auto()      # Mind-affecting magic


class ManaHeartStage(Enum):
    """Stages of Mana Heart development"""
    NASCENT = auto()       # Newly formed, unstable
    DEVELOPING = auto()    # Growing in power and stability
    MATURE = auto()        # Fully developed, reliable
    REFINED = auto()       # Enhanced through special training
    TRANSCENDENT = auto()  # Rare evolution beyond normal limits


class MagicalAffinity(Enum):
    """Special magical affinities a caster can develop"""
    ELEMENTAL_MASTER = auto()  # Enhanced elemental magic
    VOID_TOUCHED = auto()      # Connection to dangerous void energies
    HARMONY_SEEKER = auto()    # Balanced approach with domain synergy
    WILD_MAGIC = auto()        # Unpredictable but potentially powerful
    BLOOD_MAGIC = auto()       # Life force manipulation
    RUNE_MASTER = auto()       # Expertise with magical inscriptions
    SPIRIT_SPEAKER = auto()    # Communication with spiritual entities
    LEY_WEAVER = auto()        # Manipulation of leyline energies


@dataclass
class SpellModifier:
    """Modifiers that can be applied to spells"""
    id: str
    name: str
    type: str  # "extended_duration", "area_expansion", etc.
    description: str
    mana_cost_modifier: float = 1.0
    ley_energy_cost_modifier: float = 1.0
    casting_time_modifier: float = 1.0
    effect_magnitude_modifier: float = 1.0
    range_modifier: float = 1.0
    duration_modifier: float = 1.0
    domain_requirements: List[DomainRequirement] = field(default_factory=list)


@dataclass
class CombinedSpell:
    """A spell created by combining two or more spells"""
    name: str
    description: str = "A combined magical effect"
    damage_multiplier: float = 1.0
    base_power: int = 0
    area_effect: bool = False
    blind_chance: float = 0.0
    crit_chance: float = 0.0
    stamina_recovery: int = 0
    mana_cost: int = 0
    ley_energy_cost: int = 0
    component_spell_ids: List[str] = field(default_factory=list)
    

@dataclass
class MagicalService:
    """A magical service offered by an NPC mage"""
    id: str
    name: str
    description: str
    base_cost: int
    cost_per_level: int = 0
    reputation_requirement: int = 0
    domain_requirements: List[DomainRequirement] = field(default_factory=list)


@dataclass
class Effect:
    """A magical effect or consequence"""
    id: str
    description: str
    duration_seconds: Optional[int] = None
    magnitude: Any = None


@dataclass
class ReactionResult:
    """An NPC's reaction to magic use"""
    reaction_type: str  # "impressed", "horrified", "curious", etc.
    narrative: str
    reputation_change: int = 0


@dataclass
class CombatContext:
    """Context information for combat magic integration"""
    enemy_count: int = 1
    terrain: str = "neutral"
    enemy_casting_magic: bool = False
    weather_conditions: str = "clear"
    time_of_day: str = "day"
    nearby_leyline_strength: int = 0
    environment_elements: List[str] = field(default_factory=list)


@dataclass
class NPC:
    """Simple NPC representation for magic interactions"""
    id: str
    name: str
    faction: str = "neutral"
    profession: str = "commoner"
    magic_tier: MagicTier = MagicTier.SPIRITUAL_UTILITY
    known_schools: List[MagicSchool] = field(default_factory=list)
    magical_services: List[MagicalService] = field(default_factory=list)
    attitude_toward_magic: str = "neutral"  # "fearful", "respectful", "hostile", etc.
    reputation: int = 0


# ======================================================================
# 1. Environmental Magic Resonance
# ======================================================================

class EnvironmentalMagicResonance:
    """
    Dynamic magic that responds to world conditions.
    
    This system modifies spell effectiveness based on:
    - Time of day
    - Weather conditions
    - Environmental elements
    - Historical events
    - Emotional resonance
    """
    
    def __init__(self):
        """Initialize the environmental magic resonance system"""
        # Define resonance maps for different spell types
        self.resonance_map = {
            # Time of day resonances
            "time": {
                "dawn": {
                    MagicSchool.DIVINATION: 0.3,
                    MagicSchool.RESTORATION: 0.2,
                    DamageType.LIGHT: 0.2
                },
                "noon": {
                    MagicSchool.EVOCATION: 0.2,
                    DamageType.FIRE: 0.3,
                    DamageType.LIGHT: 0.3
                },
                "dusk": {
                    MagicSchool.ILLUSION: 0.3,
                    MagicSchool.ENCHANTMENT: 0.2,
                    DamageType.DARKNESS: 0.2
                },
                "night": {
                    MagicSchool.NECROMANCY: 0.3,
                    DamageType.DARKNESS: 0.4,
                    MagicSchool.DIVINATION: -0.1
                },
                "midnight": {
                    MagicSchool.NECROMANCY: 0.5,
                    DamageType.DARKNESS: 0.5,
                    DamageType.LIGHT: -0.3
                }
            },
            
            # Weather resonances
            "weather": {
                "clear": {
                    DamageType.LIGHT: 0.2,
                    MagicSchool.DIVINATION: 0.1
                },
                "cloudy": {
                    DamageType.AIR: 0.1,
                    DamageType.LIGHT: -0.1
                },
                "rain": {
                    DamageType.WATER: 0.4,
                    DamageType.LIGHTNING: 0.2,
                    DamageType.FIRE: -0.3
                },
                "storm": {
                    DamageType.LIGHTNING: 0.5,
                    DamageType.AIR: 0.3,
                    DamageType.WATER: 0.2,
                    MagicSchool.EVOCATION: 0.2
                },
                "fog": {
                    MagicSchool.ILLUSION: 0.4,
                    DamageType.WATER: 0.2,
                    MagicSchool.DIVINATION: -0.3
                },
                "snow": {
                    DamageType.ICE: 0.5,
                    DamageType.WATER: 0.2,
                    DamageType.FIRE: -0.2
                }
            },
            
            # Environmental elements
            "environment": {
                "forest": {
                    DamageType.EARTH: 0.3,
                    MagicSource.LEYLINE: 0.2
                },
                "mountain": {
                    DamageType.EARTH: 0.4,
                    DamageType.AIR: 0.2
                },
                "cave": {
                    DamageType.EARTH: 0.3,
                    DamageType.DARKNESS: 0.3,
                    MagicSchool.DIVINATION: -0.2
                },
                "desert": {
                    DamageType.FIRE: 0.3,
                    DamageType.EARTH: 0.2,
                    DamageType.WATER: -0.3
                },
                "ocean": {
                    DamageType.WATER: 0.5,
                    DamageType.FIRE: -0.4
                },
                "volcano": {
                    DamageType.FIRE: 0.6,
                    DamageType.EARTH: 0.3,
                    DamageType.ICE: -0.5
                },
                "graveyard": {
                    MagicSchool.NECROMANCY: 0.5,
                    DamageType.NECROTIC: 0.4,
                    MagicSchool.RESTORATION: -0.2
                },
                "battlefield": {
                    MagicSchool.NECROMANCY: 0.3,
                    DamageType.NECROTIC: 0.2,
                    MagicSchool.EVOCATION: 0.2
                },
                "temple": {
                    MagicSchool.RESTORATION: 0.3,
                    MagicSchool.DIVINATION: 0.3,
                    MagicSchool.NECROMANCY: -0.3
                },
                "leyline_nexus": {
                    MagicSource.LEYLINE: 0.5,
                    "all_magic": 0.2
                }
            },
            
            # Historical events
            "history": {
                "crimson_dissonance_site": {
                    DamageType.FIRE: 0.4,
                    MagicSchool.EVOCATION: 0.3,
                    "corruption_chance": 0.2
                },
                "ancient_ritual_site": {
                    MagicSchool.CONJURATION: 0.3,
                    MagicTier.ARCANE_MASTERY: 0.2
                },
                "magical_disaster": {
                    "backlash_chance": 0.3,
                    "wild_magic_chance": 0.4
                }
            },
            
            # Emotional resonance
            "emotion": {
                "fear": {
                    MagicSchool.ILLUSION: 0.3,
                    MagicSchool.ENCHANTMENT: 0.2
                },
                "joy": {
                    MagicSchool.RESTORATION: 0.3,
                    DamageType.LIGHT: 0.2
                },
                "hatred": {
                    MagicSchool.NECROMANCY: 0.3,
                    DamageType.NECROTIC: 0.2
                },
                "love": {
                    MagicSchool.RESTORATION: 0.4,
                    MagicSchool.ENCHANTMENT: 0.3
                },
                "grief": {
                    MagicSchool.NECROMANCY: 0.3,
                    MagicSchool.CONJURATION: 0.2
                }
            }
        }
    
    def calculate_spell_power_modifier(self, spell: Spell, location: Dict[str, Any]) -> float:
        """
        Calculate a power modifier for a spell based on environmental conditions.
        
        Args:
            spell: The spell being cast
            location: Information about the location
            
        Returns:
            A modifier to spell power (1.0 is baseline)
        """
        modifier = 1.0
        
        # Get spell characteristics
        spell_school = getattr(spell, "school", None)
        spell_damage_type = None
        for effect in spell.effects:
            if effect.damage_type:
                spell_damage_type = effect.damage_type
                break
        
        # Check time of day
        time_of_day = location.get("time", "day")
        if time_of_day in self.resonance_map["time"]:
            time_resonance = self.resonance_map["time"][time_of_day]
            
            # Apply school-based modifier
            if spell_school and spell_school in time_resonance:
                modifier += time_resonance[spell_school]
            
            # Apply damage-type modifier
            if spell_damage_type and spell_damage_type in time_resonance:
                modifier += time_resonance[spell_damage_type]
        
        # Check weather
        weather = location.get("weather", "clear")
        if weather in self.resonance_map["weather"]:
            weather_resonance = self.resonance_map["weather"][weather]
            
            # Apply school-based modifier
            if spell_school and spell_school in weather_resonance:
                modifier += weather_resonance[spell_school]
            
            # Apply damage-type modifier
            if spell_damage_type and spell_damage_type in weather_resonance:
                modifier += weather_resonance[spell_damage_type]
        
        # Check environment type
        environment = location.get("environment_type", "")
        if environment in self.resonance_map["environment"]:
            env_resonance = self.resonance_map["environment"][environment]
            
            # Apply school-based modifier
            if spell_school and spell_school in env_resonance:
                modifier += env_resonance[spell_school]
            
            # Apply damage-type modifier
            if spell_damage_type and spell_damage_type in env_resonance:
                modifier += env_resonance[spell_damage_type]
            
            # Apply magic source modifier
            for source in spell.magic_source_affinity:
                if source in env_resonance:
                    modifier += env_resonance[source]
            
            # Apply general magic modifier
            if "all_magic" in env_resonance:
                modifier += env_resonance["all_magic"]
        
        # Check historical events
        for event_type, event_data in self.resonance_map["history"].items():
            if location.get(event_type, False) or event_type in location.get("historical_events", []):
                # Apply school-based modifier
                if spell_school and spell_school in event_data:
                    modifier += event_data[spell_school]
                
                # Apply damage-type modifier
                if spell_damage_type and spell_damage_type in event_data:
                    modifier += event_data[spell_damage_type]
                
                # Apply tier-based modifier
                if spell.tier in event_data:
                    modifier += event_data[spell.tier]
        
        # Check emotional resonance
        for emotion, emotion_data in self.resonance_map["emotion"].items():
            if emotion in location.get("emotional_aura", []):
                # Apply school-based modifier
                if spell_school and spell_school in emotion_data:
                    modifier += emotion_data[spell_school]
                
                # Apply damage-type modifier
                if spell_damage_type and spell_damage_type in emotion_data:
                    modifier += emotion_data[spell_damage_type]
        
        # Ensure the modifier doesn't go below a minimum threshold
        return max(0.5, modifier)
    
    def get_backlash_chance_modifier(self, spell: Spell, location: Dict[str, Any]) -> float:
        """
        Calculate a modifier to backlash chance based on environmental conditions.
        
        Args:
            spell: The spell being cast
            location: Information about the location
            
        Returns:
            A modifier to backlash chance (0.0 is no change)
        """
        modifier = 0.0
        
        # Unstable magical areas increase backlash chance
        if location.get("magical_stability", 1.0) < 0.5:
            modifier += 0.2
        
        # Historical magical disasters increase backlash chance
        if "magical_disaster" in location.get("historical_events", []):
            modifier += 0.3
        
        # Proximity to leyline nexus can make magic unpredictable
        if location.get("leyline_strength", 0) >= 4:
            modifier += 0.1
        
        # Corrupted areas increase backlash for pure magic
        if location.get("corruption_level", 0) >= 3:
            spell_school = getattr(spell, "school", None)
            if spell_school in [MagicSchool.RESTORATION, MagicSchool.DIVINATION]:
                modifier += 0.2
        
        return modifier
    
    def get_environmental_magic_effects(self, location: Dict[str, Any]) -> List[Effect]:
        """
        Generate random magical effects that might occur in a location due to environmental factors.
        
        Args:
            location: Information about the location
            
        Returns:
            A list of magical effects
        """
        effects = []
        
        # Leyline surges in areas with strong leylines
        if location.get("leyline_strength", 0) >= 4 and random.random() < 0.3:
            effects.append(Effect(
                id="leyline_surge",
                description="The leylines pulse with energy, temporarily boosting magical power",
                duration_seconds=600,  # 10 minutes
                magnitude=0.2  # 20% boost to spell power
            ))
        
        # Magical echoes in historically significant locations
        if "crimson_dissonance_site" in location.get("historical_events", []) and random.random() < 0.4:
            effects.append(Effect(
                id="war_magic_echo",
                description="Echoes of war magic from the Crimson Dissonance linger, empowering destructive spells",
                duration_seconds=300,  # 5 minutes
                magnitude={"damage_bonus": 0.3}
            ))
        
        # Reality distortions in corrupted areas
        if location.get("corruption_level", 0) >= 4 and random.random() < 0.3:
            effects.append(Effect(
                id="reality_distortion",
                description="Reality warps and bends, causing spells to have unpredictable effects",
                duration_seconds=900,  # 15 minutes
                magnitude={"unpredictability": 0.5}
            ))
        
        # Elemental manifestations in strongly-aligned areas
        if location.get("environment_type") in ["volcano", "ocean", "storm"] and random.random() < 0.5:
            element_map = {
                "volcano": ("fire_manifestation", "Fire", DamageType.FIRE),
                "ocean": ("water_manifestation", "Water", DamageType.WATER),
                "storm": ("lightning_manifestation", "Lightning", DamageType.LIGHTNING)
            }
            
            element_id, element_name, element_type = element_map[location.get("environment_type")]
            effects.append(Effect(
                id=element_id,
                description=f"The ambient {element_name} energy coalesces into a temporary elemental manifestation",
                duration_seconds=120,  # 2 minutes
                magnitude={"element": element_type, "power": random.randint(1, 3)}
            ))
        
        return effects


# ======================================================================
# 2. Mana Heart Evolution System
# ======================================================================

class ManaHeartEvolution:
    """
    System for evolving and specializing a character's Mana Heart.
    
    This creates unique magical identities and progression paths for characters.
    """
    
    def __init__(self):
        """Initialize the mana heart evolution system"""
        # Define evolution paths
        self.evolution_paths = {
            "elemental_attunement": {
                "name": "Elemental Attunement",
                "description": "Develop a strong connection to elemental magic",
                "requirements": {
                    "domains": [
                        DomainRequirement(domain=Domain.SPIRIT, minimum_value=3),
                        DomainRequirement(domain=Domain.FIRE, minimum_value=3)
                    ],
                    "mana_heart_stage": ManaHeartStage.DEVELOPING,
                    "min_spells_known": 3
                },
                "bonuses": {
                    "elemental_damage": 0.3,
                    "elemental_resistance": 0.2,
                    "elemental_cost_reduction": 0.15
                },
                "abilities": ["elemental_mastery", "element_shift", "elemental_harmony"]
            },
            
            "void_touched": {
                "name": "Void Touched",
                "description": "Tap into dangerous void energies for power",
                "requirements": {
                    "domains": [
                        DomainRequirement(domain=Domain.MIND, minimum_value=4),
                        DomainRequirement(domain=Domain.DARKNESS, minimum_value=3)
                    ],
                    "mana_heart_stage": ManaHeartStage.DEVELOPING,
                    "corruption_threshold": 20
                },
                "bonuses": {
                    "spell_power": 0.4,
                    "void_resistance": 0.3,
                    "corruption_threshold": -10  # More susceptible to corruption
                },
                "abilities": ["void_channeling", "entropy_manipulation", "dimensional_shift"]
            },
            
            "harmony_seeker": {
                "name": "Harmony Seeker",
                "description": "Balance magical forces for stability and synergy",
                "requirements": {
                    "domains": [
                        DomainRequirement(domain=Domain.SPIRIT, minimum_value=4),
                        DomainRequirement(domain=Domain.MIND, minimum_value=3)
                    ],
                    "mana_heart_stage": ManaHeartStage.DEVELOPING,
                    "corruption_below": 10
                },
                "bonuses": {
                    "domain_synergy": 0.25,
                    "mana_efficiency": 0.2,
                    "backlash_resistance": 0.3
                },
                "abilities": ["domain_harmony", "balanced_casting", "purification"]
            },
            
            "wild_magic": {
                "name": "Wild Magic Conduit",
                "description": "Embrace chaotic magical energies for unpredictable power",
                "requirements": {
                    "domains": [
                        DomainRequirement(domain=Domain.SPIRIT, minimum_value=5)
                    ],
                    "mana_heart_stage": ManaHeartStage.MATURE,
                    "spells_backfired": 5  # Must have experienced backlash
                },
                "bonuses": {
                    "random_power_boost": 0.5,  # Can randomly boost spell power
                    "spell_cost_randomization": 0.3,  # Costs can be higher or lower
                    "wild_surge_chance": 0.2  # Chance for additional effects
                },
                "abilities": ["chaos_manipulation", "wild_surge", "probability_twist"]
            },
            
            "rune_master": {
                "name": "Rune Master",
                "description": "Develop expertise in magical inscriptions and symbols",
                "requirements": {
                    "domains": [
                        DomainRequirement(domain=Domain.CRAFT, minimum_value=4),
                        DomainRequirement(domain=Domain.MIND, minimum_value=3)
                    ],
                    "mana_heart_stage": ManaHeartStage.DEVELOPING,
                    "known_runes": 5
                },
                "bonuses": {
                    "rune_power": 0.3,
                    "inscription_speed": 0.4,
                    "rune_duration": 0.5
                },
                "abilities": ["living_runes", "instant_inscription", "rune_combination"]
            }
        }
    
    def get_available_evolution_paths(self, magic_profile: MagicUser, character_domains: Dict[Domain, int], 
                                      additional_stats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Get evolution paths available to a character based on their profile.
        
        Args:
            magic_profile: The character's magic profile
            character_domains: The character's domain values
            additional_stats: Additional character statistics
            
        Returns:
            Dictionary of available evolution paths with requirements met/not met
        """
        available_paths = {}
        
        for path_id, path_data in self.evolution_paths.items():
            # Skip if already on this path
            if path_id in magic_profile.attunements:
                continue
            
            requirements_met = True
            unmet_requirements = []
            
            # Check domain requirements
            for domain_req in path_data.get("requirements", {}).get("domains", []):
                domain_value = character_domains.get(domain_req.domain, 0)
                if domain_value < domain_req.minimum_value:
                    requirements_met = False
                    unmet_requirements.append(f"{domain_req.domain.name} {domain_value}/{domain_req.minimum_value}")
            
            # Check mana heart stage
            required_stage = path_data.get("requirements", {}).get("mana_heart_stage")
            if required_stage:
                current_stage = additional_stats.get("mana_heart_stage", ManaHeartStage.NASCENT)
                if current_stage.value < required_stage.value:
                    requirements_met = False
                    unmet_requirements.append(f"Mana Heart Stage: {current_stage.name}/{required_stage.name}")
            
            # Check minimum spells known
            min_spells = path_data.get("requirements", {}).get("min_spells_known", 0)
            if min_spells > 0 and len(magic_profile.known_spells) < min_spells:
                requirements_met = False
                unmet_requirements.append(f"Spells Known: {len(magic_profile.known_spells)}/{min_spells}")
            
            # Check corruption threshold
            corruption_threshold = path_data.get("requirements", {}).get("corruption_threshold")
            if corruption_threshold is not None and magic_profile.corruption_level < corruption_threshold:
                requirements_met = False
                unmet_requirements.append(f"Corruption Level: {magic_profile.corruption_level}/{corruption_threshold}")
            
            # Check corruption below threshold
            corruption_below = path_data.get("requirements", {}).get("corruption_below")
            if corruption_below is not None and magic_profile.corruption_level >= corruption_below:
                requirements_met = False
                unmet_requirements.append(f"Corruption Level: {magic_profile.corruption_level} (must be below {corruption_below})")
            
            # Check number of known runes
            known_runes = path_data.get("requirements", {}).get("known_runes", 0)
            if known_runes > 0:
                character_runes = additional_stats.get("known_runes", 0)
                if character_runes < known_runes:
                    requirements_met = False
                    unmet_requirements.append(f"Known Runes: {character_runes}/{known_runes}")
            
            # Check spells backfired
            spells_backfired = path_data.get("requirements", {}).get("spells_backfired", 0)
            if spells_backfired > 0:
                character_backfires = additional_stats.get("spells_backfired", 0)
                if character_backfires < spells_backfired:
                    requirements_met = False
                    unmet_requirements.append(f"Spells Backfired: {character_backfires}/{spells_backfired}")
            
            # Add to available paths
            available_paths[path_id] = {
                "name": path_data["name"],
                "description": path_data["description"],
                "requirements_met": requirements_met,
                "unmet_requirements": unmet_requirements if not requirements_met else []
            }
        
        return available_paths
    
    def evolve_mana_heart(self, magic_profile: MagicUser, path_id: str, 
                         character_domains: Dict[Domain, int], 
                         additional_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolve a character's Mana Heart along a specific path.
        
        Args:
            magic_profile: The character's magic profile
            path_id: The evolution path to follow
            character_domains: The character's domain values
            additional_stats: Additional character statistics
            
        Returns:
            Result of the evolution attempt
        """
        # Check if path exists
        if path_id not in self.evolution_paths:
            return {
                "success": False,
                "message": f"Evolution path '{path_id}' does not exist"
            }
        
        path_data = self.evolution_paths[path_id]
        
        # Check if already on this path
        if path_id in magic_profile.attunements:
            return {
                "success": False,
                "message": f"Already evolved along the {path_data['name']} path"
            }
        
        # Check requirements
        available_paths = self.get_available_evolution_paths(magic_profile, character_domains, additional_stats)
        path_info = available_paths.get(path_id, {})
        
        if not path_info.get("requirements_met", False):
            return {
                "success": False,
                "message": f"Requirements not met for {path_data['name']} path",
                "unmet_requirements": path_info.get("unmet_requirements", [])
            }
        
        # Apply evolution effects
        
        # Add to attunements
        magic_profile.attunements.append(path_id)
        
        # Add special abilities
        for ability in path_data.get("abilities", []):
            if ability not in magic_profile.known_skills:
                magic_profile.known_skills.append(ability)
        
        # Apply bonuses to profile
        evolution_result = {
            "success": True,
            "message": f"Successfully evolved Mana Heart along the {path_data['name']} path",
            "new_abilities": path_data.get("abilities", []),
            "bonuses": path_data.get("bonuses", {}),
            "path": path_data["name"]
        }
        
        # Add specific path effects
        if path_id == "elemental_attunement":
            # Choose a primary element if not already chosen
            if "primary_element" not in additional_stats:
                element_domains = [d for d in character_domains.keys() 
                                  if d in [Domain.FIRE, Domain.WATER, Domain.EARTH, 
                                          Domain.AIR, Domain.ICE, Domain.LIGHTNING]]
                if element_domains:
                    # Choose the highest element domain
                    primary_element = max(element_domains, key=lambda d: character_domains[d])
                    evolution_result["primary_element"] = primary_element.name
                else:
                    # Default to fire if no element domains
                    evolution_result["primary_element"] = "FIRE"
            
            # Increase mana regeneration for elemental spells
            magic_profile.mana_regeneration_rate *= 1.2
            evolution_result["mana_regen_increase"] = "20%"
        
        elif path_id == "void_touched":
            # Increase max mana but with corruption risk
            original_max = magic_profile.mana_max
            magic_profile.mana_max = int(magic_profile.mana_max * 1.5)
            evolution_result["max_mana_increase"] = f"{magic_profile.mana_max - original_max}"
            
            # Fill to new maximum
            magic_profile.mana_current = magic_profile.mana_max
            
            # Increase corruption threshold
            evolution_result["corruption_warning"] = "Your connection to void energies makes you more susceptible to corruption"
        
        elif path_id == "harmony_seeker":
            # Better mana efficiency
            evolution_result["mana_efficiency"] = "Spells cost 20% less mana"
            
            # Increase resistance to corruption
            evolution_result["corruption_resistance"] = "30% more resistant to corruption"
            
            # Balanced growth across domains
            evolution_result["domain_synergy"] = "25% bonus when using multiple domains"
        
        elif path_id == "wild_magic":
            evolution_result["wild_magic_warning"] = "Your spells may have unpredictable effects"
            evolution_result["wild_surge"] = "20% chance for additional magical effects when casting"
            evolution_result["power_flux"] = "Spells may be up to 50% more powerful or 25% weaker"
        
        elif path_id == "rune_master":
            evolution_result["rune_mastery"] = "30% more powerful runes"
            evolution_result["inscription_speed"] = "40% faster rune inscription"
            evolution_result["rune_duration"] = "50% longer rune duration"
        
        # Advance Mana Heart stage
        current_stage = additional_stats.get("mana_heart_stage", ManaHeartStage.NASCENT)
        new_stage = ManaHeartStage(min(current_stage.value + 1, ManaHeartStage.TRANSCENDENT.value))
        evolution_result["mana_heart_stage"] = {
            "previous": current_stage.name,
            "new": new_stage.name
        }
        
        # Return the result
        return evolution_result


# ======================================================================
# 3. Spell Combination System
# ======================================================================

class SpellCombinationSystem:
    """
    System for combining spells to create unique effects.
    
    This allows for creative spell use and emergent gameplay possibilities.
    """
    
    def __init__(self, magic_system):
        """
        Initialize the spell combination system.
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
        
        # Define combination rules
        self.combination_rules = [
            # Fire + Ice = Steam Explosion
            {
                "components": [
                    {"damage_type": DamageType.FIRE},
                    {"damage_type": DamageType.ICE}
                ],
                "result": {
                    "name": "Steam Explosion",
                    "description": "Creates a violent burst of scalding steam",
                    "damage_multiplier": 1.3,
                    "area_effect": True,
                    "blind_chance": 0.3,
                    "base_power": 15,
                    "mana_cost_multiplier": 1.2
                }
            },
            
            # Enhancement + Damage = Empowered Attack
            {
                "components": [
                    {"effect_type": EffectType.BUFF_STAT},
                    {"effect_type": EffectType.DAMAGE}
                ],
                "result": {
                    "name": "Empowered Strike",
                    "description": "Channels enhancement magic into a devastating attack",
                    "damage_multiplier": 1.5,
                    "crit_chance": 0.2,
                    "stamina_recovery": 10,
                    "mana_cost_multiplier": 1.3
                }
            },
            
            # Fire + Lightning = Plasma Arc
            {
                "components": [
                    {"damage_type": DamageType.FIRE},
                    {"damage_type": DamageType.LIGHTNING}
                ],
                "result": {
                    "name": "Plasma Arc",
                    "description": "Creates a searing arc of superheated plasma",
                    "damage_multiplier": 1.6,
                    "chain_targets": True,
                    "armor_penetration": 0.3,
                    "mana_cost_multiplier": 1.5
                }
            },
            
            # Heal + Protection = Regenerative Barrier
            {
                "components": [
                    {"effect_type": EffectType.HEAL},
                    {"effect_type": EffectType.WARD}
                ],
                "result": {
                    "name": "Regenerative Barrier",
                    "description": "Creates a protective barrier that slowly heals the target",
                    "ward_strength_multiplier": 1.2,
                    "healing_over_time": True,
                    "duration_multiplier": 1.5,
                    "mana_cost_multiplier": 1.4
                }
            },
            
            # Earth + Air = Dust Storm
            {
                "components": [
                    {"damage_type": DamageType.EARTH},
                    {"damage_type": DamageType.AIR}
                ],
                "result": {
                    "name": "Dust Storm",
                    "description": "Creates a blinding storm of swirling dust and debris",
                    "damage_multiplier": 1.2,
                    "area_effect": True,
                    "visibility_reduction": 0.7,
                    "movement_penalty": 0.5,
                    "mana_cost_multiplier": 1.3
                }
            },
            
            # Light + Darkness = Twilight Veil
            {
                "components": [
                    {"damage_type": DamageType.LIGHT},
                    {"damage_type": DamageType.DARKNESS}
                ],
                "result": {
                    "name": "Twilight Veil",
                    "description": "Creates a shifting veil of light and shadow that confuses and disorients",
                    "damage_multiplier": 1.0,
                    "confusion_chance": 0.4,
                    "illusion_strength": 0.6,
                    "stealth_bonus": 0.5,
                    "mana_cost_multiplier": 1.6
                }
            }
        ]
    
    def can_combine_spells(self, primary_spell_id: str, secondary_spell_id: str, 
                          caster_profile: MagicUser) -> Tuple[bool, str]:
        """
        Check if two spells can be combined.
        
        Args:
            primary_spell_id: ID of the primary spell
            secondary_spell_id: ID of the secondary spell
            caster_profile: Magic profile of the caster
            
        Returns:
            Tuple of (can_combine, reason)
        """
        # Get the spells
        primary_spell = self.magic_system.casting_service.get_spell(primary_spell_id)
        secondary_spell = self.magic_system.casting_service.get_spell(secondary_spell_id)
        
        if not primary_spell or not secondary_spell:
            return False, "One or both spells do not exist"
        
        # Check if the caster knows both spells
        if primary_spell_id not in caster_profile.known_spells:
            return False, f"You don't know the spell {primary_spell.name}"
        
        if secondary_spell_id not in caster_profile.known_spells:
            return False, f"You don't know the spell {secondary_spell.name}"
        
        # Check if the spells can be cast
        can_cast_primary, reason = self.magic_system.casting_service.can_cast_spell(caster_profile, primary_spell_id)
        if not can_cast_primary:
            return False, f"Cannot cast primary spell: {reason}"
        
        can_cast_secondary, reason = self.magic_system.casting_service.can_cast_spell(caster_profile, secondary_spell_id)
        if not can_cast_secondary:
            return False, f"Cannot cast secondary spell: {reason}"
        
        # Check if there's a valid combination rule
        has_valid_rule = False
        for rule in self.combination_rules:
            if self._check_combination_rule(primary_spell, secondary_spell, rule):
                has_valid_rule = True
                break
        
        if not has_valid_rule:
            return False, "These spells cannot be combined"
        
        # Check if the caster has the skill to combine spells
        if "spell_combination" not in caster_profile.known_skills:
            # Check if they meet the minimum requirements
            if not caster_profile.has_mana_heart:
                return False, "You need a Mana Heart to combine spells"
            
            if len(caster_profile.known_spells) < 5:
                return False, "You need to know more spells before learning spell combination"
            
            # They meet minimum requirements - they can learn it now
            return False, "You have the potential to learn spell combination (add 'spell_combination' to skills)"
        
        return True, "Spells can be combined"
    
    def combine_spells(self, primary_spell_id: str, secondary_spell_id: str, 
                      caster_profile: MagicUser) -> Dict[str, Any]:
        """
        Combine two spells to create a new effect.
        
        Args:
            primary_spell_id: ID of the primary spell
            secondary_spell_id: ID of the secondary spell
            caster_profile: Magic profile of the caster
            
        Returns:
            Result of the combination attempt
        """
        # Check if the spells can be combined
        can_combine, reason = self.can_combine_spells(primary_spell_id, secondary_spell_id, caster_profile)
        if not can_combine:
            return {
                "success": False,
                "message": reason
            }
        
        # Get the spells
        primary_spell = self.magic_system.casting_service.get_spell(primary_spell_id)
        secondary_spell = self.magic_system.casting_service.get_spell(secondary_spell_id)
        
        # Find the matching rule
        matching_rule = None
        for rule in self.combination_rules:
            if self._check_combination_rule(primary_spell, secondary_spell, rule):
                matching_rule = rule
                break
        
        if not matching_rule:
            return {
                "success": False,
                "message": "No valid combination rule found"
            }
        
        # Calculate the combined spell cost
        primary_mana_cost = primary_spell.mana_cost or 0
        secondary_mana_cost = secondary_spell.mana_cost or 0
        primary_ley_cost = primary_spell.ley_energy_cost or 0
        secondary_ley_cost = secondary_spell.ley_energy_cost or 0
        
        mana_cost_multiplier = matching_rule["result"].get("mana_cost_multiplier", 1.0)
        total_mana_cost = int((primary_mana_cost + secondary_mana_cost) * mana_cost_multiplier)
        total_ley_cost = int((primary_ley_cost + secondary_ley_cost) * mana_cost_multiplier)
        
        # Check if the caster has enough resources
        if caster_profile.has_mana_heart and caster_profile.mana_current < total_mana_cost:
            return {
                "success": False,
                "message": f"Insufficient mana ({caster_profile.mana_current}/{total_mana_cost})"
            }
        
        if caster_profile.current_ley_energy < total_ley_cost:
            return {
                "success": False,
                "message": f"Insufficient ley energy ({caster_profile.current_ley_energy}/{total_ley_cost})"
            }
        
        # Consume resources
        if total_mana_cost > 0:
            caster_profile.use_mana(total_mana_cost)
        
        if total_ley_cost > 0:
            caster_profile.use_ley_energy(total_ley_cost)
        
        # Create the combined spell
        result_data = matching_rule["result"]
        combined_spell = CombinedSpell(
            name=result_data["name"],
            description=result_data["description"],
            damage_multiplier=result_data.get("damage_multiplier", 1.0),
            base_power=result_data.get("base_power", 0),
            area_effect=result_data.get("area_effect", False),
            blind_chance=result_data.get("blind_chance", 0.0),
            crit_chance=result_data.get("crit_chance", 0.0),
            stamina_recovery=result_data.get("stamina_recovery", 0),
            mana_cost=total_mana_cost,
            ley_energy_cost=total_ley_cost,
            component_spell_ids=[primary_spell_id, secondary_spell_id]
        )
        
        # Generate backlash chance
        backlash_chance = primary_spell.backlash_potential + secondary_spell.backlash_potential
        backlash_chance *= 1.5  # Combined spells are more unstable
        backlash_chance = min(0.95, backlash_chance)  # Cap at 95%
        
        # Return the result
        return {
            "success": True,
            "message": f"Successfully combined {primary_spell.name} and {secondary_spell.name} into {combined_spell.name}",
            "combined_spell": {
                "name": combined_spell.name,
                "description": combined_spell.description,
                "damage_multiplier": combined_spell.damage_multiplier,
                "base_power": combined_spell.base_power,
                "area_effect": combined_spell.area_effect,
                "special_effects": [k for k, v in result_data.items() 
                                  if k not in ["name", "description", "damage_multiplier", 
                                              "base_power", "area_effect", "mana_cost_multiplier"] 
                                  and v],
                "mana_cost": combined_spell.mana_cost,
                "ley_energy_cost": combined_spell.ley_energy_cost,
                "backlash_chance": backlash_chance
            },
            "resources_remaining": {
                "mana": caster_profile.mana_current,
                "ley_energy": caster_profile.current_ley_energy
            }
        }
    
    def _check_combination_rule(self, primary_spell: Spell, secondary_spell: Spell, rule: Dict[str, Any]) -> bool:
        """
        Check if two spells match a combination rule.
        
        Args:
            primary_spell: The primary spell
            secondary_spell: The secondary spell
            rule: The combination rule
            
        Returns:
            True if the spells match the rule, False otherwise
        """
        # Get component requirements
        components = rule["components"]
        if len(components) != 2:
            return False
        
        # Check first component against primary spell
        if not self._spell_matches_component(primary_spell, components[0]):
            # Try the reverse
            if not self._spell_matches_component(primary_spell, components[1]):
                return False
            
            # If primary matches second component, then secondary must match first
            if not self._spell_matches_component(secondary_spell, components[0]):
                return False
        else:
            # Primary matches first component, check if secondary matches second
            if not self._spell_matches_component(secondary_spell, components[1]):
                return False
        
        return True
    
    def _spell_matches_component(self, spell: Spell, component: Dict[str, Any]) -> bool:
        """
        Check if a spell matches a component requirement.
        
        Args:
            spell: The spell to check
            component: The component requirement
            
        Returns:
            True if the spell matches the component, False otherwise
        """
        # Check damage type
        if "damage_type" in component:
            # Check if any effect has the required damage type
            has_damage_type = False
            for effect in spell.effects:
                if effect.damage_type == component["damage_type"]:
                    has_damage_type = True
                    break
            
            if not has_damage_type:
                return False
        
        # Check effect type
        if "effect_type" in component:
            # Check if any effect has the required effect type
            has_effect_type = False
            for effect in spell.effects:
                if effect.effect_type == component["effect_type"]:
                    has_effect_type = True
                    break
            
            if not has_effect_type:
                return False
        
        # Check school
        if "school" in component and hasattr(spell, "school"):
            if spell.school != component["school"]:
                return False
        
        # Check tier
        if "tier" in component:
            if spell.tier != component["tier"]:
                return False
        
        return True


# ======================================================================
# 4. Spell Crafting & Customization
# ======================================================================

class SpellCraftingSystem:
    """
    System for crafting and customizing spells.
    
    This allows players to create personalized spells and modify existing ones.
    """
    
    def __init__(self, magic_system):
        """
        Initialize the spell crafting system.
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
        
        # Define available modifiers
        self.available_modifiers = {
            "extended_duration": SpellModifier(
                id="extended_duration",
                name="Extended Duration",
                type="extended_duration",
                description="Extends the duration of the spell's effects",
                mana_cost_modifier=1.3,
                duration_modifier=2.0,
                domain_requirements=[
                    DomainRequirement(domain=Domain.MIND, minimum_value=3)
                ]
            ),
            
            "area_expansion": SpellModifier(
                id="area_expansion",
                name="Area Expansion",
                type="area_expansion",
                description="Expands the area of effect for the spell",
                mana_cost_modifier=1.5,
                range_modifier=1.5,
                domain_requirements=[
                    DomainRequirement(domain=Domain.AUTHORITY, minimum_value=3),
                    DomainRequirement(domain=Domain.AWARENESS, minimum_value=2)
                ]
            ),
            
            "power_amplification": SpellModifier(
                id="power_amplification",
                name="Power Amplification",
                type="power_amplification",
                description="Increases the power of the spell's effects",
                mana_cost_modifier=1.6,
                effect_magnitude_modifier=1.5,
                domain_requirements=[
                    DomainRequirement(domain=Domain.SPIRIT, minimum_value=4)
                ]
            ),
            
            "mana_efficiency": SpellModifier(
                id="mana_efficiency",
                name="Mana Efficiency",
                type="mana_efficiency",
                description="Reduces the mana cost of the spell",
                mana_cost_modifier=0.7,
                effect_magnitude_modifier=0.9,
                domain_requirements=[
                    DomainRequirement(domain=Domain.MIND, minimum_value=4),
                    DomainRequirement(domain=Domain.CRAFT, minimum_value=3)
                ]
            ),
            
            "silent_casting": SpellModifier(
                id="silent_casting",
                name="Silent Casting",
                type="silent_casting",
                description="Allows the spell to be cast without verbal components",
                mana_cost_modifier=1.2,
                domain_requirements=[
                    DomainRequirement(domain=Domain.MIND, minimum_value=3),
                    DomainRequirement(domain=Domain.AWARENESS, minimum_value=3)
                ]
            ),
            
            "quick_casting": SpellModifier(
                id="quick_casting",
                name="Quick Casting",
                type="quick_casting",
                description="Reduces the casting time of the spell",
                mana_cost_modifier=1.3,
                casting_time_modifier=0.5,
                domain_requirements=[
                    DomainRequirement(domain=Domain.AWARENESS, minimum_value=4)
                ]
            ),
            
            "elemental_shift": SpellModifier(
                id="elemental_shift",
                name="Elemental Shift",
                type="elemental_shift",
                description="Changes the elemental damage type of the spell",
                mana_cost_modifier=1.1,
                domain_requirements=[
                    DomainRequirement(domain=Domain.SPIRIT, minimum_value=3)
                ]
            )
        }
    
    def get_available_modifiers(self, character_domains: Dict[Domain, int]) -> Dict[str, Dict[str, Any]]:
        """
        Get modifiers available to a character based on their domains.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            Dictionary of available modifiers with requirements met/not met
        """
        available_modifiers = {}
        
        for modifier_id, modifier in self.available_modifiers.items():
            requirements_met = True
            unmet_requirements = []
            
            # Check domain requirements
            for domain_req in modifier.domain_requirements:
                domain_value = character_domains.get(domain_req.domain, 0)
                if domain_value < domain_req.minimum_value:
                    requirements_met = False
                    unmet_requirements.append(f"{domain_req.domain.name} {domain_value}/{domain_req.minimum_value}")
            
            # Add to available modifiers
            available_modifiers[modifier_id] = {
                "name": modifier.name,
                "description": modifier.description,
                "requirements_met": requirements_met,
                "unmet_requirements": unmet_requirements if not requirements_met else [],
                "mana_cost_modifier": modifier.mana_cost_modifier,
                "effect_modifiers": {
                    "duration": modifier.duration_modifier if modifier.duration_modifier != 1.0 else None,
                    "range": modifier.range_modifier if modifier.range_modifier != 1.0 else None,
                    "magnitude": modifier.effect_magnitude_modifier if modifier.effect_magnitude_modifier != 1.0 else None,
                    "casting_time": modifier.casting_time_modifier if modifier.casting_time_modifier != 1.0 else None
                }
            }
        
        return available_modifiers
    
    def apply_spell_modifier(self, spell_id: str, modifier_id: str, 
                            character_domains: Dict[Domain, int],
                            new_element: Optional[DamageType] = None) -> Dict[str, Any]:
        """
        Apply a modifier to a spell.
        
        Args:
            spell_id: ID of the spell to modify
            modifier_id: ID of the modifier to apply
            character_domains: The character's domain values
            new_element: New damage type for elemental shift modifier
            
        Returns:
            Result of the modification attempt
        """
        # Get the spell
        spell = self.magic_system.casting_service.get_spell(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} not found"
            }
        
        # Get the modifier
        if modifier_id not in self.available_modifiers:
            return {
                "success": False,
                "message": f"Modifier {modifier_id} not found"
            }
        
        modifier = self.available_modifiers[modifier_id]
        
        # Check domain requirements
        for domain_req in modifier.domain_requirements:
            domain_value = character_domains.get(domain_req.domain, 0)
            if domain_value < domain_req.minimum_value:
                return {
                    "success": False,
                    "message": f"Insufficient {domain_req.domain.name} domain ({domain_value}/{domain_req.minimum_value})"
                }
        
        # Apply the modifier
        modified_spell = self._create_modified_spell(spell, modifier, new_element)
        
        # Return the result
        return {
            "success": True,
            "message": f"Successfully applied {modifier.name} to {spell.name}",
            "original_spell": {
                "name": spell.name,
                "description": spell.description,
                "mana_cost": spell.mana_cost,
                "ley_energy_cost": spell.ley_energy_cost,
                "casting_time_seconds": spell.casting_time_seconds
            },
            "modified_spell": {
                "name": f"{spell.name} ({modifier.name})",
                "description": modified_spell["description"],
                "mana_cost": modified_spell["mana_cost"],
                "ley_energy_cost": modified_spell["ley_energy_cost"],
                "casting_time_seconds": modified_spell["casting_time_seconds"],
                "modified_effects": modified_spell["modified_effects"]
            }
        }
    
    def _create_modified_spell(self, spell: Spell, modifier: SpellModifier, 
                              new_element: Optional[DamageType] = None) -> Dict[str, Any]:
        """
        Create a modified version of a spell.
        
        Args:
            spell: The spell to modify
            modifier: The modifier to apply
            new_element: New damage type for elemental shift modifier
            
        Returns:
            Dictionary with modified spell data
        """
        modified_spell = {
            "name": f"{spell.name} ({modifier.name})",
            "description": spell.description
        }
        
        # Apply mana cost modifier
        original_mana_cost = spell.mana_cost or 0
        modified_spell["mana_cost"] = int(original_mana_cost * modifier.mana_cost_modifier)
        
        # Apply ley energy cost modifier
        original_ley_cost = spell.ley_energy_cost or 0
        modified_spell["ley_energy_cost"] = int(original_ley_cost * modifier.ley_energy_cost_modifier)
        
        # Apply casting time modifier
        original_casting_time = spell.casting_time_seconds
        modified_spell["casting_time_seconds"] = int(original_casting_time * modifier.casting_time_modifier)
        
        # Track modified effects
        modified_effects = []
        
        # Apply modifier-specific changes
        if modifier.type == "extended_duration":
            # Extend duration of effects
            for effect in spell.effects:
                if effect.duration_seconds:
                    original_duration = effect.duration_seconds
                    new_duration = int(original_duration * modifier.duration_modifier)
                    modified_effects.append(f"Duration: {original_duration}s → {new_duration}s")
            
            modified_spell["description"] += f" (Extended duration: {int(modifier.duration_modifier * 100)}%)"
        
        elif modifier.type == "area_expansion":
            # Expand area of effect
            for effect in spell.effects:
                if effect.target_type in [TargetType.SINGLE_ENEMY, TargetType.SINGLE_ALLY]:
                    modified_effects.append(f"Target: Single → Area")
                elif effect.target_type in [TargetType.AREA_ENEMIES, TargetType.AREA_ALLIES]:
                    modified_effects.append(f"Area: {int(modifier.range_modifier * 100)}% larger")
            
            modified_spell["description"] += " (Expanded area of effect)"
        
        elif modifier.type == "power_amplification":
            # Increase effect magnitude
            for effect in spell.effects:
                if effect.effect_type == EffectType.DAMAGE and isinstance(effect.magnitude, (int, float)):
                    original_magnitude = effect.magnitude
                    new_magnitude = int(original_magnitude * modifier.effect_magnitude_modifier)
                    modified_effects.append(f"Damage: {original_magnitude} → {new_magnitude}")
                elif effect.effect_type == EffectType.HEAL and isinstance(effect.magnitude, (int, float)):
                    original_magnitude = effect.magnitude
                    new_magnitude = int(original_magnitude * modifier.effect_magnitude_modifier)
                    modified_effects.append(f"Healing: {original_magnitude} → {new_magnitude}")
            
            modified_spell["description"] += f" (Amplified power: {int(modifier.effect_magnitude_modifier * 100)}%)"
        
        elif modifier.type == "mana_efficiency":
            # Already applied mana cost modifier
            modified_effects.append(f"Mana cost: {original_mana_cost} → {modified_spell['mana_cost']}")
            modified_spell["description"] += f" (Mana efficient: {int((1 - modifier.mana_cost_modifier) * 100)}% less mana)"
        
        elif modifier.type == "silent_casting":
            # No mechanical changes beyond mana cost
            modified_effects.append("Can be cast silently")
            modified_spell["description"] += " (Can be cast without verbal components)"
        
        elif modifier.type == "quick_casting":
            # Already applied casting time modifier
            modified_effects.append(f"Casting time: {original_casting_time}s → {modified_spell['casting_time_seconds']}s")
            modified_spell["description"] += f" (Quick casting: {int((1 - modifier.casting_time_modifier) * 100)}% faster)"
        
        elif modifier.type == "elemental_shift" and new_element:
            # Change damage type
            for effect in spell.effects:
                if effect.damage_type:
                    original_element = effect.damage_type
                    modified_effects.append(f"Element: {original_element.name} → {new_element.name}")
            
            modified_spell["description"] += f" (Element shifted to {new_element.name})"
        
        modified_spell["modified_effects"] = modified_effects
        return modified_spell
    
    def create_custom_spell(self, caster_magic_profile: MagicUser, character_domains: Dict[Domain, int],
                          spell_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom spell from scratch.
        
        Args:
            caster_magic_profile: Magic profile of the caster
            character_domains: The character's domain values
            spell_data: Data for the new spell
            
        Returns:
            Result of the spell creation attempt
        """
        # Check if the character has the necessary skill
        if "spell_crafting" not in caster_magic_profile.known_skills:
            return {
                "success": False,
                "message": "You need to learn spell crafting first"
            }
        
        # Check if the character has a Mana Heart
        if not caster_magic_profile.has_mana_heart:
            return {
                "success": False,
                "message": "You need a Mana Heart to craft spells"
            }
        
        # Extract spell data
        name = spell_data.get("name", "Custom Spell")
        description = spell_data.get("description", "A custom spell")
        tier = spell_data.get("tier", MagicTier.MANA_INFUSION)
        magic_sources = spell_data.get("magic_sources", [MagicSource.MANA_HEART])
        mana_cost = spell_data.get("mana_cost", 10)
        ley_energy_cost = spell_data.get("ley_energy_cost", 0)
        casting_time = spell_data.get("casting_time_seconds", 2)
        domain_requirements = spell_data.get("domain_requirements", [])
        effects_data = spell_data.get("effects", [])
        
        # Check if character meets domain requirements
        for req in domain_requirements:
            domain = req.get("domain")
            min_value = req.get("value", 0)
            
            try:
                domain_enum = Domain[domain]
                domain_value = character_domains.get(domain_enum, 0)
                if domain_value < min_value:
                    return {
                        "success": False,
                        "message": f"Insufficient {domain} domain ({domain_value}/{min_value})"
                    }
            except (KeyError, ValueError):
                return {
                    "success": False,
                    "message": f"Invalid domain: {domain}"
                }
        
        # Convert domain requirements to proper format
        domain_reqs = []
        for req in domain_requirements:
            try:
                domain_enum = Domain[req.get("domain")]
                domain_reqs.append(DomainRequirement(
                    domain=domain_enum,
                    minimum_value=req.get("value", 0)
                ))
            except (KeyError, ValueError):
                continue
        
        # Create effects
        effects = []
        for effect_data in effects_data:
            effect_type_str = effect_data.get("effect_type", "DAMAGE")
            try:
                effect_type = EffectType[effect_type_str]
            except (KeyError, ValueError):
                return {
                    "success": False,
                    "message": f"Invalid effect type: {effect_type_str}"
                }
            
            target_type_str = effect_data.get("target_type", "SINGLE_ENEMY")
            try:
                target_type = TargetType[target_type_str]
            except (KeyError, ValueError):
                return {
                    "success": False,
                    "message": f"Invalid target type: {target_type_str}"
                }
            
            damage_type_str = effect_data.get("damage_type")
            damage_type = None
            if damage_type_str:
                try:
                    damage_type = DamageType[damage_type_str]
                except (KeyError, ValueError):
                    return {
                        "success": False,
                        "message": f"Invalid damage type: {damage_type_str}"
                    }
            
            effect = MagicalEffect(
                effect_type=effect_type,
                description_template=effect_data.get("description", "A magical effect occurs"),
                magnitude=effect_data.get("magnitude", 10),
                target_type=target_type,
                damage_type=damage_type,
                duration_seconds=effect_data.get("duration_seconds")
            )
            effects.append(effect)
        
        if not effects:
            return {
                "success": False,
                "message": "Spell must have at least one effect"
            }
        
        # Generate ID for the spell
        import uuid
        spell_id = f"custom_spell_{uuid.uuid4().hex[:8]}"
        
        # Calculate backlash potential based on power and tier
        base_backlash = 0.05
        if tier == MagicTier.ARCANE_MASTERY:
            base_backlash = 0.1
        
        # Increase backlash for powerful effects
        for effect in effects:
            if effect.effect_type == EffectType.DAMAGE and isinstance(effect.magnitude, (int, float)):
                if effect.magnitude > 15:
                    base_backlash += 0.05
                if effect.magnitude > 25:
                    base_backlash += 0.1
        
        # Create the spell
        spell = Spell(
            id=spell_id,
            name=name,
            description=description,
            tier=tier,
            magic_source_affinity=magic_sources,
            effects=effects,
            mana_cost=mana_cost,
            ley_energy_cost=ley_energy_cost,
            casting_time_seconds=casting_time,
            domain_requirements=domain_reqs,
            backlash_potential=base_backlash
        )
        
        # Register the spell with the magic system
        self.magic_system.casting_service.register_spell(spell)
        
        # Add the spell to the character's known spells
        caster_magic_profile.known_spells.append(spell_id)
        
        # Return the result
        return {
            "success": True,
            "message": f"Successfully created custom spell: {name}",
            "spell_id": spell_id,
            "spell": {
                "name": name,
                "description": description,
                "tier": tier.name,
                "mana_cost": mana_cost,
                "ley_energy_cost": ley_energy_cost,
                "casting_time_seconds": casting_time,
                "effects": [
                    {
                        "type": effect.effect_type.name,
                        "target_type": effect.target_type.name,
                        "damage_type": effect.damage_type.name if effect.damage_type else None,
                        "magnitude": effect.magnitude,
                        "duration_seconds": effect.duration_seconds
                    }
                    for effect in effects
                ],
                "backlash_potential": base_backlash
            }
        }


# ======================================================================
# 5. Magical Consequences & Reactions
# ======================================================================

class MagicalConsequenceSystem:
    """
    System for tracking and applying magical consequences to the world.
    
    This ensures magic has lasting effects and meaningful choices.
    """
    
    def __init__(self):
        """Initialize the magical consequence system"""
        # Track active magical consequences by location
        self.active_consequences: Dict[str, List[Effect]] = {}
        
        # Define consequence rules
        self.consequence_rules = [
            # Necromancy leaves death echoes
            {
                "trigger": {
                    "school": MagicSchool.NECROMANCY,
                    "success": True
                },
                "consequence": {
                    "effect_id": "death_echo",
                    "description": "Lingering death energy makes the area feel cold and unsettling",
                    "duration_hours": 24,
                    "game_effects": [
                        {
                            "type": "ambient",
                            "description": "The air feels unnaturally cold and still",
                            "mechanics": "Undead creatures are more likely to appear"
                        },
                        {
                            "type": "boost",
                            "target": "necromancy",
                            "value": 0.2,
                            "description": "Necromantic magic is stronger here"
                        }
                    ]
                }
            },
            
            # Failed dangerous magic corrupts area
            {
                "trigger": {
                    "corruption_risk": 0.3,
                    "success": False
                },
                "consequence": {
                    "effect_id": "magical_corruption",
                    "description": "Failed magic has left a taint of corruption in the area",
                    "duration_hours": 48,
                    "game_effects": [
                        {
                            "type": "ambient",
                            "description": "The air shimmers with an unhealthy energy",
                            "mechanics": "Spells have a 10% higher chance to fail"
                        },
                        {
                            "type": "corruption",
                            "value": 0.1,
                            "description": "The area is slowly becoming corrupted"
                        }
                    ]
                }
            },
            
            # Elemental magic affects environment
            {
                "trigger": {
                    "damage_type": DamageType.FIRE,
                    "power_threshold": 20,
                    "success": True
                },
                "consequence": {
                    "effect_id": "lingering_flames",
                    "description": "Magical fire has superheated the area",
                    "duration_hours": 6,
                    "game_effects": [
                        {
                            "type": "ambient",
                            "description": "The air is hot and shimmers with heat",
                            "mechanics": "Fire damage increased by 20%, ice damage decreased by 20%"
                        },
                        {
                            "type": "environmental",
                            "description": "Flammable objects may spontaneously ignite"
                        }
                    ]
                }
            },
            
            {
                "trigger": {
                    "damage_type": DamageType.ICE,
                    "power_threshold": 20,
                    "success": True
                },
                "consequence": {
                    "effect_id": "magical_frost",
                    "description": "Magical ice has chilled the area to an unnatural degree",
                    "duration_hours": 6,
                    "game_effects": [
                        {
                            "type": "ambient",
                            "description": "The air is frigid and frost forms on surfaces",
                            "mechanics": "Ice damage increased by 20%, fire damage decreased by 20%"
                        },
                        {
                            "type": "environmental",
                            "description": "The ground is slippery with ice"
                        }
                    ]
                }
            },
            
            # Repeated magic in same location creates ley disruption
            {
                "trigger": {
                    "spells_cast_count": 5,
                    "time_window_minutes": 10
                },
                "consequence": {
                    "effect_id": "ley_disruption",
                    "description": "The rapid use of magic has disrupted the local leylines",
                    "duration_hours": 12,
                    "game_effects": [
                        {
                            "type": "ambient",
                            "description": "The air crackles with unstable magical energy",
                            "mechanics": "Spell effects are unpredictable, backlash chance increased by 20%"
                        },
                        {
                            "type": "ley_energy",
                            "description": "Leyline energy fluctuates wildly",
                            "mechanics": "Drawing from leylines may yield 200% or 0% of expected energy"
                        }
                    ]
                }
            },
            
            # Powerful teleportation creates spatial anomalies
            {
                "trigger": {
                    "effect_type": EffectType.TELEPORT,
                    "power_threshold": 30,
                    "success": True
                },
                "consequence": {
                    "effect_id": "spatial_anomaly",
                    "description": "The fabric of space has been temporarily weakened",
                    "duration_hours": 6,
                    "game_effects": [
                        {
                            "type": "ambient",
                            "description": "Distances seem to shift unpredictably",
                            "mechanics": "Teleportation spells are 50% more effective, but 30% more likely to cause backlash"
                        },
                        {
                            "type": "random_event",
                            "description": "Objects may spontaneously teleport short distances",
                            "mechanics": "5% chance per hour of a random teleportation event"
                        }
                    ]
                }
            }
        ]
    
    def apply_spell_consequences(self, spell: Spell, success: bool, 
                               location_id: str, location_magic_profile: Any,
                               spell_context: Dict[str, Any]) -> List[Effect]:
        """
        Apply consequences from a spell being cast.
        
        Args:
            spell: The spell that was cast
            success: Whether the spell was successful
            location_id: ID of the location
            location_magic_profile: Magical profile of the location
            spell_context: Additional context for the spell cast
            
        Returns:
            List of effects applied to the location
        """
        consequences = []
        
        # Get spell characteristics
        spell_school = getattr(spell, "school", None)
        spell_damage_type = None
        spell_effect_type = None
        spell_power = 0
        
        for effect in spell.effects:
            if effect.damage_type:
                spell_damage_type = effect.damage_type
            
            spell_effect_type = effect.effect_type
            
            # Estimate spell power from damage/healing magnitude
            if effect.effect_type in [EffectType.DAMAGE, EffectType.HEAL] and isinstance(effect.magnitude, (int, float)):
                spell_power = max(spell_power, effect.magnitude)
        
        # Check each consequence rule
        for rule in self.consequence_rules:
            trigger = rule["trigger"]
            
            # Check success/failure condition
            if "success" in trigger and trigger["success"] != success:
                continue
            
            # Check magic school
            if "school" in trigger and spell_school != trigger["school"]:
                continue
            
            # Check damage type
            if "damage_type" in trigger and spell_damage_type != trigger["damage_type"]:
                continue
            
            # Check effect type
            if "effect_type" in trigger and spell_effect_type != trigger["effect_type"]:
                continue
            
            # Check power threshold
            if "power_threshold" in trigger and spell_power < trigger["power_threshold"]:
                continue
            
            # Check corruption risk
            if "corruption_risk" in trigger and spell.backlash_potential < trigger["corruption_risk"]:
                continue
            
            # Check spell cast count in time window
            if "spells_cast_count" in trigger and "time_window_minutes" in trigger:
                # This would require tracking spell casts over time
                # For simplicity, assume this is provided in the context
                recent_casts = spell_context.get("recent_casts_count", 0)
                if recent_casts < trigger["spells_cast_count"]:
                    continue
            
            # All conditions met, apply the consequence
            consequence_data = rule["consequence"]
            
            effect = Effect(
                id=consequence_data["effect_id"],
                description=consequence_data["description"],
                duration_seconds=consequence_data["duration_hours"] * 3600,
                magnitude=consequence_data.get("game_effects", [])
            )
            
            consequences.append(effect)
            
            # Track the active consequence
            if location_id not in self.active_consequences:
                self.active_consequences[location_id] = []
            
            self.active_consequences[location_id].append(effect)
            
            # Apply effects to location if it has the necessary methods
            if hasattr(location_magic_profile, "add_ambient_effect"):
                location_magic_profile.add_ambient_effect(
                    effect_id=consequence_data["effect_id"],
                    duration_hours=consequence_data["duration_hours"]
                )
            
            # Update location corruption if applicable
            corruption_effect = next((e for e in consequence_data.get("game_effects", []) 
                                    if e.get("type") == "corruption"), None)
            if corruption_effect and hasattr(location_magic_profile, "corruption_level"):
                location_magic_profile.corruption_level += corruption_effect.get("value", 0)
        
        return consequences
    
    def get_active_consequences(self, location_id: str) -> List[Effect]:
        """
        Get active magical consequences at a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            List of active effects
        """
        return self.active_consequences.get(location_id, [])
    
    def update_consequences(self, seconds_elapsed: int = 1) -> None:
        """
        Update all active consequences, removing expired ones.
        
        Args:
            seconds_elapsed: Seconds elapsed since last update
        """
        for location_id, effects in list(self.active_consequences.items()):
            updated_effects = []
            for effect in effects:
                if effect.duration_seconds is not None:
                    effect.duration_seconds -= seconds_elapsed
                    if effect.duration_seconds <= 0:
                        continue
                updated_effects.append(effect)
            
            if updated_effects:
                self.active_consequences[location_id] = updated_effects
            else:
                del self.active_consequences[location_id]
    
    def generate_consequence_descriptions(self, location_id: str) -> List[str]:
        """
        Generate narrative descriptions of active consequences.
        
        Args:
            location_id: ID of the location
            
        Returns:
            List of descriptive strings
        """
        descriptions = []
        effects = self.get_active_consequences(location_id)
        
        for effect in effects:
            descriptions.append(effect.description)
            
            # Add specific game effect descriptions
            if isinstance(effect.magnitude, list):
                for game_effect in effect.magnitude:
                    if isinstance(game_effect, dict) and "description" in game_effect:
                        descriptions.append(f"- {game_effect['description']}")
        
        return descriptions


class NPCMagicRelationship:
    """
    System for NPC reactions to magic use.
    
    This makes NPCs respond appropriately to different types of magic.
    """
    
    def __init__(self):
        """Initialize the NPC magic relationship system"""
        # Define faction attitudes toward magic
        self.faction_attitudes = {
            "Temple_of_Light": {
                "general": "cautious",
                "schools": {
                    MagicSchool.NECROMANCY: "hostile",
                    MagicSchool.RESTORATION: "favorable",
                    MagicSchool.DIVINATION: "favorable"
                },
                "tiers": {
                    MagicTier.ARCANE_MASTERY: "suspicious",
                    MagicTier.SPIRITUAL_UTILITY: "favorable"
                }
            },
            
            "Mage_Guild": {
                "general": "favorable",
                "schools": {
                    MagicSchool.EVOCATION: "favorable",
                    MagicSchool.TRANSMUTATION: "favorable",
                    MagicSchool.CONJURATION: "favorable",
                    MagicSchool.NECROMANCY: "cautious"
                },
                "tiers": {
                    MagicTier.ARCANE_MASTERY: "very_favorable",
                    MagicTier.MANA_INFUSION: "favorable"
                }
            },
            
            "Merchants_League": {
                "general": "neutral",
                "schools": {
                    MagicSchool.ENCHANTMENT: "favorable",
                    MagicSchool.DIVINATION: "favorable"
                },
                "tiers": {}
            },
            
            "City_Watch": {
                "general": "cautious",
                "schools": {
                    MagicSchool.EVOCATION: "hostile",  # Destructive magic
                    MagicSchool.NECROMANCY: "hostile",
                    MagicSchool.ILLUSION: "suspicious"
                },
                "tiers": {
                    MagicTier.ARCANE_MASTERY: "suspicious"
                }
            },
            
            "Wilderness_Tribes": {
                "general": "cautious",
                "schools": {
                    MagicSchool.RESTORATION: "favorable",
                    MagicSchool.TRANSMUTATION: "favorable",
                    MagicSchool.NECROMANCY: "hostile"
                },
                "tiers": {
                    MagicTier.SPIRITUAL_UTILITY: "very_favorable"
                }
            },
            
            "Academy_of_Arcane_Arts": {
                "general": "very_favorable",
                "schools": {
                    MagicSchool.EVOCATION: "favorable",
                    MagicSchool.TRANSMUTATION: "favorable",
                    MagicSchool.CONJURATION: "favorable",
                    MagicSchool.ABJURATION: "favorable"
                },
                "tiers": {
                    MagicTier.ARCANE_MASTERY: "very_favorable",
                    MagicTier.MANA_INFUSION: "favorable"
                }
            }
        }
        
        # Define profession attitudes toward magic
        self.profession_attitudes = {
            "blacksmith": {
                "general": "neutral",
                "schools": {
                    MagicSchool.TRANSMUTATION: "favorable",
                    MagicSchool.ENCHANTMENT: "favorable"
                }
            },
            
            "farmer": {
                "general": "cautious",
                "schools": {
                    MagicSchool.TRANSMUTATION: "favorable"  # For crops
                }
            },
            
            "merchant": {
                "general": "neutral",
                "schools": {
                    MagicSchool.ENCHANTMENT: "favorable",
                    MagicSchool.DIVINATION: "favorable"
                }
            },
            
            "guard": {
                "general": "cautious",
                "schools": {
                    MagicSchool.EVOCATION: "hostile",
                    MagicSchool.ILLUSION: "hostile"
                }
            },
            
            "scholar": {
                "general": "favorable",
                "schools": {
                    MagicSchool.DIVINATION: "very_favorable"
                }
            },
            
            "healer": {
                "general": "favorable",
                "schools": {
                    MagicSchool.RESTORATION: "very_favorable",
                    MagicSchool.NECROMANCY: "hostile"
                }
            }
        }
        
        # Define reaction narratives
        self.reaction_narratives = {
            "very_favorable": [
                "{npc_name} watches your spellcasting with admiration.",
                "{npc_name}'s eyes light up with excitement as you cast {spell_name}.",
                "\"Impressive magic!\" {npc_name} exclaims, clearly impressed by your {spell_name}."
            ],
            
            "favorable": [
                "{npc_name} nods approvingly as you cast {spell_name}.",
                "{npc_name} seems pleased by your magical prowess.",
                "\"Well cast,\" {npc_name} comments with a small smile."
            ],
            
            "neutral": [
                "{npc_name} observes your spellcasting without reaction.",
                "{npc_name} barely seems to notice your use of {spell_name}.",
                "{npc_name} gives a noncommittal shrug at your display of magic."
            ],
            
            "cautious": [
                "{npc_name} takes a step back as you begin casting {spell_name}.",
                "{npc_name} watches your spellcasting with a wary expression.",
                "\"Be careful with that,\" {npc_name} warns, eyeing your magic with suspicion."
            ],
            
            "suspicious": [
                "{npc_name} narrows their eyes as you cast {spell_name}.",
                "\"What are you doing with that magic?\" {npc_name} asks sharply.",
                "{npc_name} seems uncomfortable with your use of {spell_name}."
            ],
            
            "hostile": [
                "{npc_name} recoils in horror at your use of {spell_name}!",
                "\"Stop that at once!\" {npc_name} demands, clearly disturbed by your magic.",
                "{npc_name} reaches for a weapon as you cast {spell_name}."
            ]
        }
        
        # Define reputation changes
        self.reputation_changes = {
            "very_favorable": 5,
            "favorable": 2,
            "neutral": 0,
            "cautious": -1,
            "suspicious": -3,
            "hostile": -10
        }
    
    def get_npc_magic_reaction(self, npc: NPC, spell_cast: Spell, 
                              success: bool) -> ReactionResult:
        """
        Determine an NPC's reaction to a spell being cast.
        
        Args:
            npc: The NPC observing the magic
            spell_cast: The spell being cast
            success: Whether the spell was successful
            
        Returns:
            Reaction result
        """
        # Get base attitude from faction
        attitude = "neutral"
        if npc.faction in self.faction_attitudes:
            attitude = self.faction_attitudes[npc.faction]["general"]
        
        # Check profession-specific attitude
        if npc.profession in self.profession_attitudes:
            prof_attitude = self.profession_attitudes[npc.profession]["general"]
            # Profession takes precedence over faction for specific reactions
            attitude = prof_attitude
        
        # Check for spell-specific attitudes
        spell_school = getattr(spell_cast, "school", None)
        if spell_school:
            # Check faction attitude toward this school
            if npc.faction in self.faction_attitudes:
                faction_school_attitudes = self.faction_attitudes[npc.faction]["schools"]
                if spell_school in faction_school_attitudes:
                    attitude = faction_school_attitudes[spell_school]
            
            # Check profession attitude toward this school
            if npc.profession in self.profession_attitudes:
                prof_school_attitudes = self.profession_attitudes[npc.profession]["schools"]
                if spell_school in prof_school_attitudes:
                    # Profession attitude takes precedence
                    attitude = prof_school_attitudes[spell_school]
        
        # Check for tier-specific attitudes
        if npc.faction in self.faction_attitudes:
            faction_tier_attitudes = self.faction_attitudes[npc.faction]["tiers"]
            if spell_cast.tier in faction_tier_attitudes:
                tier_attitude = faction_tier_attitudes[spell_cast.tier]
                # Only apply if the tier attitude is stronger
                if self._is_stronger_attitude(tier_attitude, attitude):
                    attitude = tier_attitude
        
        # Modify attitude based on spell success
        if not success:
            # Failed spells make NPCs more cautious/negative
            attitude = self._worsen_attitude(attitude)
        
        # Calculate reputation change
        reputation_change = self.reputation_changes.get(attitude, 0)
        
        # Generate narrative
        narratives = self.reaction_narratives.get(attitude, self.reaction_narratives["neutral"])
        narrative = random.choice(narratives).format(
            npc_name=npc.name,
            spell_name=spell_cast.name
        )
        
        return ReactionResult(
            reaction_type=attitude,
            narrative=narrative,
            reputation_change=reputation_change
        )
    
    def _is_stronger_attitude(self, attitude1: str, attitude2: str) -> bool:
        """
        Determine if attitude1 is a stronger reaction than attitude2.
        
        Args:
            attitude1: First attitude
            attitude2: Second attitude
            
        Returns:
            True if attitude1 is stronger (more extreme) than attitude2
        """
        attitude_strength = {
            "very_favorable": 3,
            "favorable": 2,
            "neutral": 0,
            "cautious": -1,
            "suspicious": -2,
            "hostile": -3
        }
        
        strength1 = attitude_strength.get(attitude1, 0)
        strength2 = attitude_strength.get(attitude2, 0)
        
        return abs(strength1) > abs(strength2)
    
    def _worsen_attitude(self, attitude: str) -> str:
        """
        Make an attitude more negative/cautious.
        
        Args:
            attitude: The original attitude
            
        Returns:
            A more negative attitude
        """
        attitude_progression = {
            "very_favorable": "favorable",
            "favorable": "neutral",
            "neutral": "cautious",
            "cautious": "suspicious",
            "suspicious": "hostile",
            "hostile": "hostile"  # Can't get worse
        }
        
        return attitude_progression.get(attitude, attitude)


# ======================================================================
# 6. Domain-Magic Synergy Bonuses
# ======================================================================

class DomainMagicSynergy:
    """
    System for domain-based bonuses to magic.
    
    This rewards balanced character development and creates
    interesting combinations of domains and magic types.
    """
    
    def __init__(self):
        """Initialize the domain-magic synergy system"""
        # Define synergy maps between domains and magic schools
        self.domain_school_synergy = {
            MagicSchool.EVOCATION: [Domain.FIRE, Domain.WATER, Domain.EARTH, Domain.AIR, Domain.LIGHT, Domain.DARKNESS],
            MagicSchool.ABJURATION: [Domain.SPIRIT, Domain.MIND, Domain.AUTHORITY],
            MagicSchool.CONJURATION: [Domain.SPIRIT, Domain.CRAFT, Domain.MIND],
            MagicSchool.TRANSMUTATION: [Domain.EARTH, Domain.WATER, Domain.CRAFT, Domain.MIND],
            MagicSchool.DIVINATION: [Domain.MIND, Domain.AWARENESS, Domain.SPIRIT],
            MagicSchool.ENCHANTMENT: [Domain.SOCIAL, Domain.MIND, Domain.SPIRIT],
            MagicSchool.ILLUSION: [Domain.MIND, Domain.AWARENESS, Domain.SOCIAL],
            MagicSchool.NECROMANCY: [Domain.SPIRIT, Domain.DARKNESS, Domain.BODY],
            MagicSchool.RESTORATION: [Domain.BODY, Domain.SPIRIT, Domain.LIGHT],
            MagicSchool.MENTALISM: [Domain.MIND, Domain.SOCIAL, Domain.AUTHORITY]
        }
        
        # Define synergy maps between domains and damage types
        self.domain_damage_synergy = {
            DamageType.FIRE: [Domain.FIRE],
            DamageType.ICE: [Domain.ICE, Domain.WATER],
            DamageType.LIGHTNING: [Domain.AIR, Domain.FIRE],
            DamageType.EARTH: [Domain.EARTH],
            DamageType.AIR: [Domain.AIR, Domain.WIND],
            DamageType.WATER: [Domain.WATER],
            DamageType.LIGHT: [Domain.LIGHT, Domain.SPIRIT],
            DamageType.DARKNESS: [Domain.DARKNESS],
            DamageType.ARCANE: [Domain.MIND, Domain.SPIRIT],
            DamageType.NECROTIC: [Domain.DARKNESS, Domain.SPIRIT],
            DamageType.PSYCHIC: [Domain.MIND, Domain.SOCIAL],
            DamageType.SPIRITUAL: [Domain.SPIRIT]
        }
        
        # Define domain pair synergies (when two domains work well together)
        self.domain_pair_synergies = [
            (Domain.BODY, Domain.SPIRIT, "life_force_mastery"),
            (Domain.MIND, Domain.SPIRIT, "psychic_attunement"),
            (Domain.CRAFT, Domain.MIND, "precise_enchantment"),
            (Domain.FIRE, Domain.AIR, "storm_calling"),
            (Domain.WATER, Domain.EARTH, "nature_harmony"),
            (Domain.LIGHT, Domain.DARKNESS, "balance_mastery"),
            (Domain.AWARENESS, Domain.MIND, "perceptive_casting"),
            (Domain.SOCIAL, Domain.AUTHORITY, "commanding_presence"),
            (Domain.SPIRIT, Domain.DARKNESS, "shadow_binding"),
            (Domain.FIRE, Domain.EARTH, "magma_control")
        ]
    
    def calculate_synergy_bonus(self, character: Dict[str, Any], spell: Spell) -> float:
        """
        Calculate synergy bonus when domains align with magic.
        
        Args:
            character: Character data including domains
            spell: The spell being cast
            
        Returns:
            Bonus multiplier (1.0 = no bonus)
        """
        bonus = 1.0
        
        # Get character domains
        character_domains = character.get("domains", {})
        
        # Get spell characteristics
        spell_school = getattr(spell, "school", None)
        spell_damage_types = []
        for effect in spell.effects:
            if effect.damage_type and effect.damage_type not in spell_damage_types:
                spell_damage_types.append(effect.damage_type)
        
        # Check school synergy
        if spell_school and spell_school in self.domain_school_synergy:
            synergy_domains = self.domain_school_synergy[spell_school]
            domain_levels = [character_domains.get(domain, 0) for domain in synergy_domains]
            
            # Calculate bonus based on relevant domain levels
            high_domains = [level for level in domain_levels if level >= 5]
            med_domains = [level for level in domain_levels if 3 <= level < 5]
            
            if len(high_domains) >= 2:
                # Mastery in multiple relevant domains
                bonus += 0.5  # 50% bonus
            elif len(high_domains) >= 1:
                # Mastery in one relevant domain
                bonus += 0.3  # 30% bonus
            elif len(med_domains) >= 2:
                # Competence in multiple relevant domains
                bonus += 0.2  # 20% bonus
            elif len(med_domains) >= 1:
                # Competence in one relevant domain
                bonus += 0.1  # 10% bonus
        
        # Check damage type synergy
        for damage_type in spell_damage_types:
            if damage_type in self.domain_damage_synergy:
                synergy_domains = self.domain_damage_synergy[damage_type]
                domain_levels = [character_domains.get(domain, 0) for domain in synergy_domains]
                
                # Calculate bonus based on damage type affinity
                max_level = max(domain_levels) if domain_levels else 0
                if max_level >= 5:
                    bonus += 0.3  # 30% bonus for mastery
                elif max_level >= 3:
                    bonus += 0.15  # 15% bonus for competence
        
        # Check domain pair synergies
        for domain1, domain2, synergy_name in self.domain_pair_synergies:
            level1 = character_domains.get(domain1, 0)
            level2 = character_domains.get(domain2, 0)
            
            # Both domains must be at least competent
            if level1 >= 3 and level2 >= 3:
                # Calculate average level
                avg_level = (level1 + level2) / 2
                
                # Apply synergy bonus based on spell characteristics
                if synergy_name == "life_force_mastery" and any(e.effect_type == EffectType.HEAL for e in spell.effects):
                    bonus += 0.2  # 20% bonus to healing
                
                elif synergy_name == "psychic_attunement" and any(e.damage_type == DamageType.PSYCHIC for e in spell.effects):
                    bonus += 0.25  # 25% bonus to psychic damage
                
                elif synergy_name == "precise_enchantment" and spell_school == MagicSchool.ENCHANTMENT:
                    bonus += 0.2  # 20% bonus to enchantments
                
                elif synergy_name == "storm_calling" and any(e.damage_type in [DamageType.LIGHTNING, DamageType.AIR] for e in spell.effects):
                    bonus += 0.3  # 30% bonus to storm magic
                
                # Add more synergy checks as needed
        
        # Cap the bonus at a reasonable maximum
        return min(2.0, bonus)  # Maximum 100% bonus
    
    def get_domain_synergy_description(self, character: Dict[str, Any], spell: Spell) -> List[str]:
        """
        Get descriptions of active domain synergies for a spell.
        
        Args:
            character: Character data including domains
            spell: The spell being cast
            
        Returns:
            List of synergy descriptions
        """
        synergy_descriptions = []
        
        # Get character domains
        character_domains = character.get("domains", {})
        
        # Get spell characteristics
        spell_school = getattr(spell, "school", None)
        spell_damage_types = []
        for effect in spell.effects:
            if effect.damage_type and effect.damage_type not in spell_damage_types:
                spell_damage_types.append(effect.damage_type)
        
        # Check school synergy
        if spell_school and spell_school in self.domain_school_synergy:
            synergy_domains = self.domain_school_synergy[spell_school]
            high_domains = [d for d in synergy_domains if character_domains.get(d, 0) >= 5]
            med_domains = [d for d in synergy_domains if 3 <= character_domains.get(d, 0) < 5]
            
            if high_domains:
                domain_names = ", ".join(d.name for d in high_domains)
                synergy_descriptions.append(f"Your mastery of {domain_names} greatly enhances your {spell_school.name} magic")
            elif med_domains:
                domain_names = ", ".join(d.name for d in med_domains)
                synergy_descriptions.append(f"Your skill in {domain_names} strengthens your {spell_school.name} magic")
        
        # Check damage type synergy
        for damage_type in spell_damage_types:
            if damage_type in self.domain_damage_synergy:
                synergy_domains = self.domain_damage_synergy[damage_type]
                high_domains = [d for d in synergy_domains if character_domains.get(d, 0) >= 5]
                
                if high_domains:
                    domain_names = ", ".join(d.name for d in high_domains)
                    synergy_descriptions.append(f"Your mastery of {domain_names} empowers your {damage_type.name} damage")
        
        # Check domain pair synergies
        for domain1, domain2, synergy_name in self.domain_pair_synergies:
            level1 = character_domains.get(domain1, 0)
            level2 = character_domains.get(domain2, 0)
            
            # Both domains must be at least competent
            if level1 >= 3 and level2 >= 3:
                # Domain pair synergy descriptions
                if synergy_name == "life_force_mastery" and any(e.effect_type == EffectType.HEAL for e in spell.effects):
                    synergy_descriptions.append(f"Your {domain1.name} and {domain2.name} domains harmonize, enhancing your healing magic")
                
                elif synergy_name == "psychic_attunement" and any(e.damage_type == DamageType.PSYCHIC for e in spell.effects):
                    synergy_descriptions.append(f"The synergy between your {domain1.name} and {domain2.name} domains amplifies your psychic abilities")
                
                # Add more synergy descriptions as needed
        
        return synergy_descriptions


# ======================================================================
# 7. Combat Magic Integration
# ======================================================================

class TacticalMagicCombat:
    """
    Advanced combat magic tactics.
    
    This makes magic more tactical and meaningful in combat scenarios.
    """
    
    def __init__(self, magic_system):
        """
        Initialize the tactical magic combat system.
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
    
    def create_magical_combat_move(self, spell: Spell, context: CombatContext) -> CombatMove:
        """
        Create a context-aware combat move from a spell.
        
        Args:
            spell: The spell to convert
            context: Combat context information
            
        Returns:
            A combat move enhanced with contextual information
        """
        # Start with basic conversion
        move = spell.to_combat_move()
        
        # Track original description to append tactical information
        original_description = move.description
        tactical_notes = []
        
        # Modify based on number of enemies
        if context.enemy_count > 1:
            # Check if spell can affect multiple targets
            multi_target = False
            for effect in spell.effects:
                if effect.target_type in [TargetType.AREA_ENEMIES, TargetType.AREA_ALL]:
                    multi_target = True
                    break
            
            if multi_target:
                tactical_notes.append("Can target multiple enemies")
                if "AREA_EFFECT" not in move.effects:
                    move.effects.append("AREA_EFFECT")
        
        # Modify based on terrain
        if context.terrain == "high_ground":
            # Ranged attacks benefit from high ground
            ranged_spell = any(effect.target_type not in [TargetType.SELF, TargetType.SINGLE_ALLY] 
                             for effect in spell.effects)
            
            if ranged_spell:
                tactical_notes.append("Enhanced by elevation")
                move.base_damage = int(move.base_damage * 1.2)
        
        elif context.terrain == "water":
            # Water enhances water spells, weakens fire
            for effect in spell.effects:
                if effect.damage_type == DamageType.WATER:
                    tactical_notes.append("Enhanced by water terrain")
                    move.base_damage = int(move.base_damage * 1.3)
                elif effect.damage_type == DamageType.FIRE:
                    tactical_notes.append("Weakened by water terrain")
                    move.base_damage = int(move.base_damage * 0.7)
        
        # Modify based on weather
        if context.weather_conditions == "rain":
            # Rain enhances water, weakens fire
            for effect in spell.effects:
                if effect.damage_type == DamageType.WATER:
                    tactical_notes.append("Enhanced by rain")
                    move.base_damage = int(move.base_damage * 1.2)
                elif effect.damage_type == DamageType.FIRE:
                    tactical_notes.append("Weakened by rain")
                    move.base_damage = int(move.base_damage * 0.8)
        
        elif context.weather_conditions == "storm":
            # Storm enhances lightning/air
            for effect in spell.effects:
                if effect.damage_type in [DamageType.LIGHTNING, DamageType.AIR]:
                    tactical_notes.append("Enhanced by storm")
                    move.base_damage = int(move.base_damage * 1.3)
        
        # Check for counter-spell opportunities
        if context.enemy_casting_magic:
            if hasattr(spell, "school") and spell.school == MagicSchool.ABJURATION:
                tactical_notes.append("Can potentially counter enemy spell")
                if "COUNTERSPELL_CHANCE" not in move.effects:
                    move.effects.append("COUNTERSPELL_CHANCE")
        
        # Check for environmental interactions
        for element in context.environment_elements:
            if element == "fire" and any(effect.damage_type == DamageType.FIRE for effect in spell.effects):
                tactical_notes.append("Can spread existing fires")
                if "ENVIRONMENTAL_INTERACTION" not in move.effects:
                    move.effects.append("ENVIRONMENTAL_INTERACTION")
            
            elif element == "water" and any(effect.damage_type == DamageType.ICE for effect in spell.effects):
                tactical_notes.append("Can freeze water in the environment")
                if "ENVIRONMENTAL_INTERACTION" not in move.effects:
                    move.effects.append("ENVIRONMENTAL_INTERACTION")
        
        # Add tactical notes to description
        if tactical_notes:
            move.description = f"{original_description} ({'; '.join(tactical_notes)})"
        
        return move
    
    def suggest_tactical_spell_use(self, available_spells: List[Spell], 
                                 context: CombatContext) -> List[Dict[str, Any]]:
        """
        Suggest tactical uses of spells based on combat context.
        
        Args:
            available_spells: List of available spells
            context: Combat context information
            
        Returns:
            List of tactical suggestions
        """
        suggestions = []
        
        # Check for area spells when facing multiple enemies
        if context.enemy_count > 1:
            area_spells = [spell for spell in available_spells 
                         if any(effect.target_type in [TargetType.AREA_ENEMIES, TargetType.AREA_ALL] 
                              for effect in spell.effects)]
            
            if area_spells:
                suggestions.append({
                    "tactic": "area_damage",
                    "description": "Use area-effect spells against multiple enemies",
                    "suggested_spells": [spell.name for spell in area_spells[:3]]
                })
        
        # Check for element-terrain synergy
        terrain_synergies = {
            "water": DamageType.WATER,
            "forest": DamageType.EARTH,
            "cave": DamageType.EARTH,
            "desert": DamageType.FIRE
        }
        
        if context.terrain in terrain_synergies:
            synergy_element = terrain_synergies[context.terrain]
            synergy_spells = [spell for spell in available_spells 
                           if any(effect.damage_type == synergy_element for effect in spell.effects)]
            
            if synergy_spells:
                suggestions.append({
                    "tactic": "terrain_synergy",
                    "description": f"Use {synergy_element.name} spells that synergize with the {context.terrain} terrain",
                    "suggested_spells": [spell.name for spell in synergy_spells[:3]]
                })
        
        # Check for weather synergies
        weather_synergies = {
            "rain": DamageType.WATER,
            "storm": DamageType.LIGHTNING,
            "fog": None,  # Special case
            "snow": DamageType.ICE
        }
        
        if context.weather_conditions in weather_synergies:
            synergy_element = weather_synergies[context.weather_conditions]
            
            if synergy_element:
                synergy_spells = [spell for spell in available_spells 
                               if any(effect.damage_type == synergy_element for effect in spell.effects)]
                
                if synergy_spells:
                    suggestions.append({
                        "tactic": "weather_synergy",
                        "description": f"Use {synergy_element.name} spells enhanced by the {context.weather_conditions} weather",
                        "suggested_spells": [spell.name for spell in synergy_spells[:3]]
                    })
            elif context.weather_conditions == "fog":
                # Fog enhances stealth and illusion
                stealth_spells = [spell for spell in available_spells 
                               if hasattr(spell, "school") and spell.school == MagicSchool.ILLUSION]
                
                if stealth_spells:
                    suggestions.append({
                        "tactic": "fog_stealth",
                        "description": "Use illusion magic enhanced by the fog",
                        "suggested_spells": [spell.name for spell in stealth_spells[:3]]
                    })
        
        # Check for counter-spelling
        if context.enemy_casting_magic:
            counter_spells = [spell for spell in available_spells 
                           if hasattr(spell, "school") and spell.school == MagicSchool.ABJURATION]
            
            if counter_spells:
                suggestions.append({
                    "tactic": "counter_magic",
                    "description": "Use abjuration magic to counter enemy spellcasting",
                    "suggested_spells": [spell.name for spell in counter_spells[:3]]
                })
        
        # Check for leyline usage
        if context.nearby_leyline_strength >= 3:
            leyline_spells = [spell for spell in available_spells 
                           if MagicSource.LEYLINE in spell.magic_source_affinity]
            
            if leyline_spells:
                suggestions.append({
                    "tactic": "leyline_boost",
                    "description": f"Use leyline-powered spells boosted by the strong local leylines (strength {context.nearby_leyline_strength})",
                    "suggested_spells": [spell.name for spell in leyline_spells[:3]]
                })
        
        return suggestions
    
    def calculate_tactical_advantage(self, spell: Spell, context: CombatContext) -> float:
        """
        Calculate the tactical advantage of using a spell in the current context.
        
        Args:
            spell: The spell to evaluate
            context: Combat context information
            
        Returns:
            Tactical advantage multiplier (1.0 = neutral)
        """
        advantage = 1.0
        
        # Multi-target advantage
        if context.enemy_count > 1:
            for effect in spell.effects:
                if effect.target_type in [TargetType.AREA_ENEMIES, TargetType.AREA_ALL]:
                    advantage += 0.1 * min(context.enemy_count, 5)  # Up to 50% for 5+ enemies
        
        # Terrain advantage
        for effect in spell.effects:
            if effect.damage_type == DamageType.FIRE and context.terrain == "dry_forest":
                advantage += 0.3  # Fire in dry forest is very effective
            elif effect.damage_type == DamageType.WATER and context.terrain == "desert":
                advantage += 0.2  # Water in desert is effective
            elif effect.damage_type == DamageType.EARTH and context.terrain == "cave":
                advantage += 0.2  # Earth in cave is effective
            elif effect.damage_type == DamageType.AIR and context.terrain == "cliffs":
                advantage += 0.2  # Air on cliffs is effective
        
        # Weather advantage
        for effect in spell.effects:
            if effect.damage_type == DamageType.LIGHTNING and context.weather_conditions == "storm":
                advantage += 0.3  # Lightning during storm is very effective
            elif effect.damage_type == DamageType.WATER and context.weather_conditions == "rain":
                advantage += 0.2  # Water during rain is effective
            elif effect.damage_type == DamageType.ICE and context.weather_conditions == "snow":
                advantage += 0.2  # Ice during snow is effective
            elif effect.damage_type == DamageType.FIRE and context.weather_conditions in ["rain", "snow"]:
                advantage -= 0.2  # Fire during precipitation is less effective
        
        # Time of day advantage
        for effect in spell.effects:
            if effect.damage_type == DamageType.LIGHT and context.time_of_day == "night":
                advantage += 0.2  # Light at night is effective
            elif effect.damage_type == DamageType.DARKNESS and context.time_of_day == "day":
                advantage += 0.2  # Darkness during day is effective
        
        # Leyline advantage
        if context.nearby_leyline_strength >= 3 and MagicSource.LEYLINE in spell.magic_source_affinity:
            advantage += 0.1 * context.nearby_leyline_strength  # Up to 50% for strength 5
        
        return advantage


# ======================================================================
# 8. Magical Economy Integration
# ======================================================================

class MagicalEconomy:
    """
    System for integrating magic with economic systems.
    
    This makes magic a part of the economy with supply, demand, and services.
    """
    
    def __init__(self):
        """Initialize the magical economy system"""
        # Base prices for magical components
        self.base_component_prices = {
            "ley_crystal": 50,
            "crimson_residue": 100,
            "spiritbloom": 30,
            "void_shard": 150,
            "stormforge_iron": 75,
            "phoenix_feather": 200,
            "dragon_scale": 300,
            "unicorn_horn": 500,
            "mandrake_root": 40,
            "moonflower": 60,
            "sunstone": 80,
            "shadow_essence": 120,
            "mermaid_tear": 150,
            "fairy_dust": 90,
            "troll_blood": 70,
            "ghost_ectoplasm": 110
        }
        
        # Component rarity tiers
        self.component_rarity = {
            "common": ["ley_crystal", "spiritbloom", "stormforge_iron", "mandrake_root", "moonflower"],
            "uncommon": ["crimson_residue", "sunstone", "fairy_dust", "troll_blood"],
            "rare": ["void_shard", "phoenix_feather", "shadow_essence", "ghost_ectoplasm"],
            "very_rare": ["dragon_scale", "unicorn_horn", "mermaid_tear"]
        }
        
        # Service base prices
        self.service_base_prices = {
            "identify_magic": 20,
            "remove_curse": 100,
            "enchant_item": 200,
            "brew_potion": 50,
            "scry_location": 150,
            "teleportation": 300,
            "fortune_telling": 30,
            "magical_healing": 80,
            "purification_ritual": 120,
            "mana_heart_development": 500
        }
    
    def calculate_component_prices(self, location: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate component prices based on location factors.
        
        Args:
            location: Location information
            
        Returns:
            Dictionary of component prices
        """
        # Start with base prices
        prices = self.base_component_prices.copy()
        
        # Calculate location modifier
        location_modifier = 1.0
        
        # Remoteness increases prices
        remoteness = location.get("remoteness", 0.0)
        if remoteness > 0.7:
            location_modifier += 0.5  # 50% markup in very remote areas
        elif remoteness > 0.4:
            location_modifier += 0.2  # 20% markup in somewhat remote areas
        
        # Large settlements decrease prices
        settlement_size = location.get("settlement_size", 0)
        if settlement_size >= 4:  # Large city
            location_modifier -= 0.2
        elif settlement_size >= 3:  # Town
            location_modifier -= 0.1
        
        # Magical academies decrease prices
        if location.get("has_magical_academy", False):
            location_modifier -= 0.15
        
        # Active mages increase prices (competition)
        active_mages = location.get("active_mages", 0)
        if active_mages >= 5:
            location_modifier += 0.2
        elif active_mages >= 3:
            location_modifier += 0.1
        
        # Apply general modifier
        prices = {item: int(price * location_modifier) for item, price in prices.items()}
        
        # Apply specific regional adjustments
        region_type = location.get("region_type", "")
        
        if region_type == "forest":
            # Forests have more plant-based components
            prices["spiritbloom"] = int(prices["spiritbloom"] * 0.7)
            prices["mandrake_root"] = int(prices["mandrake_root"] * 0.7)
            prices["moonflower"] = int(prices["moonflower"] * 0.8)
        
        elif region_type == "mountains":
            # Mountains have more mineral components
            prices["ley_crystal"] = int(prices["ley_crystal"] * 0.8)
            prices["stormforge_iron"] = int(prices["stormforge_iron"] * 0.7)
            prices["sunstone"] = int(prices["sunstone"] * 0.8)
        
        elif region_type == "coastal":
            # Coastal areas have more water-related components
            prices["mermaid_tear"] = int(prices["mermaid_tear"] * 0.7)
        
        # Crimson Dissonance sites have more crimson residue
        if "crimson_dissonance_site" in location.get("historical_events", []):
            prices["crimson_residue"] = int(prices["crimson_residue"] * 0.6)
        
        # Strong leylines mean more ley crystals
        if location.get("leyline_strength", 0) >= 4:
            prices["ley_crystal"] = int(prices["ley_crystal"] * 0.5)
        
        return prices
    
    def generate_magical_services(self, npc: NPC, location: Dict[str, Any]) -> List[MagicalService]:
        """
        Generate magical services offered by an NPC.
        
        Args:
            npc: The NPC offering services
            location: Location information
            
        Returns:
            List of magical services
        """
        services = []
        
        # Determine what services the NPC can offer based on their magic tier
        if npc.magic_tier == MagicTier.ARCANE_MASTERY:
            # High-tier mages can offer most services
            potential_services = [
                "identify_magic", "remove_curse", "enchant_item", "scry_location",
                "teleportation", "magical_healing", "purification_ritual", "mana_heart_development"
            ]
        elif npc.magic_tier == MagicTier.MANA_INFUSION:
            # Mid-tier mages can offer many services
            potential_services = [
                "identify_magic", "enchant_item", "brew_potion", "magical_healing"
            ]
        else:
            # Low-tier mages can offer basic services
            potential_services = [
                "identify_magic", "fortune_telling", "brew_potion"
            ]
        
        # Filter based on known schools
        if MagicSchool.DIVINATION in npc.known_schools:
            if "scry_location" not in potential_services and npc.magic_tier.value >= MagicTier.MANA_INFUSION.value:
                potential_services.append("scry_location")
            if "fortune_telling" not in potential_services:
                potential_services.append("fortune_telling")
        
        if MagicSchool.ABJURATION in npc.known_schools:
            if "remove_curse" not in potential_services and npc.magic_tier.value >= MagicTier.MANA_INFUSION.value:
                potential_services.append("remove_curse")
        
        if MagicSchool.ENCHANTMENT in npc.known_schools:
            if "enchant_item" not in potential_services and npc.magic_tier.value >= MagicTier.MANA_INFUSION.value:
                potential_services.append("enchant_item")
        
        if MagicSchool.RESTORATION in npc.known_schools:
            if "magical_healing" not in potential_services:
                potential_services.append("magical_healing")
            if "purification_ritual" not in potential_services and npc.magic_tier == MagicTier.ARCANE_MASTERY:
                potential_services.append("purification_ritual")
        
        # Create service objects
        for service_id in potential_services:
            base_price = self.service_base_prices.get(service_id, 50)
            
            # Adjust price based on location
            location_modifier = 1.0
            
            # Remoteness increases prices
            remoteness = location.get("remoteness", 0.0)
            if remoteness > 0.5:
                location_modifier += 0.3
            
            # Competition decreases prices
            active_mages = location.get("active_mages", 0)
            if active_mages >= 5:
                location_modifier -= 0.2
            
            # Calculate final price
            price = int(base_price * location_modifier)
            
            # Create service with appropriate requirements
            domain_requirements = []
            reputation_requirement = 0
            
            if service_id == "enchant_item":
                domain_requirements = [
                    DomainRequirement(domain=Domain.CRAFT, minimum_value=3)
                ]
                cost_per_level = 50
            elif service_id == "mana_heart_development":
                domain_requirements = [
                    DomainRequirement(domain=Domain.SPIRIT, minimum_value=3),
                    DomainRequirement(domain=Domain.MIND, minimum_value=3)
                ]
                reputation_requirement = 20
                cost_per_level = 0
            elif service_id == "remove_curse":
                domain_requirements = [
                    DomainRequirement(domain=Domain.SPIRIT, minimum_value=2)
                ]
                cost_per_level = 50
            else:
                cost_per_level = 0
            
            # Create the service
            service = MagicalService(
                id=service_id,
                name=self._get_service_name(service_id),
                description=self._get_service_description(service_id),
                base_cost=price,
                cost_per_level=cost_per_level,
                reputation_requirement=reputation_requirement,
                domain_requirements=domain_requirements
            )
            
            services.append(service)
        
        return services
    
    def _get_service_name(self, service_id: str) -> str:
        """
        Get a display name for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Display name for the service
        """
        service_names = {
            "identify_magic": "Magical Identification",
            "remove_curse": "Curse Removal",
            "enchant_item": "Item Enchantment",
            "brew_potion": "Potion Brewing",
            "scry_location": "Location Scrying",
            "teleportation": "Teleportation Service",
            "fortune_telling": "Fortune Telling",
            "magical_healing": "Magical Healing",
            "purification_ritual": "Purification Ritual",
            "mana_heart_development": "Mana Heart Development"
        }
        
        return service_names.get(service_id, service_id.replace("_", " ").title())
    
    def _get_service_description(self, service_id: str) -> str:
        """
        Get a description for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Description of the service
        """
        service_descriptions = {
            "identify_magic": "Identify the magical properties of an item or phenomenon",
            "remove_curse": "Remove a curse or malignant enchantment from a person or item",
            "enchant_item": "Imbue an item with magical properties",
            "brew_potion": "Create a magical potion with various effects",
            "scry_location": "Magically view a distant location or person",
            "teleportation": "Instantly transport to a known location",
            "fortune_telling": "Glimpse possible futures and portents",
            "magical_healing": "Accelerate healing beyond natural means",
            "purification_ritual": "Cleanse a person, item, or area of magical corruption",
            "mana_heart_development": "Guide the development of a Mana Heart for aspiring mages"
        }
        
        return service_descriptions.get(service_id, "A magical service")


# ======================================================================
# 9. AI GM Magic Integration
# ======================================================================

class AIGMMagicIntegration:
    """
    System for enhancing the AI GM with magical context.
    
    This ensures the AI GM can incorporate magic meaningfully into narratives.
    """
    
    def __init__(self):
        """Initialize the AI GM magic integration system"""
        # Magic-themed narrative elements
        self.magical_aura_descriptions = {
            "none": [
                "They have no discernible magical aura.",
                "Their presence feels entirely mundane.",
                "No hint of magical energy surrounds them."
            ],
            "novice": [
                "A faint magical aura surrounds them, barely perceptible.",
                "They carry the slightest hint of magical potential.",
                "A whisper of arcane energy clings to their form."
            ],
            "developing": [
                "A modest magical aura surrounds them, visible to those with sensitivity.",
                "They emanate a steady flow of magical energy.",
                "Their presence ripples with controlled arcane potential."
            ],
            "mature": [
                "A strong magical aura pulses around them rhythmically.",
                "Waves of arcane energy flow from their Mana Heart.",
                "Their magical presence is immediately noticeable to anyone sensitive to such things."
            ],
            "transcendent": [
                "Reality itself seems to bend slightly in their presence.",
                "An overwhelming aura of power radiates from them in waves.",
                "The very air around them shimmers with magical energy."
            ],
            "dark_corruption": [
                "Tendrils of dark energy writhe around them like shadowy snakes.",
                "A sickly, corrupted magical aura clings to them like a miasma.",
                "Their magic feels tainted, like spoiled wine that was once sweet."
            ],
            "elemental_fire": [
                "Heat shimmers around them even in cool environments.",
                "Their magical aura flickers like flames in a breeze.",
                "The scent of smoke and charcoal accompanies their magical presence."
            ],
            "elemental_water": [
                "A slight dampness seems to follow them, even in dry areas.",
                "Their magical aura flows and ebbs like ocean tides.",
                "The air around them feels cool and refreshing, like morning mist."
            ],
            "elemental_earth": [
                "Their footsteps feel unnaturally solid and grounded.",
                "Their magical aura has the steady, immovable quality of stone.",
                "Plants seem to subtly reach toward them as they pass."
            ],
            "elemental_air": [
                "Small breezes stir around them even in still air.",
                "Their magical aura shifts and changes like wind patterns.",
                "Their presence brings a subtle freshness to the air."
            ]
        }
        
        self.magical_environmental_effects = {
            "strong_leyline": [
                "The air tingles with magical energy from the strong leylines.",
                "Sensitive individuals might notice their hair standing on end from the ambient magic.",
                "Small, spontaneous magical phenomena occasionally manifest in the area."
            ],
            "corrupted_magic": [
                "Plants grow twisted and unnatural in this magically corrupted area.",
                "The air feels heavy and oppressive, tainted by corrupt magic.",
                "Small animals avoid this place, sensing the wrongness in the magical environment."
            ],
            "recent_spellcasting": [
                "Traces of recent spellcasting linger in the air like the scent after rainfall.",
                "A trained mage would recognize the residual energy from recent magic use.",
                "The ambient magic has been disturbed, like ripples in a pond."
            ],
            "magical_convergence": [
                "Multiple leylines converge here, creating a powerful nexus of magical energy.",
                "The veil between worlds feels thin in this place of magical convergence.",
                "Even those without magical training might feel a sense of wonder or unease here."
            ],
            "wild_magic": [
                "Magic behaves unpredictably here, with random minor effects manifesting.",
                "Colors seem more vivid, sounds more clear in this wild magic zone.",
                "The laws of nature and magic alike seem to bend and flex here."
            ]
        }
        
        self.magical_story_hooks = {
            "crimson_dissonance": [
                "Traces of ancient war magic from the Crimson Dissonance have been discovered nearby.",
                "A sealed vault containing artifacts from the Crimson Dissonance era has begun to crack open.",
                "Dreams of blood-red skies and screaming magic have plagued the locals recently."
            ],
            "mana_heart_development": [
                "A prodigy has spontaneously developed a Mana Heart without training, causing concern.",
                "The local magical academy is recruiting those with potential to develop Mana Hearts.",
                "An experimental ritual claims to fast-track Mana Heart development, but at what cost?"
            ],
            "magical_corruption": [
                "Wildlife has been spotted with strange mutations, suggesting magical corruption.",
                "Corrupted mages have been seen lurking at the edges of civilization.",
                "A once-pristine sacred grove now exudes a sickly magical aura."
            ],
            "leyline_disruption": [
                "The local leylines have shifted, causing unpredictable magical effects.",
                "Magical devices have been malfunctioning since the recent leyline disruption.",
                "The disrupted leylines have attracted the attention of magical researchers and opportunists alike."
            ],
            "forbidden_magic": [
                "Rumors spread of someone practicing forbidden magic from the Crimson Dissonance era.",
                "Ancient tomes containing dangerous magical knowledge have been stolen.",
                "Strange magical signatures have been detected that match no known school of magic."
            ]
        }
    
    def enhance_narrative_with_magic(self, base_context: Dict[str, Any], 
                                   magic_profile: Any) -> Dict[str, Any]:
        """
        Enhance the AI GM narrative context with magical elements.
        
        Args:
            base_context: Base narrative context
            magic_profile: Character's magic profile
            
        Returns:
            Enhanced narrative context
        """
        enhanced_context = base_context.copy()
        
        # Add character aura description
        if hasattr(magic_profile, "corruption_level") and magic_profile.corruption_level >= 30:
            enhanced_context["character_aura"] = "dark_corruption"
            enhanced_context["aura_description"] = random.choice(self.magical_aura_descriptions["dark_corruption"])
        elif hasattr(magic_profile, "has_mana_heart"):
            if not magic_profile.has_mana_heart:
                if hasattr(magic_profile, "ley_energy_sensitivity") and magic_profile.ley_energy_sensitivity >= 3:
                    enhanced_context["character_aura"] = "novice"
                    enhanced_context["aura_description"] = random.choice(self.magical_aura_descriptions["novice"])
                else:
                    enhanced_context["character_aura"] = "none"
                    enhanced_context["aura_description"] = random.choice(self.magical_aura_descriptions["none"])
            else:
                # Determine Mana Heart stage based on max mana
                if magic_profile.mana_max >= 100:
                    enhanced_context["character_aura"] = "transcendent"
                    enhanced_context["aura_description"] = random.choice(self.magical_aura_descriptions["transcendent"])
                elif magic_profile.mana_max >= 60:
                    enhanced_context["character_aura"] = "mature"
                    enhanced_context["aura_description"] = random.choice(self.magical_aura_descriptions["mature"])
                else:
                    enhanced_context["character_aura"] = "developing"
                    enhanced_context["aura_description"] = random.choice(self.magical_aura_descriptions["developing"])
        
        # Add elemental aura if appropriate
        if hasattr(magic_profile, "attunements"):
            for attunement in magic_profile.attunements:
                if attunement == "elemental_attunement":
                    element = "fire"  # Default
                    if hasattr(magic_profile, "primary_element"):
                        element = magic_profile.primary_element.lower()
                    
                    aura_key = f"elemental_{element}"
                    if aura_key in self.magical_aura_descriptions:
                        enhanced_context["elemental_aura"] = element
                        enhanced_context["elemental_aura_description"] = random.choice(
                            self.magical_aura_descriptions[aura_key]
                        )
                elif attunement == "void_touched":
                    enhanced_context["void_aura"] = True
                    enhanced_context["void_aura_description"] = "A subtle darkness clings to their aura, like a void hungry for light."
        
        # Add NPC reactions based on character's magical nature
        if "character_aura" in enhanced_context:
            aura = enhanced_context["character_aura"]
            if aura == "transcendent":
                enhanced_context["npc_reactions"] = enhanced_context.get("npc_reactions", []) + [
                    "awe", "deference", "wariness"
                ]
            elif aura == "dark_corruption":
                enhanced_context["npc_reactions"] = enhanced_context.get("npc_reactions", []) + [
                    "fear", "suspicion", "avoidance"
                ]
            elif aura in ["mature", "developing"]:
                enhanced_context["npc_reactions"] = enhanced_context.get("npc_reactions", []) + [
                    "respect", "curiosity"
                ]
        
        # Add environmental magical effects if location has magical properties
        location = base_context.get("location", {})
        if location:
            if location.get("leyline_strength", 0) >= 4:
                enhanced_context["magical_environment"] = "strong_leyline"
                enhanced_context["environmental_description"] = random.choice(
                    self.magical_environmental_effects["strong_leyline"]
                )
            elif location.get("corruption_level", 0) >= 3:
                enhanced_context["magical_environment"] = "corrupted_magic"
                enhanced_context["environmental_description"] = random.choice(
                    self.magical_environmental_effects["corrupted_magic"]
                )
            elif location.get("recent_spellcasting", False):
                enhanced_context["magical_environment"] = "recent_spellcasting"
                enhanced_context["environmental_description"] = random.choice(
                    self.magical_environmental_effects["recent_spellcasting"]
                )
        
        # Add magical hooks based on character and world state
        potential_hooks = []
        
        if hasattr(magic_profile, "corruption_level") and magic_profile.corruption_level >= 20:
            potential_hooks.append("magical_corruption")
        
        if not hasattr(magic_profile, "has_mana_heart") or not magic_profile.has_mana_heart:
            potential_hooks.append("mana_heart_development")
        
        if "crimson_dissonance_site" in location.get("historical_events", []):
            potential_hooks.append("crimson_dissonance")
        
        if location.get("leyline_disruption", False):
            potential_hooks.append("leyline_disruption")
        
        # Add 1-2 potential magical hooks
        if potential_hooks:
            hook_count = min(2, len(potential_hooks))
            selected_hooks = random.sample(potential_hooks, hook_count)
            enhanced_context["magical_hooks"] = []
            
            for hook in selected_hooks:
                if hook in self.magical_story_hooks:
                    hook_text = random.choice(self.magical_story_hooks[hook])
                    enhanced_context["magical_hooks"].append({
                        "type": hook,
                        "description": hook_text
                    })
        
        return enhanced_context
    
    def generate_magical_event(self, location: Dict[str, Any], 
                             magic_profile: Any = None) -> Dict[str, Any]:
        """
        Generate a random magical event appropriate to a location.
        
        Args:
            location: Location information
            magic_profile: Optional character magic profile
            
        Returns:
            Dictionary describing the magical event
        """
        # Determine event category based on location properties
        event_categories = ["minor", "ambient"]
        
        if location.get("leyline_strength", 0) >= 4:
            event_categories.extend(["leyline", "major"])
        
        if location.get("corruption_level", 0) >= 3:
            event_categories.extend(["corruption", "wild"])
        
        if "crimson_dissonance_site" in location.get("historical_events", []):
            event_categories.extend(["historical", "corruption"])
        
        if location.get("magical_academy", False):
            event_categories.extend(["academic", "controlled"])
        
        # Character's magical nature can influence events
        if magic_profile:
            if hasattr(magic_profile, "corruption_level") and magic_profile.corruption_level >= 30:
                event_categories.extend(["corruption", "void"])
            
            if hasattr(magic_profile, "has_mana_heart") and magic_profile.has_mana_heart:
                if magic_profile.mana_max >= 60:
                    event_categories.append("resonance")
        
        # Select an event category
        event_category = random.choice(event_categories)
        
        # Generate event based on category
        event = {
            "category": event_category,
            "intensity": random.randint(1, 5),  # 1-5 scale
            "duration": random.choice(["momentary", "brief", "sustained", "lasting"])
        }
        
        # Generate description and effects based on category
        if event_category == "leyline":
            event["title"] = "Leyline Surge"
            event["description"] = "The local leylines pulse with unusual energy, creating visible patterns in the air."
            event["effects"] = ["Spells cast using leyline energy are 50% more powerful for 1 hour", 
                              "Sensitive individuals may experience visions or heightened awareness"]
        
        elif event_category == "corruption":
            event["title"] = "Corruption Manifestation"
            event["description"] = "Dark, corrupted magic seeps into the physical world, creating unsettling phenomena."
            event["effects"] = ["Small objects may animate briefly with malevolent intent", 
                              "Those with magical sensitivity feel a crawling sensation on their skin"]
        
        elif event_category == "historical":
            event["title"] = "Echo of the Dissonance"
            event["description"] = "A memory of the Crimson Dissonance briefly manifests, showing ghostly images of the past."
            event["effects"] = ["Those present may gain fragmentary insights into historical events", 
                              "Emotional residue from the past may affect people's moods"]
        
        elif event_category == "wild":
            event["title"] = "Wild Magic Surge"
            event["description"] = "Magic behaves unpredictably, creating random minor effects in the area."
            event["effects"] = ["Small objects may float or change color temporarily", 
                              "Spells cast during this time have unpredictable side effects"]
        
        elif event_category == "resonance":
            event["title"] = "Mana Heart Resonance"
            event["description"] = "The character's Mana Heart resonates with local magical energies."
            event["effects"] = ["Temporarily enhanced magical perception", 
                              "Easier to draw energy from local sources"]
        
        elif event_category == "void":
            event["title"] = "Void Intrusion"
            event["description"] = "A small tear in reality briefly allows void energies to seep through."
            event["effects"] = ["Shadows deepen and seem to move independently", 
                              "Those with corruption may hear whispers from beyond"]
        
        else:  # minor/ambient
            event["title"] = "Magical Ambience"
            event["description"] = "Subtle magical effects manifest in the environment."
            event["effects"] = ["Flowers might bloom out of season", 
                              "Small animals behave unusually"]
        
        return event


# ======================================================================
# Main Integration Functions
# ======================================================================

def create_advanced_magic_features(magic_system) -> Dict[str, Any]:
    """
    Create and return all advanced magic feature systems.
    
    Args:
        magic_system: The magic system instance
        
    Returns:
        Dictionary containing the advanced feature systems
    """
    # Initialize each system
    environmental_resonance = EnvironmentalMagicResonance()
    mana_heart_evolution = ManaHeartEvolution()
    spell_combination = SpellCombinationSystem(magic_system)
    spell_crafting = SpellCraftingSystem(magic_system)
    magical_consequences = MagicalConsequenceSystem()
    npc_magic_relationship = NPCMagicRelationship()
    domain_magic_synergy = DomainMagicSynergy()
    tactical_magic_combat = TacticalMagicCombat(magic_system)
    magical_economy = MagicalEconomy()
    ai_gm_magic = AIGMMagicIntegration()
    
    return {
        "environmental_resonance": environmental_resonance,
        "mana_heart_evolution": mana_heart_evolution,
        "spell_combination": spell_combination,
        "spell_crafting": spell_crafting,
        "magical_consequences": magical_consequences,
        "npc_magic_relationship": npc_magic_relationship,
        "domain_magic_synergy": domain_magic_synergy,
        "tactical_magic_combat": tactical_magic_combat,
        "magical_economy": magical_economy,
        "ai_gm_magic": ai_gm_magic
    }


# Initialize advanced magic features with the existing magic system
from .magic_system import magic_system
advanced_magic_features = create_advanced_magic_features(magic_system)