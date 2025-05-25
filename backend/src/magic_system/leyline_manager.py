"""
Leyline Manager - System for handling magical energy flows in the world

This module manages the placement, properties, and effects of leylines - 
the magical energy currents that flow through the world and affect
magical potency in different regions.
"""

import math
import random
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Set

from world_generation.world_model import BiomeType, POIType, DBRegion, DBBiome, DBPointOfInterest


class LeylineType(str, Enum):
    """Types of leylines with different magical properties."""
    PRIMAL = "primal"         # Raw, elemental magical energy
    ARCANE = "arcane"         # Intellectual, formulaic magic
    SPIRITUAL = "spiritual"   # Soul and life-force related magic
    NATURAL = "natural"       # Nature and growth based magic
    VOID = "void"             # Entropy and chaos based magic


class LeylineStrength(str, Enum):
    """Strength levels for leylines."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    POWERFUL = "powerful"
    NEXUS = "nexus"           # A convergence of multiple leylines


class LeylineStatus(str, Enum):
    """Status of a leyline's health/integrity."""
    STABLE = "stable"
    FLUCTUATING = "fluctuating"
    DIMINISHING = "diminishing"
    SURGING = "surging"
    CORRUPTED = "corrupted"
    FRACTURED = "fractured"


class Leyline:
    """
    Represents a leyline - a flow of magical energy through the world.
    """
    def __init__(
        self,
        leyline_id: str,
        name: str,
        leyline_type: LeylineType,
        strength: LeylineStrength,
        status: LeylineStatus,
        path_points: List[Tuple[float, float]],  # List of coordinate points defining the path
        width: float,
        depth: float,
        magical_affinity: Dict[str, float],
        affected_regions: Set[str] = None,
        affected_pois: Set[str] = None,
        notes: str = ""
    ):
        self.id = leyline_id
        self.name = name
        self.leyline_type = leyline_type
        self.strength = strength
        self.status = status
        self.path_points = path_points
        self.width = width
        self.depth = depth
        self.magical_affinity = magical_affinity
        self.affected_regions = affected_regions or set()
        self.affected_pois = affected_pois or set()
        self.notes = notes
        
    def __str__(self):
        return f"{self.name} ({self.leyline_type}, {self.strength})"
    
    def get_influence_at_point(self, point: Tuple[float, float]) -> float:
        """
        Calculate the magical influence of this leyline at a specific point.
        
        Args:
            point: (x, y) coordinates to check
            
        Returns:
            Influence value between 0.0 and 1.0
        """
        # Find the closest point on the leyline
        min_distance = float('inf')
        for i in range(len(self.path_points) - 1):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            
            # Calculate distance from point to line segment
            distance = self._point_to_line_distance(point, p1, p2)
            min_distance = min(min_distance, distance)
        
        # Convert distance to influence (closer = higher influence)
        # The influence falls off based on distance and leyline width
        if min_distance <= self.width:
            influence = 1.0
        else:
            # Exponential falloff beyond the width
            influence = math.exp(-0.5 * (min_distance - self.width) / (self.width * 2))
        
        # Adjust for leyline strength
        strength_multiplier = {
            LeylineStrength.WEAK: 0.4,
            LeylineStrength.MODERATE: 0.7,
            LeylineStrength.STRONG: 1.0,
            LeylineStrength.POWERFUL: 1.5,
            LeylineStrength.NEXUS: 2.5
        }.get(self.strength, 1.0)
        
        influence *= strength_multiplier
        
        # Cap at 1.0
        return min(influence, 1.0)
    
    def _point_to_line_distance(
        self, 
        point: Tuple[float, float], 
        line_start: Tuple[float, float], 
        line_end: Tuple[float, float]
    ) -> float:
        """Calculate the shortest distance from a point to a line segment."""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate line length squared
        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        
        # If line is a point, return distance to that point
        if line_length_sq == 0:
            return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        
        # Calculate projection of point onto line
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / line_length_sq))
        
        # Calculate closest point on line
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        # Return distance to closest point
        return math.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2)


class LeylineManager:
    """
    Manages the generation, storage, and querying of leylines in the world.
    """
    def __init__(self):
        self.leylines: Dict[str, Leyline] = {}
        self.region_leyline_map: Dict[str, List[str]] = {}  # region_id -> leyline_ids
        self.poi_leyline_map: Dict[str, List[str]] = {}     # poi_id -> leyline_ids
        
    def generate_leylines_for_region(self, region: DBRegion) -> List[Leyline]:
        """
        Generate leylines for a specific region based on its properties.
        
        Args:
            region: The region to generate leylines for
            
        Returns:
            List of generated Leyline objects
        """
        # Determine how many leylines to generate for this region
        # based on region size, magical properties, etc.
        num_leylines = random.randint(1, 3)
        
        generated_leylines = []
        
        for i in range(num_leylines):
            # Generate a leyline with properties appropriate for this region
            leyline_type = random.choice(list(LeylineType))
            
            # Strength depends on region's magical properties
            strength_options = list(LeylineStrength)
            # Bias toward moderate strength but allow for variation
            strength_weights = [0.2, 0.4, 0.3, 0.08, 0.02]  # Weights for each strength level
            strength = random.choices(strength_options, weights=strength_weights)[0]
            
            # Status - mostly stable but allow for interesting variations
            status_options = list(LeylineStatus)
            status_weights = [0.7, 0.15, 0.05, 0.05, 0.03, 0.02]  # Weights for each status
            status = random.choices(status_options, weights=status_weights)[0]
            
            # Generate a natural-looking path through the region
            # This would be based on the region's coordinate bounds
            # For this example, we'll create a simple path
            path_points = self._generate_natural_path(5, 8)
            
            # Generate width based on strength
            width_base = {
                LeylineStrength.WEAK: 0.5,
                LeylineStrength.MODERATE: 1.0,
                LeylineStrength.STRONG: 2.0,
                LeylineStrength.POWERFUL: 4.0,
                LeylineStrength.NEXUS: 8.0
            }.get(strength, 1.0)
            width = width_base * (0.8 + 0.4 * random.random())
            
            # Generate depth based on strength and type
            depth_base = {
                LeylineStrength.WEAK: 10,
                LeylineStrength.MODERATE: 25,
                LeylineStrength.STRONG: 50,
                LeylineStrength.POWERFUL: 100,
                LeylineStrength.NEXUS: 250
            }.get(strength, 25)
            depth = depth_base * (0.8 + 0.4 * random.random())
            
            # Generate magical affinity based on leyline type
            magical_affinity = self._generate_magical_affinity(leyline_type)
            
            # Create a name for the leyline
            name_parts = {
                LeylineType.PRIMAL: ["Primal", "Elemental", "Raw", "Fundamental"],
                LeylineType.ARCANE: ["Arcane", "Scholarly", "Formulaic", "Reasoned"],
                LeylineType.SPIRITUAL: ["Spiritual", "Soul", "Essence", "Vital"],
                LeylineType.NATURAL: ["Natural", "Growth", "Verdant", "Fertile"],
                LeylineType.VOID: ["Void", "Entropic", "Chaotic", "Unstable"]
            }.get(leyline_type, ["Magical"])
            
            descriptor = random.choice(name_parts)
            second_parts = ["Flow", "Current", "Stream", "River", "Line", "Pulse"]
            second_part = random.choice(second_parts)
            
            name = f"The {descriptor} {second_part}"
            
            # Create the leyline
            leyline = Leyline(
                leyline_id=f"leyline_{region.id}_{i}",
                name=name,
                leyline_type=leyline_type,
                strength=strength,
                status=status,
                path_points=path_points,
                width=width,
                depth=depth,
                magical_affinity=magical_affinity,
                affected_regions={region.id},
            )
            
            # Add to results
            generated_leylines.append(leyline)
            
            # Store in internal maps
            self.leylines[leyline.id] = leyline
            
            if region.id not in self.region_leyline_map:
                self.region_leyline_map[region.id] = []
            self.region_leyline_map[region.id].append(leyline.id)
            
        return generated_leylines
    
    def _generate_natural_path(self, min_points: int, max_points: int) -> List[Tuple[float, float]]:
        """Generate a natural-looking path for a leyline."""
        num_points = random.randint(min_points, max_points)
        path = []
        
        # Start at a random point
        x, y = random.uniform(0, 100), random.uniform(0, 100)
        path.append((x, y))
        
        # Generate subsequent points with some natural variation
        angle = random.uniform(0, 2 * math.pi)
        for _ in range(num_points - 1):
            # Slightly adjust the angle for a more natural curve
            angle += random.uniform(-math.pi/4, math.pi/4)
            
            # Distance to next point
            distance = random.uniform(5, 15)
            
            # Calculate new point
            x += distance * math.cos(angle)
            y += distance * math.sin(angle)
            
            path.append((x, y))
            
        return path
    
    def _generate_magical_affinity(self, leyline_type: LeylineType) -> Dict[str, float]:
        """Generate magical affinities based on leyline type."""
        affinities = {}
        
        # Base affinities by type
        if leyline_type == LeylineType.PRIMAL:
            affinities = {
                "fire": random.uniform(0.5, 1.0),
                "water": random.uniform(0.5, 1.0),
                "earth": random.uniform(0.5, 1.0),
                "air": random.uniform(0.5, 1.0),
                "lightning": random.uniform(0.3, 0.8),
                "ice": random.uniform(0.3, 0.8)
            }
        elif leyline_type == LeylineType.ARCANE:
            affinities = {
                "divination": random.uniform(0.5, 1.0),
                "enchantment": random.uniform(0.5, 1.0),
                "teleportation": random.uniform(0.5, 1.0),
                "transmutation": random.uniform(0.5, 1.0),
                "scrying": random.uniform(0.3, 0.8),
                "warding": random.uniform(0.3, 0.8)
            }
        elif leyline_type == LeylineType.SPIRITUAL:
            affinities = {
                "healing": random.uniform(0.5, 1.0),
                "divinity": random.uniform(0.5, 1.0),
                "necromancy": random.uniform(0.5, 1.0),
                "soul": random.uniform(0.5, 1.0),
                "blessing": random.uniform(0.3, 0.8),
                "curse": random.uniform(0.3, 0.8)
            }
        elif leyline_type == LeylineType.NATURAL:
            affinities = {
                "growth": random.uniform(0.5, 1.0),
                "animal": random.uniform(0.5, 1.0),
                "plant": random.uniform(0.5, 1.0),
                "weather": random.uniform(0.5, 1.0),
                "healing": random.uniform(0.3, 0.8),
                "poison": random.uniform(0.3, 0.8)
            }
        elif leyline_type == LeylineType.VOID:
            affinities = {
                "shadow": random.uniform(0.5, 1.0),
                "chaos": random.uniform(0.5, 1.0),
                "time": random.uniform(0.5, 1.0),
                "distortion": random.uniform(0.5, 1.0),
                "nullification": random.uniform(0.3, 0.8),
                "corruption": random.uniform(0.3, 0.8)
            }
        
        return affinities
        
    def assign_leylines_to_pois(self, region_id: str, pois: List[DBPointOfInterest]):
        """
        Determine which leylines affect which POIs within a region.
        
        Args:
            region_id: ID of the region containing the POIs
            pois: List of POIs to process
        """
        if region_id not in self.region_leyline_map:
            return
        
        region_leylines = [self.leylines[lid] for lid in self.region_leyline_map[region_id]]
        
        for poi in pois:
            # For this example, we'll use a simple model
            # Assuming POIs have a position attribute
            poi_position = getattr(poi, 'position', (random.uniform(0, 100), random.uniform(0, 100)))
            
            for leyline in region_leylines:
                # Calculate influence at the POI's position
                influence = leyline.get_influence_at_point(poi_position)
                
                # If influence is significant, add this POI to the leyline's affected list
                if influence > 0.2:
                    if poi.id not in self.poi_leyline_map:
                        self.poi_leyline_map[poi.id] = []
                    
                    if leyline.id not in self.poi_leyline_map[poi.id]:
                        self.poi_leyline_map[poi.id].append(leyline.id)
                        leyline.affected_pois.add(poi.id)
    
    def get_leylines_for_poi(self, poi_id: str) -> List[Leyline]:
        """
        Get all leylines affecting a specific POI.
        
        Args:
            poi_id: ID of the POI
            
        Returns:
            List of Leyline objects affecting this POI
        """
        if poi_id not in self.poi_leyline_map:
            return []
        
        return [self.leylines[lid] for lid in self.poi_leyline_map[poi_id]]
    
    def get_magical_properties_for_poi(self, poi_id: str) -> Dict[str, Any]:
        """
        Get the combined magical properties for a specific POI based on leylines.
        
        Args:
            poi_id: ID of the POI
            
        Returns:
            Dictionary of magical properties
        """
        leylines = self.get_leylines_for_poi(poi_id)
        
        if not leylines:
            # Default minimal magical properties
            return {
                "magical_strength": 0.1,
                "affinities": {},
                "stability": "stable",
                "magical_phenomena": []
            }
        
        # Combine influences from all leylines
        combined_strength = 0
        combined_affinities = {}
        stability_scores = {
            LeylineStatus.STABLE: 1.0,
            LeylineStatus.FLUCTUATING: 0.6,
            LeylineStatus.DIMINISHING: 0.4,
            LeylineStatus.SURGING: 0.3,
            LeylineStatus.CORRUPTED: 0.2,
            LeylineStatus.FRACTURED: 0.1
        }
        stability_sum = 0
        
        for leyline in leylines:
            # Add strength (with diminishing returns for multiple leylines)
            strength_value = {
                LeylineStrength.WEAK: 0.2,
                LeylineStrength.MODERATE: 0.4,
                LeylineStrength.STRONG: 0.6,
                LeylineStrength.POWERFUL: 0.8,
                LeylineStrength.NEXUS: 1.0
            }.get(leyline.strength, 0.4)
            
            combined_strength += strength_value * (1.0 / len(leylines) ** 0.5)
            
            # Combine affinities
            for affinity, value in leyline.magical_affinity.items():
                if affinity in combined_affinities:
                    # Use the higher value but with a small bonus for overlap
                    combined_affinities[affinity] = max(combined_affinities[affinity], value) + 0.1
                else:
                    combined_affinities[affinity] = value
            
            # Add to stability calculation
            stability_sum += stability_scores.get(leyline.status, 0.5)
        
        # Normalize and cap values
        combined_strength = min(combined_strength, 1.0)
        
        for affinity in combined_affinities:
            combined_affinities[affinity] = min(combined_affinities[affinity], 1.0)
        
        # Calculate overall stability (average of all leylines)
        avg_stability = stability_sum / len(leylines)
        
        if avg_stability > 0.8:
            stability = "very_stable"
        elif avg_stability > 0.6:
            stability = "stable"
        elif avg_stability > 0.4:
            stability = "fluctuating"
        elif avg_stability > 0.2:
            stability = "unstable"
        else:
            stability = "chaotic"
        
        # Generate magical phenomena based on the properties
        magical_phenomena = self._generate_magical_phenomena(
            combined_strength, 
            combined_affinities,
            avg_stability
        )
        
        return {
            "magical_strength": combined_strength,
            "affinities": combined_affinities,
            "stability": stability,
            "magical_phenomena": magical_phenomena
        }
    
    def _generate_magical_phenomena(
        self, 
        strength: float, 
        affinities: Dict[str, float],
        stability: float
    ) -> List[str]:
        """Generate magical phenomena based on magical properties."""
        phenomena = []
        
        # Only generate phenomena if magic is relatively strong
        if strength < 0.3:
            return []
        
        # Number of phenomena based on strength
        num_phenomena = int(strength * 5) + 1
        
        # Get top affinities
        top_affinities = sorted(affinities.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Phenomena by affinity type
        phenomena_options = {
            "fire": [
                "Small objects spontaneously ignite",
                "Temperature rises around strong emotions",
                "Candles burn with unusual colors",
                "Fire spells are especially powerful",
                "Smoke forms into meaningful shapes"
            ],
            "water": [
                "Water flows against gravity",
                "Small persistent rain clouds form indoors",
                "Liquids are exceptionally reflective",
                "Water shows visions of distant places",
                "Tears or sweat may have healing properties"
            ],
            "earth": [
                "Small stones orbit certain objects",
                "Plants grow at accelerated rates",
                "Crystal formations appear in unlikely places",
                "The ground occasionally trembles in patterns",
                "Metals may change properties temporarily"
            ],
            "air": [
                "Breezes carry whispered messages",
                "Small objects float momentarily",
                "Fog forms into distinct shapes",
                "Weather changes rapidly in small areas",
                "Air pressure fluctuates with emotions"
            ],
            "divination": [
                "Dreams reveal fragments of possible futures",
                "Reflective surfaces show glimpses of other places",
                "Some people experience momentary precognition",
                "Cards or dice show improbable patterns",
                "Animals react to events before they occur"
            ],
            "enchantment": [
                "Objects temporarily gain minor magical properties",
                "Colors become more vivid around powerful emotions",
                "Mundane items occasionally function as if enchanted",
                "Spoken promises have unusual binding power",
                "Artwork seems to subtly change when unobserved"
            ],
            "healing": [
                "Minor wounds heal more quickly",
                "Plants with healing properties grow abundantly",
                "Sleep is especially restorative",
                "Water may temporarily gain curative properties",
                "Positive emotions spread more easily between people"
            ],
            "shadow": [
                "Shadows move independently of their casters",
                "Darkness is deeper than it should be",
                "Light sources have reduced radius",
                "Shadows occasionally reveal hidden truths",
                "Dreams are more vivid and meaningful"
            ],
            "chaos": [
                "Probability seems skewed toward unusual outcomes",
                "Small objects relocate when unobserved",
                "Colors shift in peripheral vision",
                "Sound occasionally travels in impossible ways",
                "Time perception varies subtly"
            ]
        }
        
        # Add phenomena based on stability
        if stability < 0.3:
            # Unstable phenomena
            phenomena.extend([
                "Magic flares unpredictably",
                "Spells may have unintended side effects",
                "Magical items function erratically",
                "Reality occasionally ripples or distorts",
                "Emotional states affect magical outcomes dramatically"
            ][:2])
        
        # Add phenomena based on top affinities
        for affinity, value in top_affinities:
            if affinity in phenomena_options:
                # Number of phenomena from this affinity based on its strength
                count = min(int(value * 3) + 1, len(phenomena_options[affinity]))
                
                # Add random selections from this affinity's phenomena
                selected = random.sample(phenomena_options[affinity], count)
                phenomena.extend(selected)
        
        # Ensure we don't exceed the desired number
        if len(phenomena) > num_phenomena:
            phenomena = random.sample(phenomena, num_phenomena)
        
        return phenomena
    
    def modify_poi_based_on_leylines(self, poi: DBPointOfInterest) -> Dict[str, Any]:
        """
        Generate additional details for a POI based on its leyline influences.
        
        Args:
            poi: The POI to enhance with magical details
            
        Returns:
            Dictionary of additional magical details for the POI
        """
        magical_properties = self.get_magical_properties_for_poi(poi.id)
        
        # Enhance POI details based on magical properties
        details = {
            "magical_strength": magical_properties["magical_strength"],
            "magical_stability": magical_properties["stability"],
            "major_affinities": [],
            "magical_phenomena": magical_properties["magical_phenomena"],
            "magical_resources": [],
            "magical_hazards": []
        }
        
        # Add major affinities
        for affinity, value in magical_properties["affinities"].items():
            if value > 0.5:
                details["major_affinities"].append(affinity)
        
        # Generate resources based on magical properties
        if magical_properties["magical_strength"] > 0.3:
            resources = self._generate_magical_resources(
                magical_properties["magical_strength"],
                magical_properties["affinities"],
                magical_properties["stability"]
            )
            details["magical_resources"] = resources
        
        # Generate hazards based on magical properties
        if magical_properties["magical_strength"] > 0.4 or magical_properties["stability"] == "unstable":
            hazards = self._generate_magical_hazards(
                magical_properties["magical_strength"],
                magical_properties["affinities"],
                magical_properties["stability"]
            )
            details["magical_hazards"] = hazards
        
        return details
    
    def _generate_magical_resources(
        self, 
        strength: float, 
        affinities: Dict[str, float],
        stability: str
    ) -> List[Dict[str, Any]]:
        """Generate magical resources that might be found at this location."""
        resources = []
        
        # Number of resources based on strength
        num_resources = int(strength * 4) + 1
        
        # Get top affinities
        top_affinities = sorted(affinities.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Resource options by affinity
        resource_options = {
            "fire": [
                {"name": "Ember Crystals", "rarity": "uncommon", "use": "Fire magic enhancement"},
                {"name": "Phoenix Feathers", "rarity": "rare", "use": "Resurrection spells"},
                {"name": "Magma Essence", "rarity": "uncommon", "use": "Heat-based enchantments"}
            ],
            "water": [
                {"name": "Aqua Pearls", "rarity": "uncommon", "use": "Water breathing enchantments"},
                {"name": "Tidal Crystals", "rarity": "rare", "use": "Weather control magic"},
                {"name": "Mermaid Scales", "rarity": "rare", "use": "Water manipulation spells"}
            ],
            "earth": [
                {"name": "Terravite Ore", "rarity": "common", "use": "Earth magic conductivity"},
                {"name": "Crystal Geodes", "rarity": "uncommon", "use": "Spell stabilization"},
                {"name": "Ancient Roots", "rarity": "uncommon", "use": "Growth enchantments"}
            ],
            "air": [
                {"name": "Windstone", "rarity": "uncommon", "use": "Levitation enchantments"},
                {"name": "Sylph Dust", "rarity": "rare", "use": "Air magic enhancement"},
                {"name": "Lightning Quartz", "rarity": "rare", "use": "Energy storage"}
            ],
            "divination": [
                {"name": "Prophetic Crystal", "rarity": "rare", "use": "Fortune telling"},
                {"name": "Vision Ink", "rarity": "uncommon", "use": "Scrying enhancement"},
                {"name": "Dream Feathers", "rarity": "rare", "use": "Prophetic dreams"}
            ],
            "enchantment": [
                {"name": "Arcane Dust", "rarity": "common", "use": "General enchantments"},
                {"name": "Spellweave Silk", "rarity": "uncommon", "use": "Wearable enchantments"},
                {"name": "Binding Crystals", "rarity": "rare", "use": "Permanent enchantments"}
            ],
            "healing": [
                {"name": "Vitality Herbs", "rarity": "common", "use": "Healing potions"},
                {"name": "Life Crystals", "rarity": "rare", "use": "Resurrection magic"},
                {"name": "Spirit Flowers", "rarity": "uncommon", "use": "Mental healing"}
            ],
            "shadow": [
                {"name": "Void Crystals", "rarity": "rare", "use": "Shadow magic enhancement"},
                {"name": "Umbral Essence", "rarity": "uncommon", "use": "Invisibility spells"},
                {"name": "Night Petals", "rarity": "uncommon", "use": "Dream manipulation"}
            ],
            "chaos": [
                {"name": "Flux Stones", "rarity": "rare", "use": "Reality manipulation"},
                {"name": "Chaos Amber", "rarity": "rare", "use": "Unpredictable magic boosting"},
                {"name": "Probability Dust", "rarity": "rare", "use": "Luck enchantments"}
            ]
        }
        
        # Generate resources based on top affinities
        for affinity, value in top_affinities:
            if affinity in resource_options:
                # Determine how many resources from this affinity
                options = resource_options[affinity]
                
                # Higher affinity value means more likely to get rarer resources
                if value > 0.8 and random.random() < 0.7:
                    # Likely to get rare resources
                    rare_options = [r for r in options if r["rarity"] == "rare"]
                    if rare_options:
                        resources.append(random.choice(rare_options))
                elif value > 0.5:
                    # Mix of uncommon and rare
                    better_options = [r for r in options if r["rarity"] in ["uncommon", "rare"]]
                    if better_options:
                        resources.append(random.choice(better_options))
                else:
                    # Any rarity
                    resources.append(random.choice(options))
        
        # Ensure we don't exceed the desired number
        if len(resources) > num_resources:
            resources = random.sample(resources, num_resources)
        
        # Add quantity and quality
        for resource in resources:
            resource["quantity"] = random.choice(["trace", "small", "moderate", "abundant"])
            resource["quality"] = random.choice(["poor", "average", "good", "excellent"])
        
        return resources
    
    def _generate_magical_hazards(
        self, 
        strength: float, 
        affinities: Dict[str, float],
        stability: str
    ) -> List[Dict[str, Any]]:
        """Generate magical hazards that might be present at this location."""
        hazards = []
        
        # Number of hazards based on strength and stability
        base_hazards = int(strength * 3)
        if stability == "unstable":
            base_hazards += 2
        elif stability == "chaotic":
            base_hazards += 3
        
        num_hazards = max(1, min(base_hazards, 4))  # Between 1 and 4 hazards
        
        # Get top affinities
        top_affinities = sorted(affinities.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Hazard options by affinity
        hazard_options = {
            "fire": [
                {"name": "Spontaneous Combustion", "severity": "moderate", "effect": "Random objects ignite"},
                {"name": "Heat Surges", "severity": "minor", "effect": "Periodic waves of intense heat"},
                {"name": "Flame Sprites", "severity": "moderate", "effect": "Small fire elementals that cause mischief"}
            ],
            "water": [
                {"name": "Drowning Air", "severity": "severe", "effect": "Pockets of air filled with water magic"},
                {"name": "Flash Floods", "severity": "moderate", "effect": "Sudden manifestations of water"},
                {"name": "Water Mimics", "severity": "minor", "effect": "Puddles that animate and attack"}
            ],
            "earth": [
                {"name": "Stone Sickness", "severity": "moderate", "effect": "Progressive petrification"},
                {"name": "Quicksand Pockets", "severity": "minor", "effect": "Ground becomes unstable"},
                {"name": "Crystal Growths", "severity": "minor", "effect": "Crystals grow on organic matter"}
            ],
            "air": [
                {"name": "Vacuum Pockets", "severity": "severe", "effect": "Areas devoid of air"},
                {"name": "Wind Blades", "severity": "moderate", "effect": "Invisible cutting air currents"},
                {"name": "Whisper Madness", "severity": "minor", "effect": "Voices on the wind cause confusion"}
            ],
            "divination": [
                {"name": "Future Echoes", "severity": "minor", "effect": "Distracting visions of possible futures"},
                {"name": "Fate Tangles", "severity": "moderate", "effect": "Actions have unpredictable outcomes"},
                {"name": "Truth Compulsion", "severity": "minor", "effect": "Inability to lie or withhold information"}
            ],
            "enchantment": [
                {"name": "Wild Enchantment", "severity": "moderate", "effect": "Items gain random magical properties"},
                {"name": "Memory Fog", "severity": "minor", "effect": "Recent memories become confused"},
                {"name": "Binding Aura", "severity": "moderate", "effect": "Movement becomes restricted"}
            ],
            "healing": [
                {"name": "Overgrowth", "severity": "minor", "effect": "Wounds heal with excessive tissue"},
                {"name": "Life Drain", "severity": "moderate", "effect": "Vitality is slowly sapped"},
                {"name": "Immortal Moment", "severity": "severe", "effect": "Time stops for the affected"}
            ],
            "shadow": [
                {"name": "Shadow Predators", "severity": "severe", "effect": "Animated shadows attack"},
                {"name": "Darkness Pockets", "severity": "moderate", "effect": "Areas of impenetrable darkness"},
                {"name": "Emotional Drain", "severity": "minor", "effect": "Feelings of despair and hopelessness"}
            ],
            "chaos": [
                {"name": "Reality Flux", "severity": "severe", "effect": "Physics behave unpredictably"},
                {"name": "Transformation Waves", "severity": "moderate", "effect": "Physical form alters temporarily"},
                {"name": "Chaos Infection", "severity": "moderate", "effect": "Magic becomes unpredictable"}
            ]
        }
        
        # Always add hazards based on stability if unstable
        if stability in ["unstable", "chaotic"]:
            instability_hazards = [
                {"name": "Spell Backfire", "severity": "moderate", "effect": "Magic has unintended consequences"},
                {"name": "Leyline Surge", "severity": "severe", "effect": "Random bursts of pure magical energy"},
                {"name": "Reality Tears", "severity": "severe", "effect": "Rifts to other planes open randomly"},
                {"name": "Time Distortion", "severity": "moderate", "effect": "Time flows at different rates"}
            ]
            hazards.append(random.choice(instability_hazards))
        
        # Generate hazards based on top affinities
        for affinity, value in top_affinities:
            if affinity in hazard_options and len(hazards) < num_hazards:
                options = hazard_options[affinity]
                
                # Higher affinity and higher strength means more dangerous hazards
                if strength > 0.7 and value > 0.7:
                    # Likely to get severe hazards
                    severe_options = [h for h in options if h["severity"] == "severe"]
                    if severe_options:
                        hazards.append(random.choice(severe_options))
                    else:
                        hazards.append(random.choice(options))
                elif strength > 0.5 or value > 0.6:
                    # Likely to get moderate hazards
                    mod_options = [h for h in options if h["severity"] in ["moderate", "severe"]]
                    if mod_options:
                        hazards.append(random.choice(mod_options))
                    else:
                        hazards.append(random.choice(options))
                else:
                    # Any severity
                    hazards.append(random.choice(options))
        
        # Ensure we don't exceed the desired number
        if len(hazards) > num_hazards:
            hazards = random.sample(hazards, num_hazards)
        
        # Add frequency and detectability
        for hazard in hazards:
            hazard["frequency"] = random.choice(["rare", "occasional", "common", "constant"])
            hazard["detectability"] = random.choice(["obvious", "noticeable", "subtle", "hidden"])
        
        return hazards