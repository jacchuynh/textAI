"""
Magic System Redis Caching Layer
High-performance caching strategies for magic system operations
"""

import redis
import json
import pickle
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class MagicCache:
    """
    Intelligent caching layer for magic system operations
    Implements various caching strategies for different data types
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db, 
            decode_responses=False,  # Keep as bytes for pickle support
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Cache TTL settings for different data types
        self.cache_ttl = {
            'player_mana': 300,          # 5 minutes - frequently changing
            'player_state': 600,         # 10 minutes - moderately changing
            'spell_data': 3600,          # 1 hour - rarely changing
            'leyline_strength': 1800,    # 30 minutes - environmental data
            'corruption_state': 600,     # 10 minutes - important for consistency
            'spell_cooldowns': 300,      # 5 minutes - time-sensitive
            'magic_statistics': 7200,    # 2 hours - analytical data
            'spell_combinations': 1800,  # 30 minutes - computed recommendations
            'environmental_bonuses': 900, # 15 minutes - location-based data
            'ritual_progress': 60,       # 1 minute - real-time ritual state
        }
        
        # Key prefixes for organization
        self.key_prefixes = {
            'player': 'magic:player:',
            'spell': 'magic:spell:',
            'leyline': 'magic:leyline:',
            'region': 'magic:region:',
            'session': 'magic:session:',
            'computed': 'magic:computed:',
            'statistics': 'magic:stats:',
            'temporary': 'magic:temp:',
        }
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """Generate a consistent cache key"""
        key_parts = [str(arg) for arg in args]
        return f"{self.key_prefixes[prefix]}{'_'.join(key_parts)}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        if isinstance(data, (str, int, float, bool)):
            return json.dumps(data).encode('utf-8')
        else:
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis"""
        try:
            # Try JSON first (faster)
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    # Player State Caching
    def cache_player_mana(self, player_id: str, mana_data: Dict[str, float]):
        """Cache player's current mana state"""
        key = self._generate_cache_key('player', player_id, 'mana')
        self.redis_client.setex(
            key, 
            self.cache_ttl['player_mana'], 
            self._serialize_data(mana_data)
        )
    
    def get_player_mana(self, player_id: str) -> Optional[Dict[str, float]]:
        """Get cached player mana state"""
        key = self._generate_cache_key('player', player_id, 'mana')
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    def cache_player_full_state(self, player_id: str, state_data: Dict[str, Any]):
        """Cache complete player magic state"""
        key = self._generate_cache_key('player', player_id, 'state')
        self.redis_client.setex(
            key,
            self.cache_ttl['player_state'],
            self._serialize_data(state_data)
        )
    
    def get_player_full_state(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get cached complete player magic state"""
        key = self._generate_cache_key('player', player_id, 'state')
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    # Spell Caching
    def cache_spell_data(self, spell_id: str, spell_data: Dict[str, Any]):
        """Cache spell template data"""
        key = self._generate_cache_key('spell', spell_id, 'data')
        self.redis_client.setex(
            key,
            self.cache_ttl['spell_data'],
            self._serialize_data(spell_data)
        )
    
    def get_spell_data(self, spell_id: str) -> Optional[Dict[str, Any]]:
        """Get cached spell data"""
        key = self._generate_cache_key('spell', spell_id, 'data')
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    def cache_spell_result(self, player_id: str, spell_id: str, context_hash: str, result: Dict[str, Any]):
        """Cache computed spell result for specific context"""
        key = self._generate_cache_key('computed', 'spell_result', player_id, spell_id, context_hash)
        # Shorter TTL for computed results
        self.redis_client.setex(key, 1800, self._serialize_data(result))
    
    def get_spell_result(self, player_id: str, spell_id: str, context_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached spell result"""
        key = self._generate_cache_key('computed', 'spell_result', player_id, spell_id, context_hash)
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    # Leyline and Environmental Caching
    def cache_leyline_strength(self, region_id: str, leyline_data: Dict[str, Any]):
        """Cache leyline strength data for a region"""
        key = self._generate_cache_key('leyline', region_id, 'strength')
        self.redis_client.setex(
            key,
            self.cache_ttl['leyline_strength'],
            self._serialize_data(leyline_data)
        )
    
    def get_leyline_strength(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get cached leyline strength data"""
        key = self._generate_cache_key('leyline', region_id, 'strength')
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    def cache_environmental_bonus(self, location_hash: str, bonus_data: Dict[str, float]):
        """Cache environmental magic bonuses for a location"""
        key = self._generate_cache_key('computed', 'env_bonus', location_hash)
        self.redis_client.setex(
            key,
            self.cache_ttl['environmental_bonuses'],
            self._serialize_data(bonus_data)
        )
    
    def get_environmental_bonus(self, location_hash: str) -> Optional[Dict[str, float]]:
        """Get cached environmental bonus"""
        key = self._generate_cache_key('computed', 'env_bonus', location_hash)
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    # Session and Temporary Data
    def cache_spell_preparation(self, player_id: str, prep_data: Dict[str, Any]):
        """Cache spell preparation state (temporary)"""
        key = self._generate_cache_key('session', player_id, 'spell_prep')
        self.redis_client.setex(key, 1800, self._serialize_data(prep_data))  # 30 minutes
    
    def get_spell_preparation(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get cached spell preparation state"""
        key = self._generate_cache_key('session', player_id, 'spell_prep')
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    def cache_active_enchantments(self, player_id: str, enchantments: List[Dict[str, Any]]):
        """Cache active enchantments using Redis sets for efficient operations"""
        key = self._generate_cache_key('player', player_id, 'enchantments')
        
        # Clear existing enchantments
        self.redis_client.delete(key)
        
        # Add each enchantment with expiration
        for enchantment in enchantments:
            enchantment_data = self._serialize_data(enchantment)
            self.redis_client.sadd(key, enchantment_data)
        
        # Set expiration on the whole set
        self.redis_client.expire(key, self.cache_ttl['player_state'])
    
    def get_active_enchantments(self, player_id: str) -> List[Dict[str, Any]]:
        """Get active enchantments from cache"""
        key = self._generate_cache_key('player', player_id, 'enchantments')
        cached_enchantments = self.redis_client.smembers(key)
        
        if cached_enchantments:
            return [self._deserialize_data(enc) for enc in cached_enchantments]
        return []
    
    def add_active_enchantment(self, player_id: str, enchantment: Dict[str, Any]):
        """Add a single enchantment to the active set"""
        key = self._generate_cache_key('player', player_id, 'enchantments')
        enchantment_data = self._serialize_data(enchantment)
        self.redis_client.sadd(key, enchantment_data)
        self.redis_client.expire(key, self.cache_ttl['player_state'])
    
    def remove_active_enchantment(self, player_id: str, enchantment: Dict[str, Any]):
        """Remove a specific enchantment from the active set"""
        key = self._generate_cache_key('player', player_id, 'enchantments')
        enchantment_data = self._serialize_data(enchantment)
        self.redis_client.srem(key, enchantment_data)
    
    # Cooldown Management
    def set_spell_cooldown(self, player_id: str, spell_id: str, cooldown_seconds: int):
        """Set a spell cooldown using Redis TTL"""
        key = self._generate_cache_key('player', player_id, 'cooldown', spell_id)
        self.redis_client.setex(key, cooldown_seconds, 'cooling_down')
    
    def check_spell_cooldown(self, player_id: str, spell_id: str) -> bool:
        """Check if a spell is on cooldown (True = on cooldown)"""
        key = self._generate_cache_key('player', player_id, 'cooldown', spell_id)
        return self.redis_client.exists(key) > 0
    
    def get_remaining_cooldown(self, player_id: str, spell_id: str) -> int:
        """Get remaining cooldown time in seconds"""
        key = self._generate_cache_key('player', player_id, 'cooldown', spell_id)
        ttl = self.redis_client.ttl(key)
        return max(0, ttl) if ttl >= 0 else 0
    
    # Statistics and Analytics Caching
    def cache_magic_statistics(self, stat_type: str, stat_data: Dict[str, Any]):
        """Cache computed magic statistics"""
        key = self._generate_cache_key('statistics', stat_type)
        self.redis_client.setex(
            key,
            self.cache_ttl['magic_statistics'],
            self._serialize_data(stat_data)
        )
    
    def get_magic_statistics(self, stat_type: str) -> Optional[Dict[str, Any]]:
        """Get cached magic statistics"""
        key = self._generate_cache_key('statistics', stat_type)
        cached_data = self.redis_client.get(key)
        return self._deserialize_data(cached_data) if cached_data else None
    
    # Cache Invalidation
    def invalidate_player_cache(self, player_id: str):
        """Invalidate all cache entries for a player"""
        pattern = self._generate_cache_key('player', player_id, '*')
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def invalidate_spell_cache(self, spell_id: str):
        """Invalidate all cache entries for a spell"""
        pattern = self._generate_cache_key('spell', spell_id, '*')
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def invalidate_region_cache(self, region_id: str):
        """Invalidate all cache entries for a region"""
        patterns = [
            self._generate_cache_key('leyline', region_id, '*'),
            self._generate_cache_key('region', region_id, '*')
        ]
        
        for pattern in patterns:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
    
    # Batch Operations
    def cache_multiple_player_states(self, player_states: Dict[str, Dict[str, Any]]):
        """Cache multiple player states efficiently using pipeline"""
        pipe = self.redis_client.pipeline()
        
        for player_id, state_data in player_states.items():
            key = self._generate_cache_key('player', player_id, 'state')
            pipe.setex(key, self.cache_ttl['player_state'], self._serialize_data(state_data))
        
        pipe.execute()
    
    def get_multiple_player_states(self, player_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get multiple player states efficiently using pipeline"""
        pipe = self.redis_client.pipeline()
        
        keys = [self._generate_cache_key('player', player_id, 'state') for player_id in player_ids]
        for key in keys:
            pipe.get(key)
        
        results = pipe.execute()
        
        player_states = {}
        for player_id, cached_data in zip(player_ids, results):
            player_states[player_id] = self._deserialize_data(cached_data) if cached_data else None
        
        return player_states
    
    # Context-Sensitive Caching
    def generate_context_hash(self, context: Dict[str, Any]) -> str:
        """Generate a hash for context-dependent caching"""
        # Sort keys for consistent hashing
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    # Cache Warming
    def warm_player_cache(self, player_id: str, player_data: Dict[str, Any]):
        """Pre-populate cache with essential player data"""
        # Cache different aspects of player data
        self.cache_player_full_state(player_id, player_data)
        
        if 'mana' in player_data:
            self.cache_player_mana(player_id, player_data['mana'])
        
        if 'enchantments' in player_data:
            self.cache_active_enchantments(player_id, player_data['enchantments'])
    
    # Health and Monitoring
    def get_cache_health(self) -> Dict[str, Any]:
        """Get cache health metrics"""
        info = self.redis_client.info()
        
        return {
            'connected': True,
            'used_memory': info.get('used_memory_human', 'Unknown'),
            'connected_clients': info.get('connected_clients', 0),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'hit_rate': (
                info.get('keyspace_hits', 0) / 
                max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
            ) * 100
        }
    
    def clear_all_magic_cache(self):
        """Clear all magic-related cache entries (use with caution)"""
        for prefix in self.key_prefixes.values():
            pattern = f"{prefix}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        
        logger.warning("All magic cache cleared")

# Decorator for automatic caching
def cache_magic_result(cache_key_func, ttl=3600, cache_instance=None):
    """
    Decorator for automatic caching of function results
    
    Args:
        cache_key_func: Function that generates cache key from args
        ttl: Time to live in seconds
        cache_instance: MagicCache instance to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = cache_instance or MagicCache()
            
            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.redis_client.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cache._deserialize_data(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.redis_client.setex(cache_key, ttl, cache._serialize_data(result))
            
            logger.debug(f"Cache miss for {func.__name__}: {cache_key}")
            return result
        
        return wrapper
    return decorator

# Specialized cache managers
class RealTimeMagicCache:
    """Specialized cache for real-time magic events"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def publish_magic_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish real-time magic event"""
        channel = f"magic_events:{event_type}"
        message = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.redis.publish(channel, json.dumps(message))
    
    def subscribe_to_magic_events(self, event_types: List[str]):
        """Subscribe to specific magic event types"""
        pubsub = self.redis.pubsub()
        for event_type in event_types:
            pubsub.subscribe(f"magic_events:{event_type}")
        return pubsub
    
    def cache_ritual_progress(self, ritual_id: str, progress_data: Dict[str, Any]):
        """Cache ritual progress for real-time updates"""
        key = f"ritual_progress:{ritual_id}"
        self.redis.setex(key, 3600, json.dumps(progress_data))  # 1 hour TTL
    
    def get_ritual_progress(self, ritual_id: str) -> Optional[Dict[str, Any]]:
        """Get current ritual progress"""
        key = f"ritual_progress:{ritual_id}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

# Global cache instance
magic_cache = MagicCache()

# Helper functions for easy integration
def get_cached_or_compute(cache_key: str, compute_func, ttl: int = 3600, *args, **kwargs):
    """Get from cache or compute and cache the result"""
    cached_result = magic_cache.redis_client.get(cache_key)
    
    if cached_result:
        return magic_cache._deserialize_data(cached_result)
    
    # Compute result
    result = compute_func(*args, **kwargs)
    
    # Cache result
    magic_cache.redis_client.setex(cache_key, ttl, magic_cache._serialize_data(result))
    
    return result

def invalidate_related_caches(player_id: str = None, spell_id: str = None, region_id: str = None):
    """Convenience function to invalidate related caches"""
    if player_id:
        magic_cache.invalidate_player_cache(player_id)
    
    if spell_id:
        magic_cache.invalidate_spell_cache(spell_id)
    
    if region_id:
        magic_cache.invalidate_region_cache(region_id)
