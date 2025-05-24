"""
NPC System CRUD Operations

This module provides database CRUD (Create, Read, Update, Delete)
operations for NPC-related models.
"""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime

from backend.src.npc.models.pydantic_models import NpcData, NpcArchetype, NpcSimulationState
from backend.src.npc.models.db_models import DBNpc, DBNpcArchetype, DBNpcSimulationState

# Create operations
def create_npc(db: Session, npc: NpcData) -> DBNpc:
    """
    Create a new NPC in the database.
    
    Args:
        db: Database session
        npc: NPC data to create
        
    Returns:
        Created NPC database object
    """
    db_npc = DBNpc(
        id=npc.id,
        name=npc.name,
        age=npc.age,
        gender=npc.gender,
        personality_tags=npc.personality_tags,
        backstory_hook=npc.backstory_hook,
        current_location_id=npc.current_location_id,
        economic_role=npc.economic_role,
        skills=npc.skills,
        currency=npc.currency,
        inventory=npc.inventory,
        needs=npc.needs.dict(),
        current_business_id=npc.current_business_id,
        faction_id=npc.faction_id,
        relationships=npc.relationships,
        daily_schedule=npc.daily_schedule,
        creation_date=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        custom_data=npc.custom_data
    )
    db.add(db_npc)
    db.commit()
    db.refresh(db_npc)
    return db_npc

def create_archetype(db: Session, archetype: NpcArchetype) -> DBNpcArchetype:
    """
    Create a new NPC archetype in the database.
    
    Args:
        db: Database session
        archetype: Archetype data to create
        
    Returns:
        Created archetype database object
    """
    db_archetype = DBNpcArchetype(
        name=archetype.name,
        description=archetype.description,
        possible_roles=archetype.possible_roles,
        age_range=archetype.age_range,
        gender_weights=archetype.gender_weights,
        currency_range=archetype.currency_range,
        skill_ranges=archetype.skill_ranges,
        personality_weights=archetype.personality_weights,
        inventory_items=archetype.inventory_items,
        backstory_templates=archetype.backstory_templates,
        need_modifiers=archetype.need_modifiers,
        custom_data=archetype.custom_data,
        creation_date=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )
    db.add(db_archetype)
    db.commit()
    db.refresh(db_archetype)
    return db_archetype

def create_npc_simulation_state(db: Session, state: NpcSimulationState) -> DBNpcSimulationState:
    """
    Create a new NPC simulation state in the database.
    
    Args:
        db: Database session
        state: Simulation state data to create
        
    Returns:
        Created simulation state database object
    """
    db_state = DBNpcSimulationState(
        npc_id=state.npc_id,
        current_activity=state.current_activity,
        hunger=state.hunger,
        energy=state.energy,
        mood=state.mood,
        target_location_id=state.target_location_id,
        daily_transactions=state.daily_transactions,
        last_meal_time=state.last_meal_time,
        last_rest_time=state.last_rest_time,
        last_work_time=state.last_work_time,
        scheduled_events=state.scheduled_events,
        simulation_data=state.simulation_data,
        last_updated=datetime.utcnow()
    )
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

# Read operations
def get_npc(db: Session, npc_id: str) -> Optional[DBNpc]:
    """
    Get an NPC by ID.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        
    Returns:
        NPC database object or None if not found
    """
    return db.query(DBNpc).filter(DBNpc.id == npc_id).first()

def get_npcs(db: Session, skip: int = 0, limit: int = 100) -> List[DBNpc]:
    """
    Get a list of NPCs with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of NPC database objects
    """
    return db.query(DBNpc).offset(skip).limit(limit).all()

def get_npcs_by_location(db: Session, location_id: str) -> List[DBNpc]:
    """
    Get all NPCs at a specific location.
    
    Args:
        db: Database session
        location_id: Location identifier
        
    Returns:
        List of NPC database objects
    """
    return db.query(DBNpc).filter(DBNpc.current_location_id == location_id).all()

def get_npcs_by_role(db: Session, role: str) -> List[DBNpc]:
    """
    Get all NPCs with a specific economic role.
    
    Args:
        db: Database session
        role: Economic role
        
    Returns:
        List of NPC database objects
    """
    return db.query(DBNpc).filter(DBNpc.economic_role == role).all()

def get_npcs_by_faction(db: Session, faction_id: str) -> List[DBNpc]:
    """
    Get all NPCs belonging to a specific faction.
    
    Args:
        db: Database session
        faction_id: Faction identifier
        
    Returns:
        List of NPC database objects
    """
    return db.query(DBNpc).filter(DBNpc.faction_id == faction_id).all()

def get_archetype(db: Session, name: str) -> Optional[DBNpcArchetype]:
    """
    Get an archetype by name.
    
    Args:
        db: Database session
        name: Archetype name
        
    Returns:
        Archetype database object or None if not found
    """
    return db.query(DBNpcArchetype).filter(DBNpcArchetype.name == name).first()

def get_archetypes(db: Session, skip: int = 0, limit: int = 100) -> List[DBNpcArchetype]:
    """
    Get a list of archetypes with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of archetype database objects
    """
    return db.query(DBNpcArchetype).offset(skip).limit(limit).all()

def get_npc_simulation_state(db: Session, npc_id: str) -> Optional[DBNpcSimulationState]:
    """
    Get an NPC's simulation state.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        
    Returns:
        Simulation state database object or None if not found
    """
    return db.query(DBNpcSimulationState).filter(DBNpcSimulationState.npc_id == npc_id).first()

# Update operations
def update_npc(db: Session, npc_id: str, npc_data: Dict[str, Any]) -> Optional[DBNpc]:
    """
    Update an NPC's data.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        npc_data: Dictionary of fields to update
        
    Returns:
        Updated NPC database object or None if not found
    """
    db_npc = db.query(DBNpc).filter(DBNpc.id == npc_id).first()
    if not db_npc:
        return None
        
    # Update fields
    for key, value in npc_data.items():
        if hasattr(db_npc, key):
            setattr(db_npc, key, value)
    
    # Always update last_updated timestamp
    db_npc.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_npc)
    return db_npc

def update_archetype(db: Session, name: str, archetype_data: Dict[str, Any]) -> Optional[DBNpcArchetype]:
    """
    Update an archetype's data.
    
    Args:
        db: Database session
        name: Archetype name
        archetype_data: Dictionary of fields to update
        
    Returns:
        Updated archetype database object or None if not found
    """
    db_archetype = db.query(DBNpcArchetype).filter(DBNpcArchetype.name == name).first()
    if not db_archetype:
        return None
        
    # Update fields
    for key, value in archetype_data.items():
        if hasattr(db_archetype, key):
            setattr(db_archetype, key, value)
    
    # Always update last_updated timestamp
    db_archetype.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_archetype)
    return db_archetype

def update_npc_simulation_state(db: Session, npc_id: str, state_data: Dict[str, Any]) -> Optional[DBNpcSimulationState]:
    """
    Update an NPC's simulation state.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        state_data: Dictionary of fields to update
        
    Returns:
        Updated simulation state database object or None if not found
    """
    db_state = db.query(DBNpcSimulationState).filter(DBNpcSimulationState.npc_id == npc_id).first()
    if not db_state:
        return None
        
    # Update fields
    for key, value in state_data.items():
        if hasattr(db_state, key):
            setattr(db_state, key, value)
    
    # Always update last_updated timestamp
    db_state.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_state)
    return db_state

# Delete operations
def delete_npc(db: Session, npc_id: str) -> bool:
    """
    Delete an NPC from the database.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        
    Returns:
        True if deleted, False if not found
    """
    db_npc = db.query(DBNpc).filter(DBNpc.id == npc_id).first()
    if not db_npc:
        return False
        
    db.delete(db_npc)
    db.commit()
    return True

def delete_archetype(db: Session, name: str) -> bool:
    """
    Delete an archetype from the database.
    
    Args:
        db: Database session
        name: Archetype name
        
    Returns:
        True if deleted, False if not found
    """
    db_archetype = db.query(DBNpcArchetype).filter(DBNpcArchetype.name == name).first()
    if not db_archetype:
        return False
        
    db.delete(db_archetype)
    db.commit()
    return True

def delete_npc_simulation_state(db: Session, npc_id: str) -> bool:
    """
    Delete an NPC's simulation state from the database.
    
    Args:
        db: Database session
        npc_id: NPC identifier
        
    Returns:
        True if deleted, False if not found
    """
    db_state = db.query(DBNpcSimulationState).filter(DBNpcSimulationState.npc_id == npc_id).first()
    if not db_state:
        return False
        
    db.delete(db_state)
    db.commit()
    return True