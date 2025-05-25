"""
Magic System Asynchronous Processing

This module provides Redis and Celery integration for the magic system,
allowing for background processing of magical effects, delayed consequences,
and optimized performance for complex magical operations.
"""

from typing import Dict, List, Any, Optional, Union
import json
import time
import uuid
from celery import Celery
from redis import Redis

# Import magic system components
from .magic_system import (
    MagicSystem, MagicUser, Spell, MagicalEffect, Domain, 
    DamageType, EffectType, MagicTier, MagicSource
)
from .advanced_magic_features import (
    EnvironmentalMagicResonance, MagicalConsequenceSystem, ManaHeartEvolution,
    SpellCombinationSystem, Effect
)

# Configure Celery with Redis as the broker and backend
celery_app = Celery('magic_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Redis client for caching and state management
redis_client = Redis(host='localhost', port=6379, db=1, decode_responses=True)


class MagicAsyncProcessor:
    """
    Handles asynchronous processing for the magic system using Celery and Redis.
    
    This allows for:
    1. Background processing of complex magical calculations
    2. Delayed magical effects and consequences
    3. Improved performance for intensive magical operations
    4. Persistent tracking of magical phenomena across sessions
    """
    
    def __init__(self, magic_system: MagicSystem, consequence_system: MagicalConsequenceSystem):
        """
        Initialize the magic async processor.
        
        Args:
            magic_system: The magic system instance
            consequence_system: The magical consequence system
        """
        self.magic_system = magic_system
        self.consequence_system = consequence_system
        self.environmental_resonance = EnvironmentalMagicResonance()
        
        # Redis keys
        self.active_effects_key = "magic:active_effects"
        self.location_magic_key_prefix = "magic:location:"
        self.spell_cooldown_key_prefix = "magic:cooldown:"
        self.mana_regen_key_prefix = "magic:mana_regen:"
        
        # Initialize Redis structures if needed
        self._initialize_redis_structures()
    
    def _initialize_redis_structures(self):
        """Initialize Redis data structures if they don't exist"""
        if not redis_client.exists(self.active_effects_key):
            redis_client.set(self.active_effects_key, json.dumps({}))
    
    # ======================================================================
    # Asynchronous Spell Casting
    # ======================================================================
    
    def cast_spell_async(self, caster_id: str, spell_id: str, 
                       targets: List[str], location_id: str, 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queue a spell cast for asynchronous processing.
        
        Args:
            caster_id: ID of the spell caster
            spell_id: ID of the spell to cast
            targets: List of target IDs
            location_id: ID of the location
            context: Additional context for the spell cast
            
        Returns:
            Task information for tracking the spell cast
        """
        # Generate a unique task ID
        task_id = f"spell_cast_{uuid.uuid4().hex}"
        
        # Store spell cast parameters in Redis
        cast_data = {
            "caster_id": caster_id,
            "spell_id": spell_id,
            "targets": targets,
            "location_id": location_id,
            "context": context,
            "status": "queued",
            "queued_at": time.time()
        }
        redis_client.set(f"magic:cast:{task_id}", json.dumps(cast_data))
        
        # Queue the spell cast task
        result = process_spell_cast.apply_async(
            args=[caster_id, spell_id, targets, location_id, context],
            task_id=task_id
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "estimated_completion": "Calculating...",
            "message": f"Spell {spell_id} queued for casting"
        }
    
    def get_spell_cast_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an asynchronous spell cast.
        
        Args:
            task_id: ID of the spell cast task
            
        Returns:
            Status information for the spell cast
        """
        # Check if the task exists in Redis
        cast_data_str = redis_client.get(f"magic:cast:{task_id}")
        if not cast_data_str:
            return {
                "status": "not_found",
                "message": f"No spell cast task found with ID {task_id}"
            }
        
        # Parse the cast data
        cast_data = json.loads(cast_data_str)
        
        # Check if the task has completed
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'SUCCESS':
            # Get the result if available
            result = task.result if task.ready() else None
            
            # Update the cast data
            cast_data["status"] = "completed"
            cast_data["completed_at"] = time.time()
            cast_data["result"] = result
            
            # Update Redis
            redis_client.set(f"magic:cast:{task_id}", json.dumps(cast_data))
            
            return {
                "status": "completed",
                "result": result,
                "spell_id": cast_data["spell_id"],
                "caster_id": cast_data["caster_id"],
                "completed_at": cast_data["completed_at"]
            }
        
        elif task.state == 'FAILURE':
            # Update the cast data
            cast_data["status"] = "failed"
            cast_data["failed_at"] = time.time()
            cast_data["error"] = str(task.result) if task.ready() else "Unknown error"
            
            # Update Redis
            redis_client.set(f"magic:cast:{task_id}", json.dumps(cast_data))
            
            return {
                "status": "failed",
                "error": cast_data["error"],
                "spell_id": cast_data["spell_id"],
                "caster_id": cast_data["caster_id"],
                "failed_at": cast_data["failed_at"]
            }
        
        else:
            # Task is still in progress
            return {
                "status": "in_progress",
                "message": f"Spell cast is being processed",
                "spell_id": cast_data["spell_id"],
                "caster_id": cast_data["caster_id"],
                "queued_at": cast_data["queued_at"]
            }
    
    # ======================================================================
    # Magical Effects Management
    # ======================================================================
    
    def register_delayed_effect(self, effect: Effect, target_id: str, 
                             delay_seconds: int, location_id: Optional[str] = None) -> str:
        """
        Register a magical effect to be applied after a delay.
        
        Args:
            effect: The magical effect to apply
            target_id: ID of the target (character, item, or location)
            delay_seconds: Delay in seconds before applying the effect
            location_id: Optional location ID if the effect is location-based
            
        Returns:
            ID of the delayed effect
        """
        # Generate a unique effect ID
        effect_id = f"effect_{uuid.uuid4().hex}"
        
        # Store effect data in Redis
        effect_data = {
            "effect": {
                "id": effect.id,
                "description": effect.description,
                "duration_seconds": effect.duration_seconds,
                "magnitude": effect.magnitude if isinstance(effect.magnitude, (int, float, str)) else str(effect.magnitude)
            },
            "target_id": target_id,
            "location_id": location_id,
            "status": "pending",
            "created_at": time.time(),
            "apply_at": time.time() + delay_seconds
        }
        redis_client.set(f"magic:delayed_effect:{effect_id}", json.dumps(effect_data))
        
        # Queue the delayed effect task
        apply_delayed_effect.apply_async(
            args=[effect_id],
            countdown=delay_seconds
        )
        
        return effect_id
    
    def get_active_effects(self, target_id: str) -> List[Dict[str, Any]]:
        """
        Get all active magical effects for a target.
        
        Args:
            target_id: ID of the target (character, item, or location)
            
        Returns:
            List of active effects
        """
        # Get all active effects from Redis
        active_effects_str = redis_client.get(self.active_effects_key)
        if not active_effects_str:
            return []
        
        active_effects = json.loads(active_effects_str)
        
        # Filter effects for the target
        target_effects = []
        for effect_id, effect_data in active_effects.items():
            if effect_data.get("target_id") == target_id:
                # Add the effect ID to the data
                effect_data["effect_id"] = effect_id
                target_effects.append(effect_data)
        
        return target_effects
    
    def update_effect_durations(self, seconds_elapsed: int = 1) -> List[Dict[str, Any]]:
        """
        Update durations for all active effects, removing expired ones.
        
        Args:
            seconds_elapsed: Seconds elapsed since last update
            
        Returns:
            List of expired effects
        """
        # Queue the update task
        result = update_active_effects.apply_async(args=[seconds_elapsed])
        
        # Wait for the result (this would normally be handled asynchronously)
        expired_effects = result.get() if result.ready() else []
        
        return expired_effects
    
    # ======================================================================
    # Mana and Resource Regeneration
    # ======================================================================
    
    def register_mana_regeneration(self, character_id: str, magic_profile: MagicUser) -> None:
        """
        Register a character for automatic mana regeneration.
        
        Args:
            character_id: ID of the character
            magic_profile: The character's magic profile
        """
        if not magic_profile.has_mana_heart:
            return
        
        # Store regeneration data in Redis
        regen_data = {
            "character_id": character_id,
            "mana_current": magic_profile.mana_current,
            "mana_max": magic_profile.mana_max,
            "regen_rate": magic_profile.mana_regeneration_rate,
            "last_update": time.time()
        }
        redis_client.set(f"{self.mana_regen_key_prefix}{character_id}", json.dumps(regen_data))
    
    def update_mana_regeneration(self, character_id: str) -> Dict[str, Any]:
        """
        Update mana regeneration for a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Updated mana information
        """
        # Get regeneration data from Redis
        regen_data_str = redis_client.get(f"{self.mana_regen_key_prefix}{character_id}")
        if not regen_data_str:
            return {
                "success": False,
                "message": f"No mana regeneration data found for character {character_id}"
            }
        
        # Parse regeneration data
        regen_data = json.loads(regen_data_str)
        
        # Calculate time elapsed since last update
        current_time = time.time()
        seconds_elapsed = current_time - regen_data["last_update"]
        
        # Calculate regenerated mana
        regen_amount = regen_data["regen_rate"] * seconds_elapsed
        new_mana = min(regen_data["mana_current"] + regen_amount, regen_data["mana_max"])
        
        # Update regeneration data
        regen_data["mana_current"] = new_mana
        regen_data["last_update"] = current_time
        
        # Store updated data in Redis
        redis_client.set(f"{self.mana_regen_key_prefix}{character_id}", json.dumps(regen_data))
        
        return {
            "success": True,
            "character_id": character_id,
            "mana_current": new_mana,
            "mana_max": regen_data["mana_max"],
            "regenerated": new_mana - regen_data["mana_current"],
            "seconds_elapsed": seconds_elapsed
        }
    
    # ======================================================================
    # Location Magic Processing
    # ======================================================================
    
    def process_location_magic(self, location_id: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process magical phenomena in a location.
        
        Args:
            location_id: ID of the location
            location_data: Data about the location
            
        Returns:
            Updated location magic information
        """
        # Queue the location processing task
        result = process_location_magic_task.apply_async(args=[location_id, location_data])
        
        # This would normally be handled asynchronously, but for simplicity we'll wait
        location_magic = result.get() if result.ready() else {"status": "processing"}
        
        return location_magic
    
    def get_location_magic_cache(self, location_id: str) -> Dict[str, Any]:
        """
        Get cached magical information about a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            Cached location magic information
        """
        # Get location magic data from Redis
        location_magic_str = redis_client.get(f"{self.location_magic_key_prefix}{location_id}")
        if not location_magic_str:
            return {}
        
        return json.loads(location_magic_str)


# ======================================================================
# Celery Tasks
# ======================================================================

@celery_app.task(name='magic.process_spell_cast')
def process_spell_cast(caster_id: str, spell_id: str, targets: List[str], 
                     location_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a spell cast asynchronously.
    
    Args:
        caster_id: ID of the spell caster
        spell_id: ID of the spell to cast
        targets: List of target IDs
        location_id: ID of the location
        context: Additional context for the spell cast
        
    Returns:
        Result of the spell cast
    """
    # This would normally fetch data from the database
    # For now, we'll just simulate processing
    time.sleep(1)  # Simulate processing time
    
    # In a real implementation, we would:
    # 1. Get the caster's magic profile
    # 2. Get the spell details
    # 3. Get the targets
    # 4. Get the location
    # 5. Perform the spell cast
    # 6. Apply consequences
    # 7. Update the database
    
    return {
        "success": True,
        "spell_id": spell_id,
        "caster_id": caster_id,
        "targets_affected": len(targets),
        "location_id": location_id,
        "effects_applied": ["damage", "status_effect"],
        "consequences": ["magical_residue", "ley_disruption"]
    }


@celery_app.task(name='magic.apply_delayed_effect')
def apply_delayed_effect(effect_id: str) -> Dict[str, Any]:
    """
    Apply a delayed magical effect.
    
    Args:
        effect_id: ID of the delayed effect
        
    Returns:
        Result of applying the effect
    """
    # Get effect data from Redis
    effect_data_str = redis_client.get(f"magic:delayed_effect:{effect_id}")
    if not effect_data_str:
        return {
            "success": False,
            "message": f"No delayed effect found with ID {effect_id}"
        }
    
    # Parse effect data
    effect_data = json.loads(effect_data_str)
    
    # Mark as applied
    effect_data["status"] = "applied"
    effect_data["applied_at"] = time.time()
    
    # Store in active effects
    active_effects_str = redis_client.get("magic:active_effects")
    active_effects = json.loads(active_effects_str) if active_effects_str else {}
    active_effects[effect_id] = {
        "effect": effect_data["effect"],
        "target_id": effect_data["target_id"],
        "location_id": effect_data["location_id"],
        "applied_at": effect_data["applied_at"],
        "expires_at": effect_data["applied_at"] + (effect_data["effect"]["duration_seconds"] or 0)
    }
    redis_client.set("magic:active_effects", json.dumps(active_effects))
    
    # Update Redis
    redis_client.set(f"magic:delayed_effect:{effect_id}", json.dumps(effect_data))
    
    return {
        "success": True,
        "effect_id": effect_id,
        "target_id": effect_data["target_id"],
        "applied_at": effect_data["applied_at"]
    }


@celery_app.task(name='magic.update_active_effects')
def update_active_effects(seconds_elapsed: int = 1) -> List[Dict[str, Any]]:
    """
    Update all active magical effects, removing expired ones.
    
    Args:
        seconds_elapsed: Seconds elapsed since last update
        
    Returns:
        List of expired effects
    """
    # Get all active effects from Redis
    active_effects_str = redis_client.get("magic:active_effects")
    if not active_effects_str:
        return []
    
    active_effects = json.loads(active_effects_str)
    
    # Track expired effects
    expired_effects = []
    current_time = time.time()
    
    # Update durations and find expired effects
    updated_effects = {}
    for effect_id, effect_data in active_effects.items():
        # Skip effects with no duration
        if not effect_data.get("effect", {}).get("duration_seconds"):
            updated_effects[effect_id] = effect_data
            continue
        
        # Check if the effect has expired
        if current_time >= effect_data.get("expires_at", 0):
            # Effect has expired
            expired_effects.append({
                "effect_id": effect_id,
                "effect": effect_data["effect"],
                "target_id": effect_data["target_id"],
                "location_id": effect_data.get("location_id"),
                "expired_at": current_time
            })
        else:
            # Effect is still active
            updated_effects[effect_id] = effect_data
    
    # Update Redis with the remaining active effects
    redis_client.set("magic:active_effects", json.dumps(updated_effects))
    
    return expired_effects


@celery_app.task(name='magic.process_location_magic')
def process_location_magic_task(location_id: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process magical phenomena in a location.
    
    Args:
        location_id: ID of the location
        location_data: Data about the location
        
    Returns:
        Updated location magic information
    """
    # In a real implementation, we would process the location's magic
    # For now, we'll just simulate processing
    time.sleep(0.5)  # Simulate processing time
    
    # Calculate magical properties based on location data
    leyline_strength = min(5, location_data.get("leyline_base", 0) + 
                         (2 if "ley_nexus" in location_data.get("features", []) else 0))
    
    # Calculate mana flux level (0-5)
    mana_flux = min(5, location_data.get("mana_flux_base", 2) + 
                  (1 if location_data.get("recent_magic_use", 0) > 5 else 0) +
                  (2 if location_data.get("magical_instability", 0) > 3 else 0))
    
    # Determine dominant aspects
    dominant_aspects = []
    if location_data.get("environment") == "forest":
        dominant_aspects.append("EARTH")
    elif location_data.get("environment") == "mountain":
        dominant_aspects.extend(["EARTH", "AIR"])
    elif location_data.get("environment") == "coast":
        dominant_aspects.append("WATER")
    elif location_data.get("environment") == "desert":
        dominant_aspects.extend(["FIRE", "EARTH"])
    
    # Calculate environmental decay
    environmental_decay = location_data.get("corruption_level", 0)
    
    # Generate random magical events based on location properties
    random_events = []
    if leyline_strength >= 4 and mana_flux >= 3:
        random_events.append({
            "type": "leyline_surge",
            "description": "The leylines surge with magical energy",
            "duration_minutes": 30,
            "effects": ["Enhanced spell power", "Increased mana regeneration"]
        })
    
    # Store the processed magic data in Redis
    location_magic = {
        "location_id": location_id,
        "leyline_strength": leyline_strength,
        "mana_flux_level": mana_flux,
        "dominant_aspects": dominant_aspects,
        "environmental_decay": environmental_decay,
        "allows_rituals": leyline_strength >= 3 or "sacred_site" in location_data.get("features", []),
        "random_events": random_events,
        "processed_at": time.time()
    }
    redis_client.set(f"magic:location:{location_id}", json.dumps(location_magic))
    
    return location_magic


# ======================================================================
# Factory Functions
# ======================================================================

def create_magic_async_processor(magic_system: MagicSystem, 
                               consequence_system: MagicalConsequenceSystem) -> MagicAsyncProcessor:
    """
    Create and initialize a magic async processor.
    
    Args:
        magic_system: The magic system instance
        consequence_system: The magical consequence system
        
    Returns:
        Initialized magic async processor
    """
    return MagicAsyncProcessor(magic_system, consequence_system)