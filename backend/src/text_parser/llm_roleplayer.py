"""
LLM Roleplayer - Phase 5 of the modular text parser system

This module handles direct LLM interaction without LangChain, providing
role-playing responses and narrative generation.

PHASE 5 COMPLETE: Comprehensive LLM integration with OpenRouter API,
multiple model support, role-playing capabilities, and robust error handling.
"""

import os
import time
import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .intent_router import IntentResult, PrimaryIntent, SubIntent
from .prompt_builder import PromptContext
from .action_executor import ActionResult


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class ResponseMode(Enum):
    """Different response generation modes."""
    NARRATIVE = "narrative"              # Story narration and descriptions
    DIALOGUE = "dialogue"                # Character dialogue and conversations
    COMBAT = "combat"                   # Combat descriptions and actions
    EXPLORATION = "exploration"         # Environment and exploration responses
    SOCIAL = "social"                   # Social interactions and reactions
    CREATIVE = "creative"               # Creative/artistic responses
    ANALYTICAL = "analytical"           # Analysis and problem-solving
    FALLBACK = "fallback"              # Fallback for failed parsing


@dataclass 
class LLMConfig:
    """Configuration for LLM interactions."""
    provider: LLMProvider = LLMProvider.OPENROUTER
    model: str = "openai/gpt-4o"
    max_tokens: int = 500
    temperature: float = 0.7
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_streaming: bool = False
    
    # Model tier configurations
    model_tiers: Dict[str, str] = field(default_factory=lambda: {
        "fast": "openai/gpt-3.5-turbo",
        "standard": "openai/gpt-4o", 
        "premium": "anthropic/claude-3-opus",
        "creative": "anthropic/claude-3-sonnet",
        "analytical": "openai/gpt-4-turbo"
    })
    
    # Response mode to model mapping
    mode_models: Dict[ResponseMode, str] = field(default_factory=lambda: {
        ResponseMode.NARRATIVE: "anthropic/claude-3-sonnet",
        ResponseMode.DIALOGUE: "anthropic/claude-3-sonnet", 
        ResponseMode.COMBAT: "openai/gpt-4o",
        ResponseMode.EXPLORATION: "anthropic/claude-3-sonnet",
        ResponseMode.SOCIAL: "anthropic/claude-3-haiku",
        ResponseMode.CREATIVE: "anthropic/claude-3-sonnet",
        ResponseMode.ANALYTICAL: "openai/gpt-4-turbo",
        ResponseMode.FALLBACK: "openai/gpt-3.5-turbo"
    })


@dataclass
class LLMResponse:
    """Response from LLM interaction."""
    response_text: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    provider: str = ""
    model: str = ""
    tokens_used: int = 0
    processing_time: float = 0.0
    response_mode: Optional[ResponseMode] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if the response was successful."""
        return self.error is None and bool(self.response_text.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "response_text": self.response_text,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "reasoning": self.reasoning,
            "provider": self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "response_mode": self.response_mode.value if self.response_mode else None,
            "error": self.error,
            "success": self.success
        }


@dataclass
class RoleplayingContext:
    """Context for role-playing responses."""
    character_name: str = ""
    character_personality: str = ""
    scene_description: str = ""
    world_state: Dict[str, Any] = field(default_factory=dict)
    previous_actions: List[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    relationship_context: Dict[str, Any] = field(default_factory=dict)
    narrative_tone: str = "balanced"  # serious, humorous, dramatic, mysterious, etc.


class LLMRoleplayer:
    """
    Handles direct LLM interaction for role-playing responses and narrative
    generation, replacing LangChain agent functionality.
    
    PHASE 5 FEATURES:
    - Multi-provider support (OpenRouter, OpenAI, Anthropic)
    - Intelligent model selection based on response modes
    - Role-playing context management
    - Robust error handling and fallbacks
    - Token usage tracking and cost optimization
    - Async and sync interfaces
    - Response caching for performance
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the LLM Roleplayer.
        
        Args:
            config: LLM configuration. If None, creates default config.
        """
        self.config = config or LLMConfig()
        self.logger = logging.getLogger("text_parser.llm_roleplayer")
        
        # API configuration
        self.api_key = self._get_api_key()
        self.session = None  # Will be created when needed
        
        # Statistics tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Response cache for performance
        self._response_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max_size = 100
        self._cache_ttl = 300  # 5 minutes
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1
        
        self.logger.info(f"LLMRoleplayer initialized with {self.config.provider.value} provider")
    
    def _get_api_key(self) -> str:
        """Get the appropriate API key based on provider."""
        if self.config.provider == LLMProvider.OPENROUTER:
            return os.environ.get('OPENROUTER_API_KEY', '')
        elif self.config.provider == LLMProvider.OPENAI:
            return os.environ.get('OPENAI_API_KEY', '')
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return os.environ.get('ANTHROPIC_API_KEY', '')
        else:
            return ''
    
    def _get_api_url(self) -> str:
        """Get the appropriate API URL based on provider."""
        if self.config.provider == LLMProvider.OPENROUTER:
            return "https://openrouter.ai/api/v1/chat/completions"
        elif self.config.provider == LLMProvider.OPENAI:
            return "https://api.openai.com/v1/chat/completions"
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return "https://api.anthropic.com/v1/messages"
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def _get_optimal_model(self, response_mode: ResponseMode, complexity: str = "standard") -> str:
        """
        Select the optimal model based on response mode and complexity.
        
        Args:
            response_mode: The type of response needed
            complexity: Complexity level (fast, standard, premium)
            
        Returns:
            Model name to use
        """
        # First check mode-specific model
        if response_mode in self.config.mode_models:
            return self.config.mode_models[response_mode]
        
        # Fallback to tier-based selection
        if complexity in self.config.model_tiers:
            return self.config.model_tiers[complexity]
        
        # Final fallback to configured default
        return self.config.model
    
    def _create_cache_key(self, prompt: str, model: str, mode: ResponseMode) -> str:
        """Create a cache key for response caching."""
        import hashlib
        content = f"{prompt}:{model}:{mode.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[LLMResponse]:
        """Check if a response is cached and still valid."""
        if cache_key not in self._response_cache:
            return None
        
        cached_data = self._response_cache[cache_key]
        cache_time = cached_data.get('timestamp', 0)
        
        # Check if cache entry is still valid
        if time.time() - cache_time > self._cache_ttl:
            del self._response_cache[cache_key]
            return None
        
        self.stats["cache_hits"] += 1
        response_data = cached_data['response']
        
        # Recreate LLMResponse object
        return LLMResponse(**response_data)
    
    def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache a response."""
        # Manage cache size
        if len(self._response_cache) >= self._cache_max_size:
            # Remove oldest entry
            oldest_key = min(self._response_cache.keys(), 
                           key=lambda k: self._response_cache[k]['timestamp'])
            del self._response_cache[oldest_key]
        
        self._response_cache[cache_key] = {
            'timestamp': time.time(),
            'response': response.to_dict()
        }
    
    def _create_headers(self) -> Dict[str, str]:
        """Create headers for API request."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.config.provider == LLMProvider.OPENROUTER:
            headers.update({
                "HTTP-Referer": "https://textrealms-ai.com",
                "X-Title": "TextRealms AI - Text Parser"
            })
        
        return headers
    
    def _create_payload(self, prompt: str, model: str, mode: ResponseMode) -> Dict[str, Any]:
        """Create the API request payload."""
        base_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        # Provider-specific adjustments
        if self.config.provider == LLMProvider.OPENROUTER:
            # OpenRouter supports additional parameters
            base_payload.update({
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            })
        elif self.config.provider == LLMProvider.ANTHROPIC:
            # Anthropic has different format
            base_payload = {
                "model": model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
        
        return base_payload
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _rate_limit(self):
        """Apply rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    async def _make_async_request(self, prompt: str, model: str, mode: ResponseMode) -> LLMResponse:
        """Make an async API request to the LLM."""
        start_time = time.time()
        
        try:
            # Rate limiting
            await asyncio.sleep(max(0, self._min_request_interval - (time.time() - self._last_request_time)))
            
            headers = self._create_headers()
            payload = self._create_payload(prompt, model, mode)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                self._get_api_url(),
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data, model, mode, time.time() - start_time)
                else:
                    error_text = await response.text()
                    self.logger.error(f"API request failed: {response.status} - {error_text}")
                    return self._create_error_response(
                        f"API request failed: {response.status}",
                        model, mode, time.time() - start_time
                    )
        
        except asyncio.TimeoutError:
            self.logger.error("API request timed out")
            return self._create_error_response("Request timed out", model, mode, time.time() - start_time)
        except Exception as e:
            self.logger.error(f"API request error: {str(e)}")
            return self._create_error_response(str(e), model, mode, time.time() - start_time)
    
    def _make_sync_request(self, prompt: str, model: str, mode: ResponseMode) -> LLMResponse:
        """Make a synchronous API request to the LLM."""
        start_time = time.time()
        
        try:
            self._rate_limit()
            
            headers = self._create_headers()
            payload = self._create_payload(prompt, model, mode)
            
            import requests
            response = requests.post(
                self._get_api_url(),
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data, model, mode, time.time() - start_time)
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return self._create_error_response(
                    f"API request failed: {response.status_code}",
                    model, mode, time.time() - start_time
                )
        
        except requests.exceptions.Timeout:
            self.logger.error("API request timed out")
            return self._create_error_response("Request timed out", model, mode, time.time() - start_time)
        except Exception as e:
            self.logger.error(f"API request error: {str(e)}")
            return self._create_error_response(str(e), model, mode, time.time() - start_time)
    
    def _parse_response(self, data: Dict[str, Any], model: str, mode: ResponseMode, processing_time: float) -> LLMResponse:
        """Parse the API response into an LLMResponse object."""
        try:
            if self.config.provider in [LLMProvider.OPENROUTER, LLMProvider.OPENAI]:
                content = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                tokens_used = usage.get('total_tokens', 0)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                content = data['content'][0]['text']
                usage = data.get('usage', {})
                tokens_used = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            else:
                content = str(data)
                tokens_used = self._estimate_tokens(content)
            
            # Update statistics
            self.stats["successful_requests"] += 1
            self.stats["total_tokens"] += tokens_used
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["successful_requests"] - 1) + processing_time) 
                / self.stats["successful_requests"]
            )
            
            return LLMResponse(
                response_text=content.strip(),
                confidence=0.9,  # High confidence for successful API responses
                metadata={
                    "usage": usage,
                    "api_data": data
                },
                reasoning="Generated by LLM API",
                provider=self.config.provider.value,
                model=model,
                tokens_used=tokens_used,
                processing_time=processing_time,
                response_mode=mode
            )
        
        except (KeyError, IndexError) as e:
            self.logger.error(f"Failed to parse API response: {e}")
            return self._create_error_response(f"Failed to parse response: {e}", model, mode, processing_time)
    
    def _create_error_response(self, error_msg: str, model: str, mode: ResponseMode, processing_time: float) -> LLMResponse:
        """Create an error response."""
        self.stats["failed_requests"] += 1
        
        return LLMResponse(
            response_text="",
            confidence=0.0,
            metadata={},
            reasoning=f"Error: {error_msg}",
            provider=self.config.provider.value,
            model=model,
            tokens_used=0,
            processing_time=processing_time,
            response_mode=mode,
            error=error_msg
        )
    
    def __init__(self, api_key: str = None, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        """
        Initialize the LLM roleplayer.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use for generation
        """
        self.logger = logging.getLogger("text_parser.llm_roleplayer")
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger.info(f"LLMRoleplayer initialized with model: {model}")
    
    # ============================================================================
    # PUBLIC INTERFACE METHODS
    # ============================================================================
    
    async def generate_response_async(self, 
                                    prompt: str,
                                    mode: ResponseMode = ResponseMode.NARRATIVE,
                                    context: Optional[RoleplayingContext] = None,
                                    complexity: str = "standard",
                                    use_cache: bool = True) -> LLMResponse:
        """
        Generate an async LLM response.
        
        Args:
            prompt: The input prompt for the LLM
            mode: Response mode for optimal model selection
            context: Optional roleplaying context
            complexity: Complexity level for model selection
            use_cache: Whether to use response caching
            
        Returns:
            LLMResponse with the generated content
        """
        self.stats["total_requests"] += 1
        
        # Select optimal model
        model = self._get_optimal_model(mode, complexity)
        
        # Enhance prompt with context if provided
        enhanced_prompt = self._enhance_prompt_with_context(prompt, context, mode)
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._create_cache_key(enhanced_prompt, model, mode)
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return cached_response
            self.stats["cache_misses"] += 1
        
        # Validate API key
        if not self.api_key:
            return self._create_error_response(
                f"No API key configured for {self.config.provider.value}",
                model, mode, 0.0
            )
        
        # Make the API request with retries
        response = await self._make_request_with_retries_async(enhanced_prompt, model, mode)
        
        # Cache successful responses
        if use_cache and response.success:
            self._cache_response(cache_key, response)
        
        return response
    
    def generate_response(self, 
                         prompt: str,
                         mode: ResponseMode = ResponseMode.NARRATIVE,
                         context: Optional[RoleplayingContext] = None,
                         complexity: str = "standard",
                         use_cache: bool = True) -> LLMResponse:
        """
        Generate a synchronous LLM response.
        
        Args:
            prompt: The input prompt for the LLM
            mode: Response mode for optimal model selection
            context: Optional roleplaying context
            complexity: Complexity level for model selection
            use_cache: Whether to use response caching
            
        Returns:
            LLMResponse with the generated content
        """
        self.stats["total_requests"] += 1
        
        # Select optimal model
        model = self._get_optimal_model(mode, complexity)
        
        # Enhance prompt with context if provided
        enhanced_prompt = self._enhance_prompt_with_context(prompt, context, mode)
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._create_cache_key(enhanced_prompt, model, mode)
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return cached_response
            self.stats["cache_misses"] += 1
        
        # Validate API key
        if not self.api_key:
            return self._create_error_response(
                f"No API key configured for {self.config.provider.value}",
                model, mode, 0.0
            )
        
        # Make the API request with retries
        response = self._make_request_with_retries(enhanced_prompt, model, mode)
        
        # Cache successful responses
        if use_cache and response.success:
            self._cache_response(cache_key, response)
        
        return response
    
    def generate_roleplay_response(self,
                                 player_action: str,
                                 world_context: Dict[str, Any],
                                 character_context: Optional[RoleplayingContext] = None,
                                 intent_result: Optional[IntentResult] = None,
                                 action_result: Optional[ActionResult] = None) -> LLMResponse:
        """
        Generate a role-playing response based on player action and context.
        
        Args:
            player_action: The player's input action
            world_context: Current world/game state
            character_context: Character and scene context
            intent_result: Result from intent routing (if available)
            action_result: Result from action execution (if available)
            
        Returns:
            LLMResponse with role-playing narrative
        """
        # Determine response mode based on intent or action result
        mode = self._determine_response_mode(intent_result, action_result, world_context)
        
        # Build comprehensive prompt
        prompt = self._build_roleplay_prompt(
            player_action, world_context, character_context, intent_result, action_result
        )
        
        # Generate response with appropriate complexity
        complexity = self._determine_complexity(intent_result, action_result)
        
        return self.generate_response(prompt, mode, character_context, complexity)
    
    def generate_fallback_response(self,
                                 failed_input: str,
                                 error_context: Dict[str, Any],
                                 suggested_alternatives: List[str] = None) -> LLMResponse:
        """
        Generate a fallback response when parsing fails.
        
        Args:
            failed_input: The input that failed to parse
            error_context: Context about the parsing failure
            suggested_alternatives: Suggested alternative phrasings
            
        Returns:
            LLMResponse with helpful fallback content
        """
        prompt = self._build_fallback_prompt(failed_input, error_context, suggested_alternatives)
        
        return self.generate_response(
            prompt, 
            ResponseMode.FALLBACK, 
            complexity="fast"  # Use fast model for fallbacks
        )
    
    # ============================================================================
    # RETRY AND ERROR HANDLING
    # ============================================================================
    
    async def _make_request_with_retries_async(self, prompt: str, model: str, mode: ResponseMode) -> LLMResponse:
        """Make API request with retry logic (async)."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = await self._make_async_request(prompt, model, mode)
                if response.success:
                    return response
                
                # If not successful, treat as error for retry
                last_error = response.error or "Unknown error"
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            
            # Wait before retry (with exponential backoff)
            if attempt < self.config.max_retries - 1:
                wait_time = self.config.retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
        
        # All retries failed
        return self._create_error_response(
            f"All {self.config.max_retries} attempts failed. Last error: {last_error}",
            model, mode, 0.0
        )
    
    def _make_request_with_retries(self, prompt: str, model: str, mode: ResponseMode) -> LLMResponse:
        """Make API request with retry logic (sync)."""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = self._make_sync_request(prompt, model, mode)
                if response.success:
                    return response
                
                # If not successful, treat as error for retry
                last_error = response.error or "Unknown error"
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            
            # Wait before retry (with exponential backoff)
            if attempt < self.config.max_retries - 1:
                wait_time = self.config.retry_delay * (2 ** attempt)
                time.sleep(wait_time)
        
        # All retries failed
        return self._create_error_response(
            f"All {self.config.max_retries} attempts failed. Last error: {last_error}",
            model, mode, 0.0
        )
    
    # ============================================================================
    # PROMPT BUILDING AND CONTEXT ENHANCEMENT
    # ============================================================================
    
    def _enhance_prompt_with_context(self, 
                                   prompt: str, 
                                   context: Optional[RoleplayingContext], 
                                   mode: ResponseMode) -> str:
        """Enhance the base prompt with roleplaying context."""
        if not context:
            return prompt
        
        context_parts = []
        
        # Add character context
        if context.character_name:
            context_parts.append(f"Character: {context.character_name}")
        
        if context.character_personality:
            context_parts.append(f"Personality: {context.character_personality}")
        
        # Add scene context
        if context.scene_description:
            context_parts.append(f"Scene: {context.scene_description}")
        
        # Add emotional state
        if context.emotional_state and context.emotional_state != "neutral":
            context_parts.append(f"Emotional State: {context.emotional_state}")
        
        # Add narrative tone
        if context.narrative_tone and context.narrative_tone != "balanced":
            context_parts.append(f"Tone: {context.narrative_tone}")
        
        # Add recent actions context
        if context.previous_actions:
            recent_actions = context.previous_actions[-3:]  # Last 3 actions
            context_parts.append(f"Recent Actions: {', '.join(recent_actions)}")
        
        # Combine context with prompt
        if context_parts:
            context_string = " | ".join(context_parts)
            return f"[Context: {context_string}]\n\n{prompt}"
        
        return prompt
    
    def _determine_response_mode(self, 
                               intent_result: Optional[IntentResult],
                               action_result: Optional[ActionResult],
                               world_context: Dict[str, Any]) -> ResponseMode:
        """Determine the appropriate response mode based on context."""
        # Check action result first
        if action_result:
            if action_result.action_category == "combat":
                return ResponseMode.COMBAT
            elif action_result.action_category in ["communication", "social"]:
                return ResponseMode.SOCIAL
            elif action_result.action_category in ["movement", "observation"]:
                return ResponseMode.EXPLORATION
        
        # Check intent result
        if intent_result:
            if intent_result.primary_intent == PrimaryIntent.COMBAT:
                return ResponseMode.COMBAT
            elif intent_result.primary_intent == PrimaryIntent.SOCIAL:
                return ResponseMode.DIALOGUE
            elif intent_result.primary_intent == PrimaryIntent.EXPLORATION:
                return ResponseMode.EXPLORATION
            elif intent_result.primary_intent == PrimaryIntent.CREATIVE:
                return ResponseMode.CREATIVE
        
        # Check world context
        if world_context.get("in_combat", False):
            return ResponseMode.COMBAT
        elif world_context.get("in_dialogue", False):
            return ResponseMode.DIALOGUE
        
        # Default to narrative
        return ResponseMode.NARRATIVE
    
    def _determine_complexity(self, 
                            intent_result: Optional[IntentResult],
                            action_result: Optional[ActionResult]) -> str:
        """Determine the complexity level needed for the response."""
        # High complexity for creative or analytical tasks
        if intent_result and intent_result.primary_intent == PrimaryIntent.CREATIVE:
            return "premium"
        
        # Standard complexity for most interactions
        if action_result and action_result.success:
            return "standard"
        
        # Fast complexity for simple responses
        return "fast"
    
    def _build_roleplay_prompt(self,
                             player_action: str,
                             world_context: Dict[str, Any],
                             character_context: Optional[RoleplayingContext],
                             intent_result: Optional[IntentResult],
                             action_result: Optional[ActionResult]) -> str:
        """Build a comprehensive role-playing prompt."""
        prompt_parts = []
        
        # Base instruction
        prompt_parts.append("You are an AI Game Master for a text-based fantasy RPG.")
        prompt_parts.append("Generate an immersive, engaging response to the player's action.")
        
        # World context
        if world_context:
            location = world_context.get("location_name", "unknown location")
            prompt_parts.append(f"Current Location: {location}")
            
            if world_context.get("location_description"):
                prompt_parts.append(f"Location Description: {world_context['location_description']}")
            
            if world_context.get("npcs_present"):
                npcs = ", ".join(world_context["npcs_present"])
                prompt_parts.append(f"NPCs Present: {npcs}")
        
        # Action context
        prompt_parts.append(f"Player Action: {player_action}")
        
        if action_result:
            if action_result.success:
                prompt_parts.append(f"Action Result: {action_result.result_text}")
                if action_result.narrative_impact:
                    prompt_parts.append(f"Narrative Impact: {action_result.narrative_impact}")
            else:
                prompt_parts.append(f"Action Failed: {action_result.error_message}")
        
        # Intent context
        if intent_result:
            prompt_parts.append(f"Player Intent: {intent_result.primary_intent.value}")
            if intent_result.confidence < 0.8:
                prompt_parts.append("(The player's intent is somewhat unclear)")
        
        # Response guidelines
        prompt_parts.append("\nResponse Guidelines:")
        prompt_parts.append("- Keep responses concise but vivid (2-4 sentences)")
        prompt_parts.append("- Focus on immediate consequences and sensory details")
        prompt_parts.append("- Maintain immersive fantasy atmosphere")
        prompt_parts.append("- If action failed, suggest alternative approaches")
        
        return "\n".join(prompt_parts)
    
    def _build_fallback_prompt(self,
                             failed_input: str,
                             error_context: Dict[str, Any],
                             suggested_alternatives: List[str] = None) -> str:
        """Build a prompt for handling parsing failures."""
        prompt_parts = []
        
        prompt_parts.append("The player input could not be understood by the game parser.")
        prompt_parts.append("Provide a helpful, in-character response that:")
        prompt_parts.append("1. Acknowledges the confusion in a friendly way")
        prompt_parts.append("2. Suggests clearer ways to phrase the action")
        prompt_parts.append("3. Maintains the fantasy game atmosphere")
        
        prompt_parts.append(f"\nPlayer Input: {failed_input}")
        
        if error_context.get("parsing_error"):
            prompt_parts.append(f"Parsing Error: {error_context['parsing_error']}")
        
        if suggested_alternatives:
            alternatives = ", ".join(suggested_alternatives[:3])  # Limit to 3 suggestions
            prompt_parts.append(f"Suggested Alternatives: {alternatives}")
        
        prompt_parts.append("\nRespond as a helpful game master who wants to keep the player engaged.")
        
        return "\n".join(prompt_parts)
    
    # ============================================================================
    # UTILITY AND MANAGEMENT METHODS  
    # ============================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        total_requests = self.stats["total_requests"]
        if total_requests > 0:
            success_rate = self.stats["successful_requests"] / total_requests
            cache_hit_rate = self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0
        else:
            success_rate = 0
            cache_hit_rate = 0
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self._response_cache),
            "provider": self.config.provider.value,
            "has_api_key": bool(self.api_key)
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self._response_cache.clear()
        self.logger.info("Response cache cleared")
    
    def update_config(self, new_config: LLMConfig):
        """Update the LLM configuration."""
        self.config = new_config
        self.api_key = self._get_api_key()
        self.logger.info(f"Configuration updated for {self.config.provider.value}")
    
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info("LLMRoleplayer closed")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        if hasattr(self, 'session') and self.session and not getattr(self.session, 'closed', True):
            # Note: In real async code, you should call close() explicitly
            pass


# ============================================================================
# FACTORY FUNCTIONS AND UTILITIES
# ============================================================================

def create_llm_roleplayer(provider: str = "openrouter", 
                         model: str = None,
                         **config_kwargs) -> LLMRoleplayer:
    """
    Factory function to create an LLMRoleplayer with common configurations.
    
    Args:
        provider: Provider name ("openrouter", "openai", "anthropic")
        model: Specific model to use (optional)
        **config_kwargs: Additional configuration parameters
        
    Returns:
        Configured LLMRoleplayer instance
    """
    provider_enum = LLMProvider(provider.lower())
    
    config = LLMConfig(provider=provider_enum, **config_kwargs)
    if model:
        config.model = model
    
    return LLMRoleplayer(config)


def create_development_roleplayer() -> LLMRoleplayer:
    """Create an LLMRoleplayer configured for development."""
    config = LLMConfig(
        provider=LLMProvider.OPENROUTER,
        model="openai/gpt-3.5-turbo",  # Faster/cheaper for development
        max_tokens=300,
        temperature=0.8,
        timeout=15.0,
        max_retries=2
    )
    return LLMRoleplayer(config)


def create_production_roleplayer() -> LLMRoleplayer:
    """Create an LLMRoleplayer configured for production."""
    config = LLMConfig(
        provider=LLMProvider.OPENROUTER,
        model="openai/gpt-4o",  # Higher quality for production
        max_tokens=500,
        temperature=0.7,
        timeout=30.0,
        max_retries=3
    )
    return LLMRoleplayer(config)
