"""
Simplified test for AI GM Brain Pacing Integration

This test demonstrates the pacing system's core features working with
domain and combat systems without relying on extensive dependencies.
"""

import asyncio
import json
from datetime import datetime, timedelta

# Import the pacing components directly for testing
from backend.src.ai_gm.pacing.pacing_manager import PacingManager, PacingState, AmbientTrigger
from backend.src.ai_gm.pacing.idle_npc_manager import IdleNPCManager
from backend.src.ai_gm.pacing.event_summarizer import EventSummarizer
from backend.src.ai_gm.pacing.pacing_integration import PacingIntegration


# Test context with domain and combat info
TEST_CONTEXT = {
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
    'player_reputation_summary': 'generally respected in town',
    
    # Domain system information
    'domains': {
        'active': ['PERCEPTION', 'SOCIAL', 'KNOWLEDGE'],
        'recent_outcomes': {
            'PERCEPTION': {'success': True, 'margin': 2},
            'SOCIAL': {'success': True, 'margin': 1},
            'KNOWLEDGE': {'success': False, 'margin': -1}
        }
    },
    
    # Combat system information
    'combat_data': {
        'in_combat': False,
        'available_actions': ['attack', 'defend', 'special_move'],
        'combatants': [
            {
                'id': 'player_123',
                'name': 'Player',
                'health': 100,
                'status': 'ready'
            },
            {
                'id': 'mysterious_stranger',
                'name': 'Shadowcloak',
                'health': 80,
                'status': 'alert'
            }
        ]
    }
}

# Mock player inputs
MOCK_INPUTS = [
    "I look around the tavern carefully",
    "I approach the barkeeper and ask about local rumors",
    "I try to recall what I know about this town's history"
]

# Mock responses
MOCK_RESPONSES = [
    {
        'response_text': "The Rusted Tavern is warm and inviting, with a crackling fireplace that casts dancing shadows across the wooden floors. Several patrons are scattered about, including Darius the barkeeper who polishes glasses behind the bar, an old merchant named Geralt sitting in the corner, and a mysterious cloaked figure who keeps to themselves.",
        'metadata': {
            'event_type': 'ENVIRONMENT_OBSERVED',
            'domain': 'PERCEPTION',
            'success': True
        }
    },
    {
        'response_text': "\"Rumors, eh?\" Darius leans in slightly. \"Well, there's been talk of increased bandit activity on the north road. The town guard doubled their patrols, but they're stretched thin. And there's strange rumors about lights seen in the abandoned mines. Some say it's just miners looking for leftover ore, others think it's something... unnatural.\"",
        'metadata': {
            'event_type': 'CONVERSATION',
            'domain': 'SOCIAL',
            'success': True
        }
    },
    {
        'response_text': "You rack your brain trying to remember details about this town's history. You recall that it was founded about a century ago as a mining settlement, but the mines began to dry up around twenty years ago. The town has struggled economically since then, with many residents leaving for more prosperous regions.",
        'metadata': {
            'event_type': 'KNOWLEDGE_RECALL',
            'domain': 'KNOWLEDGE',
            'success': True
        }
    }
]


async def test_pacing_with_domain_integration():
    """Test pacing system with domain integration"""
    print("\n=== Testing Pacing with Domain Integration ===")
    
    # Create PacingIntegration
    pacing = PacingIntegration()
    
    # Simulate player activity
    print("Simulating player interactions with domain usage...")
    for i, input_text in enumerate(MOCK_INPUTS):
        # Update on player input
        pacing.on_player_input(input_text)
        
        # Get corresponding response for this input
        if i < len(MOCK_RESPONSES):
            response = MOCK_RESPONSES[i]
        else:
            response = {'response_text': f"Response to: {input_text}", 'metadata': {}}
        
        # Update with AI response
        pacing.on_ai_response(input_text, response, TEST_CONTEXT)
        
        # Print what's happening
        domain = response.get('metadata', {}).get('domain', 'unknown')
        print(f"Player used domain: {domain}")
        
        # Small delay to simulate time passing
        await asyncio.sleep(0.2)
    
    # Get enhanced context with pacing data
    enhanced_context = pacing.get_enhanced_context(TEST_CONTEXT)
    
    # Print the domain-relevant pacing data
    print("\nDomain-relevant pacing data:")
    
    domain_keys = ['time_since_last_input', 'current_pacing_state', 'story_summary']
    for key in domain_keys:
        if key in enhanced_context:
            print(f"  {key}: {enhanced_context[key]}")
    
    # Simulate passage of time for potential ambient content
    pacing.last_input_time = datetime.utcnow() - timedelta(minutes=5)
    
    # Check for ambient content
    ambient_content = await pacing.check_and_inject_ambient_content(TEST_CONTEXT)
    
    if ambient_content:
        print(f"\nAmbient content would be injected: {ambient_content['response_text']}")
    else:
        print("\nNo ambient content triggered")
    
    return enhanced_context


async def test_pacing_with_combat_integration():
    """Test pacing system with combat integration"""
    print("\n=== Testing Pacing with Combat Integration ===")
    
    # Create PacingIntegration
    pacing = PacingIntegration()
    
    # Create combat context
    combat_context = TEST_CONTEXT['combat_data'].copy()
    combat_context['in_combat'] = True  # Set to active combat
    
    # Enhance combat context
    print("Enhancing combat context with pacing data...")
    
    # Simulate fast-paced player
    pacing.last_input_time = datetime.utcnow() - timedelta(seconds=15)
    
    # Set pacing manager state to ACTIVE
    pacing.pacing_manager.current_metrics.current_pacing_state = PacingState.ACTIVE
    
    # Add pacing-relevant combat data
    combat_enhanced = await pacing.integrate_with_combat_system(combat_context)
    
    print("\nCombat-relevant pacing data:")
    print(f"  Combat pace modifier: {combat_enhanced.get('combat_pace_modifier', 'unknown')}")
    
    # Check that ambient content and NPC initiatives are suppressed during combat
    ambient_content = await pacing.check_and_inject_ambient_content(combat_context)
    npc_initiative = await pacing.check_for_npc_initiative(combat_context)
    
    print(f"  Ambient content suppressed during combat: {ambient_content is None}")
    print(f"  NPC initiative suppressed during combat: {npc_initiative is None}")
    
    return combat_enhanced


async def test_event_summarization():
    """Test event summarization during gameplay"""
    print("\n=== Testing Event Summarization ===")
    
    # Create EventSummarizer
    summarizer = EventSummarizer()
    
    # Add significant events
    print("Adding significant game events for summarization...")
    
    events = [
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
            'event_type': 'DECISION_MADE',
            'context': {'priority_used': 'PLOT_PROGRESSION', 'outcome': 'confrontation with cultists'},
            'actor': 'player_123'
        }
    ]
    
    for event in events:
        summarizer.add_event_for_summarization(event)
        print(f"Added event: {event['event_type']}")
    
    # Force conditions for summarization
    summarizer.events_since_last_summary = [
        {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event['event_type'],
            'description': summarizer._create_event_description(event),
            'significance': summarizer._rate_event_significance(event)
        }
        for event in events
    ]
    
    # Create summary
    summary = await summarizer.create_summary("test_session")
    
    print(f"\nGenerated summary: {summary}")
    
    # Get story context for AI prompts
    story_context = summarizer.get_current_story_context()
    
    print("\nStory context for AI prompts:")
    print(f"  Summary: {story_context.get('story_summary', 'None')}")
    print(f"  Recent events: {len(story_context.get('recent_events', []))}")
    
    return story_context


async def test_idle_npc_behavior():
    """Test idle NPC behavior during gameplay lulls"""
    print("\n=== Testing Idle NPC Behavior ===")
    
    # Create IdleNPCManager
    npc_manager = IdleNPCManager()
    
    # Simulate idle period (5 minutes since last input)
    time_since_last_input = timedelta(minutes=5)
    
    # Check each NPC for initiative
    npcs_initiated = []
    
    print("Checking NPCs for potential dialogue initiation...")
    
    for npc_id in TEST_CONTEXT['present_npcs']:
        should_initiate, dialogue_theme = npc_manager.should_npc_initiate(
            npc_id, 
            TEST_CONTEXT,
            time_since_last_input
        )
        
        if should_initiate:
            npcs_initiated.append(npc_id)
            print(f"NPC {npc_id} initiated with theme: {dialogue_theme}")
            
            # Generate dialogue
            dialogue = await npc_manager.generate_npc_initiative(
                npc_id,
                dialogue_theme,
                TEST_CONTEXT
            )
            
            if dialogue:
                print(f"  {dialogue['npc_name']}: {dialogue['dialogue_text']}")
    
    print(f"\nTotal NPCs initiated: {len(npcs_initiated)}")
    
    # Get NPC initiative statistics
    stats = npc_manager.get_idle_npc_statistics()
    
    print("\nNPC Initiative Statistics:")
    print(f"  Session initiatives: {stats['session_initiative_count']}")
    print(f"  Unique NPCs initiated: {stats['unique_npcs_initiated']}")
    
    return npcs_initiated


async def main():
    """Run all tests"""
    print("=== Testing AI GM Pacing Integration with Domain & Combat Systems ===\n")
    
    await test_pacing_with_domain_integration()
    await test_pacing_with_combat_integration()
    await test_event_summarization()
    await test_idle_npc_behavior()
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(main())