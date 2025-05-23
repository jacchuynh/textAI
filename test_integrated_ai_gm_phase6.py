"""
Test script for the fully integrated AI GM Brain Phase 6 with Pacing, Domain, and Combat systems.

This test demonstrates how all systems work together:
1. World reaction system from Phase 5
2. Pacing and ambient storytelling from Phase 6
3. Integration with domain and combat systems
"""

import asyncio
import json
from datetime import datetime, timedelta
from backend.src.ai_gm.ai_gm_brain_phase6_complete import AIGMBrainPhase6Complete
from backend.src.ai_gm.ai_gm_delivery_system import DeliverySystem, DeliveryChannel, ResponsePriority


# Mock configuration
CONFIG = {
    'llm': {
        'model': 'gpt-3.5-turbo',
        'api_key': 'not-a-real-key',
        'temperature': 0.7,
        'max_tokens': 300
    },
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
}

# Simulation context (would be provided by the game in a real scenario)
SIMULATION_CONTEXT = {
    'current_location': 'Rusted Tavern',
    'player_id': 'player_123',
    'session_id': 'test_session_001',
    'current_season': 'autumn',
    'time_of_day': 'evening',
    'present_npcs': ['barkeeper', 'old_merchant', 'mysterious_stranger'],
    'npcs': {
        'barkeeper': {
            'name': 'Darius',
            'personality': 'friendly',
            'occupation': 'tavern owner'
        },
        'old_merchant': {
            'name': 'Geralt',
            'personality': 'wise',
            'occupation': 'retired merchant'
        },
        'mysterious_stranger': {
            'name': 'Shadowcloak',
            'personality': 'suspicious',
            'occupation': 'unknown'
        }
    },
    'world_state': {
        'political_stability': 'unrest',
        'economic_status': 'struggling',
        'local_threats': ['bandit activity', 'wolf pack']
    },
    'location_context': {
        'dominant_aura': 'welcoming',
        'notable_features': ['warm fireplace', 'trophy wall', 'wooden bar']
    },
    'player_reputation_summary': 'generally respected in town',
    'domains': {
        'active': ['PERCEPTION', 'SOCIAL', 'KNOWLEDGE'],
        'recent_outcomes': {
            'PERCEPTION': {'success': True, 'margin': 2},
            'SOCIAL': {'success': True, 'margin': 1},
            'KNOWLEDGE': {'success': False, 'margin': -1}
        }
    }
}

# Mock player interactions for testing
MOCK_INTERACTIONS = [
    {
        'input': 'I look around the tavern',
        'expected_domain': 'PERCEPTION'
    },
    {
        'input': 'I ask the barkeeper about rumors',
        'expected_domain': 'SOCIAL'
    },
    {
        'input': 'I recall what I know about local politics',
        'expected_domain': 'KNOWLEDGE'
    },
    {
        'input': 'I draw my sword and approach the mysterious stranger',
        'expected_domain': 'COMBAT'
    }
]

# Mock combat context
MOCK_COMBAT_CONTEXT = {
    'in_combat': True,
    'combatants': [
        {
            'id': 'player_123',
            'name': 'Player',
            'type': 'player',
            'health': 100,
            'stance': 'offensive'
        },
        {
            'id': 'mysterious_stranger',
            'name': 'Shadowcloak',
            'type': 'npc',
            'health': 80,
            'stance': 'defensive'
        }
    ],
    'environment': {
        'location': 'Rusted Tavern',
        'features': ['tables', 'chairs', 'bar counter', 'fireplace'],
        'bystanders': ['barkeeper', 'old_merchant', 'tavern patrons']
    },
    'turn': 1,
    'initiative_order': ['player_123', 'mysterious_stranger']
}


class MockDeliverySystem(DeliverySystem):
    """Mock delivery system for testing"""
    
    def __init__(self):
        self.delivered_messages = []
    
    async def deliver_response(self, 
                             response_text: str, 
                             channels=None, 
                             priority=ResponsePriority.NORMAL):
        """Mock delivery that just stores the messages"""
        if not channels:
            channels = [DeliveryChannel.NARRATIVE]
            
        channel_names = [c.name for c in channels]
        
        delivery = {
            'text': response_text,
            'channels': channel_names,
            'priority': priority.name,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.delivered_messages.append(delivery)
        print(f"[DELIVERED] [{priority.name}] {response_text} → {', '.join(channel_names)}")
        
    def get_delivered_messages(self):
        """Get all delivered messages"""
        return self.delivered_messages


class MockContextManager:
    """Mock context manager for testing"""
    
    def __init__(self, initial_context=None):
        self.context = initial_context or {}
        
    def get_current_context(self):
        """Return current context"""
        return self.context
        
    def update_context(self, updates):
        """Update context with new values"""
        self.context.update(updates)


class MockCombatIntegration:
    """Mock combat integration for testing"""
    
    async def enhance_combat_context(self, combat_context):
        """Enhance combat context with mock data"""
        enhanced = combat_context.copy()
        enhanced['extended_data'] = {
            'combat_style': 'aggressive',
            'environmental_factors': ['slippery floor', 'dim lighting'],
            'tactical_options': ['use furniture', 'intimidate bystanders']
        }
        return enhanced


async def mock_process_player_input(ai_gm, input_text):
    """Mock processing player input since we don't have real LLM"""
    print(f"[PLAYER] {input_text}")
    
    # Create a mock response
    response = {
        'response_text': f"Response to: {input_text}",
        'metadata': {
            'input_text': input_text,
            'event_type': 'PLAYER_INTERACTION',
            'decision_tree': {
                'success': True,
                'action_taken': 'process_input'
            }
        }
    }
    
    # Deliver response
    await ai_gm.deliver_response(
        response['response_text'], 
        channels=[DeliveryChannel.NARRATIVE], 
        priority=ResponsePriority.NORMAL
    )
    
    return response


async def test_world_reaction():
    """Test world reaction system"""
    print("\n=== Testing World Reaction System ===")
    
    ai_gm = AIGMBrainPhase6Complete(CONFIG)
    
    # Setup mocks
    mock_delivery = MockDeliverySystem()
    ai_gm.delivery_system = mock_delivery
    
    ai_gm.context_manager = MockContextManager(SIMULATION_CONTEXT)
    
    # Test player action reactions
    player_action = "I help the barkeeper clean up his tavern"
    target_entity = "barkeeper"
    action_context = {"effort": "significant", "motivation": "helpful"}
    
    print(f"[PLAYER ACTION] {player_action} (target: {target_entity})")
    
    # Assess world reaction
    reaction = await ai_gm.assess_world_reaction(
        player_action=player_action,
        target_entity=target_entity,
        action_context=action_context
    )
    
    print("[REACTION]")
    for key, value in reaction.items():
        print(f"  {key}: {value}")
    
    return reaction


async def test_pacing_system():
    """Test pacing system"""
    print("\n=== Testing Pacing System ===")
    
    ai_gm = AIGMBrainPhase6Complete(CONFIG)
    
    # Setup mocks
    mock_delivery = MockDeliverySystem()
    ai_gm.delivery_system = mock_delivery
    
    ai_gm.context_manager = MockContextManager(SIMULATION_CONTEXT)
    
    # Simulate player activity and response
    print("[SIMULATING PLAYER ACTIVITY]")
    
    for interaction in MOCK_INTERACTIONS[:2]:  # Just do the first two
        await mock_process_player_input(ai_gm, interaction['input'])
        await asyncio.sleep(0.2)  # Small delay to simulate time passing
    
    # Simulate idle period by adjusting last input time
    print("\n[SIMULATING IDLE PERIOD]")
    ai_gm.last_input_time = datetime.utcnow() - timedelta(minutes=5)
    
    # Check for ambient updates
    print("\n[CHECKING FOR AMBIENT UPDATES]")
    ambient_update = await ai_gm.check_ambient_updates()
    
    if ambient_update:
        print(f"Ambient update triggered: {ambient_update}")
    else:
        print("No ambient update triggered")
    
    # Get pacing statistics
    pacing_stats = ai_gm.get_pacing_statistics()
    
    print("\n[PACING STATISTICS]")
    print(json.dumps(pacing_stats, indent=2))
    
    return pacing_stats


async def test_domain_integration():
    """Test domain system integration"""
    print("\n=== Testing Domain System Integration ===")
    
    ai_gm = AIGMBrainPhase6Complete(CONFIG)
    
    # Setup mocks
    mock_delivery = MockDeliverySystem()
    ai_gm.delivery_system = mock_delivery
    
    ai_gm.context_manager = MockContextManager(SIMULATION_CONTEXT)
    
    # Test domain integration
    domain_context = {
        'current_domain': 'SOCIAL',
        'domain_level': 3,
        'active_domains': ['SOCIAL', 'PERCEPTION', 'KNOWLEDGE'],
        'recent_uses': {
            'SOCIAL': datetime.utcnow() - timedelta(minutes=10),
            'PERCEPTION': datetime.utcnow() - timedelta(minutes=30),
            'KNOWLEDGE': datetime.utcnow() - timedelta(hours=2)
        }
    }
    
    # Simulate idle period by adjusting last input time
    ai_gm.last_input_time = datetime.utcnow() - timedelta(minutes=6)
    
    # Integrate with domain system
    enhanced_domain = await ai_gm.integrate_with_domain_system(domain_context)
    
    print("[DOMAIN INTEGRATION RESULTS]")
    print("Enhanced domain context received these additional fields:")
    
    for key, value in enhanced_domain.items():
        if key not in domain_context:
            print(f"  + {key}: {value}")
    
    return enhanced_domain


async def test_combat_integration():
    """Test combat system integration"""
    print("\n=== Testing Combat System Integration ===")
    
    ai_gm = AIGMBrainPhase6Complete(CONFIG)
    
    # Setup mocks
    mock_delivery = MockDeliverySystem()
    ai_gm.delivery_system = mock_delivery
    
    ai_gm.context_manager = MockContextManager(SIMULATION_CONTEXT)
    ai_gm.combat_integration = MockCombatIntegration()
    
    # Test combat integration
    combat_context = MOCK_COMBAT_CONTEXT.copy()
    
    # Integrate with combat system
    enhanced_combat = await ai_gm.integrate_with_combat_system(combat_context)
    
    print("[COMBAT INTEGRATION RESULTS]")
    print("Enhanced combat context received these additional fields:")
    
    # Find all new fields at the top level
    for key, value in enhanced_combat.items():
        if key not in combat_context:
            print(f"  + {key}: {value}")
    
    # Check combatant-level enhancements
    for i, combatant in enumerate(enhanced_combat.get('combatants', [])):
        if 'reputation' in combatant:
            print(f"  + Combatant {combatant['name']} has reputation data")
    
    return enhanced_combat


async def test_full_integration():
    """Test full system integration"""
    print("\n=== Testing Full AI GM Phase 6 Integration ===")
    
    ai_gm = AIGMBrainPhase6Complete(CONFIG)
    
    # Setup mocks
    mock_delivery = MockDeliverySystem()
    ai_gm.delivery_system = mock_delivery
    
    ai_gm.context_manager = MockContextManager(SIMULATION_CONTEXT)
    ai_gm.combat_integration = MockCombatIntegration()
    
    # Test comprehensive statistics
    print("\n[COMPREHENSIVE SYSTEM STATISTICS]")
    
    stats = ai_gm.get_phase6_comprehensive_statistics()
    
    # Print a summary of the statistics
    print(f"Phase: {stats['phase']}")
    print(f"Timestamp: {stats['timestamp']}")
    
    # List all component categories
    print("\nComponent categories tracked:")
    for category in stats.keys():
        if category not in ['phase', 'timestamp']:
            print(f"  - {category}")
    
    # Check for specific subsystems
    subsystems = []
    if 'pacing' in stats:
        pacing_components = list(stats['pacing'].keys()) if isinstance(stats['pacing'], dict) else []
        subsystems.append(f"Pacing System ({len(pacing_components)} components)")
        
    if 'reputation' in stats:
        subsystems.append("Reputation System")
        
    if 'reaction_assessment' in stats:
        subsystems.append("Reaction Assessment")
        
    if 'enhanced_context' in stats:
        subsystems.append("Enhanced Context Management")
        
    print("\nSubsystems integrated:")
    for subsystem in subsystems:
        print(f"  - {subsystem}")
        
    return stats


async def main():
    """Run all tests"""
    print("=== Testing AI GM Brain Phase 6 Complete Integration ===\n")
    
    # Test each subsystem
    await test_world_reaction()
    await test_pacing_system()
    await test_domain_integration()
    await test_combat_integration()
    await test_full_integration()
    
    print("\n=== All integration tests completed ===")


if __name__ == "__main__":
    asyncio.run(main())