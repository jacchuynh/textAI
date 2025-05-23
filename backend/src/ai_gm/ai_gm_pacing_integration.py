"""
AI GM Brain Pacing Integration - Connects pacing system with the main AI GM Brain.

This module integrates the pacing, ambient storytelling, idle NPC interactions and 
event summarization features with the core AI GM functionality.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

from .pacing import PacingIntegration
from .pacing import PacingState, AmbientTrigger


class AIGMPacingIntegration:
    """
    Integrates the Pacing system with the AI GM Brain.
    
    - Connects pacing components to AI GM Brain
    - Ensures compatibility with combat and domain systems
    - Manages timing and triggers for ambient storytelling
    - Coordinates idle NPC initiatives
    - Maintains summarized story context
    """
    
    def __init__(self, ai_gm_brain=None):
        """
        Initialize AI GM Pacing integration.
        
        Args:
            ai_gm_brain: Reference to the main AI GM Brain
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger("AIGMPacingIntegration")
        
        self.logger.info("Initializing AI GM Pacing Integration")
        
        # Initialize pacing integration with relevant components from AI GM Brain
        llm_manager = getattr(ai_gm_brain, 'llm_manager', None)
        dialogue_generator = getattr(ai_gm_brain, 'dialogue_generator', None)
        template_processor = getattr(ai_gm_brain, 'template_processor', None)
        db_service = getattr(ai_gm_brain, 'db_service', None)
        
        self.pacing_integration = PacingIntegration(
            llm_manager=llm_manager,
            dialogue_generator=dialogue_generator,
            template_processor=template_processor,
            db_service=db_service
        )
        
        # Setup event checking config
        self.pacing_check_config = {
            'ambient_check_interval': timedelta(minutes=2),  # Check for ambient content every 2 min
            'npc_initiative_check_interval': timedelta(minutes=1),  # Check for NPC initiative every 1 min
            'event_summary_check_interval': timedelta(hours=1),  # Check for summarization every hour
            'last_ambient_check': datetime.utcnow(),
            'last_npc_check': datetime.utcnow(),
            'last_summary_check': datetime.utcnow()
        }
        
        self.logger.info("AI GM Pacing Integration initialized")
    
    async def process_player_input(self, player_input: str, ai_gm_brain=None):
        """
        Process player input for pacing components.
        
        Args:
            player_input: Player's input text
            ai_gm_brain: Reference to the AI GM Brain (if not provided at init)
        """
        if ai_gm_brain:
            self.ai_gm_brain = ai_gm_brain
            
        # Update pacing tracking with player input
        self.pacing_integration.on_player_input(player_input)
    
    async def process_ai_response(self, 
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
        # Update pacing components with this interaction
        self.pacing_integration.on_ai_response(player_input, ai_response, context)
        
        # Reset check timers
        self.pacing_check_config['last_ambient_check'] = datetime.utcnow()
        self.pacing_check_config['last_npc_check'] = datetime.utcnow()
    
    async def enhance_context(self, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance base context with pacing information.
        
        Args:
            base_context: Base context to enhance
            
        Returns:
            Enhanced context
        """
        return self.pacing_integration.get_enhanced_context(base_context)
    
    async def check_for_ambient_content(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if ambient content should be generated.
        
        Args:
            context: Current game context
            
        Returns:
            Ambient content response or None
        """
        # Check if it's time to check for ambient content
        if (datetime.utcnow() - self.pacing_check_config['last_ambient_check'] < 
                self.pacing_check_config['ambient_check_interval']):
            return None
            
        # Update check time
        self.pacing_check_config['last_ambient_check'] = datetime.utcnow()
        
        # Check if in combat
        in_combat = context.get('in_combat', False)
        if in_combat:
            return None  # Don't inject ambient during combat
        
        # Check for ambient content
        ambient_content = await self.pacing_integration.check_and_inject_ambient_content(context)
        return ambient_content
    
    async def check_for_npc_initiative(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if an NPC should initiate interaction.
        
        Args:
            context: Current game context
            
        Returns:
            NPC initiative response or None
        """
        # Check if it's time to check for NPC initiative
        if (datetime.utcnow() - self.pacing_check_config['last_npc_check'] < 
                self.pacing_check_config['npc_initiative_check_interval']):
            return None
            
        # Update check time
        self.pacing_check_config['last_npc_check'] = datetime.utcnow()
        
        # Check if in combat
        in_combat = context.get('in_combat', False)
        if in_combat:
            return None  # Don't have NPCs chat during combat
        
        # Check for NPC initiative
        npc_initiative = await self.pacing_integration.check_for_npc_initiative(context)
        return npc_initiative
    
    async def check_for_event_summary(self, session_id: str) -> Optional[str]:
        """
        Check if an event summary should be created.
        
        Args:
            session_id: Current session ID
            
        Returns:
            New summary or None
        """
        # Check if it's time to check for event summarization
        if (datetime.utcnow() - self.pacing_check_config['last_summary_check'] < 
                self.pacing_check_config['event_summary_check_interval']):
            return None
            
        # Update check time
        self.pacing_check_config['last_summary_check'] = datetime.utcnow()
        
        # Check for event summary
        return await self.pacing_integration.check_and_create_event_summary(session_id)
    
    def is_session_stale(self) -> bool:
        """
        Check if the session is considered stale (inactive for too long).
        
        Returns:
            True if session is stale
        """
        return self.pacing_integration.is_session_stale()
    
    def get_time_since_last_input(self) -> timedelta:
        """
        Get time elapsed since last player input.
        
        Returns:
            Time since last input
        """
        return self.pacing_integration.get_time_since_last_input()
    
    def get_pacing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all pacing components.
        
        Returns:
            Combined statistics
        """
        return self.pacing_integration.get_pacing_statistics()
    
    def add_significant_event(self, event_data: Dict[str, Any]):
        """
        Add a significant event for summarization.
        
        Args:
            event_data: Event data to potentially summarize
        """
        self.pacing_integration.event_summarizer.add_event_for_summarization(event_data)
        
    async def integrate_with_domain_system(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate pacing information with domain system.
        
        Args:
            context: Current context with domain information
            
        Returns:
            Enhanced context with relevant pacing information
        """
        enhanced_context = context.copy()
        
        # Add pacing state to domain context
        pacing_state = self.pacing_integration.pacing_manager.current_metrics.current_pacing_state.value
        
        # Map pacing states to domain considerations
        if pacing_state == PacingState.ACTIVE.value:
            enhanced_context['domain_pacing_modifier'] = 'high_engagement'
        elif pacing_state == PacingState.STAGNANT.value:
            enhanced_context['domain_pacing_modifier'] = 'needs_acceleration'
        else:
            enhanced_context['domain_pacing_modifier'] = 'normal'
            
        # Add story context for domain consideration
        story_context = self.pacing_integration.get_story_context()
        if story_context.get('story_summary'):
            enhanced_context['story_context_summary'] = story_context.get('story_summary')
            
        return enhanced_context
    
    async def integrate_with_combat_system(self, combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate pacing information with combat system.
        
        Args:
            combat_context: Current combat context
            
        Returns:
            Enhanced combat context with relevant pacing information
        """
        enhanced_combat = combat_context.copy()
        
        # Add time-based combat pacing info
        time_since_input = self.get_time_since_last_input()
        
        # Adjust combat pacing based on player response time
        if time_since_input > timedelta(minutes=2):
            enhanced_combat['combat_pace_modifier'] = 'relaxed'
        elif time_since_input < timedelta(seconds=30):
            enhanced_combat['combat_pace_modifier'] = 'intense'
        else:
            enhanced_combat['combat_pace_modifier'] = 'standard'
            
        return enhanced_combat