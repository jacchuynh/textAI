"""
Combat controller for the enhanced combat system.

This module provides the main interface for resolving combat
encounters between combatants, applying domain-based mechanics,
and generating narrative descriptions of combat.
"""
from typing import Dict, List, Any, Optional, Tuple
import random
from datetime import datetime

from .combat_system_core import Combatant, CombatMove, Status, MoveType, Domain


class CombatController:
    """
    Main controller for combat resolution.
    
    This class handles the mechanics of resolving combat exchanges,
    calculating damage, applying status effects, and generating
    narrative descriptions.
    """
    
    def __init__(self,
                 environment_name: str = "Neutral Ground",
                 environment_effects: Dict[str, Any] = None,
                 combat_id: str = None,
                 round_number: int = 1,
                 tags: List[str] = None,
                 narrative_style: str = "Standard",
                 log_results: bool = True):
        """
        Initialize the combat controller.
        
        Args:
            environment_name: Name of the combat environment
            environment_effects: Special effects of the environment
            combat_id: Unique identifier for this combat encounter
            round_number: Current round number
            tags: Tags that apply to this combat encounter
            narrative_style: Style of narrative generation
            log_results: Whether to log combat results
        """
        self.environment_name = environment_name
        self.environment_effects = environment_effects or {}
        self.combat_id = combat_id or f"combat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.round_number = round_number
        self.tags = tags or []
        self.narrative_style = narrative_style
        self.log_results = log_results
        
        # Combat history
        self.history = []
    
    def resolve_combat_exchange(self,
                               actor_name: str,
                               actor_move: CombatMove,
                               target_name: str,
                               target_move: CombatMove) -> Dict[str, Any]:
        """
        Resolve a combat exchange between two combatants.
        
        Args:
            actor_name: Name of the acting combatant
            actor_move: CombatMove for the actor
            target_name: Name of the target combatant
            target_move: CombatMove for the target
            
        Returns:
            Dictionary with combat results and narrative
        """
        # This is a simplified version for testing - in real implementation
        # this would use the damage calculation, status system, etc.
        
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
        
        # Apply damage to combatants (we would look them up in a real implementation)
        # For this test, we'll create dummy combatants
        actor = self._get_dummy_combatant(actor_name)
        target = self._get_dummy_combatant(target_name)
        
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
        if self.log_results:
            self.history.append(result)
            self.round_number += 1
        
        return result
    
    def _calculate_simple_damage(self, move: CombatMove) -> int:
        """Calculate a simple damage value for a move"""
        # Base damage plus small random variation
        base = move.base_damage
        variation = random.randint(-2, 2)
        return max(0, base + variation)
    
    def _get_dummy_combatant(self, name: str) -> Combatant:
        """Create a dummy combatant for testing"""
        domains = {domain: random.randint(1, 5) for domain in Domain}
        
        return Combatant(
            name=name,
            domains=domains,
            max_health=50,
            current_health=50,
            max_stamina=30,
            current_stamina=30,
            max_focus=30,
            current_focus=30,
            max_spirit=30,
            current_spirit=30
        )
    
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
        # This would normally use a more sophisticated narrative generator
        # For testing, we'll use a template-based approach
        
        templates = [
            f"{actor_name} used {actor_move.name}, while {target_name} responded with {target_move.name}. "
            f"The exchange ended with {actor_name} dealing {actor_damage} damage and taking {target_damage} damage.",
            
            f"As {actor_name} unleashed {actor_move.name}, {target_name} countered with {target_move.name}. "
            f"{actor_name} inflicted {actor_damage} damage, while suffering {target_damage} in return.",
            
            f"{actor_name}'s {actor_move.name} clashed with {target_name}'s {target_move.name} in the {self.environment_name}. "
            f"When the dust settled, {actor_name} had dealt {actor_damage} damage and received {target_damage}."
        ]
        
        return random.choice(templates)