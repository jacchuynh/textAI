"""
AI Game Master Brain Module

This module implements a simplified AI Game Master that can handle
complex or ambiguous player commands that don't fit cleanly into 
predefined action categories.
"""

from typing import Dict, List, Any, Optional


class AIGMBrain:
    """
    The AI Game Master brain that processes player commands and generates responses.
    
    This is a simplified implementation for demonstration purposes.
    In a real system, this would likely use a language model API.
    """
    def __init__(self):
        # Initialize response templates
        self._init_response_templates()
    
    def _init_response_templates(self):
        """Initialize templates for AI GM responses."""
        self.templates = {
            "greeting": [
                "Welcome, adventurer! How may I assist you in your journey?",
                "Greetings, traveler. What brings you to these lands?",
                "Well met! What quest shall we embark on today?"
            ],
            "unknown_command": [
                "I'm not sure what you're trying to do. Could you try a different approach?",
                "Hmm, I don't quite understand. Can you phrase that differently?",
                "Your intentions are unclear to me. Perhaps try a more direct command?"
            ],
            "location_description": [
                "You find yourself in {location}. The air feels {atmosphere}. {details}",
                "Looking around {location}, you notice {details}. The {atmosphere} surrounds you.",
                "As you survey {location}, you observe {details}. There's a sense of {atmosphere} here."
            ],
            "npc_interaction": [
                "{npc_name} looks at you {expression}. \"{dialogue}\"",
                "{npc_name} {action} as you approach. \"{dialogue}\"",
                "You speak with {npc_name}, who {action}. \"{dialogue}\""
            ],
            "combat_narration": [
                "The {enemy} {enemy_action}. You must react quickly!",
                "As the {enemy} {enemy_action}, you prepare your defenses.",
                "The battle with the {enemy} intensifies as it {enemy_action}!"
            ],
            "discovery": [
                "You've discovered {item}! {description}",
                "What's this? You found {item}. {description}",
                "Your keen eye spots {item}. {description}"
            ],
            "quest_update": [
                "Your quest to {objective} has been updated. {update_details}",
                "New information about your quest to {objective}: {update_details}",
                "The path to {objective} has changed. {update_details}"
            ]
        }
    
    def process_player_input(self, player_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process player input and generate an appropriate response.
        
        Args:
            player_input: The natural language input from the player
            context: Contextual information about the game state
            
        Returns:
            A dictionary containing the AI GM's response and any game state updates
        """
        # Analyze the input to determine intent
        intent = self._determine_intent(player_input)
        
        # Generate a response based on intent and context
        response = self._generate_response(intent, player_input, context)
        
        # Return the response and any game state updates
        return {
            "response": response,
            "intent": intent,
            "state_updates": {}  # Would contain game state updates in a real implementation
        }
    
    def _determine_intent(self, player_input: str) -> str:
        """
        Determine the player's intent from their input.
        
        In a real implementation, this would use NLP techniques or a language model.
        This simplified version just checks for keywords.
        """
        player_input = player_input.lower()
        
        if any(word in player_input for word in ["hello", "hi", "greet", "hey"]):
            return "greeting"
        
        if any(word in player_input for word in ["look", "see", "observe", "examine"]):
            return "observe"
        
        if any(word in player_input for word in ["talk", "speak", "ask", "tell"]):
            return "talk"
        
        if any(word in player_input for word in ["attack", "fight", "kill", "hit"]):
            return "combat"
        
        if any(word in player_input for word in ["quest", "mission", "task"]):
            return "quest"
        
        if any(word in player_input for word in ["go", "move", "travel", "walk"]):
            return "movement"
        
        if any(word in player_input for word in ["use", "equip", "wield", "wear"]):
            return "item_use"
        
        if any(word in player_input for word in ["craft", "make", "create", "build"]):
            return "crafting"
        
        if any(word in player_input for word in ["cast", "spell", "magic"]):
            return "magic"
        
        # Default to unknown
        return "unknown"
    
    def _generate_response(self, intent: str, player_input: str, context: Dict[str, Any]) -> str:
        """
        Generate a response based on the player's intent and game context.
        
        In a real implementation, this would use a language model or template system.
        This simplified version uses basic templates with some context filling.
        """
        import random
        
        # Get player information
        player = context.get("player", {})
        player_name = player.get("name", "Adventurer")
        
        # Get location information
        location_info = context.get("location", {})
        location_name = location_info.get("area", {}).get("name", "this area")
        
        # Get NPC information if relevant
        npcs = context.get("npcs", [])
        npc_name = npcs[0].get("name", "a stranger") if npcs else "a stranger"
        
        # Handle based on intent
        if intent == "greeting":
            return random.choice(self.templates["greeting"])
        
        elif intent == "unknown":
            return random.choice(self.templates["unknown_command"])
        
        elif intent == "observe":
            # Fill in location description template
            location_desc = location_info.get("area", {}).get("description", "an interesting place")
            atmosphere = "mysterious" if "ruins" in location_name.lower() else "peaceful"
            details = "There's much to explore here." if location_desc else "Nothing particularly stands out."
            
            template = random.choice(self.templates["location_description"])
            return template.format(
                location=location_name,
                atmosphere=atmosphere,
                details=details
            )
        
        elif intent == "talk" and npcs:
            # Fill in NPC interaction template
            dialogue = npcs[0].get("dialogue", {}).get("greeting", "Hello there.")
            expression = "curiously" if "elder" in npc_name.lower() else "cautiously"
            action = "nods respectfully" if "elder" in npc_name.lower() else "smiles faintly"
            
            template = random.choice(self.templates["npc_interaction"])
            return template.format(
                npc_name=npc_name,
                expression=expression,
                action=action,
                dialogue=dialogue
            )
        
        # For other intents, return a generic but contextual response
        return f"You try to {intent}, but the specific action isn't clear. Perhaps try a more direct command?"