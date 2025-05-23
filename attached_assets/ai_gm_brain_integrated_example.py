"""
Example usage of the integrated AI GM Brain with Text Parser Engine
"""

import logging
from ai_gm_brain_integrated import AIGMBrain
from text_parser import vocabulary_manager, parser_engine, game_context

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    """Demonstrate integrated AI GM Brain functionality."""
    
    # Initialize the integrated brain
    brain = AIGMBrain(
        game_id="integrated_demo_001",
        player_id="player_character_id"
    )
    
    print("AI GM Brain + Text Parser Integration Demo")
    print("=" * 50)
    print(f"Current Location: {game_context.get_current_location()}")
    print(f"Parser Statistics: {brain.get_parser_statistics()}")
    
    # Test various input types that showcase parser integration
    test_inputs = [
        # Simple parsed commands
        "look around",
        "inventory", 
        "examine sword",
        "take rusty sword",
        "go north",
        
        # Commands that might need disambiguation
        "attack weasel",  # If multiple weasels present
        "take sword",     # If multiple swords present
        
        # Conversational input (questions, complex requests)
        "What can you tell me about this sword?",
        "How do I get to the forest?",
        "Tell me about the monsters here",
        
        # Parser errors / unclear commands
        "flibbergibbet the whatsit",
        "I want to maybe possibly go somewhere",
        
        # Social interactions
        "talk to the elder",
        "greet the merchant"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{'='*20} Test {i} {'='*20}")
        print(f"Input: '{test_input}'")
        print("-" * 50)
        
        response = brain.process_player_input(test_input)
        
        print(f"Response: {response['response_text']}")
        print(f"Mode: {response['metadata']['processing_mode']}")
        print(f"Complexity: {response['metadata']['complexity']}")
        print(f"Parsed Successfully: {response['metadata']['parsed_successfully']}")
        print(f"Requires LLM: {response.get('requires_llm', False)}")
        print(f"Processing time: {response['metadata']['processing_time']:.3f}s")
        
        # Handle disambiguation if needed
        if response.get('processing_mode') == 'disambiguation':
            print("\n>>> Disambiguation needed - auto-selecting option 1 for demo")
            disambig_response = brain.process_player_input("1")
            print(f"Disambig Response: {disambig_response['response_text']}")
    
    # Demonstrate parser-specific features
    print(f"\n{'='*20} Parser Features {'='*20}")
    
    # Show vocabulary stats
    print(f"Vocabulary Statistics:")
    vocab_stats = brain.get_parser_statistics()['vocabulary_size']
    for category, count in vocab_stats.items():
        print(f"  - {category}: {count}")
    
    # Show game context
    print(f"\nGame Context:")
    print(f"  - Objects at location: {len(game_context.get_objects_at_location(game_context.get_current_location()))}")
    print(f"  - Monsters at location: {len(game_context.get_monsters_at_location(game_context.get_current_location()))}")
    print(f"  - In combat: {game_context.is_in_combat()}")
    
    # Show GM Brain statistics
    print(f"\nAI GM Brain Statistics:")
    stats = brain.get_processing_statistics()
    for key, value in stats.items():
        print(f"  - {key}: {value}")

def demo_combat_integration():
    """Demonstrate combat integration with parser and AI GM Brain."""
    print(f"\n{'='*20} Combat Demo {'='*20}")
    
    # Start combat with a monster
    monsters_here = game_context.get_monsters_at_location(game_context.get_current_location())
    if monsters_here:
        monster = monsters_here[0]
        game_context.start_combat([monster['id']])
        print(f"Combat started with {monster['name']}!")
        
        # Initialize brain
        brain = AIGMBrain(game_id="combat_demo", player_id="player_character_id")
        
        # Test combat commands
        combat_inputs = [
            "attack",           # Should target current enemy
            "attack it",        # Pronoun resolution
            "examine the enemy", # Look at current target
            "defend",           # Combat action
            "inventory"         # Check items during combat
        ]
        
        for combat_input in combat_inputs:
            print(f"\nCombat Input: '{combat_input}'")
            response = brain.process_player_input(combat_input)
            print(f"Response: {response['response_text']}")
        
        # End combat
        game_context.end_combat()
        print("Combat ended.")

if __name__ == "__main__":
    main()
    demo_combat_integration()