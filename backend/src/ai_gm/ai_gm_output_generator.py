"""
AI GM Output Generator - Generates responses for player inputs.

This module is responsible for generating appropriate narrative responses
based on decision results and context, connecting the various components
of the AI GM Brain system.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime


class AIGMOutputGenerator:
    """
    Output generator for the AI GM Brain.
    
    Generates narrative responses based on decision results,
    world state, and other contextual factors.
    """
    
    def __init__(self, config: Dict[str, Any] = None, template_processor=None):
        """
        Initialize output generator.
        
        Args:
            config: Configuration for output generation
            template_processor: Template processor for rendering templates
        """
        self.logger = logging.getLogger("AIGMOutputGenerator")
        self.config = config or {}
        self.template_processor = template_processor
    
    async def generate_response(self, 
                            decision_result: Any, 
                            player_input: str,
                            context: Dict[str, Any],
                            additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a response based on decision result and context.
        
        Args:
            decision_result: Result from decision logic
            player_input: Original player input
            context: Current game context
            additional_data: Additional data to include in response
            
        Returns:
            Generated response including text and metadata
        """
        self.logger.info(f"Generating response for action type: {decision_result.action_type}")
        
        additional_data = additional_data or {}
        
        # Process based on action type
        if decision_result.action_type == 'INITIATE_NARRATIVE_BRANCH':
            return await self._generate_narrative_branch_response(decision_result, context)
            
        elif decision_result.action_type == 'EXECUTE_BRANCH_ACTION':
            return await self._generate_branch_action_response(decision_result, context)
            
        elif decision_result.action_type == 'EXECUTE_PARSED_COMMAND':
            return await self._generate_parsed_command_response(decision_result, context)
            
        elif decision_result.action_type == 'PROCESS_GENERAL_INTENT':
            return await self._generate_general_intent_response(decision_result, player_input, context)
            
        else:  # Fallback including PROVIDE_FALLBACK_RESPONSE
            return await self._generate_fallback_response(decision_result, player_input, context)
    
    async def _generate_narrative_branch_response(self, 
                                             decision_result: Any, 
                                             context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response for initiating a narrative branch.
        
        Args:
            decision_result: Decision result
            context: Current game context
            
        Returns:
            Generated response
        """
        # Get template from decision result or default
        template = decision_result.response_template
        
        if not template:
            template = "You discover a new opportunity for adventure."
        
        # Process template if template processor available
        response_text = self._process_template(
            template, 
            {
                **context,
                **decision_result.action_data,
                'success': decision_result.success
            }
        )
        
        return {
            'response_text': response_text,
            'metadata': {
                'action_type': decision_result.action_type,
                'success': decision_result.success,
                'opportunity_id': decision_result.action_data.get('opportunity_id'),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_branch_action_response(self, 
                                          decision_result: Any, 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response for executing a branch action.
        
        Args:
            decision_result: Decision result
            context: Current game context
            
        Returns:
            Generated response
        """
        # Get template from decision result or default
        template = decision_result.response_template
        
        if not template:
            if decision_result.success:
                template = "You successfully perform the action."
            else:
                template = "You were unable to complete that action."
        
        # Process template if template processor available
        response_text = self._process_template(
            template, 
            {
                **context,
                **decision_result.action_data,
                'success': decision_result.success
            }
        )
        
        return {
            'response_text': response_text,
            'metadata': {
                'action_type': decision_result.action_type,
                'success': decision_result.success,
                'branch_action': decision_result.action_data.get('branch_action'),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_parsed_command_response(self, 
                                           decision_result: Any, 
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response for executing a parsed command.
        
        Args:
            decision_result: Decision result
            context: Current game context
            
        Returns:
            Generated response
        """
        action = decision_result.action_data.get('action', '')
        
        # Get template from decision result or config
        template = decision_result.response_template
        
        if not template and hasattr(self.config, 'get_template_for_action'):
            template = self.config.get_template_for_action(action)
            
        if not template:
            template = f"You {action}."
            if decision_result.action_data.get('direct_object'):
                template = f"You {action} the {decision_result.action_data.get('direct_object')}."
        
        # Process template if template processor available
        template_context = {
            **context,
            'parsed_command': decision_result.action_data,
            'command': {'success': decision_result.success}
        }
        
        response_text = self._process_template(template, template_context)
        
        return {
            'response_text': response_text,
            'metadata': {
                'action_type': decision_result.action_type,
                'action': action,
                'direct_object': decision_result.action_data.get('direct_object'),
                'success': decision_result.success,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_general_intent_response(self, 
                                           decision_result: Any, 
                                           player_input: str,
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response for general intent without specific game action.
        
        Args:
            decision_result: Decision result
            player_input: Original player input
            context: Current game context
            
        Returns:
            Generated response
        """
        # Get suggested response from decision result
        response_text = decision_result.response_template
        
        if not response_text:
            response_text = "I understand what you're trying to do."
        
        # No template processing needed here as this comes directly from LLM
        
        return {
            'response_text': response_text,
            'metadata': {
                'action_type': decision_result.action_type,
                'player_intent': decision_result.action_data.get('player_intent', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_fallback_response(self, 
                                      decision_result: Any, 
                                      player_input: str,
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback response when no valid action could be determined.
        
        Args:
            decision_result: Decision result
            player_input: Original player input
            context: Current game context
            
        Returns:
            Generated response
        """
        # Get fallback message from decision result or config
        response_text = decision_result.response_template
        
        if not response_text and hasattr(self.config, 'ERROR_MESSAGES'):
            response_text = self.config.ERROR_MESSAGES.get('parsing_failed')
            
        if not response_text:
            response_text = "I'm not sure what you want to do. Could you try saying that differently?"
        
        return {
            'response_text': response_text,
            'metadata': {
                'action_type': decision_result.action_type,
                'original_input': player_input,
                'fallback_reason': decision_result.action_data.get('fallback_reason', 'UNKNOWN'),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def _process_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process a template with the given context.
        
        Args:
            template: Template string to process
            context: Context for template processing
            
        Returns:
            Processed template
        """
        if self.template_processor:
            try:
                return self.template_processor.process_template(template, context)
            except Exception as e:
                self.logger.error(f"Error processing template: {e}")
                return template
        
        # Basic template processing if no processor available
        return self._basic_template_processing(template, context)
    
    def _basic_template_processing(self, template: str, context: Dict[str, Any]) -> str:
        """
        Basic template processing as fallback.
        
        Args:
            template: Template string to process
            context: Context for template processing
            
        Returns:
            Processed template
        """
        # Handle simplest {var} replacements
        result = template
        
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                placeholder = "{" + key + "}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
        
        # Handle simple conditionals like {IF var}content{ENDIF}
        # This is a very basic implementation and doesn't handle nested conditions
        import re
        if_pattern = r'\{IF ([^}]+)\}(.*?)(?:\{ELSE\}(.*?))?\{ENDIF\}'
        
        def replace_if(match):
            condition = match.group(1).strip()
            true_content = match.group(2)
            false_content = match.group(3) or ''
            
            # Evaluate simple condition
            parts = condition.split('.')
            value = context
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break
            
            if value:
                return true_content
            return false_content
        
        result = re.sub(if_pattern, replace_if, result)
        
        return result