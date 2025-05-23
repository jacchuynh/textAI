"""
Enhanced Narrative Context Manager with Reputation and World Reaction Support
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from narrative_context_manager import NarrativeContextManager
from world_reaction.reputation_manager import ReputationManager, ActionSignificance


class EnhancedNarrativeContextManager(NarrativeContextManager):
    """
    Enhanced context manager that includes reputation and world reaction context
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize enhanced context manager"""
        super().__init__(*args, **kwargs)
        
        # Initialize reputation manager
        self.reputation_manager = ReputationManager(db_service=getattr(self, 'db_service', None))
        
        self.logger = logging.getLogger("EnhancedNarrativeContextManager")
    
    def prepare_event_context(self, event, actor_id: str, location: str = None) -> Dict[str, Any]:
        """
        Enhanced event context preparation including reputation and world reaction data.
        
        Args:
            event: Game event
            actor_id: ID of the actor (usually player)
            location: Current location
            
        Returns:
            Enhanced context dictionary
        """
        # Get base context from parent class
        base_context = super().prepare_event_context(event, actor_id, location)
        
        # Add reputation and world reaction context
        reputation_context = self.reputation_manager.get_reputation_context_for_llm(
            actor_id, base_context
        )
        
        # Enhance with world reaction specific data
        enhanced_context = {
            **base_context,
            **reputation_context,
            'world_reaction_data': self._prepare_world_reaction_data(actor_id, base_context)
        }
        
        return enhanced_context
    
    def _prepare_world_reaction_data(self, player_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare world reaction specific data"""
        
        # Get current NPCs and their dispositions
        active_npcs = context.get('active_npcs', [])
        npc_dispositions = {}
        
        for npc_id in active_npcs:
            npc_reputation = self.reputation_manager.get_reputation_with_entity(
                player_id, f"npc_{npc_id}"
            )
            npc_dispositions[npc_id] = {
                'reputation_level': npc_reputation.reputation_level.value,
                'disposition': self._reputation_to_disposition(npc_reputation.reputation_level.value)
            }
        
        # Get faction tensions
        world_state = context.get('world_state', {})
        political_stability = world_state.get('political_stability', 'stable')
        economic_status = world_state.get('economic_status', 'stable')
        
        return {
            'npc_dispositions': npc_dispositions,
            'political_tension_level': self._get_tension_level(political_stability),
            'economic_pressure_level': self._get_pressure_level(economic_status),
            'world_state_summary': f"Political: {political_stability}, Economic: {economic_status}",
            'social_atmosphere': self._determine_social_atmosphere(context)
        }
    
    def _reputation_to_disposition(self, reputation_level: str) -> str:
        """Convert reputation level to NPC disposition"""
        disposition_map = {
            'revered': 'deeply respectful and eager to help',
            'respected': 'respectful and helpful',
            'liked': 'friendly and welcoming',
            'neutral': 'neutral and professional',
            'disliked': 'suspicious and unwelcoming',
            'despised': 'hostile and dismissive',
            'hated': 'openly antagonistic'
        }
        return disposition_map.get(reputation_level, 'uncertain')
    
    def _get_tension_level(self, political_stability: str) -> str:
        """Get tension level based on political stability"""
        tension_map = {
            'stable': 'low',
            'unrest': 'moderate',
            'rebellion': 'high',
            'war': 'extreme'
        }
        return tension_map.get(political_stability, 'unknown')
    
    def _get_pressure_level(self, economic_status: str) -> str:
        """Get economic pressure level"""
        pressure_map = {
            'prosperity': 'low',
            'stable': 'low',
            'recession': 'moderate',
            'depression': 'high',
            'collapse': 'extreme'
        }
        return pressure_map.get(economic_status, 'unknown')
    
    def _determine_social_atmosphere(self, context: Dict[str, Any]) -> str:
        """Determine overall social atmosphere"""
        world_state = context.get('world_state', {})
        location_context = context.get('location_context', {})
        
        # Combine factors to determine atmosphere
        political = world_state.get('political_stability', 'stable')
        economic = world_state.get('economic_status', 'stable')
        aura = location_context.get('dominant_aura', 'neutral')
        
        if political in ['rebellion', 'war'] or economic in ['depression', 'collapse']:
            return 'tense and fearful'
        elif political == 'unrest' or economic == 'recession':
            return 'uneasy and cautious'
        elif aura in ['mysterious', 'ominous']:
            return 'mysterious and watchful'
        elif aura in ['peaceful', 'serene']:
            return 'calm and welcoming'
        else:
            return 'normal and busy'
    
    def record_significant_action(self, 
                                player_id: str,
                                action_description: str,
                                significance: ActionSignificance,
                                location: str,
                                affected_entities: List[str] = None,
                                reputation_changes: Dict[str, int] = None) -> str:
        """
        Record a significant action that affects world perception.
        
        Args:
            player_id: Player identifier
            action_description: Description of what the player did
            significance: How significant the action is
            location: Where it happened
            affected_entities: Who/what was affected
            reputation_changes: Reputation changes to apply
            
        Returns:
            Action ID
        """
        return self.reputation_manager.record_significant_action(
            player_id=player_id,
            action_description=action_description,
            significance=significance,
            location=location,
            affected_entities=affected_entities,
            reputation_changes=reputation_changes
        )