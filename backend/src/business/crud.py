"""
CRUD Operations for Player Business System

This module provides Create, Read, Update, and Delete operations
for the player business system database models.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4

from backend.src.business.models.db_models import (
    DBPlayerBusinessProfile, DBPropertyDeed, DBLeaseAgreement,
    DBBusinessLicense, DBCustomOrderRequest, DBStaffMemberContract,
    DBBusinessFixtureOrUpgrade, DBResearchProject, DBConstructionProjectTracker,
    DBBusinessExpansionProposal, DBDailyBusinessSummary, DBStaffJobListing,
    DBCustomerInteraction, DBFinancialTransaction, 
    BusinessType, PropertyType, BusinessLicenseStatus, CustomOrderStatus
)

from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, PropertyDeed, LeaseAgreement,
    BusinessLicense, CustomOrderRequest, StaffMemberContract,
    BusinessFixtureOrUpgrade, ResearchProject, ConstructionProjectTracker,
    BusinessExpansionProposal, DailyBusinessSummary, FinancialTransaction,
    CustomerInteraction, TransactionType
)

logger = logging.getLogger(__name__)

# Helper functions for converting between Pydantic and SQLAlchemy models
def db_to_pydantic_player_business(db_business: DBPlayerBusinessProfile) -> PlayerBusinessProfile:
    """Convert a database player business model to a Pydantic model."""
    return PlayerBusinessProfile(
        id=db_business.id,
        player_character_id=db_business.player_character_id,
        base_business_id=db_business.base_business_id,
        business_name_player_chosen=db_business.business_name_player_chosen,
        business_type=db_business.business_type.value,
        property_deed_id=db_business.property_deed_id,
        lease_agreement_id=db_business.lease_agreement_id,
        business_licenses=[license.id for license in db_business.licenses] if db_business.licenses else [],
        shop_ledger=db_business.shop_ledger or [],
        customization_options_applied=db_business.customization_options_applied or {},
        current_staff_contracts=[contract.id for contract in db_business.staff_contracts] if db_business.staff_contracts else [],
        current_apprentices=db_business.current_apprentices or [],
        inventory=db_business.inventory or {},
        installed_fixtures=[fixture.id for fixture in db_business.fixtures] if db_business.fixtures else [],
        active_research_projects=[project.id for project in db_business.research_projects] if db_business.research_projects else [],
        pending_custom_orders=[order.id for order in db_business.custom_orders 
                              if order.status in [CustomOrderStatus.AWAITING_PLAYER_REVIEW, 
                                                 CustomOrderStatus.PLAYER_ACCEPTED,
                                                 CustomOrderStatus.MATERIALS_GATHERING,
                                                 CustomOrderStatus.CRAFTING_IN_PROGRESS]] if db_business.custom_orders else [],
        completed_custom_orders=[order.id for order in db_business.custom_orders 
                                if order.status in [CustomOrderStatus.COMPLETED_DELIVERED,
                                                   CustomOrderStatus.CANCELLED_BY_NPC,
                                                   CustomOrderStatus.CANCELLED_BY_PLAYER]] if db_business.custom_orders else [],
        business_hours=db_business.business_hours or {},
        ambiance=db_business.ambiance or {},
        reputation=db_business.reputation or {},
        mastery_level=db_business.mastery_level,
        establishment_date=db_business.establishment_date,
        last_day_open=db_business.last_day_open,
        total_revenue=db_business.total_revenue,
        total_expenses=db_business.total_expenses,
        current_balance=db_business.current_balance,
        daily_customer_capacity=db_business.daily_customer_capacity,
        special_features=db_business.special_features or [],
        custom_data=db_business.custom_data or {}
    )

def db_to_pydantic_property_deed(db_deed: DBPropertyDeed) -> PropertyDeed:
    """Convert a database property deed model to a Pydantic model."""
    return PropertyDeed(
        id=db_deed.id,
        owner_character_id=db_deed.owner_character_id,
        location_id=db_deed.location_id,
        property_type=db_deed.property_type.value,
        address_description=db_deed.address_description,
        size_sq_meters=db_deed.size_sq_meters,
        purchase_price=db_deed.purchase_price,
        property_tax_per_period=db_deed.property_tax_per_period,
        tax_due_date_rule=db_deed.tax_due_date_rule,
        building_blueprints=db_deed.building_blueprints,
        current_condition_percentage=db_deed.current_condition_percentage,
        zoning_permissions=[zone.value for zone in db_deed.zoning_permissions] if isinstance(db_deed.zoning_permissions, list) else db_deed.zoning_permissions,
        purchase_date=db_deed.purchase_date,
        last_tax_payment_date=db_deed.last_tax_payment_date,
        custom_data=db_deed.custom_data or {}
    )

def db_to_pydantic_lease_agreement(db_lease: DBLeaseAgreement) -> LeaseAgreement:
    """Convert a database lease agreement model to a Pydantic model."""
    return LeaseAgreement(
        id=db_lease.id,
        tenant_character_id=db_lease.tenant_character_id,
        lessor_npc_id=db_lease.lessor_npc_id,
        location_id=db_lease.location_id,
        property_type=db_lease.property_type.value,
        address_description=db_lease.address_description,
        size_sq_meters=db_lease.size_sq_meters,
        lease_setup_fee=db_lease.lease_setup_fee,
        rent_per_period=db_lease.rent_per_period,
        rent_due_date_rule=db_lease.rent_due_date_rule,
        lease_start_date=db_lease.lease_start_date,
        lease_end_date=db_lease.lease_end_date,
        current_condition_percentage=db_lease.current_condition_percentage,
        zoning_permissions=[zone.value for zone in db_lease.zoning_permissions] if isinstance(db_lease.zoning_permissions, list) else db_lease.zoning_permissions,
        deposit_amount=db_lease.deposit_amount,
        last_rent_payment_date=db_lease.last_rent_payment_date,
        is_renewable=db_lease.is_renewable,
        renewal_terms=db_lease.renewal_terms,
        custom_data=db_lease.custom_data or {}
    )

def db_to_pydantic_business_license(db_license: DBBusinessLicense) -> BusinessLicense:
    """Convert a database business license model to a Pydantic model."""
    return BusinessLicense(
        id=db_license.id,
        player_business_profile_id=db_license.businesses[0].id if db_license.businesses else None,
        license_type_name=db_license.license_type_name,
        issuing_authority_name=db_license.issuing_authority_name,
        issuing_authority_contact_npc_id=db_license.issuing_authority_contact_npc_id,
        application_date=db_license.application_date,
        issue_date=db_license.issue_date,
        expiry_date=db_license.expiry_date,
        application_fee=db_license.application_fee,
        renewal_fee=db_license.renewal_fee,
        status=db_license.status.value,
        requirements_met=db_license.requirements_met or {},
        notes=db_license.notes,
        benefits_description=db_license.benefits_description,
        restrictions=db_license.restrictions,
        custom_data=db_license.custom_data or {}
    )

def db_to_pydantic_custom_order(db_order: DBCustomOrderRequest) -> CustomOrderRequest:
    """Convert a database custom order model to a Pydantic model."""
    return CustomOrderRequest(
        id=db_order.id,
        requesting_npc_id=db_order.requesting_npc_id,
        target_player_business_profile_id=db_order.target_player_business_profile_id,
        item_description_by_npc=db_order.item_description_by_npc,
        item_category_hint=db_order.item_category_hint,
        desired_materials_hint=db_order.desired_materials_hint,
        quantity=db_order.quantity,
        offered_price_initial=db_order.offered_price_initial,
        negotiated_price_final=db_order.negotiated_price_final,
        deadline_preference_days=db_order.deadline_preference_days,
        deadline_date=db_order.deadline_date,
        status=db_order.status.value,
        player_notes_on_order=db_order.player_notes_on_order,
        npc_satisfaction_rating=db_order.npc_satisfaction_rating,
        npc_feedback_text=db_order.npc_feedback_text,
        materials_required=db_order.materials_required,
        crafting_difficulty=db_order.crafting_difficulty,
        requested_date=db_order.requested_date,
        completion_date=db_order.completion_date,
        custom_data=db_order.custom_data or {}
    )

def db_to_pydantic_staff_contract(db_contract: DBStaffMemberContract) -> StaffMemberContract:
    """Convert a database staff contract model to a Pydantic model."""
    return StaffMemberContract(
        id=db_contract.id,
        player_business_profile_id=db_contract.business[0].id if db_contract.business else None,
        npc_id=db_contract.npc_id,
        role_title=db_contract.role_title,
        agreed_wage_per_period=db_contract.agreed_wage_per_period,
        wage_payment_schedule=db_contract.wage_payment_schedule,
        assigned_tasks_description=db_contract.assigned_tasks_description,
        work_schedule=db_contract.work_schedule,
        contract_start_date=db_contract.contract_start_date,
        contract_end_date=db_contract.contract_end_date,
        current_morale_level=db_contract.current_morale_level,
        performance_notes_by_player=db_contract.performance_notes_by_player,
        skills=db_contract.skills or {},
        last_wage_payment_date=db_contract.last_wage_payment_date,
        is_probationary=db_contract.is_probationary,
        probation_end_date=db_contract.probation_end_date,
        benefits=db_contract.benefits,
        custom_data=db_contract.custom_data or {}
    )

def db_to_pydantic_fixture(db_fixture: DBBusinessFixtureOrUpgrade) -> BusinessFixtureOrUpgrade:
    """Convert a database fixture model to a Pydantic model."""
    return BusinessFixtureOrUpgrade(
        id=db_fixture.id,
        player_business_profile_id=db_fixture.business[0].id if db_fixture.business else None,
        fixture_type_name=db_fixture.fixture_type_name,
        description=db_fixture.description,
        cost_materials=db_fixture.cost_materials or {},
        cost_currency=db_fixture.cost_currency,
        installation_time_hours=db_fixture.installation_time_hours,
        prerequisites_text=db_fixture.prerequisites_text,
        benefits_description=db_fixture.benefits_description,
        is_installed_and_active=db_fixture.is_installed_and_active,
        condition_percentage=db_fixture.condition_percentage,
        purchase_date=db_fixture.purchase_date,
        installation_date=db_fixture.installation_date,
        last_maintenance_date=db_fixture.last_maintenance_date,
        functional_bonus=db_fixture.functional_bonus or {},
        aesthetic_bonus=db_fixture.aesthetic_bonus,
        custom_data=db_fixture.custom_data or {}
    )

def db_to_pydantic_research(db_research: DBResearchProject) -> ResearchProject:
    """Convert a database research model to a Pydantic model."""
    return ResearchProject(
        id=db_research.id,
        player_business_profile_id=db_research.business[0].id if db_research.business else None,
        research_subject=db_research.research_subject,
        description=db_research.description,
        required_materials=db_research.required_materials or {},
        required_skills=db_research.required_skills or {},
        time_investment_hours=db_research.time_investment_hours,
        start_date=db_research.start_date,
        completion_date=db_research.completion_date,
        current_progress_percentage=db_research.current_progress_percentage,
        results_description=db_research.results_description,
        unlocked_recipe_ids=db_research.unlocked_recipe_ids or [],
        unlocked_technique_ids=db_research.unlocked_technique_ids or [],
        is_completed=db_research.is_completed,
        cost_currency=db_research.cost_currency,
        custom_data=db_research.custom_data or {}
    )

def db_to_pydantic_construction(db_construction: DBConstructionProjectTracker) -> ConstructionProjectTracker:
    """Convert a database construction model to a Pydantic model."""
    return ConstructionProjectTracker(
        id=db_construction.id,
        player_character_id=db_construction.player_character_id,
        property_id=db_construction.property_id,
        project_name=db_construction.project_name,
        description=db_construction.description,
        blueprint_id=db_construction.blueprint_id,
        initial_funding=db_construction.initial_funding,
        total_estimated_cost=db_construction.total_estimated_cost,
        current_funds_allocated=db_construction.current_funds_allocated,
        materials_required=db_construction.materials_required or {},
        materials_acquired=db_construction.materials_acquired or {},
        labor_costs=db_construction.labor_costs,
        start_date=db_construction.start_date,
        estimated_completion_date=db_construction.estimated_completion_date,
        actual_completion_date=db_construction.actual_completion_date,
        current_progress_percentage=db_construction.current_progress_percentage,
        current_phase=db_construction.current_phase,
        contractor_npc_id=db_construction.contractor_npc_id,
        is_completed=db_construction.is_completed,
        project_logs=db_construction.project_logs or [],
        issues_encountered=db_construction.issues_encountered or [],
        custom_data=db_construction.custom_data or {}
    )

def db_to_pydantic_expansion(db_expansion: DBBusinessExpansionProposal) -> BusinessExpansionProposal:
    """Convert a database expansion model to a Pydantic model."""
    return BusinessExpansionProposal(
        id=db_expansion.id,
        player_business_profile_id=db_expansion.player_business_profile_id,
        expansion_type=db_expansion.expansion_type,
        description=db_expansion.description,
        estimated_cost=db_expansion.estimated_cost,
        required_permits=db_expansion.required_permits or [],
        estimated_construction_time_days=db_expansion.estimated_construction_time_days,
        benefits_description=db_expansion.benefits_description,
        proposal_date=db_expansion.proposal_date,
        approval_status=db_expansion.approval_status,
        approval_authority_npc_id=db_expansion.approval_authority_npc_id,
        construction_project_id=db_expansion.construction_project_id,
        custom_data=db_expansion.custom_data or {}
    )

def db_to_pydantic_daily_summary(db_summary: DBDailyBusinessSummary) -> DailyBusinessSummary:
    """Convert a database daily summary model to a Pydantic model."""
    return DailyBusinessSummary(
        date=db_summary.date,
        player_business_profile_id=db_summary.player_business_profile_id,
        total_sales=db_summary.total_sales,
        total_expenses=db_summary.total_expenses,
        profit=db_summary.profit,
        number_of_customers=db_summary.number_of_customers,
        customer_satisfaction_average=db_summary.customer_satisfaction_average,
        items_sold=db_summary.items_sold or {},
        materials_used=db_summary.materials_used or {},
        special_events=db_summary.special_events or [],
        staff_performance_notes=db_summary.staff_performance_notes or {},
        inventory_changes=db_summary.inventory_changes or {},
        notable_interactions=db_summary.notable_interactions or [],
        custom_data=db_summary.custom_data or {}
    )

def db_to_pydantic_transaction(db_transaction: DBFinancialTransaction) -> FinancialTransaction:
    """Convert a database transaction model to a Pydantic model."""
    return FinancialTransaction(
        id=db_transaction.id,
        transaction_type=db_transaction.transaction_type.value,
        amount=db_transaction.amount,
        description=db_transaction.description,
        related_entity_id=db_transaction.related_entity_id,
        related_entity_name=db_transaction.related_entity_name,
        timestamp=db_transaction.timestamp,
        is_income=db_transaction.is_income,
        category=db_transaction.category,
        item_details=db_transaction.item_details,
    )

# CRUD operations for PlayerBusinessProfile
def create_business(db: Session, business_data: PlayerBusinessProfile) -> PlayerBusinessProfile:
    """Create a new player business."""
    try:
        # Generate a new ID if not provided
        if not business_data.id:
            business_data.id = f"business-{uuid4().hex}"
            
        # Create new DB business
        db_business = DBPlayerBusinessProfile(
            id=business_data.id,
            player_character_id=business_data.player_character_id,
            base_business_id=business_data.base_business_id,
            business_name_player_chosen=business_data.business_name_player_chosen,
            business_type=BusinessType(business_data.business_type),
            property_deed_id=business_data.property_deed_id,
            lease_agreement_id=business_data.lease_agreement_id,
            shop_ledger=business_data.shop_ledger,
            customization_options_applied=business_data.customization_options_applied,
            current_apprentices=business_data.current_apprentices,
            inventory=business_data.inventory,
            business_hours=business_data.business_hours,
            ambiance=business_data.ambiance,
            reputation=business_data.reputation,
            mastery_level=business_data.mastery_level,
            establishment_date=business_data.establishment_date,
            last_day_open=business_data.last_day_open,
            total_revenue=business_data.total_revenue,
            total_expenses=business_data.total_expenses,
            current_balance=business_data.current_balance,
            daily_customer_capacity=business_data.daily_customer_capacity,
            special_features=business_data.special_features,
            custom_data=business_data.custom_data
        )
        
        db.add(db_business)
        db.commit()
        db.refresh(db_business)
        
        return db_to_pydantic_player_business(db_business)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating business: {str(e)}")
        raise

def get_business(db: Session, business_id: str) -> Optional[PlayerBusinessProfile]:
    """Get a player business by ID."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if db_business:
            return db_to_pydantic_player_business(db_business)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving business {business_id}: {str(e)}")
        raise

def get_businesses_by_player(db: Session, player_id: str) -> List[PlayerBusinessProfile]:
    """Get all businesses owned by a player."""
    try:
        db_businesses = db.query(DBPlayerBusinessProfile).filter(
            DBPlayerBusinessProfile.player_character_id == player_id
        ).all()
        
        return [db_to_pydantic_player_business(db_business) for db_business in db_businesses]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving businesses for player {player_id}: {str(e)}")
        raise

def get_all_businesses(db: Session, 
                      skip: int = 0, 
                      limit: int = 100,
                      business_type_filter: Optional[str] = None,
                      location_filter: Optional[str] = None,
                      active_only: bool = True) -> List[PlayerBusinessProfile]:
    """
    Get all businesses with optional filters.
    
    Args:
        db: Database session
        skip: Number of businesses to skip
        limit: Maximum number of businesses to return
        business_type_filter: Filter by business type
        location_filter: Filter by location
        active_only: Only return active businesses
        
    Returns:
        List of PlayerBusinessProfile objects
    """
    try:
        query = db.query(DBPlayerBusinessProfile)
        
        if active_only:
            query = query.filter(DBPlayerBusinessProfile.is_active == True)
            
        if business_type_filter:
            query = query.filter(DBPlayerBusinessProfile.business_type == business_type_filter)
            
        if location_filter:
            query = query.filter(DBPlayerBusinessProfile.location_id == location_filter)
            
        db_businesses = query.offset(skip).limit(limit).all()
        
        return [db_to_pydantic_player_business(business) for business in db_businesses]
        
    except SQLAlchemyError as e:
        logger.error(f"Error getting all businesses: {str(e)}")
        raise

def update_business(db: Session, business_id: str, update_data: Dict[str, Any]) -> Optional[PlayerBusinessProfile]:
    """Update a player business."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if key == 'business_type' and value:
                setattr(db_business, key, BusinessType(value))
            elif hasattr(db_business, key):
                setattr(db_business, key, value)
        
        db.commit()
        db.refresh(db_business)
        
        return db_to_pydantic_player_business(db_business)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating business {business_id}: {str(e)}")
        raise

def delete_business(db: Session, business_id: str) -> bool:
    """Delete a player business."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            return False
            
        db.delete(db_business)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting business {business_id}: {str(e)}")
        raise

# CRUD operations for PropertyDeed
def create_property_deed(db: Session, deed_data: PropertyDeed) -> PropertyDeed:
    """Create a new property deed."""
    try:
        # Generate a new ID if not provided
        if not deed_data.id:
            deed_data.id = f"deed-{uuid4().hex}"
            
        # Process zoning permissions
        zoning_permissions = []
        if deed_data.zoning_permissions:
            if isinstance(deed_data.zoning_permissions, list):
                if all(isinstance(x, str) for x in deed_data.zoning_permissions):
                    zoning_permissions = [BusinessType(zone) for zone in deed_data.zoning_permissions]
                else:
                    zoning_permissions = deed_data.zoning_permissions
            else:
                zoning_permissions = deed_data.zoning_permissions
            
        # Create new DB property deed
        db_deed = DBPropertyDeed(
            id=deed_data.id,
            owner_character_id=deed_data.owner_character_id,
            location_id=deed_data.location_id,
            property_type=PropertyType(deed_data.property_type),
            address_description=deed_data.address_description,
            size_sq_meters=deed_data.size_sq_meters,
            purchase_price=deed_data.purchase_price,
            property_tax_per_period=deed_data.property_tax_per_period,
            tax_due_date_rule=deed_data.tax_due_date_rule,
            building_blueprints=deed_data.building_blueprints,
            current_condition_percentage=deed_data.current_condition_percentage,
            zoning_permissions=zoning_permissions,
            purchase_date=deed_data.purchase_date,
            last_tax_payment_date=deed_data.last_tax_payment_date,
            custom_data=deed_data.custom_data
        )
        
        db.add(db_deed)
        db.commit()
        db.refresh(db_deed)
        
        return db_to_pydantic_property_deed(db_deed)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating property deed: {str(e)}")
        raise

def get_property_deed(db: Session, deed_id: str) -> Optional[PropertyDeed]:
    """Get a property deed by ID."""
    try:
        db_deed = db.query(DBPropertyDeed).filter(DBPropertyDeed.id == deed_id).first()
        if db_deed:
            return db_to_pydantic_property_deed(db_deed)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving property deed {deed_id}: {str(e)}")
        raise

def get_property_deeds_by_owner(db: Session, owner_id: str) -> List[PropertyDeed]:
    """Get all property deeds owned by a character."""
    try:
        db_deeds = db.query(DBPropertyDeed).filter(
            DBPropertyDeed.owner_character_id == owner_id
        ).all()
        
        return [db_to_pydantic_property_deed(db_deed) for db_deed in db_deeds]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving property deeds for owner {owner_id}: {str(e)}")
        raise

def update_property_deed(db: Session, deed_id: str, update_data: Dict[str, Any]) -> Optional[PropertyDeed]:
    """Update a property deed."""
    try:
        db_deed = db.query(DBPropertyDeed).filter(DBPropertyDeed.id == deed_id).first()
        if not db_deed:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if key == 'property_type' and value:
                setattr(db_deed, key, PropertyType(value))
            elif key == 'zoning_permissions' and value:
                if isinstance(value, list) and all(isinstance(x, str) for x in value):
                    setattr(db_deed, key, [BusinessType(zone) for zone in value])
                else:
                    setattr(db_deed, key, value)
            elif hasattr(db_deed, key):
                setattr(db_deed, key, value)
        
        db.commit()
        db.refresh(db_deed)
        
        return db_to_pydantic_property_deed(db_deed)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating property deed {deed_id}: {str(e)}")
        raise

def delete_property_deed(db: Session, deed_id: str) -> bool:
    """Delete a property deed."""
    try:
        db_deed = db.query(DBPropertyDeed).filter(DBPropertyDeed.id == deed_id).first()
        if not db_deed:
            return False
            
        db.delete(db_deed)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting property deed {deed_id}: {str(e)}")
        raise

# CRUD operations for LeaseAgreement
def create_lease_agreement(db: Session, lease_data: LeaseAgreement) -> LeaseAgreement:
    """Create a new lease agreement."""
    try:
        # Generate a new ID if not provided
        if not lease_data.id:
            lease_data.id = f"lease-{uuid4().hex}"
            
        # Process zoning permissions
        zoning_permissions = []
        if lease_data.zoning_permissions:
            if isinstance(lease_data.zoning_permissions, list):
                if all(isinstance(x, str) for x in lease_data.zoning_permissions):
                    zoning_permissions = [BusinessType(zone) for zone in lease_data.zoning_permissions]
                else:
                    zoning_permissions = lease_data.zoning_permissions
            else:
                zoning_permissions = lease_data.zoning_permissions
            
        # Create new DB lease agreement
        db_lease = DBLeaseAgreement(
            id=lease_data.id,
            tenant_character_id=lease_data.tenant_character_id,
            lessor_npc_id=lease_data.lessor_npc_id,
            location_id=lease_data.location_id,
            property_type=PropertyType(lease_data.property_type),
            address_description=lease_data.address_description,
            size_sq_meters=lease_data.size_sq_meters,
            lease_setup_fee=lease_data.lease_setup_fee,
            rent_per_period=lease_data.rent_per_period,
            rent_due_date_rule=lease_data.rent_due_date_rule,
            lease_start_date=lease_data.lease_start_date,
            lease_end_date=lease_data.lease_end_date,
            current_condition_percentage=lease_data.current_condition_percentage,
            zoning_permissions=zoning_permissions,
            deposit_amount=lease_data.deposit_amount,
            last_rent_payment_date=lease_data.last_rent_payment_date,
            is_renewable=lease_data.is_renewable,
            renewal_terms=lease_data.renewal_terms,
            custom_data=lease_data.custom_data
        )
        
        db.add(db_lease)
        db.commit()
        db.refresh(db_lease)
        
        return db_to_pydantic_lease_agreement(db_lease)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating lease agreement: {str(e)}")
        raise

def get_lease_agreement(db: Session, lease_id: str) -> Optional[LeaseAgreement]:
    """Get a lease agreement by ID."""
    try:
        db_lease = db.query(DBLeaseAgreement).filter(DBLeaseAgreement.id == lease_id).first()
        if db_lease:
            return db_to_pydantic_lease_agreement(db_lease)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving lease agreement {lease_id}: {str(e)}")
        raise

def get_lease_agreements_by_tenant(db: Session, tenant_id: str) -> List[LeaseAgreement]:
    """Get all lease agreements for a tenant."""
    try:
        db_leases = db.query(DBLeaseAgreement).filter(
            DBLeaseAgreement.tenant_character_id == tenant_id
        ).all()
        
        return [db_to_pydantic_lease_agreement(db_lease) for db_lease in db_leases]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving lease agreements for tenant {tenant_id}: {str(e)}")
        raise

def update_lease_agreement(db: Session, lease_id: str, update_data: Dict[str, Any]) -> Optional[LeaseAgreement]:
    """Update a lease agreement."""
    try:
        db_lease = db.query(DBLeaseAgreement).filter(DBLeaseAgreement.id == lease_id).first()
        if not db_lease:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if key == 'property_type' and value:
                setattr(db_lease, key, PropertyType(value))
            elif key == 'zoning_permissions' and value:
                if isinstance(value, list) and all(isinstance(x, str) for x in value):
                    setattr(db_lease, key, [BusinessType(zone) for zone in value])
                else:
                    setattr(db_lease, key, value)
            elif hasattr(db_lease, key):
                setattr(db_lease, key, value)
        
        db.commit()
        db.refresh(db_lease)
        
        return db_to_pydantic_lease_agreement(db_lease)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating lease agreement {lease_id}: {str(e)}")
        raise

def delete_lease_agreement(db: Session, lease_id: str) -> bool:
    """Delete a lease agreement."""
    try:
        db_lease = db.query(DBLeaseAgreement).filter(DBLeaseAgreement.id == lease_id).first()
        if not db_lease:
            return False
            
        db.delete(db_lease)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting lease agreement {lease_id}: {str(e)}")
        raise

# CRUD operations for BusinessLicense
def create_business_license(db: Session, license_data: BusinessLicense, business_id: str) -> BusinessLicense:
    """Create a new business license and associate it with a business."""
    try:
        # Generate a new ID if not provided
        if not license_data.id:
            license_data.id = f"license-{uuid4().hex}"
            
        # Create new DB business license
        db_license = DBBusinessLicense(
            id=license_data.id,
            license_type_name=license_data.license_type_name,
            issuing_authority_name=license_data.issuing_authority_name,
            issuing_authority_contact_npc_id=license_data.issuing_authority_contact_npc_id,
            application_date=license_data.application_date,
            issue_date=license_data.issue_date,
            expiry_date=license_data.expiry_date,
            application_fee=license_data.application_fee,
            renewal_fee=license_data.renewal_fee,
            status=BusinessLicenseStatus(license_data.status),
            requirements_met=license_data.requirements_met,
            notes=license_data.notes,
            benefits_description=license_data.benefits_description,
            restrictions=license_data.restrictions,
            custom_data=license_data.custom_data
        )
        
        # Get the business to associate with this license
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            raise ValueError(f"Business with ID {business_id} not found")
            
        db_license.businesses.append(db_business)
        
        db.add(db_license)
        db.commit()
        db.refresh(db_license)
        
        return db_to_pydantic_business_license(db_license)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating business license: {str(e)}")
        raise

def get_business_license(db: Session, license_id: str) -> Optional[BusinessLicense]:
    """Get a business license by ID."""
    try:
        db_license = db.query(DBBusinessLicense).filter(DBBusinessLicense.id == license_id).first()
        if db_license:
            return db_to_pydantic_business_license(db_license)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving business license {license_id}: {str(e)}")
        raise

def get_business_licenses_by_business(db: Session, business_id: str) -> List[BusinessLicense]:
    """Get all licenses associated with a business."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            return []
            
        return [db_to_pydantic_business_license(license) for license in db_business.licenses]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving business licenses for business {business_id}: {str(e)}")
        raise

def update_business_license(db: Session, license_id: str, update_data: Dict[str, Any]) -> Optional[BusinessLicense]:
    """Update a business license."""
    try:
        db_license = db.query(DBBusinessLicense).filter(DBBusinessLicense.id == license_id).first()
        if not db_license:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if key == 'status' and value:
                setattr(db_license, key, BusinessLicenseStatus(value))
            elif hasattr(db_license, key):
                setattr(db_license, key, value)
        
        db.commit()
        db.refresh(db_license)
        
        return db_to_pydantic_business_license(db_license)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating business license {license_id}: {str(e)}")
        raise

def delete_business_license(db: Session, license_id: str) -> bool:
    """Delete a business license."""
    try:
        db_license = db.query(DBBusinessLicense).filter(DBBusinessLicense.id == license_id).first()
        if not db_license:
            return False
            
        db.delete(db_license)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting business license {license_id}: {str(e)}")
        raise

# CRUD operations for CustomOrderRequest
def create_custom_order(db: Session, order_data: CustomOrderRequest) -> CustomOrderRequest:
    """Create a new custom order request."""
    try:
        # Generate a new ID if not provided
        if not order_data.id:
            order_data.id = f"order-{uuid4().hex}"
            
        # Create new DB custom order
        db_order = DBCustomOrderRequest(
            id=order_data.id,
            requesting_npc_id=order_data.requesting_npc_id,
            target_player_business_profile_id=order_data.target_player_business_profile_id,
            item_description_by_npc=order_data.item_description_by_npc,
            item_category_hint=order_data.item_category_hint,
            desired_materials_hint=order_data.desired_materials_hint,
            quantity=order_data.quantity,
            offered_price_initial=order_data.offered_price_initial,
            negotiated_price_final=order_data.negotiated_price_final,
            deadline_preference_days=order_data.deadline_preference_days,
            deadline_date=order_data.deadline_date,
            status=CustomOrderStatus(order_data.status),
            player_notes_on_order=order_data.player_notes_on_order,
            npc_satisfaction_rating=order_data.npc_satisfaction_rating,
            npc_feedback_text=order_data.npc_feedback_text,
            materials_required=order_data.materials_required,
            crafting_difficulty=order_data.crafting_difficulty,
            requested_date=order_data.requested_date,
            completion_date=order_data.completion_date,
            custom_data=order_data.custom_data
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return db_to_pydantic_custom_order(db_order)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating custom order request: {str(e)}")
        raise

def get_custom_order(db: Session, order_id: str) -> Optional[CustomOrderRequest]:
    """Get a custom order request by ID."""
    try:
        db_order = db.query(DBCustomOrderRequest).filter(DBCustomOrderRequest.id == order_id).first()
        if db_order:
            return db_to_pydantic_custom_order(db_order)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving custom order request {order_id}: {str(e)}")
        raise

def get_custom_orders_by_business(db: Session, business_id: str, 
                                 status_filter: Optional[List[str]] = None) -> List[CustomOrderRequest]:
    """Get custom orders for a business, optionally filtered by status."""
    try:
        query = db.query(DBCustomOrderRequest).filter(
            DBCustomOrderRequest.target_player_business_profile_id == business_id
        )
        
        # Apply status filter if provided
        if status_filter:
            status_enums = [CustomOrderStatus(status) for status in status_filter]
            query = query.filter(DBCustomOrderRequest.status.in_(status_enums))
            
        db_orders = query.all()
        
        return [db_to_pydantic_custom_order(order) for order in db_orders]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving custom orders for business {business_id}: {str(e)}")
        raise

def update_custom_order(db: Session, order_id: str, update_data: Dict[str, Any]) -> Optional[CustomOrderRequest]:
    """Update a custom order request."""
    try:
        db_order = db.query(DBCustomOrderRequest).filter(DBCustomOrderRequest.id == order_id).first()
        if not db_order:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if key == 'status' and value:
                setattr(db_order, key, CustomOrderStatus(value))
            elif hasattr(db_order, key):
                setattr(db_order, key, value)
        
        db.commit()
        db.refresh(db_order)
        
        return db_to_pydantic_custom_order(db_order)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating custom order request {order_id}: {str(e)}")
        raise

def delete_custom_order(db: Session, order_id: str) -> bool:
    """Delete a custom order request."""
    try:
        db_order = db.query(DBCustomOrderRequest).filter(DBCustomOrderRequest.id == order_id).first()
        if not db_order:
            return False
            
        db.delete(db_order)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting custom order request {order_id}: {str(e)}")
        raise

# CRUD operations for StaffMemberContract
def create_staff_contract(db: Session, contract_data: StaffMemberContract, business_id: str) -> StaffMemberContract:
    """Create a new staff member contract and associate it with a business."""
    try:
        # Generate a new ID if not provided
        if not contract_data.id:
            contract_data.id = f"contract-{uuid4().hex}"
            
        # Create new DB staff contract
        db_contract = DBStaffMemberContract(
            id=contract_data.id,
            npc_id=contract_data.npc_id,
            role_title=contract_data.role_title,
            agreed_wage_per_period=contract_data.agreed_wage_per_period,
            wage_payment_schedule=contract_data.wage_payment_schedule,
            assigned_tasks_description=contract_data.assigned_tasks_description,
            work_schedule=contract_data.work_schedule.dict(),
            contract_start_date=contract_data.contract_start_date,
            contract_end_date=contract_data.contract_end_date,
            current_morale_level=contract_data.current_morale_level,
            performance_notes_by_player=contract_data.performance_notes_by_player,
            skills=contract_data.skills,
            last_wage_payment_date=contract_data.last_wage_payment_date,
            is_probationary=contract_data.is_probationary,
            probation_end_date=contract_data.probation_end_date,
            benefits=contract_data.benefits,
            custom_data=contract_data.custom_data
        )
        
        # Get the business to associate with this contract
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            raise ValueError(f"Business with ID {business_id} not found")
            
        db_contract.business.append(db_business)
        
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        
        return db_to_pydantic_staff_contract(db_contract)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating staff contract: {str(e)}")
        raise

def get_staff_contract(db: Session, contract_id: str) -> Optional[StaffMemberContract]:
    """Get a staff contract by ID."""
    try:
        db_contract = db.query(DBStaffMemberContract).filter(DBStaffMemberContract.id == contract_id).first()
        if db_contract:
            return db_to_pydantic_staff_contract(db_contract)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving staff contract {contract_id}: {str(e)}")
        raise

def get_staff_contracts_by_business(db: Session, business_id: str) -> List[StaffMemberContract]:
    """Get all staff contracts for a business."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            return []
            
        return [db_to_pydantic_staff_contract(contract) for contract in db_business.staff_contracts]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving staff contracts for business {business_id}: {str(e)}")
        raise

def update_staff_contract(db: Session, contract_id: str, update_data: Dict[str, Any]) -> Optional[StaffMemberContract]:
    """Update a staff contract."""
    try:
        db_contract = db.query(DBStaffMemberContract).filter(DBStaffMemberContract.id == contract_id).first()
        if not db_contract:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if key == 'work_schedule' and value:
                setattr(db_contract, key, value.dict() if hasattr(value, 'dict') else value)
            elif key == 'contract_end_date' and value:
                # Handle termination
                db_contract.contract_end_date = value
                
                # Update custom data with termination reason if provided
                if 'termination_reason' in update_data:
                    if not db_contract.custom_data:
                        db_contract.custom_data = {}
                    db_contract.custom_data['termination_reason'] = update_data['termination_reason']
                    db_contract.custom_data['terminated_on'] = datetime.utcnow().isoformat()
            elif hasattr(db_contract, key):
                setattr(db_contract, key, value)
        
        db.commit()
        db.refresh(db_contract)
        
        return db_to_pydantic_staff_contract(db_contract)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating staff contract {contract_id}: {str(e)}")
        raise

def delete_staff_contract(db: Session, contract_id: str) -> bool:
    """Delete a staff contract."""
    try:
        db_contract = db.query(DBStaffMemberContract).filter(DBStaffMemberContract.id == contract_id).first()
        if not db_contract:
            return False
            
        db.delete(db_contract)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting staff contract {contract_id}: {str(e)}")
        raise

# CRUD operations for BusinessFixtureOrUpgrade
def create_business_fixture(db: Session, fixture_data: BusinessFixtureOrUpgrade, business_id: str) -> BusinessFixtureOrUpgrade:
    """Create a new business fixture and associate it with a business."""
    try:
        # Generate a new ID if not provided
        if not fixture_data.id:
            fixture_data.id = f"fixture-{uuid4().hex}"
            
        # Create new DB business fixture
        db_fixture = DBBusinessFixtureOrUpgrade(
            id=fixture_data.id,
            fixture_type_name=fixture_data.fixture_type_name,
            description=fixture_data.description,
            cost_materials=fixture_data.cost_materials,
            cost_currency=fixture_data.cost_currency,
            installation_time_hours=fixture_data.installation_time_hours,
            prerequisites_text=fixture_data.prerequisites_text,
            benefits_description=fixture_data.benefits_description,
            is_installed_and_active=fixture_data.is_installed_and_active,
            condition_percentage=fixture_data.condition_percentage,
            purchase_date=fixture_data.purchase_date,
            installation_date=fixture_data.installation_date,
            last_maintenance_date=fixture_data.last_maintenance_date,
            functional_bonus=fixture_data.functional_bonus,
            aesthetic_bonus=fixture_data.aesthetic_bonus,
            custom_data=fixture_data.custom_data
        )
        
        # Get the business to associate with this fixture
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            raise ValueError(f"Business with ID {business_id} not found")
            
        db_fixture.business.append(db_business)
        
        db.add(db_fixture)
        db.commit()
        db.refresh(db_fixture)
        
        return db_to_pydantic_fixture(db_fixture)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating business fixture: {str(e)}")
        raise

def get_business_fixture(db: Session, fixture_id: str) -> Optional[BusinessFixtureOrUpgrade]:
    """Get a business fixture by ID."""
    try:
        db_fixture = db.query(DBBusinessFixtureOrUpgrade).filter(DBBusinessFixtureOrUpgrade.id == fixture_id).first()
        if db_fixture:
            return db_to_pydantic_fixture(db_fixture)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving business fixture {fixture_id}: {str(e)}")
        raise

def get_business_fixtures_by_business(db: Session, business_id: str) -> List[BusinessFixtureOrUpgrade]:
    """Get all fixtures for a business."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            return []
            
        return [db_to_pydantic_fixture(fixture) for fixture in db_business.fixtures]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving business fixtures for business {business_id}: {str(e)}")
        raise

def update_business_fixture(db: Session, fixture_id: str, update_data: Dict[str, Any]) -> Optional[BusinessFixtureOrUpgrade]:
    """Update a business fixture."""
    try:
        db_fixture = db.query(DBBusinessFixtureOrUpgrade).filter(DBBusinessFixtureOrUpgrade.id == fixture_id).first()
        if not db_fixture:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(db_fixture, key):
                setattr(db_fixture, key, value)
        
        db.commit()
        db.refresh(db_fixture)
        
        return db_to_pydantic_fixture(db_fixture)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating business fixture {fixture_id}: {str(e)}")
        raise

def delete_business_fixture(db: Session, fixture_id: str) -> bool:
    """Delete a business fixture."""
    try:
        db_fixture = db.query(DBBusinessFixtureOrUpgrade).filter(DBBusinessFixtureOrUpgrade.id == fixture_id).first()
        if not db_fixture:
            return False
            
        db.delete(db_fixture)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting business fixture {fixture_id}: {str(e)}")
        raise

# CRUD operations for ResearchProject
def create_research_project(db: Session, research_data: ResearchProject, business_id: str) -> ResearchProject:
    """Create a new research project and associate it with a business."""
    try:
        # Generate a new ID if not provided
        if not research_data.id:
            research_data.id = f"research-{uuid4().hex}"
            
        # Create new DB research project
        db_research = DBResearchProject(
            id=research_data.id,
            research_subject=research_data.research_subject,
            description=research_data.description,
            required_materials=research_data.required_materials,
            required_skills=research_data.required_skills,
            time_investment_hours=research_data.time_investment_hours,
            start_date=research_data.start_date,
            completion_date=research_data.completion_date,
            current_progress_percentage=research_data.current_progress_percentage,
            results_description=research_data.results_description,
            unlocked_recipe_ids=research_data.unlocked_recipe_ids,
            unlocked_technique_ids=research_data.unlocked_technique_ids,
            is_completed=research_data.is_completed,
            cost_currency=research_data.cost_currency,
            custom_data=research_data.custom_data
        )
        
        # Get the business to associate with this research
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            raise ValueError(f"Business with ID {business_id} not found")
            
        db_research.business.append(db_business)
        
        db.add(db_research)
        db.commit()
        db.refresh(db_research)
        
        return db_to_pydantic_research(db_research)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating research project: {str(e)}")
        raise

def get_research_project(db: Session, research_id: str) -> Optional[ResearchProject]:
    """Get a research project by ID."""
    try:
        db_research = db.query(DBResearchProject).filter(DBResearchProject.id == research_id).first()
        if db_research:
            return db_to_pydantic_research(db_research)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving research project {research_id}: {str(e)}")
        raise

def get_research_projects_by_business(db: Session, business_id: str, 
                                     include_completed: bool = False) -> List[ResearchProject]:
    """Get research projects for a business, optionally including completed ones."""
    try:
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            return []
            
        if include_completed:
            return [db_to_pydantic_research(research) for research in db_business.research_projects]
        else:
            return [db_to_pydantic_research(research) for research in db_business.research_projects
                   if not research.is_completed]
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving research projects for business {business_id}: {str(e)}")
        raise

def update_research_project(db: Session, research_id: str, update_data: Dict[str, Any]) -> Optional[ResearchProject]:
    """Update a research project."""
    try:
        db_research = db.query(DBResearchProject).filter(DBResearchProject.id == research_id).first()
        if not db_research:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(db_research, key):
                setattr(db_research, key, value)
        
        db.commit()
        db.refresh(db_research)
        
        return db_to_pydantic_research(db_research)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating research project {research_id}: {str(e)}")
        raise

def delete_research_project(db: Session, research_id: str) -> bool:
    """Delete a research project."""
    try:
        db_research = db.query(DBResearchProject).filter(DBResearchProject.id == research_id).first()
        if not db_research:
            return False
            
        db.delete(db_research)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting research project {research_id}: {str(e)}")
        raise

# Additional helper functions for business operations

def record_financial_transaction(
    db: Session, 
    business_id: str, 
    transaction_type: TransactionType,
    amount: float,
    description: str,
    is_income: bool,
    related_entity_id: Optional[str] = None,
    related_entity_name: Optional[str] = None,
    category: Optional[str] = None,
    item_details: Optional[Dict[str, Any]] = None
) -> FinancialTransaction:
    """Record a financial transaction for a business and update its balance."""
    try:
        # Create transaction
        transaction_id = f"transaction-{uuid4().hex[:8]}"
        
        db_transaction = DBFinancialTransaction(
            id=transaction_id,
            player_business_profile_id=business_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            related_entity_id=related_entity_id,
            related_entity_name=related_entity_name,
            timestamp=datetime.utcnow(),
            is_income=is_income,
            category=category,
            item_details=item_details
        )
        
        # Update business balance
        db_business = db.query(DBPlayerBusinessProfile).filter(DBPlayerBusinessProfile.id == business_id).first()
        if not db_business:
            raise ValueError(f"Business with ID {business_id} not found")
            
        if is_income:
            db_business.current_balance += amount
            db_business.total_revenue += amount
        else:
            db_business.current_balance -= amount
            db_business.total_expenses += amount
            
        # Add transaction to business ledger
        if not db_business.shop_ledger:
            db_business.shop_ledger = []
            
        transaction_dict = {
            "id": transaction_id,
            "transaction_type": transaction_type.value,
            "amount": amount,
            "description": description,
            "related_entity_id": related_entity_id,
            "related_entity_name": related_entity_name,
            "timestamp": datetime.utcnow().isoformat(),
            "is_income": is_income,
            "category": category,
            "item_details": item_details
        }
        
        db_business.shop_ledger.append(transaction_dict)
        
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        db.refresh(db_business)
        
        return db_to_pydantic_transaction(db_transaction)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error recording financial transaction: {str(e)}")
        raise

def record_customer_interaction(
    db: Session,
    business_id: str,
    customer_npc_id: str,
    interaction_type: str,
    satisfaction_rating: Optional[int] = None,
    notes: Optional[str] = None,
    purchase_amount: Optional[float] = None,
    items_purchased: Optional[Dict[str, int]] = None
) -> CustomerInteraction:
    """Record a customer interaction with the business."""
    try:
        interaction_id = f"interaction-{uuid4().hex[:8]}"
        
        db_interaction = DBCustomerInteraction(
            id=interaction_id,
            player_business_profile_id=business_id,
            customer_npc_id=customer_npc_id,
            interaction_type=interaction_type,
            timestamp=datetime.utcnow(),
            satisfaction_rating=satisfaction_rating,
            notes=notes,
            purchase_amount=purchase_amount,
            items_purchased=items_purchased
        )
        
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        
        # Create Pydantic model
        return CustomerInteraction(
            customer_npc_id=customer_npc_id,
            interaction_type=interaction_type,
            timestamp=db_interaction.timestamp,
            satisfaction_rating=satisfaction_rating,
            notes=notes,
            purchase_amount=purchase_amount,
            items_purchased=items_purchased
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error recording customer interaction: {str(e)}")
        raise

def create_daily_business_summary(
    db: Session,
    business_id: str,
    date: datetime,
    total_sales: float,
    total_expenses: float,
    number_of_customers: int,
    items_sold: Dict[str, int],
    materials_used: Dict[str, int],
    customer_satisfaction_average: Optional[float] = None,
    special_events: Optional[List[str]] = None,
    staff_performance_notes: Optional[Dict[str, str]] = None,
    notable_interactions: Optional[List[str]] = None,
    custom_data: Optional[Dict[str, Any]] = None
) -> DailyBusinessSummary:
    """Create a daily business summary record."""
    try:
        summary_id = f"summary-{uuid4().hex[:8]}"
        
        db_summary = DBDailyBusinessSummary(
            id=summary_id,
            date=date,
            player_business_profile_id=business_id,
            total_sales=total_sales,
            total_expenses=total_expenses,
            profit=total_sales - total_expenses,
            number_of_customers=number_of_customers,
            customer_satisfaction_average=customer_satisfaction_average,
            items_sold=items_sold,
            materials_used=materials_used,
            special_events=special_events or [],
            staff_performance_notes=staff_performance_notes or {},
            inventory_changes={},  # This will be computed separately
            notable_interactions=notable_interactions or [],
            custom_data=custom_data or {}
        )
        
        # Compute inventory changes
        inventory_changes = {}
        for item_id, quantity in items_sold.items():
            inventory_changes[item_id] = inventory_changes.get(item_id, 0) - quantity
            
        for item_id, quantity in materials_used.items():
            inventory_changes[item_id] = inventory_changes.get(item_id, 0) - quantity
            
        db_summary.inventory_changes = inventory_changes
        
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        
        return db_to_pydantic_daily_summary(db_summary)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating daily business summary: {str(e)}")
        raise

def create_staff_job_listing(
    db: Session,
    business_id: str,
    role_title: str,
    role_description: str,
    wage_range_min: float,
    wage_range_max: float,
    working_hours_description: str,
    required_skills: Optional[Dict[str, int]] = None,
    preferred_skills: Optional[Dict[str, int]] = None,
    benefits_offered: Optional[str] = None,
    expiry_date: Optional[datetime] = None,
    custom_data: Optional[Dict[str, Any]] = None
) -> str:
    """Create a job listing for staff recruitment."""
    try:
        listing_id = f"job-listing-{uuid4().hex[:8]}"
        
        db_listing = DBStaffJobListing(
            id=listing_id,
            player_business_profile_id=business_id,
            role_title=role_title,
            role_description=role_description,
            required_skills=required_skills or {},
            preferred_skills=preferred_skills or {},
            wage_range_min=wage_range_min,
            wage_range_max=wage_range_max,
            working_hours_description=working_hours_description,
            benefits_offered=benefits_offered,
            listing_date=datetime.utcnow(),
            expiry_date=expiry_date,
            is_active=True,
            applicant_npc_ids=[],
            custom_data=custom_data or {}
        )
        
        db.add(db_listing)
        db.commit()
        
        return listing_id
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating staff job listing: {str(e)}")
        raise

def close_staff_job_listing(db: Session, listing_id: str) -> bool:
    """Close a staff job listing."""
    try:
        db_listing = db.query(DBStaffJobListing).filter(DBStaffJobListing.id == listing_id).first()
        if not db_listing:
            return False
            
        db_listing.is_active = False
        db_listing.custom_data['closed_on'] = datetime.utcnow().isoformat()
        
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error closing staff job listing {listing_id}: {str(e)}")
        raise