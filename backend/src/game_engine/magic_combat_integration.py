"""
Magic Combat Integration Module

This module integrates the magic system with the combat system,
allowing for magical attacks, defenses, and combat effects.
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union, TypeVar, Generic
import random
import math
import uuid
from enum import Enum, auto
from datetime import datetime, timedelta

# Import the core magic system
from game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, MagicEffect, Domain, 
    DamageType, EffectType, MagicTier
)

# Import for enhanced domain integration
from shared.models import Character, DomainType


class CombatantType(Enum):
    """Types of combatants in the combat system."""
    PLAYER = auto()
    NPC = auto()
    MONSTER = auto()
    SUMMONED = auto()
    ENVIRONMENTAL = auto()


class MoveType(Enum):
    """Types of combat moves."""
    ATTACK = auto()
    DEFEND = auto()
    SPELL = auto()
    ITEM_USE = auto()
    MOVEMENT = auto()
    SPECIAL = auto()


class Combatant:
    """
    Represents a participant in combat, which may have magical abilities.
    """
    def __init__(
        self,
        id: str,
        name: str,
        combatant_type: CombatantType,
        level: int = 1,
        max_health: int = 100,
        current_health: int = 100,
        stats: Dict[str, int] = None,
        resistances: Dict[DamageType, float] = None,  # 0.0 to 1.0 damage reduction
        weaknesses: Dict[DamageType, float] = None,   # Multiplier for damage
        immunities: Set[DamageType] = None,
        magic_profile: Optional[MagicUser] = None
    ):
        self.id = id
        self.name = name
        self.combatant_type = combatant_type
        self.level = level
        self.max_health = max_health
        self.current_health = current_health
        self.stats = stats or {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "perception": 10
        }
        self.resistances = resistances or {}
        self.weaknesses = weaknesses or {}
        self.immunities = immunities or set()
        self.magic_profile = magic_profile
        
        # Combat state
        self.status_effects = []
        self.combat_modifiers = {}
        self.last_action_time = 0
        self.equipped_items = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "combatant_type": self.combatant_type.name,
            "level": self.level,
            "max_health": self.max_health,
            "current_health": self.current_health,
            "stats": self.stats,
            "resistances": {dt.name: val for dt, val in self.resistances.items()},
            "weaknesses": {dt.name: val for dt, val in self.weaknesses.items()},
            "immunities": [dt.name for dt in self.immunities],
            "magic_profile": self.magic_profile.to_dict() if self.magic_profile else None,
            "status_effects": self.status_effects,
            "combat_modifiers": self.combat_modifiers
        }
    
    def take_damage(self, amount: int, damage_type: DamageType) -> Dict[str, Any]:
        """
        Apply damage to the combatant, accounting for resistances and weaknesses.
        
        Args:
            amount: The raw damage amount
            damage_type: The type of damage
            
        Returns:
            Dictionary with damage results
        """
        # Check for immunity
        if damage_type in self.immunities:
            return {
                "initial_damage": amount,
                "final_damage": 0,
                "damage_type": damage_type.name,
                "was_immune": True,
                "resistance_applied": 0,
                "weakness_applied": 0,
                "health_before": self.current_health,
                "health_after": self.current_health,
                "is_defeated": False
            }
        
        # Apply resistances
        resistance = self.resistances.get(damage_type, 0.0)
        resistance_multiplier = 1.0 - resistance
        
        # Apply weaknesses
        weakness = self.weaknesses.get(damage_type, 0.0)
        weakness_multiplier = 1.0 + weakness
        
        # Calculate final damage
        final_damage = int(amount * resistance_multiplier * weakness_multiplier)
        
        # Apply damage
        health_before = self.current_health
        self.current_health = max(0, self.current_health - final_damage)
        health_after = self.current_health
        is_defeated = self.current_health <= 0
        
        return {
            "initial_damage": amount,
            "final_damage": final_damage,
            "damage_type": damage_type.name,
            "was_immune": False,
            "resistance_applied": resistance,
            "weakness_applied": weakness,
            "health_before": health_before,
            "health_after": health_after,
            "is_defeated": is_defeated
        }
    
    def heal(self, amount: int) -> Dict[str, Any]:
        """
        Heal the combatant.
        
        Args:
            amount: The amount to heal
            
        Returns:
            Dictionary with healing results
        """
        health_before = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        health_after = self.current_health
        
        return {
            "amount": amount,
            "health_before": health_before,
            "health_after": health_after,
            "health_gained": health_after - health_before
        }
    
    def has_magic_capabilities(self) -> bool:
        """Check if the combatant has magical capabilities."""
        return self.magic_profile is not None


class CombatMove:
    """
    Represents a move made in combat.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        move_type: MoveType,
        base_power: float = 1.0,
        cooldown: float = 0.0,  # Time in seconds
        energy_cost: int = 0,
        targeting_type: str = "single",  # single, area, self, etc.
        range_max: float = 1.5,  # Maximum range in meters
        area_of_effect: float = 0.0,  # Radius in meters, 0 for single target
        effects: List[Dict[str, Any]] = None,
        stat_requirements: Dict[str, int] = None,
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.move_type = move_type
        self.base_power = base_power
        self.cooldown = cooldown
        self.energy_cost = energy_cost
        self.targeting_type = targeting_type
        self.range_max = range_max
        self.area_of_effect = area_of_effect
        self.effects = effects or []
        self.stat_requirements = stat_requirements or {}
        self.tags = tags or []
        self.last_used_time = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "move_type": self.move_type.name,
            "base_power": self.base_power,
            "cooldown": self.cooldown,
            "energy_cost": self.energy_cost,
            "targeting_type": self.targeting_type,
            "range_max": self.range_max,
            "area_of_effect": self.area_of_effect,
            "effects": self.effects,
            "stat_requirements": self.stat_requirements,
            "tags": self.tags
        }
    
    def is_on_cooldown(self, current_time: float) -> bool:
        """Check if the move is on cooldown."""
        return (current_time - self.last_used_time) < self.cooldown
    
    def use(self, current_time: float) -> None:
        """Use the move, updating its last used time."""
        self.last_used_time = current_time
    
    def meets_stat_requirements(self, combatant: Combatant) -> bool:
        """Check if a combatant meets the stat requirements for this move."""
        for stat, required_value in self.stat_requirements.items():
            if combatant.stats.get(stat, 0) < required_value:
                return False
        return True


class MonsterMagicIntegration:
    """
    Integrates magical capabilities with monsters.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
    
    def enhance_monster_with_magic(
        self,
        monster: Combatant,
        primary_domains: List[Domain] = None,
        secondary_domains: List[Domain] = None,
        spell_ids: List[str] = None,
        mana_max: int = None
    ) -> Combatant:
        """
        Enhance a monster with magical capabilities.
        
        Args:
            monster: The monster to enhance
            primary_domains: Primary magical domains for the monster
            secondary_domains: Secondary magical domains for the monster
            spell_ids: IDs of spells the monster knows
            mana_max: Maximum mana pool (if None, calculated based on level and stats)
            
        Returns:
            The enhanced monster
        """
        # Determine primary domains if not provided
        if not primary_domains:
            # Choose domains based on monster type/tags or randomly
            all_domains = list(Domain)
            primary_domains = [random.choice(all_domains)]
        
        # Determine secondary domains if not provided
        if not secondary_domains:
            all_domains = list(Domain)
            # Filter out primary domains to avoid duplicates
            available_domains = [d for d in all_domains if d not in primary_domains]
            # Choose 0-2 secondary domains
            num_secondary = random.randint(0, 2)
            secondary_domains = random.sample(available_domains, min(num_secondary, len(available_domains)))
        
        # Calculate mana max if not provided
        if mana_max is None:
            # Base on level and intelligence/wisdom
            intelligence = monster.stats.get("intelligence", 10)
            wisdom = monster.stats.get("wisdom", 10)
            mana_max = int((intelligence + wisdom) * monster.level * 1.5)
        
        # Create magic profile
        magic_profile = MagicUser(
            id=f"{monster.id}_magic",
            name=f"{monster.name}'s Magic",
            level=monster.level,
            mana_max=mana_max,
            mana_current=mana_max,
            mana_regen_rate=monster.level * 0.5,  # 0.5 per minute per level
            primary_domains=primary_domains,
            secondary_domains=secondary_domains,
            known_spells=set(spell_ids) if spell_ids else set(),
            magic_skills={
                "spellcasting": max(1, monster.level // 2),
                "concentration": max(1, monster.stats.get("wisdom", 10) // 3),
                "magical_knowledge": max(1, monster.stats.get("intelligence", 10) // 3),
                "mana_control": max(1, monster.level // 3)
            }
        )
        
        # Assign magic profile to monster
        monster.magic_profile = magic_profile
        
        # Add spell-based resistances based on domains
        for domain in primary_domains + secondary_domains:
            if domain == Domain.FIRE:
                monster.resistances[DamageType.FIRE] = monster.resistances.get(DamageType.FIRE, 0.0) + 0.2
            elif domain == Domain.ICE:
                monster.resistances[DamageType.ICE] = monster.resistances.get(DamageType.ICE, 0.0) + 0.2
            elif domain == Domain.LIGHTNING:
                monster.resistances[DamageType.LIGHTNING] = monster.resistances.get(DamageType.LIGHTNING, 0.0) + 0.2
            elif domain == Domain.ARCANE:
                monster.resistances[DamageType.ARCANE] = monster.resistances.get(DamageType.ARCANE, 0.0) + 0.2
            elif domain == Domain.DIVINE:
                monster.resistances[DamageType.DIVINE] = monster.resistances.get(DamageType.DIVINE, 0.0) + 0.2
            elif domain == Domain.SHADOW:
                monster.resistances[DamageType.SHADOW] = monster.resistances.get(DamageType.SHADOW, 0.0) + 0.2
        
        return monster
    
    def generate_monster_spells(
        self,
        monster: Combatant,
        num_spells: int = None,
        spell_templates: List[Dict[str, Any]] = None
    ) -> List[Spell]:
        """
        Generate spells for a monster based on its magical capabilities.
        
        Args:
            monster: The monster to generate spells for
            num_spells: Number of spells to generate (if None, based on level)
            spell_templates: Optional templates to use for generating spells
            
        Returns:
            List of generated spells
        """
        if not monster.magic_profile:
            return []
        
        # Determine number of spells if not provided
        if num_spells is None:
            num_spells = 1 + (monster.level // 3)  # 1 spell at level 1, +1 for every 3 levels
        
        generated_spells = []
        magic_profile = monster.magic_profile
        
        # Use templates if provided, otherwise generate from scratch
        if spell_templates:
            for i in range(min(num_spells, len(spell_templates))):
                template = spell_templates[i]
                
                # Create spell from template with some randomization
                spell_id = f"{monster.id}_spell_{i+1}"
                spell_name = template.get("name", f"{monster.name}'s Spell {i+1}")
                spell_description = template.get("description", "A monster spell")
                
                # Use template domains or monster's domains
                if "domains" in template:
                    domain_names = template["domains"]
                    domains = [Domain[name] for name in domain_names if hasattr(Domain, name)]
                else:
                    domains = magic_profile.primary_domains + magic_profile.secondary_domains[:1]
                    if not domains:
                        domains = [Domain.ARCANE]  # Default if no domains available
                
                # Use template damage types or infer from domains
                if "damage_types" in template:
                    damage_type_names = template["damage_types"]
                    damage_types = [DamageType[name] for name in damage_type_names if hasattr(DamageType, name)]
                else:
                    damage_types = self._infer_damage_types_from_domains(domains)
                
                # Use template effect types or infer from template
                if "effect_types" in template:
                    effect_type_names = template["effect_types"]
                    effect_types = [EffectType[name] for name in effect_type_names if hasattr(EffectType, name)]
                else:
                    # Default to damage
                    effect_types = [EffectType.DAMAGE]
                
                # Create spell
                spell = Spell(
                    id=spell_id,
                    name=spell_name,
                    description=spell_description,
                    domains=domains,
                    damage_types=damage_types,
                    effect_types=effect_types,
                    mana_cost=template.get("mana_cost", 10 + (monster.level * 2)),
                    casting_time=template.get("casting_time", 1.0),
                    cooldown=template.get("cooldown", 3.0),
                    base_power=template.get("base_power", 5.0 + monster.level),
                    level_req=template.get("level_req", max(1, monster.level - 2)),
                    tier=template.get("tier", self._determine_spell_tier(monster.level)),
                    targeting_type=template.get("targeting_type", "single"),
                    range_max=template.get("range_max", 10.0),
                    duration=template.get("duration", 0.0),
                    components=template.get("components", ["verbal", "somatic"]),
                    tags=template.get("tags", [domain.name.lower() for domain in domains])
                )
                
                generated_spells.append(spell)
                # Add to monster's known spells
                magic_profile.known_spells.add(spell.id)
                
                # Register with magic system if available
                if self.magic_system:
                    self.magic_system.register_spell(spell)
        else:
            # Generate from scratch based on monster's domains
            domains = magic_profile.primary_domains + magic_profile.secondary_domains
            
            for i in range(num_spells):
                # Choose a random domain from the monster's domains
                if domains:
                    spell_domain = random.choice(domains)
                    spell_domains = [spell_domain]
                else:
                    spell_domains = [Domain.ARCANE]  # Default if no domains available
                
                # Infer damage types from domain
                damage_types = self._infer_damage_types_from_domains(spell_domains)
                
                # Determine effect types (mostly damage, sometimes with additional effects)
                effect_types = [EffectType.DAMAGE]
                if random.random() < 0.3:  # 30% chance to add a secondary effect
                    secondary_effects = [
                        EffectType.DEBUFF, EffectType.CROWD_CONTROL, 
                        EffectType.TRANSFORMATION, EffectType.TELEPORTATION
                    ]
                    effect_types.append(random.choice(secondary_effects))
                
                # Create spell name and description
                spell_id = f"{monster.id}_spell_{i+1}"
                spell_name = self._generate_spell_name(spell_domains[0], damage_types[0] if damage_types else None)
                spell_description = f"A {spell_domains[0].name.lower()} spell that {self._describe_spell_effect(effect_types, damage_types)}."
                
                # Create spell
                spell = Spell(
                    id=spell_id,
                    name=spell_name,
                    description=spell_description,
                    domains=spell_domains,
                    damage_types=damage_types,
                    effect_types=effect_types,
                    mana_cost=10 + (monster.level * 2),
                    casting_time=1.0,
                    cooldown=random.uniform(2.0, 6.0),
                    base_power=5.0 + monster.level,
                    level_req=max(1, monster.level - 2),
                    tier=self._determine_spell_tier(monster.level),
                    targeting_type="single" if random.random() < 0.7 else "area",
                    range_max=random.uniform(5.0, 20.0),
                    duration=0.0 if effect_types == [EffectType.DAMAGE] else random.uniform(5.0, 30.0),
                    components=["verbal", "somatic"],
                    tags=[domain.name.lower() for domain in spell_domains] + \
                          [dt.name.lower() for dt in damage_types] + \
                          [et.name.lower() for et in effect_types]
                )
                
                generated_spells.append(spell)
                # Add to monster's known spells
                magic_profile.known_spells.add(spell.id)
                
                # Register with magic system if available
                if self.magic_system:
                    self.magic_system.register_spell(spell)
        
        return generated_spells
    
    def _infer_damage_types_from_domains(self, domains: List[Domain]) -> List[DamageType]:
        """Infer damage types from domains."""
        damage_types = []
        
        for domain in domains:
            if domain == Domain.FIRE:
                damage_types.append(DamageType.FIRE)
            elif domain == Domain.ICE:
                damage_types.append(DamageType.ICE)
            elif domain == Domain.LIGHTNING:
                damage_types.append(DamageType.LIGHTNING)
            elif domain == Domain.WATER:
                damage_types.append(DamageType.WATER)
            elif domain == Domain.EARTH:
                damage_types.append(DamageType.EARTH)
            elif domain == Domain.AIR:
                damage_types.append(DamageType.AIR)
            elif domain == Domain.ARCANE:
                damage_types.append(DamageType.ARCANE)
            elif domain == Domain.DIVINE:
                damage_types.append(DamageType.DIVINE)
            elif domain == Domain.NECROMANTIC:
                damage_types.append(DamageType.NECROTIC)
            elif domain == Domain.SHADOW:
                damage_types.append(DamageType.SHADOW)
            elif domain == Domain.VOID:
                damage_types.append(DamageType.VOID)
            elif domain == Domain.MIND:
                damage_types.append(DamageType.PSYCHIC)
            else:
                # Default to physical for domains without a clear damage type
                if DamageType.PHYSICAL not in damage_types:
                    damage_types.append(DamageType.PHYSICAL)
        
        # If no damage types were inferred, default to physical
        if not damage_types:
            damage_types = [DamageType.PHYSICAL]
        
        return damage_types
    
    def _determine_spell_tier(self, monster_level: int) -> MagicTier:
        """Determine spell tier based on monster level."""
        if monster_level <= 3:
            return MagicTier.LESSER
        elif monster_level <= 7:
            return MagicTier.MODERATE
        elif monster_level <= 12:
            return MagicTier.GREATER
        elif monster_level <= 18:
            return MagicTier.MASTER
        else:
            return MagicTier.LEGENDARY
    
    def _generate_spell_name(self, domain: Domain, damage_type: Optional[DamageType]) -> str:
        """Generate a name for a spell based on domain and damage type."""
        prefixes = {
            Domain.FIRE: ["Burning", "Scorching", "Flaming", "Inferno"],
            Domain.ICE: ["Freezing", "Chilling", "Frost", "Glacial"],
            Domain.LIGHTNING: ["Shocking", "Thundering", "Electric", "Storm"],
            Domain.WATER: ["Drowning", "Tidal", "Drenching", "Aquatic"],
            Domain.EARTH: ["Crushing", "Seismic", "Stone", "Mountain"],
            Domain.AIR: ["Gusting", "Cyclone", "Wind", "Tempest"],
            Domain.ARCANE: ["Arcane", "Mystic", "Eldritch", "Magical"],
            Domain.DIVINE: ["Holy", "Divine", "Sacred", "Blessed"],
            Domain.NECROMANTIC: ["Death", "Necrotic", "Withering", "Grave"],
            Domain.SHADOW: ["Shadow", "Umbral", "Darkening", "Tenebrous"],
            Domain.VOID: ["Void", "Nether", "Abyssal", "Cosmic"],
            Domain.MIND: ["Mind", "Psychic", "Mental", "Cerebral"]
        }
        
        suffixes = {
            DamageType.FIRE: ["Blast", "Nova", "Eruption", "Conflagration"],
            DamageType.ICE: ["Spike", "Storm", "Lance", "Shards"],
            DamageType.LIGHTNING: ["Bolt", "Shock", "Discharge", "Arc"],
            DamageType.WATER: ["Wave", "Torrent", "Surge", "Deluge"],
            DamageType.EARTH: ["Quake", "Slam", "Hammer", "Collapse"],
            DamageType.AIR: ["Gust", "Tornado", "Blast", "Tempest"],
            DamageType.ARCANE: ["Missile", "Beam", "Pulse", "Barrage"],
            DamageType.DIVINE: ["Smite", "Judgement", "Radiance", "Wrath"],
            DamageType.NECROTIC: ["Touch", "Grip", "Drain", "Rot"],
            DamageType.SHADOW: ["Tendril", "Veil", "Strike", "Grasp"],
            DamageType.VOID: ["Rift", "Collapse", "Implosion", "Tear"],
            DamageType.PSYCHIC: ["Assault", "Spike", "Blast", "Intrusion"]
        }
        
        # Get domain prefix
        domain_prefixes = prefixes.get(domain, ["Mysterious"])
        prefix = random.choice(domain_prefixes)
        
        # Get damage type suffix
        if damage_type and damage_type in suffixes:
            damage_suffixes = suffixes[damage_type]
            suffix = random.choice(damage_suffixes)
        else:
            # Generic suffixes if no damage type or not in the dictionary
            generic_suffixes = ["Spell", "Strike", "Attack", "Assault"]
            suffix = random.choice(generic_suffixes)
        
        return f"{prefix} {suffix}"
    
    def _describe_spell_effect(self, effect_types: List[EffectType], damage_types: List[DamageType]) -> str:
        """Generate a description of the spell's effect."""
        descriptions = []
        
        for effect_type in effect_types:
            if effect_type == EffectType.DAMAGE:
                if damage_types:
                    damage_type = damage_types[0]
                    if damage_type == DamageType.FIRE:
                        descriptions.append("burns enemies with intense flames")
                    elif damage_type == DamageType.ICE:
                        descriptions.append("freezes enemies with intense cold")
                    elif damage_type == DamageType.LIGHTNING:
                        descriptions.append("shocks enemies with electricity")
                    elif damage_type == DamageType.WATER:
                        descriptions.append("drowns enemies in a torrent of water")
                    elif damage_type == DamageType.EARTH:
                        descriptions.append("crushes enemies with stone and earth")
                    elif damage_type == DamageType.AIR:
                        descriptions.append("buffets enemies with powerful winds")
                    elif damage_type == DamageType.ARCANE:
                        descriptions.append("assaults enemies with pure magical energy")
                    elif damage_type == DamageType.DIVINE:
                        descriptions.append("smites enemies with holy power")
                    elif damage_type == DamageType.NECROTIC:
                        descriptions.append("drains the life force from enemies")
                    elif damage_type == DamageType.PSYCHIC:
                        descriptions.append("assaults the minds of enemies")
                    elif damage_type == DamageType.SHADOW:
                        descriptions.append("engulfs enemies in dark energy")
                    elif damage_type == DamageType.VOID:
                        descriptions.append("tears at the very essence of enemies")
                    else:
                        descriptions.append("damages enemies")
                else:
                    descriptions.append("damages enemies")
            elif effect_type == EffectType.HEALING:
                descriptions.append("restores health")
            elif effect_type == EffectType.BUFF:
                descriptions.append("enhances abilities")
            elif effect_type == EffectType.DEBUFF:
                descriptions.append("weakens enemies")
            elif effect_type == EffectType.CROWD_CONTROL:
                descriptions.append("restricts enemy movement")
            elif effect_type == EffectType.SUMMON:
                descriptions.append("summons allies to fight")
            elif effect_type == EffectType.TRANSFORMATION:
                descriptions.append("transforms the target")
            elif effect_type == EffectType.TELEPORTATION:
                descriptions.append("teleports the target")
            elif effect_type == EffectType.PROTECTION:
                descriptions.append("creates a protective barrier")
        
        return " and ".join(descriptions)


class MagicalCombatManager:
    """
    Manages combat involving magical abilities and effects.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
        self.monster_magic_integration = MonsterMagicIntegration(magic_system)
        
        # Combat data
        self.active_combats = {}  # combat_id -> combat data
        self.combat_logs = {}     # combat_id -> combat log
    
    def initiate_combat(
        self,
        combat_id: str,
        participants: List[Combatant],
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate a new combat encounter.
        
        Args:
            combat_id: ID for the combat encounter
            participants: List of combatants participating in the encounter
            location_id: Optional ID of the location where combat is taking place
            
        Returns:
            Dictionary with combat initialization details
        """
        # Get location magic profile if available
        location_profile = None
        if self.magic_system and location_id:
            location_profile = self.magic_system.location_magic_profiles.get(location_id)
        
        # Set up combat data
        combat_data = {
            "combat_id": combat_id,
            "status": "active",
            "participants": {combatant.id: combatant for combatant in participants},
            "initiative_order": self._calculate_initiative_order(participants),
            "current_turn_index": 0,
            "round_number": 1,
            "location_id": location_id,
            "location_magic_profile": location_profile.to_dict() if location_profile else None,
            "start_time": datetime.now().isoformat(),
            "last_action_time": datetime.now().isoformat(),
            "magical_effects_active": []
        }
        
        # Set up combat log
        combat_log = []
        
        # Add initiation entry to log
        combat_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "COMBAT_START",
            "message": f"Combat initiated with {len(participants)} participants.",
            "data": {
                "combat_id": combat_id,
                "participants": [p.name for p in participants],
                "location": location_id
            }
        })
        
        # Store combat data and log
        self.active_combats[combat_id] = combat_data
        self.combat_logs[combat_id] = combat_log
        
        return {
            "success": True,
            "message": "Combat initiated successfully",
            "combat_data": combat_data,
            "initiative_order": [p.id for p in combat_data["initiative_order"]]
        }
    
    def _calculate_initiative_order(self, participants: List[Combatant]) -> List[Combatant]:
        """
        Calculate initiative order for combat participants.
        
        Args:
            participants: List of combatants participating in the encounter
            
        Returns:
            List of combatants in initiative order
        """
        # Calculate initiative values
        initiative_values = []
        for combatant in participants:
            dexterity = combatant.stats.get("dexterity", 10)
            perception = combatant.stats.get("perception", 10)
            
            # Base initiative on dexterity and perception with some randomness
            initiative = dexterity + (perception * 0.5) + random.uniform(1, 10)
            
            # Apply magic-based modifiers if applicable
            if combatant.magic_profile:
                # Arcane users get a bonus
                for domain in combatant.magic_profile.primary_domains + combatant.magic_profile.secondary_domains:
                    if domain == Domain.ARCANE or domain == Domain.MIND:
                        initiative += 2  # Small bonus for arcane/mind mages
                
                # Initiative spells/effects could be applied here
            
            initiative_values.append((combatant, initiative))
        
        # Sort by initiative value (highest first)
        initiative_values.sort(key=lambda x: x[1], reverse=True)
        
        # Return sorted combatants
        return [iv[0] for iv in initiative_values]
    
    def cast_spell_in_combat(
        self,
        combat_id: str,
        caster_id: str,
        spell_id: str,
        target_ids: List[str],
        game_time: float
    ) -> Dict[str, Any]:
        """
        Cast a spell during combat using enhanced domain-based roll system.
        
        Args:
            combat_id: ID of the combat encounter
            caster_id: ID of the combatant casting the spell
            spell_id: ID of the spell to cast
            target_ids: IDs of the targets
            game_time: Current game time
            
        Returns:
            Dictionary with the result of the spell casting
        """
        # Get combat data
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return {
                "success": False,
                "message": f"Unknown combat: {combat_id}"
            }
        
        # Get caster
        caster = combat_data["participants"].get(caster_id)
        if not caster:
            return {
                "success": False,
                "message": f"Unknown caster: {caster_id}"
            }
        
        # Check if caster has magic capabilities
        if not caster.has_magic_capabilities():
            return {
                "success": False,
                "message": f"{caster.name} does not have magical capabilities"
            }
        
        # Check if caster's turn
        current_turn_combatant = combat_data["initiative_order"][combat_data["current_turn_index"]]
        if current_turn_combatant.id != caster_id:
            return {
                "success": False,
                "message": f"Not {caster.name}'s turn"
            }
        
        # Get magic system
        if not self.magic_system:
            return {
                "success": False,
                "message": "Magic system not available"
            }
        
        # Get spell
        spell = self.magic_system.spells.get(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Unknown spell: {spell_id}"
            }
        
        # Get targets
        targets = []
        for target_id in target_ids:
            target = combat_data["participants"].get(target_id)
            if target:
                targets.append(target)
        
        if not targets:
            return {
                "success": False,
                "message": "No valid targets specified"
            }
        
        # Enhanced Domain-Based Spell Casting Resolution
        # ===================================================
        
        # Check if caster has enhanced Character model for domain integration
        caster_character = None
        if hasattr(caster, 'character_model') and isinstance(caster.character_model, Character):
            caster_character = caster.character_model
        
        # Perform spell casting roll using enhanced domain system
        spell_success = True
        casting_roll_result = None
        
        if caster_character:
            # Determine primary domain for spell casting
            primary_domain = self._determine_spell_domain(spell)
            
            # Find relevant magic tags
            magic_tag = self._find_best_magic_tag(caster_character, spell)
            
            # Calculate spell difficulty based on tier and complexity
            base_difficulty = self._calculate_spell_difficulty(spell, targets[0] if targets else None)
            
            # Prepare action data for spell casting
            spell_action_data = {
                "label": f"Cast {spell.name}",
                "action_type": "spell_cast",
                "spell_id": spell_id,
                "spell_tier": spell.tier.value if hasattr(spell.tier, 'value') else str(spell.tier),
                "tags": [magic_tag] if magic_tag else [],
                "domains": [primary_domain.value],
                "difficulty_modifier": 0
            }
            
            # Add target data for resistance calculations
            target_data = None
            if targets:
                target_data = {
                    "level": targets[0].level,
                    "resistances": list(targets[0].resistances.keys()) if targets[0].resistances else [],
                    "weaknesses": list(targets[0].weaknesses.keys()) if targets[0].weaknesses else []
                }
            
            # Perform enhanced spell casting roll
            casting_roll_result = caster_character.roll_check_hybrid(
                domain_type=primary_domain,
                tag_name=magic_tag,
                difficulty=base_difficulty,
                action_data=spell_action_data,
                target=target_data,
                combat_state={"status": "active", "round": combat_data.get("round_number", 1)}
            )
            
            spell_success = casting_roll_result["success"]
            
            # Log enhanced spell casting attempt
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "SPELL_CASTING_ROLL",
                "message": f"{caster.name} attempts to cast {spell.name}",
                "data": {
                    "caster_id": caster_id,
                    "spell_id": spell_id,
                    "method": casting_roll_result.get("method", "dice"),
                    "method_reason": casting_roll_result.get("method_reason", ""),
                    "breakdown": casting_roll_result.get("breakdown", ""),
                    "total": casting_roll_result.get("total", 0),
                    "difficulty": casting_roll_result.get("difficulty", base_difficulty),
                    "success": spell_success,
                    "domains_used": casting_roll_result.get("domains_used", []),
                    "tags_used": casting_roll_result.get("tags_used", [])
                }
            }
            self.combat_logs[combat_id].append(log_entry)
        
        # If spell casting failed, handle failure
        if not spell_success:
            # Still consume some mana for the failed attempt
            if caster.magic_profile and spell.mana_cost:
                mana_consumed = max(1, spell.mana_cost // 2)  # Half mana for failed cast
                caster.magic_profile.use_mana(mana_consumed)
            
            failure_log = {
                "timestamp": datetime.now().isoformat(),
                "type": "SPELL_CAST_FAILED",
                "message": f"{caster.name} failed to cast {spell.name}",
                "data": {
                    "caster_id": caster_id,
                    "spell_id": spell_id,
                    "reason": "casting_roll_failed",
                    "mana_consumed": mana_consumed if 'mana_consumed' in locals() else 0
                }
            }
            self.combat_logs[combat_id].append(failure_log)
            
            return {
                "success": False,
                "message": f"{caster.name} failed to cast {spell.name}",
                "casting_roll_result": casting_roll_result,
                "combat_narration": f"{caster.name} attempts to cast {spell.name}, but the magic fizzles and fails to take hold."
            }
        
        # Spell casting succeeded - continue with original spell resolution
        # ================================================================
        
        # Get location
        location_id = combat_data.get("location_id")
        
        # Cast the spell using original magic system
        equipped_items = caster.equipped_items if hasattr(caster, "equipped_items") else None
        
        # Use the magic system to cast the spell
        cast_result = self.magic_system.cast_spell(
            caster_id=caster.magic_profile.id,
            spell_id=spell_id,
            target_id=targets[0].id if targets else None,
            location_id=location_id,
            current_time=game_time,
            equipped_items=equipped_items
        )
        
        # Enhance cast result with domain integration info
        if casting_roll_result:
            cast_result["enhanced_casting"] = {
                "method": casting_roll_result.get("method", "dice"),
                "domains_used": casting_roll_result.get("domains_used", []),
                "tags_used": casting_roll_result.get("tags_used", []),
                "total_roll": casting_roll_result.get("total", 0),
                "difficulty": casting_roll_result.get("difficulty", 0),
                "breakdown": casting_roll_result.get("breakdown", "")
            }
        
        if not cast_result["success"]:
            return cast_result
        
        # Process spell effects for each target
        target_results = []
        for target in targets:
            # Get target resistances and weaknesses
            target_resistances = target.resistances
            target_weaknesses = target.weaknesses
            
            # Calculate combined effect
            combined_effect = self.magic_system.calculate_combined_spell_effect(
                cast_result.get("effects", []),
                target_resistances,
                target_weaknesses
            )
            
            # Apply damage if any
            damage_result = None
            if combined_effect.get("total_damage", 0) > 0:
                # Determine damage type
                damage_type_str = next(iter(combined_effect.get("damage_by_type", {}).keys()), "PHYSICAL")
                try:
                    damage_type = DamageType[damage_type_str]
                except (KeyError, ValueError):
                    damage_type = DamageType.PHYSICAL
                
                # Apply damage to target
                damage_amount = int(combined_effect["total_damage"])
                damage_result = target.take_damage(damage_amount, damage_type)
            
            # Apply healing if any
            healing_result = None
            if combined_effect.get("total_healing", 0) > 0:
                healing_amount = int(combined_effect["total_healing"])
                healing_result = target.heal(healing_amount)
            
            # Apply status effects if any
            status_effects = []
            if combined_effect.get("has_buffs"):
                status_effects.append("BUFF")
            if combined_effect.get("has_debuffs"):
                status_effects.append("DEBUFF")
            if combined_effect.get("has_crowd_control"):
                status_effects.append("CROWD_CONTROL")
            
            # Add any active status effects to the target
            for effect in status_effects:
                if effect not in target.status_effects:
                    target.status_effects.append(effect)
            
            # Record result for this target
            target_results.append({
                "target_id": target.id,
                "target_name": target.name,
                "damage_result": damage_result,
                "healing_result": healing_result,
                "status_effects": status_effects,
                "combined_effect": combined_effect
            })
        
        # Log the spell casting
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SPELL_CAST",
            "message": f"{caster.name} cast {spell.name}.",
            "data": {
                "caster_id": caster_id,
                "spell_id": spell_id,
                "targets": [t.id for t in targets],
                "cast_result": cast_result,
                "target_results": target_results
            }
        }
        self.combat_logs[combat_id].append(log_entry)
        
        # Check if any targets were defeated
        defeated_targets = []
        for result in target_results:
            if result.get("damage_result", {}).get("is_defeated", False):
                defeated_target_id = result["target_id"]
                defeated_target = combat_data["participants"].get(defeated_target_id)
                if defeated_target:
                    defeated_targets.append(defeated_target)
                    
                    # Log defeat
                    defeat_log = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "COMBATANT_DEFEATED",
                        "message": f"{defeated_target.name} was defeated.",
                        "data": {
                            "defeated_id": defeated_target_id,
                            "defeated_by": caster_id,
                            "defeated_by_spell": spell_id
                        }
                    }
                    self.combat_logs[combat_id].append(defeat_log)
        
        # Advance turn
        self._advance_turn(combat_id)
        
        # Return the result
        return {
            "success": True,
            "message": f"{caster.name} successfully cast {spell.name}",
            "spell_cast_result": cast_result,
            "target_results": target_results,
            "defeated_targets": [t.id for t in defeated_targets],
            "current_turn": combat_data["initiative_order"][combat_data["current_turn_index"]].id
        }
    
    def _advance_turn(self, combat_id: str) -> None:
        """
        Advance to the next turn in combat.
        
        Args:
            combat_id: ID of the combat encounter
        """
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        # Move to next combatant
        combat_data["current_turn_index"] = (combat_data["current_turn_index"] + 1) % len(combat_data["initiative_order"])
        
        # If we've gone through all combatants, increment round number
        if combat_data["current_turn_index"] == 0:
            combat_data["round_number"] += 1
            
            # Log new round
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "ROUND_START",
                "message": f"Round {combat_data['round_number']} begins.",
                "data": {
                    "round_number": combat_data["round_number"]
                }
            }
            self.combat_logs[combat_id].append(log_entry)
        
        # Update last action time
        combat_data["last_action_time"] = datetime.now().isoformat()
    
    def get_combat_status(self, combat_id: str) -> Dict[str, Any]:
        """
        Get the current status of a combat encounter.
        
        Args:
            combat_id: ID of the combat encounter
            
        Returns:
            Dictionary with combat status
        """
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return {
                "success": False,
                "message": f"Unknown combat: {combat_id}"
            }
        
        # Get current turn combatant
        current_turn_combatant = combat_data["initiative_order"][combat_data["current_turn_index"]]
        
        # Prepare combatant summaries
        combatant_summaries = []
        for combatant in combat_data["initiative_order"]:
            combatant_summaries.append({
                "id": combatant.id,
                "name": combatant.name,
                "type": combatant.combatant_type.name,
                "health": {
                    "current": combatant.current_health,
                    "max": combatant.max_health,
                    "percentage": (combatant.current_health / combatant.max_health) * 100
                },
                "level": combatant.level,
                "status_effects": combatant.status_effects,
                "is_magical": combatant.has_magic_capabilities(),
                "is_defeated": combatant.current_health <= 0
            })
        
        return {
            "success": True,
            "combat_id": combat_id,
            "status": combat_data["status"],
            "round_number": combat_data["round_number"],
            "current_turn": {
                "combatant_id": current_turn_combatant.id,
                "combatant_name": current_turn_combatant.name
            },
            "combatants": combatant_summaries,
            "location_id": combat_data.get("location_id"),
            "magical_effects_active": combat_data.get("magical_effects_active", [])
        }
    
    def get_available_combat_actions(
        self,
        combat_id: str,
        combatant_id: str
    ) -> Dict[str, Any]:
        """
        Get available actions for a combatant in combat.
        
        Args:
            combat_id: ID of the combat encounter
            combatant_id: ID of the combatant
            
        Returns:
            Dictionary with available actions
        """
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return {
                "success": False,
                "message": f"Unknown combat: {combat_id}"
            }
        
        combatant = combat_data["participants"].get(combatant_id)
        if not combatant:
            return {
                "success": False,
                "message": f"Unknown combatant: {combatant_id}"
            }
        
        # Get basic actions
        basic_actions = [
            {
                "id": "attack",
                "name": "Attack",
                "type": "ATTACK",
                "description": "Make a basic attack against a target.",
                "requires_target": True,
                "target_type": "enemy"
            },
            {
                "id": "defend",
                "name": "Defend",
                "type": "DEFEND",
                "description": "Take a defensive stance, reducing incoming damage.",
                "requires_target": False
            },
            {
                "id": "move",
                "name": "Move",
                "type": "MOVEMENT",
                "description": "Reposition yourself on the battlefield.",
                "requires_target": False
            }
        ]
        
        # Get magical actions if applicable
        magical_actions = []
        if combatant.has_magic_capabilities() and self.magic_system:
            magic_profile = combatant.magic_profile
            
            # Get known spells
            for spell_id in magic_profile.known_spells:
                spell = self.magic_system.spells.get(spell_id)
                if spell:
                    # Check if spell can be cast (level and mana)
                    can_cast = magic_profile.level >= spell.level_req and magic_profile.mana_current >= spell.mana_cost
                    
                    magical_actions.append({
                        "id": spell_id,
                        "name": spell.name,
                        "type": "SPELL",
                        "description": spell.description,
                        "mana_cost": spell.mana_cost,
                        "requires_target": spell.targeting_type != "self",
                        "target_type": "enemy" if any(et == EffectType.DAMAGE for et in spell.effect_types) else "any",
                        "can_cast": can_cast,
                        "reason_if_cannot": None if can_cast else (
                            "Not enough mana" if magic_profile.mana_current < spell.mana_cost else
                            "Level too low" if magic_profile.level < spell.level_req else
                            "Unknown reason"
                        )
                    })
        
        # Get item actions if applicable
        item_actions = []
        if hasattr(combatant, "equipped_items") and combatant.equipped_items:
            # This would need integration with an item system
            pass
        
        return {
            "success": True,
            "combatant_id": combatant_id,
            "basic_actions": basic_actions,
            "magical_actions": magical_actions,
            "item_actions": item_actions,
            "special_actions": []  # Would be filled with character-specific special moves
        }
    
    def end_combat(
        self,
        combat_id: str,
        outcome: str,
        winning_side: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End a combat encounter.
        
        Args:
            combat_id: ID of the combat encounter
            outcome: Outcome of the combat (victory, defeat, draw, flee, etc.)
            winning_side: Optional identifier for the winning side
            
        Returns:
            Dictionary with combat end details
        """
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return {
                "success": False,
                "message": f"Unknown combat: {combat_id}"
            }
        
        # Update combat status
        combat_data["status"] = "ended"
        combat_data["end_time"] = datetime.now().isoformat()
        combat_data["outcome"] = outcome
        combat_data["winning_side"] = winning_side
        
        # Log combat end
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "COMBAT_END",
            "message": f"Combat ended with outcome: {outcome}",
            "data": {
                "outcome": outcome,
                "winning_side": winning_side,
                "total_rounds": combat_data["round_number"]
            }
        }
        self.combat_logs[combat_id].append(log_entry)
        
        # Summarize combat
        survivors = []
        defeated = []
        
        for combatant_id, combatant in combat_data["participants"].items():
            if combatant.current_health > 0:
                survivors.append({
                    "id": combatant_id,
                    "name": combatant.name,
                    "type": combatant.combatant_type.name,
                    "health_remaining": combatant.current_health,
                    "health_percentage": (combatant.current_health / combatant.max_health) * 100
                })
            else:
                defeated.append({
                    "id": combatant_id,
                    "name": combatant.name,
                    "type": combatant.combatant_type.name
                })
        
        # Return combat summary
        return {
            "success": True,
            "message": f"Combat ended with outcome: {outcome}",
            "combat_id": combat_id,
            "outcome": outcome,
            "winning_side": winning_side,
            "total_rounds": combat_data["round_number"],
            "survivors": survivors,
            "defeated": defeated,
            "location_id": combat_data.get("location_id"),
            "combat_log_available": True
        }
    
    def get_combat_log(self, combat_id: str) -> Dict[str, Any]:
        """
        Get the log for a combat encounter.
        
        Args:
            combat_id: ID of the combat encounter
            
        Returns:
            Dictionary with combat log
        """
        if combat_id not in self.combat_logs:
            return {
                "success": False,
                "message": f"No log available for combat: {combat_id}"
            }
        
        return {
            "success": True,
            "combat_id": combat_id,
            "log": self.combat_logs[combat_id]
        }
    
    def enhance_monster_for_combat(
        self, 
        monster: Combatant,
        spell_templates: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance a monster with magical capabilities for combat.
        
        Args:
            monster: The monster to enhance
            spell_templates: Optional templates for monster spells
            
        Returns:
            Dictionary with enhancement details
        """
        # Determine domains based on monster type/characteristics
        primary_domains = []
        secondary_domains = []
        
        # This could be expanded with more sophisticated domain selection logic
        if hasattr(monster, "monster_type"):
            monster_type = getattr(monster, "monster_type", "")
            if "fire" in monster_type.lower():
                primary_domains.append(Domain.FIRE)
            elif "ice" in monster_type.lower():
                primary_domains.append(Domain.ICE)
            elif "undead" in monster_type.lower():
                primary_domains.append(Domain.NECROMANTIC)
            elif "shadow" in monster_type.lower():
                primary_domains.append(Domain.SHADOW)
            elif "elemental" in monster_type.lower():
                primary_domains.append(Domain.ELEMENTAL)
        
        # If no primary domains determined, choose random ones
        if not primary_domains:
            all_domains = list(Domain)
            primary_domains = [random.choice(all_domains)]
        
        # Enhance the monster
        enhanced_monster = self.monster_magic_integration.enhance_monster_with_magic(
            monster=monster,
            primary_domains=primary_domains,
            secondary_domains=secondary_domains
        )
        
        # Generate spells for the monster
        spells = self.monster_magic_integration.generate_monster_spells(
            monster=enhanced_monster,
            spell_templates=spell_templates
        )
        
        return {
            "success": True,
            "monster_id": monster.id,
            "monster_name": monster.name,
            "primary_domains": [domain.name for domain in primary_domains],
            "secondary_domains": [domain.name for domain in secondary_domains],
            "generated_spells": [spell.to_dict() for spell in spells],
            "mana_pool": enhanced_monster.magic_profile.mana_max if enhanced_monster.magic_profile else 0
        }
    
    def _determine_spell_domain(self, spell) -> DomainType:
        """Determine the primary domain for casting a spell."""
        # Map spell schools/types to domains
        if hasattr(spell, 'school'):
            school_domain_map = {
                'evocation': DomainType.MIND,      # Raw magical power and theory
                'illusion': DomainType.SOCIAL,    # Deception and manipulation  
                'enchantment': DomainType.SOCIAL, # Mental influence
                'necromancy': DomainType.SPIRIT,  # Death and life force
                'divination': DomainType.AWARENESS, # Information gathering
                'abjuration': DomainType.SPIRIT,  # Protection and warding
                'transmutation': DomainType.CRAFT, # Changing and making
                'conjuration': DomainType.MIND    # Summoning and creation
            }
            
            school_str = str(spell.school).lower()
            for school, domain in school_domain_map.items():
                if school in school_str:
                    return domain
        
        # Default based on spell effects
        if hasattr(spell, 'effects'):
            for effect in spell.effects:
                if hasattr(effect, 'effect_type'):
                    if 'DAMAGE' in str(effect.effect_type):
                        return DomainType.MIND  # Destructive magic
                    elif 'HEAL' in str(effect.effect_type):
                        return DomainType.SPIRIT  # Healing magic
                    elif 'BUFF' in str(effect.effect_type) or 'DEBUFF' in str(effect.effect_type):
                        return DomainType.SOCIAL  # Enhancement/weakening
                    elif 'SUMMON' in str(effect.effect_type):
                        return DomainType.MIND  # Conjuration
                    elif 'CROWD_CONTROL' in str(effect.effect_type):
                        return DomainType.AUTHORITY  # Control magic
        
        # Default to Mind for magical theory and raw power
        return DomainType.MIND
    
    def _find_best_magic_tag(self, character: Character, spell) -> Optional[str]:
        """Find the best magic-related tag for the character."""
        magic_related_tags = []
        
        # Look for general magic tags
        for tag_name, tag in character.tags.items():
            tag_name_lower = tag_name.lower()
            if any(keyword in tag_name_lower for keyword in ['magic', 'spell', 'arcane', 'mana', 'enchant']):
                magic_related_tags.append((tag_name, tag.rank))
        
        # Look for specific spell school tags if spell has a school
        if hasattr(spell, 'school'):
            school_str = str(spell.school).lower()
            for tag_name, tag in character.tags.items():
                if school_str in tag_name.lower():
                    magic_related_tags.append((tag_name, tag.rank))
        
        # Return the highest ranked magic tag
        if magic_related_tags:
            return max(magic_related_tags, key=lambda x: x[1])[0]
        
        return None
    
    def _calculate_spell_difficulty(self, spell, target=None) -> int:
        """Calculate the difficulty for casting a spell."""
        base_difficulty = 10
        
        # Adjust for spell tier
        if hasattr(spell, 'tier'):
            tier_adjustments = {
                'CANTRIP': 0,
                'BASIC': 2,
                'INTERMEDIATE': 4,
                'ADVANCED': 6,
                'ARCANE_MASTERY': 8
            }
            tier_str = str(spell.tier)
            base_difficulty += tier_adjustments.get(tier_str, 2)
        
        # Adjust for spell complexity (mana cost as proxy)
        if hasattr(spell, 'mana_cost') and spell.mana_cost:
            complexity_modifier = min(spell.mana_cost // 10, 5)  # Max +5 for very expensive spells
            base_difficulty += complexity_modifier
        
        # Adjust for target resistances
        if target and hasattr(target, 'resistances'):
            resistance_count = len(target.resistances) if target.resistances else 0
            base_difficulty += resistance_count  # Each resistance adds +1 difficulty
        
        return base_difficulty