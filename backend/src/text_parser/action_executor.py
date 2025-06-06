"""
Action Executor - Phase 3 of the modular text parser system

This module executes game actions based on intent routing results,
replacing LangChain BaseTool functionality with standalone functions.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass

from .intent_router import IntentResult, PrimaryIntent, SubIntent


@dataclass
class ActionResult:
    """Result of action execution."""
    success: bool
    message: str
    game_state_changes: Dict[str, Any]
    metadata: Dict[str, Any]
    
    @classmethod
    def success_result(cls, message: str, game_state_changes: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        """Create a successful action result."""
        return cls(
            success=True,
            message=message,
            game_state_changes=game_state_changes or {},
            metadata=metadata or {}
        )
    
    @classmethod
    def failure_result(cls, message: str, error_type: str = "execution_failed", metadata: Dict[str, Any] = None):
        """Create a failed action result."""
        return cls(
            success=False,
            message=message,
            game_state_changes={},
            metadata={"error": error_type, **(metadata or {})}
        )


class ActionExecutor:
    """
    Phase 3 IMPLEMENTED: Executes game actions based on intent routing results, 
    replacing LangChain BaseTool functionality with standalone functions.
    
    This class integrates with existing game systems:
    - GameSystemsManager for core game actions
    - InventorySystem for item management
    - MagicSystem for spell casting
    - CombatSystem for battles
    """
    
    def __init__(self, game_systems_manager=None):
        """Initialize the action executor with game systems integration."""
        self.logger = logging.getLogger("text_parser.action_executor")
        self.game_systems_manager = game_systems_manager
        self._init_action_mappings()
        self._init_game_systems()
        self.logger.info("ActionExecutor initialized")
    
    def _init_action_mappings(self):
        """Initialize mappings from sub-intents to execution functions."""
        self.action_mappings = {
            # Movement actions
            SubIntent.S_MOVE_DIRECTION: self._execute_movement,
            SubIntent.S_MOVE_LOCATION: self._execute_movement,
            
            # Observation actions
            SubIntent.S_LOOK_AROUND: self._execute_observation,
            SubIntent.S_EXAMINE_TARGET: self._execute_observation,
            SubIntent.S_SEARCH_AREA: self._execute_observation,
            
            # Interaction actions
            SubIntent.S_INTERACT_ITEM_USE: self._execute_interaction,
            SubIntent.S_INTERACT_ITEM_USE_ON_TARGET: self._execute_interaction,
            SubIntent.S_INTERACT_NPC_TALK: self._execute_communication,
            SubIntent.S_INTERACT_CONTAINER_OPEN: self._execute_interaction,
            
            # Combat actions
            SubIntent.S_COMBAT_ATTACK: self._execute_combat,
            SubIntent.S_COMBAT_DEFEND: self._execute_combat,
            SubIntent.S_COMBAT_RETREAT: self._execute_combat,
            
            # Inventory actions
            SubIntent.S_INVENTORY_VIEW: self._execute_inventory,
            SubIntent.S_INVENTORY_TAKE: self._execute_inventory,
            SubIntent.S_INVENTORY_DROP: self._execute_inventory,
            SubIntent.S_INVENTORY_EQUIP: self._execute_inventory,
            SubIntent.S_INVENTORY_UNEQUIP: self._execute_inventory,
            
            # Magic actions
            SubIntent.S_MAGIC_CAST_SPELL: self._execute_magic,
            SubIntent.S_MAGIC_ENCHANT: self._execute_magic,
            
            # Meta actions
            SubIntent.S_META_HELP: self._execute_meta,
            SubIntent.S_META_STATUS: self._execute_meta,
        }
    
    def _init_game_systems(self):
        """Initialize connections to game systems."""
        self.inventory_system = None
        self.magic_system = None
        self.combat_system = None
        
        try:
            # Try to import and initialize systems if available
            if self.game_systems_manager:
                # Game systems are available through SystemIntegrationManager
                integration_manager = getattr(self.game_systems_manager, '_integration_manager', None)
                if integration_manager:
                    self.inventory_system = getattr(integration_manager, 'inventory_system', None)
                    self.magic_system = getattr(integration_manager, 'magic_system', None)
                    self.combat_system = getattr(integration_manager, 'combat_system', None)
                    
            self.logger.info("Game systems integration initialized")
            
        except Exception as e:
            self.logger.warning(f"Game systems not fully available: {e}")
    
    def execute_action(self, intent_result: IntentResult, 
                      game_context: Dict[str, Any] = None) -> ActionResult:
        """
        Execute an action based on intent routing result.
        
        Args:
            intent_result: Result from intent routing
            game_context: Current game context
            
        Returns:
            ActionResult with execution outcome
        """
        self.logger.debug(f"Executing action for sub-intent: {intent_result.sub_intent.value}")
        
        # Get the appropriate execution function
        executor_func = self.action_mappings.get(intent_result.sub_intent)
        
        if not executor_func:
            return ActionResult.failure_result(
                f"No executor found for sub-intent: {intent_result.sub_intent.value}",
                "missing_executor"
            )
        
        try:
            return executor_func(intent_result, game_context)
        except Exception as e:
            self.logger.error(f"Error executing action: {e}")
            return ActionResult.failure_result(
                f"Error executing action: {str(e)}",
                "execution_failed",
                {"exception": str(e)}
            )
    
    # Phase 3: Execution functions for different action categories
    # These replace the LangChain BaseTool subclasses with actual game system integration
    
    def _execute_movement(self, intent_result: IntentResult, 
                         game_context: Dict[str, Any]) -> ActionResult:
        """Execute movement actions (replaces MoveTool)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        
        if not target:
            return ActionResult.failure_result("No movement target specified", "missing_target")
        
        # For direction-based movement
        if intent_result.sub_intent == SubIntent.S_MOVE_DIRECTION:
            if self.game_systems_manager:
                try:
                    # Process through game systems
                    command = f"go {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You head {target}."),
                            {"new_location": target, "movement_type": "direction"},
                            {"direction": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot go {target}."),
                            "movement_blocked"
                        )
                        
                except Exception as e:
                    self.logger.error(f"Movement execution error: {e}")
                    return ActionResult.failure_result(f"Movement failed: {str(e)}", "system_error")
            
            # Fallback for basic movement
            return ActionResult.success_result(
                f"You head {target}.",
                {"movement_direction": target},
                {"sub_intent": intent_result.sub_intent.value}
            )
        
        # For location-based movement  
        else:
            if self.game_systems_manager:
                try:
                    command = f"travel to {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You travel to {target}."),
                            {"new_location": target, "movement_type": "location"},
                            {"destination": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot travel to {target}."),
                            "travel_blocked"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Travel failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You travel to {target}.",
                {"movement_destination": target},
                {"sub_intent": intent_result.sub_intent.value}
            )
    
    def _execute_observation(self, intent_result: IntentResult, 
                           game_context: Dict[str, Any]) -> ActionResult:
        """Execute observation actions (replaces LookTool, ExamineTool)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        
        if intent_result.sub_intent == SubIntent.S_LOOK_AROUND:
            # General look command
            if self.game_systems_manager:
                try:
                    result = self.game_systems_manager.process_through_integration("look")
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", "You look around the area."),
                            {"observed_area": True},
                            {"observation_type": "area", "command_processed": True}
                        )
                        
                except Exception as e:
                    self.logger.error(f"Look execution error: {e}")
            
            return ActionResult.success_result(
                "You look around the area, taking in your surroundings.",
                {"observed_area": True},
                {"observation_type": "area"}
            )
            
        elif intent_result.sub_intent == SubIntent.S_EXAMINE_TARGET:
            # Examine specific target
            if not target:
                return ActionResult.failure_result("No examination target specified", "missing_target")
            
            if self.game_systems_manager:
                try:
                    command = f"examine {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You examine the {target} carefully."),
                            {"examined_target": target},
                            {"observation_type": "examine", "target": target, "command_processed": True}
                        )
                        
                except Exception as e:
                    self.logger.error(f"Examine execution error: {e}")
            
            return ActionResult.success_result(
                f"You examine the {target} carefully, noting its details.",
                {"examined_target": target},
                {"observation_type": "examine", "target": target}
            )
            
        elif intent_result.sub_intent == SubIntent.S_SEARCH_AREA:
            # Search for hidden items or details
            if self.game_systems_manager:
                try:
                    search_target = target if target else "area"
                    command = f"search {search_target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You search the {search_target} thoroughly."),
                            {"searched_target": search_target},
                            {"observation_type": "search", "target": search_target, "command_processed": True}
                        )
                        
                except Exception as e:
                    self.logger.error(f"Search execution error: {e}")
            
            search_target = target if target else "area"
            return ActionResult.success_result(
                f"You search the {search_target} thoroughly, looking for anything of interest.",
                {"searched_target": search_target},
                {"observation_type": "search", "target": search_target}
            )
    
    def _execute_interaction(self, intent_result: IntentResult, 
                           game_context: Dict[str, Any]) -> ActionResult:
        """Execute interaction actions (replaces UseTool, OpenTool, etc.)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        original_action = metadata.get("original_action", "use")
        
        if not target:
            return ActionResult.failure_result("No interaction target specified", "missing_target")
        
        if intent_result.sub_intent == SubIntent.S_INTERACT_ITEM_USE:
            # Use an item
            if self.game_systems_manager:
                try:
                    command = f"use {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You use the {target}."),
                            {"used_item": target},
                            {"interaction_type": "use", "target": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot use the {target}."),
                            "use_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Use action failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You use the {target}.",
                {"used_item": target},
                {"interaction_type": "use", "target": target}
            )
            
        elif intent_result.sub_intent == SubIntent.S_INTERACT_ITEM_USE_ON_TARGET:
            # Use item on another target
            on_target = metadata.get("modifiers", {}).get("on_target")
            if not on_target:
                return ActionResult.failure_result("No target specified for 'use on' action", "missing_on_target")
            
            if self.game_systems_manager:
                try:
                    command = f"use {target} on {on_target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You use the {target} on the {on_target}."),
                            {"used_item": target, "on_target": on_target},
                            {"interaction_type": "use_on", "target": target, "on_target": on_target, "command_processed": True}
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Use on action failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You use the {target} on the {on_target}.",
                {"used_item": target, "on_target": on_target},
                {"interaction_type": "use_on", "target": target, "on_target": on_target}
            )
            
        elif intent_result.sub_intent == SubIntent.S_INTERACT_CONTAINER_OPEN:
            # Open a container
            if self.game_systems_manager:
                try:
                    command = f"open {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You open the {target}."),
                            {"opened_container": target},
                            {"interaction_type": "open", "target": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot open the {target}."),
                            "open_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Open action failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You open the {target}.",
                {"opened_container": target},
                {"interaction_type": "open", "target": target}
            )
    
    def _execute_communication(self, intent_result: IntentResult, 
                             game_context: Dict[str, Any]) -> ActionResult:
        """Execute communication actions (replaces TalkTool)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        topic = metadata.get("topic")
        
        if not target:
            return ActionResult.failure_result("No communication target specified", "missing_target")
        
        if self.game_systems_manager:
            try:
                if topic:
                    command = f"talk to {target} about {topic}"
                else:
                    command = f"talk to {target}"
                    
                result = self.game_systems_manager.process_through_integration(command)
                
                if result.get("success", False):
                    return ActionResult.success_result(
                        result.get("response_text", f"You speak with {target}."),
                        {"talked_to": target, "topic": topic},
                        {"communication_type": "talk", "target": target, "topic": topic, "command_processed": True}
                    )
                else:
                    return ActionResult.failure_result(
                        result.get("response_text", f"You cannot talk to {target}."),
                        "communication_failed"
                    )
                    
            except Exception as e:
                return ActionResult.failure_result(f"Communication failed: {str(e)}", "system_error")
        
        # Fallback communication
        if topic:
            message = f"You speak with {target} about {topic}."
        else:
            message = f"You greet {target} and begin a conversation."
            
        return ActionResult.success_result(
            message,
            {"talked_to": target, "topic": topic},
            {"communication_type": "talk", "target": target, "topic": topic}
        )
    
    def _execute_combat(self, intent_result: IntentResult, 
                       game_context: Dict[str, Any]) -> ActionResult:
        """Execute combat actions (replaces AttackTool, DefendTool)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        
        if intent_result.sub_intent == SubIntent.S_COMBAT_ATTACK:
            if not target:
                return ActionResult.failure_result("No attack target specified", "missing_target")
            
            if self.game_systems_manager:
                try:
                    command = f"attack {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You attack the {target}."),
                            {"attacked_target": target, "combat_initiated": True},
                            {"combat_type": "attack", "target": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot attack the {target}."),
                            "attack_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Attack failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You launch an attack against the {target}!",
                {"attacked_target": target, "combat_initiated": True},
                {"combat_type": "attack", "target": target}
            )
            
        elif intent_result.sub_intent == SubIntent.S_COMBAT_DEFEND:
            if self.game_systems_manager:
                try:
                    result = self.game_systems_manager.process_through_integration("defend")
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", "You take a defensive stance."),
                            {"defensive_stance": True},
                            {"combat_type": "defend", "command_processed": True}
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Defend action failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                "You take a defensive stance, preparing to block incoming attacks.",
                {"defensive_stance": True},
                {"combat_type": "defend"}
            )
            
        elif intent_result.sub_intent == SubIntent.S_COMBAT_RETREAT:
            if self.game_systems_manager:
                try:
                    result = self.game_systems_manager.process_through_integration("retreat")
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", "You attempt to retreat from combat."),
                            {"retreat_attempted": True},
                            {"combat_type": "retreat", "command_processed": True}
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Retreat failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                "You attempt to disengage and retreat from the battle.",
                {"retreat_attempted": True},
                {"combat_type": "retreat"}
            )
    
    def _execute_inventory(self, intent_result: IntentResult, 
                          game_context: Dict[str, Any]) -> ActionResult:
        """Execute inventory actions (replaces TakeTool, DropTool, EquipTool, etc.)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        player_id = game_context.get("player_id", "default_player") if game_context else "default_player"
        
        if intent_result.sub_intent == SubIntent.S_INVENTORY_VIEW:
            # View inventory
            if self.inventory_system:
                try:
                    inventory_display = self.inventory_system.get_player_inventory_display(player_id)
                    
                    if inventory_display:
                        items_text = "\n".join([f"- {item['name']} (x{item['quantity']})" for item in inventory_display])
                        message = f"Your inventory:\n{items_text}"
                    else:
                        message = "Your inventory is empty."
                    
                    return ActionResult.success_result(
                        message,
                        {"inventory_viewed": True, "item_count": len(inventory_display)},
                        {"inventory_type": "view", "command_processed": True}
                    )
                    
                except Exception as e:
                    return ActionResult.failure_result(f"Could not view inventory: {str(e)}", "inventory_error")
            
            # Fallback if no inventory system
            if self.game_systems_manager:
                try:
                    result = self.game_systems_manager.process_through_integration("inventory")
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", "You check your inventory."),
                            {"inventory_viewed": True},
                            {"inventory_type": "view", "command_processed": True}
                        )
                        
                except Exception as e:
                    pass
            
            return ActionResult.success_result(
                "You check your inventory.",
                {"inventory_viewed": True},
                {"inventory_type": "view"}
            )
            
        elif intent_result.sub_intent == SubIntent.S_INVENTORY_TAKE:
            if not target:
                return ActionResult.failure_result("No item specified to take", "missing_target")
            
            if self.inventory_system:
                try:
                    # Try to take item from current location
                    result = self.inventory_system.process_command("take", player_id, target, 1)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("message", f"You take the {target}."),
                            {"took_item": target},
                            {"inventory_type": "take", "item": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("message", f"You cannot take the {target}."),
                            "take_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Take action failed: {str(e)}", "inventory_error")
            
            # Fallback through game systems
            if self.game_systems_manager:
                try:
                    command = f"take {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You take the {target}."),
                            {"took_item": target},
                            {"inventory_type": "take", "item": target, "command_processed": True}
                        )
                        
                except Exception as e:
                    pass
            
            return ActionResult.success_result(
                f"You take the {target}.",
                {"took_item": target},
                {"inventory_type": "take", "item": target}
            )
            
        elif intent_result.sub_intent == SubIntent.S_INVENTORY_DROP:
            if not target:
                return ActionResult.failure_result("No item specified to drop", "missing_target")
            
            if self.inventory_system:
                try:
                    result = self.inventory_system.process_command("drop", player_id, target, 1)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("message", f"You drop the {target}."),
                            {"dropped_item": target},
                            {"inventory_type": "drop", "item": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("message", f"You cannot drop the {target}."),
                            "drop_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Drop action failed: {str(e)}", "inventory_error")
            
            # Fallback
            if self.game_systems_manager:
                try:
                    command = f"drop {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You drop the {target}."),
                            {"dropped_item": target},
                            {"inventory_type": "drop", "item": target, "command_processed": True}
                        )
                        
                except Exception as e:
                    pass
            
            return ActionResult.success_result(
                f"You drop the {target}.",
                {"dropped_item": target},
                {"inventory_type": "drop", "item": target}
            )
            
        # Handle equip/unequip actions similarly
        elif intent_result.sub_intent in [SubIntent.S_INVENTORY_EQUIP, SubIntent.S_INVENTORY_UNEQUIP]:
            if not target:
                action_type = "equip" if intent_result.sub_intent == SubIntent.S_INVENTORY_EQUIP else "unequip"
                return ActionResult.failure_result(f"No item specified to {action_type}", "missing_target")
            
            action_type = "equip" if intent_result.sub_intent == SubIntent.S_INVENTORY_EQUIP else "unequip"
            
            if self.game_systems_manager:
                try:
                    command = f"{action_type} {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You {action_type} the {target}."),
                            {f"{action_type}ped_item": target},
                            {"inventory_type": action_type, "item": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot {action_type} the {target}."),
                            f"{action_type}_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"{action_type.title()} action failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You {action_type} the {target}.",
                {f"{action_type}ped_item": target},
                {"inventory_type": action_type, "item": target}
            )
    
    def _execute_magic(self, intent_result: IntentResult, 
                      game_context: Dict[str, Any]) -> ActionResult:
        """Execute magic actions (replaces CastTool, EnchantTool)."""
        metadata = intent_result.metadata
        target = metadata.get("target")
        spell_name = target  # For magic actions, target is typically the spell name
        player_id = game_context.get("player_id", "default_player") if game_context else "default_player"
        
        if intent_result.sub_intent == SubIntent.S_MAGIC_CAST_SPELL:
            if not spell_name:
                return ActionResult.failure_result("No spell specified to cast", "missing_spell")
            
            if self.magic_system:
                try:
                    # Try to cast spell through magic system
                    # This would need proper integration with the magic system API
                    cast_result = self.magic_system.cast_spell(
                        caster_id=player_id,
                        spell_id=spell_name,
                        target_id=None,  # Could be enhanced to include spell targets
                        location_id=game_context.get("location_id") if game_context else None,
                        current_time=game_context.get("current_time") if game_context else None
                    )
                    
                    if cast_result.get("success", False):
                        return ActionResult.success_result(
                            cast_result.get("message", f"You cast {spell_name}."),
                            {"cast_spell": spell_name, "magic_used": True},
                            {"magic_type": "cast", "spell": spell_name, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            cast_result.get("message", f"You cannot cast {spell_name}."),
                            "cast_failed"
                        )
                        
                except Exception as e:
                    self.logger.error(f"Magic system cast error: {e}")
            
            # Fallback through game systems
            if self.game_systems_manager:
                try:
                    command = f"cast {spell_name}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You cast {spell_name}."),
                            {"cast_spell": spell_name, "magic_used": True},
                            {"magic_type": "cast", "spell": spell_name, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot cast {spell_name}."),
                            "cast_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Spell casting failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You focus your magical energy and cast {spell_name}.",
                {"cast_spell": spell_name, "magic_used": True},
                {"magic_type": "cast", "spell": spell_name}
            )
            
        elif intent_result.sub_intent == SubIntent.S_MAGIC_ENCHANT:
            if not target:
                return ActionResult.failure_result("No item specified to enchant", "missing_target")
            
            if self.game_systems_manager:
                try:
                    command = f"enchant {target}"
                    result = self.game_systems_manager.process_through_integration(command)
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", f"You enchant the {target}."),
                            {"enchanted_item": target, "magic_used": True},
                            {"magic_type": "enchant", "item": target, "command_processed": True}
                        )
                    else:
                        return ActionResult.failure_result(
                            result.get("response_text", f"You cannot enchant the {target}."),
                            "enchant_failed"
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Enchantment failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                f"You weave magical energy into the {target}, imbuing it with enchantment.",
                {"enchanted_item": target, "magic_used": True},
                {"magic_type": "enchant", "item": target}
            )
    
    def _execute_meta(self, intent_result: IntentResult, 
                     game_context: Dict[str, Any]) -> ActionResult:
        """Execute meta actions (replaces HelpTool, StatusTool)."""
        if intent_result.sub_intent == SubIntent.S_META_HELP:
            help_text = """
Available commands:
- Movement: go [direction], travel to [location]
- Observation: look, examine [target], search [area]
- Interaction: use [item], open [container], talk to [npc]
- Combat: attack [target], defend, retreat
- Inventory: inventory, take [item], drop [item], equip [item]
- Magic: cast [spell], enchant [item]
- Meta: help, status
            """.strip()
            
            return ActionResult.success_result(
                help_text,
                {"help_displayed": True},
                {"meta_type": "help"}
            )
            
        elif intent_result.sub_intent == SubIntent.S_META_STATUS:
            if self.game_systems_manager:
                try:
                    result = self.game_systems_manager.process_through_integration("status")
                    
                    if result.get("success", False):
                        return ActionResult.success_result(
                            result.get("response_text", "Status information displayed."),
                            {"status_displayed": True},
                            {"meta_type": "status", "command_processed": True}
                        )
                        
                except Exception as e:
                    return ActionResult.failure_result(f"Status check failed: {str(e)}", "system_error")
            
            return ActionResult.success_result(
                "You check your current status and condition.",
                {"status_displayed": True},
                {"meta_type": "status"}
            )
