"""
Decision Logic System for AI GM Brain.

This module implements the decision tree for determining appropriate actions
based on player input and context.
"""

from enum import Enum, auto
from typing import Dict, Any, List, Optional
import logging
import asyncio


class DecisionPriority(Enum):
    """Priority levels for different decision types."""
    CRITICAL = auto()              # Safety critical decisions
    COMBAT = auto()                # Combat related decisions
    DIRECT_COMMAND = auto()        # Direct player commands
    NARRATIVE_BRANCH = auto()      # Story branching points  
    DOMAIN_ACTION = auto()         # Domain-specific actions
    GENERAL_INTERPRETATION = auto() # General conversational responses
    FALLBACK = auto()              # When no clear decision path exists


class DecisionResult:
    """Result from decision tree evaluation."""
    
    def __init__(self, 
                priority: DecisionPriority,
                action_type: str,
                success: bool = True,
                action_data: Dict[str, Any] = None,
                response_template: str = None,
                template_vars: Dict[str, Any] = None,
                channels: List[str] = None):
        """
        Initialize decision result.
        
        Args:
            priority: Decision priority level
            action_type: Type of action to take
            success: Whether the decision was successful
            action_data: Additional data for the action
            response_template: Template for generating a response
            template_vars: Variables to use in the template
            channels: Delivery channels for the response
        """
        self.priority = priority
        self.action_type = action_type
        self.success = success
        self.action_data = action_data or {}
        self.response_template = response_template
        self.template_vars = template_vars or {}
        self.channels = channels or ["NARRATIVE"]


class AIGMDecisionLogic:
    """Decision logic system for AI GM Brain."""
    
    def __init__(self, config=None):
        """
        Initialize the decision logic system.
        
        Args:
            config: Configuration object or dictionary
        """
        self.logger = logging.getLogger("AIGMDecisionLogic")
        self.config = config
        
        # Stats tracking
        self.decision_count = 0
        self.decision_type_counts = {}
        self.success_rate = 1.0  # Start optimistic!
    
    async def evaluate_decision_tree(self,
                                  player_input: str,
                                  parsed_command: Dict[str, Any] = None,
                                  llm_output: Dict[str, Any] = None,
                                  game_context: Dict[str, Any] = None) -> DecisionResult:
        """
        Evaluate the decision tree to determine appropriate action.
        
        Args:
            player_input: Raw player input
            parsed_command: Command parsed by parser if available
            llm_output: LLM interpretation if available
            game_context: Current game context
            
        Returns:
            Decision result object
        """
        self.decision_count += 1
        game_context = game_context or {}
        
        # Track the start of the decision process
        self.logger.info(f"Evaluating decision tree for input: {player_input}")
        
        # Check for critical decisions first (safety, system commands)
        critical_decision = await self._check_critical_decisions(player_input)
        if critical_decision:
            self._track_decision_type(critical_decision.action_type)
            return critical_decision
            
        # Check if we're in combat mode
        in_combat = game_context.get('in_combat', False)
        if in_combat:
            combat_decision = await self._handle_combat_input(
                player_input, parsed_command, llm_output, game_context
            )
            if combat_decision:
                self._track_decision_type(combat_decision.action_type)
                return combat_decision
        
        # Check if this is a direct parseable command
        if parsed_command and parsed_command.get('success', False):
            command_decision = await self._handle_parsed_command(
                parsed_command, game_context
            )
            if command_decision:
                self._track_decision_type(command_decision.action_type)
                return command_decision
        
        # Check for narrative branch opportunities
        narrative_decision = await self._check_narrative_branches(
            player_input, llm_output, game_context
        )
        if narrative_decision:
            self._track_decision_type(narrative_decision.action_type)
            return narrative_decision
        
        # Check for domain-specific actions (social, exploration, etc)
        domain_decision = await self._check_domain_actions(
            player_input, llm_output, game_context
        )
        if domain_decision:
            self._track_decision_type(domain_decision.action_type)
            return domain_decision
        
        # If we have LLM output, use that for general interpretation
        if llm_output:
            llm_decision = await self._handle_llm_response(llm_output, game_context)
            self._track_decision_type(llm_decision.action_type)
            return llm_decision
        
        # Fallback - we couldn't determine a clear action
        fallback_decision = self._get_fallback_decision(player_input)
        self._track_decision_type(fallback_decision.action_type)
        return fallback_decision
    
    async def _check_critical_decisions(self, player_input: str) -> Optional[DecisionResult]:
        """Check for critical decisions like safety issues or system commands."""
        input_lower = player_input.lower()
        
        # Check for help command
        if input_lower == "help" or input_lower == "commands":
            return DecisionResult(
                priority=DecisionPriority.CRITICAL,
                action_type="SHOW_HELP",
                response_template="Here are the commands you can use: look, examine [object], " 
                                 "take [item], go [direction], talk to [character], and more."
            )
            
        # Check for quit/exit
        if input_lower in ["quit", "exit", "bye"]:
            return DecisionResult(
                priority=DecisionPriority.CRITICAL,
                action_type="ACKNOWLEDGE_EXIT",
                response_template="Thank you for playing! Your progress has been saved."
            )
            
        # No critical decision needed
        return None
    
    async def _handle_combat_input(self, 
                               player_input: str,
                               parsed_command: Dict[str, Any] = None,
                               llm_output: Dict[str, Any] = None,
                               game_context: Dict[str, Any] = None) -> Optional[DecisionResult]:
        """Handle input in combat mode."""
        # In a real implementation, would analyze the input for combat actions
        # For this test version, we'll return a simple combat action
        return DecisionResult(
            priority=DecisionPriority.COMBAT,
            action_type="PROCESS_COMBAT_ACTION",
            action_data={"combat_round": game_context.get("combat_round", 1)},
            response_template="You prepare to take action in combat."
        )
    
    async def _handle_parsed_command(self, 
                                 parsed_command: Dict[str, Any],
                                 game_context: Dict[str, Any] = None) -> Optional[DecisionResult]:
        """Handle a successfully parsed command."""
        action = parsed_command.get("action", "").lower()
        
        if action == "look":
            return DecisionResult(
                priority=DecisionPriority.DIRECT_COMMAND,
                action_type="DESCRIBE_SURROUNDINGS",
                action_data=parsed_command,
                response_template="You look around, taking in your surroundings."
            )
            
        elif action == "take":
            return DecisionResult(
                priority=DecisionPriority.DIRECT_COMMAND,
                action_type="TAKE_OBJECT",
                action_data=parsed_command,
                response_template="You attempt to take something."
            )
            
        elif action == "go":
            return DecisionResult(
                priority=DecisionPriority.DIRECT_COMMAND,
                action_type="MOVE_DIRECTION",
                action_data=parsed_command,
                response_template="You move in a direction."
            )
        
        # Default for other parsed commands
        return DecisionResult(
            priority=DecisionPriority.DIRECT_COMMAND,
            action_type="EXECUTE_COMMAND",
            action_data=parsed_command,
            response_template=f"You {action}."
        )
    
    async def _check_narrative_branches(self,
                                     player_input: str,
                                     llm_output: Dict[str, Any] = None,
                                     game_context: Dict[str, Any] = None) -> Optional[DecisionResult]:
        """Check for narrative branch opportunities."""
        # In a real implementation, would check for narrative branch triggers
        # based on the input and context
        
        # Check if we have branch opportunities in context
        branch_opportunities = game_context.get("branch_opportunities", {})
        
        # Look for keywords related to branch opportunities
        if branch_opportunities:
            input_lower = player_input.lower()
            
            for branch_name, branch_data in branch_opportunities.items():
                hooks = branch_data.get("hooks", [])
                
                # Check if any hook keywords are in the input
                for hook in hooks:
                    if hook.lower() in input_lower:
                        return DecisionResult(
                            priority=DecisionPriority.NARRATIVE_BRANCH,
                            action_type="INITIATE_NARRATIVE_BRANCH",
                            action_data={"branch_name": branch_name, "branch_data": branch_data},
                            response_template=f"You express interest in {hook}."
                        )
        
        # No narrative branch triggered
        return None
    
    async def _check_domain_actions(self,
                                player_input: str,
                                llm_output: Dict[str, Any] = None,
                                game_context: Dict[str, Any] = None) -> Optional[DecisionResult]:
        """Check for domain-specific actions."""
        # Check for social domain actions (talking to NPCs)
        input_lower = player_input.lower()
        
        # Check for conversation with NPCs
        present_npcs = game_context.get("present_npcs", [])
        npcs_data = game_context.get("npcs", {})
        
        for npc_id in present_npcs:
            npc_data = npcs_data.get(npc_id, {})
            npc_name = npc_data.get("name", npc_id)
            
            # Check if player is trying to talk to this NPC
            if npc_name.lower() in input_lower or npc_id.lower() in input_lower:
                if "talk" in input_lower or "ask" in input_lower or "speak" in input_lower:
                    return DecisionResult(
                        priority=DecisionPriority.DOMAIN_ACTION,
                        action_type="SOCIAL_INTERACTION",
                        action_data={"npc_id": npc_id, "npc_data": npc_data},
                        response_template=f"You speak with {npc_name}."
                    )
        
        # No domain-specific action found
        return None
    
    async def _handle_llm_response(self,
                               llm_output: Dict[str, Any],
                               game_context: Dict[str, Any] = None) -> DecisionResult:
        """Handle general LLM interpretation."""
        # In a real implementation, would extract intent and response from LLM output
        # For this test version, we'll create a general interpretation decision
        
        response_text = llm_output.get("response", "")
        
        return DecisionResult(
            priority=DecisionPriority.GENERAL_INTERPRETATION,
            action_type="PROCESS_GENERAL_INTENT",
            action_data=llm_output,
            response_template=response_text
        )
    
    def _get_fallback_decision(self, player_input: str) -> DecisionResult:
        """Get fallback decision when no clear path is determined."""
        return DecisionResult(
            priority=DecisionPriority.FALLBACK,
            action_type="ACKNOWLEDGE_INPUT",
            success=False,
            response_template="I'm not sure how to respond to that. Try a different approach or check 'help' for available commands."
        )
    
    def _track_decision_type(self, action_type: str) -> None:
        """Track the type of decision made for statistics."""
        if action_type not in self.decision_type_counts:
            self.decision_type_counts[action_type] = 0
        
        self.decision_type_counts[action_type] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about decision processing."""
        return {
            'total_decisions': self.decision_count,
            'decision_types': self.decision_type_counts,
            'success_rate': self.success_rate
        }