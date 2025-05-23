"""
AI GM Brain - Complete Integration

This module provides a complete integration of all AI GM Brain components
into a single cohesive system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import core brain and components
from .ai_gm_brain import AIGMBrain, get_ai_gm_brain, ProcessingMode
from .ai_gm_brain_ooc_integration import extend_ai_gm_brain_with_ooc
from .ai_gm_combat_integration import extend_ai_gm_brain_with_combat
from .ai_gm_decision_logic import extend_ai_gm_brain_with_decision_logic
from .ai_gm_narrative_generator import extend_ai_gm_brain_with_narrative
from .ai_gm_llm_manager import extend_ai_gm_brain_with_llm


class AIGMBrainFull:
    """
    Complete integration of all AI GM Brain components.
    
    This class provides a unified interface to all AI GM Brain functionality,
    configured and connected to work together seamlessly.
    """
    
    def __init__(self, game_id: str, player_id: str):
        """
        Initialize the full AI GM Brain.
        
        Args:
            game_id: Game session ID
            player_id: Player character ID
        """
        # Setup logging
        self.logger = logging.getLogger(f"AIGMBrainFull_{game_id}")
        
        # Get the core brain
        self.brain = get_ai_gm_brain(game_id, player_id)
        
        # Extend with all components
        self._extend_with_all_components()
        
        self.logger.info(f"Full AI GM Brain initialized for game {game_id}")
    
    def _extend_with_all_components(self) -> None:
        """Extend the core brain with all components."""
        # Add OOC command handling
        extend_ai_gm_brain_with_ooc(self.brain)
        self.logger.debug("OOC command handling added")
        
        # Add decision logic
        extend_ai_gm_brain_with_decision_logic(self.brain)
        self.logger.debug("Decision logic added")
        
        # Add narrative generation
        extend_ai_gm_brain_with_narrative(self.brain)
        self.logger.debug("Narrative generation added")
        
        # Add combat integration
        extend_ai_gm_brain_with_combat(self.brain)
        self.logger.debug("Combat integration added")
        
        # Add LLM integration (commented out for Phase 1)
        # extend_ai_gm_brain_with_llm(self.brain)
        # self.logger.debug("LLM integration added")
    
    def process_input(self, input_string: str) -> Dict[str, Any]:
        """
        Process player input through the AI GM Brain.
        
        Args:
            input_string: Raw text input from the player
            
        Returns:
            Response data dictionary
        """
        return self.brain.process_player_input(input_string)
    
    def start_combat(self, monster_id: str) -> Dict[str, Any]:
        """
        Start combat with a monster.
        
        Args:
            monster_id: ID of the monster to fight
            
        Returns:
            Combat start response data
        """
        if hasattr(self.brain, 'combat_integration'):
            return self.brain.combat_integration.start_combat(monster_id)
        else:
            return {
                "error": True,
                "response_text": "Combat integration not available"
            }
    
    def end_combat(self, result: str = "unknown") -> Dict[str, Any]:
        """
        End the current combat encounter.
        
        Args:
            result: Result of the combat (victory, defeat, flee)
            
        Returns:
            Combat end response data
        """
        if hasattr(self.brain, 'combat_integration'):
            return self.brain.combat_integration.end_combat(result)
        else:
            return {
                "error": True,
                "response_text": "Combat integration not available"
            }
    
    def generate_location_description(self, 
                                    location_type: str,
                                    details: Dict[str, Any] = {}) -> str:
        """
        Generate a description for a location.
        
        Args:
            location_type: Type of location (forest, city, etc.)
            details: Additional details about the location
            
        Returns:
            A rich location description
        """
        if hasattr(self.brain, 'narrative_generator'):
            return self.brain.narrative_generator.generate_location_description(
                location_type, details
            )
        else:
            return f"You are in a {location_type}."
    
    def generate_npc_dialogue(self, 
                            npc_name: str,
                            disposition: str = "neutral",
                            dialogue_content: str = "") -> str:
        """
        Generate dialogue for an NPC.
        
        Args:
            npc_name: Name of the NPC
            disposition: Disposition towards player (friendly, hostile, etc.)
            dialogue_content: The content of what the NPC wants to say
            
        Returns:
            Formatted NPC dialogue with narration
        """
        if hasattr(self.brain, 'narrative_generator'):
            return self.brain.narrative_generator.generate_npc_dialogue(
                npc_name, disposition, dialogue_content
            )
        else:
            return f"{npc_name} says: \"{dialogue_content}\""
    
    def make_narrative_decision(self, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Make a decision about narrative direction.
        
        Args:
            context: Context information for the decision
            
        Returns:
            Decision result
        """
        if hasattr(self.brain, 'decision_logic'):
            decision = self.brain.decision_logic.make_narrative_direction_decision(context)
            return {
                "selected": decision.selected,
                "confidence": decision.confidence,
                "choices": decision.choices
            }
        else:
            return {
                "error": True,
                "response_text": "Decision logic not available"
            }
    
    def adjust_narrative_tension(self, amount: float) -> None:
        """
        Adjust narrative tension level.
        
        Args:
            amount: Amount to adjust tension by (positive or negative)
        """
        if hasattr(self.brain, 'narrative_generator'):
            self.brain.narrative_generator.adjust_tension(amount)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the AI GM Brain.
        
        Returns:
            Dictionary of statistics
        """
        stats = {
            "core": self.brain.get_processing_statistics(),
            "components": {
                "ooc": hasattr(self.brain, 'ooc_integration'),
                "combat": hasattr(self.brain, 'combat_integration'),
                "decision": hasattr(self.brain, 'decision_logic'),
                "narrative": hasattr(self.brain, 'narrative_generator'),
                "llm": hasattr(self.brain, 'llm_manager')
            }
        }
        
        # Add component-specific stats if available
        if hasattr(self.brain, 'llm_manager'):
            stats["llm"] = self.brain.llm_manager.get_usage_statistics()
        
        return stats


# Singleton instance pattern
_ai_gm_brain_full = None

def get_ai_gm_brain_full(game_id: str, player_id: str) -> AIGMBrainFull:
    """
    Get or create the full AI GM Brain instance.
    
    Args:
        game_id: Game session ID
        player_id: Player character ID
        
    Returns:
        AIGMBrainFull instance
    """
    global _ai_gm_brain_full
    if _ai_gm_brain_full is None:
        _ai_gm_brain_full = AIGMBrainFull(game_id, player_id)
    return _ai_gm_brain_full