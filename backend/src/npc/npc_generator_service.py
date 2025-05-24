"""
NPC Generator Service

This module provides a service for generating NPCs with different roles,
attributes, and characteristics for the game world. It integrates with
the economy system and other game systems.
"""

import random
import logging
import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

# Import models
from backend.src.npc.models.pydantic_models import (
    NpcData, NpcArchetype, NpcGenerationParams, NpcNeeds,
    Gender, EconomicRole, InventorySlot
)
from backend.src.npc.models.db_models import DBNpc, DBNpcArchetype
from backend.src.npc.crud import (
    create_npc, get_npc, get_npcs, get_npcs_by_location, 
    get_archetype, get_archetypes, update_npc, delete_npc
)

# Import integration with economy system
# This is to demonstrate how we'd integrate with other systems
# from backend.src.economy.models.db_models import DBItem, DBShop, DBBusiness, DBLocation
# from backend.src.economy.services.shop_service import ShopService

logger = logging.getLogger(__name__)

class NpcGeneratorService:
    """
    Service for generating NPCs with different attributes based on various parameters.
    """
    
    def __init__(self, data_dir: str = "data/npc_generator"):
        """
        Initialize the NPC Generator Service.
        
        Args:
            data_dir: Directory containing generation data files
        """
        self.logger = logging.getLogger("NpcGeneratorService")
        self.data_dir = data_dir
        
        # Load name data
        self.first_names = self._load_names("first_names.json")
        self.last_names = self._load_names("last_names.json")
        
        # Load generation data
        self.personality_traits = self._load_data("personality_traits.json", [])
        self.backstory_templates = self._load_data("backstory_templates.json", [])
        self.skill_definitions = self._load_data("skill_definitions.json", {})
        self.item_templates = self._load_data("item_templates.json", {})
        
        # Initialization flags
        self.initialized = False
        
        # Initialize with basic archetypes if not yet loaded
        self.archetypes = {}
        self._ensure_basic_archetypes_loaded()
        
        self.logger.info("NPC Generator Service initialized")
    
    def _load_names(self, filename: str) -> Dict[str, List[str]]:
        """
        Load name data from a JSON file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Dictionary mapping cultural groups to lists of names
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Name file {filepath} not found, using default data")
                # Return some default data if file not found
                return {
                    "common": ["John", "Jane", "Alex", "Morgan", "Taylor", "Sam", "Jordan"],
                    "fantasy": ["Elrond", "Galadriel", "Aragorn", "Arwen", "Gandalf", "Frodo"]
                }
        except Exception as e:
            self.logger.error(f"Error loading names from {filename}: {e}")
            return {"common": ["John", "Jane", "Alex"]}
    
    def _load_data(self, filename: str, default: Any) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the file to load
            default: Default value to return if file not found
            
        Returns:
            Loaded data or default value
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Data file {filepath} not found, using default data")
                return default
        except Exception as e:
            self.logger.error(f"Error loading data from {filename}: {e}")
            return default
    
    def _ensure_basic_archetypes_loaded(self):
        """Ensure basic archetypes are loaded into memory."""
        # This would normally load from database or files
        if not self.archetypes:
            # Create some basic archetypes
            self.archetypes = {
                "blacksmith": {
                    "name": "blacksmith",
                    "description": "A skilled metalworker who crafts weapons and armor",
                    "possible_roles": ["ARTISAN_BLACKSMITH"],
                    "age_range": (30, 60),
                    "gender_weights": {"male": 0.7, "female": 0.3},
                    "currency_range": (50.0, 150.0),
                    "skill_ranges": {
                        "smithing": (5, 10),
                        "metalworking": (5, 10),
                        "haggling": (3, 7)
                    },
                    "personality_weights": {
                        "gruff": 0.6,
                        "hardworking": 0.8,
                        "honest": 0.7,
                        "proud": 0.6
                    },
                    "inventory_items": [
                        {"item_type": "hammer", "weight": 1.0, "quantity_range": (1, 1)},
                        {"item_type": "tongs", "weight": 1.0, "quantity_range": (1, 1)},
                        {"item_type": "iron_ingot", "weight": 0.8, "quantity_range": (5, 15)},
                        {"item_type": "steel_ingot", "weight": 0.5, "quantity_range": (2, 8)}
                    ],
                    "backstory_templates": [
                        "Learned the craft from {their} father, who was also a blacksmith.",
                        "Apprenticed under a master smith in the capital before setting up shop here.",
                        "Discovered a natural talent for metalworking after working in the mines."
                    ],
                    "need_modifiers": {
                        "food": 1.2,  # Blacksmiths work hard and eat more
                        "luxury": 0.7  # Less concerned with luxury
                    }
                },
                "merchant": {
                    "name": "merchant",
                    "description": "A traveling trader who buys and sells goods",
                    "possible_roles": ["MERCHANT", "TRADER"],
                    "age_range": (25, 55),
                    "gender_weights": {"male": 0.5, "female": 0.5},
                    "currency_range": (100.0, 300.0),
                    "skill_ranges": {
                        "haggling": (6, 10),
                        "persuasion": (5, 9),
                        "appraisal": (4, 8)
                    },
                    "personality_weights": {
                        "friendly": 0.7,
                        "shrewd": 0.8,
                        "ambitious": 0.6,
                        "worldly": 0.7
                    },
                    "inventory_items": [
                        {"item_type": "ledger", "weight": 1.0, "quantity_range": (1, 1)},
                        {"item_type": "fine_clothes", "weight": 0.8, "quantity_range": (1, 3)},
                        {"item_type": "trade_goods", "weight": 1.0, "quantity_range": (10, 30)}
                    ],
                    "backstory_templates": [
                        "Started as a humble peddler before building a successful trading business.",
                        "Inherited the family business and expanded it to new markets.",
                        "Escaped a life of poverty by developing a keen eye for valuable goods."
                    ],
                    "need_modifiers": {
                        "luxury": 1.4,  # Merchants appreciate the finer things
                        "shelter": 1.2  # Need good accommodations for business
                    }
                },
                "innkeeper": {
                    "name": "innkeeper",
                    "description": "Owner of a tavern or inn who provides food, drink, and lodging",
                    "possible_roles": ["SHOPKEEPER"],
                    "age_range": (35, 65),
                    "gender_weights": {"male": 0.5, "female": 0.5},
                    "currency_range": (75.0, 200.0),
                    "skill_ranges": {
                        "cooking": (4, 8),
                        "hospitality": (6, 10),
                        "gossip": (5, 9)
                    },
                    "personality_weights": {
                        "friendly": 0.8,
                        "gossipy": 0.7,
                        "hardworking": 0.6,
                        "welcoming": 0.9
                    },
                    "inventory_items": [
                        {"item_type": "ale_keg", "weight": 0.9, "quantity_range": (2, 5)},
                        {"item_type": "wine_bottle", "weight": 0.8, "quantity_range": (5, 15)},
                        {"item_type": "food_supplies", "weight": 1.0, "quantity_range": (10, 30)}
                    ],
                    "backstory_templates": [
                        "Took over the family inn after {their} parents retired.",
                        "Built the establishment from scratch after saving for years.",
                        "Won the deed to the inn in a game of chance with its previous owner."
                    ],
                    "need_modifiers": {
                        "food": 0.8,  # Always has access to food
                        "leisure": 0.6  # Works long hours with little leisure time
                    }
                }
            }
            
            # Add a few more archetypes
            self.archetypes.update({
                "farmer": {
                    "name": "farmer",
                    "description": "A person who works the land to grow crops or raise livestock",
                    "possible_roles": ["FARMER"],
                    "age_range": (20, 70),
                    "gender_weights": {"male": 0.6, "female": 0.4},
                    "currency_range": (20.0, 80.0),
                    "skill_ranges": {
                        "farming": (5, 10),
                        "animal_husbandry": (3, 8),
                        "weather_prediction": (4, 7)
                    },
                    "personality_weights": {
                        "hardworking": 0.9,
                        "patient": 0.7,
                        "practical": 0.8,
                        "stubborn": 0.6
                    },
                    "inventory_items": [
                        {"item_type": "hoe", "weight": 1.0, "quantity_range": (1, 1)},
                        {"item_type": "seeds", "weight": 0.9, "quantity_range": (5, 20)},
                        {"item_type": "vegetables", "weight": 0.8, "quantity_range": (10, 30)}
                    ],
                    "backstory_templates": [
                        "Has worked the same land for generations, inheriting it from {their} ancestors.",
                        "Lost everything in a flood and had to start over with this small plot.",
                        "Dreamed of adventure but stayed to take care of the family farm."
                    ],
                    "need_modifiers": {
                        "food": 0.7,  # Produces own food
                        "healthcare": 1.2  # Physical labor leads to more healthcare needs
                    }
                },
                "guard": {
                    "name": "guard",
                    "description": "A person responsible for protecting a location or person",
                    "possible_roles": ["GUARD"],
                    "age_range": (20, 45),
                    "gender_weights": {"male": 0.7, "female": 0.3},
                    "currency_range": (30.0, 90.0),
                    "skill_ranges": {
                        "combat": (5, 8),
                        "intimidation": (4, 7),
                        "perception": (3, 7)
                    },
                    "personality_weights": {
                        "vigilant": 0.8,
                        "dutiful": 0.7,
                        "suspicious": 0.6,
                        "brave": 0.7
                    },
                    "inventory_items": [
                        {"item_type": "sword", "weight": 0.9, "quantity_range": (1, 1)},
                        {"item_type": "shield", "weight": 0.8, "quantity_range": (1, 1)},
                        {"item_type": "uniform", "weight": 1.0, "quantity_range": (1, 1)}
                    ],
                    "backstory_templates": [
                        "Joined the guard after serving in the army during the last war.",
                        "Became a guard to follow in the footsteps of {their} respected parent.",
                        "Turned to guard work after witnessing crime destroy {their} neighborhood."
                    ],
                    "need_modifiers": {
                        "shelter": 0.8,  # Often provided barracks
                        "leisure": 1.3  # Needs more downtime due to stressful work
                    }
                }
            })
    
    def get_archetype(self, archetype_name: str) -> Optional[Dict[str, Any]]:
        """
        Get an archetype by name.
        
        Args:
            archetype_name: Name of the archetype
            
        Returns:
            Archetype data or None if not found
        """
        return self.archetypes.get(archetype_name.lower())
    
    def generate_npc(self, 
                   db: Session, 
                   generation_params: NpcGenerationParams) -> DBNpc:
        """
        Generate a new NPC based on the provided parameters.
        
        Args:
            db: Database session
            generation_params: Parameters for NPC generation
            
        Returns:
            Generated NPC database object
        """
        self.logger.info(f"Generating NPC for location {generation_params.target_location_id}")
        
        # Determine archetype
        archetype_data = None
        if generation_params.archetype_name:
            # Load archetype from DB or memory
            archetype_data = self.get_archetype(generation_params.archetype_name)
            if not archetype_data:
                self.logger.warning(f"Archetype {generation_params.archetype_name} not found, using random archetype")
                archetype_name = random.choice(list(self.archetypes.keys()))
                archetype_data = self.archetypes[archetype_name]
        else:
            # Select random archetype
            archetype_name = random.choice(list(self.archetypes.keys()))
            archetype_data = self.archetypes[archetype_name]
        
        # Generate NPC data
        npc_data = self._generate_npc_from_params_and_archetype(generation_params, archetype_data)
        
        # Create the NPC in the database
        db_npc = create_npc(db, npc_data)
        
        self.logger.info(f"Generated NPC: {db_npc.name} ({db_npc.id})")
        return db_npc
    
    def generate_multiple_npcs(self, 
                             db: Session, 
                             generation_requests: List[NpcGenerationParams]) -> List[DBNpc]:
        """
        Generate multiple NPCs based on the provided parameters.
        
        Args:
            db: Database session
            generation_requests: List of NPC generation parameter sets
            
        Returns:
            List of generated NPC database objects
        """
        generated_npcs = []
        
        for params in generation_requests:
            try:
                npc = self.generate_npc(db, params)
                generated_npcs.append(npc)
            except Exception as e:
                self.logger.error(f"Error generating NPC with params {params}: {e}")
        
        return generated_npcs
    
    def populate_location(self, 
                        db: Session, 
                        location_id: str, 
                        population_count: int,
                        role_distribution: Optional[Dict[str, float]] = None) -> List[DBNpc]:
        """
        Populate a location with NPCs based on specified distribution.
        
        Args:
            db: Database session
            location_id: Location identifier
            population_count: Number of NPCs to generate
            role_distribution: Optional dictionary mapping roles to proportions
            
        Returns:
            List of generated NPC database objects
        """
        self.logger.info(f"Populating location {location_id} with {population_count} NPCs")
        
        # Default role distribution if none provided
        if not role_distribution:
            role_distribution = {
                "SHOPKEEPER": 0.1,
                "ARTISAN_BLACKSMITH": 0.05,
                "ARTISAN_TAILOR": 0.05,
                "FARMER": 0.2,
                "LABORER": 0.3,
                "MERCHANT": 0.1,
                "GUARD": 0.1,
                "UNEMPLOYED_DRIFTER": 0.05,
                "NOBLE_CONSUMER": 0.05
            }
        
        # Normalize distribution
        total = sum(role_distribution.values())
        normalized_distribution = {k: v/total for k, v in role_distribution.items()}
        
        # Calculate counts for each role
        role_counts = {}
        remaining = population_count
        
        for role, proportion in normalized_distribution.items():
            if role == list(normalized_distribution.keys())[-1]:
                # Last role gets the remainder to ensure we hit exactly population_count
                role_counts[role] = remaining
            else:
                count = int(population_count * proportion)
                role_counts[role] = count
                remaining -= count
        
        # Generate NPCs for each role
        generation_requests = []
        
        for role, count in role_counts.items():
            for _ in range(count):
                # Select appropriate archetype for this role
                archetype_name = self._get_archetype_for_role(role)
                
                # Create generation parameters
                params = NpcGenerationParams(
                    target_location_id=location_id,
                    requested_role=role,
                    archetype_name=archetype_name
                )
                
                generation_requests.append(params)
        
        # Generate all NPCs
        return self.generate_multiple_npcs(db, generation_requests)
    
    def _get_archetype_for_role(self, role: str) -> str:
        """
        Get an appropriate archetype for a given role.
        
        Args:
            role: Economic role
            
        Returns:
            Archetype name
        """
        # Map roles to suitable archetypes
        role_to_archetype = {
            "SHOPKEEPER": "innkeeper",
            "ARTISAN_BLACKSMITH": "blacksmith",
            "MERCHANT": "merchant",
            "TRADER": "merchant",
            "FARMER": "farmer",
            "GUARD": "guard"
        }
        
        # Return matching archetype or default to a random one
        return role_to_archetype.get(role, random.choice(list(self.archetypes.keys())))
    
    def _generate_npc_from_params_and_archetype(self, 
                                             params: NpcGenerationParams, 
                                             archetype_data: Dict[str, Any]) -> NpcData:
        """
        Generate NPC data based on parameters and archetype.
        
        Args:
            params: NPC generation parameters
            archetype_data: Archetype data
            
        Returns:
            Generated NPC data
        """
        # Generate basic properties
        npc_id = f"npc-{uuid4().hex}"
        name = self._generate_name()
        
        # Determine age
        age_range = params.age_range or archetype_data.get("age_range", (20, 60))
        age = random.randint(age_range[0], age_range[1])
        
        # Determine gender
        if params.gender:
            gender = params.gender
        else:
            gender_weights = archetype_data.get("gender_weights", {"male": 0.5, "female": 0.5})
            gender = self._weighted_choice(gender_weights)
        
        # Determine economic role
        if params.requested_role:
            economic_role = params.requested_role
        else:
            possible_roles = archetype_data.get("possible_roles", ["UNEMPLOYED_DRIFTER"])
            economic_role = random.choice(possible_roles)
        
        # Generate personality traits
        personality_weights = archetype_data.get("personality_weights", {})
        personality_tags = self._generate_personality_traits(personality_weights, 3)
        
        # Add specified traits if any
        if params.personality_traits:
            for trait in params.personality_traits:
                if trait not in personality_tags:
                    personality_tags.append(trait)
        
        # Generate backstory
        backstory_templates = archetype_data.get("backstory_templates", [
            "{name} is just trying to make a living."
        ])
        backstory_hook = self._generate_backstory(random.choice(backstory_templates), name, gender)
        
        # Generate skills
        skill_ranges = archetype_data.get("skill_ranges", {})
        skills = self._generate_skills(skill_ranges)
        
        # Add required skills if specified
        if params.required_skills:
            for skill in params.required_skills:
                if skill not in skills:
                    skills[skill] = random.randint(1, 5)  # Basic proficiency
        
        # Determine currency
        currency_range = archetype_data.get("currency_range", (10.0, 50.0))
        min_currency = params.min_currency if params.min_currency is not None else currency_range[0]
        max_currency = params.max_currency if params.max_currency is not None else currency_range[1]
        currency = round(random.uniform(min_currency, max_currency), 2)
        
        # Generate inventory
        inventory = self._generate_inventory(archetype_data.get("inventory_items", []))
        
        # Generate needs
        base_needs = NpcNeeds()
        need_modifiers = archetype_data.get("need_modifiers", {})
        needs = self._apply_need_modifiers(base_needs, need_modifiers)
        
        # Create NPC data object
        return NpcData(
            id=npc_id,
            name=name,
            age=age,
            gender=gender,
            personality_tags=personality_tags,
            backstory_hook=backstory_hook,
            current_location_id=params.target_location_id,
            economic_role=economic_role,
            skills=skills,
            currency=currency,
            inventory=inventory,
            needs=needs,
            faction_id=params.faction_id,
            custom_data=params.custom_params
        )
    
    def _generate_name(self) -> str:
        """
        Generate a random name.
        
        Returns:
            Generated name
        """
        # Get a random cultural group for first and last names
        first_name_culture = random.choice(list(self.first_names.keys()))
        last_name_culture = random.choice(list(self.last_names.keys()))
        
        # Get random names from each culture
        first_name = random.choice(self.first_names[first_name_culture])
        last_name = random.choice(self.last_names[last_name_culture])
        
        return f"{first_name} {last_name}"
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """
        Make a weighted random choice from a dictionary of options.
        
        Args:
            weights: Dictionary mapping options to weights
            
        Returns:
            Selected option
        """
        options = list(weights.keys())
        weights_list = [weights[opt] for opt in options]
        
        # Normalize weights
        total = sum(weights_list)
        normalized_weights = [w/total for w in weights_list]
        
        # Make weighted choice
        return random.choices(options, normalized_weights, k=1)[0]
    
    def _generate_personality_traits(self, 
                                   trait_weights: Dict[str, float], 
                                   count: int = 3) -> List[str]:
        """
        Generate random personality traits.
        
        Args:
            trait_weights: Dictionary mapping traits to weights
            count: Number of traits to generate
            
        Returns:
            List of personality traits
        """
        # If weights provided, use weighted selection
        if trait_weights:
            # Select weighted traits
            traits = []
            available_traits = list(trait_weights.keys())
            
            # Ensure we don't try to select more traits than available
            selection_count = min(count, len(available_traits))
            
            for _ in range(selection_count):
                if not available_traits:
                    break
                    
                # Select trait
                weights = [trait_weights[trait] for trait in available_traits]
                total = sum(weights)
                normalized_weights = [w/total for w in weights]
                
                trait = random.choices(available_traits, normalized_weights, k=1)[0]
                traits.append(trait)
                
                # Remove selected trait to avoid duplicates
                available_traits.remove(trait)
            
            return traits
        
        # Otherwise use random selection from default list
        if not self.personality_traits:
            self.personality_traits = [
                "friendly", "shy", "bold", "cautious", "curious", "stubborn",
                "generous", "greedy", "honest", "deceitful", "loyal", "fickle",
                "patient", "impatient", "serious", "playful", "optimistic", "pessimistic"
            ]
        
        return random.sample(self.personality_traits, min(count, len(self.personality_traits)))
    
    def _generate_backstory(self, template: str, name: str, gender: Gender) -> str:
        """
        Generate a backstory from a template.
        
        Args:
            template: Backstory template
            name: NPC name
            gender: NPC gender
            
        Returns:
            Generated backstory
        """
        # Determine pronouns based on gender
        pronouns = {
            Gender.MALE: {"their": "his", "them": "him", "they": "he"},
            Gender.FEMALE: {"their": "her", "them": "her", "they": "she"},
            Gender.NON_BINARY: {"their": "their", "them": "them", "they": "they"},
            Gender.UNSPECIFIED: {"their": "their", "them": "them", "they": "they"}
        }
        
        # Replace placeholders in template
        backstory = template.replace("{name}", name)
        
        for placeholder, value in pronouns[gender].items():
            backstory = backstory.replace("{" + placeholder + "}", value)
        
        return backstory
    
    def _generate_skills(self, skill_ranges: Dict[str, Tuple[int, int]]) -> Dict[str, int]:
        """
        Generate skills based on specified ranges.
        
        Args:
            skill_ranges: Dictionary mapping skill names to (min, max) ranges
            
        Returns:
            Dictionary of skills and proficiency levels
        """
        skills = {}
        
        for skill, (min_val, max_val) in skill_ranges.items():
            skills[skill] = random.randint(min_val, max_val)
        
        return skills
    
    def _generate_inventory(self, inventory_items: List[Dict[str, Any]]) -> Dict[str, InventorySlot]:
        """
        Generate inventory based on specified items.
        
        Args:
            inventory_items: List of possible inventory items with weights and quantities
            
        Returns:
            Dictionary of inventory slots
        """
        inventory = {}
        
        for item_spec in inventory_items:
            # Check if this item should be included based on weight
            if random.random() <= item_spec.get("weight", 1.0):
                # Determine quantity
                quantity_range = item_spec.get("quantity_range", (1, 1))
                quantity = random.randint(quantity_range[0], quantity_range[1])
                
                if quantity <= 0:
                    continue
                
                # Create item ID (in a real implementation, this would reference actual items)
                item_type = item_spec.get("item_type", "unknown")
                item_id = f"{item_type}-{uuid4().hex[:8]}"
                
                # Create inventory slot
                inventory[item_id] = InventorySlot(
                    item_id=item_id,
                    quantity=quantity,
                    condition=item_spec.get("condition", 1.0),
                    custom_data={"item_type": item_type}
                ).dict()
        
        return inventory
    
    def _apply_need_modifiers(self, base_needs: NpcNeeds, modifiers: Dict[str, float]) -> NpcNeeds:
        """
        Apply modifiers to base needs.
        
        Args:
            base_needs: Base needs
            modifiers: Dictionary mapping need names to modifiers
            
        Returns:
            Modified needs
        """
        # Convert to dictionary for easier modification
        needs_dict = base_needs.dict()
        
        # Apply modifiers
        for need, modifier in modifiers.items():
            if need in needs_dict:
                needs_dict[need] *= modifier
        
        # Create new needs object
        return NpcNeeds(**needs_dict)