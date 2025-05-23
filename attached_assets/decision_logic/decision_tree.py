"""
Core decision tree and action mapping for AI GM Brain Phase 3
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum, auto
import logging
from dataclasses import dataclass
from datetime import datetime

from text_parser.parser_engine import ParsedCommand
from narrative_branch_choice_handler import NarrativeBranchChoiceHandler
from world_state import WorldState


class DecisionPriority(Enum):
    """Decision priority levels for the decision tree"""
    LLM_OPPORTUNITY_ALIGNMENT = 1
    LLM_BRANCH_ACTION_ALIGNMENT = 2
    SUCCESSFUL_PARSED_COMMAND = 3
    GENERAL_LLM_INTERPRETATION = 4
    PARSER_FAILURE_FALLBACK = 5


class ActionOutcome(Enum):
    """Possible outcomes from actions"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    REQUIRES_FOLLOWUP = "requires_followup"
    BLOCKED = "blocked"
    INVALID = "invalid"


@dataclass
class DecisionContext:
    """Context for decision making"""
    session_id: str
    player_id: str
    raw_input: str
    parsed_command: Optional[ParsedCommand] = None
    llm_output: Optional[Dict[str, Any]] = None
    current_branch_id: Optional[str] = None
    current_stage: Optional[str] = None
    world_state: Optional[Dict[str, Any]] = None
    player_context: Optional[Dict[str, Any]] = None
    pending_opportunities: List[Dict[str, Any]] = None


@dataclass
class ActionResult:
    """Result of an executed action"""
    outcome: ActionOutcome
    action_type: str
    details: Dict[str, Any]
    mechanics_triggered: bool = False
    branch_id: Optional[str] = None
    error_message: Optional[str] = None
    narrative_context: Dict[str, Any] = None


@dataclass
class DecisionResult:
    """Final result of the decision process"""
    priority_used: DecisionPriority
    action_result: Optional[ActionResult]
    gm_response_base: str
    narrative_enhancements: List[str]
    requires_followup: bool = False
    metadata: Dict[str, Any] = None


class CoreDecisionEngine:
    """
    Core decision engine that implements the decision tree logic
    """
    
    def __init__(self, 
                 branch_handler: NarrativeBranchChoiceHandler,
                 world_state_manager: WorldState,
                 db_service=None):
        """
        Initialize the decision engine.
        
        Args:
            branch_handler: Handler for narrative branches
            world_state_manager: World state manager
            db_service: Database service for tracking decisions
        """
        self.branch_handler = branch_handler
        self.world_state_manager = world_state_manager
        self.db_service = db_service
        self.logger = logging.getLogger("CoreDecisionEngine")
        
        # Action executors for different types of actions
        self.action_executors = {
            'opportunity_initiation': self._execute_opportunity_initiation,
            'branch_action': self._execute_branch_action,
            'parsed_command': self._execute_parsed_command,
            'general_interpretation': self._execute_general_interpretation,
            'fallback_response': self._execute_fallback_response
        }
        
        # Track decision statistics
        self.decision_stats = {
            'total_decisions': 0,
            'priority_usage': {priority: 0 for priority in DecisionPriority},
            'action_outcomes': {outcome: 0 for outcome in ActionOutcome}
        }
    
    def make_decision(self, context: DecisionContext) -> DecisionResult:
        """
        Main decision-making method that implements the decision tree.
        
        Args:
            context: Decision context with all necessary information
            
        Returns:
            DecisionResult with the chosen action and response information
        """
        self.decision_stats['total_decisions'] += 1
        start_time = datetime.utcnow()
        
        self.logger.info(f"Making decision for input: '{context.raw_input}'")
        
        try:
            # Priority 1: LLM Identified Opportunity Alignment
            if (context.llm_output and 
                context.llm_output.get('aligned_opportunity_id') and
                context.llm_output['aligned_opportunity_id'] != 'null'):
                
                return self._handle_priority_1(context)
            
            # Priority 2: LLM Identified Branch Action Alignment  
            elif (context.llm_output and 
                  context.llm_output.get('aligned_branch_action') and
                  context.llm_output['aligned_branch_action'] != 'null'):
                
                return self._handle_priority_2(context)
            
            # Priority 3: Successful ParsedCommand
            elif (context.parsed_command and 
                  not context.parsed_command.has_error() and 
                  not context.parsed_command.needs_disambiguation()):
                
                return self._handle_priority_3(context)
            
            # Priority 4: General LLM Interpretation
            elif (context.llm_output and 
                  context.llm_output.get('suggested_gm_acknowledgement')):
                
                return self._handle_priority_4(context)
            
            # Priority 5: Parser Failure & LLM Fallback
            else:
                return self._handle_priority_5(context)
                
        except Exception as e:
            self.logger.error(f"Decision making error: {e}")
            return self._create_error_decision(context, str(e))
        
        finally:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.debug(f"Decision completed in {processing_time:.3f}s")
    
    def _handle_priority_1(self, context: DecisionContext) -> DecisionResult:
        """Handle Priority 1: LLM Identified Opportunity Alignment"""
        self.decision_stats['priority_usage'][DecisionPriority.LLM_OPPORTUNITY_ALIGNMENT] += 1
        
        opportunity_id = context.llm_output['aligned_opportunity_id']
        self.logger.info(f"Priority 1: Attempting to initiate opportunity {opportunity_id}")
        
        # Execute opportunity initiation
        action_result = self._execute_opportunity_initiation(context, opportunity_id)
        
        # Generate response based on outcome
        if action_result.outcome == ActionOutcome.SUCCESS:
            gm_response = self._build_success_response(context, action_result)
            narrative_enhancements = self._get_opportunity_success_enhancements(action_result)
        elif action_result.outcome == ActionOutcome.FAILURE:
            gm_response = self._build_failure_response(context, action_result)
            narrative_enhancements = self._get_opportunity_failure_enhancements(action_result)
        else:
            gm_response = context.llm_output.get('suggested_gm_acknowledgement', 'Something interesting happens...')
            narrative_enhancements = []
        
        return DecisionResult(
            priority_used=DecisionPriority.LLM_OPPORTUNITY_ALIGNMENT,
            action_result=action_result,
            gm_response_base=gm_response,
            narrative_enhancements=narrative_enhancements,
            requires_followup=action_result.outcome == ActionOutcome.REQUIRES_FOLLOWUP,
            metadata={
                'opportunity_id': opportunity_id,
                'llm_confidence': context.llm_output.get('confidence_score', 0.5)
            }
        )
    
    def _handle_priority_2(self, context: DecisionContext) -> DecisionResult:
        """Handle Priority 2: LLM Identified Branch Action Alignment"""
        self.decision_stats['priority_usage'][DecisionPriority.LLM_BRANCH_ACTION_ALIGNMENT] += 1
        
        branch_action = context.llm_output['aligned_branch_action']
        self.logger.info(f"Priority 2: Executing branch action: {branch_action}")
        
        # Verify action is valid for current branch/stage
        if not self._validate_branch_action(context, branch_action):
            self.logger.warning(f"Invalid branch action: {branch_action} for current context")
            return self._handle_priority_4(context)  # Fall back to general interpretation
        
        # Execute branch action
        action_result = self._execute_branch_action(context, branch_action)
        
        # Generate response based on outcome
        gm_response = self._build_branch_action_response(context, action_result)
        narrative_enhancements = self._get_branch_action_enhancements(action_result)
        
        return DecisionResult(
            priority_used=DecisionPriority.LLM_BRANCH_ACTION_ALIGNMENT,
            action_result=action_result,
            gm_response_base=gm_response,
            narrative_enhancements=narrative_enhancements,
            requires_followup=action_result.outcome == ActionOutcome.REQUIRES_FOLLOWUP,
            metadata={
                'branch_action': branch_action,
                'branch_id': context.current_branch_id,
                'stage': context.current_stage
            }
        )
    
    def _handle_priority_3(self, context: DecisionContext) -> DecisionResult:
        """Handle Priority 3: Successful ParsedCommand"""
        self.decision_stats['priority_usage'][DecisionPriority.SUCCESSFUL_PARSED_COMMAND] += 1
        
        self.logger.info(f"Priority 3: Executing parsed command: {context.parsed_command.action}")
        
        # Execute the parsed command
        action_result = self._execute_parsed_command(context)
        
        # Generate response based on command and outcome
        gm_response = self._build_parsed_command_response(context, action_result)
        narrative_enhancements = self._get_parsed_command_enhancements(action_result)
        
        return DecisionResult(
            priority_used=DecisionPriority.SUCCESSFUL_PARSED_COMMAND,
            action_result=action_result,
            gm_response_base=gm_response,
            narrative_enhancements=narrative_enhancements,
            requires_followup=False,
            metadata={
                'command_action': context.parsed_command.action,
                'command_pattern': context.parsed_command.pattern.value if context.parsed_command.pattern else None
            }
        )
    
    def _handle_priority_4(self, context: DecisionContext) -> DecisionResult:
        """Handle Priority 4: General LLM Interpretation"""
        self.decision_stats['priority_usage'][DecisionPriority.GENERAL_LLM_INTERPRETATION] += 1
        
        self.logger.info("Priority 4: Using general LLM interpretation")
        
        # Execute general interpretation
        action_result = self._execute_general_interpretation(context)
        
        gm_response = context.llm_output.get('suggested_gm_acknowledgement', 
                                           'I understand what you\'re getting at...')
        narrative_enhancements = self._get_general_interpretation_enhancements(context)
        
        return DecisionResult(
            priority_used=DecisionPriority.GENERAL_LLM_INTERPRETATION,
            action_result=action_result,
            gm_response_base=gm_response,
            narrative_enhancements=narrative_enhancements,
            requires_followup=context.llm_output.get('requires_followup', False),
            metadata={
                'intent_summary': context.llm_output.get('player_intent_summary'),
                'input_nature': context.llm_output.get('input_nature_if_no_alignment')
            }
        )
    
    def _handle_priority_5(self, context: DecisionContext) -> DecisionResult:
        """Handle Priority 5: Parser Failure & LLM Fallback"""
        self.decision_stats['priority_usage'][DecisionPriority.PARSER_FAILURE_FALLBACK] += 1
        
        self.logger.info("Priority 5: Using fallback response")
        
        # Execute fallback response
        action_result = self._execute_fallback_response(context)
        
        # Use LLM suggestion if available, otherwise provide helpful fallback
        if context.llm_output and context.llm_output.get('suggested_gm_acknowledgement'):
            gm_response = context.llm_output['suggested_gm_acknowledgement']
        else:
            gm_response = self._generate_fallback_response(context)
        
        narrative_enhancements = ['Perhaps you could try being more specific about what you want to do?']
        
        return DecisionResult(
            priority_used=DecisionPriority.PARSER_FAILURE_FALLBACK,
            action_result=action_result,
            gm_response_base=gm_response,
            narrative_enhancements=narrative_enhancements,
            requires_followup=True,
            metadata={
                'fallback_reason': 'parser_failure_and_llm_unclear'
            }
        )
    
    # Action Execution Methods
    
    def _execute_opportunity_initiation(self, context: DecisionContext, opportunity_id: str) -> ActionResult:
        """Execute opportunity initiation through branch handler"""
        try:
            success, message, new_branch_id = self.branch_handler.attempt_to_initiate_branch_via_gm(
                opportunity_id, context.player_id, context.session_id
            )
            
            if success:
                # Log the successful initiation
                if self.db_service:
                    self.db_service.save_event({
                        'session_id': context.session_id,
                        'event_type': 'NARRATIVE_BRANCH_INITIATED',
                        'actor': context.player_id,
                        'context': {
                            'opportunity_id': opportunity_id,
                            'branch_id': new_branch_id,
                            'message': message
                        }
                    })
                
                self.decision_stats['action_outcomes'][ActionOutcome.SUCCESS] += 1
                return ActionResult(
                    outcome=ActionOutcome.SUCCESS,
                    action_type='opportunity_initiation',
                    details={
                        'opportunity_id': opportunity_id,
                        'message': message,
                        'new_branch_id': new_branch_id
                    },
                    mechanics_triggered=True,
                    branch_id=new_branch_id,
                    narrative_context={
                        'opportunity_accepted': True,
                        'new_narrative_path': True
                    }
                )
            else:
                self.decision_stats['action_outcomes'][ActionOutcome.FAILURE] += 1
                return ActionResult(
                    outcome=ActionOutcome.FAILURE,
                    action_type='opportunity_initiation',
                    details={
                        'opportunity_id': opportunity_id,
                        'failure_reason': message
                    },
                    mechanics_triggered=False,
                    error_message=message,
                    narrative_context={
                        'opportunity_blocked': True,
                        'reason': message
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error executing opportunity initiation: {e}")
            self.decision_stats['action_outcomes'][ActionOutcome.INVALID] += 1
            return ActionResult(
                outcome=ActionOutcome.INVALID,
                action_type='opportunity_initiation',
                details={'error': str(e)},
                mechanics_triggered=False,
                error_message=str(e)
            )
    
    def _execute_branch_action(self, context: DecisionContext, branch_action: str) -> ActionResult:
        """Execute branch-specific action"""
        try:
            # This would integrate with your narrative branch system
            # For now, simulate the execution
            
            # Check if action requires skill checks
            skill_check_result = self._perform_skill_checks(context, branch_action)
            
            if skill_check_result['success']:
                # Update branch progress
                self._update_branch_progress(context, branch_action, skill_check_result)
                
                # Log the action
                if self.db_service:
                    self.db_service.save_event({
                        'session_id': context.session_id,
                        'event_type': 'BRANCH_ACTION_EXECUTED',
                        'actor': context.player_id,
                        'context': {
                            'branch_id': context.current_branch_id,
                            'action': branch_action,
                            'skill_check_result': skill_check_result
                        }
                    })
                
                self.decision_stats['action_outcomes'][ActionOutcome.SUCCESS] += 1
                return ActionResult(
                    outcome=ActionOutcome.SUCCESS,
                    action_type='branch_action',
                    details={
                        'action': branch_action,
                        'skill_check': skill_check_result,
                        'branch_progress': 'advanced'
                    },
                    mechanics_triggered=True,
                    branch_id=context.current_branch_id,
                    narrative_context={
                        'action_successful': True,
                        'skill_check_passed': True,
                        'progress_made': True
                    }
                )
            else:
                self.decision_stats['action_outcomes'][ActionOutcome.FAILURE] += 1
                return ActionResult(
                    outcome=ActionOutcome.FAILURE,
                    action_type='branch_action',
                    details={
                        'action': branch_action,
                        'skill_check': skill_check_result,
                        'failure_reason': skill_check_result.get('failure_reason', 'Skill check failed')
                    },
                    mechanics_triggered=True,
                    branch_id=context.current_branch_id,
                    narrative_context={
                        'action_attempted': True,
                        'skill_check_failed': True,
                        'setback_occurred': True
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Error executing branch action: {e}")
            self.decision_stats['action_outcomes'][ActionOutcome.INVALID] += 1
            return ActionResult(
                outcome=ActionOutcome.INVALID,
                action_type='branch_action',
                details={'error': str(e)},
                mechanics_triggered=False,
                error_message=str(e)
            )
    
    def _execute_parsed_command(self, context: DecisionContext) -> ActionResult:
        """Execute a successfully parsed command"""
        try:
            command = context.parsed_command
            
            # Execute command based on action type
            execution_result = self._execute_command_mechanics(command, context)
            
            # Log the command execution
            if self.db_service:
                self.db_service.save_event({
                    'session_id': context.session_id,
                    'event_type': 'COMMAND_EXECUTED',
                    'actor': context.player_id,
                    'context': {
                        'action': command.action,
                        'target': command.direct_object_phrase.noun if command.direct_object_phrase else None,
                        'result': execution_result
                    }
                })
            
            outcome = ActionOutcome.SUCCESS if execution_result.get('success', False) else ActionOutcome.FAILURE
            self.decision_stats['action_outcomes'][outcome] += 1
            
            return ActionResult(
                outcome=outcome,
                action_type='parsed_command',
                details={
                    'command': command.action,
                    'execution_result': execution_result
                },
                mechanics_triggered=True,
                narrative_context={
                    'command_executed': True,
                    'mechanical_action': True
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error executing parsed command: {e}")
            self.decision_stats['action_outcomes'][ActionOutcome.INVALID] += 1
            return ActionResult(
                outcome=ActionOutcome.INVALID,
                action_type='parsed_command',
                details={'error': str(e)},
                mechanics_triggered=False,
                error_message=str(e)
            )
    
    def _execute_general_interpretation(self, context: DecisionContext) -> ActionResult:
        """Execute general LLM interpretation (no specific mechanics)"""
        self.decision_stats['action_outcomes'][ActionOutcome.SUCCESS] += 1
        
        return ActionResult(
            outcome=ActionOutcome.SUCCESS,
            action_type='general_interpretation',
            details={
                'intent': context.llm_output.get('player_intent_summary', 'General interaction'),
                'nature': context.llm_output.get('input_nature_if_no_alignment', 'conversational')
            },
            mechanics_triggered=False,
            narrative_context={
                'conversational_response': True,
                'no_mechanics': True
            }
        )
    
    def _execute_fallback_response(self, context: DecisionContext) -> ActionResult:
        """Execute fallback response for unclear inputs"""
        self.decision_stats['action_outcomes'][ActionOutcome.REQUIRES_FOLLOWUP] += 1
        
        return ActionResult(
            outcome=ActionOutcome.REQUIRES_FOLLOWUP,
            action_type='fallback_response',
            details={
                'reason': 'unclear_input',
                'parser_error': context.parsed_command.error_message if context.parsed_command else None
            },
            mechanics_triggered=False,
            narrative_context={
                'clarification_needed': True,
                'unclear_input': True
            }
        )
    
    # Helper Methods
    
    def _validate_branch_action(self, context: DecisionContext, branch_action: str) -> bool:
        """Validate if branch action is valid for current context"""
        # This would check against your narrative branch system
        # For now, simulate validation
        if not context.current_branch_id:
            return False
        
        # Check if action is in available actions for current stage
        # This would integrate with your narrative director
        return True  # Simplified for now
    
    def _perform_skill_checks(self, context: DecisionContext, action: str) -> Dict[str, Any]:
        """Perform skill checks for branch actions"""
        # This would integrate with your WorldStateSkillModifier system
        # For now, simulate skill checks
        
        import random
        
        # Simulate skill check based on world state and action difficulty
        base_chance = 0.7  # 70% base success rate
        
        # Modify based on world state
        world_state = context.world_state or {}
        if world_state.get('political_stability') == 'unrest':
            base_chance -= 0.1  # Harder actions during unrest
        
        success = random.random() < base_chance
        
        return {
            'success': success,
            'roll': random.randint(1, 20),
            'difficulty': 12,
            'modifiers': [],
            'failure_reason': 'The attempt was not quite successful' if not success else None
        }
    
    def _update_branch_progress(self, context: DecisionContext, action: str, skill_result: Dict[str, Any]):
        """Update narrative branch progress"""
        # This would integrate with your narrative branch system
        # For now, log the progress update
        self.logger.info(f"Branch progress updated for action: {action}")
    
    def _execute_command_mechanics(self, command: ParsedCommand, context: DecisionContext) -> Dict[str, Any]:
        """Execute the mechanics of a parsed command"""
        # This would integrate with your game's action execution system
        # For now, simulate command execution
        
        action_results = {
            'look': {'success': True, 'description': 'You observe your surroundings carefully.'},
            'take': {'success': True, 'description': 'You pick up the item.'},
            'go': {'success': True, 'description': 'You move in the specified direction.'},
            'attack': {'success': True, 'description': 'You strike at your target.'},
            'use': {'success': True, 'description': 'You use the item.'},
            'talk': {'success': True, 'description': 'You engage in conversation.'}
        }
        
        return action_results.get(command.action, {'success': False, 'description': 'Action not recognized.'})
    
    # Response Building Methods
    
    def _build_success_response(self, context: DecisionContext, action_result: ActionResult) -> str:
        """Build response for successful opportunity initiation"""
        base_response = context.llm_output.get('suggested_gm_acknowledgement', '')
        success_message = action_result.details.get('message', '')
        
        if base_response and success_message:
            return f"{base_response}\n\n{success_message}"
        elif success_message:
            return success_message
        else:
            return base_response or "Your initiative opens up new possibilities..."
    
    def _build_failure_response(self, context: DecisionContext, action_result: ActionResult) -> str:
        """Build response for failed opportunity initiation"""
        base_response = context.llm_output.get('suggested_gm_acknowledgement', '')
        failure_reason = action_result.details.get('failure_reason', '')
        
        # Create narrative explanation for the failure
        failure_narratives = {
            'conditions_not_met': 'but the circumstances don\'t seem quite right for that course of action',
            'already_active': 'but you\'re already committed to another endeavor',
            'world_state_blocking': 'but current events make that path unavailable',
            'player_state_blocking': 'but you\'re not in the right condition for such an undertaking'
        }
        
        narrative_addition = failure_narratives.get(
            action_result.error_message, 
            'but something prevents you from pursuing that path right now'
        )
        
        if base_response:
            return f"{base_response}, {narrative_addition}."
        else:
            return f"You consider that course of action, {narrative_addition}."
    
    def _build_branch_action_response(self, context: DecisionContext, action_result: ActionResult) -> str:
        """Build response for branch action execution"""
        if action_result.outcome == ActionOutcome.SUCCESS:
            return f"You successfully {action_result.details['action']}. Your efforts pay off as you make meaningful progress."
        elif action_result.outcome == ActionOutcome.FAILURE:
            skill_check = action_result.details.get('skill_check', {})
            return f"You attempt to {action_result.details['action']}, but {skill_check.get('failure_reason', 'the attempt falls short')}."
        else:
            return f"You try to {action_result.details['action']}, but the outcome is unclear."
    
    def _build_parsed_command_response(self, context: DecisionContext, action_result: ActionResult) -> str:
        """Build response for parsed command execution"""
        execution_result = action_result.details.get('execution_result', {})
        return execution_result.get('description', 'You complete the action.')
    
    def _generate_fallback_response(self, context: DecisionContext) -> str:
        """Generate fallback response when nothing else works"""
        fallback_responses = [
            "I'm not quite sure what you're trying to do. Could you be more specific?",
            "Your intentions aren't entirely clear to me. Perhaps you could rephrase that?",
            "I want to help, but I need a clearer understanding of what you want to accomplish.",
            "That's an interesting thought. Could you elaborate on what you'd like to do?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    # Enhancement Methods
    
    def _get_opportunity_success_enhancements(self, action_result: ActionResult) -> List[str]:
        """Get narrative enhancements for successful opportunity initiation"""
        return [
            "A new path opens before you.",
            "Your decision sets events in motion.",
            "The world responds to your choice."
        ]
    
    def _get_opportunity_failure_enhancements(self, action_result: ActionResult) -> List[str]:
        """Get narrative enhancements for failed opportunity initiation"""
        return [
            "Perhaps another time would be more suitable.",
            "The moment doesn't seem quite right for such an endeavor.",
            "Other considerations weigh on your mind."
        ]
    
    def _get_branch_action_enhancements(self, action_result: ActionResult) -> List[str]:
        """Get narrative enhancements for branch actions"""
        if action_result.outcome == ActionOutcome.SUCCESS:
            return [
                "Your skills serve you well in this endeavor.",
                "Progress is made through careful action.",
                "Each step brings you closer to your goal."
            ]
        else:
            return [
                "Not every attempt meets with success.",
                "Experience is gained even through setbacks.",
                "The challenge proves more difficult than expected."
            ]
    
    def _get_parsed_command_enhancements(self, action_result: ActionResult) -> List[str]:
        """Get narrative enhancements for parsed commands"""
        return [
            "Your actions have immediate effect.",
            "The world responds to your direct approach.",
            "Simple actions often yield clear results."
        ]
    
    def _get_general_interpretation_enhancements(self, context: DecisionContext) -> List[str]:
        """Get narrative enhancements for general interpretations"""
        return [
            "Your thoughts are acknowledged and considered.",
            "The conversation flows naturally.",
            "Understanding builds between you and the world around you."
        ]
    
    def _create_error_decision(self, context: DecisionContext, error_message: str) -> DecisionResult:
        """Create error decision result"""
        return DecisionResult(
            priority_used=DecisionPriority.PARSER_FAILURE_FALLBACK,
            action_result=ActionResult(
                outcome=ActionOutcome.INVALID,
                action_type='error',
                details={'error': error_message},
                mechanics_triggered=False,
                error_message=error_message
            ),
            gm_response_base="I apologize, but I'm having trouble processing your request right now.",
            narrative_enhancements=["Please try again with a different approach."],
            requires_followup=True,
            metadata={'error': error_message}
        )
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get decision-making statistics"""
        return {
            'total_decisions': self.decision_stats['total_decisions'],
            'priority_usage': {
                priority.name: count 
                for priority, count in self.decision_stats['priority_usage'].items()
            },
            'action_outcomes': {
                outcome.value: count 
                for outcome, count in self.decision_stats['action_outcomes'].items()
            },
            'success_rate': (
                self.decision_stats['action_outcomes'][ActionOutcome.SUCCESS] / 
                max(1, self.decision_stats['total_decisions'])
            )
        }