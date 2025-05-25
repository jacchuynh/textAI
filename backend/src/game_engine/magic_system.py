"""
Magic System Core Module

This module implements the core magic system for the game, including:
- Magic user profiles and progression
- Spell management and casting
- Magical effects and their application
- Leyline interaction
- Domain-based magic requirements
"""

from enum import Enum, auto
from typing import Dict, List, Any, Optional, Tuple, Union, Set
import random
import math
import time
from datetime import datetime

# Set a seed for reproducible randomness in tests
random.seed(42)

class Domain(Enum):
    """Core domains that determine a character's capabilities."""
    BODY = auto()         # Physical strength and endurance
    MIND = auto()         # Intelligence and mental acuity
    CRAFT = auto()        # Ability to create and build
    AWARENESS = auto()    # Perception and insight
    SOCIAL = auto()       # Interpersonal skills
    AUTHORITY = auto()    # Leadership and command
    SPIRIT = auto()       # Spiritual connection and will
    
    # Elemental domains
    FIRE = auto()
    WATER = auto()
    EARTH = auto()
    AIR = auto()
    LIGHT = auto()
    DARKNESS = auto()

class DamageType(Enum):
    """Types of magical damage or effect."""
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

class MagicTier(Enum):
    """Tiers of magical power, from cantrips to world-altering magic."""
    CANTRIP = auto()      # Minor, everyday magic
    APPRENTICE = auto()   # Basic magic learned by beginners
    ADEPT = auto()        # Intermediate spells requiring training
    EXPERT = auto()       # Advanced magic requiring significant skill
    MASTER = auto()       # Powerful magic few can cast
    ARCHMAGE = auto()     # Extremely rare and powerful spells
    LEGENDARY = auto()    # World-altering, ancient magic

class MagicSource(Enum):
    """Sources of magical power."""
    MANA = auto()          # Internal magical energy
    LEY_ENERGY = auto()    # External energy from leylines
    LIFE_FORCE = auto()    # Energy drawn from living beings
    RITUAL = auto()        # Energy from ritual preparations
    ITEM = auto()          # Energy stored in magical items
    ENVIRONMENTAL = auto() # Energy from the surrounding environment

class EffectType(Enum):
    """Types of magical effects."""
    DAMAGE = auto()        # Direct damage to targets
    HEALING = auto()       # Restore health to targets
    BUFF = auto()          # Enhance target's capabilities
    DEBUFF = auto()        # Weaken target's capabilities
    CONTROL = auto()       # Control target's actions
    UTILITY = auto()       # Non-combat effects
    SUMMONING = auto()     # Summon creatures or objects
    TRANSFORMATION = auto() # Change form or properties
    DIVINATION = auto()    # Gain information or insight
    ENCHANTMENT = auto()   # Add magical properties to items
    CONJURATION = auto()   # Create something from nothing
    ILLUSION = auto()      # Create false sensory information
    ABJURATION = auto()    # Protective magic

class TargetType(Enum):
    """Types of spell targets."""
    SELF = auto()          # The caster
    SINGLE = auto()        # A single target
    AREA = auto()          # An area effect
    MULTI = auto()         # Multiple specific targets
    GLOBAL = auto()        # Affects everything in range
    OBJECT = auto()        # A non-living object
    LOCATION = auto()      # A specific location

class ManaFluxLevel(Enum):
    """Levels of mana flux in an environment."""
    VERY_LOW = auto()      # Almost no ambient magic
    LOW = auto()           # Minor ambient magic
    MEDIUM = auto()        # Moderate ambient magic
    HIGH = auto()          # Strong ambient magic
    VERY_HIGH = auto()     # Extremely potent ambient magic

class DomainRequirement:
    """Requirement for a specific domain value to cast a spell or perform a magical action."""
    
    def __init__(self, domain: Domain, minimum_value: int):
        self.domain = domain
        self.minimum_value = minimum_value
    
    def check_requirement(self, character_domains: Dict[Domain, int]) -> bool:
        """Check if a character meets this domain requirement."""
        if self.domain not in character_domains:
            return False
        return character_domains[self.domain] >= self.minimum_value
    
    def __str__(self) -> str:
        return f"{self.domain.name} {self.minimum_value}+"

class MagicalEffect:
    """A magical effect that can be applied to targets."""
    
    def __init__(
        self,
        effect_type: EffectType,
        potency: int,
        duration: int,  # in seconds
        damage_type: Optional[DamageType] = None,
        description: str = ""
    ):
        self.effect_type = effect_type
        self.potency = potency
        self.duration = duration
        self.damage_type = damage_type
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def apply(self, target: Any) -> Dict[str, Any]:
        """Apply this effect to a target."""
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration
        
        # Effect application depends on the type of effect
        result = {
            "success": True,
            "message": f"Applied {self.effect_type.name} effect to target",
            "effect_details": {
                "type": self.effect_type.name,
                "potency": self.potency,
                "duration": self.duration,
                "remaining_duration": self.duration,
                "damage_type": self.damage_type.name if self.damage_type else None
            }
        }
        
        # Apply specific effects based on type
        if self.effect_type == EffectType.DAMAGE and hasattr(target, 'current_health'):
            target.current_health -= self.potency
            result["damage_dealt"] = self.potency
            result["target_health"] = target.current_health
        
        elif self.effect_type == EffectType.HEALING and hasattr(target, 'current_health'):
            original_health = target.current_health
            target.current_health = min(target.current_health + self.potency, target.max_health)
            healing_amount = target.current_health - original_health
            result["healing_done"] = healing_amount
            result["target_health"] = target.current_health
        
        return result
    
    def is_active(self) -> bool:
        """Check if this effect is still active."""
        if self.start_time is None:
            return False
        return time.time() < self.end_time
    
    def get_remaining_duration(self) -> float:
        """Get the remaining duration of this effect in seconds."""
        if self.start_time is None or not self.is_active():
            return 0.0
        return self.end_time - time.time()
    
    def __str__(self) -> str:
        return f"{self.effect_type.name} ({self.potency}) - {self.description}"

class Spell:
    """A magical spell that can be cast."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        mana_cost: int,
        ley_energy_cost: int,
        casting_time: float,  # in seconds
        effects: List[MagicalEffect],
        target_type: TargetType,
        range: int,  # in meters
        domain_requirements: List[DomainRequirement],
        source: MagicSource = MagicSource.MANA,
        is_ritual: bool = False,
        keywords: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.mana_cost = mana_cost
        self.ley_energy_cost = ley_energy_cost
        self.casting_time = casting_time
        self.effects = effects
        self.target_type = target_type
        self.range = range
        self.domain_requirements = domain_requirements
        self.source = source
        self.is_ritual = is_ritual
        self.keywords = keywords or []
    
    def can_cast(self, caster_magic: 'MagicUser', caster_domains: Dict[Domain, int]) -> Tuple[bool, str]:
        """Check if the spell can be cast by the given caster."""
        # Check mana requirement
        if self.mana_cost > caster_magic.mana_current:
            return False, f"Not enough mana ({caster_magic.mana_current}/{self.mana_cost})"
        
        # Check ley energy requirement
        if self.ley_energy_cost > caster_magic.current_ley_energy:
            return False, f"Not enough ley energy ({caster_magic.current_ley_energy}/{self.ley_energy_cost})"
        
        # Check domain requirements
        for req in self.domain_requirements:
            if not req.check_requirement(caster_domains):
                return False, f"Domain requirement not met: {req}"
        
        # Check if the spell requires a mana heart
        if not caster_magic.has_mana_heart and self.tier.value > MagicTier.CANTRIP.value:
            return False, "Requires a mana heart to cast"
        
        # Check if the spell is a ritual and if the caster can perform rituals
        if self.is_ritual and not caster_magic.can_perform_rituals:
            return False, "Cannot perform rituals"
        
        return True, "Can cast"
    
    def cast(
        self, 
        caster_id: str,
        caster_magic: 'MagicUser', 
        caster_domains: Dict[Domain, int],
        targets: List[Any],
        location_magic: Optional['LocationMagicProfile'] = None
    ) -> Dict[str, Any]:
        """Cast the spell, applying its effects to targets."""
        # Check if the spell can be cast
        can_cast, reason = self.can_cast(caster_magic, caster_domains)
        if not can_cast:
            return {
                "success": False,
                "message": reason
            }
        
        # Consume resources
        caster_magic.mana_current -= self.mana_cost
        caster_magic.current_ley_energy -= self.ley_energy_cost
        
        # Calculate spell effectiveness based on location magic if available
        effectiveness_modifier = 1.0
        if location_magic:
            # Bonus from leyline strength
            leyline_bonus = location_magic.leyline_strength * 0.1
            
            # Bonus from matching magic aspects
            aspect_bonus = 0.0
            for effect in self.effects:
                if effect.damage_type in location_magic.dominant_magic_aspects:
                    aspect_bonus += 0.2
            
            effectiveness_modifier += leyline_bonus + aspect_bonus
        
        # Apply effects to targets
        effect_results = []
        for target in targets:
            target_results = []
            for effect in self.effects:
                # Create a copy of the effect with modified potency
                modified_effect = MagicalEffect(
                    effect_type=effect.effect_type,
                    potency=int(effect.potency * effectiveness_modifier),
                    duration=effect.duration,
                    damage_type=effect.damage_type,
                    description=effect.description
                )
                # Apply the effect
                result = modified_effect.apply(target)
                target_results.append(result)
            
            effect_results.append({
                "target": target,
                "results": target_results
            })
        
        # Generate a cast message
        cast_message = f"{caster_id} cast {self.name}"
        if location_magic and effectiveness_modifier > 1.2:
            cast_message += " with enhanced effectiveness!"
        elif location_magic and effectiveness_modifier < 0.8:
            cast_message += " with reduced effectiveness."
        
        return {
            "success": True,
            "message": cast_message,
            "mana_used": self.mana_cost,
            "ley_energy_used": self.ley_energy_cost,
            "effectiveness_modifier": effectiveness_modifier,
            "effect_results": effect_results,
            "casting_time": self.casting_time
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.tier.name}) - {self.description}"

class Ritual(Spell):
    """A magical ritual that takes longer to cast but has powerful effects."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        mana_cost: int,
        ley_energy_cost: int,
        casting_time: float,  # in minutes for rituals
        effects: List[MagicalEffect],
        target_type: TargetType,
        range: int,  # in meters
        domain_requirements: List[DomainRequirement],
        material_requirements: Dict[str, int],  # item_id: quantity
        minimum_participants: int = 1,
        ideal_time_of_day: Optional[str] = None,
        ideal_location_type: Optional[str] = None,
        keywords: List[str] = None
    ):
        super().__init__(
            id=id,
            name=name,
            description=description,
            tier=tier,
            mana_cost=mana_cost,
            ley_energy_cost=ley_energy_cost,
            casting_time=casting_time * 60,  # convert to seconds
            effects=effects,
            target_type=target_type,
            range=range,
            domain_requirements=domain_requirements,
            source=MagicSource.RITUAL,
            is_ritual=True,
            keywords=keywords
        )
        self.material_requirements = material_requirements
        self.minimum_participants = minimum_participants
        self.ideal_time_of_day = ideal_time_of_day
        self.ideal_location_type = ideal_location_type
    
    def check_ritual_requirements(
        self,
        available_materials: Dict[str, int],
        participants_count: int,
        time_of_day: Optional[str] = None,
        location_type: Optional[str] = None,
        location_magic: Optional['LocationMagicProfile'] = None
    ) -> Tuple[bool, str, float]:
        """
        Check if all ritual requirements are met.
        
        Returns:
            Tuple of (success, message, effectiveness_modifier)
        """
        # Check material requirements
        for item_id, quantity in self.material_requirements.items():
            if item_id not in available_materials or available_materials[item_id] < quantity:
                return False, f"Missing material: {item_id} ({quantity} required)", 0.0
        
        # Check participant requirements
        if participants_count < self.minimum_participants:
            return False, f"Not enough participants ({participants_count}/{self.minimum_participants})", 0.0
        
        # Calculate effectiveness based on ideal conditions
        effectiveness_modifier = 1.0
        
        # Bonus for more participants than minimum
        if participants_count > self.minimum_participants:
            effectiveness_modifier += 0.1 * (participants_count - self.minimum_participants)
        
        # Bonus for ideal time of day
        if self.ideal_time_of_day and time_of_day:
            if self.ideal_time_of_day == time_of_day:
                effectiveness_modifier += 0.2
        
        # Bonus for ideal location type
        if self.ideal_location_type and location_type:
            if self.ideal_location_type == location_type:
                effectiveness_modifier += 0.2
        
        # Bonus for location that allows rituals
        if location_magic and location_magic.allows_ritual_sites:
            effectiveness_modifier += 0.3
        
        return True, "All ritual requirements met", effectiveness_modifier
    
    def perform_ritual(
        self,
        caster_id: str,
        caster_magic: 'MagicUser',
        caster_domains: Dict[Domain, int],
        targets: List[Any],
        available_materials: Dict[str, int],
        participants_count: int,
        time_of_day: Optional[str] = None,
        location_type: Optional[str] = None,
        location_magic: Optional['LocationMagicProfile'] = None
    ) -> Dict[str, Any]:
        """Perform the ritual, applying its effects to targets."""
        # Check if the ritual can be cast
        can_cast, reason = self.can_cast(caster_magic, caster_domains)
        if not can_cast:
            return {
                "success": False,
                "message": reason
            }
        
        # Check ritual requirements
        req_met, req_message, req_modifier = self.check_ritual_requirements(
            available_materials, participants_count, time_of_day, location_type, location_magic
        )
        
        if not req_met:
            return {
                "success": False,
                "message": req_message
            }
        
        # Consume materials
        consumed_materials = {}
        for item_id, quantity in self.material_requirements.items():
            consumed_materials[item_id] = quantity
        
        # Consume resources
        caster_magic.mana_current -= self.mana_cost
        caster_magic.current_ley_energy -= self.ley_energy_cost
        
        # Calculate total effectiveness
        effectiveness_modifier = req_modifier
        
        # Add location magic bonus if available
        if location_magic:
            # Bonus from leyline strength
            leyline_bonus = location_magic.leyline_strength * 0.1
            
            # Bonus from matching magic aspects
            aspect_bonus = 0.0
            for effect in self.effects:
                if effect.damage_type in location_magic.dominant_magic_aspects:
                    aspect_bonus += 0.2
            
            effectiveness_modifier += leyline_bonus + aspect_bonus
        
        # Apply effects to targets with modified potency
        effect_results = []
        for target in targets:
            target_results = []
            for effect in self.effects:
                # Create a copy of the effect with modified potency
                modified_effect = MagicalEffect(
                    effect_type=effect.effect_type,
                    potency=int(effect.potency * effectiveness_modifier),
                    duration=int(effect.duration * effectiveness_modifier),
                    damage_type=effect.damage_type,
                    description=effect.description
                )
                # Apply the effect
                result = modified_effect.apply(target)
                target_results.append(result)
            
            effect_results.append({
                "target": target,
                "results": target_results
            })
        
        # Generate a ritual message
        ritual_message = f"{caster_id} performed the ritual: {self.name}"
        if effectiveness_modifier > 1.5:
            ritual_message += " with extraordinary effectiveness!"
        elif effectiveness_modifier > 1.2:
            ritual_message += " with enhanced effectiveness!"
        elif effectiveness_modifier < 0.8:
            ritual_message += " with reduced effectiveness."
        
        return {
            "success": True,
            "message": ritual_message,
            "mana_used": self.mana_cost,
            "ley_energy_used": self.ley_energy_cost,
            "materials_consumed": consumed_materials,
            "effectiveness_modifier": effectiveness_modifier,
            "effect_results": effect_results,
            "casting_time": self.casting_time,
            "participants": participants_count
        }

class Enchantment:
    """A magical enchantment that can be applied to items."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        effects: List[str],
        duration: Optional[int] = None,  # in days, None for permanent
        charges: Optional[int] = None,  # None for unlimited
        keywords: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.effects = effects
        self.duration = duration
        self.charges = charges
        self.keywords = keywords or []
        self.creation_date = datetime.now()
        self.expiration_date = (
            datetime.now().timestamp() + (duration * 86400) if duration else None
        )
    
    def is_active(self) -> bool:
        """Check if the enchantment is still active."""
        if self.duration is None:
            return True
        return datetime.now().timestamp() < self.expiration_date
    
    def use_charge(self) -> bool:
        """Use a charge of the enchantment. Returns False if no charges left."""
        if self.charges is None:
            return True
        
        if self.charges <= 0:
            return False
        
        self.charges -= 1
        return True
    
    def get_remaining_duration(self) -> Optional[float]:
        """Get the remaining duration in days."""
        if self.duration is None:
            return None
        
        remaining_seconds = self.expiration_date - datetime.now().timestamp()
        if remaining_seconds <= 0:
            return 0
        
        return remaining_seconds / 86400  # Convert to days
    
    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about the enchantment."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.name,
            "effects": self.effects,
            "is_active": self.is_active(),
            "charges": self.charges,
            "remaining_duration": self.get_remaining_duration(),
            "keywords": self.keywords,
            "creation_date": self.creation_date.isoformat()
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.tier.name}) - {self.description}"

class ItemMagicProfile:
    """Magical properties of an item."""
    
    def __init__(
        self,
        item_id: str,
        is_enchanted: bool = False,
        enchantment_id: Optional[str] = None,
        enchantment: Optional[Enchantment] = None,
        mana_storage_capacity: int = 0,
        current_mana_stored: int = 0,
        ley_energy_capacity: int = 0,
        current_ley_energy: int = 0,
        attunement_required: bool = False,
        attuned_to: Optional[str] = None,
        material_properties: List[str] = None
    ):
        self.item_id = item_id
        self.is_enchanted = is_enchanted
        self.enchantment_id = enchantment_id
        self.enchantment = enchantment
        self.mana_storage_capacity = mana_storage_capacity
        self.current_mana_stored = current_mana_stored
        self.ley_energy_capacity = ley_energy_capacity
        self.current_ley_energy = current_ley_energy
        self.attunement_required = attunement_required
        self.attuned_to = attuned_to
        self.material_properties = material_properties or []
    
    def store_mana(self, amount: int) -> int:
        """
        Store mana in the item. Returns the amount actually stored.
        """
        if self.mana_storage_capacity == 0:
            return 0
        
        available_capacity = self.mana_storage_capacity - self.current_mana_stored
        amount_to_store = min(amount, available_capacity)
        
        self.current_mana_stored += amount_to_store
        return amount_to_store
    
    def withdraw_mana(self, amount: int) -> int:
        """
        Withdraw mana from the item. Returns the amount actually withdrawn.
        """
        amount_to_withdraw = min(amount, self.current_mana_stored)
        self.current_mana_stored -= amount_to_withdraw
        return amount_to_withdraw
    
    def store_ley_energy(self, amount: int) -> int:
        """
        Store ley energy in the item. Returns the amount actually stored.
        """
        if self.ley_energy_capacity == 0:
            return 0
        
        available_capacity = self.ley_energy_capacity - self.current_ley_energy
        amount_to_store = min(amount, available_capacity)
        
        self.current_ley_energy += amount_to_store
        return amount_to_store
    
    def withdraw_ley_energy(self, amount: int) -> int:
        """
        Withdraw ley energy from the item. Returns the amount actually withdrawn.
        """
        amount_to_withdraw = min(amount, self.current_ley_energy)
        self.current_ley_energy -= amount_to_withdraw
        return amount_to_withdraw
    
    def attune_to(self, character_id: str) -> bool:
        """
        Attune the item to a character. Returns True if successful.
        """
        if not self.attunement_required:
            return False
        
        self.attuned_to = character_id
        return True
    
    def can_use(self, character_id: Optional[str] = None) -> bool:
        """
        Check if the item can be used by the specified character.
        """
        if self.attunement_required and self.attuned_to != character_id:
            return False
        
        if self.is_enchanted and self.enchantment:
            return self.enchantment.is_active()
        
        return True
    
    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about the item's magical properties."""
        details = {
            "item_id": self.item_id,
            "is_enchanted": self.is_enchanted,
            "enchantment_id": self.enchantment_id,
            "mana_storage": {
                "capacity": self.mana_storage_capacity,
                "current": self.current_mana_stored
            },
            "ley_energy_storage": {
                "capacity": self.ley_energy_capacity,
                "current": self.current_ley_energy
            },
            "attunement": {
                "required": self.attunement_required,
                "attuned_to": self.attuned_to
            },
            "material_properties": self.material_properties
        }
        
        if self.is_enchanted and self.enchantment:
            details["enchantment"] = self.enchantment.get_details()
        
        return details

class LocationMagicProfile:
    """Magical properties of a location."""
    
    def __init__(
        self,
        leyline_strength: float = 0.0,  # 0.0 to 5.0
        mana_flux_level: ManaFluxLevel = ManaFluxLevel.LOW,
        dominant_magic_aspects: List[DamageType] = None,
        allows_ritual_sites: bool = False,
        active_magical_effects: List[MagicalEffect] = None,
        magical_landmarks: List[Dict[str, Any]] = None,
        magical_creatures: List[Dict[str, Any]] = None,
        magical_plant_life: List[Dict[str, Any]] = None,
        magical_weather_patterns: List[Dict[str, Any]] = None,
        enchantment_level: int = 0  # 0 to 10
    ):
        self.leyline_strength = leyline_strength
        self.mana_flux_level = mana_flux_level
        self.dominant_magic_aspects = dominant_magic_aspects or []
        self.allows_ritual_sites = allows_ritual_sites
        self.active_magical_effects = active_magical_effects or []
        self.magical_landmarks = magical_landmarks or []
        self.magical_creatures = magical_creatures or []
        self.magical_plant_life = magical_plant_life or []
        self.magical_weather_patterns = magical_weather_patterns or []
        self.enchantment_level = enchantment_level
    
    def get_mana_regeneration_bonus(self) -> float:
        """Get the mana regeneration bonus for characters in this location."""
        # Base bonus from leyline strength
        bonus = self.leyline_strength * 0.2
        
        # Bonus from mana flux level
        if self.mana_flux_level == ManaFluxLevel.VERY_HIGH:
            bonus += 0.5
        elif self.mana_flux_level == ManaFluxLevel.HIGH:
            bonus += 0.3
        elif self.mana_flux_level == ManaFluxLevel.MEDIUM:
            bonus += 0.1
        
        return bonus
    
    def get_spell_effectiveness_modifier(self, spell: Spell) -> float:
        """
        Get the effectiveness modifier for a spell cast in this location.
        
        Returns a value that multiplies the spell's effects. 1.0 is normal effectiveness.
        """
        # Base modifier from enchantment level
        modifier = 1.0 + (self.enchantment_level * 0.05)
        
        # Bonus from matching dominant aspects
        for effect in spell.effects:
            if effect.damage_type in self.dominant_magic_aspects:
                modifier += 0.15
        
        # Bonus from leyline strength for rituals
        if spell.is_ritual:
            modifier += self.leyline_strength * 0.1
        
        return modifier
    
    def get_available_magical_resources(self) -> List[Dict[str, Any]]:
        """Get magical resources available at this location."""
        resources = []
        
        # Add plants
        for plant in self.magical_plant_life:
            if plant.get("harvestable", False):
                resources.append({
                    "id": plant.get("id"),
                    "name": plant.get("name"),
                    "type": "plant",
                    "rarity": plant.get("rarity", "common"),
                    "magical_aspect": plant.get("magical_aspect")
                })
        
        # Add mineral deposits based on location properties
        if self.leyline_strength > 2.0:
            resources.append({
                "id": "resource_mana_crystal",
                "name": "Mana Crystal",
                "type": "mineral",
                "rarity": "uncommon",
                "magical_aspect": "arcane"
            })
        
        if self.enchantment_level > 5:
            resources.append({
                "id": "resource_enchanted_dust",
                "name": "Enchanted Dust",
                "type": "residue",
                "rarity": "rare",
                "magical_aspect": "enchantment"
            })
        
        # Add aspect-specific resources
        for aspect in self.dominant_magic_aspects:
            if aspect == DamageType.FIRE:
                resources.append({
                    "id": "resource_fire_essence",
                    "name": "Fire Essence",
                    "type": "essence",
                    "rarity": "uncommon",
                    "magical_aspect": "fire"
                })
            elif aspect == DamageType.WATER:
                resources.append({
                    "id": "resource_water_essence",
                    "name": "Water Essence",
                    "type": "essence",
                    "rarity": "uncommon",
                    "magical_aspect": "water"
                })
            # Add more aspects as needed
        
        return resources
    
    def apply_magical_environmental_effects(self, character: Any) -> List[Dict[str, Any]]:
        """Apply environmental magical effects to a character."""
        applied_effects = []
        
        # Apply active effects
        for effect in self.active_magical_effects:
            if effect.is_active():
                result = effect.apply(character)
                applied_effects.append(result)
        
        # Apply automatic effects based on location properties
        
        # Mana regeneration in high-magic areas
        if self.mana_flux_level in [ManaFluxLevel.HIGH, ManaFluxLevel.VERY_HIGH]:
            if hasattr(character, 'magic_profile') and hasattr(character.magic_profile, 'mana_current'):
                # Regenerate some mana
                regen_amount = int(5 * self.get_mana_regeneration_bonus())
                original_mana = character.magic_profile.mana_current
                character.magic_profile.mana_current = min(
                    character.magic_profile.mana_current + regen_amount,
                    character.magic_profile.mana_max
                )
                actual_regen = character.magic_profile.mana_current - original_mana
                
                if actual_regen > 0:
                    applied_effects.append({
                        "effect_type": "mana_regeneration",
                        "amount": actual_regen,
                        "source": "environmental",
                        "description": "The magical atmosphere regenerates your mana."
                    })
        
        # Environmental damage in certain locations
        for aspect in self.dominant_magic_aspects:
            if aspect == DamageType.FIRE and self.enchantment_level > 7:
                if hasattr(character, 'current_health'):
                    damage = 2
                    character.current_health -= damage
                    applied_effects.append({
                        "effect_type": "environmental_damage",
                        "damage_type": "fire",
                        "amount": damage,
                        "description": "The intense heat of the area burns you."
                    })
            
            # Add more environmental effects for other aspects
        
        return applied_effects
    
    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about the location's magical properties."""
        return {
            "leyline_strength": self.leyline_strength,
            "mana_flux_level": self.mana_flux_level.name,
            "dominant_magic_aspects": [aspect.name for aspect in self.dominant_magic_aspects],
            "allows_ritual_sites": self.allows_ritual_sites,
            "active_magical_effects_count": len(self.active_magical_effects),
            "magical_landmarks_count": len(self.magical_landmarks),
            "enchantment_level": self.enchantment_level,
            "mana_regeneration_bonus": self.get_mana_regeneration_bonus()
        }

class MagicUser:
    """Profile of a magic user with magical capabilities and resources."""
    
    def __init__(
        self,
        character_id: str,
        has_mana_heart: bool = False,
        mana_max: int = 0,
        mana_current: int = 0,
        mana_regeneration_rate: float = 0.0,  # per second
        known_spells: List[str] = None,
        known_rituals: List[str] = None,
        can_perform_rituals: bool = False,
        attunements: List[str] = None,  # Magic types the user is attuned to
        ley_energy_sensitivity: float = 0.0,  # 0.0 to 1.0
        current_ley_energy: int = 0,
        affinity: Dict[DamageType, float] = None,  # Magic types the user has affinity with
        resistance: Dict[DamageType, float] = None,  # Magic types the user resists
        active_effects: List[MagicalEffect] = None,
        enchanting_skill: int = 0,  # 0 to 100
        ritual_skill: int = 0,  # 0 to 100
        mana_heart_development: float = 0.0  # 0.0 to 1.0
    ):
        self.character_id = character_id
        self.has_mana_heart = has_mana_heart
        self.mana_max = mana_max
        self.mana_current = mana_current
        self.mana_regeneration_rate = mana_regeneration_rate
        self.known_spells = known_spells or []
        self.known_rituals = known_rituals or []
        self.can_perform_rituals = can_perform_rituals
        self.attunements = attunements or []
        self.ley_energy_sensitivity = ley_energy_sensitivity
        self.current_ley_energy = current_ley_energy
        self.affinity = affinity or {}
        self.resistance = resistance or {}
        self.active_effects = active_effects or []
        self.enchanting_skill = enchanting_skill
        self.ritual_skill = ritual_skill
        self.mana_heart_development = mana_heart_development
        self.last_mana_regen_time = time.time()
    
    def update_mana_regeneration(self) -> int:
        """
        Update mana based on regeneration rate. Returns the amount regenerated.
        """
        current_time = time.time()
        time_passed = current_time - self.last_mana_regen_time
        
        # Calculate mana to regenerate
        mana_to_regen = int(time_passed * self.mana_regeneration_rate)
        
        if mana_to_regen <= 0:
            return 0
        
        # Update mana
        original_mana = self.mana_current
        self.mana_current = min(self.mana_current + mana_to_regen, self.mana_max)
        self.last_mana_regen_time = current_time
        
        return self.mana_current - original_mana
    
    def draw_from_leyline(self, leyline_strength: float, max_draw: int) -> int:
        """
        Draw energy from a leyline. Returns the amount drawn.
        
        Args:
            leyline_strength: The strength of the leyline (0.0 to 5.0)
            max_draw: The maximum amount to draw
        """
        # Calculate base draw amount based on sensitivity and leyline strength
        base_draw = int(max_draw * self.ley_energy_sensitivity * (leyline_strength / 5.0))
        
        # Random variation
        variation = random.uniform(0.8, 1.2)
        draw_amount = int(base_draw * variation)
        
        # Ensure at least 1 is drawn if possible
        draw_amount = max(1, draw_amount) if base_draw > 0 else 0
        
        # Limit to max_draw
        draw_amount = min(draw_amount, max_draw)
        
        self.current_ley_energy += draw_amount
        return draw_amount
    
    def use_spell(self, spell_id: str, targets: List[Any], location_magic: Optional[LocationMagicProfile] = None) -> Dict[str, Any]:
        """
        Use a known spell on targets.
        
        Args:
            spell_id: The ID of the spell to use
            targets: The targets to apply the spell to
            location_magic: Optional magic profile of the current location
        
        Returns:
            Dict with result information
        """
        # Check if the spell is known
        if spell_id not in self.known_spells:
            return {
                "success": False,
                "message": f"Spell {spell_id} is not known"
            }
        
        # Get the spell from the magic system
        spell = MagicSystem.get_spell_by_id(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} not found in the magic system"
            }
        
        # Get character domains (in a real system, this would be passed in or retrieved)
        character_domains = MagicSystem.get_mock_domains(self.character_id)
        
        # Cast the spell
        return spell.cast(
            caster_id=self.character_id,
            caster_magic=self,
            caster_domains=character_domains,
            targets=targets,
            location_magic=location_magic
        )
    
    def perform_ritual(
        self,
        ritual_id: str,
        targets: List[Any],
        available_materials: Dict[str, int],
        participants_count: int,
        time_of_day: Optional[str] = None,
        location_type: Optional[str] = None,
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Perform a ritual.
        
        Args:
            ritual_id: The ID of the ritual to perform
            targets: The targets of the ritual
            available_materials: Dict of available materials (item_id: quantity)
            participants_count: Number of participants in the ritual
            time_of_day: Optional time of day
            location_type: Optional type of location
            location_magic: Optional magic profile of the current location
        
        Returns:
            Dict with result information
        """
        # Check if the ritual is known
        if ritual_id not in self.known_rituals:
            return {
                "success": False,
                "message": f"Ritual {ritual_id} is not known"
            }
        
        # Check if the character can perform rituals
        if not self.can_perform_rituals:
            return {
                "success": False,
                "message": "Cannot perform rituals"
            }
        
        # Get the ritual from the magic system
        ritual = MagicSystem.get_ritual_by_id(ritual_id)
        if not ritual:
            return {
                "success": False,
                "message": f"Ritual {ritual_id} not found in the magic system"
            }
        
        # Get character domains (in a real system, this would be passed in or retrieved)
        character_domains = MagicSystem.get_mock_domains(self.character_id)
        
        # Perform the ritual
        return ritual.perform_ritual(
            caster_id=self.character_id,
            caster_magic=self,
            caster_domains=character_domains,
            targets=targets,
            available_materials=available_materials,
            participants_count=participants_count,
            time_of_day=time_of_day,
            location_type=location_type,
            location_magic=location_magic
        )
    
    def learn_spell(self, spell_id: str) -> bool:
        """
        Learn a new spell. Returns True if learned successfully.
        """
        if spell_id in self.known_spells:
            return False
        
        self.known_spells.append(spell_id)
        return True
    
    def learn_ritual(self, ritual_id: str) -> bool:
        """
        Learn a new ritual. Returns True if learned successfully.
        """
        if not self.can_perform_rituals:
            return False
        
        if ritual_id in self.known_rituals:
            return False
        
        self.known_rituals.append(ritual_id)
        return True
    
    def apply_effect(self, effect: MagicalEffect) -> Dict[str, Any]:
        """
        Apply a magical effect to this character.
        """
        result = effect.apply(self)
        if effect.duration > 0:
            self.active_effects.append(effect)
        return result
    
    def update_active_effects(self) -> List[Dict[str, Any]]:
        """
        Update active effects, removing expired ones. Returns effects that expired.
        """
        expired_effects = []
        active_effects = []
        
        for effect in self.active_effects:
            if effect.is_active():
                active_effects.append(effect)
            else:
                expired_effects.append({
                    "effect_type": effect.effect_type.name,
                    "description": effect.description,
                    "message": f"The {effect.effect_type.name.lower()} effect has expired."
                })
        
        self.active_effects = active_effects
        return expired_effects
    
    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about the magic user."""
        return {
            "character_id": self.character_id,
            "has_mana_heart": self.has_mana_heart,
            "mana": {
                "current": self.mana_current,
                "max": self.mana_max,
                "regeneration_rate": self.mana_regeneration_rate
            },
            "ley_energy": {
                "current": self.current_ley_energy,
                "sensitivity": self.ley_energy_sensitivity
            },
            "known_spells_count": len(self.known_spells),
            "known_rituals_count": len(self.known_rituals),
            "can_perform_rituals": self.can_perform_rituals,
            "attunements": self.attunements,
            "active_effects_count": len(self.active_effects),
            "skills": {
                "enchanting": self.enchanting_skill,
                "ritual": self.ritual_skill
            },
            "mana_heart_development": self.mana_heart_development
        }

class MagicSystem:
    """
    Core magic system that manages spells, rituals, enchantments, and magical interactions.
    """
    
    # Class variables to store global spell, ritual, and enchantment data
    _spells: Dict[str, Spell] = {}
    _rituals: Dict[str, Ritual] = {}
    _enchantments: Dict[str, Enchantment] = {}
    
    def __init__(self):
        """Initialize the magic system."""
        self._initialize_default_spells()
        self._initialize_default_rituals()
        self._initialize_default_enchantments()
    
    def _initialize_default_spells(self):
        """Initialize default spells if not already loaded."""
        if not MagicSystem._spells:
            # Basic offensive spell
            fire_bolt = Spell(
                id="spell_fire_bolt",
                name="Fire Bolt",
                description="A bolt of fire that deals damage to a single target.",
                tier=MagicTier.APPRENTICE,
                mana_cost=10,
                ley_energy_cost=0,
                casting_time=1.0,
                effects=[
                    MagicalEffect(
                        effect_type=EffectType.DAMAGE,
                        potency=15,
                        duration=0,
                        damage_type=DamageType.FIRE,
                        description="Burns the target with magical fire."
                    )
                ],
                target_type=TargetType.SINGLE,
                range=30,
                domain_requirements=[
                    DomainRequirement(Domain.FIRE, 2)
                ],
                source=MagicSource.MANA,
                keywords=["fire", "damage", "offensive"]
            )
            MagicSystem._spells[fire_bolt.id] = fire_bolt
            
            # Basic defensive spell
            arcane_shield = Spell(
                id="spell_arcane_shield",
                name="Arcane Shield",
                description="Creates a shield of arcane energy that reduces damage.",
                tier=MagicTier.APPRENTICE,
                mana_cost=15,
                ley_energy_cost=0,
                casting_time=1.5,
                effects=[
                    MagicalEffect(
                        effect_type=EffectType.BUFF,
                        potency=10,
                        duration=60,
                        damage_type=DamageType.ARCANE,
                        description="Reduces incoming damage."
                    )
                ],
                target_type=TargetType.SELF,
                range=0,
                domain_requirements=[
                    DomainRequirement(Domain.MIND, 2)
                ],
                source=MagicSource.MANA,
                keywords=["arcane", "protection", "defensive"]
            )
            MagicSystem._spells[arcane_shield.id] = arcane_shield
            
            # Add more default spells as needed
    
    def _initialize_default_rituals(self):
        """Initialize default rituals if not already loaded."""
        if not MagicSystem._rituals:
            # Basic ritual
            communion_with_nature = Ritual(
                id="ritual_commune_with_nature",
                name="Communion with Nature",
                description="A ritual to commune with the natural spirits of an area.",
                tier=MagicTier.ADEPT,
                mana_cost=30,
                ley_energy_cost=10,
                casting_time=15.0,  # 15 minutes
                effects=[
                    MagicalEffect(
                        effect_type=EffectType.DIVINATION,
                        potency=20,
                        duration=3600,  # 1 hour
                        damage_type=None,
                        description="Allows the caster to sense and communicate with natural spirits."
                    )
                ],
                target_type=TargetType.AREA,
                range=100,
                domain_requirements=[
                    DomainRequirement(Domain.SPIRIT, 3),
                    DomainRequirement(Domain.AWARENESS, 2)
                ],
                material_requirements={
                    "herb_sacred_lotus": 2,
                    "incense_stick": 3
                },
                minimum_participants=1,
                ideal_time_of_day="dawn",
                ideal_location_type="natural",
                keywords=["nature", "divination", "spirits"]
            )
            MagicSystem._rituals[communion_with_nature.id] = communion_with_nature
            
            # Add more default rituals as needed
    
    def _initialize_default_enchantments(self):
        """Initialize default enchantments if not already loaded."""
        if not MagicSystem._enchantments:
            # Basic weapon enchantment
            flaming_weapon = Enchantment(
                id="enchant_flaming_weapon",
                name="Flaming Weapon",
                description="Enchants a weapon to deal additional fire damage.",
                tier=MagicTier.ADEPT,
                effects=[
                    "Adds 5 fire damage to attacks",
                    "Weapon emits light equivalent to a torch",
                    "Weapon ignites flammable materials on contact"
                ],
                duration=7,  # 7 days
                charges=None,  # Unlimited uses while active
                keywords=["fire", "weapon", "damage"]
            )
            MagicSystem._enchantments[flaming_weapon.id] = flaming_weapon
            
            # Add more default enchantments as needed
    
    @staticmethod
    def get_spell_by_id(spell_id: str) -> Optional[Spell]:
        """Get a spell by its ID."""
        return MagicSystem._spells.get(spell_id)
    
    @staticmethod
    def get_ritual_by_id(ritual_id: str) -> Optional[Ritual]:
        """Get a ritual by its ID."""
        return MagicSystem._rituals.get(ritual_id)
    
    @staticmethod
    def get_enchantment_by_id(enchantment_id: str) -> Optional[Enchantment]:
        """Get an enchantment by its ID."""
        return MagicSystem._enchantments.get(enchantment_id)
    
    @staticmethod
    def get_mock_domains(character_id: str) -> Dict[Domain, int]:
        """Get mock domains for a character (for testing purposes)."""
        # In a real system, this would retrieve domains from the character system
        return {
            Domain.BODY: 3,
            Domain.MIND: 4,
            Domain.CRAFT: 3,
            Domain.AWARENESS: 3,
            Domain.SOCIAL: 2,
            Domain.AUTHORITY: 2,
            Domain.SPIRIT: 4,
            Domain.FIRE: 2,
            Domain.WATER: 1,
            Domain.EARTH: 1,
            Domain.AIR: 1,
            Domain.LIGHT: 0,
            Domain.DARKNESS: 0
        }
    
    def initialize_magic_user(self, domains: Dict[Domain, int]) -> MagicUser:
        """
        Initialize a magic user profile based on their domains.
        
        Args:
            domains: The character's domain values
        
        Returns:
            A MagicUser profile
        """
        # Check if the character has the potential for a mana heart
        spirit_domain = domains.get(Domain.SPIRIT, 0)
        mind_domain = domains.get(Domain.MIND, 0)
        has_mana_heart = (spirit_domain >= 3 and mind_domain >= 2)
        
        # Calculate maximum mana based on domains
        base_mana = 20 if has_mana_heart else 10
        mind_bonus = mind_domain * 5
        spirit_bonus = spirit_domain * 8
        mana_max = base_mana + mind_bonus + spirit_bonus
        
        # Calculate mana regeneration rate
        base_regen = 0.1 if has_mana_heart else 0.05
        spirit_regen_bonus = spirit_domain * 0.05
        mana_regen = base_regen + spirit_regen_bonus
        
        # Calculate ley energy sensitivity
        awareness_domain = domains.get(Domain.AWARENESS, 0)
        base_sensitivity = 0.1
        awareness_bonus = awareness_domain * 0.05
        spirit_bonus = spirit_domain * 0.08
        ley_sensitivity = min(1.0, base_sensitivity + awareness_bonus + spirit_bonus)
        
        # Determine if the character can perform rituals
        ritual_capable = (spirit_domain >= 3 and awareness_domain >= 2)
        
        # Calculate enchanting skill
        craft_domain = domains.get(Domain.CRAFT, 0)
        enchanting_skill = min(100, craft_domain * 10 + mind_domain * 5 + spirit_domain * 5)
        
        # Calculate ritual skill
        ritual_skill = min(100, spirit_domain * 10 + awareness_domain * 5 + mind_domain * 5)
        
        # Determine attunements
        attunements = []
        for domain, value in domains.items():
            if domain in [Domain.FIRE, Domain.WATER, Domain.EARTH, Domain.AIR, Domain.LIGHT, Domain.DARKNESS]:
                if value >= 3:
                    attunements.append(domain.name.lower())
        
        # Create and return the magic user profile
        return MagicUser(
            character_id="test_character",  # This would be the actual character ID in a real system
            has_mana_heart=has_mana_heart,
            mana_max=mana_max,
            mana_current=mana_max // 2,  # Start with half mana
            mana_regeneration_rate=mana_regen,
            known_spells=[],  # No spells known initially
            known_rituals=[],  # No rituals known initially
            can_perform_rituals=ritual_capable,
            attunements=attunements,
            ley_energy_sensitivity=ley_sensitivity,
            current_ley_energy=0,
            enchanting_skill=enchanting_skill,
            ritual_skill=ritual_skill,
            mana_heart_development=1.0 if has_mana_heart else 0.0
        )
    
    def develop_mana_heart(self, character_id: str, magic_profile: MagicUser) -> Dict[str, Any]:
        """
        Develop a mana heart for a character.
        
        Args:
            character_id: The ID of the character
            magic_profile: The character's magic profile
        
        Returns:
            Dict with result information
        """
        # Check if already has a mana heart
        if magic_profile.has_mana_heart:
            return {
                "success": False,
                "message": "Already has a mana heart"
            }
        
        # Check if development is complete
        if magic_profile.mana_heart_development >= 1.0:
            magic_profile.has_mana_heart = True
            
            # Adjust mana stats
            previous_max = magic_profile.mana_max
            magic_profile.mana_max = int(magic_profile.mana_max * 1.5)
            magic_profile.mana_current = min(magic_profile.mana_current, magic_profile.mana_max)
            magic_profile.mana_regeneration_rate *= 1.3
            
            return {
                "success": True,
                "message": "Mana heart successfully developed!",
                "previous_mana_max": previous_max,
                "new_mana_max": magic_profile.mana_max,
                "new_mana_regen": magic_profile.mana_regeneration_rate
            }
        
        # In a real system, this would be a longer process involving quests,
        # training, or other game mechanics
        magic_profile.mana_heart_development = 1.0
        
        return self.develop_mana_heart(character_id, magic_profile)
    
    def get_available_spells(self, magic_profile: MagicUser) -> Dict[MagicTier, List[Dict[str, Any]]]:
        """
        Get available spells for a magic user, organized by tier.
        
        Args:
            magic_profile: The magic user's profile
        
        Returns:
            Dict of spells by tier, with info about whether they can be cast
        """
        # Get character domains (in a real system, this would be retrieved from the character)
        character_domains = self.get_mock_domains(magic_profile.character_id)
        
        # Organize spells by tier
        spells_by_tier = {}
        
        for tier in MagicTier:
            spells_by_tier[tier] = []
        
        # Check each spell
        for spell_id, spell in MagicSystem._spells.items():
            # Check if the spell can be cast
            can_cast, reason = spell.can_cast(magic_profile, character_domains)
            
            # Check if the spell is already known
            known = spell_id in magic_profile.known_spells
            
            # Add to the appropriate tier
            spells_by_tier[spell.tier].append({
                "id": spell_id,
                "name": spell.name,
                "description": spell.description,
                "mana_cost": spell.mana_cost,
                "ley_energy_cost": spell.ley_energy_cost,
                "known": known,
                "can_cast": can_cast,
                "reason": reason if not can_cast else ""
            })
        
        return spells_by_tier
    
    def learn_spell_from_study(self, character_id: str, spell_id: str, magic_profile: MagicUser) -> Dict[str, Any]:
        """
        Learn a spell through study.
        
        Args:
            character_id: The ID of the character
            spell_id: The ID of the spell to learn
            magic_profile: The character's magic profile
        
        Returns:
            Dict with result information
        """
        # Check if the spell is already known
        if spell_id in magic_profile.known_spells:
            return {
                "success": False,
                "message": f"The spell {spell_id} is already known."
            }
        
        # Get the spell
        spell = self.get_spell_by_id(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} not found in the magic system."
            }
        
        # Get character domains
        character_domains = self.get_mock_domains(character_id)
        
        # Check domain requirements
        for req in spell.domain_requirements:
            if not req.check_requirement(character_domains):
                return {
                    "success": False,
                    "message": f"Domain requirement not met: {req}"
                }
        
        # Check if the character has a mana heart if required
        if not magic_profile.has_mana_heart and spell.tier.value > MagicTier.CANTRIP.value:
            return {
                "success": False,
                "message": "You need a mana heart to learn spells above Cantrip tier."
            }
        
        # Learn the spell
        magic_profile.learn_spell(spell_id)
        
        return {
            "success": True,
            "message": f"Successfully learned the spell: {spell.name}",
            "spell": {
                "id": spell_id,
                "name": spell.name,
                "description": spell.description,
                "tier": spell.tier.name
            }
        }
    
    def initialize_location_magic(self, location_description: str) -> LocationMagicProfile:
        """
        Initialize a magic profile for a location based on its description.
        
        Args:
            location_description: A description of the location
        
        Returns:
            A LocationMagicProfile
        """
        # In a full implementation, this would use NLP or other techniques to
        # analyze the location description. For now, we'll use simple keyword matching.
        
        # Default values
        leyline_strength = 1.0
        mana_flux_level = ManaFluxLevel.LOW
        dominant_magic_aspects = []
        allows_ritual_sites = False
        
        # Check for leylines
        if "leyline" in location_description.lower():
            leyline_strength += 2.0
        
        # Check for magic flux indicators
        if "powerful" in location_description.lower() and "magic" in location_description.lower():
            mana_flux_level = ManaFluxLevel.HIGH
        elif "strong" in location_description.lower() and "magic" in location_description.lower():
            mana_flux_level = ManaFluxLevel.MEDIUM
        
        # Check for ritual sites
        if "shrine" in location_description.lower() or "altar" in location_description.lower():
            allows_ritual_sites = True
        
        # Check for magical aspects
        if "fire" in location_description.lower() or "flame" in location_description.lower():
            dominant_magic_aspects.append(DamageType.FIRE)
        
        if "water" in location_description.lower() or "river" in location_description.lower():
            dominant_magic_aspects.append(DamageType.WATER)
        
        if "earth" in location_description.lower() or "stone" in location_description.lower():
            dominant_magic_aspects.append(DamageType.EARTH)
        
        if "air" in location_description.lower() or "wind" in location_description.lower():
            dominant_magic_aspects.append(DamageType.AIR)
        
        if "arcane" in location_description.lower() or "magical" in location_description.lower():
            dominant_magic_aspects.append(DamageType.ARCANE)
        
        if "life" in location_description.lower() or "living" in location_description.lower():
            dominant_magic_aspects.append(DamageType.LIFE)
        
        # Ensure at least one dominant aspect
        if not dominant_magic_aspects:
            # Pick a random one
            dominant_magic_aspects.append(random.choice([
                DamageType.FIRE, DamageType.WATER, DamageType.EARTH, 
                DamageType.AIR, DamageType.ARCANE
            ]))
        
        return LocationMagicProfile(
            leyline_strength=leyline_strength,
            mana_flux_level=mana_flux_level,
            dominant_magic_aspects=dominant_magic_aspects,
            allows_ritual_sites=allows_ritual_sites
        )
    
    def create_magic_item(self, item_id: str, enchantment_id: Optional[str] = None) -> ItemMagicProfile:
        """
        Create a magic item profile.
        
        Args:
            item_id: The ID of the item
            enchantment_id: Optional ID of an enchantment to apply
        
        Returns:
            An ItemMagicProfile
        """
        # Default values
        is_enchanted = False
        enchantment = None
        mana_storage = 0
        ley_energy_capacity = 0
        
        # Apply enchantment if specified
        if enchantment_id:
            enchant = self.get_enchantment_by_id(enchantment_id)
            if enchant:
                is_enchanted = True
                enchantment = enchant
        
        # In a full implementation, item properties would be based on the item type,
        # materials, etc. For now, we'll use simple random values.
        
        # 20% chance of mana storage
        if random.random() < 0.2:
            mana_storage = random.randint(10, 50)
        
        # 10% chance of ley energy capacity
        if random.random() < 0.1:
            ley_energy_capacity = random.randint(5, 20)
        
        return ItemMagicProfile(
            item_id=item_id,
            is_enchanted=is_enchanted,
            enchantment_id=enchantment_id if is_enchanted else None,
            enchantment=enchantment,
            mana_storage_capacity=mana_storage,
            current_mana_stored=0,
            ley_energy_capacity=ley_energy_capacity,
            current_ley_energy=0
        )
    
    def get_environmental_effects(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Get magical environmental effects for a location.
        
        Args:
            location_id: The ID of the location
        
        Returns:
            List of environmental effect information
        """
        # In a full implementation, this would retrieve effects from the location
        # For now, we'll return some mock effects
        return [
            {
                "type": "positive",
                "name": "Mana Wellspring",
                "description": "The abundant magical energy accelerates mana regeneration.",
                "effect": "Mana regeneration increased by 50%"
            },
            {
                "type": "neutral",
                "name": "Arcane Resonance",
                "description": "The air shimmers with arcane energy, causing minor magical phenomena.",
                "effect": "Random minor magical effects may occur spontaneously"
            }
        ]