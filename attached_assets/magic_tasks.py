"""
Enhanced Magic System Tasks for Celery
Optimized async processing for your magic system
"""

from celery import Celery, group, chain
from celery.exceptions import Retry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import redis
import json
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

from app.db.magic_models import MagicEvent, PlayerMagicState, SpellTemplate, LeylineNode
from app.db.database import get_database_url

# Configure logging
logger = logging.getLogger(__name__)

# Redis client for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Database setup
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MagicTaskBase:
    """Base class for magic-related tasks with common functionality"""
    
    @staticmethod
    def get_db_session():
        return SessionLocal()
    
    @staticmethod
    def cache_result(key: str, data: Any, ttl: int = 3600):
        """Cache result in Redis with TTL"""
        redis_client.setex(key, ttl, json.dumps(data, default=str))
    
    @staticmethod
    def get_cached_result(key: str) -> Optional[Any]:
        """Get cached result from Redis"""
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

# Spell Processing Tasks
@celery.task(bind=True, max_retries=3, rate_limit='100/m')
def process_spell_cast(self, player_id: str, spell_data: Dict[str, Any]):
    """
    Process spell casting with full validation and side effects
    Handles complex spell interactions asynchronously
    """
    try:
        session = SessionLocal()
        
        # Check cache for recent similar spell
        cache_key = f"spell_result:{spell_data.get('spell_id')}:{player_id}"
        cached_result = MagicTaskBase.get_cached_result(cache_key)
        
        if cached_result and spell_data.get('allow_cache', True):
            logger.info(f"Using cached spell result for {player_id}")
            return cached_result
        
        # Get player magic state
        player_state = session.query(PlayerMagicState).filter_by(player_id=player_id).first()
        if not player_state:
            raise ValueError(f"Player {player_id} not found")
        
        # Validate mana requirements
        spell_template = session.query(SpellTemplate).filter_by(id=spell_data['spell_id']).first()
        if not spell_template:
            raise ValueError(f"Spell {spell_data['spell_id']} not found")
        
        if player_state.current_mana < spell_template.mana_cost:
            return {"success": False, "reason": "Insufficient mana"}
        
        # Calculate spell success based on mastery and environmental factors
        success_rate = calculate_spell_success_rate.delay(
            player_id, spell_data['spell_id'], spell_data.get('location')
        ).get()
        
        # Process spell effects
        spell_result = {
            "success": np.random.random() < success_rate,
            "mana_used": spell_template.mana_cost,
            "cast_time": spell_template.cast_time,
            "effects": spell_template.effects,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if spell_result["success"]:
            # Update player mana
            player_state.current_mana -= spell_template.mana_cost
            
            # Process spell effects
            process_spell_effects.delay(player_id, spell_template.effects, spell_data)
            
            # Check for corruption
            if spell_data.get('corruption_risk', 0) > 0:
                check_corruption_gain.delay(player_id, spell_data['corruption_risk'])
        
        # Log magic event
        magic_event = MagicEvent(
            player_id=player_id,
            event_type='spell_cast',
            spell_id=spell_data['spell_id'],
            domain_id=spell_data.get('domain_id'),
            event_data=spell_data,
            mana_cost=spell_template.mana_cost,
            cast_time=spell_template.cast_time,
            success_rate=success_rate,
            corruption_before=player_state.corruption_level
        )
        session.add(magic_event)
        session.commit()
        
        # Cache successful result
        if spell_result["success"]:
            MagicTaskBase.cache_result(cache_key, spell_result, ttl=1800)
        
        # Trigger related tasks
        update_spell_statistics.delay(spell_data['spell_id'], spell_result["success"])
        
        return spell_result
        
    except Exception as exc:
        logger.error(f"Spell processing failed for {player_id}: {exc}")
        if self.request.retries < 3:
            raise self.retry(countdown=60, exc=exc)
        raise
    
    finally:
        session.close()

@celery.task(rate_limit='50/m')
def calculate_spell_success_rate(player_id: str, spell_id: str, location: Dict = None):
    """
    Calculate spell success rate based on multiple factors
    CPU-intensive calculation done asynchronously
    """
    session = SessionLocal()
    
    try:
        # Get player mastery
        player_state = session.query(PlayerMagicState).filter_by(player_id=player_id).first()
        spell_template = session.query(SpellTemplate).filter_by(id=spell_id).first()
        
        base_success = 0.7  # Base success rate
        
        # Factor in mastery level
        if spell_template.magic_type == 'arcane':
            mastery_bonus = player_state.arcane_mastery * 0.05
        elif spell_template.magic_type == 'mana':
            mastery_bonus = player_state.mana_infusion * 0.05
        else:
            mastery_bonus = player_state.spiritual_utility * 0.05
        
        # Environmental factors
        location_bonus = 0.0
        if location:
            location_bonus = calculate_location_magic_bonus.delay(location).get()
        
        # Corruption penalty
        corruption_penalty = player_state.corruption_level * 0.1
        
        final_success_rate = min(0.95, max(0.05, 
            base_success + mastery_bonus + location_bonus - corruption_penalty
        ))
        
        return final_success_rate
        
    finally:
        session.close()

@celery.task(rate_limit='200/m')
def process_spell_effects(player_id: str, effects: Dict[str, Any], spell_data: Dict[str, Any]):
    """Process spell effects and side effects"""
    
    # Process each effect type
    for effect_type, effect_data in effects.items():
        if effect_type == 'damage':
            process_magic_damage.delay(player_id, effect_data, spell_data)
        elif effect_type == 'heal':
            process_magic_healing.delay(player_id, effect_data)
        elif effect_type == 'enchantment':
            apply_enchantment.delay(player_id, effect_data)
        elif effect_type == 'environmental':
            modify_environment.delay(spell_data.get('location'), effect_data)

# Leyline and Environmental Tasks
@celery.task(rate_limit='10/m')
def update_leyline_strengths(region_id: str = None):
    """
    Update leyline strengths based on usage and environmental factors
    Computationally expensive, run periodically
    """
    session = SessionLocal()
    
    try:
        query = session.query(LeylineNode)
        if region_id:
            query = query.filter_by(region_id=region_id)
        
        nodes = query.all()
        
        for node in nodes:
            # Complex leyline strength calculation
            new_strength = calculate_leyline_flux(node)
            
            if abs(new_strength - node.strength) > 0.1:  # Significant change
                node.strength = new_strength
                node.last_strength_update = datetime.utcnow()
                
                # Invalidate related caches
                cache_keys = [
                    f"leyline_strength:{node.region_id}",
                    f"location_magic_bonus:{node.x_coordinate}:{node.y_coordinate}"
                ]
                for key in cache_keys:
                    redis_client.delete(key)
                
                # Notify connected systems
                publish_leyline_update.delay(node.id, new_strength)
        
        session.commit()
        logger.info(f"Updated {len(nodes)} leyline nodes")
        
    finally:
        session.close()

def calculate_leyline_flux(node: LeylineNode) -> float:
    """Calculate new leyline strength based on complex factors"""
    # Time-based fluctuation
    time_factor = np.sin(datetime.utcnow().timestamp() / 3600) * 0.1  # Hourly cycle
    
    # Usage-based decay/growth
    usage_key = f"leyline_usage:{node.id}"
    usage_count = redis_client.get(usage_key) or 0
    usage_factor = min(0.2, float(usage_count) * 0.01)
    
    # Environmental stability
    stability_factor = node.stability * 0.1
    
    # Connected node influence
    connected_influence = 0.0
    for connected_id in node.connected_nodes or []:
        connected_strength = redis_client.get(f"leyline_strength:{connected_id}")
        if connected_strength:
            connected_influence += float(connected_strength) * 0.05
    
    new_strength = max(0.1, min(2.0, 
        node.strength + time_factor + usage_factor + stability_factor + connected_influence
    ))
    
    return new_strength

@celery.task(rate_limit='100/m')
def calculate_location_magic_bonus(location: Dict[str, Any]) -> float:
    """Calculate magic bonus for a specific location"""
    
    cache_key = f"location_magic_bonus:{location.get('x', 0)}:{location.get('y', 0)}"
    cached_bonus = MagicTaskBase.get_cached_result(cache_key)
    
    if cached_bonus is not None:
        return cached_bonus
    
    session = SessionLocal()
    
    try:
        # Find nearby leyline nodes
        x, y = location.get('x', 0), location.get('y', 0)
        
        nearby_nodes = session.query(LeylineNode).filter(
            ((LeylineNode.x_coordinate - x) ** 2 + (LeylineNode.y_coordinate - y) ** 2) < 100
        ).all()
        
        total_bonus = 0.0
        for node in nearby_nodes:
            distance = np.sqrt((node.x_coordinate - x) ** 2 + (node.y_coordinate - y) ** 2)
            distance_factor = max(0, 1 - distance / 100)  # Closer = stronger
            total_bonus += node.strength * distance_factor * 0.1
        
        # Cache result for 30 minutes
        MagicTaskBase.cache_result(cache_key, total_bonus, ttl=1800)
        
        return total_bonus
        
    finally:
        session.close()

# Mana Management Tasks
@celery.task(rate_limit='500/m')
def regenerate_mana(player_id: str):
    """Regenerate mana for a player"""
    
    session = SessionLocal()
    
    try:
        player_state = session.query(PlayerMagicState).filter_by(player_id=player_id).first()
        if not player_state:
            return
        
        if player_state.current_mana >= player_state.max_mana:
            return  # Already at max
        
        # Calculate time since last update
        time_diff = datetime.utcnow() - player_state.last_mana_update
        minutes_passed = time_diff.total_seconds() / 60
        
        # Calculate mana regeneration
        mana_to_regen = minutes_passed * player_state.mana_regen_rate
        new_mana = min(player_state.max_mana, player_state.current_mana + mana_to_regen)
        
        if new_mana != player_state.current_mana:
            player_state.current_mana = new_mana
            player_state.last_mana_update = datetime.utcnow()
            session.commit()
            
            # Update cache
            cache_key = f"player_mana:{player_id}"
            MagicTaskBase.cache_result(cache_key, new_mana, ttl=300)
        
    finally:
        session.close()

# Periodic Tasks
@celery.task
def refresh_magic_statistics():
    """Refresh materialized views and update spell statistics"""
    
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        # Refresh materialized views
        conn.execute("REFRESH MATERIALIZED VIEW magic_player_stats")
        conn.execute("REFRESH MATERIALIZED VIEW spell_popularity")
        conn.execute("REFRESH MATERIALIZED VIEW leyline_activity")
        
        logger.info("Refreshed magic system materialized views")

@celery.task
def cleanup_old_magic_events():
    """Clean up old magic events to maintain performance"""
    
    session = SessionLocal()
    
    try:
        # Delete events older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        deleted_count = session.query(MagicEvent).filter(
            MagicEvent.created_at < cutoff_date
        ).delete()
        
        session.commit()
        logger.info(f"Cleaned up {deleted_count} old magic events")
        
    finally:
        session.close()

# Real-time Event Publishing
@celery.task(rate_limit='1000/m')
def publish_magic_event(event_type: str, event_data: Dict[str, Any]):
    """Publish magic event to Redis pub/sub for real-time updates"""
    
    channel = f"magic_events:{event_type}"
    message = {
        "type": event_type,
        "data": event_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    redis_client.publish(channel, json.dumps(message))

@celery.task(rate_limit='100/m')
def publish_leyline_update(node_id: str, new_strength: float):
    """Publish leyline strength update"""
    
    publish_magic_event.delay("leyline_update", {
        "node_id": node_id,
        "new_strength": new_strength
    })

# Corruption System Tasks
@celery.task(rate_limit='200/m')
def check_corruption_gain(player_id: str, corruption_risk: float):
    """Check if player gains corruption from magic use"""
    
    session = SessionLocal()
    
    try:
        player_state = session.query(PlayerMagicState).filter_by(player_id=player_id).first()
        if not player_state:
            return
        
        # Calculate corruption gain probability
        corruption_chance = corruption_risk * (1 - player_state.corruption_resistance)
        
        if np.random.random() < corruption_chance:
            corruption_gain = np.random.uniform(0.1, 1.0)
            old_corruption = player_state.corruption_level
            player_state.corruption_level = min(100, player_state.corruption_level + corruption_gain)
            
            # Log corruption event
            magic_event = MagicEvent(
                player_id=player_id,
                event_type='corruption_gain',
                event_data={
                    "corruption_gain": corruption_gain,
                    "source": "spell_casting",
                    "risk_factor": corruption_risk
                },
                corruption_before=old_corruption,
                corruption_after=player_state.corruption_level
            )
            session.add(magic_event)
            session.commit()
            
            # Publish corruption update
            publish_magic_event.delay("corruption_update", {
                "player_id": player_id,
                "new_corruption": player_state.corruption_level,
                "corruption_gain": corruption_gain
            })
    
    finally:
        session.close()

# Task scheduling configuration for periodic tasks
from celery.schedules import crontab

# Add these to your Celery beat schedule
MAGIC_CELERY_BEAT_SCHEDULE = {
    'refresh-magic-statistics': {
        'task': 'app.tasks.magic_tasks.refresh_magic_statistics',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'cleanup-old-magic-events': {
        'task': 'app.tasks.magic_tasks.cleanup_old_magic_events',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    'update-leyline-strengths': {
        'task': 'app.tasks.magic_tasks.update_leyline_strengths',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

# Helper functions for your existing magic system integration
def queue_spell_processing(player_id: str, spell_data: Dict[str, Any], priority: str = 'normal'):
    """Queue spell processing with appropriate priority"""
    
    if priority == 'high':
        return process_spell_cast.apply_async(
            args=[player_id, spell_data],
            priority=9
        )
    else:
        return process_spell_cast.delay(player_id, spell_data)

def queue_batch_mana_regeneration(player_ids: List[str]):
    """Queue mana regeneration for multiple players efficiently"""
    
    # Group mana regeneration tasks
    job = group(regenerate_mana.s(player_id) for player_id in player_ids)
    return job.apply_async()

def queue_complex_ritual(ritual_data: Dict[str, Any], participant_ids: List[str]):
    """Queue complex ritual processing with multiple participants"""
    
    # Chain of tasks for complex ritual
    ritual_chain = chain(
        # Pre-process ritual requirements
        group(process_spell_cast.s(pid, ritual_data) for pid in participant_ids),
        # Calculate combined effects
        calculate_ritual_outcome.s(ritual_data),
        # Apply final effects
        apply_ritual_effects.s(participant_ids)
    )
    
    return ritual_chain.apply_async()
