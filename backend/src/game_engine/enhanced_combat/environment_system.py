"""
Environment system for enhanced combat.

This module handles environmental interactions and effects in combat,
adding tactical depth beyond direct combatant interactions.
"""
from typing import Set, Dict, List, Tuple, Any, Optional
from enum import Enum

from .combat_system_core import Domain, MoveType, CombatMove, Combatant


class EnvironmentElement(Enum):
    """Common environment elements that affect combat"""
    WATER = "Water"
    FIRE = "Fire"
    HIGH_GROUND = "High Ground"
    DARKNESS = "Darkness"
    CONFINED_SPACE = "Confined Space"
    OPEN_FIELD = "Open Field"
    MAGICAL_AURA = "Magical Aura"
    RUINS = "Ruins"
    FOREST = "Forest"
    URBAN = "Urban"
    UNSTABLE = "Unstable Ground"


class EnvironmentInteraction:
    """
    Represents a possible interaction with the environment.
    
    These are dynamically available based on the current environment tags.
    """
    def __init__(self, 
                name: str, 
                description: str, 
                requirements: Dict[str, Any] = None, 
                effects: Dict[str, Any] = None):
        """
        Initialize an environment interaction.
        
        Args:
            name: Name of the interaction
            description: Description of the interaction
            requirements: Requirements to perform this interaction
            effects: Effects when this interaction is performed
        """
        self.name = name
        self.description = description
        self.requirements = requirements or {}  # Domain requirements, etc.
        self.effects = effects or {}  # Effects on combat
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation for API responses.
        
        Returns:
            Dictionary representation of this interaction
        """
        return {
            "name": self.name,
            "description": self.description,
            "requirements": self.requirements,
            "effects": self.effects
        }


class EnvironmentSystem:
    """
    System for handling environment interactions in combat.
    
    This tracks the current environment, available interactions,
    and provides methods to apply environmental modifiers to actions.
    """
    def __init__(self):
        """Initialize the environment system"""
        self.environment_tags: Set[str] = set()
        self.available_interactions: Dict[str, EnvironmentInteraction] = {}
        
    def add_environment_tag(self, tag: str) -> None:
        """
        Add an environment tag to the current scene.
        
        Args:
            tag: The tag to add
        """
        self.environment_tags.add(tag)
        # Update available interactions based on new tag
        self._update_available_interactions()
        
    def remove_environment_tag(self, tag: str) -> None:
        """
        Remove an environment tag from the current scene.
        
        Args:
            tag: The tag to remove
        """
        if tag in self.environment_tags:
            self.environment_tags.remove(tag)
            # Update available interactions after removal
            self._update_available_interactions()
    
    def set_environment_tags(self, tags: List[str]) -> None:
        """
        Set the environment tags for the current scene.
        
        Args:
            tags: List of environment tags
        """
        self.environment_tags = set(tags)
        self._update_available_interactions()
    
    def _update_available_interactions(self) -> None:
        """Update available interactions based on current environment tags"""
        self.available_interactions = {}
        
        # Water interactions
        if "Water" in self.environment_tags:
            self.available_interactions["splash_water"] = EnvironmentInteraction(
                name="Splash Water",
                description="Splash water to distract or obscure vision",
                requirements={"domain": Domain.AWARENESS},
                effects={"target_penalty": -1, "narrative": "Water obscures vision"}
            )
        
        # Fire interactions
        if "Fire" in self.environment_tags:
            self.available_interactions["use_flames"] = EnvironmentInteraction(
                name="Use Flames",
                description="Use nearby flames as a weapon or distraction",
                requirements={"domain": Domain.CRAFT},
                effects={"damage_bonus": 3, "narrative": "Flames burn the target"}
            )
        
        # High Ground interactions
        if "High Ground" in self.environment_tags:
            self.available_interactions["tactical_advantage"] = EnvironmentInteraction(
                name="Tactical Advantage",
                description="Use high ground for combat advantage",
                requirements={"domain": Domain.AWARENESS},
                effects={"roll_bonus": 2, "narrative": "The high ground provides advantage"}
            )
            
        # Darkness interactions
        if "Darkness" in self.environment_tags:
            self.available_interactions["stealth_approach"] = EnvironmentInteraction(
                name="Stealth Approach", 
                description="Use the darkness to move unseen",
                requirements={"domain": Domain.AWARENESS},
                effects={"surprise_bonus": True, "narrative": "Darkness conceals your approach"}
            )
            
        # Confined Space interactions  
        if "Confined Space" in self.environment_tags:
            self.available_interactions["cornered_defense"] = EnvironmentInteraction(
                name="Cornered Defense",
                description="Use the confined space to limit enemy attack options",
                requirements={"domain": Domain.AWARENESS},
                effects={"defense_bonus": 2, "narrative": "The confined space limits attack options"}
            )
            
        # Open Field interactions
        if "Open Field" in self.environment_tags:
            self.available_interactions["charge"] = EnvironmentInteraction(
                name="Charge",
                description="Build momentum with a charging attack",
                requirements={"domain": Domain.BODY},
                effects={"damage_bonus": 3, "narrative": "You build momentum across the open field"}
            )
            
        # Magical Aura interactions
        if "Magical Aura" in self.environment_tags:
            self.available_interactions["channel_energy"] = EnvironmentInteraction(
                name="Channel Energy",
                description="Channel the ambient magical energy",
                requirements={"domain": Domain.SPIRIT},
                effects={"magic_bonus": 3, "narrative": "You channel the ambient magical energy"}
            )
            
        # Ruins interactions
        if "Ruins" in self.environment_tags:
            self.available_interactions["use_debris"] = EnvironmentInteraction(
                name="Use Debris",
                description="Use debris from the ruins as improvised weapons",
                requirements={"domain": Domain.CRAFT},
                effects={"damage_bonus": 2, "narrative": "You use debris as improvised weapons"}
            )
            self.available_interactions["collapse_structure"] = EnvironmentInteraction(
                name="Collapse Structure",
                description="Cause a weak structure to collapse on enemies",
                requirements={"domain": Domain.BODY, "damage_threshold": 10},
                effects={"aoe_damage": 5, "narrative": "The structure collapses on your enemies"}
            )
            
        # Forest interactions
        if "Forest" in self.environment_tags:
            self.available_interactions["take_cover"] = EnvironmentInteraction(
                name="Take Cover",
                description="Use trees for cover",
                requirements={"domain": Domain.AWARENESS},
                effects={"defense_bonus": 2, "narrative": "The trees provide cover"}
            )
            
        # Urban interactions
        if "Urban" in self.environment_tags:
            self.available_interactions["use_surroundings"] = EnvironmentInteraction(
                name="Use Surroundings",
                description="Use urban surroundings to your advantage",
                requirements={"domain": Domain.AWARENESS},
                effects={"versatile_bonus": True, "narrative": "You use the urban environment to your advantage"}
            )
            
        # Unstable Ground interactions
        if "Unstable Ground" in self.environment_tags:
            self.available_interactions["destabilize_footing"] = EnvironmentInteraction(
                name="Destabilize Footing",
                description="Cause your opponent to lose balance on unstable ground",
                requirements={"domain": Domain.AWARENESS},
                effects={"target_penalty": -2, "narrative": "Your opponent loses their footing"}
            )
    
    def get_available_interactions(self) -> List[EnvironmentInteraction]:
        """
        Get list of available environmental interactions.
        
        Returns:
            List of available interactions
        """
        return list(self.available_interactions.values())
    
    def get_available_interactions_for_domain(self, domain: Domain) -> List[EnvironmentInteraction]:
        """
        Get available interactions for a specific domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            List of available interactions for this domain
        """
        interactions = []
        for interaction in self.available_interactions.values():
            if 'domain' in interaction.requirements and interaction.requirements['domain'] == domain:
                interactions.append(interaction)
        return interactions
    
    def get_interaction(self, interaction_id: str) -> Optional[EnvironmentInteraction]:
        """
        Get an interaction by ID.
        
        Args:
            interaction_id: The ID of the interaction
            
        Returns:
            The interaction or None if not found
        """
        return self.available_interactions.get(interaction_id)
    
    def apply_environment_modifiers(self, move: CombatMove, actor: Combatant) -> Tuple[int, List[str]]:
        """
        Calculate environment-based modifiers for a move.
        
        Args:
            move: The move being performed
            actor: The actor performing the move
            
        Returns:
            Tuple containing (roll_modifier, narrative_hooks)
        """
        roll_modifier = 0
        narrative_hooks = []
        
        # Apply modifiers based on environment tags and domains
        for domain in move.domains:
            # Awareness in darkness
            if domain == Domain.AWARENESS and "Darkness" in self.environment_tags:
                if hasattr(actor, 'strong_domains') and Domain.AWARENESS in actor.strong_domains:
                    roll_modifier += 2
                    narrative_hooks.append("Expertly navigates the darkness")
                else:
                    roll_modifier -= 1
                    narrative_hooks.append("Struggles to perceive in darkness")
            
            # Body in confined spaces
            if domain == Domain.BODY and "Confined Space" in self.environment_tags:
                roll_modifier -= 1
                narrative_hooks.append("Limited movement in the confined space")
            
            # Mind in magical aura
            if domain == Domain.MIND and "Magical Aura" in self.environment_tags:
                if Domain.SPIRIT in move.domains:
                    roll_modifier += 2
                    narrative_hooks.append("Channels the ambient magical energy")
                
            # Authority in open field
            if domain == Domain.AUTHORITY and "Open Field" in self.environment_tags:
                roll_modifier += 1
                narrative_hooks.append("Voice carries powerfully across the field")
                
            # Craft in ruins
            if domain == Domain.CRAFT and "Ruins" in self.environment_tags:
                roll_modifier += 1
                narrative_hooks.append("Uses scattered debris as improvised tools")
                
            # Social in urban
            if domain == Domain.SOCIAL and "Urban" in self.environment_tags:
                roll_modifier += 1
                narrative_hooks.append("Urban setting enhances social dynamics")
                
            # Body on unstable ground
            if domain == Domain.BODY and "Unstable Ground" in self.environment_tags:
                roll_modifier -= 1
                narrative_hooks.append("Struggles to maintain balance on unstable ground")
                
            # Spirit in forest
            if domain == Domain.SPIRIT and "Forest" in self.environment_tags:
                roll_modifier += 1
                narrative_hooks.append("Connects with the natural spirits of the forest")
                
            # Body with high ground
            if domain == Domain.BODY and "High Ground" in self.environment_tags:
                roll_modifier += 1
                narrative_hooks.append("Leverages the high ground")
                
            # Body with water
            if domain == Domain.BODY and "Water" in self.environment_tags:
                roll_modifier -= 1  
                narrative_hooks.append("Movement is slowed by water")
                
            # Body with fire
            if domain == Domain.BODY and "Fire" in self.environment_tags:
                # Check if this is a fire-related move
                if "fire" in move.name.lower() or "flame" in move.name.lower():
                    roll_modifier += 2
                    narrative_hooks.append("The surrounding fire enhances the attack")
                
        return roll_modifier, narrative_hooks
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert environment state to dictionary for API responses.
        
        Returns:
            Dictionary representation of environment state
        """
        return {
            "environment_tags": list(self.environment_tags),
            "available_interactions": [interaction.to_dict() for interaction in self.available_interactions.values()]
        }


# Create a global instance
environment_system = EnvironmentSystem()