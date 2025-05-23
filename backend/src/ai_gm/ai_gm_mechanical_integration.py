"""
AI GM Brain - Mechanical Integration

This module provides the integration between mechanical actions and narrative responses,
ensuring that mechanical outcomes (success/failure of actions) are properly represented
in the GM's narrative responses.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Import from core brain
from .ai_gm_brain import AIGMBrain


class MechanicalIntegration:
    """
    Handles the integration of mechanical outcomes into narrative responses.
    
    This class ensures that when mechanical actions (from the parser or LLM-identified
    branch actions) are executed, their success/failure and details properly influence
    the GM's narrative response.
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the mechanical integration handler.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"MechanicalIntegration_{ai_gm_brain.game_id}")
        
        # Track integration metrics
        self.successful_integrations = 0
        self.failed_integrations = 0
        
        self.logger.info("Mechanical Integration handler initialized")
    
    def integrate_mechanical_outcome(self, 
                                   base_response: str,
                                   outcome: Dict[str, Any],
                                   context: Dict[str, Any]) -> str:
        """
        Integrate a mechanical outcome into a narrative response.
        
        Args:
            base_response: Base narrative response
            outcome: Mechanical outcome details
            context: Additional context for integration
            
        Returns:
            Enhanced narrative response
        """
        self.logger.info(f"Integrating mechanical outcome: {outcome.get('action', 'unknown')}")
        
        if not outcome:
            return base_response
        
        # Extract outcome details
        success = outcome.get('success', False)
        action_type = outcome.get('action_type', 'generic')
        details = outcome.get('details', {})
        outcome_message = outcome.get('message', '')
        
        # Create a narrative description based on the outcome
        narrative_addition = self._create_narrative_addition(
            success=success,
            action_type=action_type,
            details=details,
            context=context
        )
        
        # Combine base response with the narrative addition
        if not base_response.endswith('.') and not base_response.endswith('!') and not base_response.endswith('?'):
            base_response += '.'
            
        enhanced_response = f"{base_response} {narrative_addition}"
        
        if success:
            self.successful_integrations += 1
        else:
            self.failed_integrations += 1
            
        return enhanced_response
    
    def _create_narrative_addition(self,
                                 success: bool,
                                 action_type: str,
                                 details: Dict[str, Any],
                                 context: Dict[str, Any]) -> str:
        """
        Create a narrative description based on a mechanical outcome.
        
        Args:
            success: Whether the action was successful
            action_type: Type of action performed
            details: Details of the action outcome
            context: Additional context
            
        Returns:
            Narrative description of the outcome
        """
        # Check for skill check results
        if 'skill_check' in details:
            return self._create_skill_check_narrative(
                success=success,
                skill_check=details['skill_check'],
                action_type=action_type
            )
        
        # Check for combat results
        elif 'combat' in details:
            return self._create_combat_narrative(
                success=success,
                combat=details['combat'],
                action_type=action_type
            )
        
        # Check for progression results
        elif 'progression' in details:
            return self._create_progression_narrative(
                success=success,
                progression=details['progression'],
                action_type=action_type
            )
        
        # Default narrative
        else:
            if success:
                return "Your action succeeds, and you observe the results of your efforts."
            else:
                return "Despite your efforts, you're unable to accomplish what you intended."
    
    def _create_skill_check_narrative(self,
                                    success: bool,
                                    skill_check: Dict[str, Any],
                                    action_type: str) -> str:
        """
        Create a narrative description for a skill check outcome.
        
        Args:
            success: Whether the skill check was successful
            skill_check: Details of the skill check
            action_type: Type of action performed
            
        Returns:
            Narrative description of the skill check
        """
        # Extract skill check details
        roll = skill_check.get('roll', 0)
        dc = skill_check.get('dc', 10)
        skill = skill_check.get('skill', 'ability')
        margin = abs(roll - dc)
        
        # Create narrative based on success/failure and margin
        if success:
            if roll >= dc + 5:
                # Critical success
                return f"With exceptional skill, you easily accomplish the task. Your {skill} is more than sufficient for the challenge."
            else:
                # Normal success
                return f"You successfully complete the task, your {skill} proving adequate for the challenge."
        else:
            if roll <= dc - 5:
                # Critical failure
                return f"Despite your best efforts, your {skill} is simply not up to the task, and you fail dramatically."
            else:
                # Normal failure
                return f"You fall just short of success, your {skill} not quite enough for this particular challenge."
    
    def _create_combat_narrative(self,
                               success: bool,
                               combat: Dict[str, Any],
                               action_type: str) -> str:
        """
        Create a narrative description for a combat outcome.
        
        Args:
            success: Whether the combat action was successful
            combat: Details of the combat outcome
            action_type: Type of combat action performed
            
        Returns:
            Narrative description of the combat outcome
        """
        # Extract combat details
        damage_dealt = combat.get('damage_dealt', 0)
        target = combat.get('target', 'the enemy')
        attack_type = combat.get('attack_type', 'attack')
        
        # Create narrative based on success/failure and combat details
        if success:
            if damage_dealt > 0:
                if damage_dealt > 10:
                    return f"Your {attack_type} lands with devastating effect, dealing significant damage to {target}."
                else:
                    return f"Your {attack_type} connects, dealing some damage to {target}."
            else:
                return f"Your {attack_type} succeeds, though it doesn't seem to cause any damage to {target}."
        else:
            return f"Your {attack_type} misses {target}, leaving you momentarily off-balance."
    
    def _create_progression_narrative(self,
                                    success: bool,
                                    progression: Dict[str, Any],
                                    action_type: str) -> str:
        """
        Create a narrative description for a progression outcome.
        
        Args:
            success: Whether the progression action was successful
            progression: Details of the progression outcome
            action_type: Type of progression action performed
            
        Returns:
            Narrative description of the progression outcome
        """
        # Extract progression details
        advanced = progression.get('advanced', False)
        new_stage = progression.get('new_stage', '')
        
        # Create narrative based on progression details
        if advanced and new_stage:
            return f"Your actions move the situation forward, opening new possibilities."
        elif success:
            return f"You make progress, though there's still more to be done."
        else:
            return f"Your efforts don't seem to advance the situation as hoped."
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on mechanical integrations.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "successful_integrations": self.successful_integrations,
            "failed_integrations": self.failed_integrations,
            "total_integrations": self.successful_integrations + self.failed_integrations
        }


# Extension function to add mechanical integration to AI GM Brain
def extend_ai_gm_brain_with_mechanical_integration(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with mechanical integration capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create mechanical integration
    mechanical_integration = MechanicalIntegration(ai_gm_brain)
    
    # Store the mechanical integration for future reference
    ai_gm_brain.mechanical_integration = mechanical_integration
    
    # Add integrate_outcome method to the AI GM Brain
    ai_gm_brain.integrate_mechanical_outcome = lambda base_response, outcome, context: mechanical_integration.integrate_mechanical_outcome(
        base_response, outcome, context
    )
    
    # Enhance the decision tree handler's process_input method to use mechanical integration
    if hasattr(ai_gm_brain, 'decision_logic') and hasattr(ai_gm_brain.decision_logic, 'decision_tree'):
        original_process_input = ai_gm_brain.decision_logic.decision_tree.process_input
        
        def enhanced_process_input(parsed_command, llm_output):
            # Get the basic result from the decision tree
            result = original_process_input(parsed_command, llm_output)
            
            # If there's a mechanical outcome, integrate it into the response
            if result.get('mechanical_outcome') and result.get('suggested_response'):
                result['suggested_response'] = mechanical_integration.integrate_mechanical_outcome(
                    result['suggested_response'],
                    result['mechanical_outcome'],
                    {'llm_output': llm_output}
                )
                
            return result
        
        # Replace the original method with the enhanced version
        ai_gm_brain.decision_logic.decision_tree.process_input = enhanced_process_input