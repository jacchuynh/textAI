"""
AI GM Brain Response Generation Logic - Phase 4.1

Handles the final response generation based on Phase 3 decision outcomes.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum, auto
import logging
from datetime import datetime
import asyncio

# Import from core brain
from .ai_gm_brain import AIGMBrain


class ResponseMode(Enum):
    """Different modes for response generation"""
    DIRECT_LLM_ACKNOWLEDGEMENT = auto()
    NPC_DIALOGUE = auto()
    TEMPLATE_COMMAND_OUTCOME = auto()
    TEMPLATE_SCENE_DESCRIPTION = auto()
    TEMPLATE_BRANCH_OUTCOME = auto()
    CREATIVE_LLM_NARRATION = auto()
    FALLBACK_TEMPLATE = auto()


class ResponseComplexity(Enum):
    """Complexity levels for determining response generation strategy"""
    SIMPLE = "simple"           # Basic command outcomes
    MODERATE = "moderate"       # Branch actions, dialogue
    COMPLEX = "complex"         # Significant events, rich narration
    CRITICAL = "critical"       # Major story moments


class ResponseGenerationEngine:
    """
    Core engine for generating player responses based on decision outcomes
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the response generation engine.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"ResponseGenerator_{ai_gm_brain.game_id}")
        
        # Response generation statistics
        self.generation_stats = {
            'total_responses': 0,
            'mode_usage': {mode.name: 0 for mode in ResponseMode},
            'complexity_distribution': {complexity.value: 0 for complexity in ResponseComplexity},
            'llm_creative_calls': 0,
            'template_usage': 0,
            'dialogue_generations': 0
        }
        
        # Load response templates
        self._load_response_templates()
    
    def _load_response_templates(self):
        """Load response templates for different scenarios"""
        self.response_templates = {
            # Command outcome templates
            'command_outcomes': {
                'look_success': "You carefully observe {target}. {observation_details}",
                'look_failure': "You try to examine {target}, but {failure_reason}.",
                'take_success': "You pick up {target}. {acquisition_details}",
                'take_failure': "You cannot take {target}. {failure_reason}",
                'go_success': "You move {direction}. {movement_description}",
                'go_failure': "You cannot go {direction}. {obstacle_description}",
                'attack_success': "You strike {target}! {combat_result}",
                'attack_failure': "Your attack against {target} {failure_description}",
                'use_success': "You use {target}. {usage_effect}",
                'use_failure': "You cannot use {target} right now. {limitation_reason}",
                'talk_initiation': "You approach {target} to speak with them."
            },
            
            # Scene change templates
            'scene_changes': {
                'location_entered': "You enter {location_name}. {atmosphere_description} {feature_description}",
                'time_progression': "As {time_period} progresses, {temporal_changes}.",
                'weather_change': "The weather shifts. {weather_description}",
                'atmosphere_shift': "The mood of the place changes subtly. {new_atmosphere}"
            },
            
            # Branch outcome templates
            'branch_outcomes': {
                'skill_check_success': "Your {skill_type} proves sufficient. {success_description}",
                'skill_check_failure': "Despite your efforts, {failure_description}. {consequence_description}",
                'progress_made': "You make meaningful progress. {progress_description}",
                'setback_encountered': "You encounter an unexpected setback. {setback_description}",
                'branch_completed': "Your efforts culminate successfully. {completion_description}",
                'branch_failed': "Despite your best efforts, {failure_description}. {aftermath_description}"
            },
            
            # Generic acknowledgments
            'generic_responses': {
                'understanding': "I understand what you're getting at. {elaboration}",
                'clarification_needed': "I want to help, but could you be more specific about {unclear_aspect}?",
                'interesting_thought': "That's an interesting thought. {response_to_thought}",
                'considering_options': "You consider your options carefully. {options_summary}"
            },
            
            # Fallback responses
            'fallbacks': {
                'unclear_input': "I'm not entirely sure what you want to do. Could you try rephrasing that?",
                'system_limitation': "I understand your intent, but I need more specific information to help you.",
                'temporary_confusion': "Let me think about that for a moment... Could you clarify what you'd like to accomplish?"
            }
        }
    
    def generate_response(self, 
                        decision_result: Dict[str, Any],
                        game_context: Dict[str, Any],
                        interaction_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the final response based on decision result and context.
        
        Args:
            decision_result: Result from Phase 3 decision tree
            game_context: Current game state context
            interaction_context: Interaction-specific context
            
        Returns:
            Generated response with metadata
        """
        start_time = datetime.utcnow()
        self.generation_stats['total_responses'] += 1
        
        self.logger.info(f"Generating response for action: {decision_result.get('action_taken', 'unknown')}")
        
        try:
            # Determine response complexity
            complexity = self._determine_response_complexity(decision_result, game_context)
            self.generation_stats['complexity_distribution'][complexity.value] += 1
            
            # Choose response generation mode
            response_mode = self._choose_response_mode(decision_result, game_context, complexity)
            self.generation_stats['mode_usage'][response_mode.name] += 1
            
            # Generate response based on chosen mode
            response_data = self._generate_by_mode(
                response_mode, decision_result, game_context, interaction_context, complexity
            )
            
            # Add generation metadata
            response_data['generation_metadata'] = {
                'mode_used': response_mode.name,
                'complexity': complexity.value,
                'generation_time': (datetime.utcnow() - start_time).total_seconds(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._generate_fallback_response(decision_result, str(e))
    
    def _determine_response_complexity(self, 
                                     decision_result: Dict[str, Any],
                                     game_context: Dict[str, Any]) -> ResponseComplexity:
        """Determine the complexity level of the response needed"""
        
        # Critical complexity for major narrative events
        if (decision_result.get('action_taken') == 'initiate_narrative_branch' and
            decision_result.get('success', False)):
            return ResponseComplexity.CRITICAL
        
        # Complex for significant branch actions or combat
        if ('branch_action' in str(decision_result.get('action_taken', '')) or
            decision_result.get('response_basis') == 'aligned_branch_action'):
            return ResponseComplexity.COMPLEX
        
        # Moderate for dialogue, general interpretation, or parsed commands with context
        if (decision_result.get('response_basis') == 'llm_interpretation' or
            self._involves_npc_interaction(decision_result, game_context) or
            'parsed_command' in str(decision_result.get('action_taken', ''))):
            return ResponseComplexity.MODERATE
        
        # Simple for basic commands and fallbacks
        return ResponseComplexity.SIMPLE
    
    def _choose_response_mode(self, 
                            decision_result: Dict[str, Any],
                            game_context: Dict[str, Any],
                            complexity: ResponseComplexity) -> ResponseMode:
        """Choose the appropriate response generation mode"""
        
        # Direct LLM acknowledgement if available and suitable
        suggested_response = decision_result.get('suggested_response')
        if suggested_response and len(suggested_response) > 20:
            return ResponseMode.DIRECT_LLM_ACKNOWLEDGEMENT
        
        # NPC dialogue for character interactions
        if self._involves_npc_interaction(decision_result, game_context):
            return ResponseMode.NPC_DIALOGUE
        
        # Creative LLM narration for complex/critical events
        if complexity in [ResponseComplexity.COMPLEX, ResponseComplexity.CRITICAL]:
            return ResponseMode.CREATIVE_LLM_NARRATION
        
        # Template-based responses for specific action types
        action_taken = decision_result.get('action_taken', '')
        if 'parsed_command' in action_taken:
            return ResponseMode.TEMPLATE_COMMAND_OUTCOME
        elif 'branch_action' in action_taken or 'initiate_narrative_branch' in action_taken:
            return ResponseMode.TEMPLATE_BRANCH_OUTCOME
        
        # Scene description for location/atmosphere changes
        if self._involves_scene_change(decision_result, game_context):
            return ResponseMode.TEMPLATE_SCENE_DESCRIPTION
        
        # Fallback to template
        return ResponseMode.FALLBACK_TEMPLATE
    
    def _generate_by_mode(self,
                        mode: ResponseMode,
                        decision_result: Dict[str, Any],
                        game_context: Dict[str, Any],
                        interaction_context: Dict[str, Any],
                        complexity: ResponseComplexity) -> Dict[str, Any]:
        """Generate response based on the chosen mode"""
        
        if mode == ResponseMode.DIRECT_LLM_ACKNOWLEDGEMENT:
            return self._generate_direct_acknowledgement(decision_result, game_context)
        
        elif mode == ResponseMode.NPC_DIALOGUE:
            return self._generate_npc_dialogue(decision_result, game_context, interaction_context)
        
        elif mode == ResponseMode.TEMPLATE_COMMAND_OUTCOME:
            return self._generate_command_outcome(decision_result, game_context)
        
        elif mode == ResponseMode.TEMPLATE_SCENE_DESCRIPTION:
            return self._generate_scene_description(decision_result, game_context)
        
        elif mode == ResponseMode.TEMPLATE_BRANCH_OUTCOME:
            return self._generate_branch_outcome(decision_result, game_context)
        
        elif mode == ResponseMode.CREATIVE_LLM_NARRATION:
            return self._generate_creative_narration(decision_result, game_context, complexity)
        
        else:  # FALLBACK_TEMPLATE
            return self._generate_fallback_template(decision_result, game_context)
    
    def _generate_direct_acknowledgement(self,
                                       decision_result: Dict[str, Any],
                                       game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Use the LLM's suggested acknowledgement directly"""
        
        response_text = decision_result.get('suggested_response', '')
        
        # Enhance with mechanical outcome if available
        mechanical_outcome = decision_result.get('mechanical_outcome')
        if mechanical_outcome:
            outcome_message = mechanical_outcome.get('message', '')
            if outcome_message and outcome_message not in response_text:
                response_text = f"{response_text} {outcome_message}"
        
        return {
            'response_text': response_text,
            'response_source': 'llm_direct',
            'enhancements_applied': bool(mechanical_outcome)
        }
    
    def _generate_npc_dialogue(self,
                             decision_result: Dict[str, Any],
                             game_context: Dict[str, Any],
                             interaction_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NPC dialogue response"""
        self.generation_stats['dialogue_generations'] += 1
        
        # For now, simulate NPC dialogue generation
        # In a complete implementation, this would use a dialogue generator
        
        # Determine target NPC
        npc_id = self._extract_npc_from_context(decision_result, game_context)
        if not npc_id:
            npc_id = "default_narrator"
        
        # Fallback to suggested response or template
        base_response = decision_result.get('suggested_response', '')
        if not base_response:
            base_response = "The character responds to your interaction."
        
        dialogue_text = f"{base_response}"
        
        return {
            'response_text': dialogue_text,
            'response_source': 'npc_dialogue',
            'npc_id': npc_id
        }
    
    def _generate_command_outcome(self,
                                decision_result: Dict[str, Any],
                                game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate command outcome response using templates"""
        self.generation_stats['template_usage'] += 1
        
        # Parse the action from decision_result
        action_taken = decision_result.get('action_taken', '')
        action_parts = action_taken.split('_', 1)
        
        command = action_parts[1] if len(action_parts) > 1 else 'unknown'
        success = decision_result.get('success', False)
        
        # Determine template key
        template_key = f"{command}_{'success' if success else 'failure'}"
        template = self.response_templates['command_outcomes'].get(
            template_key, "You {action} {target}.")
        
        # Get mechanical outcome for details
        mechanical_outcome = decision_result.get('mechanical_outcome', {})
        
        # Prepare template variables
        template_vars = {
            'action': command,
            'target': mechanical_outcome.get('target', 'something'),
            'observation_details': mechanical_outcome.get('details', 'You notice nothing unusual.'),
            'acquisition_details': mechanical_outcome.get('details', 'It is now in your possession.'),
            'movement_description': mechanical_outcome.get('details', 'You arrive at a new location.'),
            'obstacle_description': mechanical_outcome.get('message', 'There is something blocking your way.'),
            'combat_result': mechanical_outcome.get('details', 'You deal some damage.'),
            'failure_description': mechanical_outcome.get('message', 'misses completely.'),
            'failure_reason': mechanical_outcome.get('message', "it's not possible at the moment."),
            'usage_effect': mechanical_outcome.get('details', 'It has an effect.'),
            'limitation_reason': mechanical_outcome.get('message', "it's not the right time or place.")
        }
        
        # Process the template
        response_text = self._process_template(template, template_vars)
        
        # Fallback to suggested response if template processing failed
        if not response_text:
            response_text = decision_result.get('suggested_response', "You take that action.")
        
        return {
            'response_text': response_text,
            'response_source': 'command_template',
            'template_used': template_key
        }
    
    def _generate_scene_description(self,
                                  decision_result: Dict[str, Any],
                                  game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scene description response using templates"""
        self.generation_stats['template_usage'] += 1
        
        # Determine template key based on the type of scene change
        template_key = 'location_entered'  # Default
        
        # Get scene context from game_context
        location_name = game_context.get('location', {}).get('name', 'an area')
        location_atmosphere = game_context.get('location', {}).get('atmosphere', '')
        location_features = game_context.get('location', {}).get('features', [])
        
        # Prepare template variables
        template_vars = {
            'location_name': location_name,
            'atmosphere_description': location_atmosphere or 'The atmosphere is neutral.',
            'feature_description': self._format_feature_list(location_features),
            'time_period': game_context.get('time', {}).get('period', 'the day'),
            'temporal_changes': game_context.get('time', {}).get('changes', 'time passes'),
            'weather_description': game_context.get('weather', {}).get('description', 'The weather is unremarkable.'),
            'new_atmosphere': game_context.get('atmosphere', {}).get('new', 'There is a subtle shift in the atmosphere.')
        }
        
        # Get the appropriate template
        template = self.response_templates['scene_changes'].get(
            template_key, "You observe your surroundings.")
        
        # Process the template
        response_text = self._process_template(template, template_vars)
        
        # Fallback to suggested response if template processing failed
        if not response_text:
            response_text = decision_result.get('suggested_response', "You take in your surroundings.")
        
        return {
            'response_text': response_text,
            'response_source': 'scene_template',
            'template_used': template_key
        }
    
    def _generate_branch_outcome(self,
                               decision_result: Dict[str, Any],
                               game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate narrative branch outcome response using templates"""
        self.generation_stats['template_usage'] += 1
        
        # Determine template key based on the outcome
        success = decision_result.get('success', False)
        mechanical_outcome = decision_result.get('mechanical_outcome', {})
        
        # Determine appropriate template key
        if 'skill_check' in str(mechanical_outcome):
            template_key = 'skill_check_success' if success else 'skill_check_failure'
        elif success:
            template_key = 'branch_completed' if mechanical_outcome.get('completed', False) else 'progress_made'
        else:
            template_key = 'branch_failed' if mechanical_outcome.get('failed', False) else 'setback_encountered'
        
        # Prepare template variables
        template_vars = {
            'skill_type': mechanical_outcome.get('skill_type', 'skill'),
            'success_description': mechanical_outcome.get('message', 'You succeed in your task.'),
            'failure_description': mechanical_outcome.get('message', 'you fall short of your goal'),
            'consequence_description': mechanical_outcome.get('consequence', 'You must find another approach.'),
            'progress_description': mechanical_outcome.get('details', 'You advance your objectives.'),
            'setback_description': mechanical_outcome.get('details', 'You encounter an obstacle.'),
            'completion_description': mechanical_outcome.get('details', 'You achieve what you set out to do.'),
            'aftermath_description': mechanical_outcome.get('aftermath', 'You must reconsider your approach.')
        }
        
        # Get the appropriate template
        template = self.response_templates['branch_outcomes'].get(
            template_key, "Your actions yield {result}.")
        
        # Process the template
        response_text = self._process_template(template, template_vars)
        
        # Fallback to suggested response if template processing failed
        if not response_text:
            response_text = decision_result.get('suggested_response', "Your actions have consequences.")
        
        return {
            'response_text': response_text,
            'response_source': 'branch_template',
            'template_used': template_key
        }
    
    def _generate_creative_narration(self,
                                  decision_result: Dict[str, Any],
                                  game_context: Dict[str, Any],
                                  complexity: ResponseComplexity) -> Dict[str, Any]:
        """Generate creative narration for significant events"""
        self.generation_stats['llm_creative_calls'] += 1
        
        # In a full implementation, this would call an LLM for creative narration
        # For now, we'll use the suggested response with embellishments
        
        base_response = decision_result.get('suggested_response', '')
        if not base_response:
            # Fallback to a generic description based on action type
            action_taken = decision_result.get('action_taken', '')
            if 'narrative_branch' in action_taken:
                base_response = "A new opportunity presents itself, drawing your attention."
            elif 'branch_action' in action_taken:
                base_response = "Your actions have significant consequences in this moment."
            else:
                base_response = "The situation develops in an interesting way."
        
        # Add some embellishment based on the complexity
        if complexity == ResponseComplexity.CRITICAL:
            narrative_enhancement = " The weight of this moment seems to hang in the air, as if the very fabric of reality acknowledges your choice."
        else:
            narrative_enhancement = " There's a sense that this moment will be remembered."
        
        response_text = f"{base_response}{narrative_enhancement}"
        
        return {
            'response_text': response_text,
            'response_source': 'creative_narration',
            'complexity_level': complexity.value
        }
    
    def _generate_fallback_template(self,
                                 decision_result: Dict[str, Any],
                                 game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when other methods fail"""
        
        # Select appropriate fallback from templates
        template_key = 'unclear_input'
        if decision_result.get('error'):
            template_key = 'system_limitation'
        
        fallback_text = self.response_templates['fallbacks'].get(template_key)
        
        # Use suggested response if available
        suggested = decision_result.get('suggested_response')
        if suggested:
            response_text = suggested
        else:
            response_text = fallback_text or "I understand. What would you like to do next?"
        
        return {
            'response_text': response_text,
            'response_source': 'fallback_template',
            'error': decision_result.get('error')
        }
    
    def _generate_fallback_response(self, 
                                  decision_result: Dict[str, Any],
                                  error: str) -> Dict[str, Any]:
        """Generate emergency fallback response when an error occurs"""
        
        # Try to use suggested response
        suggested = decision_result.get('suggested_response')
        if suggested:
            response_text = suggested
        else:
            response_text = "I'm processing that... Could you tell me more about what you'd like to do?"
        
        return {
            'response_text': response_text,
            'response_source': 'error_fallback',
            'error': error
        }
    
    def _process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Process a template by replacing variables"""
        try:
            # Basic variable replacement
            result = template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
            
            # Remove IF/ENDIF blocks where condition is not met
            # This is a simplified implementation
            import re
            if_pattern = r"\{IF ([^}]+)\}(.*?)\{ENDIF\}"
            
            def replace_conditional(match):
                condition = match.group(1)
                content = match.group(2)
                if variables.get(condition):
                    return content
                return ""
            
            result = re.sub(if_pattern, replace_conditional, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Template processing error: {e}")
            return ""
    
    def _involves_npc_interaction(self, 
                                decision_result: Dict[str, Any],
                                game_context: Dict[str, Any]) -> bool:
        """Check if the decision involves NPC interaction"""
        action = decision_result.get('action_taken', '')
        if 'talk' in action or 'speak' in action or 'ask' in action:
            return True
        
        # Check if there's an NPC target
        mechanical_outcome = decision_result.get('mechanical_outcome', {})
        target = mechanical_outcome.get('target', '')
        npcs = game_context.get('npcs', [])
        
        return any(npc.get('name', '') == target for npc in npcs)
    
    def _involves_scene_change(self, 
                             decision_result: Dict[str, Any],
                             game_context: Dict[str, Any]) -> bool:
        """Check if the decision involves a scene/location change"""
        action = decision_result.get('action_taken', '')
        return ('go' in action or 'move' in action or 'enter' in action or 
                'travel' in action or 'explore' in action)
    
    def _extract_npc_from_context(self, 
                                decision_result: Dict[str, Any],
                                game_context: Dict[str, Any]) -> Optional[str]:
        """Extract the NPC ID from the context"""
        mechanical_outcome = decision_result.get('mechanical_outcome', {})
        target = mechanical_outcome.get('target', '')
        
        # Find NPC in game context
        npcs = game_context.get('npcs', [])
        for npc in npcs:
            if npc.get('name', '') == target:
                return npc.get('id', '')
        
        return None
    
    def _format_feature_list(self, features: List[str]) -> str:
        """Format a list of features into a readable string"""
        if not features:
            return ""
        
        if len(features) == 1:
            return f"You notice {features[0]}."
        elif len(features) == 2:
            return f"You notice {features[0]} and {features[1]}."
        else:
            formatted = ", ".join(features[:-1])
            return f"You notice {formatted}, and {features[-1]}."
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics on response generation"""
        return self.generation_stats


# Extension function to add response generation to AI GM Brain
def extend_ai_gm_brain_with_response_generator(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with response generation capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create response generator
    response_generator = ResponseGenerationEngine(ai_gm_brain)
    
    # Store the response generator for future reference
    ai_gm_brain.response_generator = response_generator
    
    # Add response generation method to the AI GM Brain
    ai_gm_brain.generate_response = lambda decision_result, game_context, interaction_context: response_generator.generate_response(
        decision_result, game_context, interaction_context
    )