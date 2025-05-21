"""
Core combat system implementation with domain-based mechanics.

This module defines the fundamental classes and functions for the
combat system, including combatants, moves, statuses, and basic
combat resolution.
"""
from typing import Dict, List, Set, Any, Optional
from enum import Enum, auto
import random


class Domain(Enum):
    """Core domains that define character abilities and actions"""
    BODY = auto()         # Physical strength, endurance, athleticism
    MIND = auto()         # Intelligence, memory, logical reasoning
    CRAFT = auto()        # Making, fixing, technical skills
    AWARENESS = auto()    # Perception, intuition, reflexes
    SOCIAL = auto()       # Charisma, persuasion, intimidation
    AUTHORITY = auto()    # Leadership, command, willpower
    SPIRIT = auto()       # Connection to magic, emotion, faith
    
    # Extended domains for elemental and special effects
    FIRE = auto()         # Fire, heat, combustion
    WATER = auto()        # Water, ice, liquid
    EARTH = auto()        # Earth, stone, crystal
    AIR = auto()          # Air, wind, gas
    LIGHT = auto()        # Light, radiance, purity
    DARKNESS = auto()     # Shadow, void, corruption
    SOUND = auto()        # Sound, noise, music
    WIND = auto()         # Wind, storms
    ICE = auto()          # Ice, frost, cold
    
    @classmethod
    def get_by_name(cls, name: str) -> 'Domain':
        """Get a domain by its name"""
        try:
            return cls[name.upper()]
        except KeyError:
            return cls.BODY  # Default to BODY if not found


class DomainType(Enum):
    """Types of domains for categorization"""
    PHYSICAL = auto()     # Body-related domains
    MENTAL = auto()       # Mind-related domains
    SOCIAL = auto()       # Social interaction domains
    ELEMENTAL = auto()    # Natural forces
    MYSTICAL = auto()     # Magical and spiritual
    
    @classmethod
    def get_type(cls, domain: Domain) -> 'DomainType':
        """Get the type of a domain"""
        physical = [Domain.BODY]
        mental = [Domain.MIND, Domain.AWARENESS, Domain.CRAFT]
        social = [Domain.SOCIAL, Domain.AUTHORITY]
        elemental = [Domain.FIRE, Domain.WATER, Domain.EARTH, Domain.AIR, 
                    Domain.LIGHT, Domain.DARKNESS, Domain.SOUND, Domain.WIND, Domain.ICE]
        mystical = [Domain.SPIRIT]
        
        if domain in physical:
            return cls.PHYSICAL
        elif domain in mental:
            return cls.MENTAL
        elif domain in social:
            return cls.SOCIAL
        elif domain in elemental:
            return cls.ELEMENTAL
        elif domain in mystical:
            return cls.MYSTICAL
        else:
            return cls.PHYSICAL  # Default


class MoveType(Enum):
    """Types of combat moves that can be performed"""
    FORCE = auto()     # Direct, aggressive actions
    FOCUS = auto()     # Precision, targeted actions
    TRICK = auto()     # Deception, misdirection
    DEFEND = auto()    # Protection, evasion, blocking
    UTILITY = auto()   # Support, buffs, healing


class Status(Enum):
    """Status effects that can be applied to combatants"""
    # Positive statuses
    ENERGIZED = auto()   # Increased damage
    FOCUSED = auto()     # Increased accuracy
    FORTIFIED = auto()   # Reduced damage taken
    PROTECTED = auto()   # Chance to negate attacks
    INSPIRED = auto()    # All stats increased
    QUICKENED = auto()   # Increased speed/priority
    REGENERATING = auto() # Recover health over time
    
    # Negative statuses
    VULNERABLE = auto()  # Increased damage taken
    WEAKENED = auto()    # Decreased damage dealt
    CONFUSED = auto()    # May target self or allies
    STUNNED = auto()     # Skip turns or actions
    BLEEDING = auto()    # Lose health over time
    BURNING = auto()     # Take fire damage over time
    POISONED = auto()    # Take poison damage over time
    FROZEN = auto()      # Reduced actions, cold damage
    BLINDED = auto()     # Reduced accuracy
    EXHAUSTED = auto()   # Reduced resource recovery
    PRONE = auto()       # Vulnerable to melee attacks
    
    # Neutral statuses
    CHARGING = auto()    # Preparing a powerful attack
    CONCEALED = auto()   # Hidden, harder to target


class CombatMove:
    """Defines a combat action that can be taken by a combatant"""
    
    def __init__(self,
                 name: str,
                 description: str,
                 move_type: MoveType,
                 domains: List[Domain],
                 base_damage: int = 0,
                 stamina_cost: int = 0,
                 focus_cost: int = 0,
                 spirit_cost: int = 0,
                 effects: List[str] = None,
                 tags: Dict[str, int] = None):
        """
        Initialize a combat move.
        
        Args:
            name: Name of the move
            description: Description of the move
            move_type: Type of combat move
            domains: List of domains this move uses
            base_damage: Base damage of the move
            stamina_cost: Stamina cost to use the move
            focus_cost: Focus cost to use the move
            spirit_cost: Spirit cost to use the move
            effects: Special effects this move can trigger
            tags: Tags that apply to this move with their ranks
        """
        self.name = name
        self.description = description
        self.move_type = move_type
        self.domains = domains
        self.base_damage = base_damage
        self.stamina_cost = stamina_cost
        self.focus_cost = focus_cost
        self.spirit_cost = spirit_cost
        self.effects = effects or []
        self.tags = tags or {}
    
    def can_be_used(self, combatant) -> bool:
        """Check if the combatant has enough resources to use this move"""
        return (combatant.current_stamina >= self.stamina_cost and
                combatant.current_focus >= self.focus_cost and
                combatant.current_spirit >= self.spirit_cost)
    
    def use(self, combatant) -> None:
        """Apply the resource costs of using this move"""
        if not self.can_be_used(combatant):
            return False
        
        combatant.current_stamina -= self.stamina_cost
        combatant.current_focus -= self.focus_cost
        combatant.current_spirit -= self.spirit_cost
        return True


class Combatant:
    """Represents a participant in combat"""
    
    def __init__(self,
                 name: str,
                 domains: Dict[Domain, int],
                 max_health: int,
                 current_health: int,
                 max_stamina: int,
                 current_stamina: int,
                 max_focus: int,
                 current_focus: int,
                 max_spirit: int,
                 current_spirit: int,
                 statuses: Set[Status] = None,
                 tags: Dict[str, int] = None,
                 id: str = None):
        """
        Initialize a combatant.
        
        Args:
            name: Name of the combatant
            domains: Dictionary mapping domains to their values
            max_health: Maximum health
            current_health: Current health
            max_stamina: Maximum stamina
            current_stamina: Current stamina
            max_focus: Maximum focus
            current_focus: Current focus
            max_spirit: Maximum spirit
            current_spirit: Current spirit
            statuses: Set of current status effects
            tags: Dictionary mapping tags to their ranks
            id: Unique identifier
        """
        self.name = name
        self.domains = domains
        self.max_health = max_health
        self.current_health = current_health
        self.max_stamina = max_stamina
        self.current_stamina = current_stamina
        self.max_focus = max_focus
        self.current_focus = current_focus
        self.max_spirit = max_spirit
        self.current_spirit = current_spirit
        self.statuses = statuses or set()
        self.tags = tags or {}
        self.id = id or name.lower().replace(' ', '_')
        
        # Additional properties for AI and game mechanics
        self.status_modifiers = {}
        self.enhanced_statuses = []
        
    def get_domain_value(self, domain: Domain) -> int:
        """Get the value of a specific domain"""
        return self.domains.get(domain, 0)
    
    def has_status(self, status: Status) -> bool:
        """Check if the combatant has a specific status"""
        return status in self.statuses
    
    def add_status(self, status: Status) -> None:
        """Add a status effect to the combatant"""
        self.statuses.add(status)
    
    def remove_status(self, status: Status) -> None:
        """Remove a status effect from the combatant"""
        if status in self.statuses:
            self.statuses.remove(status)
    
    def take_damage(self, amount: int) -> int:
        """
        Apply damage to the combatant.
        
        Args:
            amount: Amount of damage to take
            
        Returns:
            Actual damage taken
        """
        actual_amount = max(0, amount)
        self.current_health = max(0, self.current_health - actual_amount)
        return actual_amount
    
    def heal(self, amount: int) -> int:
        """
        Heal the combatant.
        
        Args:
            amount: Amount of healing to apply
            
        Returns:
            Actual healing received
        """
        before = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - before
    
    def is_defeated(self) -> bool:
        """Check if the combatant is defeated"""
        return self.current_health <= 0
    
    def recover_resources(self, stamina: int = 0, focus: int = 0, spirit: int = 0) -> None:
        """Recover resources"""
        self.current_stamina = min(self.max_stamina, self.current_stamina + stamina)
        self.current_focus = min(self.max_focus, self.current_focus + focus)
        self.current_spirit = min(self.max_spirit, self.current_spirit + spirit)
    
    def get_tag_value(self, tag: str) -> int:
        """Get the value of a specific tag"""
        return self.tags.get(tag, 0)
    
    def has_tag(self, tag: str) -> bool:
        """Check if the combatant has a specific tag"""
        return tag in self.tags
    
    def add_tag(self, tag: str, rank: int = 1) -> None:
        """Add a tag to the combatant or increase its rank"""
        if tag in self.tags:
            self.tags[tag] = max(self.tags[tag], rank)
        else:
            self.tags[tag] = rank