#!/usr/bin/env python3
"""
Enhanced FantasyLLM Mock for Improved Phase 3 Testing

This enhancement to the FantasyLLM provides more sophisticated and realistic
responses for testing the LangChain agent integration without requiring
real API calls. It includes better pattern matching, action determination,
and tool selection simulation.
"""

from typing import Optional, List, Dict, Any
import re
import random
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

class EnhancedFantasyLLM(LLM):
    """
    Enhanced mock LLM for fantasy text parsing with improved tool selection
    and more realistic responses for Phase 3 testing.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_usage_patterns = self._init_tool_patterns()
        self.entity_database = self._init_entity_database()
        self.response_templates = self._init_response_templates()
    
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
            "cast": "MagicTool", "magic": "MagicTool", "spell": "MagicTool"
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
                    if re.search(rf'\\b{re.escape(entity)}\\b', text):
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


# Test the enhanced LLM
if __name__ == "__main__":
    llm = EnhancedFantasyLLM()
    
    test_prompts = [
        "I want to move to the enchanted forest",
        "Please help me examine the ancient sword",
        "Let me talk to the wizard about magic spells",
        "I need to attack the dragon with my weapon",
        "Help me cast a fireball spell",
        "Can I take the magical potion from the table?"
    ]
    
    print("Testing Enhanced FantasyLLM:")
    print("=" * 50)
    
    for prompt in test_prompts:
        print(f"\\nPrompt: {prompt}")
        print(f"Tool Selection: {llm._select_appropriate_tool(prompt)}")
        print(f"Intent: {llm._classify_intent_enhanced(prompt)}")
        print(f"Entities: {llm._extract_entities_enhanced(prompt)}")
