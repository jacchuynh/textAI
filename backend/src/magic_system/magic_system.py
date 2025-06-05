"""
Magic System for the RPG Game Engine.

This module implements a comprehensive magic system based on the world lore of
'The Crimson Dissonance' and the concepts of Leyweb and Mana Heart.
It fully integrates with the existing DomainSystem and CombatSystem.
"""

from enum import Enum, auto
from typing import Dict, List, Set, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import random
import uuid

# Import domain and combat systems
from backend.src.game_engine.domain_system import DomainSystem
from backend.src.game_engine.enhanced_combat.combat_system_core import Combatant, CombatMove, MoveType, Status, Domain
from backend.src.storage.character_storage import get_character
from backend.src.shared.models import Character, DomainType


# ======================================================================
# Core Magic System Enums
# ======================================================================

class MagicSource(Enum):
    """Sources of magical energy in the world"""
    LEYLINE = auto()       # External energy from the world's leylines
    MANA_HEART = auto()    # Internal, refined energy stored within the caster
    RELIC = auto()         # Energy contained within magical items/relics
    ENVIRONMENTAL = auto() # Natural magical energy in specific locations


class MagicTier(Enum):
    """Tiers of magical expression"""
    ARCANE_MASTERY = auto()   # Tier 1: True magic, requires Mana Heart
    MANA_INFUSION = auto()    # Tier 2: Enhanced abilities, partial access
    SPIRITUAL_UTILITY = auto() # Tier 3: Rituals, spirit communication


class EffectType(Enum):
    """Types of magical effects that can be produced"""
    DAMAGE = auto()          # Inflict damage on target
    HEAL = auto()            # Restore health to target
    BUFF_STAT = auto()       # Improve a stat temporarily
    DEBUFF_STAT = auto()     # Reduce a stat temporarily
    SUMMON = auto()          # Summon a creature or entity
    TELEPORT = auto()        # Move instantly between locations
    ILLUSION = auto()        # Create false sensory perceptions
    CONTROL = auto()         # Exert control over target
    WARD = auto()            # Create protective barriers
    SCRY = auto()            # Gain information or vision
    TRANSMUTE = auto()       # Change one substance to another
    CONJURE = auto()         # Create something from nothing
    BANISH = auto()          # Remove or send away
    CHARM = auto()           # Influence emotions or thoughts


class TargetType(Enum):
    """Types of targets a magical effect can affect"""
    SELF = auto()            # Affects only the caster
    SINGLE_ENEMY = auto()    # Affects a single opponent
    SINGLE_ALLY = auto()     # Affects a single ally
    AREA_ENEMIES = auto()    # Affects multiple enemies in an area
    AREA_ALLIES = auto()     # Affects multiple allies in an area
    AREA_ALL = auto()        # Affects everyone in an area
    ITEM = auto()            # Affects an item/object
    ENVIRONMENT = auto()     # Affects the environment
    LOCATION = auto()        # Affects a location


class DamageType(Enum):
    """Types of magical damage"""
    FIRE = auto()            # Burning, heat damage
    ICE = auto()             # Freezing, cold damage
    LIGHTNING = auto()       # Electrical damage
    EARTH = auto()           # Stone, crushing damage
    AIR = auto()             # Wind, pressure damage
    WATER = auto()           # Drowning, pressure damage
    LIGHT = auto()           # Radiant, divine damage
    DARKNESS = auto()        # Shadow, void damage
    ARCANE = auto()          # Pure magical energy
    NECROTIC = auto()        # Death, decay damage
    PSYCHIC = auto()         # Mental, mind damage
    SPIRITUAL = auto()       # Soul, essence damage


class ManaFluxLevel(Enum):
    """Intensity levels of mana flux in the environment"""
    DORMANT = 0              # Almost no magic present
    FAINT = 1                # Barely detectable magic
    MODERATE = 2             # Normal background magic
    STRONG = 3               # Elevated magical energy
    INTENSE = 4              # Highly active magical energy
    CHAOTIC = 5              # Unstable, dangerous levels


# ======================================================================
# Core Magic System Data Models
# ======================================================================

@dataclass
class DomainRequirement:
    """Requirement for a specific domain value"""
    domain: Domain
    minimum_value: int
    
    def is_met(self, combatant: Combatant) -> bool:
        """Check if the combatant meets this domain requirement"""
        if domain_value := combatant.domains.get(self.domain):
            return domain_value >= self.minimum_value
        return False


@dataclass
class RecipeIngredient:
    """Ingredient required for casting or crafting"""
    name: str
    quantity: int
    consumed: bool = True
    description: Optional[str] = None


@dataclass
class DomainCheckInfo:
    """Information for domain checks related to magic"""
    domain: Domain
    difficulty: int
    effect_on_success: Optional[str] = None
    effect_on_failure: Optional[str] = None


@dataclass
class ParticipantRequirement:
    """Requirements for ritual participants"""
    role: str
    minimum_count: int = 1
    domain_requirements: List[DomainRequirement] = field(default_factory=list)
    skill_requirements: List[str] = field(default_factory=list)


@dataclass
class MagicalEffect:
    """A specific magical effect that can be produced"""
    effect_type: EffectType
    description_template: str
    magnitude: Union[int, float, str]
    target_type: TargetType
    damage_type: Optional[DamageType] = None
    duration_seconds: Optional[int] = None
    associated_domain_checks: List[DomainCheckInfo] = field(default_factory=list)
    
    def apply_to_target(self, target: Combatant, caster: Combatant) -> Dict[str, Any]:
        """Apply this effect to the target and return the result"""
        result = {
            "success": True,
            "description": self.description_template,
            "applied_effect": self.effect_type.name,
            "magnitude": self.magnitude
        }
        
        # Handle different effect types
        if self.effect_type == EffectType.DAMAGE:
            if isinstance(self.magnitude, (int, float)):
                damage = int(self.magnitude)
                damage_dealt = target.take_damage(damage)
                result["actual_damage"] = damage_dealt
        
        elif self.effect_type == EffectType.HEAL:
            if isinstance(self.magnitude, (int, float)):
                heal_amount = int(self.magnitude)
                healing_done = target.heal(heal_amount) if hasattr(target, "heal") else 0
                result["actual_healing"] = healing_done
        
        elif self.effect_type == EffectType.BUFF_STAT:
            # Implementation for stat buffs would go here
            pass
        
        elif self.effect_type == EffectType.DEBUFF_STAT:
            # Implementation for stat debuffs would go here
            pass
        
        # Add more effect type implementations as needed
        
        return result


@dataclass
class ActiveMagicalEffect:
    """An active magical effect on a character or location"""
    effect_id: str
    source_effect: MagicalEffect
    remaining_duration: int  # in seconds
    source_spell_id: Optional[str] = None
    source_caster_id: Optional[str] = None
    
    def tick(self, seconds: int = 1) -> bool:
        """
        Reduce the remaining duration by the specified number of seconds.
        Returns True if the effect is still active, False if it has expired.
        """
        self.remaining_duration -= seconds
        return self.remaining_duration > 0


@dataclass
class Spell:
    """A magical spell that can be cast"""
    id: str
    name: str
    description: str
    tier: MagicTier
    magic_source_affinity: List[MagicSource]
    effects: List[MagicalEffect]
    mana_cost: Optional[int] = None
    ley_energy_cost: Optional[int] = None
    casting_time_seconds: int = 1
    components_required: List[RecipeIngredient] = field(default_factory=list)
    domain_requirements: List[DomainRequirement] = field(default_factory=list)
    skill_tag_requirements: List[str] = field(default_factory=list)
    backlash_potential: float = 0.0  # 0.0 to 1.0
    backlash_effects: List[MagicalEffect] = field(default_factory=list)
    is_ritual: bool = False
    lore_notes: Optional[str] = None
    
    def can_be_cast_by(self, caster: 'MagicUser') -> Tuple[bool, str]:
        """Check if this spell can be cast by the given caster"""
        # Check mana cost
        if self.mana_cost and (not caster.has_mana_heart or caster.mana_current < self.mana_cost):
            return False, f"Insufficient mana ({caster.mana_current}/{self.mana_cost})"
        
        # Check ley energy cost
        if self.ley_energy_cost and caster.current_ley_energy < self.ley_energy_cost:
            return False, f"Insufficient ley energy ({caster.current_ley_energy}/{self.ley_energy_cost})"
        
        # Check domain requirements
        for req in self.domain_requirements:
            domain_value = caster.domains.get(req.domain, 0)
            if domain_value < req.minimum_value:
                return False, f"Insufficient {req.domain.name} domain ({domain_value}/{req.minimum_value})"
        
        # Check skill requirements
        for skill in self.skill_tag_requirements:
            if skill not in caster.known_skills:
                return False, f"Missing required skill: {skill}"
        
        # Check for ritualistic requirements
        if self.is_ritual:
            # Rituals would have additional checks here
            pass
        
        return True, "Spell can be cast"
    
    def to_combat_move(self) -> CombatMove:
        """Convert this spell to a CombatMove for use in the combat system"""
        # Determine the appropriate move type based on the spell's effects
        move_type = MoveType.FOCUS  # Most spells are FOCUS-type actions
        
        # Create domains list based on domain requirements
        domains = [req.domain for req in self.domain_requirements]
        if not domains:
            domains = [Domain.SPIRIT]  # Default to SPIRIT if no specific domains
        
        # Calculate base damage from effects
        base_damage = 0
        for effect in self.effects:
            if effect.effect_type == EffectType.DAMAGE and isinstance(effect.magnitude, (int, float)):
                base_damage += int(effect.magnitude)
        
        # Create the combat move
        return CombatMove(
            name=self.name,
            description=self.description,
            move_type=move_type,
            domains=domains,
            base_damage=base_damage,
            stamina_cost=0,
            focus_cost=self.mana_cost or 0,
            spirit_cost=self.ley_energy_cost or 0,
            effects=[effect.effect_type.name for effect in self.effects if effect.effect_type]
        )


@dataclass
class Ritual(Spell):
    """A magical ritual that extends spell functionality"""
    duration_minutes: int = 0
    participant_requirements: List[ParticipantRequirement] = field(default_factory=list)
    location_requirements: List[str] = field(default_factory=list)
    time_of_day_requirements: Optional[str] = None
    
    def __post_init__(self):
        """Ensure ritual flag is set"""
        self.is_ritual = True


@dataclass
class Enchantment:
    """A magical enhancement that can be applied to items"""
    id: str
    name: str
    description: str
    tier: MagicTier
    applied_effects: List[MagicalEffect]
    passive_or_triggered: str  # e.g., "ON_HIT", "PASSIVE_WHILE_EQUIPPED", "ON_USE"
    recipe_id: Optional[str] = None
    
    def apply_triggered_effect(self, triggering_event: str, wielder: Combatant, target: Combatant) -> Optional[Dict[str, Any]]:
        """Apply a triggered effect if the triggering event matches"""
        if triggering_event != self.passive_or_triggered:
            return None
        
        results = []
        for effect in self.applied_effects:
            result = effect.apply_to_target(target, wielder)
            results.append(result)
        
        return {
            "enchantment_name": self.name,
            "triggered_by": triggering_event,
            "effect_results": results
        }


@dataclass
class MagicUser:
    """Magic user profile for a character"""
    # Basic magic attributes
    has_mana_heart: bool = False
    mana_current: int = 0
    mana_max: int = 0
    mana_regeneration_rate: float = 0.0
    
    # Ley energy attributes
    ley_energy_sensitivity: int = 0  # 0-10 scale
    current_ley_energy: int = 0
    
    # Knowledge and abilities
    known_spells: List[str] = field(default_factory=list)
    known_rituals: List[str] = field(default_factory=list)
    known_skills: List[str] = field(default_factory=list)
    
    # Status tracking
    active_magical_effects: List[ActiveMagicalEffect] = field(default_factory=list)
    corruption_level: int = 0  # 0-100 scale
    attunements: List[str] = field(default_factory=list)
    
    def regenerate_mana(self, seconds: int = 1) -> int:
        """Regenerate mana over time, returns amount regenerated"""
        if not self.has_mana_heart or self.mana_current >= self.mana_max:
            return 0
        
        regen_amount = int(self.mana_regeneration_rate * seconds)
        self.mana_current = min(self.mana_current + regen_amount, self.mana_max)
        return regen_amount
    
    def draw_from_leyline(self, leyline_strength: int, amount_desired: int, character: Optional['Character'] = None) -> int:
        """
        Attempt to draw energy from a leyline
        Returns the amount of energy successfully drawn
        """
        # Calculate amount drawn
        max_draw = leyline_strength * 5
        amount_drawn = min(amount_desired, max_draw)
        
        if character:
            # Use enhanced roll system for leyline drawing
            base_difficulty = 8  # Base difficulty for leyline drawing
            difficulty = base_difficulty - leyline_strength  # Stronger leylines are easier
            difficulty += max(0, amount_desired // 10)  # Harder to draw large amounts
            
            # Use Spirit domain for leyline connection, with Mind as secondary
            from backend.src.shared.models import DomainType
            result = character.roll_check_hybrid(
                primary_domain=DomainType.SPIRIT,
                secondary_domain=DomainType.MIND,
                difficulty=difficulty,
                context="drawing energy from leyline"
            )
            
            if result['success']:
                self.current_ley_energy += amount_drawn
                
                # Critical success might draw extra energy or reduce corruption risk
                if result['is_critical_success']:
                    bonus_energy = min(amount_drawn // 4, 5)
                    self.current_ley_energy += bonus_energy
                    amount_drawn += bonus_energy
                
                return amount_drawn
            else:
                # Check for backlash on failure
                backlash_difficulty = 10 + self.ley_energy_sensitivity
                backlash_result = character.roll_check_hybrid(
                    primary_domain=DomainType.SPIRIT,
                    secondary_domain=DomainType.BODY,
                    difficulty=backlash_difficulty,
                    context="resisting leyline backlash"
                )
                
                if not backlash_result['success']:
                    self.corruption_level += 1
                    if backlash_result['is_critical_failure']:
                        self.corruption_level += 1  # Extra corruption on critical failure
                
                return 0
        else:
            # Fallback to original probability system if no character provided
            base_chance = 0.3 + (0.05 * self.ley_energy_sensitivity) + (0.1 * leyline_strength)
            success_chance = min(base_chance, 0.9)  # Cap at 90%
            
            # Check for success
            if random.random() <= success_chance:
                self.current_ley_energy += amount_drawn
                return amount_drawn
            else:
                # Failed attempt
                backlash_chance = 0.2 - (0.02 * self.ley_energy_sensitivity)
                if random.random() <= backlash_chance:
                    # Backlash occurs
                    self.corruption_level += 1
                return 0
    
    def use_mana(self, amount: int) -> bool:
        """
        Use mana for a spell or ability
        Returns True if successful, False if insufficient mana
        """
        if self.mana_current < amount:
            return False
        
        self.mana_current -= amount
        return True
    
    def use_ley_energy(self, amount: int) -> bool:
        """
        Use ley energy for a spell or ability
        Returns True if successful, False if insufficient energy
        """
        if self.current_ley_energy < amount:
            return False
        
        self.current_ley_energy -= amount
        return True


@dataclass
class LocationMagicProfile:
    """Magical properties of a location"""
    leyline_strength: int = 0  # 0-5 scale
    mana_flux_level: ManaFluxLevel = ManaFluxLevel.MODERATE
    dominant_magic_aspects: List[DamageType] = field(default_factory=list)
    environmental_decay_level: int = 0  # 0-5 scale, due to corruption
    allows_ritual_sites: bool = False
    historical_magic_events: List[str] = field(default_factory=list)


@dataclass
class ItemMagicProfile:
    """Magical properties of an item"""
    is_enchanted: bool = False
    enchantment_id: Optional[str] = None
    is_relic: bool = False
    relic_power_description: Optional[str] = None
    relic_effects: List[MagicalEffect] = field(default_factory=list)
    mana_cost_to_activate: Optional[int] = None
    charges: Optional[int] = None
    attunement_required: bool = False
    cursed_or_corrupted: bool = False


# ======================================================================
# Magic System Service Classes
# ======================================================================

class MagicCastingService:
    """Service for handling the casting of spells and magical effects"""
    
    def __init__(self, spell_repository: Dict[str, Spell] = None):
        """Initialize the magic casting service"""
        self.spells = spell_repository or {}
        self.active_rituals = {}
    
    def register_spell(self, spell: Spell) -> None:
        """Register a spell with the service"""
        self.spells[spell.id] = spell
    
    def get_spell(self, spell_id: str) -> Optional[Spell]:
        """Get a spell by ID"""
        return self.spells.get(spell_id)
    
    def learn_spell(self, character_id: str, spell_id: str, character_magic_profile: MagicUser) -> Tuple[bool, str]:
        """
        Add a spell to a character's known spells with basic requirements check
        Returns (success, message)
        """
        if spell_id not in self.spells:
            return False, f"Spell {spell_id} does not exist"
        
        if spell_id in character_magic_profile.known_spells:
            return False, f"Already knows spell {self.spells[spell_id].name}"
        
        spell = self.spells[spell_id]
        
        # Check basic requirements for the spell
        can_cast, reason = spell.can_be_cast_by(character_magic_profile)
        if not can_cast and "mana" not in reason.lower():
            # Allow learning even if can't cast due to mana, but not for other requirements
            return False, f"Cannot learn {spell.name}: {reason}"
        
        # Add the spell to the character's known spells
        character_magic_profile.known_spells.append(spell_id)
        return True, f"Learned new spell: {self.spells[spell_id].name}"
    
    def can_cast_spell(self, character_magic_profile: MagicUser, spell_id: str) -> Tuple[bool, str]:
        """
        Check if a character can cast a specific spell
        Returns (can_cast, reason)
        """
        # Check if the spell exists
        spell = self.get_spell(spell_id)
        if not spell:
            return False, f"Spell {spell_id} does not exist"
        
        # Check if the character knows the spell
        if spell_id not in character_magic_profile.known_spells:
            return False, f"You don't know the spell {spell.name}"
        
        # Check spell-specific requirements
        return spell.can_be_cast_by(character_magic_profile)
    
    def cast_spell(self, 
                  caster: Combatant, 
                  caster_magic_profile: MagicUser,
                  spell_id: str, 
                  targets: List[Combatant], 
                  location_magic_profile: LocationMagicProfile,
                  character: Optional['Character'] = None) -> Dict[str, Any]:
        """
        Cast a spell and apply its effects
        Returns a result dictionary with details about the casting
        """
        # Get the spell
        spell = self.get_spell(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} does not exist"
            }
        
        # Check if the spell can be cast
        can_cast, reason = self.can_cast_spell(caster_magic_profile, spell_id)
        if not can_cast:
            return {
                "success": False,
                "message": reason
            }
        
        # Consume resources
        if spell.mana_cost:
            caster_magic_profile.use_mana(spell.mana_cost)
        
        if spell.ley_energy_cost:
            caster_magic_profile.use_ley_energy(spell.ley_energy_cost)
        
        # Check for backlash using enhanced roll system
        backlash_occurred = False
        backlash_results = []
        
        if character and spell.backlash_potential > 0:
            # Calculate difficulty for resisting backlash
            base_difficulty = int(spell.backlash_potential * 20)  # Convert to difficulty scale
            flux_modifier = (location_magic_profile.mana_flux_level.value - 2) * 2  # MODERATE is baseline
            corruption_modifier = caster_magic_profile.corruption_level
            
            backlash_resistance_difficulty = base_difficulty + flux_modifier + corruption_modifier
            
            # Use Spirit as primary (magical resistance) and Mind as secondary (concentration)
            from backend.src.shared.models import DomainType
            resistance_result = character.roll_check_hybrid(
                primary_domain=DomainType.SPIRIT,
                secondary_domain=DomainType.MIND,
                difficulty=backlash_resistance_difficulty,
                context=f"resisting backlash from {spell.name}"
            )
            
            if not resistance_result['success']:
                backlash_occurred = True
                # Apply backlash effects if any
                for effect in spell.backlash_effects:
                    result = effect.apply_to_target(caster, caster)
                    backlash_results.append(result)
                
                # Increase corruption from backlash
                corruption_increase = 1
                if resistance_result['is_critical_failure']:
                    corruption_increase = 2  # More corruption on critical failure
                caster_magic_profile.corruption_level += corruption_increase
        elif spell.backlash_potential > 0:
            # Fallback to original probability system if no character provided
            base_backlash_chance = spell.backlash_potential
            flux_modifier = 0.05 * (location_magic_profile.mana_flux_level.value - 2)  # MODERATE is baseline
            corruption_modifier = 0.01 * caster_magic_profile.corruption_level
            
            final_backlash_chance = base_backlash_chance + flux_modifier + corruption_modifier
            
            if random.random() < final_backlash_chance:
                backlash_occurred = True
                # Apply backlash effects if any
                for effect in spell.backlash_effects:
                    result = effect.apply_to_target(caster, caster)
                    backlash_results.append(result)
                
                # Increase corruption from backlash
                caster_magic_profile.corruption_level += 1
        
        # Apply spell effects to targets
        effect_results = []
        for target in targets:
            target_results = []
            for effect in spell.effects:
                # Check if the target type matches
                # (this is a simplified version - would need more logic for area effects)
                target_type = effect.target_type
                valid_target = (
                    (target_type == TargetType.SELF and target == caster) or
                    (target_type == TargetType.SINGLE_ENEMY and target != caster) or
                    (target_type == TargetType.SINGLE_ALLY and target != caster)  # This is not fully correct, need ally check
                )
                
                if valid_target:
                    result = effect.apply_to_target(target, caster)
                    target_results.append(result)
            
            effect_results.append({
                "target_name": target.name,
                "results": target_results
            })
        
        # Create the final result
        result = {
            "success": True,
            "spell_name": spell.name,
            "caster_name": caster.name,
            "targets_affected": len(targets),
            "effect_results": effect_results,
            "backlash_occurred": backlash_occurred
        }
        
        if backlash_occurred:
            result["backlash_results"] = backlash_results
        
        return result


class RitualService:
    """Service for handling magical rituals"""
    
    def __init__(self, ritual_repository: Dict[str, Ritual] = None):
        """Initialize the ritual service"""
        self.rituals = ritual_repository or {}
        self.active_rituals = {}
    
    def register_ritual(self, ritual: Ritual) -> None:
        """Register a ritual with the service"""
        self.rituals[ritual.id] = ritual
    
    def get_ritual(self, ritual_id: str) -> Optional[Ritual]:
        """Get a ritual by ID"""
        return self.rituals.get(ritual_id)
    
    def learn_ritual(self, character_id: str, ritual_id: str, character_magic_profile: MagicUser) -> Tuple[bool, str]:
        """
        Add a ritual to a character's known rituals
        Returns (success, message)
        """
        if ritual_id not in self.rituals:
            return False, f"Ritual {ritual_id} does not exist"
        
        if ritual_id in character_magic_profile.known_rituals:
            return False, f"Already knows ritual {self.rituals[ritual_id].name}"
        
        # Add the ritual to the character's known rituals
        character_magic_profile.known_rituals.append(ritual_id)
        return True, f"Learned new ritual: {self.rituals[ritual_id].name}"
    
    def initiate_ritual(self, 
                       leader_id: str,
                       leader_magic_profile: MagicUser,
                       ritual_id: str,
                       participants: Dict[str, MagicUser],
                       location_magic_profile: LocationMagicProfile) -> Dict[str, Any]:
        """
        Initiate a ritual
        Returns a result dictionary with details about the initiation
        """
        # Get the ritual
        ritual = self.get_ritual(ritual_id)
        if not ritual:
            return {
                "success": False,
                "message": f"Ritual {ritual_id} does not exist"
            }
        
        # Check if the leader knows the ritual
        if ritual_id not in leader_magic_profile.known_rituals:
            return {
                "success": False,
                "message": f"You don't know the ritual {ritual.name}"
            }
        
        # Check location requirements
        if not location_magic_profile.allows_ritual_sites:
            return {
                "success": False,
                "message": "This location is not suitable for rituals"
            }
        
        for req in ritual.location_requirements:
            if req not in location_magic_profile.historical_magic_events:
                return {
                    "success": False,
                    "message": f"This location lacks the required property: {req}"
                }
        
        # Check participant requirements
        for req in ritual.participant_requirements:
            # Count participants that match this role
            matching_participants = 0
            for p_id, profile in participants.items():
                # This is simplified - would need more logic to match roles
                matching_participants += 1
            
            if matching_participants < req.minimum_count:
                return {
                    "success": False,
                    "message": f"Need at least {req.minimum_count} participants for role {req.role}, but only have {matching_participants}"
                }
        
        # Check resource requirements
        if ritual.mana_cost and leader_magic_profile.mana_current < ritual.mana_cost:
            return {
                "success": False,
                "message": f"Insufficient mana to initiate the ritual ({leader_magic_profile.mana_current}/{ritual.mana_cost})"
            }
        
        if ritual.ley_energy_cost and leader_magic_profile.current_ley_energy < ritual.ley_energy_cost:
            return {
                "success": False,
                "message": f"Insufficient ley energy to initiate the ritual ({leader_magic_profile.current_ley_energy}/{ritual.ley_energy_cost})"
            }
        
        # Consume initial resources
        if ritual.mana_cost:
            leader_magic_profile.use_mana(ritual.mana_cost)
        
        if ritual.ley_energy_cost:
            leader_magic_profile.use_ley_energy(ritual.ley_energy_cost)
        
        # Create a unique ID for this ritual attempt
        ritual_attempt_id = str(uuid.uuid4())
        
        # Store the active ritual
        self.active_rituals[ritual_attempt_id] = {
            "ritual_id": ritual_id,
            "leader_id": leader_id,
            "participants": list(participants.keys()),
            "start_time": 0,  # Would use actual timestamp in real implementation
            "current_stage": 0,
            "total_stages": 3,  # Simplified - would be derived from ritual complexity
            "completed_actions": [],
            "status": "initiated"
        }
        
        return {
            "success": True,
            "message": f"Ritual {ritual.name} initiated successfully",
            "ritual_attempt_id": ritual_attempt_id,
            "estimated_duration_minutes": ritual.duration_minutes
        }
    
    def advance_ritual_stage(self, ritual_attempt_id: str, action_taken: str) -> Dict[str, Any]:
        """
        Advance a ritual to the next stage
        Returns a result dictionary with details about the advancement
        """
        # Get the active ritual
        ritual_attempt = self.active_rituals.get(ritual_attempt_id)
        if not ritual_attempt:
            return {
                "success": False,
                "message": f"No active ritual with ID {ritual_attempt_id}"
            }
        
        # Get the ritual definition
        ritual = self.get_ritual(ritual_attempt["ritual_id"])
        if not ritual:
            return {
                "success": False,
                "message": f"Ritual definition not found"
            }
        
        # Record the action
        ritual_attempt["completed_actions"].append(action_taken)
        
        # Advance the stage
        ritual_attempt["current_stage"] += 1
        
        # Check if the ritual is complete
        if ritual_attempt["current_stage"] >= ritual_attempt["total_stages"]:
            ritual_attempt["status"] = "completed"
            result = {
                "success": True,
                "message": f"Ritual {ritual.name} completed successfully",
                "status": "completed",
                "ritual_name": ritual.name
            }
        else:
            result = {
                "success": True,
                "message": f"Ritual {ritual.name} advanced to stage {ritual_attempt['current_stage'] + 1}/{ritual_attempt['total_stages']}",
                "status": "in_progress",
                "current_stage": ritual_attempt["current_stage"] + 1,
                "total_stages": ritual_attempt["total_stages"],
                "ritual_name": ritual.name
            }
        
        return result
    
    def conclude_ritual(self, ritual_attempt_id: str) -> Dict[str, Any]:
        """
        Conclude a completed ritual and apply its effects
        Returns a result dictionary with details about the conclusion
        """
        # Get the active ritual
        ritual_attempt = self.active_rituals.get(ritual_attempt_id)
        if not ritual_attempt:
            return {
                "success": False,
                "message": f"No active ritual with ID {ritual_attempt_id}"
            }
        
        # Check if the ritual is completed
        if ritual_attempt["status"] != "completed":
            return {
                "success": False,
                "message": f"Ritual is not yet completed (status: {ritual_attempt['status']})"
            }
        
        # Get the ritual definition
        ritual = self.get_ritual(ritual_attempt["ritual_id"])
        if not ritual:
            return {
                "success": False,
                "message": f"Ritual definition not found"
            }
        
        # Apply ritual effects (simplified - would need actual targets and effects)
        result = {
            "success": True,
            "message": f"Ritual {ritual.name} concluded successfully",
            "ritual_name": ritual.name,
            "effects_applied": [effect.effect_type.name for effect in ritual.effects]
        }
        
        # Remove from active rituals
        del self.active_rituals[ritual_attempt_id]
        
        return result


class CorruptionService:
    """Service for handling magical corruption"""
    
    def apply_corruption(self, character_id: str, amount: int, source: str, character_magic_profile: MagicUser) -> int:
        """
        Apply corruption to a character
        Returns the new corruption level
        """
        character_magic_profile.corruption_level += amount
        
        # Cap corruption at 100
        if character_magic_profile.corruption_level > 100:
            character_magic_profile.corruption_level = 100
        
        return character_magic_profile.corruption_level
    
    def get_corruption_effects(self, character_magic_profile: MagicUser) -> List[Dict[str, Any]]:
        """
        Get the effects of a character's corruption level
        Returns a list of effect dictionaries
        """
        effects = []
        
        # Define corruption thresholds and their effects
        if character_magic_profile.corruption_level >= 10:
            effects.append({
                "name": "Minor Corruption",
                "description": "Slight physical changes, occasional whispers",
                "mechanical_effect": "Perception checks against you have +1 bonus"
            })
        
        if character_magic_profile.corruption_level >= 30:
            effects.append({
                "name": "Moderate Corruption",
                "description": "Visible physical changes, constant whispers",
                "mechanical_effect": "Social penalties in civilized areas, +2 to intimidation"
            })
        
        if character_magic_profile.corruption_level >= 50:
            effects.append({
                "name": "Severe Corruption",
                "description": "Dramatic physical changes, vivid hallucinations",
                "mechanical_effect": "Occasional loss of control, but +2 to magic damage"
            })
        
        if character_magic_profile.corruption_level >= 70:
            effects.append({
                "name": "Extreme Corruption",
                "description": "Monstrous appearance, mind increasingly alien",
                "mechanical_effect": "Risk of becoming NPC, but access to forbidden magic"
            })
        
        if character_magic_profile.corruption_level >= 90:
            effects.append({
                "name": "Complete Corruption",
                "description": "Barely recognizable as former self",
                "mechanical_effect": "Character becomes NPC, lost to corruption"
            })
        
        return effects
    
    def attempt_purification_ritual(self, 
                                   character_id: str, 
                                   ritual_id: str, 
                                   character_magic_profile: MagicUser,
                                   ritual_service: 'RitualService',
                                   character: Optional['Character'] = None) -> Tuple[bool, str, int]:
        """
        Attempt to reduce corruption through a purification ritual
        Returns (success, message, amount_reduced)
        """
        # Get the ritual
        ritual = ritual_service.get_ritual(ritual_id)
        if not ritual:
            return False, f"Ritual {ritual_id} does not exist", 0
        
        # Check if it's a purification ritual (simplified)
        if "purification" not in ritual.name.lower() and "cleansing" not in ritual.name.lower():
            return False, f"The ritual {ritual.name} is not a purification ritual", 0
        
        if character:
            # Use enhanced roll system for purification ritual
            base_difficulty = 10 + (character_magic_profile.corruption_level // 5)  # Harder with more corruption
            
            # Spirit is primary for purification, Mind secondary for focus
            from backend.src.shared.models import DomainType
            purification_result = character.roll_check_hybrid(
                primary_domain=DomainType.SPIRIT,
                secondary_domain=DomainType.MIND,
                difficulty=base_difficulty,
                context=f"performing {ritual.name}"
            )
            
            if purification_result['success']:
                # Base reduction modified by success margin
                base_reduction = 3
                margin_bonus = min(purification_result['margin_of_success'] // 3, 5)
                critical_bonus = 3 if purification_result['is_critical_success'] else 0
                
                total_reduction = base_reduction + margin_bonus + critical_bonus
                
                # Apply the reduction
                original_corruption = character_magic_profile.corruption_level
                character_magic_profile.corruption_level = max(0, character_magic_profile.corruption_level - total_reduction)
                actual_reduction = original_corruption - character_magic_profile.corruption_level
                
                success_message = f"Purification successful. Corruption reduced by {actual_reduction} points"
                if purification_result['is_critical_success']:
                    success_message += " (Exceptional purification achieved!)"
                
                return True, success_message, actual_reduction
            else:
                # Failure - no reduction, possible complications
                failure_message = f"Purification ritual failed"
                
                if purification_result['is_critical_failure']:
                    # Critical failure might increase corruption or have other consequences
                    character_magic_profile.corruption_level += 1
                    failure_message += " (The ritual backfired, increasing corruption!)"
                else:
                    failure_message += " (No purification occurred)"
                
                return False, failure_message, 0
        else:
            # Fallback to simple success for backward compatibility
            base_reduction = 5
            spirit_bonus = 0  # Would calculate from domain values
            
            total_reduction = base_reduction + spirit_bonus
            
            # Apply the reduction
            original_corruption = character_magic_profile.corruption_level
            character_magic_profile.corruption_level = max(0, character_magic_profile.corruption_level - total_reduction)
            actual_reduction = original_corruption - character_magic_profile.corruption_level
            
            return True, f"Purification successful. Corruption reduced by {actual_reduction} points", actual_reduction


class MagicalPhenomenaService:
    """Service for handling magical phenomena in the world"""
    
    def handle_environmental_magic_effect(self, location_id: str, effect: MagicalEffect, location_magic_profile: LocationMagicProfile) -> Dict[str, Any]:
        """
        Apply a magical effect to the environment
        Returns a result dictionary
        """
        result = {
            "success": True,
            "location_id": location_id,
            "effect_type": effect.effect_type.name,
            "description": effect.description_template
        }
        
        # Handle different effects on the environment
        if effect.effect_type == EffectType.DAMAGE:
            # Environmental damage could increase decay level
            if location_magic_profile.environmental_decay_level < 5:  # Max 5
                location_magic_profile.environmental_decay_level += 1
                result["environmental_change"] = f"Decay level increased to {location_magic_profile.environmental_decay_level}"
        
        elif effect.effect_type == EffectType.HEAL:
            # Healing effects could reduce decay
            if location_magic_profile.environmental_decay_level > 0:
                location_magic_profile.environmental_decay_level -= 1
                result["environmental_change"] = f"Decay level decreased to {location_magic_profile.environmental_decay_level}"
        
        # Add more effect types as needed
        
        return result
    
    def update_leyline_flux(self, location_id: str, change: int, reason: str, location_magic_profile: LocationMagicProfile) -> Dict[str, Any]:
        """
        Update the leyline strength and mana flux in a location
        Returns a result dictionary
        """
        # Update leyline strength
        original_strength = location_magic_profile.leyline_strength
        location_magic_profile.leyline_strength = max(0, min(5, location_magic_profile.leyline_strength + change))
        
        # Update mana flux level based on the change
        flux_change = 0
        if abs(change) >= 3:
            # Large changes can make flux chaotic
            location_magic_profile.mana_flux_level = ManaFluxLevel.CHAOTIC
            flux_change = 5 - location_magic_profile.mana_flux_level.value  # Amount to reach CHAOTIC
        elif change > 0:
            # Increase flux by one level if not already at max
            if location_magic_profile.mana_flux_level.value < 5:
                new_flux_value = location_magic_profile.mana_flux_level.value + 1
                location_magic_profile.mana_flux_level = ManaFluxLevel(new_flux_value)
                flux_change = 1
        elif change < 0:
            # Decrease flux by one level if not already at min
            if location_magic_profile.mana_flux_level.value > 0:
                new_flux_value = location_magic_profile.mana_flux_level.value - 1
                location_magic_profile.mana_flux_level = ManaFluxLevel(new_flux_value)
                flux_change = -1
        
        return {
            "success": True,
            "location_id": location_id,
            "original_leyline_strength": original_strength,
            "new_leyline_strength": location_magic_profile.leyline_strength,
            "leyline_change": location_magic_profile.leyline_strength - original_strength,
            "new_mana_flux_level": location_magic_profile.mana_flux_level.name,
            "flux_change": flux_change,
            "reason": reason
        }


class EnchantmentService:
    """Service for handling magical enchantments on items"""
    
    def __init__(self, enchantment_repository: Dict[str, Enchantment] = None):
        """Initialize the enchantment service"""
        self.enchantments = enchantment_repository or {}
    
    def register_enchantment(self, enchantment: Enchantment) -> None:
        """Register an enchantment with the service"""
        self.enchantments[enchantment.id] = enchantment
    
    def get_enchantment(self, enchantment_id: str) -> Optional[Enchantment]:
        """Get an enchantment by ID"""
        return self.enchantments.get(enchantment_id)
    
    def apply_enchantment_to_item(self, item_id: str, enchantment_id: str, item_magic_profile: ItemMagicProfile) -> Tuple[bool, str]:
        """
        Apply an enchantment to an item
        Returns (success, message)
        """
        # Check if the enchantment exists
        enchantment = self.get_enchantment(enchantment_id)
        if not enchantment:
            return False, f"Enchantment {enchantment_id} does not exist"
        
        # Check if the item is already enchanted
        if item_magic_profile.is_enchanted:
            return False, f"Item is already enchanted"
        
        # Apply the enchantment
        item_magic_profile.is_enchanted = True
        item_magic_profile.enchantment_id = enchantment_id
        
        return True, f"Successfully applied enchantment {enchantment.name} to the item"
    
    def create_relic(self, item_id: str, name: str, description: str, effects: List[MagicalEffect], item_magic_profile: ItemMagicProfile) -> Tuple[bool, str]:
        """
        Create a magical relic
        Returns (success, message)
        """
        # Check if the item is already a relic
        if item_magic_profile.is_relic:
            return False, f"Item is already a relic"
        
        # Create the relic
        item_magic_profile.is_relic = True
        item_magic_profile.relic_power_description = description
        item_magic_profile.relic_effects = effects
        
        return True, f"Successfully created relic: {name}"
    
    def use_enchanted_item(self, item_id: str, user: Combatant, target: Combatant, item_magic_profile: ItemMagicProfile) -> Dict[str, Any]:
        """
        Use an enchanted item and apply its effects
        Returns a result dictionary
        """
        # Check if the item is enchanted
        if not item_magic_profile.is_enchanted and not item_magic_profile.is_relic:
            return {
                "success": False,
                "message": "Item is not magical"
            }
        
        # Check charges if applicable
        if item_magic_profile.charges is not None and item_magic_profile.charges <= 0:
            return {
                "success": False,
                "message": "Item has no charges remaining"
            }
        
        # Get the enchantment or relic effects
        effects = []
        if item_magic_profile.is_enchanted and item_magic_profile.enchantment_id:
            enchantment = self.get_enchantment(item_magic_profile.enchantment_id)
            if enchantment:
                effects = enchantment.applied_effects
        elif item_magic_profile.is_relic:
            effects = item_magic_profile.relic_effects
        
        # Apply effects
        results = []
        for effect in effects:
            result = effect.apply_to_target(target, user)
            results.append(result)
        
        # Reduce charges if applicable
        if item_magic_profile.charges is not None:
            item_magic_profile.charges -= 1
        
        return {
            "success": True,
            "item_id": item_id,
            "user_name": user.name,
            "target_name": target.name,
            "effect_results": results,
            "charges_remaining": item_magic_profile.charges
        }


# ======================================================================
# Magic System Integration Points
# ======================================================================

class MagicSystem:
    """
    Main magic system class that integrates all magical services.
    
    This class provides a unified interface for interacting with the magic system
    and coordinates between the various magical services.
    """
    
    def __init__(self):
        """Initialize the magic system"""
        # Initialize services
        self.casting_service = MagicCastingService()
        self.ritual_service = RitualService()
        self.corruption_service = CorruptionService()
        self.phenomena_service = MagicalPhenomenaService()
        self.enchantment_service = EnchantmentService()
        
        # Register basic spells, rituals, and enchantments
        self._register_basic_content()
    
    def _register_basic_content(self):
        """Register basic magical content for the system"""
        # Create and register some basic spells
        self._register_basic_spells()
        
        # Create and register some basic rituals
        self._register_basic_rituals()
        
        # Create and register some basic enchantments
        self._register_basic_enchantments()
    
    def _register_basic_spells(self):
        """Register basic spells with the system"""
        # Tier 1: Arcane Mastery (Mana Heart) spells
        
        # Fireball spell
        fireball = Spell(
            id="spell_fireball",
            name="Fireball",
            description="Conjures a ball of roaring flame that explodes on impact",
            tier=MagicTier.ARCANE_MASTERY,
            magic_source_affinity=[MagicSource.MANA_HEART],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.DAMAGE,
                    description_template="A ball of fire erupts, engulfing the target in flames",
                    magnitude=15,
                    target_type=TargetType.SINGLE_ENEMY,
                    damage_type=DamageType.FIRE
                )
            ],
            mana_cost=10,
            casting_time_seconds=2,
            domain_requirements=[
                DomainRequirement(domain=Domain.MIND, minimum_value=3),
                DomainRequirement(domain=Domain.FIRE, minimum_value=2)
            ],
            backlash_potential=0.1,
            backlash_effects=[
                MagicalEffect(
                    effect_type=EffectType.DAMAGE,
                    description_template="The flames backfire, burning your hands",
                    magnitude=5,
                    target_type=TargetType.SELF,
                    damage_type=DamageType.FIRE
                )
            ],
            lore_notes="A common battle spell dating back to the Crimson Dissonance"
        )
        self.casting_service.register_spell(fireball)
        
        # Arcane Shield spell
        arcane_shield = Spell(
            id="spell_arcane_shield",
            name="Arcane Shield",
            description="Creates a shimmering barrier of magical energy that absorbs damage",
            tier=MagicTier.ARCANE_MASTERY,
            magic_source_affinity=[MagicSource.MANA_HEART],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="A glowing shield of arcane energy surrounds you",
                    magnitude="damage_reduction_5",
                    target_type=TargetType.SELF
                )
            ],
            mana_cost=8,
            casting_time_seconds=1,
            domain_requirements=[
                DomainRequirement(domain=Domain.MIND, minimum_value=3)
            ],
            backlash_potential=0.05,
            backlash_effects=[
                MagicalEffect(
                    effect_type=EffectType.DEBUFF_STAT,
                    description_template="The shield flickers and fades, leaving you vulnerable",
                    magnitude="vulnerable_1_turn",
                    target_type=TargetType.SELF
                )
            ],
            lore_notes="A defensive spell taught to all apprentice mages"
        )
        self.casting_service.register_spell(arcane_shield)
        
        # Tier 2: Mana Infusion spells
        
        # Flame Edge spell
        flame_edge = Spell(
            id="spell_flame_edge",
            name="Flame Edge",
            description="Infuses a weapon with fire energy for enhanced damage",
            tier=MagicTier.MANA_INFUSION,
            magic_source_affinity=[MagicSource.LEYLINE, MagicSource.MANA_HEART],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="Your weapon blazes with magical fire",
                    magnitude="weapon_damage_fire_3",
                    target_type=TargetType.ITEM
                )
            ],
            mana_cost=5,
            ley_energy_cost=3,
            casting_time_seconds=1,
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=2),
                DomainRequirement(domain=Domain.FIRE, minimum_value=1)
            ],
            backlash_potential=0.05,
            backlash_effects=[],
            lore_notes="A common enhancement technique used by battle-mages"
        )
        self.casting_service.register_spell(flame_edge)
        
        # Nature's Vigor spell
        natures_vigor = Spell(
            id="spell_natures_vigor",
            name="Nature's Vigor",
            description="Channels the vitality of nature to restore health",
            tier=MagicTier.MANA_INFUSION,
            magic_source_affinity=[MagicSource.LEYLINE, MagicSource.ENVIRONMENTAL],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.HEAL,
                    description_template="Healing energy flows through your body",
                    magnitude=10,
                    target_type=TargetType.SELF
                )
            ],
            ley_energy_cost=5,
            casting_time_seconds=2,
            domain_requirements=[
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=2),
                DomainRequirement(domain=Domain.EARTH, minimum_value=1)
            ],
            backlash_potential=0.05,
            backlash_effects=[],
            lore_notes="A healing technique practiced by druids and nature-attuned individuals"
        )
        self.casting_service.register_spell(natures_vigor)
        
        # Tier 3: Spiritual Utility spells
        
        # Spirit Sight spell
        spirit_sight = Spell(
            id="spell_spirit_sight",
            name="Spirit Sight",
            description="Opens the mind's eye to see spiritual energies and hidden truths",
            tier=MagicTier.SPIRITUAL_UTILITY,
            magic_source_affinity=[MagicSource.LEYLINE],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="Your vision shifts, revealing spiritual energies",
                    magnitude="detect_magic_and_spirits",
                    target_type=TargetType.SELF
                )
            ],
            ley_energy_cost=2,
            casting_time_seconds=1,
            domain_requirements=[
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=3),
                DomainRequirement(domain=Domain.AWARENESS, minimum_value=2)
            ],
            backlash_potential=0.02,
            backlash_effects=[],
            lore_notes="An ancient technique for communing with the spiritual world"
        )
        self.casting_service.register_spell(spirit_sight)
    
    def _register_basic_rituals(self):
        """Register basic rituals with the system"""
        # Mana Heart Development Ritual
        mana_heart_ritual = Ritual(
            id="ritual_mana_heart_development",
            name="Awakening of the Inner Flame",
            description="A ritual to develop or strengthen one's Mana Heart",
            tier=MagicTier.SPIRITUAL_UTILITY,
            magic_source_affinity=[MagicSource.LEYLINE, MagicSource.ENVIRONMENTAL],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="Energy coalesces within you, forming or strengthening your Mana Heart",
                    magnitude="develop_mana_heart",
                    target_type=TargetType.SELF
                )
            ],
            ley_energy_cost=10,
            casting_time_seconds=300,  # 5 minutes
            duration_minutes=60,
            domain_requirements=[
                DomainRequirement(domain=Domain.MIND, minimum_value=3),
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=3)
            ],
            participant_requirements=[
                ParticipantRequirement(
                    role="Guide",
                    minimum_count=1,
                    domain_requirements=[DomainRequirement(domain=Domain.SPIRIT, minimum_value=4)]
                )
            ],
            location_requirements=["LeylineNexus"],
            lore_notes="The first major milestone in a mage's journey, dating back to pre-Dissonance traditions"
        )
        self.ritual_service.register_ritual(mana_heart_ritual)
        
        # Purification Ritual
        purification_ritual = Ritual(
            id="ritual_purification",
            name="Cleansing Waters of Serenity",
            description="A ritual to cleanse magical corruption and negative energies",
            tier=MagicTier.SPIRITUAL_UTILITY,
            magic_source_affinity=[MagicSource.LEYLINE, MagicSource.ENVIRONMENTAL],
            effects=[
                MagicalEffect(
                    effect_type=EffectType.HEAL,
                    description_template="Purifying energies wash over you, cleansing corruption",
                    magnitude="reduce_corruption_10",
                    target_type=TargetType.SELF
                )
            ],
            ley_energy_cost=5,
            casting_time_seconds=180,  # 3 minutes
            duration_minutes=30,
            domain_requirements=[
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=3),
                DomainRequirement(domain=Domain.WATER, minimum_value=2)
            ],
            participant_requirements=[
                ParticipantRequirement(
                    role="Chanter",
                    minimum_count=2,
                    domain_requirements=[DomainRequirement(domain=Domain.SPIRIT, minimum_value=2)]
                )
            ],
            location_requirements=["PurifyingSpring", "SacredGrove"],
            lore_notes="Developed after the Crimson Dissonance to heal those afflicted by corrupted magic"
        )
        self.ritual_service.register_ritual(purification_ritual)
    
    def _register_basic_enchantments(self):
        """Register basic enchantments with the system"""
        # Flaming Weapon Enchantment
        flaming_weapon = Enchantment(
            id="enchant_flaming_weapon",
            name="Enchantment of Burning Wrath",
            description="Imbues a weapon with burning flames that ignite enemies",
            tier=MagicTier.MANA_INFUSION,
            applied_effects=[
                MagicalEffect(
                    effect_type=EffectType.DAMAGE,
                    description_template="Flames leap from the weapon, burning the target",
                    magnitude=3,
                    target_type=TargetType.SINGLE_ENEMY,
                    damage_type=DamageType.FIRE
                )
            ],
            passive_or_triggered="ON_HIT",
            recipe_id="recipe_flaming_weapon"
        )
        self.enchantment_service.register_enchantment(flaming_weapon)
        
        # Protective Ward Enchantment
        protective_ward = Enchantment(
            id="enchant_protective_ward",
            name="Enchantment of the Stalwart Guardian",
            description="Creates a magical barrier that occasionally absorbs damage",
            tier=MagicTier.MANA_INFUSION,
            applied_effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="A shimmering barrier appears, absorbing the blow",
                    magnitude="negate_damage_once",
                    target_type=TargetType.SELF
                )
            ],
            passive_or_triggered="ON_DAMAGED",
            recipe_id="recipe_protective_ward"
        )
        self.enchantment_service.register_enchantment(protective_ward)
    
    # ======================================================================
    # Public Interface Methods
    # ======================================================================
    
    def initialize_magic_user(self, domains: Dict[Domain, int]) -> MagicUser:
        """
        Initialize a new magic user based on their domains
        Returns a MagicUser object
        """
        # Determine initial mana heart status and capabilities based on domains
        has_mana_heart = False
        mana_max = 0
        mana_regen = 0.0
        ley_sensitivity = 0
        known_skills = []
        
        # Check if the character has sufficient MIND and SPIRIT for a Mana Heart
        mind_value = domains.get(Domain.MIND, 0)
        spirit_value = domains.get(Domain.SPIRIT, 0)
        
        if mind_value >= 5 and spirit_value >= 3:
            # Advanced practitioner with developed Mana Heart
            has_mana_heart = True
            mana_max = 30 + (mind_value * 5) + (spirit_value * 3)
            mana_regen = 0.5 + (mind_value * 0.1)
            known_skills.append("ManaHeartDeveloped")
        
        # Determine ley sensitivity based on SPIRIT domain
        ley_sensitivity = spirit_value
        
        # Add elemental affinities based on domain values
        attunements = []
        for domain, value in domains.items():
            if domain in [Domain.FIRE, Domain.WATER, Domain.EARTH, Domain.AIR, 
                          Domain.LIGHT, Domain.DARKNESS, Domain.SOUND, Domain.WIND, 
                          Domain.ICE] and value >= 2:
                attunements.append(f"{domain.name}Attuned")
        
        # Create the magic user profile
        magic_user = MagicUser(
            has_mana_heart=has_mana_heart,
            mana_current=mana_max,
            mana_max=mana_max,
            mana_regeneration_rate=mana_regen,
            ley_energy_sensitivity=ley_sensitivity,
            current_ley_energy=0,
            known_skills=known_skills,
            attunements=attunements
        )
        
        return magic_user
    
    def initialize_location_magic(self, location_description: str, historical_context: str = "") -> LocationMagicProfile:
        """
        Initialize the magical profile of a location based on its description
        Returns a LocationMagicProfile object
        """
        # Default values
        leyline_strength = 1
        mana_flux = ManaFluxLevel.MODERATE
        dominant_aspects = []
        decay_level = 0
        allows_rituals = False
        history = []
        
        # Analyze description for magical elements (simplified)
        lower_desc = location_description.lower()
        
        # Check for leyline indicators
        if any(word in lower_desc for word in ["leyline", "nexus", "confluence", "magical node"]):
            leyline_strength = 3
            if "powerful" in lower_desc or "strong" in lower_desc:
                leyline_strength = 4
            allows_rituals = True
        
        # Check for magical decay/corruption
        if any(word in lower_desc for word in ["corrupted", "blighted", "tainted", "withered"]):
            decay_level = 3
            mana_flux = ManaFluxLevel.CHAOTIC
        
        # Check for elemental aspects
        if any(word in lower_desc for word in ["fire", "flame", "burning", "volcanic"]):
            dominant_aspects.append(DamageType.FIRE)
        if any(word in lower_desc for word in ["water", "river", "lake", "ocean"]):
            dominant_aspects.append(DamageType.WATER)
        if any(word in lower_desc for word in ["earth", "stone", "mountain", "soil"]):
            dominant_aspects.append(DamageType.EARTH)
        if any(word in lower_desc for word in ["air", "wind", "sky", "breeze"]):
            dominant_aspects.append(DamageType.AIR)
        if any(word in lower_desc for word in ["light", "radiant", "bright", "sun"]):
            dominant_aspects.append(DamageType.LIGHT)
        if any(word in lower_desc for word in ["dark", "shadow", "night", "void"]):
            dominant_aspects.append(DamageType.DARKNESS)
        
        # Check for historical magical events
        if "crimson dissonance" in lower_desc or "war magic" in lower_desc:
            history.append("CrimsonDissonanceBattlefield")
        
        # Check if it's a ritual site
        if any(word in lower_desc for word in ["shrine", "altar", "temple", "sacred", "ritual"]):
            allows_rituals = True
        
        # Create the location magic profile
        location_magic = LocationMagicProfile(
            leyline_strength=leyline_strength,
            mana_flux_level=mana_flux,
            dominant_magic_aspects=dominant_aspects,
            environmental_decay_level=decay_level,
            allows_ritual_sites=allows_rituals,
            historical_magic_events=history
        )
        
        return location_magic
    
    def convert_spell_to_combat_move(self, spell_id: str) -> Optional[CombatMove]:
        """
        Convert a spell to a combat move for use in the combat system
        Returns a CombatMove object or None if the spell doesn't exist
        """
        spell = self.casting_service.get_spell(spell_id)
        if not spell:
            return None
        
        return spell.to_combat_move()
    
    def cast_combat_spell(self, 
                         caster: Combatant, 
                         caster_magic: MagicUser,
                         spell_id: str, 
                         target: Combatant,
                         location_magic: LocationMagicProfile) -> Dict[str, Any]:
        """
        Cast a spell in combat
        Returns a result dictionary
        """
        # Get the spell
        spell = self.casting_service.get_spell(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} does not exist",
                "combat_narration": f"{caster.name} attempts to cast a spell, but something goes wrong."
            }
        
        # Cast the spell
        result = self.casting_service.cast_spell(
            caster=caster,
            caster_magic_profile=caster_magic,
            spell_id=spell_id,
            targets=[target],
            location_magic_profile=location_magic
        )
        
        # Generate a combat narration
        if result["success"]:
            narration = f"{caster.name} casts {spell.name}. "
            
            # Add effect descriptions
            if result.get("effect_results") and result["effect_results"]:
                for target_result in result["effect_results"]:
                    for effect_result in target_result.get("results", []):
                        if "description" in effect_result:
                            narration += effect_result["description"] + " "
                        
                        if effect_result.get("effect_type") == "DAMAGE" and "actual_damage" in effect_result:
                            narration += f"{target_result['target_name']} takes {effect_result['actual_damage']} damage. "
                        
                        if effect_result.get("effect_type") == "HEAL" and "actual_healing" in effect_result:
                            narration += f"{target_result['target_name']} recovers {effect_result['actual_healing']} health. "
            
            # Add backlash description if any
            if result.get("backlash_occurred", False):
                narration += "The spell backfires! "
                for backlash_result in result.get("backlash_results", []):
                    if "description" in backlash_result:
                        narration += backlash_result["description"] + " "
        else:
            narration = f"{caster.name} attempts to cast {spell.name} but fails. {result.get('message', '')}"
        
        result["combat_narration"] = narration
        return result
    
    def develop_mana_heart(self, character_id: str, character_magic: MagicUser) -> Dict[str, Any]:
        """
        Develop or strengthen a character's Mana Heart
        Returns a result dictionary
        """
        # Check if the character already has a Mana Heart
        if character_magic.has_mana_heart:
            # Strengthen existing Mana Heart
            original_max = character_magic.mana_max
            character_magic.mana_max += 10
            character_magic.mana_regeneration_rate += 0.1
            
            # Refill mana
            mana_gained = character_magic.mana_max - character_magic.mana_current
            character_magic.mana_current = character_magic.mana_max
            
            return {
                "success": True,
                "had_mana_heart": True,
                "mana_max_increase": character_magic.mana_max - original_max,
                "mana_gained": mana_gained,
                "new_mana_max": character_magic.mana_max,
                "new_regen_rate": character_magic.mana_regeneration_rate,
                "message": "Your Mana Heart grows stronger, increasing your magical capacity.",
                "narrative": "You feel the magical core within you pulse and expand, its energy flowing more freely through your being."
            }
        else:
            # Develop new Mana Heart
            character_magic.has_mana_heart = True
            character_magic.mana_max = 20
            character_magic.mana_current = 20
            character_magic.mana_regeneration_rate = 0.2
            character_magic.known_skills.append("ManaHeartDeveloped")
            
            return {
                "success": True,
                "had_mana_heart": False,
                "new_mana_max": character_magic.mana_max,
                "new_regen_rate": character_magic.mana_regeneration_rate,
                "message": "You have developed a Mana Heart, unlocking new magical potential!",
                "narrative": "A profound shift occurs within you as magical energy coalesces into a glowing core. For the first time, you feel the steady pulse of your own Mana Heart, a wellspring of arcane power that connects you to the deeper mysteries of magic."
            }
    
    def get_available_spells(self, character_magic: MagicUser) -> Dict[MagicTier, List[Dict[str, Any]]]:
        """
        Get a list of spells available to the character based on their capabilities
        Returns a dictionary of spell lists organized by tier
        """
        available_spells = {
            MagicTier.ARCANE_MASTERY: [],
            MagicTier.MANA_INFUSION: [],
            MagicTier.SPIRITUAL_UTILITY: []
        }
        
        # Check all spells
        for spell_id, spell in self.casting_service.spells.items():
            # Check if the character knows this spell
            known = spell_id in character_magic.known_spells
            
            # Check if the character can theoretically cast this spell
            can_cast, reason = spell.can_be_cast_by(character_magic)
            
            # Add to the appropriate tier
            spell_info = {
                "id": spell_id,
                "name": spell.name,
                "description": spell.description,
                "known": known,
                "can_cast": can_cast,
                "reason": reason if not can_cast else "",
                "mana_cost": spell.mana_cost,
                "ley_energy_cost": spell.ley_energy_cost,
                "is_ritual": spell.is_ritual
            }
            
            available_spells[spell.tier].append(spell_info)
        
        return available_spells
    
    def learn_spell_from_study(self, character_id: str, spell_id: str, character_magic: MagicUser) -> Dict[str, Any]:
        """
        Learn a spell through study using enhanced roll system
        Returns a result dictionary
        """
        # Get the character object for enhanced rolls
        character = get_character(character_id)
        if not character:
            return {
                "success": False,
                "message": f"Character {character_id} not found"
            }
        
        # Get the spell
        spell = self.casting_service.get_spell(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} does not exist"
            }
        
        # Check if already known
        if spell_id in character_magic.known_spells:
            return {
                "success": False,
                "message": f"You already know the spell {spell.name}"
            }
        
        # Check tier requirements
        if spell.tier == MagicTier.ARCANE_MASTERY and not character_magic.has_mana_heart:
            return {
                "success": False,
                "message": f"You need a developed Mana Heart to learn Tier 1 Arcane Mastery spells"
            }
        
        # Determine learning difficulty based on spell tier and requirements
        base_difficulty = 10
        if spell.tier == MagicTier.ARCANE_MASTERY:
            base_difficulty = 15
        elif spell.tier == MagicTier.MANA_INFUSION:
            base_difficulty = 12
        
        # Add difficulty based on domain requirements
        required_domains = []
        for req in spell.domain_requirements:
            required_domains.append(req.domain)
            if req.minimum_value > 3:
                base_difficulty += 2
        
        # Choose primary domain for the learning check
        primary_domain = DomainType.MIND  # Default to Mind for spell learning
        if required_domains:
            # Use the highest required domain if available
            primary_domain = required_domains[0]
        
        # Create learning context
        context = {
            "action_type": "spell_learning",
            "spell_name": spell.name,
            "spell_tier": spell.tier.name,
            "study_environment": "focused",
            "magical_theory": True
        }
        
        # Use enhanced roll system for learning check
        learning_result = character.roll_check_hybrid(
            domain=primary_domain,
            tag_name="arcane_theory",  # Use arcane theory tag if available
            difficulty=base_difficulty,
            context=context
        )
        
        if learning_result["success"]:
            # Successfully learned the spell
            success, message = self.casting_service.learn_spell(character_id, spell_id, character_magic)
            
            if success:
                # Generate detailed narrative based on roll result
                narrative = f"After hours of study and practice, you finally grasp the essence of {spell.name}. "
                
                if learning_result.get("critical_success"):
                    narrative += "The magical formulae click into place with remarkable clarity, and you find yourself understanding not just the spell, but deeper principles of magic itself. "
                elif learning_result.get("margin", 0) > 5:
                    narrative += "The complex magical theory gradually becomes clear as you work through each component methodically. "
                else:
                    narrative += "Through persistent effort and careful study, the spell's secrets finally reveal themselves to you. "
                
                narrative += "The magical formulae and gestures become second nature to you."
                
                return {
                    "success": True,
                    "message": message,
                    "spell_name": spell.name,
                    "spell_tier": spell.tier.name,
                    "narrative": narrative,
                    "roll_result": learning_result,
                    "learning_time": "several hours" if learning_result.get("margin", 0) < 5 else "a few hours"
                }
            else:
                return {
                    "success": False,
                    "message": message
                }
        else:
            # Failed to learn the spell
            failure_narrative = f"Despite your best efforts to understand {spell.name}, the magical concepts remain elusive. "
            
            if learning_result.get("critical_failure"):
                failure_narrative += "Your misunderstanding of a key principle causes a minor magical mishap, leaving you mentally exhausted. "
                # Apply minor corruption or fatigue
                if character_magic.corruption_level < 100:
                    character_magic.corruption_level = min(100, character_magic.corruption_level + 1)
            elif learning_result.get("margin", 0) < -5:
                failure_narrative += "The advanced magical theory proves too complex for your current understanding. "
            else:
                failure_narrative += "You make some progress but cannot quite piece together the complete picture. "
            
            failure_narrative += "Perhaps with more experience or a different approach, you might succeed."
            
            return {
                "success": False,
                "message": learning_result.get("explanation", "Failed to learn the spell"),
                "narrative": failure_narrative,
                "roll_result": learning_result,
                "can_retry": True,
                "suggested_improvement": "Consider improving your Mind domain or finding a tutor"
            }
    
    def get_corruption_status(self, character_magic: MagicUser) -> Dict[str, Any]:
        """
        Get the current corruption status of a character
        Returns a dictionary with corruption details
        """
        effects = self.corruption_service.get_corruption_effects(character_magic)
        
        corruption_tier = "None"
        if character_magic.corruption_level >= 90:
            corruption_tier = "Complete"
        elif character_magic.corruption_level >= 70:
            corruption_tier = "Extreme"
        elif character_magic.corruption_level >= 50:
            corruption_tier = "Severe"
        elif character_magic.corruption_level >= 30:
            corruption_tier = "Moderate"
        elif character_magic.corruption_level >= 10:
            corruption_tier = "Minor"
        
        description = "You show no signs of magical corruption."
        if effects:
            descriptions = [effect["description"] for effect in effects]
            description = " ".join(descriptions)
        
        return {
            "corruption_level": character_magic.corruption_level,
            "corruption_tier": corruption_tier,
            "effects": effects,
            "description": description,
            "purification_recommended": character_magic.corruption_level >= 30
        }
    
    def create_magic_item(self, item_id: str, enchantment_id: str) -> ItemMagicProfile:
        """
        Create a magical item with an enchantment
        Returns an ItemMagicProfile object
        """
        # Get the enchantment
        enchantment = self.enchantment_service.get_enchantment(enchantment_id)
        
        # Create the item magic profile
        item_magic = ItemMagicProfile(
            is_enchanted=True,
            enchantment_id=enchantment_id if enchantment else None,
            charges=None  # Permanent enchantment
        )
        
        return item_magic

# ======================================================================
# Initialization
# ======================================================================

# Create an instance of the magic system
magic_system = MagicSystem()