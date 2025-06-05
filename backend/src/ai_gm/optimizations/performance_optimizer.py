"""
AI GM Performance Optimizer - Advanced async optimization for world reaction system

This module provides comprehensive performance optimizations for the AI GM system,
focusing on async processing, caching, batching, and concurrent execution strategies.
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
from functools import wraps

# Performance metrics tracking
@dataclass
class PerformanceMetrics:
    """Track performance metrics for optimization analysis"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    batch_operations: int = 0
    concurrent_operations: int = 0
    timeout_occurrences: int = 0
    fallback_responses: int = 0
    
    def calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_cache_attempts = self.cache_hits + self.cache_misses
        return (self.cache_hits / total_cache_attempts * 100) if total_cache_attempts > 0 else 0.0
    
    def calculate_success_rate(self) -> float:
        """Calculate request success rate"""
        total_requests = self.successful_requests + self.failed_requests
        return (self.successful_requests / total_requests * 100) if total_requests > 0 else 0.0


@dataclass
class CacheEntry:
    """Cache entry with TTL and metadata"""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.utcnow() > (self.timestamp + timedelta(seconds=self.ttl_seconds))
    
    def access(self) -> Any:
        """Access cache entry and update metadata"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        return self.data


class AsyncBatchProcessor:
    """
    Advanced batching system for LLM API calls with intelligent grouping
    """
    
    def __init__(self, 
                 batch_size: int = 5,
                 batch_timeout: float = 1.0,
                 max_concurrent_batches: int = 3):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_concurrent_batches = max_concurrent_batches
        self.pending_requests = []
        self.batch_semaphore = asyncio.Semaphore(max_concurrent_batches)
        self.logger = logging.getLogger("AsyncBatchProcessor")
        
    async def add_request(self, request_data: Dict[str, Any]) -> Any:
        """Add request to batch processing queue"""
        future = asyncio.Future()
        request_item = {
            'data': request_data,
            'future': future,
            'timestamp': time.time()
        }
        
        self.pending_requests.append(request_item)
        
        # Check if we should process batch immediately
        if len(self.pending_requests) >= self.batch_size:
            asyncio.create_task(self._process_batch())
        else:
            # Schedule timeout processing
            asyncio.create_task(self._schedule_timeout_batch())
        
        return await future
    
    async def _process_batch(self):
        """Process a batch of requests"""
        if not self.pending_requests:
            return
        
        async with self.batch_semaphore:
            # Extract batch from pending requests
            batch = self.pending_requests[:self.batch_size]
            self.pending_requests = self.pending_requests[self.batch_size:]
            
            if not batch:
                return
            
            try:
                # Group similar requests for more efficient processing
                grouped_requests = self._group_similar_requests(batch)
                
                # Process each group
                for group in grouped_requests:
                    results = await self._process_request_group(group)
                    
                    # Resolve futures with results
                    for i, request_item in enumerate(group):
                        if i < len(results):
                            request_item['future'].set_result(results[i])
                        else:
                            request_item['future'].set_exception(
                                Exception("Batch processing failed")
                            )
                            
            except Exception as e:
                self.logger.error(f"Batch processing error: {e}")
                # Resolve all futures with error
                for request_item in batch:
                    if not request_item['future'].done():
                        request_item['future'].set_exception(e)
    
    def _group_similar_requests(self, batch: List[Dict]) -> List[List[Dict]]:
        """Group similar requests for more efficient processing"""
        groups = defaultdict(list)
        
        for request_item in batch:
            # Group by request type and target entity
            request_data = request_item['data']
            group_key = (
                request_data.get('prompt_mode', 'default'),
                request_data.get('target_entity', 'unknown')
            )
            groups[group_key].append(request_item)
        
        return list(groups.values())
    
    async def _process_request_group(self, group: List[Dict]) -> List[Any]:
        """Process a group of similar requests"""
        # This would be implemented to call the actual LLM API
        # For now, we'll simulate the processing
        await asyncio.sleep(0.1)  # Simulate API call
        return [{'result': f'processed_{i}'} for i in range(len(group))]
    
    async def _schedule_timeout_batch(self):
        """Schedule batch processing after timeout"""
        await asyncio.sleep(self.batch_timeout)
        if self.pending_requests:
            asyncio.create_task(self._process_batch())


class IntelligentCache:
    """
    Advanced caching system with TTL, LRU eviction, and smart invalidation
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.logger = logging.getLogger("IntelligentCache")
        
    def _generate_key(self, 
                     player_input: str, 
                     context: Dict[str, Any], 
                     target_entity: str = None) -> str:
        """Generate cache key from input parameters"""
        # Create a normalized representation for caching
        cache_data = {
            'input': player_input.lower().strip(),
            'target': target_entity,
            'player_id': context.get('player_id'),
            'location': context.get('current_location'),
            'reputation_summary': context.get('player_reputation_summary', '')[:100]  # Truncate for key
        }
        
        # Generate hash of the cache data
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired():
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return None
        
        # Update access order (LRU)
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache"""
        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Clean expired entries periodically
        if len(self.cache) % 100 == 0:  # Every 100 insertions
            self._clean_expired()
        
        ttl = ttl or self.default_ttl
        entry = CacheEntry(
            data=value,
            timestamp=datetime.utcnow(),
            ttl_seconds=ttl
        )
        
        self.cache[key] = entry
        
        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order.pop(0)
            if lru_key in self.cache:
                del self.cache[lru_key]
    
    def _clean_expired(self) -> None:
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        keys_to_remove = [
            key for key in self.cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'utilization': len(self.cache) / self.max_size * 100,
            'expired_entries': sum(1 for entry in self.cache.values() if entry.is_expired())
        }


class ConcurrentProcessingManager:
    """
    Manager for concurrent processing of multiple world reactions
    """
    
    def __init__(self, max_concurrent: int = 5, timeout: float = 3.0):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.logger = logging.getLogger("ConcurrentProcessingManager")
        
    async def process_multiple_reactions(self, 
                                       requests: List[Dict[str, Any]],
                                       processor_func: Callable) -> List[Dict[str, Any]]:
        """
        Process multiple reaction requests concurrently
        
        Args:
            requests: List of request dictionaries
            processor_func: Async function to process individual requests
            
        Returns:
            List of results (includes successful results and fallbacks for failures)
        """
        if not requests:
            return []
        
        # Create semaphore-limited tasks
        async def process_with_semaphore(request):
            async with self.semaphore:
                try:
                    return await asyncio.wait_for(
                        processor_func(request),
                        timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout processing request: {request.get('target_entity', 'unknown')}")
                    return self._create_timeout_fallback(request)
                except Exception as e:
                    self.logger.error(f"Error processing request: {e}")
                    return self._create_error_fallback(request, str(e))
        
        # Execute all tasks concurrently
        tasks = [process_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that weren't caught
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(self._create_error_fallback(requests[i], str(result)))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _create_timeout_fallback(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback response for timeout"""
        return {
            'success': False,
            'target_entity': request.get('target_entity', 'unknown'),
            'reaction_data': {
                'perception_summary': 'No immediate reaction observed.',
                'suggested_reactive_dialogue_or_narration': 'The situation continues normally.',
                'subtle_attitude_shift_description': None
            },
            'fallback_reason': 'timeout',
            'assessment_time': self.timeout
        }
    
    def _create_error_fallback(self, request: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create fallback response for errors"""
        return {
            'success': False,
            'target_entity': request.get('target_entity', 'unknown'),
            'reaction_data': {
                'perception_summary': 'Unable to assess reaction at this time.',
                'suggested_reactive_dialogue_or_narration': 'The area remains quiet.',
                'subtle_attitude_shift_description': None
            },
            'fallback_reason': f'error: {error}',
            'assessment_time': 0.0
        }


class PerformanceOptimizer:
    """
    Main performance optimization coordinator for the AI GM system
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics = PerformanceMetrics()
        self.cache = IntelligentCache(
            max_size=self.config.get('cache_max_size', 1000),
            default_ttl=self.config.get('cache_default_ttl', 300)
        )
        self.batch_processor = AsyncBatchProcessor(
            batch_size=self.config.get('batch_size', 5),
            batch_timeout=self.config.get('batch_timeout', 1.0),
            max_concurrent_batches=self.config.get('max_concurrent_batches', 3)
        )
        self.concurrent_manager = ConcurrentProcessingManager(
            max_concurrent=self.config.get('max_concurrent', 5),
            timeout=self.config.get('request_timeout', 3.0)
        )
        self.logger = logging.getLogger("PerformanceOptimizer")
        
        # Performance monitoring
        self.start_time = time.time()
        self.last_metrics_log = time.time()
        self.metrics_log_interval = 60.0  # Log metrics every minute
        
    async def optimized_world_reaction_assessment(self,
                                                player_input: str,
                                                context: Dict[str, Any],
                                                target_entities: List[str] = None,
                                                processor_func: Callable = None) -> List[Dict[str, Any]]:
        """
        Perform optimized world reaction assessment with caching, batching, and concurrency
        
        Args:
            player_input: Player's input
            context: Game context
            target_entities: List of entities to assess (NPCs, environment, etc.)
            processor_func: Function to process individual reactions
            
        Returns:
            List of reaction assessment results
        """
        start_time = time.time()
        
        # Determine target entities if not provided
        if not target_entities:
            target_entities = self._determine_target_entities(context)
        
        if not target_entities:
            self.logger.warning("No target entities found for reaction assessment")
            return []
        
        # Check cache for each entity
        cached_results = []
        uncached_requests = []
        
        for target_entity in target_entities:
            cache_key = self.cache._generate_key(player_input, context, target_entity)
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                self.metrics.cache_hits += 1
                cached_results.append(cached_result)
            else:
                self.metrics.cache_misses += 1
                uncached_requests.append({
                    'player_input': player_input,
                    'context': context,
                    'target_entity': target_entity,
                    'cache_key': cache_key
                })
        
        # Process uncached requests concurrently if we have a processor function
        if uncached_requests and processor_func:
            self.metrics.concurrent_operations += 1
            new_results = await self.concurrent_manager.process_multiple_reactions(
                uncached_requests, processor_func
            )
            
            # Cache successful results
            for i, result in enumerate(new_results):
                if result.get('success', False):
                    cache_key = uncached_requests[i]['cache_key']
                    # Cache for varying durations based on result quality
                    ttl = self._calculate_cache_ttl(result)
                    self.cache.set(cache_key, result, ttl)
                    self.metrics.successful_requests += 1
                else:
                    self.metrics.failed_requests += 1
            
            # Combine cached and new results
            all_results = cached_results + new_results
        else:
            all_results = cached_results
        
        # Update performance metrics
        processing_time = time.time() - start_time
        self.metrics.total_requests += 1
        
        # Update average response time
        if self.metrics.total_requests == 1:
            self.metrics.avg_response_time = processing_time
        else:
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (self.metrics.total_requests - 1) + processing_time) /
                self.metrics.total_requests
            )
        
        # Log metrics periodically
        if time.time() - self.last_metrics_log > self.metrics_log_interval:
            self._log_performance_metrics()
            self.last_metrics_log = time.time()
        
        return all_results
    
    def _determine_target_entities(self, context: Dict[str, Any]) -> List[str]:
        """Determine target entities for reaction assessment"""
        entities = []
        
        # Add NPCs
        active_npcs = context.get('active_npcs', [])
        present_npcs = context.get('present_npcs', [])
        all_npcs = list(set(active_npcs + present_npcs))
        entities.extend([f"npc_{npc}" for npc in all_npcs[:3]])  # Limit to 3 NPCs
        
        # Add environment
        current_location = context.get('current_location')
        if current_location:
            entities.append(f"environment_{current_location}")
        
        # Add factions if relevant
        active_factions = context.get('active_factions', [])
        entities.extend([f"faction_{faction}" for faction in active_factions[:2]])  # Limit to 2 factions
        
        return entities
    
    def _calculate_cache_ttl(self, result: Dict[str, Any]) -> int:
        """Calculate appropriate cache TTL based on result quality"""
        base_ttl = 300  # 5 minutes default
        
        # Longer cache for successful results
        if result.get('success', False):
            base_ttl *= 2
        
        # Shorter cache for fallback responses
        if result.get('fallback_reason'):
            base_ttl = 60  # 1 minute for fallbacks
        
        # Adjust based on processing time (slower calls cached longer)
        processing_time = result.get('assessment_time', 0)
        if processing_time > 2.0:  # Slow calls
            base_ttl *= 1.5
        
        return int(base_ttl)
    
    def _log_performance_metrics(self) -> None:
        """Log current performance metrics"""
        uptime = time.time() - self.start_time
        cache_stats = self.cache.get_stats()
        
        self.logger.info(
            f"Performance Metrics - "
            f"Uptime: {uptime:.1f}s, "
            f"Total Requests: {self.metrics.total_requests}, "
            f"Success Rate: {self.metrics.calculate_success_rate():.1f}%, "
            f"Avg Response Time: {self.metrics.avg_response_time:.3f}s, "
            f"Cache Hit Rate: {self.metrics.calculate_hit_rate():.1f}%, "
            f"Cache Utilization: {cache_stats['utilization']:.1f}%, "
            f"Concurrent Ops: {self.metrics.concurrent_operations}, "
            f"Batch Ops: {self.metrics.batch_operations}"
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        uptime = time.time() - self.start_time
        cache_stats = self.cache.get_stats()
        
        return {
            'uptime_seconds': uptime,
            'metrics': {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'success_rate_percent': self.metrics.calculate_success_rate(),
                'avg_response_time_seconds': self.metrics.avg_response_time,
                'cache_hits': self.metrics.cache_hits,
                'cache_misses': self.metrics.cache_misses,
                'cache_hit_rate_percent': self.metrics.calculate_hit_rate(),
                'concurrent_operations': self.metrics.concurrent_operations,
                'batch_operations': self.metrics.batch_operations,
                'timeout_occurrences': self.metrics.timeout_occurrences,
                'fallback_responses': self.metrics.fallback_responses
            },
            'cache_stats': cache_stats,
            'optimization_recommendations': self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on current metrics"""
        recommendations = []
        
        # Cache optimization
        hit_rate = self.metrics.calculate_hit_rate()
        if hit_rate < 30:
            recommendations.append("Consider increasing cache TTL or improving cache key generation")
        elif hit_rate > 80:
            recommendations.append("Cache is performing well, consider increasing cache size")
        
        # Response time optimization
        if self.metrics.avg_response_time > 2.0:
            recommendations.append("Average response time is high, consider increasing concurrency limits")
        
        # Success rate optimization
        success_rate = self.metrics.calculate_success_rate()
        if success_rate < 90:
            recommendations.append("Low success rate detected, check error handling and timeouts")
        
        # Concurrent processing optimization
        if self.metrics.concurrent_operations > self.metrics.total_requests * 0.5:
            recommendations.append("High concurrent processing usage, system is well optimized")
        else:
            recommendations.append("Consider using more concurrent processing for better performance")
        
        return recommendations


# Decorator for performance monitoring
def monitor_performance(optimizer: PerformanceOptimizer):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                optimizer.metrics.successful_requests += 1
                return result
            except Exception as e:
                optimizer.metrics.failed_requests += 1
                raise
            finally:
                processing_time = time.time() - start_time
                # Update average response time
                if optimizer.metrics.total_requests == 0:
                    optimizer.metrics.avg_response_time = processing_time
                else:
                    optimizer.metrics.avg_response_time = (
                        (optimizer.metrics.avg_response_time * optimizer.metrics.total_requests + processing_time) /
                        (optimizer.metrics.total_requests + 1)
                    )
                optimizer.metrics.total_requests += 1
        
        return wrapper
    return decorator
