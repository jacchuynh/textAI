"""
Illicit Business Models

This module defines data models for the black market and illicit business operations.
"""

import enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class IllicitItemCategory(str, enum.Enum):
    """Categories of illicit items."""
    STOLEN = "stolen"  # Stolen goods
    CONTRABAND = "contraband"  # Rare or heavily taxed items
    FORBIDDEN_ARTIFACT = "forbidden_artifact"  # Illegal magical items or relics
    ILLEGAL_SUBSTANCE = "illegal_substance"  # Poisons, drugs, banned potions
    COUNTERFEIT = "counterfeit"  # Fake currency, forged documents
    SMUGGLED = "smuggled"  # Items smuggled past customs/tariffs


class IllicitServiceType(str, enum.Enum):
    """Types of illicit services."""
    ASSASSINATION = "assassination"
    FORGERY = "forgery"
    SMUGGLING = "smuggling"
    UNLICENSED_MAGIC = "unlicensed_magic"
    INFORMATION_BROKER = "information_broker"
    MONEY_LAUNDERING = "money_laundering"
    FENCE = "fence"  # Buying/selling stolen goods


class UnderworldRole(str, enum.Enum):
    """Roles that NPCs can have in the criminal underworld."""
    FENCE = "fence"  # Buys/sells stolen goods
    SMUGGLER = "smuggler"  # Transports illicit goods
    ENFORCER = "enforcer"  # Protection, debt collection
    SPY = "spy"  # Gathers information
    INFORMANT = "informant"  # Provides information to authorities or criminals
    FORGER = "forger"  # Creates fake documents/items
    ALCHEMIST = "alchemist"  # Creates illegal substances
    ASSASSIN = "assassin"  # Professional killer
    FIXER = "fixer"  # Arranges deals, solves problems
    THIEF = "thief"  # Specialized in stealing
    KINGPIN = "kingpin"  # High-level criminal leader


class CriminalFaction(str, enum.Enum):
    """Major criminal factions in the game world."""
    THIEVES_GUILD = "thieves_guild"  # Specialized in theft, burglary
    SHADOW_SYNDICATE = "shadow_syndicate"  # Diverse criminal enterprise
    SMUGGLERS_ALLIANCE = "smugglers_alliance"  # Focus on smuggling operations


class SecurityMeasure(str, enum.Enum):
    """Security measures that can be implemented in illicit businesses."""
    HIDDEN_COMPARTMENT = "hidden_compartment"
    LOOKOUT_POST = "lookout_post"
    ESCAPE_TUNNEL = "escape_tunnel"
    BRIBED_GUARDS = "bribed_guards"
    SOUNDPROOFING = "soundproofing"
    CODE_PHRASES = "code_phrases"
    DISGUISED_MERCHANDISE = "disguised_merchandise"
    FALSE_PAPERWORK = "false_paperwork"
    MAGICAL_WARDS = "magical_wards"
    SECRET_ENTRANCE = "secret_entrance"


class InvestigationStatus(str, enum.Enum):
    """Status of an authority investigation."""
    INITIAL = "initial"  # Just started
    ONGOING = "ongoing"  # Active investigation
    GATHERING_EVIDENCE = "gathering_evidence"
    PREPARING_RAID = "preparing_raid"  # About to conduct a raid
    CONCLUDED = "concluded"  # Finished
    SUSPENDED = "suspended"  # Temporarily halted


class CrimeType(str, enum.Enum):
    """Types of crimes that can be committed."""
    THEFT = "theft"
    SMUGGLING = "smuggling"
    ILLEGAL_TRADING = "illegal_trading"
    FORGERY = "forgery"
    ASSAULT = "assault"
    EXTORTION = "extortion"
    TAX_EVASION = "tax_evasion"
    SELLING_CONTRABAND = "selling_contraband"
    UNLICENSED_BUSINESS = "unlicensed_business"
    HARBORING_CRIMINALS = "harboring_criminals"


class ConsequenceType(str, enum.Enum):
    """Types of consequences for criminal activities."""
    WARNING = "warning"
    FINE = "fine"
    CONFISCATION = "confiscation"
    IMPRISONMENT = "imprisonment"
    BUSINESS_SHUTDOWN = "business_shutdown"
    LICENSE_REVOCATION = "license_revocation"
    ASSET_SEIZURE = "asset_seizure"
    REPUTATION_DAMAGE = "reputation_damage"
    BOUNTY = "bounty"


class SmugglingStatus(str, enum.Enum):
    """Status of a smuggling operation."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INTERCEPTED = "intercepted"
    FAILED = "failed"


class IllicitBusinessOperation(BaseModel):
    """Configuration for a business's illicit operations."""
    is_active: bool = False
    hidden_capacity: int = 10  # How many illicit items can be stored
    security_level: int = 1  # 1-10 scale
    security_measures: List[SecurityMeasure] = []
    laundering_efficiency: float = 0.85  # How much of laundered money is retained
    known_black_market_contacts: List[str] = []  # NPC IDs
    bribed_officials: List[str] = []  # NPC IDs
    criminal_faction_affiliation: Optional[CriminalFaction] = None


class IllicitInventoryItem(BaseModel):
    """An item in the illicit inventory."""
    item_id: str
    name: str
    quantity: int
    purchase_price_per_unit: float
    selling_price_per_unit: float
    category: IllicitItemCategory
    is_stolen: bool = False
    origin_region_id: Optional[str] = None
    acquisition_date: datetime
    description: str
    custom_data: Dict[str, Any] = {}


class IllicitService(BaseModel):
    """An illicit service offered by a business."""
    service_id: str
    service_type: IllicitServiceType
    name: str
    description: str
    base_price: float
    skill_requirement: int = 1  # 1-10 scale
    risk_level: int = 5  # 1-10 scale
    is_available: bool = True
    required_resources: Dict[str, int] = {}  # Resource ID to quantity
    custom_data: Dict[str, Any] = {}


class BlackMarketTransaction(BaseModel):
    """Record of a black market transaction."""
    transaction_id: str
    business_id: Optional[str] = None
    player_id: str
    contact_npc_id: Optional[str] = None
    transaction_type: str  # "buy", "sell", "service"
    item_id: Optional[str] = None
    service_id: Optional[str] = None
    quantity: int = 1
    total_price: float
    location_id: str
    timestamp: datetime
    risk_taken: float  # 0.0-1.0
    was_detected: bool = False
    custom_data: Dict[str, Any] = {}


class RegionalHeatLevel(BaseModel):
    """Heat level for a specific region."""
    region_id: str
    current_heat: float = 0.0  # 0.0-10.0
    authority_presence: int = 5  # 1-10 scale
    recent_incidents: int = 0
    last_patrol_time: Optional[datetime] = None
    active_investigations: int = 0
    special_conditions: Dict[str, Any] = {}


class AuthorityInvestigation(BaseModel):
    """An investigation by authorities."""
    investigation_id: str
    target_id: str  # Could be business_id, player_id, etc.
    target_type: str  # "business", "player", "location"
    investigator_npc_id: str
    region_id: str
    start_date: datetime
    status: InvestigationStatus
    evidence_level: float = 0.0  # 0.0-1.0
    suspicion_cause: str
    progress_notes: List[Dict[str, Any]] = []
    expected_completion_date: Optional[datetime] = None


class SmugglingOperation(BaseModel):
    """A smuggling operation."""
    operation_id: str
    business_id: Optional[str] = None
    player_id: str
    route: Dict[str, str]  # From region_id to region_id
    goods: Dict[str, int]  # Item ID to quantity
    assigned_npcs: List[str] = []  # NPC IDs
    risk_assessment: float  # 0.0-1.0
    start_date: datetime
    estimated_completion_date: datetime
    actual_completion_date: Optional[datetime] = None
    status: SmugglingStatus
    profit_potential: float
    outcome_notes: Optional[str] = None


class PlayerCriminalRecord(BaseModel):
    """Criminal record for a player."""
    player_id: str
    notoriety: float = 0.0  # 0.0-10.0
    known_crimes: List[Dict[str, Any]] = []
    current_bounty: float = 0.0
    times_caught: int = 0
    times_escaped: int = 0
    faction_relationships: Dict[str, float] = {}  # Faction ID to relationship score
    current_disguise_effectiveness: float = 0.0  # 0.0-1.0
    suspected_by_regions: List[str] = []  # Region IDs


class HiddenLocation(BaseModel):
    """A hidden location for black market activities."""
    location_id: str
    name: str
    description: str
    region_id: str
    type: str  # "hideout", "black_market", "smuggler_den", etc.
    controlled_by_faction: Optional[CriminalFaction] = None
    access_difficulty: int = 5  # 1-10 scale
    security_level: int = 5  # 1-10 scale
    available_services: List[IllicitServiceType] = []
    known_to_player_ids: List[str] = []
    custom_data: Dict[str, Any] = {}


class IllicitCustomOrderRequest(BaseModel):
    """A request for an illicit custom order."""
    order_id: str
    requesting_npc_id: str
    target_player_business_profile_id: str
    item_description_by_npc: str
    item_category_hint: IllicitItemCategory
    quantity: int = 1
    offered_price_initial: float
    deadline_preference_days: int
    deadline_date: str  # ISO format date string
    status: str  # "awaiting_review", "accepted", "declined", "completed", "failed"
    risk_level: float = 0.5  # 0.0-1.0
    requires_special_skills: List[str] = []
    custom_data: Dict[str, Any] = {}