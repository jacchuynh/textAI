"""
Main entry point for the AI-RPG text parser demo.

This script demonstrates the text parser engine functionality,
including monster name resolution and disambiguation.
"""
from text_parser import parse_input, ParsedCommand, parser_engine # parser_engine for execute_command
from game_context import game_context # For direct context manipulation in demo

def display_command_info(parsed_command: ParsedCommand):
    """Helper to display parsed command details."""
    cmd_dict = parsed_command.to_command_dict()
    print("\n--- Parsed Command ---")
    print(f"Action: {cmd_dict['action']}")
    if parsed_command.direct_object_phrase:
        print(f"Direct Object Noun: '{parsed_command.direct_object_phrase.noun}' (Adjs: {parsed_command.direct_object_phrase.adjectives})")
        print(f"Direct Object ID: {parsed_command.direct_object_phrase.game_object_id}")
    
    if cmd_dict['preposition']:
        print(f"Preposition: {cmd_dict['preposition']}")
        if parsed_command.indirect_object_phrase:
            print(f"Indirect Object Noun: '{parsed_command.indirect_object_phrase.noun}' (Adjs: {parsed_command.indirect_object_phrase.adjectives})")
            print(f"Indirect Object ID: {parsed_command.indirect_object_phrase.game_object_id}")
            
    print(f"Pattern: {cmd_dict['pattern']}")
    print(f"Raw Input: '{cmd_dict['raw_input']}'")
    print("--- End Command ---")

def main_loop():
    """Run a demo of the text parser engine."""
    print("\nAI-RPG Text Parser Demo")
    print("=======================")
    print(f"Current Location: {game_context.get_current_location()}")
    print("Enter commands (or 'quit', 'look', 'inventory', 'debug context', 'start combat vine weasel', 'end combat'):")
    
    current_parsed_command: Optional[ParsedCommand] = None

    while True:
        if current_parsed_command and current_parsed_command.needs_disambiguation():
            prompt = "Which one do you mean? (enter number or 'cancel'): "
        else:
            prompt = f"[{game_context.get_current_location()}] > "
        
        user_input = input(prompt).strip()

        if user_input.lower() in ('quit', 'exit'):
            print("Exiting demo.")
            break

        # --- Demo-specific commands ---
        if user_input.lower() == "debug context":
            print("--- Game Context ---")
            print(game_context.get_context())
            print("Monsters in current location:")
            for m in game_context.get_monsters_at_location(game_context.get_current_location()):
                print(f"  - {m['name']} (ID: {m['id']}, Adjs: {m.get('adjectives', [])})")
            print("Objects in current location:")
            for o in game_context.get_objects_at_location(game_context.get_current_location()):
                print(f"  - {o['name']} (ID: {o['id']}, Adjs: {o.get('adjectives', [])})")
            print("Player Inventory:")
            for item in game_context.get_player_inventory(game_context.get_player_id()):
                 print(f"  - {item['name']} (ID: {item['id']})")
            print("--- End Context ---")
            continue
        
        if user_input.lower().startswith("start combat"):
            parts = user_input.split()
            if len(parts) > 2:
                monster_name_to_attack = " ".join(parts[2:])
                monsters_here = game_context.get_monsters_at_location(game_context.get_current_location())
                target_monster = next((m for m in monsters_here if m['name'].lower() == monster_name_to_attack.lower()), None)
                if target_monster:
                    game_context.start_combat([target_monster['id']])
                    print(f"Combat started with {target_monster['name']}!")
                else:
                    print(f"Cannot find '{monster_name_to_attack}' here to start combat.")
            else:
                print("Usage: start combat <monster name>")
            continue

        if user_input.lower() == "end combat":
            game_context.end_combat()
            print("Combat ended.")
            continue
        # --- End Demo-specific commands ---

        if current_parsed_command and current_parsed_command.needs_disambiguation():
            if user_input.lower() == 'cancel':
                print("Disambiguation cancelled.")
                current_parsed_command = None
                continue
            try:
                choice_idx = int(user_input) - 1
                if 0 <= choice_idx < len(current_parsed_command.disambiguation_candidates): # type: ignore
                    selected_candidate = current_parsed_command.disambiguation_candidates[choice_idx] # type: ignore
                    print(f"You chose: {selected_candidate['name']}")
                    # Update the command with the selected ID
                    if current_parsed_command.update_after_disambiguation(selected_candidate['id']):
                        print("Disambiguation resolved.")
                        # Now the command is ready for execution (or further processing if it was part of a multi-step parse)
                        # For this demo, we'll re-evaluate if it's fully parsed or needs more.
                        # If it was the only ambiguity, it should now be ready.
                        if not current_parsed_command.needs_disambiguation() and not current_parsed_command.has_error():
                             parser_engine.execute_command(current_parsed_command)
                             display_command_info(current_parsed_command)
                        else: # Still has error or needs more disambiguation (should not happen with current logic)
                             print(f"Error after disambiguation: {current_parsed_command.error_message}")
                    else:
                        print("Failed to update command after disambiguation.")
                    current_parsed_command = None # Reset for next input
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'cancel'.")
            continue # Go back to prompt for disambiguation or next command

        # Fresh parse
        current_parsed_command = parse_input(user_input)
        # parse_input internally uses parser_engine.parse(text, game_context.get_context())

        if current_parsed_command.has_error() and not current_parsed_command.needs_disambiguation():
            print(f"Error: {current_parsed_command.error_message}")
            current_parsed_command = None # Clear for next input
        elif current_parsed_command.needs_disambiguation():
            print(f"Error: {current_parsed_command.error_message}") # e.g., "Which X do you mean?"
            candidates = current_parsed_command.disambiguation_candidates
            if candidates:
                for i, candidate in enumerate(candidates):
                    desc = f"{i+1}. {candidate['name']}"
                    if candidate.get('adjectives'):
                        desc += f" ({', '.join(candidate['adjectives'])})"
                    if candidate.get('threat_tier'):
                        desc += f" [{candidate['threat_tier']}]"
                    if candidate.get('location'):
                        desc += f" (in {candidate['location']})"
                    print(desc)
            # The loop will now prompt for disambiguation choice
        else:
            # Command parsed successfully and no disambiguation needed
            # Execute command (publishes event)
            parser_engine.execute_command(current_parsed_command)
            display_command_info(current_parsed_command)
            current_parsed_command = None # Clear for next input

if __name__ == "__main__":
    # This ensures that the global instances in __init__.py are created first
    # before main_loop tries to use them.
    from text_parser import vocabulary_manager, object_resolver, parser_engine
    if vocabulary_manager and object_resolver and parser_engine: # Check they are not None
        main_loop()
    else:
        print("Error: Parser components not initialized correctly.")
