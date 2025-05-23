"""
Text parser package for AI-driven RPG.

This package provides text parsing capabilities for processing player input.
"""
from .vocabulary import VocabularyManager
from .monster_loader import load_all_monsters, enrich_monster_data
from .object_resolver import ObjectResolver
from .parser_engine import ParserEngine, ParsedCommand

# --- Initialization Sequence ---

# 1. Initialize Vocabulary Manager
vocabulary_manager = VocabularyManager() # Loads default vocabs

# 2. Load Monster Data from YAMLs
#    Update these paths to where your YAML files are located relative to your project root
#    or pass an absolute path.
monster_yaml_files = [
    "crimson_accord_monsters_Version3.yaml",
    "crimson_accord_monsters_part2_Version3.yaml",
    "crimson_accord_monsters_part3_Version3.yaml",
    "crimson_accord_monsters_crossregion_Version3.yaml",
    "crimson_accord_monsters_human_crossregion_Version3.yaml"
]
raw_monster_list = load_all_monsters(monster_yaml_files)
enriched_monsters = enrich_monster_data(raw_monster_list) # Add adjectives, etc.

# 3. Load monster vocabulary into the VocabularyManager
vocabulary_manager.load_monster_vocab(enriched_monsters)
vocabulary_manager.save_vocabulary() # Optional: Save updated vocab files if you want to persist dynamic additions

# 4. Initialize Object Resolver (depends on VocabularyManager)
object_resolver = ObjectResolver(vocabulary_manager)

# 5. Initialize Parser Engine (depends on VocabularyManager and ObjectResolver)
parser_engine = ParserEngine(vocabulary_manager, object_resolver)

# --- Convenience function ---
def parse_input(text: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
    """
    Parse player input text.
    
    Args:
        text: The player's input string.
        context: Optional game context dictionary. If None, uses global game_context.
    
    Returns:
        A ParsedCommand object.
    """
    return parser_engine.parse(text, context_override=context)

# --- Populate GameContext with some monsters for testing ---
# This is for demo purposes. In a real game, monsters would be loaded dynamically
# based on player location, events, etc.
from game_context import game_context

# Clear any existing test monsters
game_context._monsters = {} # type: ignore

monster_id_counter = 1
for monster_data in enriched_monsters:
    # Create a unique ID for each monster instance if not present
    if 'id' not in monster_data:
        monster_data['id'] = f"monster_instance_{monster_id_counter}"
        monster_id_counter += 1
    
    # Assign a default location for testing if not specified
    if 'location' not in monster_data:
        # Distribute some monsters to town_square for easier testing
        if "vine weasel" in monster_data['name'].lower() or "highway bandit" in monster_data['name'].lower():
            monster_data['location'] = "town_square"
        else:
            monster_data['location'] = "unknown_region" # Default for others
            
    game_context.add_monster(monster_data.copy()) # Add a copy to avoid modifying the template

# Example: Start a combat for testing attack "it" or implicit attack
# game_context.start_combat(["monster_instance_1"]) # Assuming monster_instance_1 is a Vine Weasel

print(f"Loaded {len(enriched_monsters)} monster archetypes into vocabulary.")
print(f"Populated game_context with {len(game_context._monsters)} monster instances for testing.")
if "monster_instance_1" in game_context._monsters:
    print(f"Test monster 'monster_instance_1': {game_context._monsters['monster_instance_1']['name']} in {game_context._monsters['monster_instance_1']['location']}")
if any(m['location'] == 'town_square' for m in game_context._monsters.values()):
    print("Some monsters placed in 'town_square' for testing.")
