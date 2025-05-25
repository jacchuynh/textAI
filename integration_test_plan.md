# Magic Realms Integration Test Plan

## Overview

This integration test plan focuses on testing the interactions between different components of the Magic Realms backend system. The goal is to ensure that all components work together seamlessly, with a particular emphasis on the magic system's integration with other game subsystems.

## Key Integration Points

1. **Magic System & World Generation**
   - Leyline generation and placement
   - Magic profile assignment to locations
   - Magical material distribution
   - Magical POI generation

2. **Magic System & Combat**
   - Spell casting in combat
   - Environmental effects on magic
   - Monster magical abilities
   - Magic resource management during combat

3. **Magic System & Crafting**
   - Enchanting items
   - Brewing potions
   - Magical material gathering and usage
   - Recipe requirements and domain interactions

4. **Magic System & AI Game Master**
   - Dynamic adjustment of magical encounters
   - Story generation involving magical elements
   - NPC responses to player magic usage
   - Magical event generation

5. **Magic System & Player Progression**
   - Mana heart development
   - Spell learning and advancement
   - Domain-magic synergy
   - Magical specialization paths

## Integration Test Structure

### 1. Directory Structure

Create a new directory structure for integration tests:

```
backend/
├── tests/
│   ├── unit/
│   │   └── ... (existing unit tests)
│   └── integration/
│       ├── __init__.py
│       ├── conftest.py  (shared fixtures)
│       ├── test_magic_world_integration.py
│       ├── test_magic_combat_integration.py
│       ├── test_magic_crafting_integration.py
│       ├── test_magic_ai_gm_integration.py
│       ├── test_magic_player_progression.py
│       ├── test_end_to_end_scenarios.py
│       └── test_full_system_integration.py
```

### 2. Test Case Development

Each integration test module should:
- Import necessary components
- Set up test fixtures (shared in conftest.py where appropriate)
- Define test cases with clear descriptions
- Include validation of expected outcomes

### 3. Mocking Strategy

- Use fixtures to create standardized test environments
- Mock external services (e.g., AI APIs) for predictable responses
- Create deterministic random number generation for reproducible tests
- Use transaction rollbacks for database tests to maintain isolation

## Detailed Test Scenarios

### Magic System & World Generation Integration

#### Test Case: Leyline Generation and Influence

**Components Involved:**
- MagicWorldIntegration
- World class
- Location class
- LeylineManager

**Prerequisites:**
- World object with multiple locations of different biomes

**Steps:**
1. Create a test world with diverse biomes
2. Apply magic world integration to enhance the world
3. Verify leylines are generated between locations
4. Check that magical hotspots are created at key intersections
5. Validate that location magic profiles are properly assigned
6. Ensure magical POIs are generated in appropriate locations

**Expected Outcomes:**
- Leyline network should connect a subset of locations
- Hotspots should have higher magical energy levels
- Location magic profiles should reflect the biome and leyline strength
- Magical POIs should be distributed based on magic profile

#### Test Case: Magical Material Distribution

**Components Involved:**
- MagicalMaterialWorldIntegration
- World class
- Location class

**Prerequisites:**
- World object enhanced with magic profiles

**Steps:**
1. Apply magical material integration to the world
2. Check distribution of materials across different biomes
3. Verify that high-magic areas have rarer materials
4. Validate that material types match biome affinities

**Expected Outcomes:**
- Materials should be placed in appropriate biomes
- Higher magic areas should have more and rarer materials
- Material distribution should follow expected patterns based on leyline strength

### Magic System & Combat Integration

#### Test Case: Spell Casting in Combat

**Components Involved:**
- MagicalCombatManager
- Combatant class
- MagicSystem
- CombatSystem

**Prerequisites:**
- Character with mana heart and known spells
- Monster opponent
- Combat environment with defined magic properties

**Steps:**
1. Initialize combat with character and monster
2. Get available combat spells for character
3. Cast a spell at the monster
4. Check spell effects on monster
5. Verify resource consumption (mana, ley energy)
6. Test environmental influences on spell potency

**Expected Outcomes:**
- Spell casting should affect monster state appropriately
- Resources should be consumed according to spell requirements
- Environment should modify spell effects as expected
- Combat narration should describe the magical effects

#### Test Case: Monster Magic Integration

**Components Involved:**
- MonsterMagicIntegration
- Combatant class
- MagicSystem

**Prerequisites:**
- Basic monster template

**Steps:**
1. Enhance monster with magical abilities
2. Verify monster has appropriate magic profile
3. Check monster's magical combat moves
4. Test monster's spell casting in combat
5. Verify monster reacts to player's magic appropriately

**Expected Outcomes:**
- Monster should gain magical abilities based on its type
- Monster should have domain-appropriate spells
- Monster should be able to use magical attacks in combat
- Monster's magic profile should be consistent with its nature

### Magic System & Crafting Integration

#### Test Case: Enchanting Items

**Components Involved:**
- MagicalCraftingService
- MagicSystem
- Character with crafting domains

**Prerequisites:**
- Character with sufficient crafting and magic domains
- Available magical materials
- Enchanting recipes

**Steps:**
1. List available enchanting recipes
2. Check character's ability to perform enchantments
3. Attempt to enchant an item with available materials
4. Verify the item receives the expected enchantment
5. Test using the enchanted item in various contexts

**Expected Outcomes:**
- Enchantment should succeed if requirements are met
- Materials should be consumed
- Item should gain magical properties
- Enchanted item should function correctly in relevant contexts

#### Test Case: Brewing Magical Potions

**Components Involved:**
- MagicalCraftingService
- MagicSystem
- Character with alchemy domains

**Prerequisites:**
- Character with sufficient alchemy domains
- Available potion ingredients
- Potion recipes

**Steps:**
1. List available potion recipes
2. Check character's ability to brew potions
3. Attempt to brew a potion with available ingredients
4. Verify the potion has the expected properties
5. Test using the potion in various contexts

**Expected Outcomes:**
- Potion brewing should succeed if requirements are met
- Ingredients should be consumed
- Potion should have the expected magical effects
- Potion should function correctly when used

### Magic System & AI Game Master Integration

#### Test Case: Dynamic Magical Encounter Generation

**Components Involved:**
- AI_GM
- MagicSystem
- Combat system
- World state

**Prerequisites:**
- Game world with magic profiles
- Player character with magic abilities
- AI_GM instance

**Steps:**
1. Initialize AI_GM with world state
2. Request a magical encounter generation
3. Verify the encounter includes appropriate magical elements
4. Check that monster selection considers player's magical abilities
5. Validate that environmental magic affects the encounter

**Expected Outcomes:**
- Encounter should include monsters with appropriate magical abilities
- Environment should include magical elements based on location
- Challenge level should be appropriate for player's magical development
- Encounter narration should include magical elements

#### Test Case: Magical Event Response

**Components Involved:**
- AI_GM
- MagicSystem
- EventSystem
- NPC system

**Prerequisites:**
- Game world with NPCs
- Player character with magic abilities
- AI_GM instance

**Steps:**
1. Simulate player casting a powerful spell
2. Pass this event to the AI_GM
3. Check AI_GM's response to the magical action
4. Verify NPC reactions are appropriate
5. Validate that world state changes reflect the magical event

**Expected Outcomes:**
- AI_GM should acknowledge the magical event
- NPCs should react based on their attitudes toward magic
- World state might change (e.g., leyline disturbance)
- Follow-up events might be generated

### End-to-End Scenario Tests

#### Test Case: Complete Quest with Magic Integration

**Components Involved:**
- Multiple systems: Magic, Combat, Crafting, NPC, Quest, AI_GM

**Prerequisites:**
- Complete game world setup
- Player character with magical abilities
- Quest that involves magical elements

**Steps:**
1. Initialize quest involving magical elements
2. Navigate through quest steps using magic
3. Craft magical items required for the quest
4. Engage in magical combat as part of the quest
5. Complete the quest and receive magical rewards

**Expected Outcomes:**
- All systems should interact coherently
- Magic should be properly integrated in all quest aspects
- Quest progress should correctly track magical achievements
- Magical rewards should be properly added to player inventory
- World state should update appropriately

## Test Implementation Priorities

1. **First Priority: Core Magic System Integration**
   - Magic System & World Generation
   - Magic System & Combat

2. **Second Priority: Supportive System Integration**
   - Magic System & Crafting
   - Magic System & Player Progression

3. **Third Priority: AI Integration and Complex Scenarios**
   - Magic System & AI Game Master
   - End-to-End Scenarios

4. **Fourth Priority: Performance and Stress Testing**
   - Multi-component load testing
   - Extended gameplay simulation

## Testing Tools and Frameworks

1. **pytest** - Primary testing framework
   - Use fixtures for setup/teardown
   - Use parametrization for testing multiple scenarios
   - Use marks to categorize tests

2. **unittest.mock** - For mocking dependencies
   - Mock external services and APIs
   - Create controlled test environments

3. **pytest-benchmark** - For performance testing
   - Measure performance of key integration points
   - Ensure integrations don't create bottlenecks

4. **Coverage.py** - To measure test coverage
   - Focus on integration paths
   - Identify untested interaction paths

## Integration Test Best Practices

1. **Test Real Integrations**
   - Minimize mocks for actual integration points
   - Use mocks only for external services or randomness

2. **Focus on Boundaries**
   - Test data passing between components
   - Verify state changes across system boundaries

3. **End-to-End Validation**
   - Include some full-flow tests
   - Verify complete user stories

4. **Performance Awareness**
   - Monitor performance implications of integrations
   - Watch for unexpected data growth or memory usage

5. **Error Propagation**
   - Test how errors in one component affect others
   - Ensure proper error handling across boundaries

## Execution Strategy

1. Run integration tests after unit tests in the CI pipeline
2. Tag slower integration tests to run less frequently
3. Use randomized initial states but with fixed seeds for reproducibility
4. Implement a comprehensive logging system for debugging failed tests