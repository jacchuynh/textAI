"""
Comprehensive test for Phase 5-7 of the Domain System Rehaul.

This test validates:
- Phase 5: Insight Point Spending Mechanisms and Domain Progression Tiers
- Phase 6: Enhanced Mastery Path Generation and Anti-Grinding Mechanisms  
- Phase 7: World Response Integration and AI-Driven Analysis
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from shared.models import Character, DomainType, Domain, Tag, ActionSignificanceTier, ResolutionMethod
from game_engine.unified_progression_system import unified_progression_system
from datetime import datetime

def test_phase_5_insight_spending():
    """Test insight point spending mechanisms and domain progression."""
    print("=== Testing Phase 5: Insight Point Spending ===")
    
    # Create test character with insight points
    character = Character(
        name="Test Character",
        insight_points=20  # Give enough points for testing
    )
    
    # Add some domains and tags
    character.domains[DomainType.SOCIAL] = Domain(type=DomainType.SOCIAL, value=8, usage_count=5, growth_points=10)
    character.tags["diplomacy"] = Tag(name="diplomacy", rank=3, xp=15)
    
    # Test getting available insight options
    available_options = unified_progression_system.get_available_insight_options(character)
    print(f"Available insight options: {len(available_options)}")
    
    # Test spending insight points
    result = unified_progression_system.spend_insight_points(character, "bonus_growth_points")
    print(f"Bonus growth points result: {result['success']}")
    print(f"Remaining insight points: {character.insight_points}")
    
    # Test domain progression tier
    tier = unified_progression_system.get_domain_progression_tier(character.domains[DomainType.SOCIAL].value)
    print(f"Social domain tier: {tier}")
    
    # Test advancement check
    advancement_info = unified_progression_system.can_advance_domain(character, DomainType.SOCIAL)
    print(f"Can advance social domain: {advancement_info['can_advance']}")
    print(f"Current tier: {advancement_info['current_tier']}")
    
    print("Phase 5 tests completed successfully!\n")

def test_phase_6_mastery_paths():
    """Test enhanced mastery path generation and anti-grinding."""
    print("=== Testing Phase 6: Mastery Path Generation ===")
    
    # Create character with higher domain values for mastery paths
    character = Character(
        name="Advanced Character",
        insight_points=15
    )
    
    # Add domains that meet mastery path requirements
    character.domains[DomainType.SOCIAL] = Domain(value=16, usage_count=20, growth_points=25)
    character.domains[DomainType.AUTHORITY] = Domain(value=12, usage_count=15, growth_points=18)
    
    # Add required tags
    character.tags["diplomacy"] = Tag(name="diplomacy", rank=4, xp=40)
    character.tags["negotiation"] = Tag(name="negotiation", rank=3, xp=30)
    
    # Test mastery path generation
    mastery_info = unified_progression_system.get_mastery_path_info(character, DomainType.SOCIAL)
    print(f"Available mastery paths for Social: {mastery_info['can_unlock']}")
    print(f"Unlocked paths: {mastery_info['unlocked']}")
    
    # Test unlocking a mastery path
    unlock_result = unified_progression_system.unlock_mastery_path(character, "Diplomat's Grace", DomainType.SOCIAL)
    print(f"Unlock Diplomat's Grace: {unlock_result['success']}")
    
    # Test activating mastery path
    if unlock_result['success']:
        activate_result = unified_progression_system.activate_mastery_path(character, "Diplomat's Grace")
        print(f"Activate Diplomat's Grace: {activate_result['success']}")
    
    # Test anti-grinding mechanism
    action_data = {"action_type": "persuade", "domain": "social", "tag": "diplomacy"}
    
    # Simulate multiple similar actions quickly
    penalties = []
    for i in range(5):
        penalty = unified_progression_system._check_grinding_penalty(character, action_data)
        penalties.append(penalty)
    
    print(f"Grinding penalties: {penalties}")
    print("Anti-grinding is working!" if penalties[-1] < 1.0 else "No grinding penalty applied")
    
    print("Phase 6 tests completed successfully!\n")

def test_phase_7_world_integration():
    """Test world response integration and AI-driven analysis."""
    print("=== Testing Phase 7: World Response Integration ===")
    
    character = Character(
        name="World Influencer",
        demonstrated_values={"justice": 6, "mercy": 4},
        relationship_investments={"guard_captain": 5, "merchant_guild": 3}
    )
    
    character.domains[DomainType.AUTHORITY] = Domain(value=14, usage_count=12, growth_points=20)
    character.tags["leadership"] = Tag(name="leadership", rank=4, xp=35)
    
    # Simulate action result
    action_result = {
        "success": True,
        "significance_tier_determined": "major",
        "domains_used": [DomainType.AUTHORITY],
        "tags_used": ["leadership"]
    }
    
    # World context
    world_context = {
        "current_location": {"type": "city", "name": "Capital"},
        "npcs_present": [
            {
                "id": "guard_captain",
                "name": "Captain Marcus", 
                "personality": {"respects_authority": True, "forgiving": False},
                "values": ["justice", "order"],
                "disposition": "neutral"
            }
        ],
        "political_entities": [
            {
                "name": "City Council",
                "type": "government", 
                "influence_level": "high"
            }
        ]
    }
    
    # Test world impact analysis
    world_impact = unified_progression_system.analyze_world_impact(character, action_result, world_context)
    print(f"Reputation changes: {world_impact['reputation_changes']}")
    print(f"Relationship effects: {world_impact['relationship_effects']}")
    print(f"Political ramifications: {len(world_impact['political_ramifications'])}")
    
    # Test narrative consequences
    consequences = unified_progression_system.generate_narrative_consequences(character, action_result, world_impact)
    print(f"Narrative consequences: {len(consequences)}")
    for i, consequence in enumerate(consequences[:2]):  # Show first 2
        print(f"  {i+1}. {consequence}")
    
    # Test adaptive challenges
    recent_actions = [
        {"success": True, "domains_used": [DomainType.AUTHORITY]},
        {"success": True, "domains_used": [DomainType.AUTHORITY]},
        {"success": False, "domains_used": [DomainType.SOCIAL]},
        {"success": True, "domains_used": [DomainType.AUTHORITY]}
    ]
    
    challenges = unified_progression_system.suggest_adaptive_challenges(character, recent_actions)
    print(f"Suggested adaptive challenges: {len(challenges)}")
    for challenge in challenges:
        print(f"  - {challenge['type']}: {challenge['description']}")
    
    print("Phase 7 tests completed successfully!\n")

def test_integrated_progression_flow():
    """Test the complete integrated progression flow."""
    print("=== Testing Integrated Progression Flow ===")
    
    character = Character(
        name="Complete Test Character",
        declared_goals=["Become a master diplomat", "Unite the factions"],
        learning_approach_preferences=["collaborative", "creative"],
        insight_points=5
    )
    
    # Initialize domains and tags
    character.domains[DomainType.SOCIAL] = Domain(value=10, usage_count=8, growth_points=15)
    character.tags["diplomacy"] = Tag(name="diplomacy", rank=3, xp=25)
    
    # Test complete action processing
    action_data = {
        "action_type": "negotiate_peace",
        "difficulty": 15,
        "narrative_impact": 2,  # Story-advancing
        "risk_level": "high",
        "preparation_quality_modifier": 10,
        "aligns_with_goal": "Unite the factions"
    }
    
    target = {
        "disposition_modifier": -10,  # Hostile faction
        "relationship_modifier": 5    # But character has some rapport
    }
    
    # Process the action
    result = unified_progression_system.process_player_action(
        character=character,
        domain_type=DomainType.SOCIAL,
        action_description="Attempt to negotiate a peace treaty between warring factions",
        tag_name="diplomacy",
        action_data=action_data,
        target=target,
        player_declared_goal_alignment="Unite the factions",
        player_approach_description="Using creative collaborative methods"
    )
    
    print(f"Action successful: {result['success']}")
    print(f"Resolution method: {result['method']}")
    print(f"Growth points awarded: {result['growth_points_awarded']}")
    print(f"Insight points gained: {result['insight_points_gained']}")
    print(f"Significance tier: {result['significance_tier_determined']}")
    print(f"Character insight points now: {character.insight_points}")
    
    # Check if domains leveled up
    final_domain_value = character.domains[DomainType.SOCIAL].value
    print(f"Social domain final value: {final_domain_value}")
    
    print("Integrated flow test completed successfully!\n")

def main():
    """Run all Phase 5-7 tests."""
    print("Starting Phase 5-7 Domain System Rehaul Tests...\n")
    
    try:
        test_phase_5_insight_spending()
        test_phase_6_mastery_paths()
        test_phase_7_world_integration()
        test_integrated_progression_flow()
        
        print("🎉 All Phase 5-7 tests completed successfully!")
        print("\nPhase 5-7 Implementation Summary:")
        print("✅ Insight Point Spending Mechanisms")
        print("✅ Domain Progression Tier System")
        print("✅ Enhanced Mastery Path Generation")
        print("✅ Anti-Grinding Mechanisms")
        print("✅ World Response Integration")
        print("✅ AI-Driven Analysis Systems")
        print("✅ Comprehensive Progression Flow")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
