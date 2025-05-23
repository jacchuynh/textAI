"""
Pacing Manager for AI GM Brain - Controls narrative rhythm and ambient storytelling
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import asyncio
import random


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
    
    def __init__(self, template_processor=None, db_service=None):
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
        
        # Template details for filling in variables
        self.template_details = {
            'atmospheric_verb': ['envelops you', 'settles in', 'changes subtly', 'intensifies'],
            'location_mood_verb': ['breathes', 'shifts', 'pulses', 'radiates', 'comes alive'],
            'presence_verb': ['permeates the air', 'makes itself known', 'lingers', 'hangs in the air'],
            'ambient_sound': ['A distant sound catches your attention', 'You hear faint noises in the distance', 'The ambient sounds create a soothing backdrop'],
            'ambient_detail': ['Light filters through in a mesmerizing pattern', 'The ambient sounds form a calming backdrop', 'Everything feels momentarily still'],
            'sensory_detail': ['A subtle scent fills the air', 'The sounds around you form a tapestry', 'There is a palpable feeling in the atmosphere'],
            'atmospheric_note': ['There is something intriguing about this place', 'It is quite remarkable how the atmosphere shifts', 'You cannot help but take in the surroundings'],
            
            'world_state_indicator': ['shouting', 'rumors', 'news', 'discussions', 'messengers', 'events'],
            'reminder_verb': ['reminds you', 'speaks', 'whispers', 'hints', 'serves as testament'],
            'world_situation': ['political tension', 'economic situation', 'social unrest', 'diplomatic relations'],
            'influence_verb': ['reaches', 'influences', 'touches', 'colors', 'affects'],
            'world_events': ['conflicts', 'celebrations', 'political changes', 'economic shifts'],
            'reach_verb': ['finds its way', 'manages to reach', 'slightly disturbs', 'subtly alters'],
            
            'seasonal_verb': ['has a distinctive feeling', 'carries unique scents', 'brings its own character', 'settles on your skin'],
            'seasonal_detail': ['Birds call to one another in the distance', 'The foliage rustles with a natural melody', 'The landscape shows subtle seasonal changes'],
            'weather_verb': ['transforms', 'shapes', 'enhances', 'alters', 'defines'],
            'weather_effect': ['Light changes quality as clouds shift overhead', 'The air carries hints of the changing weather', 'The environment responds to natural rhythm'],
            'natural_verb': ['continues regardless of human concerns', 'makes itself evident', 'keeps its own time', 'moves at its own pace'],
            'natural_observation': ['Nature continues its unending cycle', 'The ecosystem thrives in its own balance', 'The natural world moves at its own pace'],
            
            'npc_ambient_action': ['works quietly', 'moves about', 'attends to their tasks', 'exists in their own routine'],
            'npc_activity': ['going about their business', 'engaged in routine tasks', 'focused on their own concerns'],
            'npc_detail': ['They seem unaware of your attention', 'Their movements have a practiced efficiency', 'They occasionally glance in your direction'],
            'npc_observation': ['You wonder about their everyday life', 'There is something intriguing about their mannerisms', 'Their routine seems well-established'],
            'background_activity': ['continues with their day', 'maintains their routine', 'exists in their own world', 'attends to various matters']
        }
        
        # Initialize tracking variables
        self._last_location = None
        self._location_entry_time = datetime.utcnow()
        
        # Pacing statistics
        self.pacing_stats = {
            'total_ambient_injections': 0,
            'ambient_triggers': {trigger.value: 0 for trigger in AmbientTrigger},
            'pacing_state_changes': {state.value: 0 for state in PacingState},
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
            self.pacing_stats['pacing_state_changes'][new_state.value] += 1
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
    
    def generate_ambient_content(self, 
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
            
            # Process template (simplified if no template processor)
            if self.template_processor:
                ambient_content = self.template_processor.process(selected_template, template_context)
            else:
                # Simplified template filling
                ambient_content = self._fill_template(selected_template, template_context)
            
            # Update metrics
            self.current_metrics.last_ambient_injection = datetime.utcnow()
            self.pacing_stats['total_ambient_injections'] += 1
            self.pacing_stats['ambient_triggers'][trigger.value] += 1
            
            # Log ambient injection
            self.logger.info(f"Generated ambient content ({trigger.value}): {ambient_content[:50]}...")
            return ambient_content
            
        except Exception as e:
            self.logger.error(f"Error generating ambient content: {e}")
            return None
    
    def _is_significant_event(self, response: Dict[str, Any]) -> bool:
        """Check if response represents a significant event"""
        
        # Check decision priority in metadata
        metadata = response.get('metadata', {})
        decision_tree = metadata.get('decision_tree', {})
        
        # Check response basis in decision tree
        response_basis = decision_tree.get('response_basis', '')
        if response_basis in ['LLM_OPPORTUNITY_ALIGNMENT', 'LLM_BRANCH_ACTION_ALIGNMENT', 'BRANCH_ACTION']:
            return True
        
        # Check for successful command execution
        if metadata.get('command_parser', {}).get('success', False):
            # Command was successfully executed
            return True
        
        # Check world reaction
        if metadata.get('world_reaction', {}).get('attitude_shift'):
            # There was a significant world reaction with attitude shift
            return True
        
        return False
    
    def _is_branch_progression(self, response: Dict[str, Any]) -> bool:
        """Check if response represents branch progression"""
        
        metadata = response.get('metadata', {})
        decision_tree = metadata.get('decision_tree', {})
        
        # Check if this was a branch action
        action_taken = decision_tree.get('action_taken', '')
        if 'branch' in action_taken.lower() or 'opportunity' in action_taken.lower():
            # This was a branch or opportunity action
            return decision_tree.get('success', False)
        
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
        return random.choice(templates)
    
    def _build_ambient_template_context(self, context: Dict[str, Any], trigger: AmbientTrigger) -> Dict[str, Any]:
        """Build context for ambient template processing"""
        
        base_context = {
            'location_name': context.get('current_location', 'this place').replace('_', ' ').title(),
            'time_of_day': context.get('time_of_day', 'day'),
            'season': context.get('current_season', 'season'),
        }
        
        # Add random template details based on the trigger type
        template_context = base_context.copy()
        
        for key, values in self.template_details.items():
            template_context[key] = random.choice(values)
        
        # Add NPC details if relevant
        if trigger == AmbientTrigger.NPC_BASED:
            npcs = context.get('present_npcs', [])
            if npcs:
                npc_id = random.choice(npcs)
                npc_data = context.get('npcs', {}).get(npc_id, {})
                template_context['npc_name'] = npc_data.get('name', npc_id.replace('_', ' ').title())
        
        # Add world state details if relevant
        if trigger == AmbientTrigger.WORLD_STATE_BASED:
            world_state = context.get('world_state', {})
            template_context['world_situation'] = world_state.get('political_stability', 'situation')
            template_context['world_events'] = f"{world_state.get('political_stability', '')} events"
        
        return template_context
    
    def _fill_template(self, template: str, context: Dict[str, Any]) -> str:
        """Simple template filling when template processor is not available"""
        result = template
        
        for key, value in context.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def get_pacing_statistics(self) -> Dict[str, Any]:
        """Get statistics about pacing system"""
        return {
            'current_pacing_state': self.current_metrics.current_pacing_state.value,
            'time_since_last_significant_event': str(self.current_metrics.time_since_significant_event()),
            'time_since_last_branch_progression': str(self.current_metrics.time_since_branch_progression()),
            'ambient_injections': self.pacing_stats['total_ambient_injections'],
            'current_location_duration': str(self.current_metrics.current_location_duration),
            'state_changes': self.pacing_stats['pacing_state_changes']
        }