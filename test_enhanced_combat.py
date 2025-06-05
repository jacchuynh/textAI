#!/usr/bin/env python3
"""
Test script for the enhanced domain-integrated combat system.

This script demonstrates how the new roll_check methods work with
the combat system, showing both dice rolls and threshold checks.
"""

import sys
import os

# Add the backend src directory to Python path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

# Now we can import using absolute imports
from shared.models import Character, DomainType, Domain, Tag, TagCategory

# Add the specific module path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src', 'game_engine'))

# Import combat system components after adding path
import combat_system
CombatSystem = combat_system.CombatSystem
CombatActionType = combat_system.CombatActionType

def create_test_character():
    """Create a test character with varied domain/tag values."""
    character = Character(
        name="Test Warrior",
        character_class="Fighter"
    )
    
    # Set up domains with different values to test thresholds
    character.domains[DomainType.BODY].value = 4        # Good for combat
    character.domains[DomainType.AUTHORITY].value = 6   # High for intimidation
    character.domains[DomainType.SOCIAL].value = 2      # Low social skills
    character.domains[DomainType.AWARENESS].value = 3   # Moderate awareness
    character.domains[DomainType.MIND].value = 2        # Low intelligence
    character.domains[DomainType.CRAFT].value = 5       # High crafting
    character.domains[DomainType.SPIRIT].value = 3      # Moderate spirit
    
    # Add some tags
    character.tags["sword_fighting"] = Tag(
        name="Sword Fighting",
        category=TagCategory.COMBAT,
        description="Skill with swords",
        domains=[DomainType.BODY],
        rank=3
    )
    
    character.tags["intimidation"] = Tag(
        name="Intimidation",
        category=TagCategory.SOCIAL,
        description="Ability to frighten others",
        domains=[DomainType.AUTHORITY],
        rank=2
    )
    
    character.tags["blacksmithing"] = Tag(
        name="Blacksmithing",
        category=TagCategory.CRAFTING,
        description="Ability to forge metal items",
        domains=[DomainType.CRAFT],
        rank=4
    )
    
    return character

def test_combat_integration():
    """Test the combat system integration."""
    print("=== Enhanced Domain-Integrated Combat System Test ===\n")
    
    character = create_test_character()
    combat_system = CombatSystem()
    
    # Test 1: Basic attack (should use dice)
    print("1. Basic Attack (Body domain - should use dice)")
    action_data = {
        "label": "Sword Attack",
        "action_type": CombatActionType.ATTACK.value,
        "domains": [DomainType.BODY.value],
        "tags": ["sword_fighting", "physical"],
        "damage": 5
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.BODY,
        tag_name="sword_fighting",
        difficulty=12,
        action_data=action_data
    )
    
    print(f"Method: {result['method']} ({result['method_reason']})")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Result: {result['total']} vs {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"Domains used: {result['domains_used']}")
    print(f"Tags used: {result['tags_used']}\n")
    
    # Test 2: Intimidation against weak enemy (should use threshold)
    print("2. Intimidation vs Weak Enemy (Authority domain - should use threshold)")
    weak_enemy = {"level": 1, "name": "Goblin"}
    
    action_data = {
        "label": "Intimidate",
        "action_type": CombatActionType.SPECIAL.value,
        "domains": [DomainType.AUTHORITY.value],
        "tags": ["intimidation", "social"]
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.AUTHORITY,
        tag_name="intimidation",
        difficulty=10,
        action_data=action_data,
        target=weak_enemy
    )
    
    print(f"Method: {result['method']} ({result['method_reason']})")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Result: {result['total']} vs {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"Domains used: {result['domains_used']}")
    print(f"Tags used: {result['tags_used']}\n")
    
    # Test 3: Intimidation against strong enemy (should use dice)
    print("3. Intimidation vs Strong Enemy (Authority domain - should use dice)")
    strong_enemy = {"level": 8, "name": "Dragon", "domains": {DomainType.SOCIAL: 7}}
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.AUTHORITY,
        tag_name="intimidation",
        difficulty=15,
        action_data=action_data,
        target=strong_enemy
    )
    
    print(f"Method: {result['method']} ({result['method_reason']})")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Result: {result['total']} vs {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"Domains used: {result['domains_used']}")
    print(f"Tags used: {result['tags_used']}\n")
    
    # Test 4: Crafting (should use threshold for routine work)
    print("4. Routine Crafting (Craft domain - should use threshold)")
    action_data = {
        "label": "Forge Sword",
        "action_type": "craft",
        "domains": [DomainType.CRAFT.value],
        "tags": ["blacksmithing", "metalwork"]
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.CRAFT,
        tag_name="blacksmithing",
        difficulty=12,
        action_data=action_data
    )
    
    print(f"Method: {result['method']} ({result['method_reason']})")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Result: {result['total']} vs {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"Domains used: {result['domains_used']}")
    print(f"Tags used: {result['tags_used']}\n")
    
    # Test 5: Combat crafting (should use dice)
    print("5. Combat Crafting (Craft domain - should use dice)")
    combat_state = {"status": "active", "round": 3}
    action_data = {
        "label": "Quick Repair",
        "action_type": "combat_craft",
        "domains": [DomainType.CRAFT.value],
        "tags": ["blacksmithing", "repair"]
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.CRAFT,
        tag_name="blacksmithing",
        difficulty=14,
        action_data=action_data,
        combat_state=combat_state
    )
    
    print(f"Method: {result['method']} ({result['method_reason']})")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Result: {result['total']} vs {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"Domains used: {result['domains_used']}")
    print(f"Tags used: {result['tags_used']}\n")
    
    # Test 6: Advanced combat roll with multiple domains
    print("6. Advanced Combat Action (Multiple domains)")
    action_data = {
        "label": "Tactical Strike",
        "action_type": CombatActionType.ATTACK.value,
        "domains": [DomainType.BODY.value, DomainType.AWARENESS.value],
        "tags": ["sword_fighting", "tactical"],
        "damage": 6
    }
    
    result = character.roll_check_advanced(
        domain_type=DomainType.BODY,
        tag_name="sword_fighting",
        difficulty=13,
        action_data=action_data,
        multiple_domains=[DomainType.AWARENESS]
    )
    
    print(f"Breakdown: {result['breakdown']}")
    print(f"Difficulty: {result['difficulty_breakdown']}")
    print(f"Result: {result['total']} vs {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"Critical: {result['critical_success']}")
    print(f"Domains used: {result['domains_used']}")
    print(f"Tags used: {result['tags_used']}\n")
    
    print("=== Domain Growth Check ===")
    print("Body domain usage count:", character.domains[DomainType.BODY].usage_count)
    print("Authority domain usage count:", character.domains[DomainType.AUTHORITY].usage_count)
    print("Craft domain usage count:", character.domains[DomainType.CRAFT].usage_count)
    print("\nTag XP gains:")
    for tag_name, tag in character.tags.items():
        print(f"  {tag_name}: {tag.xp} XP (rank {tag.rank})")

if __name__ == "__main__":
    test_combat_integration()
