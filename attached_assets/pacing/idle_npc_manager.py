"""
Idle NPC Behavior Manager - Handles NPC-initiated interactions during quiet moments
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from ai_gm_dialogue_generator import AIGMDialogueGenerator


class IdleNPCManager:
    """
    Manages NPC behavior when player is idle in locations with NPCs
    """
    
    def __init__(self, dialogue_generator: AIGMDialogueGenerator, db_service=None):
        """
        Initialize idle NPC manager.
        
        Args:
            dialogue_generator: AI GM dialogue generator
            db_service: Database service for logging
        """
        self.dialogue_generator = dialogue_generator
        self.db_service = db_service
        self.logger = logging.getLogger("IdleNPCManager")
        
        # Configuration
        self.idle_config = {
            'minimum_idle_time': timedelta(minutes=3),     # Min time before NPC initiates
            'maximum_idle_time': timedelta(minutes=8),     # Max time before forced initiation
            'npc_initiative_cooldown': timedelta(minutes=5), # Cooldown between NPC initiatives
            'max_npc_initiatives_per_session': 5           # Limit NPC initiatives per session
        }
        
        # Track NPC initiative history
        self.npc_initiative_history = {}  # {npc_id: last_initiative_time}
        self.session_initiative_count = 0
        
        # NPC personality-based initiative chances
        self.personality_initiative_rates = {
            'friendly': 0.8,      # Very likely to initiate
            'helpful': 0.7,       # Likely to initiate
            'curious': 0.9,       # Most likely to initiate
            'shy': 0.3,          # Unlikely to initiate
            'suspicious': 0.4,    # Somewhat unlikely
            'professional': 0.5,  # Neutral chance
            'gruff': 0.2,        # Very unlikely
            'wise': 0.6          # Moderately likely
        }
        
        # Context-based dialogue themes for different situations
        self.idle_dialogue_themes = {
            'world_events_concern': ['worry', 'information_sharing', 'local_news'],
            'friendly_check_in': ['friendliness', 'casual_conversation', 'helpfulness'],
            'local_knowledge': ['wisdom', 'local_lore', 'helpful_advice'],
            'professional_inquiry': ['business', 'services', 'transactions'],
            'curious_observation': ['curiosity', 'observation', 'questions'],
            'weather_comment': ['casual_conversation', 'observation'],
            'concern_for_player': ['worry', 'care', 'friendliness']
        }
    
    def should_npc_initiate(self, 
                          npc_id: str, 
                          context: Dict[str, Any], 
                          time_since_last_input: timedelta) -> Tuple[bool, Optional[str]]:
        """
        Determine if an NPC should initiate interaction.
        
        Args:
            npc_id: ID of the NPC
            context: Current game context
            time_since_last_input: Time since player's last input
            
        Returns:
            Tuple of (should_initiate, dialogue_theme)
        """
        # Check basic conditions
        if not self._basic_conditions_met(npc_id, time_since_last_input):
            return False, None
        
        # Get NPC data
        npc_data = context.get('npcs', {}).get(npc_id, {})
        if not npc_data:
            return False, None
        
        # Check NPC personality-based initiative chance
        personality = npc_data.get('personality', 'professional')
        initiative_rate = self.personality_initiative_rates.get(personality, 0.5)
        
        # Apply context modifiers
        modified_rate = self._apply_context_modifiers(initiative_rate, npc_data, context)
        
        # Random chance check
        import random
        if random.random() > modified_rate:
            return False, None
        
        # Determine appropriate dialogue theme
        dialogue_theme = self._determine_dialogue_theme(npc_data, context)
        
        return True, dialogue_theme
    
    async def generate_npc_initiative(self, 
                                    npc_id: str, 
                                    dialogue_theme: str, 
                                    context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate NPC-initiated dialogue.
        
        Args:
            npc_id: ID of the initiating NPC
            dialogue_theme: Theme for the dialogue
            context: Current game context
            
        Returns:
            Generated dialogue response or None
        """
        try:
            # Get dialogue themes for the situation
            themes = self.idle_dialogue_themes.get(dialogue_theme, ['casual_conversation'])
            
            # Generate dialogue using AIGMDialogueGenerator
            dialogue_text = self.dialogue_generator.generate_dialogue(
                npc_id=npc_id,
                dialogue_themes=themes,
                context=context,
                player_id=context.get('player_id'),
                is_npc_initiated=True  # Flag to indicate NPC initiated this
            )
            
            if dialogue_text:
                # Update initiative tracking
                self.npc_initiative_history[npc_id] = datetime.utcnow()
                self.session_initiative_count += 1
                
                # Get NPC name for response formatting
                npc_data = context.get('npcs', {}).get(npc_id, {})
                npc_name = npc_data.get('name', npc_id.replace('_', ' ').title())
                
                # Log initiative
                if self.db_service:
                    await self._log_npc_initiative(npc_id, dialogue_theme, dialogue_text, context)
                
                self.logger.info(f"NPC {npc_name} initiated dialogue with theme: {dialogue_theme}")
                
                return {
                    'npc_initiated': True,
                    'npc_id': npc_id,
                    'npc_name': npc_name,
                    'dialogue_theme': dialogue_theme,
                    'dialogue_text': dialogue_text,
                    'response_text': f"{npc_name} {dialogue_text}",
                    'source': 'npc_initiative'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating NPC initiative for {npc_id}: {e}")
            return None
    
    def _basic_conditions_met(self, npc_id: str, time_since_last_input: timedelta) -> bool:
        """Check if basic conditions are met for NPC initiative"""
        
        # Check minimum idle time
        if time_since_last_input < self.idle_config['minimum_idle_time']:
            return False
        
        # Check session initiative limit
        if self.session_initiative_count >= self.idle_config['max_npc_initiatives_per_session']:
            return False
        
        # Check NPC-specific cooldown
        last_initiative = self.npc_initiative_history.get(npc_id)
        if last_initiative:
            time_since_last_initiative = datetime.utcnow() - last_initiative
            if time_since_last_initiative < self.idle_config['npc_initiative_cooldown']:
                return False
        
        return True
    
    def _apply_context_modifiers(self, 
                               base_rate: float, 
                               npc_data: Dict[str, Any], 
                               context: Dict[str, Any]) -> float:
        """Apply context-based modifiers to initiative rate"""
        
        modified_rate = base_rate
        
        # Player reputation modifier
        reputation_context = context.get('player_reputation_summary', '')
        if 'respected' in reputation_context or 'liked' in reputation_context:
            modified_rate += 0.2
        elif 'disliked' in reputation_context or 'despised' in reputation_context:
            modified_rate -= 0.3
        
        # World state modifiers
        world_state = context.get('world_state', {})
        political_stability = world_state.get('political_stability', 'stable')
        
        if political_stability in ['unrest', 'rebellion']:
            # NPCs more likely to initiate during tense times
            modified_rate += 0.1
        
        # Location atmosphere modifier
        location_context = context.get('location_context', {})
        aura = location_context.get('dominant_aura', 'neutral')
        
        if aura == 'friendly':
            modified_rate += 0.1
        elif aura == 'ominous':
            modified_rate -= 0.2
        
        # Time-based modifier (force initiative if too much time has passed)
        time_since_last_input = context.get('time_since_last_input', timedelta(0))
        if time_since_last_input > self.idle_config['maximum_idle_time']:
            modified_rate = 1.0  # Force initiative
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, modified_rate))
    
    def _determine_dialogue_theme(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Determine appropriate dialogue theme based on context"""
        
        # Check world state first
        world_state = context.get('world_state', {})
        political_stability = world_state.get('political_stability', 'stable')
        
        if political_stability in ['unrest', 'rebellion', 'war']:
            return 'world_events_concern'
        
        # Check NPC personality
        personality = npc_data.get('personality', 'professional')
        
        if personality in ['friendly', 'helpful']:
            return 'friendly_check_in'
        elif personality in ['wise', 'scholarly']:
            return 'local_knowledge'
        elif personality in ['curious', 'inquisitive']:
            return 'curious_observation'
        elif personality in ['professional', 'merchant']:
            return 'professional_inquiry'
        
        # Check player reputation
        reputation_context = context.get('player_reputation_summary', '')
        if 'disliked' in reputation_context or 'concerned' in reputation_context:
            return 'concern_for_player'
        
        # Default to friendly check-in
        return 'friendly_check_in'
    
    async def _log_npc_initiative(self, 
                                npc_id: str, 
                                dialogue_theme: str, 
                                dialogue_text: str, 
                                context: Dict[str, Any]):
        """Log NPC initiative to database"""
        if self.db_service:
            await self.db_service.save_event({
                'session_id': context.get('session_id'),
                'event_type': 'NPC_INITIATED_DIALOGUE',
                'actor': npc_id,
                'context': {
                    'dialogue_theme': dialogue_theme,
                    'dialogue_text': dialogue_text,
                    'location': context.get('current_location'),
                    'initiative_count': self.session_initiative_count
                }
            })
    
    def get_idle_npc_statistics(self) -> Dict[str, Any]:
        """Get NPC initiative statistics"""
        return {
            'session_initiative_count': self.session_initiative_count,
            'unique_npcs_initiated': len(self.npc_initiative_history),
            'npc_initiative_history': {
                npc_id: last_time.isoformat() 
                for npc_id, last_time in self.npc_initiative_history.items()
            },
            'configuration': {
                'minimum_idle_time': str(self.idle_config['minimum_idle_time']),
                'maximum_idle_time': str(self.idle_config['maximum_idle_time']),
                'max_initiatives_per_session': self.idle_config['max_npc_initiatives_per_session']
            }
        }