"""
Quest System CRUD Operations

This module provides database CRUD (Create, Read, Update, Delete)
operations for quest-related models.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from backend.src.quest.models.pydantic_models import (
    QuestData, QuestTemplate, QuestObjective, QuestGenerationContext,
    QuestStatus, QuestType, ObjectiveType, QuestProgressUpdate
)
from backend.src.quest.models.db_models import (
    DBQuest, DBQuestTemplate, DBPlayerQuest, DBQuestEvent
)

# Create operations
def create_quest(db: Session, quest: QuestData) -> DBQuest:
    """
    Create a new quest in the database.
    
    Args:
        db: Database session
        quest: Quest data to create
        
    Returns:
        Created quest database object
    """
    db_quest = DBQuest(
        id=quest.id,
        title=quest.title,
        description_template=quest.description_template,
        generated_description=quest.generated_description,
        quest_type=quest.quest_type,
        status=quest.status,
        difficulty=quest.difficulty,
        objectives=quest.objectives,
        rewards=quest.rewards.dict(),
        failure_conditions=[fc.dict() for fc in quest.failure_conditions],
        quest_giver_npc_id=quest.quest_giver_npc_id,
        target_npc_ids=quest.target_npc_ids,
        related_location_ids=quest.related_location_ids,
        prerequisites=[prereq.dict() for prereq in quest.prerequisites],
        time_limit_seconds=quest.time_limit_seconds,
        recommended_level=quest.recommended_level,
        tags=quest.tags,
        is_repeatable=quest.is_repeatable,
        cooldown_hours=quest.cooldown_hours,
        creation_timestamp=datetime.utcnow(),
        acceptance_timestamp=quest.acceptance_timestamp,
        completion_timestamp=quest.completion_timestamp,
        associated_faction_id=quest.associated_faction_id,
        template_id=quest.template_id,
        custom_data=quest.custom_data
    )
    db.add(db_quest)
    db.commit()
    db.refresh(db_quest)
    return db_quest

def create_quest_template(db: Session, template: QuestTemplate) -> DBQuestTemplate:
    """
    Create a new quest template in the database.
    
    Args:
        db: Database session
        template: Template data to create
        
    Returns:
        Created template database object
    """
    db_template = DBQuestTemplate(
        id=template.id,
        name=template.name,
        quest_type=template.quest_type,
        title_format=template.title_format,
        description_format=template.description_format,
        objective_templates=template.objective_templates,
        reward_ranges=template.reward_ranges,
        potential_failure_conditions=template.potential_failure_conditions,
        difficulty_range=template.difficulty_range,
        suitable_locations=template.suitable_locations,
        suitable_npcs=template.suitable_npcs,
        required_npc_count=template.required_npc_count,
        required_location_count=template.required_location_count,
        required_items=template.required_items,
        parameter_selection_rules=template.parameter_selection_rules,
        common_prerequisites=template.common_prerequisites,
        cooldown_hours=template.cooldown_hours,
        default_time_limit_hours=template.default_time_limit_hours,
        suitable_factions=template.suitable_factions,
        tags=template.tags,
        custom_data=template.custom_data,
        creation_date=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def create_player_quest(db: Session, player_id: str, quest_id: str) -> DBPlayerQuest:
    """
    Create a new player quest record in the database.
    
    Args:
        db: Database session
        player_id: Player identifier
        quest_id: Quest identifier
        
    Returns:
        Created player quest database object
    """
    # Get the quest to retrieve objectives
    quest = db.query(DBQuest).filter(DBQuest.id == quest_id).first()
    if not quest:
        raise ValueError(f"Quest {quest_id} not found")
    
    # Generate a new ID
    player_quest_id = f"pq-{uuid4().hex}"
    
    db_player_quest = DBPlayerQuest(
        id=player_quest_id,
        player_id=player_id,
        quest_id=quest_id,
        status=QuestStatus.ACTIVE,
        current_objectives=quest.objectives,  # Copy objectives from quest
        started_at=datetime.utcnow(),
        completed_at=None,
        custom_data={}
    )
    db.add(db_player_quest)
    
    # Update the quest status to active
    quest.status = QuestStatus.ACTIVE
    quest.acceptance_timestamp = datetime.utcnow()
    
    # Create quest event for tracking
    quest_event = DBQuestEvent(
        id=f"qe-{uuid4().hex}",
        player_id=player_id,
        quest_id=quest_id,
        event_type="quest_accepted",
        event_data={"player_id": player_id, "quest_id": quest_id},
        timestamp=datetime.utcnow()
    )
    db.add(quest_event)
    
    db.commit()
    db.refresh(db_player_quest)
    return db_player_quest

def create_quest_event(db: Session, player_id: str, quest_id: str, event_type: str, event_data: Dict[str, Any]) -> DBQuestEvent:
    """
    Create a new quest event record in the database.
    
    Args:
        db: Database session
        player_id: Player identifier
        quest_id: Quest identifier
        event_type: Type of event
        event_data: Event data
        
    Returns:
        Created quest event database object
    """
    event_id = f"qe-{uuid4().hex}"
    
    db_event = DBQuestEvent(
        id=event_id,
        player_id=player_id,
        quest_id=quest_id,
        event_type=event_type,
        event_data=event_data,
        timestamp=datetime.utcnow()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Read operations
def get_quest(db: Session, quest_id: str) -> Optional[DBQuest]:
    """
    Get a quest by ID.
    
    Args:
        db: Database session
        quest_id: Quest identifier
        
    Returns:
        Quest database object or None if not found
    """
    return db.query(DBQuest).filter(DBQuest.id == quest_id).first()

def get_quests(db: Session, skip: int = 0, limit: int = 100) -> List[DBQuest]:
    """
    Get a list of quests with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of quest database objects
    """
    return db.query(DBQuest).offset(skip).limit(limit).all()

def get_quests_by_status(db: Session, status: QuestStatus, skip: int = 0, limit: int = 100) -> List[DBQuest]:
    """
    Get quests by status with pagination.
    
    Args:
        db: Database session
        status: Quest status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of quest database objects
    """
    return db.query(DBQuest).filter(DBQuest.status == status).offset(skip).limit(limit).all()

def get_quests_by_npc(db: Session, npc_id: str) -> List[DBQuest]:
    """
    Get quests associated with an NPC.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        
    Returns:
        List of quest database objects
    """
    return db.query(DBQuest).filter(DBQuest.quest_giver_npc_id == npc_id).all()

def get_quests_by_location(db: Session, location_id: str) -> List[DBQuest]:
    """
    Get quests associated with a location.
    
    Args:
        db: Database session
        location_id: Location identifier
        
    Returns:
        List of quest database objects
    """
    # Since related_location_ids is a JSON array, we need to use a different approach
    # In a real implementation, you might need to use database-specific JSON operators
    quests = db.query(DBQuest).all()
    return [quest for quest in quests if location_id in quest.related_location_ids]

def get_quests_by_faction(db: Session, faction_id: str) -> List[DBQuest]:
    """
    Get quests associated with a faction.
    
    Args:
        db: Database session
        faction_id: Faction identifier
        
    Returns:
        List of quest database objects
    """
    return db.query(DBQuest).filter(DBQuest.associated_faction_id == faction_id).all()

def get_quest_template(db: Session, template_id: str) -> Optional[DBQuestTemplate]:
    """
    Get a quest template by ID.
    
    Args:
        db: Database session
        template_id: Template identifier
        
    Returns:
        Template database object or None if not found
    """
    return db.query(DBQuestTemplate).filter(DBQuestTemplate.id == template_id).first()

def get_quest_templates(db: Session, skip: int = 0, limit: int = 100) -> List[DBQuestTemplate]:
    """
    Get a list of quest templates with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of template database objects
    """
    return db.query(DBQuestTemplate).offset(skip).limit(limit).all()

def get_quest_templates_by_type(db: Session, quest_type: QuestType) -> List[DBQuestTemplate]:
    """
    Get quest templates by quest type.
    
    Args:
        db: Database session
        quest_type: Quest type
        
    Returns:
        List of template database objects
    """
    return db.query(DBQuestTemplate).filter(DBQuestTemplate.quest_type == quest_type).all()

def get_player_quest(db: Session, player_id: str, quest_id: str) -> Optional[DBPlayerQuest]:
    """
    Get a player's quest by player ID and quest ID.
    
    Args:
        db: Database session
        player_id: Player identifier
        quest_id: Quest identifier
        
    Returns:
        Player quest database object or None if not found
    """
    return db.query(DBPlayerQuest).filter(
        DBPlayerQuest.player_id == player_id,
        DBPlayerQuest.quest_id == quest_id
    ).first()

def get_player_quests(db: Session, player_id: str, status: Optional[QuestStatus] = None) -> List[DBPlayerQuest]:
    """
    Get all quests for a player, optionally filtered by status.
    
    Args:
        db: Database session
        player_id: Player identifier
        status: Optional quest status filter
        
    Returns:
        List of player quest database objects
    """
    query = db.query(DBPlayerQuest).filter(DBPlayerQuest.player_id == player_id)
    if status:
        query = query.filter(DBPlayerQuest.status == status)
    return query.all()

def get_quest_events(db: Session, quest_id: str, event_type: Optional[str] = None) -> List[DBQuestEvent]:
    """
    Get events for a quest, optionally filtered by event type.
    
    Args:
        db: Database session
        quest_id: Quest identifier
        event_type: Optional event type filter
        
    Returns:
        List of quest event database objects
    """
    query = db.query(DBQuestEvent).filter(DBQuestEvent.quest_id == quest_id)
    if event_type:
        query = query.filter(DBQuestEvent.event_type == event_type)
    return query.order_by(DBQuestEvent.timestamp).all()

# Update operations
def update_quest(db: Session, quest_id: str, quest_data: Dict[str, Any]) -> Optional[DBQuest]:
    """
    Update a quest's data.
    
    Args:
        db: Database session
        quest_id: Quest identifier
        quest_data: Dictionary of fields to update
        
    Returns:
        Updated quest database object or None if not found
    """
    db_quest = db.query(DBQuest).filter(DBQuest.id == quest_id).first()
    if not db_quest:
        return None
        
    # Update fields
    for key, value in quest_data.items():
        if hasattr(db_quest, key):
            setattr(db_quest, key, value)
    
    db.commit()
    db.refresh(db_quest)
    return db_quest

def update_quest_status(db: Session, quest_id: str, status: QuestStatus, player_id: Optional[str] = None) -> Optional[DBQuest]:
    """
    Update a quest's status.
    
    Args:
        db: Database session
        quest_id: Quest identifier
        status: New status
        player_id: Optional player identifier (for tracking)
        
    Returns:
        Updated quest database object or None if not found
    """
    db_quest = db.query(DBQuest).filter(DBQuest.id == quest_id).first()
    if not db_quest:
        return None
    
    old_status = db_quest.status
    db_quest.status = status
    
    # Update timestamps based on status
    if status == QuestStatus.ACTIVE and not db_quest.acceptance_timestamp:
        db_quest.acceptance_timestamp = datetime.utcnow()
    elif status in [QuestStatus.COMPLETED_SUCCESS, QuestStatus.COMPLETED_FAILURE, QuestStatus.EXPIRED, QuestStatus.CANCELLED]:
        db_quest.completion_timestamp = datetime.utcnow()
    
    # If player_id is provided, update the player_quest record as well
    if player_id:
        player_quest = get_player_quest(db, player_id, quest_id)
        if player_quest:
            player_quest.status = status
            if status in [QuestStatus.COMPLETED_SUCCESS, QuestStatus.COMPLETED_FAILURE, QuestStatus.EXPIRED, QuestStatus.CANCELLED]:
                player_quest.completed_at = datetime.utcnow()
        
        # Create an event to track the status change
        create_quest_event(db, player_id, quest_id, f"quest_status_changed", {
            "old_status": old_status.value if isinstance(old_status, QuestStatus) else old_status,
            "new_status": status.value if isinstance(status, QuestStatus) else status
        })
    
    db.commit()
    db.refresh(db_quest)
    return db_quest

def update_quest_objective_progress(db: Session, player_id: str, quest_id: str, update_data: QuestProgressUpdate) -> Optional[DBPlayerQuest]:
    """
    Update a player's progress on a quest objective.
    
    Args:
        db: Database session
        player_id: Player identifier
        quest_id: Quest identifier
        update_data: Progress update data
        
    Returns:
        Updated player quest database object or None if not found
    """
    player_quest = get_player_quest(db, player_id, quest_id)
    if not player_quest:
        return None
    
    # Find the objective to update
    objectives = player_quest.current_objectives
    objective_index = -1
    
    for i, objective in enumerate(objectives):
        if objective.get("id") == update_data.objective_id:
            objective_index = i
            break
    
    if objective_index == -1:
        return None  # Objective not found
    
    # Update the objective
    objective = objectives[objective_index]
    
    if update_data.new_quantity is not None:
        objective["current_quantity"] = update_data.new_quantity
    
    if update_data.increment_by is not None:
        objective["current_quantity"] = objective.get("current_quantity", 0) + update_data.increment_by
    
    # Check if objective is completed based on quantity
    if "required_quantity" in objective and objective.get("current_quantity", 0) >= objective.get("required_quantity", 1):
        objective["is_completed"] = True
    
    # Directly set completed status if provided
    if update_data.set_completed is not None:
        objective["is_completed"] = update_data.set_completed
    
    # Update the objective in the list
    objectives[objective_index] = objective
    player_quest.current_objectives = objectives
    
    # Check if all required objectives are completed
    all_required_completed = True
    for obj in objectives:
        if not obj.get("optional", False) and not obj.get("is_completed", False):
            all_required_completed = False
            break
    
    # Update quest status if all objectives are completed
    if all_required_completed:
        player_quest.status = QuestStatus.COMPLETED_SUCCESS
        player_quest.completed_at = datetime.utcnow()
        
        # Update the main quest record
        update_quest_status(db, quest_id, QuestStatus.COMPLETED_SUCCESS, player_id)
        
        # Create an event for quest completion
        create_quest_event(db, player_id, quest_id, "quest_completed", {
            "player_id": player_id,
            "quest_id": quest_id,
            "completed_at": datetime.utcnow().isoformat()
        })
    else:
        # Create an event for objective progress
        create_quest_event(db, player_id, quest_id, "objective_progress_updated", {
            "objective_id": update_data.objective_id,
            "current_quantity": objective.get("current_quantity", 0),
            "is_completed": objective.get("is_completed", False)
        })
    
    db.commit()
    db.refresh(player_quest)
    return player_quest

def update_quest_template(db: Session, template_id: str, template_data: Dict[str, Any]) -> Optional[DBQuestTemplate]:
    """
    Update a quest template's data.
    
    Args:
        db: Database session
        template_id: Template identifier
        template_data: Dictionary of fields to update
        
    Returns:
        Updated template database object or None if not found
    """
    db_template = db.query(DBQuestTemplate).filter(DBQuestTemplate.id == template_id).first()
    if not db_template:
        return None
        
    # Update fields
    for key, value in template_data.items():
        if hasattr(db_template, key):
            setattr(db_template, key, value)
    
    # Always update last_updated timestamp
    db_template.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_template)
    return db_template

# Delete operations
def delete_quest(db: Session, quest_id: str) -> bool:
    """
    Delete a quest from the database.
    
    Args:
        db: Database session
        quest_id: Quest identifier
        
    Returns:
        True if deleted, False if not found
    """
    db_quest = db.query(DBQuest).filter(DBQuest.id == quest_id).first()
    if not db_quest:
        return False
        
    db.delete(db_quest)
    db.commit()
    return True

def delete_quest_template(db: Session, template_id: str) -> bool:
    """
    Delete a quest template from the database.
    
    Args:
        db: Database session
        template_id: Template identifier
        
    Returns:
        True if deleted, False if not found
    """
    db_template = db.query(DBQuestTemplate).filter(DBQuestTemplate.id == template_id).first()
    if not db_template:
        return False
        
    db.delete(db_template)
    db.commit()
    return True

def delete_player_quest(db: Session, player_id: str, quest_id: str) -> bool:
    """
    Delete a player quest record from the database.
    
    Args:
        db: Database session
        player_id: Player identifier
        quest_id: Quest identifier
        
    Returns:
        True if deleted, False if not found
    """
    player_quest = get_player_quest(db, player_id, quest_id)
    if not player_quest:
        return False
        
    db.delete(player_quest)
    db.commit()
    return True