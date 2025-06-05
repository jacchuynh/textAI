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

# Enhanced combat imports
try:
    from .enhanced_combat.status_system import (
        EnhancedStatus, StatusFactory, StatusTier, StatusSource
    )
    from .enhanced_combat.combat_system_core import Status as EnhancedStatusType, Domain
    ENHANCED_STATUS_AVAILABLE = True
except ImportError:
    ENHANCED_STATUS_AVAILABLE = False

try:
    from .enhanced_combat.adaptive_enemy_ai import (
        AdaptiveEnemyAI, EnemyPersonality, CombatMemento
    )
    ADAPTIVE_AI_AVAILABLE = True
except ImportError:
    ADAPTIVE_AI_AVAILABLE = False

try:
    from .enhanced_combat.environment_effects import (
        EnvironmentEffect, _apply_burning_environment, _apply_freezing_environment
    )
    from .enhanced_combat.environment_system import (
        EnvironmentSystem, EnvironmentElement, EnvironmentInteraction
    )
    ENVIRONMENT_EFFECTS_AVAILABLE = True
except ImportError as e:
    ENVIRONMENT_EFFECTS_AVAILABLE = False

try:
    from .enhanced_combat.monster_database import (
        MonsterDatabase, load_monster_database, create_monster, get_random_monster
    )
    from .enhanced_combat.monster_archetypes import ThreatTier, ThreatCategory
    MONSTER_DATABASE_AVAILABLE = True
except ImportError:
    MONSTER_DATABASE_AVAILABLE = False
    # Fallback classes for when enhanced combat isn't available
    class StatusTier:
        MINOR = "minor"
        MODERATE = "moderate" 
        SEVERE = "severe"
        CRITICAL = "critical"
    
    class StatusSource:
        PHYSICAL = "physical"
        MENTAL = "mental"
        SPIRITUAL = "spiritual"
        ENVIRONMENTAL = "environmental"
        MAGICAL = "magical"
        SOCIAL = "social"


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
        self.active_combats: Dict[str, Dict[str, Any]] = {}
        self.combat_templates = self._load_combat_templates()
        # Enhanced combat integrations
        self.adaptive_ais: Dict[str, Dict[str, Any]] = {}  # combat_id -> {enemy_id -> AdaptiveEnemyAI}
        self.environment_systems: Dict[str, Any] = {}
        
        # Initialize monster database if available
        if MONSTER_DATABASE_AVAILABLE:
            self.monster_database = MonsterDatabase()
            self._load_monster_database()
        else:
            self.monster_database = None

    def _load_monster_database(self):
        """Load monster archetypes from YAML files in the data directory."""
        if not self.monster_database:
            return
            
        import os
        
        # Get the path to the data/monsters directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up from backend/src/game_engine to the root, then to data/monsters
        data_dir = os.path.join(current_dir, '..', '..', '..', 'data', 'monsters')
        data_dir = os.path.normpath(data_dir)
        
        try:
            if os.path.exists(data_dir):
                loaded_count = 0
                for filename in os.listdir(data_dir):
                    if filename.endswith('.yaml') or filename.endswith('.yml'):
                        file_path = os.path.join(data_dir, filename)
                        self.monster_database.load_from_yaml(file_path)
                        loaded_count += 1
                
                print(f"Combat System: Loaded {loaded_count} monster database files from {data_dir}")
                print(f"Combat System: {len(self.monster_database.archetypes)} monster archetypes available")
            else:
                print(f"Monster data directory {data_dir} does not exist. Using fallback enemy templates.")
        except Exception as e:
            print(f"Error loading monster database: {e}. Using fallback enemy templates.")

    def _create_enemy_from_database(self, 
                                  region: Optional[str] = None,
                                  tier: Optional[str] = None,
                                  category: Optional[str] = None,
                                  level: int = 1,
                                  archetype_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create an enemy using the monster database.
        
        Args:
            region: Optional region filter (e.g., 'human', 'ember', 'verdant')
            tier: Optional threat tier ('minion', 'standard', 'elite', 'boss', 'legendary')
            category: Optional category filter ('beast', 'humanoid', 'construct', etc.)
            level: Enemy level
            archetype_id: Specific archetype ID to use
            
        Returns:
            Enemy dictionary or None if creation failed
        """
        if not self.monster_database or not MONSTER_DATABASE_AVAILABLE:
            return None
        
        try:
            # Convert string tier to ThreatTier enum if provided
            threat_tier = None
            if tier:
                try:
                    threat_tier = ThreatTier[tier.upper()]
                except KeyError:
                    print(f"Warning: Unknown threat tier '{tier}', using random selection")
            
            # Convert string category to ThreatCategory enum if provided
            threat_category = None
            if category:
                try:
                    threat_category = ThreatCategory[category.upper()]
                except KeyError:
                    print(f"Warning: Unknown threat category '{category}', using random selection")
            
            # Get monster archetype
            if archetype_id:
                archetype = self.monster_database.get_archetype(archetype_id)
                if not archetype:
                    print(f"Warning: Archetype '{archetype_id}' not found")
                    return None
            else:
                archetype = self.monster_database.get_random_archetype(
                    region=region,
                    tier=threat_tier,
                    category=threat_category
                )
                if not archetype:
                    print(f"Warning: No monster found for criteria (region={region}, tier={tier}, category={category})")
                    return None
            
            # Create monster using the enhanced combat system
            monster_combatant, available_moves = create_monster(
                archetype_id=archetype.id,
                tier=threat_tier,
                level=level
            )
            
            # Convert to the format expected by the combat system
            enemy_data = {
                "id": str(uuid.uuid4()),
                "name": monster_combatant.name,
                "max_health": monster_combatant.max_health,
                "current_health": monster_combatant.current_health,
                "level": level,
                "archetype_id": archetype.id,
                "archetype": archetype,
                "combatant": monster_combatant,
                "available_moves": available_moves,
                "domains": self._convert_combatant_domains(monster_combatant),
                "attacks": self._convert_moves_to_attacks(available_moves),
                "description": archetype.description,
                "tags": [archetype.category.name.lower()],
                "resistances": [domain.name.lower() for domain in archetype.resistant_domains],
                "weaknesses": [domain.name.lower() for domain in archetype.weak_domains],
                "status_effects": []
            }
            
            return enemy_data
            
        except Exception as e:
            print(f"Error creating enemy from database: {e}")
            return None

    def _convert_combatant_domains(self, combatant) -> Dict[str, int]:
        """Convert enhanced combat domains to combat system format."""
        domain_mapping = {
            1: "body",      # Domain.BODY
            2: "mind",      # Domain.MIND
            3: "spirit",    # Domain.SPIRIT
            4: "authority", # Domain.AUTHORITY
            5: "craft",     # Domain.CRAFT
            6: "social",    # Domain.SOCIAL
            7: "awareness"  # Domain.AWARENESS
        }
        
        result = {}
        if hasattr(combatant, 'domains'):
            for domain_enum, value in combatant.domains.items():
                # domain_enum is a Domain enum (integer value)
                domain_name = domain_mapping.get(domain_enum.value, str(domain_enum).lower())
                result[domain_name] = value
        
        return result

    def _convert_moves_to_attacks(self, available_moves) -> List[Dict[str, Any]]:
        """Convert enhanced combat moves to legacy attack format."""
        attacks = []
        
        for move in available_moves:
            attack = {
                "name": move.name,
                "damage": getattr(move, 'base_damage', 3),  # Default damage if not specified
                "type": move.move_type.name.lower() if hasattr(move, 'move_type') else "physical",
                "description": getattr(move, 'description', f"Uses {move.name}"),
                "effects": []
            }
            
            # Add any special effects
            if hasattr(move, 'special_effects') and move.special_effects:
                for effect in move.special_effects:
                    attack["effects"].append({
                        "type": "special",
                        "description": effect
                    })
            
            attacks.append(attack)
        
        return attacks

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
    
    def _convert_character_domains(self, domains: Dict) -> Dict[str, int]:
        """
        Convert character domains to a simple string -> int mapping for combat.
        Handles both DomainType keys and string keys.
        """
        result = {}
        for key, value in domains.items():
            # Get the domain name as string
            if hasattr(key, 'value'):  # DomainType enum
                domain_name = key.value
            elif hasattr(key, 'name'):  # DomainType enum with .name
                domain_name = key.name.lower()
            else:  # Already a string
                domain_name = str(key).lower()
            
            # Get the domain value
            if hasattr(value, 'value'):  # Domain object
                domain_value = value.value
            else:  # Direct value
                domain_value = int(value)
            
            result[domain_name] = domain_value
        
        return result
    
    def start_combat(self, 
                    character: Character, 
                    enemy_template_id: Optional[int] = None, 
                    level_override: Optional[int] = None,
                    location_name: str = "Unknown",
                    environment_factors: List[str] = None,
                    surprise: bool = False,
                    game_id: Optional[str] = None,
                    # New monster database parameters
                    region: Optional[str] = None,
                    tier: Optional[str] = None,
                    category: Optional[str] = None,
                    archetype_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new combat encounter.
        
        Args:
            character: The player character
            enemy_template_id: ID of the enemy template (legacy, optional if using database)
            level_override: Optional level override for the enemy
            location_name: Name of the combat location
            environment_factors: List of environmental effects
            surprise: Whether this is a surprise attack
            game_id: Optional game ID for event tracking
            region: Optional region filter for monster database (e.g., 'human', 'ember', 'verdant')
            tier: Optional threat tier for monster database ('minion', 'standard', 'elite', 'boss', 'legendary')
            category: Optional category filter for monster database ('beast', 'humanoid', 'construct', etc.)
            archetype_id: Specific monster archetype ID to use from database
            
        Returns:
            New combat state
        """
        # Try to create enemy from monster database first
        enemy = None
        if MONSTER_DATABASE_AVAILABLE and self.monster_database:
            enemy_data = self._create_enemy_from_database(
                region=region,
                tier=tier,
                category=category,
                level=level_override or 1,
                archetype_id=archetype_id
            )
            if enemy_data:
                enemy = enemy_data
        
        # Fall back to template system if database creation failed or not available
        if not enemy:
            if enemy_template_id is None:
                # Default to a basic enemy if no specific enemy requested
                enemy_template_id = 1  # Wolf
                
            template = self.get_enemy_template(enemy_template_id)
            if not template:
                raise ValueError(f"Enemy template with ID {enemy_template_id} not found")
            
            # Create enemy instance from template
            enemy = template.create_instance(level_override)
        
        # Determine initiative/momentum
        momentum = "enemy" if surprise else "player"
        
        # Get health information from survival system if available
        max_health = 100
        current_health = 100
        
        # Try to get health from survival system
        try:
            from ..game_engine.survival_integration import SurvivalIntegration
            survival_integration = SurvivalIntegration()
            survival_state = survival_integration.get_survival_state(str(character.id))
            if survival_state:
                max_health = survival_state.max_health
                current_health = survival_state.current_health
        except Exception as e:
            # Fall back to calculating from character domains
            if character.domains:
                # Handle both DomainType keys and string keys
                body_domain = None
                if DomainType.BODY in character.domains:
                    body_domain = character.domains[DomainType.BODY]
                elif "body" in character.domains:
                    body_domain = character.domains["body"]
                elif hasattr(DomainType.BODY, 'value') and DomainType.BODY.value in character.domains:
                    body_domain = character.domains[DomainType.BODY.value]
                
                if body_domain:
                    body_value = body_domain.value if hasattr(body_domain, 'value') else body_domain
                    max_health = 100 + (body_value * 10)  # Base 100 + 10 per Body level
                    current_health = max_health

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
                "max_health": max_health,
                "current_health": current_health,
                "max_mana": getattr(character, "max_mana", 0),
                "current_mana": getattr(character, "current_mana", 0),
                "domains": self._convert_character_domains(character.domains) if character.domains else {},
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
        
        # Initialize environment system if available
        if ENVIRONMENT_EFFECTS_AVAILABLE:
            try:
                env_system = EnvironmentSystem()
                env_system.set_environment_tags(environment_factors or [])
                self.environment_systems[combat_id] = env_system
                
                # Add environment interactions to combat log
                if env_system.available_interactions:
                    interaction_names = list(env_system.available_interactions.keys())
                    combat_state["log"].append(f"Environmental interactions available: {', '.join(interaction_names)}")
            except Exception as e:
                # Fallback if environment system fails
                self.environment_systems[combat_id] = None
        
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
        
        # Add intimidation option (uses hybrid system)
        intimidate = CombatAction(
            label="Intimidate",
            action_type=CombatActionType.SPECIAL,
            domains=[DomainType.AUTHORITY, DomainType.SOCIAL],
            description="Attempt to frighten or demoralize the enemy",
            effects=[{"type": "fear", "duration": 2}],
            tags=["social", "intimidation", "fear"],
            requires_target=True
        )
        options.append(intimidate.to_dict())
        
        # Add precision strike (awareness + body)
        precision = CombatAction(
            label="Precision Strike",
            action_type=CombatActionType.ATTACK,
            domains=[DomainType.BODY, DomainType.AWARENESS],
            description="A carefully aimed attack targeting weak points",
            damage=4,
            tags=["physical", "weapon", "precise"],
            requires_target=True,
            difficulty_modifier=1  # Harder but more effective
        )
        options.append(precision.to_dict())
        
        # Add tactical analysis (mind-based)
        analyze = CombatAction(
            label="Analyze Enemy",
            action_type=CombatActionType.SPECIAL,
            domains=[DomainType.MIND, DomainType.AWARENESS],
            description="Study the enemy to find weaknesses and patterns",
            effects=[{"type": "analysis_bonus", "duration": 3}],
            tags=["tactical", "study", "intelligence"],
            requires_target=True
        )
        options.append(analyze.to_dict())
        
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
        
        # Add environmental interaction options
        combat_id = combat_state.get("id")
        if combat_id and combat_id in self.environment_systems and self.environment_systems[combat_id]:
            env_system = self.environment_systems[combat_id]
            for interaction_name, interaction in env_system.available_interactions.items():
                # Convert environment interaction to combat action
                env_action = CombatAction(
                    label=f"Environment: {interaction.name}",
                    action_type=CombatActionType.SPECIAL,
                    domains=[interaction.requirements.get("domain", DomainType.AWARENESS)],
                    description=interaction.description,
                    effects=[{"type": "environment", "interaction": interaction_name}],
                    tags=["environmental", "tactical"] + interaction.requirements.get("tags", []),
                    requires_target=interaction.effects.get("requires_target", False),
                    difficulty_modifier=interaction.requirements.get("difficulty_modifier", 0)
                )
                options.append(env_action.to_dict())
        
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
        
        # Roll for success using enhanced domain system
        
        # Determine primary domain for action
        primary_domain = self._determine_action_domain(action_data)
        
        # Find relevant tag for action
        action_tag = self._find_best_action_tag(character, action_data)
        
        # Calculate base difficulty
        base_difficulty = self._calculate_action_difficulty(action_data, target, combat_state)
        
        # Prepare target data for roll calculation
        target_data = None
        if target:
            target_data = {
                "level": target.get("level", 1),
                "resistances": target.get("resistances", []),
                "weaknesses": target.get("weaknesses", [])
            }
        
        # Perform enhanced action roll
        roll_result = character.roll_check_hybrid(
            domain_type=primary_domain,
            tag_name=action_tag,
            difficulty=base_difficulty,
            action_data=action_data,
            target=target_data,
            combat_state=combat_state
        )
        
        # Apply environment bonuses if available
        env_bonus = combat_state.get("environment_bonus", 0)
        if env_bonus > 0:
            roll_result["total"] += env_bonus
            roll_result["margin"] = roll_result["total"] - roll_result["difficulty"]
            roll_result["success"] = roll_result["total"] >= roll_result["difficulty"]
            roll_result["breakdown"] += f" + environment({env_bonus})"
            
            # Consume the environment bonus (one-time use)
            combat_state["environment_bonus"] = 0
        
        # Add to log with enhanced breakdown
        log_entry = f"Player used {action_data.get('label', 'an action')}. "
        
        if roll_result.get("method") == "dice":
            log_entry += f"Roll: {roll_result['breakdown']} = {roll_result['total']} "
        else:
            log_entry += f"Check: {roll_result['breakdown']} = {roll_result['total']} "
        
        log_entry += f"vs {roll_result['difficulty_breakdown']} - "
        log_entry += "Success!" if roll_result["success"] else "Failure!"
        
        # Add method information for debugging/narrative
        if roll_result.get("method_reason"):
            log_entry += f" ({roll_result['method_reason']})"
            
        combat_state["log"].append(log_entry)
        
        # Add to growth log with enhanced domain/tag tracking
        growth_entry = {
            "method": roll_result.get("method", "dice"),
            "domains_used": roll_result.get("domains_used", []),
            "tags_used": roll_result.get("tags_used", []),
            "success": roll_result["success"],
            "total": roll_result["total"],
            "dc": roll_result.get("difficulty", roll_result.get("dc", 10)),
            "margin": roll_result["margin"],
            "action": action_data.get("label", "Unknown action"),
            "critical": roll_result.get("critical", False)
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
            # Check if this is an environmental action
            is_environment_action = False
            for effect in action_data.get("effects", []):
                if effect.get("type") == "environment":
                    is_environment_action = True
                    interaction_name = effect.get("interaction")
                    try:
                        self._process_environment_action(combat_state, action_data, roll_result, interaction_name)
                    except Exception as e:
                        combat_state["log"].append(f"Error processing environment action: {e}")
                    break
            
            # Handle regular special attacks if not an environment action
            if not is_environment_action:
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
        
        # Try to use adaptive AI if available
        if ADAPTIVE_AI_AVAILABLE:
            adaptive_choice = self._choose_adaptive_attack(enemy, combat_state, attacks)
            if adaptive_choice:
                return adaptive_choice
        
        # Fallback to basic logic: usually use basic attacks, occasionally use specials
        if len(attacks) > 1 and random.random() < 0.3:
            # Use a non-primary attack
            return random.choice(attacks[1:])
        else:
            # Use the primary attack
            return attacks[0]
    
    def _choose_adaptive_attack(self, enemy: Dict[str, Any], combat_state: Dict[str, Any], attacks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Choose an attack using adaptive AI logic."""
        try:
            combat_id = combat_state.get("id", "")
            enemy_id = enemy.get("id", enemy.get("name", "unknown"))
            
            # Initialize adaptive AI for this enemy if not already done
            if combat_id not in self.adaptive_ais:
                self.adaptive_ais[combat_id] = {}
            
            if enemy_id not in self.adaptive_ais[combat_id]:
                # Create enemy personality based on enemy type
                personality = self._create_enemy_personality(enemy)
                
                # Create a mock combatant for the adaptive AI (simplified)
                enemy_combatant = self._create_mock_combatant(enemy)
                
                # Initialize the adaptive AI
                difficulty = min(1.0, enemy.get("level", 1) * 0.2)  # Scale difficulty with level
                self.adaptive_ais[combat_id][enemy_id] = AdaptiveEnemyAI(
                    enemy=enemy_combatant,
                    personality=personality,
                    difficulty=difficulty
                )
            
            # Get the adaptive AI for this enemy
            ai = self.adaptive_ais[combat_id][enemy_id]
            
            # Record player's last action if available
            if "last_player_action" in combat_state:
                last_action = combat_state["last_player_action"]
                # Convert to adaptive AI's expected format
                if last_action:
                    ai.record_player_move(last_action.get("action_type", "attack"))
            
            # Get AI's recommended action
            health_ratio = enemy["current_health"] / enemy["max_health"]
            
            # Use AI logic to choose attack
            if health_ratio < 0.3:  # Desperate
                # Favor powerful attacks when desperate
                powerful_attacks = [a for a in attacks if a.get("damage", 0) >= 5]
                if powerful_attacks:
                    return random.choice(powerful_attacks)
            elif health_ratio < 0.6:  # Tactical
                # Try to counter player patterns
                predicted_move = ai.predict_next_move() if hasattr(ai, 'predict_next_move') else None
                if predicted_move:
                    # Choose counter-attack based on prediction
                    counter_attacks = self._get_counter_attacks(attacks, predicted_move)
                    if counter_attacks:
                        return random.choice(counter_attacks)
            
            # Use personality-based selection
            return self._choose_personality_based_attack(attacks, ai.personality)
            
        except Exception as e:
            # Fallback on any error
            return None
    
    
    def _create_enemy_personality(self, enemy: Dict[str, Any]) -> 'EnemyPersonality':
        """Create a personality for an enemy based on its characteristics."""
        if not ADAPTIVE_AI_AVAILABLE:
            return None
            
        # Enhanced: Use database archetype personality if available
        if "archetype" in enemy and enemy["archetype"]:
            archetype = enemy["archetype"]
            # Base personality on archetype category and traits
            category = archetype.category.name.lower() if hasattr(archetype.category, 'name') else 'beast'
            
            # Get personality modifiers from archetype
            aggression = getattr(archetype, 'aggression_modifier', 0.5)
            adaptability = getattr(archetype, 'intelligence_modifier', 0.3)
            risk_taking = getattr(archetype, 'risk_modifier', 0.4)
            calculation = getattr(archetype, 'calculation_modifier', 0.5)
            
            # Adjust based on category
            if category in ['beast', 'animal']:
                aggression = min(1.0, aggression + 0.3)
                calculation = max(0.1, calculation - 0.3)
            elif category in ['humanoid', 'human']:
                calculation = min(1.0, calculation + 0.2)
                adaptability = min(1.0, adaptability + 0.2)
            elif category in ['construct', 'undead']:
                calculation = min(1.0, calculation + 0.4)
                risk_taking = max(0.1, risk_taking - 0.2)
            elif category in ['demon', 'devil']:
                calculation = min(1.0, calculation + 0.3)
                aggression = min(1.0, aggression + 0.2)
                
        else:
            # Fall back to original logic
            enemy_name = enemy.get("name", "").lower()
            level = enemy.get("level", 1)
            
            # Default personality
            aggression = 0.5
            adaptability = 0.3
            risk_taking = 0.4
            calculation = 0.5
            
            # Adjust based on enemy type
            if "wolf" in enemy_name or "beast" in enemy_name:
                aggression = 0.8
                risk_taking = 0.6
                calculation = 0.2
            elif "bandit" in enemy_name or "rogue" in enemy_name:
                calculation = 0.7
                adaptability = 0.6
                aggression = 0.6
            elif "mage" in enemy_name or "wizard" in enemy_name:
                calculation = 0.9
                adaptability = 0.8
                aggression = 0.3
            elif "warrior" in enemy_name or "knight" in enemy_name:
                aggression = 0.7
                calculation = 0.6
                risk_taking = 0.5
        
        # Scale adaptability with level
        level = enemy.get("level", 1)
        adaptability = min(1.0, adaptability + (level * 0.1))
        
        return EnemyPersonality(
            aggression=aggression,
            adaptability=adaptability,
            risk_taking=risk_taking,
            calculation=calculation
        )
    
    def _create_mock_combatant(self, enemy: Dict[str, Any]):
        """Create a simplified combatant object for adaptive AI."""
        # This is a simplified mock - in a full implementation,
        # you'd convert the enemy dict to a proper Combatant object
        class MockCombatant:
            def __init__(self, enemy_data):
                self.name = enemy_data.get("name", "Enemy")
                self.max_health = enemy_data.get("max_health", enemy_data.get("health", 20))
                self.current_health = enemy_data.get("current_health", self.max_health)
                self.level = enemy_data.get("level", 1)
                
                # Enhanced: Use database moves if available
                if "available_moves" in enemy_data:
                    self.available_moves = enemy_data["available_moves"]
                else:
                    self.available_moves = []  # Would be populated with actual moves
                
                # Enhanced: Use database archetype if available
                if "archetype" in enemy_data:
                    self.archetype = enemy_data["archetype"]
                    # Use archetype personality traits for AI
                    self.personality_traits = {
                        "aggression": getattr(self.archetype, 'aggression_modifier', 0.5),
                        "intelligence": getattr(self.archetype, 'intelligence_modifier', 0.5),
                        "cunning": getattr(self.archetype, 'cunning_modifier', 0.5)
                    }
                else:
                    self.archetype = None
                    self.personality_traits = {}
                
        return MockCombatant(enemy)
    
    def _get_counter_attacks(self, attacks: List[Dict[str, Any]], predicted_move: str) -> List[Dict[str, Any]]:
        """Get attacks that counter the predicted player move."""
        # Simple counter logic - in a full implementation, this would be more sophisticated
        counters = []
        
        if predicted_move == "attack":
            # Counter attacks with defensive moves or powerful strikes
            counters = [a for a in attacks if "counter" in a.get("name", "").lower() or 
                       "block" in a.get("name", "").lower() or
                       a.get("damage", 0) >= 6]
        elif predicted_move == "defend":
            # Counter defense with overwhelming attacks
            counters = [a for a in attacks if a.get("damage", 0) >= 5]
        elif predicted_move == "magic":
            # Counter magic with interruption or resistance
            counters = [a for a in attacks if "interrupt" in a.get("name", "").lower() or
                       a.get("type") == "mental"]
        
        return counters if counters else attacks
    
    def _choose_personality_based_attack(self, attacks: List[Dict[str, Any]], personality) -> Dict[str, Any]:
        """Choose an attack based on enemy personality."""
        if not personality:
            return random.choice(attacks)
        
        # High aggression favors high damage attacks
        if personality.aggression > 0.7:
            high_damage = [a for a in attacks if a.get("damage", 0) >= 5]
            if high_damage:
                return random.choice(high_damage)
        
        # High calculation favors special/tactical attacks
        if personality.calculation > 0.7 and len(attacks) > 1:
            special_attacks = [a for a in attacks if a.get("type") != "physical" or
                             "special" in a.get("name", "").lower()]
            if special_attacks:
                return random.choice(special_attacks)
        
        # Default to random selection
        return random.choice(attacks)
    
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
        
        # Sync health changes back to survival system if available
        try:
            from ..game_engine.survival_integration import SurvivalIntegration
            from ..shared.survival_models import SurvivalStateUpdate
            survival_integration = SurvivalIntegration()
            
            current_health = combat_state["player"]["current_health"]
            max_health = combat_state["player"]["max_health"]
            character_id = combat_state["player"]["id"]
            
            # Get current survival state
            survival_state = survival_integration.get_survival_state(character_id)
            if survival_state:
                # Calculate health change during combat
                health_change = current_health - survival_state.current_health
                
                # Only update if there was a change
                if health_change != 0:
                    update = SurvivalStateUpdate(current_health=health_change)
                    survival_integration.survival_system.update_survival_state(character_id, update)
        except Exception as e:
            # Silently fail if survival system not available
            pass
        
        # Clean up environment system
        if combat_id in self.environment_systems:
            del self.environment_systems[combat_id]
            
        # Clean up adaptive AI
        if combat_id in self.adaptive_ais:
            del self.adaptive_ais[combat_id]
        
        # Clean up (remove after a delay in a real implementation)
        # del self.active_combats[combat_id]
        
        return final_state

    def _determine_action_domain(self, action_data: Dict[str, Any]) -> DomainType:
        """Determine the primary domain for a combat action."""
        
        # First check if the action specifies domains
        domains = action_data.get("domains", [])
        if domains:
            # Handle both DomainType enums and integer values
            first_domain = domains[0]
            if isinstance(first_domain, DomainType):
                return first_domain
            elif isinstance(first_domain, int):
                # Convert enhanced combat Domain enum integer to DomainType
                # The enhanced combat Domain enum uses auto() which creates sequential integers
                domain_mapping = {
                    1: DomainType.BODY,      # Domain.BODY
                    2: DomainType.MIND,      # Domain.MIND  
                    3: DomainType.CRAFT,     # Domain.CRAFT
                    4: DomainType.AWARENESS, # Domain.AWARENESS
                    5: DomainType.SOCIAL,    # Domain.SOCIAL
                    6: DomainType.AUTHORITY, # Domain.AUTHORITY
                    7: DomainType.SPIRIT,    # Domain.SPIRIT
                }
                if first_domain in domain_mapping:
                    return domain_mapping[first_domain]
            elif isinstance(first_domain, str):
                # Convert string to DomainType enum
                try:
                    return DomainType(first_domain.lower())
                except ValueError:
                    pass  # Fall through to other methods
        
        action_type = action_data.get("action_type", "attack")
        action_label = action_data.get("label", "").lower()
        
        # Map action types to domains
        action_domain_map = {
            'attack': DomainType.AWARENESS,     # Combat reflexes and targeting
            'defend': DomainType.SPIRIT,        # Willpower and resilience
            'magic': DomainType.MIND,           # Magical theory and power
            'social': DomainType.SOCIAL,        # Intimidation, persuasion
            'skill': DomainType.CRAFT,          # Technical skills and tools
            'movement': DomainType.AWARENESS,   # Agility and positioning
            'special': DomainType.MIND          # Unique abilities
        }
        
        # Check for keyword matches in label
        if any(keyword in action_label for keyword in ['magic', 'spell', 'cast']):
            return DomainType.MIND
        elif any(keyword in action_label for keyword in ['intimidate', 'taunt', 'inspire']):
            return DomainType.SOCIAL
        elif any(keyword in action_label for keyword in ['dodge', 'duck', 'evade', 'move']):
            return DomainType.AWARENESS
        elif any(keyword in action_label for keyword in ['block', 'guard', 'defend', 'resist']):
            return DomainType.SPIRIT
        elif any(keyword in action_label for keyword in ['craft', 'tool', 'device']):
            return DomainType.CRAFT
        
        # Default to action type mapping
        return action_domain_map.get(action_type, DomainType.AWARENESS)

    def _find_best_action_tag(self, character: Character, action_data: Dict[str, Any]) -> Optional[str]:
        """Find the best tag for the character to use with this action."""
        action_type = action_data.get("action_type", "attack")
        action_label = action_data.get("label", "").lower()
        
        combat_related_tags = []
        
        # Look for combat-related tags
        for tag_name, tag in character.tags.items():
            tag_name_lower = tag_name.lower()
            
            # General combat tags
            if any(keyword in tag_name_lower for keyword in ['combat', 'fight', 'battle', 'warrior']):
                combat_related_tags.append((tag_name, tag.rank))
            
            # Weapon-specific tags
            elif any(keyword in tag_name_lower for keyword in ['sword', 'bow', 'staff', 'dagger', 'weapon']):
                combat_related_tags.append((tag_name, tag.rank))
                
            # Magic-related tags for magic actions
            elif action_type == 'magic' and any(keyword in tag_name_lower for keyword in ['magic', 'spell', 'arcane', 'mana']):
                combat_related_tags.append((tag_name, tag.rank))
                
            # Social tags for social actions
            elif action_type == 'social' and any(keyword in tag_name_lower for keyword in ['intimidate', 'persuade', 'leadership']):
                combat_related_tags.append((tag_name, tag.rank))
        
        # Return the highest ranked relevant tag
        if combat_related_tags:
            return max(combat_related_tags, key=lambda x: x[1])[0]
        
        return None

    def _calculate_action_difficulty(self, action_data: Dict[str, Any], target: Optional[Dict[str, Any]], combat_state: Dict[str, Any]) -> int:
        """Calculate the difficulty for performing a combat action."""
        base_difficulty = 10
        
        # Adjust for action complexity
        action_type = action_data.get("action_type", "attack")
        complexity_adjustments = {
            'attack': 0,
            'defend': 0,
            'magic': 3,      # Magic is harder
            'social': 2,     # Social actions moderately harder
            'special': 4,    # Special abilities are hardest
            'skill': 1       # Skill-based actions slightly harder
        }
        base_difficulty += complexity_adjustments.get(action_type, 0)
        
        # Adjust for target difficulty
        if target:
            target_level = target.get("level", 1)
            level_modifier = max(0, target_level - 1)  # Each level above 1 adds difficulty
            base_difficulty += level_modifier
            
            # Adjust for target resistances
            resistances = target.get("resistances", [])
            if resistances:
                base_difficulty += len(resistances)  # Each resistance adds +1 difficulty
        
        # Adjust for combat conditions
        combat_round = combat_state.get("round", 1)
        if combat_round > 5:
            base_difficulty += 1  # Combat fatigue after round 5
        
        # Adjust for wounds/status effects
        player_status = combat_state.get("player_status", {})
        if player_status.get("wounded", False):
            base_difficulty += 2
        if player_status.get("exhausted", False):
            base_difficulty += 3
        
        return max(5, base_difficulty)  # Minimum difficulty of 5

    # Enhanced Status System Integration
    def apply_enhanced_status(self, combat_state: Dict[str, Any], target_key: str, 
                            status_name: str, tier: str, source: str, 
                            duration: int = 3, description: str = "") -> Dict[str, Any]:
        """
        Apply an enhanced status effect to a combatant.
        
        Args:
            combat_state: Current combat state
            target_key: "player" or "enemies[0]" etc.
            status_name: Name of the status effect
            tier: Severity tier (minor, moderate, severe, critical)
            source: Source of the effect (physical, mental, etc.)
            duration: Duration in rounds
            description: Custom description
            
        Returns:
            Result of status application
        """
        if not ENHANCED_STATUS_AVAILABLE:
            # Fallback to basic status system
            return self._apply_basic_status(combat_state, target_key, status_name, duration, description)
        
        try:
            # Create enhanced status effect
            enhanced_status = StatusFactory.create_status(
                name=status_name,
                tier=getattr(StatusTier, tier.upper()),
                source=getattr(StatusSource, source.upper()),
                duration=duration,
                description=description or f"{status_name} effect"
            )
            
            # Apply to target
            target = self._get_combat_target(combat_state, target_key)
            if target:
                # Initialize enhanced status tracking if needed
                if "enhanced_statuses" not in target:
                    target["enhanced_statuses"] = []
                
                # Add the enhanced status
                target["enhanced_statuses"].append({
                    "name": enhanced_status.name,
                    "tier": enhanced_status.tier.name,
                    "source": enhanced_status.source.name,
                    "duration": enhanced_status.duration,
                    "description": enhanced_status.description,
                    "stat_modifiers": enhanced_status.stat_modifiers,
                    "domain_modifiers": enhanced_status.domain_modifiers,
                    "special_effects": enhanced_status.special_effects
                })
                
                # Apply immediate effects
                self._apply_status_modifiers(target, enhanced_status)
                
                combat_state["log"].append(f"{target.get('name', 'Target')} is now {enhanced_status.description}")
                
                return {
                    "success": True,
                    "status_applied": enhanced_status.name,
                    "tier": enhanced_status.tier.name,
                    "duration": enhanced_status.duration
                }
                
        except Exception as e:
            # Fallback to basic status system
            return self._apply_basic_status(combat_state, target_key, status_name, duration, description)
    
    
    def _apply_basic_status(self, combat_state: Dict[str, Any], target_key: str, 
                          status_name: str, duration: int, description: str) -> Dict[str, Any]:
        """Fallback basic status application."""
        target = self._get_combat_target(combat_state, target_key)
        if target:
            if "status_effects" not in target:
                target["status_effects"] = []
            
            target["status_effects"].append({
                "type": status_name,
                "duration": duration,
                "description": description or f"{status_name} effect"
            })
            
            combat_state["log"].append(f"{target.get('name', 'Target')} is now {description or status_name}")
            
            return {"success": True, "status_applied": status_name, "duration": duration}
        
        return {"success": False, "reason": "Target not found"}
    
    def _get_combat_target(self, combat_state: Dict[str, Any], target_key: str) -> Optional[Dict[str, Any]]:
        """Get a combat target by key."""
        if target_key == "player":
            return combat_state.get("player")
        elif target_key.startswith("enemies[") and target_key.endswith("]"):
            try:
                index = int(target_key[8:-1])
                enemies = combat_state.get("enemies", [])
                if 0 <= index < len(enemies):
                    return enemies[index]
            except (ValueError, IndexError):
                pass
        return None
    
    def _apply_status_modifiers(self, target: Dict[str, Any], enhanced_status) -> None:
        """Apply stat modifiers from enhanced status."""
        if not hasattr(enhanced_status, 'stat_modifiers'):
            return
            
        for stat, modifier in enhanced_status.stat_modifiers.items():
            if stat == "max_health":
                original_max = target.get("max_health", target.get("health", 20))
                target["max_health"] = max(1, original_max + modifier)
                # Keep current health within bounds
                target["current_health"] = min(target.get("current_health", original_max), target["max_health"])
            elif stat == "defense":
                target["defense_bonus"] = target.get("defense_bonus", 0) + modifier
            elif stat == "attack":
                target["attack_bonus"] = target.get("attack_bonus", 0) + modifier
    
    def update_status_effects(self, combat_state: Dict[str, Any]) -> None:
        """Update all status effects at the end of a round."""
        for combatant_key in ["player", "enemies"]:
            if combatant_key == "player":
                targets = [combat_state.get("player")] if combat_state.get("player") else []
            else:
                targets = combat_state.get("enemies", [])
            
            for target in targets:
                if not target:
                    continue
                    
                # Update basic status effects
                if "status_effects" in target:
                    target["status_effects"] = [
                        effect for effect in target["status_effects"]
                        if self._update_basic_status_effect(effect, target)
                    ]
                
                # Update enhanced status effects
                if "enhanced_statuses" in target:
                    target["enhanced_statuses"] = [
                        status for status in target["enhanced_statuses"]
                        if self._update_enhanced_status_effect(status, target, combat_state)
                    ]
    
    def _update_basic_status_effect(self, effect: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Update a basic status effect and return True if it should continue."""
        effect["duration"] -= 1
        if effect["duration"] <= 0:
            # Status effect expired
            return False
        return True
    
    def _update_enhanced_status_effect(self, status: Dict[str, Any], target: Dict[str, Any], combat_state: Dict[str, Any]) -> bool:
        """Update an enhanced status effect and return True if it should continue."""
        status["duration"] -= 1
        
        # Apply ongoing effects based on status type
        if status["name"] == "poisoned" and status["duration"] > 0:
            damage = 2  # Poison damage per round
            target["current_health"] = max(0, target.get("current_health", 0) - damage)
            combat_state["log"].append(f"{target.get('name', 'Target')} takes {damage} poison damage!")
        
        if status["duration"] <= 0:
            # Remove stat modifiers when status expires
            self._remove_status_modifiers(target, status)
            combat_state["log"].append(f"{target.get('name', 'Target')} recovers from {status['name']}")
            return False
        
        return True
    
    def _remove_status_modifiers(self, target: Dict[str, Any], status: Dict[str, Any]) -> None:
        """Remove stat modifiers when a status effect expires."""
        stat_modifiers = status.get("stat_modifiers", {})
        
        for stat, modifier in stat_modifiers.items():
            if stat == "defense":
                target["defense_bonus"] = target.get("defense_bonus", 0) - modifier
            elif stat == "attack":
                target["attack_bonus"] = target.get("attack_bonus", 0) - modifier

    def _process_environment_action(self, 
                                   combat_state: Dict[str, Any], 
                                   action_data: Dict[str, Any], 
                                   roll_result: Dict[str, Any], 
                                   interaction_name: str) -> None:
        """
        Process an environmental interaction action.
        
        Args:
            combat_state: Current combat state
            action_data: The action data
            roll_result: Result of the roll check
            interaction_name: Name of the environment interaction
        """
        if not roll_result["success"]:
            combat_state["log"].append(f"Failed to use the environment effectively.")
            return
        
        combat_id = combat_state.get("id")
        if not combat_id or combat_id not in self.environment_systems:
            return
            
        env_system = self.environment_systems[combat_id]
        if not env_system or interaction_name not in env_system.available_interactions:
            return
            
        interaction = env_system.available_interactions[interaction_name]
        effects = interaction.effects
        
        # Apply environment interaction effects
        if "damage_bonus" in effects:
            bonus = effects["damage_bonus"]
            # Find the target enemy and apply extra damage
            for enemy in combat_state["enemies"]:
                if enemy.get("current_health", 0) > 0:
                    enemy["current_health"] = max(0, enemy["current_health"] - bonus)
                    combat_state["log"].append(
                        f"Environmental effect deals {bonus} additional damage to {enemy['name']}! "
                        f"Health: {enemy['current_health']}/{enemy['max_health']}"
                    )
                    break
        
        if "roll_bonus" in effects:
            # Apply bonus to next action (store in combat state)
            bonus = effects["roll_bonus"]
            combat_state["environment_bonus"] = combat_state.get("environment_bonus", 0) + bonus
            combat_state["log"].append(f"Environmental advantage grants +{bonus} to your next action!")
        
        if "defense_bonus" in effects:
            bonus = effects["defense_bonus"]
            combat_state["player"]["status_effects"].append({
                "type": "environmental_defense",
                "value": bonus,
                "duration": 2,
                "description": f"Environmental defense bonus: +{bonus}"
            })
            combat_state["log"].append(f"Environmental cover provides +{bonus} defense for 2 rounds!")
        
        if "surprise_bonus" in effects:
            combat_state["momentum"] = "player"
            combat_state["log"].append("Environmental stealth gives you the advantage!")
        
        if "aoe_damage" in effects:
            aoe_damage = effects["aoe_damage"]
            # Apply to all enemies
            enemies_hit = 0
            for enemy in combat_state["enemies"]:
                if enemy.get("current_health", 0) > 0:
                    enemy["current_health"] = max(0, enemy["current_health"] - aoe_damage)
                    enemies_hit += 1
            
            if enemies_hit > 0:
                combat_state["log"].append(
                    f"Environmental collapse deals {aoe_damage} damage to {enemies_hit} enemies!"
                )
        
        # Add narrative description
        if "narrative" in effects:
            combat_state["log"].append(effects["narrative"])
        else:
            combat_state["log"].append(f"Successfully used {interaction.name}!")
        
        # Apply critical success bonuses
        if roll_result.get("critical"):
            combat_state["log"].append("Critical environmental interaction! Enhanced effects!")
            # Double any numerical bonuses for critical success
            for key in ["damage_bonus", "roll_bonus", "defense_bonus", "aoe_damage"]:
                if key in effects:
                    extra = effects[key]
                    if key == "damage_bonus" or key == "aoe_damage":
                        # Apply extra damage to enemies
                        for enemy in combat_state["enemies"]:
                            if enemy.get("current_health", 0) > 0:
                                enemy["current_health"] = max(0, enemy["current_health"] - extra)
                        combat_state["log"].append(f"Critical success deals {extra} additional damage!")
                    elif key == "roll_bonus":
                        combat_state["environment_bonus"] = combat_state.get("environment_bonus", 0) + extra
                        combat_state["log"].append(f"Critical success grants an additional +{extra} bonus!")