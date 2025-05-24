from typing import Dict, Any, List, Optional
from datetime import datetime

class NarrativeContextManager:
    """
    Prepares and manages the context used for narrative generation.
    This class gathers relevant data from multiple sources (character state,
    world state, event details, relationships) into a unified context object.
    """
    
    def __init__(self, narrative_context, world_state_manager=None):
        """
        Initialize the context manager.
        
        Args:
            narrative_context: The NarrativeContext instance to retrieve emotional states from
            world_state_manager: The WorldState instance to retrieve global state from
        """
        self.narrative_context = narrative_context
        self.world_state_manager = world_state_manager
        
    def prepare_event_context(self, event, actor_id=None, target_id=None, location=None) -> Dict[str, Any]:
        """
        Prepare a comprehensive context dictionary for an event.
        
        Args:
            event: The game event being processed
            actor_id: Optional override for the actor (if different from event.actor)
            target_id: Optional target character ID 
            location: Optional location override
            
        Returns:
            A context dictionary with all relevant information for templates
        """
        context = {}
        
        # 1. Basic event context (carried forward from the event)
        if event:
            context.update(event.context or {})
            # Ensure event type is available in context
            context['event_type'] = event.type.name if hasattr(event.type, 'name') else str(event.type)
            
        # 2. Actor context
        actor_id = actor_id or (event.actor if event else None)
        if actor_id:
            actor_context = self._prepare_character_context(actor_id)
            context['actor'] = actor_context
            
            # Allow direct access to actor emotions
            if 'emotions' in actor_context:
                context['actor_emotions'] = actor_context['emotions']
                
        # 3. Target context (if applicable)
        if target_id:
            target_context = self._prepare_character_context(target_id)
            context['target'] = target_context
            
        # 4. World state context
        if self.world_state_manager:
            world_context = self._prepare_world_state_context()
            context['world_state'] = world_context
            
            # For easier access, promote common world state elements to top level
            for key in ['economic_status', 'political_stability', 'current_season', 'active_global_threats']:
                if key in world_context:
                    context[key] = world_context[key]
            
        # 5. Location context
        location_id = location or context.get('location')
        if location_id and hasattr(self.narrative_context, 'location_contexts'):
            location_context = self._prepare_location_context(location_id)
            context['location_context'] = location_context
            
        # 6. Relationship context (if both actor and target)
        if actor_id and target_id:
            relationship_context = self._prepare_relationship_context(actor_id, target_id)
            context['relationship'] = relationship_context
            
        # 7. Time context
        context['current_time'] = datetime.utcnow().isoformat()
        context['time_of_day'] = self._determine_time_of_day()
        
        return context
        
    def _prepare_character_context(self, character_id) -> Dict[str, Any]:
        """
        Prepare context for a specific character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary with character context
        """
        character_context = {
            'id': character_id,
            'name': self._get_character_name(character_id),
            'gender': self._get_character_gender(character_id),
            'exists': True
        }
        
        # Add emotional state if available
        if hasattr(self.narrative_context, 'character_states'):
            char_state = self.narrative_context.character_states.get(character_id, {})
            if 'emotions' in char_state:
                character_context['emotions'] = char_state['emotions']
                
                # Add dominant emotion for easier access
                dominant = max(char_state['emotions'].items(), key=lambda x: x[1], default=(None, 0))
                if dominant[0] and dominant[1] > 0:
                    character_context['dominant_emotion'] = {
                        'type': dominant[0],
                        'intensity': dominant[1]
                    }
            
            # Add traits if available
            if 'traits' in char_state:
                character_context['traits'] = char_state['traits']
        
        return character_context
    
    def _prepare_world_state_context(self) -> Dict[str, Any]:
        """
        Prepare context from world state.
        
        Returns:
            Dictionary with world state context
        """
        if not self.world_state_manager:
            return {}
            
        # Use the summary provided by world_state_manager
        return self.world_state_manager.get_current_state_summary()
    
    def _prepare_location_context(self, location_id) -> Dict[str, Any]:
        """
        Prepare context for a specific location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            Dictionary with location context
        """
        location_context = {'id': location_id}
        
        if hasattr(self.narrative_context, 'location_contexts'):
            loc_data = self.narrative_context.location_contexts.get(location_id, {})
            
            # Copy emotional aura
            if 'emotional_aura' in loc_data:
                location_context['emotional_aura'] = loc_data['emotional_aura']
                
                # Get dominant aura
                dominant = max(loc_data['emotional_aura'].items(), key=lambda x: x[1], default=(None, 0))
                if dominant[0] and dominant[1] > 0:
                    location_context['dominant_aura'] = dominant[0]
                    location_context['aura_intensity'] = dominant[1]
            
            # Recent events
            if 'recent_events' in loc_data:
                location_context['recent_events_count'] = len(loc_data['recent_events'])
                location_context['has_recent_activity'] = len(loc_data['recent_events']) > 0
        
        return location_context
    
    def _prepare_relationship_context(self, actor_id, target_id) -> Dict[str, Any]:
        """
        Prepare relationship context between two characters.
        
        Args:
            actor_id: ID of the primary character
            target_id: ID of the secondary character
            
        Returns:
            Dictionary with relationship context
        """
        relationship_context = {'exists': False}
        
        if not hasattr(self.narrative_context, 'character_states'):
            return relationship_context
            
        actor_state = self.narrative_context.character_states.get(actor_id, {})
        if 'relationships' not in actor_state:
            return relationship_context
            
        relationship = actor_state['relationships'].get(target_id)
        if not relationship:
            return relationship_context
            
        # Relationship exists
        relationship_context['exists'] = True
        
        # Copy core relationship properties
        for key in ['value', 'trust', 'respect', 'familiarity']:
            if key in relationship:
                relationship_context[key] = relationship[key]
        
        # Determine relationship quality
        if 'value' in relationship:
            value = relationship['value']
            if value > 5:
                relationship_context['quality'] = 'positive'
            elif value < -5:
                relationship_context['quality'] = 'negative'
            elif value < -2:
                relationship_context['quality'] = 'unfavorable'
            elif value > 2:
                relationship_context['quality'] = 'favorable'
            else:
                relationship_context['quality'] = 'neutral'
        
        # Add significant events count
        if 'significant_events' in relationship:
            relationship_context['significant_events_count'] = len(relationship['significant_events'])
            relationship_context['has_history'] = len(relationship['significant_events']) > 0
            
        return relationship_context
    
    def _get_character_name(self, character_id) -> str:
        """Get character name from ID - placeholder implementation."""
        # In a real implementation, this would query character data
        # For now, use a simple mapping or the ID itself
        character_names = {
            # Example mapping
            "player_character_id": "Thorn",
            "mountain_elder": "Elder Krag",
            "rival_warrior": "Varek the Bold",
            "constable": "Constable Marrin"
        }
        return character_names.get(character_id, f"Character {character_id}")
    
    def _get_character_gender(self, character_id) -> str:
        """Get character gender from ID - placeholder implementation."""
        # In a real implementation, this would query character data
        # For now, use a simple mapping with "neutral" default
        character_genders = {
            # Example mapping
            "player_character_id": "male",
            "mountain_elder": "male",
            "rival_warrior": "male",
            "constable": "female"
        }
        return character_genders.get(character_id, "neutral")
    
    def _determine_time_of_day(self) -> str:
        """Determine the current time of day - placeholder implementation."""
        # In a real implementation, this would use game world time
        # For now, use real time as an example
        hour = datetime.utcnow().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"