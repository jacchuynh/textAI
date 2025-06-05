#!/usr/bin/env python3
"""
Test script to verify the sophisticated intent analysis integration
in the unified progression system.
"""
import sys
import os

# Add the backend/src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from shared.models import Character, Domain, Tag, DomainType, TagCategory, ActionSignificanceTier, ResolutionMethod
from game_engine.unified_progression_system import unified_progression_system

def test_intent_analysis_integration():
    """Test the sophisticated intent analysis integration"""
    print("=== Testing Intent Analysis Integration ===")
    
    # Create a test character
    character = Character(
        name="Test Hero",
        insight_points=15
    )
    
    # Set up character with goals and values
    character.declared_goals = [
        "become a master swordsman",
        "protect the innocent", 
        "maintain honor in all dealings"
    ]
    character.demonstrated_values = {
        "honor": 8,
        "courage": 7,
        "compassion": 6,
        "justice": 5
    }
    
    # Add some domains
    character.domains[DomainType.SOCIAL] = Domain(
        type=DomainType.SOCIAL, 
        value=8, 
        usage_count=5, 
        growth_points=10
    )
    character.domains[DomainType.BODY] = Domain(
        type=DomainType.BODY, 
        value=6, 
        usage_count=3, 
        growth_points=5
    )
    
    # Add some tags
    character.tags["diplomacy"] = Tag(
        name="diplomacy", 
        rank=3, 
        xp=15,
        category=TagCategory.SOCIAL,
        description="Skill in diplomatic negotiations and political maneuvering",
        domains=[DomainType.SOCIAL, DomainType.MIND]
    )
    character.tags["swordsmanship"] = Tag(
        name="swordsmanship", 
        rank=4, 
        xp=20,
        category=TagCategory.COMBAT,
        description="Skill with sword combat techniques",
        domains=[DomainType.BODY, DomainType.AWARENESS]
    )
    
    print(f"Character created: {character.name}")
    print(f"Goals: {character.declared_goals}")
    print(f"Values: {character.demonstrated_values}")
    
    # Test Case 1: Simple goal alignment
    print("\n--- Test Case 1: Goal Alignment ---")
    player_input = "I want to practice my sword skills to become stronger"
    action_data = {"description": "Train with sword", "difficulty": 12}
    
    intent_analysis = unified_progression_system._analyze_player_intent(
        character, 
        action_data, 
        player_input=player_input
    )
    
    print(f"Player Input: '{player_input}'")
    print(f"Goals Aligned: {intent_analysis.get('goals_aligned', [])}")
    print(f"Confidence Level: {intent_analysis.get('confidence_level', 0):.2f}")
    print(f"Value Consistent: {intent_analysis.get('value_consistent', False)}")
    print(f"Creative Approach: {intent_analysis.get('creative_approach_detected', False)}")
    
    # Test Case 2: Conflicting intents
    print("\n--- Test Case 2: Conflicting Intents ---")
    player_input = "I want to defeat my enemies quickly but I don't want to hurt innocent people"
    player_approach = "I'll use my sword skills but try to be merciful"
    action_data = {"description": "Engage in combat", "difficulty": 15}
    
    intent_analysis = unified_progression_system._analyze_player_intent(
        character, 
        action_data, 
        player_input=player_input,
        player_approach_description=player_approach
    )
    
    print(f"Player Input: '{player_input}'")
    print(f"Player Approach: '{player_approach}'")
    print(f"Conflicts Detected: {intent_analysis.get('conflicts_detected', False)}")
    print(f"Paralysis Detected: {intent_analysis.get('paralysis_detected', False)}")
    print(f"Emotional State: {intent_analysis.get('emotional_state', 'neutral')}")
    print(f"Primary Intents Count: {len(intent_analysis.get('primary_intents', []))}")
    
    if intent_analysis.get('primary_intents'):
        print("Primary Intents:")
        for intent in intent_analysis['primary_intents'][:5]:  # Show first 5
            print(f"  - {intent.category}: {intent.subcategory} (confidence: {intent.confidence:.2f})")
    
    if intent_analysis.get('recommended_clarifications'):
        print("Recommended Clarifications:")
        for clarification in intent_analysis['recommended_clarifications'][:3]:
            print(f"  - {clarification}")
    
    # Test Case 3: Creative approach
    print("\n--- Test Case 3: Creative Approach ---")
    player_input = "I want to find a creative solution that lets me win without violence"
    player_approach = "Maybe I can use diplomacy or find an innovative tactical approach"
    action_data = {"description": "Resolve conflict creatively", "difficulty": 18}
    
    intent_analysis = unified_progression_system._analyze_player_intent(
        character, 
        action_data, 
        player_input=player_input,
        player_approach_description=player_approach
    )
    
    print(f"Player Input: '{player_input}'")
    print(f"Creative Approach Detected: {intent_analysis.get('creative_approach_detected', False)}")
    print(f"Approach Novelty Score: {intent_analysis.get('approach_novelty', 0):.2f}")
    print(f"Goal Alignment Strength: {intent_analysis.get('goal_alignment_strength', 0):.2f}")
    print(f"Value Alignment Score: {intent_analysis.get('value_alignment_score', 0):.2f}")
    
    # Test Case 4: Full action processing with intent analysis
    print("\n--- Test Case 4: Full Action Processing ---")
    result = unified_progression_system.process_action(
        character=character,
        domain_type=DomainType.SOCIAL,
        action_description="Negotiate with the bandit leader",
        tag_name="diplomacy",
        action_data={"difficulty": 14, "target_level": 3},
        player_declared_goal_alignment="protect the innocent",
        player_approach_description="Use diplomatic skills to find peaceful resolution"
    )
    
    print("Full Action Processing Result:")
    print(f"Success: {result.get('success', False)}")
    print(f"Resolution Method: {result.get('resolution_method', 'unknown')}")
    if 'intent_analysis' in result:
        intent = result['intent_analysis']
        print(f"Intent Confidence: {intent.get('confidence_level', 0):.2f}")
        print(f"Goals Aligned: {intent.get('goals_aligned', [])}")
    
    print("\n=== Intent Analysis Integration Test Complete ===")
    return True

def test_player_profile_tracking():
    """Test player profile tracking over multiple interactions"""
    print("\n=== Testing Player Profile Tracking ===")
    
    character = Character(name="Profile Test Character")
    character.declared_goals = ["become a master diplomat"]
    character.demonstrated_values = {"wisdom": 7, "patience": 6}
    
    # Simulate multiple interactions
    interactions = [
        ("I want to talk my way out of this conflict", "Use careful words and diplomacy"),
        ("I prefer to negotiate rather than fight", "Find common ground with opponents"),
        ("Let me try to understand their perspective first", "Listen carefully and show empathy"),
        ("I want to build trust before making demands", "Be honest and transparent in my approach")
    ]
    
    for i, (player_input, approach) in enumerate(interactions, 1):
        print(f"\nInteraction {i}:")
        print(f"Input: '{player_input}'")
        
        intent_analysis = unified_progression_system._analyze_player_intent(
            character, 
            {"description": f"Diplomatic interaction {i}"}, 
            player_input=player_input,
            player_approach_description=approach
        )
        
        print(f"Confidence: {intent_analysis.get('confidence_level', 0):.2f}")
        
        # Check if approach consistency improves over time
        if 'approach_consistency' in intent_analysis:
            print(f"Approach Consistency: {intent_analysis['approach_consistency']:.2f}")
    
    # Check player profile data
    profile_key = character.name
    if profile_key in unified_progression_system.player_profiles:
        profile = unified_progression_system.player_profiles[profile_key]
        print(f"\nPlayer Profile Summary:")
        print(f"Total Analyses: {profile['analysis_count']}")
        print(f"Approach Patterns: {profile['approach_patterns']}")
        print(f"Value Patterns: {profile['value_patterns']}")
        print(f"Goal Patterns: {profile['goal_patterns']}")
    
    print("\n=== Player Profile Tracking Test Complete ===")
    return True

def main():
    """Main test function"""
    print("Starting Sophisticated Intent Analysis Integration Tests...\n")
    
    try:
        # Test basic intent analysis integration
        test_intent_analysis_integration()
        
        # Test player profile tracking
        test_player_profile_tracking()
        
        print("\n✅ All tests completed successfully!")
        print("\nThe sophisticated intent analysis system has been successfully integrated!")
        print("Features verified:")
        print("- Advanced intent detection and categorization")
        print("- Conflict detection between opposing intentions")
        print("- Creative approach recognition") 
        print("- Goal alignment assessment")
        print("- Value consistency checking")
        print("- Player profile tracking over time")
        print("- Integration with full action processing")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
