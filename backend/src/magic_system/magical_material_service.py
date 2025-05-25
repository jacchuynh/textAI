"""
Magical Material Service
Handles gathering, processing, and managing magical materials
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
    MagicalMaterial, MagicalMaterialInstance, MagicalGatheringLocation, 
    MagicalCraftingEvent
)
from .magic_system import MagicSystem, MagicUser
from .advanced_magic_features import EnvironmentalMagicResonance
from ..db.database import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Cache for frequently accessed material data
material_cache = {}
gathering_location_cache = {}

class MagicalMaterialService:
    """
    Service for gathering and managing magical materials
    Integrates with the magic system for location-based material discovery
    """
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the magical material service
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
        self.environmental_resonance = EnvironmentalMagicResonance()
    
    def get_db_session(self) -> Session:
        """Get a database session"""
        return SessionLocal()
    
    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """
        Get material data with caching
        
        Args:
            material_id: ID of the material
            
        Returns:
            Material data or None if not found
        """
        # Check cache first
        if material_id in material_cache:
            return material_cache[material_id]
        
        # Query database
        session = self.get_db_session()
        try:
            material = session.query(MagicalMaterial).filter_by(id=material_id).first()
            if not material:
                return None
            
            # Convert to dictionary
            material_data = {
                "id": material.id,
                "name": material.name,
                "description": material.description,
                "rarity": material.rarity,
                "magical_affinity": material.magical_affinity,
                "leyline_resonance": material.leyline_resonance,
                "corruption_resistance": material.corruption_resistance,
                "crafting_properties": material.crafting_properties,
                "gathering_difficulty": material.gathering_difficulty,
                "primary_locations": material.primary_locations,
                "required_tool": material.required_tool,
                "base_value": material.base_value,
                "base_yield": material.base_yield
            }
            
            # Cache for 1 hour (materials rarely change)
            material_cache[material_id] = material_data
            return material_data
            
        finally:
            session.close()
    
    def get_gathering_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        Get gathering location data with caching
        
        Args:
            location_id: ID of the gathering location
            
        Returns:
            Location data or None if not found
        """
        # Check cache first
        if location_id in gathering_location_cache:
            return gathering_location_cache[location_id]
        
        # Query database
        session = self.get_db_session()
        try:
            location = session.query(MagicalGatheringLocation).filter_by(id=location_id).first()
            if not location:
                return None
            
            # Convert to dictionary
            location_data = {
                "id": location.id,
                "name": location.name,
                "region_id": location.region_id,
                "location_type": location.location_type,
                "coordinates": location.coordinates,
                "available_materials": location.available_materials,
                "current_abundance": location.current_abundance,
                "leyline_strength": location.leyline_strength,
                "magical_aura": location.magical_aura,
                "corruption_level": location.corruption_level,
                "is_discovered": location.is_discovered,
                "discovery_difficulty": location.discovery_difficulty,
                "last_refresh": location.last_refresh.isoformat() if location.last_refresh else None
            }
            
            # Cache for 30 minutes (locations change more frequently)
            gathering_location_cache[location_id] = location_data
            return location_data
            
        finally:
            session.close()
    
    def get_gathering_locations_in_region(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Get all gathering locations in a region
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of gathering locations
        """
        session = self.get_db_session()
        try:
            locations = session.query(MagicalGatheringLocation).filter_by(region_id=region_id).all()
            
            # Convert to dictionaries
            locations_data = []
            for location in locations:
                # Check if discoverable by player
                if location.is_discovered:
                    location_data = self.get_gathering_location(location.id)
                    if location_data:
                        locations_data.append(location_data)
            
            return locations_data
            
        finally:
            session.close()
    
    def discover_gathering_location(self, player_id: str, region_id: str, 
                                 character_skills: Dict[str, int],
                                 magic_profile: MagicUser) -> Dict[str, Any]:
        """
        Attempt to discover a new gathering location in a region
        
        Args:
            player_id: ID of the player
            region_id: ID of the region
            character_skills: Character's skills
            magic_profile: Player's magic profile
            
        Returns:
            Result of the discovery attempt
        """
        session = self.get_db_session()
        try:
            # Find undiscovered locations in region
            undiscovered_locations = session.query(MagicalGatheringLocation).filter_by(
                region_id=region_id,
                is_discovered=False
            ).all()
            
            if not undiscovered_locations:
                return {"success": False, "reason": "No undiscovered locations in this region"}
            
            # Calculate discovery chance based on skills
            perception_skill = character_skills.get("perception", 0)
            tracking_skill = character_skills.get("tracking", 0)
            magical_sensitivity = magic_profile.ley_energy_sensitivity if hasattr(magic_profile, "ley_energy_sensitivity") else 0
            
            # Weighted skill calculation
            discovery_skill = (perception_skill * 0.4) + (tracking_skill * 0.3) + (magical_sensitivity * 0.3)
            
            # Sort locations by discovery difficulty
            undiscovered_locations.sort(key=lambda loc: loc.discovery_difficulty)
            
            for location in undiscovered_locations:
                # Base discovery chance
                base_chance = 0.1 + (discovery_skill * 0.05)
                
                # Difficulty adjustment
                difficulty_factor = 1.0 - (location.discovery_difficulty * 0.05)
                discovery_chance = base_chance * difficulty_factor
                
                # Cap minimum and maximum chance
                discovery_chance = max(0.05, min(0.9, discovery_chance))
                
                # Roll for discovery
                if random.random() < discovery_chance:
                    # Success! Mark as discovered
                    location.is_discovered = True
                    session.commit()
                    
                    # Invalidate cache
                    if location.id in gathering_location_cache:
                        del gathering_location_cache[location.id]
                    
                    # Return discovered location
                    location_data = self.get_gathering_location(location.id)
                    
                    return {
                        "success": True,
                        "location": location_data,
                        "discovery_message": f"You have discovered {location.name}!"
                    }
            
            # No successful discoveries
            return {
                "success": False, 
                "reason": "You searched but found no magical gathering locations",
                "try_again_message": "You might need to improve your perception or magical sensitivity"
            }
            
        except Exception as e:
            logger.error(f"Error discovering gathering location: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def gather_materials(self, player_id: str, location_id: str, 
                      character_skills: Dict[str, int],
                      magic_profile: MagicUser,
                      tool_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Gather magical materials from a location
        
        Args:
            player_id: ID of the player
            location_id: ID of the gathering location
            character_skills: Character's skills
            magic_profile: Player's magic profile
            tool_id: Optional ID of the gathering tool being used
            
        Returns:
            Result of the gathering attempt
        """
        session = self.get_db_session()
        try:
            # Get location data
            location_data = self.get_gathering_location(location_id)
            if not location_data:
                return {"success": False, "reason": "Location not found"}
            
            # Check if location is discovered
            if not location_data.get("is_discovered", False):
                return {"success": False, "reason": "You haven't discovered this location yet"}
            
            # Calculate gathering skill based on character skills
            gathering_skill = character_skills.get("gathering", 0)
            nature_knowledge = character_skills.get("nature_knowledge", 0)
            magical_sensitivity = magic_profile.ley_energy_sensitivity if hasattr(magic_profile, "ley_energy_sensitivity") else 0
            
            # Weighted skill calculation
            effective_skill = (gathering_skill * 0.5) + (nature_knowledge * 0.3) + (magical_sensitivity * 0.2)
            
            # Apply tool bonus if appropriate tool is used
            tool_bonus = 0.0
            if tool_id:
                # Get tool data - this would come from your item system
                # For now, just use a simple lookup
                tool_type = "basic_gathering_tool"  # This would be from the item system
                
                # Check if any materials require this tool
                required_tools = []
                for material_id, chance in location_data.get("available_materials", {}).items():
                    material_data = self.get_material(material_id)
                    if material_data and material_data.get("required_tool") == tool_type:
                        required_tools.append(material_id)
                
                if required_tools:
                    tool_bonus = 0.2  # 20% bonus for using the right tool
            
            # Get available materials at this location
            available_materials = location_data.get("available_materials", {})
            if not available_materials:
                return {"success": False, "reason": "No materials available at this location"}
            
            # Roll for each material
            gathered_materials = []
            special_finds = []
            
            for material_id, base_chance in available_materials.items():
                material_data = self.get_material(material_id)
                if not material_data:
                    continue
                
                # Calculate gathering chance
                gathering_difficulty = material_data.get("gathering_difficulty", 1)
                difficulty_factor = 1.0 - (gathering_difficulty * 0.05)
                
                # Base chance from location
                material_chance = float(base_chance)
                
                # Apply skill and bonuses
                skill_bonus = effective_skill * 0.05
                current_abundance = location_data.get("current_abundance", 1.0)
                
                # Final chance calculation
                final_chance = material_chance * difficulty_factor * (1.0 + skill_bonus) * current_abundance
                
                # Apply tool bonus if this material requires the tool
                if tool_id and material_data.get("required_tool") == tool_type:
                    final_chance *= (1.0 + tool_bonus)
                
                # Cap minimum and maximum chance
                final_chance = max(0.01, min(0.9, final_chance))
                
                # Roll for gathering
                if random.random() < final_chance:
                    # Success! Calculate quantity
                    base_yield = material_data.get("base_yield", 1)
                    skill_yield_bonus = max(0, math.floor(effective_skill / 3))
                    quantity = base_yield + random.randint(0, skill_yield_bonus)
                    
                    # Calculate quality
                    base_quality = 1.0
                    skill_quality_bonus = effective_skill * 0.02
                    luck_factor = random.uniform(-0.1, 0.3)
                    
                    quality = base_quality + skill_quality_bonus + luck_factor
                    
                    # Cap quality between 0.5 and 2.0
                    quality = max(0.5, min(2.0, quality))
                    
                    # Round to 2 decimal places
                    quality = round(quality, 2)
                    
                    # Chance for special properties
                    special_property_chance = 0.05 + (magical_sensitivity * 0.01)
                    has_special_properties = random.random() < special_property_chance
                    
                    special_properties = None
                    if has_special_properties:
                        special_properties = self._generate_special_properties(
                            material_data, location_data, quality)
                        special_finds.append({
                            "material_id": material_id,
                            "material_name": material_data["name"],
                            "special_properties": special_properties
                        })
                    
                    # Create material instance
                    material_instance = MagicalMaterialInstance(
                        material_id=material_id,
                        owner_id=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                        quantity=quantity,
                        quality=quality,
                        gathered_from=location_id,
                        gathered_by=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                        has_special_properties=has_special_properties,
                        special_properties=special_properties
                    )
                    
                    session.add(material_instance)
                    
                    # Add to gathered materials list
                    gathered_materials.append({
                        "material_id": material_id,
                        "material_name": material_data["name"],
                        "quantity": quantity,
                        "quality": quality,
                        "has_special_properties": has_special_properties
                    })
            
            # If nothing was gathered, return failure
            if not gathered_materials:
                return {
                    "success": False, 
                    "reason": "You searched but found no materials",
                    "skill_message": "Try improving your gathering skill or using better tools"
                }
            
            # Log the gathering event
            event_data = {
                "location_id": location_id,
                "gathered_materials": gathered_materials,
                "tool_id": tool_id,
                "skills": {
                    "gathering": gathering_skill,
                    "nature_knowledge": nature_knowledge,
                    "magical_sensitivity": magical_sensitivity
                }
            }
            
            magic_event = MagicalCraftingEvent(
                player_id=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                event_type="gather",
                location_id=location_id,
                event_data=event_data,
                success=True
            )
            
            session.add(magic_event)
            
            # Update location abundance (materials become slightly harder to find after gathering)
            location = session.query(MagicalGatheringLocation).filter_by(id=location_id).first()
            if location:
                # Reduce abundance by 5-15%
                reduction = random.uniform(0.05, 0.15)
                location.current_abundance = max(0.2, location.current_abundance - reduction)
                location.last_refresh = datetime.utcnow()
                
                # Invalidate cache
                if location_id in gathering_location_cache:
                    del gathering_location_cache[location_id]
            
            session.commit()
            
            # Return the result
            return {
                "success": True,
                "location_name": location_data["name"],
                "gathered_materials": gathered_materials,
                "special_finds": special_finds,
                "gathering_message": self._generate_gathering_message(location_data, gathered_materials)
            }
            
        except Exception as e:
            logger.error(f"Error gathering materials: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def _generate_special_properties(self, material_data: Dict[str, Any], 
                                 location_data: Dict[str, Any],
                                 quality: float) -> Dict[str, Any]:
        """
        Generate special properties for a gathered material
        
        Args:
            material_data: Material data
            location_data: Location data
            quality: Quality of the gathered material
            
        Returns:
            Special properties dictionary
        """
        special_properties = {}
        
        # Material affinity bonus
        if material_data.get("magical_affinity"):
            primary_affinity = material_data["magical_affinity"][0] if material_data["magical_affinity"] else None
            if primary_affinity:
                affinity_bonus = round(0.1 + (quality * 0.05), 2)
                special_properties[f"{primary_affinity.lower()}_affinity"] = affinity_bonus
        
        # Location-specific properties
        if location_data.get("leyline_strength", 0) >= 3:
            special_properties["leyline_resonance"] = round(location_data["leyline_strength"] * 0.1, 2)
        
        if location_data.get("magical_aura"):
            aura_type = location_data["magical_aura"].lower()
            special_properties[f"{aura_type}_infusion"] = round(0.2 + (quality * 0.1), 2)
        
        # Quality-based special properties
        if quality >= 1.5:
            special_properties["enchantment_receptivity"] = round(quality * 0.2, 2)
        
        if quality >= 1.8:
            special_properties["magical_stability"] = round(quality * 0.15, 2)
        
        # Rare additional property chance (10%)
        if random.random() < 0.1:
            rare_properties = [
                ("essence_purity", round(random.uniform(0.3, 0.8), 2)),
                ("magical_conductivity", round(random.uniform(0.3, 0.7), 2)),
                ("transmutation_catalyst", round(random.uniform(0.2, 0.6), 2)),
                ("ritual_amplifier", round(random.uniform(0.3, 0.7), 2)),
                ("crystalline_structure", round(random.uniform(0.4, 0.8), 2))
            ]
            
            rare_property = random.choice(rare_properties)
            special_properties[rare_property[0]] = rare_property[1]
        
        return special_properties
    
    def _generate_gathering_message(self, location_data: Dict[str, Any], 
                               gathered_materials: List[Dict[str, Any]]) -> str:
        """
        Generate a descriptive message about the gathering results
        
        Args:
            location_data: Location data
            gathered_materials: List of gathered materials
            
        Returns:
            Descriptive message
        """
        location_type = location_data.get("location_type", "area")
        location_name = location_data.get("name", "location")
        
        # Generate appropriate message based on location type
        location_descriptions = {
            "forest": [
                f"You carefully search among the trees and foliage of {location_name}.",
                f"Wandering through the ancient trees of {location_name}, you gather materials.",
                f"The verdant growth of {location_name} yields magical substances."
            ],
            "mountain": [
                f"You climb the rocky slopes of {location_name}, searching for magical materials.",
                f"Scaling the heights of {location_name}, you discover hidden treasures.",
                f"The mineral-rich stones of {location_name} contain magical essences."
            ],
            "cave": [
                f"In the dark recesses of {location_name}, you find magical substances.",
                f"The echoing chambers of {location_name} hide magical materials.",
                f"Stalactites and stalagmites in {location_name} glitter with magical potential."
            ],
            "swamp": [
                f"You wade through the murky waters of {location_name}.",
                f"The humid air of {location_name} is thick with magical energy.",
                f"Beneath the surface of {location_name}, magical materials lurk."
            ],
            "coast": [
                f"Along the shores of {location_name}, you gather materials carried by the tides.",
                f"The crashing waves of {location_name} reveal magical substances.",
                f"Tidal pools in {location_name} contain concentrated magical essences."
            ]
        }
        
        # Get appropriate description or use default
        location_description = random.choice(
            location_descriptions.get(location_type.lower(), 
                                     [f"You search {location_name} for magical materials."])
        )
        
        # Create material description
        if len(gathered_materials) == 1:
            material = gathered_materials[0]
            material_description = f"You found {material['quantity']} {material['material_name']}."
            
            # Add quality description
            if material['quality'] >= 1.8:
                material_description += " The quality is exceptional!"
            elif material['quality'] >= 1.4:
                material_description += " The quality is excellent."
            elif material['quality'] >= 1.0:
                material_description += " The quality is good."
            else:
                material_description += " The quality is poor."
        else:
            # Multiple materials
            material_names = [f"{m['quantity']} {m['material_name']}" for m in gathered_materials]
            material_description = f"You found {', '.join(material_names[:-1])} and {material_names[-1]}."
            
            # Count high quality materials
            high_quality_count = sum(1 for m in gathered_materials if m['quality'] >= 1.4)
            if high_quality_count > 0:
                material_description += f" {high_quality_count} of these are of excellent quality."
        
        # Combine descriptions
        return f"{location_description} {material_description}"
    
    def refresh_gathering_locations(self) -> Dict[str, Any]:
        """
        Refresh material abundance in gathering locations
        Should be run periodically (e.g., daily)
        
        Returns:
            Status of the refresh operation
        """
        session = self.get_db_session()
        try:
            # Find locations that haven't been refreshed in the last day
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            locations = session.query(MagicalGatheringLocation).filter(
                MagicalGatheringLocation.last_refresh < one_day_ago
            ).all()
            
            refreshed_count = 0
            
            for location in locations:
                # Increase abundance
                location.current_abundance = min(1.0, location.current_abundance + random.uniform(0.3, 0.7))
                location.last_refresh = datetime.utcnow()
                
                # Invalidate cache
                if location.id in gathering_location_cache:
                    del gathering_location_cache[location.id]
                
                refreshed_count += 1
            
            session.commit()
            
            return {
                "success": True,
                "refreshed_locations": refreshed_count,
                "message": f"Refreshed {refreshed_count} gathering locations"
            }
            
        except Exception as e:
            logger.error(f"Error refreshing gathering locations: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def get_player_materials(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all materials owned by a player
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of material instances
        """
        session = self.get_db_session()
        try:
            # Convert player_id to UUID if needed
            player_uuid = uuid.UUID(player_id) if isinstance(player_id, str) else player_id
            
            # Query material instances
            material_instances = session.query(MagicalMaterialInstance).filter_by(owner_id=player_uuid).all()
            
            # Group by material_id and aggregate quantities
            materials_by_id = {}
            
            for instance in material_instances:
                material_data = self.get_material(instance.material_id)
                if not material_data:
                    continue
                
                # Create a unique key for this material + quality + special properties
                special_props_key = "none"
                if instance.has_special_properties and instance.special_properties:
                    # Create a stable hash of the special properties
                    special_props_key = str(hash(str(sorted(instance.special_properties.items()))))
                
                key = f"{instance.material_id}_{instance.quality}_{special_props_key}"
                
                if key not in materials_by_id:
                    materials_by_id[key] = {
                        "material_id": instance.material_id,
                        "material_name": material_data["name"],
                        "quality": instance.quality,
                        "quantity": 0,
                        "has_special_properties": instance.has_special_properties,
                        "special_properties": instance.special_properties,
                        "instances": []
                    }
                
                materials_by_id[key]["quantity"] += instance.quantity
                materials_by_id[key]["instances"].append({
                    "id": str(instance.id),
                    "quantity": instance.quantity,
                    "gathered_at": instance.gathered_at.isoformat() if instance.gathered_at else None
                })
            
            # Convert to list
            return list(materials_by_id.values())
            
        finally:
            session.close()
    
    def process_material(self, player_id: str, instance_id: str, 
                       processing_type: str,
                       character_skills: Dict[str, int],
                       magic_profile: Optional[MagicUser] = None) -> Dict[str, Any]:
        """
        Process a material to enhance its properties
        
        Args:
            player_id: ID of the player
            instance_id: ID of the material instance
            processing_type: Type of processing to perform
            character_skills: Character's skills
            magic_profile: Optional player's magic profile for magical processing
            
        Returns:
            Result of the processing attempt
        """
        session = self.get_db_session()
        try:
            # Convert instance_id to UUID if needed
            instance_uuid = uuid.UUID(instance_id) if isinstance(instance_id, str) else instance_id
            
            # Get the material instance
            instance = session.query(MagicalMaterialInstance).filter_by(id=instance_uuid).first()
            if not instance:
                return {"success": False, "reason": "Material instance not found"}
            
            # Verify ownership
            player_uuid = uuid.UUID(player_id) if isinstance(player_id, str) else player_id
            if instance.owner_id != player_uuid:
                return {"success": False, "reason": "You don't own this material"}
            
            # Get material data
            material_data = self.get_material(instance.material_id)
            if not material_data:
                return {"success": False, "reason": "Material data not found"}
            
            # Calculate processing skill
            crafting_skill = character_skills.get("crafting", 0)
            alchemy_skill = character_skills.get("alchemy", 0)
            
            # Different skills affect different processing types
            effective_skill = 0
            mana_cost = 0
            
            if processing_type == "refine":
                # Refining uses crafting skill
                effective_skill = crafting_skill
            elif processing_type == "extract":
                # Extraction uses alchemy skill
                effective_skill = alchemy_skill
            elif processing_type == "enchant":
                # Enchanting uses magic and crafting
                if not magic_profile:
                    return {"success": False, "reason": "Magic profile required for enchanting"}
                
                effective_skill = (crafting_skill * 0.5) + (magic_profile.arcane_mastery * 0.5)
                mana_cost = 10 + (5 * material_data.get("leyline_resonance", 1.0))
                
                # Check mana
                if magic_profile.mana_current < mana_cost:
                    return {
                        "success": False, 
                        "reason": f"Insufficient mana ({magic_profile.mana_current}/{mana_cost})"
                    }
            else:
                return {"success": False, "reason": f"Unknown processing type: {processing_type}"}
            
            # Calculate success chance
            base_chance = 0.5 + (effective_skill * 0.05)
            
            # Adjust for material quality
            quality_factor = instance.quality * 0.1
            
            # Material-specific difficulty
            material_difficulty = material_data.get("gathering_difficulty", 1) * 0.05
            
            # Final chance calculation
            success_chance = base_chance + quality_factor - material_difficulty
            
            # Cap minimum and maximum chance
            success_chance = max(0.1, min(0.95, success_chance))
            
            # Deduct mana if needed
            if mana_cost > 0 and magic_profile:
                magic_profile.use_mana(mana_cost)
            
            # Roll for success
            if random.random() < success_chance:
                # Success! Apply processing effects
                if processing_type == "refine":
                    # Refining improves quality
                    quality_improvement = 0.1 + (effective_skill * 0.01)
                    new_quality = min(2.0, instance.quality + quality_improvement)
                    instance.quality = round(new_quality, 2)
                    
                    result_message = f"You successfully refined the {material_data['name']}, improving its quality from {instance.quality-quality_improvement:.2f} to {instance.quality:.2f}."
                
                elif processing_type == "extract":
                    # Extraction creates special properties but reduces quantity
                    if not instance.has_special_properties:
                        instance.has_special_properties = True
                        instance.special_properties = self._generate_processing_properties(
                            material_data, "extract", effective_skill, instance.quality)
                    else:
                        # Enhance existing properties
                        new_properties = self._enhance_special_properties(
                            instance.special_properties, effective_skill)
                        instance.special_properties = new_properties
                    
                    # Reduce quantity (extraction consumes material)
                    instance.quantity = max(1, instance.quantity - 1)
                    
                    result_message = f"You successfully extracted essence from the {material_data['name']}, enhancing its magical properties."
                
                elif processing_type == "enchant":
                    # Enchanting adds magical properties but costs mana
                    if not instance.has_special_properties:
                        instance.has_special_properties = True
                        instance.special_properties = self._generate_processing_properties(
                            material_data, "enchant", effective_skill, instance.quality)
                    else:
                        # Add magical properties
                        new_properties = self._add_magical_properties(
                            instance.special_properties, effective_skill, magic_profile)
                        instance.special_properties = new_properties
                    
                    result_message = f"You successfully enchanted the {material_data['name']}, infusing it with magical energy."
                
                # Update the instance
                session.commit()
                
                return {
                    "success": True,
                    "processing_type": processing_type,
                    "material_name": material_data["name"],
                    "new_quality": instance.quality,
                    "has_special_properties": instance.has_special_properties,
                    "special_properties": instance.special_properties,
                    "quantity_remaining": instance.quantity,
                    "message": result_message
                }
            else:
                # Failure
                failure_message = f"You failed to {processing_type} the {material_data['name']}."
                
                # Check for material loss on failure
                material_loss_chance = 0.2 - (effective_skill * 0.01)
                material_loss_chance = max(0.0, min(0.2, material_loss_chance))
                
                if random.random() < material_loss_chance:
                    # Lost some material
                    lost_quantity = 1
                    instance.quantity = max(0, instance.quantity - lost_quantity)
                    
                    if instance.quantity <= 0:
                        # All material lost
                        session.delete(instance)
                        failure_message += f" Unfortunately, you lost all of the material in the process."
                    else:
                        # Some material lost
                        failure_message += f" Unfortunately, you lost {lost_quantity} unit(s) in the process."
                
                session.commit()
                
                return {
                    "success": False,
                    "processing_type": processing_type,
                    "material_name": material_data["name"],
                    "quantity_remaining": instance.quantity if instance.quantity > 0 else 0,
                    "message": failure_message
                }
            
        except Exception as e:
            logger.error(f"Error processing material: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def _generate_processing_properties(self, material_data: Dict[str, Any], 
                                    processing_type: str,
                                    skill_level: float,
                                    quality: float) -> Dict[str, Any]:
        """
        Generate properties for processed materials
        
        Args:
            material_data: Material data
            processing_type: Type of processing
            skill_level: Skill level used for processing
            quality: Quality of the material
            
        Returns:
            Generated special properties
        """
        properties = {}
        
        if processing_type == "refine":
            # Refining focuses on purity and stability
            properties["purity"] = round(0.5 + (quality * 0.2) + (skill_level * 0.02), 2)
            properties["stability"] = round(0.4 + (quality * 0.1) + (skill_level * 0.01), 2)
            
            # Chance for bonus property
            if random.random() < 0.3:
                properties["crafting_quality_bonus"] = round(0.1 + (quality * 0.05), 2)
        
        elif processing_type == "extract":
            # Extraction focuses on essence and potency
            properties["essence_concentration"] = round(0.4 + (quality * 0.3) + (skill_level * 0.02), 2)
            properties["magical_potency"] = round(0.3 + (quality * 0.2) + (skill_level * 0.01), 2)
            
            # Material affinity affects extraction
            if material_data.get("magical_affinity"):
                primary_affinity = material_data["magical_affinity"][0] if material_data["magical_affinity"] else None
                if primary_affinity:
                    properties[f"{primary_affinity.lower()}_essence"] = round(0.5 + (quality * 0.2), 2)
        
        elif processing_type == "enchant":
            # Enchanting focuses on magical properties
            properties["enchantability"] = round(0.5 + (quality * 0.2) + (skill_level * 0.02), 2)
            properties["magical_conductivity"] = round(0.4 + (quality * 0.1) + (skill_level * 0.01), 2)
            
            # Leyline resonance affects enchanting
            leyline_resonance = material_data.get("leyline_resonance", 1.0)
            if leyline_resonance > 1.0:
                properties["energy_storage"] = round(0.3 + (leyline_resonance * 0.1), 2)
        
        return properties
    
    def _enhance_special_properties(self, existing_properties: Dict[str, Any], 
                               skill_level: float) -> Dict[str, Any]:
        """
        Enhance existing special properties
        
        Args:
            existing_properties: Existing special properties
            skill_level: Skill level used for enhancement
            
        Returns:
            Enhanced special properties
        """
        enhanced_properties = existing_properties.copy()
        
        # Enhance numerical properties
        for key, value in enhanced_properties.items():
            if isinstance(value, (int, float)):
                # Increase by 10-30% based on skill
                increase_factor = 0.1 + (skill_level * 0.01)
                increase_factor = min(0.3, increase_factor)
                
                enhanced_properties[key] = round(value * (1.0 + increase_factor), 2)
        
        # Chance to add a new property
        if random.random() < 0.2:
            new_properties = [
                ("refinement_quality", round(0.3 + (skill_level * 0.02), 2)),
                ("material_efficiency", round(0.2 + (skill_level * 0.01), 2)),
                ("processing_bonus", round(0.3 + (skill_level * 0.015), 2))
            ]
            
            # Filter out existing properties
            new_properties = [p for p in new_properties if p[0] not in enhanced_properties]
            
            if new_properties:
                prop = random.choice(new_properties)
                enhanced_properties[prop[0]] = prop[1]
        
        return enhanced_properties
    
    def _add_magical_properties(self, existing_properties: Dict[str, Any], 
                           skill_level: float,
                           magic_profile: MagicUser) -> Dict[str, Any]:
        """
        Add magical properties to existing special properties
        
        Args:
            existing_properties: Existing special properties
            skill_level: Skill level used for enhancement
            magic_profile: Player's magic profile
            
        Returns:
            Enhanced special properties with added magical properties
        """
        enhanced_properties = existing_properties.copy()
        
        # Add magical energy storage
        if "magical_energy" not in enhanced_properties:
            magical_energy = 10 + (skill_level * 2) + (magic_profile.arcane_mastery * 3)
            enhanced_properties["magical_energy"] = round(magical_energy, 2)
        else:
            # Increase existing magical energy
            increase = 5 + (skill_level * 1) + (magic_profile.arcane_mastery * 2)
            enhanced_properties["magical_energy"] = round(enhanced_properties["magical_energy"] + increase, 2)
        
        # Add magical affinity based on caster's strengths
        if hasattr(magic_profile, "elemental_affinity") and magic_profile.elemental_affinity:
            affinity = magic_profile.elemental_affinity.lower()
            affinity_key = f"{affinity}_affinity"
            
            if affinity_key not in enhanced_properties:
                enhanced_properties[affinity_key] = round(0.3 + (magic_profile.arcane_mastery * 0.05), 2)
            else:
                # Increase existing affinity
                enhanced_properties[affinity_key] = round(
                    enhanced_properties[affinity_key] + (0.1 + (magic_profile.arcane_mastery * 0.02)), 2
                )
        
        # Chance to add special magical property
        if random.random() < 0.3:
            magical_properties = [
                ("spell_amplification", round(0.1 + (magic_profile.arcane_mastery * 0.03), 2)),
                ("mana_efficiency", round(0.1 + (magic_profile.arcane_mastery * 0.02), 2)),
                ("magical_stability", round(0.2 + (magic_profile.arcane_mastery * 0.02), 2)),
                ("enchantment_duration", round(0.1 + (magic_profile.arcane_mastery * 0.04), 2))
            ]
            
            # Filter out existing properties
            magical_properties = [p for p in magical_properties if p[0] not in enhanced_properties]
            
            if magical_properties:
                prop = random.choice(magical_properties)
                enhanced_properties[prop[0]] = prop[1]
        
        return enhanced_properties