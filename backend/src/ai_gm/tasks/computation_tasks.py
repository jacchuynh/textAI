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
import random

logger = logging.getLogger(__name__)

# Attempt to import the computation components if available
try:
    from backend.src.ai_gm.ai_gm_combat_integration import AIGMCombatIntegration
    computation_components_available = True
except ImportError:
    logger.warning("Computation components not available. Using mock responses for development.")
    computation_components_available = False

@celery_app.task(bind=True, max_retries=2)
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
        
        if computation_components_available:
            combat_system = AIGMCombatIntegration()
            
            # Resolve the combat
            results = combat_system.resolve_full_combat(
                combat_data=combat_data,
                participants=participants,
                environment_factors=environment_factors
            )
        else:
            # Log that we'd normally resolve combat here
            logger.info(f"Would resolve combat for {len(participants)} participants...")
            # Simulate complex calculations
            time.sleep(3)
            
            # Create mock combat results for development
            rounds = []
            for i in range(1, 4):  # Simulate 3 rounds
                round_actions = []
                for participant in participants:
                    damage = random.randint(0, 10)
                    action = {
                        'actor': participant.get('id', 'unknown'),
                        'target': participants[random.randint(0, len(participants)-1)].get('id', 'unknown'),
                        'action': random.choice(['attack', 'defend', 'special']),
                        'damage_dealt': damage,
                        'status_effects': []
                    }
                    round_actions.append(action)
                rounds.append({'round': i, 'actions': round_actions})
            
            # Determine outcome
            player_won = random.choice([True, False])
            results = {
                'rounds': rounds,
                'outcome': {
                    'victor': 'player' if player_won else 'opponents',
                    'rounds_total': len(rounds),
                    'decisive_moment': f"Round {random.randint(1, len(rounds))}"
                },
                'experience': {p.get('id', 'unknown'): random.randint(10, 50) for p in participants}
            }
        
        return {
            'combat_id': combat_data.get('id', 'unknown'),
            'rounds': results.get('rounds', []),
            'outcome': results.get('outcome', {}),
            'experience': results.get('experience', {}),
            'environment_impact': environment_factors,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Combat resolution failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
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
        logger.info(f"Updating reputation network for player {player_id} affecting {len(affected_factions)} factions...")
        
        # Simulate complex reputation calculations
        time.sleep(2)
        
        # Initialize reputation changes
        direct_changes = {}
        cascading_changes = {}
        
        # Mock faction relationships (in a real system, this would come from the database)
        faction_relationships = {
            'village': {'merchants_guild': 0.5, 'city_guard': 0.7},
            'merchants_guild': {'village': 0.5, 'thieves_guild': -0.8},
            'city_guard': {'village': 0.7, 'thieves_guild': -0.9},
            'thieves_guild': {'merchants_guild': -0.8, 'city_guard': -0.9}
        }
        
        # Calculate direct reputation changes
        for faction, impact in affected_factions.items():
            direct_changes[faction] = impact
            
            # Calculate cascading effects on related factions
            if faction in faction_relationships:
                for related_faction, relationship in faction_relationships[faction].items():
                    # Reputation change diminishes based on relationship strength
                    # Positive relationships cause similar changes, negative ones cause opposite
                    cascading_effect = impact * relationship * 0.5
                    
                    if related_faction in cascading_changes:
                        cascading_changes[related_faction] += cascading_effect
                    else:
                        cascading_changes[related_faction] = cascading_effect
        
        # Round cascading changes to reasonable values
        cascading_changes = {f: round(v, 2) for f, v in cascading_changes.items()}
        
        return {
            'player_id': player_id,
            'action_type': action_data.get('action_type', 'unknown'),
            'direct_changes': direct_changes,
            'cascading_changes': cascading_changes,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Reputation network update failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
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
    try:
        logger.info(f"Analyzing behavior patterns for player {player_id} over {time_period}...")
        
        # Simulate complex pattern analysis
        time.sleep(2.5)
        
        # Count action types
        action_counts = {}
        for action in action_history:
            action_type = action.get('action_type', 'unknown')
            if action_type in action_counts:
                action_counts[action_type] += 1
            else:
                action_counts[action_type] = 1
        
        # Find most common actions
        most_common = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Identify time patterns (mock analysis)
        time_patterns = []
        if len(action_history) > 10:
            if random.random() > 0.5:
                time_patterns.append("Player tends to engage in combat during evening hours")
            if random.random() > 0.5:
                time_patterns.append("Player explores new areas primarily in the morning")
            if random.random() > 0.5:
                time_patterns.append("Social interactions peak in afternoon sessions")
        
        # Detect play style
        combat_actions = sum(1 for a in action_history if a.get('action_type', '').startswith('COMBAT'))
        social_actions = sum(1 for a in action_history if a.get('action_type', '').startswith('SOCIAL'))
        exploration_actions = sum(1 for a in action_history if a.get('action_type', '').startswith('EXPLORE'))
        
        total_actions = len(action_history) or 1  # Avoid division by zero
        
        play_style = {
            'combat_focus': round(combat_actions / total_actions, 2),
            'social_focus': round(social_actions / total_actions, 2),
            'exploration_focus': round(exploration_actions / total_actions, 2)
        }
        
        # Determine primary play style
        max_style = max(play_style.items(), key=lambda x: x[1])
        primary_style = f"{max_style[0].replace('_focus', '').title()} focused"
        
        return {
            'player_id': player_id,
            'time_period': time_period,
            'action_counts': action_counts,
            'most_common_actions': most_common,
            'time_patterns': time_patterns,
            'play_style_metrics': play_style,
            'primary_play_style': primary_style,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Player pattern analysis failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def calculate_domain_synergies(self, domain_values, available_synergies):
    """
    Calculate complex domain synergies based on character attributes.
    
    Args:
        domain_values: Character's domain attribute values
        available_synergies: Available synergy types
        
    Returns:
        Calculated domain synergies
    """
    try:
        logger.info(f"Calculating domain synergies for {len(domain_values)} domains...")
        
        # Simulate complex synergy calculations
        time.sleep(1.5)
        
        # Calculate base synergies
        synergies = {}
        for synergy_type in available_synergies:
            # Get the domains involved in this synergy
            domains = synergy_type.get('domains', [])
            if len(domains) < 2:
                continue
                
            # Calculate the synergy value based on domain values
            domain_scores = [domain_values.get(d, 0) for d in domains]
            # Basic synergy formula: average of domains multiplied by a synergy factor
            synergy_value = (sum(domain_scores) / len(domain_scores)) * synergy_type.get('factor', 1.0)
            
            # Apply thresholds
            min_threshold = synergy_type.get('min_threshold', 0)
            if synergy_value >= min_threshold:
                synergies[synergy_type.get('name', 'unknown')] = round(synergy_value, 2)
        
        # Find the strongest synergies
        top_synergies = sorted(synergies.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'synergies': synergies,
            'top_synergies': top_synergies,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Domain synergy calculation failed: {exc}")
        self.retry(exc=exc)