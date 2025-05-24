"""
Player Business System Database Models

This module defines SQLAlchemy models for the player business system,
providing database persistence for player-owned businesses and related data.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum, Time, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Import the database base class (assuming it's defined elsewhere)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Enum types for the database
class BusinessType(enum.Enum):
    BLACKSMITH = "blacksmith"
    APOTHECARY = "apothecary"
    BAKERY = "bakery"
    TAVERN = "tavern"
    INN = "inn"
    TAILOR = "tailor"
    FLETCHER = "fletcher"
    JEWELER = "jeweler"
    CARPENTER = "carpenter"
    SCRIBE = "scribe"
    LEATHERWORKER = "leatherworker"
    GENERAL_STORE = "general_store"
    WEAPONSMITH = "weaponsmith"
    ARMORSMITH = "armorsmith"
    ALCHEMIST = "alchemist"
    HERBALIST = "herbalist"
    BOOKBINDER = "bookbinder"
    STABLE = "stable"

class PropertyType(enum.Enum):
    UNDEVELOPED_LAND = "undeveloped_land"
    EXISTING_BUILDING_RUDIMENTARY = "existing_building_rudimentary"
    EXISTING_BUILDING_ESTABLISHED = "existing_building_established"
    PREMIUM_LOCATION = "premium_location"

class BusinessLicenseStatus(enum.Enum):
    PENDING_APPLICATION = "pending_application"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNDER_REVIEW = "under_review"

class CustomOrderStatus(enum.Enum):
    AWAITING_PLAYER_REVIEW = "awaiting_player_review"
    PLAYER_ACCEPTED = "player_accepted"
    PLAYER_REJECTED = "player_rejected"
    MATERIALS_GATHERING = "materials_gathering"
    CRAFTING_IN_PROGRESS = "crafting_in_progress"
    AWAITING_PICKUP = "awaiting_pickup"
    COMPLETED_DELIVERED = "completed_delivered"
    CANCELLED_BY_NPC = "cancelled_by_npc"
    CANCELLED_BY_PLAYER = "cancelled_by_player"

class StaffRole(enum.Enum):
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    MASTER = "master"
    SHOPKEEPER = "shopkeeper"
    ASSISTANT = "assistant"
    LABORER = "laborer"

class DayOfWeek(enum.Enum):
    FIRSTDAY = "firstday"
    SECONDDAY = "secondday"
    THIRDDAY = "thirdday"
    FOURTHDAY = "fourthday"
    FIFTHDAY = "fifthday"
    SIXTHDAY = "sixthday"
    SEVENTHDAY = "seventhday"

class TransactionType(enum.Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    WAGE_PAYMENT = "wage_payment"
    TAX_PAYMENT = "tax_payment"
    RENT_PAYMENT = "rent_payment"
    MAINTENANCE = "maintenance"
    UPGRADE = "upgrade"
    DONATION = "donation"
    CUSTOM_ORDER_PAYMENT = "custom_order_payment"
    OTHER = "other"

# Association tables for many-to-many relationships
business_licenses_association = Table(
    'player_business_licenses',
    Base.metadata,
    Column('player_business_id', String, ForeignKey('player_business_profiles.id')),
    Column('license_id', String, ForeignKey('business_licenses.id'))
)

staff_contracts_association = Table(
    'player_business_staff_contracts',
    Base.metadata,
    Column('player_business_id', String, ForeignKey('player_business_profiles.id')),
    Column('contract_id', String, ForeignKey('staff_member_contracts.id'))
)

fixtures_association = Table(
    'player_business_fixtures',
    Base.metadata,
    Column('player_business_id', String, ForeignKey('player_business_profiles.id')),
    Column('fixture_id', String, ForeignKey('business_fixtures_upgrades.id'))
)

research_association = Table(
    'player_business_research',
    Base.metadata,
    Column('player_business_id', String, ForeignKey('player_business_profiles.id')),
    Column('research_id', String, ForeignKey('research_projects.id'))
)

class DBPlayerBusinessProfile(Base):
    """SQLAlchemy model for player-owned businesses."""
    __tablename__ = "player_business_profiles"
    
    id = Column(String, primary_key=True)
    player_character_id = Column(String, nullable=False, index=True)
    base_business_id = Column(String, nullable=True)
    business_name_player_chosen = Column(String, nullable=False)
    business_type = Column(Enum(BusinessType), nullable=False)
    property_deed_id = Column(String, ForeignKey("property_deeds.id"), nullable=True)
    lease_agreement_id = Column(String, ForeignKey("lease_agreements.id"), nullable=True)
    shop_ledger = Column(JSON, default=list)
    customization_options_applied = Column(JSON, default=dict)
    current_apprentices = Column(JSON, default=list)
    inventory = Column(JSON, default=dict)
    business_hours = Column(JSON, default=dict)
    ambiance = Column(JSON, default=dict)
    reputation = Column(JSON, default=dict)
    mastery_level = Column(Integer, default=1)
    establishment_date = Column(DateTime, default=datetime.utcnow)
    last_day_open = Column(DateTime, nullable=True)
    total_revenue = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    daily_customer_capacity = Column(Integer, default=10)
    special_features = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    property_deed = relationship("DBPropertyDeed", back_populates="business")
    lease_agreement = relationship("DBLeaseAgreement", back_populates="business")
    licenses = relationship("DBBusinessLicense", secondary=business_licenses_association, back_populates="businesses")
    staff_contracts = relationship("DBStaffMemberContract", secondary=staff_contracts_association, back_populates="business")
    fixtures = relationship("DBBusinessFixtureOrUpgrade", secondary=fixtures_association, back_populates="business")
    research_projects = relationship("DBResearchProject", secondary=research_association, back_populates="business")
    custom_orders = relationship("DBCustomOrderRequest", back_populates="target_business")
    construction_projects = relationship("DBConstructionProjectTracker", back_populates="business")
    expansion_proposals = relationship("DBBusinessExpansionProposal", back_populates="business")
    daily_summaries = relationship("DBDailyBusinessSummary", back_populates="business")

class DBPropertyDeed(Base):
    """SQLAlchemy model for property deeds."""
    __tablename__ = "property_deeds"
    
    id = Column(String, primary_key=True)
    owner_character_id = Column(String, nullable=False, index=True)
    location_id = Column(String, nullable=False)
    property_type = Column(Enum(PropertyType), nullable=False)
    address_description = Column(Text, nullable=False)
    size_sq_meters = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    property_tax_per_period = Column(Float, nullable=False)
    tax_due_date_rule = Column(String, nullable=False)
    building_blueprints = Column(JSON, nullable=True)
    current_condition_percentage = Column(Float, default=100.0)
    zoning_permissions = Column(JSON, default=list)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    last_tax_payment_date = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", back_populates="property_deed")

class DBLeaseAgreement(Base):
    """SQLAlchemy model for lease agreements."""
    __tablename__ = "lease_agreements"
    
    id = Column(String, primary_key=True)
    tenant_character_id = Column(String, nullable=False, index=True)
    lessor_npc_id = Column(String, nullable=False)
    location_id = Column(String, nullable=False)
    property_type = Column(Enum(PropertyType), nullable=False)
    address_description = Column(Text, nullable=False)
    size_sq_meters = Column(Float, nullable=False)
    lease_setup_fee = Column(Float, nullable=False)
    rent_per_period = Column(Float, nullable=False)
    rent_due_date_rule = Column(String, nullable=False)
    lease_start_date = Column(DateTime, nullable=False)
    lease_end_date = Column(DateTime, nullable=True)
    current_condition_percentage = Column(Float, default=100.0)
    zoning_permissions = Column(JSON, default=list)
    deposit_amount = Column(Float, nullable=False)
    last_rent_payment_date = Column(DateTime, nullable=True)
    is_renewable = Column(Boolean, default=True)
    renewal_terms = Column(Text, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", back_populates="lease_agreement")

class DBBusinessLicense(Base):
    """SQLAlchemy model for business licenses."""
    __tablename__ = "business_licenses"
    
    id = Column(String, primary_key=True)
    license_type_name = Column(String, nullable=False)
    issuing_authority_name = Column(String, nullable=False)
    issuing_authority_contact_npc_id = Column(String, nullable=True)
    application_date = Column(DateTime, nullable=False)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    application_fee = Column(Float, nullable=False)
    renewal_fee = Column(Float, nullable=True)
    status = Column(Enum(BusinessLicenseStatus), nullable=False)
    requirements_met = Column(JSON, default=dict)
    notes = Column(Text, nullable=True)
    benefits_description = Column(Text, nullable=True)
    restrictions = Column(JSON, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    businesses = relationship("DBPlayerBusinessProfile", secondary=business_licenses_association, back_populates="licenses")

class DBCustomOrderRequest(Base):
    """SQLAlchemy model for custom order requests."""
    __tablename__ = "custom_order_requests"
    
    id = Column(String, primary_key=True)
    requesting_npc_id = Column(String, nullable=False)
    target_player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    item_description_by_npc = Column(Text, nullable=False)
    item_category_hint = Column(String, nullable=True)
    desired_materials_hint = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    offered_price_initial = Column(Float, nullable=False)
    negotiated_price_final = Column(Float, nullable=True)
    deadline_preference_days = Column(Integer, nullable=False)
    deadline_date = Column(DateTime, nullable=False)
    status = Column(Enum(CustomOrderStatus), default=CustomOrderStatus.AWAITING_PLAYER_REVIEW)
    player_notes_on_order = Column(Text, nullable=True)
    npc_satisfaction_rating = Column(Integer, nullable=True)
    npc_feedback_text = Column(Text, nullable=True)
    materials_required = Column(JSON, nullable=True)
    crafting_difficulty = Column(Integer, nullable=True)
    requested_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    target_business = relationship("DBPlayerBusinessProfile", back_populates="custom_orders")

class DBStaffMemberContract(Base):
    """SQLAlchemy model for staff member contracts."""
    __tablename__ = "staff_member_contracts"
    
    id = Column(String, primary_key=True)
    npc_id = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    agreed_wage_per_period = Column(Float, nullable=False)
    wage_payment_schedule = Column(String, nullable=False)
    assigned_tasks_description = Column(Text, nullable=False)
    work_schedule = Column(JSON, nullable=False)
    contract_start_date = Column(DateTime, nullable=False)
    contract_end_date = Column(DateTime, nullable=True)
    current_morale_level = Column(Integer, default=5)
    performance_notes_by_player = Column(Text, nullable=True)
    skills = Column(JSON, default=dict)
    last_wage_payment_date = Column(DateTime, nullable=True)
    is_probationary = Column(Boolean, default=False)
    probation_end_date = Column(DateTime, nullable=True)
    benefits = Column(Text, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", secondary=staff_contracts_association, back_populates="staff_contracts")

class DBBusinessFixtureOrUpgrade(Base):
    """SQLAlchemy model for business fixtures or upgrades."""
    __tablename__ = "business_fixtures_upgrades"
    
    id = Column(String, primary_key=True)
    fixture_type_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    cost_materials = Column(JSON, default=dict)
    cost_currency = Column(Float, nullable=False)
    installation_time_hours = Column(Integer, nullable=False)
    prerequisites_text = Column(Text, nullable=True)
    benefits_description = Column(Text, nullable=False)
    is_installed_and_active = Column(Boolean, default=False)
    condition_percentage = Column(Float, default=100.0)
    purchase_date = Column(DateTime, nullable=True)
    installation_date = Column(DateTime, nullable=True)
    last_maintenance_date = Column(DateTime, nullable=True)
    functional_bonus = Column(JSON, default=dict)
    aesthetic_bonus = Column(Float, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", secondary=fixtures_association, back_populates="fixtures")

class DBResearchProject(Base):
    """SQLAlchemy model for research projects."""
    __tablename__ = "research_projects"
    
    id = Column(String, primary_key=True)
    research_subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_materials = Column(JSON, default=dict)
    required_skills = Column(JSON, default=dict)
    time_investment_hours = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    current_progress_percentage = Column(Float, default=0.0)
    results_description = Column(Text, nullable=True)
    unlocked_recipe_ids = Column(JSON, default=list)
    unlocked_technique_ids = Column(JSON, default=list)
    is_completed = Column(Boolean, default=False)
    cost_currency = Column(Float, default=0.0)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", secondary=research_association, back_populates="research_projects")

class DBConstructionProjectTracker(Base):
    """SQLAlchemy model for construction project trackers."""
    __tablename__ = "construction_project_trackers"
    
    id = Column(String, primary_key=True)
    player_character_id = Column(String, nullable=False, index=True)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    property_id = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    blueprint_id = Column(String, nullable=True)
    initial_funding = Column(Float, nullable=False)
    total_estimated_cost = Column(Float, nullable=False)
    current_funds_allocated = Column(Float, nullable=False)
    materials_required = Column(JSON, default=dict)
    materials_acquired = Column(JSON, default=dict)
    labor_costs = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    estimated_completion_date = Column(DateTime, nullable=False)
    actual_completion_date = Column(DateTime, nullable=True)
    current_progress_percentage = Column(Float, default=0.0)
    current_phase = Column(String, default="planning")
    contractor_npc_id = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    project_logs = Column(JSON, default=list)
    issues_encountered = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", back_populates="construction_projects")

class DBBusinessExpansionProposal(Base):
    """SQLAlchemy model for business expansion proposals."""
    __tablename__ = "business_expansion_proposals"
    
    id = Column(String, primary_key=True)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    expansion_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    required_permits = Column(JSON, default=list)
    estimated_construction_time_days = Column(Integer, nullable=False)
    benefits_description = Column(Text, nullable=False)
    proposal_date = Column(DateTime, default=datetime.utcnow)
    approval_status = Column(String, default="pending")
    approval_authority_npc_id = Column(String, nullable=True)
    construction_project_id = Column(String, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", back_populates="expansion_proposals")

class DBDailyBusinessSummary(Base):
    """SQLAlchemy model for daily business summaries."""
    __tablename__ = "daily_business_summaries"
    
    id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    total_sales = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    number_of_customers = Column(Integer, default=0)
    customer_satisfaction_average = Column(Float, nullable=True)
    items_sold = Column(JSON, default=dict)
    materials_used = Column(JSON, default=dict)
    special_events = Column(JSON, default=list)
    staff_performance_notes = Column(JSON, default=dict)
    inventory_changes = Column(JSON, default=dict)
    notable_interactions = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business = relationship("DBPlayerBusinessProfile", back_populates="daily_summaries")

class DBStaffJobListing(Base):
    """SQLAlchemy model for staff job listings."""
    __tablename__ = "staff_job_listings"
    
    id = Column(String, primary_key=True)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    role_title = Column(String, nullable=False)
    role_description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=dict)
    preferred_skills = Column(JSON, default=dict)
    wage_range_min = Column(Float, nullable=False)
    wage_range_max = Column(Float, nullable=False)
    working_hours_description = Column(Text, nullable=False)
    benefits_offered = Column(Text, nullable=True)
    listing_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    applicant_npc_ids = Column(JSON, default=list)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business_profile = relationship("DBPlayerBusinessProfile")

class DBCustomerInteraction(Base):
    """SQLAlchemy model for customer interactions."""
    __tablename__ = "customer_interactions"
    
    id = Column(String, primary_key=True)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    customer_npc_id = Column(String, nullable=False)
    interaction_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    satisfaction_rating = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    purchase_amount = Column(Float, nullable=True)
    items_purchased = Column(JSON, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business_profile = relationship("DBPlayerBusinessProfile")

class DBFinancialTransaction(Base):
    """SQLAlchemy model for financial transactions."""
    __tablename__ = "financial_transactions"
    
    id = Column(String, primary_key=True)
    player_business_profile_id = Column(String, ForeignKey("player_business_profiles.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    related_entity_id = Column(String, nullable=True)
    related_entity_name = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_income = Column(Boolean, nullable=False)
    category = Column(String, nullable=True)
    item_details = Column(JSON, nullable=True)
    custom_data = Column(JSON, default=dict)
    
    # Relationships
    business_profile = relationship("DBPlayerBusinessProfile")