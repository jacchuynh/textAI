"""
Example usage and migration guide for the Enhanced Magic System Backend
Demonstrates how to integrate the enhancements with your existing magic system
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Import your existing magic system
# from magic_system import MagicSystem

# Import the enhanced components
from app.magic_integration import EnhancedMagicSystem, MagicSystemAdapter, enhance_existing_spell_system
from app.magic_cache import MagicCache
from app.vector.magic_vectors import initialize_spell_vectors, get_spell_recommendations
from app.tasks.magic_tasks import queue_spell_processing, refresh_magic_statistics

def example_integration_with_existing_system():
    """
    Example: How to integrate enhanced backend with your existing magic system
    """
    
    # Assuming you have an existing magic system class
    # original_magic_system = MagicSystem()
    
    # Option 1: Use the adapter (recommended for gradual migration)
    # enhanced_magic_system = MagicSystemAdapter(original_magic_system)
    
    # Option 2: Enhance existing system directly
    # enhanced_magic_system = enhance_existing_spell_system(original_magic_system)
    
    # For demonstration, we'll create a mock integration
    class MockMagicSystem:
        def cast_spell(self, player_id: str, spell_data: Dict[str, Any]) -> Dict[str, Any]:
            # Original spell casting logic
            return {
                "success": True,
                "mana_used": spell_data.get('mana_cost', 10),
                "damage": 25,
                "spell_id": spell_data.get('spell_id')
            }
        
        def calculate_spell_success(self, player_id: str, spell_data: Dict[str, Any]) -> float:
            # Original success calculation
            return 0.8
    
    original_system = MockMagicSystem()
    enhanced_system = MagicSystemAdapter(original_system)
    
    # Example spell casting with enhancements
    player_id = "player_123"
    spell_data = {
        "spell_id": "fireball",
        "mana_cost": 15,
        "location": {"x": 100, "y": 200, "region_id": "forest_region"},
        "time_of_day": "night",
        "weather": "storm",
        "allow_cache": True
    }
    
    print("=== Enhanced Spell Casting ===")
    result = enhanced_system.cast_spell(player_id, spell_data)
    print(f"Spell result: {result}")
    
    # Get intelligent spell recommendations
    print("\n=== Spell Recommendations ===")
    recommendations = enhanced_system.get_spell_recommendations(player_id)
    print(f"Recommended spells: {recommendations}")
    
    # Preload player data for better performance
    print("\n=== Performance Optimization ===")
    enhanced_system.preload_player(player_id)
    
    # Get performance metrics
    metrics = enhanced_system.get_performance_stats()
    print(f"Performance metrics: {metrics}")

def example_database_setup():
    """
    Example: Setting up the enhanced database schema
    """
    
    from app.db.magic_models import Base, create_monthly_partition, MATERIALIZED_VIEWS
    from sqlalchemy import create_engine
    
    print("=== Database Setup ===")
    
    # Create tables
    engine = create_engine("postgresql://user:password@localhost/gamedb")
    Base.metadata.create_all(engine)
    print("✓ Created enhanced magic tables")
    
    # Create monthly partitions for current and next month
    current_date = datetime.now()
    partition_sql = create_monthly_partition(current_date.year, current_date.month)
    print(f"✓ Partition SQL generated: {partition_sql[:100]}...")
    
    # Create materialized views
    with engine.connect() as conn:
        for view_name, view_sql in MATERIALIZED_VIEWS.items():
            try:
                conn.execute(view_sql)
                print(f"✓ Created materialized view: {view_name}")
            except Exception as e:
                print(f"⚠ Failed to create view {view_name}: {e}")

def example_caching_usage():
    """
    Example: Using the magic caching system
    """
    
    print("=== Caching System Usage ===")
    
    cache = MagicCache()
    
    # Cache player mana state
    player_id = "player_123"
    mana_data = {
        "current_mana": 85.5,
        "max_mana": 100.0,
        "regen_rate": 1.2
    }
    
    cache.cache_player_mana(player_id, mana_data)
    print("✓ Cached player mana state")
    
    # Retrieve from cache
    cached_mana = cache.get_player_mana(player_id)
    print(f"✓ Retrieved from cache: {cached_mana}")
    
    # Cache spell cooldown
    cache.set_spell_cooldown(player_id, "fireball", 30)  # 30 seconds
    is_on_cooldown = cache.check_spell_cooldown(player_id, "fireball")
    remaining_time = cache.get_remaining_cooldown(player_id, "fireball")
    print(f"✓ Spell on cooldown: {is_on_cooldown}, remaining: {remaining_time}s")
    
    # Cache environmental bonus
    location_hash = cache.generate_context_hash({"x": 100, "y": 200, "region": "forest"})
    bonus_data = {"total_bonus": 0.15, "leyline_bonus": 0.1, "time_bonus": 0.05}
    cache.cache_environmental_bonus(location_hash, bonus_data)
    print("✓ Cached environmental bonus")
    
    # Get cache health
    health = cache.get_cache_health()
    print(f"✓ Cache health: {health['hit_rate']:.1f}% hit rate")

def example_async_task_usage():
    """
    Example: Using async task processing
    """
    
    print("=== Async Task Processing ===")
    
    # Queue a complex spell for async processing
    player_id = "player_123"
    complex_spell_data = {
        "spell_id": "meteor_storm",
        "mana_cost": 50,
        "complex_calculation": True,
        "participants": ["player_123", "player_456"],
        "ritual_components": ["dragon_scale", "moonstone", "phoenix_feather"]
    }
    
    # Queue with high priority
    task_result = queue_spell_processing(player_id, complex_spell_data, priority='high')
    print(f"✓ Queued complex spell processing: {task_result.id}")
    
    # Queue batch mana regeneration
    player_ids = ["player_123", "player_456", "player_789"]
    from app.tasks.magic_tasks import queue_batch_mana_regeneration
    batch_task = queue_batch_mana_regeneration(player_ids)
    print(f"✓ Queued batch mana regeneration for {len(player_ids)} players")
    
    # Refresh magic statistics
    refresh_magic_statistics.delay()
    print("✓ Queued statistics refresh")

def example_vector_database_usage():
    """
    Example: Using vector database for spell intelligence
    """
    
    print("=== Vector Database Usage ===")
    
    # Initialize spell vectors (run once during setup)
    try:
        initialize_spell_vectors()
        print("✓ Initialized spell vectors")
    except Exception as e:
        print(f"⚠ Vector initialization failed: {e}")
    
    # Get spell recommendations for a player
    player_id = "player_123"
    recommendations = get_spell_recommendations(player_id)
    print(f"✓ Got {len(recommendations)} spell recommendations")
    
    for i, rec in enumerate(recommendations[:3]):  # Show top 3
        print(f"  {i+1}. {rec.get('name', 'Unknown')} (similarity: {rec.get('similarity_score', 0):.2f})")
    
    # Find similar spells for learning progression
    from app.vector.magic_vectors import find_similar_spells_for_learning
    mastery_levels = {"arcane": 5, "mana": 3, "spiritual": 2}
    learning_path = find_similar_spells_for_learning("fireball", mastery_levels)
    print(f"✓ Found {len(learning_path)} spells for learning progression")

def example_real_time_events():
    """
    Example: Real-time magic event system
    """
    
    print("=== Real-Time Events ===")
    
    from app.magic_cache import RealTimeMagicCache
    import redis
    
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    event_cache = RealTimeMagicCache(redis_client)
    
    # Publish a magic event
    event_data = {
        "player_id": "player_123",
        "spell_id": "fireball",
        "location": {"x": 100, "y": 200},
        "damage_dealt": 25,
        "targets_hit": 3
    }
    
    event_cache.publish_magic_event("spell_cast", event_data)
    print("✓ Published spell cast event")
    
    # Cache ritual progress
    ritual_data = {
        "ritual_id": "summon_dragon",
        "progress": 0.75,
        "participants": ["player_123", "player_456"],
        "estimated_completion": (datetime.now().timestamp() + 300)  # 5 minutes
    }
    
    event_cache.cache_ritual_progress("ritual_001", ritual_data)
    print("✓ Cached ritual progress")

def example_performance_monitoring():
    """
    Example: Performance monitoring and optimization
    """
    
    print("=== Performance Monitoring ===")
    
    from app.magic_integration import create_magic_performance_monitor
    
    # Create performance monitor
    monitor = create_magic_performance_monitor()
    
    # Enhanced system with metrics
    enhanced_system = EnhancedMagicSystem()
    
    # Simulate some operations
    player_id = "player_123"
    enhanced_system.get_enhanced_player_state(player_id)
    enhanced_system.get_cached_spell_template("fireball")
    enhanced_system.get_environmental_magic_bonus({"x": 100, "y": 200})
    
    # Get performance metrics
    metrics = enhanced_system.get_performance_metrics()
    print("✓ Performance Metrics:")
    print(f"  Cache hit rate: {metrics['cache_hit_rate']:.1f}%")
    print(f"  DB queries: {metrics['db_queries']}")
    print(f"  Async tasks queued: {metrics['async_tasks_queued']}")
    print(f"  Cache health: {metrics['cache_health']['hit_rate']:.1f}%")

def migration_checklist():
    """
    Checklist for migrating to the enhanced magic system
    """
    
    print("=== Migration Checklist ===")
    print("□ 1. Backup existing magic system data")
    print("□ 2. Set up PostgreSQL database with partitioning")
    print("□ 3. Configure Redis for caching and task queue")
    print("□ 4. Set up Celery workers for async processing")
    print("□ 5. Initialize vector database with existing spells")
    print("□ 6. Create materialized views for analytics")
    print("□ 7. Set up monitoring and logging")
    print("□ 8. Test with a subset of players")
    print("□ 9. Gradually migrate production traffic")
    print("□ 10. Monitor performance and optimize")
    
    print("\n=== Required Dependencies ===")
    dependencies = [
        "sqlalchemy",
        "psycopg2-binary",
        "redis",
        "celery",
        "numpy",
        "scikit-learn",
        "faiss-cpu",  # or faiss-gpu for GPU acceleration
        "pickle5"
    ]
    
    print("pip install " + " ".join(dependencies))

def example_configuration():
    """
    Example configuration for the enhanced system
    """
    
    print("=== Configuration Example ===")
    
    config_example = """
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gamedb',
        'USER': 'gameuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'socket_connect_timeout': 5,
    'socket_timeout': 5,
    'retry_on_timeout': True
}

CELERY_CONFIG = {
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_routes': {
        'app.tasks.magic_tasks.*': {'queue': 'magic'},
        'app.tasks.magic_tasks.process_spell_cast': {'queue': 'high_priority'},
    }
}

MAGIC_SYSTEM_CONFIG = {
    'cache_ttl': {
        'player_mana': 300,
        'spell_data': 3600,
        'leyline_strength': 1800,
    },
    'vector_db': {
        'dimension': 128,
        'similarity_threshold': 0.7,
    },
    'performance': {
        'enable_caching': True,
        'enable_async_processing': True,
        'enable_vector_recommendations': True,
    }
}
"""
    
    print(config_example)

if __name__ == "__main__":
    print("Enhanced Magic System Backend - Example Usage\n")
    
    # Run examples
    try:
        example_integration_with_existing_system()
        print("\n" + "="*50 + "\n")
        
        example_caching_usage()
        print("\n" + "="*50 + "\n")
        
        example_async_task_usage()
        print("\n" + "="*50 + "\n")
        
        example_vector_database_usage()
        print("\n" + "="*50 + "\n")
        
        example_real_time_events()
        print("\n" + "="*50 + "\n")
        
        example_performance_monitoring()
        print("\n" + "="*50 + "\n")
        
        migration_checklist()
        print("\n" + "="*50 + "\n")
        
        example_configuration()
        
    except Exception as e:
        print(f"Example execution failed: {e}")
        print("This is expected in a demo environment without full infrastructure setup.")
    
    print("\n✓ Enhanced Magic System Backend examples completed!")
    print("Review the implementation files for detailed integration guidance.")
