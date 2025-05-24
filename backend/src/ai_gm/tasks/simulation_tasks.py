"""
Simulation-related tasks for AI GM Brain.

This module contains Celery tasks for handling world simulation,
environmental effects, and ambient content generation.
"""

from backend.src.ai_gm.tasks.celery_app import celery_app
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Attempt to import the world reaction components if available
try:
    from backend.src.ai_gm.world_reaction.reaction_assessor import ReactionAssessor
    from backend.src.ai_gm.pacing.pacing_manager import PacingManager
    world_reaction_available = True
except ImportError:
    logger.warning("World reaction components not available. Using mock responses for development.")
    world_reaction_available = False

@celery_app.task(bind=True, max_retries=3)
def process_world_reaction(self, action_data, world_context):
    """
    Process player action and calculate world reaction.
    
    Args:
        action_data: Details of the player's action
        world_context: Current world state
        
    Returns:
        World reaction results
    """
    try:
        action_type = action_data.get('action_type', 'unknown')
        logger.info(f"Processing world reaction for action type: {action_type}...")
        
        start_time = datetime.utcnow()
        
        if world_reaction_available:
            # Use the actual world reaction system
            reaction_assessor = ReactionAssessor()
            reaction = reaction_assessor.assess_reaction(
                action=action_data,
                context=world_context
            )
        else:
            # Simulate processing time for complex world reactions
            time.sleep(2)
            
            # Create mock world reaction for development
            # In a real implementation, this would be calculated based on the action and context
            reaction = {
                'immediate_effects': [
                    "The shopkeeper frowns at your haggling attempt",
                    "A nearby guard takes notice of the commotion"
                ],
                'delayed_effects': [
                    "Word may spread about your negotiation tactics",
                    "Merchants in this district might be more wary of you"
                ],
                'reputation_changes': {
                    'merchant_guild': -2,
                    'city_watch': -1
                },
                'environment_changes': {
                    'market_atmosphere': 'tense',
                    'guard_presence': 'increased'
                },
                'probability_future_events': [
                    {'event': 'merchant_warning', 'probability': 0.7},
                    {'event': 'guard_questioning', 'probability': 0.3}
                ]
            }
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the world reaction results with metadata
        return {
            'reaction': reaction,
            'action_type': action_type,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"World reaction processing failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def generate_ambient_content(self, location, time_of_day, recent_events, mood=None):
    """
    Generate ambient content for a location.
    
    Args:
        location: The game location
        time_of_day: Current time of day
        recent_events: Recent events in the game
        mood: Optional mood/tone for the content
        
    Returns:
        Generated ambient content
    """
    try:
        logger.info(f"Generating ambient content for location: {location}, time: {time_of_day}...")
        
        start_time = datetime.utcnow()
        
        if world_reaction_available:
            # Use the actual pacing system
            pacing_manager = PacingManager()
            content = pacing_manager.generate_ambient_content(
                location=location,
                time_of_day=time_of_day,
                recent_events=recent_events,
                mood=mood
            )
        else:
            # Simulate processing time for ambient content generation
            time.sleep(1.5)
            
            # Create mock ambient content for development
            weather_conditions = {
                'morning': ['misty', 'clear', 'light rain'],
                'afternoon': ['sunny', 'partly cloudy', 'windy'],
                'evening': ['golden sunset', 'cloudy', 'light fog'],
                'night': ['starry', 'moonlit', 'heavy fog', 'stormy']
            }
            
            npc_activities = {
                'town_square': ['merchants hawking wares', 'children playing', 'musicians performing'],
                'tavern': ['patrons drinking', 'bard performing', 'card games in progress'],
                'forest': ['birds chirping', 'rustling leaves', 'distant animal calls'],
                'castle': ['guards patrolling', 'servants hurrying', 'nobles conversing'],
                'dungeon': ['water dripping', 'distant echoes', 'scurrying rats']
            }
            
            # Select appropriate conditions based on inputs
            import random
            weather = random.choice(weather_conditions.get(time_of_day, ['normal']))
            activities = npc_activities.get(location, ['normal activity'])
            activity = random.choice(activities)
            
            # Generate different content based on mood if provided
            ambient_description = ""
            if mood == 'tense':
                ambient_description = f"The {weather} {time_of_day} brings an uneasy atmosphere to the {location}. {activity}, but there's tension in the air."
            elif mood == 'peaceful':
                ambient_description = f"A {weather} {time_of_day} blankets the {location} in tranquility. {activity}, adding to the peaceful ambiance."
            elif mood == 'mysterious':
                ambient_description = f"The {weather} {time_of_day} casts eerie shadows across the {location}. {activity}, but something feels off..."
            else:
                ambient_description = f"A {weather} {time_of_day} in the {location}. {activity} as usual."
            
            # Create background elements
            background_sounds = ["distant conversation", "wind through trees", "creaking floorboards"]
            background_smells = ["cooking food", "burning torches", "fresh rain"]
            
            # Incorporate recent events if available
            event_references = []
            if recent_events and len(recent_events) > 0:
                recent_event = recent_events[0]
                event_references.append(f"People are still talking about {recent_event}.")
            
            # Combine all elements
            content = {
                'ambient_description': ambient_description,
                'background_elements': {
                    'sounds': random.choice(background_sounds),
                    'smells': random.choice(background_smells)
                },
                'npc_activities': activity,
                'event_references': event_references
            }
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Return the ambient content with metadata
        return {
            'content': content,
            'location': location,
            'time_of_day': time_of_day,
            'mood': mood,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"Ambient content generation failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(bind=True)
def simulate_npc_movements(self, location_id, time_of_day, npcs):
    """
    Simulate NPC movements and activities in a location.
    
    Args:
        location_id: The location identifier
        time_of_day: Current time of day
        npcs: List of NPCs in the location
        
    Returns:
        Updated NPC positions and activities
    """
    try:
        logger.info(f"Simulating NPC movements for {len(npcs)} NPCs in {location_id}...")
        
        # Simulate processing time
        time.sleep(1)
        
        # Create schedule templates based on time of day
        schedule_templates = {
            'morning': {
                'merchant': ['opening_shop', 'arranging_goods', 'serving_customers'],
                'guard': ['patrol', 'shift_change', 'inspection'],
                'commoner': ['breakfast', 'walking_to_work', 'shopping']
            },
            'afternoon': {
                'merchant': ['serving_customers', 'inventory', 'lunch_break'],
                'guard': ['patrol', 'training', 'watching_crowds'],
                'commoner': ['working', 'lunch', 'errands']
            },
            'evening': {
                'merchant': ['closing_shop', 'counting_earnings', 'heading_home'],
                'guard': ['patrol', 'lighting_torches', 'shift_change'],
                'commoner': ['heading_home', 'tavern_visit', 'dinner']
            },
            'night': {
                'merchant': ['sleeping', 'inventory', 'ledger_work'],
                'guard': ['night_watch', 'patrol', 'guarding_gate'],
                'commoner': ['sleeping', 'tavern_drinking', 'stargazing']
            }
        }
        
        # Location zones define where NPCs can be
        location_zones = {
            'town_square': ['fountain', 'market_stalls', 'benches', 'stage'],
            'tavern': ['bar', 'tables', 'stage', 'kitchen', 'rooms'],
            'castle': ['courtyard', 'great_hall', 'barracks', 'gardens', 'towers'],
            'forest': ['clearing', 'dense_trees', 'stream', 'path', 'campsite'],
            'dungeon': ['entrance', 'cells', 'guard_room', 'torture_chamber', 'storage']
        }
        
        # Get zones for the current location
        zones = location_zones.get(location_id, ['main_area'])
        
        # Update each NPC
        updated_npcs = []
        for npc in npcs:
            npc_type = npc.get('type', 'commoner')
            npc_id = npc.get('id', 'unknown')
            
            # Get appropriate schedule for the NPC type and time of day
            possible_activities = schedule_templates.get(time_of_day, {}).get(npc_type, ['idle'])
            
            import random
            # Choose a random activity and zone
            activity = random.choice(possible_activities)
            zone = random.choice(zones)
            
            # Update the NPC's activity and position
            updated_npc = npc.copy()
            updated_npc['current_activity'] = activity
            updated_npc['current_zone'] = zone
            updated_npc['last_updated'] = datetime.utcnow().isoformat()
            
            # Add some randomness to make NPCs more dynamic
            if random.random() < 0.2:  # 20% chance of special behavior
                special_behaviors = [
                    'talking_to_another_npc',
                    'looking_for_something',
                    'taking_a_break',
                    'observing_player'
                ]
                updated_npc['special_behavior'] = random.choice(special_behaviors)
            
            updated_npcs.append(updated_npc)
        
        return {
            'location_id': location_id,
            'time_of_day': time_of_day,
            'npcs': updated_npcs,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as exc:
        logger.error(f"NPC movement simulation failed: {exc}")
        raise self.retry(exc=exc)

@celery_app.task
def simulate_weather_changes(self, current_weather, region, season, days_elapsed):
    """
    Simulate weather changes over time.
    
    Args:
        current_weather: Current weather condition
        region: Geographic region in the game world
        season: Current season
        days_elapsed: Days elapsed since last weather update
        
    Returns:
        Updated weather conditions
    """
    logger.info(f"Simulating weather changes for {region} in {season}...")
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Weather patterns by region and season
    weather_patterns = {
        'northern_plains': {
            'spring': ['light_rain', 'moderate_rain', 'cloudy', 'clear', 'foggy'],
            'summer': ['clear', 'hot', 'thunderstorm', 'windy', 'hazy'],
            'fall': ['cloudy', 'windy', 'light_rain', 'foggy', 'clear'],
            'winter': ['snow', 'blizzard', 'freezing', 'overcast', 'sleet']
        },
        'coastal_region': {
            'spring': ['misty', 'light_rain', 'moderate_rain', 'clear', 'windy'],
            'summer': ['clear', 'hot', 'sea_breeze', 'tropical_storm', 'humid'],
            'fall': ['windy', 'stormy', 'heavy_rain', 'misty', 'clear'],
            'winter': ['cold_rain', 'sleet', 'windy', 'overcast', 'light_snow']
        },
        'mountain_range': {
            'spring': ['foggy', 'light_rain', 'clear', 'windy', 'hail'],
            'summer': ['clear', 'thunderstorm', 'warm', 'foggy', 'windy'],
            'fall': ['windy', 'foggy', 'light_snow', 'clear', 'overcast'],
            'winter': ['blizzard', 'heavy_snow', 'freezing', 'clear_freezing', 'avalanche_risk']
        },
        'forest_lands': {
            'spring': ['light_rain', 'moderate_rain', 'pollen_filled', 'clear', 'misty'],
            'summer': ['humid', 'clear', 'hot', 'thunderstorm', 'misty_morning'],
            'fall': ['foggy', 'light_rain', 'windy', 'clear', 'overcast'],
            'winter': ['light_snow', 'moderate_snow', 'freezing', 'overcast', 'clear_cold']
        }
    }
    
    # Default to forest_lands if region not recognized
    region_patterns = weather_patterns.get(region, weather_patterns['forest_lands'])
    # Default to summer if season not recognized
    season_patterns = region_patterns.get(season, region_patterns['summer'])
    
    import random
    
    # Weather persistence - weather tends to persist or change gradually
    # Determine if weather will change based on days elapsed
    change_probability = min(0.3 * days_elapsed, 0.9)  # Max 90% chance
    
    will_change = random.random() < change_probability
    
    if will_change:
        # Choose new weather, weighted toward weather similar to current
        if current_weather in season_patterns:
            # Find current weather index
            current_index = season_patterns.index(current_weather)
            # Weighted random choice - more likely to pick nearby indices
            weights = []
            for i in range(len(season_patterns)):
                # Calculate distance from current index (with wrap-around)
                distance = min(abs(i - current_index), len(season_patterns) - abs(i - current_index))
                # Higher weight for smaller distances
                weights.append(1.0 / (distance + 1))
            # Normalize weights
            total = sum(weights)
            weights = [w/total for w in weights]
            # Choose new weather based on weights
            new_weather = random.choices(season_patterns, weights=weights)[0]
        else:
            # If current weather not in patterns, just pick random
            new_weather = random.choice(season_patterns)
    else:
        # Weather stays the same
        new_weather = current_weather
    
    # Generate weather details
    weather_details = {}
    
    if 'rain' in new_weather:
        weather_details['precipitation'] = {
            'type': 'rain',
            'intensity': 'light' if 'light' in new_weather else 'moderate' if 'moderate' in new_weather else 'heavy'
        }
    elif 'snow' in new_weather:
        weather_details['precipitation'] = {
            'type': 'snow',
            'intensity': 'light' if 'light' in new_weather else 'moderate' if 'moderate' in new_weather else 'heavy'
        }
    elif 'sleet' in new_weather:
        weather_details['precipitation'] = {
            'type': 'sleet',
            'intensity': 'moderate'
        }
    elif 'hail' in new_weather:
        weather_details['precipitation'] = {
            'type': 'hail',
            'intensity': 'moderate'
        }
    
    if 'windy' in new_weather:
        weather_details['wind'] = {
            'speed': random.randint(20, 40),
            'direction': random.choice(['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'])
        }
    elif 'storm' in new_weather:
        weather_details['wind'] = {
            'speed': random.randint(40, 70),
            'direction': random.choice(['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'])
        }
    else:
        weather_details['wind'] = {
            'speed': random.randint(5, 15),
            'direction': random.choice(['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'])
        }
    
    # Temperature depends on season and weather
    base_temp = {
        'winter': random.randint(-10, 10),
        'spring': random.randint(5, 25),
        'summer': random.randint(20, 35),
        'fall': random.randint(5, 20)
    }.get(season, random.randint(10, 25))
    
    # Adjust temperature based on weather
    if 'cold' in new_weather or 'freezing' in new_weather:
        base_temp -= random.randint(5, 15)
    elif 'hot' in new_weather:
        base_temp += random.randint(5, 15)
    
    weather_details['temperature'] = base_temp
    
    # Cloud cover
    if 'clear' in new_weather:
        weather_details['cloud_cover'] = random.randint(0, 20)
    elif 'cloudy' in new_weather or 'overcast' in new_weather:
        weather_details['cloud_cover'] = random.randint(70, 100)
    else:
        weather_details['cloud_cover'] = random.randint(30, 70)
    
    # Special effects
    special_effects = []
    if 'foggy' in new_weather or 'misty' in new_weather:
        special_effects.append('fog')
    if 'thunderstorm' in new_weather:
        special_effects.append('lightning')
    if 'rainbow' in new_weather:
        special_effects.append('rainbow')
    if 'avalanche_risk' in new_weather:
        special_effects.append('avalanche_risk')
    
    # Gameplay effects - weather might impact gameplay
    gameplay_effects = []
    if 'heavy_rain' in new_weather or 'thunderstorm' in new_weather or 'blizzard' in new_weather:
        gameplay_effects.append('reduced_visibility')
    if 'windy' in new_weather and weather_details['wind']['speed'] > 30:
        gameplay_effects.append('difficulty_with_projectiles')
    if base_temp < 0:
        gameplay_effects.append('freezing_conditions')
    if 'hot' in new_weather and base_temp > 30:
        gameplay_effects.append('heat_exhaustion_risk')
    
    return {
        'weather_type': new_weather,
        'region': region,
        'season': season,
        'details': weather_details,
        'special_effects': special_effects,
        'gameplay_effects': gameplay_effects,
        'forecast_days': random.randint(1, 3),  # How long this weather will likely last
        'timestamp': datetime.utcnow().isoformat()
    }