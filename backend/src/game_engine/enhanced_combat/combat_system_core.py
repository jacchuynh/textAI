"""
Enhanced combat system core for domain-driven RPG.

This module implements the core mechanics for the enhanced combat system,
which is built on top of our domain system.
"""
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple, Set, Any
import random
import uuid
from dataclasses import dataclass
from collections import defaultdict

from ...shared.models import Character, Domain as CharacterDomain, DomainType, Tag

# Core Enumerations
class Domain(Enum):
    """Domain enum mapping to our character domain system"""
    BODY = "Body"  # Maps to DomainType.BODY
    MIND = "Mind"  # Maps to DomainType.MIND
    CRAFT = "Craft"  # Maps to DomainType.CRAFT
    AWARENESS = "Awareness"  # Maps to DomainType.AWARENESS
    SOCIAL = "Social"  # Maps to DomainType.SOCIAL
    AUTHORITY = "Authority"  # Maps to DomainType.AUTHORITY
    SPIRIT = "Spirit"  # Maps to DomainType.SPIRIT

    @staticmethod
    def from_domain_type(domain_type: DomainType) -> 'Domain':
        """Convert character DomainType to combat Domain"""
        mapping = {
            DomainType.BODY: Domain.BODY,
            DomainType.MIND: Domain.MIND,
            DomainType.CRAFT: Domain.CRAFT,
            DomainType.AWARENESS: Domain.AWARENESS,
            DomainType.SOCIAL: Domain.SOCIAL,
            DomainType.AUTHORITY: Domain.AUTHORITY,
            DomainType.SPIRIT: Domain.SPIRIT
        }
        return mapping.get(domain_type)
    
    @staticmethod
    def to_domain_type(domain: 'Domain') -> DomainType:
        """Convert combat Domain to character DomainType"""
        mapping = {
            Domain.BODY: DomainType.BODY,
            Domain.MIND: DomainType.MIND,
            Domain.CRAFT: DomainType.CRAFT,
            Domain.AWARENESS: DomainType.AWARENESS,
            Domain.SOCIAL: DomainType.SOCIAL,
            Domain.AUTHORITY: DomainType.AUTHORITY,
            Domain.SPIRIT: DomainType.SPIRIT
        }
        return mapping.get(domain)


class MoveType(Enum):
    """Types of combat moves in the enhanced system"""
    FORCE = "Force"     # Direct attacks, overwhelming power - beats TRICK
    TRICK = "Trick"     # Deception, evasion, misdirection - beats FOCUS
    FOCUS = "Focus"     # Analysis, blocking, prediction - beats FORCE
    BUFF = "Buff"       # Enhance abilities or stats
    DEBUFF = "Debuff"   # Weaken opponent abilities or stats
    UTILITY = "Utility" # Environmental interaction, movement, etc.


class CombatantType(Enum):
    """Types of combatants in the system"""
    PLAYER = "Player"
    NPC = "NPC"
    ENEMY = "Enemy"
    ALLY = "Ally"
    OBJECT = "Object"  # For doors, traps, etc.


class Status(Enum):
    """Status effects that can be applied to combatants"""
    WOUNDED = "Wounded"     # Physical damage affecting Body
    CONFUSED = "Confused"   # Mental state affecting Mind
    STUNNED = "Stunned"     # Temporary inability to act
    FRIGHTENED = "Frightened"  # Fear affecting decision-making
    INSPIRED = "Inspired"   # Enhanced performance
    POISONED = "Poisoned"   # Ongoing damage over time
    BLEEDING = "Bleeding"   # Ongoing damage over time
    EXHAUSTED = "Exhausted" # Reduced stamina regeneration


@dataclass
class Consequence:
    """Represents a long-term effect resulting from combat"""
    description: str
    affected_domains: List[Domain]
    duration: int  # In encounters/scenes
    intensity: int  # 1-5 scale
    narrative_hook: str
    affected_stats: Dict[str, int] = None  # Stat modifiers


class CombatMove:
    """A move that can be performed in combat"""
    def __init__(self, 
                 name: str,
                 move_type: MoveType,
                 domains: List[Domain],
                 description: str,
                 stamina_cost: int = 0,
                 focus_cost: int = 0,
                 spirit_cost: int = 0):
        """
        Initialize a combat move.
        
        Args:
            name: The name of the move
            move_type: The type of move (FORCE, TRICK, FOCUS, etc)
            domains: The domains this move uses
            description: Description of the move
            stamina_cost: Stamina cost to use the move
            focus_cost: Focus cost to use the move
            spirit_cost: Spirit cost to use the move
        """
        self.name = name
        self.move_type = move_type
        self.domains = domains
        self.description = description
        self.stamina_cost = stamina_cost
        self.focus_cost = focus_cost
        self.spirit_cost = spirit_cost
        self.target = None
        self.is_desperate = False
        self.is_calculated = False
        self.narrative_hook = None
    
    def set_target(self, target: 'Combatant'):
        """Set the target for this move"""
        self.target = target
        return self
    
    def as_desperate(self):
        """Mark move as desperate - higher risk, higher reward"""
        self.is_desperate = True
        return self
    
    def as_calculated(self):
        """Mark move as carefully planned - more likely to succeed but less impact"""
        self.is_calculated = True
        return self
    
    def with_narrative_hook(self, hook: str):
        """Add specific narrative element to influence AI description"""
        self.narrative_hook = hook
        return self
        
    def __str__(self):
        """String representation of this move"""
        domains_str = ", ".join([d.value for d in self.domains])
        return f"{self.name} ({self.move_type.value}): {domains_str}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for API responses"""
        return {
            "name": self.name,
            "move_type": self.move_type.value,
            "domains": [d.value for d in self.domains],
            "description": self.description,
            "stamina_cost": self.stamina_cost,
            "focus_cost": self.focus_cost,
            "spirit_cost": self.spirit_cost,
            "is_desperate": self.is_desperate,
            "is_calculated": self.is_calculated,
            "narrative_hook": self.narrative_hook
        }


class Combatant:
    """Base class for all combatants in the system"""
    def __init__(self, 
                 name: str, 
                 combatant_type: CombatantType,
                 domain_ratings: Dict[Domain, int],
                 max_health: int = 100,
                 max_stamina: int = 100,
                 max_focus: int = 100,
                 max_spirit: int = 100):
        """
        Initialize a combatant.
        
        Args:
            name: The name of the combatant
            combatant_type: The type of combatant
            domain_ratings: Dictionary mapping domains to their ratings
            max_health: Maximum health
            max_stamina: Maximum stamina
            max_focus: Maximum focus
            max_spirit: Maximum spirit
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.combatant_type = combatant_type
        self.domain_ratings = domain_ratings
        
        # Core stats
        self.max_health = max_health
        self.current_health = max_health
        self.max_stamina = max_stamina  
        self.current_stamina = max_stamina
        self.max_focus = max_focus
        self.current_focus = max_focus
        self.max_spirit = max_spirit
        self.current_spirit = max_spirit
        
        # Combat state
        self.statuses: Set[Status] = set()  # Set of Status enums
        self.consequences: List[Consequence] = []  # List of Consequence objects
        
        # Known moves
        self.available_moves: List[CombatMove] = []  # List of CombatMove objects
        
        # Memory/History
        self.combat_memory = []  # List of past interactions
        self.weak_domains: List[Domain] = []  # Domains this combatant is weak against
        self.strong_domains: List[Domain] = []  # Domains this combatant is strong with
    
    def add_move(self, move: CombatMove):
        """Add a move to this combatant's available moves"""
        self.available_moves.append(move)
    
    def apply_damage(self, amount: int, domains: List[Domain] = None) -> Dict[str, Any]:
        """
        Apply damage to health with optional domain context.
        
        Args:
            amount: Amount of damage to apply
            domains: Optional list of domains that caused the damage
            
        Returns:
            Dictionary with results of damage application
        """
        self.current_health = max(0, self.current_health - amount)
        
        # Domain-specific processing could go here
        wounded = False
        if self.current_health < self.max_health * 0.5 and Status.WOUNDED not in self.statuses:
            self.statuses.add(Status.WOUNDED)
            wounded = True
            
        return {
            "damage_dealt": amount,
            "current_health": self.current_health,
            "wounded": wounded
        }
    
    def apply_status(self, status: Status, duration: int = 3) -> Dict[str, Any]:
        """
        Apply a status effect.
        
        Args:
            status: The status to apply
            duration: How long the status lasts
            
        Returns:
            Dictionary with results of status application
        """
        self.statuses.add(status)
        
        # Status-specific logic could go here
        # For example, CONFUSED might reduce Mind domain effectiveness
        
        return {
            "status_applied": status.value,
            "duration": duration
        }
    
    def get_domain_rating(self, domain: Domain) -> int:
        """
        Get effective domain rating accounting for statuses.
        
        Args:
            domain: The domain to get rating for
            
        Returns:
            The effective domain rating
        """
        base_rating = self.domain_ratings.get(domain, 0)
        
        # Apply modifiers from statuses
        if Status.WOUNDED in self.statuses and domain == Domain.BODY:
            base_rating -= 1
        if Status.CONFUSED in self.statuses and domain == Domain.MIND:
            base_rating -= 1
        # Add more status effects as needed
        
        return max(0, base_rating)  # Can't go below 0
    
    def can_use_move(self, move: CombatMove) -> bool:
        """
        Check if combatant has resources to use this move.
        
        Args:
            move: The move to check
            
        Returns:
            True if the move can be used, False otherwise
        """
        if move.stamina_cost > self.current_stamina:
            return False
        if move.focus_cost > self.current_focus:
            return False
        if move.spirit_cost > self.current_spirit:
            return False
        return True
    
    def pay_move_costs(self, move: CombatMove):
        """
        Pay the costs to use a move.
        
        Args:
            move: The move to pay costs for
        """
        self.current_stamina -= move.stamina_cost
        self.current_focus -= move.focus_cost
        self.current_spirit -= move.spirit_cost
        
    def is_defeated(self) -> bool:
        """
        Check if combatant is defeated.
        
        Returns:
            True if the combatant is defeated, False otherwise
        """
        return self.current_health <= 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation for API responses.
        
        Returns:
            Dictionary representation of this combatant
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.combatant_type.value,
            "domain_ratings": {d.value: v for d, v in self.domain_ratings.items()},
            "health": {
                "current": self.current_health,
                "max": self.max_health
            },
            "stamina": {
                "current": self.current_stamina,
                "max": self.max_stamina
            },
            "focus": {
                "current": self.current_focus,
                "max": self.max_focus
            },
            "spirit": {
                "current": self.current_spirit,
                "max": self.max_spirit
            },
            "statuses": [s.value for s in self.statuses],
            "available_moves": [m.to_dict() for m in self.available_moves],
            "strong_domains": [d.value for d in self.strong_domains],
            "weak_domains": [d.value for d in self.weak_domains]
        }


class CombatSystem:
    """Core system for resolving combat actions"""
    def __init__(self):
        """Initialize the combat system"""
        self.combat_log = []  # List of combat events for memory
        self.momentum = defaultdict(int)  # Track momentum per combatant
        self.environment_tags = set()  # Current environment properties
        self.round_counter = 0
        self.active_combats = {}  # Track ongoing combats
    
    def _calculate_type_advantage(self, attacker_type: MoveType, defender_type: MoveType) -> int:
        """
        Calculate type advantage between moves.
        
        Args:
            attacker_type: Move type of the attacker
            defender_type: Move type of the defender
            
        Returns:
            1 if attacker has advantage, -1 if defender has advantage, 0 if neutral
        """
        # Rock-paper-scissors system:
        # FORCE beats TRICK
        # TRICK beats FOCUS
        # FOCUS beats FORCE
        
        if attacker_type == MoveType.FORCE and defender_type == MoveType.TRICK:
            return 1
        elif attacker_type == MoveType.TRICK and defender_type == MoveType.FOCUS:
            return 1
        elif attacker_type == MoveType.FOCUS and defender_type == MoveType.FORCE:
            return 1
        elif attacker_type == defender_type:
            return 0
        else:
            return -1
    
    def _calculate_move_roll(self, combatant: Combatant, move: CombatMove) -> int:
        """
        Calculate the base roll for a move.
        
        Args:
            combatant: The combatant performing the move
            move: The move being performed
            
        Returns:
            The roll result
        """
        # Base roll is d20
        roll = random.randint(1, 20)
        
        # Add domain bonuses
        domain_bonus = 0
        for domain in move.domains:
            domain_bonus += combatant.get_domain_rating(domain)
            
        # Scale domain bonus for balance (average it)
        if move.domains:
            domain_bonus = domain_bonus // len(move.domains)
            
        return roll + domain_bonus
    
    def resolve_opposed_moves(self, 
                              actor: Combatant, 
                              actor_move: CombatMove,
                              target: Combatant, 
                              target_move: CombatMove) -> Dict[str, Any]:
        """
        Resolve two opposed moves against each other.
        
        Args:
            actor: The acting combatant
            actor_move: The actor's move
            target: The target combatant
            target_move: The target's move
            
        Returns:
            Dictionary with results of the resolution
        """
        # Check if actors can use their moves
        if not actor.can_use_move(actor_move):
            return {"success": False, "reason": f"{actor.name} lacks resources for {actor_move.name}"}
        
        if not target.can_use_move(target_move):
            return {"success": False, "reason": f"{target.name} lacks resources for {target_move.name}"}
        
        # Pay costs
        actor.pay_move_costs(actor_move)
        target.pay_move_costs(target_move)
        
        # Type advantage (rock-paper-scissors)
        type_advantage = self._calculate_type_advantage(actor_move.move_type, target_move.move_type)
        
        # Calculate base rolls (domain + d20)
        actor_roll = self._calculate_move_roll(actor, actor_move)
        target_roll = self._calculate_move_roll(target, target_move)
        
        # Apply type advantage
        if type_advantage > 0:  # Actor has advantage
            actor_roll += 2
        elif type_advantage < 0:  # Target has advantage
            target_roll += 2
        
        # Apply momentum
        actor_roll += self.momentum[actor.id]
        target_roll += self.momentum[target.id]
        
        # Apply desperate/calculated modifiers
        if actor_move.is_desperate:
            actor_roll += random.randint(-3, 5)  # High variance
        if actor_move.is_calculated:
            actor_roll = max(actor_roll, actor_roll - 1 + random.randint(0, 2))  # More consistent
            
        # Apply target modifiers
        if target_move.is_desperate:
            target_roll += random.randint(-3, 5)
        if target_move.is_calculated:
            target_roll = max(target_roll, target_roll - 1 + random.randint(0, 2))
        
        # Determine winner
        actor_success = actor_roll > target_roll
        
        # Update momentum - winner gains, loser loses
        if actor_success:
            self.momentum[actor.id] = min(3, self.momentum[actor.id] + 1)
            self.momentum[target.id] = max(0, self.momentum[target.id] - 1)
        else:
            self.momentum[target.id] = min(3, self.momentum[target.id] + 1)
            self.momentum[actor.id] = max(0, self.momentum[actor.id] - 1)
        
        # Calculate effect magnitude based on difference in rolls
        effect_magnitude = abs(actor_roll - target_roll)
        
        # Process damage or effects
        result = {
            "actor": actor.name,
            "actor_id": actor.id,
            "target": target.name,
            "target_id": target.id,
            "actor_move": actor_move.name,
            "target_move": target_move.name,
            "actor_roll": actor_roll,
            "target_roll": target_roll,
            "actor_success": actor_success,
            "effect_magnitude": effect_magnitude,
            "type_advantage": type_advantage,
            "actor_momentum": self.momentum[actor.id],
            "target_momentum": self.momentum[target.id],
            "narrative_hooks": []
        }
        
        # Apply effects based on move type and success
        if actor_success:
            # Actor's move succeeds
            damage = effect_magnitude * 3
            
            # Add domain bonuses to damage
            for domain in actor_move.domains:
                if domain == Domain.BODY:
                    damage += actor.get_domain_rating(domain) * 2
                elif domain == Domain.MIND or domain == Domain.CRAFT:
                    damage += actor.get_domain_rating(domain)
            
            # Apply damage to target
            damage_result = target.apply_damage(damage, actor_move.domains)
            result.update({
                "damage_dealt": damage_result["damage_dealt"],
                "target_health": damage_result["current_health"]
            })
            
            if damage_result.get("wounded", False):
                result["status_applied"] = "Wounded"
                result["narrative_hooks"].append(f"{target.name} is now wounded")
                
            # Check for defeat
            if target.is_defeated():
                result["target_defeated"] = True
                result["narrative_hooks"].append(f"{target.name} is defeated")
        else:
            # Target's counter succeeds
            counterdamage = effect_magnitude
            
            # Apply counterdamage if it's an attacking move type
            if target_move.move_type in [MoveType.FORCE, MoveType.TRICK]:
                damage_result = actor.apply_damage(counterdamage, target_move.domains)
                result.update({
                    "counter_damage": damage_result["damage_dealt"],
                    "actor_health": damage_result["current_health"]
                })
                
                if damage_result.get("wounded", False):
                    result["status_applied"] = "Wounded"
                    result["narrative_hooks"].append(f"{actor.name} is now wounded")
                
                # Check for defeat
                if actor.is_defeated():
                    result["actor_defeated"] = True
                    result["narrative_hooks"].append(f"{actor.name} is defeated")
        
        # Add narrative hooks based on move properties
        if actor_move.narrative_hook:
            result["narrative_hooks"].append(actor_move.narrative_hook)
        if target_move.narrative_hook:
            result["narrative_hooks"].append(target_move.narrative_hook)
            
        # Update the combat log
        self.combat_log.append(result)
        
        return result

    @staticmethod
    def create_combatant_from_character(character: Character) -> Combatant:
        """
        Create a Combatant from a Character.
        
        Args:
            character: The character to convert
            
        Returns:
            A combatant based on the character
        """
        # Convert domain ratings
        domain_ratings = {}
        for domain_type, domain in character.domains.items():
            combat_domain = Domain.from_domain_type(domain_type)
            if combat_domain:
                domain_ratings[combat_domain] = domain.value
        
        # Create the combatant
        combatant = Combatant(
            name=character.name,
            combatant_type=CombatantType.PLAYER,
            domain_ratings=domain_ratings,
            max_health=character.max_health,
            current_health=character.current_health,
            max_stamina=100,  # Default values
            max_focus=100,
            max_spirit=100
        )
        
        # Add moves based on character tags/skills
        if character.tags:
            for tag_name, tag in character.tags.items():
                # Convert tag domains to combat domains
                domains = []
                for domain_type in tag.domains:
                    combat_domain = Domain.from_domain_type(domain_type)
                    if combat_domain:
                        domains.append(combat_domain)
                
                # Create move based on tag properties
                if domains:
                    # Determine move type based on tag category
                    move_type = MoveType.FORCE  # Default
                    if tag.category == TagCategory.COMBAT:
                        move_type = MoveType.FORCE
                    elif tag.category == TagCategory.MAGIC:
                        if Domain.MIND in domains:
                            move_type = MoveType.FOCUS
                        else:
                            move_type = MoveType.UTILITY
                    elif tag.category == TagCategory.SOCIAL:
                        move_type = MoveType.TRICK
                    
                    # Create and add the move
                    move = CombatMove(
                        name=f"{tag_name}",
                        move_type=move_type,
                        domains=domains,
                        description=tag.description or f"Use {tag_name} skill",
                        stamina_cost=2,
                        focus_cost=1 if Domain.MIND in domains else 0,
                        spirit_cost=1 if Domain.SPIRIT in domains else 0
                    )
                    combatant.add_move(move)
        
        # Add some default moves
        combatant.add_move(CombatMove(
            name="Basic Attack",
            move_type=MoveType.FORCE,
            domains=[Domain.BODY],
            description="A basic physical attack",
            stamina_cost=1
        ))
        
        combatant.add_move(CombatMove(
            name="Defend",
            move_type=MoveType.FOCUS,
            domains=[Domain.BODY, Domain.AWARENESS],
            description="Take a defensive stance",
            stamina_cost=1
        ))
        
        combatant.add_move(CombatMove(
            name="Feint",
            move_type=MoveType.TRICK,
            domains=[Domain.AWARENESS, Domain.SOCIAL],
            description="Attempt to trick your opponent",
            stamina_cost=1,
            focus_cost=1
        ))
        
        return combatant

    def create_enemy(self, 
                    name: str, 
                    level: int, 
                    enemy_type: str,
                    domain_focus: List[Domain] = None) -> Combatant:
        """
        Create an enemy combatant.
        
        Args:
            name: Name of the enemy
            level: Level of the enemy
            enemy_type: Type of enemy
            domain_focus: List of domains this enemy specializes in
            
        Returns:
            An enemy combatant
        """
        # Set default domains if none provided
        if not domain_focus:
            domain_focus = [Domain.BODY, Domain.AWARENESS]
        
        # Create basic domain ratings
        domain_ratings = {domain: 0 for domain in Domain}
        
        # Set base stats based on level
        base_rating = max(1, level // 2)
        
        # Enhance focus domains
        for domain in domain_focus:
            domain_ratings[domain] = base_rating + 1
        
        # Enhance remaining domains with lower values
        for domain in Domain:
            if domain not in domain_focus:
                domain_ratings[domain] = max(0, base_rating - 1)
        
        # Scale health and other stats with level
        health = 50 + (level * 10)
        
        # Create the enemy
        enemy = Combatant(
            name=name,
            combatant_type=CombatantType.ENEMY,
            domain_ratings=domain_ratings,
            max_health=health,
            max_stamina=50 + (level * 5),
            max_focus=30 + (level * 5),
            max_spirit=30 + (level * 5)
        )
        
        # Add moves based on enemy type and domains
        if Domain.BODY in domain_focus:
            enemy.add_move(CombatMove(
                name="Powerful Strike",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                description="A powerful physical attack",
                stamina_cost=2
            ))
        
        if Domain.MIND in domain_focus:
            enemy.add_move(CombatMove(
                name="Calculated Strike",
                move_type=MoveType.FOCUS,
                domains=[Domain.MIND, Domain.BODY],
                description="A precisely calculated attack",
                stamina_cost=1,
                focus_cost=2
            ))
        
        if Domain.CRAFT in domain_focus:
            enemy.add_move(CombatMove(
                name="Weapon Technique",
                move_type=MoveType.FORCE,
                domains=[Domain.CRAFT, Domain.BODY],
                description="A skillful weapon technique",
                stamina_cost=2
            ))
            
        if Domain.AWARENESS in domain_focus:
            enemy.add_move(CombatMove(
                name="Counter Strike",
                move_type=MoveType.FOCUS,
                domains=[Domain.AWARENESS, Domain.BODY],
                description="A precisely timed counter attack",
                stamina_cost=1,
                focus_cost=1
            ))
            
        if Domain.SOCIAL in domain_focus:
            enemy.add_move(CombatMove(
                name="Taunt",
                move_type=MoveType.TRICK,
                domains=[Domain.SOCIAL],
                description="A distracting taunt",
                stamina_cost=1
            ))
            
        if Domain.AUTHORITY in domain_focus:
            enemy.add_move(CombatMove(
                name="Commanding Presence",
                move_type=MoveType.DEBUFF,
                domains=[Domain.AUTHORITY, Domain.SOCIAL],
                description="An intimidating display of authority",
                stamina_cost=1,
                spirit_cost=1
            ))
            
        if Domain.SPIRIT in domain_focus:
            enemy.add_move(CombatMove(
                name="Spirit Blast",
                move_type=MoveType.FORCE,
                domains=[Domain.SPIRIT],
                description="A blast of spiritual energy",
                spirit_cost=2
            ))
        
        # Add default moves
        enemy.add_move(CombatMove(
            name="Basic Attack",
            move_type=MoveType.FORCE,
            domains=[Domain.BODY],
            description="A basic attack",
            stamina_cost=1
        ))
        
        enemy.add_move(CombatMove(
            name="Defend",
            move_type=MoveType.FOCUS,
            domains=[Domain.BODY],
            description="A defensive stance",
            stamina_cost=1
        ))
        
        return enemy

    def create_combat(self, 
                     player: Combatant, 
                     enemies: List[Combatant],
                     environment_tags: List[str] = None) -> Dict[str, Any]:
        """
        Create a new combat encounter.
        
        Args:
            player: The player combatant
            enemies: List of enemy combatants
            environment_tags: List of environment tags
            
        Returns:
            Dictionary with combat state
        """
        combat_id = str(uuid.uuid4())
        
        # Initialize combat state
        combat_state = {
            "id": combat_id,
            "round": 1,
            "player": player.to_dict(),
            "enemies": [enemy.to_dict() for enemy in enemies],
            "active_enemy_index": 0,
            "environment_tags": environment_tags or [],
            "status": "active",
            "log": [],
            "current_phase": "player_turn"
        }
        
        # Store in active combats
        self.active_combats[combat_id] = combat_state
        
        # Reset momentum
        self.momentum.clear()
        
        # Set environment tags
        self.environment_tags = set(environment_tags or [])
        
        return combat_state

    def get_combat(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a combat.
        
        Args:
            combat_id: ID of the combat
            
        Returns:
            The combat state, or None if not found
        """
        return self.active_combats.get(combat_id)

    def end_combat(self, combat_id: str) -> bool:
        """
        End a combat encounter.
        
        Args:
            combat_id: ID of the combat
            
        Returns:
            True if the combat was found and ended, False otherwise
        """
        if combat_id in self.active_combats:
            del self.active_combats[combat_id]
            return True
        return False


# Create a global instance for use throughout the system
combat_system = CombatSystem()