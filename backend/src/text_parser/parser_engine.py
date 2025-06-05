"""
Parser Engine - Core text parsing capabilities for the AI GM system

This module provides the main parsing engine that converts player input text
into structured command objects for the AI GM to process.
"""

import re
import logging
import random
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
import os
import json

import spacy
from spacy.pipeline import EntityRuler

# LangChain imports for Phase 2 and Phase 3 integration
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.memory import ConversationBufferMemory

# Phase 3: Advanced LangChain imports - Use the current ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.agents.openai_tools.base import create_openai_tools_agent

# Import for correct method signature
from langchain_core.language_models import LanguageModelInput
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Optional

# Import VocabularyManager for Phase 2 integration
from .vocabulary_manager import vocabulary_manager

logger = logging.getLogger("text_parser")


# Phase 3: OpenRouter LLM for real LLM integration
class OpenRouterLLM(ChatOpenAI):
    """OpenRouter LLM integration for LangChain agents."""
    
    def __init__(self, model_name: str = None, **kwargs):
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            logger.warning("OPENROUTER_API_KEY not found, using dummy key for testing")
            api_key = "dummy-key"
        
        # Use environment variable for model, or use OpenRouter account default
        if model_name is None:
            model_name = os.environ.get('OPENROUTER_MODEL')
            
        # Store whether to use account default in __dict__ to avoid Pydantic validation
        use_account_default = False
        
        # If no model specified or empty string, use OpenRouter account default
        if not model_name:
            logger.info("No model specified, using OpenRouter account default (qwen/qwen3-32b:free)")
            use_account_default = True
            # We'll leave model_name empty and handle this in the API call
            model_name = ""  # This will trigger OpenRouter account default
        else:
            logger.info(f"Using specified model: {model_name}")
        
        # Use a dummy model name for LangChain initialization if using account default
        langchain_model_name = model_name if model_name else "gpt-3.5-turbo"
        
        super().__init__(
            model_name=langchain_model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.1,  # Low temperature for consistent parsing
            max_tokens=200,   # Keep responses concise
            **kwargs
        )
        
        # Set after super().__init__ to avoid Pydantic field validation
        object.__setattr__(self, '_use_account_default', use_account_default)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override to handle OpenRouter account default model."""
        # If using account default, we need to modify the request
        if getattr(self, '_use_account_default', False):
            # Override the model in the request to be empty for account default
            original_model = self.model_name
            self.model_name = ""  # Empty string triggers OpenRouter account default
            try:
                result = super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                return result
            finally:
                self.model_name = original_model  # Restore original
        else:
            return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


# Phase 4: GameSystemsManager for accessing real game systems
class GameSystemsManager:
    """
    Provides LangChain tools with access to the game engine's integrated systems.
    Centralizes system access and handles error scenarios gracefully.
    """
    
    def __init__(self):
        """Initialize the game systems manager."""
        self.logger = logging.getLogger("text_parser.game_systems")
        self._systems = {}
        self._integration_manager = None
        self._nlp_processor = None
        self._setup_systems()
    
    def _setup_systems(self):
        """Initialize connections to game systems."""
        try:
            # Import and initialize System Integration Manager
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, '..', '..', '..')
            sys.path.insert(0, project_root)
            
            from system_integration_manager import SystemIntegrationManager
            
            # Create a default session for tool usage
            self._integration_manager = SystemIntegrationManager(
                session_id="langchain_tools_session",
                player_id="default_player"
            )
            
            # Initialize all available systems
            self._integration_manager.initialize_all_systems()
            
            # Store direct references for quick access
            self._systems = self._integration_manager.systems
            
            self.logger.info(f"GameSystemsManager initialized with {len(self._systems)} systems")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GameSystemsManager: {e}")
            self._systems = {}
    
    def get_ai_gm(self):
        """Get the AI GM system for narrative generation."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.AI_GM)
    
    def get_combat_system(self):
        """Get the combat system for battle mechanics."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.COMBAT)
    
    def get_magic_system(self):
        """Get the magic system for spell casting."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.MAGIC)
    
    def get_crafting_system(self):
        """Get the crafting system for item creation."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.CRAFTING)
    
    def get_economy_system(self):
        """Get the economy system for trade and currency."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.ECONOMY)
    
    def get_text_parser(self):
        """Get the text parser system."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.TEXT_PARSER)
    
    def get_npc_system(self):
        """Get the NPC system for character interactions."""
        from system_integration_manager import SystemType
        return self._systems.get(SystemType.NPC)
    
    def process_through_integration(self, input_text: str) -> Dict[str, Any]:
        """Process input through the full integration manager."""
        if self._integration_manager:
            try:
                return self._integration_manager.process_player_input(input_text)
            except Exception as e:
                self.logger.error(f"Integration processing failed: {e}")
                return self._fallback_response(input_text, "integration_error")
        else:
            return self._fallback_response(input_text, "no_integration")
    
    def _fallback_response(self, input_text: str, error_type: str) -> Dict[str, Any]:
        """Generate fallback response when systems are unavailable."""
        return {
            "action": "system_fallback",
            "target": input_text,
            "confidence": 0.3,
            "error_type": error_type,
            "message": "Game systems are currently unavailable. Using basic text processing.",
            "success": False
        }


# Global game systems manager instance
_game_systems = GameSystemsManager()


# Phase 4: Enhanced LangChain Tools with Real Game System Integration
class MoveTool(BaseTool):
    """Tool for movement actions with real game system integration."""
    name = "move"
    description = "Use this tool when the player wants to move or go somewhere. Input should be the direction or destination."
    
    def _run(self, query: str) -> str:
        try:
            # Process through full integration for movement
            result = _game_systems.process_through_integration(f"go {query.strip()}")
            
            if result.get('success'):
                return json.dumps({
                    "action": "go",
                    "target": query.strip(),
                    "confidence": 0.9,
                    "tool_used": "MoveTool",
                    "system_response": result.get('response_text', ''),
                    "game_state_changes": result.get('metadata', {}).get('mechanical_changes', [])
                })
            else:
                # Fallback to basic response
                return json.dumps({
                    "action": "go",
                    "target": query.strip(),
                    "confidence": 0.6,
                    "tool_used": "MoveTool",
                    "message": f"You attempt to move {query.strip()}."
                })
                
        except Exception as e:
            logger.error(f"MoveTool error: {e}")
            return json.dumps({
                "action": "go",
                "target": query.strip(),
                "confidence": 0.4,
                "tool_used": "MoveTool",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class LookTool(BaseTool):
    """Tool for observation actions with enhanced inventory and spatial integration."""
    name = "look"
    description = "Use this tool when the player wants to look at, examine, or observe something. Input should be what they want to look at."
    
    def _run(self, query: str) -> str:
        try:
            # Parse natural language query for spatial context
            parsed_query = self._parse_look_query(query)
            
            # Try inventory system integration first for spatial awareness
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Get player's current location
                    player_location = inventory_system.get_player_location("default_player")
                    
                    if player_location:
                        # If no specific target, look around the location
                        if not parsed_query["target"] or parsed_query["target"].lower() in ["around", "here", "location", "room"]:
                            return self._look_around_location(inventory_system, player_location, parsed_query)
                        
                        # If specific target mentioned, look for it
                        elif parsed_query["target"]:
                            return self._look_at_target(inventory_system, player_location, parsed_query)
            
            # Fallback to AI GM for rich descriptions
            ai_gm = _game_systems.get_ai_gm()
            if ai_gm:
                try:
                    look_prompt = f"describe {query.strip()}" if query.strip() else "look around"
                    ai_response = ai_gm.process_player_input(look_prompt)
                    
                    return json.dumps({
                        "action": "look",
                        "target": query.strip() if query.strip() else None,
                        "confidence": 0.95,
                        "tool_used": "LookTool",
                        "system_response": ai_response.get('response', ''),
                        "ai_description": ai_response.get('response', ''),
                        "narrative_elements": ai_response.get('narrative_elements', [])
                    })
                except Exception as e:
                    logger.warning(f"AI GM unavailable for LookTool: {e}")
            
            # Final fallback processing
            result = _game_systems.process_through_integration(f"look {query.strip()}" if query.strip() else "look")
            
            return json.dumps({
                "action": "look", 
                "target": query.strip() if query.strip() else None,
                "confidence": 0.8,
                "tool_used": "LookTool",
                "system_response": result.get('response_text', f"You examine {query.strip() if query.strip() else 'your surroundings'}.")
            })
            
        except Exception as e:
            logger.error(f"LookTool error: {e}")
            return json.dumps({
                "action": "look",
                "target": query.strip() if query.strip() else None,
                "confidence": 0.5,
                "tool_used": "LookTool",
                "system_response": f"Unable to examine {query.strip() if query.strip() else 'surroundings'}: {str(e)}",
                "error": str(e)
            })
    
    def _parse_look_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language look query for spatial context."""
        query_lower = query.lower().strip()
        
        # Extract container/location context
        container_keywords = ["in", "inside", "within", "on", "under", "behind", "from"]
        item_keywords = ["for", "at"]
        
        parsed = {
            "target": None,
            "container": None,
            "search_type": "general",
            "prepositions": []
        }
        
        if not query_lower:
            parsed["search_type"] = "area"
            return parsed
        
        # Use spaCy for more sophisticated parsing if available
        try:
            doc = _game_systems.get_nlp_processor().process(query_lower) if hasattr(_game_systems, 'get_nlp_processor') else None
            if doc:
                # Extract entities and relationships
                for token in doc:
                    if token.dep_ == "pobj" and token.head.text in container_keywords:
                        parsed["container"] = token.text
                        parsed["prepositions"].append(token.head.text)
                    elif token.dep_ in ["dobj", "obj"] and token.head.lemma_ in ["look", "examine"]:
                        parsed["target"] = token.text
        except:
            # Fallback to simple parsing
            pass
        
        # Enhanced pattern matching for natural language sentences
        if "around" in query_lower or "here" in query_lower or not query_lower:
            parsed["search_type"] = "area"
        elif any(keyword in query_lower for keyword in container_keywords):
            # Handle patterns like "look for sword in chest" or "examine the book on table"
            parts = query_lower.split()
            for i, word in enumerate(parts):
                if word in container_keywords and i + 1 < len(parts):
                    # Extract container name (handle "the" articles)
                    container_part = " ".join(parts[i+1:])
                    if container_part.startswith("the "):
                        container_part = container_part[4:]
                    parsed["container"] = container_part
                    
                    # Extract target from before the preposition
                    if i > 0:
                        target_part = " ".join(parts[:i])
                        # Remove common action words and articles
                        target_part = target_part.replace("look for", "").replace("look at", "").replace("examine", "").replace("the ", "").strip()
                        if target_part:
                            parsed["target"] = target_part
                    break
        else:
            # Clean target by removing action words
            target = query_lower.replace("look at", "").replace("examine", "").replace("look for", "").replace("the ", "").strip()
            parsed["target"] = target if target else query_lower
            parsed["search_type"] = "item" if any(kw in query_lower for kw in item_keywords) else "general"
        
        return parsed
    
    def _get_container_description_with_behaviors(self, container_info: Dict[str, Any], location_container_system) -> str:
        """Get enhanced container description based on type behaviors."""
        container_type = container_info.get("type", "container")
        behaviors = location_container_system.get_container_type_behaviors(container_type)
        
        description = container_info["name"]
        
        # Add type-specific hints
        if "discovery_hint" in behaviors:
            description = behaviors["discovery_hint"]
        
        # Add lock status with type-specific context
        if container_info.get("is_locked", False):
            if container_info.get("key_required"):
                description += " (locked - key required)"
            else:
                unlock_modifier = behaviors.get("unlock_difficulty_modifier", 0)
                if unlock_modifier > 5:
                    description += " (heavily secured)"
                elif unlock_modifier < 0:
                    description += " (simple lock)"
                else:
                    description += " (locked)"
        else:
            # Show contents for unlocked containers
            if container_info["items"]:
                item_count = len(container_info["items"])
                description += f" (contains {item_count} item{'s' if item_count != 1 else ''})"
        
        # Add special requirements hints
        if "special_requirements" in behaviors:
            description += f" - {behaviors['special_requirements']}"
        elif "special_search" in behaviors:
            description += " (may require careful examination)"
        
        return description

    def _look_around_location(self, inventory_system, location_id: str, parsed_query: Dict[str, Any]) -> str:
        """Generate description of current location with items and containers."""
        try:
            # Get location container system
            location_container_system = inventory_system.location_container_system
            if not location_container_system:
                return json.dumps({
                    "action": "look",
                    "target": "location",
                    "confidence": 0.6,
                    "tool_used": "LookTool",
                    "system_response": "You look around the area."
                })
            
            # Get all items and containers at location
            location_data = location_container_system.get_items_at_location(location_id)
            
            # Build description
            description_parts = ["You look around the area."]
            
            # Describe ground items
            if location_data["ground_items"]:
                items_list = []
                for item_id, item_info in location_data["ground_items"].items():
                    quantity_text = f"{item_info['quantity']}x " if item_info['quantity'] > 1 else ""
                    items_list.append(f"{quantity_text}{item_info['name']}")
                
                if items_list:
                    description_parts.append(f"On the ground you see: {', '.join(items_list)}.")
            
            # Describe containers
            if location_data["containers"]:
                visible_containers = []
                locked_containers = []
                for container_id, container_info in location_data["containers"].items():
                    if not container_info.get("is_hidden", False):
                        container_desc = self._get_container_description_with_behaviors(
                            container_info, location_container_system
                        )
                        
                        if container_info.get("is_locked", False):
                            locked_containers.append(container_desc)
                        else:
                            visible_containers.append(container_desc)
                
                if visible_containers:
                    description_parts.append(f"You notice: {', '.join(visible_containers)}.")
                if locked_containers:
                    description_parts.append(f"You also see: {', '.join(locked_containers)}.")
            
            full_description = " ".join(description_parts)
            
            return json.dumps({
                "action": "look",
                "target": "location",
                "confidence": 0.95,
                "tool_used": "LookTool",
                "system_response": full_description,
                "location_data": location_data,
                "spatial_context": {
                    "location_id": location_id,
                    "ground_items_count": len(location_data["ground_items"]),
                    "containers_count": len(location_data["containers"])
                }
            })
            
        except Exception as e:
            logger.error(f"Error looking around location: {e}")
            return json.dumps({
                "action": "look",
                "target": "location",
                "confidence": 0.5,
                "tool_used": "LookTool",
                "system_response": "You look around the area.",
                "error": str(e)
            })
    
    def _look_at_target(self, inventory_system, location_id: str, parsed_query: Dict[str, Any]) -> str:
        """Look at a specific target (item, container, etc.)."""
        try:
            target = parsed_query["target"]
            container_target = parsed_query.get("container")
            
            location_container_system = inventory_system.location_container_system
            if not location_container_system:
                return json.dumps({
                    "action": "look",
                    "target": target,
                    "confidence": 0.6,
                    "tool_used": "LookTool",
                    "system_response": f"You examine {target}."
                })
            
            # If looking in/at a specific container
            if container_target:
                return self._look_in_container(location_container_system, location_id, container_target, target)
            
            # Otherwise, look for the target in the location
            location_data = location_container_system.get_items_at_location(location_id)
            
            # Check ground items first
            for item_id, item_info in location_data["ground_items"].items():
                if (target.lower() in item_info["name"].lower() or 
                    target.lower() in item_id.lower()):
                    
                    quantity_text = f"({item_info['quantity']} available) " if item_info['quantity'] > 1 else ""
                    description = f"You examine the {item_info['name']}. {quantity_text}{item_info.get('description', 'A standard item.')}"
                    
                    return json.dumps({
                        "action": "look",
                        "target": target,
                        "confidence": 0.92,
                        "tool_used": "LookTool",
                        "system_response": description,
                        "item_found": {
                            "id": item_id,
                            "name": item_info["name"],
                            "quantity": item_info["quantity"],
                            "location": "ground"
                        }
                    })
            
            # Check containers
            for container_id, container_info in location_data["containers"].items():
                if (target.lower() in container_info["name"].lower() or
                    target.lower() in container_info["type"].lower()):
                    
                    items_desc = ""
                    if container_info["items"]:
                        item_names = [info["name"] for info in container_info["items"].values()]
                        items_desc = f" It contains: {', '.join(item_names)}."
                    elif not container_info.get("is_locked", False):
                        items_desc = " It appears to be empty."
                    elif container_info.get("is_locked", False):
                        items_desc = " It is locked and you cannot see inside."
                    
                    description = f"You examine the {container_info['name']}. {container_info.get('description', 'A container.')}{items_desc}"
                    
                    return json.dumps({
                        "action": "look",
                        "target": target,
                        "confidence": 0.92,
                        "tool_used": "LookTool",
                        "system_response": description,
                        "container_found": {
                            "id": container_id,
                            "name": container_info["name"],
                            "type": container_info["type"],
                            "items": container_info["items"],
                            "is_locked": container_info.get("is_locked", False)
                        }
                    })
            
            # Target not found at location
            return json.dumps({
                "action": "look",
                "target": target,
                "confidence": 0.8,
                "tool_used": "LookTool",
                "system_response": f"You don't see any '{target}' here."
            })
            
        except Exception as e:
            logger.error(f"Error looking at target: {e}")
            return json.dumps({
                "action": "look",
                "target": parsed_query.get("target", ""),
                "confidence": 0.5,
                "tool_used": "LookTool",
                "system_response": f"Unable to examine the target.",
                "error": str(e)
            })
    
    def _look_in_container(self, location_container_system, location_id: str, container_name: str, target: str = None) -> str:
        """Look inside a specific container."""
        try:
            location_data = location_container_system.get_items_at_location(location_id)
            
            # Find the container
            target_container = None
            target_container_id = None
            
            for container_id, container_info in location_data["containers"].items():
                if (container_name.lower() in container_info["name"].lower() or
                    container_name.lower() in container_info["type"].lower()):
                    target_container = container_info
                    target_container_id = container_id
                    break
            
            if not target_container:
                return json.dumps({
                    "action": "look",
                    "target": f"{target} in {container_name}" if target else container_name,
                    "confidence": 0.8,
                    "tool_used": "LookTool",
                    "system_response": f"You don't see any '{container_name}' here."
                })
            
            if target_container.get("is_locked", False):
                # Enhanced locked container feedback
                lock_info = self._analyze_lock_status(target_container)
                return json.dumps({
                    "action": "look",
                    "target": f"{target} in {container_name}" if target else container_name,
                    "confidence": 0.9,
                    "tool_used": "LookTool",
                    "system_response": lock_info["description"],
                    "lock_status": lock_info,
                    "unlock_suggestions": lock_info["suggestions"]
                })
            
            # If looking for specific item in container
            if target:
                for item_id, item_info in target_container["items"].items():
                    if (target.lower() in item_info["name"].lower() or
                        target.lower() in item_id.lower()):
                        
                        quantity_text = f"({item_info['quantity']} available) " if item_info['quantity'] > 1 else ""
                        description = f"Inside the {target_container['name']}, you see {item_info['name']}. {quantity_text}{item_info.get('description', 'A standard item.')}"
                        
                        return json.dumps({
                            "action": "look",
                            "target": f"{target} in {container_name}",
                            "confidence": 0.95,
                            "tool_used": "LookTool",
                            "system_response": description,
                            "item_found": {
                                "id": item_id,
                                "name": item_info["name"],
                                "quantity": item_info["quantity"],
                                "location": target_container_id
                            }
                        })
                
                return json.dumps({
                    "action": "look",
                    "target": f"{target} in {container_name}",
                    "confidence": 0.9,
                    "tool_used": "LookTool",
                    "system_response": f"You don't see any '{target}' in the {target_container['name']}."
                })
            
            # Look at container contents generally
            if target_container["items"]:
                item_names = [f"{info['name']} (x{info['quantity']})" if info['quantity'] > 1 else info['name'] 
                             for info in target_container["items"].values()]
                description = f"Inside the {target_container['name']}, you see: {', '.join(item_names)}."
            else:
                description = f"The {target_container['name']} is empty."
            
            return json.dumps({
                "action": "look",
                "target": container_name,
                "confidence": 0.95,
                "tool_used": "LookTool",
                "system_response": description,
                "container_contents": target_container["items"]
            })
            
        except Exception as e:
            logger.error(f"Error looking in container: {e}")
            return json.dumps({
                "action": "look",
                "target": f"{target} in {container_name}" if target else container_name,
                "confidence": 0.5,
                "tool_used": "LookTool",
                "system_response": f"Unable to examine the container.",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class TakeTool(BaseTool):
    """Tool for taking items with inventory system integration."""
    name = "take"
    description = "Use this tool when the player wants to take, get, grab, or pick up an item from the environment. DO NOT use for 'take off' commands - use unequip tool instead. Input should be the item name."
    
    def _run(self, query: str) -> str:
        try:
            # Check if this is a "take off" command that should use UnequipTool instead
            query_lower = query.strip().lower()
            if query_lower.startswith("take off ") or "take off" in query_lower or query_lower.startswith("take the ") and " off" in query_lower:
                # Force redirecting to the unequip tool with a more explicit message
                item_name = query_lower.replace("take off", "").replace("take the", "").replace("off", "").strip()
                return json.dumps({
                    "action": "unequip",  # Changed from "redirect" to directly use "unequip"
                    "target": item_name,
                    "confidence": 0.95,   # Higher confidence to override other tools
                    "tool_used": "TakeTool",
                    "success": True,      # Mark as success to ensure it's used
                    "system_response": f"You remove the {item_name}.",
                    "redirect_to": "unequip"
                })
            
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Parse item name and quantity from query
                    parts = query.strip().split()
                    quantity = 1
                    item_name = query.strip()
                    
                    # Check for quantity at start (e.g., "3 health potions")
                    if parts and parts[0].isdigit():
                        quantity = int(parts[0])
                        item_name = ' '.join(parts[1:])
                    
                    # Process through inventory system
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "TAKE", 
                        {"item_name_or_id": item_name, "quantity": quantity}
                    )
                    
                    return json.dumps({
                        "action": "take",
                        "target": item_name,
                        "quantity": quantity,
                        "confidence": 0.95,
                        "tool_used": "TakeTool",
                        "success": result.get('success', False),
                        "system_response": result.get('message', ''),
                        "inventory_changes": result.get('data', {})
                    })
            
            # Fallback to integration processing
            result = _game_systems.process_through_integration(f"take {query.strip()}")
            
            return json.dumps({
                "action": "take",
                "target": query.strip(),
                "confidence": 0.9,
                "tool_used": "TakeTool",
                "system_response": result.get('response_text', f"You take the {query.strip()}."),
                "inventory_changes": result.get('metadata', {}).get('mechanical_changes', [])
            })
            
        except Exception as e:
            logger.error(f"TakeTool error: {e}")
            return json.dumps({
                "action": "take",
                "target": query.strip(),
                "confidence": 0.6,
                "tool_used": "TakeTool",
                "message": f"You attempt to take the {query.strip()}."
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class UseTool(BaseTool):
    """Tool for using objects with crafting and magic system integration."""
    name = "use"
    description = "Use this tool when the player wants to use, activate, or interact with an object. Input should be the object and any target."
    
    def _run(self, query: str) -> str:
        try:
            # Parse the use command
            parts = query.split(" on ")
            item = parts[0].strip()
            target = parts[1].strip() if len(parts) > 1 else None
            
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Process through inventory system
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "USE", 
                        {"item_name_or_id": item, "quantity": 1, "target": target}
                    )
                    
                    response_data = {
                        "action": "use",
                        "target": item,
                        "confidence": 0.95,
                        "tool_used": "UseTool",
                        "success": result.get('success', False),
                        "system_response": result.get('message', '')
                    }
                    
                    if target:
                        response_data["modifiers"] = {"on_target": target}
                    
                    if result.get('data'):
                        response_data["game_effects"] = result['data']
                    
                    return json.dumps(response_data)
            
            # Fallback to integration processing
            use_command = f"use {item}" + (f" on {target}" if target else "")
            result = _game_systems.process_through_integration(use_command)
            
            response_data = {
                "action": "use",
                "target": item,
                "confidence": 0.9,
                "tool_used": "UseTool",
                "system_response": result.get('response_text', '')
            }
            
            if target:
                response_data["modifiers"] = {"on_target": target}
            
            if result.get('metadata', {}).get('mechanical_changes'):
                response_data["game_effects"] = result['metadata']['mechanical_changes']
            
            return json.dumps(response_data)
            
        except Exception as e:
            logger.error(f"UseTool error: {e}")
            return json.dumps({
                "action": "use",
                "target": query.strip(),
                "confidence": 0.6,
                "tool_used": "UseTool",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class TalkTool(BaseTool):
    """Tool for communication with NPC system and AI GM integration."""
    name = "talk"
    description = "Use this tool when the player wants to talk to, speak with, or communicate with someone. Input should be who they want to talk to and optionally what about."
    
    def _run(self, query: str) -> str:
        try:
            # Parse talk command
            parts = query.split(" about ")
            target = parts[0].strip()
            topic = parts[1].strip() if len(parts) > 1 else None
            
            # Get NPC system for character interactions
            npc_system = _game_systems.get_npc_system()
            ai_gm = _game_systems.get_ai_gm()
            
            # Build talk command
            talk_command = f"talk to {target}" + (f" about {topic}" if topic else "")
            
            # Try AI GM for rich dialogue generation
            if ai_gm:
                try:
                    ai_response = ai_gm.process_player_input(talk_command)
                    
                    response_data = {
                        "action": "talk",
                        "target": target,
                        "confidence": 0.95,
                        "tool_used": "TalkTool",
                        "system_response": ai_response.get('response', ''),
                        "dialogue": ai_response.get('response', ''),
                        "narrative_context": ai_response.get('narrative_elements', [])
                    }
                    
                    if topic:
                        response_data["modifiers"] = {"about_topic": topic}
                    
                    return json.dumps(response_data)
                    
                except Exception as e:
                    logger.warning(f"AI GM unavailable for TalkTool: {e}")
            
            # Fallback to integration processing
            result = _game_systems.process_through_integration(talk_command)
            
            response_data = {
                "action": "talk",
                "target": target,
                "confidence": 0.8,
                "tool_used": "TalkTool",
                "system_response": result.get('response_text', f"You speak with {target}.")
            }
            
            if topic:
                response_data["modifiers"] = {"about_topic": topic}
            
            return json.dumps(response_data)
            
        except Exception as e:
            logger.error(f"TalkTool error: {e}")
            return json.dumps({
                "action": "talk",
                "target": query.strip(),
                "confidence": 0.6,
                "tool_used": "TalkTool",
                "system_response": f"Error communicating with {query.strip()}: {str(e)}",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class AttackTool(BaseTool):
    """Tool for combat actions with full combat system integration."""
    name = "attack"
    description = "Use this tool when the player wants to attack, fight, or engage in combat. Input should be the target and optionally the weapon."
    
    def _run(self, query: str) -> str:
        try:
            # Parse attack command
            parts = query.split(" with ")
            target = parts[0].strip()
            weapon = parts[1].strip() if len(parts) > 1 else None
            
            # Get combat system for battle mechanics
            combat_system = _game_systems.get_combat_system()
            
            if combat_system:
                try:
                    # Use real combat system
                    attack_data = {
                        "target": target,
                        "weapon": weapon,
                        "action_type": "attack"
                    }
                    
                    # Process combat action through the system
                    combat_result = combat_system.process_combat_action("attack", attack_data)
                    
                    response_data = {
                        "action": "attack",
                        "target": target,
                        "confidence": 0.95,
                        "tool_used": "AttackTool",
                        "combat_result": combat_result,
                        "damage_dealt": combat_result.get('damage', 0),
                        "hit_success": combat_result.get('hit', False)
                    }
                    
                    if weapon:
                        response_data["modifiers"] = {"with_item": weapon}
                    
                    return json.dumps(response_data)
                    
                except Exception as e:
                    logger.warning(f"Combat system error: {e}")
            
            # Fallback to integration processing
            attack_command = f"attack {target}" + (f" with {weapon}" if weapon else "")
            result = _game_systems.process_through_integration(attack_command)
            
            response_data = {
                "action": "attack", 
                "target": target,
                "confidence": 0.8,
                "tool_used": "AttackTool",
                "system_response": result.get('response_text', f"You attack {target}!")
            }
            
            if weapon:
                response_data["modifiers"] = {"with_item": weapon}
            
            return json.dumps(response_data)
            
        except Exception as e:
            logger.error(f"AttackTool error: {e}")
            return json.dumps({
                "action": "attack",
                "target": query.strip(),
                "confidence": 0.6,
                "tool_used": "AttackTool",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class CastSpellTool(BaseTool):
    """Tool for magic actions with magic system integration."""
    name = "cast_magic"
    description = "Use this tool when the player wants to cast a spell or use magic. Input should be the spell name and optionally the target."
    
    def _run(self, query: str) -> str:
        try:
            # Parse spell casting command
            parts = query.split(" on ")
            spell = parts[0].strip()
            target = parts[1].strip() if len(parts) > 1 else None
            
            # Get magic system for spell mechanics
            magic_system = _game_systems.get_magic_system()
            
            if magic_system:
                try:
                    # Use real magic system
                    spell_data = {
                        "spell_name": spell,
                        "target": target,
                        "caster": "player"
                    }
                    
                    # Process spell through magic system
                    magic_result = magic_system.cast_spell(spell_data)
                    
                    response_data = {
                        "action": "cast",
                        "target": spell,
                        "confidence": 0.95,
                        "tool_used": "CastSpellTool",
                        "magic_result": magic_result,
                        "spell_success": magic_result.get('success', False),
                        "magic_effects": magic_result.get('effects', [])
                    }
                    
                    if target:
                        response_data["spell_target"] = target
                    
                    return json.dumps(response_data)
                    
                except Exception as e:
                    logger.warning(f"Magic system error: {e}")
            
            # Fallback to integration processing  
            cast_command = f"cast {spell}" + (f" on {target}" if target else "")
            result = _game_systems.process_through_integration(cast_command)
            
            response_data = {
                "action": "cast",
                "target": spell,
                "confidence": 0.8,
                "tool_used": "CastSpellTool",
                "system_response": result.get('response_text', f"You cast {spell}!")
            }
            
            if target:
                response_data["spell_target"] = target
            
            return json.dumps(response_data)
            
        except Exception as e:
            logger.error(f"CastSpellTool error: {e}")
            return json.dumps({
                "action": "cast",
                "target": query.strip(),
                "confidence": 0.6,
                "tool_used": "CastSpellTool",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class InventoryTool(BaseTool):
    """Tool for inventory management with game state integration."""
    name = "inventory"
    description = "Use this tool when the player wants to check their inventory, items, or equipment."
    
    def _run(self, query: str) -> str:
        try:
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Process through inventory system
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "INVENTORY_VIEW", 
                        {}
                    )
                    
                    # Get equipment data
                    equipment_data = inventory_system.get_player_equipment_display("default_player")

                    return json.dumps({
                        "action": "inventory",
                        "target": None,
                        "confidence": 0.98,
                        "tool_used": "InventoryTool",
                        "success": result.get('success', False),
                        "system_response": result.get('message', 'You check your inventory.'),
                        "inventory_data": result.get('data', {}),
                        "equipment_data": equipment_data
                    })
            
            # Fallback to integration processing
            result = _game_systems.process_through_integration("inventory")
            
            return json.dumps({
                "action": "inventory",
                "target": None,
                "confidence": 0.95,
                "tool_used": "InventoryTool",
                "system_response": result.get('response_text', 'You check your inventory.'),
                "inventory_data": result.get('metadata', {}).get('player_state', {})
            })
            
        except Exception as e:
            logger.error(f"InventoryTool error: {e}")
            return json.dumps({
                "action": "inventory",
                "target": None,
                "confidence": 0.7,
                "tool_used": "InventoryTool",
                "system_response": "You check your inventory.",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class DropTool(BaseTool):
    """Tool for dropping items with inventory system integration."""
    name = "drop"
    description = "Use this tool when the player wants to drop, discard, or put down an item. Input should be the item name."
    
    def _run(self, query: str) -> str:
        try:
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Parse item name and quantity from query
                    parts = query.strip().split()
                    quantity = 1
                    item_name = query.strip()
                    
                    # Check for quantity at start (e.g., "3 health potions")
                    if parts and parts[0].isdigit():
                        quantity = int(parts[0])
                        item_name = ' '.join(parts[1:])
                    
                    # Process through inventory system
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "DROP", 
                        {"item_name_or_id": item_name, "quantity": quantity}
                    )
                    
                    return json.dumps({
                        "action": "drop",
                        "target": item_name,
                        "quantity": quantity,
                        "confidence": 0.95,
                        "tool_used": "DropTool",
                        "success": result.get('success', False),
                        "system_response": result.get('message', ''),
                        "inventory_changes": result.get('data', {})
                    })
            
            # Fallback to integration processing
            result = _game_systems.process_through_integration(f"drop {query.strip()}")
            
            return json.dumps({
                "action": "drop",
                "target": query.strip(),
                "confidence": 0.9,
                "tool_used": "DropTool",
                "system_response": result.get('response_text', f"You drop the {query.strip()}."),
                "inventory_changes": result.get('metadata', {}).get('mechanical_changes', [])
            })
            
        except Exception as e:
            logger.error(f"DropTool error: {e}")
            return json.dumps({
                "action": "drop",
                "target": query.strip(),
                "confidence": 0.6,
                "tool_used": "DropTool",
                "message": f"You attempt to drop the {query.strip()}.",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class SearchTool(BaseTool):
    """Tool for active searching actions with hidden container discovery and natural language processing."""
    name = "search"
    description = "Use this tool when the player wants to search, look for hidden items, find secret compartments, or explore thoroughly. Input should be what they want to search for or where they want to search."
    
    def _run(self, query: str) -> str:
        try:
            # Parse natural language query for search context
            parsed_query = self._parse_search_query(query)
            
            # Try inventory system integration first for spatial awareness
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Get player's current location
                    player_location = inventory_system.get_player_location("default_player")
                    
                    if player_location:
                        # If searching a specific container or area
                        if parsed_query["target"] or parsed_query["search_area"]:
                            return self._search_specific_target(inventory_system, player_location, parsed_query)
                        
                        # If general area search
                        else:
                            return self._search_area_thoroughly(inventory_system, player_location, parsed_query)
            
            # Fallback to AI GM for rich search descriptions
            ai_gm = _game_systems.get_ai_gm()
            if ai_gm:
                try:
                    search_prompt = f"search for {query.strip()}" if query.strip() else "search the area thoroughly"
                    ai_response = ai_gm.process_player_input(search_prompt)
                    
                    return json.dumps({
                        "action": "search",
                        "target": query.strip() if query.strip() else None,
                        "confidence": 0.95,
                        "tool_used": "SearchTool",
                        "system_response": ai_response.get('response', ''),
                        "ai_description": ai_response.get('response', ''),
                        "search_results": ai_response.get('search_results', []),
                        "narrative_elements": ai_response.get('narrative_elements', [])
                    })
                except Exception as e:
                    logger.warning(f"AI GM unavailable for SearchTool: {e}")
            
            # Final fallback processing
            result = _game_systems.process_through_integration(f"search {query.strip()}" if query.strip() else "search")
            
            return json.dumps({
                "action": "search", 
                "target": query.strip() if query.strip() else None,
                "confidence": 0.8,
                "tool_used": "SearchTool",
                "system_response": result.get('response_text', f"You search {query.strip() if query.strip() else 'the area carefully'}.")
            })
            
        except Exception as e:
            logger.error(f"SearchTool error: {e}")
            return json.dumps({
                "action": "search",
                "target": query.strip() if query.strip() else None,
                "confidence": 0.5,
                "tool_used": "SearchTool",
                "system_response": f"Unable to search {query.strip() if query.strip() else 'the area'}: {str(e)}",
                "error": str(e)
            })
    
    def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language search query with advanced NLP processing."""
        query_lower = query.lower().strip()
        
        # Advanced search keywords and contexts
        hidden_keywords = ["hidden", "secret", "concealed", "invisible", "disguised"]
        location_keywords = ["under", "behind", "beneath", "inside", "within", "on", "around", "near"]
        item_keywords = ["for", "item", "treasure", "weapon", "key", "clue", "evidence"]
        thorough_keywords = ["thoroughly", "carefully", "meticulously", "completely", "everywhere"]
        
        parsed = {
            "target": None,
            "search_area": None,
            "search_type": "general",
            "search_intensity": "normal",
            "hidden_focus": False,
            "prepositions": [],
            "modifiers": []
        }
        
        if not query_lower:
            parsed["search_type"] = "area"
            parsed["search_intensity"] = "thorough"
            return parsed
        
        # Use spaCy for sophisticated NLP parsing if available
        try:
            doc = _game_systems.get_nlp_processor().process(query_lower) if hasattr(_game_systems, 'get_nlp_processor') else None
            if doc:
                # Extract entities, relationships, and spatial context
                for token in doc:
                    # Extract prepositional objects (search locations)
                    if token.dep_ == "pobj" and token.head.text in location_keywords:
                        parsed["search_area"] = token.text
                        parsed["prepositions"].append(token.head.text)
                    
                    # Extract direct objects (search targets)
                    elif token.dep_ in ["dobj", "obj"] and token.head.lemma_ in ["search", "find", "look"]:
                        parsed["target"] = token.text
                    
                    # Extract modifiers (adjectives and adverbs)
                    elif token.dep_ in ["amod", "advmod"]:
                        parsed["modifiers"].append(token.text)
                        if token.text in hidden_keywords:
                            parsed["hidden_focus"] = True
                        elif token.text in thorough_keywords:
                            parsed["search_intensity"] = "thorough"
                
                # Extract named entities for specific items/locations
                for ent in doc.ents:
                    if ent.label_ in ["FANTASY_ITEM", "ITEM"]:
                        parsed["target"] = ent.text
                    elif ent.label_ in ["FANTASY_LOCATION", "LOCATION"]:
                        parsed["search_area"] = ent.text
        except:
            # Fallback to simple parsing if spaCy fails
            pass
        
        # Enhanced pattern matching for natural language sentences
        if any(keyword in query_lower for keyword in hidden_keywords):
            parsed["hidden_focus"] = True
            parsed["search_type"] = "hidden"
        
        if any(keyword in query_lower for keyword in thorough_keywords):
            parsed["search_intensity"] = "thorough"
        
        if any(keyword in query_lower for keyword in location_keywords):
            # Handle patterns like "search for gold under the table" or "search behind chest"
            parts = query_lower.split()
            for i, word in enumerate(parts):
                if word in location_keywords and i + 1 < len(parts):
                    # Extract search area (handle "the" articles)
                    area_part = " ".join(parts[i+1:])
                    if area_part.startswith("the "):
                        area_part = area_part[4:]
                    parsed["search_area"] = area_part
                    
                    # Extract target from before the preposition
                    if i > 0:
                        target_part = " ".join(parts[:i])
                        # Remove common action words and articles
                        target_part = target_part.replace("search for", "").replace("search", "").replace("find", "").replace("the ", "").strip()
                        if target_part:
                            parsed["target"] = target_part
                    break
        else:
            # Clean target by removing action words
            target = query_lower.replace("search for", "").replace("search", "").replace("find", "").replace("the ", "").strip()
            parsed["target"] = target if target else query_lower
            parsed["search_type"] = "item" if any(kw in query_lower for kw in item_keywords) else "general"
        
        return parsed
    
    def _get_search_hints_for_container_type(self, container_type: str, location_container_system) -> str:
        """Get search hints based on container type behaviors."""
        behaviors = location_container_system.get_container_type_behaviors(container_type)
        
        hints = []
        if "special_search" in behaviors:
            hints.append(behaviors["special_search"])
        
        if "special_requirements" in behaviors:
            hints.append(f"Note: {behaviors['special_requirements']}")
        
        if "item_type_restriction" in behaviors:
            item_types = behaviors["item_type_restriction"]
            hints.append(f"This container typically holds: {', '.join(item_types).lower()}")
        
        return " ".join(hints) if hints else ""

    def _search_area_thoroughly(self, inventory_system, location_id: str, parsed_query: Dict[str, Any]) -> str:
        """Perform thorough area search with hidden container discovery."""
        try:
            location_container_system = inventory_system.location_container_system
            if not location_container_system:
                return json.dumps({
                    "action": "search",
                    "target": "area",
                    "confidence": 0.6,
                    "tool_used": "SearchTool",
                    "system_response": "You search the area thoroughly but find nothing of particular interest."
                })
            
            # Use search_location method for thorough exploration
            search_results = location_container_system.search_location(
                location_id, 
                search_hidden=True,
                thorough=parsed_query["search_intensity"] == "thorough"
            )
            
            # Build detailed search response
            description_parts = ["You search the area thoroughly."]
            discoveries = []
            hidden_found = []
            
            # Process ground items found
            if search_results.get("ground_items"):
                items_list = []
                for item_id, item_info in search_results["ground_items"].items():
                    quantity_text = f"{item_info['quantity']}x " if item_info['quantity'] > 1 else ""
                    items_list.append(f"{quantity_text}{item_info['name']}")
                
                if items_list:
                    description_parts.append(f"You find: {', '.join(items_list)}.")
                    discoveries.extend(items_list)
            
            # Process containers discovered
            if search_results.get("containers"):
                visible_containers = []
                hidden_containers = []
                
                for container_id, container_info in search_results["containers"].items():
                    container_desc = container_info["name"]
                    if container_info["items"]:
                        item_count = len(container_info["items"])
                        container_desc += f" (contains {item_count} item{'s' if item_count != 1 else ''})"
                    
                    if container_info.get("was_hidden", False):
                        hidden_containers.append(container_desc)
                        hidden_found.append(container_info["name"])
                    else:
                        visible_containers.append(container_desc)
                
                if hidden_containers:
                    description_parts.append(f"Your thorough search reveals: {', '.join(hidden_containers)}.")
                    discoveries.extend(hidden_containers)
                
                if visible_containers:
                    description_parts.append(f"You also notice: {', '.join(visible_containers)}.")
            # Process special discoveries (hidden passages, secret compartments, etc.)
            if search_results.get("special_discoveries"):
                special_items = search_results["special_discoveries"]
                description_parts.append(f"Your careful search uncovers: {', '.join(special_items)}.")
                discoveries.extend(special_items)
                hidden_found.extend(special_items)
            
            if not discoveries:
                description_parts.append("Despite your thorough search, you don't find anything new.")
            
            full_description = " ".join(description_parts)
            
            return json.dumps({
                "action": "search",
                "target": "area",
                "confidence": 0.95,
                "tool_used": "SearchTool",
                "system_response": full_description,
                "search_results": search_results,
                "discoveries": discoveries,
                "hidden_found": hidden_found,
                "search_context": {
                    "location_id": location_id,
                    "search_intensity": parsed_query["search_intensity"],
                    "hidden_focus": parsed_query["hidden_focus"],
                    "items_discovered": len(discoveries)
                }
            })
            
        except Exception as e:
            logger.error(f"Error searching area thoroughly: {e}")
            return json.dumps({
                "action": "search",
                "target": "area",
                "confidence": 0.5,
                "tool_used": "SearchTool",
                "system_response": "You search the area but encounter some difficulties.",
                "error": str(e)
            })
    
    def _search_specific_target(self, inventory_system, location_id: str, parsed_query: Dict[str, Any]) -> str:
        """Search for specific target or in specific area."""
        try:
            target = parsed_query.get("target")
            search_area = parsed_query.get("search_area")
            
            location_container_system = inventory_system.location_container_system
            if not location_container_system:
                search_target = target or search_area or "the specified area"
                return json.dumps({
                    "action": "search",
                    "target": search_target,
                    "confidence": 0.6,
                    "tool_used": "SearchTool",
                    "system_response": f"You search {search_target} but find nothing specific."
                })
            
            # Get current location data
            location_data = location_container_system.get_items_at_location(location_id)
            
            # If searching for specific item
            if target:
                return self._search_for_item(location_container_system, location_id, target, parsed_query)
            
            # If searching specific area/container
            elif search_area:
                return self._search_in_area(location_container_system, location_id, search_area, parsed_query)
            
            # Fallback to general search
            else:
                return self._search_area_thoroughly(inventory_system, location_id, parsed_query)
            
        except Exception as e:
            logger.error(f"Error searching specific target: {e}")
            return json.dumps({
                "action": "search",
                "target": parsed_query.get("target") or parsed_query.get("search_area") or "target",
                "confidence": 0.5,
                "tool_used": "SearchTool",
                "system_response": f"Unable to search the specified target.",
                "error": str(e)
            })
    
    def _search_for_item(self, location_container_system, location_id: str, item_name: str, parsed_query: Dict[str, Any]) -> str:
        """Search for a specific item with hidden discovery capabilities."""
        try:
            # Perform targeted search
            search_results = location_container_system.search_location(
                location_id,
                target_item=item_name,
                search_hidden=parsed_query["hidden_focus"] or parsed_query["search_intensity"] == "thorough"
            )
            
            # Check if item was found
            item_found = False
            found_location = None
            item_details = None
            
            # Check ground items
            for item_id, item_info in search_results.get("ground_items", {}).items():
                if (item_name.lower() in item_info["name"].lower() or 
                    item_name.lower() in item_id.lower()):
                    item_found = True
                    found_location = "ground"
                    item_details = item_info
                    break
            
            # Check containers
            if not item_found:
                for container_id, container_info in search_results.get("containers", {}).items():
                    for item_id, item_info in container_info.get("items", {}).items():
                        if (item_name.lower() in item_info["name"].lower() or 
                            item_name.lower() in item_id.lower()):
                            item_found = True
                            found_location = container_info["name"]
                            item_details = item_info
                            break
                    if item_found:
                        break
            
            if item_found:
                quantity_text = f"({item_details['quantity']} available) " if item_details['quantity'] > 1 else ""
                if found_location == "ground":
                    description = f"After searching carefully, you find {item_details['name']} on the ground. {quantity_text}{item_details.get('description', 'A notable item.')}"
                else:
                    description = f"Your search reveals {item_details['name']} in {found_location}. {quantity_text}{item_details.get('description', 'A notable item.')}"
                
                return json.dumps({
                    "action": "search",
                    "target": item_name,
                    "confidence": 0.95,
                    "tool_used": "SearchTool",
                    "system_response": description,
                    "item_found": {
                        "name": item_details["name"],
                        "quantity": item_details["quantity"],
                        "location": found_location,
                        "description": item_details.get("description", "")
                    },
                    "search_successful": True
                })
            else:
                return json.dumps({
                    "action": "search",
                    "target": item_name,
                    "confidence": 0.9,
                    "tool_used": "SearchTool",
                    "system_response": f"Despite your {'thorough' if parsed_query['search_intensity'] == 'thorough' else 'careful'} search, you don't find any '{item_name}' here.",
                    "search_successful": False
                })
            
        except Exception as e:
            logger.error(f"Error searching for item: {e}")
            return json.dumps({
                "action": "search",
                "target": item_name,
                "confidence": 0.5,
                "tool_used": "SearchTool",
                "system_response": f"Unable to search for '{item_name}'.",
                "error": str(e)
            })
    
    def _search_in_area(self, location_container_system, location_id: str, area_name: str, parsed_query: Dict[str, Any]) -> str:
        """Search in a specific area or container."""
        try:
            location_data = location_container_system.get_items_at_location(location_id)
            
            # Find matching container or area
            target_container = None
            target_container_id = None
            
            for container_id, container_info in location_data.get("containers", {}).items():
                if (area_name.lower() in container_info["name"].lower() or
                    area_name.lower() in container_info["type"].lower() or
                    area_name.lower() in container_id.lower()):
                    target_container = container_info
                    target_container_id = container_id
                    break
            
            # Search the specific container
            if target_container.get("is_locked", False):
                lock_info = ""
                if target_container.get("key_required"):
                    lock_info = f" It requires a specific key to unlock."
                else:
                    lock_info = f" You might be able to pick the lock with the right tools."
                
                return json.dumps({
                    "action": "search",
                    "target": f"in {area_name}",
                    "confidence": 0.9,
                    "tool_used": "SearchTool",
                    "system_response": f"The {target_container['name']} is locked and cannot be searched.{lock_info}",
                    "lock_status": {
                        "is_locked": True,
                        "key_required": target_container.get("key_required"),
                        "can_lockpick": not target_container.get("key_required")
                    }
                })
                
                # Look for hidden compartments or additional items
                search_results = location_container_system.search_location(
                    location_id,
                    target_container=target_container_id,
                    search_hidden=True
                )
                
                items_found = []
                hidden_discoveries = []
                
                # Check for items in the container
                if target_container.get("items"):
                    for item_id, item_info in target_container["items"].items():
                        quantity_text = f"{item_info['quantity']}x " if item_info['quantity'] > 1 else ""
                        items_found.append(f"{quantity_text}{item_info['name']}")
                
                # Check for hidden discoveries
                if search_results.get("special_discoveries"):
                    hidden_discoveries.extend(search_results["special_discoveries"])
                
                description_parts = [f"You search {target_container['name']} thoroughly."]
                
                if items_found:
                    description_parts.append(f"Inside you find: {', '.join(items_found)}.")
                
                if hidden_discoveries:
                    description_parts.append(f"Your careful search also reveals: {', '.join(hidden_discoveries)}.")
                
                if not items_found and not hidden_discoveries:
                    description_parts.append("It appears to be empty.")
                
                return json.dumps({
                    "action": "search",
                    "target": f"in {area_name}",
                    "confidence": 0.95,
                    "tool_used": "SearchTool",
                    "system_response": " ".join(description_parts),
                    "container_searched": {
                        "name": target_container["name"],
                        "items_found": items_found,
                        "hidden_discoveries": hidden_discoveries
                    }
                })
            
            else:
                # Area not found as container, perform general area search
                return json.dumps({
                    "action": "search",
                    "target": f"in {area_name}",
                    "confidence": 0.8,
                    "tool_used": "SearchTool",
                    "system_response": f"You search around the {area_name} area but don't find anything specific."
                })
            
        except Exception as e:
            logger.error(f"Error searching in area: {e}")
            return json.dumps({
                "action": "search",
                "target": f"in {area_name}",
                "confidence": 0.5,
                "tool_used": "SearchTool",
                "system_response": f"Unable to search in the specified area.",
                "error": str(e)
            })
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class UnlockTool(BaseTool):
    """Tool for unlocking containers and doors with keys or lockpicks."""
    name = "unlock"
    description = "Use this tool when the player wants to unlock, open with a key, or pick a lock on a container or door. Input should describe what they want to unlock and optionally how (key or lockpick)."
    
    def _run(self, query: str) -> str:
        try:
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Parse unlock query for target and method
                    parsed_query = self._parse_unlock_query(query)
                    target = parsed_query.get("target")
                    method = parsed_query.get("method", "auto")
                    
                    if not target:
                        return json.dumps({
                            "action": "unlock",
                            "confidence": 0.5,
                            "tool_used": "UnlockTool",
                            "system_response": "What would you like to unlock?",
                            "error": "No target specified"
                        })
                    
                    # Get player location and look for the container
                    player_location = getattr(inventory_system, 'current_location', 'default_location')
                    location_container_system = inventory_system.location_container_system
                    
                    if location_container_system:
                        # Find matching container
                        containers = location_container_system.get_containers_in_location(player_location)
                        target_container_id = None
                        target_container_data = None
                        
                        for container_id, container_data in containers.items():
                            if (target.lower() in container_data.name.lower() or
                                target.lower() in container_data.container_type.lower() or
                                target.lower() in container_id.lower()):
                                target_container_id = container_id
                                target_container_data = container_data
                                break
                        
                        if not target_container_id:
                            return json.dumps({
                                "action": "unlock",
                                "target": target,
                                "confidence": 0.8,
                                "tool_used": "UnlockTool",
                                "system_response": f"You don't see any '{target}' that can be unlocked here."
                            })
                        
                        # Check if already unlocked
                        if not target_container_data.is_locked:
                            return json.dumps({
                                "action": "unlock",
                                "target": target,
                                "confidence": 0.95,
                                "tool_used": "UnlockTool",
                                "system_response": f"The {target_container_data.name} is already unlocked."
                            })
                        
                        # Get player inventory for unlock attempt
                        player_inventory = inventory_system.get_player_inventory("default_player")
                        
                        # Check if unlock is possible
                        unlock_check = location_container_system.can_unlock_container(target_container_id, player_inventory)
                        
                        if not unlock_check["can_unlock"]:
                            required_items = unlock_check.get("required_items", [])
                            required_skills = unlock_check.get("required_skills", [])
                            
                            missing_items = []
                            for item in required_items:
                                item_data = location_container_system.item_registry.get_item_data(item)
                                item_name = item_data.name if item_data else item
                                missing_items.append(item_name)
                            
                            message_parts = [f"You cannot unlock the {target_container_data.name}."]
                            if missing_items:
                                message_parts.append(f"You need: {', '.join(missing_items)}.")
                            if required_skills:
                                message_parts.append(f"Required skills: {', '.join(required_skills)}.")
                            
                            return json.dumps({
                                "action": "unlock",
                                "target": target,
                                "confidence": 0.9,
                                "tool_used": "UnlockTool",
                                "system_response": " ".join(message_parts),
                                "required_items": required_items,
                                "required_skills": required_skills
                            })
                        
                        # Attempt to unlock
                        unlock_result = location_container_system.unlock_container(target_container_id, player_inventory, method)
                        
                        if unlock_result["success"]:
                            return json.dumps({
                                "action": "unlock",
                                "target": target,
                                "confidence": 0.95,
                                "tool_used": "UnlockTool",
                                "system_response": unlock_result["message"],
                                "unlock_successful": True,
                                "method_used": unlock_result.get("method", method),
                                "container_unlocked": {
                                    "id": target_container_id,
                                    "name": target_container_data.name,
                                    "type": target_container_data.container_type
                                }
                            })
                        else:
                            return json.dumps({
                                "action": "unlock",
                                "target": target,
                                "confidence": 0.9,
                                "tool_used": "UnlockTool",
                                "system_response": unlock_result["message"],
                                "unlock_successful": False
                            })
                    
                    # Fallback if no location container system
                    else:
                        return json.dumps({
                            "action": "unlock",
                            "target": target,
                            "confidence": 0.6,
                            "tool_used": "UnlockTool",
                            "system_response": f"You attempt to unlock the {target}, but the mechanism is unclear."
                        })
            
            # Try AI GM for rich descriptions if available
            ai_gm = _game_systems.get_ai_gm()
            if ai_gm:
                try:
                    unlock_prompt = f"unlock {query.strip()}" if query.strip() else "unlock"
                    ai_response = ai_gm.process_player_input(unlock_prompt)
                    
                    return json.dumps({
                        "action": "unlock",
                        "target": query.strip() if query.strip() else None,
                        "confidence": 0.95,
                        "tool_used": "UnlockTool",
                        "system_response": ai_response.get('response', ''),
                        "ai_description": ai_response.get('response', ''),
                        "narrative_elements": ai_response.get('narrative_elements', [])
                    })
                except Exception as e:
                    logger.warning(f"AI GM unavailable for UnlockTool: {e}")
            
            # Final fallback processing
            result = _game_systems.process_through_integration(f"unlock {query.strip()}" if query.strip() else "unlock")
            
            return json.dumps({
                "action": "unlock", 
                "target": query.strip() if query.strip() else None,
                "confidence": 0.8,
                "tool_used": "UnlockTool",
                "system_response": result.get('response_text', f"You attempt to unlock {query.strip() if query.strip() else 'something'}.")
            })
            
        except Exception as e:
            logger.error(f"UnlockTool error: {e}")
            return json.dumps({
                "action": "unlock",
                "target": query.strip() if query.strip() else None,
                "confidence": 0.5,
                "tool_used": "UnlockTool",
                "system_response": f"Unable to unlock {query.strip() if query.strip() else 'the target'}: {str(e)}",
                "error": str(e)
            })
    
    def _parse_unlock_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language unlock query."""
        query_lower = query.lower().strip()
        
        # Method detection keywords
        key_keywords = ["key", "with key", "using key", "use key"]
        lockpick_keywords = ["lockpick", "pick", "pick lock", "using lockpick", "with lockpick"]
        
        parsed = {
            "target": None,
            "method": "auto"
        }
        
        # Detect method
        if any(keyword in query_lower for keyword in key_keywords):
            parsed["method"] = "key"
        elif any(keyword in query_lower for keyword in lockpick_keywords):
            parsed["method"] = "lockpick"
        
        # Extract target (remove method keywords)
        target_text = query_lower
        
        # Remove common prefixes
        prefixes = ["unlock", "open", "pick", "the", "a", "an"]
        words = target_text.split()
        filtered_words = []
        
        skip_next = False
        for i, word in enumerate(words):
            if skip_next:
                skip_next = False
                continue
                
            if word in prefixes and i == 0:
                continue
            elif word == "with" and i < len(words) - 1:
                # Skip "with key", "with lockpick" etc.
                next_word = words[i + 1]
                if next_word in ["key", "lockpick", "picks"]:
                    skip_next = True
                    continue
            elif word == "using" and i < len(words) - 1:
                # Skip "using key", "using lockpick" etc.
                next_word = words[i + 1]
                if next_word in ["key", "lockpick", "picks"]:
                    skip_next = True
                    continue
            elif word in ["key", "lockpick", "picks", "lock"]:
                # Skip standalone method words
                continue
            
            filtered_words.append(word)
        
        if filtered_words:
            parsed["target"] = " ".join(filtered_words)
        else:
            # Fallback - try to extract a noun from the original query
            words = query.split()
            for word in words:
                if word.lower() not in ["unlock", "open", "pick", "the", "with", "using", "key", "lockpick"]:
                    parsed["target"] = word
                    break
        
        return parsed
    
    async def _arun(self, query: str) -> str:
        return self._run(query)

class EquipTool(BaseTool):
    """Tool for equipping items with equipment system integration."""
    name = "equip"
    description = "Use this tool when the player wants to equip, wear, or wield an item. Input should be the item name and optionally the preferred slot."

    def _run(self, query: str) -> str:
        try:
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Clean up the query to extract the item name
                    query_lower = query.strip().lower()
                    item_name = query.strip()
                    preferred_slot = None
                    
                    # Remove common equipment verbs from the start
                    equipment_verbs = ["equip", "wear", "put on", "wield", "don", "equip the", "wear the", "put on the"]
                    for verb in equipment_verbs:
                        if query_lower.startswith(verb + " "):
                            item_name = query[len(verb):].strip()
                            query_lower = item_name.lower()
                            break
                    
                    # Check for slot specification (e.g., "sword in main_hand")
                    if " in " in query_lower:
                        item_part, slot_part = query_lower.split(" in ", 1)
                        item_name = item_part.strip()
                        preferred_slot = slot_part.strip().replace(" ", "_")
                    elif " on " in query_lower:
                        item_part, slot_part = query_lower.split(" on ", 1)
                        item_name = item_part.strip()
                        # Convert common phrases to slot names
                        slot_mapping = {
                            "head": "head",
                            "chest": "chest", 
                            "legs": "legs",
                            "feet": "feet",
                            "hands": "hands",
                            "left hand": "main_hand",
                            "right hand": "off_hand",
                            "main hand": "main_hand",
                            "off hand": "off_hand",
                            "finger": "ring_left",
                            "neck": "neck"
                        }
                        preferred_slot = slot_mapping.get(slot_part.strip(), slot_part.strip())
                    
                    # Process through inventory system
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "EQUIP", 
                        {
                            "item_name": item_name,
                            "slot": preferred_slot
                        }
                    )
                    
                    return json.dumps({
                        "action": "equip",
                        "target": item_name,
                        "slot": preferred_slot,
                        "confidence": 0.95,
                        "tool_used": "EquipTool",
                        "success": result.get('success', False),
                        "system_response": result.get('message', f'You try to equip {item_name}.'),
                        "equipment_data": result.get('data', {})
                    })
            
            # Fallback
            return json.dumps({
                "action": "equip",
                "target": query,
                "confidence": 0.7,
                "tool_used": "EquipTool",
                "success": False,
                "system_response": f"Equipment system not available. You try to equip {query}.",
                "equipment_data": {}
            })
            
        except Exception as e:
            return json.dumps({
                "action": "equip", 
                "target": query,
                "confidence": 0.5,
                "tool_used": "EquipTool",
                "success": False,
                "system_response": f"Error equipping {query}: {str(e)}",
                "error": str(e)
            })

    async def _arun(self, query: str) -> str:
        return self._run(query)


class UnequipTool(BaseTool):
    """Tool for unequipping items with equipment system integration."""
    name = "unequip"
    description = "Use this tool when the player wants to unequip, remove, take off, or doff an equipped item. This tool handles 'take off' commands for equipment. Input should be the item name or equipment slot."

    def _run(self, query: str) -> str:
        try:
            # Try to use the inventory system directly if available
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Clean up the query to extract the item name
                    query_lower = query.strip().lower()
                    item_name = None
                    slot_name = None
                    cleaned_query = query.strip()
                    
                    # Remove common unequip verbs from the start
                    unequip_verbs = ["unequip", "remove", "take off", "doff", "unequip the", "remove the", "take off the", "take the"]
                    for verb in unequip_verbs:
                        if query_lower.startswith(verb + " "):
                            cleaned_query = query[len(verb):].strip()
                            query_lower = cleaned_query.lower()
                            break
                    
                    # Special case for "take X off" pattern
                    if "off" in query_lower and query_lower.startswith("take "):
                        parts = query_lower.split("off", 1)
                        if len(parts) > 0:
                            cleaned_query = parts[0].replace("take", "").strip()
                            query_lower = cleaned_query.lower()
                    
                    # Check if it's a slot name
                    slot_keywords = {
                        "head": "head", "helmet": "head", "hat": "head",
                        "chest": "chest", "armor": "chest", "body": "chest",
                        "legs": "legs", "pants": "legs", "greaves": "legs", 
                        "feet": "feet", "boots": "feet", "shoes": "feet",
                        "hands": "hands", "gloves": "hands", "gauntlets": "hands",
                        "main hand": "main_hand", "main_hand": "main_hand", "weapon": "main_hand",
                        "off hand": "off_hand", "off_hand": "off_hand", "shield": "off_hand",
                        "ring": "ring_left", "left ring": "ring_left",
                        "right ring": "ring_right",
                        "neck": "neck", "necklace": "neck",
                        "belt": "belt",
                        "cloak": "back", "cape": "back"
                    }
                    
                    # Check for slot-based removal
                    for keyword, slot in slot_keywords.items():
                        if keyword == query_lower or keyword in query_lower:
                            slot_name = slot
                            logger.debug(f"Detected slot {slot_name} from keyword '{keyword}' in '{query_lower}'")
                            break
                    
                    # If no slot detected, treat as item name
                    if not slot_name:
                        item_name = cleaned_query
                        logger.debug(f"Using item name: '{item_name}' from '{cleaned_query}'")
                    
                    # Process through inventory system
                    logger.info(f"Unequipping with item_name='{item_name}', slot='{slot_name}'")
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "UNEQUIP", 
                        {
                            "item_name": item_name,
                            "slot": slot_name
                        }
                    )
                    
                    return json.dumps({
                        "action": "unequip",
                        "target": item_name or slot_name,
                        "confidence": 0.95,
                        "tool_used": "UnequipTool", 
                        "success": result.get('success', False),
                        "system_response": result.get('message', f'You try to unequip {query}.'),
                        "equipment_data": result.get('data', {})
                    })
            
            # Fallback
            return json.dumps({
                "action": "unequip",
                "target": query,
                "confidence": 0.7,
                "tool_used": "UnequipTool",
                "success": False,
                "system_response": f"Equipment system not available. You try to unequip {query}.",
                "equipment_data": {}
            })
            
        except Exception as e:
            return json.dumps({
                "action": "unequip",
                "target": query,
                "confidence": 0.5,
                "tool_used": "UnequipTool", 
                "success": False,
                "system_response": f"Error unequipping {query}: {str(e)}",
                "error": str(e)
            })

    async def _arun(self, query: str) -> str:
        return self._run(query)

@dataclass
class ParsedCommand:
    """Structured representation of a player's text command."""
    action: str                 # Primary verb/action (e.g., "go", "look", "take")
    target: Optional[str] = None  # Primary object of the action
    modifiers: Dict[str, Any] = None  # Additional qualifiers (direction, manner, etc.)
    context: Dict[str, Any] = None  # Additional context for command execution
    confidence: float = 1.0     # Confidence level of the parse (0.0-1.0)
    raw_text: str = ""          # Original raw text input
    
    def __post_init__(self):
        """Initialize default values for empty fields."""
        if self.modifiers is None:
            self.modifiers = {}
        if self.context is None:
            self.context = {}
    
    @property
    def targets(self) -> List[str]:
        """Backwards compatibility property: returns target as a list."""
        return [self.target] if self.target else []


class FantasyLLM(LLM):
    """
    Enhanced mock LLM for fantasy text parsing with improved tool selection
    and more realistic responses for Phase 3 testing.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize enhanced attributes using object.__setattr__ to bypass Pydantic restrictions
        object.__setattr__(self, 'tool_usage_patterns', self._init_tool_patterns())
        object.__setattr__(self, 'entity_database', self._init_entity_database())
        object.__setattr__(self, 'response_templates', self._init_response_templates())
    
    def _init_tool_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for tool selection."""
        return {
            "MoveTool": [
                r'\b(go|move|walk|travel|head|navigate|proceed)\b.*\b(to|towards|north|south|east|west|up|down)\b',
                r'\b(enter|exit|leave)\b',
                r'\bdirection\b.*\b(forest|castle|room|area)\b'
            ],
            "LookTool": [
                r'\b(look|examine|inspect|observe|check|view|see|study)\b',
                r'\b(what|describe|appearance|details)\b',
                r'\b(around|at|upon|carefully)\b'
            ],
            "TakeTool": [
                r'\b(take|grab|pick|get|collect|obtain)\b.*\b(up|item|object)\b',
                r'\b(sword|shield|potion|scroll|key|gem|treasure|weapon|armor)\b'
            ],
            "TalkTool": [
                r'\b(talk|speak|say|ask|tell|communicate|discuss|chat)\b',
                r'\b(to|with|about)\b.*\b(wizard|merchant|guard|npc|character)\b',
                r'\b(conversation|dialogue|question)\b'
            ],
            "AttackTool": [
                r'\b(attack|fight|strike|hit|battle|combat|assault)\b',
                r'\b(dragon|goblin|orc|monster|enemy|foe)\b.*\b(weapon|sword|magic)\b',
                r'\b(defend|counter|retaliate)\b'
            ],
            "MagicTool": [
                r'\b(cast|magic|spell|enchant|summon|ritual|brew)\b',
                r'\b(fireball|heal|lightning|frost|arcane)\b',
                r'\b(mana|magical|mystical|enchanted)\b'
            ],
            "SearchTool": [
                r'\b(search|look for|find|explore|investigate|check)\b.*\b(hidden|secret|compartments?|areas?)\b',
                r'\b(around|everywhere|thoroughly|carefully)\b',
                r'\b(for|item|treasure|weapon|key|clue|evidence)\b'
            ],
            "UnlockTool": [
                r'\b(unlock|open|pick)\b.*\b(lock|door|chest|container|box)\b',
                r'\b(with|using)\b.*\b(key|lockpick|tool)\b',
                r'\b(locked|secure|sealed|closed)\b'
            ]
        }
    
    def _init_entity_database(self) -> Dict[str, List[str]]:
        """Initialize enhanced entity recognition database."""
        return {
            "ITEM": [
                "sword", "shield", "potion", "scroll", "key", "gem", "treasure", 
                "armor", "helmet", "boots", "gloves", "ring", "amulet", "staff",
                "bow", "arrow", "torch", "rope", "bag", "coin", "crystal"
            ],
            "LOCATION": [
                "forest", "castle", "dungeon", "cave", "tower", "village", "temple",
                "room", "chamber", "hall", "courtyard", "garden", "bridge", "door",
                "gate", "altar", "throne", "library", "armory", "tavern"
            ],
            "CREATURE": [
                "dragon", "goblin", "orc", "wizard", "knight", "thief", "merchant",
                "guard", "priest", "mage", "warrior", "archer", "rogue", "bard",
                "elf", "dwarf", "troll", "skeleton", "zombie", "ghost"
            ],
            "ACTION": [
                "attack", "defend", "cast", "move", "look", "take", "talk", "use",
                "open", "close", "push", "pull", "climb", "jump", "run", "walk",
                "sneak", "hide", "search", "listen", "smell", "taste"
            ],
            "DIRECTION": [
                "north", "south", "east", "west", "up", "down", "left", "right",
                "forward", "backward", "inside", "outside", "above", "below"
            ]
        }
    
    def _init_response_templates(self) -> Dict[str, List[str]]:
        """Initialize response templates for different scenarios."""
        return {
            "tool_selection": [
                "Based on the user's intent to {action}, I should use {tool}.",
                "The command indicates {action}, so {tool} is most appropriate.",
                "For {action} actions, {tool} provides the best functionality."
            ],
            "entity_extraction": [
                "I identify the following entities: {entities}",
                "Entities detected: {entities}",
                "The text contains these game elements: {entities}"
            ],
            "action_classification": [
                "Primary action: {action}",
                "Classified as: {action}",
                "Action type: {action}"
            ]
        }
    
    def _call(
        self, 
        prompt: str, 
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        """Process the prompt and return enhanced structured response."""
        
        # Determine the type of request
        if "tool" in prompt.lower() or "function" in prompt.lower():
            return self._select_appropriate_tool(prompt)
        elif "intent" in prompt.lower():
            return self._classify_intent_enhanced(prompt)
        elif "entities" in prompt.lower():
            return self._extract_entities_enhanced(prompt)
        elif "action" in prompt.lower():
            return self._determine_action(prompt)
        else:
            return self._comprehensive_parse(prompt)
    
    def _select_appropriate_tool(self, prompt: str) -> str:
        """Enhanced tool selection with better pattern matching."""
        prompt_lower = prompt.lower()
        
        # Score each tool based on pattern matches
        tool_scores = {}
        for tool_name, patterns in self.tool_usage_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, prompt_lower, re.IGNORECASE))
                score += matches * 10  # Weight pattern matches highly
                
                # Bonus points for exact keyword matches
                if any(keyword in prompt_lower for keyword in pattern.split()):
                    score += 5
            
            tool_scores[tool_name] = score
        
        # Find the best tool
        best_tool = max(tool_scores, key=tool_scores.get) if tool_scores else "UnknownTool"
        best_score = tool_scores.get(best_tool, 0)
        
        # If no good match, be more specific about what we found
        if best_score < 5:
            return self._fallback_tool_selection(prompt)
        
        # Return realistic tool selection response
        action = self._extract_primary_action(prompt)
        template = random.choice(self.response_templates["tool_selection"])
        return template.format(action=action, tool=best_tool)
    
    def _fallback_tool_selection(self, prompt: str) -> str:
        """Fallback tool selection when no clear pattern matches."""
        # Look for specific keywords that might indicate tool type
        keywords_to_tools = {
            "move": "MoveTool", "go": "MoveTool", "travel": "MoveTool",
            "look": "LookTool", "examine": "LookTool", "inspect": "LookTool",
            "take": "TakeTool", "grab": "TakeTool", "get": "TakeTool",
            "talk": "TalkTool", "speak": "TalkTool", "ask": "TalkTool",
            "attack": "AttackTool", "fight": "AttackTool", "combat": "AttackTool",
            "cast": "MagicTool", "magic": "MagicTool", "spell": "MagicTool",
            "search": "SearchTool", "find": "SearchTool", "explore": "SearchTool",
            "unlock": "UnlockTool", "open": "UnlockTool", "pick": "UnlockTool"
        }
        
        for keyword, tool in keywords_to_tools.items():
            if keyword in prompt.lower():
                return f"Fallback selection: {tool} (keyword: {keyword})"
        
        return "No suitable tool identified for this command."
    
    def _classify_intent_enhanced(self, prompt: str) -> str:
        """Enhanced intent classification with more nuanced categories."""
        intent_patterns = {
            "MOVEMENT": {
                "patterns": [r'\b(go|move|walk|run|travel|head|navigate|proceed)\b', 
                           r'\b(north|south|east|west|up|down|enter|exit)\b'],
                "confidence": 0.9
            },
            "OBSERVATION": {
                "patterns": [r'\b(look|examine|inspect|observe|check|view|see|study)\b',
                           r'\b(what|how|describe|appearance|details|around)\b'],
                "confidence": 0.85
            },
            "INTERACTION": {
                "patterns": [r'\b(use|take|grab|pick|drop|open|close|push|pull)\b',
                           r'\b(with|handle|manipulate|operate)\b'],
                "confidence": 0.8
            },
            "COMMUNICATION": {
                "patterns": [r'\b(talk|speak|say|ask|tell|whisper|shout|discuss)\b',
                           r'\b(to|with|about|conversation|dialogue)\b'],
                "confidence": 0.85
            },
            "COMBAT": {
                "patterns": [r'\b(attack|fight|strike|hit|defend|battle|combat)\b',
                           r'\b(weapon|sword|magic|spell|damage|defeat)\b'],
                "confidence": 0.9
            },
            "MAGIC": {
                "patterns": [r'\b(cast|enchant|summon|dispel|brew|ritual|magic)\b',
                           r'\b(spell|mana|magical|mystical|arcane)\b'],
                "confidence": 0.85
            }
        }
        
        text = prompt.lower()
        best_intent = "UNKNOWN"
        best_score = 0
        
        for intent, data in intent_patterns.items():
            score = 0
            for pattern in data["patterns"]:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches * data["confidence"]
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return f"Intent: {best_intent} (confidence: {min(best_score, 1.0):.2f})"
    
    def _extract_entities_enhanced(self, prompt: str) -> str:
        """Enhanced entity extraction with confidence scoring."""
        found_entities = []
        text = prompt.lower()
        
        for entity_type, entities in self.entity_database.items():
            for entity in entities:
                if entity in text:
                    # Calculate confidence based on context
                    confidence = 0.8
                    if re.search(rf'\b{re.escape(entity)}\b', text):
                        confidence = 0.95  # Higher confidence for exact word matches
                    
                    found_entities.append(f"{entity_type}: {entity} ({confidence:.2f})")
        
       
        
        if not found_entities:
            return "Entities: None detected"
        
        return "Entities: " + ", ".join(found_entities)
    
    def _determine_action(self, prompt: str) -> str:
        """Determine the primary action from the prompt."""
        action = self._extract_primary_action(prompt)
        confidence = self._calculate_action_confidence(prompt, action)
        
        template = random.choice(self.response_templates["action_classification"])
        return template.format(action=action) + f" (confidence: {confidence:.2f})"
    
    def _extract_primary_action(self, prompt: str) -> str:
        """Extract the primary action verb from the prompt."""
        action_verbs = [
            "go", "move", "walk", "run", "travel", "head", "navigate",
            "look", "examine", "inspect", "observe", "check", "view",
            "take", "grab", "pick", "get", "collect", "obtain",
            "talk", "speak", "say", "ask", "tell", "discuss",
            "attack", "fight", "strike", "hit", "battle", "combat",
            "cast", "use", "open", "close", "push", "pull"
        ]
        
        words = prompt.lower().split()
        for word in words:
            if word in action_verbs:
                return word
        
        return "unknown"
    
    def _calculate_action_confidence(self, prompt: str, action: str) -> float:
        """Calculate confidence score for the identified action."""
        base_confidence = 0.7
        
        # Boost confidence for clear action words
        if action != "unknown":
            base_confidence += 0.2
        
        # Check for supporting context
        context_indicators = ["carefully", "quickly", "quietly", "forcefully"]
        if any(indicator in prompt.lower() for indicator in context_indicators):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _comprehensive_parse(self, prompt: str) -> str:
        """Comprehensive parsing that combines multiple analysis types."""
        intent = self._classify_intent_enhanced(prompt)
        entities = self._extract_entities_enhanced(prompt)
        action = self._determine_action(prompt)
        
        return f"{intent}; {entities}; {action}"
    
    @property
    def _llm_type(self) -> str:
        return "enhanced_fantasy_llm"


class LangChainParserEnhancer:
    """
    LangChain-based enhancement for the text parser that provides 
    advanced natural language understanding capabilities.
    """
    
    def __init__(self):
        """Initialize the LangChain parser enhancer."""
        self.logger = logging.getLogger("text_parser.langchain")
        
        # Initialize custom LLM
        self.llm = FantasyLLM()
        
        # Initialize memory for conversation context
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Define prompt templates for different parsing tasks
        self._init_prompt_templates()
        
        # Initialize chains
        self._init_chains()
        
        self.logger.info("LangChain parser enhancer initialized.")
    
    def _init_prompt_templates(self):
        """Initialize prompt templates for various parsing tasks."""
        
        # Intent classification template
        self.intent_template = PromptTemplate(
            input_variables=["user_input", "chat_history"],
            template="""
            You are a fantasy game parser. Analyze the following user input and classify its intent.
            
            Chat History: {chat_history}
            User Input: {user_input}
            
            Classify the intent from these categories:
            - MOVEMENT: Going somewhere, entering/exiting
            - OBSERVATION: Looking, examining, inspecting
            - INTERACTION: Using, taking, manipulating objects
            - COMMUNICATION: Talking, asking, telling
            - COMBAT: Fighting, attacking, defending
            - INVENTORY: Managing items, equipment
            - MAGIC: Casting spells, using magic
            - META: Help, status, game commands
            
            Respond with just the intent category.
            """
        )
        
        # Entity extraction template
        self.entity_template = PromptTemplate(
            input_variables=["user_input"],
            template="""
            Extract entities from this fantasy game command: {user_input}
            
            Identify and categorize:
            - ITEMS: weapons, tools, potions, scrolls, etc.
            - LOCATIONS: rooms, areas, buildings, geographical features
            - NPCS: characters, creatures, monsters
            - ACTIONS: verbs describing what to do
            - MODIFIERS: adjectives, adverbs, descriptive words
            
            Format as: CATEGORY: entity_name
            """
        )
        
        # Context analysis template
        self.context_template = PromptTemplate(
            input_variables=["user_input", "spacy_entities"],
            template="""
            Analyze the context and implications of this fantasy command: {user_input}
            
            spaCy entities found: {spacy_entities}
            
            Consider:
            - Implied actions or consequences
            - Emotional tone or urgency
            - Spatial relationships (where, how)
            - Temporal aspects (when, duration)
            - Player intent and goals
            
            Provide contextual insights that would help a game master respond appropriately.
            """
        )
    
    def _init_chains(self):
        """Initialize LangChain chains for different parsing tasks."""
        
        # Intent classification chain
        self.intent_chain = LLMChain(
            llm=self.llm,
            prompt=self.intent_template,
            memory=self.memory,
            verbose=False
        )
        
        # Entity extraction chain
        self.entity_chain = LLMChain(
            llm=self.llm,
            prompt=self.entity_template,
            verbose=False
        )
        
        # Context analysis chain
        self.context_chain = LLMChain(
            llm=self.llm,
            prompt=self.context_template,
            verbose=False
        )
    
    def enhance_parse(self, user_input: str, spacy_entities: List[Dict]) -> Dict[str, Any]:
        """
        Use LangChain to enhance parsing with advanced NLP analysis.
        
        Args:
            user_input: The raw user input text
            spacy_entities: Entities found by spaCy
            
        Returns:
            Dict containing enhanced parsing results
        """
        try:
            # Get intent classification
            intent_result = self.intent_chain.run(user_input=user_input)
            
            # Extract additional entities
            entity_result = self.entity_chain.run(user_input=user_input)
            
            # Analyze context
            spacy_entities_str = ", ".join([f"{e['label']}: {e['text']}" for e in spacy_entities])
            context_result = self.context_chain.run(
                user_input=user_input,
                spacy_entities=spacy_entities_str
            )
            
            return {
                "langchain_intent": intent_result.strip(),
                "langchain_entities": entity_result.strip(),
                "langchain_context": context_result.strip(),
                "enhanced_confidence": self._calculate_enhanced_confidence(user_input, intent_result)
            }
            
        except Exception as e:
            self.logger.error(f"Error in LangChain enhancement: {e}")
            return {
                "langchain_intent": "UNKNOWN",
                "langchain_entities": "None",
                "langchain_context": "Analysis failed",
                "enhanced_confidence": 0.3
            }
    
    def _calculate_enhanced_confidence(self, user_input: str, intent: str) -> float:
        """Calculate confidence score based on parsing quality."""
        base_confidence = 0.7
        
        # Boost confidence for clear intents
        if intent and intent != "UNKNOWN":
            base_confidence += 0.2
        
        # Boost confidence for longer, more descriptive inputs
        if len(user_input.split()) > 3:
            base_confidence += 0.1
        
        # Cap at 1.0
        return min(base_confidence, 1.0)


class ActionType(Enum):
    """Categories of player actions for classification."""
    MOVEMENT = auto()       # Moving in space
    OBSERVATION = auto()    # Looking, examining, perceiving
    INTERACTION = auto()    # Touching, using, manipulating
    COMMUNICATION = auto()  # Talking, asking, telling
    COMBAT = auto()         # Fighting, attacking, defending
    INVENTORY = auto()      # Taking, dropping, inventory management
    META = auto()           # Help, quit, save, etc.
    UNKNOWN = auto()        # Could not classify


class ParserEngine:
    """
    Main engine for parsing player input text into structured commands.
    """
    
    def __init__(self):
        """Initialize the parser engine with vocabulary, patterns, and spaCy NLP."""
        self.logger = logging.getLogger("text_parser.engine")
        self.logger.info("Initializing ParserEngine...")

        # Load spaCy model and initialize EntityRuler
        try:
            self.logger.info("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info(f"spaCy model loaded. Pipeline: {self.nlp.pipe_names}")
            
            # Remove existing entity_ruler if present to avoid conflicts
            if "entity_ruler" in self.nlp.pipe_names:
                self.nlp.remove_pipe("entity_ruler")
                self.logger.info("Removed existing entity_ruler")
            
            # Add fresh EntityRuler
            self.logger.info("Adding EntityRuler to pipeline...")
            self.ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            self.logger.info(f"EntityRuler added. Pipeline: {self.nlp.pipe_names}")
            
            # Initialize patterns
            self._init_entity_ruler_patterns()
            self.logger.info("spaCy EntityRuler initialized successfully.")
        except OSError as e:
            self.logger.error(f"spaCy model 'en_core_web_sm' not found: {e}")
            self.nlp = None
            self.ruler = None
        except Exception as e:
            self.logger.error(f"Failed to initialize spaCy EntityRuler: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.nlp = None
            self.ruler = None
        
        # Initialize LangChain enhancer for Phase 2 integration
        try:
            self.langchain_enhancer = LangChainParserEnhancer()
            self.logger.info("LangChain parser enhancer initialized successfully.")
        except Exception as e:
            self.logger.warning(f"Could not initialize LangChain enhancer: {e}")
            self.langchain_enhancer = None
        
        # Connect VocabularyManager for dynamic entity updates (Phase 2)
        vocabulary_manager.set_parser_engine(self)
        self.vocabulary_manager = vocabulary_manager
        
        # Initialize patterns and action mappings
        self.patterns = self._init_patterns()
        self.action_mappings = self._init_action_mappings()
        
        # Phase 3: Initialize LangChain agent for advanced fallback parsing
        self._setup_langchain_agent()
        
        self.logger.info("ParserEngine initialized.")

    def _init_entity_ruler_patterns(self):
        """Initialize EntityRuler with predefined fantasy entity patterns."""
        if self.ruler is None:
            self.logger.warning("EntityRuler is None, skipping pattern initialization.")
            return

        patterns = [
            {"label": "FANTASY_ITEM", "pattern": "Moonblade", "id": "item_moonblade"},
            {"label": "FANTASY_NPC", "pattern": "Selene", "id": "npc_selene"},
            {"label": "FANTASY_LOCATION", "pattern": "Ironroot Caverns", "id": "loc_ironroot"},
            {"label": "FANTASY_ITEM", "pattern": [{"LOWER": "vorpal"}, {"LOWER": "sword"}], "id": "item_vorpal_sword"},
            # Add more of your core world entities here
        ]
        
        try:
            self.ruler.add_patterns(patterns)
            self.logger.info(f"EntityRuler initialized with {len(patterns)} patterns.")
        except Exception as e:
            self.logger.error(f"Failed to add patterns to EntityRuler: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def add_world_entity(self, name: str, label: str, entity_id: Optional[str] = None):
        """
        Dynamically add a new entity to spaCy's EntityRuler.
        Args:
            name: The text name of the entity (e.g., "Dragon's Peak").
            label: The type of entity (e.g., "FANTASY_LOCATION", "FANTASY_NPC").
            entity_id: An optional unique ID for this entity in the game.
        """
        if self.ruler is None:
            self.logger.warning(f"EntityRuler is None. Cannot add entity: {name} ({label})")
            return

        # Clean the name and handle multi-token entities
        clean_name = name.strip()
        if not clean_name:
            self.logger.warning(f"Empty entity name provided for label: {label}")
            return

        try:
            # Create pattern entry based on whether it's multi-token or single token
            if " " in clean_name:
                # Multi-token entity - create token-based pattern
                pattern_tokens = []
                for token in clean_name.split():
                    pattern_tokens.append({"LOWER": token.lower()})
                pattern_entry = {"label": label.upper(), "pattern": pattern_tokens}
            else:
                # Single token - use simple string pattern
                pattern_entry = {"label": label.upper(), "pattern": {"LOWER": clean_name.lower()}}

            if entity_id:
                pattern_entry["id"] = entity_id
            
            # Add the pattern to the ruler
            self.ruler.add_patterns([pattern_entry])
            self.logger.debug(f"Added entity to EntityRuler: {clean_name} ({label.upper()}), ID: {entity_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to add entity {clean_name} to EntityRuler: {e}")
    
    def _init_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for command parsing."""
        patterns = {
            # Simple movement: go north, move west, etc.
            "movement": re.compile(r"^(?:go|move|walk|run|head|travel)(?:\s+to)?\s+([a-zA-Z]+)$", re.IGNORECASE),
            
            # Look: look, look around, look at X, examine X
            "look": re.compile(r"^(?:look|examine|inspect|observe)(?:\s+(?:at|around|in|inside))?\s*(.*)$", re.IGNORECASE),
            
            # Take/Get: take X, get X, pick up X
            "take": re.compile(r"^(?:take|get|grab|pick up)\s+(.+)$", re.IGNORECASE),
            
            # Drop: drop X, put down X
            "drop": re.compile(r"^(?:drop|discard|put down|throw away)\s+(.+)$", re.IGNORECASE),
            
            # Use: use X, activate X, with Y
            "use": re.compile(r"^(?:use|activate|operate|with)\s+(.+?)(?:\s+(?:on|with)\s+(.+))?$", re.IGNORECASE),
            
            # Talk: talk to X, speak with X, ask X about Y
            "talk": re.compile(r"^(?:talk|speak|chat|converse)(?:\s+(?:to|with))?\s+(.+?)(?:\s+about\s+(.+))?$", re.IGNORECASE),
            
            # Attack: attack X, fight X, hit X with Y
            "attack": re.compile(r"^(?:attack|fight|hit|strike)\s+(.+?)(?:\s+with\s+(.+))?$", re.IGNORECASE),
            
            # Inventory: inventory, i, check inventory
            "inventory": re.compile(r"^(?:inventory|i|items|check inventory)$", re.IGNORECASE),
            
            # Help: help, ?, commands, etc.
            "help": re.compile(r"^(?:help|\?|commands|what can i do)$", re.IGNORECASE),
            
            # Search: search for X, look for X, find X
            "search": re.compile(r"^(?:search|look for|find|explore|investigate|check)\s+(.+)$", re.IGNORECASE),
            
            # Unlock: unlock X, open X with key, pick lock on X
            "unlock": re.compile(r"^(?:unlock|open|pick(?:\s+lock)?)\s+(.+?)(?:\s+(?:with|using)\s+(.+))?$", re.IGNORECASE),
            
            # Unequip: take off X, remove X, unequip X
            "unequip": re.compile(r"^(?:take off|remove|unequip)\s+(.+)$", re.IGNORECASE),
        }
        return patterns
    
    def _init_action_mappings(self) -> Dict[str, ActionType]:
        """Initialize mappings from actions to action types."""
        return {
            "go": ActionType.MOVEMENT,
            "move": ActionType.MOVEMENT,
            "walk": ActionType.MOVEMENT,
            "run": ActionType.MOVEMENT,
            "look": ActionType.OBSERVATION,
            "examine": ActionType.OBSERVATION,
            "inspect": ActionType.OBSERVATION,
            "observe": ActionType.OBSERVATION,
            "take": ActionType.INVENTORY,
            "get": ActionType.INVENTORY,
            "grab": ActionType.INVENTORY,
            "drop": ActionType.INVENTORY,
            "discard": ActionType.INVENTORY,
            "use": ActionType.INTERACTION,
            "activate": ActionType.INTERACTION,
            "operate": ActionType.INTERACTION,
            "talk": ActionType.COMMUNICATION,
            "speak": ActionType.COMMUNICATION,
            "ask": ActionType.COMMUNICATION,
            "tell": ActionType.COMMUNICATION,
            "attack": ActionType.COMBAT,
            "fight": ActionType.COMBAT,
            "hit": ActionType.COMBAT,
            "inventory": ActionType.INVENTORY,
            "help": ActionType.META,
            "search": ActionType.OBSERVATION,  # Searching is a form of observation
            "unlock": ActionType.INTERACTION,  # Unlocking containers/doors is an interaction
            "unequip": ActionType.INTERACTION, # Unequipping items is an interaction
        }
    
    def parse(self, input_text: str) -> Optional[ParsedCommand]:
        """
        Parse player input text into a structured command.
        
        Args:
            input_text: Raw text input from the player
            
        Returns:
            ParsedCommand object if parsing succeeds, None otherwise
        """
        if not input_text or not input_text.strip():
            self.logger.debug("Received empty or whitespace-only input.")
            return None # Or a specific command for empty input
            
        text_to_parse = input_text.strip() # Keep original case for spaCy if beneficial
        
        # Special case: direct detection for "take off" and "unequip" commands
        text_lower = text_to_parse.lower()
        if (text_lower.startswith("take off ") or 
            "take off" in text_lower or 
            text_lower.startswith("unequip ") or 
            text_lower.startswith("remove ") or
            (text_lower.startswith("take ") and " off" in text_lower)):
            
            # Extract the item name from the command
            item_name = ""
            if text_lower.startswith("take off "):
                item_name = text_to_parse[9:].strip()
            elif text_lower.startswith("unequip "):
                item_name = text_to_parse[8:].strip()
            elif text_lower.startswith("remove "):
                item_name = text_to_parse[7:].strip()
            elif "take off" in text_lower:
                item_name = text_lower.split("take off")[1].strip()
            elif text_lower.startswith("take ") and " off" in text_lower:
                item_name = text_lower.replace("take ", "").replace(" off", "").strip()
            
            # Create the command with high confidence
            self.logger.info(f"Direct detection of unequip command: '{text_to_parse}' -> item: '{item_name}'")
            
            # Directly handle the unequip command since pattern detection is working
            if (_game_systems._integration_manager and 
                hasattr(_game_systems._integration_manager, 'systems')):
                
                from system_integration_manager import SystemType
                
                if SystemType.INVENTORY in _game_systems._integration_manager.systems:
                    inventory_system = _game_systems._integration_manager.systems[SystemType.INVENTORY]
                    
                    # Detect slot based on item name
                    slot_name = None
                    for keyword, slot in {
                        "head": "head", "helmet": "head", "hat": "head",
                        "chest": "chest", "armor": "chest", "body": "chest",
                        "legs": "legs", "pants": "legs", "greaves": "legs", 
                        "feet": "feet", "boots": "feet", "shoes": "feet",
                        "hands": "hands", "gloves": "hands", "gauntlets": "hands",
                        "main hand": "main_hand", "main_hand": "main_hand", "weapon": "main_hand",
                        "off hand": "off_hand", "off_hand": "off_hand", "shield": "off_hand",
                        "ring": "ring_left", "left ring": "ring_left",
                        "right ring": "ring_right",
                        "neck": "neck", "necklace": "neck",
                        "belt": "belt",
                        "cloak": "back", "cape": "back"
                    }.items():
                        if keyword == item_name or keyword in item_name:
                            slot_name = slot
                            break
                    
                    self.logger.info(f"Executing unequip command with item_name='{item_name}', slot='{slot_name}'")
                    result = inventory_system.handle_player_command(
                        "default_player", 
                        "UNEQUIP", 
                        {
                            "item_name": None if slot_name else item_name,
                            "slot": slot_name
                        }
                    )
                    
                    # Create context with result information
                    context = {
                        "direct_unequip_detection": True,
                        "system_response": result.get("message", f"You unequip {item_name}."),
                        "success": result.get("success", False),
                        "equipment_data": result.get("data", {})
                    }
                    
                    return ParsedCommand(
                        action="unequip",
                        target=item_name,
                        confidence=0.95,
                        raw_text=input_text,
                        context=context
                    )
            
            # Fallback if no direct execution
            return ParsedCommand(
                action="unequip",
                target=item_name,
                confidence=0.95,
                raw_text=input_text,
                context={"direct_unequip_detection": True}
            )
        
        spacy_entities_found = []
        if self.nlp:
            doc = self.nlp(text_to_parse)
            spacy_entities_found = [
                {"text": ent.text, "label": ent.label_, "id": ent.ent_id_} 
                for ent in doc.ents if ent.label_.startswith("FANTASY_") # Filter for our custom entities
            ]
            if spacy_entities_found:
                self.logger.debug(f"spaCy recognized entities: {spacy_entities_found}")
        
        # Initialize context for ParsedCommand
        current_context = {"spacy_entities": spacy_entities_found}
        
        # Phase 2: LangChain enhancement for advanced parsing
        langchain_enhancement = {}
        if self.langchain_enhancer:
            try:
                langchain_enhancement = self.langchain_enhancer.enhance_parse(
                    text_to_parse, spacy_entities_found
                )
                current_context.update(langchain_enhancement)
                self.logger.debug(f"LangChain enhancement: {langchain_enhancement}")
            except Exception as e:
                self.logger.warning(f"LangChain enhancement failed: {e}")
        
        text = text_to_parse.lower() # For regex matching, typically use lowercased text
        
        # Try each pattern to see if we get a match
        for action_key, pattern in self.patterns.items():
            match = pattern.match(text)
            if match:
                # Extract the actual verb from the input for pattern-based matches
                words = text.split()
                action_verb = words[0] if words else action_key
                
                # Map pattern keys to canonical actions
                if action_key == "movement":
                    canonical_action = self.vocabulary_manager.get_canonical_action(action_verb) or "go"
                elif action_key == "look":
                    canonical_action = "look"
                elif action_key == "take":
                    canonical_action = "take"
                elif action_key == "drop":
                    canonical_action = "drop"
                elif action_key == "use":
                    canonical_action = "use"
                elif action_key == "talk":
                    canonical_action = "talk"
                elif action_key == "attack":
                    canonical_action = "attack"
                elif action_key == "inventory":
                    canonical_action = "inventory"
                elif action_key == "help":
                    canonical_action = "help"
                elif action_key == "search":
                    canonical_action = "search"
                elif action_key == "unlock":
                    canonical_action = "unlock"
                elif action_key == "unequip":
                    canonical_action = "unequip"
                else:
                    canonical_action = action_verb
                
                target = None
                modifiers = {} # Initialize modifiers
                
                groups = match.groups()
                # Example: "go north", pattern r"... (direction)" -> groups[0] = "north"
                # Example: "take sword", pattern r"... (item)" -> groups[0] = "sword"
                # Example: "use key on door", pattern r"... (item) ... (target_object)" -> groups[0]="key", groups[1]="door"

                if groups:
                    if len(groups) > 0 and groups[0] is not None:
                        target = groups[0].strip()
                    if action_key == "use" and len(groups) > 1 and groups[1] is not None:
                        # For "use item on target_object"
                        modifiers["on_target"] = groups[1].strip()
                    elif action_key == "talk" and len(groups) > 1 and groups[1] is not None:
                        # For "talk to character about topic"
                        modifiers["about_topic"] = groups[1].strip()
                    elif action_key == "attack" and len(groups) > 1 and groups[1] is not None:
                        # For "attack target with weapon"
                        modifiers["with_item"] = groups[1].strip()
                    elif action_key == "unlock" and len(groups) > 1 and groups[1] is not None:
                        # For "unlock container with key/lockpick"
                        modifiers["with_item"] = groups[1].strip()
                    # Add more specific modifier extraction based on your patterns
                
                # Map action_key to canonical action if needed, or use directly
                # canonical_action is already set above based on pattern matching
                
                # Use enhanced confidence if available from LangChain
                confidence = langchain_enhancement.get("enhanced_confidence", 0.8)

                command = ParsedCommand(
                    action=canonical_action,
                    target=target,
                    modifiers=modifiers,
                    context=current_context, # Add spaCy entities and LangChain analysis
                    confidence=confidence,
                    raw_text=input_text
                )
                
                # Enhance command with entity resolutions
                return self.enhance_command_with_entities(command)
                
        # If we get here, no pattern matched
        # Try to extract a simple verb-noun structure
        words = text.split()
        if len(words) >= 1:
            # Use VocabularyManager to get canonical action
            potential_action = words[0]
            canonical_action = self.vocabulary_manager.get_canonical_action(potential_action)
            
            if canonical_action:
                target = " ".join(words[1:]) if len(words) > 1 else None
                
                # Use enhanced confidence if available, otherwise use default
                confidence = langchain_enhancement.get("enhanced_confidence", 0.5)
                
                command = ParsedCommand(
                    action=canonical_action,
                    target=target,
                    context=current_context, # Add spaCy entities and LangChain analysis
                    confidence=confidence,
                    raw_text=input_text
                )
                
                # Enhance command with entity resolutions
                return self.enhance_command_with_entities(command)
            elif potential_action in self.action_mappings:
                action = potential_action # Fallback to direct mapping
                target = " ".join(words[1:]) if len(words) > 1 else None
                
                # Use enhanced confidence if available, otherwise use default
                confidence = langchain_enhancement.get("enhanced_confidence", 0.5)
                
                command = ParsedCommand(
                    action=action,
                    target=target,
                    context=current_context, # Add spaCy entities and LangChain analysis
                    confidence=confidence,
                    raw_text=input_text
                )
                
                # Enhance command with entity resolutions
                return self.enhance_command_with_entities(command)
        
        self.logger.debug(f"Could not parse input with regex or simple split: '{input_text}'")
        
        # Phase 3: Try LangChain agent as fallback before giving up
        if hasattr(self, 'agent_executor') and self.agent_executor:
            try:
                self.logger.debug(f"Using LangChain agent as fallback for: '{input_text}'")
                agent_result = self.agent_executor.invoke({
                    "input": input_text,
                    "chat_history": []  # Could enhance with actual chat history
                })
                
                # Convert agent result to ParsedCommand
                if agent_result and "output" in agent_result:
                    agent_command = self._convert_langchain_to_parsed_command(
                        agent_result["output"], 
                        input_text,
                        agent_result.get("intermediate_steps", [])
                    )
                    
                    if agent_command and agent_command.action != "unknown":
                        self.logger.info(f"LangChain agent successfully parsed: {agent_command.action}")
                        return agent_command
                
            except Exception as e:
                self.logger.warning(f"LangChain agent failed: {e}")
        
        # Could not parse with any method, return unknown action
        return ParsedCommand(
            action="unknown", # Or a specific "UNPARSED" action
            target=None,
            context=current_context, # Still include any spaCy entities found
            confidence=0.1,
            raw_text=input_text
        )
    
    def parse_enhanced_command(self, input_text: str) -> Optional[ParsedCommand]:
        """
        Enhanced parsing method alias for backward compatibility.
        
        Args:
            input_text: Raw text input from the player
            
        Returns:
            ParsedCommand object if parsing succeeds, None otherwise
        """
        return self.parse(input_text)
    
    def get_suggestions(self, input_text: str) -> List[str]:
        """
        Get suggestions for failed parsing.
        
        Args:
            input_text: Text input from the player
            
        Returns:
            List of command suggestions
        """
        # Clean input for processing
        input_text = input_text.lower().strip()
        words = input_text.split()
        suggestions = []
        
        # Common action templates with examples for different scenarios
        action_templates = {
            "look": [
                "look around", 
                "examine item", 
                "inspect object", 
                "look at target"
            ],
            "movement": [
                "go north", 
                "go south",
                "go east",
                "go west",
                "enter building"
            ],
            "interaction": [
                "take item", 
                "use object", 
                "open container", 
                "push button", 
                "pull lever"
            ],
            "social": [
                "talk to person", 
                "ask about topic", 
            ],
            "combat": [
                "attack enemy", 
                "defend", 
                "retreat", 
                "use skill"
            ],
            "inventory": [
                "inventory", 
                "check items", 
                "equip weapon"
            ],
            "meta": [
                "help", 
                "status", 
                "stats", 
                "skills"
            ],
            "search": [
                "search for treasure",
                "look for hidden items",
                "find secret compartment",
                "explore the area thoroughly"
            ]
        }
        
        # First, check for partial matches with action verbs
        action_verbs = {
            "look": ["look", "examine", "inspect", "view", "observe", "check"],
            "movement": ["go", "move", "walk", "run", "travel", "enter", "exit"],
            "take": ["take", "grab", "pick", "collect", "get"],
            "use": ["use", "activate", "operate", "apply"],
            "talk": ["talk", "speak", "chat", "converse", "ask", "tell"],
            "attack": ["attack", "fight", "strike", "hit"],
            "inventory": ["inventory", "items", "possessions", "gear"],
            "meta": ["help", "status", "commands"],
            "search": ["search", "look for", "find", "explore", "investigate"],
            "unlock": ["unlock", "open", "pick"]
        }
        
        # Check for matches in input words
        matched_categories = set()
        for word in words:
            for category, verbs in action_verbs.items():
                for verb in verbs:
                    # Check if word is similar to verb
                    if len(word) >= 2 and len(verb) >= 2:
                        if word.startswith(verb[:min(len(word), 3)]) or verb.startswith(word[:min(len(verb), 3)]):
                            matched_categories.add(category)
                            break
        
        # Extract potential objects/targets from input
        all_verbs = []
        for verbs in action_verbs.values():
            all_verbs.extend(verbs)
            
        common_words = ["the", "a", "an", "at", "to", "with", "on", "in", "from", "about"]
        potential_targets = [w for w in words if w not in all_verbs and w not in common_words and len(w) > 2]
        
        # Generate suggestions based on matched categories
        for category in matched_categories:
            if category in action_templates:
                # Add category-specific suggestions
                suggestions.extend(action_templates[category][:2])  # Add a couple from each category
                
                # If we have potential targets, add targeted suggestions
                if potential_targets and len(potential_targets) > 0:
                    target = " ".join(potential_targets)
                    
                    if category == "look":
                        suggestions.append(f"examine {target}")
                    elif category == "take":
                        suggestions.append(f"take {target}")
                    elif category == "use":
                        suggestions.append(f"use {target}")
                    elif category == "talk":
                        suggestions.append(f"talk to {target}")
                    elif category == "attack":
                        suggestions.append(f"attack {target}")
        
        # If we don't have enough suggestions, add general ones
        if len(suggestions) < 3:
            general_suggestions = [
                "look around",
                "inventory",
                "help",
                "status",
                "go north",
                "go south",
                "go east",
                "go west"
            ]
            
            for suggestion in general_suggestions:
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
                    if len(suggestions) >= 5:  # Limit to 5 suggestions
                        break
        
        # Remove duplicates and limit to top 3
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
                
        return unique_suggestions[:3]
    
    def resolve_entity_ids(self, target_text: str) -> Dict[str, Optional[str]]:
        """
        Resolve target text to entity IDs using VocabularyManager.
        
        Args:
            target_text: The target text to resolve
            
        Returns:
            Dictionary with possible entity resolutions
        """
        if not target_text:
            return {}
        
        resolutions = {}
        
        # Try to resolve as item
        item_id = self.vocabulary_manager.get_item_id(target_text)
        if item_id:
            resolutions["item_id"] = item_id
        
        # Try to resolve as character
        char_id = self.vocabulary_manager.get_character_id(target_text)
        if char_id:
            resolutions["character_id"] = char_id
        
        # Try to resolve as location
        loc_id = self.vocabulary_manager.get_location_id(target_text)
        if loc_id:
            resolutions["location_id"] = loc_id
        
        # Try to resolve as direction
        direction = self.vocabulary_manager.get_canonical_direction(target_text)
        if direction:
            resolutions["direction"] = direction
        
        return resolutions
    
    def enhance_command_with_entities(self, command: ParsedCommand) -> ParsedCommand:
        """
        Enhance a parsed command with entity ID resolutions.
        
        Args:
            command: The parsed command to enhance
            
        Returns:
            Enhanced command with entity resolutions
        """
        if not command.target:
            return command
        
        # Resolve target to entity IDs
        entity_resolutions = self.resolve_entity_ids(command.target)
        
        if entity_resolutions:
            # Add resolutions to command context
            if not command.context:
                command.context = {}
            command.context["entity_resolutions"] = entity_resolutions
            
            # Boost confidence if we found entity matches
            command.confidence = min(command.confidence + 0.1, 1.0)
        
        # Phase 3: Check if confidence is low and use agent as fallback
        if command.confidence < 0.6 and hasattr(self, 'agent_executor') and self.agent_executor:
            try:
                self.logger.debug(f"Low confidence ({command.confidence}), trying LangChain agent for: '{command.raw_text}'")
                agent_result = self.agent_executor.invoke({
                    "input": command.raw_text,
                    "chat_history": []  # Could enhance with actual chat history
                })
                
                # Convert agent result to ParsedCommand
                if agent_result:
                    agent_command = self._convert_langchain_to_parsed_command(
                        agent_result, 
                        command.raw_text
                    )
                    
                    # Use agent result if it has higher confidence
                    if (agent_command and 
                        agent_command.action != "unknown" and 
                        agent_command.confidence > command.confidence):
                        self.logger.info(f"LangChain agent improved confidence from {command.confidence} to {agent_command.confidence}")
                        return agent_command
                
            except Exception as e:
                self.logger.warning(f"LangChain agent fallback failed: {e}")
        
        return command

    # Phase 3: LangChain Agent Components
    def _setup_langchain_agent(self):
        """Setup LangChain agent with tools for parsing fallback."""
        try:
            # Initialize OpenRouter LLM
            llm = OpenRouterLLM()
            
            # Create tools list
            tools = [
                MoveTool(),
                LookTool(), 
                TakeTool(),
                UseTool(),
                TalkTool(),
                AttackTool(),
                InventoryTool(),
                DropTool(),
                CastSpellTool(),
                SearchTool(),
                EquipTool(),
                UnequipTool()
            ]
            
            # Create agent using modern OpenAI Tools approach
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a fantasy game command parser. Parse player input into appropriate game actions.
                
                Available tools represent different game actions. Choose the most appropriate tool based on the player's intent.
                Always respond with a tool call - never provide text-only responses.
                
                IMPORTANT DISAMBIGUATION RULES:
                - For commands like "take off ring", "remove helmet", "unequip sword" - ALWAYS use the UnequipTool, NOT the TakeTool
                - Only use TakeTool for picking up items from the environment (e.g., "take sword from ground")
                - If a command contains phrases like "take off", "remove", or "unequip" related to worn items, use UnequipTool
                
                Examples:
                - "go north" -> use move tool with "north"
                - "examine sword" -> use look tool with "sword" 
                - "take potion" -> use take tool with "potion"
                - "attack dragon" -> use attack tool with "dragon"
                - "take off ring" -> use unequip tool with "ring"
                - "remove helmet" -> use unequip tool with "helmet"
                """),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create agent using the modern create_openai_tools_agent function
            agent = create_openai_tools_agent(llm, tools, prompt)
            
            # Enable intermediate steps to capture tool calls
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=False,
                return_intermediate_steps=True
            )
            self.logger.info("LangChain agent initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize LangChain agent: {e}")
            self.agent_executor = None

    def _convert_langchain_to_parsed_command(self, agent_result: str, input_text: str, intermediate_steps=None) -> ParsedCommand:
        """
        Convert LangChain agent output to ParsedCommand.
        
        Args:
            agent_result: Text result from LangChain agent
            input_text: Original user input
            intermediate_steps: Tool execution steps from agent executor
            
        Returns:
            ParsedCommand object
        """
        try:
            # Check if we have intermediate steps with tool executions
            if intermediate_steps and len(intermediate_steps) > 0:
                # Extract the most recent tool execution
                last_tool_step = intermediate_steps[-1]
                tool_action, tool_output = last_tool_step
                
                # Extract tool name
                tool_used = tool_action.tool
                
                # Try to parse the tool output as JSON
                try:
                    result_data = json.loads(tool_output)
                    
                    # Check for redirection or special action override
                    if "redirect_to" in result_data:
                        # Use the redirected action instead of the original tool
                        action = result_data.get("action", result_data.get("redirect_to", "unknown"))
                        self.logger.info(f"Tool redirection detected: {tool_used} -> {action}")
                    else:
                        # Extract data from tool output
                        action = result_data.get("action", "unknown")
                    
                    target = result_data.get("target")
                    confidence = result_data.get("confidence", 0.8)
                    system_response = result_data.get("system_response", "No system response")
                    
                    # Create modifiers based on action type
                    modifiers = {}
                    
                    # Handle complex patterns from specific tools
                    if "on_target" in result_data:
                        modifiers["on_target"] = result_data["on_target"]
                    if "about_topic" in result_data:
                        modifiers["about_topic"] = result_data["about_topic"] 
                    if "with_item" in result_data:
                        modifiers["with_item"] = result_data["with_item"]
                        
                except json.JSONDecodeError:
                    # If tool output isn't JSON, use action from tool name
                    self.logger.warning(f"Could not parse tool output as JSON: {tool_output}")
                    action = tool_used.lower()
                    
                    # Try to extract target from input text using basic NLP
                    target = self._extract_target_from_input(input_text, action)
                    confidence = 0.7
                    modifiers = {}
                    system_response = "No system response"
            else:
                # No tool was used, try to extract from agent's text output
                try:
                    # First try if agent_result happens to be valid JSON
                    result_data = json.loads(agent_result)
                    
                    action = result_data.get("action", "unknown")
                    target = result_data.get("target")
                    confidence = result_data.get("confidence", 0.6)
                    tool_used = "Unknown"
                    modifiers = {}
                    system_response = result_data.get("system_response", "No system response")
                    
                except json.JSONDecodeError:
                    # Fall back to simple text parsing
                    action = self._extract_action_from_text(agent_result)
                    target = self._extract_target_from_input(input_text, action)
                    confidence = 0.6
                    tool_used = "Unknown"
                    modifiers = {}
                    system_response = "No system response"
                
            # Create context indicating LangChain parsing was used
            context = {
                "langchain_agent_used": True,
                "tool_used": tool_used,
                "system_response": system_response,
                "parsing_method": "langchain_agent_fallback"
            }
            
            command = ParsedCommand(
                action=action,
                target=target,
                modifiers=modifiers,
                context=context,
                confidence=confidence,
                raw_text=input_text
            )
            
            self.logger.info(f"LangChain agent parsed '{input_text}' -> {action}({target}) confidence={confidence}")
            return command
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to parse LangChain agent result: {e}")
            return ParsedCommand(
                action="unknown",
                target=None,
                context={"langchain_agent_failed": True, "error": str(e)},
                confidence=0.1,
                raw_text=input_text
            )
        
    def _extract_action_from_text(self, text: str) -> str:
        """Extract an action verb from text output."""
        # Common action verbs in fantasy games
        common_actions = [
            "go", "move", "walk", "run", "look", "examine", "inspect",
            "take", "get", "grab", "drop", "use", "talk", "speak",
            "attack", "fight", "cast", "inventory", "check"
        ]
        
        words = text.lower().split()
        for word in words:
            if word in common_actions:
                return word
            
        # Fallback to most common actions based on context
        if any(word in words for word in ["north", "south", "east", "west", "up", "down"]):
            return "go"
       
        if any(word in words for word in ["see", "view", "describe"]):
            return "look"
        if any(word in words for word in ["item", "object", "weapon"]):
            return "take"
        if any(word in words for word in ["enemy", "monster", "combat"]):
            return "attack"
        if any(word in words for word in ["spell", "magic", "potion"]):
            return "cast"
            
        return "unknown"
    
    def _extract_target_from_input(self, input_text: str, action: str) -> Optional[str]:
        """Extract a target from input text based on action."""
        # Simple heuristic: assume target comes after action word
        words = input_text.lower().split()
        if action in words:
            action_index = words.index(action)
            if action_index < len(words) - 1:
                return " ".join(words[action_index + 1:])
                
        # Direction-based movements
        if action in ["go", "move", "walk"]:
            directions = ["north", "south", "east", "west", "up", "down"]
            for direction in directions:
                if direction in words:
                    return direction
                    
        return None
        

def create_enhanced_langchain_tools():
    """
    Create and return a list of enhanced LangChain tools for game commands.
    
    Returns:
        List of LangChain BaseTool instances
    """
    return [
        MoveTool(),
        LookTool(),
        TakeTool(),
        UseTool(),
        TalkTool(),
        AttackTool(),
        CastSpellTool(),
        InventoryTool(),
        DropTool(),
        SearchTool(),
        UnlockTool(),
        EquipTool(),
        UnequipTool()
    ]

# Alias for backwards compatibility
TextParserEngine = ParserEngine
