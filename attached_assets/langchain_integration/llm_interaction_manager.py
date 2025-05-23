"""
LLM Interaction Manager for AI GM Brain

This module handles all interactions with Large Language Models, including
prompt construction, API calls, error handling, and response parsing.
"""

import json
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum, auto
import openai
from datetime import datetime, timedelta


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"


class PromptMode(Enum):
    """Different prompt modes for different use cases."""
    NLU_PARSER_FAILURE = "nlu_parser_failure"
    NARRATIVE_GENERATION = "narrative_generation"
    DIALOGUE_GENERATION = "dialogue_generation"
    WORLD_QUERY = "world_query"
    CREATIVE_RESPONSE = "creative_response"


@dataclass
class LLMRequest:
    """Represents an LLM request with all necessary context."""
    prompt_mode: PromptMode
    raw_input: str
    context: Dict[str, Any]
    priority: int = 1  # 1=high, 2=medium, 3=low
    max_tokens: int = 150
    temperature: float = 0.7
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 2


@dataclass
class LLMResponse:
    """Represents an LLM response with metadata."""
    content: str
    parsed_json: Optional[Dict[str, Any]] = None
    tokens_used: int = 0
    cost_estimate: float = 0.0
    response_time: float = 0.0
    provider: str = ""
    model: str = ""
    success: bool = True
    error_message: Optional[str] = None


class TokenTracker:
    """Tracks token usage and costs."""
    
    def __init__(self):
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.requests_count = 0
        self.daily_usage = {}
        
        # Cost per 1k tokens (approximate, update with current rates)
        self.cost_per_1k_tokens = {
            "gpt-3.5-turbo": 0.002,
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025
        }
    
    def record_usage(self, model: str, tokens: int, request_time: datetime = None):
        """Record token usage and calculate cost."""
        if request_time is None:
            request_time = datetime.utcnow()
        
        self.total_tokens_used += tokens
        self.requests_count += 1
        
        # Calculate cost
        cost = (tokens / 1000) * self.cost_per_1k_tokens.get(model, 0.01)
        self.total_cost += cost
        
        # Track daily usage
        date_key = request_time.strftime("%Y-%m-%d")
        if date_key not in self.daily_usage:
            self.daily_usage[date_key] = {"tokens": 0, "cost": 0.0, "requests": 0}
        
        self.daily_usage[date_key]["tokens"] += tokens
        self.daily_usage[date_key]["cost"] += cost
        self.daily_usage[date_key]["requests"] += 1
        
        return cost
    
    def get_daily_usage(self, date: str = None) -> Dict[str, Any]:
        """Get usage for a specific date (default: today)."""
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        return self.daily_usage.get(date, {"tokens": 0, "cost": 0.0, "requests": 0})
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get total usage statistics."""
        return {
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "total_requests": self.requests_count,
            "average_tokens_per_request": self.total_tokens_used / max(1, self.requests_count),
            "average_cost_per_request": self.total_cost / max(1, self.requests_count)
        }


class PromptTemplateManager:
    """Manages LLM prompt templates for different modes."""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[PromptMode, str]:
        """Load default prompt templates."""
        return {
            PromptMode.NLU_PARSER_FAILURE: self._get_nlu_parser_failure_template(),
            PromptMode.NARRATIVE_GENERATION: self._get_narrative_generation_template(),
            PromptMode.DIALOGUE_GENERATION: self._get_dialogue_generation_template(),
            PromptMode.WORLD_QUERY: self._get_world_query_template(),
            PromptMode.CREATIVE_RESPONSE: self._get_creative_response_template()
        }
    
    def _get_nlu_parser_failure_template(self) -> str:
        """Template for NLU on parser failure (as specified in requirements)."""
        return """You are a helpful AI Game Master assistant. The player's input could not be understood by the primary game parser.

Player Input: "{player_raw_input}"
Parser Failure Reason (if any): "{parser_error_message}"

Current Game Context:
- Location: {location_name} ({location_description})
- Player Status: {player_status_summary}
- Time: {time_of_day}
- Season: {current_season}
- World State: Economic status is {economic_status}, political situation is {political_stability}

Pending Narrative Opportunities for Player:
{pending_opportunities_list}

Current Active Branch (if any):
- Branch Name: {active_branch_name}
- Current Stage: {active_stage_name} ({active_stage_description})
- Available Actions in this Stage: {available_actions_list}

Recent Context:
{recent_events_summary}

Based on the player's input and the context:
1. What is the player's most likely intent or question?
2. Does this intent strongly align with any of the PENDING NARRATIVE OPPORTUNITIES listed above? If yes, specify the Opportunity ID.
3. If in an ACTIVE BRANCH, does the intent strongly align with any of the AVAILABLE ACTIONS IN THIS STAGE? If yes, specify the action string.
4. If it does not align with a specific opportunity or action, briefly describe the general nature of their input (e.g., general query, roleplaying statement, observation).
5. Suggest a brief, in-character GM acknowledgment or response to the player that is helpful and maintains immersion.

Provide your response in JSON format like this:
{{
 "player_intent_summary": "Brief summary of player's likely intent.",
 "aligned_opportunity_id": "opportunity_id_string_or_null",
 "aligned_branch_action": "action_string_or_null", 
 "input_nature_if_no_alignment": "description_or_null",
 "suggested_gm_acknowledgement": "GM's brief response to player.",
 "confidence_score": 0.8,
 "requires_followup": false
}}"""
    
    def _get_narrative_generation_template(self) -> str:
        """Template for rich narrative generation."""
        return """You are an expert AI Game Master creating immersive narrative content.

Current Situation:
- Location: {location_name} - {location_description}
- Emotional Atmosphere: {location_emotional_aura}
- Time: {time_of_day} in {current_season}
- Weather/Environment: {environmental_conditions}

Player Character:
- Name: {player_name}
- Current State: {player_status}
- Recent Actions: {recent_player_actions}

World Context:
- Economic Status: {economic_status}
- Political Climate: {political_stability}
- Active Global Threats: {active_global_threats}
- Regional Tensions: {regional_context}

Narrative Request: {narrative_request}

Generate a rich, immersive narrative response that:
1. Responds to the specific request
2. Incorporates the environmental and atmospheric details
3. Reflects the current world state and tensions
4. Maintains consistency with the established tone
5. Provides engaging sensory details
6. Suggests potential future developments

Keep the response between 100-200 words and maintain an engaging, literary style appropriate for a fantasy RPG."""
    
    def _get_dialogue_generation_template(self) -> str:
        """Template for NPC dialogue generation."""
        return """You are an AI Game Master generating authentic NPC dialogue.

NPC Character:
- Name: {npc_name}
- Role/Occupation: {npc_role}
- Personality Traits: {npc_personality}
- Current Mood: {npc_mood}
- Relationship with Player: {relationship_status}

Current Context:
- Location: {location_name}
- Situation: {current_situation}
- Recent Events Affecting NPC: {recent_npc_events}
- World Events Relevant to NPC: {relevant_world_events}

Player's Approach/Question: "{player_input}"

Generate authentic dialogue that:
1. Reflects the NPC's personality and current mood
2. Responds appropriately to the player's approach
3. Incorporates relevant world events or local gossip
4. Maintains consistency with the NPC's established character
5. Provides useful information or advances the narrative
6. Uses appropriate speech patterns for the character's background

Format the response as direct dialogue with minimal narrative framing."""
    
    def _get_world_query_template(self) -> str:
        """Template for answering world/lore questions."""
        return """You are an AI Game Master with deep knowledge of the game world, answering a player's question about the setting, lore, or current events.

Player Question: "{player_question}"

Current World State:
- Economic Status: {economic_status}
- Political Situation: {political_stability}
- Active Threats: {active_global_threats}
- Current Season/Time: {current_season}, {time_of_day}

Player's Current Context:
- Location: {location_name}
- Knowledge Level: {player_knowledge_level}
- Recent Experiences: {recent_player_experiences}

Available Knowledge Sources:
- Local Rumors: {local_rumors}
- Historical Records: {historical_context}
- Current Events: {current_events}

Provide an informative response that:
1. Directly answers the player's question
2. Provides information appropriate to the player's knowledge level and location
3. Includes relevant current events or historical context
4. Maintains world consistency
5. Suggests related information the player might find interesting
6. Uses an appropriate tone (scholarly, conversational, mysterious, etc.)

Keep the response informative but concise (100-150 words)."""
    
    def _get_creative_response_template(self) -> str:
        """Template for creative, open-ended responses."""
        return """You are a creative AI Game Master responding to an open-ended player input that requires imagination and storytelling flair.

Player Input: "{player_input}"
Input Category: {input_category}

Current Scene:
- Setting: {location_name} - {location_description}
- Atmosphere: {current_atmosphere}
- Active Elements: {active_scene_elements}

Character Context:
- Player Character: {player_character_summary}
- Present NPCs: {present_npcs}
- Ongoing Situations: {ongoing_situations}

Creative Direction: {creative_direction_hint}

Generate a creative response that:
1. Builds on the player's input in an interesting way
2. Enhances the current scene and atmosphere
3. Introduces new elements or develops existing ones
4. Maintains narrative momentum
5. Provides opportunities for further player engagement
6. Uses vivid, engaging language

Aim for 80-120 words with a focus on immersion and creativity."""
    
    def get_template(self, mode: PromptMode) -> str:
        """Get template for a specific mode."""
        return self.templates.get(mode, "")
    
    def format_template(self, mode: PromptMode, context: Dict[str, Any]) -> str:
        """Format template with provided context."""
        template = self.get_template(mode)
        if not template:
            raise ValueError(f"No template found for mode: {mode}")
        
        # Handle missing context values gracefully
        safe_context = self._make_context_safe(context)
        
        try:
            return template.format(**safe_context)
        except KeyError as e:
            logging.warning(f"Missing context key for template formatting: {e}")
            # Fill missing keys with default values
            safe_context = self._fill_missing_keys(template, safe_context)
            return template.format(**safe_context)
    
    def _make_context_safe(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make context safe for string formatting by handling None values."""
        safe_context = {}
        for key, value in context.items():
            if value is None:
                safe_context[key] = "unknown"
            elif isinstance(value, list):
                if not value:
                    safe_context[key] = "none available"
                else:
                    safe_context[key] = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                safe_context[key] = str(value) if value else "none"
            else:
                safe_context[key] = str(value)
        return safe_context
    
    def _fill_missing_keys(self, template: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing template keys with default values."""
        import re
        
        # Find all template keys
        keys = re.findall(r'\{([^}]+)\}', template)
        
        for key in keys:
            if key not in context:
                context[key] = "not available"
        
        return context


class LLMInteractionManager:
    """
    Manages all interactions with Large Language Models.
    
    Handles prompt construction, API calls, error handling, retries,
    response parsing, and cost tracking.
    """
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.OPENAI,
                 api_key: str = None,
                 model: str = "gpt-3.5-turbo",
                 default_max_tokens: int = 150,
                 default_temperature: float = 0.7,
                 enable_cost_tracking: bool = True):
        """
        Initialize the LLM Interaction Manager.
        
        Args:
            provider: LLM provider to use
            api_key: API key for the provider
            model: Default model to use
            default_max_tokens: Default maximum tokens for responses
            default_temperature: Default temperature for generation
            enable_cost_tracking: Whether to track token usage and costs
        """
        self.provider = provider
        self.model = model
        self.default_max_tokens = default_max_tokens
        self.default_temperature = default_temperature
        
        # Initialize components
        self.template_manager = PromptTemplateManager()
        self.token_tracker = TokenTracker() if enable_cost_tracking else None
        self.logger = logging.getLogger("LLMInteractionManager")
        
        # Request queue for prioritization
        self.request_queue: List[LLMRequest] = []
        self.processing_request = False
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # seconds between requests
        
        # Initialize API client
        self._initialize_client(api_key)
        
        # Error tracking
        self.error_counts = {
            "api_errors": 0,
            "timeout_errors": 0,
            "parsing_errors": 0,
            "retry_exhausted": 0
        }
    
    def _initialize_client(self, api_key: str = None):
        """Initialize the appropriate API client."""
        if self.provider == LLMProvider.OPENAI:
            if api_key:
                openai.api_key = api_key
            # OpenAI client is global
        elif self.provider == LLMProvider.ANTHROPIC:
            # Initialize Anthropic client when available
            pass
        elif self.provider == LLMProvider.LOCAL:
            # Initialize local model client
            pass
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """
        Process an LLM request with error handling and retries.
        
        Args:
            request: LLMRequest object with all necessary information
            
        Returns:
            LLMResponse object with results or error information
        """
        start_time = time.time()
        
        try:
            # Rate limiting
            await self._apply_rate_limiting()
            
            # Format prompt
            prompt = self._format_prompt(request)
            
            # Make API call
            raw_response = await self._make_api_call(
                prompt=prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                timeout=request.timeout
            )
            
            # Parse response
            response = self._parse_response(raw_response, request.prompt_mode)
            
            # Track usage
            if self.token_tracker and response.tokens_used > 0:
                cost = self.token_tracker.record_usage(self.model, response.tokens_used)
                response.cost_estimate = cost
            
            response.response_time = time.time() - start_time
            response.provider = self.provider.value
            response.model = self.model
            
            self.logger.debug(f"LLM request completed in {response.response_time:.2f}s")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM request failed: {e}")
            
            # Handle retries
            if request.retry_count < request.max_retries:
                request.retry_count += 1
                self.logger.info(f"Retrying request (attempt {request.retry_count + 1})")
                await asyncio.sleep(2 ** request.retry_count)  # Exponential backoff
                return await self.process_request(request)
            
            # Track error
            error_type = self._classify_error(e)
            self.error_counts[error_type] += 1
            
            # Return error response
            return LLMResponse(
                content="",
                success=False,
                error_message=str(e),
                response_time=time.time() - start_time,
                provider=self.provider.value,
                model=self.model
            )
    
    def _format_prompt(self, request: LLMRequest) -> str:
        """Format the prompt using templates and context."""
        # Enhance context with standard fields
        enhanced_context = self._enhance_context(request.context)
        
        # Format using template
        return self.template_manager.format_template(
            request.prompt_mode, 
            enhanced_context
        )
    
    def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with standard fields and formatting."""
        enhanced = context.copy()
        
        # Format pending opportunities
        opportunities = context.get('pending_opportunities', [])
        if opportunities:
            opp_list = []
            for opp in opportunities:
                opp_str = f"- Opportunity ID: \"{opp.get('_source_event_id_', 'unknown')}\", Name: \"{opp.get('branch_name', 'unknown')}\", Hook: \"{opp.get('description', 'No description')}\""
                opp_list.append(opp_str)
            enhanced['pending_opportunities_list'] = '\n'.join(opp_list)
        else:
            enhanced['pending_opportunities_list'] = "No pending opportunities available."
        
        # Format available actions
        actions = context.get('available_actions', [])
        if actions:
            enhanced['available_actions_list'] = ', '.join(actions)
        else:
            enhanced['available_actions_list'] = "No specific actions available."
        
        # Format recent events summary
        recent_events = context.get('recent_events', [])
        if recent_events:
            event_summaries = []
            for event in recent_events[-3:]:  # Last 3 events
                if hasattr(event, 'summarize'):
                    event_summaries.append(event.summarize()['summary'])
                elif isinstance(event, dict):
                    event_summaries.append(event.get('summary', str(event)))
            enhanced['recent_events_summary'] = '; '.join(event_summaries)
        else:
            enhanced['recent_events_summary'] = "No recent significant events."
        
        # Ensure all required fields have defaults
        defaults = {
            'location_name': 'Unknown Location',
            'location_description': 'A place of mystery',
            'player_status_summary': 'Alert and ready',
            'time_of_day': 'daytime',
            'current_season': 'spring',
            'economic_status': 'stable',
            'political_stability': 'stable',
            'active_branch_name': 'None',
            'active_stage_name': 'None',
            'active_stage_description': 'None',
            'parser_error_message': 'Unknown parsing error'
        }
        
        for key, default_value in defaults.items():
            if key not in enhanced or enhanced[key] is None:
                enhanced[key] = default_value
        
        return enhanced
    
    async def _make_api_call(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Dict[str, Any]:
        """Make the actual API call to the LLM provider."""
        if self.provider == LLMProvider.OPENAI:
            return await self._call_openai(prompt, max_tokens, temperature, timeout)
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic(prompt, max_tokens, temperature, timeout)
        elif self.provider == LLMProvider.LOCAL:
            return await self._call_local(prompt, max_tokens, temperature, timeout)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _call_openai(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Dict[str, Any]:
        """Make OpenAI API call."""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                ),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            raise Exception("OpenAI API call timed out")
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Dict[str, Any]:
        """Make Anthropic API call (placeholder)."""
        # Implement when Anthropic client is available
        raise NotImplementedError("Anthropic integration not yet implemented")
    
    async def _call_local(self, prompt: str, max_tokens: int, temperature: float, timeout: float) -> Dict[str, Any]:
        """Make local model API call (placeholder)."""
        # Implement for local models
        raise NotImplementedError("Local model integration not yet implemented")
    
    def _parse_response(self, raw_response: Dict[str, Any], prompt_mode: PromptMode) -> LLMResponse:
        """Parse the raw LLM response into structured format."""
        try:
            if self.provider == LLMProvider.OPENAI:
                content = raw_response['choices'][0]['message']['content']
                tokens_used = raw_response.get('usage', {}).get('total_tokens', 0)
            else:
                content = str(raw_response)
                tokens_used = 0
            
            # Try to parse JSON if expected
            parsed_json = None
            if prompt_mode == PromptMode.NLU_PARSER_FAILURE:
                try:
                    # Extract JSON from response (might be wrapped in text)
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        parsed_json = json.loads(json_str)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JSON from LLM response: {e}")
                    # Provide fallback structure
                    parsed_json = {
                        "player_intent_summary": "Unable to parse intent",
                        "aligned_opportunity_id": None,
                        "aligned_branch_action": None,
                        "input_nature_if_no_alignment": "parsing_error",
                        "suggested_gm_acknowledgement": content[:100] + "..." if len(content) > 100 else content,
                        "confidence_score": 0.1,
                        "requires_followup": True
                    }
            
            return LLMResponse(
                content=content,
                parsed_json=parsed_json,
                tokens_used=tokens_used,
                success=True
            )
            
        except Exception as e:
            self.error_counts["parsing_errors"] += 1
            raise Exception(f"Response parsing error: {e}")
    
    async def _apply_rate_limiting(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error for tracking purposes."""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return "timeout_errors"
        elif "api" in error_str or "http" in error_str:
            return "api_errors"
        elif "json" in error_str or "parse" in error_str:
            return "parsing_errors"
        else:
            return "api_errors"
    
    # Convenience methods for different use cases
    async def understand_failed_input(self, 
                                    raw_input: str, 
                                    parser_error: str, 
                                    context: Dict[str, Any]) -> LLMResponse:
        """Process failed parser input for NLU."""
        request = LLMRequest(
            prompt_mode=PromptMode.NLU_PARSER_FAILURE,
            raw_input=raw_input,
            context={
                **context,
                'player_raw_input': raw_input,
                'parser_error_message': parser_error
            },
            priority=1,  # High priority for gameplay flow
            max_tokens=200,
            temperature=0.3  # Lower temperature for more consistent parsing
        )
        
        return await self.process_request(request)
    
    async def generate_narrative(self, 
                               narrative_request: str, 
                               context: Dict[str, Any]) -> LLMResponse:
        """Generate rich narrative content."""
        request = LLMRequest(
            prompt_mode=PromptMode.NARRATIVE_GENERATION,
            raw_input=narrative_request,
            context={
                **context,
                'narrative_request': narrative_request
            },
            priority=2,
            max_tokens=300,
            temperature=0.8  # Higher temperature for creativity
        )
        
        return await self.process_request(request)
    
    async def generate_dialogue(self, 
                              npc_id: str, 
                              player_input: str, 
                              context: Dict[str, Any]) -> LLMResponse:
        """Generate NPC dialogue."""
        request = LLMRequest(
            prompt_mode=PromptMode.DIALOGUE_GENERATION,
            raw_input=player_input,
            context={
                **context,
                'npc_id': npc_id,
                'player_input': player_input
            },
            priority=2,
            max_tokens=200,
            temperature=0.7
        )
        
        return await self.process_request(request)
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics."""
        stats = {
            "error_counts": self.error_counts.copy(),
            "provider": self.provider.value,
            "model": self.model
        }
        
        if self.token_tracker:
            stats["token_usage"] = self.token_tracker.get_total_stats()
            stats["daily_usage"] = self.token_tracker.get_daily_usage()
        
        return stats
    
    def reset_error_counts(self):
        """Reset error counters."""
        self.error_counts = {
            "api_errors": 0,
            "timeout_errors": 0,
            "parsing_errors": 0,
            "retry_exhausted": 0
        }