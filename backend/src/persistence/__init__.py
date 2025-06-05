"""
Persistence Module for TextRealmsAI

This module provides comprehensive world state persistence functionality,
including save/load of location states, container contents, and player positions.
"""

from .world_state_persistence import WorldStatePersistenceManager
from .serializers import (
    LocationStateSerializer,
    ContainerStateSerializer,
    PlayerStateSerializer,
    WorldStateSerializer
)
from .storage_backends import (
    JSONStorageBackend,
    StorageBackend
)

__all__ = [
    'WorldStatePersistenceManager',
    'LocationStateSerializer',
    'ContainerStateSerializer', 
    'PlayerStateSerializer',
    'WorldStateSerializer',
    'JSONStorageBackend',
    'StorageBackend'
]
