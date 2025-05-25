"""
Magic World Integration Module

This module integrates the magic system with the world generation system.
It allows for the placement and discovery of magical features in the world,
such as leylines, magical resources, and ritual sites.
"""

import random
from typing import Dict, List, Optional, Tuple, Any

# Import from magic system
from .magic_system import (
    MagicSource,
    MagicTier,
    DamageType,
    ManaFluxLevel,
    LocationMagicProfile
)

# Import from world generation
from world_generation.world_model import World, Location, POI
from world_generation.poi_placement_service import POIType
from location_generators.base_generator import LocationFeature


class MagicWorldIntegration:
    """
    Integrates magic system with world generation.
    
    This class adds magical properties to generated worlds, locations, and POIs.
    It handles:
    - Leyline generation and placement in the world
    - Magical resource distribution
    - Assignment of magical properties to locations
    - Creation of magical POIs (shrines, ritual sites, etc.)
    """
    
    def __init__(self):
        """Initialize the integration service"""
        self.leyline_map = {}  # Maps coordinates to leyline strengths
        self.magical_hotspots = []  # Locations with high magical activity
    
    def enhance_world_with_magic(self, world: World) -> World:
        """
        Add magical features to a generated world
        
        Args:
            world: The world object to enhance
            
        Returns:
            The enhanced world with magical properties
        """
        # Generate leyline network
        self._generate_leyline_network(world)
        
        # Enhance locations with magical properties
        for location_id, location in world.locations.items():
            magic_profile = self._generate_location_magic_profile(location, world)
            # We would store this in the location object in a real implementation
            # For now, we'll just print it for demonstration
            location.magic_profile = magic_profile
        
        # Add magical POIs
        self._add_magical_pois(world)
        
        return world
    
    def _generate_leyline_network(self, world: World) -> None:
        """
        Generate a network of leylines across the world
        
        Args:
            world: The world to generate leylines for
        """
        # In a real implementation, this would use advanced algorithms to create
        # natural-looking leyline patterns. For now, we'll create a simple grid.
        
        # Create main leylines (high strength)
        num_major_leylines = random.randint(3, 5)
        
        for _ in range(num_major_leylines):
            # Choose random start and end points at the edges of the map
            start_x = random.choice([0, world.width])
            start_y = random.randint(0, world.height)
            
            end_x = random.choice([0, world.width])
            end_y = random.randint(0, world.height)
            
            # If both x coords are the same, we need to change one
            if start_x == end_x:
                end_x = world.width if start_x == 0 else 0
            
            # Create the leyline
            self._create_leyline_path(world, (start_x, start_y), (end_x, end_y), 
                                    strength=random.randint(4, 5))
        
        # Create minor leylines (medium strength)
        num_minor_leylines = random.randint(5, 8)
        
        for _ in range(num_minor_leylines):
            # Choose random start and end points within the map
            start_x = random.randint(0, world.width)
            start_y = random.randint(0, world.height)
            
            end_x = random.randint(0, world.width)
            end_y = random.randint(0, world.height)
            
            # Create the leyline
            self._create_leyline_path(world, (start_x, start_y), (end_x, end_y), 
                                    strength=random.randint(2, 3))
        
        # Add leyline nodes (intersections with increased strength)
        self._add_leyline_nodes(world)
    
    def _create_leyline_path(self, 
                           world: World, 
                           start: Tuple[int, int], 
                           end: Tuple[int, int], 
                           strength: int) -> None:
        """
        Create a leyline path between two points
        
        Args:
            world: The world to add the leyline to
            start: The starting coordinates (x, y)
            end: The ending coordinates (x, y)
            strength: The strength of the leyline (1-5)
        """
        # Simple line drawing algorithm (Bresenham's)
        x0, y0 = start
        x1, y1 = end
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            # Add current point to leyline map
            self.leyline_map[(x0, y0)] = max(strength, self.leyline_map.get((x0, y0), 0))
            
            if x0 == x1 and y0 == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def _add_leyline_nodes(self, world: World) -> None:
        """
        Add leyline nodes (intersections with increased strength)
        
        Args:
            world: The world to add nodes to
        """
        # Find intersection points and increase their strength
        for (x, y), strength in self.leyline_map.items():
            # Check all adjacent cells for leylines
            adjacent_count = 0
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if (x + dx, y + dy) in self.leyline_map:
                    adjacent_count += 1
            
            # If this is an intersection (3 or more connections)
            if adjacent_count >= 3:
                # Increase strength (max 5)
                self.leyline_map[(x, y)] = min(5, strength + 1)
                
                # Add to magical hotspots
                self.magical_hotspots.append((x, y))
    
    def _generate_location_magic_profile(self, location: Location, world: World) -> LocationMagicProfile:
        """
        Generate magical properties for a location
        
        Args:
            location: The location to enhance
            world: The world containing the location
            
        Returns:
            A LocationMagicProfile object with the magical properties
        """
        # Determine leyline strength at this location
        x, y = location.coordinates
        
        # Check for leylines in and around this location
        leyline_strength = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                check_x, check_y = x + dx, y + dy
                if (check_x, check_y) in self.leyline_map:
                    # Closer leylines have more influence
                    distance = max(abs(dx), abs(dy))
                    strength_at_point = self.leyline_map[(check_x, check_y)]
                    
                    # Adjust strength based on distance
                    if distance == 0:  # Direct hit
                        leyline_strength = max(leyline_strength, strength_at_point)
                    elif distance == 1:  # Adjacent
                        leyline_strength = max(leyline_strength, strength_at_point - 1)
                    else:  # Nearby
                        leyline_strength = max(leyline_strength, strength_at_point - 2)
        
        # Clamp leyline strength to valid range
        leyline_strength = max(0, min(5, leyline_strength))
        
        # Determine mana flux level based on leyline strength and randomness
        mana_flux_level = ManaFluxLevel.MODERATE  # Default
        
        if leyline_strength == 0:
            mana_flux_options = [ManaFluxLevel.DORMANT, ManaFluxLevel.FAINT]
            mana_flux_level = random.choice(mana_flux_options)
        elif leyline_strength == 1:
            mana_flux_options = [ManaFluxLevel.FAINT, ManaFluxLevel.MODERATE]
            mana_flux_level = random.choice(mana_flux_options)
        elif leyline_strength == 2:
            mana_flux_level = ManaFluxLevel.MODERATE
        elif leyline_strength == 3:
            mana_flux_options = [ManaFluxLevel.MODERATE, ManaFluxLevel.STRONG]
            mana_flux_level = random.choice(mana_flux_options)
        elif leyline_strength == 4:
            mana_flux_options = [ManaFluxLevel.STRONG, ManaFluxLevel.INTENSE]
            mana_flux_level = random.choice(mana_flux_options)
        elif leyline_strength >= 5:
            mana_flux_options = [ManaFluxLevel.INTENSE, ManaFluxLevel.CHAOTIC]
            mana_flux_level = random.choice(mana_flux_options)
        
        # Determine dominant magic aspects based on location biome and features
        dominant_magic_aspects = []
        
        # Different biomes have different magical affinities
        if hasattr(location, 'biome'):
            if location.biome == 'forest':
                dominant_magic_aspects.append(DamageType.EARTH)
            elif location.biome == 'mountain':
                dominant_magic_aspects.append(DamageType.EARTH)
                dominant_magic_aspects.append(DamageType.AIR)
            elif location.biome == 'desert':
                dominant_magic_aspects.append(DamageType.FIRE)
            elif location.biome == 'tundra':
                dominant_magic_aspects.append(DamageType.ICE)
            elif location.biome == 'swamp':
                dominant_magic_aspects.append(DamageType.WATER)
                dominant_magic_aspects.append(DamageType.NECROTIC)
            elif location.biome == 'volcanic':
                dominant_magic_aspects.append(DamageType.FIRE)
                dominant_magic_aspects.append(DamageType.EARTH)
            elif location.biome == 'coastal':
                dominant_magic_aspects.append(DamageType.WATER)
                dominant_magic_aspects.append(DamageType.AIR)
        
        # Add a random aspect if none were determined
        if not dominant_magic_aspects:
            dominant_magic_aspects.append(random.choice(list(DamageType)))
        
        # Determine if this location allows ritual sites
        allows_ritual_sites = leyline_strength >= 2
        
        # Generate a magic profile for this location
        return LocationMagicProfile(
            leyline_strength=leyline_strength,
            mana_flux_level=mana_flux_level,
            dominant_magic_aspects=dominant_magic_aspects,
            environmental_decay_level=random.randint(0, 2),  # Low decay by default
            allows_ritual_sites=allows_ritual_sites,
            historical_magic_events=[]  # Would be filled based on world history
        )
    
    def _add_magical_pois(self, world: World) -> None:
        """
        Add magical Points of Interest to the world
        
        Args:
            world: The world to add POIs to
        """
        # Add magical shrines at some leyline nodes
        for x, y in self.magical_hotspots:
            # Only add a shrine at some hotspots
            if random.random() < 0.7:
                # Find the nearest location
                nearest_location = self._find_nearest_location(world, (x, y))
                
                if nearest_location:
                    # Create a magical shrine POI
                    shrine_poi = POI(
                        id=f"shrine_{len(nearest_location.pois) + 1}",
                        name=self._generate_shrine_name(),
                        poi_type=POIType.SHRINE,
                        description=self._generate_shrine_description(),
                        coordinates=(x, y)
                    )
                    
                    # Add the POI to the location
                    nearest_location.pois.append(shrine_poi)
        
        # Add other magical POIs based on location magic profiles
        for location_id, location in world.locations.items():
            if hasattr(location, 'magic_profile'):
                # Add magical features based on the location's magic profile
                
                # Add a ritual site if the location allows it
                if location.magic_profile.allows_ritual_sites and random.random() < 0.4:
                    ritual_poi = POI(
                        id=f"ritual_site_{len(location.pois) + 1}",
                        name=self._generate_ritual_site_name(),
                        poi_type=POIType.RELIC_SITE,  # Using RELIC_SITE for ritual sites
                        description=self._generate_ritual_site_description(
                            location.magic_profile.dominant_magic_aspects
                        ),
                        coordinates=location.coordinates
                    )
                    
                    # Add the POI to the location
                    location.pois.append(ritual_poi)
                
                # Add magical grove in locations with strong earth or light aspects
                if (DamageType.EARTH in location.magic_profile.dominant_magic_aspects or
                    DamageType.LIGHT in location.magic_profile.dominant_magic_aspects) and random.random() < 0.3:
                    grove_poi = POI(
                        id=f"grove_{len(location.pois) + 1}",
                        name=self._generate_grove_name(),
                        poi_type=POIType.GROVE,
                        description=self._generate_grove_description(),
                        coordinates=location.coordinates
                    )
                    
                    # Add the POI to the location
                    location.pois.append(grove_poi)
                
                # Add magical spring in locations with strong water aspects
                if DamageType.WATER in location.magic_profile.dominant_magic_aspects and random.random() < 0.3:
                    spring_poi = POI(
                        id=f"spring_{len(location.pois) + 1}",
                        name=self._generate_spring_name(),
                        poi_type=POIType.SPRING,
                        description=self._generate_spring_description(),
                        coordinates=location.coordinates
                    )
                    
                    # Add the POI to the location
                    location.pois.append(spring_poi)
    
    def _find_nearest_location(self, world: World, coordinates: Tuple[int, int]) -> Optional[Location]:
        """
        Find the nearest location to the given coordinates
        
        Args:
            world: The world to search in
            coordinates: The coordinates to find the nearest location to
            
        Returns:
            The nearest location, or None if no locations exist
        """
        if not world.locations:
            return None
            
        x, y = coordinates
        nearest_location = None
        nearest_distance = float('inf')
        
        for location_id, location in world.locations.items():
            loc_x, loc_y = location.coordinates
            distance = ((loc_x - x) ** 2 + (loc_y - y) ** 2) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_location = location
        
        return nearest_location
    
    def _generate_shrine_name(self) -> str:
        """Generate a name for a magical shrine"""
        prefixes = ["Ancient", "Sacred", "Mystic", "Forgotten", "Shimmering", "Arcane", "Eternal"]
        types = ["Shrine", "Altar", "Monolith", "Obelisk", "Sanctuary", "Circle", "Stone"]
        
        return f"{random.choice(prefixes)} {random.choice(types)}"
    
    def _generate_shrine_description(self) -> str:
        """Generate a description for a magical shrine"""
        descriptions = [
            "A weathered stone structure humming with ancient power.",
            "Mystical runes glow faintly on this ancient monument.",
            "Locals avoid this place, claiming it's where the veil between worlds thins.",
            "The air around this structure shimmers with magical energy.",
            "A circular arrangement of stones that seems to concentrate magical energies.",
            "This ancient shrine has been a site of magical rituals for centuries."
        ]
        
        return random.choice(descriptions)
    
    def _generate_ritual_site_name(self) -> str:
        """Generate a name for a ritual site"""
        prefixes = ["Hallowed", "Ceremonial", "Ancient", "Sacred", "Arcane", "Mystical"]
        types = ["Circle", "Grove", "Grounds", "Chamber", "Altar", "Site", "Sanctum"]
        
        return f"{random.choice(prefixes)} {random.choice(types)}"
    
    def _generate_ritual_site_description(self, dominant_aspects: List[DamageType]) -> str:
        """
        Generate a description for a ritual site based on its dominant magical aspects
        
        Args:
            dominant_aspects: The dominant magical aspects of the location
            
        Returns:
            A description string
        """
        base_descriptions = [
            "A site where the boundary between worlds is thin.",
            "Ancient symbols etched into the ground form a ritual circle.",
            "The residual energy of countless rituals lingers in this place.",
            "A place of power where magic users gather to perform complex rituals."
        ]
        
        aspect_descriptions = {
            DamageType.FIRE: "The air shimmers with heat even on cold days.",
            DamageType.ICE: "A permanent chill permeates this area regardless of season.",
            DamageType.LIGHTNING: "Small static discharges occasionally spark in the air.",
            DamageType.EARTH: "The ground feels unusually fertile and alive with energy.",
            DamageType.AIR: "Gentle breezes flow in impossible patterns, defying natural air currents.",
            DamageType.WATER: "The air has a permanent moisture to it, and water droplets form on surfaces.",
            DamageType.LIGHT: "Motes of light drift through the air like fireflies, even in daylight.",
            DamageType.DARKNESS: "Shadows seem deeper and more substantial than they should be.",
            DamageType.ARCANE: "The very fabric of reality seems to warp slightly in this place.",
            DamageType.NECROTIC: "Plants struggle to grow here, and those that do appear twisted and wrong.",
            DamageType.PSYCHIC: "Visitors report hearing whispers and experiencing strange visions.",
            DamageType.SPIRITUAL: "The boundary between the physical and spiritual realms is paper-thin here."
        }
        
        description = random.choice(base_descriptions)
        
        # Add aspect-specific details
        for aspect in dominant_aspects:
            if aspect in aspect_descriptions and random.random() < 0.7:
                description += " " + aspect_descriptions[aspect]
        
        return description
    
    def _generate_grove_name(self) -> str:
        """Generate a name for a magical grove"""
        prefixes = ["Whispering", "Ancient", "Verdant", "Enchanted", "Sacred", "Living", "Eternal"]
        types = ["Grove", "Copse", "Thicket", "Glade", "Sanctuary", "Wood", "Haven"]
        
        return f"{random.choice(prefixes)} {random.choice(types)}"
    
    def _generate_grove_description(self) -> str:
        """Generate a description for a magical grove"""
        descriptions = [
            "The trees here seem to whisper to each other when no one is listening.",
            "Plants grow with unusual vigor, and many have strange properties.",
            "The canopy filters light in patterns that seem to form symbols on the forest floor.",
            "The oldest trees here are rumored to have witnessed the dawn of the world.",
            "Druids and nature mages seek this place for its natural magical energies.",
            "Animals in this grove exhibit unusual intelligence and behavior."
        ]
        
        return random.choice(descriptions)
    
    def _generate_spring_name(self) -> str:
        """Generate a name for a magical spring"""
        prefixes = ["Mystic", "Healing", "Shimmering", "Arcane", "Blessed", "Crystal", "Eternal"]
        types = ["Spring", "Font", "Well", "Waters", "Pool", "Fount", "Basin"]
        
        return f"{random.choice(prefixes)} {random.choice(types)}"
    
    def _generate_spring_description(self) -> str:
        """Generate a description for a magical spring"""
        descriptions = [
            "Water bubbles up from deep underground, carrying magical properties with it.",
            "The water glows faintly with an inner light and is said to have healing properties.",
            "Those who drink from this spring report enhanced magical abilities for a short time.",
            "The waters are unusually clear and reflect images that aren't there.",
            "Local legends claim this spring is connected to the realm of water elementals.",
            "The spring never freezes, even in the coldest winter."
        ]
        
        return random.choice(descriptions)


# Integration with magical material service
class MagicalMaterialWorldIntegration:
    """
    Integrates magical materials with the world generation system.
    
    This class handles the placement and discovery of magical materials
    throughout the generated world.
    """
    
    def __init__(self, magic_world_integration: MagicWorldIntegration):
        """
        Initialize the integration service
        
        Args:
            magic_world_integration: The MagicWorldIntegration instance
        """
        self.magic_world_integration = magic_world_integration
        self.material_deposits = {}  # Maps coordinates to material types
    
    def distribute_magical_materials(self, world: World) -> None:
        """
        Distribute magical materials throughout the world
        
        Args:
            world: The world to enhance with magical materials
        """
        # Determine material distribution based on leylines and location types
        for location_id, location in world.locations.items():
            if hasattr(location, 'magic_profile'):
                # Higher leyline strength means more and rarer materials
                material_chance = 0.2 + (location.magic_profile.leyline_strength * 0.1)
                
                # Add materials based on the location's magic profile
                if random.random() < material_chance:
                    self._add_material_deposits_to_location(location)
    
    def _add_material_deposits_to_location(self, location: Location) -> None:
        """
        Add magical material deposits to a location
        
        Args:
            location: The location to add deposits to
        """
        # In a real implementation, this would use the MagicalMaterialService
        # to create appropriate material deposits based on the location's
        # magical properties.
        
        # For now, we'll just mark the location as having material deposits
        num_deposits = random.randint(1, 3)
        
        for i in range(num_deposits):
            deposit_id = f"material_deposit_{location.id}_{i}"
            
            # In a real implementation, this would create a proper material deposit
            # with specific material types and quantities.
            # We'd also add a POI for discoverable deposits.
            
            # For now, just add a generic POI
            deposit_poi = POI(
                id=deposit_id,
                name=self._generate_deposit_name(),
                poi_type=POIType.MINE,  # Using MINE for material deposits
                description=self._generate_deposit_description(location.magic_profile.dominant_magic_aspects),
                coordinates=location.coordinates
            )
            
            # Add the POI to the location
            location.pois.append(deposit_poi)
    
    def _generate_deposit_name(self) -> str:
        """Generate a name for a magical material deposit"""
        prefixes = ["Glimmering", "Arcane", "Mystic", "Enchanted", "Resonant", "Shimmering", "Charged"]
        types = ["Vein", "Deposit", "Outcropping", "Formation", "Cluster", "Lode", "Crystal"]
        
        return f"{random.choice(prefixes)} {random.choice(types)}"
    
    def _generate_deposit_description(self, dominant_aspects: List[DamageType]) -> str:
        """
        Generate a description for a magical material deposit
        
        Args:
            dominant_aspects: The dominant magical aspects in the area
            
        Returns:
            A description string
        """
        base_descriptions = [
            "A concentration of magical materials can be harvested here.",
            "The ground sparkles with magical energy, indicating valuable materials.",
            "Unusual crystalline formations protrude from the ground, rich in magical essence.",
            "A vein of mystically-charged minerals runs through this area."
        ]
        
        aspect_descriptions = {
            DamageType.FIRE: "The materials glow with inner heat.",
            DamageType.ICE: "Frost forms on the materials even on warm days.",
            DamageType.LIGHTNING: "Small sparks occasionally jump between the crystal formations.",
            DamageType.EARTH: "Plants growing near the materials exhibit unusual growth patterns.",
            DamageType.AIR: "The materials seem unnaturally light and resonate with the slightest breeze.",
            DamageType.WATER: "Moisture collects on the surface of the materials, never quite evaporating.",
            DamageType.LIGHT: "The materials glow with a soft, inner light.",
            DamageType.DARKNESS: "The materials seem to absorb light around them.",
            DamageType.ARCANE: "The materials shimmer with patterns that hurt the eyes if viewed too long.",
            DamageType.NECROTIC: "The ground around the materials appears slightly withered.",
            DamageType.PSYCHIC: "Standing near the materials induces strange thoughts.",
            DamageType.SPIRITUAL: "The veil between worlds feels thin around these materials."
        }
        
        description = random.choice(base_descriptions)
        
        # Add aspect-specific details
        for aspect in dominant_aspects:
            if aspect in aspect_descriptions and random.random() < 0.7:
                description += " " + aspect_descriptions[aspect]
        
        return description