
"""
World Generation Service - Main service for procedural world generation

This service coordinates all aspects of world generation including regions,
biomes, POI placement, and location detail generation.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from world_model import (
    DBRegion, DBBiome, DBPointOfInterest, POIType, POIState,
    BiomeType, LocationSize
)
from poi_placement_service import POIPlacementService
from world_persistence_manager import WorldPersistenceManager
from location_generators.generator_factory import get_location_generator_factory

logger = logging.getLogger(__name__)

class WorldGenerationService:
    """
    Main service for coordinating all world generation activities.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.poi_service = POIPlacementService()
        self.persistence_manager = WorldPersistenceManager()
        self.generator_factory = get_location_generator_factory()

        # Generation configuration
        self.config = {
            "max_pois_per_biome": 50,
            "detail_generation_batch_size": 10,
            "discovery_simulation_enabled": True,
            "auto_generate_details": True
        }

    def generate_complete_region(
        self,
        db: Session,
        region_data: Dict[str, Any],
        generate_details: bool = True,
        simulation_context: Optional[Dict[str, Any]] = None
    ) -> DBRegion:
        """
        Generate a complete region with biomes, POIs, and location details.

        Args:
            db: Database session
            region_data: Region configuration data
            generate_details: Whether to generate detailed location content
            simulation_context: Context for simulating player discovery

        Returns:
            Created region with all generated content
        """
        self.logger.info(f"Generating complete region: {region_data['name']}")

        try:
            # Step 1: Create the region
            region = self._create_region(db, region_data)

            # Step 2: Create biomes for the region
            biomes_data = self._generate_biomes_for_region(region_data, region.id)
            created_biomes = []

            for biome_data in biomes_data:
                biome = self._create_biome(db, biome_data)
                created_biomes.append(biome)

                # Step 3: Generate POIs for each biome
                area_size = self._calculate_biome_area(biome)
                self.poi_service.generate_pois_for_biome(
                    db, 
                    biome.id, 
                    area_size_km2=area_size,
                    player_context=simulation_context
                )

            db.commit()

            # Step 4: Generate location details if requested
            if generate_details:
                self._generate_location_details_for_region(db, region.id)

            # Step 5: Simulate some discovery if context provided
            if simulation_context and self.config["discovery_simulation_enabled"]:
                self._simulate_player_discovery(db, region.id, simulation_context)

            self.logger.info(f"Successfully generated region {region.name}")
            return region

        except Exception as e:
            self.logger.error(f"Error generating region {region_data['name']}: {e}")
            db.rollback()
            raise

    def _create_region(self, db: Session, region_data: Dict[str, Any]) -> DBRegion:
        """Create a region from data."""
        region = DBRegion(
            name=region_data["name"],
            description=region_data["description"],
            core_lore=region_data.get("core_lore", ""),
            dominant_races=region_data.get("dominant_races", []),
            political_influence=region_data.get("political_influence", {}),
            trade_routes=region_data.get("trade_routes", []),
            resource_abundance=region_data.get("resource_abundance", {}),
            leyline_strength=region_data.get("leyline_strength", 1.0),
            crimson_corruption=region_data.get("crimson_corruption", 0.0)
        )

        db.add(region)
        db.flush()
        return region

    def _create_biome(self, db: Session, biome_data: Dict[str, Any]) -> DBBiome:
        """Create a biome from data."""
        biome = DBBiome(
            region_id=biome_data["region_id"],
            name=biome_data["name"],
            biome_type=biome_data["biome_type"],
            description=biome_data["description"],
            poi_density=biome_data.get("poi_density", 0.5),
            allowed_poi_types=biome_data.get("allowed_poi_types", []),
            generation_keywords=biome_data.get("generation_keywords", []),
            flora_fauna=biome_data.get("flora_fauna", []),
            atmospheric_tags=biome_data.get("atmospheric_tags", []),
            hazards=biome_data.get("hazards", []),
            available_resources=biome_data.get("available_resources", {}),
            leyline_intensity=biome_data.get("leyline_intensity", 1.0),
            magical_phenomena=biome_data.get("magical_phenomena", [])
        )

        db.add(biome)
        db.flush()
        return biome

    def _generate_biomes_for_region(self, region_data: Dict[str, Any], region_id: str) -> List[Dict[str, Any]]:
        """Generate biome data for a region based on its characteristics."""
        # This is a simplified version - in the full implementation,
        # you'd have more sophisticated biome generation logic

        base_biome = {
            "region_id": region_id,
            "poi_density": 0.5,
            "leyline_intensity": region_data.get("leyline_strength", 1.0),
            "allowed_poi_types": [POIType.VILLAGE.value, POIType.RUIN.value, POIType.CAVE.value],
            "generation_keywords": ["generic", "rural"],
            "atmospheric_tags": ["peaceful"],
            "hazards": [],
            "available_resources": region_data.get("resource_abundance", {}),
            "magical_phenomena": []
        }

        # Generate 2-4 biomes per region
        biome_count = random.randint(2, 4)
        biomes = []

        for i in range(biome_count):
            biome = base_biome.copy()
            biome["name"] = f"{region_data['name']} - Area {i + 1}"
            biome["biome_type"] = random.choice([
                BiomeType.VERDANT_FRONTIER.value,
                BiomeType.WHISPERING_WOODS.value,
                BiomeType.CRYSTAL_HIGHLANDS.value
            ])
            biome["description"] = f"A {biome['biome_type'].replace('_', ' ').lower()} area within {region_data['name']}"

            # Vary POI density
            biome["poi_density"] = random.uniform(0.3, 0.8)

            biomes.append(biome)

        return biomes

    def _calculate_biome_area(self, biome: DBBiome) -> float:
        """Calculate appropriate area for a biome."""
        base_areas = {
            BiomeType.VERDANT_FRONTIER.value: 150.0,
            BiomeType.EMBER_WASTES.value: 100.0,
            BiomeType.WHISPERING_WOODS.value: 120.0,
            BiomeType.CRYSTAL_HIGHLANDS.value: 80.0,
            BiomeType.SHIMMERING_MARSHES.value: 110.0,
            BiomeType.CRIMSON_SCARS.value: 60.0,
            BiomeType.RELIC_ZONES.value: 70.0
        }

        base_area = base_areas.get(biome.biome_type, 100.0)

        # Apply density modifier
        density_modifier = biome.poi_density or 0.5
        return base_area * (0.5 + density_modifier)

    def _generate_location_details_for_region(self, db: Session, region_id: str):
        """Generate location details for POIs in a region."""
        # Get all POIs in the region
        pois = db.query(DBPointOfInterest).join(DBBiome).filter(
            DBBiome.region_id == region_id
        ).all()

        generated_count = 0
        batch_size = self.config["detail_generation_batch_size"]

        # Process in batches to avoid overwhelming the system
        for i in range(0, len(pois), batch_size):
            batch = pois[i:i + batch_size]

            for poi in batch:
                try:
                    # Skip if details already generated
                    if poi.details_generated:
                        continue

                    # Generate details using the factory
                    details = self.generator_factory.generate_location_details(db, poi)

                    if details:
                        generated_count += 1
                        self.logger.debug(f"Generated details for {poi.generated_name}")

                except Exception as e:
                    self.logger.error(f"Error generating details for {poi.generated_name}: {e}")

            # Commit batch
            db.commit()

        self.logger.info(f"Generated details for {generated_count} locations in region")

    def _simulate_player_discovery(
        self, 
        db: Session, 
        region_id: str, 
        simulation_context: Dict[str, Any]
    ):
        """Simulate player discovery of POIs for testing purposes."""
        # Get undiscovered POIs
        undiscovered_pois = db.query(DBPointOfInterest).join(DBBiome).filter(
            DBBiome.region_id == region_id,
            DBPointOfInterest.current_state == POIState.UNDISCOVERED.value
        ).all()

        # Simulate discovery based on player awareness
        player_awareness = simulation_context.get("awareness", 10)
        discovery_count = 0

        for poi in undiscovered_pois:
            # Simple discovery simulation
            discovery_chance = max(0, player_awareness - poi.discovery_difficulty + 10) / 30.0

            if random.random() < discovery_chance:
                poi.current_state = POIState.DISCOVERED.value
                poi.discovered_at = datetime.utcnow()
                discovery_count += 1

                # Some discovered POIs get explored
                if random.random() < 0.3:
                    poi.current_state = POIState.EXPLORED.value
                    poi.last_visited = datetime.utcnow()

        db.commit()
        self.logger.info(f"Simulated discovery of {discovery_count} POIs")

    def discover_poi(
        self, 
        db: Session, 
        poi_id: str, 
        player_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark a POI as discovered and potentially generate its details.

        Args:
            db: Database session
            poi_id: ID of the POI to discover
            player_context: Player information for contextual generation

        Returns:
            True if discovery was successful
        """
        try:
            success = self.poi_service.update_poi_discovery_state(
                db, poi_id, POIState.DISCOVERED, player_context
            )

            if success and self.config["auto_generate_details"]:
                # Get the POI and generate details if not already done
                poi = db.query(DBPointOfInterest).filter(
                    DBPointOfInterest.id == poi_id
                ).first()

                if poi and not poi.details_generated:
                    details = self.generator_factory.generate_location_details(
                        db, poi, player_context
                    )

                    if details:
                        self.logger.info(f"Auto-generated details for discovered POI: {poi.generated_name}")

            return success

        except Exception as e:
            self.logger.error(f"Error discovering POI {poi_id}: {e}")
            return False

    def get_discoverable_locations(
        self,
        db: Session,
        biome_id: str,
        player_awareness: int = 10,
        search_radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Get locations that a player could potentially discover.

        Returns list of POI data with discovery information.
        """
        discoverable_pois = self.poi_service.get_discoverable_pois_near_location(
            db, biome_id, player_awareness, search_radius_km
        )

        result = []
        for poi in discoverable_pois:
            poi_data = {
                "id": poi.id,
                "name": poi.generated_name,
                "type": poi.poi_type,
                "discovery_difficulty": poi.discovery_difficulty,
                "location_tags": poi.relative_location_tags,
                "travel_time": poi.travel_time_from_major,
                "has_details": poi.details_generated
            }
            result.append(poi_data)

        return result

    def generate_world_report(self, db: Session) -> Dict[str, Any]:
        """
        Generate a comprehensive report about the current world state.
        """
        stats = self.persistence_manager.get_world_statistics(db)

        # Get additional detailed information
        regions = db.query(DBRegion).all()
        region_details = []

        for region in regions:
            biomes = db.query(DBBiome).filter(DBBiome.region_id == region.id).all()
            biome_summary = []

            for biome in biomes:
                poi_count = db.query(DBPointOfInterest).filter(
                    DBPointOfInterest.biome_id == biome.id
                ).count()

                biome_summary.append({
                    "name": biome.name,
                    "type": biome.biome_type,
                    "poi_count": poi_count,
                    "poi_density": biome.poi_density
                })

            region_details.append({
                "name": region.name,
                "dominant_races": region.dominant_races,
                "leyline_strength": region.leyline_strength,
                "corruption_level": region.crimson_corruption,
                "biome_count": len(biomes),
                "biomes": biome_summary
            })

        return {
            "statistics": stats,
            "regions": region_details,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "configuration": self.config
        }

    def cleanup_old_data(self, db: Session, days_threshold: int = 30) -> Dict[str, int]:
        """Clean up old, unused world data."""
        return self.persistence_manager.cleanup_old_world_data(db, days_threshold)

    def export_world_data(
        self, 
        db: Session, 
        region_ids: Optional[List[str]] = None,
        include_undiscovered: bool = False
    ) -> Dict[str, Any]:
        """Export world data for backup or analysis."""
        return self.persistence_manager.export_world_data(
            db, region_ids, include_undiscovered
        )


# Global service instance
_world_generation_service = None

def get_world_generation_service() -> WorldGenerationService:
    """Get the global world generation service instance."""
    global _world_generation_service
    if _world_generation_service is None:
        _world_generation_service = WorldGenerationService()
    return _world_generation_service
