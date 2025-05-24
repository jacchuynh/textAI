import random
from .world_state import world_state_manager, EconomicStatus, PoliticalStability
from ..event_bus import event_bus, GameEvent, EventType # Adjusted import path

class WorldEventTriggerSystem:
    """
    System responsible for triggering narrative events based on global world state.
    """
    def __init__(self):
        self.last_triggered_event_type_time: dict[EventType, float] = {}
        self.event_cooldowns: dict[EventType, float] = {
            EventType.GLOBAL_ECONOMIC_SHIFT: 3600 * 24 * 7,  # Once a week game time
            EventType.GLOBAL_POLITICAL_SHIFT: 3600 * 24 * 10, # Once every 10 days
            EventType.AMBIENT_WORLD_NARRATIVE: 3600 * 6 # Every 6 hours
        }
        # Could subscribe to WORLD_STATE_CHANGED if we want immediate reactions
        # event_bus.subscribe(EventType.WORLD_STATE_CHANGED, self.handle_world_state_change)

    def _can_trigger(self, event_type: EventType) -> bool:
        """Checks if an event type is off cooldown."""
        import time # Assuming time.time() for current time, replace with game time if available
        now = time.time() 
        cooldown = self.event_cooldowns.get(event_type, 3600 * 24) # Default 1 day cooldown
        last_triggered = self.last_triggered_event_type_time.get(event_type)
        if last_triggered and (now - last_triggered) < cooldown:
            return False
        return True

    def _mark_triggered(self, event_type: EventType):
        import time # Assuming time.time() for current time
        self.last_triggered_event_type_time[event_type] = time.time()

    def process_world_state(self, game_id: Optional[str] = None):
        """
        Evaluates the current world state and potentially triggers narrative events.
        This method would be called periodically by your game loop or a scheduler.
        """
        world_summary = world_state_manager.get_current_state_summary()
        
        # Example: Triggering an economic event
        if self._can_trigger(EventType.GLOBAL_ECONOMIC_SHIFT):
            # Simple logic: if economy is bad, trigger a recession impact event
            if world_summary["economic_status"] in [EconomicStatus.RECESSION.value, EconomicStatus.DEPRESSION.value]:
                if random.random() < 0.3: # 30% chance if conditions met and off cooldown
                    event_context = {
                        "economic_status": world_summary["economic_status"],
                        "severity": "noticeable",
                        "observation_point": "local_market" # Could be player location context
                    }
                    event = GameEvent(
                        type=EventType.GLOBAL_ECONOMIC_SHIFT,
                        actor="World",
                        context=event_context,
                        tags=["world", "economy", world_summary["economic_status"]],
                        game_id=game_id
                    )
                    event_bus.publish(event)
                    self._mark_triggered(EventType.GLOBAL_ECONOMIC_SHIFT)

        # Example: Triggering a political event
        if self._can_trigger(EventType.GLOBAL_POLITICAL_SHIFT):
            if world_summary["political_stability"] in [PoliticalStability.UNREST.value, PoliticalStability.REBELLION.value]:
                if random.random() < 0.2: # 20% chance
                    event_context = {
                        "political_stability": world_summary["political_stability"],
                        "affected_region": "capital_city", # Example
                        "rumor_type": "growing_dissent"
                    }
                    event = GameEvent(
                        type=EventType.GLOBAL_POLITICAL_SHIFT,
                        actor="World",
                        context=event_context,
                        tags=["world", "politics", world_summary["political_stability"]],
                        game_id=game_id
                    )
                    event_bus.publish(event)
                    self._mark_triggered(EventType.GLOBAL_POLITICAL_SHIFT)
        
        # Example: Ambient world narrative based on season or threats
        if self._can_trigger(EventType.AMBIENT_WORLD_NARRATIVE):
            if random.random() < 0.5: # 50% chance for an ambient message
                ambient_context = world_summary.copy() # Pass full world state for flexibility
                event = GameEvent(
                    type=EventType.AMBIENT_WORLD_NARRATIVE,
                    actor="World", # Or "Narrator"
                    context=ambient_context,
                    tags=["world", "ambient", world_summary["current_season"]],
                    game_id=game_id
                )
                event_bus.publish(event)
                self._mark_triggered(EventType.AMBIENT_WORLD_NARRATIVE)


    # def handle_world_state_change(self, event: GameEvent):
    # """React immediately to specific world state changes if needed."""
    #     if event.context.get("change") == "economic_status":
    #         new_status = event.context.get("new_value")
    #         # Potentially trigger a more immediate, specific event
    #         pass


# Global instance
world_event_trigger = WorldEventTriggerSystem()

# Example of how you might call this in a game loop:
# world_event_trigger.process_world_state(current_game_id)