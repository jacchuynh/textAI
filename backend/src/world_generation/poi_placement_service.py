
"""
POI Placement Service - Procedural generation of Points of Interest

This service handles the logic for determining where and what types of POIs
should be generated within biomes, based on biome rules, player context,
and world state.
"""

import random
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from .world_model import (
    DBBiome, DBPointOfInterest, DBRegion,
    POIType, POIState, BiomeType,
    RACIAL_CHARACTERISTICS
)

logger = logging.getLogger(__name__)

class POIPlacementService:
    """
    Service responsible for procedural placement of POIs within biomes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Distance modifiers for POI placement
        self.distance_weights = {
            "near_major_city": 1.5,      # More POIs near major cities
            "trade_route": 1.3,          # More POIs along trade routes
            "remote_wilderness": 0.7,    # Fewer POIs in deep wilderness
            "dangerous_region": 0.5      # Fewer POIs in dangerous areas
        }
        
        # POI type relationships and clustering rules
        self.poi_clustering = {
            POIType.VILLAGE: {
                "attracts": [POIType.WAYSTATION, POIType.SHRINE, POIType.FARM],
                "repels": [POIType.RUIN, POIType.DANGEROUS_CAVE],
                "cluster_distance": 2.0  # km
            },
            POIType.RUIN: {
                "attracts": [POIType.RELIC_SITE, POIType.BATTLEFIELD],
                "repels": [POIType.VILLAGE, POIType.FARM],
                "cluster_distance": 5.0
            },
            POIType.MINE: {
                "attracts": [POIType.CAMP, POIType.WAYSTATION],
                "repels": [POIType.SHRINE, POIType.GROVE],
                "cluster_distance": 3.0
            }
        }
    
    def generate_pois_for_biome(
        self,
        db: Session,
        biome_id: str,
        area_size_km2: float = 100.0,
        player_context: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None
    ) -> List[DBPointOfInterest]:
        """
        Generate POIs for a specific biome based on its generation rules.
        
        Args:
            db: Database session
            biome_id: ID of the biome to generate POIs for
            area_size_km2: Size of the area in square kilometers
            player_context: Player exploration history and preferences
            seed: Random seed for deterministic generation
            
        Returns:
            List of generated POI database objects
        """
        if seed:
            random.seed(seed)
        
        # Get biome data
        biome = db.query(DBBiome).filter(DBBiome.id == biome_id).first()
        if not biome:
            self.logger.error(f"Biome {biome_id} not found")
            return []
        
        # Get generation rules for this biome type
        generation_rules = get_biome_generation_rules(BiomeType(biome.biome_type))
        
        # Calculate number of POIs to generate
        base_poi_count = int(area_size_km2 * biome.poi_density)
        
        # Apply player context modifiers
        poi_count = self._apply_player_context_modifiers(
            base_poi_count, player_context, biome
        )
        
        self.logger.info(f"Generating {poi_count} POIs for biome {biome.name}")
        
        generated_pois = []
        
        for i in range(poi_count):
            try:
                # Select POI type based on biome rules and existing POIs
                poi_type = self._select_poi_type(
                    generation_rules["poi_types"],
                    generated_pois,
                    biome
                )
                
                # Generate POI data
                poi = self._generate_single_poi(
                    biome_id=biome_id,
                    poi_type=poi_type,
                    generation_rules=generation_rules,
                    existing_pois=generated_pois,
                    biome=biome
                )
                
                if poi:
                    generated_pois.append(poi)
                    
            except Exception as e:
                self.logger.error(f"Error generating POI {i} for biome {biome_id}: {e}")
        
        # Save POIs to database
        for poi in generated_pois:
            db.add(poi)
        
        try:
            db.commit()
            self.logger.info(f"Successfully saved {len(generated_pois)} POIs to database")
        except Exception as e:
            self.logger.error(f"Error saving POIs to database: {e}")
            db.rollback()
            return []
        
        return generated_pois
    
    def _apply_player_context_modifiers(
        self,
        base_count: int,
        player_context: Optional[Dict[str, Any]],
        biome: DBBiome
    ) -> int:
        """
        Modify POI count based on player exploration history and preferences.
        """
        if not player_context:
            return base_count
        
        modifier = 1.0
        
        # Check player exploration patterns
        exploration_history = player_context.get("exploration_history", {})
        preferred_poi_types = player_context.get("preferred_poi_types", [])
        
        # If player likes certain POI types that this biome supports, increase density
        biome_poi_types = set(biome.allowed_poi_types or [])
        player_preferred = set(preferred_poi_types)
        
        if biome_poi_types.intersection(player_preferred):
            modifier *= 1.2
        
        # If player has thoroughly explored similar biomes, reduce density
        similar_biome_exploration = exploration_history.get(biome.biome_type, 0)
        if similar_biome_exploration > 10:
            modifier *= 0.8
        elif similar_biome_exploration > 5:
            modifier *= 0.9
        
        # Apply distance from major locations
        distance_modifier = player_context.get("distance_from_major", "medium")
        if distance_modifier in self.distance_weights:
            modifier *= self.distance_weights[distance_modifier]
        
        return max(1, int(base_count * modifier))
    
    def _select_poi_type(
        self,
        allowed_types: List[POIType],
        existing_pois: List[DBPointOfInterest],
        biome: DBBiome
    ) -> POIType:
        """
        Select a POI type based on biome rules and clustering logic.
        """
        if not allowed_types:
            return POIType.VILLAGE  # Default fallback
        
        # Create weighted selection based on existing POIs
        type_weights = {}
        
        for poi_type in allowed_types:
            base_weight = 1.0
            
            # Apply clustering rules
            for existing_poi in existing_pois:
                existing_type = POIType(existing_poi.poi_type)
                
                if existing_type in self.poi_clustering:
                    clustering_rule = self.poi_clustering[existing_type]
                    
                    # If this type is attracted to existing POI, increase weight
                    if poi_type in clustering_rule.get("attracts", []):
                        base_weight *= 1.5
                    
                    # If this type is repelled by existing POI, decrease weight
                    if poi_type in clustering_rule.get("repels", []):
                        base_weight *= 0.5
            
            # Apply biome-specific modifiers
            if biome.biome_type == BiomeType.VERDANT_FRONTIER.value:
                if poi_type in [POIType.VILLAGE, POIType.FARM]:
                    base_weight *= 1.3
            elif biome.biome_type == BiomeType.EMBER_WASTES.value:
                if poi_type in [POIType.MINE, POIType.OASIS]:
                    base_weight *= 1.3
            elif biome.biome_type == BiomeType.WHISPERING_WOODS.value:
                if poi_type in [POIType.GROVE, POIType.SHRINE]:
                    base_weight *= 1.3
            
            type_weights[poi_type] = base_weight
        
        # Weighted random selection
        total_weight = sum(type_weights.values())
        if total_weight <= 0:
            return random.choice(allowed_types)
        
        rand_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for poi_type, weight in type_weights.items():
            current_weight += weight
            if rand_value <= current_weight:
                return poi_type
        
        return random.choice(allowed_types)  # Fallback
    
    def _generate_single_poi(
        self,
        biome_id: str,
        poi_type: POIType,
        generation_rules: Dict[str, Any],
        existing_pois: List[DBPointOfInterest],
        biome: DBBiome
    ) -> Optional[DBPointOfInterest]:
        """
        Generate a single POI with appropriate attributes.
        """
        try:
            # Generate name based on POI type and biome
            generated_name = self._generate_poi_name(poi_type, biome, generation_rules)
            
            # Determine discovery difficulty
            discovery_difficulty = self._calculate_discovery_difficulty(
                poi_type, biome, existing_pois
            )
            
            # Generate location tags
            location_tags = self._generate_location_tags(poi_type, biome, generation_rules)
            
            # Calculate travel time from major location
            travel_time = self._calculate_travel_time(poi_type, biome)
            
            # Create generation seed for consistent regeneration
            generation_seed = f"{biome_id}_{poi_type.value}_{len(existing_pois)}_{random.randint(1000, 9999)}"
            
            poi = DBPointOfInterest(
                biome_id=biome_id,
                poi_type=poi_type.value,
                generated_name=generated_name,
                current_state=POIState.UNDISCOVERED.value,
                discovery_difficulty=discovery_difficulty,
                relative_location_tags=location_tags,
                travel_time_from_major=travel_time,
                details_generated=False,
                generation_seed=generation_seed
            )
            
            return poi
            
        except Exception as e:
            self.logger.error(f"Error generating POI: {e}")
            return None
    
    def _generate_poi_name(
        self,
        poi_type: POIType,
        biome: DBBiome,
        generation_rules: Dict[str, Any]
    ) -> str:
        """
        Generate a thematic name for the POI based on type and biome.
        """
        # Name components based on biome and POI type
        prefixes = {
            BiomeType.VERDANT_FRONTIER: ["Green", "Golden", "Fertile", "Peaceful", "Bright"],
            BiomeType.EMBER_WASTES: ["Burning", "Red", "Scorched", "Dry", "Sun-baked"],
            BiomeType.WHISPERING_WOODS: ["Ancient", "Whispering", "Hidden", "Mystic", "Elder"],
            BiomeType.CRYSTAL_HIGHLANDS: ["Crystal", "High", "Gleaming", "Mountain", "Peak"],
            BiomeType.SHIMMERING_MARSHES: ["Misty", "Shimmer", "Bog", "Marsh", "Wetland"],
            BiomeType.FROSTBOUND_TUNDRA: ["Frozen", "Ice", "Frost", "Cold", "Winter"],
            BiomeType.CRIMSON_SCARS: ["Broken", "Scarred", "Ruined", "Cursed", "War-torn"],
            BiomeType.RELIC_ZONES: ["Lost", "Forgotten", "Ancient", "Relic", "Fallen"]
        }
        
        suffixes = {
            POIType.VILLAGE: ["village", "hamlet", "settlement", "crossing", "hollow"],
            POIType.RUIN: ["ruins", "remains", "wreckage", "rubble", "remnants"],
            POIType.CAVE: ["cave", "cavern", "grotto", "hollow", "depths"],
            POIType.SHRINE: ["shrine", "altar", "sanctum", "chapel", "memorial"],
            POIType.TOWER: ["tower", "spire", "keep", "watchtower", "beacon"],
            POIType.BRIDGE: ["bridge", "crossing", "span", "passage", "gateway"],
            POIType.MINE: ["mine", "quarry", "pit", "excavation", "dig"],
            POIType.GROVE: ["grove", "glade", "thicket", "copse", "woods"],
            POIType.SPRING: ["spring", "well", "pool", "fountain", "source"],
            POIType.BATTLEFIELD: ["battlefield", "field", "ground", "site", "memorial"]
        }
        
        # Get appropriate prefix and suffix
        biome_type = BiomeType(biome.biome_type)
        prefix_list = prefixes.get(biome_type, ["Old", "Small", "Hidden"])
        suffix_list = suffixes.get(poi_type, ["place", "site", "location"])
        
        prefix = random.choice(prefix_list)
        suffix = random.choice(suffix_list)
        
        # Sometimes add a middle descriptor
        middle_descriptors = generation_rules.get("keywords", [])
        if middle_descriptors and random.random() < 0.3:
            middle = random.choice(middle_descriptors).replace("_", " ").title()
            return f"{prefix} {middle} {suffix.title()}"
        
        return f"{prefix} {suffix.title()}"
    
    def _calculate_discovery_difficulty(
        self,
        poi_type: POIType,
        biome: DBBiome,
        existing_pois: List[DBPointOfInterest]
    ) -> int:
        """
        Calculate the difficulty of discovering this POI.
        """
        base_difficulty = {
            POIType.VILLAGE: 8,      # Easy to find
            POIType.WAYSTATION: 10,
            POIType.RUIN: 12,
            POIType.CAVE: 14,
            POIType.SHRINE: 15,
            POIType.TOWER: 10,
            POIType.BRIDGE: 8,
            POIType.MINE: 12,
            POIType.GROVE: 13,
            POIType.SPRING: 11,
            POIType.BATTLEFIELD: 10,
            POIType.RELIC_SITE: 18   # Very hard to find
        }.get(poi_type, 12)
        
        # Modify based on biome characteristics
        if biome.biome_type == BiomeType.CRIMSON_SCARS.value:
            base_difficulty += 3  # Dangerous areas are harder to explore
        elif biome.biome_type == BiomeType.WHISPERING_WOODS.value:
            base_difficulty += 2  # Magical concealment
        elif biome.biome_type == BiomeType.VERDANT_FRONTIER.value:
            base_difficulty -= 2  # Open, well-traveled areas
        
        # Existing POIs might make others easier to find
        nearby_pois = len([poi for poi in existing_pois if poi.poi_type == poi_type.value])
        if nearby_pois > 0:
            base_difficulty -= min(nearby_pois, 3)
        
        return max(5, min(25, base_difficulty))  # Clamp between 5 and 25
    
    def _generate_location_tags(
        self,
        poi_type: POIType,
        biome: DBBiome,
        generation_rules: Dict[str, Any]
    ) -> List[str]:
        """
        Generate descriptive location tags for the POI.
        """
        tags = []
        
        # Add biome-based tags
        if biome.atmospheric_tags:
            tags.extend(random.sample(biome.atmospheric_tags, min(2, len(biome.atmospheric_tags))))
        
        # Add POI-type specific tags
        type_specific_tags = {
            POIType.VILLAGE: ["inhabited", "welcoming", "trade_stop"],
            POIType.RUIN: ["abandoned", "ancient", "mysterious"],
            POIType.CAVE: ["dark", "hidden", "underground"],
            POIType.SHRINE: ["sacred", "peaceful", "spiritual"],
            POIType.MINE: ["deep", "industrial", "resource_rich"],
            POIType.GROVE: ["natural", "secluded", "peaceful"],
            POIType.BATTLEFIELD: ["haunted", "historical", "somber"]
        }
        
        if poi_type in type_specific_tags:
            tags.extend(random.sample(
                type_specific_tags[poi_type], 
                min(2, len(type_specific_tags[poi_type]))
            ))
        
        # Add geographical tags
        geographical_tags = [
            "near_river", "hilltop", "valley_floor", "forest_edge", 
            "mountain_pass", "crossroads", "isolated", "cliff_side"
        ]
        tags.append(random.choice(geographical_tags))
        
        return list(set(tags))  # Remove duplicates
    
    def _calculate_travel_time(self, poi_type: POIType, biome: DBBiome) -> int:
        """
        Calculate travel time from nearest major location in days.
        """
        base_travel_time = {
            POIType.VILLAGE: 1,      # Close to civilization
            POIType.WAYSTATION: 1,
            POIType.RUIN: 2,
            POIType.CAVE: 2,
            POIType.SHRINE: 2,
            POIType.TOWER: 1,
            POIType.BRIDGE: 1,
            POIType.MINE: 2,
            POIType.GROVE: 3,
            POIType.SPRING: 2,
            POIType.BATTLEFIELD: 2,
            POIType.RELIC_SITE: 4    # Deep in dangerous territory
        }.get(poi_type, 2)
        
        # Modify based on biome accessibility
        if biome.biome_type in [BiomeType.CRIMSON_SCARS.value, BiomeType.RELIC_ZONES.value]:
            base_travel_time += 2
        elif biome.biome_type == BiomeType.VERDANT_FRONTIER.value:
            base_travel_time = max(1, base_travel_time - 1)
        
        # Add some randomness
        modifier = random.randint(-1, 2)
        return max(1, base_travel_time + modifier)
    
    def update_poi_discovery_state(
        self,
        db: Session,
        poi_id: str,
        new_state: POIState,
        discovery_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update the discovery state of a POI when players interact with it.
        """
        try:
            poi = db.query(DBPointOfInterest).filter(DBPointOfInterest.id == poi_id).first()
            if not poi:
                self.logger.error(f"POI {poi_id} not found")
                return False
            
            old_state = poi.current_state
            poi.current_state = new_state.value
            
            # Update timestamps based on state change
            if new_state == POIState.DISCOVERED and old_state == POIState.UNDISCOVERED.value:
                poi.discovered_at = datetime.utcnow()
            
            if new_state in [POIState.EXPLORED, POIState.CLEARED]:
                poi.last_visited = datetime.utcnow()
            
            db.commit()
            
            self.logger.info(f"Updated POI {poi.generated_name} state from {old_state} to {new_state.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating POI state: {e}")
            db.rollback()
            return False
    
    def get_discoverable_pois_near_location(
        self,
        db: Session,
        biome_id: str,
        player_awareness: int = 10,
        search_radius_km: float = 10.0
    ) -> List[DBPointOfInterest]:
        """
        Get POIs that could be discovered by a player in a given area.
        """
        # Get all undiscovered POIs in the biome
        undiscovered_pois = db.query(DBPointOfInterest).filter(
            DBPointOfInterest.biome_id == biome_id,
            DBPointOfInterest.current_state == POIState.UNDISCOVERED.value
        ).all()
        
        discoverable = []
        for poi in undiscovered_pois:
            # Simple discovery check - in a real implementation, you'd factor in
            # distance, terrain, weather, player skills, etc.
            discovery_chance = max(0, player_awareness - poi.discovery_difficulty + 10) / 20.0
            
            if random.random() < discovery_chance:
                discoverable.append(poi)
        
        return discoverable
