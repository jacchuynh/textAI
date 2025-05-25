
"""
Base Generator - Abstract base class for location detail generators

This module provides the foundation for all location-specific generators,
defining the interface and common functionality for generating detailed
content for different types of POIs.
"""

import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from world_model import (
    DBPointOfInterest, DBGeneratedLocationDetails, DBBiome,
    POIType, RACIAL_CHARACTERISTICS, MAJOR_CITIES
)

logger = logging.getLogger(__name__)

class BaseLocationGenerator(ABC):
    """
    Abstract base class for all location generators.
    
    Each POI type (village, ruin, cave, etc.) should have its own generator
    that inherits from this class and implements the abstract methods.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Common generation templates and data
        self.atmosphere_descriptors = {
            "peaceful": ["tranquil", "serene", "calm", "harmonious", "restful"],
            "dangerous": ["ominous", "threatening", "foreboding", "perilous", "hostile"],
            "mysterious": ["enigmatic", "arcane", "cryptic", "puzzling", "secretive"],
            "bustling": ["busy", "active", "lively", "vibrant", "energetic"],
            "ancient": ["timeless", "weathered", "venerable", "primordial", "eternal"],
            "magical": ["enchanted", "mystical", "otherworldly", "supernatural", "ethereal"]
        }
        
        # Common materials and architectural elements by racial influence
        self.racial_architecture = {
            "human": {
                "materials": ["timber", "stone", "brick", "thatch"],
                "features": ["peaked_roofs", "large_windows", "central_squares", "practical_layouts"],
                "decorations": ["banners", "carved_lintels", "painted_shutters"]
            },
            "elf": {
                "materials": ["living_wood", "crystal", "mithril", "enchanted_stone"],
                "features": ["flowing_lines", "integrated_nature", "spiraling_towers", "organic_shapes"],
                "decorations": ["rune_carvings", "growing_vines", "crystal_inlays", "starlight_windows"]
            },
            "dwarf": {
                "materials": ["granite", "iron", "steel", "precious_metals"],
                "features": ["massive_blocks", "underground_chambers", "reinforced_doors", "geometric_patterns"],
                "decorations": ["clan_symbols", "metalwork", "gem_inlays", "ancestral_murals"]
            },
            "beastfolk": {
                "materials": ["bone", "hide", "woven_reeds", "carved_wood"],
                "features": ["circular_dwellings", "elevated_platforms", "communal_spaces", "natural_camouflage"],
                "decorations": ["totem_poles", "ritual_circles", "spirit_masks", "clan_markings"]
            },
            "orc": {
                "materials": ["rough_stone", "salvaged_metal", "reinforced_timber", "practical_materials"],
                "features": ["fortress_like", "thick_walls", "defensive_positions", "communal_workshops"],
                "decorations": ["honor_banners", "weapon_displays", "strength_symbols", "practical_art"]
            },
            "ferverl": {
                "materials": ["desert_stone", "crystalline_sand", "mana_infused_glass", "purified_metals"],
                "features": ["heat_resistant", "ritual_chambers", "purification_pools", "geometric_precision"],
                "decorations": ["ritual_symbols", "purification_runes", "memory_crystals", "honor_scars"]
            }
        }
    
    @abstractmethod
    def generate_location_details(
        self,
        db: Session,
        poi: DBPointOfInterest,
        generation_context: Optional[Dict[str, Any]] = None
    ) -> DBGeneratedLocationDetails:
        """
        Generate detailed content for a specific POI.
        
        Args:
            db: Database session
            poi: The POI to generate details for
            generation_context: Additional context for generation
            
        Returns:
            Generated location details object
        """
        pass
    
    def get_biome_context(self, db: Session, poi: DBPointOfInterest) -> Dict[str, Any]:
        """
        Get contextual information about the POI's biome for generation.
        """
        biome = db.query(DBBiome).filter(DBBiome.id == poi.biome_id).first()
        if not biome:
            return {}
        
        return {
            "biome": biome,
            "biome_type": biome.biome_type,
            "flora_fauna": biome.flora_fauna or [],
            "atmospheric_tags": biome.atmospheric_tags or [],
            "hazards": biome.hazards or [],
            "resources": biome.available_resources or {},
            "magical_phenomena": biome.magical_phenomena or [],
            "leyline_intensity": biome.leyline_intensity
        }
    
    def determine_racial_influence(
        self,
        biome_context: Dict[str, Any],
        poi: DBPointOfInterest
    ) -> Tuple[str, float]:
        """
        Determine which race has the most influence in this location.
        
        Returns:
            Tuple of (dominant_race, influence_strength)
        """
        biome = biome_context.get("biome")
        if not biome or not biome.region:
            return "human", 0.5  # Default fallback
        
        # Check if we're near any major cities and their racial influence
        region = biome.region
        regional_races = getattr(region, 'dominant_races', []) or []
        
        if not regional_races:
            # Fallback to biome-based racial preferences
            biome_type = biome_context.get("biome_type", "")
            if "desert" in biome_type.lower():
                return "ferverl", 0.7
            elif "forest" in biome_type.lower() or "wood" in biome_type.lower():
                return "elf", 0.7
            elif "mountain" in biome_type.lower() or "highland" in biome_type.lower():
                return "dwarf", 0.7
            elif "wild" in biome_type.lower() or "frontier" in biome_type.lower():
                return "beastfolk", 0.6
            else:
                return "human", 0.6
        
        # Select from regional dominant races with some randomness
        primary_race = random.choice(regional_races)
        influence_strength = random.uniform(0.6, 0.9)
        
        return primary_race, influence_strength
    
    def generate_base_description(
        self,
        poi: DBPointOfInterest,
        biome_context: Dict[str, Any],
        racial_influence: Tuple[str, float]
    ) -> str:
        """
        Generate a base environmental description for the location.
        """
        dominant_race, influence_strength = racial_influence
        biome_type = biome_context.get("biome_type", "unknown")
        
        # Get atmospheric descriptors
        atmospheric_tags = biome_context.get("atmospheric_tags", [])
        if atmospheric_tags:
            primary_atmosphere = random.choice(atmospheric_tags)
            atmosphere_words = self.atmosphere_descriptors.get(
                primary_atmosphere, ["unremarkable", "ordinary"]
            )
            atmosphere_desc = random.choice(atmosphere_words)
        else:
            atmosphere_desc = "quiet"
        
        # Get geographical context from location tags
        location_tags = poi.relative_location_tags or []
        geographical_context = ""
        
        for tag in location_tags:
            if "river" in tag:
                geographical_context = "beside a gently flowing river"
                break
            elif "hilltop" in tag:
                geographical_context = "atop a rolling hill"
                break
            elif "valley" in tag:
                geographical_context = "nestled in a sheltered valley"
                break
            elif "forest" in tag:
                geographical_context = "at the edge of ancient woodlands"
                break
            elif "crossroads" in tag:
                geographical_context = "where several paths converge"
                break
        
        if not geographical_context:
            geographical_context = "in the midst of the surrounding landscape"
        
        # Build base description
        description_parts = [
            f"The {atmosphere_desc} {poi.poi_type.replace('_', ' ')} of {poi.generated_name}",
            f"sits {geographical_context}."
        ]
        
        # Add racial architectural influence if significant
        if influence_strength > 0.6:
            race_data = self.racial_architecture.get(dominant_race, {})
            if race_data:
                materials = race_data.get("materials", [])
                features = race_data.get("features", [])
                
                if materials and features:
                    material = random.choice(materials)
                    feature = random.choice(features).replace("_", " ")
                    description_parts.append(
                        f"The {dominant_race} influence is evident in the {material} construction and {feature}."
                    )
        
        return " ".join(description_parts)
    
    def generate_environmental_details(
        self,
        biome_context: Dict[str, Any],
        poi: DBPointOfInterest
    ) -> List[str]:
        """
        Generate environmental features and details.
        """
        details = []
        
        # Add flora/fauna if available
        flora_fauna = biome_context.get("flora_fauna", [])
        if flora_fauna:
            selected_life = random.sample(flora_fauna, min(2, len(flora_fauna)))
            for life_form in selected_life:
                details.append(f"Local {life_form.replace('_', ' ')} can be observed in the area")
        
        # Add magical phenomena if present
        magical_phenomena = biome_context.get("magical_phenomena", [])
        if magical_phenomena and random.random() < 0.4:  # 40% chance
            phenomenon = random.choice(magical_phenomena)
            details.append(f"The area exhibits {phenomenon.replace('_', ' ')}")
        
        # Add hazard hints if dangerous
        hazards = biome_context.get("hazards", [])
        if hazards and random.random() < 0.3:  # 30% chance
            hazard = random.choice(hazards)
            details.append(f"Signs of {hazard.replace('_', ' ')} serve as a subtle warning")
        
        # Add leyline information if intense
        leyline_intensity = biome_context.get("leyline_intensity", 1.0)
        if leyline_intensity > 2.0:
            details.append("The air hums with barely contained magical energy")
        elif leyline_intensity > 1.5:
            details.append("A faint magical resonance can be felt by those sensitive to such things")
        
        return details
    
    def generate_resource_opportunities(
        self,
        biome_context: Dict[str, Any],
        poi_type: POIType
    ) -> List[Dict[str, Any]]:
        """
        Generate potential resources or items that might be found here.
        """
        resources = []
        available_resources = biome_context.get("resources", {})
        
        for resource_type, availability in available_resources.items():
            if random.random() < availability * 0.5:  # Reduce chance for balance
                resource_info = {
                    "name": resource_type.replace("_", " ").title(),
                    "type": resource_type,
                    "availability": availability,
                    "description": f"Small quantities of {resource_type.replace('_', ' ')} might be gathered here"
                }
                resources.append(resource_info)
        
        return resources
    
    def generate_quest_hooks(
        self,
        poi: DBPointOfInterest,
        biome_context: Dict[str, Any],
        racial_influence: Tuple[str, float]
    ) -> List[str]:
        """
        Generate potential quest hooks and adventure opportunities.
        """
        hooks = []
        dominant_race, influence_strength = racial_influence
        
        # Generic hooks based on POI type
        generic_hooks = {
            POIType.VILLAGE: [
                "Local livestock have been disappearing mysteriously",
                "An important trade caravan is overdue",
                "Strange lights have been seen in the nearby wilderness",
                "The local well has started producing odd-tasting water"
            ],
            POIType.RUIN: [
                "Ancient texts mention a hidden chamber within these ruins",
                "Valuable relics might still be buried in the rubble",
                "Local legends speak of a guardian that still protects this place",
                "Recent disturbances suggest someone else has been exploring here"
            ],
            POIType.CAVE: [
                "Deep tunnels might connect to other cave systems",
                "Mineral veins could contain valuable ores",
                "Strange echoes suggest the caves are deeper than they appear",
                "Local wildlife seems to avoid this particular cave"
            ],
            POIType.SHRINE: [
                "The shrine's blessing has weakened and needs restoration",
                "Pilgrims have reported strange visions here",
                "Sacred artifacts may have been disturbed",
                "The shrine holds clues to ancient mysteries"
            ]
        }
        
        # Add generic hooks
        poi_type = POIType(poi.poi_type)
        if poi_type in generic_hooks:
            hooks.extend(random.sample(generic_hooks[poi_type], min(2, len(generic_hooks[poi_type]))))
        
        # Add race-specific hooks if influence is strong
        if influence_strength > 0.7:
            race_specific_hooks = {
                "elf": [
                    "Ancient elven magic still lingers here",
                    "This place holds significance in elven lore",
                    "Elven refugees from the Crimson Dissonance may have hidden something here"
                ],
                "dwarf": [
                    "Dwarven craftsmanship suggests hidden mechanisms",
                    "This site might connect to old dwarven trade routes",
                    "Ancient dwarven runes hint at buried treasures"
                ],
                "beastfolk": [
                    "Spirit totems indicate this is sacred to local clans",
                    "Animal behavior suggests supernatural presence",
                    "Tribal markings tell a story of ancient conflicts"
                ],
                "ferverl": [
                    "Mana distortions from the Crimson Dissonance affect this area",
                    "Ferverl purification rituals may be needed here",
                    "This place might hold relics from the war-torn era"
                ]
            }
            
            if dominant_race in race_specific_hooks:
                race_hooks = race_specific_hooks[dominant_race]
                hooks.extend(random.sample(race_hooks, min(1, len(race_hooks))))
        
        return hooks
    
    def save_generated_details(
        self,
        db: Session,
        poi: DBPointOfInterest,
        details_data: Dict[str, Any]
    ) -> DBGeneratedLocationDetails:
        """
        Save the generated location details to the database.
        """
        try:
            details = DBGeneratedLocationDetails(
                point_of_interest_id=poi.id,
                description=details_data.get("description", ""),
                detailed_features=details_data.get("detailed_features", []),
                generated_npcs=details_data.get("generated_npcs", []),
                local_issues=details_data.get("local_issues", []),
                available_services=details_data.get("available_services", []),
                unique_items=details_data.get("unique_items", []),
                quest_hooks=details_data.get("quest_hooks", []),
                hidden_secrets=details_data.get("hidden_secrets", []),
                local_economy=details_data.get("local_economy", {}),
                generation_prompt=details_data.get("generation_prompt", "")
            )
            
            db.add(details)
            
            # Mark POI as having generated details
            poi.details_generated = True
            
            db.commit()
            
            self.logger.info(f"Successfully saved details for {poi.generated_name}")
            return details
            
        except Exception as e:
            self.logger.error(f"Error saving location details: {e}")
            db.rollback()
            raise
    
    def get_generation_prompt(
        self,
        poi: DBPointOfInterest,
        biome_context: Dict[str, Any],
        racial_influence: Tuple[str, float]
    ) -> str:
        """
        Generate a prompt that could be used with an AI service for additional content.
        """
        dominant_race, influence_strength = racial_influence
        biome_type = biome_context.get("biome_type", "unknown")
        
        prompt_parts = [
            f"Generate detailed content for {poi.generated_name}, a {poi.poi_type.replace('_', ' ')}",
            f"located in a {biome_type.replace('_', ' ')} biome.",
            f"The location shows {dominant_race} cultural influence",
            f"with {influence_strength:.1%} strength.",
            f"Include specific NPCs, local customs, current issues, and hidden secrets.",
            f"Keep the tone consistent with a post-war fantasy world",
            f"where peace is maintained by the Crimson Accord."
        ]
        
        # Add location-specific context
        location_tags = poi.relative_location_tags or []
        if location_tags:
            prompt_parts.append(f"Consider the location's characteristics: {', '.join(location_tags)}.")
        
        return " ".join(prompt_parts)
