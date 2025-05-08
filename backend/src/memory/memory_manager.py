"""
Memory management system for the game engine.

This module implements a three-tier memory system:
1. Short-term memory: Recent events and interactions (last few minutes/turns)
2. Medium-term memory: Important events from the current session
3. Long-term memory: Persistent memories across game sessions

It also handles memory compression, prioritization, and retrieval.
"""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from enum import Enum
import heapq
import re

# For future implementation with actual embeddings
# try:
#     import numpy as np
#     from sentence_transformers import SentenceTransformer
#     EMBEDDING_AVAILABLE = True
# except ImportError:
#     EMBEDDING_AVAILABLE = False


class MemoryTier(Enum):
    """Tiers of memory with different retention properties."""
    SHORT_TERM = "short_term"  # Recent events, high detail, temporary
    MEDIUM_TERM = "medium_term"  # Important events from current session
    LONG_TERM = "long_term"  # Persistent memories across sessions


class MemoryType(Enum):
    """Types of memories for categorization."""
    WORLD_EVENT = "world_event"
    NPC_INTERACTION = "npc_interaction"
    PLAYER_ACTION = "player_action"
    COMBAT = "combat"
    DISCOVERY = "discovery"
    QUEST = "quest"
    CRAFTING = "crafting"
    BASEBUILDING = "basebuilding"
    KINGDOM = "kingdom"
    IMPORTANT = "important"  # Marked as especially significant


class MemoryEntry:
    """
    A single memory entry in the memory system.
    
    Attributes:
        id: Unique identifier for this memory
        type: The type of memory for categorization
        content: The textual content of the memory
        timestamp: When this memory was created
        importance: How important this memory is (0-10)
        tier: Which memory tier this belongs to
        tags: List of tags for categorization/retrieval
        metadata: Additional structured data about the memory
        embedding: Vector representation for semantic search (if available)
        game_id: ID of the game this memory belongs to
    """
    
    def __init__(self, 
                type: Union[MemoryType, str], 
                content: str,
                importance: int = 5,
                tier: MemoryTier = MemoryTier.MEDIUM_TERM,
                tags: Optional[List[str]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                game_id: Optional[str] = None):
        """
        Initialize a new memory entry.
        
        Args:
            type: The type of memory
            content: The textual content of the memory
            importance: How important this memory is (0-10)
            tier: Which memory tier this belongs to
            tags: List of tags for categorization/retrieval
            metadata: Additional structured data about the memory
            game_id: ID of the game this memory belongs to
        """
        import uuid
        self.id = str(uuid.uuid4())
        
        # Handle string types for flexibility
        if isinstance(type, str):
            try:
                self.type = MemoryType(type)
            except ValueError:
                # Custom memory type
                self.type = type
        else:
            self.type = type
            
        self.content = content
        self.timestamp = datetime.utcnow().isoformat()
        self.importance = max(0, min(10, importance))  # Clamp to 0-10
        self.tier = tier
        self.tags = tags or []
        self.metadata = metadata or {}
        self.game_id = game_id
        self.embedding = None  # Will be computed when needed
        self.last_accessed = time.time()  # For recency tracking
        self.access_count = 0  # For frequency tracking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        type_repr = self.type.value if isinstance(self.type, MemoryType) else str(self.type)
        tier_repr = self.tier.value if isinstance(self.tier, MemoryTier) else str(self.tier)
        
        return {
            "id": self.id,
            "type": type_repr,
            "content": self.content,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "tier": tier_repr,
            "tags": self.tags,
            "metadata": self.metadata,
            "game_id": self.game_id,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create a MemoryEntry from a dictionary."""
        memory = cls(
            type=data["type"],
            content=data["content"],
            importance=data.get("importance", 5),
            tier=MemoryTier(data["tier"]) if "tier" in data else MemoryTier.MEDIUM_TERM,
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            game_id=data.get("game_id")
        )
        memory.id = data["id"]
        memory.timestamp = data["timestamp"]
        memory.access_count = data.get("access_count", 0)
        memory.last_accessed = data.get("last_accessed", time.time())
        return memory
    
    def update_access_stats(self):
        """Update the access statistics for this memory."""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def __lt__(self, other):
        """For priority queue comparison."""
        # Higher importance is higher priority
        return self.get_priority() > other.get_priority()
    
    def get_priority(self) -> float:
        """
        Calculate this memory's retrieval priority based on:
        - Importance
        - Recency
        - Access frequency
        
        Returns:
            Priority score (higher is more important)
        """
        # Recency: Higher for more recent memories
        recency = 1.0 - min(1.0, (time.time() - self.last_accessed) / (24 * 60 * 60))
        
        # Frequency: Higher for more frequently accessed memories
        frequency = min(1.0, self.access_count / 10)
        
        # Weights
        importance_weight = 0.6
        recency_weight = 0.3
        frequency_weight = 0.1
        
        # Normalized score (0-1 range)
        return (
            (self.importance / 10.0) * importance_weight +
            recency * recency_weight +
            frequency * frequency_weight
        )


class MemoryManager:
    """
    Three-tier memory system manager.
    
    This system handles:
    - Adding memories to appropriate tiers
    - Prioritizing memories for retrieval
    - Compressing and summarizing memories
    - Retrieving relevant memories for context
    """
    
    def __init__(self, 
                data_dir: str = "data/memories",
                max_short_term: int = 50,
                max_medium_term: int = 200,
                max_long_term: int = 1000):
        """
        Initialize the memory manager.
        
        Args:
            data_dir: Directory for persistent storage
            max_short_term: Maximum number of short-term memories to keep
            max_medium_term: Maximum number of medium-term memories to keep
            max_long_term: Maximum number of long-term memories to keep
        """
        # Memory storage by tier
        self.short_term_memories: List[MemoryEntry] = []
        self.medium_term_memories: List[MemoryEntry] = []
        self.long_term_memories: Dict[str, List[MemoryEntry]] = {}  # By game_id
        
        # Capacity limits
        self.max_short_term = max_short_term
        self.max_medium_term = max_medium_term
        self.max_long_term = max_long_term
        
        # Set up storage
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize embedding model (if available)
        self.embedding_model = None
        # if EMBEDDING_AVAILABLE:
        #     try:
        #         self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        #     except Exception as e:
        #         print(f"Error loading embedding model: {e}")
    
    def add_memory(self, 
                  type: Union[MemoryType, str],
                  content: str,
                  importance: int = 5,
                  tier: MemoryTier = MemoryTier.MEDIUM_TERM,
                  tags: Optional[List[str]] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  game_id: Optional[str] = None) -> str:
        """
        Add a new memory to the appropriate tier.
        
        Args:
            type: The type of memory
            content: The textual content of the memory
            importance: How important this memory is (0-10)
            tier: Which memory tier this belongs to
            tags: List of tags for categorization/retrieval
            metadata: Additional structured data about the memory
            game_id: ID of the game this memory belongs to
            
        Returns:
            ID of the new memory
        """
        # Create the memory entry
        memory = MemoryEntry(
            type=type,
            content=content,
            importance=importance,
            tier=tier,
            tags=tags,
            metadata=metadata,
            game_id=game_id
        )
        
        # Calculate embedding if model is available
        if self.embedding_model is not None:
            try:
                memory.embedding = self.embedding_model.encode(content)
            except Exception as e:
                print(f"Error generating embedding: {e}")
        
        # Add to the appropriate tier
        if tier == MemoryTier.SHORT_TERM:
            self.short_term_memories.append(memory)
            
            # Enforce capacity limit
            if len(self.short_term_memories) > self.max_short_term:
                # Remove lowest priority memories
                self.short_term_memories.sort(key=lambda x: x.get_priority())
                self.short_term_memories = self.short_term_memories[-self.max_short_term:]
                
        elif tier == MemoryTier.MEDIUM_TERM:
            self.medium_term_memories.append(memory)
            
            # Enforce capacity limit
            if len(self.medium_term_memories) > self.max_medium_term:
                # Remove lowest priority memories
                self.medium_term_memories.sort(key=lambda x: x.get_priority())
                self.medium_term_memories = self.medium_term_memories[-self.max_medium_term:]
                
        elif tier == MemoryTier.LONG_TERM:
            if not game_id:
                print("Warning: Long-term memory requires a game_id")
                return memory.id
                
            # Initialize game memory list if needed
            if game_id not in self.long_term_memories:
                self.long_term_memories[game_id] = []
                
            # Add the memory
            self.long_term_memories[game_id].append(memory)
            
            # Enforce capacity limit
            if len(self.long_term_memories[game_id]) > self.max_long_term:
                # Remove lowest priority memories
                self.long_term_memories[game_id].sort(key=lambda x: x.get_priority())
                self.long_term_memories[game_id] = self.long_term_memories[game_id][-self.max_long_term:]
                
            # Persist to disk
            self._save_long_term_memories(game_id)
        
        return memory.id
    
    def _save_long_term_memories(self, game_id: str):
        """Save long-term memories for a game to disk."""
        if game_id not in self.long_term_memories:
            return
            
        memories = self.long_term_memories[game_id]
        if not memories:
            return
            
        # Convert to dictionary format
        memory_dicts = [memory.to_dict() for memory in memories]
        
        # Save to JSON file
        file_path = os.path.join(self.data_dir, f"game_{game_id}_memories.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(memory_dicts, f, indent=2)
        except Exception as e:
            print(f"Error saving memories to disk: {e}")
    
    def _load_long_term_memories(self, game_id: str) -> List[MemoryEntry]:
        """Load long-term memories for a game from disk."""
        file_path = os.path.join(self.data_dir, f"game_{game_id}_memories.json")
        if not os.path.exists(file_path):
            return []
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                memory_dicts = json.load(f)
                
            # Convert to MemoryEntry objects
            memories = [MemoryEntry.from_dict(data) for data in memory_dicts]
            return memories
        except Exception as e:
            print(f"Error loading memories from disk: {e}")
            return []
    
    def get_memories(self, 
                    game_id: Optional[str] = None,
                    tiers: Optional[List[MemoryTier]] = None,
                    types: Optional[List[Union[MemoryType, str]]] = None,
                    tags: Optional[List[str]] = None,
                    min_importance: int = 0,
                    limit: Optional[int] = None,
                    query: Optional[str] = None) -> List[MemoryEntry]:
        """
        Get filtered memories.
        
        Args:
            game_id: Optional game ID to filter by
            tiers: Optional list of memory tiers to include
            types: Optional list of memory types to include
            tags: Optional list of tags to filter by (any match)
            min_importance: Minimum importance level (0-10)
            limit: Maximum number of memories to return
            query: Optional text query for relevance search
            
        Returns:
            List of matching memories, sorted by priority
        """
        # Default to all tiers if not specified
        if tiers is None:
            tiers = list(MemoryTier)
            
        # Collect memories from requested tiers
        all_memories = []
        
        if MemoryTier.SHORT_TERM in tiers:
            all_memories.extend(self.short_term_memories)
            
        if MemoryTier.MEDIUM_TERM in tiers:
            all_memories.extend(self.medium_term_memories)
            
        if MemoryTier.LONG_TERM in tiers:
            # Load from disk if needed
            if game_id and game_id not in self.long_term_memories:
                self.long_term_memories[game_id] = self._load_long_term_memories(game_id)
                
            # Add memories for the game
            if game_id and game_id in self.long_term_memories:
                all_memories.extend(self.long_term_memories[game_id])
            # If no game_id specified, include all long-term memories
            elif game_id is None:
                for game_memories in self.long_term_memories.values():
                    all_memories.extend(game_memories)
        
        # Apply filters
        filtered_memories = all_memories
        
        # Filter by game_id
        if game_id:
            filtered_memories = [m for m in filtered_memories if m.game_id == game_id]
            
        # Filter by types
        if types:
            type_values = [
                t.value if isinstance(t, MemoryType) else t
                for t in types
            ]
            filtered_memories = [
                m for m in filtered_memories
                if (isinstance(m.type, MemoryType) and m.type.value in type_values) or
                   (isinstance(m.type, str) and m.type in type_values)
            ]
            
        # Filter by tags (any match)
        if tags:
            filtered_memories = [
                m for m in filtered_memories
                if any(tag in m.tags for tag in tags)
            ]
            
        # Filter by importance
        if min_importance > 0:
            filtered_memories = [m for m in filtered_memories if m.importance >= min_importance]
            
        # If a query is provided, perform relevance search
        if query:
            if self.embedding_model:
                # Use vector similarity if available
                try:
                    query_embedding = self.embedding_model.encode(query)
                    
                    # Add similarity score to each memory
                    for memory in filtered_memories:
                        if memory.embedding is None:
                            memory.embedding = self.embedding_model.encode(memory.content)
                        
                        # Cosine similarity would be computed here with NumPy
                    # For now, we'll just use a dummy similarity value since we don't have NumPy
                    memory.metadata["similarity"] = 0.5  # Placeholder value
                    print("Warning: Vector similarity requires NumPy, using fallback")
                        
                    # Sort by similarity
                    filtered_memories.sort(key=lambda x: x.metadata.get("similarity", 0), reverse=True)
                except Exception as e:
                    print(f"Error in vector search: {e}")
                    # Fall back to text search
                    filtered_memories = self._text_search(filtered_memories, query)
            else:
                # Simple text search fallback
                filtered_memories = self._text_search(filtered_memories, query)
        else:
            # Sort by priority
            filtered_memories.sort(key=lambda x: x.get_priority(), reverse=True)
            
        # Update access stats for returned memories
        for memory in filtered_memories[:limit]:
            memory.update_access_stats()
            
        # Apply limit
        if limit:
            filtered_memories = filtered_memories[:limit]
            
        return filtered_memories
    
    def _text_search(self, memories: List[MemoryEntry], query: str) -> List[MemoryEntry]:
        """
        Perform text-based search on memories.
        
        Args:
            memories: List of memories to search
            query: Text query
            
        Returns:
            Filtered and ranked list of memories
        """
        # Split query into keywords
        keywords = [k.lower() for k in query.split() if len(k) > 2]
        
        results = []
        for memory in memories:
            content_lower = memory.content.lower()
            
            # Count matching keywords
            matches = sum(1 for k in keywords if k in content_lower)
            
            # Only include memories with at least one match
            if matches > 0:
                # Higher score for more matches and higher importance
                score = matches + (memory.importance / 10.0)
                results.append((memory, score))
        
        # Sort by score, descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the memories
        return [m for m, _ in results]
    
    def consolidate_memories(self, game_id: str, max_tokens: int = 1000) -> str:
        """
        Create a consolidated summary of important memories.
        
        Args:
            game_id: Game ID to consolidate memories for
            max_tokens: Approximate maximum tokens in summary
            
        Returns:
            Consolidated summary text
        """
        # Get the most important memories
        important_memories = self.get_memories(
            game_id=game_id,
            tiers=[MemoryTier.MEDIUM_TERM, MemoryTier.LONG_TERM],
            min_importance=7,
            limit=20
        )
        
        # Get recent memories
        recent_memories = self.get_memories(
            game_id=game_id,
            tiers=[MemoryTier.SHORT_TERM, MemoryTier.MEDIUM_TERM],
            limit=10
        )
        
        # Combine and deduplicate
        all_memories = []
        memory_ids = set()
        
        for memory in important_memories + recent_memories:
            if memory.id not in memory_ids:
                all_memories.append(memory)
                memory_ids.add(memory.id)
        
        # Sort by timestamp
        all_memories.sort(key=lambda x: x.timestamp)
        
        # Create summary
        summary_lines = ["# Game Memory Summary"]
        
        if not all_memories:
            return "No significant memories found."
        
        # Group memories by type
        memories_by_type = {}
        for memory in all_memories:
            memory_type = memory.type.value if isinstance(memory.type, MemoryType) else str(memory.type)
            if memory_type not in memories_by_type:
                memories_by_type[memory_type] = []
            memories_by_type[memory_type].append(memory)
        
        # Add sections for each type
        for memory_type, memories in memories_by_type.items():
            # Format the type name for display
            display_type = memory_type.replace("_", " ").title()
            summary_lines.append(f"## {display_type}")
            
            for memory in memories:
                summary_lines.append(f"- {memory.content}")
            
            summary_lines.append("")
        
        # Apply crude token limiting (approx 4 chars per token)
        result = "\n".join(summary_lines)
        if len(result) > max_tokens * 4:
            result = result[:max_tokens * 4] + "...\n[Summary truncated due to length]"
        
        return result
    
    def get_recent_narrative(self, game_id: str, limit: int = 10) -> str:
        """
        Get a narrative of recent events.
        
        Args:
            game_id: Game ID to get narrative for
            limit: Maximum number of events to include
            
        Returns:
            Narrative text
        """
        # Get recent memories in chronological order
        recent_memories = self.get_memories(
            game_id=game_id,
            tiers=[MemoryTier.SHORT_TERM, MemoryTier.MEDIUM_TERM],
            limit=limit
        )
        
        # Sort by timestamp
        recent_memories.sort(key=lambda x: x.timestamp)
        
        if not recent_memories:
            return "No recent events to report."
        
        # Convert to narrative format
        narrative_lines = ["Recent events:"]
        
        for memory in recent_memories:
            narrative_lines.append(f"- {memory.content}")
        
        return "\n".join(narrative_lines)
    
    def remember_conversation(self, 
                             game_id: str,
                             speaker: str,
                             target: str,
                             dialogue: str,
                             importance: int = 5) -> str:
        """
        Remember a conversation with an NPC.
        
        Args:
            game_id: Game ID
            speaker: Who is speaking (player/NPC name)
            target: Who they're speaking to
            dialogue: The dialogue content
            importance: Importance level (0-10)
            
        Returns:
            Memory ID
        """
        # Format the memory content
        content = f"{speaker} to {target}: {dialogue}"
        
        # Determine tier based on importance
        tier = MemoryTier.MEDIUM_TERM
        if importance >= 8:
            tier = MemoryTier.LONG_TERM
        elif importance <= 3:
            tier = MemoryTier.SHORT_TERM
        
        # Add appropriate tags
        tags = ["conversation", speaker.lower(), target.lower()]
        
        # Add the memory
        return self.add_memory(
            type=MemoryType.NPC_INTERACTION,
            content=content,
            importance=importance,
            tier=tier,
            tags=tags,
            metadata={
                "speaker": speaker,
                "target": target
            },
            game_id=game_id
        )
    
    def remember_character_development(self,
                                      game_id: str,
                                      character_id: str,
                                      development_type: str,
                                      description: str,
                                      importance: int = 7) -> str:
        """
        Remember character development (level up, new skill, etc).
        
        Args:
            game_id: Game ID
            character_id: Character ID
            development_type: Type of development (level_up, domain_increase, etc)
            description: Description of the development
            importance: Importance level (0-10)
            
        Returns:
            Memory ID
        """
        # Character development is usually important, so medium or long term
        tier = MemoryTier.MEDIUM_TERM
        if importance >= 8:
            tier = MemoryTier.LONG_TERM
        
        # Add the memory
        return self.add_memory(
            type=MemoryType.IMPORTANT,
            content=description,
            importance=importance,
            tier=tier,
            tags=["character_development", development_type, character_id],
            metadata={
                "character_id": character_id,
                "development_type": development_type
            },
            game_id=game_id
        )
    
    def prune_old_memories(self, 
                          game_id: Optional[str] = None, 
                          hours: int = 24,
                          min_importance: int = 5) -> int:
        """
        Prune old, low-importance memories.
        
        Args:
            game_id: Optional game ID to filter by
            hours: Age threshold in hours
            min_importance: Memories below this importance will be pruned
            
        Returns:
            Number of memories pruned
        """
        count = 0
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_timestamp = cutoff_time.isoformat()
        
        # Prune short-term memories
        original_count = len(self.short_term_memories)
        self.short_term_memories = [
            m for m in self.short_term_memories
            if m.timestamp > cutoff_timestamp or m.importance >= min_importance
        ]
        count += original_count - len(self.short_term_memories)
        
        # Prune medium-term memories
        original_count = len(self.medium_term_memories)
        self.medium_term_memories = [
            m for m in self.medium_term_memories
            if m.timestamp > cutoff_timestamp or m.importance >= min_importance
        ]
        count += original_count - len(self.medium_term_memories)
        
        # Prune long-term memories (only for specified game or all games)
        if game_id:
            if game_id in self.long_term_memories:
                original_count = len(self.long_term_memories[game_id])
                self.long_term_memories[game_id] = [
                    m for m in self.long_term_memories[game_id]
                    if m.timestamp > cutoff_timestamp or m.importance >= min_importance
                ]
                count += original_count - len(self.long_term_memories[game_id])
                self._save_long_term_memories(game_id)
        else:
            for game_id in list(self.long_term_memories.keys()):
                original_count = len(self.long_term_memories[game_id])
                self.long_term_memories[game_id] = [
                    m for m in self.long_term_memories[game_id]
                    if m.timestamp > cutoff_timestamp or m.importance >= min_importance
                ]
                count += original_count - len(self.long_term_memories[game_id])
                self._save_long_term_memories(game_id)
        
        return count
    
    def get_relevant_context(self, 
                            game_id: str, 
                            query: str,
                            token_limit: int = 1000) -> str:
        """
        Get relevant context for an AI prompt based on query.
        
        Args:
            game_id: Game ID
            query: Query text to find relevant memories
            token_limit: Approximate maximum tokens in context
            
        Returns:
            Formatted context string
        """
        # First, get memories relevant to the query
        relevant_memories = self.get_memories(
            game_id=game_id,
            query=query,
            limit=15
        )
        
        # Also get important memories for general context
        important_memories = self.get_memories(
            game_id=game_id,
            min_importance=8,
            limit=5
        )
        
        # Combine and deduplicate
        all_memories = []
        memory_ids = set()
        
        for memory in relevant_memories + important_memories:
            if memory.id not in memory_ids:
                all_memories.append(memory)
                memory_ids.add(memory.id)
        
        if not all_memories:
            return ""
        
        # Format memories
        context_lines = ["## Relevant Memory Context"]
        
        for memory in all_memories:
            # Format by type
            memory_type = memory.type.value if isinstance(memory.type, MemoryType) else str(memory.type)
            display_type = memory_type.replace("_", " ").title()
            
            # Format timestamp to be more readable
            try:
                ts = datetime.fromisoformat(memory.timestamp)
                timestamp = ts.strftime("%Y-%m-%d %H:%M")
            except:
                timestamp = memory.timestamp
                
            context_lines.append(f"- [{display_type}] {memory.content} (Importance: {memory.importance}/10, Time: {timestamp})")
        
        # Apply token limiting (approx 4 chars per token)
        result = "\n".join(context_lines)
        if len(result) > token_limit * 4:
            result = result[:token_limit * 4] + "...\n[Context truncated due to length]"
        
        return result


# Global memory manager instance
memory_manager = MemoryManager()