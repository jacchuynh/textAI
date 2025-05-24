from typing import Dict, List, Any, Optional
from enum import Enum

class EconomicStatus(str, Enum):
    BOOM = "booming"
    STABLE = "stable"
    RECESSION = "recession"
    DEPRESSION = "depression"

class PoliticalStability(str, Enum):
    PEACEFUL = "peaceful"
    STABLE = "stable"
    UNREST = "simmering unrest"
    REBELLION = "open rebellion"
    WAR = "at war"

class WorldState:
    """
    Manages the overall state of the game world.
    """
    def __init__(self):
        self.economic_status: EconomicStatus = EconomicStatus.STABLE
        self.political_stability: PoliticalStability = PoliticalStability.STABLE
        self.current_season: str = "spring"  # Example: "spring", "summer", "autumn", "winter"
        self.active_global_threats: List[str] = [] # E.g., ["Dragon menace in the North", "Undead plague spreading"]
        self.world_properties: Dict[str, Any] = {} # For other generic world properties

    def update_economic_status(self, status: EconomicStatus):
        self.economic_status = status
        # Potentially publish an event here if other systems need to react immediately
        # event_bus.publish(GameEvent(type=EventType.WORLD_STATE_CHANGED, actor="System", context={"change": "economic_status", "new_value": status.value}))

    def update_political_stability(self, stability: PoliticalStability):
        self.political_stability = stability
        # event_bus.publish(GameEvent(type=EventType.WORLD_STATE_CHANGED, actor="System", context={"change": "political_stability", "new_value": stability.value}))

    def set_season(self, season: str):
        self.current_season = season

    def add_global_threat(self, threat: str):
        if threat not in self.active_global_threats:
            self.active_global_threats.append(threat)

    def remove_global_threat(self, threat: str):
        if threat in self.active_global_threats:
            self.active_global_threats.remove(threat)
            
    def set_world_property(self, key: str, value: Any):
        self.world_properties[key] = value

    def get_world_property(self, key: str) -> Optional[Any]:
        return self.world_properties.get(key)

    def get_current_state_summary(self) -> Dict[str, Any]:
        """Returns a dictionary snapshot of the current world state."""
        return {
            "economic_status": self.economic_status.value,
            "political_stability": self.political_stability.value,
            "current_season": self.current_season,
            "active_global_threats": list(self.active_global_threats),
            "world_properties": dict(self.world_properties)
        }

# Global instance of the world state
world_state_manager = WorldState()

# Example usage:
# world_state_manager.update_economic_status(EconomicStatus.RECESSION)
# world_state_manager.add_global_threat("The Blighted Sands expanding")