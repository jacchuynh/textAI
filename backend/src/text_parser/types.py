"""
Shared types for the text parser system.

This module contains common types and data structures used across all parser modules
to avoid circular import issues.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class ParsedCommand:
    """
    Represents a parsed player command with extracted information.
    
    This is the core data structure that flows through the parsing pipeline:
    spaCy processing -> Intent routing -> Action execution -> Response generation
    """
    
    # Action field for compatibility with parser_engine
    action: str = ""  # Primary verb/action (e.g., "go", "look", "take")
    
    # Additional fields for parser_engine compatibility
    target: str = ""
    modifiers: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    # Raw input and basic processing
    raw_text: str = ""
    cleaned_text: str = ""
    
    # spaCy analysis results
    tokens: List[str] = field(default_factory=list)
    pos_tags: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    
    # Extracted command components
    action_word: Optional[str] = None
    target_entity: Optional[str] = None
    secondary_entity: Optional[str] = None
    direction: Optional[str] = None
    location: Optional[str] = None
    
    # Intent classification (from Phase 2)
    primary_intent: Optional[str] = None
    sub_intent: Optional[str] = None
    confidence_score: float = 0.0
    
    # Contextual information
    requires_target: bool = False
    ambiguous_entities: List[str] = field(default_factory=list)
    context_needed: List[str] = field(default_factory=list)
    
    # Metadata
    processing_time: float = 0.0
    spacy_doc: Any = None  # Store the spaCy Doc object
    matched_patterns: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'raw_text': self.raw_text,
            'cleaned_text': self.cleaned_text,
            'tokens': self.tokens,
            'pos_tags': self.pos_tags,
            'entities': self.entities,
            'dependencies': self.dependencies,
            'action_word': self.action_word,
            'target_entity': self.target_entity,
            'secondary_entity': self.secondary_entity,
            'direction': self.direction,
            'location': self.location,
            'primary_intent': self.primary_intent,
            'sub_intent': self.sub_intent,
            'confidence_score': self.confidence_score,
            'requires_target': self.requires_target,
            'ambiguous_entities': self.ambiguous_entities,
            'context_needed': self.context_needed,
            'processing_time': self.processing_time,
            'matched_patterns': self.matched_patterns,
            'action': self.action,
            'target': self.target,
            'modifiers': self.modifiers,
            'context': self.context,
            'confidence': self.confidence
        }


@dataclass
class GameContext:
    """
    Game context information available to the parser.
    
    This provides context about the current game state that helps
    with disambiguation and intent understanding.
    """
    
    # Player state
    player_id: str
    current_location: Optional[str] = None
    player_level: int = 1
    player_class: Optional[str] = None
    
    # Location information
    available_exits: List[str] = field(default_factory=list)
    visible_items: List[str] = field(default_factory=list)
    visible_npcs: List[str] = field(default_factory=list)
    visible_features: List[str] = field(default_factory=list)
    
    # Player inventory
    inventory_items: List[str] = field(default_factory=list)
    equipped_items: Dict[str, str] = field(default_factory=dict)  # slot -> item
    
    # Combat state
    in_combat: bool = False
    combat_targets: List[str] = field(default_factory=list)
    
    # Conversation state
    talking_to_npc: Optional[str] = None
    conversation_state: Optional[str] = None
    
    # Recent context
    recent_commands: List[str] = field(default_factory=list)
    recent_responses: List[str] = field(default_factory=list)
    
    # Meta information
    session_start_time: Optional[float] = None
    last_action_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'player_id': self.player_id,
            'current_location': self.current_location,
            'player_level': self.player_level,
            'player_class': self.player_class,
            'available_exits': self.available_exits,
            'visible_items': self.visible_items,
            'visible_npcs': self.visible_npcs,
            'visible_features': self.visible_features,
            'inventory_items': self.inventory_items,
            'equipped_items': self.equipped_items,
            'in_combat': self.in_combat,
            'combat_targets': self.combat_targets,
            'talking_to_npc': self.talking_to_npc,
            'conversation_state': self.conversation_state,
            'recent_commands': self.recent_commands,
            'recent_responses': self.recent_responses,
            'session_start_time': self.session_start_time,
            'last_action_time': self.last_action_time
        }


class ParseResult(Enum):
    """Result status of parsing operations."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"  
    AMBIGUOUS = "ambiguous"
    MISSING_TARGET = "missing_target"
    UNRECOGNIZED = "unrecognized"
    ERROR = "error"
