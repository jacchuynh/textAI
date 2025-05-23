"""
World Reaction System Integration for AI GM Brain

This module integrates the world reaction system with the AI GM Brain,
allowing NPCs and the environment to react appropriately to player actions.
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

# Add the assets directory to path to allow importing world reaction components
sys.path.insert(0, 'attached_assets')

try:
    from world_reaction.enhanced_context_manager import EnhancedContextManager
    from world_reaction.reaction_assessor import ReactionAssessor
    from world_reaction.reputation_manager import ReputationManager, ReputationLevel, ActionSignificance
    
    WORLD_REACTION_AVAILABLE = True
except ImportError:
    WORLD_REACTION_AVAILABLE = False
    print("World reaction system components not available.")


class WorldReactionIntegration:
    """Integration module for the world reaction system with AI GM Brain."""
    
    def __init__(self, brain):
        """
        Initialize the world reaction integration.
        
        Args:
            brain: The AI GM Brain instance to integrate with
        """
        self.brain = brain
        self.enabled = WORLD_REACTION_AVAILABLE
        
        if not self.enabled:
            return
            
        # Initialize the reputation manager
        self.reputation_manager = ReputationManager()
        
        # Initialize the enhanced context manager
        self.context_manager = EnhancedContextManager(
            reputation_manager=self.reputation_manager
        )
        
        # Initialize reaction assessor (will need LLM integration later)
        self.reaction_assessor = None
        
        # Try to initialize with mock LLM for testing
        class MockLLMManager:
            async def call_llm_with_tracking(self, **kwargs):
                return {
                    "success": True,
                    "content": '{"reaction_type": "neutral", "intensity": 0.5, "response": "The barkeeper nods briefly."}'
                }
                
            def get_optimal_model(self, *args, **kwargs):
                return "mock-model"
                
        try:
            self.reaction_assessor = ReactionAssessor(
                llm_manager=MockLLMManager()
            )
        except Exception as e:
            print(f"Could not initialize reaction assessor: {e}")
    
    def is_enabled(self) -> bool:
        """Check if the world reaction system is enabled."""
        return self.enabled
    
    def get_enhanced_context(self, player_id: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get enhanced context with world reaction data.
        
        Args:
            player_id: The ID of the player
            base_context: The base context to enhance
            
        Returns:
            Enhanced context with world reaction data
        """
        if not self.enabled:
            return base_context
            
        return self.context_manager.enhance_context(player_id, base_context)
    
    def record_player_action(self, 
                           player_id: str, 
                           action_description: str,
                           target_entity_id: Optional[str] = None,
                           significance: ActionSignificance = ActionSignificance.MINOR,
                           domain_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Record a player action for reputation tracking.
        
        Args:
            player_id: The ID of the player
            action_description: Description of the action
            target_entity_id: Optional ID of the target entity (NPC, faction, etc.)
            significance: The significance of the action
            domain_tags: Optional list of domain tags for the action
            
        Returns:
            Result of recording the action
        """
        if not self.enabled:
            return {"status": "disabled"}
            
        try:
            return self.reputation_manager.record_action(
                player_id=player_id,
                action_description=action_description,
                target_entity_id=target_entity_id,
                significance=significance,
                domain_tags=domain_tags or []
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def assess_reaction(self, 
                            player_id: str,
                            player_input: str,
                            context: Dict[str, Any],
                            target_entity: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess how the world/NPCs should react to player input.
        
        Args:
            player_id: The ID of the player
            player_input: The player's input text
            context: The current game context
            target_entity: Optional specific entity to assess reaction for
            
        Returns:
            Assessment result with reaction data
        """
        if not self.enabled or not self.reaction_assessor:
            return {
                "success": False,
                "reaction_data": {
                    "reaction_type": "neutral",
                    "intensity": 0.5,
                    "response": "The world continues as normal."
                }
            }
            
        try:
            # Enhance context first
            enhanced_context = self.get_enhanced_context(player_id, context)
            
            # Assess reaction
            reaction_result = await self.reaction_assessor.assess_reaction(
                player_input=player_input,
                context=enhanced_context,
                target_entity=target_entity
            )
            
            return {
                "success": True,
                "reaction_data": reaction_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "reaction_data": {
                    "reaction_type": "neutral",
                    "intensity": 0.5,
                    "response": "The world continues as normal."
                }
            }
    
    def get_entity_relationship(self, player_id: str, entity_id: str) -> Dict[str, Any]:
        """
        Get the relationship between a player and an entity.
        
        Args:
            player_id: The ID of the player
            entity_id: The ID of the entity
            
        Returns:
            Relationship data including reputation level
        """
        if not self.enabled:
            return {"status": "disabled", "level": "neutral"}
            
        try:
            reputation = self.reputation_manager.get_reputation_with_entity(
                player_id=player_id,
                entity_id=entity_id
            )
            
            return {
                "status": "success",
                "level": reputation.reputation_level.value,
                "score": reputation.reputation_score,
                "recent_actions": len(reputation.recent_actions),
                "last_interaction": reputation.last_interaction.isoformat() 
                    if reputation.last_interaction else None
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "level": "neutral"}


def attach_to_brain(brain):
    """
    Attach the world reaction system to the AI GM Brain.
    
    Args:
        brain: The AI GM Brain instance
        
    Returns:
        The created integration instance
    """
    integration = WorldReactionIntegration(brain)
    brain.register_extension("world_reaction", integration)
    return integration