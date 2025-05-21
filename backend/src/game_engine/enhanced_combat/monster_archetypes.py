"""
Monster archetype system for the enhanced combat system.

This module defines the core classes and functions for creating
and managing monster archetypes, which serve as templates for
generating actual monster instances in the game.
"""
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum, auto
import copy
import random

from .combat_system_core import Combatant, CombatMove, Status, MoveType, Domain


class ThreatCategory(Enum):
    """Categories of monster threats"""
    BEAST = auto()         # Natural animals, even if unusual
    MAGICAL = auto()       # Inherently magical creatures
    HUMANOID = auto()      # Human-like threats
    UNDEAD = auto()        # Formerly living creatures
    CONSTRUCT = auto()     # Created or artificial beings
    ABERRATION = auto()    # Strange, otherworldly entities
    ELEMENTAL = auto()     # Pure elemental beings
    SPIRIT = auto()        # Non-corporeal entities


class ThreatTier(Enum):
    """Tiers of monster threats, determining overall power level"""
    MINION = auto()        # Weak, often appear in groups
    STANDARD = auto()      # Average threat, common encounters
    ELITE = auto()         # Stronger, mini-boss level
    BOSS = auto()          # Major encounter centerpiece
    LEGENDARY = auto()     # Unique, campaign-defining threat


class MoveBehavior:
    """Defines a monster's combat move behavior and conditions for use"""
    
    def __init__(self,
                 name: str,
                 description: str,
                 move_type: MoveType,
                 domains: List[Domain],
                 priority: int = 5,
                 conditions: Dict[str, Any] = None,
                 special_effects: List[str] = None):
        """
        Initialize a move behavior.
        
        Args:
            name: Name of the move
            description: Description of the move
            move_type: Type of combat move (FORCE, FOCUS, etc.)
            domains: List of domains this move uses
            priority: Priority of this move (0-10, higher means more likely to be used)
            conditions: Conditions under which this move should be used
            special_effects: Special effects this move can trigger
        """
        self.name = name
        self.description = description
        self.move_type = move_type
        self.domains = domains
        self.priority = priority
        self.conditions = conditions or {}
        self.special_effects = special_effects or []


class MonsterArchetype:
    """
    Template for creating monster instances.
    
    This class defines the base characteristics of a monster type,
    which can be used to generate actual combatant instances for
    encounters.
    """
    
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 category: ThreatCategory,
                 primary_domains: List[Domain],
                 weak_domains: List[Domain],
                 resistant_domains: List[Domain],
                 health_modifier: float = 1.0,
                 stamina_modifier: float = 1.0,
                 focus_modifier: float = 1.0,
                 spirit_modifier: float = 1.0,
                 move_behaviors: List[MoveBehavior] = None,
                 tier_adjustments: Dict[ThreatTier, Dict[str, Any]] = None,
                 status_resistances: List[Status] = None,
                 status_vulnerabilities: List[Status] = None):
        """
        Initialize a monster archetype.
        
        Args:
            id: Unique identifier for this archetype
            name: Display name for this monster type
            description: Flavor text and description
            category: Broad category of monster
            primary_domains: Domains this monster specializes in
            weak_domains: Domains this monster is weak against
            resistant_domains: Domains this monster resists
            health_modifier: Modifier for base health (default 1.0)
            stamina_modifier: Modifier for base stamina (default 1.0)
            focus_modifier: Modifier for base focus (default 1.0)
            spirit_modifier: Modifier for base spirit (default 1.0)
            move_behaviors: List of move behaviors this monster can use
            tier_adjustments: Stat adjustments for different threat tiers
            status_resistances: Statuses this monster resists
            status_vulnerabilities: Statuses this monster is vulnerable to
        """
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.primary_domains = primary_domains
        self.weak_domains = weak_domains
        self.resistant_domains = resistant_domains
        self.health_modifier = health_modifier
        self.stamina_modifier = stamina_modifier
        self.focus_modifier = focus_modifier
        self.spirit_modifier = spirit_modifier
        self.move_behaviors = move_behaviors or []
        
        # Default tier adjustments if none provided
        self.tier_adjustments = tier_adjustments or {
            ThreatTier.MINION: {
                "health_mult": 0.7,
                "damage_mult": 0.8,
                "domain_bonus": 0
            },
            ThreatTier.STANDARD: {
                "health_mult": 1.0,
                "damage_mult": 1.0,
                "domain_bonus": 1
            },
            ThreatTier.ELITE: {
                "health_mult": 1.5,
                "damage_mult": 1.2,
                "domain_bonus": 2
            },
            ThreatTier.BOSS: {
                "health_mult": 2.5,
                "damage_mult": 1.5,
                "domain_bonus": 3
            },
            ThreatTier.LEGENDARY: {
                "health_mult": 4.0,
                "damage_mult": 2.0,
                "domain_bonus": 4
            }
        }
        
        self.status_resistances = status_resistances or []
        self.status_vulnerabilities = status_vulnerabilities or []
    
    def get_domain_value(self, domain: Domain, tier: ThreatTier, level: int) -> int:
        """
        Calculate the value for a specific domain based on tier and level.
        
        Args:
            domain: The domain to calculate
            tier: Threat tier of the monster
            level: Level of the monster
            
        Returns:
            Domain value
        """
        base_value = 0
        tier_bonus = self.tier_adjustments[tier]["domain_bonus"]
        
        # Primary domains get higher values
        if domain in self.primary_domains:
            base_value = max(2, level // 2 + 1)
            if len(self.primary_domains) <= 3 and domain == self.primary_domains[0]:
                base_value += 1  # Extra bonus for the main domain
        # Weak domains get lower values
        elif domain in self.weak_domains:
            base_value = max(0, level // 3)
        # Other domains get average values
        else:
            base_value = max(1, level // 3)
        
        return base_value + tier_bonus
    
    def get_health(self, tier: ThreatTier, level: int) -> int:
        """
        Calculate the health for a monster instance.
        
        Args:
            tier: Threat tier of the monster
            level: Level of the monster
            
        Returns:
            Health value
        """
        base_health = 10 + (level * 5)
        tier_mult = self.tier_adjustments[tier]["health_mult"]
        return int(base_health * tier_mult * self.health_modifier)
    
    def get_resource_values(self, tier: ThreatTier, level: int) -> Tuple[int, int, int]:
        """
        Calculate resource values (stamina, focus, spirit) for a monster instance.
        
        Args:
            tier: Threat tier of the monster
            level: Level of the monster
            
        Returns:
            Tuple of (stamina, focus, spirit)
        """
        # Base values that scale with level
        base_stamina = 10 + (level * 2)
        base_focus = 10 + (level * 2)
        base_spirit = 10 + (level * 2)
        
        # Adjust based on primary domains
        for domain in self.primary_domains:
            if domain == Domain.BODY:
                base_stamina += level * 0.5
            elif domain == Domain.MIND:
                base_focus += level * 0.5
            elif domain == Domain.SPIRIT:
                base_spirit += level * 0.5
        
        # Apply tier and archetype modifiers
        tier_mult = self.tier_adjustments[tier]["health_mult"]  # Reuse health mult for simplicity
        stamina = int(base_stamina * tier_mult * self.stamina_modifier)
        focus = int(base_focus * tier_mult * self.focus_modifier)
        spirit = int(base_spirit * tier_mult * self.spirit_modifier)
        
        return stamina, focus, spirit
    
    def create_moves(self, tier: ThreatTier, level: int) -> List[CombatMove]:
        """
        Create combat moves for a monster instance.
        
        Args:
            tier: Threat tier of the monster
            level: Level of the monster
            
        Returns:
            List of combat moves
        """
        moves = []
        tier_damage_mult = self.tier_adjustments[tier]["damage_mult"]
        
        # Base damage scales with level and tier
        base_damage = 2 + level // 2
        damage_mult = tier_damage_mult
        
        # Create a move for each behavior
        for behavior in self.move_behaviors:
            damage = int(base_damage * damage_mult)
            
            # Adjust damage based on move type
            if behavior.move_type == MoveType.FORCE:
                damage = int(damage * 1.2)  # Force moves deal more damage
            elif behavior.move_type == MoveType.FOCUS:
                damage = int(damage * 0.8)  # Focus moves deal less direct damage
            
            # Primary domain moves deal more damage
            primary_domain_bonus = 1.0
            for domain in behavior.domains:
                if domain in self.primary_domains:
                    primary_domain_bonus = 1.3
                    break
            
            damage = int(damage * primary_domain_bonus)
            
            # Create the move
            move = CombatMove(
                name=behavior.name,
                description=behavior.description,
                move_type=behavior.move_type,
                domains=behavior.domains,
                base_damage=damage,
                stamina_cost=max(1, damage // 3) if behavior.move_type == MoveType.FORCE else 0,
                focus_cost=max(1, damage // 3) if behavior.move_type == MoveType.FOCUS else 0,
                spirit_cost=max(1, damage // 4) if behavior.move_type == MoveType.TRICK else 0,
                effects=behavior.special_effects
            )
            
            moves.append(move)
        
        # Ensure there's at least a basic attack if no moves are defined
        if not moves:
            default_move = CombatMove(
                name=f"{self.name} Attack",
                description=f"A basic attack from {self.name}",
                move_type=MoveType.FORCE,
                domains=[self.primary_domains[0]] if self.primary_domains else [Domain.BODY],
                base_damage=int(base_damage * damage_mult),
                stamina_cost=max(1, int(base_damage * damage_mult) // 3),
                focus_cost=0,
                spirit_cost=0,
                effects=[]
            )
            moves.append(default_move)
        
        return moves


def create_monster_from_archetype(
    archetype: MonsterArchetype,
    name: str = None,
    tier: ThreatTier = None,
    level: int = 1,
    variant_type: str = None
) -> Tuple[Combatant, List[CombatMove]]:
    """
    Create a monster combatant from an archetype.
    
    Args:
        archetype: Monster archetype to use as a template
        name: Optional custom name (defaults to archetype name)
        tier: Threat tier (defaults to archetype's default tier)
        level: Monster level (default 1)
        variant_type: Optional variant type (e.g., "Alpha", "Elder", etc.)
        
    Returns:
        Tuple containing (monster_combatant, available_moves)
    """
    # Default name to archetype name if not provided
    if not name:
        name = archetype.name
    
    # Add variant type to name if provided
    if variant_type:
        name = f"{variant_type} {name}"
    
    # Default to STANDARD tier if not specified
    if not tier:
        tier = ThreatTier.STANDARD
    
    # Create domain values dictionary
    domain_values = {}
    for domain in Domain:
        domain_values[domain] = archetype.get_domain_value(domain, tier, level)
    
    # Get resource values
    max_health = archetype.get_health(tier, level)
    stamina, focus, spirit = archetype.get_resource_values(tier, level)
    
    # Create the combatant
    monster = Combatant(
        name=name,
        domains=domain_values,
        max_health=max_health,
        current_health=max_health,
        max_stamina=stamina,
        current_stamina=stamina,
        max_focus=focus,
        current_focus=focus,
        max_spirit=spirit,
        current_spirit=spirit,
        statuses=set(),
        id=f"{archetype.id}_{random.randint(1000, 9999)}"
    )
    
    # Create combat moves
    moves = archetype.create_moves(tier, level)
    
    return monster, moves