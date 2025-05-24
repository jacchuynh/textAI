"""
Player Business Daily Operations Service

This module provides services for managing the day-to-day operations of player-owned businesses,
including customer orders, staff management, inventory, and financial transactions.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, CustomOrderRequest, StaffMemberContract,
    InventoryItem, CustomerInteraction, DailyBusinessSummary,
    BusinessType, CustomOrderStatus, StaffRole, TransactionType
)
from backend.src.business.crud import (
    get_business, update_business, 
    create_custom_order, update_custom_order, get_custom_order, get_custom_orders_by_business,
    get_staff_contract, update_staff_contract, get_staff_contracts_by_business,
    record_financial_transaction, record_customer_interaction, create_daily_business_summary,
    create_staff_job_listing, close_staff_job_listing
)

logger = logging.getLogger(__name__)

class PlayerBusinessDailyOperationsService:
    """Service for managing the day-to-day operations of player-owned businesses."""
    
    def __init__(self):
        self.logger = logging.getLogger("PlayerBusinessDailyOperationsService")
    
    # === CUSTOM ORDER HANDLING METHODS ===
    
    def review_incoming_custom_order_requests(
        self,
        db: Session,
        business_id: str
    ) -> List[CustomOrderRequest]:
        """
        Get a list of pending custom order requests that need player review.
        
        Args:
            db: Database session
            business_id: Business profile ID
            
        Returns:
            List of custom order requests awaiting player review
        """
        # Get orders with AWAITING_PLAYER_REVIEW status
        orders = get_custom_orders_by_business(
            db, 
            business_id, 
            status_filter=[CustomOrderStatus.AWAITING_PLAYER_REVIEW.value]
        )
        
        # Sort by deadline (earliest first)
        orders.sort(key=lambda order: order.deadline_date)
        
        return orders
    
    def accept_or_decline_custom_order(
        self,
        db: Session,
        order_id: str,
        accept: bool,
        counter_offer_price: Optional[float] = None,
        player_notes: Optional[str] = None
    ) -> CustomOrderRequest:
        """
        Accept or decline a custom order request, with optional counter-offer.
        
        Args:
            db: Database session
            order_id: Order request ID
            accept: Whether to accept (True) or decline (False) the order
            counter_offer_price: Optional counter-offer price (if accepting with new price)
            player_notes: Optional notes from the player
            
        Returns:
            Updated custom order request
        """
        # Get the order
        order = get_custom_order(db, order_id)
        if not order:
            raise ValueError(f"Custom order {order_id} not found")
            
        # Check if order is in the right state
        if order.status != CustomOrderStatus.AWAITING_PLAYER_REVIEW.value:
            raise ValueError(f"Custom order {order_id} is not awaiting player review")
        
        # Update order
        update_data = {}
        
        if accept:
            update_data["status"] = CustomOrderStatus.PLAYER_ACCEPTED.value
            
            # Handle counter-offer
            if counter_offer_price is not None:
                update_data["negotiated_price_final"] = counter_offer_price
            else:
                update_data["negotiated_price_final"] = order.offered_price_initial
                
            # Add to custom_data for tracking
            custom_data = order.custom_data or {}
            custom_data["accepted_date"] = datetime.utcnow().isoformat()
            
            # Determine NPC reaction to counter-offer
            if counter_offer_price is not None:
                price_ratio = counter_offer_price / order.offered_price_initial
                
                if price_ratio > 1.2:  # More than 20% increase
                    # NPC might be upset or cancel
                    if random.random() < 0.3:  # 30% chance to cancel
                        update_data["status"] = CustomOrderStatus.CANCELLED_BY_NPC.value
                        custom_data["cancellation_reason"] = "Price too high"
                        custom_data["cancelled_date"] = datetime.utcnow().isoformat()
                    else:
                        custom_data["npc_reaction"] = "Reluctantly accepted higher price"
                elif price_ratio > 1.1:  # 10-20% increase
                    custom_data["npc_reaction"] = "Somewhat disappointed with higher price"
                elif price_ratio < 0.9:  # More than 10% discount
                    custom_data["npc_reaction"] = "Very pleased with lower price"
                    # Could add bonus to reputation here
                elif price_ratio < 0.95:  # 5-10% discount
                    custom_data["npc_reaction"] = "Happy with the discount"
                else:
                    custom_data["npc_reaction"] = "Satisfied with the price"
            
            update_data["custom_data"] = custom_data
        else:
            # Decline the order
            update_data["status"] = CustomOrderStatus.PLAYER_REJECTED.value
            
            # Add to custom_data for tracking
            custom_data = order.custom_data or {}
            custom_data["rejected_date"] = datetime.utcnow().isoformat()
            custom_data["rejection_reason"] = player_notes or "No reason provided"
            update_data["custom_data"] = custom_data
        
        # Add player notes if provided
        if player_notes:
            update_data["player_notes_on_order"] = player_notes
        
        # Update the order
        updated_order = update_custom_order(db, order_id, update_data)
        
        self.logger.info(f"Custom order {order_id} {'accepted' if accept else 'declined'} by player")
        
        return updated_order
    
    def plan_material_sourcing_for_order(
        self,
        db: Session,
        business_id: str,
        order_id: str
    ) -> Dict[str, Any]:
        """
        Plan material sourcing for a custom order, checking what's in stock and what needs to be purchased.
        
        Args:
            db: Database session
            business_id: Business profile ID
            order_id: Custom order ID
            
        Returns:
            Dictionary with materials needed, in stock, and to purchase
        """
        # Get the order
        order = get_custom_order(db, order_id)
        if not order:
            raise ValueError(f"Custom order {order_id} not found")
            
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Check materials required
        materials_required = order.materials_required or {}
        inventory = business.inventory or {}
        
        materials_in_stock = {}
        materials_to_purchase = {}
        
        # Track total costs
        total_cost = 0.0
        
        for material_id, quantity_needed in materials_required.items():
            # Check if in stock
            if material_id in inventory and inventory[material_id]["quantity"] > 0:
                quantity_available = inventory[material_id]["quantity"]
                
                if quantity_available >= quantity_needed:
                    # Have enough
                    materials_in_stock[material_id] = {
                        "item_id": material_id,
                        "quantity_needed": quantity_needed,
                        "quantity_available": quantity_available,
                        "name": inventory[material_id].get("name", f"Material {material_id}"),
                        "unit_cost": inventory[material_id].get("purchase_price_per_unit", 0.0)
                    }
                    total_cost += quantity_needed * inventory[material_id].get("purchase_price_per_unit", 0.0)
                else:
                    # Partially in stock
                    materials_in_stock[material_id] = {
                        "item_id": material_id,
                        "quantity_needed": quantity_needed,
                        "quantity_available": quantity_available,
                        "name": inventory[material_id].get("name", f"Material {material_id}"),
                        "unit_cost": inventory[material_id].get("purchase_price_per_unit", 0.0)
                    }
                    
                    quantity_to_purchase = quantity_needed - quantity_available
                    materials_to_purchase[material_id] = {
                        "item_id": material_id,
                        "quantity_to_purchase": quantity_to_purchase,
                        "name": inventory[material_id].get("name", f"Material {material_id}"),
                        "estimated_unit_cost": inventory[material_id].get("purchase_price_per_unit", 0.0)
                    }
                    
                    total_cost += quantity_available * inventory[material_id].get("purchase_price_per_unit", 0.0)
                    total_cost += quantity_to_purchase * inventory[material_id].get("purchase_price_per_unit", 0.0)
            else:
                # Not in stock at all
                # For estimation, we'll use a placeholder cost or look up from a reference
                estimated_unit_cost = self._estimate_material_cost(material_id, business.business_type)
                
                materials_to_purchase[material_id] = {
                    "item_id": material_id,
                    "quantity_to_purchase": quantity_needed,
                    "name": f"Material {material_id}",
                    "estimated_unit_cost": estimated_unit_cost
                }
                
                total_cost += quantity_needed * estimated_unit_cost
        
        # Update the order with material planning
        update_data = {
            "status": CustomOrderStatus.MATERIALS_GATHERING.value,
            "custom_data": order.custom_data or {}
        }
        
        update_data["custom_data"]["material_planning"] = {
            "materials_in_stock": materials_in_stock,
            "materials_to_purchase": materials_to_purchase,
            "total_estimated_material_cost": total_cost,
            "planning_date": datetime.utcnow().isoformat()
        }
        
        update_custom_order(db, order_id, update_data)
        
        # Return the planning results
        return {
            "order_id": order_id,
            "materials_in_stock": materials_in_stock,
            "materials_to_purchase": materials_to_purchase,
            "total_estimated_material_cost": total_cost,
            "order_price": order.negotiated_price_final or order.offered_price_initial,
            "estimated_profit": (order.negotiated_price_final or order.offered_price_initial) - total_cost
        }
    
    def _estimate_material_cost(self, material_id: str, business_type: str) -> float:
        """
        Estimate the cost of a material not in inventory.
        
        Args:
            material_id: Material ID
            business_type: Type of business
            
        Returns:
            Estimated unit cost
        """
        # In a real implementation, this would query a market database or item database
        # For now, return a simple estimate
        
        # Base cost by material ID (just using ID as a numeric seed)
        base_cost = 5.0 + (int(material_id.replace("item-", "").replace("material-", "")) % 10) * 2.5
        
        # Adjust by business type (some businesses get certain materials cheaper)
        business_type_modifiers = {
            BusinessType.BLACKSMITH.value: {"metals": 0.8, "wood": 1.2},
            BusinessType.APOTHECARY.value: {"herbs": 0.7, "minerals": 0.9},
            BusinessType.TAILOR.value: {"cloth": 0.75, "leather": 0.9},
            BusinessType.JEWELER.value: {"gems": 0.85, "metals": 0.9},
            BusinessType.CARPENTER.value: {"wood": 0.7, "metals": 1.1},
            BusinessType.ALCHEMIST.value: {"herbs": 0.8, "minerals": 0.8}
        }
        
        # Simplified material category inference
        category = "general"
        if "metal" in material_id or "iron" in material_id or "steel" in material_id:
            category = "metals"
        elif "herb" in material_id or "plant" in material_id:
            category = "herbs"
        elif "wood" in material_id or "timber" in material_id:
            category = "wood"
        elif "cloth" in material_id or "fabric" in material_id:
            category = "cloth"
        elif "leather" in material_id or "hide" in material_id:
            category = "leather"
        elif "gem" in material_id or "crystal" in material_id:
            category = "gems"
        elif "mineral" in material_id or "stone" in material_id:
            category = "minerals"
        
        # Apply modifier if available
        modifier = 1.0
        if business_type in business_type_modifiers and category in business_type_modifiers[business_type]:
            modifier = business_type_modifiers[business_type][category]
        
        return base_cost * modifier
    
    def initiate_crafting_session(
        self,
        db: Session,
        business_id: str,
        item_to_craft: Union[str, Dict[str, Any]],
        crafter_id: str,
        is_custom_order: bool = False,
        staff_ids: Optional[List[str]] = None,
        player_skill_level: int = 1
    ) -> Dict[str, Any]:
        """
        Initiate a crafting session for either a custom order or a standard item.
        
        Args:
            db: Database session
            business_id: Business profile ID
            item_to_craft: Either a custom order ID or item details
            crafter_id: Player character ID or NPC ID of primary crafter
            is_custom_order: Whether this is a custom order
            staff_ids: Optional list of staff IDs assisting
            player_skill_level: Skill level of the player (1-10)
            
        Returns:
            Dictionary with crafting session details
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Initialize crafting session
        crafting_id = f"crafting-{uuid4().hex[:8]}"
        
        staff_assists = []
        if staff_ids:
            # Validate staff IDs and collect their skills
            for staff_id in staff_ids:
                staff = get_staff_contract(db, staff_id)
                if not staff or staff.player_business_profile_id != business_id:
                    raise ValueError(f"Staff member {staff_id} not found or not employed by this business")
                
                staff_assists.append({
                    "staff_id": staff_id,
                    "role": staff.role_title,
                    "skills": staff.skills,
                    "contribution_factor": 0.2 + (sum(staff.skills.values()) / 100) if staff.skills else 0.2
                })
        
        if is_custom_order:
            # Handle custom order
            order_id = item_to_craft if isinstance(item_to_craft, str) else None
            if not order_id:
                raise ValueError("Custom order ID must be provided")
                
            order = get_custom_order(db, order_id)
            if not order:
                raise ValueError(f"Custom order {order_id} not found")
                
            # Check if order is ready for crafting
            if order.status not in [CustomOrderStatus.PLAYER_ACCEPTED.value, CustomOrderStatus.MATERIALS_GATHERING.value]:
                raise ValueError(f"Custom order {order_id} is not ready for crafting")
            
            # Calculate crafting time based on difficulty and skills
            difficulty = order.crafting_difficulty or 5
            base_crafting_time = difficulty * 2  # hours
            
            # Adjust for player skill
            skill_modifier = 1.0 - (player_skill_level - 1) * 0.05  # 5% reduction per skill level
            
            # Adjust for staff assistance
            staff_modifier = 1.0
            for staff in staff_assists:
                staff_modifier -= staff["contribution_factor"]
            staff_modifier = max(0.5, staff_modifier)  # Cap at 50% reduction
            
            crafting_time = base_crafting_time * skill_modifier * staff_modifier
            
            # Calculate quality based on skills
            base_quality = 0.5 + (player_skill_level / 20)  # 0.5 to 1.0
            
            # Add staff quality bonus
            for staff in staff_assists:
                avg_staff_skill = sum(staff["skills"].values()) / max(1, len(staff["skills"]))
                base_quality += (avg_staff_skill / 200)  # Small boost per staff
            
            # Cap quality at 1.0
            quality = min(1.0, base_quality)
            
            # Update order status
            update_custom_order(db, order_id, {
                "status": CustomOrderStatus.CRAFTING_IN_PROGRESS.value,
                "custom_data": {
                    **(order.custom_data or {}),
                    "crafting_session": {
                        "crafting_id": crafting_id,
                        "start_time": datetime.utcnow().isoformat(),
                        "estimated_completion_time": (datetime.utcnow() + timedelta(hours=crafting_time)).isoformat(),
                        "primary_crafter_id": crafter_id,
                        "assisting_staff_ids": staff_ids or [],
                        "estimated_quality": quality,
                        "crafting_time_hours": crafting_time
                    }
                }
            })
            
            # Create crafting session
            crafting_session = {
                "crafting_id": crafting_id,
                "business_id": business_id,
                "is_custom_order": True,
                "order_id": order_id,
                "item_name": f"Custom {order.item_category_hint or 'Item'} for {order.requesting_npc_id}",
                "item_description": order.item_description_by_npc,
                "primary_crafter_id": crafter_id,
                "assisting_staff_ids": staff_ids or [],
                "start_time": datetime.utcnow().isoformat(),
                "estimated_completion_time": (datetime.utcnow() + timedelta(hours=crafting_time)).isoformat(),
                "estimated_quality": quality,
                "crafting_time_hours": crafting_time,
                "materials_used": order.materials_required or {},
                "status": "in_progress"
            }
            
            # In a real implementation, this would be stored in a database table
            # For now, we just update the order
            
            self.logger.info(f"Crafting session {crafting_id} started for custom order {order_id}")
            
            return crafting_session
        else:
            # Handle standard item crafting
            if not isinstance(item_to_craft, dict):
                raise ValueError("Item details must be provided for standard crafting")
                
            # Extract item details
            item_id = item_to_craft.get("item_id")
            if not item_id:
                raise ValueError("Item ID must be provided")
                
            item_name = item_to_craft.get("name", f"Item {item_id}")
            quantity = item_to_craft.get("quantity", 1)
            materials_required = item_to_craft.get("materials_required", {})
            
            # Check materials in inventory
            inventory = business.inventory or {}
            for material_id, quantity_needed in materials_required.items():
                quantity_needed_total = quantity_needed * quantity
                
                if material_id not in inventory or inventory[material_id]["quantity"] < quantity_needed_total:
                    raise ValueError(f"Not enough {material_id} in inventory")
            
            # Calculate crafting time
            difficulty = item_to_craft.get("difficulty", 3)
            base_crafting_time = difficulty * quantity * 1.5  # hours per item
            
            # Adjust for player skill
            skill_modifier = 1.0 - (player_skill_level - 1) * 0.05  # 5% reduction per skill level
            
            # Adjust for staff assistance
            staff_modifier = 1.0
            for staff in staff_assists:
                staff_modifier -= staff["contribution_factor"]
            staff_modifier = max(0.5, staff_modifier)  # Cap at 50% reduction
            
            crafting_time = base_crafting_time * skill_modifier * staff_modifier
            
            # Calculate quality based on skills
            base_quality = 0.5 + (player_skill_level / 20)  # 0.5 to 1.0
            
            # Add staff quality bonus
            for staff in staff_assists:
                avg_staff_skill = sum(staff["skills"].values()) / max(1, len(staff["skills"]))
                base_quality += (avg_staff_skill / 200)  # Small boost per staff
            
            # Cap quality at 1.0
            quality = min(1.0, base_quality)
            
            # Create crafting session
            crafting_session = {
                "crafting_id": crafting_id,
                "business_id": business_id,
                "is_custom_order": False,
                "item_id": item_id,
                "item_name": item_name,
                "quantity": quantity,
                "primary_crafter_id": crafter_id,
                "assisting_staff_ids": staff_ids or [],
                "start_time": datetime.utcnow().isoformat(),
                "estimated_completion_time": (datetime.utcnow() + timedelta(hours=crafting_time)).isoformat(),
                "estimated_quality": quality,
                "crafting_time_hours": crafting_time,
                "materials_used": materials_required,
                "status": "in_progress"
            }
            
            # Update inventory to remove used materials
            for material_id, quantity_needed in materials_required.items():
                quantity_needed_total = quantity_needed * quantity
                
                # Update inventory
                new_inventory = business.inventory.copy()
                new_inventory[material_id]["quantity"] -= quantity_needed_total
                
                # Record material usage
                record_financial_transaction(
                    db=db,
                    business_id=business_id,
                    transaction_type=TransactionType.OTHER,
                    amount=quantity_needed_total * (new_inventory[material_id].get("purchase_price_per_unit", 0.0)),
                    description=f"Materials used for crafting {item_name} x{quantity}",
                    is_income=False,
                    category="crafting_materials"
                )
            
            # Update business inventory
            update_business(db, business_id, {"inventory": new_inventory})
            
            self.logger.info(f"Crafting session {crafting_id} started for standard item {item_id}")
            
            return crafting_session
    
    # === STAFF MANAGEMENT METHODS ===
    
    def post_job_listing_for_staff(
        self,
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
        listing_duration_days: int = 14
    ) -> str:
        """
        Post a job listing to attract NPC applicants.
        
        Args:
            db: Database session
            business_id: Business profile ID
            role_title: Title of the role
            role_description: Description of the role
            wage_range_min: Minimum wage offered
            wage_range_max: Maximum wage offered
            working_hours_description: Description of working hours
            required_skills: Optional required skills and levels
            preferred_skills: Optional preferred skills and levels
            benefits_offered: Optional benefits description
            listing_duration_days: Duration in days to keep the listing active
            
        Returns:
            Job listing ID
        """
        # Validate inputs
        if wage_range_min > wage_range_max:
            raise ValueError("Minimum wage cannot be higher than maximum wage")
            
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=listing_duration_days)
        
        # Create job listing
        listing_id = create_staff_job_listing(
            db=db,
            business_id=business_id,
            role_title=role_title,
            role_description=role_description,
            wage_range_min=wage_range_min,
            wage_range_max=wage_range_max,
            working_hours_description=working_hours_description,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            benefits_offered=benefits_offered,
            expiry_date=expiry_date
        )
        
        # In a real implementation, this would potentially trigger NPC application generation
        # over the next few days, based on business reputation, location, etc.
        
        self.logger.info(f"Job listing {listing_id} posted for business {business_id}")
        
        return listing_id
    
    def interview_npc_applicant(
        self,
        db: Session,
        business_id: str,
        npc_id: str,
        player_charisma: int = 5,
        interview_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Interview an NPC applicant for a job position.
        
        Args:
            db: Database session
            business_id: Business profile ID
            npc_id: NPC character ID
            player_charisma: Player's charisma attribute (1-10)
            interview_questions: Optional list of questions to ask
            
        Returns:
            Dictionary with interview results
        """
        # In a real implementation, this would query NPC data and job listing
        # For now, we'll generate a simulated response
        
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Generate NPC personality and skills (randomly for demonstration)
        personality_traits = ["friendly", "ambitious", "nervous", "confident", "diligent", "creative"]
        npc_personality = random.sample(personality_traits, 3)
        
        # Generate skills based on business type
        npc_skills = {}
        
        if business.business_type == BusinessType.BLACKSMITH.value:
            npc_skills = {
                "smithing": random.randint(1, 8),
                "metalworking": random.randint(1, 7),
                "strength": random.randint(3, 8),
                "customer_service": random.randint(1, 6)
            }
        elif business.business_type == BusinessType.APOTHECARY.value:
            npc_skills = {
                "herbalism": random.randint(1, 8),
                "alchemy": random.randint(1, 7),
                "medicine": random.randint(2, 7),
                "customer_service": random.randint(2, 6)
            }
        elif business.business_type == BusinessType.TAILOR.value:
            npc_skills = {
                "sewing": random.randint(1, 8),
                "design": random.randint(1, 7),
                "color_theory": random.randint(2, 7),
                "customer_service": random.randint(3, 7)
            }
        else:
            # Generic skills
            npc_skills = {
                "crafting": random.randint(1, 6),
                "organization": random.randint(2, 7),
                "customer_service": random.randint(2, 8)
            }
        
        # Generate wage expectations (random for now)
        min_wage_expectation = 5 + random.randint(0, 10)
        max_wage_expectation = min_wage_expectation + random.randint(1, 5)
        
        # Simulate the interview process
        interview_compatibility = random.random() * 0.5 + 0.3  # Base between 0.3 and 0.8
        
        # Adjust for player charisma
        interview_compatibility += (player_charisma - 5) * 0.03  # +/- 0.15 for charisma
        
        # Adjust based on questions if provided
        if interview_questions:
            question_bonus = len(interview_questions) * 0.02  # More questions = better understanding
            interview_compatibility = min(1.0, interview_compatibility + question_bonus)
        
        # Generate interview responses
        interview_responses = {}
        if interview_questions:
            for question in interview_questions:
                interview_responses[question] = self._generate_npc_interview_response(
                    question, npc_personality, npc_skills
                )
        
        # Calculate overall rating
        overall_rating = min(10, max(1, int(interview_compatibility * 10)))
        
        # Generate recommendation
        recommendation = "Highly recommended" if overall_rating >= 8 else \
                         "Recommended" if overall_rating >= 6 else \
                         "Consider with caution" if overall_rating >= 4 else \
                         "Not recommended"
        
        # Construct result
        interview_result = {
            "npc_id": npc_id,
            "interview_date": datetime.utcnow().isoformat(),
            "npc_personality": npc_personality,
            "npc_skills": npc_skills,
            "wage_expectation": {
                "min": min_wage_expectation,
                "max": max_wage_expectation
            },
            "interview_responses": interview_responses,
            "compatibility_score": interview_compatibility,
            "overall_rating": overall_rating,
            "recommendation": recommendation,
            "notes": f"NPC appears to be {', '.join(npc_personality)}. Skills are particularly strong in {max(npc_skills, key=npc_skills.get)}."
        }
        
        self.logger.info(f"Interviewed NPC {npc_id} for business {business_id}, rating: {overall_rating}/10")
        
        return interview_result
    
    def _generate_npc_interview_response(
        self,
        question: str,
        personality: List[str],
        skills: Dict[str, int]
    ) -> str:
        """
        Generate a response for an NPC during an interview based on their personality and skills.
        
        Args:
            question: The question asked
            personality: List of personality traits
            skills: Dictionary of skills and levels
            
        Returns:
            NPC's response
        """
        # Very simple response generation based on keywords in the question
        # In a real implementation, this would be much more sophisticated
        
        question_lower = question.lower()
        
        # Experience questions
        if "experience" in question_lower or "worked" in question_lower:
            top_skill = max(skills, key=skills.get)
            skill_level = skills[top_skill]
            
            if skill_level >= 7:
                return f"I've been practicing {top_skill} for many years now. I apprenticed with a master in the capital city and have been honing my craft ever since."
            elif skill_level >= 4:
                return f"I have several years of experience with {top_skill}. I've worked at a few different establishments and learned a great deal."
            else:
                return f"I'm still relatively new to {top_skill}, but I'm a quick learner and very passionate about improving."
        
        # Personality questions
        elif "yourself" in question_lower or "about you" in question_lower:
            personality_str = ", ".join(personality[:-1]) + " and " + personality[-1]
            return f"I would describe myself as {personality_str}. I take pride in my work and always strive to improve."
        
        # Availability questions
        elif "available" in question_lower or "hours" in question_lower or "schedule" in question_lower:
            if "diligent" in personality:
                return "I'm available whenever you need me. I'm very dedicated to my work and can adjust my schedule as needed."
            else:
                return "I'm available most days, though I do prefer to have at least one day off per week to rest."
        
        # Wage questions
        elif "wage" in question_lower or "pay" in question_lower or "salary" in question_lower:
            if "ambitious" in personality:
                return "I believe my skills are valuable, but I'm willing to negotiate a fair wage that works for both of us."
            else:
                return "I'm just looking for fair compensation for my work. I'm sure we can come to an agreement."
        
        # Goals questions
        elif "goal" in question_lower or "future" in question_lower:
            if "ambitious" in personality:
                return "I'm hoping to eventually become a master in my craft. Working here would be an excellent opportunity to learn and grow."
            elif "creative" in personality:
                return "I want to push the boundaries of what's possible in this field. I have many ideas I'd like to explore."
            else:
                return "I'm looking for a stable position where I can practice my trade and make a good living."
        
        # Default response
        else:
            if "friendly" in personality:
                return "That's an interesting question! I'd be happy to discuss that further if you'd like."
            elif "nervous" in personality:
                return "Um, well... I'm not entirely sure how to answer that, but I'll do my best."
            else:
                return "I think I have the skills and temperament that would make me a good fit for this position."
    
    def hire_staff_member(
        self,
        db: Session,
        business_id: str,
        npc_id: str,
        role_title: str,
        agreed_wage_per_period: float,
        wage_payment_schedule: str,
        assigned_tasks_description: str,
        work_schedule: Dict[str, Any],
        contract_duration_months: Optional[int] = None,
        is_probationary: bool = False,
        probation_period_days: int = 30,
        benefits: Optional[str] = None
    ) -> StaffMemberContract:
        """
        Hire an NPC as staff for the business.
        
        Args:
            db: Database session
            business_id: Business profile ID
            npc_id: NPC character ID
            role_title: Title of the role
            agreed_wage_per_period: Agreed wage per payment period
            wage_payment_schedule: Schedule for wage payments (e.g., "weekly", "monthly")
            assigned_tasks_description: Description of assigned tasks
            work_schedule: Work schedule details
            contract_duration_months: Optional contract duration in months (None = permanent)
            is_probationary: Whether this is a probationary contract
            probation_period_days: Length of probation period in days
            benefits: Optional benefits provided
            
        Returns:
            Created staff contract
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Prepare contract data
        contract_start_date = datetime.utcnow()
        contract_end_date = None
        if contract_duration_months:
            contract_end_date = contract_start_date + timedelta(days=contract_duration_months * 30)
            
        probation_end_date = None
        if is_probationary:
            probation_end_date = contract_start_date + timedelta(days=probation_period_days)
        
        # Create schedule data
        schedule_data = {
            "days": work_schedule.get("days", []),
            "start_time": work_schedule.get("start_time"),
            "end_time": work_schedule.get("end_time"),
            "break_start": work_schedule.get("break_start"),
            "break_end": work_schedule.get("break_end")
        }
        
        # Create contract with placeholder skills (would be populated from NPC data in a real system)
        contract_data = StaffMemberContract(
            id=f"contract-{uuid4().hex}",
            player_business_profile_id=business_id,
            npc_id=npc_id,
            role_title=role_title,
            agreed_wage_per_period=agreed_wage_per_period,
            wage_payment_schedule=wage_payment_schedule,
            assigned_tasks_description=assigned_tasks_description,
            work_schedule=schedule_data,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
            current_morale_level=8,  # Start with good morale
            performance_notes_by_player=None,
            skills={},  # Would be populated from NPC data
            last_wage_payment_date=None,
            is_probationary=is_probationary,
            probation_end_date=probation_end_date,
            benefits=benefits,
            custom_data={
                "hiring_date": contract_start_date.isoformat()
            }
        )
        
        # Save to database (this create_staff_contract function would need to be implemented)
        contract = create_staff_contract(db, contract_data, business_id)
        
        # Add to business staff contracts list
        current_staff_contracts = business.current_staff_contracts or []
        current_staff_contracts.append(contract.id)
        update_business(db, business_id, {"current_staff_contracts": current_staff_contracts})
        
        # Record transaction for any signing bonus or initial payment
        if "signing_bonus" in contract_data.custom_data:
            signing_bonus = contract_data.custom_data["signing_bonus"]
            record_financial_transaction(
                db=db,
                business_id=business_id,
                transaction_type=TransactionType.WAGE_PAYMENT,
                amount=signing_bonus,
                description=f"Signing bonus for {npc_id} as {role_title}",
                is_income=False,
                related_entity_id=npc_id,
                related_entity_name=npc_id,  # Would be NPC name in a real system
                category="staff_wages"
            )
        
        self.logger.info(f"Hired NPC {npc_id} as {role_title} for business {business_id}")
        
        return contract
    
    def assign_daily_tasks_to_staff(
        self,
        db: Session,
        business_id: str,
        staff_contract_id: str,
        task_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assign daily tasks to a staff member.
        
        Args:
            db: Database session
            business_id: Business profile ID
            staff_contract_id: Staff contract ID
            task_list: List of tasks to assign
            
        Returns:
            Dictionary with task assignment results
        """
        # Get the staff contract
        staff = get_staff_contract(db, staff_contract_id)
        if not staff:
            raise ValueError(f"Staff contract {staff_contract_id} not found")
            
        if staff.player_business_profile_id != business_id:
            raise ValueError(f"Staff member {staff_contract_id} is not employed by business {business_id}")
        
        # Validate task list
        if not task_list or not isinstance(task_list, list):
            raise ValueError("Task list must be a non-empty list")
            
        for task in task_list:
            if not isinstance(task, dict) or "task_type" not in task:
                raise ValueError("Each task must be a dictionary with at least a task_type field")
        
        # Update staff contract with assigned tasks
        custom_data = staff.custom_data or {}
        task_history = custom_data.get("task_history", [])
        
        # Add new task assignment
        task_assignment = {
            "assignment_date": datetime.utcnow().isoformat(),
            "tasks": task_list,
            "status": "assigned"
        }
        
        task_history.append(task_assignment)
        custom_data["task_history"] = task_history
        custom_data["current_tasks"] = task_list
        
        update_staff_contract(db, staff_contract_id, {"custom_data": custom_data})
        
        # Return the assignment details
        return {
            "staff_id": staff_contract_id,
            "npc_id": staff.npc_id,
            "assignment_date": datetime.utcnow().isoformat(),
            "tasks": task_list,
            "estimated_completion": self._estimate_task_completion(task_list, staff.skills)
        }
    
    def _estimate_task_completion(
        self,
        task_list: List[Dict[str, Any]],
        staff_skills: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Estimate how well a staff member will complete their tasks based on their skills.
        
        Args:
            task_list: List of tasks assigned
            staff_skills: Staff member's skills
            
        Returns:
            Dictionary with completion estimates
        """
        # In a real implementation, this would be more sophisticated
        # For now, make a simple estimate
        
        estimated_quality = 0.5  # Base quality
        estimated_efficiency = 0.5  # Base efficiency
        
        # Iterate through tasks and relevant skills
        for task in task_list:
            task_type = task.get("task_type")
            
            # Different task types rely on different skills
            relevant_skills = []
            
            if task_type == "crafting":
                relevant_skills = ["crafting", "smithing", "alchemy", "sewing", "woodworking"]
            elif task_type == "customer_service":
                relevant_skills = ["customer_service", "speech", "charisma", "social"]
            elif task_type == "cleaning":
                relevant_skills = ["cleaning", "organization", "diligence"]
            elif task_type == "inventory":
                relevant_skills = ["organization", "counting", "attention_to_detail"]
            elif task_type == "training":
                relevant_skills = ["teaching", "leadership", "knowledge"]
            
            # Check if staff has any relevant skills
            for skill in relevant_skills:
                if skill in staff_skills:
                    skill_level = staff_skills[skill]
                    estimated_quality += (skill_level / 100)  # Small boost per skill level
                    estimated_efficiency += (skill_level / 80)  # Slightly larger efficiency boost
        
        # Cap values at reasonable levels
        estimated_quality = min(1.0, estimated_quality)
        estimated_efficiency = min(1.0, estimated_efficiency)
        
        # Calculate time efficiency factor (lower is faster)
        time_factor = 1.0 - (estimated_efficiency - 0.5)  # 0.5 to 1.0 maps to 1.0 to 0.5
        
        return {
            "estimated_quality": estimated_quality,
            "estimated_efficiency": estimated_efficiency,
            "time_factor": time_factor,
            "likelihood_of_success": "High" if estimated_quality > 0.8 else "Medium" if estimated_quality > 0.6 else "Low"
        }
    
    def conduct_staff_performance_review(
        self,
        db: Session,
        business_id: str,
        staff_contract_id: str,
        performance_rating: int,
        performance_notes: str,
        wage_adjustment: Optional[float] = None,
        promotion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct a performance review for a staff member.
        
        Args:
            db: Database session
            business_id: Business profile ID
            staff_contract_id: Staff contract ID
            performance_rating: Performance rating (1-10)
            performance_notes: Performance notes
            wage_adjustment: Optional wage adjustment (can be positive or negative)
            promotion: Optional new role title for promotion
            
        Returns:
            Dictionary with review results
        """
        # Get the staff contract
        staff = get_staff_contract(db, staff_contract_id)
        if not staff:
            raise ValueError(f"Staff contract {staff_contract_id} not found")
            
        if staff.player_business_profile_id != business_id:
            raise ValueError(f"Staff member {staff_contract_id} is not employed by business {business_id}")
        
        # Validate inputs
        if performance_rating < 1 or performance_rating > 10:
            raise ValueError("Performance rating must be between 1 and 10")
            
        # Calculate morale impact
        old_morale = staff.current_morale_level
        morale_change = 0
        
        # Performance rating affects morale
        if performance_rating >= 8:
            morale_change += 1  # Good review boosts morale
        elif performance_rating <= 3:
            morale_change -= 2  # Bad review hurts morale significantly
            
        # Wage adjustment affects morale
        if wage_adjustment:
            if wage_adjustment > 0:
                morale_change += 2  # Raise boosts morale significantly
            elif wage_adjustment < 0:
                morale_change -= 3  # Pay cut hurts morale severely
                
        # Promotion affects morale
        if promotion:
            morale_change += 3  # Promotion boosts morale significantly
        
        # Calculate new morale level (capped at 1-10)
        new_morale = max(1, min(10, old_morale + morale_change))
        
        # Update staff contract
        update_data = {
            "performance_notes_by_player": performance_notes,
            "current_morale_level": new_morale
        }
        
        # Handle wage adjustment
        if wage_adjustment:
            new_wage = staff.agreed_wage_per_period + wage_adjustment
            if new_wage <= 0:
                raise ValueError("Wage adjustment would result in non-positive wage")
                
            update_data["agreed_wage_per_period"] = new_wage
        
        # Handle promotion
        if promotion:
            update_data["role_title"] = promotion
            
        # Add to custom data
        custom_data = staff.custom_data or {}
        performance_reviews = custom_data.get("performance_reviews", [])
        
        review_data = {
            "review_date": datetime.utcnow().isoformat(),
            "performance_rating": performance_rating,
            "performance_notes": performance_notes,
            "wage_adjustment": wage_adjustment,
            "promotion": promotion,
            "morale_before": old_morale,
            "morale_after": new_morale
        }
        
        performance_reviews.append(review_data)
        custom_data["performance_reviews"] = performance_reviews
        custom_data["last_review_date"] = datetime.utcnow().isoformat()
        
        update_data["custom_data"] = custom_data
        
        # Update the contract
        updated_staff = update_staff_contract(db, staff_contract_id, update_data)
        
        # Create review results
        review_results = {
            "staff_id": staff_contract_id,
            "npc_id": staff.npc_id,
            "review_date": datetime.utcnow().isoformat(),
            "performance_rating": performance_rating,
            "morale_change": morale_change,
            "new_morale_level": new_morale,
            "wage_before": staff.agreed_wage_per_period,
            "wage_after": updated_staff.agreed_wage_per_period,
            "role_before": staff.role_title,
            "role_after": updated_staff.role_title
        }
        
        self.logger.info(f"Conducted performance review for staff {staff_contract_id}, rating: {performance_rating}/10")
        
        return review_results
    
    def pay_staff_wages(
        self,
        db: Session,
        business_id: str,
        payment_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Pay wages to all staff members of the business.
        
        Args:
            db: Database session
            business_id: Business profile ID
            payment_date: Optional payment date (defaults to current date)
            
        Returns:
            Dictionary with payment results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Use current date if not provided
        payment_date = payment_date or datetime.utcnow()
        
        # Get all staff contracts
        staff_contracts = get_staff_contracts_by_business(db, business_id)
        
        # Track payment results
        payment_results = {
            "payment_date": payment_date.isoformat(),
            "total_wages_paid": 0.0,
            "staff_payments": [],
            "staff_count": len(staff_contracts)
        }
        
        # Process each staff member
        for staff in staff_contracts:
            # Check if payment is due based on schedule
            if not self._is_wage_payment_due(staff, payment_date):
                continue
                
            # Calculate payment amount
            payment_amount = staff.agreed_wage_per_period
            
            # Record transaction
            record_financial_transaction(
                db=db,
                business_id=business_id,
                transaction_type=TransactionType.WAGE_PAYMENT,
                amount=payment_amount,
                description=f"Wage payment to {staff.npc_id} ({staff.role_title})",
                is_income=False,
                related_entity_id=staff.npc_id,
                related_entity_name=staff.npc_id,  # Would be NPC name in a real system
                category="staff_wages"
            )
            
            # Update staff contract
            update_staff_contract(db, staff.id, {"last_wage_payment_date": payment_date})
            
            # Update payment results
            payment_results["total_wages_paid"] += payment_amount
            payment_results["staff_payments"].append({
                "staff_id": staff.id,
                "npc_id": staff.npc_id,
                "role_title": staff.role_title,
                "payment_amount": payment_amount
            })
        
        # Update business balance
        update_business(db, business_id, {
            "current_balance": business.current_balance - payment_results["total_wages_paid"],
            "total_expenses": business.total_expenses + payment_results["total_wages_paid"]
        })
        
        self.logger.info(f"Paid wages to {len(payment_results['staff_payments'])} staff members, total: {payment_results['total_wages_paid']}")
        
        return payment_results
    
    def _is_wage_payment_due(self, staff: StaffMemberContract, payment_date: datetime) -> bool:
        """
        Check if a wage payment is due for a staff member.
        
        Args:
            staff: Staff contract
            payment_date: Payment date to check
            
        Returns:
            Whether payment is due
        """
        # If never paid before, payment is due
        if not staff.last_wage_payment_date:
            return True
            
        # Check based on payment schedule
        schedule = staff.wage_payment_schedule.lower()
        last_payment = staff.last_wage_payment_date
        
        if schedule == "daily":
            # Due if payment date is after last payment date
            return payment_date.date() > last_payment.date()
        elif schedule == "weekly":
            # Due if a week has passed since last payment
            return (payment_date - last_payment).days >= 7
        elif schedule == "biweekly":
            # Due if two weeks have passed since last payment
            return (payment_date - last_payment).days >= 14
        elif schedule == "monthly":
            # Due if a month has passed (approximated as 30 days)
            return (payment_date - last_payment).days >= 30
        else:
            # Default to monthly
            return (payment_date - last_payment).days >= 30
    
    # === INVENTORY MANAGEMENT METHODS ===
    
    def check_material_stock_levels(
        self,
        db: Session,
        business_id: str
    ) -> Dict[str, Any]:
        """
        Check material stock levels and identify items needing restocking.
        
        Args:
            db: Database session
            business_id: Business profile ID
            
        Returns:
            Dictionary with inventory status
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        inventory = business.inventory or {}
        
        # Track inventory status
        status = {
            "total_items": len(inventory),
            "items_below_threshold": [],
            "out_of_stock_items": [],
            "expiring_soon_items": [],
            "overstocked_items": [],
            "normal_items": []
        }
        
        # Check each inventory item
        for item_id, item_data in inventory.items():
            item_status = {
                "item_id": item_id,
                "name": item_data.get("name", f"Item {item_id}"),
                "quantity": item_data["quantity"],
                "restock_threshold": item_data.get("restock_threshold", 0),
                "is_material": item_data.get("is_material", False)
            }
            
            # Check if out of stock
            if item_data["quantity"] <= 0:
                status["out_of_stock_items"].append(item_status)
                continue
                
            # Check if below threshold
            if "restock_threshold" in item_data and item_data["quantity"] <= item_data["restock_threshold"]:
                status["items_below_threshold"].append(item_status)
                continue
                
            # Check if expiring soon (for perishable items)
            if "expiration_date" in item_data and item_data["expiration_date"]:
                expiration = datetime.fromisoformat(item_data["expiration_date"]) \
                             if isinstance(item_data["expiration_date"], str) else item_data["expiration_date"]
                             
                if (expiration - datetime.utcnow()).days <= 7:  # Expiring within a week
                    item_status["expiration_date"] = expiration.isoformat()
                    item_status["days_until_expiry"] = (expiration - datetime.utcnow()).days
                    status["expiring_soon_items"].append(item_status)
                    continue
            
            # Check if overstocked (for materials, having too much ties up capital)
            if item_data.get("is_material", False) and "restock_threshold" in item_data:
                if item_data["quantity"] >= item_data["restock_threshold"] * 5:  # 5x threshold is overstocked
                    status["overstocked_items"].append(item_status)
                    continue
            
            # If none of the above, item is at normal levels
            status["normal_items"].append(item_status)
        
        return status
    
    def order_materials_from_supplier(
        self,
        db: Session,
        business_id: str,
        orders: List[Dict[str, Any]],
        supplier_id: Optional[str] = None,
        negotiation_skill_level: int = 1
    ) -> Dict[str, Any]:
        """
        Order materials from a supplier.
        
        Args:
            db: Database session
            business_id: Business profile ID
            orders: List of orders to place
            supplier_id: Optional supplier NPC ID
            negotiation_skill_level: Player's negotiation skill (1-10)
            
        Returns:
            Dictionary with order results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Validate orders
        if not orders or not isinstance(orders, list):
            raise ValueError("Orders must be a non-empty list")
            
        for order in orders:
            if not isinstance(order, dict) or "item_id" not in order or "quantity" not in order:
                raise ValueError("Each order must be a dictionary with item_id and quantity fields")
                
            if order["quantity"] <= 0:
                raise ValueError("Order quantity must be positive")
        
        # Apply negotiation skill to potentially reduce costs
        # Higher skill means better deals
        discount_factor = 1.0
        if negotiation_skill_level > 1:
            discount_factor = 1.0 - (negotiation_skill_level * 0.01)  # 1% discount per skill level
        
        # Process orders
        order_results = {
            "order_date": datetime.utcnow().isoformat(),
            "supplier_id": supplier_id,
            "total_cost": 0.0,
            "discount_applied": 1.0 - discount_factor if negotiation_skill_level > 1 else 0.0,
            "items_ordered": [],
            "estimated_delivery_date": (datetime.utcnow() + timedelta(days=random.randint(1, 3))).isoformat()
        }
        
        inventory = business.inventory or {}
        
        # Process each order
        for order in orders:
            item_id = order["item_id"]
            quantity = order["quantity"]
            
            # Determine price per unit
            if item_id in inventory and "purchase_price_per_unit" in inventory[item_id]:
                price_per_unit = inventory[item_id]["purchase_price_per_unit"]
            else:
                # Estimate price for new items
                price_per_unit = self._estimate_material_cost(item_id, business.business_type)
            
            # Apply discount
            discounted_price = price_per_unit * discount_factor
            total_item_cost = discounted_price * quantity
            
            # Add to total cost
            order_results["total_cost"] += total_item_cost
            
            # Add to ordered items
            order_results["items_ordered"].append({
                "item_id": item_id,
                "quantity": quantity,
                "price_per_unit": discounted_price,
                "total_cost": total_item_cost
            })
        
        # Record the transaction
        record_financial_transaction(
            db=db,
            business_id=business_id,
            transaction_type=TransactionType.PURCHASE,
            amount=order_results["total_cost"],
            description=f"Material order from supplier {supplier_id or 'market'}",
            is_income=False,
            related_entity_id=supplier_id,
            related_entity_name=supplier_id or "General Market",  # Would be supplier name in a real system
            category="inventory_purchase"
        )
        
        # Update business balance
        update_business(db, business_id, {
            "current_balance": business.current_balance - order_results["total_cost"],
            "total_expenses": business.total_expenses + order_results["total_cost"]
        })
        
        # In a real system, this would trigger a delivery event after the estimated time
        # For now, immediately update the inventory for demonstration
        for order_item in order_results["items_ordered"]:
            item_id = order_item["item_id"]
            quantity = order_item["quantity"]
            price_per_unit = order_item["price_per_unit"]
            
            # Update or add to inventory
            if item_id in inventory:
                inventory[item_id]["quantity"] += quantity
                inventory[item_id]["last_restocked"] = datetime.utcnow().isoformat()
                
                # Update price as a weighted average of old and new
                old_price = inventory[item_id]["purchase_price_per_unit"]
                old_quantity = inventory[item_id]["quantity"] - quantity
                if old_quantity > 0:
                    new_price = ((old_price * old_quantity) + (price_per_unit * quantity)) / inventory[item_id]["quantity"]
                    inventory[item_id]["purchase_price_per_unit"] = new_price
                else:
                    inventory[item_id]["purchase_price_per_unit"] = price_per_unit
            else:
                # Add new item to inventory
                inventory[item_id] = {
                    "item_id": item_id,
                    "quantity": quantity,
                    "purchase_price_per_unit": price_per_unit,
                    "selling_price_per_unit": price_per_unit * 1.5,  # Default markup
                    "restock_threshold": max(1, quantity // 5),  # Default restock threshold
                    "is_material": True,
                    "last_restocked": datetime.utcnow().isoformat()
                }
        
        # Update business inventory
        update_business(db, business_id, {"inventory": inventory})
        
        self.logger.info(f"Ordered materials for business {business_id}, total cost: {order_results['total_cost']}")
        
        return order_results
    
    def manage_spoilage_or_degradation(
        self,
        db: Session,
        business_id: str
    ) -> Dict[str, Any]:
        """
        Manage spoilage or degradation of perishable inventory items.
        
        Args:
            db: Database session
            business_id: Business profile ID
            
        Returns:
            Dictionary with spoilage results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        inventory = business.inventory or {}
        
        # Track spoilage
        spoilage_results = {
            "check_date": datetime.utcnow().isoformat(),
            "expired_items": [],
            "soon_expiring_items": [],
            "total_value_lost": 0.0
        }
        
        # Check each inventory item
        updated_inventory = inventory.copy()
        for item_id, item_data in inventory.items():
            # Check if item has expiration date
            if "expiration_date" in item_data and item_data["expiration_date"] and item_data["quantity"] > 0:
                expiration = datetime.fromisoformat(item_data["expiration_date"]) \
                             if isinstance(item_data["expiration_date"], str) else item_data["expiration_date"]
                
                if expiration <= datetime.utcnow():
                    # Item has expired
                    value_lost = item_data["quantity"] * (item_data.get("purchase_price_per_unit", 0.0))
                    spoilage_results["total_value_lost"] += value_lost
                    
                    spoilage_results["expired_items"].append({
                        "item_id": item_id,
                        "name": item_data.get("name", f"Item {item_id}"),
                        "quantity": item_data["quantity"],
                        "expiration_date": expiration.isoformat(),
                        "value_lost": value_lost
                    })
                    
                    # Remove from inventory
                    updated_inventory[item_id]["quantity"] = 0
                elif (expiration - datetime.utcnow()).days <= 3:  # Expiring within 3 days
                    # Flag for imminent expiration
                    spoilage_results["soon_expiring_items"].append({
                        "item_id": item_id,
                        "name": item_data.get("name", f"Item {item_id}"),
                        "quantity": item_data["quantity"],
                        "expiration_date": expiration.isoformat(),
                        "days_until_expiry": (expiration - datetime.utcnow()).days,
                        "potential_value_at_risk": item_data["quantity"] * (item_data.get("purchase_price_per_unit", 0.0))
                    })
            
            # Check for general degradation based on time since restocking
            # This would be more sophisticated in a real system
            # For now, just flag items that haven't been restocked in a long time
            if "last_restocked" in item_data and item_data["last_restocked"] and item_data["quantity"] > 0:
                last_restocked = datetime.fromisoformat(item_data["last_restocked"]) \
                                if isinstance(item_data["last_restocked"], str) else item_data["last_restocked"]
                
                # If it's been more than 60 days since restocking, some degradation might occur
                if (datetime.utcnow() - last_restocked).days > 60:
                    # Simulate some degradation for certain item types
                    # This would be more sophisticated in a real system
                    pass
        
        # Update inventory if there were any changes
        if spoilage_results["expired_items"]:
            update_business(db, business_id, {"inventory": updated_inventory})
            
            # Record spoilage loss transaction
            if spoilage_results["total_value_lost"] > 0:
                record_financial_transaction(
                    db=db,
                    business_id=business_id,
                    transaction_type=TransactionType.OTHER,
                    amount=spoilage_results["total_value_lost"],
                    description="Inventory spoilage loss",
                    is_income=False,
                    category="inventory_loss"
                )
        
        self.logger.info(f"Checked for spoilage in business {business_id}, items expired: {len(spoilage_results['expired_items'])}")
        
        return spoilage_results
    
    # === SHOP FRONT OPERATIONS METHODS ===
    
    def set_daily_prices_for_stock_items(
        self,
        db: Session,
        business_id: str,
        item_price_updates: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Set or update prices for stock items.
        
        Args:
            db: Database session
            business_id: Business profile ID
            item_price_updates: Dictionary mapping item IDs to new prices
            
        Returns:
            Dictionary with price update results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        inventory = business.inventory or {}
        
        # Track price updates
        price_update_results = {
            "update_date": datetime.utcnow().isoformat(),
            "updated_items": [],
            "invalid_items": []
        }
        
        # Update prices
        updated_inventory = inventory.copy()
        for item_id, new_price in item_price_updates.items():
            if item_id in inventory:
                if new_price <= 0:
                    price_update_results["invalid_items"].append({
                        "item_id": item_id,
                        "reason": "Price must be positive"
                    })
                    continue
                
                old_price = inventory[item_id].get("selling_price_per_unit", 0.0)
                updated_inventory[item_id]["selling_price_per_unit"] = new_price
                
                price_update_results["updated_items"].append({
                    "item_id": item_id,
                    "name": inventory[item_id].get("name", f"Item {item_id}"),
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_percentage": ((new_price - old_price) / old_price * 100) if old_price > 0 else 100
                })
            else:
                price_update_results["invalid_items"].append({
                    "item_id": item_id,
                    "reason": "Item not found in inventory"
                })
        
        # Update inventory if there were any changes
        if price_update_results["updated_items"]:
            update_business(db, business_id, {"inventory": updated_inventory})
        
        self.logger.info(f"Updated prices for {len(price_update_results['updated_items'])} items in business {business_id}")
        
        return price_update_results
    
    def interact_with_browsing_customer_npc(
        self,
        db: Session,
        business_id: str,
        customer_npc_id: str,
        interaction_type: str,
        player_charisma: int = 5,
        interaction_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interact with a browsing customer NPC.
        
        Args:
            db: Database session
            business_id: Business profile ID
            customer_npc_id: Customer NPC ID
            interaction_type: Type of interaction (e.g., "greet", "help", "suggest", "negotiate")
            player_charisma: Player's charisma attribute (1-10)
            interaction_details: Optional additional details for the interaction
            
        Returns:
            Dictionary with interaction results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Validate interaction type
        valid_interaction_types = ["greet", "help", "suggest", "negotiate", "smalltalk", "explain_product"]
        if interaction_type not in valid_interaction_types:
            raise ValueError(f"Invalid interaction type. Must be one of: {', '.join(valid_interaction_types)}")
        
        # Determine success chance based on charisma
        base_success_chance = 0.5
        charisma_modifier = (player_charisma - 5) * 0.05  # +/- 5% per point from average
        
        # Adjust based on interaction type
        interaction_difficulty = {
            "greet": 0.2,      # Very easy
            "help": 0.0,       # Average
            "suggest": -0.1,   # Slightly hard
            "negotiate": -0.2, # Hard
            "smalltalk": 0.1,  # Easy
            "explain_product": -0.05  # Slightly hard
        }
        
        success_chance = base_success_chance + charisma_modifier + interaction_difficulty[interaction_type]
        success_chance = min(0.95, max(0.05, success_chance))  # Cap between 5% and 95%
        
        # Determine outcome
        success = random.random() < success_chance
        
        # Generate customer response
        customer_response = self._generate_customer_interaction_response(
            interaction_type, success, customer_npc_id, interaction_details
        )
        
        # Determine satisfaction change
        satisfaction_change = 0
        if success:
            if interaction_type in ["negotiate", "suggest"]:
                satisfaction_change = random.randint(1, 2)
            else:
                satisfaction_change = random.randint(0, 1)
        else:
            if interaction_type in ["negotiate", "suggest"]:
                satisfaction_change = -random.randint(1, 2)
            else:
                satisfaction_change = -random.randint(0, 1)
        
        # Create interaction result
        interaction_result = {
            "customer_npc_id": customer_npc_id,
            "interaction_type": interaction_type,
            "success": success,
            "customer_response": customer_response,
            "satisfaction_change": satisfaction_change,
            "next_recommended_actions": self._get_next_recommended_actions(interaction_type, success)
        }
        
        # Record the interaction
        record_customer_interaction(
            db=db,
            business_id=business_id,
            customer_npc_id=customer_npc_id,
            interaction_type=interaction_type,
            satisfaction_rating=5 + satisfaction_change,  # Base satisfaction of 5 + change
            notes=f"Player {interaction_type} interaction, {'successful' if success else 'unsuccessful'}"
        )
        
        self.logger.info(f"Player interacted with customer {customer_npc_id} in business {business_id}, interaction: {interaction_type}")
        
        return interaction_result
    
    def _generate_customer_interaction_response(
        self,
        interaction_type: str,
        success: bool,
        customer_npc_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response for a customer interaction.
        
        Args:
            interaction_type: Type of interaction
            success: Whether the interaction was successful
            customer_npc_id: Customer NPC ID
            details: Optional additional details
            
        Returns:
            Customer response text
        """
        # In a real implementation, this would be more sophisticated and potentially
        # query NPC data for personality and preferences
        
        # Simple response generation based on interaction type and success
        if interaction_type == "greet":
            if success:
                return random.choice([
                    "Hello there! Nice to meet you. I'm looking for something special today.",
                    "Good day! Your shop looks interesting. I'd love to browse around.",
                    "Greetings! I've heard good things about your establishment."
                ])
            else:
                return random.choice([
                    "Hmm? Oh, hello. I'm just looking.",
                    "*nods silently and continues browsing*",
                    "I'm in a bit of a hurry, actually."
                ])
        
        elif interaction_type == "help":
            if success:
                return random.choice([
                    "Yes, actually, I could use some assistance. I'm looking for something durable and well-crafted.",
                    "Thank you, that would be helpful. I'm trying to find a gift for my spouse.",
                    "Indeed, I'm not familiar with these items. Could you explain the differences to me?"
                ])
            else:
                return random.choice([
                    "No, I'm fine just browsing for now, thanks.",
                    "I prefer to look around on my own first.",
                    "I'll let you know if I need anything."
                ])
        
        elif interaction_type == "suggest":
            if success:
                return random.choice([
                    "That does look perfect for what I need! I hadn't noticed it before.",
                    "Hmm, good suggestion. I think that would work well for me.",
                    "You've got a good eye! That's exactly the sort of thing I was hoping to find."
                ])
            else:
                return random.choice([
                    "I don't think that's quite what I'm looking for.",
                    "That's a bit outside my budget, to be honest.",
                    "Hmm, I'm not sure that suits my needs."
                ])
        
        elif interaction_type == "negotiate":
            if success:
                return random.choice([
                    "Well, when you put it that way... alright, we have a deal.",
                    "That seems fair enough. I'll take it at that price.",
                    "You drive a hard bargain, but I can work with that."
                ])
            else:
                return random.choice([
                    "I'm afraid that's still more than I'm willing to pay.",
                    "I'll have to think about it. Maybe I'll come back another time.",
                    "I was hoping for a better price, to be honest."
                ])
        
        elif interaction_type == "smalltalk":
            if success:
                return random.choice([
                    "Indeed, the weather has been quite pleasant lately. Makes for good traveling.",
                    "Oh, you heard about that too? The town's been buzzing with that news.",
                    "Haha, that's a good one! You're quite the conversationalist."
                ])
            else:
                return random.choice([
                    "Hmm? Oh, yes, I suppose so. *looks distracted*",
                    "I should really focus on my shopping...",
                    "I'm not really one for idle chatter, I'm afraid."
                ])
        
        elif interaction_type == "explain_product":
            if success:
                return random.choice([
                    "I see! That's quite fascinating. I had no idea there was such craftsmanship involved.",
                    "That makes sense now. I appreciate you taking the time to explain.",
                    "Oh, so that's how it works! That's much more impressive than I realized."
                ])
            else:
                return random.choice([
                    "I'm not sure I follow all the technical details...",
                    "That's... a lot of information. I'll need to think about it.",
                    "Hmm, sounds complicated. Is there something simpler available?"
                ])
        
        # Default response
        return "I see. Interesting."
    
    def _get_next_recommended_actions(self, interaction_type: str, success: bool) -> List[str]:
        """
        Get recommended next actions based on the current interaction.
        
        Args:
            interaction_type: Type of interaction
            success: Whether the interaction was successful
            
        Returns:
            List of recommended next actions
        """
        if interaction_type == "greet":
            if success:
                return ["help", "smalltalk"]
            else:
                return ["give_space", "smalltalk"]
        
        elif interaction_type == "help":
            if success:
                return ["suggest", "explain_product"]
            else:
                return ["give_space", "greet_again_later"]
        
        elif interaction_type == "suggest":
            if success:
                return ["explain_product", "negotiate"]
            else:
                return ["suggest_alternative", "help"]
        
        elif interaction_type == "negotiate":
            if success:
                return ["complete_sale", "suggest_additional_item"]
            else:
                return ["suggest_alternative", "provide_discount"]
        
        elif interaction_type == "smalltalk":
            if success:
                return ["help", "suggest"]
            else:
                return ["help", "give_space"]
        
        elif interaction_type == "explain_product":
            if success:
                return ["suggest", "negotiate"]
            else:
                return ["suggest_alternative", "simplify_explanation"]
        
        # Default recommendations
        return ["help", "give_space"]
    
    def process_direct_sale_to_npc(
        self,
        db: Session,
        business_id: str,
        customer_npc_id: str,
        items_to_sell: Dict[str, int],
        apply_discount: Optional[float] = None,
        player_persuasion: int = 5
    ) -> Dict[str, Any]:
        """
        Process a direct sale to an NPC customer.
        
        Args:
            db: Database session
            business_id: Business profile ID
            customer_npc_id: Customer NPC ID
            items_to_sell: Dictionary mapping item IDs to quantities
            apply_discount: Optional discount percentage (0-100)
            player_persuasion: Player's persuasion attribute (1-10)
            
        Returns:
            Dictionary with sale results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        inventory = business.inventory or {}
        
        # Validate items to sell
        if not items_to_sell:
            raise ValueError("No items specified for sale")
            
        for item_id, quantity in items_to_sell.items():
            if item_id not in inventory:
                raise ValueError(f"Item {item_id} not found in inventory")
                
            if inventory[item_id]["quantity"] < quantity:
                raise ValueError(f"Not enough of item {item_id} in inventory")
                
            if quantity <= 0:
                raise ValueError(f"Quantity must be positive for item {item_id}")
        
        # Process discount
        discount_multiplier = 1.0
        if apply_discount is not None:
            if apply_discount < 0 or apply_discount > 100:
                raise ValueError("Discount must be between 0 and 100 percent")
                
            discount_multiplier = 1.0 - (apply_discount / 100.0)
        
        # Calculate sale details
        sale_items = []
        total_price = 0.0
        total_cost = 0.0
        
        for item_id, quantity in items_to_sell.items():
            item_data = inventory[item_id]
            unit_price = item_data.get("selling_price_per_unit", 0.0) * discount_multiplier
            unit_cost = item_data.get("purchase_price_per_unit", 0.0)
            
            item_total_price = unit_price * quantity
            item_total_cost = unit_cost * quantity
            
            total_price += item_total_price
            total_cost += item_total_cost
            
            sale_items.append({
                "item_id": item_id,
                "name": item_data.get("name", f"Item {item_id}"),
                "quantity": quantity,
                "unit_price": unit_price,
                "unit_cost": unit_cost,
                "total_price": item_total_price,
                "total_cost": item_total_cost,
                "profit": item_total_price - item_total_cost
            })
        
        # Calculate total profit
        total_profit = total_price - total_cost
        
        # Update inventory
        updated_inventory = inventory.copy()
        for item_id, quantity in items_to_sell.items():
            updated_inventory[item_id]["quantity"] -= quantity
        
        # Record the sale transaction
        transaction_id = record_financial_transaction(
            db=db,
            business_id=business_id,
            transaction_type=TransactionType.SALE,
            amount=total_price,
            description=f"Sale to customer {customer_npc_id}",
            is_income=True,
            related_entity_id=customer_npc_id,
            category="sales",
            item_details={
                "items_sold": {item_id: quantity for item_id, quantity in items_to_sell.items()},
                "discount_applied": apply_discount
            }
        ).id
        
        # Record customer interaction
        # Determine satisfaction based on discount and persuasion
        satisfaction_base = 3  # Base satisfaction on a 1-5 scale
        
        # Discount increases satisfaction
        if apply_discount is not None and apply_discount > 0:
            satisfaction_base += min(2, apply_discount / 25)  # Up to +2 for 50%+ discount
            
        # Persuasion can affect satisfaction
        persuasion_modifier = (player_persuasion - 5) * 0.2  # +/- 1 for extreme persuasion
        
        # Cap at 1-5 range
        satisfaction_rating = max(1, min(5, int(satisfaction_base + persuasion_modifier + 0.5)))
        
        interaction_id = record_customer_interaction(
            db=db,
            business_id=business_id,
            customer_npc_id=customer_npc_id,
            interaction_type="purchase",
            satisfaction_rating=satisfaction_rating,
            notes=f"Customer purchased {len(items_to_sell)} different items",
            purchase_amount=total_price,
            items_purchased=items_to_sell
        )
        
        # Update business data
        update_business(db, business_id, {
            "inventory": updated_inventory,
            "current_balance": business.current_balance + total_price,
            "total_revenue": business.total_revenue + total_price
        })
        
        # Create sale result
        sale_result = {
            "transaction_id": transaction_id,
            "interaction_id": interaction_id,
            "customer_npc_id": customer_npc_id,
            "sale_date": datetime.utcnow().isoformat(),
            "items_sold": sale_items,
            "total_price": total_price,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "discount_applied": apply_discount,
            "customer_satisfaction": satisfaction_rating
        }
        
        self.logger.info(f"Processed sale to customer {customer_npc_id} for business {business_id}, total: {total_price}")
        
        return sale_result
    
    # === FINANCIAL MANAGEMENT METHODS ===
    
    def review_daily_or_weekly_ledger(
        self,
        db: Session,
        business_id: str,
        period: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Review financial transactions for a specific period.
        
        Args:
            db: Database session
            business_id: Business profile ID
            period: Period to review ("daily", "weekly", "monthly")
            start_date: Optional start date (defaults to appropriate period start)
            end_date: Optional end date (defaults to current date)
            
        Returns:
            Dictionary with financial summary
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Set default end date to now
        if not end_date:
            end_date = datetime.utcnow()
            
        # Set default start date based on period
        if not start_date:
            if period == "daily":
                # Start at beginning of the day
                start_date = datetime(end_date.year, end_date.month, end_date.day)
            elif period == "weekly":
                # Start 7 days ago
                start_date = end_date - timedelta(days=7)
            elif period == "monthly":
                # Start 30 days ago
                start_date = end_date - timedelta(days=30)
            else:
                raise ValueError("Invalid period. Must be 'daily', 'weekly', or 'monthly'")
        
        # Get transactions from the shop ledger
        shop_ledger = business.shop_ledger or []
        
        # Filter transactions within the date range
        period_transactions = []
        for transaction in shop_ledger:
            transaction_date = datetime.fromisoformat(transaction["timestamp"]) \
                              if isinstance(transaction["timestamp"], str) else transaction["timestamp"]
            
            if start_date <= transaction_date <= end_date:
                period_transactions.append(transaction)
        
        # Calculate summary
        summary = {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_transactions": len(period_transactions),
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "transaction_categories": {},
            "transactions_by_day": {},
            "top_selling_items": {},
            "top_expenses": []
        }
        
        # Process transactions
        for transaction in period_transactions:
            amount = transaction["amount"]
            is_income = transaction["is_income"]
            category = transaction.get("category", "uncategorized")
            
            # Add to total revenue/expenses
            if is_income:
                summary["total_revenue"] += amount
            else:
                summary["total_expenses"] += amount
            
            # Add to category summaries
            category_key = f"{category}_{'income' if is_income else 'expense'}"
            if category_key not in summary["transaction_categories"]:
                summary["transaction_categories"][category_key] = 0.0
            summary["transaction_categories"][category_key] += amount
            
            # Add to daily summaries
            transaction_date = datetime.fromisoformat(transaction["timestamp"]) \
                              if isinstance(transaction["timestamp"], str) else transaction["timestamp"]
            day_key = transaction_date.strftime("%Y-%m-%d")
            
            if day_key not in summary["transactions_by_day"]:
                summary["transactions_by_day"][day_key] = {
                    "revenue": 0.0,
                    "expenses": 0.0,
                    "profit": 0.0,
                    "transaction_count": 0
                }
            
            if is_income:
                summary["transactions_by_day"][day_key]["revenue"] += amount
            else:
                summary["transactions_by_day"][day_key]["expenses"] += amount
            
            summary["transactions_by_day"][day_key]["transaction_count"] += 1
            summary["transactions_by_day"][day_key]["profit"] = \
                summary["transactions_by_day"][day_key]["revenue"] - summary["transactions_by_day"][day_key]["expenses"]
            
            # Track top selling items (for sales)
            if is_income and transaction["transaction_type"] == TransactionType.SALE.value:
                item_details = transaction.get("item_details", {})
                items_sold = item_details.get("items_sold", {})
                
                for item_id, quantity in items_sold.items():
                    if item_id not in summary["top_selling_items"]:
                        summary["top_selling_items"][item_id] = {
                            "item_id": item_id,
                            "quantity_sold": 0,
                            "revenue": 0.0
                        }
                    
                    summary["top_selling_items"][item_id]["quantity_sold"] += quantity
                    # Approximate revenue attribution (more detailed tracking would be better)
                    item_revenue = amount * (quantity / sum(items_sold.values()))
                    summary["top_selling_items"][item_id]["revenue"] += item_revenue
            
            # Track top expenses (for non-income transactions)
            if not is_income:
                summary["top_expenses"].append({
                    "amount": amount,
                    "description": transaction["description"],
                    "category": category,
                    "transaction_type": transaction["transaction_type"],
                    "timestamp": transaction["timestamp"]
                })
        
        # Calculate net profit
        summary["net_profit"] = summary["total_revenue"] - summary["total_expenses"]
        
        # Sort top selling items by revenue
        top_selling_items_list = list(summary["top_selling_items"].values())
        top_selling_items_list.sort(key=lambda x: x["revenue"], reverse=True)
        summary["top_selling_items"] = top_selling_items_list[:10]  # Top 10
        
        # Sort top expenses by amount
        summary["top_expenses"].sort(key=lambda x: x["amount"], reverse=True)
        summary["top_expenses"] = summary["top_expenses"][:10]  # Top 10
        
        # Generate business recommendations based on the data
        summary["recommendations"] = self._generate_business_recommendations(summary, business)
        
        # Create daily summary record if this is a daily summary
        if period == "daily" and start_date.date() == end_date.date():
            self._create_daily_summary_record(db, business_id, summary)
        
        self.logger.info(f"Generated {period} financial summary for business {business_id}")
        
        return summary
    
    def _generate_business_recommendations(
        self,
        financial_summary: Dict[str, Any],
        business: PlayerBusinessProfile
    ) -> List[Dict[str, Any]]:
        """
        Generate business recommendations based on financial data.
        
        Args:
            financial_summary: Financial summary data
            business: Business profile
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check profit margin
        if financial_summary["total_revenue"] > 0:
            profit_margin = financial_summary["net_profit"] / financial_summary["total_revenue"] * 100
            
            if profit_margin < 10:
                recommendations.append({
                    "category": "profitability",
                    "title": "Low Profit Margin",
                    "description": f"Your profit margin is only {profit_margin:.1f}%. Consider increasing prices or reducing expenses.",
                    "priority": "high"
                })
            elif profit_margin > 50:
                recommendations.append({
                    "category": "pricing",
                    "title": "High Profit Margin",
                    "description": f"Your profit margin is {profit_margin:.1f}%. You might be able to lower prices to attract more customers.",
                    "priority": "medium"
                })
        
        # Check top selling items
        if financial_summary["top_selling_items"]:
            top_item = financial_summary["top_selling_items"][0]
            recommendations.append({
                "category": "inventory",
                "title": "Popular Item Identified",
                "description": f"Item {top_item['item_id']} is your best seller. Consider stocking more of this item.",
                "priority": "medium"
            })
        
        # Check expense patterns
        staff_expenses = 0
        for category, amount in financial_summary["transaction_categories"].items():
            if "staff_wages_expense" in category or "wage_payment_expense" in category:
                staff_expenses += amount
                
        if staff_expenses > financial_summary["total_expenses"] * 0.5:
            recommendations.append({
                "category": "staffing",
                "title": "High Staff Costs",
                "description": f"Staff wages account for over 50% of your expenses. Review your staffing needs.",
                "priority": "high"
            })
        
        # Check daily patterns
        daily_data = financial_summary["transactions_by_day"]
        if len(daily_data) > 1:
            profit_by_day = [(day, data["profit"]) for day, data in daily_data.items()]
            profit_by_day.sort(key=lambda x: x[1])
            
            worst_day = profit_by_day[0]
            best_day = profit_by_day[-1]
            
            if worst_day[1] < 0:
                recommendations.append({
                    "category": "operations",
                    "title": "Unprofitable Day Identified",
                    "description": f"{worst_day[0]} was your least profitable day. Consider adjusting operations on this day.",
                    "priority": "medium"
                })
                
            if best_day[1] > 0:
                recommendations.append({
                    "category": "operations",
                    "title": "Most Profitable Day Identified",
                    "description": f"{best_day[0]} was your most profitable day. Consider what worked well on this day.",
                    "priority": "low"
                })
        
        return recommendations
    
    def _create_daily_summary_record(
        self,
        db: Session,
        business_id: str,
        summary: Dict[str, Any]
    ) -> None:
        """
        Create a daily business summary record from financial data.
        
        Args:
            db: Database session
            business_id: Business profile ID
            summary: Financial summary data
        """
        date_str = summary["start_date"]
        summary_date = datetime.fromisoformat(date_str) if isinstance(date_str, str) else date_str
        
        # Extract daily summary data
        total_sales = summary["total_revenue"]
        total_expenses = summary["total_expenses"]
        profit = summary["net_profit"]
        
        # Estimate number of customers from transactions
        # In a real system, this would be more accurate
        estimated_customers = len([t for t in summary.get("transactions", []) 
                                if t.get("transaction_type") == TransactionType.SALE.value])
        
        # Extract items sold
        items_sold = {}
        for item in summary.get("top_selling_items", []):
            items_sold[item["item_id"]] = item["quantity_sold"]
        
        # Create the summary record
        create_daily_business_summary(
            db=db,
            business_id=business_id,
            date=summary_date,
            total_sales=total_sales,
            total_expenses=total_expenses,
            number_of_customers=estimated_customers,
            items_sold=items_sold,
            materials_used={},  # Would need more detailed tracking
            customer_satisfaction_average=None,  # Would need customer interaction data
            special_events=[],
            staff_performance_notes={},
            notable_interactions=[]
        )
    
    def pay_rent_or_taxes(
        self,
        db: Session,
        business_id: str,
        payment_type: str,
        payment_amount: float,
        property_id: Optional[str] = None,
        payment_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Pay rent or taxes for the business property.
        
        Args:
            db: Database session
            business_id: Business profile ID
            payment_type: Type of payment ("rent" or "tax")
            payment_amount: Amount to pay
            property_id: Optional property ID (deed or lease)
            payment_date: Optional payment date (defaults to current date)
            
        Returns:
            Dictionary with payment results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Validate payment type
        if payment_type not in ["rent", "tax"]:
            raise ValueError("Payment type must be 'rent' or 'tax'")
            
        # Use current date if not provided
        payment_date = payment_date or datetime.utcnow()
        
        # Determine transaction type
        transaction_type = TransactionType.RENT_PAYMENT if payment_type == "rent" else TransactionType.TAX_PAYMENT
        
        # Determine property details
        property_details = None
        if property_id:
            if payment_type == "rent" and business.lease_agreement_id == property_id:
                lease = get_lease_agreement(db, property_id)
                if lease:
                    property_details = {
                        "id": lease.id,
                        "type": "lease",
                        "address": lease.address_description,
                        "lessor_id": lease.lessor_npc_id,
                        "payment_period": lease.rent_due_date_rule
                    }
                    
                    # Update lease with payment date
                    update_data = {"last_rent_payment_date": payment_date}
                    # Call the update function for lease agreement (needs to be implemented)
            
            elif payment_type == "tax" and business.property_deed_id == property_id:
                deed = get_property_deed(db, property_id)
                if deed:
                    property_details = {
                        "id": deed.id,
                        "type": "deed",
                        "address": deed.address_description,
                        "tax_authority": "Local Government",
                        "payment_period": deed.tax_due_date_rule
                    }
                    
                    # Update deed with payment date
                    update_data = {"last_tax_payment_date": payment_date}
                    # Call the update function for property deed (needs to be implemented)
        
        # Record the payment transaction
        description = f"{'Rent' if payment_type == 'rent' else 'Property tax'} payment"
        if property_details:
            description += f" for {property_details['address']}"
            
        transaction_id = record_financial_transaction(
            db=db,
            business_id=business_id,
            transaction_type=transaction_type,
            amount=payment_amount,
            description=description,
            is_income=False,
            related_entity_id=property_details["lessor_id"] if property_type == "rent" and "lessor_id" in property_details else None,
            related_entity_name=property_details["lessor_id"] if property_type == "rent" and "lessor_id" in property_details else "Tax Authority",
            category=payment_type
        ).id
        
        # Update business balance
        update_business(db, business_id, {
            "current_balance": business.current_balance - payment_amount,
            "total_expenses": business.total_expenses + payment_amount
        })
        
        # Create payment result
        payment_result = {
            "transaction_id": transaction_id,
            "payment_type": payment_type,
            "payment_amount": payment_amount,
            "payment_date": payment_date.isoformat(),
            "property_details": property_details,
            "new_balance": business.current_balance - payment_amount
        }
        
        self.logger.info(f"Paid {payment_type} of {payment_amount} for business {business_id}")
        
        return payment_result