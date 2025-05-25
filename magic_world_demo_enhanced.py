"""
Magic World Demo (Enhanced Version)

This script demonstrates how the magic system integrates with the world generator
to create a rich, magical world with leylines, magical POIs, and material deposits.
The enhanced version includes advanced magic features like environmental resonance.
"""

import random
import uuid
import logging
from enum import Enum, auto
from typing import Dict, List, Any, Tuple, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from backend package if available
try:
    from backend.src.magic_system.magic_world_integration import MagicWorldIntegration, MagicalMaterialWorldIntegration
    from backend.src.magic_system.advanced_magic_world_integration import AdvancedMagicWorldIntegration, enhance_world_with_advanced_magic
    from backend.src.magic_system.magic_crafting_seed import seed_magical_materials
    logger.info("Using magic system components from backend package")
except ImportError:
    logger.warning("Could not import from backend package, using local classes")


# === Simple World Model ===

class Climate(Enum):
    TEMPERATE = auto()
    TROPICAL = auto()
    ARID = auto()
    ARCTIC = auto()


class Terrain(Enum):
    FLAT = auto()
    HILLS = auto()
    MOUNTAINS = auto()
    COASTAL = auto()
    RIVER = auto()


class POIType(Enum):
    VILLAGE = auto()
    RUIN = auto()
    CAVE = auto()
    SHRINE = auto()
    TOWER = auto()
    BRIDGE = auto()
    CAMP = auto()
    SETTLEMENT = auto()
    MINE = auto()
    GROVE = auto()
    SPRING = auto()
    RELIC_SITE = auto()
    FARM = auto()


class DamageType(Enum):
    FIRE = auto()
    WATER = auto()
    EARTH = auto()
    AIR = auto()
    ARCANE = auto()
    LIGHT = auto()
    DARKNESS = auto()
    LIFE = auto()
    DEATH = auto()
    POISON = auto()
    ICE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()


class ManaFluxLevel(Enum):
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()


class POI:
    def __init__(self, id, name, poi_type, description, coordinates):
        self.id = id
        self.name = name
        self.poi_type = poi_type
        self.description = description
        self.coordinates = coordinates
        self.metadata = {}


class LocationMagicProfile:
    def __init__(self, leyline_strength, mana_flux_level, dominant_magic_aspects, allows_ritual_sites):
        self.leyline_strength = leyline_strength
        self.mana_flux_level = mana_flux_level
        self.dominant_magic_aspects = dominant_magic_aspects
        self.allows_ritual_sites = allows_ritual_sites


class Location:
    def __init__(self, id, name, description, coordinates, terrain, pois, biome):
        self.id = id
        self.name = name
        self.description = description
        self.coordinates = coordinates
        self.terrain = terrain
        self.pois = pois
        self.biome = biome
        # Magic profile will be added later
        self.metadata = {}


class World:
    def __init__(self, id, name, width, height, locations, climate):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.locations = locations
        self.climate = climate
        self.leylines = []
        self.hotspots = []


# Only define these classes if we couldn't import them from the backend package
if 'MagicWorldIntegration' not in globals():
    # === Magic World Integration ===
    class MagicWorldIntegration:
        def __init__(self):
            """Initialize the magic world integration"""
            # Mapping of biome types to likely magic aspects
            self.biome_magic_mapping = {
                'forest': ['EARTH', 'LIFE'],
                'mountain': ['EARTH', 'AIR'],
                'desert': ['FIRE', 'EARTH'],
                'coastal': ['WATER', 'AIR'],
                'swamp': ['WATER', 'POISON'],
                'plains': ['EARTH', 'LIFE'],
                'tundra': ['ICE', 'AIR']
            }
            
            # POI types that can be associated with different magic aspects
            self.magical_poi_types = {
                'SHRINE': {
                    'FIRE': "Fire Shrine",
                    'WATER': "Water Shrine",
                    'EARTH': "Earth Shrine",
                    'AIR': "Air Shrine",
                    'ARCANE': "Arcane Shrine",
                    'LIFE': "Life Shrine",
                    'DEATH': "Death Shrine",
                    'POISON': "Poison Shrine",
                    'ICE': "Ice Shrine"
                },
                'GROVE': {
                    'LIFE': "Verdant Grove",
                    'EARTH': "Ancient Grove",
                    'DEATH': "Withered Grove",
                    'POISON': "Toxic Grove"
                },
                'SPRING': {
                    'WATER': "Eternal Water Spring",
                    'LIFE': "Healing Spring",
                    'POISON': "Eternal Poison Spring",
                    'ICE': "Eternal Ice Spring"
                },
                'RELIC_SITE': {
                    'ARCANE': "Forgotten Ruins",
                    'FIRE': "Scorched Ruins",
                    'WATER': "Sunken Temple",
                    'EARTH': "Earthen Monument",
                    'AIR': "Sky Pillar",
                    'LIFE': "Overgrown Sanctuary",
                    'DEATH': "Desolate Ruins",
                    'POISON': "Corrupted Shrine",
                    'ICE': "Frozen Relics"
                }
            }
        
        def enhance_world_with_magic(self, world):
            """
            Enhance a world with magical features
            
            Args:
                world: The world to enhance
            """
            # Add magic profiles to locations
            for location_id, location in world.locations.items():
                self._add_magic_profile(location)
            
            # Create leylines connecting locations
            self._create_leyline_network(world)
            
            # Create magical hotspots
            self._create_magical_hotspots(world)
            
            # Add magical POIs to locations
            for location_id, location in world.locations.items():
                self._add_magical_pois(location)
            
            return world
        
        def _add_magic_profile(self, location):
            """Add a magic profile to a location based on its biome"""
            # Base magic profile with low values
            leyline_strength = 0.1  # Will be modified by leylines later
            mana_flux_level = ManaFluxLevel.LOW
            allows_ritual_sites = False
            
            # Determine dominant magic aspects based on biome
            dominant_magic_aspects = []
            if hasattr(location, 'biome') and location.biome in self.biome_magic_mapping:
                dominant_magic_aspects = self.biome_magic_mapping[location.biome]
            else:
                # Default to random aspects if biome not recognized
                all_aspects = list(DamageType.__members__.keys())
                dominant_magic_aspects = random.sample(all_aspects, 2)
            
            # Create magic profile
            location.magic_profile = LocationMagicProfile(
                leyline_strength=leyline_strength,
                mana_flux_level=mana_flux_level,
                dominant_magic_aspects=dominant_magic_aspects,
                allows_ritual_sites=allows_ritual_sites
            )
        
        def _create_leyline_network(self, world):
            """Create a network of leylines connecting locations"""
            locations = list(world.locations.values())
            
            # Determine number of leylines based on world size
            num_leylines = max(1, len(locations) // 3)
            
            for _ in range(num_leylines):
                # Select two random locations to connect
                loc1, loc2 = random.sample(locations, 2)
                
                # Create a leyline between them
                leyline = {
                    'id': f"leyline_{uuid.uuid4().hex[:8]}",
                    'start_location_id': loc1.id,
                    'end_location_id': loc2.id,
                    'strength': random.uniform(0.5, 1.5)
                }
                
                # Add to world
                world.leylines.append(leyline)
                
                # Enhance magic profiles of connected locations
                loc1.magic_profile.leyline_strength += leyline['strength']
                loc2.magic_profile.leyline_strength += leyline['strength']
            
            # Update mana flux levels based on leyline strength
            for location in locations:
                if location.magic_profile.leyline_strength < 0.5:
                    location.magic_profile.mana_flux_level = ManaFluxLevel.LOW
                elif location.magic_profile.leyline_strength < 1.0:
                    location.magic_profile.mana_flux_level = ManaFluxLevel.MEDIUM
                elif location.magic_profile.leyline_strength < 1.5:
                    location.magic_profile.mana_flux_level = ManaFluxLevel.HIGH
                else:
                    location.magic_profile.mana_flux_level = ManaFluxLevel.VERY_HIGH
                    location.magic_profile.allows_ritual_sites = True
        
        def _create_magical_hotspots(self, world):
            """Create magical hotspots at leyline intersections"""
            # Find locations with multiple leylines
            location_leyline_count = {}
            
            for leyline in world.leylines:
                start_id = leyline['start_location_id']
                end_id = leyline['end_location_id']
                
                location_leyline_count[start_id] = location_leyline_count.get(start_id, 0) + 1
                location_leyline_count[end_id] = location_leyline_count.get(end_id, 0) + 1
            
            # Locations with 2+ leylines become hotspots
            for location_id, count in location_leyline_count.items():
                if count >= 2:
                    location = world.locations[location_id]
                    
                    # Create a hotspot
                    hotspot = {
                        'id': f"hotspot_{uuid.uuid4().hex[:8]}",
                        'location_id': location_id,
                        'strength': location.magic_profile.leyline_strength * 1.5
                    }
                    
                    # Further enhance the location's magic
                    location.magic_profile.leyline_strength = hotspot['strength']
                    location.magic_profile.mana_flux_level = ManaFluxLevel.VERY_HIGH
                    location.magic_profile.allows_ritual_sites = True
                    
                    # Add to world
                    world.hotspots.append(hotspot)
        
        def _add_magical_pois(self, location):
            """Add magical POIs to a location based on its magic profile"""
            # Skip if location has no magic profile
            if not hasattr(location, 'magic_profile'):
                return
            
            # Higher chance of magical POIs in high-magic areas
            num_magical_pois = 0
            if location.magic_profile.mana_flux_level == ManaFluxLevel.VERY_HIGH:
                num_magical_pois = random.randint(2, 4)
            elif location.magic_profile.mana_flux_level == ManaFluxLevel.HIGH:
                num_magical_pois = random.randint(1, 3)
            elif location.magic_profile.mana_flux_level == ManaFluxLevel.MEDIUM:
                num_magical_pois = random.randint(0, 2)
            else:
                # Low mana flux has small chance of magical POI
                num_magical_pois = random.randint(0, 1)
            
            # Add magical POIs
            for _ in range(num_magical_pois):
                # Select POI type
                poi_type = random.choice(list(self.magical_poi_types.keys()))
                poi_type_enum = POIType[poi_type]
                
                # Select a magic aspect from the location's dominant aspects
                aspect = random.choice(location.magic_profile.dominant_magic_aspects)
                
                # Generate name and description
                name, description = self._generate_magical_poi_details(poi_type, aspect, location.biome)
                
                # Create the POI
                poi = POI(
                    id=f"poi_{uuid.uuid4().hex[:8]}",
                    name=name,
                    poi_type=poi_type_enum,
                    description=description,
                    coordinates=(
                        location.coordinates[0] + random.uniform(-0.5, 0.5),
                        location.coordinates[1] + random.uniform(-0.5, 0.5)
                    )
                )
                
                # Add to location
                location.pois.append(poi)
        
        def _generate_magical_poi_details(self, poi_type, aspect, biome):
            """Generate a name and description for a magical POI"""
            # Get the name based on POI type and aspect
            if aspect in self.magical_poi_types[poi_type]:
                name = self.magical_poi_types[poi_type][aspect]
            else:
                # Fallback if no specific name for this aspect
                prefix = random.choice(["Sacred", "Forgotten", "Ancient", "Mystical", "Enchanted"])
                name = f"{prefix} {poi_type.title()}"
            
            # Generate a description based on POI type
            descriptions = {
                'SHRINE': f"A shrine dedicated to the power of {aspect.lower()}. The air here feels charged with magical energy.",
                'GROVE': f"A sacred grove where the trees seem to whisper ancient secrets. The foliage glows faintly at night.",
                'SPRING': f"A spring whose waters are infused with {aspect.lower()} energy, said to grant magical insights to those who drink.",
                'RELIC_SITE': f"The remains of an ancient magical site. Powerful artifacts may still be buried beneath the rubble."
            }
            
            description = descriptions.get(poi_type, f"A magical location infused with {aspect.lower()} energy.")
            
            return name, description

    class MagicalMaterialWorldIntegration:
        def __init__(self, magic_integration):
            """
            Initialize the magical material world integration
            
            Args:
                magic_integration: The magic world integration instance
            """
            self.magic_integration = magic_integration
            self.materials = self._get_mock_materials()
        
        def _get_mock_materials(self):
            """Get mock magical materials for demonstration"""
            return [
                {
                    "id": "luminite_crystal",
                    "name": "Luminite Crystal",
                    "rarity": "uncommon",
                    "magical_affinity": ["LIGHT"],
                    "leyline_resonance": 1.4,
                    "primary_locations": ["mountain", "cave"],
                    "magical_aspect": "light"
                },
                {
                    "id": "fire_crystal",
                    "name": "Fire Crystal",
                    "rarity": "uncommon",
                    "magical_affinity": ["FIRE"],
                    "leyline_resonance": 1.5,
                    "primary_locations": ["volcanic", "mountain", "hot_springs"],
                    "magical_aspect": "fire"
                },
                {
                    "id": "aqua_essence_gem",
                    "name": "Aqua Essence Gem",
                    "rarity": "uncommon",
                    "magical_affinity": ["WATER"],
                    "leyline_resonance": 1.4,
                    "primary_locations": ["coastal", "river"],
                    "magical_aspect": "water"
                },
                {
                    "id": "resonant_quartz",
                    "name": "Resonant Quartz",
                    "rarity": "common",
                    "magical_affinity": ["EARTH"],
                    "leyline_resonance": 1.7,
                    "primary_locations": ["mountain", "hills"],
                    "magical_aspect": "earth"
                },
                {
                    "id": "etheric_resonance_crystal",
                    "name": "Etheric Resonance Crystal",
                    "rarity": "rare",
                    "magical_affinity": ["ARCANE"],
                    "leyline_resonance": 2.1,
                    "primary_locations": ["forest", "grove"],
                    "magical_aspect": "arcane"
                }
            ]
        
        def distribute_magical_materials(self, world):
            """
            Distribute magical materials throughout the world
            
            Args:
                world: The world to distribute materials in
            """
            # For each location, determine if it should have material deposits
            for location_id, location in world.locations.items():
                # Skip if location has no magic profile
                if not hasattr(location, 'magic_profile'):
                    continue
                
                # Higher chance of materials in high-magic areas
                chance = min(0.8, location.magic_profile.leyline_strength * 0.5)
                
                if random.random() < chance:
                    self._add_material_deposit(location)
        
        def _add_material_deposit(self, location):
            """
            Add a magical material deposit to a location
            
            Args:
                location: The location to add a deposit to
            """
            # Filter materials by location biome compatibility
            compatible_materials = []
            
            if hasattr(location, 'biome'):
                for material in self.materials:
                    # Check if material has primary locations
                    primary_locations = material.get('primary_locations', [])
                    if isinstance(primary_locations, str):
                        primary_locations = [primary_locations]
                    
                    # Check if this biome is preferred for the material
                    if location.biome in primary_locations:
                        # Higher weight for preferred biomes
                        compatible_materials.extend([material] * 3)
                    else:
                        # Still possible but less likely
                        compatible_materials.append(material)
            else:
                compatible_materials = self.materials
            
            # No compatible materials
            if not compatible_materials:
                return
            
            # Select a random material
            material = random.choice(compatible_materials)
            
            # Create a mine POI for the material
            mine_name = f"Glimmering {material['name']} Deposit"
            
            # Generate description
            descriptions = [
                f"A rich deposit of {material['name']}, the crystals glowing with magical energy.",
                f"This mine contains veins of {material['name']}, prized by enchanters and spellcrafters.",
                f"The walls of this cave sparkle with {material['name']} deposits, emanating {material.get('magical_aspect', 'magical').lower()} energy.",
                f"A natural formation where {material['name']} can be harvested. The entire area resonates with magical potential."
            ]
            mine_description = random.choice(descriptions)
            
            # Create the POI
            poi = POI(
                id=f"poi_{uuid.uuid4().hex[:8]}",
                name=mine_name,
                poi_type=POIType.MINE,
                description=mine_description,
                coordinates=(
                    location.coordinates[0] + random.uniform(-0.5, 0.5),
                    location.coordinates[1] + random.uniform(-0.5, 0.5)
                )
            )
            
            # Add material information to POI metadata
            poi.metadata = {
                "material_id": material.get("id", str(uuid.uuid4())),
                "material_name": material["name"],
                "material_rarity": material.get("rarity", "common"),
                "material_magical_aspect": material.get("magical_aspect", "arcane"),
                "leyline_resonance": material.get("leyline_resonance", 1.0)
            }
            
            # Add to location
            location.pois.append(poi)


    # === Advanced Magic World Integration ===
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
                'FIRE': 'FIRE',
                'WATER': 'WATER',
                'EARTH': 'EARTH',
                'AIR': 'AIR',
                'ARCANE': 'ARCANE',
                'LIGHT': 'LIGHT',
                'DARKNESS': 'DARKNESS',
                'LIFE': 'LIFE',
                'DEATH': 'NECROTIC',
                'POISON': 'POISON',
                'ICE': 'ICE',
                'LIGHTNING': 'LIGHTNING'
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
            if 'historical_events' not in location.metadata:
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
        
        # Add magical materials
        material_integration = MagicalMaterialWorldIntegration(basic_integration)
        material_integration.distribute_magical_materials(world)
        
        return world


def create_test_world():
    """Create a test world with diverse biomes"""
    print("Creating a test world...")
    
    # Create a simple world
    world = World(
        id="test_world_1",
        name="Mystic Realms",
        width=30,
        height=30,
        locations={},
        climate=Climate.TEMPERATE
    )
    
    # Create locations with different biomes
    biomes = ['forest', 'mountain', 'desert', 'coastal', 'swamp', 'plains', 'tundra']
    terrains = {
        'forest': Terrain.HILLS,
        'mountain': Terrain.MOUNTAINS,
        'desert': Terrain.FLAT,
        'coastal': Terrain.COASTAL,
        'swamp': Terrain.RIVER,
        'plains': Terrain.FLAT,
        'tundra': Terrain.FLAT
    }
    
    # Create 20 locations
    for i in range(20):
        # Randomly select biome and terrain
        biome = random.choice(biomes)
        terrain = terrains.get(biome, Terrain.FLAT)
        
        # Generate a name
        suffixes = ['Highlands', 'Lowlands', 'Valley', 'Basin', 'Plateau', 'Hills']
        name = f"{biome.title()} {random.choice(suffixes)}"
        
        # Create location
        location = Location(
            id=f"loc_{i}",
            name=name,
            description=f"A {biome} with {terrain.name.lower()} terrain.",
            coordinates=(random.randint(1, world.width), random.randint(1, world.height)),
            terrain=terrain,
            pois=[],
            biome=biome
        )
        
        # Add some basic POIs
        for j in range(random.randint(1, 3)):
            poi_types = [POIType.VILLAGE, POIType.RUIN, POIType.CAVE, POIType.TOWER, 
                        POIType.CAMP, POIType.SETTLEMENT, POIType.MINE, POIType.FARM]
            poi_type = random.choice(poi_types)
            
            # Generate a name
            prefixes = ['North', 'South', 'East', 'West', 'Old', 'New', 'Black', 'White', 'Blue', 'Red']
            suffixes = ['Village', 'Settlement', 'Mine', 'Camp', 'Hill', 'Wood', 'Creek']
            poi_name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
            
            # Create POI
            poi = POI(
                id=f"poi_{i}_{j}",
                name=poi_name,
                poi_type=poi_type,
                description=f"A {poi_type.name.lower()} in the {biome}.",
                coordinates=(
                    location.coordinates[0] + random.uniform(-0.5, 0.5),
                    location.coordinates[1] + random.uniform(-0.5, 0.5)
                )
            )
            
            location.pois.append(poi)
        
        # Add to world
        world.locations[location.id] = location
    
    return world


def enhance_world_with_magic(world, use_advanced_features=True):
    """Enhance the world with magical features"""
    print("Enhancing world with magical features...")
    
    # Try to use the imported functions if available, otherwise use local implementation
    if use_advanced_features and 'enhance_world_with_advanced_magic' in globals():
        # Use the advanced magic integration
        world = enhance_world_with_advanced_magic(world)
        return world, None
    else:
        # Create magic world integration
        magic_integration = MagicWorldIntegration()
        
        # Enhance world with magic
        magic_integration.enhance_world_with_magic(world)
        
        # Create material integration
        material_integration = MagicalMaterialWorldIntegration(magic_integration)
        material_integration.distribute_magical_materials(world)
        
        return world, magic_integration


def print_world_overview(world, magic_integration=None):
    """Print an overview of the world's magical features"""
    print("\n" + "=" * 80)
    print(f"\nWORLD: {world.name}")
    print(f"Size: {world.width}x{world.height}")
    print(f"Climate: {world.climate.name}")
    print(f"Locations: {len(world.locations)}")
    
    print("\nLEYLINE NETWORK:")
    print(f"Leylines: {len(world.leylines)}")
    print(f"Magical hotspots: {len(world.hotspots)}")
    
    # Count magical POIs
    magical_poi_count = 0
    material_deposit_count = 0
    
    for location in world.locations.values():
        for poi in location.pois:
            # Count mines with material metadata as material deposits
            if poi.poi_type == POIType.MINE and hasattr(poi, 'metadata') and 'material_id' in poi.metadata:
                material_deposit_count += 1
            # Count shrines, groves, springs, and relic sites as magical POIs
            elif poi.poi_type in [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]:
                magical_poi_count += 1
    
    print(f"\nMagical POIs: {magical_poi_count}")
    print(f"Material deposits: {material_deposit_count}")
    
    print("\n" + "=" * 80)


def print_location_details(world):
    """Print details for each location in the world"""
    print("\nLOCATION DETAILS:")
    
    # Print a few random locations for brevity
    location_sample = random.sample(list(world.locations.values()), min(10, len(world.locations)))
    
    for location in location_sample:
        print(f"{location.name} ({location.biome}):")
        print(f"  Coordinates: {location.coordinates}")
        if hasattr(location, 'magic_profile'):
            print(f"  Leyline strength: {location.magic_profile.leyline_strength}")
            print(f"  Mana flux: {location.magic_profile.mana_flux_level.name}")
            print(f"  Magic aspects: {location.magic_profile.dominant_magic_aspects}")
            print(f"  Allows rituals: {location.magic_profile.allows_ritual_sites}")
        
        print("  Points of Interest:")
        for poi in location.pois:
            print(f"    - {poi.name} ({poi.poi_type.name})")
            print(f"      {poi.description}")
        
        print()


def print_magical_features(world):
    """Print details about magical features in the world"""
    # Collect all magical POIs
    magical_pois = []
    material_deposits = []
    
    for location in world.locations.values():
        for poi in location.pois:
            if poi.poi_type in [POIType.SHRINE, POIType.GROVE, POIType.SPRING, POIType.RELIC_SITE]:
                magical_pois.append((poi, location))
            elif poi.poi_type == POIType.MINE and hasattr(poi, 'metadata') and 'material_id' in poi.metadata:
                material_deposits.append((poi, location))
    
    # Print magical POIs
    print(f"\nMagical Points of Interest ({len(magical_pois)}):")
    for poi, location in magical_pois:
        print(f"  {poi.name} ({poi.poi_type.name}) in {location.name}")
        print(f"    {poi.description}")
    
    # Print material deposits
    print(f"\nMagical Material Deposits ({len(material_deposits)}):")
    for poi, location in material_deposits:
        print(f"  {poi.name} in {location.name}")
        print(f"    {poi.description}")
        if hasattr(poi, 'metadata'):
            print(f"    Material: {poi.metadata.get('material_name', 'Unknown')} ({poi.metadata.get('material_rarity', 'common')})")
            print(f"    Magical Aspect: {poi.metadata.get('material_magical_aspect', 'unknown')}")
        print()


def print_advanced_magic_features(world):
    """Print advanced magical features for locations"""
    print("\nADVANCED MAGICAL FEATURES:")
    
    # Print a few locations with advanced features
    locations_with_advanced_features = []
    
    for location in world.locations.values():
        if hasattr(location, 'metadata') and location.metadata:
            if any(key in location.metadata for key in [
                'environment_type', 'magical_stability', 'emotional_aura', 
                'historical_events', 'peak_magic_time', 'seasonal_magic'
            ]):
                locations_with_advanced_features.append(location)
    
    # Select a sample of locations
    location_sample = random.sample(
        locations_with_advanced_features, 
        min(5, len(locations_with_advanced_features))
    ) if locations_with_advanced_features else []
    
    if not location_sample:
        print("  No locations with advanced magical features found.")
        return
    
    for location in location_sample:
        print(f"\n  {location.name} ({location.biome}):")
        
        if 'environment_type' in location.metadata:
            print(f"    Environment Type: {location.metadata['environment_type']}")
        
        if 'magical_stability' in location.metadata:
            stability = location.metadata['magical_stability']
            stability_desc = "Unstable" if stability < 0.5 else "Stable" if stability > 0.8 else "Moderate"
            print(f"    Magical Stability: {stability_desc} ({stability:.2f})")
        
        if 'emotional_aura' in location.metadata and location.metadata['emotional_aura']:
            emotions = ", ".join(location.metadata['emotional_aura'])
            print(f"    Emotional Aura: {emotions}")
        
        if 'historical_events' in location.metadata and location.metadata['historical_events']:
            events = ", ".join(location.metadata['historical_events'])
            print(f"    Historical Magical Events: {events}")
        
        if 'peak_magic_time' in location.metadata:
            print(f"    Peak Magic Time: {location.metadata['peak_magic_time']}")
            if 'time_magic_feature' in location.metadata:
                print(f"      Effect: {location.metadata['time_magic_feature']}")
        
        if 'weather_magic_affinities' in location.metadata and location.metadata['weather_magic_affinities']:
            affinities = [f"{weather}: {aspect}" for weather, aspect in location.metadata['weather_magic_affinities'].items()]
            print(f"    Weather Magic Affinities: {', '.join(affinities)}")
        
        if 'seasonal_magic' in location.metadata:
            seasonal = location.metadata['seasonal_magic']
            print(f"    Seasonal Magic (Peak: {location.metadata.get('peak_magic_season', 'unknown')}):")
            if 'enhanced_aspects' in seasonal:
                print(f"      Enhanced Aspects: {', '.join(seasonal['enhanced_aspects'])}")
            if 'diminished_aspects' in seasonal:
                print(f"      Diminished Aspects: {', '.join(seasonal['diminished_aspects'])}")
            if 'description' in seasonal:
                print(f"      Effect: {seasonal['description']}")


def main():
    """Main demonstration function"""
    # Create a test world
    world = create_test_world()
    
    # Enhance the world with magic
    world, magic_integration = enhance_world_with_magic(world, use_advanced_features=True)
    
    # Print world overview
    print_world_overview(world, magic_integration)
    
    # Print location details
    print_location_details(world)
    
    # Print magical features
    print_magical_features(world)
    
    # Print advanced magical features
    print_advanced_magic_features(world)
    
    print("\nDemonstration complete.")


if __name__ == "__main__":
    main()