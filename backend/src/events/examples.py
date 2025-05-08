"""
Example usage of the event system.

This module provides examples of how to use the event system in different contexts.
"""
from .event_bus import event_bus, GameEvent, EventType


def example_combat_system():
    """Example of how the combat system might use events."""
    
    # 1. Subscribe to events that the combat system needs to handle
    def on_combat_started(event):
        """Handle combat started event."""
        print(f"Combat system: Starting combat with {event.context.get('enemy_name')}")
        # combat_system.start_combat(event.actor, event.context.get('enemy_id'))
    
    def on_attack_performed(event):
        """Handle attack performed event."""
        print(f"Combat system: {event.actor} attacked {event.context.get('target')}")
        # Process attack logic
    
    # Register event handlers
    event_bus.subscribe(EventType.COMBAT_STARTED, on_combat_started)
    event_bus.subscribe(EventType.ATTACK_PERFORMED, on_attack_performed)
    
    # 2. Publish events when combat actions occur
    
    # Example: Player starts combat with an enemy
    combat_event = GameEvent(
        type=EventType.COMBAT_STARTED,
        actor="player_123",
        context={
            "enemy_id": 42,
            "enemy_name": "Forest Troll",
            "location": "Dark Forest",
            "surprise": False
        },
        tags=["combat", "encounter", "forest"],
        effects=[
            {"type": "start_combat_state", "target": "player_123"},
            {"type": "play_music", "value": "combat_theme"}
        ],
        game_id="game_789"
    )
    event_bus.publish(combat_event)
    
    # Example: Player attacks enemy
    attack_event = GameEvent(
        type=EventType.ATTACK_PERFORMED,
        actor="player_123",
        context={
            "target": "Forest Troll",
            "weapon": "Long Sword",
            "skill_used": "Power Attack",
            "roll": 15,
            "success": True
        },
        tags=["combat", "attack", "melee"],
        effects=[
            {"type": "damage", "target": "Forest Troll", "amount": 8},
            {"type": "animation", "value": "sword_swing"}
        ],
        game_id="game_789"
    )
    event_bus.publish(attack_event)


def example_domain_progression():
    """Example of how the domain progression system might use events."""
    
    # 1. Subscribe to domain and skill events
    def on_domain_check(event):
        """Handle domain check events."""
        print(f"Domain system: {event.actor} made a {event.context.get('domain')} check " + 
              f"with result {event.context.get('success')}")
        # domain_system.log_domain_use(event.actor, event.context.get('domain'), event.context.get('success'))
    
    def on_domain_increased(event):
        """Handle domain increased events."""
        print(f"Domain system: {event.actor}'s {event.context.get('domain')} increased to " +
              f"level {event.context.get('new_value')}")
        # progression_system.apply_domain_benefits(event.actor, event.context.get('domain'))
    
    # Register event handlers
    event_bus.subscribe(EventType.DOMAIN_CHECK, on_domain_check)
    event_bus.subscribe(EventType.DOMAIN_INCREASED, on_domain_increased)
    
    # 2. Publish events for domain checks and increases
    
    # Example: Player makes a domain check
    domain_check_event = GameEvent(
        type=EventType.DOMAIN_CHECK,
        actor="player_123",
        context={
            "domain": "CRAFT",
            "difficulty": 15,
            "roll": 12,
            "modifier": 5,
            "total": 17,
            "success": True,
            "action": "Repair damaged armor"
        },
        tags=["check", "craft", "armor", "repair"],
        effects=[
            {"type": "domain_log_entry", "domain": "CRAFT", "success": True},
            {"type": "item_repaired", "item_id": 567}
        ],
        game_id="game_789"
    )
    event_bus.publish(domain_check_event)
    
    # Example: Domain increases after enough successful checks
    domain_increased_event = GameEvent(
        type=EventType.DOMAIN_INCREASED,
        actor="player_123",
        context={
            "domain": "CRAFT",
            "old_value": 2,
            "new_value": 3,
            "tier": "SKILLED"
        },
        tags=["progression", "craft", "level_up"],
        effects=[
            {"type": "domain_level_up", "domain": "CRAFT", "value": 3},
            {"type": "unlock_ability", "ability_id": "expert_crafting"},
            {"type": "notification", "message": "Your Craft domain has increased to Skilled tier!"}
        ],
        game_id="game_789"
    )
    event_bus.publish(domain_increased_event)


def example_narrative_query():
    """Example of how to query the event history to build narrative summaries."""
    
    # Get a general summary of recent events
    recent_summary = event_bus.get_summary(
        game_id="game_789",
        limit=5
    )
    print("\nRecent events summary:")
    print(recent_summary)
    
    # Get a filtered summary for specific event types
    combat_summary = event_bus.get_summary(
        event_types=[EventType.COMBAT_STARTED, EventType.ATTACK_PERFORMED, EventType.ENEMY_DEFEATED],
        actor="player_123",
        game_id="game_789",
        limit=10
    )
    print("\nCombat summary:")
    print(combat_summary)
    
    # Get raw event history filtered by tags
    crafting_events = event_bus.get_history(
        tags=["craft", "repair"],
        game_id="game_789"
    )
    print("\nCrafting events:")
    for event in crafting_events:
        print(f"- {event['timestamp']}: {event['type']} ({', '.join(event['tags'][:3])})")


def example_wildcard_subscriber():
    """Example of using wildcard subscriptions to handle all events."""
    
    # Analytics system that tracks all events
    def analytics_tracker(event):
        """Track all events for analytics."""
        print(f"Analytics: Tracking {event.type} event from {event.actor}")
        # analytics_system.track_event(event.to_dict())
    
    # Memory system that stores all notable events for the character
    def memory_recorder(event):
        """Record all events to the memory system if they're notable."""
        # Only record events that have certain tags or are of certain types
        should_remember = (
            any(tag in event.tags for tag in ["important", "notable", "quest", "combat"]) or
            isinstance(event.type, EventType) and event.type in [
                EventType.QUEST_COMPLETED, 
                EventType.ENEMY_DEFEATED,
                EventType.LOCATION_DISCOVERED
            ]
        )
        
        if should_remember:
            print(f"Memory system: Recording {event.type} event to long-term memory")
            # memory_system.add_memory(event.to_dict())
    
    # Register wildcard handlers
    event_bus.subscribe(EventType.WILDCARD, analytics_tracker)
    event_bus.subscribe(EventType.WILDCARD, memory_recorder)


def run_all_examples():
    """Run all examples."""
    # Reset the event bus for clean examples
    event_bus.logger.clear()
    
    # First, set up all the event listeners
    example_wildcard_subscriber()
    
    # Then, generate example events
    print("\n=== COMBAT SYSTEM EXAMPLE ===")
    example_combat_system()
    
    print("\n=== DOMAIN PROGRESSION EXAMPLE ===")
    example_domain_progression()
    
    print("\n=== NARRATIVE QUERY EXAMPLE ===")
    example_narrative_query()
    
    
if __name__ == "__main__":
    run_all_examples()