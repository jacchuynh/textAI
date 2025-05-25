"""
End-to-End Scenario Runner

This script demonstrates a complete gameplay flow through multiple systems,
showing how player actions propagate through the entire game engine.
"""

import sys
import json
from pathlib import Path

# Add the project root to the Python path to allow importing our modules
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Import the end-to-end scenario module
from backend.src.end_to_end_scenarios import EndToEndScenarioRunner

def main():
    """Run an end-to-end gameplay scenario."""
    print("\n===== Starting End-to-End Gameplay Scenario =====\n")
    
    # Create a scenario runner with debug mode enabled
    scenario_runner = EndToEndScenarioRunner(debug=True)
    
    # Run the end-to-end scenario
    results = scenario_runner.run_end_to_end_scenario()
    
    # Save the logs to a file for analysis
    log_path = Path(project_root) / "scenario_logs.json"
    with open(log_path, 'w') as f:
        json.dump({
            "action_log": results["action_log"],
            "system_log": results["system_log"]
        }, f, indent=2)
    
    print(f"\nScenario logs saved to {log_path}")
    print("\n===== End-to-End Gameplay Scenario Complete =====\n")
    
    # Print a summary of what happened
    player_state = results["final_player_state"]
    print("Player Final State Summary:")
    print(f"  Name: {player_state['name']}")
    print(f"  Level: {player_state['level']}")
    print(f"  Health: {player_state['health']['current']}/{player_state['health']['max']}")
    print(f"  Gold: {player_state['gold']}")
    print(f"  Location: {player_state['location']['area']} in {player_state['location']['region']}")
    print(f"  Inventory Items: {len(player_state['inventory']['items'])}")
    print(f"  Materials: {len(player_state['inventory']['materials'])}")
    print(f"  Completed Quests: {len(player_state['quests']['completed'])}")
    
    # Print magic stats if available
    if "magic" in player_state:
        magic_id = player_state["magic"]["profile_id"]
        magic_user = scenario_runner.magic_system.magic_users.get(magic_id)
        if magic_user:
            print("\nMagic Profile:")
            print(f"  Mana: {magic_user.mana_current}/{magic_user.mana_max}")
            print(f"  Known Spells: {len(magic_user.known_spells)}")
            primary_domains = [d.name for d in magic_user.primary_domains]
            print(f"  Primary Domains: {', '.join(primary_domains)}")

if __name__ == "__main__":
    main()