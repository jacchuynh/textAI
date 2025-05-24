"""
World State Module

This module manages the state of the game world, including locations,
characters, factions, and environmental conditions. It provides a
central repository for querying and updating world information.
"""

from typing import Dict, Any, List, Optional, Set, Union, Tuple
import logging
import json
from datetime import datetime
import uuid
import copy

logger = logging.getLogger(__name__)

class WorldState:
    """
    Represents and manages the state of the game world.
    
    This class handles queries about the world, updates to its state,
    and provides a historical record of world changes.
    """
    
    def __init__(self, world_id: str = None):
        """
        Initialize a new world state.
        
        Args:
            world_id: Optional identifier for this world state
        """
        self.id = world_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        
        # Core world elements
        self.locations = {}
        self.npcs = {}
        self.factions = {}
        self.items = {}
        self.resources = {}
        
        # World conditions
        self.current_time = 0  # Game time in hours
        self.weather_conditions = {}
        self.global_events = []
        self.active_events = []
        
        # History tracking
        self.change_history = []
        self.version = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world state to dictionary representation."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "locations": self.locations,
            "npcs": self.npcs,
            "factions": self.factions,
            "items": self.items,
            "resources": self.resources,
            "current_time": self.current_time,
            "weather_conditions": self.weather_conditions,
            "global_events": self.global_events,
            "active_events": self.active_events,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldState':
        """Create a world state from dictionary representation."""
        world = cls(world_id=data.get("id"))
        
        # Set attributes from data dictionary
        world.created_at = data.get("created_at", world.created_at)
        world.updated_at = data.get("updated_at", world.updated_at)
        world.locations = data.get("locations", {})
        world.npcs = data.get("npcs", {})
        world.factions = data.get("factions", {})
        world.items = data.get("items", {})
        world.resources = data.get("resources", {})
        world.current_time = data.get("current_time", 0)
        world.weather_conditions = data.get("weather_conditions", {})
        world.global_events = data.get("global_events", [])
        world.active_events = data.get("active_events", [])
        world.version = data.get("version", 1)
        
        return world
    
    def _record_change(self, change_type: str, entity_type: str, entity_id: str, changes: Dict[str, Any]) -> None:
        """
        Record a change to the world state.
        
        Args:
            change_type: Type of change (add, update, remove)
            entity_type: Type of entity affected
            entity_id: Identifier of the entity
            changes: The changes made
        """
        change_record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "game_time": self.current_time,
            "change_type": change_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "changes": changes,
            "version": self.version
        }
        
        self.change_history.append(change_record)
        self.version += 1
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_location(self, location_id: str, location_data: Dict[str, Any]) -> None:
        """
        Add a new location to the world.
        
        Args:
            location_id: Location identifier
            location_data: Location data
        """
        if location_id in self.locations:
            logger.warning(f"Location {location_id} already exists. Use update_location instead.")
            return
            
        self.locations[location_id] = location_data
        self._record_change("add", "location", location_id, location_data)
    
    def update_location(self, location_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing location.
        
        Args:
            location_id: Location identifier
            updates: Data to update
        """
        if location_id not in self.locations:
            logger.warning(f"Location {location_id} does not exist. Use add_location instead.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.locations[location_id])
        
        # Update the location
        self.locations[location_id].update(updates)
        
        # Record the change
        self._record_change("update", "location", location_id, {
            "original": original,
            "updates": updates
        })
    
    def remove_location(self, location_id: str) -> None:
        """
        Remove a location from the world.
        
        Args:
            location_id: Location identifier
        """
        if location_id not in self.locations:
            logger.warning(f"Location {location_id} does not exist.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.locations[location_id])
        
        # Remove the location
        del self.locations[location_id]
        
        # Record the change
        self._record_change("remove", "location", location_id, {
            "original": original
        })
    
    def add_npc(self, npc_id: str, npc_data: Dict[str, Any]) -> None:
        """
        Add a new NPC to the world.
        
        Args:
            npc_id: NPC identifier
            npc_data: NPC data
        """
        if npc_id in self.npcs:
            logger.warning(f"NPC {npc_id} already exists. Use update_npc instead.")
            return
            
        self.npcs[npc_id] = npc_data
        self._record_change("add", "npc", npc_id, npc_data)
    
    def update_npc(self, npc_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing NPC.
        
        Args:
            npc_id: NPC identifier
            updates: Data to update
        """
        if npc_id not in self.npcs:
            logger.warning(f"NPC {npc_id} does not exist. Use add_npc instead.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.npcs[npc_id])
        
        # Update the NPC
        self.npcs[npc_id].update(updates)
        
        # Record the change
        self._record_change("update", "npc", npc_id, {
            "original": original,
            "updates": updates
        })
    
    def remove_npc(self, npc_id: str) -> None:
        """
        Remove an NPC from the world.
        
        Args:
            npc_id: NPC identifier
        """
        if npc_id not in self.npcs:
            logger.warning(f"NPC {npc_id} does not exist.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.npcs[npc_id])
        
        # Remove the NPC
        del self.npcs[npc_id]
        
        # Record the change
        self._record_change("remove", "npc", npc_id, {
            "original": original
        })
    
    def add_faction(self, faction_id: str, faction_data: Dict[str, Any]) -> None:
        """
        Add a new faction to the world.
        
        Args:
            faction_id: Faction identifier
            faction_data: Faction data
        """
        if faction_id in self.factions:
            logger.warning(f"Faction {faction_id} already exists. Use update_faction instead.")
            return
            
        self.factions[faction_id] = faction_data
        self._record_change("add", "faction", faction_id, faction_data)
    
    def update_faction(self, faction_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing faction.
        
        Args:
            faction_id: Faction identifier
            updates: Data to update
        """
        if faction_id not in self.factions:
            logger.warning(f"Faction {faction_id} does not exist. Use add_faction instead.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.factions[faction_id])
        
        # Update the faction
        self.factions[faction_id].update(updates)
        
        # Record the change
        self._record_change("update", "faction", faction_id, {
            "original": original,
            "updates": updates
        })
    
    def remove_faction(self, faction_id: str) -> None:
        """
        Remove a faction from the world.
        
        Args:
            faction_id: Faction identifier
        """
        if faction_id not in self.factions:
            logger.warning(f"Faction {faction_id} does not exist.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.factions[faction_id])
        
        # Remove the faction
        del self.factions[faction_id]
        
        # Record the change
        self._record_change("remove", "faction", faction_id, {
            "original": original
        })
    
    def add_item(self, item_id: str, item_data: Dict[str, Any]) -> None:
        """
        Add a new item to the world.
        
        Args:
            item_id: Item identifier
            item_data: Item data
        """
        if item_id in self.items:
            logger.warning(f"Item {item_id} already exists. Use update_item instead.")
            return
            
        self.items[item_id] = item_data
        self._record_change("add", "item", item_id, item_data)
    
    def update_item(self, item_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing item.
        
        Args:
            item_id: Item identifier
            updates: Data to update
        """
        if item_id not in self.items:
            logger.warning(f"Item {item_id} does not exist. Use add_item instead.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.items[item_id])
        
        # Update the item
        self.items[item_id].update(updates)
        
        # Record the change
        self._record_change("update", "item", item_id, {
            "original": original,
            "updates": updates
        })
    
    def remove_item(self, item_id: str) -> None:
        """
        Remove an item from the world.
        
        Args:
            item_id: Item identifier
        """
        if item_id not in self.items:
            logger.warning(f"Item {item_id} does not exist.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.items[item_id])
        
        # Remove the item
        del self.items[item_id]
        
        # Record the change
        self._record_change("remove", "item", item_id, {
            "original": original
        })
    
    def add_global_event(self, event_data: Dict[str, Any]) -> str:
        """
        Add a global event affecting the world.
        
        Args:
            event_data: Event data
            
        Returns:
            Event ID
        """
        # Ensure event has an ID
        event_id = event_data.get("id", str(uuid.uuid4()))
        event_data["id"] = event_id
        
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.utcnow().isoformat()
            
        # Add game time
        event_data["game_time"] = self.current_time
        
        # Add to global events
        self.global_events.append(event_data)
        
        # Record the change
        self._record_change("add", "global_event", event_id, event_data)
        
        return event_id
    
    def add_active_event(self, event_data: Dict[str, Any]) -> str:
        """
        Add an active event affecting the world.
        
        Args:
            event_data: Event data
            
        Returns:
            Event ID
        """
        # Ensure event has an ID
        event_id = event_data.get("id", str(uuid.uuid4()))
        event_data["id"] = event_id
        
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.utcnow().isoformat()
            
        # Add game time
        event_data["game_time"] = self.current_time
        
        # Add start time if not present
        if "start_time" not in event_data:
            event_data["start_time"] = self.current_time
            
        # Add to active events
        self.active_events.append(event_data)
        
        # Record the change
        self._record_change("add", "active_event", event_id, event_data)
        
        return event_id
    
    def complete_active_event(self, event_id: str, completion_data: Dict[str, Any] = None) -> None:
        """
        Mark an active event as completed.
        
        Args:
            event_id: Event identifier
            completion_data: Optional data about how the event was completed
        """
        # Find the event
        event = None
        for e in self.active_events:
            if e.get("id") == event_id:
                event = e
                break
                
        if event is None:
            logger.warning(f"Active event {event_id} not found.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(event)
        
        # Update with completion data
        if completion_data:
            event.update(completion_data)
            
        # Add completion time
        event["completed_at"] = datetime.utcnow().isoformat()
        event["end_time"] = self.current_time
        
        # Move from active events to global events
        self.active_events.remove(event)
        self.global_events.append(event)
        
        # Record the change
        self._record_change("complete", "active_event", event_id, {
            "original": original,
            "completion": completion_data or {}
        })
    
    def update_time(self, hours: float) -> float:
        """
        Advance the game time.
        
        Args:
            hours: Number of hours to advance
            
        Returns:
            New game time
        """
        old_time = self.current_time
        self.current_time += hours
        
        # Record the change
        self._record_change("update", "time", "game_time", {
            "old_time": old_time,
            "new_time": self.current_time,
            "change": hours
        })
        
        return self.current_time
    
    def set_weather(self, location_id: str, weather_data: Dict[str, Any]) -> None:
        """
        Set weather conditions for a location.
        
        Args:
            location_id: Location identifier
            weather_data: Weather data
        """
        # Ensure location exists
        if location_id not in self.locations:
            logger.warning(f"Location {location_id} does not exist.")
            return
            
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.weather_conditions.get(location_id, {}))
        
        # Update weather
        self.weather_conditions[location_id] = weather_data
        
        # Record the change
        self._record_change("update", "weather", location_id, {
            "original": original,
            "new_weather": weather_data
        })
    
    def get_entities_in_location(self, location_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all entities (NPCs, items) in a location.
        
        Args:
            location_id: Location identifier
            
        Returns:
            Dictionary of entities by type
        """
        if location_id not in self.locations:
            logger.warning(f"Location {location_id} does not exist.")
            return {"npcs": [], "items": []}
            
        entities = {
            "npcs": [],
            "items": []
        }
        
        # Find NPCs in this location
        for npc_id, npc_data in self.npcs.items():
            if npc_data.get("location_id") == location_id:
                npc_copy = copy.deepcopy(npc_data)
                npc_copy["id"] = npc_id
                entities["npcs"].append(npc_copy)
                
        # Find items in this location
        for item_id, item_data in self.items.items():
            if item_data.get("location_id") == location_id:
                item_copy = copy.deepcopy(item_data)
                item_copy["id"] = item_id
                entities["items"].append(item_copy)
                
        return entities
    
    def get_faction_members(self, faction_id: str) -> List[Dict[str, Any]]:
        """
        Get all NPCs belonging to a faction.
        
        Args:
            faction_id: Faction identifier
            
        Returns:
            List of NPCs
        """
        if faction_id not in self.factions:
            logger.warning(f"Faction {faction_id} does not exist.")
            return []
            
        members = []
        
        # Find NPCs in this faction
        for npc_id, npc_data in self.npcs.items():
            if npc_data.get("faction_id") == faction_id:
                npc_copy = copy.deepcopy(npc_data)
                npc_copy["id"] = npc_id
                members.append(npc_copy)
                
        return members
    
    def get_active_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get all active events of a specific type.
        
        Args:
            event_type: Event type
            
        Returns:
            List of active events
        """
        return [e for e in self.active_events if e.get("type") == event_type]
    
    def get_faction_relationship(self, faction1_id: str, faction2_id: str) -> Optional[int]:
        """
        Get the relationship value between two factions.
        
        Args:
            faction1_id: First faction ID
            faction2_id: Second faction ID
            
        Returns:
            Relationship value or None if not found
        """
        # Ensure factions exist
        if faction1_id not in self.factions or faction2_id not in self.factions:
            logger.warning(f"One or both factions do not exist: {faction1_id}, {faction2_id}")
            return None
            
        # Check for relationship in faction data
        relation_key = f"relation_{faction2_id}"
        if relation_key in self.factions[faction1_id]:
            return self.factions[faction1_id][relation_key]
            
        # Check reverse relationship
        relation_key = f"relation_{faction1_id}"
        if relation_key in self.factions[faction2_id]:
            return self.factions[faction2_id][relation_key]
            
        # Default neutral relationship
        return 0
    
    def set_faction_relationship(self, faction1_id: str, faction2_id: str, value: int) -> None:
        """
        Set the relationship value between two factions.
        
        Args:
            faction1_id: First faction ID
            faction2_id: Second faction ID
            value: Relationship value
        """
        # Ensure factions exist
        if faction1_id not in self.factions or faction2_id not in self.factions:
            logger.warning(f"One or both factions do not exist: {faction1_id}, {faction2_id}")
            return
            
        # Store relationship in first faction
        relation_key = f"relation_{faction2_id}"
        
        # Make a copy of the original for change tracking
        original = copy.deepcopy(self.factions[faction1_id].get(relation_key))
        
        # Update relationship
        self.factions[faction1_id][relation_key] = value
        
        # Record the change
        self._record_change("update", "faction_relation", f"{faction1_id}_{faction2_id}", {
            "faction1_id": faction1_id,
            "faction2_id": faction2_id,
            "original": original,
            "new_value": value
        })
    
    def get_recent_changes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent changes to the world state.
        
        Args:
            limit: Maximum number of changes to return
            
        Returns:
            List of recent changes
        """
        # Sort changes by timestamp (newest first)
        sorted_changes = sorted(
            self.change_history,
            key=lambda c: c.get("timestamp", ""),
            reverse=True
        )
        
        return sorted_changes[:limit]


class WorldStateManager:
    """
    Manager for world states.
    
    Provides functionality for creating, loading, saving, and updating
    world states, as well as accessing specific aspects of the world.
    """
    
    def __init__(self, storage_service=None):
        """
        Initialize the world state manager.
        
        Args:
            storage_service: Optional service for persisting world states
        """
        self.logger = logging.getLogger("WorldStateManager")
        self.storage_service = storage_service
        self.active_worlds = {}  # In-memory cache of active world states
    
    def create_world(self, world_id: str = None) -> WorldState:
        """
        Create a new world state.
        
        Args:
            world_id: Optional identifier for the world
            
        Returns:
            New world state
        """
        world = WorldState(world_id)
        self.active_worlds[world.id] = world
        
        # Save to storage if available
        self._save_world(world)
        
        return world
    
    def get_world(self, world_id: str) -> Optional[WorldState]:
        """
        Get a world state by ID.
        
        Args:
            world_id: World identifier
            
        Returns:
            World state or None if not found
        """
        # Check in-memory cache first
        if world_id in self.active_worlds:
            return self.active_worlds[world_id]
            
        # Try to load from storage
        return self._load_world(world_id)
    
    def _save_world(self, world: WorldState) -> bool:
        """
        Save a world state to persistent storage.
        
        Args:
            world: World state to save
            
        Returns:
            Success flag
        """
        if not self.storage_service:
            # No storage service available
            return False
            
        try:
            world_dict = world.to_dict()
            self.storage_service.save_world_state(world.id, world_dict)
            return True
        except Exception as e:
            self.logger.error(f"Error saving world {world.id}: {e}")
            return False
    
    def _load_world(self, world_id: str) -> Optional[WorldState]:
        """
        Load a world state from persistent storage.
        
        Args:
            world_id: World identifier
            
        Returns:
            World state or None if not found or error
        """
        if not self.storage_service:
            # No storage service available
            return None
            
        try:
            world_dict = self.storage_service.load_world_state(world_id)
            
            if not world_dict:
                return None
                
            world = WorldState.from_dict(world_dict)
            
            # Add to active worlds cache
            self.active_worlds[world.id] = world
            
            return world
        except Exception as e:
            self.logger.error(f"Error loading world {world_id}: {e}")
            return None
    
    def update_world(self, world_id: str, update_func) -> Optional[WorldState]:
        """
        Update a world state using a function.
        
        Args:
            world_id: World identifier
            update_func: Function to apply to the world state
            
        Returns:
            Updated world state or None if error
        """
        world = self.get_world(world_id)
        
        if not world:
            self.logger.warning(f"Attempted to update non-existent world: {world_id}")
            return None
            
        # Apply the update function
        try:
            update_func(world)
        except Exception as e:
            self.logger.error(f"Error updating world {world_id}: {e}")
            return None
            
        # Save the updated world
        self._save_world(world)
        
        return world
    
    def process_events(self, world_id: str, current_game_time: float) -> List[Dict[str, Any]]:
        """
        Process all active events in a world based on current game time.
        
        Args:
            world_id: World identifier
            current_game_time: Current game time in hours
            
        Returns:
            List of processed events
        """
        world = self.get_world(world_id)
        
        if not world:
            self.logger.warning(f"Attempted to process events for non-existent world: {world_id}")
            return []
            
        processed_events = []
        
        # Update the world's time
        old_time = world.current_time
        world.update_time(current_game_time - old_time)
        
        # Process active events
        events_to_complete = []
        
        for event in world.active_events:
            # Check if event has an end time and if it's passed
            if "end_time" in event and event["end_time"] <= world.current_time:
                events_to_complete.append(event)
                processed_events.append({
                    "event_id": event.get("id"),
                    "event_type": event.get("type"),
                    "action": "completed",
                    "reason": "time_elapsed"
                })
                
        # Complete events
        for event in events_to_complete:
            world.complete_active_event(event.get("id"), {
                "completion_type": "time_elapsed",
                "completed_at": datetime.utcnow().isoformat()
            })
            
        # Save the world
        self._save_world(world)
        
        return processed_events
    
    def get_location_by_name(self, world_id: str, location_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Find a location by name.
        
        Args:
            world_id: World identifier
            location_name: Name to search for
            
        Returns:
            Tuple of (location_id, location_data) or None if not found
        """
        world = self.get_world(world_id)
        
        if not world:
            return None
            
        # Search for location by name
        for location_id, location_data in world.locations.items():
            if location_data.get("name") == location_name:
                return (location_id, location_data)
                
        return None
    
    def get_npc_by_name(self, world_id: str, npc_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Find an NPC by name.
        
        Args:
            world_id: World identifier
            npc_name: Name to search for
            
        Returns:
            Tuple of (npc_id, npc_data) or None if not found
        """
        world = self.get_world(world_id)
        
        if not world:
            return None
            
        # Search for NPC by name
        for npc_id, npc_data in world.npcs.items():
            if npc_data.get("name") == npc_name:
                return (npc_id, npc_data)
                
        return None
    
    def get_faction_by_name(self, world_id: str, faction_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Find a faction by name.
        
        Args:
            world_id: World identifier
            faction_name: Name to search for
            
        Returns:
            Tuple of (faction_id, faction_data) or None if not found
        """
        world = self.get_world(world_id)
        
        if not world:
            return None
            
        # Search for faction by name
        for faction_id, faction_data in world.factions.items():
            if faction_data.get("name") == faction_name:
                return (faction_id, faction_data)
                
        return None