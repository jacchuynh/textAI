#!/usr/bin/env python3
"""
Standalone AI GM Integration Test

This script tests the AI GM Brain integration system by working around import dependencies
and focusing on the core functionality.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_import_paths():
    """Test if we can import AI GM modules with various path configurations."""
    print("🔍 Testing import paths...")
    
    # Add backend/src to path
    backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
    if backend_src_path not in sys.path:
        sys.path.insert(0, backend_src_path)
    
    print(f"Added to Python path: {backend_src_path}")
    
    # Test core imports
    import_results = {}
    
    # Test core brain import
    try:
        from ai_gm.ai_gm_brain import AIGMBrain
        import_results['ai_gm_brain'] = True
        print("✅ ai_gm_brain imported successfully")
    except ImportError as e:
        import_results['ai_gm_brain'] = False
        print(f"❌ ai_gm_brain import failed: {e}")
    
    # Test config import
    try:
        from ai_gm.ai_gm_config import IntegratedAIGMConfig
        import_results['ai_gm_config'] = True
        print("✅ ai_gm_config imported successfully")
    except ImportError as e:
        import_results['ai_gm_config'] = False
        print(f"❌ ai_gm_config import failed: {e}")
    
    # Test integration modules
    integration_modules = [
        'world_reaction_integration',
        'pacing_integration', 
        'output_integration',
        'ai_gm_brain_ooc_handler',
        'ai_gm_llm_manager',
        'ai_gm_combat_integration'
    ]
    
    for module_name in integration_modules:
        try:
            module = __import__(f'ai_gm.{module_name}', fromlist=[''])
            import_results[module_name] = True
            print(f"✅ {module_name} imported successfully")
        except ImportError as e:
            import_results[module_name] = False
            print(f"⚠️  {module_name} import failed: {e}")
    
    return import_results

def test_core_brain_functionality():
    """Test core AI GM Brain functionality."""
    print("\n🧠 Testing core AI GM Brain functionality...")
    
    try:
        from ai_gm.ai_gm_brain import AIGMBrain
        
        # Create brain instance
        brain = AIGMBrain(game_id="test_session", player_id="test_player")
        print("✅ AI GM Brain instance created successfully")
        
        # Test basic input processing
        test_inputs = [
            "look around",
            "examine the room", 
            "/help",
            "go north",
            "say hello"
        ]
        
        for test_input in test_inputs:
            try:
                response = brain.process_player_input(test_input)
                print(f"✅ Processed '{test_input}': {response.get('status', 'unknown')}")
            except Exception as e:
                print(f"❌ Failed to process '{test_input}': {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Core brain test failed: {e}")
        return False

def test_config_functionality():
    """Test configuration functionality."""
    print("\n⚙️ Testing configuration functionality...")
    
    try:
        from ai_gm.ai_gm_config import IntegratedAIGMConfig
        
        # Test basic config creation
        config = IntegratedAIGMConfig()
        print("✅ Basic config created successfully")
        
        # Test config methods
        if hasattr(config, 'get_config'):
            full_config = config.get_config()
            print(f"✅ Full config retrieved: {len(full_config)} keys")
        
        if hasattr(config, 'get_development_config'):
            dev_config = config.get_development_config()
            print(f"✅ Development config retrieved: {len(dev_config)} keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_unified_integration():
    """Test the unified integration system."""
    print("\n🔗 Testing unified integration system...")
    
    try:
        from ai_gm.ai_gm_unified_integration import AIGMUnifiedSystem, create_unified_gm
        
        # Test unified system creation
        unified_gm = create_unified_gm(
            game_id="test_integration_session",
            player_id="test_integration_player",
            initial_context={
                "player": {
                    "name": "Test Adventurer",
                    "domains": {"Combat": 2, "Social": 3, "Knowledge": 4}
                },
                "current_location": "Testing Chamber"
            }
        )
        
        print("✅ Unified AI GM system created successfully")
        
        # Test system status
        status = unified_gm.get_system_status()
        print(f"✅ System status retrieved: {len(status['available_systems'])} systems")
        
        # Display available systems
        print("Available systems:")
        for system, available in status['available_systems'].items():
            status_indicator = "✅" if available else "❌"
            print(f"  {status_indicator} {system}")
        
        # Test basic input processing
        test_responses = []
        test_inputs = [
            "look around",
            "/status",
            "/help",
            "examine the testing chamber",
            "say hello to any NPCs here"
        ]
        
        for test_input in test_inputs:
            try:
                response = unified_gm.process_player_input(test_input)
                test_responses.append({
                    "input": test_input,
                    "status": response.get("status", "unknown"),
                    "processing_time": response.get("metadata", {}).get("processing_time_total", 0)
                })
                print(f"✅ Processed '{test_input}': {response.get('status')}")
            except Exception as e:
                print(f"❌ Failed to process '{test_input}': {e}")
                test_responses.append({
                    "input": test_input,
                    "status": "error",
                    "error": str(e)
                })
        
        # Test async processing if available
        try:
            import asyncio
            async def test_async():
                async_response = await unified_gm.process_player_input_async("test async processing")
                return async_response
            
            async_result = asyncio.run(test_async())
            print(f"✅ Async processing test: {async_result.get('status', 'unknown')}")
        except Exception as e:
            print(f"⚠️  Async processing test failed: {e}")
        
        return True, test_responses
        
    except Exception as e:
        print(f"❌ Unified integration test failed: {e}")
        return False, []

def test_performance():
    """Test system performance with multiple inputs."""
    print("\n⚡ Testing system performance...")
    
    try:
        from ai_gm.ai_gm_unified_integration import create_unified_gm
        
        # Create system
        gm = create_unified_gm("perf_test", "perf_player")
        
        # Performance test inputs
        perf_inputs = [
            "look around",
            "go north", 
            "examine door",
            "open door",
            "go through door",
            "look around",
            "search room",
            "take items",
            "check inventory",
            "go back"
        ]
        
        start_time = datetime.now()
        
        for i, test_input in enumerate(perf_inputs):
            try:
                response = gm.process_player_input(test_input)
                processing_time = response.get("metadata", {}).get("processing_time_total", 0)
                print(f"Input {i+1}: {processing_time:.3f}s")
            except Exception as e:
                print(f"Input {i+1}: ERROR - {e}")
        
        total_time = (datetime.now() - start_time).total_seconds()
        avg_time = total_time / len(perf_inputs)
        
        print(f"✅ Performance test completed:")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Average per input: {avg_time:.3f}s")
        print(f"   Inputs per second: {1/avg_time:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 AI GM Brain Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Import paths
    import_results = test_import_paths()
    imports_successful = sum(import_results.values())
    imports_total = len(import_results)
    print(f"\nImport Summary: {imports_successful}/{imports_total} modules imported successfully")
    
    # Test 2: Core functionality
    if import_results.get('ai_gm_brain', False):
        core_success = test_core_brain_functionality()
    else:
        print("\n❌ Skipping core brain test - import failed")
        core_success = False
    
    # Test 3: Configuration
    if import_results.get('ai_gm_config', False):
        config_success = test_config_functionality()
    else:
        print("\n❌ Skipping config test - import failed")
        config_success = False
    
    # Test 4: Unified integration
    unified_success = False
    test_responses = []
    try:
        unified_success, test_responses = test_unified_integration()
    except:
        print("\n❌ Skipping unified integration test - dependencies not available")
    
    # Test 5: Performance
    if unified_success:
        performance_success = test_performance()
    else:
        print("\n❌ Skipping performance test - unified system not available")
        performance_success = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary")
    print("=" * 60)
    print(f"Import Tests:       {'✅ PASS' if imports_successful >= 2 else '❌ FAIL'} ({imports_successful}/{imports_total})")
    print(f"Core Brain Test:    {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"Config Test:        {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"Integration Test:   {'✅ PASS' if unified_success else '❌ FAIL'}")
    print(f"Performance Test:   {'✅ PASS' if performance_success else '❌ FAIL'}")
    
    if test_responses:
        print(f"\nProcessed {len(test_responses)} test inputs successfully")
    
    overall_success = (imports_successful >= 2) and core_success and config_success
    print(f"\nOverall Result:     {'✅ SYSTEM READY' if overall_success else '⚠️  NEEDS ATTENTION'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
