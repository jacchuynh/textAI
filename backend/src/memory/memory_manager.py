"""
Memory Manager

This module provides a tiered memory system for storing and retrieving
game state, player actions, and narrative history.
"""

import os
import json
import pickle
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime, timedelta


class MemoryTier(Enum):
    """Tiers of memory with different characteristics."""
    WORKING = auto()   # Short-term, high detail, small capacity
    RECENT = auto()    # Medium-term, moderate detail, medium capacity
    ARCHIVAL = auto()  # Long-term, compressed, large capacity


class MemoryType(Enum):
    """Types of memories that can be stored."""
    PLAYER_ACTION = auto()
    NPC_INTERACTION = auto()
    LOCATION = auto()
    ITEM = auto()
    QUEST = auto()
    COMBAT = auto()
    NARRATIVE = auto()
    SYSTEM = auto()


class MemoryEntry:
    """A single memory entry with metadata."""
    
    def __init__(self,
                 memory_type: MemoryType,
                 content: Dict[str, Any],
                 importance: float = 0.5,
                 entry_id: str = None,
                 timestamp: datetime = None,
                 tags: List[str] = None):
        """
        Initialize a memory entry.
        
        Args:
            memory_type: Type of memory
            content: Memory content
            importance: Importance score (0.0 to 1.0)
            entry_id: Unique ID for the memory
            timestamp: When the memory was formed
            tags: Tags for categorizing the memory
        """
        import uuid
        self.id = entry_id or str(uuid.uuid4())
        self.type = memory_type
        self.content = content
        self.importance = max(0.0, min(1.0, importance))  # Clamp to [0, 1]
        self.timestamp = timestamp or datetime.utcnow()
        self.tags = tags or []
        self.retrieval_count = 0
        self.last_accessed = self.timestamp
    
    def __repr__(self) -> str:
        return f"Memory({self.id[:8]}, {self.type.name}, importance={self.importance:.2f})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.name,
            "content": self.content,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "retrieval_count": self.retrieval_count,
            "last_accessed": self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create a memory entry from a dictionary."""
        return cls(
            memory_type=MemoryType[data["type"]],
            content=data["content"],
            importance=data["importance"],
            entry_id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            tags=data.get("tags", [])
        )


class MemoryManager:
    """
    Manages the storage and retrieval of game memories across different tiers.
    
    This implements a three-tier memory system:
    - Working memory: Recent, high-detail memories (last ~1 hour)
    - Recent memory: Medium-term memories (last ~1 day)
    - Archival memory: Long-term, compressed memories (entire game history)
    """
    
    def __init__(self, game_id: str):
        """
        Initialize the memory manager.
        
        Args:
            game_id: Unique ID for the game session
        """
        self.game_id = game_id
        self.working_memory: Dict[str, MemoryEntry] = {}
        self.recent_memory: Dict[str, MemoryEntry] = {}
        self.archival_memory: Dict[str, MemoryEntry] = {}
        
        # Thresholds for importance
        self.working_to_recent_threshold = 0.3
        self.recent_to_archival_threshold = 0.2
        
        # Time thresholds for automatic memory movement
        self.working_memory_max_age = timedelta(hours=1)
        self.recent_memory_max_age = timedelta(days=1)
        
        # Capacity limits (set to -1 for unlimited)
        self.working_memory_capacity = 100
        self.recent_memory_capacity = 1000
        self.archival_memory_capacity = -1
        
        # Memory file paths
        self.memory_dir = os.path.join("data", "memory", game_id)
        self.working_memory_file = os.path.join(self.memory_dir, "working_memory.json")
        self.recent_memory_file = os.path.join(self.memory_dir, "recent_memory.json")
        self.archival_memory_file = os.path.join(self.memory_dir, "archival_memory.pkl")
        
        # Create directory if it doesn't exist
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Load existing memories
        self._load_memories()
    
    def _load_memories(self) -> None:
        """Load memories from disk."""
        # Load working memory
        if os.path.exists(self.working_memory_file):
            try:
                with open(self.working_memory_file, 'r') as f:
                    data = json.load(f)
                    for entry_data in data:
                        entry = MemoryEntry.from_dict(entry_data)
                        self.working_memory[entry.id] = entry
            except Exception as e:
                print(f"Error loading working memory: {e}")
        
        # Load recent memory
        if os.path.exists(self.recent_memory_file):
            try:
                with open(self.recent_memory_file, 'r') as f:
                    data = json.load(f)
                    for entry_data in data:
                        entry = MemoryEntry.from_dict(entry_data)
                        self.recent_memory[entry.id] = entry
            except Exception as e:
                print(f"Error loading recent memory: {e}")
        
        # Load archival memory
        if os.path.exists(self.archival_memory_file):
            try:
                with open(self.archival_memory_file, 'rb') as f:
                    self.archival_memory = pickle.load(f)
            except Exception as e:
                print(f"Error loading archival memory: {e}")
    
    def _save_memories(self) -> None:
        """Save memories to disk."""
        # Save working memory
        try:
            with open(self.working_memory_file, 'w') as f:
                json.dump([entry.to_dict() for entry in self.working_memory.values()], f, indent=2)
        except Exception as e:
            print(f"Error saving working memory: {e}")
        
        # Save recent memory
        try:
            with open(self.recent_memory_file, 'w') as f:
                json.dump([entry.to_dict() for entry in self.recent_memory.values()], f, indent=2)
        except Exception as e:
            print(f"Error saving recent memory: {e}")
        
        # Save archival memory
        try:
            with open(self.archival_memory_file, 'wb') as f:
                pickle.dump(self.archival_memory, f)
        except Exception as e:
            print(f"Error saving archival memory: {e}")
    
    def add_memory(self, 
                  memory_type: MemoryType, 
                  content: Dict[str, Any],
                  importance: float = 0.5,
                  tags: List[str] = None) -> str:
        """
        Add a new memory to the system.
        
        Args:
            memory_type: Type of memory
            content: Memory content
            importance: Importance score (0.0 to 1.0)
            tags: Tags for categorizing the memory
            
        Returns:
            ID of the created memory
        """
        memory = MemoryEntry(
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags
        )
        
        # Determine which tier to store in based on importance
        if importance >= self.working_to_recent_threshold:
            self.working_memory[memory.id] = memory
            
            # Check if we need to move memories out
            if (self.working_memory_capacity > 0 and 
                len(self.working_memory) > self.working_memory_capacity):
                self._consolidate_working_memory()
        else:
            self.recent_memory[memory.id] = memory
            
            # Check if we need to move memories out
            if (self.recent_memory_capacity > 0 and
                len(self.recent_memory) > self.recent_memory_capacity):
                self._consolidate_recent_memory()
        
        # Save to disk
        self._save_memories()
        
        return memory.id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory entry if found, None otherwise
        """
        # Check working memory first
        if memory_id in self.working_memory:
            memory = self.working_memory[memory_id]
            memory.retrieval_count += 1
            memory.last_accessed = datetime.utcnow()
            return memory
        
        # Check recent memory
        if memory_id in self.recent_memory:
            memory = self.recent_memory[memory_id]
            memory.retrieval_count += 1
            memory.last_accessed = datetime.utcnow()
            
            # If memory is important enough, move it to working memory
            if memory.importance >= self.working_to_recent_threshold:
                self.working_memory[memory_id] = memory
                del self.recent_memory[memory_id]
            
            return memory
        
        # Check archival memory
        if memory_id in self.archival_memory:
            memory = self.archival_memory[memory_id]
            memory.retrieval_count += 1
            memory.last_accessed = datetime.utcnow()
            
            # If memory is important enough, move it to recent memory
            if memory.importance >= self.recent_to_archival_threshold:
                self.recent_memory[memory_id] = memory
                del self.archival_memory[memory_id]
            
            return memory
        
        return None
    
    def find_memories(self,
                     memory_type: Optional[MemoryType] = None,
                     tags: Optional[List[str]] = None,
                     min_importance: float = 0.0,
                     time_range: Optional[tuple] = None,
                     include_tiers: Set[MemoryTier] = None,
                     limit: int = 10) -> List[MemoryEntry]:
        """
        Find memories matching the specified criteria.
        
        Args:
            memory_type: Type of memory to find
            tags: Tags that memories must have (AND logic)
            min_importance: Minimum importance score
            time_range: Tuple of (start_time, end_time) to filter by
            include_tiers: Set of memory tiers to search in
            limit: Maximum number of memories to return
            
        Returns:
            List of matching memory entries
        """
        if include_tiers is None:
            include_tiers = {MemoryTier.WORKING, MemoryTier.RECENT, MemoryTier.ARCHIVAL}
        
        results = []
        current_time = datetime.utcnow()
        
        # Helper function to check if a memory matches criteria
        def matches_criteria(memory: MemoryEntry) -> bool:
            if memory_type and memory.type != memory_type:
                return False
            
            if memory.importance < min_importance:
                return False
            
            if tags and not all(tag in memory.tags for tag in tags):
                return False
            
            if time_range:
                start_time, end_time = time_range
                if start_time and memory.timestamp < start_time:
                    return False
                if end_time and memory.timestamp > end_time:
                    return False
            
            return True
        
        # Check working memory
        if MemoryTier.WORKING in include_tiers:
            for memory in self.working_memory.values():
                if matches_criteria(memory):
                    results.append(memory)
        
        # Check recent memory if we haven't hit the limit
        if MemoryTier.RECENT in include_tiers and len(results) < limit:
            for memory in self.recent_memory.values():
                if matches_criteria(memory):
                    results.append(memory)
                    if len(results) >= limit:
                        break
        
        # Check archival memory if we haven't hit the limit
        if MemoryTier.ARCHIVAL in include_tiers and len(results) < limit:
            for memory in self.archival_memory.values():
                if matches_criteria(memory):
                    results.append(memory)
                    if len(results) >= limit:
                        break
        
        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        
        # Update access times and counts
        for memory in results:
            memory.retrieval_count += 1
            memory.last_accessed = current_time
        
        return results[:limit]
    
    def update_memory(self, 
                     memory_id: str, 
                     content: Optional[Dict[str, Any]] = None,
                     importance: Optional[float] = None,
                     tags: Optional[List[str]] = None) -> bool:
        """
        Update an existing memory.
        
        Args:
            memory_id: ID of the memory to update
            content: New content (if None, content is not updated)
            importance: New importance score (if None, importance is not updated)
            tags: New tags (if None, tags are not updated)
            
        Returns:
            True if memory was found and updated, False otherwise
        """
        memory = self.get_memory(memory_id)
        
        if not memory:
            return False
        
        if content is not None:
            memory.content = content
        
        if importance is not None:
            memory.importance = max(0.0, min(1.0, importance))
        
        if tags is not None:
            memory.tags = tags
        
        # Save to disk
        self._save_memories()
        
        return True
    
    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove a memory from the system.
        
        Args:
            memory_id: ID of the memory to remove
            
        Returns:
            True if memory was found and removed, False otherwise
        """
        if memory_id in self.working_memory:
            del self.working_memory[memory_id]
            self._save_memories()
            return True
        
        if memory_id in self.recent_memory:
            del self.recent_memory[memory_id]
            self._save_memories()
            return True
        
        if memory_id in self.archival_memory:
            del self.archival_memory[memory_id]
            self._save_memories()
            return True
        
        return False
    
    def _consolidate_working_memory(self) -> None:
        """Move less important memories from working to recent memory."""
        # Sort memories by importance and recency
        sorted_memories = sorted(
            self.working_memory.values(),
            key=lambda m: (m.importance, (datetime.utcnow() - m.timestamp).total_seconds()),
        )
        
        # Move excess memories to recent memory
        excess_count = len(self.working_memory) - self.working_memory_capacity
        for i in range(excess_count):
            memory = sorted_memories[i]
            self.recent_memory[memory.id] = memory
            del self.working_memory[memory.id]
        
        # Also move old memories regardless of importance
        for memory_id, memory in list(self.working_memory.items()):
            if datetime.utcnow() - memory.timestamp > self.working_memory_max_age:
                self.recent_memory[memory_id] = memory
                del self.working_memory[memory_id]
    
    def _consolidate_recent_memory(self) -> None:
        """Move less important memories from recent to archival memory."""
        # Sort memories by importance and recency
        sorted_memories = sorted(
            self.recent_memory.values(),
            key=lambda m: (m.importance, (datetime.utcnow() - m.timestamp).total_seconds()),
        )
        
        # Move excess memories to archival memory
        excess_count = len(self.recent_memory) - self.recent_memory_capacity
        for i in range(excess_count):
            memory = sorted_memories[i]
            self.archival_memory[memory.id] = memory
            del self.recent_memory[memory.id]
        
        # Also move old memories regardless of importance
        for memory_id, memory in list(self.recent_memory.items()):
            if datetime.utcnow() - memory.timestamp > self.recent_memory_max_age:
                self.archival_memory[memory_id] = memory
                del self.recent_memory[memory_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        return {
            "working_memory_count": len(self.working_memory),
            "recent_memory_count": len(self.recent_memory),
            "archival_memory_count": len(self.archival_memory),
            "total_memory_count": len(self.working_memory) + len(self.recent_memory) + len(self.archival_memory),
            "working_memory_capacity": self.working_memory_capacity,
            "recent_memory_capacity": self.recent_memory_capacity,
            "archival_memory_capacity": self.archival_memory_capacity
        }
    
    def clear_all_memories(self) -> None:
        """Clear all memories (use with caution)."""
        self.working_memory.clear()
        self.recent_memory.clear()
        self.archival_memory.clear()
        self._save_memories()


# Singleton instance for the default game
memory_manager = MemoryManager("default_game")