"""
AI GM Brain - Decision Logic Integration

This module provides the decision-making capabilities for the AI GM Brain,
allowing it to make intelligent choices about narrative flow and game state.
It includes a core decision tree for processing player input and determining
appropriate game actions and narrative responses.
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta

# Import from core brain
from .ai_gm_brain import AIGMBrain, ProcessingMode


class DecisionType(Enum):
    """Types of decisions the AI GM Brain can make."""
    NARRATIVE_DIRECTION = auto()     # How the story should progress
    NPC_REACTION = auto()            # How NPCs react to player actions
    ENCOUNTER_GENERATION = auto()    # What encounters to generate
    REWARD_GENERATION = auto()       # What rewards to provide
    DIFFICULTY_ADJUSTMENT = auto()   # Adjust difficulty based on player performance


class DecisionResult:
    """Result of a decision-making process."""
    
    def __init__(self, 
                 decision_type: DecisionType,
                 choices: Dict[str, float],
                 selected: str,
                 confidence: float,
                 context: Dict[str, Any]):
        """
        Initialize a decision result.
        
        Args:
            decision_type: Type of decision made
            choices: Dictionary of choices with their weights
            selected: The selected choice
            confidence: Confidence in the decision (0.0-1.0)
            context: Context used to make the decision
        """
        self.decision_type = decision_type
        self.choices = choices
        self.selected = selected
        self.confidence = confidence
        self.context = context
        self.timestamp = datetime.utcnow()


class DecisionTreeHandler:
    """
    Decision Tree for processing player input and determining game actions.
    
    This class implements the core decision tree logic that determines
    how the AI GM responds to player input, based on a hierarchy of
    priorities from LLM-identified opportunities to general conversation.
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the decision tree handler.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"DecisionTree_{ai_gm_brain.game_id}")
        
        # Track processing metrics
        self.decisions_processed = 0
        self.successful_branch_initiations = 0
        self.successful_branch_actions = 0
        self.successful_parsed_commands = 0
        self.general_interpretations = 0
        
        self.logger.info("Decision Tree Handler initialized")
    
    def process_input(self, 
                     parsed_command: Optional[Any], 
                     llm_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process player input through the decision tree to determine the appropriate action.
        
        Args:
            parsed_command: Result from the command parser (if successful)
            llm_output: Output from the LLM interpretation
            
        Returns:
            Processing result with action taken and response details
        """
        self.decisions_processed += 1
        self.logger.info("Processing input through decision tree")
        
        result = {
            "action_taken": None,
            "mechanical_outcome": None,
            "response_basis": None,
            "suggested_response": None,
            "success": False
        }
        
        # Priority 1: LLM Identified Opportunity Alignment
        if self._check_aligned_opportunity(llm_output, result):
            return result
            
        # Priority 2: LLM Identified Branch Action
        if self._check_aligned_branch_action(llm_output, result):
            return result
            
        # Priority 3: Successful ParsedCommand
        if parsed_command and self._check_parsed_command(parsed_command, result):
            return result
            
        # Priority 4: General LLM Interpretation
        self._use_general_llm_interpretation(llm_output, result)
        return result
    
    def _check_aligned_opportunity(self, llm_output: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """
        Check if the LLM identified an aligned narrative opportunity.
        
        Args:
            llm_output: Output from the LLM interpretation
            result: Result dictionary to populate
            
        Returns:
            True if an aligned opportunity was found and processed
        """
        opportunity_id = llm_output.get("aligned_opportunity_id")
        if not opportunity_id:
            return False
            
        self.logger.info(f"LLM identified aligned opportunity: {opportunity_id}")
        
        # In a full implementation, this would call:
        # outcome = NarrativeBranchChoiceHandler.attempt_to_initiate_branch_via_gm(
        #     opportunity_id, self.ai_gm_brain.player_id, self.ai_gm_brain.game_id)
        
        # For now, simulate the outcome
        outcome = {
            "success": True,
            "branch_id": "simulated_branch_" + str(self.decisions_processed),
            "message": "Successfully initiated narrative branch."
        }
        
        if outcome["success"]:
            self.successful_branch_initiations += 1
            result["action_taken"] = "initiate_narrative_branch"
            result["mechanical_outcome"] = outcome
            result["response_basis"] = "aligned_opportunity"
            result["suggested_response"] = llm_output.get("suggested_gm_acknowledgement", 
                                                       "Let's explore this interesting direction...")
            result["success"] = True
            return True
        else:
            # Branch initiation failed, include reason in response
            result["action_taken"] = "failed_branch_initiation"
            result["mechanical_outcome"] = outcome
            result["response_basis"] = "aligned_opportunity_failed"
            
            # Append failure reason to the suggested response
            base_response = llm_output.get("suggested_gm_acknowledgement", "")
            failure_reason = f" {outcome.get('message', 'Something prevents you from proceeding that way.')}"
            result["suggested_response"] = base_response + failure_reason
            
            result["success"] = False
            return True
            
        return False
    
    def _check_aligned_branch_action(self, llm_output: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """
        Check if the LLM identified an aligned branch action.
        
        Args:
            llm_output: Output from the LLM interpretation
            result: Result dictionary to populate
            
        Returns:
            True if an aligned branch action was found and processed
        """
        branch_action = llm_output.get("aligned_branch_action")
        if not branch_action:
            return False
            
        self.logger.info(f"LLM identified aligned branch action: {branch_action}")
        
        # In a full implementation, this would:
        # 1. Verify this action is valid for the current branch/stage
        # 2. Trigger the game logic for this specific branch action
        
        # For now, simulate the outcome
        action_outcome = {
            "success": True,
            "action": branch_action,
            "details": {
                "skill_check": {"result": "success", "roll": 15, "dc": 12},
                "progression": {"advanced": True, "new_stage": "next_stage"}
            },
            "message": "You successfully perform the action."
        }
        
        if action_outcome["success"]:
            self.successful_branch_actions += 1
            result["action_taken"] = f"branch_action_{branch_action}"
            result["mechanical_outcome"] = action_outcome
            result["response_basis"] = "aligned_branch_action"
            result["suggested_response"] = llm_output.get("suggested_gm_acknowledgement", 
                                                       "Your action succeeds...") 
            result["success"] = True
            return True
        else:
            # Action failed, include reason in response
            result["action_taken"] = f"failed_branch_action_{branch_action}"
            result["mechanical_outcome"] = action_outcome
            result["response_basis"] = "aligned_branch_action_failed"
            
            # Append failure reason to the suggested response
            base_response = llm_output.get("suggested_gm_acknowledgement", "")
            failure_reason = f" {action_outcome.get('message', 'Your attempt fails.')}"
            result["suggested_response"] = base_response + failure_reason
            
            result["success"] = False
            return True
        
        return False
    
    def _check_parsed_command(self, parsed_command: Any, result: Dict[str, Any]) -> bool:
        """
        Process a successfully parsed command.
        
        Args:
            parsed_command: Result from the command parser
            result: Result dictionary to populate
            
        Returns:
            True if the parsed command was successfully processed
        """
        if not parsed_command:
            return False
            
        self.logger.info(f"Processing parsed command: {getattr(parsed_command, 'command', 'unknown')}")
        
        # In a full implementation, this would execute the mechanics of the ParsedCommand
        # For now, simulate a successful outcome
        command_outcome = {
            "success": True,
            "command": getattr(parsed_command, "command", "unknown"),
            "message": "Command executed successfully."
        }
        
        self.successful_parsed_commands += 1
        result["action_taken"] = f"parsed_command_{command_outcome['command']}"
        result["mechanical_outcome"] = command_outcome
        result["response_basis"] = "parsed_command"
        result["suggested_response"] = command_outcome.get("message", "You take that action.")
        result["success"] = True
        return True
    
    def _use_general_llm_interpretation(self, llm_output: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Process general LLM interpretation when no specific action is identified.
        
        Args:
            llm_output: Output from the LLM interpretation
            result: Result dictionary to populate
        """
        self.logger.info("Using general LLM interpretation")
        self.general_interpretations += 1
        
        result["action_taken"] = "general_conversation"
        result["mechanical_outcome"] = None
        result["response_basis"] = "llm_interpretation"
        
        # Use the LLM's suggested GM acknowledgement as the basis for the response
        player_intent = llm_output.get("player_intent_summary", "You said something.")
        suggested_response = llm_output.get("suggested_gm_acknowledgement", 
                                          "I understand what you're trying to do.")
        
        result["suggested_response"] = suggested_response
        result["success"] = True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on decision tree processing.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "decisions_processed": self.decisions_processed,
            "successful_branch_initiations": self.successful_branch_initiations,
            "successful_branch_actions": self.successful_branch_actions,
            "successful_parsed_commands": self.successful_parsed_commands,
            "general_interpretations": self.general_interpretations
        }


class DecisionLogic:
    """
    Logic engine for making game-related decisions.
    
    This class provides methods for making various types of decisions
    that influence the game's narrative and mechanics.
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the decision logic engine.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"DecisionLogic_{ai_gm_brain.game_id}")
        
        # Recent decisions history
        self.decisions: List[DecisionResult] = []
        self.max_decisions_history = 50
        
        # Decision strategy configuration
        self.default_confidence = 0.7
        self.randomness_factor = 0.2  # Inject some randomness for unpredictability
        
        # Add the decision tree handler
        self.decision_tree = DecisionTreeHandler(ai_gm_brain)
        
        self.logger.info("Decision Logic initialized")
    
    def make_decision(self, 
                     decision_type: DecisionType,
                     choices: Dict[str, float],
                     context: Dict[str, Any]) -> DecisionResult:
        """
        Make a decision based on context and available choices.
        
        Args:
            decision_type: Type of decision to make
            choices: Dictionary of choices with their baseline weights
            context: Contextual information for the decision
            
        Returns:
            Decision result
        """
        self.logger.debug(f"Making {decision_type.name} decision with {len(choices)} choices")
        
        # Adjust weights based on context
        adjusted_weights = self._adjust_weights(choices, context, decision_type)
        
        # Introduce some randomness for unpredictability
        final_weights = self._add_randomness(adjusted_weights)
        
        # Select the highest weighted choice
        selected = max(final_weights.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on weight difference
        sorted_weights = sorted(final_weights.values(), reverse=True)
        if len(sorted_weights) > 1:
            # Higher difference between top choices = higher confidence
            weight_diff = sorted_weights[0] - sorted_weights[1]
            confidence = min(0.5 + weight_diff, 1.0)
        else:
            confidence = self.default_confidence
        
        # Create and store decision result
        result = DecisionResult(
            decision_type=decision_type,
            choices=final_weights,
            selected=selected,
            confidence=confidence,
            context=context
        )
        
        # Add to history and trim if needed
        self.decisions.append(result)
        if len(self.decisions) > self.max_decisions_history:
            self.decisions = self.decisions[-self.max_decisions_history:]
        
        self.logger.info(
            f"Decision made: {decision_type.name} → {selected} (confidence: {confidence:.2f})"
        )
        
        return result
    
    def make_narrative_direction_decision(self, context: Dict[str, Any]) -> DecisionResult:
        """
        Decide on the narrative direction to take.
        
        Args:
            context: Current game context
            
        Returns:
            Decision about narrative direction
        """
        # Default narrative directions
        directions = {
            "continue_current_thread": 0.4,
            "introduce_new_element": 0.2,
            "escalate_tension": 0.2,
            "provide_resolution": 0.1,
            "surprise_reversal": 0.1
        }
        
        return self.make_decision(
            decision_type=DecisionType.NARRATIVE_DIRECTION,
            choices=directions,
            context=context
        )
    
    def make_npc_reaction_decision(self, 
                                  npc_id: str, 
                                  player_action: str,
                                  context: Dict[str, Any]) -> DecisionResult:
        """
        Decide how an NPC should react to a player action.
        
        Args:
            npc_id: ID of the NPC
            player_action: Description of the player's action
            context: Additional context
            
        Returns:
            Decision about NPC reaction
        """
        # Default NPC reactions
        reactions = {
            "friendly": 0.2,
            "hostile": 0.2,
            "neutral": 0.3,
            "suspicious": 0.2,
            "fearful": 0.1
        }
        
        # Add NPC-specific context
        npc_context = context.copy()
        npc_context.update({
            "npc_id": npc_id,
            "player_action": player_action
        })
        
        return self.make_decision(
            decision_type=DecisionType.NPC_REACTION,
            choices=reactions,
            context=npc_context
        )
    
    def make_encounter_decision(self, location_id: str, context: Dict[str, Any]) -> DecisionResult:
        """
        Decide what type of encounter to generate.
        
        Args:
            location_id: ID of the current location
            context: Additional context
            
        Returns:
            Decision about encounter type
        """
        # Default encounter types
        encounters = {
            "combat": 0.3,
            "social": 0.3,
            "exploration": 0.2,
            "puzzle": 0.1,
            "resource": 0.1
        }
        
        # Add location-specific context
        location_context = context.copy()
        location_context.update({
            "location_id": location_id
        })
        
        return self.make_decision(
            decision_type=DecisionType.ENCOUNTER_GENERATION,
            choices=encounters,
            context=location_context
        )
    
    def make_reward_decision(self, 
                           player_action: str,
                           difficulty: float,
                           context: Dict[str, Any]) -> DecisionResult:
        """
        Decide what rewards to give the player.
        
        Args:
            player_action: Description of the action that earned the reward
            difficulty: Difficulty rating of the action (0.0-1.0)
            context: Additional context
            
        Returns:
            Decision about rewards
        """
        # Default reward types
        rewards = {
            "gold": 0.3,
            "item": 0.3,
            "experience": 0.2,
            "reputation": 0.1,
            "information": 0.1
        }
        
        # Add reward-specific context
        reward_context = context.copy()
        reward_context.update({
            "player_action": player_action,
            "difficulty": difficulty
        })
        
        return self.make_decision(
            decision_type=DecisionType.REWARD_GENERATION,
            choices=rewards,
            context=reward_context
        )
    
    def make_difficulty_adjustment_decision(self, 
                                          player_performance: float,
                                          context: Dict[str, Any]) -> DecisionResult:
        """
        Decide how to adjust difficulty based on player performance.
        
        Args:
            player_performance: Rating of player performance (0.0-1.0)
            context: Additional context
            
        Returns:
            Decision about difficulty adjustment
        """
        # Default difficulty adjustments
        adjustments = {
            "increase": 0.2,
            "decrease": 0.2,
            "maintain": 0.6
        }
        
        # Add performance-specific context
        adjustment_context = context.copy()
        adjustment_context.update({
            "player_performance": player_performance
        })
        
        return self.make_decision(
            decision_type=DecisionType.DIFFICULTY_ADJUSTMENT,
            choices=adjustments,
            context=adjustment_context
        )
    
    def _adjust_weights(self, 
                       choices: Dict[str, float],
                       context: Dict[str, Any],
                       decision_type: DecisionType) -> Dict[str, float]:
        """
        Adjust choice weights based on context.
        
        Args:
            choices: Dictionary of choices with baseline weights
            context: Contextual information
            decision_type: Type of decision being made
            
        Returns:
            Dictionary of choices with adjusted weights
        """
        adjusted = choices.copy()
        
        # Adjust based on decision type and context
        if decision_type == DecisionType.NARRATIVE_DIRECTION:
            # Adjust narrative direction based on pacing
            tension = context.get('tension', 0.5)
            # Increase escalation when tension is low
            if tension < 0.3:
                adjusted['escalate_tension'] = adjusted.get('escalate_tension', 0) + 0.2
                adjusted['introduce_new_element'] = adjusted.get('introduce_new_element', 0) + 0.1
            # Favor resolution when tension is high
            elif tension > 0.7:
                adjusted['provide_resolution'] = adjusted.get('provide_resolution', 0) + 0.2
                
        elif decision_type == DecisionType.NPC_REACTION:
            # Adjust NPC reaction based on disposition
            disposition = context.get('disposition', 0.5)
            # More friendly reactions for higher disposition
            if disposition > 0.7:
                adjusted['friendly'] = adjusted.get('friendly', 0) + 0.3
                adjusted['hostile'] = max(adjusted.get('hostile', 0) - 0.2, 0)
            # More hostile reactions for lower disposition
            elif disposition < 0.3:
                adjusted['hostile'] = adjusted.get('hostile', 0) + 0.3
                adjusted['friendly'] = max(adjusted.get('friendly', 0) - 0.2, 0)
                
        elif decision_type == DecisionType.ENCOUNTER_GENERATION:
            # Adjust encounters based on recent history
            recent_encounters = context.get('recent_encounters', [])
            # Avoid repeating the same encounter type
            if recent_encounters:
                last_encounter = recent_encounters[-1]
                if last_encounter in adjusted:
                    adjusted[last_encounter] = max(adjusted.get(last_encounter, 0) - 0.2, 0)
                
        elif decision_type == DecisionType.REWARD_GENERATION:
            # Scale rewards with difficulty
            difficulty = context.get('difficulty', 0.5)
            if difficulty > 0.7:
                adjusted['item'] = adjusted.get('item', 0) + 0.2
                adjusted['experience'] = adjusted.get('experience', 0) + 0.1
            
        elif decision_type == DecisionType.DIFFICULTY_ADJUSTMENT:
            # Adapt difficulty based on performance
            performance = context.get('player_performance', 0.5)
            # Increase difficulty for high performance
            if performance > 0.7:
                adjusted['increase'] = adjusted.get('increase', 0) + 0.2
                adjusted['decrease'] = max(adjusted.get('decrease', 0) - 0.1, 0)
            # Decrease difficulty for low performance
            elif performance < 0.3:
                adjusted['decrease'] = adjusted.get('decrease', 0) + 0.2
                adjusted['increase'] = max(adjusted.get('increase', 0) - 0.1, 0)
        
        # Normalize weights
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}
    
    def _add_randomness(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Add randomness to weights for unpredictability.
        
        Args:
            weights: Dictionary of choices with weights
            
        Returns:
            Dictionary with randomness added
        """
        result = {}
        for choice, weight in weights.items():
            # Add random factor within configured bounds
            random_factor = (random.random() * 2 - 1) * self.randomness_factor
            # Ensure weight stays positive
            result[choice] = max(0.01, weight + random_factor)
        
        # Renormalize weights
        total = sum(result.values())
        return {k: v / total for k, v in result.items()}
    
    def get_recent_decisions(self, 
                           decision_type: Optional[DecisionType] = None,
                           limit: int = 10) -> List[DecisionResult]:
        """
        Get recent decisions, optionally filtered by type.
        
        Args:
            decision_type: Optional filter for decision type
            limit: Maximum number of decisions to return
            
        Returns:
            List of recent decisions
        """
        if decision_type:
            filtered = [d for d in self.decisions if d.decision_type == decision_type]
            return filtered[-limit:]
        else:
            return self.decisions[-limit:]


# Extension function to add decision logic to AI GM Brain
def extend_ai_gm_brain_with_decision_logic(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with decision-making capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create decision logic
    decision_logic = DecisionLogic(ai_gm_brain)
    
    # Store the decision logic for future reference
    ai_gm_brain.decision_logic = decision_logic
    
    # Add process_decision_tree method to the AI GM Brain
    ai_gm_brain.process_decision_tree = lambda parsed_command, llm_output: decision_logic.decision_tree.process_input(
        parsed_command, llm_output
    )
    
    # Override the existing process_player_input method to use decision tree
    original_process_player_input = ai_gm_brain.process_player_input
    
    def enhanced_process_player_input(player_input: str) -> Dict[str, Any]:
        """Enhanced player input processing using decision tree logic."""
        # First, get the basic response using the original method
        basic_response = original_process_player_input(player_input)
        
        # Extract parsed command and LLM output from the response metadata
        parsed_command = basic_response.get('metadata', {}).get('parsed_command')
        llm_output = basic_response.get('metadata', {}).get('llm_output', {})
        
        # If we have LLM output, use the decision tree to process the input
        if llm_output:
            decision_result = decision_logic.decision_tree.process_input(parsed_command, llm_output)
            
            # Enhance the response with decision tree results
            if decision_result.get('success', False):
                # Use the decision tree's suggested response
                suggested_response = decision_result.get('suggested_response')
                if suggested_response:
                    basic_response['response_text'] = suggested_response
                
                # Add decision information to metadata
                basic_response['metadata']['decision_tree'] = {
                    'action_taken': decision_result.get('action_taken'),
                    'response_basis': decision_result.get('response_basis'),
                    'mechanical_outcome': decision_result.get('mechanical_outcome')
                }
        
        return basic_response
    
    # Replace the original method with the enhanced version
    ai_gm_brain.process_player_input = enhanced_process_player_input