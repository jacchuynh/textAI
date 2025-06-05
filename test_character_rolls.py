#!/usr/bin/env python3
"""
Test script for the enhanced Character.roll_check methods.

This script demonstrates the new roll_check_advanced and roll_check_hybrid methods.
"""

import sys
import os

# Add the backend src directory to Python path  
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

def test_character_rolls():
    """Test the character roll methods directly."""
    
    # Import here to avoid path issues
    from shared.models import Character, DomainType, Domain, Tag, TagCategory
    
    print("=== Enhanced Character Roll Check Test ===\n")
    
    # Create a test character
    character = Character(
        name="Test Hero",
        character_class="Warrior"
    )
    
    # Set up domains with different values
    character.domains[DomainType.BODY].value = 4
    character.domains[DomainType.AUTHORITY].value = 6
    character.domains[DomainType.SOCIAL].value = 2
    character.domains[DomainType.AWARENESS].value = 3
    character.domains[DomainType.MIND].value = 2
    character.domains[DomainType.CRAFT].value = 5
    character.domains[DomainType.SPIRIT].value = 3
    
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
        description="Ability to forge items",
        domains=[DomainType.CRAFT],
        rank=4
    )
    
    print("Character Setup:")
    print(f"  Body: {character.domains[DomainType.BODY].value}")
    print(f"  Authority: {character.domains[DomainType.AUTHORITY].value}")
    print(f"  Craft: {character.domains[DomainType.CRAFT].value}")
    print(f"  Tags: sword_fighting(3), intimidation(2), blacksmithing(4)\n")
    
    # Test 1: Basic roll check
    print("1. Basic Body Check (original method)")
    result = character.roll_check(DomainType.BODY, "sword_fighting", 12)
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Result: {result['total']} vs DC {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}\n")
    
    # Test 2: Advanced roll check
    print("2. Advanced Combat Roll (multiple domains)")
    action_data = {
        "label": "Tactical Strike",
        "tags": ["sword_fighting", "tactical"],
        "action_type": "attack"
    }
    
    result = character.roll_check_advanced(
        domain_type=DomainType.BODY,
        tag_name="sword_fighting", 
        difficulty=13,
        action_data=action_data,
        multiple_domains=[DomainType.AWARENESS]
    )
    
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Difficulty: {result['difficulty_breakdown']}")
    print(f"  Result: {result['total']} vs DC {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}")
    print(f"  Critical: {result['critical_success']}")
    print(f"  Domains used: {result['domains_used']}")
    print(f"  Tags used: {result['tags_used']}\n")
    
    # Test 3: Hybrid check - Authority vs weak target (should use threshold)
    print("3. Hybrid Check - Intimidation vs Weak Enemy (should use threshold)")
    weak_enemy = {"level": 1, "name": "Goblin"}
    action_data = {
        "label": "Intimidate",
        "tags": ["intimidation", "social"],
        "action_type": "social"
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.AUTHORITY,
        tag_name="intimidation",
        difficulty=10,
        action_data=action_data,
        target=weak_enemy
    )
    
    print(f"  Method: {result['method']} ({result['method_reason']})")
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Result: {result['total']} vs DC {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}\n")
    
    # Test 4: Hybrid check - Authority vs strong target (should use dice)
    print("4. Hybrid Check - Intimidation vs Strong Enemy (should use dice)")
    strong_enemy = {"level": 8, "name": "Dragon"}
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.AUTHORITY,
        tag_name="intimidation",
        difficulty=15,
        action_data=action_data,
        target=strong_enemy
    )
    
    print(f"  Method: {result['method']} ({result['method_reason']})")
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Result: {result['total']} vs DC {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}\n")
    
    # Test 5: Hybrid check - Crafting (should use threshold for routine)
    print("5. Hybrid Check - Routine Crafting (should use threshold)")
    craft_action = {
        "label": "Forge Sword",
        "tags": ["blacksmithing", "metalwork"],
        "action_type": "craft"
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.CRAFT,
        tag_name="blacksmithing",
        difficulty=12,
        action_data=craft_action
    )
    
    print(f"  Method: {result['method']} ({result['method_reason']})")
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Result: {result['total']} vs DC {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}\n")
    
    # Test 6: Hybrid check - Combat crafting (should use dice)
    print("6. Hybrid Check - Combat Crafting (should use dice)")
    combat_state = {"status": "active", "round": 3}
    combat_craft_action = {
        "label": "Emergency Repair",
        "tags": ["blacksmithing", "repair"],
        "action_type": "combat_craft"
    }
    
    result = character.roll_check_hybrid(
        domain_type=DomainType.CRAFT,
        tag_name="blacksmithing",
        difficulty=14,
        action_data=combat_craft_action,
        combat_state=combat_state
    )
    
    print(f"  Method: {result['method']} ({result['method_reason']})")
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Result: {result['total']} vs DC {result['difficulty']} = {'SUCCESS' if result['success'] else 'FAILURE'}\n")
    
    # Show domain growth
    print("=== Domain Growth Tracking ===")
    for domain_type, domain in character.domains.items():
        if domain.usage_count > 0:
            domain_name = domain_type.value if hasattr(domain_type, 'value') else str(domain_type)
            print(f"{domain_name}: used {domain.usage_count} times, current value {domain.value}")
    
    print("\n=== Tag XP Gains ===")
    for tag_name, tag in character.tags.items():
        if tag.xp > 0:
            print(f"{tag_name}: {tag.xp} XP (rank {tag.rank})")

if __name__ == "__main__":
    test_character_rolls()
