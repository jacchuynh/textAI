"""
World State Persistence Manager

Main persistence management system that coordinates saving and loading
of all world state components including locations, containers, and player data.
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime
from enum import Enum

from .storage_backends import StorageBackend, JSONStorageBackend
from .serializers import (
    WorldStateSerializer,
    LocationState,
    ContainerState,
    PlayerState
)

logger = logging.getLogger(__name__)


class PersistenceEvent(Enum):
    """Events that trigger persistence operations."""
    LOCATION_CHANGED = "location_changed"
    ITEM_MOVED = "item_moved"
    CONTAINER_ACCESSED = "container_accessed"
    PLAYER_ACTION = "player_action"
    EQUIPMENT_CHANGED = "equipment_changed"
    SYSTEM_SHUTDOWN = "system_shutdown"
    PERIODIC_SAVE = "periodic_save"


class WorldStatePersistenceManager:
    """
    Main manager for world state persistence operations.
    
    Handles saving and loading of complete world state including:
    - Location states and item placements
    - Container contents and states
    - Player position and inventory
    - Cross-system state coordination
    """
    
    def __init__(
        self,
        storage_backend: Optional[StorageBackend] = None,
        auto_save_interval: int = 300,  # 5 minutes
        backup_interval: int = 3600    # 1 hour
    ):
        """
        Initialize the world state persistence manager.
        
        Args:
            storage_backend: Storage backend to use (defaults to JSON)
            auto_save_interval: Automatic save interval in seconds
            backup_interval: Backup creation interval in seconds
        """
        self.storage_backend = storage_backend or JSONStorageBackend()
        self.serializer = WorldStateSerializer()
        self.auto_save_interval = auto_save_interval
        self.backup_interval = backup_interval
        
        # Auto-save configuration
        self.auto_save_enabled = True
        self.min_changes_threshold = 1
        
        # Event handlers
        self.event_handlers: Dict[PersistenceEvent, List[Callable]] = {
            event: [] for event in PersistenceEvent
        }
        
        # State tracking
        self.current_game_id: Optional[str] = None
        self.last_save_time: Optional[datetime] = None
        self.last_backup_time: Optional[datetime] = None
        self.dirty_flags: Dict[str, bool] = {
            "locations": False,
            "containers": False,
            "player": False,
            "global": False
        }
        
        # Auto-save configuration
        self.auto_save_enabled = True
        self.min_changes_threshold = 1
        
        logger.info("World State Persistence Manager initialized")
    
    def register_event_handler(self, event: PersistenceEvent, handler: Callable):
        """
        Register an event handler for persistence events.
        
        Args:
            event: Event type to handle
            handler: Callback function to execute
        """
        self.event_handlers[event].append(handler)
        logger.debug(f"Registered handler for {event.value}")
    
    def trigger_event(self, event: PersistenceEvent, data: Optional[Dict[str, Any]] = None):
        """
        Trigger a persistence event and execute all registered handlers.
        
        Args:
            event: Event type to trigger
            data: Optional event data
        """
        try:
            for handler in self.event_handlers[event]:
                handler(data or {})
            logger.debug(f"Triggered {event.value} event")
        except Exception as e:
            logger.error(f"Error triggering {event.value} event: {e}")
    
    def start_session(self, game_id: str) -> bool:
        """
        Start a new persistence session for a game.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            True if session started successfully
        """
        try:
            self.current_game_id = game_id
            self.reset_dirty_flags()
            
            logger.info(f"Started persistence session for game {game_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start persistence session: {e}")
            return False
    
    def end_session(self, auto_save: bool = True) -> bool:
        """
        End the current persistence session.
        
        Args:
            auto_save: Whether to automatically save before ending
            
        Returns:
            True if session ended successfully
        """
        try:
            if auto_save and self.current_game_id:
                self.trigger_event(PersistenceEvent.SYSTEM_SHUTDOWN)
            
            self.current_game_id = None
            self.reset_dirty_flags()
            
            logger.info("Persistence session ended")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end persistence session: {e}")
            return False
    
    def save_world_state(self, world_state: Dict[str, Any], force: bool = False, partial: bool = False) -> bool:
        """
        Save the complete world state.
        
        Args:
            world_state: Complete world state data
            force: Force save even if no changes detected
            partial: Allow partial save for incremental updates
            
        Returns:
            True if save was successful
        """
        try:
            if not self.current_game_id:
                logger.error("No active persistence session")
                return False
            
            # Check if save is needed
            if not force and not self.is_save_needed():
                logger.debug("No changes detected, skipping save")
                return True
            
            # Validate world state (allow partial validation for incremental saves)
            if not self.serializer.validate_world_state(world_state, partial=partial):
                logger.error("World state validation failed")
                return False
            
            # For partial saves, merge with existing state if available
            final_world_state = world_state
            if partial and hasattr(self, '_cached_world_state') and self._cached_world_state:
                # Create a merged state for serialization
                final_world_state = self._cached_world_state.copy()
                final_world_state.update(world_state)
                logger.debug("Merged partial world state with cached state")
            
            # Serialize world state
            serialized_state = self.serializer.serialize_world_state(final_world_state)
            
            # Save to storage backend
            success = self.storage_backend.save_world_state(
                self.current_game_id,
                serialized_state
            )
            
            if success:
                self.last_save_time = datetime.now()
                self.reset_dirty_flags()
                logger.info(f"World state saved for game {self.current_game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to save world state: {e}")
            return False
    
    def load_world_state(self, game_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load the complete world state.
        
        Args:
            game_id: Game ID to load (uses current session if None)
            
        Returns:
            World state data if found, None otherwise
        """
        try:
            target_game_id = game_id or self.current_game_id
            if not target_game_id:
                logger.error("No game ID specified for loading")
                return None
            
            # Load from storage backend
            serialized_state = self.storage_backend.load_world_state(target_game_id)
            if not serialized_state:
                logger.info(f"No saved state found for game {target_game_id}")
                return None
            
            # Deserialize world state
            world_state = self.serializer.deserialize_world_state(serialized_state)
            
            # Validate loaded state
            if not self.serializer.validate_world_state(world_state):
                logger.error("Loaded world state validation failed")
                return None
            
            logger.info(f"World state loaded for game {target_game_id}")
            return world_state
            
        except Exception as e:
            logger.error(f"Failed to load world state: {e}")
            return None
    
    def save_location_state(self, location_id: str, location_data: Dict[str, Any]) -> bool:
        """
        Save state for a specific location.
        
        Args:
            location_id: Unique location identifier
            location_data: Location state data
            
        Returns:
            True if save was successful
        """
        try:
            # Create LocationState object
            location_state = LocationState(
                location_id=location_id,
                name=location_data.get("name", "Unknown Location"),
                description=location_data.get("description", ""),
                items=location_data.get("items", []),
                containers=location_data.get("containers", {}),
                visited=location_data.get("visited", False),
                last_visited=location_data.get("last_visited"),
                custom_properties=location_data.get("custom_properties", {})
            )
            
            # Mark location data as dirty
            self.mark_dirty("locations")
            
            # Trigger location changed event
            self.trigger_event(PersistenceEvent.LOCATION_CHANGED, {
                "location_id": location_id,
                "location_data": location_data
            })
            
            logger.debug(f"Location state saved for {location_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save location state for {location_id}: {e}")
            return False
    
    def save_container_state(self, container_id: str, container_data: Dict[str, Any]) -> bool:
        """
        Save state for a specific container.
        
        Args:
            container_id: Unique container identifier
            container_data: Container state data
            
        Returns:
            True if save was successful
        """
        try:
            # Create ContainerState object
            container_state = ContainerState(
                container_id=container_id,
                location_id=container_data.get("location_id", ""),
                container_type=container_data.get("container_type", "generic"),
                contents=container_data.get("contents", []),
                is_open=container_data.get("is_open", False),
                last_accessed=container_data.get("last_accessed"),
                custom_properties=container_data.get("custom_properties", {})
            )
            
            # Mark container data as dirty
            self.mark_dirty("containers")
            
            # Trigger container accessed event
            self.trigger_event(PersistenceEvent.CONTAINER_ACCESSED, {
                "container_id": container_id,
                "container_data": container_data
            })
            
            logger.debug(f"Container state saved for {container_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save container state for {container_id}: {e}")
            return False
    
    def save_player_state(self, player_data: Dict[str, Any]) -> bool:
        """
        Save player state data.
        
        Args:
            player_data: Player state data
            
        Returns:
            True if save was successful
        """
        try:
            # Create PlayerState object
            player_state = PlayerState(
                player_id=player_data.get("player_id", ""),
                current_location=player_data.get("current_location", ""),
                inventory=player_data.get("inventory", []),
                equipped_items=player_data.get("equipped_items", {}),
                stats=player_data.get("stats", {}),
                discovered_locations=set(player_data.get("discovered_locations", [])),
                last_save=datetime.now().isoformat(),
                custom_data=player_data.get("custom_data", {})
            )
            
            # Mark player data as dirty
            self.mark_dirty("player")
            
            # Trigger player action event
            self.trigger_event(PersistenceEvent.PLAYER_ACTION, {
                "player_data": player_data
            })
            
            logger.debug(f"Player state saved for {player_state.player_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save player state: {e}")
            return False
    
    def mark_dirty(self, section: str):
        """Mark a section as dirty (needs saving)."""
        if section in self.dirty_flags:
            self.dirty_flags[section] = True
            logger.debug(f"Marked {section} as dirty")
    
    def reset_dirty_flags(self):
        """Reset all dirty flags."""
        for section in self.dirty_flags:
            self.dirty_flags[section] = False
    
    def is_save_needed(self) -> bool:
        """Check if any data needs to be saved."""
        return any(self.dirty_flags.values())
    
    def create_backup(self) -> bool:
        """
        Create a backup of the current world state.
        
        Returns:
            True if backup was successful
        """
        try:
            if not self.current_game_id:
                logger.error("No active session for backup")
                return False
            
            success = self.storage_backend.backup_world_state(self.current_game_id)
            if success:
                self.last_backup_time = datetime.now()
                logger.info(f"Backup created for game {self.current_game_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def auto_save_check(self, world_state: Dict[str, Any]) -> bool:
        """
        Check if automatic save should be triggered and perform it if needed.
        
        Args:
            world_state: Current world state (may be partial)
            
        Returns:
            True if auto-save was performed
        """
        try:
            # Check if auto-save should be triggered
            should_save, save_reason = self.should_auto_save()
            save_performed = False
            
            if should_save:
                logger.info(f"Triggering auto-save: {save_reason}")
                self.trigger_event(PersistenceEvent.PERIODIC_SAVE)
                
                # Ensure we have a valid world state structure for auto-save
                if not world_state or not isinstance(world_state, dict):
                    world_state = {}
                
                # Use partial save for auto-save operations to handle incomplete state
                save_performed = self.save_world_state(world_state, partial=True)
                
                if save_performed:
                    logger.info("Auto-save completed successfully")
                else:
                    logger.warning("Auto-save failed")
            
            # Check if backup should be created
            should_backup, backup_reason = self.should_backup()
            
            if should_backup:
                logger.info(f"Triggering backup: {backup_reason}")
                backup_success = self.create_backup()
                
                if backup_success:
                    logger.info("Backup completed successfully")
                else:
                    logger.warning("Backup failed")
            
            return save_performed
            
        except Exception as e:
            logger.error(f"Auto-save check failed: {e}")
            return False
    
    def get_save_info(self, game_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a saved game.
        
        Args:
            game_id: Game ID to check (uses current session if None)
            
        Returns:
            Save information dictionary
        """
        try:
            target_game_id = game_id or self.current_game_id
            if not target_game_id:
                return None
            
            saved_states = self.storage_backend.list_saved_states()
            if target_game_id not in saved_states:
                return None
            
            # Try to load metadata
            serialized_state = self.storage_backend.load_world_state(target_game_id)
            if not serialized_state:
                return None
            
            metadata = serialized_state.get("metadata", {})
            
            return {
                "game_id": target_game_id,
                "has_save": True,
                "last_saved": metadata.get("serialized_at"),
                "version": metadata.get("version"),
                "serializer": metadata.get("serializer")
            }
            
        except Exception as e:
            logger.error(f"Failed to get save info: {e}")
            return None
    
    def list_saved_games(self) -> List[Dict[str, Any]]:
        """
        List all saved games with their information.
        
        Returns:
            List of saved game information dictionaries
        """
        try:
            saved_states = self.storage_backend.list_saved_states()
            games_info = []
            
            for game_id in saved_states:
                info = self.get_save_info(game_id)
                if info:
                    games_info.append(info)
            
            return games_info
            
        except Exception as e:
            logger.error(f"Failed to list saved games: {e}")
            return []
    
    def configure_auto_save(self, 
                           enabled: bool = True, 
                           interval_seconds: int = 300, 
                           backup_interval_seconds: int = 3600,
                           min_changes_threshold: int = 1) -> bool:
        """
        Configure auto-save behavior and timing.
        
        Args:
            enabled: Whether auto-save is enabled
            interval_seconds: Auto-save interval in seconds (default: 5 minutes)
            backup_interval_seconds: Backup interval in seconds (default: 1 hour)
            min_changes_threshold: Minimum changes before triggering save (default: 1)
            
        Returns:
            True if configuration was successful
        """
        try:
            self.auto_save_enabled = enabled
            self.auto_save_interval = interval_seconds
            self.backup_interval = backup_interval_seconds
            self.min_changes_threshold = min_changes_threshold
            
            logger.info(f"Auto-save configured: enabled={enabled}, interval={interval_seconds}s, "
                       f"backup_interval={backup_interval_seconds}s, threshold={min_changes_threshold}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure auto-save: {e}")
            return False
    
    def should_auto_save(self) -> Tuple[bool, str]:
        """
        Check if auto-save should be triggered based on current conditions.
        
        Returns:
            Tuple of (should_save, reason)
        """
        if not getattr(self, 'auto_save_enabled', True):
            return False, "Auto-save disabled"
        
        if not self.current_game_id:
            return False, "No active session"
        
        if not self.is_save_needed():
            return False, "No changes detected"
        
        now = datetime.now()
        
        # Check time-based trigger
        if self.last_save_time:
            time_since_save = (now - self.last_save_time).total_seconds()
            if time_since_save >= self.auto_save_interval:
                return True, f"Time interval reached ({time_since_save:.1f}s >= {self.auto_save_interval}s)"
        else:
            # No previous save, trigger if there are changes
            return True, "First save with changes detected"
        
        # Check change threshold (if configured)
        min_threshold = getattr(self, 'min_changes_threshold', 1)
        dirty_count = sum(1 for flag in self.dirty_flags.values() if flag)
        if dirty_count >= min_threshold:
            return True, f"Change threshold met ({dirty_count} >= {min_threshold})"
        
        return False, "Conditions not met"
    
    def should_backup(self) -> Tuple[bool, str]:
        """
        Check if backup should be created based on current conditions.
        
        Returns:
            Tuple of (should_backup, reason)
        """
        if not self.current_game_id:
            return False, "No active session"
        
        now = datetime.now()
        
        if self.last_backup_time:
            time_since_backup = (now - self.last_backup_time).total_seconds()
            if time_since_backup >= self.backup_interval:
                return True, f"Backup interval reached ({time_since_backup:.1f}s >= {self.backup_interval}s)"
        else:
            # No previous backup, create one if we have a save
            if self.last_save_time:
                return True, "First backup after initial save"
        
        return False, "Backup interval not reached"
    
    def start_auto_save_timer(self, check_interval: int = 60) -> bool:
        """
        Start a background timer for periodic auto-save checking.
        
        Args:
            check_interval: Interval between auto-save checks in seconds (default: 1 minute)
            
        Returns:
            True if timer started successfully
        """
        try:
            import threading
            import time
            
            def auto_save_worker():
                """Background worker for auto-save checking."""
                while getattr(self, '_auto_save_running', False):
                    try:
                        if self.current_game_id:
                            # Get current world state from shared context if available
                            world_state = getattr(self, '_cached_world_state', {})
                            if world_state:
                                self.auto_save_check(world_state)
                        
                        time.sleep(check_interval)
                        
                    except Exception as e:
                        logger.error(f"Auto-save worker error: {e}")
                        time.sleep(check_interval)  # Continue despite errors
            
            # Start the auto-save timer
            self._auto_save_running = True
            self._auto_save_thread = threading.Thread(target=auto_save_worker, daemon=True)
            self._auto_save_thread.start()
            
            logger.info(f"Auto-save timer started (check interval: {check_interval}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start auto-save timer: {e}")
            return False
    
    def stop_auto_save_timer(self) -> bool:
        """
        Stop the background auto-save timer.
        
        Returns:
            True if timer stopped successfully
        """
        try:
            if hasattr(self, '_auto_save_running'):
                self._auto_save_running = False
                logger.info("Auto-save timer stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop auto-save timer: {e}")
            return False
    
    def update_cached_world_state(self, world_state: Dict[str, Any]):
        """
        Update the cached world state for auto-save operations.
        
        Args:
            world_state: Current world state to cache
        """
        self._cached_world_state = world_state.copy()
