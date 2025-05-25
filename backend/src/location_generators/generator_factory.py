"""
Generator Factory - Central factory for creating appropriate location generators

This module provides a factory for selecting and instantiating the correct
location generator based on POI type, ensuring consistent and appropriate
content generation across different location types.
"""

import logging
from typing import Dict, Type, Optional
from abc import ABC

from .base_generator import BaseLocationGenerator
from .village_generator import VillageGenerator
from world_model import POIType

logger = logging.getLogger(__name__)


class RuinGenerator(BaseLocationGenerator):
    """Generator for ruins and ancient sites."""

    def generate_location_details(self, db, poi, generation_context=None):
        biome_context = self.get_biome_context(db, poi)
        racial_influence = self.determine_racial_influence(biome_context, poi)

        # Generate ruin-specific content
        description = self._generate_ruin_description(poi, biome_context,
                                                      racial_influence)
        detailed_features = self._generate_ruin_features(
            biome_context, racial_influence)
        quest_hooks = self._generate_ruin_quest_hooks(poi, biome_context)
        hidden_secrets = self._generate_ruin_secrets(biome_context,
                                                     racial_influence)

        details_data = {
            "description":
            description,
            "detailed_features":
            detailed_features,
            "generated_npcs":
            [],  # Ruins typically have no permanent residents
            "local_issues": ["structural_instability", "dangerous_wildlife"],
            "available_services": [],
            "unique_items":
            self.generate_resource_opportunities(biome_context, POIType.RUIN),
            "quest_hooks":
            quest_hooks,
            "hidden_secrets":
            hidden_secrets,
            "local_economy": {},
            "generation_prompt":
            self.get_generation_prompt(poi, biome_context, racial_influence)
        }

        return self.save_generated_details(db, poi, details_data)

    def _generate_ruin_description(self, poi, biome_context, racial_influence):
        dominant_race, influence_strength = racial_influence
        base_desc = self.generate_base_description(poi, biome_context,
                                                   racial_influence)

        age_descriptors = [
            "ancient", "crumbling", "weathered", "forgotten", "moss-covered"
        ]
        age_desc = f"These {poi.generated_name.split()[-1].lower()} are {', '.join(age_descriptors[:2])}"

        if influence_strength > 0.6:
            race_history = f", showing clear signs of {dominant_race} architecture from a bygone era"
        else:
            race_history = ", though their original builders remain a mystery"

        return f"{base_desc} {age_desc}{race_history}."

    def _generate_ruin_features(self, biome_context, racial_influence):
        features = [
            "Partially collapsed walls and structures",
            "Overgrown vegetation reclaiming the site"
        ]

        dominant_race, influence_strength = racial_influence
        if influence_strength > 0.6:
            race_arch = self.racial_architecture.get(dominant_race, {})
            if race_arch:
                material = f"remnants of {dominant_race} {race_arch.get('materials', ['stone'])[0]} construction"
                features.append(f"Distinctive {material}")

        # Add magical features if leyline intensity is high
        leyline_intensity = biome_context.get("leyline_intensity", 1.0)
        if leyline_intensity > 1.5:
            features.append(
                "Faint magical auras emanating from certain stones")

        return features

    def _generate_ruin_quest_hooks(self, poi, biome_context):
        hooks = [
            "Ancient inscriptions might reveal historical secrets",
            "Hidden chambers could contain valuable artifacts",
            "The ruins may be connected to larger archaeological sites"
        ]

        # Add biome-specific hooks
        if biome_context.get("biome_type") == "crimson_scars":
            hooks.append(
                "War relics from the Crimson Dissonance may be buried here")

        return hooks

    def _generate_ruin_secrets(self, biome_context, racial_influence):
        secrets = ["A hidden chamber contains preserved artifacts"]

        dominant_race, influence_strength = racial_influence
        if influence_strength > 0.7:
            secrets.append(
                f"The ruins hold clues to {dominant_race} history during the Crimson Dissonance"
            )

        return secrets


class CaveGenerator(BaseLocationGenerator):
    """Generator for caves and underground locations."""

    def generate_location_details(self, db, poi, generation_context=None):
        biome_context = self.get_biome_context(db, poi)
        racial_influence = self.determine_racial_influence(biome_context, poi)

        description = self._generate_cave_description(poi, biome_context)
        detailed_features = self._generate_cave_features(biome_context)
        quest_hooks = self._generate_cave_quest_hooks(poi, biome_context)

        details_data = {
            "description":
            description,
            "detailed_features":
            detailed_features,
            "generated_npcs":
            self._generate_cave_inhabitants(biome_context),
            "local_issues": ["unstable_passages", "underground_predators"],
            "available_services": [],
            "unique_items":
            self._generate_cave_resources(biome_context),
            "quest_hooks":
            quest_hooks,
            "hidden_secrets": ["Deep passages lead to unknown destinations"],
            "local_economy": {},
            "generation_prompt":
            self.get_generation_prompt(poi, biome_context, racial_influence)
        }

        return self.save_generated_details(db, poi, details_data)

    def _generate_cave_description(self, poi, biome_context):
        entrance_types = [
            "narrow opening", "yawning mouth", "concealed entrance",
            "natural archway"
        ]
        entrance = f"The {poi.generated_name} opens through a {entrance_types[hash(poi.id) % len(entrance_types)]}"

        depth_desc = [
            "extends deep into the earth", "winds through natural passages",
            "descends into darkness"
        ]
        depth = depth_desc[hash(poi.generated_name) % len(depth_desc)]

        return f"{entrance} that {depth}. The air carries hints of minerals and deep earth."

    def _generate_cave_features(self, biome_context):
        features = [
            "Natural rock formations and stalactites",
            "Underground water sources"
        ]

        # Add biome-specific features
        if "crystal" in biome_context.get("biome_type", "").lower():
            features.append("Glittering crystal formations line the walls")

        return features

    def _generate_cave_inhabitants(self, biome_context):
        # Simple cave dwellers - could be expanded
        return [{
            "id": "cave_hermit_001",
            "name": "Old Tom",
            "race": "human",
            "role": "Hermit",
            "description": "A weathered hermit who knows the cave's secrets",
            "services": ["local_knowledge", "safe_passage"]
        }]

    def _generate_cave_resources(self, biome_context):
        resources = [{
            "name": "Cave Water",
            "type": "water",
            "description": "Fresh underground spring water"
        }, {
            "name": "Stone Minerals",
            "type": "materials",
            "description": "Common cave minerals"
        }]

        # Add special resources based on biome
        if biome_context.get("leyline_intensity", 1.0) > 1.5:
            resources.append({
                "name":
                "Leyline Crystals",
                "type":
                "magical_materials",
                "description":
                "Crystals charged with leyline energy"
            })

        return resources

    def _generate_cave_quest_hooks(self, poi, biome_context):
        return [
            "Deeper passages might connect to other cave systems",
            "Strange noises echo from the depths",
            "Ancient cave paintings hint at forgotten history"
        ]


class LocationGeneratorFactory:
    """
    Factory for creating appropriate location generators based on POI type.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Register generators for different POI types
        self._generators: Dict[POIType, Type[BaseLocationGenerator]] = {
            POIType.VILLAGE: VillageGenerator,
            POIType.SETTLEMENT:
            VillageGenerator,  # Use village generator for settlements
            POIType.RUIN: RuinGenerator,
            POIType.CAVE: CaveGenerator,
            POIType.SHRINE:
            RuinGenerator,  # Shrines can use ruin generator with modifications
            POIType.TOWER: RuinGenerator,  # Towers can use ruin generator
            POIType.MINE: CaveGenerator,  # Mines are similar to caves
            POIType.CAMP: VillageGenerator,  # Camps are like small villages
        }

        # Cache instantiated generators for reuse
        self._generator_instances: Dict[Type[BaseLocationGenerator],
                                        BaseLocationGenerator] = {}

    def get_generator(self,
                      poi_type: POIType) -> Optional[BaseLocationGenerator]:
        """
        Get the appropriate generator for a POI type.

        Args:
            poi_type: The type of POI to generate content for

        Returns:
            Appropriate generator instance or None if no generator available
        """
        try:
            if poi_type not in self._generators:
                self.logger.warning(
                    f"No generator available for POI type: {poi_type}")
                return None

            generator_class = self._generators[poi_type]

            # Return cached instance if available
            if generator_class in self._generator_instances:
                return self._generator_instances[generator_class]

            # Create new instance and cache it
            generator_instance = generator_class()
            self._generator_instances[generator_class] = generator_instance

            self.logger.debug(f"Created generator for POI type: {poi_type}")
            return generator_instance

        except Exception as e:
            self.logger.error(
                f"Error creating generator for POI type {poi_type}: {e}")
            return None

    def register_generator(self, poi_type: POIType,
                           generator_class: Type[BaseLocationGenerator]):
        """
        Register a new generator class for a POI type.

        Args:
            poi_type: POI type to register generator for
            generator_class: Generator class to use for this POI type
        """
        self._generators[poi_type] = generator_class
        self.logger.info(
            f"Registered generator {generator_class.__name__} for POI type {poi_type}"
        )

    def get_available_poi_types(self) -> List[POIType]:
        """Get list of POI types that have generators available."""
        return list(self._generators.keys())

    def generate_location_details(self,
                                  db,
                                  poi,
                                  generation_context: Optional[Dict] = None):
        """
        Generate location details using the appropriate generator.

        Args:
            db: Database session
            poi: POI object to generate details for
            generation_context: Optional context for generation

        Returns:
            Generated location details or None if generation fails
        """
        try:
            poi_type = POIType(poi.poi_type)
            generator = self.get_generator(poi_type)

            if not generator:
                self.logger.error(
                    f"No generator available for POI type: {poi_type}")
                return None

            self.logger.info(
                f"Generating details for {poi.generated_name} ({poi_type})")
            details = generator.generate_location_details(
                db, poi, generation_context)

            if details:
                self.logger.info(
                    f"Successfully generated details for {poi.generated_name}")
            else:
                self.logger.warning(
                    f"Generator returned None for {poi.generated_name}")

            return details

        except Exception as e:
            self.logger.error(
                f"Error generating location details for {poi.generated_name}: {e}"
            )
            import traceback
            traceback.print_exc()
            return None


# Global factory instance
location_generator_factory = LocationGeneratorFactory()


def get_location_generator_factory() -> LocationGeneratorFactory:
    """Get the global location generator factory instance."""
    return location_generator_factory
