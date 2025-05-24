"""
Celery application configuration for AI GM Brain.

This module sets up the Celery application and configuration for the
asynchronous task processing system.
"""

import os
import logging
from typing import Dict, Any

# Import Celery
try:
    from celery import Celery
    celery_available = True
except ImportError:
    logging.warning("Celery not installed. Using mock Celery implementation for development.")
    celery_available = False
    
    # Create a mock Celery class for development without Celery installed
    class MockCelery:
        """Mock Celery for development without Celery installed."""
        
        def __init__(self, *args, **kwargs):
            self.tasks = {}
            self.logger = logging.getLogger("MockCelery")
            self.logger.info("MockCelery initialized")
            
        def task(self, *args, **kwargs):
            """Mock task decorator."""
            def decorator(func):
                self.tasks[func.__name__] = func
                return func
            return decorator
            
        def conf(self, *args, **kwargs):
            """Mock configuration."""
            return {}
            
    # Create a mock Celery instance
    Celery = MockCelery

# Configure logger
logger = logging.getLogger(__name__)

# Determine if we're running in development or production
is_development = os.environ.get('ENVIRONMENT', 'development') == 'development'

# Configure Redis connection if available
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery application
if celery_available:
    celery_app = Celery(
        'ai_gm_tasks',
        broker=redis_url,
        backend=redis_url,
        include=[
            'backend.src.ai_gm.tasks.llm_tasks',
            'backend.src.ai_gm.tasks.simulation_tasks',
            'backend.src.ai_gm.tasks.computation_tasks',
            'backend.src.ai_gm.tasks.maintenance_tasks'
        ]
    )
    
    # Configure Celery
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        task_track_started=True,
        worker_prefetch_multiplier=1,
        result_expires=3600,  # Results expire after 1 hour
    )
    
    # Configure task routing by priority
    celery_app.conf.task_routes = {
        'backend.src.ai_gm.tasks.llm_tasks.*': {'queue': 'high_priority'},
        'backend.src.ai_gm.tasks.simulation_tasks.*': {'queue': 'medium_priority'},
        'backend.src.ai_gm.tasks.computation_tasks.*': {'queue': 'medium_priority'},
        'backend.src.ai_gm.tasks.maintenance_tasks.*': {'queue': 'low_priority'}
    }
    
    # Configure task timeouts
    celery_app.conf.task_time_limit = 300  # 5 minutes max
    celery_app.conf.task_soft_time_limit = 240  # 4 minutes warning
    
    logger.info("Celery application configured with Redis broker")
else:
    # Create a mock Celery application for development
    celery_app = Celery()
    logger.warning("Using mock Celery implementation")

# Define test task to verify Celery operation
@celery_app.task(bind=True)
def test_celery(self):
    """
    Test task to verify Celery operation.
    
    Returns:
        Test message
    """
    return {
        'status': 'success',
        'message': 'Celery is working correctly'
    }