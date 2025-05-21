def apply_environment_effects(self):
    """
    Apply effects from the environment to all combatants
    Uses the enhanced damage system to calculate environmental damage
    Call this at the start of each combat round
    """
    if not self.active_combatants:
        return
        
    # Track all effects applied this round
    round_effects = {}
        
    # Apply effects based on environment tags
    for tag in self.current_environment["tags"]:
        # Environmental effect examples with more nuanced damage calculation
        if tag == "burning":
            for name, combatant in self.active_combatants.items():
                # Calculate damage based on resistances and vulnerabilities
                base_damage = 2  # Base burning damage
                damage_mod = 1.0
                
                # Resistance check
                if Domain.FIRE in combatant.strong_domains:
                    damage_mod *= 0.5  # Half damage for fire resistance
                # Vulnerability check
                if Domain.WATER in combatant.weak_domains:
                    damage_mod *= 1.5  # Extra damage for water weakness
                    
                # Status modification
                if Status.PROTECTED in combatant.statuses:
                    damage_mod *= 0.7  # Reduced damage if protected
                    
                # Apply the damage
                final_damage = round(base_damage * damage_mod)
                original_health = combatant.current_health
                combatant.current_health = max(0, combatant.current_health - final_damage)
                actual_damage = original_health - combatant.current_health
                
                # Add status effect if not already present
                effect_applied = False
                if Status.BURNING not in combatant.statuses:
                    combatant.statuses.append(Status.BURNING)
                    effect_applied = True
                    
                # Track effects
                round_effects[name] = {
                    "environment": tag,
                    "damage": actual_damage,
                    "status_applied": "BURNING" if effect_applied else None
                }
        
        elif tag == "freezing":
            for name, combatant in self.active_combatants.items():
                # Resistance and vulnerability check for freezing
                stamina_loss = 1  # Base stamina loss
                damage = 0
                
                if Domain.ICE in combatant.weak_domains:
                    stamina_loss += 1  # Extra stamina loss
                    damage = 1  # Also causes minor health damage
                    
                if Domain.FIRE in combatant.strong_domains:
                    stamina_loss = max(0, stamina_loss - 1)  # Reduced effect
                    
                # Apply effects
                combatant.current_stamina = max(0, combatant.current_stamina - stamina_loss)
                
                if damage > 0:
                    original_health = combatant.current_health
                    combatant.current_health = max(0, combatant.current_health - damage)
                    actual_damage = original_health - combatant.current_health
                else:
                    actual_damage = 0
                    
                # Add status effect if not already present
                effect_applied = False
                if Status.SLOWED not in combatant.statuses:
                    combatant.statuses.append(Status.SLOWED)
                    effect_applied = True
                    
                # Track effects
                round_effects[name] = {
                    "environment": tag,
                    "damage": actual_damage,
                    "stamina_loss": stamina_loss,
                    "status_applied": "SLOWED" if effect_applied else None
                }
        
        elif tag == "electrified":
            for name, combatant in self.active_combatants.items():
                # Calculate shock damage
                base_damage = 1  # Base shock damage
                damage_mod = 1.0
                
                # Resistances and vulnerabilities
                if Domain.SPARK in combatant.strong_domains:
                    damage_mod *= 0.3  # Significant resistance
                if Domain.WATER in combatant.domains:
                    damage_mod *= 1.8  # Significant vulnerability when wet
                    
                # Status effects
                if Status.SOAKED in combatant.statuses:
                    damage_mod *= 2.0  # Double damage when soaked
                    
                # Apply damage
                final_damage = round(base_damage * damage_mod)
                original_health = combatant.current_health
                combatant.current_health = max(0, combatant.current_health - final_damage)
                actual_damage = original_health - combatant.current_health
                
                # Random chance to apply stunned status (25% chance)
                effect_applied = False
                if random.random() < 0.25 and Status.STUNNED not in combatant.statuses:
                    combatant.statuses.append(Status.STUNNED)
                    effect_applied = True
                    
                # Track effects
                round_effects[name] = {
                    "environment": tag,
                    "damage": actual_damage,
                    "status_applied": "STUNNED" if effect_applied else None
                }
        
        elif tag == "inspirational":
            for name, combatant in self.active_combatants.items():
                # Calculate spirit boost based on personality
                spirit_boost = 1  # Base spirit gain
                
                # Boost is higher for those with spirit domain
                if Domain.SPIRIT in combatant.domains:
                    spirit_boost += 1
                    
                # Apply the boost
                original_spirit = combatant.current_spirit
                combatant.current_spirit = min(combatant.max_spirit, 
                                             combatant.current_spirit + spirit_boost)
                actual_boost = combatant.current_spirit - original_spirit
                
                # Chance to apply inspired status (50% chance)
                effect_applied = False
                if random.random() < 0.5 and Status.INSPIRED not in combatant.statuses:
                    combatant.statuses.append(Status.INSPIRED)
                    effect_applied = True
                    
                # Track effects
                round_effects[name] = {
                    "environment": tag,
                    "spirit_gain": actual_boost,
                    "status_applied": "INSPIRED" if effect_applied else None
                }
        
        elif tag == "toxic":
            for name, combatant in self.active_combatants.items():
                # Calculate poison damage
                base_damage = 1  # Base poison damage
                damage_mod = 1.0
                
                # Resistances and vulnerabilities
                if Domain.NATURE in combatant.strong_domains:
                    damage_mod *= 0.5  # Resistance
                    
                # Status effects
                if Status.WEAKENED in combatant.statuses:
                    damage_mod *= 1.5  # More vulnerable when weakened
                    
                # Apply damage
                final_damage = round(base_damage * damage_mod)
                original_health = combatant.current_health
                combatant.current_health = max(0, combatant.current_health - final_damage)
                actual_damage = original_health - combatant.current_health
                
                # Chance to apply poisoned status (75% chance)
                effect_applied = False
                if random.random() < 0.75 and Status.POISONED not in combatant.statuses:
                    combatant.statuses.append(Status.POISONED)
                    effect_applied = True
                    
                # Track effects
                round_effects[name] = {
                    "environment": tag,
                    "damage": actual_damage,
                    "status_applied": "POISONED" if effect_applied else None
                }
    
    # Return the effects that were applied this round
    return round_effects
