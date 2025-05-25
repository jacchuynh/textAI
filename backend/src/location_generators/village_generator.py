
"""
Village Generator - Specialized generator for village and settlement POIs

This module generates detailed content for village-type locations, including
NPCs, local economy, services, and community dynamics.
"""

import random
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from .base_generator import BaseLocationGenerator
from world_generation.world_model import (
    DBPointOfInterest, DBGeneratedLocationDetails,
    POIType, RACIAL_CHARACTERISTICS
)

class VillageGenerator(BaseLocationGenerator):
    """
    Generator specialized for creating detailed village and settlement content.
    """
    
    def __init__(self):
        super().__init__()
        
        # Village-specific data
        self.village_types = {
            "farming": {
                "primary_activities": ["agriculture", "livestock", "food_processing"],
                "typical_buildings": ["barn", "mill", "granary", "farmhouse"],
                "common_services": ["general_store", "blacksmith", "tavern"],
                "population_range": (15, 60),
                "wealth_level": "modest"
            },
            "trading": {
                "primary_activities": ["commerce", "transportation", "hospitality"],
                "typical_buildings": ["inn", "warehouse", "stable", "marketplace"],
                "common_services": ["inn", "general_store", "caravan_services", "money_changer"],
                "population_range": (25, 80),
                "wealth_level": "comfortable"
            },
            "mining": {
                "primary_activities": ["mining", "metalworking", "gem_cutting"],
                "typical_buildings": ["mine_office", "smelter", "workers_quarters", "tool_shop"],
                "common_services": ["equipment_supplier", "assayer", "tavern"],
                "population_range": (20, 70),
                "wealth_level": "variable"
            },
            "fishing": {
                "primary_activities": ["fishing", "boat_building", "net_making"],
                "typical_buildings": ["dock", "smokehouse", "boat_shed", "fisherman_hut"],
                "common_services": ["fish_market", "boat_repair", "tavern"],
                "population_range": (10, 45),
                "wealth_level": "modest"
            },
            "frontier": {
                "primary_activities": ["hunting", "trapping", "foraging", "defense"],
                "typical_buildings": ["palisade", "watchtower", "hunter_lodge", "storage_pit"],
                "common_services": ["general_supplies", "weaponsmith", "guide_services"],
                "population_range": (8, 30),
                "wealth_level": "poor"
            }
        }
        
        # NPC role templates by village type
        self.npc_roles = {
            "farming": [
                {"role": "village_elder", "importance": "high", "count": 1},
                {"role": "farmer", "importance": "medium", "count": (3, 8)},
                {"role": "miller", "importance": "medium", "count": 1},
                {"role": "blacksmith", "importance": "medium", "count": 1},
                {"role": "innkeeper", "importance": "medium", "count": 1},
                {"role": "merchant", "importance": "low", "count": (1, 2)},
                {"role": "laborer", "importance": "low", "count": (2, 6)}
            ],
            "trading": [
                {"role": "trade_master", "importance": "high", "count": 1},
                {"role": "innkeeper", "importance": "high", "count": 1},
                {"role": "caravan_guide", "importance": "medium", "count": (2, 4)},
                {"role": "merchant", "importance": "medium", "count": (3, 6)},
                {"role": "stable_master", "importance": "medium", "count": 1},
                {"role": "guard", "importance": "medium", "count": (2, 5)},
                {"role": "scribe", "importance": "low", "count": 1}
            ],
            "mining": [
                {"role": "mine_foreman", "importance": "high", "count": 1},
                {"role": "miner", "importance": "medium", "count": (4, 12)},
                {"role": "smelter", "importance": "medium", "count": (1, 2)},
                {"role": "safety_inspector", "importance": "medium", "count": 1},
                {"role": "equipment_smith", "importance": "medium", "count": 1},
                {"role": "assayer", "importance": "low", "count": 1},
                {"role": "camp_cook", "importance": "low", "count": 1}
            ]
        }
        
        # Common village issues and local problems
        self.village_issues = {
            "economic": [
                "Recent trade disruptions have affected local prosperity",
                "Competition from nearby settlements is hurting business",
                "Valuable resources are becoming harder to find",
                "Bandits have been targeting merchant caravans"
            ],
            "social": [
                "Generational conflicts between elders and youth",
                "Disputes over land ownership and usage rights", 
                "Cultural tensions between different racial groups",
                "A charismatic outsider is causing division in the community"
            ],
            "environmental": [
                "Unusual weather patterns are affecting local activities",
                "Wildlife behavior has changed, causing problems",
                "Water sources are becoming contaminated or scarce",
                "Strange magical phenomena are manifesting nearby"
            ],
            "security": [
                "Increased monster activity in the surrounding area",
                "Mysterious disappearances have the village on edge",
                "Bandits or raiders have been spotted in the region",
                "Ancient ruins nearby are showing signs of activity"
            ]
        }
    
    def generate_location_details(
        self,
        db: Session,
        poi: DBPointOfInterest,
        generation_context: Optional[Dict[str, Any]] = None
    ) -> DBGeneratedLocationDetails:
        """
        Generate detailed content for a village POI.
        """
        self.logger.info(f"Generating village details for {poi.generated_name}")
        
        # Get biome and racial context
        biome_context = self.get_biome_context(db, poi)
        racial_influence = self.determine_racial_influence(biome_context, poi)
        
        # Determine village type based on biome and context
        village_type = self._determine_village_type(biome_context, poi, racial_influence)
        village_data = self.village_types[village_type]
        
        # Generate base description
        description = self._generate_village_description(
            poi, biome_context, racial_influence, village_type, village_data
        )
        
        # Generate detailed features
        detailed_features = self._generate_village_features(
            village_data, biome_context, racial_influence
        )
        
        # Generate NPCs
        generated_npcs = self._generate_village_npcs(
            village_type, village_data, racial_influence, poi
        )
        
        # Generate local issues
        local_issues = self._generate_village_issues(village_type, biome_context)
        
        # Generate services
        available_services = self._generate_village_services(village_data, generated_npcs)
        
        # Generate unique items/resources
        unique_items = self.generate_resource_opportunities(biome_context, POIType.VILLAGE)
        
        # Generate quest hooks
        quest_hooks = self._generate_village_quest_hooks(
            poi, village_type, local_issues, generated_npcs
        )
        
        # Generate hidden secrets
        hidden_secrets = self._generate_village_secrets(village_type, biome_context, racial_influence)
        
        # Generate local economy data
        local_economy = self._generate_village_economy(village_data, generated_npcs, biome_context)
        
        # Create generation prompt for AI enhancement
        generation_prompt = self.get_generation_prompt(poi, biome_context, racial_influence)
        
        # Prepare details data
        details_data = {
            "description": description,
            "detailed_features": detailed_features,
            "generated_npcs": generated_npcs,
            "local_issues": local_issues,
            "available_services": available_services,
            "unique_items": unique_items,
            "quest_hooks": quest_hooks,
            "hidden_secrets": hidden_secrets,
            "local_economy": local_economy,
            "generation_prompt": generation_prompt
        }
        
        # Save and return details
        return self.save_generated_details(db, poi, details_data)
    
    def _determine_village_type(
        self,
        biome_context: Dict[str, Any],
        poi: DBPointOfInterest,
        racial_influence: tuple
    ) -> str:
        """
        Determine what type of village this should be based on context.
        """
        biome_type = biome_context.get("biome_type", "")
        location_tags = poi.relative_location_tags or []
        dominant_race, influence_strength = racial_influence
        
        # Check location tags for hints
        if any("river" in tag or "water" in tag for tag in location_tags):
            if random.random() < 0.4:
                return "fishing"
        
        if any("crossroads" in tag or "route" in tag for tag in location_tags):
            if random.random() < 0.5:
                return "trading"
        
        # Check biome type preferences
        if "verdant" in biome_type.lower() or "frontier" in biome_type.lower():
            weights = {"farming": 0.4, "trading": 0.2, "frontier": 0.3, "mining": 0.1}
        elif "mountain" in biome_type.lower() or "highland" in biome_type.lower():
            weights = {"mining": 0.5, "frontier": 0.3, "trading": 0.1, "farming": 0.1}
        elif "ember" in biome_type.lower() or "desert" in biome_type.lower():
            weights = {"trading": 0.4, "mining": 0.3, "frontier": 0.3}
        elif "marsh" in biome_type.lower() or "wetland" in biome_type.lower():
            weights = {"fishing": 0.6, "frontier": 0.3, "trading": 0.1}
        else:
            # Default distribution
            weights = {"farming": 0.3, "trading": 0.25, "frontier": 0.2, "mining": 0.15, "fishing": 0.1}
        
        # Racial preferences
        if dominant_race == "dwarf":
            weights["mining"] = weights.get("mining", 0) + 0.3
        elif dominant_race == "elf":
            weights["farming"] = weights.get("farming", 0) + 0.2
        elif dominant_race == "human":
            weights["trading"] = weights.get("trading", 0) + 0.2
        elif dominant_race == "beastfolk":
            weights["frontier"] = weights.get("frontier", 0) + 0.3
        
        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}
        
        # Weighted random selection
        rand_val = random.random()
        cumulative = 0
        for village_type, weight in normalized_weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                return village_type
        
        return "farming"  # Fallback
    
    def _generate_village_description(
        self,
        poi: DBPointOfInterest,
        biome_context: Dict[str, Any],
        racial_influence: tuple,
        village_type: str,
        village_data: Dict[str, Any]
    ) -> str:
        """
        Generate a rich description of the village.
        """
        # Start with base description
        base_desc = self.generate_base_description(poi, biome_context, racial_influence)
        
        # Add village-specific elements
        primary_activities = village_data["primary_activities"]
        typical_buildings = village_data["typical_buildings"]
        
        # Population estimation
        pop_range = village_data["population_range"]
        estimated_pop = random.randint(pop_range[0], pop_range[1])
        
        population_desc = ""
        if estimated_pop < 20:
            population_desc = "a small community"
        elif estimated_pop < 40:
            population_desc = "a modest settlement"
        elif estimated_pop < 70:
            population_desc = "a thriving village"
        else:
            population_desc = "a large village approaching town status"
        
        # Activity description
        main_activity = random.choice(primary_activities).replace("_", " ")
        activity_desc = f"The community's livelihood centers around {main_activity}"
        
        # Architectural details
        building_desc = ""
        if typical_buildings:
            prominent_building = random.choice(typical_buildings).replace("_", " ")
            building_desc = f", with a prominent {prominent_building} serving as a focal point"
        
        # Environmental integration
        environmental_details = self.generate_environmental_details(biome_context, poi)
        env_desc = ""
        if environmental_details:
            env_detail = random.choice(environmental_details)
            env_desc = f" {env_detail}."
        
        full_description = (
            f"{base_desc} This is {population_desc} of roughly {estimated_pop} inhabitants. "
            f"{activity_desc}{building_desc}. The village shows signs of {village_data['wealth_level']} prosperity.{env_desc}"
        )
        
        return full_description
    
    def _generate_village_features(
        self,
        village_data: Dict[str, Any],
        biome_context: Dict[str, Any],
        racial_influence: tuple
    ) -> List[str]:
        """
        Generate specific architectural and cultural features of the village.
        """
        features = []
        dominant_race, influence_strength = racial_influence
        
        # Add typical buildings
        typical_buildings = village_data.get("typical_buildings", [])
        selected_buildings = random.sample(
            typical_buildings, min(3, len(typical_buildings))
        )
        
        for building in selected_buildings:
            building_name = building.replace("_", " ").title()
            features.append(f"A well-maintained {building_name}")
        
        # Add racial architectural features
        if influence_strength > 0.6:
            race_arch = self.racial_architecture.get(dominant_race, {})
            racial_features = race_arch.get("features", [])
            racial_decorations = race_arch.get("decorations", [])
            
            if racial_features:
                feature = random.choice(racial_features).replace("_", " ")
                features.append(f"Buildings display {dominant_race} {feature}")
            
            if racial_decorations and random.random() < 0.7:
                decoration = random.choice(racial_decorations).replace("_", " ")
                features.append(f"Many structures are adorned with {decoration}")
        
        # Add biome-specific adaptations
        biome_type = biome_context.get("biome_type", "")
        if "desert" in biome_type.lower():
            features.append("Buildings feature thick walls and small windows to combat heat")
        elif "mountain" in biome_type.lower():
            features.append("Structures are built low and sturdy to withstand mountain weather")
        elif "marsh" in biome_type.lower():
            features.append("Houses are elevated on stilts to avoid seasonal flooding")
        elif "forest" in biome_type.lower():
            features.append("Buildings incorporate living trees and natural materials")
        
        # Add magical features if leyline intensity is high
        leyline_intensity = biome_context.get("leyline_intensity", 1.0)
        if leyline_intensity > 2.0:
            features.append("Crystal formations around the village glow softly with magical energy")
        elif leyline_intensity > 1.5:
            features.append("Subtle ward stones mark the village boundaries")
        
        return features
    
    def _generate_village_npcs(
        self,
        village_type: str,
        village_data: Dict[str, Any],
        racial_influence: tuple,
        poi: DBPointOfInterest
    ) -> List[Dict[str, Any]]:
        """
        Generate NPCs for the village based on its type and characteristics.
        """
        npcs = []
        dominant_race, influence_strength = racial_influence
        
        # Get role template for this village type
        role_templates = self.npc_roles.get(village_type, self.npc_roles["farming"])
        
        for role_template in role_templates:
            role = role_template["role"]
            importance = role_template["importance"]
            count = role_template["count"]
            
            # Determine actual count
            if isinstance(count, tuple):
                actual_count = random.randint(count[0], count[1])
            else:
                actual_count = count
            
            # Generate NPCs for this role
            for i in range(actual_count):
                npc = self._generate_single_npc(
                    role, importance, dominant_race, influence_strength, village_type
                )
                npcs.append(npc)
        
        return npcs
    
    def _generate_single_npc(
        self,
        role: str,
        importance: str,
        dominant_race: str,
        influence_strength: float,
        village_type: str
    ) -> Dict[str, Any]:
        """
        Generate a single NPC with characteristics.
        """
        # Determine race
        if random.random() < influence_strength:
            npc_race = dominant_race
        else:
            # Secondary race based on village type and location
            secondary_races = ["human", "elf", "dwarf", "orc", "beastfolk", "ferverl"]
            secondary_races.remove(dominant_race)
            npc_race = random.choice(secondary_races)
        
        # Generate name (simplified - in a real implementation, you'd have race-specific name generators)
        name = self._generate_npc_name(npc_race, role)
        
        # Generate basic characteristics
        personality_traits = self._generate_personality_traits(npc_race, role)
        motivations = self._generate_npc_motivations(role, village_type)
        
        npc = {
            "id": str(uuid.uuid4()),
            "name": name,
            "race": npc_race,
            "role": role.replace("_", " ").title(),
            "importance": importance,
            "personality_traits": personality_traits,
            "motivations": motivations,
            "services": self._get_npc_services(role),
            "knowledge": self._get_npc_knowledge(role, importance),
            "attitude": "neutral",  # Starting attitude
            "dialogue_style": self._get_dialogue_style(npc_race, personality_traits)
        }
        
        return npc
    
    def _generate_npc_name(self, race: str, role: str) -> str:
        """
        Generate a name appropriate for the NPC's race and role.
        """
        # Simplified name generation - in a full implementation, 
        # you'd have extensive name databases by race
        prefixes = {
            "human": ["Aldric", "Mira", "Gareth", "Elena", "Thom", "Sara"],
            "elf": ["Aelindra", "Silvyr", "Thalion", "Nimrodel", "Legolas", "Arwen"],
            "dwarf": ["Thorin", "Daina", "Balin", "Nala", "Gimli", "Disa"],
            "orc": ["Grosh", "Urka", "Thrak", "Morghul", "Grishna", "Bolg"],
            "beastfolk": ["Fenris", "Lyra", "Hawk-Eye", "Swift-Paw", "Iron-Mane", "Bright-Tail"],
            "ferverl": ["Zara", "Kael", "Nyth", "Vera", "Thane", "Lysa"]
        }
        
        titles = {
            "village_elder": ["the Wise", "the Elder", "the Respected"],
            "blacksmith": ["the Smith", "Ironhand", "Hammerfall"],
            "merchant": ["the Trader", "Coinpurse", "the Dealer"],
            "innkeeper": ["the Host", "Welcomeheart", "the Friendly"],
            "mine_foreman": ["the Foreman", "Rockbreaker", "the Supervisor"],
            "trade_master": ["the Negotiator", "Goldtongue", "the Broker"]
        }
        
        base_names = prefixes.get(race, prefixes["human"])
        name = random.choice(base_names)
        
        # Add title if it's an important role
        if role in titles and random.random() < 0.6:
            title = random.choice(titles[role])
            name = f"{name} {title}"
        
        return name
    
    def _generate_personality_traits(self, race: str, role: str) -> List[str]:
        """
        Generate personality traits based on race and role.
        """
        race_traits = {
            "human": ["adaptable", "ambitious", "curious", "pragmatic"],
            "elf": ["patient", "wise", "formal", "traditional"],
            "dwarf": ["sturdy", "loyal", "craftsman", "stubborn"],
            "orc": ["direct", "strong", "honorable", "hardworking"],
            "beastfolk": ["instinctual", "spiritual", "communal", "protective"],
            "ferverl": ["resilient", "ritualistic", "adaptive", "scarred"]
        }
        
        role_traits = {
            "village_elder": ["respected", "authoritative", "wise"],
            "blacksmith": ["skilled", "strong", "practical"],
            "merchant": ["shrewd", "persuasive", "well-traveled"],
            "innkeeper": ["hospitable", "gossiper", "friendly"],
            "farmer": ["hardworking", "seasonal", "earth-connected"],
            "guard": ["vigilant", "protective", "disciplined"]
        }
        
        traits = []
        
        # Add racial traits
        racial_options = race_traits.get(race, race_traits["human"])
        traits.extend(random.sample(racial_options, min(2, len(racial_options))))
        
        # Add role traits
        role_options = role_traits.get(role, ["competent", "dedicated"])
        traits.extend(random.sample(role_options, min(2, len(role_options))))
        
        return list(set(traits))  # Remove duplicates
    
    def _generate_npc_motivations(self, role: str, village_type: str) -> List[str]:
        """
        Generate motivations for the NPC based on their role and village context.
        """
        motivations = []
        
        role_motivations = {
            "village_elder": [
                "Maintain peace and prosperity in the village",
                "Preserve local traditions and customs",
                "Mediate disputes fairly"
            ],
            "blacksmith": [
                "Perfect their craft and techniques",
                "Provide quality tools for the community",
                "Train the next generation of smiths"
            ],
            "merchant": [
                "Expand trade opportunities", 
                "Build profitable relationships",
                "Discover new markets and goods"
            ],
            "innkeeper": [
                "Provide comfort to travelers",
                "Gather news and information",
                "Maintain a welcoming establishment"
            ]
        }
        
        # Add role-specific motivations
        if role in role_motivations:
            motivations.extend(random.sample(
                role_motivations[role], 
                min(2, len(role_motivations[role]))
            ))
        
        # Add village-type specific motivations
        if village_type == "trading":
            motivations.append("Increase trade volume through the village")
        elif village_type == "farming":
            motivations.append("Ensure good harvests and food security")
        elif village_type == "mining":
            motivations.append("Maintain safe and productive mining operations")
        elif village_type == "frontier":
            motivations.append("Protect the village from external threats")
        
        return motivations
    
    def _get_npc_services(self, role: str) -> List[str]:
        """
        Get services that this NPC can provide to players.
        """
        services_map = {
            "blacksmith": ["weapon_repair", "armor_repair", "custom_forging", "tool_creation"],
            "innkeeper": ["room_rental", "meals", "local_information", "message_delivery"],
            "merchant": ["goods_purchase", "goods_sale", "price_information", "trade_contacts"],
            "village_elder": ["local_history", "dispute_resolution", "official_permits"],
            "farmer": ["food_supplies", "local_produce", "seasonal_information"],
            "guard": ["security_escort", "threat_assessment", "training"],
            "mine_foreman": ["mining_equipment", "ore_assessment", "underground_maps"],
            "caravan_guide": ["route_planning", "escort_services", "travel_supplies"]
        }
        
        return services_map.get(role, ["general_assistance", "local_information"])
    
    def _get_npc_knowledge(self, role: str, importance: str) -> List[str]:
        """
        Determine what knowledge this NPC possesses.
        """
        knowledge = ["local_area", "village_residents"]
        
        if importance == "high":
            knowledge.extend(["village_history", "regional_politics", "important_secrets"])
        elif importance == "medium":
            knowledge.extend(["trade_information", "recent_events"])
        
        role_knowledge = {
            "village_elder": ["ancient_lore", "family_histories", "traditional_customs"],
            "merchant": ["trade_routes", "market_prices", "distant_cities"],
            "blacksmith": ["metallurgy", "weapon_quality", "armor_assessment"],
            "innkeeper": ["traveler_news", "regional_gossip", "local_rumors"],
            "guard": ["security_threats", "monster_activity", "patrol_routes"],
            "farmer": ["weather_patterns", "crop_cycles", "animal_behavior"]
        }
        
        if role in role_knowledge:
            knowledge.extend(role_knowledge[role])
        
        return knowledge
    
    def _get_dialogue_style(self, race: str, personality_traits: List[str]) -> str:
        """
        Determine the NPC's dialogue style based on race and personality.
        """
        if "formal" in personality_traits or race == "elf":
            return "formal"
        elif "direct" in personality_traits or race == "orc":
            return "direct"
        elif "friendly" in personality_traits or "hospitable" in personality_traits:
            return "friendly"
        elif "wise" in personality_traits:
            return "thoughtful"
        else:
            return "conversational"
    
    def _generate_village_issues(
        self,
        village_type: str,
        biome_context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate current issues affecting the village.
        """
        issues = []
        
        # Select 1-3 issues from different categories
        issue_categories = list(self.village_issues.keys())
        selected_categories = random.sample(issue_categories, random.randint(1, 3))
        
        for category in selected_categories:
            category_issues = self.village_issues[category]
            issues.append(random.choice(category_issues))
        
        # Add village-type specific issues
        if village_type == "mining":
            mining_issues = [
                "A recent cave-in has blocked access to the richest ore vein",
                "Strange noises from deep tunnels have spooked the miners",
                "Equipment keeps breaking down at an unusual rate"
            ]
            if random.random() < 0.4:
                issues.append(random.choice(mining_issues))
        
        elif village_type == "trading":
            trading_issues = [
                "A rival trading post is undercutting local prices",
                "Caravan schedules have become unreliable",
                "Customs disputes are delaying shipments"
            ]
            if random.random() < 0.4:
                issues.append(random.choice(trading_issues))
        
        # Add biome-specific issues
        hazards = biome_context.get("hazards", [])
        if hazards and random.random() < 0.3:
            hazard = random.choice(hazards)
            issues.append(f"Recent {hazard.replace('_', ' ')} has been affecting village operations")
        
        return issues
    
    def _generate_village_services(
        self,
        village_data: Dict[str, Any],
        generated_npcs: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate available services in the village.
        """
        services = set()
        
        # Add services from NPCs
        for npc in generated_npcs:
            npc_services = npc.get("services", [])
            services.update(npc_services)
        
        # Add common services based on village type
        common_services = village_data.get("common_services", [])
        services.update(common_services)
        
        # Convert to readable format
        readable_services = []
        for service in services:
            readable_service = service.replace("_", " ").title()
            readable_services.append(readable_service)
        
        return sorted(readable_services)
    
    def _generate_village_quest_hooks(
        self,
        poi: DBPointOfInterest,
        village_type: str,
        local_issues: List[str],
        generated_npcs: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate quest hooks specific to this village.
        """
        hooks = []
        
        # Generate hooks from local issues
        for issue in local_issues[:2]:  # Use first 2 issues as quest hooks
            if "bandits" in issue.lower():
                hooks.append("The village needs protection from bandit raids")
            elif "missing" in issue.lower() or "disappear" in issue.lower():
                hooks.append("Someone needs to investigate the mysterious disappearances")
            elif "water" in issue.lower():
                hooks.append("The village's water supply needs to be restored or purified")
            elif "trade" in issue.lower():
                hooks.append("A diplomatic mission could resolve the trade disputes")
            else:
                hooks.append(f"The community seeks help with: {issue.lower()}")
        
        # Add village-type specific hooks
        type_hooks = {
            "mining": [
                "Ancient tunnels beneath the mine may hold forgotten treasures",
                "Strange ore samples need to be analyzed by experts",
                "Missing miners were last seen heading toward the old shafts"
            ],
            "trading": [
                "A lost caravan needs to be tracked down",
                "New trade routes through dangerous territory need to be scouted",
                "Valuable cargo has been stolen and must be recovered"
            ],
            "farming": [
                "Crops are failing due to an unknown blight",
                "Livestock are being taken by an unknown predator",
                "Ancient irrigation channels need to be cleared"
            ],
            "frontier": [
                "The village needs scouts to map the surrounding wilderness",
                "Hostile creatures threaten the settlement's borders",
                "Supplies for the village are trapped behind enemy lines"
            ]
        }
        
        if village_type in type_hooks:
            village_hooks = type_hooks[village_type]
            hooks.append(random.choice(village_hooks))
        
        # Add NPC-driven hooks
        important_npcs = [npc for npc in generated_npcs if npc.get("importance") == "high"]
        if important_npcs:
            npc = random.choice(important_npcs)
            hooks.append(f"{npc['name']} has a personal request that could benefit the village")
        
        return hooks
    
    def _generate_village_secrets(
        self,
        village_type: str,
        biome_context: Dict[str, Any],
        racial_influence: tuple
    ) -> List[str]:
        """
        Generate hidden secrets that players might discover.
        """
        secrets = []
        dominant_race, influence_strength = racial_influence
        
        # Generic village secrets
        generic_secrets = [
            "One of the villagers is not who they claim to be",
            "There's a hidden cache of supplies from the Crimson Dissonance era",
            "The village was built on the site of an ancient settlement",
            "Local folklore contains clues to a lost treasure",
            "Someone in the village is secretly communicating with outsiders"
        ]
        
        secrets.append(random.choice(generic_secrets))
        
        # Village-type specific secrets
        if village_type == "mining":
            mining_secrets = [
                "The mine connects to a network of ancient dwarven tunnels",
                "Rare crystals found in the mine have magical properties",
                "There's a sealed chamber that predates the current mining operation"
            ]
            secrets.append(random.choice(mining_secrets))
        
        elif village_type == "trading":
            trading_secrets = [
                "The village serves as a waystation for smugglers",
                "Hidden compartments in the inn conceal valuable contraband",
                "The trade master has contacts in rival cities' governments"
            ]
            secrets.append(random.choice(trading_secrets))
        
        # Racial secrets
        if influence_strength > 0.7:
            if dominant_race == "elf":
                secrets.append("Elven residents maintain a secret shrine to their ancestors")
            elif dominant_race == "dwarf":
                secrets.append("The village contains entrance to abandoned dwarven halls")
            elif dominant_race == "ferverl":
                secrets.append("Ferverl rituals here help maintain leyline stability")
            elif dominant_race == "beastfolk":
                secrets.append("The village protects sacred spirit totems")
        
        # Biome-related secrets
        magical_phenomena = biome_context.get("magical_phenomena", [])
        if magical_phenomena:
            phenomenon = random.choice(magical_phenomena)
            secrets.append(f"The village's location helps control {phenomenon.replace('_', ' ')}")
        
        return secrets
    
    def _generate_village_economy(
        self,
        village_data: Dict[str, Any],
        generated_npcs: List[Dict[str, Any]],
        biome_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate economic data for the village.
        """
        economy = {
            "wealth_level": village_data["wealth_level"],
            "primary_industries": village_data["primary_activities"],
            "trade_goods": [],
            "imports": [],
            "exports": [],
            "currency_flow": "moderate",
            "economic_challenges": []
        }
        
        # Determine trade goods based on biome resources and village type
        available_resources = biome_context.get("resources", {})
        
        for resource, availability in available_resources.items():
            if availability > 0.5:  # High availability
                economy["trade_goods"].append({
                    "name": resource.replace("_", " ").title(),
                    "availability": "abundant",
                    "price_modifier": 0.8  # Cheaper due to local abundance
                })
                economy["exports"].append(resource.replace("_", " ").title())
        
        # Add imports based on what's missing
        all_basic_needs = ["food", "tools", "clothing", "medicine"]
        local_production = [activity.replace("_", " ") for activity in village_data["primary_activities"]]
        
        for need in all_basic_needs:
            if need not in local_production:
                economy["imports"].append(need.title())
        
        # Economic challenges based on issues
        if village_data["wealth_level"] == "poor":
            economy["economic_challenges"].append("Limited access to capital for improvements")
        
        economy["currency_flow"] = village_data["wealth_level"]
        
        return economy
