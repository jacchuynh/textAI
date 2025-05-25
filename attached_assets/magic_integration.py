"""
Magic System Integration Layer
Seamlessly integrates enhanced backend with your existing magic system
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from contextlib import contextmanager

from app.tasks.magic_tasks import (
    process_spell_cast, calculate_spell_success_rate, regenerate_mana,
    update_leyline_strengths, queue_spell_processing, queue_batch_mana_regeneration
)
from app.vector.magic_vectors import (
    MagicVectorDatabase, get_spell_recommendations, find_similar_spells_for_learning
)
from app.magic_cache import MagicCache, magic_cache, get_cached_or_compute
from app.db.magic_models import MagicEvent, PlayerMagicState, SpellTemplate, LeylineNode
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

class EnhancedMagicSystem:
    """
    Enhanced magic system that integrates with your existing magic_system.py
    Provides high-performance backend operations while maintaining compatibility
    """
    
    def __init__(self):
        self.cache = MagicCache()
        self.vector_db = MagicVectorDatabase()
        
        # Performance tracking
        self.performance_metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'db_queries': 0,
            'async_tasks_queued': 0
        }
    
    @contextmanager
    def get_db_session(self):
        """Database session context manager"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def integrate_with_existing_spell_cast(self, player_id: str, spell_data: Dict[str, Any], 
                                         existing_magic_system) -> Dict[str, Any]:
        """
        Integrate with your existing spell casting system
        Adds caching, async processing, and intelligence while preserving existing logic
        """
        
        # Generate context hash for caching
        context_hash = self.cache.generate_context_hash({
            'location': spell_data.get('location', {}),
            'time_of_day': spell_data.get('time_of_day', 'day'),
            'weather': spell_data.get('weather', 'clear'),
            'domain_id': spell_data.get('domain_id')
        })
        
        # Check cache first
        cached_result = self.cache.get_spell_result(player_id, spell_data['spell_id'], context_hash)
        if cached_result and spell_data.get('allow_cache', True):
            self.performance_metrics['cache_hits'] += 1
            logger.info(f"Using cached spell result for {player_id}")
            return cached_result
        
        self.performance_metrics['cache_misses'] += 1
        
        # Get enhanced player state (cached)
        player_state = self.get_enhanced_player_state(player_id)
        if not player_state:
            return {"success": False, "reason": "Player not found"}
        
        # Check mana with cache
        if player_state['current_mana'] < spell_data.get('mana_cost', 0):
            return {"success": False, "reason": "Insufficient mana"}
        
        # Get spell template with caching
        spell_template = self.get_cached_spell_template(spell_data['spell_id'])
        if not spell_template:
            return {"success": False, "reason": "Spell not found"}
        
        # Queue async processing for complex calculations
        if spell_data.get('complex_calculation', False):
            # Use async processing for heavy computations
            task_result = queue_spell_processing(player_id, spell_data, priority='high')
            self.performance_metrics['async_tasks_queued'] += 1
            
            # Return immediate result with task ID for status checking
            return {
                "success": True,
                "processing": True,
                "task_id": task_result.id,
                "estimated_completion": datetime.utcnow() + timedelta(seconds=5)
            }
        
        # For simple spells, use existing system with enhancements
        try:
            # Calculate success rate with environmental factors
            environmental_bonus = self.get_environmental_magic_bonus(spell_data.get('location', {}))
            base_success_rate = existing_magic_system.calculate_spell_success(player_id, spell_data)
            enhanced_success_rate = min(0.95, base_success_rate + environmental_bonus)
            
            # Use existing spell casting logic
            spell_result = existing_magic_system.cast_spell(
                player_id, 
                spell_data, 
                success_rate_override=enhanced_success_rate
            )
            
            # Enhance result with additional data
            spell_result.update({
                "environmental_bonus": environmental_bonus,
                "cache_used": False,
                "processing_time": 0.1,  # Estimate
                "leyline_influence": self.get_leyline_influence(spell_data.get('location', {}))
            })
            
            # Cache successful results
            if spell_result.get("success", False):
                self.cache.cache_spell_result(player_id, spell_data['spell_id'], context_hash, spell_result)
            
            # Update player state cache
            self.update_player_state_cache(player_id, spell_result)
            
            # Queue analytics update
            self.queue_spell_analytics_update(player_id, spell_data, spell_result)
            
            return spell_result
            
        except Exception as e:
            logger.error(f"Enhanced spell casting failed for {player_id}: {e}")
            # Fallback to existing system
            return existing_magic_system.cast_spell(player_id, spell_data)
    
    def get_enhanced_player_state(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get player magic state with intelligent caching
        Falls back to database if cache miss
        """
        
        # Try cache first
        cached_state = self.cache.get_player_full_state(player_id)
        if cached_state:
            self.performance_metrics['cache_hits'] += 1
            return cached_state
        
        self.performance_metrics['cache_misses'] += 1
        self.performance_metrics['db_queries'] += 1
        
        # Load from database
        with self.get_db_session() as session:
            player_state = session.query(PlayerMagicState).filter_by(player_id=player_id).first()
            
            if not player_state:
                return None
            
            # Convert to dict and cache
            state_dict = {
                'player_id': str(player_state.player_id),
                'current_mana': player_state.current_mana,
                'max_mana': player_state.max_mana,
                'mana_regen_rate': player_state.mana_regen_rate,
                'arcane_mastery': player_state.arcane_mastery,
                'mana_infusion': player_state.mana_infusion,
                'spiritual_utility': player_state.spiritual_utility,
                'corruption_level': player_state.corruption_level,
                'corruption_resistance': player_state.corruption_resistance,
                'active_enchantments': player_state.active_enchantments or [],
                'active_buffs': player_state.active_buffs or {},
                'spell_cooldowns': player_state.spell_cooldowns or {},
                'last_mana_update': player_state.last_mana_update.isoformat() if player_state.last_mana_update else None,
                'last_corruption_check': player_state.last_corruption_check.isoformat() if player_state.last_corruption_check else None
            }
            
            # Cache the state
            self.cache.cache_player_full_state(player_id, state_dict)
            return state_dict
    
    def get_cached_spell_template(self, spell_id: str) -> Optional[Dict[str, Any]]:
        """Get spell template with caching"""
        
        cached_spell = self.cache.get_spell_data(spell_id)
        if cached_spell:
            self.performance_metrics['cache_hits'] += 1
            return cached_spell
        
        self.performance_metrics['cache_misses'] += 1
        self.performance_metrics['db_queries'] += 1
        
        with self.get_db_session() as session:
            spell_template = session.query(SpellTemplate).filter_by(id=spell_id).first()
            
            if not spell_template:
                return None
            
            spell_dict = {
                'id': spell_template.id,
                'name': spell_template.name,
                'tier': spell_template.tier,
                'magic_type': spell_template.magic_type,
                'mana_cost': spell_template.mana_cost,
                'min_mastery_level': spell_template.min_mastery_level,
                'components': spell_template.components or [],
                'cast_time': spell_template.cast_time,
                'effects': spell_template.effects or {},
                'avg_success_rate': spell_template.avg_success_rate,
                'usage_count': spell_template.usage_count,
                'feature_vector': spell_template.feature_vector
            }
            
            self.cache.cache_spell_data(spell_id, spell_dict)
            return spell_dict
    
    def get_environmental_magic_bonus(self, location: Dict[str, Any]) -> float:
        """Get environmental magic bonus with caching"""
        
        location_hash = self.cache.generate_context_hash(location)
        cached_bonus = self.cache.get_environmental_bonus(location_hash)
        
        if cached_bonus:
            self.performance_metrics['cache_hits'] += 1
            return cached_bonus.get('total_bonus', 0.0)
        
        self.performance_metrics['cache_misses'] += 1
        
        # Calculate environmental bonus
        def compute_bonus():
            bonus = 0.0
            
            # Leyline proximity bonus
            leyline_bonus = self.get_leyline_influence(location)
            bonus += leyline_bonus
            
            # Time of day bonus
            time_bonus = self.calculate_time_bonus(location.get('time_of_day', 'day'))
            bonus += time_bonus
            
            # Weather bonus
            weather_bonus = self.calculate_weather_bonus(location.get('weather', 'clear'))
            bonus += weather_bonus
            
            return {
                'total_bonus': bonus,
                'leyline_bonus': leyline_bonus,
                'time_bonus': time_bonus,
                'weather_bonus': weather_bonus
            }
        
        bonus_data = get_cached_or_compute(
            f"env_bonus_{location_hash}",
            compute_bonus,
            ttl=900  # 15 minutes
        )
        
        self.cache.cache_environmental_bonus(location_hash, bonus_data)
        return bonus_data['total_bonus']
    
    def get_leyline_influence(self, location: Dict[str, Any]) -> float:
        """Calculate leyline influence on magic at location"""
        
        x, y = location.get('x', 0), location.get('y', 0)
        region_id = location.get('region_id', 'default')
        
        # Check cache
        location_key = f"leyline_influence_{region_id}_{x}_{y}"
        cached_influence = get_cached_or_compute(
            location_key,
            lambda: self._calculate_leyline_influence(x, y, region_id),
            ttl=1800  # 30 minutes
        )
        
        return cached_influence
    
    def _calculate_leyline_influence(self, x: float, y: float, region_id: str) -> float:
        """Internal leyline influence calculation"""
        
        with self.get_db_session() as session:
            nearby_nodes = session.query(LeylineNode).filter(
                LeylineNode.region_id == region_id,
                ((LeylineNode.x_coordinate - x) ** 2 + (LeylineNode.y_coordinate - y) ** 2) < 10000  # 100 unit radius
            ).all()
            
            total_influence = 0.0
            for node in nearby_nodes:
                distance = ((node.x_coordinate - x) ** 2 + (node.y_coordinate - y) ** 2) ** 0.5
                distance_factor = max(0, 1 - distance / 100)  # Linear falloff
                influence = node.strength * distance_factor * 0.1
                total_influence += influence
            
            return min(0.3, total_influence)  # Cap at 30% bonus
    
    def calculate_time_bonus(self, time_of_day: str) -> float:
        """Calculate time-based magic bonus"""
        time_bonuses = {
            'dawn': 0.05,
            'day': 0.0,
            'dusk': 0.05,
            'night': 0.1,
            'midnight': 0.15
        }
        return time_bonuses.get(time_of_day, 0.0)
    
    def calculate_weather_bonus(self, weather: str) -> float:
        """Calculate weather-based magic bonus"""
        weather_bonuses = {
            'clear': 0.0,
            'cloudy': 0.02,
            'rain': 0.05,
            'storm': 0.1,
            'snow': 0.03,
            'fog': 0.08
        }
        return weather_bonuses.get(weather, 0.0)
    
    def update_player_state_cache(self, player_id: str, spell_result: Dict[str, Any]):
        """Update player state cache after spell casting"""
        
        current_state = self.cache.get_player_full_state(player_id)
        if current_state and spell_result.get('success', False):
            # Update mana
            mana_used = spell_result.get('mana_used', 0)
            current_state['current_mana'] = max(0, current_state['current_mana'] - mana_used)
            
            # Update cooldowns if any
            if spell_result.get('cooldown_time', 0) > 0:
                self.cache.set_spell_cooldown(
                    player_id, 
                    spell_result.get('spell_id'), 
                    spell_result['cooldown_time']
                )
            
            # Update corruption if changed
            if 'corruption_change' in spell_result:
                current_state['corruption_level'] += spell_result['corruption_change']
                current_state['corruption_level'] = max(0, min(100, current_state['corruption_level']))
            
            # Re-cache updated state
            self.cache.cache_player_full_state(player_id, current_state)
    
    def queue_spell_analytics_update(self, player_id: str, spell_data: Dict[str, Any], 
                                   spell_result: Dict[str, Any]):
        """Queue analytics update for spell usage"""
        
        analytics_data = {
            'player_id': player_id,
            'spell_id': spell_data.get('spell_id'),
            'success': spell_result.get('success', False),
            'mana_used': spell_result.get('mana_used', 0),
            'environmental_bonus': spell_result.get('environmental_bonus', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Queue async analytics processing
        from app.tasks.magic_tasks import update_spell_statistics
        update_spell_statistics.delay(spell_data.get('spell_id'), spell_result.get('success', False))
        
        self.performance_metrics['async_tasks_queued'] += 1
    
    def get_intelligent_spell_recommendations(self, player_id: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get AI-powered spell recommendations"""
        
        cache_key = f"spell_recommendations_{player_id}_{self.cache.generate_context_hash(context or {})}"
        
        cached_recommendations = get_cached_or_compute(
            cache_key,
            lambda: get_spell_recommendations(player_id, context),
            ttl=1800  # 30 minutes
        )
        
        return cached_recommendations
    
    def find_spell_learning_path(self, player_id: str, target_spell_id: str) -> List[Dict[str, Any]]:
        """Find optimal learning path to a target spell"""
        
        player_state = self.get_enhanced_player_state(player_id)
        if not player_state:
            return []
        
        mastery_levels = {
            'arcane': player_state['arcane_mastery'],
            'mana': player_state['mana_infusion'],
            'spiritual': player_state['spiritual_utility']
        }
        
        cache_key = f"learning_path_{player_id}_{target_spell_id}_{hash(str(mastery_levels))}"
        
        learning_path = get_cached_or_compute(
            cache_key,
            lambda: find_similar_spells_for_learning(target_spell_id, mastery_levels),
            ttl=3600  # 1 hour
        )
        
        return learning_path
    
    def efficient_mana_regeneration(self, player_ids: List[str]):
        """Efficiently regenerate mana for multiple players"""
        
        # Get current mana states from cache
        cached_states = self.cache.get_multiple_player_states(player_ids)
        
        # Only regenerate for players who need it
        players_needing_regen = []
        for player_id, state in cached_states.items():
            if state and state.get('current_mana', 0) < state.get('max_mana', 100):
                players_needing_regen.append(player_id)
        
        if players_needing_regen:
            # Queue batch regeneration
            queue_batch_mana_regeneration(players_needing_regen)
            self.performance_metrics['async_tasks_queued'] += len(players_needing_regen)
    
    def update_leyline_network(self, region_id: str = None):
        """Trigger leyline network update"""
        
        # Invalidate related caches
        if region_id:
            self.cache.invalidate_region_cache(region_id)
        
        # Queue leyline update
        update_leyline_strengths.delay(region_id)
        self.performance_metrics['async_tasks_queued'] += 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        
        cache_health = self.cache.get_cache_health()
        
        return {
            **self.performance_metrics,
            'cache_hit_rate': (
                self.performance_metrics['cache_hits'] / 
                max(1, self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'])
            ) * 100,
            'cache_health': cache_health
        }
    
    def preload_player_data(self, player_id: str):
        """Preload and cache player data for optimal performance"""
        
        # Load core player state
        player_state = self.get_enhanced_player_state(player_id)
        
        if player_state:
            # Preload recent spell usage for recommendations
            self.vector_db.generate_player_preference_vector(player_id)
            
            # Preload environmental data for current location
            if 'last_location' in player_state:
                self.get_environmental_magic_bonus(player_state['last_location'])
            
            logger.info(f"Preloaded data for player {player_id}")

# Integration helper functions for easy adoption
def enhance_existing_spell_system(existing_magic_system):
    """
    Wrapper to enhance existing magic system with minimal code changes
    """
    enhanced_system = EnhancedMagicSystem()
    
    # Store reference to original methods
    original_cast_spell = existing_magic_system.cast_spell
    
    def enhanced_cast_spell(player_id: str, spell_data: Dict[str, Any]):
        return enhanced_system.integrate_with_existing_spell_cast(
            player_id, spell_data, existing_magic_system
        )
    
    # Replace with enhanced version
    existing_magic_system.cast_spell = enhanced_cast_spell
    existing_magic_system.enhanced_backend = enhanced_system
    
    return existing_magic_system

def create_magic_performance_monitor():
    """Create a performance monitor for the magic system"""
    
    enhanced_system = EnhancedMagicSystem()
    
    def log_performance_metrics():
        metrics = enhanced_system.get_performance_metrics()
        logger.info(f"Magic System Performance: {metrics}")
    
    return log_performance_metrics

# Example integration with your existing magic system
class MagicSystemAdapter:
    """
    Adapter to bridge your existing magic system with enhanced backend
    Preserves all existing functionality while adding performance optimizations
    """
    
    def __init__(self, original_magic_system):
        self.original_system = original_magic_system
        self.enhanced_backend = EnhancedMagicSystem()
    
    def cast_spell(self, player_id: str, spell_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced spell casting with fallback to original system"""
        
        try:
            # Try enhanced processing first
            return self.enhanced_backend.integrate_with_existing_spell_cast(
                player_id, spell_data, self.original_system
            )
        except Exception as e:
            logger.warning(f"Enhanced processing failed, falling back to original: {e}")
            # Fallback to original system
            return self.original_system.cast_spell(player_id, spell_data)
    
    def get_spell_recommendations(self, player_id: str) -> List[Dict[str, Any]]:
        """Get intelligent spell recommendations"""
        return self.enhanced_backend.get_intelligent_spell_recommendations(player_id)
    
    def preload_player(self, player_id: str):
        """Preload player data for optimal performance"""
        self.enhanced_backend.preload_player_data(player_id)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.enhanced_backend.get_performance_metrics()
    
    # Delegate all other methods to original system
    def __getattr__(self, name):
        return getattr(self.original_system, name)
