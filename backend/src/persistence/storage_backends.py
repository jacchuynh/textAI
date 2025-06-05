"""
Storage Backend Interfaces and Implementations

Provides different storage backend options for world state persistence.
"""

import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save_world_state(self, game_id: str, world_state: Dict[str, Any]) -> bool:
        """Save world state data."""
        pass
    
    @abstractmethod
    def load_world_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Load world state data."""
        pass
    
    @abstractmethod
    def delete_world_state(self, game_id: str) -> bool:
        """Delete world state data."""
        pass
    
    @abstractmethod
    def list_saved_states(self) -> List[str]:
        """List all saved game states."""
        pass
    
    @abstractmethod
    def backup_world_state(self, game_id: str) -> bool:
        """Create a backup of world state."""
        pass


class JSONStorageBackend(StorageBackend):
    """JSON file-based storage backend."""
    
    def __init__(self, storage_dir: str = "game_saves"):
        """
        Initialize JSON storage backend.
        
        Args:
            storage_dir: Directory to store save files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.storage_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"JSON storage backend initialized at {self.storage_dir}")
    
    def _get_save_path(self, game_id: str) -> Path:
        """Get the save file path for a game."""
        return self.storage_dir / f"{game_id}_world_state.json"
    
    def _get_backup_path(self, game_id: str, timestamp: str = None) -> Path:
        """Get the backup file path for a game."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.backup_dir / f"{game_id}_world_state_backup_{timestamp}.json"
    
    def save_world_state(self, game_id: str, world_state: Dict[str, Any]) -> bool:
        """
        Save world state to JSON file.
        
        Args:
            game_id: Unique game identifier
            world_state: World state data to save
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            save_path = self._get_save_path(game_id)
            
            # Create backup if file exists
            if save_path.exists():
                self.backup_world_state(game_id)
            
            # Add metadata
            save_data = {
                "metadata": {
                    "game_id": game_id,
                    "saved_at": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "world_state": world_state
            }
            
            # Write to temporary file first, then move (atomic operation)
            temp_path = save_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            # Atomic move
            temp_path.rename(save_path)
            
            logger.info(f"World state saved successfully for game {game_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save world state for game {game_id}: {e}")
            return False
    
    def load_world_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Load world state from JSON file.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            World state data if found, None otherwise
        """
        try:
            save_path = self._get_save_path(game_id)
            
            if not save_path.exists():
                logger.info(f"No save file found for game {game_id}")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Validate save data structure
            if "world_state" not in save_data:
                logger.error(f"Invalid save file format for game {game_id}")
                return None
            
            logger.info(f"World state loaded successfully for game {game_id}")
            return save_data["world_state"]
            
        except Exception as e:
            logger.error(f"Failed to load world state for game {game_id}: {e}")
            return None
    
    def delete_world_state(self, game_id: str) -> bool:
        """
        Delete world state file.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            save_path = self._get_save_path(game_id)
            
            if save_path.exists():
                save_path.unlink()
                logger.info(f"World state deleted for game {game_id}")
                return True
            else:
                logger.warning(f"No save file to delete for game {game_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete world state for game {game_id}: {e}")
            return False
    
    def list_saved_states(self) -> List[str]:
        """
        List all saved game states.
        
        Returns:
            List of game IDs with saved states
        """
        try:
            game_ids = []
            for file_path in self.storage_dir.glob("*_world_state.json"):
                game_id = file_path.stem.replace("_world_state", "")
                game_ids.append(game_id)
            
            logger.info(f"Found {len(game_ids)} saved game states")
            return game_ids
            
        except Exception as e:
            logger.error(f"Failed to list saved states: {e}")
            return []
    
    def backup_world_state(self, game_id: str) -> bool:
        """
        Create a backup of world state.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            save_path = self._get_save_path(game_id)
            
            if not save_path.exists():
                logger.warning(f"No save file to backup for game {game_id}")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self._get_backup_path(game_id, timestamp)
            
            # Copy file to backup location
            import shutil
            shutil.copy2(save_path, backup_path)
            
            logger.info(f"Backup created for game {game_id} at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup world state for game {game_id}: {e}")
            return False
    
    def cleanup_old_backups(self, game_id: str, keep_count: int = 10) -> int:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            game_id: Unique game identifier
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        try:
            pattern = f"{game_id}_world_state_backup_*.json"
            backup_files = list(self.backup_dir.glob(pattern))
            
            if len(backup_files) <= keep_count:
                return 0
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Delete old backups
            deleted_count = 0
            for backup_file in backup_files[keep_count:]:
                backup_file.unlink()
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backups for game {game_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup backups for game {game_id}: {e}")
            return 0
