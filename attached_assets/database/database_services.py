"""
Database service layer for AI GM Brain system
"""

from sqlalchemy import create_engine, desc, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from typing import Dict, Any, List, Optional, Tuple
import json
import numpy as np
from datetime import datetime, timedelta
import logging

from .models import (
    Base, GameSession, PlayerInteraction, LLMRequest, 
    GameEvent, WorldState, ConversationMemory, NarrativeEmbedding
)

class DatabaseService:
    """Main database service for the AI GM Brain system"""
    
    def __init__(self, database_url: str):
        """
        Initialize database service.
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger("DatabaseService")
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    # Game Session Management
    def create_game_session(self, player_id: str, session_name: str = None) -> str:
        """Create new game session."""
        with self.get_session() as db:
            session = GameSession(
                player_id=player_id,
                session_name=session_name or f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return str(session.id)
    
    def get_active_session(self, player_id: str) -> Optional[GameSession]:
        """Get active session for player."""
        with self.get_session() as db:
            return db.query(GameSession).filter(
                and_(GameSession.player_id == player_id, GameSession.is_active == True)
            ).order_by(desc(GameSession.last_active)).first()
    
    def update_session_activity(self, session_id: str, current_location: str = None):
        """Update session last activity."""
        with self.get_session() as db:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if session:
                session.last_active = datetime.utcnow()
                if current_location:
                    session.current_location = current_location
                db.commit()
    
    # Player Interaction Management
    def save_interaction(self, interaction_data: Dict[str, Any]) -> str:
        """Save player interaction."""
        with self.get_session() as db:
            interaction = PlayerInteraction(**interaction_data)
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            return str(interaction.id)
    
    def get_recent_interactions(self, session_id: str, limit: int = 10) -> List[PlayerInteraction]:
        """Get recent interactions for session."""
        with self.get_session() as db:
            return db.query(PlayerInteraction).filter(
                PlayerInteraction.session_id == session_id
            ).order_by(desc(PlayerInteraction.interaction_number)).limit(limit).all()
    
    def get_interaction_stats(self, session_id: str) -> Dict[str, Any]:
        """Get interaction statistics for session."""
        with self.get_session() as db:
            stats = db.query(
                func.count(PlayerInteraction.id).label('total_interactions'),
                func.avg(PlayerInteraction.processing_time).label('avg_processing_time'),
                func.sum(PlayerInteraction.tokens_used).label('total_tokens'),
                func.sum(PlayerInteraction.cost_estimate).label('total_cost'),
                func.count(func.nullif(PlayerInteraction.llm_used, False)).label('llm_interactions'),
                func.count(func.nullif(PlayerInteraction.parser_success, False)).label('parser_successes')
            ).filter(PlayerInteraction.session_id == session_id).first()
            
            return {
                'total_interactions': stats.total_interactions or 0,
                'avg_processing_time': float(stats.avg_processing_time) if stats.avg_processing_time else 0.0,
                'total_tokens': stats.total_tokens or 0,
                'total_cost': float(stats.total_cost) if stats.total_cost else 0.0,
                'llm_interactions': stats.llm_interactions or 0,
                'parser_successes': stats.parser_successes or 0,
                'parser_success_rate': (stats.parser_successes / max(1, stats.total_interactions)) if stats.parser_successes else 0.0,
                'llm_usage_rate': (stats.llm_interactions / max(1, stats.total_interactions)) if stats.llm_interactions else 0.0
            }
    
    # LLM Request Management
    def save_llm_request(self, request_data: Dict[str, Any]) -> str:
        """Save LLM request."""
        with self.get_session() as db:
            request = LLMRequest(**request_data)
            db.add(request)
            db.commit()
            db.refresh(request)
            return str(request.id)
    
    def get_llm_usage_stats(self, session_id: str = None, days: int = 7) -> Dict[str, Any]:
        """Get LLM usage statistics."""
        with self.get_session() as db:
            query = db.query(
                LLMRequest.provider,
                LLMRequest.model,
                func.count(LLMRequest.id).label('request_count'),
                func.sum(LLMRequest.tokens_used).label('total_tokens'),
                func.sum(LLMRequest.cost_estimate).label('total_cost'),
                func.avg(LLMRequest.response_time).label('avg_response_time')
            )
            
            # Filter by session if provided
            if session_id:
                query = query.join(PlayerInteraction).filter(
                    PlayerInteraction.session_id == session_id
                )
            
            # Filter by date range
            since_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(LLMRequest.created_at >= since_date)
            
            stats = query.group_by(LLMRequest.provider, LLMRequest.model).all()
            
            return [
                {
                    'provider': stat.provider,
                    'model': stat.model,
                    'request_count': stat.request_count,
                    'total_tokens': stat.total_tokens or 0,
                    'total_cost': float(stat.total_cost) if stat.total_cost else 0.0,
                    'avg_response_time': float(stat.avg_response_time) if stat.avg_response_time else 0.0
                }
                for stat in stats
            ]
    
    # Game Event Management
    def save_event(self, event_data: Dict[str, Any]) -> str:
        """Save game event."""
        with self.get_session() as db:
            event = GameEvent(**event_data)
            db.add(event)
            db.commit()
            db.refresh(event)
            return str(event.id)
    
    def get_recent_events(self, session_id: str, event_types: List[str] = None, limit: int = 20) -> List[GameEvent]:
        """Get recent events for session."""
        with self.get_session() as db:
            query = db.query(GameEvent).filter(GameEvent.session_id == session_id)
            
            if event_types:
                query = query.filter(GameEvent.event_type.in_(event_types))
            
            return query.order_by(desc(GameEvent.created_at)).limit(limit).all()
    
    # World State Management
    def save_world_state(self, session_id: str, world_state_data: Dict[str, Any]) -> str:
        """Save world state."""
        with self.get_session() as db:
            # Get current version
            current_version = db.query(func.max(WorldState.version)).filter(
                WorldState.session_id == session_id
            ).scalar() or 0
            
            world_state = WorldState(
                session_id=session_id,
                version=current_version + 1,
                **world_state_data
            )
            db.add(world_state)
            db.commit()
            db.refresh(world_state)
            return str(world_state.id)
    
    def get_current_world_state(self, session_id: str) -> Optional[WorldState]:
        """Get current world state for session."""
        with self.get_session() as db:
            return db.query(WorldState).filter(
                WorldState.session_id == session_id
            ).order_by(desc(WorldState.version)).first()
    
    # Conversation Memory Management
    def save_conversation_memory(self, memory_data: Dict[str, Any]) -> str:
        """Save conversation memory."""
        with self.get_session() as db:
            memory = ConversationMemory(**memory_data)
            db.add(memory)
            db.commit()
            db.refresh(memory)
            return str(memory.id)
    
    def get_conversation_memory(self, session_id: str, conversation_id: str) -> Optional[ConversationMemory]:
        """Get conversation memory."""
        with self.get_session() as db:
            return db.query(ConversationMemory).filter(
                and_(
                    ConversationMemory.session_id == session_id,
                    ConversationMemory.conversation_id == conversation_id
                )
            ).order_by(desc(ConversationMemory.updated_at)).first()
    
    def update_conversation_memory(self, memory_id: str, memory_data: Dict[str, Any]):
        """Update conversation memory."""
        with self.get_session() as db:
            memory = db.query(ConversationMemory).filter(ConversationMemory.id == memory_id).first()
            if memory:
                memory.memory_data = memory_data
                memory.updated_at = datetime.utcnow()
                db.commit()
    
    # Vector Embedding Management
    def save_embedding(self, embedding_data: Dict[str, Any]) -> str:
        """Save narrative embedding."""
        with self.get_session() as db:
            embedding = NarrativeEmbedding(**embedding_data)
            db.add(embedding)
            db.commit()
            db.refresh(embedding)
            return str(embedding.id)
    
    def search_similar_embeddings(self, 
                                 query_embedding: List[float], 
                                 session_id: str = None,
                                 content_types: List[str] = None,
                                 limit: int = 5,
                                 similarity_threshold: float = 0.7) -> List[Tuple[NarrativeEmbedding, float]]:
        """Search for similar embeddings using cosine similarity."""
        with self.get_session() as db:
            query = db.query(NarrativeEmbedding)
            
            if session_id:
                query = query.filter(NarrativeEmbedding.session_id == session_id)
            
            if content_types:
                query = query.filter(NarrativeEmbedding.content_type.in_(content_types))
            
            embeddings = query.all()
            
            # Calculate cosine similarity
            results = []
            query_embedding = np.array(query_embedding)
            
            for embedding in embeddings:
                stored_embedding = np.array(embedding.embedding)
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                if similarity >= similarity_threshold:
                    results.append((embedding, float(similarity)))
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]