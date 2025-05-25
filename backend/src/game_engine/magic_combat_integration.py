"""
Magic Combat Integration Module

This module integrates the magic system with the combat system,
allowing for spell casting and magical effects during combat.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import random
import math
from enum import Enum, auto

# Import the core magic system
from game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, MagicEffect, Domain, 
    DamageType, EffectType, MagicTier, LocationMagicProfile
)


class CombatantType(Enum):
    """Types of combatants in the combat system."""
    PLAYER = auto()
    NPC = auto()
    MONSTER = auto()
    SUMMON = auto()


class MoveType(Enum):
    """Types of combat moves that can be performed."""
    MELEE = auto()
    RANGED = auto()
    SPELL = auto()
    ABILITY = auto()
    ITEM = auto()


class Combatant:
    """
    Represents an entity participating in combat.
    Can be a player, NPC, monster, or summon.
    """
    def __init__(
        self,
        id: str,
        name: str,
        combatant_type: CombatantType,
        level: int,
        max_health: int,
        current_health: int,
        stats: Dict[str, int],
        resistances: Dict[DamageType, float] = None,
        weaknesses: Dict[DamageType, float] = None,
        immunities: Set[DamageType] = None,
        magic_profile: Optional[MagicUser] = None
    ):
        self.id = id
        self.name = name
        self.combatant_type = combatant_type
        self.level = level
        self.max_health = max_health
        self.current_health = current_health
        self.stats = stats
        self.resistances = resistances or {}
        self.weaknesses = weaknesses or {}
        self.immunities = immunities or set()
        self.magic_profile = magic_profile
        self.active_effects = []
        self.is_alive = True
        self.position = (0, 0)  # x, y coordinates in the combat area
        self.initiative = 0
        self.action_points = 2
        self.movement_points = 1
    
    def take_damage(self, amount: int, damage_type: DamageType = None) -> Dict[str, Any]:
        """
        Apply damage to the combatant, accounting for resistances and weaknesses.
        Returns a dict with the result of the damage application.
        """
        if not self.is_alive:
            return {"success": False, "message": f"{self.name} is already defeated"}
        
        # Apply resistances and weaknesses if a damage type is specified
        modified_amount = amount
        resistance_applied = False
        weakness_applied = False
        
        if damage_type:
            # Check immunities
            if damage_type in self.immunities:
                return {
                    "success": True,
                    "original_damage": amount,
                    "final_damage": 0,
                    "immune": True,
                    "message": f"{self.name} is immune to {damage_type.name} damage"
                }
            
            # Apply resistance
            if damage_type in self.resistances:
                resistance_factor = self.resistances[damage_type]
                modified_amount = int(amount * (1 - resistance_factor))
                resistance_applied = True
            
            # Apply weakness
            if damage_type in self.weaknesses:
                weakness_factor = self.weaknesses[damage_type]
                modified_amount = int(amount * (1 + weakness_factor))
                weakness_applied = True
        
        # Apply damage
        self.current_health = max(0, self.current_health - modified_amount)
        
        # Check if defeated
        was_defeated = False
        if self.current_health == 0:
            self.is_alive = False
            was_defeated = True
        
        # Return result
        return {
            "success": True,
            "original_damage": amount,
            "final_damage": modified_amount,
            "resistance_applied": resistance_applied,
            "weakness_applied": weakness_applied,
            "current_health": self.current_health,
            "was_defeated": was_defeated,
            "message": f"{self.name} took {modified_amount} damage" + (" and was defeated!" if was_defeated else "")
        }
    
    def heal(self, amount: int) -> Dict[str, Any]:
        """
        Heal the combatant for a specified amount.
        Returns a dict with the result of the healing.
        """
        if not self.is_alive:
            return {"success": False, "message": f"{self.name} is defeated and cannot be healed"}
        
        # Calculate actual healing (cannot exceed max health)
        old_health = self.current_health
        self.current_health = min(self.current_health + amount, self.max_health)
        actual_healing = self.current_health - old_health
        
        # Return result
        return {
            "success": True,
            "healing_amount": amount,
            "actual_healing": actual_healing,
            "current_health": self.current_health,
            "message": f"{self.name} healed for {actual_healing} health points"
        }
    
    def reset_combat_state(self) -> None:
        """Reset the combatant's state for a new combat."""
        self.active_effects = []
        self.initiative = 0
        self.action_points = 2
        self.movement_points = 1
        
        # Reset mana if the combatant has a magic profile
        if self.magic_profile:
            # Restore 50% of max mana at the start of combat
            self.magic_profile.mana_current = max(
                self.magic_profile.mana_current,
                int(self.magic_profile.mana_max * 0.5)
            )
    
    def can_cast_spell(self, spell_id: str) -> bool:
        """Check if the combatant can cast a specific spell."""
        if not self.magic_profile:
            return False
        
        if not self.is_alive:
            return False
        
        if self.action_points < 1:
            return False
        
        if spell_id not in self.magic_profile.known_spells:
            return False
        
        return True
    
    def get_magical_combat_stats(self) -> Dict[str, Any]:
        """Get the combatant's magical combat statistics."""
        if not self.magic_profile:
            return {
                "has_magic": False,
                "magic_level": 0,
                "known_spells": 0,
                "mana": 0,
                "max_mana": 0
            }
        
        return {
            "has_magic": True,
            "magic_level": self.magic_profile.level,
            "known_spells": len(self.magic_profile.known_spells),
            "mana": self.magic_profile.mana_current,
            "max_mana": self.magic_profile.mana_max,
            "primary_domains": [d.name for d in self.magic_profile.primary_domains],
            "secondary_domains": [d.name for d in self.magic_profile.secondary_domains]
        }


class CombatMove:
    """
    Represents a move that can be performed in combat.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        move_type: MoveType,
        action_cost: int = 1,
        range_min: float = 0.0,
        range_max: float = 1.5,
        area_of_effect: float = 0.0,
        cooldown: int = 0,
        damage: int = 0,
        damage_type: Optional[DamageType] = None,
        effects: List[Dict[str, Any]] = None,
        targeting_type: str = "single",  # "single", "area", "self", "all"
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.move_type = move_type
        self.action_cost = action_cost
        self.range_min = range_min
        self.range_max = range_max
        self.area_of_effect = area_of_effect
        self.cooldown = cooldown
        self.damage = damage
        self.damage_type = damage_type
        self.effects = effects or []
        self.targeting_type = targeting_type
        self.tags = tags or []
        self.current_cooldown = 0
    
    def is_available(self) -> bool:
        """Check if the move is available (not on cooldown)."""
        return self.current_cooldown == 0
    
    def reset_cooldown(self) -> None:
        """Reset the move's cooldown to its maximum value."""
        self.current_cooldown = self.cooldown
    
    def reduce_cooldown(self) -> None:
        """Reduce the move's cooldown by 1."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def is_in_range(self, source_pos: Tuple[float, float], target_pos: Tuple[float, float]) -> bool:
        """Check if the target is within range of the move."""
        distance = math.sqrt(
            (target_pos[0] - source_pos[0]) ** 2 + 
            (target_pos[1] - source_pos[1]) ** 2
        )
        return self.range_min <= distance <= self.range_max


class MonsterMagicIntegration:
    """
    Handles the integration of magic into monster combatants.
    """
    def __init__(self, magic_system: MagicSystem):
        self.magic_system = magic_system
    
    def enhance_monster_with_magic(self, monster: Combatant, power_level: float = 1.0) -> Combatant:
        """
        Enhance a monster with magical abilities based on its type and level.
        Returns the enhanced monster.
        """
        if monster.magic_profile:
            # Monster already has magic, just return it
            return monster
        
        # Create a new magic profile for the monster
        monster_domains = self._determine_monster_domains(monster)
        
        magic_user = MagicUser(
            id=f"magic_{monster.id}",
            name=f"{monster.name}'s Magic",
            level=monster.level,
            mana_max=self._calculate_monster_mana(monster, power_level),
            mana_current=self._calculate_monster_mana(monster, power_level),
            primary_domains=monster_domains[:1],  # First domain is primary
            secondary_domains=monster_domains[1:],  # Rest are secondary
            known_spells=set()
        )
        
        # Assign the magic profile to the monster
        monster.magic_profile = magic_user
        
        # Add spells based on the monster's domains and level
        self._add_monster_spells(monster, power_level)
        
        # Add resistances and weaknesses based on domains
        self._add_domain_based_attributes(monster)
        
        return monster
    
    def _determine_monster_domains(self, monster: Combatant) -> List[Domain]:
        """Determine appropriate magical domains for a monster based on its traits."""
        # This would typically use monster type, environment, etc.
        # For now, we'll assign domains randomly
        
        # Weighted randomization based on monster traits would be ideal
        domains = list(Domain)
        
        # Determine number of domains based on level
        num_domains = 1
        if monster.level >= 5:
            num_domains = 2
        if monster.level >= 15:
            num_domains = 3
        
        # Select domains randomly
        selected_domains = random.sample(domains, min(num_domains, len(domains)))
        
        return selected_domains
    
    def _calculate_monster_mana(self, monster: Combatant, power_level: float) -> int:
        """Calculate appropriate mana pool for a monster."""
        # Base mana calculation
        base_mana = 50 + (monster.level * 10)
        
        # Apply power level modifier
        modified_mana = int(base_mana * power_level)
        
        # Add random variance
        variance = random.uniform(0.8, 1.2)
        final_mana = int(modified_mana * variance)
        
        return final_mana
    
    def _add_monster_spells(self, monster: Combatant, power_level: float) -> None:
        """Add appropriate spells to a monster based on its domains and level."""
        if not monster.magic_profile:
            return
        
        # Determine number of spells based on level and power
        num_spells = 1 + int(monster.level / 3) + int(power_level)
        num_spells = min(num_spells, 7)  # Cap at 7 spells
        
        # Create a pool of potential spells
        spell_pool = []
        
        # Add domain-specific spells
        for domain in monster.magic_profile.primary_domains + monster.magic_profile.secondary_domains:
            if domain == Domain.ARCANE:
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Arcane Bolt", domain, EffectType.DAMAGE, DamageType.ARCANE
                ))
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Mystic Shield", domain, EffectType.SHIELD
                ))
                
            elif domain == Domain.ELEMENTAL:
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Firebolt", domain, EffectType.DAMAGE, DamageType.FIRE
                ))
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Ice Shard", domain, EffectType.DAMAGE, DamageType.ICE
                ))
                
            elif domain == Domain.NATURAL:
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Healing Touch", domain, EffectType.HEALING
                ))
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Poison Spray", domain, EffectType.DAMAGE, DamageType.POISON
                ))
                
            elif domain == Domain.DIVINE:
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Radiant Beam", domain, EffectType.DAMAGE, DamageType.LIGHT
                ))
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Blessed Shield", domain, EffectType.SHIELD
                ))
                
            elif domain == Domain.SHADOW:
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Shadow Bolt", domain, EffectType.DAMAGE, DamageType.DARKNESS
                ))
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Life Drain", domain, EffectType.DAMAGE, DamageType.NECROTIC
                ))
                
            elif domain == Domain.CHAOS:
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Chaos Blast", domain, EffectType.DAMAGE, DamageType.ARCANE
                ))
                spell_pool.append(self.magic_system.create_basic_spell(
                    "Warp Reality", domain, EffectType.CONTROL
                ))
                
            else:
                # Generic spell for other domains
                spell_pool.append(self.magic_system.create_basic_spell(
                    f"{domain.name} Energy", domain, EffectType.DAMAGE, DamageType.ARCANE
                ))
        
        # Select spells randomly from the pool
        selected_spells = random.sample(spell_pool, min(num_spells, len(spell_pool)))
        
        # Add the spells to the monster's known spells
        for spell in selected_spells:
            monster.magic_profile.learn_spell(spell.id)
    
    def _add_domain_based_attributes(self, monster: Combatant) -> None:
        """Add resistances and weaknesses based on the monster's magical domains."""
        if not monster.magic_profile:
            return
        
        # Add resistances based on primary domains
        for domain in monster.magic_profile.primary_domains:
            # Get damage types associated with this domain
            domain_damage_types = DamageType.get_domain_affinities().get(domain, [])
            
            # Add resistance to these damage types
            for damage_type in domain_damage_types:
                if damage_type not in monster.resistances:
                    monster.resistances[damage_type] = 0.25  # 25% resistance
        
        # Add weaknesses based on opposing domains
        for domain in monster.magic_profile.primary_domains:
            # Get the opposing domain
            opposing_domain = Domain.get_opposing_domains().get(domain)
            if opposing_domain:
                # Get damage types associated with the opposing domain
                opposing_damage_types = DamageType.get_domain_affinities().get(opposing_domain, [])
                
                # Add weakness to these damage types
                for damage_type in opposing_damage_types:
                    if damage_type not in monster.weaknesses:
                        monster.weaknesses[damage_type] = 0.25  # 25% weakness


class MagicalCombatManager:
    """
    Manages magical combat, including spell casting and magical effects.
    """
    def __init__(self, magic_system: MagicSystem):
        self.magic_system = magic_system
        self.active_combats = {}  # Dict[combat_id, Dict[str, Any]]
        self.combat_counter = 0
        self.monster_magic_integration = MonsterMagicIntegration(magic_system)
    
    def initialize_combat(self, combatants: List[Combatant], location_description: str = None) -> Dict[str, Any]:
        """
        Initialize a new combat encounter with the given combatants.
        Returns a dict with the combat information.
        """
        combat_id = f"combat_{self.combat_counter}"
        self.combat_counter += 1
        
        # Reset all combatants for the new combat
        for combatant in combatants:
            combatant.reset_combat_state()
        
        # Generate a combat leyline if applicable
        combat_leyline = self._generate_combat_leyline(location_description)
        
        # Store the combat information
        self.active_combats[combat_id] = {
            "id": combat_id,
            "combatants": {c.id: c for c in combatants},
            "turn_order": [],
            "current_turn": 0,
            "round": 0,
            "location_description": location_description,
            "combat_leyline": combat_leyline,
            "environmental_effects": [],
            "combat_log": []
        }
        
        # Calculate initiative and set turn order
        self._calculate_initiative(combat_id)
        
        return {
            "success": True,
            "combat_id": combat_id,
            "combatants": [c.name for c in combatants],
            "turn_order": self.active_combats[combat_id]["turn_order"],
            "combat_leyline": combat_leyline,
            "message": "Combat initialized successfully"
        }
    
    def _generate_combat_leyline(self, location_description: str = None) -> Dict[str, Any]:
        """
        Generate a combat leyline based on the location description.
        This is a source of magical energy that combatants can draw from during combat.
        """
        # Default leyline values
        leyline = {
            "strength": random.uniform(0.1, 0.5),  # Base leyline strength
            "stability": random.uniform(0.6, 0.9),  # How stable the leyline is
            "dominant_domains": [],  # Dominant magical domains
            "mana_pool": random.randint(20, 50),  # Available mana
            "resonance": 1.0  # Multiplier for spells cast using this leyline
        }
        
        if location_description:
            # Parse the location description to determine leyline properties
            if "magical" in location_description.lower() or "arcane" in location_description.lower():
                leyline["strength"] += 0.3
                leyline["mana_pool"] += 30
                
            if "ancient" in location_description.lower() or "power" in location_description.lower():
                leyline["strength"] += 0.2
                leyline["stability"] -= 0.1
                leyline["mana_pool"] += 20
                
            if "tranquil" in location_description.lower() or "peaceful" in location_description.lower():
                leyline["stability"] += 0.2
                
            if "chaotic" in location_description.lower() or "unstable" in location_description.lower():
                leyline["stability"] -= 0.3
                leyline["resonance"] += 0.5
            
            # Determine dominant domains based on keywords
            if "fire" in location_description.lower() or "flame" in location_description.lower():
                leyline["dominant_domains"].append(Domain.ELEMENTAL)
                
            if "forest" in location_description.lower() or "nature" in location_description.lower():
                leyline["dominant_domains"].append(Domain.NATURAL)
                
            if "holy" in location_description.lower() or "sacred" in location_description.lower():
                leyline["dominant_domains"].append(Domain.DIVINE)
                
            if "dark" in location_description.lower() or "shadow" in location_description.lower():
                leyline["dominant_domains"].append(Domain.SHADOW)
                
            if "study" in location_description.lower() or "library" in location_description.lower():
                leyline["dominant_domains"].append(Domain.ARCANE)
            
            # If no specific domains were identified, add a random one
            if not leyline["dominant_domains"]:
                leyline["dominant_domains"].append(random.choice(list(Domain)))
        else:
            # No location description, add a random domain
            leyline["dominant_domains"].append(random.choice(list(Domain)))
        
        return leyline
    
    def _calculate_initiative(self, combat_id: str) -> None:
        """Calculate initiative for all combatants and set the turn order."""
        if combat_id not in self.active_combats:
            return
        
        combat = self.active_combats[combat_id]
        combatants = combat["combatants"].values()
        
        # Calculate initiative for each combatant
        for combatant in combatants:
            # Base initiative from stats
            dexterity = combatant.stats.get("dexterity", 10)
            perception = combatant.stats.get("perception", 10)
            
            # Calculate initiative
            base_initiative = (dexterity + perception) / 2
            random_factor = random.uniform(0.8, 1.2)
            
            combatant.initiative = int(base_initiative * random_factor)
        
        # Sort combatants by initiative (highest first)
        sorted_combatants = sorted(
            combatants,
            key=lambda c: c.initiative,
            reverse=True
        )
        
        # Set turn order
        combat["turn_order"] = [c.id for c in sorted_combatants]
        combat["current_turn"] = 0
    
    def execute_magical_combat_move(self, caster: Combatant, target: Combatant, spell_id: str) -> Dict[str, Any]:
        """
        Execute a magical combat move (spell casting).
        Returns a dict with the result of the move.
        """
        # Check if the caster can cast the spell
        if not caster.can_cast_spell(spell_id):
            return {
                "success": False,
                "message": f"{caster.name} cannot cast this spell"
            }
        
        # Get the spell
        if spell_id not in self.magic_system.spells:
            return {
                "success": False,
                "message": "Spell not found"
            }
        
        spell = self.magic_system.spells[spell_id]
        
        # Check if the spell is on cooldown
        if spell.is_on_cooldown(caster.id):
            remaining = spell.get_remaining_cooldown(caster.id)
            return {
                "success": False,
                "message": f"Spell on cooldown for {remaining:.1f} seconds"
            }
        
        # Calculate spell power
        spell_power = caster.magic_profile.calculate_spell_power(spell)
        
        # Calculate mana cost
        mana_cost = spell.get_scaled_mana_cost(spell_power)
        
        # Attempt to spend mana
        if not caster.magic_profile.spend_mana(mana_cost):
            return {
                "success": False,
                "message": f"{caster.name} does not have enough mana"
            }
        
        # Mark spell as used
        spell.mark_used(caster.id)
        
        # Spend action points
        caster.action_points -= 1
        
        # Apply spell effects based on type
        result = self._apply_spell_effects(spell, spell_power, caster, target)
        
        # Add additional information to the result
        result["spell_id"] = spell_id
        result["spell_name"] = spell.name
        result["mana_cost"] = mana_cost
        result["spell_power"] = spell_power
        
        return result
    
    def _apply_spell_effects(self, spell: Spell, spell_power: float, caster: Combatant, target: Combatant) -> Dict[str, Any]:
        """Apply the effects of a spell in combat."""
        result = {
            "success": True,
            "message": f"{caster.name} cast {spell.name}",
            "combat_effects": []
        }
        
        # Process different effect types
        for effect_type in spell.effect_types:
            if effect_type == EffectType.DAMAGE:
                # Calculate damage
                base_damage = int(10 * spell_power)  # Base value, would be more complex in a real game
                
                # Apply damage
                damage_result = target.take_damage(base_damage, spell.damage_types[0] if spell.damage_types else None)
                
                result["combat_effects"].append({
                    "type": "damage",
                    "target": target.name,
                    "amount": damage_result["final_damage"],
                    "damage_type": spell.damage_types[0].name if spell.damage_types else "untyped"
                })
                
                # Update message
                result["message"] += f", dealing {damage_result['final_damage']} damage to {target.name}"
                
                # Check if target was defeated
                if damage_result["was_defeated"]:
                    result["message"] += f" and defeating them!"
                
            elif effect_type == EffectType.HEALING:
                # Calculate healing
                base_healing = int(8 * spell_power)  # Base value, would be more complex in a real game
                
                # Apply healing
                healing_result = target.heal(base_healing)
                
                result["combat_effects"].append({
                    "type": "healing",
                    "target": target.name,
                    "amount": healing_result["actual_healing"]
                })
                
                # Update message
                result["message"] += f", healing {target.name} for {healing_result['actual_healing']} health"
                
            elif effect_type == EffectType.BUFF:
                # Apply buff effect
                # This would be more complex in a real game
                buff_duration = 3  # rounds
                
                result["combat_effects"].append({
                    "type": "buff",
                    "target": target.name,
                    "duration": buff_duration,
                    "effect_description": f"Enhanced by {spell.name}"
                })
                
                # Update message
                result["message"] += f", buffing {target.name} for {buff_duration} rounds"
                
            elif effect_type == EffectType.DEBUFF:
                # Apply debuff effect
                # This would be more complex in a real game
                debuff_duration = 2  # rounds
                
                result["combat_effects"].append({
                    "type": "debuff",
                    "target": target.name,
                    "duration": debuff_duration,
                    "effect_description": f"Weakened by {spell.name}"
                })
                
                # Update message
                result["message"] += f", debuffing {target.name} for {debuff_duration} rounds"
                
            elif effect_type == EffectType.SHIELD:
                # Apply shield effect
                shield_amount = int(15 * spell_power)  # Base value
                shield_duration = 2  # rounds
                
                result["combat_effects"].append({
                    "type": "shield",
                    "target": target.name,
                    "amount": shield_amount,
                    "duration": shield_duration,
                    "effect_description": f"Protected by {spell.name}"
                })
                
                # Update message
                result["message"] += f", shielding {target.name} for {shield_amount} damage over {shield_duration} rounds"
        
        return result
    
    def draw_from_combat_leyline(self, combatant: Combatant, amount_requested: int) -> Dict[str, Any]:
        """
        Attempt to draw mana from the combat leyline.
        Returns a dict with the result of the attempt.
        """
        # Find the combat this combatant is participating in
        combat_id = None
        for cid, combat in self.active_combats.items():
            if combatant.id in combat["combatants"]:
                combat_id = cid
                break
        
        if not combat_id:
            return {
                "success": False,
                "message": "Combatant not found in any active combat"
            }
        
        combat = self.active_combats[combat_id]
        leyline = combat["combat_leyline"]
        
        # Check if the leyline has any mana left
        if leyline["mana_pool"] <= 0:
            return {
                "success": False,
                "message": "The leyline is depleted"
            }
        
        # Calculate how much mana can be drawn
        max_draw = min(amount_requested, leyline["mana_pool"])
        
        # Calculate draw efficiency based on combatant's domains and leyline properties
        efficiency = 1.0
        
        if combatant.magic_profile:
            # Check for domain resonance
            combatant_domains = combatant.magic_profile.primary_domains + combatant.magic_profile.secondary_domains
            for domain in combatant_domains:
                if domain in leyline["dominant_domains"]:
                    efficiency += 0.2  # 20% bonus per matching domain
            
            # Scale with magical skill
            mana_control = combatant.magic_profile.magic_skills.get("mana_control", 1)
            efficiency += (mana_control - 1) * 0.05  # 5% per skill level above 1
        
        # Stability affects efficiency
        stability_factor = leyline["stability"]
        if random.random() > stability_factor:
            # Leyline fluctuation
            efficiency *= random.uniform(0.5, 1.5)
        
        # Calculate final amount drawn
        amount_drawn = int(max_draw * efficiency)
        
        # Update leyline mana pool
        leyline["mana_pool"] -= max_draw
        
        # Add mana to the combatant
        if combatant.magic_profile:
            old_mana = combatant.magic_profile.mana_current
            combatant.magic_profile.mana_current = min(
                combatant.magic_profile.mana_current + amount_drawn,
                combatant.magic_profile.mana_max
            )
            actual_gained = combatant.magic_profile.mana_current - old_mana
        else:
            actual_gained = 0
        
        # Result
        return {
            "success": True,
            "amount_requested": amount_requested,
            "amount_drawn": amount_drawn,
            "actual_gained": actual_gained,
            "efficiency": efficiency,
            "leyline_remaining": leyline["mana_pool"],
            "message": f"{combatant.name} drew {actual_gained} mana from the leyline"
        }
    
    def generate_magical_environment_effect(self) -> Optional[Dict[str, Any]]:
        """
        Generate a random magical environmental effect that can influence combat.
        Returns a dict with the effect information, or None if no effect is generated.
        """
        # 20% chance of generating an effect
        if random.random() > 0.2:
            return None
        
        # Possible effect types
        effect_types = [
            "mana_surge",
            "energy_disruption",
            "elemental_manifestation",
            "magical_resonance",
            "arcane_anomaly"
        ]
        
        # Select a random effect type
        effect_type = random.choice(effect_types)
        
        # Generate effect details based on type
        if effect_type == "mana_surge":
            return {
                "effect_type": effect_type,
                "description": "A surge of magical energy floods the area",
                "game_effect": "All spellcasters regain 1d6 mana",
                "duration": "Instant"
            }
            
        elif effect_type == "energy_disruption":
            return {
                "effect_type": effect_type,
                "description": "Magical energies become unstable and difficult to control",
                "game_effect": "Spell costs increased by 50% for 1d3 rounds",
                "duration": f"{random.randint(1, 3)} rounds"
            }
            
        elif effect_type == "elemental_manifestation":
            elements = ["fire", "water", "earth", "air", "arcane"]
            element = random.choice(elements)
            
            return {
                "effect_type": effect_type,
                "description": f"A manifestation of {element} energy appears",
                "game_effect": f"{element.capitalize()} spells are empowered, opposing elements are weakened",
                "duration": f"{random.randint(2, 4)} rounds"
            }
            
        elif effect_type == "magical_resonance":
            return {
                "effect_type": effect_type,
                "description": "The area begins to resonate with magical energy",
                "game_effect": "Spells cast on consecutive turns grow in power",
                "duration": f"{random.randint(3, 5)} rounds"
            }
            
        elif effect_type == "arcane_anomaly":
            return {
                "effect_type": effect_type,
                "description": "An arcane anomaly warps the fabric of reality",
                "game_effect": "Spell targets are randomized",
                "duration": f"{random.randint(1, 2)} rounds"
            }
        
        return None
    
    def simulate_combat_victory(self, victor_name: str) -> Dict[str, Any]:
        """
        Simulate a combat victory for testing purposes.
        In a real game, this would be determined by the combat system.
        """
        # This is a simplified version for testing
        return {
            "success": True,
            "victor": victor_name,
            "message": f"{victor_name} is victorious!",
            "rewards": {
                "experience": random.randint(100, 500),
                "gold": random.randint(10, 100),
                "items": [f"Random Item {random.randint(1, 10)}"]
            }
        }