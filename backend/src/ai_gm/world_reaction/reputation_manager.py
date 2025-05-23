"""
Reputation and Recent Actions Manager for World Reaction System
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import uuid


class ReputationLevel(Enum):
    """Player reputation levels"""
    REVERED = "revered"           # +3
    RESPECTED = "respected"       # +2  
    LIKED = "liked"              # +1
    NEUTRAL = "neutral"          # 0
    DISLIKED = "disliked"        # -1
    DESPISED = "despised"        # -2
    HATED = "hated"              # -3


class ActionSignificance(Enum):
    """Significance levels for player actions"""
    MINOR = "minor"              # Local impact only
    MODERATE = "moderate"        # Regional impact
    MAJOR = "major"              # Widespread impact
    LEGENDARY = "legendary"      # World-changing impact


@dataclass
class ReputationEntry:
    """Represents reputation with a specific faction/NPC"""
    entity_id: str
    entity_name: str
    entity_type: str  # 'faction', 'npc', 'region', 'global'
    reputation_level: ReputationLevel
    reputation_score: int  # Numeric value for calculations
    last_updated: datetime
    reasons: List[str] = field(default_factory=list)
    
    def get_reputation_description(self) -> str:
        """Get descriptive text for reputation level"""
        descriptions = {
            ReputationLevel.REVERED: "You are revered and held in highest esteem",
            ReputationLevel.RESPECTED: "You are well-respected and trusted",
            ReputationLevel.LIKED: "You are generally liked and welcomed",
            ReputationLevel.NEUTRAL: "You are regarded neutrally",
            ReputationLevel.DISLIKED: "You are viewed with suspicion and dislike",
            ReputationLevel.DESPISED: "You are despised and unwelcome",
            ReputationLevel.HATED: "You are hated and considered an enemy"
        }
        return descriptions.get(self.reputation_level, "Your reputation is unknown")


@dataclass
class SignificantAction:
    """Represents a significant player action that affects world perception"""
    action_id: str
    action_description: str
    significance: ActionSignificance
    location: str
    timestamp: datetime
    affected_entities: List[str] = field(default_factory=list)
    reputation_changes: Dict[str, int] = field(default_factory=dict)
    world_state_impact: Dict[str, Any] = field(default_factory=dict)
    witnesses: List[str] = field(default_factory=list)
    
    def get_action_summary(self) -> str:
        """Get concise summary of the action for context"""
        time_ago = self._get_time_ago_string()
        return f"{self.action_description} ({self.location}, {time_ago})"
    
    def _get_time_ago_string(self) -> str:
        """Get human-readable time difference"""
        now = datetime.utcnow()
        diff = now - self.timestamp
        
        if diff.days > 7:
            return f"{diff.days // 7} weeks ago"
        elif diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        else:
            return "recently"


class ReputationManager:
    """
    Manages player reputation with various entities and tracks significant actions
    """
    
    def __init__(self, db_service=None):
        """
        Initialize reputation manager.
        
        Args:
            db_service: Database service for persistence
        """
        self.db_service = db_service
        self.logger = logging.getLogger("ReputationManager")
        
        # In-memory caches
        self.reputation_cache: Dict[str, ReputationEntry] = {}
        self.recent_actions_cache: List[SignificantAction] = []
        
        # Configuration
        self.max_recent_actions = 10  # Keep last 10 significant actions
        self.action_relevance_days = 30  # Actions older than 30 days are less relevant
        
        # Load from database if available
        if self.db_service:
            self._load_from_database()
    
    def get_reputation_with_entity(self, player_id: str, entity_id: str) -> Optional[ReputationEntry]:
        """Get player's reputation with a specific entity"""
        cache_key = f"{player_id}_{entity_id}"
        
        if cache_key in self.reputation_cache:
            return self.reputation_cache[cache_key]
        
        # Load from database if not cached
        if self.db_service:
            reputation_data = self._load_reputation_from_db(player_id, entity_id)
            if reputation_data:
                entry = ReputationEntry(**reputation_data)
                self.reputation_cache[cache_key] = entry
                return entry
        
        # Return neutral reputation if not found
        return ReputationEntry(
            entity_id=entity_id,
            entity_name=entity_id.replace('_', ' ').title(),
            entity_type='unknown',
            reputation_level=ReputationLevel.NEUTRAL,
            reputation_score=0,
            last_updated=datetime.utcnow()
        )
    
    def get_global_reputation(self, player_id: str) -> ReputationEntry:
        """Get player's global reputation"""
        return self.get_reputation_with_entity(player_id, 'global')
    
    def get_relevant_reputations(self, player_id: str, context: Dict[str, Any]) -> List[ReputationEntry]:
        """Get reputations relevant to current context"""
        relevant_reputations = []
        
        # Always include global reputation
        global_rep = self.get_global_reputation(player_id)
        relevant_reputations.append(global_rep)
        
        # Include location-based reputation
        current_location = context.get('current_location')
        if current_location:
            location_rep = self.get_reputation_with_entity(player_id, f"location_{current_location}")
            if location_rep.reputation_level != ReputationLevel.NEUTRAL:
                relevant_reputations.append(location_rep)
        
        # Include faction reputations if relevant
        active_factions = context.get('active_factions', [])
        for faction in active_factions:
            faction_rep = self.get_reputation_with_entity(player_id, f"faction_{faction}")
            if faction_rep.reputation_level != ReputationLevel.NEUTRAL:
                relevant_reputations.append(faction_rep)
        
        # Include NPC reputations if in conversation
        active_npcs = context.get('active_npcs', [])
        for npc_id in active_npcs:
            npc_rep = self.get_reputation_with_entity(player_id, f"npc_{npc_id}")
            if npc_rep.reputation_level != ReputationLevel.NEUTRAL:
                relevant_reputations.append(npc_rep)
        
        return relevant_reputations
    
    def record_significant_action(self, 
                                player_id: str, 
                                action_description: str,
                                significance: ActionSignificance,
                                location: str,
                                affected_entities: List[str] = None,
                                reputation_changes: Dict[str, int] = None,
                                world_state_impact: Dict[str, Any] = None) -> str:
        """
        Record a significant player action that affects world perception.
        
        Args:
            player_id: Player identifier
            action_description: Description of the action
            significance: How significant the action is
            location: Where the action took place
            affected_entities: List of entities affected by the action
            reputation_changes: Reputation changes {entity_id: change_amount}
            world_state_impact: Impact on world state
            
        Returns:
            Action ID
        """
        action_id = str(uuid.uuid4())
        
        action = SignificantAction(
            action_id=action_id,
            action_description=action_description,
            significance=significance,
            location=location,
            timestamp=datetime.utcnow(),
            affected_entities=affected_entities or [],
            reputation_changes=reputation_changes or {},
            world_state_impact=world_state_impact or {}
        )
        
        # Add to recent actions cache
        self.recent_actions_cache.append(action)
        
        # Maintain cache size
        if len(self.recent_actions_cache) > self.max_recent_actions:
            self.recent_actions_cache.pop(0)
        
        # Apply reputation changes
        for entity_id, change in (reputation_changes or {}).items():
            self._update_reputation(player_id, entity_id, change, action_description)
        
        # Save to database
        if self.db_service:
            self._save_action_to_db(player_id, action)
        
        self.logger.info(f"Recorded significant action: {action_description} ({significance.value})")
        return action_id
    
    def get_recent_significant_actions(self, 
                                     player_id: str, 
                                     max_actions: int = 5,
                                     relevance_filter: bool = True) -> List[SignificantAction]:
        """
        Get player's recent significant actions.
        
        Args:
            player_id: Player identifier
            max_actions: Maximum number of actions to return
            relevance_filter: Whether to filter by relevance (time/significance)
            
        Returns:
            List of recent significant actions
        """
        # Load from database if cache is empty
        if not self.recent_actions_cache and self.db_service:
            self._load_recent_actions_from_db(player_id)
        
        actions = self.recent_actions_cache.copy()
        
        if relevance_filter:
            # Filter by relevance (recent + significant actions have priority)
            cutoff_date = datetime.utcnow() - timedelta(days=self.action_relevance_days)
            
            # Keep all recent actions or highly significant ones
            actions = [
                action for action in actions 
                if (action.timestamp >= cutoff_date or 
                    action.significance in [ActionSignificance.MAJOR, ActionSignificance.LEGENDARY])
            ]
        
        # Sort by significance and recency
        actions.sort(key=lambda a: (a.significance.value, a.timestamp), reverse=True)
        
        return actions[:max_actions]
    
    def _update_reputation(self, player_id: str, entity_id: str, change: int, reason: str):
        """Update reputation with an entity"""
        current_rep = self.get_reputation_with_entity(player_id, entity_id)
        
        # Update score and level
        new_score = current_rep.reputation_score + change
        new_level = self._score_to_level(new_score)
        
        # Update reputation entry
        cache_key = f"{player_id}_{entity_id}"
        updated_rep = ReputationEntry(
            entity_id=entity_id,
            entity_name=current_rep.entity_name,
            entity_type=current_rep.entity_type,
            reputation_level=new_level,
            reputation_score=new_score,
            last_updated=datetime.utcnow(),
            reasons=current_rep.reasons + [reason]
        )
        
        self.reputation_cache[cache_key] = updated_rep
        
        # Save to database
        if self.db_service:
            self._save_reputation_to_db(player_id, updated_rep)
        
        self.logger.info(f"Updated reputation with {entity_id}: {change:+d} -> {new_level.value}")
    
    def _score_to_level(self, score: int) -> ReputationLevel:
        """Convert numeric score to reputation level"""
        if score >= 15:
            return ReputationLevel.REVERED
        elif score >= 10:
            return ReputationLevel.RESPECTED
        elif score >= 5:
            return ReputationLevel.LIKED
        elif score >= -5:
            return ReputationLevel.NEUTRAL
        elif score >= -10:
            return ReputationLevel.DISLIKED
        elif score >= -15:
            return ReputationLevel.DESPISED
        else:
            return ReputationLevel.HATED
    
    def get_reputation_context_for_llm(self, player_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get reputation and recent actions context formatted for LLM prompts.
        
        Args:
            player_id: Player identifier
            context: Current game context
            
        Returns:
            Dictionary with reputation and actions context for LLM
        """
        # Get relevant reputations
        relevant_reps = self.get_relevant_reputations(player_id, context)
        
        # Get recent significant actions
        recent_actions = self.get_recent_significant_actions(player_id)
        
        # Format for LLM context
        reputation_summaries = []
        for rep in relevant_reps:
            if rep.entity_type == 'global':
                reputation_summaries.append(f"Global reputation: {rep.reputation_level.value}")
            else:
                reputation_summaries.append(f"{rep.entity_name}: {rep.reputation_level.value}")
        
        action_summaries = [action.get_action_summary() for action in recent_actions]
        
        return {
            'player_reputation_summary': '; '.join(reputation_summaries) if reputation_summaries else 'No notable reputation',
            'recent_significant_actions': action_summaries,
            'primary_reputation_level': relevant_reps[0].reputation_level.value if relevant_reps else 'neutral',
            'reputation_details': [
                {
                    'entity': rep.entity_name,
                    'level': rep.reputation_level.value,
                    'score': rep.reputation_score
                }
                for rep in relevant_reps
            ]
        }
    
    # Database integration methods (simplified for now)
    def _load_from_database(self):
        """Load reputation and actions from database"""
        # This would load cached data from the database
        pass
    
    def _load_reputation_from_db(self, player_id: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Load specific reputation from database"""
        # This would query the database for reputation data
        return None
    
    def _save_reputation_to_db(self, player_id: str, reputation: ReputationEntry):
        """Save reputation to database"""
        # This would save reputation data to the database
        pass
    
    def _save_action_to_db(self, player_id: str, action: SignificantAction):
        """Save action to database"""
        # This would save action data to the database
        pass
    
    def _load_recent_actions_from_db(self, player_id: str):
        """Load recent actions from database"""
        # This would load recent actions from the database
        pass