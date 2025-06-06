"""
Parser Engine - Core text parsing capabilities for the AI GM system

This module provides the main parsing engine that converts player input text
into structured command objects for the AI GM to process.

PHASE 1 COMPLETE: Removed LangChain dependencies and implemented spaCy+rules approach
PHASE 2 COMPLETE: Integrated IntentRouter for enhanced intent detection
PHASE 3 COMPLETE: Integrated ActionExecutor for game system actions
PHASE 4 COMPLETE: Integrated PromptBuilder for context-aware prompts
PHASE 5 COMPLETE: Integrated LLMRoleplayer for direct API calls
PHASE 6 COMPLETE: Final integration and comprehensive modular system

The refactor successfully established a clean, modular architecture that replaces
LangChain agent-based approach with direct game system integration.
"""

import re
import logging
import random
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import os
import json
import time

import spacy
from spacy.pipeline import EntityRuler

# Import shared types to avoid circular imports
from .types import ParsedCommand, GameContext, ParseResult

# Import VocabularyManager for Phase 2 integration
from .vocabulary_manager import vocabulary_manager

# Import IntentRouter (already implemented)
from .intent_router import IntentRouter, PrimaryIntent, SubIntent

# Import ActionExecutor (Phase 3 - COMPLETE)
from .action_executor import ActionExecutor, ActionResult

# Import PromptBuilder (Phase 4 - COMPLETE)
from .prompt_builder import PromptBuilder, PromptContext

# Import LLMRoleplayer (Phase 5 - COMPLETE)
from .llm_roleplayer import LLMRoleplayer, ResponseMode, RoleplayingContext, create_development_roleplayer

# RAG Integration imports (keeping for future Phase 4)
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

logger = logging.getLogger("text_parser")


# Phase 4: GameSystemsManager for accessing real game systems
class GameSystemsManager:
    """
    Provides game systems access for the parser engine.
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
            # Initialize with default session and player
            self._integration_manager = SystemIntegrationManager(
                session_id="default_session",
                player_id="default_player"
            )
            
            self.logger.info("Game systems initialized successfully")
            
        except ImportError as e:
            self.logger.warning(f"Game systems not available: {e}")
            self._integration_manager = None
        except Exception as e:
            self.logger.warning(f"Game systems initialization failed: {e}")
            self._integration_manager = None
    
    def process_through_integration(self, command: str) -> Dict[str, Any]:
        """Process command through system integration."""
        if self._integration_manager:
            try:
                return self._integration_manager.process_command("default_player", command)
            except Exception as e:
                self.logger.error(f"Integration processing error: {e}")
                return {"success": False, "response_text": "System error occurred", "metadata": {}}
        else:
            return {"success": False, "response_text": f"Processing: {command}", "metadata": {}}

# Global instance
_game_systems = GameSystemsManager()


class ActionType(Enum):
    """Categories of player actions for classification."""
    MOVEMENT = auto()
    OBSERVATION = auto()
    INVENTORY = auto()
    INTERACTION = auto()
    COMMUNICATION = auto()
    COMBAT = auto()
    MAGIC = auto()
    META = auto()


class ParserEngine:
    """
    Main engine for parsing player input text into structured commands.
    
    PHASE 6 COMPLETE: Comprehensive modular system with all phases integrated:
    - Phase 1: spaCy + rules approach (replacing LangChain agents)
    - Phase 2: IntentRouter integration for enhanced intent detection
    - Phase 3: ActionExecutor integration for game system actions
    - Phase 4: PromptBuilder integration for context-aware prompts
    - Phase 5: LLMRoleplayer integration for direct API calls
    - Phase 6: Complete end-to-end integration and testing
    """
    
    def __init__(self):
        """Initialize the parser engine with spaCy and rule-based components."""
        self.logger = logging.getLogger("text_parser.engine")
        
        # Initialize spaCy for advanced NLP
        self._init_spacy()
        
        # Initialize rule-based pattern matching
        self._init_patterns()
        
        # Initialize action mappings
        self.action_mappings = self._init_action_mappings()
        
        # Phase 2: Initialize IntentRouter (COMPLETE)
        self.intent_router = IntentRouter()
        
        # Phase 3: Initialize ActionExecutor (COMPLETE)
        self.action_executor = ActionExecutor()
        
        # Phase 4: Initialize PromptBuilder (COMPLETE)
        self.prompt_builder = PromptBuilder()
        
        # Phase 5: Initialize LLMRoleplayer (COMPLETE)
        self.llm_roleplayer = create_development_roleplayer()
        
        # Initialize RAG for context-aware parsing
        self._init_rag_system()
        
        # Initialize GameSystemsManager for system integration
        self.game_systems = GameSystemsManager()
        
        self.logger.info("ParserEngine initialized with complete modular system (Phases 1-6 COMPLETE)")
        self.logger.info("Features: spaCy+rules, IntentRouter, ActionExecutor, PromptBuilder, LLMRoleplayer")
    
    def _init_spacy(self):
        """Initialize spaCy with custom entity ruler for game-specific entities."""
        try:
            # Load English model
            self.nlp = spacy.load("en_core_web_sm")
            # Add custom entity ruler for game entities
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            # Define game-specific entity patterns
            patterns = [
                {"label": "DIRECTION", "pattern": [{"LOWER": {"IN": ["north", "south", "east", "west", "up", "down", "northeast", "northwest", "southeast", "southwest"]}}]},
                {"label": "ITEM", "pattern": [{"LOWER": {"IN": ["sword", "shield", "potion", "scroll", "key", "ring", "armor", "helmet", "bow", "arrow"]}}]},
                {"label": "NPC", "pattern": [{"LOWER": {"IN": ["wizard", "merchant", "guard", "blacksmith", "innkeeper", "priest"]}}]},
                {"label": "CONTAINER", "pattern": [{"LOWER": {"IN": ["chest", "box", "barrel", "sack", "bag", "drawer", "cabinet"]}}]},
                {"label": "MONSTER", "pattern": [{"LOWER": {"IN": ["dragon", "goblin", "orc", "skeleton", "spider", "wolf", "bear"]}}]},
            ]
            ruler.add_patterns(patterns)
            self.logger.info("spaCy initialized with custom entity ruler")
        except Exception as e:
            self.logger.error(f"Failed to initialize spaCy: {e}")
            self.nlp = None
    
    def _init_patterns(self):
        """Initialize rule-based pattern matching for actions."""
        self.action_patterns = {
            "go": [
                r'\b(go|move|walk|travel|head)\s+(north|south|east|west|up|down|to)\b',
                r'\b(enter|exit|leave)\b',
            ],
            "look": [
                r'\b(look|examine|inspect|observe|check)\b',
                r'\b(describe|what.*look)\b',
            ],
            "take": [
                r'\b(take|get|grab|pick up|collect)\b',
                r'\b(loot|gather)\b',
            ],
            "drop": [
                r'\b(drop|discard|leave|put down)\b',
            ],
            "use": [
                r'\b(use|activate|operate|pull|push|turn)\b',
            ],
            "talk": [
                r'\b(talk|speak|say|ask|tell)\b.*\b(to|with)\b',
                r'\b(greet|hello)\b',
            ],
            "attack": [
                r'\b(attack|fight|hit|strike|battle)\b',
                r'\b(kill|slay|destroy)\b',
            ],
            "cast": [
                r'\b(cast|spell|magic|enchant)\b',
                r'\b(heal|fireball|lightning)\b',
            ],
            "search": [
                r'\b(search|find|look for)\b',
            ],
            "inventory": [
                r'\b(inventory|items|equipment|gear)\b',
                r'\b(i|inv)\b$',
            ],
            "equip": [
                r'\b(equip|wear|wield|put on)\b',
            ],
            "unequip": [
                r'\b(unequip|remove|take off)\b',
            ],
            "unlock": [
                r'\b(unlock|open|pick)\b.*\b(lock|door|chest)\b',
            ],
        }
    
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
            "search": ActionType.OBSERVATION,
            "unlock": ActionType.INTERACTION,
            "unequip": ActionType.INTERACTION,
            "equip": ActionType.INTERACTION,
            "cast": ActionType.MAGIC,
        }
    
    def _init_rag_system(self):
        """Initialize RAG system for context-aware parsing."""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.chroma_client = chromadb.Client()
            
            # Create collection for parsing context
            self.context_collection = self.chroma_client.create_collection("parsing_context")
            
            self.logger.info("RAG system initialized")
        except Exception as e:
            self.logger.warning(f"RAG system initialization failed: {e}")
            self.embedding_model = None
            self.context_collection = None
    
    def parse(self, input_text: str, context: Dict[str, Any] = None) -> ParsedCommand:
        """
        Phase 1 COMPLETE: Parse input text using spaCy + rules approach.
        
        This replaces the previous LangChain agent-based approach with a more 
        modular spaCy + rule-based system.
        """
        if not input_text or not input_text.strip():
            return ParsedCommand(action="unknown", raw_text=input_text, confidence=0.0)
        
        normalized_input = input_text.strip().lower()
        context = context or {}
        
        try:
            # Phase 1: Enhanced spaCy processing with linguistic features
            spacy_result = self._process_with_spacy(normalized_input)
            
            # Phase 1: Rule-based pattern matching
            pattern_result = self._match_patterns(normalized_input)
            
            # Phase 1: Extract entities and modifiers
            entities = self._extract_entities(normalized_input, spacy_result)
            modifiers = self._extract_pattern_modifiers(normalized_input, pattern_result)
            
            # Phase 1: Map pattern to action
            action = self._map_pattern_to_action(pattern_result, spacy_result)
            
            # Phase 1: Calculate confidence based on spaCy analysis and pattern matching
            confidence = self._calculate_spacy_confidence(spacy_result, pattern_result, action)
            
            # Phase 1: Extract target from entities and spaCy analysis
            target = self._extract_target(entities, spacy_result, normalized_input)
            
            # Phase 2: Route through IntentRouter for enhanced intent detection
            command = ParsedCommand(
                action=action,
                target=target,
                modifiers=modifiers,
                context=context,
                confidence=confidence,
                raw_text=input_text
            )
            
            enhanced_command = self._route_and_enhance_command(command)
            
            self.logger.info(f"Parsed '{input_text}' -> action: {enhanced_command.action}, target: {enhanced_command.target}, confidence: {enhanced_command.confidence:.2f}")
            
            return enhanced_command
            
        except Exception as e:
            self.logger.error(f"Parsing error for '{input_text}': {e}")
            return ParsedCommand(
                action="unknown",
                target=None,
                confidence=0.1,
                raw_text=input_text,
                context={"error": str(e)}
            )
    
    def _process_with_spacy(self, text: str) -> Dict[str, Any]:
        """Process text with spaCy for linguistic analysis."""
        if not self.nlp:
            return {"entities": [], "tokens": [], "dependencies": []}
        
        try:
            doc = self.nlp(text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
            
            # Extract tokens with POS and dependencies
            tokens = []
            for token in doc:
                tokens.append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "dep": token.dep_,
                    "head": token.head.text
                })
            
            # Extract dependency relationships
            dependencies = []
            for token in doc:
                if token.dep_ != "ROOT":
                    dependencies.append({
                        "child": token.text,
                        "relation": token.dep_,
                        "head": token.head.text
                    })
            
            return {
                "entities": entities,
                "tokens": tokens,
                "dependencies": dependencies,
                "doc": doc
            }
            
        except Exception as e:
            self.logger.error(f"spaCy processing error: {e}")
            return {"entities": [], "tokens": [], "dependencies": []}
    
    def _match_patterns(self, text: str) -> Dict[str, Any]:
        """Match text against rule-based patterns."""
        matched_actions = []
        
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matched_actions.append({
                        "action": action,
                        "pattern": pattern,
                        "confidence": 0.8  # Base confidence for pattern matches
                    })
        
        # Return best match or unknown
        if matched_actions:
            # Sort by confidence and return the best match
            best_match = max(matched_actions, key=lambda x: x["confidence"])
            return best_match
        else:
            return {"action": "unknown", "pattern": None, "confidence": 0.1}
    
    def _map_pattern_to_action(self, pattern_result: Dict[str, Any], spacy_result: Dict[str, Any]) -> str:
        """Map pattern matching results to actions."""
        if pattern_result.get("action") != "unknown":
            return pattern_result["action"]
        
        # Fallback to spaCy-based action detection
        tokens = spacy_result.get("tokens", [])
        for token in tokens:
            if token["pos"] == "VERB":
                lemma = token["lemma"].lower()
                if lemma in self.action_mappings:
                    return lemma
        
        return "unknown"
    
    def _extract_pattern_modifiers(self, text: str, pattern_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract modifiers based on pattern analysis."""
        modifiers = {}
        
        # Extract direction modifiers for movement
        direction_pattern = r'\b(north|south|east|west|up|down|northeast|northwest|southeast|southwest)\b'
        direction_match = re.search(direction_pattern, text, re.IGNORECASE)
        if direction_match:
            modifiers["direction"] = direction_match.group(1).lower()
        
        # Extract preposition modifiers (in, on, with, etc.)
        prep_pattern = r'\b(in|on|with|using|from|to|at)\s+(\w+)'
        prep_matches = re.findall(prep_pattern, text, re.IGNORECASE)
        if prep_matches:
            for prep, obj in prep_matches:
                modifiers[f"prep_{prep}"] = obj
        
        return modifiers
    
    def _calculate_spacy_confidence(self, spacy_result: Dict[str, Any], pattern_result: Dict[str, Any], action: str) -> float:
        """Calculate confidence based on spaCy analysis and pattern matching."""
        base_confidence = pattern_result.get("confidence", 0.1)
        
        # Boost confidence if spaCy found relevant entities
        entities = spacy_result.get("entities", [])
        entity_boost = 0
        
        for entity in entities:
            if entity["label"] in ["DIRECTION", "ITEM", "NPC", "CONTAINER", "MONSTER"]:
                entity_boost += 0.1
        
        # Boost confidence if we found a clear verb
        tokens = spacy_result.get("tokens", [])
        verb_boost = 0
        for token in tokens:
            if token["pos"] == "VERB" and token["lemma"].lower() in self.action_mappings:
                verb_boost = 0.2
                break
        
        final_confidence = min(1.0, base_confidence + entity_boost + verb_boost)
        return final_confidence
    
    def _extract_entities(self, text: str, spacy_result: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract entities from spaCy analysis."""
        entities = {"items": [], "npcs": [], "directions": [], "containers": [], "monsters": []}
        
        spacy_entities = spacy_result.get("entities", [])
        for entity in spacy_entities:
            label = entity["label"]
            if label == "ITEM":
                entities["items"].append(entity["text"])
            elif label == "NPC":
                entities["npcs"].append(entity["text"])
            elif label == "DIRECTION":
                entities["directions"].append(entity["text"])
            elif label == "CONTAINER":
                entities["containers"].append(entity["text"])
            elif label == "MONSTER":
                entities["monsters"].append(entity["text"])
        
        return entities
    
    def _extract_target(self, entities: Dict[str, List[str]], spacy_result: Dict[str, Any], text: str) -> Optional[str]:
        """Extract the target of the action from entities and text analysis."""
        # Check entities first
        all_entity_values = []
        for entity_list in entities.values():
            all_entity_values.extend(entity_list)
        
        if all_entity_values:
            return all_entity_values[0]  # Return first entity found
        
        # Fallback to spaCy object detection
        tokens = spacy_result.get("tokens", [])
        for token in tokens:
            if token["dep"] in ["dobj", "pobj", "obj"]:  # Direct object, object of preposition
                return token["text"]
        
        # Last resort: extract nouns
        for token in tokens:
            if token["pos"] == "NOUN":
                return token["text"]
        
        return None
    
    def _route_and_enhance_command(self, command: ParsedCommand) -> ParsedCommand:
        """
        Phase 2 ENHANCED: Route command through IntentRouter for advanced enhancement.
        
        This method now fully leverages the IntentRouter's capabilities to:
        - Improve action classification based on intent
        - Enhance target detection using intent metadata
        - Add rich context information for downstream processing
        - Handle ambiguous commands with disambiguation requests
        """
        try:
            # Route through IntentRouter with current game context
            game_context = command.context.get("game_state", {})
            intent_result = self.intent_router.route_intent(command, game_context)
            
            # Phase 2: Enhance action based on intent classification
            enhanced_action = self._enhance_action_from_intent(command.action, intent_result)
            if enhanced_action != command.action:
                self.logger.debug(f"Action enhanced: '{command.action}' -> '{enhanced_action}'")
                command.action = enhanced_action
            
            # Phase 2: Enhance target detection using intent metadata
            enhanced_target = self._enhance_target_from_intent(command.target, intent_result)
            if enhanced_target != command.target:
                self.logger.debug(f"Target enhanced: '{command.target}' -> '{enhanced_target}'")
                command.target = enhanced_target
            
            # Phase 2: Update confidence using intent confidence
            original_confidence = command.confidence
            command.confidence = self._calculate_combined_confidence(
                original_confidence, intent_result.confidence
            )
            
            # Phase 2: Add comprehensive intent information to context
            command.context.update({
                "primary_intent": intent_result.primary_intent.value,
                "sub_intent": intent_result.sub_intent.value,
                "intent_confidence": intent_result.confidence,
                "intent_reasoning": intent_result.reasoning,
                "intent_metadata": intent_result.metadata,
                "enhancement_applied": True
            })
            
            # Phase 2: Handle disambiguation requests
            if intent_result.sub_intent.value == "request_disambiguation":
                command.context["requires_disambiguation"] = True
                command.context["disambiguation_reason"] = intent_result.reasoning
            
            # Phase 2: Add action type for downstream processing
            action_type = self._get_action_type_from_intent(intent_result)
            if action_type:
                command.context["action_type"] = action_type.value
            
            self.logger.debug(f"Command enhanced via IntentRouter: {intent_result.primary_intent.value}/{intent_result.sub_intent.value} (confidence: {command.confidence:.2f})")
            
            return command
            
        except Exception as e:
            self.logger.error(f"IntentRouter enhancement error: {e}")
            command.context["intent_error"] = str(e)
            return command
    
    def _enhance_action_from_intent(self, original_action: str, intent_result) -> str:
        """Enhance action classification based on intent routing results."""
        # If original action was ambiguous or unknown, try to infer from intent
        if not original_action or original_action in ["unknown", "unclear"]:
            # Map primary intents to representative actions
            intent_to_action = {
                "movement": "go",
                "observation": "look",
                "interaction": "use",
                "communication": "talk",
                "combat": "attack",
                "inventory": "inventory",
                "magic": "cast",
                "meta": "help"
            }
            inferred_action = intent_to_action.get(intent_result.primary_intent.value)
            if inferred_action:
                return inferred_action
        
        # Refine action based on sub-intent for better specificity
        sub_intent_refinements = {
            "move_direction": "go",
            "move_location": "travel",
            "look_around": "look",
            "examine_target": "examine",
            "search_area": "search",
            "use_item": "use",
            "use_item_on_target": "use",
            "talk_to_npc": "talk",
            "open_container": "open",
            "attack_target": "attack",
            "defend_self": "defend",
            "retreat_from_combat": "retreat",
            "view_inventory": "inventory",
            "take_item": "take",
            "drop_item": "drop",
            "equip_item": "equip",
            "unequip_item": "unequip",
            "cast_spell": "cast",
            "enchant_item": "enchant",
            "request_help": "help",
            "check_status": "status"
        }
        
        refined_action = sub_intent_refinements.get(intent_result.sub_intent.value)
        if refined_action and (not original_action or len(refined_action) > len(original_action)):
            return refined_action
        
        return original_action
    
    def _enhance_target_from_intent(self, original_target: str, intent_result) -> str:
        """Enhance target detection using intent metadata and requirements."""
        metadata = intent_result.metadata
        
        # Handle cases where target is missing but required
        if not original_target and metadata:
            if metadata.get("requires_npc_target"):
                # Look for NPC entities in the original text or context
                entities = metadata.get("original_context", {}).get("entities", [])
                for entity in entities:
                    if entity.get("label") == "NPC":
                        return entity.get("text")
            
            elif metadata.get("requires_two_objects"):
                # For "use X on Y" type commands
                modifiers = metadata.get("modifiers", {})
                if "on_target" in modifiers:
                    return modifiers["on_target"]
        
        # Enhance target specificity based on sub-intent
        if original_target:
            sub_intent = intent_result.sub_intent.value
            
            # Add context clues for directional movement
            if sub_intent == "move_direction":
                # Ensure target is recognized as a direction
                directions = ["north", "south", "east", "west", "up", "down", 
                             "northeast", "northwest", "southeast", "southwest"]
                for direction in directions:
                    if direction in original_target.lower():
                        return direction
            
            # Enhance inventory-related targets
            elif sub_intent in ["take_item", "drop_item", "equip_item", "unequip_item"]:
                # Target should be treated as an item
                return original_target  # Could be enhanced with item validation
        
        return original_target
    
    def _calculate_combined_confidence(self, parser_confidence: float, intent_confidence: float) -> float:
        """Calculate combined confidence from parser and intent router."""
        # Use weighted average with slight preference for intent confidence
        # since it has more context
        combined = (parser_confidence * 0.4) + (intent_confidence * 0.6)
        return round(min(combined, 1.0), 2)
    
    def _get_action_type_from_intent(self, intent_result) -> Optional[ActionType]:
        """Map intent result to ActionType enum."""
        intent_to_action_type = {
            "movement": ActionType.MOVEMENT,
            "observation": ActionType.OBSERVATION,
            "interaction": ActionType.INTERACTION,
            "communication": ActionType.COMMUNICATION,
            "combat": ActionType.COMBAT,
            "inventory": ActionType.INVENTORY,
            "magic": ActionType.MAGIC,
            "meta": ActionType.META
        }
        return intent_to_action_type.get(intent_result.primary_intent.value)

    # ============================================================================
    # PHASE 6: COMPREHENSIVE END-TO-END PROCESSING METHODS
    # ============================================================================
    
    def process_player_input(self, 
                           input_text: str, 
                           game_context: Dict[str, Any] = None,
                           use_llm: bool = True,
                           use_action_executor: bool = True) -> Dict[str, Any]:
        """
        PHASE 6: Complete end-to-end processing of player input.
        
        This is the main entry point that orchestrates all phases:
        1. Parse input with spaCy+rules (Phase 1)
        2. Route through IntentRouter (Phase 2)
        3. Execute actions via ActionExecutor (Phase 3)
        4. Build context-aware prompts (Phase 4)
        5. Generate LLM responses (Phase 5)
        6. Return comprehensive results (Phase 6)
        
        Args:
            input_text: Raw player input text
            game_context: Current game state and context
            use_llm: Whether to use LLM for response generation
            use_action_executor: Whether to execute actions
            
        Returns:
            Comprehensive result dictionary with all processing data
        """
        start_time = time.time()
        game_context = game_context or {}
        
        try:
            self.logger.info(f"Processing input: '{input_text}'")
            
            # PHASE 1 & 2: Parse and route intent
            parsed_command = self.parse(input_text, {"game_state": game_context})
            
            # PHASE 3: Execute action if enabled
            action_result = None
            if use_action_executor and parsed_command.action != "unknown":
                action_result = self.action_executor.execute_action(
                    parsed_command, game_context
                )
                self.logger.debug(f"Action executed: {action_result.success}")
            
            # PHASE 4: Build context for LLM prompt
            prompt_context = PromptContext(
                player_input=input_text,
                parsed_command=parsed_command,
                game_context=game_context,
                action_result=action_result
            )
            
            # PHASE 5: Generate LLM response if enabled
            llm_response = None
            if use_llm:
                # Create roleplaying context
                roleplay_context = self._create_roleplay_context(game_context, action_result)
                
                # Get intent result for mode determination
                intent_result = self._extract_intent_result(parsed_command)
                
                # Generate response
                llm_response = self.llm_roleplayer.generate_roleplay_response(
                    input_text, game_context, roleplay_context, intent_result, action_result
                )
                self.logger.debug(f"LLM response generated: {llm_response.success}")
            
            # PHASE 6: Compile comprehensive results
            processing_time = time.time() - start_time
            
            result = {
                # Core parsing results
                "parsed_command": {
                    "action": parsed_command.action,
                    "target": parsed_command.target,
                    "modifiers": parsed_command.modifiers,
                    "confidence": parsed_command.confidence,
                    "raw_text": parsed_command.raw_text
                },
                
                # Intent routing results
                "intent_analysis": parsed_command.context.get("intent_metadata", {}),
                "primary_intent": parsed_command.context.get("primary_intent"),
                "sub_intent": parsed_command.context.get("sub_intent"),
                
                # Action execution results
                "action_executed": action_result is not None,
                "action_result": action_result.to_dict() if action_result else None,
                
                # LLM response
                "llm_response": llm_response.to_dict() if llm_response else None,
                
                # System metadata
                "processing_time": processing_time,
                "system_version": "Phase 6 Complete",
                "features_used": {
                    "spacy_nlp": True,
                    "rule_patterns": True,
                    "intent_router": True,
                    "action_executor": use_action_executor,
                    "prompt_builder": True,
                    "llm_roleplayer": use_llm
                },
                
                # Response text (primary output)
                "response_text": self._generate_response_text(
                    llm_response, action_result, parsed_command
                ),
                
                # Status indicators
                "success": True,
                "requires_disambiguation": parsed_command.context.get("requires_disambiguation", False),
                "error": None
            }
            
            self.logger.info(f"Processing complete in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Processing failed: {e}")
            
            return {
                "parsed_command": {"action": "unknown", "confidence": 0.0},
                "action_executed": False,
                "action_result": None,
                "llm_response": None,
                "processing_time": processing_time,
                "response_text": f"I'm sorry, I couldn't understand that command. Please try rephrasing.",
                "success": False,
                "error": str(e)
            }
    
    async def process_player_input_async(self, 
                                       input_text: str, 
                                       game_context: Dict[str, Any] = None,
                                       use_llm: bool = True,
                                       use_action_executor: bool = True) -> Dict[str, Any]:
        """
        PHASE 6: Async version of complete end-to-end processing.
        
        Same as process_player_input but uses async LLM calls for better performance.
        """
        start_time = time.time()
        game_context = game_context or {}
        
        try:
            self.logger.info(f"Processing input (async): '{input_text}'")
            
            # PHASE 1 & 2: Parse and route intent
            parsed_command = self.parse(input_text, {"game_state": game_context})
            
            # PHASE 3: Execute action if enabled
            action_result = None
            if use_action_executor and parsed_command.action != "unknown":
                action_result = self.action_executor.execute_action(
                    parsed_command, game_context
                )
            
            # PHASE 5: Generate LLM response if enabled (async)
            llm_response = None
            if use_llm:
                roleplay_context = self._create_roleplay_context(game_context, action_result)
                intent_result = self._extract_intent_result(parsed_command)
                
                llm_response = await self.llm_roleplayer.generate_response_async(
                    self._build_comprehensive_prompt(input_text, game_context, parsed_command, action_result),
                    self._determine_response_mode(intent_result, action_result, game_context),
                    roleplay_context
                )
            
            # PHASE 6: Compile results
            processing_time = time.time() - start_time
            
            result = {
                "parsed_command": {
                    "action": parsed_command.action,
                    "target": parsed_command.target,
                    "modifiers": parsed_command.modifiers,
                    "confidence": parsed_command.confidence,
                    "raw_text": parsed_command.raw_text
                },
                "intent_analysis": parsed_command.context.get("intent_metadata", {}),
                "action_executed": action_result is not None,
                "action_result": action_result.to_dict() if action_result else None,
                "llm_response": llm_response.to_dict() if llm_response else None,
                "processing_time": processing_time,
                "response_text": self._generate_response_text(
                    llm_response, action_result, parsed_command
                ),
                "success": True,
                "error": None
            }
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Async processing failed: {e}")
            
            return {
                "parsed_command": {"action": "unknown", "confidence": 0.0},
                "processing_time": processing_time,
                "response_text": f"I'm sorry, I encountered an error processing that command.",
                "success": False,
                "error": str(e)
            }
    
    def handle_parsing_failure(self, 
                             input_text: str, 
                             error_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        PHASE 6: Handle parsing failures with LLM fallback.
        
        When regular parsing fails, use the LLM to provide helpful responses
        and suggestions for alternative phrasings.
        """
        try:
            self.logger.info(f"Handling parsing failure for: '{input_text}'")
            
            # Generate fallback response using LLM
            fallback_response = self.llm_roleplayer.generate_fallback_response(
                input_text, error_context or {}, []
            )
            
            return {
                "parsed_command": {"action": "unknown", "confidence": 0.0},
                "action_executed": False,
                "action_result": None,
                "llm_response": fallback_response.to_dict(),
                "response_text": fallback_response.response_text,
                "success": False,
                "fallback_used": True,
                "error": "Parsing failed, fallback response generated"
            }
            
        except Exception as e:
            self.logger.error(f"Fallback handling failed: {e}")
            return {
                "response_text": "I'm sorry, I couldn't understand that command. Please try rephrasing.",
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # PHASE 6: HELPER METHODS FOR INTEGRATION
    # ============================================================================
    
    def _create_roleplay_context(self, 
                               game_context: Dict[str, Any], 
                               action_result: Optional[ActionResult]) -> RoleplayingContext:
        """Create roleplaying context from game state and action results."""
        return RoleplayingContext(
            character_name=game_context.get("player_name", "Player"),
            scene_description=game_context.get("location_description", ""),
            world_state=game_context,
            emotional_state=game_context.get("player_mood", "neutral"),
            narrative_tone=game_context.get("narrative_tone", "balanced")
        )
    
    def _extract_intent_result(self, parsed_command: ParsedCommand):
        """Extract intent result from parsed command context."""
        # Create a minimal IntentResult from context
        class MockIntentResult:
            def __init__(self, primary_intent, sub_intent, confidence):
                self.primary_intent = self._get_intent_enum(primary_intent)
                self.sub_intent = self._get_sub_intent_enum(sub_intent)
                self.confidence = confidence
                
            def _get_intent_enum(self, intent_str):
                try:
                    return PrimaryIntent(intent_str)
                except:
                    return PrimaryIntent.UNKNOWN
                    
            def _get_sub_intent_enum(self, sub_intent_str):
                try:
                    return SubIntent(sub_intent_str)
                except:
                    return SubIntent.UNKNOWN
        
        primary = parsed_command.context.get("primary_intent", "unknown")
        sub = parsed_command.context.get("sub_intent", "unknown")
        confidence = parsed_command.context.get("intent_confidence", 0.5)
        
        return MockIntentResult(primary, sub, confidence)
    
    def _determine_response_mode(self, 
                               intent_result, 
                               action_result: Optional[ActionResult], 
                               game_context: Dict[str, Any]) -> ResponseMode:
        """Determine appropriate response mode for LLM generation."""
        if action_result and action_result.action_category:
            category = action_result.action_category
            if category == "combat":
                return ResponseMode.COMBAT
            elif category == "communication":
                return ResponseMode.DIALOGUE
            elif category in ["movement", "observation"]:
                return ResponseMode.EXPLORATION
        
        # Fallback to narrative
        return ResponseMode.NARRATIVE
    
    def _build_comprehensive_prompt(self,
                                  input_text: str,
                                  game_context: Dict[str, Any],
                                  parsed_command: ParsedCommand,
                                  action_result: Optional[ActionResult]) -> str:
        """Build a comprehensive prompt using the PromptBuilder."""
        context = PromptContext(
            player_input=input_text,
            parsed_command=parsed_command,
            game_context=game_context,
            action_result=action_result
        )
        
        return self.prompt_builder.build_narrative_prompt(context)
    
    def _generate_response_text(self,
                              llm_response: Optional[Any],
                              action_result: Optional[ActionResult],
                              parsed_command: ParsedCommand) -> str:
        """Generate the final response text from all processing results."""
        # Priority: LLM response > Action result > Default message
        
        if llm_response and llm_response.success:
            return llm_response.response_text
        
        if action_result and action_result.result_text:
            return action_result.result_text
        
        # Fallback based on action
        action = parsed_command.action
        if action == "unknown":
            return "I'm not sure what you want to do. Could you try rephrasing that?"
        else:
            return f"You {action}."
    
    # ============================================================================
    # PHASE 6: SYSTEM STATUS AND DIAGNOSTICS
    # ============================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and statistics."""
        return {
            "parser_engine": {
                "spacy_loaded": self.nlp is not None,
                "patterns_loaded": len(self.action_patterns),
                "action_mappings": len(self.action_mappings)
            },
            "intent_router": {
                "available": self.intent_router is not None,
                "primary_intents": len(PrimaryIntent),
                "sub_intents": len(SubIntent)
            },
            "action_executor": {
                "available": self.action_executor is not None,
                "stats": self.action_executor.get_stats() if self.action_executor else {}
            },
            "prompt_builder": {
                "available": self.prompt_builder is not None,
                "templates_loaded": len(self.prompt_builder.templates) if self.prompt_builder else 0
            },
            "llm_roleplayer": {
                "available": self.llm_roleplayer is not None,
                "stats": self.llm_roleplayer.get_stats() if self.llm_roleplayer else {}
            },
            "system": {
                "phase": "6 - Complete",
                "features": [
                    "spaCy NLP",
                    "Rule-based patterns", 
                    "Intent routing",
                    "Action execution",
                    "Prompt building",
                    "LLM integration"
                ]
            }
        }
    
    def run_diagnostic(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostic."""
        diagnostic = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Test spaCy
        if not self.nlp:
            diagnostic["issues"].append("spaCy not loaded")
            diagnostic["recommendations"].append("Install spaCy English model: python -m spacy download en_core_web_sm")
        
        # Test LLM API key
        if not self.llm_roleplayer.api_key:
            diagnostic["issues"].append("No LLM API key configured")
            diagnostic["recommendations"].append("Set OPENROUTER_API_KEY environment variable")
        
        # Test basic parsing
        try:
            test_result = self.parse("look around")
            if test_result.confidence < 0.5:
                diagnostic["issues"].append("Low parsing confidence on test input")
        except Exception as e:
            diagnostic["issues"].append(f"Parsing test failed: {e}")
        
        if diagnostic["issues"]:
            diagnostic["system_status"] = "degraded"
        
        return diagnostic
    
    async def close(self):
        """Clean up all resources."""
        if self.llm_roleplayer:
            await self.llm_roleplayer.close()
        self.logger.info("ParserEngine closed")
