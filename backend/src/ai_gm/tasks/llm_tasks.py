"""
LLM-related tasks for AI GM Brain.

This module contains Celery tasks for handling language model
interactions asynchronously.
"""

from backend.src.ai_gm.tasks.celery_app import celery_app
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Attempt to import the LLM manager if available
try:
    from backend.src.ai_gm.llm_integration.llm_manager import LLMManager
    llm_available = True
except ImportError:
    logger.warning("LLM manager not available. Using mock responses for development.")
    llm_available = False

@celery_app.task(bind=True, max_retries=3)
def process_llm_request(self, prompt, context=None, model=None, temperature=0.7):
    """
    Process a request to the language model.
    
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
        
        start_time = datetime.utcnow()
        
        if llm_available:
            # Use the actual LLM manager
            llm_manager = LLMManager()
            response = llm_manager.generate_text(
                prompt=prompt,
                context=context,
                model=model,
                temperature=temperature
            )
        else:
            # Simulate processing time for LLM request
            time.sleep(1)
            
            # Create mock LLM response for development
            response = {
                'text': f"This is a mock response to: {prompt[:30]}...\n\nThe AI GM responds with appropriate narrative based on the context.",
                'finish_reason': 'stop',
                'model': model or 'mock-llm-model',
                'tokens_used': len(prompt.split()) + 50  # Rough estimation
            }
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the LLM response with metadata
        return {
            'response': response,
            'prompt_summary': prompt[:50] + "..." if len(prompt) > 50 else prompt,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"LLM request failed: {exc}")
        self.retry(exc=exc, countdown=2)

@celery_app.task(bind=True, max_retries=3)
def generate_npc_dialogue(self, npc_id, dialogue_context, player_input):
    """
    Generate dialogue for an NPC.
    
    Args:
        npc_id: Identifier for the NPC
        dialogue_context: Context for the dialogue generation
        player_input: What the player said
        
    Returns:
        Generated NPC dialogue
    """
    try:
        logger.info(f"Generating dialogue for NPC {npc_id}...")
        
        start_time = datetime.utcnow()
        
        if llm_available:
            # Use the actual LLM manager with a specialized prompt for NPC dialogue
            llm_manager = LLMManager()
            
            # Construct a dialogue-specific prompt
            npc_name = dialogue_context.get('npc_name', 'NPC')
            npc_personality = dialogue_context.get('personality', 'neutral')
            npc_knowledge = dialogue_context.get('knowledge', [])
            relationship = dialogue_context.get('relationship_to_player', 'neutral')
            
            # Create a detailed prompt for the LLM
            prompt = f"""
            Generate dialogue for {npc_name}, who has a {npc_personality} personality.
            Their relationship with the player is: {relationship}.
            They know about: {', '.join(npc_knowledge)}.
            
            The player just said: "{player_input}"
            
            Generate {npc_name}'s response:
            """
            
            response = llm_manager.generate_text(
                prompt=prompt,
                context=dialogue_context,
                temperature=0.8  # Slightly higher creativity for dialogue
            )
            
            dialogue = response.get('text', '')
        else:
            # Simulate processing time for dialogue generation
            time.sleep(1.5)
            
            # Create mock NPC dialogue for development
            npc_name = dialogue_context.get('npc_name', 'NPC')
            npc_personality = dialogue_context.get('personality', 'neutral')
            
            # Generate different responses based on personality
            if npc_personality == 'friendly':
                dialogue = f"[{npc_name} smiles warmly] Ah, good to see you, friend! {player_input.capitalize()}? Well, I'd be happy to help with that!"
            elif npc_personality == 'hostile':
                dialogue = f"[{npc_name} scowls] Hmph. {player_input.capitalize()}? Why should I care about that? Get lost before I lose my patience."
            elif npc_personality == 'mysterious':
                dialogue = f"[{npc_name} speaks softly] {player_input.capitalize()}? Interesting... There are layers to this question that few understand. Perhaps you seek knowledge that was meant to stay hidden..."
            else:
                dialogue = f"[{npc_name} nods] About '{player_input}'? I see. Well, that's something to consider, isn't it?"
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the dialogue with metadata
        return {
            'dialogue': dialogue,
            'npc_id': npc_id,
            'player_input': player_input,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"NPC dialogue generation failed: {exc}")
        self.retry(exc=exc, countdown=2)

@celery_app.task(bind=True, max_retries=2)
def generate_narrative_description(self, scene_context, action_result, narrative_style='standard'):
    """
    Generate a narrative description of a scene or action result.
    
    Args:
        scene_context: Context about the current scene
        action_result: Result of a player action
        narrative_style: Style of narrative (standard, dramatic, terse, etc.)
        
    Returns:
        Generated narrative description
    """
    try:
        logger.info(f"Generating narrative description in {narrative_style} style...")
        
        start_time = datetime.utcnow()
        
        if llm_available:
            # Use the actual LLM manager with a specialized prompt for narrative
            llm_manager = LLMManager()
            
            # Construct a narrative-specific prompt
            location = scene_context.get('location', 'the area')
            time_of_day = scene_context.get('time_of_day', 'day')
            mood = scene_context.get('mood', 'neutral')
            action = action_result.get('action', 'The player did something.')
            outcome = action_result.get('outcome', 'Something happened.')
            
            # Style instructions based on narrative style
            style_instructions = {
                'standard': "Write in a balanced, descriptive style with moderate detail.",
                'dramatic': "Use vivid imagery, metaphors, and emphasize emotional impact. Be theatrical.",
                'terse': "Be brief and to the point. Use short sentences and minimal description.",
                'humorous': "Add wit and humor to the description. Find the comedy in the situation.",
                'poetic': "Use flowery language, rich metaphors, and rhythmic prose."
            }
            
            style_guide = style_instructions.get(narrative_style, style_instructions['standard'])
            
            # Create a detailed prompt for the LLM
            prompt = f"""
            Generate a narrative description of the following scene and action outcome.
            Location: {location}
            Time of day: {time_of_day}
            Mood: {mood}
            
            Player action: {action}
            Outcome: {outcome}
            
            Style guide: {style_guide}
            
            Narrative description:
            """
            
            response = llm_manager.generate_text(
                prompt=prompt,
                context=scene_context,
                temperature=0.7
            )
            
            narrative = response.get('text', '')
        else:
            # Simulate processing time for narrative generation
            time.sleep(1.2)
            
            # Create mock narrative description for development
            location = scene_context.get('location', 'the area')
            time_of_day = scene_context.get('time_of_day', 'day')
            mood = scene_context.get('mood', 'neutral')
            action = action_result.get('action', 'The player did something.')
            outcome = action_result.get('outcome', 'Something happened.')
            
            # Different narratives based on style
            if narrative_style == 'dramatic':
                narrative = f"The {time_of_day} air hangs heavy in {location}, a palpable tension permeating every shadow. As you {action}, fate itself seems to hold its breath. Then, with the inevitability of the tides, {outcome}. The very foundations of reality tremble at this development."
            elif narrative_style == 'terse':
                narrative = f"{time_of_day}. {location}. You {action}. {outcome}. Moving on."
            elif narrative_style == 'humorous':
                narrative = f"Another lovely {time_of_day} in the tourist trap known as {location}! You decide to {action} - because apparently you slept through the 'Common Sense 101' class. Lo and behold, {outcome}. Shocking absolutely nobody."
            else:
                narrative = f"The {time_of_day} in {location} is {mood}. You {action} and as a result, {outcome}."
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the narrative with metadata
        return {
            'narrative': narrative,
            'style': narrative_style,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Narrative description generation failed: {exc}")
        self.retry(exc=exc, countdown=2)

@celery_app.task
def analyze_player_intent(self, player_input, session_history=None):
    """
    Analyze the player's intent from their input.
    
    Args:
        player_input: The text input from the player
        session_history: Optional history of the session for context
        
    Returns:
        Analysis of player intent
    """
    logger.info(f"Analyzing player intent from: {player_input[:50]}...")
    
    # Simulate processing time
    time.sleep(0.8)
    
    # Define common intent categories
    intent_categories = [
        'information_seeking',  # Player wants to know something
        'action_attempt',       # Player tries to do something
        'dialogue',             # Player is talking to an NPC
        'navigation',           # Player wants to move somewhere
        'inventory_management', # Player is managing items
        'combat_related',       # Player is engaging in combat
        'meta_game',            # Player is talking about the game itself
        'emotional_expression'  # Player is expressing feelings
    ]
    
    # Simple keyword-based intent analysis
    # In a real implementation, this would use a more sophisticated NLP approach
    keywords = {
        'information_seeking': ['what', 'who', 'where', 'when', 'why', 'how', 'tell me', 'explain', 'info'],
        'action_attempt': ['use', 'take', 'grab', 'pick', 'open', 'close', 'push', 'pull', 'break', 'craft'],
        'dialogue': ['talk', 'ask', 'tell', 'say', 'speak', 'hello', 'hi', 'greet', 'bye'],
        'navigation': ['go', 'move', 'walk', 'run', 'enter', 'exit', 'leave', 'north', 'south', 'east', 'west'],
        'inventory_management': ['inventory', 'items', 'equip', 'unequip', 'drop', 'store', 'sell', 'buy'],
        'combat_related': ['attack', 'fight', 'kill', 'defend', 'block', 'dodge', 'cast', 'spell'],
        'meta_game': ['save', 'load', 'menu', 'options', 'quit', 'game', 'bug', 'glitch'],
        'emotional_expression': ['feel', 'happy', 'sad', 'angry', 'afraid', 'excited', 'bored', 'love', 'hate']
    }
    
    # Count keyword matches for each category
    input_lower = player_input.lower()
    scores = {category: 0 for category in intent_categories}
    
    for category, words in keywords.items():
        for word in words:
            if f" {word} " in f" {input_lower} ":  # Add spaces to ensure whole word matching
                scores[category] += 1
    
    # Determine primary and secondary intents
    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_intent = sorted_intents[0][0] if sorted_intents[0][1] > 0 else 'unclear'
    secondary_intent = sorted_intents[1][0] if len(sorted_intents) > 1 and sorted_intents[1][1] > 0 else None
    
    # Extract potential targets of the intent
    # This is a simplified approach - a real implementation would use NLP parsing
    import re
    
    # Look for nouns/objects after verbs
    target_patterns = [
        r"(?:use|take|open|close|examine|look at|talk to|ask|tell) (the |a |an )?(\w+)",
        r"(?:go|move|walk|run) (?:to |toward |towards |into )?(the |a |an )?(\w+)"
    ]
    
    potential_targets = []
    for pattern in target_patterns:
        matches = re.findall(pattern, input_lower)
        for match in matches:
            # Extract the actual noun, ignoring articles
            if len(match) > 1:
                potential_targets.append(match[-1])  # Last group contains the noun
    
    # Determine emotional tone
    positive_words = ['please', 'thanks', 'kind', 'good', 'nice', 'happy', 'excited']
    negative_words = ['stupid', 'hate', 'bad', 'dumb', 'annoying', 'frustrated', 'angry']
    
    positive_count = sum(1 for word in positive_words if f" {word} " in f" {input_lower} ")
    negative_count = sum(1 for word in negative_words if f" {word} " in f" {input_lower} ")
    
    if positive_count > negative_count:
        emotional_tone = 'positive'
    elif negative_count > positive_count:
        emotional_tone = 'negative'
    else:
        emotional_tone = 'neutral'
    
    # Determine complexity of the request
    words = input_lower.split()
    complexity = 'simple' if len(words) < 5 else 'moderate' if len(words) < 10 else 'complex'
    
    return {
        'primary_intent': primary_intent,
        'secondary_intent': secondary_intent,
        'potential_targets': potential_targets,
        'emotional_tone': emotional_tone,
        'complexity': complexity,
        'input_summary': player_input[:50] + "..." if len(player_input) > 50 else player_input,
        'confidence_score': sorted_intents[0][1] / max(sum(scores.values()), 1),  # Normalized confidence
        'timestamp': datetime.utcnow().isoformat()
    }