"""
Combat system for the game engine.

This module implements a domain-driven, dice-resolved combat system with:
- Choice-based combat flow
- Integration with domain progression
- Environment and status effects
- AI-generated narrative and choices
"""
import random
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

from ..shared.models import Character, DomainType, Tag
from ..events.event_bus import event_bus, GameEvent, EventType
from ..memory.memory_manager import memory_manager, MemoryTier, MemoryType


class CombatPhase(Enum):
    """Phases of combat."""
    INITIALIZATION = "initialization"
    DECISION = "decision"
    ACTION_RESOLUTION = "action_resolution"
    ENEMY_ACTION = "enemy_action"
    ROUND_ADVANCEMENT = "round_advancement"
    COMBAT_END = "combat_end"


class CombatActionType(Enum):
    """Types of combat actions."""
    ATTACK = "attack"
    SPELL = "spell"
    DEFEND = "defend"
    MANEUVER = "maneuver"
    ITEM = "item"
    ESCAPE = "escape"
    SPECIAL = "special"


class CombatStatus(Enum):
    """Status of a combat encounter."""
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"
    NEUTRAL = "neutral"  # For special narrative resolutions


class EnemyTemplate:
    """Template for creating enemy instances."""
    
    def __init__(self, 
                id: int,
                name: str,
                level: int = 1,
                health_base: int = 20,
                health_per_level: int = 5,
                domains: Dict[DomainType, int] = None,
                attacks: List[Dict[str, Any]] = None,
                resistances: List[str] = None,
                weaknesses: List[str] = None,
                description: str = "",
                loot_table: List[Dict[str, Any]] = None,
                tags: List[str] = None):
        """
        Initialize an enemy template.
        
        Args:
            id: Unique identifier for this enemy type
            name: Name of the enemy
            level: Base level of the enemy
            health_base: Base health points
            health_per_level: Additional health per level
            domains: Domain values for the enemy
            attacks: List of attacks available to the enemy
            resistances: List of damage types the enemy resists
            weaknesses: List of damage types the enemy is weak to
            description: Description of the enemy
            loot_table: List of possible loot drops
            tags: List of tags for the enemy
        """
        self.id = id
        self.name = name
        self.level = level
        self.health_base = health_base
        self.health_per_level = health_per_level
        self.domains = domains or {
            DomainType.BODY: 1,
            DomainType.MIND: 1,
            DomainType.SPIRIT: 1,
            DomainType.SOCIAL: 1,
            DomainType.CRAFT: 1,
            DomainType.AUTHORITY: 1,
            DomainType.AWARENESS: 1
        }
        self.attacks = attacks or [
            {
                "name": "Strike",
                "damage": 3,
                "type": "physical",
                "description": "A basic attack"
            }
        ]
        self.resistances = resistances or []
        self.weaknesses = weaknesses or []
        self.description = description or f"A level {level} {name}"
        self.loot_table = loot_table or []
        self.tags = tags or []
    
    def create_instance(self, level_override: Optional[int] = None) -> Dict[str, Any]:
        """
        Create an instance of this enemy for combat.
        
        Args:
            level_override: Optional level override
            
        Returns:
            Enemy instance dictionary
        """
        level = level_override if level_override is not None else self.level
        max_health = self.health_base + (self.health_per_level * (level - 1))
        
        # Scale domain values with level (simplified)
        domains = {}
        for domain, value in self.domains.items():
            domains[domain] = min(10, value + ((level - 1) // 2))
        
        # Create the enemy instance
        return {
            "id": str(uuid.uuid4()),
            "template_id": self.id,
            "name": self.name,
            "level": level,
            "max_health": max_health,
            "current_health": max_health,
            "domains": domains,
            "attacks": self.attacks.copy(),
            "resistances": self.resistances.copy(),
            "weaknesses": self.weaknesses.copy(),
            "description": self.description,
            "tags": self.tags.copy(),
            "status_effects": []
        }


class CombatAction:
    """
    Represents a combat action that can be taken by the player.
    
    This is used to generate structured choices for the player.
    """
    
    def __init__(self,
                label: str,
                action_type: CombatActionType,
                domains: List[DomainType],
                description: str = "",
                cost: int = 0,
                damage: int = 0,
                healing: int = 0,
                effects: List[Dict[str, Any]] = None,
                tags: List[str] = None,
                requires_target: bool = True,
                difficulty_modifier: int = 0):
        """
        Initialize a combat action.
        
        Args:
            label: Display name of the action
            action_type: Type of action
            domains: Domains used for this action
            description: Description of the action
            cost: Mana/stamina/resource cost
            damage: Base damage amount
            healing: Base healing amount
            effects: Additional effects
            tags: Tags for categorization
            requires_target: Whether this action requires a target
            difficulty_modifier: Modifier to the difficulty check
        """
        self.label = label
        self.action_type = action_type
        self.domains = domains
        self.description = description
        self.cost = cost
        self.damage = damage
        self.healing = healing
        self.effects = effects or []
        self.tags = tags or []
        self.requires_target = requires_target
        self.difficulty_modifier = difficulty_modifier
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for frontend."""
        return {
            "label": self.label,
            "action_type": self.action_type.value,
            "domains": [d.value for d in self.domains],
            "description": self.description,
            "cost": self.cost,
            "damage": self.damage,
            "healing": self.healing,
            "effects": self.effects,
            "tags": self.tags,
            "requires_target": self.requires_target,
            "difficulty_modifier": self.difficulty_modifier
        }


class CombatSystem:
    """
    Combat system for handling encounters, choices, and resolution.
    
    This class manages:
    - Creating and updating combat state
    - Generating combat options
    - Resolving actions
    - Managing enemy behavior
    - Tracking combat logs and growth
    """
    
    def __init__(self):
        """Initialize the combat system."""
        # Enemy templates
        self.enemy_templates: Dict[int, EnemyTemplate] = {}
        self._initialize_enemy_templates()
        
        # Active combats
        self.active_combats: Dict[str, Dict[str, Any]] = {}
    
    def _initialize_enemy_templates(self):
        """Initialize built-in enemy templates."""
        # Add some basic enemy templates
        self.enemy_templates[1] = EnemyTemplate(
            id=1,
            name="Wolf",
            level=1,
            health_base=12,
            health_per_level=3,
            domains={
                DomainType.BODY: 2,
                DomainType.MIND: 1,
                DomainType.SPIRIT: 1,
                DomainType.SOCIAL: 0,
                DomainType.CRAFT: 0,
                DomainType.AUTHORITY: 0,
                DomainType.AWARENESS: 3
            },
            attacks=[
                {
                    "name": "Bite",
                    "damage": 4,
                    "type": "physical",
                    "description": "A painful bite attack"
                },
                {
                    "name": "Howl",
                    "damage": 0,
                    "type": "fear",
                    "description": "A frightening howl that can reduce resolve",
                    "effects": [{"type": "intimidate", "difficulty": 12}]
                }
            ],
            description="A lean, hungry wolf with sharp teeth and keen senses.",
            tags=["beast", "wilderness", "pack_animal"]
        )
        
        self.enemy_templates[2] = EnemyTemplate(
            id=2,
            name="Bandit",
            level=2,
            health_base=15,
            health_per_level=4,
            domains={
                DomainType.BODY: 2,
                DomainType.MIND: 1,
                DomainType.SPIRIT: 1,
                DomainType.SOCIAL: 1,
                DomainType.CRAFT: 1,
                DomainType.AUTHORITY: 0,
                DomainType.AWARENESS: 2
            },
            attacks=[
                {
                    "name": "Dagger Strike",
                    "damage": 5,
                    "type": "physical",
                    "description": "A quick stab with a rusty dagger"
                },
                {
                    "name": "Threaten",
                    "damage": 0,
                    "type": "social",
                    "description": "Intimidating threats that can shake resolve",
                    "effects": [{"type": "intimidate", "difficulty": 13}]
                }
            ],
            description="A rough-looking bandit with worn leather armor and a menacing glare.",
            loot_table=[
                {"item": "Coin Pouch", "chance": 0.7},
                {"item": "Rusty Dagger", "chance": 0.3}
            ],
            tags=["humanoid", "criminal", "group"]
        )
        
        self.enemy_templates[3] = EnemyTemplate(
            id=3,
            name="Arcane Construct",
            level=3,
            health_base=25,
            health_per_level=6,
            domains={
                DomainType.BODY: 3,
                DomainType.MIND: 0,
                DomainType.SPIRIT: 2,
                DomainType.SOCIAL: 0,
                DomainType.CRAFT: 0,
                DomainType.AUTHORITY: 0,
                DomainType.AWARENESS: 1
            },
            attacks=[
                {
                    "name": "Arcane Blast",
                    "damage": 6,
                    "type": "magical",
                    "description": "A burst of raw magical energy"
                }
            ],
            resistances=["physical", "poison"],
            weaknesses=["spirit", "anti-magic"],
            description="A floating construct of arcane energy bound to a crystalline core.",
            loot_table=[
                {"item": "Mana Crystal", "chance": 0.5},
                {"item": "Arcane Dust", "chance": 0.9}
            ],
            tags=["construct", "magical", "elemental"]
        )
    
    def get_enemy_template(self, template_id: int) -> Optional[EnemyTemplate]:
        """Get an enemy template by ID."""
        return self.enemy_templates.get(template_id)
    
    def register_enemy_template(self, template: EnemyTemplate) -> int:
        """
        Register a custom enemy template.
        
        Args:
            template: The enemy template to register
            
        Returns:
            The template ID
        """
        # Generate a new ID if not provided
        if template.id in self.enemy_templates:
            # Find the next available ID
            next_id = max(self.enemy_templates.keys()) + 1
            template.id = next_id
        
        self.enemy_templates[template.id] = template
        return template.id
    
    def start_combat(self, 
                    character: Character, 
                    enemy_template_id: int, 
                    level_override: Optional[int] = None,
                    location_name: str = "Unknown",
                    environment_factors: List[str] = None,
                    surprise: bool = False,
                    game_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new combat encounter.
        
        Args:
            character: The player character
            enemy_template_id: ID of the enemy template
            level_override: Optional level override for the enemy
            location_name: Name of the combat location
            environment_factors: List of environmental effects
            surprise: Whether this is a surprise attack
            game_id: Optional game ID for event tracking
            
        Returns:
            New combat state
        """
        # Get the enemy template
        template = self.get_enemy_template(enemy_template_id)
        if not template:
            raise ValueError(f"Enemy template with ID {enemy_template_id} not found")
        
        # Create enemy instance
        enemy = template.create_instance(level_override)
        
        # Determine initiative/momentum
        momentum = "enemy" if surprise else "player"
        
        # Create combat state
        combat_id = str(uuid.uuid4())
        combat_state = {
            "id": combat_id,
            "game_id": game_id,
            "location": location_name,
            "round": 1,
            "momentum": momentum,
            "environment": environment_factors or [],
            "enemies": [enemy],
            "player": {
                "id": str(character.id),
                "name": character.name,
                "max_health": character.max_health,
                "current_health": character.current_health,
                "max_mana": getattr(character, "max_mana", 0),
                "current_mana": getattr(character, "current_mana", 0),
                "domains": {d.name: v.value for d, v in character.domains.items()} if character.domains else {},
                "tags": {name: tag.rank for name, tag in character.tags.items()} if character.tags else {},
                "status_effects": []
            },
            "growth_log": [],
            "log": [
                f"Combat started against {enemy['name']} in {location_name}."
            ],
            "phase": CombatPhase.INITIALIZATION.value,
            "status": CombatStatus.ACTIVE.value,
            "available_actions": [],
            "surprise": surprise,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store the active combat
        self.active_combats[combat_id] = combat_state
        
        # Emit combat started event
        if game_id:
            event_bus.publish(GameEvent(
                type=EventType.COMBAT_STARTED,
                actor=str(character.id),
                context={
                    "enemy_id": enemy["template_id"],
                    "enemy_name": enemy["name"],
                    "location": location_name,
                    "surprise": surprise,
                    "combat_id": combat_id
                },
                tags=["combat", "encounter", *enemy["tags"]],
                game_id=game_id
            ))
            
            # Add memory
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=f"Combat began with a {enemy['name']} at {location_name}." + 
                        (" You were caught by surprise!" if surprise else ""),
                importance=6,
                tier=MemoryTier.MEDIUM_TERM,
                tags=["combat", "encounter", *enemy["tags"]],
                game_id=game_id
            )
        
        # Advance to decision phase
        self._advance_to_decision_phase(combat_id, character)
        
        return combat_state
    
    def _advance_to_decision_phase(self, combat_id: str, character: Character) -> None:
        """
        Advance combat to the decision phase and generate options.
        
        Args:
            combat_id: The combat ID
            character: The player character
        """
        if combat_id not in self.active_combats:
            return
            
        combat_state = self.active_combats[combat_id]
        
        # Skip decision phase if combat is not active
        if combat_state["status"] != CombatStatus.ACTIVE.value:
            return
            
        # Set phase to decision
        combat_state["phase"] = CombatPhase.DECISION.value
        
        # Generate available actions
        combat_state["available_actions"] = self._generate_combat_options(character, combat_state)
        
        # Update timestamp
        combat_state["updated_at"] = datetime.utcnow().isoformat()
    
    def _generate_combat_options(self, character: Character, combat_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate combat options based on character state and context.
        
        Args:
            character: The player character
            combat_state: Current combat state
            
        Returns:
            List of combat action dictionaries
        """
        options = []
        
        # Basic attack option
        attack = CombatAction(
            label="Attack",
            action_type=CombatActionType.ATTACK,
            domains=[DomainType.BODY],
            description="Attack with your weapon",
            damage=5,
            tags=["physical", "weapon"],
            requires_target=True
        )
        options.append(attack.to_dict())
        
        # Add defensive option
        defend = CombatAction(
            label="Defend",
            action_type=CombatActionType.DEFEND,
            domains=[DomainType.BODY, DomainType.AWARENESS],
            description="Take a defensive stance to reduce incoming damage",
            effects=[{"type": "defense_bonus", "value": 3, "duration": 1}],
            tags=["defense", "tactical"],
            requires_target=False
        )
        options.append(defend.to_dict())
        
        # Add maneuver option
        maneuver = CombatAction(
            label="Tactical Maneuver",
            action_type=CombatActionType.MANEUVER,
            domains=[DomainType.BODY, DomainType.MIND],
            description="Attempt to gain a tactical advantage",
            effects=[{"type": "advantage", "duration": 1}],
            tags=["positioning", "tactical"],
            requires_target=True
        )
        options.append(maneuver.to_dict())
        
        # Add escape option
        escape = CombatAction(
            label="Attempt Escape",
            action_type=CombatActionType.ESCAPE,
            domains=[DomainType.BODY, DomainType.AWARENESS],
            description="Try to flee from combat",
            tags=["escape", "movement"],
            requires_target=False,
            difficulty_modifier=2  # Harder than normal actions
        )
        options.append(escape.to_dict())
        
        # Check if character has spells and add them
        # TODO: Implement spell system integration
        
        # Check if character has special abilities based on tags
        if character.tags:
            for tag_name, tag in character.tags.items():
                # Only include higher-rank tags (2+)
                if tag.rank >= 2:
                    # Example: Add a special attack for weapon-related tags
                    if "weapon" in tag.name.lower() or "combat" in tag.name.lower():
                        special_attack = CombatAction(
                            label=f"Special: {tag_name} Technique",
                            action_type=CombatActionType.SPECIAL,
                            domains=[DomainType.BODY],
                            description=f"Use your {tag_name} skill for a special attack",
                            damage=3 + tag.rank,
                            tags=["physical", "special", "skill", tag_name.lower()],
                            requires_target=True
                        )
                        options.append(special_attack.to_dict())
        
        return options
    
    def process_combat_action(self, 
                             combat_id: str,
                             action_data: Dict[str, Any],
                             character: Character) -> Dict[str, Any]:
        """
        Process a player's combat action.
        
        Args:
            combat_id: The combat ID
            action_data: The action data from the frontend
            character: The player character
            
        Returns:
            Updated combat state
        """
        if combat_id not in self.active_combats:
            raise ValueError(f"Combat with ID {combat_id} not found")
            
        combat_state = self.active_combats[combat_id]
        
        # Ensure combat is active and in decision phase
        if combat_state["status"] != CombatStatus.ACTIVE.value:
            return combat_state
            
        if combat_state["phase"] != CombatPhase.DECISION.value:
            return combat_state
            
        # Extract action details
        action_type = action_data.get("action_type")
        domains = action_data.get("domains", [])
        target_id = action_data.get("target")
        
        # Find target enemy
        target = None
        for enemy in combat_state["enemies"]:
            if enemy["id"] == target_id:
                target = enemy
                break
                
        # If action requires target but none specified, use first enemy
        if not target and action_data.get("requires_target", True) and combat_state["enemies"]:
            target = combat_state["enemies"][0]
        
        # Set phase to action resolution
        combat_state["phase"] = CombatPhase.ACTION_RESOLUTION.value
        
        # Roll for success
        roll_result = self._resolve_action_roll(character, action_data, combat_state, target)
        
        # Add to log
        log_entry = f"Player used {action_data.get('label', 'an action')}. "
        log_entry += f"Roll: {roll_result['roll']} + {roll_result['modifier']} = {roll_result['total']} "
        log_entry += f"vs DC {roll_result['dc']} - "
        log_entry += "Success!" if roll_result["success"] else "Failure!"
        combat_state["log"].append(log_entry)
        
        # Add to growth log
        growth_entry = {
            "domain": domains[0] if domains else None,
            "success": roll_result["success"],
            "roll": roll_result["total"],
            "dc": roll_result["dc"],
            "action": action_data.get("label", "Unknown action")
        }
        combat_state["growth_log"].append(growth_entry)
        
        # Apply effects based on action type and success
        self._apply_action_effects(combat_state, action_data, roll_result, target)
        
        # Check for combat end
        if self._check_combat_end(combat_state):
            return combat_state
            
        # Advance to enemy action phase
        combat_state["phase"] = CombatPhase.ENEMY_ACTION.value
        
        # Process enemy actions
        self._process_enemy_actions(combat_state, character)
        
        # Check for combat end again
        if self._check_combat_end(combat_state):
            return combat_state
            
        # Advance to next round
        combat_state["round"] += 1
        combat_state["phase"] = CombatPhase.ROUND_ADVANCEMENT.value
        
        # Apply round effects (like status durations)
        self._apply_round_effects(combat_state)
        
        # Advance to decision phase for next round
        self._advance_to_decision_phase(combat_id, character)
        
        # Update timestamp
        combat_state["updated_at"] = datetime.utcnow().isoformat()
        
        return combat_state
    
    def _resolve_action_roll(self, 
                            character: Character, 
                            action_data: Dict[str, Any],
                            combat_state: Dict[str, Any],
                            target: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve a dice roll for an action.
        
        Args:
            character: The player character
            action_data: The action data
            combat_state: Current combat state
            target: Optional target enemy
            
        Returns:
            Roll result dictionary
        """
        # Roll d20
        roll = random.randint(1, 20)
        
        # Calculate domain modifier
        domain_modifier = 0
        for domain_str in action_data.get("domains", []):
            try:
                domain = DomainType(domain_str)
                if domain in character.domains:
                    domain_modifier += character.domains[domain].value
            except (ValueError, KeyError):
                # Invalid domain or not present
                pass
        
        # Add tag/skill modifier if applicable
        tag_modifier = 0
        for tag in action_data.get("tags", []):
            if character.tags and tag in character.tags:
                tag_modifier += character.tags[tag].rank
        
        # Calculate total modifier
        modifier = domain_modifier + tag_modifier
        
        # Calculate difficulty
        base_difficulty = 10  # Default difficulty
        
        # Adjust for enemy level if targeting an enemy
        if target:
            base_difficulty += target.get("level", 0)
            
            # Check for target resistances
            for resistance in target.get("resistances", []):
                if resistance in action_data.get("tags", []):
                    base_difficulty += 2
            
            # Check for target weaknesses
            for weakness in target.get("weaknesses", []):
                if weakness in action_data.get("tags", []):
                    base_difficulty -= 2
        
        # Adjust for environmental factors
        for factor in combat_state.get("environment", []):
            # Example adjustments
            if factor == "Darkness" and "light" not in action_data.get("tags", []):
                base_difficulty += 1
            if factor == "Slippery Ground" and action_data.get("action_type") == "maneuver":
                base_difficulty += 1
        
        # Adjust for momentum
        if combat_state.get("momentum") == "player":
            base_difficulty -= 1
        elif combat_state.get("momentum") == "enemy":
            base_difficulty += 1
        
        # Apply action's difficulty modifier
        base_difficulty += action_data.get("difficulty_modifier", 0)
        
        # Ensure difficulty is at least 5
        dc = max(5, base_difficulty)
        
        # Calculate total and success
        total = roll + modifier
        success = total >= dc
        
        # Return result
        return {
            "roll": roll,
            "modifier": modifier,
            "total": total,
            "dc": dc,
            "success": success,
            "critical": roll == 20,
            "fumble": roll == 1,
            "margin": total - dc
        }
    
    def _apply_action_effects(self, 
                             combat_state: Dict[str, Any],
                             action_data: Dict[str, Any],
                             roll_result: Dict[str, Any],
                             target: Optional[Dict[str, Any]]) -> None:
        """
        Apply the effects of an action based on roll results.
        
        Args:
            combat_state: The current combat state
            action_data: The action data
            roll_result: The roll result
            target: The target enemy
        """
        action_type = action_data.get("action_type")
        
        # Handle based on action type
        if action_type == CombatActionType.ATTACK.value or action_type == CombatActionType.SPELL.value:
            if roll_result["success"] and target:
                # Calculate damage
                base_damage = action_data.get("damage", 3)
                
                # Critical hits do double damage
                if roll_result["critical"]:
                    damage = base_damage * 2
                    combat_state["log"].append(f"Critical hit! Double damage ({damage}).")
                else:
                    # Scale damage with margin of success
                    damage = base_damage + (roll_result["margin"] // 3)
                
                # Apply damage to target
                target["current_health"] = max(0, target["current_health"] - damage)
                combat_state["log"].append(f"Dealt {damage} damage to {target['name']}. "
                                          f"Health: {target['current_health']}/{target['max_health']}")
                
                # If target defeated
                if target["current_health"] <= 0:
                    combat_state["log"].append(f"{target['name']} was defeated!")
            else:
                combat_state["log"].append("The attack missed!")
                
        elif action_type == CombatActionType.DEFEND.value:
            if roll_result["success"]:
                # Apply defense bonus
                for effect in action_data.get("effects", []):
                    if effect.get("type") == "defense_bonus":
                        value = effect.get("value", 3)
                        duration = effect.get("duration", 1)
                        
                        # Add status effect to player
                        combat_state["player"]["status_effects"].append({
                            "type": "defense_bonus",
                            "value": value,
                            "duration": duration,
                            "description": f"+{value} to defense for {duration} rounds"
                        })
                        
                        combat_state["log"].append(f"Defense increased by {value} for {duration} rounds.")
            else:
                combat_state["log"].append("Failed to take a proper defensive stance.")
                
        elif action_type == CombatActionType.MANEUVER.value:
            if roll_result["success"]:
                # Apply advantage
                combat_state["momentum"] = "player"
                
                for effect in action_data.get("effects", []):
                    if effect.get("type") == "advantage":
                        duration = effect.get("duration", 1)
                        
                        # Add status effect to player
                        combat_state["player"]["status_effects"].append({
                            "type": "advantage",
                            "duration": duration,
                            "description": f"Tactical advantage for {duration} rounds"
                        })
                        
                        combat_state["log"].append(f"Gained tactical advantage for {duration} rounds.")
            else:
                combat_state["log"].append("The maneuver failed.")
                combat_state["momentum"] = "enemy"
                
        elif action_type == CombatActionType.ESCAPE.value:
            if roll_result["success"]:
                combat_state["status"] = CombatStatus.FLED.value
                combat_state["phase"] = CombatPhase.COMBAT_END.value
                combat_state["log"].append("Successfully escaped from combat!")
                
                # Emit event if game_id exists
                if combat_state.get("game_id"):
                    event_bus.publish(GameEvent(
                        type=EventType.COMBAT_ENDED,
                        actor=str(combat_state["player"]["id"]),
                        context={
                            "result": "fled",
                            "enemy_name": target["name"] if target else "the enemy",
                            "combat_id": combat_state["id"],
                            "rounds": combat_state["round"]
                        },
                        tags=["combat", "escape", "fled"],
                        game_id=combat_state["game_id"]
                    ))
            else:
                combat_state["log"].append("Failed to escape!")
                combat_state["momentum"] = "enemy"
                
        elif action_type == CombatActionType.ITEM.value:
            # Apply item effects
            if roll_result["success"]:
                combat_state["log"].append(f"Successfully used {action_data.get('label', 'item')}.")
                
                # TODO: Implement specific item effect logic
            else:
                combat_state["log"].append(f"Failed to use {action_data.get('label', 'item')} effectively.")
        
        elif action_type == CombatActionType.SPECIAL.value:
            if roll_result["success"] and target:
                # Calculate damage
                base_damage = action_data.get("damage", 5)
                
                # Critical hits do double damage
                if roll_result["critical"]:
                    damage = base_damage * 2
                    combat_state["log"].append(f"Critical hit with special attack! Double damage ({damage}).")
                else:
                    # Scale damage with margin of success
                    damage = base_damage + (roll_result["margin"] // 2)
                
                # Apply damage to target
                target["current_health"] = max(0, target["current_health"] - damage)
                combat_state["log"].append(f"Special attack dealt {damage} damage to {target['name']}. "
                                          f"Health: {target['current_health']}/{target['max_health']}")
                
                # If target defeated
                if target["current_health"] <= 0:
                    combat_state["log"].append(f"{target['name']} was defeated!")
            else:
                combat_state["log"].append("The special attack missed!")
    
    def _process_enemy_actions(self, 
                              combat_state: Dict[str, Any],
                              character: Character) -> None:
        """
        Process actions for all active enemies.
        
        Args:
            combat_state: The current combat state
            character: The player character
        """
        # Skip if combat is over
        if combat_state["status"] != CombatStatus.ACTIVE.value:
            return
            
        # Process each enemy
        for enemy in combat_state["enemies"]:
            if enemy["current_health"] <= 0:
                continue  # Skip defeated enemies
                
            # Choose an attack
            attack = self._choose_enemy_attack(enemy, combat_state)
            
            # Roll for the attack
            enemy_roll = random.randint(1, 20)
            
            # Calculate modifier based on enemy level and domains
            relevant_domain = DomainType.BODY  # Default for physical attacks
            if attack.get("type") == "magical":
                relevant_domain = DomainType.MIND
            elif attack.get("type") == "social":
                relevant_domain = DomainType.SOCIAL
                
            domain_value = enemy["domains"].get(relevant_domain.name, 1)
            
            # Calculate difficulty
            # Base difficulty is 10, modified by character's domains and status effects
            defense_bonus = 0
            for effect in combat_state["player"]["status_effects"]:
                if effect.get("type") == "defense_bonus":
                    defense_bonus += effect.get("value", 0)
                    
            # If character has relevant domain for defense, add half its value
            defense_domain = DomainType.BODY  # Default for physical defense
            if attack.get("type") == "magical":
                defense_domain = DomainType.SPIRIT
            elif attack.get("type") == "social":
                defense_domain = DomainType.SOCIAL
                
            if defense_domain in character.domains:
                defense_bonus += character.domains[defense_domain].value // 2
                
            dc = 10 + defense_bonus
            
            # Calculate total and success
            total = enemy_roll + domain_value
            success = total >= dc
            
            # Log the attack
            log_entry = f"{enemy['name']} used {attack['name']}. "
            log_entry += f"Roll: {enemy_roll} + {domain_value} = {total} vs DC {dc}. "
            
            if success:
                # Calculate damage
                damage = attack.get("damage", 3)
                
                # Critical hit
                if enemy_roll == 20:
                    damage *= 2
                    log_entry += f"Critical hit! {damage} damage."
                else:
                    log_entry += f"Hit! {damage} damage."
                    
                # Apply damage to player
                combat_state["player"]["current_health"] = max(0, combat_state["player"]["current_health"] - damage)
                
                # Check for player defeat
                if combat_state["player"]["current_health"] <= 0:
                    log_entry += " You were defeated!"
                    combat_state["status"] = CombatStatus.DEFEAT.value
                    combat_state["phase"] = CombatPhase.COMBAT_END.value
                else:
                    log_entry += f" Health: {combat_state['player']['current_health']}/{combat_state['player']['max_health']}"
                    
                # Apply any additional effects
                for effect in attack.get("effects", []):
                    # Example: Apply intimidate effect
                    if effect.get("type") == "intimidate":
                        effect_dc = effect.get("difficulty", 10)
                        
                        # Roll for resistance
                        spirit_roll = random.randint(1, 20)
                        spirit_mod = 0
                        if DomainType.SPIRIT in character.domains:
                            spirit_mod = character.domains[DomainType.SPIRIT].value
                            
                        if spirit_roll + spirit_mod < effect_dc:
                            # Apply intimidated status
                            combat_state["player"]["status_effects"].append({
                                "type": "intimidated",
                                "duration": 1,
                                "description": "Intimidated: -1 to all rolls for 1 round"
                            })
                            log_entry += " You are intimidated!"
            else:
                log_entry += "Miss!"
                
            combat_state["log"].append(log_entry)
                
            # Set momentum based on attack result
            if success:
                combat_state["momentum"] = "enemy"
            else:
                combat_state["momentum"] = "player"
    
    def _choose_enemy_attack(self, 
                            enemy: Dict[str, Any],
                            combat_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Choose an attack for an enemy to use.
        
        Args:
            enemy: The enemy data
            combat_state: The current combat state
            
        Returns:
            The chosen attack
        """
        attacks = enemy.get("attacks", [])
        
        if not attacks:
            # Default attack if none defined
            return {
                "name": "Strike",
                "damage": 3,
                "type": "physical",
                "description": "A basic attack"
            }
            
        # Simple logic: usually use basic attacks, occasionally use specials
        if len(attacks) > 1 and random.random() < 0.3:
            # Use a non-primary attack
            return random.choice(attacks[1:])
        else:
            # Use the primary attack
            return attacks[0]
    
    def _check_combat_end(self, combat_state: Dict[str, Any]) -> bool:
        """
        Check if combat has ended (victory, defeat, or escape).
        
        Args:
            combat_state: The current combat state
            
        Returns:
            True if combat has ended, False otherwise
        """
        # Already ended
        if combat_state["status"] != CombatStatus.ACTIVE.value:
            return True
            
        # Check for player defeat
        if combat_state["player"]["current_health"] <= 0:
            combat_state["status"] = CombatStatus.DEFEAT.value
            combat_state["phase"] = CombatPhase.COMBAT_END.value
            combat_state["log"].append("You were defeated!")
            
            # Emit event if game_id exists
            if combat_state.get("game_id"):
                first_enemy = combat_state["enemies"][0] if combat_state["enemies"] else None
                enemy_name = first_enemy["name"] if first_enemy else "the enemy"
                
                event_bus.publish(GameEvent(
                    type=EventType.CHARACTER_DEFEATED,
                    actor=str(combat_state["player"]["id"]),
                    context={
                        "enemy_name": enemy_name,
                        "combat_id": combat_state["id"],
                        "rounds": combat_state["round"]
                    },
                    tags=["combat", "defeat"],
                    game_id=combat_state["game_id"]
                ))
            
            return True
            
        # Check for enemy defeat (all enemies defeated)
        all_defeated = all(enemy["current_health"] <= 0 for enemy in combat_state["enemies"])
        
        if all_defeated:
            combat_state["status"] = CombatStatus.VICTORY.value
            combat_state["phase"] = CombatPhase.COMBAT_END.value
            combat_state["log"].append("Victory! All enemies defeated.")
            
            # Emit event if game_id exists
            if combat_state.get("game_id"):
                first_enemy = combat_state["enemies"][0] if combat_state["enemies"] else None
                enemy_name = first_enemy["name"] if first_enemy else "the enemy"
                
                event_bus.publish(GameEvent(
                    type=EventType.ENEMY_DEFEATED,
                    actor=str(combat_state["player"]["id"]),
                    context={
                        "enemy_name": enemy_name,
                        "combat_id": combat_state["id"],
                        "rounds": combat_state["round"]
                    },
                    tags=["combat", "victory"],
                    game_id=combat_state["game_id"]
                ))
            
            return True
            
        return False
    
    def _apply_round_effects(self, combat_state: Dict[str, Any]) -> None:
        """
        Apply effects that happen at the end of a round.
        
        Args:
            combat_state: The current combat state
        """
        # Process player status effects
        if "status_effects" in combat_state["player"]:
            # Track effects to remove
            effects_to_remove = []
            
            for i, effect in enumerate(combat_state["player"]["status_effects"]):
                # Decrease duration
                if "duration" in effect:
                    effect["duration"] -= 1
                    
                    # Mark for removal if expired
                    if effect["duration"] <= 0:
                        effects_to_remove.append(i)
                        combat_state["log"].append(f"Effect '{effect.get('description', 'Unknown')}' has worn off.")
            
            # Remove expired effects (in reverse order to avoid index issues)
            for i in sorted(effects_to_remove, reverse=True):
                combat_state["player"]["status_effects"].pop(i)
                
        # Process enemy status effects
        for enemy in combat_state["enemies"]:
            if enemy["current_health"] <= 0:
                continue  # Skip defeated enemies
                
            if "status_effects" in enemy:
                # Track effects to remove
                effects_to_remove = []
                
                for i, effect in enumerate(enemy["status_effects"]):
                    # Decrease duration
                    if "duration" in effect:
                        effect["duration"] -= 1
                        
                        # Mark for removal if expired
                        if effect["duration"] <= 0:
                            effects_to_remove.append(i)
                
                # Remove expired effects (in reverse order to avoid index issues)
                for i in sorted(effects_to_remove, reverse=True):
                    enemy["status_effects"].pop(i)
    
    def get_combat_growth_log(self, combat_id: str) -> List[Dict[str, Any]]:
        """
        Get the growth log for a combat.
        
        Args:
            combat_id: The combat ID
            
        Returns:
            The combat growth log
        """
        if combat_id not in self.active_combats:
            return []
            
        return self.active_combats[combat_id].get("growth_log", [])
    
    def get_combat_state(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a combat.
        
        Args:
            combat_id: The combat ID
            
        Returns:
            The combat state or None if not found
        """
        return self.active_combats.get(combat_id)
    
    def update_player_state(self, 
                           combat_id: str,
                           player_data: Dict[str, Any]) -> bool:
        """
        Update the player state in combat (for syncing with character data).
        
        Args:
            combat_id: The combat ID
            player_data: Updated player data
            
        Returns:
            True if updated successfully, False otherwise
        """
        if combat_id not in self.active_combats:
            return False
            
        # Update only allowed fields
        allowed_fields = ["current_health", "max_health", "current_mana", "max_mana", "domains", "tags"]
        
        for field in allowed_fields:
            if field in player_data:
                self.active_combats[combat_id]["player"][field] = player_data[field]
                
        return True
    
    def end_combat(self, combat_id: str, game_id: Optional[str] = None) -> Dict[str, Any]:
        """
        End a combat encounter and clean up.
        
        Args:
            combat_id: The combat ID
            game_id: Optional game ID for event tracking
            
        Returns:
            The final combat state
        """
        if combat_id not in self.active_combats:
            return {}
            
        combat_state = self.active_combats[combat_id]
        
        # Set phase to combat end if not already
        if combat_state["phase"] != CombatPhase.COMBAT_END.value:
            combat_state["phase"] = CombatPhase.COMBAT_END.value
            
            # If status is still active, mark as neutral end (narrative resolution)
            if combat_state["status"] == CombatStatus.ACTIVE.value:
                combat_state["status"] = CombatStatus.NEUTRAL.value
                
        # Emit combat ended event
        if game_id:
            event_bus.publish(GameEvent(
                type=EventType.COMBAT_ENDED,
                actor=str(combat_state["player"]["id"]),
                context={
                    "result": combat_state["status"],
                    "combat_id": combat_id,
                    "rounds": combat_state["round"]
                },
                tags=["combat", "ended", combat_state["status"]],
                game_id=game_id
            ))
            
            # Add memory
            first_enemy = combat_state["enemies"][0] if combat_state["enemies"] else None
            enemy_name = first_enemy["name"] if first_enemy else "the enemy"
            
            # Format based on outcome
            if combat_state["status"] == CombatStatus.VICTORY.value:
                memory_content = f"You defeated {enemy_name} in combat after {combat_state['round']} rounds."
                memory_importance = 7
            elif combat_state["status"] == CombatStatus.DEFEAT.value:
                memory_content = f"You were defeated by {enemy_name} in combat."
                memory_importance = 8
            elif combat_state["status"] == CombatStatus.FLED.value:
                memory_content = f"You fled from combat with {enemy_name}."
                memory_importance = 6
            else:
                memory_content = f"Combat with {enemy_name} ended after {combat_state['round']} rounds."
                memory_importance = 6
                
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=memory_content,
                importance=memory_importance,
                tier=MemoryTier.MEDIUM_TERM,
                tags=["combat", combat_state["status"]],
                game_id=game_id
            )
        
        # Return the final state before cleanup
        final_state = combat_state.copy()
        
        # Clean up (remove after a delay in a real implementation)
        # del self.active_combats[combat_id]
        
        return final_state


# Global combat system instance
combat_system = CombatSystem()