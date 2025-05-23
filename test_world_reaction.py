"""
World Reaction System Test Script

This script demonstrates the World Reaction components of the AI GM Brain system.
It shows how the system enhances narrative by incorporating reputation and
environmental reactions to player inputs.
"""

import sys
import time
import asyncio
from typing import Dict, Any

# Import core components
from backend.src.ai_gm.ai_gm_brain import get_ai_gm_brain, ProcessingMode
from backend.src.ai_gm.ai_gm_decision_logic import extend_ai_gm_brain_with_decision_logic
from backend.src.ai_gm.ai_gm_mechanical_integration import extend_ai_gm_brain_with_mechanical_integration
from backend.src.ai_gm.ai_gm_response_generator import extend_ai_gm_brain_with_response_generator
from backend.src.ai_gm.ai_gm_delivery_system import extend_ai_gm_brain_with_output_delivery, DeliveryChannel, ResponsePriority
from backend.src.ai_gm.world_reaction.world_reaction_integration import extend_ai_gm_brain_with_world_reaction
from backend.src.ai_gm.world_reaction.reputation_manager import ActionSignificance


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")


def setup_test_brain():
    """Set up a test brain with all components."""
    # Create AI GM Brain
    brain = get_ai_gm_brain("test_game", "test_player")
    
    # Extend with components in order
    extend_ai_gm_brain_with_decision_logic(brain)
    extend_ai_gm_brain_with_mechanical_integration(brain)
    extend_ai_gm_brain_with_response_generator(brain)
    extend_ai_gm_brain_with_output_delivery(brain)
    extend_ai_gm_brain_with_world_reaction(brain)
    
    print("AI GM Brain configured with world reaction capabilities!")
    
    return brain


def setup_test_world(brain):
    """Set up a test world with initial reputation and world state."""
    
    # Create a simple world state
    brain.enhanced_context_manager.update_world_state({
        'political_stability': 'unrest',
        'economic_status': 'recession',
        'region': 'town_of_crossroads',
        'time_of_day': 'evening'
    })
    
    # Record some significant player actions
    brain.record_significant_action(
        "Rescued the mayor's daughter from bandits", 
        ActionSignificance.MAJOR,
        "forest_road",
        affected_entities=["mayor", "town_guard"],
        reputation_changes={"mayor": 10, "town_guard": 5, "global": 3}
    )
    
    brain.record_significant_action(
        "Haggled aggressively with local merchant", 
        ActionSignificance.MINOR,
        "market_square",
        affected_entities=["merchants_guild"],
        reputation_changes={"merchants_guild": -3}
    )
    
    brain.record_significant_action(
        "Defended tavern from drunk mercenaries", 
        ActionSignificance.MODERATE,
        "tavern",
        affected_entities=["innkeeper", "tavern_patrons"],
        reputation_changes={"innkeeper": 7, "global": 2}
    )
    
    print("Test world set up with initial reputation and actions.")


async def test_direct_world_reaction(brain):
    """Test direct world reaction assessment."""
    print_separator()
    print("=== Testing Direct World Reaction Assessment ===")
    
    # Prepare a test event and context
    event = {'event_type': 'PLAYER_INPUT', 'input': 'Hello innkeeper, how are you doing today?'}
    context = brain.enhanced_context_manager.prepare_event_context(
        event, brain.player_id, "tavern"
    )
    
    # Set a specific target entity
    target_entity = "npc_innkeeper"
    
    print("\nAssessing reaction to: 'Hello innkeeper, how are you doing today?'")
    print(f"Target entity: {target_entity}")
    print(f"Location: tavern")
    
    # Assess world reaction
    reaction = await brain.assess_world_reaction(
        "Hello innkeeper, how are you doing today?",
        context,
        target_entity
    )
    
    if reaction['success']:
        print("\nReaction Assessment Result:")
        print(f"Perception: {reaction['reaction_data']['perception_summary']}")
        print(f"Response: {reaction['reaction_data']['suggested_reactive_dialogue_or_narration']}")
        
        if reaction['reaction_data']['subtle_attitude_shift_description']:
            print(f"Subtle shift: {reaction['reaction_data']['subtle_attitude_shift_description']}")
    else:
        print(f"\nReaction assessment failed: {reaction.get('error', 'Unknown error')}")
    
    return reaction


async def test_enhanced_input_processing(brain):
    """Test enhanced input processing with world reaction."""
    print_separator()
    print("=== Testing Enhanced Input Processing with World Reaction ===")
    
    # Test different player inputs in a conversation with the innkeeper
    test_inputs = [
        "Good evening, innkeeper. I'd like a room for the night.",
        "Can you tell me about the recent troubles in town?",
        "Have there been any strange travelers passing through lately?",
        "The mayor speaks highly of you. I helped his daughter recently.",
        "The merchant prices in town are highway robbery!"
    ]
    
    for input_text in test_inputs:
        print_separator()
        print(f"Player input: '{input_text}'")
        
        # Process the input with world reaction integration
        result = brain.process_player_input(input_text)
        
        # The output is shown by the delivery system, so no need to print here
        
        # Show whether world reaction was applied
        if result.get('metadata', {}).get('processing', {}).get('world_reaction_applied'):
            print("\nWorld reaction was incorporated into the response.")
            
            # Show world reaction metadata
            world_reaction = result.get('metadata', {}).get('world_reaction', {})
            print(f"Target perception: {world_reaction.get('perception_summary')}")
            
            if world_reaction.get('attitude_shift'):
                print(f"Attitude shift: {world_reaction.get('attitude_shift')}")
        else:
            print("\nBasic response without world reaction was used.")
        
        # Add a small delay between inputs
        await asyncio.sleep(1)
    
    return result


def simulate_adventure_sequence(brain):
    """Simulate a more complex adventure sequence with reputation changes."""
    print_separator()
    print("=== Simulating Adventure Sequence with Reputation Changes ===")
    
    print("\nDay 1: You arrive in the town of Crossroads...")
    
    # Record new significant actions as the adventure progresses
    print("\nYou help the blacksmith with a difficult forge job...")
    brain.record_significant_action(
        "Assisted the blacksmith with a difficult masterwork sword", 
        ActionSignificance.MODERATE,
        "blacksmith_forge",
        affected_entities=["blacksmith", "craftsmen_guild"],
        reputation_changes={"blacksmith": 5, "craftsmen_guild": 3}
    )
    
    print("\nYou investigate rumors of bandits in the hills...")
    brain.record_significant_action(
        "Discovered bandit camp location and reported to town guard", 
        ActionSignificance.MODERATE,
        "eastern_hills",
        affected_entities=["town_guard", "mayor"],
        reputation_changes={"town_guard": 4, "mayor": 2}
    )
    
    print("\nYou confront the bandit leader...")
    brain.record_significant_action(
        "Defeated bandit leader in single combat and recovered stolen goods", 
        ActionSignificance.MAJOR,
        "bandit_hideout",
        affected_entities=["merchants_guild", "town_guard", "mayor"],
        reputation_changes={"merchants_guild": 7, "town_guard": 6, "mayor": 8, "global": 5}
    )
    
    # Show the player's reputation after these actions
    event = {'event_type': 'STATUS_CHECK'}
    context = brain.enhanced_context_manager.prepare_event_context(
        event, brain.player_id, "town_square"
    )
    
    reputation_context = context.get('player_reputation_summary', 'No reputation data')
    recent_actions = context.get('recent_significant_actions', [])
    
    print("\nYour current reputation in town:")
    print(reputation_context)
    
    print("\nYour recent significant actions:")
    for action in recent_actions:
        print(f"- {action}")


async def run_tests():
    """Run all the world reaction tests."""
    try:
        # Setup test brain with all components
        brain = setup_test_brain()
        
        # Setup test world
        setup_test_world(brain)
        
        # Test direct world reaction assessment
        await test_direct_world_reaction(brain)
        
        # Test enhanced input processing
        await test_enhanced_input_processing(brain)
        
        # Simulate adventure sequence
        simulate_adventure_sequence(brain)
        
        print_separator()
        print("All world reaction tests completed!")
        
    except Exception as e:
        print(f"Error during tests: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to run the tests."""
    print_separator()
    print("World Reaction System Test")
    print_separator()
    
    # Run the async tests
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()