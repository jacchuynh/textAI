"""
Combat memory system for enhanced combat.

This module tracks and recalls combat history, providing context
for narrative generation and AI decision making.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...events.event_bus import GameEvent, EventType, event_bus


class CombatMemory:
    """
    Stores and manages memories of combat encounters.
    
    This allows for callback to previous encounters, tracking of effectiveness,
    and providing contextual information for narratives.
    """
    def __init__(self):
        """Initialize the combat memory"""
        self.encounters = []  # List of combat encounters
        self.opponent_history = {}  # History with specific opponents
        self.move_usage_stats = {}  # Stats on move usage and effectiveness
        
    def record_encounter(self, encounter_data: Dict[str, Any]) -> None:
        """
        Record a full combat encounter.
        
        Args:
            encounter_data: Data about the encounter
        """
        # Add timestamp
        encounter_data["timestamp"] = datetime.now().isoformat()
        
        # Add to encounters list
        self.encounters.append(encounter_data)
        
        # Update opponent histories
        for opponent in encounter_data.get("opponents", []):
            self._update_opponent_history(opponent, encounter_data)
            
        # Update move usage stats
        for move_record in encounter_data.get("moves_used", []):
            self._update_move_stats(move_record)
    
    def _update_opponent_history(self, opponent: Dict, encounter_data: Dict) -> None:
        """
        Update history with a specific opponent.
        
        Args:
            opponent: The opponent data
            encounter_data: Data about the encounter
        """
        opponent_name = opponent.get("name")
        if not opponent_name:
            return
            
        if opponent_name not in self.opponent_history:
            self.opponent_history[opponent_name] = {
                "encounters": 0,
                "victories": 0,
                "defeats": 0,
                "last_encounter": None,
                "known_moves": set(),
                "known_weaknesses": set(),
                "known_strengths": set(),
                "narrative_moments": []
            }
            
        # Update stats
        history = self.opponent_history[opponent_name]
        history["encounters"] += 1
        history["last_encounter"] = encounter_data["timestamp"]
        
        # Record outcome
        if encounter_data.get("outcome") == "victory":
            history["victories"] += 1
        elif encounter_data.get("outcome") == "defeat":
            history["defeats"] += 1
            
        # Record moves used by opponent
        for move in opponent.get("moves_used", []):
            history["known_moves"].add(move["name"])
            
        # Record any discovered weaknesses/strengths
        for weakness in opponent.get("weaknesses_shown", []):
            history["known_weaknesses"].add(weakness)
        for strength in opponent.get("strengths_shown", []):
            history["known_strengths"].add(strength)
            
        # Record narrative moments
        if "notable_moments" in encounter_data:
            for moment in encounter_data["notable_moments"]:
                if moment.get("involves", "") == opponent_name:
                    history["narrative_moments"].append(moment)
    
    def _update_move_stats(self, move_record: Dict) -> None:
        """
        Update statistics for a specific move.
        
        Args:
            move_record: Data about the move usage
        """
        move_name = move_record.get("name")
        if not move_name:
            return
            
        if move_name not in self.move_usage_stats:
            self.move_usage_stats[move_name] = {
                "times_used": 0,
                "successful_uses": 0,
                "total_damage": 0,
                "average_damage": 0,
                "effectiveness_rating": 0
            }
            
        stats = self.move_usage_stats[move_name]
        stats["times_used"] += 1
        
        if move_record.get("success", False):
            stats["successful_uses"] += 1
            
        # Update damage stats if applicable
        if "damage" in move_record:
            stats["total_damage"] += move_record["damage"]
            stats["average_damage"] = stats["total_damage"] / stats["times_used"]
            
        # Calculate overall effectiveness rating (success rate * avg damage)
        success_rate = stats["successful_uses"] / stats["times_used"]
        stats["effectiveness_rating"] = success_rate * stats["average_damage"] if stats["average_damage"] else success_rate * 5
    
    def get_opponent_insights(self, opponent_name: str) -> Dict[str, Any]:
        """
        Get tactical insights about a specific opponent.
        
        Args:
            opponent_name: Name of the opponent
            
        Returns:
            Dictionary with insights about the opponent
        """
        if opponent_name not in self.opponent_history:
            return {"known": False, "message": "No history with this opponent"}
            
        history = self.opponent_history[opponent_name]
        
        insights = {
            "known": True,
            "encounters": history["encounters"],
            "victory_rate": history["victories"] / history["encounters"] if history["encounters"] > 0 else 0,
            "known_moves": list(history["known_moves"]),
            "known_weaknesses": list(history["known_weaknesses"]),
            "known_strengths": list(history["known_strengths"]),
            "suggested_approaches": []
        }
        
        # Generate tactical suggestions based on history
        if history["known_weaknesses"]:
            insights["suggested_approaches"].append(
                f"Target their known weaknesses: {', '.join(list(history['known_weaknesses']))}"
            )
            
        if history["known_moves"]:
            # Suggest counters to their most common moves
            insights["suggested_approaches"].append(
                f"Prepare counters for their typical moves: {', '.join(list(history['known_moves'])[:3])}"
            )
            
        # Add narrative callback if there's history
        if history["narrative_moments"]:
            recent_moment = history["narrative_moments"][-1]
            insights["narrative_callback"] = recent_moment.get("description", "You've faced this opponent before.")
            
        return insights
    
    def get_most_effective_moves(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Get the most effective moves based on past combat.
        
        Args:
            count: Number of moves to return
            
        Returns:
            List of the most effective moves
        """
        move_stats = list(self.move_usage_stats.items())
        # Sort by effectiveness rating
        move_stats.sort(key=lambda x: x[1]["effectiveness_rating"], reverse=True)
        
        top_moves = []
        for move_name, stats in move_stats[:count]:
            top_moves.append({
                "name": move_name,
                "success_rate": stats["successful_uses"] / stats["times_used"] if stats["times_used"] > 0 else 0,
                "average_damage": stats["average_damage"],
                "effectiveness": stats["effectiveness_rating"]
            })
            
        return top_moves
    
    def get_narrative_hooks(self) -> List[str]:
        """
        Extract interesting narrative hooks from combat history.
        
        Returns:
            List of narrative hooks
        """
        hooks = []
        
        # Look for recurring opponents
        for opponent, history in self.opponent_history.items():
            if history["encounters"] > 1:
                hooks.append(f"You've faced {opponent} {history['encounters']} times before.")
                
            # Add victorious or defeat narratives
            if history["victories"] > 0 and history["defeats"] == 0:
                hooks.append(f"You've always emerged victorious against {opponent}.")
            elif history["defeats"] > 0 and history["victories"] == 0:
                hooks.append(f"{opponent} has bested you every time you've met.")
                
            # Add memorable moments
            if history["narrative_moments"]:
                recent_moment = history["narrative_moments"][-1]
                hooks.append(recent_moment.get("description", ""))
                
        return hooks
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save combat memory to a JSON file.
        
        Args:
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert sets to lists for JSON serialization
            serializable_data = self._prepare_for_serialization()
            
            with open(filename, 'w') as f:
                json.dump(serializable_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving combat memory: {e}")
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load combat memory from a JSON file.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Restore data structures
            self.encounters = data.get("encounters", [])
            
            # Restore opponent history with sets
            self.opponent_history = {}
            for opponent, history in data.get("opponent_history", {}).items():
                self.opponent_history[opponent] = history
                # Convert lists back to sets
                self.opponent_history[opponent]["known_moves"] = set(history.get("known_moves", []))
                self.opponent_history[opponent]["known_weaknesses"] = set(history.get("known_weaknesses", []))
                self.opponent_history[opponent]["known_strengths"] = set(history.get("known_strengths", []))
                
            self.move_usage_stats = data.get("move_usage_stats", {})
            return True
        except Exception as e:
            print(f"Error loading combat memory: {e}")
            return False
    
    def _prepare_for_serialization(self) -> Dict:
        """
        Prepare data for JSON serialization (convert sets to lists).
        
        Returns:
            Serializable data dictionary
        """
        serializable_data = {
            "encounters": self.encounters,
            "opponent_history": {},
            "move_usage_stats": self.move_usage_stats
        }
        
        # Convert sets to lists in opponent history
        for opponent, history in self.opponent_history.items():
            serializable_data["opponent_history"][opponent] = {
                **history,
                "known_moves": list(history["known_moves"]),
                "known_weaknesses": list(history["known_weaknesses"]),
                "known_strengths": list(history["known_strengths"])
            }
            
        return serializable_data
    
    def create_memory_context(self, current_opponent_name: str = None) -> Dict[str, Any]:
        """
        Create a dictionary of memory elements for narrative generation.
        
        Args:
            current_opponent_name: Name of the current opponent
            
        Returns:
            Memory context dictionary
        """
        memory_elements = {
            "recent_encounters": self.encounters[-3:] if self.encounters else [],
            "opponent_records": {},
            "most_effective_moves": self.get_most_effective_moves(3),
            "narrative_hooks": self.get_narrative_hooks(),
            "current_opponent_name": current_opponent_name
        }
        
        # Add opponent records for recently encountered opponents
        recent_opponents = set()
        for encounter in memory_elements["recent_encounters"]:
            for opponent in encounter.get("opponents", []):
                opponent_name = opponent.get("name")
                if opponent_name:
                    recent_opponents.add(opponent_name)
                    
        for opponent_name in recent_opponents:
            if opponent_name in self.opponent_history:
                memory_elements["opponent_records"][opponent_name] = {
                    **self.opponent_history[opponent_name],
                    # Convert sets to lists for serialization
                    "known_moves": list(self.opponent_history[opponent_name]["known_moves"]),
                    "known_weaknesses": list(self.opponent_history[opponent_name]["known_weaknesses"]),
                    "known_strengths": list(self.opponent_history[opponent_name]["known_strengths"])
                }
                
        # Add the current opponent if not already included
        if current_opponent_name and current_opponent_name in self.opponent_history and current_opponent_name not in memory_elements["opponent_records"]:
            memory_elements["opponent_records"][current_opponent_name] = {
                **self.opponent_history[current_opponent_name],
                # Convert sets to lists for serialization
                "known_moves": list(self.opponent_history[current_opponent_name]["known_moves"]),
                "known_weaknesses": list(self.opponent_history[current_opponent_name]["known_weaknesses"]),
                "known_strengths": list(self.opponent_history[current_opponent_name]["known_strengths"])
            }
                
        return memory_elements
    
    def publish_memory_event(self, 
                            game_id: str,
                            character_id: str,
                            opponent_name: str,
                            content: str,
                            tags: List[str] = None) -> None:
        """
        Publish a memory event to the event bus.
        
        Args:
            game_id: ID of the game
            character_id: ID of the character
            opponent_name: Name of the opponent
            content: Content of the memory
            tags: Tags for the memory
        """
        # Create and publish the event
        event = GameEvent(
            type=EventType.COMBAT_MEMORY,
            actor=character_id,
            context={
                "opponent": opponent_name,
                "content": content,
                "timestamp": datetime.now().isoformat()
            },
            tags=tags or ["combat", "memory"],
            game_id=game_id
        )
        
        event_bus.publish(event)
        

# Create a global instance
combat_memory = CombatMemory()