"""
Integration layer for mechanical outcomes into GM response flow
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from decision_logic.decision_tree import ActionResult, DecisionResult, ActionOutcome
from template_processor_enhanced import TemplateProcessor


class MechanicalOutcomesIntegrator:
    """
    Integrates mechanical action outcomes into the GM's narrative response flow
    """
    
    def __init__(self, template_processor: TemplateProcessor):
        """
        Initialize the mechanical outcomes integrator.
        
        Args:
            template_processor: Template processor for generating responses
        """
        self.template_processor = template_processor
        self.logger = logging.getLogger("MechanicalOutcomesIntegrator")
        
        # Outcome templates for different scenarios
        self.outcome_templates = {
            'opportunity_success': {
                'immediate': "{base_response}\n\n{success_details}",
                'with_consequence': "{base_response}\n\n{success_details} {consequence_narrative}",
                'world_reaction': "{base_response}\n\n{success_details} {world_reaction}"
            },
            'opportunity_failure': {
                'blocked_by_guards': "{base_response}, but a sudden patrol of guards makes you reconsider approaching it right now.",
                'wrong_timing': "{base_response}, but the timing doesn't feel right for such an undertaking.",
                'insufficient_resources': "{base_response}, but you realize you lack what's needed to pursue that path effectively.",
                'world_state_conflict': "{base_response}, but current events make that course of action inadvisable.",
                'character_state_conflict': "{base_response}, but your current condition prevents you from taking such action."
            },
            'branch_action_success': {
                'skill_triumph': "You successfully {action}! {skill_description} Your expertise serves you well.",
                'partial_success': "You manage to {action}, though not without some difficulty. {partial_outcome}",
                'unexpected_benefit': "You {action} with remarkable success! {unexpected_benefit}"
            },
            'branch_action_failure': {
                'skill_shortfall': "You attempt to {action}, but {skill_failure_reason}. Perhaps with more preparation...",
                'external_interference': "You try to {action}, but {interference_reason} disrupts your efforts.",
                'environmental_challenge': "You work to {action}, but {environmental_factor} proves more challenging than expected."
            },
            'command_outcomes': {
                'look_success': "You carefully observe {target}. {observation_details}",
                'take_success': "You pick up {target}. {item_acquired_effect}",
                'go_success': "You move {direction}. {location_transition}",
                'attack_success': "You strike at {target}! {combat_outcome}",
                'use_success': "You use {target}. {usage_effect}",
                'talk_success': "You engage {target} in conversation. {dialogue_initiation}"
            }
        }
    
    def integrate_mechanical_outcome(self, 
                                   decision_result: DecisionResult, 
                                   context: Dict[str, Any]) -> str:
        """
        Integrate mechanical outcomes into the GM response.
        
        Args:
            decision_result: Result from the decision tree
            context: Current game context
            
        Returns:
            Enhanced GM response with mechanical outcomes integrated
        """
        if not decision_result.action_result:
            return self._enhance_non_mechanical_response(decision_result, context)
        
        action_result = decision_result.action_result
        
        if action_result.action_type == 'opportunity_initiation':
            return self._integrate_opportunity_outcome(decision_result, context)
        elif action_result.action_type == 'branch_action':
            return self._integrate_branch_action_outcome(decision_result, context)
        elif action_result.action_type == 'parsed_command':
            return self._integrate_command_outcome(decision_result, context)
        else:
            return self._enhance_general_response(decision_result, context)
    
    def _integrate_opportunity_outcome(self, 
                                     decision_result: DecisionResult, 
                                     context: Dict[str, Any]) -> str:
        """Integrate opportunity initiation outcomes"""
        action_result = decision_result.action_result
        base_response = decision_result.gm_response_base
        
        if action_result.outcome == ActionOutcome.SUCCESS:
            return self._build_opportunity_success_response(
                base_response, action_result, context
            )
        elif action_result.outcome == ActionOutcome.FAILURE:
            return self._build_opportunity_failure_response(
                base_response, action_result, context
            )
        else:
            return self._enhance_with_narrative_elements(
                base_response, decision_result.narrative_enhancements
            )
    
    def _build_opportunity_success_response(self, 
                                          base_response: str, 
                                          action_result: ActionResult, 
                                          context: Dict[str, Any]) -> str:
        """Build response for successful opportunity initiation"""
        success_details = action_result.details.get('message', 'The path opens before you.')
        
        # Determine response template based on context
        if self._has_immediate_consequences(action_result, context):
            template_key = 'with_consequence'
            consequence_narrative = self._generate_consequence_narrative(action_result, context)
        elif self._has_world_reaction(action_result, context):
            template_key = 'world_reaction'
            world_reaction = self._generate_world_reaction(action_result, context)
        else:
            template_key = 'immediate'
        
        template = self.outcome_templates['opportunity_success'][template_key]
        
        template_context = {
            'base_response': base_response,
            'success_details': success_details,
            'consequence_narrative': consequence_narrative if template_key == 'with_consequence' else '',
            'world_reaction': world_reaction if template_key == 'world_reaction' else ''
        }
        
        return self.template_processor.process(template, template_context)
    
    def _build_opportunity_failure_response(self, 
                                          base_response: str, 
                                          action_result: ActionResult, 
                                          context: Dict[str, Any]) -> str:
        """Build response for failed opportunity initiation"""
        failure_reason = action_result.error_message or action_result.details.get('failure_reason', '')
        
        # Determine specific failure template
        template_key = self._determine_failure_template_key(failure_reason, context)
        template = self.outcome_templates['opportunity_failure'][template_key]
        
        return template.format(base_response=base_response)
    
    def _integrate_branch_action_outcome(self, 
                                       decision_result: DecisionResult, 
                                       context: Dict[str, Any]) -> str:
        """Integrate branch action outcomes"""
        action_result = decision_result.action_result
        action = action_result.details.get('action', 'take action')
        
        if action_result.outcome == ActionOutcome.SUCCESS:
            return self._build_branch_action_success_response(action_result, context, action)
        elif action_result.outcome == ActionOutcome.FAILURE:
            return self._build_branch_action_failure_response(action_result, context, action)
        else:
            return decision_result.gm_response_base
    
    def _build_branch_action_success_response(self, 
                                            action_result: ActionResult, 
                                            context: Dict[str, Any], 
                                            action: str) -> str:
        """Build response for successful branch action"""
        skill_check = action_result.details.get('skill_check', {})
        
        # Determine success type
        if skill_check.get('roll', 10) >= 18:  # Critical success
            template_key = 'unexpected_benefit'
            template_context = {
                'action': action,
                'unexpected_benefit': self._generate_unexpected_benefit(action_result, context)
            }
        elif skill_check.get('roll', 10) >= 15:  # Strong success
            template_key = 'skill_triumph'
            template_context = {
                'action': action,
                'skill_description': self._generate_skill_description(skill_check)
            }
        else:  # Marginal success
            template_key = 'partial_success'
            template_context = {
                'action': action,
                'partial_outcome': self._generate_partial_outcome(action_result, context)
            }
        
        template = self.outcome_templates['branch_action_success'][template_key]
        return self.template_processor.process(template, template_context)
    
    def _build_branch_action_failure_response(self, 
                                            action_result: ActionResult, 
                                            context: Dict[str, Any], 
                                            action: str) -> str:
        """Build response for failed branch action"""
        skill_check = action_result.details.get('skill_check', {})
        failure_reason = skill_check.get('failure_reason', 'the task proves too difficult')
        
        # Determine failure type
        if self._is_external_interference(context):
            template_key = 'external_interference'
            template_context = {
                'action': action,
                'interference_reason': self._get_interference_reason(context)
            }
        elif self._is_environmental_challenge(context):
            template_key = 'environmental_challenge'
            template_context = {
                'action': action,
                'environmental_factor': self._get_environmental_factor(context)
            }
        else:
            template_key = 'skill_shortfall'
            template_context = {
                'action': action,
                'skill_failure_reason': failure_reason
            }
        
        template = self.outcome_templates['branch_action_failure'][template_key]
        return self.template_processor.process(template, template_context)
    
    def _integrate_command_outcome(self, 
                                 decision_result: DecisionResult, 
                                 context: Dict[str, Any]) -> str:
        """Integrate parsed command outcomes"""
        action_result = decision_result.action_result
        execution_result = action_result.details.get('execution_result', {})
        
        # Use the existing command response as base, enhance with context
        base_response = execution_result.get('description', decision_result.gm_response_base)
        
        # Add environmental and contextual details
        enhanced_response = self._enhance_command_response(base_response, action_result, context)
        
        return enhanced_response
    
    def _enhance_command_response(self, 
                                base_response: str, 
                                action_result: ActionResult, 
                                context: Dict[str, Any]) -> str:
        """Enhance command response with contextual details"""
        # Add atmospheric details
        atmospheric_elements = self._get_atmospheric_elements(context)
        
        # Add world state reactions
        world_state_effects = self._get_world_state_effects(context)
        
        # Combine elements
        enhancements = []
        if atmospheric_elements:
            enhancements.append(atmospheric_elements)
        if world_state_effects:
            enhancements.append(world_state_effects)
        
        if enhancements:
            return f"{base_response} {' '.join(enhancements)}"
        else:
            return base_response
    
    def _enhance_non_mechanical_response(self, 
                                       decision_result: DecisionResult, 
                                       context: Dict[str, Any]) -> str:
        """Enhance responses that don't involve mechanical outcomes"""
        base_response = decision_result.gm_response_base
        enhancements = decision_result.narrative_enhancements
        
        return self._enhance_with_narrative_elements(base_response, enhancements)
    
    def _enhance_general_response(self, 
                                decision_result: DecisionResult, 
                                context: Dict[str, Any]) -> str:
        """Enhance general responses"""
        return self._enhance_non_mechanical_response(decision_result, context)
    
    def _enhance_with_narrative_elements(self, 
                                       base_response: str, 
                                       enhancements: List[str]) -> str:
        """Enhance response with narrative elements"""
        if not enhancements:
            return base_response
        
        # Select appropriate enhancements based on response length and context
        if len(base_response) < 100:  # Short response, add one enhancement
            selected_enhancements = enhancements[:1]
        else:  # Longer response, can handle more enhancements
            selected_enhancements = enhancements[:2]
        
        if selected_enhancements:
            return f"{base_response} {' '.join(selected_enhancements)}"
        else:
            return base_response
    
    # Helper Methods for Context Analysis
    
    def _has_immediate_consequences(self, action_result: ActionResult, context: Dict[str, Any]) -> bool:
        """Check if action has immediate consequences"""
        return (action_result.narrative_context and 
                action_result.narrative_context.get('immediate_consequence', False))
    
    def _has_world_reaction(self, action_result: ActionResult, context: Dict[str, Any]) -> bool:
        """Check if action triggers world reaction"""
        world_state = context.get('world_state', {})
        return (world_state.get('political_stability') in ['unrest', 'rebellion'] or
                len(world_state.get('active_global_threats', [])) > 0)
    
    def _determine_failure_template_key(self, failure_reason: str, context: Dict[str, Any]) -> str:
        """Determine which failure template to use"""
        if 'guard' in failure_reason.lower() or 'patrol' in failure_reason.lower():
            return 'blocked_by_guards'
        elif 'timing' in failure_reason.lower() or 'time' in failure_reason.lower():
            return 'wrong_timing'
        elif 'resource' in failure_reason.lower() or 'equipment' in failure_reason.lower():
            return 'insufficient_resources'
        elif 'world' in failure_reason.lower() or 'event' in failure_reason.lower():
            return 'world_state_conflict'
        else:
            return 'character_state_conflict'
    
    def _is_external_interference(self, context: Dict[str, Any]) -> bool:
        """Check if failure is due to external interference"""
        world_state = context.get('world_state', {})
        return world_state.get('political_stability') in ['unrest', 'rebellion']
    
    def _is_environmental_challenge(self, context: Dict[str, Any]) -> bool:
        """Check if failure is due to environmental challenges"""
        world_state = context.get('world_state', {})
        season = world_state.get('current_season', 'spring')
        return season in ['winter', 'storm_season']
    
    # Generator Methods for Dynamic Content
    
    def _generate_consequence_narrative(self, action_result: ActionResult, context: Dict[str, Any]) -> str:
        """Generate consequence narrative"""
        consequences = [
            "This choice will have lasting effects on your journey.",
            "You sense that this decision opens new paths while closing others.",
            "The ramifications of your choice ripple through the world around you."
        ]
        import random
        return random.choice(consequences)
    
    def _generate_world_reaction(self, action_result: ActionResult, context: Dict[str, Any]) -> str:
        """Generate world reaction narrative"""
        reactions = [
            "The world seems to shift subtly in response to your decision.",
            "You notice changes in the atmosphere around you as word of your choice spreads.",
            "Other forces in the world take note of your actions."
        ]
        import random
        return random.choice(reactions)
    
    def _generate_unexpected_benefit(self, action_result: ActionResult, context: Dict[str, Any]) -> str:
        """Generate unexpected benefit narrative"""
        benefits = [
            "Your exceptional performance catches the attention of influential observers.",
            "The quality of your work opens up possibilities you hadn't anticipated.",
            "Your mastery of the task reveals hidden opportunities."
        ]
        import random
        return random.choice(benefits)
    
    def _generate_skill_description(self, skill_check: Dict[str, Any]) -> str:
        """Generate skill description based on check result"""
        roll = skill_check.get('roll', 10)
        if roll >= 18:
            return "Your technique is flawless, executed with masterful precision."
        elif roll >= 15:
            return "You demonstrate considerable skill and competence."
        else:
            return "Your effort is solid and workmanlike."
    
    def _generate_partial_outcome(self, action_result: ActionResult, context: Dict[str, Any]) -> str:
        """Generate partial outcome narrative"""
        outcomes = [
            "Progress is made, though not without some complications.",
            "You achieve your goal, but with unexpected side effects.",
            "Success comes at a small cost that may matter later."
        ]
        import random
        return random.choice(outcomes)
    
    def _get_interference_reason(self, context: Dict[str, Any]) -> str:
        """Get interference reason based on context"""
        world_state = context.get('world_state', {})
        if world_state.get('political_stability') == 'unrest':
            return "civil unrest in the area"
        elif world_state.get('political_stability') == 'rebellion':
            return "active conflict nearby"
        else:
            return "unexpected complications"
    
    def _get_environmental_factor(self, context: Dict[str, Any]) -> str:
        """Get environmental factor based on context"""
        world_state = context.get('world_state', {})
        season = world_state.get('current_season', 'spring')
        
        environmental_factors = {
            'winter': 'the harsh winter conditions',
            'summer': 'the oppressive heat',
            'spring': 'the unpredictable spring weather',
            'autumn': 'the changing season',
            'storm_season': 'the violent storms'
        }
        
        return environmental_factors.get(season, 'the challenging environment')
    
    def _get_atmospheric_elements(self, context: Dict[str, Any]) -> str:
        """Get atmospheric elements for enhancement"""
        location_context = context.get('location_context', {})
        if location_context and location_context.get('emotional_aura'):
            dominant_aura = location_context.get('dominant_aura', 'neutral')
            return f"The {dominant_aura} atmosphere of the place adds weight to your actions."
        return ""
    
    def _get_world_state_effects(self, context: Dict[str, Any]) -> str:
        """Get world state effects for enhancement"""
        world_state = context.get('world_state', {})
        
        if world_state.get('active_global_threats'):
            return "The current troubles in the world cast a shadow over even simple actions."
        elif world_state.get('political_stability') == 'unrest':
            return "The tension in the air makes everyone more cautious."
        
        return ""