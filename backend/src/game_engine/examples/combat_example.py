"""
Example usage of the combat system.

This script demonstrates:
1. Starting a combat encounter
2. Processing player actions
3. Handling combat flow
4. Accessing combat history and growth logs
"""
import random
from typing import Dict, Any
import uuid

from ..combat_system import combat_system
from ...shared.models import Character, Domain, DomainType, Tag, TagCategory


def create_test_character() -> Character:
    """Create a test character for the example."""
    # Create character
    character = Character(
        id=str(uuid.uuid4()),
        name="Kaelin Stormrider",
        class_name="Spellblade",
        background="Former soldier turned arcane student",
        level=3,
        stats={
            "strength": 14,
            "dexterity": 12,
            "intelligence": 16,
            "charisma": 10
        },
        max_health=35,
        current_health=35,
        max_mana=25,
        current_mana=25
    )
    
    # Add domains
    character.domains = {
        DomainType.BODY: Domain(
            type=DomainType.BODY,
            value=2,
            growth_points=30,
            growth_required=100,
            usage_count=15,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.MIND: Domain(
            type=DomainType.MIND,
            value=3,
            growth_points=60,
            growth_required=100,
            usage_count=30,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.SPIRIT: Domain(
            type=DomainType.SPIRIT,
            value=2,
            growth_points=40,
            growth_required=100,
            usage_count=15,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.SOCIAL: Domain(
            type=DomainType.SOCIAL,
            value=1,
            growth_points=20,
            growth_required=100,
            usage_count=10,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.CRAFT: Domain(
            type=DomainType.CRAFT,
            value=1,
            growth_points=15,
            growth_required=100,
            usage_count=5,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.AUTHORITY: Domain(
            type=DomainType.AUTHORITY,
            value=0,
            growth_points=5,
            growth_required=100,
            usage_count=3,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.AWARENESS: Domain(
            type=DomainType.AWARENESS,
            value=2,
            growth_points=35,
            growth_required=100,
            usage_count=15,
            growth_log=[],
            level_ups_required=8
        )
    }
    
    # Add tags/skills
    character.tags = {
        "Longsword Proficiency": Tag(
            id="tag_longsword",
            name="Longsword Proficiency",
            category=TagCategory.COMBAT,
            description="Skilled in the use of longswords",
            domains=[DomainType.BODY],
            rank=2,
            xp=30,
            xp_required=200
        ),
        "Arcane Knowledge": Tag(
            id="tag_arcane",
            name="Arcane Knowledge",
            category=TagCategory.MAGIC,
            description="Knowledge of arcane theory and practice",
            domains=[DomainType.MIND, DomainType.SPIRIT],
            rank=3,
            xp=120,
            xp_required=400
        ),
        "Battlefield Tactics": Tag(
            id="tag_tactics",
            name="Battlefield Tactics",
            category=TagCategory.COMBAT,
            description="Understanding of military tactics and battlefield positioning",
            domains=[DomainType.MIND, DomainType.BODY],
            rank=2,
            xp=40,
            xp_required=200
        )
    }
    
    return character


def run_combat_simulation():
    """Run a combat simulation."""
    print("=== Combat System Example ===")
    
    # Create a test character
    character = create_test_character()
    print(f"Created character: {character.name}, Level {character.level} {character.class_name}")
    print(f"Health: {character.current_health}/{character.max_health}, Mana: {character.current_mana}/{character.max_mana}")
    print("Domains:", ", ".join([f"{domain.type.value}: {domain.value}" for domain in character.domains.values()]))
    print("Skills:", ", ".join([f"{name} (Rank {tag.rank})" for name, tag in character.tags.items()]))
    print()
    
    # Start a combat encounter
    game_id = "example_game_123"
    enemy_template_id = 2  # Bandit
    
    print(f"Starting combat against enemy template {enemy_template_id}...")
    combat_state = combat_system.start_combat(
        character=character,
        enemy_template_id=enemy_template_id,
        location_name="Forest Road",
        environment_factors=["Light Foliage", "Uneven Ground"],
        surprise=False,
        game_id=game_id
    )
    
    print(f"Combat started with ID: {combat_state['id']}")
    print(f"Location: {combat_state['location']}")
    print(f"Environment: {', '.join(combat_state['environment'])}")
    
    enemy = combat_state['enemies'][0]
    print(f"Enemy: {enemy['name']} (Level {enemy['level']}, HP: {enemy['current_health']}/{enemy['max_health']})")
    print()
    
    # Display available actions
    print("Available actions:")
    for i, action in enumerate(combat_state['available_actions']):
        print(f"{i+1}. {action['label']} ({action['action_type']})")
        print(f"   Domains: {', '.join(action['domains'])}")
        print(f"   Tags: {', '.join(action['tags'])}")
        if action.get('description'):
            print(f"   Description: {action['description']}")
        print()
    
    # Combat loop
    while combat_state['status'] == 'active':
        print(f"=== Round {combat_state['round']} ===")
        print(f"Player HP: {combat_state['player']['current_health']}/{combat_state['player']['max_health']}")
        
        for enemy in combat_state['enemies']:
            if enemy['current_health'] > 0:
                print(f"{enemy['name']} HP: {enemy['current_health']}/{enemy['max_health']}")
        
        # Choose a random action
        if combat_state['available_actions']:
            chosen_action = random.choice(combat_state['available_actions'])
            print(f"Choosing action: {chosen_action['label']}")
            
            # Prepare action data
            action_data = chosen_action.copy()
            if action_data.get('requires_target', True) and combat_state['enemies']:
                action_data['target'] = combat_state['enemies'][0]['id']
            
            # Process the action
            combat_state = combat_system.process_combat_action(
                combat_id=combat_state['id'],
                action_data=action_data,
                character=character
            )
            
            # Display combat log
            print("\nCombat Log:")
            for log_entry in combat_state['log'][-3:]:  # Show last 3 log entries
                print(f"- {log_entry}")
            print()
            
            # Check if combat has ended
            if combat_state['status'] != 'active':
                print(f"Combat ended with status: {combat_state['status']}")
                break
        else:
            print("No actions available!")
            break
    
    # Display final outcome
    print("\n=== Combat Summary ===")
    print(f"Combat lasted {combat_state['round']} rounds")
    print(f"Final status: {combat_state['status']}")
    print(f"Player final HP: {combat_state['player']['current_health']}/{combat_state['player']['max_health']}")
    
    # Display growth log
    print("\n=== Growth Log ===")
    for entry in combat_state['growth_log']:
        domain = entry.get('domain')
        success = entry.get('success', False)
        action = entry.get('action', 'Unknown')
        result = "Success" if success else "Failure"
        print(f"Domain: {domain}, Action: {action}, Result: {result}")
    
    # End combat
    combat_system.end_combat(combat_state['id'], game_id)
    print("\nCombat session ended and cleaned up.")


if __name__ == "__main__":
    run_combat_simulation()