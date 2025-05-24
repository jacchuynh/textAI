"""
LLM-related tasks for AI GM Brain.

This module contains Celery tasks for handling asynchronous
language model processing.
"""

from backend.src.ai_gm.tasks.celery_app import celery_app
import logging
import time
import json

logger = logging.getLogger(__name__)

# Attempt to import the LLM manager if available
try:
    from backend.src.ai_gm.ai_gm_llm_manager import LLMManager
    llm_manager_available = True
except ImportError:
    logger.warning("LLMManager not available. Using mock responses for development.")
    llm_manager_available = False

@celery_app.task(bind=True, max_retries=3, retry_backoff=True)
def process_llm_request(self, prompt, context=None, model=None, temperature=0.7):
    """
    Process an LLM request asynchronously.
    
    Args:
        prompt: The text prompt to send to the LLM
        context: Additional context for the LLM
        model: Specific model to use (optional)
        temperature: Creativity parameter
        
    Returns:
        LLM response
    """
    try:
        logger.info(f"Processing LLM request: {prompt[:50]}...")
        
        if llm_manager_available:
            llm_manager = LLMManager()
            result = llm_manager.generate_text(prompt, context, model, temperature)
        else:
            # Log that we'd normally make an API call here
            logger.info(f"Would call LLM API with prompt: {prompt[:100]}...")
            # Simulate processing time
            time.sleep(2)
            # Create a mock response for development
            result = f"This is a simulated LLM response to: {prompt[:50]}..."
        
        return {
            'success': True,
            'response': result,
            'metadata': {
                'model': model,
                'temperature': temperature
            }
        }
    except Exception as exc:
        logger.error(f"LLM request failed: {exc}")
        self.retry(exc=exc, countdown=5)

@celery_app.task(bind=True, max_retries=2)
def generate_npc_dialogue(self, npc_id, dialogue_context, player_input):
    """
    Generate dialogue for an NPC based on context and player input.
    
    Args:
        npc_id: Identifier for the NPC
        dialogue_context: Context for the dialogue generation
        player_input: What the player said
        
    Returns:
        Generated NPC dialogue
    """
    try:
        logger.info(f"Generating dialogue for NPC {npc_id} responding to: {player_input[:50]}...")
        
        # Format the prompt for the LLM
        prompt = (
            f"Generate dialogue for NPC {npc_id} responding to '{player_input}' "
            f"with the following context: {json.dumps(dialogue_context)}"
        )
        
        # Call the LLM processing task
        result = process_llm_request.delay(
            prompt=prompt,
            context={"type": "dialogue", "npc_id": npc_id},
            temperature=0.8
        ).get(timeout=30)
        
        if result and result.get('success'):
            return {
                'npc_id': npc_id,
                'dialogue': result['response'],
                'metadata': {
                    'context_used': dialogue_context,
                    'player_input': player_input
                }
            }
        else:
            raise Exception(f"Failed to generate dialogue: {result}")
            
    except Exception as exc:
        logger.error(f"NPC dialogue generation failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def generate_narrative_branch(self, branch_context, player_choices, world_state):
    """
    Generate a narrative branch based on player choices and world state.
    
    Args:
        branch_context: Context for the narrative branch
        player_choices: Previous choices made by the player
        world_state: Current state of the game world
        
    Returns:
        Generated narrative branch options
    """
    try:
        logger.info(f"Generating narrative branch for context: {branch_context[:50]}...")
        
        # Format prompt for narrative generation
        prompt = (
            f"Create a narrative branch based on the following context: {json.dumps(branch_context)}. "
            f"The player has previously made these choices: {json.dumps(player_choices)}. "
            f"Consider the current world state: {json.dumps(world_state)}. "
            f"Generate 2-3 possible narrative paths forward with their consequences."
        )
        
        # Call the LLM processing task
        result = process_llm_request.delay(
            prompt=prompt,
            context={"type": "narrative_branch"},
            temperature=0.9  # Higher creativity for narrative
        ).get(timeout=45)
        
        if result and result.get('success'):
            # Process the narrative response
            # In a real implementation, you might parse this into structured options
            return {
                'narrative_options': result['response'],
                'branch_context': branch_context,
                'metadata': {
                    'player_choices': player_choices,
                    'world_state_snapshot': world_state
                }
            }
        else:
            raise Exception(f"Failed to generate narrative branch: {result}")
            
    except Exception as exc:
        logger.error(f"Narrative branch generation failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def generate_world_event(self, event_trigger, location, time_of_day, active_npcs, world_state):
    """
    Generate a dynamic world event based on the current game state.
    
    Args:
        event_trigger: What triggered this event
        location: Where the event occurs
        time_of_day: When the event occurs
        active_npcs: NPCs who might be involved
        world_state: Current state of the game world
        
    Returns:
        Generated world event
    """
    try:
        logger.info(f"Generating world event based on trigger: {event_trigger}...")
        
        # Format prompt for event generation
        prompt = (
            f"Generate a dynamic world event for location '{location}' during {time_of_day}. "
            f"The event was triggered by: {event_trigger}. "
            f"These NPCs are present: {json.dumps(active_npcs)}. "
            f"Consider the current world state: {json.dumps(world_state)}. "
            f"Describe what happens, who is involved, and potential consequences."
        )
        
        # Call the LLM processing task
        result = process_llm_request.delay(
            prompt=prompt,
            context={"type": "world_event", "location": location},
            temperature=0.85
        ).get(timeout=40)
        
        if result and result.get('success'):
            return {
                'event_description': result['response'],
                'location': location,
                'time_of_day': time_of_day,
                'involved_npcs': active_npcs,
                'trigger': event_trigger
            }
        else:
            raise Exception(f"Failed to generate world event: {result}")
            
    except Exception as exc:
        logger.error(f"World event generation failed: {exc}")
        self.retry(exc=exc)