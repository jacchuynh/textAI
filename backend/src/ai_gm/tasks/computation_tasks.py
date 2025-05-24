"""
Computation-related tasks for AI GM Brain.

This module contains Celery tasks for handling resource-intensive
computational operations asynchronously.
"""

from backend.src.ai_gm.tasks.celery_app import celery_app
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Attempt to import the combat system if available
try:
    from backend.src.ai_gm.ai_gm_combat_integration import AIGMCombatIntegration
    combat_system_available = True
except ImportError:
    logger.warning("Combat system not available. Using mock responses for development.")
    combat_system_available = False

@celery_app.task(bind=True, max_retries=3)
def resolve_complex_combat(self, combat_data, participants, environment_factors):
    """
    Resolve a complex combat scenario with multiple participants.
    
    Args:
        combat_data: Combat configuration and state
        participants: List of combatants
        environment_factors: Environmental effects on combat
        
    Returns:
        Combat resolution results
    """
    try:
        logger.info(f"Resolving complex combat with {len(participants)} participants...")
        start_time = datetime.utcnow()
        
        if combat_system_available:
            # Use the actual combat system
            combat_system = AIGMCombatIntegration()
            result = combat_system.resolve_multi_participant_combat(
                combat_data=combat_data,
                participants=participants,
                environment_factors=environment_factors
            )
        else:
            # Create mock combat resolution for development
            # Simulate processing time for complex combat
            time.sleep(3)
            
            # Create mock results
            result = {
                'rounds': 3,
                'victor': participants[0]['id'] if len(participants) > 0 else None,
                'participants_status': {},
                'key_moments': [
                    "Player landed a critical hit in round 1",
                    "Enemy used defensive stance in round 2",
                    "Environmental effect 'heavy rain' reduced accuracy for all participants"
                ],
                'loot_generated': [
                    {'item_id': 'rusty_sword', 'quality': 'common'},
                    {'item_id': 'healing_potion', 'quality': 'uncommon'}
                ]
            }
            
            # Add status for each participant
            for participant in participants:
                participant_id = participant.get('id', 'unknown')
                result['participants_status'][participant_id] = {
                    'health_remaining': 65,
                    'status_effects': ['bleeding', 'focused'],
                    'actions_used': ['heavy_attack', 'dodge', 'defensive_stance']
                }
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the combat results with metadata
        return {
            'result': result,
            'combat_id': combat_data.get('id', 'unknown'),
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Combat resolution failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(bind=True)
def update_reputation_network(self, player_id, action_data, affected_factions):
    """
    Update reputation across a network of interconnected factions.
    
    Args:
        player_id: Identifier for the player
        action_data: Details of the player's action
        affected_factions: Factions directly affected by the action
        
    Returns:
        Updated reputation values and cascading effects
    """
    try:
        logger.info(f"Updating reputation network for player {player_id}, affecting {len(affected_factions)} factions...")
        
        # Simulate processing time for complex reputation calculations
        time.sleep(2)
        
        # Mock reputation updates
        direct_changes = {}
        indirect_changes = {}
        
        # Generate direct changes for directly affected factions
        for faction in affected_factions:
            # Simulate reputation change based on action
            faction_id = faction.get('id', 'unknown')
            faction_attitude = faction.get('attitude', 'neutral')
            
            # Different impact based on faction's initial attitude
            if faction_attitude == 'friendly':
                change = 5
            elif faction_attitude == 'hostile':
                change = -2
            else:
                change = 3
                
            direct_changes[faction_id] = change
        
        # Generate cascading effects for related factions
        # In a real implementation, this would use a faction relationship graph
        if len(affected_factions) > 0:
            # Simulate related factions
            related_factions = [
                {'id': 'forest_dwellers', 'relationship': 'allied', 'with': affected_factions[0]['id']},
                {'id': 'mountain_clan', 'relationship': 'rival', 'with': affected_factions[0]['id']},
                {'id': 'coastal_traders', 'relationship': 'neutral', 'with': affected_factions[0]['id']}
            ]
            
            for related in related_factions:
                related_id = related['id']
                relationship = related['relationship']
                with_faction = related['with']
                
                # The change for related factions depends on their relationship with the directly affected faction
                if with_faction in direct_changes:
                    direct_change = direct_changes[with_faction]
                    
                    if relationship == 'allied':
                        # Allied factions react similarly but less strongly
                        indirect_changes[related_id] = int(direct_change * 0.7)
                    elif relationship == 'rival':
                        # Rival factions react oppositely
                        indirect_changes[related_id] = int(direct_change * -0.5)
                    else:
                        # Neutral factions are affected minimally
                        indirect_changes[related_id] = int(direct_change * 0.2)
        
        return {
            'player_id': player_id,
            'action_type': action_data.get('type', 'unknown'),
            'direct_changes': direct_changes,
            'indirect_changes': indirect_changes,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Reputation network update failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task
def analyze_player_patterns(self, player_id, action_history, time_period):
    """
    Analyze patterns in player behavior.
    
    Args:
        player_id: Identifier for the player
        action_history: History of player actions
        time_period: Time period to analyze
        
    Returns:
        Analysis of player behavior patterns
    """
    logger.info(f"Analyzing behavior patterns for player {player_id}...")
    
    # Simulate processing time
    time.sleep(3)
    
    # Count action types
    action_counts = {}
    for action in action_history:
        action_type = action.get('type', 'unknown')
        if action_type in action_counts:
            action_counts[action_type] += 1
        else:
            action_counts[action_type] = 1
    
    # Find most common action
    most_common_action = max(action_counts.items(), key=lambda x: x[1], default=('none', 0))
    
    # Calculate playtime distribution by time of day
    time_distribution = {
        'morning': 0,
        'afternoon': 0,
        'evening': 0,
        'night': 0
    }
    
    for action in action_history:
        # Extract hour from timestamp (assuming ISO format)
        timestamp = action.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                hour = dt.hour
                
                if 5 <= hour < 12:
                    time_distribution['morning'] += 1
                elif 12 <= hour < 17:
                    time_distribution['afternoon'] += 1
                elif 17 <= hour < 22:
                    time_distribution['evening'] += 1
                else:
                    time_distribution['night'] += 1
            except (ValueError, TypeError):
                pass
    
    # Convert counts to percentages
    total_actions = len(action_history)
    time_percentages = {}
    if total_actions > 0:
        for key, value in time_distribution.items():
            time_percentages[key] = round((value / total_actions) * 100, 1)
    
    # Generate insights
    preferred_playtime = max(time_percentages.items(), key=lambda x: x[1], default=('none', 0))[0]
    
    # Analyze social interactions
    social_actions = [a for a in action_history if a.get('type') in ['dialogue', 'trade', 'quest_accept']]
    social_percentage = round((len(social_actions) / total_actions) * 100 if total_actions > 0 else 0, 1)
    
    # Analyze combat frequency
    combat_actions = [a for a in action_history if a.get('type') in ['attack', 'defend', 'cast_spell']]
    combat_percentage = round((len(combat_actions) / total_actions) * 100 if total_actions > 0 else 0, 1)
    
    return {
        'player_id': player_id,
        'time_period': time_period,
        'action_counts': action_counts,
        'most_common_action': most_common_action[0],
        'time_distribution': time_percentages,
        'preferred_playtime': preferred_playtime,
        'social_interaction_percentage': social_percentage,
        'combat_percentage': combat_percentage,
        'total_actions_analyzed': total_actions,
        'insights': [
            f"Player prefers {preferred_playtime} gameplay sessions",
            f"Player's most common action is '{most_common_action[0]}'",
            f"Player engages in social interactions {social_percentage}% of the time",
            f"Player engages in combat {combat_percentage}% of the time"
        ],
        'timestamp': datetime.utcnow().isoformat()
    }

@celery_app.task
def calculate_domain_synergies(self, domain_values, available_synergies):
    """
    Calculate complex domain synergies based on character attributes.
    
    Args:
        domain_values: Character's domain attribute values
        available_synergies: Available synergy types
        
    Returns:
        Calculated domain synergies
    """
    logger.info(f"Calculating domain synergies for {len(domain_values)} domains...")
    
    # Simulate complex calculation time
    time.sleep(1.5)
    
    # Calculate primary synergies (direct combinations)
    primary_synergies = {}
    
    # In a real implementation, this would use the actual synergy formulas
    # For now, we'll create mock synergies based on domain combinations
    for i, (domain1, value1) in enumerate(domain_values.items()):
        for domain2, value2 in list(domain_values.items())[i+1:]:
            synergy_key = f"{domain1}_{domain2}"
            
            # Only calculate for available synergy types
            if synergy_key in available_synergies:
                # Mock synergy calculation - in reality would be more complex
                synergy_value = round((value1 * value2) ** 0.5 / 10, 1)
                
                # Apply minimum threshold for meaningful synergies
                if synergy_value >= 1.0:
                    primary_synergies[synergy_key] = synergy_value
    
    # Calculate secondary effects (derived benefits)
    secondary_effects = {}
    for synergy, value in primary_synergies.items():
        # Each primary synergy may provide secondary benefits to other domains
        domains = synergy.split('_')
        for domain in domain_values.keys():
            if domain not in domains:
                # Secondary effect is weaker than primary
                effect_value = round(value * 0.3, 1)
                if effect_value >= 0.5:
                    secondary_effects[f"{synergy}_affects_{domain}"] = effect_value
    
    # Calculate overall synergy rating
    total_synergy = sum(primary_synergies.values()) + sum(secondary_effects.values()) * 0.5
    
    # Determine synergy tier
    if total_synergy >= 20:
        tier = "Legendary"
    elif total_synergy >= 15:
        tier = "Master"
    elif total_synergy >= 10:
        tier = "Expert"
    elif total_synergy >= 5:
        tier = "Adept"
    else:
        tier = "Novice"
    
    return {
        'primary_synergies': primary_synergies,
        'secondary_effects': secondary_effects,
        'total_synergy_value': total_synergy,
        'synergy_tier': tier,
        'domain_count': len(domain_values),
        'timestamp': datetime.utcnow().isoformat()
    }