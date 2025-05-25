"""
Magic System Core Module

This module implements the core magic system mechanics, including spells, magic effects,
domains, and other fundamental magical concepts.
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union, TypeVar, Generic
import random
import math
import uuid
from enum import Enum, auto
from datetime import datetime, timedelta


class Domain(Enum):
    """Magical domains or schools of magic."""
    ARCANE = auto()      # Raw magical energy
    DIVINE = auto()      # Holy/religious magic
    ELEMENTAL = auto()   # Control over elements
    NATURAL = auto()     # Nature and life magic
    SHADOW = auto()      # Darkness and illusion
    MIND = auto()        # Mental manipulation
    BLOOD = auto()       # Life force manipulation
    VOID = auto()        # Space and void magic
    NECROMANTIC = auto() # Death magic
    TEMPORAL = auto()    # Time manipulation
    SPIRIT = auto()      # Spirit and soul magic
    WILD = auto()        # Chaotic, unpredictable magic
    RUNIC = auto()       # Symbol-based magic
    ASTRAL = auto()      # Astral plane magic
    ENCHANTMENT = auto() # Object enhancement
    LIGHT = auto()       # Light-based magic
    DARKNESS = auto()    # Darkness-based magic
    FIRE = auto()        # Fire-specific elemental
    WATER = auto()       # Water-specific elemental
    EARTH = auto()       # Earth-specific elemental
    AIR = auto()         # Air-specific elemental
    ICE = auto()         # Ice-specific elemental
    LIGHTNING = auto()   # Lightning-specific elemental
    SUMMONING = auto()   # Creature summoning
    ABJURATION = auto()  # Protective magic
    TRANSMUTATION = auto() # Transformation magic
    ILLUSION = auto()    # Sensory manipulation
    DIVINATION = auto()  # Knowledge/future sight
    CONJURATION = auto() # Creating/calling objects
    HEALING = auto()     # Restoration magic


class DamageType(Enum):
    """Types of damage that can be dealt by magical effects."""
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()
    LIGHTNING = auto()
    WATER = auto()
    EARTH = auto()
    AIR = auto()
    ARCANE = auto()
    DIVINE = auto()
    NECROTIC = auto()
    POISON = auto()
    PSYCHIC = auto()
    RADIANT = auto()
    SHADOW = auto()
    VOID = auto()
    TRUE = auto()  # Bypasses resistances


class EffectType(Enum):
    """Types of effects that magical abilities can produce."""
    DAMAGE = auto()
    HEALING = auto()
    BUFF = auto()
    DEBUFF = auto()
    CROWD_CONTROL = auto()
    SUMMON = auto()
    TRANSFORMATION = auto()
    TELEPORTATION = auto()
    PROTECTION = auto()
    DETECTION = auto()
    CREATION = auto()
    DESTRUCTION = auto()
    ILLUSION = auto()
    DIVINATION = auto()
    ENCHANTMENT = auto()
    ABSORPTION = auto()
    REFLECTION = auto()
    BANISHMENT = auto()
    RESURRECTION = auto()
    BINDING = auto()
    DISPEL = auto()
    CURSE = auto()
    BLESSING = auto()
    UTILITY = auto()


class MagicTier(Enum):
    """Tiers of magical power."""
    CANTRIP = 1        # Minor magical effects
    LESSER = 2         # Basic spells and abilities
    MODERATE = 3       # Standard magical abilities
    GREATER = 4        # Powerful magical abilities
    MASTER = 5         # Master-level magic
    LEGENDARY = 6      # World-altering magic


class ManaFluxLevel(Enum):
    """Levels of ambient mana flux in an area."""
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()


class MagicEffect:
    """
    Represents a magical effect produced by a spell or ability.
    """
    def __init__(
        self,
        effect_type: EffectType,
        potency: float,
        duration: float = 0.0,  # Duration in seconds, 0 for instantaneous
        damage_type: Optional[DamageType] = None,
        stat_modified: Optional[str] = None,
        area_of_effect: float = 0.0,  # Radius in meters
        target_tags: List[str] = None
    ):
        self.effect_type = effect_type
        self.potency = potency
        self.duration = duration
        self.damage_type = damage_type
        self.stat_modified = stat_modified
        self.area_of_effect = area_of_effect
        self.target_tags = target_tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "effect_type": self.effect_type.name,
            "potency": self.potency,
            "duration": self.duration,
            "damage_type": self.damage_type.name if self.damage_type else None,
            "stat_modified": self.stat_modified,
            "area_of_effect": self.area_of_effect,
            "target_tags": self.target_tags
        }


class Spell:
    """
    Represents a magical spell or ability.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        domains: List[Domain],
        damage_types: List[DamageType] = None,
        effect_types: List[EffectType] = None,
        mana_cost: int = 0,
        casting_time: float = 1.0,  # Time in seconds
        cooldown: float = 0.0,      # Time in seconds
        base_power: float = 1.0,
        level_req: int = 1,
        tier: MagicTier = MagicTier.LESSER,
        targeting_type: str = "single",  # single, area, self, etc.
        range_max: float = 5.0,     # Maximum range in meters
        duration: float = 0.0,      # Duration in seconds, 0 for instantaneous
        components: List[str] = None,  # verbal, somatic, material, etc.
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.domains = domains
        self.damage_types = damage_types or []
        self.effect_types = effect_types or []
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
        self.last_cast_time = 0  # Game time of last casting
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domains": [domain.name for domain in self.domains],
            "damage_types": [dt.name for dt in self.damage_types],
            "effect_types": [et.name for et in self.effect_types],
            "mana_cost": self.mana_cost,
            "casting_time": self.casting_time,
            "cooldown": self.cooldown,
            "base_power": self.base_power,
            "level_req": self.level_req,
            "tier": self.tier.name,
            "targeting_type": self.targeting_type,
            "range_max": self.range_max,
            "duration": self.duration,
            "components": self.components,
            "tags": self.tags
        }
    
    def is_on_cooldown(self, current_time: float) -> bool:
        """Check if the spell is on cooldown."""
        return (current_time - self.last_cast_time) < self.cooldown
    
    def cast(self, current_time: float) -> None:
        """Cast the spell, updating its last cast time."""
        self.last_cast_time = current_time


class MagicUser:
    """
    Represents a character with magical abilities.
    """
    def __init__(
        self,
        id: str,
        name: str,
        level: int = 1,
        mana_max: int = 100,
        mana_current: int = 100,
        mana_regen_rate: float = 1.0,  # Mana per minute
        primary_domains: List[Domain] = None,
        secondary_domains: List[Domain] = None,
        known_spells: Set[str] = None,
        magic_skills: Dict[str, int] = None,
        magic_traits: List[str] = None
    ):
        self.id = id
        self.name = name
        self.level = level
        self.mana_max = mana_max
        self.mana_current = mana_current
        self.mana_regen_rate = mana_regen_rate
        self.primary_domains = primary_domains or []
        self.secondary_domains = secondary_domains or []
        self.known_spells = known_spells or set()
        self.magic_skills = magic_skills or {
            "spellcasting": 1,
            "concentration": 1,
            "magical_knowledge": 1,
            "mana_control": 1
        }
        self.magic_traits = magic_traits or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "mana_max": self.mana_max,
            "mana_current": self.mana_current,
            "mana_regen_rate": self.mana_regen_rate,
            "primary_domains": [domain.name for domain in self.primary_domains],
            "secondary_domains": [domain.name for domain in self.secondary_domains],
            "known_spells": list(self.known_spells),
            "magic_skills": self.magic_skills,
            "magic_traits": self.magic_traits
        }
    
    def can_cast_spell(self, spell: Spell, current_time: float) -> bool:
        """Check if the character can cast a spell."""
        # Check level requirement
        if self.level < spell.level_req:
            return False
        
        # Check mana cost
        if self.mana_current < spell.mana_cost:
            return False
        
        # Check cooldown
        if spell.is_on_cooldown(current_time):
            return False
        
        # Check if spell is known
        if spell.id not in self.known_spells:
            return False
        
        return True
    
    def spend_mana(self, amount: int) -> bool:
        """
        Spend mana if available.
        
        Args:
            amount: The amount of mana to spend
            
        Returns:
            True if successful, False if not enough mana
        """
        if self.mana_current >= amount:
            self.mana_current -= amount
            return True
        return False
    
    def regenerate_mana(self, minutes_passed: float) -> None:
        """
        Regenerate mana based on time passed.
        
        Args:
            minutes_passed: Minutes of game time that have passed
        """
        regen_amount = int(self.mana_regen_rate * minutes_passed)
        self.mana_current = min(self.mana_max, self.mana_current + regen_amount)


class Enchantment:
    """
    Represents a magical enchantment that can be applied to items.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        domains: List[Domain],
        effects: List[str],
        item_types: List[str],
        power_level: float,
        duration_days: Optional[int] = None,  # None for permanent
        charges: Optional[int] = None,  # None for unlimited
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
        self.creation_date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.name,
            "domains": [domain.name for domain in self.domains],
            "effects": self.effects,
            "item_types": self.item_types,
            "power_level": self.power_level,
            "duration_days": self.duration_days,
            "charges": self.charges,
            "required_materials": self.required_materials,
            "tags": self.tags,
            "creation_date": self.creation_date.isoformat()
        }
    
    def is_expired(self) -> bool:
        """Check if the enchantment has expired."""
        if self.duration_days is None:
            return False
        
        days_elapsed = (datetime.now() - self.creation_date).days
        return days_elapsed > self.duration_days
    
    def use_charge(self) -> bool:
        """
        Use one charge of the enchantment if available.
        
        Returns:
            True if successful, False if out of charges
        """
        if self.charges is None:
            return True
        
        if self.charges > 0:
            self.charges -= 1
            return True
        
        return False


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
        crafting_tier: MagicTier = MagicTier.LESSER,
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "item_id": self.item_id,
            "is_magical": self.is_magical,
            "is_enchanted": self.is_enchanted,
            "is_artifact": self.is_artifact,
            "enchantment_id": self.enchantment_id,
            "inherent_magical_properties": self.inherent_magical_properties,
            "mana_storage_capacity": self.mana_storage_capacity,
            "stored_mana": self.stored_mana,
            "resonance_domains": [domain.name for domain in self.resonance_domains],
            "crafting_tier": self.crafting_tier.name,
            "creation_date": self.creation_date.isoformat()
        }
    
    def store_mana(self, amount: int) -> int:
        """
        Store mana in the item, up to its capacity.
        
        Args:
            amount: The amount of mana to store
            
        Returns:
            The actual amount stored
        """
        if not self.is_magical:
            return 0
        
        available_capacity = self.mana_storage_capacity - self.stored_mana
        actual_storage = min(available_capacity, amount)
        self.stored_mana += actual_storage
        return actual_storage
    
    def extract_mana(self, amount: int) -> int:
        """
        Extract mana from the item.
        
        Args:
            amount: The amount of mana to extract
            
        Returns:
            The actual amount extracted
        """
        if not self.is_magical:
            return 0
        
        actual_extraction = min(self.stored_mana, amount)
        self.stored_mana -= actual_extraction
        return actual_extraction


class LocationMagicProfile:
    """
    Represents the magical properties of a location.
    """
    def __init__(
        self,
        location_id: str,
        dominant_magic_aspects: List[Domain] = None,
        leyline_strength: float = 0.0,  # 0.0 to 1.0
        mana_flux_level: ManaFluxLevel = ManaFluxLevel.MEDIUM,
        magical_resources: List[Dict[str, Any]] = None,
        magical_pois: List[Dict[str, Any]] = None,
        ambient_effects: List[str] = None,
        allows_ritual_sites: bool = True,
        unstable_magic: bool = False,
        magic_hazards: List[str] = None
    ):
        self.location_id = location_id
        self.dominant_magic_aspects = dominant_magic_aspects or []
        self.leyline_strength = leyline_strength
        self.mana_flux_level = mana_flux_level
        self.magical_resources = magical_resources or []
        self.magical_pois = magical_pois or []
        self.ambient_effects = ambient_effects or []
        self.allows_ritual_sites = allows_ritual_sites
        self.unstable_magic = unstable_magic
        self.magic_hazards = magic_hazards or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "location_id": self.location_id,
            "dominant_magic_aspects": [aspect.name for aspect in self.dominant_magic_aspects],
            "leyline_strength": self.leyline_strength,
            "mana_flux_level": self.mana_flux_level.name,
            "magical_resources": self.magical_resources,
            "magical_pois": self.magical_pois,
            "ambient_effects": self.ambient_effects,
            "allows_ritual_sites": self.allows_ritual_sites,
            "unstable_magic": self.unstable_magic,
            "magic_hazards": self.magic_hazards
        }
    
    def get_casting_modifier(self, spell: Spell) -> float:
        """
        Calculate a modifier for spell casting based on location magic properties.
        
        Args:
            spell: The spell being cast
            
        Returns:
            A multiplier for the spell's effect (higher = stronger)
        """
        # Base modifier
        modifier = 1.0
        
        # Adjust based on leyline strength
        modifier += self.leyline_strength * 0.5
        
        # Adjust based on mana flux
        flux_adjustments = {
            ManaFluxLevel.VERY_LOW: 0.7,
            ManaFluxLevel.LOW: 0.85,
            ManaFluxLevel.MEDIUM: 1.0,
            ManaFluxLevel.HIGH: 1.15,
            ManaFluxLevel.VERY_HIGH: 1.3
        }
        modifier *= flux_adjustments.get(self.mana_flux_level, 1.0)
        
        # Adjust based on domain resonance
        domain_resonance = 0.0
        for spell_domain in spell.domains:
            if spell_domain in self.dominant_magic_aspects:
                domain_resonance += 0.15
        
        modifier += domain_resonance
        
        # Adjust for unstable magic
        if self.unstable_magic:
            # 50% chance to boost, 50% chance to reduce
            if random.random() < 0.5:
                modifier *= random.uniform(1.1, 1.5)
            else:
                modifier *= random.uniform(0.5, 0.9)
        
        return modifier


class MagicSystem:
    """
    Core magic system that manages spells, enchantments, and magical interactions.
    """
    def __init__(self):
        # Registries for magical entities
        self.spells = {}  # id -> Spell
        self.enchantments = {}  # id -> Enchantment
        self.item_magic_profiles = {}  # item_id -> ItemMagicProfile
        self.location_magic_profiles = {}  # location_id -> LocationMagicProfile
        self.magic_users = {}  # id -> MagicUser
        
        # Domain compatibility/synergy matrix
        self.domain_synergies = self._initialize_domain_synergies()
        
        # Magical phenomena tracking
        self.active_leylines = []  # List of leyline paths (lists of location IDs)
        self.magical_hotspots = []  # List of location IDs with high magical energy
    
    def _initialize_domain_synergies(self) -> Dict[Domain, Dict[Domain, float]]:
        """Initialize the domain synergy matrix."""
        synergies = {domain: {} for domain in Domain}
        
        # Some example synergies (could be expanded with a full matrix)
        # Values: -1.0 (conflicting) to 1.0 (highly synergistic), 0.0 = neutral
        
        # Elemental synergies
        synergies[Domain.FIRE][Domain.AIR] = 0.5
        synergies[Domain.FIRE][Domain.WATER] = -0.8
        synergies[Domain.FIRE][Domain.EARTH] = 0.1
        synergies[Domain.FIRE][Domain.ICE] = -0.9
        
        synergies[Domain.WATER][Domain.FIRE] = -0.8
        synergies[Domain.WATER][Domain.AIR] = 0.2
        synergies[Domain.WATER][Domain.EARTH] = 0.5
        synergies[Domain.WATER][Domain.ICE] = 0.8
        
        synergies[Domain.EARTH][Domain.FIRE] = 0.1
        synergies[Domain.EARTH][Domain.WATER] = 0.5
        synergies[Domain.EARTH][Domain.AIR] = -0.4
        synergies[Domain.EARTH][Domain.LIGHTNING] = -0.3
        
        synergies[Domain.AIR][Domain.FIRE] = 0.5
        synergies[Domain.AIR][Domain.WATER] = 0.2
        synergies[Domain.AIR][Domain.EARTH] = -0.4
        synergies[Domain.AIR][Domain.LIGHTNING] = 0.9
        
        # Light/Dark oppositions
        synergies[Domain.LIGHT][Domain.DARKNESS] = -0.9
        synergies[Domain.DARKNESS][Domain.LIGHT] = -0.9
        
        # Arcane synergies
        synergies[Domain.ARCANE][Domain.ELEMENTAL] = 0.3
        synergies[Domain.ARCANE][Domain.ENCHANTMENT] = 0.7
        synergies[Domain.ARCANE][Domain.DIVINE] = -0.2
        synergies[Domain.ARCANE][Domain.VOID] = 0.5
        
        # Divine synergies
        synergies[Domain.DIVINE][Domain.LIGHT] = 0.8
        synergies[Domain.DIVINE][Domain.HEALING] = 0.9
        synergies[Domain.DIVINE][Domain.NECROMANTIC] = -0.7
        synergies[Domain.DIVINE][Domain.BLOOD] = -0.4
        
        # Nature synergies
        synergies[Domain.NATURAL][Domain.ELEMENTAL] = 0.6
        synergies[Domain.NATURAL][Domain.EARTH] = 0.8
        synergies[Domain.NATURAL][Domain.WATER] = 0.7
        synergies[Domain.NATURAL][Domain.HEALING] = 0.5
        
        # Fill in reverse direction and any missing values
        for domain1 in Domain:
            for domain2 in Domain:
                # If synergy is not defined, set to 0.0 (neutral)
                if domain2 not in synergies[domain1]:
                    synergies[domain1][domain2] = 0.0
                
                # If reverse direction not defined, copy from forward direction
                if domain1 != domain2 and domain1 not in synergies[domain2]:
                    synergies[domain2][domain1] = synergies[domain1][domain2]
        
        return synergies
    
    def register_spell(self, spell: Spell) -> None:
        """Register a spell with the magic system."""
        self.spells[spell.id] = spell
    
    def register_enchantment(self, enchantment: Enchantment) -> None:
        """Register an enchantment with the magic system."""
        self.enchantments[enchantment.id] = enchantment
    
    def register_item_profile(self, profile: ItemMagicProfile) -> None:
        """Register an item's magic profile with the magic system."""
        self.item_magic_profiles[profile.item_id] = profile
    
    def register_location_profile(self, profile: LocationMagicProfile) -> None:
        """Register a location's magic profile with the magic system."""
        self.location_magic_profiles[profile.location_id] = profile
    
    def register_magic_user(self, user: MagicUser) -> None:
        """Register a magic user with the magic system."""
        self.magic_users[user.id] = user
    
    def calculate_spell_power(
        self,
        caster: MagicUser,
        spell: Spell,
        location: Optional[LocationMagicProfile] = None,
        equipped_items: List[str] = None
    ) -> float:
        """
        Calculate the power of a spell based on various factors.
        
        Args:
            caster: The magic user casting the spell
            spell: The spell being cast
            location: Optional location magic profile
            equipped_items: Optional list of equipped item IDs
            
        Returns:
            The calculated spell power
        """
        # Base power from spell
        power = spell.base_power
        
        # Adjust based on caster level
        power *= 1.0 + (caster.level * 0.1)
        
        # Adjust based on caster skill
        spellcasting_skill = caster.magic_skills.get("spellcasting", 1)
        power *= 1.0 + (spellcasting_skill * 0.05)
        
        # Adjust based on domain affinity
        domain_factor = 1.0
        for domain in spell.domains:
            if domain in caster.primary_domains:
                domain_factor += 0.2  # 20% bonus per primary domain match
            elif domain in caster.secondary_domains:
                domain_factor += 0.1  # 10% bonus per secondary domain match
        
        power *= domain_factor
        
        # Adjust based on location
        if location:
            location_modifier = location.get_casting_modifier(spell)
            power *= location_modifier
        
        # Adjust based on equipped items
        if equipped_items:
            item_bonus = 0.0
            for item_id in equipped_items:
                if item_id in self.item_magic_profiles:
                    item_profile = self.item_magic_profiles[item_id]
                    
                    # Check for domain resonance
                    for domain in spell.domains:
                        if domain in item_profile.resonance_domains:
                            item_bonus += 0.05  # 5% bonus per resonant domain
                    
                    # Bonus for magical items
                    if item_profile.is_magical:
                        item_bonus += 0.05
                    
                    # Bonus for enchanted items
                    if item_profile.is_enchanted and item_profile.enchantment_id:
                        enchantment = self.enchantments.get(item_profile.enchantment_id)
                        if enchantment:
                            # Check for domain synergy
                            for spell_domain in spell.domains:
                                for enchantment_domain in enchantment.domains:
                                    synergy = self.get_domain_synergy(spell_domain, enchantment_domain)
                                    item_bonus += synergy * 0.1
            
            power *= (1.0 + item_bonus)
        
        return power
    
    def get_domain_synergy(self, domain1: Domain, domain2: Domain) -> float:
        """
        Get the synergy value between two domains.
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            Synergy value from -1.0 (opposing) to 1.0 (synergistic)
        """
        return self.domain_synergies.get(domain1, {}).get(domain2, 0.0)
    
    def cast_spell(
        self,
        caster_id: str,
        spell_id: str,
        target_id: Optional[str] = None,
        location_id: Optional[str] = None,
        current_time: float = 0.0,
        equipped_items: List[str] = None
    ) -> Dict[str, Any]:
        """
        Attempt to cast a spell.
        
        Args:
            caster_id: ID of the magic user casting the spell
            spell_id: ID of the spell to cast
            target_id: Optional ID of the target
            location_id: Optional ID of the location
            current_time: Current game time
            equipped_items: Optional list of equipped item IDs
            
        Returns:
            Dictionary with the result of the casting attempt
        """
        # Get caster
        caster = self.magic_users.get(caster_id)
        if not caster:
            return {
                "success": False,
                "message": f"Unknown caster: {caster_id}"
            }
        
        # Get spell
        spell = self.spells.get(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Unknown spell: {spell_id}"
            }
        
        # Check if caster can cast spell
        if not caster.can_cast_spell(spell, current_time):
            # Check why the spell can't be cast
            if spell.id not in caster.known_spells:
                return {
                    "success": False,
                    "message": f"Caster does not know this spell"
                }
            
            if caster.level < spell.level_req:
                return {
                    "success": False,
                    "message": f"Caster level too low. Requires level {spell.level_req}."
                }
            
            if caster.mana_current < spell.mana_cost:
                return {
                    "success": False,
                    "message": f"Not enough mana. Requires {spell.mana_cost}, have {caster.mana_current}."
                }
            
            if spell.is_on_cooldown(current_time):
                cooldown_remaining = spell.cooldown - (current_time - spell.last_cast_time)
                return {
                    "success": False,
                    "message": f"Spell is on cooldown for {cooldown_remaining:.1f} more seconds."
                }
            
            return {
                "success": False,
                "message": "Cannot cast spell for unknown reason."
            }
        
        # Get location profile if available
        location = None
        if location_id and location_id in self.location_magic_profiles:
            location = self.location_magic_profiles[location_id]
        
        # Calculate spell power
        spell_power = self.calculate_spell_power(caster, spell, location, equipped_items)
        
        # Spend mana
        caster.spend_mana(spell.mana_cost)
        
        # Update spell cooldown
        spell.cast(current_time)
        
        # Generate effects
        effects = []
        for effect_type in spell.effect_types:
            for damage_type in spell.damage_types:
                # Create effect with randomized potency around the spell power
                potency_variation = random.uniform(0.9, 1.1)
                effect = MagicEffect(
                    effect_type=effect_type,
                    potency=spell_power * potency_variation,
                    damage_type=damage_type if effect_type == EffectType.DAMAGE else None,
                    duration=spell.duration
                )
                effects.append(effect.to_dict())
        
        # Result
        return {
            "success": True,
            "message": f"Successfully cast {spell.name}",
            "spell_power": spell_power,
            "mana_spent": spell.mana_cost,
            "effects": effects,
            "target_id": target_id
        }
    
    def calculate_combined_spell_effect(
        self,
        effects: List[Dict[str, Any]],
        target_resistances: Dict[DamageType, float] = None,
        target_weaknesses: Dict[DamageType, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate the combined effect of multiple spell effects on a target.
        
        Args:
            effects: List of spell effect dictionaries
            target_resistances: Optional dictionary of damage type -> resistance value (0.0 to 1.0)
            target_weaknesses: Optional dictionary of damage type -> weakness value (0.0 to 1.0)
            
        Returns:
            Dictionary with combined effect details
        """
        target_resistances = target_resistances or {}
        target_weaknesses = target_weaknesses or {}
        
        # Track total by effect type
        total_by_effect = {}
        damage_by_type = {}
        
        # Process each effect
        for effect_dict in effects:
            effect_type_str = effect_dict.get("effect_type")
            damage_type_str = effect_dict.get("damage_type")
            potency = effect_dict.get("potency", 0.0)
            
            # Skip invalid effects
            if not effect_type_str:
                continue
            
            # Convert strings to enums
            try:
                effect_type = EffectType[effect_type_str]
                damage_type = DamageType[damage_type_str] if damage_type_str else None
            except (KeyError, ValueError):
                continue  # Skip invalid enum values
            
            # For damage effects, apply resistances and weaknesses
            if effect_type == EffectType.DAMAGE and damage_type:
                # Apply resistance
                resistance = target_resistances.get(damage_type, 0.0)
                potency *= (1.0 - resistance)
                
                # Apply weakness
                weakness = target_weaknesses.get(damage_type, 0.0)
                potency *= (1.0 + weakness)
                
                # Add to damage by type
                if damage_type not in damage_by_type:
                    damage_by_type[damage_type] = 0.0
                damage_by_type[damage_type] += potency
            
            # Add to total by effect type
            if effect_type not in total_by_effect:
                total_by_effect[effect_type] = 0.0
            total_by_effect[effect_type] += potency
        
        # Convert enums to strings for the result
        result = {
            "total_by_effect": {et.name: val for et, val in total_by_effect.items()},
            "damage_by_type": {dt.name: val for dt, val in damage_by_type.items()},
            "total_damage": sum(damage_by_type.values()),
            "total_healing": total_by_effect.get(EffectType.HEALING, 0.0),
            "has_crowd_control": EffectType.CROWD_CONTROL in total_by_effect,
            "has_buffs": EffectType.BUFF in total_by_effect,
            "has_debuffs": EffectType.DEBUFF in total_by_effect
        }
        
        return result
    
    def detect_magical_resonance(
        self,
        location_id: str,
        item_id: str
    ) -> Dict[str, Any]:
        """
        Detect magical resonance between a location and an item.
        
        Args:
            location_id: ID of the location
            item_id: ID of the item
            
        Returns:
            Dictionary with resonance details
        """
        # Get location profile
        location = self.location_magic_profiles.get(location_id)
        if not location:
            return {
                "success": False,
                "message": f"Unknown location: {location_id}"
            }
        
        # Get item profile
        item = self.item_magic_profiles.get(item_id)
        if not item:
            return {
                "success": False,
                "message": f"Unknown item: {item_id}"
            }
        
        # Check for domain resonance
        resonant_domains = []
        for item_domain in item.resonance_domains:
            if item_domain in location.dominant_magic_aspects:
                resonant_domains.append(item_domain.name)
        
        # Calculate resonance strength based on matching domains and leyline strength
        resonance_strength = len(resonant_domains) * 0.2 + location.leyline_strength * 0.3
        resonance_strength = min(1.0, resonance_strength)  # Cap at 1.0
        
        # Determine resonance effects
        effects = []
        if resonance_strength > 0.8:
            effects.append("Strong magical amplification")
            effects.append("Possible artifact activation")
        elif resonance_strength > 0.5:
            effects.append("Moderate magical amplification")
            effects.append("Enhanced spell casting")
        elif resonance_strength > 0.2:
            effects.append("Mild magical amplification")
        else:
            effects.append("Minimal resonance detected")
        
        return {
            "success": True,
            "resonant_domains": resonant_domains,
            "resonance_strength": resonance_strength,
            "effects": effects,
            "location_aspects": [aspect.name for aspect in location.dominant_magic_aspects],
            "item_domains": [domain.name for domain in item.resonance_domains]
        }
    
    def register_leyline(self, location_ids: List[str]) -> None:
        """
        Register a leyline connecting multiple locations.
        
        Args:
            location_ids: List of location IDs forming the leyline
        """
        if len(location_ids) >= 2:
            self.active_leylines.append(location_ids)
            
            # Enhance leyline strength for all locations on the path
            for loc_id in location_ids:
                if loc_id in self.location_magic_profiles:
                    profile = self.location_magic_profiles[loc_id]
                    # Increase leyline strength, capped at 1.0
                    profile.leyline_strength = min(1.0, profile.leyline_strength + 0.2)
    
    def register_magical_hotspot(self, location_id: str) -> None:
        """
        Register a location as a magical hotspot.
        
        Args:
            location_id: ID of the location
        """
        if location_id not in self.magical_hotspots:
            self.magical_hotspots.append(location_id)
            
            # Enhance magical properties of the location
            if location_id in self.location_magic_profiles:
                profile = self.location_magic_profiles[location_id]
                # Increase mana flux level if not already at max
                if profile.mana_flux_level != ManaFluxLevel.VERY_HIGH:
                    flux_levels = list(ManaFluxLevel)
                    current_index = flux_levels.index(profile.mana_flux_level)
                    if current_index < len(flux_levels) - 1:
                        profile.mana_flux_level = flux_levels[current_index + 1]
    
    def is_on_leyline(self, location_id: str) -> bool:
        """
        Check if a location is on a leyline.
        
        Args:
            location_id: ID of the location
            
        Returns:
            True if the location is on a leyline, False otherwise
        """
        for leyline in self.active_leylines:
            if location_id in leyline:
                return True
        return False
    
    def is_magical_hotspot(self, location_id: str) -> bool:
        """
        Check if a location is a magical hotspot.
        
        Args:
            location_id: ID of the location
            
        Returns:
            True if the location is a magical hotspot, False otherwise
        """
        return location_id in self.magical_hotspots
    
    def get_leylines_for_location(self, location_id: str) -> List[List[str]]:
        """
        Get all leylines that pass through a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            List of leylines (each a list of location IDs)
        """
        return [leyline for leyline in self.active_leylines if location_id in leyline]
    
    def get_connected_locations(self, location_id: str) -> List[str]:
        """
        Get all locations directly connected to a location via leylines.
        
        Args:
            location_id: ID of the location
            
        Returns:
            List of connected location IDs
        """
        connected = set()
        for leyline in self.active_leylines:
            if location_id in leyline:
                # Find position in leyline
                index = leyline.index(location_id)
                # Add adjacent locations
                if index > 0:
                    connected.add(leyline[index - 1])
                if index < len(leyline) - 1:
                    connected.add(leyline[index + 1])
        
        return list(connected)
    
    def get_magical_disturbances(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Get magical disturbances in a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            List of disturbance details
        """
        disturbances = []
        location = self.location_magic_profiles.get(location_id)
        
        if not location:
            return disturbances
        
        # Check for leyline intersections
        intersection_count = 0
        for leyline in self.active_leylines:
            if location_id in leyline:
                intersection_count += 1
        
        if intersection_count > 1:
            disturbances.append({
                "type": "LEYLINE_INTERSECTION",
                "severity": min(1.0, 0.3 * intersection_count),
                "description": f"Intersection of {intersection_count} leylines creating magical turbulence."
            })
        
        # Check for mana flux
        if location.mana_flux_level in [ManaFluxLevel.HIGH, ManaFluxLevel.VERY_HIGH]:
            disturbances.append({
                "type": "HIGH_MANA_FLUX",
                "severity": 0.7 if location.mana_flux_level == ManaFluxLevel.VERY_HIGH else 0.4,
                "description": f"High levels of ambient mana causing magical fluctuations."
            })
        
        # Check for unstable magic
        if location.unstable_magic:
            disturbances.append({
                "type": "UNSTABLE_MAGIC",
                "severity": 0.8,
                "description": "Unstable magical energies causing unpredictable effects."
            })
        
        # Check for magical hazards
        for hazard in location.magic_hazards:
            disturbances.append({
                "type": "MAGICAL_HAZARD",
                "severity": 0.6,
                "description": hazard
            })
        
        return disturbances