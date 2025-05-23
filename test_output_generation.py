"""
Output Generation & Delivery Test Script

This script demonstrates the Response Generation and Output Delivery
components of the AI GM Brain system.
"""

import sys
import time
from typing import Dict, Any, List

# Import core components
from backend.src.ai_gm.ai_gm_brain import get_ai_gm_brain, ProcessingMode
from backend.src.ai_gm.ai_gm_decision_logic import extend_ai_gm_brain_with_decision_logic
from backend.src.ai_gm.ai_gm_mechanical_integration import extend_ai_gm_brain_with_mechanical_integration
from backend.src.ai_gm.ai_gm_response_generator import extend_ai_gm_brain_with_response_generator
from backend.src.ai_gm.ai_gm_delivery_system import extend_ai_gm_brain_with_output_delivery, DeliveryChannel, ResponsePriority


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 60 + "\n")


def setup_test_brain():
    """Set up a test brain with all components."""
    # Create AI GM Brain
    brain = get_ai_gm_brain("test_game", "test_player")
    
    # Extend with each component
    extend_ai_gm_brain_with_decision_logic(brain)
    extend_ai_gm_brain_with_mechanical_integration(brain)
    extend_ai_gm_brain_with_response_generator(brain)
    extend_ai_gm_brain_with_output_delivery(brain)
    
    print("AI GM Brain configured with all components!")
    
    return brain


def test_direct_output_flow(brain):
    """Test the direct output generation and delivery flow."""
    print("\n=== Testing Direct Output Flow ===")
    
    # Create a mock decision result to pass to the response generator
    decision_result = {
        'action_taken': 'parsed_command_look',
        'response_basis': 'parsed_command',
        'mechanical_outcome': {
            'success': True,
            'command': 'look',
            'target': 'room',
            'details': 'The room is dimly lit with torches on the wall. A large wooden door stands on the far wall.'
        },
        'suggested_response': 'You observe your surroundings, noticing the dim torchlight.',
        'success': True
    }
    
    # Create a mock game context
    game_context = {
        'location': {
            'name': 'The Dungeon Entrance',
            'atmosphere': 'An eerie chill fills the air.',
            'features': ['flickering torches', 'wooden door', 'stone walls']
        },
        'player': {
            'name': 'Adventurer',
            'status': 'Healthy'
        },
        'npcs': []
    }
    
    # Create a mock interaction context
    interaction_context = {
        'player_input': 'look',
        'processing_time': 0.1,
        'player_id': 'test_player'
    }
    
    print("\nGenerating response...")
    response_data = brain.response_generator.generate_response(
        decision_result, game_context, interaction_context
    )
    
    print(f"Generated response: {response_data['response_text']}")
    print(f"Response source: {response_data['response_source']}")
    
    # Create metadata for delivery
    metadata = {
        'game_id': brain.game_id,
        'player_id': brain.player_id,
        'processing_time': 0.1,
        'decision_priority': decision_result['response_basis']
    }
    
    print("\nDelivering response...")
    delivery_result = brain.deliver_response(response_data, metadata)
    
    print(f"Delivery successful: {delivery_result['overall_success']}")
    print(f"Successful channels: {delivery_result['successful_channels']}")
    
    return response_data


def test_full_input_output_flow(brain):
    """Test the full player input to output flow."""
    print("\n=== Testing Full Input-Output Flow ===")
    
    # Test different player inputs
    test_inputs = [
        "look around",
        "go north",
        "take the sword",
        "attack the goblin",
        "who built this castle?"
    ]
    
    for input_text in test_inputs:
        print_separator()
        print(f"Player input: '{input_text}'")
        
        start_time = time.time()
        result = brain.process_player_input(input_text)
        elapsed = time.time() - start_time
        
        print(f"Total processing time: {elapsed:.3f}s")
        
        # The output is shown by the delivery system, so no need to print here
        
        # Show generation and delivery statistics
        if hasattr(brain, 'response_generator'):
            print("\nResponse Generation Stats:")
            for key, value in brain.response_generator.generation_stats.items():
                if key != 'mode_usage' and key != 'complexity_distribution':
                    print(f"- {key}: {value}")
        
        if hasattr(brain, 'output_delivery'):
            print("\nOutput Delivery Stats:")
            for key, value in brain.output_delivery.delivery_stats.items():
                if key != 'channel_usage':
                    print(f"- {key}: {value}")
        
        # Add a small delay between inputs
        time.sleep(1)
    
    return result


def test_scene_description(brain):
    """Test generating a scene description."""
    print("\n=== Testing Scene Description ===")
    
    # Create a mock decision result
    decision_result = {
        'action_taken': 'parsed_command_go',
        'response_basis': 'parsed_command',
        'mechanical_outcome': {
            'success': True,
            'command': 'go',
            'direction': 'north',
            'details': 'You enter a grand hall.'
        },
        'suggested_response': 'You move north into a new area.',
        'success': True
    }
    
    # Create a mock game context with rich location details
    game_context = {
        'location': {
            'name': 'The Grand Hall',
            'atmosphere': 'The high ceiling creates an imposing atmosphere.',
            'features': [
                'marble columns', 
                'a massive chandelier', 
                'intricate tapestries depicting ancient battles'
            ]
        },
        'time': {
            'period': 'evening',
            'changes': 'shadows grow longer as the last light fades'
        },
        'weather': {
            'description': 'Rain patters gently against the stained glass windows.'
        }
    }
    
    # Create a mock interaction context
    interaction_context = {
        'player_input': 'go north',
        'processing_time': 0.1,
        'player_id': 'test_player'
    }
    
    print("\nGenerating response...")
    response_data = brain.response_generator.generate_response(
        decision_result, game_context, interaction_context
    )
    
    print(f"Generated response: {response_data['response_text']}")
    print(f"Response source: {response_data['response_source']}")
    
    # Create metadata for delivery
    metadata = {
        'game_id': brain.game_id,
        'player_id': brain.player_id,
        'processing_time': 0.1,
        'decision_priority': 'HIGH'
    }
    
    print("\nDelivering response...")
    delivery_result = brain.deliver_response(response_data, metadata)
    
    return response_data


def test_branch_outcome(brain):
    """Test generating a narrative branch outcome."""
    print("\n=== Testing Narrative Branch Outcome ===")
    
    # Create a mock decision result
    decision_result = {
        'action_taken': 'branch_action_pick_lock',
        'response_basis': 'aligned_branch_action',
        'mechanical_outcome': {
            'success': True,
            'skill_type': 'lockpicking',
            'details': 'The ancient lock clicks open, revealing a secret chamber.',
            'message': 'You successfully pick the complex lock.',
            'skill_check': {
                'result': 'success',
                'roll': 18,
                'dc': 15,
                'skill': 'lockpicking'
            }
        },
        'suggested_response': 'With careful manipulation, you hear a satisfying click from the lock.',
        'success': True
    }
    
    # Create a mock game context
    game_context = {
        'location': {
            'name': 'Ancient Treasury',
            'atmosphere': 'The air is thick with dust and anticipation.',
            'features': ['locked chest', 'faded murals', 'stone pedestal']
        }
    }
    
    # Create a mock interaction context
    interaction_context = {
        'player_input': 'pick the lock on the chest',
        'processing_time': 0.2,
        'player_id': 'test_player'
    }
    
    print("\nGenerating response...")
    response_data = brain.response_generator.generate_response(
        decision_result, game_context, interaction_context
    )
    
    print(f"Generated response: {response_data['response_text']}")
    print(f"Response source: {response_data['response_source']}")
    
    # Create metadata for delivery
    metadata = {
        'game_id': brain.game_id,
        'player_id': brain.player_id,
        'processing_time': 0.2,
        'decision_priority': 'ALIGNED_BRANCH_ACTION'
    }
    
    print("\nDelivering response...")
    delivery_result = brain.deliver_response(response_data, metadata)
    
    return response_data


def main():
    """Main function to run the tests."""
    print_separator()
    print("Output Generation & Delivery Test")
    print_separator()
    
    # Set up the brain with all components
    brain = setup_test_brain()
    
    # Run the tests
    print_separator()
    test_direct_output_flow(brain)
    
    print_separator()
    test_scene_description(brain)
    
    print_separator()
    test_branch_outcome(brain)
    
    print_separator()
    test_full_input_output_flow(brain)
    
    print_separator()
    print("All tests completed!")


if __name__ == "__main__":
    main()