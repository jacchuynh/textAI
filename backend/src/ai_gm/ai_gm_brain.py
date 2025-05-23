"""
AI GM Brain - Core Controller

This module provides the core orchestration logic for the AI Game Master,
integrating with the existing event system, memory management, and narrative engine.
"""

import logging
import time
from enum import Enum, auto
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Import existing components
from ..events.event_bus import GameEvent, EventType, event_bus
from ..memory.memory_manager import memory_manager, MemoryTier, MemoryType


class InputComplexity(Enum):
    """Categorizes input complexity to determine processing strategy."""
    SIMPLE_COMMAND = auto()     # Clear, direct command
    CONVERSATIONAL = auto()     # Dialog, questions, complex interaction
    AMBIGUOUS = auto()          # Unclear input
    PARSING_ERROR = auto()      # Unable to parse


class ProcessingMode(Enum):
    """Processing modes for different types of interactions."""
    MECHANICAL = auto()        # Template-based, fast responses
    NARRATIVE = auto()         # Rich storytelling, moderate LLM usage
    INTERPRETIVE = auto()      # Heavy LLM usage for complex situations
    ERROR = auto()             # Error handling mode


class AIGMBrain:
    """
    The central AI GM orchestrator that intelligently manages game narrative and responses.
    
    This class serves as the coordinator between:
    - Player input processing
    - Event system integration
    - Memory management
    - Response generation (template-based and LLM)
    """
    
    def __init__(self, 
                 game_id: str,
                 player_id: str):
        """
        Initialize the AI GM Brain.
        
        Args:
            game_id: Unique identifier for the game session
            player_id: ID of the primary player character
        """
        self.game_id = game_id
        self.player_id = player_id
        
        # Connect to existing systems
        self.event_bus = event_bus
        self.memory_manager = memory_manager
        
        # Internal state tracking
        self.current_location = None
        self.recent_events: List[GameEvent] = []
        self.active_conversations: Dict[str, Any] = {}
        self.processing_mode = ProcessingMode.MECHANICAL
        self.last_llm_interaction = None
        self.interaction_count = 0
        
        # Configuration
        self.max_recent_events = 20
        self.llm_cooldown_seconds = 5
        self.conversational_keywords = {
            'question_words': ['what', 'where', 'when', 'why', 'how', 'who', 'which'],
            'conversational_starters': ['tell me', 'explain', 'describe', 'what about', 'how about'],
            'social_actions': ['talk to', 'speak with', 'ask', 'greet', 'converse', 'chat with']
        }
        
        # Event subscriptions
        self._setup_event_listeners()
        
        # Logging
        self.logger = logging.getLogger(f"AIGMBrain_{game_id}")
        self.logger.info(f"AI GM Brain initialized for game {game_id}")
    
    def _setup_event_listeners(self):
        """Set up event listeners for relevant game events."""
        self.event_bus.subscribe(EventType.LOCATION_ENTERED, self._handle_location_change)
        self.event_bus.subscribe(EventType.NPC_INTERACTION, self._handle_npc_interaction)
        self.event_bus.subscribe(EventType.COMBAT_STARTED, self._handle_combat_event)
        self.event_bus.subscribe(EventType.COMBAT_ENDED, self._handle_combat_event)
        self.event_bus.subscribe(EventType.QUEST_STARTED, self._handle_quest_event)
        self.event_bus.subscribe(EventType.QUEST_COMPLETED, self._handle_quest_event)
    
    def process_player_input(self, input_string: str) -> Dict[str, Any]:
        """
        Main entry point for processing player input.
        
        Args:
            input_string: Raw text input from the player
            
        Returns:
            Dictionary containing response data and metadata
        """
        self.interaction_count += 1
        start_time = time.time()
        
        self.logger.debug(f"Processing input #{self.interaction_count}: '{input_string}'")
        
        # Check for OOC command
        if input_string.lower().startswith('/ooc'):
            return self._handle_ooc_command(input_string, start_time)
        
        # Analyze input complexity
        complexity = self._analyze_input_complexity(input_string)
        
        # Route to appropriate processing based on complexity
        if complexity == InputComplexity.SIMPLE_COMMAND:
            response_data = self._process_mechanical_command(input_string)
            self.processing_mode = ProcessingMode.MECHANICAL
        elif complexity == InputComplexity.CONVERSATIONAL:
            response_data = self._process_conversational_input(input_string)
            self.processing_mode = ProcessingMode.NARRATIVE
        elif complexity == InputComplexity.AMBIGUOUS:
            response_data = self._process_ambiguous_input(input_string)
            self.processing_mode = ProcessingMode.INTERPRETIVE
        else:  # PARSING_ERROR
            response_data = self._handle_parsing_error(input_string)
            self.processing_mode = ProcessingMode.ERROR
        
        # Log the interaction
        self._log_interaction(input_string, response_data)
        
        # Add processing metadata
        processing_time = time.time() - start_time
        response_data['metadata'] = {
            'processing_time': processing_time,
            'complexity': complexity.name,
            'processing_mode': self.processing_mode.name,
            'interaction_count': self.interaction_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return response_data
    
    def _analyze_input_complexity(self, input_string: str) -> InputComplexity:
        """
        Analyze complexity of player input.
        
        Args:
            input_string: Raw text input from the player
            
        Returns:
            InputComplexity enum value indicating complexity
        """
        input_lower = input_string.lower().strip()
        
        # Check for conversational patterns
        has_question = '?' in input_string or any(
            word in input_lower for word in self.conversational_keywords['question_words']
        )
        
        has_conversational = any(
            starter in input_lower for starter in self.conversational_keywords['conversational_starters']
        )
        
        has_social = any(
            action in input_lower for action in self.conversational_keywords['social_actions']
        )
        
        # Determine complexity
        if has_question or has_conversational or has_social:
            return InputComplexity.CONVERSATIONAL
        
        # Check if this looks like a simple command
        # For now we'll use a simple heuristic, but this will be replaced by the parser
        words = input_lower.split()
        if 1 <= len(words) <= 4:
            # Likely a simple command like "look", "take sword", "go north"
            return InputComplexity.SIMPLE_COMMAND
        
        # If we're not sure, consider it ambiguous
        return InputComplexity.AMBIGUOUS
    
    def _process_mechanical_command(self, input_string: str) -> Dict[str, Any]:
        """
        Process mechanical commands using templates.
        
        Args:
            input_string: Command string
            
        Returns:
            Response data
        """
        # This is a placeholder for now - will implement actual command processing later
        # In Phase 2, this will connect to the command parser
        
        # Simple direction commands
        directions = ['north', 'south', 'east', 'west', 'up', 'down']
        words = input_string.lower().split()
        
        if input_string.lower() in directions:
            return {
                'response_text': f"You move {input_string.lower()}.",
                'action_executed': True,
                'requires_llm': False,
                'command_type': 'movement'
            }
        
        if input_string.lower() == 'look' or input_string.lower() == 'look around':
            return {
                'response_text': "You look around the area. [Environment description would go here]",
                'action_executed': True,
                'requires_llm': False,
                'command_type': 'observation'
            }
        
        if words and words[0] == 'take':
            item = ' '.join(words[1:])
            return {
                'response_text': f"You take the {item}.",
                'action_executed': True,
                'requires_llm': False,
                'command_type': 'item_interaction'
            }
        
        # Default to ambiguous handling
        return self._process_ambiguous_input(input_string)
    
    def _process_conversational_input(self, input_string: str) -> Dict[str, Any]:
        """
        Process conversational input requiring narrative response.
        
        Args:
            input_string: Conversational input string
            
        Returns:
            Response data
        """
        # This is a placeholder for now - will implement LLM call in Phase 2
        
        # For now, return a template response
        response_templates = [
            "That's an interesting question. [LLM-generated response would go here]",
            "Let me think about that... [LLM-generated response would go here]",
            "I understand you're asking about that. [LLM-generated response would go here]"
        ]
        
        import random
        response = random.choice(response_templates)
        
        return {
            'response_text': response,
            'action_executed': False,
            'requires_llm': True,
            'response_type': 'narrative'
        }
    
    def _process_ambiguous_input(self, input_string: str) -> Dict[str, Any]:
        """
        Process ambiguous input that could have multiple interpretations.
        
        Args:
            input_string: Ambiguous input string
            
        Returns:
            Response data
        """
        # This is a placeholder for now
        
        return {
            'response_text': f"I'm not sure what you mean by '{input_string}'. Could you be more specific?",
            'action_executed': False,
            'requires_llm': False,
            'response_type': 'clarification_request'
        }
    
    def _handle_parsing_error(self, input_string: str) -> Dict[str, Any]:
        """
        Handle input that could not be parsed.
        
        Args:
            input_string: Unparseable input string
            
        Returns:
            Response data
        """
        return {
            'response_text': "I don't understand that command. Try something like 'look', 'go north', or 'take item'.",
            'action_executed': False,
            'requires_llm': False,
            'response_type': 'error',
            'error_type': 'parsing_error'
        }
    
    def _handle_ooc_command(self, input_string: str, start_time: float) -> Dict[str, Any]:
        """
        Handle out-of-character commands starting with /ooc.
        
        Args:
            input_string: OOC command string
            start_time: Processing start time for metrics
            
        Returns:
            Response data
        """
        # Strip the /ooc prefix and any leading/trailing whitespace
        command = input_string.lower().replace('/ooc', '', 1).strip()
        
        # Handle empty command
        if not command:
            help_text = "(OOC) Available commands: help, stats, inventory, quests, time"
            return {
                'response_text': help_text,
                'ooc_response': True,
                'requires_llm': False,
                'processing_time': time.time() - start_time
            }
        
        # Process specific OOC commands
        if command == 'help':
            help_text = """(OOC) Available commands:
- help: Show this help message
- stats: Show character statistics
- inventory: Show your inventory
- quests: Show active quests
- time: Show game time
"""
            return {
                'response_text': help_text,
                'ooc_response': True,
                'requires_llm': False,
                'processing_time': time.time() - start_time
            }
        
        if command == 'stats':
            # Placeholder for actual stats
            stats_text = "(OOC) Your stats: [Character stats would go here]"
            return {
                'response_text': stats_text,
                'ooc_response': True,
                'requires_llm': False,
                'processing_time': time.time() - start_time
            }
        
        # Default OOC response for unknown commands
        return {
            'response_text': f"(OOC) Unknown command: '{command}'. Type '/ooc help' for available commands.",
            'ooc_response': True,
            'requires_llm': False,
            'processing_time': time.time() - start_time
        }
    
    def _log_interaction(self, input_string: str, response_data: Dict[str, Any]) -> None:
        """
        Log player interaction for analysis and history.
        
        Args:
            input_string: Player input
            response_data: Generated response data
        """
        # Add to memory manager if significant
        is_significant = (
            self.processing_mode == ProcessingMode.NARRATIVE or
            response_data.get('action_executed', False) or
            'error' in response_data
        )
        
        if is_significant:
            memory_content = f"Player: {input_string}\nAI GM: {response_data.get('response_text', '')}"
            memory_type = MemoryType.PLAYER_ACTION
            
            # Determine importance
            importance = 3  # Default medium-low importance
            if self.processing_mode == ProcessingMode.NARRATIVE:
                importance = 5  # Narrative interactions are more important
            if response_data.get('action_executed', False):
                importance = 6  # Actions that change game state are important
            
            # Add to memory
            self.memory_manager.add_memory(
                type=memory_type,
                content=memory_content,
                importance=importance,
                tier=MemoryTier.SHORT_TERM,
                game_id=self.game_id
            )
    
    def _handle_location_change(self, event: GameEvent) -> None:
        """Handle location change events."""
        self.current_location = event.context.get('location_id')
        self.logger.debug(f"Location changed to {self.current_location}")
    
    def _handle_npc_interaction(self, event: GameEvent) -> None:
        """Handle NPC interaction events."""
        npc_id = event.context.get('npc_id')
        if npc_id:
            # Track active conversations
            self.active_conversations[npc_id] = {
                'started_at': datetime.utcnow(),
                'last_update': datetime.utcnow(),
                'context': event.context
            }
    
    def _handle_combat_event(self, event: GameEvent) -> None:
        """Handle combat-related events."""
        if event.type == EventType.COMBAT_STARTED:
            self.logger.info(f"Combat started with {event.context.get('opponent_id')}")
        elif event.type == EventType.COMBAT_ENDED:
            self.logger.info(f"Combat ended with result: {event.context.get('result')}")
    
    def _handle_quest_event(self, event: GameEvent) -> None:
        """Handle quest-related events."""
        quest_id = event.context.get('quest_id')
        if event.type == EventType.QUEST_STARTED:
            self.logger.info(f"Quest started: {quest_id}")
        elif event.type == EventType.QUEST_COMPLETED:
            self.logger.info(f"Quest completed: {quest_id}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the AI GM Brain's processing.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'total_interactions': self.interaction_count,
            'current_mode': self.processing_mode.name,
            'active_conversations': len(self.active_conversations),
            'current_location': self.current_location,
            'last_llm_interaction': self.last_llm_interaction.isoformat() if self.last_llm_interaction else None
        }


# Singleton instance pattern
_ai_gm_brain = None

def get_ai_gm_brain(game_id: str, player_id: str) -> AIGMBrain:
    """
    Get or create the AI GM Brain instance.
    
    Args:
        game_id: Game session ID
        player_id: Player character ID
        
    Returns:
        AIGMBrain instance
    """
    global _ai_gm_brain
    if _ai_gm_brain is None:
        _ai_gm_brain = AIGMBrain(game_id, player_id)
    return _ai_gm_brain