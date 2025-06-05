# AI GM Integration with LLM Support

This package provides a comprehensive integration for the AI Game Master (GM) Brain system with full LLM support via OpenRouter. The integration is designed to serve as a logic layer between player input and LLM responses, managing game context and providing appropriate responses.

## Overview

The AI GM Brain is designed to be an intelligent game master for text-based games, providing:

1. Context-aware responses to player actions
2. Persistent game state management
3. LLM-powered natural language responses
4. Extensible architecture for game mechanics

This integration focuses exclusively on the full-featured unified implementation with LLM support, without fallbacks to minimal implementations.

## Requirements

- Python 3.7+
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
- Required Python packages:
  - aiohttp
  - asyncio

## Quick Start

1. **Set up your OpenRouter API key:**

```bash
python setup_ai_gm_llm.py --setup
```

2. **Validate the integration:**

```bash
python setup_ai_gm_llm.py --validate
```

3. **Try the example application:**

```bash
python example_ai_gm_integration.py
```

## Key Components

- **ai_gm_unified_integration_full.py**: Main integration with LLM support
- **setup_ai_gm_llm.py**: Utility for setting up and validating LLM integration
- **example_ai_gm_integration.py**: Example application demonstrating usage

## How It Works

The AI GM integration with LLM support processes player input through several steps:

1. **Input Processing**: Player input is received and preprocessed
2. **Context Analysis**: The current game context is analyzed
3. **LLM Integration**: The input and context are sent to the LLM via OpenRouter
4. **Response Generation**: The LLM generates a response based on the input and context
5. **Post-processing**: The response is post-processed for delivery to the player

## Integration API

### Creating an AI GM instance

```python
from ai_gm_unified_integration_full import create_ai_gm

# Create an AI GM instance
ai_gm = create_ai_gm(
    game_id="my_game_123",
    player_id="player1",
    initial_context={
        "player_name": "Hero",
        "location_name": "Forest",
        "location_description": "A dense forest with towering trees."
    }
)
```

### Processing player input

```python
# Synchronous processing
response = ai_gm.process_player_input("look around")
print(response["response_text"])

# Asynchronous processing (recommended for LLM integration)
async def process_async():
    response = await ai_gm.process_player_input_async("look around")
    print(response["response_text"])
```

### Managing game context

```python
# Update game context
ai_gm.update_context({
    "weather": "Rainy",
    "time_of_day": "Night",
    "active_npcs": [
        {"name": "Merchant", "description": "A traveling merchant selling goods"}
    ]
})

# Get current context
context = ai_gm.get_context()
```

### Getting system status

```python
status = ai_gm.get_system_status()
print(f"LLM Support: {status.get('llm_support')}")
print(f"OpenRouter API Key: {status.get('openrouter_api_key')}")
```

## LLM Integration Details

The LLM integration is handled by the `LLMInteractionManager` class, which:

1. Manages API calls to OpenRouter
2. Constructs prompts based on game context
3. Handles different response types (narrative, dialogue, combat)
4. Provides error handling and fallbacks
5. Tracks token usage and costs

You can access the LLM manager directly for advanced usage:

```python
llm_manager = ai_gm.get_llm_manager()
```

## Context Structure for LLM Prompts

For optimal LLM responses, include these fields in your context:

```python
context = {
    "player_name": "Hero",              # Character name
    "location_name": "Ancient Forest",   # Current location name
    "location_description": "A dense forest with towering trees...", # Description
    "recent_events": [                   # Recent events (for context)
        "You found an old key",
        "You heard strange noises"
    ],
    "active_npcs": [                     # NPCs in the current location
        {"name": "Guard", "description": "A stern-looking guard watching the gate"}
    ],
    "character_info": {                  # Character stats/abilities
        "domains": {
            "Combat": 3,
            "Magic": 4
        }
    }
}
```

## Example Application

The `example_ai_gm_integration.py` script demonstrates a simple text-based game using the AI GM with LLM integration. It shows:

1. How to initialize the AI GM
2. How to process player commands
3. How to update game state
4. How to implement a game loop

## Troubleshooting

If you encounter issues:

1. **Check the OpenRouter API key**: Ensure it's correctly set
   ```bash
   python setup_ai_gm_llm.py --validate
   ```

2. **Test LLM responses**: Test if LLM responses are working
   ```bash
   python setup_ai_gm_llm.py --test
   ```

3. **Check logs**: Look at the log file (ai_gm_integration.log) for more detailed error information

4. **Verify imports**: Ensure all required modules are in the correct locations

## Advanced Configuration

For advanced users, the LLM integration supports:

- Different model tiers (fast/standard/premium)
- Custom prompt templates
- Response type selection (narrative/dialogue/combat)
- Token usage tracking

## License

This project is proprietary and confidential. Unauthorized copying, transfer, or reproduction is strictly prohibited.

## Credits

- OpenRouter for LLM API access
- TextRealmsAI development team 