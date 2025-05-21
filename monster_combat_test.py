#!/usr/bin/env python3
"""
Simplified test script for the monster combat system.
This script demonstrates creating and battling monsters from YAML templates.
"""
import random
import yaml
from enum import Enum, auto
from typing import Dict, List, Set, Any, Optional, Tuple


# ======================================================================
# Core Combat System Classes (Simplified for the test)
# ======================================================================

class Domain(Enum):
    """Core domains that define character abilities and actions"""
    BODY = auto()         # Physical strength, endurance, athleticism
    MIND = auto()         # Intelligence, memory, logical reasoning
    CRAFT = auto()        # Making, fixing, technical skills
    AWARENESS = auto()    # Perception, intuition, reflexes
    SOCIAL = auto()       # Charisma, persuasion, intimidation
    AUTHORITY = auto()    # Leadership, command, willpower
    SPIRIT = auto()       # Connection to magic, emotion, faith
    FIRE = auto()         # Fire element
    WATER = auto()        # Water element
    EARTH = auto()        # Earth element
    AIR = auto()          # Air element
    LIGHT = auto()        # Light element
    DARKNESS = auto()     # Darkness element
    SOUND = auto()        # Sound element
    WIND = auto()         # Wind element
    ICE = auto()          # Ice element


class MoveType(Enum):
    """Types of combat moves that can be performed"""
    FORCE = auto()     # Direct, aggressive actions
    FOCUS = auto()     # Precision, targeted actions
    TRICK = auto()     # Deception, misdirection
    DEFEND = auto()    # Protection, evasion, blocking
    UTILITY = auto()   # Support, buffs, healing


class Status(Enum):
    """Status effects that can be applied to combatants"""
    ENERGIZED = auto()   # Positive status: increased damage
    VULNERABLE = auto()  # Negative status: increased damage taken


class ThreatCategory(Enum):
    """Categories of monster threats"""
    BEAST = auto()       # Natural animals, even if unusual
    MAGICAL = auto()     # Inherently magical creatures
    HUMANOID = auto()    # Human-like threats
    UNDEAD = auto()      # Formerly living creatures
    CONSTRUCT = auto()   # Created or artificial beings
    ABERRATION = auto()  # Strange, otherworldly entities
    ELEMENTAL = auto()   # Pure elemental beings
    SPIRIT = auto()      # Non-corporeal entities


class ThreatTier(Enum):
    """Tiers of monster threats, determining overall power level"""
    MINION = auto()      # Weak, often appear in groups
    STANDARD = auto()    # Average threat, common encounters
    ELITE = auto()       # Stronger, mini-boss level
    BOSS = auto()        # Major encounter centerpiece
    LEGENDARY = auto()   # Unique, campaign-defining threat


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
                 effects: List[str] = None):
        self.name = name
        self.description = description
        self.move_type = move_type
        self.domains = domains
        self.base_damage = base_damage
        self.stamina_cost = stamina_cost
        self.focus_cost = focus_cost
        self.spirit_cost = spirit_cost
        self.effects = effects or []


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
                 id: str = None):
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
        self.id = id or name.lower().replace(' ', '_')
    
    def take_damage(self, amount: int) -> int:
        """Apply damage to the combatant"""
        actual_amount = max(0, amount)
        self.current_health = max(0, self.current_health - actual_amount)
        return actual_amount
    
    def is_defeated(self) -> bool:
        """Check if the combatant is defeated"""
        return self.current_health <= 0


# ======================================================================
# Monster Archetype System
# ======================================================================

class MoveBehavior:
    """Defines a monster's combat move behavior and conditions for use"""
    
    def __init__(self,
                 name: str,
                 description: str,
                 move_type: MoveType,
                 domains: List[Domain],
                 priority: int = 5,
                 special_effects: List[str] = None):
        self.name = name
        self.description = description
        self.move_type = move_type
        self.domains = domains
        self.priority = priority
        self.special_effects = special_effects or []


class MonsterArchetype:
    """Template for creating monster instances"""
    
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
                 move_behaviors: List[MoveBehavior] = None):
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
        
        # Default tier adjustments
        self.tier_adjustments = {
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
    
    def get_domain_value(self, domain: Domain, tier: ThreatTier, level: int) -> int:
        """Calculate the value for a specific domain based on tier and level"""
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
        """Calculate the health for a monster instance"""
        base_health = 10 + (level * 5)
        tier_mult = self.tier_adjustments[tier]["health_mult"]
        return int(base_health * tier_mult * self.health_modifier)
    
    def get_resource_values(self, tier: ThreatTier, level: int) -> Tuple[int, int, int]:
        """Calculate resource values (stamina, focus, spirit) for a monster instance"""
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
        """Create combat moves for a monster instance"""
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


# ======================================================================
# Monster Database
# ======================================================================

class MonsterDatabase:
    """Database of monster archetypes loaded from YAML files"""
    
    def __init__(self):
        """Initialize the monster database"""
        self.archetypes = {}
        self.by_region = {}
        self.by_tier = {}
        self.by_category = {}
    
    def load_from_yaml(self, yaml_file_path: str) -> None:
        """Load monster archetypes from a YAML file"""
        try:
            with open(yaml_file_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
                
            if not data or 'monster_archetypes' not in data:
                print(f"Warning: No monster archetypes found in {yaml_file_path}")
                return
            
            # Extract region from file path
            region = yaml_file_path.split('_')[-1].split('.')[0] if '_' in yaml_file_path else "unknown"
            
            for monster_data in data['monster_archetypes']:
                archetype = self._create_archetype_from_yaml(monster_data)
                if archetype:
                    self.archetypes[archetype.id] = archetype
                    
                    # Add to region index
                    if region not in self.by_region:
                        self.by_region[region] = []
                    self.by_region[region].append(archetype.id)
                    
                    # Add to tier index
                    tier_str = monster_data.get('threat_tier', 'standard').upper()
                    try:
                        tier = ThreatTier[tier_str]
                    except KeyError:
                        tier = ThreatTier.STANDARD
                    
                    if tier not in self.by_tier:
                        self.by_tier[tier] = []
                    self.by_tier[tier].append(archetype.id)
                    
                    # Add to category index
                    category_name = monster_data.get('category', 'Beast').split('/')[0].strip()
                    try:
                        category = ThreatCategory[category_name.upper()]
                    except KeyError:
                        category = ThreatCategory.BEAST
                    
                    if category not in self.by_category:
                        self.by_category[category] = []
                    self.by_category[category].append(archetype.id)
            
            print(f"Loaded {len(data['monster_archetypes'])} monster archetypes from {yaml_file_path}")
        except Exception as e:
            print(f"Error loading monster archetypes from {yaml_file_path}: {e}")
    
    def _create_archetype_from_yaml(self, monster_data: Dict[str, Any]) -> Optional[MonsterArchetype]:
        """Create a monster archetype from YAML data"""
        try:
            name = monster_data.get('name', 'Unknown Monster')
            monster_id = name.lower().replace(' ', '_')
            
            # Parse description
            description = monster_data.get('description', '').strip()
            
            # Parse category
            category_str = monster_data.get('category', 'Beast')
            if '/' in category_str:
                # For dual categories, take the first one
                category_str = category_str.split('/')[0].strip()
            
            try:
                category = ThreatCategory[category_str.upper()]
            except KeyError:
                print(f"Warning: Unknown category '{category_str}' for monster '{name}', defaulting to BEAST")
                category = ThreatCategory.BEAST
            
            # Parse domains
            primary_domains = []
            for domain_str in monster_data.get('primary_domains', []):
                try:
                    primary_domains.append(Domain[domain_str])
                except KeyError:
                    print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
            
            weak_domains = []
            for domain_str in monster_data.get('weak_domains', []):
                try:
                    weak_domains.append(Domain[domain_str])
                except KeyError:
                    print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
            
            resistant_domains = []
            for domain_str in monster_data.get('resistant_domains', []):
                try:
                    resistant_domains.append(Domain[domain_str])
                except KeyError:
                    print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
            
            # Create move behaviors based on typical moves and special abilities
            move_behaviors = []
            
            # Parse typical moves
            for move_data in monster_data.get('typical_moves', []):
                move_name = move_data
                move_domain = None
                move_type = MoveType.FORCE
                
                # Check if move has domain specified in parentheses
                if '(' in move_data and ')' in move_data:
                    move_parts = move_data.split('(')
                    move_name = move_parts[0].strip()
                    domain_str = move_parts[1].strip(')').strip()
                    
                    try:
                        move_domain = Domain[domain_str]
                    except KeyError:
                        print(f"Warning: Unknown domain '{domain_str}' in move '{move_name}' for monster '{name}'")
                
                # Determine move type based on name hints
                if any(hint in move_name.lower() for hint in ['dodge', 'evade', 'hide', 'stealth', 'retreat']):
                    move_type = MoveType.DEFEND
                elif any(hint in move_name.lower() for hint in ['spell', 'magic', 'curse', 'hex', 'enchant']):
                    move_type = MoveType.FOCUS
                elif any(hint in move_name.lower() for hint in ['trick', 'deceive', 'confuse', 'distract']):
                    move_type = MoveType.TRICK
                elif any(hint in move_name.lower() for hint in ['utility', 'heal', 'buff', 'support']):
                    move_type = MoveType.UTILITY
                
                # Create move behavior
                domains = [move_domain] if move_domain else primary_domains[:1]
                
                move_behavior = MoveBehavior(
                    name=move_name,
                    description=f"{name} uses {move_name}",
                    move_type=move_type,
                    domains=domains,
                    priority=7,  # Default to medium-high priority
                    special_effects=[]
                )
                move_behaviors.append(move_behavior)
            
            # Parse special abilities for additional move behaviors or effects
            for ability in monster_data.get('special_abilities', []):
                # Add special effects to existing moves or create new utility moves
                for move in move_behaviors:
                    if any(keyword in ability.lower() for keyword in move.name.lower().split()):
                        move.special_effects.append(ability)
                        break
                else:
                    # Create a new utility move for this ability
                    move_behavior = MoveBehavior(
                        name=ability,
                        description=f"{name} uses {ability}",
                        move_type=MoveType.UTILITY,
                        domains=primary_domains[:1],
                        priority=5,  # Medium priority
                        special_effects=[ability]
                    )
                    move_behaviors.append(move_behavior)
            
            # Set stat modifiers based on threat tier
            health_mod = 1.0
            stamina_mod = 1.0
            focus_mod = 1.0
            spirit_mod = 1.0
            
            tier_str = monster_data.get('threat_tier', 'standard').upper()
            try:
                tier = ThreatTier[tier_str]
                
                if tier == ThreatTier.MINION:
                    health_mod = 0.7
                    stamina_mod = 0.8
                    focus_mod = 0.7
                    spirit_mod = 0.7
                elif tier == ThreatTier.ELITE:
                    health_mod = 1.5
                    stamina_mod = 1.3
                    focus_mod = 1.3
                    spirit_mod = 1.3
                elif tier == ThreatTier.BOSS:
                    health_mod = 2.5
                    stamina_mod = 2.0
                    focus_mod = 2.0
                    spirit_mod = 2.0
                elif tier == ThreatTier.LEGENDARY:
                    health_mod = 4.0
                    stamina_mod = 3.0
                    focus_mod = 3.0
                    spirit_mod = 3.0
            except KeyError:
                # Default to STANDARD if not found
                pass
            
            # Create the archetype
            archetype = MonsterArchetype(
                id=monster_id,
                name=name,
                description=description,
                category=category,
                primary_domains=primary_domains,
                weak_domains=weak_domains,
                resistant_domains=resistant_domains,
                health_modifier=health_mod,
                stamina_modifier=stamina_mod,
                focus_modifier=focus_mod,
                spirit_modifier=spirit_mod,
                move_behaviors=move_behaviors
            )
            
            return archetype
        except Exception as e:
            print(f"Error creating monster archetype: {e}")
            return None
    
    def get_archetype(self, archetype_id: str) -> Optional[MonsterArchetype]:
        """Get a monster archetype by ID"""
        return self.archetypes.get(archetype_id)
    
    def get_archetypes_by_region(self, region: str) -> List[MonsterArchetype]:
        """Get monster archetypes by region"""
        archetype_ids = self.by_region.get(region, [])
        return [self.archetypes[archetype_id] for archetype_id in archetype_ids if archetype_id in self.archetypes]
    
    def get_archetypes_by_tier(self, tier: ThreatTier) -> List[MonsterArchetype]:
        """Get monster archetypes by threat tier"""
        archetype_ids = self.by_tier.get(tier, [])
        return [self.archetypes[archetype_id] for archetype_id in archetype_ids if archetype_id in self.archetypes]
    
    def get_archetypes_by_category(self, category: ThreatCategory) -> List[MonsterArchetype]:
        """Get monster archetypes by category"""
        archetype_ids = self.by_category.get(category, [])
        return [self.archetypes[archetype_id] for archetype_id in archetype_ids if archetype_id in self.archetypes]
    
    def get_random_archetype(self, 
                           region: Optional[str] = None, 
                           tier: Optional[ThreatTier] = None,
                           category: Optional[ThreatCategory] = None) -> Optional[MonsterArchetype]:
        """Get a random monster archetype with optional filters"""
        filtered_ids = set(self.archetypes.keys())
        
        if region:
            region_ids = set(self.by_region.get(region, []))
            filtered_ids &= region_ids
        
        if tier:
            tier_ids = set(self.by_tier.get(tier, []))
            filtered_ids &= tier_ids
        
        if category:
            category_ids = set(self.by_category.get(category, []))
            filtered_ids &= category_ids
        
        if not filtered_ids:
            return None
        
        archetype_id = random.choice(list(filtered_ids))
        return self.archetypes.get(archetype_id)


def create_monster_from_archetype(
    archetype: MonsterArchetype,
    name: str = None,
    tier: ThreatTier = None,
    level: int = 1,
    variant_type: str = None
) -> Tuple[Combatant, List[CombatMove]]:
    """Create a monster combatant from an archetype"""
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


# ======================================================================
# Combat Controller
# ======================================================================

class CombatController:
    """Controller for resolving combat exchanges between combatants"""
    
    def __init__(self, environment_name: str = "Neutral Ground"):
        self.environment_name = environment_name
        self.round_number = 1
        self.history = []
    
    def resolve_combat_exchange(self,
                               actor_name: str,
                               actor_move: CombatMove,
                               target_name: str,
                               target_move: CombatMove,
                               actor: Combatant,
                               target: Combatant) -> Dict[str, Any]:
        """Resolve a combat exchange between two combatants"""
        # Calculate basic attack success and damage
        actor_damage = self._calculate_simple_damage(actor_move)
        target_damage = self._calculate_simple_damage(target_move)
        
        # Adjust for move types (simplified)
        if actor_move.move_type == MoveType.FORCE and target_move.move_type == MoveType.DEFEND:
            # Defense reduces damage
            actor_damage = max(0, actor_damage - 3)
        elif actor_move.move_type == MoveType.FOCUS and target_move.move_type == MoveType.FORCE:
            # Focus beats force
            actor_damage += 2
            target_damage -= 1
        elif actor_move.move_type == MoveType.TRICK and target_move.move_type == MoveType.FOCUS:
            # Tricks work well against focus
            actor_damage += 2
            target_damage -= 1
        
        # Apply damage to combatants
        actor.take_damage(target_damage)
        target.take_damage(actor_damage)
        
        # Generate outcome descriptions
        actor_outcome = self._get_outcome_description(actor_name, actor_damage, target_damage)
        target_outcome = self._get_outcome_description(target_name, target_damage, actor_damage)
        
        # Generate narrative
        narrative = self._generate_exchange_narrative(
            actor_name, actor_move, target_name, target_move, actor_damage, target_damage
        )
        
        # Create result dictionary
        result = {
            "actor_name": actor_name,
            "actor_move": actor_move.name,
            "actor_damage_dealt": actor_damage,
            "actor_damage_taken": target_damage,
            "actor_outcome": actor_outcome,
            "target_name": target_name,
            "target_move": target_move.name,
            "target_damage_dealt": target_damage,
            "target_damage_taken": actor_damage,
            "target_outcome": target_outcome,
            "narrative": narrative,
            "round": self.round_number,
            "environment": self.environment_name
        }
        
        # Log the result
        self.history.append(result)
        self.round_number += 1
        
        return result
    
    def _calculate_simple_damage(self, move: CombatMove) -> int:
        """Calculate a simple damage value for a move"""
        # Base damage plus small random variation
        base = move.base_damage
        variation = random.randint(-2, 2)
        return max(0, base + variation)
    
    def _get_outcome_description(self, name: str, damage_dealt: int, damage_taken: int) -> str:
        """Get a description of the combatant's outcome"""
        if damage_dealt > damage_taken * 2:
            return f"{name} overwhelmed their opponent"
        elif damage_dealt > damage_taken:
            return f"{name} gained the upper hand"
        elif damage_dealt == damage_taken:
            return f"{name} traded blows evenly"
        elif damage_taken > damage_dealt * 2:
            return f"{name} was overwhelmed"
        else:
            return f"{name} was at a disadvantage"
    
    def _generate_exchange_narrative(self,
                                  actor_name: str,
                                  actor_move: CombatMove,
                                  target_name: str,
                                  target_move: CombatMove,
                                  actor_damage: int,
                                  target_damage: int) -> str:
        """Generate a narrative description of the combat exchange"""
        templates = [
            f"{actor_name} used {actor_move.name}, while {target_name} responded with {target_move.name}. "
            f"The exchange ended with {actor_name} dealing {actor_damage} damage and taking {target_damage} damage.",
            
            f"As {actor_name} unleashed {actor_move.name}, {target_name} countered with {target_move.name}. "
            f"{actor_name} inflicted {actor_damage} damage, while suffering {target_damage} in return.",
            
            f"{actor_name}'s {actor_move.name} clashed with {target_name}'s {target_move.name} in the {self.environment_name}. "
            f"When the dust settled, {actor_name} had dealt {actor_damage} damage and received {target_damage}."
        ]
        
        return random.choice(templates)


# ======================================================================
# Helper Functions
# ======================================================================

def print_monster_stats(monster: Combatant, moves: List[CombatMove]) -> None:
    """Print the stats and moves of a monster"""
    print(f"\n{'=' * 50}")
    print(f"MONSTER: {monster.name}")
    print(f"{'=' * 50}")
    print(f"  Health: {monster.current_health}/{monster.max_health}")
    print(f"  Stamina: {monster.current_stamina}/{monster.max_stamina}")
    print(f"  Focus: {monster.current_focus}/{monster.max_focus}")
    print(f"  Spirit: {monster.current_spirit}/{monster.max_spirit}")
    
    print("\nDOMAIN VALUES:")
    for domain, value in monster.domains.items():
        print(f"  {domain.name}: {value}")
    
    print("\nAVAILABLE MOVES:")
    for i, move in enumerate(moves, 1):
        domains_str = ", ".join([d.name for d in move.domains])
        print(f"  {i}. {move.name} ({move.move_type.name}) - Domains: {domains_str}")
        print(f"     Damage: {move.base_damage} | Costs: {move.stamina_cost} stamina, {move.focus_cost} focus, {move.spirit_cost} spirit")
        if move.effects:
            print(f"     Effects: {', '.join(move.effects)}")
        print()


def simulate_combat_round(controller: CombatController, 
                          monster1: Combatant, monster1_moves: List[CombatMove],
                          monster2: Combatant, monster2_moves: List[CombatMove]) -> Dict[str, Any]:
    """Simulate a round of combat between two monsters"""
    
    # Randomly select moves for each monster
    monster1_move = random.choice(monster1_moves)
    monster2_move = random.choice(monster2_moves)
    
    print(f"\n{'-' * 50}")
    print(f"COMBAT ROUND: {monster1.name} vs {monster2.name}")
    print(f"{'-' * 50}")
    print(f"{monster1.name} uses {monster1_move.name} ({monster1_move.move_type.name})")
    print(f"{monster2.name} uses {monster2_move.name} ({monster2_move.move_type.name})")
    
    # Resolve the combat exchange
    result = controller.resolve_combat_exchange(
        actor_name=monster1.name,
        actor_move=monster1_move,
        target_name=monster2.name,
        target_move=monster2_move,
        actor=monster1,
        target=monster2
    )
    
    # Print the results
    print("\nRESULTS:")
    print(f"  {monster1.name}: {result['actor_outcome']}")
    print(f"    Health: {monster1.current_health}/{monster1.max_health}")
    print(f"  {monster2.name}: {result['target_outcome']}")
    print(f"    Health: {monster2.current_health}/{monster2.max_health}")
    
    print("\nNARRATIVE:")
    print(f"  {result['narrative']}")
    
    return result


def load_monster_database(monster_db: MonsterDatabase) -> None:
    """Load monster YAML files into the database"""
    # Look for monster YAML files in the data directory
    import os
    data_dir = './data/monsters'
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                file_path = os.path.join(data_dir, filename)
                monster_db.load_from_yaml(file_path)
    else:
        print(f"Monster data directory {data_dir} does not exist.")


def get_random_monster(
    monster_db: MonsterDatabase,
    region: Optional[str] = None,
    tier: Optional[ThreatTier] = None,
    category: Optional[ThreatCategory] = None,
    level: int = 1
) -> Tuple[Combatant, List[CombatMove]]:
    """Get a random monster from the database with optional filters"""
    archetype = monster_db.get_random_archetype(region, tier, category)
    if not archetype:
        raise ValueError(f"No monster found matching the criteria (region={region}, tier={tier}, category={category})")
    
    return create_monster_from_archetype(
        archetype=archetype,
        tier=tier,
        level=level
    )


# ======================================================================
# Main Function
# ======================================================================

def main():
    """Main function to test the combat system"""
    print("Loading monster database...")
    monster_db = MonsterDatabase()
    load_monster_database(monster_db)
    
    if not monster_db.archetypes:
        print("No monsters loaded. Check that the data directory exists and contains YAML files.")
        return
    
    # Create a combat controller
    controller = CombatController(environment_name="Verdant Forest")
    
    # Generate monsters from database
    try:
        print("\nGenerating a monster from the Verdant region...")
        verdant_monster, verdant_moves = get_random_monster(
            monster_db=monster_db,
            region="verdant",
            tier=ThreatTier.STANDARD,
            level=3
        )
        
        print("\nGenerating a monster from the Ember region...")
        ember_monster, ember_moves = get_random_monster(
            monster_db=monster_db,
            region="ember",
            tier=ThreatTier.ELITE,
            level=5
        )
        
        # Print the monsters' stats
        print_monster_stats(verdant_monster, verdant_moves)
        print_monster_stats(ember_monster, ember_moves)
        
        # Simulate multiple rounds of combat
        for _ in range(3):
            result = simulate_combat_round(
                controller=controller,
                monster1=verdant_monster,
                monster1_moves=verdant_moves,
                monster2=ember_monster,
                monster2_moves=ember_moves
            )
            
            # Check if either monster is defeated
            if verdant_monster.is_defeated():
                print(f"\n{verdant_monster.name} has been defeated by {ember_monster.name}!")
                break
            elif ember_monster.is_defeated():
                print(f"\n{ember_monster.name} has been defeated by {verdant_monster.name}!")
                break
        
        print("\nCombat simulation completed.")
    
    except Exception as e:
        print(f"Error during combat simulation: {e}")


if __name__ == "__main__":
    main()