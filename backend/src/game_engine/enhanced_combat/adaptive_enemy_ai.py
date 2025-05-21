"""
Adaptive enemy AI for enhanced combat.

This module implements AI logic for enemies that adapts to player patterns,
creating more challenging and engaging combat.
"""
import random
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from .combat_system_core import Domain, MoveType, CombatMove, Combatant, Status


class EnemyPersonality:
    """
    Personality traits for an enemy that influence combat behavior.
    
    This allows for more varied and interesting enemy behaviors beyond
    simple stat differences.
    """
    def __init__(self, 
                 aggression: float = 0.5,      # 0.0 to 1.0, how aggressive the enemy is
                 adaptability: float = 0.5,     # How quickly they learn from combat
                 risk_taking: float = 0.5,      # Willingness to use desperate moves
                 calculation: float = 0.5,      # Tendency to plan and use calculated moves
                 specialization: List[Domain] = None,  # Domains they favor
                 preferred_moves: List[MoveType] = None):  # Move types they prefer
        """
        Initialize an enemy personality.
        
        Args:
            aggression: How aggressive the enemy is (0.0 to 1.0)
            adaptability: How quickly they learn from combat (0.0 to 1.0)
            risk_taking: Willingness to use desperate moves (0.0 to 1.0)
            calculation: Tendency to plan and use calculated moves (0.0 to 1.0)
            specialization: Domains they favor
            preferred_moves: Move types they prefer
        """
        self.aggression = aggression
        self.adaptability = adaptability  
        self.risk_taking = risk_taking
        self.calculation = calculation
        self.specialization = specialization or []
        self.preferred_moves = preferred_moves or []
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation for API responses.
        
        Returns:
            Dictionary representation of this personality
        """
        return {
            "aggression": self.aggression,
            "adaptability": self.adaptability,
            "risk_taking": self.risk_taking,
            "calculation": self.calculation,
            "specialization": [domain.value for domain in self.specialization],
            "preferred_moves": [move_type.value for move_type in self.preferred_moves]
        }


class CombatMemento:
    """
    Tracks what happened in previous rounds for AI decision making.
    
    This allows the AI to learn from the player's behavior and adapt
    its strategies accordingly.
    """
    def __init__(self):
        """Initialize a combat memento"""
        self.player_moves_used = []
        self.successful_player_moves = []
        self.successful_enemy_moves = []
        self.player_patterns = {}  # Track patterns in player behavior
        
    def record_round(self, player_move: CombatMove, enemy_move: CombatMove, player_success: bool) -> None:
        """
        Record the results of a combat round.
        
        Args:
            player_move: The move used by the player
            enemy_move: The move used by the enemy
            player_success: Whether the player succeeded
        """
        # Track move types used
        self.player_moves_used.append(player_move.move_type)
        
        # Track successful moves
        if player_success:
            self.successful_player_moves.append(player_move.move_type)
        else:
            self.successful_enemy_moves.append(enemy_move.move_type)
            
        # Update pattern recognition
        self._update_player_patterns()
    
    def _update_player_patterns(self) -> None:
        """Analyze player's moves for patterns"""
        # Only analyze if we have enough history
        if len(self.player_moves_used) < 3:
            return
            
        # Look for sequences of 2 moves
        for i in range(len(self.player_moves_used) - 2):
            pattern = (self.player_moves_used[i], self.player_moves_used[i+1])
            follow_up = self.player_moves_used[i+2]
            
            pattern_key = f"{pattern[0].value}-{pattern[1].value}"
            if pattern_key not in self.player_patterns:
                self.player_patterns[pattern_key] = {}
                
            if follow_up.value not in self.player_patterns[pattern_key]:
                self.player_patterns[pattern_key][follow_up.value] = 0
                
            self.player_patterns[pattern_key][follow_up.value] += 1
    
    def predict_next_move(self) -> Optional[MoveType]:
        """
        Try to predict player's next move based on patterns.
        
        Returns:
            The predicted move type or None if no prediction can be made
        """
        if len(self.player_moves_used) < 2:
            return None
            
        # Get the last two moves
        last_moves = (self.player_moves_used[-2], self.player_moves_used[-1])
        pattern_key = f"{last_moves[0].value}-{last_moves[1].value}"
        
        if pattern_key in self.player_patterns:
            # Find the most common follow-up
            predictions = self.player_patterns[pattern_key]
            if predictions:
                # Get the move type with highest count
                most_common = max(predictions.items(), key=lambda x: x[1])
                for move_type in MoveType:
                    if move_type.value == most_common[0]:
                        return move_type
                        
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation for API responses.
        
        Returns:
            Dictionary representation of this memento
        """
        return {
            "player_moves_used": [move_type.value for move_type in self.player_moves_used],
            "successful_player_moves": [move_type.value for move_type in self.successful_player_moves],
            "successful_enemy_moves": [move_type.value for move_type in self.successful_enemy_moves],
            "predicted_next_move": self.predict_next_move().value if self.predict_next_move() else None
        }


class AdaptiveEnemyAI:
    """
    AI for enemies that adapts to player's combat style.
    
    This makes combat more dynamic and challenging by learning
    from the player's patterns and adapting strategies accordingly.
    """
    def __init__(self, 
                 enemy: Combatant,
                 personality: EnemyPersonality = None,
                 difficulty: float = 0.5):  # 0.0 to 1.0
        """
        Initialize the adaptive enemy AI.
        
        Args:
            enemy: The enemy combatant
            personality: The enemy's personality
            difficulty: How difficult the enemy should be (0.0 to 1.0)
        """
        self.enemy = enemy
        self.personality = personality or EnemyPersonality()
        self.difficulty = difficulty
        self.memento = CombatMemento()
        self.rounds_played = 0
        
        # Key elements that influence decision making
        self.desperation_threshold = 0.3  # Health % where enemy gets desperate
        
    def choose_move(self, 
                    player: Combatant, 
                    player_last_move: Optional[CombatMove] = None) -> CombatMove:
        """
        Choose the enemy's next move based on AI logic.
        
        Args:
            player: The player combatant
            player_last_move: The player's last move
            
        Returns:
            The chosen combat move
        """
        self.rounds_played += 1
        
        # Filter to moves the enemy can use
        usable_moves = [move for move in self.enemy.available_moves 
                      if self.enemy.can_use_move(move)]
        
        if not usable_moves:
            # If no usable moves, create a basic one with no cost
            return CombatMove(
                name="Desperate Action",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                description="A last-resort action when no other moves are available",
                stamina_cost=0,
                focus_cost=0,
                spirit_cost=0
            )
        
        # Different selection strategies based on state and personality
        if self._is_desperate():
            return self._choose_desperate_move(usable_moves)
        elif self._should_counter(player_last_move):
            return self._choose_counter_move(usable_moves, player_last_move)
        elif self._should_exploit_weakness(player):
            return self._choose_weakness_targeting_move(usable_moves, player)
        else:
            return self._choose_standard_move(usable_moves, player)
    
    def _is_desperate(self) -> bool:
        """
        Determine if the enemy is in a desperate state.
        
        Returns:
            True if desperate, False otherwise
        """
        health_ratio = self.enemy.current_health / self.enemy.max_health
        # More likely to get desperate if risk-taking is high
        adjusted_threshold = self.desperation_threshold - (self.personality.risk_taking * 0.15)
        return health_ratio <= adjusted_threshold
    
    def _should_counter(self, player_last_move: Optional[CombatMove]) -> bool:
        """
        Determine if the enemy should try to counter the player's last move.
        
        Args:
            player_last_move: The player's last move
            
        Returns:
            True if should counter, False otherwise
        """
        if not player_last_move:
            return False
            
        # Higher adaptability means more likely to counter
        counter_chance = 0.2 + (self.personality.adaptability * 0.4)
        
        # If we've seen this move before and failed against it, more likely to counter
        if player_last_move.move_type in self.memento.successful_player_moves:
            counter_chance += 0.2
            
        return random.random() < counter_chance
    
    def _should_exploit_weakness(self, player: Combatant) -> bool:
        """
        Determine if the enemy should try to exploit player weaknesses.
        
        Args:
            player: The player combatant
            
        Returns:
            True if should exploit weakness, False otherwise
        """
        # Check if player has any statuses that can be exploited
        has_exploitable_status = False
        for status in player.statuses:
            if status in [Status.WOUNDED, Status.CONFUSED, Status.STUNNED]:
                has_exploitable_status = True
                break
                
        # Higher aggression means more likely to exploit weaknesses
        exploit_chance = 0.3 + (self.personality.aggression * 0.4)
        if has_exploitable_status:
            exploit_chance += 0.2
            
        return random.random() < exploit_chance
    
    def _get_counter_move_type(self, move_type: MoveType) -> MoveType:
        """
        Get the counter move type for a given move type.
        
        Args:
            move_type: The move type to counter
            
        Returns:
            The counter move type
        """
        # FORCE beats TRICK
        # TRICK beats FOCUS
        # FOCUS beats FORCE
        if move_type == MoveType.FORCE:
            return MoveType.FOCUS
        elif move_type == MoveType.TRICK:
            return MoveType.FORCE
        elif move_type == MoveType.FOCUS:
            return MoveType.TRICK
        else:
            # Default to a random counter type for other move types
            return random.choice([MoveType.FORCE, MoveType.TRICK, MoveType.FOCUS])
    
    def _choose_desperate_move(self, usable_moves: List[CombatMove]) -> CombatMove:
        """
        Choose a move when in a desperate state.
        
        Args:
            usable_moves: List of usable moves
            
        Returns:
            The chosen combat move
        """
        # Prefer high damage moves, especially Force type
        force_moves = [move for move in usable_moves if move.move_type == MoveType.FORCE]
        
        if force_moves:
            chosen_move = random.choice(force_moves)
        else:
            chosen_move = random.choice(usable_moves)
            
        # Make it desperate for higher risk/reward
        chosen_move.as_desperate()
        chosen_move.with_narrative_hook("Fights with desperate fury")
        return chosen_move
    
    def _choose_counter_move(self, usable_moves: List[CombatMove], 
                            player_move: CombatMove) -> CombatMove:
        """
        Choose a move that counters the player's move.
        
        Args:
            usable_moves: List of usable moves
            player_move: The player's move
            
        Returns:
            The chosen combat move
        """
        # Get the move type that counters the player's move
        counter_type = self._get_counter_move_type(player_move.move_type)
        
        # Find moves of the counter type
        counter_moves = [move for move in usable_moves if move.move_type == counter_type]
        
        if counter_moves:
            chosen_move = random.choice(counter_moves)
            # If enemy is calculating, use calculated approach
            if random.random() < self.personality.calculation:
                chosen_move.as_calculated()
                chosen_move.with_narrative_hook("Analyzes and counters your strategy")
            return chosen_move
        else:
            # No direct counter available, choose standard move
            return self._choose_standard_move(usable_moves, None)
    
    def _choose_weakness_targeting_move(self, usable_moves: List[CombatMove], 
                                      player: Combatant) -> CombatMove:
        """
        Choose a move that targets player weaknesses.
        
        Args:
            usable_moves: List of usable moves
            player: The player combatant
            
        Returns:
            The chosen combat move
        """
        # Check for status-specific targeting
        if Status.WOUNDED in player.statuses:
            # Target physical weakness
            body_moves = [move for move in usable_moves 
                        if Domain.BODY in move.domains 
                        and move.move_type == MoveType.FORCE]
            if body_moves:
                chosen_move = random.choice(body_moves)
                chosen_move.with_narrative_hook("Targets your wounds")
                return chosen_move
                
        if Status.CONFUSED in player.statuses:
            # Target mental weakness
            mind_moves = [move for move in usable_moves 
                        if Domain.MIND in move.domains 
                        and move.move_type == MoveType.FOCUS]
            if mind_moves:
                chosen_move = random.choice(mind_moves)
                chosen_move.with_narrative_hook("Exploits your confusion")
                return chosen_move
        
        # Default to standard move if no specific weaknesses to target
        return self._choose_standard_move(usable_moves, player)
    
    def _choose_standard_move(self, usable_moves: List[CombatMove], 
                            player: Optional[Combatant]) -> CombatMove:
        """
        Choose a standard move based on personality and situation.
        
        Args:
            usable_moves: List of usable moves
            player: The player combatant
            
        Returns:
            The chosen combat move
        """
        # Apply personality preferences
        preferred_moves = []
        
        # Filter by preferred move types if specified
        if self.personality.preferred_moves:
            type_filtered = [move for move in usable_moves 
                           if move.move_type in self.personality.preferred_moves]
            if type_filtered:
                preferred_moves = type_filtered
                
        # Filter by specialization domains if specified
        if not preferred_moves and self.personality.specialization:
            domain_filtered = [move for move in usable_moves 
                             if any(domain in move.domains 
                                  for domain in self.personality.specialization)]
            if domain_filtered:
                preferred_moves = domain_filtered
                
        # If we have preferred moves, choose from them, otherwise use all usable moves
        move_pool = preferred_moves if preferred_moves else usable_moves
        
        # Apply move type weighting based on aggression
        force_weight = 1.0 + (self.personality.aggression * 0.5)
        trick_weight = 1.0 + ((1.0 - self.personality.aggression) * 0.5)
        focus_weight = 1.0
        
        # Weight the moves
        weighted_moves = []
        for move in move_pool:
            weight = 1.0
            if move.move_type == MoveType.FORCE:
                weight = force_weight
            elif move.move_type == MoveType.TRICK:
                weight = trick_weight
            elif move.move_type == MoveType.FOCUS:
                weight = focus_weight
                
            # Add the move to the weighted pool multiple times based on weight
            weighted_count = max(1, int(weight * 3))
            for _ in range(weighted_count):
                weighted_moves.append(move)
                
        # Select a random move from the weighted pool
        chosen_move = random.choice(weighted_moves)
        
        # Check if we should make it calculated based on personality
        if random.random() < self.personality.calculation:
            chosen_move.as_calculated()
            
        # Check if we should make it desperate based on personality
        if random.random() < self.personality.risk_taking * 0.3:  # Less likely for standard moves
            chosen_move.as_desperate()
            
        return chosen_move
    
    def update_from_combat_result(self, result: Dict[str, Any], 
                                player_move: CombatMove, 
                                enemy_move: CombatMove) -> None:
        """
        Update AI knowledge based on combat result.
        
        Args:
            result: The combat result
            player_move: The player's move
            enemy_move: The enemy's move
        """
        # Record the round in our memento
        player_success = result.get("actor_success", False)
        if result.get("actor", "") == self.enemy.name:
            # If the enemy was the actor, flip the success value
            player_success = not player_success
            
        self.memento.record_round(player_move, enemy_move, player_success)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation for API responses.
        
        Returns:
            Dictionary representation of this AI
        """
        return {
            "personality": self.personality.to_dict(),
            "difficulty": self.difficulty,
            "rounds_played": self.rounds_played,
            "memento": self.memento.to_dict(),
            "is_desperate": self._is_desperate()
        }