def calculate_damage(
    actor,              # Acting combatant
    target,             # Target combatant
    actor_move,         # CombatMove being used
    target_move,        # Target's response move
    actor_roll,         # Actor's roll result
    target_roll,        # Target's roll result
    actor_success,      # Whether actor succeeded with their move
    effect_magnitude,   # Base magnitude of the effect
    type_advantage,     # Move type advantage factor
    actor_momentum,     # Actor's momentum
    target_momentum,    # Target's momentum
    environment_tags    # Current environment tags
):
    """
    Comprehensive damage calculation that accounts for all combat factors.
    Returns a tuple of (damage, special_effects).
    """
    # Base damage calculation
    if not actor_success:
        return 0, []  # No damage on failure
    
    # Start with base damage from effect magnitude
    base_damage = effect_magnitude
    
    # Apply move type modifiers
    move_type_modifier = 1.0
    if type_advantage > 0:
        move_type_modifier = 1.5  # 50% bonus for advantageous move type
    elif type_advantage < 0:
        move_type_modifier = 0.7  # 30% penalty for disadvantageous move type
    
    # Apply domain expertise modifiers
    domain_modifier = 1.0
    for domain in actor_move.domains:
        # Increase damage based on actor's skill in the domain
        domain_rating = actor.domain_ratings.get(domain, 1)
        domain_modifier += (domain_rating - 1) * 0.1  # +10% per point above 1
        
        # Check if targeting a weakness
        if domain in target.weak_domains:
            domain_modifier += 0.3  # +30% damage when targeting weakness
    
    # Apply momentum modifiers
    momentum_modifier = 1.0
    momentum_diff = actor_momentum - target_momentum
    if momentum_diff > 0:
        momentum_modifier += min(momentum_diff * 0.2, 0.6)  # Up to +60% for momentum
    
    # Apply status effect modifiers
    status_modifier = 1.0
    special_effects = []
    
    # Actor status effects that boost damage
    if Status.ENERGIZED in actor.statuses:
        status_modifier += 0.2  # +20% damage
    if Status.FOCUSED in actor.statuses:
        status_modifier += 0.1  # +10% damage
    if Status.INSPIRED in actor.statuses:
        status_modifier += 0.15  # +15% damage
    
    # Target status effects that increase damage taken
    if Status.VULNERABLE in target.statuses:
        status_modifier += 0.3  # +30% damage
    if Status.WEAKENED in target.statuses:
        status_modifier += 0.2  # +20% damage
    if Status.BURNING in target.statuses and Domain.WATER in actor_move.domains:
        status_modifier += 0.4  # +40% damage for water vs burning
        special_effects.append("EXTINGUISH")  # Add special effect to remove burning
    
    # Target status effects that reduce damage taken
    if Status.PROTECTED in target.statuses:
        status_modifier -= 0.3  # -30% damage
    if Status.FORTIFIED in target.statuses:
        status_modifier -= 0.2  # -20% damage
    
    # Environmental modifiers
    environment_modifier = 1.0
    for tag in environment_tags:
        # Domain-specific environment bonuses
        if tag == "flooded" and Domain.WATER in actor_move.domains:
            environment_modifier += 0.2  # +20% for water moves in flooded environment
        elif tag == "electrified" and Domain.SPARK in actor_move.domains:
            environment_modifier += 0.3  # +30% for spark moves in electrified environment
        elif tag == "windy" and Domain.AIR in actor_move.domains:
            environment_modifier += 0.2  # +20% for air moves in windy environment
        
        # Move type environmental bonuses
        if tag == "chaotic" and actor_move.move_type == MoveType.TRICK:
            environment_modifier += 0.15  # +15% for trick moves in chaotic environment
        elif tag == "confined" and actor_move.move_type == MoveType.FORCE:
            environment_modifier += 0.1  # +10% for force moves in confined spaces
    
    # Special modifiers for calculated and desperate moves
    special_modifier = 1.0
    if actor_move.is_calculated:
        # Calculated moves do less damage but are more reliable
        special_modifier = 0.8
    elif actor_move.is_desperate:
        # Desperate moves do more damage but are risky
        special_modifier = 1.5
    
    # Critical hit chance based on the difference between rolls
    roll_diff = actor_roll - target_roll
    critical_hit = False
    if roll_diff >= 8:  # Significant success
        critical_hit = True
        special_effects.append("CRITICAL")
    
    # Calculate final damage
    final_damage = (base_damage * move_type_modifier * domain_modifier * 
                   momentum_modifier * status_modifier * environment_modifier * 
                   special_modifier)
    
    # Apply critical hit multiplier
    if critical_hit:
        final_damage *= 1.5  # 50% bonus damage on critical hit
    
    # Round to integer
    final_damage = round(final_damage)
    
    # Ensure minimum damage of 1 for successful hits
    if actor_success and final_damage < 1:
        final_damage = 1
    
    return final_damage, special_effects


def apply_damage_and_effects(
    actor,             # Acting combatant
    target,            # Target combatant
    damage,            # Calculated damage value
    special_effects,   # List of special effects to apply
    actor_move,        # Move that was used
    combat_system      # Reference to combat system for status updates
):
    """
    Apply the calculated damage and any special effects to the target
    Returns a dict with the results of the damage application
    """
    # Apply base damage to health
    original_health = target.current_health
    target.current_health = max(0, target.current_health - damage)
    health_damage = original_health - target.current_health
    
    # Track additional effects
    applied_effects = []
    removed_effects = []
    
    # Handle special effects
    for effect in special_effects:
        if effect == "CRITICAL":
            applied_effects.append("Critical hit")
            # Add vulnerable status on critical hit
            if Status.VULNERABLE not in target.statuses:
                target.statuses.append(Status.VULNERABLE)
                applied_effects.append("Target vulnerable")
        
        elif effect == "EXTINGUISH":
            if Status.BURNING in target.statuses:
                target.statuses.remove(Status.BURNING)
                removed_effects.append("Burning removed")
    
    # Apply move-specific status effects based on move type and domains
    if actor_move.move_type == MoveType.FORCE and damage >= 5:
        # Strong force moves can stun
        if Status.STUNNED not in target.statuses:
            target.statuses.append(Status.STUNNED)
            applied_effects.append("Target stunned")
    
    elif actor_move.move_type == MoveType.TRICK and actor_move.is_calculated:
        # Calculated trick moves can confuse
        if Status.CONFUSED not in target.statuses:
            target.statuses.append(Status.CONFUSED)
            applied_effects.append("Target confused")
    
    # Domain-specific effects
    for domain in actor_move.domains:
        if domain == Domain.FIRE and damage >= 3:
            # Fire moves can cause burning
            if Status.BURNING not in target.statuses:
                target.statuses.append(Status.BURNING)
                applied_effects.append("Target burning")
        
        elif domain == Domain.ICE and damage >= 3:
            # Ice moves can slow
            if Status.SLOWED not in target.statuses:
                target.statuses.append(Status.SLOWED)
                applied_effects.append("Target slowed")
    
    # Apply resource costs to actor
    actor.current_stamina -= actor_move.stamina_cost
    actor.current_focus -= actor_move.focus_cost
    actor.current_spirit -= actor_move.spirit_cost
    
    # Check for knockdown on high damage
    if damage >= 7 and Status.PRONE not in target.statuses:
        target.statuses.append(Status.PRONE)
        applied_effects.append("Target knocked down")
    
    # Check for defeat
    defeated = target.current_health <= 0
    
    # Update momentum after successful attack
    if damage > 0:
        # This assumes combat_system has a method to update momentum
        combat_system.update_momentum(actor, +1)
        combat_system.update_momentum(target, -1)
    
    return {
        "damage_dealt": health_damage,
        "applied_effects": applied_effects,
        "removed_effects": removed_effects,
        "target_defeated": defeated,
        "remaining_health": target.current_health,
        "remaining_health_percent": (target.current_health / target.max_health) * 100
    }
