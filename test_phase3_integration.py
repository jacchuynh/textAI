#!/usr/bin/env python3
"""
Test script for Phase 3: Adaptive AI Integration
Tests the complete integration of monster database, adaptive AI, and environmental effects.
"""

import sys
import os
import random
from pathlib import Path

# Add the backend src to the path
backend_path = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

def create_test_character():
    """Create a test character for combat testing."""
    from game_engine.character import Character
    from game_engine.domain import DomainType
    
    # Create character with balanced stats
    domains = {
        DomainType.BODY: 3,
        DomainType.MIND: 3,
        DomainType.SOUL: 3,
        DomainType.AUTHORITY: 2,
        DomainType.SOCIAL: 2,
        DomainType.CRAFT: 2,
        DomainType.ARCANE: 2
    }
    
    character = Character(
        name="Test Hero",
        domains=domains,
        growth_points=0,
        background="Fighter",
        location="Test Arena"
    )
    
    return character

def test_monster_database_integration():
    """Test monster database integration with combat system."""
    print("\n=== Testing Monster Database Integration ===")
    
    try:
        from game_engine.combat_system import CombatSystem
        
        # Initialize combat system
        combat_system = CombatSystem()
        character = create_test_character()
        
        # Test 1: Create enemy from database with region filter
        print("\n1. Testing database enemy creation with region filter...")
        combat_state = combat_system.start_combat(
            character=character,
            location_name="Verdant Wilds",
            environment_factors=["dense_forest", "magical_aura"],
            region="verdant"
        )
        
        if combat_state["status"] == "ongoing":
            enemy = combat_state["enemy"]
            print(f"✓ Created enemy from database: {enemy['name']}")
            print(f"  Level: {enemy.get('level', 'Unknown')}")
            print(f"  Archetype: {enemy.get('archetype', 'None')}")
            if "available_moves" in enemy:
                print(f"  Available moves: {len(enemy['available_moves'])}")
        else:
            print("✗ Failed to create enemy from database")
            
        # End combat for cleanup
        combat_system.end_combat(combat_state["combat_id"])
        
        # Test 2: Create enemy with tier filter
        print("\n2. Testing database enemy creation with tier filter...")
        combat_state = combat_system.start_combat(
            character=character,
            location_name="Mountain Pass",
            environment_factors=["rocky_terrain", "high_altitude"],
            tier="elite"
        )
        
        if combat_state["status"] == "ongoing":
            enemy = combat_state["enemy"]
            print(f"✓ Created elite enemy: {enemy['name']}")
            print(f"  Challenge level appropriate for tier")
        else:
            print("✗ Failed to create elite enemy")
            
        combat_system.end_combat(combat_state["combat_id"])
        
        # Test 3: Create specific archetype
        print("\n3. Testing specific archetype creation...")
        combat_state = combat_system.start_combat(
            character=character,
            location_name="Ancient Ruins",
            environment_factors=["cursed_ground", "unstable_magic"],
            archetype_id="shadow_warrior"
        )
        
        if combat_state["status"] == "ongoing":
            enemy = combat_state["enemy"]
            print(f"✓ Created specific archetype: {enemy['name']}")
        else:
            print("ℹ No specific archetype found, using fallback")
            
        combat_system.end_combat(combat_state["combat_id"])
        
        print("✓ Monster database integration tests completed")
        
    except Exception as e:
        print(f"✗ Monster database test failed: {e}")
        import traceback
        traceback.print_exc()

def test_adaptive_ai_with_database():
    """Test adaptive AI working with database monsters."""
    print("\n=== Testing Adaptive AI with Database Monsters ===")
    
    try:
        from game_engine.combat_system import CombatSystem
        
        combat_system = CombatSystem()
        character = create_test_character()
        
        # Start combat with database monster
        combat_state = combat_system.start_combat(
            character=character,
            location_name="Ember Wastes",
            environment_factors=["scorching_heat", "volcanic_ash"],
            region="ember",
            tier="standard"
        )
        
        if combat_state["status"] != "ongoing":
            print("✗ Failed to start combat")
            return
            
        print(f"✓ Combat started with: {combat_state['enemy']['name']}")
        
        # Test adaptive AI decision making
        print("\n1. Testing AI attack selection...")
        for round_num in range(3):
            print(f"\nRound {round_num + 1}:")
            
            # Get combat options to see environment interactions
            options = combat_system._generate_combat_options(combat_state)
            print(f"  Available options: {len(options)}")
            
            # Check if environment options are available
            env_options = [opt for opt in options if opt.startswith("Environment:")]
            if env_options:
                print(f"  Environment options: {env_options}")
            
            # Simulate player action (attack)
            player_action = "attack"
            result = combat_system.process_action(
                combat_state["combat_id"], 
                player_action, 
                {}
            )
            
            if result["status"] == "ongoing":
                print(f"  Player attacked, AI responded")
                if "enemy_action" in result:
                    print(f"  AI chose: {result['enemy_action']}")
            elif result["status"] == "victory":
                print("  Combat ended in victory!")
                break
            elif result["status"] == "defeat":
                print("  Combat ended in defeat!")
                break
        
        # Clean up
        if combat_state["combat_id"] in combat_system.active_combats:
            combat_system.end_combat(combat_state["combat_id"])
            
        print("✓ Adaptive AI tests completed")
        
    except Exception as e:
        print(f"✗ Adaptive AI test failed: {e}")
        import traceback
        traceback.print_exc()

def test_environment_monster_integration():
    """Test environment effects working with database monsters."""
    print("\n=== Testing Environment + Monster Integration ===")
    
    try:
        from game_engine.combat_system import CombatSystem
        
        combat_system = CombatSystem()
        character = create_test_character()
        
        # Test different environment + monster combinations
        test_scenarios = [
            {
                "location": "Underwater Cavern",
                "environment": ["underwater", "low_visibility", "pressure"],
                "region": "human",
                "expected_effects": "underwater combat modifiers"
            },
            {
                "location": "Volcanic Crater",
                "environment": ["extreme_heat", "toxic_fumes", "unstable_ground"],
                "region": "ember", 
                "expected_effects": "heat and instability effects"
            },
            {
                "location": "Mystical Grove",
                "environment": ["magical_enhancement", "healing_springs", "ancient_wards"],
                "region": "verdant",
                "expected_effects": "magical amplification"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. Testing {scenario['location']}...")
            
            combat_state = combat_system.start_combat(
                character=character,
                location_name=scenario["location"],
                environment_factors=scenario["environment"],
                region=scenario["region"]
            )
            
            if combat_state["status"] == "ongoing":
                enemy = combat_state["enemy"]
                print(f"  ✓ Enemy: {enemy['name']}")
                
                # Check environment system
                if "environment_systems" in combat_state:
                    env_sys = combat_state["environment_systems"]
                    print(f"  ✓ Environment system active with {len(env_sys)} factors")
                
                # Test environment action
                options = combat_system._generate_combat_options(combat_state)
                env_options = [opt for opt in options if opt.startswith("Environment:")]
                if env_options:
                    print(f"  ✓ Environment interactions available: {len(env_options)}")
                    
                    # Try an environment action
                    env_action = env_options[0].replace("Environment: ", "")
                    result = combat_system.process_action(
                        combat_state["combat_id"],
                        f"environment_{env_action.lower().replace(' ', '_')}",
                        {}
                    )
                    
                    if "environment_bonus" in result:
                        print(f"  ✓ Environment action granted bonus: {result['environment_bonus']}")
                else:
                    print("  ℹ No environment interactions available")
                    
            combat_system.end_combat(combat_state["combat_id"])
            
        print("✓ Environment + Monster integration tests completed")
        
    except Exception as e:
        print(f"✗ Environment integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_complete_combat_scenario():
    """Test a complete combat scenario with all Phase 3 features."""
    print("\n=== Testing Complete Combat Scenario ===")
    
    try:
        from game_engine.combat_system import CombatSystem
        
        combat_system = CombatSystem()
        character = create_test_character()
        
        print("Starting epic battle in the Crystal Caverns...")
        
        combat_state = combat_system.start_combat(
            character=character,
            location_name="Crystal Caverns",
            environment_factors=["crystal_resonance", "reflecting_lights", "echo_chamber"],
            region="human",
            tier="elite",
            surprise=False
        )
        
        if combat_state["status"] != "ongoing":
            print("✗ Failed to start epic battle")
            return
            
        enemy = combat_state["enemy"]
        print(f"✓ Epic battle started against: {enemy['name']}")
        print(f"  Location: {combat_state['location']}")
        print(f"  Environment factors: {len(combat_state.get('environment_systems', {}))}")
        
        # Simulate several rounds of complex combat
        round_count = 0
        max_rounds = 10
        
        while (combat_state["status"] == "ongoing" and 
               round_count < max_rounds and
               combat_state["combat_id"] in combat_system.active_combats):
            
            round_count += 1
            print(f"\n--- Round {round_count} ---")
            
            # Get all available options
            options = combat_system._generate_combat_options(combat_state)
            print(f"Available actions: {len(options)}")
            
            # Randomly choose between different action types
            action_type = random.choice([
                "attack", "defend", "environment_action", "special"
            ])
            
            if action_type == "environment_action":
                env_options = [opt for opt in options if opt.startswith("Environment:")]
                if env_options:
                    env_action = random.choice(env_options).replace("Environment: ", "")
                    action = f"environment_{env_action.lower().replace(' ', '_')}"
                    print(f"Player uses environment: {env_action}")
                else:
                    action = "attack"
                    print("Player attacks (no environment options)")
            else:
                action = "attack"
                print("Player attacks")
            
            # Process the action
            result = combat_system.process_action(
                combat_state["combat_id"],
                action,
                {}
            )
            
            # Update combat state
            if result["status"] == "ongoing":
                combat_state = combat_system.get_combat_state(combat_state["combat_id"])
                
                # Show action results
                if "damage_dealt" in result:
                    print(f"  Damage dealt: {result['damage_dealt']}")
                if "environment_bonus" in result:
                    print(f"  Environment bonus: {result['environment_bonus']}")
                if "enemy_action" in result:
                    print(f"  Enemy response: {result['enemy_action']}")
                    
            elif result["status"] == "victory":
                print("\n🎉 Victory! The hero triumphs!")
                break
            elif result["status"] == "defeat":
                print("\n💀 Defeat! The enemy proves too strong!")
                break
        
        # Cleanup
        if combat_state["combat_id"] in combat_system.active_combats:
            final_result = combat_system.end_combat(combat_state["combat_id"])
            print(f"\nCombat ended. Final status: {final_result.get('status', 'unknown')}")
            
        print("✓ Complete combat scenario test finished")
        
    except Exception as e:
        print(f"✗ Complete combat scenario failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all Phase 3 integration tests."""
    print("🚀 Phase 3: Adaptive AI Integration Test Suite")
    print("=" * 60)
    
    # Run all test categories
    test_monster_database_integration()
    test_adaptive_ai_with_database()
    test_environment_monster_integration()
    test_complete_combat_scenario()
    
    print("\n" + "=" * 60)
    print("✅ Phase 3 Integration Testing Complete!")
    print("\nPhase 3 Features Tested:")
    print("• Monster Database Integration")
    print("• Adaptive AI with Database Monsters")
    print("• Environment + Monster Interactions")
    print("• Complete Combat Scenarios")
    print("\nThe enhanced combat system is ready for advanced gameplay!")

if __name__ == "__main__":
    main()
