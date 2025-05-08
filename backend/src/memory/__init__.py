"""
Memory management module for the game engine.

This module provides:
1. Three-tier memory system (short/medium/long-term)
2. Game state compression utilities
3. Priority-based memory retrieval
4. Event-driven memory creation and management
"""

from .memory_manager import memory_manager, MemoryEntry, MemoryTier, MemoryType
from .state_compression import StateCompressor, PriorityStateQueue
from .memory_connector import memory_connector

__all__ = [
    "memory_manager", "MemoryEntry", "MemoryTier", "MemoryType",
    "StateCompressor", "PriorityStateQueue", "memory_connector"
]