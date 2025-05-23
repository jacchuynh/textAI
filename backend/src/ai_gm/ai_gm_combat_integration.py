"""
AI GM Brain - Combat System Integration

This module connects the AI GM Brain to the existing monster combat system,
allowing it to orchestrate combat encounters and generate narrative descriptions.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Import from core brain
from .ai_gm_brain import AIGMBrain, ProcessingMode

# Import existing combat system
from ..game_engine.enhanced_combat.combat_controller import CombatController
from ..game_engine.enhanced_combat.monster_database import MonsterDatabase
from monster_combat_test import create_monster_from_archetype, ThreatTier


class CombatIntegration:
    """
    Integration layer that connects the AI GM Brain to the combat system.
    
    This class:
    1. Manages combat state within the AI GM Brain
    2. Translates player input into combat actions
    3. Generates narrative combat descriptions
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the combat integration layer.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"CombatIntegration_{ai_gm_brain.game_id}")
        
        # Initialize combat components
        self.combat_controller = CombatController()
        self.monster_db = MonsterDatabase()
        self.active_combat = None
        
        # Command mappings for combat
        self.combat_commands = {
            "attack": self._cmd_attack,
            "defend": self._cmd_defend,
            "dodge": self._cmd_dodge,
            "use": self._cmd_use_item,
            "flee": self._cmd_flee,
            "status": self._cmd_combat_status
        }
        
        self.logger.info("Combat Integration initialized")
    
    def is_in_combat(self) -> bool:
        """Check if the player is currently in combat."""
        return self.active_combat is not None
    
    def start_combat(self, monster_id: str, tier: ThreatTier = ThreatTier.STANDARD) -> Dict[str, Any]:
        """
        Start a combat encounter with a monster.
        
        Args:
            monster_id: ID of the monster to fight
            tier: Threat tier of the monster
            
        Returns:
            Combat start response data
        """
        self.logger.info(f"Starting combat with monster: {monster_id}, tier: {tier.name}")
        
        try:
            # Load monster archetype
            archetype = self.monster_db.get_archetype(monster_id)
            if not archetype:
                return self._create_error_response(f"Monster with ID '{monster_id}' not found")
            
            # Create monster combatant
            monster, monster_moves = create_monster_from_archetype(
                archetype,
                tier=tier,
                level=1
            )
            
            # TODO: Create player combatant from actual player stats
            # For now, create a placeholder player combatant
            from monster_combat_test import Combatant, Domain, CombatMove, MoveType
            
            player_domains = {
                Domain.BODY: 3,
                Domain.MIND: 2,
                Domain.AWARENESS: 4,
                Domain.SOCIAL: 1,
                Domain.CRAFT: 2,
                Domain.AUTHORITY: 1,
                Domain.SPIRIT: 2
            }
            
            player = Combatant(
                name="Player",
                domains=player_domains,
                max_health=50,
                current_health=50,
                max_stamina=30,
                current_stamina=30,
                max_focus=20,
                current_focus=20,
                max_spirit=10,
                current_spirit=10
            )
            
            player_moves = [
                CombatMove(
                    name="Slash",
                    description="A quick sword attack",
                    move_type=MoveType.FORCE,
                    domains=[Domain.BODY],
                    base_damage=5,
                    stamina_cost=2
                ),
                CombatMove(
                    name="Precise Strike",
                    description="A carefully aimed attack",
                    move_type=MoveType.FOCUS,
                    domains=[Domain.AWARENESS],
                    base_damage=7,
                    focus_cost=3
                ),
                CombatMove(
                    name="Feint",
                    description="A deceptive attack that confuses the opponent",
                    move_type=MoveType.TRICK,
                    domains=[Domain.MIND],
                    base_damage=4,
                    focus_cost=2
                ),
                CombatMove(
                    name="Shield Block",
                    description="Block incoming damage with your shield",
                    move_type=MoveType.DEFEND,
                    domains=[Domain.BODY],
                    stamina_cost=3
                )
            ]
            
            # Set up active combat
            self.active_combat = {
                "player": player,
                "player_moves": player_moves,
                "monster": monster,
                "monster_moves": monster_moves,
                "round": 0,
                "last_exchange": None,
                "combat_log": []
            }
            
            # Generate combat start narrative
            start_narrative = self._generate_combat_start_narrative(monster)
            
            # Record in combat log
            self._log_combat_event("Combat Started", {
                "monster_id": monster_id,
                "monster_name": monster.name,
                "monster_health": monster.current_health,
                "player_health": player.current_health
            })
            
            return {
                "response_text": start_narrative,
                "combat_started": True,
                "monster_name": monster.name,
                "monster_health": monster.current_health,
                "player_health": player.current_health,
                "available_moves": [move.name for move in player_moves]
            }
            
        except Exception as e:
            self.logger.error(f"Error starting combat: {str(e)}")
            return self._create_error_response(f"Error starting combat: {str(e)}")
    
    def end_combat(self, result: str = "unknown") -> Dict[str, Any]:
        """
        End the current combat encounter.
        
        Args:
            result: Result of the combat (victory, defeat, flee)
            
        Returns:
            Combat end response data
        """
        if not self.active_combat:
            return self._create_error_response("No active combat to end")
        
        monster_name = self.active_combat["monster"].name
        
        # Generate end narrative based on result
        if result == "victory":
            end_narrative = f"You have defeated the {monster_name}! The creature lies motionless as you catch your breath, the adrenaline of battle still coursing through your veins. You've earned experience and possibly some loot from this encounter."
        elif result == "defeat":
            end_narrative = f"You've been defeated by the {monster_name}. Your vision blurs as you collapse to the ground, your strength failing you. Somehow, you manage to survive, but not without consequences."
        elif result == "flee":
            end_narrative = f"You manage to escape from the {monster_name}, leaving the threat behind. Your heart races as you put distance between yourself and danger, knowing you narrowly avoided a worse fate."
        else:
            end_narrative = f"The combat with the {monster_name} has ended."
        
        # Log the combat end
        self._log_combat_event("Combat Ended", {
            "result": result,
            "monster_name": monster_name,
            "rounds": self.active_combat["round"]
        })
        
        # Clear active combat
        self.active_combat = None
        
        return {
            "response_text": end_narrative,
            "combat_ended": True,
            "result": result
        }
    
    def process_combat_command(self, input_string: str) -> Dict[str, Any]:
        """
        Process a combat command from the player.
        
        Args:
            input_string: Player input during combat
            
        Returns:
            Combat response data
        """
        if not self.active_combat:
            return self._create_error_response("Not in combat. Start combat first.")
        
        # Parse the command
        words = input_string.lower().split()
        if not words:
            return self._create_error_response("Please specify a combat action")
        
        command = words[0]
        args = " ".join(words[1:])
        
        # Check if it's a known combat command
        if command in self.combat_commands:
            return self.combat_commands[command](args)
        
        # Check if it matches a player move name
        for move in self.active_combat["player_moves"]:
            if move.name.lower() == input_string.lower():
                return self._execute_player_move(move)
        
        # Unknown command
        return self._create_error_response(
            f"Unknown combat command: '{command}'. Try 'attack', 'defend', 'dodge', 'use [item]', 'flee', or 'status'."
        )
    
    def _execute_player_move(self, move) -> Dict[str, Any]:
        """Execute a specific player combat move."""
        self.active_combat["round"] += 1
        round_num = self.active_combat["round"]
        
        player = self.active_combat["player"]
        monster = self.active_combat["monster"]
        
        # Select a random monster move
        monster_move = random.choice(self.active_combat["monster_moves"])
        
        # Check if player has enough resources for the move
        if move.stamina_cost > player.current_stamina:
            return self._create_error_response(f"Not enough stamina to use {move.name}")
        
        if move.focus_cost > player.current_focus:
            return self._create_error_response(f"Not enough focus to use {move.name}")
        
        if move.spirit_cost > player.current_spirit:
            return self._create_error_response(f"Not enough spirit to use {move.name}")
        
        # Deduct costs
        player.current_stamina -= move.stamina_cost
        player.current_focus -= move.focus_cost
        player.current_spirit -= move.spirit_cost
        
        # Resolve combat exchange
        exchange_result = self.combat_controller.resolve_combat_exchange(
            actor_name=player.name,
            actor_move=move,
            target_name=monster.name,
            target_move=monster_move,
            actor=player,
            target=monster
        )
        
        # Store last exchange result
        self.active_combat["last_exchange"] = exchange_result
        
        # Log the combat round
        self._log_combat_event(f"Combat Round {round_num}", {
            "player_move": move.name,
            "monster_move": monster_move.name,
            "player_damage_dealt": exchange_result.get("actor_damage_dealt", 0),
            "monster_damage_dealt": exchange_result.get("target_damage_dealt", 0),
            "player_health": player.current_health,
            "monster_health": monster.current_health
        })
        
        # Check if combat should end
        if monster.is_defeated():
            return self.end_combat("victory")
        
        if player.is_defeated():
            return self.end_combat("defeat")
        
        # Continue combat with exchange narrative
        return {
            "response_text": exchange_result.get("narrative", "The exchange continues..."),
            "player_health": player.current_health,
            "monster_health": monster.current_health,
            "player_stamina": player.current_stamina,
            "player_focus": player.current_focus,
            "player_spirit": player.current_spirit,
            "round": round_num
        }
    
    def _cmd_attack(self, args: str) -> Dict[str, Any]:
        """Handle the 'attack' command."""
        # Default to first offensive move if available
        offensive_moves = [
            move for move in self.active_combat["player_moves"]
            if move.move_type.name in ["FORCE", "FOCUS", "TRICK"]
        ]
        
        if offensive_moves:
            return self._execute_player_move(offensive_moves[0])
        
        return self._create_error_response("No offensive moves available")
    
    def _cmd_defend(self, args: str) -> Dict[str, Any]:
        """Handle the 'defend' command."""
        # Find a defensive move
        defensive_moves = [
            move for move in self.active_combat["player_moves"]
            if move.move_type.name == "DEFEND"
        ]
        
        if defensive_moves:
            return self._execute_player_move(defensive_moves[0])
        
        return self._create_error_response("No defensive moves available")
    
    def _cmd_dodge(self, args: str) -> Dict[str, Any]:
        """Handle the 'dodge' command."""
        # Similar to defend but with different flavor
        dodge_moves = [
            move for move in self.active_combat["player_moves"]
            if move.move_type.name == "DEFEND" and "dodge" in move.name.lower()
        ]
        
        if dodge_moves:
            return self._execute_player_move(dodge_moves[0])
        elif len(self.active_combat["player_moves"]) > 0:
            # Use any defensive move if no specific dodge
            defensive_moves = [
                move for move in self.active_combat["player_moves"]
                if move.move_type.name == "DEFEND"
            ]
            if defensive_moves:
                return self._execute_player_move(defensive_moves[0])
        
        return self._create_error_response("No dodge moves available")
    
    def _cmd_use_item(self, args: str) -> Dict[str, Any]:
        """Handle the 'use' command for items."""
        if not args:
            return self._create_error_response("Specify an item to use")
        
        # Placeholder for item usage
        # Would connect to inventory system
        item_name = args
        
        return {
            "response_text": f"You attempt to use {item_name}, but item usage is not implemented yet.",
            "item_used": False
        }
    
    def _cmd_flee(self, args: str) -> Dict[str, Any]:
        """Handle the 'flee' command."""
        # Simple random chance to flee
        success_chance = 0.4  # 40% chance to escape
        
        if random.random() < success_chance:
            return self.end_combat("flee")
        else:
            # Failed to flee, monster gets a free attack
            monster = self.active_combat["monster"]
            player = self.active_combat["player"]
            
            # Simple damage calculation
            damage = random.randint(3, 8)
            player.take_damage(damage)
            
            # Check if player is defeated
            if player.is_defeated():
                return self.end_combat("defeat")
            
            return {
                "response_text": f"You try to flee, but the {monster.name} blocks your escape and strikes you for {damage} damage!",
                "player_health": player.current_health,
                "flee_failed": True
            }
    
    def _cmd_combat_status(self, args: str) -> Dict[str, Any]:
        """Handle the 'status' command in combat."""
        if not self.active_combat:
            return self._create_error_response("Not in combat")
        
        player = self.active_combat["player"]
        monster = self.active_combat["monster"]
        
        status_text = f"""Combat Status:
You ({player.name}): {player.current_health}/{player.max_health} HP, {player.current_stamina}/{player.max_stamina} Stamina, {player.current_focus}/{player.max_focus} Focus, {player.current_spirit}/{player.max_spirit} Spirit

{monster.name}: {monster.current_health}/{monster.max_health} HP

Available Moves:
{', '.join([move.name for move in self.active_combat["player_moves"]])}

Round: {self.active_combat["round"]}
"""
        
        return {
            "response_text": status_text,
            "player_health": player.current_health,
            "monster_health": monster.current_health,
            "display_status": True
        }
    
    def _generate_combat_start_narrative(self, monster) -> str:
        """Generate a narrative description for combat start."""
        monster_type = monster.__class__.__name__
        
        narratives = [
            f"A {monster.name} appears before you, its menacing presence demanding your attention. The air grows tense as you ready your weapons, knowing that only one of you will walk away from this encounter.",
            
            f"The {monster.name} lets out a challenging sound as it spots you. Its hostile intent is clear—this creature sees you as prey or a threat to be eliminated. You have no choice but to defend yourself.",
            
            f"Without warning, a {monster.name} lunges toward you! You narrowly dodge the first attack, but the creature circles back, forcing you into combat. There's no avoiding this fight now.",
            
            f"The shadows part to reveal a {monster.name}, its eyes fixed on you with deadly purpose. Your hand instinctively moves to your weapon as you prepare to face this threat head-on."
        ]
        
        return random.choice(narratives)
    
    def _log_combat_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log a combat event to the combat log."""
        if not self.active_combat:
            return
        
        self.active_combat["combat_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "details": details
        })
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create an error response."""
        self.logger.error(f"Combat error: {message}")
        
        return {
            "response_text": message,
            "error": True,
            "combat_error": True
        }


# Extension function to add combat capabilities to AI GM Brain
def extend_ai_gm_brain_with_combat(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with combat integration capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create combat integration
    combat_integration = CombatIntegration(ai_gm_brain)
    
    # Store the original _process_mechanical_command method
    original_process_mechanical = ai_gm_brain._process_mechanical_command
    
    # Replace with combat-aware version
    def combat_aware_process_mechanical(input_string: str) -> Dict[str, Any]:
        """Process commands with combat awareness."""
        # Check if in combat
        if combat_integration.is_in_combat():
            # Process as combat command
            return combat_integration.process_combat_command(input_string)
        
        # Special case for "fight" or "attack" commands to start combat
        words = input_string.lower().split()
        if len(words) >= 1 and words[0] in ["fight", "attack"]:
            if len(words) >= 2:
                # Extract monster name/id
                monster_id = words[1]  # This would need to be mapped to actual monster IDs
                
                # For testing, use a hardcoded ID from the monster database
                return combat_integration.start_combat(monster_id)
        
        # Not in combat or not a combat command, use original method
        return original_process_mechanical(input_string)
    
    # Patch the AI GM Brain
    ai_gm_brain._process_mechanical_command = combat_aware_process_mechanical
    
    # Store the combat integration for future reference
    ai_gm_brain.combat_integration = combat_integration