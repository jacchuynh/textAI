"""
Celery configuration for AI GM Brain tasks.

This module sets up the Celery application for handling asynchronous tasks
related to the AI GM Brain system.
"""

import os
from celery import Celery

# Get Redis URL from environment variable
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'ai_gm_brain',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'backend.src.ai_gm.tasks.llm_tasks',
        'backend.src.ai_gm.tasks.simulation_tasks',
        'backend.src.ai_gm.tasks.computation_tasks',
        'backend.src.ai_gm.tasks.maintenance_tasks',
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Task execution settings
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=300,  # 5 minutes soft limit
    # Retry settings
    task_acks_late=True,  # Tasks acknowledged after execution
    task_reject_on_worker_lost=True,  # Reject tasks when worker disconnects
)

# Route tasks to different queues based on priority
celery_app.conf.task_routes = {
    'backend.src.ai_gm.tasks.llm_tasks.*': {'queue': 'llm'},
    'backend.src.ai_gm.tasks.simulation_tasks.*': {'queue': 'simulation'},
    'backend.src.ai_gm.tasks.computation_tasks.*': {'queue': 'computation'},
    'backend.src.ai_gm.tasks.maintenance_tasks.*': {'queue': 'maintenance'},
}

# Optional: Configure the periodic task scheduler (Celery Beat)
celery_app.conf.beat_schedule = {
    'summarize-game-events-hourly': {
        'task': 'backend.src.ai_gm.tasks.maintenance_tasks.summarize_recent_events',
        'schedule': 3600.0,  # Every hour
        'args': ('default_session',),
    },
    'cleanup-old-data-daily': {
        'task': 'backend.src.ai_gm.tasks.maintenance_tasks.cleanup_old_game_data',
        'schedule': 86400.0,  # Every day
        'args': (30,),  # 30 days threshold
    },
    'ambient-world-updates': {
        'task': 'backend.src.ai_gm.tasks.simulation_tasks.update_ambient_world_state',
        'schedule': 900.0,  # Every 15 minutes
        'args': (),
    },
}