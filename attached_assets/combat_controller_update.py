def resolve_combat_exchange(self, 
                           actor_name: str, 
                           actor_move: CombatMove,
                           target_name: str, 
                           target_move: CombatMove) -> dict:
    """
    Resolve a combat exchange between two combatants with enhanced damage calculation
    
    Args:
        actor_name: Name of the acting combatant
        actor_move: CombatMove for the actor
        target_name: Name of the target combatant
        target_move: CombatMove for the target (can be defensive or offensive)
        
    Returns:
        Dictionary with combat results and narrative
    """
    # Ensure combatants exist
    if actor_name not in self.active_combatants:
        raise ValueError(f"Actor {actor_name} not found in active combatants")
    if target_name not in self.active_combatants:
        raise ValueError(f"Target {target_name} not found in active combatants")
        
    actor = self.active_combatants[actor_name]
    target = self.active_combatants[target_name]
    
    # Resolve the opposed moves
    result = self.combat_system.resolve_opposed_moves(actor, actor_move, target, target_move)
    
    # Calculate damage using our enhanced system
    damage, special_effects = calculate_damage(
        actor=actor,
        target=target,
        actor_move=actor_move,
        target_move=target_move,
        actor_roll=result["actor_roll"],
        target_roll=result["target_roll"],
        actor_success=result["actor_success"],
        effect_magnitude=result["effect_magnitude"],
        type_advantage=result["type_advantage"],
        actor_momentum=result["actor_momentum"],
        target_momentum=result["target_momentum"],
        environment_tags=self.current_environment["tags"]
    )
    
    # Apply the damage and effects
    damage_result = apply_damage_and_effects(
        actor=actor,
        target=target,
        damage=damage,
        special_effects=special_effects,
        actor_move=actor_move,
        combat_system=self.combat_system
    )
    
    # Add damage information to the result
    result["damage"] = damage
    result["special_effects"] = special_effects
    result["damage_result"] = damage_result
    
    # Generate a consequence if significant damage was dealt
    consequence = None
    if result["actor_success"] and damage >= 3:
        # Get character history for context
        character_history = self._get_character_history(target_name)
        current_status = self._get_character_status(target_name)
        
        # Generate consequence
        consequence_data = self.narrative_engine.generate_consequence(
            combat_event=result,
            character_history=character_history,
            current_status=current_status
        )
        
        # Create and apply the consequence
        consequence = self._create_consequence_from_data(consequence_data)
        if consequence:
            target.consequences.append(consequence)
    
    # Generate narrative
    narrative = self._generate_combat_narrative(result, actor, target, actor_move, target_move)
    
    # Update combat history
    self.combat_history.append({
        "round": self.current_round,
        "actor": actor_name,
        "target": target_name,
        "actor_move": actor_move.name,
        "target_move": target_move.name,
        "result": result,
        "narrative": narrative,
        "consequence": asdict(consequence) if consequence else None
    })
    
    # Increment round counter
    self.current_round += 1
    
    # Return the combined results
    return {
        "mechanical_result": result,
        "narrative": narrative,
        "consequence": asdict(consequence) if consequence else None,
        "actor_stats": {
            "health": actor.current_health,
            "stamina": actor.current_stamina,
            "focus": actor.current_focus,
            "spirit": actor.current_spirit,
            "statuses": [s.value for s in actor.statuses]
        },
        "target_stats": {
            "health": target.current_health,
            "stamina": target.current_stamina,
            "focus": target.current_focus,
            "spirit": target.current_spirit,
            "statuses": [s.value for s in target.statuses]
        },
        "damage_info": {
            "base_damage": damage,
            "special_effects": special_effects,
            "applied_effects": damage_result["applied_effects"],
            "removed_effects": damage_result["removed_effects"]
        }
    }
