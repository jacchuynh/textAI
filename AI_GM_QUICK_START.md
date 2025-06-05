# AI GM Brain Integration Quick Start Guide

This guide provides step-by-step instructions for getting started with the AI GM Brain integration system for TextRealmsAI.

## Prerequisites

- Python 3.8+
- TextRealmsAI project downloaded

## Quick Setup

### 1. Run the Quick Fix Script

The quickest way to set up the AI GM Brain integration is to run the quick fix script:

```bash
python ai_gm_quick_fix.py
```

This script will:
- Fix import paths
- Create any missing directories and files
- Verify that imports work correctly
- Run a basic test of the integration

### 2. Choose Your Integration Approach

The AI GM Brain integration system offers two main approaches:

#### Option A: Unified Integration (Comprehensive)

This approach provides a full-featured integration with all components:

```python
from ai_gm_unified_demo import create_unified_gm

gm = create_unified_gm(
    game_id="my_game",
    player_id="player1",
    initial_context={
        "player": {
            "name": "Hero",
            "domains": {"Combat": 3, "Magic": 4, "Survival": 2},
            "health": 100
        },
        "current_location": "Forest Clearing"
    }
)

# Process player input
response = gm.process_player_input("look around")
print(response["response_text"])
```

#### Option B: Direct Implementation (Simplified)

This approach provides a simplified implementation with minimal dependencies:

```python
from ai_gm_direct_test import create_unified_gm

gm = create_unified_gm(
    game_id="my_game",
    player_id="player1"
)

# Process player input
response = gm.process_player_input("look around")
print(response["response_text"])
```

### 3. Run a Demo

To see the AI GM Brain in action, run one of the demo scripts:

```bash
# Run the simple demo
python ai_gm_simple_demo.py

# Or test both approaches
python test_ai_gm_approaches.py
```

## Common Commands

The AI GM Brain understands various commands:

### Basic Commands
- `look around` - Look at your surroundings
- `examine [object]` - Examine an object
- `go [direction]` - Move in a direction
- `take [item]` - Pick up an item

### OOC Commands
- `/help` - Display help information
- `/status` - Show your character status
- `/stats` - Show game statistics
- `/location` - Show information about your current location

## Context Management

You can update the game context at any time:

```python
# Update context
gm.update_context({
    "weather": "Rainy",
    "time_of_day": "Night",
    "active_npcs": ["Merchant", "Guard"]
})

# Get current context
context = gm.get_context()
```

## Troubleshooting

### Import Issues

If you experience import errors:

1. Run the quick fix script: `python ai_gm_quick_fix.py`
2. Verify that all required directories and files exist
3. Check that Python path includes the project directory

### Integration Issues

If the integration doesn't work as expected:

1. Try the direct implementation approach first (Option B)
2. Check the AI_GM_INTEGRATION_GUIDE.md for detailed information
3. Look at the test scripts for examples of correct usage

## Next Steps

- Review the comprehensive integration guide: `AI_GM_INTEGRATION_GUIDE.md`
- Explore the demo implementations for more advanced usage
- Check out the test scripts for examples of different integration patterns

## Server Implementation

To run the AI GM Brain as a server:

```bash
# Start the basic server
python ai_gm_server.py

# Or start the advanced server
python advanced_ai_gm_server.py

# Or use the integrated system startup script
./start_integrated_system.sh
```

## Additional Resources

- `AI_GM_BRAIN_INTEGRATION.md` - Technical integration details
- `integration_test_plan.md` - Testing approach and plan
- `ai_gm_direct_test.py` - Direct implementation example
- `ai_gm_unified_demo.py` - Unified implementation example 