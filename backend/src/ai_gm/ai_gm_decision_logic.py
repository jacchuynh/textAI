"""
AI GM Brain Decision Logic - Decision tree logic for the AI GM Brain.

This module implements the decision tree logic for determining the most appropriate
action to take based on player input and game context.
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from enum import Enum
import logging


class DecisionPriority(Enum):
    """Priorities for decision tree evaluation."""
    NARRATIVE_ALIGNMENT = 1
    PARSED_COMMAND = 2
    GENERAL_INTERPRETATION = 3
    FALLBACK = 4


class DecisionResult:
    """Result of a decision tree evaluation."""
    
    def __init__(self, 
                priority: DecisionPriority, 
                action_type: str,
                success: bool = True,
                action_data: Dict[str, Any] = None,
                response_template: str = None):
        """
        Initialize a decision result.
        
        Args:
            priority: Priority level of this decision
            action_type: Type of action to take
            success: Whether the action was successful
            action_data: Additional data about the action
            response_template: Optional template for generating a response
        """
        self.priority = priority
        self.action_type = action_type
        self.success = success
        self.action_data = action_data or {}
        self.response_template = response_template
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision result to dictionary."""
        return {
            'priority': self.priority.name,
            'action_type': self.action_type,
            'success': self.success,
            'action_data': self.action_data,
            'response_template': self.response_template
        }


class AIGMDecisionLogic:
    """Decision tree logic for the AI GM Brain."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize decision logic.
        
        Args:
            config: Configuration for decision logic
        """
        self.logger = logging.getLogger("AIGMDecisionLogic")
        self.config = config or {}
    
    async def evaluate_decision_tree(self, 
                                  player_input: str,
                                  parsed_command: Dict[str, Any] = None,
                                  llm_output: Dict[str, Any] = None,
                                  game_context: Dict[str, Any] = None) -> DecisionResult:
        """
        Evaluate the decision tree to determine the most appropriate action.
        
        Args:
            player_input: Raw player input
            parsed_command: Output from parser if available
            llm_output: Output from LLM if available
            game_context: Current game context
            
        Returns:
            Decision result
        """
        self.logger.info(f"Evaluating decision tree for input: {player_input}")
        
        # Default game context if not provided
        game_context = game_context or {}
        
        # Priority 1: LLM Identified Narrative Alignment
        if llm_output and self._check_narrative_alignment(llm_output):
            return await self._handle_narrative_alignment(llm_output, game_context)
        
        # Priority 2: Successful ParsedCommand
        if parsed_command and self._is_valid_parsed_command(parsed_command):
            return await self._handle_parsed_command(parsed_command, game_context)
        
        # Priority 3: General LLM Interpretation
        if llm_output and self._has_player_intent(llm_output):
            return await self._handle_general_interpretation(llm_output, game_context)
        
        # Priority 4: Fallback
        return await self._handle_fallback(player_input, game_context)
    
    def _check_narrative_alignment(self, llm_output: Dict[str, Any]) -> bool:
        """Check if LLM output contains narrative alignment."""
        return (llm_output.get('aligned_opportunity_id') is not None or 
                llm_output.get('aligned_branch_action') is not None)
    
    def _is_valid_parsed_command(self, parsed_command: Dict[str, Any]) -> bool:
        """Check if parsed command is valid."""
        return (parsed_command and 
                parsed_command.get('action') and 
                parsed_command.get('success', False))
    
    def _has_player_intent(self, llm_output: Dict[str, Any]) -> bool:
        """Check if LLM output contains player intent."""
        return (llm_output.get('player_intent_summary') or 
                llm_output.get('suggested_gm_acknowledgement'))
    
    async def _handle_narrative_alignment(self, 
                                      llm_output: Dict[str, Any],
                                      game_context: Dict[str, Any]) -> DecisionResult:
        """
        Handle narrative alignment decision.
        
        Args:
            llm_output: LLM output containing narrative alignment
            game_context: Current game context
            
        Returns:
            Decision result
        """
        self.logger.info("Handling narrative alignment decision")
        
        aligned_opportunity_id = llm_output.get('aligned_opportunity_id')
        aligned_branch_action = llm_output.get('aligned_branch_action')
        
        # Check if opportunity alignment
        if aligned_opportunity_id:
            # Would call NarrativeBranchChoiceHandler here
            # For now, simulate success
            success = True
            action_data = {
                'opportunity_id': aligned_opportunity_id,
                'branch_initiated': success,
                'player_id': game_context.get('player_id', 'default_player'),
                'game_id': game_context.get('game_id', 'default_game')
            }
            
            return DecisionResult(
                priority=DecisionPriority.NARRATIVE_ALIGNMENT,
                action_type='INITIATE_NARRATIVE_BRANCH',
                success=success,
                action_data=action_data,
                response_template=llm_output.get('suggested_gm_acknowledgement')
            )
        
        # Check if branch action alignment
        elif aligned_branch_action:
            # Would verify action is valid for current branch/stage
            # For now, simulate success
            success = True
            action_data = {
                'branch_action': aligned_branch_action,
                'action_outcome': 'SUCCESS' if success else 'FAILURE',
                'player_id': game_context.get('player_id', 'default_player')
            }
            
            return DecisionResult(
                priority=DecisionPriority.NARRATIVE_ALIGNMENT,
                action_type='EXECUTE_BRANCH_ACTION',
                success=success,
                action_data=action_data,
                response_template=llm_output.get('suggested_gm_acknowledgement')
            )
        
        # Should never reach here if _check_narrative_alignment was called first
        return await self._handle_fallback(llm_output.get('player_raw_input', ''), game_context)
    
    async def _handle_parsed_command(self, 
                                 parsed_command: Dict[str, Any],
                                 game_context: Dict[str, Any]) -> DecisionResult:
        """
        Handle parsed command decision.
        
        Args:
            parsed_command: Successful parsed command
            game_context: Current game context
            
        Returns:
            Decision result
        """
        self.logger.info(f"Handling parsed command: {parsed_command.get('action')}")
        
        action = parsed_command.get('action')
        direct_object = parsed_command.get('direct_object')
        indirect_object = parsed_command.get('indirect_object')
        
        # Get action template if available in config
        template = None
        if hasattr(self.config, 'get_template_for_action'):
            template = self.config.get_template_for_action(action)
        
        action_data = {
            'action': action,
            'direct_object': direct_object,
            'indirect_object': indirect_object,
            'modifiers': parsed_command.get('modifiers', {}),
            'full_command': parsed_command.get('full_command', '')
        }
        
        return DecisionResult(
            priority=DecisionPriority.PARSED_COMMAND,
            action_type='EXECUTE_PARSED_COMMAND',
            success=True,
            action_data=action_data,
            response_template=template
        )
    
    async def _handle_general_interpretation(self, 
                                         llm_output: Dict[str, Any],
                                         game_context: Dict[str, Any]) -> DecisionResult:
        """
        Handle general LLM interpretation decision.
        
        Args:
            llm_output: LLM output with player intent
            game_context: Current game context
            
        Returns:
            Decision result
        """
        self.logger.info("Handling general LLM interpretation")
        
        player_intent = llm_output.get('player_intent_summary', '')
        suggested_response = llm_output.get('suggested_gm_acknowledgement', '')
        
        action_data = {
            'player_intent': player_intent,
            'player_id': game_context.get('player_id', 'default_player'),
            'interaction_type': 'CONVERSATIONAL'
        }
        
        return DecisionResult(
            priority=DecisionPriority.GENERAL_INTERPRETATION,
            action_type='PROCESS_GENERAL_INTENT',
            success=True,
            action_data=action_data,
            response_template=suggested_response
        )
    
    async def _handle_fallback(self, 
                           player_input: str,
                           game_context: Dict[str, Any]) -> DecisionResult:
        """
        Handle fallback decision when no other decision applies.
        
        Args:
            player_input: Original player input
            game_context: Current game context
            
        Returns:
            Decision result
        """
        self.logger.info("Handling fallback decision")
        
        # Get error message if available in config
        error_message = None
        if hasattr(self.config, 'ERROR_MESSAGES'):
            error_message = self.config.ERROR_MESSAGES.get('parsing_failed', 
                                                          "I'm not sure what you want to do.")
        
        action_data = {
            'original_input': player_input,
            'player_id': game_context.get('player_id', 'default_player'),
            'fallback_reason': 'NO_VALID_INTERPRETATION'
        }
        
        return DecisionResult(
            priority=DecisionPriority.FALLBACK,
            action_type='PROVIDE_FALLBACK_RESPONSE',
            success=False,
            action_data=action_data,
            response_template=error_message
        )