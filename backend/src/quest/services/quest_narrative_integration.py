"""
Quest Narrative Integration Service

This module provides integration between the quest system and the
narrative engine, allowing story events to trigger quests and
quest completion to affect the narrative.
"""

import random
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

# Import quest models and services
from backend.src.quest.models.pydantic_models import (
    QuestData, QuestGenerationContext, QuestType, QuestStatus
)
from backend.src.quest.services.quest_generator_service import QuestGeneratorService
from backend.src.quest.crud import get_quest, update_quest

# Import narrative engine models and services (uncomment in real implementation)
# from backend.src.narrative_engine.models.pydantic_models import StoryEvent, NarrativeContext
# from backend.src.narrative_engine.ai_gm_brain_integrated import AIGMBrain

# Import event bus for handling events
# from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class QuestNarrativeIntegrationService:
    """
    Service for integrating the quest system with the narrative engine.
    """
    
    def __init__(self):
        """Initialize the Quest Narrative Integration Service."""
        self.logger = logging.getLogger("QuestNarrativeIntegrationService")
        
        # Initialize related services
        self.quest_generator = QuestGeneratorService()
        # self.ai_gm_brain = AIGMBrain()
        # self.event_bus = get_event_bus()
        
        # Subscribe to narrative events
        # self.event_bus.subscribe("character_introduced", self._handle_character_introduced)
        # self.event_bus.subscribe("location_discovered", self._handle_location_discovered)
        # self.event_bus.subscribe("faction_conflict", self._handle_faction_conflict)
        # self.event_bus.subscribe("story_milestone", self._handle_story_milestone)
        # self.event_bus.subscribe("world_event", self._handle_world_event)
        # self.event_bus.subscribe("player_decision", self._handle_player_decision)
        
        self.logger.info("Quest Narrative Integration Service initialized")
    
    def generate_story_driven_quest(self, 
                                 db: Session, 
                                 story_event: Dict[str, Any],
                                 player_id: Optional[str] = None) -> Optional[QuestData]:
        """
        Generate a quest based on a narrative story event.
        
        Args:
            db: Database session
            story_event: Story event details
            player_id: Optional player identifier for personalized quests
            
        Returns:
            Generated quest data or None if generation failed
        """
        self.logger.info(f"Generating story-driven quest for event: {story_event.get('event_type', 'unknown')}")
        
        try:
            # Determine quest type based on event type
            event_type = story_event.get("event_type", "")
            quest_type = self._map_event_to_quest_type(event_type)
            
            # Extract location and NPC information
            location_id = story_event.get("location_id")
            npc_id = story_event.get("npc_id")
            
            # Extract narrative context information
            narrative_context = {
                "event_type": event_type,
                "event_importance": story_event.get("importance", 3),
                "related_theme": story_event.get("theme"),
                "related_plot": story_event.get("plot_id"),
                "story_phase": story_event.get("story_phase"),
                "dramatic_tension": story_event.get("tension_level", 5)
            }
            
            # Create generation context
            context = QuestGenerationContext(
                triggering_location_id=location_id,
                triggering_npc_id=npc_id,
                player_character_id=player_id,
                desired_quest_type=quest_type,
                desired_difficulty=story_event.get("suggested_difficulty", 3),
                narrative_context=narrative_context,
                generation_reason=f"story_event_{event_type}"
            )
            
            # Generate quest
            quest = self.quest_generator.generate_quest(db, context)
            
            if quest:
                # Add narrative information to quest custom data
                update_data = {
                    "custom_data": quest.custom_data or {}
                }
                update_data["custom_data"]["narrative_context"] = narrative_context
                update_data["custom_data"]["story_event_id"] = story_event.get("id")
                update_quest(db, quest.id, update_data)
                
                # Publish event
                # self.event_bus.publish(Event(
                #     event_type="narrative_quest_generated",
                #     data={
                #         "quest_id": quest.id,
                #         "story_event_id": story_event.get("id"),
                #         "quest_type": str(quest_type),
                #         "player_id": player_id,
                #         "timestamp": datetime.utcnow().isoformat()
                #     },
                #     source="quest_narrative_integration_service"
                # ))
            
            return quest
        except Exception as e:
            self.logger.error(f"Error generating story-driven quest: {e}")
            return None
    
    def generate_branching_quests(self, 
                               db: Session, 
                               parent_quest_id: str, 
                               outcome: str,
                               player_id: Optional[str] = None) -> List[QuestData]:
        """
        Generate branching follow-up quests based on the outcome of a completed quest.
        
        Args:
            db: Database session
            parent_quest_id: Parent quest identifier
            outcome: Outcome of the parent quest ('success' or 'failure')
            player_id: Optional player identifier
            
        Returns:
            List of generated quest data
        """
        self.logger.info(f"Generating branching quests for parent quest {parent_quest_id} with outcome {outcome}")
        
        try:
            # Get the parent quest
            parent_quest = get_quest(db, parent_quest_id)
            if not parent_quest:
                self.logger.warning(f"Parent quest {parent_quest_id} not found")
                return []
            
            # Determine number of branching quests based on quest importance and complexity
            custom_data = parent_quest.custom_data or {}
            narrative_context = custom_data.get("narrative_context", {})
            importance = narrative_context.get("event_importance", 3)
            
            # More important quests might have more branches
            num_branches = 1
            if importance >= 7:  # Very important quest
                num_branches = random.randint(2, 3)
            elif importance >= 4:  # Moderately important quest
                num_branches = random.randint(1, 2)
            
            generated_quests = []
            
            # Generate quests for each branch
            for i in range(num_branches):
                # Determine quest type for this branch
                if i == 0:
                    # First branch is directly related to parent quest
                    quest_type = parent_quest.quest_type
                else:
                    # Other branches might be different types
                    quest_type = self._get_related_quest_type(parent_quest.quest_type)
                
                # Create generation context with reference to parent quest
                context = QuestGenerationContext(
                    triggering_location_id=parent_quest.related_location_ids[0] if parent_quest.related_location_ids else None,
                    triggering_npc_id=parent_quest.quest_giver_npc_id,
                    player_character_id=player_id,
                    desired_quest_type=quest_type,
                    desired_difficulty=parent_quest.difficulty + random.randint(-1, 1),  # Slight variation in difficulty
                    narrative_context={
                        "parent_quest_id": parent_quest_id,
                        "parent_quest_outcome": outcome,
                        "branch_number": i + 1,
                        "branch_type": "continuation" if i == 0 else "side_effect",
                        **narrative_context  # Include original narrative context
                    },
                    generation_reason=f"branching_quest_from_{parent_quest_id}"
                )
                
                # Generate quest
                quest = self.quest_generator.generate_quest(db, context)
                if quest:
                    # Update quest with parent reference
                    update_data = {
                        "custom_data": quest.custom_data or {}
                    }
                    update_data["custom_data"]["parent_quest_id"] = parent_quest_id
                    update_data["custom_data"]["parent_outcome"] = outcome
                    update_data["custom_data"]["branch_number"] = i + 1
                    update_quest(db, quest.id, update_data)
                    
                    generated_quests.append(quest)
            
            return generated_quests
        except Exception as e:
            self.logger.error(f"Error generating branching quests: {e}")
            return []
    
    def integrate_quest_outcome_with_narrative(self, 
                                           db: Session, 
                                           quest_id: str, 
                                           outcome: str,
                                           player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Integrate a quest's outcome with the narrative system.
        
        Args:
            db: Database session
            quest_id: Quest identifier
            outcome: Quest outcome ('success' or 'failure')
            player_id: Optional player identifier
            
        Returns:
            Dictionary of narrative impacts
        """
        self.logger.info(f"Integrating quest {quest_id} outcome ({outcome}) with narrative")
        
        try:
            # Get the quest
            quest = get_quest(db, quest_id)
            if not quest:
                self.logger.warning(f"Quest {quest_id} not found")
                return {"success": False, "reason": "Quest not found"}
            
            # Extract narrative context
            custom_data = quest.custom_data or {}
            narrative_context = custom_data.get("narrative_context", {})
            
            # Determine narrative impact
            impacts = {
                "success": True,
                "effects": [],
                "story_progression": [],
                "character_development": [],
                "world_state_changes": []
            }
            
            # Different handling based on quest type and outcome
            if outcome == "success":
                # Process successful completion
                if quest.quest_type == QuestType.FETCH_ITEM or quest.quest_type == QuestType.DELIVER_ITEM:
                    # Item quests might reveal information or establish relationships
                    impacts["story_progression"].append({
                        "type": "information_revealed",
                        "description": f"Information was revealed through the {quest.quest_type.lower().replace('_', ' ')}",
                        "importance": narrative_context.get("event_importance", 3)
                    })
                    
                    # If there's an NPC involved, improve relationship
                    if quest.quest_giver_npc_id:
                        impacts["character_development"].append({
                            "type": "relationship_improved",
                            "npc_id": quest.quest_giver_npc_id,
                            "magnitude": 1
                        })
                
                elif quest.quest_type == QuestType.SLAY_CREATURES or quest.quest_type == QuestType.CLEAR_LOCATION:
                    # Combat quests might change area safety or faction influence
                    impacts["world_state_changes"].append({
                        "type": "area_safety_improved",
                        "location_id": quest.related_location_ids[0] if quest.related_location_ids else None,
                        "magnitude": 2
                    })
                
                elif quest.quest_type == QuestType.INVESTIGATE_AREA:
                    # Investigation quests reveal plot information
                    impacts["story_progression"].append({
                        "type": "plot_advanced",
                        "plot_id": narrative_context.get("related_plot"),
                        "advancement_level": 1
                    })
                
                elif quest.quest_type == QuestType.PERSUADE_NPC:
                    # Persuasion quests change NPC attitudes
                    target_npc_id = quest.target_npc_ids[0] if quest.target_npc_ids else None
                    if target_npc_id:
                        impacts["character_development"].append({
                            "type": "npc_attitude_changed",
                            "npc_id": target_npc_id,
                            "attitude_change": "positive",
                            "magnitude": 2
                        })
                
                elif quest.quest_type == QuestType.FACTION_TASK:
                    # Faction tasks improve faction standing
                    if quest.associated_faction_id:
                        impacts["world_state_changes"].append({
                            "type": "faction_influence_increased",
                            "faction_id": quest.associated_faction_id,
                            "magnitude": 1
                        })
            
            else:  # Failure outcome
                # Process failed completion
                if quest.quest_type == QuestType.PROTECT_LOCATION:
                    # Failed protection might decrease area safety
                    impacts["world_state_changes"].append({
                        "type": "area_safety_decreased",
                        "location_id": quest.related_location_ids[0] if quest.related_location_ids else None,
                        "magnitude": 1
                    })
                
                elif quest.quest_type == QuestType.FACTION_TASK:
                    # Failed faction tasks might decrease faction standing
                    if quest.associated_faction_id:
                        impacts["world_state_changes"].append({
                            "type": "faction_influence_decreased",
                            "faction_id": quest.associated_faction_id,
                            "magnitude": 1
                        })
                
                # General failure impacts
                impacts["story_progression"].append({
                    "type": "complication_introduced",
                    "description": "Quest failure has introduced a complication in the story",
                    "importance": narrative_context.get("event_importance", 2)
                })
            
            # In a real implementation, we would send these impacts to the narrative engine
            # to update the story state and potentially trigger new events
            # self.ai_gm_brain.process_quest_outcome(quest_id, outcome, impacts)
            
            # Update quest with narrative impact information
            update_data = {
                "custom_data": custom_data
            }
            update_data["custom_data"]["narrative_impacts"] = impacts
            update_quest(db, quest_id, update_data)
            
            return impacts
        except Exception as e:
            self.logger.error(f"Error integrating quest outcome with narrative: {e}")
            return {"success": False, "reason": str(e)}
    
    def generate_quest_chain(self, 
                          db: Session, 
                          story_arc_id: str,
                          num_quests: int = 3,
                          player_id: Optional[str] = None) -> List[QuestData]:
        """
        Generate a chain of connected quests forming a story arc.
        
        Args:
            db: Database session
            story_arc_id: Story arc identifier
            num_quests: Number of quests in the chain
            player_id: Optional player identifier
            
        Returns:
            List of generated quest data
        """
        self.logger.info(f"Generating quest chain for story arc {story_arc_id} with {num_quests} quests")
        
        try:
            # In a real implementation, we would get story arc data
            # story_arc = self.ai_gm_brain.get_story_arc(story_arc_id)
            
            # Simulate story arc data for this example
            story_arc = {
                "id": story_arc_id,
                "title": f"Story Arc {story_arc_id[-4:]}",
                "theme": random.choice(["redemption", "revenge", "discovery", "corruption", "survival"]),
                "starting_location_id": f"location-{random.randint(1, 5)}",
                "key_npc_id": f"npc-{random.randint(1, 10)}",
                "difficulty": random.randint(2, 5),
                "phases": [
                    "introduction",
                    "rising_action",
                    "climax",
                    "resolution"
                ]
            }
            
            generated_quests = []
            previous_quest_id = None
            
            # Determine appropriate quest types for the story arc
            quest_types = self._get_quest_types_for_theme(story_arc["theme"])
            
            # Generate each quest in the chain
            for i in range(num_quests):
                # Determine phase and difficulty progression
                phase_index = min(i, len(story_arc["phases"]) - 1)
                phase = story_arc["phases"][phase_index]
                
                # Difficulty increases as the chain progresses
                phase_difficulty = story_arc["difficulty"] + i
                
                # Select quest type appropriate for this phase
                if i == 0:
                    # First quest is often investigative or introductory
                    quest_type = random.choice([QuestType.INVESTIGATE_AREA, QuestType.FETCH_ITEM, QuestType.INTERACT_NPC])
                elif i == num_quests - 1:
                    # Final quest is often climactic
                    quest_type = random.choice([QuestType.SLAY_CREATURES, QuestType.PROTECT_LOCATION, QuestType.DIPLOMATIC_MISSION])
                else:
                    # Middle quests advance the story
                    quest_type = random.choice(quest_types)
                
                # Create generation context
                context = QuestGenerationContext(
                    triggering_location_id=story_arc["starting_location_id"],
                    triggering_npc_id=story_arc["key_npc_id"],
                    player_character_id=player_id,
                    desired_quest_type=quest_type,
                    desired_difficulty=phase_difficulty,
                    narrative_context={
                        "story_arc_id": story_arc_id,
                        "story_arc_theme": story_arc["theme"],
                        "story_phase": phase,
                        "chain_position": i + 1,
                        "chain_length": num_quests,
                        "previous_quest_id": previous_quest_id
                    },
                    generation_reason=f"quest_chain_for_{story_arc_id}"
                )
                
                # Generate quest
                quest = self.quest_generator.generate_quest(db, context)
                if quest:
                    # Update quest with chain information
                    update_data = {
                        "custom_data": quest.custom_data or {}
                    }
                    update_data["custom_data"]["story_arc_id"] = story_arc_id
                    update_data["custom_data"]["chain_position"] = i + 1
                    update_data["custom_data"]["chain_length"] = num_quests
                    
                    if previous_quest_id:
                        update_data["custom_data"]["previous_quest_id"] = previous_quest_id
                    
                    # Only the first quest in the chain is initially available
                    if i > 0:
                        update_data["status"] = QuestStatus.UNAVAILABLE
                        update_data["custom_data"]["unlock_condition"] = {
                            "type": "quest_completed",
                            "quest_id": previous_quest_id
                        }
                    
                    update_quest(db, quest.id, update_data)
                    
                    generated_quests.append(quest)
                    previous_quest_id = quest.id
                else:
                    self.logger.error(f"Failed to generate quest {i+1} in chain for story arc {story_arc_id}")
            
            return generated_quests
        except Exception as e:
            self.logger.error(f"Error generating quest chain: {e}")
            return []
    
    def _map_event_to_quest_type(self, event_type: str) -> QuestType:
        """
        Map a narrative event type to an appropriate quest type.
        
        Args:
            event_type: Narrative event type
            
        Returns:
            Appropriate quest type
        """
        event_to_quest = {
            "character_introduced": QuestType.INTERACT_NPC,
            "location_discovered": QuestType.EXPLORE_AREA,
            "faction_conflict": QuestType.DIPLOMATIC_MISSION,
            "enemy_threat": QuestType.SLAY_CREATURES,
            "item_discovery": QuestType.FETCH_ITEM,
            "political_intrigue": QuestType.PERSUADE_NPC,
            "natural_disaster": QuestType.PROTECT_LOCATION,
            "mystery_uncovered": QuestType.INVESTIGATE_AREA,
            "betrayal": QuestType.PERSUADE_NPC,
            "alliance_formed": QuestType.DIPLOMATIC_MISSION
        }
        
        return event_to_quest.get(event_type, QuestType.FETCH_ITEM)  # Default to fetch item
    
    def _get_related_quest_type(self, quest_type: QuestType) -> QuestType:
        """
        Get a related quest type for branching quests.
        
        Args:
            quest_type: Original quest type
            
        Returns:
            Related quest type
        """
        related_types = {
            QuestType.FETCH_ITEM: [QuestType.DELIVER_ITEM, QuestType.INVESTIGATE_AREA],
            QuestType.DELIVER_ITEM: [QuestType.FETCH_ITEM, QuestType.PERSUADE_NPC],
            QuestType.ESCORT_NPC: [QuestType.PROTECT_LOCATION, QuestType.SLAY_CREATURES],
            QuestType.PROTECT_LOCATION: [QuestType.SLAY_CREATURES, QuestType.ESCORT_NPC],
            QuestType.INVESTIGATE_AREA: [QuestType.PERSUADE_NPC, QuestType.FETCH_ITEM],
            QuestType.CRAFT_ITEM: [QuestType.GATHER_RESOURCE, QuestType.DELIVER_ITEM],
            QuestType.SLAY_CREATURES: [QuestType.CLEAR_LOCATION, QuestType.PROTECT_LOCATION],
            QuestType.ECONOMIC_OPPORTUNITY: [QuestType.GATHER_RESOURCE, QuestType.DELIVER_ITEM],
            QuestType.GATHER_RESOURCE: [QuestType.CRAFT_ITEM, QuestType.ECONOMIC_OPPORTUNITY],
            QuestType.CLEAR_LOCATION: [QuestType.SLAY_CREATURES, QuestType.INVESTIGATE_AREA],
            QuestType.PERSUADE_NPC: [QuestType.FETCH_ITEM, QuestType.INVESTIGATE_AREA],
            QuestType.SABOTAGE: [QuestType.STEAL_ITEM, QuestType.CLEAR_LOCATION],
            QuestType.STEAL_ITEM: [QuestType.SABOTAGE, QuestType.DELIVER_ITEM],
            QuestType.EXPLORE_AREA: [QuestType.INVESTIGATE_AREA, QuestType.GATHER_RESOURCE],
            QuestType.DIPLOMATIC_MISSION: [QuestType.PERSUADE_NPC, QuestType.ESCORT_NPC],
            QuestType.FACTION_TASK: [QuestType.FETCH_ITEM, QuestType.SLAY_CREATURES]
        }
        
        options = related_types.get(quest_type, [QuestType.FETCH_ITEM, QuestType.DELIVER_ITEM])
        return random.choice(options)
    
    def _get_quest_types_for_theme(self, theme: str) -> List[QuestType]:
        """
        Get appropriate quest types for a story theme.
        
        Args:
            theme: Story theme
            
        Returns:
            List of appropriate quest types
        """
        theme_to_quest_types = {
            "redemption": [
                QuestType.HELP_NPC, QuestType.PROTECT_LOCATION, 
                QuestType.CLEAR_LOCATION, QuestType.ESCORT_NPC
            ],
            "revenge": [
                QuestType.SLAY_CREATURES, QuestType.SABOTAGE, 
                QuestType.STEAL_ITEM, QuestType.INVESTIGATE_AREA
            ],
            "discovery": [
                QuestType.EXPLORE_AREA, QuestType.INVESTIGATE_AREA, 
                QuestType.FETCH_ITEM, QuestType.GATHER_RESOURCE
            ],
            "corruption": [
                QuestType.INVESTIGATE_AREA, QuestType.PERSUADE_NPC, 
                QuestType.STEAL_ITEM, QuestType.DIPLOMATIC_MISSION
            ],
            "survival": [
                QuestType.GATHER_RESOURCE, QuestType.CLEAR_LOCATION, 
                QuestType.PROTECT_LOCATION, QuestType.CRAFT_ITEM
            ],
            "power": [
                QuestType.FACTION_TASK, QuestType.DIPLOMATIC_MISSION, 
                QuestType.ECONOMIC_OPPORTUNITY, QuestType.SLAY_CREATURES
            ],
            "justice": [
                QuestType.INVESTIGATE_AREA, QuestType.PERSUADE_NPC, 
                QuestType.SLAY_CREATURES, QuestType.CLEAR_LOCATION
            ]
        }
        
        # Default to a mix of common quest types
        default_types = [
            QuestType.FETCH_ITEM, QuestType.DELIVER_ITEM, 
            QuestType.SLAY_CREATURES, QuestType.INVESTIGATE_AREA
        ]
        
        return theme_to_quest_types.get(theme.lower(), default_types)
    
    def _handle_character_introduced(self, event: Any) -> None:
        """
        Handle a character introduced event.
        
        Args:
            event: Event data
        """
        # In a real implementation, this would generate interaction quests
        pass
    
    def _handle_location_discovered(self, event: Any) -> None:
        """
        Handle a location discovered event.
        
        Args:
            event: Event data
        """
        # In a real implementation, this would generate exploration quests
        pass
    
    def _handle_faction_conflict(self, event: Any) -> None:
        """
        Handle a faction conflict event.
        
        Args:
            event: Event data
        """
        # In a real implementation, this would generate diplomatic quests
        pass
    
    def _handle_story_milestone(self, event: Any) -> None:
        """
        Handle a story milestone event.
        
        Args:
            event: Event data
        """
        # In a real implementation, this would generate key plot quests
        pass
    
    def _handle_world_event(self, event: Any) -> None:
        """
        Handle a world event.
        
        Args:
            event: Event data
        """
        # In a real implementation, this would generate event response quests
        pass
    
    def _handle_player_decision(self, event: Any) -> None:
        """
        Handle a player decision event.
        
        Args:
            event: Event data
        """
        # In a real implementation, this would generate consequence quests
        pass