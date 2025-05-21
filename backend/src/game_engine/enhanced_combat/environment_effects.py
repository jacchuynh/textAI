"""
Enhanced environment effects for combat system.

This module provides more sophisticated environmental interactions and effects
that can dynamically alter combat conditions and create tactical opportunities.
"""
from typing import Dict, List, Any, Callable, Optional, TypeGuard
import random

from .combat_system_core import Combatant, Domain, Status


class EnvironmentEffect:
    """Class representing an environmental effect that can be applied to combatants"""
    def __init__(self, 
                name: str, 
                description: str,
                apply_function: Callable,
                tags: Optional[List[str]] = None):
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
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to fire domain users
        if hasattr(combatant, 'domain_ratings') and Domain.FIRE.value in combatant.domain_ratings:
            fire_rating = combatant.domain_ratings[Domain.FIRE.value]
            if fire_rating > 3:  # High fire domain users benefit from burning
                result["effects"].append("Empowered by flames")
                result["description"] = f"{name} draws power from the burning surroundings."
            
        # Apply damage to combatants without fire protection
        if hasattr(combatant, 'statuses') and Status.BURNING not in combatant.statuses:
            # Check if already protected from fire
            fire_protected = False
            if hasattr(combatant, 'statuses'):
                fire_protected = Status.FIRE_RESISTANT in combatant.statuses
            
            if not fire_protected:
                damage = random.randint(1, 3)
                combatant.current_health = max(0, combatant.current_health - damage)
                result["damage"] = damage
                result["description"] = f"{name} takes {damage} damage from the burning environment."
                
                # Chance to apply burning status
                if random.random() < 0.3 and hasattr(combatant, 'statuses'):  # 30% chance
                    combatant.statuses.append(Status.BURNING)
                    result["effects"].append("Burning")
                    result["description"] += f" {name} is now burning!"
        
        results[name] = result
        
    return results


def _apply_freezing_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply freezing environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to ice domain users
        if hasattr(combatant, 'domain_ratings') and Domain.ICE.value in combatant.domain_ratings:
            ice_rating = combatant.domain_ratings[Domain.ICE.value]
            if ice_rating > 3:  # High ice domain users benefit from freezing
                result["effects"].append("Empowered by frost")
                result["description"] = f"{name} harnesses the freezing environment."
            
        # Apply effects to combatants without cold protection
        cold_protected = False
        if hasattr(combatant, 'statuses'):
            cold_protected = Status.COLD_RESISTANT in combatant.statuses
            
        if not cold_protected:
            # Reduce stamina
            if hasattr(combatant, 'current_stamina') and hasattr(combatant, 'max_stamina'):
                stamina_reduction = random.randint(1, 2)
                combatant.current_stamina = max(0, combatant.current_stamina - stamina_reduction)
                result["effects"].append(f"Stamina reduced by {stamina_reduction}")
                result["description"] = f"The freezing cold saps {name}'s stamina."
                
                # Chance to apply slowed status
                if random.random() < 0.3 and hasattr(combatant, 'statuses'):  # 30% chance
                    combatant.statuses.append(Status.SLOWED)
                    result["effects"].append("Slowed")
                    result["description"] += f" {name} is slowed by the cold!"
        
        results[name] = result
        
    return results


def _apply_electrified_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply electrified environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to spark domain users
        if hasattr(combatant, 'domain_ratings') and Domain.SPARK.value in combatant.domain_ratings:
            spark_rating = combatant.domain_ratings[Domain.SPARK.value]
            if spark_rating > 3:  # High spark domain users benefit
                result["effects"].append("Charged with energy")
                result["description"] = f"{name} channels the electrical energy of the surroundings."
                if hasattr(combatant, 'statuses') and Status.ENERGIZED not in combatant.statuses:
                    combatant.statuses.append(Status.ENERGIZED)
            
        # Apply effects to combatants without protection
        protected = False
        if hasattr(combatant, 'statuses'):
            protected = Status.SHOCK_RESISTANT in combatant.statuses
            
        if not protected:
            # Random chance for minor shock damage
            if random.random() < 0.4:  # 40% chance
                damage = random.randint(1, 4)
                combatant.current_health = max(0, combatant.current_health - damage)
                result["damage"] = damage
                result["description"] = f"{name} takes {damage} damage from electrical discharges."
                
                # Chance to apply stunned status
                if random.random() < 0.25 and hasattr(combatant, 'statuses'):  # 25% chance
                    combatant.statuses.append(Status.STUNNED)
                    result["effects"].append("Stunned")
                    result["description"] += f" {name} is momentarily stunned!"
        
        results[name] = result
        
    return results


def _apply_inspirational_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply inspirational environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Restore spirit
        if hasattr(combatant, 'current_spirit') and hasattr(combatant, 'max_spirit'):
            spirit_gain = random.randint(1, 3)
            combatant.current_spirit = min(combatant.max_spirit, combatant.current_spirit + spirit_gain)
            result["effects"].append(f"Spirit increased by {spirit_gain}")
            result["description"] = f"{name} is inspired by the surroundings, gaining {spirit_gain} spirit."
            
            # Chance to apply inspired status
            if random.random() < 0.3 and hasattr(combatant, 'statuses'):  # 30% chance
                combatant.statuses.append(Status.INSPIRED)
                result["effects"].append("Inspired")
                result["description"] += f" {name} feels inspired!"
        
        results[name] = result
        
    return results


def _apply_toxic_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply toxic environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to users with poison/toxin affinity
        poison_affinity = False
        if hasattr(combatant, 'domain_ratings') and Domain.NATURE.value in combatant.domain_ratings:
            nature_rating = combatant.domain_ratings[Domain.NATURE.value]
            if nature_rating > 4:  # High nature domain users can control toxins
                poison_affinity = True
                result["effects"].append("Toxin control")
                result["description"] = f"{name} manipulates the toxic elements in the environment."
            
        # Apply poison to combatants without protection
        protected = False
        if hasattr(combatant, 'statuses'):
            protected = Status.POISON_RESISTANT in combatant.statuses
            
        if not (protected or poison_affinity):
            # Apply poison damage
            damage = random.randint(1, 2)
            combatant.current_health = max(0, combatant.current_health - damage)
            result["damage"] = damage
            result["description"] = f"{name} takes {damage} damage from the toxic atmosphere."
            
            # Chance to apply poisoned status
            if random.random() < 0.35 and hasattr(combatant, 'statuses'):  # 35% chance
                combatant.statuses.append(Status.POISONED)
                result["effects"].append("Poisoned")
                result["description"] += f" {name} is poisoned!"
        
        results[name] = result
        
    return results


def _apply_darkness_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply darkness environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to stealth-oriented or shadow/darkness users
        shadow_affinity = False
        if hasattr(combatant, 'tags') and 'stealth' in combatant.tags:
            shadow_affinity = True
            result["effects"].append("Shadow advantage")
            result["description"] = f"{name} uses the darkness to their advantage."
            
        # Apply penalties to those without night vision or similar abilities
        night_vision = False
        if hasattr(combatant, 'statuses'):
            night_vision = Status.NIGHT_VISION in combatant.statuses
            
        if not (night_vision or shadow_affinity):
            # Apply accuracy penalty
            result["effects"].append("Visibility reduced")
            result["description"] = f"{name} struggles to see in the darkness."
            
            # Simulate missed attacks or reduced combat effectiveness
            if hasattr(combatant, 'status_modifiers'):
                if 'accuracy' not in combatant.status_modifiers:
                    combatant.status_modifiers['accuracy'] = 0
                combatant.status_modifiers['accuracy'] -= 2
                result["effects"].append("Accuracy -2")
        
        results[name] = result
        
    return results


def _apply_unstable_ground_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply unstable ground environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to agile combatants
        agile = False
        if hasattr(combatant, 'tags') and 'agile' in combatant.tags:
            agile = True
            result["effects"].append("Sure-footed")
            result["description"] = f"{name} maintains balance on the unstable ground."
            
        # Apply penalties to those without agility
        if not agile:
            # Chance to lose balance and fall
            if random.random() < 0.25 and hasattr(combatant, 'statuses'):  # 25% chance
                combatant.statuses.append(Status.PRONE)
                result["effects"].append("Knocked down")
                result["description"] = f"{name} loses footing and falls on the unstable ground!"
            else:
                result["effects"].append("Off-balance")
                result["description"] = f"{name} struggles to maintain balance."
                
                # Apply movement penalty
                if hasattr(combatant, 'status_modifiers'):
                    if 'movement' not in combatant.status_modifiers:
                        combatant.status_modifiers['movement'] = 0
                    combatant.status_modifiers['movement'] -= 1
                    result["effects"].append("Movement -1")
        
        results[name] = result
        
    return results


def _apply_confined_space_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply confined space environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        # Apply bonus to small or nimble combatants
        small_or_nimble = False
        if hasattr(combatant, 'tags') and ('small' in combatant.tags or 'nimble' in combatant.tags):
            small_or_nimble = True
            result["effects"].append("Spatial advantage")
            result["description"] = f"{name} maneuvers effectively in the confined space."
            
        # Apply penalties to large combatants
        large = False
        if hasattr(combatant, 'tags') and 'large' in combatant.tags:
            large = True
            
        if large:
            result["effects"].append("Constrained")
            result["description"] = f"{name} is constrained by the confined space."
            
            # Apply evasion penalty
            if hasattr(combatant, 'status_modifiers'):
                if 'evasion' not in combatant.status_modifiers:
                    combatant.status_modifiers['evasion'] = 0
                combatant.status_modifiers['evasion'] -= 2
                result["effects"].append("Evasion -2")
                
            # Apply force move bonus for all combatants (easier to hit in confined space)
            if hasattr(combatant, 'status_modifiers'):
                if 'force_move_power' not in combatant.status_modifiers:
                    combatant.status_modifiers['force_move_power'] = 0
                combatant.status_modifiers['force_move_power'] += 1
                result["effects"].append("Force moves +1")
        
        results[name] = result
        
    return results


def _apply_high_ground_environment(combatants: Dict[str, Combatant]) -> Dict[str, Dict[str, Any]]:
    """
    Apply high ground environment effects to combatants.
    
    Args:
        combatants: Dictionary mapping combatant names to combatant objects
        
    Returns:
        Dictionary mapping combatant names to effect results
    """
    results = {}
    
    # Determine who has high ground advantage
    has_high_ground = {}
    for name, combatant in combatants.items():
        # Random assignment for demo purposes - in real implementation this would be based on
        # tactical position or player choices
        has_high_ground[name] = random.choice([True, False])
    
    for name, combatant in combatants.items():
        result = {"damage": 0, "effects": [], "description": ""}
        
        if has_high_ground[name]:
            result["effects"].append("High ground advantage")
            result["description"] = f"{name} has the high ground advantage."
            
            # Apply accuracy bonus
            if hasattr(combatant, 'status_modifiers'):
                if 'accuracy' not in combatant.status_modifiers:
                    combatant.status_modifiers['accuracy'] = 0
                combatant.status_modifiers['accuracy'] += 2
                result["effects"].append("Accuracy +2")
                
            # Apply damage bonus
            if hasattr(combatant, 'status_modifiers'):
                if 'damage' not in combatant.status_modifiers:
                    combatant.status_modifiers['damage'] = 0
                combatant.status_modifiers['damage'] += 1
                result["effects"].append("Damage +1")
        else:
            result["effects"].append("Low ground disadvantage")
            result["description"] = f"{name} is at a disadvantage from lower ground."
            
            # Apply accuracy penalty
            if hasattr(combatant, 'status_modifiers'):
                if 'accuracy' not in combatant.status_modifiers:
                    combatant.status_modifiers['accuracy'] = 0
                combatant.status_modifiers['accuracy'] -= 1
                result["effects"].append("Accuracy -1")
        
        results[name] = result
        
    return results


# Dictionary mapping environment tags to effect functions
ENVIRONMENT_EFFECTS = {
    "burning": _apply_burning_environment,
    "freezing": _apply_freezing_environment,
    "electrified": _apply_electrified_environment, 
    "inspirational": _apply_inspirational_environment,
    "toxic": _apply_toxic_environment,
    "darkness": _apply_darkness_environment,
    "unstable": _apply_unstable_ground_environment,
    "confined": _apply_confined_space_environment,
    "highground": _apply_high_ground_environment
}


# Dictionary mapping environment tags to descriptions
ENVIRONMENT_DESCRIPTIONS = {
    "burning": "The area is engulfed in flames, with heat distorting the air.",
    "freezing": "A bitter cold permeates the area, with frost covering surfaces.",
    "electrified": "Electrical energy crackles through the environment, with occasional discharges.",
    "inspirational": "There's something magical about this place that fills one with hope and determination.",
    "toxic": "Noxious fumes fill the air, making it difficult to breathe without coughing.",
    "darkness": "Deep shadows blanket the area, making it difficult to see clearly.",
    "unstable": "The ground shifts and trembles underfoot, making it challenging to maintain balance.",
    "confined": "The walls press in from all sides, limiting movement and combat options.",
    "highground": "The terrain features elevation differences that provide tactical advantages.",
    "wet": "The ground is slick with water, affecting traction and movement.",
    "windy": "Strong winds howl through the area, affecting ranged attacks and movement.",
    "foggy": "A thick fog limits visibility to just a few feet ahead.",
    "sunny": "Bright sunlight bathes the area, potentially affecting vision for those not used to it.",
    "sacred": "The area has a spiritual significance that empowers certain abilities.",
    "corrupted": "Dark energies have twisted this place, enhancing sinister abilities.",
    "natural": "The untamed wilderness provides advantages to those attuned to nature.",
    "urban": "The constructed environment offers numerous hiding spots and tactical options.",
    "underwater": "Combat takes place submerged, dramatically changing movement and breathing."
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
    results = {}
    
    for tag in active_tags:
        if tag.lower() in ENVIRONMENT_EFFECTS:
            effect_function = ENVIRONMENT_EFFECTS[tag.lower()]
            tag_results = effect_function(combatants)
            
            # Merge results
            for name, result in tag_results.items():
                if name not in results:
                    results[name] = {"damage": 0, "effects": [], "descriptions": []}
                
                results[name]["damage"] += result["damage"]
                results[name]["effects"].extend(result["effects"])
                
                if result["description"]:
                    results[name]["descriptions"].append(result["description"])
    
    # Consolidate descriptions for each combatant
    for name, result in results.items():
        result["description"] = " ".join(result["descriptions"])
        del result["descriptions"]
    
    return results


def get_environment_description(active_tags: List[str]) -> str:
    """
    Generate a description of the environment based on active tags.
    
    Args:
        active_tags: List of active environment tags
        
    Returns:
        Description of the environment
    """
    if not active_tags:
        return "The environment appears normal with no special features."
    
    descriptions = []
    for tag in active_tags:
        if tag.lower() in ENVIRONMENT_DESCRIPTIONS:
            descriptions.append(ENVIRONMENT_DESCRIPTIONS[tag.lower()])
    
    if not descriptions:
        return "The environment has some unique aspects that might affect combat."
    
    return " ".join(descriptions)