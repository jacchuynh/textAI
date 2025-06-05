"""
AI GM Brain Shim
This module provides lightweight mocks and shims for components needed by the AI GM Brain.
"""

import logging
from typing import Dict, Any, List, Optional

class EventType:
    """Event types used by the AI GM Brain."""
    NARRATIVE_BRANCH_AVAILABLE = "NARRATIVE_BRANCH_AVAILABLE"
    NPC_INTERACTION = "NPC_INTERACTION"
    LOCATION_ENTERED = "LOCATION_ENTERED"
    WORLD_STATE_CHANGED = "WORLD_STATE_CHANGED"
    ACTION_PERFORMED = "ACTION_PERFORMED"
    PLAYER_COMMAND = "PLAYER_COMMAND"

class GameEvent:
    """A game event with type and data."""
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data

class EventBus:
    """Simple event bus implementation."""
    def __init__(self):
        self.subscribers = {}
        self.logger = logging.getLogger("EventBus")
    
    def subscribe(self, event_type: str, callback):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event: GameEvent):
        """Publish an event to subscribers."""
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event subscriber: {e}")

class WorldState:
    """Mock world state manager."""
    def __init__(self):
        self.state = {}
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current world state."""
        return self.state
    
    def update_state(self, updates: Dict[str, Any]):
        """Update the world state."""
        self.state.update(updates)

class NarrativeContextManager:
    """Mock narrative context manager."""
    def __init__(self, narrative_context, world_state):
        self.narrative_context = narrative_context
        self.world_state = world_state
    
    def prepare_context(self, player_id: str) -> Dict[str, Any]:
        """Prepare narrative context for a player."""
        return {"player_id": player_id}

class TemplateProcessor:
    """Mock template processor."""
    def process_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Process a template with context."""
        return f"Processed template: {template_name}"

class AIGMDialogueGenerator:
    """Mock dialogue generator."""
    def __init__(self, template_processor):
        self.template_processor = template_processor
    
    def generate_dialogue(self, context: Dict[str, Any]) -> str:
        """Generate dialogue based on context."""
        return "Generated dialogue based on context"

class NarrativeBranchChoiceHandler:
    """Mock narrative branch choice handler."""
    def __init__(self, narrative_director, event_bus):
        self.narrative_director = narrative_director
        self.event_bus = event_bus
    
    def handle_choice(self, choice_id: str, player_id: str):
        """Handle a narrative branch choice."""
        pass

class ParsedCommand:
    """Mock parsed command."""
    def __init__(self, command_type: str, target: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        self.command_type = command_type
        self.target = target
        self.params = params or {}

# Create singletons
event_bus = EventBus()
world_state_manager = WorldState()

# Create mock text parser components
class TextParser:
    """Mock text parser."""
    def parse_input(self, input_text: str) -> ParsedCommand:
        """Parse input text into a command."""
        return ParsedCommand("unknown", None, {"raw_input": input_text})

class VocabularyManager:
    """Mock vocabulary manager."""
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word."""
        return [word]

class ObjectResolver:
    """Mock object resolver."""
    def resolve_object(self, name: str) -> Optional[Dict[str, Any]]:
        """Resolve an object by name."""
        return None

class GameContext:
    """Mock game context."""
    def get_current_location(self) -> Dict[str, Any]:
        """Get the current location."""
        return {"name": "Unknown Location", "description": "An unknown location"}

# Create mock text parser singletons
parser_engine = TextParser()
vocabulary_manager = VocabularyManager()
object_resolver = ObjectResolver()
game_context = GameContext()

# Mock for the parse_input function
def parse_input(input_text: str) -> ParsedCommand:
    """Parse input text into a command."""
    return parser_engine.parse_input(input_text)

# LLM components
class LLMProvider:
    """LLM provider enum."""
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class PromptMode:
    """Prompt mode enum."""
    MECHANICAL = "mechanical"
    NARRATIVE = "narrative"
    INTERPRETIVE = "interpretive"

class LLMManager:
    """Mock LLM manager."""
    def __init__(self):
        self.logger = logging.getLogger("LLMManager")
    
    async def generate_response(self, prompt: str, mode: str = PromptMode.MECHANICAL) -> str:
        """Generate a response using an LLM."""
        return f"LLM response for prompt: {prompt[:20]}..."
