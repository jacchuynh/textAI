"""
Handler for Celery task results in the AI GM Brain system.

This module provides utilities for working with asynchronous Celery task
results and integrating them back into the AI GM Brain workflow.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

# Note: In a real implementation, would import this from Celery
# For now, we'll create a mock implementation for compatibility
class AsyncResult:
    """Mock AsyncResult for development without Celery installed."""
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.result = None
        self._ready = False
        self.logger = logging.getLogger("MockAsyncResult")
        
    def ready(self):
        """Check if the task is ready."""
        # In a real implementation, this would check the task status
        return self._ready
        
    def get(self, timeout=None):
        """Get the task result."""
        # In a real implementation, this would retrieve the actual result
        self.logger.info(f"Would get result for task {self.task_id} with timeout {timeout}")
        return self.result
        
    # For development/testing
    def set_ready(self, result):
        """Set the task as ready with a result (for testing)."""
        self._ready = True
        self.result = result

logger = logging.getLogger(__name__)

class TaskResultHandler:
    """Handler for Celery task results."""
    
    @staticmethod
    async def get_task_result(task_id: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get the result of a Celery task asynchronously.
        
        Args:
            task_id: The Celery task ID
            timeout: Optional timeout in seconds
            
        Returns:
            Task result or None if not ready or error
        """
        task = AsyncResult(task_id)
        
        if task.ready():
            try:
                return task.get(timeout=timeout)
            except Exception as e:
                logger.error(f"Error getting task result: {e}")
                return None
        
        return None
    
    @staticmethod
    async def wait_for_task_completion(task_id: str, max_wait: int = 30, check_interval: float = 0.5) -> Optional[Dict[str, Any]]:
        """
        Wait for a Celery task to complete.
        
        Args:
            task_id: The Celery task ID
            max_wait: Maximum time to wait in seconds
            check_interval: How often to check in seconds
            
        Returns:
            Task result or None if timeout or error
        """
        task = AsyncResult(task_id)
        waited = 0
        
        while not task.ready() and waited < max_wait:
            await asyncio.sleep(check_interval)
            waited += check_interval
        
        if task.ready():
            try:
                return task.get(timeout=5)
            except Exception as e:
                logger.error(f"Error getting task result: {e}")
                return None
        
        logger.warning(f"Task {task_id} did not complete within {max_wait} seconds")
        return None
    
    @staticmethod
    async def process_completed_tasks(task_ids: List[str], callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process multiple completed tasks and call callback if provided.
        
        Args:
            task_ids: List of task IDs to check
            callback: Optional callback function for each completed task
            
        Returns:
            Dict mapping task_id to result for completed tasks
        """
        completed_results = {}
        
        for task_id in task_ids:
            result = await TaskResultHandler.get_task_result(task_id)
            
            if result is not None:
                completed_results[task_id] = result
                
                if callback:
                    await callback(task_id, result)
        
        return completed_results
    
    @staticmethod
    async def apply_task_result_to_context(task_id: str, context: Dict[str, Any], result_key: str) -> Dict[str, Any]:
        """
        Apply a task result to a context dictionary.
        
        Args:
            task_id: The Celery task ID
            context: Context dictionary to update
            result_key: Key under which to store the result
            
        Returns:
            Updated context dictionary
        """
        result = await TaskResultHandler.get_task_result(task_id)
        
        if result is not None:
            # Create task results section if it doesn't exist
            if 'task_results' not in context:
                context['task_results'] = {}
                
            # Store the result under the specified key
            context['task_results'][result_key] = result
            
            # Add metadata about when the result was applied
            context['task_results']['last_updated'] = datetime.utcnow().isoformat()
        
        return context