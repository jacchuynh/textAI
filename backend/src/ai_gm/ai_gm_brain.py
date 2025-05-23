"""
AI Game Master Brain - Integrated with Text Parsing and LLM Capabilities

This module implements the core AI Game Master controller that orchestrates
narrative experiences, manages NPCs, and provides dynamic storytelling
with advanced text parsing capabilities and LLM integration.
"""

import time
import uuid
import logging
import random
import asyncio
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Callable, Set, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import from our own modules
from ..events.event_bus import event_bus, EventType, GameEvent
from ..memory.memory_manager import memory_manager, MemoryTier, MemoryType

# These imports will be used later when we integrate these components
# For now they're commented out to avoid import errors
# from ..text_parser import parse_input, ParsedCommand, parser_engine, vocabulary_manager
# from ..llm_integration import LLMInteractionManager, LLMProvider, PromptMode


class InputComplexity(Enum):
    """Complexity levels for player input."""
    SIMPLE = auto()      # Simple commands like "look", "go north"
    MODERATE = auto()    # More complex but still straight-forward
    COMPLEX = auto()     # Complex, potentially ambiguous input
    CONVERSATIONAL = auto()  # Natural language conversation


class ProcessingMode(Enum):
    """Different modes of processing player input."""
    MECHANICAL = auto()  # Direct mechanical response (movement, etc.)
    NARRATIVE = auto()   # Narrative-focused response
    HYBRID = auto()      # A mix of mechanical and narrative
    OOC = auto()         # Out of character processing


class AIGMBrain:
    """
    Core AI Game Master Brain that coordinates all game systems.
    
    This class orchestrates the various game systems to provide a cohesive
    player experience, managing the flow of information and narrative.
    """
    
    def __init__(self, game_id: str, player_id: str):
        """
        Initialize the AI GM Brain.
        
        Args:
            game_id: ID of the game session
            player_id: ID of the player
        """
        self.game_id = game_id
        self.player_id = player_id
        self.logger = logging.getLogger(f"AIGMBrain:{game_id}")
        
        # Initialize component flags (will be set by extension modules)
        self.has_ooc_integration = False
        self.has_llm_integration = False
        self.has_combat_integration = False
        self.has_decision_logic = False
        self.has_narrative_generator = False
        
        # Component extensions will add themselves to this dictionary
        self.extensions: Dict[str, Any] = {}
        
        # Processing statistics
        self.stats = {
            "total_inputs_processed": 0,
            "mechanical_responses": 0,
            "narrative_responses": 0,
            "hybrid_responses": 0,
            "ooc_responses": 0,
            "simple_inputs": 0,
            "moderate_inputs": 0,
            "complex_inputs": 0,
            "conversational_inputs": 0,
            "avg_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        
        # Game state properties
        self.current_location = None  # Will be updated as the player moves
        
        # Subscribe to relevant events
        self._subscribe_to_events()
        
        self.logger.info(f"AI GM Brain initialized for game {game_id} and player {player_id}")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant game events."""
        event_types = [
            EventType.PLAYER_JOINED,
            EventType.PLAYER_LEFT,
            EventType.LOCATION_ENTERED,
            EventType.LOCATION_EXITED,
            EventType.NPC_INTERACTION,
            EventType.ITEM_ACQUIRED,
            EventType.COMBAT_STARTED,
            EventType.COMBAT_ENDED,
            EventType.QUEST_STARTED,
            EventType.QUEST_PROGRESSED,
            EventType.QUEST_COMPLETED,
            EventType.DOMAIN_ADVANCED
        ]
        
        for event_type in event_types:
            event_bus.subscribe(event_type, self._handle_event)
    
    def _handle_event(self, event: GameEvent):
        """
        Handle a game event.
        
        Args:
            event: Game event to handle
        """
        # Log the event
        self.logger.debug(f"Handling event: {event}")
        
        # Update game state based on the event
        if event.type == EventType.LOCATION_ENTERED:
            # Update current location when the player enters a new location
            if 'location_id' in event.context:
                self.current_location = event.context['location_id']
                self.logger.info(f"Updated current location to: {self.current_location}")
        
        # Store important events in memory
        importance = 0.5  # Default importance
        
        # Adjust importance based on event type
        if event.type in [EventType.QUEST_COMPLETED, EventType.COMBAT_ENDED, 
                         EventType.DOMAIN_ADVANCED, EventType.PLAYER_JOINED]:
            importance = 0.8
        elif event.type in [EventType.QUEST_STARTED, EventType.COMBAT_STARTED, 
                           EventType.NPC_INTERACTION]:
            importance = 0.6
        
        # Store in memory
        memory_content = {
            "event_type": event.type.name,
            "timestamp": event.timestamp.isoformat(),
            "source_id": event.source_id,
            "context": event.context
        }
        
        memory_manager.add_memory(
            memory_type=MemoryType.SYSTEM,
            content=memory_content,
            importance=importance,
            tags=[event.type.name] + event.tags
        )
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input and generate a response.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        # Log input
        self.logger.info(f"Processing input: '{input_text}'")
        
        # Check for empty input
        if not input_text or input_text.strip() == "":
            return {
                "response_text": "I didn't catch that. What would you like to do?",
                "metadata": {
                    "processing_mode": ProcessingMode.NARRATIVE.name,
                    "complexity": InputComplexity.SIMPLE.name,
                    "processing_time": 0.0
                }
            }
        
        # Check for OOC command
        if input_text.startswith("/") and self.has_ooc_integration:
            result = self.extensions["ooc_integration"].process_command(input_text)
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(ProcessingMode.OOC, InputComplexity.SIMPLE, processing_time)
            
            return {
                "response_text": result["response"],
                "metadata": {
                    "processing_mode": ProcessingMode.OOC.name,
                    "complexity": InputComplexity.SIMPLE.name,
                    "processing_time": processing_time,
                    "ooc_response": True,
                    "ooc_command": result.get("command", "unknown")
                }
            }
        
        # Determine input complexity
        complexity = self._determine_input_complexity(input_text)
        
        # Determine processing mode
        processing_mode = self._determine_processing_mode(input_text, complexity)
        
        # Generate response based on processing mode
        response = self._generate_response(input_text, processing_mode, complexity)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update statistics
        self._update_stats(processing_mode, complexity, processing_time)
        
        # Prepare the result
        result = {
            "response_text": response,
            "metadata": {
                "processing_mode": processing_mode.name,
                "complexity": complexity.name,
                "processing_time": processing_time
            }
        }
        
        return result
    
    def _determine_input_complexity(self, input_text: str) -> InputComplexity:
        """
        Determine the complexity of the player's input.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Complexity level of the input
        """
        text = input_text.lower().strip()
        
        # Check for simple commands
        simple_commands = ["look", "go", "take", "drop", "use", "attack", "help", "inventory"]
        if any(text.startswith(cmd) for cmd in simple_commands) and len(text.split()) <= 3:
            return InputComplexity.SIMPLE
        
        # Check for moderate complexity
        if len(text.split()) <= 8 and "?" not in text:
            return InputComplexity.MODERATE
        
        # Check for conversational input
        conversational_indicators = ["?", "hello", "hi", "thanks", "thank you", "please"]
        if any(indicator in text for indicator in conversational_indicators):
            return InputComplexity.CONVERSATIONAL
        
        # Default to complex
        return InputComplexity.COMPLEX
    
    def _determine_processing_mode(self, input_text: str, complexity: InputComplexity) -> ProcessingMode:
        """
        Determine the appropriate processing mode for the input.
        
        Args:
            input_text: Text input from the player
            complexity: Complexity level of the input
            
        Returns:
            Processing mode to use
        """
        text = input_text.lower().strip()
        
        # If OOC, already handled in process_player_input
        if text.startswith("/"):
            return ProcessingMode.OOC
        
        # Check for mechanical commands
        mechanical_commands = ["go", "take", "drop", "use", "attack", "inventory", "equip"]
        if any(text.startswith(cmd) for cmd in mechanical_commands):
            return ProcessingMode.MECHANICAL
        
        # Check for narrative-focused input
        narrative_indicators = ["tell me about", "describe", "what is", "who is", "?"]
        if any(indicator in text for indicator in narrative_indicators):
            return ProcessingMode.NARRATIVE
        
        # Default based on complexity
        if complexity == InputComplexity.SIMPLE:
            return ProcessingMode.MECHANICAL
        elif complexity == InputComplexity.CONVERSATIONAL:
            return ProcessingMode.NARRATIVE
        else:
            return ProcessingMode.HYBRID
    
    def _generate_response(self, input_text: str, mode: ProcessingMode, 
                          complexity: InputComplexity) -> str:
        """
        Generate a response based on the input and processing mode.
        
        Args:
            input_text: Text input from the player
            mode: Processing mode to use
            complexity: Complexity of the input
            
        Returns:
            Response text
        """
        # Handle based on processing mode
        if mode == ProcessingMode.MECHANICAL:
            return self._handle_mechanical_input(input_text)
        elif mode == ProcessingMode.NARRATIVE:
            return self._handle_narrative_input(input_text)
        elif mode == ProcessingMode.HYBRID:
            return self._handle_hybrid_input(input_text)
        else:
            return "I'm not sure how to respond to that."
    
    def _handle_mechanical_input(self, input_text: str) -> str:
        """
        Handle mechanical input like movement, inventory, etc.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Response text
        """
        text = input_text.lower().strip()
        
        # Basic mechanical commands
        if text == "look":
            return "You look around and see the area."
        elif text.startswith("go "):
            direction = text[3:].strip()
            return f"You move {direction}."
        elif text == "inventory":
            return "You check your inventory."
        elif text.startswith("take "):
            item = text[5:].strip()
            return f"You take the {item}."
        elif text.startswith("drop "):
            item = text[5:].strip()
            return f"You drop the {item}."
        elif text.startswith("use "):
            item = text[4:].strip()
            return f"You use the {item}."
        elif text.startswith("attack "):
            target = text[7:].strip()
            
            # Use combat integration if available
            if self.has_combat_integration:
                return self.extensions["combat_integration"].initiate_combat(target)
            
            return f"You attack the {target}."
        else:
            return "I'm not sure how to do that."
    
    def _handle_narrative_input(self, input_text: str) -> str:
        """
        Handle narrative-focused input.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Response text
        """
        # Use narrative generator if available
        if self.has_narrative_generator:
            return self.extensions["narrative_generator"].generate_response(input_text)
        
        # Basic fallback responses
        text = input_text.lower().strip()
        
        if "describe" in text:
            return "You see a detailed scene before you."
        elif text.endswith("?"):
            return "That's an interesting question. Let me think about it."
        elif "hello" in text or "hi" in text:
            return "Greetings, adventurer. How may I assist you on your journey?"
        else:
            return "You ponder the situation before you."
    
    def _handle_hybrid_input(self, input_text: str) -> str:
        """
        Handle input that requires both mechanical and narrative processing.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Response text
        """
        # Here we'd implement a more sophisticated parsing and response system
        # For now, we'll provide a basic implementation
        
        # Use decision logic if available
        if self.has_decision_logic:
            context = {
                "input": input_text,
                "recent_memory": self._get_recent_memory()
            }
            return self.extensions["decision_logic"].make_response_decision(context)
        
        # Simple fallback combining mechanical and narrative
        mechanical = self._handle_mechanical_input(input_text)
        narrative = "You consider your next move carefully."
        
        return f"{mechanical} {narrative}"
    
    def _get_recent_memory(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent memories to provide context.
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory dictionaries
        """
        memories = memory_manager.find_memories(
            include_tiers={MemoryTier.WORKING},
            limit=limit
        )
        
        return [memory.content for memory in memories]
    
    def _update_stats(self, mode: ProcessingMode, complexity: InputComplexity, processing_time: float):
        """
        Update processing statistics.
        
        Args:
            mode: Processing mode used
            complexity: Input complexity
            processing_time: Time taken to process
        """
        self.stats["total_inputs_processed"] += 1
        
        # Update mode stats
        if mode == ProcessingMode.MECHANICAL:
            self.stats["mechanical_responses"] += 1
        elif mode == ProcessingMode.NARRATIVE:
            self.stats["narrative_responses"] += 1
        elif mode == ProcessingMode.HYBRID:
            self.stats["hybrid_responses"] += 1
        elif mode == ProcessingMode.OOC:
            self.stats["ooc_responses"] += 1
        
        # Update complexity stats
        if complexity == InputComplexity.SIMPLE:
            self.stats["simple_inputs"] += 1
        elif complexity == InputComplexity.MODERATE:
            self.stats["moderate_inputs"] += 1
        elif complexity == InputComplexity.COMPLEX:
            self.stats["complex_inputs"] += 1
        elif complexity == InputComplexity.CONVERSATIONAL:
            self.stats["conversational_inputs"] += 1
        
        # Update timing stats
        self.stats["total_processing_time"] += processing_time
        self.stats["avg_processing_time"] = (
            self.stats["total_processing_time"] / self.stats["total_inputs_processed"]
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Dictionary of statistics
        """
        return self.stats
    
    def register_extension(self, name: str, extension: Any) -> None:
        """
        Register an extension component.
        
        Args:
            name: Name of the extension
            extension: Extension object
        """
        self.extensions[name] = extension
        self.logger.info(f"Registered extension: {name}")
        
        # Set the appropriate flag
        if name == "ooc_integration":
            self.has_ooc_integration = True
        elif name == "llm_integration":
            self.has_llm_integration = True
        elif name == "combat_integration":
            self.has_combat_integration = True
        elif name == "decision_logic":
            self.has_decision_logic = True
        elif name == "narrative_generator":
            self.has_narrative_generator = True


def get_ai_gm_brain(game_id: str, player_id: str) -> AIGMBrain:
    """
    Get an AI GM Brain instance for the specified game and player.
    
    Args:
        game_id: ID of the game session
        player_id: ID of the player
        
    Returns:
        AIGMBrain instance
    """
    return AIGMBrain(game_id, player_id)