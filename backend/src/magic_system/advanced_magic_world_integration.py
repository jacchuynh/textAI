"""
Advanced Magic World Integration

This module integrates advanced magic features with the world generator.
It enhances the magic world integration with environmental resonance,
dynamic spell effects based on location, and magical consequences.
"""

import random
import logging
from typing import Dict, List, Any, Optional, Tuple

from .magic_world_integration import MagicWorldIntegration
from .advanced_magic_features import (
    EnvironmentalMagicResonance, MagicSchool, ManaHeartStage,
    MagicalAffinity, Effect, CombatContext
)
from .magic_system import DamageType, MagicTier, MagicSource

# Configure logging
logger = logging.getLogger(__name__)


class AdvancedMagicWorldIntegration:
    """
    Integrates advanced magic features with the world generator.
    
    This class extends the basic magic world integration with:
    1. Environmental resonance effects on magic
    2. Dynamic magical events based on location conditions
    3. Advanced magical POI generation
    4. Seasonal magical effects
    5. Time-of-day magical properties
    """
    
    def __init__(self, basic_integration: MagicWorldIntegration):
        """
        Initialize advanced magic world integration
        
        Args:
            basic_integration: The basic magic world integration instance
        """
        self.basic_integration = basic_integration
        self.environmental_resonance = EnvironmentalMagicResonance()
        
        # Map biomes to environmental types for resonance calculations
        self.biome_to_environment_map = {
            'forest': 'forest',
            'mountain': 'mountain',
            'desert': 'desert',
            'coastal': 'ocean',
            'swamp': 'cave',  # Using cave for swamp as it's the closest match
            'plains': 'forest',  # Using forest for plains as it's somewhat similar
            'tundra': 'mountain',  # Using mountain for tundra
            'volcanic': 'volcano',
            'jungle': 'forest',
            'cave': 'cave'
        }
        
        # Map location types to possible emotional resonances
        self.location_type_to_emotions = {
            'battlefield': ['fear', 'hatred'],
            'graveyard': ['grief', 'fear'],
            'temple': ['love', 'joy'],
            'ruins': ['grief', 'fear'],
            'village': ['joy', 'love'],
            'settlement': ['joy'],
            'tower': ['fear'],
            'shrine': ['love', 'joy']
        }
        
        # Map magical aspects to damage types
        self.aspect_to_damage_type = {
            'FIRE': DamageType.FIRE,
            'WATER': DamageType.WATER,
            'EARTH': DamageType.EARTH,
            'AIR': DamageType.AIR,
            'ARCANE': DamageType.ARCANE,
            'LIGHT': DamageType.LIGHT,
            'DARKNESS': DamageType.DARKNESS,
            'LIFE': DamageType.LIFE,
            'DEATH': DamageType.NECROTIC,
            'POISON': DamageType.POISON,
            'ICE': DamageType.ICE,
            'LIGHTNING': DamageType.LIGHTNING
        }
    
    def enhance_location_with_advanced_magic(self, location) -> None:
        """
        Enhance a location with advanced magical features
        
        Args:
            location: The location to enhance
        """
        # Skip if location doesn't have a magic profile
        if not hasattr(location, 'magic_profile'):
            return
        
        # Add magical environment context for spell resonance
        self._add_magical_environment_context(location)
        
        # Add emotional resonance based on location type and history
        self._add_emotional_resonance(location)
        
        # Add historical magical events
        if location.magic_profile.leyline_strength > 1.0 and random.random() < 0.3:
            self._add_historical_magical_event(location)
        
        # Add time-of-day magical effects
        self._add_time_of_day_effects(location)
        
        # Add weather effects on magic
        self._add_weather_magic_effects(location)
        
        # Add seasonal magic influences
        self._add_seasonal_magic_effects(location)
    
    def _add_magical_environment_context(self, location) -> None:
        """
        Add magical environment context to a location for spell resonance
        
        Args:
            location: The location to enhance
        """
        # Initialize metadata if not present
        if not hasattr(location, 'metadata'):
            location.metadata = {}
        
        # Map biome to environment type
        if hasattr(location, 'biome') and location.biome in self.biome_to_environment_map:
            location.metadata['environment_type'] = self.biome_to_environment_map[location.biome]
        else:
            # Default to neutral environment
            location.metadata['environment_type'] = 'neutral'
        
        # Add magical stability based on leyline strength
        # Higher leyline strength = more stable magic, except at very high levels where it can become unstable
        if location.magic_profile.leyline_strength > 2.0:
            # Very high leyline strength can cause instability
            location.metadata['magical_stability'] = max(0.3, 1.0 - (location.magic_profile.leyline_strength - 2.0) * 0.2)
        else:
            # Normal stability increases with leyline strength
            location.metadata['magical_stability'] = min(1.0, 0.5 + location.magic_profile.leyline_strength * 0.25)
        
        # Add magical aspects as damage types for resonance
        location.metadata['magical_damage_types'] = []
        for aspect in location.magic_profile.dominant_magic_aspects:
            if aspect in self.aspect_to_damage_type:
                location.metadata['magical_damage_types'].append(self.aspect_to_damage_type[aspect])
    
    def _add_emotional_resonance(self, location) -> None:
        """
        Add emotional resonance to a location based on its type and history
        
        Args:
            location: The location to enhance
        """
        if not hasattr(location, 'metadata'):
            location.metadata = {}
        
        location.metadata['emotional_aura'] = []
        
        # Check POIs for emotional influences
        for poi in location.pois:
            poi_type = poi.poi_type.name.lower() if hasattr(poi.poi_type, 'name') else str(poi.poi_type).lower()
            
            # Look for emotional resonance based on POI type
            for location_type, emotions in self.location_type_to_emotions.items():
                if location_type in poi_type:
                    # Add emotions with some randomness
                    for emotion in emotions:
                        if random.random() < 0.7:  # 70% chance to add each emotion
                            if emotion not in location.metadata['emotional_aura']:
                                location.metadata['emotional_aura'].append(emotion)
        
        # Add random emotional resonance based on magic profile
        if location.magic_profile.leyline_strength > 1.0:
            potential_emotions = ['joy', 'fear', 'love', 'hatred', 'grief']
            selected_emotion = random.choice(potential_emotions)
            
            if selected_emotion not in location.metadata['emotional_aura']:
                location.metadata['emotional_aura'].append(selected_emotion)
    
    def _add_historical_magical_event(self, location) -> None:
        """
        Add a historical magical event to a location
        
        Args:
            location: The location to enhance
        """
        if not hasattr(location, 'metadata'):
            location.metadata = {}
        
        if not 'historical_events' in location.metadata:
            location.metadata['historical_events'] = []
        
        # Possible historical events
        events = [
            'ancient_ritual_site',
            'magical_disaster',
            'crimson_dissonance_site'
        ]
        
        # Higher chance for ancient ritual sites in high magic areas
        weights = [3, 1, 1]
        if location.magic_profile.leyline_strength > 1.5:
            weights = [2, 2, 3]  # More dangerous events in very high magic areas
        
        # Select a random event with weights
        chosen_event = random.choices(events, weights=weights, k=1)[0]
        location.metadata['historical_events'].append(chosen_event)
        
        # Add event description to location description
        event_descriptions = {
            'ancient_ritual_site': "Ancient magical symbols are etched into stones throughout this area, remnants of powerful rituals performed long ago.",
            'magical_disaster': "The very fabric of reality seems thin here, perhaps due to some magical catastrophe in the distant past.",
            'crimson_dissonance_site': "A faint crimson glow occasionally emanates from the ground here, echoing the magical disturbance known as the Crimson Dissonance."
        }
        
        # Append to location description if available
        if hasattr(location, 'description') and location.description:
            location.description += f" {event_descriptions[chosen_event]}"
    
    def _add_time_of_day_effects(self, location) -> None:
        """
        Add time-of-day effects to a location's magical properties
        
        Args:
            location: The location to enhance
        """
        if not hasattr(location, 'metadata'):
            location.metadata = {}
        
        # Time periods and their magical significance
        time_periods = ['dawn', 'noon', 'dusk', 'night', 'midnight']
        
        # Each location has a time period where magic is strongest
        dominant_time = random.choice(time_periods)
        location.metadata['peak_magic_time'] = dominant_time
        
        # Add special magical features that only manifest at certain times
        special_time_features = {
            'dawn': "Spells of divination and restoration are more powerful at dawn in this location.",
            'noon': "Fire and light magic reach their peak potency at noon here.",
            'dusk': "Illusions and enchantments cast at dusk have increased effectiveness in this area.",
            'night': "Darkness and necromantic energies flow more freely at night in this location.",
            'midnight': "The veil between worlds thins at midnight here, empowering necromancy but weakening light magic."
        }
        
        location.metadata['time_magic_feature'] = special_time_features[dominant_time]
    
    def _add_weather_magic_effects(self, location) -> None:
        """
        Add weather-related magical effects to a location
        
        Args:
            location: The location to enhance
        """
        if not hasattr(location, 'metadata'):
            location.metadata = {}
        
        # Base weather types
        weather_types = ['clear', 'cloudy', 'rain', 'storm', 'fog', 'snow']
        
        # Select predominant weather based on biome
        biome_to_weather = {
            'forest': ['clear', 'cloudy', 'rain'],
            'mountain': ['clear', 'cloudy', 'snow', 'storm'],
            'desert': ['clear', 'cloudy'],
            'coastal': ['clear', 'cloudy', 'rain', 'fog', 'storm'],
            'swamp': ['cloudy', 'rain', 'fog'],
            'plains': ['clear', 'cloudy', 'storm'],
            'tundra': ['clear', 'cloudy', 'snow', 'storm'],
            'jungle': ['cloudy', 'rain', 'storm'],
            'volcanic': ['clear', 'cloudy', 'ash_fall'],
            'cave': ['fog']
        }
        
        # Get potential weather for this biome
        if hasattr(location, 'biome') and location.biome in biome_to_weather:
            potential_weather = biome_to_weather[location.biome]
        else:
            potential_weather = weather_types
        
        # Set current weather (for demo purposes)
        location.metadata['weather'] = random.choice(potential_weather)
        
        # Add magical affinity for certain weather conditions
        location.metadata['weather_magic_affinities'] = {}
        for aspect in location.magic_profile.dominant_magic_aspects:
            # Map aspects to preferred weather
            aspect_weather_map = {
                'FIRE': ['clear'],
                'WATER': ['rain', 'fog'],
                'EARTH': ['clear', 'cloudy'],
                'AIR': ['cloudy', 'storm'],
                'ARCANE': ['clear'],
                'LIGHT': ['clear'],
                'DARKNESS': ['cloudy', 'fog'],
                'LIFE': ['rain', 'clear'],
                'DEATH': ['fog'],
                'POISON': ['fog', 'rain'],
                'ICE': ['snow'],
                'LIGHTNING': ['storm']
            }
            
            if aspect in aspect_weather_map:
                for weather in aspect_weather_map[aspect]:
                    location.metadata['weather_magic_affinities'][weather] = aspect
    
    def _add_seasonal_magic_effects(self, location) -> None:
        """
        Add seasonal influences on magical properties
        
        Args:
            location: The location to enhance
        """
        if not hasattr(location, 'metadata'):
            location.metadata = {}
        
        # Seasons
        seasons = ['spring', 'summer', 'autumn', 'winter']
        
        # Each location has a season where magic is strongest
        dominant_season = random.choice(seasons)
        location.metadata['peak_magic_season'] = dominant_season
        
        # Add seasonal magic effects
        seasonal_magic_effects = {
            'spring': {
                'enhanced_aspects': ['LIFE', 'WATER', 'AIR'],
                'diminished_aspects': ['DEATH', 'FIRE', 'ICE'],
                'description': "Life and renewal magic flourish in spring, while death magic wanes."
            },
            'summer': {
                'enhanced_aspects': ['FIRE', 'LIGHT', 'AIR'],
                'diminished_aspects': ['ICE', 'DARKNESS', 'WATER'],
                'description': "Fire and light magic reach their peak in summer heat."
            },
            'autumn': {
                'enhanced_aspects': ['EARTH', 'DEATH', 'AIR'],
                'diminished_aspects': ['LIFE', 'WATER', 'FIRE'],
                'description': "Magic tied to transformation and decay grows stronger in autumn."
            },
            'winter': {
                'enhanced_aspects': ['ICE', 'DARKNESS', 'WATER'],
                'diminished_aspects': ['FIRE', 'LIFE', 'LIGHT'],
                'description': "Ice and preservation magic dominate in winter's grasp."
            }
        }
        
        location.metadata['seasonal_magic'] = seasonal_magic_effects[dominant_season]
    
    def calculate_spell_effectiveness(self, spell, location, time_of_day='day', season='summer'):
        """
        Calculate how effective a spell would be at this location under given conditions
        
        Args:
            spell: The spell being cast
            location: The location where the spell is cast
            time_of_day: The time of day
            season: The current season
            
        Returns:
            A modifier to spell power (1.0 is baseline) and a description of effects
        """
        # Create a location context for the environmental resonance system
        location_context = {
            'time': time_of_day,
            'weather': location.metadata.get('weather', 'clear'),
            'environment_type': location.metadata.get('environment_type', 'neutral'),
            'magical_stability': location.metadata.get('magical_stability', 1.0),
            'emotional_aura': location.metadata.get('emotional_aura', []),
            'historical_events': location.metadata.get('historical_events', [])
        }
        
        # Calculate the base modifier
        modifier = self.environmental_resonance.calculate_spell_power_modifier(spell, location_context)
        
        # Apply seasonal modifiers
        if hasattr(location, 'metadata') and 'seasonal_magic' in location.metadata:
            seasonal_magic = location.metadata['seasonal_magic']
            
            # Check if spell uses enhanced aspects
            for aspect in seasonal_magic['enhanced_aspects']:
                if aspect in spell.magic_source_affinity:
                    modifier += 0.2
                    break
            
            # Check if spell uses diminished aspects
            for aspect in seasonal_magic['diminished_aspects']:
                if aspect in spell.magic_source_affinity:
                    modifier -= 0.2
                    break
        
        # Apply time of day peak magic modifier
        if (hasattr(location, 'metadata') and 'peak_magic_time' in location.metadata and 
            location.metadata['peak_magic_time'] == time_of_day):
            modifier += 0.3
        
        # Generate description of effects
        description = self._generate_spell_effectiveness_description(modifier, location, time_of_day, season)
        
        return modifier, description
    
    def _generate_spell_effectiveness_description(self, modifier, location, time_of_day, season):
        """
        Generate a description of spell effectiveness based on the modifier
        
        Args:
            modifier: The calculated modifier
            location: The location
            time_of_day: The time of day
            season: The current season
            
        Returns:
            A string describing the effects
        """
        location_name = getattr(location, 'name', 'this location')
        
        if modifier > 1.5:
            return f"Magic surges with extraordinary power in {location_name} during {time_of_day} in {season}. Spells cast here are significantly amplified, but may be harder to control."
        elif modifier > 1.2:
            return f"The magical energies in {location_name} are particularly conducive during {time_of_day} in {season}, enhancing spell effectiveness."
        elif modifier > 0.8:
            return f"Magic flows normally in {location_name} during {time_of_day} in {season}."
        elif modifier > 0.5:
            return f"Something in {location_name} during {time_of_day} in {season} slightly impedes the flow of magic, reducing spell effectiveness."
        else:
            return f"Magic is severely dampened in {location_name} during {time_of_day} in {season}. Spells will be much weaker than normal."


def enhance_world_with_advanced_magic(world):
    """
    Enhance a world with advanced magical features
    
    Args:
        world: The world to enhance
        
    Returns:
        The enhanced world
    """
    # First apply basic magic enhancements
    basic_integration = MagicWorldIntegration()
    basic_integration.enhance_world_with_magic(world)
    
    # Then apply advanced magic features
    advanced_integration = AdvancedMagicWorldIntegration(basic_integration)
    
    # Enhance each location with advanced features
    for location_id, location in world.locations.items():
        advanced_integration.enhance_location_with_advanced_magic(location)
    
    return world