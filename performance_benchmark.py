#!/usr/bin/env python3
"""
AI GM Performance Benchmark Suite

This script runs comprehensive benchmarks to validate the performance optimizations
implemented in the AI GM unified integration system.
"""

import asyncio
import time
import statistics
import logging
from typing import Dict, List, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text} ")
    print("=" * 80)

def print_section(text: str):
    """Print a section divider"""
    print(f"\n{'─' * 20} {text} {'─' * 20}")

class PerformanceBenchmark:
    """Comprehensive performance benchmark suite"""
    
    def __init__(self):
        self.results = {}
        
    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print_header("AI GM PERFORMANCE BENCHMARK SUITE")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: System initialization speed
        self.test_system_initialization()
        
        # Test 2: Basic processing speed
        self.test_basic_processing_speed()
        
        # Test 3: Concurrent processing
        self.test_concurrent_processing()
        
        # Test 4: Memory usage
        self.test_memory_efficiency()
        
        # Test 5: System stress test
        self.test_system_stress()
        
        # Test 6: Optimization effectiveness
        self.test_optimization_effectiveness()
        
        # Generate final report
        self.generate_benchmark_report()
    
    def test_system_initialization(self):
        """Test system initialization performance"""
        print_section("System Initialization Speed")
        
        try:
            # Test unified system creation
            start_time = time.time()
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
            
            gm = create_unified_gm(
                game_id="benchmark_init",
                player_id="benchmark_player",
                initial_context={
                    "player": {"name": "Benchmark Tester", "health": 100},
                    "current_location": "Test Environment"
                }
            )
            init_time = time.time() - start_time
            
            # Get system status
            status = gm.get_system_status()
            active_systems = sum(1 for available in status['available_systems'].values() if available)
            
            print(f"✅ System initialized in {init_time:.3f}s")
            print(f"📊 Active systems: {active_systems}/{len(status['available_systems'])}")
            
            self.results['initialization'] = {
                'time': init_time,
                'active_systems': active_systems,
                'total_systems': len(status['available_systems'])
            }
            
        except Exception as e:
            print(f"❌ Initialization test failed: {e}")
            self.results['initialization'] = {'error': str(e)}
    
    def test_basic_processing_speed(self):
        """Test basic input processing speed"""
        print_section("Basic Processing Speed")
        
        try:
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
            
            gm = create_unified_gm("benchmark_basic", "benchmark_player")
            
            # Test various input types
            test_inputs = [
                "look around",
                "go north", 
                "examine room",
                "say hello",
                "open door",
                "check inventory",
                "rest here",
                "cast spell",
                "attack monster",
                "use item"
            ]
            
            processing_times = []
            
            for i, input_text in enumerate(test_inputs, 1):
                start_time = time.time()
                result = gm.process_player_input(input_text)
                processing_time = time.time() - start_time
                processing_times.append(processing_time)
                
                print(f"Input {i:2d}: {processing_time:.4f}s - {input_text}")
            
            # Calculate statistics
            avg_time = statistics.mean(processing_times)
            median_time = statistics.median(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)
            
            print(f"\n📈 Processing Statistics:")
            print(f"   Average: {avg_time:.4f}s")
            print(f"   Median:  {median_time:.4f}s") 
            print(f"   Min:     {min_time:.4f}s")
            print(f"   Max:     {max_time:.4f}s")
            print(f"   Rate:    {1/avg_time:.1f} inputs/second")
            
            self.results['basic_processing'] = {
                'avg_time': avg_time,
                'median_time': median_time,
                'min_time': min_time,
                'max_time': max_time,
                'rate': 1/avg_time,
                'samples': len(processing_times)
            }
            
        except Exception as e:
            print(f"❌ Basic processing test failed: {e}")
            self.results['basic_processing'] = {'error': str(e)}
    
    def test_concurrent_processing(self):
        """Test concurrent processing capabilities"""
        print_section("Concurrent Processing")
        
        try:
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
            
            gm = create_unified_gm("benchmark_concurrent", "benchmark_player")
            
            # Test concurrent processing if async methods are available
            if hasattr(gm, 'process_player_input_async'):
                print("Testing async concurrent processing...")
                
                async def process_batch(inputs):
                    """Process a batch of inputs concurrently"""
                    tasks = [gm.process_player_input_async(inp) for inp in inputs]
                    start_time = time.time()
                    results = await asyncio.gather(*tasks)
                    processing_time = time.time() - start_time
                    return processing_time, results
                
                # Test with increasing batch sizes
                test_inputs = ["test input"] * 10
                
                try:
                    # Run async test
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    batch_time, batch_results = loop.run_until_complete(
                        process_batch(test_inputs)
                    )
                    
                    loop.close()
                    
                    print(f"✅ Processed {len(test_inputs)} inputs concurrently in {batch_time:.3f}s")
                    print(f"📊 Concurrent rate: {len(test_inputs)/batch_time:.1f} inputs/second")
                    
                    self.results['concurrent_processing'] = {
                        'batch_size': len(test_inputs),
                        'batch_time': batch_time,
                        'concurrent_rate': len(test_inputs)/batch_time
                    }
                    
                except Exception as e:
                    print(f"⚠️ Async test failed, falling back to sync: {e}")
                    self.test_sync_batch_processing(gm)
            else:
                print("Async methods not available, testing sync batch processing...")
                self.test_sync_batch_processing(gm)
                
        except Exception as e:
            print(f"❌ Concurrent processing test failed: {e}")
            self.results['concurrent_processing'] = {'error': str(e)}
    
    def test_sync_batch_processing(self, gm):
        """Test synchronous batch processing"""
        test_inputs = ["test sync input"] * 10
        
        start_time = time.time()
        for inp in test_inputs:
            gm.process_player_input(inp)
        sync_time = time.time() - start_time
        
        print(f"✅ Processed {len(test_inputs)} inputs synchronously in {sync_time:.3f}s")
        print(f"📊 Sync rate: {len(test_inputs)/sync_time:.1f} inputs/second")
        
        self.results['concurrent_processing'] = {
            'batch_size': len(test_inputs),
            'sync_time': sync_time,
            'sync_rate': len(test_inputs)/sync_time,
            'method': 'synchronous'
        }
    
    def test_memory_efficiency(self):
        """Test memory usage efficiency"""
        print_section("Memory Efficiency")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Measure initial memory
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create multiple GM instances
            gms = []
            for i in range(5):
                from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
                gm = create_unified_gm(f"benchmark_memory_{i}", f"player_{i}")
                gms.append(gm)
            
            # Measure memory after creation
            after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process some inputs
            for gm in gms:
                for _ in range(10):
                    gm.process_player_input("memory test input")
            
            # Measure memory after processing
            after_processing_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            creation_overhead = after_creation_memory - initial_memory
            processing_overhead = after_processing_memory - after_creation_memory
            
            print(f"📊 Memory Usage:")
            print(f"   Initial:          {initial_memory:.1f} MB")
            print(f"   After creation:   {after_creation_memory:.1f} MB")
            print(f"   After processing: {after_processing_memory:.1f} MB")
            print(f"   Creation overhead: {creation_overhead:.1f} MB")
            print(f"   Processing overhead: {processing_overhead:.1f} MB")
            
            self.results['memory_efficiency'] = {
                'initial_memory': initial_memory,
                'creation_overhead': creation_overhead,
                'processing_overhead': processing_overhead,
                'instances_tested': len(gms)
            }
            
        except ImportError:
            print("⚠️ psutil not available, skipping memory test")
            self.results['memory_efficiency'] = {'error': 'psutil not available'}
        except Exception as e:
            print(f"❌ Memory efficiency test failed: {e}")
            self.results['memory_efficiency'] = {'error': str(e)}
    
    def test_system_stress(self):
        """Test system under stress conditions"""
        print_section("System Stress Test")
        
        try:
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
            
            gm = create_unified_gm("benchmark_stress", "stress_player")
            
            # Stress test parameters
            num_inputs = 100
            stress_inputs = [
                "This is a very long and complex input that should test the system's ability to handle detailed and extensive player commands with lots of descriptive text and multiple actions",
                "look",
                "examine everything in great detail including all the minute aspects",
                "go",
                "cast a very powerful spell with multiple components and effects",
                "short",
                "attack the dragon with my enchanted sword while dodging its fire breath and casting protective spells",
                "hi"
            ]
            
            print(f"Running stress test with {num_inputs} inputs...")
            
            start_time = time.time()
            processing_times = []
            errors = 0
            
            for i in range(num_inputs):
                input_text = stress_inputs[i % len(stress_inputs)]
                
                try:
                    input_start = time.time()
                    result = gm.process_player_input(input_text)
                    input_time = time.time() - input_start
                    processing_times.append(input_time)
                    
                    if i % 20 == 0:
                        print(f"   Progress: {i}/{num_inputs} ({i/num_inputs*100:.1f}%)")
                        
                except Exception as e:
                    errors += 1
                    logger.error(f"Error processing input {i}: {e}")
            
            total_time = time.time() - start_time
            
            if processing_times:
                avg_time = statistics.mean(processing_times)
                throughput = len(processing_times) / total_time
                
                print(f"\n📊 Stress Test Results:")
                print(f"   Total inputs:    {num_inputs}")
                print(f"   Successful:      {len(processing_times)}")
                print(f"   Errors:          {errors}")
                print(f"   Total time:      {total_time:.2f}s")
                print(f"   Average time:    {avg_time:.4f}s")
                print(f"   Throughput:      {throughput:.1f} inputs/second")
                print(f"   Success rate:    {len(processing_times)/num_inputs*100:.1f}%")
                
                self.results['stress_test'] = {
                    'total_inputs': num_inputs,
                    'successful': len(processing_times),
                    'errors': errors,
                    'total_time': total_time,
                    'avg_time': avg_time,
                    'throughput': throughput,
                    'success_rate': len(processing_times)/num_inputs*100
                }
            else:
                print("❌ No successful inputs processed")
                self.results['stress_test'] = {'error': 'No successful processing'}
                
        except Exception as e:
            print(f"❌ Stress test failed: {e}")
            self.results['stress_test'] = {'error': str(e)}
    
    def test_optimization_effectiveness(self):
        """Test effectiveness of optimizations"""
        print_section("Optimization Effectiveness")
        
        try:
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
            
            gm = create_unified_gm("benchmark_optimization", "opt_player")
            
            # Check if optimization methods are available
            optimization_features = []
            
            if hasattr(gm, 'get_performance_report_sync'):
                try:
                    perf_report = gm.get_performance_report_sync()
                    optimization_features.append("Performance reporting")
                    print(f"✅ Performance reporting available")
                except:
                    pass
            elif hasattr(gm, 'get_performance_report'):
                try:
                    # This is async, so we skip it to avoid the coroutine warning
                    optimization_features.append("Performance reporting (async)")
                    print(f"✅ Performance reporting available (async)")
                except:
                    pass
            
            if hasattr(gm, 'get_optimization_status'):
                try:
                    opt_status = gm.get_optimization_status()
                    optimization_features.append("Optimization status")
                    print(f"✅ Optimization status available")
                except:
                    pass
            
            if hasattr(gm, 'adjust_optimization_setting'):
                optimization_features.append("Dynamic optimization adjustment")
                print(f"✅ Dynamic optimization adjustment available")
            
            # Test world reaction optimizations
            if hasattr(gm, 'assess_world_reaction_async'):
                optimization_features.append("Async world reaction assessment")
                print(f"✅ Async world reaction assessment available")
            
            # Check available systems for optimization features
            status = gm.get_system_status()
            optimized_systems = []
            
            for system, available in status['available_systems'].items():
                if available and 'optimized' in system:
                    optimized_systems.append(system)
            
            print(f"\n📊 Optimization Summary:")
            print(f"   Features available: {len(optimization_features)}")
            print(f"   Optimized systems: {len(optimized_systems)}")
            print(f"   Total systems: {len(status['available_systems'])}")
            
            self.results['optimization_effectiveness'] = {
                'features_available': len(optimization_features),
                'optimized_systems': len(optimized_systems),
                'total_systems': len(status['available_systems']),
                'optimization_features': optimization_features,
                'optimized_system_names': optimized_systems
            }
            
        except Exception as e:
            print(f"❌ Optimization effectiveness test failed: {e}")
            self.results['optimization_effectiveness'] = {'error': str(e)}
    
    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""
        print_header("BENCHMARK RESULTS SUMMARY")
        
        print("\n📊 PERFORMANCE METRICS:")
        
        # System initialization
        if 'initialization' in self.results and 'time' in self.results['initialization']:
            init_data = self.results['initialization']
            print(f"   🚀 Initialization: {init_data['time']:.3f}s ({init_data['active_systems']}/{init_data['total_systems']} systems)")
        
        # Basic processing
        if 'basic_processing' in self.results and 'rate' in self.results['basic_processing']:
            proc_data = self.results['basic_processing']
            print(f"   ⚡ Processing rate: {proc_data['rate']:.1f} inputs/second")
            print(f"   ⏱️  Average time: {proc_data['avg_time']:.4f}s")
        
        # Concurrent processing
        if 'concurrent_processing' in self.results:
            conc_data = self.results['concurrent_processing']
            if 'concurrent_rate' in conc_data:
                print(f"   🔄 Concurrent rate: {conc_data['concurrent_rate']:.1f} inputs/second")
            elif 'sync_rate' in conc_data:
                print(f"   🔄 Sync batch rate: {conc_data['sync_rate']:.1f} inputs/second")
        
        # Memory efficiency
        if 'memory_efficiency' in self.results and 'creation_overhead' in self.results['memory_efficiency']:
            mem_data = self.results['memory_efficiency']
            print(f"   💾 Memory overhead: {mem_data['creation_overhead']:.1f} MB/instance")
        
        # Stress test
        if 'stress_test' in self.results and 'success_rate' in self.results['stress_test']:
            stress_data = self.results['stress_test']
            print(f"   💪 Stress test: {stress_data['success_rate']:.1f}% success rate")
            print(f"   🎯 Stress throughput: {stress_data['throughput']:.1f} inputs/second")
        
        # Optimizations
        if 'optimization_effectiveness' in self.results and 'features_available' in self.results['optimization_effectiveness']:
            opt_data = self.results['optimization_effectiveness']
            print(f"   🔧 Optimization features: {opt_data['features_available']}")
            print(f"   ⚙️  Optimized systems: {opt_data['optimized_systems']}/{opt_data['total_systems']}")
        
        print(f"\n🎉 BENCHMARK COMPLETED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Performance rating
        self.calculate_performance_rating()
    
    def calculate_performance_rating(self):
        """Calculate overall performance rating"""
        print("\n🏆 PERFORMANCE RATING:")
        
        score = 0
        max_score = 0
        
        # Initialization speed (max 20 points)
        max_score += 20
        if 'initialization' in self.results and 'time' in self.results['initialization']:
            init_time = self.results['initialization']['time']
            if init_time < 0.1:
                score += 20
            elif init_time < 0.5:
                score += 15
            elif init_time < 1.0:
                score += 10
            else:
                score += 5
        
        # Processing rate (max 25 points)
        max_score += 25
        if 'basic_processing' in self.results and 'rate' in self.results['basic_processing']:
            rate = self.results['basic_processing']['rate']
            if rate > 10000:
                score += 25
            elif rate > 5000:
                score += 20
            elif rate > 1000:
                score += 15
            elif rate > 100:
                score += 10
            else:
                score += 5
        
        # System reliability (max 20 points)
        max_score += 20
        if 'stress_test' in self.results and 'success_rate' in self.results['stress_test']:
            success_rate = self.results['stress_test']['success_rate']
            if success_rate >= 99:
                score += 20
            elif success_rate >= 95:
                score += 15
            elif success_rate >= 90:
                score += 10
            else:
                score += 5
        
        # Optimization features (max 15 points)
        max_score += 15
        if 'optimization_effectiveness' in self.results and 'features_available' in self.results['optimization_effectiveness']:
            features = self.results['optimization_effectiveness']['features_available']
            if features >= 4:
                score += 15
            elif features >= 3:
                score += 12
            elif features >= 2:
                score += 8
            else:
                score += features * 2
        
        # System integration (max 20 points)
        max_score += 20
        if 'initialization' in self.results and 'active_systems' in self.results['initialization']:
            active = self.results['initialization']['active_systems']
            total = self.results['initialization']['total_systems']
            ratio = active / total if total > 0 else 0
            
            if ratio >= 0.75:
                score += 20
            elif ratio >= 0.5:
                score += 15
            elif ratio >= 0.25:
                score += 10
            else:
                score += 5
        
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        print(f"   Overall Score: {score}/{max_score} points ({percentage:.1f}%)")
        
        if percentage >= 90:
            grade = "A+ (Excellent)"
        elif percentage >= 80:
            grade = "A (Very Good)"
        elif percentage >= 70:
            grade = "B (Good)"
        elif percentage >= 60:
            grade = "C (Satisfactory)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"   Performance Grade: {grade}")
        
        return percentage, grade

def main():
    """Run the performance benchmark suite"""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()

if __name__ == "__main__":
    main()
