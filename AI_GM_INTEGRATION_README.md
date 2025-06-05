# AI GM Integration System

## Overview

The AI GM Integration System provides a unified interface for integrating the AI Game Master brain into your TextRealms application. This system automatically handles the complexity of choosing the best available implementation and provides a simple, consistent API for interacting with the AI GM.

## Key Features

- **Unified API**: A single, consistent API regardless of the underlying implementation
- **Automatic Fallback**: Uses the best available implementation with automatic fallback capability
- **Robust Error Handling**: Gracefully handles errors and provides meaningful fallbacks
- **Simple Integration**: Easy to integrate into any application with minimal dependencies

## Quick Start

```python
from ai_gm_integration import create_game_master, process_command

# Create an AI Game Master instance
gm = create_game_master(
    game_id="my_game_session",
    player_id="player123",
    initial_context={
        "player": {
            "name": "Hero",
            "health": 100,
            "inventory": ["Sword", "Shield", "Potion"]
        },
        "location": "Forest",
        "time_of_day": "Day"
    }
)

# Process player commands
response = process_command(gm, "look around")
print(response["response_text"])

# Update game context
from ai_gm_integration import update_game_context
update_game_context(gm, {"weather": "Rainy", "time_of_day": "Night"})
```

## Implementation Options

The system supports two main implementation approaches:

1. **Unified Implementation** (default): A comprehensive implementation that includes all AI GM components and advanced features
2. **Minimal Implementation**: A lightweight implementation that provides core functionality without complex dependencies

By default, the system attempts to use the Unified Implementation and automatically falls back to the Minimal Implementation if necessary.

To explicitly choose an implementation:

```python
# Use AUTO mode (tries unified first, falls back to minimal)
gm = create_game_master(game_id="game1", player_id="player1", use_unified=True)

# Force minimal implementation
gm = create_game_master(game_id="game2", player_id="player2", use_unified=False)
```

## API Reference

### Core Functions

#### `create_game_master(game_id, player_id, initial_context=None, use_unified=True)`

Creates a new AI GM instance.

- **game_id**: Unique identifier for the game session
- **player_id**: Identifier for the player
- **initial_context**: Optional dictionary containing initial game context
- **use_unified**: Whether to use the unified implementation (if False, uses minimal)

#### `process_command(gm_instance, player_input)`

Processes a player command and returns the AI GM's response.

- **gm_instance**: The AI GM instance
- **player_input**: The player's input text

#### `update_game_context(gm_instance, context_update)`

Updates the game context.

- **gm_instance**: The AI GM instance
- **context_update**: Dictionary of context values to update

#### `get_game_context(gm_instance)`

Gets the current game context.

- **gm_instance**: The AI GM instance

#### `get_implementation_info(gm_instance)`

Gets information about the implementation being used.

- **gm_instance**: The AI GM instance

## Demos and Testing

Run the integration demo to see the system in action:

```bash
python ai_gm_integration.py --demo
```

To test the minimal implementation specifically:

```bash
python ai_gm_integration_minimal_test.py
```

## Advanced Configuration

For more advanced configuration, you can access the underlying implementation:

```python
# Get the implementation mode
mode = gm.get_implementation_mode()

# Get detailed system status
status = gm.get_system_status()
```

## Troubleshooting

If you encounter integration issues:

1. Check that all required files are in the correct locations
2. Verify that any dependencies are installed
3. Try the minimal implementation as a fallback
4. Check the logs for specific error messages

## Files

- `ai_gm_integration.py` - Main entry point for the integration system
- `ai_gm_combined_stable.py` - Stable implementation with fallback capabilities
- `ai_gm_minimal_wrapper.py` - Minimal implementation wrapper
- `ai_gm_direct_test.py` - Unified implementation test harness

## Contributing

To contribute to the AI GM Integration System:

1. Ensure all changes maintain backward compatibility
2. Add appropriate error handling for robustness
3. Test both implementation paths (unified and minimal)
4. Update documentation to reflect changes 