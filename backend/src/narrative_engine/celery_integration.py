"""
Narrative Engine Celery Integration

This module provides a high-level interface for integrating the narrative engine
with Celery for asynchronous task processing. It connects narrative engine components
with the task queue system to enable background processing of resource-intensive operations.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime
import asyncio

# Import task definitions
from backend.src.narrative_engine.tasks import (
    generate_combat_narrative,
    generate_npc_dialogue,
    generate_narrative_branch,
    update_world_state,
    update_relationship_network,
    process_event_queue
)

logger = logging.getLogger(__name__)

class NarrativeEngineCeleryIntegration:
    """
    Integration class connecting the narrative engine with Celery for asynchronous processing.
    
    This class provides methods for dispatching narrative engine tasks to Celery workers
    and retrieving results when they're complete.
    """
    
    def __init__(self):
        """Initialize the Celery integration for the narrative engine."""
        self.logger = logging.getLogger("NarrativeEngineCelery")
        self.pending_tasks = {}  # Track pending tasks
        
        # Try to import result handler
        try:
            from backend.src.ai_gm.tasks.result_handler import TaskResultHandler
            self.task_result_handler = TaskResultHandler()
            self.result_handler_available = True
        except ImportError:
            self.logger.warning("TaskResultHandler not available. Results will need to be checked manually.")
            self.result_handler_available = False
    
    async def generate_combat_narrative_async(self,
                                           combat_result: Dict[str, Any],
                                           actor: Dict[str, Any],
                                           target: Dict[str, Any],
                                           environment_tags: List[str],
                                           memory_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a combat narrative asynchronously using Celery.
        
        Args:
            combat_result: The result of the combat calculation
            actor: The character performing the action
            target: The target of the action
            environment_tags: Environmental factors affecting the combat
            memory_context: Optional historical context between combatants
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async combat narrative generation for {actor.get('name', 'unknown')} vs {target.get('name', 'unknown')}...")
            
            # Dispatch to Celery task
            task = generate_combat_narrative.delay(
                combat_result=combat_result,
                actor=actor,
                target=target,
                environment_tags=environment_tags,
                memory_context=memory_context
            )
            
            # Mock task ID if task.id isn't available (for development)
            task_id = getattr(task, 'id', f"mock-narrative-{datetime.utcnow().timestamp()}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'combat_narrative',
                'combat_id': combat_result.get('id', 'unknown'),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching combat narrative task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def generate_npc_dialogue_async(self,
                                       npc_data: Dict[str, Any],
                                       dialogue_context: Dict[str, Any],
                                       player_input: str) -> Dict[str, Any]:
        """
        Generate NPC dialogue asynchronously using Celery.
        
        Args:
            npc_data: Data about the NPC
            dialogue_context: Context for the dialogue
            player_input: Player's input or question
            
        Returns:
            Task information including task_id
        """
        try:
            npc_id = npc_data.get('id', 'unknown')
            self.logger.info(f"Dispatching async dialogue generation for NPC {npc_id}...")
            
            # Dispatch to Celery task
            task = generate_npc_dialogue.delay(
                npc_data=npc_data,
                dialogue_context=dialogue_context,
                player_input=player_input
            )
            
            # Mock task ID if task.id isn't available (for development)
            task_id = getattr(task, 'id', f"mock-dialogue-{npc_id}-{datetime.utcnow().timestamp()}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'npc_dialogue',
                'npc_id': npc_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching NPC dialogue task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def generate_narrative_branch_async(self,
                                          branch_point_id: str,
                                          context: Dict[str, Any],
                                          character_data: Dict[str, Any],
                                          available_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate narrative branch options asynchronously using Celery.
        
        Args:
            branch_point_id: Identifier for the narrative branch point
            context: Current narrative context
            character_data: Player character data affecting choices
            available_options: Pre-defined available options
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async narrative branch generation for point {branch_point_id}...")
            
            # Dispatch to Celery task
            task = generate_narrative_branch.delay(
                branch_point_id=branch_point_id,
                context=context,
                character_data=character_data,
                available_options=available_options
            )
            
            # Mock task ID if task.id isn't available (for development)
            task_id = getattr(task, 'id', f"mock-branch-{branch_point_id}-{datetime.utcnow().timestamp()}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'narrative_branch',
                'branch_point_id': branch_point_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching narrative branch task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def update_world_state_async(self,
                                    world_data: Dict[str, Any],
                                    events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update world state asynchronously using Celery.
        
        Args:
            world_data: Current world state data
            events: List of events that affect the world
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async world state update with {len(events)} events...")
            
            # Dispatch to Celery task
            task = update_world_state.delay(
                world_data=world_data,
                events=events
            )
            
            # Mock task ID if task.id isn't available (for development)
            task_id = getattr(task, 'id', f"mock-world-update-{datetime.utcnow().timestamp()}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'world_update',
                'events_count': len(events),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching world state update task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def update_relationship_network_async(self,
                                             character_id: str,
                                             action_data: Dict[str, Any],
                                             affected_npcs: List[str]) -> Dict[str, Any]:
        """
        Update relationship network asynchronously using Celery.
        
        Args:
            character_id: Identifier for the character
            action_data: Details of the character's action
            affected_npcs: NPCs affected by the action
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async relationship network update for character {character_id}...")
            
            # Dispatch to Celery task
            task = update_relationship_network.delay(
                character_id=character_id,
                action_data=action_data,
                affected_npcs=affected_npcs
            )
            
            # Mock task ID if task.id isn't available (for development)
            task_id = getattr(task, 'id', f"mock-relationship-{character_id}-{datetime.utcnow().timestamp()}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'relationship_update',
                'character_id': character_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching relationship network update task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def process_event_queue_async(self,
                                     event_queue: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process event queue asynchronously using Celery.
        
        Args:
            event_queue: List of events to process
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async event queue processing with {len(event_queue)} events...")
            
            # Dispatch to Celery task
            task = process_event_queue.delay(
                event_queue=event_queue
            )
            
            # Mock task ID if task.id isn't available (for development)
            task_id = getattr(task, 'id', f"mock-event-queue-{datetime.utcnow().timestamp()}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'event_queue',
                'events_count': len(event_queue),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching event queue processing task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a specific task.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task result or None if not ready or error
        """
        if not self.result_handler_available:
            self.logger.warning(f"TaskResultHandler not available. Cannot retrieve result for task {task_id}.")
            return None
            
        try:
            return await self.task_result_handler.get_task_result(task_id)
        except Exception as e:
            self.logger.error(f"Error getting task result: {e}")
            return None
    
    async def wait_for_task_completion(self, task_id: str, max_wait: int = 30) -> Optional[Dict[str, Any]]:
        """
        Wait for a task to complete.
        
        Args:
            task_id: The task ID
            max_wait: Maximum time to wait in seconds
            
        Returns:
            Task result or None if timeout or error
        """
        if not self.result_handler_available:
            self.logger.warning(f"TaskResultHandler not available. Cannot wait for completion of task {task_id}.")
            return None
            
        try:
            return await self.task_result_handler.wait_for_task_completion(task_id, max_wait)
        except Exception as e:
            self.logger.error(f"Error waiting for task completion: {e}")
            return None
    
    async def check_pending_tasks(self) -> Dict[str, Any]:
        """
        Check status of all pending tasks.
        
        Returns:
            Dictionary with task statuses
        """
        if not self.result_handler_available:
            return {
                'error': 'TaskResultHandler not available. Cannot check pending tasks.',
                'pending_count': len(self.pending_tasks)
            }
            
        task_statuses = {
            'completed': [],
            'pending': [],
            'failed': []
        }
        
        for task_id, task_info in list(self.pending_tasks.items()):
            result = await self.get_task_result(task_id)
            
            if result is not None:
                # Task completed
                task_info['status'] = 'completed'
                task_info['completed_at'] = datetime.utcnow().isoformat()
                task_statuses['completed'].append(task_id)
                
                # Remove from pending tasks
                self.pending_tasks.pop(task_id, None)
            elif (datetime.utcnow() - datetime.fromisoformat(task_info['created_at'])).total_seconds() > 3600:
                # Task timed out (1 hour is a generous timeout)
                task_info['status'] = 'failed'
                task_info['error'] = 'Task timed out'
                task_statuses['failed'].append(task_id)
                
                # Remove from pending tasks
                self.pending_tasks.pop(task_id, None)
            else:
                # Task still pending
                task_statuses['pending'].append(task_id)
        
        return {
            'completed_count': len(task_statuses['completed']),
            'pending_count': len(task_statuses['pending']),
            'failed_count': len(task_statuses['failed']),
            'completed_tasks': task_statuses['completed'],
            'pending_tasks': task_statuses['pending'],
            'failed_tasks': task_statuses['failed']
        }
    
    async def dispatch_custom_task(self, 
                                task_name: str, 
                                task_args: List[Any] = None,
                                task_kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Dispatch a custom Celery task by name.
        
        This allows other systems (like the economy system) to use the
        Celery integration for their own tasks.
        
        Args:
            task_name: Full import path to the task function
            task_args: Positional arguments for the task
            task_kwargs: Keyword arguments for the task
            
        Returns:
            Task information
        """
        self.logger.info(f"Dispatching custom task: {task_name}")
        
        task_args = task_args or []
        task_kwargs = task_kwargs or {}
        
        try:
            # Import the task module dynamically
            module_path, task_func = task_name.rsplit('.', 1)
            
            try:
                module = __import__(module_path, fromlist=[task_func])
                task = getattr(module, task_func)
                
                # Call the task's delay method
                result = task.delay(*task_args, **task_kwargs)
                
                # Get task ID
                task_id = getattr(result, 'id', f"mock-task-{datetime.utcnow().timestamp()}")
                
                # Track the pending task
                task_info = {
                    'task_id': task_id,
                    'task_name': task_name,
                    'created_at': datetime.utcnow().isoformat(),
                    'status': 'pending'
                }
                
                self.pending_tasks[task_id] = task_info
                
                return {
                    'task_id': task_id,
                    'task_name': task_name,
                    'status': 'dispatched',
                    'timestamp': datetime.utcnow().isoformat()
                }
            except (ImportError, AttributeError) as e:
                self.logger.error(f"Error importing task {task_name}: {e}")
                
                # Fall back to mock task ID for development
                mock_task_id = f"mock-task-{datetime.utcnow().timestamp()}"
                
                # Track as a pending task even in mock mode
                self.pending_tasks[mock_task_id] = {
                    'task_id': mock_task_id,
                    'task_name': task_name,
                    'created_at': datetime.utcnow().isoformat(),
                    'status': 'mock_pending'
                }
                
                return {
                    'task_id': mock_task_id,
                    'task_name': task_name,
                    'status': 'mock_dispatched',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error dispatching custom task: {e}")
            return {
                'error': str(e),
                'task_name': task_name,
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }