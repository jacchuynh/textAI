"""
Serializers for World State Components

Provides serialization and deserialization functionality for different
world state components like locations, containers, and player states.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class LocationState:
    """Represents the state of a location."""
    location_id: str
    name: str
    description: str
    items: List[Dict[str, Any]]
    containers: Dict[str, Dict[str, Any]]
    visited: bool
    last_visited: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None


@dataclass
class ContainerState:
    """Represents the state of a container."""
    container_id: str
    location_id: str
    container_type: str
    contents: List[Dict[str, Any]]
    is_open: bool
    last_accessed: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None


@dataclass
class PlayerState:
    """Represents the player's state."""
    player_id: str
    current_location: str
    inventory: List[Dict[str, Any]]
    equipped_items: Dict[str, Dict[str, Any]]
    stats: Dict[str, Any]
    discovered_locations: Set[str]
    last_save: str
    custom_data: Optional[Dict[str, Any]] = None


class StateSerializer(ABC):
    """Abstract base class for state serializers."""
    
    @abstractmethod
    def serialize(self, obj: Any) -> Dict[str, Any]:
        """Serialize an object to a dictionary."""
        pass
    
    @abstractmethod
    def deserialize(self, data: Dict[str, Any]) -> Any:
        """Deserialize a dictionary to an object."""
        pass


class LocationStateSerializer(StateSerializer):
    """Serializer for location states."""
    
    def serialize(self, location_state: LocationState) -> Dict[str, Any]:
        """
        Serialize a LocationState object.
        
        Args:
            location_state: LocationState object to serialize
            
        Returns:
            Dictionary representation of the location state
        """
        try:
            data = asdict(location_state)
            # Ensure datetime fields are properly serialized
            if location_state.last_visited:
                data['last_visited'] = location_state.last_visited
            
            logger.debug(f"Serialized location state for {location_state.location_id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to serialize location state: {e}")
            raise
    
    def deserialize(self, data: Dict[str, Any]) -> LocationState:
        """
        Deserialize a dictionary to a LocationState object.
        
        Args:
            data: Dictionary data to deserialize
            
        Returns:
            LocationState object
        """
        try:
            # Handle optional fields
            data.setdefault('custom_properties', {})
            
            location_state = LocationState(**data)
            logger.debug(f"Deserialized location state for {location_state.location_id}")
            return location_state
            
        except Exception as e:
            logger.error(f"Failed to deserialize location state: {e}")
            raise
    
    def serialize_multiple(self, location_states: List[LocationState]) -> List[Dict[str, Any]]:
        """Serialize multiple location states."""
        return [self.serialize(state) for state in location_states]
    
    def deserialize_multiple(self, data_list: List[Dict[str, Any]]) -> List[LocationState]:
        """Deserialize multiple location states."""
        return [self.deserialize(data) for data in data_list]


class ContainerStateSerializer(StateSerializer):
    """Serializer for container states."""
    
    def serialize(self, container_state: ContainerState) -> Dict[str, Any]:
        """
        Serialize a ContainerState object.
        
        Args:
            container_state: ContainerState object to serialize
            
        Returns:
            Dictionary representation of the container state
        """
        try:
            data = asdict(container_state)
            logger.debug(f"Serialized container state for {container_state.container_id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to serialize container state: {e}")
            raise
    
    def deserialize(self, data: Dict[str, Any]) -> ContainerState:
        """
        Deserialize a dictionary to a ContainerState object.
        
        Args:
            data: Dictionary data to deserialize
            
        Returns:
            ContainerState object
        """
        try:
            # Handle optional fields
            data.setdefault('custom_properties', {})
            
            container_state = ContainerState(**data)
            logger.debug(f"Deserialized container state for {container_state.container_id}")
            return container_state
            
        except Exception as e:
            logger.error(f"Failed to deserialize container state: {e}")
            raise
    
    def serialize_multiple(self, container_states: List[ContainerState]) -> List[Dict[str, Any]]:
        """Serialize multiple container states."""
        return [self.serialize(state) for state in container_states]
    
    def deserialize_multiple(self, data_list: List[Dict[str, Any]]) -> List[ContainerState]:
        """Deserialize multiple container states."""
        return [self.deserialize(data) for data in data_list]


class PlayerStateSerializer(StateSerializer):
    """Serializer for player states."""
    
    def serialize(self, player_state: PlayerState) -> Dict[str, Any]:
        """
        Serialize a PlayerState object.
        
        Args:
            player_state: PlayerState object to serialize
            
        Returns:
            Dictionary representation of the player state
        """
        try:
            data = asdict(player_state)
            # Convert set to list for JSON serialization
            data['discovered_locations'] = list(player_state.discovered_locations)
            
            logger.debug(f"Serialized player state for {player_state.player_id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to serialize player state: {e}")
            raise
    
    def deserialize(self, data: Dict[str, Any]) -> PlayerState:
        """
        Deserialize a dictionary to a PlayerState object.
        
        Args:
            data: Dictionary data to deserialize
            
        Returns:
            PlayerState object
        """
        try:
            # Convert list back to set
            if 'discovered_locations' in data:
                data['discovered_locations'] = set(data['discovered_locations'])
            else:
                data['discovered_locations'] = set()
            
            # Handle optional fields
            data.setdefault('custom_data', {})
            
            # Filter data to only include fields that PlayerState expects
            valid_fields = {
                'player_id', 'current_location', 'inventory', 'equipped_items', 
                'stats', 'discovered_locations', 'last_save', 'custom_data'
            }
            
            # Store extra fields in custom_data if they don't belong to PlayerState
            extra_fields = {}
            filtered_data = {}
            
            for key, value in data.items():
                if key in valid_fields:
                    filtered_data[key] = value
                else:
                    extra_fields[key] = value
            
            # Merge extra fields into custom_data
            if extra_fields:
                if 'custom_data' not in filtered_data:
                    filtered_data['custom_data'] = {}
                filtered_data['custom_data'].update(extra_fields)
            
            # Ensure required fields have defaults
            filtered_data.setdefault('inventory', [])
            filtered_data.setdefault('equipped_items', {})
            filtered_data.setdefault('stats', {})
            filtered_data.setdefault('last_save', datetime.now().isoformat())
            
            player_state = PlayerState(**filtered_data)
            logger.debug(f"Deserialized player state for {player_state.player_id}")
            return player_state
            
        except Exception as e:
            logger.error(f"Failed to deserialize player state: {e}")
            raise


class WorldStateSerializer:
    """Main serializer for complete world state."""
    
    def __init__(self):
        self.location_serializer = LocationStateSerializer()
        self.container_serializer = ContainerStateSerializer()
        self.player_serializer = PlayerStateSerializer()
    
    def serialize_world_state(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize complete world state.
        
        Args:
            world_state: World state dictionary containing all game data
            
        Returns:
            Serialized world state dictionary
        """
        try:
            # Initialize serialized structure based on what's actually in world_state
            serialized = {
                "metadata": {
                    "serialized_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "serializer": "WorldStateSerializer"
                }
            }
            
            # Only include sections that exist in the input world_state
            # Serialize locations
            if "locations" in world_state:
                serialized["locations"] = {}
                for location_id, location_data in world_state["locations"].items():
                    if isinstance(location_data, LocationState):
                        serialized["locations"][location_id] = self.location_serializer.serialize(location_data)
                    else:
                        serialized["locations"][location_id] = location_data
            
            # Serialize containers
            if "containers" in world_state:
                serialized["containers"] = {}
                for container_id, container_data in world_state["containers"].items():
                    if isinstance(container_data, ContainerState):
                        serialized["containers"][container_id] = self.container_serializer.serialize(container_data)
                    else:
                        serialized["containers"][container_id] = container_data
            
            # Serialize player state
            if "player" in world_state:
                player_data = world_state["player"]
                if isinstance(player_data, PlayerState):
                    serialized["player"] = self.player_serializer.serialize(player_data)
                else:
                    serialized["player"] = player_data
            
            # Create global_state section for other data
            global_state = {}
            for key, value in world_state.items():
                if key not in ["locations", "containers", "player"]:
                    global_state[key] = value
            
            if global_state:
                serialized["global_state"] = global_state
            
            logger.info("World state serialized successfully")
            return serialized
            
        except Exception as e:
            logger.error(f"Failed to serialize world state: {e}")
            raise
    
    def deserialize_world_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize complete world state.
        
        Args:
            data: Serialized world state data
            
        Returns:
            Deserialized world state dictionary
        """
        try:
            world_state = {}
            
            # Deserialize locations
            if "locations" in data:
                world_state["locations"] = {}
                for location_id, location_data in data["locations"].items():
                    try:
                        world_state["locations"][location_id] = self.location_serializer.deserialize(location_data)
                    except Exception as e:
                        logger.warning(f"Failed to deserialize location {location_id}: {e}")
                        world_state["locations"][location_id] = location_data
            
            # Deserialize containers
            if "containers" in data:
                world_state["containers"] = {}
                for container_id, container_data in data["containers"].items():
                    try:
                        world_state["containers"][container_id] = self.container_serializer.deserialize(container_data)
                    except Exception as e:
                        logger.warning(f"Failed to deserialize container {container_id}: {e}")
                        world_state["containers"][container_id] = container_data
            
            # Deserialize player state
            if "player" in data:
                try:
                    player_data = data["player"]
                    
                    # Handle nested player structure (like {'test_player': {...}})
                    if isinstance(player_data, dict):
                        # Check if it's a nested structure with player IDs as keys
                        if len(player_data) == 1 and all(isinstance(v, dict) for v in player_data.values()):
                            # Extract the actual player data from the nested structure
                            player_id = next(iter(player_data.keys()))
                            actual_player_data = player_data[player_id]
                            world_state["player"] = self.player_serializer.deserialize(actual_player_data)
                        else:
                            # Direct player data structure
                            world_state["player"] = self.player_serializer.deserialize(player_data)
                    else:
                        world_state["player"] = self.player_serializer.deserialize(player_data)
                        
                except Exception as e:
                    logger.error(f"Failed to deserialize player state: {e}")
                    logger.warning(f"Failed to deserialize player state: {e}")
                    world_state["player"] = data["player"]
            
            # Copy other global state data
            if "global_state" in data:
                world_state.update(data["global_state"])
            
            logger.info("World state deserialized successfully")
            return world_state
            
        except Exception as e:
            logger.error(f"Failed to deserialize world state: {e}")
            raise
    
    def validate_world_state(self, world_state: Dict[str, Any], partial: bool = False) -> bool:
        """
        Validate world state structure and data integrity.
        
        Args:
            world_state: World state to validate
            partial: Allow partial validation for incremental saves
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if partial:
                # For partial validation, just check if present sections are valid
                if "player" in world_state:
                    player_state = world_state["player"]
                    if isinstance(player_state, dict) and len(player_state) > 0:
                        # Basic validation - just ensure it's not empty
                        logger.debug("Partial validation: player state present")
                
                if "locations" in world_state:
                    locations = world_state["locations"]
                    if isinstance(locations, dict):
                        logger.debug(f"Partial validation: {len(locations)} locations present")
                
                if "containers" in world_state:
                    containers = world_state["containers"]
                    if isinstance(containers, dict):
                        logger.debug(f"Partial validation: {len(containers)} containers present")
                
                logger.debug("Partial world state validation passed")
                return True
            
            # Full validation - require all sections
            required_sections = ["locations", "containers", "player"]
            
            for section in required_sections:
                if section not in world_state:
                    logger.error(f"Missing required section: {section}")
                    return False
                
                # Check that required sections exist (but allow empty containers)
                section_data = world_state[section]
                if section == "containers":
                    # Containers can be empty - just ensure it's a dict
                    if not isinstance(section_data, dict):
                        logger.error(f"Required section '{section}' is not a dictionary")
                        return False
                elif not section_data:
                    # For locations and player, they must not be empty
                    logger.error(f"Required section '{section}' is empty")
                    return False
            
            # Validate player state has required fields
            player_state = world_state["player"]
            
            # Handle nested player data structure (like {'test_player': {...}})
            if isinstance(player_state, dict):
                # Check if it's a nested structure with player IDs as keys
                if len(player_state) == 0:
                    logger.error("Player state is empty")
                    return False
                
                # Get the first player data (assuming single player for now)
                first_player_data = next(iter(player_state.values()))
                if not isinstance(first_player_data, dict):
                    logger.error("Invalid player data structure")
                    return False
                
                # Validate required player fields in the nested structure
                required_player_fields = ["player_id", "current_location", "inventory"]
                for field in required_player_fields:
                    if field not in first_player_data:
                        logger.error(f"Missing required player field: {field}")
                        return False
            elif isinstance(player_state, PlayerState):
                # Validate PlayerState object attributes
                required_player_fields = ["player_id", "current_location", "inventory"]
                for field in required_player_fields:
                    if not hasattr(player_state, field):
                        logger.error(f"Missing required player field: {field}")
                        return False
            else:
                logger.error("Invalid player state format")
                return False
            
            logger.info("Full world state validation passed")
            return True
            
        except Exception as e:
            logger.error(f"World state validation failed: {e}")
            return False
