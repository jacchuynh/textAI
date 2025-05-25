
"""
World Persistence Manager - Handles saving and loading of dynamic world state

This module manages the persistence of procedurally generated world content,
including POI states, location details, and world changes over time.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .world_model import (
    DBRegion, DBBiome, DBPredefinedLocation, DBPointOfInterest,
    DBGeneratedLocationDetails, POIState
)

logger = logging.getLogger(__name__)

class WorldPersistenceManager:
    """
    Manages saving and loading of dynamic world state and procedural content.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def save_world_state_snapshot(
        self,
        db: Session,
        game_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a snapshot of the current world state for a specific game.
        
        Args:
            db: Database session
            game_id: Unique identifier for the game session
            context: Additional context information
            
        Returns:
            Dictionary containing the world state snapshot
        """
        try:
            snapshot = {
                "game_id": game_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context or {},
                "regions": [],
                "discovered_pois": [],
                "location_states": {},
                "player_discoveries": {}
            }
            
            # Get all regions
            regions = db.query(DBRegion).all()
            for region in regions:
                region_data = {
                    "id": region.id,
                    "name": region.name,
                    "description": region.description,
                    "biomes": []
                }
                
                # Get biomes for this region
                biomes = db.query(DBBiome).filter(DBBiome.region_id == region.id).all()
                for biome in biomes:
                    biome_data = {
                        "id": biome.id,
                        "name": biome.name,
                        "biome_type": biome.biome_type,
                        "poi_count": len(biome.points_of_interest or [])
                    }
                    region_data["biomes"].append(biome_data)
                
                snapshot["regions"].append(region_data)
            
            # Get discovered POIs
            discovered_pois = db.query(DBPointOfInterest).filter(
                DBPointOfInterest.current_state != POIState.UNDISCOVERED.value
            ).all()
            
            for poi in discovered_pois:
                poi_data = {
                    "id": poi.id,
                    "name": poi.generated_name,
                    "type": poi.poi_type,
                    "state": poi.current_state,
                    "discovered_at": poi.discovered_at.isoformat() if poi.discovered_at else None,
                    "last_visited": poi.last_visited.isoformat() if poi.last_visited else None,
                    "biome_id": poi.biome_id
                }
                snapshot["discovered_pois"].append(poi_data)
            
            self.logger.info(f"Created world state snapshot for game {game_id}")
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error creating world state snapshot: {e}")
            raise
    
    def load_world_state_snapshot(
        self,
        db: Session,
        snapshot: Dict[str, Any]
    ) -> bool:
        """
        Load a world state snapshot (primarily for debugging/testing).
        
        Note: In a production system, you'd want more sophisticated
        merging logic to handle conflicts with current world state.
        """
        try:
            game_id = snapshot.get("game_id")
            if not game_id:
                self.logger.error("No game_id in snapshot")
                return False
            
            # Update POI states from snapshot
            discovered_pois = snapshot.get("discovered_pois", [])
            
            for poi_data in discovered_pois:
                poi = db.query(DBPointOfInterest).filter(
                    DBPointOfInterest.id == poi_data["id"]
                ).first()
                
                if poi:
                    poi.current_state = poi_data["state"]
                    if poi_data.get("discovered_at"):
                        poi.discovered_at = datetime.fromisoformat(poi_data["discovered_at"])
                    if poi_data.get("last_visited"):
                        poi.last_visited = datetime.fromisoformat(poi_data["last_visited"])
            
            db.commit()
            self.logger.info(f"Loaded world state snapshot for game {game_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading world state snapshot: {e}")
            db.rollback()
            return False
    
    def get_player_discovered_locations(
        self,
        db: Session,
        player_id: str,
        region_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all locations discovered by a specific player.
        """
        try:
            query = db.query(DBPointOfInterest).filter(
                DBPointOfInterest.current_state != POIState.UNDISCOVERED.value
            )
            
            if region_id:
                # Filter by region through biome relationship
                query = query.join(DBBiome).filter(DBBiome.region_id == region_id)
            
            discovered_pois = query.all()
            
            locations = []
            for poi in discovered_pois:
                location_data = {
                    "id": poi.id,
                    "name": poi.generated_name,
                    "type": poi.poi_type,
                    "state": poi.current_state,
                    "location_tags": poi.relative_location_tags,
                    "travel_time": poi.travel_time_from_major,
                    "discovered_at": poi.discovered_at.isoformat() if poi.discovered_at else None,
                    "has_details": poi.details_generated
                }
                
                # Add biome information
                if poi.biome:
                    location_data["biome"] = {
                        "name": poi.biome.name,
                        "type": poi.biome.biome_type
                    }
                
                # Add generated details if they exist
                if poi.location_details:
                    details = poi.location_details[0]  # Assuming one detail record per POI
                    location_data["services"] = details.available_services
                    location_data["quest_hooks"] = details.quest_hooks
                    location_data["npcs"] = len(details.generated_npcs or [])
                
                locations.append(location_data)
            
            return locations
            
        except Exception as e:
            self.logger.error(f"Error getting player discovered locations: {e}")
            return []
    
    def update_poi_persistent_state(
        self,
        db: Session,
        poi_id: str,
        state_changes: Dict[str, Any]
    ) -> bool:
        """
        Update persistent state information for a POI.
        
        Args:
            db: Database session
            poi_id: POI identifier
            state_changes: Dictionary of changes to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            poi = db.query(DBPointOfInterest).filter(
                DBPointOfInterest.id == poi_id
            ).first()
            
            if not poi:
                self.logger.error(f"POI {poi_id} not found")
                return False
            
            # Update POI state
            if "current_state" in state_changes:
                poi.current_state = state_changes["current_state"]
            
            if "last_visited" in state_changes:
                poi.last_visited = datetime.utcnow()
            
            # Update location details if they exist
            if poi.location_details and "location_updates" in state_changes:
                details = poi.location_details[0]
                location_updates = state_changes["location_updates"]
                
                if "new_issues" in location_updates:
                    current_issues = details.local_issues or []
                    current_issues.extend(location_updates["new_issues"])
                    details.local_issues = current_issues
                
                if "resolved_issues" in location_updates:
                    current_issues = details.local_issues or []
                    for resolved in location_updates["resolved_issues"]:
                        if resolved in current_issues:
                            current_issues.remove(resolved)
                    details.local_issues = current_issues
                
                if "npc_updates" in location_updates:
                    # Update NPC states/relationships
                    npc_updates = location_updates["npc_updates"]
                    current_npcs = details.generated_npcs or []
                    
                    for npc_update in npc_updates:
                        npc_id = npc_update.get("id")
                        for npc in current_npcs:
                            if npc.get("id") == npc_id:
                                npc.update(npc_update.get("changes", {}))
                                break
                    
                    details.generated_npcs = current_npcs
                
                details.last_refreshed = datetime.utcnow()
            
            db.commit()
            self.logger.info(f"Updated persistent state for POI {poi.generated_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating POI persistent state: {e}")
            db.rollback()
            return False
    
    def get_world_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get statistics about the current world state.
        """
        try:
            stats = {}
            
            # Region statistics
            total_regions = db.query(DBRegion).count()
            stats["regions"] = {
                "total": total_regions
            }
            
            # Biome statistics
            total_biomes = db.query(DBBiome).count()
            stats["biomes"] = {
                "total": total_biomes
            }
            
            # POI statistics
            total_pois = db.query(DBPointOfInterest).count()
            discovered_pois = db.query(DBPointOfInterest).filter(
                DBPointOfInterest.current_state != POIState.UNDISCOVERED.value
            ).count()
            generated_details = db.query(DBGeneratedLocationDetails).count()
            
            stats["points_of_interest"] = {
                "total": total_pois,
                "discovered": discovered_pois,
                "undiscovered": total_pois - discovered_pois,
                "with_generated_details": generated_details,
                "discovery_rate": (discovered_pois / total_pois * 100) if total_pois > 0 else 0
            }
            
            # POI type breakdown
            poi_types = db.query(DBPointOfInterest.poi_type).distinct().all()
            poi_type_counts = {}
            for poi_type_tuple in poi_types:
                poi_type = poi_type_tuple[0]
                count = db.query(DBPointOfInterest).filter(
                    DBPointOfInterest.poi_type == poi_type
                ).count()
                poi_type_counts[poi_type] = count
            
            stats["poi_types"] = poi_type_counts
            
            # Discovery timeline (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_discoveries = db.query(DBPointOfInterest).filter(
                and_(
                    DBPointOfInterest.discovered_at >= week_ago,
                    DBPointOfInterest.discovered_at <= datetime.utcnow()
                )
            ).count()
            
            stats["recent_activity"] = {
                "discoveries_last_week": recent_discoveries
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting world statistics: {e}")
            return {}
    
    def cleanup_old_world_data(
        self,
        db: Session,
        days_threshold: int = 30
    ) -> Dict[str, int]:
        """
        Clean up old, unused world data to prevent database bloat.
        
        Args:
            db: Database session
            days_threshold: Number of days after which to consider data old
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
            cleanup_stats = {
                "pois_cleaned": 0,
                "details_cleaned": 0
            }
            
            # Find old, undiscovered POIs that were created but never interacted with
            old_undiscovered_pois = db.query(DBPointOfInterest).filter(
                and_(
                    DBPointOfInterest.current_state == POIState.UNDISCOVERED.value,
                    DBPointOfInterest.created_at < cutoff_date,
                    DBPointOfInterest.discovered_at.is_(None),
                    DBPointOfInterest.last_visited.is_(None)
                )
            ).all()
            
            # Delete their details first
            for poi in old_undiscovered_pois:
                if poi.location_details:
                    for details in poi.location_details:
                        db.delete(details)
                        cleanup_stats["details_cleaned"] += 1
                
                db.delete(poi)
                cleanup_stats["pois_cleaned"] += 1
            
            db.commit()
            
            self.logger.info(
                f"Cleaned up {cleanup_stats['pois_cleaned']} old POIs and "
                f"{cleanup_stats['details_cleaned']} detail records"
            )
            
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            db.rollback()
            return {"pois_cleaned": 0, "details_cleaned": 0}
    
    def export_world_data(
        self,
        db: Session,
        region_ids: Optional[List[str]] = None,
        include_undiscovered: bool = False
    ) -> Dict[str, Any]:
        """
        Export world data for backup or analysis purposes.
        
        Args:
            db: Database session
            region_ids: Specific regions to export, or None for all
            include_undiscovered: Whether to include undiscovered POIs
            
        Returns:
            Dictionary containing exportable world data
        """
        try:
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "regions": [],
                "statistics": self.get_world_statistics(db)
            }
            
            # Build region query
            region_query = db.query(DBRegion)
            if region_ids:
                region_query = region_query.filter(DBRegion.id.in_(region_ids))
            
            regions = region_query.all()
            
            for region in regions:
                region_data = {
                    "id": region.id,
                    "name": region.name,
                    "description": region.description,
                    "core_lore": region.core_lore,
                    "dominant_races": region.dominant_races,
                    "biomes": []
                }
                
                # Export biomes
                for biome in region.biomes:
                    biome_data = {
                        "id": biome.id,
                        "name": biome.name,
                        "biome_type": biome.biome_type,
                        "description": biome.description,
                        "poi_density": biome.poi_density,
                        "points_of_interest": []
                    }
                    
                    # Export POIs
                    poi_query = db.query(DBPointOfInterest).filter(
                        DBPointOfInterest.biome_id == biome.id
                    )
                    
                    if not include_undiscovered:
                        poi_query = poi_query.filter(
                            DBPointOfInterest.current_state != POIState.UNDISCOVERED.value
                        )
                    
                    pois = poi_query.all()
                    
                    for poi in pois:
                        poi_data = {
                            "id": poi.id,
                            "name": poi.generated_name,
                            "type": poi.poi_type,
                            "state": poi.current_state,
                            "location_tags": poi.relative_location_tags,
                            "discovery_difficulty": poi.discovery_difficulty,
                            "discovered_at": poi.discovered_at.isoformat() if poi.discovered_at else None
                        }
                        
                        # Include generated details if they exist
                        if poi.location_details:
                            details = poi.location_details[0]
                            poi_data["details"] = {
                                "description": details.description,
                                "features": details.detailed_features,
                                "services": details.available_services,
                                "quest_hooks": details.quest_hooks,
                                "npc_count": len(details.generated_npcs or [])
                            }
                        
                        biome_data["points_of_interest"].append(poi_data)
                    
                    region_data["biomes"].append(biome_data)
                
                export_data["regions"].append(region_data)
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting world data: {e}")
            return {}
