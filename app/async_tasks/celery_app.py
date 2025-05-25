"""
Celery Application Configuration

This module configures the Celery application for asynchronous task processing.
It sets up the broker, backend, and task routes.
"""

from celery import Celery
import os

# Celery broker URL (Redis)
# In production, you would use environment variables for these settings
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')

# Create Celery app
celery_app = Celery(
    'time_system',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    include=['app.async_tasks.time_tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.async_tasks.time_tasks.*': {'queue': 'time_queue'},
    },
    task_time_limit=300,  # 5 minutes timeout
    task_soft_time_limit=240,  # 4 minutes soft timeout
)

# Optional: Define task priority
celery_app.conf.task_queue_max_priority = 10
celery_app.conf.task_default_priority = 5

if __name__ == '__main__':
    celery_app.start()