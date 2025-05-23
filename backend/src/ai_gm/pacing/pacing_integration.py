"""
Pacing Integration for AI GM Brain - Connects pacing components to the core system
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from .pacing_manager import PacingManager, PacingState, AmbientTrigger
from .idle_npc_manager import IdleNPCManager
from .event_summarizer import EventSummarizer


class PacingIntegration:
    """
    Integrates pacing components with the AI GM brain.
    
    Responsible for:
    - Coordinating pacing manager, idle NPC manager, and event summarizer
    - Tracking timing for pacing-related events
    - Determining when to inject ambient content or NPC interactions
    - Maintaining event summaries for context optimization
    """
    
    def __init__(self, 
                 llm_manager=None, 
                 dialogue_generator=None, 
                 template_processor=None, 
                 db_service=None):
        """
        Initialize pacing integration.
        
        Args:
            llm_manager: LLM manager for API calls
            dialogue_generator: Dialogue generator for NPC interactions
            template_processor: Template processor for ambient narration
            db_service: Database service for logging
        """
        self.logger = logging.getLogger("PacingIntegration")
        
        # Initialize pacing components
        self.pacing_manager = PacingManager(
            template_processor=template_processor,
            db_service=db_service
        )
        
        self.idle_npc_manager = IdleNPCManager(
            dialogue_generator=dialogue_generator,
            db_service=db_service
        )
        
        self.event_summarizer = EventSummarizer(
            llm_manager=llm_manager,
            db_service=db_service
        )
        
        # Initialize timing tracking
        self.last_input_time = datetime.utcnow()
        
        # Pacing configuration
        self.pacing_config = {
            'ambient_check_interval': timedelta(minutes=2),  # Check for ambient content every 2 min
            'npc_initiative_check_interval': timedelta(minutes=1),  # Check for NPC initiative every 1 min
            'event_summary_check_interval': timedelta(hours=1),  # Check for summarization every hour
            'max_idle_time': timedelta(minutes=30)  # Consider session stale after 30 min idle
        }
        
        self.logger.info("Pacing integration initialized with all components")
    
    def on_player_input(self, input_text: str):
        """
        Update timing tracking on player input.
        
        Args:
            input_text: Player's input text
        """
        self.last_input_time = datetime.utcnow()
    
    def on_ai_response(self, 
                     player_input: str, 
                     ai_response: Dict[str, Any], 
                     context: Dict[str, Any]):
        """
        Process AI GM response for pacing components.
        
        Args:
            player_input: Player's input
            ai_response: AI GM response
            context: Current game context
        """
        # Update pacing manager with this interaction
        self.pacing_manager.update_player_activity(player_input, ai_response, context)
        
        # Add event for potential summarization
        event_data = {
            'event_type': ai_response.get('metadata', {}).get('event_type', 'PLAYER_INTERACTION'),
            'context': ai_response.get('metadata', {}),
            'actor': context.get('player_id', 'player')
        }
        self.event_summarizer.add_event_for_summarization(event_data)
    
    def get_time_since_last_input(self) -> timedelta:
        """
        Get time elapsed since last player input.
        
        Returns:
            Time since last input
        """
        return datetime.utcnow() - self.last_input_time
    
    def is_session_stale(self) -> bool:
        """
        Check if session is considered stale (inactive for too long).
        
        Returns:
            True if session is stale
        """
        return self.get_time_since_last_input() > self.pacing_config['max_idle_time']
    
    async def check_and_inject_ambient_content(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if ambient content should be injected and generate it if needed.
        
        Args:
            context: Current game context
            
        Returns:
            Ambient content response or None
        """
        # Add time since last input to context
        time_since_last_input = self.get_time_since_last_input()
        enriched_context = context.copy()
        enriched_context['time_since_last_input'] = time_since_last_input
        
        # Check if we should inject ambient content
        should_inject, trigger_type = self.pacing_manager.should_inject_ambient_content(enriched_context)
        
        if should_inject and trigger_type:
            # Generate the ambient content
            ambient_content = self.pacing_manager.generate_ambient_content(trigger_type, enriched_context)
            
            if ambient_content:
                self.logger.info(f"Injecting ambient content ({trigger_type.value})")
                return {
                    'ambient_content': True,
                    'content_type': trigger_type.value,
                    'response_text': ambient_content,
                    'source': 'ambient_narrative'
                }
        
        return None
    
    async def check_for_npc_initiative(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if an NPC should initiate interaction and generate it if needed.
        
        Args:
            context: Current game context
            
        Returns:
            NPC initiative response or None
        """
        time_since_last_input = self.get_time_since_last_input()
        
        # Get NPCs in current location
        present_npcs = context.get('present_npcs', [])
        
        if not present_npcs:
            return None
        
        # Check each NPC for potential initiative
        for npc_id in present_npcs:
            should_initiate, dialogue_theme = self.idle_npc_manager.should_npc_initiate(
                npc_id, 
                context, 
                time_since_last_input
            )
            
            if should_initiate and dialogue_theme:
                # Generate NPC dialogue
                npc_dialogue = await self.idle_npc_manager.generate_npc_initiative(
                    npc_id,
                    dialogue_theme,
                    context
                )
                
                if npc_dialogue:
                    self.logger.info(f"NPC {npc_id} initiating dialogue with theme: {dialogue_theme}")
                    return npc_dialogue
        
        return None
    
    async def check_and_create_event_summary(self, session_id: str) -> Optional[str]:
        """
        Check if an event summary should be created and create it if needed.
        
        Args:
            session_id: Current session ID
            
        Returns:
            New summary or None
        """
        if self.event_summarizer.should_create_summary():
            summary = await self.event_summarizer.create_summary(session_id)
            if summary:
                self.logger.info(f"Created new event summary: {summary[:50]}...")
                return summary
        
        return None
    
    def get_story_context(self) -> Dict[str, Any]:
        """
        Get current story context from summarizer for LLM prompts.
        
        Returns:
            Story context
        """
        return self.event_summarizer.get_current_story_context()
    
    def get_enhanced_context(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance context with pacing information.
        
        Args:
            base_context: Base context to enhance
            
        Returns:
            Enhanced context
        """
        # Start with base context
        enhanced_context = base_context.copy()
        
        # Add time-related context
        enhanced_context['time_since_last_input'] = self.get_time_since_last_input()
        enhanced_context['current_pacing_state'] = self.pacing_manager.current_metrics.current_pacing_state.value
        
        # Add story summary context
        story_context = self.get_story_context()
        if story_context:
            enhanced_context['story_summary'] = story_context.get('story_summary', '')
            enhanced_context['recent_events'] = story_context.get('recent_events', [])
        
        return enhanced_context
    
    def get_pacing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all pacing components.
        
        Returns:
            Combined statistics
        """
        return {
            'pacing_manager': self.pacing_manager.get_pacing_statistics(),
            'idle_npc_manager': self.idle_npc_manager.get_idle_npc_statistics(),
            'event_summarizer': self.event_summarizer.get_summarization_statistics(),
            'integration': {
                'time_since_last_input': str(self.get_time_since_last_input()),
                'session_stale': self.is_session_stale()
            }
        }