"""
Simulation-related tasks for AI GM Brain.

This module contains Celery tasks for handling asynchronous
world simulation processing.
"""

from backend.src.ai_gm.tasks.celery_app import celery_app
import logging
import time
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Attempt to import the simulation components if available
try:
    from backend.src.ai_gm.world_reaction.reaction_assessor import ReactionAssessor
    from backend.src.ai_gm.pacing.pacing_manager import PacingManager
    simulation_components_available = True
except ImportError:
    logger.warning("Simulation components not available. Using mock responses for development.")
    simulation_components_available = False

@celery_app.task(bind=True, max_retries=2)
def process_world_reaction(self, action_data, world_context):
    """
    Process how the world reacts to a significant player action.
    
    Args:
        action_data: Details of the player's action
        world_context: Current world state
        
    Returns:
        Computed reactions
    """
    try:
        logger.info(f"Processing world reaction to action: {action_data.get('action_type', 'unknown')}...")
        
        if simulation_components_available:
            reaction_assessor = ReactionAssessor()
            
            # Compute reactions for different NPCs and factions
            npc_reactions = reaction_assessor.compute_npc_reactions(action_data, world_context)
            faction_reactions = reaction_assessor.compute_faction_reactions(action_data, world_context)
            environment_changes = reaction_assessor.compute_environment_changes(action_data, world_context)
        else:
            # Log that we'd normally process the reactions here
            logger.info(f"Would process world reactions for action: {action_data.get('action_type', 'unknown')}...")
            # Simulate processing time
            time.sleep(1.5)
            # Create mock responses for development
            npc_reactions = {"barkeeper": "slightly impressed", "merchant": "indifferent"}
            faction_reactions = {"village": 0.1, "merchants_guild": -0.05}
            environment_changes = ["Some villagers start whispering about your actions"]
        
        return {
            'npc_reactions': npc_reactions,
            'faction_reactions': faction_reactions,
            'environment_changes': environment_changes,
            'timestamp': datetime.utcnow().isoformat(),
            'action_data': action_data
        }
    except Exception as exc:
        logger.error(f"World reaction processing failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def generate_ambient_content(self, location, time_of_day, recent_events, mood=None):
    """
    Generate rich ambient content for a location.
    
    Args:
        location: The game location
        time_of_day: Current time of day
        recent_events: Recent events in the game
        mood: Optional mood/tone for the content
        
    Returns:
        Generated ambient content
    """
    try:
        logger.info(f"Generating ambient content for location: {location} at {time_of_day}...")
        
        if simulation_components_available:
            pacing_manager = PacingManager()
            ambient_content = pacing_manager.generate_ambient_content(
                location=location,
                time_of_day=time_of_day,
                recent_events=recent_events,
                mood=mood
            )
        else:
            # Log that we'd normally generate content here
            logger.info(f"Would generate ambient content for {location} at {time_of_day}...")
            # Simulate processing time
            time.sleep(1)
            # Create mock content for development
            ambient_descriptions = [
                f"The {location} is {mood or 'quiet'} as the {time_of_day} light filters through.",
                f"A gentle breeze rustles through {location} as {time_of_day} settles in.",
                f"The sounds of distant conversation can be heard throughout {location}."
            ]
            ambient_content = ambient_descriptions[int(time.time()) % len(ambient_descriptions)]
        
        return {
            'location': location,
            'content': ambient_content,
            'time_of_day': time_of_day,
            'timestamp': datetime.utcnow().isoformat(),
            'mood': mood
        }
    except Exception as exc:
        logger.error(f"Ambient content generation failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def process_npc_decision(self, npc_id, decision_context, available_actions):
    """
    Process a complex NPC decision.
    
    Args:
        npc_id: Identifier for the NPC
        decision_context: Context for the decision
        available_actions: Actions the NPC can take
        
    Returns:
        NPC decision result
    """
    try:
        logger.info(f"Processing decision for NPC {npc_id}...")
        
        # Simulate NPC decision-making process
        # In a real implementation, this would use AI/rules to determine the action
        time.sleep(2)
        
        # For demonstration, choose action based on simple rules
        priority_action = None
        if decision_context.get('threat_level', 0) > 7:
            priority_action = next((a for a in available_actions if a.get('type') == 'flee'), None)
        elif decision_context.get('player_reputation', 0) > 8:
            priority_action = next((a for a in available_actions if a.get('type') == 'help'), None)
        
        # Default to a random action if no priority set
        chosen_action = priority_action or available_actions[int(time.time()) % len(available_actions)]
        
        return {
            'npc_id': npc_id,
            'chosen_action': chosen_action,
            'decision_context': decision_context,
            'reasoning': f"NPC {npc_id} chose action based on current circumstances.",
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"NPC decision processing failed: {exc}")
        self.retry(exc=exc)

@celery_app.task
def update_ambient_world_state():
    """
    Periodic task to update the ambient world state.
    This is called by the scheduler at regular intervals.
    
    Returns:
        Summary of world state updates
    """
    logger.info("Updating ambient world state...")
    
    # This would typically:
    # 1. Get current world state from database
    # 2. Apply time-based changes (weather, NPC movements, etc.)
    # 3. Process any pending world events
    # 4. Update the database with new state
    
    # Simulate processing
    time.sleep(3)
    
    return {
        'weather_changes': ["Clear skies have turned cloudy", "Temperature has dropped slightly"],
        'npc_movements': ["Merchant has moved to the market", "Guard has started patrolling"],
        'time_progression': "Advanced 15 minutes in game time",
        'timestamp': datetime.utcnow().isoformat()
    }

@celery_app.task(bind=True, max_retries=2)
def simulate_npc_routine(self, npc_id, current_time, location):
    """
    Simulate an NPC's routine activities based on time and location.
    
    Args:
        npc_id: Identifier for the NPC
        current_time: Current game time
        location: Current NPC location
        
    Returns:
        Results of the NPC's routine activities
    """
    try:
        logger.info(f"Simulating routine for NPC {npc_id} at {location}...")
        
        # Simulate routine processing time
        time.sleep(1.5)
        
        # Determine routine activity based on time and location
        # This is a simplified example - a real implementation would be more complex
        hour = int(current_time.split(':')[0]) if ':' in current_time else 12
        
        if 6 <= hour < 10:
            activity = "morning preparations"
            new_location = "home"
        elif 10 <= hour < 14:
            activity = "working"
            new_location = "market" if npc_id == "merchant" else "tavern"
        elif 14 <= hour < 18:
            activity = "afternoon business"
            new_location = location  # Stay in current location
        else:
            activity = "evening relaxation"
            new_location = "tavern"
        
        # Determine if NPC needs to satisfy any needs
        needs = []
        if hour in [7, 12, 18]:
            needs.append("hunger")
        if hour >= 22:
            needs.append("rest")
        
        return {
            'npc_id': npc_id,
            'previous_location': location,
            'new_location': new_location,
            'activity': activity,
            'needs_addressed': needs,
            'time': current_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"NPC routine simulation failed: {exc}")
        self.retry(exc=exc)