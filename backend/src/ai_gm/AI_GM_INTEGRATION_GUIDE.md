# AI GM Brain Integration Guide

This guide explains how to integrate the AI GM Brain system into your application. The AI GM Brain provides an intelligent game master system for text-based games.

## Overview

The AI GM Brain system consists of several components:

1. **Core Brain** - The central orchestration system
2. **World Reaction** - Handles how the world reacts to player actions
3. **Pacing** - Controls the pacing of the game
4. **Output Generation** - Generates output for the player
5. **OOC Handler** - Handles out-of-character commands
6. **LLM Manager** - Manages interactions with language models
7. **Combat Integration** - Handles combat mechanics

## Quick Start

The easiest way to integrate the AI GM Brain is to use the minimal wrapper, which provides a simplified interface that doesn't rely on complex imports.

```python
# Import the minimal wrapper
from backend.src.ai_gm.ai_gm_minimal_wrapper import create_unified_gm

# Create a GM instance
gm = create_unified_gm(
    game_id="your_game_id",
    player_id="player_id",
    initial_context={
        "player": {
            "name": "Player Name",
            "domains": {"Combat": 3, "Social": 2, "Knowledge": 4},
            "health": 100
        },
        "current_location": "Starting Location",
        "active_npcs": ["NPC Name"]
    }
)

# Process player input
response = gm.process_player_input("look around")
print(response["response_text"])

# Update context
gm.update_context({"weather": "Rainy", "time_of_day": "Night"})
```

## Integration Steps

If you want to use the full AI GM Brain system with all components, follow these steps:

1. Run the integration setup script:
   ```bash
   python -m backend.src.ai_gm.ai_gm_integration_setup
   ```

2. Fix any import issues in the unified integration file:
   ```bash
   python -m backend.src.ai_gm.ai_gm_unified_fix
   ```

3. Test the integration:
   ```bash
   python -m backend.src.ai_gm.ai_gm_simple_test
   ```

## Using the Full System

If the full system is available, you can use it with the same interface as the minimal wrapper:

```python
# Import the unified integration
from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm

# Create a GM instance
gm = create_unified_gm(
    game_id="your_game_id",
    player_id="player_id",
    initial_context={...}
)

# Process player input
response = gm.process_player_input("look around")
```

## Extending the System

To extend the AI GM Brain system, you can:

1. Implement your own versions of the component modules (world_reaction_integration.py, pacing_integration.py, etc.)
2. Add new components by registering them with the brain:
   ```python
   brain.register_extension("custom_component", YourCustomComponent(brain))
   ```

## Troubleshooting

If you encounter import issues:

1. Make sure all required directories exist:
   - ai_gm/
   - events/
   - memory/
   - text_parser/

2. Check that all component modules exist and have the correct class names

3. Run the fix_ai_gm_imports.py script to create any missing dependencies

4. If you continue to have issues, fall back to using the minimal wrapper

## API Reference

### AIGMBrainMinimal

The minimal implementation of the AI GM Brain.

#### Methods

- `process_player_input(input_text: str) -> Dict[str, Any]`: Process player input and return a response
- `update_context(context_update: Dict[str, Any]) -> Dict[str, Any]`: Update the game context
- `get_context() -> Dict[str, Any]`: Get the current game context
- `get_status() -> Dict[str, Any]`: Get the status of the AI GM Brain

### create_unified_gm

Factory function to create a GM instance.

#### Parameters

- `game_id: str`: The ID of the game session
- `player_id: str`: The ID of the player
- `initial_context: Optional[Dict[str, Any]]`: Optional initial context

#### Returns

An AI GM Brain instance that can process player input and manage game state. 