#!/usr/bin/env python3
"""
Debug script to isolate the environment action processing error.
"""

import sys
sys.path.append('.')

from backend.src.game_engine.combat_system import CombatSystem
from backend.src.shared.models import Character, DomainType, Domain, Tag

def debug_environment_action():
    """Debug the environment action processing."""
    
    # Create test character
    character = Character(
        name="Test Hero",
        domains={
            DomainType.BODY: Domain(type=DomainType.BODY, value=3),
            DomainType.AWARENESS: Domain(type=DomainType.AWARENESS, value=4),
            DomainType.SPIRIT: Domain(type=DomainType.SPIRIT, value=2)
        }
    )
    
    # Create combat system
    combat_system = CombatSystem()
    
    print("=== Environment Action Debug ===")
    
    # Start combat
    combat_result = combat_system.start_combat(
        character=character,
        enemy_template_id=1,
        environment_factors=["Forest", "High Ground"],
        location_name="Test Forest"
    )
    
    combat_id = combat_result["id"]
    
    # Get combat options
    options = combat_system._generate_combat_options(
        combat_state=combat_result,
        character=character
    )
    
    # Find environment actions
    env_actions = [opt for opt in options if opt.get("label", "").startswith("Environment:")]
    
    if env_actions:
        env_action = env_actions[0]
        print(f"Environment action found: {env_action['label']}")
        print(f"Action data: {env_action}")
        
        # Test the roll check directly
        print("\n=== Testing Roll Check ===")
        try:
            # Use the combat system's domain mapping
            mapped_domain = combat_system._determine_action_domain(env_action)
            print(f"Mapped domain: {mapped_domain}")
            
            roll_result = character.roll_check_hybrid(
                domain_type=mapped_domain,
                tag_name=None,
                difficulty=10,
                action_data=env_action,
                target=None,
                combat_state=combat_result
            )
            print(f"Roll result: {roll_result}")
        except Exception as e:
            print(f"Roll check error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test action processing
        print("\n=== Testing Action Processing ===")
        try:
            updated_state = combat_system.process_combat_action(
                combat_id=combat_id,
                action_data=env_action,
                character=character
            )
            print("Action processed successfully!")
        except Exception as e:
            print(f"Action processing error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No environment actions found")

if __name__ == "__main__":
    debug_environment_action()
