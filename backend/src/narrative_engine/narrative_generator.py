"""
Narrative Generator

This module handles the generation of narrative content for the game,
using LLM integration for dynamic content creation.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class CombatNarrativeGenerator:
    """
    Generates narrative descriptions for combat encounters.
    
    This class provides methods for creating rich, contextual narratives
    around combat situations, taking into account character abilities,
    environment, and combat results.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the combat narrative generator.
        
        Args:
            api_key: Optional API key for LLM service
        """
        self.api_key = api_key
        self.narrative_templates = self._load_narrative_templates()
        self.descriptive_cache = {}  # Cache for common descriptions
    
    def _load_narrative_templates(self) -> Dict:
        """Load narrative templates for different combat situations"""
        # In a real implementation, these would be loaded from a file or database
        return {
            "move_success": [
                "{actor} executes {move} with precision. {target} {reaction}.",
                "With skillful application of {domain}, {actor}'s {move} lands true. {target} {reaction}.",
                "{actor} channels their {domain} expertise into a powerful {move}. {target} {reaction}."
            ],
            "move_failure": [
                "{target} anticipates {actor}'s {move} and {counter}.",
                "{actor}'s {move} fails to connect as {target} {counter}.",
                "Despite drawing on {domain}, {actor}'s {move} is thwarted when {target} {counter}."
            ],
            "status_applied": [
                "{target} is now {status} from the effects of {move}.",
                "The {move} leaves {target} {status}.",
                "{actor}'s {move} results in {target} becoming {status}."
            ],
            "critical_success": [
                "In a display of extraordinary skill, {actor}'s {move} strikes a critical weakness!",
                "{actor} executes {move} with uncanny precision, finding the perfect opening!",
                "A moment of perfect execution! {actor}'s {move} lands with devastating effect!"
            ],
            "environment_interaction": [
                "{actor} uses the {environment} to their advantage, {interaction_effect}.",
                "The {environment} becomes a weapon in {actor}'s hands, {interaction_effect}.",
                "Drawing on the surroundings, {actor} {interaction_effect} using the {environment}."
            ]
        }
    
    async def generate_combat_narrative(self, 
                                      combat_result: Dict[str, Any],
                                      actor: Dict[str, Any], 
                                      target: Dict[str, Any],
                                      environment_tags: List[str],
                                      memory_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate narrative descriptions for a combat round.
        
        Args:
            combat_result: The result of the combat calculation
            actor: The character performing the action
            target: The target of the action
            environment_tags: Environmental factors affecting the combat
            memory_context: Optional historical context between combatants
            
        Returns:
            Dictionary with different narrative elements
        """
        # Prepare the base context from combat result
        context = self._prepare_narrative_context(combat_result, actor, target, environment_tags)
        
        # Add memory context if available
        if memory_context:
            context.update(self._prepare_memory_context(memory_context))
            
        # If no API key, use template-based generation
        if not self.api_key:
            return self._generate_from_templates(context)
            
        # Otherwise, use LLM via API
        try:
            # Import LLM manager if available
            from backend.src.ai_gm.llm_integration.llm_manager import LLMManager
            llm_manager = LLMManager()
            
            # Construct a detailed prompt for combat narrative
            prompt = self._construct_llm_prompt(context)
            
            response = llm_manager.generate_text(
                prompt=prompt,
                context=context,
                temperature=0.7
            )
            
            # Parse the LLM response into structured narrative segments
            return self._parse_llm_response(response.get('text', ''))
        except ImportError:
            logger.warning("LLM manager not available. Falling back to template-based generation.")
            return self._generate_from_templates(context)
        except Exception as e:
            logger.error(f"Error in LLM-based narrative generation: {e}")
            return self._generate_from_templates(context)
    
    def _prepare_narrative_context(self, combat_result: Dict[str, Any], 
                                 actor: Dict[str, Any], 
                                 target: Dict[str, Any], 
                                 environment_tags: List[str]) -> Dict[str, Any]:
        """Prepare context for narrative generation"""
        context = {
            "actor_name": actor.get("name", "The attacker"),
            "target_name": target.get("name", "The defender"),
            "move_name": combat_result.get("actor_move", "attack"),
            "move_type": self._get_move_type_description(combat_result.get("actor_move_type")),
            "success": combat_result.get("actor_success", False),
            "effect_magnitude": combat_result.get("effect_magnitude", 0),
            "environment": environment_tags,
            "narrative_hooks": combat_result.get("narrative_hooks", []),
            "combo_used": combat_result.get("combo_used"),
            "status_applied": combat_result.get("status_applied"),
            "actor_domains": actor.get("domains", []),
            "target_domains": target.get("domains", []),
            "desperation": combat_result.get("actor_desperate", False),
            "calculation": combat_result.get("actor_calculated", False),
        }
        
        # Add reaction based on success
        if context["success"]:
            damage = combat_result.get("damage_dealt", 0)
            if damage > 20:
                context["target_reaction"] = "staggers backward, severely wounded"
            elif damage > 10:
                context["target_reaction"] = "winces in pain"
            else:
                context["target_reaction"] = "absorbs the blow"
        else:
            counter_type = combat_result.get("target_move_type")
            if counter_type == "FORCE":
                context["target_counter"] = "responds with overwhelming force"
            elif counter_type == "TRICK":
                context["target_counter"] = "deftly evades"
            elif counter_type == "FOCUS":
                context["target_counter"] = "perfectly anticipates the attack"
            else:
                context["target_counter"] = "defends effectively"
                
        return context
    
    def _prepare_memory_context(self, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare memory-related context for narrative generation"""
        memory_elements = {}
        
        # Add history with this opponent if available
        opponent_name = memory_context.get("current_opponent_name")
        if opponent_name and opponent_name in memory_context.get("opponent_records", {}):
            record = memory_context["opponent_records"][opponent_name]
            memory_elements["previous_encounters"] = record["encounters"]
            memory_elements["victory_record"] = f"{record['victories']} wins, {record['defeats']} losses"
            
            # Add narrative callbacks if available
            if record.get("narrative_moments"):
                memory_elements["past_moment"] = record["narrative_moments"][-1].get("description")
                
        # Add recently used effective moves if available
        if "most_effective_moves" in memory_context:
            memory_elements["effective_move"] = memory_context["most_effective_moves"][0]["name"]
            
        return {"memory": memory_elements}
    
    def _get_move_type_description(self, move_type: str) -> str:
        """Get a descriptive phrase for a move type"""
        if not move_type:
            return "skillful attack"
            
        descriptions = {
            "FORCE": ["powerful", "forceful", "mighty", "overwhelming"],
            "TRICK": ["deceptive", "cunning", "tricky", "clever"],
            "FOCUS": ["precise", "calculated", "focused", "analytical"],
            "BUFF": ["supportive", "enhancing", "empowering", "strengthening"],
            "DEBUFF": ["weakening", "hindering", "disabling", "hampering"],
            "UTILITY": ["versatile", "resourceful", "adaptive", "practical"]
        }
        
        move_type_upper = move_type.upper() if isinstance(move_type, str) else ""
        options = descriptions.get(move_type_upper, ["skillful"])
        
        # Cache common descriptions
        cache_key = f"{move_type_upper}_desc"
        if cache_key not in self.descriptive_cache:
            import random
            self.descriptive_cache[cache_key] = random.choice(options)
            
        return self.descriptive_cache[cache_key]
    
    def _generate_from_templates(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate narrative using templates"""
        import random
        
        narratives = {}
        
        # Select the right template category
        if context["success"]:
            if context.get("effect_magnitude", 0) > 5:
                template_category = "critical_success"
            else:
                template_category = "move_success"
        else:
            template_category = "move_failure"
            
        # Select and fill a template for the main action
        templates = self.narrative_templates[template_category]
        template = random.choice(templates)
        
        # Basic replacements
        filled_template = template.replace("{actor}", context["actor_name"])
        filled_template = filled_template.replace("{target}", context["target_name"])
        filled_template = filled_template.replace("{move}", context["move_name"])
        
        # More complex replacements
        if "{domain}" in filled_template:
            if context["actor_domains"]:
                domain = random.choice(context["actor_domains"])
                filled_template = filled_template.replace("{domain}", domain)
            else:
                filled_template = filled_template.replace("{domain}", "skill")
                
        if "{reaction}" in filled_template and "target_reaction" in context:
            filled_template = filled_template.replace("{reaction}", context["target_reaction"])
            
        if "{counter}" in filled_template and "target_counter" in context:
            filled_template = filled_template.replace("{counter}", context["target_counter"])
            
        narratives["action_description"] = filled_template
        
        # Add environment description if available
        if context["environment"]:
            env = random.choice(context["environment"])
            env_template = random.choice(self.narrative_templates["environment_interaction"])
            
            # Generate a random interaction effect
            effects = [
                "gains an advantage",
                "creates an opening",
                "improves their position",
                "finds a tactical opportunity"
            ]
            
            env_narrative = env_template.replace("{actor}", context["actor_name"])
            env_narrative = env_narrative.replace("{environment}", env)
            env_narrative = env_narrative.replace("{interaction_effect}", random.choice(effects))
            
            narratives["environment_description"] = env_narrative
        else:
            narratives["environment_description"] = ""
            
        # Add memory callback if available
        if "memory" in context and "past_moment" in context["memory"]:
            narratives["memory_callback"] = context["memory"]["past_moment"]
        else:
            narratives["memory_callback"] = ""
            
        # Generate a basic consequence description
        if context["success"] and context.get("effect_magnitude", 0) > 3:
            consequence = f"This powerful strike might leave lasting damage on {context['target_name']}."
            narratives["consequence_description"] = consequence
        else:
            narratives["consequence_description"] = ""
            
        # Generate a basic emotion description
        if context["success"]:
            emotion = f"{context['actor_name']} feels a surge of confidence."
            if "memory" in context and context["memory"].get("previous_encounters", 0) > 1:
                emotion += f" There's history between these combatants that fuels the intensity."
            narratives["emotion_description"] = emotion
        else:
            emotion = f"{context['actor_name']} feels frustrated by the failed attempt."
            narratives["emotion_description"] = emotion
            
        return narratives
    
    def _construct_llm_prompt(self, context: Dict[str, Any]) -> str:
        """Construct a detailed prompt for LLM-based narrative generation"""
        # This would construct a rich prompt for the LLM based on the context
        prompt = f"""
        Generate a detailed combat narrative for the following scenario:
        
        Actor: {context['actor_name']}
        Target: {context['target_name']}
        Move: {context['move_name']} ({context['move_type']})
        Success: {"Yes" if context['success'] else "No"}
        Environment: {', '.join(context['environment']) if context['environment'] else "Standard arena"}
        
        Please generate separate narrative segments for:
        1. Action Description - A vivid description of the combat action
        2. Environment Description - How the environment affects the action
        3. Consequence Description - Any lasting effects of this action
        4. Emotion Description - The emotional impact on the combatants
        
        Format each segment with a clear heading.
        """
        
        # Add memory elements if available
        if "memory" in context:
            prompt += "\n\nPrevious History: "
            if "previous_encounters" in context["memory"]:
                prompt += f"These combatants have faced each other {context['memory']['previous_encounters']} times before. "
            if "victory_record" in context["memory"]:
                prompt += f"Record: {context['memory']['victory_record']}. "
            if "past_moment" in context["memory"]:
                prompt += f"Notable past event: {context['memory']['past_moment']}"
                
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, str]:
        """Parse the LLM response into structured narrative segments"""
        narratives = {
            "action_description": "",
            "environment_description": "",
            "consequence_description": "",
            "emotion_description": "",
            "memory_callback": ""
        }
        
        # This is a simplified parser - in production, you'd want more robust parsing
        segments = response_text.split("\n\n")
        
        for segment in segments:
            lowercase_segment = segment.lower()
            if "action description" in lowercase_segment:
                narratives["action_description"] = segment.split(":", 1)[1].strip() if ":" in segment else segment
            elif "environment description" in lowercase_segment:
                narratives["environment_description"] = segment.split(":", 1)[1].strip() if ":" in segment else segment
            elif "consequence description" in lowercase_segment:
                narratives["consequence_description"] = segment.split(":", 1)[1].strip() if ":" in segment else segment
            elif "emotion description" in lowercase_segment:
                narratives["emotion_description"] = segment.split(":", 1)[1].strip() if ":" in segment else segment
            elif "memory" in lowercase_segment or "history" in lowercase_segment:
                narratives["memory_callback"] = segment.split(":", 1)[1].strip() if ":" in segment else segment
        
        return narratives


class NarrativeDirector:
    """
    High-level manager for narrative generation and progression.
    
    This class coordinates the various narrative components and interfaces
    with the Celery integration for asynchronous processing.
    """
    
    def __init__(self):
        """Initialize the narrative director."""
        self.logger = logging.getLogger("NarrativeDirector")
        
        # Initialize narrative components
        self.combat_generator = CombatNarrativeGenerator()
        
        # Connect to Celery integration
        try:
            from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
            self.celery_integration = NarrativeEngineCeleryIntegration()
            self.async_enabled = True
            self.logger.info("Narrative engine connected to Celery for async processing")
        except ImportError:
            self.logger.warning("Celery integration not available. Running in synchronous mode.")
            self.async_enabled = False
    
    async def generate_combat_narrative(self,
                                     combat_result: Dict[str, Any],
                                     actor: Dict[str, Any],
                                     target: Dict[str, Any],
                                     environment_tags: List[str],
                                     memory_context: Optional[Dict[str, Any]] = None,
                                     async_processing: bool = True) -> Union[Dict[str, str], Dict[str, Any]]:
        """
        Generate a narrative for a combat encounter.
        
        Args:
            combat_result: The result of the combat calculation
            actor: The character performing the action
            target: The target of the action
            environment_tags: Environmental factors affecting the combat
            memory_context: Optional historical context between combatants
            async_processing: Whether to process asynchronously with Celery
            
        Returns:
            Either the narrative content or a task information dict if async
        """
        # If async is disabled or explicitly requested synchronous
        if not self.async_enabled or not async_processing:
            return await self.combat_generator.generate_combat_narrative(
                combat_result=combat_result,
                actor=actor,
                target=target,
                environment_tags=environment_tags,
                memory_context=memory_context
            )
        
        # Otherwise, process asynchronously with Celery
        return await self.celery_integration.generate_combat_narrative_async(
            combat_result=combat_result,
            actor=actor,
            target=target,
            environment_tags=environment_tags,
            memory_context=memory_context
        )
    
    async def generate_npc_dialogue(self,
                                 npc_data: Dict[str, Any],
                                 dialogue_context: Dict[str, Any],
                                 player_input: str,
                                 async_processing: bool = True) -> Union[Dict[str, str], Dict[str, Any]]:
        """
        Generate dialogue for an NPC.
        
        Args:
            npc_data: Data about the NPC
            dialogue_context: Context for the dialogue
            player_input: Player's input or question
            async_processing: Whether to process asynchronously with Celery
            
        Returns:
            Either the dialogue content or a task information dict if async
        """
        # If async is disabled or explicitly requested synchronous
        if not self.async_enabled or not async_processing:
            # Import LLM manager if available
            try:
                from backend.src.ai_gm.llm_integration.llm_manager import LLMManager
                llm_manager = LLMManager()
                
                # Prepare the prompt
                npc_name = npc_data.get('name', 'NPC')
                npc_personality = npc_data.get('personality', 'neutral')
                npc_knowledge = npc_data.get('knowledge', [])
                relationship = dialogue_context.get('relationship', 'neutral')
                
                prompt = f"""
                Generate dialogue for {npc_name}, who has a {npc_personality} personality.
                Their relationship with the player is: {relationship}.
                They know about: {', '.join(npc_knowledge)}.
                
                The player just said: "{player_input}"
                
                Generate {npc_name}'s response:
                """
                
                response = llm_manager.generate_text(
                    prompt=prompt,
                    context=dialogue_context,
                    temperature=0.8
                )
                
                return {
                    'dialogue': response.get('text', ''),
                    'npc_id': npc_data.get('id', 'unknown'),
                    'player_input': player_input
                }
            except ImportError:
                self.logger.warning("LLM manager not available. Using simple dialogue generation.")
                
                # Simple dialogue generation
                npc_name = npc_data.get('name', 'NPC')
                npc_personality = npc_data.get('personality', 'neutral')
                
                if npc_personality == 'friendly':
                    dialogue = f"[{npc_name} smiles] Ah, I'm glad you asked about that! {player_input.capitalize()}? Let me help you with that."
                elif npc_personality == 'hostile':
                    dialogue = f"[{npc_name} glares] Why should I tell you about {player_input.lower()}? Mind your own business."
                elif npc_personality == 'mysterious':
                    dialogue = f"[{npc_name} speaks cryptically] {player_input.capitalize()}? Some secrets are best left undiscovered... but perhaps I can share a fragment of truth."
                else:
                    dialogue = f"[{npc_name} responds] About {player_input}? I suppose I can tell you what I know."
                    
                return {
                    'dialogue': dialogue,
                    'npc_id': npc_data.get('id', 'unknown'),
                    'player_input': player_input
                }
        
        # Otherwise, process asynchronously with Celery
        return await self.celery_integration.generate_npc_dialogue_async(
            npc_data=npc_data,
            dialogue_context=dialogue_context,
            player_input=player_input
        )
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of an asynchronous narrative task.
        
        Args:
            task_id: The task ID to check
            
        Returns:
            Status information about the task
        """
        if not self.async_enabled:
            return {
                'error': 'Async processing not enabled',
                'task_id': task_id,
                'status': 'unavailable'
            }
            
        result = await self.celery_integration.get_task_result(task_id)
        
        if result is not None:
            return {
                'task_id': task_id,
                'status': 'completed',
                'result': result
            }
        else:
            return {
                'task_id': task_id,
                'status': 'pending',
                'message': 'Task still processing or not found'
            }
    
    async def wait_for_task_completion(self, task_id: str, max_wait: int = 30) -> Dict[str, Any]:
        """
        Wait for a narrative task to complete.
        
        Args:
            task_id: The task ID to wait for
            max_wait: Maximum seconds to wait
            
        Returns:
            The task result or timeout information
        """
        if not self.async_enabled:
            return {
                'error': 'Async processing not enabled',
                'task_id': task_id,
                'status': 'unavailable'
            }
            
        result = await self.celery_integration.wait_for_task_completion(task_id, max_wait)
        
        if result is not None:
            return {
                'task_id': task_id,
                'status': 'completed',
                'result': result
            }
        else:
            return {
                'task_id': task_id,
                'status': 'timeout',
                'message': f'Task did not complete within {max_wait} seconds'
            }