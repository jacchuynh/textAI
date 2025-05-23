"""
AI GM Brain Response Generation Logic - Phase 4.1

Handles the final response generation based on Phase 3 decision outcomes.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum, auto
import logging
from datetime import datetime
import asyncio

from decision_logic.decision_tree import DecisionResult, ActionResult, ActionOutcome, DecisionPriority
from ai_gm_dialogue_generator import AIGMDialogueGenerator
from template_processor_enhanced import TemplateProcessor
from llm_integration.openrouter_llm import EnhancedLLMManager


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
    
    def __init__(self, 
                 dialogue_generator: AIGMDialogueGenerator,
                 template_processor: TemplateProcessor,
                 llm_manager: EnhancedLLMManager,
                 db_service=None):
        """
        Initialize the response generation engine.
        
        Args:
            dialogue_generator: NPC dialogue generator
            template_processor: Template processor for responses
            llm_manager: LLM manager for creative narration
            db_service: Database service for logging
        """
        self.dialogue_generator = dialogue_generator
        self.template_processor = template_processor
        self.llm_manager = llm_manager
        self.db_service = db_service
        self.logger = logging.getLogger("ResponseGenerationEngine")
        
        # Response generation statistics
        self.generation_stats = {
            'total_responses': 0,
            'mode_usage': {mode: 0 for mode in ResponseMode},
            'complexity_distribution': {complexity: 0 for complexity in ResponseComplexity},
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
                'location_entered': "You enter {location_name}. {IF location_atmosphere}{atmosphere_description}{ENDIF} {IF notable_features}{feature_description}{ENDIF}",
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
    
    async def generate_response(self, 
                              decision_result: DecisionResult,
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
        
        self.logger.info(f"Generating response for priority {decision_result.priority_used.name}")
        
        try:
            # Determine response complexity
            complexity = self._determine_response_complexity(decision_result, game_context)
            self.generation_stats['complexity_distribution'][complexity] += 1
            
            # Choose response generation mode
            response_mode = self._choose_response_mode(decision_result, game_context, complexity)
            self.generation_stats['mode_usage'][response_mode] += 1
            
            # Generate response based on chosen mode
            response_data = await self._generate_by_mode(
                response_mode, decision_result, game_context, interaction_context, complexity
            )
            
            # Add generation metadata
            response_data['generation_metadata'] = {
                'mode_used': response_mode.name,
                'complexity': complexity.value,
                'generation_time': (datetime.utcnow() - start_time).total_seconds(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log the response generation
            if self.db_service:
                await self._log_response_generation(response_data, decision_result, interaction_context)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return await self._generate_fallback_response(decision_result, str(e))
    
    def _determine_response_complexity(self, 
                                     decision_result: DecisionResult,
                                     game_context: Dict[str, Any]) -> ResponseComplexity:
        """Determine the complexity level of the response needed"""
        
        # Critical complexity for major events
        if (decision_result.action_result and 
            decision_result.action_result.action_type == 'opportunity_initiation' and
            decision_result.action_result.outcome == ActionOutcome.SUCCESS):
            return ResponseComplexity.CRITICAL
        
        # Complex for significant branch actions or major failures
        if (decision_result.priority_used == DecisionPriority.LLM_BRANCH_ACTION_ALIGNMENT or
            (decision_result.action_result and 
             decision_result.action_result.mechanics_triggered and
             decision_result.action_result.outcome in [ActionOutcome.SUCCESS, ActionOutcome.FAILURE])):
            return ResponseComplexity.COMPLEX
        
        # Moderate for dialogue, general interpretation, or parsed commands with context
        if (decision_result.priority_used in [DecisionPriority.GENERAL_LLM_INTERPRETATION] or
            self._involves_npc_interaction(decision_result, game_context) or
            self._has_rich_context(game_context)):
            return ResponseComplexity.MODERATE
        
        # Simple for basic commands and fallbacks
        return ResponseComplexity.SIMPLE
    
    def _choose_response_mode(self, 
                            decision_result: DecisionResult,
                            game_context: Dict[str, Any],
                            complexity: ResponseComplexity) -> ResponseMode:
        """Choose the appropriate response generation mode"""
        
        # Direct LLM acknowledgement if available and suitable
        if (decision_result.gm_response_base and 
            len(decision_result.gm_response_base) > 20 and
            not self._needs_enhancement(decision_result, complexity)):
            return ResponseMode.DIRECT_LLM_ACKNOWLEDGEMENT
        
        # NPC dialogue for character interactions
        if self._involves_npc_interaction(decision_result, game_context):
            return ResponseMode.NPC_DIALOGUE
        
        # Creative LLM narration for complex/critical events
        if (complexity in [ResponseComplexity.COMPLEX, ResponseComplexity.CRITICAL] and
            self._should_use_creative_llm(decision_result, game_context)):
            return ResponseMode.CREATIVE_LLM_NARRATION
        
        # Template-based responses for specific action types
        if decision_result.action_result:
            if decision_result.action_result.action_type == 'parsed_command':
                return ResponseMode.TEMPLATE_COMMAND_OUTCOME
            elif decision_result.action_result.action_type in ['branch_action', 'opportunity_initiation']:
                return ResponseMode.TEMPLATE_BRANCH_OUTCOME
        
        # Scene description for location/atmosphere changes
        if self._involves_scene_change(decision_result, game_context):
            return ResponseMode.TEMPLATE_SCENE_DESCRIPTION
        
        # Fallback to template
        return ResponseMode.FALLBACK_TEMPLATE
    
    async def _generate_by_mode(self,
                              mode: ResponseMode,
                              decision_result: DecisionResult,
                              game_context: Dict[str, Any],
                              interaction_context: Dict[str, Any],
                              complexity: ResponseComplexity) -> Dict[str, Any]:
        """Generate response based on the chosen mode"""
        
        if mode == ResponseMode.DIRECT_LLM_ACKNOWLEDGEMENT:
            return await self._generate_direct_acknowledgement(decision_result, game_context)
        
        elif mode == ResponseMode.NPC_DIALOGUE:
            return await self._generate_npc_dialogue(decision_result, game_context, interaction_context)
        
        elif mode == ResponseMode.TEMPLATE_COMMAND_OUTCOME:
            return await self._generate_command_outcome(decision_result, game_context)
        
        elif mode == ResponseMode.TEMPLATE_SCENE_DESCRIPTION:
            return await self._generate_scene_description(decision_result, game_context)
        
        elif mode == ResponseMode.TEMPLATE_BRANCH_OUTCOME:
            return await self._generate_branch_outcome(decision_result, game_context)
        
        elif mode == ResponseMode.CREATIVE_LLM_NARRATION:
            return await self._generate_creative_narration(decision_result, game_context, complexity)
        
        else:  # FALLBACK_TEMPLATE
            return await self._generate_fallback_template(decision_result, game_context)
    
    async def _generate_direct_acknowledgement(self,
                                             decision_result: DecisionResult,
                                             game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Use the LLM's suggested acknowledgement directly"""
        
        response_text = decision_result.gm_response_base
        
        # Enhance with narrative elements if available
        if decision_result.narrative_enhancements:
            enhancement = decision_result.narrative_enhancements[0]  # Use first enhancement
            response_text = f"{response_text} {enhancement}"
        
        return {
            'response_text': response_text,
            'response_source': 'llm_direct',
            'enhancements_applied': len(decision_result.narrative_enhancements)
        }
    
    async def _generate_npc_dialogue(self,
                                   decision_result: DecisionResult,
                                   game_context: Dict[str, Any],
                                   interaction_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NPC dialogue response"""
        self.generation_stats['dialogue_generations'] += 1
        
        # Determine target NPC
        npc_id = self._extract_npc_from_context(decision_result, game_context)
        if not npc_id:
            npc_id = "default_narrator"
        
        # Determine dialogue themes
        dialogue_themes = self._determine_dialogue_themes(decision_result, game_context)
        
        try:
            # Generate dialogue using AIGMDialogueGenerator
            dialogue_response = self.dialogue_generator.generate_dialogue(
                npc_id=npc_id,
                dialogue_themes=dialogue_themes,
                context=game_context,
                player_id=interaction_context.get('player_id', 'unknown')
            )
            
            # Combine with base response if needed
            if decision_result.gm_response_base and dialogue_response:
                response_text = f"{decision_result.gm_response_base}\n\n{dialogue_response}"
            else:
                response_text = dialogue_response or decision_result.gm_response_base
            
            return {
                'response_text': response_text,
                'response_source': 'npc_dialogue',
                'npc_id': npc_id,
                'dialogue_themes': dialogue_themes
            }
            
        except Exception as e:
            self.logger.error(f"Error generating NPC dialogue: {e}")
            # Fallback to base response
            return {
                'response_text': decision_result.gm_response_base or "The character looks at you thoughtfully.",
                'response_source': 'npc_dialogue_fallback',
                'error': str(e)
            }
    
    async def _generate_command_outcome(self,
                                      decision_result: DecisionResult,
                                      game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for parsed command outcomes"""
        self.generation_stats['template_usage'] += 1
        
        if not decision_result.action_result:
            return await self._generate_fallback_template(decision_result, game_context)
        
        action_result = decision_result.action_result
        execution_result = action_result.details.get('execution_result', {})
        
        # Determine command and outcome
        command = execution_result.get('command', 'unknown')
        success = execution_result.get('success', False)
        
        # Build template context
        template_context = {
            'target': self._extract_target_from_result(action_result),
            'success': success,
            'failure_reason': execution_result.get('failure_reason', 'unknown circumstances prevent this'),
            **self._build_command_context(action_result, game_context)
        }
        
        # Choose appropriate template
        template_key = f"{command}_{'success' if success else 'failure'}"
        template = self.response_templates['command_outcomes'].get(
            template_key, 
            self.response_templates['command_outcomes'].get(f"{command}_success", 
                "You {command}. {IF success}It works.{ELSE}It doesn't work as expected.{ENDIF}")
        )
        
        # Process template
        response_text = self.template_processor.process(template, template_context)
        
        return {
            'response_text': response_text,
            'response_source': 'command_template',
            'template_used': template_key,
            'command': command,
            'success': success
        }
    
    async def _generate_scene_description(self,
                                        decision_result: DecisionResult,
                                        game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scene description response"""
        self.generation_stats['template_usage'] += 1
        
        # Determine scene change type
        scene_type = self._determine_scene_change_type(decision_result, game_context)
        
        # Build template context
        template_context = {
            'location_name': game_context.get('location_name', 'the area'),
            'atmosphere_description': self._get_atmosphere_description(game_context),
            'feature_description': self._get_notable_features(game_context),
            'time_period': game_context.get('time_of_day', 'the day'),
            'temporal_changes': self._get_temporal_changes(game_context),
            'weather_description': self._get_weather_description(game_context),
            'new_atmosphere': self._get_new_atmosphere(game_context),
            **game_context
        }
        
        # Get appropriate template
        template = self.response_templates['scene_changes'].get(
            scene_type, 
            self.response_templates['scene_changes']['location_entered']
        )
        
        # Process template
        response_text = self.template_processor.process(template, template_context)
        
        return {
            'response_text': response_text,
            'response_source': 'scene_template',
            'scene_type': scene_type
        }
    
    async def _generate_branch_outcome(self,
                                     decision_result: DecisionResult,
                                     game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for branch action outcomes"""
        self.generation_stats['template_usage'] += 1
        
        if not decision_result.action_result:
            return await self._generate_fallback_template(decision_result, game_context)
        
        action_result = decision_result.action_result
        
        # Determine outcome type
        if action_result.outcome == ActionOutcome.SUCCESS:
            outcome_type = 'skill_check_success'
        elif action_result.outcome == ActionOutcome.FAILURE:
            outcome_type = 'skill_check_failure'
        elif action_result.action_type == 'opportunity_initiation':
            outcome_type = 'progress_made' if action_result.outcome == ActionOutcome.SUCCESS else 'setback_encountered'
        else:
            outcome_type = 'skill_check_success'  # Default
        
        # Build template context
        skill_check = action_result.details.get('skill_check', {})
        template_context = {
            'skill_type': self._determine_skill_type(action_result, game_context),
            'success_description': action_result.details.get('message', 'Your efforts pay off.'),
            'failure_description': skill_check.get('failure_reason', 'the task proves challenging'),
            'consequence_description': self._get_consequence_description(action_result, game_context),
            'progress_description': self._get_progress_description(action_result, game_context),
            'setback_description': self._get_setback_description(action_result, game_context),
            **game_context
        }
        
        # Get template and process
        template = self.response_templates['branch_outcomes'].get(outcome_type, 
            "You attempt the task. {IF success}It succeeds.{ELSE}It doesn't go as planned.{ENDIF}")
        
        response_text = self.template_processor.process(template, template_context)
        
        return {
            'response_text': response_text,
            'response_source': 'branch_template',
            'outcome_type': outcome_type,
            'skill_check_result': skill_check
        }
    
    async def _generate_creative_narration(self,
                                         decision_result: DecisionResult,
                                         game_context: Dict[str, Any],
                                         complexity: ResponseComplexity) -> Dict[str, Any]:
        """Generate creative LLM narration for significant events"""
        self.generation_stats['llm_creative_calls'] += 1
        
        # Build creative narration prompt
        prompt = self._build_creative_narration_prompt(decision_result, game_context, complexity)
        
        try:
            # Determine optimal model for creative narration
            model = self.llm_manager.get_optimal_model("narrative_generation", complexity.value)
            
            # Call LLM for creative narration
            llm_result = await self.llm_manager.call_llm_with_tracking(
                prompt=prompt,
                model=model,
                prompt_mode="creative_narration",
                temperature=0.8,  # Higher temperature for creativity
                max_tokens=300
            )
            
            if llm_result['success']:
                response_text = llm_result['content'].strip()
                
                # Enhance with base response if needed
                if decision_result.gm_response_base and response_text:
                    response_text = f"{decision_result.gm_response_base}\n\n{response_text}"
                
                return {
                    'response_text': response_text,
                    'response_source': 'creative_llm',
                    'model_used': model,
                    'tokens_used': llm_result['tokens_used'],
                    'cost_estimate': llm_result['cost_estimate']
                }
            else:
                # Fallback if LLM fails
                return await self._generate_fallback_template(decision_result, game_context)
                
        except Exception as e:
            self.logger.error(f"Error in creative LLM narration: {e}")
            return await self._generate_fallback_template(decision_result, game_context)
    
    def _build_creative_narration_prompt(self,
                                       decision_result: DecisionResult,
                                       game_context: Dict[str, Any],
                                       complexity: ResponseComplexity) -> str:
        """Build prompt for creative LLM narration"""
        
        # Extract event details
        event_summary = self._create_event_summary(decision_result, game_context)
        
        # Get character context
        player_name = game_context.get('player_name', 'the adventurer')
        player_status = game_context.get('player_status_summary', 'alert and ready')
        player_emotion = game_context.get('player_dominant_emotion', 'focused')
        
        # Get NPC context if relevant
        npc_context = ""
        npc_id = self._extract_npc_from_context(decision_result, game_context)
        if npc_id and npc_id != "default_narrator":
            npc_data = game_context.get('npcs', {}).get(npc_id, {})
            npc_name = npc_data.get('name', 'a character')
            npc_emotion = npc_data.get('dominant_emotion', 'neutral')
            relationship = npc_data.get('relationship_to_player', 'unknown')
            npc_context = f"Key NPC Involved: {npc_name} (current emotion: {npc_emotion}, relationship to player: {relationship})"
        else:
            npc_context = "Key NPC Involved: None"
        
        # Get location context
        location_name = game_context.get('location_name', 'the current location')
        location_aura = game_context.get('location_context', {}).get('dominant_aura', 'neutral')
        world_state_summary = self._get_world_state_summary(game_context)
        
        # Determine desired tone
        desired_tone = self._determine_narrative_tone(decision_result, complexity)
        
        prompt = f"""You are a master storyteller AI Game Master.

Event Summary: {event_summary}
Player: {player_name} ({player_status}, current emotion: {player_emotion})
{npc_context}
Current Location: {location_name} (atmosphere: {location_aura}, world state: {world_state_summary})
Desired Tone: {desired_tone}

Narrate this event or its immediate aftermath vividly and immersively in 1-3 sentences. Focus on sensory details and emotional impact."""
        
        return prompt
    
    async def _generate_fallback_template(self,
                                        decision_result: DecisionResult,
                                        game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response using templates"""
        self.generation_stats['template_usage'] += 1
        
        # Use base response if available
        if decision_result.gm_response_base:
            response_text = decision_result.gm_response_base
            
            # Add narrative enhancements
            if decision_result.narrative_enhancements:
                enhancement = decision_result.narrative_enhancements[0]
                response_text = f"{response_text} {enhancement}"
            
            return {
                'response_text': response_text,
                'response_source': 'fallback_base'
            }
        
        # Use generic template
        template_context = {
            'unclear_aspect': 'what you want to accomplish',
            'elaboration': 'Let me know how I can help.',
            'response_to_thought': 'Tell me more about what you\'re thinking.',
            'options_summary': 'There are several paths available to you.',
            **game_context
        }
        
        # Choose appropriate fallback
        if decision_result.requires_followup:
            template = self.response_templates['generic_responses']['clarification_needed']
        else:
            template = self.response_templates['generic_responses']['understanding']
        
        response_text = self.template_processor.process(template, template_context)
        
        return {
            'response_text': response_text,
            'response_source': 'fallback_template'
        }
    
    async def _generate_fallback_response(self,
                                        decision_result: DecisionResult,
                                        error_message: str) -> Dict[str, Any]:
        """Generate fallback response for errors"""
        fallback_responses = [
            "I need a moment to process that. Could you try again?",
            "Something seems unclear to me. Could you rephrase your request?",
            "I want to help, but I'm having trouble understanding what you want to do."
        ]
        
        import random
        response_text = random.choice(fallback_responses)
        
        return {
            'response_text': response_text,
            'response_source': 'error_fallback',
            'error': error_message,
            'generation_metadata': {
                'mode_used': 'ERROR_FALLBACK',
                'complexity': 'SIMPLE',
                'generation_time': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    # Helper methods for context analysis and generation
    
    def _needs_enhancement(self, decision_result: DecisionResult, complexity: ResponseComplexity) -> bool:
        """Check if response needs enhancement beyond direct acknowledgement"""
        return (complexity in [ResponseComplexity.COMPLEX, ResponseComplexity.CRITICAL] or
                len(decision_result.narrative_enhancements) > 0)
    
    def _involves_npc_interaction(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> bool:
        """Check if response involves NPC interaction"""
        # Check if action involves talking or NPC presence
        if decision_result.action_result:
            details = decision_result.action_result.details
            if 'talk' in str(details).lower() or 'npc' in str(details).lower():
                return True
        
        # Check if there are active NPCs in context
        return bool(game_context.get('active_npcs') or game_context.get('present_npcs'))
    
    def _should_use_creative_llm(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> bool:
        """Check if creative LLM should be used"""
        # Use for significant events
        if (decision_result.action_result and 
            decision_result.action_result.action_type == 'opportunity_initiation' and
            decision_result.action_result.outcome == ActionOutcome.SUCCESS):
            return True
        
        # Use for critical branch outcomes
        if (decision_result.action_result and 
            decision_result.action_result.action_type == 'branch_action' and
            decision_result.action_result.details.get('skill_check', {}).get('roll', 0) >= 18):
            return True
        
        # Use sparingly - check cooldown or frequency limits
        return self.generation_stats['llm_creative_calls'] < 3  # Limit creative calls
    
    def _involves_scene_change(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> bool:
        """Check if response involves scene changes"""
        if decision_result.action_result:
            details = decision_result.action_result.details
            return ('location' in str(details).lower() or 
                   'movement' in str(details).lower() or
                   'go' in str(details).lower())
        return False
    
    def _extract_npc_from_context(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> Optional[str]:
        """Extract NPC ID from context"""
        # Check action result for NPC references
        if decision_result.action_result:
            details = decision_result.action_result.details
            if 'npc_id' in details:
                return details['npc_id']
        
        # Check for active NPCs
        active_npcs = game_context.get('active_npcs', [])
        if active_npcs:
            return active_npcs[0]  # Return first active NPC
        
        return None
    
    def _determine_dialogue_themes(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> List[str]:
        """Determine appropriate dialogue themes"""
        themes = []
        
        # Check world state for themes
        world_state = game_context.get('world_state', {})
        if world_state.get('political_stability') in ['unrest', 'rebellion']:
            themes.append('caution')
        
        # Check action outcome for themes
        if decision_result.action_result:
            if decision_result.action_result.outcome == ActionOutcome.SUCCESS:
                themes.append('encouragement')
            elif decision_result.action_result.outcome == ActionOutcome.FAILURE:
                themes.append('sympathy')
        
        # Default themes
        if not themes:
            themes = ['wisdom', 'helpfulness']
        
        return themes
    
    def _extract_target_from_result(self, action_result: ActionResult) -> str:
        """Extract target from action result"""
        details = action_result.details
        execution_result = details.get('execution_result', {})
        return execution_result.get('target', 'something')
    
    def _build_command_context(self, action_result: ActionResult, game_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for command templates"""
        return {
            'observation_details': 'The details become clear to you.',
            'acquisition_details': 'It feels solid in your hands.',
            'movement_description': 'The path opens before you.',
            'combat_result': 'Your blow lands true.',
            'usage_effect': 'It responds to your touch.',
            'failure_description': 'misses its mark',
            'obstacle_description': 'The way is blocked.',
            'limitation_reason': 'The circumstances aren\'t right.',
            **game_context
        }
    
    def _determine_scene_change_type(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> str:
        """Determine the type of scene change"""
        if decision_result.action_result:
            details = decision_result.action_result.details
            if 'go' in str(details).lower() or 'movement' in str(details).lower():
                return 'location_entered'
        
        return 'location_entered'  # Default
    
    def _get_atmosphere_description(self, game_context: Dict[str, Any]) -> str:
        """Get atmosphere description from context"""
        location_context = game_context.get('location_context', {})
        aura = location_context.get('dominant_aura', 'neutral')
        return f"The atmosphere feels {aura}."
    
    def _get_notable_features(self, game_context: Dict[str, Any]) -> str:
        """Get notable features from context"""
        features = game_context.get('notable_features', [])
        if features:
            return f"You notice {', '.join(features)}."
        return ""
    
    def _get_temporal_changes(self, game_context: Dict[str, Any]) -> str:
        """Get temporal changes description"""
        return "the world continues its rhythm around you"
    
    def _get_weather_description(self, game_context: Dict[str, Any]) -> str:
        """Get weather description"""
        season = game_context.get('current_season', 'spring')
        weather_descriptions = {
            'spring': 'A gentle breeze carries the scent of new growth.',
            'summer': 'The warm air shimmers with heat.',
            'autumn': 'Crisp air carries the scent of changing leaves.',
            'winter': 'Cold air bites at exposed skin.'
        }
        return weather_descriptions.get(season, 'The weather is unremarkable.')
    
    def _get_new_atmosphere(self, game_context: Dict[str, Any]) -> str:
        """Get new atmosphere description"""
        return "A subtle shift in mood settles over the area."
    
    def _determine_skill_type(self, action_result: ActionResult, game_context: Dict[str, Any]) -> str:
        """Determine skill type from action result"""
        action = action_result.details.get('action', 'effort')
        skill_types = {
            'investigate': 'investigation',
            'climb': 'athletics',
            'sneak': 'stealth',
            'persuade': 'persuasion',
            'intimidate': 'intimidation'
        }
        return skill_types.get(action, 'skill')
    
    def _get_consequence_description(self, action_result: ActionResult, game_context: Dict[str, Any]) -> str:
        """Get consequence description for failures"""
        return "You'll need to try a different approach."
    
    def _get_progress_description(self, action_result: ActionResult, game_context: Dict[str, Any]) -> str:
        """Get progress description for successes"""
        return "Each step brings you closer to your goal."
    
    def _get_setback_description(self, action_result: ActionResult, game_context: Dict[str, Any]) -> str:
        """Get setback description"""
        return "This complication will require careful consideration."
    
    def _create_event_summary(self, decision_result: DecisionResult, game_context: Dict[str, Any]) -> str:
        """Create summary of the event for creative narration"""
        if decision_result.action_result:
            action_type = decision_result.action_result.action_type
            outcome = decision_result.action_result.outcome.value
            
            if action_type == 'opportunity_initiation':
                return f"Player initiated a narrative opportunity with {outcome}"
            elif action_type == 'branch_action':
                action = decision_result.action_result.details.get('action', 'unknown action')
                return f"Player attempted {action} with {outcome}"
            elif action_type == 'parsed_command':
                command = decision_result.action_result.details.get('command', 'unknown command')
                return f"Player executed {command} command with {outcome}"
        
        return "Player engaged in conversation or general interaction"
    
    def _get_world_state_summary(self, game_context: Dict[str, Any]) -> str:
        """Get summary of world state for narration"""
        world_state = game_context.get('world_state', {})
        economic = world_state.get('economic_status', 'stable')
        political = world_state.get('political_stability', 'stable')
        
        if economic != 'stable' or political != 'stable':
            return f"economically {economic}, politically {political}"
        else:
            return "peaceful and stable"
    
    def _determine_narrative_tone(self, decision_result: DecisionResult, complexity: ResponseComplexity) -> str:
        """Determine appropriate narrative tone"""
        if decision_result.action_result:
            if decision_result.action_result.outcome == ActionOutcome.SUCCESS:
                if complexity == ResponseComplexity.CRITICAL:
                    return "triumphant"
                else:
                    return "victorious"
            elif decision_result.action_result.outcome == ActionOutcome.FAILURE:
                return "tense"
        
        return "mysterious"
    
    async def _log_response_generation(self,
                                     response_data: Dict[str, Any],
                                     decision_result: DecisionResult,
                                     interaction_context: Dict[str, Any]):
        """Log response generation to database"""
        if self.db_service:
            await self.db_service.save_event({
                'session_id': interaction_context.get('session_id'),
                'event_type': 'RESPONSE_GENERATED',
                'actor': interaction_context.get('player_id'),
                'context': {
                    'response_mode': response_data['generation_metadata']['mode_used'],
                    'complexity': response_data['generation_metadata']['complexity'],
                    'response_source': response_data.get('response_source'),
                    'generation_time': response_data['generation_metadata']['generation_time'],
                    'decision_priority': decision_result.priority_used.name
                }
            })
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get response generation statistics"""
        return {
            'total_responses': self.generation_stats['total_responses'],
            'mode_usage': {
                mode.name: count 
                for mode, count in self.generation_stats['mode_usage'].items()
            },
            'complexity_distribution': {
                complexity.value: count 
                for complexity, count in self.generation_stats['complexity_distribution'].items()
            },
            'llm_creative_calls': self.generation_stats['llm_creative_calls'],
            'template_usage': self.generation_stats['template_usage'],
            'dialogue_generations': self.generation_stats['dialogue_generations'],
            'creative_llm_ratio': (
                self.generation_stats['llm_creative_calls'] / 
                max(1, self.generation_stats['total_responses'])
            )
        }