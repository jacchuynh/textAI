"""
Magical Materials System - Components for magical crafting materials

This module provides systems for managing magical materials that can be found
in different regions and locations, as well as their properties and uses in
magical crafting and enchantment.
"""

import random
import math
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Set

from world_generation.world_model import BiomeType, POIType, DBRegion, DBBiome, DBPointOfInterest
from magic_system.leyline_manager import LeylineManager, LeylineType


class MaterialRarity(str, Enum):
    """Rarity levels for magical materials."""
    COMMON = "common"           # Easily found in many locations
    UNCOMMON = "uncommon"       # Found in specific biomes or conditions
    RARE = "rare"               # Difficult to find, requires specific conditions
    VERY_RARE = "very_rare"     # Extremely difficult to find, special conditions
    LEGENDARY = "legendary"     # Unique or nearly unique materials


class MaterialType(str, Enum):
    """Primary categories of magical materials."""
    METAL = "metal"             # Magical metals and alloys
    CRYSTAL = "crystal"         # Crystalline formations with magical properties
    HERB = "herb"               # Plants with magical properties
    FLUID = "fluid"             # Liquids with magical properties
    ESSENCE = "essence"         # Pure magical essences
    ORGANIC = "organic"         # Animal or monster parts
    MINERAL = "mineral"         # Non-metallic minerals
    FABRIC = "fabric"           # Magical cloths and fibers
    WOOD = "wood"               # Magical woods and plant materials
    COMPOUND = "compound"       # Complex materials made of multiple components


class MaterialState(str, Enum):
    """Physical states of magical materials."""
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"
    PLASMA = "plasma"
    ETHEREAL = "ethereal"       # Not fully physical
    CRYSTALLINE = "crystalline" # Organized solid structure
    AMORPHOUS = "amorphous"     # Solid without crystal structure


class MagicalMaterial:
    """
    Represents a type of magical material that can be found in the world.
    """
    def __init__(
        self,
        material_id: str,
        name: str,
        description: str,
        material_type: MaterialType,
        rarity: MaterialRarity,
        state: MaterialState,
        primary_element: str,
        secondary_elements: List[str],
        magical_properties: Dict[str, float],
        typical_locations: List[str],
        harvesting_difficulty: float,  # 0.0 to 1.0
        processing_requirements: List[str],
        crafting_uses: List[str],
        value_per_unit: int,
        lore: Optional[str] = None,
        special_effects: Optional[List[str]] = None
    ):
        self.id = material_id
        self.name = name
        self.description = description
        self.material_type = material_type
        self.rarity = rarity
        self.state = state
        self.primary_element = primary_element
        self.secondary_elements = secondary_elements
        self.magical_properties = magical_properties
        self.typical_locations = typical_locations
        self.harvesting_difficulty = harvesting_difficulty
        self.processing_requirements = processing_requirements
        self.crafting_uses = crafting_uses
        self.value_per_unit = value_per_unit
        self.lore = lore
        self.special_effects = special_effects or []
    
    def __str__(self):
        return f"{self.name} ({self.material_type}, {self.rarity})"


class MaterialInstance:
    """
    An instance of a magical material with specific quantity and quality.
    """
    def __init__(
        self,
        instance_id: str,
        material: MagicalMaterial,
        quantity: float,
        quality: float,  # 0.0 to 1.0
        location_found: Optional[str] = None,
        harvested_by: Optional[str] = None,
        processing_level: int = 0,  # 0=raw, 1=processed, 2=refined, etc.
        special_traits: List[str] = None
    ):
        self.id = instance_id
        self.material = material
        self.quantity = quantity
        self.quality = quality
        self.location_found = location_found
        self.harvested_by = harvested_by
        self.processing_level = processing_level
        self.special_traits = special_traits or []
    
    def get_value(self) -> int:
        """Calculate the total value of this material instance."""
        # Base value per unit
        base_value = self.material.value_per_unit
        
        # Quality multiplier
        quality_mult = 0.5 + (self.quality * 1.5)  # 0.5x to 2.0x
        
        # Processing level multiplier
        processing_mult = 1.0 + (self.processing_level * 0.5)  # 1.0x to 3.0x for fully refined
        
        # Special traits bonus
        special_bonus = len(self.special_traits) * 0.2  # +20% per special trait
        
        total_value = int(base_value * self.quantity * quality_mult * processing_mult * (1 + special_bonus))
        return total_value
    
    def process(self) -> bool:
        """
        Process the material to the next level.
        
        Returns:
            True if processing was successful, False if already at max level
        """
        # Maximum processing level is 3 (raw, processed, refined, perfected)
        if self.processing_level >= 3:
            return False
        
        self.processing_level += 1
        
        # Processing reduces quantity slightly
        efficiency = 0.8 + (self.quality * 0.15)  # 80-95% efficiency based on quality
        self.quantity *= efficiency
        
        return True
    
    def __str__(self):
        processing_levels = ["Raw", "Processed", "Refined", "Perfected"]
        processing_desc = processing_levels[min(self.processing_level, 3)]
        quality_desc = "Poor" if self.quality < 0.3 else "Average" if self.quality < 0.6 else "Good" if self.quality < 0.8 else "Excellent"
        
        return f"{processing_desc} {self.material.name} ({quality_desc}, {self.quantity:.1f} units)"


class MagicalMaterialsManager:
    """
    System for managing magical materials, their generation, and distribution.
    """
    def __init__(self, leyline_manager: Optional[LeylineManager] = None):
        self.materials: Dict[str, MagicalMaterial] = {}
        self.material_instances: Dict[str, MaterialInstance] = {}
        self.leyline_manager = leyline_manager or LeylineManager()
        
        # Maps from biome types to material types commonly found there
        self.biome_material_affinities: Dict[BiomeType, List[Tuple[MaterialType, float]]] = {}
        
        # Maps from POI types to material types commonly found there
        self.poi_material_affinities: Dict[POIType, List[Tuple[MaterialType, float]]] = {}
        
        # Initialize material library
        self._load_default_materials()
        self._initialize_biome_affinities()
        self._initialize_poi_affinities()
    
    def _load_default_materials(self):
        """Load a set of default magical materials."""
        # Metals
        self.materials["sunmetal"] = MagicalMaterial(
            material_id="sunmetal",
            name="Sunmetal",
            description="A golden metal that glows warmly and is unusually light.",
            material_type=MaterialType.METAL,
            rarity=MaterialRarity.RARE,
            state=MaterialState.SOLID,
            primary_element="fire",
            secondary_elements=["light"],
            magical_properties={
                "light_manipulation": 0.8,
                "heat_resistance": 0.9,
                "enchantment_capacity": 0.7
            },
            typical_locations=["mountains", "volcanoes", "ancient_ruins"],
            harvesting_difficulty=0.7,
            processing_requirements=["high_heat", "magical_forge"],
            crafting_uses=["weapons", "light_focusing_devices", "protective_amulets"],
            value_per_unit=200,
            lore="First discovered by ancient sun worshippers, this metal is said to contain the essence of the sun itself."
        )
        
        self.materials["moonshadow_steel"] = MagicalMaterial(
            material_id="moonshadow_steel",
            name="Moonshadow Steel",
            description="A dark blue-black metal that seems to absorb light. Unusually hard and resilient.",
            material_type=MaterialType.METAL,
            rarity=MaterialRarity.VERY_RARE,
            state=MaterialState.SOLID,
            primary_element="shadow",
            secondary_elements=["water"],
            magical_properties={
                "shadow_manipulation": 0.9,
                "durability": 0.8,
                "spell_focusing": 0.7
            },
            typical_locations=["deep_caves", "ancient_battlefields", "cursed_lands"],
            harvesting_difficulty=0.8,
            processing_requirements=["moonlight_forging", "cold_working", "shadow_essence"],
            crafting_uses=["weapons", "armor", "scrying_devices", "shadow_magic_foci"],
            value_per_unit=350,
            lore="Legend holds that moonshadow steel was first forged by shadow elves seeking to create the perfect weapon against light creatures."
        )
        
        # Crystals
        self.materials["aether_crystal"] = MagicalMaterial(
            material_id="aether_crystal",
            name="Aether Crystal",
            description="Translucent crystals with swirling colors that seem to shift as you watch them.",
            material_type=MaterialType.CRYSTAL,
            rarity=MaterialRarity.RARE,
            state=MaterialState.CRYSTALLINE,
            primary_element="air",
            secondary_elements=["space"],
            magical_properties={
                "mana_storage": 0.9,
                "spell_amplification": 0.8,
                "elemental_attunement": 0.7
            },
            typical_locations=["high_mountains", "leyline_nexus", "magical_wastelands"],
            harvesting_difficulty=0.6,
            processing_requirements=["resonant_tools", "stabilization_chamber", "expert_handling"],
            crafting_uses=["wands", "staves", "magical_foci", "enchanted_jewelry"],
            value_per_unit=300,
            lore="Aether crystals are believed to be crystallized mana from the early days of creation."
        )
        
        self.materials["dreamstone"] = MagicalMaterial(
            material_id="dreamstone",
            name="Dreamstone",
            description="Opalescent crystals that seem to contain swirling mists. They hum softly when touched.",
            material_type=MaterialType.CRYSTAL,
            rarity=MaterialRarity.VERY_RARE,
            state=MaterialState.CRYSTALLINE,
            primary_element="mind",
            secondary_elements=["void"],
            magical_properties={
                "dream_manipulation": 0.9,
                "mental_enhancement": 0.8,
                "illusion_casting": 0.9
            },
            typical_locations=["ancient_ruins", "deep_caves", "magical_groves"],
            harvesting_difficulty=0.8,
            processing_requirements=["dream_infusion", "moonlight_polishing", "mental_focusing"],
            crafting_uses=["scrying_orbs", "dream_catchers", "illusion_devices", "mind-affecting_items"],
            value_per_unit=450,
            lore="Dreamstones are said to be fragments of the realm of dreams that have somehow crossed into the waking world."
        )
        
        # Herbs
        self.materials["frostbloom"] = MagicalMaterial(
            material_id="frostbloom",
            name="Frostbloom",
            description="Pale blue flowers that remain cool to the touch even in extreme heat.",
            material_type=MaterialType.HERB,
            rarity=MaterialRarity.UNCOMMON,
            state=MaterialState.SOLID,
            primary_element="water",
            secondary_elements=["air"],
            magical_properties={
                "cold_manipulation": 0.7,
                "preservation": 0.8,
                "healing_enhancement": 0.5
            },
            typical_locations=["tundra", "high_mountains", "glaciers"],
            harvesting_difficulty=0.4,
            processing_requirements=["cold_pressing", "quick_drying", "moonlight_exposure"],
            crafting_uses=["healing_potions", "cold_resistance_elixirs", "preservation_charms"],
            value_per_unit=75,
            lore="Frostblooms are said to bloom only where winter spirits have danced."
        )
        
        self.materials["sunfire_sage"] = MagicalMaterial(
            material_id="sunfire_sage",
            name="Sunfire Sage",
            description="Vibrant red and orange herbs that feel warm to the touch and give off a spicy aroma.",
            material_type=MaterialType.HERB,
            rarity=MaterialRarity.UNCOMMON,
            state=MaterialState.SOLID,
            primary_element="fire",
            secondary_elements=["life"],
            magical_properties={
                "fire_resistance": 0.7,
                "energy_enhancement": 0.8,
                "healing_acceleration": 0.6
            },
            typical_locations=["volcanic_regions", "deserts", "fire_elemental_nexus"],
            harvesting_difficulty=0.5,
            processing_requirements=["sun_drying", "flame_curing", "oil_extraction"],
            crafting_uses=["fire_resistance_potions", "energy_elixirs", "healing_salves", "combat_stimulants"],
            value_per_unit=90,
            lore="Ancient fire priests used sunfire sage in their rituals to commune with flame spirits."
        )
        
        # Fluids
        self.materials["moonlight_dew"] = MagicalMaterial(
            material_id="moonlight_dew",
            name="Moonlight Dew",
            description="Silvery liquid that glows softly in darkness and evaporates in direct sunlight.",
            material_type=MaterialType.FLUID,
            rarity=MaterialRarity.RARE,
            state=MaterialState.LIQUID,
            primary_element="light",
            secondary_elements=["water", "time"],
            magical_properties={
                "time_manipulation": 0.6,
                "healing": 0.7,
                "illusion_enhancement": 0.8
            },
            typical_locations=["enchanted_forests", "sacred_groves", "ancient_springs"],
            harvesting_difficulty=0.7,
            processing_requirements=["silver_containers", "nighttime_collection", "magical_stabilization"],
            crafting_uses=["healing_potions", "divination_media", "enchantment_bases", "youth_elixirs"],
            value_per_unit=250,
            lore="Moonlight dew is said to be the tears of the moon goddess, shed for her lost love."
        )
        
        self.materials["vital_ichor"] = MagicalMaterial(
            material_id="vital_ichor",
            name="Vital Ichor",
            description="Thick, golden fluid that pulses with a gentle rhythm and smells of honey and spices.",
            material_type=MaterialType.FLUID,
            rarity=MaterialRarity.VERY_RARE,
            state=MaterialState.LIQUID,
            primary_element="life",
            secondary_elements=["earth"],
            magical_properties={
                "vitality_enhancement": 0.9,
                "healing_amplification": 0.8,
                "life_preservation": 0.9
            },
            typical_locations=["heart_of_ancient_forests", "life_leyline_nexus", "sacred_springs"],
            harvesting_difficulty=0.9,
            processing_requirements=["blessed_containers", "life_energy_infusion", "alchemical_stabilization"],
            crafting_uses=["supreme_healing_potions", "resurrection_elixirs", "life-preserving_amulets"],
            value_per_unit=500,
            lore="Vital ichor is believed to be the pure essence of life itself, condensed into liquid form."
        )
        
        # Essences
        self.materials["void_essence"] = MagicalMaterial(
            material_id="void_essence",
            name="Void Essence",
            description="A strange, dark substance that seems to absorb light and sound. It feels unnaturally cold.",
            material_type=MaterialType.ESSENCE,
            rarity=MaterialRarity.VERY_RARE,
            state=MaterialState.ETHEREAL,
            primary_element="void",
            secondary_elements=["shadow", "death"],
            magical_properties={
                "void_manipulation": 0.9,
                "reality_warping": 0.7,
                "spell_negation": 0.8
            },
            typical_locations=["dimensional_rifts", "ancient_ruins", "sites_of_great_calamities"],
            harvesting_difficulty=0.9,
            processing_requirements=["void-attuned_containers", "anti-magic_field", "soul_protection"],
            crafting_uses=["reality_manipulation_devices", "null_magic_zones", "powerful_destructive_weapons"],
            value_per_unit=700,
            lore="Some scholars believe void essence is actually matter from between dimensions, leaking into our reality."
        )
        
        self.materials["elemental_harmony"] = MagicalMaterial(
            material_id="elemental_harmony",
            name="Elemental Harmony",
            description="A swirling, iridescent substance that constantly shifts between different elemental states.",
            material_type=MaterialType.ESSENCE,
            rarity=MaterialRarity.LEGENDARY,
            state=MaterialState.ETHEREAL,
            primary_element="balance",
            secondary_elements=["fire", "water", "earth", "air"],
            magical_properties={
                "elemental_balance": 1.0,
                "spell_enhancement": 0.9,
                "magical_stability": 0.9
            },
            typical_locations=["elemental_convergences", "planar_crossroads", "primordial_sites"],
            harvesting_difficulty=1.0,
            processing_requirements=["elemental_containment", "perfect_balance_maintenance", "master_alchemist"],
            crafting_uses=["legendary_artifacts", "elemental_mastery_items", "universal_spell_catalysts"],
            value_per_unit=1000,
            lore="Elemental harmony is created only when all four primordial elements achieve perfect balance."
        )
    
    def _initialize_biome_affinities(self):
        """Initialize the affinities between biome types and material types."""
        self.biome_material_affinities = {
            BiomeType.VERDANT_FRONTIER: [
                (MaterialType.HERB, 0.8),
                (MaterialType.WOOD, 0.7),
                (MaterialType.ORGANIC, 0.6),
                (MaterialType.FABRIC, 0.5)
            ],
            BiomeType.EMBER_WASTES: [
                (MaterialType.METAL, 0.8),
                (MaterialType.MINERAL, 0.7),
                (MaterialType.CRYSTAL, 0.6),
                (MaterialType.ESSENCE, 0.4)
            ],
            BiomeType.WHISPERING_WOODS: [
                (MaterialType.WOOD, 0.9),
                (MaterialType.HERB, 0.8),
                (MaterialType.ORGANIC, 0.7),
                (MaterialType.ESSENCE, 0.6)
            ],
            BiomeType.CRYSTAL_HIGHLANDS: [
                (MaterialType.CRYSTAL, 0.9),
                (MaterialType.MINERAL, 0.8),
                (MaterialType.ESSENCE, 0.7),
                (MaterialType.METAL, 0.5)
            ],
            BiomeType.SHIMMERING_MARSHES: [
                (MaterialType.FLUID, 0.9),
                (MaterialType.HERB, 0.7),
                (MaterialType.ORGANIC, 0.7),
                (MaterialType.ESSENCE, 0.5)
            ],
            BiomeType.FROSTBOUND_TUNDRA: [
                (MaterialType.CRYSTAL, 0.8),
                (MaterialType.FLUID, 0.7),
                (MaterialType.ESSENCE, 0.6),
                (MaterialType.HERB, 0.4)
            ],
            BiomeType.CRIMSON_SCARS: [
                (MaterialType.ESSENCE, 0.9),
                (MaterialType.METAL, 0.7),
                (MaterialType.CRYSTAL, 0.6),
                (MaterialType.FLUID, 0.5)
            ],
            BiomeType.RELIC_ZONES: [
                (MaterialType.ESSENCE, 0.9),
                (MaterialType.COMPOUND, 0.8),
                (MaterialType.METAL, 0.7),
                (MaterialType.CRYSTAL, 0.6)
            ]
        }
    
    def _initialize_poi_affinities(self):
        """Initialize the affinities between POI types and material types."""
        self.poi_material_affinities = {
            POIType.VILLAGE: [
                (MaterialType.HERB, 0.7),
                (MaterialType.FABRIC, 0.6),
                (MaterialType.WOOD, 0.6),
                (MaterialType.METAL, 0.4)
            ],
            POIType.RUIN: [
                (MaterialType.ESSENCE, 0.8),
                (MaterialType.METAL, 0.7),
                (MaterialType.CRYSTAL, 0.6),
                (MaterialType.COMPOUND, 0.5)
            ],
            POIType.CAVE: [
                (MaterialType.MINERAL, 0.8),
                (MaterialType.CRYSTAL, 0.7),
                (MaterialType.METAL, 0.6),
                (MaterialType.FLUID, 0.4)
            ],
            POIType.DANGEROUS_CAVE: [
                (MaterialType.CRYSTAL, 0.8),
                (MaterialType.ESSENCE, 0.7),
                (MaterialType.MINERAL, 0.6),
                (MaterialType.ORGANIC, 0.5)
            ],
            POIType.SHRINE: [
                (MaterialType.ESSENCE, 0.9),
                (MaterialType.CRYSTAL, 0.8),
                (MaterialType.FLUID, 0.6),
                (MaterialType.METAL, 0.5)
            ],
            POIType.TOWER: [
                (MaterialType.ESSENCE, 0.8),
                (MaterialType.CRYSTAL, 0.7),
                (MaterialType.METAL, 0.6),
                (MaterialType.COMPOUND, 0.5)
            ],
            POIType.GROVE: [
                (MaterialType.HERB, 0.9),
                (MaterialType.WOOD, 0.8),
                (MaterialType.FLUID, 0.7),
                (MaterialType.ESSENCE, 0.6)
            ],
            POIType.MINE: [
                (MaterialType.METAL, 0.9),
                (MaterialType.MINERAL, 0.8),
                (MaterialType.CRYSTAL, 0.7),
                (MaterialType.ESSENCE, 0.4)
            ],
            POIType.BATTLEFIELD: [
                (MaterialType.ESSENCE, 0.8),
                (MaterialType.METAL, 0.7),
                (MaterialType.ORGANIC, 0.5),
                (MaterialType.CRYSTAL, 0.4)
            ],
            POIType.RELIC_SITE: [
                (MaterialType.ESSENCE, 0.9),
                (MaterialType.COMPOUND, 0.8),
                (MaterialType.CRYSTAL, 0.7),
                (MaterialType.METAL, 0.6)
            ]
        }
    
    def add_material(self, material: MagicalMaterial) -> bool:
        """
        Add a new magical material to the system.
        
        Args:
            material: The material to add
            
        Returns:
            True if added successfully, False if ID already exists
        """
        if material.id in self.materials:
            return False
        
        self.materials[material.id] = material
        return True
    
    def get_material(self, material_id: str) -> Optional[MagicalMaterial]:
        """Get a material by ID."""
        return self.materials.get(material_id)
    
    def get_materials_by_type(self, material_type: MaterialType) -> List[MagicalMaterial]:
        """Get all materials of a specific type."""
        return [m for m in self.materials.values() if m.material_type == material_type]
    
    def get_materials_by_element(self, element: str) -> List[MagicalMaterial]:
        """Get all materials with a specific primary or secondary element."""
        return [
            m for m in self.materials.values() 
            if m.primary_element == element or element in m.secondary_elements
        ]
    
    def get_materials_by_rarity(self, rarity: MaterialRarity) -> List[MagicalMaterial]:
        """Get all materials of a specific rarity."""
        return [m for m in self.materials.values() if m.rarity == rarity]
    
    def create_material_instance(
        self,
        material_id: str,
        quantity: float,
        quality: Optional[float] = None,
        location_found: Optional[str] = None,
        harvested_by: Optional[str] = None,
        special_traits: List[str] = None
    ) -> Optional[MaterialInstance]:
        """
        Create a new instance of a magical material.
        
        Args:
            material_id: ID of the material type
            quantity: Amount of the material
            quality: Quality of the material (0.0 to 1.0), random if None
            location_found: ID of the location where found
            harvested_by: ID of the character who harvested it
            special_traits: List of special traits
            
        Returns:
            New material instance or None if material type not found
        """
        if material_id not in self.materials:
            return None
        
        material = self.materials[material_id]
        
        # Generate a quality value if not provided
        if quality is None:
            # Base quality is random
            quality = random.uniform(0.3, 0.8)
            
            # Location can affect quality if provided
            if location_found:
                magical_props = self.leyline_manager.get_magical_properties_for_poi(location_found)
                if magical_props:
                    # Higher magical strength can improve quality
                    quality += magical_props["magical_strength"] * 0.2
                    
                    # Matching elements can improve quality
                    for element in [material.primary_element] + material.secondary_elements:
                        if element in magical_props["affinities"]:
                            quality += magical_props["affinities"][element] * 0.1
            
            # Cap quality between 0.1 and 1.0
            quality = max(0.1, min(1.0, quality))
        
        # Generate instance ID
        instance_id = f"material_instance_{material_id}_{len(self.material_instances)}"
        
        # Create the instance
        instance = MaterialInstance(
            instance_id=instance_id,
            material=material,
            quantity=quantity,
            quality=quality,
            location_found=location_found,
            harvested_by=harvested_by,
            processing_level=0,
            special_traits=special_traits
        )
        
        # Store and return the instance
        self.material_instances[instance_id] = instance
        return instance
    
    def generate_materials_for_location(
        self,
        location_id: str,
        biome_type: BiomeType,
        poi_type: POIType,
        search_effort: float = 0.5,  # 0.0 to 1.0
        searcher_skill: float = 0.5,  # 0.0 to 1.0
        magic_affinity: Dict[str, float] = None  # elemental affinities of searcher
    ) -> List[MaterialInstance]:
        """
        Generate materials that could be found at a specific location.
        
        Args:
            location_id: ID of the location
            biome_type: Biome type of the location
            poi_type: POI type of the location
            search_effort: How much effort is put into searching (affects quantity)
            searcher_skill: Skill level of the searcher (affects quality and finding rare materials)
            magic_affinity: Elemental affinities of the searcher (affects finding matching materials)
            
        Returns:
            List of material instances found at this location
        """
        found_materials = []
        
        # Get magical properties of the location
        magical_props = self.leyline_manager.get_magical_properties_for_poi(location_id)
        magical_strength = magical_props["magical_strength"] if magical_props else 0.2
        
        # Determine the number of different materials to find
        base_material_count = 1 + int(search_effort * 3) + int(searcher_skill * 2)
        # Magical locations yield more materials
        material_count = int(base_material_count * (1 + magical_strength * 0.5))
        
        # Get affinities for this biome and POI type
        biome_affinities = self.biome_material_affinities.get(biome_type, [])
        poi_affinities = self.poi_material_affinities.get(poi_type, [])
        
        # Combine affinities, with POI having a bit more weight
        combined_affinities = {}
        for material_type, affinity in biome_affinities:
            combined_affinities[material_type] = affinity * 0.4
        
        for material_type, affinity in poi_affinities:
            if material_type in combined_affinities:
                combined_affinities[material_type] += affinity * 0.6
            else:
                combined_affinities[material_type] = affinity * 0.6
        
        # Normalize affinities
        if combined_affinities:
            max_affinity = max(combined_affinities.values())
            for material_type in combined_affinities:
                combined_affinities[material_type] /= max_affinity
        
        # Limit to maximum materials we can find
        material_count = min(material_count, len(self.materials))
        
        # Convert affinities to weighted list for random selection
        material_type_weights = []
        for material_type, affinity in combined_affinities.items():
            material_type_weights.append((material_type, affinity))
        
        # If no affinities, use all material types with equal weight
        if not material_type_weights:
            material_type_weights = [(material_type, 1.0) for material_type in MaterialType]
        
        # Randomly select material types based on affinities
        selected_materials = []
        for _ in range(material_count):
            if not material_type_weights:
                break
            
            # Select a material type based on weights
            weights = [w for _, w in material_type_weights]
            material_type = random.choices(
                [t for t, _ in material_type_weights],
                weights=weights,
                k=1
            )[0]
            
            # Find materials of this type
            matching_materials = self.get_materials_by_type(material_type)
            
            if not matching_materials:
                # Remove this material type from consideration and retry
                material_type_weights = [(t, w) for t, w in material_type_weights if t != material_type]
                continue
            
            # Calculate rarity weights based on searcher skill
            rarity_weights = {
                MaterialRarity.COMMON: 0.5 - (searcher_skill * 0.3),      # Less common as skill increases
                MaterialRarity.UNCOMMON: 0.3,                             # Steady
                MaterialRarity.RARE: 0.1 + (searcher_skill * 0.2),        # More likely as skill increases
                MaterialRarity.VERY_RARE: 0.05 + (searcher_skill * 0.15), # More likely as skill increases
                MaterialRarity.LEGENDARY: 0.01 + (searcher_skill * 0.05)  # Slightly more likely as skill increases
            }
            
            # Adjust weights based on magical strength of location
            if magical_props:
                rarity_weights[MaterialRarity.RARE] += magical_strength * 0.2
                rarity_weights[MaterialRarity.VERY_RARE] += magical_strength * 0.15
                rarity_weights[MaterialRarity.LEGENDARY] += magical_strength * 0.1
            
            # Normalize rarity weights
            total_weight = sum(rarity_weights.values())
            for rarity in rarity_weights:
                rarity_weights[rarity] /= total_weight
            
            # Select material based on rarity
            rarity_roll = random.random()
            cumulative_weight = 0
            selected_rarity = MaterialRarity.COMMON  # Default
            
            for rarity, weight in rarity_weights.items():
                cumulative_weight += weight
                if rarity_roll <= cumulative_weight:
                    selected_rarity = rarity
                    break
            
            # Filter materials by selected rarity
            rarity_materials = [m for m in matching_materials if m.rarity == selected_rarity]
            
            if not rarity_materials:
                # If no materials of this rarity, get all materials of this type
                potential_materials = matching_materials
            else:
                potential_materials = rarity_materials
            
            # If searcher has elemental affinities, prioritize matching materials
            if magic_affinity:
                # Score materials based on elemental match
                scored_materials = []
                for material in potential_materials:
                    score = 0
                    # Check primary element
                    if material.primary_element in magic_affinity:
                        score += magic_affinity[material.primary_element] * 2
                    
                    # Check secondary elements
                    for element in material.secondary_elements:
                        if element in magic_affinity:
                            score += magic_affinity[element]
                    
                    scored_materials.append((material, score))
                
                # Sort by score (higher first)
                scored_materials.sort(key=lambda x: x[1], reverse=True)
                
                # Take top 3 or all if fewer
                top_materials = [m for m, _ in scored_materials[:3]]
                
                if top_materials:
                    # Randomly select from top materials
                    selected_material = random.choice(top_materials)
                else:
                    # Fallback to random selection
                    selected_material = random.choice(potential_materials)
            else:
                # Random selection without elemental affinity
                selected_material = random.choice(potential_materials)
            
            selected_materials.append(selected_material)
            
            # Remove this material type from consideration to ensure variety
            material_type_weights = [(t, w) for t, w in material_type_weights if t != material_type]
        
        # Create instances for selected materials
        for material in selected_materials:
            # Determine quantity based on search effort and rarity
            base_quantity = 1.0  # Base unit
            
            # Adjust for rarity
            rarity_multiplier = {
                MaterialRarity.COMMON: 3.0,
                MaterialRarity.UNCOMMON: 2.0,
                MaterialRarity.RARE: 1.0,
                MaterialRarity.VERY_RARE: 0.5,
                MaterialRarity.LEGENDARY: 0.2
            }.get(material.rarity, 1.0)
            
            # Adjust for search effort
            quantity = base_quantity * rarity_multiplier * (0.5 + search_effort)
            
            # Add some randomness
            quantity *= random.uniform(0.8, 1.2)
            
            # Round to reasonable precision
            quantity = round(quantity, 1)
            
            # Determine quality based on searcher skill and magical properties
            base_quality = 0.3 + (searcher_skill * 0.4)  # 0.3 to 0.7 based on skill
            
            # Magical locations improve quality
            if magical_props:
                # General magical strength
                base_quality += magical_strength * 0.1
                
                # Element-specific boost
                for element in [material.primary_element] + material.secondary_elements:
                    if element in magical_props["affinities"]:
                        base_quality += magical_props["affinities"][element] * 0.05
            
            # Add some randomness
            quality = base_quality * random.uniform(0.9, 1.1)
            
            # Cap between 0.1 and 1.0
            quality = max(0.1, min(1.0, quality))
            
            # Determine special traits based on location and material
            special_traits = []
            
            # Location magical properties can add special traits
            if magical_props and random.random() < 0.3:
                if magical_props["stability"] == "unstable" and random.random() < 0.7:
                    special_traits.append("Unstable")
                elif magical_props["stability"] == "chaotic" and random.random() < 0.8:
                    special_traits.append("Chaotic")
                elif magical_props["stability"] == "very_stable" and random.random() < 0.6:
                    special_traits.append("Stabilized")
                
                # Add traits based on strong affinities
                for element, value in magical_props["affinities"].items():
                    if value > 0.7 and random.random() < 0.4:
                        special_traits.append(f"{element.capitalize()}-Infused")
            
            # Create and add the instance
            instance = self.create_material_instance(
                material_id=material.id,
                quantity=quantity,
                quality=quality,
                location_found=location_id,
                special_traits=special_traits
            )
            
            if instance:
                found_materials.append(instance)
        
        return found_materials
    
    def get_crafting_compatibility(
        self,
        material1_id: str,
        material2_id: str
    ) -> Tuple[float, str]:
        """
        Determine how compatible two materials are for crafting together.
        
        Args:
            material1_id: ID of the first material
            material2_id: ID of the second material
            
        Returns:
            Tuple of (compatibility_score, description) where score is 0.0 to 1.0
        """
        # Get the materials
        material1 = self.get_material(material1_id)
        material2 = self.get_material(material2_id)
        
        if not material1 or not material2:
            return 0.0, "One or both materials not found"
        
        # Base compatibility starts neutral
        compatibility = 0.5
        compatibility_notes = []
        
        # Check material types
        if material1.material_type == material2.material_type:
            # Same type is usually compatible
            compatibility += 0.1
            compatibility_notes.append(f"Both are {material1.material_type.value} type")
        elif (material1.material_type == MaterialType.METAL and material2.material_type == MaterialType.METAL) or \
             (material1.material_type == MaterialType.CRYSTAL and material2.material_type == MaterialType.CRYSTAL):
            # Metals combine well with metals, crystals with crystals
            compatibility += 0.2
            compatibility_notes.append("Naturally complementary material types")
        elif (material1.material_type == MaterialType.METAL and material2.material_type == MaterialType.CRYSTAL) or \
             (material1.material_type == MaterialType.CRYSTAL and material2.material_type == MaterialType.METAL):
            # Metals and crystals often combine well
            compatibility += 0.15
            compatibility_notes.append("Metal and crystal have good synergy")
        elif (material1.material_type == MaterialType.HERB and material2.material_type == MaterialType.FLUID) or \
             (material1.material_type == MaterialType.FLUID and material2.material_type == MaterialType.HERB):
            # Herbs and fluids combine well for potions
            compatibility += 0.15
            compatibility_notes.append("Herbs and fluids combine well")
        
        # Check elemental compatibility
        # Same primary element is very compatible
        if material1.primary_element == material2.primary_element:
            compatibility += 0.2
            compatibility_notes.append(f"Same primary element ({material1.primary_element})")
        
        # Opposing elements reduce compatibility
        opposing_elements = {
            "fire": "water",
            "water": "fire",
            "earth": "air",
            "air": "earth",
            "light": "shadow",
            "shadow": "light",
            "life": "death",
            "death": "life"
        }
        
        if material1.primary_element in opposing_elements and \
           opposing_elements[material1.primary_element] == material2.primary_element:
            compatibility -= 0.3
            compatibility_notes.append(f"Opposing primary elements ({material1.primary_element} vs {material2.primary_element})")
        
        # Secondary element overlap increases compatibility
        common_secondary = set(material1.secondary_elements) & set(material2.secondary_elements)
        if common_secondary:
            bonus = min(len(common_secondary) * 0.1, 0.3)
            compatibility += bonus
            compatibility_notes.append(f"Shared secondary elements: {', '.join(common_secondary)}")
        
        # Different states can reduce compatibility
        if material1.state != material2.state:
            # Some state combinations work better than others
            if (material1.state == MaterialState.LIQUID and material2.state == MaterialState.SOLID) or \
               (material1.state == MaterialState.SOLID and material2.state == MaterialState.LIQUID):
                compatibility -= 0.05
                compatibility_notes.append("Different states but manageable")
            elif (material1.state == MaterialState.ETHEREAL or material2.state == MaterialState.ETHEREAL):
                # Ethereal is hard to combine with anything
                compatibility -= 0.15
                compatibility_notes.append("Ethereal state is difficult to work with")
            else:
                compatibility -= 0.1
                compatibility_notes.append("Different states require special techniques")
        
        # Cap compatibility between 0.0 and 1.0
        compatibility = max(0.0, min(1.0, compatibility))
        
        # Generate description based on compatibility score
        if compatibility >= 0.8:
            description = "Exceptional compatibility. These materials harmonize perfectly."
        elif compatibility >= 0.6:
            description = "Good compatibility. These materials work well together."
        elif compatibility >= 0.4:
            description = "Moderate compatibility. These materials can be combined with proper technique."
        elif compatibility >= 0.2:
            description = "Poor compatibility. Combining these materials will be challenging."
        else:
            description = "Very poor compatibility. These materials naturally resist combination."
        
        # Add compatibility notes
        if compatibility_notes:
            description += f" Notes: {'; '.join(compatibility_notes)}."
        
        return compatibility, description
    
    def generate_enchantment_options(
        self,
        material_instance_ids: List[str],
        enchantment_purpose: str
    ) -> List[Dict[str, Any]]:
        """
        Generate possible enchantment options based on materials.
        
        Args:
            material_instance_ids: List of material instance IDs to use
            enchantment_purpose: General purpose of the enchantment
            
        Returns:
            List of possible enchantment options with properties and requirements
        """
        # Get the material instances
        material_instances = [
            self.material_instances.get(instance_id) 
            for instance_id in material_instance_ids
            if instance_id in self.material_instances
        ]
        
        if not material_instances:
            return []
        
        # Collect all materials involved
        materials = [instance.material for instance in material_instances]
        
        # Collect elemental affinities
        elemental_affinities = {}
        
        for material in materials:
            # Primary element has stronger influence
            if material.primary_element in elemental_affinities:
                elemental_affinities[material.primary_element] += 1.0
            else:
                elemental_affinities[material.primary_element] = 1.0
            
            # Secondary elements
            for element in material.secondary_elements:
                if element in elemental_affinities:
                    elemental_affinities[element] += 0.5
                else:
                    elemental_affinities[element] = 0.5
        
        # Sort elements by strength of affinity
        sorted_elements = sorted(elemental_affinities.items(), key=lambda x: x[1], reverse=True)
        
        # Define possible enchantment effects based on elements and purpose
        possible_effects = []
        
        # Map purposes to effect types
        purpose_effect_map = {
            "weapon": ["damage", "accuracy", "critical", "elemental_damage", "speed"],
            "armor": ["protection", "resistance", "durability", "regeneration", "mobility"],
            "jewelry": ["attribute_boost", "skill_boost", "magical_capacity", "resistance", "special_ability"],
            "tool": ["efficiency", "durability", "quality", "special_function", "magical_sensing"]
        }
        
        # Map elements to specific effects
        element_effect_map = {
            "fire": {
                "weapon": "deals additional fire damage",
                "armor": "provides resistance to fire",
                "jewelry": "enhances fire magic",
                "tool": "heats materials during use"
            },
            "water": {
                "weapon": "deals additional cold damage",
                "armor": "provides resistance to water and cold",
                "jewelry": "enhances water magic",
                "tool": "never rusts or corrodes"
            },
            "earth": {
                "weapon": "has increased durability",
                "armor": "provides additional physical protection",
                "jewelry": "enhances earth magic",
                "tool": "works effectively on stone and metal"
            },
            "air": {
                "weapon": "strikes with increased speed",
                "armor": "reduces weight and increases mobility",
                "jewelry": "enhances air magic",
                "tool": "reduces weight of materials being worked"
            },
            "light": {
                "weapon": "illuminates when drawn",
                "armor": "glows in darkness",
                "jewelry": "enhances light magic",
                "tool": "illuminates work area"
            },
            "shadow": {
                "weapon": "deals additional shadow damage",
                "armor": "helps conceal the wearer",
                "jewelry": "enhances shadow magic",
                "tool": "works effectively in darkness"
            },
            "life": {
                "weapon": "heals wielder when it strikes",
                "armor": "slowly regenerates the wearer",
                "jewelry": "enhances life magic",
                "tool": "helps materials grow or repair"
            },
            "death": {
                "weapon": "drains life from targets",
                "armor": "intimidates nearby creatures",
                "jewelry": "enhances death magic",
                "tool": "preserves organic materials"
            },
            "mind": {
                "weapon": "confuses targets when it strikes",
                "armor": "protects against mental influence",
                "jewelry": "enhances mental focus",
                "tool": "helps user maintain concentration"
            },
            "void": {
                "weapon": "occasionally negates magical protections",
                "armor": "absorbs some incoming spell energy",
                "jewelry": "enhances void magic",
                "tool": "creates pocket dimensional space"
            },
            "time": {
                "weapon": "occasionally allows extra attacks",
                "armor": "occasionally lets wearer dodge attacks",
                "jewelry": "enhances temporal magic",
                "tool": "works faster than normal"
            },
            "space": {
                "weapon": "has extended reach",
                "armor": "reduces impact of attacks",
                "jewelry": "enhances spatial magic",
                "tool": "can affect materials at a distance"
            }
        }
        
        # Generate effect options based on elemental affinities
        if enchantment_purpose in purpose_effect_map:
            effect_types = purpose_effect_map[enchantment_purpose]
            
            # For each top element, generate a specific effect
            for element, strength in sorted_elements[:3]:  # Use top 3 elements
                if element in element_effect_map and enchantment_purpose in element_effect_map[element]:
                    effect = element_effect_map[element][enchantment_purpose]
                    
                    # Power based on elemental strength and material quality
                    avg_quality = sum(instance.quality for instance in material_instances) / len(material_instances)
                    power = strength * 0.3 + avg_quality * 0.7  # Quality matters more
                    
                    possible_effects.append({
                        "effect": effect,
                        "element": element,
                        "power": round(power * 10) / 10,  # Round to 1 decimal
                        "stability": round(avg_quality * 10) / 10  # Stability based on quality
                    })
        
        # Generate general enchantment options
        enchantment_options = []
        
        if possible_effects:
            # Create options based on possible effects
            for i, effect in enumerate(possible_effects):
                option = {
                    "name": f"{effect['element'].capitalize()} {enchantment_purpose.capitalize()} Enchantment",
                    "description": f"An enchantment that {effect['effect']}.",
                    "effects": [effect],
                    "materials_required": material_instance_ids,
                    "difficulty": 3 + int((1 - effect['stability']) * 7),  # 3-10 scale
                    "time_required": 30 + int((1 - effect['stability']) * 90),  # 30-120 minutes
                    "success_chance": effect['stability'] * 100  # percentage
                }
                enchantment_options.append(option)
            
            # If we have multiple effects, create a combined option
            if len(possible_effects) >= 2:
                combined_effects = possible_effects[:2]  # Take top 2
                avg_power = sum(effect['power'] for effect in combined_effects) / len(combined_effects)
                avg_stability = sum(effect['stability'] for effect in combined_effects) / len(combined_effects)
                
                # Combined enchantments are more complex
                combined_option = {
                    "name": f"Dual-aspect {enchantment_purpose.capitalize()} Enchantment",
                    "description": f"A complex enchantment that combines multiple elemental aspects.",
                    "effects": combined_effects,
                    "materials_required": material_instance_ids,
                    "difficulty": 5 + int((1 - avg_stability) * 5),  # 5-10 scale
                    "time_required": 60 + int((1 - avg_stability) * 120),  # 60-180 minutes
                    "success_chance": avg_stability * 80  # Lower chance for complex enchantment
                }
                enchantment_options.append(combined_option)
        
        return enchantment_options