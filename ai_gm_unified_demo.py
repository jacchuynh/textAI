#!/usr/bin/env python3
"""
AI GM Brain Unified Integration Example

This script demonstrates how to use the unified AI GM Brain system
and shows the integration between all components.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

# Add the backend src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_src = os.path.join(current_dir, 'backend', 'src')
sys.path.insert(0, backend_src)
sys.path.insert(0, current_dir)

try:
    from ai_gm.ai_gm_unified_integration import AIGMUnifiedSystem, create_unified_gm, create_gm_for_environment
    from ai_gm.ai_gm_config import IntegratedAIGMConfig
    UNIFIED_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import unified system: {e}")
    UNIFIED_SYSTEM_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demonstrate_basic_usage():
    """Demonstrate basic usage of the unified AI GM system."""
    print("=" * 60)
    print("AI GM Brain Unified Integration - Basic Usage Demo")
    print("=" * 60)
    
    if not UNIFIED_SYSTEM_AVAILABLE:
        print("❌ Unified system not available. Please check imports.")
        return
    
    # Create a unified GM system
    print("🔧 Creating unified AI GM system...")
    gm = create_unified_gm(
        game_id="demo_session_001",
        player_id="demo_player",
        initial_context={
            "player": {
                "name": "Adventurer",
                "domains": {"Combat": 3, "Social": 2, "Knowledge": 4},
                "health": 100,
                "experience": 150
            },
            "current_location": "Tavern of the Dancing Dragon",
            "location_description": "A cozy tavern filled with warm light and the murmur of conversations.",
            "active_npcs": ["Bartender Marcus", "Traveling Merchant", "Local Farmer"]
        }
    )
    
    # Show system status
    print("📊 System Status:")
    status = gm.get_system_status()
    print(f"   Game ID: {status['game_id']}")
    print(f"   Player ID: {status['player_id']}")
    print(f"   Available Systems:")
    for system, available in status['available_systems'].items():
        icon = "✅" if available else "❌"
        print(f"     {icon} {system.replace('_', ' ').title()}")
    
    # Test various input types
    test_inputs = [
        # OOC Commands
        "/help",
        "/status", 
        "/stats",
        "/location",
        
        # Simple commands
        "look around",
        "inventory",
        
        # Conversational inputs
        "What can you tell me about this tavern?",
        "Who is the bartender?",
        
        # Action commands
        "approach the bartender",
        "order a drink"
    ]
    
    print(f"\n🎮 Testing {len(test_inputs)} different input types...")
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n--- Test {i}: '{input_text}' ---")
        
        try:
            response = gm.process_player_input(input_text)
            
            print(f"Response: {response['response_text']}")
            
            # Show metadata for debugging
            metadata = response.get('metadata', {})
            if metadata:
                print(f"Processing Mode: {metadata.get('processing_mode', 'Unknown')}")
                print(f"Processing Time: {metadata.get('processing_time_total', 0):.3f}s")
                
                integrations = metadata.get('integrations', {})
                if integrations:
                    active_integrations = [k for k, v in integrations.items() if v]
                    if active_integrations:
                        print(f"Active Integrations: {', '.join(active_integrations)}")
            
        except Exception as e:
            print(f"❌ Error processing input: {e}")
    
    # Show final statistics
    print(f"\n📈 Final Integration Statistics:")
    stats = gm.get_integration_statistics()
    for system, system_stats in stats.items():
        if system_stats:
            print(f"   {system.title()}: {len(system_stats)} metrics")

async def demonstrate_async_usage():
    """Demonstrate async usage of the unified AI GM system."""
    print("\n" + "=" * 60)
    print("AI GM Brain Unified Integration - Async Usage Demo")
    print("=" * 60)
    
    if not UNIFIED_SYSTEM_AVAILABLE:
        print("❌ Unified system not available. Please check imports.")
        return
    
    # Create a unified GM system for async testing
    print("🔧 Creating unified AI GM system for async processing...")
    gm = create_gm_for_environment(
        environment="development",
        game_id="async_demo_002", 
        player_id="async_player"
    )
    
    # Set context for a more complex scenario
    gm.set_initial_context({
        "player": {
            "name": "Mage Thornwick",
            "domains": {"Magic": 5, "Knowledge": 4, "Social": 2},
            "health": 85,
            "mana": 120,
            "experience": 450
        },
        "current_location": "Ancient Library of Mystras",
        "location_description": "Towering shelves filled with arcane tomes stretch into shadow above.",
        "active_npcs": ["Librarian Sage Eldara", "Apprentice Scribe"],
        "world_state": {
            "political_stability": "unrest",
            "magical_resonance": "high",
            "time_of_day": "midnight"
        }
    })
    
    # Test async processing with more complex inputs
    async_test_inputs = [
        "I want to research information about ancient summoning rituals",
        "Ask Sage Eldara about the political situation in the realm",
        "Examine the magical aura in this library",
        "Look for any books about dimensional magic",
        "Cast a spell to detect magical items in the area"
    ]
    
    print(f"🎮 Testing {len(async_test_inputs)} complex inputs with async processing...")
    
    # Process inputs concurrently to show async capabilities
    tasks = []
    for i, input_text in enumerate(async_test_inputs, 1):
        task = gm.process_player_input_async(input_text)
        tasks.append((i, input_text, task))
    
    # Wait for all responses
    for i, input_text, task in tasks:
        print(f"\n--- Async Test {i}: '{input_text}' ---")
        
        try:
            response = await task
            
            print(f"Response: {response['response_text']}")
            
            # Show integration details
            metadata = response.get('metadata', {})
            integrations = metadata.get('integrations', {})
            if integrations:
                active = [k for k, v in integrations.items() if v]
                print(f"Integrations Used: {', '.join(active) if active else 'None'}")
            
            # Show world reaction if present
            world_reaction = response.get('world_reaction')
            if world_reaction:
                print(f"World Reaction: {world_reaction.get('status', 'Unknown')}")
            
            # Show pacing update if present
            pacing_update = response.get('pacing_update')
            if pacing_update:
                pacing_state = pacing_update.get('pacing_state', 'Unknown')
                print(f"Pacing State: {pacing_state}")
            
        except Exception as e:
            print(f"❌ Error in async processing: {e}")

def demonstrate_configuration_options():
    """Demonstrate different configuration options."""
    print("\n" + "=" * 60)
    print("AI GM Brain Unified Integration - Configuration Demo")
    print("=" * 60)
    
    if not UNIFIED_SYSTEM_AVAILABLE:
        print("❌ Unified system not available. Please check imports.")
        return
    
    # Show different environment configurations
    environments = ["development", "production", "testing"]
    
    for env in environments:
        print(f"\n🔧 {env.title()} Environment Configuration:")
        
        try:
            gm = create_gm_for_environment(
                environment=env,
                game_id=f"{env}_demo",
                player_id=f"{env}_player"
            )
            
            status = gm.get_system_status()
            available_count = sum(status['available_systems'].values())
            total_count = len(status['available_systems'])
            
            print(f"   Available Systems: {available_count}/{total_count}")
            print(f"   Game ID: {status['game_id']}")
            
            # Test a simple input
            response = gm.process_player_input("look around")
            processing_time = response.get('metadata', {}).get('processing_time_total', 0)
            print(f"   Sample Processing Time: {processing_time:.3f}s")
            
        except Exception as e:
            print(f"   ❌ Error creating {env} environment: {e}")

def test_error_handling():
    """Test error handling in the unified system."""
    print("\n" + "=" * 60)
    print("AI GM Brain Unified Integration - Error Handling Demo")
    print("=" * 60)
    
    if not UNIFIED_SYSTEM_AVAILABLE:
        print("❌ Unified system not available. Please check imports.")
        return
    
    # Create system
    gm = create_unified_gm("error_test", "error_player")
    
    # Test various error scenarios
    error_test_cases = [
        "",  # Empty input
        "a" * 1000,  # Very long input
        "/@#$%^&*()",  # Special characters
        "/nonexistent_command",  # Non-existent OOC command
        "thisismytestinputwithnospaces",  # No spaces
    ]
    
    print(f"🧪 Testing {len(error_test_cases)} error scenarios...")
    
    for i, test_input in enumerate(error_test_cases, 1):
        print(f"\n--- Error Test {i}: '{test_input[:50]}{'...' if len(test_input) > 50 else ''}' ---")
        
        try:
            response = gm.process_player_input(test_input)
            status = response.get('status', 'unknown')
            
            if status == 'error':
                print(f"✅ Error handled gracefully")
                print(f"   Error Response: {response.get('response_text', 'No response')}")
            else:
                print(f"✅ Processed successfully")
                print(f"   Response: {response.get('response_text', 'No response')[:100]}...")
                
        except Exception as e:
            print(f"❌ Unhandled exception: {e}")

def performance_test():
    """Test performance of the unified system."""
    print("\n" + "=" * 60)
    print("AI GM Brain Unified Integration - Performance Test")
    print("=" * 60)
    
    if not UNIFIED_SYSTEM_AVAILABLE:
        print("❌ Unified system not available. Please check imports.")
        return
    
    import time
    
    # Create system
    gm = create_unified_gm("perf_test", "perf_player")
    
    # Performance test inputs
    test_inputs = [
        "look",
        "inventory", 
        "go north",
        "attack",
        "What is this place?",
        "/stats"
    ] * 5  # Repeat each 5 times
    
    print(f"🏃 Running performance test with {len(test_inputs)} inputs...")
    
    start_time = time.time()
    processing_times = []
    
    for i, input_text in enumerate(test_inputs):
        iter_start = time.time()
        
        try:
            response = gm.process_player_input(input_text)
            iter_time = time.time() - iter_start
            processing_times.append(iter_time)
            
            if (i + 1) % 10 == 0:
                print(f"   Completed {i + 1}/{len(test_inputs)} inputs...")
                
        except Exception as e:
            print(f"   Error on input {i + 1}: {e}")
    
    total_time = time.time() - start_time
    
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        min_time = min(processing_times)
        max_time = max(processing_times)
        
        print(f"\n📊 Performance Results:")
        print(f"   Total Time: {total_time:.3f}s")
        print(f"   Average Processing Time: {avg_time:.3f}s")
        print(f"   Min Processing Time: {min_time:.3f}s")
        print(f"   Max Processing Time: {max_time:.3f}s")
        print(f"   Throughput: {len(test_inputs) / total_time:.1f} inputs/second")

async def main():
    """Run all demonstrations."""
    print("🎮 AI GM Brain Unified Integration - Comprehensive Demo")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not UNIFIED_SYSTEM_AVAILABLE:
        print("\n❌ Cannot run demo - unified system not available.")
        print("Please ensure all AI GM components are properly installed and accessible.")
        return
    
    try:
        # Run demonstrations
        demonstrate_basic_usage()
        await demonstrate_async_usage()
        demonstrate_configuration_options()
        test_error_handling()
        performance_test()
        
        print("\n" + "=" * 60)
        print("✅ All demonstrations completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
