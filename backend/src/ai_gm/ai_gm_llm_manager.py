"""
AI GM Brain - LLM Integration Manager

This module provides the integration layer between the AI GM Brain and 
the OpenRouter API for LLM-based response generation.
"""

import os
import logging
import json
import time
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# Import from core brain
from .ai_gm_brain import AIGMBrain, ProcessingMode


class LLMInteractionManager:
    """
    Manager for LLM interactions with cost optimization and context management.
    
    This class handles:
    1. LLM prompt construction
    2. API calls with appropriate error handling
    3. Response processing and extraction
    4. Cost optimization strategies
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the LLM interaction manager.
        
        Args:
            ai_gm_brain: Reference to the parent AI GM Brain
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"LLMManager_{ai_gm_brain.game_id}")
        
        # API configuration
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        self.api_base_url = "https://openrouter.ai/api/v1"
        self.default_model = "openai/gpt-4o"
        
        # Cost optimization
        self.total_tokens_used = 0
        self.last_call_time = None
        self.rate_limit_delay = 1.0  # seconds
        self.default_temperature = 0.7
        
        # Session for API calls
        self.session = None
        
        # Model selection tiers
        self.model_tiers = {
            "fast": "openai/gpt-3.5-turbo",
            "standard": "openai/gpt-4o",
            "premium": "anthropic/claude-3-opus"
        }
        
        self.logger.info("LLM Interaction Manager initialized")
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def generate_response(self, 
                               input_text: str,
                               context: Dict[str, Any],
                               response_type: str = "narrative",
                               model_tier: str = "standard",
                               max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate an LLM response based on input and context.
        
        Args:
            input_text: User input text
            context: Game context for prompt construction
            response_type: Type of response to generate
            model_tier: Model tier to use (fast, standard, premium)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response data dictionary
        """
        start_time = time.time()
        
        # Check if API key is available
        if not self.api_key:
            return self._generate_error_response(
                "OpenRouter API key not available. Set the OPENROUTER_API_KEY environment variable.",
                start_time
            )
        
        # Rate limiting
        if self.last_call_time:
            elapsed = time.time() - self.last_call_time
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        
        # Construct the prompt
        prompt = self._construct_prompt(input_text, context, response_type)
        
        # Select model based on tier
        model = self.model_tiers.get(model_tier, self.default_model)
        
        try:
            # Make API call
            await self.ensure_session()
            
            # Set up the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                "max_tokens": max_tokens,
                "temperature": self.default_temperature
            }
            
            async with self.session.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                self.last_call_time = time.time()
                
                if response.status != 200:
                    error_text = await response.text()
                    return self._generate_error_response(
                        f"API error (status {response.status}): {error_text}",
                        start_time
                    )
                
                response_data = await response.json()
                
                # Extract content from response
                llm_response = response_data["choices"][0]["message"]["content"]
                
                # Update token usage
                usage = response_data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                
                self.total_tokens_used += total_tokens
                
                processing_time = time.time() - start_time
                self.logger.info(
                    f"Generated {response_type} response in {processing_time:.3f}s "
                    f"using {total_tokens} tokens ({prompt_tokens} prompt, {completion_tokens} completion)"
                )
                
                # Prepare successful response
                return {
                    "response_text": llm_response,
                    "requires_llm": True,
                    "response_type": response_type,
                    "model_used": model,
                    "processing_time": processing_time,
                    "token_usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens
                    }
                }
                
        except Exception as e:
            self.logger.error(f"LLM API error: {str(e)}")
            return self._generate_error_response(f"LLM API error: {str(e)}", start_time)
    
    def _construct_prompt(self, 
                         input_text: str, 
                         context: Dict[str, Any],
                         response_type: str) -> Dict[str, str]:
        """
        Construct a prompt for the LLM based on input type and context.
        
        Args:
            input_text: User input text
            context: Game context information
            response_type: Type of response to generate
            
        Returns:
            Dictionary with system and user prompts
        """
        # Basic context elements
        player_name = context.get("player_name", "the player")
        location_name = context.get("location_name", "the current area")
        location_description = context.get("location_description", "")
        
        # Recent events
        recent_events = context.get("recent_events", [])
        recent_events_text = "\n".join([f"- {event}" for event in recent_events[-5:]])
        
        # NPC information
        active_npcs = context.get("active_npcs", [])
        npcs_text = "\n".join([f"- {npc['name']}: {npc['description']}" for npc in active_npcs])
        
        # Character information
        character_info = context.get("character_info", {})
        domains = character_info.get("domains", {})
        domains_text = "\n".join([f"- {domain}: {level}" for domain, level in domains.items()])
        
        # System prompt varies by response type
        system_prompts = {
            "narrative": f"""You are the AI Game Master for a narrative text-based RPG. 
Your primary goal is to provide immersive, descriptive responses that advance the story 
and create a rich world for {player_name} to explore.

Follow these guidelines:
1. Write in second person perspective ("You see...", "You feel...")
2. Be descriptive but concise
3. Include sensory details to make the world feel alive
4. Maintain a consistent tone appropriate to the game world
5. Avoid breaking the fourth wall or referencing game mechanics directly
6. Provide clear hints about possible actions without being too explicit

The game uses a domain-based character system with d20 dice rolls:
{domains_text}

Response should be 3-5 paragraphs of rich, evocative text.""",

            "dialogue": f"""You are the AI Game Master roleplaying as an NPC in a narrative text-based RPG.
Your responses should be in-character dialogue that creates an immersive, interactive conversation 
between the NPC and {player_name}.

Follow these guidelines:
1. Stay completely in character for the NPC
2. Write realistic dialogue that reflects the NPC's personality
3. Include minimal narration for tone and actions
4. Don't describe the player's responses or actions
5. Keep responses shorter than 3-4 paragraphs
6. End with something that invites further conversation

Response should be purely dialogue with minimal narration.""",

            "combat": f"""You are the AI Game Master narrating combat in a domain-based RPG.
Your response should create a vivid, dynamic description of the combat exchange between 
{player_name} and their opponent.

Follow these guidelines:
1. Describe actions with exciting, visceral language
2. Focus on the impact and consequences of actions
3. Include environmental details that affect the combat
4. Highlight domain-based abilities when relevant
5. Maintain tension and stakes
6. End with a clear state of the combat (who has advantage, injuries, etc.)

Response should be 2-3 paragraphs of action-oriented description."""
        }
        
        # Default to narrative if type not found
        system_prompt = system_prompts.get(response_type, system_prompts["narrative"])
        
        # User prompt includes context and the player's input
        user_prompt = f"""
CURRENT LOCATION: {location_name}
{location_description}

ACTIVE NPCs:
{npcs_text}

RECENT EVENTS:
{recent_events_text}

PLAYER INPUT: {input_text}

Respond as the Game Master, providing an immersive {response_type} response.
"""
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def _generate_error_response(self, error_message: str, start_time: float) -> Dict[str, Any]:
        """
        Generate an error response when LLM generation fails.
        
        Args:
            error_message: Error message
            start_time: Start time for processing time calculation
            
        Returns:
            Error response dictionary
        """
        self.logger.error(f"LLM error: {error_message}")
        
        return {
            "response_text": "I'm having trouble generating a response right now. Let's try a different approach.",
            "requires_llm": True,
            "response_type": "error",
            "error": error_message,
            "processing_time": time.time() - start_time
        }
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about LLM usage.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "total_tokens_used": self.total_tokens_used,
            "last_call_time": self.last_call_time,
            "default_model": self.default_model
        }


# Extension function to add LLM capabilities to AI GM Brain
def extend_ai_gm_brain_with_llm(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with LLM integration capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create LLM manager
    llm_manager = LLMInteractionManager(ai_gm_brain)
    
    # Store the original process_conversational_input method
    original_process_conversational = ai_gm_brain._process_conversational_input
    
    # Replace with LLM-powered version
    async def llm_process_conversational(input_string: str) -> Dict[str, Any]:
        """Process conversational input with LLM."""
        # Get context from memory and current state
        context = {
            "player_name": "Player",  # Would come from character system
            "location_name": ai_gm_brain.current_location or "Unknown Location",
            "location_description": "A nondescript area.",  # Would come from location system
            "recent_events": ["An event occurred"],  # Would come from memory system
            "active_npcs": [],  # Would come from NPC system
            "character_info": {
                "domains": {
                    "BODY": 2,
                    "MIND": 3,
                    "SPIRIT": 1
                }
            }  # Would come from character system
        }
        
        # Generate response with LLM
        response = await llm_manager.generate_response(
            input_text=input_string,
            context=context,
            response_type="narrative"
        )
        
        # Update last LLM interaction time
        ai_gm_brain.last_llm_interaction = datetime.utcnow()
        
        return response
    
    # Set up sync proxy for the async function
    def _process_conversational_input_proxy(input_string: str) -> Dict[str, Any]:
        """Synchronous proxy for the async LLM processing method."""
        # For simplicity in Phase 1, just use a template response
        # We'll implement the full async version in Phase 2
        return original_process_conversational(input_string)
    
    # Store references for later phases
    ai_gm_brain.llm_manager = llm_manager
    ai_gm_brain._llm_process_conversational = llm_process_conversational
    
    # We'll replace this in Phase 2 with the async version
    # ai_gm_brain._process_conversational_input = _process_conversational_input_proxy