#!/usr/bin/env python3
"""
Test script for the enhanced combat system with monster generation.
This script demonstrates how monsters are created from YAML templates and
how the combat system resolves encounters between them.
"""
import sys
import random
from typing import List, Dict, Any

# Add the backend directory to the path so we can import modules
sys.path.append("backend/src")

# Import the required modules
from game_engine.enhanced_combat.monster_database import load_monster_database, get_random_monster
from game_engine.enhanced_combat.monster_archetypes import ThreatTier, ThreatCategory
from game_engine.enhanced_combat.combat_controller import CombatController
from game_engine.enhanced_combat.combat_system_core import CombatMove, Combatant, MoveType, Domain


def print_monster_stats(monster: Combatant, moves: List[CombatMove]) -> None:
    """Print the stats and moves of a monster"""
    print(f"\n{'=' * 50}")
    print(f"MONSTER: {monster.name}")
    print(f"{'=' * 50}")
    print(f"  Health: {monster.current_health}/{monster.max_health}")
    print(f"  Stamina: {monster.current_stamina}/{monster.max_stamina}")
    print(f"  Focus: {monster.current_focus}/{monster.max_focus}")
    print(f"  Spirit: {monster.current_spirit}/{monster.max_spirit}")
    
    print("\nDOMAIN VALUES:")
    for domain, value in monster.domains.items():
        print(f"  {domain.name}: {value}")
    
    print("\nAVAILABLE MOVES:")
    for i, move in enumerate(moves, 1):
        domains_str = ", ".join([d.name for d in move.domains])
        print(f"  {i}. {move.name} ({move.move_type.name}) - Domains: {domains_str}")
        print(f"     Damage: {move.base_damage} | Costs: {move.stamina_cost} stamina, {move.focus_cost} focus, {move.spirit_cost} spirit")
        if move.effects:
            print(f"     Effects: {', '.join(move.effects)}")
        print()


def simulate_combat_round(controller: CombatController, 
                          monster1: Combatant, monster1_moves: List[CombatMove],
                          monster2: Combatant, monster2_moves: List[CombatMove]) -> Dict[str, Any]:
    """Simulate a round of combat between two monsters"""
    
    # Randomly select moves for each monster
    monster1_move = random.choice(monster1_moves)
    monster2_move = random.choice(monster2_moves)
    
    print(f"\n{'-' * 50}")
    print(f"COMBAT ROUND: {monster1.name} vs {monster2.name}")
    print(f"{'-' * 50}")
    print(f"{monster1.name} uses {monster1_move.name} ({monster1_move.move_type.name})")
    print(f"{monster2.name} uses {monster2_move.name} ({monster2_move.move_type.name})")
    
    # Resolve the combat exchange
    result = controller.resolve_combat_exchange(
        actor_name=monster1.name,
        actor_move=monster1_move,
        target_name=monster2.name,
        target_move=monster2_move
    )
    
    # Print the results
    print("\nRESULTS:")
    print(f"  {monster1.name}: {result['actor_outcome']}")
    print(f"    Health: {monster1.current_health}/{monster1.max_health}")
    print(f"  {monster2.name}: {result['target_outcome']}")
    print(f"    Health: {monster2.current_health}/{monster2.max_health}")
    
    print("\nNARRATIVE:")
    print(f"  {result['narrative']}")
    
    return result


def main():
    """Main function to test the combat system"""
    print("Loading monster database...")
    load_monster_database()
    
    # Create a combat controller with environment
    controller = CombatController(environment_name="Verdant Forest")
    
    # Generate a standard monster from the Verdant region
    print("\nGenerating a monster from the Verdant region...")
    verdant_monster, verdant_moves = get_random_monster(
        region="verdant",
        tier=ThreatTier.STANDARD,
        level=3
    )
    
    # Generate an elite monster from the Ember region
    print("\nGenerating a monster from the Ember region...")
    ember_monster, ember_moves = get_random_monster(
        region="ember",
        tier=ThreatTier.ELITE,
        level=5
    )
    
    # Print the monsters' stats
    print_monster_stats(verdant_monster, verdant_moves)
    print_monster_stats(ember_monster, ember_moves)
    
    # Simulate multiple rounds of combat
    for _ in range(3):
        result = simulate_combat_round(
            controller=controller,
            monster1=verdant_monster,
            monster1_moves=verdant_moves,
            monster2=ember_monster,
            monster2_moves=ember_moves
        )
        
        # Check if either monster is defeated
        if verdant_monster.current_health <= 0:
            print(f"\n{verdant_monster.name} has been defeated by {ember_monster.name}!")
            break
        elif ember_monster.current_health <= 0:
            print(f"\n{ember_monster.name} has been defeated by {verdant_monster.name}!")
            break
    
    print("\nCombat simulation completed.")


if __name__ == "__main__":
    main()