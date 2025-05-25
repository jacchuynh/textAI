"""
Leyline-Enhanced Crafting Station Service
Handles crafting stations connected to leylines for enhanced magical crafting
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid
import logging
import math

from sqlalchemy.orm import Session
from sqlalchemy import func

from .magic_crafting_models import (
    LeylineCraftingStation, MagicalCraftingEvent, 
    MagicalMaterialInstance, EnchantedItem
)
from .magic_system import MagicSystem, MagicUser
from .advanced_magic_features import EnvironmentalMagicResonance
from backend.src.db.database import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Cache for frequently accessed stations
crafting_station_cache = {}

class LeylineCraftingService:
    """
    Service for leyline-enhanced crafting stations
    Integrates magic system with crafting for enhanced item creation
    """
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the leyline crafting service
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
        self.environmental_resonance = EnvironmentalMagicResonance()
    
    def get_db_session(self) -> Session:
        """Get a database session"""
        return SessionLocal()
    
    def get_crafting_station(self, station_id: str) -> Optional[Dict[str, Any]]:
        """
        Get crafting station data with caching
        
        Args:
            station_id: ID of the crafting station
            
        Returns:
            Station data or None if not found
        """
        # Check cache first
        if station_id in crafting_station_cache:
            return crafting_station_cache[station_id]
        
        # Query database
        session = self.get_db_session()
        try:
            station = session.query(LeylineCraftingStation).filter_by(id=station_id).first()
            if not station:
                return None
            
            # Convert to dictionary
            station_data = {
                "id": station.id,
                "name": station.name,
                "location_id": station.location_id,
                "station_type": station.station_type,
                "leyline_connection": station.leyline_connection,
                "quality_bonus": station.quality_bonus,
                "material_efficiency": station.material_efficiency,
                "time_efficiency": station.time_efficiency,
                "special_abilities": station.special_abilities,
                "access_level": station.access_level,
                "required_reputation": station.required_reputation,
                "is_active": station.is_active,
                "last_leyline_update": station.last_leyline_update.isoformat() if station.last_leyline_update else None
            }
            
            # Cache for 30 minutes (stations can change with leyline fluctuations)
            crafting_station_cache[station_id] = station_data
            return station_data
            
        finally:
            session.close()
    
    def get_crafting_stations_in_region(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Get all crafting stations in a region
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of crafting stations
        """
        session = self.get_db_session()
        try:
            # Find all stations in locations within the region
            stations = session.query(LeylineCraftingStation).filter(
                LeylineCraftingStation.location_id.like(f"{region_id}%"),
                LeylineCraftingStation.is_active == True
            ).all()
            
            # Convert to dictionaries
            stations_data = []
            for station in stations:
                station_data = self.get_crafting_station(station.id)
                if station_data:
                    stations_data.append(station_data)
            
            return stations_data
            
        finally:
            session.close()
    
    def update_leyline_connections(self) -> Dict[str, Any]:
        """
        Update leyline connections for all crafting stations
        Should be run periodically (e.g., daily)
        
        Returns:
            Status of the update operation
        """
        session = self.get_db_session()
        try:
            # Find stations that haven't been updated in the last day
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            stations = session.query(LeylineCraftingStation).filter(
                LeylineCraftingStation.last_leyline_update < one_day_ago,
                LeylineCraftingStation.is_active == True
            ).all()
            
            updated_count = 0
            
            for station in stations:
                # Get location leyline information
                # In a real implementation, this would query the location service
                # For now, we'll simulate random leyline fluctuations
                
                # Small random fluctuation in leyline connection
                fluctuation = random.uniform(-0.2, 0.3)
                new_connection = max(0.5, min(5.0, station.leyline_connection + fluctuation))
                
                # Update station stats based on new connection
                station.leyline_connection = new_connection
                station.quality_bonus = 0.05 * new_connection
                station.material_efficiency = max(0.5, 1.0 - (0.05 * new_connection))
                station.time_efficiency = max(0.5, 1.0 - (0.05 * new_connection))
                station.last_leyline_update = datetime.utcnow()
                
                # Invalidate cache
                if station.id in crafting_station_cache:
                    del crafting_station_cache[station.id]
                
                updated_count += 1
            
            session.commit()
            
            return {
                "success": True,
                "updated_stations": updated_count,
                "message": f"Updated leyline connections for {updated_count} crafting stations"
            }
            
        except Exception as e:
            logger.error(f"Error updating leyline connections: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def can_access_station(self, player_id: str, station_id: str, 
                        player_reputation: int = 0) -> Tuple[bool, str]:
        """
        Check if a player can access a crafting station
        
        Args:
            player_id: ID of the player
            station_id: ID of the crafting station
            player_reputation: Player's reputation level
            
        Returns:
            Tuple of (can_access, reason)
        """
        # Get station data
        station_data = self.get_crafting_station(station_id)
        if not station_data:
            return False, "Station not found"
        
        # Check if station is active
        if not station_data.get("is_active", False):
            return False, "This crafting station is currently inactive"
        
        # Check reputation requirements
        required_reputation = station_data.get("required_reputation", 0)
        if player_reputation < required_reputation:
            return False, f"Insufficient reputation. Required: {required_reputation}, Current: {player_reputation}"
        
        # Check access level (0=public, higher=restricted)
        access_level = station_data.get("access_level", 0)
        if access_level > 0:
            # In a real implementation, this would check faction membership, guild access, etc.
            # For now, we'll just assume access is granted if we get this far
            pass
        
        return True, "Access granted"
    
    def craft_item_with_magic(self, player_id: str, station_id: str, recipe_id: str,
                           materials: List[Dict[str, Any]], magic_profile: MagicUser,
                           character_skills: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Craft an item with magical enhancement from a leyline crafting station
        
        Args:
            player_id: ID of the player
            station_id: ID of the crafting station
            recipe_id: ID of the recipe being crafted
            materials: List of materials being used
            magic_profile: Player's magic profile
            character_skills: Optional character skills
            
        Returns:
            Result of the crafting attempt
        """
        session = self.get_db_session()
        try:
            # Get station data
            station_data = self.get_crafting_station(station_id)
            if not station_data:
                return {"success": False, "reason": "Crafting station not found"}
            
            # Check access
            can_access, reason = self.can_access_station(player_id, station_id)
            if not can_access:
                return {"success": False, "reason": reason}
            
            # Verify that we have all materials
            material_ids = [m.get("material_id") for m in materials if m.get("material_id")]
            material_instances = session.query(MagicalMaterialInstance).filter(
                MagicalMaterialInstance.id.in_([uuid.UUID(mid) if isinstance(mid, str) else mid for mid in material_ids])
            ).all()
            
            if len(material_instances) != len(material_ids):
                return {"success": False, "reason": "Some materials are not available"}
            
            # In a real implementation, this would invoke the crafting system
            # Here we'll just simulate the crafting process with leyline enhancement
            
            # Calculate base crafting skill
            crafting_skill = (character_skills.get("crafting", 0) if character_skills else 0)
            
            # Calculate magic enhancement
            leyline_connection = station_data.get("leyline_connection", 1.0)
            
            # Calculate magic contribution
            arcane_mastery = magic_profile.arcane_mastery if hasattr(magic_profile, "arcane_mastery") else 0
            mana_infusion = magic_profile.mana_infusion if hasattr(magic_profile, "mana_infusion") else 0
            
            magic_skill = (arcane_mastery * 0.7) + (mana_infusion * 0.3)
            
            # Calculate total crafting skill
            total_skill = crafting_skill + (magic_skill * 0.5)
            
            # Calculate quality bonus from station
            station_quality_bonus = station_data.get("quality_bonus", 0.0)
            
            # Calculate material quality
            material_quality = 0.0
            material_count = 0
            
            for material in material_instances:
                material_quality += material.quality
                material_count += 1
            
            avg_material_quality = material_quality / material_count if material_count > 0 else 1.0
            
            # Calculate base success chance
            base_success_chance = 0.7 + (total_skill * 0.02)
            
            # Material quality affects success
            material_factor = avg_material_quality * 0.1
            
            # Final success chance
            success_chance = min(0.95, base_success_chance + material_factor)
            
            # Check if mana is required
            mana_cost = int(10 * leyline_connection)
            
            if mana_cost > 0 and magic_profile.mana_current < mana_cost:
                return {
                    "success": False, 
                    "reason": f"Insufficient mana for magical crafting ({magic_profile.mana_current}/{mana_cost})"
                }
            
            # Deduct mana if needed
            if mana_cost > 0:
                magic_profile.use_mana(mana_cost)
            
            # Roll for success
            if random.random() < success_chance:
                # Success! Calculate item quality
                base_quality = 1.0
                skill_bonus = total_skill * 0.01
                leyline_bonus = leyline_connection * station_quality_bonus
                material_bonus = (avg_material_quality - 1.0) * 0.3
                
                # Final quality
                item_quality = min(2.0, base_quality + skill_bonus + leyline_bonus + material_bonus)
                
                # Round to 2 decimal places
                item_quality = round(item_quality, 2)
                
                # Calculate material efficiency (lower is better)
                material_efficiency = station_data.get("material_efficiency", 1.0)
                
                # Calculate time efficiency (lower is better)
                time_efficiency = station_data.get("time_efficiency", 1.0)
                
                # Calculate chance for special properties
                special_property_chance = 0.1 + (leyline_connection * 0.05) + (magic_skill * 0.01)
                has_special_properties = random.random() < special_property_chance
                
                special_properties = None
                if has_special_properties:
                    special_properties = self._generate_magical_properties(
                        leyline_connection, magic_profile, item_quality)
                
                # Simulate creating the crafted item (in reality, this would call the crafting system)
                crafted_item = {
                    "id": f"crafted_item_{uuid.uuid4().hex}",
                    "recipe_id": recipe_id,
                    "name": f"Magically Enhanced Item",  # This would come from the recipe
                    "quality": item_quality,
                    "created_at": datetime.utcnow().isoformat(),
                    "crafted_by": player_id,
                    "station_id": station_id,
                    "materials_used": [m.get("material_id") for m in materials if m.get("material_id")],
                    "has_special_properties": has_special_properties,
                    "special_properties": special_properties
                }
                
                # In a real implementation, the crafted item would be saved to the database
                
                # Log the crafting event
                event_data = {
                    "recipe_id": recipe_id,
                    "station_id": station_id,
                    "materials_used": [m.get("material_id") for m in materials if m.get("material_id")],
                    "quality": item_quality,
                    "leyline_connection": leyline_connection,
                    "mana_cost": mana_cost,
                    "material_efficiency": material_efficiency,
                    "time_efficiency": time_efficiency,
                    "has_special_properties": has_special_properties
                }
                
                magic_event = MagicalCraftingEvent(
                    player_id=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                    event_type="craft",
                    item_id=crafted_item["id"],
                    location_id=station_data.get("location_id"),
                    event_data=event_data,
                    success=True,
                    mana_cost=mana_cost,
                    leyline_influence=leyline_connection
                )
                
                session.add(magic_event)
                
                # Remove used materials
                for material in material_instances:
                    # Remove one of each material (adjust quantity as needed)
                    material.quantity -= 1
                    
                    if material.quantity <= 0:
                        session.delete(material)
                
                session.commit()
                
                # Create success message
                success_message = self._generate_crafting_success_message(
                    station_data, crafted_item, leyline_connection)
                
                return {
                    "success": True,
                    "item": crafted_item,
                    "message": success_message,
                    "mana_used": mana_cost,
                    "material_efficiency": material_efficiency,
                    "time_efficiency": time_efficiency
                }
            else:
                # Failure
                # Determine material loss on failure
                material_loss_chance = 0.3 - (total_skill * 0.01)
                material_loss_chance = max(0.0, min(0.3, material_loss_chance))
                
                materials_lost = []
                
                for material in material_instances:
                    if random.random() < material_loss_chance:
                        # Lost this material
                        material.quantity -= 1
                        materials_lost.append(material.material_id)
                        
                        if material.quantity <= 0:
                            session.delete(material)
                
                # Log the failed crafting event
                event_data = {
                    "recipe_id": recipe_id,
                    "station_id": station_id,
                    "materials_used": [m.get("material_id") for m in materials if m.get("material_id")],
                    "materials_lost": materials_lost,
                    "mana_cost": mana_cost,
                    "leyline_connection": leyline_connection
                }
                
                magic_event = MagicalCraftingEvent(
                    player_id=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                    event_type="craft",
                    location_id=station_data.get("location_id"),
                    event_data=event_data,
                    success=False,
                    mana_cost=mana_cost,
                    leyline_influence=leyline_connection
                )
                
                session.add(magic_event)
                session.commit()
                
                # Create failure message
                failure_message = self._generate_crafting_failure_message(
                    station_data, materials_lost, leyline_connection)
                
                return {
                    "success": False,
                    "message": failure_message,
                    "mana_used": mana_cost,
                    "materials_lost": materials_lost
                }
            
        except Exception as e:
            logger.error(f"Error crafting with magic: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def _generate_magical_properties(self, leyline_connection: float, 
                                magic_profile: MagicUser,
                                item_quality: float) -> Dict[str, Any]:
        """
        Generate magical properties for a crafted item
        
        Args:
            leyline_connection: Strength of the leyline connection
            magic_profile: Player's magic profile
            item_quality: Quality of the crafted item
            
        Returns:
            Magical properties dictionary
        """
        properties = {}
        
        # Base properties based on leyline connection
        if leyline_connection >= 2.0:
            properties["magical_conductivity"] = round(0.2 * leyline_connection, 2)
        
        if leyline_connection >= 3.0:
            properties["mana_regeneration"] = round(0.05 * leyline_connection, 2)
        
        if leyline_connection >= 4.0:
            properties["spell_amplification"] = round(0.03 * leyline_connection, 2)
        
        # Properties based on magic profile
        arcane_mastery = magic_profile.arcane_mastery if hasattr(magic_profile, "arcane_mastery") else 0
        mana_infusion = magic_profile.mana_infusion if hasattr(magic_profile, "mana_infusion") else 0
        
        if arcane_mastery >= 3:
            properties["arcane_resonance"] = round(0.1 * arcane_mastery, 2)
        
        if mana_infusion >= 3:
            properties["mana_efficiency"] = round(0.1 * mana_infusion, 2)
        
        # Properties based on item quality
        if item_quality >= 1.5:
            properties["magical_durability"] = round(item_quality * 0.2, 2)
        
        if item_quality >= 1.8:
            properties["magical_potency"] = round(item_quality * 0.3, 2)
        
        # Random specialized property (20% chance)
        if random.random() < 0.2:
            specialized_properties = [
                ("elemental_affinity", ["fire", "ice", "lightning", "earth", "air"]),
                ("damage_resistance", ["physical", "magical", "elemental", "void"]),
                ("skill_bonus", ["crafting", "enchanting", "gathering", "perception"]),
                ("stat_bonus", ["strength", "agility", "mind", "spirit"])
            ]
            
            prop_type, prop_values = random.choice(specialized_properties)
            prop_value = random.choice(prop_values)
            prop_magnitude = round(0.1 + (item_quality * 0.1), 2)
            
            properties[f"{prop_type}_{prop_value}"] = prop_magnitude
        
        return properties
    
    def _generate_crafting_success_message(self, station_data: Dict[str, Any],
                                      crafted_item: Dict[str, Any],
                                      leyline_connection: float) -> str:
        """
        Generate a descriptive message about successful crafting
        
        Args:
            station_data: Station data
            crafted_item: Crafted item data
            leyline_connection: Strength of the leyline connection
            
        Returns:
            Descriptive message
        """
        station_name = station_data.get("name", "crafting station")
        
        # Base message by station type
        station_type = station_data.get("station_type", "forge")
        
        base_messages = {
            "forge": [
                f"The {station_name} hums with magical energy as you work the metal.",
                f"Leyline energy flows through the {station_name}, imbuing your work with magical potential.",
                f"The fires of the {station_name} burn with an otherworldly glow as you craft."
            ],
            "alchemy_lab": [
                f"Magical energies swirl around the {station_name} as you mix the components.",
                f"The leyline connection causes your mixtures to shimmer with arcane potential.",
                f"The {station_name}'s equipment resonates with the ambient magical energy."
            ],
            "enchanting_table": [
                f"The runes on the {station_name} glow brilliantly as you work.",
                f"Leyline energy flows through the {station_name}, empowering your enchantments.",
                f"The {station_name} magnifies your magical abilities as you craft."
            ],
            "workbench": [
                f"The tools of the {station_name} seem to move with supernatural precision.",
                f"Leyline energy suffuses the materials as you work at the {station_name}.",
                f"The {station_name} enhances your crafting with subtle magical energies."
            ]
        }
        
        base_message = random.choice(
            base_messages.get(station_type, [f"The {station_name} enhances your crafting with magical energy."])
        )
        
        # Quality description
        quality = crafted_item.get("quality", 1.0)
        if quality >= 1.8:
            quality_desc = "masterwork quality"
        elif quality >= 1.5:
            quality_desc = "excellent quality"
        elif quality >= 1.2:
            quality_desc = "good quality"
        else:
            quality_desc = "average quality"
        
        # Special properties description
        special_props = ""
        if crafted_item.get("has_special_properties", False):
            if leyline_connection >= 4.0:
                special_props = " It pulses with powerful magical energy."
            elif leyline_connection >= 3.0:
                special_props = " It glows with magical potential."
            elif leyline_connection >= 2.0:
                special_props = " It has a subtle magical aura."
            else:
                special_props = " It has unusual magical properties."
        
        # Combine all parts
        return f"{base_message} You successfully create a {quality_desc} item.{special_props}"
    
    def _generate_crafting_failure_message(self, station_data: Dict[str, Any],
                                      materials_lost: List[str],
                                      leyline_connection: float) -> str:
        """
        Generate a descriptive message about failed crafting
        
        Args:
            station_data: Station data
            materials_lost: List of lost material IDs
            leyline_connection: Strength of the leyline connection
            
        Returns:
            Descriptive message
        """
        station_name = station_data.get("name", "crafting station")
        
        # Base message by station type
        station_type = station_data.get("station_type", "forge")
        
        failure_messages = {
            "forge": [
                f"The leyline energy surges through the {station_name}, causing your work to crack.",
                f"Your control slips and the magical energies of the {station_name} disrupt your crafting.",
                f"The materials react unpredictably to the magical energies of the {station_name}."
            ],
            "alchemy_lab": [
                f"The mixture bubbles violently and dissipates as the leyline energies interfere.",
                f"Magical resonance from the {station_name} causes your concoction to destabilize.",
                f"The components react chaotically to the ambient magical energies."
            ],
            "enchanting_table": [
                f"The runes on the {station_name} flare painfully bright as your enchantment fails.",
                f"The leyline connection overwhelms your magical control, disrupting the enchantment.",
                f"Your enchantment unravels as the {station_name}'s energies fluctuate unpredictably."
            ],
            "workbench": [
                f"The materials warp under the influence of the {station_name}'s magical field.",
                f"Your work falls apart as the leyline energy interferes with your crafting.",
                f"The subtle magical energies of the {station_name} cause unexpected complications."
            ]
        }
        
        failure_message = random.choice(
            failure_messages.get(station_type, [f"The magical energies of the {station_name} disrupt your crafting."])
        )
        
        # Materials lost description
        if materials_lost:
            if len(materials_lost) == 1:
                materials_desc = " You lost a material in the process."
            else:
                materials_desc = f" You lost {len(materials_lost)} materials in the process."
        else:
            materials_desc = " Fortunately, you didn't lose any materials."
        
        # Advice based on leyline connection
        if leyline_connection >= 4.0:
            advice = " The leyline connection is very strong - you may need more magical control to work here."
        elif leyline_connection >= 3.0:
            advice = " You'll need more skill to work with this level of magical energy."
        else:
            advice = " More practice with magical crafting might help."
        
        # Combine all parts
        return f"{failure_message}{materials_desc}{advice}"
    
    def create_crafting_station(self, name: str, location_id: str, station_type: str,
                             leyline_strength: float = 1.0) -> Dict[str, Any]:
        """
        Create a new leyline crafting station
        
        Args:
            name: Name of the station
            location_id: ID of the location
            station_type: Type of crafting station
            leyline_strength: Initial leyline strength
            
        Returns:
            Newly created station data
        """
        session = self.get_db_session()
        try:
            # Generate station ID
            station_id = f"{station_type}_{location_id}_{uuid.uuid4().hex[:8]}"
            
            # Calculate initial stats based on leyline strength
            quality_bonus = 0.05 * leyline_strength
            material_efficiency = max(0.5, 1.0 - (0.05 * leyline_strength))
            time_efficiency = max(0.5, 1.0 - (0.05 * leyline_strength))
            
            # Generate special abilities
            special_abilities = {}
            
            if leyline_strength >= 2.0:
                special_abilities["magical_affinity"] = True
            
            if leyline_strength >= 3.0:
                special_abilities["leyline_channeling"] = True
            
            if leyline_strength >= 4.0:
                special_abilities["rare_crafting"] = True
            
            # Create the station
            station = LeylineCraftingStation(
                id=station_id,
                name=name,
                location_id=location_id,
                station_type=station_type,
                leyline_connection=leyline_strength,
                quality_bonus=quality_bonus,
                material_efficiency=material_efficiency,
                time_efficiency=time_efficiency,
                special_abilities=special_abilities,
                access_level=0,  # Public by default
                required_reputation=0,
                is_active=True,
                last_leyline_update=datetime.utcnow()
            )
            
            session.add(station)
            session.commit()
            
            # Get the new station data
            station_data = self.get_crafting_station(station_id)
            
            return {
                "success": True,
                "station": station_data,
                "message": f"Created new {station_type} crafting station: {name}"
            }
            
        except Exception as e:
            logger.error(f"Error creating crafting station: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def get_station_statistics(self, station_id: str) -> Dict[str, Any]:
        """
        Get statistics about a crafting station's usage
        
        Args:
            station_id: ID of the crafting station
            
        Returns:
            Station usage statistics
        """
        session = self.get_db_session()
        try:
            # Get basic station info
            station = self.get_crafting_station(station_id)
            if not station:
                return {"success": False, "reason": "Station not found"}
            
            # Get recent crafting events
            one_month_ago = datetime.utcnow() - timedelta(days=30)
            
            crafting_events = session.query(MagicalCraftingEvent).filter(
                MagicalCraftingEvent.event_data['station_id'].astext == station_id,
                MagicalCraftingEvent.created_at >= one_month_ago
            ).all()
            
            # Calculate statistics
            total_crafts = len(crafting_events)
            successful_crafts = sum(1 for e in crafting_events if e.success)
            success_rate = successful_crafts / total_crafts if total_crafts > 0 else 0
            
            # Calculate average quality
            quality_sum = sum(
                float(e.event_data.get('quality', 0)) 
                for e in crafting_events 
                if e.success and 'quality' in e.event_data
            )
            avg_quality = quality_sum / successful_crafts if successful_crafts > 0 else 0
            
            # Get unique users
            unique_users = len(set(str(e.player_id) for e in crafting_events))
            
            # Get most common recipes
            recipe_counts = {}
            for event in crafting_events:
                recipe_id = event.event_data.get('recipe_id')
                if recipe_id:
                    recipe_counts[recipe_id] = recipe_counts.get(recipe_id, 0) + 1
            
            top_recipes = sorted(recipe_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "success": True,
                "station_id": station_id,
                "station_name": station.get("name"),
                "station_type": station.get("station_type"),
                "leyline_connection": station.get("leyline_connection"),
                "total_crafts": total_crafts,
                "successful_crafts": successful_crafts,
                "success_rate": round(success_rate * 100, 1),
                "average_quality": round(avg_quality, 2),
                "unique_users": unique_users,
                "top_recipes": [{"recipe_id": r[0], "count": r[1]} for r in top_recipes]
            }
            
        except Exception as e:
            logger.error(f"Error getting station statistics: {e}")
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()