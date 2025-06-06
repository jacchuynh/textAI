"""
Intent Router - Phase 2 of the modular text parser system

This module handles routing parsed commands to specific intents based on
hierarchical intent classification.
"""

from typing import Dict, Any, Optional
from enum import Enum
import logging
from dataclasses import dataclass

# Import the ParsedCommand and GameContext from shared types
from .types import ParsedCommand, GameContext


class PrimaryIntent(Enum):
    """Primary intent categories."""
    P_MOVEMENT = "movement"
    P_OBSERVATION = "observation"
    P_INTERACTION = "interaction"
    P_COMMUNICATION = "communication"
    P_COMBAT = "combat"
    P_INVENTORY = "inventory"
    P_MAGIC = "magic"
    P_META = "meta"
    P_UNKNOWN = "unknown"


class SubIntent(Enum):
    """Specific sub-intents for fine-grained routing."""
    # Movement sub-intents
    S_MOVE_DIRECTION = "move_direction"
    S_MOVE_LOCATION = "move_location"
    
    # Observation sub-intents
    S_LOOK_AROUND = "look_around"
    S_EXAMINE_TARGET = "examine_target"
    S_SEARCH_AREA = "search_area"
    
    # Interaction sub-intents
    S_INTERACT_ITEM_USE = "use_item"
    S_INTERACT_ITEM_USE_ON_TARGET = "use_item_on_target"
    S_INTERACT_NPC_TALK = "talk_to_npc"
    S_INTERACT_CONTAINER_OPEN = "open_container"
    
    # Combat sub-intents
    S_COMBAT_ATTACK = "attack_target"
    S_COMBAT_DEFEND = "defend_self"
    S_COMBAT_RETREAT = "retreat_from_combat"
    
    # Inventory sub-intents
    S_INVENTORY_VIEW = "view_inventory"
    S_INVENTORY_TAKE = "take_item"
    S_INVENTORY_DROP = "drop_item"
    S_INVENTORY_EQUIP = "equip_item"
    S_INVENTORY_UNEQUIP = "unequip_item"
    
    # Magic sub-intents
    S_MAGIC_CAST_SPELL = "cast_spell"
    S_MAGIC_ENCHANT = "enchant_item"
    
    # Meta sub-intents
    S_META_HELP = "request_help"
    S_META_STATUS = "check_status"
    
    # Disambiguation
    S_REQUEST_DISAMBIGUATION = "request_disambiguation"


@dataclass
class IntentResult:
    """Result of intent routing with confidence and metadata."""
    primary_intent: PrimaryIntent
    sub_intent: SubIntent
    confidence: float
    metadata: Dict[str, Any]
    reasoning: str


class IntentRouter:
    """
    Routes ParsedCommand objects to specific sub-intents based on 
    hierarchical classification and game context.
    """
    
    def __init__(self):
        """Initialize the intent router."""
        self.logger = logging.getLogger("text_parser.intent_router")
        self._init_intent_mappings()
        self.logger.info("IntentRouter initialized")
    
    def _init_intent_mappings(self):
        """Initialize mappings from actions to intents."""
        self.action_to_primary = {
            # Movement actions
            "go": PrimaryIntent.P_MOVEMENT,
            "move": PrimaryIntent.P_MOVEMENT,
            "walk": PrimaryIntent.P_MOVEMENT,
            "run": PrimaryIntent.P_MOVEMENT,
            "travel": PrimaryIntent.P_MOVEMENT,
            "head": PrimaryIntent.P_MOVEMENT,
            "enter": PrimaryIntent.P_MOVEMENT,
            "exit": PrimaryIntent.P_MOVEMENT,
            
            # Observation actions
            "look": PrimaryIntent.P_OBSERVATION,
            "examine": PrimaryIntent.P_OBSERVATION,
            "inspect": PrimaryIntent.P_OBSERVATION,
            "observe": PrimaryIntent.P_OBSERVATION,
            "search": PrimaryIntent.P_OBSERVATION,
            
            # Interaction actions
            "use": PrimaryIntent.P_INTERACTION,
            "activate": PrimaryIntent.P_INTERACTION,
            "operate": PrimaryIntent.P_INTERACTION,
            "open": PrimaryIntent.P_INTERACTION,
            "close": PrimaryIntent.P_INTERACTION,
            "unlock": PrimaryIntent.P_INTERACTION,
            
            # Communication actions
            "talk": PrimaryIntent.P_COMMUNICATION,
            "speak": PrimaryIntent.P_COMMUNICATION,
            "ask": PrimaryIntent.P_COMMUNICATION,
            "tell": PrimaryIntent.P_COMMUNICATION,
            "chat": PrimaryIntent.P_COMMUNICATION,
            
            # Combat actions
            "attack": PrimaryIntent.P_COMBAT,
            "fight": PrimaryIntent.P_COMBAT,
            "hit": PrimaryIntent.P_COMBAT,
            "strike": PrimaryIntent.P_COMBAT,
            "defend": PrimaryIntent.P_COMBAT,
            "retreat": PrimaryIntent.P_COMBAT,
            
            # Inventory actions
            "inventory": PrimaryIntent.P_INVENTORY,
            "take": PrimaryIntent.P_INVENTORY,
            "get": PrimaryIntent.P_INVENTORY,
            "grab": PrimaryIntent.P_INVENTORY,
            "drop": PrimaryIntent.P_INVENTORY,
            "equip": PrimaryIntent.P_INVENTORY,
            "unequip": PrimaryIntent.P_INVENTORY,
            "wear": PrimaryIntent.P_INVENTORY,
            "remove": PrimaryIntent.P_INVENTORY,
            
            # Magic actions
            "cast": PrimaryIntent.P_MAGIC,
            "enchant": PrimaryIntent.P_MAGIC,
            "conjure": PrimaryIntent.P_MAGIC,
            "summon": PrimaryIntent.P_MAGIC,
            
            # Meta actions
            "help": PrimaryIntent.P_META,
            "status": PrimaryIntent.P_META,
            "quit": PrimaryIntent.P_META,
        }
    
    def route_intent(self, parsed_command: ParsedCommand, game_context: Dict[str, Any] = None) -> IntentResult:
        """
        Route a ParsedCommand to a specific sub-intent.
        
        Args:
            parsed_command: The parsed command from Phase 1
            game_context: Current game context for disambiguation
            
        Returns:
            IntentResult with primary intent, sub-intent, and metadata
        """
        if not parsed_command or not parsed_command.action:
            return IntentResult(
                primary_intent=PrimaryIntent.P_UNKNOWN,
                sub_intent=SubIntent.S_REQUEST_DISAMBIGUATION,
                confidence=0.1,
                metadata={},
                reasoning="No action identified in command"
            )
        
        # Get primary intent
        primary_intent = self.action_to_primary.get(
            parsed_command.action.lower(), 
            PrimaryIntent.P_UNKNOWN
        )
        
        # Route to specific sub-intent
        sub_intent = self._determine_sub_intent(parsed_command, primary_intent, game_context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(parsed_command, primary_intent, sub_intent)
        
        # Extract metadata
        metadata = self._extract_metadata(parsed_command, sub_intent)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(parsed_command, primary_intent, sub_intent)
        
        result = IntentResult(
            primary_intent=primary_intent,
            sub_intent=sub_intent,
            confidence=confidence,
            metadata=metadata,
            reasoning=reasoning
        )
        
        self.logger.debug(f"Routed '{parsed_command.action}' -> {primary_intent.value}/{sub_intent.value} (confidence: {confidence:.2f})")
        
        return result
    
    def _determine_sub_intent(self, parsed_command: ParsedCommand, primary_intent: PrimaryIntent, game_context: Dict[str, Any]) -> SubIntent:
        """Determine the specific sub-intent based on primary intent and command details."""
        action = parsed_command.action.lower()
        target = parsed_command.target
        modifiers = parsed_command.modifiers or {}
        
        if primary_intent == PrimaryIntent.P_MOVEMENT:
            if target and any(direction in target.lower() for direction in ["north", "south", "east", "west", "up", "down"]):
                return SubIntent.S_MOVE_DIRECTION
            else:
                return SubIntent.S_MOVE_LOCATION
                
        elif primary_intent == PrimaryIntent.P_OBSERVATION:
            if action == "search" or "search" in action:
                return SubIntent.S_SEARCH_AREA
            elif target:
                return SubIntent.S_EXAMINE_TARGET
            else:
                return SubIntent.S_LOOK_AROUND
                
        elif primary_intent == PrimaryIntent.P_INTERACTION:
            if action in ["talk", "speak", "ask", "tell"]:
                return SubIntent.S_INTERACT_NPC_TALK
            elif action == "use":
                if modifiers.get("on_target"):
                    return SubIntent.S_INTERACT_ITEM_USE_ON_TARGET
                else:
                    return SubIntent.S_INTERACT_ITEM_USE
            elif action in ["open", "unlock"]:
                return SubIntent.S_INTERACT_CONTAINER_OPEN
            else:
                return SubIntent.S_INTERACT_ITEM_USE
                
        elif primary_intent == PrimaryIntent.P_COMBAT:
            if action in ["defend", "block"]:
                return SubIntent.S_COMBAT_DEFEND
            elif action in ["retreat", "flee", "run away"]:
                return SubIntent.S_COMBAT_RETREAT
            else:
                return SubIntent.S_COMBAT_ATTACK
                
        elif primary_intent == PrimaryIntent.P_INVENTORY:
            if action == "inventory":
                return SubIntent.S_INVENTORY_VIEW
            elif action in ["take", "get", "grab", "pick"]:
                return SubIntent.S_INVENTORY_TAKE
            elif action in ["drop", "discard", "put down"]:
                return SubIntent.S_INVENTORY_DROP
            elif action in ["equip", "wear", "wield"]:
                return SubIntent.S_INVENTORY_EQUIP
            elif action in ["unequip", "remove", "take off"]:
                return SubIntent.S_INVENTORY_UNEQUIP
            else:
                return SubIntent.S_INVENTORY_VIEW
                
        elif primary_intent == PrimaryIntent.P_MAGIC:
            if action in ["enchant", "imbue"]:
                return SubIntent.S_MAGIC_ENCHANT
            else:
                return SubIntent.S_MAGIC_CAST_SPELL
                
        elif primary_intent == PrimaryIntent.P_META:
            if action == "help":
                return SubIntent.S_META_HELP
            else:
                return SubIntent.S_META_STATUS
        
        # Fallback
        return SubIntent.S_REQUEST_DISAMBIGUATION
    
    def _calculate_confidence(self, parsed_command: ParsedCommand, primary_intent: PrimaryIntent, sub_intent: SubIntent) -> float:
        """Calculate confidence score for the intent routing."""
        base_confidence = parsed_command.confidence if parsed_command.confidence else 0.5
        
        # Boost confidence if we have a clear target
        if parsed_command.target:
            base_confidence = min(base_confidence + 0.2, 1.0)
        
        # Reduce confidence if intent is unknown
        if primary_intent == PrimaryIntent.P_UNKNOWN:
            base_confidence *= 0.3
        
        # Boost confidence for common patterns
        if sub_intent in [SubIntent.S_MOVE_DIRECTION, SubIntent.S_INVENTORY_VIEW, SubIntent.S_LOOK_AROUND]:
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        return round(base_confidence, 2)
    
    def _extract_metadata(self, parsed_command: ParsedCommand, sub_intent: SubIntent) -> Dict[str, Any]:
        """Extract relevant metadata for the sub-intent."""
        metadata = {
            "original_action": parsed_command.action,
            "target": parsed_command.target,
            "modifiers": parsed_command.modifiers or {},
            "original_context": parsed_command.context or {}
        }
        
        # Add sub-intent specific metadata
        if sub_intent == SubIntent.S_INTERACT_ITEM_USE_ON_TARGET:
            metadata["requires_two_objects"] = True
            
        elif sub_intent == SubIntent.S_INTERACT_NPC_TALK:
            metadata["requires_npc_target"] = True
            if parsed_command.modifiers and "about_topic" in parsed_command.modifiers:
                metadata["topic"] = parsed_command.modifiers["about_topic"]
        
        elif sub_intent in [SubIntent.S_INVENTORY_EQUIP, SubIntent.S_INVENTORY_UNEQUIP]:
            metadata["requires_equipment_slot_detection"] = True
        
        return metadata
    
    def _generate_reasoning(self, parsed_command: ParsedCommand, primary_intent: PrimaryIntent, sub_intent: SubIntent) -> str:
        """Generate human-readable reasoning for the intent classification."""
        action = parsed_command.action
        target = parsed_command.target or "unspecified"
        
        if primary_intent == PrimaryIntent.P_UNKNOWN:
            return f"Could not classify action '{action}' into a known intent category"
        
        reasoning_parts = [
            f"Action '{action}' classified as {primary_intent.value}",
            f"Sub-intent determined as {sub_intent.value}",
        ]
        
        if target != "unspecified":
            reasoning_parts.append(f"with target '{target}'")
        
        if parsed_command.modifiers:
            modifier_info = ", ".join([f"{k}={v}" for k, v in parsed_command.modifiers.items()])
            reasoning_parts.append(f"and modifiers: {modifier_info}")
        
        return " ".join(reasoning_parts)
