"""
Monster archetypes for the enhanced combat system.

This module defines common monster/threat archetypes that serve as templates 
for creating varied and thematically consistent enemies.
"""
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .combat_system_core import Domain, MoveType, Status, Combatant, CombatMove


class ThreatTier(Enum):
    """Tiers of threat difficulty"""
    MINION = auto()      # Weak enemies, easily defeated
    STANDARD = auto()    # Normal difficulty enemies
    ELITE = auto()       # Challenging enemies with special abilities
    BOSS = auto()        # Major opponents with unique mechanics
    LEGENDARY = auto()   # Epic-level threats with complex abilities


class ThreatCategory(Enum):
    """Categories of threats/monsters"""
    BEAST = "Beast"             # Animals and natural creatures
    UNDEAD = "Undead"           # Reanimated dead and spirits
    HUMANOID = "Humanoid"       # Human-like intelligent creatures
    MAGICAL = "Magical"         # Magical creatures and constructs
    ELEMENTAL = "Elemental"     # Elemental manifestations
    ABERRATION = "Aberration"   # Unnatural, otherworldly beings
    COSMIC = "Cosmic"           # Reality-warping entities
    MECHANICAL = "Mechanical"   # Constructs and machines
    PLANT = "Plant"             # Plant-based creatures
    SWARM = "Swarm"             # Groups of small creatures acting as one


@dataclass
class MoveBehavior:
    """Defines a specific move behavior for an archetype"""
    name: str
    description: str
    move_type: MoveType
    domains: List[Domain]
    priority: int  # 0-10 scale, higher means more likely to use
    conditions: Dict[str, Any]  # Conditions when this behavior is preferred
    special_effects: List[str]  # Special effects this move can apply


@dataclass
class MonsterArchetype:
    """
    Template for creating monsters/threats of a specific type.
    
    This provides thematic consistency and starting points for
    enemy creation, while still allowing for customization.
    """
    id: str
    name: str
    description: str
    category: ThreatCategory
    primary_domains: List[Domain]  # Main domains this archetype excels in
    weak_domains: List[Domain]     # Domains this archetype is weak against
    resistant_domains: List[Domain]  # Domains this archetype resists
    
    # Base stat modifiers relative to standard (1.0)
    health_modifier: float = 1.0
    stamina_modifier: float = 1.0
    focus_modifier: float = 1.0
    spirit_modifier: float = 1.0
    
    # Base move behaviors
    move_behaviors: List[MoveBehavior] = None
    
    # Tier-specific behavior modifications
    tier_adjustments: Dict[ThreatTier, Dict[str, Any]] = None
    
    # Status effect resistances and vulnerabilities
    status_resistances: List[Status] = None
    status_vulnerabilities: List[Status] = None
    
    def apply_tier_adjustments(self, tier: ThreatTier) -> Dict[str, Any]:
        """
        Get stat adjustments for a specific threat tier.
        
        Args:
            tier: The threat tier
            
        Returns:
            Dictionary with adjusted stat modifiers
        """
        if not self.tier_adjustments or tier not in self.tier_adjustments:
            # Default tier adjustments if none specified
            if tier == ThreatTier.MINION:
                return {
                    "health_modifier": self.health_modifier * 0.5,
                    "stamina_modifier": self.stamina_modifier * 0.7,
                    "focus_modifier": self.focus_modifier * 0.6,
                    "spirit_modifier": self.spirit_modifier * 0.5,
                    "domain_bonus": -1
                }
            elif tier == ThreatTier.ELITE:
                return {
                    "health_modifier": self.health_modifier * 1.5,
                    "stamina_modifier": self.stamina_modifier * 1.3,
                    "focus_modifier": self.focus_modifier * 1.4,
                    "spirit_modifier": self.spirit_modifier * 1.3,
                    "domain_bonus": 1
                }
            elif tier == ThreatTier.BOSS:
                return {
                    "health_modifier": self.health_modifier * 2.5,
                    "stamina_modifier": self.stamina_modifier * 1.8,
                    "focus_modifier": self.focus_modifier * 2.0,
                    "spirit_modifier": self.spirit_modifier * 2.0,
                    "domain_bonus": 2,
                    "special_ability": True
                }
            elif tier == ThreatTier.LEGENDARY:
                return {
                    "health_modifier": self.health_modifier * 4.0,
                    "stamina_modifier": self.stamina_modifier * 2.5,
                    "focus_modifier": self.focus_modifier * 3.0,
                    "spirit_modifier": self.spirit_modifier * 3.0,
                    "domain_bonus": 3,
                    "special_ability": True,
                    "legendary_action": True
                }
            else:  # STANDARD tier or any unspecified tier
                return {
                    "health_modifier": self.health_modifier,
                    "stamina_modifier": self.stamina_modifier,
                    "focus_modifier": self.focus_modifier,
                    "spirit_modifier": self.spirit_modifier,
                    "domain_bonus": 0
                }
        else:
            # Use specified tier adjustments
            return self.tier_adjustments[tier]


# Library of monster archetypes
MONSTER_ARCHETYPES: Dict[str, MonsterArchetype] = {}


def _init_archetypes():
    """Initialize the monster archetype library"""
    
    # Wolf archetype (Beast category)
    wolf_archetype = MonsterArchetype(
        id="wolf",
        name="Wolf",
        description="A fierce predator that hunts in packs. Known for speed and coordinated attacks.",
        category=ThreatCategory.BEAST,
        primary_domains=[Domain.BODY, Domain.AWARENESS],
        weak_domains=[Domain.MIND, Domain.SPIRIT],
        resistant_domains=[Domain.BODY],
        health_modifier=0.8,
        stamina_modifier=1.2,
        focus_modifier=0.7,
        spirit_modifier=0.6,
        move_behaviors=[
            MoveBehavior(
                name="Bite",
                description="A powerful bite attack that can cause bleeding",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                priority=8,
                conditions={"health_percent": ">50"},
                special_effects=["BLEED"]
            ),
            MoveBehavior(
                name="Howl",
                description="A chilling howl that can frighten opponents",
                move_type=MoveType.UTILITY,
                domains=[Domain.AUTHORITY],
                priority=4,
                conditions={"first_round": True},
                special_effects=["FRIGHTEN"]
            ),
            MoveBehavior(
                name="Pack Tactics",
                description="Coordinated attack that's more effective against distracted foes",
                move_type=MoveType.TRICK,
                domains=[Domain.AWARENESS, Domain.BODY],
                priority=7,
                conditions={"target_status": "STUNNED"},
                special_effects=["BONUS_DAMAGE"]
            )
        ],
        status_resistances=[Status.FRIGHTENED],
        status_vulnerabilities=[Status.STUNNED]
    )
    
    # Zombie archetype (Undead category)
    zombie_archetype = MonsterArchetype(
        id="zombie",
        name="Zombie",
        description="A reanimated corpse driven by dark magic. Slow but relentless.",
        category=ThreatCategory.UNDEAD,
        primary_domains=[Domain.BODY],
        weak_domains=[Domain.MIND, Domain.AWARENESS],
        resistant_domains=[Domain.SPIRIT],
        health_modifier=1.3,
        stamina_modifier=0.7,
        focus_modifier=0.3,
        spirit_modifier=0.5,
        move_behaviors=[
            MoveBehavior(
                name="Shambling Attack",
                description="A slow but powerful strike",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                priority=9,
                conditions={},
                special_effects=[]
            ),
            MoveBehavior(
                name="Festering Wound",
                description="An attack that can cause disease",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                priority=6,
                conditions={"target_health_percent": "<70"},
                special_effects=["POISON"]
            ),
            MoveBehavior(
                name="Undying Resilience",
                description="Temporarily ignore wounds and fight on",
                move_type=MoveType.UTILITY,
                domains=[Domain.SPIRIT],
                priority=5,
                conditions={"health_percent": "<30"},
                special_effects=["TEMPORARY_HEALTH"]
            )
        ],
        status_resistances=[Status.POISONED, Status.FRIGHTENED],
        status_vulnerabilities=[Status.STUNNED]
    )
    
    # Cultist archetype (Humanoid category)
    cultist_archetype = MonsterArchetype(
        id="cultist",
        name="Cultist",
        description="A fanatical follower of dark powers. Uses forbidden knowledge and rituals.",
        category=ThreatCategory.HUMANOID,
        primary_domains=[Domain.SPIRIT, Domain.MIND],
        weak_domains=[Domain.BODY],
        resistant_domains=[Domain.SPIRIT],
        health_modifier=0.7,
        stamina_modifier=0.8,
        focus_modifier=1.2,
        spirit_modifier=1.4,
        move_behaviors=[
            MoveBehavior(
                name="Dark Incantation",
                description="A spell that drains life force",
                move_type=MoveType.FOCUS,
                domains=[Domain.SPIRIT, Domain.MIND],
                priority=8,
                conditions={"focus_percent": ">50"},
                special_effects=["LIFE_DRAIN"]
            ),
            MoveBehavior(
                name="Sacrificial Ritual",
                description="A desperate move that harms the cultist but deals significant damage",
                move_type=MoveType.FORCE,
                domains=[Domain.SPIRIT],
                priority=5,
                conditions={"health_percent": "<40"},
                special_effects=["SELF_DAMAGE", "BONUS_DAMAGE"]
            ),
            MoveBehavior(
                name="Mind Fog",
                description="Clouds the target's mind, reducing their focus",
                move_type=MoveType.TRICK,
                domains=[Domain.MIND],
                priority=7,
                conditions={"first_meeting": True},
                special_effects=["CONFUSE"]
            )
        ],
        status_resistances=[Status.CONFUSED],
        status_vulnerabilities=[Status.STUNNED, Status.WOUNDED]
    )
    
    # Elemental archetype (Elemental category)
    elemental_archetype = MonsterArchetype(
        id="elemental",
        name="Elemental",
        description="A living manifestation of natural forces. Powerful but single-minded.",
        category=ThreatCategory.ELEMENTAL,
        primary_domains=[Domain.SPIRIT, Domain.BODY],
        weak_domains=[Domain.MIND, Domain.SOCIAL],
        resistant_domains=[Domain.BODY, Domain.SPIRIT],
        health_modifier=1.2,
        stamina_modifier=1.5,
        focus_modifier=0.6,
        spirit_modifier=1.6,
        move_behaviors=[
            MoveBehavior(
                name="Elemental Surge",
                description="A powerful blast of elemental energy",
                move_type=MoveType.FORCE,
                domains=[Domain.SPIRIT, Domain.BODY],
                priority=8,
                conditions={},
                special_effects=["ELEMENTAL_EFFECT"]
            ),
            MoveBehavior(
                name="Nature's Shield",
                description="Hardens the elemental's form for protection",
                move_type=MoveType.UTILITY,
                domains=[Domain.BODY, Domain.SPIRIT],
                priority=6,
                conditions={"health_percent": "<60"},
                special_effects=["DAMAGE_REDUCTION"]
            ),
            MoveBehavior(
                name="Elemental Absorption",
                description="Absorbs energy to heal",
                move_type=MoveType.UTILITY,
                domains=[Domain.SPIRIT],
                priority=7,
                conditions={"health_percent": "<50"},
                special_effects=["HEAL"]
            )
        ],
        status_resistances=[Status.POISONED, Status.STUNNED],
        status_vulnerabilities=[Status.EXHAUSTED]
    )
    
    # Bandit archetype (Humanoid category)
    bandit_archetype = MonsterArchetype(
        id="bandit",
        name="Bandit",
        description="An outlaw who preys on travelers. Skilled in ambush tactics.",
        category=ThreatCategory.HUMANOID,
        primary_domains=[Domain.BODY, Domain.AWARENESS, Domain.CRAFT],
        weak_domains=[Domain.SPIRIT, Domain.AUTHORITY],
        resistant_domains=[],
        health_modifier=0.9,
        stamina_modifier=1.1,
        focus_modifier=1.0,
        spirit_modifier=0.8,
        move_behaviors=[
            MoveBehavior(
                name="Surprise Attack",
                description="A quick strike with bonus damage on first round",
                move_type=MoveType.TRICK,
                domains=[Domain.AWARENESS, Domain.BODY],
                priority=9,
                conditions={"first_round": True},
                special_effects=["BONUS_DAMAGE"]
            ),
            MoveBehavior(
                name="Dirty Fighting",
                description="Underhanded tactics that can stun",
                move_type=MoveType.TRICK,
                domains=[Domain.CRAFT, Domain.BODY],
                priority=7,
                conditions={"target_status": "!STUNNED"},
                special_effects=["STUN"]
            ),
            MoveBehavior(
                name="Tactical Retreat",
                description="Creates distance to reassess the situation",
                move_type=MoveType.UTILITY,
                domains=[Domain.AWARENESS],
                priority=6,
                conditions={"health_percent": "<30"},
                special_effects=["EVASION_BOOST"]
            )
        ],
        status_resistances=[],
        status_vulnerabilities=[Status.FRIGHTENED]
    )
    
    # Troll archetype (Beast category)
    troll_archetype = MonsterArchetype(
        id="troll",
        name="Troll",
        description="A large, brutish creature with natural regeneration abilities.",
        category=ThreatCategory.BEAST,
        primary_domains=[Domain.BODY],
        weak_domains=[Domain.MIND, Domain.SOCIAL],
        resistant_domains=[Domain.BODY],
        health_modifier=1.7,
        stamina_modifier=1.4,
        focus_modifier=0.5,
        spirit_modifier=0.7,
        move_behaviors=[
            MoveBehavior(
                name="Crushing Blow",
                description="A devastating attack with the troll's enormous strength",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                priority=8,
                conditions={},
                special_effects=["KNOCKDOWN"]
            ),
            MoveBehavior(
                name="Regeneration",
                description="The troll regenerates some of its wounds",
                move_type=MoveType.UTILITY,
                domains=[Domain.BODY, Domain.SPIRIT],
                priority=7,
                conditions={"health_percent": "<70"},
                special_effects=["HEAL"]
            ),
            MoveBehavior(
                name="Frenzied Attack",
                description="Multiple wild attacks with reduced accuracy",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                priority=6,
                conditions={"health_percent": "<40"},
                special_effects=["MULTIPLE_HITS", "ACCURACY_PENALTY"]
            )
        ],
        status_resistances=[Status.WOUNDED],
        status_vulnerabilities=[Status.STUNNED, Status.CONFUSED]
    )
    
    # Dragon archetype (Magical category)
    dragon_archetype = MonsterArchetype(
        id="dragon",
        name="Dragon",
        description="An ancient, powerful creature of magic and might. Commands respect and fear.",
        category=ThreatCategory.MAGICAL,
        primary_domains=[Domain.BODY, Domain.SPIRIT, Domain.AUTHORITY],
        weak_domains=[],
        resistant_domains=[Domain.BODY, Domain.SPIRIT, Domain.MIND],
        health_modifier=2.0,
        stamina_modifier=1.6,
        focus_modifier=1.5,
        spirit_modifier=1.8,
        move_behaviors=[
            MoveBehavior(
                name="Dragon Breath",
                description="A devastating breath attack",
                move_type=MoveType.FORCE,
                domains=[Domain.SPIRIT, Domain.BODY],
                priority=9,
                conditions={"cooldown": "3+"},
                special_effects=["AREA_EFFECT", "ELEMENTAL_EFFECT"]
            ),
            MoveBehavior(
                name="Terrifying Presence",
                description="The dragon's mere presence inspires terror",
                move_type=MoveType.UTILITY,
                domains=[Domain.AUTHORITY, Domain.SPIRIT],
                priority=8,
                conditions={"first_round": True},
                special_effects=["FEAR"]
            ),
            MoveBehavior(
                name="Ancient Wisdom",
                description="The dragon anticipates its opponent's moves",
                move_type=MoveType.FOCUS,
                domains=[Domain.MIND, Domain.AWARENESS],
                priority=7,
                conditions={"target_momentum": ">1"},
                special_effects=["COUNTER"]
            ),
            MoveBehavior(
                name="Tail Sweep",
                description="A powerful sweep affecting multiple opponents",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                priority=6,
                conditions={"multiple_opponents": True},
                special_effects=["AREA_EFFECT", "KNOCKDOWN"]
            )
        ],
        tier_adjustments={
            ThreatTier.LEGENDARY: {
                "health_modifier": 5.0,
                "stamina_modifier": 3.0,
                "focus_modifier": 3.0,
                "spirit_modifier": 4.0,
                "domain_bonus": 4,
                "special_ability": True,
                "legendary_action": True,
                "regeneration": True
            }
        },
        status_resistances=[Status.FRIGHTENED, Status.STUNNED],
        status_vulnerabilities=[]
    )
    
    # Mage archetype (Humanoid category)
    mage_archetype = MonsterArchetype(
        id="mage",
        name="Mage",
        description="A practitioner of arcane arts. Intelligent and skilled in magical combat.",
        category=ThreatCategory.HUMANOID,
        primary_domains=[Domain.MIND, Domain.SPIRIT, Domain.CRAFT],
        weak_domains=[Domain.BODY],
        resistant_domains=[Domain.MIND],
        health_modifier=0.7,
        stamina_modifier=0.8,
        focus_modifier=1.6,
        spirit_modifier=1.5,
        move_behaviors=[
            MoveBehavior(
                name="Arcane Bolt",
                description="A focused burst of magical energy",
                move_type=MoveType.FOCUS,
                domains=[Domain.MIND, Domain.SPIRIT],
                priority=8,
                conditions={"focus_percent": ">30"},
                special_effects=["ACCURACY_BONUS"]
            ),
            MoveBehavior(
                name="Magical Barrier",
                description="Creates a protective shield against attacks",
                move_type=MoveType.UTILITY,
                domains=[Domain.MIND, Domain.CRAFT],
                priority=7,
                conditions={"health_percent": "<70"},
                special_effects=["DAMAGE_REDUCTION"]
            ),
            MoveBehavior(
                name="Mind Control",
                description="Attempts to control the target's mind",
                move_type=MoveType.TRICK,
                domains=[Domain.MIND, Domain.SOCIAL],
                priority=6,
                conditions={"target_focus_percent": "<50"},
                special_effects=["CONFUSE", "CONTROL"]
            ),
            MoveBehavior(
                name="Teleport",
                description="Quickly relocates to escape danger",
                move_type=MoveType.UTILITY,
                domains=[Domain.MIND, Domain.SPIRIT],
                priority=9,
                conditions={"health_percent": "<30"},
                special_effects=["ESCAPE"]
            )
        ],
        status_resistances=[Status.CONFUSED],
        status_vulnerabilities=[Status.STUNNED, Status.EXHAUSTED]
    )
    
    # Register all archetypes
    MONSTER_ARCHETYPES["wolf"] = wolf_archetype
    MONSTER_ARCHETYPES["zombie"] = zombie_archetype
    MONSTER_ARCHETYPES["cultist"] = cultist_archetype
    MONSTER_ARCHETYPES["elemental"] = elemental_archetype
    MONSTER_ARCHETYPES["bandit"] = bandit_archetype
    MONSTER_ARCHETYPES["troll"] = troll_archetype
    MONSTER_ARCHETYPES["dragon"] = dragon_archetype
    MONSTER_ARCHETYPES["mage"] = mage_archetype


def create_monster_from_archetype(
    archetype_id: str,
    name: str,
    tier: ThreatTier = ThreatTier.STANDARD,
    level: int = 1,
    variant_type: str = None
) -> Tuple[Combatant, List[CombatMove]]:
    """
    Create a monster combatant from an archetype.
    
    Args:
        archetype_id: ID of the archetype to use
        name: Name of the monster
        tier: Threat tier of the monster
        level: Level of the monster
        variant_type: Optional variant type for customization
        
    Returns:
        Tuple containing (monster_combatant, available_moves)
    """
    # Make sure archetypes are initialized
    if not MONSTER_ARCHETYPES:
        _init_archetypes()
        
    # Get the archetype
    archetype = MONSTER_ARCHETYPES.get(archetype_id)
    if not archetype:
        raise ValueError(f"Monster archetype '{archetype_id}' not found")
        
    # Apply tier adjustments
    adjustments = archetype.apply_tier_adjustments(tier)
    
    # Calculate base stats
    base_health = 30 + (level * 10)
    base_stamina = 20 + (level * 5)
    base_focus = 15 + (level * 3)
    base_spirit = 15 + (level * 3)
    
    # Apply modifiers
    max_health = int(base_health * adjustments["health_modifier"])
    max_stamina = int(base_stamina * adjustments["stamina_modifier"])
    max_focus = int(base_focus * adjustments["focus_modifier"])
    max_spirit = int(base_spirit * adjustments["spirit_modifier"])
    
    # Create domain ratings
    domain_ratings = {}
    domain_bonus = adjustments.get("domain_bonus", 0)
    
    # Set base ratings for all domains
    for domain in Domain:
        if domain in archetype.primary_domains:
            # Primary domains start higher and scale better with level
            domain_ratings[domain] = min(10, 1 + int(level / 2) + domain_bonus)
        elif domain in archetype.resistant_domains:
            # Resistant domains have a moderate rating
            domain_ratings[domain] = min(8, 1 + int(level / 3) + domain_bonus)
        else:
            # Other domains start low
            domain_ratings[domain] = max(0, min(5, int(level / 4) + domain_bonus))
    
    # Create the combatant
    from .combat_system_core import CombatantType
    monster = Combatant(
        name=name,
        combatant_type=CombatantType.ENEMY,
        domain_ratings=domain_ratings,
        max_health=max_health,
        max_stamina=max_stamina,
        max_focus=max_focus,
        max_spirit=max_spirit
    )
    
    # Add weak/strong domains for targeting
    monster.weak_domains = archetype.weak_domains.copy() if archetype.weak_domains else []
    monster.strong_domains = archetype.primary_domains.copy() if archetype.primary_domains else []
    
    # Create moves based on behaviors
    available_moves = []
    if archetype.move_behaviors:
        for behavior in archetype.move_behaviors:
            # Create the move
            move = CombatMove(
                name=behavior.name,
                move_type=behavior.move_type,
                domains=behavior.domains,
                description=behavior.description,
                stamina_cost=2 if MoveType.FORCE in behavior.move_type else 1,
                focus_cost=2 if MoveType.FOCUS in behavior.move_type else 0,
                spirit_cost=1 if MoveType.UTILITY in behavior.move_type else 0
            )
            
            # Add to the monster's moves
            monster.add_move(move)
            available_moves.append(move)
    
    # Add generic moves if no specific moves are available
    if not available_moves:
        default_move = CombatMove(
            name="Attack",
            move_type=MoveType.FORCE,
            domains=[Domain.BODY],
            description="A basic attack",
            stamina_cost=1
        )
        monster.add_move(default_move)
        available_moves.append(default_move)
    
    return monster, available_moves


# Initialize the archetypes
_init_archetypes()