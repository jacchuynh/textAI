"""
Database models for AI GM Brain system using SQLAlchemy and PostgreSQL
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import uuid

Base = declarative_base()

class GameSession(Base):
    """Game session tracking"""
    __tablename__ = 'game_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(String(50), nullable=False)
    session_name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    current_location = Column(String(100))
    session_state = Column(JSONB)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    interactions = relationship("PlayerInteraction", back_populates="session", cascade="all, delete-orphan")
    events = relationship("GameEvent", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_game_sessions_player_active', 'player_id', 'is_active'),
        Index('idx_game_sessions_last_active', 'last_active'),
    )

class PlayerInteraction(Base):
    """Player input and AI responses"""
    __tablename__ = 'player_interactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('game_sessions.id'), nullable=False)
    interaction_number = Column(Integer, nullable=False)
    player_input = Column(Text, nullable=False)
    input_complexity = Column(String(50))
    processing_mode = Column(String(50))
    
    # Parser results
    parser_success = Column(Boolean, default=False)
    parsed_command = Column(JSONB)
    disambiguation_needed = Column(Boolean, default=False)
    
    # AI response
    ai_response = Column(Text)
    response_type = Column(String(50))
    llm_used = Column(Boolean, default=False)
    
    # Performance metrics
    processing_time = Column(Float)
    tokens_used = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="interactions")
    llm_requests = relationship("LLMRequest", back_populates="interaction", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_interactions_session_number', 'session_id', 'interaction_number'),
        Index('idx_interactions_created_at', 'created_at'),
    )

class LLMRequest(Base):
    """LLM API requests and responses"""
    __tablename__ = 'llm_requests'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey('player_interactions.id'))
    
    # Request details
    provider = Column(String(50))  # openrouter, openai, etc.
    model = Column(String(100))
    prompt_mode = Column(String(50))
    prompt_text = Column(Text)
    request_parameters = Column(JSONB)  # temperature, max_tokens, etc.
    
    # Response details
    response_text = Column(Text)
    parsed_json = Column(JSONB)
    tokens_used = Column(Integer)
    cost_estimate = Column(Float)
    response_time = Column(Float)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    interaction = relationship("PlayerInteraction", back_populates="llm_requests")
    
    __table_args__ = (
        Index('idx_llm_requests_provider_model', 'provider', 'model'),
        Index('idx_llm_requests_created_at', 'created_at'),
    )

class GameEvent(Base):
    """Game events and state changes"""
    __tablename__ = 'game_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('game_sessions.id'), nullable=False)
    
    event_type = Column(String(100), nullable=False)
    actor = Column(String(100))
    context = Column(JSONB)
    metadata = Column(JSONB)
    tags = Column(ARRAY(String))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="events")
    
    __table_args__ = (
        Index('idx_game_events_session_type', 'session_id', 'event_type'),
        Index('idx_game_events_created_at', 'created_at'),
    )

class WorldState(Base):
    """World state tracking"""
    __tablename__ = 'world_states'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('game_sessions.id'), nullable=False)
    
    # World state data
    economic_status = Column(String(50))
    political_stability = Column(String(50))
    current_season = Column(String(50))
    active_global_threats = Column(ARRAY(String))
    world_properties = Column(JSONB)
    
    # Versioning
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_world_states_session_version', 'session_id', 'version'),
    )

class ConversationMemory(Base):
    """Conversation memory for Langchain integration"""
    __tablename__ = 'conversation_memory'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('game_sessions.id'), nullable=False)
    
    # Memory data
    conversation_id = Column(String(100))  # For Langchain conversation chains
    memory_type = Column(String(50))  # summary, buffer, vector, etc.
    memory_data = Column(JSONB)  # Serialized Langchain memory
    
    # Context
    character_id = Column(String(100))  # Player, NPC, etc.
    context_type = Column(String(50))   # dialogue, narrative, world_query
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_conversation_memory_session_char', 'session_id', 'character_id'),
        Index('idx_conversation_memory_conv_id', 'conversation_id'),
    )

# Vector embeddings table for semantic search
class NarrativeEmbedding(Base):
    """Vector embeddings for narrative content"""
    __tablename__ = 'narrative_embeddings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('game_sessions.id'))
    
    # Content identification
    content_type = Column(String(50))  # event, dialogue, description, etc.
    content_id = Column(String(100))   # Reference to original content
    content_text = Column(Text)
    
    # Vector embedding (stored as JSON array for PostgreSQL compatibility)
    embedding = Column(JSONB)
    embedding_model = Column(String(100))
    
    # Metadata for filtering
    tags = Column(ARRAY(String))
    metadata = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_narrative_embeddings_session_type', 'session_id', 'content_type'),
        Index('idx_narrative_embeddings_content_id', 'content_id'),
    )