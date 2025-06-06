"""
Prompt Builder - Phase 4 of the modular text parser system

This module builds context-aware prompts for LLM interaction, incorporating
RAG retrieval and game state information.
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

from .intent_router import IntentResult, PrimaryIntent, SubIntent
from .action_executor import ActionResult


@dataclass
class PromptContext:
    """Context information for building prompts."""
    intent_result: IntentResult
    game_state: Dict[str, Any]
    rag_documents: List[Dict[str, Any]]
    player_history: List[str]
    character_sheet: Dict[str, Any]
    action_result: Optional[ActionResult] = None
    location_info: Optional[Dict[str, Any]] = None
    inventory_info: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create_basic(cls, intent_result: IntentResult, game_state: Dict[str, Any] = None):
        """Create a basic prompt context with minimal information."""
        return cls(
            intent_result=intent_result,
            game_state=game_state or {},
            rag_documents=[],
            player_history=[],
            character_sheet={}
        )


class PromptBuilder:
    """
    Phase 4 IMPLEMENTED: Builds context-aware prompts for LLM interaction based on 
    intent routing and game context.
    
    This replaces LangChain's prompt templates with modular, intent-aware prompts
    that incorporate game state, RAG context, and player history.
    """
    
    def __init__(self, rag_system=None):
        """Initialize the prompt builder."""
        self.logger = logging.getLogger("text_parser.prompt_builder")
        self.rag_system = rag_system
        self._init_prompt_templates()
        self.logger.info("PromptBuilder initialized")
    
    def _init_prompt_templates(self):
        """Initialize prompt templates for different intent categories."""
        self.templates = {
            "movement": {
                "system": "You are an AI Game Master handling player movement in a fantasy RPG.",
                "context_focus": ["location", "environment", "available_exits"],
                "response_style": "descriptive_narrative"
            },
            "observation": {
                "system": "You are an AI Game Master describing what the player observes.",
                "context_focus": ["location", "objects", "npcs", "atmosphere"],
                "response_style": "detailed_description"
            },
            "interaction": {
                "system": "You are an AI Game Master handling player interactions with objects and NPCs.",
                "context_focus": ["target_object", "npcs", "inventory", "location"],
                "response_style": "interactive_narrative"
            },
            "communication": {
                "system": "You are an AI Game Master managing NPC dialogue and communication.",
                "context_focus": ["npc_data", "relationship", "quests", "lore"],
                "response_style": "dialogue_focused"
            },
            "combat": {
                "system": "You are an AI Game Master orchestrating tactical combat encounters.",
                "context_focus": ["enemies", "environment", "weapons", "tactical_situation"],
                "response_style": "action_packed"
            },
            "inventory": {
                "system": "You are an AI Game Master handling inventory and item management.",
                "context_focus": ["inventory", "items", "equipment", "containers"],
                "response_style": "practical_description"
            },
            "magic": {
                "system": "You are an AI Game Master managing magical effects and spellcasting.",
                "context_focus": ["magic_state", "spells", "mana", "magical_environment"],
                "response_style": "mystical_narrative"
            },
            "meta": {
                "system": "You are an AI Game Master providing game information and assistance.",
                "context_focus": ["game_state", "character_info", "available_options"],
                "response_style": "helpful_informative"
            }
        }
    
    def build_prompt(self, prompt_context: PromptContext) -> str:
        """
        Build a context-aware prompt for LLM interaction.
        
        Args:
            prompt_context: Context information for prompt building
            
        Returns:
            Formatted prompt string ready for LLM processing
        """
        intent_category = prompt_context.intent_result.primary_intent.value
        self.logger.debug(f"Building prompt for intent: {intent_category}")
        
        # Get template for this intent category
        template = self.templates.get(intent_category, self.templates["meta"])
        
        # Build the complete prompt
        prompt_sections = []
        
        # 1. System instruction
        prompt_sections.append(f"SYSTEM: {template['system']}")
        
        # 2. Intent and action context
        prompt_sections.append(self._build_intent_section(prompt_context.intent_result))
        
        # 3. Game state context
        if prompt_context.game_state:
            prompt_sections.append(self._build_context_section(
                prompt_context.game_state, 
                template['context_focus']
            ))
        
        # 4. Character information
        if prompt_context.character_sheet:
            prompt_sections.append(self._build_character_section(prompt_context.character_sheet))
        
        # 5. Location and environment
        if prompt_context.location_info:
            prompt_sections.append(self._build_location_section(prompt_context.location_info))
        
        # 6. Inventory context if relevant
        if prompt_context.inventory_info and intent_category in ["inventory", "interaction"]:
            prompt_sections.append(self._build_inventory_section(prompt_context.inventory_info))
        
        # 7. RAG context (lore, rules, etc.)
        if prompt_context.rag_documents:
            prompt_sections.append(self._build_rag_section(prompt_context.rag_documents))
        
        # 8. Recent history context
        if prompt_context.player_history:
            prompt_sections.append(self._build_history_section(prompt_context.player_history))
        
        # 9. Action result context (if action was executed)
        if prompt_context.action_result:
            prompt_sections.append(self._build_action_result_section(prompt_context.action_result))
        
        # 10. Response style instruction
        prompt_sections.append(self._build_style_instruction(template['response_style'], intent_category))
        
        # 11. Final instruction
        prompt_sections.append(self._build_final_instruction(prompt_context.intent_result))
        
        # Join all sections
        full_prompt = "\n\n".join(filter(None, prompt_sections))
        
        self.logger.debug(f"Generated prompt length: {len(full_prompt)} characters")
        return full_prompt
    
    def build_action_prompt(self, intent_result: IntentResult, action_result: ActionResult, 
                          game_context: Dict[str, Any] = None) -> str:
        """
        Build a prompt specifically for describing action results.
        
        Args:
            intent_result: The intent that was processed
            action_result: Result of the action execution
            game_context: Current game context
            
        Returns:
            Formatted prompt for action result description
        """
        prompt_context = PromptContext.create_basic(intent_result, game_context)
        prompt_context.action_result = action_result
        
        return self.build_prompt(prompt_context)
    
    def _build_intent_section(self, intent_result: IntentResult) -> str:
        """Build the intent and action context section."""
        sections = [
            "INTENT ANALYSIS:",
            f"Primary Intent: {intent_result.primary_intent.value}",
            f"Sub-Intent: {intent_result.sub_intent.value}",
            f"Confidence: {intent_result.confidence:.2f}",
            f"Reasoning: {intent_result.reasoning}"
        ]
        
        if intent_result.metadata:
            sections.append("Intent Metadata:")
            for key, value in intent_result.metadata.items():
                if key != "original_context":  # Skip verbose context
                    sections.append(f"  - {key}: {value}")
        
        return "\n".join(sections)
    
    def _build_context_section(self, game_state: Dict[str, Any], focus_areas: List[str]) -> str:
        """Build the game context section focused on specific areas."""
        if not game_state:
            return ""
        
        sections = ["GAME CONTEXT:"]
        
        # Current location
        if "location" in focus_areas and "current_location" in game_state:
            sections.append(f"Current Location: {game_state['current_location']}")
        
        # Time and environment
        if "environment" in focus_areas:
            if "time_of_day" in game_state:
                sections.append(f"Time: {game_state['time_of_day']}")
            if "weather" in game_state:
                sections.append(f"Weather: {game_state['weather']}")
        
        # Available exits/directions
        if "available_exits" in focus_areas and "available_exits" in game_state:
            exits = game_state["available_exits"]
            if exits:
                sections.append(f"Available Exits: {', '.join(exits)}")
        
        # NPCs present
        if "npcs" in focus_areas and "active_npcs" in game_state:
            npcs = game_state["active_npcs"]
            if npcs:
                npc_list = [npc.get("name", "Unknown") for npc in npcs if isinstance(npc, dict)]
                if npc_list:
                    sections.append(f"NPCs Present: {', '.join(npc_list)}")
        
        # Current quest
        if "quests" in focus_areas and "current_quest" in game_state:
            sections.append(f"Active Quest: {game_state['current_quest']}")
        
        # Recent events
        if "recent_events" in game_state:
            recent = game_state["recent_events"]
            if recent and isinstance(recent, list):
                sections.append("Recent Events:")
                for event in recent[-3:]:  # Last 3 events
                    sections.append(f"  - {event}")
        
        return "\n".join(sections) if len(sections) > 1 else ""
    
    def _build_character_section(self, character_sheet: Dict[str, Any]) -> str:
        """Build the character information section."""
        if not character_sheet:
            return ""
        
        sections = ["CHARACTER INFO:"]
        
        # Basic character info
        if "name" in character_sheet:
            sections.append(f"Name: {character_sheet['name']}")
        if "class" in character_sheet:
            sections.append(f"Class: {character_sheet['class']}")
        if "level" in character_sheet:
            sections.append(f"Level: {character_sheet['level']}")
        
        # Health and status
        if "health" in character_sheet:
            health = character_sheet["health"]
            if isinstance(health, dict):
                current = health.get("current", "?")
                maximum = health.get("max", "?")
                sections.append(f"Health: {current}/{maximum}")
        
        # Magic/mana
        if "mana" in character_sheet:
            mana = character_sheet["mana"]
            if isinstance(mana, dict):
                current = mana.get("current", "?")
                maximum = mana.get("max", "?")
                sections.append(f"Mana: {current}/{maximum}")
        
        # Key skills or domains
        if "domains" in character_sheet:
            domains = character_sheet["domains"]
            if isinstance(domains, dict):
                top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:3]
                domain_str = ", ".join([f"{name}: {level}" for name, level in top_domains])
                sections.append(f"Top Domains: {domain_str}")
        
        return "\n".join(sections) if len(sections) > 1 else ""
    
    def _build_location_section(self, location_info: Dict[str, Any]) -> str:
        """Build the location and environment section."""
        if not location_info:
            return ""
        
        sections = ["LOCATION DETAILS:"]
        
        if "name" in location_info:
            sections.append(f"Location: {location_info['name']}")
        
        if "description" in location_info:
            sections.append(f"Description: {location_info['description']}")
        
        if "items" in location_info and location_info["items"]:
            items = location_info["items"]
            sections.append(f"Items Here: {', '.join(items)}")
        
        if "containers" in location_info and location_info["containers"]:
            containers = location_info["containers"]
            sections.append(f"Containers: {', '.join(containers.keys())}")
        
        if "magical_properties" in location_info:
            sections.append(f"Magical Aura: {location_info['magical_properties']}")
        
        return "\n".join(sections) if len(sections) > 1 else ""
    
    def _build_inventory_section(self, inventory_info: Dict[str, Any]) -> str:
        """Build the inventory context section."""
        if not inventory_info:
            return ""
        
        sections = ["INVENTORY STATUS:"]
        
        if "items" in inventory_info:
            items = inventory_info["items"]
            if items:
                item_list = [f"{item['name']} (x{item.get('quantity', 1)})" for item in items]
                sections.append(f"Carrying: {', '.join(item_list)}")
            else:
                sections.append("Inventory: Empty")
        
        if "equipped" in inventory_info:
            equipped = inventory_info["equipped"]
            if equipped:
                sections.append(f"Equipped: {', '.join(equipped)}")
        
        if "weight" in inventory_info:
            weight = inventory_info["weight"]
            sections.append(f"Encumbrance: {weight.get('current', 0)}/{weight.get('max', 100)}")
        
        return "\n".join(sections) if len(sections) > 1 else ""
    
    def _build_rag_section(self, rag_documents: List[Dict[str, Any]]) -> str:
        """Build the RAG context section with relevant lore and rules."""
        if not rag_documents:
            return ""
        
        sections = ["RELEVANT LORE & RULES:"]
        
        for doc in rag_documents[:3]:  # Limit to top 3 most relevant
            if "content" in doc:
                content = doc["content"]
                # Truncate if too long
                if len(content) > 200:
                    content = content[:200] + "..."
                sections.append(f"- {content}")
            elif "title" in doc and "summary" in doc:
                sections.append(f"- {doc['title']}: {doc['summary']}")
        
        return "\n".join(sections) if len(sections) > 1 else ""
    
    def _build_history_section(self, player_history: List[str]) -> str:
        """Build the recent history section."""
        if not player_history:
            return ""
        
        sections = ["RECENT HISTORY:"]
        
        # Show last 3 actions
        for action in player_history[-3:]:
            sections.append(f"- {action}")
        
        return "\n".join(sections) if len(sections) > 1 else ""
    
    def _build_action_result_section(self, action_result: ActionResult) -> str:
        """Build the action result context section."""
        sections = ["ACTION EXECUTION RESULT:"]
        
        sections.append(f"Success: {action_result.success}")
        sections.append(f"System Message: {action_result.message}")
        
        if action_result.game_state_changes:
            sections.append("State Changes:")
            for key, value in action_result.game_state_changes.items():
                sections.append(f"  - {key}: {value}")
        
        if action_result.metadata:
            relevant_metadata = {k: v for k, v in action_result.metadata.items() 
                                if k not in ["command_processed", "exception"]}
            if relevant_metadata:
                sections.append("Additional Info:")
                for key, value in relevant_metadata.items():
                    sections.append(f"  - {key}: {value}")
        
        return "\n".join(sections)
    
    def _build_style_instruction(self, response_style: str, intent_category: str) -> str:
        """Build the response style instruction."""
        style_instructions = {
            "descriptive_narrative": "Provide rich, immersive descriptions that make the player feel present in the world.",
            "detailed_description": "Focus on sensory details and specific observations that paint a clear picture.",
            "interactive_narrative": "Emphasize the interaction and its consequences, making the world feel responsive.",
            "dialogue_focused": "Prioritize natural dialogue and character interactions over exposition.",
            "action_packed": "Use dynamic language that conveys the intensity and stakes of combat.",
            "practical_description": "Be clear and informative about items, quantities, and practical details.",
            "mystical_narrative": "Use evocative language that captures the wonder and power of magic.",
            "helpful_informative": "Provide clear, useful information in a friendly and accessible manner."
        }
        
        instruction = style_instructions.get(response_style, "Respond appropriately to the player's action.")
        return f"RESPONSE STYLE: {instruction}"
    
    def _build_final_instruction(self, intent_result: IntentResult) -> str:
        """Build the final instruction for the LLM."""
        original_action = intent_result.metadata.get("original_action", "unknown action")
        
        return f"""INSTRUCTION: Based on the above context, generate an appropriate response to the player's action: "{original_action}". 
Your response should be immersive, consistent with the game world, and provide the player with enough information to make their next decision. 
Keep the response engaging but concise (2-4 sentences unless more detail is specifically needed).

RESPONSE:"""
    
    def enhance_with_rag(self, prompt_context: PromptContext, query: str, max_documents: int = 3) -> PromptContext:
        """
        Enhance prompt context with RAG-retrieved documents.
        
        Args:
            prompt_context: Current prompt context
            query: Query string for RAG retrieval
            max_documents: Maximum number of documents to retrieve
            
        Returns:
            Enhanced prompt context with RAG documents
        """
        if not self.rag_system:
            return prompt_context
        
        try:
            # Retrieve relevant documents
            rag_docs = self.rag_system.retrieve_documents(query, max_documents)
            prompt_context.rag_documents = rag_docs
            
            self.logger.debug(f"Enhanced prompt with {len(rag_docs)} RAG documents")
            
        except Exception as e:
            self.logger.error(f"RAG enhancement failed: {e}")
        
        return prompt_context
