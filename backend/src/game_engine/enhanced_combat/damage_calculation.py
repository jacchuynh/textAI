"""
Enhanced damage calculation for combat system.

This module provides more nuanced damage calculations that account for
momentum, status effects, environment, and other combat factors.
"""
from typing import Dict, List, Tuple, Any, Optional
import random

from .combat_system_core import Domain, Status, MoveType, Combatant, CombatMove


def calculate_damage(
    actor: Combatant,              # Acting combatant
    target: Combatant,             # Target combatant
    actor_move: CombatMove,        # CombatMove being used
    target_move: CombatMove,       # Target's response move
    actor_roll: int,               # Actor's roll result
    target_roll: int,              # Target's roll result
    actor_success: bool,           # Whether actor succeeded with their move
    effect_magnitude: int,         # Base magnitude of the effect
    type_advantage: int,           # Move type advantage factor
    actor_momentum: int,           # Actor's momentum
    target_momentum: int,          # Target's momentum
    environment_tags: List[str]    # Current environment tags
) -> Tuple[int, List[str]]:
    """
    Comprehensive damage calculation that accounts for all combat factors.
    
    Args:
        actor: Acting combatant
        target: Target combatant
        actor_move: CombatMove being used
        target_move: Target's response move
        actor_roll: Actor's roll result
        target_roll: Target's roll result
        actor_success: Whether actor succeeded with their move
        effect_magnitude: Base magnitude of the effect
        type_advantage: Move type advantage factor
        actor_momentum: Actor's momentum
        target_momentum: Target's momentum
        environment_tags: Current environment tags
        
    Returns:
        Tuple of (damage, special_effects)
    """
    # Base damage calculation
    if not actor_success:
        return 0, []  # No damage on failure
    
    # Start with base damage from effect magnitude
    base_damage = effect_magnitude
    
    # Apply move type modifiers
    move_type_modifier = 1.0
    if type_advantage > 0:
        move_type_modifier = 1.5  # 50% bonus for advantageous move type
    elif type_advantage < 0:
        move_type_modifier = 0.7  # 30% penalty for disadvantageous move type
    
    # Apply domain expertise modifiers
    domain_modifier = 1.0
    for domain in actor_move.domains:
        # Increase damage based on actor's skill in the domain
        domain_rating = actor.domain_ratings.get(domain, 1)
        domain_modifier += (domain_rating - 1) * 0.1  # +10% per point above 1
        
        # Check if targeting a weakness
        if hasattr(target, 'weak_domains') and domain in target.weak_domains:
            domain_modifier += 0.3  # +30% damage when targeting weakness
    
    # Apply momentum modifiers
    momentum_modifier = 1.0
    momentum_diff = actor_momentum - target_momentum
    if momentum_diff > 0:
        momentum_modifier += min(momentum_diff * 0.2, 0.6)  # Up to +60% for momentum
    
    # Apply status effect modifiers
    status_modifier = 1.0
    special_effects = []
    
    # Actor status effects that boost damage
    if Status.INSPIRED in actor.statuses:
        status_modifier += 0.15  # +15% damage
    
    # Target status effects that increase damage taken
    if Status.WOUNDED in target.statuses:
        status_modifier += 0.2  # +20% damage
    if Status.STUNNED in target.statuses:
        status_modifier += 0.1  # +10% damage
    
    # Target status effects that reduce damage taken
    if Status.FRIGHTENED in actor.statuses:
        status_modifier -= 0.1  # -10% damage
    
    # Environmental modifiers
    environment_modifier = 1.0
    for tag in environment_tags:
        # Domain-specific environment bonuses
        if tag.lower() == "water" and Domain.BODY in actor_move.domains:
            environment_modifier += 0.1  # +10% for body moves in water
        elif tag.lower() == "darkness" and Domain.AWARENESS in actor_move.domains:
            environment_modifier += 0.2  # +20% for awareness moves in darkness
        
        # Move type environmental bonuses
        if tag.lower() == "unstable ground" and actor_move.move_type == MoveType.TRICK:
            environment_modifier += 0.15  # +15% for trick moves on unstable ground
        elif tag.lower() == "confined space" and actor_move.move_type == MoveType.FORCE:
            environment_modifier += 0.1  # +10% for force moves in confined spaces
    
    # Special modifiers for calculated and desperate moves
    special_modifier = 1.0
    if actor_move.is_calculated:
        # Calculated moves do less damage but are more reliable
        special_modifier = 0.8
    elif actor_move.is_desperate:
        # Desperate moves do more damage but are risky
        special_modifier = 1.5
    
    # Critical hit chance based on the difference between rolls
    roll_diff = actor_roll - target_roll
    critical_hit = False
    if roll_diff >= 8:  # Significant success
        critical_hit = True
        special_effects.append("CRITICAL")
    
    # Calculate final damage
    final_damage = (base_damage * move_type_modifier * domain_modifier * 
                   momentum_modifier * status_modifier * environment_modifier * 
                   special_modifier)
    
    # Apply critical hit multiplier
    if critical_hit:
        final_damage *= 1.5  # 50% bonus damage on critical hit
    
    # Round to integer
    final_damage = round(final_damage)
    
    # Ensure minimum damage of 1 for successful hits
    if actor_success and final_damage < 1:
        final_damage = 1
    
    return final_damage, special_effects


def apply_damage_and_effects(
    actor: Combatant,             # Acting combatant
    target: Combatant,            # Target combatant
    damage: int,                  # Calculated damage value
    special_effects: List[str],   # List of special effects to apply
    actor_move: CombatMove,       # Move that was used
    combat_system: Any            # Reference to combat system for status updates
) -> Dict[str, Any]:
    """
    Apply the calculated damage and any special effects to the target.
    
    Args:
        actor: Acting combatant
        target: Target combatant
        damage: Calculated damage value
        special_effects: List of special effects to apply
        actor_move: Move that was used
        combat_system: Reference to combat system for status updates
        
    Returns:
        Dictionary with results of damage application
    """
    # Apply base damage to health
    original_health = target.current_health
    target.current_health = max(0, target.current_health - damage)
    health_damage = original_health - target.current_health
    
    # Track additional effects
    applied_effects = []
    removed_effects = []
    
    # Handle special effects
    for effect in special_effects:
        if effect == "CRITICAL":
            applied_effects.append("Critical hit")
            # Add wounded status on critical hit if not already present
            if Status.WOUNDED not in target.statuses:
                target.statuses.add(Status.WOUNDED)
                applied_effects.append("Target wounded")
    
    # Apply move-specific status effects based on move type and domains
    if actor_move.move_type == MoveType.FORCE and damage >= 5:
        # Strong force moves can stun
        if Status.STUNNED not in target.statuses:
            target.statuses.add(Status.STUNNED)
            applied_effects.append("Target stunned")
    
    elif actor_move.move_type == MoveType.TRICK and actor_move.is_calculated:
        # Calculated trick moves can confuse
        if Status.CONFUSED not in target.statuses:
            target.statuses.add(Status.CONFUSED)
            applied_effects.append("Target confused")
    
    # Domain-specific effects
    for domain in actor_move.domains:
        if domain == Domain.SPIRIT and damage >= 3:
            # Spirit moves can cause frightened
            if Status.FRIGHTENED not in target.statuses:
                target.statuses.add(Status.FRIGHTENED)
                applied_effects.append("Target frightened")
        
        elif domain == Domain.AUTHORITY and damage >= 3:
            # Authority moves can intimidate
            if Status.FRIGHTENED not in target.statuses:
                target.statuses.add(Status.FRIGHTENED)
                applied_effects.append("Target intimidated")
    
    # Check for knockdown on high damage
    if damage >= 7 and not hasattr(target, 'statuses_immune') and not getattr(target, 'statuses_immune', False):
        # A knockdown effect could be represented as stunned in our system
        if Status.STUNNED not in target.statuses:
            target.statuses.add(Status.STUNNED)
            applied_effects.append("Target knocked down")
    
    # Check for defeat
    defeated = target.current_health <= 0
    
    # Update momentum if the combat system supports it
    if hasattr(combat_system, 'momentum') and damage > 0:
        combat_system.momentum[actor.id] = min(3, combat_system.momentum.get(actor.id, 0) + 1)
        combat_system.momentum[target.id] = max(0, combat_system.momentum.get(target.id, 0) - 1)
    
    return {
        "damage_dealt": health_damage,
        "applied_effects": applied_effects,
        "removed_effects": removed_effects,
        "target_defeated": defeated,
        "remaining_health": target.current_health,
        "remaining_health_percent": (target.current_health / target.max_health) * 100 if target.max_health > 0 else 0
    }