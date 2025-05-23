"""
Game context provider for accessing game state.

This module provides access to the current game state, including
player information, location, objects, and monsters.
"""
from typing import Dict, List, Any, Optional, Union, Set


class GameObject:
    """Base class for all game objects."""
    def __init__(self, obj_id: str, name: str, location: str):
        self.id = obj_id
        self.name = name
        self.location = location


class Monster(GameObject):
    """Monster class extending GameObject."""
    def __init__(self, 
                obj_id: str, 
                name: str, 
                location: str,
                threat_tier: str = "minion",
                category: str = "",
                primary_domains: List[str] = None,
                adjectives: List[str] = None,
                aliases: List[str] = None,
                description: str = ""):
        super().__init__(obj_id, name, location)
        self.threat_tier = threat_tier
        self.category = category
        self.primary_domains = primary_domains or []
        self.adjectives = adjectives or []
        self.aliases = aliases or []
        self.description = description
        self.health = 100  # Default
        self.in_combat = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert monster to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "threat_tier": self.threat_tier,
            "category": self.category,
            "adjectives": self.adjectives,
            "aliases": self.aliases,
            "description": self.description,
            "health": self.health,
            "in_combat": self.in_combat
        }


class GameContext:
    """
    Provides access to the current game state.
    
    This class serves as an interface to access information about the
    current game state, including player information, locations, objects, and monsters.
    """
    
    def __init__(self):
        """Initialize the game context provider."""
        # In a real implementation, this would connect to your game state database
        # For now, we'll use simple dictionaries for demonstration
        self._current_player_id = "player_001"
        self._current_location_id = "town_square"
        
        # Example game objects (would come from your database)
        self._objects = {
            "sword_001": {
                "id": "sword_001",
                "name": "sword",
                "adjectives": ["rusty", "old"],
                "aliases": ["blade"],
                "location": "town_square"
            },
            "sword_002": {
                "id": "sword_002",
                "name": "sword",
                "adjectives": ["shiny", "new"],
                "aliases": ["blade"],
                "location": "inventory_player_001"
            },
            "key_001": {
                "id": "key_001",
                "name": "key",
                "adjectives": ["brass", "small"],
                "aliases": [],
                "location": "town_square"
            },
            "potion_001": {
                "id": "potion_001",
                "name": "potion",
                "adjectives": ["red", "healing"],
                "aliases": ["vial", "medicine"],
                "location": "inventory_player_001"
            }
        }
        
        # Example monsters (would come from your database)
        self._monsters = {
            "monster_001": {
                "id": "monster_001",
                "name": "Vine Weasel",
                "threat_tier": "minion",
                "category": "Beast",
                "adjectives": ["small", "furry"],
                "aliases": ["weasel", "rodent"],
                "location": "town_square",
                "health": 30,
                "in_combat": False,
                "description": "A small, furry creature with vines growing from its back."
            },
            "monster_002": {
                "id": "monster_002",
                "name": "Blizzard Bear",
                "threat_tier": "standard",
                "category": "Beast",
                "adjectives": ["large", "white"],
                "aliases": ["bear"],
                "location": "forest_edge",
                "health": 120,
                "in_combat": False,
                "description": "A massive bear with fur like drifting snow."
            }
        }
        
        # Combat state
        self._current_combat = {
            "active": False,
            "enemies": [],
            "last_enemy": None
        }
        
        # Recently referenced objects
        self._recently_referenced = {
            "monsters": [],  # List of recently referenced monster IDs
            "objects": [],   # List of recently referenced object IDs
            "locations": []  # List of recently referenced location IDs
        }
    
    def get_player_id(self) -> str:
        """
        Get the current player ID.
        
        Returns:
            Current player ID
        """
        return self._current_player_id
    
    def get_current_location(self) -> str:
        """
        Get the current location ID.
        
        Returns:
            Current location ID
        """
        return self._current_location_id
    
    def set_current_location(self, location_id: str) -> None:
        """
        Set the current location.
        
        Args:
            location_id: New location ID
        """
        self._current_location_id = location_id
    
    def get_objects_at_location(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Get objects at a location.
        
        Args:
            location_id: Location ID
            
        Returns:
            List of objects at the location
        """
        return [
            obj for obj in self._objects.values()
            if obj.get('location') == location_id
        ]
    
    def get_monsters_at_location(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Get monsters at a location.
        
        Args:
            location_id: Location ID
            
        Returns:
            List of monsters at the location
        """
        return [
            monster for monster in self._monsters.values()
            if monster.get('location') == location_id
        ]
    
    def get_player_inventory(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get player inventory.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of objects in player inventory
        """
        inventory_location = f"inventory_{player_id}"
        return [
            obj for obj in self._objects.values()
            if obj.get('location') == inventory_location
        ]
    
    def get_object_by_id(self, object_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an object by ID.
        
        Args:
            object_id: Object ID
            
        Returns:
            Object data or None if not found
        """
        return self._objects.get(object_id)
    
    def get_monster_by_id(self, monster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a monster by ID.
        
        Args:
            monster_id: Monster ID
            
        Returns:
            Monster data or None if not found
        """
        return self._monsters.get(monster_id)
    
    def move_object(self, object_id: str, new_location: str) -> bool:
        """
        Move an object to a new location.
        
        Args:
            object_id: Object ID
            new_location: New location ID
            
        Returns:
            True if successful, False otherwise
        """
        if object_id in self._objects:
            self._objects[object_id]['location'] = new_location
            return True
        return False
    
    def move_monster(self, monster_id: str, new_location: str) -> bool:
        """
        Move a monster to a new location.
        
        Args:
            monster_id: Monster ID
            new_location: New location ID
            
        Returns:
            True if successful, False otherwise
        """
        if monster_id in self._monsters:
            self._monsters[monster_id]['location'] = new_location
            return True
        return False
    
    def add_to_inventory(self, player_id: str, object_id: str) -> bool:
        """
        Add an object to player inventory.
        
        Args:
            player_id: Player ID
            object_id: Object ID
            
        Returns:
            True if successful, False otherwise
        """
        inventory_location = f"inventory_{player_id}"
        return self.move_object(object_id, inventory_location)
    
    def remove_from_inventory(self, player_id: str, object_id: str, new_location: str) -> bool:
        """
        Remove an object from player inventory.
        
        Args:
            player_id: Player ID
            object_id: Object ID
            new_location: New location for the object
            
        Returns:
            True if successful, False otherwise
        """
        inventory_location = f"inventory_{player_id}"
        if (object_id in self._objects and 
            self._objects[object_id]['location'] == inventory_location):
            return self.move_object(object_id, new_location)
        return False
    
    def start_combat(self, enemy_ids: List[str]) -> None:
        """
        Start combat with the specified enemies.
        
        Args:
            enemy_ids: List of enemy monster IDs
        """
        self._current_combat["active"] = True
        self._current_combat["enemies"] = enemy_ids
        if enemy_ids:
            self._current_combat["last_enemy"] = enemy_ids[0]
            # Mark monsters as in combat
            for enemy_id in enemy_ids:
                if enemy_id in self._monsters:
                    self._monsters[enemy_id]["in_combat"] = True
    
    def end_combat(self) -> None:
        """End the current combat."""
        # Mark monsters as no longer in combat
        for enemy_id in self._current_combat["enemies"]:
            if enemy_id in self._monsters:
                self._monsters[enemy_id]["in_combat"] = False
        
        self._current_combat["active"] = False
        self._current_combat["enemies"] = []
        self._current_combat["last_enemy"] = None
    
    def is_in_combat(self) -> bool:
        """
        Check if the player is currently in combat.
        
        Returns:
            True if in combat, False otherwise
        """
        return self._current_combat["active"]
    
    def get_current_enemies(self) -> List[Dict[str, Any]]:
        """
        Get the current enemies in combat.
        
        Returns:
            List of enemy monster data
        """
        return [self._monsters[enemy_id] for enemy_id in self._current_combat["enemies"]
                if enemy_id in self._monsters]
    
    def get_last_enemy(self) -> Optional[Dict[str, Any]]:
        """
        Get the last enemy interacted with.
        
        Returns:
            Last enemy data or None
        """
        enemy_id = self._current_combat["last_enemy"]
        if enemy_id and enemy_id in self._monsters:
            return self._monsters[enemy_id]
        return None
    
    def reference_entity(self, entity_id: str, entity_type: str) -> None:
        """
        Reference an entity (object, monster, location).
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type ("monsters", "objects", "locations")
        """
        if entity_type in self._recently_referenced:
            # Remove if already in list
            if entity_id in self._recently_referenced[entity_type]:
                self._recently_referenced[entity_type].remove(entity_id)
            # Add to front of list
            self._recently_referenced[entity_type].insert(0, entity_id)
            # Limit to 10 most recent
            self._recently_referenced[entity_type] = self._recently_referenced[entity_type][:10]
    
    def get_recently_referenced(self, entity_type: str, n: int = 1) -> List[str]:
        """
        Get recently referenced entities.
        
        Args:
            entity_type: Entity type ("monsters", "objects", "locations")
            n: Number of recent entities to return
            
        Returns:
            List of entity IDs
        """
        if entity_type in self._recently_referenced:
            return self._recently_referenced[entity_type][:n]
        return []
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current game context.
        
        Returns:
            Dictionary with current game context
        """
        context = {
            "player_id": self._current_player_id,
            "current_location": self._current_location_id,
            "in_combat": self._current_combat["active"],
            "last_enemy": self._current_combat["last_enemy"]
        }
        
        # Add recent references
        context["recently_referenced"] = {
            k: v[0] if v else None for k, v in self._recently_referenced.items()
        }
        
        return context
    
    def add_monster(self, monster_data: Dict[str, Any]) -> str:
        """
        Add a monster to the game.
        
        Args:
            monster_data: Monster data
            
        Returns:
            Monster ID
        """
        monster_id = monster_data.get("id", f"monster_{len(self._monsters) + 1}")
        self._monsters[monster_id] = monster_data
        return monster_id
    
    def add_object(self, object_data: Dict[str, Any]) -> str:
        """
        Add an object to the game.
        
        Args:
            object_data: Object data
            
        Returns:
            Object ID
        """
        object_id = object_data.get("id", f"object_{len(self._objects) + 1}")
        self._objects[object_id] = object_data
        return object_id


# Global game context instance
game_context = GameContext()