"""
Output Generation System for AI GM Brain.

This module transforms decision results into appropriate narrative responses,
handling template processing and dynamic content.
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio
import random
from datetime import datetime

from .ai_gm_decision_logic import DecisionResult, DecisionPriority


class AIGMOutputGenerator:
    """System for generating narrative outputs from decision results."""
    
    def __init__(self, config=None, template_processor=None):
        """
        Initialize the output generator.
        
        Args:
            config: Configuration object or dictionary
            template_processor: Optional template processor for complex templates
        """
        self.logger = logging.getLogger("AIGMOutputGenerator")
        self.config = config or {}
        self.template_processor = template_processor
        
        # Stats tracking
        self.response_count = 0
        self.template_usage = {}
        self.response_type_counts = {}
    
    async def generate_response(self,
                             decision_result: DecisionResult,
                             player_input: str,
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a narrative response from a decision result.
        
        Args:
            decision_result: Decision result from decision logic
            player_input: Original player input
            context: Current game context
            
        Returns:
            Response data dictionary
        """
        self.response_count += 1
        context = context or {}
        
        # Track start of response generation
        self.logger.info(f"Generating response for decision type: {decision_result.action_type}")
        
        # Get appropriate response text based on decision type
        if decision_result.response_template:
            # Use provided template from decision result
            response_text = self._process_template(
                decision_result.response_template,
                decision_result.template_vars,
                decision_result,
                context
            )
        else:
            # Generate response based on action type
            response_text = self._generate_response_for_action_type(
                decision_result.action_type,
                decision_result.success,
                decision_result.action_data,
                context
            )
        
        # Track usage stats
        self._track_response_type(decision_result.action_type)
        
        # Create response data structure
        response_data = {
            'response_text': response_text,
            'metadata': {
                'action_type': decision_result.action_type,
                'priority': decision_result.priority.name if decision_result.priority else None,
                'success': decision_result.success,
                'channels': decision_result.channels,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        # Merge in action data for further processing if needed
        if decision_result.action_data:
            response_data['metadata']['action_data'] = decision_result.action_data
        
        return response_data
    
    def _process_template(self,
                      template: str,
                      template_vars: Dict[str, Any] = None,
                      decision_result: DecisionResult = None,
                      context: Dict[str, Any] = None) -> str:
        """
        Process a response template with variables.
        
        Args:
            template: Template string
            template_vars: Variables for the template
            decision_result: Decision result for more context
            context: Game context
            
        Returns:
            Processed template string
        """
        template_vars = template_vars or {}
        
        # If we have a template processor, use it
        if self.template_processor:
            try:
                return self.template_processor.process(template, {
                    **template_vars,
                    'decision': decision_result.__dict__ if decision_result else {},
                    'context': context or {}
                })
            except Exception as e:
                self.logger.error(f"Error processing template: {e}")
        
        # Simple template replacement as fallback
        result = template
        
        # Replace variables in the template
        for key, value in template_vars.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        # Handle some common dynamic elements
        result = self._add_descriptive_elements(result, context)
        
        return result
    
    def _generate_response_for_action_type(self,
                                      action_type: str,
                                      success: bool = True,
                                      action_data: Dict[str, Any] = None,
                                      context: Dict[str, Any] = None) -> str:
        """
        Generate a response based on action type.
        
        Args:
            action_type: Type of action
            success: Whether the action was successful
            action_data: Additional data for the action
            context: Game context
            
        Returns:
            Generated response text
        """
        action_data = action_data or {}
        
        # Look up template from config if available
        if hasattr(self.config, 'get_template_for_action'):
            template = self.config.get_template_for_action(
                action_type, 
                "success" if success else "failure"
            )
            if template:
                return self._process_template(template, action_data, None, context)
        
        # Use hardcoded templates for common actions
        if action_type == "DESCRIBE_SURROUNDINGS":
            return self._generate_surroundings_description(action_data, context)
            
        elif action_type == "SOCIAL_INTERACTION":
            return self._generate_social_interaction(action_data, context)
            
        elif action_type == "PROCESS_GENERAL_INTENT":
            # For general intents, the action data should contain a response
            return action_data.get("response", "I'm not sure how to respond to that.")
            
        elif action_type == "ACKNOWLEDGE_INPUT":
            if success:
                return "I acknowledge your input."
            else:
                return "I'm not sure how to respond to that. Try something else or check 'help' for available commands."
                
        elif action_type == "SHOW_HELP":
            return self._generate_help_text()
        
        # Fallback for unknown action types
        return f"You {action_type.lower().replace('_', ' ')}."
    
    def _generate_surroundings_description(self,
                                      action_data: Dict[str, Any],
                                      context: Dict[str, Any]) -> str:
        """Generate a description of the surroundings."""
        location_name = context.get("current_location", "the area")
        location_context = context.get("location_context", {})
        dominant_aura = location_context.get("dominant_aura", "unremarkable")
        features = location_context.get("notable_features", [])
        npcs = context.get("present_npcs", [])
        npcs_data = context.get("npcs", {})
        
        # Base description
        description = f"You look around {location_name}. "
        
        # Add atmosphere
        description += f"The area {self._get_random_verb(['appears', 'seems', 'looks'])} {dominant_aura}. "
        
        # Add features if available
        if features:
            description += "You notice " + self._join_with_and([
                f"a {feature}" if not feature.startswith("the ") else feature 
                for feature in features
            ]) + ". "
        
        # Add NPCs if present
        if npcs:
            npc_descriptions = []
            for npc_id in npcs:
                npc_data = npcs_data.get(npc_id, {})
                npc_name = npc_data.get("name", npc_id)
                npc_desc = f"{npc_name} the {npc_data.get('occupation', 'person')}"
                npc_descriptions.append(npc_desc)
            
            description += "You can see " + self._join_with_and(npc_descriptions) + " here."
        
        return description
    
    def _generate_social_interaction(self,
                                action_data: Dict[str, Any],
                                context: Dict[str, Any]) -> str:
        """Generate a response for social interaction."""
        npc_data = action_data.get("npc_data", {})
        npc_name = npc_data.get("name", "the person")
        disposition = npc_data.get("disposition", "neutral")
        
        # Get player reputation with this NPC if available
        player_reputation = context.get("player_reputation", {})
        reputation_with_npc = player_reputation.get(action_data.get("npc_id", ""), disposition)
        
        # Base response
        response = f"You speak with {npc_name}. "
        
        # Add reaction based on disposition and reputation
        if reputation_with_npc in ["friendly", "respected"]:
            response += f"{npc_name} smiles warmly and speaks with you in a friendly manner."
        elif reputation_with_npc in ["neutral", "indifferent"]:
            response += f"{npc_name} responds politely, if somewhat reserved."
        else:
            response += f"{npc_name} seems {disposition} toward you and keeps the conversation brief."
        
        return response
    
    def _generate_help_text(self) -> str:
        """Generate help text with available commands."""
        help_text = "Available Commands:\n\n"
        
        help_text += "- look: Examine your surroundings\n"
        help_text += "- examine [object]: Look at a specific object\n"
        help_text += "- take [item]: Pick up an item\n"
        help_text += "- drop [item]: Drop an item from your inventory\n"
        help_text += "- inventory: Check what you're carrying\n"
        help_text += "- go [direction]: Move in a direction\n"
        help_text += "- talk to [character]: Speak with an NPC\n"
        help_text += "- ask [character] about [topic]: Ask an NPC about something\n"
        
        help_text += "\nYou can also just type what you want to do naturally, and I'll try to understand."
        
        return help_text
    
    def _get_error_message(self, error_type: str) -> str:
        """Get an appropriate error message."""
        if hasattr(self.config, 'ERROR_MESSAGES'):
            return self.config.ERROR_MESSAGES.get(
                error_type, "I encountered an issue with that command."
            )
        
        # Default error messages
        error_messages = {
            "parsing_failed": "I don't understand that command. Try something like 'look', 'take [item]', or 'go [direction]'.",
            "disambiguation_failed": "I couldn't resolve which object you meant. Please try being more specific.",
            "action_failed": "I couldn't complete that action right now.",
            "no_suggestions": "I'm not sure what you want to do. Try 'help' for available commands."
        }
        
        return error_messages.get(error_type, "I encountered an issue with that command.")
    
    def _add_descriptive_elements(self, text: str, context: Dict[str, Any]) -> str:
        """Add descriptive elements to the text based on context."""
        # Replace some placeholders with dynamic content
        if "{RANDOM_FEATURE}" in text and context.get("location_context"):
            features = context.get("location_context", {}).get("notable_features", [])
            if features:
                text = text.replace("{RANDOM_FEATURE}", random.choice(features))
        
        # Add time-of-day flavor
        if "{TIME_OF_DAY}" in text:
            time_of_day = context.get("time_of_day", "day")
            text = text.replace("{TIME_OF_DAY}", time_of_day)
        
        return text
    
    def _get_random_verb(self, options: List[str]) -> str:
        """Get a random verb from options for variety."""
        return random.choice(options)
    
    def _join_with_and(self, items: List[str]) -> str:
        """Join a list of items with commas and 'and'."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        
        return ", ".join(items[:-1]) + f", and {items[-1]}"
    
    def _track_response_type(self, action_type: str) -> None:
        """Track response type for stats."""
        if action_type not in self.response_type_counts:
            self.response_type_counts[action_type] = 0
        
        self.response_type_counts[action_type] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about response generation."""
        return {
            'total_responses': self.response_count,
            'response_types': self.response_type_counts,
            'template_usage': self.template_usage
        }