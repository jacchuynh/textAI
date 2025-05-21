#!/usr/bin/env python3
"""
Player vs Monster Combat Demo

This script demonstrates how a player would engage in combat with a monster.
It features player choice, domain-based combat resolution, and combat narration.
"""
import random
import yaml
from enum import Enum, auto
from typing import Dict, List, Set, Any, Optional, Tuple


# ======================================================================
# Core Combat System Classes
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
    
    def can_be_used(self, combatant) -> bool:
        """Check if the combatant has enough resources to use this move"""
        return (combatant.current_stamina >= self.stamina_cost and
                combatant.current_focus >= self.focus_cost and
                combatant.current_spirit >= self.spirit_cost)
    
    def use(self, combatant) -> bool:
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
    
    def heal(self, amount: int) -> int:
        """Heal the combatant"""
        before = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - before
    
    def recover_resources(self, stamina: int = 0, focus: int = 0, spirit: int = 0) -> None:
        """Recover resources"""
        self.current_stamina = min(self.max_stamina, self.current_stamina + stamina)
        self.current_focus = min(self.max_focus, self.current_focus + focus)
        self.current_spirit = min(self.max_spirit, self.current_spirit + spirit)


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
                               actor: Combatant,
                               actor_move: CombatMove,
                               target: Combatant,
                               target_move: CombatMove) -> Dict[str, Any]:
        """Resolve a combat exchange between two combatants"""
        if not actor_move.use(actor):
            print(f"{actor.name} doesn't have enough resources to use {actor_move.name}!")
            return {"success": False}
        
        if not target_move.use(target):
            print(f"{target.name} doesn't have enough resources to use {target_move.name}!")
            return {"success": False}
        
        # Apply domain bonuses to base damage
        actor_domain_bonus = self._get_domain_bonus(actor, actor_move)
        target_domain_bonus = self._get_domain_bonus(target, target_move)
        
        actor_damage = int(actor_move.base_damage * actor_domain_bonus)
        target_damage = int(target_move.base_damage * target_domain_bonus)
        
        # Add randomness (d20 system)
        actor_roll = random.randint(1, 20)
        target_roll = random.randint(1, 20)
        
        actor_damage = max(0, actor_damage + (actor_roll // 5))
        target_damage = max(0, target_damage + (target_roll // 5))
        
        # Adjust for move types (rock-paper-scissors style)
        if actor_move.move_type == MoveType.FORCE and target_move.move_type == MoveType.DEFEND:
            # Defense reduces damage
            actor_damage = max(0, actor_damage - 3)
            print(f"{target.name}'s {target_move.name} reduces incoming damage!")
        elif actor_move.move_type == MoveType.FOCUS and target_move.move_type == MoveType.FORCE:
            # Focus beats force
            actor_damage += 2
            target_damage -= 1
            print(f"{actor.name}'s focused attack counters {target.name}'s forceful approach!")
        elif actor_move.move_type == MoveType.TRICK and target_move.move_type == MoveType.FOCUS:
            # Tricks work well against focus
            actor_damage += 2
            target_damage -= 1
            print(f"{actor.name}'s trickery disrupts {target.name}'s concentration!")
        elif actor_move.move_type == MoveType.DEFEND and target_move.move_type == MoveType.TRICK:
            # Defense works well against tricks
            actor_damage -= 1
            target_damage -= 2
            print(f"{actor.name}'s defenses are tough to trick!")
        
        # Utility moves have special handling
        if actor_move.move_type == MoveType.UTILITY:
            # Healing or buffing effect
            if "heal" in actor_move.name.lower() or "regenerate" in actor_move.name.lower():
                heal_amount = max(3, actor_damage // 2)
                actor.heal(heal_amount)
                print(f"{actor.name} recovers {heal_amount} health from {actor_move.name}!")
                actor_damage = 0  # Utility moves often don't deal damage
        
        if target_move.move_type == MoveType.UTILITY:
            # Healing or buffing effect
            if "heal" in target_move.name.lower() or "regenerate" in target_move.name.lower():
                heal_amount = max(3, target_damage // 2)
                target.heal(heal_amount)
                print(f"{target.name} recovers {heal_amount} health from {target_move.name}!")
                target_damage = 0  # Utility moves often don't deal damage
        
        # Apply damage
        actual_actor_damage = target.take_damage(actor_damage)
        actual_target_damage = actor.take_damage(target_damage)
        
        # Generate outcome descriptions
        actor_outcome = self._get_outcome_description(actor.name, actor_damage, target_damage)
        target_outcome = self._get_outcome_description(target.name, target_damage, actor_damage)
        
        # Generate narrative
        narrative = self._generate_exchange_narrative(
            actor.name, actor_move, target.name, target_move, actor_damage, target_damage
        )
        
        # Create result dictionary
        result = {
            "success": True,
            "actor_name": actor.name,
            "actor_move": actor_move.name,
            "actor_damage_dealt": actor_damage,
            "actor_damage_taken": target_damage,
            "actor_outcome": actor_outcome,
            "actor_roll": actor_roll,
            "target_name": target.name,
            "target_move": target_move.name,
            "target_damage_dealt": target_damage,
            "target_damage_taken": actor_damage,
            "target_outcome": target_outcome,
            "target_roll": target_roll,
            "narrative": narrative,
            "round": self.round_number,
            "environment": self.environment_name
        }
        
        # Log the result
        self.history.append(result)
        self.round_number += 1
        
        return result
    
    def _get_domain_bonus(self, combatant: Combatant, move: CombatMove) -> float:
        """Calculate a bonus multiplier based on the combatant's domain values for the move"""
        if not move.domains:
            return 1.0
        
        total_domain_value = 0
        for domain in move.domains:
            total_domain_value += combatant.domains.get(domain, 0)
        
        # Average value of all domains used by the move
        avg_domain = total_domain_value / len(move.domains)
        
        # Bonus scales from 0.8 to 2.0 based on domain values
        # Domain 0 = 0.8x damage, Domain 5 = 1.5x damage, Domain 10 = 2.0x damage
        return 0.8 + (min(10, avg_domain) * 0.12)
    
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
        
        # Add special narration for critical success (roll of 20)
        if "actor_roll" in self.history[-1] and self.history[-1]["actor_roll"] >= 18:
            templates.append(
                f"{actor_name} executed a perfect {actor_move.name}, catching {target_name} off guard despite their {target_move.name}. "
                f"The masterful attack dealt {actor_damage} damage while {actor_name} only suffered {target_damage} in return."
            )
        
        # Add special narration for critical failure (roll of 1)
        if "actor_roll" in self.history[-1] and self.history[-1]["actor_roll"] <= 3:
            templates.append(
                f"{actor_name} stumbled while attempting {actor_move.name}, giving {target_name} an opening with {target_move.name}. "
                f"The mistake resulted in only {actor_damage} damage dealt while taking {target_damage} damage."
            )
        
        return random.choice(templates)


# ======================================================================
# Monster Generation
# ======================================================================

def load_monster_from_yaml(yaml_file_path: str, monster_name: str = None, tier: ThreatTier = ThreatTier.STANDARD):
    """Load a single monster from a YAML file, optionally filtering by name"""
    try:
        with open(yaml_file_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            
        if not data or 'monster_archetypes' not in data:
            print(f"Warning: No monster archetypes found in {yaml_file_path}")
            return None, []
        
        # Find the specified monster or pick a random one
        monsters = data['monster_archetypes']
        if monster_name:
            monster_data = next((m for m in monsters if m['name'] == monster_name), None)
            if not monster_data:
                print(f"Monster '{monster_name}' not found in {yaml_file_path}")
                return None, []
        else:
            monster_data = random.choice(monsters)
        
        # Create the monster
        return create_monster_from_data(monster_data, tier)
        
    except Exception as e:
        print(f"Error loading monster from {yaml_file_path}: {e}")
        return None, []


def create_monster_from_data(monster_data: Dict[str, Any], tier: ThreatTier, level: int = 3) -> Tuple[Combatant, List[CombatMove]]:
    """Create a monster from parsed YAML data"""
    name = monster_data['name']
    
    # Parse domain listings
    domain_values = {}
    for domain in Domain:
        domain_values[domain] = 1  # Base value for all domains
    
    # Apply tier bonuses to primary domains
    tier_bonus = {
        ThreatTier.MINION: 0,
        ThreatTier.STANDARD: 1,
        ThreatTier.ELITE: 2,
        ThreatTier.BOSS: 3,
        ThreatTier.LEGENDARY: 4
    }.get(tier, 1)
    
    # Parse domains and apply bonuses
    for domain_str in monster_data.get('primary_domains', []):
        try:
            domain = Domain[domain_str]
            domain_values[domain] = 2 + level // 2 + tier_bonus
        except KeyError:
            print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
    
    # Lower values for weak domains
    for domain_str in monster_data.get('weak_domains', []):
        try:
            domain = Domain[domain_str]
            domain_values[domain] = max(0, domain_values[domain] - 2)
        except KeyError:
            print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
    
    # Calculate health and resources based on tier and level
    tier_health_mult = {
        ThreatTier.MINION: 0.7,
        ThreatTier.STANDARD: 1.0,
        ThreatTier.ELITE: 1.5,
        ThreatTier.BOSS: 2.5,
        ThreatTier.LEGENDARY: 4.0
    }.get(tier, 1.0)
    
    max_health = int((10 + level * 5) * tier_health_mult)
    max_stamina = int((10 + level * 2) * tier_health_mult)
    max_focus = int((10 + level * 2) * tier_health_mult)
    max_spirit = int((10 + level * 2) * tier_health_mult)
    
    # Create the combatant
    monster = Combatant(
        name=name,
        domains=domain_values,
        max_health=max_health,
        current_health=max_health,
        max_stamina=max_stamina,
        current_stamina=max_stamina,
        max_focus=max_focus,
        current_focus=max_focus,
        max_spirit=max_spirit,
        current_spirit=max_spirit
    )
    
    # Create combat moves
    moves = []
    
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
                continue
        
        # Determine move type based on name hints
        if any(hint in move_name.lower() for hint in ['dodge', 'evade', 'hide', 'stealth', 'retreat', 'shield', 'protect']):
            move_type = MoveType.DEFEND
        elif any(hint in move_name.lower() for hint in ['spell', 'magic', 'curse', 'hex', 'enchant', 'focus']):
            move_type = MoveType.FOCUS
        elif any(hint in move_name.lower() for hint in ['trick', 'deceive', 'confuse', 'distract']):
            move_type = MoveType.TRICK
        
        # Create domains list
        domains = []
        if move_domain:
            domains.append(move_domain)
        else:
            # Use the first primary domain if none specified
            for domain_str in monster_data.get('primary_domains', []):
                try:
                    domains.append(Domain[domain_str])
                    break
                except KeyError:
                    continue
        
        if not domains:
            domains.append(Domain.BODY)  # Default to BODY if no domains found
        
        # Calculate base damage
        tier_damage_mult = {
            ThreatTier.MINION: 0.8,
            ThreatTier.STANDARD: 1.0,
            ThreatTier.ELITE: 1.2,
            ThreatTier.BOSS: 1.5,
            ThreatTier.LEGENDARY: 2.0
        }.get(tier, 1.0)
        
        base_damage = int((2 + level // 2) * tier_damage_mult)
        
        # Adjust damage based on move type
        if move_type == MoveType.FORCE:
            base_damage = int(base_damage * 1.2)  # Force moves deal more damage
        elif move_type == MoveType.FOCUS:
            base_damage = int(base_damage * 0.8)  # Focus moves deal less direct damage
        
        # Create the move
        move = CombatMove(
            name=move_name,
            description=f"{name} uses {move_name}",
            move_type=move_type,
            domains=domains,
            base_damage=base_damage,
            stamina_cost=max(1, base_damage // 3) if move_type == MoveType.FORCE else 0,
            focus_cost=max(1, base_damage // 3) if move_type == MoveType.FOCUS else 0,
            spirit_cost=max(1, base_damage // 4) if move_type == MoveType.TRICK else 0
        )
        
        moves.append(move)
    
    # Create utility moves from special abilities
    for ability in monster_data.get('special_abilities', []):
        ability_name = ability.split(' - ')[0].strip()
        ability_desc = ability.split(' - ')[1].strip() if ' - ' in ability else ability
        
        # Determine primary domain for the ability
        domains = []
        if any(kw in ability_desc.lower() for kw in ['fire', 'flame', 'burn', 'heat', 'ember']):
            domains.append(Domain.FIRE)
        elif any(kw in ability_desc.lower() for kw in ['water', 'ice', 'frost', 'liquid', 'cold']):
            domains.append(Domain.WATER)
        elif any(kw in ability_desc.lower() for kw in ['earth', 'stone', 'rock', 'soil', 'ground']):
            domains.append(Domain.EARTH)
        elif any(kw in ability_desc.lower() for kw in ['air', 'wind', 'breath', 'sky']):
            domains.append(Domain.AIR)
        elif any(kw in ability_desc.lower() for kw in ['light', 'radiant', 'holy', 'sun']):
            domains.append(Domain.LIGHT)
        elif any(kw in ability_desc.lower() for kw in ['dark', 'shadow', 'void', 'night']):
            domains.append(Domain.DARKNESS)
        elif any(kw in ability_desc.lower() for kw in ['heal', 'regenerate', 'recover', 'restore']):
            domains.append(Domain.SPIRIT)
        else:
            # Default to the first primary domain
            for domain_str in monster_data.get('primary_domains', []):
                try:
                    domains.append(Domain[domain_str])
                    break
                except KeyError:
                    continue
        
        if not domains:
            domains.append(Domain.BODY)  # Default
        
        # Create the utility move
        move = CombatMove(
            name=ability_name,
            description=ability_desc,
            move_type=MoveType.UTILITY,
            domains=domains,
            base_damage=max(1, base_damage // 2),  # Utility moves often deal less damage
            stamina_cost=1,
            focus_cost=1,
            spirit_cost=1,
            effects=[ability_desc]
        )
        
        moves.append(move)
    
    # Ensure there's at least a basic attack if no moves are defined
    if not moves:
        default_move = CombatMove(
            name=f"{name} Attack",
            description=f"A basic attack from {name}",
            move_type=MoveType.FORCE,
            domains=[Domain.BODY],
            base_damage=base_damage,
            stamina_cost=max(1, base_damage // 3),
            focus_cost=0,
            spirit_cost=0
        )
        moves.append(default_move)
    
    return monster, moves


# ======================================================================
# Player Creation
# ======================================================================

def create_player(name: str = "Hero") -> Tuple[Combatant, List[CombatMove]]:
    """Create a player character with basic stats and moves"""
    # Create balanced domain values
    domains = {domain: 2 for domain in Domain}  # Start with all domains at 2
    
    # Let's specialize a bit in a few domains
    domains[Domain.BODY] = 4       # Good at physical combat
    domains[Domain.AWARENESS] = 3  # Decent perception
    domains[Domain.MIND] = 3       # Decent intelligence
    
    # Create the player combatant
    player = Combatant(
        name=name,
        domains=domains,
        max_health=50,
        current_health=50,
        max_stamina=30,
        current_stamina=30,
        max_focus=25,
        current_focus=25,
        max_spirit=20,
        current_spirit=20
    )
    
    # Create basic combat moves
    moves = [
        CombatMove(
            name="Sword Strike",
            description="A basic attack with your sword",
            move_type=MoveType.FORCE,
            domains=[Domain.BODY],
            base_damage=5,
            stamina_cost=2,
            focus_cost=0,
            spirit_cost=0
        ),
        CombatMove(
            name="Precise Thrust",
            description="A carefully aimed stab seeking a weak point",
            move_type=MoveType.FOCUS,
            domains=[Domain.BODY, Domain.AWARENESS],
            base_damage=4,
            stamina_cost=1,
            focus_cost=2,
            spirit_cost=0
        ),
        CombatMove(
            name="Feint",
            description="A deceptive move to catch your opponent off-guard",
            move_type=MoveType.TRICK,
            domains=[Domain.MIND, Domain.BODY],
            base_damage=3,
            stamina_cost=1,
            focus_cost=1,
            spirit_cost=1
        ),
        CombatMove(
            name="Defensive Stance",
            description="Adopt a defensive posture to ward off attacks",
            move_type=MoveType.DEFEND,
            domains=[Domain.BODY],
            base_damage=1,
            stamina_cost=1,
            focus_cost=1,
            spirit_cost=0
        ),
        CombatMove(
            name="Battle Meditation",
            description="A quick focusing technique to recover your spirit and focus",
            move_type=MoveType.UTILITY,
            domains=[Domain.MIND, Domain.SPIRIT],
            base_damage=0,
            stamina_cost=0,
            focus_cost=0,
            spirit_cost=1,
            effects=["Recover 5 focus and 5 spirit"]
        )
    ]
    
    return player, moves


# ======================================================================
# Combat Simulation
# ======================================================================

def simulate_player_combat():
    """Simulate combat between a player and a monster"""
    print("\n" + "=" * 60)
    print("Welcome to the Crimson Accord Combat Demo!")
    print("=" * 60)
    
    # Create the player with a default name (no input required)
    player_name = "Hero"
    print(f"\nCreating character: {player_name}")
    
    player, player_moves = create_player(player_name)
    
    # Load a random monster
    monster_yaml_files = [
        "data/monsters/crimson_accord_monsters_verdant.yaml",
        "data/monsters/crimson_accord_monsters_ember.yaml"
    ]
    
    yaml_file = random.choice(monster_yaml_files)
    region = "Verdant Forest" if "verdant" in yaml_file else "Ember Plains"
    
    # Randomly determine monster tier
    tier_choice = random.randint(1, 100)
    if tier_choice <= 15:  # 15% chance
        tier = ThreatTier.ELITE
        print(f"\nYou've encountered an elite monster in the {region}!")
    elif tier_choice <= 2:  # 2% chance
        tier = ThreatTier.BOSS
        print(f"\nA boss monster approaches in the {region}! This will be a tough fight!")
    else:  # 83% chance
        tier = ThreatTier.STANDARD
        print(f"\nYou've encountered a monster in the {region}.")
    
    monster, monster_moves = load_monster_from_yaml(yaml_file, tier=tier)
    
    if not monster:
        print("Failed to load a monster. Exiting.")
        return
    
    print(f"\nA {monster.name} appears before you!")
    print(f"{monster.description}" if hasattr(monster, 'description') else "It looks dangerous!")
    
    # Create combat controller
    controller = CombatController(environment_name=region)
    
    # Combat loop
    round_number = 1
    
    while True:
        print("\n" + "-" * 60)
        print(f"ROUND {round_number}")
        print("-" * 60)
        
        # Display health bars
        print(f"{player.name}: Health {player.current_health}/{player.max_health} | "
              f"Stamina {player.current_stamina}/{player.max_stamina} | "
              f"Focus {player.current_focus}/{player.max_focus} | "
              f"Spirit {player.current_spirit}/{player.max_spirit}")
        
        print(f"{monster.name}: Health {monster.current_health}/{monster.max_health}")
        
        # Player chooses a move
        print("\nChoose your move:")
        for i, move in enumerate(player_moves, 1):
            cost_str = []
            if move.stamina_cost > 0:
                cost_str.append(f"{move.stamina_cost} stamina")
            if move.focus_cost > 0:
                cost_str.append(f"{move.focus_cost} focus")
            if move.spirit_cost > 0:
                cost_str.append(f"{move.spirit_cost} spirit")
            
            costs = ", ".join(cost_str)
            costs = f" ({costs})" if costs else ""
            
            can_use = move.can_be_used(player)
            available = "" if can_use else " (NOT ENOUGH RESOURCES)"
            
            print(f"{i}. {move.name} - {move.description}{costs}{available}")
        
        # Automatically select first available move
        choice = 0
        for i, move in enumerate(player_moves, 1):
            if move.can_be_used(player):
                choice = i
                print(f"\nAutomatically selected move: {choice}. {move.name}")
                break
                
        if choice == 0:
            print("No moves available! You're exhausted.")
            choice = 1  # Default to first move even if can't use
        
        player_move = player_moves[choice-1]
        
        # Monster randomly chooses a move
        valid_monster_moves = [move for move in monster_moves if move.can_be_used(monster)]
        if not valid_monster_moves:
            print(f"{monster.name} is too exhausted to continue fighting!")
            break
        
        monster_move = random.choice(valid_monster_moves)
        
        # Resolve the combat
        print(f"\n{player.name} uses {player_move.name}!")
        print(f"{monster.name} responds with {monster_move.name}!")
        
        result = controller.resolve_combat_exchange(
            actor=player,
            actor_move=player_move,
            target=monster,
            target_move=monster_move
        )
        
        if not result.get("success", False):
            continue
        
        # Display the narrative
        print(f"\n{result['narrative']}")
        
        # Check for victory/defeat
        if monster.is_defeated():
            print(f"\nVictory! You have defeated the {monster.name}!")
            break
        
        if player.is_defeated():
            print(f"\nDefeat! The {monster.name} has bested you in combat.")
            break
        
        # Recover some resources each round
        player.recover_resources(stamina=2, focus=1, spirit=1)
        monster.recover_resources(stamina=2, focus=1, spirit=1)
        
        # Special recovery from Battle Meditation
        if player_move.name == "Battle Meditation":
            player.recover_resources(focus=5, spirit=5)
            print(f"{player.name} recovers focus and spirit through meditation.")
        
        round_number += 1
        
        # Offer the option to flee after round 3
        if round_number > 3 and not monster.is_defeated() and not player.is_defeated():
            flee = input("\nDo you want to attempt to flee? (y/n): ").lower().strip()
            if flee == 'y':
                # 50% chance to successfully flee, modified by Awareness
                flee_roll = random.randint(1, 20) + player.domains[Domain.AWARENESS]
                if flee_roll >= 15:
                    print(f"You successfully escape from the {monster.name}!")
                    break
                else:
                    print(f"You fail to escape! The {monster.name} blocks your path!")
                    # The monster gets a free attack
                    monster_attack = next((m for m in monster_moves if m.move_type == MoveType.FORCE), random.choice(monster_moves))
                    damage = int(monster_attack.base_damage * controller._get_domain_bonus(monster, monster_attack))
                    player.take_damage(damage)
                    print(f"The {monster.name} catches you as you try to flee and deals {damage} damage with {monster_attack.name}!")
                    
                    if player.is_defeated():
                        print(f"\nDefeat! The {monster.name} has struck you down as you tried to flee.")
                        break
    
    print("\nCombat has ended.")
    print("\nThank you for playing the Crimson Accord Combat Demo!")


if __name__ == "__main__":
    simulate_player_combat()