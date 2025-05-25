"""
Magic Crafting Integration System

This module integrates the magic system with the crafting system, providing
a unified interface for magical materials, enchantments, and leyline-enhanced crafting.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import redis
import asyncio
from datetime import datetime

from .magic_system import MagicSystem, MagicUser
from .advanced_magic_features import (
    EnvironmentalMagicResonance, DomainMagicSynergy, SpellCraftingSystem
)
from .enchantment_service import EnchantmentService
from .magical_material_service import MagicalMaterialService
from .leyline_crafting_service import LeylineCraftingService

# Configure logging
logger = logging.getLogger(__name__)

# Redis client for caching frequently accessed data
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
    redis_available = True
except Exception as e:
    logger.warning(f"Redis not available for magic-crafting integration: {e}")
    redis_available = False


class MagicCraftingIntegration:
    """
    Main integration class that provides a unified interface for
    all magic-crafting related functionality.
    """
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the magic crafting integration
        
        Args:
            magic_system: The magic system instance
        """
        self.magic_system = magic_system
        
        # Initialize services
        self.enchantment_service = EnchantmentService(magic_system)
        self.material_service = MagicalMaterialService(magic_system)
        self.crafting_service = LeylineCraftingService(magic_system)
        
        # Initialize utility systems
        self.environmental_resonance = EnvironmentalMagicResonance()
        self.domain_synergy = DomainMagicSynergy()
        self.spell_crafting = SpellCraftingSystem(magic_system)
        
        # Performance tracking
        self.performance_metrics = {
            'enchantment_operations': 0,
            'material_operations': 0,
            'crafting_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    # ======================================================================
    # Enchantment Integration
    # ======================================================================
    
    def get_available_enchantments(self, player_id: str, magic_profile: MagicUser) -> List[Dict[str, Any]]:
        """
        Get enchantments available to a player based on their magic abilities
        
        Args:
            player_id: ID of the player
            magic_profile: Player's magic profile
            
        Returns:
            List of available enchantments with requirements met/not met
        """
        self.performance_metrics['enchantment_operations'] += 1
        return self.enchantment_service.get_available_enchantments(player_id, magic_profile)
    
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
        self.performance_metrics['enchantment_operations'] += 1
        return self.enchantment_service.apply_enchantment(player_id, item_id, enchantment_id, materials, location)
    
    def get_enchanted_items(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all enchanted items owned by a player
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of enchanted items
        """
        self.performance_metrics['enchantment_operations'] += 1
        return self.enchantment_service.get_enchanted_items(player_id)
    
    def use_enchanted_item_charge(self, item_id: str) -> Dict[str, Any]:
        """
        Use a charge from an enchanted item
        
        Args:
            item_id: ID of the enchanted item
            
        Returns:
            Result of using the charge
        """
        self.performance_metrics['enchantment_operations'] += 1
        return self.enchantment_service.use_enchanted_item_charge(item_id)
    
    # ======================================================================
    # Material Integration
    # ======================================================================
    
    def get_gathering_locations(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Get all gathering locations in a region
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of gathering locations
        """
        self.performance_metrics['material_operations'] += 1
        return self.material_service.get_gathering_locations_in_region(region_id)
    
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
        self.performance_metrics['material_operations'] += 1
        return self.material_service.discover_gathering_location(
            player_id, region_id, character_skills, magic_profile)
    
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
        self.performance_metrics['material_operations'] += 1
        return self.material_service.gather_materials(
            player_id, location_id, character_skills, magic_profile, tool_id)
    
    def get_player_materials(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all materials owned by a player
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of material instances
        """
        self.performance_metrics['material_operations'] += 1
        return self.material_service.get_player_materials(player_id)
    
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
        self.performance_metrics['material_operations'] += 1
        return self.material_service.process_material(
            player_id, instance_id, processing_type, character_skills, magic_profile)
    
    # ======================================================================
    # Crafting Integration
    # ======================================================================
    
    def get_crafting_stations(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Get all crafting stations in a region
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of crafting stations
        """
        self.performance_metrics['crafting_operations'] += 1
        return self.crafting_service.get_crafting_stations_in_region(region_id)
    
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
        self.performance_metrics['crafting_operations'] += 1
        return self.crafting_service.craft_item_with_magic(
            player_id, station_id, recipe_id, materials, magic_profile, character_skills)
    
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
        self.performance_metrics['crafting_operations'] += 1
        return self.crafting_service.create_crafting_station(
            name, location_id, station_type, leyline_strength)
    
    # ======================================================================
    # System Maintenance and Updates
    # ======================================================================
    
    def refresh_all_systems(self) -> Dict[str, Any]:
        """
        Refresh all magic-crafting systems
        Should be run periodically (e.g., daily)
        
        Returns:
            Status of the refresh operations
        """
        # Refresh gathering locations
        try:
            material_refresh = self.material_service.refresh_gathering_locations()
        except Exception as e:
            logger.error(f"Error refreshing gathering locations: {e}")
            material_refresh = {"success": False, "reason": str(e)}
        
        # Update leyline connections
        try:
            station_refresh = self.crafting_service.update_leyline_connections()
        except Exception as e:
            logger.error(f"Error updating leyline connections: {e}")
            station_refresh = {"success": False, "reason": str(e)}
        
        return {
            "success": material_refresh.get("success", False) and station_refresh.get("success", False),
            "material_refresh": material_refresh,
            "station_refresh": station_refresh
        }
    
    async def scheduled_refresh(self, interval_hours: int = 24):
        """
        Schedule regular refreshes of the magic-crafting systems
        
        Args:
            interval_hours: Interval between refreshes in hours
        """
        while True:
            # Perform refresh
            result = self.refresh_all_systems()
            
            # Log result
            if result.get("success", False):
                logger.info(f"Successfully refreshed magic-crafting systems")
            else:
                logger.warning(f"Failed to refresh some magic-crafting systems: {result}")
            
            # Wait for next refresh
            await asyncio.sleep(interval_hours * 3600)
    
    # ======================================================================
    # Utility Functions
    # ======================================================================
    
    def calculate_magical_bonus(self, location: Dict[str, Any], domain_type: str) -> float:
        """
        Calculate magical bonus for activities in a location
        
        Args:
            location: Location information
            domain_type: Type of activity (crafting, gathering, enchanting)
            
        Returns:
            Magical bonus (0.0-1.0)
        """
        # Create a dummy spell with the domain as its school
        dummy_spell = {
            "school": domain_type.upper()
        }
        
        # Use environmental resonance to calculate bonus
        modifier = self.environmental_resonance.calculate_spell_power_modifier(dummy_spell, location)
        
        # Convert to a 0.0-1.0 bonus
        return max(0.0, min(1.0, modifier - 1.0))
    
    def get_domain_bonus(self, character_domains: Dict[str, int], domain_type: str) -> float:
        """
        Calculate domain synergy bonus for crafting activities
        
        Args:
            character_domains: Character's domain levels
            domain_type: Type of activity (crafting, gathering, enchanting)
            
        Returns:
            Domain bonus (0.0-1.0)
        """
        # This would use the domain synergy system to calculate bonuses
        # For now, we'll use a simplified approach
        
        relevant_domains = {
            "crafting": ["CRAFT", "MIND", "SPIRIT"],
            "gathering": ["AWARENESS", "BODY", "MIND"],
            "enchanting": ["SPIRIT", "MIND", "CRAFT"]
        }
        
        domains = relevant_domains.get(domain_type.lower(), ["CRAFT"])
        
        # Calculate average of relevant domains
        total = 0
        count = 0
        
        for domain in domains:
            if domain in character_domains:
                total += character_domains[domain]
                count += 1
        
        avg_domain = total / count if count > 0 else 0
        
        # Convert to a 0.0-1.0 bonus
        return min(1.0, avg_domain * 0.05)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the integration
        
        Returns:
            Performance statistics
        """
        return {
            "enchantment_operations": self.performance_metrics['enchantment_operations'],
            "material_operations": self.performance_metrics['material_operations'],
            "crafting_operations": self.performance_metrics['crafting_operations'],
            "cache_hits": self.performance_metrics['cache_hits'],
            "cache_misses": self.performance_metrics['cache_misses'],
            "total_operations": (
                self.performance_metrics['enchantment_operations'] +
                self.performance_metrics['material_operations'] +
                self.performance_metrics['crafting_operations']
            ),
            "cache_hit_rate": (
                self.performance_metrics['cache_hits'] /
                (self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'])
                if (self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']) > 0
                else 0
            )
        }


# Create a global instance for easy import
def create_magic_crafting_integration(magic_system: MagicSystem) -> MagicCraftingIntegration:
    """
    Create a magic crafting integration instance
    
    Args:
        magic_system: The magic system instance
        
    Returns:
        Magic crafting integration instance
    """
    return MagicCraftingIntegration(magic_system)