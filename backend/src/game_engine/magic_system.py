"""
Magic System Core Module

This module defines the core components and functionality of the magic system.
It serves as the foundation for all magic-related features in the game.
"""

from enum import Enum, auto
from typing import Dict, List, Set, Optional, Any, Tuple, Union
import random
import math
import uuid
from datetime import datetime, timedelta

# --- Enumerations ---

class Domain(Enum):
    """Magic domains representing different types of magical specialization."""
    ARCANE = auto()
    ELEMENTAL = auto()
    NATURAL = auto()
    DIVINE = auto()
    SHADOW = auto()
    BLOOD = auto()
    MIND = auto()
    SPIRIT = auto()
    CHAOS = auto()
    ORDER = auto()
    VOID = auto()
    TEMPORAL = auto()
    
    @classmethod
    def get_opposing_domains(cls) -> Dict['Domain', 'Domain']:
        """Return pairs of opposing domains."""
        return {
            cls.ARCANE: cls.NATURAL,
            cls.NATURAL: cls.ARCANE,
            cls.DIVINE: cls.SHADOW,
            cls.SHADOW: cls.DIVINE,
            cls.ORDER: cls.CHAOS,
            cls.CHAOS: cls.ORDER,
            cls.MIND: cls.SPIRIT,
            cls.SPIRIT: cls.MIND,
            cls.BLOOD: cls.VOID,
            cls.VOID: cls.BLOOD,
            cls.ELEMENTAL: cls.TEMPORAL,
            cls.TEMPORAL: cls.ELEMENTAL
        }
    
    @classmethod
    def get_domain_synergies(cls) -> Dict[Tuple['Domain', 'Domain'], float]:
        """Return synergy levels between domains (0.0-2.0)."""
        return {
            (cls.ARCANE, cls.TEMPORAL): 1.8,
            (cls.ARCANE, cls.ELEMENTAL): 1.5,
            (cls.ARCANE, cls.MIND): 1.5,
            (cls.NATURAL, cls.ELEMENTAL): 1.8,
            (cls.NATURAL, cls.SPIRIT): 1.5,
            (cls.DIVINE, cls.ORDER): 1.8,
            (cls.DIVINE, cls.SPIRIT): 1.5,
            (cls.SHADOW, cls.VOID): 1.8,
            (cls.SHADOW, cls.CHAOS): 1.5,
            (cls.MIND, cls.ORDER): 1.5,
            (cls.BLOOD, cls.SHADOW): 1.5,
            (cls.BLOOD, cls.CHAOS): 1.3,
            (cls.CHAOS, cls.VOID): 1.5,
            (cls.ORDER, cls.TEMPORAL): 1.5,
            (cls.ELEMENTAL, cls.NATURAL): 1.8,
            (cls.SPIRIT, cls.NATURAL): 1.5,
            (cls.VOID, cls.SHADOW): 1.8,
            (cls.TEMPORAL, cls.ARCANE): 1.8
        }


class DamageType(Enum):
    """Types of magical damage that can be dealt."""
    FIRE = auto()
    WATER = auto()
    EARTH = auto()
    AIR = auto()
    ARCANE = auto()
    LIGHT = auto()
    DARKNESS = auto()
    LIFE = auto()
    DEATH = auto()
    POISON = auto()
    ICE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()
    PHYSICAL = auto()  # For non-magical damage
    
    @classmethod
    def get_domain_affinities(cls) -> Dict[Domain, List['DamageType']]:
        """Return damage types associated with each domain."""
        return {
            Domain.ARCANE: [cls.ARCANE],
            Domain.ELEMENTAL: [cls.FIRE, cls.WATER, cls.EARTH, cls.AIR, cls.ICE, cls.LIGHTNING],
            Domain.NATURAL: [cls.LIFE, cls.POISON, cls.EARTH, cls.WATER],
            Domain.DIVINE: [cls.LIGHT, cls.LIFE],
            Domain.SHADOW: [cls.DARKNESS, cls.DEATH],
            Domain.BLOOD: [cls.NECROTIC, cls.DEATH, cls.LIFE],
            Domain.MIND: [cls.ARCANE, cls.LIGHT],
            Domain.SPIRIT: [cls.LIGHT, cls.DARKNESS],
            Domain.CHAOS: [cls.FIRE, cls.LIGHTNING, cls.DARKNESS],
            Domain.ORDER: [cls.LIGHT, cls.ARCANE],
            Domain.VOID: [cls.DEATH, cls.ARCANE, cls.DARKNESS],
            Domain.TEMPORAL: [cls.ARCANE, cls.LIFE, cls.DEATH]
        }
    
    @classmethod
    def get_opposing_types(cls) -> Dict['DamageType', 'DamageType']:
        """Return pairs of opposing damage types."""
        return {
            cls.FIRE: cls.WATER,
            cls.WATER: cls.FIRE,
            cls.EARTH: cls.AIR,
            cls.AIR: cls.EARTH,
            cls.ARCANE: cls.PHYSICAL,
            cls.PHYSICAL: cls.ARCANE,
            cls.LIGHT: cls.DARKNESS,
            cls.DARKNESS: cls.LIGHT,
            cls.LIFE: cls.DEATH,
            cls.DEATH: cls.LIFE,
            cls.POISON: cls.LIFE,
            cls.ICE: cls.FIRE,
            cls.LIGHTNING: cls.EARTH
        }


class EffectType(Enum):
    """Types of magical effects that can be applied."""
    DAMAGE = auto()
    HEALING = auto()
    BUFF = auto()
    DEBUFF = auto()
    CONTROL = auto()
    SUMMON = auto()
    TELEPORT = auto()
    TRANSFORM = auto()
    ILLUSION = auto()
    ENCHANT = auto()
    DISPEL = auto()
    SHIELD = auto()
    
    @classmethod
    def get_domain_affinities(cls) -> Dict[Domain, List['EffectType']]:
        """Return effect types associated with each domain."""
        return {
            Domain.ARCANE: [cls.DAMAGE, cls.TELEPORT, cls.ENCHANT, cls.ILLUSION, cls.DISPEL],
            Domain.ELEMENTAL: [cls.DAMAGE, cls.CONTROL, cls.TRANSFORM],
            Domain.NATURAL: [cls.HEALING, cls.BUFF, cls.TRANSFORM],
            Domain.DIVINE: [cls.HEALING, cls.BUFF, cls.SHIELD, cls.DISPEL],
            Domain.SHADOW: [cls.DAMAGE, cls.DEBUFF, cls.ILLUSION],
            Domain.BLOOD: [cls.DAMAGE, cls.HEALING, cls.DEBUFF],
            Domain.MIND: [cls.CONTROL, cls.ILLUSION, cls.DEBUFF],
            Domain.SPIRIT: [cls.BUFF, cls.DEBUFF, cls.SUMMON],
            Domain.CHAOS: [cls.DAMAGE, cls.TRANSFORM, cls.ILLUSION],
            Domain.ORDER: [cls.CONTROL, cls.SHIELD, cls.DISPEL],
            Domain.VOID: [cls.TELEPORT, cls.DISPEL, cls.DAMAGE],
            Domain.TEMPORAL: [cls.CONTROL, cls.BUFF, cls.DEBUFF]
        }


class MagicTier(Enum):
    """Tiers of magical power, from weakest to strongest."""
    CANTRIP = auto()
    LESSER = auto()
    MODERATE = auto()
    GREATER = auto()
    MASTER = auto()
    LEGENDARY = auto()
    
    @classmethod
    def get_mana_cost_range(cls, tier: 'MagicTier') -> Tuple[int, int]:
        """Return the mana cost range for a given tier."""
        costs = {
            cls.CANTRIP: (1, 5),
            cls.LESSER: (5, 15),
            cls.MODERATE: (15, 30),
            cls.GREATER: (30, 50),
            cls.MASTER: (50, 100),
            cls.LEGENDARY: (100, 200)
        }
        return costs.get(tier, (0, 0))
    
    @classmethod
    def get_level_requirement(cls, tier: 'MagicTier') -> int:
        """Return the minimum magic level required to use a given tier."""
        requirements = {
            cls.CANTRIP: 1,
            cls.LESSER: 3,
            cls.MODERATE: 7,
            cls.GREATER: 12,
            cls.MASTER: 18,
            cls.LEGENDARY: 25
        }
        return requirements.get(tier, 0)


class ManaFluxLevel(Enum):
    """Levels of mana flux in an area, affecting magical potency."""
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()
    
    @classmethod
    def get_mana_regen_modifier(cls, level: 'ManaFluxLevel') -> float:
        """Return the mana regeneration modifier for a given flux level."""
        modifiers = {
            cls.VERY_LOW: 0.5,
            cls.LOW: 0.75,
            cls.MEDIUM: 1.0,
            cls.HIGH: 1.5,
            cls.VERY_HIGH: 2.0
        }
        return modifiers.get(level, 1.0)
    
    @classmethod
    def get_spell_power_modifier(cls, level: 'ManaFluxLevel') -> float:
        """Return the spell power modifier for a given flux level."""
        modifiers = {
            cls.VERY_LOW: 0.8,
            cls.LOW: 0.9,
            cls.MEDIUM: 1.0,
            cls.HIGH: 1.2,
            cls.VERY_HIGH: 1.5
        }
        return modifiers.get(level, 1.0)


# --- Core Classes ---

class MagicUser:
    """
    Represents an entity capable of using magic.
    This can be a player character, NPC, or monster.
    """
    def __init__(
        self,
        id: str,
        name: str,
        level: int = 1,
        mana_max: int = 100,
        mana_current: int = 100,
        primary_domains: List[Domain] = None,
        secondary_domains: List[Domain] = None,
        known_spells: Set[str] = None,
        magic_skills: Dict[str, int] = None
    ):
        self.id = id
        self.name = name
        self.level = level
        self.mana_max = mana_max
        self.mana_current = mana_current
        self.primary_domains = primary_domains or []
        self.secondary_domains = secondary_domains or []
        self.known_spells = known_spells or set()
        self.magic_skills = magic_skills or {
            "spellcasting": 1,
            "concentration": 1,
            "magical_knowledge": 1,
            "mana_control": 1
        }
        self.active_effects = []
        self.mana_regen_rate = self._calculate_mana_regen_rate()
        self.last_cast_time = datetime.now()
    
    def _calculate_mana_regen_rate(self) -> float:
        """Calculate the mana regeneration rate based on level and skills."""
        base_rate = 1.0  # Mana per second
        level_bonus = self.level * 0.2
        skill_bonus = self.magic_skills.get("mana_control", 1) * 0.3
        return base_rate + level_bonus + skill_bonus
    
    def regenerate_mana(self, seconds_elapsed: float = 1.0, location_modifier: float = 1.0) -> int:
        """
        Regenerate mana based on time elapsed and location.
        Returns the amount of mana regenerated.
        """
        if self.mana_current >= self.mana_max:
            return 0
        
        regen_amount = int(self.mana_regen_rate * seconds_elapsed * location_modifier)
        old_mana = self.mana_current
        self.mana_current = min(self.mana_current + regen_amount, self.mana_max)
        return self.mana_current - old_mana
    
    def spend_mana(self, amount: int) -> bool:
        """
        Attempt to spend mana. Returns True if successful, False if insufficient.
        """
        if amount > self.mana_current:
            return False
        
        self.mana_current -= amount
        return True
    
    def learn_spell(self, spell_id: str) -> bool:
        """
        Learn a new spell. Returns True if successful, False if already known.
        """
        if spell_id in self.known_spells:
            return False
        
        self.known_spells.add(spell_id)
        return True
    
    def can_cast_spell(self, spell: 'Spell') -> bool:
        """
        Check if the user can cast a given spell based on mana, level, and domains.
        """
        # Check if spell is known
        if spell.id not in self.known_spells:
            return False
        
        # Check mana cost
        if spell.mana_cost > self.mana_current:
            return False
        
        # Check level requirement
        if spell.level_req > self.level:
            return False
        
        # Check domain compatibility
        has_primary_domain = any(domain in self.primary_domains for domain in spell.domains)
        has_secondary_domain = any(domain in self.secondary_domains for domain in spell.domains)
        
        if not (has_primary_domain or has_secondary_domain):
            return False
        
        return True
    
    def calculate_spell_power(self, spell: 'Spell') -> float:
        """
        Calculate the power of a spell when cast by this user.
        Takes into account level, domains, and skills.
        """
        # Base power
        power = 1.0
        
        # Level bonus
        power += (self.level / 10)
        
        # Domain affinity bonus
        primary_domain_match = sum(1 for domain in spell.domains if domain in self.primary_domains)
        secondary_domain_match = sum(1 for domain in spell.domains if domain in self.secondary_domains)
        
        power += primary_domain_match * 0.3
        power += secondary_domain_match * 0.1
        
        # Skill bonus
        spellcasting_bonus = self.magic_skills.get("spellcasting", 1) * 0.05
        knowledge_bonus = self.magic_skills.get("magical_knowledge", 1) * 0.03
        
        power += spellcasting_bonus + knowledge_bonus
        
        # Domain synergy bonus
        for i, domain1 in enumerate(spell.domains):
            for domain2 in spell.domains[i+1:]:
                synergy = Domain.get_domain_synergies().get((domain1, domain2), 1.0)
                power *= synergy
        
        return power


class Spell:
    """
    Represents a magical spell that can be cast by a MagicUser.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        domains: List[Domain],
        damage_types: List[DamageType],
        effect_types: List[EffectType],
        mana_cost: int,
        casting_time: float,  # in seconds
        cooldown: float,  # in seconds
        base_power: float,
        level_req: int,
        tier: MagicTier,
        targeting_type: str,  # "self", "single", "area", "all"
        range_max: float,  # in meters
        duration: float = 0.0,  # in seconds, 0 for instant
        components: List[str] = None,  # verbal, somatic, material, etc.
        tags: List[str] = None  # fire, water, healing, etc.
    ):
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
        self.targeting_type = targeting_type
        self.range_max = range_max
        self.duration = duration
        self.components = components or []
        self.tags = tags or []
        self.last_used = {}  # Dict[user_id, datetime]
    
    def is_on_cooldown(self, user_id: str) -> bool:
        """Check if the spell is on cooldown for a given user."""
        if user_id not in self.last_used:
            return False
        
        elapsed = datetime.now() - self.last_used[user_id]
        return elapsed.total_seconds() < self.cooldown
    
    def get_remaining_cooldown(self, user_id: str) -> float:
        """Get the remaining cooldown time in seconds."""
        if user_id not in self.last_used:
            return 0.0
        
        elapsed = datetime.now() - self.last_used[user_id]
        remaining = self.cooldown - elapsed.total_seconds()
        return max(0.0, remaining)
    
    def mark_used(self, user_id: str) -> None:
        """Mark the spell as used by a user, starting the cooldown."""
        self.last_used[user_id] = datetime.now()
    
    def get_scaled_mana_cost(self, spell_power: float) -> int:
        """Calculate the scaled mana cost based on spell power."""
        return int(self.mana_cost * (0.8 + (spell_power * 0.2)))
    
    def get_scaled_effect_power(self, spell_power: float) -> float:
        """Calculate the scaled effect power based on spell power."""
        return self.base_power * spell_power


class MagicEffect:
    """
    Represents a magical effect applied to an entity or location.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        effect_type: EffectType,
        potency: float,
        duration: float,  # in seconds
        damage_type: Optional[DamageType] = None,
        source_id: Optional[str] = None,
        target_id: str = None,
        is_permanent: bool = False,
        ticks_per_second: float = 0.0,  # for effects that apply over time
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.effect_type = effect_type
        self.potency = potency
        self.duration = duration
        self.damage_type = damage_type
        self.source_id = source_id
        self.target_id = target_id
        self.is_permanent = is_permanent
        self.ticks_per_second = ticks_per_second
        self.tags = tags or []
        self.start_time = datetime.now()
        self.last_tick_time = self.start_time
        self.is_active = True
    
    def is_expired(self) -> bool:
        """Check if the effect has expired."""
        if self.is_permanent:
            return False
        
        elapsed = datetime.now() - self.start_time
        return elapsed.total_seconds() >= self.duration
    
    def get_remaining_duration(self) -> float:
        """Get the remaining duration in seconds."""
        if self.is_permanent:
            return float('inf')
        
        elapsed = datetime.now() - self.start_time
        remaining = self.duration - elapsed.total_seconds()
        return max(0.0, remaining)
    
    def should_tick(self) -> bool:
        """Check if the effect should tick."""
        if self.ticks_per_second <= 0.0:
            return False
        
        if not self.is_active or self.is_expired():
            return False
        
        elapsed = datetime.now() - self.last_tick_time
        return elapsed.total_seconds() >= (1.0 / self.ticks_per_second)
    
    def apply_tick(self) -> Dict[str, Any]:
        """
        Apply a tick of the effect. Returns data about the tick.
        Subclasses should override this to implement specific behavior.
        """
        self.last_tick_time = datetime.now()
        return {
            "effect_id": self.id,
            "target_id": self.target_id,
            "potency": self.potency,
            "time": self.last_tick_time
        }
    
    def end_effect(self) -> None:
        """End the effect prematurely."""
        self.is_active = False


class Enchantment:
    """
    Represents a magical enchantment applied to an item.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        domains: List[Domain],
        effects: List[str],  # descriptions of the enchantment effects
        item_types: List[str],  # types of items that can receive this enchantment
        power_level: float,
        duration_days: Optional[int] = None,  # None means permanent
        charges: Optional[int] = None,  # None means unlimited
        required_materials: Dict[str, int] = None,
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.domains = domains
        self.effects = effects
        self.item_types = item_types
        self.power_level = power_level
        self.duration_days = duration_days
        self.charges = charges
        self.required_materials = required_materials or {}
        self.tags = tags or []
        self.creation_time = datetime.now()
        self.current_charges = charges
    
    def is_expired(self) -> bool:
        """Check if the enchantment has expired."""
        if self.duration_days is None:
            return False
        
        elapsed = datetime.now() - self.creation_time
        return elapsed.days >= self.duration_days
    
    def has_charges_left(self) -> bool:
        """Check if the enchantment has charges left."""
        if self.charges is None:
            return True
        
        return self.current_charges > 0
    
    def use_charge(self) -> bool:
        """
        Use a charge of the enchantment.
        Returns True if successful, False if no charges left.
        """
        if self.charges is None:
            return True
        
        if self.current_charges <= 0:
            return False
        
        self.current_charges -= 1
        return True
    
    def get_remaining_days(self) -> Optional[int]:
        """Get the remaining days of the enchantment."""
        if self.duration_days is None:
            return None
        
        elapsed = datetime.now() - self.creation_time
        remaining = self.duration_days - elapsed.days
        return max(0, remaining)
    
    def get_effect_power(self) -> float:
        """Calculate the power of the enchantment effects."""
        return self.power_level * MagicTier.get_level_requirement(self.tier) / 10.0


class ItemMagicProfile:
    """
    Represents the magical properties of an item.
    """
    def __init__(
        self,
        item_id: str,
        is_magical: bool = False,
        is_enchanted: bool = False,
        is_artifact: bool = False,
        enchantment_id: Optional[str] = None,
        inherent_magical_properties: List[str] = None,
        mana_storage_capacity: int = 0,
        stored_mana: int = 0,
        resonance_domains: List[Domain] = None,
        crafting_tier: Optional[MagicTier] = None,
        creation_date: Optional[datetime] = None
    ):
        self.item_id = item_id
        self.is_magical = is_magical
        self.is_enchanted = is_enchanted
        self.is_artifact = is_artifact
        self.enchantment_id = enchantment_id
        self.inherent_magical_properties = inherent_magical_properties or []
        self.mana_storage_capacity = mana_storage_capacity
        self.stored_mana = stored_mana
        self.resonance_domains = resonance_domains or []
        self.crafting_tier = crafting_tier
        self.creation_date = creation_date or datetime.now()
        self.last_used = None
    
    def store_mana(self, amount: int) -> int:
        """
        Store mana in the item. Returns the amount actually stored.
        """
        if self.mana_storage_capacity == 0:
            return 0
        
        available_capacity = self.mana_storage_capacity - self.stored_mana
        amount_to_store = min(amount, available_capacity)
        
        self.stored_mana += amount_to_store
        return amount_to_store
    
    def extract_mana(self, amount: int) -> int:
        """
        Extract mana from the item. Returns the amount actually extracted.
        """
        amount_to_extract = min(amount, self.stored_mana)
        
        self.stored_mana -= amount_to_extract
        return amount_to_extract
    
    def mark_used(self) -> None:
        """Mark the item as used, updating the last_used timestamp."""
        self.last_used = datetime.now()
    
    def days_since_creation(self) -> int:
        """Get the number of days since the item was created."""
        elapsed = datetime.now() - self.creation_date
        return elapsed.days
    
    def is_compatible_with_domain(self, domain: Domain) -> bool:
        """Check if the item is compatible with a specific domain."""
        if not self.resonance_domains:
            return True  # Items without specific resonance are neutral
        
        return domain in self.resonance_domains


class LocationMagicProfile:
    """
    Represents the magical properties of a location.
    """
    def __init__(
        self,
        location_id: str,
        leyline_strength: float = 0.0,  # 0.0 to 1.0
        mana_flux_level: ManaFluxLevel = ManaFluxLevel.MEDIUM,
        dominant_magic_aspects: List[Domain] = None,
        allows_ritual_sites: bool = True,
        magical_pois: List[Dict[str, Any]] = None,
        magical_resources: List[Dict[str, Any]] = None,
        historical_events: List[Dict[str, Any]] = None,
        environmental_effects: List[Dict[str, Any]] = None,
        seasonal_changes: Dict[str, Dict[str, Any]] = None,
        temporal_fluctuations: Dict[str, float] = None
    ):
        self.location_id = location_id
        self.leyline_strength = leyline_strength
        self.mana_flux_level = mana_flux_level
        self.dominant_magic_aspects = dominant_magic_aspects or []
        self.allows_ritual_sites = allows_ritual_sites
        self.magical_pois = magical_pois or []
        self.magical_resources = magical_resources or []
        self.historical_events = historical_events or []
        self.environmental_effects = environmental_effects or []
        self.seasonal_changes = seasonal_changes or {}
        self.temporal_fluctuations = temporal_fluctuations or {
            "dawn": 1.2,
            "noon": 1.0,
            "dusk": 1.3,
            "midnight": 1.5
        }
        self.active_rituals = []
    
    def get_mana_regen_modifier(self) -> float:
        """Calculate the mana regeneration modifier for this location."""
        base_modifier = ManaFluxLevel.get_mana_regen_modifier(self.mana_flux_level)
        leyline_bonus = self.leyline_strength * 0.5
        
        # Time of day would be determined by the game's time system
        # This is a placeholder
        time_of_day = "noon"  # Would come from game state
        time_modifier = self.temporal_fluctuations.get(time_of_day, 1.0)
        
        return base_modifier + leyline_bonus * time_modifier
    
    def get_spell_power_modifier(self, spell_domains: List[Domain]) -> float:
        """
        Calculate the spell power modifier based on location affinity with spell domains.
        """
        base_modifier = ManaFluxLevel.get_spell_power_modifier(self.mana_flux_level)
        
        # Domain affinity bonus
        domain_match_count = sum(1 for domain in spell_domains if domain in self.dominant_magic_aspects)
        domain_bonus = domain_match_count * 0.15
        
        # Leyline bonus
        leyline_bonus = self.leyline_strength * 0.3
        
        return base_modifier + domain_bonus + leyline_bonus
    
    def get_available_magical_resources(self) -> List[Dict[str, Any]]:
        """Get the magical resources available in this location."""
        # In a real implementation, this might filter based on character skills
        return self.magical_resources
    
    def add_ritual_site(self, site_data: Dict[str, Any]) -> bool:
        """
        Add a ritual site to the location.
        Returns True if successful, False if rituals are not allowed.
        """
        if not self.allows_ritual_sites:
            return False
        
        self.magical_pois.append({
            "id": str(uuid.uuid4()),
            "name": site_data.get("name", "Ritual Site"),
            "type": "ritual_site",
            "description": site_data.get("description", "A place of power."),
            "coordinates": site_data.get("coordinates", (0, 0)),
            "power_level": site_data.get("power_level", 1.0),
            "domains": site_data.get("domains", [])
        })
        return True
    
    def get_environmental_effect(self, domain: Optional[Domain] = None) -> Optional[Dict[str, Any]]:
        """
        Get a random environmental effect for this location, optionally filtered by domain.
        Returns None if no suitable effect is found.
        """
        if not self.environmental_effects:
            return None
        
        suitable_effects = self.environmental_effects
        if domain:
            suitable_effects = [effect for effect in suitable_effects 
                               if domain.name.lower() in effect.get("tags", [])]
        
        if not suitable_effects:
            return None
        
        return random.choice(suitable_effects)
    
    def get_current_seasonal_effects(self, season: str) -> Dict[str, Any]:
        """Get the seasonal effects for the current season."""
        return self.seasonal_changes.get(season, {})


class MagicSystem:
    """
    Main class for managing magic functionality throughout the game.
    """
    def __init__(self):
        self.spells = {}  # Dict[spell_id, Spell]
        self.enchantments = {}  # Dict[enchantment_id, Enchantment]
        self.magic_users = {}  # Dict[user_id, MagicUser]
        self.location_profiles = {}  # Dict[location_id, LocationMagicProfile]
        self.item_profiles = {}  # Dict[item_id, ItemMagicProfile]
        self.active_effects = {}  # Dict[effect_id, MagicEffect]
        
        # Counters for generation of IDs
        self._spell_counter = 0
        self._enchantment_counter = 0
        self._effect_counter = 0
    
    def register_magic_user(self, magic_user: MagicUser) -> None:
        """Register a magic user with the system."""
        self.magic_users[magic_user.id] = magic_user
    
    def register_spell(self, spell: Spell) -> None:
        """Register a spell with the system."""
        self.spells[spell.id] = spell
    
    def register_enchantment(self, enchantment: Enchantment) -> None:
        """Register an enchantment with the system."""
        self.enchantments[enchantment.id] = enchantment
    
    def register_location_profile(self, profile: LocationMagicProfile) -> None:
        """Register a location's magic profile."""
        self.location_profiles[profile.location_id] = profile
    
    def register_item_profile(self, profile: ItemMagicProfile) -> None:
        """Register an item's magic profile."""
        self.item_profiles[profile.item_id] = profile
    
    def cast_spell(self, user_id: str, spell_id: str, target_id: str, location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Attempt to cast a spell.
        Returns a dict with the result of the casting attempt.
        """
        # Check if user and spell exist
        if user_id not in self.magic_users:
            return {"success": False, "message": "Magic user not found"}
        
        if spell_id not in self.spells:
            return {"success": False, "message": "Spell not found"}
        
        user = self.magic_users[user_id]
        spell = self.spells[spell_id]
        
        # Check if spell can be cast
        if not user.can_cast_spell(spell):
            return {"success": False, "message": "Cannot cast spell"}
        
        # Check cooldown
        if spell.is_on_cooldown(user_id):
            remaining = spell.get_remaining_cooldown(user_id)
            return {"success": False, "message": f"Spell on cooldown for {remaining:.1f} seconds"}
        
        # Calculate spell power
        spell_power = user.calculate_spell_power(spell)
        
        # Apply location modifiers if available
        location_modifier = 1.0
        if location_id and location_id in self.location_profiles:
            location = self.location_profiles[location_id]
            location_modifier = location.get_spell_power_modifier(spell.domains)
            spell_power *= location_modifier
        
        # Calculate final mana cost
        mana_cost = spell.get_scaled_mana_cost(spell_power)
        
        # Attempt to spend mana
        if not user.spend_mana(mana_cost):
            return {"success": False, "message": "Insufficient mana"}
        
        # Mark spell as used
        spell.mark_used(user_id)
        
        # Generate effect
        effect_id = f"effect_{self._effect_counter}"
        self._effect_counter += 1
        
        effect_power = spell.get_scaled_effect_power(spell_power)
        
        # Create appropriate effect based on spell type
        effect = self._create_effect_from_spell(effect_id, spell, effect_power, user_id, target_id)
        
        if effect:
            self.active_effects[effect_id] = effect
        
        # Return result
        return {
            "success": True,
            "spell_id": spell_id,
            "caster_id": user_id,
            "target_id": target_id,
            "mana_spent": mana_cost,
            "spell_power": spell_power,
            "location_modifier": location_modifier,
            "effect_id": effect_id if effect else None,
            "effect_power": effect_power,
            "message": f"Successfully cast {spell.name}"
        }
    
    def _create_effect_from_spell(
        self, effect_id: str, spell: Spell, power: float, source_id: str, target_id: str
    ) -> Optional[MagicEffect]:
        """Create an appropriate MagicEffect based on the spell type."""
        # This is a simplified implementation
        # A real game would have more complex logic based on spell type
        
        if EffectType.DAMAGE in spell.effect_types and spell.damage_types:
            return MagicEffect(
                id=effect_id,
                name=f"{spell.name} Effect",
                description=f"Damage effect from {spell.name}",
                effect_type=EffectType.DAMAGE,
                potency=power,
                duration=spell.duration,
                damage_type=spell.damage_types[0],
                source_id=source_id,
                target_id=target_id,
                ticks_per_second=1.0 if spell.duration > 0 else 0.0
            )
        
        elif EffectType.HEALING in spell.effect_types:
            return MagicEffect(
                id=effect_id,
                name=f"{spell.name} Effect",
                description=f"Healing effect from {spell.name}",
                effect_type=EffectType.HEALING,
                potency=power,
                duration=spell.duration,
                source_id=source_id,
                target_id=target_id,
                ticks_per_second=1.0 if spell.duration > 0 else 0.0
            )
        
        elif EffectType.BUFF in spell.effect_types:
            return MagicEffect(
                id=effect_id,
                name=f"{spell.name} Effect",
                description=f"Buff effect from {spell.name}",
                effect_type=EffectType.BUFF,
                potency=power,
                duration=spell.duration,
                source_id=source_id,
                target_id=target_id
            )
        
        elif EffectType.DEBUFF in spell.effect_types:
            return MagicEffect(
                id=effect_id,
                name=f"{spell.name} Effect",
                description=f"Debuff effect from {spell.name}",
                effect_type=EffectType.DEBUFF,
                potency=power,
                duration=spell.duration,
                source_id=source_id,
                target_id=target_id
            )
        
        return None
    
    def process_active_effects(self) -> List[Dict[str, Any]]:
        """
        Process all active effects, applying ticks and removing expired effects.
        Returns a list of effect application results.
        """
        results = []
        expired_effects = []
        
        for effect_id, effect in self.active_effects.items():
            if effect.is_expired():
                expired_effects.append(effect_id)
                continue
            
            if effect.should_tick():
                tick_result = effect.apply_tick()
                results.append(tick_result)
        
        # Remove expired effects
        for effect_id in expired_effects:
            del self.active_effects[effect_id]
        
        return results
    
    def process_location_effects(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Process magical effects for a specific location.
        Returns a list of environmental effects that should be applied.
        """
        if location_id not in self.location_profiles:
            return []
        
        location = self.location_profiles[location_id]
        effects = []
        
        # Generate random environmental effects based on location profile
        # This is simplified; a real game would have more complex logic
        if random.random() < (0.1 + location.leyline_strength * 0.2):
            env_effect = location.get_environmental_effect()
            if env_effect:
                effects.append(env_effect)
        
        return effects
    
    def create_basic_spell(self, name: str, domain: Domain, effect_type: EffectType, 
                          damage_type: Optional[DamageType] = None) -> Spell:
        """Utility method to create a basic spell."""
        spell_id = f"spell_{self._spell_counter}"
        self._spell_counter += 1
        
        tier = MagicTier.LESSER
        mana_cost_range = MagicTier.get_mana_cost_range(tier)
        mana_cost = random.randint(*mana_cost_range)
        
        spell = Spell(
            id=spell_id,
            name=name,
            description=f"A {domain.name.lower()} spell that causes {effect_type.name.lower()}",
            domains=[domain],
            damage_types=[damage_type] if damage_type else [],
            effect_types=[effect_type],
            mana_cost=mana_cost,
            casting_time=1.0,
            cooldown=5.0,
            base_power=10.0,
            level_req=MagicTier.get_level_requirement(tier),
            tier=tier,
            targeting_type="single",
            range_max=10.0,
            duration=0.0,  # instant effect
            components=["verbal", "somatic"],
            tags=[domain.name.lower(), effect_type.name.lower()]
        )
        
        self.register_spell(spell)
        return spell
    
    def create_basic_enchantment(self, name: str, domain: Domain, item_type: str) -> Enchantment:
        """Utility method to create a basic enchantment."""
        enchantment_id = f"enchantment_{self._enchantment_counter}"
        self._enchantment_counter += 1
        
        tier = MagicTier.LESSER
        
        enchantment = Enchantment(
            id=enchantment_id,
            name=name,
            description=f"A {domain.name.lower()} enchantment for {item_type}",
            tier=tier,
            domains=[domain],
            effects=[f"Enhances {domain.name.lower()} capabilities"],
            item_types=[item_type],
            power_level=5.0,
            duration_days=None,  # permanent
            charges=None,  # unlimited
            required_materials={"magic_essence": 1},
            tags=[domain.name.lower(), item_type]
        )
        
        self.register_enchantment(enchantment)
        return enchantment