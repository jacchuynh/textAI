"""
Combat controller for the enhanced combat system.

This module serves as the main entry point for combat functionality,
integrating all the combat subsystems and connecting to the domain system.
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import random

from ...shared.models import Character, DomainType
from ...events.event_bus import GameEvent, EventType, event_bus
from ..domain_system import domain_system
from ...memory.memory_manager import memory_manager, MemoryTier, MemoryType

from .combat_system_core import (
    CombatSystem, Combatant, CombatMove, Domain, 
    MoveType, Status, combat_system
)
from .status_system import StatusFactory, StatusTier, EnhancedStatus
from .environment_system import EnvironmentSystem, environment_system
from .narrative_generator import narrative_generator
from .adaptive_enemy_ai import AdaptiveEnemyAI, EnemyPersonality
from .combat_memory import combat_memory


class CombatController:
    """
    Main controller for the enhanced combat system.
    
    This class integrates all the combat subsystems and provides
    a unified interface for combat functionality.
    """
    def __init__(self):
        """Initialize the combat controller"""
        self.active_combats = {}
        self.combat_ai = {}
        
    def start_combat(self, 
                    character: Character, 
                    enemy_type: str, 
                    enemy_level: int = None,
                    environment_tags: List[str] = None,
                    game_id: str = None) -> Dict[str, Any]:
        """
        Start a new combat encounter.
        
        Args:
            character: The player character
            enemy_type: Type of enemy to create
            enemy_level: Optional level override for the enemy (defaults to character level)
            environment_tags: Optional environment tags
            game_id: Optional game ID for event tracking
            
        Returns:
            Combat state dictionary
        """
        # Create a player combatant from the character
        player_combatant = combat_system.create_combatant_from_character(character)
        
        # Set enemy level based on character if not provided
        if enemy_level is None:
            enemy_level = character.level if hasattr(character, 'level') else 1
            
        # Determine enemy domain focus based on type
        domain_focus = self._get_enemy_domain_focus(enemy_type)
        
        # Create an enemy
        enemy = combat_system.create_enemy(
            name=self._generate_enemy_name(enemy_type),
            level=enemy_level,
            enemy_type=enemy_type,
            domain_focus=domain_focus
        )
        
        # Create an AI for the enemy
        personality = self._create_enemy_personality(enemy_type, domain_focus)
        enemy_ai = AdaptiveEnemyAI(
            enemy=enemy,
            personality=personality,
            difficulty=0.5 + (enemy_level * 0.05)  # Scale difficulty with level
        )
        
        # Set environment
        if environment_tags:
            environment_system.set_environment_tags(environment_tags)
        
        # Create the combat state
        combat_state = combat_system.create_combat(
            player=player_combatant,
            enemies=[enemy],
            environment_tags=environment_tags or []
        )
        
        # Store the enemy AI
        self.combat_ai[combat_state["id"]] = enemy_ai
        
        # Store the combat state
        self.active_combats[combat_state["id"]] = combat_state
        
        # Generate initial narrative
        initial_narrative = self._generate_combat_start_narrative(
            player_name=character.name,
            enemy_name=enemy.name,
            enemy_type=enemy_type,
            environment_tags=environment_tags or []
        )
        
        # Update the combat state with the narrative
        combat_state["narrative"] = initial_narrative
        
        # Publish combat started event
        if game_id:
            event_bus.publish(GameEvent(
                type=EventType.COMBAT_STARTED,
                actor=str(character.id),
                context={
                    "enemy_name": enemy.name,
                    "enemy_type": enemy_type,
                    "environment": environment_tags or [],
                    "combat_id": combat_state["id"]
                },
                tags=["combat", "encounter"],
                game_id=game_id
            ))
            
            # Add to memory
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=f"Combat began with a {enemy.name} ({enemy_type})." +
                        (f" Environment: {', '.join(environment_tags)}" if environment_tags else ""),
                importance=6,
                tier=MemoryTier.MEDIUM_TERM,
                tags=["combat", "encounter", enemy_type.lower()],
                game_id=game_id
            )
        
        return combat_state
    
    def process_player_action(self,
                             combat_id: str,
                             action_data: Dict[str, Any],
                             character: Character,
                             game_id: str = None) -> Dict[str, Any]:
        """
        Process a player's combat action.
        
        Args:
            combat_id: ID of the combat
            action_data: Data about the action
            character: The player character
            game_id: Optional game ID for event tracking
            
        Returns:
            Updated combat state
        """
        # Get the combat state
        combat_state = self.active_combats.get(combat_id)
        if not combat_state:
            raise ValueError(f"Combat with ID {combat_id} not found")
            
        # Get the player and enemy combatants
        player_combatant = None
        enemy_combatant = None
        
        for enemy in combat_state.get("enemies", []):
            if enemy.get("id"):
                enemy_id = enemy.get("id")
                enemy_combatant = self._get_combatant_by_id(combat_state, enemy_id)
                
        player_id = combat_state.get("player", {}).get("id")
        player_combatant = self._get_combatant_by_id(combat_state, player_id)
        
        if not player_combatant or not enemy_combatant:
            raise ValueError("Could not find player or enemy combatants")
            
        # Create or get the player's move
        player_move = self._create_move_from_action_data(action_data, player_combatant)
        
        # Get the enemy AI
        enemy_ai = self.combat_ai.get(combat_id)
        if not enemy_ai:
            raise ValueError(f"Enemy AI for combat {combat_id} not found")
            
        # Get the enemy's move
        enemy_move = enemy_ai.choose_move(player_combatant, player_move)
        
        # Resolve the combat round
        result = combat_system.resolve_opposed_moves(
            actor=player_combatant,
            actor_move=player_move,
            target=enemy_combatant,
            target_move=enemy_move
        )
        
        # Update the AI with the result
        enemy_ai.update_from_combat_result(result, player_move, enemy_move)
        
        # Apply environment effects if applicable
        environment_modifier, environment_hooks = environment_system.apply_environment_modifiers(
            move=player_move,
            actor=player_combatant
        )
        
        if environment_modifier != 0:
            result["environment_modifier"] = environment_modifier
            
        if environment_hooks:
            result["environment_hooks"] = environment_hooks
        
        # Apply status effects if applicable
        if "status_applied" in result:
            status_name = result["status_applied"]
            status_tier = StatusTier.MODERATE
            
            if result.get("effect_magnitude", 0) > 7:
                status_tier = StatusTier.SEVERE
            elif result.get("effect_magnitude", 0) > 4:
                status_tier = StatusTier.MODERATE
            else:
                status_tier = StatusTier.MINOR
                
            status = None
            if status_name == "Wounded":
                status = StatusFactory.create_wounded(status_tier)
            elif status_name == "Confused":
                status = StatusFactory.create_confused(status_tier)
                
            if status:
                if result["actor_success"]:
                    status.apply_to_combatant(enemy_combatant)
                else:
                    status.apply_to_combatant(player_combatant)
        
        # Generate narrative
        narrative = self._generate_combat_narrative(
            combat_result=result,
            player_name=character.name,
            player_move=player_move,
            enemy_name=enemy_combatant.name,
            enemy_move=enemy_move,
            environment_tags=combat_state.get("environment_tags", [])
        )
        
        # Update combat state
        self._update_combat_state(
            combat_state=combat_state,
            player_combatant=player_combatant,
            enemy_combatant=enemy_combatant,
            result=result,
            narrative=narrative
        )
        
        # Check if combat has ended
        if result.get("target_defeated", False):
            combat_state["status"] = "victory"
            combat_state["current_phase"] = "combat_end"
            
            # Generate victory narrative
            victory_narrative = self._generate_victory_narrative(
                player_name=character.name,
                enemy_name=enemy_combatant.name
            )
            combat_state["narrative"] = victory_narrative
            
        elif result.get("actor_defeated", False):
            combat_state["status"] = "defeat"
            combat_state["current_phase"] = "combat_end"
            
            # Generate defeat narrative
            defeat_narrative = self._generate_defeat_narrative(
                player_name=character.name,
                enemy_name=enemy_combatant.name
            )
            combat_state["narrative"] = defeat_narrative
        
        # Publish events and update memory if the combat has ended
        if combat_state["status"] != "active" and game_id:
            outcome = "victory" if combat_state["status"] == "victory" else "defeat"
            
            event_bus.publish(GameEvent(
                type=EventType.COMBAT_ENDED,
                actor=str(character.id),
                context={
                    "enemy_name": enemy_combatant.name,
                    "outcome": outcome,
                    "combat_id": combat_id
                },
                tags=["combat", "encounter", outcome],
                game_id=game_id
            ))
            
            # Add to memory
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=f"Combat with {enemy_combatant.name} ended in {outcome}.",
                importance=7,
                tier=MemoryTier.MEDIUM_TERM,
                tags=["combat", "encounter", outcome],
                game_id=game_id
            )
            
            # Add to combat memory
            if outcome == "victory":
                self._record_combat_victory(
                    player_name=character.name,
                    enemy_name=enemy_combatant.name,
                    combat_log=combat_state.get("log", []),
                    game_id=game_id,
                    character_id=str(character.id)
                )
            else:
                self._record_combat_defeat(
                    player_name=character.name,
                    enemy_name=enemy_combatant.name,
                    combat_log=combat_state.get("log", []),
                    game_id=game_id,
                    character_id=str(character.id)
                )
        
        # Record domain growth from combat action
        if game_id:
            # Extract the domains used in the action
            domains_used = [Domain.to_domain_type(domain) for domain in player_move.domains]
            
            # Log domain usage for each domain
            for domain_type in domains_used:
                if domain_type:
                    domain_system.log_domain_use(
                        character_id=str(character.id),
                        domain_type=domain_type,
                        action=f"Used {player_move.name} in combat",
                        success=result.get("actor_success", False)
                    )
        
        return combat_state
    
    def end_combat(self, combat_id: str) -> bool:
        """
        End a combat encounter.
        
        Args:
            combat_id: ID of the combat
            
        Returns:
            True if successful, False otherwise
        """
        if combat_id in self.active_combats:
            # Clean up AI
            if combat_id in self.combat_ai:
                del self.combat_ai[combat_id]
                
            # Clean up combat state
            del self.active_combats[combat_id]
            
            # End combat in the core system
            combat_system.end_combat(combat_id)
            
            return True
        return False
    
    def get_available_player_moves(self, 
                                  combat_id: str, 
                                  player_id: str) -> List[Dict[str, Any]]:
        """
        Get available moves for a player in combat.
        
        Args:
            combat_id: ID of the combat
            player_id: ID of the player
            
        Returns:
            List of available moves
        """
        combat_state = self.active_combats.get(combat_id)
        if not combat_state:
            return []
            
        player_combatant = self._get_combatant_by_id(combat_state, player_id)
        if not player_combatant:
            return []
            
        # Get all available moves
        available_moves = []
        for move in player_combatant.available_moves:
            if player_combatant.can_use_move(move):
                available_moves.append(move.to_dict())
                
        return available_moves
    
    def get_available_environment_interactions(self, combat_id: str) -> List[Dict[str, Any]]:
        """
        Get available environment interactions for a combat.
        
        Args:
            combat_id: ID of the combat
            
        Returns:
            List of available environment interactions
        """
        combat_state = self.active_combats.get(combat_id)
        if not combat_state or not combat_state.get("environment_tags"):
            return []
            
        # Set environment tags
        environment_system.set_environment_tags(combat_state["environment_tags"])
        
        # Get available interactions
        interactions = environment_system.get_available_interactions()
        
        return [interaction.to_dict() for interaction in interactions]
    
    def get_combat_state(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a combat.
        
        Args:
            combat_id: ID of the combat
            
        Returns:
            Combat state dictionary or None if not found
        """
        return self.active_combats.get(combat_id)
    
    def _get_combatant_by_id(self, combat_state: Dict[str, Any], combatant_id: str) -> Optional[Combatant]:
        """
        Get a combatant by ID from a combat state.
        
        Args:
            combat_state: The combat state
            combatant_id: ID of the combatant
            
        Returns:
            Combatant object or None if not found
        """
        # Check if it's the player
        if combat_state.get("player", {}).get("id") == combatant_id:
            # Reconstruct the player combatant
            player_data = combat_state["player"]
            
            # Create domain ratings
            domain_ratings = {}
            for domain_name, value in player_data.get("domain_ratings", {}).items():
                for domain in Domain:
                    if domain.value == domain_name:
                        domain_ratings[domain] = value
            
            player = Combatant(
                name=player_data["name"],
                combatant_type=player_data["type"],
                domain_ratings=domain_ratings,
                max_health=player_data["health"]["max"],
                max_stamina=player_data["stamina"]["max"],
                max_focus=player_data["focus"]["max"],
                max_spirit=player_data["spirit"]["max"]
            )
            
            # Set current stats
            player.current_health = player_data["health"]["current"]
            player.current_stamina = player_data["stamina"]["current"]
            player.current_focus = player_data["focus"]["current"]
            player.current_spirit = player_data["spirit"]["current"]
            
            # Set ID
            player.id = player_data["id"]
            
            # Add statuses
            for status_name in player_data.get("statuses", []):
                for status in Status:
                    if status.value == status_name:
                        player.statuses.add(status)
                        
            # Add moves
            for move_data in player_data.get("available_moves", []):
                domains = []
                for domain_name in move_data.get("domains", []):
                    for domain in Domain:
                        if domain.value == domain_name:
                            domains.append(domain)
                
                move_type = MoveType.FORCE
                for mt in MoveType:
                    if mt.value == move_data.get("move_type"):
                        move_type = mt
                
                move = CombatMove(
                    name=move_data["name"],
                    move_type=move_type,
                    domains=domains,
                    description=move_data.get("description", ""),
                    stamina_cost=move_data.get("stamina_cost", 0),
                    focus_cost=move_data.get("focus_cost", 0),
                    spirit_cost=move_data.get("spirit_cost", 0)
                )
                
                if move_data.get("is_desperate", False):
                    move.as_desperate()
                    
                if move_data.get("is_calculated", False):
                    move.as_calculated()
                    
                if move_data.get("narrative_hook"):
                    move.with_narrative_hook(move_data["narrative_hook"])
                    
                player.add_move(move)
                
            return player
            
        # Check if it's an enemy
        for enemy_data in combat_state.get("enemies", []):
            if enemy_data.get("id") == combatant_id:
                # Reconstruct the enemy combatant
                domain_ratings = {}
                for domain_name, value in enemy_data.get("domain_ratings", {}).items():
                    for domain in Domain:
                        if domain.value == domain_name:
                            domain_ratings[domain] = value
                
                enemy = Combatant(
                    name=enemy_data["name"],
                    combatant_type=enemy_data["type"],
                    domain_ratings=domain_ratings,
                    max_health=enemy_data["health"]["max"],
                    max_stamina=enemy_data["stamina"]["max"],
                    max_focus=enemy_data["focus"]["max"],
                    max_spirit=enemy_data["spirit"]["max"]
                )
                
                # Set current stats
                enemy.current_health = enemy_data["health"]["current"]
                enemy.current_stamina = enemy_data["stamina"]["current"]
                enemy.current_focus = enemy_data["focus"]["current"]
                enemy.current_spirit = enemy_data["spirit"]["current"]
                
                # Set ID
                enemy.id = enemy_data["id"]
                
                # Add statuses
                for status_name in enemy_data.get("statuses", []):
                    for status in Status:
                        if status.value == status_name:
                            enemy.statuses.add(status)
                            
                # Add moves
                for move_data in enemy_data.get("available_moves", []):
                    domains = []
                    for domain_name in move_data.get("domains", []):
                        for domain in Domain:
                            if domain.value == domain_name:
                                domains.append(domain)
                    
                    move_type = MoveType.FORCE
                    for mt in MoveType:
                        if mt.value == move_data.get("move_type"):
                            move_type = mt
                    
                    move = CombatMove(
                        name=move_data["name"],
                        move_type=move_type,
                        domains=domains,
                        description=move_data.get("description", ""),
                        stamina_cost=move_data.get("stamina_cost", 0),
                        focus_cost=move_data.get("focus_cost", 0),
                        spirit_cost=move_data.get("spirit_cost", 0)
                    )
                    
                    if move_data.get("is_desperate", False):
                        move.as_desperate()
                        
                    if move_data.get("is_calculated", False):
                        move.as_calculated()
                        
                    if move_data.get("narrative_hook"):
                        move.with_narrative_hook(move_data["narrative_hook"])
                        
                    enemy.add_move(move)
                    
                return enemy
                
        return None
    
    def _create_move_from_action_data(self, action_data: Dict[str, Any], combatant: Combatant) -> CombatMove:
        """
        Create a CombatMove from action data.
        
        Args:
            action_data: Data about the action
            combatant: The combatant performing the action
            
        Returns:
            A CombatMove object
        """
        # Check if this is a move ID reference
        if "move_id" in action_data:
            # Find the move by ID in the combatant's available moves
            for move in combatant.available_moves:
                if move.name == action_data["move_id"]:
                    # Create a copy of the move
                    new_move = CombatMove(
                        name=move.name,
                        move_type=move.move_type,
                        domains=move.domains,
                        description=move.description,
                        stamina_cost=move.stamina_cost,
                        focus_cost=move.focus_cost,
                        spirit_cost=move.spirit_cost
                    )
                    
                    # Apply desperate/calculated modifiers if specified
                    if action_data.get("desperate", False):
                        new_move.as_desperate()
                        
                    if action_data.get("calculated", False):
                        new_move.as_calculated()
                        
                    # Apply narrative hook if specified
                    if action_data.get("narrative_hook"):
                        new_move.with_narrative_hook(action_data["narrative_hook"])
                        
                    return new_move
        
        # If we didn't find a move by ID, create a new one from the action data
        domains = []
        if "domains" in action_data:
            for domain_name in action_data["domains"]:
                for domain in Domain:
                    if domain.value == domain_name:
                        domains.append(domain)
        
        move_type = MoveType.FORCE
        if "move_type" in action_data:
            for mt in MoveType:
                if mt.value == action_data["move_type"]:
                    move_type = mt
        
        move = CombatMove(
            name=action_data.get("name", "Custom Move"),
            move_type=move_type,
            domains=domains,
            description=action_data.get("description", "A custom move"),
            stamina_cost=action_data.get("stamina_cost", 1),
            focus_cost=action_data.get("focus_cost", 0),
            spirit_cost=action_data.get("spirit_cost", 0)
        )
        
        if action_data.get("desperate", False):
            move.as_desperate()
            
        if action_data.get("calculated", False):
            move.as_calculated()
            
        if action_data.get("narrative_hook"):
            move.with_narrative_hook(action_data["narrative_hook"])
            
        return move
    
    def _update_combat_state(self,
                           combat_state: Dict[str, Any],
                           player_combatant: Combatant,
                           enemy_combatant: Combatant,
                           result: Dict[str, Any],
                           narrative: Dict[str, str]) -> None:
        """
        Update a combat state with the results of a combat round.
        
        Args:
            combat_state: The combat state to update
            player_combatant: The player combatant
            enemy_combatant: The enemy combatant
            result: Results of the combat round
            narrative: Narrative description of the combat round
        """
        # Increment round counter
        combat_state["round"] = combat_state.get("round", 1) + 1
        
        # Update player state
        player_dict = player_combatant.to_dict()
        combat_state["player"]["health"]["current"] = player_dict["health"]["current"]
        combat_state["player"]["health"]["max"] = player_dict["health"]["max"]
        combat_state["player"]["stamina"]["current"] = player_dict["stamina"]["current"]
        combat_state["player"]["stamina"]["max"] = player_dict["stamina"]["max"]
        combat_state["player"]["focus"]["current"] = player_dict["focus"]["current"]
        combat_state["player"]["focus"]["max"] = player_dict["focus"]["max"]
        combat_state["player"]["spirit"]["current"] = player_dict["spirit"]["current"]
        combat_state["player"]["spirit"]["max"] = player_dict["spirit"]["max"]
        combat_state["player"]["statuses"] = player_dict["statuses"]
        
        # Update enemy state
        for i, enemy in enumerate(combat_state["enemies"]):
            if enemy["id"] == enemy_combatant.id:
                enemy_dict = enemy_combatant.to_dict()
                combat_state["enemies"][i]["health"]["current"] = enemy_dict["health"]["current"]
                combat_state["enemies"][i]["health"]["max"] = enemy_dict["health"]["max"]
                combat_state["enemies"][i]["stamina"]["current"] = enemy_dict["stamina"]["current"]
                combat_state["enemies"][i]["stamina"]["max"] = enemy_dict["stamina"]["max"]
                combat_state["enemies"][i]["focus"]["current"] = enemy_dict["focus"]["current"]
                combat_state["enemies"][i]["focus"]["max"] = enemy_dict["focus"]["max"]
                combat_state["enemies"][i]["spirit"]["current"] = enemy_dict["spirit"]["current"]
                combat_state["enemies"][i]["spirit"]["max"] = enemy_dict["spirit"]["max"]
                combat_state["enemies"][i]["statuses"] = enemy_dict["statuses"]
                break
        
        # Add to combat log
        if "log" not in combat_state:
            combat_state["log"] = []
            
        combat_state["log"].append(result)
        
        # Set narrative
        combat_state["narrative"] = narrative
    
    def _generate_combat_start_narrative(self,
                                        player_name: str,
                                        enemy_name: str,
                                        enemy_type: str,
                                        environment_tags: List[str]) -> Dict[str, str]:
        """
        Generate narrative for the start of combat.
        
        Args:
            player_name: Name of the player
            enemy_name: Name of the enemy
            enemy_type: Type of enemy
            environment_tags: List of environment tags
            
        Returns:
            Narrative dictionary
        """
        environment_desc = ""
        if environment_tags:
            environment_desc = f" in {', '.join(environment_tags)}"
            
        main_narrative = f"{player_name} encounters a {enemy_name} ({enemy_type}){environment_desc}! Combat begins!"
        
        # Get any memory context
        memory_hooks = combat_memory.get_narrative_hooks()
        memory_hook = ""
        
        for hook in memory_hooks:
            if enemy_type.lower() in hook.lower():
                memory_hook = hook
                break
                
        if not memory_hook and enemy_name in combat_memory.opponent_history:
            insights = combat_memory.get_opponent_insights(enemy_name)
            if insights.get("narrative_callback"):
                memory_hook = insights["narrative_callback"]
        
        return {
            "main": main_narrative,
            "memory_hook": memory_hook,
            "environment": f"The battle takes place{environment_desc}." if environment_desc else ""
        }
    
    def _generate_combat_narrative(self,
                                  combat_result: Dict[str, Any],
                                  player_name: str,
                                  player_move: CombatMove,
                                  enemy_name: str,
                                  enemy_move: CombatMove,
                                  environment_tags: List[str]) -> Dict[str, str]:
        """
        Generate narrative for a combat round.
        
        Args:
            combat_result: Results of the combat round
            player_name: Name of the player
            player_move: The player's move
            enemy_name: Name of the enemy
            enemy_move: The enemy's move
            environment_tags: List of environment tags
            
        Returns:
            Narrative dictionary
        """
        # Determine who is the actor and target based on the result structure
        is_player_actor = combat_result.get("actor", "") == player_name
        
        actor_name = player_name if is_player_actor else enemy_name
        target_name = enemy_name if is_player_actor else player_name
        
        move_name = player_move.name if is_player_actor else enemy_move.name
        domains = [d.value for d in player_move.domains] if is_player_actor else [d.value for d in enemy_move.domains]
        
        is_desperate = player_move.is_desperate if is_player_actor else enemy_move.is_desperate
        is_calculated = player_move.is_calculated if is_player_actor else enemy_move.is_calculated
        
        # Generate the narrative
        narrative = narrative_generator.generate_combat_narrative(
            combat_result=combat_result,
            actor_name=actor_name,
            target_name=target_name,
            move_name=move_name,
            domains=domains,
            environment_tags=environment_tags,
            is_desperate=is_desperate,
            is_calculated=is_calculated
        )
        
        return narrative
    
    def _generate_victory_narrative(self, player_name: str, enemy_name: str) -> Dict[str, str]:
        """
        Generate narrative for victory in combat.
        
        Args:
            player_name: Name of the player
            enemy_name: Name of the enemy
            
        Returns:
            Narrative dictionary
        """
        victory_messages = [
            f"{player_name} has defeated {enemy_name}!",
            f"After a fierce battle, {player_name} emerges victorious over {enemy_name}!",
            f"{enemy_name} falls before {player_name}'s might!",
            f"Victory! {player_name} has triumphed over {enemy_name}!"
        ]
        
        return {
            "main": random.choice(victory_messages),
            "consequence": f"You can proceed having defeated {enemy_name}."
        }
    
    def _generate_defeat_narrative(self, player_name: str, enemy_name: str) -> Dict[str, str]:
        """
        Generate narrative for defeat in combat.
        
        Args:
            player_name: Name of the player
            enemy_name: Name of the enemy
            
        Returns:
            Narrative dictionary
        """
        defeat_messages = [
            f"{player_name} has been defeated by {enemy_name}!",
            f"The battle ends with {player_name}'s defeat at the hands of {enemy_name}.",
            f"{player_name} falls before {enemy_name}'s might.",
            f"Defeat! {player_name} has been beaten by {enemy_name}."
        ]
        
        return {
            "main": random.choice(defeat_messages),
            "consequence": "You will need to recover before trying again."
        }
    
    def _record_combat_victory(self,
                              player_name: str,
                              enemy_name: str,
                              combat_log: List[Dict[str, Any]],
                              game_id: str,
                              character_id: str) -> None:
        """
        Record a combat victory in the combat memory.
        
        Args:
            player_name: Name of the player
            enemy_name: Name of the enemy
            combat_log: Log of the combat
            game_id: ID of the game
            character_id: ID of the character
        """
        # Extract relevant data for memory
        encounter_data = {
            "outcome": "victory",
            "opponents": [
                {
                    "name": enemy_name,
                    "moves_used": self._extract_enemy_moves(combat_log)
                }
            ],
            "moves_used": self._extract_player_moves(combat_log),
            "notable_moments": self._extract_notable_moments(combat_log)
        }
        
        # Record the encounter
        combat_memory.record_encounter(encounter_data)
        
        # Create memory event
        combat_memory.publish_memory_event(
            game_id=game_id,
            character_id=character_id,
            opponent_name=enemy_name,
            content=f"Defeated {enemy_name} in combat.",
            tags=["combat", "victory"]
        )
    
    def _record_combat_defeat(self,
                             player_name: str,
                             enemy_name: str,
                             combat_log: List[Dict[str, Any]],
                             game_id: str,
                             character_id: str) -> None:
        """
        Record a combat defeat in the combat memory.
        
        Args:
            player_name: Name of the player
            enemy_name: Name of the enemy
            combat_log: Log of the combat
            game_id: ID of the game
            character_id: ID of the character
        """
        # Extract relevant data for memory
        encounter_data = {
            "outcome": "defeat",
            "opponents": [
                {
                    "name": enemy_name,
                    "moves_used": self._extract_enemy_moves(combat_log),
                    "strengths_shown": self._extract_enemy_strengths(combat_log)
                }
            ],
            "moves_used": self._extract_player_moves(combat_log),
            "notable_moments": self._extract_notable_moments(combat_log)
        }
        
        # Record the encounter
        combat_memory.record_encounter(encounter_data)
        
        # Create memory event
        combat_memory.publish_memory_event(
            game_id=game_id,
            character_id=character_id,
            opponent_name=enemy_name,
            content=f"Was defeated by {enemy_name} in combat.",
            tags=["combat", "defeat"]
        )
    
    def _extract_enemy_moves(self, combat_log: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract enemy moves from combat log"""
        moves = []
        for entry in combat_log:
            if not entry.get("actor_success", False):
                moves.append({
                    "name": entry.get("target_move", "Unknown"),
                    "success": True,
                    "damage": entry.get("counter_damage", 0)
                })
        return moves
    
    def _extract_player_moves(self, combat_log: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract player moves from combat log"""
        moves = []
        for entry in combat_log:
            if "actor_move" in entry:
                moves.append({
                    "name": entry.get("actor_move", "Unknown"),
                    "success": entry.get("actor_success", False),
                    "damage": entry.get("damage_dealt", 0)
                })
        return moves
    
    def _extract_enemy_strengths(self, combat_log: List[Dict[str, Any]]) -> List[str]:
        """Extract enemy strengths from combat log"""
        strengths = []
        
        # If player failed more against certain move types, those are enemy strengths
        move_type_failures = {}
        for entry in combat_log:
            if not entry.get("actor_success", False) and "target_move" in entry:
                move_type = entry.get("target_move_type", "FORCE")
                if move_type not in move_type_failures:
                    move_type_failures[move_type] = 0
                move_type_failures[move_type] += 1
        
        # Get the move types with most failures
        if move_type_failures:
            max_failures = max(move_type_failures.values())
            for move_type, failures in move_type_failures.items():
                if failures == max_failures:
                    strengths.append(f"Strong with {move_type.lower()} attacks")
        
        return strengths
    
    def _extract_notable_moments(self, combat_log: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract notable moments from combat log"""
        moments = []
        
        # Find high damage or critical hits
        for entry in combat_log:
            if entry.get("actor_success", False) and entry.get("damage_dealt", 0) > 15:
                moments.append({
                    "description": f"Dealt a devastating {entry.get('damage_dealt')} damage with {entry.get('actor_move')}",
                    "involves": entry.get("target", "")
                })
            
            if not entry.get("actor_success", False) and entry.get("counter_damage", 0) > 10:
                moments.append({
                    "description": f"Suffered a powerful counter-attack of {entry.get('counter_damage')} damage",
                    "involves": entry.get("target", "")
                })
        
        return moments
    
    def _get_enemy_domain_focus(self, enemy_type: str) -> List[Domain]:
        """
        Get domain focus for an enemy type.
        
        Args:
            enemy_type: The type of enemy
            
        Returns:
            List of focus domains
        """
        # Define domain focus based on enemy type
        domain_focuses = {
            "bandit": [Domain.BODY, Domain.AWARENESS],
            "wolf": [Domain.BODY, Domain.AWARENESS],
            "troll": [Domain.BODY, Domain.CRAFT],
            "goblin": [Domain.CRAFT, Domain.TRICK],
            "skeleton": [Domain.BODY],
            "cultist": [Domain.SPIRIT, Domain.MIND],
            "knight": [Domain.BODY, Domain.AUTHORITY],
            "mage": [Domain.MIND, Domain.SPIRIT],
            "vampire": [Domain.SOCIAL, Domain.SPIRIT],
            "dragon": [Domain.BODY, Domain.SPIRIT, Domain.AUTHORITY],
            "zombie": [Domain.BODY],
            "orc": [Domain.BODY, Domain.CRAFT],
            "demon": [Domain.SPIRIT, Domain.BODY],
            "elemental": [Domain.SPIRIT, Domain.BODY],
            "ghost": [Domain.SPIRIT, Domain.SOCIAL],
            "minotaur": [Domain.BODY, Domain.AUTHORITY],
            "ogre": [Domain.BODY],
            "werewolf": [Domain.BODY, Domain.AWARENESS],
            "assassin": [Domain.AWARENESS, Domain.CRAFT],
            "pirate": [Domain.SOCIAL, Domain.BODY]
        }
        
        # Default to BODY if no specific focus defined
        enemy_type_lower = enemy_type.lower()
        
        for key, domains in domain_focuses.items():
            if key in enemy_type_lower:
                return domains
        
        return [Domain.BODY, Domain.AWARENESS]
    
    def _create_enemy_personality(self, enemy_type: str, domain_focus: List[Domain]) -> EnemyPersonality:
        """
        Create an enemy personality based on type and domain focus.
        
        Args:
            enemy_type: The type of enemy
            domain_focus: List of focus domains
            
        Returns:
            An EnemyPersonality object
        """
        # Define personality traits based on enemy type
        personality_traits = {
            "bandit": {"aggression": 0.6, "adaptability": 0.5, "risk_taking": 0.7, "calculation": 0.3},
            "wolf": {"aggression": 0.8, "adaptability": 0.6, "risk_taking": 0.7, "calculation": 0.2},
            "troll": {"aggression": 0.9, "adaptability": 0.3, "risk_taking": 0.8, "calculation": 0.1},
            "goblin": {"aggression": 0.5, "adaptability": 0.7, "risk_taking": 0.8, "calculation": 0.4},
            "skeleton": {"aggression": 0.5, "adaptability": 0.2, "risk_taking": 0.4, "calculation": 0.2},
            "cultist": {"aggression": 0.4, "adaptability": 0.6, "risk_taking": 0.5, "calculation": 0.7},
            "knight": {"aggression": 0.6, "adaptability": 0.5, "risk_taking": 0.3, "calculation": 0.8},
            "mage": {"aggression": 0.3, "adaptability": 0.7, "risk_taking": 0.4, "calculation": 0.9},
            "vampire": {"aggression": 0.5, "adaptability": 0.8, "risk_taking": 0.4, "calculation": 0.8},
            "dragon": {"aggression": 0.7, "adaptability": 0.6, "risk_taking": 0.3, "calculation": 0.9}
        }
        
        # Default personality
        default_traits = {"aggression": 0.5, "adaptability": 0.5, "risk_taking": 0.5, "calculation": 0.5}
        
        # Find the most specific match
        traits = default_traits
        match_length = 0
        
        for key, value in personality_traits.items():
            if key in enemy_type.lower() and len(key) > match_length:
                traits = value
                match_length = len(key)
        
        # Create preferred move types based on domain focus
        preferred_moves = []
        if Domain.BODY in domain_focus or Domain.CRAFT in domain_focus:
            preferred_moves.append(MoveType.FORCE)
        if Domain.MIND in domain_focus or Domain.AWARENESS in domain_focus:
            preferred_moves.append(MoveType.FOCUS)
        if Domain.SOCIAL in domain_focus:
            preferred_moves.append(MoveType.TRICK)
        
        # Create the personality
        return EnemyPersonality(
            aggression=traits["aggression"],
            adaptability=traits["adaptability"],
            risk_taking=traits["risk_taking"],
            calculation=traits["calculation"],
            specialization=domain_focus,
            preferred_moves=preferred_moves
        )
    
    def _generate_enemy_name(self, enemy_type: str) -> str:
        """
        Generate a name for an enemy of a specific type.
        
        Args:
            enemy_type: The type of enemy
            
        Returns:
            A generated name
        """
        # Define name prefixes based on enemy type
        prefixes = {
            "bandit": ["Ruthless", "Cutthroat", "Savage", "Outlaw", "Renegade"],
            "wolf": ["Fierce", "Hungry", "Alpha", "Grey", "Shadow"],
            "troll": ["Hulking", "Mossy", "Bridge", "Rock", "Mountain"],
            "goblin": ["Sneaky", "Clever", "Greedy", "Nimble", "Tricky"],
            "skeleton": ["Ancient", "Rattling", "Crumbling", "Undying", "Bony"],
            "cultist": ["Fanatical", "Hooded", "Zealous", "Dark", "Devoted"],
            "knight": ["Fallen", "Dark", "Corrupted", "Oath-bound", "Forsaken"],
            "mage": ["Arcane", "Eldritch", "Mystic", "Astral", "Forgotten"],
            "vampire": ["Ancient", "Blood-thirsting", "Noble", "Nocturnal", "Immortal"],
            "dragon": ["Ancient", "Fiery", "Scaled", "Winged", "Thundering"],
            "zombie": ["Shuffling", "Rotting", "Groaning", "Festering", "Shambling"],
            "orc": ["Scarred", "War-painted", "Tusked", "Brutish", "Battleworn"],
            "demon": ["Soul-eating", "Flame-eyed", "Pit-spawned", "Horned", "Infernal"],
            "elemental": ["Primal", "Ancient", "Crystalline", "Tempestuous", "Earthen"],
            "ghost": ["Wailing", "Vengeful", "Ethereal", "Chained", "Forlorn"],
            "minotaur": ["Maze-dwelling", "Horn-crowned", "Mighty", "Bull-headed", "Labyrinth"],
            "ogre": ["Lumbering", "Dim-witted", "Club-wielding", "Massive", "Hungry"],
            "werewolf": ["Moonlit", "Feral", "Pack", "Silver-fearing", "Curse-bound"],
            "assassin": ["Silent", "Poisoned-blade", "Shadow", "Masked", "Contract-bound"],
            "pirate": ["One-eyed", "Sea-worn", "Cutlass", "Rum-soaked", "Salt-weathered"]
        }
        
        # Define name suffixes based on enemy type
        suffixes = {
            "bandit": ["Raider", "Thug", "Marauder", "Pillager", "Brigand"],
            "wolf": ["Fang", "Howler", "Hunter", "Stalker", "Pack Leader"],
            "troll": ["Smasher", "Crusher", "Stomper", "Clubber", "Brute"],
            "goblin": ["Thief", "Trickster", "Backstabber", "Sneak", "Firestarter"],
            "skeleton": ["Warrior", "Archer", "Guard", "Sentry", "Champion"],
            "cultist": ["Acolyte", "Devotee", "Follower", "Preacher", "Priest"],
            "knight": ["Templar", "Guardian", "Defender", "Paladin", "Crusader"],
            "mage": ["Sorcerer", "Conjurer", "Illusionist", "Diviner", "Wizard"],
            "vampire": ["Count", "Lord", "Master", "Thrall-keeper", "Blood-drinker"],
            "dragon": ["Wyrm", "Drake", "Serpent", "Wyvern", "Destroyer"],
            "zombie": ["Corpse", "Revenant", "Walker", "Shambler", "Undead"],
            "orc": ["Warrior", "Berserker", "Hunter", "Raider", "Champion"],
            "demon": ["Fiend", "Hellspawn", "Tormentor", "Soul-taker", "Corruptor"],
            "elemental": ["Spirit", "Embodiment", "Avatar", "Essence", "Force"],
            "ghost": ["Apparition", "Haunt", "Specter", "Phantom", "Spirit"],
            "minotaur": ["Bull", "Horned One", "Labyrinth Guardian", "Beast", "Bull-man"],
            "ogre": ["Giant", "Crusher", "Man-eater", "Brute", "Smasher"],
            "werewolf": ["Hunter", "Howler", "Moon-cursed", "Shape-shifter", "Beast"],
            "assassin": ["Killer", "Blade", "Mercenary", "Hunter", "Death-dealer"],
            "pirate": ["Captain", "Buccaneer", "Corsair", "Marauder", "Swashbuckler"]
        }
        
        # Find the appropriate name components
        enemy_type_lower = enemy_type.lower()
        prefix_list = None
        suffix_list = None
        
        for key, value in prefixes.items():
            if key in enemy_type_lower:
                prefix_list = value
                break
                
        for key, value in suffixes.items():
            if key in enemy_type_lower:
                suffix_list = value
                break
                
        # Use defaults if no match found
        if not prefix_list:
            prefix_list = ["Dangerous", "Deadly", "Fearsome", "Menacing", "Threatening"]
            
        if not suffix_list:
            suffix_list = ["Foe", "Enemy", "Opponent", "Adversary", "Challenger"]
            
        # Generate a name
        prefix = random.choice(prefix_list)
        suffix = random.choice(suffix_list)
        
        return f"{prefix} {suffix}"


# Create a global instance
combat_controller = CombatController()