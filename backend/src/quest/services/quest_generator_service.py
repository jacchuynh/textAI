"""
Quest Generator Service

This module provides a service for generating dynamic quests based on
the state of the game world, NPC characteristics, economic conditions,
and other factors.
"""

import random
import logging
import json
import os
import string
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

# Import models
from backend.src.quest.models.pydantic_models import (
    QuestData, QuestTemplate, QuestObjective, QuestGenerationContext,
    QuestStatus, QuestType, ObjectiveType, QuestReward, QuestPrerequisite,
    QuestFailureCondition
)
from backend.src.quest.models.db_models import DBQuest, DBQuestTemplate
from backend.src.quest.crud import (
    create_quest, get_quest, get_quests, get_quest_template, get_quest_templates,
    get_quest_templates_by_type, update_quest, delete_quest
)

# Import integration with other systems (in a real implementation)
# from backend.src.npc.models.pydantic_models import NpcData
# from backend.src.npc.models.db_models import DBNpc
# from backend.src.npc.crud import get_npc, get_npcs_by_location, get_npcs_by_role
# from backend.src.economy.models.db_models import DBItem, DBLocation, DBFaction
# from backend.src.economy.services.economy_service import EconomyService

# Import event bus for handling events
# from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class QuestGeneratorService:
    """
    Service for generating dynamic quests based on various parameters and world state.
    """
    
    def __init__(self, templates_dir: str = "data/quest_generator/templates"):
        """
        Initialize the Quest Generator Service.
        
        Args:
            templates_dir: Directory containing quest templates data files
        """
        self.logger = logging.getLogger("QuestGeneratorService")
        self.templates_dir = templates_dir
        
        # Load quest template data
        self.template_data = self._load_template_data()
        
        # Initialize integration services (if needed)
        # self.economy_service = EconomyService()
        # self.event_bus = get_event_bus()
        
        # Subscribe to events that might trigger quest generation
        # self.event_bus.subscribe("world_event_triggered", self._handle_world_event)
        # self.event_bus.subscribe("npc_location_changed", self._handle_npc_movement)
        # self.event_bus.subscribe("economic_event", self._handle_economic_event)
        
        self.logger.info("Quest Generator Service initialized")
    
    def _load_template_data(self) -> Dict[str, Any]:
        """
        Load quest template data from JSON files.
        
        Returns:
            Dictionary of template data
        """
        template_data = {}
        
        # Create directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Check if templates directory exists and has files
        if not os.path.exists(self.templates_dir) or not os.listdir(self.templates_dir):
            self.logger.warning(f"Template directory {self.templates_dir} not found or empty, using default templates")
            template_data = self._create_default_templates()
        else:
            # Load all template files
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(self.templates_dir, filename), 'r', encoding='utf-8') as f:
                            templates = json.load(f)
                            for template in templates:
                                template_id = template.get('id')
                                if template_id:
                                    template_data[template_id] = template
                    except Exception as e:
                        self.logger.error(f"Error loading template file {filename}: {e}")
        
        # If no templates were loaded, create defaults
        if not template_data:
            template_data = self._create_default_templates()
        
        return template_data
    
    def _create_default_templates(self) -> Dict[str, Any]:
        """
        Create default quest templates.
        
        Returns:
            Dictionary of default template data
        """
        default_templates = {}
        
        # Fetch Item Quest Template
        fetch_item_template = {
            "id": "template-fetch-item",
            "name": "Fetch Item Quest",
            "quest_type": QuestType.FETCH_ITEM,
            "title_format": "Retrieve the {item_name}",
            "description_format": "{quest_giver_name} has asked you to retrieve {item_name} from {location_name}. {additional_context}",
            "objective_templates": [
                {
                    "type": ObjectiveType.REACH_LOCATION,
                    "description_format": "Go to {location_name}",
                    "order": 1
                },
                {
                    "type": ObjectiveType.ACQUIRE_ITEM,
                    "description_format": "Find and retrieve {item_name}",
                    "required_quantity": 1,
                    "order": 2
                },
                {
                    "type": ObjectiveType.INTERACT_NPC,
                    "description_format": "Return to {quest_giver_name}",
                    "order": 3
                }
            ],
            "reward_ranges": {
                "currency": (10, 50),
                "experience": (50, 100),
                "item_chance": 0.3
            },
            "potential_failure_conditions": [
                {
                    "type": "time_expires",
                    "description_format": "You failed to retrieve {item_name} in time."
                }
            ],
            "difficulty_range": (1, 3),
            "suitable_locations": ["cave", "dungeon", "forest", "ruins"],
            "suitable_npcs": ["villager", "merchant", "guard", "noble"],
            "required_npc_count": 1,
            "required_location_count": 1,
            "required_items": ["quest_item", "valuable_item"],
            "parameter_selection_rules": {
                "item_selection": "random_from_type",
                "location_selection": "nearest_to_quest_giver"
            }
        }
        default_templates[fetch_item_template["id"]] = fetch_item_template
        
        # Deliver Item Quest Template
        deliver_item_template = {
            "id": "template-deliver-item",
            "name": "Deliver Item Quest",
            "quest_type": QuestType.DELIVER_ITEM,
            "title_format": "Deliver {item_name} to {target_npc_name}",
            "description_format": "{quest_giver_name} has asked you to deliver {item_name} to {target_npc_name} at {location_name}. {additional_context}",
            "objective_templates": [
                {
                    "type": ObjectiveType.ACQUIRE_ITEM,
                    "description_format": "Receive {item_name} from {quest_giver_name}",
                    "required_quantity": 1,
                    "order": 1
                },
                {
                    "type": ObjectiveType.REACH_LOCATION,
                    "description_format": "Travel to {location_name}",
                    "order": 2
                },
                {
                    "type": ObjectiveType.DELIVER_ITEM,
                    "description_format": "Give {item_name} to {target_npc_name}",
                    "required_quantity": 1,
                    "order": 3
                }
            ],
            "reward_ranges": {
                "currency": (15, 40),
                "experience": (40, 80),
                "reputation_change": (5, 10)
            },
            "potential_failure_conditions": [
                {
                    "type": "item_lost",
                    "description_format": "You lost {item_name} and failed the delivery."
                },
                {
                    "type": "time_expires",
                    "description_format": "You failed to deliver {item_name} in time."
                }
            ],
            "difficulty_range": (1, 2),
            "suitable_locations": ["town", "village", "city", "outpost"],
            "suitable_npcs": ["merchant", "villager", "noble", "scholar"],
            "required_npc_count": 2,  # Quest giver and recipient
            "required_location_count": 1,
            "required_items": ["letter", "package", "supplies", "medicine"],
            "parameter_selection_rules": {
                "target_npc_selection": "different_location_from_quest_giver"
            }
        }
        default_templates[deliver_item_template["id"]] = deliver_item_template
        
        # Add a few more templates
        # Slay Creatures Template
        slay_creatures_template = {
            "id": "template-slay-creatures",
            "name": "Slay Creatures Quest",
            "quest_type": QuestType.SLAY_CREATURES,
            "title_format": "Defeat the {creature_name}s",
            "description_format": "{quest_giver_name} has asked you to clear out some {creature_name}s that have been causing trouble near {location_name}. {additional_context}",
            "objective_templates": [
                {
                    "type": ObjectiveType.REACH_LOCATION,
                    "description_format": "Go to {location_name}",
                    "order": 1
                },
                {
                    "type": ObjectiveType.DEFEAT_TARGET,
                    "description_format": "Defeat {required_quantity} {creature_name}s",
                    "required_quantity": "{creature_count}",
                    "order": 2
                },
                {
                    "type": ObjectiveType.INTERACT_NPC,
                    "description_format": "Return to {quest_giver_name} for your reward",
                    "order": 3
                }
            ],
            "reward_ranges": {
                "currency": (30, 100),
                "experience": (80, 150),
                "item_chance": 0.5
            },
            "potential_failure_conditions": [],
            "difficulty_range": (2, 5),
            "suitable_locations": ["forest", "cave", "dungeon", "mountains", "swamp"],
            "suitable_npcs": ["guard", "hunter", "villager", "farmer"],
            "required_npc_count": 1,
            "required_location_count": 1,
            "required_items": [],
            "parameter_selection_rules": {
                "creature_count": (3, 10)
            }
        }
        default_templates[slay_creatures_template["id"]] = slay_creatures_template
        
        # Economic Opportunity Template
        economic_template = {
            "id": "template-economic-opportunity",
            "name": "Economic Opportunity Quest",
            "quest_type": QuestType.ECONOMIC_OPPORTUNITY,
            "title_format": "Market Opportunity: {resource_name}",
            "description_format": "There's a shortage of {resource_name} in {location_name}, creating a profitable opportunity for trade. {additional_context}",
            "objective_templates": [
                {
                    "type": ObjectiveType.ACQUIRE_ITEM,
                    "description_format": "Acquire {required_quantity} {resource_name}",
                    "required_quantity": "{resource_count}",
                    "order": 1
                },
                {
                    "type": ObjectiveType.REACH_LOCATION,
                    "description_format": "Bring the {resource_name} to {location_name}",
                    "order": 2
                },
                {
                    "type": ObjectiveType.INTERACT_NPC,
                    "description_format": "Sell the {resource_name} to {target_npc_name}",
                    "order": 3
                }
            ],
            "reward_ranges": {
                "currency": (50, 200),
                "experience": (30, 60),
                "reputation_change": (2, 5)
            },
            "potential_failure_conditions": [
                {
                    "type": "market_changes",
                    "description_format": "The market for {resource_name} crashed before you could complete the trade."
                }
            ],
            "difficulty_range": (2, 4),
            "suitable_locations": ["town", "city", "trading_post", "market"],
            "suitable_npcs": ["merchant", "trader", "shopkeeper", "craftsman"],
            "required_npc_count": 1,
            "required_location_count": 1,
            "required_items": ["trade_goods", "resources", "crafting_materials"],
            "parameter_selection_rules": {
                "resource_count": (5, 20)
            }
        }
        default_templates[economic_template["id"]] = economic_template
        
        # Save default templates to files
        try:
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # Group templates by type
            template_by_type = {}
            for template_id, template in default_templates.items():
                quest_type = template["quest_type"]
                if quest_type not in template_by_type:
                    template_by_type[quest_type] = []
                template_by_type[quest_type].append(template)
            
            # Save each type to a separate file
            for quest_type, templates in template_by_type.items():
                filename = os.path.join(self.templates_dir, f"{quest_type.lower()}_templates.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, indent=2)
            
            self.logger.info(f"Default templates saved to {self.templates_dir}")
        except Exception as e:
            self.logger.error(f"Error saving default templates: {e}")
        
        return default_templates
    
    def _load_template_from_db(self, db: Session, template_id: str) -> Optional[QuestTemplate]:
        """
        Load a quest template from the database.
        
        Args:
            db: Database session
            template_id: Template identifier
            
        Returns:
            Quest template or None if not found
        """
        db_template = get_quest_template(db, template_id)
        if not db_template:
            return None
        
        # Convert SQLAlchemy model to Pydantic model
        template = QuestTemplate(
            id=db_template.id,
            name=db_template.name,
            quest_type=db_template.quest_type,
            title_format=db_template.title_format,
            description_format=db_template.description_format,
            objective_templates=db_template.objective_templates,
            reward_ranges=db_template.reward_ranges,
            potential_failure_conditions=db_template.potential_failure_conditions,
            difficulty_range=db_template.difficulty_range,
            suitable_locations=db_template.suitable_locations,
            suitable_npcs=db_template.suitable_npcs,
            required_npc_count=db_template.required_npc_count,
            required_location_count=db_template.required_location_count,
            required_items=db_template.required_items,
            parameter_selection_rules=db_template.parameter_selection_rules,
            common_prerequisites=db_template.common_prerequisites,
            cooldown_hours=db_template.cooldown_hours,
            default_time_limit_hours=db_template.default_time_limit_hours,
            suitable_factions=db_template.suitable_factions,
            tags=db_template.tags,
            custom_data=db_template.custom_data
        )
        
        return template
    
    def generate_quest(self, 
                     db: Session, 
                     generation_context: QuestGenerationContext) -> Optional[DBQuest]:
        """
        Generate a new quest based on the provided context.
        
        Args:
            db: Database session
            generation_context: Context for quest generation
            
        Returns:
            Generated quest database object or None if generation failed
        """
        self.logger.info(f"Generating quest with context: {generation_context.dict()}")
        
        try:
            # Select an appropriate template
            template = self._select_template(db, generation_context)
            if not template:
                self.logger.error("Failed to select an appropriate quest template")
                return None
            
            # Gather parameters for the quest
            quest_params = self._gather_quest_parameters(db, template, generation_context)
            
            # Generate quest data
            quest_data = self._generate_quest_from_template(template, quest_params)
            
            # Create the quest in the database
            db_quest = create_quest(db, quest_data)
            
            # Publish event
            # self.event_bus.publish(Event(
            #     event_type="quest_generated",
            #     data={
            #         "quest_id": db_quest.id,
            #         "quest_type": str(db_quest.quest_type),
            #         "difficulty": db_quest.difficulty,
            #         "triggering_context": generation_context.dict(),
            #         "timestamp": datetime.utcnow().isoformat()
            #     },
            #     source="quest_generator_service"
            # ))
            
            self.logger.info(f"Generated quest: {db_quest.title} ({db_quest.id})")
            return db_quest
        except Exception as e:
            self.logger.error(f"Error generating quest: {e}")
            return None
    
    def generate_quests_for_location(self, 
                                  db: Session, 
                                  location_id: str,
                                  count: int = 3,
                                  difficulty_range: Tuple[int, int] = (1, 5),
                                  quest_types: Optional[List[QuestType]] = None) -> List[DBQuest]:
        """
        Generate multiple quests for a specific location.
        
        Args:
            db: Database session
            location_id: Location identifier
            count: Number of quests to generate
            difficulty_range: Min and max difficulty level
            quest_types: Optional list of quest types to generate
            
        Returns:
            List of generated quest database objects
        """
        self.logger.info(f"Generating {count} quests for location {location_id}")
        
        generated_quests = []
        
        # In a real implementation, we would get location details
        # location = db.query(DBLocation).filter(DBLocation.id == location_id).first()
        # if not location:
        #     self.logger.warning(f"Location {location_id} not found")
        #     return []
        
        # Get NPCs at this location (in a real implementation)
        # npcs = get_npcs_by_location(db, location_id)
        
        # Simulate NPCs for this example
        npcs = [
            {"id": f"npc-{uuid4().hex[:8]}", "name": f"NPC {i}", "economic_role": random.choice(["SHOPKEEPER", "MERCHANT", "GUARD", "VILLAGER"])}
            for i in range(1, 6)
        ]
        
        # Generate quests
        for i in range(count):
            try:
                # Select a random NPC as quest giver
                quest_giver = random.choice(npcs) if npcs else None
                
                # Create generation context
                context = QuestGenerationContext(
                    triggering_location_id=location_id,
                    triggering_npc_id=quest_giver["id"] if quest_giver else None,
                    desired_difficulty=random.randint(difficulty_range[0], difficulty_range[1]),
                    desired_quest_type=random.choice(quest_types) if quest_types else None,
                    generation_reason=f"location_quest_generation_{location_id}"
                )
                
                # Generate quest
                quest = self.generate_quest(db, context)
                if quest:
                    generated_quests.append(quest)
            except Exception as e:
                self.logger.error(f"Error generating quest for location {location_id}: {e}")
        
        return generated_quests
    
    def generate_quests_for_npc(self, 
                             db: Session, 
                             npc_id: str,
                             count: int = 2,
                             quest_types: Optional[List[QuestType]] = None) -> List[DBQuest]:
        """
        Generate quests for a specific NPC.
        
        Args:
            db: Database session
            npc_id: NPC identifier
            count: Number of quests to generate
            quest_types: Optional list of quest types to generate
            
        Returns:
            List of generated quest database objects
        """
        self.logger.info(f"Generating {count} quests for NPC {npc_id}")
        
        # In a real implementation, we would get NPC details
        # npc = get_npc(db, npc_id)
        # if not npc:
        #     self.logger.warning(f"NPC {npc_id} not found")
        #     return []
        
        # Simulate NPC for this example
        npc = {
            "id": npc_id,
            "name": f"NPC {npc_id[-4:]}",
            "economic_role": random.choice(["SHOPKEEPER", "MERCHANT", "GUARD", "VILLAGER"]),
            "current_location_id": f"location-{uuid4().hex[:8]}"
        }
        
        # Determine suitable quest types based on NPC role (in a real implementation)
        if not quest_types:
            role_to_quest_types = {
                "SHOPKEEPER": [QuestType.FETCH_ITEM, QuestType.DELIVER_ITEM, QuestType.ECONOMIC_OPPORTUNITY],
                "MERCHANT": [QuestType.DELIVER_ITEM, QuestType.ECONOMIC_OPPORTUNITY, QuestType.FACTION_TASK],
                "GUARD": [QuestType.PROTECT_LOCATION, QuestType.SLAY_CREATURES, QuestType.CLEAR_LOCATION],
                "VILLAGER": [QuestType.FETCH_ITEM, QuestType.GATHER_RESOURCE, QuestType.HELP_NPC]
            }
            quest_types = role_to_quest_types.get(npc["economic_role"], [QuestType.FETCH_ITEM, QuestType.DELIVER_ITEM])
        
        generated_quests = []
        
        # Generate quests
        for i in range(count):
            try:
                # Create generation context
                context = QuestGenerationContext(
                    triggering_npc_id=npc_id,
                    triggering_location_id=npc["current_location_id"],
                    desired_quest_type=random.choice(quest_types),
                    generation_reason=f"npc_quest_generation_{npc_id}"
                )
                
                # Generate quest
                quest = self.generate_quest(db, context)
                if quest:
                    generated_quests.append(quest)
            except Exception as e:
                self.logger.error(f"Error generating quest for NPC {npc_id}: {e}")
        
        return generated_quests
    
    def generate_economic_opportunity_quest(self, 
                                         db: Session, 
                                         economic_event: Dict[str, Any],
                                         location_id: str) -> Optional[DBQuest]:
        """
        Generate an economic opportunity quest based on an economic event.
        
        Args:
            db: Database session
            economic_event: Dictionary describing the economic event
            location_id: Location identifier
            
        Returns:
            Generated quest database object or None if generation failed
        """
        self.logger.info(f"Generating economic opportunity quest for event: {economic_event}")
        
        try:
            # Create generation context
            context = QuestGenerationContext(
                triggering_location_id=location_id,
                triggering_economic_event=economic_event,
                desired_quest_type=QuestType.ECONOMIC_OPPORTUNITY,
                generation_reason="economic_event_response"
            )
            
            # Generate quest
            return self.generate_quest(db, context)
        except Exception as e:
            self.logger.error(f"Error generating economic quest: {e}")
            return None
    
    def generate_faction_task(self, 
                           db: Session, 
                           faction_id: str,
                           difficulty: int = 3) -> Optional[DBQuest]:
        """
        Generate a faction-specific task.
        
        Args:
            db: Database session
            faction_id: Faction identifier
            difficulty: Desired difficulty level
            
        Returns:
            Generated quest database object or None if generation failed
        """
        self.logger.info(f"Generating faction task for faction {faction_id}")
        
        try:
            # In a real implementation, we would get faction details
            # faction = db.query(DBFaction).filter(DBFaction.id == faction_id).first()
            # if not faction:
            #     self.logger.warning(f"Faction {faction_id} not found")
            #     return None
            
            # Create generation context
            context = QuestGenerationContext(
                associated_faction_id=faction_id,
                desired_quest_type=QuestType.FACTION_TASK,
                desired_difficulty=difficulty,
                generation_reason="faction_task_generation"
            )
            
            # Generate quest
            return self.generate_quest(db, context)
        except Exception as e:
            self.logger.error(f"Error generating faction task: {e}")
            return None
    
    def _select_template(self, 
                       db: Session, 
                       context: QuestGenerationContext) -> Optional[QuestTemplate]:
        """
        Select an appropriate quest template based on the generation context.
        
        Args:
            db: Database session
            context: Generation context
            
        Returns:
            Selected quest template or None if selection failed
        """
        # First, check if a specific quest type is desired
        if context.desired_quest_type:
            # Check if we have this template in the database
            db_templates = get_quest_templates_by_type(db, context.desired_quest_type)
            if db_templates:
                # Choose a random template of the desired type
                db_template = random.choice(db_templates)
                return self._load_template_from_db(db, db_template.id)
            
            # If not in the database, check our memory cache
            type_templates = [t for t in self.template_data.values() 
                             if t.get('quest_type') == context.desired_quest_type]
            if type_templates:
                template_data = random.choice(type_templates)
                return self._convert_dict_to_template(template_data)
        
        # If no specific type is desired or no matching template was found,
        # select based on other context factors
        
        # Check if triggered by an NPC
        if context.triggering_npc_id:
            # In a real implementation, we would get NPC details and find suitable templates
            # npc = get_npc(db, context.triggering_npc_id)
            # if npc:
            #     suitable_templates = self._get_templates_suitable_for_npc(db, npc)
            #     if suitable_templates:
            #         return random.choice(suitable_templates)
            
            # For this example, we'll just return a random template
            all_templates = list(self.template_data.values())
            template_data = random.choice(all_templates)
            return self._convert_dict_to_template(template_data)
        
        # Check if triggered by an economic event
        if context.triggering_economic_event:
            # Try to find an economic opportunity template
            db_templates = get_quest_templates_by_type(db, QuestType.ECONOMIC_OPPORTUNITY)
            if db_templates:
                db_template = random.choice(db_templates)
                return self._load_template_from_db(db, db_template.id)
            
            # If not in the database, check our memory cache
            type_templates = [t for t in self.template_data.values() 
                             if t.get('quest_type') == QuestType.ECONOMIC_OPPORTUNITY]
            if type_templates:
                template_data = random.choice(type_templates)
                return self._convert_dict_to_template(template_data)
        
        # Default: pick a random template
        all_templates = list(self.template_data.values())
        if not all_templates:
            return None
        
        template_data = random.choice(all_templates)
        return self._convert_dict_to_template(template_data)
    
    def _convert_dict_to_template(self, template_dict: Dict[str, Any]) -> QuestTemplate:
        """
        Convert a dictionary to a QuestTemplate object.
        
        Args:
            template_dict: Template dictionary
            
        Returns:
            QuestTemplate object
        """
        # Handle any type conversion needed
        if 'quest_type' in template_dict and isinstance(template_dict['quest_type'], str):
            template_dict['quest_type'] = QuestType(template_dict['quest_type'])
        
        # Convert the dictionary to a QuestTemplate
        return QuestTemplate(**template_dict)
    
    def _gather_quest_parameters(self, 
                               db: Session, 
                               template: QuestTemplate, 
                               context: QuestGenerationContext) -> Dict[str, Any]:
        """
        Gather parameters needed to fill in the template.
        
        Args:
            db: Database session
            template: Quest template
            context: Generation context
            
        Returns:
            Dictionary of parameters
        """
        params = {}
        
        # Add basic parameters
        params["quest_id"] = f"quest-{uuid4().hex}"
        params["template_id"] = template.id
        
        # Add difficulty
        if context.desired_difficulty:
            params["difficulty"] = context.desired_difficulty
        else:
            params["difficulty"] = random.randint(template.difficulty_range[0], template.difficulty_range[1])
        
        # Add quest giver NPC
        if context.triggering_npc_id:
            params["quest_giver_npc_id"] = context.triggering_npc_id
            
            # In a real implementation, we would get NPC details
            # npc = get_npc(db, context.triggering_npc_id)
            # if npc:
            #     params["quest_giver_name"] = npc.name
            
            # For this example, we'll use a placeholder
            params["quest_giver_name"] = f"NPC {context.triggering_npc_id[-4:]}"
        else:
            # If no triggering NPC, we might need to find or generate one
            params["quest_giver_npc_id"] = f"npc-{uuid4().hex[:8]}"
            params["quest_giver_name"] = self._generate_random_name()
        
        # Add location information
        if context.triggering_location_id:
            params["location_id"] = context.triggering_location_id
            
            # In a real implementation, we would get location details
            # location = db.query(DBLocation).filter(DBLocation.id == context.triggering_location_id).first()
            # if location:
            #     params["location_name"] = location.name
            
            # For this example, we'll use a placeholder
            params["location_name"] = f"Location {context.triggering_location_id[-4:]}"
        else:
            # If no triggering location, we might need to find or generate one
            params["location_id"] = f"location-{uuid4().hex[:8]}"
            params["location_name"] = self._generate_random_location_name()
        
        # For fetch/deliver item quests, add item information
        if template.quest_type in [QuestType.FETCH_ITEM, QuestType.DELIVER_ITEM, QuestType.ECONOMIC_OPPORTUNITY]:
            # In a real implementation, we would select an appropriate item
            # items = db.query(DBItem).all()
            # if items:
            #     item = random.choice(items)
            #     params["item_id"] = item.id
            #     params["item_name"] = item.name
            
            # For this example, we'll use a placeholder
            params["item_id"] = f"item-{uuid4().hex[:8]}"
            
            if template.quest_type == QuestType.ECONOMIC_OPPORTUNITY:
                params["item_name"] = params["resource_name"] = self._generate_random_resource_name()
                
                # If we have economic event data, use it
                if context.triggering_economic_event:
                    event = context.triggering_economic_event
                    if "resource_id" in event:
                        params["item_id"] = event["resource_id"]
                    if "resource_name" in event:
                        params["item_name"] = params["resource_name"] = event["resource_name"]
                    if "quantity" in event:
                        params["resource_count"] = event["quantity"]
                    else:
                        params["resource_count"] = random.randint(5, 20)
            else:
                params["item_name"] = self._generate_random_item_name()
        
        # For slay creatures quests, add creature information
        if template.quest_type == QuestType.SLAY_CREATURES:
            params["creature_name"] = self._generate_random_creature_name()
            params["creature_count"] = random.randint(3, 10)
        
        # For quests that need a target NPC (delivery, escort, etc.)
        if template.quest_type in [QuestType.DELIVER_ITEM, QuestType.ESCORT_NPC, QuestType.PERSUADE_NPC]:
            # In a real implementation, we would select an appropriate NPC
            # npcs = get_npcs_by_location(db, params["location_id"])
            # if npcs:
            #     target_npc = random.choice(npcs)
            #     params["target_npc_id"] = target_npc.id
            #     params["target_npc_name"] = target_npc.name
            
            # For this example, we'll use a placeholder
            params["target_npc_id"] = f"npc-{uuid4().hex[:8]}"
            params["target_npc_name"] = self._generate_random_name()
        
        # Add faction information if needed
        if context.associated_faction_id:
            params["faction_id"] = context.associated_faction_id
            
            # In a real implementation, we would get faction details
            # faction = db.query(DBFaction).filter(DBFaction.id == context.associated_faction_id).first()
            # if faction:
            #     params["faction_name"] = faction.name
            
            # For this example, we'll use a placeholder
            params["faction_name"] = f"Faction {context.associated_faction_id[-4:]}"
        
        # Generate additional context text
        params["additional_context"] = self._generate_additional_context(template.quest_type, params)
        
        return params
    
    def _generate_quest_from_template(self, 
                                    template: QuestTemplate, 
                                    params: Dict[str, Any]) -> QuestData:
        """
        Generate a quest using the template and parameters.
        
        Args:
            template: Quest template
            params: Parameters for the template
            
        Returns:
            Generated quest data
        """
        # Generate title and descriptions
        title = self._format_string(template.title_format, params)
        description_template = template.description_format
        generated_description = self._format_string(description_template, params)
        
        # Generate objectives
        objectives = []
        for obj_template in template.objective_templates:
            objective = self._generate_objective_from_template(obj_template, params)
            objectives.append(objective)
        
        # Generate rewards
        rewards = self._generate_rewards(template.reward_ranges, params)
        
        # Generate failure conditions
        failure_conditions = []
        for fc_template in template.potential_failure_conditions:
            failure_condition = self._generate_failure_condition(fc_template, params)
            failure_conditions.append(failure_condition)
        
        # Generate prerequisites (if any)
        prerequisites = []
        if hasattr(template, 'common_prerequisites') and template.common_prerequisites:
            for prereq_template in template.common_prerequisites:
                prerequisite = self._generate_prerequisite(prereq_template, params)
                prerequisites.append(prerequisite)
        
        # Create quest data
        quest_data = QuestData(
            id=params["quest_id"],
            title=title,
            description_template=description_template,
            generated_description=generated_description,
            quest_type=template.quest_type,
            status=QuestStatus.AVAILABLE,
            difficulty=params["difficulty"],
            objectives=objectives,
            rewards=rewards,
            failure_conditions=failure_conditions,
            quest_giver_npc_id=params.get("quest_giver_npc_id"),
            target_npc_ids=[params.get("target_npc_id")] if "target_npc_id" in params else [],
            related_location_ids=[params.get("location_id")] if "location_id" in params else [],
            prerequisites=prerequisites,
            time_limit_seconds=template.default_time_limit_hours * 3600 if template.default_time_limit_hours else None,
            is_repeatable=False,  # Default to non-repeatable
            cooldown_hours=template.cooldown_hours,
            template_id=template.id,
            associated_faction_id=params.get("faction_id"),
            tags=template.tags,
            custom_data={"generation_params": params}
        )
        
        return quest_data
    
    def _generate_objective_from_template(self, 
                                       objective_template: Dict[str, Any], 
                                       params: Dict[str, Any]) -> QuestObjective:
        """
        Generate an objective from a template.
        
        Args:
            objective_template: Objective template
            params: Parameters for the template
            
        Returns:
            Generated objective
        """
        # Get objective type
        obj_type = ObjectiveType(objective_template["type"]) if isinstance(objective_template["type"], str) else objective_template["type"]
        
        # Format description
        description = self._format_string(objective_template["description_format"], params)
        
        # Determine required quantity
        required_quantity = 1
        if "required_quantity" in objective_template:
            if isinstance(objective_template["required_quantity"], str):
                # This might be a parameter reference like "{creature_count}"
                required_quantity = params.get(objective_template["required_quantity"].strip("{}"), 1)
            else:
                required_quantity = objective_template["required_quantity"]
        
        # Create objective
        objective = QuestObjective(
            id=f"objective-{uuid4().hex[:8]}",
            description=description,
            type=obj_type,
            target_id=params.get("item_id" if obj_type in [ObjectiveType.ACQUIRE_ITEM, ObjectiveType.DELIVER_ITEM] else 
                                 "target_npc_id" if obj_type in [ObjectiveType.INTERACT_NPC, ObjectiveType.PERSUADE_NPC] else
                                 "location_id" if obj_type == ObjectiveType.REACH_LOCATION else None),
            target_name=params.get("item_name" if obj_type in [ObjectiveType.ACQUIRE_ITEM, ObjectiveType.DELIVER_ITEM] else 
                                   "target_npc_name" if obj_type in [ObjectiveType.INTERACT_NPC, ObjectiveType.PERSUADE_NPC] else
                                   "location_name" if obj_type == ObjectiveType.REACH_LOCATION else
                                   "creature_name" if obj_type == ObjectiveType.DEFEAT_TARGET else None),
            required_quantity=required_quantity,
            current_quantity=0,
            is_completed=False,
            order=objective_template.get("order", None),
            optional=objective_template.get("optional", False),
            hidden=objective_template.get("hidden", False),
            completion_text=None  # Could be generated if needed
        )
        
        return objective
    
    def _generate_rewards(self, 
                       reward_ranges: Dict[str, Any], 
                       params: Dict[str, Any]) -> QuestReward:
        """
        Generate rewards for a quest.
        
        Args:
            reward_ranges: Reward range specifications
            params: Quest parameters
            
        Returns:
            Generated rewards
        """
        # Determine currency reward
        currency = 0.0
        if "currency" in reward_ranges:
            min_currency, max_currency = reward_ranges["currency"]
            currency = round(random.uniform(min_currency, max_currency), 2)
            
            # Scale by difficulty if applicable
            if "difficulty" in params:
                difficulty_multiplier = params["difficulty"] / 5.0  # Normalize to 0.2-2.0 range for difficulty 1-10
                currency *= (1.0 + difficulty_multiplier)
        
        # Determine experience reward
        experience = None
        if "experience" in reward_ranges:
            min_exp, max_exp = reward_ranges["experience"]
            experience = random.randint(min_exp, max_exp)
            
            # Scale by difficulty if applicable
            if "difficulty" in params:
                difficulty_multiplier = params["difficulty"] / 5.0
                experience = int(experience * (1.0 + difficulty_multiplier))
        
        # Determine item rewards
        items = {}
        if "item_chance" in reward_ranges and random.random() < reward_ranges["item_chance"]:
            # In a real implementation, we would select appropriate reward items
            # For this example, we'll generate a random reward item
            item_id = f"reward-item-{uuid4().hex[:8]}"
            item_name = self._generate_random_reward_item_name()
            
            items[item_id] = {
                "quantity": random.randint(1, 3),
                "name": item_name,
                "quality": random.choice(["common", "uncommon", "rare"])
            }
        
        # Determine reputation changes
        reputation_changes = {}
        if "reputation_change" in reward_ranges:
            min_rep, max_rep = reward_ranges["reputation_change"]
            
            # Add reputation with quest giver's faction if applicable
            if "faction_id" in params:
                reputation_changes[params["faction_id"]] = random.uniform(min_rep, max_rep)
            
            # Could also add reputation with the quest giver NPC
            if "quest_giver_npc_id" in params:
                reputation_changes[params["quest_giver_npc_id"]] = random.uniform(min_rep, max_rep)
        
        # Create reward object
        reward = QuestReward(
            currency=currency,
            items=items,
            experience_points=experience,
            reputation_changes=reputation_changes,
            skill_experience={},  # Could be filled if needed
            unlocked_quests=[],  # Could be filled if needed
            unlocked_locations=[],  # Could be filled if needed
            unlocked_items=[]  # Could be filled if needed
        )
        
        return reward
    
    def _generate_failure_condition(self, 
                                 fc_template: Dict[str, Any], 
                                 params: Dict[str, Any]) -> QuestFailureCondition:
        """
        Generate a failure condition.
        
        Args:
            fc_template: Failure condition template
            params: Parameters for the template
            
        Returns:
            Generated failure condition
        """
        # Format description
        description = self._format_string(fc_template["description_format"], params)
        
        # Determine target ID based on failure type
        target_id = None
        if fc_template["type"] == "npc_dies" and "target_npc_id" in params:
            target_id = params["target_npc_id"]
        elif fc_template["type"] == "item_lost" and "item_id" in params:
            target_id = params["item_id"]
        
        # Create failure condition
        failure_condition = QuestFailureCondition(
            type=fc_template["type"],
            target_id=target_id,
            description=description,
            custom_data={}  # Could be filled if needed
        )
        
        return failure_condition
    
    def _generate_prerequisite(self, 
                            prereq_template: Dict[str, Any], 
                            params: Dict[str, Any]) -> QuestPrerequisite:
        """
        Generate a prerequisite condition.
        
        Args:
            prereq_template: Prerequisite template
            params: Quest parameters
            
        Returns:
            Generated prerequisite
        """
        # Create prerequisite
        prerequisite = QuestPrerequisite(
            type=prereq_template["type"],
            value=prereq_template["value"],
            comparator=prereq_template.get("comparator", ">="),
            custom_data={}  # Could be filled if needed
        )
        
        return prerequisite
    
    def _format_string(self, format_string: str, params: Dict[str, Any]) -> str:
        """
        Format a string by replacing placeholders with parameter values.
        
        Args:
            format_string: String with placeholders
            params: Parameter values
            
        Returns:
            Formatted string
        """
        try:
            # Replace placeholders using string formatting
            return format_string.format(**params)
        except KeyError as e:
            # If a key is missing, use a generic replacement
            self.logger.warning(f"Missing parameter for placeholder {e} in format string")
            
            # Replace the missing placeholder with a generic value
            missing_key = str(e).strip("'")
            generic_value = self._generate_generic_value(missing_key)
            params[missing_key] = generic_value
            
            # Try again with the added generic value
            return self._format_string(format_string, params)
    
    def _generate_generic_value(self, key: str) -> str:
        """
        Generate a generic value for a missing parameter.
        
        Args:
            key: Parameter key
            
        Returns:
            Generic value
        """
        if "name" in key.lower():
            if "item" in key.lower():
                return self._generate_random_item_name()
            elif "location" in key.lower():
                return self._generate_random_location_name()
            elif "npc" in key.lower() or "character" in key.lower():
                return self._generate_random_name()
            else:
                return f"Mysterious {key.title()}"
        elif "count" in key.lower() or "quantity" in key.lower():
            return str(random.randint(1, 10))
        else:
            return f"Unknown {key.replace('_', ' ').title()}"
    
    def _generate_random_name(self) -> str:
        """
        Generate a random NPC name.
        
        Returns:
            Random name
        """
        first_names = ["Aldric", "Brenna", "Cedric", "Doria", "Elwin", "Fiona", "Gareth", "Hilda", "Ingmar", "Jonna"]
        last_names = ["Ironheart", "Silverleaf", "Thunderforge", "Nightshade", "Stormcloak", "Goldenhand", "Blackthorn"]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_random_location_name(self) -> str:
        """
        Generate a random location name.
        
        Returns:
            Random location name
        """
        prefixes = ["Dark", "Misty", "Ancient", "Hidden", "Forgotten", "Cursed", "Sacred", "Silent", "Golden", "Crimson"]
        locations = ["Forest", "Cave", "Ruins", "Valley", "Mountain", "Temple", "Tower", "Village", "Castle", "Swamp"]
        
        return f"{random.choice(prefixes)} {random.choice(locations)}"
    
    def _generate_random_item_name(self) -> str:
        """
        Generate a random item name.
        
        Returns:
            Random item name
        """
        adjectives = ["Ancient", "Rusty", "Enchanted", "Cursed", "Mysterious", "Forgotten", "Sacred", "Broken", "Glowing"]
        items = ["Amulet", "Sword", "Map", "Key", "Scroll", "Gem", "Ring", "Book", "Artifact", "Pendant"]
        
        return f"{random.choice(adjectives)} {random.choice(items)}"
    
    def _generate_random_reward_item_name(self) -> str:
        """
        Generate a random reward item name.
        
        Returns:
            Random reward item name
        """
        qualities = ["Fine", "Superior", "Exquisite", "Masterwork", "Artisan's", "Expert's", "Flawless"]
        items = ["Blade", "Armor", "Helm", "Shield", "Bow", "Staff", "Robe", "Boots", "Gloves", "Potion"]
        
        return f"{random.choice(qualities)} {random.choice(items)}"
    
    def _generate_random_creature_name(self) -> str:
        """
        Generate a random creature name.
        
        Returns:
            Random creature name
        """
        creatures = ["Wolf", "Goblin", "Bandit", "Troll", "Spider", "Skeleton", "Zombie", "Orc", "Rat", "Bear"]
        
        return random.choice(creatures)
    
    def _generate_random_resource_name(self) -> str:
        """
        Generate a random resource name.
        
        Returns:
            Random resource name
        """
        resources = ["Iron Ore", "Silver Ingot", "Gold Dust", "Mithril Bar", "Oak Wood", "Elven Silk", "Dwarven Steel", 
                     "Healing Herbs", "Mana Crystal", "Dragon Scale", "Phoenix Feather", "Troll Hide"]
        
        return random.choice(resources)
    
    def _generate_additional_context(self, quest_type: QuestType, params: Dict[str, Any]) -> str:
        """
        Generate additional context for the quest description.
        
        Args:
            quest_type: Type of quest
            params: Quest parameters
            
        Returns:
            Additional context text
        """
        context_options = {
            QuestType.FETCH_ITEM: [
                "It's said to be guarded by dangerous creatures.",
                "Legend has it that it holds mysterious powers.",
                "It was lost during a recent attack on a caravan.",
                "It's a family heirloom with great sentimental value.",
                "It contains information vital to the region's safety."
            ],
            QuestType.DELIVER_ITEM: [
                "The contents are sealed and should not be opened.",
                "It must be delivered with utmost haste.",
                "Be careful, as others may try to steal it.",
                "It's extremely fragile and must be handled with care.",
                "The recipient has been waiting anxiously for its arrival."
            ],
            QuestType.SLAY_CREATURES: [
                "They've been terrorizing travelers on the main road.",
                "They've taken over an abandoned mine and are threatening nearby settlements.",
                "They're unnaturally aggressive, possibly under some evil influence.",
                "They carry a rare disease that must be contained.",
                "Their numbers have grown out of control and upset the natural balance."
            ],
            QuestType.ECONOMIC_OPPORTUNITY: [
                "The shortage has caused prices to triple in the last week.",
                "Merchants are offering premium rates for anyone who can supply them.",
                "The local crafters can't continue their work without these materials.",
                "A wealthy noble is paying handsomely to corner the market.",
                "Rival traders are already scrambling to capitalize on the situation."
            ]
        }
        
        # Get context options for this quest type, or use generic ones
        options = context_options.get(quest_type, [
            "Time is of the essence.",
            "Success will be rewarded handsomely.",
            "This task is more important than it might seem at first.",
            "Many have tried and failed before you.",
            "Your reputation would benefit greatly from this task."
        ])
        
        return random.choice(options)