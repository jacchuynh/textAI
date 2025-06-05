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
try:
    from ..events.event_bus import event_bus, EventType, GameEvent
    from ..memory.memory_manager import memory_manager, MemoryTier, MemoryType
    from ..text_parser import parse_input, ParsedCommand, parser_engine, vocabulary_manager, object_resolver
except (ImportError, ValueError):
    try:
        from events.event_bus import event_bus, EventType, GameEvent
        from memory.memory_manager import memory_manager, MemoryTier, MemoryType
        from text_parser import parse_input, ParsedCommand, parser_engine, vocabulary_manager, object_resolver
    except ImportError:
        try:
            from backend.src.events.event_bus import event_bus, EventType, GameEvent
            from backend.src.memory.memory_manager import memory_manager, MemoryTier, MemoryType
            from backend.src.text_parser import parse_input, ParsedCommand, parser_engine, vocabulary_manager, object_resolver
        except ImportError:
            # Create stub objects if imports fail
            import logging
            logging.warning("Failed to import required modules, using stubs")
            from enum import Enum, auto
            from dataclasses import dataclass
            from typing import Dict, Any, List, Set, Optional, Callable
            from datetime import datetime
            
            # Create stub event system
            class EventType(Enum):
                PLAYER_JOINED = auto()
                PLAYER_LEFT = auto()
                LOCATION_ENTERED = auto()
                LOCATION_EXITED = auto()
                NPC_INTERACTION = auto()
                ITEM_ACQUIRED = auto()
                COMBAT_STARTED = auto()
                COMBAT_ENDED = auto()
                QUEST_STARTED = auto()
                QUEST_PROGRESSED = auto()
                QUEST_COMPLETED = auto()
                DOMAIN_ADVANCED = auto()
            
            @dataclass
            class GameEvent:
                type: EventType
                timestamp: datetime
                source_id: str
                context: Dict[str, Any]
                tags: List[str] = None
                
                def __post_init__(self):
                    if self.tags is None:
                        self.tags = []
            
            class EventBus:
                def __init__(self):
                    self.subscribers = {et: set() for et in EventType}
                
                def subscribe(self, event_type, callback):
                    self.subscribers[event_type].add(callback)
                
                def unsubscribe(self, event_type, callback):
                    if callback in self.subscribers[event_type]:
                        self.subscribers[event_type].remove(callback)
                
                def publish(self, event):
                    for callback in self.subscribers[event.type]:
                        try:
                            callback(event)
                        except Exception as e:
                            print(f"Error in event handler: {e}")
            
            event_bus = EventBus()
            
            # Create stub memory system
            class MemoryTier(Enum):
                SHORT_TERM = "short_term"
                MEDIUM_TERM = "medium_term"
                LONG_TERM = "long_term"
            
            class MemoryType(Enum):
                NARRATIVE = "narrative"
                MECHANICAL = "mechanical"
                PLAYER = "player"
                NPC = "npc"
                WORLD = "world"
                SYSTEM = "system"
            
            class MemoryManager:
                def __init__(self):
                    self.memories = {}
                
                def add_memory(self, memory_type, content, importance=0.5, tags=None, tier=None):
                    memory_id = f"{memory_type.value}_{datetime.utcnow().timestamp()}"
                    return memory_id
                
                def get_memory(self, memory_id):
                    return None
                
                def query_memories(self, memory_type=None, tags=None, min_importance=0.0, limit=10, sort_by_importance=True):
                    return []
            
            memory_manager = MemoryManager()
            
            # Create stub parser components
            @dataclass
            class ParsedCommand:
                action: str
                direct_object: Optional[str] = None
                indirect_object: Optional[str] = None
                modifiers: Dict[str, Any] = None
                original_input: str = ""
                confidence: float = 1.0
                alternative_parses: List[Dict[str, Any]] = None
            
            def parse_input(input_text: str) -> ParsedCommand:
                parts = input_text.strip().lower().split(maxsplit=1)
                action = parts[0] if parts else ""
                direct_object = parts[1] if len(parts) > 1 else None
                return ParsedCommand(
                    action=action,
                    direct_object=direct_object,
                    original_input=input_text
                )
            
            parser_engine = parse_input
            
            class VocabularyManager:
                def __init__(self):
                    self.verb_map = {}
                
                def is_verb(self, word: str) -> bool:
                    return False
                
                def get_canonical_verb(self, word: str) -> str:
                    return word
            
            vocabulary_manager = VocabularyManager()
            
            class ObjectResolver:
                def __init__(self):
                    pass
                
                def resolve_object(self, object_reference: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                    return []
                
                def needs_disambiguation(self, matches: List[Dict[str, Any]]) -> bool:
                    return False
            
            object_resolver = ObjectResolver()
# LLM integration will be added later
# from ..llm_integration import LLMInteractionManager, LLMProvider, PromptMode


class InputComplexity(Enum):
    """Categorizes input complexity to determine processing strategy."""
    SIMPLE_COMMAND = auto()      # Clear, direct command (look, go north)
    MODERATE = auto()           # More complex but still straight-forward
    COMPLEX = auto()            # Complex, potentially ambiguous input
    CONVERSATIONAL = auto()     # Natural language conversation
    DISAMBIGUATION = auto()     # Needs player to choose between options
    PARSING_ERROR = auto()      # Parser couldn't understand input


class ProcessingMode(Enum):
    """Processing modes for different types of interactions."""
    MECHANICAL = auto()     # Direct mechanical response (movement, etc.)
    NARRATIVE = auto()      # Narrative-focused response
    HYBRID = auto()         # A mix of mechanical and narrative
    OOC = auto()            # Out of character processing
    INTERPRETIVE = auto()   # Heavy processing for complex situations
    DISAMBIGUATION = auto() # Handling disambiguation between options


class AIGMBrain:
    """
    Core AI Game Master Brain that coordinates all game systems.
    
    This class orchestrates the various game systems to provide a cohesive
    player experience, managing the flow of information and narrative with
    text parsing, LLM integration, and sophisticated response generation.
    """
    
    def __init__(self, game_id: str, player_id: str, llm_client=None):
        """
        Initialize the AI GM Brain with advanced features.
        
        Args:
            game_id: ID of the game session
            player_id: ID of the player
            llm_client: LLM client for complex narrative generation (optional)
        """
        self.game_id = game_id
        self.player_id = player_id
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"AIGMBrain:{game_id}")
        
        # Initialize component flags (will be set by extension modules)
        self.has_ooc_integration = False
        self.has_llm_integration = False
        self.has_combat_integration = False
        self.has_decision_logic = False
        self.has_narrative_generator = False
        self.has_text_parser = False  # Will be set when text parser is integrated
        
        # Component extensions will add themselves to this dictionary
        self.extensions: Dict[str, Any] = {}
        
        # State tracking for disambiguation and conversations
        self.pending_disambiguation = None
        self.conversation_context = []
        self.last_input_time = datetime.now()
        
        # Processing statistics
        self.stats = {
            "total_inputs_processed": 0,
            "mechanical_responses": 0,
            "narrative_responses": 0,
            "hybrid_responses": 0,
            "ooc_responses": 0,
            "interpretive_responses": 0,
            "disambiguation_responses": 0,
            "simple_inputs": 0,
            "moderate_inputs": 0,
            "complex_inputs": 0,
            "conversational_inputs": 0,
            "disambiguation_inputs": 0,
            "parsing_error_inputs": 0,
            "avg_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        
        # Game state properties
        self.current_location = None  # Will be updated as the player moves
        self.recent_events = []       # Keep track of recent events
        self.max_recent_events = 20   # Maximum number of events to track
        self.active_conversations = {}  # Track active NPC conversations
        self.last_action_time = datetime.utcnow()
        self.session_start_time = self.last_action_time
        
        # Disambiguation state
        self.pending_disambiguation = None
        self.last_llm_interaction = None
        self.llm_cooldown_seconds = 5
        
        # Initialize text parser components
        self.parser_engine = parser_engine
        self.vocabulary = vocabulary_manager
        self.object_resolver = object_resolver
        self.game_context = {"player_id": player_id, "game_id": game_id}
        
        # Conversational analysis configuration
        self.conversational_keywords = {
            'question_words': ['what', 'where', 'when', 'why', 'how', 'who'],
            'conversational_starters': ['tell me', 'explain', 'describe', 'what about'],
            'social_actions': ['talk to', 'speak with', 'ask', 'greet', 'converse']
        }
        
        # Subscribe to relevant events
        self._subscribe_to_events()
        
        self.logger.info(f"Enhanced AI GM Brain initialized for game {game_id} and player {player_id}")
    
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
                    "complexity": InputComplexity.SIMPLE_COMMAND.name,
                    "processing_time": 0.0
                }
            }
        
        # Check for OOC command
        if input_text.startswith("/") and self.has_ooc_integration:
            result = self.extensions["ooc_integration"].process_command(input_text)
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(ProcessingMode.OOC, InputComplexity.SIMPLE_COMMAND, processing_time)
            
            return {
                "response_text": result["response"],
                "metadata": {
                    "processing_mode": ProcessingMode.OOC.name,
                    "complexity": InputComplexity.SIMPLE_COMMAND.name,
                    "processing_time": processing_time,
                    "ooc_response": True,
                    "ooc_command": result.get("command", "unknown")
                }
            }
        
        # Check if we have a pending disambiguation and this is a response to it
        if self.pending_disambiguation and self.pending_disambiguation.get("options"):
            # Handle disambiguation response
            response, processing_mode, complexity = self._handle_disambiguation_response(input_text)
        else:
            # Normal processing path
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
        Determine the complexity of the player's input using the text parser.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Complexity level of the input
        """
        text = input_text.lower().strip()
        
        # Try to parse with the text parser
        command = parse_input(input_text)
        
        # If parser was successful with high confidence, it's a simple command
        if command and command.confidence > 0.8:
            self.logger.debug(f"Input classified as SIMPLE_COMMAND: {command.action}")
            return InputComplexity.SIMPLE_COMMAND
        
        # Check for disambiguation potential
        # First update game context to ensure relevant information is available
        self._update_game_context()
        # Get disambiguation candidates 
        # For now use a simple approach to avoid import issues
        candidates = []
        try:
            # Try to use existing method from ObjectResolver
            if hasattr(self.object_resolver, 'find_disambiguation_candidates'):
                candidates = self.object_resolver.find_disambiguation_candidates(input_text, self.game_context)
        except Exception as e:
            self.logger.error(f"Error finding disambiguation candidates: {e}")
            candidates = []
        if candidates and len(candidates) > 0:
            self.logger.debug(f"Input needs DISAMBIGUATION with {len(candidates)} options")
            return InputComplexity.DISAMBIGUATION
            
        # Check for conversational patterns
        if self._is_conversational(text):
            self.logger.debug("Input classified as CONVERSATIONAL")
            return InputComplexity.CONVERSATIONAL
            
        # Check for moderate complexity
        if len(text.split()) <= 8 and "?" not in text:
            self.logger.debug("Input classified as MODERATE complexity")
            return InputComplexity.MODERATE
            
        # If still can't classify well, it's complex
        self.logger.debug("Input classified as COMPLEX")
        return InputComplexity.COMPLEX
        
    def _is_conversational(self, input_text: str) -> bool:
        """
        Determine if input is conversational in nature.
        
        Args:
            input_text: Raw text input from the player
            
        Returns:
            True if input appears to be conversational
        """
        text = input_text.lower()
        
        # Check for question words at start
        for word in self.conversational_keywords['question_words']:
            if text.startswith(word + ' '):
                return True
                
        # Check for conversational starters
        for phrase in self.conversational_keywords['conversational_starters']:
            if phrase in text:
                return True
                
        # Check for social actions
        for action in self.conversational_keywords['social_actions']:
            if action in text:
                return True
                
        # Check for common conversational indicators
        conversational_indicators = ["?", "hello", "hi", "thanks", "thank you", "please"]
        if any(indicator in text for indicator in conversational_indicators):
            return True
                
        # Check for lengthy input (likely conversational)
        if len(text.split()) > 6:
            # More complex input that isn't a simple command
            return True
            
        return False
        
    def _update_game_context(self):
        """Update the game context with current state for text parser."""
        # This provides context to the parser for better understanding
        # Using dictionary comprehension to avoid issue with update method
        context_updates = {
            "current_location": self.current_location,
            "timestamp": datetime.utcnow().isoformat()
            # Add more context as needed, like nearby NPCs, visible items, etc.
        }
        
        for key, value in context_updates.items():
            self.game_context[key] = value
    
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
        if complexity == InputComplexity.SIMPLE_COMMAND:
            return ProcessingMode.MECHANICAL
        elif complexity == InputComplexity.CONVERSATIONAL:
            return ProcessingMode.NARRATIVE
        elif complexity == InputComplexity.DISAMBIGUATION:
            return ProcessingMode.DISAMBIGUATION
        elif complexity == InputComplexity.PARSING_ERROR:
            return ProcessingMode.INTERPRETIVE
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
        elif mode == ProcessingMode.INTERPRETIVE:
            return self._handle_interpretive_input(input_text)
        elif mode == ProcessingMode.DISAMBIGUATION:
            return self._handle_disambiguation_request(input_text)
        elif mode == ProcessingMode.OOC:
            # Should be handled earlier, but just in case
            if self.has_ooc_integration:
                return self.extensions["ooc_integration"].process_command(input_text)["response"]
            else:
                return "OOC commands are not supported."
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
    
    def _handle_interpretive_input(self, input_text: str) -> str:
        """
        Handle complex input that requires interpretive processing.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Response text
        """
        # If LLM integration is available, use it
        if self.has_llm_integration:
            try:
                return self.extensions["llm_integration"].process_complex_input(input_text)
            except Exception as e:
                self.logger.error(f"Error in LLM processing: {e}")
                
        # Use command suggestions if available
        suggestions = self._get_command_suggestions(input_text)
        
        if suggestions:
            return f"I'm not sure how to interpret that. Did you mean: {', '.join(suggestions)}?"
        
        # Fallback response
        return "I don't understand that command. Try something more specific."
        
    def _handle_disambiguation_request(self, input_text: str) -> str:
        """
        Handle disambiguation for ambiguous input using the text parser.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            Response text with disambiguation options
        """
        # Use the same approach to get disambiguation candidates
        candidates = []
        try:
            # Try to use the method from ObjectResolver
            if hasattr(self.object_resolver, 'find_disambiguation_candidates'):
                candidates = self.object_resolver.find_disambiguation_candidates(input_text, self.game_context)
        except Exception as e:
            self.logger.error(f"Error finding disambiguation candidates: {e}")
            candidates = []
        
        if not candidates or len(candidates) == 0:
            # Fall back to basic suggestions if the text parser couldn't find candidates
            options = self._generate_disambiguation_options(input_text)
        else:
            # Convert to the format expected by the rest of the system
            options = []
            for candidate in candidates[:5]:  # Limit to top 5
                option = {
                    "text": candidate["match"],
                    "confidence": candidate["confidence"],
                    "action": candidate.get("action", "examine"),
                    "object_id": candidate.get("id", ""),
                    "object_type": candidate.get("type", "")
                }
                options.append(option)
                
        # Store disambiguation state
        self.pending_disambiguation = {
            "options": options,
            "original_input": input_text
        }
            
        options = self.pending_disambiguation.get("options", [])
        
        if not options:
            return "I couldn't determine what you meant. Please try again with a more specific command."
            
        # Format disambiguation options
        response_lines = ["I'm not sure what you meant. Could you be more specific?"]
        
        for i, option in enumerate(options):
            response_lines.append(f"{i+1}. {option['description']}")
            
        response_lines.append("Please choose an option by number, or type 'cancel' to try something else.")
        
        return "\n".join(response_lines)
        
    def _generate_disambiguation_options(self, input_text: str) -> List[Dict[str, Any]]:
        """
        Generate disambiguation options for ambiguous input.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            List of disambiguation options
        """
        # Ensure context is up-to-date
        self._update_game_context()
        
        # Make sure we have a cleaned input
        input_text = input_text.strip().lower()
        words = input_text.split()
        options = []
        
        # First, try to use the text parser to find candidates
        try:
            # Try to use object resolver to find candidates
            candidates = []
            if isinstance(self.object_resolver, object) and hasattr(self.object_resolver, 'find_disambiguation_candidates'):
                candidates = self.object_resolver.find_disambiguation_candidates(input_text, self.game_context)
            elif hasattr(object_resolver, 'find_disambiguation_candidates'):
                candidates = object_resolver.find_disambiguation_candidates(input_text, self.game_context)
                
            # Convert candidates to options
            for i, candidate in enumerate(candidates[:5]):  # Limit to top 5
                action = candidate.get("action", "examine")
                target = candidate.get("match", "")
                object_type = candidate.get("type", "item")
                
                # Format description based on object type and action
                if object_type == "character" and action == "talk":
                    description = f"Talk to {target}"
                elif object_type == "location" and action == "go":
                    description = f"Go to {target}"
                else:
                    description = f"{action.capitalize()} the {target}"
                
                option = {
                    "id": i,
                    "description": description,
                    "action": action,
                    "target": target
                }
                options.append(option)
                
        except Exception as e:
            self.logger.error(f"Error generating disambiguation options from text parser: {e}")
        
        # If we didn't get candidates from the text parser, use our fallback logic
        if not options:
            # Analyze input for potential action and target
            action_words = {
                "go": ["go", "move", "travel", "walk", "run"],
                "look": ["look", "examine", "inspect", "check"],
                "take": ["take", "grab", "pick", "get"],
                "talk": ["talk", "speak", "chat", "ask", "tell"],
                "use": ["use", "activate", "operate"]
            }
            
            # Identify likely action from keywords
            detected_action = None
            for action, keywords in action_words.items():
                if any(keyword in words for keyword in keywords):
                    detected_action = action
                    break
            
            # Default to examine if no action detected
            if not detected_action:
                detected_action = "examine"
                
            # Extract potential target by removing action words and common articles
            skip_words = []
            for keywords in action_words.values():
                skip_words.extend(keywords)
            skip_words.extend(["the", "a", "an", "at", "to", "with"])
            
            potential_target = " ".join([w for w in words if w not in skip_words])
            
            if not potential_target:
                potential_target = input_text
                
            # Generate action-specific options
            if detected_action == "go":
                directions = ["north", "south", "east", "west", "up", "down"]
                # If directions are mentioned, prioritize them
                direction_options = []
                for direction in directions:
                    if direction in words:
                        direction_options.append({
                            "id": len(direction_options),
                            "description": f"Go {direction}",
                            "action": "go",
                            "target": direction
                        })
                
                if direction_options:
                    options = direction_options
                else:
                    # Suggest common directions
                    for i, direction in enumerate(directions):
                        options.append({
                            "id": i,
                            "description": f"Go {direction}",
                            "action": "go",
                            "target": direction
                        })
                    
                    # Add potential target if provided
                    if potential_target and potential_target not in ["go", ""]:
                        options.append({
                            "id": len(options),
                            "description": f"Go to {potential_target}",
                            "action": "go",
                            "target": potential_target
                        })
                        
            elif detected_action == "look" or detected_action == "examine":
                # First option is to look at the specific target
                if potential_target and potential_target not in ["look", "examine", ""]:
                    options.append({
                        "id": 0,
                        "description": f"Examine the {potential_target}",
                        "action": "examine",
                        "target": potential_target
                    })
                
                # Add general look around option
                options.append({
                    "id": len(options),
                    "description": "Look around the area",
                    "action": "look",
                    "target": "around"
                })
                
                # Add inventory check option
                options.append({
                    "id": len(options),
                    "description": "Check your inventory",
                    "action": "inventory",
                    "target": "self"
                })
                
            elif detected_action == "take":
                if potential_target and potential_target not in ["take", ""]:
                    options.append({
                        "id": 0,
                        "description": f"Take the {potential_target}",
                        "action": "take",
                        "target": potential_target
                    })
                    
                    # Also suggest examining it
                    options.append({
                        "id": 1,
                        "description": f"Examine the {potential_target} first",
                        "action": "examine",
                        "target": potential_target
                    })
                else:
                    options.append({
                        "id": 0,
                        "description": "Take an item",
                        "action": "take",
                        "target": "item"
                    })
                    
            elif detected_action == "talk":
                if potential_target and potential_target not in ["talk", ""]:
                    options.append({
                        "id": 0,
                        "description": f"Talk to {potential_target}",
                        "action": "talk",
                        "target": potential_target
                    })
                    
                    # Also suggest examining them
                    options.append({
                        "id": 1,
                        "description": f"Examine {potential_target}",
                        "action": "examine",
                        "target": potential_target
                    })
                else:
                    options.append({
                        "id": 0,
                        "description": "Talk to someone nearby",
                        "action": "talk",
                        "target": "npc"
                    })
                    
            elif detected_action == "use":
                if potential_target and potential_target not in ["use", ""]:
                    options.append({
                        "id": 0,
                        "description": f"Use the {potential_target}",
                        "action": "use",
                        "target": potential_target
                    })
                    
                    # Also suggest examining it
                    options.append({
                        "id": 1,
                        "description": f"Examine the {potential_target}",
                        "action": "examine",
                        "target": potential_target
                    })
                else:
                    options.append({
                        "id": 0,
                        "description": "Use an item",
                        "action": "use",
                        "target": "item"
                    })
            
            # If we still don't have options, provide some generic ones
            if not options:
                options = [
                    {
                        "id": "help",
                        "description": "Show help information",
                        "action": "help",
                        "target": None
                    },
                    {
                        "id": "look_around",
                        "description": "Look around the area",
                        "action": "look",
                        "target": "around"
                    },
                    {
                        "id": "inventory",
                        "description": "Check your inventory",
                        "action": "inventory",
                        "target": "self"
                    }
                ]
        
        return options
        
    def _get_command_suggestions(self, input_text: str) -> List[str]:
        """
        Get command suggestions for failed parsing.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            List of command suggestions
        """
        # Update context for better suggestions
        self._update_game_context()
        
        # Clean and prepare input
        input_text = input_text.strip().lower()
        words = input_text.split()
        suggestions = []
        
        # Try to use the parser for suggestions if available
        try:
            # Check if the parser_engine instance has a get_suggestions method
            if isinstance(self.parser_engine, object) and hasattr(self.parser_engine, 'get_suggestions'):
                parser_suggestions = self.parser_engine.get_suggestions(input_text)
                if parser_suggestions and len(parser_suggestions) > 0:
                    suggestions.extend(parser_suggestions)
            # Or try the module function if available
            elif hasattr(parser_engine, 'get_suggestions'):
                parser_suggestions = parser_engine.get_suggestions(input_text)
                if parser_suggestions and len(parser_suggestions) > 0:
                    suggestions.extend(parser_suggestions)
        except Exception as e:
            self.logger.error(f"Error getting suggestions from parser engine: {e}")
        
        # If we didn't get suggestions from the parser, use our smart analysis
        if not suggestions:
            # Common command patterns with examples
            command_patterns = {
                "look": ["look around", "examine item", "look at target", "inspect object"],
                "movement": ["go north", "move to location", "enter building", "climb object"],
                "interaction": ["take item", "use item", "open container", "push object", "pull lever"],
                "social": ["talk to npc", "ask about topic", "tell npc about topic"],
                "inventory": ["inventory", "check items", "equip item", "unequip item"],
                "combat": ["attack target", "defend", "cast spell", "use skill on target"],
                "meta": ["help", "stats", "status", "quit", "save"]
            }
            
            # Analyze input for potential intentions
            potential_actions = []
            
            # Check for partially typed commands
            for category, patterns in command_patterns.items():
                for pattern in patterns:
                    # Extract command word (first word in pattern)
                    command_word = pattern.split()[0]
                    
                    # Check if any word in input starts with the command word
                    for word in words:
                        if word.startswith(command_word[:min(len(word), len(command_word))]) or \
                           command_word.startswith(word[:min(len(word), len(command_word))]):
                            # Word partially matches command
                            potential_actions.append(pattern)
                            break
            
            # Add the most relevant potential actions to suggestions
            suggestions.extend(potential_actions[:4])
            
            # Extract potential targets from input
            potential_targets = [word for word in words if len(word) > 3 and 
                                word not in ["look", "examine", "inspect", "around", "help",
                                            "take", "get", "drop", "use", "open", "close",
                                            "talk", "speak", "attack", "move", "go", "enter"]]
            
            # Generate targeted suggestions if we found potential targets
            if potential_targets and len(suggestions) < 5:
                target = potential_targets[0]  # Use the first potential target
                targeted_suggestions = [
                    f"examine the {target}",
                    f"take the {target}",
                    f"use the {target}"
                ]
                suggestions.extend(targeted_suggestions)
                
            # Ensure we always have some default suggestions for common actions
            if len(suggestions) < 3:
                default_suggestions = ["look around", "inventory", "help", "status"]
                for suggestion in default_suggestions:
                    if suggestion not in suggestions:
                        suggestions.append(suggestion)
        
        # Remove duplicates and limit to a reasonable number
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
                
        return unique_suggestions[:3]  # Limit to top 3 suggestions
        
    def _handle_disambiguation_response(self, input_text: str) -> Tuple[str, ProcessingMode, InputComplexity]:
        """
        Handle player response to a disambiguation request.
        
        Args:
            input_text: Player's response to disambiguation
            
        Returns:
            Tuple of (response_text, processing_mode, complexity)
        """
        input_text = input_text.strip().lower()
        
        # Make sure we have a valid pending_disambiguation
        if not self.pending_disambiguation:
            return "I'm not sure what you're referring to. Could you be more specific?", ProcessingMode.NARRATIVE, InputComplexity.MODERATE
            
        options = self.pending_disambiguation.get("options", [])
        
        # Handle cancel request
        if input_text == "cancel":
            response = "Okay, let's try something else."
            self.pending_disambiguation = None
            return response, ProcessingMode.NARRATIVE, InputComplexity.SIMPLE_COMMAND
        
        # Try to parse as a number
        try:
            choice_num = int(input_text)
            if 1 <= choice_num <= len(options):
                # Valid option selected
                selected_option = options[choice_num - 1]
                self.logger.info(f"Disambiguation: selected option {choice_num}: {selected_option['description']}")
                
                # Clear disambiguation state
                original_input = self.pending_disambiguation.get("original_input", "")
                self.pending_disambiguation = None
                
                # Generate response based on the selected option
                if selected_option.get("action") == "go":
                    direction = selected_option.get("target", "")
                    response = f"You move {direction}."
                    return response, ProcessingMode.MECHANICAL, InputComplexity.SIMPLE_COMMAND
                    
                elif selected_option.get("action") == "look":
                    target = selected_option.get("target")
                    if target:
                        response = f"You examine the {target} closely."
                    else:
                        response = "You look around and observe your surroundings."
                    return response, ProcessingMode.NARRATIVE, InputComplexity.SIMPLE_COMMAND
                    
                elif selected_option.get("action") == "help":
                    response = "Available commands: look, go [direction], take [item], use [item], inventory, help"
                    return response, ProcessingMode.OOC, InputComplexity.SIMPLE_COMMAND
                    
                elif selected_option.get("action") == "inventory":
                    response = "You check your inventory."
                    return response, ProcessingMode.MECHANICAL, InputComplexity.SIMPLE_COMMAND
                    
                else:
                    # Generic handling for other actions
                    response = f"You {selected_option.get('action', 'do')} {selected_option.get('target', '')}."
                    return response, ProcessingMode.HYBRID, InputComplexity.MODERATE
            
        except ValueError:
            # Not a number, continue with handling below
            pass
        
        # If we get here, the input wasn't a valid option number or "cancel"
        # Try to use text parser to match the input to an option
        best_match = None
        best_score = 0.0
        
        # Use the text parser's similarity calculation if available
        try:
            for i, option in enumerate(options):
                desc = option.get('description', '').lower()
                target = option.get('target', '').lower()
                action = option.get('action', '').lower()
                
                # Create a combined text to match against
                option_text = f"{action} {target} {desc}".strip()
                
                # Calculate similarity score for this option
                similarity = 0.0
                
                try:
                    # Get the object resolver instance methods
                    if isinstance(self.object_resolver, object) and hasattr(self.object_resolver, '_calculate_similarity'):
                        # Use the instance method
                        similarity = self.object_resolver._calculate_similarity(input_text, option_text)
                    elif hasattr(object_resolver, '_calculate_similarity'):
                        # Fallback to module function
                        similarity = object_resolver._calculate_similarity(input_text, option_text)
                    else:
                        # Fallback to simple string matching
                        if input_text == option_text:
                            similarity = 1.0
                        elif input_text in option_text:
                            similarity = 0.8
                        elif option_text in input_text:
                            similarity = 0.6
                        elif any(word in option_text for word in input_text.split() if len(word) > 3):
                            similarity = 0.5
                        else:
                            similarity = 0.0
                except Exception as e:
                    self.logger.error(f"Error calculating similarity: {e}")
                    # Simple fallback check
                    if input_text in option_text or any(word in option_text for word in input_text.split()):
                        similarity = 0.6
                
                # Update best match if this one is better
                if similarity > best_score and similarity > 0.5:  # Threshold
                    best_score = similarity
                    best_match = i
        except Exception as e:
            self.logger.error(f"Error matching disambiguation response: {e}")
            
        # If we found a match, process it
        if best_match is not None:
            selected_option = options[best_match]
            self.logger.info(f"Disambiguation: matched text input to option {best_match}: {selected_option.get('description', '')}")
            
            # Clear disambiguation state
            original_input = self.pending_disambiguation.get("original_input", "")
            self.pending_disambiguation = None
            
            # Generate response based on the selected option
            if selected_option.get("action") == "go":
                direction = selected_option.get("target", "")
                response = f"You move {direction}."
                return response, ProcessingMode.MECHANICAL, InputComplexity.SIMPLE_COMMAND
                
            elif selected_option.get("action") == "look":
                target = selected_option.get("target")
                if target:
                    response = f"You examine the {target} closely."
                else:
                    response = "You look around and observe your surroundings."
                return response, ProcessingMode.NARRATIVE, InputComplexity.SIMPLE_COMMAND
                
            elif selected_option.get("action") == "help":
                response = "Available commands: look, go [direction], take [item], use [item], inventory, help"
                return response, ProcessingMode.OOC, InputComplexity.SIMPLE_COMMAND
                
            elif selected_option.get("action") == "inventory":
                response = "You check your inventory."
                return response, ProcessingMode.MECHANICAL, InputComplexity.SIMPLE_COMMAND
                
            else:
                # Generic handling for other actions
                response = f"You {selected_option.get('action', 'do')} {selected_option.get('target', '')}."
                return response, ProcessingMode.HYBRID, InputComplexity.MODERATE
        
        # No match found
        response = "Please choose an option by number, or type 'cancel' to try something else."
        return response, ProcessingMode.DISAMBIGUATION, InputComplexity.DISAMBIGUATION
        
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
        elif mode == ProcessingMode.INTERPRETIVE:
            self.stats["interpretive_responses"] += 1
        elif mode == ProcessingMode.DISAMBIGUATION:
            self.stats["disambiguation_responses"] += 1
        
        # Update complexity stats
        if complexity == InputComplexity.SIMPLE_COMMAND:
            self.stats["simple_inputs"] += 1
        elif complexity == InputComplexity.MODERATE:
            self.stats["moderate_inputs"] += 1
        elif complexity == InputComplexity.COMPLEX:
            self.stats["complex_inputs"] += 1
        elif complexity == InputComplexity.CONVERSATIONAL:
            self.stats["conversational_inputs"] += 1
        elif complexity == InputComplexity.DISAMBIGUATION:
            self.stats["disambiguation_inputs"] += 1
        elif complexity == InputComplexity.PARSING_ERROR:
            self.stats["parsing_error_inputs"] += 1
        
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