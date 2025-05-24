import os
from celery import Celery

# Get Redis URL from environment variable; provide a default for local development if not set
# Your AI agentic coding web app should be configured to set the REDIS_URL environment variable.
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Initialize Celery
# The first argument is the name of the current module, important for Celery's auto-discovery of tasks.
# You can also name it after your project, e.g., 'fantasy_rpg_celery'
celery_app = Celery(
    'app', # Or your project name
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.tasks']  # List of modules where Celery should look for tasks
)

# Optional Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # You might want to add more configurations, e.g., for task routing, rate limits, etc.
)

if __name__ == '__main__':
    celery_app.start()
