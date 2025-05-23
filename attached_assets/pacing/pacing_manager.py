"""
Pacing Manager for AI GM Brain - Controls narrative rhythm and ambient storytelling
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import asyncio


class PacingState(Enum):
    """Different pacing states for the game"""
    ACTIVE = "active"           # Recent significant activity
    SETTLING = "settling"       # Activity slowing down
    LULL = "lull"              # Extended quiet period
    STAGNANT = "stagnant"      # Too quiet, needs intervention


class AmbientTrigger(Enum):
    """Types of ambient narrative triggers"""
    TIME_BASED = "time_based"                   # Based on time elapsed
    LOCATION_BASED = "location_based"           # Based on location characteristics
    WORLD_STATE_BASED = "world_state_based"     # Based on world events
    NPC_BASED = "npc_based"                     # Based on NPC presence
    WEATHER_BASED = "weather_based"             # Based on weather/season
    MOOD_BASED = "mood_based"                   # Based on current atmosphere


@dataclass
class PacingMetrics:
    """Metrics for tracking game pacing"""
    last_significant_event: datetime
    last_branch_progression: datetime
    last_player_input: datetime
    last_ambient_injection: datetime
    interaction_count_last_hour: int
    current_location_duration: timedelta
    current_pacing_state: PacingState
    
    def time_since_significant_event(self) -> timedelta:
        """Get time since last significant event"""
        return datetime.utcnow() - self.last_significant_event
    
    def time_since_branch_progression(self) -> timedelta:
        """Get time since last branch progression"""
        return datetime.utcnow() - self.last_branch_progression
    
    def time_since_last_input(self) -> timedelta:
        """Get time since last player input"""
        return datetime.utcnow() - self.last_player_input


class PacingManager:
    """
    Manages game pacing and ambient storytelling injection
    """
    
    def __init__(self, template_processor, db_service=None):
        """
        Initialize pacing manager.
        
        Args:
            template_processor: Template processor for ambient narration
            db_service: Database service for logging
        """
        self.template_processor = template_processor
        self.db_service = db_service
        self.logger = logging.getLogger("PacingManager")
        
        # Pacing configuration
        self.pacing_config = {
            'significant_event_threshold': timedelta(minutes=10),  # 10 min = lull
            'branch_progression_threshold': timedelta(minutes=15), # 15 min = stagnant
            'ambient_injection_cooldown': timedelta(minutes=5),    # Min 5 min between ambient
            'location_change_significance': timedelta(minutes=2),  # Location changes reset some timers
            'interaction_activity_threshold': 3                    # 3+ interactions/hour = active
        }
        
        # Current metrics
        self.current_metrics = PacingMetrics(
            last_significant_event=datetime.utcnow(),
            last_branch_progression=datetime.utcnow(),
            last_player_input=datetime.utcnow(),
            last_ambient_injection=datetime.utcnow() - timedelta(hours=1),  # Allow immediate first ambient
            interaction_count_last_hour=0,
            current_location_duration=timedelta(0),
            current_pacing_state=PacingState.ACTIVE
        )
        
        # Ambient narrative templates
        self.ambient_templates = {
            'time_passage': [
                "Time passes quietly in {location_name}. {ambient_detail}",
                "The {time_of_day} continues its steady rhythm. {ambient_detail}",
                "Moments drift by peacefully. {ambient_detail}"
            ],
            'location_atmosphere': [
                "The atmosphere of {location_name} {atmospheric_verb}. {sensory_detail}",
                "{location_name} {location_mood_verb} around you. {ambient_sound}",
                "The essence of {location_name} {presence_verb}. {atmospheric_note}"
            ],
            'world_state_hints': [
                "Distant {world_state_indicator} {reminder_verb} of the broader world's concerns.",
                "The ongoing {world_situation} {influence_verb} even this peaceful moment.",
                "Echoes of {world_events} {reach_verb} even here."
            ],
            'seasonal_atmospheric': [
                "The {season} air {seasonal_verb}. {seasonal_detail}",
                "{season} weather {weather_verb} the surroundings. {weather_effect}",
                "Nature's {season} rhythm {natural_verb}. {natural_observation}"
            ],
            'npc_ambient': [
                "{npc_name} {npc_ambient_action} nearby. {npc_detail}",
                "You notice {npc_name} {npc_activity}. {npc_observation}",
                "In the background, {npc_name} {background_activity}."
            ]
        }
        
        # Pacing statistics
        self.pacing_stats = {
            'total_ambient_injections': 0,
            'ambient_triggers': {trigger: 0 for trigger in AmbientTrigger},
            'pacing_state_changes': {state: 0 for state in PacingState},
            'current_session_rhythm': 'unknown'
        }
    
    def update_player_activity(self, 
                             input_string: str, 
                             response: Dict[str, Any], 
                             context: Dict[str, Any]):
        """
        Update pacing metrics based on player activity.
        
        Args:
            input_string: Player's input
            response: AI GM response
            context: Current game context
        """
        now = datetime.utcnow()
        
        # Update basic metrics
        self.current_metrics.last_player_input = now
        
        # Check for significant events
        if self._is_significant_event(response):
            self.current_metrics.last_significant_event = now
            self.logger.info("Significant event detected, resetting pacing timer")
        
        # Check for branch progression
        if self._is_branch_progression(response):
            self.current_metrics.last_branch_progression = now
            self.logger.info("Branch progression detected, updating pacing metrics")
        
        # Update location duration
        current_location = context.get('current_location')
        if hasattr(self, '_last_location') and self._last_location != current_location:
            # Location changed, reset location duration
            self.current_metrics.current_location_duration = timedelta(0)
            self._location_entry_time = now
        else:
            # Same location, update duration
            if hasattr(self, '_location_entry_time'):
                self.current_metrics.current_location_duration = now - self._location_entry_time
            else:
                self._location_entry_time = now
        
        self._last_location = current_location
        
        # Update interaction count (simplified - in real implementation, use sliding window)
        self.current_metrics.interaction_count_last_hour += 1
        
        # Update pacing state
        old_state = self.current_metrics.current_pacing_state
        new_state = self._calculate_pacing_state()
        
        if old_state != new_state:
            self.current_metrics.current_pacing_state = new_state
            self.pacing_stats['pacing_state_changes'][new_state] += 1
            self.logger.info(f"Pacing state changed: {old_state.value} -> {new_state.value}")
    
    def should_inject_ambient_content(self, context: Dict[str, Any]) -> Tuple[bool, Optional[AmbientTrigger]]:
        """
        Determine if ambient content should be injected.
        
        Args:
            context: Current game context
            
        Returns:
            Tuple of (should_inject, trigger_type)
        """
        # Check cooldown
        time_since_last_ambient = datetime.utcnow() - self.current_metrics.last_ambient_injection
        if time_since_last_ambient < self.pacing_config['ambient_injection_cooldown']:
            return False, None
        
        # Check pacing state
        if self.current_metrics.current_pacing_state in [PacingState.LULL, PacingState.STAGNANT]:
            
            # Determine best trigger type
            trigger = self._determine_ambient_trigger(context)
            return True, trigger
        
        # Check for special conditions even if not in lull
        if self._should_inject_despite_pacing(context):
            trigger = self._determine_ambient_trigger(context)
            return True, trigger
        
        return False, None
    
    async def generate_ambient_content(self, 
                                     trigger: AmbientTrigger, 
                                     context: Dict[str, Any]) -> Optional[str]:
        """
        Generate ambient narrative content.
        
        Args:
            trigger: Type of ambient trigger
            context: Current game context
            
        Returns:
            Generated ambient narrative or None
        """
        try:
            # Select appropriate template category
            template_category = self._map_trigger_to_template(trigger)
            templates = self.ambient_templates.get(template_category, [])
            
            if not templates:
                return None
            
            # Choose template based on context
            selected_template = self._select_template(templates, context, trigger)
            
            # Build template context
            template_context = self._build_ambient_template_context(context, trigger)
            
            # Process template
            ambient_content = self.template_processor.process(selected_template, template_context)
            
            # Update metrics
            self.current_metrics.last_ambient_injection = datetime.utcnow()
            self.pacing_stats['total_ambient_injections'] += 1
            self.pacing_stats['ambient_triggers'][trigger] += 1
            
            # Log ambient injection
            if self.db_service:
                await self._log_ambient_injection(trigger, ambient_content, context)
            
            self.logger.info(f"Generated ambient content ({trigger.value}): {ambient_content[:50]}...")
            return ambient_content
            
        except Exception as e:
            self.logger.error(f"Error generating ambient content: {e}")
            return None
    
    def _is_significant_event(self, response: Dict[str, Any]) -> bool:
        """Check if response represents a significant event"""
        
        # Check decision priority
        priority = response.get('decision_priority', '')
        if priority in ['LLM_OPPORTUNITY_ALIGNMENT', 'LLM_BRANCH_ACTION_ALIGNMENT']:
            return True
        
        # Check if action was executed successfully
        if response.get('action_executed', False):
            action_result = response.get('action_result', {})
            if action_result.get('outcome') == 'success':
                return True
        
        # Check world reaction assessment
        if response.get('phase5_metadata', {}).get('world_reaction_assessed', False):
            if response.get('phase5_metadata', {}).get('attitude_shift_detected', False):
                return True
        
        return False
    
    def _is_branch_progression(self, response: Dict[str, Any]) -> bool:
        """Check if response represents branch progression"""
        
        action_result = response.get('action_result', {})
        if action_result:
            action_type = action_result.get('action_type', '')
            if action_type in ['opportunity_initiation', 'branch_action']:
                return action_result.get('outcome') == 'success'
        
        return False
    
    def _calculate_pacing_state(self) -> PacingState:
        """Calculate current pacing state based on metrics"""
        
        time_since_significant = self.current_metrics.time_since_significant_event()
        time_since_branch = self.current_metrics.time_since_branch_progression()
        
        # Check for stagnant state (no branch progression)
        if time_since_branch > self.pacing_config['branch_progression_threshold']:
            return PacingState.STAGNANT
        
        # Check for lull state (no significant events)
        elif time_since_significant > self.pacing_config['significant_event_threshold']:
            return PacingState.LULL
        
        # Check activity level
        elif self.current_metrics.interaction_count_last_hour >= self.pacing_config['interaction_activity_threshold']:
            return PacingState.ACTIVE
        
        else:
            return PacingState.SETTLING
    
    def _determine_ambient_trigger(self, context: Dict[str, Any]) -> AmbientTrigger:
        """Determine the best ambient trigger for current context"""
        
        # Priority order based on context
        
        # NPC-based if NPCs are present
        if context.get('present_npcs') or context.get('active_npcs'):
            return AmbientTrigger.NPC_BASED
        
        # World state-based if there are significant world events
        world_state = context.get('world_state', {})
        if (world_state.get('political_stability') != 'stable' or 
            world_state.get('economic_status') != 'stable'):
            return AmbientTrigger.WORLD_STATE_BASED
        
        # Location-based if in an interesting location
        location_context = context.get('location_context', {})
        if location_context.get('dominant_aura') not in ['neutral', None]:
            return AmbientTrigger.LOCATION_BASED
        
        # Weather/seasonal if current season is notable
        current_season = context.get('current_season', 'spring')
        if current_season in ['winter', 'autumn']:
            return AmbientTrigger.WEATHER_BASED
        
        # Default to time-based
        return AmbientTrigger.TIME_BASED
    
    def _should_inject_despite_pacing(self, context: Dict[str, Any]) -> bool:
        """Check if ambient should be injected despite current pacing state"""
        
        # Inject if player has been in same location for a long time
        if self.current_metrics.current_location_duration > timedelta(minutes=20):
            return True
        
        # Inject if world state is very significant
        world_state = context.get('world_state', {})
        if world_state.get('political_stability') in ['rebellion', 'war']:
            return True
        
        return False
    
    def _map_trigger_to_template(self, trigger: AmbientTrigger) -> str:
        """Map trigger type to template category"""
        mapping = {
            AmbientTrigger.TIME_BASED: 'time_passage',
            AmbientTrigger.LOCATION_BASED: 'location_atmosphere',
            AmbientTrigger.WORLD_STATE_BASED: 'world_state_hints',
            AmbientTrigger.NPC_BASED: 'npc_ambient',
            AmbientTrigger.WEATHER_BASED: 'seasonal_atmospheric',
            AmbientTrigger.MOOD_BASED: 'location_atmosphere'
        }
        return mapping.get(trigger, 'time_passage')
    
    def _select_template(self, templates: List[str], context: Dict[str, Any], trigger: AmbientTrigger) -> str:
        """Select most appropriate template from available options"""
        # For now, use simple selection. Could be enhanced with context analysis
        import random
        return random.choice(templates)
    
    def _build_ambient_template_context(self, context: Dict[str, Any], trigger: AmbientTrigger) -> Dict[str, Any]:
        """Build context for ambient template processing"""
        
        base_context = {
            'location_name': context.get('current_location', 'the area'),
            'time_of_day': context.get('time_of_day', 'the day'),
            'season': context.get('current_season', 'spring'),
            **context  # Include all context
        }
        
        # Add trigger-specific context
        if trigger == AmbientTrigger.TIME_BASED:
            base_context.update({
                'ambient_detail': 'The world continues its quiet rhythm.',
                'atmospheric_verb': 'settles peacefully',
                'sensory_detail': 'Gentle sounds drift through the air.'
            })
        
        elif trigger == AmbientTrigger.LOCATION_BASED:
            location_context = context.get('location_context', {})
            aura = location_context.get('dominant_aura', 'peaceful')
            base_context.update({
                'atmospheric_verb': f'feels {aura}',
                'location_mood_verb': f'maintains its {aura} presence',
                'presence_verb': f'emanates a {aura} energy',
                'sensory_detail': f'The {aura} atmosphere is tangible.',
                'ambient_sound': self._get_ambient_sound_for_aura(aura),
                'atmospheric_note': f'Everything here speaks of {aura} intentions.'
            })
        
        elif trigger == AmbientTrigger.WORLD_STATE_BASED:
            world_state = context.get('world_state', {})
            political = world_state.get('political_stability', 'stable')
            economic = world_state.get('economic_status', 'stable')
            
            base_context.update({
                'world_state_indicator': self._get_world_state_indicator(political, economic),
                'reminder_verb': 'remind you',
                'world_situation': f'{political} political situation',
                'influence_verb': 'casts its shadow over',
                'world_events': f'the {political} times',
                'reach_verb': 'manage to reach'
            })
        
        elif trigger == AmbientTrigger.WEATHER_BASED:
            season = context.get('current_season', 'spring')
            base_context.update({
                'seasonal_verb': self._get_seasonal_verb(season),
                'seasonal_detail': self._get_seasonal_detail(season),
                'weather_verb': f'brings {season}\'s influence to',
                'weather_effect': self._get_weather_effect(season),
                'natural_verb': 'continues undisturbed',
                'natural_observation': self._get_natural_observation(season)
            })
        
        elif trigger == AmbientTrigger.NPC_BASED:
            npcs = context.get('present_npcs', []) or context.get('active_npcs', [])
            if npcs:
                npc_id = npcs[0]
                npc_name = context.get('npcs', {}).get(npc_id, {}).get('name', npc_id.replace('_', ' ').title())
                
                base_context.update({
                    'npc_name': npc_name,
                    'npc_ambient_action': self._get_npc_ambient_action(),
                    'npc_detail': 'They seem absorbed in their own thoughts.',
                    'npc_activity': self._get_npc_activity(),
                    'npc_observation': 'Their presence adds life to the scene.',
                    'background_activity': self._get_background_activity()
                })
        
        return base_context
    
    def _get_ambient_sound_for_aura(self, aura: str) -> str:
        """Get appropriate ambient sound for location aura"""
        sounds = {
            'peaceful': 'Gentle sounds create a soothing backdrop.',
            'mysterious': 'Strange whispers seem to echo from unseen places.',
            'ominous': 'An unsettling quiet dominates the atmosphere.',
            'sacred': 'Reverent silence fills the space.',
            'bustling': 'The sounds of activity provide constant background noise.'
        }
        return sounds.get(aura, 'Subtle sounds drift through the air.')
    
    def _get_world_state_indicator(self, political: str, economic: str) -> str:
        """Get world state indicator text"""
        if political != 'stable':
            return f'echoes of {political}'
        elif economic != 'stable':
            return f'signs of economic {economic}'
        else:
            return 'distant concerns'
    
    def _get_seasonal_verb(self, season: str) -> str:
        """Get seasonal verb"""
        verbs = {
            'spring': 'carries the promise of renewal',
            'summer': 'brings warmth and vitality',
            'autumn': 'whispers of coming change',
            'winter': 'brings a crisp clarity'
        }
        return verbs.get(season, 'moves with natural rhythm')
    
    def _get_seasonal_detail(self, season: str) -> str:
        """Get seasonal detail"""
        details = {
            'spring': 'New growth can be seen everywhere.',
            'summer': 'The warmth is pleasant and energizing.',
            'autumn': 'Leaves rustle with the season\'s passage.',
            'winter': 'The cold is sharp but invigorating.'
        }
        return details.get(season, 'The season makes its presence known.')
    
    def _get_weather_effect(self, season: str) -> str:
        """Get weather effect description"""
        effects = {
            'spring': 'Everything seems touched with new possibility.',
            'summer': 'A pleasant warmth suffuses everything.',
            'autumn': 'A sense of transition colors the scene.',
            'winter': 'A crystalline clarity sharpens all details.'
        }
        return effects.get(season, 'The weather adds its own character.')
    
    def _get_natural_observation(self, season: str) -> str:
        """Get natural observation for season"""
        observations = {
            'spring': 'Nature awakens with renewed vigor.',
            'summer': 'The natural world hums with life.',
            'autumn': 'Nature prepares for its quiet rest.',
            'winter': 'Nature rests in peaceful dormancy.'
        }
        return observations.get(season, 'Nature follows its ancient patterns.')
    
    def _get_npc_ambient_action(self) -> str:
        """Get random NPC ambient action"""
        actions = [
            'moves about quietly',
            'tends to their own affairs',
            'goes about their business',
            'works at some task',
            'pauses thoughtfully'
        ]
        import random
        return random.choice(actions)
    
    def _get_npc_activity(self) -> str:
        """Get NPC activity description"""
        activities = [
            'engaged in quiet work',
            'lost in contemplation',
            'attending to daily tasks',
            'moving with purpose',
            'observing their surroundings'
        ]
        import random
        return random.choice(activities)
    
    def _get_background_activity(self) -> str:
        """Get background activity description"""
        activities = [
            'continues their quiet routine',
            'maintains their steady rhythm',
            'pursues their own concerns',
            'follows their established patterns',
            'keeps to their familiar habits'
        ]
        import random
        return random.choice(activities)
    
    async def _log_ambient_injection(self, 
                                   trigger: AmbientTrigger, 
                                   content: str, 
                                   context: Dict[str, Any]):
        """Log ambient injection to database"""
        if self.db_service:
            await self.db_service.save_event({
                'session_id': context.get('session_id'),
                'event_type': 'AMBIENT_CONTENT_INJECTED',
                'actor': 'pacing_manager',
                'context': {
                    'trigger_type': trigger.value,
                    'content': content,
                    'pacing_state': self.current_metrics.current_pacing_state.value,
                    'location': context.get('current_location'),
                    'time_since_last_significant': str(self.current_metrics.time_since_significant_event())
                }
            })
    
    def get_pacing_statistics(self) -> Dict[str, Any]:
        """Get pacing and ambient storytelling statistics"""
        return {
            'current_pacing_state': self.current_metrics.current_pacing_state.value,
            'time_since_significant_event': str(self.current_metrics.time_since_significant_event()),
            'time_since_branch_progression': str(self.current_metrics.time_since_branch_progression()),
            'total_ambient_injections': self.pacing_stats['total_ambient_injections'],
            'ambient_trigger_usage': {
                trigger.value: count 
                for trigger, count in self.pacing_stats['ambient_triggers'].items()
            },
            'pacing_state_distribution': {
                state.value: count 
                for state, count in self.pacing_stats['pacing_state_changes'].items()
            }
        }