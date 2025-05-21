"""
Enhanced environment effects for combat system.

This module provides more sophisticated environmental interactions and effects
that can dynamically alter combat conditions and create tactical opportunities.
"""
import random
from typing import Dict, List, Any, Optional

from .combat_system_core import Domain, Status, Combatant


class EnvironmentEffect:
    """Class representing an environmental effect that can be applied to combatants"""
    def __init__(self, 
                name: str, 
                description: str,
                apply_function: callable,
                tags: List[str] = None):
        """
        Initialize an environment effect.
        
        Args:
            name: Name of the effect
            description: Description of what the effect does
            apply_function: Function that applies the effect to combatants
            tags: Tags for categorizing the effect
        """
        self.name = name
        self.description = description
        self.apply_function = apply_function
        self.tags = tags or []
        
    def apply(self, combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
        """
        Apply this effect to all combatants.
        
        Args:
            combatants: Dictionary mapping combatant names to combatant objects
            
        Returns:
            Dictionary mapping combatant names to effect results
        """
        return self.apply_function(combatants)


def _apply_burning_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply burning environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Calculate damage based on resistances and vulnerabilities
        base_damage = 2  # Base burning damage
        damage_mod = 1.0
        
        # Resistance check
        if hasattr(combatant, 'strong_domains') and Domain.SPIRIT in combatant.strong_domains:
            damage_mod *= 0.5  # Half damage for fire resistance
            
        # Vulnerability check
        if hasattr(combatant, 'weak_domains') and Domain.BODY in combatant.weak_domains:
            damage_mod *= 1.5  # Extra damage for physical weakness
            
        # Status modification
        if Status.WOUNDED in combatant.statuses:
            damage_mod *= 1.2  # More damage if already wounded
            
        # Apply the damage
        final_damage = round(base_damage * damage_mod)
        original_health = combatant.current_health
        combatant.current_health = max(0, combatant.current_health - final_damage)
        actual_damage = original_health - combatant.current_health
        
        # Add status effect if not already present
        effect_applied = False
        if Status.WOUNDED not in combatant.statuses:
            combatant.statuses.add(Status.WOUNDED)
            effect_applied = True
            
        # Track effects
        round_effects[name] = {
            "environment": "burning",
            "damage": actual_damage,
            "status_applied": "WOUNDED" if effect_applied else None
        }
    
    return round_effects


def _apply_freezing_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply freezing environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Resistance and vulnerability check for freezing
        stamina_loss = 2  # Base stamina loss
        damage = 0
        
        if hasattr(combatant, 'weak_domains') and Domain.BODY in combatant.weak_domains:
            stamina_loss += 1  # Extra stamina loss
            damage = 1  # Also causes minor health damage
            
        if hasattr(combatant, 'strong_domains') and Domain.SPIRIT in combatant.strong_domains:
            stamina_loss = max(0, stamina_loss - 1)  # Reduced effect
            
        # Apply effects
        combatant.current_stamina = max(0, combatant.current_stamina - stamina_loss)
        
        if damage > 0:
            original_health = combatant.current_health
            combatant.current_health = max(0, combatant.current_health - damage)
            actual_damage = original_health - combatant.current_health
        else:
            actual_damage = 0
            
        # Add status effect if not already present
        effect_applied = False
        if Status.EXHAUSTED not in combatant.statuses:
            combatant.statuses.add(Status.EXHAUSTED)
            effect_applied = True
            
        # Track effects
        round_effects[name] = {
            "environment": "freezing",
            "damage": actual_damage,
            "stamina_loss": stamina_loss,
            "status_applied": "EXHAUSTED" if effect_applied else None
        }
    
    return round_effects


def _apply_electrified_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply electrified environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Calculate shock damage
        base_damage = 1  # Base shock damage
        damage_mod = 1.0
        
        # Resistances and vulnerabilities
        if hasattr(combatant, 'strong_domains') and Domain.MIND in combatant.strong_domains:
            damage_mod *= 0.3  # Significant resistance
            
        if hasattr(combatant, 'weak_domains') and Domain.MIND in combatant.weak_domains:
            damage_mod *= 1.8  # Significant vulnerability
            
        # Apply damage
        final_damage = round(base_damage * damage_mod)
        original_health = combatant.current_health
        combatant.current_health = max(0, combatant.current_health - final_damage)
        actual_damage = original_health - combatant.current_health
        
        # Random chance to apply stunned status (25% chance)
        effect_applied = False
        if random.random() < 0.25 and Status.STUNNED not in combatant.statuses:
            combatant.statuses.add(Status.STUNNED)
            effect_applied = True
            
        # Track effects
        round_effects[name] = {
            "environment": "electrified",
            "damage": actual_damage,
            "status_applied": "STUNNED" if effect_applied else None
        }
    
    return round_effects


def _apply_inspirational_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply inspirational environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Calculate spirit boost based on personality
        spirit_boost = 1  # Base spirit gain
        
        # Boost is higher for those with spirit domain
        if Domain.SPIRIT in combatant.domain_ratings and combatant.domain_ratings[Domain.SPIRIT] > 2:
            spirit_boost += 1
            
        # Apply the boost
        original_spirit = combatant.current_spirit
        combatant.current_spirit = min(combatant.max_spirit, combatant.current_spirit + spirit_boost)
        actual_boost = combatant.current_spirit - original_spirit
        
        # Chance to apply inspired status (50% chance)
        effect_applied = False
        if random.random() < 0.5 and Status.INSPIRED not in combatant.statuses:
            combatant.statuses.add(Status.INSPIRED)
            effect_applied = True
            
        # Track effects
        round_effects[name] = {
            "environment": "inspirational",
            "spirit_gain": actual_boost,
            "status_applied": "INSPIRED" if effect_applied else None
        }
    
    return round_effects


def _apply_toxic_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply toxic environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Calculate poison damage
        base_damage = 1  # Base poison damage
        damage_mod = 1.0
        
        # Resistances and vulnerabilities
        if hasattr(combatant, 'strong_domains') and Domain.BODY in combatant.strong_domains:
            damage_mod *= 0.5  # Resistance
            
        # Status effects
        if Status.WOUNDED in combatant.statuses:
            damage_mod *= 1.5  # More vulnerable when wounded
            
        # Apply damage
        final_damage = round(base_damage * damage_mod)
        original_health = combatant.current_health
        combatant.current_health = max(0, combatant.current_health - final_damage)
        actual_damage = original_health - combatant.current_health
        
        # Chance to apply poisoned status (75% chance)
        effect_applied = False
        if random.random() < 0.75 and Status.EXHAUSTED not in combatant.statuses:
            combatant.statuses.add(Status.EXHAUSTED)
            effect_applied = True
            
        # Track effects
        round_effects[name] = {
            "environment": "toxic",
            "damage": actual_damage,
            "status_applied": "EXHAUSTED" if effect_applied else None
        }
    
    return round_effects


def _apply_darkness_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply darkness environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Darkness primarily affects focus and awareness
        focus_loss = 1  # Base focus loss
        
        # Resistance based on awareness domain
        if Domain.AWARENESS in combatant.domain_ratings and combatant.domain_ratings[Domain.AWARENESS] > 2:
            focus_loss = 0  # No focus loss for those with high awareness
            
        # Apply the effects
        original_focus = combatant.current_focus
        combatant.current_focus = max(0, combatant.current_focus - focus_loss)
        actual_loss = original_focus - combatant.current_focus
        
        # Track effects
        round_effects[name] = {
            "environment": "darkness",
            "focus_loss": actual_loss,
            "status_applied": None
        }
    
    return round_effects


def _apply_unstable_ground_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply unstable ground environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Chance of falling based on awareness
        fall_chance = 0.2  # Base chance
        
        # Reduce chance based on awareness
        if Domain.AWARENESS in combatant.domain_ratings:
            fall_chance -= combatant.domain_ratings[Domain.AWARENESS] * 0.03
            fall_chance = max(0.05, fall_chance)  # Minimum 5% chance
            
        # Check if combatant falls
        if random.random() < fall_chance:
            # Apply damage and status
            damage = 1
            original_health = combatant.current_health
            combatant.current_health = max(0, combatant.current_health - damage)
            actual_damage = original_health - combatant.current_health
            
            # Apply stunned status
            effect_applied = False
            if Status.STUNNED not in combatant.statuses:
                combatant.statuses.add(Status.STUNNED)
                effect_applied = True
                
            round_effects[name] = {
                "environment": "unstable ground",
                "damage": actual_damage,
                "fell": True,
                "status_applied": "STUNNED" if effect_applied else None
            }
        else:
            round_effects[name] = {
                "environment": "unstable ground",
                "damage": 0,
                "fell": False,
                "status_applied": None
            }
    
    return round_effects


def _apply_confined_space_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply confined space environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    round_effects = {}
    
    for name, combatant in combatants.items():
        # Confined spaces mainly affect stamina usage
        stamina_loss = 1  # Base stamina loss
        
        # Body-focused characters are less affected
        if Domain.BODY in combatant.domain_ratings and combatant.domain_ratings[Domain.BODY] > 3:
            stamina_loss = 0
            
        # Apply the effects
        original_stamina = combatant.current_stamina
        combatant.current_stamina = max(0, combatant.current_stamina - stamina_loss)
        actual_loss = original_stamina - combatant.current_stamina
        
        # Track effects
        round_effects[name] = {
            "environment": "confined space",
            "stamina_loss": actual_loss,
            "status_applied": None
        }
    
    return round_effects


def _apply_high_ground_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply high ground environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    # High ground doesn't directly apply effects each round, but instead
    # provides tactical advantages during move resolution.
    # This function just returns a placeholder.
    round_effects = {}
    
    for name, combatant in combatants.items():
        round_effects[name] = {
            "environment": "high ground",
            "status_applied": None
        }
    
    return round_effects


# Create a dictionary of all environment effects
ENVIRONMENT_EFFECTS = {
    "burning": EnvironmentEffect(
        name="Burning",
        description="Fire engulfs the area, causing damage and potentially setting targets on fire.",
        apply_function=_apply_burning_environment,
        tags=["damage", "fire", "harmful"]
    ),
    "freezing": EnvironmentEffect(
        name="Freezing",
        description="Extreme cold saps stamina and can cause frostbite.",
        apply_function=_apply_freezing_environment,
        tags=["stamina", "cold", "harmful"]
    ),
    "electrified": EnvironmentEffect(
        name="Electrified",
        description="Electrical discharges can stun and cause damage.",
        apply_function=_apply_electrified_environment,
        tags=["damage", "stun", "harmful"]
    ),
    "inspirational": EnvironmentEffect(
        name="Inspirational",
        description="Something about this place inspires greatness, boosting spirit.",
        apply_function=_apply_inspirational_environment,
        tags=["spirit", "buff", "beneficial"]
    ),
    "toxic": EnvironmentEffect(
        name="Toxic",
        description="Poisonous fumes or substances cause gradual harm.",
        apply_function=_apply_toxic_environment,
        tags=["damage", "poison", "harmful"]
    ),
    "darkness": EnvironmentEffect(
        name="Darkness",
        description="Poor visibility makes it harder to focus and perceive threats.",
        apply_function=_apply_darkness_environment,
        tags=["debuff", "perception"]
    ),
    "unstable ground": EnvironmentEffect(
        name="Unstable Ground",
        description="The footing is treacherous, with risk of falling.",
        apply_function=_apply_unstable_ground_environment,
        tags=["movement", "harmful"]
    ),
    "confined space": EnvironmentEffect(
        name="Confined Space",
        description="Limited room to maneuver increases stamina usage.",
        apply_function=_apply_confined_space_environment,
        tags=["stamina", "movement"]
    ),
    "high ground": EnvironmentEffect(
        name="High Ground",
        description="Elevated position provides tactical advantages.",
        apply_function=_apply_high_ground_environment,
        tags=["advantage", "tactical", "beneficial"]
    )
}


def apply_environment_effects(
    active_tags: List[str],
    combatants: Dict[str, Combatant]
) -> Dict[str, Dict[str, Any]]:
    """
    Apply all active environment effects to combatants.
    
    Args:
        active_tags: List of active environment tags
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary with results of effect application
    """
    # Track all effects applied this round
    round_effects = {}
    
    # Apply each active effect
    for tag in active_tags:
        tag_lower = tag.lower()
        if tag_lower in ENVIRONMENT_EFFECTS:
            effect = ENVIRONMENT_EFFECTS[tag_lower]
            effect_results = effect.apply(combatants)
            
            # Merge results
            for name, result in effect_results.items():
                if name not in round_effects:
                    round_effects[name] = {}
                round_effects[name][tag_lower] = result
    
    return round_effects


def get_environment_description(active_tags: List[str]) -> str:
    """
    Generate a description of the environment based on active tags.
    
    Args:
        active_tags: List of active environment tags
        
    Returns:
        Description of the environment
    """
    descriptions = []
    
    for tag in active_tags:
        tag_lower = tag.lower()
        if tag_lower in ENVIRONMENT_EFFECTS:
            descriptions.append(ENVIRONMENT_EFFECTS[tag_lower].description)
    
    if not descriptions:
        return "The environment appears normal with no special effects."
    
    return " ".join(descriptions)