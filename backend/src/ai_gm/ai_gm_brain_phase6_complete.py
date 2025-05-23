"""
AI GM Brain - Phase 6 Complete with Pacing Integration

This module extends the AI GM Brain with the pacing and ambient storytelling features, 
fully integrating all components including world reaction, domain system, and combat.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
import json

# Import core AI GM components
from .ai_gm_brain import AIGMBrain
from .ai_gm_delivery_system import DeliveryChannel, ResponsePriority

# Import decision logic and output generator
from .ai_gm_decision_logic import AIGMDecisionLogic, DecisionResult, DecisionPriority
from .ai_gm_output_generator import AIGMOutputGenerator

# Import configuration
from .ai_gm_config import IntegratedAIGMConfig

# Import world reaction components from phase 5
from .world_reaction.reputation_manager import ReputationManager
from .world_reaction.reaction_assessor import ReactionAssessor
from .world_reaction.enhanced_context_manager import EnhancedContextManager

# Import pacing components from phase 6
from .pacing.pacing_manager import PacingManager
from .pacing.idle_npc_manager import IdleNPCManager
from .pacing.event_summarizer import EventSummarizer
from .pacing.pacing_integration import PacingIntegration
from .ai_gm_pacing_integration import AIGMPacingIntegration

# Import domain and combat integration
from .ai_gm_combat_integration import AIGMCombatIntegration


class AIGMBrainPhase6Complete(AIGMBrain):
    """
    Phase 6 Complete AI GM Brain with Pacing and Ambient Storytelling

    This class extends the base AI GM Brain with:
    - Pacing management and ambient storytelling
    - Idle NPC behavior for more natural interactions
    - Event summarization for optimized context
    - Full integration with domain and combat systems
    - Enhanced world reactivity
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Phase 6 Complete AI GM Brain.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.logger = logging.getLogger("AIGMBrainPhase6")
        
        self.logger.info("Initializing AI GM Brain Phase 6 Complete")
        
        # Load configuration from AI GM Config if no custom config provided
        if not config:
            self.config = IntegratedAIGMConfig.get_config()
        else:
            self.config = config
        
        # Initialize Phase 5 world reaction components if not already present
        if not hasattr(self, 'enhanced_context_manager'):
            self.enhanced_context_manager = EnhancedContextManager(
                llm_manager=self.llm_manager,
                db_service=self.db_service
            )
            
        if not hasattr(self, 'reputation_manager'):
            self.reputation_manager = ReputationManager(
                db_service=self.db_service
            )
            
        if not hasattr(self, 'reaction_assessor'):
            self.reaction_assessor = ReactionAssessor(
                llm_manager=self.llm_manager,
                db_service=self.db_service
            )
        
        # Initialize Phase 6 pacing integration
        self.ai_gm_pacing = AIGMPacingIntegration(self)
        
        # Initialize combat integration if not already present
        if not hasattr(self, 'combat_integration'):
            self.combat_integration = AIGMCombatIntegration()
            
        # Initialize decision logic system
        self.decision_logic = AIGMDecisionLogic(IntegratedAIGMConfig)
        
        # Initialize output generator
        self.output_generator = AIGMOutputGenerator(
            config=IntegratedAIGMConfig,
            template_processor=getattr(self, 'template_processor', None)
        )
        
        # Track last activity time for pacing
        self.last_input_time = datetime.utcnow()
        
        self.logger.info("AI GM Brain Phase 6 Complete initialized")
    
    async def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input and generate a response.
        
        Args:
            input_text: Player's input text
            
        Returns:
            Response data including text and metadata
        """
        try:
            # Update pacing tracking for this input
            await self.ai_gm_pacing.process_player_input(input_text, self)
            
            # Track input time
            self.last_input_time = datetime.utcnow()
            
            # Get current context
            context = self._get_current_context()
            
            # Enhance context with pacing and world reaction data
            enhanced_context = await self._enhance_context_with_pacing(context)
            
            # Phase 1: Try to parse command using text parser if available
            parsed_command = None
            if hasattr(self, 'parser_engine') and self.parser_engine:
                try:
                    parsed_command = await self.parser_engine.parse_input(input_text, enhanced_context)
                except Exception as parser_error:
                    self.logger.warning(f"Parser error: {parser_error}")
            
            # Phase 2: Process with LLM for intent analysis and disambiguation if needed
            llm_output = None
            if hasattr(self, 'llm_manager') and self.llm_manager:
                try:
                    # Determine if LLM processing is needed (parser failed or input seems conversational)
                    needs_llm_processing = (
                        parsed_command is None or 
                        not parsed_command.get('success', False) or
                        self._is_input_conversational(input_text)
                    )
                    
                    if needs_llm_processing:
                        llm_output = await self._process_with_llm(input_text, parsed_command, enhanced_context)
                except Exception as llm_error:
                    self.logger.warning(f"LLM processing error: {llm_error}")
            
            # Phase 3: Decision Logic - Determine appropriate action based on parsing and LLM
            decision_result = await self.decision_logic.evaluate_decision_tree(
                player_input=input_text,
                parsed_command=parsed_command,
                llm_output=llm_output,
                game_context=enhanced_context
            )
            
            # Phase 4: Execute decision and generate appropriate response
            response = await self.output_generator.generate_response(
                decision_result=decision_result,
                player_input=input_text,
                context=enhanced_context
            )
            
            # Update pacing with AI response
            await self.ai_gm_pacing.process_ai_response(input_text, response, enhanced_context)
            
            # Record significant action if appropriate
            if decision_result.action_type in ['INITIATE_NARRATIVE_BRANCH', 'EXECUTE_BRANCH_ACTION']:
                await self.record_significant_action(
                    action_type=f"PLAYER_{decision_result.action_type}",
                    description=response['response_text'],
                    context=decision_result.action_data
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing player input: {e}")
            return {
                'response_text': f"I encountered a problem processing your input. Please try again.",
                'metadata': {'error': str(e), 'input_text': input_text}
            }
            
    def _is_input_conversational(self, input_text: str) -> bool:
        """
        Check if input appears to be conversational rather than a command.
        
        Args:
            input_text: Player's input text
            
        Returns:
            True if input seems conversational
        """
        # Get conversational keywords from config
        conversational_keywords = self.config.get('conversational_keywords', {})
        
        # Check if input contains conversational patterns
        input_lower = input_text.lower()
        
        # Check for question words
        for word in conversational_keywords.get('question_words', []):
            if input_lower.startswith(word + ' ') or f" {word} " in input_lower:
                return True
                
        # Check for conversational starters
        for phrase in conversational_keywords.get('conversational_starters', []):
            if phrase in input_lower:
                return True
                
        # Check for social actions
        for action in conversational_keywords.get('social_actions', []):
            if action in input_lower:
                return True
        
        # Check if input is long (likely conversational)
        if len(input_text.split()) > 6:
            return True
            
        return False
        
    async def _process_with_llm(self, 
                             input_text: str, 
                             parsed_command: Dict[str, Any] = None, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process input with LLM for intent analysis.
        
        Args:
            input_text: Player's input text
            parsed_command: Parser output if available
            context: Current game context
            
        Returns:
            LLM processing result
        """
        if not hasattr(self, 'llm_manager') or not self.llm_manager:
            return None
            
        # Prepare context for LLM
        llm_context = {
            'input_text': input_text,
            'parsed_command': parsed_command,
            'game_context': context,
        }
        
        # Use LLM manager to interpret input
        try:
            return await self.llm_manager.process_conversational_input(llm_context)
        except Exception as e:
            self.logger.error(f"Error in LLM processing: {e}")
            return None
    
    async def _enhance_context_with_pacing(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance context with pacing information.
        
        Args:
            base_context: Base context to enhance
            
        Returns:
            Enhanced context with pacing information
        """
        # Get enhanced context from world reaction
        enhanced_context = await self.enhanced_context_manager.enhance_context(base_context)
        
        # Further enhance with pacing data
        pacing_enhanced = await self.ai_gm_pacing.enhance_context(enhanced_context)
        
        return pacing_enhanced
    
    async def _check_and_inject_ambient_content(self) -> Optional[Dict[str, Any]]:
        """
        Check if ambient content should be injected and generate it if needed.
        
        Returns:
            Ambient content response or None
        """
        context = self._get_current_context()
        
        # Check if in combat
        if context.get('in_combat', False):
            return None  # Don't inject ambient during combat
        
        # Check for ambient content through pacing integration
        return await self.ai_gm_pacing.check_for_ambient_content(context)
    
    async def _check_for_npc_initiative(self) -> Optional[Dict[str, Any]]:
        """
        Check if an NPC should initiate interaction and generate it if needed.
        
        Returns:
            NPC initiative response or None
        """
        context = self._get_current_context()
        
        # Check if in combat
        if context.get('in_combat', False):
            return None  # Don't have NPCs chat during combat
        
        # Check for NPC initiative through pacing integration
        return await self.ai_gm_pacing.check_for_npc_initiative(context)
    
    async def _check_for_event_summary(self) -> Optional[str]:
        """
        Check if a new event summary should be created.
        
        Returns:
            New summary or None
        """
        session_id = self.session_id if hasattr(self, 'session_id') else "default_session"
        
        # Check for event summary through pacing integration
        return await self.ai_gm_pacing.check_for_event_summary(session_id)
    
    async def _process_ambient_updates(self) -> Optional[Dict[str, Any]]:
        """
        Process ambient updates including NPC initiatives and ambient storytelling.
        
        Returns:
            Ambient update response or None
        """
        # First check for NPC initiative (higher priority)
        npc_initiative = await self._check_for_npc_initiative()
        if npc_initiative:
            # Deliver NPC initiative via appropriate channel
            await self.deliver_response(
                npc_initiative['response_text'],
                channels=[DeliveryChannel.NARRATIVE],
                priority=ResponsePriority.AMBIENT
            )
            return npc_initiative
        
        # Then check for ambient content
        ambient_content = await self._check_and_inject_ambient_content()
        if ambient_content:
            # Deliver ambient content via appropriate channel
            await self.deliver_response(
                ambient_content['response_text'],
                channels=[DeliveryChannel.AMBIENT],
                priority=ResponsePriority.AMBIENT
            )
            return ambient_content
        
        # No ambient updates needed
        return None
    
    async def _check_context_optimizations(self) -> bool:
        """
        Check for context optimizations like event summarization.
        
        Returns:
            True if optimizations were performed
        """
        # Check for event summarization
        summary = await self._check_for_event_summary()
        
        if summary:
            self.logger.info(f"Created new event summary: {summary[:50]}...")
            return True
            
        return False
    
    def _get_current_context(self) -> Dict[str, Any]:
        """
        Get current context for AI GM.
        
        Returns:
            Current context
        """
        # Get base context from memory or create empty
        if hasattr(self, 'context_manager') and self.context_manager:
            context = self.context_manager.get_current_context()
        else:
            context = {}
            
        # Add time since last input
        if hasattr(self, 'last_input_time'):
            time_since_input = datetime.utcnow() - self.last_input_time
            context['time_since_last_input'] = time_since_input
        
        return context
    
    async def deliver_response(self, 
                             response_text: str, 
                             channels: List[DeliveryChannel] = None, 
                             priority: ResponsePriority = ResponsePriority.NORMAL) -> None:
        """
        Deliver response through appropriate channels.
        
        Args:
            response_text: Response text to deliver
            channels: List of delivery channels
            priority: Response priority
        """
        if not hasattr(self, 'delivery_system') or not self.delivery_system:
            # Just print the response if no delivery system
            print(f"[{priority.name}] {response_text}")
            return
            
        # Use delivery system
        if not channels:
            channels = [DeliveryChannel.NARRATIVE]
            
        await self.delivery_system.deliver_response(
            response_text, 
            channels=channels,
            priority=priority
        )
    
    async def check_ambient_updates(self) -> bool:
        """
        Check and process ambient updates (to be called periodically).
        
        Returns:
            True if any ambient updates were processed
        """
        try:
            ambient_update = await self._process_ambient_updates()
            return ambient_update is not None
        except Exception as e:
            self.logger.error(f"Error checking ambient updates: {e}")
            return False
    
    async def check_context_optimizations(self) -> bool:
        """
        Check and process context optimizations (to be called periodically).
        
        Returns:
            True if any optimizations were performed
        """
        try:
            return await self._check_context_optimizations()
        except Exception as e:
            self.logger.error(f"Error checking context optimizations: {e}")
            return False
    
    def get_pacing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about pacing components.
        
        Returns:
            Pacing statistics
        """
        return self.ai_gm_pacing.get_pacing_statistics()
    
    def add_significant_event(self, event_data: Dict[str, Any]) -> None:
        """
        Add a significant event for summarization.
        
        Args:
            event_data: Event data to potentially summarize
        """
        self.ai_gm_pacing.add_significant_event(event_data)
    
    async def assess_world_reaction(self, 
                                  player_action: str, 
                                  target_entity: str, 
                                  action_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess world reaction to player action.
        
        Args:
            player_action: Description of player's action
            target_entity: Entity affected by the action
            action_context: Additional context about the action
            
        Returns:
            Reaction assessment result
        """
        # Get current context
        current_context = self._get_current_context()
        
        # Enhance context with pacing data
        enhanced_context = await self._enhance_context_with_pacing(current_context)
        
        # Get player reputation and recent actions
        reputation_data = self.reputation_manager.get_entity_reputation(
            target_entity, 
            enhanced_context.get('player_id', 'player')
        )
        
        # Add to context
        enhanced_context['player_reputation'] = reputation_data
        
        # Assess reaction
        reaction = await self.reaction_assessor.assess_reaction(
            player_action=player_action,
            target_entity=target_entity,
            action_context=action_context,
            enhanced_context=enhanced_context
        )
        
        # Record the significant action for summarization
        self.add_significant_event({
            'event_type': 'WORLD_REACTION_ASSESSED',
            'context': {
                'player_action': player_action,
                'target_entity': target_entity,
                'reaction': reaction.get('reaction_summary', ''),
                'reputation_change': reaction.get('reputation_change', 0)
            },
            'actor': enhanced_context.get('player_id', 'player')
        })
        
        return reaction
    
    async def record_significant_action(self, 
                                      action_type: str, 
                                      description: str,
                                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Record a significant player action for reputation tracking and summarization.
        
        Args:
            action_type: Type of action
            description: Description of the action
            context: Additional context about the action
            
        Returns:
            Result of recording the action
        """
        # Get current context
        current_context = self._get_current_context()
        player_id = current_context.get('player_id', 'player')
        
        # Record the action in reputation manager
        if action_type.startswith("REPUTATION_"):
            # Extract target entity from context
            target_entity = context.get('target_entity', 'world')
            
            # Update reputation
            reputation_change = context.get('reputation_change', 0)
            reason = context.get('reason', description)
            
            self.reputation_manager.update_reputation(
                entity_name=target_entity,
                entity_type=context.get('entity_type', 'npc'),
                actor_id=player_id,
                reputation_change=reputation_change,
                reason=reason
            )
        
        # Add to event summarizer for all significant actions
        self.add_significant_event({
            'event_type': 'SIGNIFICANT_ACTION_RECORDED',
            'context': {
                'action_type': action_type,
                'description': description,
                'additional_context': context
            },
            'actor': player_id
        })
        
        return {
            'action_recorded': True,
            'action_type': action_type,
            'player_id': player_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def is_session_stale(self) -> bool:
        """
        Check if the session is considered stale (inactive for too long).
        
        Returns:
            True if session is stale
        """
        return self.ai_gm_pacing.is_session_stale()
    
    async def integrate_with_combat_system(self, combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate current AI GM state with combat system.
        
        Args:
            combat_context: Current combat context
            
        Returns:
            Enhanced combat context
        """
        # First integrate via combat integration if available
        if hasattr(self, 'combat_integration') and self.combat_integration:
            enhanced_combat = await self.combat_integration.enhance_combat_context(combat_context)
        else:
            enhanced_combat = combat_context.copy()
        
        # Add pacing-based enhancements
        enhanced_combat = await self.ai_gm_pacing.integrate_with_combat_system(enhanced_combat)
        
        # Add world reaction context
        if hasattr(self, 'enhanced_context_manager') and self.enhanced_context_manager:
            # Get reputation data for combatants
            for combatant in enhanced_combat.get('combatants', []):
                if combatant.get('id') and combatant.get('type') == 'npc':
                    combatant_id = combatant.get('id')
                    reputation = self.reputation_manager.get_entity_reputation(
                        combatant_id,
                        enhanced_combat.get('player_id', 'player')
                    )
                    combatant['reputation'] = reputation
        
        return enhanced_combat
    
    async def integrate_with_domain_system(self, domain_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate current AI GM state with domain system.
        
        Args:
            domain_context: Current domain context
            
        Returns:
            Enhanced domain context
        """
        # Add pacing-based enhancements
        enhanced_domain = await self.ai_gm_pacing.integrate_with_domain_system(domain_context)
        
        # Add world reaction context
        if hasattr(self, 'enhanced_context_manager') and self.enhanced_context_manager:
            # Get reputation data and emotions for domain entities
            for entity in enhanced_domain.get('entities', []):
                if entity.get('id'):
                    entity_id = entity.get('id')
                    reputation = self.reputation_manager.get_entity_reputation(
                        entity_id,
                        enhanced_domain.get('player_id', 'player')
                    )
                    entity['reputation'] = reputation
        
        return enhanced_domain
    
    def get_phase6_comprehensive_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics from all Phase 6 components.
        
        Returns:
            Combined statistics
        """
        stats = {
            'phase': 'Phase 6 Complete',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add world reaction stats from Phase 5
        if hasattr(self, 'enhanced_context_manager'):
            stats['enhanced_context'] = self.enhanced_context_manager.get_statistics()
            
        if hasattr(self, 'reputation_manager'):
            stats['reputation'] = self.reputation_manager.get_statistics()
            
        if hasattr(self, 'reaction_assessor'):
            stats['reaction_assessment'] = self.reaction_assessor.get_statistics()
            
        # Add pacing stats from Phase 6
        stats['pacing'] = self.get_pacing_statistics()
        
        # Add decision logic stats if available
        if hasattr(self, 'decision_logic'):
            stats['decision_logic'] = {
                'decision_count': getattr(self.decision_logic, 'decision_count', 0),
                'decision_types': getattr(self.decision_logic, 'decision_type_counts', {}),
                'success_rate': getattr(self.decision_logic, 'success_rate', 1.0)
            }
            
        # Add output generator stats if available
        if hasattr(self, 'output_generator'):
            stats['output_generator'] = {
                'response_count': getattr(self.output_generator, 'response_count', 0),
                'template_usage': getattr(self.output_generator, 'template_usage', {}),
                'response_types': getattr(self.output_generator, 'response_type_counts', {})
            }
            
        # Add parser stats if available
        if hasattr(self, 'parser_engine'):
            stats['parser'] = {
                'parse_count': getattr(self.parser_engine, 'parse_count', 0),
                'success_rate': getattr(self.parser_engine, 'success_rate', 0),
                'command_distribution': getattr(self.parser_engine, 'command_distribution', {})
            }
            
        # Add llm stats if available
        if hasattr(self, 'llm_manager'):
            stats['llm'] = {
                'request_count': getattr(self.llm_manager, 'request_count', 0),
                'average_response_time': getattr(self.llm_manager, 'average_response_time', 0),
                'token_usage': getattr(self.llm_manager, 'token_usage', {})
            }
            
        # Add combat integration stats if available
        if hasattr(self, 'combat_integration'):
            stats['combat'] = {
                'combat_count': getattr(self.combat_integration, 'combat_count', 0),
                'average_combat_rounds': getattr(self.combat_integration, 'average_rounds', 0),
                'combat_outcomes': getattr(self.combat_integration, 'combat_outcomes', {})
            }
        
        # Add session info
        stats['session_info'] = {
            'stale': self.is_session_stale(),
            'time_since_last_input': str(datetime.utcnow() - self.last_input_time)
        }
        
        return stats