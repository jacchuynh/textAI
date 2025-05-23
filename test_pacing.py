"""
Test module for the Pacing and Ambient Storytelling System

This test demonstrates how the pacing system:
1. Tracks player activity and pacing state
2. Generates ambient narrative during lulls
3. Initiates NPC dialogue during player idle times
4. Summarizes events to maintain concise context
"""

import asyncio
import json
from datetime import datetime, timedelta
from backend.src.ai_gm.pacing import (
    PacingManager, 
    IdleNPCManager, 
    EventSummarizer, 
    PacingIntegration,
    PacingState,
    AmbientTrigger
)

# Simulation context (would be provided by the game in a real scenario)
SIMULATION_CONTEXT = {
    'current_location': 'Rusted Tavern',
    'player_id': 'player_123',
    'session_id': 'test_session_001',
    'current_season': 'autumn',
    'time_of_day': 'evening',
    'present_npcs': ['barkeeper', 'old_merchant', 'mysterious_stranger'],
    'npcs': {
        'barkeeper': {
            'name': 'Darius',
            'personality': 'friendly',
            'occupation': 'tavern owner'
        },
        'old_merchant': {
            'name': 'Geralt',
            'personality': 'wise',
            'occupation': 'retired merchant'
        },
        'mysterious_stranger': {
            'name': 'Shadowcloak',
            'personality': 'suspicious',
            'occupation': 'unknown'
        }
    },
    'world_state': {
        'political_stability': 'unrest',
        'economic_status': 'struggling',
        'local_threats': ['bandit activity', 'wolf pack']
    },
    'location_context': {
        'dominant_aura': 'welcoming',
        'notable_features': ['warm fireplace', 'trophy wall', 'wooden bar']
    },
    'player_reputation_summary': 'generally respected in town'
}

# Mock player interactions for testing
MOCK_INTERACTIONS = [
    {
        'input': 'I look around the tavern',
        'response': {
            'response_text': 'The Rusted Tavern is warm and inviting, with a crackling fireplace that casts dancing shadows across the wooden floors. Several patrons are scattered about, including Darius the barkeeper who polishes glasses behind the bar, an old merchant named Geralt sitting in the corner, and a mysterious cloaked figure who keeps to themselves.',
            'metadata': {
                'event_type': 'ENVIRONMENT_OBSERVED',
                'command_parser': {'success': True}
            }
        }
    },
    {
        'input': 'I approach the barkeeper',
        'response': {
            'response_text': 'You walk up to the wooden bar where Darius is working. He looks up with a friendly smile and sets aside the glass he was polishing.',
            'metadata': {
                'event_type': 'MOVEMENT',
                'command_parser': {'success': True}
            }
        }
    },
    {
        'input': 'Ask about recent news',
        'response': {
            'response_text': '"News, eh?" Darius leans in slightly. "Well, there\'s been talk of increased bandit activity on the north road. The town guard doubled their patrols, but they\'re stretched thin. And there\'s strange rumors about lights seen in the abandoned mines. Some say it\'s just miners looking for leftover ore, others think it\'s something... unnatural."',
            'metadata': {
                'event_type': 'CONVERSATION_STARTED',
                'decision_tree': {
                    'response_basis': 'LLM_CONVERSATION_FLOW',
                    'action_taken': 'engage_dialogue',
                    'success': True
                }
            }
        }
    }
]

# Significant events for summarization
SIGNIFICANT_EVENTS = [
    {
        'event_type': 'NARRATIVE_BRANCH_INITIATED',
        'context': {'branch_name': 'The Abandoned Mine Mystery'},
        'actor': 'player_123'
    },
    {
        'event_type': 'SIGNIFICANT_ACTION_RECORDED',
        'context': {'action': 'discovered hidden entrance', 'location': 'north mine shaft'},
        'actor': 'player_123'
    },
    {
        'event_type': 'WORLD_REACTION_ASSESSED',
        'context': {'target_entity': 'Miners Guild', 'reaction': 'increased suspicion'},
        'actor': 'player_123'
    },
    {
        'event_type': 'BRANCH_ACTION_EXECUTED',
        'context': {'action': 'investigate strange sounds', 'skill_check_result': {'success': True}},
        'actor': 'player_123'
    },
    {
        'event_type': 'DECISION_MADE',
        'context': {'priority_used': 'PLOT_PROGRESSION', 'outcome': 'confrontation with cultists'},
        'actor': 'player_123'
    }
]

async def test_pacing_manager():
    """Test the PacingManager's ambient narrative generation"""
    print("\n=== Testing PacingManager ===")
    
    pacing_manager = PacingManager()
    
    # Simulate player interactions to establish baseline
    for interaction in MOCK_INTERACTIONS:
        pacing_manager.update_player_activity(
            interaction['input'], 
            interaction['response'], 
            SIMULATION_CONTEXT
        )
        
    print(f"Current pacing state: {pacing_manager.current_metrics.current_pacing_state}")
    
    # Simulate time passing (lull in activity)
    pacing_manager.current_metrics.last_significant_event = datetime.utcnow() - timedelta(minutes=15)
    pacing_manager.current_metrics.last_player_input = datetime.utcnow() - timedelta(minutes=5)
    pacing_manager.current_metrics.current_pacing_state = PacingState.LULL
    
    # Check if ambient content should be generated
    should_inject, trigger = pacing_manager.should_inject_ambient_content(SIMULATION_CONTEXT)
    print(f"Should inject ambient content: {should_inject}, Trigger: {trigger}")
    
    if should_inject and trigger:
        # Generate ambient content
        ambient_content = pacing_manager.generate_ambient_content(trigger, SIMULATION_CONTEXT)
        print(f"Generated ambient content: {ambient_content}")
    
    # Get statistics
    stats = pacing_manager.get_pacing_statistics()
    print("Pacing statistics:", json.dumps(stats, indent=2))

async def test_idle_npc_manager():
    """Test the IdleNPCManager's NPC-initiated dialogue"""
    print("\n=== Testing IdleNPCManager ===")
    
    idle_npc_manager = IdleNPCManager()
    
    # Simulate idle time
    time_since_last_input = timedelta(minutes=5)
    
    # Check each NPC for potential initiative
    for npc_id in SIMULATION_CONTEXT['present_npcs']:
        should_initiate, dialogue_theme = idle_npc_manager.should_npc_initiate(
            npc_id, 
            SIMULATION_CONTEXT,
            time_since_last_input
        )
        
        print(f"NPC {npc_id} should initiate: {should_initiate}, Theme: {dialogue_theme}")
        
        if should_initiate and dialogue_theme:
            npc_dialogue = await idle_npc_manager.generate_npc_initiative(
                npc_id,
                dialogue_theme,
                SIMULATION_CONTEXT
            )
            
            if npc_dialogue:
                print(f"NPC dialogue: {npc_dialogue['response_text']}")
    
    # Get statistics
    stats = idle_npc_manager.get_idle_npc_statistics()
    print("NPC initiative statistics:", json.dumps(stats, indent=2))

async def test_event_summarizer():
    """Test the EventSummarizer's event summarization functionality"""
    print("\n=== Testing EventSummarizer ===")
    
    event_summarizer = EventSummarizer()
    
    # Add significant events for summarization
    for event in SIGNIFICANT_EVENTS:
        event_summarizer.add_event_for_summarization(event)
    
    # Force event summarization
    event_summarizer.events_since_last_summary = [
        {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event['event_type'],
            'description': event_summarizer._create_event_description(event),
            'significance': event_summarizer._rate_event_significance(event)
        }
        for event in SIGNIFICANT_EVENTS
    ]
    
    print(f"Events pending summarization: {len(event_summarizer.events_since_last_summary)}")
    
    # Create summary
    summary = await event_summarizer.create_summary(SIMULATION_CONTEXT['session_id'])
    print(f"Generated summary: {summary}")
    
    # Get story context after summarization
    story_context = event_summarizer.get_current_story_context()
    print("Story context:")
    print(json.dumps(story_context, indent=2))
    
    # Get statistics
    stats = event_summarizer.get_summarization_statistics()
    print("Summarization statistics:", json.dumps(stats, indent=2))

async def test_pacing_integration():
    """Test the PacingIntegration component that ties everything together"""
    print("\n=== Testing PacingIntegration ===")
    
    # Initialize pacing integration
    pacing_integration = PacingIntegration()
    
    # Simulate player activity
    print("Simulating player interactions...")
    for interaction in MOCK_INTERACTIONS:
        pacing_integration.on_player_input(interaction['input'])
        pacing_integration.on_ai_response(
            interaction['input'], 
            interaction['response'], 
            SIMULATION_CONTEXT
        )
        await asyncio.sleep(0.1)  # Simulate time passing
    
    print("Simulating passage of time (idle period)...")
    
    # Manually adjust last input time to simulate idle period
    pacing_integration.last_input_time = datetime.utcnow() - timedelta(minutes=7)
    
    # Check for ambient content
    print("Checking for ambient content...")
    ambient_content = await pacing_integration.check_and_inject_ambient_content(
        SIMULATION_CONTEXT
    )
    
    if ambient_content:
        print(f"Ambient content: {ambient_content['response_text']}")
    else:
        print("No ambient content generated")
    
    # Check for NPC initiative
    print("Checking for NPC initiative...")
    npc_initiative = await pacing_integration.check_for_npc_initiative(
        SIMULATION_CONTEXT
    )
    
    if npc_initiative:
        print(f"NPC initiative: {npc_initiative['response_text']}")
    else:
        print("No NPC initiative generated")
    
    # Add events for summarization
    for event in SIGNIFICANT_EVENTS:
        pacing_integration.event_summarizer.add_event_for_summarization(event)
    
    # Force conditions for summarization
    pacing_integration.event_summarizer.events_since_last_summary = [
        {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event['event_type'],
            'description': pacing_integration.event_summarizer._create_event_description(event),
            'significance': pacing_integration.event_summarizer._rate_event_significance(event)
        }
        for event in SIGNIFICANT_EVENTS
    ]
    
    # Create event summary
    print("Creating event summary...")
    summary = await pacing_integration.check_and_create_event_summary(
        SIMULATION_CONTEXT['session_id']
    )
    
    if summary:
        print(f"Event summary: {summary}")
    else:
        print("No summary generated")
    
    # Get enhanced context
    enhanced_context = pacing_integration.get_enhanced_context(SIMULATION_CONTEXT)
    print("Enhanced context additions:")
    for key in ['time_since_last_input', 'current_pacing_state', 'story_summary']:
        if key in enhanced_context:
            print(f"- {key}: {enhanced_context[key]}")
    
    # Get combined statistics
    stats = pacing_integration.get_pacing_statistics()
    print("Pacing integration statistics overview:")
    for component, component_stats in stats.items():
        print(f"- {component}: {len(component_stats)} metrics")

async def main():
    """Run all tests"""
    print("=== Testing Pacing and Ambient Storytelling System ===\n")
    
    await test_pacing_manager()
    await test_idle_npc_manager()
    await test_event_summarizer()
    await test_pacing_integration()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(main())