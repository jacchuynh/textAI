"""
Magic System Module

This module implements the core magic system functionality including
spell mechanics, magic user profiles, and magical effects.
"""

import random
import time
from enum import Enum, auto
from typing import Dict, List, Set, Any, Optional, Tuple


class Domain(Enum):
    """Magic domains that spells can belong to."""
    ARCANE = auto()
    FIRE = auto()
    WATER = auto()
    EARTH = auto()
    AIR = auto()
    LIGHT = auto()
    SHADOW = auto()
    NATURE = auto()
    LIFE = auto()
    DEATH = auto()
    MIND = auto()
    TIME = auto()
    CHAOS = auto()
    ORDER = auto()


class DamageType(Enum):
    """Types of damage that spells can inflict."""
    PHYSICAL = auto()
    FIRE = auto()
    COLD = auto()
    LIGHTNING = auto()
    ACID = auto()
    POISON = auto()
    ARCANE = auto()
    NECROTIC = auto()
    RADIANT = auto()
    PSYCHIC = auto()


class EffectType(Enum):
    """Types of effects that spells can produce."""
    DAMAGE = auto()
    HEALING = auto()
    BUFF = auto()
    DEBUFF = auto()
    CONTROL = auto()
    UTILITY = auto()
    SUMMON = auto()
    TRANSFORM = auto()
    WARDING = auto()
    ILLUSION = auto()
    DIVINATION = auto()
    TELEPORTATION = auto()


class MagicTier(Enum):
    """Tiers of magic power."""
    LESSER = auto()
    MODERATE = auto()
    GREATER = auto()
    EPIC = auto()
    LEGENDARY = auto()


class MagicUser:
    """
    Represents a character with magical abilities.
    """
    def __init__(self, 
                 id: str, 
                 name: str, 
                 level: int, 
                 mana_max: float, 
                 mana_current: float, 
                 mana_regen_rate: float,
                 primary_domains: List[Domain],
                 secondary_domains: List[Domain],
                 known_spells: Set[str],
                 magic_skills: Dict[str, float] = None):
        """Initialize a magic user."""
        self.id = id
        self.name = name
        self.level = level
        self.mana_max = mana_max
        self.mana_current = mana_current
        self.mana_regen_rate = mana_regen_rate
        self.primary_domains = primary_domains
        self.secondary_domains = secondary_domains
        self.known_spells = known_spells
        self.magic_skills = magic_skills or {
            "spellcasting": 1.0,
            "concentration": 1.0,
            "magical_knowledge": 1.0,
            "mana_control": 1.0
        }
        self.active_effects = {}
        self.cooldowns = {}
        self.last_cast_time = {}


class Spell:
    """
    Represents a magical spell that can be cast.
    """
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 domains: List[Domain],
                 damage_types: List[DamageType],
                 effect_types: List[EffectType],
                 mana_cost: float,
                 casting_time: float,
                 cooldown: float,
                 base_power: float,
                 level_req: int,
                 tier: MagicTier,
                 targeting_type: str,
                 range_max: float,
                 duration: float = 0.0,
                 components: List[str] = None,
                 tags: List[str] = None):
        """Initialize a spell."""
        self.id = id
        self.name = name
        self.description = description
        self.domains = domains
        self.damage_types = damage_types
        self.effect_types = effect_types
        self.mana_cost = mana_cost
        self.casting_time = casting_time
        self.cooldown = cooldown
        self.base_power = base_power
        self.level_req = level_req
        self.tier = tier
        self.targeting_type = targeting_type  # single, area, self, etc.
        self.range_max = range_max
        self.duration = duration
        self.components = components or []
        self.tags = tags or []


class MagicSystem:
    """
    Core magic system that manages spells, magic users, and magical effects.
    """
    def __init__(self):
        """Initialize the magic system."""
        self.spells = {}
        self.magic_users = {}
        self.location_magic_profiles = {}
        self.active_effects = {}
        self.last_update_time = time.time()
    
    def register_spell(self, spell: Spell) -> None:
        """Register a spell with the magic system."""
        self.spells[spell.id] = spell
    
    def register_magic_user(self, magic_user: MagicUser) -> None:
        """Register a magic user with the magic system."""
        self.magic_users[magic_user.id] = magic_user
    
    def register_location_magic(self, location_id: str, magic_profile: Dict[str, Any]) -> None:
        """Register magic properties for a location."""
        self.location_magic_profiles[location_id] = magic_profile
    
    def get_spell(self, spell_id: str) -> Optional[Spell]:
        """Get a spell by its ID."""
        return self.spells.get(spell_id)
    
    def get_magic_user(self, user_id: str) -> Optional[MagicUser]:
        """Get a magic user by their ID."""
        return self.magic_users.get(user_id)
    
    def get_location_magic(self, location_id: str) -> Dict[str, Any]:
        """Get magic properties for a location."""
        return self.location_magic_profiles.get(location_id, {
            "mana_density": 1.0,
            "domain_affinities": {},
            "magical_properties": []
        })
    
    def update(self, current_time: float) -> None:
        """
        Update the magic system's state.
        
        This handles mana regeneration, effect durations, cooldowns, etc.
        """
        # Calculate time delta since last update
        delta_time = current_time - self.last_update_time
        
        # Update magic users
        for user_id, user in self.magic_users.items():
            # Regenerate mana
            mana_regen = user.mana_regen_rate * delta_time
            user.mana_current = min(user.mana_max, user.mana_current + mana_regen)
            
            # Update cooldowns
            expired_cooldowns = []
            for spell_id, cooldown_end in user.cooldowns.items():
                if current_time >= cooldown_end:
                    expired_cooldowns.append(spell_id)
            
            # Remove expired cooldowns
            for spell_id in expired_cooldowns:
                del user.cooldowns[spell_id]
            
            # Update active effects
            expired_effects = []
            for effect_id, effect in user.active_effects.items():
                if effect["end_time"] <= current_time:
                    expired_effects.append(effect_id)
            
            # Remove expired effects
            for effect_id in expired_effects:
                del user.active_effects[effect_id]
        
        # Update active effects in the world
        expired_world_effects = []
        for effect_id, effect in self.active_effects.items():
            if effect["end_time"] <= current_time:
                expired_world_effects.append(effect_id)
        
        # Remove expired world effects
        for effect_id in expired_world_effects:
            del self.active_effects[effect_id]
        
        # Update last update time
        self.last_update_time = current_time
    
    def cast_spell(self, 
                  caster_id: str, 
                  spell_id: str, 
                  target_id: Optional[str] = None,
                  location_id: Optional[str] = None,
                  current_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Cast a spell with the given parameters.
        
        Args:
            caster_id: ID of the magic user casting the spell
            spell_id: ID of the spell being cast
            target_id: ID of the target (creature, object, location)
            location_id: ID of the location where the spell is being cast
            current_time: Current game time
            
        Returns:
            A dictionary with the results of the spell casting
        """
        # Use current time if not provided
        if current_time is None:
            current_time = time.time()
        
        # Update magic system
        self.update(current_time)
        
        # Get caster and spell
        caster = self.get_magic_user(caster_id)
        spell = self.get_spell(spell_id)
        
        # Validate caster and spell
        if not caster:
            return {"success": False, "message": f"Magic user {caster_id} not found"}
        
        if not spell:
            return {"success": False, "message": f"Spell {spell_id} not found"}
        
        # Check if caster knows the spell
        if spell_id not in caster.known_spells:
            return {"success": False, "message": f"{caster.name} doesn't know {spell.name}"}
        
        # Check cooldown
        if spell_id in caster.cooldowns and caster.cooldowns[spell_id] > current_time:
            remaining_cooldown = caster.cooldowns[spell_id] - current_time
            return {
                "success": False, 
                "message": f"{spell.name} is on cooldown for {remaining_cooldown:.1f} more seconds"
            }
        
        # Check mana cost
        if caster.mana_current < spell.mana_cost:
            return {
                "success": False, 
                "message": f"Not enough mana to cast {spell.name}. Need {spell.mana_cost}, have {caster.mana_current}"
            }
        
        # Check level requirement
        if caster.level < spell.level_req:
            return {
                "success": False, 
                "message": f"{spell.name} requires level {spell.level_req}, but {caster.name} is only level {caster.level}"
            }
        
        # Consume mana
        caster.mana_current -= spell.mana_cost
        
        # Set cooldown
        caster.cooldowns[spell_id] = current_time + spell.cooldown
        
        # Record cast time
        caster.last_cast_time[spell_id] = current_time
        
        # Calculate spell power based on caster and location
        spell_power = self._calculate_spell_power(caster, spell, location_id)
        
        # Generate effects
        effects = self._generate_spell_effects(caster, spell, spell_power, target_id, location_id, current_time)
        
        # Return result
        return {
            "success": True,
            "message": f"{caster.name} casts {spell.name}",
            "caster_id": caster_id,
            "spell_id": spell_id,
            "target_id": target_id,
            "location_id": location_id,
            "cast_time": current_time,
            "mana_cost": spell.mana_cost,
            "spell_power": spell_power,
            "effects": effects
        }
    
    def _calculate_spell_power(self, 
                              caster: MagicUser, 
                              spell: Spell, 
                              location_id: Optional[str] = None) -> float:
        """
        Calculate the power of a spell based on caster and environmental factors.
        
        Args:
            caster: The magic user casting the spell
            spell: The spell being cast
            location_id: The location where the spell is being cast
            
        Returns:
            The calculated spell power
        """
        # Base power from spell
        power = spell.base_power
        
        # Caster level modifier
        power *= (1.0 + (caster.level * 0.1))
        
        # Skill modifiers
        spellcasting_skill = caster.magic_skills.get("spellcasting", 1.0)
        mana_control_skill = caster.magic_skills.get("mana_control", 1.0)
        
        power *= (1.0 + ((spellcasting_skill + mana_control_skill) * 0.05))
        
        # Domain affinity modifiers
        for domain in spell.domains:
            if domain in caster.primary_domains:
                power *= 1.25  # 25% bonus for primary domains
            elif domain in caster.secondary_domains:
                power *= 1.1   # 10% bonus for secondary domains
        
        # Location modifiers
        if location_id:
            location_magic = self.get_location_magic(location_id)
            mana_density = location_magic.get("mana_density", 1.0)
            domain_affinities = location_magic.get("domain_affinities", {})
            
            # Mana density affects overall power
            power *= mana_density
            
            # Domain affinities in the location
            for domain in spell.domains:
                domain_affinity = domain_affinities.get(domain.name, 1.0)
                power *= domain_affinity
        
        # Random variation (±10%)
        variation = random.uniform(0.9, 1.1)
        power *= variation
        
        return power
    
    def _generate_spell_effects(self,
                               caster: MagicUser,
                               spell: Spell,
                               spell_power: float,
                               target_id: Optional[str],
                               location_id: Optional[str],
                               current_time: float) -> List[Dict[str, Any]]:
        """
        Generate the effects of a spell.
        
        Args:
            caster: The magic user casting the spell
            spell: The spell being cast
            spell_power: The calculated power of the spell
            target_id: ID of the target
            location_id: ID of the location
            current_time: Current game time
            
        Returns:
            A list of effect dictionaries
        """
        effects = []
        
        # Process each effect type
        for effect_type in spell.effect_types:
            effect = {
                "effect_id": f"{spell.id}_{effect_type.name.lower()}_{current_time}",
                "effect_type": effect_type.name,
                "caster_id": caster.id,
                "spell_id": spell.id,
                "target_id": target_id,
                "location_id": location_id,
                "start_time": current_time,
                "end_time": current_time + spell.duration if spell.duration > 0 else current_time,
                "potency": 0.0,
                "description": ""
            }
            
            # Calculate effect potency based on effect type
            if effect_type == EffectType.DAMAGE:
                effect["potency"] = spell_power
                
                # Get first damage type for description
                damage_type = spell.damage_types[0].name if spell.damage_types else "unknown"
                effect["description"] = f"Deals {effect['potency']:.1f} {damage_type.lower()} damage"
                
            elif effect_type == EffectType.HEALING:
                effect["potency"] = spell_power
                effect["description"] = f"Heals for {effect['potency']:.1f} health"
                
            elif effect_type == EffectType.BUFF:
                effect["potency"] = spell_power * 0.2  # Buffs are typically 20% of damage
                effect["description"] = f"Increases effectiveness by {effect['potency']:.1f}"
                
            elif effect_type == EffectType.DEBUFF:
                effect["potency"] = spell_power * 0.2  # Debuffs similar to buffs
                effect["description"] = f"Decreases effectiveness by {effect['potency']:.1f}"
                
            elif effect_type == EffectType.CONTROL:
                effect["potency"] = spell_power * 0.1  # Control effects are weaker
                effect["duration"] = spell.duration
                effect["description"] = f"Controls target for {spell.duration:.1f} seconds"
                
            else:
                # Generic effect for other types
                effect["potency"] = spell_power
                effect["description"] = f"Applies {effect_type.name.lower()} effect"
            
            effects.append(effect)
            
            # If the spell has a duration, add to active effects
            if spell.duration > 0:
                if target_id and target_id in self.magic_users:
                    # Add to target's active effects
                    target = self.magic_users[target_id]
                    target.active_effects[effect["effect_id"]] = effect
                else:
                    # Add to world effects
                    self.active_effects[effect["effect_id"]] = effect
        
        return effects