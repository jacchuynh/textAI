"""
Celery integration for AI GM Brain.

This module provides methods to integrate the AI GM Brain with Celery
for asynchronous task processing.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from backend.src.ai_gm.tasks.result_handler import TaskResultHandler

# Import task modules
try:
    from backend.src.ai_gm.tasks import llm_tasks, simulation_tasks, computation_tasks, maintenance_tasks
    tasks_available = True
except ImportError:
    logging.warning("Celery task modules not available. Async operations will be simulated.")
    tasks_available = False

class AIGMCeleryIntegration:
    """Integration of Celery with AI GM Brain for asynchronous task processing."""
    
    def __init__(self):
        """Initialize the Celery integration."""
        self.logger = logging.getLogger("AIGMCeleryIntegration")
        self.pending_tasks = {}  # Track pending tasks by type
        self.task_result_handler = TaskResultHandler()
    
    async def process_llm_async(self, 
                              prompt: str, 
                              context: Optional[Dict[str, Any]] = None,
                              model: Optional[str] = None,
                              temperature: float = 0.7) -> Dict[str, Any]:
        """
        Process an LLM request asynchronously.
        
        Args:
            prompt: The text prompt to send to the LLM
            context: Additional context for the LLM
            model: Specific model to use (optional)
            temperature: Creativity parameter
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async LLM request: {prompt[:50]}...")
            
            if tasks_available:
                # Dispatch to Celery task
                task = llm_tasks.process_llm_request.delay(
                    prompt=prompt,
                    context=context,
                    model=model,
                    temperature=temperature
                )
                task_id = task.id
            else:
                # Mock task ID for development
                task_id = f"mock-llm-{datetime.utcnow().timestamp()}"
                self.logger.info(f"Created mock LLM task with ID: {task_id}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'llm_request',
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Store in pending tasks
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching LLM task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def generate_npc_dialogue_async(self, 
                                        npc_id: str, 
                                        dialogue_context: Dict[str, Any], 
                                        player_input: str) -> Dict[str, Any]:
        """
        Generate NPC dialogue asynchronously.
        
        Args:
            npc_id: Identifier for the NPC
            dialogue_context: Context for the dialogue generation
            player_input: What the player said
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async NPC dialogue task for NPC {npc_id}...")
            
            if tasks_available:
                # Dispatch to Celery task
                task = llm_tasks.generate_npc_dialogue.delay(
                    npc_id=npc_id,
                    dialogue_context=dialogue_context,
                    player_input=player_input
                )
                task_id = task.id
            else:
                # Mock task ID for development
                task_id = f"mock-dialogue-{npc_id}-{datetime.utcnow().timestamp()}"
                self.logger.info(f"Created mock NPC dialogue task with ID: {task_id}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'npc_dialogue',
                'npc_id': npc_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Store in pending tasks
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching NPC dialogue task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def process_world_reaction_async(self, 
                                         action_data: Dict[str, Any], 
                                         world_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process world reaction asynchronously.
        
        Args:
            action_data: Details of the player's action
            world_context: Current world state
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async world reaction task for action: {action_data.get('action_type', 'unknown')}...")
            
            if tasks_available:
                # Dispatch to Celery task
                task = simulation_tasks.process_world_reaction.delay(
                    action_data=action_data,
                    world_context=world_context
                )
                task_id = task.id
            else:
                # Mock task ID for development
                task_id = f"mock-world-reaction-{datetime.utcnow().timestamp()}"
                self.logger.info(f"Created mock world reaction task with ID: {task_id}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'world_reaction',
                'action_type': action_data.get('action_type', 'unknown'),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Store in pending tasks
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching world reaction task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def generate_ambient_content_async(self, 
                                          location: str, 
                                          time_of_day: str, 
                                          recent_events: List[str],
                                          mood: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate ambient content asynchronously.
        
        Args:
            location: The game location
            time_of_day: Current time of day
            recent_events: Recent events in the game
            mood: Optional mood/tone for the content
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async ambient content task for location: {location}...")
            
            if tasks_available:
                # Dispatch to Celery task
                task = simulation_tasks.generate_ambient_content.delay(
                    location=location,
                    time_of_day=time_of_day,
                    recent_events=recent_events,
                    mood=mood
                )
                task_id = task.id
            else:
                # Mock task ID for development
                task_id = f"mock-ambient-{location}-{datetime.utcnow().timestamp()}"
                self.logger.info(f"Created mock ambient content task with ID: {task_id}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'ambient_content',
                'location': location,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Store in pending tasks
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching ambient content task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def resolve_complex_combat_async(self, 
                                        combat_data: Dict[str, Any], 
                                        participants: List[Dict[str, Any]], 
                                        environment_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve complex combat asynchronously.
        
        Args:
            combat_data: Combat configuration and state
            participants: List of combatants
            environment_factors: Environmental effects on combat
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async combat resolution task with {len(participants)} participants...")
            
            if tasks_available:
                # Dispatch to Celery task
                task = computation_tasks.resolve_complex_combat.delay(
                    combat_data=combat_data,
                    participants=participants,
                    environment_factors=environment_factors
                )
                task_id = task.id
            else:
                # Mock task ID for development
                task_id = f"mock-combat-{datetime.utcnow().timestamp()}"
                self.logger.info(f"Created mock combat resolution task with ID: {task_id}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'combat_resolution',
                'combat_id': combat_data.get('id', 'unknown'),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Store in pending tasks
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching combat resolution task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def summarize_recent_events_async(self, 
                                         session_id: str, 
                                         time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Summarize recent events asynchronously.
        
        Args:
            session_id: The game session ID
            time_period: Optional time period to summarize (in hours)
            
        Returns:
            Task information including task_id
        """
        try:
            self.logger.info(f"Dispatching async event summarization task for session {session_id}...")
            
            if tasks_available:
                # Dispatch to Celery task
                task = maintenance_tasks.summarize_recent_events.delay(
                    session_id=session_id,
                    time_period=time_period
                )
                task_id = task.id
            else:
                # Mock task ID for development
                task_id = f"mock-summary-{session_id}-{datetime.utcnow().timestamp()}"
                self.logger.info(f"Created mock event summarization task with ID: {task_id}")
            
            # Track the pending task
            task_info = {
                'task_id': task_id,
                'type': 'event_summarization',
                'session_id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            # Store in pending tasks
            self.pending_tasks[task_id] = task_info
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"Error dispatching event summarization task: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    async def get_task_result(self, task_id: str, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get the result of a task.
        
        Args:
            task_id: The task ID
            timeout: Optional timeout in seconds
            
        Returns:
            Task result or None if not ready or error
        """
        return await TaskResultHandler.get_task_result(task_id, timeout)
    
    async def wait_for_task_completion(self, task_id: str, max_wait: int = 30) -> Optional[Dict[str, Any]]:
        """
        Wait for a task to complete.
        
        Args:
            task_id: The task ID
            max_wait: Maximum time to wait in seconds
            
        Returns:
            Task result or None if timeout or error
        """
        return await TaskResultHandler.wait_for_task_completion(task_id, max_wait)
    
    async def check_pending_tasks(self) -> Dict[str, Any]:
        """
        Check status of all pending tasks.
        
        Returns:
            Dictionary with task statuses
        """
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
            elif (datetime.utcnow() - datetime.fromisoformat(task_info['created_at'])) > timedelta(hours=1):
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