"""
Narrative Engine Integration Example

This script demonstrates how to use the narrative engine with Celery/Redis
for asynchronous processing. It shows basic usage patterns and how to
interact with the high-level service interface.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List

from backend.src.narrative_engine.service import NarrativeService
from backend.src.narrative_engine.event_bus import get_event_bus, Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_demo():
    """Run a demonstration of the narrative engine integration."""
    logger.info("Starting narrative engine integration demo")
    
    # Create the narrative service
    service = NarrativeService()
    event_bus = get_event_bus()
    
    # Create a new game session
    logger.info("Creating new game session")
    session = await service.create_game_session()
    session_id = session["session_id"]
    logger.info(f"Created session with ID: {session_id}")
    
    # Subscribe to events
    def event_handler(event):
        logger.info(f"Event received: {event.type} - {event.data}")
    
    event_bus.subscribe("player_choice", event_handler)
    event_bus.subscribe("world_updated", event_handler)
    event_bus.subscribe("tension_changed", event_handler)
    
    # Generate a combat narrative (synchronous)
    logger.info("Generating combat narrative (synchronous)")
    combat_result = {
        "id": "combat-001",
        "actor_move": "Powerful Strike",
        "actor_move_type": "FORCE",
        "actor_success": True,
        "damage_dealt": 15,
        "effect_magnitude": 4,
        "actor_desperate": False,
        "actor_calculated": True
    }
    
    actor = {
        "name": "Player Hero",
        "domains": ["BODY", "FIRE", "CRAFT"],
        "id": "player-001"
    }
    
    target = {
        "name": "Forest Troll",
        "domains": ["BODY", "EARTH"],
        "id": "monster-001"
    }
    
    environment_tags = ["dense forest", "rocky terrain", "twilight"]
    
    narrative = await service.generate_combat_narrative(
        session_id=session_id,
        combat_result=combat_result,
        actor=actor,
        target=target,
        environment_tags=environment_tags,
        async_processing=False
    )
    
    logger.info("Combat narrative generated:")
    logger.info(json.dumps(narrative, indent=2))
    
    # Generate a combat narrative (asynchronous with Celery)
    logger.info("Generating combat narrative (asynchronous with Celery)")
    combat_result_2 = {
        "id": "combat-002",
        "actor_move": "Flame Burst",
        "actor_move_type": "FIRE",
        "actor_success": True,
        "damage_dealt": 25,
        "effect_magnitude": 7,
        "actor_desperate": False,
        "actor_calculated": True
    }
    
    task_info = await service.generate_combat_narrative(
        session_id=session_id,
        combat_result=combat_result_2,
        actor=actor,
        target=target,
        environment_tags=environment_tags,
        async_processing=True
    )
    
    logger.info(f"Async task dispatched: {task_info}")
    
    # Wait for task completion
    logger.info("Waiting for async task to complete...")
    task_id = task_info.get("task_id")
    
    if task_id:
        task_result = await service.wait_for_task_completion(task_id, max_wait=10)
        logger.info(f"Task result: {task_result}")
    
    # Process a narrative template
    logger.info("Processing a narrative template")
    
    # First, add a template to the cache
    from backend.src.narrative_engine.template_processor import get_template_processor
    template_processor = get_template_processor()
    
    template_processor.load_templates_from_dict({
        "encounter_intro": "As {player_name} ventures into the {location_name}, {environment_description}. [[if tension_level > 0.7]]The air feels thick with tension.[[else]]The area seems relatively calm.[[endif]]"
    })
    
    # Process the template
    template_result = await service.process_narrative_template(
        session_id=session_id,
        template_key="encounter_intro",
        variables={
            "player_name": "Eldric the Brave",
            "location_name": "Whispering Woods",
            "environment_description": "ancient trees creak in the gentle breeze"
        },
        async_processing=False
    )
    
    logger.info(f"Template result: {template_result}")
    
    # Update the world state
    logger.info("Updating world state")
    
    world_update_events = [
        {
            "type": "location_update",
            "location_id": "whispering_woods",
            "data": {
                "name": "Whispering Woods",
                "description": "An ancient forest where the trees seem to whisper secrets.",
                "danger_level": 45,
                "atmosphere": "mysterious",
                "discovered_at": "2023-06-15T14:30:00Z"
            }
        },
        {
            "type": "npc_update",
            "npc_id": "elder_treant",
            "data": {
                "name": "Elder Treant",
                "description": "An ancient tree spirit that guards the forest.",
                "faction_id": "forest_guardians",
                "location_id": "whispering_woods",
                "disposition": "neutral"
            }
        },
        {
            "type": "time_update",
            "time": 2.5  # Advance game time by 2.5 hours
        }
    ]
    
    world_update = await service.update_world_state(
        session_id=session_id,
        events=world_update_events,
        async_processing=False
    )
    
    logger.info(f"World update result: {world_update}")
    
    # Demonstrate relationship updates
    logger.info("Updating relationship network")
    
    relationship_update = await service.update_relationship_network(
        session_id=session_id,
        character_id="player-001",
        action_data={
            "type": "help",
            "target": "elder_treant",
            "description": "The player helped the Elder Treant by clearing corrupted vines."
        },
        affected_npcs=["elder_treant", "forest_sprite"],
        async_processing=False
    )
    
    logger.info(f"Relationship update result: {relationship_update}")
    
    # Process a narrative branch
    logger.info("Processing a narrative branch")
    
    branch_options = [
        {
            "id": "investigate_ruins",
            "text": "Investigate the ancient ruins deeper in the forest",
            "relevant_domain": "AWARENESS",
            "consequence_preview": "May discover valuable artifacts or awaken ancient guardians"
        },
        {
            "id": "follow_stream",
            "text": "Follow the babbling stream to its source",
            "relevant_domain": "WATER",
            "consequence_preview": "May find a hidden grotto or encounter water spirits"
        },
        {
            "id": "help_villagers",
            "text": "Help the nearby villagers with their monster problem",
            "relevant_domain": "SOCIAL",
            "consequence_preview": "May earn reputation and rewards or face dangerous monsters"
        }
    ]
    
    branch_result = await service.generate_narrative_branch(
        session_id=session_id,
        branch_point_id="forest_choice_point",
        available_options=branch_options,
        async_processing=False
    )
    
    logger.info(f"Branch result: {branch_result}")
    
    # Process a player choice
    logger.info("Processing player choice")
    
    choice_result = await service.process_player_choice(
        session_id=session_id,
        branch_point_id="forest_choice_point",
        choice_id="investigate_ruins"
    )
    
    logger.info(f"Choice result: {choice_result}")
    
    # Get session info
    logger.info("Getting session info")
    
    session_info = await service.get_session_info(session_id)
    
    logger.info(f"Session info: {session_info}")
    
    logger.info("Demo completed successfully")

async def test_celery_integration():
    """Test the Celery integration specifically."""
    logger.info("Testing Celery integration")
    
    # Create the narrative service
    service = NarrativeService()
    
    # Create a session
    session = await service.create_game_session()
    session_id = session["session_id"]
    
    # Submit an asynchronous task
    combat_result = {
        "id": "combat-test-001",
        "actor_move": "Dual Strike",
        "actor_move_type": "FORCE",
        "actor_success": True,
        "damage_dealt": 18,
        "effect_magnitude": 5
    }
    
    actor = {
        "name": "Test Hero",
        "domains": ["BODY", "MIND"],
        "id": "test-player"
    }
    
    target = {
        "name": "Test Enemy",
        "domains": ["DARKNESS", "SPIRIT"],
        "id": "test-enemy"
    }
    
    environment_tags = ["test environment"]
    
    # Dispatch the task
    logger.info("Dispatching async combat narrative task")
    task_info = await service.generate_combat_narrative(
        session_id=session_id,
        combat_result=combat_result,
        actor=actor,
        target=target,
        environment_tags=environment_tags,
        async_processing=True
    )
    
    task_id = task_info.get("task_id")
    logger.info(f"Task dispatched with ID: {task_id}")
    
    # Check task status
    logger.info("Checking task status...")
    task_status = await service.check_task_status(task_id)
    logger.info(f"Task status: {task_status}")
    
    # Wait for completion
    logger.info("Waiting for task completion...")
    task_result = await service.wait_for_task_completion(task_id, max_wait=15)
    logger.info(f"Task result: {task_result}")
    
    logger.info("Celery integration test completed")

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(run_demo())
    
    # Uncomment to run the Celery integration test
    # asyncio.run(test_celery_integration())