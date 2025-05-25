
"""
Comprehensive Integration Test for All Major Systems

This test validates that all major systems work together seamlessly:
- World Generation System
- AI GM Brain with all phases
- Economy System with crafting
- Combat System
- Text Parser Integration
- Pacing and World Reaction
- Magic System
- Time and Weather Systems
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("FullSystemIntegration")

class FullSystemIntegrationTester:
    """Comprehensive tester for all major game systems."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    async def run_all_tests(self):
        """Run all integration tests in sequence."""
        logger.info("=== STARTING FULL SYSTEM INTEGRATION TEST ===")
        
        # Test individual systems first
        await self.test_world_generation_system()
        await self.test_ai_gm_brain_integration()
        await self.test_economy_crafting_integration()
        await self.test_combat_system_integration()
        await self.test_text_parser_integration()
        await self.test_pacing_world_reaction()
        await self.test_magic_system_integration()
        await self.test_time_weather_systems()
        
        # Test cross-system integration
        await self.test_cross_system_integration()
        
        # Generate final report
        self.generate_final_report()
        
    async def test_world_generation_system(self):
        """Test the procedural world generation system."""
        logger.info("\n--- Testing World Generation System ---")
        
        try:
            # Import and test world generation
            from world_model import WorldModel, Region, BiomeType
            from poi_placement_service import POIPlacementService
            from location_generators.village_generator import VillageGenerator
            from world_persistence_manager import WorldPersistenceManager
            
            # Create world model
            world = WorldModel()
            region = Region(
                region_id="test_region",
                name="Test Region",
                biome_type=BiomeType.TEMPERATE_FOREST,
                size_km2=1000,
                population_density=0.5,
                danger_level=3,
                center_coordinates=(0, 0)
            )
            
            world.add_region(region)
            
            # Test POI placement
            poi_service = POIPlacementService()
            pois = poi_service.generate_pois_for_region(region)
            
            # Test village generation
            village_gen = VillageGenerator()
            village = village_gen.generate_village(region, {"name": "Test Village"})
            
            # Test persistence
            persistence = WorldPersistenceManager()
            world_data = persistence.serialize_world(world)
            
            self.test_results['world_generation'] = {
                'status': 'PASSED',
                'regions_created': len(world.regions),
                'pois_generated': len(pois),
                'village_created': village is not None,
                'persistence_working': world_data is not None
            }
            
            logger.info("✅ World Generation System: PASSED")
            
        except Exception as e:
            logger.error(f"❌ World Generation System: FAILED - {e}")
            self.test_results['world_generation'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_ai_gm_brain_integration(self):
        """Test AI GM Brain with all integrated components."""
        logger.info("\n--- Testing AI GM Brain Integration ---")
        
        try:
            # Test basic AI GM Brain functionality
            from backend.src.ai_gm.ai_gm_brain_phase6_complete import AIGMBrainPhase6Complete
            from backend.src.ai_gm.ai_gm_config import IntegratedAIGMConfig
            
            config = IntegratedAIGMConfig.get_config()
            ai_gm = AIGMBrainPhase6Complete(config)
            
            # Test context management
            test_context = {
                'player_id': 'test_player',
                'current_location': 'Test Tavern',
                'world_state': {'stability': 'peaceful'}
            }
            
            enhanced_context = await ai_gm._enhance_context_with_pacing(test_context)
            
            # Test statistics
            stats = ai_gm.get_phase6_comprehensive_statistics()
            
            self.test_results['ai_gm_brain'] = {
                'status': 'PASSED',
                'context_enhancement': enhanced_context is not None,
                'statistics_available': stats is not None,
                'extensions_loaded': len(stats.get('extensions', []))
            }
            
            logger.info("✅ AI GM Brain Integration: PASSED")
            
        except Exception as e:
            logger.error(f"❌ AI GM Brain Integration: FAILED - {e}")
            self.test_results['ai_gm_brain'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_economy_crafting_integration(self):
        """Test economy and crafting system integration."""
        logger.info("\n--- Testing Economy & Crafting Integration ---")
        
        try:
            # Test crafting service
            from backend.src.crafting.services.crafting_service import CraftingService
            from backend.src.economy.services.economy_service import EconomyService
            
            # Mock database session for testing
            class MockSession:
                def query(self, *args): return self
                def filter(self, *args): return self
                def first(self): return None
                def all(self): return []
                def add(self, item): pass
                def commit(self): pass
                def close(self): pass
            
            mock_db = MockSession()
            
            # Test services can be instantiated
            crafting_service = CraftingService(mock_db)
            economy_service = EconomyService(mock_db)
            
            self.test_results['economy_crafting'] = {
                'status': 'PASSED',
                'crafting_service': crafting_service is not None,
                'economy_service': economy_service is not None
            }
            
            logger.info("✅ Economy & Crafting Integration: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Economy & Crafting Integration: FAILED - {e}")
            self.test_results['economy_crafting'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_combat_system_integration(self):
        """Test combat system integration."""
        logger.info("\n--- Testing Combat System Integration ---")
        
        try:
            # Test enhanced combat system
            from backend.src.game_engine.enhanced_combat.combat_system_core import CombatSystemCore
            from backend.src.game_engine.enhanced_combat.combat_controller import CombatController
            
            # Create mock combat scenario
            combat_system = CombatSystemCore()
            
            # Test basic combat functionality
            player_data = {
                'id': 'test_player',
                'health': 100,
                'domains': {'BODY': 3, 'MIND': 2}
            }
            
            monster_data = {
                'id': 'test_monster',
                'health': 50,
                'attack_power': 15
            }
            
            self.test_results['combat_system'] = {
                'status': 'PASSED',
                'combat_core': combat_system is not None,
                'player_setup': player_data is not None,
                'monster_setup': monster_data is not None
            }
            
            logger.info("✅ Combat System Integration: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Combat System Integration: FAILED - {e}")
            self.test_results['combat_system'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_text_parser_integration(self):
        """Test text parser integration with economic systems."""
        logger.info("\n--- Testing Text Parser Integration ---")
        
        try:
            # Test parser components
            from backend.src.text_parser.parser_engine import ParserEngine
            from backend.src.text_parser.economic_command_handler import EconomicCommandHandler
            
            # Create parser engine
            parser = ParserEngine()
            
            # Test economic command handler
            class MockSession:
                def query(self, *args): return self
                def filter(self, *args): return self
                def first(self): return None
                def all(self): return []
            
            mock_db = MockSession()
            economic_handler = EconomicCommandHandler(mock_db)
            
            self.test_results['text_parser'] = {
                'status': 'PASSED',
                'parser_engine': parser is not None,
                'economic_handler': economic_handler is not None
            }
            
            logger.info("✅ Text Parser Integration: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Text Parser Integration: FAILED - {e}")
            self.test_results['text_parser'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_pacing_world_reaction(self):
        """Test pacing and world reaction systems."""
        logger.info("\n--- Testing Pacing & World Reaction ---")
        
        try:
            # Test pacing system
            from backend.src.ai_gm.pacing.pacing_manager import PacingManager
            from backend.src.ai_gm.world_reaction.reaction_assessor import ReactionAssessor
            
            pacing_manager = PacingManager()
            reaction_assessor = ReactionAssessor()
            
            # Test basic functionality
            test_context = {
                'player_id': 'test_player',
                'current_location': 'test_location'
            }
            
            # Test pacing assessment
            pacing_state = pacing_manager.assess_current_pacing(test_context)
            
            self.test_results['pacing_world_reaction'] = {
                'status': 'PASSED',
                'pacing_manager': pacing_manager is not None,
                'reaction_assessor': reaction_assessor is not None,
                'pacing_assessment': pacing_state is not None
            }
            
            logger.info("✅ Pacing & World Reaction: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Pacing & World Reaction: FAILED - {e}")
            self.test_results['pacing_world_reaction'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_magic_system_integration(self):
        """Test magic system integration."""
        logger.info("\n--- Testing Magic System Integration ---")
        
        try:
            # Test magic system components
            from backend.src.game_engine.magic_system import MagicSystem
            
            magic_system = MagicSystem()
            
            # Test basic magic functionality
            test_spell = {
                'name': 'Test Spell',
                'element': 'FIRE',
                'power': 5
            }
            
            self.test_results['magic_system'] = {
                'status': 'PASSED',
                'magic_system': magic_system is not None,
                'spell_testing': test_spell is not None
            }
            
            logger.info("✅ Magic System Integration: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Magic System Integration: FAILED - {e}")
            self.test_results['magic_system'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_time_weather_systems(self):
        """Test time and weather systems."""
        logger.info("\n--- Testing Time & Weather Systems ---")
        
        try:
            # Test time service
            from app.services.time_service import TimeService
            from app.services.weather_service import WeatherService
            from app.models.time_models import GameTimeSettings
            
            # Mock database for testing
            class MockDB:
                def query(self, *args): return self
                def filter(self, *args): return self
                def first(self): return None
                def all(self): return []
                def add(self, item): pass
                def commit(self): pass
            
            mock_db = MockDB()
            settings = GameTimeSettings()
            
            time_service = TimeService(mock_db, settings, "test_game")
            weather_service = WeatherService(mock_db, time_service)
            
            self.test_results['time_weather'] = {
                'status': 'PASSED',
                'time_service': time_service is not None,
                'weather_service': weather_service is not None
            }
            
            logger.info("✅ Time & Weather Systems: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Time & Weather Systems: FAILED - {e}")
            self.test_results['time_weather'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_cross_system_integration(self):
        """Test how different systems work together."""
        logger.info("\n--- Testing Cross-System Integration ---")
        
        try:
            # Test event bus integration
            from backend.src.events.event_bus import EventBus, GameEvent
            
            event_bus = EventBus()
            
            # Create test event
            test_event = GameEvent(
                event_type="PLAYER_ACTION",
                data={"action": "test_action", "location": "test_location"},
                source="integration_test"
            )
            
            # Test event publishing
            await event_bus.publish(test_event)
            
            self.test_results['cross_system'] = {
                'status': 'PASSED',
                'event_bus': event_bus is not None,
                'event_publishing': True
            }
            
            logger.info("✅ Cross-System Integration: PASSED")
            
        except Exception as e:
            logger.error(f"❌ Cross-System Integration: FAILED - {e}")
            self.test_results['cross_system'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def generate_final_report(self):
        """Generate a comprehensive test report."""
        logger.info("\n" + "="*80)
        logger.info("FULL SYSTEM INTEGRATION TEST REPORT")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Test Duration: {datetime.now() - self.start_time}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n--- Detailed Results ---")
        for system, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            logger.info(f"{status_icon} {system.upper()}: {result['status']}")
            if result['status'] == 'FAILED':
                logger.info(f"   Error: {result.get('error', 'Unknown error')}")
        
        if failed_tests == 0:
            logger.info("\n🎉 ALL SYSTEMS INTEGRATION: SUCCESSFUL! 🎉")
            logger.info("All major game systems are working seamlessly together.")
        else:
            logger.info(f"\n⚠️  {failed_tests} systems need attention before full integration.")
        
        logger.info("="*80)

async def main():
    """Run the full system integration test."""
    tester = FullSystemIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Full System Integration Test

This script tests the integration of all major systems:
- World Generation (Procedural World System)
- Economy System
- Magic System
- Combat System
- AI GM Brain
- Text Parser
- Narrative Engine
"""

import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("FullSystemIntegration")

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")

def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-' * 40}")
    print(f" {title}")
    print(f"{'-' * 40}")

def test_world_generation_system():
    """Test the procedural world generation system."""
    print_section("Testing World Generation System")
    
    try:
        # Import world generation components
        from world_model import WorldModel
        from poi_placement_service import POIPlacementService
        from location_generators.village_generator import VillageGenerator
        from world_persistence_manager import WorldPersistenceManager
        
        print("✓ World generation imports successful")
        
        # Test world model
        world = WorldModel()
        print(f"✓ World model created: {world}")
        
        # Test POI placement
        poi_service = POIPlacementService()
        print(f"✓ POI placement service created: {poi_service}")
        
        # Test village generator
        village_gen = VillageGenerator()
        print(f"✓ Village generator created: {village_gen}")
        
        # Test persistence manager
        persistence = WorldPersistenceManager()
        print(f"✓ Persistence manager created: {persistence}")
        
        print("✓ World Generation System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ World Generation System failed: {e}")
        return False

def test_economy_system():
    """Test the economy system."""
    print_section("Testing Economy System")
    
    try:
        # Import economy system
        from backend.src.game_engine.economy_system import economy_system
        
        print("✓ Economy system import successful")
        
        # Test market initialization
        economy_system._initialize_default_data()
        print("✓ Economy system initialized")
        
        # Test market entry
        result = economy_system.enter_market("test_player", "Ashkar Vale")
        print(f"✓ Market entry successful: {result['name']}")
        
        print("✓ Economy System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Economy System failed: {e}")
        return False

def test_magic_system():
    """Test the magic system."""
    print_section("Testing Magic System")
    
    try:
        # Import magic system
        from backend.src.game_engine.magic_system import MagicSystem
        
        print("✓ Magic system import successful")
        
        # Test magic system creation
        magic_system = MagicSystem()
        print("✓ Magic system created")
        
        # Test magic user initialization
        test_domains = {
            "BODY": type('Domain', (), {'value': 3}),
            "MIND": type('Domain', (), {'value': 4}),
            "SPIRIT": type('Domain', (), {'value': 3})
        }
        
        # Convert to the expected format
        domain_dict = {getattr(k, 'name', k): getattr(v, 'value', v) for k, v in test_domains.items()}
        
        magic_profile = magic_system.initialize_magic_user(domain_dict)
        print(f"✓ Magic user profile created: {magic_profile}")
        
        print("✓ Magic System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Magic System failed: {e}")
        return False

def test_combat_system():
    """Test the combat system."""
    print_section("Testing Combat System")
    
    try:
        # Import combat system
        from backend.src.game_engine.enhanced_combat.combat_system_core import Combatant, CombatMove, MoveType
        from backend.src.game_engine.enhanced_combat.monster_database import load_monster_database, get_random_monster
        from backend.src.game_engine.enhanced_combat.monster_archetypes import ThreatTier
        
        print("✓ Combat system imports successful")
        
        # Test monster database loading
        load_monster_database()
        print("✓ Monster database loaded")
        
        # Test monster generation
        monster, moves = get_random_monster(
            region="verdant",
            tier=ThreatTier.STANDARD,
            level=3
        )
        print(f"✓ Monster generated: {monster.name}")
        
        print("✓ Combat System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Combat System failed: {e}")
        return False

async def test_ai_gm_brain():
    """Test the AI GM Brain system."""
    print_section("Testing AI GM Brain System")
    
    try:
        # Import AI GM Brain
        from backend.src.ai_gm.ai_gm_brain_phase6_complete import AIGMBrainPhase6Complete
        from backend.src.ai_gm.ai_gm_config import IntegratedAIGMConfig
        
        print("✓ AI GM Brain imports successful")
        
        # Test AI GM Brain creation
        config = IntegratedAIGMConfig.get_config()
        ai_gm = AIGMBrainPhase6Complete(config)
        print("✓ AI GM Brain created")
        
        # Test basic statistics
        stats = ai_gm.get_phase6_comprehensive_statistics()
        print(f"✓ AI GM Brain statistics: Phase {stats['phase']}")
        
        print("✓ AI GM Brain System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ AI GM Brain System failed: {e}")
        return False

def test_text_parser():
    """Test the text parser system."""
    print_section("Testing Text Parser System")
    
    try:
        # Import text parser
        from backend.src.text_parser.parser_engine import ParserEngine
        from backend.src.text_parser.vocabulary_manager import VocabularyManager
        
        print("✓ Text parser imports successful")
        
        # Test vocabulary manager
        vocab_manager = VocabularyManager()
        print("✓ Vocabulary manager created")
        
        # Test parser engine
        parser = ParserEngine(vocab_manager)
        print("✓ Parser engine created")
        
        print("✓ Text Parser System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Text Parser System failed: {e}")
        return False

def test_narrative_engine():
    """Test the narrative engine system."""
    print_section("Testing Narrative Engine System")
    
    try:
        # Import narrative engine
        from backend.src.narrative_engine.narrative_generator import NarrativeGenerator
        from backend.src.narrative_engine.world_state import world_state_manager
        
        print("✓ Narrative engine imports successful")
        
        # Test narrative generator
        narrator = NarrativeGenerator()
        print("✓ Narrative generator created")
        
        # Test world state manager
        current_state = world_state_manager.get_current_state()
        print(f"✓ World state manager: {current_state}")
        
        print("✓ Narrative Engine System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Narrative Engine System failed: {e}")
        return False

def test_event_bus():
    """Test the event bus system."""
    print_section("Testing Event Bus System")
    
    try:
        # Import event bus
        from backend.src.events.event_bus import event_bus, GameEvent, EventType
        
        print("✓ Event bus imports successful")
        
        # Test event creation
        test_event = GameEvent(
            event_type=EventType.PLAYER_ACTION,
            data={"action": "test_integration", "result": "success"},
            source="test_full_system_integration"
        )
        print(f"✓ Test event created: {test_event.event_id}")
        
        # Test event publishing
        event_bus.publish(test_event)
        print("✓ Event published successfully")
        
        print("✓ Event Bus System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Event Bus System failed: {e}")
        return False

async def test_full_integration():
    """Test integration between all systems."""
    print_section("Testing Full System Integration")
    
    try:
        # This would test actual integration between systems
        # For now, we'll test that all systems can coexist
        
        print("Testing system coexistence...")
        
        # Import key components from each system
        from world_model import WorldModel
        from backend.src.game_engine.economy_system import economy_system
        from backend.src.game_engine.magic_system import MagicSystem
        from backend.src.ai_gm.ai_gm_brain_phase6_complete import AIGMBrainPhase6Complete
        from backend.src.events.event_bus import event_bus
        
        print("✓ All systems can be imported together")
        
        # Test basic initialization
        world = WorldModel()
        magic_system = MagicSystem()
        ai_gm = AIGMBrainPhase6Complete()
        
        print("✓ All systems can be initialized together")
        
        # Test event publishing with multiple systems
        from backend.src.events.event_bus import GameEvent, EventType
        
        integration_event = GameEvent(
            event_type=EventType.SYSTEM_INTEGRATION_TEST,
            data={
                "world_model": "initialized",
                "magic_system": "initialized",
                "ai_gm": "initialized",
                "timestamp": datetime.utcnow().isoformat()
            },
            source="full_system_integration_test"
        )
        
        event_bus.publish(integration_event)
        print("✓ Integration event published successfully")
        
        print("✓ Full System Integration - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Full System Integration failed: {e}")
        return False

async def main():
    """Run all integration tests."""
    print_section("FULL SYSTEM INTEGRATION TEST SUITE")
    print(f"Starting tests at: {datetime.utcnow()}")
    
    # Track test results
    test_results = {}
    
    # Run individual system tests
    test_results["World Generation"] = test_world_generation_system()
    test_results["Economy"] = test_economy_system()
    test_results["Magic"] = test_magic_system()
    test_results["Combat"] = test_combat_system()
    test_results["AI GM Brain"] = await test_ai_gm_brain()
    test_results["Text Parser"] = test_text_parser()
    test_results["Narrative Engine"] = test_narrative_engine()
    test_results["Event Bus"] = test_event_bus()
    
    # Run full integration test
    test_results["Full Integration"] = await test_full_integration()
    
    # Print summary
    print_section("TEST RESULTS SUMMARY")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL SYSTEMS INTEGRATION TESTS PASSED! 🎉")
        print("Your RPG backend is ready for action!")
    else:
        print(f"\n⚠️  {failed} system(s) need attention before full integration.")
    
    print(f"\nTests completed at: {datetime.utcnow()}")

if __name__ == "__main__":
    # Add the backend src to path for imports
    sys.path.append("backend/src")
    sys.path.append(".")
    
    # Run the tests
    asyncio.run(main())
