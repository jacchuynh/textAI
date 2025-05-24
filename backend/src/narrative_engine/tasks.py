"""
Narrative Engine Celery Tasks

This module contains Celery tasks for handling asynchronous narrative processing.
Tasks are categorized by their function within the narrative engine.
"""

from backend.src.ai_gm.tasks.celery_app import celery_app
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

# Import narrative engine components if available
try:
    from backend.src.narrative_engine.narrative_generator import CombatNarrativeGenerator
    from backend.src.narrative_engine.narrative_context_manager import NarrativeContextManager
    from backend.src.narrative_engine.world_state import WorldState
    narrative_components_available = True
except ImportError:
    logger.warning("Narrative engine components not available. Using mock responses for development.")
    narrative_components_available = False

# Try to import LLM manager for dialogue generation
try:
    from backend.src.ai_gm.llm_integration.llm_manager import LLMManager
    llm_available = True
except ImportError:
    logger.warning("LLM manager not available. Using mock responses for dialogue generation.")
    llm_available = False

#########################
# Narrative Generation Tasks
#########################

@celery_app.task(bind=True, max_retries=3)
def generate_combat_narrative(self, combat_result: Dict[str, Any], 
                              actor: Dict[str, Any], 
                              target: Dict[str, Any],
                              environment_tags: List[str],
                              memory_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate narrative descriptions for a combat encounter asynchronously.
    
    Args:
        combat_result: The result of the combat calculation
        actor: The character performing the action
        target: The target of the action
        environment_tags: Environmental factors affecting the combat
        memory_context: Optional historical context between combatants
        
    Returns:
        Dictionary containing narrative descriptions
    """
    try:
        logger.info(f"Generating combat narrative for {actor.get('name', 'unknown')} vs {target.get('name', 'unknown')}...")
        
        start_time = datetime.utcnow()
        
        if narrative_components_available:
            # Use the actual narrative generator
            generator = CombatNarrativeGenerator()
            # Since this is a Celery task, we need to handle the async call synchronously
            import asyncio
            narrative = asyncio.run(generator.generate_combat_narrative(
                combat_result=combat_result,
                actor=actor,
                target=target,
                environment_tags=environment_tags,
                memory_context=memory_context
            ))
        else:
            # Simulate processing time
            time.sleep(1.5)
            
            # Create mock narrative for development
            narrative = {
                "action_description": f"{actor.get('name', 'The attacker')} performs {combat_result.get('actor_move', 'an attack')} against {target.get('name', 'the defender')}.",
                "environment_description": f"The {environment_tags[0] if environment_tags else 'environment'} affects the combat.",
                "consequence_description": "This action may have lasting consequences.",
                "emotion_description": f"{actor.get('name', 'The attacker')} feels determined.",
                "memory_callback": "There is history between these combatants."
            }
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the narrative with metadata
        return {
            'narrative': narrative,
            'combat_id': combat_result.get('id', 'unknown'),
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Combat narrative generation failed: {exc}")
        self.retry(exc=exc, countdown=2)

@celery_app.task(bind=True, max_retries=3)
def generate_npc_dialogue(self, npc_data: Dict[str, Any], 
                         dialogue_context: Dict[str, Any], 
                         player_input: str) -> Dict[str, Any]:
    """
    Generate dialogue for an NPC asynchronously.
    
    Args:
        npc_data: Data about the NPC
        dialogue_context: Context for the dialogue
        player_input: Player's input or question
        
    Returns:
        Generated dialogue response
    """
    try:
        npc_id = npc_data.get('id', 'unknown')
        logger.info(f"Generating dialogue for NPC {npc_id}...")
        
        start_time = datetime.utcnow()
        
        if llm_available:
            # Use LLM manager for dialogue generation
            llm_manager = LLMManager()
            
            # Prepare the prompt
            npc_name = npc_data.get('name', 'NPC')
            npc_personality = npc_data.get('personality', 'neutral')
            npc_knowledge = npc_data.get('knowledge', [])
            relationship = dialogue_context.get('relationship', 'neutral')
            
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
                temperature=0.8
            )
            
            dialogue = response.get('text', '')
        else:
            # Simulate processing time
            time.sleep(1.2)
            
            # Generate mock dialogue based on personality
            npc_name = npc_data.get('name', 'NPC')
            npc_personality = npc_data.get('personality', 'neutral')
            
            if npc_personality == 'friendly':
                dialogue = f"[{npc_name} smiles] Ah, I'm glad you asked about that! {player_input.capitalize()}? Let me help you with that."
            elif npc_personality == 'hostile':
                dialogue = f"[{npc_name} glares] Why should I tell you about {player_input.lower()}? Mind your own business."
            elif npc_personality == 'mysterious':
                dialogue = f"[{npc_name} speaks cryptically] {player_input.capitalize()}? Some secrets are best left undiscovered... but perhaps I can share a fragment of truth."
            else:
                dialogue = f"[{npc_name} responds] About {player_input}? I suppose I can tell you what I know."
        
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
def generate_narrative_branch(self, 
                            branch_point_id: str, 
                            context: Dict[str, Any], 
                            character_data: Dict[str, Any],
                            available_options: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate narrative branch options for a choice point.
    
    Args:
        branch_point_id: Identifier for the narrative branch point
        context: Current narrative context
        character_data: Player character data affecting choices
        available_options: Pre-defined available options
        
    Returns:
        Enhanced narrative branch with descriptions and consequences
    """
    try:
        logger.info(f"Generating narrative branch for point {branch_point_id}...")
        
        start_time = datetime.utcnow()
        
        # In a real implementation, this would use actual narrative branch generation logic
        # Simulate processing time for complex branch generation
        time.sleep(2)
        
        # Mock branch generation
        enhanced_options = []
        
        for option in available_options:
            # Enhance each option with more detailed description and consequences
            option_id = option.get('id', 'unknown')
            option_text = option.get('text', 'Make a choice')
            
            # Calculate character-specific outcomes
            character_domains = character_data.get('domains', {})
            primary_domain = max(character_domains.items(), key=lambda x: x[1])[0] if character_domains else "Unknown"
            
            # Determine success chance based on character domains
            relevant_domain = option.get('relevant_domain')
            success_chance = 0.5  # Default
            if relevant_domain and relevant_domain in character_domains:
                domain_value = character_domains[relevant_domain]
                success_chance = min(0.9, 0.4 + (domain_value / 100))
            
            enhanced_options.append({
                'id': option_id,
                'text': option_text,
                'enhanced_description': f"{option_text} This choice will test your {relevant_domain or 'abilities'}.",
                'predicted_outcome': f"Your {primary_domain} expertise may influence the outcome.",
                'success_chance': success_chance,
                'consequence_preview': option.get('consequence_preview', 'This choice will have consequences.')
            })
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the enhanced branch with metadata
        return {
            'branch_point_id': branch_point_id,
            'enhanced_options': enhanced_options,
            'context_summary': "Current narrative context: " + context.get('summary', 'In progress'),
            'character_domains_analysis': f"Your {primary_domain} expertise will be particularly valuable in this situation.",
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Narrative branch generation failed: {exc}")
        self.retry(exc=exc, countdown=2)

#########################
# World State Update Tasks
#########################

@celery_app.task
def update_world_state(world_data: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Update the world state based on narrative events.
    
    Args:
        world_data: Current world state data
        events: List of events that affect the world
        
    Returns:
        Updated world state
    """
    logger.info(f"Updating world state with {len(events)} events...")
    
    # Simulate processing time for complex world updates
    time.sleep(1.5)
    
    # Mock world state update
    # In a real implementation, this would use WorldState logic
    updated_world = world_data.copy()
    
    # Process each event's impact on the world
    for event in events:
        event_type = event.get('type', 'unknown')
        event_location = event.get('location', 'unknown')
        event_magnitude = event.get('magnitude', 1)
        
        # Update faction relationships
        if event_type == 'faction_conflict':
            faction1 = event.get('faction1')
            faction2 = event.get('faction2')
            
            if faction1 and faction2 and 'factions' in updated_world:
                # Worsen relationship between factions
                if faction1 in updated_world['factions'] and faction2 in updated_world['factions']:
                    relationship_key = f"{faction1}_{faction2}_relation"
                    current_relation = updated_world.get(relationship_key, 0)
                    updated_world[relationship_key] = max(-100, current_relation - (event_magnitude * 5))
        
        # Update location atmosphere
        if 'locations' in updated_world and event_location in updated_world['locations']:
            location_data = updated_world['locations'][event_location]
            
            if event_type == 'battle':
                location_data['danger_level'] = min(100, location_data.get('danger_level', 50) + (event_magnitude * 10))
                location_data['atmosphere'] = 'tense'
            elif event_type == 'celebration':
                location_data['prosperity'] = min(100, location_data.get('prosperity', 50) + (event_magnitude * 5))
                location_data['atmosphere'] = 'jubilant'
            elif event_type == 'disaster':
                location_data['prosperity'] = max(0, location_data.get('prosperity', 50) - (event_magnitude * 15))
                location_data['danger_level'] = min(100, location_data.get('danger_level', 50) + (event_magnitude * 20))
                location_data['atmosphere'] = 'devastated'
    
    # Update global world properties
    # Example: Advance world time
    if 'current_time' in updated_world:
        hours_passed = sum(event.get('time_advance', 0) for event in events)
        if hours_passed > 0:
            current_time = updated_world['current_time']
            # In a real implementation, this would use proper datetime logic
            updated_world['current_time'] = current_time + hours_passed
    
    return {
        'updated_world_state': updated_world,
        'events_processed': len(events),
        'timestamp': datetime.utcnow().isoformat()
    }

#########################
# Relationship System Tasks
#########################

@celery_app.task
def update_relationship_network(character_id: str, 
                              action_data: Dict[str, Any],
                              affected_npcs: List[str]) -> Dict[str, Any]:
    """
    Update relationship network based on character actions.
    
    Args:
        character_id: Identifier for the character
        action_data: Details of the character's action
        affected_npcs: NPCs affected by the action
        
    Returns:
        Updated relationship information
    """
    logger.info(f"Updating relationship network for character {character_id}...")
    
    # Simulate processing time
    time.sleep(1.5)
    
    # Mock relationship update
    # In a real implementation, this would use the relationship system logic
    
    action_type = action_data.get('type', 'unknown')
    action_context = action_data.get('context', {})
    action_target = action_data.get('target', 'unknown')
    
    relationship_changes = {}
    relationship_cascades = {}
    
    # Calculate direct relationship changes
    for npc_id in affected_npcs:
        # Different impact based on action type
        if action_type == 'help':
            relationship_changes[npc_id] = 10
        elif action_type == 'harm':
            relationship_changes[npc_id] = -15
        elif action_type == 'trade':
            relationship_changes[npc_id] = 5
        elif action_type == 'steal':
            relationship_changes[npc_id] = -20
        else:
            relationship_changes[npc_id] = 0
    
    # Calculate relationship cascades (how this affects NPCs related to the affected NPCs)
    # In a real implementation, this would use a social graph
    if action_target in affected_npcs:
        # Mock social connections
        npc_connections = {
            'merchant_1': ['guard_1', 'merchant_2'],
            'guard_1': ['guard_captain', 'merchant_1'],
            'innkeeper': ['bard', 'server', 'patron_1'],
            'villager_1': ['villager_2', 'farmer_1']
        }
        
        if action_target in npc_connections:
            for connected_npc in npc_connections[action_target]:
                # Connected NPCs are affected less strongly
                change = relationship_changes.get(action_target, 0)
                relationship_cascades[connected_npc] = int(change * 0.4)  # 40% of the main effect
    
    return {
        'character_id': character_id,
        'action_type': action_type,
        'direct_changes': relationship_changes,
        'cascade_changes': relationship_cascades,
        'timestamp': datetime.utcnow().isoformat()
    }

#########################
# Event Bus Tasks
#########################

@celery_app.task
def process_event_queue(event_queue: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process a queue of events from the event bus.
    
    Args:
        event_queue: List of events to process
        
    Returns:
        Results of event processing
    """
    logger.info(f"Processing event queue with {len(event_queue)} events...")
    
    # Simulate processing time
    time.sleep(1)
    
    # Mock event queue processing
    # In a real implementation, this would use the event bus logic
    
    processed_events = []
    triggered_events = []
    errors = []
    
    for event in event_queue:
        event_id = event.get('id', 'unknown')
        event_type = event.get('type', 'unknown')
        
        try:
            # Process the event (simulate successful processing)
            processed_events.append({
                'id': event_id,
                'type': event_type,
                'status': 'processed',
                'processed_at': datetime.utcnow().isoformat()
            })
            
            # Check if this event triggers other events
            if event_type == 'faction_attacked' and event.get('magnitude', 0) > 5:
                # High-magnitude faction attack triggers retaliation
                triggered_events.append({
                    'type': 'faction_retaliation',
                    'source_event': event_id,
                    'target_faction': event.get('attacker'),
                    'magnitude': event.get('magnitude') * 0.8
                })
            elif event_type == 'item_discovered' and event.get('item_rarity', '') == 'legendary':
                # Discovering legendary items affects the market
                triggered_events.append({
                    'type': 'market_shift',
                    'source_event': event_id,
                    'item_category': event.get('item_category'),
                    'price_multiplier': 1.5
                })
        except Exception as e:
            errors.append({
                'event_id': event_id,
                'error': str(e)
            })
    
    return {
        'processed_count': len(processed_events),
        'processed_events': processed_events,
        'triggered_events': triggered_events,
        'errors': errors,
        'timestamp': datetime.utcnow().isoformat()
    }