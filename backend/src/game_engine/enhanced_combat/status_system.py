"""
Status system for enhanced combat.

This module handles status effects and consequences in combat, 
providing richer combat outcomes beyond simple damage.
"""
from typing import List, Dict, Set, Optional, Any
from enum import Enum, auto
from dataclasses import dataclass

from .combat_system_core import Domain, Status, Consequence, Combatant

class StatusTier(Enum):
    """Tiers of status effect severity"""
    MINOR = auto()
    MODERATE = auto()
    SEVERE = auto()
    CRITICAL = auto()


class StatusSource(Enum):
    """Sources of status effects"""
    PHYSICAL = auto()
    MENTAL = auto()
    SPIRITUAL = auto()
    ENVIRONMENTAL = auto()
    MAGICAL = auto()
    SOCIAL = auto()


@dataclass
class EnhancedStatus:
    """
    Enhanced status effect with detailed properties.
    
    This extends the base Status enum with more detailed information
    about effect duration, intensity, and impact on gameplay.
    """
    name: str
    base_status: Status
    tier: StatusTier
    source: StatusSource
    duration: int  # In rounds
    description: str
    affected_domains: List[Domain]
    stat_modifiers: Dict[str, int]
    domain_modifiers: Dict[Domain, int]
    special_effects: List[str]
    
    def apply_to_combatant(self, combatant: Combatant) -> Dict[str, Any]:
        """
        Apply this status to a combatant.
        
        Args:
            combatant: The combatant to apply the status to
            
        Returns:
            Dictionary with results of status application
        """
        # Add base status
        combatant.statuses.add(self.base_status)
        
        # Apply stat modifiers if tracking enhanced statuses
        if not hasattr(combatant, 'enhanced_statuses'):
            combatant.enhanced_statuses = []
        
        # Add to enhanced statuses list
        combatant.enhanced_statuses.append(self)
        
        # Apply immediate effects
        self._apply_stat_modifiers(combatant)
        
        return {
            "status_applied": self.name,
            "duration": self.duration,
            "tier": self.tier.name,
            "affected_domains": [d.value for d in self.affected_domains],
            "special_effects": self.special_effects
        }
        
    def _apply_stat_modifiers(self, combatant: Combatant) -> None:
        """
        Apply stat modifiers from this status.
        
        Args:
            combatant: The combatant to apply modifiers to
        """
        for stat, modifier in self.stat_modifiers.items():
            if stat == "stamina_regen":
                # Would be applied during stamina regeneration
                pass
            elif stat == "max_stamina":
                # Temporarily modify max stamina
                combatant.max_stamina = max(1, combatant.max_stamina + modifier)
                # Also adjust current stamina if it's now above max
                combatant.current_stamina = min(combatant.current_stamina, combatant.max_stamina)
            elif stat == "max_health":
                # Temporarily modify max health
                combatant.max_health = max(1, combatant.max_health + modifier)
                # Also adjust current health if it's now above max
                combatant.current_health = min(combatant.current_health, combatant.max_health)
            elif stat == "max_focus":
                # Temporarily modify max focus
                combatant.max_focus = max(1, combatant.max_focus + modifier)
                # Also adjust current focus if it's now above max
                combatant.current_focus = min(combatant.current_focus, combatant.max_focus)
            elif stat == "max_spirit":
                # Temporarily modify max spirit
                combatant.max_spirit = max(1, combatant.max_spirit + modifier)
                # Also adjust current spirit if it's now above max
                combatant.current_spirit = min(combatant.current_spirit, combatant.max_spirit)
    
    def get_domain_modifier(self, domain: Domain) -> int:
        """
        Get modifier for a specific domain from this status.
        
        Args:
            domain: The domain to get modifier for
            
        Returns:
            The modifier value
        """
        return self.domain_modifiers.get(domain, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation for API responses.
        
        Returns:
            Dictionary representation of this status
        """
        return {
            "name": self.name,
            "base_status": self.base_status.value,
            "tier": self.tier.name,
            "source": self.source.name,
            "duration": self.duration,
            "description": self.description,
            "affected_domains": [d.value for d in self.affected_domains],
            "special_effects": self.special_effects
        }


class StatusFactory:
    """Factory for creating standard enhanced statuses"""
    
    @staticmethod
    def create_wounded(tier: StatusTier = StatusTier.MODERATE) -> EnhancedStatus:
        """
        Create a wounded status with appropriate tier.
        
        Args:
            tier: The severity tier of the wound
            
        Returns:
            An EnhancedStatus object
        """
        if tier == StatusTier.MINOR:
            return EnhancedStatus(
                name="Lightly Wounded",
                base_status=Status.WOUNDED,
                tier=tier,
                source=StatusSource.PHYSICAL,
                duration=3,
                description="A minor wound that hampers physical activity",
                affected_domains=[Domain.BODY],
                stat_modifiers={"stamina_regen": -1},
                domain_modifiers={Domain.BODY: -1},
                special_effects=[]
            )
        elif tier == StatusTier.MODERATE:
            return EnhancedStatus(
                name="Wounded",
                base_status=Status.WOUNDED,
                tier=tier,
                source=StatusSource.PHYSICAL,
                duration=4,
                description="A significant wound that limits movement",
                affected_domains=[Domain.BODY, Domain.AWARENESS],
                stat_modifiers={"stamina_regen": -1, "max_stamina": -10},
                domain_modifiers={Domain.BODY: -1, Domain.AWARENESS: -1},
                special_effects=["May leave blood trail"]
            )
        elif tier == StatusTier.SEVERE:
            return EnhancedStatus(
                name="Severely Wounded",
                base_status=Status.WOUNDED,
                tier=tier,
                source=StatusSource.PHYSICAL,
                duration=6,
                description="A severe wound that greatly impairs function",
                affected_domains=[Domain.BODY, Domain.AWARENESS, Domain.CRAFT],
                stat_modifiers={"stamina_regen": -2, "max_stamina": -20},
                domain_modifiers={Domain.BODY: -2, Domain.AWARENESS: -1, Domain.CRAFT: -1},
                special_effects=["Bleeding: Take 3 damage each round", "Visible weakness: Enemies target you more"]
            )
        else:  # CRITICAL
            return EnhancedStatus(
                name="Critically Wounded",
                base_status=Status.WOUNDED,
                tier=tier,
                source=StatusSource.PHYSICAL,
                duration=8,
                description="A life-threatening wound that severely impairs all function",
                affected_domains=[Domain.BODY, Domain.AWARENESS, Domain.CRAFT, Domain.MIND],
                stat_modifiers={"stamina_regen": -3, "max_stamina": -30, "max_focus": -20},
                domain_modifiers={Domain.BODY: -3, Domain.AWARENESS: -2, Domain.CRAFT: -2, Domain.MIND: -1},
                special_effects=["Heavy Bleeding: Take 5 damage each round", 
                                "Shock: 20% chance to lose a turn",
                                "Requires immediate medical attention"]
            )
    
    @staticmethod
    def create_confused(tier: StatusTier = StatusTier.MODERATE) -> EnhancedStatus:
        """
        Create a confused status with appropriate tier.
        
        Args:
            tier: The severity tier of the confusion
            
        Returns:
            An EnhancedStatus object
        """
        if tier == StatusTier.MINOR:
            return EnhancedStatus(
                name="Slightly Confused",
                base_status=Status.CONFUSED,
                tier=tier,
                source=StatusSource.MENTAL,
                duration=2,
                description="Momentarily disoriented",
                affected_domains=[Domain.MIND],
                stat_modifiers={"focus_regen": -1},
                domain_modifiers={Domain.MIND: -1},
                special_effects=[]
            )
        elif tier == StatusTier.MODERATE:
            return EnhancedStatus(
                name="Confused",
                base_status=Status.CONFUSED,
                tier=tier,
                source=StatusSource.MENTAL,
                duration=3,
                description="Disoriented and having trouble focusing",
                affected_domains=[Domain.MIND, Domain.AWARENESS],
                stat_modifiers={"focus_regen": -1, "max_focus": -10},
                domain_modifiers={Domain.MIND: -2, Domain.AWARENESS: -1},
                special_effects=["10% chance to use wrong move"]
            )
        elif tier == StatusTier.SEVERE:
            return EnhancedStatus(
                name="Severely Confused",
                base_status=Status.CONFUSED,
                tier=tier,
                source=StatusSource.MENTAL,
                duration=4,
                description="Severely disoriented and unable to think clearly",
                affected_domains=[Domain.MIND, Domain.AWARENESS, Domain.SOCIAL],
                stat_modifiers={"focus_regen": -2, "max_focus": -20},
                domain_modifiers={Domain.MIND: -3, Domain.AWARENESS: -2, Domain.SOCIAL: -1},
                special_effects=["20% chance to use wrong move", "Cannot use Focus move types"]
            )
        else:  # CRITICAL
            return EnhancedStatus(
                name="Delirious",
                base_status=Status.CONFUSED,
                tier=tier,
                source=StatusSource.MENTAL,
                duration=5,
                description="Completely disoriented and unable to function properly",
                affected_domains=[Domain.MIND, Domain.AWARENESS, Domain.SOCIAL, Domain.CRAFT],
                stat_modifiers={"focus_regen": -3, "max_focus": -30, "max_stamina": -10},
                domain_modifiers={Domain.MIND: -4, Domain.AWARENESS: -3, Domain.SOCIAL: -2, Domain.CRAFT: -1},
                special_effects=["30% chance to use wrong move", 
                                "Cannot use Focus move types",
                                "20% chance to lose turn"]
            )
    
    # Add more factory methods for other status types as needed


class ConsequenceSystem:
    """Enhanced system for handling long-term consequences"""
    
    @staticmethod
    def create_consequence_from_combat(result: dict, target: Combatant, 
                                       status: EnhancedStatus = None) -> Optional[Consequence]:
        """
        Create a lasting consequence based on combat result and status.
        
        Args:
            result: Combat result dictionary
            target: The target combatant
            status: Optional enhanced status that may influence the consequence
            
        Returns:
            A Consequence object or None if no consequence is created
        """
        if not result.get("actor_success", False) or result.get("effect_magnitude", 0) < 3:
            return None
            
        # Base consequence severity on effect magnitude and status
        severity = result.get("effect_magnitude", 0)
        if status and status.tier == StatusTier.SEVERE:
            severity += 2
        elif status and status.tier == StatusTier.CRITICAL:
            severity += 4
            
        # Determine affected domains
        affected_domains = []
        if status:
            affected_domains = status.affected_domains.copy()
        elif "domains" in result:
            affected_domains = result["domains"]
        
        # Generate appropriate consequence
        if severity >= 8:
            # Major permanent consequence
            desc = f"Permanent injury from {result.get('actor_move', 'attack')}"
            hook = f"The {result.get('actor_move', 'attack')} left a permanent scar, both physically and mentally"
            return Consequence(
                description=desc,
                affected_domains=affected_domains,
                duration=-1,  # Permanent
                intensity=4,
                narrative_hook=hook,
                affected_stats={"max_health": -10, "stamina_regen": -1}
            )
        elif severity >= 5:
            # Major consequence
            desc = f"Serious injury from {result.get('actor_move', 'attack')}"
            hook = f"The {result.get('actor_move', 'attack')} left a lasting mark"
            return Consequence(
                description=desc,
                affected_domains=affected_domains,
                duration=5,
                intensity=3,
                narrative_hook=hook,
                affected_stats={"stamina_regen": -1}
            )
        else:
            # Minor consequence
            desc = f"Minor injury from {result.get('actor_move', 'attack')}"
            hook = f"Still feeling the effects of the {result.get('actor_move', 'attack')}"
            return Consequence(
                description=desc,
                affected_domains=affected_domains,
                duration=2,
                intensity=1,
                narrative_hook=hook
            )