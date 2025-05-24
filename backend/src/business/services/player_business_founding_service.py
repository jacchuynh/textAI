"""
Player Business Founding Service

This module provides services for establishing player-owned businesses,
including property acquisition, licensing, and business setup.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, PropertyDeed, LeaseAgreement,
    BusinessLicense, ConstructionProjectTracker,
    BusinessType, PropertyType, BusinessLicenseStatus
)
from backend.src.business.crud import (
    create_business, create_property_deed, create_lease_agreement,
    create_business_license, update_business,
    get_property_deed, get_lease_agreement,
    record_financial_transaction
)
from backend.src.business.models.pydantic_models import TransactionType

logger = logging.getLogger(__name__)

class PlayerBusinessFoundingService:
    """Service for founding and establishing player-owned businesses."""
    
    def __init__(self):
        self.logger = logging.getLogger("PlayerBusinessFoundingService")
    
    def scout_available_properties(
        self, 
        db: Session,
        location_id: str,
        player_id: Optional[str] = None,
        property_type_filter: Optional[List[str]] = None,
        business_type_filter: Optional[List[str]] = None,
        price_range: Optional[Tuple[float, float]] = None,
        size_range: Optional[Tuple[float, float]] = None
    ) -> Dict[str, List]:
        """
        Scout for available properties (both for sale and for lease) in a location.
        
        Args:
            db: Database session
            location_id: ID of the location to search in
            player_id: Optional player ID to customize results
            property_type_filter: Optional filter for property types
            business_type_filter: Optional filter for business types allowed
            price_range: Optional tuple of (min_price, max_price)
            size_range: Optional tuple of (min_size, max_size)
            
        Returns:
            Dictionary with 'for_sale' and 'for_lease' lists of properties
        """
        # In a real implementation, this would query from a repository of available properties
        # For now, we'll generate some example properties
        
        for_sale = []
        for_lease = []
        
        # Generate example properties for sale
        property_types = [pt for pt in PropertyType] if not property_type_filter else [PropertyType(pt) for pt in property_type_filter]
        business_types = [bt for bt in BusinessType] if not business_type_filter else [BusinessType(bt) for bt in business_type_filter]
        
        # Sample property generation for demonstration
        property_details = [
            {
                "name": "Abandoned Blacksmith Shop",
                "type": PropertyType.EXISTING_BUILDING_RUDIMENTARY,
                "price": 1500,
                "size": 80,
                "description": "A simple forge with basic tools. Needs repairs but functional.",
                "allowed_businesses": [BusinessType.BLACKSMITH, BusinessType.WEAPONSMITH, BusinessType.ARMORSMITH]
            },
            {
                "name": "Market District Storefront",
                "type": PropertyType.EXISTING_BUILDING_ESTABLISHED,
                "price": 3000,
                "size": 100,
                "description": "A well-maintained shop in the busy market district. Previous owner was a jeweler.",
                "allowed_businesses": [BusinessType.JEWELER, BusinessType.TAILOR, BusinessType.GENERAL_STORE]
            },
            {
                "name": "Riverside Plot",
                "type": PropertyType.UNDEVELOPED_LAND,
                "price": 800,
                "size": 150,
                "description": "Undeveloped land near the river. Good for water access.",
                "allowed_businesses": [BusinessType.ALCHEMIST, BusinessType.APOTHECARY, BusinessType.HERBALIST]
            },
            {
                "name": "Town Square Building",
                "type": PropertyType.PREMIUM_LOCATION,
                "price": 5000,
                "size": 200,
                "description": "Prime location on the town square. High traffic and visibility.",
                "allowed_businesses": [BusinessType.INN, BusinessType.TAVERN, BusinessType.GENERAL_STORE]
            }
        ]
        
        for i, details in enumerate(property_details):
            # Filter by property type
            if property_type_filter and details["type"].value not in property_type_filter:
                continue
                
            # Filter by business type
            if business_type_filter and not any(bt.value in business_type_filter for bt in details["allowed_businesses"]):
                continue
                
            # Filter by price
            if price_range and (details["price"] < price_range[0] or details["price"] > price_range[1]):
                continue
                
            # Filter by size
            if size_range and (details["size"] < size_range[0] or details["size"] > size_range[1]):
                continue
                
            # Create property deed for sale
            property_id = f"property-{i+1}"
            for_sale.append({
                "id": property_id,
                "name": details["name"],
                "property_type": details["type"].value,
                "address_description": f"Located at {details['name']} in {location_id}",
                "size_sq_meters": details["size"],
                "purchase_price": details["price"],
                "property_tax_per_period": details["price"] * 0.05,  # 5% annual tax
                "description": details["description"],
                "zoning_permissions": [bt.value for bt in details["allowed_businesses"]],
                "location_id": location_id
            })
            
            # For lease options (typically more expensive over time, but lower upfront cost)
            if details["type"] in [PropertyType.EXISTING_BUILDING_RUDIMENTARY, PropertyType.EXISTING_BUILDING_ESTABLISHED, PropertyType.PREMIUM_LOCATION]:
                lease_price = details["price"] * 0.15  # Annual lease at 15% of purchase price
                for_lease.append({
                    "id": f"lease-{i+1}",
                    "property_id": property_id,
                    "name": details["name"],
                    "property_type": details["type"].value,
                    "address_description": f"Located at {details['name']} in {location_id}",
                    "size_sq_meters": details["size"],
                    "lessor_npc_id": f"npc-landlord-{i+1}",
                    "lessor_name": f"Landlord {i+1}",
                    "lease_setup_fee": lease_price * 0.1,  # 10% of annual lease as setup fee
                    "rent_per_period": lease_price / 12,  # Monthly rent
                    "deposit_amount": lease_price / 6,  # 2 months rent as deposit
                    "description": details["description"],
                    "zoning_permissions": [bt.value for bt in details["allowed_businesses"]],
                    "location_id": location_id,
                    "lease_term_months": 12,  # 1-year lease
                    "is_renewable": True
                })
        
        return {
            "for_sale": for_sale,
            "for_lease": for_lease
        }
    
    def purchase_property_deed(
        self,
        db: Session,
        player_id: str,
        property_data: Dict[str, Any]
    ) -> PropertyDeed:
        """
        Purchase a property and create a deed for the player.
        
        Args:
            db: Database session
            player_id: Player character ID
            property_data: Property information
            
        Returns:
            Created property deed
        """
        # Validate property data
        required_fields = ["location_id", "property_type", "address_description", 
                          "size_sq_meters", "purchase_price", "property_tax_per_period",
                          "zoning_permissions"]
        
        for field in required_fields:
            if field not in property_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create property deed
        deed_data = PropertyDeed(
            id=f"deed-{uuid4().hex}",
            owner_character_id=player_id,
            location_id=property_data["location_id"],
            property_type=property_data["property_type"],
            address_description=property_data["address_description"],
            size_sq_meters=property_data["size_sq_meters"],
            purchase_price=property_data["purchase_price"],
            property_tax_per_period=property_data["property_tax_per_period"],
            tax_due_date_rule=property_data.get("tax_due_date_rule", "1st day of each quarter"),
            building_blueprints=property_data.get("building_blueprints"),
            current_condition_percentage=property_data.get("current_condition_percentage", 100.0),
            zoning_permissions=property_data["zoning_permissions"],
            purchase_date=datetime.utcnow(),
            custom_data=property_data.get("custom_data", {})
        )
        
        # Save to database
        deed = create_property_deed(db, deed_data)
        
        # For character-based role-playing games, you might want to track this transaction
        # in the character's financial records as well
        
        self.logger.info(f"Player {player_id} purchased property deed {deed.id}")
        
        return deed
    
    def negotiate_lease_agreement(
        self,
        db: Session,
        player_id: str,
        lease_data: Dict[str, Any],
        negotiation_skill_level: int = 1
    ) -> LeaseAgreement:
        """
        Negotiate a lease agreement for a property.
        
        Args:
            db: Database session
            player_id: Player character ID
            lease_data: Lease information
            negotiation_skill_level: Player's negotiation skill (1-10)
            
        Returns:
            Created lease agreement
        """
        # Validate lease data
        required_fields = ["location_id", "property_type", "address_description", 
                          "size_sq_meters", "lessor_npc_id", "lease_setup_fee",
                          "rent_per_period", "zoning_permissions", "deposit_amount"]
        
        for field in required_fields:
            if field not in lease_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Apply negotiation skill to potentially reduce costs
        # Higher skill means better deals
        if negotiation_skill_level > 1:
            discount_factor = 1.0 - (negotiation_skill_level * 0.02)  # 2% discount per skill level
            lease_data["rent_per_period"] *= discount_factor
            lease_data["lease_setup_fee"] *= discount_factor
            lease_data["deposit_amount"] *= discount_factor
        
        # Create lease agreement
        lease_term_months = lease_data.get("lease_term_months", 12)
        lease_data = LeaseAgreement(
            id=f"lease-{uuid4().hex}",
            tenant_character_id=player_id,
            lessor_npc_id=lease_data["lessor_npc_id"],
            location_id=lease_data["location_id"],
            property_type=lease_data["property_type"],
            address_description=lease_data["address_description"],
            size_sq_meters=lease_data["size_sq_meters"],
            lease_setup_fee=lease_data["lease_setup_fee"],
            rent_per_period=lease_data["rent_per_period"],
            rent_due_date_rule=lease_data.get("rent_due_date_rule", "1st day of each month"),
            lease_start_date=datetime.utcnow(),
            lease_end_date=datetime.utcnow() + timedelta(days=30*lease_term_months) if lease_term_months else None,
            current_condition_percentage=lease_data.get("current_condition_percentage", 100.0),
            zoning_permissions=lease_data["zoning_permissions"],
            deposit_amount=lease_data["deposit_amount"],
            is_renewable=lease_data.get("is_renewable", True),
            renewal_terms=lease_data.get("renewal_terms"),
            custom_data=lease_data.get("custom_data", {})
        )
        
        # Save to database
        lease = create_lease_agreement(db, lease_data)
        
        self.logger.info(f"Player {player_id} negotiated lease agreement {lease.id}")
        
        return lease
    
    def commission_building_construction(
        self,
        db: Session,
        player_id: str,
        property_id: str,
        construction_data: Dict[str, Any],
        initial_funding: float
    ) -> ConstructionProjectTracker:
        """
        Commission the construction of a building on a property.
        
        Args:
            db: Database session
            player_id: Player character ID
            property_id: Property ID
            construction_data: Construction details
            initial_funding: Initial funds for the project
            
        Returns:
            Construction project tracker
        """
        # Validate property ownership
        property_deed = get_property_deed(db, property_id)
        if not property_deed or property_deed.owner_character_id != player_id:
            raise ValueError(f"Player {player_id} does not own property {property_id}")
        
        # Validate construction data
        required_fields = ["project_name", "description", "materials_required", 
                          "total_estimated_cost", "estimated_completion_days"]
        
        for field in required_fields:
            if field not in construction_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate initial funding
        if initial_funding < construction_data["total_estimated_cost"] * 0.2:
            raise ValueError(f"Initial funding must be at least 20% of the total estimated cost")
        
        # Create construction project
        project_data = ConstructionProjectTracker(
            id=f"construction-{uuid4().hex}",
            player_character_id=player_id,
            property_id=property_id,
            project_name=construction_data["project_name"],
            description=construction_data["description"],
            blueprint_id=construction_data.get("blueprint_id"),
            initial_funding=initial_funding,
            total_estimated_cost=construction_data["total_estimated_cost"],
            current_funds_allocated=initial_funding,
            materials_required=construction_data["materials_required"],
            materials_acquired={},
            labor_costs=construction_data.get("labor_costs", construction_data["total_estimated_cost"] * 0.4),
            start_date=datetime.utcnow(),
            estimated_completion_date=datetime.utcnow() + timedelta(days=construction_data["estimated_completion_days"]),
            current_progress_percentage=0.0,
            current_phase="planning",
            contractor_npc_id=construction_data.get("contractor_npc_id"),
            is_completed=False,
            project_logs=[{
                "date": datetime.utcnow().isoformat(),
                "event": "Project started",
                "description": f"Construction project {construction_data['project_name']} initiated with {initial_funding} funding"
            }],
            custom_data=construction_data.get("custom_data", {})
        )
        
        # In a real implementation, this would create the project in the database
        # and potentially trigger time-based progression events
        
        # Record the financial transaction
        record_financial_transaction(
            db=db,
            business_id=None,  # Not associated with a business yet
            transaction_type=TransactionType.PURCHASE,
            amount=initial_funding,
            description=f"Initial funding for construction project: {construction_data['project_name']}",
            is_income=False,
            related_entity_id=property_id,
            category="construction"
        )
        
        self.logger.info(f"Player {player_id} commissioned construction project {project_data.id}")
        
        return project_data
    
    def apply_for_business_license(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        license_data: Dict[str, Any]
    ) -> BusinessLicense:
        """
        Apply for a business license.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            license_data: License application details
            
        Returns:
            Business license application
        """
        # Validate license data
        required_fields = ["license_type_name", "issuing_authority_name", "application_fee"]
        
        for field in required_fields:
            if field not in license_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create license application
        license_data = BusinessLicense(
            id=f"license-{uuid4().hex}",
            player_business_profile_id=business_id,
            license_type_name=license_data["license_type_name"],
            issuing_authority_name=license_data["issuing_authority_name"],
            issuing_authority_contact_npc_id=license_data.get("issuing_authority_contact_npc_id"),
            application_date=datetime.utcnow(),
            application_fee=license_data["application_fee"],
            renewal_fee=license_data.get("renewal_fee"),
            status=BusinessLicenseStatus.PENDING_APPLICATION.value,
            requirements_met=license_data.get("requirements_met", {}),
            notes=license_data.get("notes"),
            benefits_description=license_data.get("benefits_description"),
            restrictions=license_data.get("restrictions"),
            custom_data=license_data.get("custom_data", {})
        )
        
        # Save to database
        license_obj = create_business_license(db, license_data, business_id)
        
        # Record the financial transaction
        record_financial_transaction(
            db=db,
            business_id=business_id,
            transaction_type=TransactionType.TAX_PAYMENT,
            amount=license_data["application_fee"],
            description=f"Application fee for {license_data['license_type_name']} license",
            is_income=False,
            related_entity_id=license_data.get("issuing_authority_contact_npc_id"),
            related_entity_name=license_data["issuing_authority_name"],
            category="licensing"
        )
        
        self.logger.info(f"Business {business_id} applied for license {license_obj.id}")
        
        return license_obj
    
    def officially_open_business(
        self,
        db: Session,
        player_id: str,
        business_data: Dict[str, Any],
        property_deed_id: Optional[str] = None,
        lease_agreement_id: Optional[str] = None,
        initial_inventory: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> PlayerBusinessProfile:
        """
        Officially open a business at a property.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_data: Business details
            property_deed_id: Optional property deed ID if owned
            lease_agreement_id: Optional lease agreement ID if leased
            initial_inventory: Optional initial inventory items
            
        Returns:
            Created business profile
        """
        # Validate business data
        required_fields = ["business_name_player_chosen", "business_type"]
        
        for field in required_fields:
            if field not in business_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate property ownership or lease
        if not property_deed_id and not lease_agreement_id:
            raise ValueError("Either property_deed_id or lease_agreement_id must be provided")
            
        if property_deed_id:
            property_deed = get_property_deed(db, property_deed_id)
            if not property_deed or property_deed.owner_character_id != player_id:
                raise ValueError(f"Player {player_id} does not own property {property_deed_id}")
                
            # Validate business type against zoning permissions
            if not isinstance(property_deed.zoning_permissions, list) or business_data["business_type"] not in property_deed.zoning_permissions:
                raise ValueError(f"Business type {business_data['business_type']} not allowed in this property")
                
        if lease_agreement_id:
            lease_agreement = get_lease_agreement(db, lease_agreement_id)
            if not lease_agreement or lease_agreement.tenant_character_id != player_id:
                raise ValueError(f"Player {player_id} does not have lease {lease_agreement_id}")
                
            # Validate business type against zoning permissions
            if not isinstance(lease_agreement.zoning_permissions, list) or business_data["business_type"] not in lease_agreement.zoning_permissions:
                raise ValueError(f"Business type {business_data['business_type']} not allowed in this property")
        
        # Process inventory
        inventory = {}
        if initial_inventory:
            for item_id, item_data in initial_inventory.items():
                inventory[item_id] = {
                    "item_id": item_id,
                    "quantity": item_data.get("quantity", 0),
                    "quality": item_data.get("quality"),
                    "purchase_price_per_unit": item_data.get("purchase_price_per_unit"),
                    "selling_price_per_unit": item_data.get("selling_price_per_unit"),
                    "restock_threshold": item_data.get("restock_threshold"),
                    "category": item_data.get("category"),
                    "is_material": item_data.get("is_material", False),
                    "last_restocked": datetime.utcnow().isoformat() if item_data.get("quantity", 0) > 0 else None,
                    "expiration_date": item_data.get("expiration_date")
                }
        
        # Create business profile
        business_data = PlayerBusinessProfile(
            id=f"business-{uuid4().hex}",
            player_character_id=player_id,
            base_business_id=business_data.get("base_business_id"),
            business_name_player_chosen=business_data["business_name_player_chosen"],
            business_type=business_data["business_type"],
            property_deed_id=property_deed_id,
            lease_agreement_id=lease_agreement_id,
            business_licenses=[],
            shop_ledger=[],
            customization_options_applied=business_data.get("customization_options_applied", {}),
            current_staff_contracts=[],
            current_apprentices=[],
            inventory=inventory,
            installed_fixtures=[],
            active_research_projects=[],
            pending_custom_orders=[],
            completed_custom_orders=[],
            business_hours=business_data.get("business_hours", {}),
            ambiance=business_data.get("ambiance", {}),
            reputation=business_data.get("reputation", {}),
            mastery_level=business_data.get("mastery_level", 1),
            establishment_date=datetime.utcnow(),
            total_revenue=0.0,
            total_expenses=0.0,
            current_balance=business_data.get("initial_balance", 0.0),
            daily_customer_capacity=business_data.get("daily_customer_capacity", 10),
            special_features=business_data.get("special_features", []),
            custom_data=business_data.get("custom_data", {})
        )
        
        # Save to database
        business = create_business(db, business_data)
        
        # Record opening transaction if initial balance is provided
        if business_data.get("initial_balance", 0.0) > 0:
            record_financial_transaction(
                db=db,
                business_id=business.id,
                transaction_type=TransactionType.OTHER,
                amount=business_data.get("initial_balance", 0.0),
                description="Initial business capital",
                is_income=True,
                category="capital"
            )
        
        self.logger.info(f"Player {player_id} opened business {business.id}: {business.business_name_player_chosen}")
        
        return business