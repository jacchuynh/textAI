"""
Player Business System Pydantic Models

This module defines Pydantic models for the player business system,
ensuring data validation and type safety.
"""

from typing import Dict, Any, List, Optional, Union, Set
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, time
from uuid import uuid4

class BusinessType(str, Enum):
    """Types of businesses a player can own and operate."""
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
    
class PropertyType(str, Enum):
    """Types of properties available for business establishments."""
    UNDEVELOPED_LAND = "undeveloped_land"
    EXISTING_BUILDING_RUDIMENTARY = "existing_building_rudimentary"
    EXISTING_BUILDING_ESTABLISHED = "existing_building_established"
    PREMIUM_LOCATION = "premium_location"
    
class BusinessLicenseStatus(str, Enum):
    """Status of a business license."""
    PENDING_APPLICATION = "pending_application"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNDER_REVIEW = "under_review"
    
class CustomOrderStatus(str, Enum):
    """Status of a custom order request."""
    AWAITING_PLAYER_REVIEW = "awaiting_player_review"
    PLAYER_ACCEPTED = "player_accepted"
    PLAYER_REJECTED = "player_rejected"
    MATERIALS_GATHERING = "materials_gathering"
    CRAFTING_IN_PROGRESS = "crafting_in_progress"
    AWAITING_PICKUP = "awaiting_pickup"
    COMPLETED_DELIVERED = "completed_delivered"
    CANCELLED_BY_NPC = "cancelled_by_npc"
    CANCELLED_BY_PLAYER = "cancelled_by_player"
    
class StaffRole(str, Enum):
    """Roles that staff members can have in a business."""
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    MASTER = "master"
    SHOPKEEPER = "shopkeeper"
    ASSISTANT = "assistant"
    LABORER = "laborer"
    
class DayOfWeek(str, Enum):
    """Days of the week in the game world."""
    FIRSTDAY = "firstday"
    SECONDDAY = "secondday"
    THIRDDAY = "thirdday"
    FOURTHDAY = "fourthday"
    FIFTHDAY = "fifthday"
    SIXTHDAY = "sixthday"
    SEVENTHDAY = "seventhday"
    
class TransactionType(str, Enum):
    """Types of financial transactions in the business."""
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

class FinancialTransaction(BaseModel):
    """Represents a financial transaction in the business ledger."""
    id: str = Field(default_factory=lambda: f"transaction-{uuid4().hex[:8]}")
    transaction_type: TransactionType
    amount: float
    description: str
    related_entity_id: Optional[str] = None  # Customer, supplier, staff ID, etc.
    related_entity_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_income: bool
    category: Optional[str] = None  # For further categorization
    item_details: Optional[Dict[str, Any]] = None  # Additional details for items involved

class WorkSchedule(BaseModel):
    """Represents a work schedule for a staff member."""
    days: List[DayOfWeek]
    start_time: time
    end_time: time
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('break_end')
    def break_end_after_break_start(cls, v, values):
        if v and 'break_start' in values and values['break_start'] and v <= values['break_start']:
            raise ValueError('Break end time must be after break start time')
        return v

class InventoryItem(BaseModel):
    """Represents an item in the business inventory."""
    item_id: str
    quantity: int
    quality: Optional[float] = None  # 0.0 to 1.0
    purchase_price_per_unit: Optional[float] = None
    selling_price_per_unit: Optional[float] = None
    restock_threshold: Optional[int] = None
    category: Optional[str] = None
    is_material: bool = False  # Whether this is a raw material or finished product
    last_restocked: Optional[datetime] = None
    expiration_date: Optional[datetime] = None  # For perishable goods

class CustomerInteraction(BaseModel):
    """Records an interaction with a customer."""
    customer_npc_id: str
    interaction_type: str  # browse, purchase, inquiry, complaint, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    satisfaction_rating: Optional[int] = None  # 1-5 stars
    notes: Optional[str] = None
    purchase_amount: Optional[float] = None
    items_purchased: Optional[Dict[str, int]] = None  # item_id: quantity

class PropertyDeed(BaseModel):
    """Represents ownership of a property."""
    id: str = Field(default_factory=lambda: f"deed-{uuid4().hex}")
    owner_character_id: str
    location_id: str
    property_type: PropertyType
    address_description: str
    size_sq_meters: float
    purchase_price: float
    property_tax_per_period: float
    tax_due_date_rule: str  # e.g., "1st of each month"
    building_blueprints: Optional[Dict[str, Any]] = None
    current_condition_percentage: float = 100.0
    zoning_permissions: List[BusinessType]
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    last_tax_payment_date: Optional[datetime] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class LeaseAgreement(BaseModel):
    """Represents a lease agreement for a property."""
    id: str = Field(default_factory=lambda: f"lease-{uuid4().hex}")
    tenant_character_id: str
    lessor_npc_id: str
    location_id: str
    property_type: PropertyType
    address_description: str
    size_sq_meters: float
    lease_setup_fee: float
    rent_per_period: float
    rent_due_date_rule: str  # e.g., "1st of each month"
    lease_start_date: datetime
    lease_end_date: Optional[datetime] = None
    current_condition_percentage: float = 100.0
    zoning_permissions: List[BusinessType]
    deposit_amount: float
    last_rent_payment_date: Optional[datetime] = None
    is_renewable: bool = True
    renewal_terms: Optional[str] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class BusinessLicense(BaseModel):
    """Represents a business license or guild membership."""
    id: str = Field(default_factory=lambda: f"license-{uuid4().hex}")
    player_business_profile_id: str
    license_type_name: str
    issuing_authority_name: str
    issuing_authority_contact_npc_id: Optional[str] = None
    application_date: datetime
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    application_fee: float
    renewal_fee: Optional[float] = None
    status: BusinessLicenseStatus
    requirements_met: Dict[str, bool] = Field(default_factory=dict)
    notes: Optional[str] = None
    benefits_description: Optional[str] = None
    restrictions: Optional[List[str]] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class CustomOrderRequest(BaseModel):
    """Represents a custom order request from an NPC."""
    id: str = Field(default_factory=lambda: f"order-{uuid4().hex}")
    requesting_npc_id: str
    target_player_business_profile_id: str
    item_description_by_npc: str
    item_category_hint: Optional[str] = None
    desired_materials_hint: Optional[str] = None
    quantity: int = 1
    offered_price_initial: float
    negotiated_price_final: Optional[float] = None
    deadline_preference_days: int
    deadline_date: datetime
    status: CustomOrderStatus = CustomOrderStatus.AWAITING_PLAYER_REVIEW
    player_notes_on_order: Optional[str] = None
    npc_satisfaction_rating: Optional[int] = None  # 1-5 stars
    npc_feedback_text: Optional[str] = None
    materials_required: Optional[Dict[str, int]] = None  # item_id: quantity
    crafting_difficulty: Optional[int] = None  # 1-10
    requested_date: datetime = Field(default_factory=datetime.utcnow)
    completion_date: Optional[datetime] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class StaffMemberContract(BaseModel):
    """Represents a contract with a staff member."""
    id: str = Field(default_factory=lambda: f"contract-{uuid4().hex}")
    player_business_profile_id: str
    npc_id: str
    role_title: str
    agreed_wage_per_period: float
    wage_payment_schedule: str  # e.g., "weekly", "biweekly", "monthly"
    assigned_tasks_description: str
    work_schedule: WorkSchedule
    contract_start_date: datetime
    contract_end_date: Optional[datetime] = None
    current_morale_level: int = 5  # 1-10
    performance_notes_by_player: Optional[str] = None
    skills: Dict[str, int] = Field(default_factory=dict)
    last_wage_payment_date: Optional[datetime] = None
    is_probationary: bool = False
    probation_end_date: Optional[datetime] = None
    benefits: Optional[str] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class BusinessFixtureOrUpgrade(BaseModel):
    """Represents a fixture or upgrade for the business."""
    id: str = Field(default_factory=lambda: f"fixture-{uuid4().hex}")
    player_business_profile_id: str
    fixture_type_name: str
    description: str
    cost_materials: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity
    cost_currency: float
    installation_time_hours: int
    prerequisites_text: Optional[str] = None
    benefits_description: str
    is_installed_and_active: bool = False
    condition_percentage: float = 100.0
    purchase_date: Optional[datetime] = None
    installation_date: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    functional_bonus: Dict[str, float] = Field(default_factory=dict)  # e.g., {"crafting_speed": 0.15}
    aesthetic_bonus: Optional[float] = None  # Affects shop ambiance
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class ResearchProject(BaseModel):
    """Represents a research project for new recipes or techniques."""
    id: str = Field(default_factory=lambda: f"research-{uuid4().hex}")
    player_business_profile_id: str
    research_subject: str
    description: str
    required_materials: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity
    required_skills: Dict[str, int] = Field(default_factory=dict)  # skill_name: min_level
    time_investment_hours: int
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    current_progress_percentage: float = 0.0
    results_description: Optional[str] = None
    unlocked_recipe_ids: List[str] = Field(default_factory=list)
    unlocked_technique_ids: List[str] = Field(default_factory=list)
    is_completed: bool = False
    cost_currency: float = 0.0
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class ShopAmbiance(BaseModel):
    """Represents the ambiance and reputation of a shop."""
    cleanliness: int = 5  # 1-10
    decor_quality: int = 5  # 1-10
    lighting: int = 5  # 1-10
    organization: int = 5  # 1-10
    customer_comfort: int = 5  # 1-10
    unique_features: List[str] = Field(default_factory=list)
    ambiance_description: Optional[str] = None
    last_cleaned_date: Optional[datetime] = None
    overall_ambiance_rating: int = 5  # 1-10, calculated from other factors
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class BusinessReputation(BaseModel):
    """Represents the reputation of a business in the community."""
    overall_reputation: int = 5  # 1-10
    quality_reputation: int = 5  # 1-10
    service_reputation: int = 5  # 1-10
    price_reputation: int = 5  # 1-10
    reliability_reputation: int = 5  # 1-10
    specialty_reputation: Dict[str, int] = Field(default_factory=dict)  # category: rating
    notable_achievements: List[str] = Field(default_factory=list)
    community_standing: int = 5  # 1-10
    guild_standing: Optional[int] = None  # 1-10
    customer_testimonials: List[Dict[str, Any]] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class PlayerBusinessProfile(BaseModel):
    """Core model for a player-owned business."""
    id: str = Field(default_factory=lambda: f"business-{uuid4().hex}")
    player_character_id: str
    base_business_id: Optional[str] = None  # Link to general business entity if exists
    business_name_player_chosen: str
    business_type: BusinessType
    property_deed_id: Optional[str] = None
    lease_agreement_id: Optional[str] = None
    business_licenses: List[str] = Field(default_factory=list)  # List of license IDs
    shop_ledger: List[FinancialTransaction] = Field(default_factory=list)
    customization_options_applied: Dict[str, Any] = Field(default_factory=dict)
    current_staff_contracts: List[str] = Field(default_factory=list)  # List of contract IDs
    current_apprentices: List[str] = Field(default_factory=list)  # List of apprentice NPCs
    inventory: Dict[str, InventoryItem] = Field(default_factory=dict)
    installed_fixtures: List[str] = Field(default_factory=list)  # List of fixture IDs
    active_research_projects: List[str] = Field(default_factory=list)  # List of research IDs
    pending_custom_orders: List[str] = Field(default_factory=list)  # List of order IDs
    completed_custom_orders: List[str] = Field(default_factory=list)  # List of order IDs
    business_hours: Dict[DayOfWeek, Dict[str, time]] = Field(default_factory=dict)
    ambiance: ShopAmbiance = Field(default_factory=ShopAmbiance)
    reputation: BusinessReputation = Field(default_factory=BusinessReputation)
    mastery_level: int = 1  # 1-10, represents player's skill as a business owner
    establishment_date: datetime = Field(default_factory=datetime.utcnow)
    last_day_open: Optional[datetime] = None
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    current_balance: float = 0.0
    daily_customer_capacity: int = 10
    special_features: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_profit(self) -> float:
        """Calculate the total profit (revenue - expenses)."""
        return self.total_revenue - self.total_expenses

class ConstructionProjectTracker(BaseModel):
    """Tracks the progress of a construction project."""
    id: str = Field(default_factory=lambda: f"construction-{uuid4().hex}")
    player_character_id: str
    property_id: str
    project_name: str
    description: str
    blueprint_id: Optional[str] = None
    initial_funding: float
    total_estimated_cost: float
    current_funds_allocated: float
    materials_required: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity
    materials_acquired: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity
    labor_costs: float
    start_date: datetime
    estimated_completion_date: datetime
    actual_completion_date: Optional[datetime] = None
    current_progress_percentage: float = 0.0
    current_phase: str = "planning"  # planning, foundation, framing, etc.
    contractor_npc_id: Optional[str] = None
    is_completed: bool = False
    project_logs: List[Dict[str, Any]] = Field(default_factory=list)
    issues_encountered: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class BusinessExpansionProposal(BaseModel):
    """Represents a proposal for expanding an existing business."""
    id: str = Field(default_factory=lambda: f"expansion-{uuid4().hex}")
    player_business_profile_id: str
    expansion_type: str  # e.g., "add_room", "second_floor", "new_workstation"
    description: str
    estimated_cost: float
    required_permits: List[str] = Field(default_factory=list)
    estimated_construction_time_days: int
    benefits_description: str
    proposal_date: datetime = Field(default_factory=datetime.utcnow)
    approval_status: str = "pending"  # pending, approved, rejected
    approval_authority_npc_id: Optional[str] = None
    construction_project_id: Optional[str] = None  # If approved and construction started
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class DailyBusinessSummary(BaseModel):
    """Summarizes a day's business activities."""
    date: datetime
    player_business_profile_id: str
    total_sales: float = 0.0
    total_expenses: float = 0.0
    profit: float = 0.0
    number_of_customers: int = 0
    customer_satisfaction_average: Optional[float] = None
    items_sold: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity
    materials_used: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity
    special_events: List[str] = Field(default_factory=list)
    staff_performance_notes: Dict[str, str] = Field(default_factory=dict)  # staff_id: note
    inventory_changes: Dict[str, int] = Field(default_factory=dict)  # item_id: quantity_change
    notable_interactions: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)

class BusinessFoundingRequest(BaseModel):
    """Request to found a new business."""
    player_character_id: str
    business_name_player_chosen: str
    business_type: str  # BusinessType enum value
    founding_capital: float
    location_id: str
    founding_inventory: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    business_plan: Optional[str] = None
    request_id: str = Field(default_factory=lambda: f"founding-{uuid4().hex}")
    request_date: datetime = Field(default_factory=datetime.utcnow)
    approval_status: str = "pending"  # pending, approved, rejected
    approval_authority_npc_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)