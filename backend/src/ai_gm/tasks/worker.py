"""
Worker configuration for Celery tasks.

This module sets up the Celery workers for running
AI GM Brain asynchronous tasks. It handles worker configuration
and startup parameters.
"""

import os
import logging
from backend.src.ai_gm.tasks.celery_app import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("celery_worker")

# Set Celery worker configuration
worker_config = {
    # General settings
    'loglevel': os.environ.get('CELERY_LOG_LEVEL', 'INFO'),
    'concurrency': int(os.environ.get('CELERY_CONCURRENCY', 4)),
    'prefetch_multiplier': 1,  # Prefetch one task at a time
    'max_tasks_per_child': 100,  # Worker process recycled after 100 tasks
    'task_time_limit': 300,  # 5 minute max task execution time
    'task_soft_time_limit': 240,  # 4 minute warning before hard limit
    
    # Queue configuration for priority processing
    'queues': 'high_priority,medium_priority,low_priority',
    
    # Enable events for monitoring
    'events': True,
}

def start_worker():
    """
    Start the Celery worker with appropriate configuration.
    This function is used when running the worker directly.
    """
    logger.info("Starting Celery worker for AI GM Brain tasks...")
    
    # Build worker arguments
    worker_args = []
    for key, value in worker_config.items():
        worker_args.append(f"--{key}={value}")
    
    # Start the worker
    celery_app.worker_main(argv=['worker'] + worker_args)

if __name__ == '__main__':
    start_worker()