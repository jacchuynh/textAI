"""
Enchantment Service for Magic-Crafting Integration
Handles applying magical enchantments to crafted items
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from .magic_crafting_models import Enchantment, EnchantedItem, MagicalMaterial, MagicalCraftingEvent
from .magic_system import MagicSystem, MagicUser
from .advanced_magic_features import DomainMagicSynergy, EnvironmentalMagicResonance
from ..db.database import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Cache for frequently accessed enchantments
enchantment_cache = {}

class EnchantmentService:
    """
    Service for applying enchantments to crafted items
    Integrates with the magic system for spell-like enchanting
    """
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the enchantment service
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
        self.domain_synergy = DomainMagicSynergy()
        self.environmental_resonance = EnvironmentalMagicResonance()
        
    def get_db_session(self) -> Session:
        """Get a database session"""
        return SessionLocal()
    
    def get_enchantment(self, enchantment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get enchantment data with caching
        
        Args:
            enchantment_id: ID of the enchantment
            
        Returns:
            Enchantment data or None if not found
        """
        # Check cache first
        if enchantment_id in enchantment_cache:
            return enchantment_cache[enchantment_id]
        
        # Query database
        session = self.get_db_session()
        try:
            enchantment = session.query(Enchantment).filter_by(id=enchantment_id).first()
            if not enchantment:
                return None
            
            # Convert to dictionary
            enchantment_data = {
                "id": enchantment.id,
                "name": enchantment.name,
                "description": enchantment.description,
                "tier": enchantment.tier,
                "magic_school": enchantment.magic_school,
                "compatible_item_types": enchantment.compatible_item_types,
                "min_mana_cost": enchantment.min_mana_cost,
                "min_arcane_mastery": enchantment.min_arcane_mastery,
                "required_materials": enchantment.required_materials,
                "effects": enchantment.effects,
                "duration_type": enchantment.duration_type,
                "max_charges": enchantment.max_charges,
                "base_success_chance": enchantment.base_success_chance,
                "complexity": enchantment.complexity
            }
            
            # Cache for 1 hour (enchantments rarely change)
            enchantment_cache[enchantment_id] = enchantment_data
            return enchantment_data
            
        finally:
            session.close()
    
    def get_available_enchantments(self, player_id: str, magic_profile: MagicUser) -> List[Dict[str, Any]]:
        """
        Get enchantments available to a player based on their magic abilities
        
        Args:
            player_id: ID of the player
            magic_profile: Player's magic profile
            
        Returns:
            List of available enchantments with requirements met/not met
        """
        session = self.get_db_session()
        try:
            # Get all enchantments
            enchantments = session.query(Enchantment).all()
            
            # Check requirements for each enchantment
            available_enchantments = []
            for enchantment in enchantments:
                requirements_met = True
                unmet_requirements = []
                
                # Check arcane mastery
                if enchantment.min_arcane_mastery > magic_profile.arcane_mastery:
                    requirements_met = False
                    unmet_requirements.append(f"Arcane Mastery: {magic_profile.arcane_mastery}/{enchantment.min_arcane_mastery}")
                
                # Check mana requirements
                if enchantment.min_mana_cost > magic_profile.mana_max:
                    requirements_met = False
                    unmet_requirements.append(f"Max Mana: {magic_profile.mana_max}/{enchantment.min_mana_cost}")
                
                # Convert to dictionary
                enchantment_data = {
                    "id": enchantment.id,
                    "name": enchantment.name,
                    "description": enchantment.description,
                    "tier": enchantment.tier,
                    "magic_school": enchantment.magic_school,
                    "compatible_item_types": enchantment.compatible_item_types,
                    "min_mana_cost": enchantment.min_mana_cost,
                    "required_materials": enchantment.required_materials,
                    "effects": enchantment.effects,
                    "duration_type": enchantment.duration_type,
                    "requirements_met": requirements_met,
                    "unmet_requirements": unmet_requirements if not requirements_met else []
                }
                
                available_enchantments.append(enchantment_data)
            
            return available_enchantments
            
        finally:
            session.close()
    
    def apply_enchantment(self, player_id: str, item_id: str, enchantment_id: str, 
                        materials: List[Dict[str, Any]], location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply an enchantment to a crafted item
        
        Args:
            player_id: ID of the player performing the enchantment
            item_id: ID of the item to enchant
            enchantment_id: ID of the enchantment to apply
            materials: List of materials being used
            location: Optional location data for environmental bonuses
            
        Returns:
            Result of the enchantment attempt
        """
        session = self.get_db_session()
        try:
            # Get player's magic profile
            magic_profile = self.magic_system.get_player_profile(player_id)
            if not magic_profile:
                return {"success": False, "reason": "Player magic profile not found"}
            
            # Get enchantment data
            enchantment_data = self.get_enchantment(enchantment_id)
            if not enchantment_data:
                return {"success": False, "reason": f"Enchantment {enchantment_id} not found"}
            
            # Check if player has enough mana
            if magic_profile.mana_current < enchantment_data["min_mana_cost"]:
                return {
                    "success": False, 
                    "reason": f"Insufficient mana ({magic_profile.mana_current}/{enchantment_data['min_mana_cost']})"
                }
            
            # Check arcane mastery requirement
            if magic_profile.arcane_mastery < enchantment_data["min_arcane_mastery"]:
                return {
                    "success": False, 
                    "reason": f"Insufficient arcane mastery ({magic_profile.arcane_mastery}/{enchantment_data['min_arcane_mastery']})"
                }
            
            # Check required materials
            required_materials = enchantment_data.get("required_materials", {})
            available_materials = {m["material_id"]: m for m in materials}
            
            for material_id, quantity in required_materials.items():
                if material_id not in available_materials:
                    return {"success": False, "reason": f"Missing required material: {material_id}"}
                
                if available_materials[material_id].get("quantity", 0) < quantity:
                    return {
                        "success": False, 
                        "reason": f"Insufficient {material_id} ({available_materials[material_id].get('quantity', 0)}/{quantity})"
                    }
            
            # Calculate material quality bonus
            material_quality_bonus = self._calculate_material_quality_bonus(materials, required_materials)
            
            # Calculate environmental bonus if location provided
            environmental_bonus = 0.0
            if location:
                environmental_bonus = self._calculate_environmental_bonus(location, enchantment_data["magic_school"])
            
            # Calculate domain synergy bonus if available
            domain_bonus = 0.0
            if hasattr(magic_profile, "domains"):
                character = {"domains": magic_profile.domains}
                domain_bonus = self.domain_synergy.calculate_synergy_bonus(character, {
                    "school": enchantment_data["magic_school"],
                    "tier": enchantment_data["tier"]
                })
            
            # Calculate base success chance
            base_chance = enchantment_data["base_success_chance"]
            
            # Apply bonuses
            success_chance = min(0.95, base_chance + 
                              (material_quality_bonus * 0.1) + 
                              (environmental_bonus * 0.05) +
                              (domain_bonus * 0.1) +
                              (magic_profile.arcane_mastery * 0.02))
            
            # Deduct mana cost
            mana_cost = enchantment_data["min_mana_cost"]
            magic_profile.use_mana(mana_cost)
            
            # Determine success
            success = random.random() < success_chance
            
            # Calculate enchantment quality if successful
            quality = 1.0
            if success:
                # Base quality based on success margin
                quality_base = 0.8 + ((success_chance - random.random()) * 0.4)
                
                # Add bonuses
                quality = min(2.0, quality_base + 
                           (material_quality_bonus * 0.2) + 
                           (environmental_bonus * 0.1) +
                           (domain_bonus * 0.1))
            
            # Create enchantment result data
            result_data = {
                "success": success,
                "quality": round(quality, 2) if success else 0,
                "mana_used": mana_cost,
                "materials_used": [
                    {"material_id": material_id, "quantity": qty}
                    for material_id, qty in required_materials.items()
                ]
            }
            
            # If successful, create enchanted item record
            if success:
                # Determine expiration or charges based on duration type
                charges_remaining = None
                expiration_date = None
                
                if enchantment_data["duration_type"] == "charges":
                    charges_remaining = enchantment_data["max_charges"]
                    # Quality affects max charges
                    if quality > 1.2:
                        charges_remaining = int(charges_remaining * quality)
                
                elif enchantment_data["duration_type"] == "temporary":
                    # Base duration is 1 day per tier
                    base_duration_days = enchantment_data["tier"]
                    # Quality affects duration
                    duration_days = base_duration_days * quality
                    expiration_date = datetime.utcnow() + timedelta(days=duration_days)
                
                # Generate custom properties based on quality
                custom_properties = self._generate_custom_properties(
                    enchantment_data, quality, material_quality_bonus)
                
                # Create enchanted item record
                enchanted_item = EnchantedItem(
                    item_id=item_id,
                    item_type=enchantment_data["compatible_item_types"][0] if enchantment_data["compatible_item_types"] else "generic",
                    owner_id=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                    enchantment_id=enchantment_id,
                    quality=quality,
                    charges_remaining=charges_remaining,
                    expiration_date=expiration_date,
                    enchanted_by=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                    custom_properties=custom_properties
                )
                
                session.add(enchanted_item)
                
                # Add the enchantment details to the result
                result_data["enchanted_item"] = {
                    "id": str(enchanted_item.id),
                    "enchantment_id": enchantment_id,
                    "enchantment_name": enchantment_data["name"],
                    "quality": quality,
                    "charges_remaining": charges_remaining,
                    "expiration_date": expiration_date.isoformat() if expiration_date else None,
                    "custom_properties": custom_properties
                }
            
            # Log the enchantment event
            event_data = {
                "enchantment_id": enchantment_id,
                "item_id": item_id,
                "success": success,
                "quality": quality if success else 0,
                "material_quality_bonus": material_quality_bonus,
                "environmental_bonus": environmental_bonus,
                "domain_bonus": domain_bonus,
                "success_chance": success_chance,
                "materials_used": [
                    {"material_id": material_id, "quantity": qty}
                    for material_id, qty in required_materials.items()
                ]
            }
            
            leyline_influence = 0.0
            if location and location.get("leyline_strength"):
                leyline_influence = location.get("leyline_strength", 1.0)
            
            magic_event = MagicalCraftingEvent(
                player_id=uuid.UUID(player_id) if isinstance(player_id, str) else player_id,
                event_type="enchant",
                item_id=item_id,
                enchantment_id=enchantment_id,
                location_id=location.get("id") if location else None,
                event_data=event_data,
                success=success,
                mana_cost=mana_cost,
                leyline_influence=leyline_influence
            )
            
            session.add(magic_event)
            session.commit()
            
            # Return the result
            return result_data
            
        except Exception as e:
            logger.error(f"Error applying enchantment: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def _calculate_material_quality_bonus(self, 
                                     materials: List[Dict[str, Any]], 
                                     required_materials: Dict[str, int]) -> float:
        """
        Calculate quality bonus from materials
        
        Args:
            materials: List of materials being used
            required_materials: Required materials for the enchantment
            
        Returns:
            Quality bonus (0.0-1.0)
        """
        if not materials:
            return 0.0
        
        # Calculate weighted average quality
        total_quality = 0.0
        total_weight = 0
        
        for material in materials:
            material_id = material.get("material_id")
            if material_id in required_materials:
                quality = material.get("quality", 1.0)
                quantity = material.get("quantity", 0)
                required_quantity = required_materials[material_id]
                
                # Only count up to the required quantity
                used_quantity = min(quantity, required_quantity)
                
                total_quality += quality * used_quantity
                total_weight += used_quantity
        
        if total_weight == 0:
            return 0.0
        
        avg_quality = total_quality / total_weight
        
        # Convert to bonus (1.0 is normal, 2.0 is max quality)
        # This gives a bonus from 0.0 to 1.0
        return max(0.0, min(1.0, avg_quality - 1.0))
    
    def _calculate_environmental_bonus(self, location: Dict[str, Any], magic_school: str) -> float:
        """
        Calculate environmental bonus for enchanting
        
        Args:
            location: Location data
            magic_school: Magic school of the enchantment
            
        Returns:
            Environmental bonus (0.0-1.0)
        """
        # Create a dummy spell with the right school for environmental resonance
        dummy_spell = {
            "school": magic_school
        }
        
        # Use the environmental resonance system
        modifier = self.environmental_resonance.calculate_spell_power_modifier(dummy_spell, location)
        
        # Convert to a 0.0-1.0 bonus (1.0 modifier is normal, 2.0 is maximum)
        return max(0.0, min(1.0, modifier - 1.0))
    
    def _generate_custom_properties(self, 
                               enchantment_data: Dict[str, Any], 
                               quality: float,
                               material_quality: float) -> Dict[str, Any]:
        """
        Generate custom properties for an enchanted item based on quality
        
        Args:
            enchantment_data: Enchantment data
            quality: Quality of the enchantment (0.5-2.0)
            material_quality: Material quality bonus (0.0-1.0)
            
        Returns:
            Custom properties for the enchanted item
        """
        custom_properties = {}
        
        # Base effects from the enchantment
        base_effects = enchantment_data.get("effects", {})
        
        # Scale numeric effects by quality
        for effect_name, effect_value in base_effects.items():
            if isinstance(effect_value, (int, float)):
                scaled_value = effect_value * quality
                custom_properties[effect_name] = scaled_value
            else:
                custom_properties[effect_name] = effect_value
        
        # Chance for bonus property based on quality and material quality
        bonus_chance = (quality - 1.0) * 0.5 + material_quality * 0.3
        
        if random.random() < bonus_chance:
            # Add a bonus property
            tier = enchantment_data["tier"]
            potential_bonuses = self._get_potential_bonuses(enchantment_data["magic_school"], tier)
            
            if potential_bonuses:
                bonus_property = random.choice(potential_bonuses)
                custom_properties[bonus_property["name"]] = bonus_property["value"]
        
        return custom_properties
    
    def _get_potential_bonuses(self, magic_school: str, tier: int) -> List[Dict[str, Any]]:
        """
        Get potential bonus properties based on magic school and tier
        
        Args:
            magic_school: Magic school of the enchantment
            tier: Tier of the enchantment
            
        Returns:
            List of potential bonus properties
        """
        # School-specific bonuses
        school_bonuses = {
            "evocation": [
                {"name": "critical_chance_bonus", "value": 0.05 * tier},
                {"name": "damage_bonus", "value": 2 * tier},
                {"name": "element_resistance", "value": 0.1 * tier}
            ],
            "abjuration": [
                {"name": "damage_reduction", "value": 0.05 * tier},
                {"name": "ward_strength_bonus", "value": 0.1 * tier},
                {"name": "magic_resistance", "value": 0.05 * tier}
            ],
            "restoration": [
                {"name": "healing_bonus", "value": 0.1 * tier},
                {"name": "health_regeneration", "value": 0.5 * tier},
                {"name": "stamina_recovery", "value": 1 * tier}
            ],
            "divination": [
                {"name": "detection_range_bonus", "value": 5 * tier},
                {"name": "trap_detection_chance", "value": 0.1 * tier},
                {"name": "initiative_bonus", "value": 1 * tier}
            ],
            "transmutation": [
                {"name": "crafting_quality_bonus", "value": 0.05 * tier},
                {"name": "weight_reduction", "value": 0.1 * tier},
                {"name": "durability_bonus", "value": 0.2 * tier}
            ],
            "enchantment": [
                {"name": "persuasion_bonus", "value": 0.1 * tier},
                {"name": "mental_resistance", "value": 0.1 * tier},
                {"name": "charm_power_bonus", "value": 0.1 * tier}
            ],
            "illusion": [
                {"name": "stealth_bonus", "value": 0.1 * tier},
                {"name": "invisibility_duration", "value": 10 * tier},
                {"name": "illusion_power_bonus", "value": 0.1 * tier}
            ],
            "conjuration": [
                {"name": "summon_duration_bonus", "value": 0.2 * tier},
                {"name": "summon_strength_bonus", "value": 0.1 * tier},
                {"name": "teleport_distance_bonus", "value": 5 * tier}
            ],
            "necromancy": [
                {"name": "undead_control_bonus", "value": 1 * tier},
                {"name": "life_drain_power", "value": 0.1 * tier},
                {"name": "fear_aura_strength", "value": 0.05 * tier}
            ]
        }
        
        # Generic bonuses available to all schools
        generic_bonuses = [
            {"name": "mana_cost_reduction", "value": 0.05 * tier},
            {"name": "casting_speed_bonus", "value": 0.05 * tier},
            {"name": "spell_duration_bonus", "value": 0.1 * tier}
        ]
        
        # Combine school-specific and generic bonuses
        magic_school = magic_school.lower()
        all_bonuses = school_bonuses.get(magic_school, []) + generic_bonuses
        
        return all_bonuses
    
    def get_enchanted_items(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all enchanted items owned by a player
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of enchanted items
        """
        session = self.get_db_session()
        try:
            # Convert player_id to UUID if needed
            player_uuid = uuid.UUID(player_id) if isinstance(player_id, str) else player_id
            
            # Query enchanted items
            enchanted_items = session.query(EnchantedItem).filter_by(owner_id=player_uuid).all()
            
            # Convert to dictionaries
            items_data = []
            for item in enchanted_items:
                enchantment_data = self.get_enchantment(item.enchantment_id)
                
                item_data = {
                    "id": str(item.id),
                    "item_id": item.item_id,
                    "item_type": item.item_type,
                    "enchantment_id": item.enchantment_id,
                    "enchantment_name": enchantment_data["name"] if enchantment_data else "Unknown Enchantment",
                    "quality": item.quality,
                    "charges_remaining": item.charges_remaining,
                    "is_expired": item.expiration_date is not None and item.expiration_date < datetime.utcnow(),
                    "expiration_date": item.expiration_date.isoformat() if item.expiration_date else None,
                    "enchanted_at": item.enchanted_at.isoformat(),
                    "custom_properties": item.custom_properties
                }
                
                items_data.append(item_data)
            
            return items_data
            
        finally:
            session.close()
    
    def use_enchanted_item_charge(self, item_id: str) -> Dict[str, Any]:
        """
        Use a charge from an enchanted item
        
        Args:
            item_id: ID of the enchanted item
            
        Returns:
            Result of using the charge
        """
        session = self.get_db_session()
        try:
            # Convert to UUID if needed
            item_uuid = uuid.UUID(item_id) if isinstance(item_id, str) else item_id
            
            # Query the enchanted item
            enchanted_item = session.query(EnchantedItem).filter_by(id=item_uuid).first()
            if not enchanted_item:
                return {"success": False, "reason": "Enchanted item not found"}
            
            # Check if the item uses charges
            if enchanted_item.charges_remaining is None:
                return {"success": False, "reason": "This enchantment does not use charges"}
            
            # Check if there are charges remaining
            if enchanted_item.charges_remaining <= 0:
                return {"success": False, "reason": "No charges remaining"}
            
            # Use a charge
            enchanted_item.charges_remaining -= 1
            
            # Check if this was the last charge
            is_depleted = enchanted_item.charges_remaining <= 0
            
            # If depleted, mark for later cleanup or remove immediately
            if is_depleted:
                # Option 1: Remove immediately
                # session.delete(enchanted_item)
                
                # Option 2: Mark as depleted but keep record
                enchanted_item.charges_remaining = 0
            
            session.commit()
            
            return {
                "success": True,
                "charges_remaining": enchanted_item.charges_remaining,
                "is_depleted": is_depleted
            }
            
        except Exception as e:
            logger.error(f"Error using enchanted item charge: {e}")
            session.rollback()
            return {"success": False, "reason": str(e)}
            
        finally:
            session.close()
    
    def get_enchantment_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about enchantments
        
        Returns:
            Enchantment statistics
        """
        session = self.get_db_session()
        try:
            # Get most popular enchantments
            popular_enchantments = session.query(
                MagicalCraftingEvent.enchantment_id,
                func.count(MagicalCraftingEvent.id).label('usage_count'),
                func.avg(MagicalCraftingEvent.event_data['quality'].astext.cast(Float)).label('avg_quality')
            ).filter(
                MagicalCraftingEvent.event_type == 'enchant',
                MagicalCraftingEvent.success == True
            ).group_by(
                MagicalCraftingEvent.enchantment_id
            ).order_by(
                func.count(MagicalCraftingEvent.id).desc()
            ).limit(10).all()
            
            # Get success rates by tier
            tier_success_rates = session.query(
                Enchantment.tier,
                func.count(MagicalCraftingEvent.id).label('attempt_count'),
                func.sum(func.cast(MagicalCraftingEvent.success, Integer)).label('success_count')
            ).join(
                MagicalCraftingEvent, 
                MagicalCraftingEvent.enchantment_id == Enchantment.id
            ).filter(
                MagicalCraftingEvent.event_type == 'enchant'
            ).group_by(
                Enchantment.tier
            ).all()
            
            # Format results
            popular_data = [
                {
                    "enchantment_id": e[0],
                    "usage_count": e[1],
                    "avg_quality": float(e[2]) if e[2] is not None else 0.0
                }
                for e in popular_enchantments
            ]
            
            tier_data = [
                {
                    "tier": t[0],
                    "attempt_count": t[1],
                    "success_count": t[2],
                    "success_rate": float(t[2]) / t[1] if t[1] > 0 else 0.0
                }
                for t in tier_success_rates
            ]
            
            return {
                "popular_enchantments": popular_data,
                "tier_success_rates": tier_data
            }
            
        finally:
            session.close()