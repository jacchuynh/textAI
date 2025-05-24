"""
Narrative Engine Service

This module provides a high-level service interface for interacting with
the narrative engine. It integrates all the narrative components and
provides methods for generating narratives, updating world state, and
managing game flow.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import json
import asyncio
from datetime import datetime

from backend.src.narrative_engine.narrative_generator import NarrativeDirector, CombatNarrativeGenerator
from backend.src.narrative_engine.narrative_context_manager import NarrativeContextManager, NarrativeContext
from backend.src.narrative_engine.world_state import WorldStateManager, WorldState
from backend.src.narrative_engine.event_bus import get_event_bus, Event
from backend.src.narrative_engine.template_processor import get_template_processor
from backend.src.narrative_engine.narrative_pacing import get_pacing_manager
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration

logger = logging.getLogger(__name__)

class NarrativeService:
    """
    Service for interacting with the narrative engine.
    
    Provides a high-level interface for generating narratives, updating
    world state, and managing game flow.
    """
    
    def __init__(self, storage_service=None):
        """
        Initialize the narrative service.
        
        Args:
            storage_service: Optional service for persisting data
        """
        self.logger = logging.getLogger("NarrativeService")
        
        # Initialize component managers
        self.context_manager = NarrativeContextManager(storage_service)
        self.world_manager = WorldStateManager(storage_service)
        self.narrative_director = NarrativeDirector()
        self.template_processor = get_template_processor()
        self.pacing_manager = get_pacing_manager()
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration
        self.celery_integration = NarrativeEngineCeleryIntegration()
        
        # Connect Celery integration with event bus
        self.event_bus.set_celery_integration(self.celery_integration)
        
        # Set up event handlers
        self.event_bus.subscribe("player_action", self._handle_player_action)
        self.event_bus.subscribe("combat_result", self._handle_combat_result)
        self.event_bus.subscribe("world_change", self._handle_world_change)
        
        self.logger.info("Narrative service initialized")
    
    async def create_game_session(self, session_id: str = None) -> Dict[str, str]:
        """
        Create a new game session with narrative context and world state.
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            Session information
        """
        # Create narrative context
        context = self.context_manager.create_context(session_id)
        
        # Create world state with same ID for consistency
        world = self.world_manager.create_world(context.id)
        
        # Log creation
        self.logger.info(f"Created new game session: {context.id}")
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="session_created",
            data={
                "session_id": context.id,
                "created_at": context.created_at
            },
            source="narrative_service"
        ))
        
        return {
            "session_id": context.id,
            "context_id": context.id,
            "world_id": world.id,
            "created_at": context.created_at
        }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a game session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information
        """
        # Get narrative context
        context = self.context_manager.get_context(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}
            
        # Get world state
        world = self.world_manager.get_world(session_id)
        
        # Get summary information
        context_summary = self.context_manager.get_context_summary(session_id)
        
        # Get pacing information
        pacing_state = self.pacing_manager.get_pacing_state()
        
        return {
            "session_id": session_id,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
            "context_summary": context_summary,
            "pacing_state": pacing_state,
            "world_version": world.version if world else None
        }
    
    async def generate_combat_narrative(self,
                                     session_id: str,
                                     combat_result: Dict[str, Any],
                                     actor: Dict[str, Any],
                                     target: Dict[str, Any],
                                     environment_tags: List[str],
                                     async_processing: bool = True) -> Dict[str, Any]:
        """
        Generate a narrative for a combat encounter.
        
        Args:
            session_id: Session identifier
            combat_result: Result of the combat
            actor: Character performing the action
            target: Target of the action
            environment_tags: Environmental factors
            async_processing: Whether to process asynchronously
            
        Returns:
            Generated narrative or task information
        """
        # Get narrative context for memory
        context = self.context_manager.get_context(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}
            
        # Prepare memory context
        memory_context = self._prepare_memory_context(context, actor, target)
        
        # Generate narrative with director
        result = await self.narrative_director.generate_combat_narrative(
            combat_result=combat_result,
            actor=actor,
            target=target,
            environment_tags=environment_tags,
            memory_context=memory_context,
            async_processing=async_processing
        )
        
        # Record the narrative in context if synchronous
        if not async_processing and isinstance(result, dict) and "dialogue" not in result:
            self._record_combat_narrative(context.id, combat_result, result)
            
        return result
    
    async def generate_npc_dialogue(self,
                                 session_id: str,
                                 npc_data: Dict[str, Any],
                                 player_input: str,
                                 async_processing: bool = True) -> Dict[str, Any]:
        """
        Generate dialogue for an NPC.
        
        Args:
            session_id: Session identifier
            npc_data: Data about the NPC
            player_input: Player's input or question
            async_processing: Whether to process asynchronously
            
        Returns:
            Generated dialogue or task information
        """
        # Get narrative context for dialogue context
        context = self.context_manager.get_context(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}
            
        # Get world state for additional context
        world = self.world_manager.get_world(session_id)
        
        # Prepare dialogue context
        dialogue_context = self._prepare_dialogue_context(context, npc_data, world)
        
        # Generate dialogue with director
        result = await self.narrative_director.generate_npc_dialogue(
            npc_data=npc_data,
            dialogue_context=dialogue_context,
            player_input=player_input,
            async_processing=async_processing
        )
        
        # Record the dialogue in context if synchronous
        if not async_processing and isinstance(result, dict) and "dialogue" in result:
            self._record_dialogue(context.id, npc_data, player_input, result)
            
        return result
    
    async def generate_narrative_branch(self,
                                     session_id: str,
                                     branch_point_id: str,
                                     available_options: List[Dict[str, Any]],
                                     async_processing: bool = True) -> Dict[str, Any]:
        """
        Generate narrative branch options for a choice point.
        
        Args:
            session_id: Session identifier
            branch_point_id: Identifier for the branch point
            available_options: Available options for the branch
            async_processing: Whether to process asynchronously
            
        Returns:
            Enhanced narrative branch or task information
        """
        # Get narrative context
        context = self.context_manager.get_context(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}
            
        # Get character data from context
        character_data = context.characters.get("player", {})
        
        # Prepare branch context
        branch_context = {
            "session_id": session_id,
            "branch_point_id": branch_point_id,
            "summary": "Player making a choice at narrative branch point",
            "tension_level": self.pacing_manager.tension_level,
            "recent_events": self.context_manager.get_recent_events(session_id, 5)
        }
        
        # Use Celery task for branch generation
        if async_processing and self.celery_integration:
            return await self.celery_integration.generate_narrative_branch_async(
                branch_point_id=branch_point_id,
                context=branch_context,
                character_data=character_data,
                available_options=available_options
            )
        
        # Generate branch options with character-specific outcomes
        enhanced_options = []
        
        for option in available_options:
            # Enhance each option with more detailed description and consequences
            option_id = option.get('id', 'unknown')
            option_text = option.get('text', 'Make a choice')
            
            # Calculate character-specific outcomes
            character_domains = character_data.get('domains', {})
            primary_domain = max(character_domains.items(), key=lambda x: x[1])[0] if character_domains else "Unknown"
            
            # Determine success chance based on character domains
            relevant_domain = option.get('relevant_domain')
            success_chance = 0.5  # Default
            if relevant_domain and relevant_domain in character_domains:
                domain_value = character_domains[relevant_domain]
                success_chance = min(0.9, 0.4 + (domain_value / 100))
            
            enhanced_options.append({
                'id': option_id,
                'text': option_text,
                'enhanced_description': f"{option_text} This choice will test your {relevant_domain or 'abilities'}.",
                'predicted_outcome': f"Your {primary_domain} expertise may influence the outcome.",
                'success_chance': success_chance,
                'consequence_preview': option.get('consequence_preview', 'This choice will have consequences.')
            })
        
        return {
            'branch_point_id': branch_point_id,
            'enhanced_options': enhanced_options,
            'context_summary': "Current narrative context: " + branch_context.get('summary', 'In progress'),
            'character_domains_analysis': f"Your {primary_domain} expertise will be particularly valuable in this situation.",
        }
    
    async def process_player_choice(self,
                                 session_id: str,
                                 branch_point_id: str,
                                 choice_id: str) -> Dict[str, Any]:
        """
        Process a player's choice at a narrative branch point.
        
        Args:
            session_id: Session identifier
            branch_point_id: Identifier for the branch point
            choice_id: Identifier for the chosen option
            
        Returns:
            Result of the choice
        """
        # Get narrative context
        context = self.context_manager.get_context(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}
            
        # Record the choice
        context.add_player_choice({
            "branch_point_id": branch_point_id,
            "choice_id": choice_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update narrative arc position
        self.pacing_manager.advance_narrative_arc(0.05)
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="player_choice",
            data={
                "session_id": session_id,
                "branch_point_id": branch_point_id,
                "choice_id": choice_id
            },
            source="narrative_service"
        ))
        
        # Return result
        return {
            "status": "choice_processed",
            "branch_point_id": branch_point_id,
            "choice_id": choice_id,
            "next_steps": ["Continue the narrative", "Begin next scene", "Update world state"]
        }
    
    async def update_world_state(self,
                              session_id: str,
                              events: List[Dict[str, Any]],
                              async_processing: bool = True) -> Dict[str, Any]:
        """
        Update the world state based on events.
        
        Args:
            session_id: Session identifier
            events: List of events affecting the world
            async_processing: Whether to process asynchronously
            
        Returns:
            Updated world state or task information
        """
        # Get world state
        world = self.world_manager.get_world(session_id)
        if not world:
            return {"error": f"World for session {session_id} not found"}
            
        # Use Celery task for world update
        if async_processing and self.celery_integration:
            return await self.celery_integration.update_world_state_async(
                world_data=world.to_dict(),
                events=events
            )
        
        # Process events to update world
        for event in events:
            event_type = event.get("type", "unknown")
            
            if event_type == "location_update":
                location_id = event.get("location_id")
                location_data = event.get("data", {})
                
                if location_id:
                    if location_id in world.locations:
                        world.update_location(location_id, location_data)
                    else:
                        world.add_location(location_id, location_data)
                        
            elif event_type == "npc_update":
                npc_id = event.get("npc_id")
                npc_data = event.get("data", {})
                
                if npc_id:
                    if npc_id in world.npcs:
                        world.update_npc(npc_id, npc_data)
                    else:
                        world.add_npc(npc_id, npc_data)
                        
            elif event_type == "faction_update":
                faction_id = event.get("faction_id")
                faction_data = event.get("data", {})
                
                if faction_id:
                    if faction_id in world.factions:
                        world.update_faction(faction_id, faction_data)
                    else:
                        world.add_faction(faction_id, faction_data)
                        
            elif event_type == "faction_relation":
                faction1_id = event.get("faction1_id")
                faction2_id = event.get("faction2_id")
                relation_value = event.get("value", 0)
                
                if faction1_id and faction2_id:
                    world.set_faction_relationship(faction1_id, faction2_id, relation_value)
                    
            elif event_type == "global_event":
                world.add_global_event(event)
                
            elif event_type == "active_event":
                world.add_active_event(event)
                
            elif event_type == "time_update":
                time_value = event.get("time", 0)
                if isinstance(time_value, (int, float)) and time_value > 0:
                    world.update_time(time_value)
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="world_updated",
            data={
                "session_id": session_id,
                "events_processed": len(events),
                "world_version": world.version
            },
            source="narrative_service"
        ))
        
        return {
            "status": "world_updated",
            "session_id": session_id,
            "events_processed": len(events),
            "world_version": world.version
        }
    
    async def update_relationship_network(self,
                                       session_id: str,
                                       character_id: str,
                                       action_data: Dict[str, Any],
                                       affected_npcs: List[str],
                                       async_processing: bool = True) -> Dict[str, Any]:
        """
        Update relationship network based on character actions.
        
        Args:
            session_id: Session identifier
            character_id: Character identifier
            action_data: Details of the character's action
            affected_npcs: NPCs affected by the action
            async_processing: Whether to process asynchronously
            
        Returns:
            Updated relationship information or task information
        """
        # Get narrative context
        context = self.context_manager.get_context(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}
            
        # Use Celery task for relationship update
        if async_processing and self.celery_integration:
            return await self.celery_integration.update_relationship_network_async(
                character_id=character_id,
                action_data=action_data,
                affected_npcs=affected_npcs
            )
        
        # Calculate relationship changes
        relationship_changes = {}
        
        action_type = action_data.get("type", "unknown")
        action_target = action_data.get("target", "unknown")
        
        # Different impact based on action type
        for npc_id in affected_npcs:
            if action_type == "help":
                relationship_changes[npc_id] = 10
            elif action_type == "harm":
                relationship_changes[npc_id] = -15
            elif action_type == "trade":
                relationship_changes[npc_id] = 5
            elif action_type == "steal":
                relationship_changes[npc_id] = -20
            else:
                relationship_changes[npc_id] = 0
        
        # Update relationships in context
        for npc_id, change in relationship_changes.items():
            # Get current relationship value
            current_relationship = context.get_relationship(character_id, npc_id)
            current_value = current_relationship.get("value", 0) if current_relationship else 0
            
            # Update relationship
            context.update_relationship(character_id, npc_id, {
                "value": current_value + change,
                "last_interaction": action_type,
                "last_interaction_time": datetime.utcnow().isoformat()
            })
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="relationships_updated",
            data={
                "session_id": session_id,
                "character_id": character_id,
                "action_type": action_type,
                "affected_npcs": affected_npcs
            },
            source="narrative_service"
        ))
        
        return {
            "status": "relationships_updated",
            "character_id": character_id,
            "relationship_changes": relationship_changes
        }
    
    async def process_narrative_template(self,
                                      session_id: str,
                                      template_key: str,
                                      variables: Dict[str, Any] = None,
                                      async_processing: bool = True) -> Dict[str, Any]:
        """
        Process a narrative template with variables.
        
        Args:
            session_id: Session identifier
            template_key: Template key
            variables: Variables to substitute
            async_processing: Whether to process asynchronously
            
        Returns:
            Processed template or task information
        """
        variables = variables or {}
        
        # Get narrative context for additional variables
        context = self.context_manager.get_context(session_id)
        if context:
            # Add context variables
            variables.update({
                "session_id": session_id,
                "tension_level": self.pacing_manager.tension_level,
                "pacing_mode": self.pacing_manager.pacing_mode
            })
            
            # Add player character if available
            if "player" in context.characters:
                variables["player"] = context.characters["player"]
        
        # Get template
        template_data = {
            "template": self.template_processor.get_cached_template(template_key)
        }
        
        if not template_data["template"]:
            return {"error": f"Template {template_key} not found"}
        
        # Use Celery task for template processing
        if async_processing and self.celery_integration:
            return await self.celery_integration.process_narrative_templates(
                template_key=template_key,
                template_data=template_data,
                variables=variables
            )
        
        # Process template
        processed_content = self.template_processor.process_template(
            template_data["template"],
            variables
        )
        
        return {
            "template_key": template_key,
            "processed_content": processed_content,
            "variables_used": list(variables.keys())
        }
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of an asynchronous task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status information
        """
        if not self.celery_integration:
            return {"error": "Celery integration not available"}
            
        result = await self.celery_integration.get_task_result(task_id)
        
        if result is not None:
            # If this was a combat narrative task, record it
            if isinstance(result, dict) and "narrative" in result and "combat_id" in result:
                # Extract the combat result and narrative
                combat_id = result.get("combat_id")
                narrative = result.get("narrative", {})
                
                # Find an active session
                # In a real implementation, you'd track which session this task belongs to
                # For now, we'll just use the first active session
                active_contexts = list(self.context_manager.active_contexts.values())
                if active_contexts:
                    context_id = active_contexts[0].id
                    self._record_combat_narrative(context_id, {"id": combat_id}, narrative)
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result
            }
        else:
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Task still processing or not found"
            }
    
    async def wait_for_task_completion(self, task_id: str, max_wait: int = 30) -> Dict[str, Any]:
        """
        Wait for an asynchronous task to complete.
        
        Args:
            task_id: Task identifier
            max_wait: Maximum time to wait in seconds
            
        Returns:
            Task result or timeout information
        """
        if not self.celery_integration:
            return {"error": "Celery integration not available"}
            
        result = await self.celery_integration.wait_for_task_completion(task_id, max_wait)
        
        if result is not None:
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result
            }
        else:
            return {
                "task_id": task_id,
                "status": "timeout",
                "message": f"Task did not complete within {max_wait} seconds"
            }
    
    def _prepare_memory_context(self, 
                              context: NarrativeContext, 
                              actor: Dict[str, Any], 
                              target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare memory context for narrative generation.
        
        Args:
            context: Narrative context
            actor: Actor character
            target: Target character
            
        Returns:
            Memory context
        """
        memory_context = {
            "current_opponent_name": target.get("name", "unknown"),
            "opponent_records": {}
        }
        
        # Get previous encounters from significant moments
        target_name = target.get("name", "unknown")
        actor_name = actor.get("name", "unknown")
        
        encounters = 0
        victories = 0
        defeats = 0
        narrative_moments = []
        
        for moment in context.significant_moments:
            if moment.get("type") == "combat" and moment.get("participants") == [actor_name, target_name]:
                encounters += 1
                
                if moment.get("result") == "victory" and moment.get("victor") == actor_name:
                    victories += 1
                elif moment.get("result") == "defeat" or moment.get("victor") == target_name:
                    defeats += 1
                    
                narrative_moments.append(moment)
        
        # Add opponent record
        memory_context["opponent_records"][target_name] = {
            "encounters": encounters,
            "victories": victories,
            "defeats": defeats,
            "narrative_moments": narrative_moments
        }
        
        # Add most effective moves
        # In a real implementation, this would be extracted from combat history
        memory_context["most_effective_moves"] = [
            {"name": "Quick Strike", "success_rate": 0.8},
            {"name": "Power Attack", "success_rate": 0.7}
        ]
        
        return memory_context
    
    def _prepare_dialogue_context(self, 
                                context: NarrativeContext, 
                                npc_data: Dict[str, Any],
                                world: Optional[WorldState]) -> Dict[str, Any]:
        """
        Prepare dialogue context for NPC interactions.
        
        Args:
            context: Narrative context
            npc_data: NPC data
            world: World state
            
        Returns:
            Dialogue context
        """
        npc_id = npc_data.get("id", "unknown")
        
        dialogue_context = {
            "relationship": "neutral",
            "recent_interactions": [],
            "world_events": [],
            "tension_level": self.pacing_manager.tension_level,
            "pacing_mode": self.pacing_manager.pacing_mode
        }
        
        # Get relationship if available
        if "player" in context.characters:
            player_id = "player"
            relationship = context.get_relationship(player_id, npc_id)
            
            if relationship:
                value = relationship.get("value", 0)
                
                if value > 50:
                    dialogue_context["relationship"] = "friendly"
                elif value > 20:
                    dialogue_context["relationship"] = "positive"
                elif value < -50:
                    dialogue_context["relationship"] = "hostile"
                elif value < -20:
                    dialogue_context["relationship"] = "negative"
        
        # Get recent interactions
        recent_events = self.context_manager.get_recent_events(context.id, 10)
        
        for event in recent_events:
            if event.get("type") == "dialogue" and event.get("npc_id") == npc_id:
                dialogue_context["recent_interactions"].append(event)
            elif event.get("type") == "global_event":
                dialogue_context["world_events"].append(event)
        
        # Add faction information if available
        if world and npc_data.get("faction_id") in world.factions:
            faction_id = npc_data.get("faction_id")
            dialogue_context["faction"] = world.factions[faction_id]
            
            # Add faction relationships
            dialogue_context["faction_relationships"] = {}
            
            for other_faction_id in world.factions:
                if other_faction_id != faction_id:
                    relation = world.get_faction_relationship(faction_id, other_faction_id)
                    dialogue_context["faction_relationships"][other_faction_id] = relation
        
        return dialogue_context
    
    def _record_combat_narrative(self, 
                               context_id: str, 
                               combat_result: Dict[str, Any], 
                               narrative: Dict[str, str]) -> None:
        """
        Record a combat narrative in the context.
        
        Args:
            context_id: Context identifier
            combat_result: Combat result data
            narrative: Generated narrative
        """
        # Add a significant moment for the combat
        def add_moment(context):
            context.add_significant_moment({
                "type": "combat",
                "combat_id": combat_result.get("id", "unknown"),
                "description": narrative.get("action_description", ""),
                "environment": narrative.get("environment_description", ""),
                "consequence": narrative.get("consequence_description", ""),
                "emotion": narrative.get("emotion_description", ""),
                "result": combat_result.get("result", "unknown"),
                "participants": [
                    combat_result.get("actor_name", "unknown"),
                    combat_result.get("target_name", "unknown")
                ],
                "victor": combat_result.get("victor", "unknown")
            })
        
        self.context_manager.update_context(context_id, add_moment)
    
    def _record_dialogue(self, 
                       context_id: str, 
                       npc_data: Dict[str, Any], 
                       player_input: str, 
                       result: Dict[str, str]) -> None:
        """
        Record a dialogue interaction in the context.
        
        Args:
            context_id: Context identifier
            npc_data: NPC data
            player_input: Player input
            result: Dialogue result
        """
        # Add dialogue to events
        def add_dialogue(context):
            context.add_event({
                "type": "dialogue",
                "npc_id": npc_data.get("id", "unknown"),
                "npc_name": npc_data.get("name", "NPC"),
                "player_input": player_input,
                "npc_response": result.get("dialogue", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.context_manager.update_context(context_id, add_dialogue)
    
    def _handle_player_action(self, event: Event) -> None:
        """
        Handle a player action event.
        
        Args:
            event: Player action event
        """
        session_id = event.data.get("session_id")
        if not session_id:
            return
            
        # Update pacing based on action
        action_type = event.data.get("action_type", "")
        
        # Pass to pacing manager
        self.pacing_manager._handle_player_action(event)
    
    def _handle_combat_result(self, event: Event) -> None:
        """
        Handle a combat result event.
        
        Args:
            event: Combat result event
        """
        session_id = event.data.get("session_id")
        if not session_id:
            return
            
        # Get result info
        result = event.data.get("result", "")
        
        # Pass to pacing manager based on result
        if result == "start":
            self.pacing_manager._handle_combat_start(event)
        elif result in ["victory", "defeat", "draw", "escape"]:
            self.pacing_manager._handle_combat_end(event)
    
    def _handle_world_change(self, event: Event) -> None:
        """
        Handle a world change event.
        
        Args:
            event: World change event
        """
        session_id = event.data.get("session_id")
        if not session_id:
            return
            
        # Get world state
        world = self.world_manager.get_world(session_id)
        if not world:
            return
            
        # Handle different types of world changes
        change_type = event.data.get("change_type", "")
        
        if change_type == "time_advance":
            time_delta = event.data.get("time_delta", 0.0)
            
            # Update world time
            world.update_time(time_delta)
            
            # Update pacing
            self.pacing_manager._handle_time_advance(event)
        elif change_type == "location_discover":
            location_id = event.data.get("location_id")
            location_data = event.data.get("location_data", {})
            
            if location_id and location_data:
                # Add new location
                world.add_location(location_id, location_data)
        elif change_type == "npc_discover":
            npc_id = event.data.get("npc_id")
            npc_data = event.data.get("npc_data", {})
            
            if npc_id and npc_data:
                # Add new NPC
                world.add_npc(npc_id, npc_data)