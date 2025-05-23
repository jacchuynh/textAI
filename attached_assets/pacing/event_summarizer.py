"""
Event Summarization Manager - Uses LLM to maintain concise story summaries
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json

from llm_integration.openrouter_llm import EnhancedLLMManager


class EventSummarizer:
    """
    Manages event summarization to maintain concise story history using LLM
    """
    
    def __init__(self, llm_manager: EnhancedLLMManager, db_service=None):
        """
        Initialize event summarizer.
        
        Args:
            llm_manager: LLM manager for making API calls
            db_service: Database service for persistence
        """
        self.llm_manager = llm_manager
        self.db_service = db_service
        self.logger = logging.getLogger("EventSummarizer")
        
        # Configuration
        self.summarization_config = {
            'events_per_summary': 10,           # Summarize every 10 events
            'max_event_age_days': 7,            # Don't summarize events older than 7 days
            'summary_cooldown_hours': 2,        # Min 2 hours between summaries
            'max_summary_length': 4,            # Max 4 sentences per summary
            'cost_threshold_tokens': 2000       # Only summarize if would save 2000+ tokens
        }
        
        # Track summaries
        self.current_summary = ""
        self.last_summarization_time = datetime.utcnow() - timedelta(days=1)  # Allow immediate first
        self.events_since_last_summary = []
        self.summarization_stats = {
            'total_summaries_created': 0,
            'tokens_saved_estimate': 0,
            'events_summarized': 0
        }
    
    def add_event_for_summarization(self, event_data: Dict[str, Any]):
        """
        Add an event to the queue for potential summarization.
        
        Args:
            event_data: Event data to potentially summarize
        """
        # Filter events worth summarizing
        if self._is_event_worth_summarizing(event_data):
            self.events_since_last_summary.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_data.get('event_type', 'unknown'),
                'description': self._create_event_description(event_data),
                'significance': self._rate_event_significance(event_data)
            })
            
            self.logger.debug(f"Added event for summarization: {event_data.get('event_type', 'unknown')}")
    
    async def should_create_summary(self) -> bool:
        """
        Determine if a new summary should be created.
        
        Returns:
            True if summarization should occur
        """
        # Check cooldown
        time_since_last = datetime.utcnow() - self.last_summarization_time
        if time_since_last < timedelta(hours=self.summarization_config['summary_cooldown_hours']):
            return False
        
        # Check if we have enough events
        if len(self.events_since_last_summary) < self.summarization_config['events_per_summary']:
            return False
        
        # Check if summarization would save tokens (cost-benefit analysis)
        estimated_current_tokens = self._estimate_current_event_tokens()
        if estimated_current_tokens < self.summarization_config['cost_threshold_tokens']:
            return False
        
        return True
    
    async def create_summary(self, session_id: str) -> Optional[str]:
        """
        Create a new summary of recent events.
        
        Args:
            session_id: Current session ID
            
        Returns:
            New summary string or None if failed
        """
        if not self.events_since_last_summary:
            return None
        
        try:
            # Build event log for summarization
            event_log = self._build_event_log()
            
            # Create LLM prompt for summarization
            prompt = self._build_summarization_prompt(event_log)
            
            # Use cheaper model for summarization
            model = self.llm_manager.get_optimal_model("world_query", "medium")
            
            # Call LLM for summarization
            llm_result = await self.llm_manager.call_llm_with_tracking(
                prompt=prompt,
                model=model,
                prompt_mode="event_summarization",
                temperature=0.3,  # Lower temperature for consistent summaries
                max_tokens=150    # Keep summaries concise
            )
            
            if llm_result['success']:
                new_summary = llm_result['content'].strip()
                
                # Update tracking
                self.current_summary = new_summary
                self.last_summarization_time = datetime.utcnow()
                
                # Calculate token savings
                original_tokens = self._estimate_current_event_tokens()
                summary_tokens = len(new_summary.split()) * 1.3  # Rough estimate
                tokens_saved = max(0, original_tokens - summary_tokens)
                
                # Update statistics
                self.summarization_stats['total_summaries_created'] += 1
                self.summarization_stats['tokens_saved_estimate'] += tokens_saved
                self.summarization_stats['events_summarized'] += len(self.events_since_last_summary)
                
                # Clear events queue
                self.events_since_last_summary = []
                
                # Log summarization
                if self.db_service:
                    await self._log_summarization(session_id, new_summary, tokens_saved)
                
                self.logger.info(f"Created event summary, estimated {tokens_saved:.0f} tokens saved")
                return new_summary
            else:
                self.logger.error(f"Failed to create summary: {llm_result.get('error_message', 'Unknown error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating summary: {e}")
            return None
    
    def get_current_story_context(self) -> Dict[str, Any]:
        """
        Get current story context including summary and recent events.
        
        Returns:
            Story context for LLM prompts
        """
        return {
            'story_summary': self.current_summary,
            'recent_events': self.events_since_last_summary[-5:],  # Last 5 events
            'has_summary': bool(self.current_summary),
            'events_since_summary': len(self.events_since_last_summary)
        }
    
    def _is_event_worth_summarizing(self, event_data: Dict[str, Any]) -> bool:
        """Check if event is worth including in summaries"""
        
        event_type = event_data.get('event_type', '')
        
        # Include significant game events
        significant_events = [
            'NARRATIVE_BRANCH_INITIATED',
            'BRANCH_ACTION_EXECUTED', 
            'WORLD_REACTION_ASSESSED',
            'SIGNIFICANT_ACTION_RECORDED',
            'DECISION_MADE',
            'NPC_INITIATED_DIALOGUE'
        ]
        
        if event_type in significant_events:
            return True
        
        # Include player actions with outcomes
        if event_type == 'COMMAND_EXECUTED':
            context = event_data.get('context', {})
            if context.get('result', {}).get('success', False):
                return True
        
        # Include social interactions
        if event_type in ['CONVERSATION_STARTED', 'REPUTATION_CHANGED']:
            return True
        
        return False
    
    def _create_event_description(self, event_data: Dict[str, Any]) -> str:
        """Create human-readable description of event"""
        
        event_type = event_data.get('event_type', 'unknown')
        context = event_data.get('context', {})
        actor = event_data.get('actor', 'unknown')
        
        # Create descriptions based on event type
        if event_type == 'NARRATIVE_BRANCH_INITIATED':
            branch_name = context.get('branch_name', 'unknown quest')
            return f"Player began {branch_name}"
        
        elif event_type == 'BRANCH_ACTION_EXECUTED':
            action = context.get('action', 'an action')
            result = context.get('skill_check_result', {})
            success = result.get('success', False)
            return f"Player {'successfully' if success else 'unsuccessfully'} attempted {action}"
        
        elif event_type == 'WORLD_REACTION_ASSESSED':
            target = context.get('target_entity', 'someone')
            return f"World reacted to player's interaction with {target}"
        
        elif event_type == 'NPC_INITIATED_DIALOGUE':
            npc_name = context.get('npc_name', actor)
            theme = context.get('dialogue_theme', 'conversation')
            return f"{npc_name} initiated {theme} with player"
        
        elif event_type == 'DECISION_MADE':
            priority = context.get('priority_used', 'decision')
            return f"Player made {priority.lower().replace('_', ' ')}"
        
        else:
            return f"Player {event_type.lower().replace('_', ' ')}"
    
    def _rate_event_significance(self, event_data: Dict[str, Any]) -> int:
        """Rate event significance 1-5"""
        
        event_type = event_data.get('event_type', '')
        
        # High significance events (5)
        if event_type == 'NARRATIVE_BRANCH_INITIATED':
            return 5
        
        # Medium-high significance (4)
        if event_type in ['BRANCH_ACTION_EXECUTED', 'SIGNIFICANT_ACTION_RECORDED']:
            return 4
        
        # Medium significance (3)
        if event_type in ['WORLD_REACTION_ASSESSED', 'DECISION_MADE']:
            return 3
        
        # Low-medium significance (2)
        if event_type in ['NPC_INITIATED_DIALOGUE', 'COMMAND_EXECUTED']:
            return 2
        
        # Low significance (1)
        return 1
    
    def _build_event_log(self) -> str:
        """Build formatted event log for LLM prompt"""
        
        if not self.events_since_last_summary:
            return "No recent events to summarize."
        
        # Sort events by significance and time
        sorted_events = sorted(
            self.events_since_last_summary,
            key=lambda e: (e['significance'], e['timestamp']),
            reverse=True
        )
        
        # Format events
        event_lines = []
        for event in sorted_events:
            timestamp = event['timestamp'][:16]  # YYYY-MM-DD HH:MM
            significance = "★" * event['significance']  # Visual significance indicator
            event_lines.append(f"[{timestamp}] {significance} {event['description']}")
        
        return "\n".join(event_lines)
    
    def _build_summarization_prompt(self, event_log: str) -> str:
        """Build LLM prompt for event summarization using Template 4"""
        
        prompt = f"""You are an AI assistant that summarizes game events.

Recent Event Log:
{event_log}

Previous Summary (if any): {self.current_summary if self.current_summary else "No previous summary."}

Condense the new events and integrate them with the previous summary into a concise narrative recap of what has happened. Max 3-4 sentences.

Focus on:
- Major story developments and player achievements
- Important character interactions and relationships
- Significant world events or changes
- Player's overall progress and current situation

Provide a flowing narrative summary, not a list of events."""
        
        return prompt
    
    def _estimate_current_event_tokens(self) -> int:
        """Estimate tokens used by current event descriptions"""
        
        total_text = ""
        for event in self.events_since_last_summary:
            total_text += event['description'] + " "
        
        # Rough token estimation (1.3 tokens per word)
        return len(total_text.split()) * 1.3
    
    async def _log_summarization(self, session_id: str, summary: str, tokens_saved: float):
        """Log summarization event to database"""
        if self.db_service:
            await self.db_service.save_event({
                'session_id': session_id,
                'event_type': 'EVENT_SUMMARY_CREATED',
                'actor': 'event_summarizer',
                'context': {
                    'summary': summary,
                    'events_summarized': len(self.events_since_last_summary),
                    'estimated_tokens_saved': tokens_saved,
                    'summary_length': len(summary)
                }
            })
    
    def get_summarization_statistics(self) -> Dict[str, Any]:
        """Get event summarization statistics"""
        return {
            'total_summaries_created': self.summarization_stats['total_summaries_created'],
            'total_events_summarized': self.summarization_stats['events_summarized'],
            'estimated_tokens_saved': self.summarization_stats['tokens_saved_estimate'],
            'current_summary_length': len(self.current_summary),
            'events_pending_summarization': len(self.events_since_last_summary),
            'last_summarization': self.last_summarization_time.isoformat() if self.last_summarization_time else None,
            'cost_efficiency': {
                'tokens_saved_per_summary': (
                    self.summarization_stats['tokens_saved_estimate'] / 
                    max(1, self.summarization_stats['total_summaries_created'])
                ),
                'events_per_summary': (
                    self.summarization_stats['events_summarized'] / 
                    max(1, self.summarization_stats['total_summaries_created'])
                )
            }
        }